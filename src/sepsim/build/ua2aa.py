"""Convert a (relaxed) united-atom PE/iPP box to all-atom OPLS/2020 by adding hydrogens.

Decision D32: AA iPP is not grown directly. UA iPP is grown, relaxed in LAMMPS (push-off,
minimization, short MD), written with ``write_data``, and converted here:

* The input data file is validated against the source UA ``manifest.yaml`` (polymer,
  resolution, chain count/length, atom count, molecule ids, per-atom type names via the
  manifest's ``type_ids``). Any mismatch raises :class:`ConversionError`.
* Each chain is made whole: its first atom is unwrapped with its image flags and every
  other atom is placed along the bond tree by minimum image.
* UA sites map to AA carbons through an explicit index map built from the two
  ``build_chain`` molecules (same backbone/substituent order); carbons keep the UA positions.
* Hydrogens are placed geometrically with FF C-H lengths and H-C-X angles: the methine H
  along the UA explicit-H direction (so tacticity is preserved by construction), CH2 H's
  on the bisector-plane construction, methyl H's staggered against a heavy neighbour.

Output: ``<out>/<polymer>_aa_amorph_n{chains}_c{carbons}_s{seed}_from_ua/{data.lmp,
manifest.yaml}``; deterministic for a given input.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from sepsim.build.amorphous import (
    DATA_NAME,
    MANIFEST_NAME,
    source_git_state,
    system_manifest,
    write_manifest,
)
from sepsim.build.datafile import read_data_file, wrap, write_data_file
from sepsim.build.growth import (
    _unit,
    bisector_pair,
    bonded_lookup,
    chirality_signs,
    min_nonbonded_distances,
    staggered_hs,
)
from sepsim.build.topology import Molecule, build_chain, typed_chain
from sepsim.run import sha256_file


class ConversionError(ValueError):
    """Raised when the UA input does not match its source manifest or cannot be converted."""


def converted_id(polymer: str, n_chains: int, n_carbons: int, seed: int) -> str:
    return f"{polymer}_aa_amorph_n{n_chains}_c{n_carbons}_s{seed}_from_ua"


def ua_to_aa_index_map(ua: Molecule, aa: Molecule) -> dict[int, int]:
    """UA atom index -> AA atom index: backbone by position, then substituents in order.

    Both molecules come from ``build_chain`` with the same backbone and heavy-first
    substituent order, so the UA methyl maps to the AA methyl and the explicit UA methine H
    to the AA methine H.
    """
    out: dict[int, int] = {}
    for i in range(len(ua.backbone)):
        out.update(zip([ua.backbone[i], *ua.subs[i]], [aa.backbone[i], *aa.subs[i]]))
    return out


def _whole_chain(mol: Molecule, wrapped: np.ndarray, images: np.ndarray, lengths) -> np.ndarray:
    """Unwrap one chain: atom 0 by its image flags, the rest along bonds by minimum image."""
    pos = np.empty_like(wrapped)
    pos[0] = wrapped[0] + images[0] * lengths
    nbr = mol.neighbors()
    seen = {0}
    stack = [0]
    while stack:
        a = stack.pop()
        for b in sorted(nbr[a]):
            if b in seen:
                continue
            d = wrapped[b] - wrapped[a]
            pos[b] = pos[a] + d - lengths * np.round(d / lengths)
            seen.add(b)
            stack.append(b)
    return pos


def place_hydrogens(aa: Molecule, ff, pos: np.ndarray, known: np.ndarray) -> np.ndarray:
    """Fill every AA hydrogen not marked ``known``; ``pos`` holds one chain (AA indices)."""
    pos = pos.copy()
    is_h = aa.is_hydrogen()
    nbr = aa.neighbors()
    r0, th0 = bonded_lookup(aa, ff)
    for c in range(aa.n_atoms):
        if is_h[c]:
            continue
        heavy = sorted(x for x in nbr[c] if not is_h[x])
        todo = sorted(x for x in nbr[c] if is_h[x] and not known[x])
        if not todo:
            continue
        if len(heavy) == 2 and len(todo) == 2:  # CH2
            a, b = pos[heavy[0]], pos[heavy[1]]
            dirs = bisector_pair(pos[c], a, b, th0[(todo[0], c, todo[1])], 1.0)
            for h, d in zip(todo, dirs, strict=True):
                pos[h] = pos[c] + r0[(c, h)] * d
        elif len(heavy) == 1 and len(todo) == 3:  # CH3, staggered against a neighbour
            nb = heavy[0]
            ref = min(x for x in nbr[nb] if x != c and not is_h[x])
            r, th = r0[(c, todo[0])], th0[(todo[0], c, nb)]
            pos[todo] = staggered_hs(pos[ref], pos[nb], pos[c], r, th)
        else:
            raise ConversionError(
                f"no H placement rule for atom {c} ({aa.types[c]}): "
                f"{len(heavy)} heavy neighbours, {len(todo)} H to place"
            )
    return pos


def convert_ua_to_aa(data: str | Path, source: str | Path, out: str | Path = "systems") -> Path:
    """Convert the UA data file ``data`` (validated against ``source``) and write the AA system."""
    data, source, out = Path(data), Path(source), Path(out)
    git = source_git_state(exclude=out)
    man_path = source / MANIFEST_NAME
    if not man_path.is_file():
        raise ConversionError(f"source manifest not found: {man_path}")
    src = yaml.safe_load(man_path.read_text())
    if src.get("resolution") != "ua":
        raise ConversionError(f"source manifest resolution is {src.get('resolution')!r}, not 'ua'")
    polymer, n_chains, n_carbons = src["polymer"], int(src["n_chains"]), int(src["n_carbons"])
    ua = build_chain(polymer, "ua", n_carbons)
    aa, ff = typed_chain(polymer, "aa", n_carbons)
    nper = ua.n_atoms

    df = read_data_file(data)
    if len(df.box) != 3:
        raise ConversionError(f"{data}: box bounds not found")
    atoms = df.sorted_atoms()
    if len(atoms) != n_chains * nper or df.counts.get("atoms") != len(atoms):
        raise ConversionError(
            f"{data}: {len(atoms)} atoms (header {df.counts.get('atoms')}), "
            f"source expects {n_chains} x {nper} = {n_chains * nper}"
        )
    if not np.array_equal(atoms[:, 0].astype(np.int64), np.arange(1, len(atoms) + 1)):
        raise ConversionError(f"{data}: atom ids are not 1..{len(atoms)}")
    mol_ids = atoms[:, 1].astype(np.int64)
    if not np.array_equal(mol_ids, np.repeat(np.arange(1, n_chains + 1), nper)):
        raise ConversionError(f"{data}: molecule ids do not match {n_chains} chains of {nper}")
    type_ids = src["type_ids"]["atom"]
    expected = np.tile([type_ids[t] for t in ua.types], n_chains)
    if not np.array_equal(atoms[:, 2].astype(np.int64), expected):
        raise ConversionError(f"{data}: atom types do not match the source manifest type_ids")

    lengths = np.array([hi - lo for lo, hi in df.box])
    ua_is_h = ua.is_hydrogen()
    index = ua_to_aa_index_map(ua, aa)
    carbons = [(u, a) for u, a in index.items() if not ua_is_h[u]]
    ua_c, aa_c = (np.array(x) for x in zip(*carbons, strict=True))
    # explicit methine H -> AA H along the same direction: (UA H, AA H, UA C, AA C)
    ua_nbr = ua.neighbors()
    methine_h = [(u, index[u], ua_nbr[u][0], index[ua_nbr[u][0]]) for u in index if ua_is_h[u]]
    known = np.zeros(aa.n_atoms, dtype=bool)
    known[aa_c] = True
    known[[a for _, a, _, _ in methine_h]] = True
    r0, _ = bonded_lookup(aa, ff)
    out_pos = np.empty((n_chains * aa.n_atoms, 3))
    for c in range(n_chains):
        rows = atoms[c * nper : (c + 1) * nper]
        upos = _whole_chain(ua, rows[:, 4:7], rows[:, 7:10], lengths)
        apos = np.zeros((aa.n_atoms, 3))
        apos[aa_c] = upos[ua_c]
        for u, a, cu, ca in methine_h:
            apos[a] = apos[ca] + r0[(ca, a)] * _unit(upos[u] - upos[cu])
        apos = place_hydrogens(aa, ff, apos, known)
        if chirality_signs(aa, apos) != chirality_signs(ua, upos):
            raise ConversionError(f"chain {c}: AA chirality differs from UA")
        out_pos[c * aa.n_atoms : (c + 1) * aa.n_atoms] = apos

    # Minima from the coordinates as written, so they depend only on the output.
    written, _ = wrap(out_pos, df.box)
    lo = np.array([b[0] for b in df.box])
    minima = min_nonbonded_distances(aa, written - lo, lengths, n_chains)
    seed = int(src["seed"])
    sid = converted_id(polymer, n_chains, n_carbons, seed)
    sysdir = out / sid
    sysdir.mkdir(parents=True, exist_ok=True)
    write_data_file(sysdir / DATA_NAME, aa, ff, n_chains, out_pos, df.box, title=sid)
    extra = {
        "conversion": {
            "method": "ua2aa (D32): carbons at UA positions; H placed geometrically",
            "methine_h": "along UA explicit C-H, AA C-H length",
            "methylene_h": "bisector plane, H-C-H theta0",
            "methyl_h": "staggered (60/180/300) against lowest-index heavy neighbour",
        },
        "source": {
            "id": src["id"],
            "manifest_sha256": sha256_file(man_path),
            "data_file": data.name,
            "data_sha256": sha256_file(data),
        },
    }
    manifest = system_manifest(sid, aa, ff, n_chains, df.box, seed, minima, git, extra=extra)
    write_manifest(sysdir, manifest)
    return sysdir
