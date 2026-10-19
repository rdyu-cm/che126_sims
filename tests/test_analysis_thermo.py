"""Tests for density, thermal expansion and classical heat capacity."""

import numpy as np
import pytest

from sepsim.analysis.thermo import (
    density,
    heat_capacity_classical,
    thermal_expansion,
    thermal_expansion_inplane,
)


def test_density_exact():
    # N_A * 10 A^3 = 6.02214076e24 A^3 = 6.02214076 cm^3 -> 1 g/cm^3
    assert density(6.02214076, 10.0) == pytest.approx(1.0, rel=1e-12)
    np.testing.assert_allclose(density(6.02214076, np.array([10.0, 20.0])), [1.0, 0.5])


def test_thermal_expansion_recovers_alpha():
    T = np.arange(298.0, 434.0, 10.0)
    alpha, V0 = 7e-4, 50_000.0
    T0 = T.mean()  # alpha_V = (1/Vbar) dV/dT equals alpha exactly when T0 = mean(T)
    V = V0 * (1 + alpha * (T - T0))
    V += np.random.default_rng(2).normal(0, 1.0, T.size)
    res = thermal_expansion(T, V)
    assert res.alpha_V == pytest.approx(alpha, rel=0.01)
    assert res.alpha_L == pytest.approx(alpha / 3, rel=0.01)
    assert res.alpha_V_err > 0


def test_thermal_expansion_window():
    T = np.arange(300.0, 410.0, 10.0)
    V = np.where(T < 350, 1000 + 1.0 * (T - 300), 1050 + 3.0 * (T - 350))
    res = thermal_expansion(T, V, V_err=np.full(T.size, 0.1), T_window=(350, 400))
    assert res.n_points == 6
    assert res.alpha_V == pytest.approx(3.0 / V[T >= 350].mean(), rel=1e-9)


def test_heat_capacity_classical():
    T = np.arange(300.0, 400.0, 10.0)
    slope, mass = 25.0, 10_000.0  # kcal/(mol K), g/mol
    H = -5000.0 + slope * T
    res = heat_capacity_classical(T, H, mass)
    assert res.cp_kcalmolK == pytest.approx(slope, rel=1e-9)
    assert res.cp_JgK == pytest.approx(25.0 * 4184.0 / 10_000.0, rel=1e-9)  # 10.46 J/(g K)
    assert res.n_points == 10


def test_inplane_expansion_from_area():
    T = np.arange(300.0, 400.0, 10.0)
    alpha_L = 1e-4
    Lx = 50.0 * (1 + alpha_L * (T - T.mean()))
    Ly = 40.0 * (1 + alpha_L * (T - T.mean()))
    res = thermal_expansion_inplane(T, Lx * Ly)
    assert res.alpha_L == pytest.approx(alpha_L, rel=1e-3)  # second-order term alpha_L^2
    assert res.alpha_A == pytest.approx(2 * res.alpha_L, rel=1e-12)
    assert res.A_mean == pytest.approx(2000.0, rel=1e-3)
    assert res.n_points == 10
