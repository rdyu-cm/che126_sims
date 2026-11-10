"""Cavitation under triaxial tension (D58): hydrostatic stress and voids.

Input is the ``fix ave/time`` output of the ``cavitation`` deck (``cavitation.txt``:
engineering strain e per axis, volume strain eV = V/V0 - 1, pressure and its diagonal in
atm, box lengths, T, PE, each averaged over ``avg_ps``) and the frames of
``cavitation.dcd``. Lengths are Angstrom.

- sigma_h = -(P - p_ref) in MPa, tension positive; smoothed over ``SMOOTH_PS``;
  sigma_cav = its maximum, eV_cav the volume strain there, the drop after it, the
  plateau = mean sigma_h over eV >= eV_cav + ``PLATEAU_OFFSET``, K_app = OLS slope of
  sigma_h vs eV over eV <= ``K_FIT_MAX`` (:func:`analyze_curve`).
- Voids (:func:`void_stats`): beads wrapped into the box, a ``VOXEL_A`` grid; a voxel
  centre farther than the probe radius from every bead centre is empty
  (``scipy.spatial.cKDTree`` with periodic ``boxsize``); the void space is the empty
  centres dilated by the probe radius (the space a probe sphere sweeps), split into
  connected clusters with periodic merging; phi_v = void fraction, the largest void
  volume V and R_void = (3V / 4 pi)^(1/3), the number of voids above ``VOID_MIN_A3``.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from sepsim.analysis.stats import linear_fit
from sepsim.analysis.tensile import ATM_MPA, moving_average

COLUMNS = ("e", "ev", "press")  # required in cavitation.txt
SMOOTH_PS = 10.0
PLATEAU_OFFSET = 0.2  # plateau from eV_cav + 0.2 to the end
K_FIT_MAX = 0.02
VOXEL_A = 2.0
PROBE_A = 4.0
VOID_MIN_A3 = 1000.0  # 1 nm^3: counted voids
FIRST_VOID_A3 = 4.0 / 3.0 * math.pi * 10.0**3  # R = 1 nm (4.19 nm^3)
FIRST_VOID_PHI = 0.005  # or phi_v - phi_v(0) above 0.5%


def hydrostatic_stress(press_atm, p_ref_atm: float = 1.0) -> np.ndarray:
    """sigma_h = -(P - p_ref) in MPa (tension positive)."""
    return -(np.asarray(press_atm, dtype=float) - p_ref_atm) * ATM_MPA


def analyze_curve(t_ps, ev, sigma, smooth_ps: float = SMOOTH_PS) -> dict:
    """Cavitation stress and strain from sigma_h(eV) rows at times ``t_ps``."""
    t = np.asarray(t_ps, dtype=float)
    ev, sigma = np.asarray(ev, dtype=float), np.asarray(sigma, dtype=float)
    out: dict = {"rows": len(t), "ev_max": float(ev[-1]) if len(ev) else 0.0}
    if len(t) < 3:
        out["error"] = f"only {len(t)} rows"
        return out
    smooth, full = moving_average(t, sigma, smooth_ps)
    pick = np.flatnonzero(full) if full.any() else np.arange(len(t))
    k = int(pick[np.argmax(smooth[pick])])
    s_cav = float(smooth[k])
    plateau = ev >= ev[k] + PLATEAU_OFFSET
    fit = (ev >= 0) & (ev <= K_FIT_MAX)
    k_app = k_err = None
    if fit.sum() >= 3:
        k_app, _, k_err, _ = linear_fit(ev[fit], sigma[fit])
    out.update(
        sigma_cav_MPa=s_cav,
        ev_cav=float(ev[k]),
        t_cav_ps=float(t[k]),
        cav_at_end=bool(t[k] >= t[-1] - smooth_ps),
        drop_MPa=float(s_cav - smooth[k:].min()),
        plateau_MPa=float(sigma[plateau].mean()) if plateau.any() else None,
        K_app_MPa=None if k_app is None else float(k_app),
        K_app_err_MPa=None if k_err is None else float(k_err),
        curves={"t_ps": t, "ev": ev, "sigma_h": sigma, "sigma_smooth": smooth},
    )
    return out


def _grid_shape(lengths, spacing: float) -> np.ndarray:
    return np.maximum(4, np.round(np.asarray(lengths, dtype=float) / spacing)).astype(int)


def empty_voxels(pos, lengths, probe: float = PROBE_A, spacing: float = VOXEL_A) -> np.ndarray:
    """Boolean grid (about ``spacing``) of voxel centres farther than ``probe`` from every
    bead centre (periodic box ``lengths``, origin at the box corner)."""
    lengths = np.asarray(lengths, dtype=float)
    shape = _grid_shape(lengths, spacing)
    wrapped = np.mod(np.asarray(pos, dtype=float), lengths)
    wrapped[wrapped >= lengths] = 0.0  # mod can round up to L
    tree = cKDTree(wrapped, boxsize=lengths)
    axes = [(np.arange(n) + 0.5) * (L / n) for n, L in zip(shape, lengths, strict=True)]
    centres = np.stack(np.meshgrid(*axes, indexing="ij"), axis=-1).reshape(-1, 3)
    dist, _ = tree.query(centres, k=1, distance_upper_bound=probe)
    return np.isinf(dist).reshape(shape)


def _ball(lengths, shape, radius: float) -> np.ndarray:
    """Structuring element: voxel offsets within ``radius`` (per-axis voxel sizes)."""
    step = np.asarray(lengths, dtype=float) / shape
    r = np.ceil(radius / step).astype(int)
    g = np.meshgrid(
        *[np.arange(-n, n + 1) * s for n, s in zip(r, step, strict=True)], indexing="ij"
    )
    return (g[0] ** 2 + g[1] ** 2 + g[2] ** 2) <= radius**2 + 1e-9


def dilate_periodic(mask: np.ndarray, ball: np.ndarray) -> np.ndarray:
    """Binary dilation of ``mask`` by ``ball`` with periodic boundaries."""
    pad = [(n // 2, n // 2) for n in ball.shape]
    big = np.pad(mask, pad, mode="wrap")
    out = ndimage.binary_dilation(big, structure=ball)
    sl = tuple(slice(p, p + n) for (p, _), n in zip(pad, mask.shape, strict=True))
    return out[sl]


def periodic_label(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """Connected clusters (face neighbours) of ``mask`` with the box faces joined:
    (labels 1..n, 0 outside, n)."""
    labels, n = ndimage.label(mask)
    if n == 0:
        return labels, 0
    a, b = [], []
    for ax in range(3):
        lo = np.take(labels, 0, axis=ax)
        hi = np.take(labels, -1, axis=ax)
        both = (lo > 0) & (hi > 0)
        a.append(lo[both])
        b.append(hi[both])
    a, b = np.concatenate(a), np.concatenate(b)
    graph = coo_matrix((np.ones(len(a)), (a, b)), shape=(n + 1, n + 1))
    _, comp = connected_components(graph, directed=False)
    # renumber the components of labels 1..n as 1..m
    _, new = np.unique(comp[1:], return_inverse=True)
    lut = np.concatenate([[0], new + 1])
    return lut[labels], int(new.max() + 1)


def void_stats(pos, lengths, probe: float = PROBE_A, spacing: float = VOXEL_A) -> dict:
    """Void fraction, cluster volumes, the largest void and its equivalent radius."""
    lengths = np.asarray(lengths, dtype=float)
    empty = empty_voxels(pos, lengths, probe, spacing)
    void = dilate_periodic(empty, _ball(lengths, empty.shape, probe)) if empty.any() else empty
    labels, n = periodic_label(void)
    voxel = float(np.prod(lengths / empty.shape))
    vols = np.bincount(labels.ravel())[1:] * voxel if n else np.zeros(0)
    largest = float(vols.max()) if len(vols) else 0.0
    return {
        "phi_v": float(void.mean()),
        "n_voids": int((vols > VOID_MIN_A3).sum()),
        "largest_A3": largest,
        "r_void_A": (3.0 * largest / (4.0 * math.pi)) ** (1.0 / 3.0),
        "volume_A3": float(np.prod(lengths)),
    }


def first_void(ev, phi_rel, largest_A3) -> float | None:
    """Volume strain of the first frame with a void above ``FIRST_VOID_A3`` or a void
    fraction above its eV = 0 baseline by more than ``FIRST_VOID_PHI``."""
    for e, phi, v in zip(ev, phi_rel, largest_A3, strict=True):
        if v > FIRST_VOID_A3 or phi > FIRST_VOID_PHI:
            return float(e)
    return None
