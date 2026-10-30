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
    block: int = 1  # samples per block mean the SEM was computed from (1: raw series)
    n_blocks: int | None = None  # number of block means (None: raw series)
    lower_bound: bool = False  # fewer than ``min_blocks`` blocks of the requested length


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


def timeseries_mean(
    x,
    mintime: int = 3,
    block: int | None = None,
    min_blocks: int = 20,
    fallback_blocks: int = 10,
) -> TimeseriesMean:
    """Mean, SEM = sigma sqrt(g / N), g and N_eff = N / g of a correlated series.

    g from :func:`statistical_inefficiency`; sigma is the sample standard
    deviation (ddof = 1). Discard equilibration before calling.

    ``block`` (samples, D55): compute the SEM from the means of consecutive
    non-overlapping blocks of ``block`` samples (trailing remainder dropped) with
    the statistical inefficiency of the block means, SEM = sigma_b sqrt(g_b / N_b).
    Use it for series whose autocorrelation is not monotone (barostat or thermostat
    ringing makes C(t) cross zero early and the plain truncation discards a long
    slow tail); pick ``block`` >= ~10 damping times. With fewer than
    ``min_blocks`` blocks the block length falls back to the largest one giving
    ``fallback_blocks`` blocks and ``lower_bound`` is set: the window is too short
    to resolve the slow component. The mean is always that of the full series; g
    and n_eff are reported in raw samples, g = N SEM^2 / sigma^2, floored at 1 (D26).
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    if block is None or block <= 1:
        g = statistical_inefficiency(x, mintime)
        return TimeseriesMean(
            mean=float(x.mean()),
            sem=float(x.std(ddof=1) * np.sqrt(g / n)),
            g=g,
            n_eff=n / g,
        )
    lower = n // block < min_blocks
    b = max(1, n // fallback_blocks) if lower else int(block)
    xb = block_means(x, b)
    nb = len(xb)
    if nb < 3:
        raise ValueError("need at least 3 blocks")
    sd = float(x.std(ddof=1))
    if sd == 0.0:
        raise ValueError("series has zero variance")
    if np.ptp(xb) == 0.0:
        sem = 0.0
    else:
        gb = statistical_inefficiency(xb, mintime)
        sem = float(xb.std(ddof=1) * np.sqrt(gb / nb))
    # floor g at 1 as in D26: never quote less than the uncorrelated SEM sigma / sqrt(N)
    sem = max(sem, sd / np.sqrt(n))
    g = n * sem**2 / sd**2
    return TimeseriesMean(
        mean=float(x.mean()), sem=sem, g=g, n_eff=n / g, block=b, n_blocks=nb, lower_bound=lower
    )


def block_means(x, block: int) -> np.ndarray:
    """Means of consecutive non-overlapping blocks of ``block`` samples (remainder dropped)."""
    x = np.asarray(x, dtype=float)
    nb = len(x) // int(block)
    if nb < 1:
        raise ValueError("series shorter than one block")
    return x[: nb * block].reshape(nb, block).mean(axis=1)


@dataclass
class Blocking:
    """Outcome of :func:`blocking_sem` (Flyvbjerg-Petersen blocking)."""

    block_sizes: np.ndarray  # samples per block, 1, 2, 4, ...
    n_blocks: np.ndarray
    sems: np.ndarray  # naive SEM of the block means at each size
    sem_errs: np.ndarray  # their 1-sigma uncertainty, SEM / sqrt(2 (n_blocks - 1))
    sem: float  # estimate: the SEM at the largest size with >= min_blocks blocks
    block: int  # that size


def blocking_sem(x, min_blocks: int = 20) -> Blocking:
    """Flyvbjerg-Petersen blocking analysis of the SEM of a correlated series.

    The series is repeatedly halved by averaging neighbouring pairs; at each level
    the naive SEM sigma_b / sqrt(N_b) of the block means is recorded (it rises and
    plateaus once blocks are longer than the correlation time). Flyvbjerg &
    Petersen, J. Chem. Phys. 91, 461 (1989), doi:10.1063/1.457480. The estimate is
    the SEM at the largest block size with at least ``min_blocks`` blocks (a
    conservative plateau read-out; inspect ``sems`` vs ``block_sizes`` to check
    that a plateau was reached). For diagnostics (D55).
    """
    x = np.asarray(x, dtype=float)
    if len(x) < 2 * min_blocks:
        raise ValueError(f"need at least {2 * min_blocks} samples")
    sizes, nbs, sems, errs = [], [], [], []
    xb, size = x.copy(), 1
    while len(xb) >= 2:
        nb = len(xb)
        se = float(xb.std(ddof=1) / np.sqrt(nb))
        sizes.append(size)
        nbs.append(nb)
        sems.append(se)
        errs.append(se / np.sqrt(2.0 * (nb - 1)))
        m = nb // 2
        xb = 0.5 * (xb[0 : 2 * m : 2] + xb[1 : 2 * m : 2])
        size *= 2
    nbs_a = np.array(nbs)
    k = int(np.flatnonzero(nbs_a >= min_blocks)[-1])
    return Blocking(
        block_sizes=np.array(sizes),
        n_blocks=nbs_a,
        sems=np.array(sems),
        sem_errs=np.array(errs),
        sem=sems[k],
        block=sizes[k],
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
