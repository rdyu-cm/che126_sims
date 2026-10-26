"""Replicated bulk box for the CG finite-size check (decision D50).

``build_replicate`` repeats a bulk data file (LAMMPS ``write_data``, e.g. the 500 K
``prep/hold.data``) over an ``nx x ny x nz`` grid of box images and writes a new bulk
system. Molecules are made whole first (``pore.whole_molecules``: first atom unwrapped
with its image flags, the rest placed along the bonds by minimum image), each replica is
shifted by its image vector, and the result is wrapped into the enlarged box with image
flags, so every molecule stays whole across the replica seams. Atom, molecule and
topology ids are offset per replica (replica k adds k times the source counts, x
fastest, as in the pore builder's ``replicate_z``); types, charges and velocities are
kept; coefficient sections are rewritten from the force-field YAML, so the decks'
``read_data ... nocoeff`` and ``_ff`` lines apply unchanged.

The replica images are copies, so they stay correlated until the box is decorrelated
(D50: a 500 K ``extend`` run before the wide pore is cut). Id:
``pe_cg_amorph_n40_c240_s1`` -> ``pe_cg_amorph_n320_c240_s1_rep222``.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from sepsim.build.amorphous import source_git_state
from sepsim.build.datafile import wrap
from sepsim.build.pore import (
    PoreError,
    _base_manifest,
    _data_text,
    _load_source,
    _read_input,
    _write,
    replicate,
    whole_molecules,
)
from sepsim.run import sha256_file

_N_TAG = re.compile(r"_n(\d+)_")


class ReplicateError(PoreError):
    """Raised when the bulk input cannot be replicated."""


def replicate_id(source_id: str, n_chains: int, n: tuple[int, int, int]) -> str:
    """``pe_cg_amorph_n40_c240_s1``, (2, 2, 2) -> ``pe_cg_amorph_n320_c240_s1_rep222``."""
    if "_amorph_" not in source_id or not _N_TAG.search(source_id):
        raise ReplicateError(f"source id {source_id!r} is not an amorphous bulk system (_n<N>_)")
    if "_rep" in source_id:
        raise ReplicateError(f"source id {source_id!r} is already replicated")
    total = int(n_chains) * int(np.prod(n))
    return _N_TAG.sub(f"_n{total}_", source_id, count=1) + "_rep" + "".join(str(v) for v in n)


def max_bond_length(pos: np.ndarray, bonds: np.ndarray) -> float:
    """Longest bond in coordinates ``pos`` (row k = atom id k + 1; ``bonds``: atom id pairs)."""
    b = np.asarray(bonds, dtype=np.int64) - 1
    return float(np.linalg.norm(pos[b[:, 0]] - pos[b[:, 1]], axis=1).max()) if len(b) else 0.0


def build_replicate(
    data: str | Path,
    source: str | Path,
    n: tuple[int, int, int] = (2, 2, 2),
    out: str | Path = "systems",
    data_origin: str | None = None,
) -> Path:
    """Replicate the bulk box ``data`` (validated by the ``source`` system's manifest)
    ``nx x ny x nz`` times; returns the new system directory."""
    data, source, out = Path(data), Path(source), Path(out)
    n = tuple(int(v) for v in n)
    if len(n) != 3 or any(not 1 <= v <= 9 for v in n):
        raise ReplicateError(f"replicate factors must be three integers in 1..9, got {n}")
    if n == (1, 1, 1):
        raise ReplicateError("replicate factors 1 1 1: nothing to replicate")
    git = source_git_state(exclude=out)
    man_path, src = _load_source(source)
    if "pore" in src:
        raise ReplicateError(f"{man_path}: source is a pore system, not a bulk box")
    if "replicate" in src:
        raise ReplicateError(f"{man_path}: source is already replicated")
    n_chains = int(src["n_chains"])
    sid = replicate_id(src["id"], n_chains, n)
    df, atoms, masses, ff, tm = _read_input(data, src)
    r = int(np.prod(n))

    lo = np.array([b[0] for b in df.box])
    lengths = np.array([hi - lo_ for lo_, hi in df.box])
    bonds = df.topology("Bonds")[:, 2:4]
    pos = replicate(whole_molecules(atoms, bonds, lengths), lengths, n)
    bounds = tuple((float(a), float(a + k * L)) for a, k, L in zip(lo, n, lengths, strict=True))
    wrapped, img = wrap(pos, bounds)
    # whole across the seams: every bond, unwrapped with the new image flags, stays short
    new_len = np.array([b - a for a, b in bounds])
    rep_bonds = np.vstack([bonds + k * len(atoms) for k in range(r)])
    longest = max_bond_length(wrapped + img * new_len, rep_bonds)
    if longest > 0.5 * float(lengths.min()):
        raise ReplicateError(
            f"a bond of {longest:.2f} A after replication (> half the source box): molecules"
            " are not whole"
        )
    text = _data_text(sid, df, ff, tm, bounds, wrapped, img, r, n_chains)

    mass = float(masses.sum()) * r
    manifest = _base_manifest(src, sid, bounds, mass, git, r)
    manifest["replicate"] = {
        "factors": list(n),
        "source_id": src["id"],
        "source_box_angstrom": [[float(a), float(b)] for a, b in df.box],
        "max_bond_angstrom": longest,
        "correlated": (
            "the replica images are copies of one box and stay correlated until"
            " decorrelated (D50: a 500 K extend run before any pore is cut)"
        ),
    }
    manifest["source"] = {
        "id": src["id"],
        "manifest_sha256": sha256_file(man_path),
        "data_file": data_origin or str(data),
        "data_sha256": sha256_file(data),
    }
    return _write(out, sid, text, manifest)
