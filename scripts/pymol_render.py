"""PyMOL helpers for scripts/presentation_figures.py: PDB writer, view, CGO, cached renders.

PyMOL is used as an external program (``pymol -cq script.pml``; the open-source build is
not importable from the project venv). Coordinates are rotated into the camera frame
before they are written, so every render uses the same fixed orthoscopic view: camera on
+z looking down -z, x to the right, y up. A render is cached as ``<out>/<name>.png`` with
``<name>.key`` (hash of the PDB files and the script); a rerun with the same inputs reuses
it. Without ``pymol`` on PATH, a cached PNG is reused if present, otherwise ``None`` is
returned and the caller draws a placeholder.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np


def _clean_env() -> dict:
    """Environment without the project venv: the Debian ``pymol`` wrapper runs ``python3``
    from PATH, which must be the system Python that has the pymol module."""
    env = dict(os.environ)
    venv = env.pop("VIRTUAL_ENV", None)
    for k in ("PYTHONPATH", "PYTHONHOME", "UV_PROJECT_ENVIRONMENT"):
        env.pop(k, None)
    if venv:
        env["PATH"] = os.pathsep.join(
            d for d in env.get("PATH", "").split(os.pathsep) if not d.startswith(venv)
        )
    return env


def pymol_exe() -> str | None:
    return shutil.which("pymol", path=_clean_env().get("PATH"))


def pdb_text(
    pos: np.ndarray,
    elem,
    resi,
    bonds: np.ndarray | None = None,
    names=None,
    resn: str = "POL",
) -> str:
    """HETATM records (serials from 1) plus one CONECT per bond (0-based index pairs)."""
    pos = np.asarray(pos, float)
    n = len(pos)
    if n > 99999:
        raise ValueError(f"{n} atoms: too many for a PDB file")
    if isinstance(elem, str):
        elem = [elem] * n
    resi = np.asarray(resi, int)
    lines = []
    for i in range(n):
        e = str(elem[i])
        nm = str(names[i]) if names is not None else e
        x, y, z = pos[i]
        lines.append(
            f"HETATM{i + 1:5d}  {nm:<3s} {resn:>3s} A{int(resi[i]) % 10000:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {e:>2s}"
        )
    if bonds is not None:
        for a, b in np.asarray(bonds, int):
            lines.append(f"CONECT{a + 1:5d}{b + 1:5d}")
    lines.append("END")
    return "\n".join(lines) + "\n"


def view_lines(half_w: float, half_h: float, width: int, height: int, depth: float) -> list[str]:
    """Fixed orthoscopic view of the camera-frame box |x| <= half_w, |y| <= half_h."""
    fov = 20.0
    half = max(half_h, half_w * height / width)
    dist = half / np.tan(np.radians(fov / 2))
    return [
        f"set field_of_view, {fov}",
        "set orthoscopic, 1",
        (
            f"set_view (1,0,0, 0,1,0, 0,0,1, 0,0,{-dist:.3f}, 0,0,0,"
            f" {max(dist - depth, 1.0):.3f}, {dist + depth:.3f}, 1)"
        ),
    ]


def style_lines(outline: bool = True) -> list[str]:
    return [
        "bg_color white",
        "set ray_opaque_background, 1",
        "set antialias, 2",
        "set ray_shadows, 0",
        "set specular, 0.25",
        "set ambient, 0.45",
        "set direct, 0.6",
        "set depth_cue, 0",
        f"set ray_trace_mode, {1 if outline else 0}",
        "set ray_trace_color, black",
        "set valence, 0",
        "set auto_zoom, off",
    ]


def color_lines(obj: str, colors: np.ndarray, resi: np.ndarray, prefix: str) -> list[str]:
    """One named colour per residue (chain) id."""
    out = []
    for i in np.unique(resi):
        r, g_, b = colors[i] if colors.ndim == 2 and len(colors) > i else colors
        out.append(f"set_color {prefix}{i}, [{r:.3f}, {g_:.3f}, {b:.3f}]")
        out.append(f"color {prefix}{i}, {obj} and resi {int(i)}")
    return out


def cgo_cylinders(name: str, segments, radius: float, color) -> list[str]:
    """CGO object of cylinders (e.g. cell edges) as an embedded python block."""
    r, g_, b = color
    items = []
    for p, q in segments:
        items.append(
            "CYLINDER,"
            + ",".join(f"{v:.3f}" for v in (*p, *q))
            + f",{radius:.3f},{r},{g_},{b},{r},{g_},{b}"
        )
    return [
        "python",
        "from pymol.cgo import CYLINDER",
        "from pymol import cmd",
        f"cmd.load_cgo([{','.join(items)}], {name!r})",
        "python end",
    ]


def cgo_quad(name: str, corners, color, alpha: float) -> list[str]:
    """A translucent quadrilateral (two triangles), e.g. to highlight a gap."""
    r, g_, b = color
    a, b2, c, d = (",".join(f"{v:.3f}" for v in p) for p in corners)
    return [
        "python",
        "from pymol.cgo import ALPHA, BEGIN, COLOR, END, NORMAL, TRIANGLES, VERTEX",
        "from pymol import cmd",
        (
            f"cmd.load_cgo([ALPHA,{alpha},COLOR,{r},{g_},{b},BEGIN,TRIANGLES,NORMAL,0,0,1,"
            f"VERTEX,{a},VERTEX,{b2},VERTEX,{c},VERTEX,{a},VERTEX,{c},VERTEX,{d},END], {name!r})"
        ),
        "python end",
    ]


def box_edges(corners: np.ndarray) -> list[tuple]:
    """12 edges of a box from its 8 corners ordered by (ix, iy, iz) bits."""
    edges = []
    for i in range(8):
        for bit in (1, 2, 4):
            j = i | bit
            if j != i:
                edges.append((corners[i], corners[j]))
    return edges


def box_corners(lo, hi) -> np.ndarray:
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    return np.array([[(hi if (i >> k) & 1 else lo)[k] for k in range(3)] for i in range(8)])


def render(
    name: str,
    files: dict[str, str],
    body: list[str],
    out_dir: Path,
    size: tuple[int, int],
    enabled: bool = True,
) -> tuple[Path | None, str]:
    """Render ``body`` (pml lines; the PDB ``files`` are in the working directory) to
    ``out_dir/name.png``. Returns (path or None, status: rendered/cached/stale cache/
    no pymol/disabled/failed: ...)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{name}.png"
    keyf = out_dir / f"{name}.key"
    w, h = size
    script = "\n".join([*body, f"ray {w}, {h}", "png out.png, dpi=300", "quit"]) + "\n"
    hsh = hashlib.sha256(script.encode())
    for k in sorted(files):
        hsh.update(k.encode())
        hsh.update(files[k].encode())
    key = hsh.hexdigest()
    if png.is_file() and keyf.is_file() and keyf.read_text().strip() == key:
        return png, "cached"
    exe = pymol_exe() if enabled else None
    if exe is None:
        if png.is_file():
            return png, "stale cache (pymol unavailable)" if enabled else "cached (render off)"
        return None, "no pymol on PATH" if enabled else "render disabled"
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        for k, v in files.items():
            (tdp / k).write_text(v)
        (tdp / "render.pml").write_text(script)
        try:
            subprocess.run(
                [exe, "-cq", "render.pml"],
                cwd=tdp,
                check=True,
                capture_output=True,
                timeout=900,
                env=_clean_env(),
            )
        except (subprocess.SubprocessError, OSError) as e:
            return None, f"failed: {type(e).__name__}"
        if not (tdp / "out.png").is_file():
            return None, "failed: no image written"
        shutil.copyfile(tdp / "out.png", png)
    keyf.write_text(key + "\n")
    return png, "rendered"
