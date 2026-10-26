"""Interactive OVITO viewer for run trajectories, for scripts/view.ipynb.

Runs in its own environment (~/projects/installations/ovito-viewer: ovito, ipywidgets,
jupyterlab), not the project's, so the simulation code has no OVITO dependency.
Topology (types, bonds, molecule ids) comes from the system's data.lmp; the DCD frames
replace the positions (DCDs are unwrapped and in atom-id order, like data.lmp).
Runs on rdyu-rog are copied on demand into results/viewer/rdyu-rog/<system>/<stage>/.
Every view uses STYLE below; edit it once to change the look of all views.
"""

import subprocess
from pathlib import Path

import ipywidgets
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
    "color": "chain",  # "chain" (molecule id), "z" (height; pores) or "type"
    "chain_gradient": "Rainbow",  # any ColorCodingModifier gradient: Rainbow, Viridis, Jet, ...
    "z_gradient": "Viridis",
    "radii": [(2.0, 0.3), (20.0, 0.8), (1e9, 2.2)],  # (mass below amu, radius Å): H, C/UA, CG
    "bond_width": 0.5,  # Å
    "hide_h": True,
    "wrap": True,  # wrap atoms into the periodic box
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
    return pipeline_for(data or ROOT / "systems" / system / "data.lmp", run_dir / dcd, **style)


def pipeline_for(data, dcd, **style):
    """Pipeline of the topology file `data` (LAMMPS data, atom_style full) plus the
    trajectory `dcd`, drawn with STYLE (keyword arguments override entries)."""
    st = {**STYLE, **style}
    pipeline = import_file(str(data), atom_style="full")
    traj = LoadTrajectoryModifier()
    traj.source.load(str(dcd))
    pipeline.modifiers.append(traj)
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
    source = pipeline.source.data
    for t in source.particles_.particle_types_.types_:
        t.radius = next(r for m, r in st["radii"] if t.mass < m)
    source.particles.bonds.vis.width = st["bond_width"]
    return pipeline


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
