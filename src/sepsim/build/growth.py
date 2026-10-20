"""Periodic random-walk growth of amorphous chains at low density.

Chains are grown one after another, backbone bead by backbone bead, directly in a cubic
periodic box. One growth step places backbone atom ``k`` and, now that both its backbone
neighbors exist, the substituents of backbone atom ``k-1`` (pendant methyl and its H's,
methine/methylene H's), so a step's overlap check covers every atom it adds. Hydrogens are
placed geometrically (FF bond lengths and angles), not sampled.

Bond lengths and AA/UA backbone angles come from the matched FF types. CG angles are drawn
from the FF angle's own Boltzmann distribution at ``cg_angle_temp_K`` (D29),
P(theta) ~ sin(theta) exp(-E(theta) / kT), by inverse CDF on a fine grid. E is the full LAMMPS
``angle_style spica`` energy (D33): K (theta - theta0)^2 plus the 1-3 repulsion, the lj/spica
pair energy of the end-bead types at r13(theta) (from the two FF bond lengths), shifted by
its minimum and cut at r_min (LAMMPS CG-SPICA angle_spica.cpp, pair_lj_spica.cpp init_one).
Backbone torsions follow a rotational-isomeric-state (RIS) bias (t, g+, g-) with Gaussian
jitter around each state (D29), and g+g-/g-g+ consecutive pairs are forbidden (pentane
rule). This is only a starting-state bias; LAMMPS equilibration relaxes it.

Overlap checks run against every previously placed atom (cell list, minimum image) with the
per-resolution thresholds ``MIN_DIST``, excluding intra-chain pairs up to 1-4. When a step
fails ``max_tries`` times the chain backtracks; after ``max_backtracks`` it restarts.
Everything is driven by one ``numpy.random.Generator``: same seed, same coordinates.

iPP (D30): every methine has the configuration ``CHIRAL_SIGN``. Backbone torsions use a
simplified meso-dyad rule following the Suter & Flory 1975 RIS picture (tg/gt dominant), not
their statistical weights (Macromolecules 8, 765, doi:10.1021/ma60048a018): the two torsions
flanking each CH2 between two methines are ``IPP_DYAD_TG`` or ``IPP_DYAD_GT``. The first
dyad is a fair coin (``ipp_p_tg``); each later dyad reverses helix sense with probability
``ipp_p_reversal``. A (t, g+) -> (g-, t) reversal puts g+ g- across the junction methine, so
the pentane rule is waived for that choice.

iPP local strain (D31): the overlap check ignores intra-chain pairs up to
``ipp_local_exclusion_bonds`` (6) bonds apart, so reversals and other local methyl contacts
are accepted; a soft-core push-off in LAMMPS removes them. AA iPP is not grown (D32): UA iPP
is relaxed in LAMMPS and converted by ``sepsim.build.ua2aa``.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import asdict, dataclass

import numpy as np
from scipy.spatial import cKDTree

from sepsim.analysis.units import AVOGADRO
from sepsim.build.topology import Molecule
from sepsim.ff.params import KB_KCAL, ForceField, to_lammps_real

# Isotacticity convention: sign(det[methyl - C, H - C, next_backbone - prev_backbone]) of
# every methine. Growth places the methyl/H pair to give this sign (see bisector_pair).
CHIRAL_SIGN = 1
# iPP meso-dyad pair states (D30) as (first, second) torsion states, 0 t / 1 g+ / 2 g-, for
# CHIRAL_SIGN = +1 in the IUPAC dihedral convention: the compatible gauche sign flips
# between the two positions. Derived geometrically (methyl 1-5 clearance) in the tests.
IPP_DYAD_TG = (0, 1)
IPP_DYAD_GT = (2, 0)
# Growth overlap thresholds (angstrom): heavy-heavy, heavy-H, H-H (AA: D29).
MIN_DIST = {"aa": (3.0, 2.0, 1.6), "ua": (3.2, 2.2, 1.8), "cg": (4.0, 4.0, 4.0)}
CG_ANGLE_GRID_POINTS = 18001  # 0.01 degree spacing on [0, 180]
# lj/spica forms (prefactor, m, n): E = pref eps ((sigma/r)^m - (sigma/r)^n), copied from
# LAMMPS src/CG-SPICA/lj_spica_common.h (lj_prefact, lj_pow1, lj_pow2).
LJ_SPICA_FORMS = {
    "lj9_6": (6.75, 9, 6),
    "lj12_4": (2.59807621135332, 12, 4),
    "lj12_6": (4.0, 12, 6),
    "lj12_5": (3.20377984125109, 12, 5),
}
STAGGERED_DEG = (60.0, 180.0, 300.0)


@dataclass(frozen=True)
class GrowthParams:
    """Growth knobs (the manifest records them with the effective thresholds)."""

    p_trans: float = 0.6
    p_gauche: float = 0.2  # each of g+ and g-
    gauche_deg: float = 60.0
    torsion_sd_deg: float = 10.0  # D29; must be > 0
    cg_angle_temp_K: float = 500.0
    ipp_p_tg: float = 0.5  # first dyad only; (g-, t) otherwise
    # Calibrated once so the phantom C240 UA chain has C_n ~ 5.0, the middle of the iPP
    # theta-condition range 4.1-6.0 (Miyamoto 1969; Kinsinger & Hughes 1963,
    # doi:10.1021/j100803a507); 0.05 grid, phantom C_n = 5.61 at 0.35, 4.71 at 0.40.
    ipp_p_reversal: float = 0.40
    # D31: smallest window that lets an ideal UA helix reversal through (derived in tests).
    ipp_local_exclusion_bonds: int = 6
    check_overlaps: bool = True  # False only for phantom-chain statistics
    max_tries: int = 50
    backtrack: int = 3
    max_backtracks: int = 500
    max_restarts: int = 50

    def __post_init__(self) -> None:
        if not self.torsion_sd_deg > 0:
            raise ValueError("torsion_sd_deg must be > 0 (D29 torsion jitter)")

    def exclusion_bonds(self, mol: Molecule) -> int:
        """Intra-chain pairs up to this many bonds apart are not overlap-checked."""
        if mol.polymer == "ipp" and mol.resolution != "cg":
            return self.ipp_local_exclusion_bonds
        return 3

    def record(self, mol: Molecule) -> dict:
        """Effective parameters for the manifest."""
        heavy, heavy_h, hh = MIN_DIST[mol.resolution]
        return {
            **asdict(self),
            "min_dist": {"heavy": heavy, "heavy_h": heavy_h, "h_h": hh},
            "exclusion_bonds": self.exclusion_bonds(mol),
            **({"cg_angle_energy": CG_ANGLE_ENERGY} if mol.resolution == "cg" else {}),
        }


CG_ANGLE_ENERGY = "angle_style spica: K (theta - theta0)^2 + 1-3 lj/spica repulsion (D33)"


class GrowthError(RuntimeError):
    """Raised when a chain cannot be grown within the restart budget."""


# --------------------------------------------------------------------------- geometry


def _unit(v: np.ndarray) -> np.ndarray:
    return v / math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def _cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cross product of two 3-vectors (np.cross is slow for single vectors)."""
    return np.array(
        [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    )


def place_atom(a, b, c, r: float, theta_deg: float, phi_deg: float) -> np.ndarray:
    """Position d with |d-c| = r, angle(b,c,d) = theta, dihedral(a,b,c,d) = phi (trans 180)."""
    th, ph = math.radians(theta_deg), math.radians(phi_deg)
    bc = _unit(c - b)
    n = _unit(_cross(b - a, bc))
    m = _cross(n, bc)
    d2 = np.array(
        [-r * math.cos(th), r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph)]
    )
    return c + d2[0] * bc + d2[1] * m + d2[2] * n


def bisector_pair(c, a, b, angle_deg: float, sign: float) -> tuple[np.ndarray, np.ndarray]:
    """Unit directions of two substituents on C (neighbors a, b) at ``angle_deg`` apart.

    Both lie in the plane bisecting angle a-C-b, normal to the a-C-b plane; ``sign`` picks
    which one goes to which side (det[d1, d2, b - a] has sign -sign).
    """
    u, v = _unit(a - c), _unit(b - c)
    w = -_unit(u + v)
    n = _unit(_cross(u, v))
    half = math.radians(angle_deg) / 2
    d1 = math.cos(half) * w + sign * math.sin(half) * n
    d2 = math.cos(half) * w - sign * math.sin(half) * n
    return d1, d2


def staggered_hs(ref, nb, me, r: float, theta_deg: float) -> list[np.ndarray]:
    """Three methyl H's on ``me`` (bonded to ``nb``): H-me-nb-ref dihedrals 60/180/300."""
    return [place_atom(ref, nb, me, r, theta_deg, phi) for phi in STAGGERED_DEG]


def bonded_lookup(mol: Molecule, ff: ForceField) -> tuple[dict, dict]:
    """FF r0 per bonded atom pair and theta0 per angle triple, keyed both ways round."""
    r0, th0 = {}, {}
    for (a, b), t in zip(mol.bonds, mol.bond_types, strict=True):
        r0[(a, b)] = r0[(b, a)] = float(ff.bond_types[t]["r0"])
    for (a, j, b), t in zip(mol.angles, mol.angle_types, strict=True):
        th0[(a, j, b)] = th0[(b, j, a)] = float(ff.angle_types[t]["theta0"])
    return r0, th0


def dihedral_deg(p0, p1, p2, p3) -> np.ndarray:
    """IUPAC dihedral angle(s) in degrees in (-180, 180]; trans = 180. Accepts (..., 3)."""
    b0, b1, b2 = p0 - p1, p2 - p1, p3 - p2
    b1n = b1 / np.linalg.norm(b1, axis=-1, keepdims=True)
    v = b0 - np.sum(b0 * b1n, axis=-1, keepdims=True) * b1n
    w = b2 - np.sum(b2 * b1n, axis=-1, keepdims=True) * b1n
    x = np.sum(v * w, axis=-1)
    y = np.sum(np.cross(b1n, v) * w, axis=-1)
    return np.degrees(np.arctan2(y, x))


def angle_deg(p0, p1, p2) -> np.ndarray:
    """Angle p0-p1-p2 in degrees. Accepts (..., 3)."""
    u, v = p0 - p1, p2 - p1
    cos = np.sum(u * v, axis=-1) / (np.linalg.norm(u, axis=-1) * np.linalg.norm(v, axis=-1))
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))


def chirality_signs(mol: Molecule, pos: np.ndarray) -> list[int]:
    """``CHIRAL_SIGN`` convention value of every methine of one chain (isotactic: all equal)."""
    signs = []
    bb = mol.backbone
    for i, sub in mol.subs.items():
        if len(sub) == 2 and mol.types[sub[0]] in ("CT_CH3_iso", "CH3"):
            c = pos[bb[i]]
            vol = np.linalg.det(
                np.array([pos[sub[0]] - c, pos[sub[1]] - c, pos[bb[i + 1]] - pos[bb[i - 1]]])
            )
            signs.append(int(np.sign(vol)))
    return signs


def spica_13_energy(r, epsilon: float, sigma: float, form: str) -> np.ndarray:
    """``angle_style spica`` 1-3 repulsion (kcal/mol) at 1-3 distance(s) ``r`` (angstrom).

    The lj/spica pair energy minus its value at the minimum r_min = sigma (m/n)^(1/(m-n)),
    for r < r_min only, zero beyond (angle_spica.cpp; rminsq/emin from pair_lj_spica.cpp).
    """
    pref, m, n = LJ_SPICA_FORMS[form]
    rmin = sigma * (m / n) ** (1.0 / (m - n))
    r = np.asarray(r, dtype=float)
    e = pref * epsilon * ((sigma / r) ** m - (sigma / r) ** n)
    emin = pref * epsilon * ((sigma / rmin) ** m - (sigma / rmin) ** n)
    return np.where(r < rmin, e - emin, 0.0)


def cg_angle_energy(theta_deg, K: float, theta0_deg: float, r1=0.0, r2=0.0, pair=None):
    """Full ``angle_style spica`` energy (kcal/mol) of an angle at ``theta_deg``.

    K (theta - theta0)^2 (K in kcal/mol/rad^2) plus, when ``pair`` (epsilon, sigma, form of
    the end-bead type pair) is given, the 1-3 repulsion at r13 from bond lengths r1, r2.
    """
    th = np.radians(np.asarray(theta_deg, dtype=float))
    e = K * (th - math.radians(theta0_deg)) ** 2
    if pair is not None:
        r13 = np.sqrt(r1 * r1 + r2 * r2 - 2.0 * r1 * r2 * np.cos(th))
        r13 = np.maximum(r13, 0.1)  # r13 -> 0 at theta = 0 (r1 == r2); exp(-E/kT) is 0 there
        e = e + spica_13_energy(r13, pair["epsilon"], pair["sigma"], pair["form"])
    return e


def cg_angle_grid(
    K: float, theta0_deg: float, temp_K: float, r1=0.0, r2=0.0, pair=None
) -> tuple[np.ndarray, np.ndarray]:
    """Grid (degrees) and normalized CDF of P(theta) ~ sin(theta) exp(-E(theta) / kT).

    E is ``cg_angle_energy`` (harmonic only when ``pair`` is None).
    """
    grid = np.linspace(0.0, 180.0, CG_ANGLE_GRID_POINTS)
    energy = cg_angle_energy(grid, K, theta0_deg, r1, r2, pair)
    pdf = np.sin(np.radians(grid)) * np.exp(-energy / (KB_KCAL * temp_K))
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (pdf[1:] + pdf[:-1]))])
    return grid, cdf / cdf[-1]


def box_length(total_mass: float, density: float) -> float:
    """Cubic box edge (angstrom) for ``total_mass`` (g/mol) at ``density`` (g/cm^3)."""
    volume = total_mass / (AVOGADRO * density) * 1e24
    return volume ** (1.0 / 3.0)


def bond_distances(mol: Molecule, max_bonds: int) -> np.ndarray:
    """Topological distance [i, j] in bonds within one chain, -1 beyond ``max_bonds``."""
    nbr = mol.neighbors()
    out = np.full((mol.n_atoms, mol.n_atoms), -1, dtype=np.int16)
    for s in range(mol.n_atoms):
        dist = {s: 0}
        queue = deque([s])
        while queue:
            a = queue.popleft()
            if dist[a] == max_bonds:
                continue
            for b in nbr[a]:
                if b not in dist:
                    dist[b] = dist[a] + 1
                    queue.append(b)
        out[s, list(dist)] = list(dist.values())
    return out


def exclusion_matrix(mol: Molecule, max_bonds: int = 3) -> np.ndarray:
    """Boolean [i, j]: atoms i and j of one chain are within ``max_bonds`` bonds (incl. i == j)."""
    return bond_distances(mol, max_bonds) >= 0


def ipp_dyad_roles(mol: Molecule) -> list[int]:
    """Dyad role of the backbone torsion set at each growth step k (about bond k-2 -- k-1).

    1 = first, 2 = second torsion flanking a CH2 that sits between two methines (an iPP meso
    dyad); 0 elsewhere (PE, CG, and the iPP chain ends).
    """
    nb = len(mol.backbone)
    roles = [0] * nb
    if mol.polymer != "ipp" or mol.resolution == "cg":
        return roles
    is_h = mol.is_hydrogen()
    methine = [any(not is_h[s] for s in mol.subs[i]) for i in range(nb)]
    for m in range(1, nb - 1):
        if methine[m - 1] and methine[m + 1] and not methine[m]:
            roles[m + 1], roles[m + 2] = 1, 2
    return roles


# --------------------------------------------------------------------------- cell list


class _CellList:
    """Fixed-grid cell list with LIFO removal (growth only ever removes its latest atoms)."""

    def __init__(self, n_atoms: int, box: float, cell: float) -> None:
        self.box = box
        self.nc = max(1, min(int(box // cell), 100))
        self.size = box / self.nc
        self.count = np.zeros(self.nc**3, dtype=np.int64)
        self.slots = np.full((self.nc**3, 16), -1, dtype=np.int64)
        self.atom_cell = np.full(n_atoms, -1, dtype=np.int64)
        off = np.array(np.meshgrid(*[np.arange(-1, 2)] * 3, indexing="ij")).reshape(3, -1).T
        self.offsets = off

    def _cell_xyz(self, p: np.ndarray) -> np.ndarray:
        return (np.floor(np.mod(p, self.box) / self.size).astype(np.int64)) % self.nc

    def _flat(self, xyz: np.ndarray) -> np.ndarray:
        xyz = np.mod(xyz, self.nc)
        return (xyz[..., 0] * self.nc + xyz[..., 1]) * self.nc + xyz[..., 2]

    def add(self, g: int, p: np.ndarray) -> None:
        c = int(self._flat(self._cell_xyz(p)))
        if self.count[c] == self.slots.shape[1]:
            self.slots = np.concatenate([self.slots, np.full_like(self.slots, -1)], axis=1)
        self.slots[c, self.count[c]] = g
        self.count[c] += 1
        self.atom_cell[g] = c

    def remove_last(self, g: int) -> None:
        c = self.atom_cell[g]
        self.count[c] -= 1
        assert self.slots[c, self.count[c]] == g, "cell list removal must be LIFO"
        self.slots[c, self.count[c]] = -1
        self.atom_cell[g] = -1

    def neighbors(self, p: np.ndarray) -> np.ndarray:
        """Indices of atoms in the 27 cells around each row of ``p`` -> (m, k) with -1 pads."""
        cells = self._flat(self._cell_xyz(p)[:, None, :] + self.offsets[None, :, :])
        return self.slots[cells].reshape(len(p), -1)


# --------------------------------------------------------------------------- growth


class _Grower:
    def __init__(self, mol, ff, n_chains, box, params, rng) -> None:
        self.mol, self.params, self.rng, self.box = mol, params, rng, box
        self.nper = mol.n_atoms
        self.pos = np.zeros((n_chains * mol.n_atoms, 3))
        self.is_h = np.array(mol.is_hydrogen())
        self.excl = exclusion_matrix(mol, params.exclusion_bonds(mol))
        xx, xh, hh = MIN_DIST[mol.resolution]
        self.thr = np.array([[xx, xh], [xh, hh]])  # index 0 = heavy, 1 = hydrogen
        self.cells = _CellList(len(self.pos), box, max(xx, xh, hh))
        self.cg = mol.resolution == "cg"
        self.bond_r0, self.angle_th0 = bonded_lookup(mol, ff)
        self.cg_cdf: dict[tuple, tuple[np.ndarray, np.ndarray]] = {}
        if self.cg:  # one inverse-CDF table per (angle type, end types, bond lengths)
            real = to_lammps_real(ff)
            spica = ff.styles["angle"] == "spica"
            tables: dict[tuple, tuple[np.ndarray, np.ndarray]] = {}
            for (a, j, b), t in zip(mol.angles, mol.angle_types, strict=True):
                ends = (mol.types[a], mol.types[b])
                r1, r2 = self.bond_r0[(a, j)], self.bond_r0[(j, b)]
                key = (t, ends, r1, r2)
                if key not in tables:
                    pair = (real["pair"].get(ends) or real["pair"][ends[::-1]]) if spica else None
                    K, th0 = real["angle"][t]["K"], real["angle"][t]["theta0"]
                    tables[key] = cg_angle_grid(K, th0, params.cg_angle_temp_K, r1, r2, pair)
                self.cg_cdf[(a, j, b)] = self.cg_cdf[(b, j, a)] = tables[key]
        probs = np.array([params.p_trans, params.p_gauche, params.p_gauche], dtype=float)
        self.ris_probs = probs / probs.sum()
        self.ris_angles = (180.0, params.gauche_deg, -params.gauche_deg)
        self.dyad_role = ipp_dyad_roles(mol)
        self.stats = {"proposals": 0, "backtracks": 0, "restarts": 0, "dyads": 0, "reversals": 0}

    # -- proposals ----------------------------------------------------------------

    def _theta(self, a: int, j: int, b: int) -> float:
        if not self.cg:
            return self.angle_th0[(a, j, b)]
        grid, cdf = self.cg_cdf[(a, j, b)]
        return float(np.interp(self.rng.random(), cdf, grid))

    def _torsion_state(self, k: int, tors: list) -> int:
        """State (0 t, 1 g+, 2 g-) of the backbone torsion set at step ``k`` (k >= 3)."""
        role = self.dyad_role[k]
        prev_state = tors[k - 1]
        probs = np.zeros(3)
        reversal = None
        if role == 1:
            if self.dyad_role[k - 2] != 1:  # first dyad: fair coin by default
                probs[IPP_DYAD_TG[0]] = self.params.ipp_p_tg
                probs[IPP_DYAD_GT[0]] = 1.0 - self.params.ipp_p_tg
            else:
                same = IPP_DYAD_TG if tors[k - 2] == IPP_DYAD_TG[0] else IPP_DYAD_GT
                other = IPP_DYAD_GT if same is IPP_DYAD_TG else IPP_DYAD_TG
                probs[same[0]] = 1.0 - self.params.ipp_p_reversal
                probs[other[0]] = self.params.ipp_p_reversal
                reversal = other[0]
        elif role == 2:  # second torsion of the dyad is fixed by the first
            probs[IPP_DYAD_TG[1] if prev_state == IPP_DYAD_TG[0] else IPP_DYAD_GT[1]] = 1.0
        else:
            probs = self.ris_probs.copy()
        if prev_state in (1, 2) and 3 - prev_state != reversal:  # pentane rule
            probs[3 - prev_state] = 0.0
        return int(self.rng.choice(3, p=probs / probs.sum()))

    def _backbone_torsion(self, k: int, tors: list) -> tuple[int, float]:
        """(state, dihedral in degrees) for step k >= 3 of an AA/UA chain."""
        state = self._torsion_state(k, tors)
        return state, self.ris_angles[state] + self.rng.normal(0.0, self.params.torsion_sd_deg)

    def _interior_subs(self, out: dict, known: dict, i: int) -> None:
        """Substituents of backbone atom i (both backbone neighbours known)."""
        mol = self.mol
        subs = mol.subs[i]
        if not subs:
            return
        if len(subs) != 2:
            raise ValueError(f"interior backbone atom with {len(subs)} substituents")
        c, a, b = mol.backbone[i], mol.backbone[i - 1], mol.backbone[i + 1]
        dirs = bisector_pair(
            known[c], known[a], known[b], self.angle_th0[(subs[0], c, subs[1])], -CHIRAL_SIGN
        )
        for sub, d in zip(subs, dirs, strict=True):
            out[sub] = known[c] + self.bond_r0[(c, sub)] * d
            if sub in mol.sub_hs:  # pendant methyl H's, staggered against prev backbone
                self._methyl_hs(out, sub, mol.sub_hs[sub], c, a, {**known, **out})

    def _methyl_hs(self, out: dict, me: int, hs: list, nb: int, ref: int, known: dict) -> None:
        r, th = self.bond_r0[(me, hs[0])], self.angle_th0[(hs[0], me, nb)]
        out.update(zip(hs, staggered_hs(known[ref], known[nb], known[me], r, th), strict=True))

    def _propose(self, k: int, bb_pos: dict, tors: list) -> tuple[dict, int | None]:
        """New atom positions for growth step k (backbone atom k + finished substituents)."""
        mol, bb, rng = self.mol, self.mol.backbone, self.rng
        out: dict[int, np.ndarray] = {}
        state = None
        if k == 0:
            out[bb[0]] = rng.uniform(0.0, self.box, 3)
            return out, None
        r = self.bond_r0[(bb[k - 1], bb[k])]
        if k == 1:
            out[bb[1]] = bb_pos[bb[0]] + r * _unit(rng.normal(size=3))
        else:
            theta = self._theta(bb[k - 2], bb[k - 1], bb[k])
            if k == 2:
                ref = bb_pos[bb[1]] + _unit(rng.normal(size=3))
                phi = rng.uniform(-180.0, 180.0)
            elif self.cg:
                ref, phi = bb_pos[bb[k - 3]], rng.uniform(-180.0, 180.0)
            else:
                state, phi = self._backbone_torsion(k, tors)
                ref = bb_pos[bb[k - 3]]
            out[bb[k]] = place_atom(ref, bb_pos[bb[k - 2]], bb_pos[bb[k - 1]], r, theta, phi)
        known = {**bb_pos, **out}
        if k >= 2:
            self._interior_subs(out, known, k - 1)
            if k == 2 and mol.subs[0]:
                self._methyl_hs(out, bb[0], mol.subs[0], bb[1], bb[2], known)
            if k == len(bb) - 1 and mol.subs[k]:
                self._methyl_hs(out, bb[k], mol.subs[k], bb[k - 1], bb[k - 2], known)
        return out, state

    # -- overlap ------------------------------------------------------------------

    def _clashes(self, chain: int, new: dict) -> bool:
        if not self.params.check_overlaps:
            return False
        loc = np.fromiter(new.keys(), dtype=np.int64)
        p = np.array(list(new.values()))
        h_new = self.is_h[loc]
        # against placed atoms
        cand = self.cells.neighbors(p)
        rows, cols = np.nonzero(cand >= 0)
        if rows.size:
            other = cand[rows, cols]
            d = p[rows] - self.pos[other]
            d -= self.box * np.round(d / self.box)
            dist = np.sqrt(np.einsum("ij,ij->i", d, d))
            same = (other // self.nper) == chain
            o_loc = other % self.nper
            excluded = same & self.excl[loc[rows], o_loc]
            thr = self.thr[h_new[rows].astype(int), self.is_h[o_loc].astype(int)]
            if np.any((dist < thr) & ~excluded):
                return True
        # among the new atoms themselves
        if len(loc) > 1:
            i, j = np.triu_indices(len(loc), 1)
            d = p[i] - p[j]
            dist = np.sqrt(np.einsum("ij,ij->i", d, d))
            thr = self.thr[h_new[i].astype(int), h_new[j].astype(int)]
            if np.any((dist < thr) & ~self.excl[loc[i], loc[j]]):
                return True
        return False

    # -- driver -------------------------------------------------------------------

    def grow_chain(self, chain: int) -> None:
        p, mol = self.params, self.mol
        base = chain * self.nper
        nb = len(mol.backbone)
        restarts = 0
        while True:
            steps: list[list[int]] = []  # local indices added per step
            bb_pos: dict[int, np.ndarray] = {}
            tors: list[int | None] = []
            backtracks = stuck = best = 0
            k = 0
            while k < nb:
                for _ in range(p.max_tries):
                    self.stats["proposals"] += 1
                    new, state = self._propose(k, bb_pos, tors)
                    if not self._clashes(chain, new):
                        break
                    new = None
                if new is not None:
                    for loc, x in new.items():
                        self.pos[base + loc] = x
                        self.cells.add(base + loc, x)
                        bb_pos[loc] = x
                    steps.append(list(new))
                    tors.append(state)
                    k += 1
                    if k > best:
                        best, stuck = k, 0
                    continue
                backtracks += 1
                stuck += 1
                self.stats["backtracks"] += 1
                if backtracks > p.max_backtracks:
                    break
                # Escalate: the n-th consecutive backtrack without progress undoes n * backtrack.
                for _ in range(min(p.backtrack * stuck, k)):
                    self._pop(base, steps, bb_pos, tors)
                    k -= 1
            if k == nb:
                self._count_reversals(tors)
                return
            while steps:
                self._pop(base, steps, bb_pos, tors)
            restarts += 1
            self.stats["restarts"] += 1
            if restarts > p.max_restarts:
                raise GrowthError(
                    f"chain {chain} could not be grown after {p.max_restarts} restarts; "
                    "lower the density"
                )

    def _count_reversals(self, tors: list) -> None:
        """Realised dyad junctions and helix reversals of a finished chain."""
        for k, role in enumerate(self.dyad_role):
            if role == 1 and self.dyad_role[k - 2] == 1:
                self.stats["dyads"] += 1
                self.stats["reversals"] += tors[k] != tors[k - 2]

    def _pop(self, base: int, steps: list, bb_pos: dict, tors: list) -> None:
        for loc in reversed(steps.pop()):
            self.cells.remove_last(base + loc)
            bb_pos.pop(loc, None)
        tors.pop()


def grow_amorphous(
    mol: Molecule,
    ff: ForceField,
    n_chains: int,
    density: float,
    seed: int,
    params: GrowthParams | None = None,
) -> tuple[np.ndarray, float, dict]:
    """Grow ``n_chains`` copies of ``mol`` in a cubic box at ``density`` (g/cm^3).

    Returns (unwrapped positions (n_chains * n_atoms, 3), box edge in angstrom, stats).
    """
    params = params or GrowthParams()
    masses = [ff.atom_types[t]["mass"] for t in mol.types]
    box = box_length(n_chains * float(sum(masses)), density)
    grower = _Grower(mol, ff, n_chains, box, params, np.random.default_rng(seed))
    for c in range(n_chains):
        grower.grow_chain(c)
    return grower.pos, box, grower.stats


def min_nonbonded_distances(
    mol: Molecule,
    pos: np.ndarray,
    box,
    n_chains: int,
    rmax: float = 6.0,
    params: GrowthParams | None = None,
) -> dict:
    """Minimum distances (minimum image) for the pairs growth checks, plus local pairs.

    ``box`` is the cube edge or the three orthogonal box lengths. ``heavy`` (heavy-heavy)
    and ``all`` (any pair) cover inter-chain pairs and intra-chain pairs more than
    ``params.exclusion_bonds(mol)`` bonds apart (3 for PE/CG, 6 for iPP). ``local`` covers
    the intra-chain pairs 4 to that many bonds apart, which growth does not check (D31):
    ``heavy_heavy``, ``heavy_h`` and ``h_h`` minima. ``None`` where no pair is within rmax.
    """
    params = params or GrowthParams()
    nb = params.exclusion_bonds(mol)
    box = np.broadcast_to(np.asarray(box, dtype=float), (3,))
    wrapped = np.mod(pos, box)
    wrapped = np.where(wrapped >= box, 0.0, wrapped)
    pairs = cKDTree(wrapped, boxsize=box).query_pairs(rmax, output_type="ndarray")
    bdist = bond_distances(mol, nb)
    is_h = np.tile(np.array(mol.is_hydrogen()), n_chains)
    nper = mol.n_atoms
    i, j = pairs[:, 0], pairs[:, 1]
    topo = np.where(i // nper == j // nper, bdist[i % nper, j % nper], -1)
    checked, local = topo < 0, topo >= 4
    d = wrapped[i] - wrapped[j]
    d -= box * np.round(d / box)
    dist = np.linalg.norm(d, axis=1)
    n_h = is_h[i].astype(int) + is_h[j].astype(int)

    def smallest(mask):
        return float(dist[mask].min()) if mask.any() else None

    return {
        "heavy": smallest(checked & (n_h == 0)),
        "all": smallest(checked),
        "local": {
            "bonds": [4, nb] if nb >= 4 else None,
            "heavy_heavy": smallest(local & (n_h == 0)),
            "heavy_h": smallest(local & (n_h == 1)),
            "h_h": smallest(local & (n_h == 2)),
        },
    }
