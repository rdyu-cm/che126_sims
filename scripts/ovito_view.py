"""Interactive OVITO viewer for run trajectories, for scripts/view.ipynb.

Runs in its own environment (~/projects/installations/ovito-viewer: ovito, ipywidgets,
jupyterlab), not the project's, so the simulation code has no OVITO dependency.
Topology (types, bonds, molecule ids) comes from the system's data.lmp; the DCD frames
replace the positions (DCDs are unwrapped and in atom-id order, like data.lmp).
Runs on rdyu-rog are copied on demand into results/viewer/rdyu-rog/<system>/<stage>/.
Every view uses STYLE below; edit it once to change the look of all views.
"""

import colorsys
import subprocess
from pathlib import Path

import ipywidgets
import numpy as np
import ovito
from ovito.io import import_file
from ovito.modifiers import (
    ColorCodingModifier,
    DeleteSelectedModifier,
    ExpressionSelectionModifier,
    LoadTrajectoryModifier,
    WrapPeriodicImagesModifier,
)
from ovito.vis import Viewport

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results" / "runs"
CACHE = ROOT / "results" / "viewer"
REMOTE = "rdyu-rog"

# The look of every view; load()/show() keyword arguments override single entries.
STYLE = {
    "color": "chain",  # "chain" (molecule id), "z" (height) or "type"
    "chain_gradient": "Rainbow",  # any ColorCodingModifier gradient: Rainbow, Viridis, Jet, ...
    "z_gradient": "Viridis",
    # (mass below amu, radius Å): H, C/UA, CG bead. CG beads are drawn smaller than their
    # size (sigma ~4.5 Å) so the bonds show and chains read as strings of beads.
    "radii": [(2.0, 0.3), (20.0, 0.8), (1e9, 1.2)],
    # Å; a number, or (heaviest type mass below amu, width) pairs: AA/UA, CG
    "bond_width": [(20.0, 0.5), (1e9, 1.4)],
    "hide_h": True,
    "wrap": True,  # wrap atoms into the periodic box
    "center_gap": False,  # shift along z so the slit-pore gap is mid-box (load(): pores)
    "highlight": 0,  # N > 0: N random chains in bright colors, the rest faint grey
    "highlight_seed": 0,
    "highlight_transparency": 0.7,  # of the other chains (0 opaque .. 1 invisible)
    "camera_dir": (1.0, 0.6, -0.5),
    "width": "900px",
    "height": "600px",
    "frame_ms": 200,  # play-button speed
}


def runs(node="local"):
    """{(system, stage): [dcd names]} for the run directories on `node`."""
    if node == "local":
        files = [str(p.relative_to(RUNS)) for p in RUNS.glob("*/*/*.dcd")]
    else:
        out = subprocess.run(
            ["ssh", node, f"cd {RUNS} && ls -1 */*/*.dcd"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        files = out.split()
    found = {}
    for f in sorted(files):
        system, stage, name = f.split("/")
        found.setdefault((system, stage), []).append(name)
    return found


def fetch(system, stage, dcd, node=REMOTE):
    """Copy one DCD (and the stage's data files) from `node`; returns the local dir."""
    dest = CACHE / node / system / stage
    dest.mkdir(parents=True, exist_ok=True)
    src = f"{node}:{RUNS / system / stage}/"
    subprocess.run(
        ["rsync", "-a", "--include", dcd, "--include", "*.data", "--exclude", "*", src, f"{dest}/"],
        check=True,
    )
    return dest


def parse_path(path):
    """(node, system, stage, dcd name, project root or None) of a DCD path:
    .../results/runs/<system>/<stage>/<file>.dcd, a results/viewer/<node>/... copy, or
    "rdyu-rog:<path on rdyu-rog>"."""
    node, rest = "local", str(path)
    if rest.startswith(REMOTE + ":"):
        node, rest = REMOTE, rest[len(REMOTE) + 1 :]
    parts = Path(rest).parts
    if len(parts) >= 5 and parts[-5:-3] == ("results", "runs"):
        (system, stage, dcd), root = parts[-3:], parts[:-5]
    elif len(parts) >= 6 and parts[-6:-4] == ("results", "viewer"):  # an earlier copy
        node, (system, stage, dcd), root = parts[-4], parts[-3:], parts[:-6]
    else:
        raise ValueError(
            f"{path}: expected .../results/runs/<system>/<stage>/<file>.dcd"
            " or .../results/viewer/<node>/<system>/<stage>/<file>.dcd"
        )
    return node, system, stage, dcd, Path(*root) if root else None


def load_path(path, **style):
    """Pipeline for a DCD given by path, e.g. pasted from VS Code's "Copy Path":
    .../results/runs/<system>/<stage>/<file>.dcd, a results/viewer/<node>/... copy, or
    "rdyu-rog:<path on rdyu-rog>" (copied over first)."""
    node, system, stage, dcd, _ = parse_path(path)
    return load(system, stage, dcd, node=node, **style)


def load(system, stage, dcd, node="local", data=None, **style):
    """Pipeline for one trajectory, drawn with STYLE (keyword arguments override entries).

    data: topology file; default systems/<system>/data.lmp.
    """
    run_dir = RUNS / system / stage if node == "local" else fetch(system, stage, dcd, node)
    style.setdefault("center_gap", "_pore" in system)
    return pipeline_for(data or ROOT / "systems" / system / "data.lmp", run_dir / dcd, **style)


def pipeline_for(data, dcd, **style):
    """Pipeline of the topology file `data` (LAMMPS data, atom_style full) plus the
    trajectory `dcd`, drawn with STYLE (keyword arguments override entries)."""
    st = {**STYLE, **style}
    pipeline = import_file(str(data), atom_style="full")
    traj = LoadTrajectoryModifier()
    traj.source.load(str(dcd))
    pipeline.modifiers.append(traj)
    if st["center_gap"]:
        pipeline.modifiers.append(center_gap)
    if st["wrap"]:
        pipeline.modifiers.append(WrapPeriodicImagesModifier())
    if st["hide_h"]:
        pipeline.modifiers.append(ExpressionSelectionModifier(expression="Mass < 2"))
        pipeline.modifiers.append(DeleteSelectedModifier())
    if st["color"] == "chain":
        gradient = getattr(ColorCodingModifier, st["chain_gradient"])()
        pipeline.modifiers.append(
            ColorCodingModifier(property="Molecule Identifier", gradient=gradient)
        )
    elif st["color"] == "z":
        gradient = getattr(ColorCodingModifier, st["z_gradient"])()
        pipeline.modifiers.append(ColorCodingModifier(property="Position.Z", gradient=gradient))
    if st["highlight"]:
        pipeline.modifiers.append(
            highlight_chains(st["highlight"], st["highlight_seed"], st["highlight_transparency"])
        )
    source = pipeline.source.data
    types = source.particles_.particle_types_.types_
    for t in types:
        t.radius = next(r for m, r in st["radii"] if t.mass < m)
    width = st["bond_width"]
    if not isinstance(width, (int, float)):
        heaviest = max(t.mass for t in types)
        width = next(w for m, w in width if heaviest < m)
    source.particles.bonds.vis.width = width
    return pipeline


def gap_center(z, lo, length, bin_width=2.0, empty=0.1):
    """z of the middle of the largest low-density periodic run of the z histogram (the
    slit-pore gap; it may straddle the boundary), or None if there is no such run.
    Low density: a bin count at most `empty` times the 90th-percentile count."""
    nbins = max(8, int(length / bin_width))
    counts, _ = np.histogram(np.mod(z - lo, length), bins=nbins, range=(0.0, length))
    low = counts <= empty * np.percentile(counts, 90)
    if low.all() or not low.any():
        return None
    # Longest run of low bins on the ring: rotate so the ring starts on a dense bin.
    start = int(np.argmin(low))
    ring = np.roll(low, -start)
    best_len, best_end, run = 0, 0, 0
    for i, v in enumerate(ring):
        run = run + 1 if v else 0
        if run > best_len:
            best_len, best_end = run, i
    mid = (best_end + 1 - best_len / 2 + start) * length / nbins
    return lo + mid % length


def center_gap(frame, data):
    """Pipeline function: translate all particles along z so the slit-pore gap is in the
    middle of the cell (add a WrapPeriodicImagesModifier after it). Bulk: no change."""
    cell = data.cell
    lo, length = cell[2, 3], cell[2, 2]
    zc = gap_center(data.particles.positions[:, 2], lo, length)
    if zc is not None:
        data.particles_.positions_[:, 2] += lo + length / 2 - zc


def highlight_colors(n):
    """n well-separated bright colors (golden-ratio hue steps)."""
    return [colorsys.hsv_to_rgb((0.6 + 0.618034 * i) % 1.0, 0.9, 0.95) for i in range(n)]


def highlight_chains(n, seed=0, transparency=0.7, grey=0.7):
    """Pipeline function: color n random whole chains (molecule ids, fixed by `seed`)
    brightly and draw the others grey and mostly transparent."""
    chosen = {}

    def modify(frame, data):
        mol = np.asarray(data.particles["Molecule Identifier"])
        if not chosen:
            ids = np.unique(mol)
            pick = np.random.default_rng(seed).choice(ids, size=min(n, ids.size), replace=False)
            chosen.update(zip(pick.tolist(), highlight_colors(len(pick))))
        color = np.full((mol.size, 3), grey)
        alpha = np.full(mol.size, transparency)
        for m, c in chosen.items():
            on = mol == m
            color[on] = c
            alpha[on] = 0.0
        data.particles_.create_property("Color", data=color)
        data.particles_.create_property("Transparency", data=alpha)
        bonds = data.particles.bonds
        if bonds is not None and bonds.count:
            data.particles_.bonds_.create_property(
                "Transparency", data=alpha[np.asarray(bonds.topology)[:, 0]]
            )

    return modify


def show(pipeline, **style):
    """Viewport widget with a frame slider (and play button) under it."""
    st = {**STYLE, **style}
    width, height = st["width"], st["height"]
    ovito.scene.pipelines.clear()
    pipeline.add_to_scene()
    n = pipeline.modifiers[0].source.num_frames
    # A viewport on the global scene: passing the pipeline itself fails in the PyPI build
    # (ovito 3.17.0: ovito.nonpublic has no Scene) and would not follow the frame slider.
    vp = Viewport(type=Viewport.Type.Perspective, camera_dir=st["camera_dir"])
    vp.zoom_all()
    view = ovito.gui.create_ipywidget(vp, layout=ipywidgets.Layout(width=width, height=height))
    slider = ipywidgets.IntSlider(
        value=0,
        min=0,
        max=max(n - 1, 0),
        description="frame",
        layout=ipywidgets.Layout(width=width),
    )
    play = ipywidgets.Play(min=0, max=max(n - 1, 0), interval=st["frame_ms"])
    ipywidgets.jslink((play, "value"), (slider, "value"))

    def on_frame(change):
        # The widget shows a captured copy of the scene: re-capture it after each frame change.
        ovito.scene.anim.current_frame = change["new"]
        view.refresh()

    slider.observe(on_frame, names="value")
    return ipywidgets.VBox([view, ipywidgets.HBox([play, slider])])
