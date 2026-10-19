"""Basic statistics: mean and error of correlated time series, weighted linear regression."""

from dataclasses import dataclass

import numpy as np

from ._corr import autocorr


@dataclass
class TimeseriesMean:
    """Mean of a correlated time series with its standard error."""

    mean: float
    sem: float  # sigma * sqrt(g / N)
    g: float  # statistical inefficiency, >= 1 (1 + 2 * integrated autocorrelation time)
    n_eff: float  # effective number of uncorrelated samples, N / g


def statistical_inefficiency(x, mintime: int = 3) -> float:
    """Statistical inefficiency g of a time series.

    g = 1 + 2 sum_{t=1}^{t_max} (1 - t/N) C(t), with C(t) the normalized
    autocorrelation function (multiple time origins, FFT), summed until the
    first lag t > ``mintime`` with C(t) <= 0; g is floored at 1. Chodera,
    Swope, Pitera, Seok & Dill, J. Chem. Theory Comput. 3, 26 (2007),
    doi:10.1021/ct0502864; same algorithm as pymbar
    ``timeseries.statisticalInefficiency`` (non-fast mode).
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 3:
        raise ValueError("need at least 3 samples")
    dx = x - x.mean()
    var = float(np.mean(dx**2))
    if var == 0.0:
        raise ValueError("series has zero variance")
    c = autocorr(dx, n - 2)[1:] / var  # lags t = 1 .. N-2
    t = np.arange(1, n - 1)
    stop = np.flatnonzero((c <= 0.0) & (t > mintime))
    k = stop[0] if len(stop) else len(t)
    g = 1.0 + 2.0 * float(np.sum(c[:k] * (1.0 - t[:k] / n)))
    return max(g, 1.0)


def timeseries_mean(x, mintime: int = 3) -> TimeseriesMean:
    """Mean, SEM = sigma sqrt(g / N), g and N_eff = N / g of a correlated series.

    g from :func:`statistical_inefficiency`; sigma is the sample standard
    deviation (ddof = 1). Discard equilibration before calling.
    """
    x = np.asarray(x, dtype=float)
    g = statistical_inefficiency(x, mintime)
    n = len(x)
    return TimeseriesMean(
        mean=float(x.mean()),
        sem=float(x.std(ddof=1) * np.sqrt(g / n)),
        g=g,
        n_eff=n / g,
    )


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
