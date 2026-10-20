"""Write and read LAMMPS data files (``atom_style full``) for grown chain systems.

The writer takes one typed ``Molecule``, its force field, the number of chains and the
unwrapped coordinates from growth. Only the atom/bond/angle/dihedral types the molecule
actually uses are emitted, numbered in force-field YAML order; every coefficient line is
commented with its type name. Coefficients come from ``sepsim.ff.params.to_lammps_real``:

* ``Pair Coeffs`` (epsilon, sigma) for force fields with a mixing rule (OPLS, TraPPE);
* ``PairIJ Coeffs`` (form, epsilon, sigma) for SDK/SPICA, which lists every cross pair;
* ``Bond Coeffs`` (K, r0), ``Angle Coeffs`` (K, theta0), ``Dihedral Coeffs`` (opls K1..K4).

Atoms are wrapped into the box and carry image flags, so ``x + i*L`` restores the
unwrapped chain. Molecule IDs are 1-based chain indices. The output is a pure function of
the inputs (fixed formatting), so a fixed seed gives identical bytes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from sepsim.build.topology import Molecule
from sepsim.ff.params import ForceField, to_lammps_real

COORD_FMT = "{:.6f}"
BOX_FMT = "{:.8f}"


def _num(x: float) -> str:
    """Compact, deterministic number formatting for coefficients (12 significant digits)."""
    return f"{float(x):.12g}"


def _used(names, order) -> list[str]:
    """Names from ``order`` (YAML order) that occur in ``names``."""
    present = set(names)
    return [n for n in order if n in present]


@dataclass
class TypeMaps:
    """1-based LAMMPS type ids keyed by FF type name, per section."""

    atom: dict[str, int]
    bond: dict[str, int]
    angle: dict[str, int]
    dihedral: dict[str, int]


def type_maps(mol: Molecule, ff: ForceField) -> TypeMaps:
    """Type ids for the types ``mol`` uses, numbered in force-field YAML order."""

    def ids(names, order):
        return {n: i + 1 for i, n in enumerate(_used(names, order))}

    return TypeMaps(
        atom=ids(mol.types, ff.atom_types),
        bond=ids(mol.bond_types, ff.bond_types),
        angle=ids(mol.angle_types, ff.angle_types),
        dihedral=ids(mol.dihedral_types, ff.dihedral_types),
    )


Box = float | tuple[tuple[float, float], tuple[float, float], tuple[float, float]]


def box_bounds(box: Box) -> tuple[tuple[float, float], ...]:
    """((xlo, xhi), (ylo, yhi), (zlo, zhi)); a scalar means the cube [0, box)^3."""
    if np.isscalar(box):
        return ((0.0, float(box)),) * 3
    bounds = tuple((float(lo), float(hi)) for lo, hi in box)
    if len(bounds) != 3 or any(hi <= lo for lo, hi in bounds):
        raise ValueError(f"bad box bounds {box!r}")
    return bounds


def wrap(pos: np.ndarray, box: Box) -> tuple[np.ndarray, np.ndarray]:
    """Wrap unwrapped coordinates into the box; return (wrapped, image flags).

    A coordinate may print as exactly ``hi`` after rounding; LAMMPS read_data remaps it.
    """
    bounds = box_bounds(box)
    lo = np.array([b[0] for b in bounds])
    length = np.array([b[1] - b[0] for b in bounds])
    img = np.floor((pos - lo) / length).astype(np.int64)
    w = np.round(pos - img * length, 6) + 0.0  # + 0.0 turns -0.0 into 0.0
    return w, img


def _pair_lines(ff: ForceField, real: dict, atom_ids: dict[str, int]) -> tuple[str, list[str]]:
    names = list(atom_ids)
    if ff.styles.get("mixing", "none") == "none":
        lines = []
        for i, a in enumerate(names):
            for b in names[i:]:
                p = real["pair"].get((a, b)) or real["pair"].get((b, a))
                if p is None:
                    raise ValueError(f"{ff.name}: no pair coefficients for {a}-{b} (no mixing)")
                lines.append(
                    f"{atom_ids[a]} {atom_ids[b]} {p['form']} {_num(p['epsilon'])} "
                    f"{_num(p['sigma'])}  # {a}-{b}"
                )
        return "PairIJ Coeffs # " + ff.styles["pair"], lines
    lines = []
    for a in names:
        p = real["pair"].get((a, a))
        if p is None:
            raise ValueError(f"{ff.name}: atom type {a} has no LJ parameters")
        lines.append(f"{atom_ids[a]} {_num(p['epsilon'])} {_num(p['sigma'])}  # {a}")
    return "Pair Coeffs # " + ff.styles["pair"], lines


def format_data_file(
    mol: Molecule,
    ff: ForceField,
    n_chains: int,
    positions: np.ndarray,
    box: Box,
    title: str = "sepsim amorphous system",
) -> str:
    """Return the LAMMPS data file text (atom_style full) for ``n_chains`` copies of ``mol``.

    ``box`` is a cube edge (box [0, L)^3) or orthogonal bounds ((xlo, xhi), ...).
    """
    nper = mol.n_atoms
    if positions.shape != (n_chains * nper, 3):
        raise ValueError(f"positions shape {positions.shape} != ({n_chains * nper}, 3)")
    real = to_lammps_real(ff)
    tm = type_maps(mol, ff)
    n_bonds = n_chains * len(mol.bonds)
    n_angles = n_chains * len(mol.angles)
    n_dihedrals = n_chains * len(mol.dihedrals)

    out = [f"LAMMPS data file: {title} (atom_style full, units real)", ""]
    out.append(f"{n_chains * nper} atoms")
    out.append(f"{n_bonds} bonds")
    out.append(f"{n_angles} angles")
    if n_dihedrals:
        out.append(f"{n_dihedrals} dihedrals")
    out.append("")
    out.append(f"{len(tm.atom)} atom types")
    out.append(f"{len(tm.bond)} bond types")
    out.append(f"{len(tm.angle)} angle types")
    if n_dihedrals:
        out.append(f"{len(tm.dihedral)} dihedral types")
    out.append("")
    for ax, (lo, hi) in zip("xyz", box_bounds(box), strict=True):
        out.append(f"{BOX_FMT.format(lo)} {BOX_FMT.format(hi)} {ax}lo {ax}hi")

    def section(header: str, lines: list[str]) -> None:
        out.extend(["", header, "", *lines])

    section(
        "Masses",
        [f"{i} {_num(real['atoms'][n]['mass'])}  # {n}" for n, i in tm.atom.items()],
    )
    section(*_pair_lines(ff, real, tm.atom))
    section(
        "Bond Coeffs # " + ff.styles["bond"],
        [
            f"{i} {_num(real['bond'][n]['K'])} {_num(real['bond'][n]['r0'])}  # {n}"
            for n, i in tm.bond.items()
        ],
    )
    section(
        "Angle Coeffs # " + ff.styles["angle"],
        [
            f"{i} {_num(real['angle'][n]['K'])} {_num(real['angle'][n]['theta0'])}  # {n}"
            for n, i in tm.angle.items()
        ],
    )
    if n_dihedrals:
        section(
            "Dihedral Coeffs # " + ff.styles["dihedral"],
            [
                f"{i} "
                + " ".join(_num(real["dihedral"][n][f"K{k}"]) for k in range(1, 5))
                + f"  # {n}"
                for n, i in tm.dihedral.items()
            ],
        )

    wrapped, img = wrap(positions, box)
    atype = [tm.atom[t] for t in mol.types]
    charge = [_num(real["atoms"][t]["charge"]) for t in mol.types]
    lines = []
    for c in range(n_chains):
        for loc in range(nper):
            g = c * nper + loc
            x, y, z = (COORD_FMT.format(v) for v in wrapped[g])
            ix, iy, iz = img[g]
            lines.append(f"{g + 1} {c + 1} {atype[loc]} {charge[loc]} {x} {y} {z} {ix} {iy} {iz}")
    section("Atoms # full", lines)

    def topo(header, entries, types, ids):
        rows, n = [], 0
        for c in range(n_chains):
            off = c * nper + 1
            for e, t in zip(entries, types, strict=True):
                n += 1
                rows.append(f"{n} {ids[t]} " + " ".join(str(a + off) for a in e))
        section(header, rows)

    topo("Bonds", mol.bonds, mol.bond_types, tm.bond)
    topo("Angles", mol.angles, mol.angle_types, tm.angle)
    if n_dihedrals:
        topo("Dihedrals", mol.dihedrals, mol.dihedral_types, tm.dihedral)
    return "\n".join(out) + "\n"


def write_data_file(path: str | Path, *args, **kwargs) -> Path:
    """Write :func:`format_data_file` output to ``path`` (bytes are deterministic)."""
    path = Path(path)
    path.write_text(format_data_file(*args, **kwargs), newline="\n")
    return path


# --------------------------------------------------------------------------- reader


@dataclass
class DataFile:
    """Parsed data file. Coefficient sections keep the raw tokens (comments in ``names``)."""

    counts: dict[str, int]
    box: tuple[tuple[float, float], ...]
    sections: dict[str, list[list[str]]] = field(default_factory=dict)
    names: dict[str, dict[int, str]] = field(default_factory=dict)
    atoms: np.ndarray | None = None  # columns: id mol type q x y z [ix iy iz]

    def sorted_atoms(self) -> np.ndarray:
        """Atom rows ordered by id, always with image columns (zeros when absent)."""
        a = self.atoms[np.argsort(self.atoms[:, 0], kind="stable")]
        if a.shape[1] == 7:
            a = np.hstack([a, np.zeros((len(a), 3))])
        if a.shape[1] != 10:
            raise ValueError(f"Atoms rows have {a.shape[1]} columns; expected atom_style full")
        return a

    def unwrapped(self) -> np.ndarray:
        """Unwrapped coordinates ordered by atom id (x + image * box length)."""
        a = self.sorted_atoms()
        lengths = np.array([hi - lo for lo, hi in self.box])
        return a[:, 4:7] + a[:, 7:10] * lengths

    def topology(self, name: str) -> np.ndarray:
        """Integer array for Bonds/Angles/Dihedrals: id, type, atom ids..."""
        rows = self.sections.get(name, [])
        if not rows:
            return np.zeros((0, 2), dtype=np.int64)
        return np.array(rows, dtype=np.int64)


_COUNT_KEYS = ("atoms", "bonds", "angles", "dihedrals", "impropers")


def read_data_file(path: str | Path) -> DataFile:
    """Minimal parser for our data files and LAMMPS ``write_data`` output (atom_style full).

    Atoms may be in any id order and with or without image flags; other sections
    (Velocities, coefficients) are kept as raw tokens. Triclinic boxes are rejected.
    """
    lines = Path(path).read_text().splitlines()
    counts: dict[str, int] = {}
    box = []
    i = 1
    while i < len(lines):
        body = lines[i].split("#", 1)[0].split()
        if not body:
            i += 1
            continue
        if body[-1] == "yz":
            raise ValueError(f"{path}: triclinic boxes are not supported")
        if body[-1] in ("xhi", "yhi", "zhi"):
            box.append((float(body[0]), float(body[1])))
        elif len(body) >= 2 and body[0].isdigit():
            counts[" ".join(body[1:])] = int(body[0])
        else:
            break
        i += 1
    df = DataFile(counts=counts, box=tuple(box))
    current = None
    for raw in lines[i:]:
        body, _, comment = raw.partition("#")
        tokens = body.split()
        if not tokens:
            continue
        if not tokens[0].lstrip("-").replace(".", "", 1).isdigit():
            current = " ".join(tokens)
            df.sections[current] = []
            df.names[current] = {}
            continue
        df.sections[current].append(tokens)
        if comment.strip():
            df.names[current][int(tokens[0])] = comment.strip()
    if "Atoms" in df.sections:
        df.atoms = np.array(df.sections["Atoms"], dtype=float)
    for key in _COUNT_KEYS:
        counts.setdefault(key, 0)
    return df
