"""Molecule graphs for linear PE and isotactic PP chains at AA, UA and CG resolution.

A chain is built as a *backbone* (the longest carbon path, grown bead by bead) plus
*substituents* hanging off each backbone atom (pendant methyls and hydrogens). Atom types
are force-field type names from the YAMLs in ``forcefields/``; angles and dihedrals are
derived from the bond graph, and every bonded entry is mapped to exactly one FF type.

Chain chemistry (``n`` = total carbons per chain):

* PE: n-C(n)H(2n+2). Backbone = all ``n`` carbons.
* iPP: H-[CH2-CH(CH3)](n/3)-H. The first unit's CH2 gains the terminal H and becomes a
  CH3 bonded to a CH (iso-methyl); the last unit's CH gains the other terminal H and becomes
  a CH2 bearing an n-CH3. Backbone = head CH3, the alternating CH/CH2 chain, the last
  CH2 and its methyl (2n/3 + 1 carbons); the other n/3 - 1 methyls are pendant on the
  n/3 - 1 methines. Formula C(n)H(2n+2).
* CG (SDK, PE only): n/3 beads, CT-(CM)(n/3-2)-CT.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import yaml

from sepsim.ff.params import ForceField, load_forcefield

POLYMERS = ("pe", "ipp")
RESOLUTIONS = ("aa", "ua", "cg")
FF_BY_RES = {"aa": "opls2020_aa", "ua": "trappe_ua", "cg": "sdk_cg"}

ELEMENT_MASS = {"C": 12.011, "H": 1.008}
# Element composition of every type name used by the builders (UA/CG sites are lumped).
TYPE_COMPOSITION = {
    # OPLS/2020 AA
    "CT_CH3": {"C": 1},
    "CT_CH3_iso": {"C": 1},
    "CT_CH2": {"C": 1},
    "CT_CH": {"C": 1},
    "HC": {"H": 1},
    # TraPPE-UA (+ explicit methine H)
    "CH3": {"C": 1, "H": 3},
    "CH2": {"C": 1, "H": 2},
    "CH": {"C": 1},
    "H": {"H": 1},
    # SDK CG
    "CM": {"C": 3, "H": 6},
    "CT": {"C": 3, "H": 7},
}


class TopologyError(ValueError):
    """Raised for unsupported chain requests or bonded entries without a unique FF type."""


@dataclass
class Molecule:
    """One chain: typed atoms, bonds, the backbone path and per-backbone substituents.

    ``subs[i]`` lists the atoms bonded to backbone position ``i`` that are not backbone
    atoms (heavy substituent first); ``sub_hs[a]`` lists the hydrogens of a pendant methyl
    ``a``. ``backbone`` holds atom indices in growth order.
    """

    polymer: str
    resolution: str
    n_carbons: int
    types: list[str]
    bonds: list[tuple[int, int]]
    backbone: list[int]
    subs: dict[int, list[int]]
    sub_hs: dict[int, list[int]] = field(default_factory=dict)
    angles: list[tuple[int, int, int]] = field(default_factory=list)
    dihedrals: list[tuple[int, int, int, int]] = field(default_factory=list)
    bond_types: list[str] = field(default_factory=list)
    angle_types: list[str] = field(default_factory=list)
    dihedral_types: list[str] = field(default_factory=list)

    @property
    def n_atoms(self) -> int:
        return len(self.types)

    def neighbors(self) -> list[list[int]]:
        nbr: list[list[int]] = [[] for _ in self.types]
        for a, b in self.bonds:
            nbr[a].append(b)
            nbr[b].append(a)
        return nbr

    def is_hydrogen(self) -> list[bool]:
        return [TYPE_COMPOSITION[t] == {"H": 1} for t in self.types]


def _validate(polymer: str, resolution: str, n_carbons: int) -> None:
    if polymer not in POLYMERS:
        raise TopologyError(f"unknown polymer {polymer!r}; choose from {POLYMERS}")
    if resolution not in RESOLUTIONS:
        raise TopologyError(f"unknown resolution {resolution!r}; choose from {RESOLUTIONS}")
    if resolution == "cg" and polymer != "pe":
        raise TopologyError(
            "CG resolution supports PE only: the SDK/SPICA force field has no iPP model "
            "(decisions.md D7). Use --res aa or --res ua for iPP."
        )
    if polymer == "pe" and resolution != "cg" and n_carbons < 4:
        raise TopologyError(f"PE needs at least 4 carbons, got {n_carbons}")
    if (polymer == "ipp" or resolution == "cg") and (n_carbons % 3 or n_carbons < 6):
        raise TopologyError(
            f"{polymer.upper()} at {resolution.upper()} needs a carbon count divisible by 3 "
            f"and >= 6, got {n_carbons}"
        )


class _Graph:
    def __init__(self) -> None:
        self.types: list[str] = []
        self.bonds: list[tuple[int, int]] = []

    def add(self, typ: str, bonded_to: int | None = None) -> int:
        self.types.append(typ)
        idx = len(self.types) - 1
        if bonded_to is not None:
            self.bonds.append((bonded_to, idx))
        return idx


def _carbon_skeleton(polymer: str, n: int) -> tuple[list[int], dict[int, int]]:
    """Backbone carbon count and pendant-methyl positions {backbone pos: 1} for the chain."""
    if polymer == "pe":
        return list(range(n)), {}
    units = n // 3
    n_backbone = 2 * units + 1
    # Backbone: 0 = head CH3, odd positions 1..2*units-3 = methines, then CH2s, last = n-CH3.
    pendant = {pos: 1 for pos in range(1, 2 * units - 2, 2)}
    return list(range(n_backbone)), pendant


def _heavy_type(resolution: str, n_c: int, nbr_is_ch: bool) -> str:
    if resolution == "aa":
        if n_c == 1:
            return "CT_CH3_iso" if nbr_is_ch else "CT_CH3"
        return {2: "CT_CH2", 3: "CT_CH"}[n_c]
    return {1: "CH3", 2: "CH2", 3: "CH"}[n_c]


def build_chain(polymer: str, resolution: str, n_carbons: int) -> Molecule:
    """Return the typed molecule graph (with angles/dihedrals) for one chain."""
    _validate(polymer, resolution, n_carbons)
    if resolution == "cg":
        return _build_cg(n_carbons)

    backbone_pos, pendant = _carbon_skeleton(polymer, n_carbons)
    nb = len(backbone_pos)
    # Carbon-neighbor counts along the backbone (pendant methyls add one).
    n_c = [(1 if i in (0, nb - 1) else 2) + pendant.get(i, 0) for i in range(nb)]

    g = _Graph()
    backbone: list[int] = []
    subs: dict[int, list[int]] = {}
    sub_hs: dict[int, list[int]] = {}
    for i in range(nb):
        nbr_is_ch = (i == 0 and n_c[1] == 3) or (i == nb - 1 and n_c[nb - 2] == 3)
        atom = g.add(_heavy_type(resolution, n_c[i], nbr_is_ch), backbone[-1] if i else None)
        backbone.append(atom)
        subs[i] = []
        if pendant.get(i):
            me = g.add(_heavy_type(resolution, 1, True), atom)
            subs[i].append(me)
            if resolution == "aa":
                sub_hs[me] = [g.add("HC", me) for _ in range(3)]
        n_h = 4 - n_c[i]
        if resolution == "aa":
            subs[i].extend(g.add("HC", atom) for _ in range(n_h))
        elif n_c[i] == 3:  # UA: explicit H only on methines
            subs[i].append(g.add("H", atom))

    mol = Molecule(polymer, resolution, n_carbons, g.types, g.bonds, backbone, subs, sub_hs)
    derive_angles_dihedrals(mol)
    return mol


def _build_cg(n_carbons: int) -> Molecule:
    nb = n_carbons // 3
    types = ["CT"] + ["CM"] * (nb - 2) + ["CT"]
    bonds = [(i, i + 1) for i in range(nb - 1)]
    mol = Molecule("pe", "cg", n_carbons, types, bonds, list(range(nb)), {i: [] for i in range(nb)})
    derive_angles_dihedrals(mol)
    return mol


def derive_angles_dihedrals(mol: Molecule) -> None:
    """Fill ``mol.angles`` and ``mol.dihedrals`` from the bond graph.

    Angles: every pair of neighbors around each atom (count = sum C(deg, 2)).
    Dihedrals: for every bond j-k, every i in N(j)-{k} and l in N(k)-{j}
    (count = sum over bonds (deg_j - 1)(deg_k - 1)). At UA, dihedrals containing the
    explicit methine H are dropped (the FF defines none); at CG none are generated.
    """
    nbr = mol.neighbors()
    mol.angles = [
        (a, j, b) for j in range(mol.n_atoms) for a, b in itertools.combinations(nbr[j], 2)
    ]
    mol.dihedrals = []
    if mol.resolution == "cg":
        return
    is_h = mol.is_hydrogen()
    for j, k in mol.bonds:
        for i in nbr[j]:
            if i == k:
                continue
            for m in nbr[k]:
                if m == j:
                    continue
                if mol.resolution == "ua" and (is_h[i] or is_h[m] or is_h[j] or is_h[k]):
                    continue
                mol.dihedrals.append((i, j, k, m))


# --------------------------------------------------------------------------- typing


def _token_matches(token: str, typ: str, ff: ForceField, wildcards: dict) -> bool:
    if token == typ:
        return True
    if token == ff.atom_types[typ].get("class"):
        return True
    return typ in wildcards.get(token, ())


def match_type(atom_types: tuple[str, ...], section: dict, ff: ForceField, wildcards: dict) -> str:
    """Return the unique FF type name in ``section`` whose pattern matches ``atom_types``.

    Patterns match forward or reversed, on type name, OPLS ``class``, or a YAML wildcard.
    Raises ``TopologyError`` when no type or more than one type matches.
    """
    hits = []
    for name, entry in section.items():
        pattern = entry["pattern"]
        if len(pattern) != len(atom_types):
            continue
        for seq in (atom_types, atom_types[::-1]):
            if all(_token_matches(p, t, ff, wildcards) for p, t in zip(pattern, seq, strict=True)):
                hits.append(name)
                break
    if len(hits) != 1:
        what = "no" if not hits else f"{len(hits)} ({', '.join(hits)})"
        raise TopologyError(f"{'-'.join(atom_types)} matches {what} FF types in {ff.name}")
    return hits[0]


def assign_bonded_types(mol: Molecule, ff: ForceField) -> None:
    """Map every bond/angle/dihedral of ``mol`` to exactly one FF type (fail loudly)."""
    raw = yaml.safe_load(ff.path.read_text()) if ff.path else {}
    wildcards = raw.get("wildcards") or {}
    for t in set(mol.types):
        if t not in ff.atom_types:
            raise TopologyError(f"atom type {t} is not defined in {ff.name}")
    cache: dict[tuple, str] = {}

    def typed(entries, section):
        out = []
        for e in entries:
            key = tuple(mol.types[i] for i in e)
            if key not in cache:
                cache[key] = match_type(key, section, ff, wildcards)
            out.append(cache[key])
        return out

    mol.bond_types = typed(mol.bonds, ff.bond_types)
    mol.angle_types = typed(mol.angles, ff.angle_types)
    mol.dihedral_types = typed(mol.dihedrals, ff.dihedral_types)


def typed_chain(polymer: str, resolution: str, n_carbons: int) -> tuple[Molecule, ForceField]:
    """Build one chain and assign FF bonded types; returns (molecule, force field)."""
    mol = build_chain(polymer, resolution, n_carbons)
    ff = load_forcefield(FF_BY_RES[resolution])
    assign_bonded_types(mol, ff)
    return mol, ff


def formula(types: list[str]) -> tuple[dict[str, int], str]:
    """Element counts and Hill-style formula string for a list of type names."""
    counts = {"C": 0, "H": 0}
    for t in types:
        for el, k in TYPE_COMPOSITION[t].items():
            counts[el] += k
    return counts, f"C{counts['C']}H{counts['H']}"
