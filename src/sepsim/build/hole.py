"""Cylindrical hole through a free-standing film (decision D52).

Source: a finished narrow dry pore (D48, ``pore.kind: narrow``), its snapshot at one
temperature (``results/runs/<pore id>/pore/hold_<T>C.data``: box x, y already at the
D48 lateral size L(T), velocities included). The builder

* validates the data file against the pore manifest (counts, ids, types) and checks the
  temperature against the file name (``hold_<T>C``) and the box against L(T) from the
  manifest's ``pore.lateral`` table (heating branch);
* makes molecules whole, re-centres the film (most compact placement over the periodic
  z, mass centre at the box centre) and keeps x, y, ids, types and velocities;
* sets ``Lz_new = t_T (1 + pi R^2 / A) + gap`` with ``t_T = M / (rho_bulk(T) A)`` the
  mass-equivalent film thickness at T (``rho_bulk`` on the heating branch): the hole
  displaces pi R^2 t_T of polymer, which thickens the film by about that factor, and
  ``gap`` (default 5 nm) is the vacuum left above the film;
* fails if any atom would leave the box.

The hole itself is opened in LAMMPS (``sepsim render hole``: a soft radial push about
the axis at the box centre). Id: ``pe_cg_pore_w5nm_n320_...`` ->
``pe_cg_hole_r3nm_160C_n320_...``; one system per (R, T). The manifest keeps the ``pore``
block (provenance, lateral table) and adds ``hole``; render gates on ``hole``.
"""

from __future__ import annotations

import copy
import math
import re
import warnings
from pathlib import Path

import numpy as np

from sepsim.analysis.units import AVOGADRO
from sepsim.build.amorphous import source_git_state
from sepsim.build.datafile import wrap
from sepsim.build.pore import (
    PoreError,
    _base_manifest,
    _data_text,
    _load_source,
    _read_input,
    _write,
    bulk_density,
    lateral_lengths,
    place_molecules,
    whole_molecules,
)
from sepsim.run import sha256_file

_NARROW_TAG = re.compile(r"_pore_w[0-9p]+nm(_z\d+)?")
_HOLD_NAME = re.compile(r"hold_(m?\d+(?:\.\d+)?)C")
BOX_TOL_A = 0.01  # data box x, y vs L(T) from the lateral rule


class HoleError(PoreError):
    """Raised when the hole cannot be built from the given input."""


def _label(x: float) -> str:
    return f"{x:g}".replace(".", "p").replace("-", "m")


def hole_id(source_id: str, radius_nm: float, t_c: float) -> str:
    """``pe_cg_pore_w5nm_n320_c240_s1_rep222`` -> ``pe_cg_hole_r3nm_160C_n320_c240_s1_rep222``."""
    if not _NARROW_TAG.search(source_id):
        raise HoleError(f"source id {source_id!r} is not a narrow pore (_pore_w...nm)")
    tag = f"_hole_r{_label(radius_nm)}nm_{_label(t_c)}C"
    return _NARROW_TAG.sub(tag, source_id, count=1)


def check_temperature(data: Path, t_c: float, strict: bool = True) -> None:
    """Fail if the file name says ``hold_<T>C`` with another T; warn if it says nothing."""
    m = _HOLD_NAME.search(data.name)
    if m is None:
        warnings.warn(
            f"{data.name}: no hold_<T>C in the file name; cannot check --t-c {t_c:g}",
            stacklevel=2,
        )
        return
    t_file = float(m.group(1).replace("m", "-"))
    if strict and abs(t_file - t_c) > 1e-6:
        raise HoleError(f"{data.name} is the {t_file:g} C snapshot, --t-c is {t_c:g} C")


def build_hole(
    data: str | Path,
    source: str | Path,
    radius_nm: float,
    t_c: float,
    gap_nm: float = 5.0,
    out: str | Path = "systems",
    data_origin: str | None = None,
) -> Path:
    """Film with room for a cylindrical hole of radius ``radius_nm`` at ``t_c`` (D52).

    ``source`` is the narrow pore system, ``data`` its snapshot at ``t_c`` (box x, y at
    the D48 L(T)). Returns the new system directory.
    """
    data, source, out = Path(data), Path(source), Path(out)
    if radius_nm <= 0:
        raise HoleError(f"hole radius must be > 0 nm, got {radius_nm}")
    if gap_nm <= 0:
        raise HoleError(f"gap must be > 0 nm, got {gap_nm}")
    check_temperature(data, t_c)
    git = source_git_state(exclude=out)
    man_path, src = _load_source(source)
    pore = src.get("pore") or {}
    if "hole" in src:
        raise HoleError(f"{man_path}: source is already a hole system")
    if pore.get("kind") != "narrow" or not pore.get("lateral"):
        raise HoleError(f"{man_path}: source is not a narrow pore with a pore.lateral table (D48)")
    sid = hole_id(src["id"], radius_nm, t_c)
    df, atoms, masses, ff, tm = _read_input(data, src)
    lo = np.array([b[0] for b in df.box])
    lengths = np.array([hi - lo_ for lo_, hi in df.box])
    t_k = t_c + 273.15
    lat = pore["lateral"]
    l_t = lateral_lengths(lat, "heating", t_k)
    if not np.allclose(lengths[:2], l_t, atol=BOX_TOL_A):
        raise HoleError(
            f"{data}: box x, y {lengths[0]:.4f} x {lengths[1]:.4f} A, but the D48 lateral rule"
            f" gives {l_t[0]:.4f} x {l_t[1]:.4f} A at {t_c:g} C: wrong temperature or file"
        )
    area = float(lengths[0] * lengths[1])
    r_a = 10.0 * float(radius_nm)
    if 2.0 * r_a >= min(lengths[:2]):
        raise HoleError(
            f"hole diameter {2 * r_a:g} A does not fit the {min(lengths[:2]):.1f} A box"
        )

    # ---- whole molecules, most compact film over the periodic z, mass centre at box centre
    pos = whole_molecules(atoms, df.topology("Bonds")[:, 2:4], lengths)
    mol_ids = atoms[:, 1].astype(np.int64)
    _, shift = place_molecules(pos[:, 2], mol_ids, masses, float(lo[2]), float(lengths[2]))
    pos[:, 2] += shift
    mass = float(masses.sum())
    rho = bulk_density(lat, "heating", t_k)
    t_film = mass / AVOGADRO / (rho * area * 1e-24)
    frac = math.pi * r_a**2 / area
    t_hole = t_film * (1.0 + frac)
    gap = 10.0 * float(gap_nm)
    lz_new = t_hole + gap
    z_lo = float(lo[2])
    com = float((masses * pos[:, 2]).sum() / mass)
    pos[:, 2] += z_lo + 0.5 * lz_new - com
    zmin, zmax = float(pos[:, 2].min()), float(pos[:, 2].max())
    if zmin < z_lo or zmax >= z_lo + lz_new:
        raise HoleError(
            f"film atoms span z {zmin:.2f}..{zmax:.2f} A, beyond the new box"
            f" {z_lo:.2f}..{z_lo + lz_new:.2f} A: increase --gap-nm (now {gap_nm:g})"
        )
    bounds = (df.box[0], df.box[1], (z_lo, z_lo + lz_new))
    wrapped, img = wrap(pos, bounds)
    img[:, 2] = 0
    text = _data_text(sid, df, ff, tm, bounds, wrapped, img, 1, int(src["n_chains"]))

    axis = [0.5 * (a + b) for a, b in df.box[:2]]
    manifest = _base_manifest(src, sid, bounds, mass, git)
    manifest["hole"] = {
        "method": (
            "D52: narrow-pore snapshot at T, molecules whole, film re-centred, x, y kept;"
            " Lz = t_T (1 + pi R^2 / A) + gap; the hole is opened in LAMMPS (render hole)"
        ),
        "radius_nm": float(radius_nm),
        "t_c": float(t_c),
        "axis_angstrom": [float(axis[0]), float(axis[1])],
        "lz_new": float(lz_new),
        "film_thickness_angstrom": float(t_film),
        "film_thickness_with_hole": float(t_hole),
        "gap_angstrom": gap,
        "area": area,
        "hole_area_fraction": frac,
        "bulk_density_g_cm3": rho,
        "film_z_extent_angstrom": [zmin, zmax],
        "ligament_angstrom": float(min(lengths[:2]) - 2.0 * r_a),
        "source": {
            "id": src["id"],
            "manifest_sha256": sha256_file(man_path),
            "data_file": data_origin or str(data),
            "data_sha256": sha256_file(data),
            "source": src.get("source"),
        },
    }
    manifest["source"] = copy.deepcopy(manifest["hole"]["source"])
    return _write(out, sid, text, manifest)
