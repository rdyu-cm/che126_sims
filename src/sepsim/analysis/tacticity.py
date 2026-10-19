"""Methine chirality and stereo-inversion counting (tacticity monitor).

In the TraPPE-UA iPP model the methine configuration is held only by the
H-CH-C angle terms (no improper), so a methine can invert during a run;
check the inversion count against the starting structure at each hold.
"""

import numpy as np
from MDAnalysis.lib.distances import minimize_vectors

from .order import _box_dimensions, _cell_matrix


def methine_chirality(positions, methine, methyl, hydrogen, prev, next_, cell=None) -> np.ndarray:
    """Chirality sign (+1/-1) of each methine carbon.

    s = sign( [(r_prev - r_C) x (r_next - r_C)] . (r_Me - r_H) ), with C the
    methine, prev/next its backbone neighbours in chain order, Me its methyl
    and H its hydrogen (index arrays of equal length into ``positions``,
    (N, 3) in Angstrom). For an isotactic chain with consistent prev/next
    order all signs are equal. With ``cell`` (3 lengths or a lower-triangular
    3x3 matrix of lattice vectors as rows) bond vectors use the minimum image.
    Returns an int array; 0 only for a degenerate (planar) centre.
    """
    x = np.asarray(positions, dtype=float)
    c = x[np.asarray(methine)]
    vecs = [x[np.asarray(k)] - c for k in (prev, next_, methyl, hydrogen)]
    if cell is not None:
        box = _box_dimensions(_cell_matrix(cell))
        vecs = [minimize_vectors(v, box) for v in vecs]
    d_prev, d_next, d_me, d_h = vecs
    return np.sign(np.einsum("ij,ij->i", np.cross(d_prev, d_next), d_me - d_h)).astype(int)


def count_inversions(signs, reference) -> int:
    """Number of methines whose chirality sign differs from ``reference``."""
    signs = np.asarray(signs)
    reference = np.asarray(reference)
    if signs.shape != reference.shape:
        raise ValueError("signs and reference must have the same shape")
    return int(np.count_nonzero(signs != reference))
