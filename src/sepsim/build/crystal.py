"""Perfect PE crystal of infinite stems (decision D59, stage 1; D6d, D27).

``build_crystal`` places straight stems along z on the orthorhombic PE lattice of
``data/crystals/pe_orthorhombic_busing.yaml`` (Busing 23 C cell, two chains per a x b
cell at fractional (0, 0) and (1/2, 1/2)), ``na x nb`` cells laterally, and bonds every
stem to its own periodic image along z (D6d): one molecule per stem, no chain ends, the
last site bonded to the first, so angles (and UA dihedrals) run across the z boundary
too (derived from the ring bond graph; LAMMPS takes the closest image of each bonded
partner). Atoms are written inside the box with image flags 0.

* **CG (SDK):** ``nz`` CM beads per stem (3 CH2 each, no CT ends), straight, with the
  rise per bead ``r0 sin(theta0 / 2)`` of the CM-CM bond and CM-CM-CM angle in the
  force-field YAML (3.64 A, 173 deg: 3.6332 A), i.e. the axial advance of a planar
  zigzag at the force field's own bond and angle; the straight stem then has bonds
  0.007 A short of r0 and 180 deg angles (energy < 0.02 kcal/mol per bead), relaxed by
  the minimization. The setting angle has no CG meaning; the (1/2, 1/2) chain is
  staggered by half a rise along z (project choice: lateral nearest-bead distance 4.81
  instead of 4.46 A, below the 5.16 A LJ 9-6 minimum either way). Lz = nz * rise.
* **UA (TraPPE):** ``2 nz`` CH2 sites per stem (``nz`` c repeats), planar zigzag with
  the TraPPE bond l = 1.54 A and the cell's c: theta = 2 asin(c / 2l) = 111.83 deg
  (TraPPE theta0 114 deg; the YAML constraint c = 2 l sin(theta/2)), carbons at
  z = c/4 + k c/2, displaced by +-(l^2 - c^2/4)^(1/2)/2 = 0.431 A from the stem axis in
  the zigzag plane at the Bunn setting angle (41 deg to b), mirrored for the (1/2, 1/2)
  chain (Pnam: chain 1 carbon at (x a, y b), chain 2 at (a/2 + x a, b/2 - y b)).
  Lz = nz * c; the lattice density is the cell's 0.9963 g/cm3.

Every box length must exceed 2 (recommended LJ cutoff + 2 A skin), so no site sees its
own image or a bonded partner's image within the cutoff (LAMMPS excludes special pairs by
atom id). Output ``<out>/<system_id>/{data.lmp, manifest.yaml}``, id
``pe_<res>_crystal_<na>x<nb>x<nz>_s<seed>`` (the seed is the deck's velocity seed; the
structure itself is deterministic); manifest block ``crystal``.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from sepsim.build.amorphous import (
    DATA_NAME,
    source_git_state,
    system_manifest,
    write_manifest,
)
from sepsim.build.datafile import write_data_file
from sepsim.build.topology import (
    FF_BY_RES,
    Molecule,
    assign_bonded_types,
    derive_angles_dihedrals,
)
from sepsim.crystal_data import CRYSTAL_DIR, load_crystal
from sepsim.ff.params import load_forcefield
from sepsim.run import sha256_file

LATTICE = "pe_orthorhombic_busing"
RESOLUTIONS = ("cg", "ua")
# default repeats (na, nb, nz): CG 51.8 x 49.5 x 98.1 A (3,780 beads), UA 51.8 x 49.5 x
# 102.0 A (11,200 sites)
DEFAULT_REPEATS = {"cg": (7, 10, 27), "ua": (7, 10, 40)}
SKIN_A = 2.0  # neighbor skin of the decks (render._COMMON)
CG_BEAD, UA_SITE = "CM", "CH2"


class CrystalError(ValueError):
    """Raised for an unsupported crystal request (resolution, repeats, box too small)."""


def crystal_id(resolution: str, na: int, nb: int, nz: int, seed: int = 1) -> str:
    """``pe_cg_crystal_7x10x27_s1``: polymer, resolution, repeats a x b x z, seed."""
    return f"pe_{resolution}_crystal_{na}x{nb}x{nz}_s{seed}"


def cg_rise(ff) -> dict:
    """CG rise per bead from the force field: r0 sin(theta0 / 2) of the CM-CM bond and the
    CM-CM-CM angle (the axial advance of a planar zigzag at r0 and theta0)."""
    bond = next(v for v in ff.bond_types.values() if v["pattern"] == [CG_BEAD, CG_BEAD])
    angle = next(v for v in ff.angle_types.values() if v["pattern"] == [CG_BEAD] * 3)
    r0, th0 = float(bond["r0"]), float(angle["theta0"])
    return {"rise_A": r0 * math.sin(math.radians(th0) / 2.0), "r0_A": r0, "theta0_deg": th0}


def ua_zigzag(ff, c: float) -> dict:
    """UA planar zigzag at the TraPPE CHx-CHy bond l and the cell constant c: bond angle
    theta = 2 asin(c / 2l) and the carbons' distance from the stem axis."""
    bond = next(v for v in ff.bond_types.values() if v["pattern"] == ["CHx", "CHx"])
    angle = next(v for v in ff.angle_types.values() if v["pattern"] == ["CHx", "CH2", "CHx"])
    l_cc = float(bond["r0"])
    if c >= 2.0 * l_cc:
        raise CrystalError(f"c = {c} A cannot be spanned by two {l_cc} A bonds")
    theta = 2.0 * math.degrees(math.asin(c / (2.0 * l_cc)))
    return {
        "bond_A": l_cc,
        "angle_deg": theta,
        "ff_theta0_deg": float(angle["theta0"]),
        "r_perp_A": 0.5 * math.sqrt(l_cc**2 - 0.25 * c**2),
    }


def stem_molecule(resolution: str, n_sites: int, ff) -> Molecule:
    """One infinite stem: ``n_sites`` CM beads (CG) or CH2 sites (UA) in a ring of bonds
    (site k bonded to k + 1, the last to the first), angles and UA dihedrals from the ring
    graph, bonded types from the force field."""
    if n_sites < 4:
        raise CrystalError(f"a stem needs at least 4 sites, got {n_sites}")
    typ = CG_BEAD if resolution == "cg" else UA_SITE
    bonds = [(k, k + 1) for k in range(n_sites - 1)] + [(n_sites - 1, 0)]
    n_c = 3 * n_sites if resolution == "cg" else n_sites
    mol = Molecule(
        "pe",
        resolution,
        n_c,
        [typ] * n_sites,
        bonds,
        list(range(n_sites)),
        {k: [] for k in range(n_sites)},
    )
    derive_angles_dihedrals(mol)
    assign_bonded_types(mol, ff)
    return mol


def lattice_positions(resolution: str, cell: dict, na: int, nb: int, nz: int, geom: dict):
    """Site positions (stem by stem, cell by cell with x slowest; two stems per cell),
    the box lengths and the stem axes (x, y)."""
    a, b = float(cell["a"]), float(cell["b"])
    chains = cell["_chains"]
    if resolution == "cg":
        rise = geom["rise_A"]
        lz = nz * rise
    else:
        lz = nz * float(cell["c"])
        phi = math.radians(geom["setting_angle_deg"])
        r_perp = geom["r_perp_A"]
    pos, axes = [], []
    for ia in range(na):
        for ib in range(nb):
            for k, ch in enumerate(chains):
                fx, fy = ch["xy"]
                x0, y0 = (ia + fx) * a, (ib + fy) * b
                axes.append((x0, y0))
                if resolution == "cg":
                    z = (np.arange(nz) + 0.25 + 0.5 * k) * rise
                    xy = np.tile([x0, y0], (nz, 1))
                else:
                    n = 2 * nz
                    s = float(ch["setting_angle_sign"])
                    z = (np.arange(n) + 0.5) * 0.5 * float(cell["c"])
                    sign = np.where(np.arange(n) % 2 == 0, 1.0, -1.0)[:, None]
                    u = np.array([math.sin(phi), s * math.cos(phi)])
                    xy = np.array([x0, y0]) + sign * r_perp * u
                pos.append(np.column_stack([xy, z]))
    lengths = np.array([na * a, nb * b, lz])
    return np.mod(np.vstack(pos), lengths), lengths, np.array(axes)


def _minima(pos: np.ndarray, lengths: np.ndarray, n_per: int, mol: Molecule) -> dict:
    """Shortest inter-stem distance and the bond length range (minimum image), in A."""
    tree = cKDTree(pos, boxsize=lengths)
    pairs = tree.query_pairs(6.0, output_type="ndarray")
    other = pairs[pairs[:, 0] // n_per != pairs[:, 1] // n_per]
    d = pos[other[:, 0]] - pos[other[:, 1]]
    d -= lengths * np.round(d / lengths)
    b = np.array(mol.bonds)
    db = pos[b[:, 0]] - pos[b[:, 1]]
    db -= lengths * np.round(db / lengths)
    bl = np.linalg.norm(db, axis=1)
    return {
        "interstem": float(np.linalg.norm(d, axis=1).min()) if len(d) else None,
        "bond_min": float(bl.min()),
        "bond_max": float(bl.max()),
    }


def build_crystal(
    resolution: str = "cg",
    na: int | None = None,
    nb: int | None = None,
    nz: int | None = None,
    seed: int = 1,
    out: str | Path = "systems",
    lateral: tuple[float, float] | None = None,
) -> Path:
    """Write the crystal's ``data.lmp`` and ``manifest.yaml``; return the system dir.

    ``lateral`` (Lx, Ly in A) picks na, nb as the nearest whole numbers of cells (for a
    lateral box matching another system, e.g. the stage 2 stack); it excludes na/nb."""
    if resolution not in RESOLUTIONS:
        raise CrystalError(f"crystal resolution {resolution!r}: choose from {RESOLUTIONS}")
    crys = load_crystal(LATTICE)
    cell = dict(crys["cell"]) | {"_chains": crys["chains"]}
    if lateral is not None:
        if na is not None or nb is not None:
            raise CrystalError("give either the lateral box or --na/--nb, not both")
        na = max(1, round(float(lateral[0]) / float(cell["a"])))
        nb = max(1, round(float(lateral[1]) / float(cell["b"])))
    d_na, d_nb, d_nz = DEFAULT_REPEATS[resolution]
    na, nb, nz = (int(v if v is not None else d) for v, d in ((na, d_na), (nb, d_nb), (nz, d_nz)))
    if min(na, nb, nz) < 1:
        raise CrystalError(f"repeats must be >= 1, got {na} x {nb} x {nz}")
    out = Path(out)
    git = source_git_state(exclude=out)
    ff = load_forcefield(FF_BY_RES[resolution])
    if resolution == "cg":
        geom = cg_rise(ff)
        n_per = nz
    else:
        geom = ua_zigzag(ff, float(cell["c"]))
        geom["setting_angle_deg"] = float(crys["setting_angle"]["value_deg"])
        n_per = 2 * nz
    mol = stem_molecule(resolution, n_per, ff)
    pos, lengths, axes = lattice_positions(resolution, cell, na, nb, nz, geom)
    rc = float(ff.recommended["lj_cutoff"])
    if lengths.min() < 2.0 * (rc + SKIN_A):
        raise CrystalError(
            f"box {' x '.join(f'{v:.1f}' for v in lengths)} A: every length must exceed"
            f" 2 (LJ cutoff {rc:g} + skin {SKIN_A:g}) = {2 * (rc + SKIN_A):g} A (no site may"
            " see its own or a bonded partner's image); increase the repeats"
        )
    n_stems = len(axes)
    sid = crystal_id(resolution, na, nb, nz, seed)
    sysdir = out / sid
    sysdir.mkdir(parents=True, exist_ok=True)
    bounds = tuple((0.0, float(v)) for v in lengths)
    write_data_file(sysdir / DATA_NAME, mol, ff, n_stems, pos, bounds, title=sid)
    minima = _minima(pos, lengths, n_per, mol)
    mass_cell = 2 * float(ff.atom_types[mol.types[0]]["mass"]) * n_per / nz  # per a x b x rise/c
    lattice_file = CRYSTAL_DIR / f"{LATTICE}.yaml"
    block = {
        "resolution": resolution,
        "lattice": {
            "source": LATTICE,
            "file": lattice_file.name,
            "sha256": sha256_file(lattice_file),
            "a_A": float(cell["a"]),
            "b_A": float(cell["b"]),
            "c_A": float(cell["c"]),
            "temperature_C": float(cell["temperature_C"]),
            "density_g_cm3": float(crys["verification"]["density_g_cm3"]),
            "area_per_chain_A2": float(cell["a"]) * float(cell["b"]) / 2.0,
        },
        "repeats": {"na": na, "nb": nb, "nz": nz},
        "lateral_request_A": None if lateral is None else [float(v) for v in lateral],
        "stems": n_stems,
        "sites_per_stem": n_per,
        "periodic_stems": True,  # each stem bonded to its own z image (D6d): no chain ends
        "stem_axes": "z",
        "box_lengths_A": [float(v) for v in lengths],
        "area_per_chain_A2": float(lengths[0] * lengths[1] / n_stems),
        "rise_per_site_A": float(lengths[2] / n_per),
        "mass_per_cell_repeat_g_mol": mass_cell,
    }
    if resolution == "cg":
        block["cg"] = geom | {
            "rule": "rise = r0 sin(theta0/2) of CM-CM / CM-CM-CM (straight stems)",
            "stagger_rise": 0.5,  # the (1/2, 1/2) chain shifted by half a rise along z
            "setting_angle_deg": None,
        }
    else:
        block["ua"] = geom | {"rule": "planar zigzag, theta = 2 asin(c / 2l), Pnam setting"}
    write_manifest(
        sysdir,
        system_manifest(sid, mol, ff, n_stems, bounds, seed, minima, git, None, {"crystal": block}),
    )
    return sysdir
