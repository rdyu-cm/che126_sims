"""Render plain LAMMPS input decks from Jinja templates for a built system.

A deck is rendered from ``templates/<protocol>.in.j2`` (``prep``, ``sweep``,
``benchmark``) and the system's
``manifest.yaml``: styles, mixing, special_bonds, type ids and SHAKE bond types come
from the manifest; every coefficient line is emitted from the force-field YAML via
``sepsim.ff.params.to_lammps_real`` (the deck must not rely on data-file coefficients,
because changing ``pair_style`` during the push-off discards them). Run parameters come
from a per-protocol, per-resolution defaults table (decisions D12a, D12c, D12g, D20,
D24, D25, D28, D31, D34-D39), an optional preset (``smoke``) and ``key=value`` overrides, in that order. The deck
header lists every resolved parameter; output is deterministic (no timestamps).

Decks carry no accelerator ``package`` or suffix lines; pass ``-sf``/``-pk`` to ``lmp``.
"""

from __future__ import annotations

import os
from pathlib import Path

import jinja2
import yaml

from sepsim import __version__
from sepsim.ff.params import FORCEFIELD_DIR, load_forcefield, to_lammps_real
from sepsim.run import sha256_file

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
PROTOCOLS = ("prep", "sweep", "benchmark")
MANIFEST_NAME = "manifest.yaml"
DATA_NAME = "data.lmp"

# Durations are in ps, temperatures in K, pressures in atm, lengths in angstrom, dt in fs.
_COMMON = {
    "neighbor_skin": 2.0,
    "tdamp_dt": 100,  # Tdamp = 100 dt (D12g)
    "pdamp_dt": 1000,  # Pdamp = 1000 dt (D12g)
    "thermo_ps": 1.0,  # D28
    "restart_ps": 1000.0,  # rolling restart.a/restart.b for manual resume
    "min_etol": 1.0e-4,
    "min_ftol": 1.0e-6,
    "min_maxiter": 10000,
    "min_maxeval": 100000,
    "shake_tol": 1.0e-4,
    "shake_iter": 20,
    "t_melt": 500.0,  # D24
    "nvt_ps": 100.0,
    "p_compress_atm": 100.0,  # brief moderate overpressure (D24)
    "p_atm": 1.0,  # D9
    "hold_dump_ps": 10.0,  # D28: frames every 10 ps in holds
    "t_final": 298.15,
    "cool_steps": 8,
    "cool_dump_ps": 100.0,  # D28: frames every 100 ps in ramps
}

# Push-off (D31): pair soft ramp, nve/limit + langevin, bonded terms on, no Coulomb.
_PUSHOFF = {
    "pushoff": True,
    "pushoff_ps": 20.0,
    "pushoff_a_max": 50.0,  # kcal/mol, end of the ramp(0, A)
    "pushoff_nve_limit": 0.1,  # angstrom per step
    "pushoff_t": 500.0,
}

DEFAULTS = {
    "aa": _COMMON
    | _PUSHOFF
    | {
        "dt_fs": 1.0,
        "lj_cutoff": 12.0,
        "tail": True,
        "kspace_accuracy": 1.0e-5,  # D25
        "pushoff_rc": 3.0,
        "pushoff_dt_fs": 0.5,
        "compress_hi_ps": 200.0,
        "compress_ps": 800.0,
        "hold_ps": 5000.0,
        "cool_step_ps": 1000.0,
    },
    "ua": _COMMON
    | _PUSHOFF
    | {
        "dt_fs": 2.0,
        "lj_cutoff": 14.0,
        "tail": True,
        "kspace_accuracy": 0.0,  # 0 = no kspace
        "pushoff_rc": 4.0,
        "pushoff_dt_fs": 1.0,
        "compress_hi_ps": 200.0,
        "compress_ps": 800.0,
        "hold_ps": 20000.0,
        "cool_step_ps": 2000.0,
    },
    # CG has no push-off: angle_style spica needs an lj/spica pair style (recorded decision).
    "cg": _COMMON
    | {
        "pushoff": False,
        "dt_fs": 10.0,
        "lj_cutoff": 15.0,
        "tail": False,
        "kspace_accuracy": 0.0,
        "compress_hi_ps": 400.0,
        "compress_ps": 1600.0,
        "hold_ps": 20000.0,
        "cool_step_ps": 5000.0,
    },
}

# Force-field and integrator keys every protocol shares with prep (same values).
_FF_KEYS = (
    "neighbor_skin",
    "tdamp_dt",
    "pdamp_dt",
    "thermo_ps",
    "restart_ps",
    "shake_tol",
    "shake_iter",
    "p_atm",
    "dt_fs",
    "lj_cutoff",
    "tail",
    "kspace_accuracy",
)

# Sweep grid (D11, D36) in deg C; an "h" suffix marks a hold. Every point after the
# first is reached by an instantaneous target change and run as a step; a hold point
# then continues as a hold. The default gives 14 steps + 4 holds.
SWEEP_GRID_C = "25h,35,45,55,65,75,85,90h,100,110,120,130h,140,150,160h"
_SWEEP_RES = {  # D36: step and hold durations per resolution (ps); VDOS is AA only (D12c)
    "aa": {"step_ps": 1000.0, "sweep_hold_ps": 5000.0, "vdos": True},
    "ua": {"step_ps": 2000.0, "sweep_hold_ps": 10000.0, "vdos": False},
    "cg": {"step_ps": 5000.0, "sweep_hold_ps": 25000.0, "vdos": False},
}
SWEEP_DEFAULTS = {
    res: {k: DEFAULTS[res][k] for k in _FF_KEYS}
    | _SWEEP_RES[res]
    | {
        "sweep_grid_c": SWEEP_GRID_C,
        "step_dump_ps": 100.0,  # D28/D39: frames every 100 ps in ramp steps
        "hold_dump_ps": 10.0,  # D28/D39: frames every 10 ps in holds
        # D12c/D39: NVE velocity dump after each hold
        "vdos_ps": 10.0,
        "vdos_dt_fs": 1.0,
        "vdos_dump_fs": 4.0,
        "vdos_gzip": True,  # needs LAMMPS_GZIP (pipes through gzip)
    }
    for res in DEFAULTS
}

# Benchmark (D38): warm-up + timed run on a compressed box; ensemble=nve for the dt check.
BENCHMARK_ENSEMBLES = ("npt", "nve")
BENCHMARK_DEFAULTS = {
    res: {k: DEFAULTS[res][k] for k in _FF_KEYS}
    | {
        "ensemble": "npt",
        "bench_t": 500.0,
        "warmup_steps": 1000,
        "timed_steps": 2000,  # npt only; nve runs nve_ps
        "bench_thermo_steps": 100,
        "nve_ps": 100.0,  # D38: NVE length for the energy-drift check
    }
    for res in DEFAULTS
}

PROTOCOL_DEFAULTS = {"prep": DEFAULTS, "sweep": SWEEP_DEFAULTS, "benchmark": BENCHMARK_DEFAULTS}

# Data a protocol reads by default: a prep output in the sibling prep/ run directory.
DEFAULT_INPUT = {"sweep": "cooled.data", "benchmark": "compressed.data"}

# ps-scale stages for checking that a deck runs end to end. A protocol ignores the
# keys it does not use.
PRESETS = {
    "smoke": {
        "pushoff_ps": 2.0,
        "restart_ps": 1.0,
        "min_maxiter": 100,
        "min_maxeval": 1000,
        "nvt_ps": 1.0,
        "compress_hi_ps": 1.0,
        "compress_ps": 2.0,
        "hold_ps": 1.0,
        "hold_dump_ps": 0.5,
        "cool_step_ps": 0.5,
        "cool_dump_ps": 1.0,
        # sweep: two steps and one hold
        "sweep_grid_c": "25,35,45h",
        "step_ps": 1.0,
        "step_dump_ps": 0.5,
        "sweep_hold_ps": 2.0,
        "vdos_ps": 0.2,
        # benchmark
        "warmup_steps": 100,
        "timed_steps": 200,
        "nve_ps": 1.0,
    },
}


class RenderError(ValueError):
    """Bad protocol, preset, override or system directory."""


def _coerce(key: str, value, default):
    """Convert an override (string from the CLI, or a Python value) to the default's type."""
    if not isinstance(value, str):
        return type(default)(value)
    text = value.strip()
    if isinstance(default, bool):
        low = text.lower()
        if low in ("1", "true", "yes", "on"):
            return True
        if low in ("0", "false", "no", "off"):
            return False
        raise RenderError(f"--set {key}: expected a boolean, got {value!r}")
    try:
        return type(default)(text)
    except ValueError:
        raise RenderError(
            f"--set {key}: expected {type(default).__name__}, got {value!r}"
        ) from None


def parse_overrides(items: list[str]) -> dict[str, str]:
    """``["k=v", ...]`` -> ``{k: v}`` (values stay strings; typed in ``resolve_params``)."""
    out = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep or not key.strip():
            raise RenderError(f"--set expects key=value, got {item!r}")
        out[key.strip()] = value
    return out


def resolve_params(
    resolution: str,
    preset: str | None = None,
    overrides: dict | None = None,
    protocol: str = "prep",
):
    """Defaults for ``protocol`` at ``resolution``, then ``preset``, then ``overrides`` (typed)."""
    if protocol not in PROTOCOL_DEFAULTS:
        raise RenderError(f"unknown protocol {protocol!r} (known: {', '.join(PROTOCOLS)})")
    table = PROTOCOL_DEFAULTS[protocol]
    if resolution not in table:
        raise RenderError(f"unknown resolution {resolution!r}")
    params = dict(table[resolution])
    layers = []
    if preset is not None:
        if preset not in PRESETS:
            raise RenderError(f"unknown preset {preset!r} (known: {', '.join(PRESETS)})")
        layers.append({k: v for k, v in PRESETS[preset].items() if k in params})
    layers.append(overrides or {})
    for layer in layers:
        for key, value in layer.items():
            if key not in params:
                raise RenderError(
                    f"unknown parameter {key!r} for {resolution}; known: {', '.join(sorted(params))}"
                )
            params[key] = _coerce(key, value, params[key])
    if resolution == "cg" and params.get("pushoff"):
        raise RenderError("CG has no push-off: angle_style spica cannot run with pair_style soft")
    if protocol == "sweep":
        parse_grid(params["sweep_grid_c"])
    if protocol == "benchmark" and params["ensemble"] not in BENCHMARK_ENSEMBLES:
        raise RenderError(
            f"--set ensemble: expected one of {', '.join(BENCHMARK_ENSEMBLES)},"
            f" got {params['ensemble']!r}"
        )
    return params


def parse_grid(text: str) -> list[tuple[float, bool]]:
    """``"25h,35,90h"`` -> ``[(25.0, True), (35.0, False), (90.0, True)]`` (deg C, hold?)."""
    points = []
    for raw in text.split(","):
        item = raw.strip().lower()
        hold = item.endswith("h")
        try:
            points.append((float(item[:-1] if hold else item), hold))
        except ValueError:
            raise RenderError(
                f"sweep_grid_c: bad point {raw!r} (expected e.g. 25h,35,45h)"
            ) from None
    if len(points) < 2 and not points[0][1]:
        raise RenderError("sweep_grid_c: no segments (need a hold or at least two points)")
    return points


def _label(t_c: float) -> str:
    """File-name label for a temperature in deg C: 25 -> 25C, -10 -> m10C."""
    return f"{_num(t_c)}C".replace("-", "m")


def sweep_segments(params: dict) -> list[dict]:
    """Constant-T NPT segments of the sweep: a step at every grid point after the first,
    then a hold where the point is marked as one. Files are named by index and deg C."""
    segments = []
    for k, (t_c, hold) in enumerate(parse_grid(params["sweep_grid_c"])):
        for kind in (["step"] if k > 0 else []) + (["hold"] if hold else []):
            idx = len(segments) + 1
            label = _label(t_c)
            is_hold = kind == "hold"
            segments.append(
                {
                    "index": idx,
                    "kind": kind,
                    "t_c": t_c,
                    "t_k": t_c + 273.15,
                    "ps": params["sweep_hold_ps"] if is_hold else params["step_ps"],
                    "dump_ps": params["hold_dump_ps"] if is_hold else params["step_dump_ps"],
                    "dcd": f"seg{idx:02d}_{kind}_{label}.dcd",
                    "stage": f"hold_{label}" if is_hold else None,
                    "vdos": (
                        f"vdos_{label}.dump" + (".gz" if params["vdos_gzip"] else "")
                        if is_hold and params["vdos"]
                        else None
                    ),
                }
            )
    # A hold right after the step to the same T keeps the running fix npt (no thermostat
    # or barostat reset); a VDOS segment in between ends it.
    for k, seg in enumerate(segments):
        prev = segments[k - 1] if k else None
        seg["new_fix"] = prev is None or prev["t_k"] != seg["t_k"] or prev["vdos"] is not None
    for k, seg in enumerate(segments):
        last = k == len(segments) - 1
        seg["unfix"] = last or segments[k + 1]["new_fix"] or seg["vdos"] is not None
    return segments


def _num(x: float) -> str:
    """Same 12-significant-digit formatting as the data-file writer."""
    return f"{float(x):.12g}"


def steps(ps: float, dt_fs: float) -> int:
    """Whole number of steps in ``ps`` at timestep ``dt_fs``; at least 1."""
    n = ps * 1000.0 / dt_fs
    if abs(n - round(n)) > 1e-6:
        raise RenderError(f"{ps} ps is not a whole number of {dt_fs} fs steps")
    return max(1, round(n))


def coeff_lines(manifest: dict, ff) -> dict[str, list[str]]:
    """LAMMPS coefficient commands from the FF YAML, numbered by the manifest type ids."""
    real = to_lammps_real(ff)
    ids = manifest["type_ids"]
    styles = manifest["lammps_styles"]
    atoms = ids["atom"]
    out: dict[str, list[str]] = {
        "mass": [f"mass {i} {_num(real['atoms'][n]['mass'])}  # {n}" for n, i in atoms.items()]
    }
    pair = []
    if styles.get("mixing", "none") == "none":
        names = list(atoms)
        for k, a in enumerate(names):
            for b in names[k:]:
                p = real["pair"].get((a, b)) or real["pair"].get((b, a))
                if p is None:
                    raise RenderError(f"{ff.name}: no pair coefficients for {a}-{b} (no mixing)")
                i, j = sorted((atoms[a], atoms[b]))
                pair.append(
                    f"pair_coeff {i} {j} {p['form']} {_num(p['epsilon'])} {_num(p['sigma'])}"
                    f"  # {a}-{b}"
                )
    else:
        for n, i in atoms.items():
            p = real["pair"].get((n, n))
            if p is None:
                raise RenderError(f"{ff.name}: atom type {n} has no LJ parameters")
            pair.append(f"pair_coeff {i} {i} {_num(p['epsilon'])} {_num(p['sigma'])}  # {n}")
    out["pair"] = pair
    out["bond"] = [
        f"bond_coeff {i} {_num(real['bond'][n]['K'])} {_num(real['bond'][n]['r0'])}  # {n}"
        for n, i in ids["bond"].items()
    ]
    out["angle"] = [
        f"angle_coeff {i} {_num(real['angle'][n]['K'])} {_num(real['angle'][n]['theta0'])}  # {n}"
        for n, i in ids["angle"].items()
    ]
    out["dihedral"] = [
        f"dihedral_coeff {i} "
        + " ".join(_num(real["dihedral"][n][f"K{k}"]) for k in range(1, 5))
        + f"  # {n}"
        for n, i in (ids.get("dihedral") or {}).items()
    ]
    return out


def _special_bonds(sb: dict) -> str:
    parts = []
    for key in ("lj", "coul"):
        if key in sb:
            parts.append(key + " " + " ".join(_num(v) for v in sb[key]))
    if sb.get("angle"):
        parts.append("angle yes")
    return " ".join(parts)


def _environment() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["num"] = _num
    return env


def default_data(protocol: str, system_dir: str | Path, run_dir: str | Path | None) -> Path:
    """Default input data: ``SYSTEM/data.lmp`` for prep; for sweep/benchmark the prep
    output (``cooled.data`` / ``compressed.data``) in the sibling ``prep/`` run directory."""
    if protocol not in DEFAULT_INPUT:
        return Path(system_dir) / DATA_NAME
    if run_dir is None:
        raise RenderError(f"{protocol}: give the data file (default needs the run directory)")
    return Path(run_dir).parent / "prep" / DEFAULT_INPUT[protocol]


def render_deck(
    protocol: str,
    system_dir: str | Path,
    data: str | Path | None = None,
    overrides: dict | None = None,
    preset: str | None = None,
    deck_dir: str | Path | None = None,
    require_data: bool = True,
) -> str:
    """Return the text of the ``protocol`` deck for the system in ``system_dir``.

    ``data`` defaults to ``default_data(protocol, system_dir, deck_dir)``. The deck reads
    it by a path relative to ``deck_dir`` (the directory LAMMPS will run in) when given,
    else by absolute path. With ``require_data=False`` a data file that does not exist
    yet (the output of an earlier stage still to run) is allowed; the header then
    records no hash for it (``sepsim run`` hashes it at run time).
    """
    if protocol not in PROTOCOLS:
        raise RenderError(f"unknown protocol {protocol!r} (known: {', '.join(PROTOCOLS)})")
    system_dir = Path(system_dir)
    manifest_path = system_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise RenderError(f"{manifest_path}: no such file")
    manifest = yaml.safe_load(manifest_path.read_text())
    data = Path(data) if data is not None else default_data(protocol, system_dir, deck_dir)
    if require_data and not data.is_file():
        raise RenderError(f"{data}: no such file")
    data_ref = (
        os.path.relpath(data.resolve(), Path(deck_dir).resolve())
        if deck_dir is not None
        else str(data.resolve())
    )
    if any(c.isspace() for c in data_ref):
        raise RenderError(f"data path {data_ref!r} contains whitespace")

    res = manifest["resolution"]
    params = resolve_params(res, preset, overrides, protocol)
    ff_path = FORCEFIELD_DIR / manifest["forcefield"]["file"]
    ff = load_forcefield(ff_path)
    styles = manifest["lammps_styles"]
    dt = params["dt_fs"]
    context = {
        "p": params,
        "system": {
            "id": manifest["id"],
            "resolution": res,
            "seed": int(manifest["seed"]),
            "manifest_sha256": sha256_file(manifest_path),
            "data": data_ref,
            "data_sha256": sha256_file(data) if data.is_file() else None,
            "forcefield": ff_path.name,
            "forcefield_sha256": sha256_file(ff_path),
        },
        "protocol": protocol,
        "preset": preset,
        "version": __version__,
        "styles": styles,
        "special_bonds": _special_bonds(styles["special_bonds"]),
        "coeffs": coeff_lines(manifest, ff),
        "shake_types": sorted((manifest.get("shake_bond_types") or {}).values()),
        # step counts at the production timestep
        "n": lambda ps: steps(ps, dt),
    }
    if protocol == "prep":
        t0, t1, n = params["t_melt"], params["t_final"], params["cool_steps"]
        context["cool_temps"] = [t0 + (t1 - t0) * (k + 1) / n for k in range(n)]
        context["n_push"] = lambda ps: steps(ps, params.get("pushoff_dt_fs", dt))
    elif protocol == "sweep":
        context["segments"] = sweep_segments(params)
        context["n_vdos"] = lambda ps: steps(ps, params["vdos_dt_fs"])
    return _environment().get_template(f"{protocol}.in.j2").render(context)


def write_deck(
    protocol: str,
    system_dir: str | Path,
    out: str | Path,
    data: str | Path | None = None,
    overrides: dict | None = None,
    preset: str | None = None,
    run_dir: str | Path | None = None,
    require_data: bool = True,
) -> Path:
    """Render ``protocol`` and write it to ``out/in.<protocol>``; return the deck path.

    Paths in the deck are relative to ``run_dir`` (default ``out``), where LAMMPS runs;
    a Slurm job (``sepsim.lammps.slurm``) copies the deck from ``out`` into ``run_dir``.
    """
    out = Path(out)
    run_dir = out if run_dir is None else Path(run_dir)
    text = render_deck(
        protocol, system_dir, data, overrides, preset, deck_dir=run_dir, require_data=require_data
    )
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"in.{protocol}"
    path.write_text(text, newline="\n")
    return path
