"""Load cited crystal-structure YAMLs from ``<repo>/data/crystals`` and basic crystallography."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

CRYSTAL_DIR = Path(__file__).resolve().parents[2] / "data" / "crystals"


def load_crystal(name: str) -> dict:
    """Load ``data/crystals/<name>.yaml`` as a plain dict."""
    return yaml.safe_load((CRYSTAL_DIR / f"{name}.yaml").read_text())


def cell_matrix(a, b, c, alpha=90.0, beta=90.0, gamma=90.0) -> np.ndarray:
    """Return a 3x3 matrix whose rows are the lattice vectors (a along x, b in the xy plane).

    Cartesian coordinates are ``frac @ cell_matrix(...)``. Angles in degrees.
    """
    al, be, ga = np.radians([alpha, beta, gamma])
    ax = np.array([a, 0.0, 0.0])
    bx = np.array([b * np.cos(ga), b * np.sin(ga), 0.0])
    cx = c * np.cos(be)
    cy = c * (np.cos(al) - np.cos(be) * np.cos(ga)) / np.sin(ga)
    cz = np.sqrt(c**2 - cx**2 - cy**2)
    return np.array([ax, bx, [cx, cy, cz]])


def expand_p21c(asym_frac, tol: float = 1e-4) -> np.ndarray:
    """Apply the P2_1/c (unique axis b) operations and return unique sites wrapped to [0, 1).

    Ops: (x,y,z), (-x,y+1/2,-z+1/2), (-x,-y,-z), (x,-y+1/2,z+1/2). Sites are ordered by
    operation, then by asymmetric-unit index; duplicates (within ``tol``) are dropped.
    """
    p = np.asarray(asym_frac, dtype=float)
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    images = [
        np.column_stack([x, y, z]),
        np.column_stack([-x, y + 0.5, -z + 0.5]),
        np.column_stack([-x, -y, -z]),
        np.column_stack([x, -y + 0.5, z + 0.5]),
    ]
    out: list[np.ndarray] = []
    for site in np.concatenate(images) % 1.0:
        site = np.where(site >= 1.0 - 1e-12, 0.0, site)
        if not any(np.all(np.abs((site - q + 0.5) % 1.0 - 0.5) < tol) for q in out):
            out.append(site)
    return np.array(out)
