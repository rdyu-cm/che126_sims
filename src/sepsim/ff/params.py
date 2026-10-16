"""Load force-field parameter YAMLs and convert them to LAMMPS real-unit coefficients.

The YAML files live in ``<repo>/forcefields``. Each file declares a ``convention``:

* ``lammps_real``: values are already LAMMPS ``units real`` coefficients (OPLS, SDK).
* ``trappe``: TraPPE source units (energies as E/kB in K, GROMACS bond k0 in kJ/mol/nm^2,
  cosine-series torsion c0..c3 in K). Individual entries may override with
  ``convention: lammps_real`` (the explicit methine H borrowed from OPLS).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

KB_KCAL = 0.0019872043  # Boltzmann constant, kcal/mol/K
KJ_PER_KCAL = 4.184

FORCEFIELD_DIR = Path(__file__).resolve().parents[3] / "forcefields"


@dataclass
class ForceField:
    """Parsed force-field YAML. Sections are plain dicts keyed by type name."""

    name: str
    convention: str
    units: dict
    styles: dict
    citations: list
    atom_types: dict
    bond_types: dict
    angle_types: dict
    dihedral_types: dict
    pair_types: dict = field(default_factory=dict)
    recommended: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    path: Path | None = None


def load_forcefield(name_or_path: str | Path) -> ForceField:
    """Load a force field by name (e.g. ``"trappe_ua"``) or by path to a YAML file."""
    path = Path(name_or_path)
    if not path.suffix:
        path = FORCEFIELD_DIR / f"{name_or_path}.yaml"
    data = yaml.safe_load(path.read_text())
    return ForceField(
        name=data["name"],
        convention=data["convention"],
        units=data["units"],
        styles=data["styles"],
        citations=data["citations"],
        atom_types=data["atom_types"],
        bond_types=data["bond_types"],
        angle_types=data["angle_types"],
        dihedral_types=data["dihedral_types"] or {},
        pair_types=data.get("pair_types") or {},
        recommended=data.get("recommended") or {},
        notes=data.get("notes") or [],
        path=path,
    )


def _is_trappe(ff: ForceField, entry: dict) -> bool:
    return entry.get("convention", ff.convention) == "trappe"


def to_lammps_real(ff: ForceField) -> dict:
    """Return LAMMPS ``units real`` coefficients for every type in ``ff``.

    Result keys: ``atoms`` (mass, charge), ``pair`` keyed by type-name tuple
    (epsilon kcal/mol, sigma angstrom, plus ``form`` for SDK), ``bond`` (K, r0, constrained),
    ``angle`` (K, theta0), ``dihedral`` (opls K1..K4). Harmonic K follow the LAMMPS
    convention E = K (x - x0)^2. For mixed force fields only like pairs are listed;
    LAMMPS applies ``styles['mixing']``.
    """
    out: dict = {"atoms": {}, "pair": {}, "bond": {}, "angle": {}, "dihedral": {}}

    for name, t in ff.atom_types.items():
        out["atoms"][name] = {"mass": float(t["mass"]), "charge": float(t["charge"])}
        if "epsilon" in t:
            scale = KB_KCAL if _is_trappe(ff, t) else 1.0
            out["pair"][(name, name)] = {
                "epsilon": t["epsilon"] * scale,
                "sigma": float(t["sigma"]),
            }
    for p in ff.pair_types.values():
        i, j = p["pattern"]
        out["pair"][(i, j)] = {
            "epsilon": float(p["epsilon"]),
            "sigma": float(p["sigma"]),
            "form": p["form"],
        }

    for name, b in ff.bond_types.items():
        if _is_trappe(ff, b):
            # GROMACS E = k0/2 (r - r0)^2 in kJ/mol/nm^2 -> LAMMPS K in kcal/mol/A^2.
            k = b["k0"] / 2 / KJ_PER_KCAL / 100
        else:
            k = b["K"]
        out["bond"][name] = {
            "K": float(k),
            "r0": float(b["r0"]),
            "constrained": bool(b.get("constrained", False)),
        }

    for name, a in ff.angle_types.items():
        # TraPPE E = k/2 (theta - theta0)^2 with k/kB in K/rad^2.
        k = a["k"] * KB_KCAL / 2 if _is_trappe(ff, a) else a["K"]
        out["angle"][name] = {"K": float(k), "theta0": float(a["theta0"])}

    for name, d in ff.dihedral_types.items():
        if _is_trappe(ff, d):
            # LAMMPS opls E = sum K_n/2 (...), TraPPE U = sum c_n (...); c0 is dropped.
            ks = [2 * d["c1"] * KB_KCAL, 2 * d["c2"] * KB_KCAL, 2 * d["c3"] * KB_KCAL, 0.0]
        else:
            ks = [d["K1"], d["K2"], d["K3"], d["K4"]]
        out["dihedral"][name] = {f"K{n}": float(k) for n, k in enumerate(ks, start=1)}

    return out
