"""Uniaxial tensile curves (D54): stress-strain, apparent modulus, Poisson ratio.

Input is the per-axis ``fix ave/time`` output of the ``tensile`` deck
(``tensile_<axis>.txt``): engineering strain e = (L - L0)/L0 along the pulled axis,
the diagonal pressure tensor Pxx Pyy Pzz (atm), the box lengths and T, each averaged
over ``avg_ps``. With the lateral axes barostatted at p_ref (1 atm), the true (Cauchy)
stress along the axis is sigma = -(P_axis - p_ref), tension positive.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from .stats import linear_fit

ATM_MPA = 0.101325  # 1 atm in MPa
AXES = ("x", "y", "z")
FLOW_WINDOW = (0.3, 0.5)  # engineering strain window of the flow stress
SMOOTH_STRAIN = 0.01  # moving-average width (strain) for the peak stress
FITS = ("origin", "steepest")  # E_app window: [0, fit_max], or the steepest fit_max-wide one
STEEPEST_STEP = 0.1  # window start spacing of the steepest search, in units of fit_max

_PRESS = re.compile(r"^c_thermo_press\[(\d)\]$")
_THERMO = {"c_thermo_temp": "temp", "c_thermo_press": "press", "c_thermo_pe": "pe"}


TENSILE_COLUMNS = ("e", "pxx", "pyy", "pzz", "lx", "ly", "lz")


def read_ave_time(
    path: str | Path, required: tuple[str, ...] = TENSILE_COLUMNS
) -> dict[str, np.ndarray]:
    """Columns of a ``fix ave/time`` file by short name, e.g. for a tensile file ``step``,
    ``e``, ``pxx``, ``pyy``, ``pzz``, ``lx``, ``ly``, ``lz``, ``temp``. The names come from
    the file's ``# TimeStep ...`` header line (``v_<prefix>_<name>`` -> ``<name>``,
    ``c_thermo_press[k]`` -> ``pxx``..., ``c_thermo_press`` -> ``press``, ``c_thermo_temp``
    -> ``temp``, ``c_thermo_pe`` -> ``pe``; anything else, e.g. ``f_tip[3]``, as is). A
    partly written last line (a running job) is dropped. Raises ValueError if a column
    in ``required`` (default: the tensile columns) is missing."""
    names, rows = None, []
    for line in Path(path).read_text(errors="replace").splitlines():
        if line.startswith("#"):
            tokens = line[1:].split()
            if tokens and tokens[0] == "TimeStep":
                names = [_short_name(t) for t in tokens]
            continue
        tokens = line.split()
        if names is None or len(tokens) != len(names):
            continue
        try:
            rows.append([float(t) for t in tokens])
        except ValueError:
            continue
    if names is None:
        raise ValueError(f"{path}: no '# TimeStep ...' header (not a fix ave/time file?)")
    data = np.array(rows, dtype=float).reshape(-1, len(names))
    out = {name: data[:, k] for k, name in enumerate(names)}
    missing = [k for k in required if k not in out]
    if missing:
        raise ValueError(f"{path}: missing columns {', '.join(missing)}")
    return out


def _short_name(token: str) -> str:
    if token == "TimeStep":
        return "step"
    if m := _PRESS.match(token):
        return "p" + 2 * AXES[int(m.group(1)) - 1]
    if token in _THERMO:
        return _THERMO[token]
    if token.startswith("v_"):
        return token.rsplit("_", 1)[-1]
    return token


def moving_average(x, y, width: float) -> tuple[np.ndarray, np.ndarray]:
    """Mean of ``y`` over |x - x_i| <= width/2 for every point (x increasing); also a
    mask of the points whose window lies inside the data range."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    cs = np.concatenate([[0.0], np.cumsum(y)])
    lo = np.searchsorted(x, x - width / 2, side="left")
    hi = np.searchsorted(x, x + width / 2, side="right")
    full = (x - width / 2 >= x[0]) & (x + width / 2 <= x[-1])
    return (cs[hi] - cs[lo]) / (hi - lo), full


def _steepest_start(eps, smooth, width: float, e_peak: float) -> float:
    """Start e0 of the ``width``-wide strain window (>= 3 points) with the largest OLS
    slope of the smoothed stress, e0 in steps of STEEPEST_STEP * width from 0 to
    ``e_peak`` - width (0 when no window fits before the peak)."""
    best, e_best = -np.inf, 0.0
    for e0 in np.arange(0.0, max(e_peak - width, 0.0) + 1e-12, STEEPEST_STEP * width):
        sel = (eps >= e0) & (eps <= e0 + width)
        if sel.sum() < 3:
            continue
        slope = linear_fit(eps[sel], smooth[sel])[0]
        if slope > best:
            best, e_best = slope, float(e0)
    return e_best


def _ln_fit(eps, ln_l, sel):
    """slope, intercept, slope error of ln L vs ln(1 + e) over ``sel`` (>= 3 points)."""
    if sel.sum() < 3:
        return None
    return linear_fit(np.log1p(eps[sel]), ln_l[sel])


def analyze_axis(
    data: dict[str, np.ndarray],
    axis: str,
    p_ref_atm: float = 1.0,
    fit_max: float = 0.02,
    fit: str = "origin",
) -> dict:
    """Tensile properties of one axis run (``data`` from :func:`read_ave_time`).

    - true stress sigma = -(P_axis - p_ref) in MPa; engineering stress sigma A/A0 with
      A0 the lateral area at e = 0 (from the fits of ln L_lat);
    - E_app: OLS slope of the true stress vs e over 0 <= e <= fit_max (MPa), or with
      ``fit="steepest"`` over the fit_max-wide window [e0, e0 + fit_max] with the largest
      slope of the smoothed stress, e0 stepped by STEEPEST_STEP * fit_max from 0 to the
      peak strain (``fit_start``: a soft toe before the linear rise, e.g. the UA crystal at
      1e9 /s, is skipped; the max over windows biases E up by ~ its noise);
    - Poisson ratio nu = -d ln L_lat / d ln L_axis (L_axis = L0 (1 + e)), the mean of
      the two lateral axes, from OLS fits over the same window and over the whole run;
    - peak: the maximum of the true stress after a SMOOTH_STRAIN moving average, and
      its strain (``at_end`` when it lies within the last window: no maximum);
    - flow stress: mean true stress over FLOW_WINDOW (None unless the run reaches it).
    Curves (strain, true and engineering stress, smoothed stress, lateral true strains,
    secant nu) are returned for plots.
    """
    if axis not in AXES:
        raise ValueError(f"axis {axis!r}")
    if fit not in FITS:
        raise ValueError(f"fit {fit!r} (one of {', '.join(FITS)})")
    eps = np.asarray(data["e"], dtype=float)
    order = np.argsort(eps, kind="stable")
    eps = eps[order]
    lat = [a for a in AXES if a != axis]
    sigma = -(data["p" + 2 * axis][order] - p_ref_atm) * ATM_MPA
    ln_lat = [np.log(data["l" + a][order]) for a in lat]
    n = len(eps)
    out: dict = {
        "axis": axis,
        "lateral": lat,
        "rows": n,
        "strain_max": float(eps[-1]) if n else 0.0,
    }
    if n < 3:
        out["error"] = f"only {n} rows"
        return out
    smooth, full = moving_average(eps, sigma, SMOOTH_STRAIN)
    pick = np.flatnonzero(full) if full.any() else np.arange(n)
    k = pick[np.argmax(smooth[pick])]
    e0 = _steepest_start(eps, smooth, fit_max, eps[k]) if fit == "steepest" else 0.0
    win = (eps >= e0) & (eps <= e0 + fit_max)
    out["fit"] = fit
    out["fit_start"] = float(e0)
    out["fit_max"] = fit_max
    out["fit_rows"] = int(win.sum())
    if win.sum() >= 3:
        e_fit, b_fit, e_err, _ = linear_fit(eps[win], sigma[win])
        out["E_MPa"], out["E_err_MPa"], out["E_intercept_MPa"] = e_fit, e_err, b_fit
    else:
        out["E_MPa"] = out["E_err_MPa"] = out["E_intercept_MPa"] = None
    nu_fit, nu_run, ln_l0 = [], [], []
    for ln_l in ln_lat:
        f = _ln_fit(eps, ln_l, win)
        r = _ln_fit(eps, ln_l, np.ones(n, bool))
        nu_fit.append(None if f is None else -f[0])
        nu_run.append(-r[0])
        ln_l0.append(f[1] if f is not None else r[1])
    out["nu_fit"] = None if None in nu_fit else float(np.mean(nu_fit))
    out["nu_fit_per_axis"] = nu_fit
    out["nu_run"] = float(np.mean(nu_run))
    out["nu_run_per_axis"] = nu_run
    lat_strain = np.stack([ln_l - l0 for ln_l, l0 in zip(ln_lat, ln_l0, strict=True)])
    sigma_eng = sigma * np.exp(lat_strain.sum(axis=0))  # sigma A / A0
    out["peak_MPa"] = float(smooth[k])
    out["peak_strain"] = float(eps[k])
    out["peak_at_end"] = bool(eps[k] >= eps[-1] - SMOOTH_STRAIN)
    lo, hi = FLOW_WINDOW
    flow = (eps >= lo) & (eps <= hi)
    out["flow_MPa"] = (
        float(sigma[flow].mean()) if flow.any() and eps[-1] >= hi - SMOOTH_STRAIN else None
    )
    out["flow_window"] = list(FLOW_WINDOW)
    if "temp" in data:
        out["temp_mean_K"] = float(np.mean(data["temp"]))
    ln1e = np.log1p(eps)
    with np.errstate(divide="ignore", invalid="ignore"):
        secant = np.where(ln1e > 0, -lat_strain.mean(axis=0) / ln1e, np.nan)
    out["curves"] = {
        "strain": eps,
        "sigma_true": sigma,
        "sigma_eng": sigma_eng,
        "sigma_smooth": smooth,
        "lat_true_strain": lat_strain,
        "nu_secant": secant,
    }
    return out


def mean_sd(values) -> dict | None:
    """{"mean", "sd", "n"} of the non-None values (sd None for one value)."""
    v = np.array([x for x in values if x is not None], dtype=float)
    if not len(v):
        return None
    return {
        "mean": float(v.mean()),
        "sd": float(v.std(ddof=1)) if len(v) > 1 else None,
        "n": len(v),
    }
