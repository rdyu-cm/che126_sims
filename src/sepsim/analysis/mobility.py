"""Chain mobility: mean-squared displacement and bond-vector reorientation."""

from dataclasses import dataclass

import numpy as np

from ._corr import autocorr, check_max_lag
from .stats import linear_fit


def msd(positions_unwrapped, dt: float, max_lag: int | None = None):
    """Mean-squared displacement averaged over atoms and time origins.

    MSD(t_m) = < |r_i(k+m) - r_i(k)|^2 >_{i,k}, using every origin k; computed
    in O(N log N) as MSD(m) = S1(m) - 2 S2(m), with S2 the FFT position
    autocorrelation (Calandrini et al., Collection SFN 12, 201 (2011);
    nMoldyn). Positions (n_frames, n_atoms, 3) must be unwrapped; for
    polymers pass monomer or chain-COM positions as appropriate.
    Returns (lag_times, msd) for lags 0..max_lag (default n_frames // 2);
    lag_times in units of ``dt``, msd in squared position units.
    Diffusion: D = slope / 6 in the linear (Fickian) regime.
    Same algorithm as MDAnalysis ``EinsteinMSD(fft=True)``, which is not used
    because it needs a Universe, has no max_lag and needs the ``tidynamics`` package.
    """
    r = np.asarray(positions_unwrapped, dtype=float)
    n = r.shape[0]
    max_lag = check_max_lag(n, max_lag)
    m = np.arange(max_lag + 1)

    d2 = np.sum(r**2, axis=2)  # (frames, atoms)
    cs = np.concatenate([np.zeros((1, d2.shape[1])), np.cumsum(d2, axis=0)])
    s1 = (cs[n - m] + cs[n] - cs[m]) / (n - m)[:, None]
    s2 = autocorr(r, max_lag).sum(axis=2)
    return m * dt, (s1 - 2.0 * s2).mean(axis=1)


def p2_autocorrelation(vectors, dt: float, max_lag: int | None = None):
    """Second-Legendre reorientation correlation C(t) = < P2(u(0) . u(t)) >.

    P2(x) = (3x^2 - 1)/2, u = vector/|vector|, averaged over vectors and time
    origins. Uses x^2 = sum_ab u_a u_b(0) u_a u_b(t), so
    C(t) = 1.5 * sum_ab <u_a u_b(0) u_a u_b(t)> - 0.5 via FFT autocorrelation.
    ``vectors``: (n_frames, n_vectors, 3) bond/segment vectors (unwrapped or
    minimum-image). Returns (lag_times, C) for lags 0..max_lag (default
    n_frames // 2); C(0) = 1, C -> 0 for isotropic decorrelation.
    """
    u = np.asarray(vectors, dtype=float)
    u = u / np.linalg.norm(u, axis=2, keepdims=True)
    max_lag = check_max_lag(u.shape[0], max_lag)
    products = (u[..., :, None] * u[..., None, :]).reshape(u.shape[0], u.shape[1], 9)
    c = 1.5 * autocorr(products, max_lag).sum(axis=2).mean(axis=1) - 0.5
    return np.arange(max_lag + 1) * dt, c


def mean_over_batches(fn, x, dt: float, max_lag: int, batch_elems: int = 4_000_000):
    """``fn(x[:, batch], dt, max_lag)`` (:func:`msd` or :func:`p2_autocorrelation`)
    averaged over batches of the second axis, weighted by batch size.

    Both functions average over that axis, so this equals ``fn(x, dt, max_lag)``
    while bounding the FFT work array to about ``batch_elems`` complex values
    (frames are zero-padded to the next power of two >= 2 n_frames - 1; P2 uses 9
    components per vector, MSD 3).
    """
    x = np.asarray(x)
    nfft = 1 << (2 * x.shape[0] - 1).bit_length()
    comps = 9 if fn is p2_autocorrelation else 3
    size = max(1, batch_elems // (nfft * comps))
    total, lags = None, None
    for k in range(0, x.shape[1], size):
        part = x[:, k : k + size]
        lags, c = fn(part.astype(float), dt, max_lag)
        total = c * part.shape[1] if total is None else total + c * part.shape[1]
    return lags, total / x.shape[1]


def average_curves(curves):
    """Average (lags, values, n_frames) curves of several short trajectories (bursts).

    Each curve is weighted at lag index m by its number of time origins n_frames - m;
    lags must share one spacing. Returns (lags, values) up to the longest curve.
    """
    curves = list(curves)
    if not curves:
        raise ValueError("no curves")
    n = max(len(c[0]) for c in curves)
    total, weight = np.zeros(n), np.zeros(n)
    lags = max((c[0] for c in curves), key=len)
    for lag, val, n_frames in curves:
        m = np.arange(len(val))
        w = n_frames - m
        total[: len(val)] += w * np.asarray(val, dtype=float)
        weight[: len(val)] += w
    return np.asarray(lags, dtype=float), total / weight


def stitch_curves(short_lags, short_vals, long_lags, long_vals):
    """One curve from a finely sampled short trajectory and a coarse long one.

    Keeps the short curve (e.g. 0.1 ps burst frames) for lags below the long curve's
    first nonzero lag (its frame interval, e.g. 10 ps) and the long curve (more time
    origins) from that lag on. Returns (lags, values, source) with source 0 for
    short and 1 for long points.
    """
    sl, sv = np.asarray(short_lags, dtype=float), np.asarray(short_vals, dtype=float)
    ll, lv = np.asarray(long_lags, dtype=float), np.asarray(long_vals, dtype=float)
    first = ll[ll > 0][0] if np.any(ll > 0) else np.inf
    keep_s = sl < first * (1 - 1e-9)
    keep_l = ll >= first * (1 - 1e-9)
    lags = np.concatenate([sl[keep_s], ll[keep_l]])
    vals = np.concatenate([sv[keep_s], lv[keep_l]])
    src = np.concatenate([np.zeros(keep_s.sum(), int), np.ones(keep_l.sum(), int)])
    return lags, vals, src


@dataclass
class DiffusionFit:
    """Outcome of :func:`diffusion_coefficient`."""

    diffusive: bool  # a trailing range with local log-slope >= min_slope was found
    D: float | None  # MSD units per lag unit (e.g. A^2/ns), MSD = 2 dim D t + c
    D_err: float | None  # from the OLS slope error (correlated points: a lower bound)
    t_start: float | None  # fit range in lag units
    t_end: float | None
    slope_end: float  # local log-slope at the longest lag
    slope_max: float  # largest local log-slope over the curve


def local_log_slope(lags, values, factor: float = 1.25):
    """d ln(values) / d ln(lag) on a log-spaced subset of the positive lags.

    Points are picked so successive lags grow by at least ``factor`` (which smooths
    the dense long-lag tail); returns (lags_subset, slope) from np.gradient.
    """
    t, y = np.asarray(lags, dtype=float), np.asarray(values, dtype=float)
    ok = (t > 0) & (y > 0)
    t, y = t[ok], y[ok]
    pick, last = [], -np.inf
    for k, tk in enumerate(t):
        if tk >= last * factor:
            pick.append(k)
            last = tk
    if pick[-1] != len(t) - 1:
        pick.append(len(t) - 1)
    t, y = t[pick], y[pick]
    if len(t) < 2:
        raise ValueError("need at least 2 positive lags")
    return t, np.gradient(np.log(y), np.log(t))


def diffusion_coefficient(
    lags, msd_values, min_slope: float = 0.9, min_span: float = 2.0, dim: int = 3
) -> DiffusionFit:
    """Self-diffusion coefficient from the diffusive (Fickian) end of an MSD curve.

    Criterion: the local log-slope (:func:`local_log_slope`) is >= ``min_slope`` at
    every point from some lag t_start up to the longest lag t_end, and t_end /
    t_start >= ``min_span``. Then D = slope / (2 dim) of an OLS line through the MSD
    points with t_start <= t <= t_end; otherwise ``diffusive`` is False and D None.
    """
    t, s = local_log_slope(lags, msd_values)
    k = len(s)
    while k > 0 and s[k - 1] >= min_slope:
        k -= 1
    slope_end, slope_max = float(s[-1]), float(s.max())
    if k == len(s) or t[-1] / t[k] < min_span:
        return DiffusionFit(False, None, None, None, None, slope_end, slope_max)
    lag, m = np.asarray(lags, dtype=float), np.asarray(msd_values, dtype=float)
    sel = (lag >= t[k]) & (lag <= t[-1])
    if sel.sum() < 3:
        return DiffusionFit(False, None, None, None, None, slope_end, slope_max)
    slope, _, err, _ = linear_fit(lag[sel], m[sel])
    return DiffusionFit(
        True, slope / (2 * dim), err / (2 * dim), float(t[k]), float(t[-1]), slope_end, slope_max
    )


def _origins(n_frames: int, lag: int, max_origins: int | None) -> np.ndarray:
    k = np.arange(n_frames - lag)
    if max_origins is not None and len(k) > max_origins:
        k = np.unique(np.linspace(0, len(k) - 1, max_origins).round().astype(int))
    return k


def _chunks(origins: np.ndarray, per_frame: int, elems: int = 2_000_000):
    size = max(1, elems // max(1, per_frame))
    for s in range(0, len(origins), size):
        yield origins[s : s + size]


def msd_by_class(positions, labels, lags, n_classes: int, max_origins: int | None = None):
    """Squared displacements per Cartesian component, split by a class fixed at the
    time origin (e.g. surface layer vs film interior).

    ``positions`` (n_frames, n_sites, 3) unwrapped; ``labels`` (n_frames, n_sites)
    integer class of each site at each frame (negative: not counted); ``lags`` frame
    counts >= 1. For lag m every origin k (or ``max_origins`` evenly spaced ones)
    contributes |r_i(k+m) - r_i(k)|^2 per component to the class labels[k, i]. Returns
    (sums (n_lags, n_classes, 3), counts (n_lags, n_classes)) so that several
    trajectories (bursts) can be pooled; MSD_component = sums / counts.
    """
    x = np.asarray(positions)
    lab = np.asarray(labels)
    n, n_sites = x.shape[:2]
    sums = np.zeros((len(lags), n_classes, 3))
    counts = np.zeros((len(lags), n_classes))
    for j, m in enumerate(lags):
        for o in _chunks(_origins(n, int(m), max_origins), n_sites * 3):
            d2 = (x[o + m].astype(float) - x[o]) ** 2
            c = lab[o].ravel()
            ok = c >= 0
            for k in range(3):
                sums[j, :, k] += np.bincount(c[ok], d2[..., k].ravel()[ok], minlength=n_classes)
            counts[j] += np.bincount(c[ok], minlength=n_classes)
    return sums, counts


def unit_bonds(x, a, b) -> np.ndarray:
    """Unit vectors from site ``a`` to site ``b`` of positions x (..., n_sites, 3)."""
    v = x[..., b, :].astype(float) - x[..., a, :]
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def p2_by_class(positions, a, b, labels, lags, n_classes: int, max_origins: int | None = None):
    """Bond reorientation <P2(u(0) . u(t))> split by a class fixed at the time origin.

    Bonds run from site ``a[j]`` to ``b[j]`` of ``positions`` (n_frames, n_sites, 3);
    ``labels`` (n_frames, n_bonds). Same origin sampling and return convention as
    :func:`msd_by_class`: (sums (n_lags, n_classes), counts (n_lags, n_classes)).
    """
    x = np.asarray(positions)
    lab = np.asarray(labels)
    n = x.shape[0]
    sums = np.zeros((len(lags), n_classes))
    counts = np.zeros((len(lags), n_classes))
    for j, m in enumerate(lags):
        for o in _chunks(_origins(n, int(m), max_origins), len(a) * 6):
            cos = np.sum(unit_bonds(x[o], a, b) * unit_bonds(x[o + m], a, b), axis=-1)
            p2 = 1.5 * cos**2 - 0.5
            c = lab[o].ravel()
            ok = c >= 0
            sums[j] += np.bincount(c[ok], p2.ravel()[ok], minlength=n_classes)
            counts[j] += np.bincount(c[ok], minlength=n_classes)
    return sums, counts
