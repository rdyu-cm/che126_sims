"""Density, thermal expansion and classical heat capacity from T-step means."""

from dataclasses import dataclass

import numpy as np

from .stats import linear_fit
from .units import A3_CM3, AVOGADRO, KCAL_J


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
    Errors: sigma(alpha_V) = sigma(slope) / V_mean (V_mean error neglected).
    Inputs: T in K, V in Angstrom^3 (per-step means; ``V_err`` their SEMs, used
    as fit weights).
    """
    T, V, V_err = _window(T, V, V_err, T_window=T_window)
    slope, _, slope_err, _ = linear_fit(T, V, V_err)
    v_mean = float(V.mean())
    a, a_err = slope / v_mean, slope_err / v_mean
    return ThermalExpansion(a, a_err, a / 3.0, a_err / 3.0, v_mean, len(T))


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
    Fit over ``T_window`` = (T_min, T_max) inclusive; ``H_err`` are SEMs used as
    weights. This is the classical value; for AA add
    :func:`sepsim.analysis.vdos.quantum_cv_correction` (D12c).
    """
    T, H, H_err = _window(T, H_kcalmol, H_err, T_window=T_window)
    slope, _, slope_err, _ = linear_fit(T, H, H_err)
    to_jg = KCAL_J / float(mass_gmol)
    return HeatCapacity(slope, slope_err, slope * to_jg, slope_err * to_jg, len(T))
