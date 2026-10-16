"""Vibrational density of states and the quantum-harmonic heat-capacity correction."""

from dataclasses import dataclass

import numpy as np

from ._corr import autocorr, check_max_lag
from .units import FS_S, H_J_S, KB_J_PER_K, KB_KCAL_PER_MOL_K, THZ_CM1, THZ_HZ

_ATOM_CHUNK = 1024  # atoms per FFT batch, bounds memory for large systems


@dataclass
class VDOS:
    """Vibrational density of states g(nu), normalized to int g dnu = 3N - n_constraints."""

    freq_THz: np.ndarray
    freq_cm1: np.ndarray
    g: np.ndarray  # states per THz (total system)


def vdos(velocities, masses, dt_fs: float, max_lag: int | None = None, n_constraints: int = 0):
    """VDOS from the mass-weighted velocity autocorrelation function (Wiener-Khinchin).

    C(t) = sum_i m_i <v_i(0) . v_i(t)>  (multiple time origins, all atoms and
    Cartesian components), truncated at ``max_lag`` frames (default
    n_frames // 2) and multiplied by a Hann taper w(t) = [1 + cos(pi t / t_max)] / 2
    to suppress truncation ringing. Then
        g(nu) ∝ ∫ w(t) C(t) cos(2 pi nu t) dt,   nu >= 0,
    rescaled so that ∫_0^nu_Nyquist g dnu = 3N - n_constraints (trapezoid rule).
    Frequency resolution is 1 / (2 * max_lag * dt).
    Dickey & Paskin, Phys. Rev. 188, 1407 (1969); Berens et al., J. Chem. Phys.
    79, 2375 (1983).

    ``velocities``: (n_frames, n_atoms, 3), any units; ``masses``: (n_atoms,);
    ``dt_fs``: time between frames in fs (must resolve the highest frequency,
    e.g. C-H stretch ~90 THz needs dt <= ~5 fs).
    """
    v = np.asarray(velocities, dtype=float)
    m = np.asarray(masses, dtype=float)
    n_frames, n_atoms, _ = v.shape
    max_lag = check_max_lag(n_frames, max_lag)

    c = np.zeros(max_lag + 1)
    for start in range(0, n_atoms, _ATOM_CHUNK):
        sl = slice(start, start + _ATOM_CHUNK)
        acf = autocorr(v[:, sl, :], max_lag)  # (lag, atoms, 3)
        c += np.einsum("tai,a->t", acf, m[sl])

    lags = np.arange(max_lag + 1)
    c *= 0.5 * (1.0 + np.cos(np.pi * lags / max_lag))
    c_sym = np.concatenate([c, c[-2:0:-1]])  # even extension, length 2*max_lag
    spec = np.fft.rfft(c_sym).real
    freq_THz = np.fft.rfftfreq(len(c_sym), d=dt_fs * FS_S) / THZ_HZ
    g = spec * (3 * n_atoms - n_constraints) / np.trapezoid(spec, freq_THz)
    return VDOS(freq_THz, freq_THz * THZ_CM1, g)


def quantum_weight(u):
    """Harmonic quantum/classical heat-capacity weight W_Q(u) = u^2 e^u / (e^u - 1)^2.

    Evaluated as u^2 e^-u / (1 - e^-u)^2 with |u| (even in u; overflow-free);
    W_Q(0) = 1.
    """
    u = np.abs(np.asarray(u, dtype=float))
    safe = np.where(u == 0.0, 1.0, u)
    return np.where(u == 0.0, 1.0, safe**2 * np.exp(-safe) / np.expm1(-safe) ** 2)


def quantum_cv_correction(freq_THz, g, T: float) -> float:
    """Quantum-harmonic correction to the classical heat capacity, kcal/(mol K).

    dCv = kB ∫ g(nu) [W_Q(u) - 1] dnu,  u = h nu / (kB T),
    W_Q(u) = u^2 e^u / (e^u - 1)^2 (Berens, Mackay, White & Wilson,
    J. Chem. Phys. 79, 2375 (1983)). ``g`` (states/THz, total system, e.g. from
    :func:`vdos`) on grid ``freq_THz``; T in K. Returns the total-system value
    in kcal/(mol K) ("mol" = mole of systems, same as LAMMPS real enthalpy), so
    it is added directly to the classical dH/dT. dCv <= 0.

    Harmonic approximation: each VDOS mode is treated as an independent
    harmonic oscillator; anharmonicity and the Cp - Cv difference of the
    correction are neglected.
    """
    nu = np.asarray(freq_THz, dtype=float)
    u = H_J_S * nu * THZ_HZ / (KB_J_PER_K * T)
    return float(KB_KCAL_PER_MOL_K * np.trapezoid(np.asarray(g) * (quantum_weight(u) - 1.0), nu))
