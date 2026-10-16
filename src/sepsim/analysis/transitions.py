"""Melting point from a heating ramp (decision D26)."""

from dataclasses import dataclass

import numpy as np


@dataclass
class MeltingResult:
    """Melting temperature estimates (K) from one heating ramp."""

    Tm: float  # T where the crystalline fraction first falls to half its initial value; NaN if not
    initial_fraction: float  # mean crystalline fraction of the first k points
    T_max_dVdT: float  # T of the largest dV/dT (NaN if V not given)
    T_max_dHdT: float  # T of the largest dH/dT (NaN if H not given)
    consistent: bool  # all available estimates agree with Tm within the tolerance
    reason: str | None  # why Tm is NaN or the estimates are inconsistent; None if fine


def _t_max_slope(T: np.ndarray, y) -> float:
    """T at the largest forward-difference slope, placed at the interval midpoint."""
    if y is None:
        return float("nan")
    y = np.asarray(y, dtype=float)
    if y.shape != T.shape:
        raise ValueError("V/H must have the same length as T")
    slope = np.diff(y) / np.diff(T)
    k = int(np.argmax(slope))
    return float(0.5 * (T[k] + T[k + 1]))


def melting_point(
    T,
    crystalline_fraction,
    V=None,
    H=None,
    *,
    k: int = 3,
    tolerance_K: float = 15.0,
) -> MeltingResult:
    """Tm from crystalline fraction vs temperature, cross-checked with V(T) and H(T).

    ``T`` (K) must be strictly increasing (heating ramp, one value per
    sampled state). Primary estimate: initial fraction X0 = mean of the first
    ``k`` points; Tm is the first temperature at which the fraction reaches
    X0/2, by linear interpolation between the bracketing points (the first
    point with X <= X0/2 and the one before it).

    Cross-checks (if ``V`` volume or ``H`` enthalpy are given, any units):
    temperature of maximum dV/dT and dH/dT, from forward finite differences
    (y_{n+1} - y_n)/(T_{n+1} - T_n) assigned to the interval midpoint, so the
    resolution is the T grid spacing. ``consistent`` is False, with a
    ``reason``, if any available cross-check differs from Tm by more than
    ``tolerance_K``. If the fraction never halves (or X0 <= 0) Tm is NaN and
    ``reason`` says why.
    """
    T = np.asarray(T, dtype=float)
    x = np.asarray(crystalline_fraction, dtype=float)
    if T.ndim != 1 or x.shape != T.shape:
        raise ValueError("T and crystalline_fraction must be 1-D arrays of equal length")
    if len(T) < 2 or np.any(np.diff(T) <= 0):
        raise ValueError("T must be strictly increasing with at least 2 points")
    if not 1 <= k <= len(T):
        raise ValueError("k must be between 1 and len(T)")

    x0 = float(x[:k].mean())
    t_v = _t_max_slope(T, V)
    t_h = _t_max_slope(T, H)

    tm, reason = float("nan"), None
    half = 0.5 * x0
    if x0 <= 0.0:
        reason = "initial crystalline fraction is not positive"
    else:
        below = np.flatnonzero(x[1:] <= half) + 1
        if len(below) == 0:
            reason = f"crystalline fraction never falls to half its initial value ({x0:.3g})"
        else:
            n = int(below[0])
            if x[n - 1] <= half:  # only possible for n == 1 with a noisy first point
                tm = float(T[0])
            else:
                w = (x[n - 1] - half) / (x[n - 1] - x[n])
                tm = float(T[n - 1] + w * (T[n] - T[n - 1]))

    consistent = reason is None
    if consistent:
        bad = [
            f"{name} = {t:.1f} K"
            for name, t in (("T(max dV/dT)", t_v), ("T(max dH/dT)", t_h))
            if not np.isnan(t) and abs(t - tm) > tolerance_K
        ]
        if bad:
            consistent = False
            reason = f"{', '.join(bad)} differ from Tm = {tm:.1f} K by > {tolerance_K} K"
    return MeltingResult(
        Tm=tm,
        initial_fraction=x0,
        T_max_dVdT=t_v,
        T_max_dHdT=t_h,
        consistent=consistent,
        reason=reason,
    )
