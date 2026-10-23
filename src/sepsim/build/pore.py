"""Dry slit pore from an equilibrated bulk box (decision D44).

Hapke et al. (arXiv cond-mat/9607112), method 2: start from an equilibrated periodic
bulk and enlarge the box along z, which opens two free surfaces. The wall is the
source box (the stage 1 ``prep/cooled.data``), optionally replicated ``replicate_z``
times along z first (thick-wall check):

* The data file is validated against the source ``manifest.yaml`` (atom, bond, angle
  and dihedral counts; molecule ids; per-atom types from the manifest's ``type_ids``).
* Each molecule is made whole: its first atom is unwrapped with its image flags and
  every other atom is placed along the bond graph by minimum image.
* The slab is cut open at a z plane ``z_cut``, and each molecule is shifted by whole
  slab periods so it sticks out of the window ``[z_cut, z_cut + Lz_slab)`` as little
  as possible; the plane giving the most compact slab is kept (``place_molecules``).
  Chains crossing the cut still stick out of the window, so the surfaces are rough
  and the outermost atoms lie beyond it. If they would reach across the pore (atoms
  outside the new box), the build fails.
* The box keeps x and y; ``Lz_new = Lz_slab + width``, and the slab's centre of mass
  is put at the box centre. Since the slab keeps all its mass, ``width`` is the mass-equivalent pore width
  ``Lz_new - M / (rho_bulk * A)`` with ``rho_bulk`` the source box density.

Atom, molecule and topology ids, types, charges and velocities are carried over
unchanged (replica k adds k times the source counts to every id); the coefficient
sections are rewritten from the force-field YAML, as in every other system, so the
decks' ``read_data ... nocoeff`` and ``_ff`` coefficient lines apply as they are.

Output: ``<out>/<id>/{data.lmp, manifest.yaml}`` with the source id's ``_amorph_``
replaced by ``_pore_w<width>nm[_z<k>]_`` (``pe_ua_pore_w3nm_n40_c240_s1``,
``pe_cg_pore_w5nm_z2_n40_c240_s1``); deterministic for a given input.
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import yaml

from sepsim import __version__
from sepsim.analysis.units import AVOGADRO
from sepsim.build.amorphous import DATA_NAME, MANIFEST_NAME, source_git_state, write_manifest
from sepsim.build.datafile import (
    BOX_FMT,
    COORD_FMT,
    TypeMaps,
    coeff_sections,
    read_data_file,
    wrap,
)
from sepsim.build.topology import typed_chain
from sepsim.ff.params import FORCEFIELD_DIR, load_forcefield
from sepsim.run import sha256_file

CUT_SCAN_A = 0.25  # spacing of the candidate cut planes, Angstrom
_TOPOLOGY = ("Bonds", "Angles", "Dihedrals", "Impropers")
# Source-manifest keys describing how the bulk box was made; the pore records its source.
_DROP_KEYS = ("build_density_g_cm3", "overlap_minima_angstrom", "growth", "conversion", "source")


class PoreError(ValueError):
    """Raised when the bulk input does not match its manifest or cannot be opened."""


def _width_label(width_nm: float) -> str:
    """3 -> '3nm', 2.5 -> '2p5nm'."""
    return f"{width_nm:g}nm".replace(".", "p")


def pore_id(source_id: str, width_nm: float, replicate_z: int = 1) -> str:
    """``pe_ua_amorph_n40_c240_s1`` -> ``pe_ua_pore_w3nm_n40_c240_s1`` (``_z2`` if replicated)."""
    if "_amorph_" not in source_id:
        raise PoreError(f"source id {source_id!r} is not an amorphous bulk system")
    tag = f"_pore_w{_width_label(width_nm)}" + (f"_z{replicate_z}" if replicate_z > 1 else "")
    return source_id.replace("_amorph_", tag + "_", 1)


def whole_molecules(atoms: np.ndarray, bonds: np.ndarray, lengths: np.ndarray) -> np.ndarray:
    """Unwrapped coordinates with every molecule whole (rows as in ``atoms``, sorted by id).

    The first atom of each molecule is unwrapped with its image flags; the rest are
    placed along the bonds by minimum image, so stale image flags do not matter.
    """
    n = len(atoms)
    row = {int(a): k for k, a in enumerate(atoms[:, 0])}
    nbr: list[list[int]] = [[] for _ in range(n)]
    for a, b in bonds:
        i, j = row[int(a)], row[int(b)]
        nbr[i].append(j)
        nbr[j].append(i)
    wrapped = atoms[:, 4:7]
    pos = np.full((n, 3), np.nan)
    for start in range(n):
        if not np.isnan(pos[start, 0]):
            continue
        pos[start] = wrapped[start] + atoms[start, 7:10] * lengths
        stack = [start]
        while stack:
            a = stack.pop()
            for b in nbr[a]:
                if np.isnan(pos[b, 0]):
                    d = wrapped[b] - wrapped[a]
                    pos[b] = pos[a] + d - lengths * np.round(d / lengths)
                    stack.append(b)
    return pos


def place_molecules(
    z: np.ndarray, mol: np.ndarray, masses: np.ndarray, z_lo: float, period: float
) -> tuple[float, np.ndarray]:
    """(z_cut, shift per atom): the most compact slab of whole molecules.

    For a candidate cut plane ``z_cut`` (scanned over one period from ``z_lo``), each
    molecule is shifted by the whole number of periods that puts it furthest inside the
    window ``[z_cut, z_cut + period)`` (least protrusion; ties to the centre of mass
    nearest the window centre). The plane with the smallest total z extent is kept, so
    the vacuum left between the two rough surfaces is as wide as possible.
    """
    ids, inv = np.unique(mol, return_inverse=True)
    lo_m = np.full(len(ids), np.inf)
    hi_m = np.full(len(ids), -np.inf)
    np.minimum.at(lo_m, inv, z)
    np.maximum.at(hi_m, inv, z)
    m_mol = np.bincount(inv, weights=masses)
    com = np.bincount(inv, weights=masses * z) / m_mol
    best = None
    for zc in z_lo + np.arange(0.0, period, CUT_SCAN_A):
        n0 = -np.floor((com - zc) / period)
        cands = np.stack([n0 - 1, n0, n0 + 1]) * period  # (3, n_mol) shifts
        prot = np.maximum(np.maximum(zc - (lo_m + cands), (hi_m + cands) - (zc + period)), 0.0)
        off = np.abs(com + cands - (zc + 0.5 * period))
        pick = np.lexsort((off, prot), axis=0)[0]  # least protrusion, then nearest centre
        shift = cands[pick, np.arange(len(ids))]
        extent = float((hi_m + shift).max() - (lo_m + shift).min())
        if best is None or extent < best[0] - 1e-9:
            best = (extent, float(zc), shift)
    _, zc, shift = best
    return zc, shift[inv]


def _rows_by_id(rows: list[list[str]]) -> list[list[str]]:
    return sorted(rows, key=lambda r: int(r[0]))


def build_pore(
    data: str | Path,
    source: str | Path,
    width_nm: float,
    replicate_z: int = 1,
    out: str | Path = "systems",
    data_origin: str | None = None,
) -> Path:
    """Open a slit pore of nominal width ``width_nm`` in the bulk box ``data``.

    ``source`` is the bulk system directory (its manifest validates ``data``);
    ``data_origin`` is recorded as the data file's location (default: ``data`` as given).
    Returns the new system directory.
    """
    data, source, out = Path(data), Path(source), Path(out)
    if width_nm <= 0:
        raise PoreError(f"pore width must be > 0 nm, got {width_nm}")
    if replicate_z < 1:
        raise PoreError(f"replicate_z must be >= 1, got {replicate_z}")
    git = source_git_state(exclude=out)
    man_path = source / MANIFEST_NAME
    if not man_path.is_file():
        raise PoreError(f"source manifest not found: {man_path}")
    src = yaml.safe_load(man_path.read_text())
    if "pore" in src:
        raise PoreError(f"{man_path}: source is already a pore system")
    sid = pore_id(src["id"], width_nm, replicate_z)
    n_chains = int(src["n_chains"])
    mol, _ = typed_chain(src["polymer"], src["resolution"], int(src["n_carbons"]))
    nper = mol.n_atoms

    df = read_data_file(data)
    if len(df.box) != 3:
        raise PoreError(f"{data}: box bounds not found")
    if df.counts.get("impropers"):
        raise PoreError(f"{data}: impropers are not supported")
    total = src["counts"]["total"]
    for key in ("atoms", "bonds", "angles", "dihedrals"):
        if df.counts.get(key, 0) != total[key]:
            raise PoreError(
                f"{data}: {df.counts.get(key, 0)} {key}, source manifest has {total[key]}"
            )
    atoms = df.sorted_atoms()
    if len(atoms) != total["atoms"]:
        raise PoreError(f"{data}: {len(atoms)} Atoms rows, header says {total['atoms']}")
    if not np.array_equal(atoms[:, 0].astype(np.int64), np.arange(1, len(atoms) + 1)):
        raise PoreError(f"{data}: atom ids are not 1..{len(atoms)}")
    if not np.array_equal(
        atoms[:, 1].astype(np.int64), np.repeat(np.arange(1, n_chains + 1), nper)
    ):
        raise PoreError(f"{data}: molecule ids do not match {n_chains} chains of {nper}")
    ids = src["type_ids"]
    expected = np.tile([ids["atom"][t] for t in mol.types], n_chains)
    if not np.array_equal(atoms[:, 2].astype(np.int64), expected):
        raise PoreError(f"{data}: atom types do not match the source manifest type_ids")

    ff_path = FORCEFIELD_DIR / src["forcefield"]["file"]
    ff = load_forcefield(ff_path)
    tm = TypeMaps(
        atom=ids["atom"], bond=ids["bond"], angle=ids["angle"], dihedral=ids.get("dihedral") or {}
    )
    mass_of = {i: float(ff.atom_types[n]["mass"]) for n, i in ids["atom"].items()}
    masses = np.array([mass_of[int(t)] for t in atoms[:, 2]])

    # ---- whole molecules, replicated along z
    lo = np.array([b[0] for b in df.box])
    lengths = np.array([hi - lo_ for lo_, hi in df.box])
    bonds = df.topology("Bonds")[:, 2:4]
    pos = whole_molecules(atoms, bonds, lengths)
    n_src, r = len(atoms), replicate_z
    pos = np.vstack([pos + [0.0, 0.0, k * lengths[2]] for k in range(r)])
    masses = np.tile(masses, r)
    mol_ids = np.concatenate([atoms[:, 1].astype(np.int64) + k * n_chains for k in range(r)])
    slab = float(r * lengths[2])  # wall thickness = slab period before opening, Angstrom

    # ---- cut plane, molecules into the window [z_cut, z_cut + slab), mass centre at box centre
    z_cut, shift = place_molecules(pos[:, 2], mol_ids, masses, float(lo[2]), slab)
    pos[:, 2] += shift
    width = 10.0 * float(width_nm)
    lz_new = slab + width
    z_lo_new = float(lo[2])
    com = float((masses * pos[:, 2]).sum() / masses.sum())
    pos[:, 2] += z_lo_new + 0.5 * lz_new - com  # slab centre of mass at the box centre
    win_lo = z_cut + z_lo_new + 0.5 * lz_new - com  # the window [z_cut, z_cut + slab), moved
    zmin, zmax = float(pos[:, 2].min()), float(pos[:, 2].max())
    if zmin < z_lo_new or zmax >= z_lo_new + lz_new:
        # placement relative to the mass centre does not depend on the width
        half = max(z_lo_new + 0.5 * lz_new - zmin, zmax - z_lo_new - 0.5 * lz_new)
        raise PoreError(
            f"slab atoms span z {zmin:.2f}..{zmax:.2f} A, beyond the new box"
            f" {z_lo_new:.2f}..{z_lo_new + lz_new:.2f} A: chains would bridge the pore"
            f" (width {width_nm} nm is too small for this wall; this input needs"
            f" > {(2 * half - slab) / 10:.2f} nm)"
        )
    bounds = (df.box[0], df.box[1], (z_lo_new, z_lo_new + lz_new))
    wrapped, img = wrap(pos, bounds)
    img[:, 2] = 0  # inside the box by the check above (rounding may print z = zhi)

    # ---- data file
    counts = {k: df.counts.get(k, 0) * r for k in ("atoms", "bonds", "angles", "dihedrals")}
    out_lines = [f"LAMMPS data file: {sid} (atom_style full, units real)", ""]
    out_lines += [f"{counts[k]} {k}" for k in ("atoms", "bonds", "angles")]
    if counts["dihedrals"]:
        out_lines.append(f"{counts['dihedrals']} dihedrals")
    out_lines.append("")
    out_lines += [f"{len(tm.atom)} atom types", f"{len(tm.bond)} bond types"]
    out_lines.append(f"{len(tm.angle)} angle types")
    if counts["dihedrals"]:
        out_lines.append(f"{len(tm.dihedral)} dihedral types")
    out_lines.append("")
    for ax, (blo, bhi) in zip("xyz", bounds, strict=True):
        out_lines.append(f"{BOX_FMT.format(blo)} {BOX_FMT.format(bhi)} {ax}lo {ax}hi")

    def section(header: str, lines: list[str]) -> None:
        out_lines.extend(["", header, "", *lines])

    for header, lines in coeff_sections(ff, tm):
        section(header, lines)
    raw_atoms = _rows_by_id(df.sections["Atoms"])
    lines = []
    for k in range(r):
        for loc, row in enumerate(raw_atoms):
            g = k * n_src + loc
            x, y, z = (COORD_FMT.format(v) for v in wrapped[g])
            ix, iy, iz = img[g]
            aid, mid = int(row[0]) + k * n_src, int(row[1]) + k * n_chains
            lines.append(f"{aid} {mid} {row[2]} {row[3]} {x} {y} {z} {ix} {iy} {iz}")
    section("Atoms # full", lines)
    if df.sections.get("Velocities"):
        vel = _rows_by_id(df.sections["Velocities"])
        section(
            "Velocities",
            [f"{int(v[0]) + k * n_src} {' '.join(v[1:4])}" for k in range(r) for v in vel],
        )
    for name in _TOPOLOGY:
        rows = _rows_by_id(df.sections.get(name, []))
        if not rows:
            continue
        n_rows = len(rows)
        section(
            name,
            [
                f"{int(t[0]) + k * n_rows} {t[1]} "
                + " ".join(str(int(a) + k * n_src) for a in t[2:])
                for k in range(r)
                for t in rows
            ],
        )

    # ---- manifest
    area = float(lengths[0] * lengths[1])
    slab_mass = float(masses.sum())
    rho_bulk = slab_mass / AVOGADRO / (area * slab * 1e-24)
    manifest = {k: v for k, v in copy.deepcopy(src).items() if k not in _DROP_KEYS}
    manifest["id"] = sid
    manifest["n_chains"] = n_chains * r
    manifest["box_angstrom"] = [[float(a), float(b)] for a, b in bounds]
    manifest["density_g_cm3"] = slab_mass / AVOGADRO / (area * lz_new * 1e-24)
    manifest["counts"]["total"] = {k: v * r for k, v in src["counts"]["total"].items()}
    manifest["formula"]["total"] = {k: v * r for k, v in src["formula"]["total"].items()}
    manifest["total_mass_g_mol"] = slab_mass
    manifest["sepsim_version"] = __version__
    manifest["git"] = git
    manifest["pore"] = {
        "method": "D44: bulk box enlarged along z (Hapke et al., cond-mat/9607112, method 2)",
        "nominal_width_nm": float(width_nm),
        "width_definition": "mass-equivalent: Lz_new - M / (rho_bulk * Lx * Ly)",
        "replicate_z": r,
        "wall_thickness_angstrom": float(slab),
        "lz_source_angstrom": float(lengths[2]),
        "lz_new_angstrom": float(lz_new),
        "area_angstrom2": area,
        "slab_mass_g_mol": slab_mass,
        "bulk_density_g_cm3": rho_bulk,
        "cut_z_angstrom": z_cut,
        "slab_z_extent_angstrom": [zmin, zmax],
        "window_z_angstrom": [win_lo, win_lo + slab],
        "protrusion_angstrom": [win_lo - zmin, zmax - win_lo - slab],
        "clear_gap_angstrom": float(lz_new - (zmax - zmin)),
    }
    manifest["source"] = {
        "id": src["id"],
        "manifest_sha256": sha256_file(man_path),
        "data_file": data_origin or str(data),
        "data_sha256": sha256_file(data),
    }
    sysdir = out / sid
    sysdir.mkdir(parents=True, exist_ok=True)
    (sysdir / DATA_NAME).write_text("\n".join(out_lines) + "\n", newline="\n")
    write_manifest(sysdir, manifest)
    return sysdir
