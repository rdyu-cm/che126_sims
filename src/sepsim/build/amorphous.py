"""Build an amorphous system end to end: typed chain, growth, data file and manifest.

Output goes to ``<out>/<system_id>/{data.lmp, manifest.yaml}`` with
``system_id = {polymer}_{res}_amorph_n{chains}_c{carbons}_s{seed}``. Both files are
deterministic for a given seed and code state: the manifest holds no timestamps or host
data, only the git commit and dirty flag of the sepsim source tree.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from sepsim import __version__
from sepsim.analysis.units import AVOGADRO
from sepsim.build.datafile import box_bounds, type_maps, write_data_file
from sepsim.build.growth import GrowthParams, grow_amorphous, min_nonbonded_distances
from sepsim.build.topology import formula, typed_chain
from sepsim.run import _git, sha256_file

DATA_NAME = "data.lmp"
MANIFEST_NAME = "manifest.yaml"
SOURCE_DIR = Path(__file__).resolve().parent


def system_id(polymer: str, resolution: str, n_chains: int, n_carbons: int, seed: int) -> str:
    return f"{polymer}_{resolution}_amorph_n{n_chains}_c{n_carbons}_s{seed}"


def source_git_state(exclude: Path | None = None) -> dict:
    """Commit and dirty flag of the repo holding the sepsim source.

    ``exclude`` (the output root, if inside the repo) is left out of the dirty check, so
    writing several systems into ``systems/`` doesn't mark later builds dirty.
    """
    top = _git(["rev-parse", "--show-toplevel"], SOURCE_DIR)
    commit = _git(["rev-parse", "HEAD"], SOURCE_DIR)
    if top is None or commit is None:
        return {"commit": None, "dirty": None}
    args = ["status", "--porcelain", "--", "."]
    if exclude is not None:
        try:
            rel = Path(exclude).resolve().relative_to(Path(top).resolve())
            if str(rel) != ".":
                args.append(f":(exclude){rel.as_posix()}")
        except ValueError:
            pass  # output outside the repo
    status = _git(args, Path(top))
    return {"commit": commit, "dirty": None if status is None else bool(status)}


class DirectAAiPPError(ValueError):
    """Raised when AA iPP is requested from the growth builder (decision D32)."""


AA_IPP_MESSAGE = (
    "AA iPP is not grown directly (decision D32). Build UA iPP "
    "(sepsim build amorphous --polymer ipp --res ua ...), relax it in LAMMPS, then convert "
    "it with: sepsim build ua2aa --data <relaxed UA data file> --source <UA system dir>"
)


def system_manifest(
    sid: str,
    mol,
    ff,
    n_chains: int,
    bounds,
    seed: int,
    minima: dict,
    git: dict,
    build_density: float | None = None,
    extra: dict | None = None,
) -> dict:
    """Manifest shared by every builder; ``extra`` keys (growth, source...) go last."""
    tm = type_maps(mol, ff)
    elements, chain_formula = formula(mol.types)
    per_chain = {
        "atoms": mol.n_atoms,
        "bonds": len(mol.bonds),
        "angles": len(mol.angles),
        "dihedrals": len(mol.dihedrals),
    }
    total_mass = sum(float(ff.atom_types[t]["mass"]) for t in mol.types) * n_chains
    volume = float(np.prod([hi - lo for lo, hi in bounds]))
    manifest = {
        "id": sid,
        "polymer": mol.polymer,
        "resolution": mol.resolution,
        "n_chains": n_chains,
        "n_carbons": mol.n_carbons,
        "seed": seed,
    }
    if build_density is not None:
        manifest["build_density_g_cm3"] = float(build_density)
    manifest |= {
        "box_angstrom": [[float(lo), float(hi)] for lo, hi in bounds],
        "density_g_cm3": total_mass / AVOGADRO / (volume * 1e-24),
        "counts": {
            "per_chain": per_chain,
            "total": {k: v * n_chains for k, v in per_chain.items()},
        },
        "formula": {
            "per_chain": chain_formula,
            "total": {el: k * n_chains for el, k in elements.items()},
        },
        "total_mass_g_mol": total_mass,
        "forcefield": {"name": ff.name, "file": ff.path.name, "sha256": sha256_file(ff.path)},
        "sepsim_version": __version__,
        "git": git,
        # D24/D31: LAMMPS always starts with a soft-core push-off; these are informational.
        "overlap_minima_angstrom": minima,
        "type_ids": {"atom": tm.atom, "bond": tm.bond, "angle": tm.angle, "dihedral": tm.dihedral},
        "shake_bond_types": {
            n: tm.bond[n] for n in tm.bond if ff.bond_types[n].get("constrained", False)
        },
        "lammps_styles": {k: v for k, v in ff.styles.items() if k not in ("source", "note")},
    }
    return manifest | (extra or {})


def write_manifest(sysdir: Path, manifest: dict) -> Path:
    path = sysdir / MANIFEST_NAME
    path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, default_flow_style=None), newline="\n"
    )
    return path


def build_amorphous(
    polymer: str,
    resolution: str,
    n_chains: int = 40,
    n_carbons: int = 240,
    density: float = 0.3,
    seed: int = 1,
    out: str | Path = "systems",
    params: GrowthParams | None = None,
) -> Path:
    """Grow the system and write ``data.lmp`` + ``manifest.yaml``; return the system dir."""
    if polymer == "ipp" and resolution == "aa":
        raise DirectAAiPPError(AA_IPP_MESSAGE)
    params = params or GrowthParams()
    out = Path(out)
    git = source_git_state(exclude=out)  # before writing anything
    mol, ff = typed_chain(polymer, resolution, n_carbons)
    pos, box, stats = grow_amorphous(mol, ff, n_chains, density, seed, params)
    minima = min_nonbonded_distances(mol, pos, box, n_chains, params=params)
    sid = system_id(polymer, resolution, n_chains, n_carbons, seed)
    sysdir = out / sid
    sysdir.mkdir(parents=True, exist_ok=True)
    write_data_file(sysdir / DATA_NAME, mol, ff, n_chains, pos, box, title=sid)
    growth = {"growth": {"params": params.record(mol), "stats": dict(stats)}}
    write_manifest(
        sysdir,
        system_manifest(
            sid, mol, ff, n_chains, box_bounds(box), seed, minima, git, density, growth
        ),
    )
    return sysdir
