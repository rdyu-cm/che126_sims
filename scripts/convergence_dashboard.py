"""Centralized convergence figures: one project overview grid plus one dashboard per system.

    uv run --frozen python scripts/convergence_dashboard.py [--runs DIR ...] [--analysis DIR]
        [--systems DIR] [--out-dir results] [--systems-only ID ...] [--cache DIR | --no-cache]

Writes ``<out-dir>/convergence_overview.png`` (+ ``.svg``): one row per current
(non-superseded) system, one column per check, cell colour = pass / flagged / fail /
info / running / not run / n.a. with the value printed; and ``<out-dir>/convergence/<id>.png``:

- row 1, the 500 K chain equilibration (D37/D47, from ``progress.json`` ``hold.curves``):
  C_n plateau vs time with the melt band, end-to-end vector ACF with 1/e, chain COM
  MSD/<Rg^2> with the 2.0 line; inherited from the source box for ua2aa AA boxes and pores;
- rows 2-3, the step-cool (``cool`` run, else the prep) and the sweep, or the pore run, on
  one time axis: T, density/enthalpy/volume (bulk) or gamma/PE/Pzz (pore), thinned trace,
  analysis windows shaded (steps second half, holds without their first 10%, as D49),
  block averages +- SEM, windows whose halves differ by > 2 combined SEM highlighted;
- row 4, per hold: SEM vs block length (block SEM / statistical-inefficiency SEM) and a
  table of window means +- SEM with drift flags; pores also gamma vs T;
- pores with ``<analysis>/<id>/pore/results.json`` (``convergence`` key): film thickness,
  gap and interior density panels.

Systems, stages, superseded detection, ordering and the equilibration verdicts come from
``scripts/summarize_systems.py`` (imported). Logs are parsed with ``sepsim.progress`` /
``sepsim.analysis.lammps_log``; the per-run results are cached (keyed by the log's size
and mtime) in ``--cache`` (default ``~/.cache/che126_sims/convergence``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from itertools import pairwise
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import summarize_systems as ss
import validity as va

from sepsim.analysis.chain import drift_check
from sepsim.analysis.lammps_log import read_log
from sepsim.analysis.stats import timeseries_mean
from sepsim.analysis.thermo import isothermal_compressibility
from sepsim.analysis.units import KB_J_PER_K
from sepsim.progress import (
    ATM_A_TO_MN_M,
    D47_ACF,
    D47_MSD_RG2,
    _concat_thermo,
    _input_stage,
    d_com_flag,
    find_deck,
    load_json,
    parse_deck,
)

ROOT = ss.ROOT
CACHE_VERSION = 4  # 3: hold kappa_T convergence records; 4: D55 block SEMs
HOLD_SKIP = 0.10  # D49: holds drop their first 10% of rows
STEP_SKIP = 0.50  # steps (and every non-sweep segment): second half
HOLD_BLOCKS, STEP_BLOCKS = 10, 5  # block averages per analysis window
SEM_BLOCKS = (256, 128, 64, 32, 16, 8, 4)  # block counts of the SEM-vs-block curve
STORE_POINTS = 1000  # thinned points per segment kept in the cache
MAX_POINTS = 2000  # points per timeline panel
N_SIGMA = 2.0
HYST_FLAG_PCT = 0.5  # cooling vs heating density difference flagged above this (%)
PREC_FLAG_PCT = 0.1  # hold density relative SEM flagged above this (%)
GAMMA_PREC_FLAG = 0.10  # pore: hold gamma SEM / |gamma| flagged above this
CHAIN_RELAXED = va.CHAIN_RELAXED  # hold COM MSD >= <Rg^2>: chains moved their own size
KAPPA_BLOCKS = 6  # blocks of a hold window for the block-averaged kappa_T
KAPPA_POINTS = 60  # points of the running (cumulative) kappa_T curve
CURVED_CHI2 = va.CURVED_CHI2  # alpha_V / Cp chi2_red above this: "curved" (information)
D_MIN_SLOPE = 0.9  # D49 diffusive criterion: local log-slope >= 0.9 ...

# ---------------------------------------------------------------- statuses and colours
PASS, FLAG, FAIL, INFO, RUN, NOTRUN, NA = (
    "pass",
    "flagged",
    "fail",
    "info",
    "running",
    "not run",
    "n.a.",
)
COLORS = {
    PASS: "#9fd89f",
    FLAG: "#f7d26a",
    FAIL: "#ee8a8a",
    INFO: "#b9d3ee",
    RUN: "#d7c4ee",
    NOTRUN: "#d9d9d9",
    NA: "#ffffff",
}
STATUS_TEXT = {
    PASS: "pass",
    FLAG: "flagged (informational: look at it)",
    FAIL: "fail",
    INFO: "information (not a criterion)",
    RUN: "running / partial",
    NOTRUN: "not run yet",
    NA: "does not apply",
}
QCOLOR = {
    "T": "#c0392b",
    "density": "#1f5fa8",
    "enthalpy": "#2e8b57",
    "volume": "#7d3c98",
    "gamma": "#d35400",
    "pe": "#2e8b57",
    "pzz": "#7d3c98",
    "film_gibbs_A": "#1f5fa8",
    "gap_gibbs_A": "#7d3c98",
    "plateau": "#2e8b57",
}
QLABEL = {
    "T": "T (K)",
    "density": r"density (g/cm$^3$)",
    "enthalpy": "enthalpy (kcal/mol)",
    "volume": r"volume ($\AA^3$)",
    "gamma": r"$\gamma$ (mN/m per surface)",
    "pe": "potential energy (kcal/mol)",
    "pzz": r"$P_{zz}$ (atm)",
    "film_gibbs_A": r"film thickness, Gibbs ($\AA$)",
    "gap_gibbs_A": r"gap width, Gibbs ($\AA$)",
    "plateau": r"interior density (g/cm$^3$)",
}
BULK_Q = ("T", "density", "enthalpy", "volume")
PORE_Q = ("T", "gamma", "pe", "pzz")
FILM_Q = ("film_gibbs_A", "gap_gibbs_A", "plateau")
ZOOM_Q = ("gamma", "pzz")


# ---------------------------------------------------------------- statistics


def window_slice(n: int, skip: float) -> slice:
    return slice(int(np.floor(skip * n)), None)


def mean_sem(x, block: int | None = None) -> dict | None:
    """Mean, statistical-inefficiency SEM and g (D26; on ``block``-row block means if given,
    D55); constant series: SEM 0."""
    x = np.asarray(x, dtype=float)
    if len(x) < 3:
        return None
    if np.ptp(x) == 0.0:
        return {"mean": float(x[0]), "sem": 0.0, "g": 1.0}
    r = timeseries_mean(x, block=block)
    return {"mean": r.mean, "sem": r.sem, "g": r.g}


def block_averages(t, x, n_blocks: int) -> list[dict]:
    """``n_blocks`` equal blocks of a series: mid time, mean and statistical-inefficiency
    SEM of each (blocks with < 3 rows are dropped)."""
    t, x = np.asarray(t, dtype=float), np.asarray(x, dtype=float)
    out = []
    for idx in np.array_split(np.arange(len(x)), n_blocks):
        if len(idx) >= 3:
            ms = mean_sem(x[idx])
            out.append({"t": float(t[idx].mean()), "mean": ms["mean"], "sem": ms["sem"]})
    return out


def sem_vs_block(x, dt: float, sem_g: float | None = None) -> list[dict]:
    """SEM of the window mean from the means of n blocks (n in ``SEM_BLOCKS``, >= 3 rows
    each) vs block length; ``ratio`` = that SEM / the statistical-inefficiency SEM. Once
    blocks outlast the correlation time the curve plateaus at ratio ~1."""
    x = np.asarray(x, dtype=float)
    out = []
    for nb in SEM_BLOCKS:
        if len(x) >= 3 * nb:
            means = np.array([b.mean() for b in np.array_split(x, nb)])
            sem = float(means.std(ddof=1) / np.sqrt(nb))
            out.append(
                {
                    "n_blocks": nb,
                    "block_ns": len(x) / nb * dt,
                    "sem": sem,
                    "ratio": sem / sem_g if sem_g else None,
                }
            )
    return out


def halves_drift(w, block: int | None = None) -> dict | None:
    """Halves test on an analysis window: second - first half beyond ``N_SIGMA`` combined
    statistical-inefficiency SEMs (:func:`sepsim.analysis.chain.drift_check`)."""
    w = np.asarray(w, dtype=float)
    if len(w) < 12 or np.ptp(w) == 0.0:
        return None
    try:
        a, b, delta, sem, drift = drift_check(w, N_SIGMA, block=block)
    except ValueError:  # a zero-variance half
        return None
    return {"first": a, "second": b, "delta": delta, "sem": sem, "drift": drift}


def thin_idx(n: int, k: int) -> np.ndarray:
    return np.unique(np.linspace(0, n - 1, min(n, max(k, 2))).round().astype(int))


def quantity_record(t_ns, x, skip: float, n_blocks: int, hold: bool) -> dict:
    """Thinned series, block averages over the window, window mean +- SEM, halves drift
    and (holds) SEM vs block size. Times are relative to the segment start (ns)."""
    t, x = np.asarray(t_ns, dtype=float), np.asarray(x, dtype=float)
    sl = window_slice(len(x), skip)
    tw, w = t[sl], x[sl]
    k = thin_idx(len(x), STORE_POINTS)
    # D55: SEMs from 100 ps block means (thermo rows; barostat ringing)
    dt = float(np.median(np.diff(tw))) if len(tw) > 1 else 0.0
    blk = max(1, round(0.1 / dt)) if dt > 0 else None
    ms = mean_sem(w, blk)
    rec = {
        "t": [round(float(v), 6) for v in t[k]],
        "value": [float(f"{v:.8g}") for v in x[k]],
        "blocks": block_averages(tw, w, n_blocks) if len(w) >= 3 * n_blocks else [],
        "mean": None if ms is None else ms["mean"],
        "sem": None if ms is None else ms["sem"],
        "g": None if ms is None else ms["g"],
        "halves": halves_drift(w, blk),
        # bin means of the full series (~250 rows each) for the noisy pressure-type traces
        "binned": [
            [round(float(t[b].mean()), 6), float(f"{x[b].mean():.8g}")]
            for b in np.array_split(np.arange(len(x)), max(10, len(x) // 250))
            if len(b)
        ],
    }
    rec["drift"] = None if rec["halves"] is None else rec["halves"]["drift"]
    if hold and len(tw) > 1 and ms and ms["sem"]:
        rec["sem_vs_block"] = sem_vs_block(w, float(np.median(np.diff(tw))), ms["sem"])
    return rec


def kappa_record(t_ns, v, t_k: float) -> dict | None:
    """κ_T convergence of one NPT hold (volume fluctuations, Allen & Tildesley; the same
    formula as ``sepsim analyze``) over the hold window (first 10% dropped): the running
    (cumulative) κ_T(t), κ_T of ``KAPPA_BLOCKS`` blocks (mean ± SEM over blocks; blocks
    shorter than the volume correlation time underestimate it), and the two halves with
    their statistical-inefficiency SEMs; ``drift`` when they differ by > 2 combined SEM."""
    t, v = np.asarray(t_ns, dtype=float), np.asarray(v, dtype=float)
    sl = window_slice(len(v), HOLD_SKIP)
    tw, w = t[sl], v[sl]
    if len(w) < 12 * KAPPA_BLOCKS or np.ptp(w) == 0.0:
        return None
    gpa = 1e-21 / (KB_J_PER_K * t_k)  # A^3 / J -> 1/GPa, divided by <V> below
    n = np.arange(1, len(w) + 1)
    c1, c2 = np.cumsum(w), np.cumsum(w * w)
    mean = c1 / n
    run_k = (c2 / n - mean**2) / mean * gpa
    idx = np.unique(np.linspace(len(w) // 20, len(w) - 1, KAPPA_POINTS).astype(int))
    blocks = []
    for b in np.array_split(np.arange(len(w)), KAPPA_BLOCKS):
        blocks.append({"t": float(tw[b].mean()), "kappa": float(w[b].var() / w[b].mean() * gpa)})
    bk = np.array([b["kappa"] for b in blocks])
    try:
        full = isothermal_compressibility(w, t_k)
        h1 = isothermal_compressibility(w[: len(w) // 2], t_k)
        h2 = isothermal_compressibility(w[len(w) // 2 :], t_k)
    except ValueError:
        return None
    sem = float(np.hypot(h1.kappa_T_sem, h2.kappa_T_sem))
    delta = h2.kappa_T - h1.kappa_T
    return {
        "kappa": full.kappa_T,
        "sem": full.kappa_T_sem,
        "running": [[float(tw[i]), float(run_k[i])] for i in idx],
        "blocks": blocks,
        "block_mean": float(bk.mean()),
        "block_sem": float(bk.std(ddof=1) / np.sqrt(len(bk))),
        "first": [h1.kappa_T, h1.kappa_T_sem],
        "second": [h2.kappa_T, h2.kappa_T_sem],
        "delta": float(delta),
        "delta_sem": sem,
        "drift": bool(abs(delta) > N_SIGMA * sem) if sem > 0 else None,
    }


# ---------------------------------------------------------------- runs -> segment records


def gamma_series(th: dict) -> np.ndarray:
    """gamma = (Lz/2)[Pzz - (Pxx+Pyy)/2] per surface, mN/m (D48)."""
    return 0.5 * th["Lz"] * (th["Pzz"] - 0.5 * (th["Pxx"] + th["Pyy"])) * ATM_A_TO_MN_M


def thermo_columns(th: dict) -> dict[str, np.ndarray]:
    cols = {}
    for q, c in (
        ("T", "Temp"),
        ("density", "Density"),
        ("enthalpy", "Enthalpy"),
        ("volume", "Volume"),
        ("pe", "PotEng"),
        ("pzz", "Pzz"),
    ):
        if c in th:
            cols[q] = th[c]
    if all(c in th for c in ("Pxx", "Pyy", "Pzz", "Lz")):
        cols["gamma"] = gamma_series(th)
    return cols


def segment_kind(seg) -> str:
    if seg.sweep_kind:
        return seg.sweep_kind
    return "cool" if seg.cool_step is not None else "md"


def is_md(seg) -> bool:
    return (
        seg.command == "run" and not seg.vdos and seg.ensemble in ("npt", "nvt") and seg.steps > 0
    )


def segment_records(run_dir: Path) -> list[dict]:
    """Per MD segment (NVT/NPT runs; minimize, soft-core and VDOS NVE skipped): kind,
    state, set T, duration and window (ns, relative to the segment start) and a
    :func:`quantity_record` per thermo quantity. Partial (running) segments included."""
    deck = find_deck(run_dir, load_json(run_dir / "run_manifest.json"))
    log_path = run_dir / "log.lammps"
    if deck is None or not log_path.is_file():
        return []
    segments = parse_deck(deck)
    runs = read_log(log_path).runs
    out, k = [], 0
    for seg in segments:
        mine = runs[k : k + len(seg.run_steps)]
        k += len(seg.run_steps)
        if not mine or not is_md(seg):
            continue
        th = _concat_thermo(mine)
        if "Time" not in th or len(th["Time"]) < 6:
            continue
        state = (
            "done"
            if len(mine) == len(seg.run_steps) and all(r.complete for r in mine)
            else "running"
        )
        kind = segment_kind(seg)
        skip = HOLD_SKIP if kind == "hold" else STEP_SKIP
        n_blocks = HOLD_BLOCKS if kind == "hold" else STEP_BLOCKS
        t = (th["Time"] - th["Time"][0]) / 1e6  # fs -> ns
        sl = window_slice(len(t), skip)
        t_set = seg.t_c if seg.t_c is not None else (seg.t_target_k or 0.0) - 273.15
        cols = thermo_columns(th)
        kap = None
        if kind == "hold" and seg.ensemble == "npt" and "volume" in cols:
            kap = kappa_record(t, cols["volume"], t_set + 273.15)
        out.append(
            {
                "index": seg.index,
                "name": seg.name,
                "kind": kind,
                "state": state,
                "ensemble": seg.ensemble,
                "t_set_c": t_set,
                "t_start_ps": float(th["Time"][0] / 1000.0),
                "duration_ns": float(t[-1]),
                "planned_ns": seg.steps * seg.dt_fs / 1e6,
                "window": [float(t[sl][0]), float(t[-1])],
                "rows": len(t),
                "quantities": {
                    q: quantity_record(t, x, skip, n_blocks, kind == "hold")
                    for q, x in cols.items()
                },
                "kappa": kap,
            }
        )
    return out


def _file_key(p: Path) -> list | None:
    try:
        st = p.stat()
    except OSError:
        return None
    return [st.st_size, st.st_mtime_ns]


def run_records(run_dir: Path, cache_dir: Path | None) -> list[dict]:
    """:func:`segment_records`, cached per run directory by its log and deck stat."""
    run_dir = Path(run_dir)
    deck = find_deck(run_dir, load_json(run_dir / "run_manifest.json"))
    key = [CACHE_VERSION, _file_key(run_dir / "log.lammps"), _file_key(deck) if deck else None]
    cfile = None
    if cache_dir is not None:
        h = hashlib.sha256(str(run_dir.resolve()).encode()).hexdigest()[:12]
        cfile = Path(cache_dir) / f"{run_dir.parent.name}__{run_dir.name}__{h}.json"
        old = load_json(cfile)
        if old and old.get("key") == key:
            return old["segments"]
    recs = segment_records(run_dir)
    if cfile is not None:
        cfile.parent.mkdir(parents=True, exist_ok=True)
        tmp = cfile.with_suffix(".tmp")
        tmp.write_text(json.dumps({"key": key, "segments": recs}))
        tmp.replace(cfile)
    return recs


# ---------------------------------------------------------------- per system data


def timeline_plan(sid: str, ctx: dict) -> list[tuple[dict, str]]:
    """(run, part) for the timeline: pores their pore (or pore_relax) run; bulk the stage
    the sweep cools from (``cool`` run, else the prep's NVT/NPT segments), then the sweep;
    without both, the cool/prep alone, else a 500 K extension (replicated boxes)."""
    runs = ss.current_runs(ctx["runs"].get(sid, {}))
    if ctx["meta"][sid]["pore"]:
        r = ss.latest(runs, "pore") or ss.latest(runs, "pore_relax")
        return [(r, "pore")] if r else []
    sweep, cool, prep = (ss.latest(runs, k) for k in ("sweep", "cool", "prep"))
    src = None
    if sweep is not None:
        deck = find_deck(Path(sweep["path"]))
        stage = _input_stage(deck) if deck else None
        src = next((r for r in runs if r["dir"] == stage), None) if stage else None
    src = src or cool or prep
    out = [(src, "cool" if src["kind"] == "cool" else "prep")] if src else []
    if sweep is not None:
        out.append((sweep, "sweep"))
    if not out:
        ext = ss.latest(runs, "extend")
        if ext:
            out.append((ext, "extend"))
    return out


def system_data(sid: str, ctx: dict, cache_dir: Path | None) -> dict:
    """Timeline segments on one concatenated axis (``t0`` offset per segment, ns), plus
    the sweep (or pore sweep) subset used by the overview."""
    segs, offset = [], 0.0
    for run, part in timeline_plan(sid, ctx):
        if not (Path(run["path"]) / "log.lammps").is_file():
            continue
        for r in run_records(Path(run["path"]), cache_dir):
            r = dict(r, stage=run["dir"], part=part, t0=offset)
            offset += r["duration_ns"]
            segs.append(r)
    sweep = [s for s in segs if s["kind"] in ("step", "hold")]
    return {"segments": segs, "sweep": sweep, "pore": bool(ctx["meta"][sid]["pore"])}


def chain_source(sid: str, ctx: dict) -> tuple[dict | None, str | None]:
    """The progress ``hold`` block behind the system's equilibration verdict and the
    system it belongs to (the source box for inherited verdicts)."""
    eq = ctx["eq"][sid]
    ch = eq.get("checks")
    if not ch:
        return None, None
    owner = eq["via"][-1] if eq.get("basis") == "inherited" and eq.get("via") else sid
    run = ctx["runs"].get(owner, {}).get(ch["stage"])
    return ss.get(run, "progress", "hold"), owner


def long_cg(sid: str, ctx: dict) -> bool:
    man = ctx["systems"].get(sid) or {}
    return (
        ctx["meta"][sid]["resolution"] == "cg"
        and (man.get("n_carbons") or 0) >= ss.D47_EXEMPT_CG_CARBONS
    )


def analysis_for(sid: str, ctx: dict, kind: str) -> dict | None:
    ana = ctx["analysis"].get(sid, {})
    if kind in ana:
        return ana[kind]
    return next((v for k, v in ana.items() if ss.classify_stage(k)[0] == kind), None)


# ---------------------------------------------------------------- overview cells


def _f(x, spec=".2f") -> str:
    return ss.fnum(x, spec)


def stage_cell(sid: str, ctx: dict, kinds: tuple[str, ...]) -> tuple[str, str]:
    runs = ss.current_runs(ctx["runs"].get(sid, {}))
    expected = ss.expected_stages(sid, ctx)
    run = next((ss.latest(runs, k) for k in kinds if ss.latest(runs, k)), None)
    if run is None:
        if not any(k in expected for k in kinds):
            return NA, ""
        later = expected[expected.index(next(k for k in kinds if k in expected)) + 1 :]
        if any(ss.latest(runs, k) for k in later):
            return NA, "skipped"
        return NOTRUN, "not started"
    if ss.is_done(run):
        return PASS, "done"
    p = run.get("progress") or {}
    st, pct = p.get("status"), p.get("percent")
    txt = f"{pct:.0f}%" if pct is not None else (st or "?")
    kind = run["kind"]
    later = expected[expected.index(kind) + 1 :] if kind in expected else []
    if st not in ("running", "starting") and any(ss.latest(runs, k) for k in later):
        return INFO, f"{txt}, stopped\n(later stages ran)"
    if st in ("running", "starting"):
        return RUN, txt
    if st == "stalled?":
        return FLAG, f"{txt}\nstalled?"
    return FAIL, f"{txt}\n{st or 'unknown'}"


def overview_cells(sid: str, ctx: dict, data: dict) -> dict[str, tuple[str, str]]:
    """{column: (status, text)} for one system (see :data:`COLUMNS`)."""
    c: dict[str, tuple[str, str]] = {}
    eq = ctx["eq"][sid]
    ch = eq.get("checks") or {}
    d = ch.get("d47") or {}
    inh = "\n(inherited)" if eq.get("basis") == "inherited" else ""
    if eq.get("basis") == "prep only":
        inh = "\n(prep hold)"
    lcg = long_cg(sid, ctx)
    if not d:
        c["acf"] = c["msd"] = (NOTRUN, "")
    elif lcg:
        c["acf"] = (NA, f"{_f(d.get('acf'))}\nn/a: C1500{inh}")
        c["msd"] = (NA, f"{_f(d.get('ratio'))}\nn/a: C1500{inh}")
    else:
        acf, ratio = d.get("acf"), d.get("ratio")
        run = " (so far)" if ch.get("running") else ""
        c["acf"] = (
            (PASS if acf < D47_ACF else FAIL) if acf is not None else NOTRUN,
            f"{_f(acf)}{run}{inh}",
        )
        c["msd"] = (
            (PASS if ratio >= D47_MSD_RG2 else FAIL) if ratio is not None else NOTRUN,
            f"{_f(ratio)}{run}{inh}",
        )
    if ch.get("plateau") is None:
        c["cn"] = c["cn_drift"] = (NOTRUN, "")
    else:
        ref = ch.get("reference") or ss.MELT_C_INF_500K.get(ctx["meta"][sid]["polymer"] or "")
        band = "in band" if ch.get("within_reference") else "outside"
        c["cn"] = (INFO, f"{_f(ch['plateau'])} vs {_f(ref[0], 'g') if ref else '?'}\n{band}")
        dr = ch.get("drift")
        txt = f"Δ {_f(ch.get('delta'), '+.2f')} ± {_f(ch.get('delta_sem'))}\n" + (
            "drift" if dr else "no drift" if dr is False else "n/a"
        )
        # long CG chains are accepted on the C_n no-drift check (D47): it decides there
        c["cn_drift"] = (
            ((FAIL if dr else PASS) if dr is not None else NOTRUN, txt)
            if lcg
            else (
                INFO,
                txt,
            )
        )
    for col, kinds in (
        ("prep", ("prep",)),
        ("extend", ("extend",)),
        ("cool", ("cool",)),
        ("sweep", ("sweep",)),
        ("pore", ("pore", "pore_relax")),
    ):
        c[col] = stage_cell(sid, ctx, kinds)
    pore = data["pore"]
    sweep = data["sweep"]
    runs = ss.current_runs(ctx["runs"].get(sid, {}))
    sweep_kind = "pore" if pore else "sweep"
    has_sweep = ss.latest(runs, sweep_kind) is not None
    expects_sweep = has_sweep or sweep_kind in ss.expected_stages(sid, ctx)
    done = [s for s in sweep if s["state"] == "done"]
    running = any(s["state"] == "running" for s in sweep) or (
        has_sweep
        and ss.get(ss.latest(runs, "pore" if pore else "sweep"), "progress", "status")
        in ("running", "starting")
    )

    def drift_count(q: str) -> tuple[str, str]:
        if not has_sweep:
            return NOTRUN, ""
        tested = [s for s in done if s["quantities"].get(q, {}).get("drift") is not None]
        if not tested:
            return (RUN, "none done") if running else (NOTRUN, "no data")
        n = sum(bool(s["quantities"][q]["drift"]) for s in tested)
        txt = f"{n}/{len(tested)}" + (" so far" if running else "")
        return (FLAG if n else PASS), txt

    if pore:
        c["rho_drift"] = c["h_drift"] = c["hyst"] = (NA, "")
        c["gamma_drift"] = drift_count("gamma") if expects_sweep else (NA, "")
    else:
        c["rho_drift"] = drift_count("density") if expects_sweep else (NA, "")
        c["h_drift"] = drift_count("enthalpy") if expects_sweep else (NA, "")
        c["gamma_drift"] = (NA, "")
        hyst = ss.get(ss.latest(runs, "sweep"), "progress", "hysteresis") or []
        vals = [abs(h["delta_pct"]) for h in hyst if h.get("delta_pct") is not None]
        if vals:
            m = max(vals)
            c["hyst"] = (FLAG if m > HYST_FLAG_PCT else PASS, f"{m:.2f}%")
        else:
            c["hyst"] = (NOTRUN, "") if expects_sweep else (NA, "")
    holds = [s for s in done if s["kind"] == "hold"]
    if pore:
        vals = [
            (s["quantities"]["gamma"]["sem"], s["quantities"]["gamma"]["mean"])
            for s in holds
            if s["quantities"].get("gamma", {}).get("sem") is not None
        ]
        if vals:
            worst = max(vals, key=lambda v: v[0] / max(abs(v[1]), 1e-9))
            rel = worst[0] / max(abs(worst[1]), 1e-9)
            c["prec"] = (FLAG if rel > GAMMA_PREC_FLAG else PASS, f"γ ±{worst[0]:.2f}\n({rel:.0%})")
        else:
            c["prec"] = (RUN, "running") if running else (NOTRUN, "") if expects_sweep else (NA, "")
    else:
        rel = [
            s["quantities"]["density"]["sem"] / s["quantities"]["density"]["mean"] * 100
            for s in holds
            if s["quantities"].get("density", {}).get("sem") is not None
        ]
        if rel:
            m = max(rel)
            c["prec"] = (FLAG if m > PREC_FLAG_PCT else PASS, f"ρ {m:.3f}%")
        else:
            c["prec"] = (RUN, "running") if running else (NOTRUN, "") if expects_sweep else (NA, "")
    c["chain"] = chain_cell(sid, ctx, pore) if expects_sweep else (NA, "")
    if pore:
        c["kappa"] = c["fit"] = (NA, "")
    else:
        c["kappa"] = kappa_cell(holds, has_sweep, running) if expects_sweep else (NA, "")
        c["fit"] = fit_cell(analysis_for(sid, ctx, "sweep")) if expects_sweep else (NA, "")
    c["dyn"] = (
        dyn_cell(analysis_for(sid, ctx, "pore" if pore else "sweep")) if expects_sweep else (NA, "")
    )
    c["diffuse"] = diffuse_cell(extra_runs(sid, ctx, "diffuse"))
    c["tensile"] = tensile_cell(extra_runs(sid, ctx, "tensile"), sid, ctx)
    c["hole"] = hole_cell(extra_runs(sid, ctx, "hole"))
    return c


def kappa_cell(holds: list[dict], has_sweep: bool, running: bool) -> tuple[str, str]:
    """Holds whose κ_T halves differ by > 2 combined SEM (flagged) and the worst SEM."""
    k = [s["kappa"] for s in holds if s.get("kappa")]
    if not k:
        if not has_sweep:
            return NOTRUN, ""
        return (RUN, "none done") if running else (NOTRUN, "no data")
    n = sum(bool(x["drift"]) for x in k)
    rel = max(x["sem"] / x["kappa"] for x in k if x["kappa"])
    txt = f"{n}/{len(k)} halves differ\nSEM ≤ {rel:.1%}" + (" (so far)" if running else "")
    return (FLAG if n else PASS), txt


def fit_cell(res: dict | None) -> tuple[str, str]:
    """χ²_red of the 25–160 °C α_V and Cp fits (information: ≫ 1 = curved in T)."""
    if res is None:
        return NOTRUN, "no analysis"
    fits = res.get("fits") or {}
    chi = {}
    for q in ("alpha_V", "cp"):
        f = next((x for x in fits.get(q) or [] if x.get("window_c") == [25.0, 160.0]), None)
        f = f or next(iter(fits.get(q) or []), None)
        chi[q] = (f or {}).get("chi2_red")
    if all(v is None for v in chi.values()):
        return NOTRUN, "no fits"
    curved = any(v is not None and v > CURVED_CHI2 for v in chi.values())
    txt = f"α {_f(chi['alpha_V'], '.3g')} / Cp {_f(chi['cp'], '.3g')}" + (
        "\ncurved in T" if curved else "\nlinear"
    )
    return INFO, txt


def dyn_cell(res: dict | None) -> tuple[str, str]:
    """Per hold: D_COM diffusive? and P2 1/e reached within the hold?"""
    if res is None:
        return NOTRUN, "no analysis"
    hf = [h for h in va.hold_facts(res) if h["p2"] or h["diffusive"] is not None]
    if not hf:
        return NOTRUN, "no traj."
    nd = sum(bool(h["diffusive"]) for h in hf)
    np2 = sum(bool(h["p2_reached"]) for h in hf)
    st = FLAG if np2 < len(hf) else INFO
    return st, f"D_COM diffusive {nd}/{len(hf)}\nP2 1/e reached {np2}/{len(hf)}"


def extra_runs(sid: str, ctx: dict, kind: str) -> list[dict]:
    return [r for r in ss.current_runs(ctx["runs"].get(sid, {})) if r["kind"] == kind]


def _run_txt(r: dict) -> str:
    p = r.get("progress") or {}
    if ss.is_done(r):
        return "done"
    pct = p.get("percent")
    return f"{pct:.0f}%" if pct is not None else (p.get("status") or "?")


def _runs_status(runs: list[dict]) -> str:
    sts = {ss.get(r, "progress", "status") for r in runs}
    if all(ss.is_done(r) for r in runs):
        return PASS
    if sts & {"running", "starting"}:
        return RUN
    if "stalled?" in sts:
        return FLAG
    return FAIL


def diffuse_cell(runs: list[dict]) -> tuple[str, str]:
    """D53 holds: per run T, % done and the D_COM verdict of the monitor."""
    if not runs:
        return NA, ""
    lines = []
    diff = []
    for r in runs:
        hold = ss.get(r, "progress", "hold") or {}
        d = hold.get("d_com") or {}
        tag = r["dir"].removeprefix("diffuse_")
        v = "diffusive" if d.get("diffusive") else "not diff." if d else "no check"
        diff.append(bool(d.get("diffusive")))
        lines.append(f"{tag} {_run_txt(r)}, {v}")
    st = _runs_status(runs)
    if st == PASS:
        st = PASS if all(diff) else INFO
    return st, "\n".join(lines[:3])


def tensile_cell(runs: list[dict], sid: str, ctx: dict) -> tuple[str, str]:
    """D54 runs: status, and E_app (mean ± SD over axes) once analysed."""
    if not runs:
        return NA, ""
    ana = ctx["analysis"].get(sid, {})
    lines = []
    for r in runs:
        res = ana.get(r["dir"])
        e = ss.get(res, "runs", 0, "summary", "E_MPa")
        tag = r["dir"].removeprefix("tensile_")
        if e:
            lines.append(f"{tag}: E {e['mean']:.0f}±{e.get('sd') or 0:.0f}")
        else:
            lines.append(f"{tag} {_run_txt(r)}")
    st = _runs_status(runs)
    if st == PASS and not all(ana.get(r["dir"]) for r in runs):
        st = INFO
        lines.append("(no analysis)")
    return st, "\n".join(lines[:4])


def hole_cell(runs: list[dict]) -> tuple[str, str]:
    if not runs:
        return NA, ""
    return _runs_status(runs), "\n".join(f"{r['dir']} {_run_txt(r)}" for r in runs[:3])


def chain_ratios(res: dict | None) -> list[tuple[float, float]]:
    """(T, hold COM MSD max / <Rg^2>) per hold of an analysis results.json."""
    out = []
    for h in (res or {}).get("holds") or []:
        t = va.hold_traj(h)
        msd = ss.get(t, "com_msd", "msd_at_max_A2")
        rg2 = ss.get(t, "rg", "rg2_A2", "mean")
        if msd is not None and rg2:
            out.append((h.get("t_c"), msd / rg2))
    return out


def chain_cell(sid: str, ctx: dict, pore: bool) -> tuple[str, str]:
    res = analysis_for(sid, ctx, "pore" if pore else "sweep")
    if res is None:
        return NOTRUN, "no analysis"
    r = chain_ratios(res)
    if not r:
        return NOTRUN, "no traj."
    lo, hi = min(v for _, v in r), max(v for _, v in r)
    st = PASS if lo >= CHAIN_RELAXED else FLAG
    return st, f"{lo:.2f}–{hi:.2f}"


COLUMNS = (
    ("acf", "D47 R$_{ee}$ ACF\n(< 1/e)"),
    ("msd", "D47 COM MSD\n/⟨R$_g^2$⟩ (≥ 2)"),
    ("cn", "C$_n$ plateau\nvs melt (info)"),
    ("cn_drift", "C$_n$ drift\n(info; C1500: rule)"),
    ("prep", "prep"),
    ("extend", "extend"),
    ("cool", "cool"),
    ("sweep", "sweep"),
    ("pore", "pore"),
    ("rho_drift", "sweep ρ drift\n(segments)"),
    ("h_drift", "sweep H drift\n(segments)"),
    ("hyst", "hysteresis\nmax |Δρ| cool/heat"),
    ("prec", "hold precision\nmax SEM"),
    ("kappa", "κ$_T$ halves\n(holds, > 2 SEM)"),
    ("fit", "α$_V$ / C$_p$ fit\nχ²$_{red}$ 25–160 °C"),
    ("gamma_drift", "pore γ drift\n(segments)"),
    ("chain", "chain-scale relax.\nhold MSD/⟨R$_g^2$⟩"),
    ("dyn", "hold dynamics\nD$_{COM}$ / P2 1/e"),
    ("diffuse", "diffuse (D53)\nlong-hold D$_{COM}$"),
    ("tensile", "tensile (D54)\nE$_{app}$ (MPa)"),
    ("hole", "hole (D52)"),
)
GROUPS = (4, 9, 16, 18)  # column separators: chain | stages | sampling | relaxation | extra runs


def current_order(ctx: dict, only: list[str] | None = None) -> list[str]:
    order = sorted(ctx["meta"], key=lambda s: ss.sort_key(s, ctx["meta"][s], ctx["systems"].get(s)))
    # superseded systems and systems with nothing to show (no runs, no verdict) left out
    order = ss.current_systems(ctx, order)
    if only:
        order = [s for s in order if s in only]
    return order


def draw_overview(path: Path, ctx: dict, order: list[str], cells: dict[str, dict]) -> None:
    ncol, nrow = len(COLUMNS), len(order)
    fig_w, fig_h = 3.9 + 1.18 * ncol, 1.5 + 0.66 * nrow + 2.0
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=100)
    left, right = 3.8 / fig_w, 0.997
    top = 1 - 1.5 / fig_h
    bottom = 2.0 / fig_h
    ax = fig.add_axes([left, bottom, right - left, top - bottom])
    ax.set_xlim(0, ncol)
    ax.set_ylim(nrow, 0)
    ax.axis("off")
    for i, sid in enumerate(order):
        for j, (key, _) in enumerate(COLUMNS):
            st, txt = cells[sid].get(key, (NA, ""))
            ax.add_patch(
                plt.Rectangle((j, i), 1, 1, facecolor=COLORS[st], edgecolor="#777", lw=0.6)
            )
            if txt:
                ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=7.2)
        m = ctx["meta"][sid]
        tag = f"{(m['resolution'] or '?').upper()} {ss.POLYMER_NAME.get(m['polymer'], '?')}, {ss.kind_label(m)}"
        ax.text(-0.08, i + 0.38, sid, ha="right", va="center", fontsize=8, family="monospace")
        ax.text(-0.08, i + 0.75, tag, ha="right", va="center", fontsize=7, color="#555")
    for j, (_, lab) in enumerate(COLUMNS):
        ax.text(j + 0.5, -0.12, lab, ha="center", va="bottom", fontsize=7.6, weight="bold")
    for x in GROUPS:  # chain checks | stages | sampling | relaxation | extra runs
        ax.plot([x, x], [-0.9, nrow], color="black", lw=1.6, clip_on=False)
    for (a, b), name in zip(
        pairwise((0, *GROUPS, ncol)),
        (
            "500 K chain equilibration",
            "stages",
            "sampling of the cool/sweep/pore runs",
            "relaxation at T",
            "extra runs",
        ),
        strict=True,
    ):
        ax.text((a + b) / 2, -0.95, name, ha="center", va="bottom", fontsize=9.5, style="italic")
    fig.suptitle(
        "Convergence overview: every current system × every check"
        f"  (generated {time.strftime('%Y-%m-%d %H:%M %Z')})",
        fontsize=13,
        weight="bold",
        y=1 - 0.25 / fig_h,
    )
    handles = [Patch(facecolor=COLORS[k], edgecolor="#777", label=STATUS_TEXT[k]) for k in COLORS]
    fig.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.01, 1.2 / fig_h),
        ncol=4,
        fontsize=8.5,
        frameon=False,
    )
    rules = (
        "Project rule: D47 decides acceptance (500 K, at half the combined prep hold + extension: end-to-end ACF < 1/e and "
        "chain COM MSD ≥ 2⟨Rg²⟩). C_n vs the melt C∞ (PE 6.7, iPP 6.15 ±10%) and its drift are information only; C1500-type "
        "long CG chains are exempt from D47 and accepted on a C_n plateau without drift.\n"
        "Inherited = ua2aa AA boxes and pores carry their source box's 500 K verdict. Stages: % of MD steps done. "
        "Drift (sweep segments): the analysis window's halves (steps: second half; holds: without the first 10%) differ by > 2 combined "
        "statistical-inefficiency SEM; flagged, informational.\n"
        f"Hysteresis flagged > {HYST_FLAG_PCT:g}%; hold precision flagged if ρ SEM/ρ > {PREC_FLAG_PCT:g}% (bulk) or γ SEM/|γ| > "
        f"{GAMMA_PREC_FLAG:.0%} (pores). Chain-scale relaxation: COM MSD at the longest hold lag / ⟨Rg²⟩ (sepsim analyze), min–max over "
        "holds; < 1 = chains moved less than their size, so chain-scale properties (Rg, C_n, R_ee) at that T are inherited from the cooled melt.\n"
        "κ_T halves: κ_T from the volume fluctuations of each half of the hold window differs by > 2 combined SEM (flagged). α_V/Cp fit: χ²_red of the "
        f"25–160 °C linear fits (information; > {CURVED_CHI2:g} = curved, use the half windows). Hold dynamics: chain COM MSD diffusive (D49: log-slope ≥ 0.9 over ≥ 2× in lag) "
        "and bond P2 ACF reaching 1/e within the hold (flagged if not).\n"
        "Extra runs: diffuse (D53 long NPT hold, D_COM from the monitor), tensile (D54; E_app mean ± SD over axes once analysed), hole (D52). "
        "Per-system details: results/convergence/<system>.png; which properties can be compared with experiment: results/validity_overview.png."
    )
    fig.text(0.01, 0.12 / fig_h, rules, fontsize=8.5, va="bottom", ha="left", wrap=True)
    fig.savefig(path)
    if path.suffix == ".png":
        fig.savefig(path.with_suffix(".svg"))
    plt.close(fig)


def draw_validity(path: Path, ctx: dict, order: list[str]) -> dict[str, dict]:
    """Colour-coded grid of :func:`validity.system_validity` (rows as the convergence
    overview); returns {system: {property: verdict}}."""
    props = va.PROPERTIES
    ncol, nrow = len(props), len(order)
    fig_w, fig_h = 3.9 + 1.45 * ncol, 1.4 + 0.66 * nrow + 1.9
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=100)
    left, top, bottom = 3.8 / fig_w, 1 - 1.4 / fig_h, 1.9 / fig_h
    ax = fig.add_axes([left, bottom, 0.997 - left, top - bottom])
    ax.set_xlim(0, ncol)
    ax.set_ylim(nrow, 0)
    ax.axis("off")
    out = {}
    for i, sid in enumerate(order):
        v = va.system_validity(sid, ctx)
        out[sid] = v
        for j, (key, _) in enumerate(props):
            c = v[key]
            ax.add_patch(
                plt.Rectangle(
                    (j, i),
                    1,
                    1,
                    facecolor=va.COLORS[c["verdict"]],
                    edgecolor="#777",
                    lw=0.6,
                    hatch="///" if c["flag"] else None,
                )
            )
            txt = c["verdict"] if c["verdict"] != va.NA else ""
            if c["verdict"] == va.NOT_YET and c.get("then"):
                txt = f"not yet\n(then: {c['then']})"
            elif c["value"]:
                txt += "\n" + c["value"]
            if c["flag"]:
                txt += "\n(eq. not accepted)"
            ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=7.4)
        m = ctx["meta"][sid]
        tag = f"{(m['resolution'] or '?').upper()} {ss.POLYMER_NAME.get(m['polymer'], '?')}, {ss.kind_label(m)}"
        ax.text(-0.08, i + 0.38, sid, ha="right", va="center", fontsize=8, family="monospace")
        ax.text(-0.08, i + 0.75, tag, ha="right", va="center", fontsize=7, color="#555")
    for j, (_, lab) in enumerate(props):
        ax.text(
            j + 0.5,
            -0.12,
            lab.replace(" ", "\n", 1) if len(lab) > 12 else lab,
            ha="center",
            va="bottom",
            fontsize=8.5,
            weight="bold",
        )
    fig.suptitle(
        "Physical validity: can each property be compared with experiment, per system"
        f"  (generated {time.strftime('%Y-%m-%d %H:%M %Z')})",
        fontsize=13,
        weight="bold",
        y=1 - 0.25 / fig_h,
    )
    handles = [
        Patch(facecolor=va.COLORS[k], edgecolor="#777", label=f"{k}: {va.MEANING[k]}")
        for k in va.VERDICTS
    ]
    handles.append(
        Patch(
            facecolor="white",
            edgecolor="#777",
            hatch="///",
            label="flagged: 500 K equilibration not accepted / no verdict",
        )
    )
    fig.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.01, 0.95 / fig_h),
        ncol=4,
        fontsize=8.5,
        frameon=False,
    )
    notes = (
        "Rules: scripts/validity.py (single source of truth; base = docs/property_guide.md comparability table, refined by each system's checks). "
        "Chain size at the sweep T is 'trend' when a hold's chain COM MSD < ⟨Rg²⟩ (inherited from the 500 K melt). "
        "C1500: D47 not reached → 500 K chain size 'trend'.\n"
        "D_COM counts only when the COM MSD is diffusive and ≥ 2⟨Rg²⟩ (sweep hold or D53 diffuse hold). γ is cutoff-dependent (D48); 'size Δγ' = largest 40-chain vs 2×2×2 "
        "difference in combined SEM (D50).\nCG dynamics correction: times × 4.07 (Hall et al. 2019), recalibrate per T against UA/AA. "
        "Reasons per cell: results/summary.md, 'Physical validity by system'; numbers vs experiment: docs/experiment_comparison.md."
    )
    fig.text(0.01, 0.1 / fig_h, notes, fontsize=8.5, va="bottom", ha="left")
    fig.savefig(path)
    plt.close(fig)
    return out


# ---------------------------------------------------------------- per-system dashboard


def _thin_plan(segs: list[dict], max_points: int) -> list[int]:
    total = sum(max(s["duration_ns"], 1e-9) for s in segs) or 1.0
    return [max(20, int(max_points * max(s["duration_ns"], 1e-9) / total)) for s in segs]


def draw_timeline(ax, segs: list[dict], q: str, labels: bool = False) -> None:
    """One quantity over the concatenated segments (see the module docstring)."""
    col = QCOLOR.get(q, "black")
    have = [s for s in segs if q in s["quantities"]]
    if not have:
        ax.text(0.5, 0.5, f"no {q} data", transform=ax.transAxes, ha="center", va="center")
        return
    for s, k in zip(have, _thin_plan(have, MAX_POINTS), strict=True):
        r = s["quantities"][q]
        t = np.asarray(r["t"]) + s["t0"]
        y = np.asarray(r["value"])
        if q in ZOOM_Q and r.get("binned"):  # noisy: bin means of the full series
            bt, by = np.asarray(r["binned"]).T
            ax.plot(bt + s["t0"], by, color=col, alpha=0.5, lw=0.7)
        else:
            idx = thin_idx(len(t), k)
            ax.plot(t[idx], y[idx], color=col, alpha=0.28, lw=0.6)
        w0, w1 = s["t0"] + s["window"][0], s["t0"] + s["window"][1]
        drift = r.get("drift")
        ax.axvspan(
            w0, w1, color="#ff3030" if drift else "#808080", alpha=0.16 if drift else 0.07, lw=0
        )
        b = r.get("blocks") or []
        if b:
            ax.errorbar(
                [x["t"] + s["t0"] for x in b],
                [x["mean"] for x in b],
                yerr=[x["sem"] for x in b],
                fmt="o",
                ms=2.2,
                color=col,
                ecolor="black",
                elinewidth=0.7,
                capsize=1.2,
                zorder=3,
            )
    for s in segs:
        ax.axvline(s["t0"], color="#999", lw=0.4, zorder=0)
    stages = [
        (s["t0"], s["stage"])
        for k, s in enumerate(segs)
        if k == 0 or segs[k - 1]["stage"] != s["stage"]
    ]
    for t0, name in stages:
        ax.axvline(t0, color="black", lw=1.2, ls="--", zorder=1)
        if labels:
            ax.text(
                t0,
                1.0,
                f" {name}",
                transform=ax.get_xaxis_transform(),
                fontsize=7.5,
                va="bottom",
                ha="left",
                weight="bold",
            )
    if labels:
        for s in segs:
            mid = s["t0"] + 0.5 * s["duration_ns"]
            if s["kind"] == "hold":
                txt, kw = f"{s['t_set_c']:.0f}°C\nhold", {"weight": "bold", "fontsize": 6.5}
            else:
                txt = (
                    f"{s['t_set_c']:.0f}"
                    if s["kind"] == "step"
                    else f"{s['t_set_c'] + 273.15:.0f} K"
                )
                kw = {"fontsize": 5.5, "rotation": 90}
            ax.text(
                mid,
                0.98,
                txt,
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                color="#333",
                **kw,
            )
    if q in ZOOM_Q:  # trace fluctuations >> the means: zoom on the block means
        b = [x for s in have for x in s["quantities"][q].get("blocks") or []]
        if b:
            lo = min(x["mean"] - x["sem"] for x in b)
            hi = max(x["mean"] + x["sem"] for x in b)
            pad = 0.4 * (hi - lo) + 1e-9
            ax.set_ylim(lo - pad, hi + pad)
            ax.text(
                0.995,
                0.02,
                "trace: means of ~250-row bins; y zoomed on the block means",
                transform=ax.transAxes,
                ha="right",
                va="bottom",
                fontsize=6.5,
                color="#555",
            )
    ax.set_ylabel(QLABEL.get(q, q), fontsize=8.5)
    ax.tick_params(labelsize=7.5)
    ax.margins(x=0.005)
    if labels:  # room for the T labels
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.22 * (hi - lo))


def draw_chain_row(axes, hold: dict | None, owner: str | None, sid: str, ctx: dict) -> None:
    ax_cn, ax_acf, ax_msd, ax_txt = axes
    inherited = owner is not None and owner != sid
    tag = f" (inherited from {owner})" if inherited else ""
    curves = (hold or {}).get("curves")
    if not curves:
        for a in (ax_cn, ax_acf, ax_msd):
            a.text(
                0.5, 0.5, "no 500 K hold checks", transform=a.transAxes, ha="center", va="center"
            )
            a.set_xticks([])
            a.set_yticks([])
    else:
        ref = (hold.get("msid") or {}).get("reference") or [6.7, 6.7]
        ax_cn.axhspan(
            0.9 * ref[0], 1.1 * ref[-1], color="#2e8b57", alpha=0.15, label="melt C∞ ±10%"
        )
        ax_cn.axhline(ref[0], color="#2e8b57", lw=0.8)
        ax_cn.plot(curves["plateau_t_ns"], curves["plateau_t"], ".", ms=2.5, color="#1f5fa8")
        pl = (hold.get("msid") or {}).get("plateau")
        if pl is not None:
            ax_cn.axhline(pl, color="#1f5fa8", lw=1.0, ls=":", label=f"plateau {pl:.2f}")
        for b in hold.get("boundaries_ns") or []:
            ax_cn.axvline(b, color="black", ls="--", lw=1)
            ax_cn.text(
                b, 0.02, " prep | extension", transform=ax_cn.get_xaxis_transform(), fontsize=7
            )
        ax_cn.set_xlabel("time at 500 K (ns)", fontsize=8)
        ax_cn.set_ylabel("C$_n$ plateau (n ≥ 100 C)", fontsize=8.5)
        ax_cn.legend(fontsize=7, loc="upper right")
        ax_acf.plot(curves["acf_lag_ns"], curves["acf"], color="#c0392b")
        ax_acf.axhline(D47_ACF, color="black", ls="--", lw=0.9, label="1/e")
        lag = ss.get(hold, "ree_acf", "lag_ns")
        if lag:
            ax_acf.axvline(lag, color="#777", ls=":", lw=0.9, label="D47 lag (half run)")
        ax_acf.set_xlabel("lag (ns)", fontsize=8)
        ax_acf.set_ylabel("end-to-end vector ACF", fontsize=8.5)
        ax_acf.legend(fontsize=7)
        rg2 = ss.get(hold, "com_msd", "rg2_A2")
        if rg2:
            ax_msd.plot(curves["msd_lag_ns"], np.asarray(curves["msd_A2"]) / rg2, color="#7d3c98")
            ax_msd.axhline(D47_MSD_RG2, color="black", ls="--", lw=0.9, label="2 ⟨Rg²⟩ (D47)")
            ax_msd.axhline(1.0, color="#777", ls=":", lw=0.8, label="⟨Rg²⟩")
            if lag:
                ax_msd.axvline(lag, color="#777", ls=":", lw=0.9)
            ax_msd.legend(fontsize=7)
        ax_msd.set_xlabel("lag (ns)", fontsize=8)
        ax_msd.set_ylabel("chain COM MSD / ⟨R$_g^2$⟩", fontsize=8.5)
        for a in (ax_cn, ax_acf, ax_msd):
            a.tick_params(labelsize=7.5)
    ax_cn.set_title("C$_n$ plateau vs time (500 K)" + tag, fontsize=9)
    ax_acf.set_title("R$_{ee}$ vector ACF", fontsize=9)
    ax_msd.set_title("chain COM MSD / ⟨R$_g^2$⟩", fontsize=9)
    ax_txt.axis("off")
    eq = ctx["eq"][sid]
    ch = eq.get("checks") or {}
    d = ch.get("d47") or {}
    lines = ["500 K equilibration" + (f"\ninherited from {owner}" if inherited else "")]
    if d:
        hold_ns = ch.get("hold_ns")
        lines += [
            f"hold {_f(hold_ns, '.1f')} ns ({ch.get('stage')})",
            f"R_ee ACF {_f(d.get('acf'))} at {_f(d.get('lag_ns'), '.1f')} ns (< {D47_ACF:.3f})",
            f"COM MSD/<Rg²> {_f(d.get('ratio'))} (≥ {D47_MSD_RG2:g})",
        ]
    if ch.get("plateau") is not None:
        lines.append(f"C_n {_f(ch['plateau'])}, drift: {'yes' if ch.get('drift') else 'no'} (info)")
    acc = eq.get("accepted")
    verdict = "ACCEPTED" if acc else "NOT ACCEPTED" if acc is False else "no verdict yet"
    if long_cg(sid, ctx):
        verdict += "\n(C1500: D47 n/a, C_n no-drift rule)"
    lines.append("")
    lines.append(verdict)
    ax_txt.text(
        0.02,
        0.95,
        "\n".join(lines),
        va="top",
        ha="left",
        fontsize=8.5,
        transform=ax_txt.transAxes,
        bbox={
            "facecolor": COLORS[PASS] if acc else COLORS[FAIL] if acc is False else COLORS[NOTRUN],
            "alpha": 0.6,
            "edgecolor": "#777",
        },
    )


HOLD_COLORS = {25: "#1f5fa8", 90: "#2e8b57", 130: "#e67e22", 160: "#c0392b"}


def hold_color(t_c: float) -> str:
    return HOLD_COLORS.get(round(t_c), plt.get_cmap("viridis")(np.clip((t_c - 25) / 135, 0, 1)))


def draw_sem_vs_block(ax, holds: list[dict], q: str) -> None:
    any_ = False
    for s in holds:
        curve = (s["quantities"].get(q) or {}).get("sem_vs_block") or []
        if not curve:
            continue
        any_ = True
        c = hold_color(s["t_set_c"])
        ax.plot(
            [p["block_ns"] for p in curve],
            [p["ratio"] for p in curve],
            "o-",
            ms=3,
            color=c,
            label=f"{s['t_set_c']:.0f} °C" + (" (running)" if s["state"] != "done" else ""),
        )
    ax.axhline(1.0, color="black", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("block length (ns)", fontsize=8)
    ax.set_ylabel("block SEM / stat.-ineff. SEM", fontsize=8)
    ax.set_title(f"holds: SEM vs block size ({QLABEL.get(q, q).split(' (')[0]})", fontsize=9)
    ax.tick_params(labelsize=7.5)
    if any_:
        ax.legend(fontsize=7)
    else:
        ax.text(0.5, 0.5, "no hold data yet", transform=ax.transAxes, ha="center", va="center")


def _pm(r: dict | None, spec: str) -> str:
    if not r or r.get("mean") is None:
        return "—"
    return f"{r['mean']:{spec}} ± {r['sem']:{spec}}"


def draw_hold_table(ax, holds: list[dict], pore: bool) -> None:
    ax.axis("off")
    ax.set_title("holds: analysis-window mean ± SEM, drift (halves > 2 SEM)", fontsize=9)
    if not holds:
        ax.text(0.5, 0.5, "no hold data yet", transform=ax.transAxes, ha="center", va="center")
        return
    if pore:
        head = ["T (°C)", "window (ns)", "γ (mN/m)", "PE (kcal/mol)", "Pzz (atm)", "drift"]
        keys = (("gamma", ".2f"), ("pe", ".1f"), ("pzz", ".2f"))
        dq = ("gamma", "pe", "T")
    else:
        head = ["T (°C)", "window (ns)", "ρ (g/cm³)", "ρ SEM %", "H (kcal/mol)", "drift"]
        keys = (("density", ".5f"), ("enthalpy", ".1f"))
        dq = ("density", "enthalpy", "T")
    rows, colors = [], []
    for s in holds:
        qs = s["quantities"]
        row = [
            f"{s['t_set_c']:.0f}" + ("*" if s["state"] != "done" else ""),
            f"{s['window'][1] - s['window'][0]:.2f}",
        ]
        if pore:
            row += [_pm(qs.get(k), f) for k, f in keys]
        else:
            d = qs.get("density") or {}
            row += [
                _pm(d, ".5f"),
                f"{d['sem'] / d['mean'] * 100:.4f}" if d.get("sem") is not None else "—",
                _pm(qs.get("enthalpy"), ".1f"),
            ]
        flagged = [q for q in dq if (qs.get(q) or {}).get("drift")]
        row.append(", ".join(flagged) or "none")
        rows.append(row)
        colors.append(["white"] * (len(row) - 1) + [COLORS[FLAG] if flagged else COLORS[PASS]])
    tab = ax.table(
        cellText=rows, colLabels=head, cellColours=colors, loc="upper center", cellLoc="center"
    )
    tab.auto_set_font_size(False)
    tab.set_fontsize(7.5)
    tab.scale(1, 1.35)
    if any(s["state"] != "done" for s in holds):
        ax.text(0.0, 0.0, "* running: partial window", transform=ax.transAxes, fontsize=7)


def draw_gamma_vs_t(ax, segs: list[dict]) -> None:
    for kind, mk, col in (
        ("cool", "v", "#1f5fa8"),
        ("step", "o", "#d35400"),
        ("hold", "s", "black"),
    ):
        pts = [
            s
            for s in segs
            if s["kind"] == kind and (s["quantities"].get("gamma") or {}).get("mean") is not None
        ]
        if pts:
            g = [s["quantities"]["gamma"] for s in pts]
            ax.errorbar(
                [s["t_set_c"] for s in pts],
                [x["mean"] for x in g],
                yerr=[x["sem"] for x in g],
                fmt=mk,
                ms=4,
                color=col,
                capsize=2,
                label={"cool": "step-cool", "step": "sweep step", "hold": "sweep hold"}[kind],
                mfc="none" if kind == "cool" else col,
            )
    ax.set_xlabel("T (°C)", fontsize=8)
    ax.set_ylabel("γ (mN/m per surface)", fontsize=8)
    ax.set_title("γ vs T (window means ± SEM)", fontsize=9)
    ax.tick_params(labelsize=7.5)
    if ax.get_legend_handles_labels()[0]:
        ax.legend(fontsize=7)


def film_records(res: dict | None, segs: list[dict]) -> list[dict]:
    """Pore analysis ``convergence`` entries mapped onto the timeline: per matching
    segment (by name) the film quantities as quantity records relative to its start."""
    conv = (res or {}).get("convergence")
    if not isinstance(conv, list):
        return []
    by_name = {s["name"]: s for s in segs}
    out = []
    for c in conv:
        s = by_name.get(c.get("name")) if isinstance(c, dict) else None
        if s is None:
            continue
        t_start = c.get("t_start_ps", s["t_start_ps"])
        qs = {}
        for q in FILM_Q:
            r = (c.get("quantities") or {}).get(q)
            if not r or not r.get("t_ps"):
                continue
            qs[q] = {
                "t": [(t - t_start) / 1000.0 for t in r["t_ps"]],
                "value": r.get("value") or [],
                "blocks": [
                    {"t": (b["t"] - t_start) / 1000.0, "mean": b["mean"], "sem": b["sem"]}
                    for b in r.get("blocks") or []
                ],
                "drift": r.get("drift"),
            }
        if qs:
            w = c.get("window") or [t_start, c.get("t_end_ps", t_start)]
            out.append(
                dict(
                    s, quantities=qs, window=[(w[0] - t_start) / 1000.0, (w[1] - t_start) / 1000.0]
                )
            )
    return out


def _no_data(ax, msg: str) -> None:
    ax.text(
        0.5,
        0.5,
        msg,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=8,
        color="#555",
        wrap=True,
    )
    ax.set_xticks([])
    ax.set_yticks([])


def _small(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=9)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(labelsize=7.5)


def draw_kappa_running(ax, holds: list[dict]) -> None:
    """Running (cumulative) κ_T over each hold window; final value ± SEM at the end."""
    have = [s for s in holds if s.get("kappa")]
    if not have:
        _no_data(ax, "no NPT hold volume data yet")
        ax.set_title("κ$_T$ running estimate", fontsize=9)
        return
    for s in have:
        k, c = s["kappa"], hold_color(s["t_set_c"])
        t, y = np.asarray(k["running"]).T
        ax.plot(t, y, color=c, lw=1.2, label=f"{s['t_set_c']:.0f} °C")
        ax.errorbar(
            [t[-1] * 1.01], [k["kappa"]], yerr=[k["sem"]], fmt="o", color=c, ms=3, capsize=2
        )
    _small(ax, "κ$_T$ running (cumulative) estimate", "time in hold (ns)", "κ$_T$ (GPa$^{-1}$)")
    ax.legend(fontsize=7, ncol=2)


def draw_kappa_blocks(ax, holds: list[dict]) -> None:
    """κ_T per block of each hold window, and the two halves ± SEM (red: > 2 SEM)."""
    have = [s for s in holds if s.get("kappa")]
    if not have:
        _no_data(ax, "no NPT hold volume data yet")
        ax.set_title("κ$_T$ blocks and halves", fontsize=9)
        return
    for i, s in enumerate(have):
        k, c = s["kappa"], hold_color(s["t_set_c"])
        nb = len(k["blocks"])
        x = i + np.linspace(-0.35, 0.35, nb)
        ax.plot(x, [b["kappa"] for b in k["blocks"]], "o", color=c, ms=3, alpha=0.7)
        col = "#d62728" if k["drift"] else "black"
        for j, (m, e) in enumerate((k["first"], k["second"])):
            ax.errorbar([i - 0.2 + 0.4 * j], [m], yerr=[e], fmt="s", color=col, ms=4, capsize=3)
        ax.text(
            i,
            1.0,
            f"Δ {k['delta']:+.3f}\n± {k['delta_sem']:.3f}",
            fontsize=6.5,
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            color=col,
        )
    ax.set_xticks(range(len(have)), [f"{s['t_set_c']:.0f} °C" for s in have])
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + 0.3 * (hi - lo))
    _small(
        ax,
        f"κ$_T$: {KAPPA_BLOCKS} blocks (dots), halves ± SEM (squares; red > 2 SEM)",
        "",
        "κ$_T$ (GPa$^{-1}$)",
    )


FIT_COLORS = {(25.0, 160.0): "black", (25.0, 90.0): "#1f5fa8", (90.0, 160.0): "#c0392b"}


def fit_residuals(res: dict | None, q: str) -> list[dict]:
    """Per fit window of ``fits[q]`` (alpha_V: volume, cp: enthalpy): the fit points'
    residuals from the stored line (T in K) with their SEMs, and χ²_red."""
    if not res:
        return []
    stat = "volume" if q == "alpha_V" else "enthalpy"
    pts = {}
    for sg in res.get("segments") or []:  # D49: latest completed segment per set T
        st = (sg.get("stats") or {}).get(stat)
        if sg.get("done") and st and st.get("mean") is not None and sg.get("t_set_c") is not None:
            pts[round(sg["t_set_c"], 3)] = st
    out = []
    for f in (res.get("fits") or {}).get(q) or []:
        lo, hi = f.get("window_c") or (None, None)
        line = f.get("line")
        if lo is None or not line:
            continue
        sel = sorted(t for t in pts if lo - 1e-6 <= t <= hi + 1e-6)
        out.append(
            {
                "window": (lo, hi),
                "t": sel,
                "resid": [pts[t]["mean"] - (line[0] * (t + 273.15) + line[1]) for t in sel],
                "err": [pts[t].get("sem") or 0.0 for t in sel],
                "chi2": f.get("chi2_red"),
            }
        )
    return out


def draw_fit_residuals(ax, res: dict | None, q: str) -> None:
    name = "α$_V$: V(T)" if q == "alpha_V" else "C$_p$: H(T)"
    unit = "Å$^3$" if q == "alpha_V" else "kcal/mol"
    rs = fit_residuals(res, q)
    if not rs:
        _no_data(ax, "no sweep analysis (fits) yet")
        ax.set_title(f"{name} fit residuals", fontsize=9)
        return
    for k, r in enumerate(rs):
        c = FIT_COLORS.get(tuple(r["window"]), "gray")
        ax.errorbar(
            np.asarray(r["t"]) + (k - 1) * 1.2,
            r["resid"],
            yerr=r["err"],
            fmt="o-",
            ms=3,
            lw=0.8,
            color=c,
            capsize=1.5,
            label=f"{r['window'][0]:g}–{r['window'][1]:g} °C: χ²$_{{red}}$ {r['chi2']:.3g}",
        )
    ax.axhline(0, color="#777", lw=0.8)
    curved = any((r["chi2"] or 0) > CURVED_CHI2 for r in rs)
    _small(
        ax,
        f"{name} minus linear fit" + (" (curved: info)" if curved else ""),
        "T (°C)",
        f"residual ({unit})",
    )
    ax.legend(fontsize=6.5)


def _hold_curves(res: dict | None) -> list[tuple[float, dict, dict]]:
    out = []
    for h in (res or {}).get("holds") or []:
        t = va.hold_traj(h)
        if t.get("curves"):
            out.append((h.get("t_c"), t, t["curves"]))
    return out


def log_slope(lag, y, smooth: int = 7) -> tuple[np.ndarray, np.ndarray]:
    """Local d ln y / d ln lag (positive lags and values), smoothed over ``smooth`` points."""
    lag, y = np.asarray(lag, dtype=float), np.asarray(y, dtype=float)
    ok = (lag > 0) & (y > 0)
    lag, y = lag[ok], y[ok]
    if len(lag) < smooth + 2:
        return np.array([]), np.array([])
    s = np.gradient(np.log(y), np.log(lag))
    k = np.ones(smooth) / smooth
    s = np.convolve(s, k, mode="valid")
    return lag[smooth // 2 : smooth // 2 + len(s)], s


NOT_STORED = "not stored in results.json"


def draw_msd(ax, res: dict | None) -> None:
    hc = _hold_curves(res)
    if not hc:
        _no_data(ax, "no hold MSD curves (" + ("no analysis" if res is None else NOT_STORED) + ")")
        ax.set_title("segment and chain COM MSD", fontsize=9)
        return
    for tc, t, c in hc:
        col = hold_color(tc)
        if c.get("msd_lag_ps"):
            ax.loglog(c["msd_lag_ps"], c["msd_A2"], color=col, lw=1, label=f"{tc:g} °C segment")
        if c.get("com_lag_ps"):
            ax.loglog(c["com_lag_ps"], c["com_A2"], color=col, lw=1, ls="--")
        rg2 = ss.get(t, "rg", "rg2_A2", "mean")
        if rg2:
            ax.axhline(rg2, color=col, lw=0.6, ls=":")
    _small(
        ax, "MSD: segment (solid), chain COM (dashed); ⟨R$_g^2$⟩ dotted", "lag (ps)", "MSD (Å$^2$)"
    )
    ax.legend(fontsize=6.5, loc="upper left")


def draw_log_slope(ax, res: dict | None) -> None:
    hc = _hold_curves(res)
    if not hc:
        _no_data(ax, "no hold MSD curves")
        ax.set_title("local log-slope of the MSD", fontsize=9)
        return
    for tc, t, c in hc:
        col = hold_color(tc)
        if c.get("com_lag_ps"):
            x, y = log_slope(c["com_lag_ps"], c["com_A2"])
            com = t.get("com_msd") or {}
            tag = "diffusive" if com.get("diffusive") else "not diffusive"
            ax.semilogx(x, y, color=col, lw=1.1, label=f"{tc:g} °C COM: {tag}")
        if c.get("msd_lag_ps"):
            x, y = log_slope(c["msd_lag_ps"], c["msd_A2"])
            ax.semilogx(x, y, color=col, lw=0.6, ls=":", alpha=0.8)
    ax.axhline(1.0, color="black", lw=0.8)
    ax.axhline(D_MIN_SLOPE, color="black", lw=0.8, ls="--")
    ax.set_ylim(0, 2.0)
    _small(
        ax,
        "d ln MSD / d ln t: COM (solid), segment (dotted); 0.9 = D49",
        "lag (ps)",
        "local log-slope",
    )
    ax.legend(fontsize=6.5, loc="upper left")


def draw_p2(ax, res: dict | None) -> None:
    hc = [(tc, t, c) for tc, t, c in _hold_curves(res) if c.get("p2_lag_ps")]
    if not hc:
        _no_data(ax, "no P2 ACF curves (" + ("no analysis" if res is None else NOT_STORED) + ")")
        ax.set_title("bond P2 ACF", fontsize=9)
        return
    for tc, t, c in hc:
        col = hold_color(tc)
        t1e = ss.get(t, "p2", "t_1e_ps")
        lab = f"{tc:g} °C: 1/e at {t1e:.3g} ps" if t1e else f"{tc:g} °C: 1/e NOT reached"
        ax.semilogx(c["p2_lag_ps"], c["p2"], color=col, lw=1.1, label=lab)
        if t1e:
            ax.plot([t1e], [np.exp(-1)], "o", color=col, ms=4)
    ax.axhline(np.exp(-1), color="black", lw=0.8, ls="--")
    _small(ax, "bond P2 ACF (1/e dashed)", "lag (ps)", "⟨P2(u(0)·u(t))⟩")
    ax.legend(fontsize=6.5)


def draw_chain_ratio(ax, res: dict | None) -> None:
    r = chain_ratios(res)
    if not r:
        _no_data(
            ax, "no hold chain COM MSD (" + ("no analysis" if res is None else NOT_STORED) + ")"
        )
        ax.set_title("chain-scale relaxation per hold", fontsize=9)
        return
    x = np.arange(len(r))
    vals = [v for _, v in r]
    ax.bar(
        x,
        vals,
        color=[COLORS[PASS] if v >= CHAIN_RELAXED else COLORS[FLAG] for v in vals],
        edgecolor="#555",
    )
    ax.axhline(CHAIN_RELAXED, color="black", ls="--", lw=0.9)
    for xi, v in zip(x, vals, strict=True):
        ax.text(xi, v, f"{v:.2f}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x, [f"{t:g} °C" for t, _ in r])
    ax.set_ylim(0, max(1.35, max(vals) * 1.25))
    if min(vals) < CHAIN_RELAXED:
        ax.text(
            0.5,
            0.97,
            "< 1: chain size inherited from the cooled melt\n(not re-equilibrated at this T)",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=7,
            color="#7a5c00",
        )
    _small(ax, "chain COM MSD at max lag / ⟨R$_g^2$⟩ per hold", "", "ratio")


CHAIN_Q = (
    ("rg", ("rg", "rg_A"), "R$_g$ (Å)"),
    ("ree", ("ree", "ree_A"), "R$_{ee}$ (Å)"),
    ("cn", ("c_n", "plateau"), "C$_n$ plateau"),
)


def draw_chain_vs_t(ax, res: dict | None, which: int, eq_hold: dict | None) -> None:
    key, path, lab = CHAIN_Q[which]
    pts = [(h.get("t_c"), ss.get(va.hold_traj(h), *path)) for h in (res or {}).get("holds") or []]
    pts = [(t, v) for t, v in pts if isinstance(v, dict) and v.get("mean") is not None]
    if not pts:
        _no_data(ax, "no hold chain-size data")
        ax.set_title(f"{lab.split(' (')[0]} vs T", fontsize=9)
        return
    ax.errorbar(
        [t for t, _ in pts],
        [v["mean"] for _, v in pts],
        yerr=[v.get("sem") or 0 for _, v in pts],
        fmt="o-",
        color="#1f5fa8",
        capsize=3,
        ms=4,
    )
    ref = None  # the 500 K value from the equilibration hold, when stored
    if eq_hold:
        if key == "rg" and ss.get(eq_hold, "com_msd", "rg2_A2"):
            ref = float(np.sqrt(eq_hold["com_msd"]["rg2_A2"]))
        elif key == "ree" and ss.get(eq_hold, "ree_acf", "r2_mean_A2"):
            ref = float(np.sqrt(eq_hold["ree_acf"]["r2_mean_A2"]))
        elif key == "cn":
            ref = ss.get(eq_hold, "msid", "plateau")
            band = ss.get(eq_hold, "msid", "reference")
            if band:
                ax.axhspan(
                    0.9 * band[0], 1.1 * band[-1], color="#2e8b57", alpha=0.12, label="melt C∞ ±10%"
                )
    if ref:
        ax.axhline(ref, color="#c0392b", ls="--", lw=0.9, label="500 K hold")
    if ax.get_legend_handles_labels()[0]:
        ax.legend(fontsize=6.5)
    _small(ax, f"{lab.split(' (')[0]} vs T (hold mean ± SEM)", "T (°C)", lab)


def draw_dyn_text(ax, res: dict | None, pore: bool) -> None:
    ax.axis("off")
    ax.set_title("per-hold verdicts", fontsize=9)
    if res is None:
        ax.text(
            0.02,
            0.95,
            f"no {'pore' if pore else 'sweep'} analysis results.json yet",
            transform=ax.transAxes,
            va="top",
            fontsize=8,
        )
        return
    lines = []
    for h in res.get("holds") or []:
        t = va.hold_traj(h)
        com = t.get("com_msd") or {}
        t1e = ss.get(t, "p2", "t_1e_ps")
        d = (
            f"D {com['D_cm2_s']:.2g} cm²/s"
            if com.get("D_cm2_s") is not None
            else f"not diff. (slope {_f(com.get('slope_end'))})"
            if com
            else "—"
        )
        p2 = f"P2 1/e {t1e:.3g} ps" if t1e else ("P2 1/e not reached" if t.get("p2") else "P2 —")
        lines.append(f"{_f(h.get('t_c'), 'g')} °C: {d}; {p2}")
    missing = [
        "per-frame/block Rg, R_ee, C_n series\n  (chain-size drift within a hold)",
        "D_COM fit window (t_start, t_end)",
    ]
    lines += ["", "not stored in results.json:", *[f"• {m}" for m in missing]]
    ax.text(0.02, 0.97, "\n".join(lines), transform=ax.transAxes, va="top", fontsize=7.3)


def _msd(summary: dict, key: str, spec: str) -> str:
    """'mean ± SD' of a tensile summary entry ({mean, sd})."""
    v = summary.get(key) or {}
    if v.get("mean") is None:
        return "—"
    return f"{v['mean']:{spec}} ± {v.get('sd') or 0:{spec}}"


def draw_extra_row(axes, sid: str, ctx: dict) -> None:
    """diffuse (D53): COM MSD/⟨Rg²⟩ vs lag and D_COM; tensile (D54): status and E/ν/peak;
    hole (D52): status."""
    ax_msd, ax_txt, ax_ten, ax_hole = axes
    dif = extra_runs(sid, ctx, "diffuse")
    lines = []
    any_curve = False
    for r in dif:
        hold = ss.get(r, "progress", "hold") or {}
        c, rg2 = hold.get("curves") or {}, ss.get(hold, "com_msd", "rg2_A2")
        tag = r["dir"].removeprefix("diffuse_")
        if c.get("msd_lag_ns") and rg2:
            any_curve = True
            ax_msd.loglog(c["msd_lag_ns"], np.asarray(c["msd_A2"]) / rg2, label=tag)
        d = hold.get("d_com") or {}
        lines.append(f"{r['dir']}: {ss.get(r, 'progress', 'status') or '?'}, {_run_txt(r)}")
        lines.append("   " + (d_com_flag(d) if d else "no D_COM check yet"))
    if any_curve:
        ax_msd.axhline(1.0, color="black", ls="--", lw=0.8)
        ax_msd.legend(fontsize=7)
        _small(ax_msd, "diffuse: chain COM MSD / ⟨R$_g^2$⟩", "lag (ns)", "MSD / ⟨R$_g^2$⟩")
    else:
        _no_data(ax_msd, "no diffuse (D53) COM MSD curves" if dif else "no diffuse run (D53)")
        ax_msd.set_title("diffuse: chain COM MSD", fontsize=9)
    ax_txt.axis("off")
    ax_txt.set_title("diffuse (D53) status and D_COM", fontsize=9)
    ax_txt.text(
        0.02,
        0.95,
        "\n".join(lines) or "no diffuse run",
        transform=ax_txt.transAxes,
        va="top",
        fontsize=7.5,
    )
    ax_ten.axis("off")
    ax_ten.set_title("tensile (D54)", fontsize=9)
    ana = ctx["analysis"].get(sid, {})
    tl = []
    for r in extra_runs(sid, ctx, "tensile"):
        tl.append(f"{r['dir']}: {ss.get(r, 'progress', 'status') or '?'}, {_run_txt(r)}")
        s = ss.get(ana.get(r["dir"]), "runs", 0, "summary") or {}
        if s:
            tl.append(
                f"   E_app {_msd(s, 'E_MPa', '.0f')} MPa, ν {_msd(s, 'nu_fit', '.2f')},"
                f" peak {_msd(s, 'peak_MPa', '.1f')} MPa"
            )
        else:
            tl.append("   no analysis yet")
    ax_ten.text(
        0.02,
        0.95,
        "\n".join(tl) or "no tensile run",
        transform=ax_ten.transAxes,
        va="top",
        fontsize=7.5,
    )
    ax_hole.axis("off")
    ax_hole.set_title("hole (D52)", fontsize=9)
    hl = [
        f"{r['dir']}: {ss.get(r, 'progress', 'status') or '?'}, {_run_txt(r)}"
        for r in extra_runs(sid, ctx, "hole")
    ]
    ax_hole.text(
        0.02,
        0.95,
        "\n".join(hl) or "no hole run",
        transform=ax_hole.transAxes,
        va="top",
        fontsize=7.5,
    )


def draw_dashboard(path: Path, sid: str, ctx: dict, data: dict) -> None:
    pore = data["pore"]
    segs = data["segments"]
    res = analysis_for(sid, ctx, "pore" if pore else "sweep")
    film = film_records(res, segs) if pore else []
    extra = any(extra_runs(sid, ctx, k) for k in ("diffuse", "tensile", "hole"))
    # rows: chain 500 K, 2 timelines, SEM/table, [film], [kappa/fits], dynamics, chain size, [extra]
    rows = ["chain", "tl1", "tl2", "sem"]
    if pore:
        rows.append("film")
    else:
        rows.append("kappa")
    rows += ["dyn", "size"] if res is not None or not pore else ["nodyn"]
    if extra:
        rows.append("extra")
    ratios = {
        "chain": 1,
        "tl1": 1,
        "tl2": 1,
        "sem": 1.05,
        "film": 0.9 if film else 0.12,
        "kappa": 1,
        "dyn": 1,
        "size": 1,
        "nodyn": 0.12,
        "extra": 0.8,
    }
    height = 3.0 * sum(ratios[r] for r in rows) + 1.2
    fig = plt.figure(figsize=(16, height), dpi=100)
    gs = GridSpec(
        len(rows),
        4,
        figure=fig,
        height_ratios=[ratios[r] for r in rows],
        hspace=0.62,
        wspace=0.28,
        left=0.055,
        right=0.985,
        top=1 - 1.5 / height,
        bottom=0.45 / height,
    )
    R = {r: i for i, r in enumerate(rows)}
    hold, owner = chain_source(sid, ctx)
    draw_chain_row([fig.add_subplot(gs[0, i]) for i in range(4)], hold, owner, sid, ctx)
    q = PORE_Q if pore else BULK_Q
    axes = [fig.add_subplot(gs[R["tl1"], 0:2]), fig.add_subplot(gs[R["tl1"], 2:4])]
    axes.append(fig.add_subplot(gs[R["tl2"], 0:2], sharex=axes[0]))
    axes.append(fig.add_subplot(gs[R["tl2"], 2:4], sharex=axes[1]))
    if segs:
        for a, qq in zip(axes, q, strict=True):
            draw_timeline(a, segs, qq, labels=a in axes[:2])
        for a in axes[2:]:
            a.set_xlabel("time along the runs (ns, segments concatenated)", fontsize=8)
        parts = " → ".join(dict.fromkeys(s["stage"] for s in segs))
        axes[0].set_title(
            f"{parts}: thinned trace, analysis windows shaded (red = halves differ > 2 SEM),"
            " block averages ± SEM",
            fontsize=9,
            loc="left",
            pad=14,
        )
    else:
        for a in axes:
            _no_data(a, "no cool/sweep/pore log yet")
    holds = [s for s in segs if s["kind"] == "hold"]
    r3 = R["sem"]
    if pore:
        draw_sem_vs_block(fig.add_subplot(gs[r3, 0]), holds, "gamma")
        draw_gamma_vs_t(fig.add_subplot(gs[r3, 1]), segs)
    else:
        draw_sem_vs_block(fig.add_subplot(gs[r3, 0]), holds, "density")
        draw_sem_vs_block(fig.add_subplot(gs[r3, 1]), holds, "enthalpy")
    draw_hold_table(fig.add_subplot(gs[r3, 2:4]), holds, pore)
    if pore:
        r = R["film"]
        if film:
            for i, qq in enumerate(FILM_Q):
                a = fig.add_subplot(gs[r, i])
                draw_timeline(a, film, qq)
                a.set_title(QLABEL[qq].split(" (")[0] + " (pore analysis)", fontsize=9)
                a.set_xlabel("time (ns)", fontsize=8)
            fig.add_subplot(gs[r, 3]).axis("off")
        else:
            a = fig.add_subplot(gs[r, :])
            a.axis("off")
            a.text(
                0.5,
                0.5,
                "Pore film analysis (film thickness, gap, interior density) not available yet:"
                f" results/analysis/{sid}/pore/results.json (sepsim analyze pore) missing or"
                " without a 'convergence' key. These panels appear once it exists.",
                ha="center",
                va="center",
                fontsize=10,
                color="#555",
                wrap=True,
            )
    else:
        r = R["kappa"]
        sweep_holds = [s for s in holds if s["part"] == "sweep"]
        draw_kappa_running(fig.add_subplot(gs[r, 0]), sweep_holds)
        draw_kappa_blocks(fig.add_subplot(gs[r, 1]), sweep_holds)
        draw_fit_residuals(fig.add_subplot(gs[r, 2]), res, "alpha_V")
        draw_fit_residuals(fig.add_subplot(gs[r, 3]), res, "cp")
    if "nodyn" in R:
        a = fig.add_subplot(gs[R["nodyn"], :])
        a.axis("off")
        a.text(
            0.5,
            0.5,
            "Pore dynamics and chain size per hold (MSD, log-slope, P2 ACF, chain-scale"
            " relaxation, Rg/R_ee/C_n vs T) appear once the pore analysis results.json"
            " (sepsim analyze pore, D51) exists with per-hold 'holds[].traj' like the sweep's.",
            ha="center",
            va="center",
            fontsize=10,
            color="#555",
            wrap=True,
        )
    else:
        _dyn_rows(fig, gs, R, res, hold, pore)
    if extra:
        draw_extra_row([fig.add_subplot(gs[R["extra"], i]) for i in range(4)], sid, ctx)
    _dashboard_title(fig, sid, ctx)
    fig.savefig(path)
    plt.close(fig)


def _dyn_rows(fig, gs, R, res, hold, pore) -> None:
    r = R["dyn"]
    draw_msd(fig.add_subplot(gs[r, 0]), res)
    draw_log_slope(fig.add_subplot(gs[r, 1]), res)
    draw_p2(fig.add_subplot(gs[r, 2]), res)
    draw_chain_ratio(fig.add_subplot(gs[r, 3]), res)
    r = R["size"]
    for i in range(3):
        draw_chain_vs_t(fig.add_subplot(gs[r, i]), res, i, hold)
    draw_dyn_text(fig.add_subplot(gs[r, 3]), res, pore)


def _dashboard_title(fig, sid: str, ctx: dict) -> None:
    m = ctx["meta"][sid]
    man = ctx["systems"].get(sid) or {}
    src = ss.source_info(man)
    prov = f"\nbuilt from {' ← '.join(s.get('id', '?') for s in src)}" if src else ""
    stage, status = ss.stage_now(sid, ctx)
    if len(status) > 110:
        status = status[:107] + "..."
    fig.suptitle(
        f"{sid}: {(m['resolution'] or '?').upper()} {ss.POLYMER_NAME.get(m['polymer'], '?')}"
        f" {man.get('n_chains', '?')} × C{man.get('n_carbons', '?')}, {ss.kind_label(m)}{prov}\n"
        f"now: {stage}: {status}",
        fontsize=11.5,
        weight="bold",
    )


# ---------------------------------------------------------------- main


def build(
    run_roots: list[Path],
    analysis_root: Path,
    systems_root: Path,
    out_dir: Path,
    only: list[str] | None = None,
    cache_dir: Path | None = None,
    log=print,
) -> dict:
    ctx = ss.build_context(run_roots, analysis_root, systems_root)
    order = current_order(ctx)
    draw = [s for s in order if not only or s in only]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "convergence").mkdir(exist_ok=True)
    cells, written = {}, []
    for sid in order:
        t = time.time()
        data = system_data(sid, ctx, cache_dir)
        cells[sid] = overview_cells(sid, ctx, data)
        if sid in draw:
            p = out_dir / "convergence" / f"{sid}.png"
            draw_dashboard(p, sid, ctx, data)
            written.append(p)
            log(f"{sid}: {len(data['segments'])} segments, {time.time() - t:.1f} s -> {p}")
    ov = out_dir / "convergence_overview.png"
    draw_overview(ov, ctx, order, cells)
    vo = out_dir / "validity_overview.png"
    verdicts = draw_validity(vo, ctx, order)
    log(f"wrote {ov} and {vo}")
    return {
        "order": order,
        "cells": cells,
        "validity": verdicts,
        "written": [ov, vo, *written],
        "ctx": ctx,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--runs",
        action="append",
        help="run root(s) (default results/runs and results/progress/rdyu-rog)",
    )
    ap.add_argument("--analysis", default="results/analysis")
    ap.add_argument("--systems", default="systems")
    ap.add_argument("--out-dir", default="results")
    ap.add_argument("--systems-only", nargs="+", metavar="ID", help="dashboards for these only")
    ap.add_argument("--cache", default=str(Path.home() / ".cache" / "che126_sims" / "convergence"))
    ap.add_argument("--no-cache", action="store_true")
    a = ap.parse_args(argv)
    if a.runs:
        roots = [ss._path(r) for r in a.runs]
    else:
        roots = [ss._path("results/runs")]
        if ss._path("results/progress/rdyu-rog").is_dir():
            roots.append(ss._path("results/progress/rdyu-rog"))
    t = time.time()
    build(
        roots,
        ss._path(a.analysis),
        ss._path(a.systems),
        ss._path(a.out_dir),
        a.systems_only,
        None if a.no_cache else Path(a.cache).expanduser(),
    )
    print(f"done in {time.time() - t:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
