"""`sepsim analyze crystal` (D59): crystal reference runs -> results.md, results.json, PNGs.

For a ``crystal`` run directory ``results/runs/<crystal id>/crystal/`` (deck
``in.crystal``, ``log.lammps``, the hold DCDs) of a `sepsim build crystal` system:

- per hold (thermo without its first ``HOLD_SKIP``, mean +- SEM from the statistical
  inefficiency on block means, D55, and the halves drift test): the cell a = Lx/na,
  b = Ly/nb, the repeat along the stems c = Lz/nz (CG: the rise per bead; UA: the c
  repeat of 2 CH2), a/b (sqrt(3) = 1.732 for hexagonal packing, 1.497 in the Busing
  cell), density vs the cell's 0.996 g/cm3 (Busing, 23 C), area per chain Lx Ly / stems
  vs a b / 2 = 18.3 A^2, T;
- per hold from <= ``max_frames`` evenly spaced DCD frames: the D26 crystallinity
  (:func:`sepsim.analysis.order.crystallinity` with ring chords: the stems are bonded to
  their own image) with the calibrated threshold and r_c of the D59 record when there is
  one, else the D56 fixed threshold 0.4 (labelled uncalibrated), the mean stem P2 =
  <P2(u.z)> of the chords against the stem axis z, the largest cluster as a fraction of
  the sites, first and last frame; a hold is **stable** when its last frame has a
  crystalline fraction >= ``STABLE_FRACTION`` and stem P2 >= ``STABLE_STEM_P2``;
- thermal expansion alpha = d ln L / dT of a, b, c and V (OLS of ln of the hold means vs
  T, its standard error from >= 3 points) over the stable holds;
- the optional ramp (``ramp=true``): crystallinity per frame vs T (linear in time) and the
  T where the fraction first drops below half its starting value (a stability bound of
  a superheated periodic crystal, not Tm).

Calibration (``calibrate``: melt sweep run directories, CG): per-site p2 of the crystal
holds whose stem P2 stays >= ``STABLE_STEM_P2`` (a threshold-free criterion) against the
per-site p2 of the melt sweep holds (``melt_t``: their temperatures, default every
hold), <= ``CAL_FRAMES`` frames per hold, at r_c = 1.4 sigma (the D56 setting) and the
``RC_SCAN`` factors; the threshold is the equal-error point of the two distributions
(:func:`sepsim.analysis.order.calibrate_threshold`, Anwar & Schilling, Polymer 2015, 76,
307). The record (threshold, r_c, error rates, the r_c scan, histograms, the source runs
with sha256 of their decks, logs and DCDs, date, code git) goes to
``data/crystals/calibration_<res>_pe.json`` (or ``calibration_out``), which the D56
monitor (:func:`sepsim.analyze.monitor_settings`) then reads. The r_c stays 1.4 sigma;
the scan only reports whether another factor separates the two better.
"""

from __future__ import annotations

import datetime as dt
import json
import warnings
from pathlib import Path

import numpy as np

from sepsim.analysis.lammps_log import read_log
from sepsim.analyze import (
    HOLD_SKIP,
    Window,
    calibration_path,
    crystal_parameters,
    monitor_settings,
    out_dir_for,
    segment_thermo,
)
from sepsim.progress import LOG_NAME, _block_rows, deck_system, load_json, parse_deck
from sepsim.reporting import (
    _f,
    _pm,
    dump_json,
    header_markdown,
    load_system_arrays,
    plots_markdown,
    report_header,
    write_atomic,
)
from sepsim.run import MANIFEST_NAME, sha256_file

VERSION = 1
MD_NAME, JSON_NAME = "results.md", "results.json"
DECK = "in.crystal"
MAX_FRAMES = 50  # frames per hold for the crystallinity
CAL_FRAMES = 20  # frames per hold for the calibration distributions
STABLE_FRACTION = 0.8  # last-frame crystalline fraction of a stable hold
STABLE_STEM_P2 = 0.8  # last-frame stem P2 of a stable hold (and of a calibration hold)
RC_SCAN = (1.2, 1.4, 1.6)  # r_c / sigma factors of the calibration check
RC_FACTOR = 1.4  # D56 r_c = 1.4 sigma, kept by the calibration
HIST_EDGES = np.linspace(-0.5, 1.0, 61)
EXP_DENSITY = 0.9963  # g/cm3, Busing 23 C cell (data/crystals/pe_orthorhombic_busing.yaml)

CAVEATS = [
    (
        "A periodic perfect crystal of infinite stems has no surfaces, ends or defects to"
        " nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds"
        " its stability from above; it is not the melting point."
    ),
    (
        "CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b ="
        " √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell."
    ),
    (
        "The barostat is anisotropic (x, y, z independent, couple none); the stems stay"
        " along z only while the crystal holds."
    ),
]


class CrystalAnalysisError(ValueError):
    """The run directory cannot be analysed (no crystal deck, no log, no system)."""


# --------------------------------------------------------------------------- frames


def crystal_arrays(system_dir: Path) -> dict:
    """Site rows and stems of a crystal system: every atom is a backbone site, the stems
    are its molecules (contiguous ids, in stem order), ``chains`` index into the rows."""
    import yaml

    from sepsim.build.datafile import read_data_file

    man = yaml.safe_load((system_dir / "manifest.yaml").read_text())
    if not man.get("crystal"):
        raise CrystalAnalysisError(f"{system_dir}: not a crystal system (no crystal block)")
    atoms = read_data_file(system_dir / "data.lmp").sorted_atoms()
    mol = atoms[:, 1].astype(np.int64)
    if np.any(np.diff(mol) < 0):
        raise CrystalAnalysisError(f"{system_dir}: stems are not contiguous in atom id order")
    starts = np.flatnonzero(np.r_[True, mol[1:] != mol[:-1]])
    chains = np.split(np.arange(len(atoms)), starts[1:])
    return {"manifest": man, "n_atoms": len(atoms), "rows": np.arange(len(atoms)), "chains": chains}


def dcd_frames(path: Path, rows, n_pick: int, n_atoms: int):
    """Positions of ``rows`` and the box of <= ``n_pick`` evenly spaced frames of a DCD;
    returns (frame indices, positions list, boxes list, number of frames)."""
    from MDAnalysis.coordinates.DCD import DCDReader

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        reader = DCDReader(str(path))
    try:
        if reader.n_atoms != n_atoms:
            raise ValueError(f"{path.name}: {reader.n_atoms} atoms, data.lmp has {n_atoms}")
        nf = reader.n_frames
        pick = np.unique(np.linspace(0, nf - 1, min(nf, n_pick)).round().astype(int))
        pos, box = [], []
        for f in pick:
            ts = reader[int(f)]
            if ts.dimensions is None or not np.all(np.isfinite(ts.dimensions)):
                raise ValueError(f"{path.name}: frames carry no box")
            pos.append(ts.positions[rows].astype(float))
            box.append(np.array(ts.dimensions, dtype=float))
    finally:
        reader.close()
    return pick, pos, box, nf


def frame_order(pos, box, chains, par: dict, threshold: float, ring: bool):
    """:func:`sepsim.analysis.order.crystallinity` of one frame (sites in chain order)
    and the stem P2 = <P2(u.z)> of its chords; returns (result, stem P2)."""
    from MDAnalysis.lib.mdamath import triclinic_vectors

    from sepsim.analysis.order import chord_vectors, crystallinity

    order = np.concatenate(chains)
    cid = np.concatenate([np.full(len(c), k) for k, c in enumerate(chains)])
    cell = triclinic_vectors(box)
    x = pos[order]
    res = crystallinity(
        x,
        cid,
        cell,
        r_c=par["r_c_A"],
        threshold=threshold,
        half_span=par["half_span"],
        l_proj=par["l_proj_A"],
        ring=ring,
    )
    u = chord_vectors(x, cid, cell, par["half_span"], ring=ring)
    stem = float(np.nanmean(1.5 * u[:, 2] ** 2 - 0.5))
    return res, stem


def hold_order(path: Path, arr: dict, settings: dict, n_pick: int) -> dict:
    """Crystallinity, stem P2 and largest cluster of the picked frames of one crystal hold
    DCD (ring chords), with the frame indices; ``p2`` keeps the per-site values."""
    pick, pos, box, nf = dcd_frames(path, arr["rows"], n_pick, arr["n_atoms"])
    frac, stem, largest, p2 = [], [], [], []
    for x, b in zip(pos, box, strict=True):
        res, s = frame_order(x, b, arr["chains"], settings, settings["threshold"], ring=True)
        frac.append(res.fraction)
        stem.append(s)
        largest.append(res.largest_cluster / res.n_sites if res.n_sites else 0.0)
        p2.append(res.p2)
    frac, stem, largest = np.array(frac), np.array(stem), np.array(largest)
    return {
        "available": True,
        "dcd": path.name,
        "frames_total": int(nf),
        "frames": len(pick),
        "frame_index": pick.tolist(),
        "fraction": {"mean": float(frac.mean()), "sd": float(frac.std())},
        "fraction_first": float(frac[0]),
        "fraction_last": float(frac[-1]),
        "stem_p2": {"mean": float(stem.mean()), "first": float(stem[0]), "last": float(stem[-1])},
        "largest_cluster_fraction": {"mean": float(largest.mean()), "last": float(largest[-1])},
        "p2_mean": float(np.nanmean(np.concatenate(p2))),
        "series": {"fraction": frac.tolist(), "stem_p2": stem.tolist()},
    }


# --------------------------------------------------------------------------- thermo


def _ms(win: Window) -> dict | None:
    return win.mean_sem()


def hold_cell(thermo: dict, crystal: dict) -> dict:
    """Cell lengths, density, area per chain and T of one hold (after HOLD_SKIP), mean +-
    SEM and the halves drift flag of each."""
    rep = crystal["repeats"]
    stems = crystal["stems"]
    block = _block_rows(thermo)
    series = {
        "a_A": thermo["Lx"] / rep["na"],
        "b_A": thermo["Ly"] / rep["nb"],
        "c_A": thermo["Lz"] / rep["nz"],
        "a_over_b": (thermo["Lx"] / rep["na"]) / (thermo["Ly"] / rep["nb"]),
        "density": thermo["Density"],
        "volume_A3": thermo["Volume"],
        "area_per_chain_A2": thermo["Lx"] * thermo["Ly"] / stems,
        "t_c": thermo["Temp"] - 273.15,
    }
    out: dict = {"rows": len(thermo["Step"])}
    drift = []
    for key, x in series.items():
        w = Window(x, HOLD_SKIP, block)
        out[key] = _ms(w)
        h = w.halves if len(w.w) >= 12 and w.ptp > 0 else None
        if h is not None and key != "t_c":
            out.setdefault("drift", {})[key] = {"delta": h[2], "delta_sem": h[3], "drift": h[4]}
            if h[4]:
                drift.append(key)
    out["drifting"] = drift
    if out["density"]:
        out["density_vs_exp"] = out["density"]["mean"] / EXP_DENSITY
    if out["area_per_chain_A2"]:
        out["area_vs_exp"] = (
            out["area_per_chain_A2"]["mean"] / crystal["lattice"]["area_per_chain_A2"]
        )
    return out


def expansion(rows: list[dict]) -> dict | None:
    """alpha = d ln L / dT (1/K) of a, b, c and V over the given hold rows (OLS of ln of
    the means vs T; standard error from >= 3 points), None for < 2 rows."""
    pts = [r for r in rows if r["cell"].get("volume_A3")]
    if len(pts) < 2:
        return None
    t = np.array([r["cell"]["t_c"]["mean"] for r in pts])
    out = {"t_c": t.tolist(), "holds": [r["t_set_c"] for r in pts]}
    for key in ("a_A", "b_A", "c_A", "volume_A3"):
        y = np.log([r["cell"][key]["mean"] for r in pts])
        slope, icpt = np.polyfit(t, y, 1)
        se = None
        if len(t) >= 3:
            res = y - (slope * t + icpt)
            se = float(np.sqrt(res @ res / (len(t) - 2) / ((t - t.mean()) @ (t - t.mean()))))
        out[key] = {"alpha_per_K": float(slope), "se": se}
    return out


# --------------------------------------------------------------------------- calibration


def _crystal_p2(run_dir, holds_segs, arr, par, r_c, n_pick) -> tuple[list, list]:
    """Per-site p2 values of the crystal holds (ring chords) at cutoff ``r_c``."""
    vals, per_hold = [], []
    p = par | {"r_c_A": r_c}
    for seg in holds_segs:
        _, pos, box, _ = dcd_frames(run_dir / seg.dcd[0], arr["rows"], n_pick, arr["n_atoms"])
        v = np.concatenate(
            [frame_order(x, b, arr["chains"], p, 0.0, ring=True)[0].p2 for x, b in zip(pos, box)]
        )
        v = v[~np.isnan(v)]
        vals.append(v)
        per_hold.append({"t_c": seg.t_c, "values": v})
    return vals, per_hold


def melt_sources(melt_dirs, systems: Path, melt_t) -> list[dict]:
    """Melt sweep holds (run dir, system arrays, segment) to calibrate against."""
    out = []
    for d in melt_dirs:
        d = Path(d)
        deck = d / "in.sweep"
        if not deck.is_file():
            raise CrystalAnalysisError(f"{d}: no in.sweep (melt runs are bulk sweeps)")
        system, _ = deck_system(deck)
        notes: list[str] = []
        arr = load_system_arrays(systems / str(system), notes)
        if arr is None:
            raise CrystalAnalysisError("; ".join(notes))
        segs = [s for s in parse_deck(deck) if s.sweep_kind == "hold" and not s.vdos]
        for s in segs:
            if melt_t is not None and not any(abs(s.t_c - t) < 1e-6 for t in melt_t):
                continue
            hold = [f for f in s.dcd if "_burst" not in f]
            if hold and (d / hold[0]).is_file():
                out.append({"run_dir": d, "system": system, "arr": arr, "seg": s, "dcd": hold[0]})
    if not out:
        raise CrystalAnalysisError("no melt hold DCDs found for the calibration")
    return out


def _melt_p2(sources, par, r_c, n_pick) -> tuple[list, list]:
    vals, per_hold = [], []
    p = par | {"r_c_A": r_c}
    for src in sources:
        arr = src["arr"]
        _, pos, box, _ = dcd_frames(
            src["run_dir"] / src["dcd"], arr["bb_rows"], n_pick, arr["n_atoms"]
        )
        v = np.concatenate(
            [frame_order(x, b, arr["chains"], p, 0.0, ring=False)[0].p2 for x, b in zip(pos, box)]
        )
        v = v[~np.isnan(v)]
        vals.append(v)
        per_hold.append({"system": src["system"], "t_c": src["seg"].t_c, "values": v})
    return vals, per_hold


def equal_error(c, m) -> tuple[float, float]:
    """(threshold, error rate): :func:`calibrate_threshold` and the fraction of crystal
    sites below it (= the fraction of melt sites at or above it at the equal-error point)."""
    from sepsim.analysis.order import calibrate_threshold

    t = calibrate_threshold(c, m)
    return t, 0.5 * (float(np.mean(c < t)) + float(np.mean(m >= t)))


def _files(run_dir: Path, names) -> list[dict]:
    return [
        {"name": n, "sha256": sha256_file(run_dir / n)} for n in names if (run_dir / n).is_file()
    ]


def calibration_record(
    run_dir: Path, holds_segs, arr: dict, melt_dirs, systems: Path, melt_t, n_pick=CAL_FRAMES
) -> dict:
    """The D59 calibration record (see the module docstring)."""
    import yaml

    from sepsim.ff.params import FORCEFIELD_DIR
    from sepsim.run import CODE_DIR, git_info

    man = arr["manifest"]
    par = crystal_parameters(man)
    sources = melt_sources(melt_dirs, systems, melt_t)
    ff = yaml.safe_load((FORCEFIELD_DIR / man["forcefield"]["file"]).read_text())
    if man["resolution"] == "cg":
        sigma = float(
            next(v for v in ff["pair_types"].values() if v["pattern"] == ["CM", "CM"])["sigma"]
        )
    else:
        sigma = par["r_c_A"] / RC_FACTOR  # UA/AA: r_c 6.5 A taken as the 1.4 "sigma" point
    scan, chosen = [], None
    for k in RC_SCAN:
        r_c = k * sigma
        cv, ch = _crystal_p2(run_dir, holds_segs, arr, par, r_c, n_pick)
        mv, mh = _melt_p2(sources, par, r_c, n_pick)
        c, m = np.concatenate(cv), np.concatenate(mv)
        thr, err = equal_error(c, m)
        scan.append({"factor": k, "r_c_A": r_c, "threshold": thr, "error_rate": err})
        if abs(k - RC_FACTOR) < 1e-9:
            chosen = (r_c, thr, err, c, m, ch, mh)
    r_c, thr, err, c, m, ch, mh = chosen
    best = min(scan, key=lambda s: s["error_rate"])

    def quant(v):
        return {str(q): float(np.quantile(v, q / 100)) for q in (5, 25, 50, 75, 95)}

    melt_runs = {}
    for src in sources:
        d = src["run_dir"]
        rec = melt_runs.setdefault(
            str(d.resolve()),
            {
                "run_dir": str(d.resolve()),
                "system": src["system"],
                "holds_c": [],
                "files": _files(d, ["in.sweep", LOG_NAME]),
            },
        )
        rec["holds_c"].append(src["seg"].t_c)
        rec["files"] += _files(d, [src["dcd"]])
    return {
        "kind": "sepsim D59 crystallinity calibration",
        "resolution": man["resolution"],
        "polymer": man.get("polymer", "pe"),
        "forcefield": {"file": man["forcefield"]["file"], "sha256": man["forcefield"]["sha256"]},
        "threshold": thr,
        "r_c_A": r_c,
        "r_c_sigma": RC_FACTOR,
        "sigma_A": sigma,
        "half_span": par["half_span"],
        "l_proj_A": par["l_proj_A"],
        "error_rate": err,
        "method": (
            "equal-error threshold of the per-site p2 distributions (sepsim.analysis.order."
            "calibrate_threshold; Anwar & Schilling, Polymer 2015, 76, 307): crystal holds"
            f" with stem P2 >= {STABLE_STEM_P2:g} (ring chords) vs melt sweep holds,"
            f" <= {n_pick} evenly spaced frames per hold"
        ),
        "r_c_scan": scan,
        "r_c_check": (
            f"r_c = {RC_FACTOR:g} sigma: error rate {err:.4f};"
            f" best of the scan {best['factor']:g} sigma ({best['error_rate']:.4f})"
        ),
        "crystal": {
            "run_dir": str(run_dir.resolve()),
            "system": man["id"],
            "holds_c": [s.t_c for s in holds_segs],
            "files": _files(run_dir, [DECK, LOG_NAME, *(s.dcd[0] for s in holds_segs)]),
            "n_values": len(c),
            "quantiles": quant(c),
        },
        "melt": {"runs": list(melt_runs.values()), "n_values": len(m), "quantiles": quant(m)},
        "per_hold": [
            {
                "source": "crystal",
                "system": man["id"],
                "t_c": h["t_c"],
                "fraction_at_threshold": float(np.mean(h["values"] >= thr)),
            }
            for h in ch
        ]
        + [
            {
                "source": "melt",
                "system": h["system"],
                "t_c": h["t_c"],
                "fraction_at_threshold": float(np.mean(h["values"] >= thr)),
            }
            for h in mh
        ],
        "histogram": {
            "edges": HIST_EDGES.tolist(),
            "crystal": np.histogram(c, HIST_EDGES, density=True)[0].tolist(),
            "melt": np.histogram(m, HIST_EDGES, density=True)[0].tolist(),
        },
        "date": dt.date.today().isoformat(),
        "code_git": git_info(CODE_DIR),
    }


def write_calibration(record: dict, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    return path


# --------------------------------------------------------------------------- report


def analyze_crystal(
    run_dir: str | Path,
    out: str | Path | None = None,
    systems: str | Path = "systems",
    max_frames: int = MAX_FRAMES,
    calibrate: list | tuple = (),
    melt_t: list[float] | None = None,
    calibration_out: str | Path | None = None,
    plots: bool = True,
) -> tuple[dict, Path]:
    """Analyse a crystal run directory (and calibrate against melt runs); returns
    (report, output directory)."""
    run_dir = Path(run_dir)
    deck = run_dir / DECK
    if not deck.is_file():
        raise CrystalAnalysisError(f"{run_dir}: no {DECK} (not a crystal run directory)")
    if not (run_dir / LOG_NAME).is_file():
        raise CrystalAnalysisError(f"{run_dir}: no {LOG_NAME}")
    system, resolution = deck_system(deck)
    system = system or run_dir.resolve().parent.name
    out_dir = out_dir_for(run_dir, system, out)
    try:
        arr = crystal_arrays(Path(systems) / system)
    except (OSError, KeyError) as exc:
        raise CrystalAnalysisError(f"system {system} not usable: {exc}") from None
    crystal = arr["manifest"]["crystal"]
    manifest = load_json(run_dir / MANIFEST_NAME)
    report = report_header(VERSION, run_dir, manifest, system, resolution)
    report["notes"] = []
    report["crystal"] = {k: crystal[k] for k in ("repeats", "stems", "sites_per_stem", "lattice")}
    segments = parse_deck(deck)
    thermo = segment_thermo(segments, read_log(run_dir / LOG_NAME), report["notes"])
    holds = [(s, th) for s, th in zip(segments, thermo, strict=True) if s.sweep_kind == "hold"]
    ramp = next(
        ((s, th) for s, th in zip(segments, thermo, strict=True) if "ramp from" in s.name), None
    )

    cal_rec = None
    if calibrate:
        cal_holds = []
        for s, th in holds:
            if th is None or not s.dcd or not (run_dir / s.dcd[0]).is_file():
                continue
            pick = hold_order(run_dir / s.dcd[0], arr, monitor_settings(arr["manifest"]), 3)
            if pick["stem_p2"]["last"] >= STABLE_STEM_P2:
                cal_holds.append(s)
        if not cal_holds:
            raise CrystalAnalysisError("no complete crystal hold with intact stems to calibrate")
        cal_rec = calibration_record(run_dir, cal_holds, arr, calibrate, Path(systems), melt_t)
        if calibration_out:
            path = Path(calibration_out)
        elif resolution:
            path = calibration_path(resolution)
        else:
            raise CrystalAnalysisError(
                f"{deck}: the deck header names no resolution ('# system <id> (<res>)'):"
                " give --calibration-out"
            )
        report["calibration_file"] = str(write_calibration(cal_rec, path))
        report["calibration"] = cal_rec

    settings = monitor_settings(arr["manifest"])
    if cal_rec is not None:  # the record just made, also when written elsewhere
        settings |= {
            "r_c_A": cal_rec["r_c_A"],
            "threshold": cal_rec["threshold"],
            "label": f"calibrated ({Path(report['calibration_file']).name}, {cal_rec['date']})",
            "calibration": Path(report["calibration_file"]).name,
        }
    report["settings"] = settings
    if settings.get("calibration_note"):
        report["notes"].append(settings["calibration_note"])
    rows = []
    for s, th in holds:
        row = {"index": s.sweep_index, "t_set_c": s.t_c, "done": th is not None, "name": s.name}
        row["cell"] = hold_cell(th, crystal) if th is not None else {}
        dcd = s.dcd[0] if s.dcd else None
        if th is None:
            row["order"] = {"available": False, "notes": ["hold not complete"]}
        elif dcd is None or not (run_dir / dcd).is_file():
            row["order"] = {"available": False, "notes": [f"{dcd} not found"]}
        else:
            try:
                row["order"] = hold_order(run_dir / dcd, arr, settings, max_frames)
            except (OSError, ValueError) as exc:
                row["order"] = {"available": False, "notes": [f"trajectory failed: {exc}"]}
        o = row["order"]
        row["stable"] = (
            o["fraction_last"] >= STABLE_FRACTION and o["stem_p2"]["last"] >= STABLE_STEM_P2
            if o.get("available")
            else None
        )
        rows.append(row)
    report["holds"] = rows
    done = [r for r in rows if r["done"]]
    stable = [r for r in done if r["stable"]]
    if done and all(r["stable"] is None for r in done):
        report["notes"].append("no hold trajectories: expansion over every complete hold")
        stable = done
    report["expansion"] = expansion(stable)
    report["ramp"] = _ramp(run_dir, ramp, arr, settings, max_frames) if ramp else None
    report["caveats"] = CAVEATS
    report["plots"] = make_plots(report, out_dir) if plots else {}
    return report, out_dir


def _ramp(run_dir: Path, ramp, arr, settings, max_frames) -> dict:
    """Crystallinity vs T over the ramp (T linear in time) and the first T where the
    fraction is below half its starting value."""
    seg, th = ramp
    out: dict = {"name": seg.name, "done": th is not None}
    dcd = seg.dcd[0] if seg.dcd else None
    if th is None or dcd is None or not (run_dir / dcd).is_file():
        out["available"] = False
        return out
    o = hold_order(run_dir / dcd, arr, settings, max_frames)
    # set points from the header "Segment N: ramp from T0 to T1 C at ..."
    t_lo, t_hi = (float(v) for v in seg.name.split("from", 1)[1].split(" C", 1)[0].split(" to "))
    t = t_lo + (t_hi - t_lo) * np.asarray(o["frame_index"]) / max(o["frames_total"] - 1, 1)
    frac = np.asarray(o["series"]["fraction"])
    below = np.flatnonzero(frac < 0.5 * frac[0])
    out.update(
        available=True,
        t_c=t.tolist(),
        fraction=frac.tolist(),
        stem_p2=o["series"]["stem_p2"],
        t_half_c=float(t[below[0]]) if len(below) else None,
        density_end=float(th["Density"][-1]),
    )
    return out


def make_plots(report: dict, out_dir: Path) -> dict:
    """cell.png (a, b, c and density vs T), order.png (crystalline fraction and stem P2
    per hold over its frames, ramp), calibration.png (p2 histograms and threshold)."""
    from sepsim.progress_plots import _save, plt

    out_dir.mkdir(parents=True, exist_ok=True)
    plots = {}
    rows = [r for r in report["holds"] if r["done"] and r["cell"].get("a_A")]
    if rows:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
        t = [r["cell"]["t_c"]["mean"] for r in rows]
        for key, lab in (("a_A", "a = Lx/na"), ("b_A", "b = Ly/nb"), ("c_A", "c = Lz/nz")):
            y = [r["cell"][key]["mean"] for r in rows]
            ax1.plot(t, np.array(y) / y[0], "o-", label=f"{lab} ({y[0]:.3f} Å at {t[0]:.0f} °C)")
        ax1.set(xlabel="T (°C)", ylabel="L / L(first hold)", title="cell lengths")
        d = [r["cell"]["density"]["mean"] for r in rows]
        mark = ["o" if r["stable"] is not False else "x" for r in rows]
        for x, y, mk in zip(t, d, mark, strict=True):
            ax2.plot(x, y, mk, color="C0")
        ax2.plot(t, d, "-", color="C0", lw=0.8)
        ax2.axhline(EXP_DENSITY, color="0.5", ls=":", label="Busing cell 23 °C (0.996)")
        ax2.set(xlabel="T (°C)", ylabel="density (g/cm³)", title="density (x: not stable)")
        for ax in (ax1, ax2):
            ax.legend(fontsize=7)
        _save(fig, out_dir / "cell.png")
        plots["cell"] = {"file": "cell.png", "title": "cell lengths and density per hold"}
    ordered = [r for r in report["holds"] if r["order"].get("available")]
    ramp = report.get("ramp") or {}
    if ordered or ramp.get("available"):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
        for r in ordered:
            s = r["order"]["series"]
            ax1.plot(s["fraction"], label=f"{r['t_set_c']:g} °C fraction")
            ax1.plot(s["stem_p2"], ls="--", color=ax1.lines[-1].get_color(), lw=0.8)
        ax1.set(
            xlabel="frame (evenly spaced over the hold)",
            ylabel="crystalline fraction (—), stem P2 (--)",
            title=f"holds; threshold {report['settings']['threshold']:.3g}"
            f" ({report['settings']['label']})",
            ylim=(-0.05, 1.05),
        )
        if ramp.get("available"):
            ax2.plot(ramp["t_c"], ramp["fraction"], label="fraction")
            ax2.plot(ramp["t_c"], ramp["stem_p2"], "--", label="stem P2")
            if ramp["t_half_c"] is not None:
                ax2.axvline(ramp["t_half_c"], color="0.5", ls=":", label="half the start")
        ax2.set(xlabel="T (°C)", title="ramp" if ramp else "ramp (none)", ylim=(-0.05, 1.05))
        for ax in (ax1, ax2):
            if ax.get_legend_handles_labels()[0]:
                ax.legend(fontsize=7)
        _save(fig, out_dir / "order.png")
        plots["order"] = {"file": "order.png", "title": "crystallinity and stem P2"}
    cal = report.get("calibration")
    if cal:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        e = np.asarray(cal["histogram"]["edges"])
        mid = 0.5 * (e[1:] + e[:-1])
        ax.plot(mid, cal["histogram"]["crystal"], label="crystal holds")
        ax.plot(mid, cal["histogram"]["melt"], label="melt holds")
        ax.axvline(cal["threshold"], color="0.3", ls=":", label=f"threshold {cal['threshold']:.3f}")
        ax.set(xlabel="site p2", ylabel="density", yscale="log", title=f"r_c {cal['r_c_A']:.2f} Å")
        ax.legend(fontsize=7)
        _save(fig, out_dir / "calibration.png")
        plots["calibration"] = {"file": "calibration.png", "title": "p2 calibration (D59)"}
    return plots


def render_markdown(r: dict) -> str:
    """results.md for a crystal report."""
    lines = header_markdown(r, "Crystal analysis", "crystal", "D59")
    lat = r["crystal"]["lattice"]
    rep = r["crystal"]["repeats"]
    st = r["settings"]
    lines += [
        (
            f"- {r['crystal']['stems']} stems x {r['crystal']['sites_per_stem']} sites,"
            f" {rep['na']} x {rep['nb']} x {rep['nz']} repeats of {lat['source']}"
            f" (a {lat['a_A']:g}, b {lat['b_A']:g}, c {lat['c_A']:g} Å at {lat['temperature_C']:g} °C,"
            f" {lat['density_g_cm3']:g} g/cm³, {lat['area_per_chain_A2']:.2f} Å² per chain)"
        ),
        (
            f"- crystallinity: D26 local P2 with ring chords, r_c {st['r_c_A']:.2f} Å,"
            f" threshold {st['threshold']:.3g} (**{st['label']}**); stable hold: last frame"
            f" fraction ≥ {STABLE_FRACTION:g} and stem P2 ≥ {STABLE_STEM_P2:g}"
        ),
    ]
    lines += [f"- note: {n}" for n in r["notes"]]
    lines += [
        "",
        "## Holds",
        "",
        (
            "Thermo after the first 10% of each hold (mean ± SEM). a = Lx/na, b = Ly/nb,"
            " c = Lz/nz (CG: rise per bead; UA: the 2-CH2 repeat). ρ/ρ_exp and A/A_exp against"
            f" the Busing cell ({EXP_DENSITY:g} g/cm³, {lat['area_per_chain_A2']:.2f} Å²)."
        ),
        "",
        (
            "| T (°C) | a (Å) | b (Å) | c (Å) | a/b | ρ (g/cm³) | ρ/ρ_exp | A/chain (Å²) |"
            " A/A_exp | drift | crystalline (mean; first → last) | stem P2 (last) |"
            " largest cluster (last) | stable |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in r["holds"]:
        c, o = row["cell"], row["order"]
        if not row["done"]:
            lines.append(f"| {row['t_set_c']:g} | not complete | | | | | | | | | | | | |")
            continue
        cr = (
            f"{o['fraction']['mean']:.3f}; {o['fraction_first']:.3f} → {o['fraction_last']:.3f}"
            if o.get("available")
            else "n/a"
        )
        stem = f"{o['stem_p2']['last']:.3f}" if o.get("available") else "n/a"
        lc = f"{o['largest_cluster_fraction']['last']:.3f}" if o.get("available") else "n/a"
        lines.append(
            f"| {c['t_c']['mean']:.1f} | {_pm(c['a_A'], '.4f')} | {_pm(c['b_A'], '.4f')} |"
            f" {_pm(c['c_A'], '.4f')} | {c['a_over_b']['mean']:.3f} | {_pm(c['density'], '.4f')}"
            f" | {_f(c.get('density_vs_exp'), '.3f')} | {_pm(c['area_per_chain_A2'], '.2f')} |"
            f" {_f(c.get('area_vs_exp'), '.3f')} | {', '.join(c['drifting']) or 'none'} | {cr} |"
            f" {stem} | {lc} | {row['stable']} |"
        )
    ex = r.get("expansion")
    lines += ["", "## Thermal expansion (stable holds)", ""]
    if ex:
        lines += [
            f"Holds {', '.join(f'{t:g}' for t in ex['holds'])} °C; α = d ln L/dT, OLS.",
            "",
            "| quantity | α (10⁻⁴ K⁻¹) |",
            "|---|---|",
        ]
        for key, lab in (("a_A", "a"), ("b_A", "b"), ("c_A", "c"), ("volume_A3", "V")):
            a = ex[key]
            se = "" if a["se"] is None else f" ± {a['se'] * 1e4:.3f}"
            lines.append(f"| {lab} | {a['alpha_per_K'] * 1e4:.3f}{se} |")
    else:
        lines.append("Fewer than two stable holds.")
    ramp = r.get("ramp")
    if ramp:
        lines += ["", "## Ramp", ""]
        if ramp.get("available"):
            th = ramp["t_half_c"]
            lines.append(
                f"{ramp['name']}: fraction {ramp['fraction'][0]:.3f} → {ramp['fraction'][-1]:.3f};"
                + (
                    f" below half its start from {th:.1f} °C (stability bound, not Tm)."
                    if th is not None
                    else " stays above half its start (crystal stable over the ramp)."
                )
            )
        else:
            lines.append("Ramp not complete or no trajectory.")
    cal = r.get("calibration")
    if cal:
        lines += [
            "",
            "## Calibration (D59)",
            "",
            f"Written to `{r['calibration_file']}`. {cal['method']}.",
            "",
            (
                f"- threshold **{cal['threshold']:.4f}** at r_c {cal['r_c_A']:.3f} Å"
                f" ({cal['r_c_sigma']:g} σ), equal-error rate {cal['error_rate']:.4f}"
            ),
            f"- {cal['r_c_check']}",
            (
                f"- crystal holds {', '.join(f'{t:g}' for t in cal['crystal']['holds_c'])} °C,"
                f" {cal['crystal']['n_values']} site values; melt"
                f" {cal['melt']['n_values']} site values from"
                f" {', '.join(m['system'] for m in cal['melt']['runs'])}"
            ),
            "",
            "| r_c / σ | r_c (Å) | threshold | error rate |",
            "|---|---|---|---|",
        ]
        lines += [
            f"| {s['factor']:g} | {s['r_c_A']:.3f} | {s['threshold']:.4f} | {s['error_rate']:.4f} |"
            for s in cal["r_c_scan"]
        ]
        lines += ["", "| source | system | T (°C) | fraction ≥ threshold |", "|---|---|---|---|"]
        lines += [
            f"| {h['source']} | {h['system']} | {h['t_c']:g} | {h['fraction_at_threshold']:.3f} |"
            for h in cal["per_hold"]
        ]
    lines += ["", "## Caveats", ""] + [f"- {c}" for c in r["caveats"]]
    lines += plots_markdown(r.get("plots"))
    return "\n".join(lines) + "\n"


def write_results(report: dict, out_dir: Path) -> None:
    """Write results.json and results.md atomically."""
    write_atomic(out_dir, ((JSON_NAME, dump_json(report)), (MD_NAME, render_markdown(report))))
