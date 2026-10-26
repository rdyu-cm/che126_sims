"""Test-only helpers for the phase 2 builders (moved out of the library)."""

import math

import numpy as np

from sepsim.build import growth as G
from sepsim.build.topology import typed_chain

ANGLE = {0: 180.0, 1: 60.0, 2: -60.0}  # torsion state -> dihedral (degrees)


def expected_counts(polymer: str, resolution: str, n: int) -> dict[str, int]:
    """Closed-form per-chain counts (atoms, bonds, angles, dihedrals), no building.

    AA (every carbon sp3 with 4 neighbors): atoms 3n+2, bonds 3n+1, angles 6n, dihedrals
    9(n-1). UA PE: n, n-1, n-2, n-3. UA iPP (m = n/3 - 1 methines, each with an explicit H):
    atoms n+m, bonds n+m-1, angles (4n/3 - 3) carbon-only + 3m H-CH-C = 7n/3 - 6, dihedrals
    2 per CH-CH2 backbone bond (2m - 1 of them) + 1 for the tail CH2-CH2 = 4n/3 - 5.
    CG PE (b = n/3 beads): b, b-1, b-2, 0.
    """
    if resolution == "aa":
        return {"atoms": 3 * n + 2, "bonds": 3 * n + 1, "angles": 6 * n, "dihedrals": 9 * (n - 1)}
    if resolution == "cg":
        b = n // 3
        return {"atoms": b, "bonds": b - 1, "angles": b - 2, "dihedrals": 0}
    if polymer == "pe":
        return {"atoms": n, "bonds": n - 1, "angles": n - 2, "dihedrals": n - 3}
    m = n // 3 - 1
    return {
        "atoms": n + m,
        "bonds": n + m - 1,
        "angles": 7 * n // 3 - 6,
        "dihedrals": 4 * n // 3 - 5,
    }


def ris_stationary(params: G.GrowthParams) -> dict[str, float]:
    """Stationary (t, g+, g-) fractions of the RIS Markov chain with the pentane rule."""
    p = np.array([params.p_trans, params.p_gauche, params.p_gauche])
    T = np.tile(p, (3, 1))
    T[1, 2] = T[2, 1] = 0.0
    T /= T.sum(axis=1, keepdims=True)
    w, v = np.linalg.eig(T.T)
    pi = np.real(v[:, np.argmin(np.abs(w - 1))])
    pi /= pi.sum()
    return {"t": float(pi[0]), "g+": float(pi[1]), "g-": float(pi[2])}


class _FixedGrower(G._Grower):
    """Grower whose backbone torsions are prescribed (no sampling, no jitter)."""

    def __init__(self, mol, ff, phis):
        super().__init__(mol, ff, 1, 1000.0, G.GrowthParams(), np.random.default_rng(0))
        self.phis = [float(x) for x in phis]

    def _backbone_torsion(self, k, tors):
        return None, self.phis[k]


def build_fixed_conformation(mol, ff, phis) -> np.ndarray:
    """One chain with torsion ``phis[k]`` set at growth step k >= 3; no overlap checks."""
    grower = _FixedGrower(mol, ff, phis)
    bb_pos: dict[int, np.ndarray] = {}
    for k in range(len(mol.backbone)):
        new, _ = grower._propose(k, bb_pos, [])
        for loc, x in new.items():
            grower.pos[loc] = x
            bb_pos[loc] = x
    return grower.pos


def methyl_clearance(mol, pos: np.ndarray) -> float:
    """Minimum distance from any methyl carbon to a heavy atom more than 3 bonds away."""
    is_h = np.array(mol.is_hydrogen())
    excl = G.exclusion_matrix(mol)
    nbr = mol.neighbors()
    methyls = [
        i for i in range(mol.n_atoms) if not is_h[i] and sum(not is_h[j] for j in nbr[i]) == 1
    ]
    best = math.inf
    for i in methyls:
        mask = ~is_h & ~excl[i]
        if mask.any():
            best = min(best, float(np.linalg.norm(pos[mask] - pos[i], axis=1).min()))
    return best


def derive_ipp_dyad_states(resolution: str = "ua", n_carbons: int = 30) -> tuple[tuple, tuple]:
    """(t, g) and (g, t) dyad pair states compatible with CHIRAL_SIGN: larger methyl clearance."""
    mol, ff = typed_chain("ipp", resolution, n_carbons)
    roles = G.ipp_dyad_roles(mol)
    out = []
    for pattern in ("tg", "gt"):
        best = None
        for g in (1, 2):
            pair = (0, g) if pattern == "tg" else (g, 0)
            phis = [ANGLE[pair[r - 1]] if r else 180.0 for r in roles]
            clear = methyl_clearance(mol, build_fixed_conformation(mol, ff, phis))
            if best is None or clear > best[0]:
                best = (clear, pair)
        out.append(best[1])
    return tuple(out[0]), tuple(out[1])


def reversal_conformation(res, n_carbons=30, at=4):
    """iPP chain in (t, g+) dyads, reversing to (g-, t) at dyad number ``at``."""
    mol, ff = typed_chain("ipp", res, n_carbons)
    roles = G.ipp_dyad_roles(mol)
    k_rev = [k for k, r in enumerate(roles) if r == 1][at]
    phis = [
        ANGLE[(G.IPP_DYAD_TG if k < k_rev else G.IPP_DYAD_GT)[r - 1]] if r else 180.0
        for k, r in enumerate(roles)
    ]
    return mol, ff, k_rev, build_fixed_conformation(mol, ff, phis)


# Synthetic D48 bulk densities (cooling branch incl. the 500 K hold, heating sweep) for
# tiny test pores built from unrelaxed 0.3 g/cm^3 boxes.
SYN_BULK = {
    "t_source_k": 500.0,
    "rho_source_g_cm3": 0.30,
    "cooling": [[298.15, 0.336], [400.0, 0.318], [500.0, 0.30]],
    "heating": [[298.15, 0.335], [433.15, 0.312]],
    "sources": {
        k: {
            "run_dir": f"results/runs/x/{k}",
            "deck": "in.x",
            "deck_sha256": "0" * 64,
            "log_sha256": "1" * 64,
            "segments": "synthetic",
        }
        for k in ("hold", "cool", "sweep")
    },
}


def tiny_pores(polymer, res, chains, carbons, root, width_nm=3.0, bulk_table=None):
    """(bulk, wide, narrow) system dirs: a small amorphous box, its wide pore, and that
    pore narrowed (from its own data.lmp, standing in for the relaxed state; D48)."""
    from sepsim.build.amorphous import build_amorphous
    from sepsim.build.pore import build_pore, narrow_pore

    bulk = build_amorphous(polymer, res, chains, carbons, 0.3, 3, root)
    wide = build_pore(bulk / "data.lmp", bulk, width_nm, 1, root)
    narrow = narrow_pore(wide / "data.lmp", wide, width_nm, bulk_table or SYN_BULK, root)
    return bulk, wide, narrow
