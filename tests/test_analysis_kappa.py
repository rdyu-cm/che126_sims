"""Tests for the reverse-NEMD thermal conductivity."""

import numpy as np
import pytest

from sepsim.analysis.kappa import kappa_rnemd, kappa_rnemd_auto


def _profile(kappa, E_kcalmol, t_fs, A_A2, Lz, nbins, T_cold=280.0):
    # Self-consistency check: re-derives the flux formula kappa_rnemd uses, so not independent.
    flux = E_kcalmol * 4184.0 / 6.02214076e23 / (2 * t_fs * 1e-15 * A_A2 * 1e-20)
    grad = flux / kappa * 1e-10  # K/Angstrom
    z = (np.arange(nbins) + 0.5) * Lz / nbins
    zc = Lz / (2 * nbins)  # cold slab = first bin centre (LAMMPS layer 1)
    s = np.mod(z - zc, Lz)
    T = T_cold + grad * np.minimum(s, Lz - s)  # exact sawtooth
    return z, T, zc


def test_kappa_recovers_exact_sawtooth():
    kappa, E, t, A, Lz = 0.35, 5.0e4, 1.0e6, 900.0, 300.0
    z, T, zc = _profile(kappa, E, t, A, Lz, nbins=40)
    res = kappa_rnemd(z, T, E, t, A, Lz_A=Lz, exclude_A=20.0, z_cold_A=zc)
    assert res.kappa == pytest.approx(kappa, rel=1e-6)
    assert res.kappa_lower == pytest.approx(kappa, rel=1e-6)
    assert res.kappa_upper == pytest.approx(kappa, rel=1e-6)
    assert res.slope_lower > 0 > res.slope_upper
    assert res.r2_lower == pytest.approx(1.0) and res.r2_upper == pytest.approx(1.0)
    # sign of the exchanged energy does not matter
    neg = kappa_rnemd(z, T, -E, t, A, Lz_A=Lz, exclude_A=20.0, z_cold_A=zc)
    assert neg.kappa == pytest.approx(res.kappa, rel=1e-12)


def test_kappa_exclusion_zone_respected():
    kappa, E, t, A, Lz = 0.35, 5.0e4, 1.0e6, 900.0, 300.0
    z, T, zc = _profile(kappa, E, t, A, Lz, nbins=40)
    s = np.mod(z - zc, Lz)
    near = np.minimum.reduce([s, np.abs(s - Lz / 2), Lz - s]) < 20.0
    T_bad = T.copy()
    T_bad[near] += np.random.default_rng(7).normal(0, 50.0, near.sum())  # garbage near slabs
    res = kappa_rnemd(z, T_bad, E, t, A, Lz_A=Lz, exclude_A=20.0, z_cold_A=zc)
    assert res.kappa == pytest.approx(kappa, rel=1e-6)
    bad = kappa_rnemd(z, T_bad, E, t, A, Lz_A=Lz, exclude_A=0.0, z_cold_A=zc)
    assert bad.kappa != pytest.approx(kappa, rel=1e-3)


def test_kappa_auto_linear_profile():
    kappa, E, t, A, Lz = 0.35, 5.0e4, 1.0e6, 900.0, 300.0
    z, T, zc = _profile(kappa, E, t, A, Lz, nbins=40)
    res = kappa_rnemd_auto(z, T, E, t, A, Lz_A=Lz, z_cold_A=zc)
    assert res.exclude_A == pytest.approx(0.2 * Lz / 2)
    assert res.kappa == pytest.approx(kappa, rel=1e-6)
    assert res.kappa_lower == pytest.approx(kappa, rel=1e-6)
    assert res.kappa_upper == pytest.approx(kappa, rel=1e-6)
    assert res.linear_ok and res.reason is None
    manual = kappa_rnemd(z, T, E, t, A, Lz_A=Lz, exclude_A=0.1 * Lz, z_cold_A=zc)
    assert res.kappa == manual.kappa


def test_kappa_auto_flags_curved_profile():
    kappa, E, t, A, Lz = 0.35, 2.5e3, 1.0e6, 900.0, 300.0  # dT/dz ~ 0.28 K/A, ~41 K per half
    z, T, zc = _profile(kappa, E, t, A, Lz, nbins=40)
    s = np.mod(z - zc, Lz)
    lower = s < Lz / 2
    T_curved = T.copy()
    T_curved[lower] += 10.0 * np.sin(2 * np.pi * s[lower] / Lz)  # 10 K hump, lower half only
    res = kappa_rnemd_auto(z, T_curved, E, t, A, Lz_A=Lz, z_cold_A=zc)
    assert res.r2_lower < 0.98 <= res.r2_upper
    assert not res.linear_ok
    assert "lower" in res.reason and "upper" not in res.reason
