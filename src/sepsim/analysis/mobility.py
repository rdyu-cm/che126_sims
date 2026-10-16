"""Chain mobility: mean-squared displacement and bond-vector reorientation."""

import numpy as np

from ._corr import autocorr, check_max_lag


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
