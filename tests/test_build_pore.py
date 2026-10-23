"""Dry slit-pore builder (decision D44): whole molecules, box, mass, topology, centring, width."""

import numpy as np
import pytest
import yaml

from sepsim.analysis.pore import pore_width
from sepsim.analysis.units import AVOGADRO
from sepsim.build.amorphous import DATA_NAME, MANIFEST_NAME, build_amorphous
from sepsim.build.datafile import read_data_file
from sepsim.build.pore import PoreError, build_pore, pore_id
from sepsim.cli import main

# Small bulk boxes whose chains are short next to the box, so a 3 nm gap opens cleanly.
BULK = {"ua": ("pe", 20, 12), "cg": ("pe", 12, 24), "aa": ("pe", 12, 12)}
WIDTH_NM = 3.0


def _with_velocities(sysdir, rng_seed=0):
    """Append a Velocities section (as LAMMPS write_data does) to the bulk data file."""
    path = sysdir / DATA_NAME
    df = read_data_file(path)
    n = df.counts["atoms"]
    v = np.random.default_rng(rng_seed).normal(0.0, 0.003, (n, 3))
    text = path.read_text().rstrip("\n").split("\nBonds\n")
    rows = "\n".join(f"{i + 1} {a:.10g} {b:.10g} {c:.10g}" for i, (a, b, c) in enumerate(v))
    path.write_text(f"{text[0]}\nVelocities\n\n{rows}\n\nBonds\n{text[1]}\n")
    return v


@pytest.fixture(scope="module")
def bulk(tmp_path_factory):
    root = tmp_path_factory.mktemp("bulk")
    out = {}
    for res, (polymer, chains, carbons) in BULK.items():
        sysdir = build_amorphous(polymer, res, chains, carbons, 0.3, 3, root)
        out[res] = (sysdir, _with_velocities(sysdir))
    return out


@pytest.fixture(scope="module")
def pores(bulk, tmp_path_factory):
    root = tmp_path_factory.mktemp("pores")
    built = {}
    for res, (sysdir, _) in bulk.items():
        for r in (1, 2):
            built[(res, r)] = build_pore(sysdir / DATA_NAME, sysdir, WIDTH_NM, r, root)
    return built


CASES = [(res, r) for res in BULK for r in (1, 2)]


@pytest.fixture(params=CASES, ids=lambda c: f"{c[0]}-z{c[1]}")
def case(request, bulk, pores):
    res, r = request.param
    src, vel = bulk[res]
    out = pores[(res, r)]
    return {
        "res": res,
        "r": r,
        "src": read_data_file(src / DATA_NAME),
        "src_manifest": yaml.safe_load((src / MANIFEST_NAME).read_text()),
        "src_dir": src,
        "vel": vel,
        "df": read_data_file(out / DATA_NAME),
        "manifest": yaml.safe_load((out / MANIFEST_NAME).read_text()),
        "dir": out,
    }


def _lengths(df):
    return np.array([hi - lo for lo, hi in df.box])


def _masses(df):
    mass = {int(r[0]): float(r[1]) for r in df.sections["Masses"]}
    return np.array([mass[int(t)] for t in df.sorted_atoms()[:, 2]])


def test_ids_follow_source_naming():
    assert pore_id("pe_ua_amorph_n40_c240_s1", 3) == "pe_ua_pore_w3nm_n40_c240_s1"
    assert pore_id("pe_cg_amorph_n40_c240_s1", 5.0, 2) == "pe_cg_pore_w5nm_z2_n40_c240_s1"
    assert pore_id("ipp_aa_amorph_n40_c240_s1_from_ua", 2.5) == (
        "ipp_aa_pore_w2p5nm_n40_c240_s1_from_ua"
    )
    with pytest.raises(PoreError, match="not an amorphous"):
        pore_id("pe_ua_pore_w3nm_n40_c240_s1", 3)


def test_box_lengths(case):
    src, df, r = _lengths(case["src"]), _lengths(case["df"]), case["r"]
    assert df[:2] == pytest.approx(src[:2], abs=2e-8)  # x, y as in the source
    assert np.array(case["df"].box[:2]) == pytest.approx(np.array(case["src"].box[:2]), abs=1e-8)
    assert df[2] == pytest.approx(r * src[2] + 10 * WIDTH_NM, abs=2e-8)
    p = case["manifest"]["pore"]
    assert p["lz_source_angstrom"] == pytest.approx(src[2])
    assert p["wall_thickness_angstrom"] == pytest.approx(r * src[2])
    assert p["lz_new_angstrom"] == pytest.approx(df[2], abs=2e-8)
    assert p["replicate_z"] == r and p["nominal_width_nm"] == WIDTH_NM


def test_molecules_whole_and_inside_the_box(case):
    """No bond crosses z: z image flags are 0 and every bond is short in the raw coordinates."""
    df = case["df"]
    atoms = df.sorted_atoms()
    (zlo, zhi) = df.box[2]
    assert np.all(atoms[:, 9] == 0)
    assert atoms[:, 6].min() >= zlo and atoms[:, 6].max() <= zhi
    pos = df.unwrapped()
    row = {int(a): k for k, a in enumerate(atoms[:, 0])}
    b = df.topology("Bonds")[:, 2:4]
    i, j = (np.array([row[int(x)] for x in col]) for col in b.T)
    dz = np.abs(atoms[i, 6] - atoms[j, 6])
    assert dz.max() < 5.0  # bonded atoms are never on opposite sides of the gap
    # bond lengths equal the source's (whole molecules, rigid shifts only)
    src = case["src"]
    s_atoms = src.sorted_atoms()
    s_pos = src.unwrapped()
    s_row = {int(a): k for k, a in enumerate(s_atoms[:, 0])}
    sb = src.topology("Bonds")[:, 2:4]
    s_len = np.linalg.norm(
        s_pos[[s_row[int(x)] for x in sb[:, 0]]] - s_pos[[s_row[int(x)] for x in sb[:, 1]]],
        axis=1,
    )
    length = np.linalg.norm(pos[i] - pos[j], axis=1)
    assert length == pytest.approx(np.tile(s_len, case["r"]), abs=2e-5)


def test_mass_and_counts_conserved(case):
    src, df, r = case["src"], case["df"], case["r"]
    for key in ("atoms", "bonds", "angles", "dihedrals"):
        assert df.counts[key] == r * src.counts[key]
    for key in ("atom types", "bond types", "angle types"):
        assert df.counts[key] == src.counts[key]
    mass = _masses(df).sum()
    assert mass == pytest.approx(r * _masses(src).sum(), rel=1e-12)
    m = case["manifest"]
    assert m["total_mass_g_mol"] == pytest.approx(mass, rel=1e-12)
    assert m["pore"]["slab_mass_g_mol"] == pytest.approx(mass, rel=1e-12)
    assert m["n_chains"] == r * case["src_manifest"]["n_chains"]
    assert m["counts"]["total"]["atoms"] == df.counts["atoms"]
    vol = np.prod(_lengths(df))
    assert m["density_g_cm3"] == pytest.approx(mass / AVOGADRO / (vol * 1e-24), rel=1e-9)


def test_topology_ids_types_charges_unchanged(case):
    src, df, r = case["src"], case["df"], case["r"]
    s, a = src.sorted_atoms(), df.sorted_atoms()
    n, n_mol = len(s), int(s[:, 1].max())
    for k in range(r):
        block = a[k * n : (k + 1) * n]
        assert np.array_equal(block[:, 0], s[:, 0] + k * n)
        assert np.array_equal(block[:, 1], s[:, 1] + k * n_mol)
        assert np.array_equal(block[:, 2:4], s[:, 2:4])  # types and charges
    for name in ("Bonds", "Angles", "Dihedrals"):
        st, t = src.topology(name), df.topology(name)
        if not len(st):
            assert not len(t)
            continue
        for k in range(r):
            block = t[k * len(st) : (k + 1) * len(st)]
            assert np.array_equal(block[:, 0], st[:, 0] + k * len(st))
            assert np.array_equal(block[:, 1], st[:, 1])
            assert np.array_equal(block[:, 2:], st[:, 2:] + k * n)
    # coefficient sections are the source's (both written from the force-field YAML)
    for name in src.sections:
        if name in ("Masses",) or "Coeffs" in name:
            assert df.sections[name] == src.sections[name]
            assert df.names[name] == src.names[name]


def test_velocities_carried_over(case):
    v = np.array(case["df"].sections["Velocities"], dtype=float)
    v = v[np.argsort(v[:, 0])]
    assert np.array_equal(v[:, 0], np.arange(1, len(v) + 1))
    assert v[:, 1:] == pytest.approx(np.tile(case["vel"], (case["r"], 1)), rel=1e-9)


def test_slab_centred(case):
    """The slab's centre of mass is at the box centre; the source window is recorded."""
    df, p = case["df"], case["manifest"]["pore"]
    (zlo, zhi) = df.box[2]
    z = df.sorted_atoms()[:, 6]
    m = _masses(df)
    assert float((m * z).sum() / m.sum()) == pytest.approx(0.5 * (zlo + zhi), abs=1e-5)
    zmin, zmax = p["slab_z_extent_angstrom"]
    assert zmin == pytest.approx(z.min(), abs=1e-6) and zmax == pytest.approx(z.max(), abs=1e-6)
    w_lo, w_hi = p["window_z_angstrom"]
    assert w_hi - w_lo == pytest.approx(p["wall_thickness_angstrom"], abs=1e-9)
    assert p["protrusion_angstrom"] == pytest.approx([w_lo - zmin, zmax - w_hi])
    assert p["clear_gap_angstrom"] == pytest.approx(zhi - zlo - (zmax - zmin))
    assert p["clear_gap_angstrom"] > 0
    # most of the mass lies inside the window
    inside = (z >= w_lo) & (z < w_hi)
    assert m[inside].sum() > 0.8 * m.sum()


def test_nominal_width_is_mass_equivalent_and_measured(case):
    df, p = case["df"], case["manifest"]["pore"]
    lengths = _lengths(df)
    area = lengths[0] * lengths[1]
    mass = _masses(df).sum()
    rho_src = _masses(case["src"]).sum() / AVOGADRO / (np.prod(_lengths(case["src"])) * 1e-24)
    assert p["bulk_density_g_cm3"] == pytest.approx(rho_src, rel=1e-9)
    slab = mass / AVOGADRO / (rho_src * 1e-24) / area  # M / (rho_bulk A), Angstrom
    assert lengths[2] - slab == pytest.approx(10 * WIDTH_NM, abs=1e-6)
    # 50%-of-bulk width from the mass profile, against the source bulk density
    (zlo, _) = df.box[2]
    nb = int(lengths[2] // 2.0)
    h, e = np.histogram(
        df.sorted_atoms()[:, 6] - zlo, bins=nb, range=(0, lengths[2]), weights=_masses(df)
    )
    rho = h / AVOGADRO / (area * lengths[2] / nb * 1e-24)
    w = pore_width(0.5 * (e[1:] + e[:-1]), rho, Lz_A=lengths[2], bulk_density=rho_src)
    assert w.width == pytest.approx(10 * WIDTH_NM, rel=0.25)


def test_manifest_records_source(case):
    m, src = case["manifest"], case["src_manifest"]
    assert m["id"] == pore_id(src["id"], WIDTH_NM, case["r"]) == case["dir"].name
    s = m["source"]
    assert s["id"] == src["id"] and s["data_file"] == str(case["src_dir"] / DATA_NAME)
    assert len(s["data_sha256"]) == 64 and len(s["manifest_sha256"]) == 64
    for key in ("type_ids", "lammps_styles", "shake_bond_types", "forcefield", "seed"):
        assert m[key] == src[key]
    assert "growth" not in m and "overlap_minima_angstrom" not in m


def test_deterministic(bulk, pores, tmp_path):
    sysdir, _ = bulk["ua"]
    again = build_pore(sysdir / DATA_NAME, sysdir, WIDTH_NM, 1, tmp_path)
    first = pores[("ua", 1)]
    assert (again / DATA_NAME).read_bytes() == (first / DATA_NAME).read_bytes()


def test_too_narrow_or_bad_inputs_raise(bulk, pores, tmp_path):
    sysdir, _ = bulk["cg"]
    with pytest.raises(PoreError, match="bridge the pore"):
        build_pore(sysdir / DATA_NAME, sysdir, 0.1, 1, tmp_path)
    with pytest.raises(PoreError, match="width"):
        build_pore(sysdir / DATA_NAME, sysdir, 0.0, 1, tmp_path)
    with pytest.raises(PoreError, match="replicate_z"):
        build_pore(sysdir / DATA_NAME, sysdir, 3.0, 0, tmp_path)
    ua_dir, _ = bulk["ua"]
    with pytest.raises(PoreError, match="atoms"):  # CG data against the UA manifest
        build_pore(sysdir / DATA_NAME, ua_dir, 3.0, 1, tmp_path)
    pore = pores[("ua", 1)]
    with pytest.raises(PoreError, match="already a pore"):
        build_pore(pore / DATA_NAME, pore, 3.0, 1, tmp_path)
    with pytest.raises(PoreError, match="manifest not found"):
        build_pore(sysdir / DATA_NAME, tmp_path, 3.0, 1, tmp_path)


def test_cli_build_pore(bulk, pores, tmp_path, capsys):
    sysdir, _ = bulk["ua"]
    argv = ["build", "pore", "--data", str(sysdir / DATA_NAME), "--source", str(sysdir)]
    argv += ["--width-nm", "3", "--replicate-z", "2", "--out", str(tmp_path)]
    argv += ["--data-origin", "node:results/runs/x/prep/cooled.data"]
    assert main(argv) == 0
    out = tmp_path / pores[("ua", 2)].name
    assert str(out) in capsys.readouterr().out
    assert (out / DATA_NAME).read_bytes() == (pores[("ua", 2)] / DATA_NAME).read_bytes()
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    assert m["source"]["data_file"] == "node:results/runs/x/prep/cooled.data"
    argv[argv.index("3")] = "0.1"
    assert main(argv) == 1
    assert "sepsim build pore: error" in capsys.readouterr().err
