"""Cylindrical hole through a film: radius from bead occupancy maps (decision D52).

All coordinates are Angstrom. A frame is analysed about a *tracked centre* (the hole
centroid of the previous frame; initially the build axis):

* x, y are wrapped into [-L/2, L/2) about the centre (so a hole that drifts across the
  box edge stays in one piece; the map is "rolled" to put the centre mid-box);
* the beads are binned on a 2 A grid, projected through z, and smoothed with a periodic
  Gaussian (sigma 1 bin); the threshold is ``THRESH`` (50%) of the median count of the
  bins farther than r_ref + ``FAR_PAD_A`` from the centre (the undisturbed film);
* the hole is the connected sub-threshold region (``scipy.ndimage.label``) that holds
  the sub-threshold bin nearest the centre, if that bin is within
  max(r_ref / 2, 2 bins) of it; else the hole is closed (area 0);
* A = bins x bin area, R_eff = sqrt(A / pi), centroid = mean bin position.

R(z): the same per 10 A z-slab of the film interior (between the 50% crossings of the
film density profile, from ``sepsim.analysis.pore.pore_width``), each slab smoothed with
sigma ``SLAB_SIGMA_BINS`` (a slab holds ~0.4 beads per bin); R_min = the smallest slab
radius. A pinched hole (open at the surfaces, plugged inside) has R_min = 0 while the
projected R_eff > 0. The hole is closed when R_min < ``CLOSED_R_A`` for
``CLOSED_FRAMES`` consecutive frames.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import ndimage

from sepsim.analysis.pore import pore_width

BIN_A = 2.0
SIGMA_BINS = 1.0
SLAB_A = 10.0
SLAB_SIGMA_BINS = 2.0
FAR_PAD_A = 20.0
THRESH = 0.5
CLOSED_R_A = 3.0
CLOSED_FRAMES = 5
Z_BIN_A = 2.0


@dataclass
class Hole2D:
    """Hole found in one (projected or slab) map."""

    area: float  # A^2 (0 if closed)
    r_eff: float  # sqrt(area / pi)
    centroid: np.ndarray  # (x, y) relative to the map centre (0, 0 if closed)
    threshold: float
    far_median: float
    found: bool


@dataclass
class HoleFrame:
    """One frame: projected hole, slab radii, film thickness."""

    r_eff: float
    area: float
    centre: np.ndarray  # absolute (x, y) of the hole centroid (tracked centre if closed)
    found: bool
    r_min: float
    slab_z: np.ndarray  # slab centres relative to the film mid-plane
    slab_r: np.ndarray
    thickness: float
    film_mid: float
    map: np.ndarray | None = field(default=None, repr=False)  # smoothed projected map
    mask: np.ndarray | None = field(default=None, repr=False)  # hole bins


def wrap_about(xy: np.ndarray, centre, lengths) -> np.ndarray:
    """x, y relative to ``centre`` wrapped into [-L/2, L/2)."""
    lengths = np.asarray(lengths, dtype=float)[:2]
    d = np.asarray(xy, dtype=float)[:, :2] - np.asarray(centre, dtype=float)[:2]
    return d - lengths * np.floor(d / lengths + 0.5)


def _grid(lengths, bin_a: float) -> tuple[np.ndarray, np.ndarray]:
    """Bin edges over [-L/2, L/2) for x and y (bins close to ``bin_a``)."""
    out = []
    for L in np.asarray(lengths, dtype=float)[:2]:
        n = max(4, round(L / bin_a))
        out.append(np.linspace(-0.5 * L, 0.5 * L, n + 1))
    return out[0], out[1]


def find_hole(smap: np.ndarray, ex: np.ndarray, ey: np.ndarray, r_ref: float) -> tuple:
    """(Hole2D, mask) in a smoothed map binned on edges ``ex``, ``ey`` about (0, 0)."""
    cx, cy = 0.5 * (ex[1:] + ex[:-1]), 0.5 * (ey[1:] + ey[:-1])
    gx, gy = np.meshgrid(cx, cy, indexing="ij")
    dist = np.hypot(gx, gy)
    far = dist > r_ref + FAR_PAD_A
    if far.sum() < 10:
        far = dist > np.percentile(dist, 75)
    med = float(np.median(smap[far]))
    thr = THRESH * med
    below = smap < thr
    bx, by = ex[1] - ex[0], ey[1] - ey[0]
    empty = (Hole2D(0.0, 0.0, np.zeros(2), thr, med, False), np.zeros_like(below))
    if not below.any() or med <= 0:
        return empty
    d_below = np.where(below, dist, np.inf)
    k = np.unravel_index(np.argmin(d_below), below.shape)
    if d_below[k] > max(0.5 * r_ref, 2.0 * max(bx, by)):
        return empty
    labels, _ = ndimage.label(below)
    mask = labels == labels[k]
    area = float(mask.sum() * bx * by)
    centroid = np.array([gx[mask].mean(), gy[mask].mean()])
    return Hole2D(area, float(np.sqrt(area / np.pi)), centroid, thr, med, True), mask


def film_profile(z: np.ndarray, z_lo: float, lz: float, bin_a: float = Z_BIN_A):
    """(bin centres, counts) of wrapped z over [z_lo, z_lo + lz)."""
    n = max(4, round(lz / bin_a))
    edges = np.linspace(z_lo, z_lo + lz, n + 1)
    zw = z_lo + np.mod(z - z_lo, lz)
    counts, _ = np.histogram(zw, bins=edges)
    return 0.5 * (edges[1:] + edges[:-1]), counts.astype(float)


def film_bounds(z: np.ndarray, z_lo: float, lz: float) -> tuple[float, float]:
    """(bottom, top) of the film: the 50%-plateau crossings (top may exceed z_lo + lz)."""
    zc, prof = film_profile(z, z_lo, lz)
    gap = pore_width(zc, prof, Lz_A=lz)
    if gap.width <= 0:
        return z_lo, z_lo + lz
    bottom, top = gap.z_upper, gap.z_lower
    if top < bottom:
        top += lz
    return float(bottom), float(top)


def analyse_frame(
    pos: np.ndarray,
    lengths,
    centre,
    r_ref: float,
    z_lo: float,
    keep_map: bool = False,
) -> HoleFrame:
    """Hole in one frame of positions ``pos`` (N, 3), box ``lengths`` (Lx, Ly, Lz), about
    the tracked ``centre`` (absolute x, y); ``r_ref`` the expected radius (for the far
    field and the search distance); ``z_lo`` the box bottom."""
    lengths = np.asarray(lengths, dtype=float)
    centre = np.asarray(centre, dtype=float)[:2]
    rel = wrap_about(pos, centre, lengths)
    ex, ey = _grid(lengths, BIN_A)
    counts, _, _ = np.histogram2d(rel[:, 0], rel[:, 1], bins=(ex, ey))
    smap = ndimage.gaussian_filter(counts, SIGMA_BINS, mode="wrap")
    hole, mask = find_hole(smap, ex, ey, r_ref)
    new_centre = centre + hole.centroid if hole.found else centre.copy()
    new_centre = np.asarray(new_centre)

    # film thickness from the beads away from the hole
    r_far = max(hole.r_eff, r_ref) + FAR_PAD_A
    away = np.hypot(rel[:, 0], rel[:, 1]) > r_far
    if away.sum() < 0.1 * len(pos):
        away = np.ones(len(pos), bool)
    z = pos[:, 2]
    bottom, top = film_bounds(z[away], z_lo, lengths[2])
    mid = 0.5 * (bottom + top)

    # slabs of the film interior, about the projected hole centroid
    n_half = int(np.floor(0.5 * (top - bottom) / SLAB_A))
    slab_z = (np.arange(-n_half, n_half) + 0.5) * SLAB_A
    slab_r = np.zeros(len(slab_z))
    if n_half > 0:
        rel2 = rel - (hole.centroid if hole.found else 0.0)
        rel2 = rel2 - lengths[:2] * np.floor(rel2 / lengths[:2] + 0.5)
        zr = z_lo + np.mod(z - z_lo, lengths[2]) - mid
        zr = zr - lengths[2] * np.floor(zr / lengths[2] + 0.5)
        ez = np.arange(-n_half, n_half + 1) * SLAB_A
        h3, _ = np.histogramdd(np.column_stack([rel2, zr]), bins=(ex, ey, ez))
        h3 = ndimage.gaussian_filter(h3, (SLAB_SIGMA_BINS, SLAB_SIGMA_BINS, 0), mode="wrap")
        r_slab_ref = max(hole.r_eff, 0.5 * r_ref)
        for k in range(len(slab_z)):
            slab_r[k] = find_hole(h3[:, :, k], ex, ey, r_slab_ref)[0].r_eff
    r_min = float(slab_r.min()) if len(slab_r) else hole.r_eff
    return HoleFrame(
        r_eff=hole.r_eff,
        area=hole.area,
        centre=new_centre,
        found=hole.found,
        r_min=r_min,
        slab_z=slab_z,
        slab_r=slab_r,
        thickness=float(top - bottom),
        film_mid=float(mid),
        map=smap if keep_map else None,
        mask=mask if keep_map else None,
    )


def closure_time(times, r_min, threshold: float = CLOSED_R_A, n: int = CLOSED_FRAMES):
    """First time from which R_min < ``threshold`` for ``n`` consecutive frames (None)."""
    r = np.asarray(r_min, dtype=float)
    run = 0
    for k, v in enumerate(r):
        run = run + 1 if v < threshold else 0
        if run >= n:
            return float(np.asarray(times)[k - n + 1])
    return None


def linear_rate(times, r) -> dict | None:
    """Least-squares slope dR/dt (A per unit of ``times``) with its standard error."""
    t, y = np.asarray(times, dtype=float), np.asarray(r, dtype=float)
    if len(t) < 3 or np.ptp(t) <= 0:
        return None
    a = np.vstack([t, np.ones_like(t)]).T
    coef, res, *_ = np.linalg.lstsq(a, y, rcond=None)
    dof = len(t) - 2
    s2 = float(res[0]) / dof if len(res) and dof > 0 else 0.0
    cov = s2 * np.linalg.inv(a.T @ a)
    return {
        "slope": float(coef[0]),
        "slope_se": float(np.sqrt(cov[0, 0])),
        "intercept": float(coef[1]),
        "n": len(t),
    }
