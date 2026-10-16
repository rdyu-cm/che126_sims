"""Thermal conductivity from reverse NEMD (Muller-Plathe) temperature profiles."""

from dataclasses import dataclass

import numpy as np

from .stats import linear_fit
from .units import ANGSTROM_M, AVOGADRO, FS_S, KCAL_J


@dataclass
class KappaResult:
    """rNEMD thermal conductivity, W/(m K), with fit diagnostics."""

    kappa: float  # from mean |dT/dz| of the two halves
    kappa_lower: float  # half between the cold slab and the hot slab (z_cold .. z_cold+Lz/2)
    kappa_upper: float  # other half (z_cold+Lz/2 .. z_cold+Lz)
    slope_lower: float  # dT/dz, K/Angstrom (> 0 for a valid run)
    slope_upper: float  # dT/dz, K/Angstrom (< 0 for a valid run)
    r2_lower: float  # linearity diagnostic of each fit
    r2_upper: float
    heat_flux: float  # J = E / (2 t A), W/m^2


def _r2(x, y, slope, intercept) -> float:
    resid = y - (slope * x + intercept)
    return float(1.0 - np.sum(resid**2) / np.sum((y - y.mean()) ** 2))


def kappa_rnemd(
    z_bins_A,
    T_profile_K,
    exchanged_energy_kcalmol: float,
    time_fs: float,
    area_A2: float,
    *,
    Lz_A: float,
    exclude_A: float,
    z_cold_A: float = 0.0,
) -> KappaResult:
    """Thermal conductivity kappa = -J / (dT/dz) by reverse NEMD.

    Muller-Plathe, J. Chem. Phys. 106, 6082 (1997). Periodic box of length
    ``Lz_A`` along the flux axis with the cold (energy-source) slab centred at
    ``z_cold_A`` and the hot slab at ``z_cold_A + Lz_A/2``. Heat flows both
    ways round the periodic box, so J = E / (2 t A). dT/dz is fitted
    separately on each half, dropping bins whose (periodic) distance to either
    slab centre is < ``exclude_A``; kappa = J / mean(|slope_lower|, |slope_upper|),
    and per-half kappa = J / |slope|.

    Sign convention: LAMMPS ``fix thermal/conductivity`` swaps the hottest atom
    of layer 1 (box bottom) with the coldest of layer Nbin/2+1 (middle) and
    its scalar output is the cumulative kinetic energy moved from the bottom
    into the middle, which is positive (layer 1 becomes cold, the middle hot).
    Its magnitude is used here. Note LAMMPS layer 1 spans [zlo, zlo+Lz/Nbin],
    so with ``ave/chunk`` bin centres starting at zlo, the cold slab centre is
    at zlo + Lz/(2 Nbin); pass that as ``z_cold_A``.

    Units: z, Lz, exclude in Angstrom; T in K; E in kcal/mol (LAMMPS real,
    whole-system); t in fs (duration over which E accumulated); A in Angstrom^2
    (box cross-section normal to z). Returns kappa in W/(m K).
    """
    z = np.mod(np.asarray(z_bins_A, dtype=float) - z_cold_A, Lz_A)  # cold slab at 0
    T = np.asarray(T_profile_K, dtype=float)
    half = 0.5 * Lz_A
    dist = np.minimum.reduce([z, np.abs(z - half), Lz_A - z])
    keep = dist >= exclude_A

    energy_J = abs(exchanged_energy_kcalmol) * KCAL_J / AVOGADRO
    flux = energy_J / (2.0 * time_fs * FS_S * area_A2 * ANGSTROM_M**2)

    fits = []
    for sel in (keep & (z < half), keep & (z > half)):
        if sel.sum() < 3:
            raise ValueError("fewer than 3 bins in a half after exclusion")
        slope, intercept, _, _ = linear_fit(z[sel], T[sel])
        fits.append((slope, _r2(z[sel], T[sel], slope, intercept)))
    (s_lo, r2_lo), (s_up, r2_up) = fits

    def to_kappa(slope_KA: float) -> float:
        return flux / (slope_KA / ANGSTROM_M)

    return KappaResult(
        kappa=to_kappa(0.5 * (abs(s_lo) + abs(s_up))),
        kappa_lower=to_kappa(abs(s_lo)),
        kappa_upper=to_kappa(abs(s_up)),
        slope_lower=s_lo,
        slope_upper=s_up,
        r2_lower=r2_lo,
        r2_upper=r2_up,
        heat_flux=flux,
    )


@dataclass
class KappaAutoResult(KappaResult):
    """``KappaResult`` plus the automatic fit-region choice and a linearity verdict."""

    exclude_A: float  # bins closer than this to either slab centre were dropped
    linear_ok: bool  # both halves have R^2 >= min_r2
    reason: str | None  # which half failed the linearity check; None if linear_ok


def kappa_rnemd_auto(
    z_bins_A,
    T_profile_K,
    exchanged_energy_kcalmol: float,
    time_fs: float,
    area_A2: float,
    *,
    Lz_A: float,
    z_cold_A: float = 0.0,
    drop_fraction: float = 0.2,
    min_r2: float = 0.98,
) -> KappaAutoResult:
    """``kappa_rnemd`` with the fit region fixed by decision D26.

    Each half-box (length Lz/2, between the cold and hot slab centres) is
    trimmed by ``drop_fraction`` of its length at each slab end, i.e.
    exclude_A = drop_fraction * Lz_A / 2, so the default fits the middle 60%
    of each half. Both halves are reported (``kappa_lower``/``kappa_upper``);
    ``linear_ok`` is False, with a ``reason``, if either fit has
    R^2 < ``min_r2`` (non-linear profile: kappa not trustworthy). Units and
    conventions as in ``kappa_rnemd``.
    """
    if not 0.0 <= drop_fraction < 0.5:
        raise ValueError("drop_fraction must be in [0, 0.5)")
    exclude = drop_fraction * 0.5 * Lz_A
    res = kappa_rnemd(
        z_bins_A,
        T_profile_K,
        exchanged_energy_kcalmol,
        time_fs,
        area_A2,
        Lz_A=Lz_A,
        exclude_A=exclude,
        z_cold_A=z_cold_A,
    )
    bad = [
        f"R^2 of {name} half = {r2:.4f} < {min_r2}"
        for name, r2 in (("lower", res.r2_lower), ("upper", res.r2_upper))
        if not r2 >= min_r2
    ]
    return KappaAutoResult(
        **vars(res),
        exclude_A=exclude,
        linear_ok=not bad,
        reason="; ".join(bad) if bad else None,
    )
