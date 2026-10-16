"""Tests for MSD and P2 reorientation correlation."""

import numpy as np
import pytest

from sepsim.analysis.mobility import msd, p2_autocorrelation


def test_msd_ballistic_exact():
    t = np.arange(50)
    vel = np.array([[1.0, 2.0, -2.0], [0.0, 3.0, 4.0]])  # |v|^2 = 9, 25
    r = t[:, None, None] * vel[None]
    lag, m = msd(r, dt=0.5, max_lag=20)
    np.testing.assert_allclose(lag, 0.5 * np.arange(21))
    np.testing.assert_allclose(m, 17.0 * np.arange(21) ** 2, atol=1e-8)


def test_msd_matches_direct():
    r = np.cumsum(np.random.default_rng(4).normal(size=(60, 3, 3)), axis=0)
    _, m = msd(r, dt=1.0, max_lag=30)
    direct = [np.mean(np.sum((r[k:] - r[: len(r) - k]) ** 2, axis=2)) for k in range(31)]
    np.testing.assert_allclose(m, direct, atol=1e-9)


def test_msd_random_walk_diffusion():
    D, dt = 0.25, 2.0
    sigma = np.sqrt(2 * D * dt)  # per-component step std
    steps = np.random.default_rng(5).normal(0, sigma, size=(1000, 200, 3))
    r = np.cumsum(steps, axis=0)
    lag, m = msd(r, dt, max_lag=100)
    slope = np.polyfit(lag[1:], m[1:], 1)[0]
    assert slope / 6 == pytest.approx(D, rel=0.05)


def test_p2_static_and_random():
    rng = np.random.default_rng(6)
    static = np.repeat(rng.normal(size=(1, 50, 3)) * 3.0, 100, axis=0)
    _, c = p2_autocorrelation(static, dt=1.0)
    np.testing.assert_allclose(c, 1.0, atol=1e-12)

    random = rng.normal(size=(2000, 50, 3))
    lag, c = p2_autocorrelation(random, dt=1.0, max_lag=50)
    assert c[0] == pytest.approx(1.0)
    assert np.all(np.abs(c[1:]) < 0.02)
    assert len(lag) == 51
