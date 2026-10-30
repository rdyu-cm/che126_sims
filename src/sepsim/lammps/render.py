"""Render plain LAMMPS input decks from Jinja templates for a built system.

A deck is rendered from ``templates/<protocol>.in.j2`` (``prep``, ``sweep``,
``benchmark``, ``extend``, ``cool``, ``diffuse``, ``tensile`` for bulk systems; ``pore_relax`` for wide 500 K
slit pores and ``pore`` for narrowed ones, D44/D48) and the system's
``manifest.yaml``: styles, mixing, special_bonds, type ids and SHAKE bond types come
from the manifest; every coefficient line is emitted from the force-field YAML via
``sepsim.ff.params.to_lammps_real`` (the deck must not rely on data-file coefficients,
because changing ``pair_style`` during the push-off discards them). Run parameters come
from a per-protocol, per-resolution defaults table (decisions D12a, D12c, D12g, D20,
D24, D25, D28, D31, D34-D39, D44, D47, D48, D53, D54), an optional preset (``smoke``) and ``key=value`` overrides, in that order. The deck
header lists every resolved parameter; output is deterministic (no timestamps).

Decks carry no accelerator ``package`` or suffix lines; pass ``-sf``/``-pk`` to ``lmp``.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import jinja2
import yaml

from sepsim import __version__
from sepsim.ff.params import FORCEFIELD_DIR, load_forcefield, to_lammps_real
from sepsim.run import sha256_file

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
PROTOCOLS = ("prep", "sweep", "benchmark", "pore_relax", "pore", "extend", "cool")
PROTOCOLS += ("diffuse", "tensile")  # D53, D54
# protocols for slit-pore systems (manifest has a ``pore`` key), by pore.kind (D48)
PORE_PROTOCOLS = {"pore_relax": "wide", "pore": "narrow"}
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
        # D46: dense bursts in every hold: burst_len_ps at burst_dt_ps (both ends written,
        # burst_len/burst_dt + 1 frames) at the start of every burst_period_ps; 0 = off
        "burst_period_ps": 1000.0,
        "burst_len_ps": 10.0,
        "burst_dt_ps": 0.1,
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

# Dry slit pores (D44, D48). Plain LJ cutoff at every resolution: the analytic tail
# correction assumes a homogeneous bulk. AA cutoff 14 A (bulk 12, D25); UA stays 14, CG 15.
_MIN_KEYS = ("min_etol", "min_ftol", "min_maxiter", "min_maxeval")
_PORE_FF = {
    res: {
        "tail": False,
        "lj_cutoff": 14.0 if res == "aa" else DEFAULTS[res]["lj_cutoff"],
    }
    for res in DEFAULTS
}
# Wide pore (D48 step 1): minimize, then NVT surface relaxation at 500 K with the box fixed.
PORE_RELAX_DEFAULTS = {
    res: {k: DEFAULTS[res][k] for k in (*_FF_KEYS, *_MIN_KEYS, "t_melt", "hold_dump_ps")}
    | _PORE_FF[res]
    | {"relax_ps": {"aa": 1000.0, "ua": 2000.0, "cg": 5000.0}[res]}
    for res in DEFAULTS
}
# Narrow pore (D48 step 2): minimize, short NVT re-relaxation at 500 K, the prep's step-cool
# and the bulk sweep, all NVT with the lateral box of the bulk density at each T (change_box).
PORE_DEFAULTS = {
    res: SWEEP_DEFAULTS[res]
    | {
        k: DEFAULTS[res][k]
        for k in (*_MIN_KEYS, "t_melt", "t_final", "cool_steps", "cool_step_ps", "cool_dump_ps")
    }
    | _PORE_FF[res]
    | {"rerelax_ps": {"aa": 500.0, "ua": 1000.0, "cg": 2000.0}[res]}
    for res in DEFAULTS
}

# Extended 500 K hold (D47): the prep's NPT hold continued from its hold.data, in
# chunks of chunk_ps, each ending in a write_data snapshot hold_ext_<ns>ns.data.
EXTEND_DEFAULTS = {
    res: {k: DEFAULTS[res][k] for k in (*_FF_KEYS, "t_melt", "hold_dump_ps")}
    | {"extend_ps": 80000.0, "chunk_ps": 10000.0}
    for res in DEFAULTS
}

# Step-cool alone (D47): the prep's Stage 7 from any 500 K snapshot -> cooled.data.
COOL_DEFAULTS = {
    res: {
        k: DEFAULTS[res][k]
        for k in (*_FF_KEYS, "t_melt", "t_final", "cool_steps", "cool_step_ps", "cool_dump_ps")
    }
    for res in DEFAULTS
}

# Long NPT hold at one sweep temperature for chain diffusion (D53): from the sweep's
# hold_<T>C.data, frames every hold_dump_ps into one hold.dcd, chunks of chunk_ps each
# ending in write_data hold_<cumulative ns>ns.data. t_c in deg C.
_DIFFUSE_RES = {
    "aa": {"diffuse_ps": 20000.0, "chunk_ps": 5000.0, "hold_dump_ps": 20.0},
    "ua": {"diffuse_ps": 100000.0, "chunk_ps": 10000.0, "hold_dump_ps": 100.0},
    "cg": {"diffuse_ps": 300000.0, "chunk_ps": 25000.0, "hold_dump_ps": 100.0},
}
DIFFUSE_DEFAULTS = {
    res: {k: DEFAULTS[res][k] for k in _FF_KEYS} | {"t_c": 25.0} | _DIFFUSE_RES[res]
    for res in DEFAULTS
}

# Uniaxial tensile test (D54): from the sweep's hold_<T>C.data, one segment per axis in
# ``axes`` (each re-reads the start data after ``clear``), fix deform erate along the
# axis, NPT at p_atm on the two lateral axes (coupled), averages every avg_ps into
# tensile_<axis>.txt, frames every tensile_dump_ps into tensile_<axis>.dcd.
TENSILE_AXES = ("x", "y", "z")
TENSILE_DEFAULTS = {
    res: {k: DEFAULTS[res][k] for k in _FF_KEYS}
    | {
        "t_c": 25.0,
        "rate_per_s": 1.0e8,  # engineering strain rate, 1/s
        "strain_max": 0.5,  # engineering strain at the end of each axis
        "axes": "x,y,z",
        "avg_ps": 1.0,  # fix ave/time window (every step averaged)
        "tensile_dump_ps": 100.0,
    }
    for res in DEFAULTS
}

PROTOCOL_DEFAULTS = {
    "prep": DEFAULTS,
    "sweep": SWEEP_DEFAULTS,
    "benchmark": BENCHMARK_DEFAULTS,
    "pore_relax": PORE_RELAX_DEFAULTS,
    "pore": PORE_DEFAULTS,
    "extend": EXTEND_DEFAULTS,
    "cool": COOL_DEFAULTS,
    "diffuse": DIFFUSE_DEFAULTS,
    "tensile": TENSILE_DEFAULTS,
}

# Data a protocol reads by default: a prep output in the sibling prep/ run directory.
DEFAULT_INPUT = {"sweep": "cooled.data", "benchmark": "compressed.data", "extend": "hold.data"}
# Protocols that read an earlier stage's output (results/runs/<id>/<stage>/): a relative
# --data path is taken relative to the run directory and may not exist yet. cool has no
# default input (the extension snapshot to cool is chosen once the D47 checks pass).
STAGE_INPUT = (*DEFAULT_INPUT, "cool", "diffuse", "tensile")
# Protocols run once per temperature (D53, D54): the default stage directory carries
# t_c (and a non-default tensile rate) so the runs do not overwrite each other.
PER_T_STAGE = ("diffuse", "tensile")

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
        "burst_period_ps": 1.0,
        "burst_len_ps": 0.2,
        "burst_dt_ps": 0.02,
        # pores
        "relax_ps": 1.0,
        "rerelax_ps": 1.0,
        # extend: two chunks of 1 ps
        "extend_ps": 2.0,
        "chunk_ps": 1.0,
        # diffuse: two chunks of 1 ps (chunk_ps above)
        "diffuse_ps": 2.0,
        # tensile: strain 0.01 at 1e10 /s = 1 ps per axis
        "strain_max": 0.01,
        "rate_per_s": 1.0e10,
        "avg_ps": 0.1,
        "tensile_dump_ps": 0.5,
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
    if protocol in ("sweep", "pore"):
        parse_grid(params["sweep_grid_c"])
        _check_bursts(params)
    if protocol == "extend" and not (params["extend_ps"] > 0 and params["chunk_ps"] > 0):
        raise RenderError("extend_ps and chunk_ps must be > 0")
    if protocol == "diffuse" and not (params["diffuse_ps"] > 0 and params["chunk_ps"] > 0):
        raise RenderError("diffuse_ps and chunk_ps must be > 0")
    if protocol == "tensile":
        if not (params["rate_per_s"] > 0 and params["strain_max"] > 0 and params["avg_ps"] > 0):
            raise RenderError("rate_per_s, strain_max and avg_ps must be > 0")
        tensile_axes(params)
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


def _check_bursts(params: dict) -> None:
    """Burst parameters (D46): off at period 0, else 0 < len <= period, len a multiple of dt."""
    period, length, dt_b = (params[k] for k in ("burst_period_ps", "burst_len_ps", "burst_dt_ps"))
    if period == 0:
        return
    if period < 0 or not 0 < length <= period or dt_b <= 0:
        raise RenderError(
            "bursts need 0 < burst_len_ps <= burst_period_ps and burst_dt_ps > 0"
            " (burst_period_ps=0 disables them)"
        )
    n_len, n_dt = steps(length, params["dt_fs"]), steps(dt_b, params["dt_fs"])
    if n_len % n_dt:
        raise RenderError(f"burst_len_ps {length} is not a multiple of burst_dt_ps {dt_b}")


def _bursts(params: dict, hold_ps: float, prefix: str) -> list[dict]:
    """Chunks of one hold (D46): a burst of burst_len_ps at the start of every
    burst_period_ps, then the rest of the chunk; the last chunk may be shorter."""
    period, length = params["burst_period_ps"], params["burst_len_ps"]
    if period == 0:
        return []
    chunks, t, k = [], 0.0, 0
    while hold_ps - t > 1e-9:
        span = min(period, hold_ps - t)
        burst = min(length, span)
        k += 1
        rest = span - burst if span - burst > 1e-9 else 0.0
        chunks.append({"file": f"{prefix}_burst{k:02d}.dcd", "burst_ps": burst, "rest_ps": rest})
        t += span
    return chunks


def extend_chunks(
    params: dict, total_key: str = "extend_ps", prefix: str = "hold_ext"
) -> list[dict]:
    """Chunks of the hold extension (D47): ``chunk_ps`` each (the last may be shorter),
    each ending in ``<prefix>_<cumulative ns>ns`` (written as .data). The diffusion hold
    (D53) uses ``diffuse_ps`` and the prefix ``hold``."""
    total, size = params[total_key], params["chunk_ps"]
    chunks, t = [], 0.0
    while total - t > 1e-9:
        ps = min(size, total - t)
        t += ps
        chunks.append({"ps": ps, "end_ns": t / 1000.0, "stage": f"{prefix}_{_num(t / 1000.0)}ns"})
    return chunks


def rate_label(rate_per_s: float) -> str:
    """Strain rate for names and headers: 1e8, 2.5e9, 3e10."""
    mant, exp = f"{float(rate_per_s):.3g}".partition("e")[::2]
    if not exp:
        return mant
    return f"{mant}e{int(exp)}"


def tensile_axes(params: dict) -> list[dict]:
    """Segments of the tensile deck (D54), one per axis in ``axes``: the pulled axis, the
    two lateral (barostatted, coupled) axes, the run length strain_max / (rate dt) and
    the per-axis file and variable names (variables survive ``clear``)."""
    axes = [a.strip().lower() for a in params["axes"].split(",") if a.strip()]
    if not axes or any(a not in TENSILE_AXES for a in axes) or len(set(axes)) != len(axes):
        raise RenderError(f"axes: expected distinct axes from x,y,z, got {params['axes']!r}")
    run_ps = params["strain_max"] / params["rate_per_s"] * 1e12
    out = []
    for k, ax in enumerate(axes):
        lat = [a for a in TENSILE_AXES if a != ax]
        out.append(
            {
                "index": k + 1,
                "ax": ax,
                "lat": lat,
                "couple": "".join(lat),
                "comp": TENSILE_AXES.index(ax) + 1,  # pressure tensor component (pxx = 1)
                "var": f"t{ax}",
                "txt": f"tensile_{ax}.txt",
                "dcd": f"tensile_{ax}.dcd",
                "run_ps": run_ps,
            }
        )
    return out


def default_stage(protocol: str, resolution: str, overrides: dict | None = None) -> str:
    """Default stage directory name: the protocol, or for the per-temperature protocols
    (D53, D54) ``diffuse_<T>C`` / ``tensile_<T>C`` with ``_r<rate>`` for a tensile rate
    other than the default (e.g. ``tensile_25C_r1e9``)."""
    if protocol not in PER_T_STAGE:
        return protocol
    p = resolve_params(resolution, None, overrides, protocol)
    name = f"{protocol}_{_label(p['t_c'])}"
    if protocol == "tensile" and p["rate_per_s"] != TENSILE_DEFAULTS[resolution]["rate_per_s"]:
        name += f"_r{rate_label(p['rate_per_s'])}"
    return name


_HOLD_DATA = re.compile(r"^hold_(m?)([\d.]+)C\.data$")


def data_temperature_warning(protocol: str, data: str | Path, t_c: float) -> str | None:
    """For diffuse/tensile (D53, D54): a warning when the input is a sweep snapshot
    ``hold_<T>C.data`` of another temperature than t_c, else None."""
    if protocol not in PER_T_STAGE:
        return None
    m = _HOLD_DATA.match(Path(data).name)
    if not m:
        return None
    t_data = float(m.group(2)) * (-1 if m.group(1) else 1)
    if abs(t_data - t_c) > 1e-6:
        return (
            f"{Path(data).name} is the {_num(t_data)} C sweep hold but t_c = {_num(t_c)} C"
            " (--set t_c=...)"
        )
    return None


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
                    "bursts": (
                        _bursts(params, params["sweep_hold_ps"], f"seg{idx:02d}_hold_{label}")
                        if is_hold
                        else []
                    ),
                    "box": None,  # pore decks: the D48 lateral box at this T (change_box)
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


def _check_burst_alignment(protocol: str, params: dict, segments: list[dict]) -> None:
    """Every burst must start on a multiple of its dump interval, so it gets its first
    frame and burst_len/burst_dt + 1 frames in all. The deck's step counter starts at 0
    (read_data; the pore deck resets it after the minimization and runs the 500 K
    re-relaxation and the step-cool before the sweep)."""
    dt = params["dt_fs"]
    every = steps(params["burst_dt_ps"], dt) if params["burst_period_ps"] else 0
    step = 0
    if protocol == "pore":
        step = steps(params["rerelax_ps"], dt) + params["cool_steps"] * steps(
            params["cool_step_ps"], dt
        )
    for seg in segments:
        for c in seg["bursts"]:
            if step % every:
                raise RenderError(
                    f"{c['file']} would start at step {step}, not a multiple of the burst"
                    f" interval {every}: choose durations that are multiples of burst_dt_ps"
                )
            step += steps(c["burst_ps"], dt) + (steps(c["rest_ps"], dt) if c["rest_ps"] else 0)
        if not seg["bursts"]:
            step += steps(seg["ps"], dt)
        if seg["vdos"]:
            step += steps(params["vdos_ps"], params["vdos_dt_fs"])


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
    """Default input data: ``SYSTEM/data.lmp`` for prep and the pores; for sweep/benchmark/extend
    the prep output (``cooled.data`` / ``compressed.data`` / ``hold.data``) in the sibling
    ``prep/`` run directory. cool has no default."""
    if protocol == "cool":
        raise RenderError("cool: give the data file to cool (--data), e.g. an extension snapshot")
    if protocol in PER_T_STAGE:
        raise RenderError(f"{protocol}: give the data file (--data), e.g. ../sweep/hold_25C.data")
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
    pore = manifest.get("pore")
    if (pore is not None) != (protocol in PORE_PROTOCOLS):
        raise RenderError(
            f"{manifest['id']}: the {protocol} protocol is for "
            + ("slit-pore systems (use prep/sweep/benchmark)" if pore is None else "bulk systems")
            + ("" if pore is None else f"; pore systems use {', '.join(PORE_PROTOCOLS)}")
        )
    if pore is not None and pore.get("kind") != PORE_PROTOCOLS[protocol]:
        want = {v: k for k, v in PORE_PROTOCOLS.items()}.get(pore.get("kind"))
        raise RenderError(
            f"{manifest['id']}: {protocol} is for {PORE_PROTOCOLS[protocol]} pores (D48); this"
            f" is a {pore.get('kind') or 'D44 (superseded)'} pore"
            + (f": use {want}" if want else ": rebuild it with sepsim build pore")
        )
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
    p_atm, pdamp = _num(params["p_atm"]), _num(params["pdamp_dt"] * dt)
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
        "pore": pore,
        # D9/D12g: iso for bulk; pores run NVT with the D48 lateral box (no barostat)
        "barostat": f"iso {p_atm} {p_atm} {pdamp}",
        "cool_boxes": None,
        # step counts at the production timestep
        "n": lambda ps: steps(ps, dt),
    }
    if protocol in ("prep", "cool", "pore"):
        t0, t1, n = params["t_melt"], params["t_final"], params["cool_steps"]
        context["cool_temps"] = [t0 + (t1 - t0) * (k + 1) / n for k in range(n)]
        context["n_push"] = lambda ps: steps(ps, params.get("pushoff_dt_fs", dt))
    if protocol == "extend":
        context["chunks"] = extend_chunks(params)
    elif protocol == "diffuse":
        context["chunks"] = extend_chunks(params, "diffuse_ps", "hold")
    elif protocol == "tensile":
        context["axes"] = tensile_axes(params)
        context["rate"] = rate_label(params["rate_per_s"])
    elif protocol in ("sweep", "pore"):
        context["segments"] = sweep_segments(params)
        context["n_vdos"] = lambda ps: steps(ps, params["vdos_dt_fs"])
        _check_burst_alignment(protocol, params, context["segments"])
    if protocol == "pore":
        _pore_boxes(context, manifest, params)
    return _environment().get_template(f"{protocol}.in.j2").render(context)


def _pore_boxes(context: dict, manifest: dict, params: dict) -> None:
    """D48 lateral boxes of a pore deck: the 500 K re-relaxation and each step-cool stage
    on the bulk cooling branch, each sweep segment that changes T on the heating branch;
    x and y centred on the data box, z untouched. ``box_table`` lists them all."""
    from sepsim.build.pore import PoreError, bulk_density, lateral_lengths

    lat = manifest["pore"].get("lateral")
    if not lat:
        raise RenderError(f"{manifest['id']}: manifest has no pore.lateral table (D48)")
    centre = [0.5 * (lo + hi) for lo, hi in manifest["box_angstrom"][:2]]

    def box(label: str, branch: str, t_k: float) -> dict:
        try:
            lx, ly = lateral_lengths(lat, branch, t_k)
            rho = bulk_density(lat, branch, t_k)
        except PoreError as exc:
            raise RenderError(f"{label}: {exc}") from None
        return {
            "label": label,
            "branch": branch,
            "t_k": t_k,
            "rho": rho,
            "lx": lx,
            "ly": ly,
            "x": (centre[0] - 0.5 * lx, centre[0] + 0.5 * lx),
            "y": (centre[1] - 0.5 * ly, centre[1] + 0.5 * ly),
        }

    n = params["cool_steps"]
    context["relax_box"] = box("re-relax", "cooling", params["t_melt"])
    context["cool_boxes"] = [
        box(f"cool {k + 1}/{n}", "cooling", t) for k, t in enumerate(context["cool_temps"])
    ]
    for seg in context["segments"]:
        if seg["new_fix"]:
            seg["box"] = box(f"seg {seg['index']:02d} {seg['kind']}", "heating", seg["t_k"])
    context["box_table"] = [
        context["relax_box"],
        *context["cool_boxes"],
        *(s["box"] for s in context["segments"] if s["box"]),
    ]


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
