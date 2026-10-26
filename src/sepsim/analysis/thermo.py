"""Density, thermal expansion and classical heat capacity from T-step means."""

from dataclasses import dataclass

import numpy as np

from .stats import linear_fit, timeseries_mean
from .units import A3_CM3, AVOGADRO, KB_J_PER_K, KCAL_J


def density(mass_gmol, volume_A3):
    """Mass density rho = M / (N_A * V) in g/cm^3.

    ``mass_gmol``: total system mass (g/mol, LAMMPS real); ``volume_A3``: box
    volume in Angstrom^3 (scalar or array).
    """
    return np.asarray(mass_gmol, dtype=float) / (
        AVOGADRO * np.asarray(volume_A3, dtype=float) * A3_CM3
    )


def _window(T, *arrays, T_window):
    T = np.asarray(T, dtype=float)
    mask = np.ones(T.shape, bool)
    if T_window is not None:
        mask = (T >= T_window[0]) & (T <= T_window[1])
    if mask.sum() < 3:
        raise ValueError("need at least 3 temperature points in the window")
    return [T[mask]] + [None if a is None else np.asarray(a, dtype=float)[mask] for a in arrays]


@dataclass
class ThermalExpansion:
    """Thermal expansion coefficients (1/K) with 1-sigma uncertainties."""

    alpha_V: float
    alpha_V_err: float
    alpha_L: float
    alpha_L_err: float
    V_mean: float  # mean volume over the window, Angstrom^3
    n_points: int


def thermal_expansion(T, V, V_err=None, T_window=None) -> ThermalExpansion:
    """Volumetric and linear thermal expansion coefficients from V(T).

    alpha_V = (1/V_mean) dV/dT, with dV/dT the slope of a linear fit of V vs T
    over ``T_window`` = (T_min, T_max) inclusive (all points if None), V_mean the
    mean of V over the same points; alpha_L = alpha_V / 3 (isotropic).
    Bulk (isotropically barostatted) boxes only; for slabs barostatted in x, y
    use :func:`thermal_expansion_inplane`.
    Errors: sigma(alpha_V) = sigma(slope) / V_mean (V_mean error neglected).
    Inputs: T in K, V in Angstrom^3 (per-step means; ``V_err`` their SEMs from
    :func:`sepsim.analysis.stats.timeseries_mean`, used as fit weights).
    """
    T, V, V_err = _window(T, V, V_err, T_window=T_window)
    slope, _, slope_err, _ = linear_fit(T, V, V_err)
    v_mean = float(V.mean())
    a, a_err = slope / v_mean, slope_err / v_mean
    return ThermalExpansion(a, a_err, a / 3.0, a_err / 3.0, v_mean, len(T))


@dataclass
class InPlaneExpansion:
    """In-plane thermal expansion of a slab (1/K) with 1-sigma uncertainties."""

    alpha_A: float  # areal, (1/A) dA/dT
    alpha_A_err: float
    alpha_L: float  # in-plane linear, alpha_A / 2
    alpha_L_err: float
    A_mean: float  # mean box area Lx * Ly over the window, Angstrom^2
    n_points: int


def thermal_expansion_inplane(T, A, A_err=None, T_window=None) -> InPlaneExpansion:
    """Areal and in-plane linear expansion from the box area A = Lx * Ly of a slab.

    For a slab (e.g. a membrane with vacuum or fixed walls along z) barostatted
    only in x and y, the box volume is not the material volume, so use the
    area: alpha_A = (1/A_mean) dA/dT from a linear fit of A vs T over
    ``T_window`` (as :func:`thermal_expansion`), and the in-plane linear
    coefficient alpha_L = alpha_A / 2 (isotropic in the plane).
    Inputs: T in K, A in Angstrom^2 (per-step means; ``A_err`` their SEMs).
    """
    T, A, A_err = _window(T, A, A_err, T_window=T_window)
    slope, _, slope_err, _ = linear_fit(T, A, A_err)
    a_mean = float(A.mean())
    a, a_err = slope / a_mean, slope_err / a_mean
    return InPlaneExpansion(a, a_err, a / 2.0, a_err / 2.0, a_mean, len(T))


@dataclass
class HeatCapacity:
    """Isobaric heat capacity with 1-sigma uncertainties."""

    cp_kcalmolK: float  # total system, kcal/(mol K), "mol" = mole of systems
    cp_kcalmolK_err: float
    cp_JgK: float  # specific, J/(g K)
    cp_JgK_err: float
    n_points: int


def heat_capacity_classical(T, H_kcalmol, mass_gmol, H_err=None, T_window=None) -> HeatCapacity:
    """Classical isobaric heat capacity Cp = dH/dT from a linear fit of H(T).

    ``H_kcalmol`` is the total (extensive) LAMMPS enthalpy in kcal/mol (per mole
    of whole systems) and ``mass_gmol`` the total system mass in g/mol, so
    Cp [J/(g K)] = slope [kcal/(mol K)] * 4184 / mass_gmol.
    Fit over ``T_window`` = (T_min, T_max) inclusive; ``H_err`` are SEMs (e.g.
    :func:`sepsim.analysis.stats.timeseries_mean`) used as weights. This is the classical value; for AA add
    :func:`sepsim.analysis.vdos.quantum_cv_correction` (D12c).
    """
    T, H, H_err = _window(T, H_kcalmol, H_err, T_window=T_window)
    slope, _, slope_err, _ = linear_fit(T, H, H_err)
    to_jg = KCAL_J / float(mass_gmol)
    return HeatCapacity(slope, slope_err, slope * to_jg, slope_err * to_jg, len(T))


@dataclass
class Compressibility:
    """Isothermal compressibility from NPT volume fluctuations, with its SEM."""

    kappa_T: float  # 1/GPa
    kappa_T_sem: float  # 1/GPa
    V_mean: float  # Angstrom^3
    V_std: float  # Angstrom^3 (population, ddof = 0)
    g: float  # statistical inefficiency of (V - <V>)^2
    n_samples: int


def isothermal_compressibility(V_A3, T_K: float, mintime: int = 3) -> Compressibility:
    """kappa_T = (<V^2> - <V>^2) / (k_B T <V>) from an NPT volume series.

    The standard isothermal-isobaric fluctuation formula (Allen & Tildesley,
    Computer Simulation of Liquids, 2nd ed., OUP 2017, sec. 2.5); valid for an
    ensemble that samples NPT fluctuations correctly (e.g. Nose-Hoover/MTK ``fix
    npt``, not a Berendsen barostat). ``V_A3``: box volumes in Angstrom^3, sampled
    at equal intervals after equilibration; ``T_K``: the ensemble temperature.
    SEM: the variance is the mean of s = (V - <V>)^2, so its SEM is the
    statistical-inefficiency SEM of s (:func:`sepsim.analysis.stats.timeseries_mean`,
    D26); the uncertainty of <V> (relative ~1e-4) is neglected. Returns 1/GPa.
    """
    v = np.asarray(V_A3, dtype=float)
    if len(v) < 3:
        raise ValueError("need at least 3 volume samples")
    dv2 = (v - v.mean()) ** 2
    s = timeseries_mean(dv2, mintime)
    # A^6 / (J * A^3) = 1e-30 m^3 / J = 1e-30 1/Pa; 1/GPa = 1e9 1/Pa
    to_gpa = 1e-30 * 1e9 / (KB_J_PER_K * float(T_K) * float(v.mean()))
    return Compressibility(
        kappa_T=s.mean * to_gpa,
        kappa_T_sem=s.sem * to_gpa,
        V_mean=float(v.mean()),
        V_std=float(np.sqrt(s.mean)),
        g=s.g,
        n_samples=len(v),
    )
