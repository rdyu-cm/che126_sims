"""Tests for the statistical inefficiency, time-series SEM and linear fitting."""

import numpy as np
import pytest
from scipy.signal import lfilter

from sepsim.analysis.chain import drift_check
from sepsim.analysis.stats import (
    block_means,
    blocking_sem,
    linear_fit,
    statistical_inefficiency,
    timeseries_mean,
)


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


def _ringing(n, seed, phi_slow=0.995, slow_frac=0.03):
    """Barostat-like series (D55): a strongly damped oscillation (AR(2), period 6
    samples, C(t) negative from t = 2) plus a weak slow AR(1) tail holding
    ``slow_frac`` of the variance. Returns (x, exact long-run variance), i.e.
    N Var(mean) for N >> the correlation time."""
    r, th = 0.8, 2 * np.pi / 6
    a1, a2 = 2 * r * np.cos(th), -(r**2)
    rng = np.random.default_rng(seed)
    burn = 2000
    osc = lfilter([1.0], [1.0, -a1, -a2], rng.normal(size=n + burn))[burn:]
    var_osc = (1 - a2) / ((1 + a2) * ((1 - a2) ** 2 - a1**2))  # AR(2) stationary variance
    sd_slow = np.sqrt(slow_frac * var_osc)
    slow = sd_slow * np.sqrt(1 - phi_slow**2) * _ar1(phi_slow, n, seed + 1000)
    lrv = 1.0 / (1 - a1 - a2) ** 2 + sd_slow**2 * (1 + phi_slow) / (1 - phi_slow)
    return osc + slow, lrv


def test_block_sem_resolves_slow_tail_under_ringing():
    """The plain truncated ACF stops at the first negative lag (t ~ 4) and misses the
    slow tail; SI on 100-sample block means recovers the true SEM (D55)."""
    n = 50_000
    old, new, true = [], [], []
    for seed in range(8):
        x, lrv = _ringing(n, seed)
        true.append(np.sqrt(lrv / n))
        old.append(timeseries_mean(x).sem)
        r = timeseries_mean(x, block=100)
        assert r.block == 100 and r.n_blocks == 500 and not r.lower_bound
        assert r.mean == pytest.approx(x.mean()) and r.n_eff == pytest.approx(n / r.g)
        new.append(r.sem)
    true = np.mean(true)
    assert np.mean(new) == pytest.approx(true, rel=0.3)
    assert np.mean(old) < 0.6 * true  # the plain estimator underestimates


def test_block_sem_fallback_marks_lower_bound():
    x = _ar1(0.5, 1500, 4)  # 15 blocks of 100 < 20: fall back to 10 blocks of 150
    r = timeseries_mean(x, block=100)
    assert r.lower_bound and r.block == 150 and r.n_blocks == 10
    r = timeseries_mean(x, block=50)
    assert not r.lower_bound and r.block == 50 and r.n_blocks == 30
    # block=None and block=1: the plain estimator
    assert timeseries_mean(x, block=1).sem == pytest.approx(timeseries_mean(x).sem)
    np.testing.assert_allclose(block_means(np.arange(7.0), 3), [1.0, 4.0])


def test_blocking_sem_white_noise_and_ar1():
    x = np.random.default_rng(2).normal(0.0, 2.0, size=2**16)
    b = blocking_sem(x)
    assert b.block_sizes[0] == 1 and b.n_blocks[b.block_sizes == b.block][0] >= 20
    assert b.sems[0] == pytest.approx(2.0 / np.sqrt(len(x)), rel=0.02)
    assert b.sem == pytest.approx(2.0 / np.sqrt(len(x)), rel=0.35)
    phi = 0.9
    sems, want = [], []
    for seed in range(5):
        y = _ar1(phi, 2**17, seed)
        sems.append(blocking_sem(y).sem)
        want.append(y.std() * np.sqrt((1 + phi) / (1 - phi) / len(y)))
    assert np.mean(sems) == pytest.approx(np.mean(want), rel=0.2)
    # the naive SEM rises with block size to the plateau
    assert blocking_sem(y).sems[0] < 0.4 * np.mean(want)


def test_drift_check_block_means_under_ringing():
    """Stationary ringing series: halves agree within 2 sigma at about the nominal
    rate with block-mean SEMs, while the plain SEMs give many false drifts; a real
    ramp is still detected."""
    false_old = false_new = 0
    for seed in range(30):
        x, _ = _ringing(20_000, 100 + seed)
        false_old += drift_check(x)[4]
        false_new += drift_check(x, block=100)[4]
    assert false_new <= 5 and false_old >= false_new + 5
    x, _ = _ringing(20_000, 7)
    assert drift_check(x + np.linspace(0.0, 2.0, len(x)), block=100)[4]


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
