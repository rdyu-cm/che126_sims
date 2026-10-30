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

import datetime as dt
import platform
from pathlib import Path

from sepsim.analysis.lammps_log import read_log
from sepsim.analyze import (
    HOLD_SKIP,
    MAX_FRAMES,
    AnalyzeError,
    _f,
    _pm,
    _system_arrays,
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
    _concat_thermo,
    _prep_hold_dcd,
    deck_system,
    find_deck,
    load_json,
    parse_deck,
)
from sepsim.run import CODE_DIR, MANIFEST_NAME, git_info

VERSION = 1
HOLD_DCD = {"extend": "hold_ext.dcd", "diffuse": "hold.dcd"}


def hold_thermo(segments, log, seg) -> tuple[dict | None, bool]:
    """Thermo rows of segment ``seg`` (its chunk runs concatenated; incomplete runs
    included) and whether all its runs are complete."""
    runs = log.runs if log else []
    start = sum(len(s.run_steps) for s in segments if s.index < seg.index)
    mine = runs[start : start + len(seg.run_steps)]
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
    th, done = hold_thermo(segments, log, seg)
    t_k = seg.t_target_k
    now = dt.datetime.now().astimezone()
    report: dict = {
        "version": VERSION,
        "generated": now.isoformat(timespec="seconds"),
        "generated_on": platform.node(),
        "system": system,
        "resolution": resolution,
        "stage": run_dir.resolve().name,
        "protocol": protocol,
        "run_dir": str(run_dir.resolve()),
        "run_status": (manifest or {}).get("status"),
        "run_node": (manifest or {}).get("hostname"),
        "run_git": (manifest or {}).get("git"),
        "code_git": git_info(CODE_DIR),
        "segment": seg.name,
        "t_k": t_k,
        "t_c": None if t_k is None else t_k - 273.15,
        "planned_ns": seg.steps * seg.dt_fs / 1e6,
        "complete": done,
        "method": {
            "hold_window": f"without the first {HOLD_SKIP:.0%} of rows",
            "sem": "100 ps block means (D55)",
            "max_frames": max_frames,
        },
        "notes": [],
    }
    if th is None or len(th.get("Step", ())) < 6:
        report["notes"].append("no thermo rows for the hold yet")
        report["stats"] = report["kappa"] = None
    else:
        if not done:
            report["notes"].append("hold not complete: thermo and trajectory over the part run")
        report["stats"] = window_stats(th, HOLD_SKIP)
        report["kappa"] = kappa_t(th, t_k, HOLD_SKIP) if t_k else None

    before = []
    if protocol == "extend" and name in seg.dcd:
        frame_ps = seg.dump_every[seg.dcd.index(name)] * seg.dt_fs / 1000.0
        prep, note = _prep_hold_dcd(run_dir, frame_ps)
        if note:
            report["notes"].append(note)
        if prep is not None:
            before = [prep]
    report["combined_with"] = [str(b) for b in before]
    try:
        sys_arr = _system_arrays(Path(systems) / system)
    except (OSError, ValueError, KeyError) as exc:
        sys_arr = None
        report["notes"].append(f"system {Path(systems) / system} not usable: {exc}")
    if sys_arr is None:
        report["traj"] = {"available": False, "notes": ["trajectory not available (no system)"]}
    else:
        try:
            report["traj"] = hold_trajectory(run_dir, seg, sys_arr, max_frames, before=before)
        except (OSError, ValueError) as exc:
            report["traj"] = {"available": False, "notes": [f"trajectory failed: {exc}"]}
    caveats = []
    tr = report["traj"]
    if tr.get("available"):
        lag = tr["relaxation"]["lag_max_ps"]
        caveats.append(
            f"Relaxation times use lags up to half the analysed hold ({lag / 1000:g} ns); a"
            " time beyond that is 'not reached' and only the extrapolated exponential fit"
            " is given."
        )
    if resolution == "cg":
        caveats.append(
            "CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD,"
            " D_COM and relaxation times are model times (docs/experiment_comparison.md)."
        )
    if not tr.get("available"):
        caveats.append(
            f"No trajectory results: {name} is not in this run directory (a run on another"
            " node may keep its DCD there) or could not be read."
        )
    report["caveats"] = caveats
    if plots:
        report["plots"] = make_plots(report, out_dir)
    return report, out_dir


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
    cg, rg = r.get("code_git") or {}, r.get("run_git") or {}
    lines = [
        f"# Hold analysis: {r['system']} / {r['stage']}",
        "",
        (
            f"- system: `{r['system']}` ({r.get('resolution')}); source run directory"
            f" `{r['run_dir']}` ({r['protocol']}, status {r.get('run_status')}, node"
            f" {r.get('run_node')}, run code commit {(rg.get('commit') or 'n/a')[:10]})"
        ),
        f"- analysis: `sepsim analyze hold` (D56), code commit {(cg.get('commit') or 'n/a')[:10]}"
        + (" (dirty)" if cg.get("dirty") else "")
        + f", {r['generated'][:16].replace('T', ' ')} on {r['generated_on']}",
        (
            f"- segment: {r['segment']} ({r['planned_ns']:g} ns planned,"
            f" {'complete' if r['complete'] else 'not complete'}); thermo window"
            f" {r['method']['hold_window']}, SEM from {r['method']['sem']}"
        ),
    ]
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
    if r.get("plots"):
        lines += ["", "## Plots", ""]
        for p in r["plots"].values():
            lines += [f"**{p['title']}**", "", f"![{p['title']}]({p['file']})", ""]
    return "\n".join(lines) + "\n"


def write_results(report: dict, out_dir: Path) -> None:
    _write(report, out_dir, render=render_markdown)
