"""Interactive OVITO viewer for run trajectories, for scripts/view.ipynb.

Runs in its own environment (~/projects/installations/ovito-viewer: ovito, ipywidgets,
jupyterlab), not the project's, so the simulation code has no OVITO dependency.
Topology (types, bonds, molecule ids) comes from the system's data.lmp; the DCD frames
replace the positions (DCDs are unwrapped and in atom-id order, like data.lmp).
Runs on rdyu-rog are copied on demand into results/viewer/rdyu-rog/<system>/<stage>/.
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

# Display radius by type mass (amu): H, united-atom/AA carbon, CG bead.
RADII = [(2.0, 0.3), (20.0, 0.8), (1e9, 2.2)]


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


def load(system, stage, dcd, node="local", color="chain", hide_h=True, wrap=True, data=None):
    """Pipeline for one trajectory.

    color: "chain" (molecule id), "z" (height; pores) or "type".
    data: topology file; default systems/<system>/data.lmp.
    """
    run_dir = RUNS / system / stage if node == "local" else fetch(system, stage, dcd, node)
    pipeline = import_file(str(data or ROOT / "systems" / system / "data.lmp"), atom_style="full")
    traj = LoadTrajectoryModifier()
    traj.source.load(str(run_dir / dcd))
    pipeline.modifiers.append(traj)
    if wrap:
        pipeline.modifiers.append(WrapPeriodicImagesModifier())
    if hide_h:
        pipeline.modifiers.append(ExpressionSelectionModifier(expression="Mass < 2"))
        pipeline.modifiers.append(DeleteSelectedModifier())
    if color == "chain":
        pipeline.modifiers.append(
            ColorCodingModifier(
                property="Molecule Identifier", gradient=ColorCodingModifier.Rainbow()
            )
        )
    elif color == "z":
        pipeline.modifiers.append(
            ColorCodingModifier(property="Position.Z", gradient=ColorCodingModifier.Viridis())
        )
    source = pipeline.source.data
    for t in source.particles_.particle_types_.types_:
        t.radius = next(r for m, r in RADII if t.mass < m)
    source.particles.bonds.vis.width = 0.5
    return pipeline


def show(pipeline, width="900px", height="600px"):
    """Viewport widget with a frame slider (and play button) under it."""
    ovito.scene.pipelines.clear()
    pipeline.add_to_scene()
    n = pipeline.modifiers[0].source.num_frames
    # A viewport on the global scene: passing the pipeline itself fails in the PyPI build
    # (ovito 3.17.0: ovito.nonpublic has no Scene) and would not follow the frame slider.
    vp = Viewport(type=Viewport.Type.Perspective, camera_dir=(1.0, 0.6, -0.5))
    vp.zoom_all()
    view = ovito.gui.create_ipywidget(vp, layout=ipywidgets.Layout(width=width, height=height))
    slider = ipywidgets.IntSlider(
        value=0,
        min=0,
        max=max(n - 1, 0),
        description="frame",
        layout=ipywidgets.Layout(width=width),
    )
    play = ipywidgets.Play(min=0, max=max(n - 1, 0), interval=200)
    ipywidgets.jslink((play, "value"), (slider, "value"))

    def on_frame(change):
        ovito.scene.anim.current_frame = change["new"]

    slider.observe(on_frame, names="value")
    return ipywidgets.VBox([view, ipywidgets.HBox([play, slider])])
