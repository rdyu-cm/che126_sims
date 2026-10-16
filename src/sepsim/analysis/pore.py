"""Slit-pore width from polymer density profiles along z (decision D26)."""

from dataclasses import dataclass

import numpy as np


@dataclass
class PoreWidth:
    """Width of a slit pore normal to z, Angstrom."""

    width: float  # z_upper - z_lower (periodic); 0.0 if the density never drops below threshold
    z_lower: float  # lower 50%-bulk crossing, wrapped into [0, Lz) (NaN if no pore)
    z_upper: float  # upper crossing, wrapped into [0, Lz); may be < z_lower if the pore wraps
    bulk_density: float  # bulk (plateau) density used, same units as the profile
    threshold: float  # 0.5 * bulk_density
    n_pores: int  # number of separate sub-threshold regions; the widest is reported


def bulk_plateau(density_profile) -> float:
    """Plateau density: median of the bins whose density exceeds 80% of the maximum."""
    rho = np.asarray(density_profile, dtype=float)
    return float(np.median(rho[rho > 0.8 * rho.max()]))


def _crossing(z1, r1, z2, r2, thr) -> float:
    return float(z1 + (thr - r1) / (r2 - r1) * (z2 - z1))


def pore_width(
    z_A, density_profile, *, Lz_A: float, bulk_density: float | None = None
) -> PoreWidth:
    """Pore width = distance between the z where the density crosses 50% of bulk.

    ``z_A`` (Angstrom) are bin centres in increasing order spanning one
    periodic box length ``Lz_A``; ``density_profile`` any density units.
    bulk = ``bulk_density`` if given, else the plateau of the slab interior
    (``bulk_plateau``: median of bins above 80% of the max). The pore is a
    (periodically) contiguous run of bins with density < bulk/2; each edge is
    located by linear interpolation between the last bin above and first bin
    below the threshold. The pore may wrap across the periodic boundary; the
    width is measured along +z from z_lower to z_upper through the pore. If
    several separate sub-threshold runs exist the widest is reported (and
    ``n_pores`` > 1); if none, the pore is closed and width = 0.
    """
    z = np.asarray(z_A, dtype=float)
    rho = np.asarray(density_profile, dtype=float)
    if z.ndim != 1 or rho.shape != z.shape:
        raise ValueError("z_A and density_profile must be 1-D arrays of equal length")
    if np.any(np.diff(z) <= 0) or z[-1] - z[0] >= Lz_A:
        raise ValueError("z_A must be increasing and span less than Lz_A")
    bulk = bulk_plateau(rho) if bulk_density is None else float(bulk_density)
    thr = 0.5 * bulk
    below = rho < thr
    if below.all():
        raise ValueError("density is below half bulk everywhere: no polymer slab")
    if not below.any():
        return PoreWidth(0.0, float("nan"), float("nan"), bulk, thr, 0)

    # Rotate so that bin 0 is above threshold; unwrap z so it increases monotonically.
    m = len(z)
    s = int(np.argmin(below))
    order = np.r_[np.arange(s, m), np.arange(0, s), s]  # closes the ring with bin s again
    zz = z[order] + np.r_[np.zeros(m - s), np.full(s, Lz_A), Lz_A]
    rr = rho[order]
    bb = below[order]

    starts = np.flatnonzero(~bb[:-1] & bb[1:]) + 1  # first below-threshold bin of a run
    ends = np.flatnonzero(bb[:-1] & ~bb[1:])  # last below-threshold bin of a run
    best = None
    for a, b in zip(starts, ends, strict=True):
        lo = _crossing(zz[a - 1], rr[a - 1], zz[a], rr[a], thr)
        hi = _crossing(zz[b], rr[b], zz[b + 1], rr[b + 1], thr)
        if best is None or hi - lo > best[1] - best[0]:
            best = (lo, hi)
    lo, hi = best
    return PoreWidth(
        width=hi - lo,
        z_lower=float(np.mod(lo, Lz_A)),
        z_upper=float(np.mod(hi, Lz_A)),
        bulk_density=bulk,
        threshold=thr,
        n_pores=len(starts),
    )


@dataclass
class LocalPoreWidths:
    """Pore width resolved over an x-y grid of z-profiles, Angstrom."""

    widths: np.ndarray  # (nx, ny) width of each column (0 where the pore is closed)
    min: float
    max: float
    mean: float
    bulk_density: float  # bulk density used for every column


def local_pore_widths(
    z_A, density_profiles, *, Lz_A: float, bulk_density: float | None = None
) -> LocalPoreWidths:
    """Pore width per x-y column from density profiles of shape (nx, ny, nz).

    Each column is analysed with ``pore_width``. One common bulk density is
    used for all columns: ``bulk_density`` if given, else the plateau
    (``bulk_plateau``) of the x-y-averaged profile, because single columns are
    noisier. Closed columns have width 0. Returns the 2-D width array and its
    min, max and mean.
    """
    rho = np.asarray(density_profiles, dtype=float)
    if rho.ndim != 3:
        raise ValueError("density_profiles must have shape (nx, ny, nz)")
    bulk = bulk_plateau(rho.mean(axis=(0, 1))) if bulk_density is None else float(bulk_density)
    widths = np.empty(rho.shape[:2])
    for ix in range(rho.shape[0]):
        for iy in range(rho.shape[1]):
            widths[ix, iy] = pore_width(z_A, rho[ix, iy], Lz_A=Lz_A, bulk_density=bulk).width
    return LocalPoreWidths(
        widths=widths,
        min=float(widths.min()),
        max=float(widths.max()),
        mean=float(widths.mean()),
        bulk_density=bulk,
    )
