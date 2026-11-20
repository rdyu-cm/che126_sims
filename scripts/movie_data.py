"""Per-frame data of the presentation clips of render_movies.py (pres_*), computed with the
project package, which the OVITO environment cannot import.

    uv run --frozen python scripts/movie_data.py CLIP [CLIP ...] [--frames 120]
        [--out DIR] [--data-root ROOT]

For each clip, into <out>/<clip>/data/ (default <out>: results/presentation/renders/movies,
the default of render_movies.py):

- traj.dcd: the clip's frames, evenly spaced in time over the clip's segments of the run
  (a sweep's step and hold DCDs read as one trajectory, a frame repeated at a segment
  boundary dropped), unwrapped and in atom-id order like the run's DCDs;
- series.npz: per clip frame the time t_ns (from the segments' start) and set-point
  T_set_k, the per-bead colour value ``color`` where OVITO cannot compute it (local
  alignment p2; NaN = no value), and the inset's curves (below).

Clips (SOURCES below; all CG PE C240, 40 chains):

- pres_melt_500K: the whole 500 K hold, 80 ns: the prep hold (hold.dcd, 20 ns) and its
  D47 extension (../extend/hold_ext.dcd, 60 ns, started from the prep's hold.data) read
  as one trajectory, as `sepsim progress` does; t = 0 at the first frame. The extension's
  steps restart at 0 (read_data): its frames are placed after the prep hold's last thermo
  step, when hold.data was written. Its first frame is that state, 568 steps after the
  prep's last frame (no repeat); both DCDs are unwrapped and the seam is continuous (COM
  step across it 1.9 Å, bead step 10.6 Å, vs 2.9 / 13.5 Å between prep frames).
  Colour: bead displacement since the first frame (Å), done in OVITO. Inset: the chain
  centre-of-mass MSD from the first frame (one time origin; the mean over chains removed
  per frame, as in sepsim.analysis.chain.com_msd_over_rg2, which averages over origins
  instead) against 2 <Rg^2> (over chains and frames of the run): D47 asks for MSD >=
  2 <Rg^2> at half the run.
- pres_anneal_down: the 500 K -> 25 C step cooling (prep cool.dcd, 8 x 5 ns).
- pres_anneal_up: the 25 -> 160 C heating sweep (sweep seg01..seg18, 165 ns).
  Both: colour = per-bead local chain alignment p2 of sepsim.analysis.order.crystallinity
  with the crystallinity monitor's settings (sepsim.analyze.monitor_settings: r_c = 1.4
  sigma = 6.31 Å, chord half-span 1, chain ends NaN); inset: set-point T and the thermo
  density (block means) vs time.
- pres_pore_gamma: the 5 nm slit-pore sweep (pore seg01..seg18). Colour: depth, done in
  OVITO (no colour array). Inset: gamma = (Lz/2)[Pzz - (Pxx+Pyy)/2] from the thermo
  (sepsim.analyze_pore.gamma_series), its running mean restarted at each segment.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CG = "pe_cg_amorph_n40_c240_s1"
PORE = "pe_cg_pore_w5nm_n40_c240_s1"
# run dir, deck, which deck segments, colour, inset; thermo block (rows) for the density
SOURCES = {
    "pres_melt_500K": {
        "system": CG,
        "run": "prep",
        "pick": lambda s: "hold.dcd" in s.dcd,
        "extend": "../extend/hold_ext.dcd",  # read after the picked segments
        "t0_first_frame": True,
        "color": None,  # displacement: OVITO's CalculateDisplacementsModifier
        "inset": "msd",
    },
    "pres_anneal_down": {
        "system": CG,
        "run": "prep",
        "pick": lambda s: s.cool_step is not None,
        "color": "p2",
        "inset": "thermo",
        "block": 100,  # 0.1 ns
    },
    "pres_anneal_up": {
        "system": CG,
        "run": "sweep",
        "pick": lambda s: s.sweep_kind is not None and not s.vdos,
        "color": "p2",
        "inset": "thermo",
        "block": 500,  # 0.5 ns
    },
    "pres_pore_gamma": {
        "system": PORE,
        "run": "pore",
        "pick": lambda s: s.sweep_kind is not None and not s.vdos,
        "color": None,
        "inset": "gamma",
    },
}
GAMMA_THIN = 20  # thermo rows per stored gamma running-mean point (20 ps)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clips", nargs="+", choices=list(SOURCES) + ["all"])
    ap.add_argument("--frames", type=int, default=120, help="clip frames (default %(default)s)")
    ap.add_argument("--out", help="default: results/presentation/renders/movies/")
    ap.add_argument("--data-root", type=Path, default=ROOT, help="checkout holding results/runs")
    return ap.parse_args(argv)


def dcd_reader(path):
    from MDAnalysis.coordinates.DCD import DCDReader

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return DCDReader(str(path))


def segments_and_thermo(run_dir: Path, pick):
    """The picked deck segments of a run with their thermo (sepsim.analyze.segment_thermo)."""
    from sepsim.analysis.lammps_log import read_log
    from sepsim.analyze import segment_thermo
    from sepsim.progress import parse_deck

    deck = next(run_dir.glob("in.*"))
    segs = parse_deck(deck)
    thermo = segment_thermo(segs, read_log(run_dir / "log.lammps"))
    out = [(s, th) for s, th in zip(segs, thermo, strict=True) if pick(s)]
    missing = [s.name for s, th in out if th is None]
    if missing:
        raise SystemExit(f"{run_dir}: segments not complete in the log: {', '.join(missing)}")
    return deck, out


def frame_table(run_dir: Path, segs):
    """(step, DCD path, frame index) of every frame of the segments' main DCDs (bursts
    left out), sorted by step, a step written twice (segment boundary) kept once."""
    rows, seen = [], set()
    for name in dict.fromkeys(d for s, _ in segs for d in s.dcd if "_burst" not in d):
        path = run_dir / name
        if not path.is_file():
            raise SystemExit(f"{path}: missing")
        r = dcd_reader(path)
        h = r._file.header
        for k in range(r.n_frames):
            step = h["istart"] + k * h["nsavc"]
            if step not in seen:
                seen.add(step)
                rows.append((step, path, k))
        r.close()
    return sorted(rows, key=lambda r: r[0])


def pick_frames(table, n):
    """n frames evenly spaced in step (nearest available frame, no repeats)."""
    steps = np.array([r[0] for r in table])
    want = np.linspace(steps[0], steps[-1], n)
    idx = np.unique(np.abs(steps[None, :] - want[:, None]).argmin(axis=1))
    return [table[i] for i in idx]


def read_positions(frames):
    """Positions (n, N, 3) and box dimensions (n, 6) of the picked frames."""
    pos, box, readers = [], [], {}
    for _, path, k in frames:
        r = readers.setdefault(path, dcd_reader(path))
        ts = r[k]
        pos.append(ts.positions.copy())
        box.append(ts.dimensions.copy())
    for r in readers.values():
        r.close()
    return np.array(pos), np.array(box)


def p2_frames(pos, box, sys_arr, settings):
    """Per-bead local alignment p2 (sepsim.analysis.order.crystallinity) of every frame;
    NaN for chain ends, sites without neighbours and non-backbone atoms."""
    from MDAnalysis.lib.mdamath import triclinic_vectors

    from sepsim.analysis.order import crystallinity

    chains = sys_arr["chains"]
    order = sys_arr["bb_rows"][np.concatenate(chains)]  # atom rows, chain by chain
    chain_id = np.concatenate([np.full(len(c), k) for k, c in enumerate(chains)])
    out = np.full(pos.shape[:2], np.nan, dtype=np.float32)
    for f in range(len(pos)):
        r = crystallinity(
            pos[f][order].astype(float),
            chain_id,
            triclinic_vectors(box[f]),
            r_c=settings["r_c_A"],
            threshold=settings["threshold"],
            half_span=settings["half_span"],
            l_proj=settings["l_proj_A"],
        )
        out[f, order] = r.p2
    return out


def com_msd(table, sys_arr, ns):
    """Chain COM MSD from the first frame of the hold, every DCD frame: (t_ns, msd in
    nm^2), <Rg^2> (nm^2, chains and frames) and the D47 origin-averaged MSD at half the
    run (nm^2). The DCDs are unwrapped (dump_modify unwrap yes)."""
    from sepsim.analysis.chain import chain_com_rg2, com_msd_over_rg2

    com = np.empty((len(table), len(sys_arr["mol_mass"]), 3))
    rg2 = np.empty(com.shape[:2])
    readers = {}
    for n, (_, path, k) in enumerate(table):
        x = readers.setdefault(path, dcd_reader(path))[k].positions
        c, g = chain_com_rg2(x, sys_arr["molecule"], sys_arr["masses"])
        com[n], rg2[n] = c[0], g[0]
    for r in readers.values():
        r.close()
    c = com - com.mean(axis=1, keepdims=True)  # no drift of the whole box
    msd = np.mean(np.sum((c - c[0]) ** 2, axis=2), axis=1) / 100.0
    _, msd_half, _, _ = com_msd_over_rg2(com, rg2, 1.0)
    return ns([r[0] for r in table]), msd, float(rg2.mean()) / 100.0, msd_half / 100.0


def block_means(x, block):
    n = len(x) // block
    return np.asarray(x[: n * block], dtype=float).reshape(n, block).mean(axis=1)


def make_clip(name, args, out_root):
    import MDAnalysis as mda
    import yaml

    from sepsim.analysis.chain import system_arrays
    from sepsim.analyze import monitor_settings

    src = SOURCES[name]
    run_dir = args.data_root / "results" / "runs" / src["system"] / src["run"]
    system_dir = args.data_root / "systems" / src["system"]
    deck, segs = segments_and_thermo(run_dir, src["pick"])
    dt_fs = segs[0][0].dt_fs
    step0 = int(segs[0][1]["Step"][0])  # the first segment's start: t = 0
    table = [r for r in frame_table(run_dir, segs) if r[0] >= step0]
    if src.get("extend"):  # a continuation from the last segment's write_data (step reset)
        path = run_dir / src["extend"]
        r = dcd_reader(path)
        h, offset = r._file.header, int(segs[-1][1]["Step"][-1])
        table += [(offset + h["istart"] + k * h["nsavc"], path, k) for k in range(r.n_frames)]
        r.close()
    if src.get("t0_first_frame"):
        step0 = table[0][0]

    def ns(steps):
        return (np.asarray(steps, dtype=float) - step0) * dt_fs * 1e-6

    frames = pick_frames(table, args.frames)
    pos, box = read_positions(frames)
    t_ns = ns([f[0] for f in frames])
    # set-point T of each frame: the segment whose thermo holds its step
    ends = np.array([th["Step"][-1] for _, th in segs])
    t_set = np.array([s.t_target_k for s, _ in segs])
    seg_of = np.minimum(np.searchsorted(ends, [f[0] for f in frames]), len(segs) - 1)
    data = {"t_ns": t_ns, "T_set_k": t_set[seg_of]}

    sys_arr = system_arrays(system_dir)
    if src["color"] == "p2":
        settings = monitor_settings(yaml.safe_load((system_dir / "manifest.yaml").read_text()))
        data["color"] = p2_frames(pos, box, sys_arr, settings)
        data["r_c_A"] = settings["r_c_A"]
        data["threshold"] = settings["threshold"]

    if src["inset"] == "msd":
        data["msd_t_ns"], data["msd_nm2"], data["rg2_nm2"], data["msd_d47_nm2"] = com_msd(
            table, sys_arr, ns
        )
        if src.get("extend"):  # where the extension starts
            data["seam_t_ns"] = ns(int(segs[-1][1]["Step"][-1]))
    elif src["inset"] == "thermo":
        b = src["block"]
        data["th_t_ns"] = np.concatenate([block_means(ns(th["Step"]), b) for _, th in segs])
        data["th_rho"] = np.concatenate([block_means(th["Density"], b) for _, th in segs])
        data["th_T_set_k"] = np.concatenate(
            [np.full(len(th["Step"]) // b, s.t_target_k) for s, th in segs]
        )
        data["seg_t_ns"] = np.array([[ns(th["Step"][0]), ns(th["Step"][-1])] for _, th in segs])
        data["seg_T_k"] = t_set
    elif src["inset"] == "gamma":
        from sepsim.analyze_pore import PL_TO_MN_M, deck_units, gamma_series

        factor = PL_TO_MN_M[deck_units(deck)]
        gt, gr, gs = [], [], []
        for k, (_, th) in enumerate(segs):
            g = gamma_series(th, factor)
            run = np.cumsum(g) / np.arange(1, len(g) + 1)
            sel = slice(GAMMA_THIN - 1, None, GAMMA_THIN)
            gt.append(ns(th["Step"])[sel])
            gr.append(run[sel])
            gs.append(np.full(len(run[sel]), k))
        data["g_t_ns"], data["g_run"], data["g_seg"] = map(np.concatenate, (gt, gr, gs))
        data["seg_t_ns"] = np.array([[ns(th["Step"][0]), ns(th["Step"][-1])] for _, th in segs])
        data["seg_T_k"] = t_set

    out = out_root / name / "data"
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "series.npz", **data)
    u = mda.Universe.empty(pos.shape[1], trajectory=True)
    with mda.Writer(str(out / "traj.dcd"), n_atoms=pos.shape[1]) as w:
        for x, b in zip(pos, box, strict=True):
            u.atoms.positions = x
            u.dimensions = b
            w.write(u.atoms)
    print(
        f"{name}: {len(frames)} frames, {t_ns[0]:.3g}..{t_ns[-1]:.4g} ns from"
        f" {len(table)} ({run_dir}) -> {out}",
        flush=True,
    )


def main(argv=None) -> int:
    args = parse_args(argv)
    out_root = (
        Path(args.out) if args.out else ROOT / "results" / "presentation" / "renders" / "movies"
    )
    for name in list(SOURCES) if "all" in args.clips else args.clips:
        make_clip(name, args, out_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
