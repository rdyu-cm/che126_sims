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
  <R_ee^2>^1/2 and the C_n plateau (n >= 100 carbons, D37) averaged over the hold.

The segment parser, log reader and thermo concatenation are those of
:mod:`sepsim.progress`; the DCDs are read with MDAnalysis ``DCDReader`` (id-sorted,
unwrapped, D39). Holds without a DCD are reported as "trajectory not available".
Pore decks (``in.pore``) are rejected with a pointer to `sepsim analyze pore` (D51,
:mod:`sepsim.analyze_pore`).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import platform
import warnings
from pathlib import Path

import numpy as np

from sepsim.analysis.lammps_log import read_log
from sepsim.analysis.stats import linear_fit
from sepsim.analysis.units import A3_CM3, AVOGADRO
from sepsim.progress import (
    JSON_NAME as PROGRESS_JSON,
)
from sepsim.progress import (
    LOG_NAME,
    _block_rows,
    _concat_thermo,
    _enthalpy_mean_sem,
    _input_stage,
    _mean_sem,
    _round,
    d47_criteria,
    deck_system,
    find_deck,
    load_json,
    parse_deck,
)
from sepsim.run import CODE_DIR, MANIFEST_NAME, git_info

VERSION = 1
MD_NAME, JSON_NAME = "results.md", "results.json"
HOLD_SKIP = 0.10  # fraction of a hold's thermo rows dropped as equilibration
STEP_SKIP = 0.50  # steps: second half, as in `sepsim progress`
MAX_FRAMES = 500  # hold frames (evenly spaced) for the C_n plateau
FIT_WINDOWS_C = ((25.0, 160.0), (25.0, 90.0), (90.0, 160.0))
D_MIN_SLOPE = 0.9  # diffusive regime: local d ln MSD / d ln t >= this ...
D_MIN_SPAN = 2.0  # ... from t_start to the longest lag, with t_end / t_start >= this
A2_PS_TO_CM2_S = 1e-16 / 1e-12  # Angstrom^2/ps -> cm^2/s


class AnalyzeError(ValueError):
    """The run directory cannot be analysed (no deck, not a sweep, no log)."""


def out_dir_for(run_dir: Path, system: str, out: str | Path | None) -> Path:
    """``out`` if given, else ``results/analysis/<system>/<stage>/`` under the cwd."""
    if out is not None:
        return Path(out)
    return Path("results") / "analysis" / system / Path(run_dir).resolve().name


# --------------------------------------------------------------------------- thermo


def segment_thermo(segments, log) -> list[dict | None]:
    """Thermo of every segment (its chunk blocks concatenated) once all its runs are
    complete, else None; blocks are assigned in deck order as in `sepsim progress`."""
    runs = log.runs if log else []
    out, start = [], 0
    for seg in segments:
        mine = runs[start : start + len(seg.run_steps)]
        start += len(seg.run_steps)
        done = len(mine) == len(seg.run_steps) and all(r.complete for r in mine)
        out.append(_concat_thermo(mine) if done and seg.command == "run" else None)
    return out


def window_stats(thermo: dict, skip: float) -> dict:
    """Mean +- SEM of T (C), density, enthalpy and volume over the rows after the first
    ``skip`` fraction; also the window's row count and length (ps, from Time)."""
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
            ms = _mean_sem(thermo[col][k:], _block_rows(thermo))  # D55 block means
            if ms is not None:
                ms["mean"] += shift
            out[key] = ms
    if out.get("enthalpy"):  # D55: SEM from E + p_ext V
        out["enthalpy"] = _enthalpy_mean_sem(thermo, slice(k, None))
    return out


def kappa_t(thermo: dict, t_k: float, skip: float) -> dict | None:
    """Isothermal compressibility (1/GPa) from the Volume column after ``skip``."""
    from sepsim.analysis.thermo import isothermal_compressibility

    v = thermo.get("Volume")
    if v is None:
        return None
    v = v[int(np.floor(skip * len(v))) :]
    if len(v) < 3 or np.ptp(v) == 0:
        return None
    c = isothermal_compressibility(v, t_k)
    return {
        "kappa_T_GPa": c.kappa_T,
        "sem": c.kappa_T_sem,
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
        win = (lo + 273.15 - 1e-6, hi + 273.15 + 1e-6)
        sel = (t >= win[0]) & (t <= win[1])
        if sel.sum() < 3:
            out["notes"].append(f"{lo:g}-{hi:g} C: fewer than 3 temperatures, no fit")
            continue
        te = thermal_expansion(t, v, v_err, T_window=win)
        cp = heat_capacity_classical(t, h, mass_gmol, h_err, T_window=win)
        vs, vi, _, _ = linear_fit(t[sel], v[sel], v_err[sel])
        hs, hi_, _, _ = linear_fit(t[sel], h[sel], h_err[sel])
        chi_v = _chi2_red(t[sel], v[sel], v_err[sel], vs, vi)
        chi_h = _chi2_red(t[sel], h[sel], h_err[sel], hs, hi_)
        out["alpha_V"].append(
            {
                "window_c": [lo, hi],
                "alpha_V_per_K": te.alpha_V,
                "err": te.alpha_V_err * _birge(chi_v),
                "err_unscaled": te.alpha_V_err,
                "alpha_L_per_K": te.alpha_L,
                "V_mean_A3": te.V_mean,
                "n": te.n_points,
                "line": [vs, vi],
                "chi2_red": chi_v,
            }
        )
        out["cp"].append(
            {
                "window_c": [lo, hi],
                "cp_J_gK": cp.cp_JgK,
                "err": cp.cp_JgK_err * _birge(chi_h),
                "err_unscaled": cp.cp_JgK_err,
                "cp_kcal_molK": cp.cp_kcalmolK,
                "n": cp.n_points,
                "line": [hs, hi_],
                "chi2_red": chi_h,
            }
        )
    return out


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


def drift_flags(series: dict, skip: float, block: int | None = None) -> dict:
    """Halves of the analysis window (rows after ``skip``) compared per named series:
    :func:`sepsim.analysis.chain.drift_check` (mean difference > 2 combined SEM)."""
    from sepsim.analysis.chain import drift_check

    out = {}
    for name, x in series.items():
        x = np.asarray(x, dtype=float)
        w = x[int(np.floor(skip * len(x))) :]
        if len(w) < 12 or np.ptp(w) == 0:
            continue
        try:
            a, b, delta, sem, drift = drift_check(w, block=block)
        except ValueError:  # a zero-variance half
            continue
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


def block_convergence(x, skip: float, block: int | None = None) -> dict | None:
    """Block-average check of the window's SEM: the SEM from the statistical inefficiency
    (D26) vs the SEM of the means of ``CONV_BLOCKS`` blocks; once blocks are longer than
    the correlation time the block SEM plateaus at the statistical-inefficiency value.
    ``converged``: the 8-block SEM is within a factor 2 of it."""
    x = np.asarray(x, dtype=float)
    w = x[int(np.floor(skip * len(x))) :]
    ms = _mean_sem(w, block)
    if ms is None or not ms["sem"]:
        return None
    blocks = {}
    for nb in CONV_BLOCKS:
        if len(w) >= 3 * nb:
            means = np.array([b.mean() for b in np.array_split(w, nb)])
            blocks[str(nb)] = float(means.std(ddof=1) / np.sqrt(nb))
    last = blocks.get(str(CONV_BLOCKS[-1]))
    return {
        "sem": ms["sem"],
        "block_sem": blocks,
        "converged": None if last is None else bool(last <= 2.0 * ms["sem"]),
    }


def quantity_convergence(t_ps, x, skip: float, block: int | None = None) -> dict:
    """Convergence record of one series over a segment (``results.json`` ``convergence``):
    the series thinned to <= ``EQ_POINTS`` points (t_ps, value), ``EQ_BLOCKS`` block
    averages over the whole segment, and over the analysis window (after ``skip``) the
    mean +- SEM, statistical inefficiency g, and the halves test (second - first half,
    combined SEM, their ratio z, drift if |z| > 2)."""
    from sepsim.analysis.chain import drift_check
    from sepsim.analysis.stats import timeseries_mean

    t, x = np.asarray(t_ps, dtype=float), np.asarray(x, dtype=float)
    if block is None and len(t) >= 2:  # D55: 100 ps block means for thermo series
        block = _block_rows({"Time": t * 1000.0})
    k = int(np.floor(skip * len(x)))
    w = x[k:]
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
    if len(w) >= 3 and np.ptp(w) > 0:
        tm = timeseries_mean(w, block=block)
        out.update(sem=tm.sem, g=tm.g)
        if len(w) >= 12:
            try:
                _, _, delta, sem, drift = drift_check(w, block=block)
                out.update(
                    halves={"delta": delta, "sem": sem, "z": delta / sem if sem else None},
                    drift=drift,
                )
            except ValueError:
                pass
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
    out = []
    for nb in SEM_BLOCKS:
        if len(w) >= 3 * nb:
            means = np.array([b.mean() for b in np.array_split(w, nb)])
            out.append(
                {
                    "n_blocks": nb,
                    "block_ps": len(w) // nb * dt,
                    "sem": float(means.std(ddof=1) / np.sqrt(nb)),
                }
            )
    return out


def segment_convergence(name: str, kind: str, thermo: dict, skip: float, cols: dict) -> dict:
    """``results.json`` ``convergence`` entry of one segment: name, kind, start/end time
    and analysis window (ps), :func:`quantity_convergence` per series in ``cols``, and for
    holds the :func:`sem_vs_block` curve per series."""
    t = np.asarray(thermo["Time"], dtype=float) / 1000.0  # fs -> ps
    k = int(np.floor(skip * len(t)))
    out = {
        "name": name,
        "kind": kind,
        "t_start_ps": float(t[0]),
        "t_end_ps": float(t[-1]),
        "window": [float(t[k]), float(t[-1])],
        "skip": skip,
        "quantities": {q: quantity_convergence(t, x, skip) for q, x in cols.items()},
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


def _system_arrays(system_dir: Path) -> dict:
    """Backbone rows, molecule index and masses of the id-sorted atoms of a system."""
    import yaml

    from sepsim.analysis.chain import backbone_chains
    from sepsim.build.datafile import read_data_file

    man = yaml.safe_load((system_dir / "manifest.yaml").read_text())
    chains = backbone_chains(system_dir / "data.lmp", man)
    df = read_data_file(system_dir / "data.lmp")
    atoms = df.sorted_atoms()
    mass_of = {int(r[0]): float(r[1]) for r in df.sections["Masses"]}
    masses = np.array([mass_of[int(t)] for t in atoms[:, 2]])
    _, molecule = np.unique(atoms[:, 1].astype(np.int64), return_inverse=True)
    local, k = [], 0
    for c in chains:
        local.append(np.arange(k, k + len(c)))
        k += len(c)
    return {
        "manifest": man,
        "n_atoms": len(atoms),
        "bb_rows": np.concatenate(chains),
        "chains": local,  # backbone sites per chain, as indices into bb_rows
        "molecule": molecule,
        "masses": masses,
        "mol_mass": np.bincount(molecule, weights=masses),
    }


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
        bb, com, rg2 = [], [], []
        for ts in reader:
            x = ts.positions.astype(float)
            c, g = chain_com_rg2(x, sys_arr["molecule"], sys_arr["masses"])
            bb.append(x[sys_arr["bb_rows"]].astype(np.float32))
            com.append(c[0])
            rg2.append(g[0])
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
    }


def _bond_vectors(bb: np.ndarray, chains: list[np.ndarray]) -> np.ndarray:
    a = np.concatenate([c[:-1] for c in chains])
    b = np.concatenate([c[1:] for c in chains])
    return bb[:, b] - bb[:, a]


def _mean_sd(x) -> dict:
    """Mean +- SEM (statistical inefficiency) of a per-frame series."""
    ms = _mean_sem(x)
    if ms is None:
        x = np.asarray(x, dtype=float)
        return {"mean": float(x.mean()), "sem": None}
    return ms


def _root(ms: dict) -> dict:
    """<x>^1/2 with SEM / (2 <x>^1/2)."""
    r = float(np.sqrt(ms["mean"]))
    return {"mean": r, "sem": None if ms["sem"] is None else ms["sem"] / (2 * r)}


def hold_trajectory(run_dir: Path, seg, sys_arr: dict, max_frames: int = MAX_FRAMES) -> dict:
    """Mobility and chain-size results of one hold (a :class:`sepsim.progress.Segment`)
    from its DCD and burst DCDs."""
    from sepsim.analysis.chain import (
        CARBONS_PER_SITE,
        characteristic_ratio,
        decorrelation_time,
    )
    from sepsim.analysis.mobility import (
        average_curves,
        diffusion_coefficient,
        mean_over_batches,
        msd,
        p2_autocorrelation,
        stitch_curves,
    )

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
    tr = read_frames(run_dir / dcd, sys_arr)
    nf = len(tr["bb"])
    if nf < 6:
        out["notes"].append(f"trajectory not available ({dcd}: only {nf} frames)")
        return out
    out.update(
        available=True, dcd=dcd, frames=nf, frame_ps=frame_ps, hold_ns=(nf - 1) * frame_ps / 1000
    )
    chains = sys_arr["chains"]
    lag_max = nf // 2
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
            out["notes"].append(f"{f} skipped: {exc}")
            continue
        m = len(b["bb"])
        if m < 3:
            continue
        b_ps = n * seg.dt_fs / 1000.0
        lb, mb = mean_over_batches(msd, b["bb"], b_ps, m - 1)
        b_msd.append((lb, mb, m))
        b_com.append((*msd(b["com"], b_ps, m - 1), m))
        _, pb = mean_over_batches(p2_autocorrelation, _bond_vectors(b["bb"], chains), b_ps, m - 1)
        b_p2.append((lb, pb, m))
        used.append(f)
    if bursts and not used:
        out["notes"].append(f"burst DCDs not found ({len(bursts)} listed in the deck)")
    elif not bursts:
        out["notes"].append("no burst DCDs (deck without D46 bursts): lags from the hold DCD only")
    out["bursts"] = {"listed": len(bursts), "used": len(used)}

    def combine(burst_curves, lags, vals):
        if not burst_curves:
            return lags, vals, np.ones(len(lags), int)
        bl, bv = average_curves(burst_curves)
        return stitch_curves(bl, bv, lags, vals)

    lm, vm, sm = combine(b_msd, lags_h, msd_h)
    lc, vc, _sc = combine(b_com, lags_h, com_h)
    lp, vp, _sp = combine(b_p2, lags_h, p2_h)

    fit = diffusion_coefficient(lc, vc, D_MIN_SLOPE, D_MIN_SPAN, rg2=float(tr["rg2"].mean()))
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
        )
    t_1e = decorrelation_time(lp, vp)
    seg_msd = {"lag_max_ps": float(lm[-1]), "msd_at_max_A2": float(vm[-1])}
    for lag in (1.0, 10.0, 1000.0):
        k = np.flatnonzero(np.isclose(lm, lag, rtol=1e-6))
        if len(k):
            seg_msd[f"msd_{lag:g}ps_A2"] = float(vm[k[0]])

    # chain size over the hold
    rg2 = _mean_sd(tr["rg2"].mean(axis=1))
    first = np.array([c[0] for c in chains])
    last = np.array([c[-1] for c in chains])
    ree = tr["bb"][:, last].astype(float) - tr["bb"][:, first]
    ree2 = _mean_sd(np.sum(ree**2, axis=2).mean(axis=1))
    pick = np.unique(np.linspace(0, nf - 1, min(nf, max_frames)).round().astype(int))
    res = sys_arr["manifest"]["resolution"]
    cg = res == "cg"
    nc, cn = characteristic_ratio(
        tr["bb"][pick].astype(float),
        chains,
        carbons_per_site=CARBONS_PER_SITE[res],
        bond_length=1.54 if cg else None,
        per_frame=True,
    )
    sel = nc >= 100
    cn_plateau = _mean_sd(cn[:, sel].mean(axis=1)) if sel.any() else None
    out.update(
        segment_msd=seg_msd,
        com_msd=com,
        p2={
            "t_1e_ps": t_1e,
            "lag_max_ps": float(lp[-1]),
            "at_max": float(vp[-1]),
            "vectors": "bead-bead bonds" if cg else "backbone C-C bonds",
        },
        rg={"rg2_A2": rg2, "rg_A": _root(rg2)},
        ree={"ree2_A2": ree2, "ree_A": _root(ree2)},
        c_n={
            "plateau": cn_plateau,
            "frames": len(pick),
            "n_min": 100,
            "bond_length": 1.54 if cg else None,
        },
        curves={
            "msd_lag_ps": _round(_log_thin(lm)),
            "msd_A2": _round(vm[_log_idx(lm)]),
            "msd_src": sm[_log_idx(lm)].tolist(),
            "com_lag_ps": _round(_log_thin(lc)),
            "com_A2": _round(vc[_log_idx(lc)]),
            "p2_lag_ps": _round(_log_thin(lp)),
            "p2": _round(vp[_log_idx(lp)]),
            "cn_n": nc.tolist(),
            "cn": _round(cn.mean(axis=0)),
        },
    )
    return out


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
    thermo = segment_thermo(segments, log)
    now = dt.datetime.now().astimezone()
    report: dict = {
        "version": VERSION,
        "generated": now.isoformat(timespec="seconds"),
        "generated_on": platform.node(),
        "system": system,
        "resolution": resolution,
        "stage": run_dir.resolve().name,
        "run_dir": str(run_dir.resolve()),
        "run_status": (manifest or {}).get("status"),
        "run_node": (manifest or {}).get("hostname"),
        "run_git": (manifest or {}).get("git"),
        "code_git": git_info(CODE_DIR),
        "method": {
            "step_window": f"second half ({STEP_SKIP:.0%} of rows dropped)",
            "hold_window": f"without the first {HOLD_SKIP:.0%} of rows",
            "sem": "statistical inefficiency (D26)",
            "max_frames": max_frames,
            "d_criterion": {"min_log_slope": D_MIN_SLOPE, "min_span": D_MIN_SPAN},
        },
        "notes": [],
    }
    rows, mass, eq = [], None, []
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
        if th is not None and len(th.get("Step", ())) >= 6:
            skip = HOLD_SKIP if seg.sweep_kind == "hold" else STEP_SKIP
            row["stats"] = window_stats(th, skip)
            main = {
                k: th[c] for k, c in (("density", "Density"), ("enthalpy", "Enthalpy")) if c in th
            }
            blk = _block_rows(th)
            row["drift"] = drift_flags(main, skip, blk)
            if seg.sweep_kind == "hold":
                row["convergence"] = {k: block_convergence(x, skip, blk) for k, x in main.items()}
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
                eq.append(segment_convergence(row["name"], seg.sweep_kind, th, skip, cols))
            if mass is None and "Density" in th and "Volume" in th:
                mass = float(th["Density"][0] * th["Volume"][0] * AVOGADRO * A3_CM3)
            if seg.sweep_kind == "hold":
                row["kappa"] = kappa_t(th, seg.t_target_k, HOLD_SKIP)
        rows.append(row)
    report["segments"] = rows
    report["mass_gmol"] = mass
    missing = [r["name"] for r in rows if not r["done"]]
    if missing:
        report["notes"].append(f"{len(missing)} segment(s) not complete: {', '.join(missing)}")
    pts = fit_points([r for r in rows if r["done"]])
    report["fit_points_c"] = [p["t_set_c"] for p in pts]
    report["fits"] = sweep_fits(pts, mass) if mass and len(pts) >= 3 else None

    holds = []
    seg_by_index = {s.sweep_index: s for s in segments if s.sweep_kind == "hold" and not s.vdos}
    sys_arr = None
    system_dir = Path(systems) / system
    if traj:
        try:
            sys_arr = _system_arrays(system_dir)
        except (OSError, ValueError, KeyError) as exc:
            report["notes"].append(f"system {system_dir} not usable: {exc}")
    for r in rows:
        if r["kind"] != "hold":
            continue
        h = {"index": r["index"], "t_c": r["t_set_c"], "kappa": r.get("kappa")}
        if not traj:
            h["traj"] = {"available": False, "notes": ["trajectory analysis skipped (--no-traj)"]}
        elif sys_arr is None:
            h["traj"] = {"available": False, "notes": ["trajectory not available (no system)"]}
        elif not r["done"]:
            h["traj"] = {"available": False, "notes": ["hold not complete"]}
        else:
            try:
                h["traj"] = hold_trajectory(run_dir, seg_by_index[r["index"]], sys_arr, max_frames)
            except (OSError, ValueError) as exc:
                h["traj"] = {"available": False, "notes": [f"trajectory failed: {exc}"]}
        holds.append(h)
    report["holds"] = holds
    caveats = [_cp_caveat(resolution)]
    caveats += chain_relaxation_caveat(run_dir)
    caveats.append(
        "α_V and Cp are linear fits in T over each window with SEM weights; a reduced χ²"
        " > 1 (curvature over the window, or SEMs too small) inflates the quoted errors"
        " by √χ²_red, and a large χ²_red over 25–160 °C means α_V or Cp depends on T"
        " (compare the two half windows)."
    )
    no_traj = [f"{h['t_c']:g} C" for h in holds if not h["traj"]["available"]]
    if no_traj and traj:
        caveats.append(f"No trajectory results for the hold(s) at {', '.join(no_traj)}.")
    if resolution == "cg":
        caveats.append(
            "CG time is not real time: SDK beads move faster than the atoms they"
            " represent, so MSD, D_COM and P2 times are model times (not rescaled)."
        )
    report["caveats"] = caveats
    report["convergence"] = eq
    if plots:
        report["plots"] = make_plots(report, out_dir, eq)
    return report, out_dir


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


def _pm(ms: dict | None, fmt: str) -> str:
    if not ms:
        return ""
    if ms.get("sem") is None:
        return f"{ms['mean']:{fmt}}"
    return f"{ms['mean']:{fmt}} ± {ms['sem']:{fmt}}"


def render_markdown(r: dict) -> str:
    """results.md for one sweep analysis."""
    cg, rg = r.get("code_git") or {}, r.get("run_git") or {}
    lines = [
        f"# Sweep analysis: {r['system']} / {r['stage']}",
        "",
        (
            f"- system: `{r['system']}` ({r.get('resolution')}); source run directory"
            f" `{r['run_dir']}` (status {r.get('run_status')}, node {r.get('run_node')}, run"
            f" code commit {(rg.get('commit') or 'n/a')[:10]})"
        ),
        f"- analysis: `sepsim analyze sweep` (D49), code commit {(cg.get('commit') or 'n/a')[:10]}"
        + (" (dirty)" if cg.get("dirty") else "")
        + f", {r['generated'][:16].replace('T', ' ')} on {r['generated_on']}",
        (
            f"- windows: steps {r['method']['step_window']}; holds {r['method']['hold_window']};"
            f" SEM from the {r['method']['sem']}"
        ),
    ]
    if r.get("mass_gmol"):
        lines.append(f"- system mass {r['mass_gmol']:.1f} g/mol (from Density × Volume)")
    for n in r.get("notes", []):
        lines.append(f"- note: {n}")
    lines += [
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
    lines += [
        "",
        "## Isothermal compressibility (holds)",
        "",
        (
            "κ_T = (⟨V²⟩ − ⟨V⟩²)/(k_B T ⟨V⟩) over the hold window (NPT iso Nosé–Hoover), T the set"
            " point; SEM = statistical-inefficiency SEM of (V − ⟨V⟩)² (g given)."
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
    f = r.get("fits")
    lines += ["", "## Thermal expansion and classical Cp (fits over the sweep)", ""]
    if not f:
        lines.append("Not enough completed segments for a fit.")
    else:
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
    lines += [
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
    lines += [""] + notes if notes else []
    lines += equilibration_markdown(r, LOCAL_NOTE, CHAIN_NOTE)
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r.get("caveats", [])]
    if r.get("plots"):
        lines += ["", "## Plots", ""]
        for p in r["plots"].values():
            lines += [f"**{p['title']}**", "", f"![{p['title']}]({p['file']})", ""]
    return "\n".join(lines) + "\n"


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


def _f(x, fmt: str = ".2f") -> str:
    return "n/a" if x is None else f"{x:{fmt}}"


def write_results(report: dict, out_dir: Path, render=None) -> None:
    """Write results.json and results.md (``render``, default the sweep report's
    :func:`render_markdown`) atomically into ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in (
        (JSON_NAME, json.dumps(report, indent=1, sort_keys=True, default=_json) + "\n"),
        (MD_NAME, (render or render_markdown)(report)),
    ):
        tmp = out_dir / (name + ".tmp")
        tmp.write_text(text)
        os.replace(tmp, out_dir / name)


def _json(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    raise TypeError(f"not JSON serializable: {type(x).__name__}")
