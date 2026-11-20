"""Presentation movies of CG trajectories, ray-traced with OVITO's Tachyon renderer.

Runs in the OVITO environment, like render_snapshots.py:

    ~/projects/installations/ovito-viewer/bin/python scripts/render_movies.py CLIP [CLIP ...]
        [--stills] [--size W H] [--frames N] [--renderer tachyon|standard] [--out DIR]
        [--video-dir DIR] [--data-root ROOT]

Clips (CLIPS below; paths relative to the project root, frames of the DCD):

- melt_500K, hold_90C: the CG C240 bulk box at 500 K (prep hold) and 90 C (sweep hold) over
  the same 20 ns window, every bead coloured by its displacement since the first frame on
  one shared scale, so the two read as fast vs slow.
- anneal: the 500 K -> 25 C step cooling (prep), chains coloured, with a live T / density
  plot.
- hole, hole_slice: the R 3 nm hole at 25 C closing (0-0.35 ns after release), centred:
  the film's smooth surface over a 3 x 3 patch of periodic images, seen obliquely from
  above; and a 2.5 nm thick
  slice through the hole axis, side on, showing the mid-film pinch-off.
- pore: the 40-chain 5 nm slit pore at 160 C, side view with periodic images along y and
  z (gap | film | gap | film | gap), beads coloured by depth from the film mid-plane so
  the surface layers stand out.
- punct_25C_v3, punct_25C_v10, punct_25C_v100, punct_160C_v10: puncture (D57) of the
  rep441 film clamped beyond 8 nm (the c1 runs), a 2.5 nm slice through the indenter axis seen side on, chains coloured,
  the indenter (R 2 nm sphere + shaft) drawn in grey, and a live force-depth plot. Depth,
  force and break-through come from ``sepsim analyze puncture --out results/analysis/
  puncture_movies`` (its results.json), so the movie shows the same numbers as the analysis.

Presentation clips (pres_*): CG PE C240, 40 chains, each bead colour with a vertical
colour bar and a live inset plot. Their frames and per-frame data come from
scripts/movie_data.py (run it first, same --out), which writes <out>/<clip>/data/traj.dcd
(the clip's frames, evenly spaced in time over the run's segments) and series.npz:

- pres_melt_500K: the whole 500 K hold, 80 ns (the 20 ns prep hold and its 60 ns D47
  extension as one trajectory), beads coloured by displacement since the first frame
  (0-150 Å: about the 95th percentile at 80 ns); inset: the chain centre-of-mass MSD
  since the first frame (nm²) against 2⟨Rg²⟩, the D47 criterion, with the start of the
  extension and the first crossing marked.
- pres_anneal_down, pres_anneal_up: the 500 K -> 25 C step cooling (prep) and the
  25 -> 160 C heating sweep (sweep seg01..seg18), beads coloured by their local chain
  alignment p2 (sepsim.analysis.order.crystallinity, the crystallinity monitor's r_c and
  chord; chain ends grey) on the full range of p2, -0.5 (perpendicular neighbours) to 1
  (parallel), the same bar for both; inset: set-point T and density vs time.
- pres_pore_gamma: the 5 nm slit-pore sweep (pore seg01..seg18), the pore clip's view
  with beads coloured by depth from the film mid-plane (nm); inset: the gamma running
  mean of each sweep segment vs time with the LLDPE experimental gamma(T) = 39.05 -
  0.0725 T(C) mN/m (Moreira et al. 2003) as a dashed reference.

--stills renders the first, middle and last frame of each clip into <out>/<clip>/stills/
(a quick look). Otherwise --frames N evenly spaced frames (pres_*: all frames of
movie_data.py) go to <out>/<clip>/frames/ as PNGs and are encoded to <clip>.mp4 in
--video-dir (default <out>/<clip>/) with OVITO's video encoder; the GIF is made from the
PNGs with ``uv run python scripts/shrink_gif.py <out>/<clip>/frames ...``.
Default <out>: results/presentation/renders/movies/.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from render_snapshots import ensure_vulkan

CG = "results/runs/pe_cg_amorph_n40_c240_s1"
HOLE = "pe_cg_hole_r3nm_25C_n320_c240_s1_rep222"
COOL_K = [474.8, 449.5, 424.3, 399.1, 373.8, 348.6, 323.4, 298.15]  # prep cooling steps
STYLES = {  # bead radius / bond width overrides of ovito_view.STYLE (Å; CG beads)
    "beads": {},
    "tube": {"radii": [(2.0, 0.3), (20.0, 0.8), (1e9, 1.5)], "bond_width": 3.0},
}
DISP_MAX = 80.0  # Å, top of the shared displacement colour scale
CLIPS = {
    "melt_500K": {
        "dcd": f"{CG}/prep/hold.dcd",
        "range": (0, 1999),
        "t0_ns": 0.01,
        "frame_ns": 0.01,
        "title": "melt, 500 K",
        "color": "displacement",
    },
    "hold_90C": {
        "dcd": f"{CG}/sweep/seg09_hold_90C.dcd",
        "range": (0, 2000),
        "t0_ns": 0.0,
        "frame_ns": 0.01,
        "title": "90 °C",
        "color": "displacement",
    },
    "anneal": {
        "dcd": f"{CG}/prep/cool.dcd",
        "range": (0, 399),
        "t0_ns": 0.1,
        "frame_ns": 0.1,
        "title": "cooling 500 K → 25 °C",
        "color": "chain",
        "plot": True,
    },
    "hole": {
        "dcd": f"results/runs/{HOLE}/hole_free/hole_dense_s01.dcd",
        "data": f"systems/{HOLE}/data.lmp",
        "range": (0, 70),
        "t0_ns": 0.0,
        "frame_ns": 0.005,
        "title": "hole, R₀ = 3 nm, 25 °C",
        "color": "chain",
        "center_hole": True,
        "images": (3, 3, 1),
        "surface": True,
        "view": "oblique",
    },
    "hole_slice": {
        "dcd": f"results/runs/{HOLE}/hole_free/hole_dense_s01.dcd",
        "data": f"systems/{HOLE}/data.lmp",
        "range": (0, 70),
        "t0_ns": 0.0,
        "frame_ns": 0.005,
        "title": "hole, R₀ = 3 nm, 25 °C: 2.5 nm slice through the axis",
        "color": "z",
        "center_hole": True,
        "slice": 25.0,
        "view": "side_y",
    },
    "pore": {
        "dcd": "results/runs/pe_cg_pore_w5nm_n40_c240_s1/pore/seg18_hold_160C.dcd",
        "range": (0, 2500),
        "t0_ns": 0.0,
        "frame_ns": 0.01,
        "title": "5 nm slit pore, 160 °C",
        "color": "depth",
        "legend": "depth from the film mid-plane (Å)",
        "ticks": 10.0,
        "images": (1, 3, 3),
        "center_gap": True,
        "view": "side_zx",
    },
}
# presentation clips: frames and per-frame data from scripts/movie_data.py (<out>/<clip>/data)
P2_RANGE = (-0.5, 1.0)  # the full range of the local alignment p2, shared by both anneals
GAMMA_EXP = (39.05, -0.0725)  # LLDPE melt gamma = a + b T(C), mN/m (Moreira et al. 2003)
CLIPS["pres_melt_500K"] = {
    "movie_data": True,
    "data": "systems/pe_cg_amorph_n40_c240_s1/data.lmp",
    "title": "melt, 500 K",
    "color": "displacement",
    "disp_max": 150.0,  # Å: 80 ns, beyond the melt_500K scale
    "colorbar": ("bead displacement since t = 0 (Å)", 50.0, "%.0f"),
    "shift": 0.1,
    "inset": "msd",
}
for _name, _title in (("down", "cooling 500 K → 25 °C"), ("up", "heating 25 → 160 °C")):
    CLIPS[f"pres_anneal_{_name}"] = {
        "movie_data": True,
        "data": "systems/pe_cg_amorph_n40_c240_s1/data.lmp",
        "title": _title,
        "color": "array",
        "value_range": P2_RANGE,
        "colorbar": ("local chain alignment p₂", 0.5, "%.1f"),  # title, tick step, format
        "shift": 0.1,  # scene moved left by this fraction of the width: room for the inset
        "inset": "thermo",
    }
CLIPS["pres_pore_gamma"] = {
    "movie_data": True,
    "data": "systems/pe_cg_pore_w5nm_n40_c240_s1/data.lmp",
    "title": "5 nm slit pore",
    "color": "depth",
    "depth_unit": 10.0,  # Å per nm
    "colorbar": ("depth from the film mid-plane (nm)", 1.0, "%.0f"),
    "images": (1, 3, 3),
    "center_gap": True,
    "view": "side_zx",
    "shift": 0.16,
    "fov": 1.3,
    "inset": "gamma",
}
PUNCT_JSON = "results/analysis/puncture_movies/results.json"  # the clamped (c1) runs
for _t, _v in ((25, 3), (25, 10), (25, 100), (160, 10)):
    _run = f"results/runs/pe_cg_film_{_t}C_n640_c240_s1_rep441/puncture_{_t}C_v{_v}_R2nm_c1"
    CLIPS[f"punct_{_t}C_v{_v}"] = {
        "dcd": f"{_run}/puncture.dcd",
        "title": f"puncture, {_t} °C, {_v} m/s, R 2 nm, clamped beyond 8 nm",
        "color": "chain",
        "puncture": PUNCT_JSON,
        "slice": 25.0,
        "view": "side_y",
    }
# camera (direction, up); "perspective": the ovito_view STYLE direction
VIEWS = {
    "perspective": (None, (0.0, 0.0, 1.0)),  # the bulk box
    "side_x": ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),  # along x, z up
    "side_y": ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),  # along y, z up
    "side_zx": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),  # along x, z to the right
    "oblique": ((0.45, 0.6, -0.9), (0.0, 0.0, 1.0)),  # looking down onto a film
}


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clips", nargs="+", choices=list(CLIPS) + ["all"])
    ap.add_argument("--stills", action="store_true", help="first/middle/last frame only")
    ap.add_argument("--frames", type=int, default=120, help="movie frames (default %(default)s)")
    ap.add_argument("--size", type=int, nargs=2, default=[1920, 1080], metavar=("W", "H"))
    ap.add_argument("--renderer", choices=["tachyon", "standard"], default="tachyon")
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "2")))
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--out", help="default: results/presentation/renders/movies/")
    ap.add_argument("--video-dir", type=Path, help="where <clip>.mp4 goes (default <out>/<clip>/)")
    ap.add_argument(
        "--style",
        choices=list(STYLES),
        default="beads",
        help="beads (default) or tube: bonds as wide as the beads, each chain one tube",
    )
    ap.add_argument(
        "--data-root",
        type=Path,
        default=ROOT,
        help="checkout holding results/runs and systems (default: this one)",
    )
    return ap.parse_args(argv)


def puncture_series(clip, root):
    """The clip's run in the puncture analysis: per-DCD-frame time, tip centre and depth,
    the force-depth curve, the indenter radius and axis offset, and the break depth."""
    import json

    import numpy as np

    run_dir = (root / clip["dcd"]).parent
    res = json.loads((root / clip["puncture"]).read_text())
    run = next(
        r
        for r in res["runs"]
        if Path(r["run_dir"]).name == run_dir.name and r["system"] == run_dir.parent.name
    )
    fr = run["frames"]
    c = run["curve"]["curves"]
    return {
        "k": [f["k"] for f in fr],
        "t_ps": np.array([f["t_ps"] for f in fr]),
        "zc": np.array([f["zc"] for f in fr]),
        "d_nm": np.array([f["d_nm"] for f in fr]),
        "depth": np.array(c["depth_nm"]),
        "force": np.array(c["force_smooth_nN"]),
        "r_a": 10.0 * run["r_nm"],
        "offset_a": 10.0 * np.array(run["offset_nm"]),
        "d_break": (run.get("break") or {}).get("d_break_nm"),
    }


def add_indenter(series, cell):
    """A second pipeline drawing the indenter at the tip centre of each frame: a grey
    sphere of radius R plus a shaft of overlapping spheres up to 15 nm above it."""
    import numpy as np
    from ovito.data import DataCollection
    from ovito.pipeline import Pipeline, PythonSource

    xy = cell[:2, 3] + np.diag(cell[:2, :3]) / 2 + series["offset_a"]
    r = series["r_a"]
    dz = np.arange(0.0, 150.0 + 1e-9, r / 4)

    def source(frame, data: DataCollection):
        i = series["k"].index(frame) if frame in series["k"] else min(frame, len(series["k"]) - 1)
        pos = np.zeros((len(dz), 3))
        pos[:, :2] = xy
        pos[:, 2] = series["zc"][i] + dz
        p = data.create_particles(count=len(dz))
        p.create_property("Position", data=pos)
        p.create_property("Radius", data=np.full(len(dz), r))
        p.create_property("Color", data=np.tile([0.62, 0.64, 0.68], (len(dz), 1)))
        p.create_property("Transparency", data=np.full(len(dz), 0.35))

    pipe = Pipeline(source=PythonSource(function=source))
    pipe.add_to_scene()
    return pipe


def hole_center(xy, lo, length, bin_a=5.0):
    """(x, y) of the hole: the circular mean of the empty bins of the xy histogram."""
    import numpy as np

    nb = np.maximum((length / bin_a).astype(int), 8)
    h, _, _ = np.histogram2d(
        np.mod(xy[:, 0] - lo[0], length[0]),
        np.mod(xy[:, 1] - lo[1], length[1]),
        bins=nb,
        range=[(0, length[0]), (0, length[1])],
    )
    ix, iy = np.nonzero(h == 0)
    out = []
    for idx, n, L, o in ((ix, nb[0], length[0], lo[0]), (iy, nb[1], length[1], lo[1])):
        ang = 2 * np.pi * (idx + 0.5) / n
        mean = np.arctan2(np.sin(ang).mean(), np.cos(ang).mean()) % (2 * np.pi)
        out.append(o + mean / (2 * np.pi) * L)
    return np.array(out)


def build(clip: dict, args):
    """The clip's pipeline (added to the scene) and the colour-coding modifier, if any."""
    import numpy as np
    import ovito
    import ovito_view as ov
    from ovito.modifiers import (
        CalculateDisplacementsModifier,
        ColorCodingModifier,
        ConstructSurfaceModifier,
        ReplicateModifier,
    )

    root = args.data_root
    dcd = (
        args.out_root / args.name / "data" / "traj.dcd"
        if clip.get("movie_data")
        else root / clip["dcd"]
    )
    data = root / clip["data"] if "data" in clip else root / "systems" / dcd.parts[-3] / "data.lmp"
    color = clip["color"]
    pipeline = ov.pipeline_for(
        data,
        dcd,
        color=color if color in ("chain", "z") else "type",  # else coloured below
        center_gap=clip.get("center_gap", False),
        **STYLES[args.style],
    )
    first = clip.get("range", (0,))[0]  # puncture clips start at DCD frame 0
    traj = pipeline.modifiers[0]
    k = 1 + clip.get("center_gap", False)  # insert before the wrap
    if clip.get("puncture"):
        origin = np.asarray(pipeline.source.data.cell)[:, 3].copy()

        def open_z(frame, data):  # boundary p p m: beads pushed below the box stay there
            data.cell_.pbc = (True, True, False)
            # OVITO centres DCD frames on the origin (cell from -L/2, positions shifted by
            # -L/2 per frame; MDAnalysis gives the LAMMPS coordinates): undo the shift so the
            # beads are in the deck's frame, the one the indenter's tip z lives in, then put
            # back the data file's origin so the wrap keeps the indenter axis mid-box
            data.particles_.positions_[:] -= np.asarray(data.cell)[:, 3]
            data.cell_[:, 3] = origin

        pipeline.modifiers.insert(k, open_z)
        k += 1
    if clip.get("center_hole"):
        raw = traj.source.compute(first)
        cell = np.asarray(raw.cell)
        lo, length = cell[:2, 3], np.diag(cell[:2, :3])
        pos0 = np.asarray(raw.particles.positions)
        com0 = pos0[:, :2].mean(axis=0)
        shift0 = lo + length / 2 - hole_center(pos0[:, :2], lo, length)

        def center(frame, data):
            pos = data.particles_.positions_
            pos[:, :2] += shift0 - (pos[:, :2].mean(axis=0) - com0)

        pipeline.modifiers.insert(k, center)
        k += 1
    mapping = None
    if color == "displacement":
        disp = CalculateDisplacementsModifier(reference_frame=first)
        disp.assume_unwrapped_coordinates = True
        disp.vis.enabled = False
        pipeline.modifiers.insert(k, disp)
        mapping = ColorCodingModifier(
            property="Displacement Magnitude",
            start_value=0.0,
            end_value=clip.get("disp_max", DISP_MAX),
            gradient=ColorCodingModifier.Viridis(),
        )
        pipeline.modifiers.append(mapping)
    if color == "depth":
        # gap mid-cell (center_gap), so the film's mid-plane is the cell's z boundary
        lz = float(np.asarray(pipeline.source.data.cell)[2, 2])
        unit = clip.get("depth_unit", 1.0)  # Å per colour-bar unit

        def depth(frame, data):
            c = np.asarray(data.cell)
            z = np.mod(np.asarray(data.particles.positions)[:, 2] - c[2, 3], c[2, 2])
            data.particles_.create_property("Depth", data=np.minimum(z, c[2, 2] - z) / unit)

        pipeline.modifiers.append(depth)
        mapping = ColorCodingModifier(
            property="Depth",
            start_value=0.0,
            end_value=(lz - 50.0) / 2 / unit,  # the film half-thickness (5 nm gap)
            gradient=ColorCodingModifier.Magma(),
        )
        pipeline.modifiers.append(mapping)
    if color == "array":  # movie_data.py's per-bead value of each clip frame (NaN: grey)
        values = args.series["color"]

        def value(frame, data):
            v = values[min(frame, len(values) - 1)]
            data.particles_.create_property("Value", data=np.nan_to_num(v, nan=np.nanmin(v)))
            data.particles_.create_property("No value", data=np.isnan(v).astype(int))

        def grey(frame, data):
            nan = np.asarray(data.particles["No value"]) == 1
            data.particles_.colors_[nan] = (0.6, 0.6, 0.6)

        pipeline.modifiers.append(value)
        lo, hi = clip["value_range"]
        mapping = ColorCodingModifier(
            property="Value", start_value=lo, end_value=hi, gradient=ColorCodingModifier.Viridis()
        )
        pipeline.modifiers.append(mapping)
        pipeline.modifiers.append(grey)
    if clip.get("slice"):
        half = clip["slice"] / 2

        def slab(frame, data):  # keep a slab of beads through the (centred) hole axis
            c = np.asarray(data.cell)
            xc, yc = c[0, 3] + c[0, 0] / 2, c[1, 3] + c[1, 1] / 2
            pos = np.asarray(data.particles.positions)
            out = np.abs(pos[:, 1] - yc) > half
            if clip.get("puncture"):  # and a 22 nm window around the indenter axis
                out |= np.abs(pos[:, 0] - xc) > 110.0
            data.particles_.delete_elements(out)

        pipeline.modifiers.append(slab)
    if clip.get("surface"):
        surf = ConstructSurfaceModifier(radius=6.0, smoothing_level=12)
        surf.vis.surface_color = (0.35, 0.55, 0.85)
        surf.vis.show_cap = True  # close the faces cut by the cell: a solid slab
        surf.vis.cap_color = (0.25, 0.42, 0.7)
        surf.vis.highlight_edges = False
        surf.vis.surface_transparency = 0.0
        surf.vis.smooth_shading = True
        pipeline.modifiers.append(surf)
        # the surface alone reads best: hide the beads and bonds
        pipeline.source.data.particles.vis.enabled = False
        pipeline.source.data.particles.bonds.vis.enabled = False
    if clip.get("images"):
        nx, ny, nz = clip["images"]
        pipeline.modifiers.append(ReplicateModifier(num_x=nx, num_y=ny, num_z=nz, adjust_box=False))
    cell_vis = pipeline.source.data.cell.vis
    cell_vis.enabled = not clip.get("puncture")  # the cropped window, not the box
    cell_vis.rendering_color = (0.0, 0.0, 0.0)
    cell_vis.line_width = 0.004 * float(
        np.max(np.diag(np.asarray(pipeline.source.data.cell)[:, :3]))
    )
    ovito.scene.pipelines.clear()
    pipeline.add_to_scene()
    return pipeline, mapping


def anneal_series(pipeline, frames):
    """T (K) and density (g/cm3) per trajectory frame of the anneal clip."""
    import numpy as np

    src = pipeline.modifiers[0].source
    d = pipeline.source.data
    masses = {t.id: t.mass for t in d.particles.particle_types.types}
    total_amu = sum(masses[int(t)] for t in np.asarray(d.particles.particle_types))
    rho = []
    for f in frames:
        c = np.asarray(src.compute(f).cell)
        rho.append(total_amu * 1.66054 / float(np.prod(np.diag(c[:, :3]))))
    temps = [COOL_K[min(f // 50, len(COOL_K) - 1)] for f in frames]
    return np.array(temps), np.array(rho)


def caption(canvas, text, max_width=0.96, font_size=0.045):
    """The caption at the bottom left, its font shrunk if needed to fit within max_width
    (a fraction of the frame width)."""
    (_, _), (w, _) = canvas.text_bounds(text, pos=(0.02, 0.03), font_size=font_size)
    if w > max_width - 0.02:
        font_size *= (max_width - 0.02) / w
    canvas.draw_text(text, pos=(0.02, 0.03), font_size=font_size, color=(0.1, 0.1, 0.1))


def puncture_overlay(clip, ps):
    """Caption (title, time, depth, force) and a live force-depth plot: the whole smoothed
    curve in grey, the part up to the current depth in red, break-through dotted."""
    import numpy as np
    from ovito.qt_compat import QtCore, QtGui
    from ovito.vis import ViewportOverlayInterface

    depth, force = ps["depth"], ps["force"]
    dlo, dhi = float(depth.min()), float(depth.max())
    fhi = 1.15 * float(np.nanmax(force))
    flo = min(0.0, float(np.nanmin(force)))

    class Overlay(ViewportOverlayInterface):
        def render(self, canvas, *, frame, **kwargs):
            i = ps["k"].index(frame) if frame in ps["k"] else min(frame, len(ps["k"]) - 1)
            d = float(ps["d_nm"][i])
            f = float(np.interp(d, depth, force))
            text = (
                f"{clip['title']}    t = {ps['t_ps'][i] / 1000:.3g} ns    "
                f"depth {d:.1f} nm    F = {f:.2f} nN"
            )
            caption(canvas, text, font_size=0.04)
            w, h = canvas.logical_size
            x0, y0, pw, ph = 0.66 * w, 0.08 * h, 0.30 * w, 0.32 * h
            fh = 0.028 * h

            def px(v):
                return x0 + pw * (v - dlo) / (dhi - dlo)

            def py(v):
                return y0 + ph * (1 - (v - flo) / (fhi - flo))

            with canvas.qt_painter() as qp:
                qp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                font = qp.font()
                font.setPixelSize(int(fh))
                qp.setFont(font)
                qp.fillRect(QtCore.QRectF(x0, y0, pw, ph), QtGui.QColor(255, 255, 255, 210))
                qp.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60), 1.5))
                qp.drawRect(QtCore.QRectF(x0, y0, pw, ph))

                def line(xs, ys, color, width):
                    ok = np.isfinite(ys)
                    pts = [QtCore.QPointF(px(a), py(b)) for a, b in zip(xs[ok], ys[ok])]
                    if len(pts) > 1:
                        qp.setPen(QtGui.QPen(QtGui.QColor(*color), width))
                        qp.drawPolyline(QtGui.QPolygonF(pts))

                line(depth, force, (175, 175, 175), 2.0)
                done = depth <= d
                line(depth[done], force[done], (200, 50, 40), 3.0)
                qp.setBrush(QtGui.QColor(200, 50, 40))
                qp.drawEllipse(QtCore.QPointF(px(d), py(f)), 0.25 * fh, 0.25 * fh)
                if ps["d_break"] is not None:
                    qp.setPen(
                        QtGui.QPen(QtGui.QColor(40, 90, 200), 2.0, QtCore.Qt.PenStyle.DotLine)
                    )
                    xb = px(ps["d_break"])
                    qp.drawLine(QtCore.QPointF(xb, y0), QtCore.QPointF(xb, y0 + ph))

                def label(x, y, s, right=False):
                    qp.setPen(QtGui.QColor(40, 40, 40))
                    if right:
                        x -= qp.fontMetrics().horizontalAdvance(s)
                    qp.drawText(QtCore.QPointF(x, y), s)

                label(x0 - 6, py(fhi) + 0.9 * fh, f"{fhi:.2g}", right=True)
                label(x0 - 6, py(0.0) + 0.35 * fh, "0", right=True)
                label(x0, y0 - 0.5 * fh, "F on the indenter (nN)")
                if ps["d_break"] is not None:
                    label(x0 + pw, y0 - 0.5 * fh, "··· break-through", right=True)
                label(x0, y0 + ph + 1.3 * fh, f"{dlo:.0f}")
                label(x0 + pw, y0 + ph + 1.3 * fh, f"{dhi:.0f} nm", right=True)
                label(x0 + 0.5 * pw - 2.5 * fh, y0 + ph + 1.3 * fh, "depth")

    return Overlay()


def make_overlay(clip, series=None):
    """Caption (title, time, T) and, for the anneal, a live T / density plot."""
    from ovito.qt_compat import QtCore, QtGui
    from ovito.vis import ViewportOverlayInterface

    class Overlay(ViewportOverlayInterface):
        def render(self, canvas, *, frame, **kwargs):
            t = clip["t0_ns"] + frame * clip["frame_ns"]
            text = f"{clip['title']}    t = {t:.3g} ns"
            if series is not None:
                temps, rho, frames = series
                i = min(range(len(frames)), key=lambda j: abs(frames[j] - frame))
                text += f"    T = {temps[i]:.0f} K ({temps[i] - 273.15:.0f} °C)"
            # clear of the colour legend at the bottom right, if any
            caption(canvas, text, 0.62 if clip["color"] in ("displacement", "depth") else 0.96)
            if series is None:
                return
            temps, rho, frames = series
            w, h = canvas.logical_size
            x0, y0, pw, ph = 0.70 * w, 0.08 * h, 0.25 * w, 0.28 * h  # plot box, from the top
            with canvas.qt_painter() as qp:
                qp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                font = qp.font()
                font.setPixelSize(int(0.028 * h))
                qp.setFont(font)
                qp.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60), 1.5))
                qp.drawRect(QtCore.QRectF(x0, y0, pw, ph))

                def poly(vals, lo, hi, color):
                    pts = [
                        QtCore.QPointF(
                            x0 + pw * j / (len(vals) - 1),
                            y0 + ph * (1 - (v - lo) / (hi - lo)),
                        )
                        for j, v in enumerate(vals)
                    ]
                    qp.setPen(QtGui.QPen(QtGui.QColor(*color), 2.5))
                    qp.drawPolyline(QtGui.QPolygonF(pts))

                red, blue = (200, 60, 40), (40, 90, 200)
                rlo, rhi = rho.min() - 0.01, rho.max() + 0.01
                poly(temps, 280, 490, red)
                poly(rho, rlo, rhi, blue)
                xm = x0 + pw * i / (len(frames) - 1)
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2.0, QtCore.Qt.PenStyle.DashLine))
                qp.drawLine(QtCore.QPointF(xm, y0), QtCore.QPointF(xm, y0 + ph))
                fh = 0.028 * h

                def text(x, y, s, color=(40, 40, 40), right=False):
                    qp.setPen(QtGui.QColor(*color))
                    if right:
                        x -= qp.fontMetrics().horizontalAdvance(s)
                    qp.drawText(QtCore.QPointF(x, y), s)

                def ty(v, lo, hi):  # y of value v on an axis lo..hi
                    return y0 + ph * (1 - (v - lo) / (hi - lo)) + 0.35 * fh

                # left axis: T (K); right axis: density; bottom: time
                text(x0 - 6, ty(temps.max(), 280, 490), f"{temps.max():.0f}", red, right=True)
                text(x0 - 6, ty(temps.min(), 280, 490), f"{temps.min():.0f}", red, right=True)
                text(x0 + pw + 6, ty(rho.min(), rlo, rhi), f"{rho.min():.2f}", blue)
                text(x0 + pw + 6, ty(rho.max(), rlo, rhi), f"{rho.max():.2f}", blue)
                t_end = clip["t0_ns"] + frames[-1] * clip["frame_ns"]
                text(x0, y0 + ph + 1.3 * fh, "0")
                text(x0 + pw, y0 + ph + 1.3 * fh, f"{t_end:.0f} ns", right=True)
                text(x0 + 0.5 * pw - 1.2 * fh, y0 + ph + 1.3 * fh, "t")
                # key above the plot, with the current values
                text(x0, y0 - 0.5 * fh, f"T = {temps[i]:.0f} K", red)
                text(x0 + pw, y0 - 0.5 * fh, f"ρ = {rho[i]:.3f} g/cm³", blue, right=True)

    return Overlay()


def pres_overlay(clip, s):
    """Caption (title, time, set-point T) and the live inset plot of a pres_* clip, drawn
    up to the current frame: the chain COM MSD against 2<Rg^2> (msd), set-point T and
    density (thermo) or each segment's gamma running mean with the experimental line
    (gamma). ``s``: the clip's series.npz."""
    import numpy as np
    from ovito.qt_compat import QtCore, QtGui
    from ovito.vis import ViewportOverlayInterface

    class Overlay(ViewportOverlayInterface):
        def render(self, canvas, *, frame, **kwargs):
            i = min(frame, len(s["t_ns"]) - 1)
            t, tk = float(s["t_ns"][i]), float(s["T_set_k"][i])
            temp = f"{tk:.0f} K" if tk > 480 else f"{tk - 273.15:.0f} °C"
            caption(canvas, f"{clip['title']}    t = {t:.3g} ns    T = {temp}", 0.80)
            w, h = canvas.logical_size
            x0, y0, pw, ph = 0.64 * w, 0.08 * h, 0.30 * w, 0.30 * h  # plot box, from the top
            fh = 0.026 * h
            with canvas.qt_painter() as qp:
                qp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                font = qp.font()
                font.setPixelSize(int(fh))
                qp.setFont(font)
                qp.fillRect(QtCore.QRectF(x0, y0, pw, ph), QtGui.QColor(255, 255, 255, 210))
                qp.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60), 1.5))
                qp.drawRect(QtCore.QRectF(x0, y0, pw, ph))

                def line(xs, ys, xlim, ylim, color, width, style=None):
                    """Polyline of (xs, ys) on the axes xlim x ylim, clipped to the box."""
                    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
                    ok = np.isfinite(ys)
                    px = x0 + pw * (xs[ok] - xlim[0]) / (xlim[1] - xlim[0])
                    py = y0 + ph * (1 - (ys[ok] - ylim[0]) / (ylim[1] - ylim[0]))
                    if len(px) < 2:
                        return
                    pen = QtGui.QPen(QtGui.QColor(*color), width)
                    if style:
                        pen.setStyle(style)
                    qp.setPen(pen)
                    qp.setClipRect(QtCore.QRectF(x0, y0, pw, ph))
                    qp.drawPolyline(QtGui.QPolygonF([QtCore.QPointF(a, b) for a, b in zip(px, py)]))
                    qp.setClipping(False)

                def text(x, y, txt, color=(40, 40, 40), right=False):
                    qp.setPen(QtGui.QColor(*color))
                    if right:
                        x -= qp.fontMetrics().horizontalAdvance(txt)
                    qp.drawText(QtCore.QPointF(x, y), txt)

                def ty(v, lo, hi):  # text baseline for a label at value v on an axis lo..hi
                    return y0 + ph * (1 - (v - lo) / (hi - lo)) + 0.35 * fh

                def time_axis(xmax, label="t"):
                    text(x0, y0 + ph + 1.3 * fh, "0")
                    text(x0 + pw, y0 + ph + 1.3 * fh, f"{xmax:.0f} ns", right=True)
                    text(x0 + 0.5 * pw - 0.5 * fh, y0 + ph + 1.3 * fh, label)

                dash = QtCore.Qt.PenStyle.DashLine
                red, blue = (200, 60, 40), (40, 90, 200)
                if clip["inset"] == "msd":
                    mt, msd, ref = s["msd_t_ns"], s["msd_nm2"], 2 * float(s["rg2_nm2"])
                    xl = (0.0, float(mt[-1]))
                    yl = (0.0, 1.1 * max(float(msd.max()), ref))
                    now = mt <= t
                    line(xl, (ref, ref), xl, yl, (90, 90, 90), 1.5, dash)
                    if "seam_t_ns" in s:  # the extension's start
                        ts = float(s["seam_t_ns"])
                        line((ts, ts), yl, xl, yl, (175, 175, 175), 1.5)
                        text(x0 + pw * ts / xl[1] + 4, y0 + 1.2 * fh, "extension", (150, 150, 150))
                    line(mt[now], msd[now], xl, yl, red, 3.0)
                    cross = np.flatnonzero(msd >= ref)
                    if len(cross) and mt[cross[0]] <= t:  # first crossing of 2<Rg^2>
                        qp.setBrush(QtGui.QColor(255, 255, 255))
                        qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2.0))
                        qp.drawEllipse(
                            QtCore.QPointF(
                                x0 + pw * mt[cross[0]] / xl[1], y0 + ph * (1 - ref / yl[1])
                            ),
                            0.4 * fh,
                            0.4 * fh,
                        )
                    text(x0 - 6, ty(0.0, *yl), "0", right=True)
                    text(x0 - 6, ty(yl[1], *yl), f"{yl[1]:.0f}", right=True)
                    text(x0 + pw + 6, ty(ref, *yl), "2⟨Rg²⟩", (90, 90, 90))
                    time_axis(xl[1])
                    cur = float(msd[now][-1]) if now.any() else 0.0
                    text(
                        x0,
                        y0 - 0.5 * fh,
                        f"chain COM MSD = {cur:.1f} nm²  (2⟨Rg²⟩ = {ref:.1f} nm²)",
                        red,
                    )
                elif clip["inset"] == "thermo":
                    tt, temp_k, rho = s["th_t_ns"], s["th_T_set_k"], s["th_rho"]
                    xl = (0.0, float(tt[-1]))
                    tl = (temp_k.min() - 15, temp_k.max() + 15)
                    rl = (rho.min() - 0.01, rho.max() + 0.01)
                    now = tt <= t
                    line(tt, temp_k, xl, tl, (235, 190, 180), 2.0)  # the whole run, faint
                    line(tt, rho, xl, rl, (180, 195, 235), 2.0)
                    line(tt[now], temp_k[now], xl, tl, red, 2.5)
                    line(tt[now], rho[now], xl, rl, blue, 2.5)
                    line((t, t), tl, xl, tl, (0, 0, 0), 2.0, dash)
                    for v in (temp_k.max(), temp_k.min()):
                        text(x0 - 6, ty(v, *tl), f"{v - 273.15:.0f}", red, right=True)
                    text(x0 + pw + 6, ty(rho.min(), *rl), f"{rho.min():.2f}", blue)
                    text(x0 + pw + 6, ty(rho.max(), *rl), f"{rho.max():.2f}", blue)
                    time_axis(xl[1])
                    k = min(np.searchsorted(tt, t), len(tt) - 1)
                    text(x0, y0 - 0.5 * fh, f"T = {tk - 273.15:.0f} °C", red)
                    text(x0 + pw, y0 - 0.5 * fh, f"ρ = {rho[k]:.3f} g/cm³", blue, right=True)
                elif clip["inset"] == "gamma":
                    gt, gr, gs = s["g_t_ns"], s["g_run"], s["g_seg"]
                    seg_t, seg_c = s["seg_t_ns"], s["seg_T_k"] - 273.15
                    exp = GAMMA_EXP[0] + GAMMA_EXP[1] * seg_c
                    last = np.array([gr[gs == k][-1] for k in range(len(seg_c))])
                    yl = (
                        np.floor(min(exp.min(), last.min()) - 5),
                        np.ceil(max(exp.max(), last.max()) + 5),
                    )
                    xl = (0.0, float(seg_t[-1, 1]))
                    for k in range(len(seg_c)):  # the reference over the whole sweep
                        line(seg_t[k], (exp[k], exp[k]), xl, yl, (60, 60, 60), 1.5, dash)
                    for k in range(len(seg_c)):  # running means drawn from 1 ns into a segment
                        sel = (gs == k) & (gt <= t) & (gt >= seg_t[k, 0] + 1.0)
                        line(gt[sel], gr[sel], xl, yl, red, 2.5)
                    line((t, t), yl, xl, yl, (0, 0, 0), 2.0, dash)
                    text(x0 - 6, ty(yl[1], *yl), f"{yl[1]:.0f}", right=True)
                    text(x0 - 6, ty(yl[0], *yl), f"{yl[0]:.0f}", right=True)
                    time_axis(xl[1])
                    k = min(np.searchsorted(seg_t[:, 1], t), len(seg_c) - 1)
                    cur = gr[(gs == k) & (gt <= t)]
                    now = f"γ = {cur[-1]:.1f} mN/m" if len(cur) else "γ (mN/m)"
                    text(x0, y0 - 0.5 * fh, now + " (running mean)", red)
                    text(
                        x0 + pw,
                        y0 + ph + 2.6 * fh,
                        "- - LLDPE expt. (Moreira 2003)",
                        (60, 60, 60),
                        right=True,
                    )

    return Overlay()


def viewport(clip, pipeline, mapping, series=None):
    import ovito_view as ov
    from ovito.qt_compat import QtCore
    from ovito.vis import ColorLegendOverlay, PythonViewportOverlay, Viewport

    cam, up = VIEWS[clip.get("view", "perspective")]
    vp = Viewport(
        type=Viewport.Type.Perspective if cam is None else Viewport.Type.Ortho,
        camera_dir=cam or ov.STYLE["camera_dir"],
        camera_up=up,
    )
    if clip.get("puncture"):
        overlay = puncture_overlay(clip, series)
    elif clip.get("movie_data"):
        overlay = pres_overlay(clip, series)
    else:
        overlay = make_overlay(clip, series)
    vp.overlays.append(PythonViewportOverlay(delegate=overlay))
    if clip.get("colorbar"):  # vertical, at the right below the inset
        title, ticks, fmt = clip["colorbar"]
        legend = ColorLegendOverlay(
            modifier=mapping,
            title=title,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom,
            orientation=QtCore.Qt.Orientation.Vertical,
            rotate_title=True,
            format_string=fmt,
            legend_size=0.38,
            aspect_ratio=8.0,
            font_size=0.09,
            label_size=0.8,
            ticks_enabled=True,
            ticks_spacing=ticks,
            text_color=(0.1, 0.1, 0.1),
            offset_x=-0.03,
            offset_y=0.08,
        )
        vp.overlays.append(legend)
    elif mapping is not None:
        legend = ColorLegendOverlay(
            modifier=mapping,
            title=clip.get("legend", "bead displacement since t = 0 (Å)"),
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom,
            orientation=QtCore.Qt.Orientation.Horizontal,
            format_string="%.0f",
            legend_size=0.32,
            font_size=0.09,
            label_size=0.8,
            ticks_enabled=True,
            ticks_spacing=clip.get("ticks", 20.0),
            text_color=(0.1, 0.1, 0.1),
            offset_x=-0.05,  # headless, the label extent is measured short: keep clear of the edge
            offset_y=0.06,  # room for the tick labels below the bar
        )
        vp.overlays.append(legend)
    return vp


def render_clip(name, args, out_root):
    import numpy as np
    import ovito
    from ovito.vis import StandardRenderer, TachyonRenderer, Viewport

    clip = CLIPS[name]
    t0 = time.time()
    args.name, args.out_root, args.series = name, out_root, None
    if clip.get("movie_data"):  # scripts/movie_data.py's frames and per-frame data
        args.series = dict(np.load(out_root / name / "data" / "series.npz"))
    pipeline, mapping = build(clip, args)
    series = args.series
    if clip.get("movie_data"):
        lo, hi = 0, len(series["t_ns"]) - 1
    elif clip.get("puncture"):
        series = puncture_series(clip, args.data_root)
        add_indenter(series, np.asarray(pipeline.source.data.cell))
        lo, hi = series["k"][0], series["k"][-1]
    else:
        lo, hi = clip["range"]
    if args.stills:
        frames = [lo, (lo + hi) // 2, hi]
        out = out_root / name / "stills"
    else:
        n = hi - lo + 1 if clip.get("movie_data") else args.frames
        frames = sorted({round(f) for f in np.linspace(lo, hi, n)})
        out = out_root / name / "frames"
    out.mkdir(parents=True, exist_ok=True)
    if clip.get("plot"):
        temps, rho = anneal_series(pipeline, list(range(lo, hi + 1)))
        series = (temps, rho, list(range(lo, hi + 1)))
    vp = viewport(clip, pipeline, mapping, series)
    if args.renderer == "tachyon":
        renderer = TachyonRenderer(ambient_occlusion=True, antialiasing_samples=8, shadows=False)
    else:
        renderer = StandardRenderer()
    # one camera for the whole clip, fitted to the last frame with some room
    ovito.scene.anim.current_frame = hi
    vp.zoom_all()
    vp.fov *= clip.get("fov", 1.12)
    if clip.get("shift"):  # move the scene left by this fraction of the width
        cam, up = np.array(vp.camera_dir, float), np.array(vp.camera_up, float)
        cam /= np.linalg.norm(cam)
        right = np.cross(cam, up) / np.linalg.norm(np.cross(cam, up))
        pos = np.asarray(vp.camera_pos, float)
        if vp.type == Viewport.Type.Perspective:  # fov: the vertical view angle, at the cell centre
            c = np.asarray(pipeline.source.data.cell)
            centre = c[:, 3] + c[:, :3].sum(axis=1) / 2
            half = np.dot(centre - pos, cam) * np.tan(vp.fov / 2)
        else:  # fov: half the visible height
            half = vp.fov
        vp.camera_pos = tuple(pos + right * clip["shift"] * 2 * half * args.size[0] / args.size[1])
    paths = []
    for k, f in enumerate(frames):
        t = time.time()
        path = out / f"{name}_{k:04d}.png"
        vp.render_image(size=tuple(args.size), frame=f, filename=str(path), renderer=renderer)
        paths.append(path)
        print(f"{path}  frame {f}  {time.time() - t:.1f} s", flush=True)
    print(f"{name}: {len(paths)} image(s) in {time.time() - t0:.0f} s", flush=True)
    return paths


def encode_mp4(paths, dst, fps, size):
    """Encode PNG frames to a video with OVITO's encoder: an empty scene whose overlay paints
    frame k's image, rendered with the (cheap) standard renderer."""
    import ovito
    from ovito.data import DataCollection
    from ovito.pipeline import Pipeline, PythonSource
    from ovito.qt_compat import QtGui
    from ovito.vis import (
        PythonViewportOverlay,
        StandardRenderer,
        Viewport,
        ViewportOverlayInterface,
    )

    images = [str(p) for p in paths]

    class Frames(ViewportOverlayInterface):
        def render(self, canvas, *, frame, **kwargs):
            canvas.draw_image(QtGui.QImage(images[min(frame, len(images) - 1)]), (0, 0), (1, 1))

    def source(frame, data: DataCollection):  # an empty frame per image
        pass

    ovito.scene.pipelines.clear()
    src = PythonSource(function=source)
    pipe = Pipeline(source=src)
    pipe.add_to_scene()
    vp = Viewport(type=Viewport.Type.Ortho)
    vp.overlays.append(PythonViewportOverlay(delegate=Frames()))
    ovito.scene.anim.last_frame = len(images) - 1
    vp.render_anim(
        filename=str(dst),
        size=tuple(size),
        fps=fps,
        renderer=StandardRenderer(),
        range=(0, len(images) - 1),
    )
    print(f"{dst}: {len(images)} frames", flush=True)


def main(argv=None) -> int:
    args = parse_args(argv)
    ensure_vulkan(args.threads)
    out_root = (
        Path(args.out) if args.out else ROOT / "results" / "presentation" / "renders" / "movies"
    )
    names = list(CLIPS) if "all" in args.clips else args.clips
    for name in names:
        paths = render_clip(name, args, out_root)
        if not args.stills:
            video = args.video_dir or out_root / name
            video.mkdir(parents=True, exist_ok=True)
            encode_mp4(paths, video / f"{name}.mp4", args.fps, args.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
