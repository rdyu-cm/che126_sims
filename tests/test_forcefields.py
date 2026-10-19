"""Force-field YAMLs: structure, provenance, agreement with upstream excerpts, unit conversions."""

import re
from pathlib import Path

import numpy as np
import pytest
import yaml

from sepsim.ff.params import FORCEFIELD_DIR, KB_KCAL, KJ_PER_KCAL, load_forcefield, to_lammps_real

NAMES = ["opls2020_aa", "trappe_ua", "sdk_cg"]
REF_DIR = FORCEFIELD_DIR / "_reference"
KB_KJ = KB_KCAL * KJ_PER_KCAL  # kJ/mol/K
TYPED_SECTIONS = ["atom_types", "pair_types", "bond_types", "angle_types", "dihedral_types"]
REQUIRED_KEYS = [
    "name",
    "convention",
    "citations",
    "upstream",
    "units",
    "styles",
    "atom_types",
    "bond_types",
    "angle_types",
    "dihedral_types",
    "recommended",
]


def raw_yaml(name):
    return yaml.safe_load((FORCEFIELD_DIR / f"{name}.yaml").read_text())


def read_excerpt(filename: str) -> dict[int, str]:
    """Map upstream line number -> original line text for an excerpt file."""
    lines = {}
    for text in (REF_DIR / filename).read_text().splitlines():
        m = re.match(r"^L(\d+): (.*)$", text)
        if m:
            lines[int(m.group(1))] = m.group(2)
    return lines


def all_sources(entry: dict) -> list[dict]:
    """Primary source plus any independent `alt_sources` for a typed entry."""
    return [entry["source"], *entry.get("alt_sources", [])]


def parse_record(line: str) -> tuple[str, list]:
    """Classify an upstream line and return (kind, values) using token positions."""
    body = re.split(r"[#;]", line, maxsplit=1)[0]
    tok = body.split()
    # SPICA spica_db.prm records
    if tok[0] == "bond":
        return "bond", [float(v) for v in tok[3:5]]
    if tok[0] == "angle":
        return "angle", [float(v) for v in tok[4:6]]
    if tok[0] == "pair" and tok[3] == "lj9_6":
        return "pair", [float(v) for v in tok[4:6]]
    if tok[:2] == ["set", "type"] and tok[3] == "charge":
        return "charge", [float(tok[4])]
    if len(tok) == 2 and tok[0].startswith("@atom:"):
        return "mass", [float(tok[1])]
    if tok[0] == "pair_coeff":
        vals = tok[4:6] if tok[3] == "lj9_6" else tok[3:5]
        return "pair", [float(v) for v in vals]
    if tok[0] in ("bond_coeff", "angle_coeff"):
        vals = tok[3:5] if tok[2] in ("harmonic", "sdk") else tok[2:4]
        return tok[0].split("_")[0], [float(v) for v in vals]
    if tok[0] == "dihedral_coeff":
        return "dihedral", [float(v) for v in tok[2:6]]
    # GROMACS itp records
    if len(tok) == 7 and tok[4] == "A":
        return "itp_atom", [float(v) for v in tok[2:4] + tok[5:7]]  # mass, q, sigma nm, eps kJ
    if len(tok) == 5 and tok[2] == "1":
        return "itp_bond", [float(v) for v in tok[3:5]]  # b0 nm, k0
    if len(tok) == 6 and tok[3] == "1":
        return "itp_angle", [float(v) for v in tok[4:6]]  # th0, cth kJ/mol/rad^2
    if len(tok) == 11 and tok[4] == "3":
        return "itp_rb", [float(v) for v in tok[5:11]]  # C0..C5 kJ/mol
    raise ValueError(f"unrecognized upstream record: {line!r}")


def trappe_to_rb(c0, c1, c2, c3):
    """TraPPE cosine series (K) -> GROMACS RB C0..C3 (kJ/mol), per the itp header formulas."""
    return [
        (c0 + c1 + 2 * c2 + c3) * KB_KJ,
        (-c1 + 3 * c3) * KB_KJ,
        (-2 * c2) * KB_KJ,
        (-4 * c3) * KB_KJ,
    ]


def _typed_entries():
    for name in NAMES:
        data = raw_yaml(name)
        for section in TYPED_SECTIONS:
            for tname, entry in (data.get(section) or {}).items():
                yield pytest.param(name, data, section, tname, entry, id=f"{name}:{tname}")


def typed_entries():
    return list(_typed_entries())


# (a) structure and provenance -------------------------------------------------------------


@pytest.mark.parametrize("name", NAMES)
def test_yaml_loads_with_required_fields(name):
    data = raw_yaml(name)
    for key in REQUIRED_KEYS:
        assert key in data, key
    ff = load_forcefield(name)
    assert ff.name == name
    keys = {c["key"] for c in data["citations"]}
    for c in data["citations"]:
        for field in ("key", "authors", "year"):
            assert c.get(field), (c, field)
        assert c.get("doi") or c.get("url"), c
    for up in data["upstream"]:
        assert up["url"].startswith("https://raw.githubusercontent.com/")
        assert (FORCEFIELD_DIR / up["file"]).is_file()
    upstream_files = {up["file"] for up in data["upstream"]}
    # styles/recommended may be citation-only (ref, no excerpt line); parameters may not.
    sources = [data["styles"]["source"], data["recommended"]["source"]]
    for section in TYPED_SECTIONS:
        for e in (data.get(section) or {}).values():
            assert "file" in e["source"] and e["source"]["lines"]
            sources += all_sources(e)
    for src in sources:
        assert src["ref"] in keys
        if "file" in src:
            assert f"_reference/{src['file']}" in upstream_files, src["file"]
            assert src["lines"], src


@pytest.mark.parametrize("name,data,section,tname,entry", typed_entries())
def test_every_parameter_has_a_source_line(name, data, section, tname, entry):
    for src in all_sources(entry):
        excerpt = read_excerpt(src["file"])
        assert src["lines"], f"{tname} has no source lines"
        for line_no in src["lines"].values():
            assert line_no in excerpt, f"{tname}: L{line_no} missing from {src['file']}"


def test_load_by_path():
    ff = load_forcefield(FORCEFIELD_DIR / "sdk_cg.yaml")
    assert ff.name == "sdk_cg"


# (b) YAML values equal the verbatim upstream excerpt values -----------------------------


@pytest.mark.parametrize("name,data,section,tname,entry", typed_entries())
def test_values_match_upstream_excerpt(name, data, section, tname, entry):
    native = entry.get("convention", data["convention"]) == "lammps_real"
    for src in all_sources(entry):
        excerpt = read_excerpt(src["file"])
        checked = 0
        for line_no in src["lines"].values():
            kind, v = parse_record(excerpt[line_no])
            if kind == "charge":
                assert entry["charge"] == v[0]
            elif kind == "mass":
                assert entry["mass"] == v[0]
            elif kind == "pair":
                assert [entry["epsilon"], entry["sigma"]] == v
            elif kind == "bond" and native:
                assert [entry["K"], entry["r0"]] == v
            elif kind == "angle" and native:
                assert [entry["K"], entry["theta0"]] == v
            elif kind == "dihedral" and native:
                assert [entry[k] for k in ("K1", "K2", "K3", "K4")] == v
            elif kind == "itp_atom":
                mass, charge, sigma_nm, eps_kj = v
                # CH carries its H explicitly in this project: upstream UA mass = C + H.
                expected_mass = entry["mass"] + 1.008 if tname == "CH" else entry["mass"]
                assert expected_mass == pytest.approx(mass, abs=1e-9)
                assert entry["charge"] == charge
                assert entry["sigma"] == pytest.approx(sigma_nm * 10, abs=1e-9)
                assert entry["epsilon"] * KB_KJ == pytest.approx(eps_kj, rel=1e-4)
            elif kind == "itp_bond":
                assert entry["r0"] == pytest.approx(v[0] * 10, abs=1e-9)
                assert entry["k0"] == v[1]
            elif kind == "itp_angle":
                assert entry["theta0"] == v[0]
                assert entry["k"] * KB_KJ == pytest.approx(v[1], rel=1e-4)
            elif kind == "itp_rb":
                rb = trappe_to_rb(*(entry[f"c{n}"] for n in range(4)))
                assert rb == pytest.approx(v[:4], abs=1e-3)
                assert v[4:] == [0.0, 0.0]
            else:
                pytest.fail(f"{tname}: unexpected record kind {kind} at L{line_no}")
            checked += 1
        assert checked == len(src["lines"])


def test_opls_uses_hydrocarbon_not_butane_dihedral():
    excerpt = read_excerpt("oplsaa2024.excerpt.txt")
    assert "butane only" in excerpt[8439] and parse_record(excerpt[8439])[1][0] == 1.100
    assert "hydrocarbon" in excerpt[8440]
    ff = load_forcefield("opls2020_aa")
    assert ff.dihedral_types["CT-CT-CT-CT"]["K1"] == 0.850
    assert ff.dihedral_types["CT-CT-CT-CT"]["source"]["lines"]["coeffs"] == 8440


def test_styles_match_upstream():
    opls = read_excerpt("oplsaa2024.excerpt.txt")
    assert opls[10374].split() == ["pair_modify", "mix", "geometric"]
    assert opls[10375].split() == ["special_bonds", "lj/coul", "0.0", "0.0", "0.5"]
    assert load_forcefield("opls2020_aa").styles["special_bonds"]["lj"] == [0.0, 0.0, 0.5]

    trappe = load_forcefield("trappe_ua")
    # Sourced to the primary paper only (unlicensed upstream prose is not reproduced).
    assert trappe.styles["source"] == {"ref": "martin1998"}
    assert trappe.recommended["source"] == {"ref": "martin1998"}
    assert trappe.styles["mixing"] == "arithmetic"
    assert trappe.styles["special_bonds"]["lj"] == [0.0, 0.0, 0.0]
    assert trappe.recommended["lj_cutoff"] == 14.0

    # SDK/SPICA run settings come from SPICA's official setup_lmp.py (uncharged branch).
    spica = read_excerpt("spica_setup_lmp.excerpt.txt")
    sb = re.search(r'"special_bonds\s+(.*?)"', spica[453]).group(1).split()
    ps = re.search(r'"pair_style\s+(.*?)"', spica[434]).group(1).split()
    assert "else" in spica[452] and "else" in spica[433]  # uncharged branch
    ff = load_forcefield("sdk_cg")
    yaml_sb = ff.styles["special_bonds"]
    assert sb[0] == "lj" and "coul" not in yaml_sb
    assert yaml_sb["lj"] == [float(v) for v in sb[1:4]]
    assert sb[4:] == ["angle", "yes"] and yaml_sb["angle"] is True
    assert ps[0] == "lj/sdk" and ff.recommended["lj_cutoff"] == float(ps[1]) == 15.0
    src = ff.styles["source"]
    assert src["file"] == "spica_setup_lmp.excerpt.txt"
    assert src["lines"]["special_bonds"] == 453 and src["lines"]["pair"] == 434
    assert ff.recommended["source"]["lines"]["lj_cutoff"] == 434
    assert "needs_verification" not in yaml_sb and "needs_verification" not in ff.recommended


# (c) TraPPE unit conversions --------------------------------------------------------------


def test_trappe_conversions():
    ff = load_forcefield("trappe_ua")
    lmp = to_lammps_real(ff)
    nb = read_excerpt("trappeua_ffnonbonded.excerpt.txt")
    for tname, line_no in [("CH3", 19), ("CH2", 21), ("CH", 23)]:
        eps_kj = parse_record(nb[line_no])[1][3]
        assert ff.atom_types[tname]["epsilon"] * KB_KJ == pytest.approx(eps_kj, rel=1e-4)
        assert lmp["pair"][(tname, tname)]["epsilon"] == pytest.approx(eps_kj / KJ_PER_KCAL, 1e-4)

    bonded = read_excerpt("trappeua_ffbonded.excerpt.txt")
    for dname, line_no in [("CHx-CH2-CH2-CHy", 105), ("CHx-CH2-CH-CHy", 121)]:
        d = ff.dihedral_types[dname]
        rb = parse_record(bonded[line_no])[1]
        assert trappe_to_rb(d["c0"], d["c1"], d["c2"], d["c3"]) == pytest.approx(rb[:4], abs=1e-3)
        k = lmp["dihedral"][dname]
        assert k["K1"] == pytest.approx(2 * d["c1"] * KB_KCAL)
        assert k["K4"] == 0.0

    for aname in ("CHx-CH2-CHy", "CHx-CH-CHy"):
        assert lmp["angle"][aname]["K"] == pytest.approx(62.10, abs=0.01)
    assert lmp["bond"]["CHx-CHy"]["K"] == pytest.approx(600.4, abs=0.1)
    assert lmp["bond"]["CHx-CHy"]["r0"] == 1.54
    # Backbone bonds are flexible in production; only the methine C-H is SHAKE-constrained.
    assert ff.bond_types["CHx-CHy"]["constrained"] is False
    assert lmp["bond"]["CHx-CHy"]["constrained"] is False
    assert [n for n, b in lmp["bond"].items() if b["constrained"]] == ["CH-H"]

    # Explicit methine H: OPLS values pass through unchanged, no LJ, no charge.
    assert lmp["bond"]["CH-H"] == {"K": 340.0, "r0": 1.09, "constrained": True}
    assert lmp["angle"]["H-CH-CHx"] == {"K": 37.5, "theta0": 110.7}
    assert lmp["pair"][("H", "H")] == {"epsilon": 0.0, "sigma": 0.0}
    assert lmp["atoms"]["H"] == {"mass": 1.008, "charge": 0.0}
    assert lmp["atoms"]["CH"]["mass"] == 12.011
    assert all("H" not in d["pattern"] for d in ff.dihedral_types.values())


def test_trappe_torsion_energy_matches_cosine_series_and_rb():
    """LAMMPS dihedral_style opls energy on a phi grid vs TraPPE and GROMACS RB forms."""
    ff = load_forcefield("trappe_ua")
    lmp = to_lammps_real(ff)
    phi = np.radians(np.linspace(-180.0, 180.0, 721))  # IUPAC, trans = 180 deg
    psi = phi - np.pi  # GROMACS RB polymer convention, trans = 0
    for name, d in ff.dihedral_types.items():
        k = lmp["dihedral"][name]
        e_lmp = 0.5 * (  # docs.lammps.org/dihedral_opls.html
            k["K1"] * (1 + np.cos(phi))
            + k["K2"] * (1 - np.cos(2 * phi))
            + k["K3"] * (1 + np.cos(3 * phi))
            + k["K4"] * (1 - np.cos(4 * phi))
        )
        u_trappe = KB_KCAL * (
            d["c0"]
            + d["c1"] * (1 + np.cos(phi))
            + d["c2"] * (1 - np.cos(2 * phi))
            + d["c3"] * (1 + np.cos(3 * phi))
        )
        rb = trappe_to_rb(d["c0"], d["c1"], d["c2"], d["c3"])
        u_rb = sum(c * np.cos(psi) ** n for n, c in enumerate(rb)) / KJ_PER_KCAL
        for ref in (u_trappe, u_rb):
            offset = ref - e_lmp
            assert np.ptp(offset) < 1e-9 * np.ptp(ref), name
            assert offset[0] == pytest.approx(d["c0"] * KB_KCAL, abs=1e-9), name
        assert np.argmin(e_lmp) == 0  # trans (phi = -180) is the global minimum


def test_passthrough_conventions():
    opls = to_lammps_real(load_forcefield("opls2020_aa"))
    assert opls["pair"][("CT_CH2", "CT_CH2")] == {"epsilon": 0.066, "sigma": 3.51}
    assert opls["dihedral"]["CT-CT-CT-CT"] == {"K1": 0.85, "K2": -0.2, "K3": 0.2, "K4": 0.0}
    sdk = to_lammps_real(load_forcefield("sdk_cg"))
    assert sdk["pair"][("CM", "CT")] == {"epsilon": 0.444, "sigma": 4.5455, "form": "lj9_6"}
    assert sdk["angle"]["CM-CM-CT"] == {"K": 1.19, "theta0": 175.0}
    assert sdk["dihedral"] == {}


def test_sdk_params_also_match_spica_db():
    ff = load_forcefield("sdk_cg")
    for section in ("pair_types", "bond_types", "angle_types"):
        for tname, entry in getattr(ff, section).items():
            alts = [a for a in entry.get("alt_sources", []) if a["file"] == "spica_db.excerpt.txt"]
            assert len(alts) == 1, tname


# (d) OPLS group charge neutrality ---------------------------------------------------------


@pytest.mark.parametrize(
    "carbon,n_h", [("CT_CH3", 3), ("CT_CH3_iso", 3), ("CT_CH2", 2), ("CT_CH", 1)]
)
def test_opls_groups_neutral(carbon, n_h):
    at = load_forcefield("opls2020_aa").atom_types
    assert at[carbon]["charge"] + n_h * at["HC"]["charge"] == pytest.approx(0.0, abs=1e-12)


# (e) SDK bead masses ----------------------------------------------------------------------


def test_sdk_masses_match_heavy_atom_groups():
    at = load_forcefield("sdk_cg").atom_types
    ch3, ch2 = 15.035, 14.027
    assert at["CM"]["mass"] == pytest.approx(3 * ch2, abs=0.01)
    assert at["CT"]["mass"] == pytest.approx(ch3 + 2 * ch2, abs=0.01)


def test_reference_headers():
    for path in Path(REF_DIR).glob("*.excerpt.txt"):
        head = path.read_text().splitlines()[:6]
        joined = "\n".join(head)
        for tag in ("Upstream URL:", "Commit:", "License:", "Retrieved: 2026-10-16"):
            assert tag in joined, (path.name, tag)
