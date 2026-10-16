"""FFT time-correlation helper shared by the analysis modules."""

import numpy as np


def autocorr(x: np.ndarray, max_lag: int) -> np.ndarray:
    """Multiple-origin autocorrelation <x(t0) x(t0+t)> along axis 0, t = 0..max_lag.

    Zero-padded FFT (no circular wrap), divided by the number of origins
    (n_frames - t) per lag. Trailing axes are kept (not summed).
    """
    n = x.shape[0]
    nfft = 1 << (2 * n - 1).bit_length()
    f = np.fft.rfft(x, n=nfft, axis=0)
    c = np.fft.irfft(f * np.conj(f), n=nfft, axis=0)[: max_lag + 1]
    counts = (n - np.arange(max_lag + 1)).reshape((-1,) + (1,) * (x.ndim - 1))
    return c / counts


def check_max_lag(n_frames: int, max_lag: int | None) -> int:
    """Default max_lag = n_frames // 2; validate 1 <= max_lag < n_frames."""
    if max_lag is None:
        max_lag = n_frames // 2
    if not 1 <= max_lag < n_frames:
        raise ValueError(f"max_lag must be in [1, {n_frames - 1}]")
    return max_lag
