"""Tests for the VDOS and the quantum heat-capacity correction."""

import numpy as np
import pytest

from sepsim.analysis.units import H_J_S, KB_J_PER_K, KB_KCAL_PER_MOL_K
from sepsim.analysis.vdos import quantum_cv_correction, quantum_weight, vdos


def _oscillators(nu_THz, n_atoms=4, n_frames=4000, dt_fs=1.0, seed=3):
    rng = np.random.default_rng(seed)
    t = np.arange(n_frames) * dt_fs * 1e-3  # ps
    phase = rng.uniform(0, 2 * np.pi, (n_atoms, 3))
    amp = rng.uniform(0.5, 1.5, (n_atoms, 3))
    return amp * np.cos(2 * np.pi * nu_THz * t[:, None, None] + phase)


def test_vdos_peak_and_normalization():
    dt_fs, max_lag = 1.0, 1000
    dnu = 1.0 / (2 * max_lag * dt_fs * 1e-3)  # 0.5 THz grid
    nu0 = 40 * dnu  # 20 THz, on the grid
    v = _oscillators(nu0)
    res = vdos(v, np.ones(4), dt_fs, max_lag=max_lag)
    assert res.freq_THz[np.argmax(res.g)] == pytest.approx(nu0, abs=dnu / 2)
    assert np.trapezoid(res.g, res.freq_THz) == pytest.approx(12.0, rel=1e-9)
    assert res.freq_cm1[40] == pytest.approx(20.0 * 33.35641, rel=1e-6)
    res_c = vdos(v, np.ones(4), dt_fs, max_lag=max_lag, n_constraints=2)
    assert np.trapezoid(res_c.g, res_c.freq_THz) == pytest.approx(10.0, rel=1e-9)


def _einstein(nu_THz, T, n_atoms):
    u = H_J_S * nu_THz * 1e12 / (KB_J_PER_K * T)
    w = u**2 * np.exp(u) / np.expm1(u) ** 2
    return KB_KCAL_PER_MOL_K * 3 * n_atoms * (w - 1)


def test_quantum_correction_einstein_spike():
    nu = np.linspace(0, 100, 10001)
    g = np.zeros_like(nu)
    i0 = 1000  # 10 THz
    g[i0] = 12.0 / (nu[1] - nu[0])  # trapezoid integral of the spike = 3N, N = 4
    dcv = quantum_cv_correction(nu, g, 300.0)
    assert dcv == pytest.approx(_einstein(nu[i0], 300.0, 4), rel=1e-9)
    assert dcv < 0


def test_quantum_correction_from_vdos():
    dt_fs, max_lag = 1.0, 1000
    nu0 = 20.0
    res = vdos(_oscillators(nu0), np.ones(4), dt_fs, max_lag=max_lag)
    dcv = quantum_cv_correction(res.freq_THz, res.g, 300.0)
    assert dcv == pytest.approx(_einstein(nu0, 300.0, 4), rel=0.01)


def test_quantum_correction_vanishes_at_high_T():
    res = vdos(_oscillators(20.0), np.ones(4), 1.0, max_lag=1000)
    ref = abs(quantum_cv_correction(res.freq_THz, res.g, 300.0))
    assert abs(quantum_cv_correction(res.freq_THz, res.g, 1e6)) < 1e-6 * ref


def test_quantum_weight_limits():
    assert quantum_weight(0.0) == 1.0
    assert quantum_weight(1e-4) == pytest.approx(1.0 - 1e-8 / 12, rel=1e-12)
    assert quantum_weight(2000.0) == 0.0


def test_vdos_mass_weighting():
    """Unequal masses: C(t) = 3/2 sum_a m_a cos(2 pi nu_a t), so peak areas go as the masses."""
    dt_fs, max_lag, n_frames = 1.0, 1000, 8000
    dnu = 1.0 / (2 * max_lag * dt_fs * 1e-3)  # 0.5 THz grid
    nus = np.array([20, 60]) * dnu  # 10 and 30 THz, on the grid
    masses = np.array([1.0, 4.0])
    t = np.arange(n_frames) * dt_fs * 1e-3  # ps
    phase = np.random.default_rng(5).uniform(0, 2 * np.pi, (2, 3))
    v = np.cos(2 * np.pi * nus[None, :, None] * t[:, None, None] + phase)  # unit amplitude
    res = vdos(v, masses, dt_fs, max_lag=max_lag)
    areas = []
    for nu in nus:
        win = np.abs(res.freq_THz - nu) <= 5 * dnu
        areas.append(np.trapezoid(res.g[win], res.freq_THz[win]))
    # 3N = 6 states split 1:4 by mass (equal or no weighting would give 3:3).
    assert areas == pytest.approx([6.0 * 1 / 5, 6.0 * 4 / 5], rel=1e-3)


def test_reference_numbers():
    assert quantum_weight(1.0) == pytest.approx(np.e / (np.e - 1) ** 2, rel=1e-12)
    assert quantum_weight(1.0) == pytest.approx(0.920674, abs=1e-6)
    u = H_J_S * 10e12 / (KB_J_PER_K * 300.0)  # 10 THz at 300 K
    assert u == pytest.approx(1.59975, abs=1e-5)
