"""`sepsim analyze cavitation` (D58): cavitation runs -> results.md, results.json, PNGs.

Reads each run directory's deck (``in.cavitation``: system id, resolved parameters from
the header), its ``cavitation.txt`` (:mod:`sepsim.analysis.cavitation`) and, when
present, ``cavitation.dcd`` (voids per frame), and writes to
``results/analysis/<system>/<stage>/`` (or ``--out``; several run directories:
``results/analysis/<system>/cavitation_compare/``). Nothing is written into the run
directories. Runs of one system at the same T, rate and mode (replica snapshots, tags)
are pooled: mean ± SD. K_app is shown next to 1/κ_T of the system's sweep hold at that T
when ``results/analysis/<system>/sweep/results.json`` has it.
"""

from __future__ import annotations

import datetime as dt
import json
import warnings
from pathlib import Path

import numpy as np

from sepsim.analysis import cavitation as C
from sepsim.analysis.tensile import mean_sd, read_ave_time
from sepsim.analyze_tensile import _ms, _thin_json
from sepsim.progress import deck_params, deck_system, load_json
from sepsim.reporting import _f, dump_json, plots_markdown, write_atomic

MD_NAME, JSON_NAME = "results.md", "results.json"
DECK = "in.cavitation"
SUMMARY_KEYS = ("sigma_cav_MPa", "ev_cav", "drop_MPa", "plateau_MPa", "K_app_MPa", "ev_void")
ANALYSIS_ROOT = Path("results") / "analysis"

CAVEATS = [
    (
        "The box is an amorphous melt (no crystallinity): cavitation of a melt under fast"
        " triaxial tension, not the cavitation of the amorphous layers between lamellae of a"
        " stretched semicrystalline separator."
    ),
    (
        "MD strain rates (10⁸–10¹⁰ s⁻¹ per axis) are many orders of magnitude above"
        " experiment, and CG time runs ≈ 4× fast: σ_cav is rate-inflated."
    ),
    (
        "The strain is homogeneous and affine (fix deform with remap x): the box cannot"
        " neck or localise beyond its size, and NVT removes the heat of the deformation."
    ),
    (
        "Voids are defined by a probe: space farther than the probe radius from every bead"
        " centre, swept by the probe sphere, on a 2 Å grid; the volumes depend on the probe"
        " radius (--probe-a)."
    ),
    (
        "A small periodic box holds about one void: after cavitation it grows as a single"
        " cavity, so the plateau stress is box-size dependent (compare the 2×2×2 box)."
    ),
    (
        "Plain LJ cutoff without tail correction: the missing attractive tail grows in"
        " magnitude as the density drops, biasing σ_h low at large strain."
    ),
]


class CavitationError(ValueError):
    """A run directory cannot be analysed (no cavitation deck, no data)."""


def _params(deck: Path, resolution: str) -> dict:
    """Resolved parameters from the deck header, typed like the cavitation defaults."""
    from sepsim.lammps.render import CAVITATION_DEFAULTS, _coerce

    defaults = CAVITATION_DEFAULTS[resolution]
    params = dict(defaults)
    for key, value in deck_params(deck).items():
        if key in defaults:
            params[key] = _coerce(key, value, defaults[key])
    return params


def bulk_modulus(system: str, t_c: float, root: Path = ANALYSIS_ROOT) -> float | None:
    """1/κ_T (MPa) of the system's sweep hold at t_c from its `analyze sweep` results."""
    res = load_json(root / system / "sweep" / JSON_NAME) or {}
    for h in res.get("holds") or []:
        k = (h.get("kappa") or {}).get("kappa_T_GPa")
        if h.get("t_c") is not None and abs(h["t_c"] - t_c) < 1e-6 and k:
            return 1000.0 / k
    return None


def voids(dcd: Path, probe_a: float) -> dict | None:
    """Void statistics per frame of cavitation.dcd (volume strain from the box)."""
    from MDAnalysis.coordinates.DCD import DCDReader

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reader = DCDReader(str(dcd))
    rows = []
    try:
        for ts in reader:
            lengths = np.asarray(ts.dimensions[:3], dtype=float)
            rows.append(C.void_stats(ts.positions.astype(float), lengths, probe_a))
    finally:
        reader.close()
    if not rows:
        return None
    v0, phi0 = rows[0]["volume_A3"], rows[0]["phi_v"]
    ev = [r["volume_A3"] / v0 - 1.0 for r in rows]
    phi_rel = [r["phi_v"] - phi0 for r in rows]
    largest = [r["largest_A3"] for r in rows]
    return {
        "frames": len(rows),
        "probe_A": probe_a,
        "phi_v0": phi0,
        "ev": ev,
        "phi_rel": phi_rel,
        "largest_A3": largest,
        "r_void_A": [r["r_void_A"] for r in rows],
        "n_voids": [r["n_voids"] for r in rows],
        "ev_first_void": C.first_void(ev, largest),
    }


def analyze_run(run_dir: Path, probe_a: float = C.PROBE_A) -> dict:
    """One cavitation run directory: the σ_h curve and (with its DCD) the voids."""
    deck = run_dir / DECK
    if not deck.is_file():
        raise CavitationError(f"{run_dir}: no {DECK} (not a cavitation run directory)")
    system, res = deck_system(deck)
    params = _params(deck, res or "cg")
    run = {
        "run_dir": str(run_dir.resolve()),
        "stage": run_dir.resolve().name,
        "system": system,
        "resolution": res,
        "status": (load_json(run_dir / "run_manifest.json") or {}).get("status", "not started"),
        "t_c": params["t_c"],
        "rate_per_s": params["rate_per_s"],
        "strain_max": params["strain_max"],
        "cav_mode": params["cav_mode"],
        "tag": params["tag"],
        "p_atm": params["p_atm"],
        "notes": [],
    }
    path = run_dir / "cavitation.txt"
    if not path.is_file():
        raise CavitationError(f"{run_dir}: cavitation.txt not found (not run yet)")
    try:
        data = read_ave_time(path, required=C.COLUMNS)
    except ValueError as exc:
        raise CavitationError(str(exc)) from None
    t_ps = data["step"] * params["dt_fs"] / 1000.0
    curve = C.analyze_curve(t_ps, data["ev"], C.hydrostatic_stress(data["press"], params["p_atm"]))
    if "error" in curve:
        raise CavitationError(f"{run_dir}: {curve['error']}")
    run["curve"] = curve
    if curve["cav_at_end"]:
        run["notes"].append("σ_h still rising at the end of the run: no cavitation peak yet")
    if curve["plateau_MPa"] is None:
        run["notes"].append(f"run ends before ε_V,cav + {C.PLATEAU_OFFSET:g}: no plateau stress")
    if "temp" in data:
        run["temp_mean_K"] = float(np.mean(data["temp"]))
    dcd = run_dir / "cavitation.dcd"
    run["voids"] = voids(dcd, probe_a) if dcd.is_file() else None
    if run["voids"] is None:
        run["notes"].append("no cavitation.dcd frames: void analysis skipped")
    run["inv_kappa_MPa"] = bulk_modulus(system, run["t_c"]) if system else None
    run["summary"] = {
        "sigma_cav_MPa": curve["sigma_cav_MPa"],
        "ev_cav": curve["ev_cav"],
        "drop_MPa": curve["drop_MPa"],
        "plateau_MPa": curve["plateau_MPa"],
        "K_app_MPa": curve["K_app_MPa"],
        "ev_void": (run["voids"] or {}).get("ev_first_void"),
    }
    return run


def analyze_cavitation(
    run_dirs, out: str | Path | None = None, probe_a: float = C.PROBE_A, plots: bool = True
) -> tuple[dict, Path]:
    """Report dict and output directory for one or more cavitation run directories."""
    if probe_a <= 0:
        raise CavitationError("--probe-a must be > 0")
    runs = [analyze_run(Path(d), probe_a) for d in run_dirs]
    systems = sorted({r["system"] for r in runs if r["system"]})
    if out is None:
        if len(systems) != 1:
            raise CavitationError(f"runs of several systems ({', '.join(systems)}): give --out")
        stage = runs[0]["stage"] if len(runs) == 1 else "cavitation_compare"
        out_dir = ANALYSIS_ROOT / systems[0] / stage
    else:
        out_dir = Path(out)
    groups: dict[tuple, list] = {}
    for r in runs:
        groups.setdefault((r["system"], r["t_c"], r["rate_per_s"], r["cav_mode"]), []).append(r)
    pooled = [
        {
            "system": key[0],
            "t_c": key[1],
            "rate_per_s": key[2],
            "cav_mode": key[3],
            "runs": [r["stage"] for r in rs],
            "summary": {k: mean_sd(r["summary"][k] for r in rs) for k in SUMMARY_KEYS},
        }
        for key, rs in sorted(groups.items())
    ]
    report = {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "smooth_ps": C.SMOOTH_PS,
        "probe_A": probe_a,
        "runs": runs,
        "pooled": pooled,
        "caveats": CAVEATS,
        "plots": {},
    }
    if plots:
        report["plots"] = make_plots(report, out_dir)
    return report, out_dir


def _legend(ax, size: int) -> None:
    if ax.get_legend_handles_labels()[0]:
        ax.legend(fontsize=size)


def make_plots(report: dict, out_dir: Path) -> dict:
    """sigma_vs_strain.png, void_fraction.png (with DCD frames) and cavitation_vs_T.png;
    returns {name: {"file", "title"}}."""
    from sepsim.progress_plots import _save, plt

    out_dir.mkdir(parents=True, exist_ok=True)
    plots = {}
    fig, ax = plt.subplots(figsize=(7, 4.4))
    for j, run in enumerate(report["runs"]):
        c, col = run["curve"]["curves"], f"C{j % 10}"
        ax.plot(c["ev"], c["sigma_h"], color=col, alpha=0.2, lw=0.6)
        ax.plot(c["ev"], c["sigma_smooth"], color=col, label=f"{run['stage']}")
        ax.plot([run["curve"]["ev_cav"]], [run["curve"]["sigma_cav_MPa"]], "o", color=col)
    ax.set(
        xlabel="volume strain ε_V = V/V0 − 1",
        ylabel="σ_h = −(P − p_atm) (MPa)",
        title=f"hydrostatic stress (lines: {report['smooth_ps']:g} ps moving average)",
    )
    _legend(ax, 7)
    _save(fig, out_dir / "sigma_vs_strain.png")
    plots["sigma_vs_strain"] = {"file": "sigma_vs_strain.png", "title": "σ_h vs volume strain"}

    with_voids = [r for r in report["runs"] if r["voids"]]
    if with_voids:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
        for j, run in enumerate(with_voids):
            v, col = run["voids"], f"C{j % 10}"
            ax1.plot(v["ev"], np.array(v["phi_rel"]) * 100, color=col, label=run["stage"])
            ax2.plot(v["ev"], np.array(v["r_void_A"]) / 10, color=col, label=run["stage"])
            if v["ev_first_void"] is not None:
                for ax in (ax1, ax2):
                    ax.axvline(v["ev_first_void"], color=col, ls=":", lw=0.8)
        ax1.set(
            xlabel="ε_V",
            ylabel="φ_v − φ_v(0) (%)",
            title=f"void fraction (probe {report['probe_A']:g} Å)",
        )
        ax2.axhline(1.0, color="0.5", ls=":", lw=0.8)
        ax2.set(xlabel="ε_V", ylabel="R_void (nm)", title="largest void, equivalent radius")
        for ax in (ax1, ax2):
            _legend(ax, 7)
        _save(fig, out_dir / "void_fraction.png")
        plots["void_fraction"] = {"file": "void_fraction.png", "title": "void fraction and size"}

    fig, axes = plt.subplots(1, 4, figsize=(15, 3.8))
    series: dict[tuple, list] = {}
    for p in report["pooled"]:
        series.setdefault((p["system"], p["rate_per_s"], p["cav_mode"]), []).append(p)
    keys = ("sigma_cav_MPa", "ev_cav", "plateau_MPa", "K_app_MPa")
    for (system, rate, mode), ps in sorted(series.items()):
        t = [p["t_c"] for p in ps]
        for ax, key in zip(axes, keys, strict=True):
            ms = [p["summary"][key] for p in ps]
            y = [m["mean"] if m else np.nan for m in ms]
            e = [(m["sd"] or 0.0) if m else 0.0 for m in ms]
            lab = f"{rate:.3g} /s" + ("" if mode == "triaxial" else f" {mode}")
            ax.errorbar(t, y, yerr=e, marker="o", capsize=3, label=lab)
    labels = ("σ_cav (MPa)", "ε_V,cav", "plateau σ_h (MPa)", "K_app (MPa)")
    for ax, lab in zip(axes, labels, strict=True):
        ax.set(xlabel="T (°C)", ylabel=lab)
        _legend(ax, 7)
    _save(fig, out_dir / "cavitation_vs_T.png")
    plots["cavitation_vs_T"] = {"file": "cavitation_vs_T.png", "title": "cavitation vs T"}
    return plots


def render_markdown(r: dict) -> str:
    """results.md for a cavitation report."""
    lines = ["# Cavitation analysis (D58)", ""]
    lines.append(
        f"Generated {r['generated']}. σ_h = −(P − p_atm) in MPa (tension positive), smoothed"
        f" over {r['smooth_ps']:g} ps; σ_cav = its maximum at ε_V,cav (ε_V = V/V0 − 1); drop ="
        f" σ_cav − the lowest smoothed σ_h after it; plateau = mean σ_h over ε_V ≥ ε_V,cav +"
        f" {C.PLATEAU_OFFSET:g}; K_app = dσ_h/dε_V over ε_V ≤ {C.K_FIT_MAX:g}. Voids: probe"
        f" {r['probe_A']:g} Å on a {C.VOXEL_A:g} Å grid; first void = largest void >"
        f" {C.FIRST_VOID_A3 / 1000:.1f} nm³ (R = 1 nm) for {C.FIRST_VOID_FRAMES} frames"
        " in a row."
    )
    for run in r["runs"]:
        c, v = run["curve"], run["voids"]
        lines += [
            "",
            f"## {run['system']} / {run['stage']}",
            "",
            (
                f"- {run['t_c']:g} °C, {run['rate_per_s']:.3g} s⁻¹ per axis ({run['cav_mode']}) to"
                f" strain {run['strain_max']:g}; status {run['status']}; `{run['run_dir']}`"
            ),
        ]
        lines += [f"- note: {n}" for n in run["notes"]]
        inv_k = run.get("inv_kappa_MPa")
        lines += [
            "",
            "| quantity | value |",
            "|---|---|",
            f"| σ_cav (MPa) | {c['sigma_cav_MPa']:.1f}{' (at end)' if c['cav_at_end'] else ''} |",
            f"| ε_V,cav (pressure) | {c['ev_cav']:.3f} |",
            f"| ε_V at the first void (voids) | {_f((v or {}).get('ev_first_void'), '.3f')} |",
            f"| drop after σ_cav (MPa) | {c['drop_MPa']:.1f} |",
            f"| plateau σ_h (MPa) | {_f(c['plateau_MPa'], '.1f')} |",
            f"| K_app (MPa) | {_f(c['K_app_MPa'], '.0f')}"
            + (f" ± {c['K_app_err_MPa']:.0f}" if c["K_app_err_MPa"] is not None else "")
            + (f"; 1/κ_T (sweep) {inv_k:.0f}" if inv_k else "")
            + " |",
            f"| T mean (K) | {_f(run.get('temp_mean_K'), '.1f')} |",
        ]
        if v:
            k = int(np.argmax(v["largest_A3"]))
            lines.append(
                f"| largest void (frame {k}) | {v['largest_A3'][k] / 1000:.2f} nm³, R_void"
                f" {v['r_void_A'][k] / 10:.2f} nm, {v['n_voids'][k]} voids > 1 nm³ at ε_V"
                f" {v['ev'][k]:.3f} |"
            )
    lines += [
        "",
        "## Pooled over runs at the same T, rate and mode (replicas, tags)",
        "",
        (
            "| system | T (°C) | rate (1/s) | mode | runs | σ_cav (MPa) | ε_V,cav | plateau (MPa) |"
            " K_app (MPa) | ε_V first void |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in r["pooled"]:
        s = p["summary"]
        lines.append(
            f"| {p['system']} | {p['t_c']:g} | {p['rate_per_s']:.3g} | {p['cav_mode']} |"
            f" {', '.join(p['runs'])} | {_ms(s['sigma_cav_MPa'], '.1f')} |"
            f" {_ms(s['ev_cav'], '.3f')} | {_ms(s['plateau_MPa'], '.1f')} |"
            f" {_ms(s['K_app_MPa'], '.0f')} | {_ms(s['ev_void'], '.3f')} |"
        )
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r["caveats"]]
    lines += plots_markdown(r.get("plots"))
    return "\n".join(lines) + "\n"


def write_results(report: dict, out_dir: Path) -> None:
    """Write results.json (curves thinned to <= 2000 points) and results.md atomically."""
    slim = json.loads(json.dumps(report, default=_thin_json))
    write_atomic(
        out_dir,
        ((JSON_NAME, dump_json(slim, default=None)), (MD_NAME, render_markdown(report))),
    )
