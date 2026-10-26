"""Dry slit pores from an equilibrated bulk box (decisions D44, D48).

D48 makes the surfaces at 500 K, in two builder steps with a LAMMPS run between them:

1. **Wide pore** (``build_pore``, source = a bulk system): Hapke et al. (arXiv
   cond-mat/9607112), method 2: start from an equilibrated periodic bulk and enlarge
   the box along z, which opens two free surfaces. The wall is the source box (the
   500 K ``prep/hold.data``, or a D47 extension snapshot), optionally replicated
   ``replicate_z`` times along z first (thick-wall check):

   * The data file is validated against the source ``manifest.yaml`` (atom, bond,
     angle and dihedral counts; molecule ids; per-atom types from ``type_ids``).
   * Each molecule is made whole: its first atom is unwrapped with its image flags and
     every other atom is placed along the bond graph by minimum image.
   * The slab is cut open at a z plane ``z_cut``, and each molecule is shifted by whole
     slab periods so it sticks out of the window ``[z_cut, z_cut + Lz_slab)`` as little
     as possible; the plane giving the most compact slab is kept (``place_molecules``).
     Chains crossing the cut still stick out of the window, so the surfaces are rough
     and the outermost atoms lie beyond it. If they would reach across the pore (atoms
     outside the new box), the build fails.
   * The box keeps x and y; ``Lz_new = Lz_slab + width``, and the slab's centre of mass
     is put at the box centre. Since the slab keeps all its mass, ``width`` is the
     mass-equivalent width ``Lz_new - M / (rho_src * A)`` with ``rho_src`` the source
     box density (500 K). Id: ``_amorph_`` -> ``_pore500k_w<width>nm[_z<k>]_``.

   The wide pore is then relaxed at 500 K with the box fixed (``sepsim render
   pore_relax``), which lets the protruding chains retract.

2. **Narrow pore** (``narrow_pore``, source = a wide pore system, data = its relaxed
   ``pore_relax/relaxed.data``): molecules made whole, the slab re-centred (the most
   compact placement over the periodic z), x and y kept (the 500 K box), and
   ``Lz_new = M / (rho_bulk(25 C) * A(25 C)) + width``: the nominal width is defined at
   25 C, where Lz stays fixed for the rest of the pore run. ``A(T)`` follows the bulk
   thermal expansion (rule D48, ``lateral_lengths``):
   ``L(T) = L_src * (rho_bulk(T_src) / rho_bulk(T))^(1/3)`` for x and y, with
   ``rho_bulk(T)`` read from the same bulk system's runs (``bulk_density_table``).
   The table is stored in the manifest, where the ``pore`` deck reads it. Id:
   ``_pore500k_w<w>nm`` -> ``_pore_w<width>nm`` (``pe_cg_pore_w3nm_n40_c240_s1``).

Atom, molecule and topology ids, types, charges and velocities are carried over
unchanged (replica k adds k times the source counts to every id); the coefficient
sections are rewritten from the force-field YAML, as in every other system, so the
decks' ``read_data ... nocoeff`` and ``_ff`` coefficient lines apply as they are.
Output: ``<out>/<id>/{data.lmp, manifest.yaml}``; deterministic for a given input.
"""

from __future__ import annotations

import copy
import re
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
T_SOURCE_K = 500.0  # D48: the wide pore is cut from the 500 K bulk box
T_NOMINAL_K = 298.15  # D48: the nominal pore width is defined at 25 C
_TOPOLOGY = ("Bonds", "Angles", "Dihedrals", "Impropers")
# Source-manifest keys describing how the bulk box was made; the pore records its source.
_DROP_KEYS = ("build_density_g_cm3", "overlap_minima_angstrom", "growth", "conversion", "source")
_WIDE_TAG = re.compile(r"_pore500k_w[0-9p]+nm")


class PoreError(ValueError):
    """Raised when the bulk input does not match its manifest or cannot be opened."""


def _width_label(width_nm: float) -> str:
    """3 -> '3nm', 2.5 -> '2p5nm'."""
    return f"{width_nm:g}nm".replace(".", "p")


def pore_id(source_id: str, width_nm: float, replicate_z: int = 1) -> str:
    """Wide 500 K pore id: ``pe_cg_amorph_n40_c240_s1`` -> ``pe_cg_pore500k_w10nm_n40_c240_s1``
    (``_z2`` after the width if replicated)."""
    if "_amorph_" not in source_id:
        raise PoreError(f"source id {source_id!r} is not an amorphous bulk system")
    tag = f"_pore500k_w{_width_label(width_nm)}" + (f"_z{replicate_z}" if replicate_z > 1 else "")
    return source_id.replace("_amorph_", tag + "_", 1)


def narrow_id(wide_id: str, width_nm: float) -> str:
    """Narrow pore id: ``pe_cg_pore500k_w10nm_z2_...`` -> ``pe_cg_pore_w3nm_z2_...``."""
    if not _WIDE_TAG.search(wide_id):
        raise PoreError(f"source id {wide_id!r} is not a wide 500 K pore (_pore500k_w...)")
    return _WIDE_TAG.sub(f"_pore_w{_width_label(width_nm)}", wide_id, count=1)


# --------------------------------------------------------------------------- bulk densities


def _run_files(run_dir: Path) -> tuple[Path, Path]:
    from sepsim.progress import LOG_NAME, find_deck, load_json
    from sepsim.run import MANIFEST_NAME as RUN_MANIFEST

    deck = find_deck(run_dir, load_json(run_dir / RUN_MANIFEST))
    log = run_dir / LOG_NAME
    if deck is None or not log.is_file():
        raise PoreError(f"{run_dir}: needs its deck (in.*) and {LOG_NAME}")
    return deck, log


def _provenance(run_dir: Path, deck: Path, log: Path, what: str) -> dict:
    return {
        "run_dir": str(run_dir),
        "deck": deck.name,
        "deck_sha256": sha256_file(deck),
        "log_sha256": sha256_file(log),
        "segments": what,
    }


def bulk_density_table(hold_dir: str | Path, cool_dir: str | Path, sweep_dir: str | Path) -> dict:
    """Bulk densities for the D48 lateral rule, from the bulk system's own runs.

    ``hold_dir``: the run holding the 500 K hold the wide pore was cut from (``prep``,
    or ``extend`` for a D47 snapshot; a cancelled extension counts up to its last
    thermo row); ``cool_dir``: the step-cool (``prep`` or ``cool``); ``sweep_dir``: the
    heating sweep. Segments are parsed with ``sepsim.progress`` (second-half mean of
    each NPT segment). Cooling points are the step-cool stages plus the hold at
    ``t_source_k``; heating points are the sweep segments, the latest per temperature
    (so a hold wins over the step before it, as in the monitor's hysteresis table).
    """
    from sepsim.progress import segments_for

    out: dict = {"sources": {}}
    hold_dir, cool_dir, sweep_dir = Path(hold_dir), Path(cool_dir), Path(sweep_dir)

    deck, log = _run_files(hold_dir)
    hold = next(
        (
            r
            for r in segments_for(hold_dir, partial=True) or []
            if {"hold.dcd", "hold_ext.dcd"} & set(r["dcd"]) and r["state"] != "pending"
        ),
        None,
    )
    rho = ((hold or {}).get("stats") or {}).get("density")
    if hold is None or rho is None or hold["ensemble"] != "npt":
        raise PoreError(f"{hold_dir}: no NPT hold segment (hold.dcd/hold_ext.dcd) with stats")
    out["t_source_k"] = float(hold["t_target_k"])
    out["rho_source_g_cm3"] = float(rho["mean"])
    out["sources"]["hold"] = _provenance(hold_dir, deck, log, f"{hold['index']}: {hold['name']}")

    deck, log = _run_files(cool_dir)
    cool = [
        r
        for r in segments_for(cool_dir) or []
        if r.get("cool_step") is not None and r["state"] == "done" and r["ensemble"] == "npt"
    ]
    if not cool or any(not (r.get("stats") or {}).get("density") for r in cool):
        raise PoreError(f"{cool_dir}: no completed NPT step-cool stages with density stats")
    pts = {out["t_source_k"]: out["rho_source_g_cm3"]}
    pts |= {float(r["t_target_k"]): float(r["stats"]["density"]["mean"]) for r in cool}
    out["cooling"] = [[t, pts[t]] for t in sorted(pts)]
    out["sources"]["cool"] = _provenance(
        cool_dir, deck, log, f"{len(cool)} step-cool stages + the hold"
    )

    deck, log = _run_files(sweep_dir)
    heat: dict[float, float] = {}
    n = 0
    for r in segments_for(sweep_dir) or []:
        rho = (r.get("stats") or {}).get("density")
        md = r.get("sweep_kind") and not r.get("vdos") and r["ensemble"] == "npt"
        if md and r["state"] == "done" and rho:
            heat[float(r["t_target_k"])] = float(rho["mean"])  # latest per T: holds win
            n += 1
    if not heat:
        raise PoreError(f"{sweep_dir}: no completed NPT sweep segments with density stats")
    out["heating"] = [[t, heat[t]] for t in sorted(heat)]
    out["sources"]["sweep"] = _provenance(sweep_dir, deck, log, f"{n} sweep segments")
    return out


def bulk_density(lateral: dict, branch: str, t_k: float) -> float:
    """rho_bulk(T) on the ``cooling`` or ``heating`` branch, linear in T (no extrapolation)."""
    pts = np.array(lateral[branch], dtype=float)
    lo, hi = pts[0, 0], pts[-1, 0]
    if not lo - 1e-6 <= t_k <= hi + 1e-6:
        raise PoreError(
            f"{t_k:g} K is outside the bulk {branch} densities ({lo:g}-{hi:g} K): no extrapolation"
        )
    return float(np.interp(t_k, pts[:, 0], pts[:, 1]))


def lateral_lengths(lateral: dict, branch: str, t_k: float) -> np.ndarray:
    """D48: box x, y lengths at ``t_k``: L_src * (rho_bulk(T_src) / rho_bulk(T))^(1/3)."""
    ratio = lateral["rho_source_g_cm3"] / bulk_density(lateral, branch, t_k)
    return np.asarray(lateral["l_source_angstrom"], dtype=float) * ratio ** (1.0 / 3.0)


# --------------------------------------------------------------------------- geometry


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


def _read_input(data: Path, src: dict):
    """Data file checked against the source manifest: (df, atoms by id, masses, ff, type maps)."""
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
    ff = load_forcefield(FORCEFIELD_DIR / src["forcefield"]["file"])
    tm = TypeMaps(
        atom=ids["atom"], bond=ids["bond"], angle=ids["angle"], dihedral=ids.get("dihedral") or {}
    )
    mass_of = {i: float(ff.atom_types[n]["mass"]) for n, i in ids["atom"].items()}
    masses = np.array([mass_of[int(t)] for t in atoms[:, 2]])
    return df, atoms, masses, ff, tm


def _data_text(sid, df, ff, tm, bounds, wrapped, img, r: int, n_chains: int) -> str:
    """Data file of ``r`` z-replicas of ``df`` at the given (wrapped) coordinates."""
    n_src = len(df.sections["Atoms"])
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
    return "\n".join(out_lines) + "\n"


def _centre_and_check(pos, masses, z_lo, lz_new, slab_a: float, width_nm: float):
    """Put the slab's mass centre at the box centre; fail if any atom leaves the box.

    ``slab_a`` is the slab thickness that ``lz_new`` adds the width to (for the
    smallest-width hint). Returns (shift applied, zmin, zmax).
    """
    com = float((masses * pos[:, 2]).sum() / masses.sum())
    dz = z_lo + 0.5 * lz_new - com
    pos[:, 2] += dz
    zmin, zmax = float(pos[:, 2].min()), float(pos[:, 2].max())
    if zmin < z_lo or zmax >= z_lo + lz_new:
        # placement relative to the mass centre does not depend on the width
        half = max(z_lo + 0.5 * lz_new - zmin, zmax - z_lo - 0.5 * lz_new)
        raise PoreError(
            f"slab atoms span z {zmin:.2f}..{zmax:.2f} A, beyond the new box"
            f" {z_lo:.2f}..{z_lo + lz_new:.2f} A: chains would bridge the pore"
            f" (width {width_nm} nm is too small for this wall; this input needs"
            f" > {(2 * half - slab_a) / 10:.2f} nm)"
        )
    return dz, zmin, zmax


def _write(out: Path, sid: str, text: str, manifest: dict) -> Path:
    sysdir = out / sid
    sysdir.mkdir(parents=True, exist_ok=True)
    (sysdir / DATA_NAME).write_text(text, newline="\n")
    write_manifest(sysdir, manifest)
    return sysdir


def _base_manifest(src: dict, sid: str, bounds, mass: float, git: dict, r: int = 1) -> dict:
    manifest = {k: v for k, v in copy.deepcopy(src).items() if k not in _DROP_KEYS}
    lengths = [b - a for a, b in bounds]
    manifest["id"] = sid
    manifest["n_chains"] = int(src["n_chains"]) * r
    manifest["box_angstrom"] = [[float(a), float(b)] for a, b in bounds]
    manifest["density_g_cm3"] = mass / AVOGADRO / (float(np.prod(lengths)) * 1e-24)
    manifest["counts"]["total"] = {k: v * r for k, v in src["counts"]["total"].items()}
    manifest["formula"]["total"] = {k: v * r for k, v in src["formula"]["total"].items()}
    manifest["total_mass_g_mol"] = mass
    manifest["sepsim_version"] = __version__
    manifest["git"] = git
    return manifest


def _load_source(source: Path) -> tuple[Path, dict]:
    man_path = source / MANIFEST_NAME
    if not man_path.is_file():
        raise PoreError(f"source manifest not found: {man_path}")
    return man_path, yaml.safe_load(man_path.read_text())


# --------------------------------------------------------------------------- builders


def build_pore(
    data: str | Path,
    source: str | Path,
    width_nm: float,
    replicate_z: int = 1,
    out: str | Path = "systems",
    data_origin: str | None = None,
) -> Path:
    """Open a wide slit pore (D48 step 1) of width ``width_nm`` in the 500 K bulk box ``data``.

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
    man_path, src = _load_source(source)
    if "pore" in src:
        raise PoreError(f"{man_path}: source is already a pore system")
    sid = pore_id(src["id"], width_nm, replicate_z)
    n_chains = int(src["n_chains"])
    df, atoms, masses, ff, tm = _read_input(data, src)

    # ---- whole molecules, replicated along z
    lo = np.array([b[0] for b in df.box])
    lengths = np.array([hi - lo_ for lo_, hi in df.box])
    bonds = df.topology("Bonds")[:, 2:4]
    pos = whole_molecules(atoms, bonds, lengths)
    r = replicate_z
    pos = np.vstack([pos + [0.0, 0.0, k * lengths[2]] for k in range(r)])
    masses = np.tile(masses, r)
    mol_ids = np.concatenate([atoms[:, 1].astype(np.int64) + k * n_chains for k in range(r)])
    slab = float(r * lengths[2])  # wall thickness = slab period before opening, Angstrom

    # ---- cut plane, molecules into the window [z_cut, z_cut + slab), mass centre at box centre
    z_cut, shift = place_molecules(pos[:, 2], mol_ids, masses, float(lo[2]), slab)
    pos[:, 2] += shift
    lz_new = slab + 10.0 * float(width_nm)
    z_lo_new = float(lo[2])
    dz, zmin, zmax = _centre_and_check(pos, masses, z_lo_new, lz_new, slab, width_nm)
    win_lo = z_cut + dz  # the window [z_cut, z_cut + slab), moved
    bounds = (df.box[0], df.box[1], (z_lo_new, z_lo_new + lz_new))
    wrapped, img = wrap(pos, bounds)
    img[:, 2] = 0  # inside the box by the check above (rounding may print z = zhi)
    text = _data_text(sid, df, ff, tm, bounds, wrapped, img, r, n_chains)

    # ---- manifest
    area = float(lengths[0] * lengths[1])
    slab_mass = float(masses.sum())
    rho_bulk = slab_mass / AVOGADRO / (area * slab * 1e-24)
    manifest = _base_manifest(src, sid, bounds, slab_mass, git, r)
    manifest["pore"] = {
        "kind": "wide",
        "method": (
            "D48 step 1: 500 K bulk box enlarged along z (Hapke et al., cond-mat/9607112,"
            " method 2); relax with pore_relax, then narrow"
        ),
        "temperature_k": T_SOURCE_K,
        "nominal_width_nm": float(width_nm),
        "width_definition": "mass-equivalent at the source density: Lz_new - M / (rho_src * Lx * Ly)",
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
    return _write(out, sid, text, manifest)


def narrow_pore(
    data: str | Path,
    source: str | Path,
    width_nm: float,
    bulk: dict,
    out: str | Path = "systems",
    data_origin: str | None = None,
) -> Path:
    """Narrow a relaxed wide pore (D48 step 2) to the nominal 25 C width ``width_nm``.

    ``source`` is the wide pore system directory, ``data`` its relaxed state (the
    ``pore_relax`` run's ``relaxed.data``, box x and y unchanged), ``bulk`` the
    :func:`bulk_density_table` of the bulk system it was cut from. Returns the new
    system directory.
    """
    data, source, out = Path(data), Path(source), Path(out)
    if width_nm <= 0:
        raise PoreError(f"pore width must be > 0 nm, got {width_nm}")
    git = source_git_state(exclude=out)
    man_path, src = _load_source(source)
    wide = src.get("pore") or {}
    if wide.get("kind") != "wide":
        raise PoreError(f"{man_path}: source is not a wide 500 K pore (pore.kind: wide)")
    sid = narrow_id(src["id"], width_nm)
    df, atoms, masses, ff, tm = _read_input(data, src)
    lo = np.array([b[0] for b in df.box])
    lengths = np.array([hi - lo_ for lo_, hi in df.box])
    src_box = np.array(src["box_angstrom"], dtype=float)
    if not np.allclose(lengths[:2], src_box[:2, 1] - src_box[:2, 0], atol=1e-4):
        raise PoreError(
            f"{data}: box x, y {lengths[0]:.4f} x {lengths[1]:.4f} A differ from the wide"
            " pore's: give the fixed-box pore_relax output"
        )
    if abs(bulk["t_source_k"] - wide["temperature_k"]) > 1e-6:
        raise PoreError(
            f"bulk hold at {bulk['t_source_k']:g} K, wide pore made at {wide['temperature_k']:g} K"
        )
    lateral = copy.deepcopy(bulk)
    lateral["l_source_angstrom"] = [float(v) for v in src_box[:2, 1] - src_box[:2, 0]]

    # ---- whole molecules, the most compact slab over the periodic z, mass centre at box centre
    pos = whole_molecules(atoms, df.topology("Bonds")[:, 2:4], lengths)
    mol_ids = atoms[:, 1].astype(np.int64)
    z_cut, shift = place_molecules(pos[:, 2], mol_ids, masses, float(lo[2]), float(lengths[2]))
    pos[:, 2] += shift
    mass = float(masses.sum())
    area = float(lengths[0] * lengths[1])
    l25 = lateral_lengths(lateral, "heating", T_NOMINAL_K)
    rho25 = bulk_density(lateral, "heating", T_NOMINAL_K)
    rho_src = float(lateral["rho_source_g_cm3"])
    t25 = mass / AVOGADRO / (rho25 * float(l25[0] * l25[1]) * 1e-24)  # slab thickness at 25 C
    t_src = mass / AVOGADRO / (rho_src * area * 1e-24)  # ... and at 500 K in this box
    lz_new = t25 + 10.0 * float(width_nm)
    z_lo_new = float(lo[2])
    _, zmin, zmax = _centre_and_check(pos, masses, z_lo_new, lz_new, t25, width_nm)
    centre = z_lo_new + 0.5 * lz_new
    win = [centre - 0.5 * t_src, centre + 0.5 * t_src]
    bounds = (df.box[0], df.box[1], (z_lo_new, z_lo_new + lz_new))
    wrapped, img = wrap(pos, bounds)
    img[:, 2] = 0
    text = _data_text(sid, df, ff, tm, bounds, wrapped, img, 1, int(src["n_chains"]))

    manifest = _base_manifest(src, sid, bounds, mass, git)
    manifest["pore"] = {
        "kind": "narrow",
        "method": (
            "D48 step 2: relaxed 500 K wide pore re-centred (whole molecules), x, y kept,"
            " Lz = M / (rho_bulk(25 C) A(25 C)) + width; Lz fixed in the pore run"
        ),
        "temperature_k": wide["temperature_k"],
        "nominal_width_nm": float(width_nm),
        "width_definition": (
            "at 25 C: Lz - M / (rho_bulk(298.15 K) * A(298.15 K)), A from the D48 lateral rule"
            " (heating branch)"
        ),
        "width_500k_nm": (lz_new - t_src) / 10.0,
        "replicate_z": int(wide["replicate_z"]),
        "wall_thickness_angstrom": t25,
        "wall_thickness_500k_angstrom": t_src,
        "lz_source_angstrom": float(lengths[2]),
        "lz_new_angstrom": float(lz_new),
        "area_angstrom2": area,
        "area_25c_angstrom2": float(l25[0] * l25[1]),
        "slab_mass_g_mol": mass,
        "bulk_density_g_cm3": rho25,
        "bulk_density_500k_g_cm3": rho_src,
        "cut_z_angstrom": z_cut,
        "slab_z_extent_angstrom": [zmin, zmax],
        "window_z_angstrom": win,  # the 500 K mass-equivalent slab around the mass centre
        "protrusion_angstrom": [win[0] - zmin, zmax - win[1]],
        "clear_gap_angstrom": float(lz_new - (zmax - zmin)),
        "lateral": lateral,
    }
    manifest["source"] = {
        "id": src["id"],
        "manifest_sha256": sha256_file(man_path),
        "data_file": data_origin or str(data),
        "data_sha256": sha256_file(data),
        "source": src["source"],  # the bulk system the wide pore was cut from
    }
    return _write(out, sid, text, manifest)
