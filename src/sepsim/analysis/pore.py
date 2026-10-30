"""Slit-pore width from polymer density profiles along z (decision D26); film centring,
mass density profiles, Gibbs surfaces, interfacial widths and the clear gap (D51)."""

from dataclasses import dataclass

import numpy as np

from .units import A3_CM3, AVOGADRO


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


# --------------------------------------------------------------------------- film profiles (D51)

GRAMS_PER_A3 = 1.0 / (AVOGADRO * A3_CM3)  # (g/mol)/A^3 -> g/cm^3


def film_centre(z_A, Lz_A: float, masses=None, bin_A: float = 2.0) -> float:
    """Mass centre (in [0, Lz)) of a film normal to z in a periodic box, any image.

    The film may straddle the periodic boundary: the coordinates are wrapped, the
    longest (periodically) contiguous run of empty ``bin_A`` bins is taken as the gap
    (if no bin is empty, the emptiest bin), the box is cut at the gap centre so the
    film is contiguous, and the (mass-weighted) mean is taken there.
    """
    z = np.mod(np.asarray(z_A, dtype=float), Lz_A)
    nb = max(4, int(Lz_A // bin_A))
    counts = np.bincount(np.minimum((z / Lz_A * nb).astype(int), nb - 1), minlength=nb)
    empty = counts == 0
    if empty.any() and not empty.all():
        s = int(np.argmin(empty))  # first occupied bin: the rotated ring starts occupied
        ring = np.r_[empty[s:], empty[:s], False]
        starts = np.flatnonzero(~ring[:-1] & ring[1:]) + 1
        ends = np.flatnonzero(ring[:-1] & ~ring[1:]) + 1  # one past the run
        k = int(np.argmax(ends - starts))
        gap = (s + 0.5 * (starts[k] + ends[k])) * Lz_A / nb
    else:
        gap = (int(np.argmin(counts)) + 0.5) * Lz_A / nb
    zc = np.mod(z - gap, Lz_A)
    com = float(np.average(zc, weights=masses))
    return float(np.mod(gap + com, Lz_A))


def relative_z(z_A, centre_A: float, Lz_A: float) -> np.ndarray:
    """z relative to the film centre, wrapped into [-Lz/2, Lz/2)."""
    return np.mod(np.asarray(z_A, dtype=float) - centre_A + 0.5 * Lz_A, Lz_A) - 0.5 * Lz_A


def density_profile(z_rel_A, masses, area_A2: float, Lz_A: float, n_bins: int):
    """Mass density (g/cm^3) in ``n_bins`` (even) bins over [-Lz/2, Lz/2) of z relative
    to the film centre; ``masses`` in g/mol. Returns (bin centres, rho). The bins are
    symmetric about 0, so ``rho[::-1]`` is the profile mirrored at the film centre."""
    if n_bins % 2:
        raise ValueError("n_bins must be even (bins symmetric about the film centre)")
    edges = np.linspace(-0.5 * Lz_A, 0.5 * Lz_A, n_bins + 1)
    m, _ = np.histogram(z_rel_A, bins=edges, weights=masses)
    dz = Lz_A / n_bins
    return 0.5 * (edges[1:] + edges[:-1]), m / (area_A2 * dz) * GRAMS_PER_A3


def symmetrize(rho) -> np.ndarray:
    """Profile(s) (last axis z) averaged with the mirror image about the film centre."""
    rho = np.asarray(rho, dtype=float)
    return 0.5 * (rho + rho[..., ::-1])


def gibbs_thickness(z_A, rho, rho_plateau: float) -> float:
    """Equimolar (Gibbs) film thickness: integral of rho over z / plateau density
    (= M / (rho_plateau A) for the whole film)."""
    z = np.asarray(z_A, dtype=float)
    return float(np.sum(rho) * (z[1] - z[0]) / rho_plateau)


def plateau_density(z_A, rho_sym, margin_A: float, n_iter: int = 5) -> tuple[float, float]:
    """(plateau density, Gibbs thickness) of a symmetrized film profile.

    Start from :func:`bulk_plateau`; then repeatedly take the plateau as the mean
    density over |z| < t_G/2 - ``margin_A`` (the film interior; the central half of
    the film if that is too thin) and t_G = :func:`gibbs_thickness` with it.
    """
    z, rho = np.asarray(z_A, dtype=float), np.asarray(rho_sym, dtype=float)
    rp = bulk_plateau(rho)
    for _ in range(n_iter):
        h = 0.5 * gibbs_thickness(z, rho, rp)
        inner = np.abs(z) < h - margin_A
        if inner.sum() < 3:
            inner = np.abs(z) < 0.5 * h
        rp = float(rho[inner].mean())
    return rp, gibbs_thickness(z, rho, rp)


def _outer_crossing(z, rho, level) -> float:
    """Outermost z (z > 0 side) where rho falls through ``level``, interpolated."""
    k = np.flatnonzero((z > 0) & (rho >= level))
    if not len(k):
        return float("nan")
    k = int(k[-1])
    if k + 1 >= len(z):
        return float(z[k])
    return _crossing(z[k], rho[k], z[k + 1], rho[k + 1], level)


def interface_10_90(z_A, rho, rho_plateau: float, lo: float = 0.1, hi: float = 0.9) -> dict:
    """10-90 interfacial width of each film surface (profile relative to the film
    centre): outermost crossings of ``hi`` and ``lo`` times the plateau per side.
    Returns upper/lower widths and crossing positions (|z|), Angstrom."""
    z, r = np.asarray(z_A, dtype=float), np.asarray(rho, dtype=float)
    out = {}
    for side, zz, rr in (("upper", z, r), ("lower", -z[::-1], r[::-1])):
        z_hi = _outer_crossing(zz, rr, hi * rho_plateau)
        z_lo = _outer_crossing(zz, rr, lo * rho_plateau)
        out[side] = {"z90": z_hi, "z10": z_lo, "width": z_lo - z_hi}
    return out


TANH_10_90 = 2.0 * float(np.arctanh(0.8))  # 10-90 width of 1 - tanh(x/delta), in delta


def tanh_fit(z_A, rho_sym, rho_plateau: float, half_thickness_A: float) -> dict | None:
    """Fit rho(|z|) = rho_p/2 [1 - tanh((|z| - h)/delta)] to the z >= 0 half of a
    symmetrized profile; returns rho_p, h, delta and the fit's 10-90 width
    (2 atanh(0.8) delta), or None if the fit fails."""
    from scipy.optimize import curve_fit

    z, r = np.asarray(z_A, dtype=float), np.asarray(rho_sym, dtype=float)
    sel = z >= 0

    def f(x, rp, h, d):
        return 0.5 * rp * (1.0 - np.tanh((x - h) / d))

    try:
        p, cov = curve_fit(f, z[sel], r[sel], p0=(rho_plateau, half_thickness_A, 3.0))
    except (RuntimeError, ValueError):
        return None
    err = np.sqrt(np.diag(cov))
    d = abs(float(p[2]))
    return {
        "rho_p": float(p[0]),
        "h_A": float(p[1]),
        "delta_A": d,
        "delta_err_A": float(err[2]),
        "width_10_90_A": TANH_10_90 * d,
    }


def surface_layer(z_rel_A, half_thickness_A: float, depth_A: float) -> np.ndarray:
    """True for points within ``depth_A`` of either Gibbs surface on the film side, or
    outside the film (|z| > h - depth, h = Gibbs half-thickness); False = interior."""
    return np.abs(np.asarray(z_rel_A)) > half_thickness_A - depth_A


def clear_gap(xyz_A, box_A, centre_A: float, window_A: float = 10.0) -> tuple[float, float]:
    """(z gap, closest approach) across the slit for one frame, Angstrom.

    ``xyz_A`` (n, 3) any image, ``box_A`` (Lx, Ly, Lz), ``centre_A`` the film centre
    (:func:`film_centre`). The z gap is Lz minus the film's z extent; the closest
    approach is the smallest 3-D distance between an atom near the film top and the
    periodic z image of an atom near its bottom (minimum image in x, y). Candidates lie
    within ``window_A`` of the extremes; the window is doubled until the result is
    below z gap + window, which makes it exact.
    """
    from scipy.spatial import cKDTree

    lx, ly, lz = (float(b) for b in box_A[:3])
    x = np.asarray(xyz_A, dtype=float)
    z = relative_z(x[:, 2], centre_A, lz)
    zmin, zmax = float(z.min()), float(z.max())
    gap = lz - (zmax - zmin)
    xy = np.mod(x[:, :2], [lx, ly])
    xy = np.where(xy >= [lx, ly], 0.0, xy)  # float rounding of the mod
    w = window_A
    while True:
        top, bot = z > zmax - w, z < zmin + w
        a = np.column_stack([xy[top], z[top] - zmin])
        b = np.column_stack([xy[bot], z[bot] - zmin + lz])
        tree = cKDTree(b, boxsize=[lx, ly, 4.0 * lz])
        d = float(tree.query(a, k=1)[0].min())
        if d <= gap + w or w >= lz:
            return gap, d
        w *= 2.0
