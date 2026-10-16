"""Basic statistics: block averaging and weighted linear regression."""

import numpy as np


def block_average(x, n_blocks: int = 5) -> tuple[float, float]:
    """Mean and standard error of a correlated time series by block averaging.

    The series is split into ``n_blocks`` equal contiguous blocks (the
    ``len(x) % n_blocks`` leading samples are dropped as extra equilibration).
    mean = mean of block means; sem = std(block means, ddof=1) / sqrt(n_blocks).
    Flyvbjerg & Petersen, J. Chem. Phys. 91, 461 (1989).
    """
    x = np.asarray(x, dtype=float)
    if n_blocks < 2 or len(x) < n_blocks:
        raise ValueError("need n_blocks >= 2 and len(x) >= n_blocks")
    x = x[len(x) % n_blocks :]
    means = x.reshape(n_blocks, -1).mean(axis=1)
    return float(means.mean()), float(means.std(ddof=1) / np.sqrt(n_blocks))


def linear_fit(x, y, sigma=None) -> tuple[float, float, float, float]:
    """Least-squares fit y = slope*x + intercept.

    With ``sigma`` (absolute 1-sigma errors of y) this is weighted least squares
    with weights 1/sigma^2 and parameter errors from the unscaled covariance
    (X^T W X)^-1. Without ``sigma`` it is ordinary least squares with the
    covariance scaled by the residual variance chi^2/(n-2) (needs n > 2).
    Returns (slope, intercept, slope_err, intercept_err).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if sigma is None:
        p, cov = np.polyfit(x, y, 1, cov=True)
    else:
        w = 1.0 / np.asarray(sigma, dtype=float)
        p, cov = np.polyfit(x, y, 1, w=w, cov="unscaled")
    err = np.sqrt(np.diag(cov))
    return float(p[0]), float(p[1]), float(err[0]), float(err[1])
