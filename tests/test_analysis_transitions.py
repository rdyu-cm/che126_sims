"""Tests for the heating-ramp melting point."""

import numpy as np
import pytest

from sepsim.analysis.transitions import melting_point

TM = 411.3  # K, deliberately off the grid


def _ramp(dT=5.0, width=3.0):
    T = np.arange(300.0, 500.0 + dT / 2, dT)
    x = 0.6 / (1.0 + np.exp((T - TM) / width))  # sigmoid from 0.6 to 0, midpoint TM
    return T, x


def test_tm_from_sigmoid_within_grid_resolution():
    T, x = _ramp()
    res = melting_point(T, x)
    assert res.initial_fraction == pytest.approx(0.6)
    assert abs(res.Tm - TM) < 5.0  # grid spacing
    assert res.consistent and res.reason is None
    assert np.isnan(res.T_max_dVdT) and np.isnan(res.T_max_dHdT)


def test_volume_and_enthalpy_steps_agree():
    T, x = _ramp()
    V = 1000.0 + 0.5 * T + 80.0 * (T > TM)  # thermal expansion + melting jump
    H = 10.0 * T + 2000.0 / (1.0 + np.exp(-(T - TM) / 2.0))
    res = melting_point(T, x, V=V, H=H)
    assert res.T_max_dVdT == pytest.approx(412.5)  # midpoint of the bracketing interval
    assert abs(res.T_max_dHdT - TM) <= 2.5
    assert res.consistent and res.reason is None


def test_disagreeing_cross_check_flagged():
    T, x = _ramp()
    V = 1000.0 + 80.0 * (T > TM + 40.0)
    res = melting_point(T, x, V=V, tolerance_K=15.0)
    assert not res.consistent
    assert "dV/dT" in res.reason
    assert abs(res.Tm - TM) < 5.0


def test_never_halving_gives_nan_with_reason():
    T = np.linspace(300.0, 400.0, 21)
    x = 0.6 - 0.001 * (T - 300.0)  # falls only to 0.5
    res = melting_point(T, x)
    assert np.isnan(res.Tm)
    assert not res.consistent
    assert "never falls to half" in res.reason


def test_rejects_non_increasing_temperature():
    with pytest.raises(ValueError):
        melting_point([300.0, 300.0, 310.0], [0.5, 0.4, 0.1])
