"""Crystallinity from a local chain-alignment (P2) order parameter.

Decision D26: each backbone site i carries a normalized chord vector u_i along
the local chain axis; its local order is the mean second Legendre polynomial
of the angle to the chords of its spatial neighbours on other stems (same-chain
sites within a backbone window are excluded),

    p2_i = < P2(u_i . u_j) >_{j in N(i)},   P2(x) = (3 x^2 - 1) / 2,

and the site is crystalline if p2_i >= threshold. The crystalline fraction and
the largest cluster of crystalline sites connected by the neighbour relation
are reported.

This is a variant of the chord-alignment criterion of Anwar & Schilling,
Polymer 76, 307 (2015), doi:10.1016/j.polymer.2015.08.041, who use the chord
r_{i+1} - r_{i-1}, neighbours within 1.4 sigma, count neighbours whose chords
are aligned within 10 degrees and call a site crystalline if it has >= 12
aligned neighbours, with the thresholds chosen from crystal vs liquid
reference distributions. Here (user decision D26) the mean P2 over
neighbours replaces the aligned-neighbour count; the threshold is calibrated
the same way (``calibrate_threshold``).

Units: positions and cell in Angstrom.
"""

from dataclasses import dataclass

import numpy as np
from MDAnalysis.lib.distances import minimize_vectors, self_capped_distance
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


@dataclass
class CrystallinityResult:
    """Per-site order and global crystallinity of one configuration."""

    p2: np.ndarray  # (N,) local mean P2; NaN for chain ends and sites with no neighbours
    crystalline: np.ndarray  # (N,) bool, p2 >= threshold (False where p2 is NaN)
    n_neighbours: np.ndarray  # (N,) neighbour count after same-chain exclusion
    fraction: float  # crystalline sites / sites with a chord (chain ends excluded)
    n_sites: int  # sites with a chord (denominator of ``fraction``)
    largest_cluster: int  # sites in the largest connected crystalline cluster (0 if none)
    n_clusters: int  # number of crystalline clusters
    cluster_labels: np.ndarray  # (N,) cluster index of crystalline sites, -1 otherwise


def _cell_matrix(cell) -> np.ndarray:
    """3x3 cell matrix with rows = lattice vectors a, b, c (LAMMPS convention)."""
    h = np.asarray(cell, dtype=float)
    if h.shape == (3,):
        h = np.diag(h)
    if h.shape != (3, 3):
        raise ValueError("cell must be 3 box lengths or a 3x3 matrix of lattice vectors (rows)")
    if abs(np.linalg.det(h)) <= 0.0:
        raise ValueError("cell matrix is singular")
    return h


def _perpendicular_widths(h: np.ndarray) -> np.ndarray:
    """Distances between opposite cell faces, w_k = V / |a_l x a_m|."""
    vol = abs(np.linalg.det(h))
    return np.array(
        [vol / np.linalg.norm(np.cross(h[(k + 1) % 3], h[(k + 2) % 3])) for k in range(3)]
    )


def _box_dimensions(h: np.ndarray) -> np.ndarray:
    """MDAnalysis box [lx, ly, lz, alpha, beta, gamma] (degrees) of a LAMMPS-style cell.

    MDAnalysis puts a along x and b in the xy plane, so the cell must be lower
    triangular (LAMMPS restricted triclinic); positions are in the same frame.
    """
    if np.any(np.triu(h, 1) != 0.0):
        raise ValueError("cell must be lower triangular: a = (lx,0,0), b = (xy,ly,0)")
    lengths = np.linalg.norm(h, axis=1)

    def angle(p, q):
        return np.degrees(np.arccos(h[p] @ h[q] / (lengths[p] * lengths[q])))

    return np.array([*lengths, angle(1, 2), angle(0, 2), angle(0, 1)])


def _neighbour_pairs(x: np.ndarray, h: np.ndarray, r_c: float):
    """Unique pairs (i, j) with minimum-image distance <= r_c (periodic cell ``h``).

    MDAnalysis ``self_capped_distance`` (orthorhombic or triclinic; wrapped or
    unwrapped positions). r_c < w_min / 2 is enforced, so each pair has at most
    one image within r_c.
    """
    if r_c >= 0.5 * _perpendicular_widths(h).min():
        raise ValueError("r_c must be smaller than half the smallest perpendicular cell width")
    pairs = self_capped_distance(x, r_c, box=_box_dimensions(h), return_distances=False)
    pairs = np.asarray(pairs, dtype=np.intp).reshape(-1, 2)
    return pairs[:, 0], pairs[:, 1]


def chord_vectors(positions, chain_id, cell, half_span: int) -> np.ndarray:
    """Normalized chord u_i = (r_{i+h} - r_{i-h}) / |...| with h = ``half_span``.

    Sites must be backbone sites only, ordered along the backbone within each
    chain, and each chain's sites contiguous in the arrays. The chord is taken
    with the minimum-image convention (MDAnalysis ``minimize_vectors``), so
    wrapped or unwrapped coordinates both work (requires the chord length < half the smallest cell width). The first
    and last h sites of each chain (chain ends) get NaN.
    """
    x = np.asarray(positions, dtype=float)
    cid = np.asarray(chain_id)
    h_mat = _cell_matrix(cell)
    if half_span < 1:
        raise ValueError("half_span must be >= 1")
    box = _box_dimensions(h_mat)
    u = np.full_like(x, np.nan)
    starts = np.flatnonzero(np.r_[True, cid[1:] != cid[:-1]])
    ends = np.r_[starts[1:], len(cid)]
    if len(np.unique(cid)) != len(starts):
        raise ValueError("sites of each chain must be contiguous")
    for s, e in zip(starts, ends, strict=True):
        if e - s <= 2 * half_span:
            continue
        d = minimize_vectors(x[s + 2 * half_span : e] - x[s : e - 2 * half_span], box)
        u[s + half_span : e - half_span] = d / np.linalg.norm(d, axis=1, keepdims=True)
    return u


def crystallinity(
    positions,
    chain_id,
    cell,
    *,
    r_c: float,
    threshold: float,
    half_span: int,
    l_proj: float = 1.27,
    exclude_window: int | None = None,
) -> CrystallinityResult:
    """Crystalline fraction and largest crystalline cluster from local chain alignment.

    Inputs: ``positions`` (N, 3) backbone sites in Angstrom (PE: AA carbons, UA
    sites or CG beads; iPP: backbone carbons only -- methyls/H excluded),
    ordered along the backbone within each chain and contiguous per chain;
    ``chain_id`` (N,) chain label; ``cell`` 3 box lengths (orthorhombic) or a
    3x3 matrix whose rows are the lattice vectors a, b, c (triclinic, e.g. the
    LAMMPS a = (lx,0,0), b = (xy,ly,0), c = (xz,yz,lz)).

    Chord: u_i = r_{i+h} - r_{i-h}, h = ``half_span``. Use h = 1 for PE (planar
    zigzag: the i-1 -> i+1 chord lies exactly on the stem axis). Use h = 3 for
    iPP: its crystalline stems are 3_1 helices (3 monomers = 6 backbone bonds
    per turn), so the i-1 -> i+1 chord is tilted off the helix axis and rotates
    about it from site to site, which lowers P2 even in a perfect crystal; the
    chord r_{i+3} - r_{i-3} spans one full turn and lies along the helix axis.

    Neighbours of i: sites j whose minimum-image distance is <= r_c, excluding
    sites without a chord (the h end sites of each chain) and same-chain sites
    with |i - j| <= ``exclude_window``, so p2 measures alignment with segments
    of other stems, not with the site's own stem. Default window:
    ceil(r_c / ``l_proj``) + h, where ``l_proj`` is the projection of one
    backbone step on the stem axis (Angstrom; 1.27 for PE at AA/UA, ~1.08 for
    the iPP 3_1 helix = 6.5 A / 6; set it for CG beads). Same-chain sites
    beyond the window (a stem folded back next to its own chain) still count.
    Neighbour search: MDAnalysis ``self_capped_distance``, orthorhombic or
    triclinic cells; r_c must be less than half the smallest perpendicular
    cell width.

    p2_i = mean_j P2(u_i . u_j), P2(x) = (3x^2 - 1)/2 (= 1 for parallel
    chords, -1/2 perpendicular, 0 on isotropic average). Site i is
    crystalline if p2_i >= ``threshold``; sites with no neighbours have
    p2 = NaN and are not crystalline. fraction = crystalline / sites with a
    chord. Clusters are connected components of crystalline sites linked by the
    same (exclusion-applied) neighbour relation (scipy.sparse.csgraph).

    ``r_c`` and ``threshold`` are required: both depend on the model
    resolution. A starting point for r_c is ~1.4 sigma of the backbone LJ site
    (Anwar & Schilling 2015), i.e. ~5.6 Angstrom for UA/AA PE carbons; confirm
    by calibration, and set ``threshold`` with ``calibrate_threshold`` from
    reference crystal and melt configurations of the same model.
    """
    x = np.asarray(positions, dtype=float)
    cid = np.asarray(chain_id)
    h_mat = _cell_matrix(cell)
    n = len(x)
    u = chord_vectors(x, cid, h_mat, half_span)
    valid = ~np.isnan(u[:, 0])
    idx = np.flatnonzero(valid)

    # Position of each site within its chain, for the same-chain exclusion.
    starts = np.flatnonzero(np.r_[True, cid[1:] != cid[:-1]])
    seq = np.arange(n) - np.repeat(starts, np.diff(np.r_[starts, n]))

    if exclude_window is None:
        exclude_window = int(np.ceil(r_c / l_proj)) + half_span
    pi, pj = _neighbour_pairs(x[idx], h_mat, r_c)
    i, j = idx[pi], idx[pj]
    keep = (cid[i] != cid[j]) | (np.abs(seq[i] - seq[j]) > exclude_window)
    i, j = i[keep], j[keep]

    p2_pair = 1.5 * np.einsum("ij,ij->i", u[i], u[j]) ** 2 - 0.5
    count = np.bincount(i, minlength=n) + np.bincount(j, minlength=n)
    total = np.bincount(i, p2_pair, minlength=n) + np.bincount(j, p2_pair, minlength=n)
    with np.errstate(invalid="ignore", divide="ignore"):
        p2 = np.where(valid & (count > 0), total / count, np.nan)
    crystalline = np.nan_to_num(p2, nan=-np.inf) >= threshold

    labels = np.full(n, -1)
    cidx = np.flatnonzero(crystalline)
    n_clusters, largest = 0, 0
    if len(cidx):
        both = crystalline[i] & crystalline[j]
        local = np.full(n, -1)
        local[cidx] = np.arange(len(cidx))
        a, b = local[i[both]], local[j[both]]
        graph = coo_matrix((np.ones(len(a)), (a, b)), shape=(len(cidx), len(cidx)))
        n_clusters, lab = connected_components(graph, directed=False)
        labels[cidx] = lab
        largest = int(np.bincount(lab).max())

    n_sites = int(valid.sum())
    return CrystallinityResult(
        p2=p2,
        crystalline=crystalline,
        n_neighbours=count,
        fraction=float(crystalline.sum() / n_sites) if n_sites else float("nan"),
        n_sites=n_sites,
        largest_cluster=largest,
        n_clusters=int(n_clusters),
        cluster_labels=labels,
    )


def calibrate_threshold(p2_crystal, p2_melt) -> float:
    """Equal-error threshold separating reference crystal and melt p2 distributions.

    Given per-site p2 values from a reference crystal and a reference melt of
    the same model (same r_c and half_span), returns the threshold t at which
    the fraction of crystal sites misclassified as melt, P_c(p2 < t), equals
    the fraction of melt sites misclassified as crystal, P_m(p2 >= t)
    (equal-error point of the two empirical distributions), with linear
    interpolation of the difference between adjacent candidate thresholds.
    NaNs are ignored. Calibration from crystal vs liquid reference
    distributions follows Anwar & Schilling, Polymer 76, 307 (2015),
    doi:10.1016/j.polymer.2015.08.041.
    """
    c = np.asarray(p2_crystal, dtype=float)
    m = np.asarray(p2_melt, dtype=float)
    c = np.sort(c[~np.isnan(c)])
    m = np.sort(m[~np.isnan(m)])
    if len(c) == 0 or len(m) == 0:
        raise ValueError("need non-empty crystal and melt samples")
    t = np.unique(np.concatenate([c, m]))
    miss_c = np.searchsorted(c, t, side="left") / len(c)  # P_c(p2 < t), non-decreasing
    false_m = 1.0 - np.searchsorted(m, t, side="left") / len(m)  # P_m(p2 >= t), non-increasing
    d = miss_c - false_m  # non-decreasing
    k = int(np.searchsorted(d, 0.0, side="left"))
    if k == 0:
        return float(t[0])
    if k == len(t):
        return float(t[-1])
    if d[k] == 0.0:
        return float(t[k])
    w = -d[k - 1] / (d[k] - d[k - 1])
    return float(t[k - 1] + w * (t[k] - t[k - 1]))
