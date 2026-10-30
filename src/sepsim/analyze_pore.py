"""Pore analysis: `sepsim analyze pore` (D51).

For a finished (or partly finished) dry slit-pore run directory
``results/runs/<system>/pore/`` (deck ``in.pore``, D48: film normal to z, Lz fixed, NVT,
x and y set per T by ``change_box``) this writes ``results.md``, ``results.json`` and PNG
plots into ``results/analysis/<system>/pore/`` (or ``--out``):

- per segment (500 K re-relaxation, the 8 step-cool stages, 14 sweep steps + 4 holds):
  T, Lx, Ly, Pxx, Pyy, Pzz and the surface tension gamma = (Lz/2) [Pzz - (Pxx + Pyy)/2]
  (two surfaces) as mean +- SEM (statistical inefficiency of each series, D26) over the
  second half (re-relaxation, cool stages, steps) or without the first 10% (holds);
  linear fits gamma(T) over the sweep (one point per T, the hold where there is one) and
  over the step-cool, SEM-weighted with the Birge scaling of `sepsim analyze sweep`;
- per hold, from <= ``max_frames`` evenly spaced hold DCD frames: the mass density
  profile rho(z) about the film's mass centre (periodic z; the film may straddle the
  boundary), symmetrized; the interior plateau vs the bulk density at the same T (from
  the bulk system's `analyze sweep` results.json); film thickness from the equimolar
  Gibbs surfaces (M / (rho_plateau A)) and from the 50% crossings; gap = Lz - film; the
  10-90 width per surface and a tanh fit; the clear gap per frame (z extent and the
  closest 3-D approach across the slit) as mean and minimum;
- per hold, by layer (surface: within ``LAYER_A`` of either Gibbs surface on the film
  side or outside it; interior: the rest; assigned at each time origin): backbone-site
  MSD per dimension in-plane ((<dx^2> + <dy^2>)/2) and normal (<dz^2>) from the hold
  DCD and its D46 bursts, the bond P2 autocorrelation and its 1/e time, the bond
  orientation <P2(cos theta_z)> vs z, and <Rg_z^2> vs <Rg_xy^2>/2 of chains whose mass
  centre is in either layer; plus the whole-film results of `analyze sweep`
  (:func:`sepsim.analyze.hold_trajectory`) next to the bulk hold;
- over the sweep grid (one point per T, hold wins; steps from their DCD, second half):
  Gibbs film thickness and interior density vs T (bulk density alongside), alpha_z =
  (1/t_G) dt_G/dT, the imposed in-plane alpha_L and the film alpha_V = alpha_z + 2 alpha_L
  over 25-160, 25-90 and 90-160 C next to the bulk alpha_V, classical Cv = dE/dT, and the
  surface excess energy e_s = (E_pore - (M_pore/M_bulk) E_bulk(T))/(2A) (bulk TotEng from
  the bulk sweep run) against gamma - T dgamma/dT.

Deck and log parsing, the thermo windows and the hold trajectory machinery are those of
:mod:`sepsim.analyze` (D49); profile helpers in :mod:`sepsim.analysis.pore`.
"""

from __future__ import annotations

import datetime as dt
import platform
import re
import warnings
from pathlib import Path

import numpy as np

from sepsim.analysis.lammps_log import read_log
from sepsim.analysis.stats import linear_fit
from sepsim.analysis.units import A3_CM3, ANGSTROM_M, AVOGADRO, KCAL_J
from sepsim.analyze import (
    CHAIN_NOTE,
    FIT_WINDOWS_C,
    HOLD_SKIP,
    LOG_NAME,
    MAX_FRAMES,
    STEP_SKIP,
    AnalyzeError,
    _birge,
    _chi2_red,
    _f,
    _floor_err,
    _log_idx,
    _mean_sd,
    _pm,
    _system_arrays,
    block_convergence,
    draw_plots,
    drift_cell,
    drift_flags,
    equilibration_jobs,
    equilibration_markdown,
    hold_trajectory,
    out_dir_for,
    quantity_convergence,
    segment_convergence,
    segment_thermo,
    sem_vs_block,
    window_stats,
)
from sepsim.progress import (
    ATM_A_TO_MN_M,
    _block_rows,
    _mean_sem,
    _round,
    deck_system,
    find_deck,
    load_json,
    parse_deck,
)
from sepsim.run import CODE_DIR, MANIFEST_NAME, git_info

VERSION = 1
LAYER_A = 15.0  # surface layer depth from each Gibbs surface (film side), Angstrom
PROFILE_BIN_A = 0.5  # density profile bin, Angstrom (rounded so Lz holds an even number)
P2Z_BIN_A = 2.0  # <P2(cos theta_z)> vs |z| bin, Angstrom
P2Z_MIN_FRACTION = 0.005  # ... bins with fewer bonds than this fraction of the fullest are dropped
MAX_ORIGINS = 200  # time origins per lag (evenly spaced) for the layer MSD / P2
BURST_ORIGINS = 50  # ... per burst
REPORT_LAGS_PS = (10.0, 100.0, 1000.0)  # MSD table lags (plus the longest lag)
BURST_LAGS = (1, 2, 3, 5, 7, 10, 14, 20, 30, 50, 70, 99)  # burst frames (0.1 ps)
CLASSES = ("interior", "surface")  # layer class indices 0, 1
# pressure x length -> mN/m per LAMMPS units style (real: atm A; metal: bar A)
PL_TO_MN_M = {"real": ATM_A_TO_MN_M, "metal": 1e5 * 1e-10 * 1e3}

_UNITS = re.compile(r"^\s*units\s+(\w+)")


def deck_units(deck: Path) -> str | None:
    """The deck's ``units`` style (first ``units`` command)."""
    for line in Path(deck).read_text(errors="replace").splitlines():
        if m := _UNITS.match(line):
            return m.group(1)
    return None


# --------------------------------------------------------------------------- thermo


def gamma_series(thermo: dict, factor: float) -> np.ndarray:
    """Instantaneous gamma = (Lz/2) [Pzz - (Pxx + Pyy)/2] (two surfaces), mN/m."""
    p_lat = 0.5 * (thermo["Pxx"] + thermo["Pyy"])
    return 0.5 * thermo["Lz"] * (thermo["Pzz"] - p_lat) * factor


def pore_window_stats(thermo: dict, skip: float, factor: float) -> dict:
    """:func:`sepsim.analyze.window_stats` plus Lx, Ly, Pxx, Pyy, Pzz, PotEng and TotEng
    (mean +- SEM) and gamma (mean +- SEM of the instantaneous series) over the same rows."""
    out = window_stats(thermo, skip)
    k = int(np.floor(skip * len(thermo.get("Step", ()))))
    for key, col in (
        ("lx", "Lx"),
        ("ly", "Ly"),
        ("pxx", "Pxx"),
        ("pyy", "Pyy"),
        ("pzz", "Pzz"),
        ("pe", "PotEng"),
        ("etotal", "TotEng"),
    ):
        if col in thermo:
            out[key] = _mean_sem(thermo[col][k:], _block_rows(thermo))
    if all(c in thermo for c in ("Pxx", "Pyy", "Pzz", "Lz")):
        out["gamma"] = _mean_sem(gamma_series(thermo, factor)[k:], _block_rows(thermo))
    return out


def _kind(seg) -> str | None:
    if seg.sweep_index is not None and not seg.vdos:
        return seg.sweep_kind
    if seg.cool_step is not None:
        return "cool"
    if seg.command == "run" and seg.ensemble == "nvt":
        return "relax"
    return None


def gamma_fit(points: list[dict]) -> dict | None:
    """SEM-weighted linear fit of gamma vs T (K), errors scaled by the Birge ratio;
    ``points`` rows with ``t_set_c`` and stats.gamma. None if < 3 points."""
    pts = [p for p in points if (p.get("stats") or {}).get("gamma")]
    if len(pts) < 3:
        return None
    t = np.array([p["t_set_c"] + 273.15 for p in pts])
    g = np.array([p["stats"]["gamma"]["mean"] for p in pts])
    e = _floor_err(np.array([p["stats"]["gamma"]["sem"] for p in pts]))
    slope, icpt, s_err, _ = linear_fit(t, g, e)
    chi = _chi2_red(t, g, e, slope, icpt)
    return {
        "n": len(pts),
        "window_c": [float(t.min() - 273.15), float(t.max() - 273.15)],
        "dgamma_dT_mN_mK": slope,
        "err": s_err * _birge(chi),
        "err_unscaled": s_err,
        "gamma_25c_mN_m": slope * 298.15 + icpt,
        "chi2_red": chi,
        "line": [slope, icpt],
    }


def _per_t(rows: list[dict]) -> list[dict]:
    """One row per set T (the latest, so a hold wins over its step), sorted by T."""
    pts: dict[float, dict] = {}
    for r in rows:
        if (r.get("stats") or {}).get("gamma"):
            pts[round(r["t_set_c"], 3)] = r
    return [pts[t] for t in sorted(pts)]


# --------------------------------------------------------------------------- bulk reference


def find_bulk_analysis(manifest: dict | None, root: str | Path = "results/analysis") -> Path | None:
    """The bulk `analyze sweep` results.json for a pore: the bulk sweep the D48 lateral
    table was read from (``pore.lateral.sources.sweep``), else the first system of the
    source chain (wide pore, bulk, replicate source) with ``<root>/<id>/sweep/``."""
    root = Path(root)
    cands = []
    src = (((manifest or {}).get("pore") or {}).get("lateral") or {}).get("sources") or {}
    if (sw := src.get("sweep")) and sw.get("run_dir"):
        cands.append((Path(sw["run_dir"]).parent.name, Path(sw["run_dir"]).name))
    s = (manifest or {}).get("source")
    while s:
        if s.get("id"):
            cands.append((s["id"], "sweep"))
        s = s.get("source")
    if rid := ((manifest or {}).get("replicate") or {}).get("source_id"):
        cands.append((rid, "sweep"))
    for sid, stage in cands:
        p = root / sid / stage / "results.json"
        if p.is_file():
            return p
    return None


def _bulk_at(bulk: dict | None, t_c: float) -> dict:
    """Bulk hold (density, per-dimension MSD curve, P2 1/e, Rg) at the set T t_c."""
    if not bulk:
        return {}
    out: dict = {}
    for s in bulk.get("segments", []):  # latest segment at T, so the hold wins
        if abs(s["t_set_c"] - t_c) < 1e-6 and (s.get("stats") or {}).get("density"):
            out["density"] = s["stats"]["density"]
    for h in bulk.get("holds", []):
        tr = h.get("traj") or {}
        if abs(h["t_c"] - t_c) < 1e-6 and tr.get("available"):
            c = tr["curves"]
            out.update(
                msd_lag_ps=c["msd_lag_ps"],
                msd_per_dim_A2=[v / 3.0 for v in c["msd_A2"]],
                p2_t_1e_ps=tr["p2"]["t_1e_ps"],
                rg_A=tr["rg"]["rg_A"],
                ree_A=tr["ree"]["ree_A"],
                msd_at_max_A2=tr["segment_msd"]["msd_at_max_A2"],
                com_msd_at_max_A2=tr["com_msd"]["msd_at_max_A2"],
                lag_max_ps=tr["segment_msd"]["lag_max_ps"],
                c_n=tr["c_n"]["plateau"],
            )
    return out


def _interp_log(lags, vals, lag: float) -> float | None:
    t, v = np.asarray(lags, dtype=float), np.asarray(vals, dtype=float)
    ok = (t > 0) & (v > 0)
    t, v = t[ok], v[ok]
    if not len(t) or lag < t[0] * (1 - 1e-9) or lag > t[-1] * (1 + 1e-9):
        return None
    return float(np.exp(np.interp(np.log(lag), np.log(t), np.log(v))))


# --------------------------------------------------------------------------- trajectories


def read_positions(path: Path, n_atoms: int, masses: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """All frames of a DCD as float32 (n_frames, n_atoms, 3), the system's mass centre
    removed per frame, and the box lengths (n_frames, 3)."""
    from MDAnalysis.coordinates.DCD import DCDReader

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        reader = DCDReader(str(path))
    try:
        if reader.n_atoms != n_atoms:
            raise ValueError(f"{path.name}: {reader.n_atoms} atoms, data.lmp has {n_atoms}")
        x = np.empty((reader.n_frames, n_atoms, 3), dtype=np.float32)
        box = np.empty((reader.n_frames, 3))
        w = masses / masses.sum()
        for k, ts in enumerate(reader):
            p = ts.positions.astype(float)
            x[k] = p - w @ p
            box[k] = ts.dimensions[:3]
    finally:
        reader.close()
    if not len(x):
        raise ValueError(f"{path.name}: no frames")
    return x, box


def _centres(x: np.ndarray, box: np.ndarray, masses: np.ndarray) -> np.ndarray:
    from sepsim.analysis.pore import film_centre

    return np.array([film_centre(x[k, :, 2], box[k, 2], masses) for k in range(len(x))])


def _labels(z: np.ndarray, centres: np.ndarray, lz: np.ndarray, h: float) -> np.ndarray:
    """Layer class (0 interior, 1 surface) of points z (n_frames, n) per frame."""
    from sepsim.analysis.pore import relative_z, surface_layer

    out = np.empty(z.shape, dtype=np.int8)
    for s in range(0, len(z), 100):  # frame chunks bound the float64 temporaries
        k = slice(s, s + 100)
        zr = relative_z(z[k], centres[k, None], lz[k, None])
        out[k] = surface_layer(zr, h, LAYER_A)
    return out


def _bonds(sys_arr: dict) -> tuple[np.ndarray, np.ndarray]:
    """Backbone bonds as atom rows (a -> b)."""
    rows, ch = sys_arr["bb_rows"], sys_arr["chains"]
    a = np.concatenate([rows[c[:-1]] for c in ch])
    b = np.concatenate([rows[c[1:]] for c in ch])
    return a, b


def film_profile(x, box, centres, masses, pick, use=None, frame_ps: float = 1.0) -> dict:
    """Density profile, Gibbs/50% film thickness, interfacial widths and clear gap over
    the frames ``pick[use]`` (the analysis window; default all), and per frame of
    ``pick`` the Gibbs thickness, gap, interior density and clear gap (time series, with
    a halves-of-window drift test of the thickness)."""
    from sepsim.analysis.pore import (
        clear_gap,
        density_profile,
        interface_10_90,
        plateau_density,
        pore_width,
        relative_z,
        symmetrize,
        tanh_fit,
    )

    lz = float(box[pick[0], 2])
    n_bins = 2 * max(2, round(lz / (2 * PROFILE_BIN_A)))
    prof, gaps = [], []
    for k in pick:
        area = float(box[k, 0] * box[k, 1])
        z, rho = density_profile(
            relative_z(x[k, :, 2], centres[k], box[k, 2]), masses, area, box[k, 2], n_bins
        )
        prof.append(rho)
        gaps.append(clear_gap(x[k], box[k], centres[k]))
    prof = np.array(prof)
    use = np.ones(len(pick), bool) if use is None else np.asarray(use, bool)
    rho = prof[use].mean(axis=0)
    sym = symmetrize(rho)
    rp, t_g = plateau_density(z, sym, LAYER_A)
    inner = np.abs(z) < 0.5 * t_g - LAYER_A
    if inner.sum() < 3:
        inner = np.abs(z) < 0.25 * t_g
    pw = pore_width(z, sym, Lz_A=lz, bulk_density=rp)
    gaps = np.array(gaps)
    rp_f = symmetrize(prof)[:, inner].mean(axis=1)  # per-frame plateau and Gibbs thickness
    tg_f = prof.sum(axis=1) * (z[1] - z[0]) / rp_f
    t_ns = np.asarray(pick) * frame_ps / 1000.0
    series = {
        "t_ns": _round(t_ns),
        "window_ns": float(t_ns[use][0]),
        "film_gibbs_A": _round(tg_f, 4),
        "gap_gibbs_A": _round(box[pick, 2] - tg_f, 4),
        "plateau": _round(rp_f),
        "closest_A": _round(gaps[:, 1], 3),
        "gap_z_A": _round(gaps[:, 0], 3),
    }
    drift = drift_flags({"film_gibbs": tg_f[use]}, 0.0)
    gaps, rp_f, tg_f = gaps[use], rp_f[use], tg_f[use]
    return {
        "series": series,
        "drift": drift,
        "frames": int(use.sum()),
        "lz_A": lz,
        "area_A2": float(np.mean(box[pick[use], 0] * box[pick[use], 1])),
        "bin_A": float(z[1] - z[0]),
        "plateau": _mean_sd(rp_f),
        "film_gibbs_frames": _mean_sd(tg_f),
        "plateau_region_A": float(np.abs(z[inner]).max()),
        "film_gibbs_A": t_g,
        "gap_gibbs_A": lz - t_g,
        "film_50_A": lz - pw.width,
        "gap_50_A": pw.width,
        "interface_10_90": interface_10_90(z, rho, rp),
        "tanh": tanh_fit(z, sym, rp, 0.5 * t_g),
        "gap_z_A": {"mean": float(gaps[:, 0].mean()), "min": float(gaps[:, 0].min())},
        "closest_A": {"mean": float(gaps[:, 1].mean()), "min": float(gaps[:, 1].min())},
        "z_A": _round(z, 3),
        "rho_sym": _round(sym),
    }


def _orientation_and_size(x, box, centres, sys_arr, pick, h) -> dict:
    """<P2(cos theta_z)> of backbone bonds vs |z| and per layer; <Rg_z^2> and
    <Rg_xy^2>/2 of chains by the layer of their mass centre; over frames ``pick``."""
    from sepsim.analysis.mobility import unit_bonds
    from sepsim.analysis.pore import relative_z, surface_layer

    a, b = _bonds(sys_arr)
    mol, m = sys_arr["molecule"], sys_arr["masses"]
    mtot = sys_arr["mol_mass"]
    n_mol = len(mtot)
    zmax = 0.5 * float(box[pick, 2].max())
    edges = np.arange(0.0, zmax + P2Z_BIN_A, P2Z_BIN_A)
    s_bin, n_bin = np.zeros(len(edges) - 1), np.zeros(len(edges) - 1)
    p2_cls = [[], []]
    rg = {c: {"z": [], "xy": [], "n": []} for c in CLASSES}
    for k in pick:
        xf = x[k].astype(float)
        lz = box[k, 2]
        u = unit_bonds(xf, a, b)
        p2 = 1.5 * u[:, 2] ** 2 - 0.5
        mid = relative_z(0.5 * (xf[a, 2] + xf[b, 2]), centres[k], lz)
        idx = np.digitize(np.abs(mid), edges) - 1
        ok = (idx >= 0) & (idx < len(s_bin))
        s_bin += np.bincount(idx[ok], p2[ok], minlength=len(s_bin))
        n_bin += np.bincount(idx[ok], minlength=len(s_bin))
        surf = surface_layer(mid, h, LAYER_A)
        for c, sel in ((0, ~surf), (1, surf)):
            p2_cls[c].append(p2[sel].mean() if sel.any() else np.nan)
        com = np.stack(
            [np.bincount(mol, m * xf[:, j], minlength=n_mol) / mtot for j in range(3)], axis=1
        )
        d = xf - com[mol]
        rz = np.bincount(mol, m * d[:, 2] ** 2, minlength=n_mol) / mtot
        rxy = np.bincount(mol, m * (d[:, 0] ** 2 + d[:, 1] ** 2), minlength=n_mol) / mtot / 2
        cs = surface_layer(relative_z(com[:, 2], centres[k], lz), h, LAYER_A)
        for c, sel in ((CLASSES[0], ~cs), (CLASSES[1], cs)):
            rg[c]["n"].append(int(sel.sum()))
            rg[c]["z"].append(rz[sel].mean() if sel.any() else np.nan)
            rg[c]["xy"].append(rxy[sel].mean() if sel.any() else np.nan)
    with np.errstate(invalid="ignore"):
        prof = s_bin / n_bin
    keep = n_bin >= P2Z_MIN_FRACTION * n_bin.max()  # drop sparsely sampled outer bins
    out = {
        "p2z_z_A": _round((0.5 * (edges[1:] + edges[:-1]))[keep], 3),
        "p2z": _round(prof[keep]),
        "p2z_layer": {},
        "rg": {},
    }
    for c, name in enumerate(CLASSES):
        v = np.array(p2_cls[c])
        out["p2z_layer"][name] = _mean_sd(v[~np.isnan(v)]) if np.isfinite(v).any() else None
        r = rg[name]
        z, xy = np.array(r["z"]), np.array(r["xy"])
        ok = ~np.isnan(z)
        out["rg"][name] = {
            "chains_mean": float(np.mean(r["n"])),
            "rg_z2_A2": _mean_sd(z[ok]) if ok.sum() else None,
            "rg_xy2_half_A2": _mean_sd(xy[ok]) if ok.sum() else None,
        }
    return out


def _hold_lags(nf: int) -> np.ndarray:
    top = max(1, nf // 2)
    grid = np.geomspace(1, top, 60).round().astype(int)
    fixed = [k for k in (1, 10, 100, top) if k <= top]
    return np.unique(np.r_[grid, fixed, np.arange(1, min(top, 30) + 1)])


def _curves(sums, counts, p2_sums=None, p2_counts=None):
    """Per class (and pooled 'film') in-plane per-dim, normal MSD and P2 from sums."""
    out = {}
    pooled_s, pooled_c = sums.sum(axis=1), counts.sum(axis=1)
    for name, s, c in [(n, sums[:, k], counts[:, k]) for k, n in enumerate(CLASSES)] + [
        ("film", pooled_s, pooled_c)
    ]:
        with np.errstate(invalid="ignore", divide="ignore"):
            out[name] = {
                "xy": 0.5 * (s[:, 0] + s[:, 1]) / c,
                "z": s[:, 2] / c,
                "count": c,
            }
    if p2_sums is not None:
        with np.errstate(invalid="ignore", divide="ignore"):
            for k, n in enumerate(CLASSES):
                out[n]["p2"] = p2_sums[:, k] / p2_counts[:, k]
            out["film"]["p2"] = p2_sums.sum(axis=1) / p2_counts.sum(axis=1)
    return out


def layer_dynamics(run_dir: Path, seg, sys_arr, x, box, centres, h, frame_ps) -> dict:
    """Layer-split MSD (in-plane per dimension, normal) and bond P2 ACF of the backbone
    sites: hold DCD for lags >= its frame interval, the D46 bursts below it."""
    from sepsim.analysis.chain import decorrelation_time
    from sepsim.analysis.mobility import msd_by_class, p2_by_class, stitch_curves

    rows = sys_arr["bb_rows"]
    a, b = _bonds(sys_arr)
    lz = box[:, 2]
    nf = len(x)
    lags = _hold_lags(nf)
    bb = x if np.array_equal(rows, np.arange(x.shape[1])) else x[:, rows]
    lab = _labels(bb[..., 2], centres, lz, h)
    blab = _labels(0.5 * (x[:, a, 2] + x[:, b, 2]), centres, lz, h)
    hs, hc = msd_by_class(bb, lab, lags, 2, MAX_ORIGINS)
    ps, pc = p2_by_class(x, a, b, blab, lags, 2, MAX_ORIGINS)
    frac = float(lab.mean())
    del lab, blab
    hold = _curves(hs, hc, ps, pc)
    hold_lags = lags * frame_ps

    bursts = [(f, n) for f, n in zip(seg.dcd, seg.dump_every, strict=True) if "_burst" in f]
    bs = bc = bps = bpc = b_lags = None
    used, b_ps = 0, None
    for f, n in bursts:
        path = run_dir / f
        if not path.is_file():
            continue
        try:
            xb, boxb = read_positions(path, x.shape[1], sys_arr["masses"])
        except (OSError, ValueError):
            continue
        if len(xb) < 3:
            continue
        cb = _centres(xb, boxb, sys_arr["masses"])
        bl = np.array([k for k in BURST_LAGS if k < len(xb)])
        bbb = xb if bb is x else xb[:, rows]
        s1, c1 = msd_by_class(bbb, _labels(bbb[..., 2], cb, boxb[:, 2], h), bl, 2, BURST_ORIGINS)
        mid = 0.5 * (xb[:, a, 2] + xb[:, b, 2])
        s2, c2 = p2_by_class(xb, a, b, _labels(mid, cb, boxb[:, 2], h), bl, 2, BURST_ORIGINS)
        if bs is None:
            bs, bc, bps, bpc, b_lags = s1, c1, s2, c2, bl
        elif len(bl) == len(b_lags):
            bs, bc, bps, bpc = bs + s1, bc + c1, bps + s2, bpc + c2
        else:
            continue
        b_ps = n * seg.dt_fs / 1000.0
        used += 1
    out: dict = {"bursts_used": used, "surface_fraction": frac, "layer_A": LAYER_A}
    burst = _curves(bs, bc, bps, bpc) if used else None
    curves = {}
    for name in (*CLASSES, "film"):
        cur = {}
        for key in ("xy", "z", "p2"):
            if burst:
                lg, v, _ = stitch_curves(
                    b_lags * b_ps, burst[name][key], hold_lags, hold[name][key]
                )
            else:
                lg, v = hold_lags, hold[name][key]
            cur[key] = (np.asarray(lg), np.asarray(v))
        curves[name] = cur
    for name, cur in curves.items():
        lg, vxy = cur["xy"]
        _, vz = cur["z"]
        at = {}
        for lag in (*REPORT_LAGS_PS, float(hold_lags[-1])):
            k = np.flatnonzero(np.isclose(lg, lag, rtol=1e-6))
            if len(k):
                at[f"{lag:g}"] = {"xy": float(vxy[k[0]]), "z": float(vz[k[0]])}
        lp, vp = cur["p2"]
        t_1e = decorrelation_time(np.r_[0.0, lp], np.r_[1.0, vp])
        idx = _log_idx(lg)
        out[name] = {
            "msd_at": at,
            "p2_t_1e_ps": t_1e,
            "p2_at_max": float(vp[-1]),
            "curves": {
                "lag_ps": _round(lg[idx]),
                "xy_A2": _round(vxy[idx]),
                "z_A2": _round(vz[idx]),
                "p2_lag_ps": _round(lp[_log_idx(lp)]),
                "p2": _round(vp[_log_idx(lp)]),
            },
        }
    out["lag_max_ps"] = float(hold_lags[-1])
    out["origins_per_lag"] = {"hold": MAX_ORIGINS, "burst": BURST_ORIGINS}
    return out


def _window_frames(nf: int, skip: float, max_frames: int) -> np.ndarray:
    """Up to ``max_frames`` evenly spaced frames after the first ``skip`` fraction."""
    k = int(np.floor(skip * nf))
    return np.unique(np.linspace(k, nf - 1, min(nf - k, max_frames)).round().astype(int))


def step_profile(run_dir: Path, seg, sys_arr: dict, max_frames: int = MAX_FRAMES) -> dict:
    """Film thickness and plateau density of a sweep step from its DCD (second half)."""
    dcd = [f for f in seg.dcd if "_burst" not in f]
    if not dcd or not (run_dir / dcd[0]).is_file():
        return {"available": False, "notes": [f"{dcd[0] if dcd else 'step DCD'} not found"]}
    masses = sys_arr["masses"]
    x, box = read_positions(run_dir / dcd[0], sys_arr["n_atoms"], masses)
    if len(x) < 4:
        return {"available": False, "notes": [f"{dcd[0]}: only {len(x)} frames"]}
    every = seg.dump_every[seg.dcd.index(dcd[0])]
    pick = _window_frames(len(x), 0.0, max_frames)
    use = pick >= int(np.floor(STEP_SKIP * len(x)))
    prof = film_profile(
        x, box, _centres(x, box, masses), masses, pick, use, every * seg.dt_fs / 1000.0
    )
    for k in ("z_A", "rho_sym", "tanh", "interface_10_90"):
        prof.pop(k)
    return {"available": True, "dcd": dcd[0], **prof}


def pore_hold(run_dir: Path, seg, sys_arr: dict, max_frames: int = MAX_FRAMES) -> dict:
    """Density profile, gap, layer mobility and conformation of one pore hold."""
    names = list(zip(seg.dcd, seg.dump_every, strict=True))
    hold = [(f, n) for f, n in names if "_burst" not in f]
    out: dict = {"available": False, "notes": []}
    if not hold or not (run_dir / hold[0][0]).is_file():
        name = hold[0][0] if hold else "hold DCD"
        out["notes"].append(f"trajectory not available ({name} not found)")
        return out
    dcd, every = hold[0]
    frame_ps = every * seg.dt_fs / 1000.0
    masses = sys_arr["masses"]
    x, box = read_positions(run_dir / dcd, sys_arr["n_atoms"], masses)
    nf = len(x)
    if nf < 6:
        out["notes"].append(f"trajectory not available ({dcd}: only {nf} frames)")
        return out
    centres = _centres(x, box, masses)
    pick = _window_frames(nf, 0.0, max_frames)
    use = pick >= int(np.floor(HOLD_SKIP * nf))
    prof = film_profile(x, box, centres, masses, pick, use, frame_ps)
    pick = pick[use]
    h = 0.5 * prof["film_gibbs_A"]
    out.update(
        available=True,
        dcd=dcd,
        frames=nf,
        frame_ps=frame_ps,
        hold_ns=(nf - 1) * frame_ps / 1000,
        profile=prof,
        conformation=_orientation_and_size(x, box, centres, sys_arr, pick, h),
        layers=layer_dynamics(run_dir, seg, sys_arr, x, box, centres, h, frame_ps),
    )
    if not out["layers"]["bursts_used"]:
        out["notes"].append("no burst DCDs used: layer lags from the hold DCD only")
    return out


# --------------------------------------------------------------------------- thermal (sweep grid)

KCAL_MOL_A2_TO_MJ_M2 = KCAL_J / AVOGADRO / ANGSTROM_M**2 * 1e3  # (kcal/mol)/A^2 -> mJ/m^2


def bulk_energies(bulk: dict, manifest: dict | None) -> dict[float, dict]:
    """TotEng and PotEng (mean +- SEM, the `analyze sweep` windows) per set T of the bulk
    sweep (latest segment per T, so holds win), from the bulk run directory named in its
    results.json (else the pore manifest's lateral sweep source)."""
    cands = [bulk.get("run_dir")]
    src = (((manifest or {}).get("pore") or {}).get("lateral") or {}).get("sources") or {}
    cands.append((src.get("sweep") or {}).get("run_dir"))
    run = next((Path(c) for c in cands if c and (Path(c) / LOG_NAME).is_file()), None)
    if run is None:
        raise AnalyzeError("bulk sweep run directory with log.lammps not found")
    deck = find_deck(run, load_json(run / MANIFEST_NAME))
    if deck is None:
        raise AnalyzeError(f"{run}: no deck")
    segs = parse_deck(deck)
    if re.search(r"^\s*pair_modify\b.*\btail\s+yes", deck.read_text(), re.MULTILINE):
        raise AnalyzeError(f"{deck}: bulk uses a tail correction, the pore does not (D48)")
    out: dict[float, dict] = {}
    for seg, th in zip(segs, segment_thermo(segs, read_log(run / LOG_NAME)), strict=True):
        if seg.sweep_index is None or seg.vdos or th is None or len(th.get("Step", ())) < 6:
            continue
        k = int(np.floor((HOLD_SKIP if seg.sweep_kind == "hold" else STEP_SKIP) * len(th["Step"])))
        out[round(seg.t_c, 3)] = {
            key: _mean_sem(th[col][k:], _block_rows(th))
            for key, col in (("etotal", "TotEng"), ("pe", "PotEng"))
        } | {"run_dir": str(run)}
    return out


def _ms(x: dict | None) -> tuple[float, float] | None:
    return None if not x else (x["mean"], x["sem"] or 0.0)


def pore_thermal(points, film, bulk, energies, mass, gamma_fits) -> dict:
    """Film thickness, plateau density, energy and surface excess energy per set T of the
    sweep (``points``: one row per T, hold wins; ``film``: profile per sweep index), and
    the fits per window of FIT_WINDOWS_C: alpha_z = (1/h) dh/dT (Gibbs thickness h),
    alpha_L from the imposed box area, the film's alpha_V = alpha_z + 2 alpha_L, and
    classical Cv = dE/dT (TotEng), next to the bulk alpha_V and Cp."""
    from sepsim.analysis.thermo import (
        heat_capacity_classical,
        thermal_expansion,
        thermal_expansion_inplane,
    )

    slope = (gamma_fits.get("sweep") or {}).get("dgamma_dT_mN_mK")
    m_bulk = (bulk or {}).get("mass_gmol")
    rows = []
    for p in points:
        st, pr = p["stats"], film.get(p["index"])
        t_c = p["t_set_c"]
        area = st["lx"]["mean"] * st["ly"]["mean"]
        row = {
            "index": p["index"],
            "kind": p["kind"],
            "t_c": t_c,
            "area_A2": area,
            "lx_A": st["lx"]["mean"],
            "etotal": st.get("etotal"),
            "pe": st.get("pe"),
            "gamma": st.get("gamma"),
        }
        if pr:
            row.update(film_gibbs_A=pr["film_gibbs_frames"], plateau=pr["plateau"])
        bd = _bulk_at(bulk, t_c).get("density")
        if bd:
            row["bulk_density"] = bd
        eb = (energies or {}).get(round(t_c, 3))
        if eb and eb.get("etotal") and st.get("etotal") and mass and m_bulk:
            f = mass / m_bulk
            ep, eb_ = _ms(st["etotal"]), _ms(eb["etotal"])
            conv = KCAL_MOL_A2_TO_MJ_M2 / (2 * area)
            row["e_s_mJ_m2"] = {
                "mean": (ep[0] - f * eb_[0]) * conv,
                "sem": float(np.hypot(ep[1], f * eb_[1])) * conv,
            }
        if slope is not None and st.get("gamma"):
            row["gamma_minus_TdgdT"] = st["gamma"]["mean"] - (t_c + 273.15) * slope
        rows.append(row)
    out: dict = {"points": rows, "alpha": [], "cv": [], "notes": []}
    if not all("e_s_mJ_m2" in r for r in rows):
        why = (
            "no bulk energies"
            if not energies
            else "system masses unknown"
            if not (mass and m_bulk)
            else "TotEng missing in the pore or bulk thermo, or a bulk T missing"
        )
        out["notes"].append(f"surface excess energy not computed at every T: {why}")
    if slope is not None:
        out["surface_entropy_mJ_m2K"] = {
            "mean": -slope,
            "err": gamma_fits["sweep"]["err"],
        }
    bulk_fit = {
        tuple(a["window_c"]): a for a in ((bulk or {}).get("fits") or {}).get("alpha_V", [])
    }
    bulk_cp = {tuple(a["window_c"]): a for a in ((bulk or {}).get("fits") or {}).get("cp", [])}
    for lo, hi in FIT_WINDOWS_C:
        win = (lo + 273.15 - 1e-6, hi + 273.15 + 1e-6)
        sel = [r for r in rows if lo - 1e-6 <= r["t_c"] <= hi + 1e-6]
        if len(sel) < 3:
            out["notes"].append(f"{lo:g}-{hi:g} C: fewer than 3 temperatures, no fit")
            continue
        t = np.array([r["t_c"] + 273.15 for r in sel])
        a = thermal_expansion_inplane(t, np.array([r["area_A2"] for r in sel]))
        b = bulk_fit.get((lo, hi)) or {}
        al = {
            "window_c": [lo, hi],
            "n": len(sel),
            "alpha_L_per_K": a.alpha_L,
            "bulk_alpha_V_per_K": b.get("alpha_V_per_K"),
            "bulk_alpha_V_err": b.get("err"),
        }
        hs = [r for r in sel if r.get("film_gibbs_A")]
        if len(hs) == len(sel):
            h = np.array([r["film_gibbs_A"]["mean"] for r in hs])
            he = _floor_err(np.array([r["film_gibbs_A"]["sem"] or 0.0 for r in hs]))
            te = thermal_expansion(t, h, he, T_window=win)
            sl, ic, _, _ = linear_fit(t, h, he)
            chi = _chi2_red(t, h, he, sl, ic)
            al.update(
                alpha_z_per_K=te.alpha_V,
                alpha_z_err=te.alpha_V_err * _birge(chi),
                alpha_z_err_unscaled=te.alpha_V_err,
                chi2_red=chi,
                h_mean_A=te.V_mean,
                line=[sl, ic],
                alpha_V_film_per_K=te.alpha_V + 2 * a.alpha_L,
            )
        else:
            out["notes"].append(f"{lo:g}-{hi:g} C: film thickness missing at some T, no α_z")
        out["alpha"].append(al)
        es = [r for r in sel if r.get("etotal")]
        if mass and len(es) == len(sel):
            e = np.array([r["etotal"]["mean"] for r in es])
            ee = _floor_err(np.array([r["etotal"]["sem"] or 0.0 for r in es]))
            cv = heat_capacity_classical(t, e, mass, ee, T_window=win)
            sl, ic, _, _ = linear_fit(t, e, ee)
            chi = _chi2_red(t, e, ee, sl, ic)
            bc = bulk_cp.get((lo, hi)) or {}
            out["cv"].append(
                {
                    "window_c": [lo, hi],
                    "n": len(sel),
                    "cv_J_gK": cv.cp_JgK,
                    "err": cv.cp_JgK_err * _birge(chi),
                    "chi2_red": chi,
                    "bulk_cp_J_gK": bc.get("cp_J_gK"),
                    "bulk_cp_err": bc.get("err"),
                }
            )
    return out


# --------------------------------------------------------------------------- report


def analyze_pore(
    run_dir: str | Path,
    out: str | Path | None = None,
    systems: str | Path = "systems",
    max_frames: int = MAX_FRAMES,
    traj: bool = True,
    plots: bool = True,
    bulk_analysis: str | Path | None = None,
) -> tuple[dict, Path]:
    """Analyse a pore run directory; returns (report, output directory)."""
    import yaml

    run_dir = Path(run_dir)
    manifest = load_json(run_dir / MANIFEST_NAME)
    deck = find_deck(run_dir, manifest)
    if deck is None:
        raise AnalyzeError(f"{run_dir}: no deck (in.*) found")
    if deck.name.split(".", 1)[1] != "pore":
        raise AnalyzeError(f"{run_dir}: deck {deck.name} is not a pore run (in.pore)")
    if not (run_dir / LOG_NAME).is_file():
        raise AnalyzeError(f"{run_dir}: no {LOG_NAME}")
    units = deck_units(deck) or "lj"
    if units not in PL_TO_MN_M:
        raise AnalyzeError(f"{run_dir}: units {units} not supported (real or metal)")
    factor = PL_TO_MN_M[units]
    system, resolution = deck_system(deck)
    system = system or run_dir.resolve().parent.name
    out_dir = out_dir_for(run_dir, system, out)
    system_dir = Path(systems) / system
    man_path = system_dir / "manifest.yaml"
    sys_man = yaml.safe_load(man_path.read_text()) if man_path.is_file() else None
    pore = (sys_man or {}).get("pore") or {}
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
        "units": units,
        "pore": {
            k: pore.get(k)
            for k in (
                "nominal_width_nm",
                "wall_thickness_angstrom",
                "slab_mass_g_mol",
                "lz_new_angstrom",
                "replicate_z",
            )
        },
        "method": {
            "step_window": f"second half ({STEP_SKIP:.0%} of rows dropped)",
            "hold_window": f"without the first {HOLD_SKIP:.0%} of rows",
            "sem": "statistical inefficiency (D26)",
            "max_frames": max_frames,
            "layer_A": LAYER_A,
            "profile_bin_A": PROFILE_BIN_A,
        },
        "notes": [],
    }
    if sys_man is None:
        report["notes"].append(f"no {man_path}: nominal width and source chain unknown")
    rows, eq, conv_by_segment = [], [], {}
    for seg, th in zip(segments, thermo, strict=True):
        kind = _kind(seg)
        if kind is None or seg.t_target_k is None:
            continue
        row = {
            "index": seg.sweep_index,
            "segment": seg.index,
            "name": seg.name,
            "kind": kind,
            "t_set_c": seg.t_c if seg.t_c is not None else seg.t_target_k - 273.15,
            "t_k": seg.t_target_k,
            "done": th is not None,
        }
        if th is not None and len(th.get("Step", ())) >= 6:
            skip = HOLD_SKIP if kind == "hold" else STEP_SKIP
            row["stats"] = pore_window_stats(th, skip, factor)
            main = {"pe": th["PotEng"]} if "PotEng" in th else {}
            if all(c in th for c in ("Pxx", "Pyy", "Pzz", "Lz")):
                main["gamma"] = gamma_series(th, factor)
            blk = _block_rows(th)
            row["drift"] = drift_flags(main, skip, blk)
            if kind == "hold":
                row["convergence"] = {k: block_convergence(v, skip, blk) for k, v in main.items()}
            cols = {"T": th["Temp"]} if "Temp" in th else {}
            cols |= {k: th[c] for k, c in (("pe", "PotEng"), ("etotal", "TotEng")) if c in th}
            if "gamma" in main:
                cols |= {"gamma": main["gamma"], "pzz": th["Pzz"]}
            if "Time" in th:
                eq.append(segment_convergence(row["name"], kind, th, skip, cols))
                conv_by_segment[seg.index] = eq[-1]
        rows.append(row)
    report["segments"] = rows
    missing = [r["name"] for r in rows if not r["done"]]
    if missing:
        report["notes"].append(f"{len(missing)} segment(s) not complete: {', '.join(missing)}")
    sweep_pts = _per_t([r for r in rows if r["kind"] in ("step", "hold") and r["done"]])
    cool_pts = _per_t([r for r in rows if r["kind"] == "cool" and r["done"]])
    report["fits"] = {"sweep": gamma_fit(sweep_pts), "cool": gamma_fit(cool_pts)}
    report["fit_points_c"] = [p["t_set_c"] for p in sweep_pts]

    bulk_path = Path(bulk_analysis) if bulk_analysis else find_bulk_analysis(sys_man)
    bulk = load_json(bulk_path) if bulk_path else None
    report["bulk_analysis"] = str(bulk_path) if bulk_path else None
    if bulk is None:
        report["notes"].append("bulk analysis results.json not found: no bulk comparison")
    else:
        report["bulk_system"] = bulk.get("system")

    sys_arr = None
    if traj:
        try:
            sys_arr = _system_arrays(system_dir)
        except (OSError, ValueError, KeyError) as exc:
            report["notes"].append(f"system {system_dir} not usable: {exc}")
    seg_by_index = {s.sweep_index: s for s in segments if s.sweep_kind == "hold" and not s.vdos}
    seg_by_step = {s.sweep_index: s for s in segments if s.sweep_kind == "step" and not s.vdos}
    holds = []
    for r in rows:
        if r["kind"] != "hold":
            continue
        h = {"index": r["index"], "t_c": r["t_set_c"], "bulk": _bulk_at(bulk, r["t_set_c"])}
        if not traj:
            h["traj"] = {"available": False, "notes": ["trajectory analysis skipped (--no-traj)"]}
        elif sys_arr is None:
            h["traj"] = {"available": False, "notes": ["trajectory not available (no system)"]}
        elif not r["done"]:
            h["traj"] = {"available": False, "notes": ["hold not complete"]}
        else:
            seg = seg_by_index[r["index"]]
            try:
                h["traj"] = pore_hold(run_dir, seg, sys_arr, max_frames)
                if h["traj"]["available"]:
                    h["film"] = hold_trajectory(run_dir, seg, sys_arr, max_frames)
            except (OSError, ValueError) as exc:
                h["traj"] = {"available": False, "notes": [f"trajectory failed: {exc}"]}
        holds.append(h)
    report["holds"] = holds
    mass = next(
        (
            float(r["stats"]["density"]["mean"] * r["stats"]["volume"]["mean"] * AVOGADRO * A3_CM3)
            for r in rows
            if (r.get("stats") or {}).get("density") and r["stats"].get("volume")
        ),
        None,
    )
    report["mass_gmol"] = mass
    film = {h["index"]: h["traj"].get("profile") for h in holds if h["traj"].get("available")}
    for r in rows:
        if r["kind"] != "step" or not r["done"] or sys_arr is None:
            continue
        try:
            sp = step_profile(run_dir, seg_by_step[r["index"]], sys_arr, max_frames)
        except (OSError, ValueError) as exc:
            sp = {"available": False, "notes": [f"step trajectory failed: {exc}"]}
        r["profile"] = sp
        if sp["available"]:
            film[r["index"]] = sp
    for r in rows:
        if r["index"] in film and r["kind"] in ("step", "hold"):
            r.setdefault("drift", {}).update(film[r["index"]].get("drift") or {})
            c = conv_by_segment.get(r["segment"])
            se = film[r["index"]].get("series")
            if c and se:  # film quantities per DCD frame, on the thermo time axis
                t = c["t_start_ps"] + np.asarray(se["t_ns"]) * 1000.0
                skip = HOLD_SKIP if r["kind"] == "hold" else STEP_SKIP
                for q in ("film_gibbs_A", "gap_gibbs_A", "plateau", "closest_A"):
                    c["quantities"][q] = quantity_convergence(t, se[q], skip)
                    if r["kind"] == "hold":
                        c["sem_vs_block"][q] = sem_vs_block(t, se[q], skip)
    energies = None
    if bulk is not None:
        try:
            energies = bulk_energies(bulk, sys_man)
        except (AnalyzeError, OSError, ValueError) as exc:
            report["notes"].append(f"bulk energies not available: {exc}")
    report["thermal"] = pore_thermal(sweep_pts, film, bulk, energies, mass, report["fits"])
    caveats = [
        (
            "γ uses a plain LJ cutoff without tail correction (D44/D48: `pair_modify tail no`,"
            " CG 15 Å, UA/AA 14 Å), so it is cutoff-dependent and lower than a full-dispersion"
            " (LJ-PPPM or tail-corrected) value; compare it across our runs, not directly with"
            " experiment."
        ),
        (
            "γ is the mechanical (pressure-tensor) value per surface, (Lz/2)[Pzz − (Pxx+Pyy)/2]"
            " with two film surfaces; the fits are SEM-weighted linear fits in T with errors"
            " scaled by √χ²_red when χ²_red > 1."
        ),
        (
            "The slit is a local patch of a pore wall: real separator pores are 30–100 nm and"
            " their walls semicrystalline (D50); these walls are amorphous (melt-like or"
            " post-shutdown)."
        ),
        (
            f"Layers: surface = within {LAYER_A:g} Å of either Gibbs surface on the film side (or"
            " outside it), interior = the rest, assigned at each time origin; sites leave their"
            " layer at long lags, so long-lag layer MSDs mix layers. MSDs are per dimension:"
            " in-plane (⟨Δx²⟩+⟨Δy²⟩)/2, normal ⟨Δz²⟩, bulk MSD/3 (isotropic)."
        ),
    ]
    caveats.append(
        "Cv = dE/dT (total energy, NVT, per gram) and the surface excess energy are classical:"
        " Cv is not comparable to experiment for the same reasons as the bulk Cp (classical"
        " equipartition; UA/CG drop degrees of freedom). e_s = (E_pore − (M_pore/M_bulk)"
        " E_bulk(T))/(2A) compares the NVT film with the NPT bulk at 1 atm (PV ≈ 0) at the"
        " same set T; the film's lateral box follows the bulk density (D48)."
    )
    if resolution == "cg":
        caveats.append(
            "CG time is not real time: SDK beads move faster than the atoms they"
            " represent, so MSD and P2 times are model times (not rescaled)."
        )
    no_traj = [f"{h['t_c']:g} C" for h in holds if not h["traj"]["available"]]
    if no_traj and traj:
        caveats.append(f"No trajectory results for the hold(s) at {', '.join(no_traj)}.")
    report["caveats"] = caveats
    report["convergence"] = eq
    if plots:
        report["plots"] = make_plots(report, out_dir, eq)
    return report, out_dir


PORE_EQ_PANELS = (
    ("T", "T (K)"),
    ("pe", "PE (kcal/mol)"),
    ("etotal", "E (kcal/mol)"),
    ("gamma", "γ (mN/m)"),
    ("pzz", "Pzz (atm)"),
    ("film_gibbs_A", "t_G (Å)"),
    ("plateau", "interior ρ (g/cm³)"),
)


def make_plots(report: dict, out_dir: Path, eq: list[dict] | None = None) -> dict:
    from sepsim import analyze_plots as ap

    title = f"{report['system']} / {report['stage']}"
    jobs = []
    pts = [r for r in report["segments"] if (r.get("stats") or {}).get("gamma")]
    if pts:
        jobs.append(
            ("gamma_vs_T", "γ vs T", lambda p: ap.gamma_vs_t(p, pts, report["fits"], title))
        )
    th = (report.get("thermal") or {}).get("points") or []
    if any(p.get("film_gibbs_A") for p in th):
        jobs.append(
            (
                "thermal_vs_T",
                "film thickness, interior density and surface energy vs T",
                lambda p: ap.thermal_vs_t(p, report["thermal"], title),
            )
        )
    tr = [h for h in report["holds"] if h["traj"].get("available")]
    if tr:
        nominal = (report.get("pore") or {}).get("nominal_width_nm")
        jobs += [
            ("density_profile", "ρ(z) at the holds", lambda p: ap.density_profiles(p, tr, title)),
            ("gap_vs_T", "gap width vs T", lambda p: ap.gap_vs_t(p, tr, nominal, title)),
            ("msd_layers", "MSD by layer", lambda p: ap.msd_layers(p, tr, title)),
            ("p2_layers", "bond P2 ACF by layer", lambda p: ap.p2_layers(p, tr, title)),
            ("p2z_profile", "⟨P2(cos θ_z)⟩ vs z", lambda p: ap.p2z_profiles(p, tr, title)),
        ]
        fs = [
            {"name": f"hold {h['t_c']:g} C", "series": h["traj"]["profile"]["series"]} for h in tr
        ]
        jobs.append(
            (
                "film_vs_time",
                "film thickness, gap, interior density and closest approach vs time (holds)",
                lambda p: ap.film_vs_time(p, fs, title),
            )
        )
    jobs += equilibration_jobs(eq or [], PORE_EQ_PANELS, title)
    return draw_plots(jobs, report, out_dir)


# --------------------------------------------------------------------------- markdown


def render_markdown(r: dict) -> str:
    """results.md for one pore analysis."""
    cg, rg = r.get("code_git") or {}, r.get("run_git") or {}
    po = r.get("pore") or {}
    lines = [
        f"# Pore analysis: {r['system']} / {r['stage']}",
        "",
        (
            f"- system: `{r['system']}` ({r.get('resolution')}); source run directory"
            f" `{r['run_dir']}` (status {r.get('run_status')}, node {r.get('run_node')}, run"
            f" code commit {(rg.get('commit') or 'n/a')[:10]})"
        ),
        f"- analysis: `sepsim analyze pore` (D51), code commit {(cg.get('commit') or 'n/a')[:10]}"
        + (" (dirty)" if cg.get("dirty") else "")
        + f", {r['generated'][:16].replace('T', ' ')} on {r['generated_on']}",
        (
            f"- pore: nominal width {_f(po.get('nominal_width_nm'), 'g')} nm at 25 °C, wall"
            f" {_f(po.get('wall_thickness_angstrom'), '.1f')} Å at 25 °C, Lz"
            f" {_f(po.get('lz_new_angstrom'), '.2f')} Å (fixed), slab mass"
            f" {_f(po.get('slab_mass_g_mol'), '.0f')} g/mol; units {r['units']}"
        ),
        (
            f"- windows: steps, cool stages and the re-relaxation {r['method']['step_window']};"
            f" holds {r['method']['hold_window']}; SEM from the {r['method']['sem']}"
        ),
        f"- bulk reference: `{r.get('bulk_analysis') or 'not found'}`",
    ]
    for n in r.get("notes", []):
        lines.append(f"- note: {n}")
    lines += [
        "",
        "## Segments: box, pressure tensor and surface tension",
        "",
        (
            "γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface (two surfaces), mean ± SEM of the"
            " instantaneous series."
        ),
        "",
        (
            "| # | segment | T set (°C) | window (ns) | T (°C) | Lx (Å) | Ly (Å) | Pxx (atm) |"
            " Pyy (atm) | Pzz (atm) | γ (mN/m) | drift |"
            if r["units"] == "real"
            else "| # | segment | T set (°C) | window (ns) | T (°C) | Lx (Å) | Ly (Å) | Pxx |"
            " Pyy | Pzz | γ (mN/m) | drift |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in r["segments"]:
        st = s.get("stats") or {}
        idx = s["index"] if s["index"] is not None else ""
        name = s["kind"] if s["kind"] in ("step", "hold") else s["name"]
        if not st:
            lines.append(f"| {idx} | {name} | {s['t_set_c']:g} | not complete | | | | | | | | |")
            continue
        win = f"{st['window_ps'] / 1000:.2f}" if st.get("window_ps") else ""
        lines.append(
            f"| {idx} | {name} | {s['t_set_c']:.4g} | {win} | {_pm(st.get('t_c'), '.2f')} |"
            f" {_mean(st.get('lx'), '.3f')} | {_mean(st.get('ly'), '.3f')} |"
            f" {_pm(st.get('pxx'), '.1f')} | {_pm(st.get('pyy'), '.1f')} |"
            f" {_pm(st.get('pzz'), '.1f')} | {_pm(st.get('gamma'), '.2f')} | {drift_cell(s)} |"
        )
    lines += ["", "## Surface tension vs T", ""]
    f = r.get("fits") or {}
    lines += [
        (
            "SEM-weighted linear fit of γ in T, one point per temperature (hold where there is one);"
            " errors 1σ, scaled by √χ²_red when χ²_red > 1."
        ),
        "",
        "| branch | points | T range (°C) | dγ/dT (mN m⁻¹ K⁻¹) | γ(25 °C) from fit (mN/m) | χ²_red |",
        "|---|---|---|---|---|---|",
    ]
    for key, label in (("sweep", "heating (sweep)"), ("cool", "cooling (step-cool)")):
        g = f.get(key)
        if not g:
            lines.append(f"| {label} | < 3 | | n/a | | |")
            continue
        lines.append(
            f"| {label} | {g['n']} | {g['window_c'][0]:.0f}–{g['window_c'][1]:.0f} |"
            f" {g['dgamma_dT_mN_mK']:.4f} ± {g['err']:.4f} | {g['gamma_25c_mN_m']:.2f} |"
            f" {_f(g['chi2_red'])} |"
        )
    lines += _thermal_markdown(r)
    holds = r["holds"]
    tr = [h for h in holds if h["traj"].get("available")]
    lines += [
        "",
        "## Density profile, film thickness and gap (holds)",
        "",
        (
            "ρ(z) is the mass density about the film's mass centre (periodic z, film centred per"
            f" frame) over ≤ {r['method']['max_frames']} evenly spaced hold frames, symmetrized;"
            f" plateau = mean over |z| < t_G/2 − {r['method']['layer_A']:g} Å (SEM over frames);"
            " t_G = M/(ρ_plateau A) (equimolar Gibbs surfaces), t_50 between the 50%-of-plateau"
            " crossings; gap = Lz − film. Clear gap per frame: z gap = Lz − z extent of all"
            " atoms; closest = smallest 3-D distance across the slit (periodic image)."
        ),
        "",
        (
            "| T (°C) | frames | ρ plateau (g/cm³) | ρ bulk (g/cm³) | Δρ/ρ bulk | t_G (Å) |"
            " t_50 (Å) | gap_G (Å) | gap_50 (Å) | z gap mean / min (Å) | closest mean / min (Å) |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for h in holds:
        t = h["traj"]
        if not t.get("available"):
            lines.append(f"| {h['t_c']:g} | trajectory not available | | | | | | | | | |")
            continue
        p = t["profile"]
        bd = (h.get("bulk") or {}).get("density")
        rel = f"{(p['plateau']['mean'] - bd['mean']) / bd['mean'] * 100:+.2f}%" if bd else "n/a"
        lines.append(
            f"| {h['t_c']:g} | {p['frames']} | {_pm(p['plateau'], '.4f')} |"
            f" {_pm(bd, '.4f') if bd else 'n/a'} | {rel} | {p['film_gibbs_A']:.2f} |"
            f" {p['film_50_A']:.2f} | {p['gap_gibbs_A']:.2f} | {p['gap_50_A']:.2f} |"
            f" {p['gap_z_A']['mean']:.1f} / {p['gap_z_A']['min']:.1f} |"
            f" {p['closest_A']['mean']:.1f} / {p['closest_A']['min']:.1f} |"
        )
    if tr and po.get("nominal_width_nm"):
        t25 = next((h for h in tr if abs(h["t_c"] - 25.0) < 1e-6), None)
        if t25:
            g = t25["traj"]["profile"]["gap_gibbs_A"]
            lines += [
                "",
                (
                    f"Gibbs gap at 25 °C {g / 10:.3f} nm vs nominal {po['nominal_width_nm']:g} nm"
                    " (the nominal width uses the bulk density, D48)."
                ),
            ]
    lines += [
        "",
        (
            "Interfacial width: 10–90 distance of each surface (outermost crossings of 90% and"
            " 10% of the plateau) and the 10–90 width 2 atanh(0.8) δ of a tanh fit"
            " ρ_p/2 [1 − tanh((|z| − h)/δ)] to the symmetrized profile."
        ),
        "",
        "| T (°C) | 10–90 lower (Å) | 10–90 upper (Å) | tanh δ (Å) | tanh 10–90 (Å) | tanh h (Å) |",
        "|---|---|---|---|---|---|",
    ]
    for h in tr:
        p = h["traj"]["profile"]
        w, th = p["interface_10_90"], p.get("tanh")
        lines.append(
            f"| {h['t_c']:g} | {w['lower']['width']:.2f} | {w['upper']['width']:.2f} |"
            + (
                f" {th['delta_A']:.2f} ± {th['delta_err_A']:.2f} | {th['width_10_90_A']:.2f} |"
                f" {th['h_A']:.2f} |"
                if th
                else " fit failed | | |"
            )
        )
    lines += [
        "",
        "## Mobility by layer (holds)",
        "",
        (
            "Backbone sites (CG: beads; UA/AA: backbone carbons), positions relative to the"
            " system's mass centre, layer at the time origin; ≤ "
            f"{MAX_ORIGINS} origins per lag (hold DCD, lags ≥ its frame interval) and ≤"
            f" {BURST_ORIGINS} per burst (D46 bursts, shorter lags). MSD per dimension (Å²):"
            " in-plane xy = (⟨Δx²⟩+⟨Δy²⟩)/2, normal z = ⟨Δz²⟩, bulk = MSD/3 of the bulk"
            " hold. P2 1/e: first 1/e crossing of ⟨P2(u(0)·u(t))⟩ of backbone bonds (layer of"
            " the bond midpoint at the origin)."
        ),
        "",
        (
            "| T (°C) | layer | site fraction | xy / z @ 10 ps | xy / z @ 100 ps | xy / z @ 1 ns |"
            " xy / z @ max | P2 1/e (ps) |"
        ),
        "|---|---|---|---|---|---|---|---|",
    ]
    for h in tr:
        ly = h["traj"]["layers"]
        lag_max = f"{ly['lag_max_ps']:g}"
        for name in (*CLASSES, "film"):
            d = ly[name]
            frac = {
                "surface": ly["surface_fraction"],
                "interior": 1 - ly["surface_fraction"],
                "film": 1.0,
            }[name]
            cells = []
            for lag in (*[f"{x:g}" for x in REPORT_LAGS_PS], lag_max):
                v = d["msd_at"].get(lag)
                cells.append(f"{v['xy']:.1f} / {v['z']:.1f}" if v else "n/a")
            lines.append(
                f"| {h['t_c']:g} | {name} | {frac:.2f} | {' | '.join(cells)} |"
                f" {_t1e(d['p2_t_1e_ps'], d['p2_at_max'])} |"
            )
        b = h.get("bulk") or {}
        if b.get("msd_lag_ps"):
            cells = []
            for lag in (*REPORT_LAGS_PS, ly["lag_max_ps"]):
                v = _interp_log(b["msd_lag_ps"], b["msd_per_dim_A2"], lag)
                cells.append(_f(v, ".1f"))
            lines.append(
                f"| {h['t_c']:g} | bulk | | {' | '.join(cells)} |"
                f" {_t1e(b.get('p2_t_1e_ps'), None)} |"
            )
    lines += [
        "",
        "## Orientation and chain shape by layer (holds)",
        "",
        (
            "⟨P2(cos θ_z)⟩ of backbone bonds (θ_z: angle to the film normal; 0 isotropic, −0.5"
            " all in-plane) by the layer of the bond midpoint; ⟨Rg_z²⟩ and ⟨Rg_xy²⟩/2"
            " (mass-weighted, per dimension; equal for isotropic chains) of chains by the"
            " layer of their mass centre; over the profile frames, SEM over frames."
        ),
        "",
        (
            "| T (°C) | layer | ⟨P2(cos θ_z)⟩ | chains | ⟨Rg_z²⟩ (Å²) | ⟨Rg_xy²⟩/2 (Å²) |"
            " ratio z/xy |"
        ),
        "|---|---|---|---|---|---|---|",
    ]
    for h in tr:
        c = h["traj"]["conformation"]
        for name in CLASSES:
            rr = c["rg"][name]
            z, xy = rr["rg_z2_A2"], rr["rg_xy2_half_A2"]
            ratio = f"{z['mean'] / xy['mean']:.2f}" if z and xy else "n/a"
            lines.append(
                f"| {h['t_c']:g} | {name} | {_pm(c['p2z_layer'][name], '.3f')} |"
                f" {rr['chains_mean']:.1f} | {_pm(z, '.0f')} | {_pm(xy, '.0f')} | {ratio} |"
            )
    lines += [
        "",
        "## Whole film vs bulk (holds; `analyze sweep` method)",
        "",
        (
            "Film-averaged results of the `analyze sweep` hold analysis (FFT MSD over every"
            " origin, bursts stitched) next to the bulk hold at the same T."
        ),
        "",
        (
            "| T (°C) | MSD max film / bulk (Å²) | COM MSD max film / bulk (Å²) | P2 1/e film / bulk"
            " (ps) | Rg film / bulk (Å) | R_ee film / bulk (Å) | C_n film / bulk |"
        ),
        "|---|---|---|---|---|---|---|",
    ]
    for h in tr:
        fm, b = h.get("film") or {}, h.get("bulk") or {}
        if not fm.get("available"):
            continue
        lines.append(
            f"| {h['t_c']:g} | {fm['segment_msd']['msd_at_max_A2']:.0f} /"
            f" {_f(b.get('msd_at_max_A2'), '.0f')} | {fm['com_msd']['msd_at_max_A2']:.0f} /"
            f" {_f(b.get('com_msd_at_max_A2'), '.0f')} |"
            f" {_t1e(fm['p2']['t_1e_ps'], fm['p2']['at_max'])} / {_t1e(b.get('p2_t_1e_ps'), None)} |"
            f" {_pm(fm['rg']['rg_A'], '.2f')} / {_pm(b.get('rg_A'), '.2f') or 'n/a'} |"
            f" {_pm(fm['ree']['ree_A'], '.1f')} / {_pm(b.get('ree_A'), '.1f') or 'n/a'} |"
            f" {_pm(fm['c_n']['plateau'], '.2f')} / {_pm(b.get('c_n'), '.2f') or 'n/a'} |"
        )
    notes = []
    for h in holds:
        for n in h["traj"].get("notes", []) + (h.get("film") or {}).get("notes", []):
            notes.append(f"- {h['t_c']:g} °C: {n}")
    lines += [""] + notes if notes else []
    lines += equilibration_markdown(r, PORE_LOCAL_NOTE, CHAIN_NOTE)
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r.get("caveats", [])]
    if r.get("plots"):
        lines += ["", "## Plots", ""]
        for p in r["plots"].values():
            lines += [f"**{p['title']}**", "", f"![{p['title']}]({p['file']})", ""]
    return "\n".join(lines) + "\n"


PORE_LOCAL_NOTE = (
    "Local quantities (γ, PE, film thickness and interior density, interfacial width,"
    " segmental MSD, bond P2: relaxation times ~10–100 ps in CG) equilibrate within the"
    " dropped part of each segment (`film_vs_time.png`: thickness, gap, interior density"
    " and clear gap per hold frame). Surface chain conformation and orientation by layer"
    " (Rg_z vs Rg_xy, layer membership of chains) are chain-scale quantities."
)


def _thermal_markdown(r: dict) -> list[str]:
    """The thermal-analysis section (pore analogue of the bulk sweep fits)."""
    th = r.get("thermal") or {}
    lines = [
        "",
        "## Thermal analysis over the sweep grid",
        "",
        (
            "One point per set T (the hold where there is one). Film thickness t_G (Gibbs) and"
            " the interior plateau density from the segment's DCD (steps: second half; holds:"
            " without the first 10%; ≤ max-frames frames; SEM over frames); E = TotEng (NVT"
            " thermo window). Surface excess energy per surface e_s = (E_pore −"
            " (M_pore/M_bulk) E_bulk(T))/(2A), E_bulk from the bulk sweep at the same set T;"
            " γ − T dγ/dT with the sweep fit slope (should ≈ e_s)."
        ),
        "",
        (
            "| T (°C) | seg | t_G (Å) | ρ plateau (g/cm³) | ρ bulk (g/cm³) | Δρ/ρ bulk | Lx (Å) |"
            " E (kcal/mol) | γ (mN/m) | e_s (mJ/m²) | γ − T dγ/dT (mJ/m²) |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in th.get("points", []):
        pl, bd = p.get("plateau"), p.get("bulk_density")
        rel = f"{(pl['mean'] - bd['mean']) / bd['mean'] * 100:+.2f}%" if pl and bd else "n/a"
        lines.append(
            f"| {p['t_c']:g} | {p['kind']} | {_pm(p.get('film_gibbs_A'), '.2f') or 'n/a'} |"
            f" {_pm(pl, '.4f') or 'n/a'} | {_pm(bd, '.4f') or 'n/a'} | {rel} |"
            f" {p['lx_A']:.3f} | {_pm(p.get('etotal'), '.1f')} | {_pm(p.get('gamma'), '.2f')} |"
            f" {_pm(p.get('e_s_mJ_m2'), '.1f') or 'n/a'} | {_f(p.get('gamma_minus_TdgdT'), '.1f')} |"
        )
    if th.get("surface_entropy_mJ_m2K"):
        se = th["surface_entropy_mJ_m2K"]
        lines += [
            "",
            (
                f"Surface entropy per area −dγ/dT = {se['mean']:.4f} ± {se['err']:.4f} mJ m⁻² K⁻¹"
                " (sweep fit)."
            ),
        ]
    lines += [
        "",
        (
            "Expansion: α_z = (1/t_G) dt_G/dT (film normal, SEM-weighted, errors ×√χ²_red when"
            " > 1); α_L = (1/2A) dA/dT of the imposed box area (D48: follows the bulk density,"
            " so ≈ bulk α_V/3 by construction); film α_V = α_z + 2 α_L. Cv = dE/dT per gram"
            " (classical, NVT) next to the bulk classical Cp."
        ),
        "",
        (
            "| window (°C) | points | α_z (10⁻⁴ K⁻¹) | χ²_red | α_L (10⁻⁴ K⁻¹) | film α_V (10⁻⁴"
            " K⁻¹) | bulk α_V/3 | bulk α_V | Cv (J g⁻¹ K⁻¹) | bulk Cp (J g⁻¹ K⁻¹) |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    cv = {tuple(c["window_c"]): c for c in th.get("cv", [])}
    for a in th.get("alpha", []):
        c = cv.get(tuple(a["window_c"])) or {}
        bv = a.get("bulk_alpha_V_per_K")
        az = (
            f"{a['alpha_z_per_K'] * 1e4:.3f} ± {a['alpha_z_err'] * 1e4:.3f}"
            if a.get("alpha_z_per_K") is not None
            else "n/a"
        )
        fv = a.get("alpha_V_film_per_K")
        lines.append(
            f"| {a['window_c'][0]:g}–{a['window_c'][1]:g} | {a['n']} | {az} |"
            f" {_f(a.get('chi2_red'))} | {a['alpha_L_per_K'] * 1e4:.3f} |"
            f" {_f(fv * 1e4 if fv is not None else None, '.3f')} |"
            f" {_f(bv / 3 * 1e4 if bv else None, '.3f')} | {_f(bv * 1e4 if bv else None, '.3f')} |"
            + (f" {c['cv_J_gK']:.3f} ± {c['err']:.3f} |" if c else " n/a |")
            + f" {_f(c.get('bulk_cp_J_gK'), '.3f')} |"
        )
    for n in th.get("notes", []):
        lines.append(f"- {n}")
    return lines


def _mean(ms: dict | None, fmt: str) -> str:
    """Mean alone where the SEM is 0 (box lengths fixed in NVT), else mean +- SEM."""
    if ms and ms.get("sem") == 0.0:
        return f"{ms['mean']:{fmt}}"
    return _pm(ms, fmt)


def _t1e(t: float | None, at_max: float | None) -> str:
    if t is not None:
        return f"{t:.1f}"
    return "not reached" if at_max is None else f"not reached (P2 {at_max:.2f})"


def write_results(report: dict, out_dir: Path) -> None:
    from sepsim.analyze import write_results as _write

    _write(report, out_dir, render=render_markdown)
