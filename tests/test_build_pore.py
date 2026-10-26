"""Dry slit-pore builder (D44, D48): wide pore from the bulk (whole molecules, box, mass,
topology, centring, width), narrowing from a relaxed wide pore, bulk density table and
the lateral rule."""

import hashlib

import numpy as np
import pytest
import yaml
from _build_helpers import SYN_BULK

from sepsim.analysis.pore import pore_width
from sepsim.analysis.units import AVOGADRO
from sepsim.build.amorphous import DATA_NAME, MANIFEST_NAME, build_amorphous
from sepsim.build.datafile import read_data_file
from sepsim.build.pore import (
    T_NOMINAL_K,
    PoreError,
    build_pore,
    bulk_density,
    bulk_density_table,
    lateral_lengths,
    narrow_id,
    narrow_pore,
    pore_id,
)
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
    assert pore_id("pe_ua_amorph_n40_c240_s1", 10) == "pe_ua_pore500k_w10nm_n40_c240_s1"
    assert pore_id("pe_cg_amorph_n40_c240_s1", 12.0, 2) == "pe_cg_pore500k_w12nm_z2_n40_c240_s1"
    assert pore_id("ipp_aa_amorph_n40_c240_s1_from_ua", 2.5) == (
        "ipp_aa_pore500k_w2p5nm_n40_c240_s1_from_ua"
    )
    with pytest.raises(PoreError, match="not an amorphous"):
        pore_id("pe_ua_pore_w3nm_n40_c240_s1", 3)
    assert narrow_id("pe_cg_pore500k_w10nm_n40_c240_s1", 3) == "pe_cg_pore_w3nm_n40_c240_s1"
    assert narrow_id("pe_cg_pore500k_w12nm_z2_n40_c240_s1", 5) == "pe_cg_pore_w5nm_z2_n40_c240_s1"
    assert narrow_id("ipp_aa_pore500k_w10nm_n40_c240_s1_from_ua", 2.5) == (
        "ipp_aa_pore_w2p5nm_n40_c240_s1_from_ua"
    )
    with pytest.raises(PoreError, match="not a wide"):
        narrow_id("pe_cg_pore_w3nm_n40_c240_s1", 3)


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
    assert p["kind"] == "wide" and p["temperature_k"] == 500.0


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
    with pytest.raises(PoreError, match="not a wide"):  # narrowing needs a wide pore source
        narrow_pore(sysdir / DATA_NAME, sysdir, 3.0, SYN_BULK, tmp_path)
    with pytest.raises(PoreError, match="manifest not found"):
        build_pore(sysdir / DATA_NAME, tmp_path, 3.0, 1, tmp_path)


def test_cli_build_pore(bulk, pores, tmp_path, capsys):
    sysdir, _ = bulk["ua"]
    argv = ["build", "pore", "--data", str(sysdir / DATA_NAME), "--source", str(sysdir)]
    argv += ["--width-nm", "3", "--replicate-z", "2", "--out", str(tmp_path)]
    argv += ["--data-origin", "node:results/runs/x/prep/hold.data"]
    assert main(argv) == 0
    out = tmp_path / pores[("ua", 2)].name
    assert str(out) in capsys.readouterr().out
    assert (out / DATA_NAME).read_bytes() == (pores[("ua", 2)] / DATA_NAME).read_bytes()
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    assert m["source"]["data_file"] == "node:results/runs/x/prep/hold.data"
    argv[argv.index("3")] = "0.1"
    assert main(argv) == 1
    assert "sepsim build pore: error" in capsys.readouterr().err


# ---- D48: bulk density table, lateral rule, narrowing a relaxed wide pore ----


def _block(rho, s0=0, n=41, stride=1):
    rows = "".join(
        f"  {s0 + stride * k}  {10.0 * (s0 + stride * k)}  400  {rho}  -10  5  {0.1 * k}\n"
        for k in range(n)
    )
    return "   Step   Time   Temp   Density   Enthalpy   PotEng   CPU\n" + rows


LOOP = "Loop time of 1 on 1 procs for 40 steps with 10 atoms\n"
HEAD = "# sepsim 0.1.0 deck: {}\n# system demo (cg), seed 1\ntimestep 10\n"


def _bulk_runs(root):
    """Synthetic bulk prep (hold + 2 cool steps) and sweep (hold, step, hold) run dirs."""
    prep, sweep = root / "prep", root / "sweep"
    prep.mkdir(parents=True)
    sweep.mkdir()
    (prep / "in.prep").write_text(
        HEAD.format("prep")
        + "\n# ---- Stage 6: NPT hold 0.4 ps at 500 K, 1 atm -> hold.data, hold.dcd\n"
        "fix md all npt temp 500 500 1000 iso 1 1 10000\ndump hold all dcd 10 hold.dcd\n"
        "run 40\nundump hold\nunfix md\n"
        "\n# ---- Stage 7: step-cool 500 -> 300 K in 2 steps\n"
        "# cool step 1/2: 400 K\nfix md all npt temp 400 400 1000 iso 1 1 10000\nrun 40\n"
        "unfix md\n# cool step 2/2: 300 K\nfix md all npt temp 300 300 1000 iso 1 1 10000\n"
        "run 40\nunfix md\n"
    )
    (prep / "log.lammps").write_text("".join(_block(r) + LOOP for r in (0.72, 0.76, 0.81)))
    (sweep / "in.sweep").write_text(
        HEAD.format("sweep") + "\n# ---- Segment 1: hold at 25 C (298.15 K), 0.4 ps\n"
        "fix md all npt temp 298.15 298.15 1000 iso 1 1 10000\nrun 40\nunfix md\n"
        "\n# ---- Segment 2: step at 100 C (373.15 K), 0.4 ps\n"
        "fix md all npt temp 373.15 373.15 1000 iso 1 1 10000\nrun 40\n"
        "\n# ---- Segment 3: hold at 100 C (373.15 K), 0.4 ps\nrun 40\nunfix md\n"
    )
    (sweep / "log.lammps").write_text("".join(_block(r) + LOOP for r in (0.83, 0.80, 0.79)))
    return prep, sweep


def test_bulk_density_table_from_runs(tmp_path):
    prep, sweep = _bulk_runs(tmp_path)
    t = bulk_density_table(prep, prep, sweep)
    assert t["t_source_k"] == 500.0 and t["rho_source_g_cm3"] == pytest.approx(0.72)
    np.testing.assert_allclose(t["cooling"], [[300.0, 0.81], [400.0, 0.76], [500.0, 0.72]])
    np.testing.assert_allclose(t["heating"], [[298.15, 0.83], [373.15, 0.79]])  # the hold wins
    src = t["sources"]
    assert set(src) == {"hold", "cool", "sweep"} and src["sweep"]["deck"] == "in.sweep"
    assert (
        src["hold"]["log_sha256"] == hashlib.sha256((prep / "log.lammps").read_bytes()).hexdigest()
    )
    assert "Stage 6" in src["hold"]["segments"]
    # a cancelled D47 extension: its hold counts up to the last thermo row
    ext = tmp_path / "extend"
    ext.mkdir()
    (ext / "in.extend").write_text(
        HEAD.format("extend") + "\n# ---- Stage 1: NPT hold extension 0.8 ps at 500 K\n"
        "fix md all npt temp 500 500 1000 iso 1 1 10000\ndump e all dcd 10 hold_ext.dcd\n"
        "run 40\nwrite_data hold_ext_1ns.data\nrun 40\n"
    )
    (ext / "log.lammps").write_text(_block(0.70) + LOOP + _block(0.70, 40, 30))
    assert bulk_density_table(ext, prep, sweep)["rho_source_g_cm3"] == pytest.approx(0.70)
    with pytest.raises(PoreError, match="hold"):
        bulk_density_table(sweep, prep, sweep)
    with pytest.raises(PoreError, match="step-cool"):
        bulk_density_table(prep, sweep, sweep)
    with pytest.raises(PoreError, match="deck"):
        bulk_density_table(prep, prep, tmp_path)


def test_lateral_rule_and_no_extrapolation():
    lat = SYN_BULK | {"l_source_angstrom": [60.0, 50.0]}
    assert bulk_density(lat, "heating", 298.15) == pytest.approx(0.335)
    mid = 0.5 * (298.15 + 433.15)
    assert bulk_density(lat, "heating", mid) == pytest.approx(0.5 * (0.335 + 0.312))
    assert lateral_lengths(lat, "cooling", 500.0) == pytest.approx([60.0, 50.0])
    f = (0.30 / 0.336) ** (1 / 3)
    assert lateral_lengths(lat, "cooling", 298.15) == pytest.approx([60.0 * f, 50.0 * f])
    with pytest.raises(PoreError, match="no extrapolation"):
        lateral_lengths(lat, "heating", 500.0)


@pytest.fixture(scope="module")
def narrowed(bulk, tmp_path_factory):
    """The CG wide pore (with velocities) narrowed to 3 nm from its own data file."""
    root = tmp_path_factory.mktemp("narrow")
    sysdir, vel = bulk["cg"]
    wide = build_pore(sysdir / DATA_NAME, sysdir, 4.0, 1, root)
    return wide, narrow_pore(wide / DATA_NAME, wide, WIDTH_NM, SYN_BULK, root), vel


def test_narrow_box_width_and_centring(narrowed):
    wide_dir, out, vel = narrowed
    wide, df = read_data_file(wide_dir / DATA_NAME), read_data_file(out / DATA_NAME)
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    p = m["pore"]
    assert m["id"] == out.name == "pe_cg_pore_w3nm_n12_c24_s3"
    assert np.array(df.box[:2]) == pytest.approx(np.array(wide.box[:2]), abs=1e-8)  # x, y kept
    lx, ly, lz = _lengths(df)
    mass = _masses(df).sum()
    # nominal width at 25 C: Lz - M / (rho(25 C) A(25 C)), A from the lateral rule
    f = (0.30 / 0.335) ** (1 / 3)
    t25 = mass / AVOGADRO / (0.335 * lx * ly * f * f * 1e-24)
    assert lz - t25 == pytest.approx(10 * WIDTH_NM, abs=1e-6)
    t500 = mass / AVOGADRO / (0.30 * lx * ly * 1e-24)
    assert p["width_500k_nm"] == pytest.approx((lz - t500) / 10, abs=1e-9)
    assert p["wall_thickness_angstrom"] == pytest.approx(t25)
    assert p["kind"] == "narrow" and p["nominal_width_nm"] == WIDTH_NM
    assert p["bulk_density_g_cm3"] == pytest.approx(0.335)
    assert p["area_25c_angstrom2"] == pytest.approx(lx * ly * f * f)
    # mass centre at the box centre, molecules whole and inside, protrusions and clear gap
    atoms = df.sorted_atoms()
    zlo, zhi = df.box[2]
    z = atoms[:, 6]
    assert float((_masses(df) * z).sum() / mass) == pytest.approx(0.5 * (zlo + zhi), abs=1e-5)
    assert np.all(atoms[:, 9] == 0) and z.min() >= zlo and z.max() <= zhi
    w_lo, w_hi = p["window_z_angstrom"]
    assert w_hi - w_lo == pytest.approx(t500)
    assert p["protrusion_angstrom"] == pytest.approx([w_lo - z.min(), z.max() - w_hi])
    assert p["clear_gap_angstrom"] == pytest.approx(lz - (z.max() - z.min()))
    # velocities, ids and topology carried over; the lateral table is stored with L_src
    v = np.array(df.sections["Velocities"], dtype=float)
    assert v[np.argsort(v[:, 0]), 1:] == pytest.approx(vel, rel=1e-9)
    assert np.array_equal(df.topology("Bonds"), wide.topology("Bonds"))
    lat = p["lateral"]
    assert lat["l_source_angstrom"] == pytest.approx([lx, ly])
    assert lat["heating"] == SYN_BULK["heating"] and lat["sources"] == SYN_BULK["sources"]
    assert lateral_lengths(lat, "heating", T_NOMINAL_K) == pytest.approx([lx * f, ly * f])


def test_narrow_records_the_source_chain(narrowed):
    wide_dir, out, _ = narrowed
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    wide = yaml.safe_load((wide_dir / MANIFEST_NAME).read_text())
    s = m["source"]
    assert s["id"] == wide["id"] and s["data_file"] == str(wide_dir / DATA_NAME)
    assert (
        s["manifest_sha256"] == hashlib.sha256((wide_dir / MANIFEST_NAME).read_bytes()).hexdigest()
    )
    assert s["source"] == wide["source"] and s["source"]["id"] == "pe_cg_amorph_n12_c24_s3"


def test_narrow_bridging_and_bad_inputs(narrowed, tmp_path):
    wide_dir, out, _ = narrowed
    with pytest.raises(PoreError, match="bridge the pore"):
        narrow_pore(wide_dir / DATA_NAME, wide_dir, 0.05, SYN_BULK, tmp_path)
    with pytest.raises(PoreError, match="not a wide"):
        narrow_pore(out / DATA_NAME, out, 3.0, SYN_BULK, tmp_path)
    with pytest.raises(PoreError, match="outside the bulk heating"):
        narrow_pore(
            wide_dir / DATA_NAME, wide_dir, 3.0, SYN_BULK | {"heating": [[300, 0.3]]}, tmp_path
        )
    # a relaxed state whose box x, y changed (not the fixed-box pore_relax output)
    lines = (wide_dir / DATA_NAME).read_text().splitlines()
    k = next(i for i, ln in enumerate(lines) if ln.endswith("xlo xhi"))
    lo, hi = lines[k].split()[:2]
    lines[k] = f"{lo} {float(hi) + 0.5} xlo xhi"
    bad = tmp_path / "bad.data"
    bad.write_text("\n".join(lines) + "\n")
    with pytest.raises(PoreError, match="differ from the wide"):
        narrow_pore(bad, wide_dir, 3.0, SYN_BULK, tmp_path)


def test_cli_narrow_pore_reads_bulk_runs(narrowed, tmp_path, capsys):
    wide_dir, _, _ = narrowed
    _, sweep = _bulk_runs(tmp_path / "runs" / "pe_cg_amorph_n12_c24_s3")
    argv = ["build", "pore", "--data", str(wide_dir / DATA_NAME), "--source", str(wide_dir)]
    argv += [
        "--width-nm",
        "3",
        "--out",
        str(tmp_path / "sys"),
        "--bulk-root",
        str(tmp_path / "runs"),
    ]
    assert main(argv) == 0
    out = tmp_path / "sys" / "pe_cg_pore_w3nm_n12_c24_s3"
    assert str(out) in capsys.readouterr().out
    lat = yaml.safe_load((out / MANIFEST_NAME).read_text())["pore"]["lateral"]
    assert lat["sources"]["sweep"]["run_dir"] == str(sweep)
    np.testing.assert_allclose(lat["heating"], [[298.15, 0.83], [373.15, 0.79]])
    assert main([*argv, "--replicate-z", "2"]) == 1
    assert "replicate-z" in capsys.readouterr().err
    assert main([*argv, "--bulk-sweep", str(tmp_path)]) == 1  # no deck/log there
    assert "deck" in capsys.readouterr().err
