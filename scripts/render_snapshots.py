"""Render PNG snapshots (and optionally a movie) of a run trajectory with OVITO, headless.

Runs in the OVITO environment, not the project's:

    ~/projects/installations/ovito-viewer/bin/python scripts/render_snapshots.py \\
        results/runs/<system>/<stage>/<file>.dcd [--frames last] [--views side,top] \\
        [--color z] [--images 1 3 3] [--highlight 8] [--movie mp4] [--out DIR]

The topology is the system's data.lmp, found from the DCD path like scripts/ovito_view.py
(.../results/runs/<system>/<stage>/<file>.dcd -> .../systems/<system>/data.lmp); the look
(radii, bond width, colors, wrapping, hidden H) is ovito_view.STYLE. Chains are colored by
molecule id; --highlight N instead colors N random whole chains and greys out the rest.

Pore systems (``_pore`` in the id) default to a side view along x (z across the image).
Each frame is shifted along z so the gap sits mid-cell (ovito_view.center_gap; --no-center
keeps the simulated z), and periodic images are drawn around the cell: by default none
along the line of sight and three along z and across the film (side: 1 3 3, i.e.
gap | film | gap | film | gap with the cell's own gap in the middle; perspective: 2 2 2).
The cell is outlined in black, the images in grey. Bulk systems default to a perspective
view without images. Images go to results/figures/<system>/<stage>/ (gitignored) by
default, named <dcd>_<view>[_hl<N>]_f<frame>.png.

OVITO 3.17 (pip) needs a Vulkan driver for every renderer, Tachyon included. Without a
system driver (``sudo apt install mesa-vulkan-drivers``), the user-space Mesa lavapipe
copy in $SEPSIM_INSTALL_DIR/vulkan-lavapipe (default ~/projects/installations) is used:
the script re-executes itself with VK_DRIVER_FILES and LD_LIBRARY_PATH pointing there.
"""

from __future__ import annotations

import argparse
import itertools
import os
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
INSTALL = Path(os.environ.get("SEPSIM_INSTALL_DIR", Path.home() / "projects" / "installations"))
LAVAPIPE = INSTALL / "vulkan-lavapipe"
SYSTEM_ICDS = (Path("/usr/share/vulkan/icd.d"), Path("/etc/vulkan/icd.d"))

# view name -> (viewport type, camera direction, camera up); None: ovito_view.STYLE camera.
# The side views put z across the (landscape) image: the films stand as walls left and
# right of the gap; side_zup keeps z up (slab-profile orientation).
VIEWS = {
    "side": ("Ortho", (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),  # along x: z to the right, y up
    "side_zup": ("Ortho", (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),  # along x: y across, z up
    "front": ("Ortho", (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)),  # along y: z to the right, x up
    "top": ("Ortho", (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)),  # down z: the film surface
    "perspective": ("Perspective", None, (0.0, 0.0, 1.0)),
}
# Default periodic images (NX, NY, NZ) of pore systems per view: none along the line of
# sight, three along z (gap | film | gap | film | gap with the cell's gap in the middle)
# and across the film so it reads as a continuous sheet.
PORE_IMAGES = {
    "side": [1, 3, 3],
    "side_zup": [1, 3, 3],
    "front": [3, 1, 3],
    "top": [3, 3, 1],
    "perspective": [2, 2, 2],
}
IMAGE_CELL_COLOR = (0.75, 0.75, 0.75)
MARGIN = 1.2  # zoom out from the fitted view, leaving room for the label


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dcd", help=".../results/runs/<system>/<stage>/<file>.dcd")
    ap.add_argument(
        "--frames",
        default="last",
        help="'last', 'first', a comma list of first/last/frame indices (e.g. first,last or"
        " 0,50,last), or one integer N: N frames evenly spaced from first to last"
        " (default %(default)s)",
    )
    ap.add_argument(
        "--views",
        help="comma list of " + ", ".join(VIEWS) + " (default: side for pores,"
        " perspective for bulk)",
    )
    ap.add_argument(
        "--color", choices=["chain", "z", "type"], default="chain", help="default %(default)s"
    )
    ap.add_argument(
        "--images",
        type=int,
        nargs=3,
        metavar=("NX", "NY", "NZ"),
        help="periodic images to draw per direction, centred on the cell (outlined black;"
        " the images in grey), for every view. Default for pores, per view: side/side_zup"
        " 1 3 3 (gap | film | gap | film | gap, the film as a sheet), front 3 1 3, top 3 3 1,"
        " perspective 2 2 2; bulk 1 1 1",
    )
    ap.add_argument(
        "--highlight",
        type=int,
        default=0,
        metavar="N",
        help="color N random whole chains brightly, the rest faint grey (default off)",
    )
    ap.add_argument("--seed", type=int, default=0, help="--highlight chain choice (default 0)")
    ap.add_argument(
        "--no-center",
        action="store_true",
        help="pores: keep z as simulated (default: shift along z so the gap is mid-cell)",
    )
    ap.add_argument("--no-wrap", action="store_true", help="draw unwrapped coordinates")
    ap.add_argument("--data", help="topology (default: <project>/systems/<system>/data.lmp)")
    ap.add_argument("--out", help="output directory (default: results/figures/<system>/<stage>/)")
    ap.add_argument("--size", type=int, nargs=2, default=[1600, 1000], metavar=("W", "H"))
    ap.add_argument(
        "--renderer",
        choices=["standard", "tachyon", "opengl"],
        default="standard",
        help="OVITO renderer (all CPU via lavapipe here; tachyon is a ray tracer, ~10x slower;"
        " default %(default)s)",
    )
    ap.add_argument("--threads", type=int, default=2, help="CPU threads (default %(default)s)")
    ap.add_argument(
        "--movie",
        choices=["mp4", "gif", "png"],
        help="also render an animation per view (OVITO's built-in encoder; png: numbered frames)",
    )
    ap.add_argument("--movie-frames", type=int, default=100, help="frames in the movie (about)")
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--no-label", action="store_true", help="no system/stage/frame text label")
    return ap.parse_args(argv)


def _label(text: str) -> str:
    # Headless, the overlay measures its text a little short and clips the end: pad it.
    return text + " " * (len(text) // 5)


def _has_system_vulkan() -> bool:
    return any(d.is_dir() and any(d.glob("*.json")) for d in SYSTEM_ICDS)


def ensure_vulkan(threads: int) -> None:
    """Re-execute with the lavapipe driver in the environment if no Vulkan driver is set
    up (LD_LIBRARY_PATH is only read at process start, so it cannot be set in-process)."""
    env = dict(os.environ)
    env.setdefault("OVITO_THREAD_COUNT", str(threads))
    env.setdefault("LP_NUM_THREADS", str(threads))  # lavapipe rasterizer threads
    need_icd = "VK_DRIVER_FILES" not in env and "VK_ICD_FILENAMES" not in env
    if need_icd and not _has_system_vulkan() and (LAVAPIPE / "lvp_icd.json").is_file():
        env["VK_DRIVER_FILES"] = str(LAVAPIPE / "lvp_icd.json")
        lib = str(LAVAPIPE / "root" / "usr" / "lib" / "x86_64-linux-gnu")
        env["LD_LIBRARY_PATH"] = ":".join(p for p in (lib, env.get("LD_LIBRARY_PATH")) if p)
    if env != dict(os.environ):
        os.execve(sys.executable, [sys.executable, *sys.argv], env)


def _image_range(n: int) -> range:
    """Image indices ReplicateModifier makes for n copies: -(n-1)//2 .. n//2."""
    return range(-((n - 1) // 2), n // 2 + 1)


def _drop_particles(frame, data):
    """Pipeline function: keep only the cell (for the image outlines)."""
    if data.particles is not None:
        data.objects.remove(data.particles)


def pick_frames(spec: str, n: int) -> list[int]:
    """Frame indices for ``--frames`` (see the option help); out-of-range indices fail."""
    spec = spec.strip()
    if spec.isdigit() and "," not in spec:
        k = int(spec)
        if k < 1:
            raise SystemExit("--frames N needs N >= 1")
        if k == 1 or n == 1:
            return [n - 1]
        return sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})
    out = []
    for item in spec.split(","):
        item = item.strip()
        f = {"first": 0, "last": n - 1}.get(item)
        if f is None:
            f = int(item) if item.lstrip("-").isdigit() else None
            if f is None:
                raise SystemExit(f"--frames: bad item {item!r}")
            f = f + n if f < 0 else f
        if not 0 <= f < n:
            raise SystemExit(f"--frames: frame {item} outside 0..{n - 1}")
        out.append(f)
    return list(dict.fromkeys(out))


def main(argv=None) -> int:
    args = parse_args(argv)
    ensure_vulkan(args.threads)

    sys.path.insert(0, str(SCRIPTS))
    import numpy as np
    import ovito
    import ovito_view as ov
    from ovito.modifiers import ReplicateModifier
    from ovito.pipeline import Pipeline
    from ovito.qt_compat import QtCore
    from ovito.vis import (
        OpenGLRenderer,
        StandardRenderer,
        TachyonRenderer,
        TextLabelOverlay,
        Viewport,
    )

    def fit(vp):
        vp.zoom_all()
        vp.fov *= MARGIN

    dcd = Path(args.dcd).resolve()
    _, system, stage, _, root = ov.parse_path(dcd)
    data = Path(args.data) if args.data else None
    if data is None:
        roots = [r for r in (root, ROOT) if r is not None]
        data = next(
            (
                r / "systems" / system / "data.lmp"
                for r in roots
                if (r / "systems" / system / "data.lmp").is_file()
            ),
            None,
        )
        if data is None:
            raise SystemExit(f"no systems/{system}/data.lmp under {', '.join(map(str, roots))}")
    pore = "_pore" in system
    if args.images and min(args.images) < 1:
        raise SystemExit("--images: each count must be >= 1")
    views = (args.views or ("side" if pore else "perspective")).split(",")
    bad = [v for v in views if v not in VIEWS]
    if bad:
        raise SystemExit(f"--views: unknown {bad} (known: {', '.join(VIEWS)})")
    out = Path(args.out) if args.out else ROOT / "results" / "figures" / system / stage
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    pipeline = ov.pipeline_for(
        data,
        dcd,
        color=args.color,
        wrap=not args.no_wrap,
        center_gap=pore and not args.no_center,
        highlight=args.highlight,
        highlight_seed=args.seed,
    )
    cell_vis = pipeline.source.data.cell.vis
    cell_vis.enabled = True
    cell_vis.rendering_color = (0.0, 0.0, 0.0)
    ovito.scene.pipelines.clear()
    replicate = ReplicateModifier(adjust_box=False)
    pipeline.modifiers.append(replicate)
    pipeline.add_to_scene()
    # Faint outlines of the images: cell-only copies of the pipeline (sharing its
    # trajectory), placed at the image's cell offset for each frame.
    ghosts = {}
    shown = []

    def set_images(counts):
        replicate.num_x, replicate.num_y, replicate.num_z = counts
        replicate.enabled = list(counts) != [1, 1, 1]
        for ghost, _ in shown:
            ghost.remove_from_scene()
        shown.clear()
        for shift in itertools.product(*(_image_range(k) for k in counts)):
            if shift == (0, 0, 0):
                continue
            if shift not in ghosts:
                ghost = Pipeline(source=pipeline.source)
                ghost.modifiers.append(pipeline.modifiers[0])  # the trajectory
                ghost.modifiers.append(_drop_particles)
                vis = ghost.make_vis_element_independent(cell_vis)
                vis.rendering_color = IMAGE_CELL_COLOR
                vis.line_width = 0.4 * cell_vis.line_width
                ghosts[shift] = ghost
            shown.append((ghosts[shift], np.array(shift, dtype=float)))

    def place_outlines(frame):
        if shown:
            cell = np.asarray(shown[0][0].compute(frame).cell)
            for ghost, shift in shown:
                ghost.add_to_scene(translation=cell[:, :3] @ shift)

    n = pipeline.num_frames
    frames = pick_frames(args.frames, n)
    renderer = {
        "standard": StandardRenderer,
        "tachyon": TachyonRenderer,
        "opengl": OpenGLRenderer,
    }[args.renderer]()
    print(f"{dcd}: {n} frames; topology {data}; t_load {time.time() - t0:.1f} s", flush=True)

    tag = f"_hl{args.highlight}" if args.highlight else ""
    # The cell itself in a bold line (the automatic width matches the faint image outlines).
    cell_vis.line_width = 0.005 * float(
        np.max(np.diag(np.asarray(pipeline.source.data.cell)[:, :3]))
    )
    written = []
    for name in views:
        kind, cam, up = VIEWS[name]
        counts = args.images or (PORE_IMAGES[name] if pore else [1, 1, 1])
        set_images(counts)
        print(f"{name}: images {' '.join(map(str, counts))}", flush=True)
        vp = Viewport(
            type=getattr(Viewport.Type, kind),
            camera_dir=cam or ov.STYLE["camera_dir"],
            camera_up=up,
        )
        label = None
        if not args.no_label:
            label = TextLabelOverlay(
                text="",
                font_size=0.025,
                text_color=(0, 0, 0),
                alignment=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft,
            )
            label.offset_x, label.offset_y = 0.01, 0.01
            vp.overlays.append(label)
        for f in frames:
            t = time.time()
            ovito.scene.anim.current_frame = f
            place_outlines(f)
            fit(vp)
            if label is not None:
                label.text = _label(f"{system}   {stage}/{dcd.name}   frame {f}/{n - 1}")
            path = out / f"{dcd.stem}_{name}{tag}_f{f:05d}.png"
            vp.render_image(size=tuple(args.size), frame=f, filename=str(path), renderer=renderer)
            written.append(path)
            print(f"{path}  {time.time() - t:.1f} s", flush=True)
        if args.movie:
            every = max(1, n // max(args.movie_frames, 1))
            if label is not None:
                label.text = _label(f"{system}   {stage}/{dcd.name}   every {every} frame(s)")
            ovito.scene.anim.current_frame = n - 1
            place_outlines(n - 1)
            fit(vp)
            stem = f"{dcd.stem}_{name}{tag}_movie"
            path = out / (f"{stem}.{args.movie}" if args.movie != "png" else f"{stem}_*.png")
            t = time.time()
            vp.render_anim(
                filename=str(path),
                size=tuple(args.size),
                fps=args.fps,
                renderer=renderer,
                range=(0, n - 1),
                every_nth=every,
            )
            written.append(path)
            print(f"{path}  {time.time() - t:.1f} s ({len(range(0, n, every))} frames)", flush=True)
    print(f"{len(written)} file(s) in {out}; total {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
