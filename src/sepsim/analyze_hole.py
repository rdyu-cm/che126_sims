"""Hole analysis: `sepsim analyze hole` (D52).

For a hole run directory ``results/runs/<system>/<stage>/`` (deck ``in.hole``, the DCDs
``inflate.dcd``, ``hole_scaf.dcd``, ``hole.dcd`` and the dense windows
``hole_dense_s<NN>.dcd``, merged in time order with one frame per time;
``inflated.data`` for the scaffold)
this writes ``results.md``, ``results.json``, ``hole_radius.png``, ``hole_maps.png`` and
``thickness.png`` into ``results/analysis/<system>/<stage>/`` (or ``--out``):

- per frame (``sepsim.analysis.hole``): projected hole area A, R_eff = sqrt(A/pi),
  centroid drift from the build axis, R(z) per 10 A slab, R_min, film thickness;
  time 0 is the start of production (push removed; after the scaffolded hold if any);
- R after inflation (end of the push hold), the closure time t_close (R_min < 3 A for
  5 consecutive frames), dR/dt over the first ``FIT_NS`` of production and over the
  whole open period, the plateau radius of a hole that stays open (last quarter);
- per production segment (ramps): T, scaffold state, mean R_eff and R_min over its
  second half, open/closed;
- scaffold runs: tethered beads (recomputed from inflated.data and the deck geometry,
  checked against the LAMMPS group count), the nearest tethered bead to the axis
  (annulus: must be >= R + d), its minimum over the held frames; for every run the
  free shell R < r < R + d at t0: areal density vs the far film, and its bead MSD;
- ``--compare``: a table over runs (R0, T, variant -> t_close or final R, dR/dt) and
  ``compare_radius.png`` (R_eff(t) overlaid).

The deck timeline (stage lengths, dump interval, grid, release) is rebuilt from the
resolved parameters in the deck header with ``sepsim.lammps.render.hole_plan``.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import warnings
from pathlib import Path

import numpy as np
import yaml

from sepsim.analysis import hole as H
from sepsim.progress import deck_system

VERSION = 1
MD_NAME, JSON_NAME = "results.md", "results.json"
FIT_NS = 5.0  # initial dR/dt window
PLATEAU_FRAC = 0.25  # last quarter of production for the plateau radius
MAP_FRAMES = 6
_PARAM = re.compile(r"^#\s{3}(\w+) = (.*)$")
_GROUP = re.compile(r"^\s*(\d+) atoms in group scaffold")


class HoleAnalysisError(ValueError):
    """The run directory cannot be analysed."""


# --------------------------------------------------------------------------- inputs


def deck_params(deck: Path, resolution: str = "cg") -> dict:
    """Resolved parameters from the deck header, typed like the hole defaults."""
    from sepsim.lammps.render import HOLE_DEFAULTS, _coerce

    defaults = HOLE_DEFAULTS[resolution]
    params = dict(defaults)
    for line in deck.read_text(errors="replace").splitlines():
        if not line.startswith("#"):
            break
        if m := _PARAM.match(line):
            key, value = m.group(1), m.group(2)
            if key in defaults:
                params[key] = _coerce(key, value, defaults[key])
    return params


def timeline(params: dict, plan: list[dict]) -> dict:
    """Stage starts (ps from the deck start), production t0, segment bounds (ns of prod.)."""
    inflate, hold = params["inflate_ps"], params["wall_hold_ps"]
    scaf = params["scaffold_hold_ps"]
    t0 = inflate + hold + scaf
    segs, t = [], 0.0
    for s in plan:
        segs.append(
            {
                "index": s["index"],
                "kind": s["kind"],
                "t_c": s["t_c"],
                "start_ns": t / 1000.0,
                "end_ns": (t + s["ps"]) / 1000.0,
                "state": s["state"],
                "release": s["release"],
                "new_t": s["new_t"],
            }
        )
        t += s["ps"]
    every = params["hole_dump_ps"]
    dense = [
        (
            "production",
            f"hole_dense_s{s['index']:02d}.dcd",
            t0 + 1000.0 * s["start_ns"],
            params["dense_dump_ps"],
        )
        for s in plan
        if s.get("dense")
    ]
    return {
        "t0_ps": t0,
        "inflate_end_ns": (inflate - t0) / 1000.0,
        "hold_end_ns": (inflate + hold - t0) / 1000.0,
        # (phase, file, start ps from the deck start, frame interval ps)
        "dcds": [
            ("inflate", "inflate.dcd", 0.0, every),
            ("scaffold hold", "hole_scaf.dcd", inflate + hold, every),
            *dense,
            ("production", "hole.dcd", t0, every),
        ],
        "segments": segs,
    }


def _reader(path: Path):
    from MDAnalysis.coordinates.DCD import DCDReader

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return DCDReader(str(path))


def _n_frames(path: Path) -> int:
    from MDAnalysis.coordinates.DCD import DCDReader

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reader = DCDReader(str(path))
    try:
        return reader.n_frames
    finally:
        reader.close()


def _data_positions(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """(positions sorted by id, box lengths) of a LAMMPS data file."""
    from sepsim.build.datafile import read_data_file

    df = read_data_file(path)
    atoms = df.sorted_atoms()
    lengths = np.array([hi - lo for lo, hi in df.box])
    return atoms[:, 4:7].astype(float), lengths


def _min_image_r(xy: np.ndarray, axis, lengths) -> np.ndarray:
    d = H.wrap_about(xy, axis, lengths)
    return np.hypot(d[:, 0], d[:, 1])


def tethered_mask(pos, lengths, hole: dict, params: dict, box) -> np.ndarray:
    """Beads the deck tethers (same geometry as the deck's region)."""
    from sepsim.lammps.render import column_centres

    axis = hole["axis_angstrom"]
    if params["scaffold"] == "annulus":
        r_s = 10.0 * (hole["radius_nm"] + params["scaffold_d_nm"])
        # the LAMMPS region is not periodic: distance to the axis in the primary box
        r = np.hypot(pos[:, 0] - axis[0], pos[:, 1] - axis[1])
        return r > r_s
    cols = column_centres(hole, params, box)
    r_c = 10.0 * params["scaffold_col_r_nm"]
    mask = np.zeros(len(pos), bool)
    for cx, cy in cols:
        mask |= np.hypot(pos[:, 0] - cx, pos[:, 1] - cy) < r_c
    return mask


def _log_group_count(run_dir: Path) -> int | None:
    log = run_dir / "log.lammps"
    if not log.is_file():
        return None
    with log.open(errors="replace") as fh:
        for line in fh:
            if m := _GROUP.match(line):
                return int(m.group(1))
    return None


# --------------------------------------------------------------------------- analysis


def _box_wrap(pos: np.ndarray, box) -> np.ndarray:
    """x, y wrapped into the manifest box (the deck keeps the box centre fixed)."""
    out = pos.copy()
    for k in (0, 1):
        lo, hi = box[k]
        out[:, k] = lo + np.mod(out[:, k] - lo, hi - lo)
    return out


def analyze_hole(
    run_dir: str | Path, out: str | Path | None = None, systems: str | Path = "systems"
) -> tuple[dict, Path]:
    """Analyse one hole run directory; returns (report, output directory)."""
    run_dir = Path(run_dir)
    deck = run_dir / "in.hole"
    if not deck.is_file():
        raise HoleAnalysisError(f"{run_dir}: no in.hole deck")
    system, resolution = deck_system(deck)
    if system is None:
        raise HoleAnalysisError(f"{deck}: no '# system' header line")
    sys_dir = Path(systems) / system
    man_path = sys_dir / "manifest.yaml"
    if not man_path.is_file():
        raise HoleAnalysisError(f"{man_path}: not found (--systems)")
    manifest = yaml.safe_load(man_path.read_text())
    hole = manifest.get("hole")
    if not hole:
        raise HoleAnalysisError(f"{system}: not a hole system")
    from sepsim.lammps.render import hole_plan

    params = deck_params(deck, resolution or "cg")
    plan = hole_plan(params, float(hole["t_c"]))
    tl = timeline(params, plan)
    stage = run_dir.resolve().name
    out_dir = Path(out) if out else Path("results") / "analysis" / system / stage
    box = manifest["box_angstrom"]
    z_lo = float(box[2][0])
    axis = np.array(hole["axis_angstrom"], dtype=float)
    r0 = 10.0 * float(hole["radius_nm"])
    d_a = 10.0 * params["scaffold_d_nm"]

    frames: list[dict] = []
    keep: list[dict] = []
    centre, r_ref = axis.copy(), 0.0
    shell = shell_x0 = None
    tether = None
    tether_min: list[float] = []
    scaffold = params["scaffold"] != "none"
    if scaffold and (run_dir / "inflated.data").is_file():
        pos_inf, l_inf = _data_positions(run_dir / "inflated.data")
        tether = tethered_mask(pos_inf, l_inf, hole, params, box)
    available, events = [], []
    readers: dict[str, object] = {}
    rank = {"inflate": 0, "scaffold hold": 1, "production": 2}
    for phase, name, start_ps, every in tl["dcds"]:
        path = run_dir / name
        if not path.is_file():
            continue
        nf = _n_frames(path)
        available.append({"dcd": name, "frames": nf, "every_ps": every})
        for k in range(nf):
            t_ns = (start_ps + k * every - tl["t0_ps"]) / 1000.0
            events.append((round(t_ns, 9), rank[phase], phase, name, k))
    # one frame per time (DCDs overlap: stage ends, the dense windows), the later phase
    events.sort()
    merged = []
    for ev in events:
        if merged and abs(merged[-1][0] - ev[0]) < 1e-9:
            if ev[1] >= merged[-1][1]:
                merged[-1] = ev
            continue
        merged.append(ev)
    prod_idx = [i for i, ev in enumerate(merged) if ev[2] == "production"]
    pick = set()
    infl = [i for i, ev in enumerate(merged) if ev[2] == "inflate"]
    if infl:
        pick.add(infl[-1])
    if prod_idx:
        pick |= {prod_idx[round(v)] for v in np.linspace(0, len(prod_idx) - 1, MAP_FRAMES - 1)}
    try:
        for i, (t_ns, _, phase, name, k) in enumerate(merged):
            if name not in readers:
                readers[name] = _reader(run_dir / name)
            ts = readers[name][k]
            pos = ts.positions.astype(float)
            lengths = np.asarray(ts.dimensions[:3], dtype=float)
            if phase == "inflate" and r_ref == 0.0:
                centre = axis.copy()
            f = H.analyse_frame(pos, lengths, centre, max(r_ref, 4.0), z_lo, keep_map=i in pick)
            centre, r_ref = f.centre, f.r_eff
            drift = H.wrap_about(f.centre[None, :], axis, lengths)[0]
            row = {
                "t_ns": t_ns,
                "phase": phase,
                "dcd": name,
                "r_eff": f.r_eff,
                "r_min": f.r_min,
                "area": f.area,
                "drift": float(np.hypot(*drift)),
                "thickness": f.thickness,
                "slab_z": f.slab_z.tolist(),
                "slab_r": f.slab_r.tolist(),
                "lx": float(lengths[0]),
            }
            if tether is not None and phase != "inflate":
                seg = _segment_at(tl["segments"], t_ns) if phase == "production" else None
                held = phase == "scaffold hold" or (seg is not None and seg["state"] == "held")
                r_t = _min_image_r(pos[tether], axis, lengths)
                row["tether_rmin"] = float(r_t.min())
                if held:
                    tether_min.append(row["tether_rmin"])
            if phase == "production":
                com = pos.mean(axis=0)
                if shell is None:
                    r = _min_image_r(pos, axis, lengths)
                    shell = (r > r0) & (r < r0 + d_a)
                    far = r >= r0 + d_a
                    a_shell = math.pi * ((r0 + d_a) ** 2 - r0**2)
                    a_far = lengths[0] * lengths[1] - math.pi * (r0 + d_a) ** 2
                    ratio = (shell.sum() / a_shell) / (far.sum() / a_far) if far.any() else None
                    shell_x0 = (pos[shell] - com, int(shell.sum()), ratio)
                disp = (pos[shell] - com) - shell_x0[0]
                row["shell_msd"] = float((disp**2).sum(axis=1).mean()) if len(disp) else None
            frames.append(row)
            if i in pick:
                keep.append({"t_ns": t_ns, "phase": phase, "map": f.map, "mask": f.mask})
    finally:
        for rd in readers.values():
            rd.close()
    if not frames:
        raise HoleAnalysisError(f"{run_dir}: no inflate.dcd / hole.dcd frames")

    report = summarize(frames, tl, params, hole, manifest, run_dir, system, stage)
    report["dcds"] = available
    if tether is not None:
        r_inf = _min_image_r(pos_inf, axis, l_inf)
        n_log = _log_group_count(run_dir)
        report["scaffold"] = {
            "mode": params["scaffold"],
            "d_nm": params["scaffold_d_nm"],
            "k": params["scaffold_k"],
            "tethered": int(tether.sum()),
            "tethered_fraction": float(tether.mean()),
            "lammps_group_count": n_log,
            "count_matches_log": None if n_log is None else n_log == int(tether.sum()),
            "nearest_tethered_r_t0": float(r_inf[tether].min()) if tether.any() else None,
            "nearest_ok": (
                bool(r_inf[tether].min() >= r0 + d_a - 1e-6)
                if params["scaffold"] == "annulus" and tether.any()
                else None
            ),
            "nearest_tethered_r_held_min": min(tether_min) if tether_min else None,
        }
    if shell_x0 is not None:
        report["free_shell"] = {
            "r_in": r0,
            "r_out": r0 + d_a,
            "beads": shell_x0[1],
            "areal_density_ratio": shell_x0[2],
            "msd": _msd_points([f for f in frames if f["phase"] == "production"]),
        }
    report["_keep"] = keep
    return report, out_dir


def _segment_at(segments, t_ns):
    for s in segments:
        if s["start_ns"] - 1e-9 <= t_ns < s["end_ns"] - 1e-9:
            return s
    return segments[-1] if segments and t_ns >= segments[-1]["end_ns"] - 1e-9 else None


def _msd_points(prod: list[dict]) -> dict:
    out = {}
    if not prod:
        return out
    t = np.array([f["t_ns"] for f in prod])
    m = np.array([f.get("shell_msd") or 0.0 for f in prod])
    for target in (1.0, 10.0):
        if t[-1] >= target:
            out[f"{target:g} ns"] = float(np.interp(target, t, m))
    out["end"] = float(m[-1])
    out["end_ns"] = float(t[-1])
    return out


def summarize(frames, tl, params, hole, manifest, run_dir, system, stage) -> dict:
    t = np.array([f["t_ns"] for f in frames])
    r = np.array([f["r_eff"] for f in frames])
    rmin = np.array([f["r_min"] for f in frames])
    phase = np.array([f["phase"] for f in frames])
    prod = phase == "production"
    hold = (t > tl["inflate_end_ns"] + 1e-9) & (t <= tl["hold_end_ns"] + 1e-9)
    hold_tail = hold & (t >= tl["hold_end_ns"] - 0.2 * (tl["hold_end_ns"] - tl["inflate_end_ns"]))
    out: dict = {
        "version": VERSION,
        "system": system,
        "stage": stage,
        "run_dir": str(run_dir),
        "created": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "radius_nominal_nm": hole["radius_nm"],
        "t_c": hole["t_c"],
        "film_thickness_angstrom": hole["film_thickness_angstrom"],
        "ligament_angstrom": hole.get("ligament_angstrom"),
        "variant": variant_label(params),
        "params": {
            k: params[k]
            for k in (
                "inflate_ps",
                "wall_hold_ps",
                "push_style",
                "push_k",
                "scaffold",
                "scaffold_d_nm",
                "scaffold_k",
                "scaffold_hold_ps",
                "hole_grid_c",
                "hole_step_ps",
                "hole_hold_ps",
                "release_t_c",
                "hole_dump_ps",
            )
        },
        "segments": tl["segments"],
        "frames": [{k: v for k, v in f.items()} for f in frames],
        "notes": [],
    }
    out["r_after_inflation"] = (
        {"mean": float(r[hold_tail].mean()), "r_min_mean": float(rmin[hold_tail].mean())}
        if hold_tail.any()
        else None
    )
    if prod.any():
        tp, rp, rmp = t[prod], r[prod], rmin[prod]
        tc = H.closure_time(tp, rmp)
        out["r_t0"] = float(rp[0])
        out["t_close_ns"] = tc
        open_ = tp < tc if tc is not None else np.ones_like(tp, bool)
        first = open_ & (tp <= FIT_NS)
        out["rate_initial"] = H.linear_rate(tp[first], rp[first])
        out["rate_open"] = H.linear_rate(tp[open_], rp[open_])
        out["production_ns"] = float(tp[-1])
        if tc is None and len(tp) >= 4:
            tail = tp >= tp[-1] - PLATEAU_FRAC * (tp[-1] - tp[0])
            out["plateau"] = {
                "r_eff": float(rp[tail].mean()),
                "r_eff_sd": float(rp[tail].std()),
                "r_min": float(rmp[tail].mean()),
                "window_ns": [float(tp[tail][0]), float(tp[-1])],
            }
        out["r_final"] = float(rp[-1])
        out["r_min_final"] = float(rmp[-1])
        out["thickness_t0"] = frames[int(np.flatnonzero(prod)[0])]["thickness"]
        out["thickness_final"] = frames[-1]["thickness"]
        rows = []
        for s in tl["segments"]:
            sel = prod & (t >= 0.5 * (s["start_ns"] + s["end_ns"])) & (t <= s["end_ns"] + 1e-9)
            if not sel.any():
                continue
            rows.append(
                s
                | {
                    "r_eff": float(r[sel].mean()),
                    "r_min": float(rmin[sel].mean()),
                    "open": bool(rmin[sel].mean() >= H.CLOSED_R_A),
                    "frames": int(sel.sum()),
                }
            )
        out["per_segment"] = rows
    else:
        out["notes"].append("no production frames (hole.dcd) yet")
    return out


def variant_label(params: dict) -> str:
    if params["scaffold"] == "none":
        v = "free"
    else:
        v = f"{params['scaffold']} d={params['scaffold_d_nm']:g} nm"
        rel = str(params["release_t_c"]).strip().lower()
        v += ", held" if rel in ("", "none") else f", released at {rel} C"
        if params["scaffold_hold_ps"] > 0:
            v += f" (scaffolded hold {params['scaffold_hold_ps'] / 1000:g} ns)"
    grid = params["hole_grid_c"]
    if grid and "," in grid:
        v += ", ramp"
    return v


# --------------------------------------------------------------------------- output


def _marks(ax, report):
    for s in report["segments"]:
        if s["new_t"]:
            ax.axvline(s["start_ns"], color="0.7", lw=0.6, ls=":")
        if s["release"]:
            ax.axvline(s["start_ns"], color="tab:red", lw=1.0, ls="--", label="scaffold released")
    ax.axvline(0.0, color="k", lw=0.6, ls="-")


def make_plots(report: dict, out_dir: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fr = report["frames"]
    t = np.array([f["t_ns"] for f in fr])
    r = np.array([f["r_eff"] for f in fr])
    rmin = np.array([f["r_min"] for f in fr])
    drift = np.array([f["drift"] for f in fr])
    title = f"{report['system']} / {report['stage']}"
    files = []
    ramp = len(report.get("per_segment") or []) > 1
    fig, axes = plt.subplots(2 + ramp, 1, figsize=(8, 7 + 3 * ramp))
    ax = axes[0]
    ax.plot(t, r / 10, label="R_eff (projected)")
    ax.plot(t, rmin / 10, label="R_min (10 A slabs)", alpha=0.7)
    ax.axhline(report["radius_nominal_nm"], color="0.5", ls="--", lw=0.8, label="nominal R")
    if report.get("t_close_ns") is not None:
        ax.axvline(report["t_close_ns"], color="tab:green", label="t_close")
    _marks(ax, report)
    ax.set_xlabel("t (ns; 0 = push removed / production)")
    ax.set_ylabel("R (nm)")
    ax.set_title(title)
    h, lab = ax.get_legend_handles_labels()
    seen = {}
    for hh, ll in zip(h, lab, strict=True):
        seen.setdefault(ll, hh)
    ax.legend(seen.values(), seen.keys(), fontsize=8)
    axes[1].plot(t, drift / 10)
    axes[1].set_ylabel("centroid drift (nm)")
    axes[1].set_xlabel("t (ns)")
    if ramp:
        rows = report["per_segment"]
        tc = [s["t_c"] for s in rows]
        axes[2].plot(tc, [s["r_eff"] / 10 for s in rows], "o-", label="R_eff")
        axes[2].plot(tc, [s["r_min"] / 10 for s in rows], "s--", label="R_min")
        for s in rows:
            if s["release"]:
                axes[2].axvline(s["t_c"], color="tab:red", ls="--", label="released")
        axes[2].set_xlabel("T (C), second half of each segment")
        axes[2].set_ylabel("R (nm)")
        axes[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "hole_radius.png", dpi=120)
    plt.close(fig)
    files.append("hole_radius.png")

    keep = report.get("_keep") or []
    if keep:
        n = len(keep)
        cols = min(3, n)
        rows_ = math.ceil(n / cols)
        fig, axes = plt.subplots(rows_, cols, figsize=(4 * cols, 4 * rows_), squeeze=False)
        for ax, k in zip(axes.ravel(), keep, strict=False):
            ax.imshow(k["map"].T, origin="lower", cmap="viridis")
            if k["mask"] is not None and k["mask"].any():
                ax.contour(k["mask"].T.astype(float), levels=[0.5], colors="r", linewidths=0.8)
            ax.set_title(f"{k['phase']} t = {k['t_ns']:.2f} ns", fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])
        for ax in axes.ravel()[n:]:
            ax.axis("off")
        fig.suptitle(f"{title}: beads projected along z (2 A bins), hole in red", fontsize=9)
        fig.tight_layout()
        fig.savefig(out_dir / "hole_maps.png", dpi=110)
        plt.close(fig)
        files.append("hole_maps.png")

    fig, axes = plt.subplots(2, 1, figsize=(8, 7))
    axes[0].plot(t, [f["thickness"] / 10 for f in fr])
    _marks(axes[0], report)
    axes[0].set_ylabel("film thickness away from the hole (nm)")
    zs = sorted({round(z, 3) for f in fr for z in f["slab_z"]})
    if zs:
        grid = np.full((len(zs), len(fr)), np.nan)
        idx = {z: i for i, z in enumerate(zs)}
        for j, f in enumerate(fr):
            for z, rr in zip(f["slab_z"], f["slab_r"], strict=True):
                grid[idx[round(z, 3)], j] = rr / 10
        im = axes[1].pcolormesh(t, np.array(zs) / 10, grid, shading="nearest", cmap="magma")
        fig.colorbar(im, ax=axes[1], label="R(z) (nm)")
    axes[1].set_xlabel("t (ns)")
    axes[1].set_ylabel("z - film mid-plane (nm)")
    fig.tight_layout()
    fig.savefig(out_dir / "thickness.png", dpi=120)
    plt.close(fig)
    files.append("thickness.png")
    return files


def _f(x, fmt=".2f") -> str:
    return "n/a" if x is None else f"{x:{fmt}}"


def _nm(x) -> str:
    """Angstrom -> nm, 2 decimals (n/a for None)."""
    return "n/a" if x is None else f"{x / 10:.2f}"


CAVEATS = [
    (
        "The scaffold is imposed harmonic tethers (fix spring/self) on the film outside R + d,"
        " a stand-in for the semicrystalline network that holds real separator pores open; it is"
        " not crystallinity, and its release is an emulation of melting, not a prediction of the"
        " shutdown temperature."
    ),
    "The free film is the post-shutdown limit (a hole in an amorphous melt-like film).",
    (
        "Times are CG model times (the SDK CG dynamics is faster than real PE by an unknown"
        " factor); compare runs with each other, not with experiment."
    ),
    (
        "All holes here have R < h (R/h <= 0.31), so closure is expected from the energy balance"
        " (R_c proportional to h, prefactor ~0.3-1 depending on rim geometry; Taylor & Michael"
        " 1973, Ilton et al. 2016): these runs measure closure kinetics (viscous scale"
        " ~ eta R / gamma), not the opening threshold."
    ),
    (
        "Finite size: the film is periodic in x, y; the ligament between the hole and its"
        " periodic images is L - 2R (given above; R = 4 nm leaves ~5 nm)."
    ),
    (
        "gamma (and so the closure speed) depends on the plain LJ cutoff without tail correction"
        " (D48)."
    ),
]


def render_markdown(r: dict) -> str:
    lines = [f"# Hole: {r['system']} / {r['stage']}", ""]
    lines.append(
        f"Nominal R {r['radius_nominal_nm']:g} nm at {r['t_c']:g} C, film"
        f" {r['film_thickness_angstrom'] / 10:.2f} nm (R/h ="
        f" {10 * r['radius_nominal_nm'] / r['film_thickness_angstrom']:.2f}), ligament"
        f" {_nm(r.get('ligament_angstrom'))} nm; variant: {r['variant']}."
    )
    lines.append("")
    p = r["params"]
    lines.append(
        f"Inflate {p['inflate_ps'] / 1000:g} ns + push hold {p['wall_hold_ps'] / 1000:g} ns"
        f" ({p['push_style']}, K {p['push_k']:g}); grid `{p['hole_grid_c'] or f'{r["t_c"]:g}h'}`;"
        f" frames every {p['hole_dump_ps']:g} ps. Time 0 = start of production."
    )
    lines += ["", "## Summary", "", "| quantity | value |", "|---|---|"]
    ai = r.get("r_after_inflation")
    lines.append(
        f"| R_eff after inflation (last 20% of the push hold) | {_nm(ai and ai['mean'])} nm |"
    )
    lines.append(f"| R_min after inflation | {_nm(ai and ai['r_min_mean'])} nm |")
    lines.append(f"| R_eff at t0 | {_nm(r.get('r_t0'))} nm |")
    lines.append(
        f"| t_close (R_min < {H.CLOSED_R_A:g} A for {H.CLOSED_FRAMES} frames) |"
        f" {_f(r.get('t_close_ns'))} ns |"
    )
    for key, label in (
        ("rate_initial", f"dR_eff/dt, first {FIT_NS:g} ns"),
        ("rate_open", "dR_eff/dt, open period"),
    ):
        v = r.get(key)
        lines.append(
            f"| {label} | "
            + ("n/a" if not v else f"{v['slope'] / 10:.3f} ± {v['slope_se'] / 10:.3f} nm/ns")
            + " |"
        )
    pl = r.get("plateau")
    if pl:
        lines.append(
            f"| plateau R_eff ({pl['window_ns'][0]:.1f}-{pl['window_ns'][1]:.1f} ns) |"
            f" {pl['r_eff'] / 10:.2f} ± {pl['r_eff_sd'] / 10:.2f} nm (R_min {pl['r_min'] / 10:.2f}) |"
        )
    lines.append(
        f"| final R_eff / R_min | {_nm(r.get('r_final'))} / {_nm(r.get('r_min_final'))} nm |"
    )
    lines.append(
        f"| film thickness t0 / final | {_nm(r.get('thickness_t0'))}"
        f" / {_nm(r.get('thickness_final'))} nm |"
    )
    sc = r.get("scaffold")
    if sc:
        lines += ["", "## Scaffold", ""]
        lines.append(
            f"- {sc['mode']}, d = {sc['d_nm']:g} nm, K = {sc['k']:g} kcal/mol/A²:"
            f" {sc['tethered']} tethered beads ({100 * sc['tethered_fraction']:.1f}%);"
            f" LAMMPS group count {sc['lammps_group_count']}"
            f" ({'matches' if sc['count_matches_log'] else 'n/a' if sc['count_matches_log'] is None else 'MISMATCH'})."
        )
        lines.append(
            f"- nearest tethered bead to the axis at t0: {_f(sc['nearest_tethered_r_t0'])} A"
            + (
                f" ({'>= R + d: ok' if sc['nearest_ok'] else 'BELOW R + d'})"
                if sc["nearest_ok"] is not None
                else ""
            )
            + f"; minimum while held: {_f(sc['nearest_tethered_r_held_min'])} A."
        )
    fs = r.get("free_shell")
    if fs:
        msd = fs["msd"]
        lines += ["", "## Free shell", ""]
        lines.append(
            f"- beads with {fs['r_in'] / 10:g} < r < {fs['r_out'] / 10:g} nm at t0: {fs['beads']};"
            f" areal density / far film: {_f(fs['areal_density_ratio'], '.3f')}."
        )
        lines.append(
            "- bead MSD from t0 (COM removed): "
            + ", ".join(f"{k}: {v:.1f} A²" for k, v in msd.items() if k != "end_ns")
            + (f" (end = {msd['end_ns']:.2f} ns)" if "end_ns" in msd else "")
        )
    rows = r.get("per_segment") or []
    if rows:
        lines += [
            "",
            "## Per production segment (second half)",
            "",
            "| # | kind | T (C) | scaffold | R_eff (nm) | R_min (nm) | open |",
            "|---|---|---|---|---|---|---|",
        ]
        for s in rows:
            lines.append(
                f"| {s['index']} | {s['kind']} | {s['t_c']:g} | {s['state'] or '-'} |"
                f" {s['r_eff'] / 10:.2f} | {s['r_min'] / 10:.2f} | {'yes' if s['open'] else 'no'} |"
            )
    if r.get("compare"):
        lines += ["", "## Comparison", ""] + compare_table(r["compare"])
    if r.get("notes"):
        lines += ["", "## Notes", ""] + [f"- {n}" for n in r["notes"]]
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in CAVEATS]
    lines += ["", "Figures: " + ", ".join(f"`{f}`" for f in r.get("figures", []))]
    return "\n".join(lines) + "\n"


def compare_table(rows: list[dict]) -> list[str]:
    out = [
        (
            "| system / stage | R0 (nm) | T (C) | variant | t_close (ns) | final R_eff (nm) |"
            f" dR/dt first {FIT_NS:g} ns (nm/ns) |"
        ),
        "|---|---|---|---|---|---|---|",
    ]
    for c in rows:
        rate = c.get("rate_initial")
        out.append(
            f"| {c['system']} / {c['stage']} | {c['radius_nominal_nm']:g} | {c['t_c']:g} |"
            f" {c['variant']} | {_f(c.get('t_close_ns'))} |"
            f" {_nm(c.get('r_final'))} |"
            f" {'n/a' if not rate else f'{rate["slope"] / 10:.3f}'} |"
        )
    return out


def _json(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    raise TypeError(f"not JSON serializable: {type(x).__name__}")


def write_results(report: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    report["figures"] = make_plots(report, out_dir) + report.pop("_extra_figures", [])
    report.pop("_keep", None)
    for name, text in (
        (JSON_NAME, json.dumps(report, indent=1, sort_keys=True, default=_json) + "\n"),
        (MD_NAME, render_markdown(report)),
    ):
        tmp = out_dir / (name + ".tmp")
        tmp.write_text(text)
        os.replace(tmp, out_dir / name)
    return out_dir / MD_NAME


def _compare_entry(report: dict) -> dict:
    keys = ("system", "stage", "radius_nominal_nm", "t_c", "variant", "t_close_ns", "r_final")
    entry = {k: report.get(k) for k in keys} | {"rate_initial": report.get("rate_initial")}
    entry["t"] = [f["t_ns"] for f in report["frames"]]
    entry["r_eff"] = [f["r_eff"] for f in report["frames"]]
    return entry


def _load_or_analyze(run_dir: Path, systems) -> dict:
    deck = run_dir / "in.hole"
    system, _ = deck_system(deck) if deck.is_file() else (None, None)
    if system:
        cached = Path("results") / "analysis" / system / run_dir.resolve().name / JSON_NAME
        if cached.is_file():
            rep = json.loads(cached.read_text())
            if rep.get("version") == VERSION:
                return rep
    rep, _ = analyze_hole(run_dir, systems=systems)
    rep.pop("_keep", None)
    return rep


def compare_plot(entries: list[dict], out_dir: Path) -> str:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    for e in entries:
        ax.plot(
            e["t"],
            np.array(e["r_eff"]) / 10,
            label=f"R{e['radius_nominal_nm']:g} {e['t_c']:g}C {e['variant']} ({e['stage']})",
        )
    ax.axvline(0.0, color="k", lw=0.6)
    ax.set_xlabel("t (ns; 0 = production start)")
    ax.set_ylabel("R_eff (nm)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out_dir / "compare_radius.png", dpi=120)
    plt.close(fig)
    return "compare_radius.png"


def analyze_hole_cli(run_dir, compare=(), out=None, systems="systems") -> Path:
    """Analyse ``run_dir`` (and tabulate it with the ``compare`` runs); returns results.md."""
    report, out_dir = analyze_hole(run_dir, out=out, systems=systems)
    if compare:
        entries = [_compare_entry(report)]
        entries += [_compare_entry(_load_or_analyze(Path(c), systems)) for c in compare]
        report["compare"] = [
            {k: v for k, v in e.items() if k not in ("t", "r_eff")} for e in entries
        ]
        out_dir.mkdir(parents=True, exist_ok=True)
        report["_extra_figures"] = [compare_plot(entries, out_dir)]
    return write_results(report, out_dir)
