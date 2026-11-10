"""Puncture test of a free film (D57): force-depth curve, peak, break-through, energy.

Input is the ``fix ave/time`` output of the ``puncture`` deck (``puncture.txt``: the tip
centre z ``zc``, the force on the indenter from its two ``fix indent`` (``f_tip[k]``,
``f_shaft[k]``, kcal/mol/A), T near and far from the axis, the bead z range) and,
frame by frame, the bead positions of ``puncture.dcd``. All lengths here are Angstrom
unless named ``_nm``; forces are converted to nN.

- F = f_tip[3] + f_shaft[3]: the z force on the indenter, positive while the film
  resists the tip moving down (:func:`indenter_force` flips the sign if it is not).
- Depth d = z_top0 - (zc - R): the tip bottom below the far-field film top at t0
  (``FAR_PAD_A`` beyond the indenter radius, :func:`far_surfaces`).
- :func:`analyze_curve`: F_peak (maximum of a ``SMOOTH_NM`` moving average over depth),
  d_peak (the largest raw F within that window), contact (first smoothed F above
  max(``CONTACT_SD`` SD of the settle rows, ``CONTACT_FLOOR`` F_peak)), break by force
  (signal i: smoothed F below ``BREAK_FRAC`` F_peak after the peak, sustained over
  ``BREAK_SUSTAIN_NM``), the work W = integral F dd from contact to d_peak and to d_break.
- :func:`break_through`: signal iii, no material ahead of the tip (at most ``AHEAD_MAX``
  beads with r < R/2 within ``AHEAD_A`` below the tip for ``AHEAD_FRAMES`` frames); the
  break-through depth needs signals i and iii (the later of the two).
"""

from __future__ import annotations

import numpy as np

from sepsim.analysis import hole as H
from sepsim.analysis.tensile import moving_average
from sepsim.analysis.units import ANGSTROM_M, AVOGADRO, KCAL_J

KCAL_MOL_A_NN = KCAL_J / AVOGADRO / ANGSTROM_M * 1e9  # 1 kcal/mol/A = 0.06948 nN
KCAL_MOL_AJ = KCAL_J / AVOGADRO * 1e18  # 1 kcal/mol = 0.006948 aJ (nN nm = aJ)
COLUMNS = ("zc", "f_tip[3]", "f_shaft[3]")  # required in puncture.txt
SMOOTH_NM = 0.5
CONTACT_SD = 3.0
CONTACT_FLOOR = 0.01  # fraction of F_peak: the contact threshold when the settle F is ~0
BREAK_FRAC = 0.5
BREAK_SUSTAIN_NM = 0.5
AHEAD_A = 10.0
AHEAD_MAX = 2
AHEAD_FRAMES = 3
FAR_PAD_A = 20.0  # far field: r > R + 2 nm
INSIDE_FLAG = 1e-3  # beads inside the indenter: flag above this fraction
STRETCH_FLAG = 0.20  # bond stretch: flag 20 points above the first Stage 2 frame (thermal baseline)
Z_PAD_A = 20.0  # z padding of the (non-periodic) film profile


def indenter_force(data: dict[str, np.ndarray]) -> tuple[np.ndarray, bool]:
    """(F in nN, flipped): the z force on the indenter (tip + shaft), made positive for a
    film resisting the indentation (``flipped`` when its largest excursion is negative)."""
    f = (np.asarray(data["f_tip[3]"]) + np.asarray(data["f_shaft[3]"])) * KCAL_MOL_A_NN
    flipped = bool(len(f) and -f.min() > f.max())
    return (-f if flipped else f), flipped


def depth_nm(zc, r_a: float, z_top0: float) -> np.ndarray:
    """Depth of the tip bottom below the far-field top surface at t0, nm."""
    return (z_top0 - (np.asarray(zc, dtype=float) - r_a)) / 10.0


def work(d, f, d0: float, d1: float) -> float | None:
    """Trapezoid integral of f over d from d0 to d1 (interpolated ends); None if empty."""
    d, f = np.asarray(d, dtype=float), np.asarray(f, dtype=float)
    if d1 is None or d0 is None or d1 <= d0 or len(d) < 2:
        return None
    inner = (d > d0) & (d < d1)
    x = np.concatenate([[d0], d[inner], [d1]])
    y = np.interp(x, d, f)
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def analyze_curve(d, f, settle_f=(), smooth_nm: float = SMOOTH_NM) -> dict:
    """Force-depth curve of the indentation rows (``d`` nm increasing, ``f`` nN):
    smoothed F, peak, contact, break by force (signal i) and the work (aJ = nN nm)."""
    d, f = np.asarray(d, dtype=float), np.asarray(f, dtype=float)
    out: dict = {"rows": len(d)}
    if len(d) < 3:
        out["error"] = f"only {len(d)} rows"
        return out
    smooth, full = moving_average(d, f, smooth_nm)
    pick = np.flatnonzero(full) if full.any() else np.arange(len(d))
    k = int(pick[np.argmax(smooth[pick])])
    f_peak = float(smooth[k])
    win = np.flatnonzero(np.abs(d - d[k]) <= 0.5 * smooth_nm)
    k_raw = int(win[np.argmax(f[win])])
    settle = np.asarray(settle_f, dtype=float)
    noise = float(settle.std(ddof=1)) if len(settle) > 1 else 0.0
    thr = max(CONTACT_SD * noise, CONTACT_FLOOR * f_peak)
    above = np.flatnonzero(smooth > thr)
    d_contact = float(d[above[0]]) if len(above) else None
    d_force = None
    low = smooth < BREAK_FRAC * f_peak
    for j in range(k + 1, len(d)):
        if not low[j] or d[-1] < d[j] + BREAK_SUSTAIN_NM:
            continue
        span = (d >= d[j]) & (d <= d[j] + BREAK_SUSTAIN_NM)
        if low[span].all():
            d_force = float(d[j])
            break
    out.update(
        f_peak_nN=f_peak,
        d_peak_nm=float(d[k_raw]),
        d_peak_smooth_nm=float(d[k]),
        peak_at_end=bool(d[k] >= d[-1] - smooth_nm),
        settle_sd_nN=noise,
        contact_threshold_nN=thr,
        d_contact_nm=d_contact,
        d_break_force_nm=d_force,
        w_peak_aJ=work(d, f, d_contact, float(d[k_raw])),
        d_max_nm=float(d[-1]),
        curves={"depth_nm": d, "force_nN": f, "force_smooth_nN": smooth},
    )
    return out


def break_through(curve: dict, frame_d, ahead) -> dict:
    """Break-through from signal i (``curve['d_break_force_nm']``) and signal iii: the
    first of ``AHEAD_FRAMES`` consecutive frames after contact (depth > max(contact, 0))
    with at most ``AHEAD_MAX`` beads ahead of the tip (``ahead`` per frame at depth
    ``frame_d`` nm). d_break is the later of the two (None unless both are seen); the
    work to it is added to ``curve``."""
    frame_d, ahead = np.asarray(frame_d, dtype=float), np.asarray(ahead)
    start = max(curve.get("d_contact_nm") or 0.0, 0.0)
    d_clear, run = None, 0
    for k in range(len(frame_d)):
        ok = frame_d[k] > start and ahead[k] <= AHEAD_MAX
        run = run + 1 if ok else 0
        if run >= AHEAD_FRAMES:
            d_clear = float(frame_d[k - AHEAD_FRAMES + 1])
            break
    d_force = curve.get("d_break_force_nm")
    d_break = max(d_force, d_clear) if d_force is not None and d_clear is not None else None
    c = curve.get("curves") or {}
    w = None
    if d_break is not None and c:
        w = work(c["depth_nm"], c["force_nN"], curve.get("d_contact_nm"), d_break)
    return {"d_break_clear_nm": d_clear, "d_break_nm": d_break, "w_break_aJ": w}


def axis_r(pos: np.ndarray, axis, lengths) -> np.ndarray:
    """Distance of each bead from the indenter axis (minimum image in x, y)."""
    rel = H.wrap_about(pos, axis, lengths)
    return np.hypot(rel[:, 0], rel[:, 1])


def ahead_count(pos: np.ndarray, axis, lengths, zc: float, r_a: float) -> int:
    """Beads with r < R/2 and z within ``AHEAD_A`` below the tip bottom (zc - R)."""
    r = axis_r(pos, axis, lengths)
    tip = zc - r_a
    z = pos[:, 2]
    return int(((r < 0.5 * r_a) & (z >= tip - AHEAD_A) & (z <= tip)).sum())


def inside_count(pos: np.ndarray, axis, lengths, zc: float, r_a: float) -> int:
    """Beads inside the indenter volume: the tip sphere or the shaft (r < R, z > zc)."""
    r = axis_r(pos, axis, lengths)
    dz = pos[:, 2] - zc
    return int(((r < r_a) & ((dz > 0) | (r * r + dz * dz < r_a * r_a))).sum())


def far_surfaces(pos: np.ndarray, axis, lengths, r_a: float) -> tuple[float, float]:
    """(bottom, top) of the far-field film (beads with r > R + ``FAR_PAD_A``): the 50%
    crossings of its z profile, z taken as non-periodic (padded by ``Z_PAD_A``)."""
    far = axis_r(pos, axis, lengths) > r_a + FAR_PAD_A
    z = pos[far, 2] if far.sum() > 10 else pos[:, 2]
    z_lo = float(z.min()) - Z_PAD_A
    return H.film_bounds(z, z_lo, float(np.ptp(z)) + 2 * Z_PAD_A)


def max_bond_stretch(pos: np.ndarray, bonds: np.ndarray, lengths, l0: float) -> float:
    """Largest bond length / ``l0`` - 1 (``bonds`` as index pairs; minimum image in x, y)."""
    if not len(bonds):
        return 0.0
    v = pos[bonds[:, 1]] - pos[bonds[:, 0]]
    lxy = np.asarray(lengths, dtype=float)[:2]
    v[:, :2] -= lxy * np.round(v[:, :2] / lxy)
    return float(np.sqrt((v * v).sum(axis=1)).max() / l0 - 1.0)


def image_rows(zspan, lz: float, cutoff: float, boundary: str) -> np.ndarray:
    """Rows where the film could interact with its z image: z periodic and the bead z
    span + the LJ cutoff exceeds Lz. Never for a non-periodic z (``p p m``)."""
    zspan = np.asarray(zspan, dtype=float)
    if boundary.split()[2] != "p":
        return np.zeros(len(zspan), bool)
    return zspan + cutoff > lz


def free_hole_radius(r_eff, r_a: float) -> np.ndarray:
    """Radius of the hole area not taken by the indenter column: sqrt(R_eff^2 - R^2)."""
    r = np.asarray(r_eff, dtype=float)
    return np.sqrt(np.maximum(r * r - r_a * r_a, 0.0))
