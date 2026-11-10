"""`sepsim analyze puncture` (D57): puncture runs -> results.md, results.json, PNGs.

Reads each run directory's deck (``in.puncture``: system id, resolved parameters from
the header), the film system's manifest (``--systems``: film z extent, box), the
``puncture.txt`` averages (:mod:`sepsim.analysis.puncture`) and, when present,
``puncture.dcd`` (far-field film surfaces at t0, material ahead of the tip, beads inside
the indenter, bond stretch, the hole about the axis after break-through) with the
topology of the deck's data file. Writes to ``results/analysis/<system>/<stage>/`` (or
``--out``; several run directories: ``results/analysis/<system>/puncture_compare/``, the
film ids with ``_film_<T>C`` reduced to ``_film`` when the runs span temperatures).
Nothing is written into the run directories. Runs at the same (T, v, R) (indenter
positions, tags) are pooled: mean ± SD.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import warnings
from pathlib import Path

import numpy as np
import yaml

from sepsim.analysis import hole as H
from sepsim.analysis import puncture as P
from sepsim.analysis.tensile import mean_sd, read_ave_time
from sepsim.analyze_tensile import _ms, _thin_json
from sepsim.progress import deck_params, deck_system, load_json
from sepsim.reporting import _f, dump_json, plots_markdown, write_atomic

MD_NAME, JSON_NAME = "results.md", "results.json"
DECK = "in.puncture"
SUMMARY_KEYS = ("f_peak_nN", "d_peak_nm", "d_break_nm", "w_break_aJ", "w_peak_aJ")
MAP_BIN_A = 4.0
_FILM_T = re.compile(r"_film_m?[0-9p]+C")

CAVEATS = [
    (
        "The film is an amorphous melt film (no crystallinity, no lamellae or fibrils), a few nm"
        " thick: a nanoscale puncture of a melt, not the ASTM/UL puncture strength of a"
        " separator."
    ),
    (
        "Indentation speeds are 10³–10⁴× faster than standard puncture tests and CG time runs"
        " ≈ 4× fast (D57; reporting.CG_TIME_NOTE): forces are rate-inflated viscous forces."
    ),
    (
        "No bond breaking: the CG bonds are harmonic, so the melt yields by chain pull-out and"
        " flow; break-through is the film parting around the tip, not chain scission."
    ),
    (
        "The film is periodic in x and y: it is clamped at the box edge, a distance L/2 from"
        " the axis (L/2R sets the span); the deflection and the force scale with it."
    ),
    (
        "The indenter is soft (fix indent, F = K (R − r)², K in kcal/mol/Å³): beads penetrate"
        " it slightly; check the inside-indenter count below."
    ),
    (
        "A hole in a melt re-seals: closure after break-through is physical (surface tension),"
        " but around the indenter column only the free annulus can close."
    ),
    (
        "The thermostat acts on all beads (thermostat=partial: x and y only), so the heat of"
        " the deformation near the tip is removed at the thermostat rate; see T_near."
    ),
]


class PunctureError(ValueError):
    """A run directory cannot be analysed (no puncture deck, no data)."""


def _params(deck: Path, resolution: str) -> dict:
    """Resolved parameters from the deck header, typed like the puncture defaults."""
    from sepsim.lammps.render import PUNCTURE_DEFAULTS, _coerce

    defaults = PUNCTURE_DEFAULTS[resolution]
    params = dict(defaults)
    for key, value in deck_params(deck).items():
        if key in defaults:
            params[key] = _coerce(key, value, defaults[key])
    return params


def _reader(path: Path):
    from MDAnalysis.coordinates.DCD import DCDReader

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return DCDReader(str(path))


def _deck_data(deck: Path, run_dir: Path, sys_dir: Path) -> Path:
    """The data file the deck reads (relative to the run directory), else data.lmp."""
    for line in deck.read_text(errors="replace").splitlines():
        t = line.split("#", 1)[0].split()
        if t and t[0] == "read_data" and len(t) > 1:
            p = Path(t[1])
            p = p if p.is_absolute() else run_dir / p
            if p.is_file():
                return p
    return sys_dir / "data.lmp"


def _bonds(data: Path) -> np.ndarray:
    """Bond index pairs (rows of the id-sorted atoms, the DCD order) of a data file."""
    from sepsim.build.datafile import read_data_file

    df = read_data_file(data)
    ids = df.sorted_atoms()[:, 0].astype(np.int64)
    pairs = df.topology("Bonds")[:, 2:4].astype(np.int64)
    return np.searchsorted(ids, pairs)


def _zc(plan: dict, k_step: int) -> float:
    """Tip centre z at step k_step of Stage 2 (the ramp)."""
    return plan["z0"] - plan["travel"] * min(k_step / plan["n_steps"], 1.0)


def analyze_run(run_dir: Path, systems: Path) -> dict:
    """One puncture run directory: curve, break-through, re-seal and diagnostics."""
    from sepsim.lammps.render import puncture_plan, steps

    deck = run_dir / DECK
    if not deck.is_file():
        raise PunctureError(f"{run_dir}: no {DECK} (not a puncture run directory)")
    system, res = deck_system(deck)
    if system is None:
        raise PunctureError(f"{deck}: no '# system' header line")
    params = _params(deck, res or "cg")
    sys_dir = systems / system
    man_path = sys_dir / "manifest.yaml"
    if not man_path.is_file():
        raise PunctureError(f"{man_path}: not found (--systems)")
    manifest = yaml.safe_load(man_path.read_text())
    film = manifest.get("film")
    if not film:
        raise PunctureError(f"{system}: not a film system (sepsim build film)")
    box = manifest["box_angstrom"]
    plan = puncture_plan(params, film, box)
    dt_fs = params["dt_fs"]
    settle_steps = steps(params["settle_ps"], dt_fs)
    dump_every = steps(params["puncture_dump_ps"], dt_fs)
    r_a = plan["r_a"]
    axis = (plan["xc"], plan["yc"])
    t_k = float(film["t_c"]) + 273.15
    run = {
        "run_dir": str(run_dir.resolve()),
        "stage": run_dir.resolve().name,
        "system": system,
        "resolution": res,
        "status": (load_json(run_dir / "run_manifest.json") or {}).get("status", "not started"),
        "t_c": float(film["t_c"]),
        "v_m_s": params["indent_v_m_s"],
        "r_nm": params["indent_r_nm"],
        "k": params["indent_k"],
        "offset_nm": [params["indent_x_nm"], params["indent_y_nm"]],
        "thermostat": params["thermostat"],
        "boundary": params["boundary"],
        "tag": params["tag"],
        "travel_nm": plan["travel"] / 10.0,
        "notes": [],
        "flags": [],
    }
    path = run_dir / "puncture.txt"
    if not path.is_file():
        raise PunctureError(f"{run_dir}: puncture.txt not found (not run yet)")
    try:
        data = read_ave_time(path, required=P.COLUMNS)
    except ValueError as exc:
        raise PunctureError(str(exc)) from None
    f, flipped = P.indenter_force(data)
    if flipped:
        run["notes"].append("indenter z force was negative while pushing: sign flipped")
    settle = data["step"] <= settle_steps
    ind = ~settle

    # far-field surfaces at t0 (first puncture.dcd frame, else the bead z range)
    dcd = run_dir / "puncture.dcd"
    reader = _reader(dcd) if dcd.is_file() else None
    if reader is not None and reader.n_frames:
        ts = reader[0]
        lengths0 = np.asarray(ts.dimensions[:3], dtype=float)
        z_bot0, z_top0 = P.far_surfaces(ts.positions.astype(float), axis, lengths0, r_a)
        run["surfaces_from"] = "puncture.dcd frame 0 (far field, 50% crossings)"
    else:
        if reader is not None:
            reader.close()
            reader = None
        first = np.flatnonzero(ind)[:1] if ind.any() else np.arange(min(1, len(f)))
        if not len(first) or "c_zmax" not in data:
            raise PunctureError(f"{run_dir}: no indentation rows and no puncture.dcd")
        z_bot0, z_top0 = float(data["c_zmin"][first[0]]), float(data["c_zmax"][first[0]])
        run["surfaces_from"] = "c_zmin/c_zmax at t0 (no puncture.dcd: outermost beads)"
        run["notes"].append("no puncture.dcd: signal iii, re-seal and maps not available")
    run["z_top0"], run["z_bot0"] = float(z_top0), float(z_bot0)
    run["thickness_nm"] = (z_top0 - z_bot0) / 10.0
    d_all = P.depth_nm(data["zc"], r_a, z_top0)
    curve = P.analyze_curve(d_all[ind], f[ind], f[settle])
    if "error" in curve:
        raise PunctureError(f"{run_dir}: {curve['error']}")
    run["curve"] = curve
    # signal ii: the tip bottom below the far-field bottom surface
    run["d_bottom_nm"] = run["thickness_nm"] if curve["d_max_nm"] >= run["thickness_nm"] else None

    frames = []
    if reader is not None:
        # frames on multiples of the dump interval from the start of Stage 2 on
        first = (-settle_steps) % dump_every
        geo = {"plan": plan, "axis": axis, "r_a": r_a, "z_top0": z_top0, "dt_fs": dt_fs}
        geo["first_step"] = first
        frames = _frames(reader, _deck_data(deck, run_dir, sys_dir), geo, dump_every, curve)
        reader.close()
    fd = np.array([fr["d_nm"] for fr in frames])
    run["break"] = P.break_through(curve, fd, [fr["ahead"] for fr in frames])
    d_break = run["break"]["d_break_nm"]
    run["deflection_at_break_nm"] = (
        d_break - curve["d_contact_nm"]
        if d_break is not None and curve["d_contact_nm"] is not None
        else None
    )
    run["frames"] = frames
    _reseal(run, frames, params, r_a)
    _diagnostics(run, data, ind, frames, params, manifest, t_k)
    run["_maps"] = _maps(run_dir, run, frames, axis) if frames else []
    return run


def _frames(reader, data_path: Path, geo: dict, dump_every: int, curve: dict) -> list[dict]:
    """Per frame of puncture.dcd: time, tip z, depth, beads ahead of / inside the
    indenter, max bond stretch (vs the median bond length of frame 0) and, from the
    force break on, the projected hole radius about the axis (R_eff)."""
    bonds = _bonds(data_path) if data_path.is_file() else np.zeros((0, 2), np.int64)
    plan, axis, r_a = geo["plan"], geo["axis"], geo["r_a"]
    d_force = curve.get("d_break_force_nm")
    out, l0 = [], None
    for k, ts in enumerate(reader):
        pos = ts.positions.astype(float)
        lengths = np.asarray(ts.dimensions[:3], dtype=float)
        k_step = geo.get("first_step", 0) + k * dump_every
        zc = _zc(plan, k_step)
        d = float((geo["z_top0"] - (zc - r_a)) / 10.0)
        use_bonds = len(bonds) and int(bonds.max()) < len(pos)
        if l0 is None and use_bonds:
            v = pos[bonds[:, 1]] - pos[bonds[:, 0]]
            v[:, :2] -= lengths[:2] * np.round(v[:, :2] / lengths[:2])
            l0 = float(np.median(np.sqrt((v * v).sum(axis=1))))
        fr = {
            "k": k,
            "t_ps": k_step * geo["dt_fs"] / 1000.0,
            "zc": zc,
            "d_nm": d,
            "ahead": P.ahead_count(pos, axis, lengths, zc, r_a),
            "inside": P.inside_count(pos, axis, lengths, zc, r_a),
            "n_beads": len(pos),
            "stretch": P.max_bond_stretch(pos, bonds, lengths, l0) if use_bonds else None,
            "zspan": float(np.ptp(pos[:, 2])),
        }
        if d_force is not None and d >= d_force:
            z = pos[:, 2]
            span = (lengths[0], lengths[1], float(np.ptp(z)) + 2 * P.Z_PAD_A)
            fr["r_eff"] = H.analyse_frame(pos, span, axis, r_a, float(z.min()) - P.Z_PAD_A).r_eff
        out.append(fr)
    return out


def _reseal(run: dict, frames: list[dict], params: dict, r_a: float) -> None:
    """Hole after break-through: the free radius sqrt(R_eff^2 - R^2) about the axis per
    frame; t_heal = first time it stays below 3 A for 5 frames (hole.closure_time)."""
    d_break = run["break"]["d_break_nm"]
    after = [fr for fr in frames if d_break is not None and fr["d_nm"] >= d_break and "r_eff" in fr]
    run["reseal"] = None
    if not after:
        return
    t = np.array([fr["t_ps"] for fr in after])
    r_free = P.free_hole_radius([fr["r_eff"] for fr in after], r_a)
    for fr, r in zip(after, r_free, strict=True):
        fr["r_free"] = float(r)
    t_heal = H.closure_time(t, r_free)
    run["reseal"] = {
        "frames": len(after),
        "r_free_max_A": float(r_free.max()),
        "r_free_end_A": float(r_free[-1]),
        "t_heal_ps": None if t_heal is None else float(t_heal - t[0]),
        "resealed": t_heal is not None,
    }


def _diagnostics(run, data, ind, frames, params, manifest, t_k) -> None:
    """Inside-indenter beads, bond stretch, T near/far vs the set T, z images (p p p) or
    the box growth along z (p p m); flags appended to run["flags"]."""
    diag: dict = {"t_set_K": t_k}
    for key, col in (("t_near_K", "c_tnear"), ("t_far_K", "c_tfar"), ("t_all_K", "temp")):
        if col in data and ind.any():
            diag[key] = float(np.mean(data[col][ind]))
    if frames:
        frac = max(fr["inside"] / fr["n_beads"] for fr in frames)
        diag["inside_max_fraction"] = frac
        diag["inside_max"] = max(fr["inside"] for fr in frames)
        if frac > P.INSIDE_FLAG:
            run["flags"].append(
                f"beads inside the indenter: up to {frac:.2%} of beads (> {P.INSIDE_FLAG:.1%}):"
                " the indenter is too soft (raise indent_k)"
            )
        st = [fr["stretch"] for fr in frames if fr["stretch"] is not None]
        if st:
            diag["max_bond_stretch"] = max(st)
            # the max over all bonds is ~30% from thermal motion alone (CG melt at 160 C):
            # compare with the first frame, taken before contact
            diag["bond_stretch_baseline"] = st[0]
            if max(st) > st[0] + P.STRETCH_FLAG:
                run["flags"].append(
                    f"max bond stretch {max(st):.0%} (> {st[0]:.0%} before contact"
                    f" + {P.STRETCH_FLAG:.0%}): bonds over-strained"
                )
    lz = float(manifest["box_angstrom"][2][1] - manifest["box_angstrom"][2][0])
    zspan = None
    if "c_zmax" in data and "c_zmin" in data:
        zspan = data["c_zmax"] - data["c_zmin"]
    elif frames:
        zspan = np.array([fr["zspan"] for fr in frames])
    diag["lz_data_A"] = lz
    if zspan is not None and len(zspan):
        bad = P.image_rows(zspan, lz, params["lj_cutoff"], params["boundary"])
        diag["zspan_max_A"] = float(np.max(zspan))
        diag["image_rows"] = int(bad.sum())
        if bad.any():
            run["flags"].append(
                f"z periodic: {int(bad.sum())} rows with bead z span + cutoff > Lz"
                f" ({lz:.1f} A): the film can interact with its z image"
            )
        if params["boundary"].split()[2] != "p":
            diag["lz_growth_A"] = max(0.0, float(np.max(zspan)) - lz)
    run["diagnostics"] = diag


def _maps(run_dir: Path, run: dict, frames: list[dict], axis) -> list[dict]:
    """Projected bead occupancy (x, y about the axis) at contact, peak, break and end."""
    c = run["curve"]
    picks = [
        ("contact", c.get("d_contact_nm")),
        ("peak", c.get("d_peak_nm")),
        ("break", run["break"]["d_break_nm"]),
        ("end", frames[-1]["d_nm"]),
    ]
    fd = np.array([fr["d_nm"] for fr in frames])
    reader = _reader(run_dir / "puncture.dcd")
    out = []
    try:
        for label, d in picks:
            if d is None:
                continue
            k = int(np.argmin(np.abs(fd - d)))
            ts = reader[k]
            lengths = np.asarray(ts.dimensions[:3], dtype=float)
            rel = H.wrap_about(ts.positions.astype(float), axis, lengths)
            ex, ey = H._grid(lengths, MAP_BIN_A)
            counts, _, _ = np.histogram2d(rel[:, 0], rel[:, 1], bins=(ex, ey))
            out.append({"label": label, "d_nm": float(fd[k]), "map": counts, "ex": ex, "ey": ey})
    finally:
        reader.close()
    return out


def _out_dir(runs: list[dict], out) -> Path:
    if out is not None:
        return Path(out)
    systems = sorted({r["system"] for r in runs})
    if len(runs) == 1:
        return Path("results") / "analysis" / systems[0] / runs[0]["stage"]
    names = sorted({_FILM_T.sub("_film", s) for s in systems})
    if len(names) != 1:
        raise PunctureError(f"runs of several systems ({', '.join(systems)}): give --out")
    return (
        Path("results")
        / "analysis"
        / (systems[0] if len(systems) == 1 else names[0])
        / ("puncture_compare")
    )


def _summary(run: dict) -> dict:
    c, b = run["curve"], run["break"]
    return {
        "f_peak_nN": c["f_peak_nN"],
        "d_peak_nm": c["d_peak_nm"],
        "d_break_nm": b["d_break_nm"],
        "w_break_aJ": b["w_break_aJ"],
        "w_peak_aJ": c["w_peak_aJ"],
    }


def analyze_puncture(
    run_dirs, out: str | Path | None = None, systems: str | Path = "systems", plots: bool = True
) -> tuple[dict, Path]:
    """Report dict and output directory for one or more puncture run directories."""
    runs = [analyze_run(Path(d), Path(systems)) for d in run_dirs]
    out_dir = _out_dir(runs, out)
    groups: dict[tuple, list] = {}
    for r in runs:
        r["summary"] = _summary(r)
        groups.setdefault((r["t_c"], r["v_m_s"], r["r_nm"]), []).append(r)
    pooled = [
        {
            "t_c": key[0],
            "v_m_s": key[1],
            "r_nm": key[2],
            "runs": [f"{r['system']}/{r['stage']}" for r in rs],
            "summary": {k: mean_sd(r["summary"][k] for r in rs) for k in SUMMARY_KEYS},
        }
        for key, rs in sorted(groups.items())
    ]
    report = {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "smooth_nm": P.SMOOTH_NM,
        "runs": runs,
        "pooled": pooled,
        "caveats": CAVEATS,
        "plots": {},
    }
    if plots:
        report["plots"] = make_plots(report, out_dir)
    return report, out_dir


# --------------------------------------------------------------------------- plots


def _legend(ax, size: int) -> None:
    if ax.get_legend_handles_labels()[0]:
        ax.legend(fontsize=size)


def make_plots(report: dict, out_dir: Path) -> dict:
    """force_depth.png, puncture_vs_T.png, rate_radius.png, diagnostics.png and (with
    DCD frames) film_maps.png; returns {name: {"file", "title"}}."""
    from sepsim.progress_plots import _save, plt

    out_dir.mkdir(parents=True, exist_ok=True)
    runs = report["runs"]
    plots = {}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for j, run in enumerate(runs):
        c, col = run["curve"]["curves"], f"C{j % 10}"
        ax1.plot(c["depth_nm"], c["force_nN"], color=col, alpha=0.25, lw=0.6)
        ax1.plot(c["depth_nm"], c["force_smooth_nN"], color=col, label=run["stage"])
        for key, mark in (("d_contact_nm", "o"), ("d_peak_nm", "^")):
            d = run["curve"].get(key)
            if d is not None:
                ax1.plot([d], [np.interp(d, c["depth_nm"], c["force_smooth_nN"])], mark, color=col)
        if run["break"]["d_break_nm"] is not None:
            ax1.axvline(run["break"]["d_break_nm"], color=col, ls=":", lw=0.8)
        if run["frames"]:
            ax2.plot(
                [f["d_nm"] for f in run["frames"]],
                [f["ahead"] for f in run["frames"]],
                color=col,
                label=run["stage"],
            )
    ax1.set(
        xlabel="depth d (nm)",
        ylabel="F on the indenter (nN)",
        title=f"F–d (lines: {P.SMOOTH_NM:g} nm moving average; dotted: break-through)",
    )
    ax2.axhline(P.AHEAD_MAX, color="0.5", ls=":", lw=0.8)
    ax2.set(
        xlabel="depth d (nm)",
        ylabel="beads ahead of the tip",
        title=f"material ahead (r < R/2, {P.AHEAD_A:g} Å below the tip)",
    )
    for ax in (ax1, ax2):
        _legend(ax, 7)
    _save(fig, out_dir / "force_depth.png")
    plots["force_depth"] = {"file": "force_depth.png", "title": "force–depth curves"}

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    series: dict[tuple, list] = {}
    for p in report["pooled"]:
        series.setdefault((p["v_m_s"], p["r_nm"]), []).append(p)
    for (v, r), ps in sorted(series.items()):
        t = [p["t_c"] for p in ps]
        for ax, key in zip(axes, ("f_peak_nN", "d_break_nm", "w_break_aJ"), strict=True):
            ms = [p["summary"][key] for p in ps]
            y = [m["mean"] if m else np.nan for m in ms]
            e = [(m["sd"] or 0.0) if m else 0.0 for m in ms]
            ax.errorbar(t, y, yerr=e, marker="o", capsize=3, label=f"{v:g} m/s, R {r:g} nm")
    for ax, lab in zip(axes, ("F_peak (nN)", "d_break (nm)", "W to break (aJ)"), strict=True):
        ax.set(xlabel="T (°C)", ylabel=lab)
        _legend(ax, 7)
    _save(fig, out_dir / "puncture_vs_T.png")
    plots["puncture_vs_T"] = {"file": "puncture_vs_T.png", "title": "F_peak, d_break, W vs T"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    for p in report["pooled"]:
        m = p["summary"]["f_peak_nN"]
        if not m:
            continue
        lab = f"{p['t_c']:g} °C"
        ax1.errorbar(
            [p["v_m_s"]],
            [m["mean"]],
            yerr=[m["sd"] or 0],
            marker="o",
            label=f"{lab}, R {p['r_nm']:g}",
        )
        ax2.errorbar(
            [p["r_nm"]],
            [m["mean"]],
            yerr=[m["sd"] or 0],
            marker="s",
            label=f"{lab}, {p['v_m_s']:g} m/s",
        )
    ax1.set(xscale="log", xlabel="v (m/s)", ylabel="F_peak (nN)", title="rate")
    ax2.set(xlabel="R (nm)", ylabel="F_peak (nN)", title="indenter radius")
    for ax in (ax1, ax2):
        _legend(ax, 6)
    _save(fig, out_dir / "rate_radius.png")
    plots["rate_radius"] = {"file": "rate_radius.png", "title": "F_peak vs speed and radius"}

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13, 4))
    for j, run in enumerate(runs):
        fr, col = run["frames"], f"C{j % 10}"
        if fr:
            d = [f["d_nm"] for f in fr]
            ax1.plot(d, [f["inside"] / f["n_beads"] for f in fr], color=col, label=run["stage"])
            st = [np.nan if f["stretch"] is None else f["stretch"] for f in fr]
            ax2.plot(d, st, color=col, label=run["stage"])
            if "bond_stretch_baseline" in run["diagnostics"]:
                b = run["diagnostics"]["bond_stretch_baseline"] + P.STRETCH_FLAG
                ax2.axhline(b, color=col, ls=":", lw=0.8)
        c = run["curve"]["curves"]
        diag = run["diagnostics"]
        ax3.axhline(diag["t_set_K"], color=col, ls=":", lw=0.8)
        for key, ls in (("t_near_K", "-"), ("t_far_K", "--")):
            if key in diag:
                ax3.plot(
                    [c["depth_nm"][0], c["depth_nm"][-1]],
                    [diag[key]] * 2,
                    color=col,
                    ls=ls,
                    label=f"{run['stage']} {key[2:-2]}",
                )
    ax1.axhline(P.INSIDE_FLAG, color="0.5", ls=":", lw=0.8)
    ax1.set(xlabel="depth d (nm)", ylabel="fraction of beads", title="beads inside the indenter")
    ax2.set(xlabel="depth d (nm)", ylabel="max bond stretch", title="bond stretch")
    ax3.set(xlabel="depth d (nm)", ylabel="T (K)", title="T near / far (mean over Stage 2)")
    for ax in (ax1, ax2, ax3):
        _legend(ax, 6)
    _save(fig, out_dir / "diagnostics.png")
    plots["diagnostics"] = {"file": "diagnostics.png", "title": "diagnostics"}

    mapped = [r for r in runs if r.get("_maps")][:4]
    if mapped:
        ncol = max(len(r["_maps"]) for r in mapped)
        fig, axes = plt.subplots(
            len(mapped), ncol, figsize=(3.2 * ncol, 3.0 * len(mapped)), squeeze=False
        )
        for i, run in enumerate(mapped):
            for j, m in enumerate(run["_maps"]):
                ax = axes[i][j]
                ax.imshow(
                    m["map"].T,
                    origin="lower",
                    cmap="viridis",
                    extent=(m["ex"][0] / 10, m["ex"][-1] / 10, m["ey"][0] / 10, m["ey"][-1] / 10),
                )
                ax.add_patch(plt.Circle((0, 0), run["r_nm"], fill=False, color="w", lw=0.8))
                ax.set_title(f"{run['stage']}: {m['label']} d {m['d_nm']:.1f} nm", fontsize=7)
                ax.set(xlabel="x (nm)", ylabel="y (nm)")
            for j in range(len(run["_maps"]), ncol):
                axes[i][j].axis("off")
        _save(fig, out_dir / "film_maps.png")
        plots["film_maps"] = {"file": "film_maps.png", "title": "projected bead occupancy"}
    return plots


# --------------------------------------------------------------------------- report


def _w(x) -> str:
    """Energy in aJ with kcal/mol."""
    return "n/a" if x is None else f"{x:.3g} aJ ({x / P.KCAL_MOL_AJ:.3g} kcal/mol)"


def render_markdown(r: dict) -> str:
    """results.md for a puncture report."""
    lines = ["# Puncture analysis (D57)", ""]
    lines.append(
        f"Generated {r['generated']}. F = z force on the indenter (tip + shaft), nN; depth d ="
        " tip bottom below the far-field film top at t0, nm. F_peak = maximum of a"
        f" {r['smooth_nm']:g} nm moving average (d_peak: largest raw F in that window); contact ="
        f" first smoothed F above max({P.CONTACT_SD:g} SD of the settle rows,"
        f" {P.CONTACT_FLOOR:.0%} F_peak). Break-through needs (i) smoothed F <"
        f" {P.BREAK_FRAC:.0%} F_peak after the peak over {P.BREAK_SUSTAIN_NM:g} nm and (iii)"
        f" ≤ {P.AHEAD_MAX} beads ahead of the tip (r < R/2, {P.AHEAD_A:g} Å) for"
        f" {P.AHEAD_FRAMES} frames; (ii) tip below the far-field bottom surface is reported."
        " W = ∫F dd from contact (1 aJ = 1 nN·nm = 143.9 kcal/mol)."
    )
    for run in r["runs"]:
        c, b, s = run["curve"], run["break"], run.get("reseal")
        diag = run["diagnostics"]
        lines += [
            "",
            f"## {run['system']} / {run['stage']}",
            "",
            (
                f"- {run['t_c']:g} °C, v {run['v_m_s']:g} m/s, R {run['r_nm']:g} nm, K"
                f" {run['k']:g} kcal/mol/Å³, axis offset {run['offset_nm'][0]:g},"
                f" {run['offset_nm'][1]:g} nm, travel {run['travel_nm']:.2f} nm, thermostat"
                f" {run['thermostat']}, boundary {run['boundary']}; status {run['status']};"
                f" `{run['run_dir']}`"
            ),
            f"- film thickness (far field, t0) {run['thickness_nm']:.2f} nm ({run['surfaces_from']})",
        ]
        lines += [f"- note: {n}" for n in run["notes"]]
        lines += [f"- **flag**: {n}" for n in run["flags"]]
        fpk = c["f_peak_nN"]
        lines += [
            "",
            "| quantity | value |",
            "|---|---|",
            f"| contact depth (nm) | {_f(c['d_contact_nm'])} |",
            f"| F_peak | {fpk:.3g} nN ({fpk * 1e3:.0f} pN){' (at end)' if c['peak_at_end'] else ''} |",
            f"| d_peak (nm) | {c['d_peak_nm']:.2f} |",
            f"| (i) force break d (nm) | {_f(c['d_break_force_nm'])} |",
            f"| (iii) clear ahead d (nm) | {_f(b['d_break_clear_nm'])} |",
            f"| (ii) tip below bottom surface d (nm) | {_f(run['d_bottom_nm'])} |",
            f"| **d_break** (i and iii, nm) | {_f(b['d_break_nm'])} |",
            f"| deflection contact → break (nm) | {_f(run['deflection_at_break_nm'])} |",
            f"| W to peak | {_w(c['w_peak_aJ'])} |",
            f"| W to break | {_w(b['w_break_aJ'])} |",
            "| re-seal | "
            + (
                "no break-through frames"
                if not s
                else (
                    f"resealed {s['t_heal_ps']:.0f} ps after break-through"
                    if s["resealed"]
                    else f"not resealed (free radius {s['r_free_end_A'] / 10:.2f} nm at the end)"
                )
            )
            + " |",
            (
                f"| T set / all / near / far (K) | {diag['t_set_K']:.1f} / {_f(diag.get('t_all_K'), '.1f')}"
                f" / {_f(diag.get('t_near_K'), '.1f')} / {_f(diag.get('t_far_K'), '.1f')} |"
            ),
            f"| beads inside the indenter (max) | {diag.get('inside_max', 'n/a')}"
            + (f" ({diag['inside_max_fraction']:.3%})" if "inside_max_fraction" in diag else "")
            + " |",
            (
                f"| max bond stretch (before contact) | {_f(diag.get('max_bond_stretch'), '.1%')}"
                f" ({_f(diag.get('bond_stretch_baseline'), '.1%')}) |"
            ),
            f"| z span max / Lz data (Å) | {_f(diag.get('zspan_max_A'), '.1f')} / {diag['lz_data_A']:.1f}"
            + (f"; Lz growth {diag['lz_growth_A']:.1f} Å" if "lz_growth_A" in diag else "")
            + (f"; image rows {diag['image_rows']}" if diag.get("image_rows") else "")
            + " |",
        ]
    lines += [
        "",
        "## Pooled at the same T, v and R (positions, tags)",
        "",
        "| T (°C) | v (m/s) | R (nm) | runs | F_peak (nN) | d_peak (nm) | d_break (nm) | W to break (aJ) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p in r["pooled"]:
        s = p["summary"]
        lines.append(
            f"| {p['t_c']:g} | {p['v_m_s']:g} | {p['r_nm']:g} | {len(p['runs'])} |"
            f" {_ms(s['f_peak_nN'], '.3g')} | {_ms(s['d_peak_nm'], '.2f')} |"
            f" {_ms(s['d_break_nm'], '.2f')} | {_ms(s['w_break_aJ'], '.3g')} |"
        )
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r["caveats"]]
    lines += plots_markdown(r.get("plots"))
    return "\n".join(lines) + "\n"


def write_results(report: dict, out_dir: Path) -> None:
    """Write results.json (curves thinned to <= 2000 points; no maps) and results.md."""
    slim = {
        **report,
        "runs": [{k: v for k, v in r.items() if k != "_maps"} for r in report["runs"]],
    }
    slim = json.loads(json.dumps(slim, default=_thin_json))
    write_atomic(
        out_dir,
        ((JSON_NAME, dump_json(slim, default=None)), (MD_NAME, render_markdown(report))),
    )
