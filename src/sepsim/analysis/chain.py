"""Chain equilibration: mean-square internal distances (MSID) and characteristic ratio.

Decision D24 (Auhl, Everaers, Grest, Kremer & Plimpton, J. Chem. Phys. 119, 12718
(2003), doi:10.1063/1.1628670): <R^2(n)>/n vs n, with R(n) the distance between
backbone sites i and i+n of the same chain, averaged over all i and chains, from
unwrapped coordinates. The characteristic ratio is C_n = <R^2(n)> / (n l^2).

Pass criterion (``msid_check``): (i) the C_n plateau (mean over carbon-equivalent
separations >= n_min) lies within +-10% of the caller's experimental C_inf range;
(ii) no drift: the plateau of the first and second halves of the frames differ by
at most 2 combined SEMs (statistical-inefficiency SEM of the per-frame plateau).

Units: positions in Angstrom; n in backbone sites (``carbons_per_site`` converts to
carbon equivalents, 3 for SDK CG PE beads).
"""

from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

import numpy as np
import yaml

from sepsim.build.datafile import read_data_file
from sepsim.build.topology import build_chain

from .stats import timeseries_mean

CARBONS_PER_SITE = {"aa": 1, "ua": 1, "cg": 3}  # backbone carbons per backbone site
# D42: melt C_inf at the 500 K hold from SANS (Fetters, Lohse & Colby, Physical Properties
# of Polymers Handbook 2007, ch. 25, doi:10.1007/978-0-387-69002-5_25, Table 25.1): PE 7.38
# at 413 K scaled by d ln<R^2>/dT = -1.2e-3 /K (Table 25.7) to 6.7; iPP 6.15 at 463 K,
# temperature-independent.
MELT_C_INF_500K = {"pe": (6.7, 6.7), "ipp": (6.15, 6.15)}


@dataclass
class MSIDResult:
    """Outcome of :func:`msid_check`."""

    n_carbons: np.ndarray  # carbon-equivalent separations n * carbons_per_site
    c_n: np.ndarray  # frame-averaged C_n at each separation
    plateau: float  # mean C_n over n_carbons >= n_min (all frames)
    reference: tuple[float, float]  # experimental C_inf range
    within_reference: bool  # plateau in [0.9 lo, 1.1 hi]
    first_half: float | None  # plateau mean over the first half of the frames
    second_half: float | None
    delta: float | None  # second_half - first_half
    delta_sem: float | None  # sqrt(SEM_1^2 + SEM_2^2)
    drift: bool | None  # |delta| > 2 delta_sem; None if < 3 frames per half
    passed: bool  # within_reference and drift is False


def _frames(positions) -> np.ndarray:
    x = np.asarray(positions, dtype=float)
    return x[None] if x.ndim == 2 else x


def internal_distances(positions, chains, per_frame: bool = False):
    """Mean-square internal distance <R^2(n)> over all site pairs (i, i+n) of each chain.

    ``positions``: (n_frames, n_atoms, 3) or (n_atoms, 3), unwrapped (or with
    every chain made whole). ``chains``: ordered backbone index arrays (may differ
    in length). Returns (n, r2) with n = 1 .. L_max - 1; r2 is averaged over frames,
    i and chains (each pair weighted equally), or (n_frames, len(n)) if ``per_frame``.
    """
    x = _frames(positions)
    chains = [np.asarray(c, dtype=np.int64) for c in chains]
    n_max = max(len(c) for c in chains) - 1
    total = np.zeros((x.shape[0], n_max))
    count = np.zeros(n_max)
    for length in sorted({len(c) for c in chains}):
        idx = np.array([c for c in chains if len(c) == length])
        r = x[:, idx]  # (frames, chains, length, 3)
        for n in range(1, length):
            d = r[:, :, n:] - r[:, :, :-n]
            total[:, n - 1] += np.einsum("fcik,fcik->f", d, d)
            count[n - 1] += idx.shape[0] * (length - n)
    r2 = total / count
    return np.arange(1, n_max + 1), r2 if per_frame else r2.mean(axis=0)


def characteristic_ratio(
    positions, chains, carbons_per_site: int = 1, bond_length: float | None = None, per_frame=False
):
    """C_n = <R^2(n)> / (n_b l^2) for each backbone separation n.

    Without ``bond_length``: l = mean distance between consecutive backbone sites
    (per frame) and n_b = n (site bonds). With ``bond_length`` (e.g. 1.54 A for a
    CG model compared to an atomistic C_inf): l = bond_length and n_b = n *
    carbons_per_site. Returns (n * carbons_per_site, C_n), C_n per frame if
    ``per_frame``.
    """
    x = _frames(positions)
    n, r2 = internal_distances(x, chains, per_frame=True)
    if bond_length is None:
        bonds = np.concatenate(
            [np.linalg.norm(np.diff(x[:, np.asarray(c)], axis=1), axis=2) for c in chains], axis=1
        )
        c_n = r2 / (n * bonds.mean(axis=1)[:, None] ** 2)
    else:
        c_n = r2 / (n * carbons_per_site * bond_length**2)
    return n * carbons_per_site, c_n if per_frame else c_n.mean(axis=0)


def drift_check(series, n_sigma: float = 2.0):
    """Compare halves of a per-frame series: (mean_1, mean_2, delta, delta_sem, drift).

    SEMs from :func:`sepsim.analysis.stats.timeseries_mean` (statistical
    inefficiency); drift if |mean_2 - mean_1| > n_sigma * sqrt(SEM_1^2 + SEM_2^2).
    """
    s = np.asarray(series, dtype=float)
    half = len(s) // 2
    a, b = timeseries_mean(s[:half]), timeseries_mean(s[half : 2 * half])
    delta, sem = b.mean - a.mean, float(np.hypot(a.sem, b.sem))
    return a.mean, b.mean, delta, sem, bool(abs(delta) > n_sigma * sem)


def msid_check(
    positions,
    chains,
    reference: tuple[float, float],
    n_min: int = 100,
    carbons_per_site: int = 1,
    bond_length: float | None = None,
    tolerance: float = 0.10,
) -> MSIDResult:
    """D24 chain-equilibration check against an experimental C_inf range.

    ``reference`` = (lo, hi) C_inf (e.g. ``MELT_C_INF_500K``); ``n_min`` in
    carbon equivalents. Arguments as in :func:`characteristic_ratio`. The drift
    test needs >= 3 frames per half; with fewer, ``drift`` is None and ``passed``
    is False.
    """
    nc, c_frames = characteristic_ratio(
        positions, chains, carbons_per_site, bond_length, per_frame=True
    )
    sel = nc >= n_min
    if not sel.any():
        raise ValueError(f"no separation >= n_min = {n_min} carbons (max {nc[-1]})")
    plateau_t = c_frames[:, sel].mean(axis=1)
    plateau = float(plateau_t.mean())
    lo, hi = reference
    within = bool((1 - tolerance) * lo <= plateau <= (1 + tolerance) * hi)
    first = second = delta = sem = drift = None
    if len(plateau_t) >= 6:
        first, second, delta, sem, drift = drift_check(plateau_t)
    return MSIDResult(
        n_carbons=nc,
        c_n=c_frames.mean(axis=0),
        plateau=plateau,
        reference=(float(lo), float(hi)),
        within_reference=within,
        first_half=first,
        second_half=second,
        delta=delta,
        delta_sem=sem,
        drift=drift,
        passed=within and drift is False,
    )


def backbone_chains(data_file, manifest) -> list[np.ndarray]:
    """Ordered backbone indices of every chain, as 0-based rows of the id-sorted atoms.

    The indices address ``read_data_file(data_file).unwrapped()`` (and any
    trajectory sorted by atom id). ``manifest`` is a manifest.yaml path or dict.
    Each molecule's atoms, sorted by id, are matched to the template chain from
    ``build_chain(polymer, resolution, n_carbons)`` (the builders write atoms in
    template order): atom types are checked against the manifest type ids and
    every backbone step against the data-file bonds. PE: all carbons; iPP:
    backbone carbons only (head CH3 to tail CH3, pendant methyls and H excluded);
    CG: all beads.
    """
    man = manifest if isinstance(manifest, dict) else yaml.safe_load(Path(manifest).read_text())
    mol = build_chain(man["polymer"], man["resolution"], int(man["n_carbons"]))
    df = read_data_file(data_file)
    atoms = df.sorted_atoms()
    type_ids = man["type_ids"]["atom"]
    template_types = np.array([type_ids[t] for t in mol.types])
    row = {int(a): k for k, a in enumerate(atoms[:, 0])}
    bond_set = {(row[int(a)], row[int(b)]) for a, b in df.topology("Bonds")[:, 2:4]}
    mol_ids = atoms[:, 1].astype(np.int64)
    chains = []
    for m in np.unique(mol_ids):
        rows = np.flatnonzero(mol_ids == m)
        if len(rows) != mol.n_atoms or np.any(atoms[rows, 2] != template_types):
            raise ValueError(f"molecule {m} does not match the {man['id']} chain template")
        bb = rows[np.asarray(mol.backbone)]
        for a, b in pairwise(bb):
            if (a, b) not in bond_set and (b, a) not in bond_set:
                raise ValueError(f"molecule {m}: backbone rows {a}, {b} are not bonded")
        chains.append(bb)
    return chains
