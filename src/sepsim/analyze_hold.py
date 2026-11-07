"""Isothermal NPT hold analysis: `sepsim analyze hold` (D56).

For an ``extend`` (D47, 500 K) or ``diffuse`` (D53) run directory
``results/runs/<system>/<stage>/`` this writes ``results.md``, ``results.json`` and PNG
plots into ``results/analysis/<system>/<stage>/`` (or ``--out``), reusing the sweep
machinery (:mod:`sepsim.analyze`):

- thermo of the hold (its chunk runs concatenated; a running or cancelled hold uses the
  rows present): T, density, enthalpy, volume as mean +- SEM without the first 10%
  (``window_stats``, D55 block means) and kappa_T from the volume fluctuations;
- the hold DCD (``hold_ext.dcd`` / ``hold.dcd``) with ``hold_trajectory``: MSD, chain COM
  MSD and D_COM (D49 with the D55 >= 2<Rg^2> criterion), bond P2, Rg, R_ee, C_n, and the
  D56 chain relaxation (end-to-end and Rouse mode ACFs) and crystallinity monitor.

``extend``: the sibling prep's ``../prep/hold.dcd`` is read ahead of ``hold_ext.dcd`` as
one continuous 500 K trajectory (the extension starts from the prep hold's last
snapshot, velocities kept), as `sepsim progress` does for the D47 criteria, so the lags
reach half the combined hold; without it (or with a different frame interval) the
extension alone is analysed, with a note. Thermo is the extension's own log.
"""

from __future__ import annotations

from pathlib import Path

from sepsim.analysis.lammps_log import read_log
from sepsim.analyze import (
    HOLD_SKIP,
    MAX_FRAMES,
    AnalyzeError,
    draw_plots,
    hold_trajectory,
    kappa_t,
    out_dir_for,
    relaxation_markdown,
    window_stats,
)
from sepsim.analyze import write_results as _write
from sepsim.progress import (
    LOG_NAME,
    MIN_STAT_ROWS,
    _concat_thermo,
    _prep_hold_dcd,
    deck_system,
    find_deck,
    load_json,
    parse_deck,
    runs_by_segment,
)
from sepsim.reporting import (
    CG_TIME_NOTE,
    _f,
    _pm,
    header_markdown,
    load_system_arrays,
    plots_markdown,
    report_header,
    trajectory_or_note,
)
from sepsim.run import MANIFEST_NAME

VERSION = 1
HOLD_DCD = {"extend": "hold_ext.dcd", "diffuse": "hold.dcd"}


def hold_thermo(segments, log, seg, notes: list[str] | None = None) -> tuple[dict | None, bool]:
    """Thermo rows of segment ``seg`` (its chunk runs concatenated; incomplete runs
    included) and whether all its runs are complete; blocks assigned as in `sepsim
    progress` (:func:`sepsim.progress.runs_by_segment`, plan-mismatch notes to ``notes``)."""
    per_seg, mismatch = runs_by_segment(segments, log)
    if notes is not None:
        notes += mismatch
    mine = per_seg[segments.index(seg)]
    if not mine:
        return None, False
    done = len(mine) == len(seg.run_steps) and all(r.complete for r in mine)
    return _concat_thermo(mine), done


def analyze_hold(
    run_dir: str | Path,
    out: str | Path | None = None,
    systems: str | Path = "systems",
    max_frames: int = MAX_FRAMES,
    plots: bool = True,
) -> tuple[dict, Path]:
    """Analyse an extend or diffuse run directory; returns (report, output directory)."""
    run_dir = Path(run_dir)
    manifest = load_json(run_dir / MANIFEST_NAME)
    deck = find_deck(run_dir, manifest)
    if deck is None:
        raise AnalyzeError(f"{run_dir}: no deck (in.*) found")
    protocol = deck.name.split(".", 1)[1]
    if protocol not in HOLD_DCD:
        raise AnalyzeError(
            f"{run_dir}: deck {deck.name} is not an isothermal hold (in.extend, in.diffuse);"
            " sweeps: `sepsim analyze sweep`, pores: `sepsim analyze pore`"
        )
    if not (run_dir / LOG_NAME).is_file():
        raise AnalyzeError(f"{run_dir}: no {LOG_NAME}")
    name = HOLD_DCD[protocol]
    segments = parse_deck(deck)
    seg = next((s for s in segments if name in s.dcd), None)
    if seg is None:
        raise AnalyzeError(f"{run_dir}: no segment of {deck.name} dumps {name}")
    system, resolution = deck_system(deck)
    system = system or run_dir.resolve().parent.name
    out_dir = out_dir_for(run_dir, system, out)
    log = read_log(run_dir / LOG_NAME)
    t_k = seg.t_target_k
    report = report_header(VERSION, run_dir, manifest, system, resolution)
    report.update(
        protocol=protocol,
        segment=seg.name,
        t_k=t_k,
        t_c=None if t_k is None else t_k - 273.15,
        planned_ns=seg.steps * seg.dt_fs / 1e6,
        method={
            "hold_window": f"without the first {HOLD_SKIP:.0%} of rows",
            "sem": "100 ps block means (D55)",
            "max_frames": max_frames,
        },
        notes=[],
    )
    th, done = hold_thermo(segments, log, seg, report["notes"])
    report["complete"] = done
    if th is None or len(th.get("Step", ())) < MIN_STAT_ROWS:
        report["notes"].append("no thermo rows for the hold yet")
        report["stats"] = report["kappa"] = None
    else:
        if not done:
            report["notes"].append("hold not complete: thermo and trajectory over the part run")
        report["stats"] = window_stats(th, HOLD_SKIP)
        report["kappa"] = kappa_t(th, t_k, HOLD_SKIP) if t_k else None

    before = []
    if protocol == "extend":  # seg dumps `name` (chosen above)
        frame_ps = seg.dump_every[seg.dcd.index(name)] * seg.dt_fs / 1000.0
        prep, note = _prep_hold_dcd(run_dir, frame_ps)
        if note:
            report["notes"].append(note)
        if prep is not None:
            before = [prep]
    report["combined_with"] = [str(b) for b in before]
    sys_arr = load_system_arrays(Path(systems) / system, report["notes"])
    report["traj"] = trajectory_or_note(
        True,
        sys_arr,
        True,
        "hold",
        lambda: hold_trajectory(run_dir, seg, sys_arr, max_frames, before=before),
    )
    report["caveats"] = hold_caveats(report, name)
    if plots:
        report["plots"] = make_plots(report, out_dir)
    return report, out_dir


def hold_caveats(report: dict, dcd_name: str) -> list[str]:
    """The hold report's caveats: the relaxation lag window, CG time, no trajectory."""
    caveats = []
    tr = report["traj"]
    if tr.get("available"):
        lag = tr["relaxation"]["lag_max_ps"]
        caveats.append(
            f"Relaxation times use lags up to half the analysed hold ({lag / 1000:g} ns); a"
            " time beyond that is 'not reached' and only the extrapolated exponential fit"
            " is given."
        )
    if report["resolution"] == "cg":
        caveats.append(CG_TIME_NOTE)
    if not tr.get("available"):
        caveats.append(
            f"No trajectory results: {dcd_name} is not in this run directory (a run on another"
            " node may keep its DCD there) or could not be read."
        )
    return caveats


def make_plots(report: dict, out_dir: Path) -> dict:
    from sepsim import analyze_plots as ap

    title = f"{report['system']} / {report['stage']}"
    tr = report["traj"]
    jobs = []
    if tr.get("available"):
        h = [{"t_c": report["t_c"] or 0.0, "traj": tr}]
        jobs += [
            ("msd", "backbone-site and chain COM MSD", lambda p: ap.msd_curves(p, h, title)),
            ("p2_acf", "bond P2 autocorrelation", lambda p: ap.p2_curves(p, h, title)),
            (
                "relaxation",
                "end-to-end and Rouse mode ACFs, p²τ_p vs p",
                lambda p: ap.relaxation_curves(p, [(h[0]["t_c"], tr)], title),
            ),
        ]
    return draw_plots(jobs, report, out_dir)


def render_markdown(r: dict) -> str:
    """results.md for one hold analysis."""
    lines = header_markdown(r, "Hold analysis", "hold", "D56", f"{r['protocol']}, ")
    lines.append(
        f"- segment: {r['segment']} ({r['planned_ns']:g} ns planned,"
        f" {'complete' if r['complete'] else 'not complete'}); thermo window"
        f" {r['method']['hold_window']}, SEM from {r['method']['sem']}"
    )
    if r.get("combined_with"):
        lines.append(
            "- trajectory: "
            + " + ".join(f"`{p}`" for p in r["combined_with"])
            + " read ahead of the hold DCD as one continuous trajectory (D47)"
        )
    for n in r.get("notes", []):
        lines.append(f"- note: {n}")
    st, k = r.get("stats") or {}, r.get("kappa")
    lines += ["", "## Thermo", ""]
    if st:
        lines += [
            "| window (ns) | T (°C) | density (g/cm³) | H (kcal/mol) | V (Å³) | κ_T (GPa⁻¹) |",
            "|---|---|---|---|---|---|",
            f"| {st.get('window_ps', 0) / 1000:.2f} | {_pm(st.get('t_c'), '.2f')} |"
            f" {_pm(st.get('density'), '.5f')} | {_pm(st.get('enthalpy'), '.1f')} |"
            f" {_pm(st.get('volume'), '.0f')} |"
            + (f" {k['kappa_T_GPa']:.3f} ± {k['sem']:.3f} |" if k else " n/a |"),
        ]
    else:
        lines.append("No thermo yet.")
    t = r["traj"]
    lines += ["", "## Trajectory: mobility and chain size", ""]
    if not t.get("available"):
        lines += [f"- {n}" for n in t.get("notes", [])] or ["- trajectory not available"]
    else:
        cm, p2 = t["com_msd"], t["p2"]
        d = (
            f"{cm['D_cm2_s']:.2e} ± {cm['D_err_cm2_s']:.1e} cm²/s (fit"
            f" {cm['t_start_ps'] / 1000:.3g}–{cm['t_end_ps'] / 1000:.3g} ns)"
            if cm["diffusive"]
            else f"not diffusive (log-slope {cm['slope_end']:.2f} at the longest lag,"
            f" MSD/⟨Rg²⟩ {_f(cm.get('msd_rg2_end'))})"
        )
        p2t = (
            f"{p2['t_1e_ps']:.1f} ps" if p2["t_1e_ps"] is not None else f"> {p2['lag_max_ps']:g} ps"
        )
        lines += [
            (
                f"{t['frames']} frames × {t['frame_ps']:g} ps ({t['hold_ns']:.3g} ns)"
                + (
                    "; parts: "
                    + ", ".join(f"{Path(p['file']).name} {p['frames']}" for p in t["parts"])
                    if t.get("parts")
                    else ""
                )
                + "."
            ),
            "",
            (
                "| COM MSD max (Å²) at lag (ns) | D_COM (D55 criterion) | bond P2 1/e | Rg (Å) |"
                " R_ee (Å) | C_n plateau |"
            ),
            "|---|---|---|---|---|---|",
            (
                f"| {cm['msd_at_max_A2']:.0f} at {cm['lag_max_ps'] / 1000:g} | {d} | {p2t} |"
                f" {_pm(t['rg']['rg_A'], '.2f')} | {_pm(t['ree']['ree_A'], '.1f')} |"
                f" {_pm(t['c_n']['plateau'], '.3f')} |"
            ),
        ]
        lines += [""] + [f"- {n}" for n in t.get("notes", [])] if t.get("notes") else []
    lines += relaxation_markdown([(r["t_c"] or 0.0, t)], r.get("resolution"))
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r.get("caveats", [])]
    lines += plots_markdown(r.get("plots"))
    return "\n".join(lines) + "\n"


def write_results(report: dict, out_dir: Path) -> None:
    _write(report, out_dir, render=render_markdown)
