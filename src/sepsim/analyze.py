"""Sweep analysis: `sepsim analyze sweep` (D49).

For a finished (or partly finished) bulk ``sweep`` run directory
``results/runs/<system>/<stage>/`` (deck ``in.sweep``, ``log.lammps``, the segment
DCDs) this writes ``results.md``, ``results.json`` and PNG plots into
``results/analysis/<system>/<stage>/`` (or ``--out``):

- per segment (14 steps + 4 holds): T, density, enthalpy and volume as mean +- SEM
  (statistical inefficiency, D26) over the second half of a step and over a hold
  without its first ``HOLD_SKIP`` (10%);
- per hold: the isothermal compressibility from the volume fluctuations,
  kappa_T = (<V^2> - <V>^2) / (k_B T <V>), over the same window;
- over the sweep: alpha_V and classical Cp = dH/dT from linear fits over 25-160,
  25-90 and 90-160 C (one point per temperature, the hold where there is one);
- per hold, from the hold DCD (10 ps frames) and its D46 burst DCDs (0.1 ps,
  10 ps long): backbone-site MSD and chain COM MSD vs lag (bursts below the hold
  frame interval, the hold DCD from there to half the hold), D_COM from the diffusive
  end of the COM MSD (local log-slope >= 0.9 over a factor >= 2 in lag), the
  backbone bond P2 autocorrelation and its 1/e time, and <Rg^2>^1/2,
  <R_ee^2>^1/2 and the C_n plateau (n >= 100 carbons, D37) averaged over the hold
  (with <= 100 block means of each for convergence plots);
- per hold (D56): the end-to-end vector and Rouse mode (p = 1..5) autocorrelations with
  their 1/e times and exponential fits (``chain_relaxation``), and a crystallinity
  monitor (D26 alignment order, fixed uncalibrated threshold; ``crystallinity_monitor``).

The segment parser, log reader and thermo concatenation are those of
:mod:`sepsim.progress`; the DCDs are read with MDAnalysis ``DCDReader`` (id-sorted,
unwrapped, D39). Holds without a DCD are reported as "trajectory not available".
Pore decks (``in.pore``) are rejected with a pointer to `sepsim analyze pore` (D51,
:mod:`sepsim.analyze_pore`).
"""

from __future__ import annotations

import warnings
from functools import cached_property
from pathlib import Path

import numpy as np

from sepsim.analysis.chain import CG_CC_BOND_A, CN_N_MIN
from sepsim.analysis.lammps_log import read_log
from sepsim.analysis.stats import DegenerateSeries, timeseries_mean
from sepsim.analysis.units import A2_PS_TO_CM2_S, A3_CM3, AVOGADRO
from sepsim.progress import (
    JSON_NAME as PROGRESS_JSON,
)
from sepsim.progress import (
    LOG_NAME,
    MIN_DRIFT_ROWS,
    MIN_HOLD_FRAMES,
    MIN_STAT_ROWS,
    SEM_RESOLVE_BLOCKS,
    T_MATCH_TOL,
    _block_rows,
    _concat_thermo,
    _enthalpy_mean_sem,
    _input_stage,
    _mean_sem,
    _ms_of,
    _round,
    d47_criteria,
    deck_system,
    find_deck,
    load_json,
    parse_deck,
    runs_by_segment,
)
from sepsim.reporting import (
    CG_TIME_NOTE,
    _f,
    _json,
    _pm,
    dump_json,
    header_markdown,
    load_system_arrays,
    plots_markdown,
    report_header,
    trajectory_or_note,
    write_atomic,
)
from sepsim.run import MANIFEST_NAME

__all__ = ["A2_PS_TO_CM2_S", "_f", "_json", "_pm"]  # re-exported (sepsim.reporting, units)

VERSION = 1
MD_NAME, JSON_NAME = "results.md", "results.json"
HOLD_SKIP = 0.10  # fraction of a hold's thermo rows dropped as equilibration
STEP_SKIP = 0.50  # steps: second half, as in `sepsim progress`
MAX_FRAMES = 500  # hold frames (evenly spaced) for the C_n plateau
FIT_WINDOWS_C = ((25.0, 160.0), (25.0, 90.0), (90.0, 160.0))
D_MIN_SLOPE = 0.9  # diffusive regime: local d ln MSD / d ln t >= this ...
D_MIN_SPAN = 2.0  # ... from t_start to the longest lag, with t_end / t_start >= this


class AnalyzeError(ValueError):
    """The run directory cannot be analysed (no deck, not a sweep, no log)."""


def out_dir_for(run_dir: Path, system: str, out: str | Path | None) -> Path:
    """``out`` if given, else ``results/analysis/<system>/<stage>/`` under the cwd."""
    if out is not None:
        return Path(out)
    return Path("results") / "analysis" / system / Path(run_dir).resolve().name


# --------------------------------------------------------------------------- thermo


def segment_thermo(segments, log, notes: list[str] | None = None) -> list[dict | None]:
    """Thermo of every segment (its chunk blocks concatenated) once all its runs are
    complete, else None; blocks are assigned in deck order as in `sepsim progress`
    (:func:`sepsim.progress.runs_by_segment`, whose plan-mismatch notes go to ``notes``)."""
    per_seg, mismatch = runs_by_segment(segments, log)
    if notes is not None:
        notes += mismatch
    out = []
    for seg, mine in zip(segments, per_seg, strict=True):
        done = len(mine) == len(seg.run_steps) and all(r.complete for r in mine)
        out.append(_concat_thermo(mine) if done and seg.command == "run" else None)
    return out


class Window:
    """A series' analysis window ``w`` (rows after the first ``skip`` fraction) with its
    :func:`timeseries_mean` (``tm``) and halves drift test (``halves``), D55 block means
    of ``block`` rows, each computed at most once; callers test ``len(w)`` and ``ptp``
    (the window's range) before using them."""

    def __init__(self, x, skip: float, block: int | None):
        x = np.asarray(x, dtype=float)
        self.w, self.block = x[int(np.floor(skip * len(x))) :], block
        self.ptp = np.ptp(self.w) if len(self.w) else 0.0

    @cached_property
    def tm(self):
        return timeseries_mean(self.w, block=self.block)

    @cached_property
    def halves(self) -> tuple | None:
        """:func:`sepsim.analysis.chain.drift_check` (mean_1, mean_2, delta, delta_sem,
        drift), None for a degenerate (zero-variance) half."""
        from sepsim.analysis.chain import drift_check

        try:
            return drift_check(self.w, block=self.block)
        except DegenerateSeries:
            return None

    def mean_sem(self) -> dict | None:
        """The window's mean +- SEM dict as :func:`sepsim.progress._mean_sem` gives it."""
        if len(self.w) < 3:
            return None
        if self.ptp == 0.0:  # NVT/NVE density: constant, no statistical inefficiency
            return {"mean": float(self.w[0]), "sem": 0.0}
        return _ms_of(self.tm, len(self.w), self.block)


class SegmentWindows:
    """The :class:`Window` of each series of one segment (same ``skip`` and ``block``),
    keyed by the series array, so the segment stats, drift flags, block check and
    convergence record share one mean +- SEM and halves test per series."""

    def __init__(self, skip: float, block: int | None):
        self.skip, self.block = skip, block
        self._by_id: dict[int, tuple] = {}

    def __call__(self, x) -> Window:
        hit = self._by_id.get(id(x))
        if hit is None or hit[0] is not x:
            hit = (x, Window(x, self.skip, self.block))  # holds x: its id stays unique
            self._by_id[id(x)] = hit
        return hit[1]


def window_stats(thermo: dict, skip: float, windows: SegmentWindows | None = None) -> dict:
    """Mean +- SEM of T (C), density, enthalpy and volume over the rows after the first
    ``skip`` fraction; also the window's row count and length (ps, from Time).
    ``windows``: the segment's shared windows (default: new ones, D55 block means)."""
    windows = windows or SegmentWindows(skip, _block_rows(thermo))
    n = len(thermo.get("Step", ()))
    k = int(np.floor(skip * n))
    out: dict = {"rows": n, "rows_used": n - k}
    if "Time" in thermo and n - k >= 2:
        out["window_ps"] = float((thermo["Time"][-1] - thermo["Time"][k]) / 1000.0)
    for key, col, shift in (
        ("t_c", "Temp", -273.15),
        ("density", "Density", 0.0),
        ("enthalpy", "Enthalpy", 0.0),
        ("volume", "Volume", 0.0),
    ):
        if col in thermo:
            ms = windows(thermo[col]).mean_sem()  # D55 block means
            if ms is not None:
                ms["mean"] += shift
            out[key] = ms
    if out.get("enthalpy"):  # D55: SEM from E + p_ext V
        out["enthalpy"] = _enthalpy_mean_sem(thermo, slice(k, None), out["enthalpy"])
    return out


def kappa_t(thermo: dict, t_k: float, skip: float) -> dict | None:
    """Isothermal compressibility (1/GPa) from the Volume column after ``skip``, its SEM
    from 100 ps block means of (V - <V>)^2 (D55, as the other thermo SEMs) with
    ``sem_lower_bound`` as :func:`sepsim.progress._mean_sem` sets it."""
    from sepsim.analysis.thermo import isothermal_compressibility

    v = thermo.get("Volume")
    if v is None:
        return None
    v = v[int(np.floor(skip * len(v))) :]
    if len(v) < 3 or np.ptp(v) == 0:
        return None
    block = _block_rows(thermo)
    c = isothermal_compressibility(v, t_k, block=block)
    return {
        "kappa_T_GPa": c.kappa_T,
        "sem": c.kappa_T_sem,
        "sem_lower_bound": bool(c.lower_bound or len(v) < SEM_RESOLVE_BLOCKS * block),
        "V_mean_A3": c.V_mean,
        "V_std_A3": c.V_std,
        "g": c.g,
        "samples": c.n_samples,
    }


def fit_points(rows: list[dict]) -> list[dict]:
    """One point per set temperature: the latest completed MD segment (so a hold wins
    over the step before it at the same T), sorted by T."""
    pts: dict[float, dict] = {}
    for r in rows:
        st = r.get("stats") or {}
        if st.get("volume") and st.get("enthalpy"):
            pts[round(r["t_set_c"], 3)] = r
    return [pts[t] for t in sorted(pts)]


def sweep_fits(points: list[dict], mass_gmol: float) -> dict:
    """alpha_V (thermal_expansion on V(T)) and classical Cp (heat_capacity_classical on
    H(T)) per window of FIT_WINDOWS_C, SEM-weighted linear fits in T (K); also each
    fit's line (slope, intercept vs T in K) for the plots."""
    from sepsim.analysis.thermo import heat_capacity_classical, thermal_expansion

    t = np.array([p["t_set_c"] + 273.15 for p in points])
    v = np.array([p["stats"]["volume"]["mean"] for p in points])
    v_err = np.array([p["stats"]["volume"]["sem"] for p in points])
    h = np.array([p["stats"]["enthalpy"]["mean"] for p in points])
    h_err = np.array([p["stats"]["enthalpy"]["sem"] for p in points])
    v_err, h_err = _floor_err(v_err), _floor_err(h_err)
    out = {"alpha_V": [], "cp": [], "notes": []}
    for lo, hi in FIT_WINDOWS_C:
        win = fit_window_k(lo, hi)
        sel = (t >= win[0]) & (t <= win[1])
        if sel.sum() < 3:
            out["notes"].append(f"{lo:g}-{hi:g} C: fewer than 3 temperatures, no fit")
            continue
        te = thermal_expansion(t, v, v_err, T_window=win)
        cp = heat_capacity_classical(t, h, mass_gmol, h_err, T_window=win)
        chi_v, scale_v = fit_quality(t[sel], v[sel], v_err[sel], te.line)
        chi_h, scale_h = fit_quality(t[sel], h[sel], h_err[sel], cp.line)
        out["alpha_V"].append(
            {
                "window_c": [lo, hi],
                "alpha_V_per_K": te.alpha_V,
                "err": te.alpha_V_err * scale_v,
                "err_unscaled": te.alpha_V_err,
                "alpha_L_per_K": te.alpha_L,
                "V_mean_A3": te.V_mean,
                "n": te.n_points,
                "line": list(te.line),
                "chi2_red": chi_v,
            }
        )
        out["cp"].append(
            {
                "window_c": [lo, hi],
                "cp_J_gK": cp.cp_JgK,
                "err": cp.cp_JgK_err * scale_h,
                "err_unscaled": cp.cp_JgK_err,
                "cp_kcal_molK": cp.cp_kcalmolK,
                "n": cp.n_points,
                "line": list(cp.line),
                "chi2_red": chi_h,
            }
        )
    return out


def fit_window_k(lo_c: float, hi_c: float) -> tuple[float, float]:
    """A FIT_WINDOWS_C window in K, widened by T_MATCH_TOL (its set points included)."""
    return (lo_c + 273.15 - T_MATCH_TOL, hi_c + 273.15 + T_MATCH_TOL)


def fit_quality(x, y, s, line) -> tuple[float | None, float]:
    """Reduced chi^2 of a SEM-weighted line fit (slope, intercept) to y +- s and the
    error scale :func:`_birge` of it; the one fit-quality step of the sweep, gamma and
    pore thermal fits."""
    chi = _chi2_red(x, y, s, *line)
    return chi, _birge(chi)


def _floor_err(err: np.ndarray) -> np.ndarray:
    """SEMs as fit weights: a zero SEM (e.g. too few rows) gets the smallest positive one."""
    pos = err[err > 0]
    return np.where(err > 0, err, pos.min() if len(pos) else 1.0)


def _birge(chi2_red: float | None) -> float:
    """Error scale factor max(1, sqrt(chi2_red)) (Birge ratio): a fit worse than its
    SEM weights allow gets its parameter errors inflated, never deflated."""
    return 1.0 if chi2_red is None else max(1.0, float(np.sqrt(chi2_red)))


def _chi2_red(x, y, s, slope, intercept) -> float | None:
    if len(x) <= 2:
        return None
    return float(np.sum(((y - (slope * x + intercept)) / s) ** 2) / (len(x) - 2))


# --------------------------------------------------------------------------- equilibration

EQ_BLOCKS = 8  # block averages per segment in the equilibration plots
EQ_POINTS = 500  # points per series and segment kept in results.json "convergence"
CONV_BLOCKS = (32, 16, 8)  # block counts of the block-average SEM check


def drift_flags(
    series: dict, skip: float, block: int | None = None, windows: SegmentWindows | None = None
) -> dict:
    """Halves of the analysis window (rows after ``skip``) compared per named series:
    :func:`sepsim.analysis.chain.drift_check` (mean difference > 2 combined SEM).
    ``windows``: the segment's shared windows (default: new ones with ``block``)."""
    windows = windows or SegmentWindows(skip, block)
    out = {}
    for name, x in series.items():
        win = windows(x)
        if len(win.w) < MIN_DRIFT_ROWS or win.ptp == 0 or win.halves is None:
            continue
        a, b, delta, sem, drift = win.halves
        out[name] = {"first": a, "second": b, "delta": delta, "sem": sem, "drift": drift}
    return out


def block_averages(t, x, n_blocks: int = EQ_BLOCKS) -> list[dict]:
    """Mean +- SEM (statistical inefficiency) of ``n_blocks`` equal blocks of a series,
    with each block's mid time."""
    t, x = np.asarray(t, dtype=float), np.asarray(x, dtype=float)
    out = []
    for idx in np.array_split(np.arange(len(x)), n_blocks):
        if len(idx) >= 3:
            ms = _mean_sem(x[idx])
            out.append({"t": float(t[idx].mean()), "mean": ms["mean"], "sem": ms["sem"]})
    return out


def block_mean_sem(w, n_blocks: int) -> float:
    """SEM of the mean of ``w`` from the means of ``n_blocks`` equal blocks (the
    block-average check, :func:`block_convergence` and :func:`sem_vs_block`)."""
    means = np.array([b.mean() for b in np.array_split(w, n_blocks)])
    return float(means.std(ddof=1) / np.sqrt(n_blocks))


def block_convergence(
    x, skip: float, block: int | None = None, windows: SegmentWindows | None = None
) -> dict | None:
    """Block-average check of the window's SEM: the SEM from the statistical inefficiency
    (D26) vs the SEM of the means of ``CONV_BLOCKS`` blocks; once blocks are longer than
    the correlation time the block SEM plateaus at the statistical-inefficiency value.
    ``converged``: the 8-block SEM is within a factor 2 of it."""
    win = (windows or SegmentWindows(skip, block))(x)
    w, ms = win.w, win.mean_sem()
    if ms is None or not ms["sem"]:
        return None
    blocks = {str(nb): block_mean_sem(w, nb) for nb in CONV_BLOCKS if len(w) >= 3 * nb}
    last = blocks.get(str(CONV_BLOCKS[-1]))
    return {
        "sem": ms["sem"],
        "block_sem": blocks,
        "converged": None if last is None else bool(last <= 2.0 * ms["sem"]),
    }


def quantity_convergence(
    t_ps, x, skip: float, block: int | None = None, windows: SegmentWindows | None = None
) -> dict:
    """Convergence record of one series over a segment (``results.json`` ``convergence``):
    the series thinned to <= ``EQ_POINTS`` points (t_ps, value), ``EQ_BLOCKS`` block
    averages over the whole segment, and over the analysis window (after ``skip``) the
    mean +- SEM, statistical inefficiency g, and the halves test (second - first half,
    combined SEM, their ratio z, drift if |z| > 2). ``windows``: the segment's shared
    windows, used when their skip and block match."""
    t = np.asarray(t_ps, dtype=float)
    if block is None and len(t) >= 2:  # D55: 100 ps block means for thermo series
        block = _block_rows({"Time": t * 1000.0})
    same = windows is not None and (windows.skip, windows.block) == (skip, block)
    win = windows(x) if same else Window(x, skip, block)
    x, w = np.asarray(x, dtype=float), win.w
    step = max(1, -(-len(x) // EQ_POINTS))
    out: dict = {
        "t_ps": _round(t[::step]),
        "value": _round(x[::step], 8),
        "blocks": block_averages(t, x),
        "mean": float(w.mean()) if len(w) else None,
        "sem": None,
        "g": None,
        "halves": None,
        "drift": None,
    }
    if len(w) >= 3 and win.ptp > 0:
        out.update(sem=win.tm.sem, g=win.tm.g)
        if len(w) >= MIN_DRIFT_ROWS and win.halves is not None:
            _, _, delta, sem, drift = win.halves
            out.update(
                halves={"delta": delta, "sem": sem, "z": delta / sem if sem else None},
                drift=drift,
            )
    elif len(w):
        out.update(sem=0.0, g=1.0)
    return out


SEM_BLOCKS = (128, 64, 32, 16, 8, 4)  # block counts of the SEM-vs-block-size curve


def sem_vs_block(t_ps, x, skip: float) -> list[dict]:
    """SEM of the window mean from the means of n blocks, for n in ``SEM_BLOCKS`` (>= 3
    rows per block), vs the block length; plateaus at the statistical-inefficiency SEM
    once blocks outlast the correlation time."""
    t, x = np.asarray(t_ps, dtype=float), np.asarray(x, dtype=float)
    k = int(np.floor(skip * len(x)))
    w, tw = x[k:], t[k:]
    dt = float(np.median(np.diff(tw))) if len(tw) > 1 else 0.0
    return [
        {"n_blocks": nb, "block_ps": len(w) // nb * dt, "sem": block_mean_sem(w, nb)}
        for nb in SEM_BLOCKS
        if len(w) >= 3 * nb
    ]


def segment_convergence(
    name: str,
    kind: str,
    thermo: dict,
    skip: float,
    cols: dict,
    windows: SegmentWindows | None = None,
) -> dict:
    """``results.json`` ``convergence`` entry of one segment: name, kind, start/end time
    and analysis window (ps), :func:`quantity_convergence` per series in ``cols``, and for
    holds the :func:`sem_vs_block` curve per series. ``windows``: the segment's shared
    windows."""
    t = np.asarray(thermo["Time"], dtype=float) / 1000.0  # fs -> ps
    k = int(np.floor(skip * len(t)))
    out = {
        "name": name,
        "kind": kind,
        "t_start_ps": float(t[0]),
        "t_end_ps": float(t[-1]),
        "window": [float(t[k]), float(t[-1])],
        "skip": skip,
        "quantities": {
            q: quantity_convergence(t, x, skip, windows=windows) for q, x in cols.items()
        },
    }
    if kind == "hold":
        out["sem_vs_block"] = {q: sem_vs_block(t, x, skip) for q, x in cols.items()}
    return out


def drift_cell(row: dict) -> str:
    """results.md drift column: the quantities whose window drifts, else blank."""
    return ", ".join(q for q, d in (row.get("drift") or {}).items() if d["drift"])


def equilibration_markdown(r: dict, local: str, chain_scale: str) -> list[str]:
    """The results.md "Equilibration" section shared by the sweep and pore analyses:
    windows, segments whose window drifts, the block-average SEM check of the holds, and
    local vs chain-scale quantities (chain COM MSD over <Rg^2> per hold)."""
    m = r["method"]
    lines = [
        "",
        "## Equilibration",
        "",
        (
            f"Every average uses only the analysis window: steps {m['step_window']}, holds"
            f" {m['hold_window']} (the rest is equilibration after the T change; see"
            " `equilibration.png`, windows shaded, block averages ± SEM overlaid, and"
            " `equilibration_holds.png`). Drift: the window's two halves differ by > 2"
            " combined SEM (statistical inefficiency)."
        ),
        "",
    ]
    flagged = []
    for s in r["segments"]:
        bad = [
            f"{q} {d['delta']:+.4g} ± {d['sem']:.2g}"
            for q, d in (s.get("drift") or {}).items()
            if d["drift"]
        ]
        if bad:
            flagged.append(f"| {s['name']} | {s['t_set_c']:.4g} | {'; '.join(bad)} |")
    tested = sorted({q for s in r["segments"] for q in (s.get("drift") or {})})
    if flagged:
        lines += [
            f"Segments with a drifting window (tested: {', '.join(tested)}):",
            "",
            "| segment | T set (°C) | drift (second − first half ± SEM) |",
            "|---|---|---|",
            *flagged,
        ]
    else:
        lines.append(f"No segment window drifts (tested: {', '.join(tested) or 'none'}).")
    conv = [s for s in r["segments"] if s.get("convergence")]
    if conv:
        lines += [
            "",
            (
                "Block-average check of the hold SEMs: SEM of the means of 32 / 16 / 8 blocks vs"
                " the statistical-inefficiency SEM (blocks longer than the correlation time"
                " plateau at it; flagged if the 8-block SEM exceeds it by > 2×)."
            ),
            "",
            "| T (°C) | quantity | SEM (g) | block SEM 32 / 16 / 8 | converged |",
            "|---|---|---|---|---|",
        ]
        for s in conv:
            for q, c in s["convergence"].items():
                if not c:
                    continue
                b = " / ".join(
                    f"{c['block_sem'].get(k, float('nan')):.3g}" for k in ("32", "16", "8")
                )
                ok = {True: "yes", False: "**no**", None: "n/a"}[c["converged"]]
                lines.append(f"| {s['t_set_c']:g} | {q} | {c['sem']:.3g} | {b} | {ok} |")
    lines += ["", local, "", chain_scale]
    for h in r.get("holds", []):
        tr = h.get("film") or h.get("traj") or {}
        if not tr.get("available") or "com_msd" not in tr:
            continue
        ratio = tr["com_msd"]["msd_at_max_A2"] / tr["rg"]["rg2_A2"]["mean"]
        verdict = (
            "chains have moved about their own size"
            if ratio >= 1
            else "chains have **not** moved their own size: chain-scale averages sample a"
            " partly relaxed set of chain configurations"
        )
        lines.append(
            f"- {h['t_c']:g} °C: chain COM MSD at {tr['com_msd']['lag_max_ps'] / 1000:g} ns"
            f" / ⟨Rg²⟩ = {ratio:.2f}; {verdict}."
        )
    return lines


# --------------------------------------------------------------------------- trajectories


def read_frames(path: Path, sys_arr: dict) -> dict:
    """Backbone positions (float32), chain COMs and Rg^2 of every frame of a DCD, with
    the system's mass centre removed per frame (box drift does not count)."""
    from MDAnalysis.coordinates.DCD import DCDReader

    from sepsim.analysis.chain import chain_com_rg2

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        reader = DCDReader(str(path))
    try:
        if reader.n_atoms != sys_arr["n_atoms"]:
            raise ValueError(
                f"{path.name}: {reader.n_atoms} atoms, data.lmp has {sys_arr['n_atoms']}"
            )
        bb, com, rg2, box = [], [], [], []
        for ts in reader:
            x = ts.positions.astype(float)
            c, g = chain_com_rg2(x, sys_arr["molecule"], sys_arr["masses"])
            bb.append(x[sys_arr["bb_rows"]].astype(np.float32))
            com.append(c[0])
            rg2.append(g[0])
            box.append(ts.dimensions if ts.dimensions is not None else np.full(6, np.nan))
    finally:
        reader.close()
    if not bb:
        raise ValueError(f"{path.name}: no frames")
    com, bb = np.array(com), np.array(bb)
    w = sys_arr["mol_mass"]
    origin = (com * w[None, :, None]).sum(axis=1) / w.sum()
    return {
        "bb": bb - origin[:, None, :].astype(np.float32),
        "com": com - origin[:, None, :],
        "rg2": np.array(rg2),
        "box": np.array(box, dtype=float),  # MDAnalysis [lx, ly, lz, alpha, beta, gamma]
    }


def concat_frames(parts: list[dict]) -> tuple[dict, list[int]]:
    """Frames of consecutive DCDs of one continuous run (:func:`read_frames` outputs) as
    one trajectory; a part's first frame is dropped when it repeats the previous part's
    last frame (a run continued from a write_data of its last step), as in
    :func:`sepsim.progress.hold_chain_checks`. Returns (frames, frames taken per part)."""
    from sepsim.analysis.chain import repeats_frame

    keep, taken = [], []
    for k, p in enumerate(parts):
        start = 0
        if k and repeats_frame(p["bb"][0], parts[k - 1]["bb"][-1]):
            start = 1
        keep.append(start)
        taken.append(len(p["bb"]) - start)
    out = {
        key: np.concatenate([p[key][s:] for p, s in zip(parts, keep, strict=True)])
        for key in parts[0]
    }
    return out, taken


def _bond_vectors(bb: np.ndarray, chains: list[np.ndarray]) -> np.ndarray:
    """Backbone bond vectors (n_frames, n_bonds, 3) of every chain's consecutive sites."""
    from sepsim.analysis.chain import bond_pairs

    a, b = bond_pairs(chains)
    return bb[:, b] - bb[:, a]


def _frame_mean_sem(x) -> dict:
    """Mean +- SEM (plain statistical inefficiency, no block means) of a per-frame
    series; SEM None for fewer than 3 frames."""
    ms = _mean_sem(x)
    if ms is None:
        x = np.asarray(x, dtype=float)
        return {"mean": float(x.mean()), "sem": None}
    return ms


def _root(ms: dict) -> dict:
    """<x>^1/2 with SEM / (2 <x>^1/2)."""
    r = float(np.sqrt(ms["mean"]))
    return {"mean": r, "sem": None if ms["sem"] is None else ms["sem"] / (2 * r)}


def hold_trajectory(
    run_dir: Path, seg, sys_arr: dict, max_frames: int = MAX_FRAMES, before=()
) -> dict:
    """Mobility, chain-size and chain-relaxation results of one hold (a
    :class:`sepsim.progress.Segment`) from its DCD and burst DCDs. ``before``: DCDs of
    the same continuous run read ahead of the hold DCD as one trajectory (an extension
    after the prep hold, D47/D56), all with the hold's frame interval."""
    names = list(zip(seg.dcd, seg.dump_every, strict=True))
    hold = [(f, n) for f, n in names if "_burst" not in f]
    bursts = [(f, n) for f, n in names if "_burst" in f]
    out: dict = {"available": False, "notes": []}
    if not hold or not (run_dir / hold[0][0]).is_file():
        name = hold[0][0] if hold else "hold DCD"
        out["notes"].append(f"trajectory not available ({name} not found)")
        return out
    dcd, every = hold[0]
    frame_ps = every * seg.dt_fs / 1000.0
    tr = _hold_frames(run_dir / dcd, sys_arr, before, frame_ps, out)
    nf = len(tr["bb"])
    if nf < MIN_HOLD_FRAMES:
        out["notes"].append(f"trajectory not available ({dcd}: only {nf} frames)")
        return out
    out.update(
        available=True, dcd=dcd, frames=nf, frame_ps=frame_ps, hold_ns=(nf - 1) * frame_ps / 1000
    )
    curves, used = _mobility_curves(run_dir, tr, bursts, seg.dt_fs, sys_arr, frame_ps, out["notes"])
    out["bursts"] = {"listed": len(bursts), "used": used}
    cg = sys_arr["manifest"]["resolution"] == "cg"
    out.update(_mobility_results(curves, float(tr["rg2"].mean()), cg))
    size, size_curves = _hold_chain_size(tr, sys_arr, frame_ps, max_frames)
    out.update(size)
    (lm, vm, sm), (lc, vc, _), (lp, vp, _) = curves["msd"], curves["com"], curves["p2"]
    out["curves"] = {
        "msd_lag_ps": _round(_log_thin(lm)),
        "msd_A2": _round(vm[_log_idx(lm)]),
        "msd_src": sm[_log_idx(lm)].tolist(),
        "com_lag_ps": _round(_log_thin(lc)),
        "com_A2": _round(vc[_log_idx(lc)]),
        "p2_lag_ps": _round(_log_thin(lp)),
        "p2": _round(vp[_log_idx(lp)]),
        **size_curves,
    }
    return out


def _hold_frames(path: Path, sys_arr: dict, before, frame_ps: float, out: dict) -> dict:
    """:func:`read_frames` of the hold DCD ``path``, with the ``before`` DCDs read ahead
    of it as one trajectory (:func:`concat_frames`; their parts and boundaries go to
    ``out``)."""
    tr = read_frames(path, sys_arr)
    if before:
        names_all = [Path(b) for b in before] + [path]
        tr, taken = concat_frames([read_frames(Path(b), sys_arr) for b in before] + [tr])
        starts = np.cumsum(taken)[:-1]
        out["parts"] = [
            {"file": str(f), "frames": n} for f, n in zip(names_all, taken, strict=True)
        ]
        out["boundaries_ps"] = [float((k - 0.5) * frame_ps) for k in starts]
    return tr


def _mobility_curves(run_dir: Path, tr: dict, bursts, dt_fs: float, sys_arr, frame_ps, notes):
    """Backbone-site MSD, chain COM MSD and bond P2 ACF of a hold: the hold frames for
    lags up to half the hold, stitched with the D46 burst DCDs (0.1 ps frames over 10 ps)
    below the hold frame interval. Returns ({"msd", "com", "p2"}: (lags, values, source)
    each, bursts used); burst problems go to ``notes``."""
    from sepsim.analysis.mobility import (
        average_curves,
        mean_over_batches,
        msd,
        p2_autocorrelation,
        stitch_curves,
    )

    chains = sys_arr["chains"]
    lag_max = len(tr["bb"]) // 2
    lags_h, msd_h = mean_over_batches(msd, tr["bb"], frame_ps, lag_max)
    _, com_h = msd(tr["com"], frame_ps, lag_max)
    vec = _bond_vectors(tr["bb"], chains)
    _, p2_h = mean_over_batches(p2_autocorrelation, vec, frame_ps, lag_max)
    del vec

    # bursts: 0.1 ps frames over 10 ps (D46)
    b_msd, b_com, b_p2, used = [], [], [], []
    for f, n in bursts:
        path = run_dir / f
        if not path.is_file():
            continue
        try:
            b = read_frames(path, sys_arr)
        except (OSError, ValueError) as exc:
            notes.append(f"{f} skipped: {exc}")
            continue
        m = len(b["bb"])
        if m < 3:
            continue
        b_ps = n * dt_fs / 1000.0
        lb, mb = mean_over_batches(msd, b["bb"], b_ps, m - 1)
        b_msd.append((lb, mb, m))
        b_com.append((*msd(b["com"], b_ps, m - 1), m))
        _, pb = mean_over_batches(p2_autocorrelation, _bond_vectors(b["bb"], chains), b_ps, m - 1)
        b_p2.append((lb, pb, m))
        used.append(f)
    if bursts and not used:
        notes.append(f"burst DCDs not found ({len(bursts)} listed in the deck)")
    elif not bursts:
        notes.append("no burst DCDs (deck without D46 bursts): lags from the hold DCD only")

    def combine(burst_curves, lags, vals):
        if not burst_curves:
            return lags, vals, np.ones(len(lags), int)
        bl, bv = average_curves(burst_curves)
        return stitch_curves(bl, bv, lags, vals)

    curves = {
        "msd": combine(b_msd, lags_h, msd_h),
        "com": combine(b_com, lags_h, com_h),
        "p2": combine(b_p2, lags_h, p2_h),
    }
    return curves, len(used)


def _mobility_results(curves: dict, rg2_mean: float, cg: bool) -> dict:
    """The ``segment_msd``, ``com_msd`` (D_COM by the D49/D55 criterion) and ``p2``
    entries of a hold from its :func:`_mobility_curves`."""
    from sepsim.analysis.chain import decorrelation_time
    from sepsim.analysis.mobility import diffusion_coefficient

    (lm, vm, _), (lc, vc, _), (lp, vp, _) = curves["msd"], curves["com"], curves["p2"]
    fit = diffusion_coefficient(lc, vc, D_MIN_SLOPE, D_MIN_SPAN, rg2=rg2_mean)
    com = {
        "lag_max_ps": float(lc[-1]),
        "msd_at_max_A2": float(vc[-1]),
        "diffusive": fit.diffusive,
        "slope_end": fit.slope_end,
        "slope_max": fit.slope_max,
        "msd_rg2_end": fit.msd_rg2_end,
    }
    if fit.diffusive:
        com.update(
            D_cm2_s=fit.D * A2_PS_TO_CM2_S,
            D_err_cm2_s=fit.D_err * A2_PS_TO_CM2_S,
            fit_ps=[fit.t_start, fit.t_end],
            t_start_ps=fit.t_start,
            t_end_ps=fit.t_end,
        )
    seg_msd = {"lag_max_ps": float(lm[-1]), "msd_at_max_A2": float(vm[-1])}
    for lag in (1.0, 10.0, 1000.0):
        k = np.flatnonzero(np.isclose(lm, lag, rtol=1e-6))
        if len(k):
            seg_msd[f"msd_{lag:g}ps_A2"] = float(vm[k[0]])
    p2 = {
        "t_1e_ps": decorrelation_time(lp, vp),
        "lag_max_ps": float(lp[-1]),
        "at_max": float(vp[-1]),
        "vectors": "bead-bead bonds" if cg else "backbone C-C bonds",
    }
    return {"segment_msd": seg_msd, "com_msd": com, "p2": p2}


def _hold_chain_size(tr: dict, sys_arr: dict, frame_ps: float, max_frames: int):
    """Chain size over a hold (``rg``, ``ree``, ``c_n`` with block series), the D56
    ``relaxation`` and the ``crystallinity`` monitor; also their plot curves."""
    chains, man = sys_arr["chains"], sys_arr["manifest"]
    nf = len(tr["bb"])
    rg2 = _frame_mean_sem(tr["rg2"].mean(axis=1))
    ree = _end_to_end(tr["bb"], chains)
    ree2_t = np.sum(ree**2, axis=2).mean(axis=1)
    ree2 = _frame_mean_sem(ree2_t)
    t_ps = np.arange(nf) * frame_ps
    relax, relax_curves = chain_relaxation(ree, tr["bb"], chains, frame_ps, nf // 2)
    pick = np.unique(np.linspace(0, nf - 1, min(nf, max_frames)).round().astype(int))
    nc, cn, cn_t = _cn_frames(tr["bb"][pick], chains, man)
    block = {
        "rg": {
            "rg2_A2": rg2,
            "rg_A": _root(rg2),
            "series": block_series(t_ps, tr["rg2"].mean(axis=1), "rg2_A2"),
        },
        "ree": {
            "ree2_A2": ree2,
            "ree_A": _root(ree2),
            "series": block_series(t_ps, ree2_t, "ree2_A2"),
        },
        "c_n": {
            "plateau": None if cn_t is None else _frame_mean_sem(cn_t),
            "frames": len(pick),
            "n_min": CN_N_MIN,
            "bond_length": CG_CC_BOND_A if man["resolution"] == "cg" else None,
            "series": None if cn_t is None else block_series(t_ps[pick], cn_t, "plateau"),
        },
        "relaxation": relax,
        "crystallinity": _crystallinity(tr, chains, man),
    }
    curves = {"cn_n": nc.tolist(), "cn": _round(cn.mean(axis=0)), **relax_curves}
    return block, curves


def _end_to_end(bb: np.ndarray, chains) -> np.ndarray:
    """End-to-end vectors (n_frames, n_chains, 3; last minus first backbone site)."""
    first = np.array([c[0] for c in chains])
    last = np.array([c[-1] for c in chains])
    return bb[:, last].astype(float) - bb[:, first]


def _cn_frames(bb: np.ndarray, chains, manifest: dict):
    """Per-frame C_n of backbone frames ``bb`` (CG: carbon-equivalent n and the C-C bond,
    D37): (carbons n, C_n per frame, plateau over n >= CN_N_MIN per frame or None)."""
    from sepsim.analysis.chain import CARBONS_PER_SITE, characteristic_ratio

    res = manifest["resolution"]
    nc, cn = characteristic_ratio(
        bb.astype(float),
        chains,
        carbons_per_site=CARBONS_PER_SITE[res],
        bond_length=CG_CC_BOND_A if res == "cg" else None,
        per_frame=True,
    )
    sel = nc >= CN_N_MIN
    return nc, cn, (cn[:, sel].mean(axis=1) if sel.any() else None)


def _crystallinity(tr: dict, chains, manifest: dict) -> dict:
    """:func:`crystallinity_monitor`, or a note when it cannot be computed."""
    try:
        return crystallinity_monitor(tr, chains, manifest)
    except (ValueError, KeyError, OSError) as exc:
        return {"available": False, "note": f"crystallinity not computed: {exc}"}


def step_static(run_dir: Path, seg, sys_arr: dict, skip: float = STEP_SKIP) -> dict:
    """Static chain properties of one sweep step (a :class:`sepsim.progress.Segment`) from
    its DCD over the step's analysis window (frames after ``skip``, the second half as for
    its thermo stats): <Rg^2>^1/2, <R_ee^2>^1/2 and the C_n plateau (n >= 100 carbons) with
    SEMs from the statistical inefficiency of the per-frame values, and the crystallinity
    monitor. No MSD / ACF / relaxation: a 5 ns step is too short for them."""
    files = [f for f in seg.dcd if "_burst" not in f]
    out: dict = {"available": False, "notes": []}
    if not files or not (run_dir / files[0]).is_file():
        out["notes"].append(
            f"trajectory not available ({files[0] if files else 'step DCD'} not found)"
        )
        return out
    dcd = files[0]
    frame_ps = seg.dump_every[seg.dcd.index(dcd)] * seg.dt_fs / 1000.0
    tr = read_frames(run_dir / dcd, sys_arr)
    n_all = len(tr["bb"])
    k0 = int(np.floor(skip * n_all))
    tr = {k: v[k0:] for k, v in tr.items()}
    nf = len(tr["bb"])
    if nf < 3:
        out["notes"].append(f"trajectory not available ({dcd}: only {nf} frames in the window)")
        return out
    chains, man = sys_arr["chains"], sys_arr["manifest"]
    ree = _end_to_end(tr["bb"], chains)
    rg2 = _frame_mean_sem(tr["rg2"].mean(axis=1))
    ree2 = _frame_mean_sem(np.sum(ree**2, axis=2).mean(axis=1))
    _, _, cn_t = _cn_frames(tr["bb"], chains, man)
    out.update(
        available=True,
        dcd=dcd,
        frames=nf,
        frames_total=n_all,
        frame_ps=frame_ps,
        window_ns=(nf - 1) * frame_ps / 1000,
        rg={"rg2_A2": rg2, "rg_A": _root(rg2)},
        ree={"ree2_A2": ree2, "ree_A": _root(ree2)},
        c_n={
            "plateau": None if cn_t is None else _frame_mean_sem(cn_t),
            "frames": nf,
            "n_min": CN_N_MIN,
            "bond_length": CG_CC_BOND_A if man["resolution"] == "cg" else None,
        },
        crystallinity=_crystallinity(tr, chains, man),
    )
    return out


ROUSE_P_MAX = 5  # Rouse modes p = 1..ROUSE_P_MAX (D56)
SERIES_BLOCKS = 100  # block means per hold in the rg/ree/c_n "series" (D56)


def block_series(t_ps, x, name: str, n_blocks: int = SERIES_BLOCKS) -> dict:
    """<= ``n_blocks`` consecutive block means of a per-frame series with each block's
    mid time (ps from the first hold frame): ``{"t_ps": [...], name: [...]}``."""
    t, x = np.asarray(t_ps, dtype=float), np.asarray(x, dtype=float)
    idx = [b for b in np.array_split(np.arange(len(x)), min(n_blocks, len(x))) if len(b)]
    return {
        "t_ps": _round([t[b].mean() for b in idx]),
        name: _round([x[b].mean() for b in idx], 8),
        "frames_per_block": int(len(x) // max(1, len(idx))),
    }


def chain_relaxation(ree, bb, chains, frame_ps: float, lag_max: int, p_max: int = ROUSE_P_MAX):
    """D56 relaxation block of a hold: the end-to-end vector ACF and the Rouse mode ACFs
    (p = 1..p_max) over lags up to ``lag_max`` frames, each with its 1/e time and an
    exponential fit (:func:`sepsim.analysis.chain.relaxation_time`), the mode amplitudes
    <X_p^2> and p^2 <X_p^2> (flat for an ideal Rouse chain), and tau_1 estimated as
    p^2 tau_p from every mode whose 1/e time is reached. Returns (block, plot curves)."""
    from sepsim.analysis.chain import (
        end_to_end_autocorrelation,
        mode_autocorrelation,
        relaxation_time,
        rouse_modes,
    )

    lags, c_ee = end_to_end_autocorrelation(ree, frame_ps, lag_max)
    ee = relaxation_time(lags, c_ee)
    lags_p, c_p, amp, p2_amp = mode_autocorrelation(
        rouse_modes(bb, chains, p_max), frame_ps, lag_max
    )
    rouse = []
    for k in range(p_max):
        rt = relaxation_time(lags_p, c_p[k])
        rouse.append(
            {
                "p": k + 1,
                "amp_A2": float(amp[k]),
                "p2_amp_A2": float(p2_amp[k]),
                "t_1e_ps": rt["t_1e"],
                "tau_fit_ps": rt["tau_fit"],
                "reached": rt["reached"],
                "extrapolated": rt["extrapolated"],
                "acf_at_max": rt["acf_at_max"],
            }
        )
    block = {
        "lag_max_ps": float(lags[-1]),
        "ree": {
            "t_1e_ps": ee["t_1e"],
            "tau_fit_ps": ee["tau_fit"],
            "reached": ee["reached"],
            "extrapolated": ee["extrapolated"],
            "acf_at_max": ee["acf_at_max"],
            "fit_ps": ee["fit_t"],
        },
        "rouse": rouse,
        "tau1_from_p": {str(m["p"]): m["p"] ** 2 * m["t_1e_ps"] for m in rouse if m["reached"]},
        "p2_amp_rel": [float(v / p2_amp[0]) for v in p2_amp],
    }
    idx = _log_idx(lags)
    curves = {
        "relax_lag_ps": _round(lags[idx]),
        "ree_acf": _round(c_ee[idx]),
        "rouse_acf": [_round(c[idx]) for c in c_p],
    }
    return block, curves


CRYSTAL_THRESHOLD = 0.4  # D56: fixed p2 threshold, uncalibrated (no crystal reference)
CRYSTAL_FRAMES = 50  # hold frames (evenly spaced) for the crystallinity monitor
CRYSTAL_RC_UA_AA = 6.5  # Angstrom, backbone carbons (UA/AA)
CRYSTAL_LABEL = "uncalibrated, melt baseline"


def crystal_parameters(manifest: dict) -> dict:
    """D56 crystallinity-monitor settings for a system: r_c = 1.4 sigma of the CG
    backbone bead pair (from the force-field YAML named in the manifest) or 6.5 A for
    UA/AA backbone carbons; chord half-span 1 (PE) or 3 (iPP 3_1 helix); l_proj the CG
    backbone bond r0, else 1.27 A (PE) / 1.08 A (iPP) (:func:`sepsim.analysis.order.
    crystallinity`)."""
    import yaml

    from sepsim.ff.params import FORCEFIELD_DIR

    ipp = manifest.get("polymer") == "ipp"
    half_span, l_proj, r_c = (3, 1.08, CRYSTAL_RC_UA_AA) if ipp else (1, 1.27, CRYSTAL_RC_UA_AA)
    if manifest["resolution"] == "cg":
        ff = yaml.safe_load((FORCEFIELD_DIR / manifest["forcefield"]["file"]).read_text())
        bead = "CM"  # the SDK PE backbone bead (CT only at the chain ends)
        pair = next(v for v in ff["pair_types"].values() if v["pattern"] == [bead, bead])
        bond = next(v for v in ff["bond_types"].values() if v["pattern"] == [bead, bead])
        r_c, l_proj = 1.4 * float(pair["sigma"]), float(bond["r0"])
    return {"r_c_A": r_c, "half_span": half_span, "l_proj_A": l_proj}


def crystallinity_monitor(tr: dict, chains, manifest: dict, n_frames: int = CRYSTAL_FRAMES):
    """D56 crystallinity monitor over <= ``n_frames`` evenly spaced hold frames: the
    D26 local-alignment order (:func:`sepsim.analysis.order.crystallinity`) with the
    :func:`crystal_parameters` cutoff and a fixed, uncalibrated threshold p2 >=
    ``CRYSTAL_THRESHOLD`` (no crystal reference: a melt baseline, to confirm the boxes
    stay amorphous). Fraction (mean, SD, first/last frame, max) and largest cluster."""
    from MDAnalysis.lib.mdamath import triclinic_vectors

    from sepsim.analysis.order import crystallinity

    par = crystal_parameters(manifest)
    nf = len(tr["bb"])
    pick = np.unique(np.linspace(0, nf - 1, min(nf, n_frames)).round().astype(int))
    order = np.concatenate(chains)
    chain_id = np.concatenate([np.full(len(c), k) for k, c in enumerate(chains)])
    frac, largest, p2m = [], [], []
    for f in pick:
        box = tr["box"][f]
        if not np.all(np.isfinite(box)):
            raise ValueError("DCD frames carry no box")
        r = crystallinity(
            tr["bb"][f][order].astype(float),
            chain_id,
            triclinic_vectors(box),
            r_c=par["r_c_A"],
            threshold=CRYSTAL_THRESHOLD,
            half_span=par["half_span"],
            l_proj=par["l_proj_A"],
        )
        frac.append(r.fraction)
        largest.append(r.largest_cluster)
        p2m.append(float(np.nanmean(r.p2)))
    frac = np.array(frac)
    return {
        "available": True,
        "label": CRYSTAL_LABEL,
        "threshold": CRYSTAL_THRESHOLD,
        **par,
        "frames": len(pick),
        "sites": len(order),
        "fraction": {"mean": float(frac.mean()), "sd": float(frac.std())},
        "fraction_first": float(frac[0]),
        "fraction_last": float(frac[-1]),
        "fraction_max": float(frac.max()),
        "largest_cluster": {"mean": float(np.mean(largest)), "max": int(np.max(largest))},
        "p2_mean": float(np.mean(p2m)),
    }


def _log_idx(lags, n: int = 300) -> np.ndarray:
    """Indices of up to ``n`` log-spaced positive lags (for log-axis plots)."""
    t = np.asarray(lags, dtype=float)
    pos = np.flatnonzero(t > 0)
    if len(pos) <= n:
        return pos
    grid = np.geomspace(t[pos[0]], t[pos[-1]], n)
    return np.unique(pos[np.searchsorted(t[pos], grid).clip(0, len(pos) - 1)])


def _log_thin(lags) -> np.ndarray:
    return np.asarray(lags, dtype=float)[_log_idx(lags)]


# --------------------------------------------------------------------------- caveats


def chain_relaxation_caveat(run_dir: Path) -> list[str]:
    """Unrelaxed-chain warnings from the source system's extend or prep progress.json:
    D47 (end-to-end ACF < 1/e and COM MSD >= 2 <Rg^2> at half the hold) and D37."""
    parent = Path(run_dir).resolve().parent
    deck = find_deck(Path(run_dir))
    src = _input_stage(deck) or "prep"
    for stage in ("extend", "prep") if src == "cool" else ("prep",):
        rep = load_json(parent / stage / PROGRESS_JSON)
        hold = (rep or {}).get("hold") or {}
        if "ree_acf" not in hold:
            continue
        d = hold.get("d47") or d47_criteria(hold)
        notes = []
        what = "prep hold + extension" if stage == "extend" else "prep 500 K hold"
        if not d["passed"]:
            notes.append(
                f"Chains may not be relaxed: the D47 criteria fail on the {what}"
                f" ({stage}/progress.json: end-to-end ACF {d['acf']:.2f} at"
                f" {d['lag_ns']:.1f} ns, needs < 1/e; COM MSD/<Rg²> {d['ratio']:.2f},"
                " needs >= 2)."
            )
        m = hold.get("msid") or {}
        if m and not m.get("passed"):
            notes.append(
                f"D37 chain check FAIL on the {what}: C_n plateau {m['plateau']:.2f} vs melt"
                f" {m['reference'][0]:g} ±10%" + (" (drift)" if m.get("drift") else "") + "."
            )
        return notes
    return []


def _cp_caveat(resolution: str | None) -> str:
    base = (
        "Cp is the classical dH/dT and is not comparable to experiment: classical MD"
        " gives every degree of freedom k_B/2 per quadratic term"
    )
    if resolution == "aa":
        return base + (
            ", so the stiff C–H/C–C modes that are quantum-frozen at these T make AA Cp"
            " too high; it needs the VDOS quantum correction (D12c), not done here."
        )
    return base + (
        f"; {'CG' if resolution == 'cg' else 'UA'} also drops degrees of freedom"
        f" ({'all motion inside a 3-CH2 bead' if resolution == 'cg' else 'the hydrogens'}),"
        " so its Cp per gram is not a property of the real polymer at all (reported for"
        " completeness and resolution comparisons only)."
    )


# --------------------------------------------------------------------------- report


def analyze_sweep(
    run_dir: str | Path,
    out: str | Path | None = None,
    systems: str | Path = "systems",
    max_frames: int = MAX_FRAMES,
    traj: bool = True,
    plots: bool = True,
) -> tuple[dict, Path]:
    """Analyse a sweep run directory; returns (report, output directory)."""
    run_dir = Path(run_dir)
    manifest = load_json(run_dir / MANIFEST_NAME)
    deck = find_deck(run_dir, manifest)
    if deck is None:
        raise AnalyzeError(f"{run_dir}: no deck (in.*) found")
    protocol = deck.name.split(".", 1)[1]
    if protocol == "pore":
        raise AnalyzeError(
            f"{run_dir}: pore runs (in.pore, D48: NVT, fixed lateral area) are analysed with"
            " `sepsim analyze pore` (D51); `sepsim analyze sweep` handles bulk NPT sweeps only"
        )
    if protocol != "sweep":
        raise AnalyzeError(f"{run_dir}: deck {deck.name} is not a sweep (in.sweep)")
    if not (run_dir / LOG_NAME).is_file():
        raise AnalyzeError(f"{run_dir}: no {LOG_NAME}")
    system, resolution = deck_system(deck)
    system = system or run_dir.resolve().parent.name
    out_dir = out_dir_for(run_dir, system, out)
    segments = parse_deck(deck)
    log = read_log(run_dir / LOG_NAME)
    report = report_header(VERSION, run_dir, manifest, system, resolution)
    report["method"] = {
        "step_window": f"second half ({STEP_SKIP:.0%} of rows dropped)",
        "hold_window": f"without the first {HOLD_SKIP:.0%} of rows",
        "sem": "statistical inefficiency (D26)",
        "max_frames": max_frames,
        "d_criterion": {"min_log_slope": D_MIN_SLOPE, "min_span": D_MIN_SPAN},
    }
    report["notes"] = []
    thermo = segment_thermo(segments, log, report["notes"])
    rows, eq, step_kappa, mass = sweep_rows(segments, thermo)
    report["segments"] = rows
    report["mass_gmol"] = mass
    missing = [r["name"] for r in rows if not r["done"]]
    if missing:
        report["notes"].append(f"{len(missing)} segment(s) not complete: {', '.join(missing)}")
    pts = fit_points([r for r in rows if r["done"]])
    report["fit_points_c"] = [p["t_set_c"] for p in pts]
    report["fits"] = sweep_fits(pts, mass) if mass and len(pts) >= 3 else None

    sys_arr = load_system_arrays(Path(systems) / system, report["notes"]) if traj else None
    hold_seg = {s.sweep_index: s for s in segments if s.sweep_kind == "hold" and not s.vdos}
    report["holds"] = [
        {
            "index": r["index"],
            "t_c": r["t_set_c"],
            "kappa": r.get("kappa"),
            "traj": trajectory_or_note(
                traj,
                sys_arr,
                r["done"],
                "hold",
                lambda r=r: hold_trajectory(run_dir, hold_seg[r["index"]], sys_arr, max_frames),
            ),
        }
        for r in rows
        if r["kind"] == "hold"
    ]
    # per-step kappa_T and static chain properties (steps: second half, as their stats)
    step_seg = {s.sweep_index: s for s in segments if s.sweep_kind == "step" and not s.vdos}
    report["steps"] = [
        {
            "index": r["index"],
            "t_c": r["t_set_c"],
            "kappa": step_kappa.get(r["index"]),
            "traj": trajectory_or_note(
                traj,
                sys_arr,
                r["done"],
                "step",
                lambda r=r: step_static(run_dir, step_seg[r["index"]], sys_arr),
            ),
        }
        for r in rows
        if r["kind"] == "step"
    ]
    report["caveats"] = sweep_caveats(report, run_dir, traj)
    report["convergence"] = eq
    if plots:
        report["plots"] = make_plots(report, out_dir, eq)
    return report, out_dir


def sweep_rows(segments, thermo) -> tuple[list[dict], list[dict], dict, float | None]:
    """The sweep's MD segments (steps and holds, VDOS runs skipped) as report rows: window
    stats, drift flags, the holds' block-average check and kappa_T; their convergence
    records; kappa_T per step (sweep index -> its second half); and the system mass
    (from the first Density x Volume row)."""
    rows, eq, step_kappa, mass = [], [], {}, None
    for seg, th in zip(segments, thermo, strict=True):
        if seg.sweep_index is None or seg.vdos:
            continue
        row = {
            "index": seg.sweep_index,
            "segment": seg.index,
            "name": seg.name,
            "kind": seg.sweep_kind,
            "t_set_c": seg.t_c,
            "t_k": seg.t_target_k,
            "done": th is not None,
        }
        if th is not None and len(th.get("Step", ())) >= MIN_STAT_ROWS:
            skip = HOLD_SKIP if seg.sweep_kind == "hold" else STEP_SKIP
            windows = SegmentWindows(skip, _block_rows(th))  # D55 block means
            row["stats"] = window_stats(th, skip, windows)
            main = {
                k: th[c] for k, c in (("density", "Density"), ("enthalpy", "Enthalpy")) if c in th
            }
            row["drift"] = drift_flags(main, skip, windows=windows)
            if seg.sweep_kind == "hold":
                row["convergence"] = {
                    k: block_convergence(x, skip, windows=windows) for k, x in main.items()
                }
            cols = {
                k: th[c]
                for k, c in (
                    ("T", "Temp"),
                    ("density", "Density"),
                    ("volume", "Volume"),
                    ("enthalpy", "Enthalpy"),
                )
                if c in th
            }
            if "Time" in th:
                eq.append(segment_convergence(row["name"], seg.sweep_kind, th, skip, cols, windows))
            if mass is None and "Density" in th and "Volume" in th:
                mass = float(th["Density"][0] * th["Volume"][0] * AVOGADRO * A3_CM3)
            if seg.sweep_kind == "hold":
                row["kappa"] = kappa_t(th, seg.t_target_k, HOLD_SKIP)
            elif seg.sweep_kind == "step":
                step_kappa[seg.sweep_index] = kappa_t(th, seg.t_target_k, STEP_SKIP)
        rows.append(row)
    return rows, eq, step_kappa, mass


def sweep_caveats(report: dict, run_dir: Path, traj: bool) -> list[str]:
    """The sweep report's caveats: Cp, unrelaxed chains (D47/D37), the fits, holds
    without trajectory results and CG time."""
    resolution = report["resolution"]
    caveats = [_cp_caveat(resolution)]
    caveats += chain_relaxation_caveat(run_dir)
    caveats.append(
        "α_V and Cp are linear fits in T over each window with SEM weights; a reduced χ²"
        " > 1 (curvature over the window, or SEMs too small) inflates the quoted errors"
        " by √χ²_red, and a large χ²_red over 25–160 °C means α_V or Cp depends on T"
        " (compare the two half windows)."
    )
    no_traj = [f"{h['t_c']:g} C" for h in report["holds"] if not h["traj"]["available"]]
    if no_traj and traj:
        caveats.append(f"No trajectory results for the hold(s) at {', '.join(no_traj)}.")
    if resolution == "cg":
        caveats.append(CG_TIME_NOTE)
    return caveats


SWEEP_EQ_PANELS = (
    ("T", "T (K)"),
    ("density", "density (g/cm³)"),
    ("volume", "V (Å³)"),
    ("enthalpy", "H (kcal/mol)"),
)


def equilibration_jobs(eq: list[dict], panels, title: str) -> list:
    """Plot jobs for ``equilibration.png`` (all segments on one time axis) and
    ``equilibration_holds.png`` (one column per hold)."""
    from sepsim import analyze_plots as ap

    if not eq:
        return []
    jobs = [
        (
            "equilibration",
            "thermo vs time, analysis windows shaded, block averages ± SEM",
            lambda p: ap.equilibration(p, eq, panels, title),
        )
    ]
    holds = [e for e in eq if e["kind"] == "hold"]
    if holds:
        jobs.append(
            (
                "equilibration_holds",
                "holds: thermo vs time, analysis window shaded, block averages ± SEM",
                lambda p: ap.equilibration_holds(p, holds, panels, title),
            )
        )
    return jobs


def make_plots(report: dict, out_dir: Path, eq: list[dict] | None = None) -> dict:
    from sepsim import analyze_plots as ap

    title = f"{report['system']} / {report['stage']}"
    jobs = []
    pts = [r for r in report["segments"] if r.get("stats")]
    if pts:
        jobs.append(
            (
                "thermo_vs_T",
                "density and enthalpy vs T with the linear fits",
                lambda p: ap.thermo_vs_t(p, pts, report.get("fits"), report["mass_gmol"], title),
            )
        )
    kap = [h for h in report["holds"] if h.get("kappa")]
    if kap:
        jobs.append(("kappa_T", "κ_T vs T (holds)", lambda p: ap.kappa_vs_t(p, kap, title)))
    if report.get("fits") and report["fits"]["alpha_V"]:
        jobs.append(
            (
                "alpha_V",
                "α_V and Cp per fit window",
                lambda p: ap.fit_windows(p, report["fits"], title),
            )
        )
    tr = [h for h in report["holds"] if h["traj"].get("available")]
    if tr:
        jobs += [
            ("msd", "backbone-site and chain COM MSD", lambda p: ap.msd_curves(p, tr, title)),
            ("p2_acf", "bond P2 autocorrelation", lambda p: ap.p2_curves(p, tr, title)),
            ("chain_vs_T", "Rg, R_ee and C_n vs T", lambda p: ap.chain_vs_t(p, tr, title)),
        ]
        rel = [(h["t_c"], h["traj"]) for h in tr if h["traj"].get("relaxation")]
        if rel:
            jobs.append(
                (
                    "relaxation",
                    "end-to-end and Rouse mode ACFs, p²τ_p vs p",
                    lambda p: ap.relaxation_curves(p, rel, title),
                )
            )
    jobs += equilibration_jobs(eq or [], SWEEP_EQ_PANELS, title)
    return draw_plots(jobs, report, out_dir)


def draw_plots(jobs, report: dict, out_dir: Path) -> dict:
    """Draw (name, title, draw(path)) jobs into ``out_dir``/<name>.png; a failing plot is
    noted in the report and skipped. Returns {name: {file, title}}."""
    out = {}
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, desc, draw in jobs:
        file = f"{name}.png"
        try:
            draw(out_dir / file)
        except (ValueError, OSError) as exc:
            report["notes"].append(f"plot {name} failed: {exc}")
            continue
        out[name] = {"file": file, "title": desc}
    return out


# --------------------------------------------------------------------------- markdown


def render_markdown(r: dict) -> str:
    """results.md for one sweep analysis."""
    lines = header_markdown(r, "Sweep analysis", "sweep", "D49")
    lines.append(
        f"- windows: steps {r['method']['step_window']}; holds {r['method']['hold_window']};"
        f" SEM from the {r['method']['sem']}"
    )
    if r.get("mass_gmol"):
        lines.append(f"- system mass {r['mass_gmol']:.1f} g/mol (from Density × Volume)")
    for n in r.get("notes", []):
        lines.append(f"- note: {n}")
    lines += _segments_markdown(r)
    lines += _kappa_markdown(r)
    lines += _steps_markdown(r)
    lines += _fits_markdown(r)
    lines += _holds_markdown(r)
    lines += relaxation_markdown([(h["t_c"], h["traj"]) for h in r["holds"]], r.get("resolution"))
    lines += equilibration_markdown(r, LOCAL_NOTE, CHAIN_NOTE)
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r.get("caveats", [])]
    lines += plots_markdown(r.get("plots"))
    return "\n".join(lines) + "\n"


def _segments_markdown(r: dict) -> list[str]:
    lines = [
        "",
        "## Segments",
        "",
        (
            "| # | segment | T set (°C) | window (ns) | T (°C) | density (g/cm³) | H (kcal/mol) |"
            " V (Å³) | drift |"
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in r["segments"]:
        st = s.get("stats") or {}
        win = f"{st['window_ps'] / 1000:.2f}" if st.get("window_ps") else ""
        lines.append(
            f"| {s['index']} | {s['kind']} | {s['t_set_c']:g} | {win} |"
            f" {_pm(st.get('t_c'), '.2f')} | {_pm(st.get('density'), '.5f')} |"
            f" {_pm(st.get('enthalpy'), '.1f')} | {_pm(st.get('volume'), '.0f')} |"
            f" {drift_cell(s)} |"
            if st
            else f"| {s['index']} | {s['kind']} | {s['t_set_c']:g} | not complete | | | | | |"
        )
    return lines


def _kappa_markdown(r: dict) -> list[str]:
    lines = [
        "",
        "## Isothermal compressibility (holds)",
        "",
        (
            "κ_T = (⟨V²⟩ − ⟨V⟩²)/(k_B T ⟨V⟩) over the hold window (NPT iso Nosé–Hoover), T the set"
            " point; SEM = statistical-inefficiency SEM of (V − ⟨V⟩)² on 100 ps block means, as"
            " for the other thermo SEMs (D55; g given in raw samples)."
        ),
        "",
        "| T (°C) | κ_T (GPa⁻¹) | σ_V (Å³) | ⟨V⟩ (Å³) | g | samples |",
        "|---|---|---|---|---|---|",
    ]
    for h in r["holds"]:
        k = h.get("kappa")
        lines.append(
            f"| {h['t_c']:g} | {k['kappa_T_GPa']:.3f} ± {k['sem']:.3f} | {k['V_std_A3']:.1f} |"
            f" {k['V_mean_A3']:.0f} | {k['g']:.1f} | {k['samples']} |"
            if k
            else f"| {h['t_c']:g} | n/a | | | | |"
        )
    return lines


def _steps_markdown(r: dict) -> list[str]:
    steps = r.get("steps") or []
    if not steps:
        return []
    lines = [
        "",
        "## Sweep steps: κ_T and chain size",
        "",
        (
            "Per step, over its second half (as its thermo stats): κ_T as for the holds and"
            " the static chain properties from the step DCD (no MSD / relaxation). The"
            " steps are short, so κ_T is noisier and the chain shape is largely inherited"
            " from the segment before."
        ),
        "",
        "| T (°C) | κ_T (GPa⁻¹) | frames | R_g (Å) | R_ee (Å) | C_n plateau | ordered fraction |",
        "|---|---|---|---|---|---|---|",
    ]
    for st in steps:
        k, t = st.get("kappa"), st.get("traj") or {}
        kap = f"{k['kappa_T_GPa']:.3f} ± {k['sem']:.3f}" if k else "n/a"
        if t.get("available"):
            cr = t.get("crystallinity") or {}
            frac = f"{cr['fraction']['mean']:.3f}" if cr.get("available") else "n/a"
            lines.append(
                f"| {st['t_c']:g} | {kap} | {t['frames']} | {_pm(t['rg']['rg_A'], '.2f')} |"
                f" {_pm(t['ree']['ree_A'], '.1f')} | {_pm(t['c_n']['plateau'], '.2f')} |"
                f" {frac} |"
            )
        else:
            note = "; ".join(t.get("notes") or []) or "no trajectory"
            lines.append(f"| {st['t_c']:g} | {kap} | {note} | | | | |")
    return lines


def _fits_markdown(r: dict) -> list[str]:
    f = r.get("fits")
    lines = ["", "## Thermal expansion and classical Cp (fits over the sweep)", ""]
    if not f:
        return lines + ["Not enough completed segments for a fit."]
    lines += [
        (
            "Linear fits in T over each window, SEM-weighted, one point per temperature"
            f" (hold where there is one): {', '.join(f'{t:g}' for t in r['fit_points_c'])} °C."
            " α_V = (1/⟨V⟩) dV/dT; Cp = dH/dT per gram; errors 1σ from the fit, scaled by"
            " √χ²_red when χ²_red > 1."
        ),
        "",
        "| window (°C) | points | α_V (10⁻⁴ K⁻¹) | χ²_red (V) | Cp (J g⁻¹ K⁻¹) | χ²_red (H) |",
        "|---|---|---|---|---|---|",
    ]
    for a, c in zip(f["alpha_V"], f["cp"], strict=True):
        lines.append(
            f"| {a['window_c'][0]:g}–{a['window_c'][1]:g} | {a['n']} |"
            f" {a['alpha_V_per_K'] * 1e4:.3f} ± {a['err'] * 1e4:.3f} | {_f(a['chi2_red'])} |"
            f" {c['cp_J_gK']:.3f} ± {c['err']:.3f} | {_f(c['chi2_red'])} |"
        )
    for n in f.get("notes", []):
        lines.append(f"- {n}")
    return lines


def _holds_markdown(r: dict) -> list[str]:
    lines = [
        "",
        "## Hold trajectories: mobility and chain size",
        "",
        (
            "Backbone sites (CG: beads; UA/AA: backbone carbons) and chains, positions relative"
            " to the system's mass centre. MSD and P2 combine the D46 bursts (0.1 ps frames,"
            " lags < the hold frame interval) with the hold DCD (lags up to half the hold)."
            f" D_COM from an OLS line over the end of the COM MSD where the local log-slope"
            f" stays ≥ {D_MIN_SLOPE:g} over a factor ≥ {D_MIN_SPAN:g} in lag and the MSD ≥ 2⟨Rg²⟩"
            ' (D55; error: slope spread of the two halves of that range); else "not'
            ' diffusive" (log-slope at the longest lag given). Rg mass-weighted over all atoms'
            " of a chain;"
            f" C_n plateau over n ≥ 100 carbons (D37) on ≤ {r['method']['max_frames']} frames."
        ),
        "",
        (
            "| T (°C) | frames | bursts | MSD seg 10 ps / max (Å²) | COM MSD max (Å²) | D_COM"
            " (cm²/s) | P2 1/e (ps) | Rg (Å) | R_ee (Å) | C_n plateau |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    notes = []
    for h in r["holds"]:
        t = h["traj"]
        for n in t.get("notes", []):
            notes.append(f"- {h['t_c']:g} °C: {n}")
        if not t.get("available"):
            lines.append(f"| {h['t_c']:g} | trajectory not available | | | | | | | | |")
            continue
        sm, cm, p2 = t["segment_msd"], t["com_msd"], t["p2"]
        d = (
            f"{cm['D_cm2_s']:.2e} ± {cm['D_err_cm2_s']:.1e}"
            if cm["diffusive"]
            else f"not diffusive (log-slope {cm['slope_end']:.2f} at the longest lag)"
        )
        p2t = (
            f"{p2['t_1e_ps']:.1f}"
            if p2["t_1e_ps"] is not None
            else f"> {p2['lag_max_ps']:g} (P2 {p2['at_max']:.2f})"
        )
        m10 = sm.get("msd_10ps_A2")
        lines.append(
            f"| {h['t_c']:g} | {t['frames']} × {t['frame_ps']:g} ps | {t['bursts']['used']} |"
            f" {_f(m10, '.1f')} / {sm['msd_at_max_A2']:.0f} ({sm['lag_max_ps'] / 1000:g} ns) |"
            f" {cm['msd_at_max_A2']:.0f} | {d} | {p2t} | {_pm(t['rg']['rg_A'], '.2f')} |"
            f" {_pm(t['ree']['ree_A'], '.1f')} | {_pm(t['c_n']['plateau'], '.3f')} |"
        )
    return lines + ([""] + notes if notes else [])


def _ns(ps: float | None) -> str:
    return "n/a" if ps is None else f"{ps / 1000:.3g}"


def _tau_cell(m: dict, t_key: str = "t_1e_ps") -> str:
    """A relaxation time in ns: the 1/e time if reached, else the fit marked extrapolated."""
    if m.get("reached"):
        return _ns(m[t_key])
    fit = m.get("tau_fit_ps")
    tail = f"C {m['acf_at_max']:.2f} at max lag"
    return f"not reached ({tail}; fit {_ns(fit)}, extrap.)" if fit else f"not reached ({tail})"


def relaxation_markdown(items, resolution: str | None, what: str = "hold") -> list[str]:
    """results.md "Chain relaxation" section (D56) shared by `analyze sweep`, `analyze
    pore` (whole film) and `analyze hold`. ``items``: (T in C, traj dict) per hold."""
    rows = [(t, tr) for t, tr in items if tr and tr.get("available") and tr.get("relaxation")]
    lines = ["", f"## Chain relaxation ({what}s; D56)", ""]
    if not rows:
        return lines + ["No trajectory results."]
    lag = rows[0][1]["relaxation"]["lag_max_ps"]
    lines += [
        (
            "End-to-end vector ACF ⟨R(t)·R(0)⟩/⟨R²⟩ and Rouse mode ACFs ⟨X_p(t)·X_p(0)⟩/⟨X_p²⟩,"
            " X_p = (1/N) Σ_n cos(pπ(n−½)/N) r_n over the backbone sites, every time origin,"
            f" lags up to half the {what} ({lag / 1000:g} ns here). Times in ns: the first 1/e"
            " crossing; if C stays above 1/e within the lag window the time is 'not reached'"
            " and only an exponential fit of ln C over 0.2 ≤ C ≤ 0.9 is given (marked"
            " extrap.: it extrapolates the early decay). τ_ee fit is that fit for R_ee. τ_1/τ_2"
            " is 4 for Rouse chains. p²⟨X_p²⟩ (relative to p = 1, p = 2…5) is flat for an ideal"
            " Rouse chain; it falls at high p where the chain is stiffer than Gaussian on that"
            " scale. Crystallinity: D26 local alignment, fraction of backbone sites with"
            f" p2 ≥ {CRYSTAL_THRESHOLD:g} (**{CRYSTAL_LABEL}**: no crystal reference, so the"
            " number is a baseline for an amorphous box, not a calibrated crystallinity) and"
            " the largest crystalline cluster (sites)."
        ),
        "",
        (
            "| T (°C) | τ_ee 1/e (ns) | τ_ee fit (ns) | τ_1 (ns) | τ_2 (ns) | τ_3 (ns) |"
            " τ_1/τ_2 (Rouse 4) | p²⟨X_p²⟩ / p=1 (p = 2…5) | crystallinity |"
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    est = []
    for t, tr in rows:
        rx = tr["relaxation"]
        ee, modes = rx["ree"], {m["p"]: m for m in rx["rouse"]}
        ee_fit = _ns(ee["tau_fit_ps"]) + (" (extrap.)" if ee["extrapolated"] else "")
        m1, m2 = modes.get(1), modes.get(2)
        ratio = "n/a"
        if m1 and m2:
            if m1["reached"] and m2["reached"]:
                ratio = f"{m1['t_1e_ps'] / m2['t_1e_ps']:.2f}"
            elif m1["tau_fit_ps"] and m2["tau_fit_ps"]:
                ratio = f"{m1['tau_fit_ps'] / m2['tau_fit_ps']:.2f} (fits)"
        flat = " / ".join(f"{v:.2f}" for v in rx["p2_amp_rel"][1:])
        cr = tr.get("crystallinity") or {}
        crys = (
            f"{cr['fraction']['mean']:.3f} (max {cr['fraction_max']:.3f}; cluster ≤"
            f" {cr['largest_cluster']['max']})"
            if cr.get("available")
            else "n/a"
        )
        cells = [_tau_cell(modes[p]) if p in modes else "n/a" for p in (1, 2, 3)]
        lines.append(
            f"| {t:g} | {_tau_cell(ee)} | {ee_fit} | {' | '.join(cells)} | {ratio} | {flat} |"
            f" {crys} |"
        )
        if not (m1 or {}).get("reached") and rx["tau1_from_p"]:
            vals = ", ".join(f"p={p}: {_ns(v)}" for p, v in rx["tau1_from_p"].items())
            est.append(f"- {t:g} °C: τ_1 ≈ p²τ_p from the reached modes: {vals} ns.")
    if est:
        lines += [
            "",
            (
                "Where τ_1 is not reached, p²τ_p of the faster modes estimates it under ideal"
                " Rouse scaling (τ_p ∝ p⁻²). Real melts show τ_p ∝ p^−2.2…−2.4 (stiffness,"
                " local friction), so p²τ_p underestimates τ_1, more so the higher p:"
            ),
            "",
            *est,
        ]
    if resolution == "cg":
        lines += ["", CG_TIME_NOTE]
    return lines


LOCAL_NOTE = (
    "Local quantities (density, enthalpy, κ_T, segmental MSD, bond P2: relaxation times"
    " ~10–100 ps in CG, the bond P2 1/e time above) equilibrate within the dropped part"
    " of each segment; their windows are what the drift and block checks test."
)
CHAIN_NOTE = (
    "Chain-scale quantities (Rg, R_ee, C_n, chain COM motion) relax on the end-to-end"
    " time (CG C240 at 25 °C: of order 100 ns; C1500 far longer), longer than a 25 ns"
    " hold: their hold"
    " averages describe the chain configurations carried in from the 500 K equilibration"
    " and cooling rather than a re-equilibrated state at T. Per hold:"
)


def write_results(report: dict, out_dir: Path, render=None) -> None:
    """Write results.json and results.md (``render``, default the sweep report's
    :func:`render_markdown`) atomically into ``out_dir``."""
    write_atomic(
        out_dir, ((JSON_NAME, dump_json(report)), (MD_NAME, (render or render_markdown)(report)))
    )
