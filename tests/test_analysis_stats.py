"""Tests for block averaging and linear fitting."""

import numpy as np

from sepsim.analysis.stats import block_average, linear_fit


def test_block_average_iid():
    rng = np.random.default_rng(0)
    x = rng.normal(5.0, 2.0, size=100_003)  # remainder of 3 dropped
    mean, sem = block_average(x, n_blocks=100)
    expected = 2.0 / np.sqrt(100_000)
    assert abs(mean - 5.0) < 4 * expected
    assert 0.75 * expected < sem < 1.25 * expected  # 100 blocks: ~7% scatter


def test_block_average_drops_leading_remainder():
    x = np.array([100.0, 1.0, 2.0, 3.0, 4.0])
    mean, _ = block_average(x, n_blocks=2)
    assert mean == 2.5


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
