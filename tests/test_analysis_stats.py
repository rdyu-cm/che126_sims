"""Tests for the statistical inefficiency, time-series SEM and linear fitting."""

import numpy as np
import pytest
from scipy.signal import lfilter

from sepsim.analysis.stats import linear_fit, statistical_inefficiency, timeseries_mean


def _ar1(phi, n, seed):
    """x_k = phi x_{k-1} + eps_k from a stationary start."""
    eps = np.random.default_rng(seed).normal(size=n)
    eps[0] /= np.sqrt(1 - phi**2)
    return lfilter([1.0], [1.0, -phi], eps)


def _g_loop(x, mintime=3):
    """Literal transcription of the pymbar statisticalInefficiency loop (fft=False, fast=False)."""
    n = len(x)
    dx = x - x.mean()
    var = np.mean(dx * dx)
    g, t = 1.0, 1
    while t < n - 1:
        c = np.sum(dx[: n - t] * dx[t:]) / ((n - t) * var)
        if c <= 0.0 and t > mintime:
            break
        g += 2.0 * c * (1.0 - t / n)
        t += 1
    return max(g, 1.0)


def test_statistical_inefficiency_matches_reference_loop():
    for seed, phi in [(1, 0.0), (2, 0.7), (3, -0.5)]:
        x = _ar1(phi, 2000, seed)
        assert statistical_inefficiency(x) == pytest.approx(_g_loop(x), rel=1e-10)


@pytest.mark.parametrize("phi", [0.5, 0.9])
def test_statistical_inefficiency_ar1(phi):
    g_exact = (1 + phi) / (1 - phi)  # 3 and 19
    gs = [statistical_inefficiency(_ar1(phi, 200_000, seed)) for seed in range(3)]
    assert np.mean(gs) == pytest.approx(g_exact, rel=0.1)


def test_white_noise_g_is_one_and_sem():
    x = np.random.default_rng(0).normal(5.0, 2.0, size=100_000)
    res = timeseries_mean(x)
    assert 1.0 <= res.g < 1.05
    assert res.n_eff == pytest.approx(len(x) / res.g)
    expected = 2.0 / np.sqrt(len(x))
    assert res.sem == pytest.approx(expected, rel=0.05)
    assert abs(res.mean - 5.0) < 4 * expected


def test_sem_matches_spread_of_means_ar1():
    phi, n = 0.8, 20_000
    runs = [_ar1(phi, n, seed) for seed in range(200)]
    spread = np.std([r.mean() for r in runs], ddof=1)
    sems = [timeseries_mean(r).sem for r in runs]
    assert np.mean(sems) == pytest.approx(spread, rel=0.15)


def test_statistical_inefficiency_rejects_constant():
    with pytest.raises(ValueError, match="zero variance"):
        statistical_inefficiency(np.ones(10))


def test_linear_fit_unweighted_and_weighted():
    rng = np.random.default_rng(1)
    x = np.linspace(0, 10, 50)
    sigma = np.full_like(x, 0.5)
    y = 3.0 * x - 2.0 + rng.normal(0, 0.5, x.size)
    for s in (None, sigma):
        slope, intercept, slope_err, intercept_err = linear_fit(x, y, s)
        assert abs(slope - 3.0) < 3 * slope_err
        assert abs(intercept + 2.0) < 3 * intercept_err
    # analytic WLS slope error: sigma / sqrt(sum (x - xbar)^2)
    _, _, slope_err, _ = linear_fit(x, y, sigma)
    np.testing.assert_allclose(slope_err, 0.5 / np.sqrt(np.sum((x - x.mean()) ** 2)))
