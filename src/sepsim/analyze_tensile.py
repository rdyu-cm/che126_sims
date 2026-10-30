"""`sepsim analyze tensile` (D54): tensile runs -> results.md, results.json, PNGs.

Reads each run directory's deck (``in.tensile``: system id, resolved parameters from
the header) and its per-axis ``tensile_<axis>.txt`` (:mod:`sepsim.analysis.tensile`),
and writes to ``results/analysis/<system>/<stage>/`` (or ``--out``; several run
directories: ``results/analysis/<system>/tensile_compare/``). Nothing is written into
the run directories. The axes of one run are pseudo-replicas (same start snapshot,
different pull direction): per run the mean ± SD over axes; runs at the same T and rate
are also pooled.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path

import numpy as np

from sepsim.analysis.tensile import FLOW_WINDOW, SMOOTH_STRAIN, analyze_axis, mean_sd, read_ave_time
from sepsim.progress import deck_system, load_json

MD_NAME, JSON_NAME = "results.md", "results.json"
DECK = "in.tensile"
_PARAM = re.compile(r"^#\s{3}(\w+) = (.*)$")
SUMMARY_KEYS = ("E_MPa", "nu_fit", "nu_run", "peak_MPa", "peak_strain", "flow_MPa")

CAVEATS = [
    (
        "The box is an amorphous melt above Tg (Tg is below 25 °C for PE, D14), so the"
        " response is viscoelastic and rate-dependent: these are not the moduli of a"
        " semicrystalline separator, whose stiffness and yield come from its crystallinity."
    ),
    (
        "E_app is the apparent (high-frequency) modulus at the simulated strain rate, many"
        " orders of magnitude above experiment; it falls with the rate."
    ),
    (
        "There is no true yield in a melt: the peak or plateau is a viscous flow stress"
        " (≈ 3 η × rate for a Newtonian melt), again rate-dependent."
    ),
    (
        "ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed"
        " strain, so the lateral contraction trails the axial extension (ν low at small strain);"
        " a fully relaxed melt approaches ν = 0.5."
    ),
    (
        "Stress is -(P_axis - p_atm) from the virial pressure tensor averaged over avg_ps;"
        " the axes of one run start from the same snapshot, so their spread is not a full"
        " independent-sample error."
    ),
]


class TensileError(ValueError):
    """A run directory cannot be analysed (no tensile deck, no data)."""


def deck_params(deck: Path) -> dict[str, str]:
    """Resolved parameters from the deck header (``#   key = value``)."""
    out = {}
    for line in deck.read_text(errors="replace").splitlines():
        if not line.startswith("#"):
            break
        if m := _PARAM.match(line):
            out[m.group(1)] = m.group(2).strip()
    return out


def analyze_run(run_dir: Path, fit_max: float) -> dict:
    """Per-axis results and the mean ± SD over axes of one tensile run directory."""
    deck = run_dir / DECK
    if not deck.is_file():
        raise TensileError(f"{run_dir}: no {DECK} (not a tensile run directory)")
    params = deck_params(deck)
    system, res = deck_system(deck)
    manifest = load_json(run_dir / "run_manifest.json") or {}
    p_ref = float(params.get("p_atm", 1.0))
    axes = [a.strip() for a in params.get("axes", "x,y,z").split(",") if a.strip()]
    run = {
        "run_dir": str(run_dir.resolve()),
        "stage": run_dir.resolve().name,
        "system": system,
        "resolution": res,
        "status": manifest.get("status", "not started"),
        "node": manifest.get("hostname"),
        "t_c": float(params.get("t_c", "nan")),
        "rate_per_s": float(params.get("rate_per_s", "nan")),
        "strain_max": float(params.get("strain_max", "nan")),
        "avg_ps": float(params.get("avg_ps", "nan")),
        "p_atm": p_ref,
        "axes": [],
        "notes": [],
    }
    for ax in axes:
        path = run_dir / f"tensile_{ax}.txt"
        if not path.is_file():
            run["notes"].append(f"axis {ax}: tensile_{ax}.txt not found (not run yet)")
            continue
        try:
            r = analyze_axis(read_ave_time(path), ax, p_ref, fit_max)
        except ValueError as exc:
            run["notes"].append(f"axis {ax}: {exc}")
            continue
        if "error" in r:
            run["notes"].append(f"axis {ax}: {r['error']}")
            continue
        # the last average is centred half a window before the end
        window = run["rate_per_s"] * run["avg_ps"] * 1e-12
        if r["strain_max"] < run["strain_max"] - 1.5 * window:
            run["notes"].append(
                f"axis {ax}: reached strain {r['strain_max']:.3f} of {run['strain_max']:g}"
                " (running or stopped)"
            )
        run["axes"].append(r)
    if not run["axes"]:
        raise TensileError(f"{run_dir}: no tensile_<axis>.txt data")
    run["summary"] = {k: mean_sd(a.get(k) for a in run["axes"]) for k in SUMMARY_KEYS}
    return run


def analyze_tensile(
    run_dirs, out: str | Path | None = None, fit_max: float = 0.02, plots: bool = True
) -> tuple[dict, Path]:
    """Report dict and output directory for one or more tensile run directories."""
    if fit_max <= 0:
        raise TensileError("--fit-max must be > 0")
    runs = [analyze_run(Path(d), fit_max) for d in run_dirs]
    systems = sorted({r["system"] for r in runs if r["system"]})
    if out is None:
        if len(systems) != 1:
            raise TensileError(f"runs of several systems ({', '.join(systems)}): give --out")
        stage = runs[0]["stage"] if len(runs) == 1 else "tensile_compare"
        out_dir = Path("results") / "analysis" / systems[0] / stage
    else:
        out_dir = Path(out)
    groups: dict[tuple, list] = {}
    for r in runs:
        groups.setdefault((r["system"], r["t_c"], r["rate_per_s"]), []).append(r)
    pooled = [
        {
            "system": key[0],
            "t_c": key[1],
            "rate_per_s": key[2],
            "runs": [r["stage"] for r in rs],
            "summary": {k: mean_sd(a.get(k) for r in rs for a in r["axes"]) for k in SUMMARY_KEYS},
        }
        for key, rs in groups.items()
        if len(rs) > 1
    ]
    report = {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "fit_max": fit_max,
        "smooth_strain": SMOOTH_STRAIN,
        "flow_window": list(FLOW_WINDOW),
        "runs": runs,
        "pooled": pooled,
        "caveats": CAVEATS,
        "plots": {},
    }
    if plots:
        report["plots"] = make_plots(report, out_dir)
    return report, out_dir


def make_plots(report: dict, out_dir: Path) -> dict:
    """stress_strain.png (true stress, 1% moving average, fits) and poisson.png (secant
    ν vs strain); returns {name: {"file", "title"}}."""
    from sepsim.progress_plots import _save, plt

    out_dir.mkdir(parents=True, exist_ok=True)
    styles = ("-", "--", ":", "-.")
    colors = {"x": "C0", "y": "C1", "z": "C2"}
    fit_max = report["fit_max"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    fig2, ax3 = plt.subplots(figsize=(6, 4.2))
    for j, run in enumerate(report["runs"]):
        tag = f"{run['stage']} " if len(report["runs"]) > 1 else ""
        for a in run["axes"]:
            c, ls = a["curves"], styles[j % len(styles)]
            e = c["strain"]
            col = colors[a["axis"]]
            ax1.plot(e, c["sigma_true"], color=col, alpha=0.2, lw=0.6)
            ax1.plot(e, c["sigma_smooth"], color=col, ls=ls, label=f"{tag}{a['axis']}")
            near = e <= 5 * fit_max
            ax2.plot(e[near], c["sigma_true"][near], ".", color=col, ms=2, alpha=0.5)
            if a.get("E_MPa") is not None:
                xf = np.array([0.0, fit_max])
                ax2.plot(
                    xf,
                    a["E_intercept_MPa"] + a["E_MPa"] * xf,
                    color=col,
                    ls=ls,
                    label=f"{tag}{a['axis']}: E {a['E_MPa']:.0f} MPa",
                )
            ok = e > fit_max / 2
            ax3.plot(e[ok], c["nu_secant"][ok], color=col, ls=ls, label=f"{tag}{a['axis']}")
    ax1.set(
        xlabel="engineering strain",
        ylabel="true stress (MPa)",
        title=f"σ–ε (faint: {report['runs'][0]['avg_ps']:g} ps averages; lines:"
        f" {SMOOTH_STRAIN:g} strain moving average)",
    )
    ax2.axvline(fit_max, color="0.5", lw=0.8, ls=":")
    ax2.set(xlabel="engineering strain", ylabel="true stress (MPa)", title="E_app fits")
    ax3.axhline(0.5, color="0.5", lw=0.8, ls=":")
    ax3.set(
        xlabel="engineering strain",
        ylabel="ν = −ln(L_lat/L_lat0)/ln(1+ε)",
        title="secant Poisson ratio",
        ylim=(-0.2, 0.8),
    )
    for ax in (ax1, ax2, ax3):
        ax.legend(fontsize=7)
    _save(fig, out_dir / "stress_strain.png")
    _save(fig2, out_dir / "poisson.png")
    return {
        "stress_strain": {"file": "stress_strain.png", "title": "stress–strain and E_app fits"},
        "poisson": {"file": "poisson.png", "title": "secant Poisson ratio vs strain"},
    }


def _f(x, fmt: str = ".1f") -> str:
    return "n/a" if x is None else f"{x:{fmt}}"


def _ms(ms: dict | None, fmt: str) -> str:
    if not ms:
        return "n/a"
    return f"{ms['mean']:{fmt}}" + (f" ± {ms['sd']:{fmt}}" if ms["sd"] is not None else "")


def render_markdown(r: dict) -> str:
    """results.md for a tensile report."""
    lines = ["# Tensile analysis (D54)", ""]
    lines.append(
        f"Generated {r['generated']}. E_app and ν fitted over 0 ≤ ε ≤ {r['fit_max']:g};"
        f" peak after a {r['smooth_strain']:g}-strain moving average; flow stress = mean"
        f" true stress over ε ∈ [{r['flow_window'][0]:g}, {r['flow_window'][1]:g}]."
        " True stress σ = −(P_axis − p_atm), tension positive; engineering stress σ·A/A0."
    )
    for run in r["runs"]:
        lines += [
            "",
            f"## {run['system']} / {run['stage']}",
            "",
            f"- {run['t_c']:g} °C, {run['rate_per_s']:.3g} s⁻¹ to strain {run['strain_max']:g},"
            f" lateral {run['p_atm']:g} atm; status {run['status']}"
            + (f" on {run['node']}" if run.get("node") else "")
            + f"; `{run['run_dir']}`",
        ]
        lines += [f"- note: {n}" for n in run["notes"]]
        lines += [
            "",
            (
                "| axis | strain reached | E_app (MPa) | ν (fit) | ν (run) | σ_peak (MPa) |"
                " ε_peak | flow σ (MPa) | T (K) |"
            ),
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for a in run["axes"]:
            e = "n/a" if a["E_MPa"] is None else f"{a['E_MPa']:.0f} ± {a['E_err_MPa']:.0f}"
            peak = f"{a['peak_strain']:.3f}" + (" (end)" if a["peak_at_end"] else "")
            lines.append(
                f"| {a['axis']} | {a['strain_max']:.3f} | {e} | {_f(a['nu_fit'], '.2f')} |"
                f" {a['nu_run']:.2f} | {a['peak_MPa']:.1f} | {peak} | {_f(a['flow_MPa'])} |"
                f" {_f(a.get('temp_mean_K'))} |"
            )
        s = run["summary"]
        lines.append(
            f"| mean ± SD | | {_ms(s['E_MPa'], '.0f')} | {_ms(s['nu_fit'], '.2f')} |"
            f" {_ms(s['nu_run'], '.2f')} | {_ms(s['peak_MPa'], '.1f')} |"
            f" {_ms(s['peak_strain'], '.3f')} | {_ms(s['flow_MPa'], '.1f')} | |"
        )
    if r["pooled"]:
        lines += [
            "",
            "## Pooled over runs at the same T and rate",
            "",
            (
                "| system | T (°C) | rate (1/s) | runs | E_app (MPa) | ν (fit) | ν (run) |"
                " σ_peak (MPa) | flow σ (MPa) |"
            ),
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for p in r["pooled"]:
            s = p["summary"]
            lines.append(
                f"| {p['system']} | {p['t_c']:g} | {p['rate_per_s']:.3g} |"
                f" {', '.join(p['runs'])} | {_ms(s['E_MPa'], '.0f')} | {_ms(s['nu_fit'], '.2f')}"
                f" | {_ms(s['nu_run'], '.2f')} | {_ms(s['peak_MPa'], '.1f')} |"
                f" {_ms(s['flow_MPa'], '.1f')} |"
            )
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r["caveats"]]
    if r.get("plots"):
        lines += ["", "## Plots", ""]
        for p in r["plots"].values():
            lines += [f"**{p['title']}**", "", f"![{p['title']}]({p['file']})", ""]
    return "\n".join(lines) + "\n"


def _json(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return [None if isinstance(v, float) and not np.isfinite(v) else v for v in x.tolist()]
    raise TypeError(f"not JSON serializable: {type(x).__name__}")


def write_results(report: dict, out_dir: Path) -> None:
    """Write results.json (curves thinned to <= 2000 points) and results.md atomically."""
    out_dir.mkdir(parents=True, exist_ok=True)
    slim = json.loads(json.dumps(report, default=_thin_json))
    for name, text in (
        (JSON_NAME, json.dumps(slim, indent=1, sort_keys=True) + "\n"),
        (MD_NAME, render_markdown(report)),
    ):
        tmp = out_dir / (name + ".tmp")
        tmp.write_text(text)
        os.replace(tmp, out_dir / name)


def _thin_json(x):
    if isinstance(x, np.ndarray) and x.ndim >= 1 and x.shape[-1] > 2000:
        stride = -(-x.shape[-1] // 2000)
        x = x[..., ::stride]
    if isinstance(x, np.ndarray):
        x = np.where(np.isfinite(x), x, np.nan) if x.dtype.kind == "f" else x
        return [_nan_none(v) for v in x.tolist()]
    return _json(x)


def _nan_none(v):
    if isinstance(v, list):
        return [_nan_none(u) for u in v]
    return None if isinstance(v, float) and not np.isfinite(v) else v
