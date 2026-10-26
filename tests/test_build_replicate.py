"""Replicated bulk box (D50): counts, ids, whole molecules across the seams, manifest, the
extend deck reading the replicated data.lmp, and pores cut from it narrowed with the small
bulk's runs."""

import hashlib

import numpy as np
import pytest
import yaml
from test_build_pore import _bulk_runs, _with_velocities

from sepsim.build.amorphous import DATA_NAME, MANIFEST_NAME, build_amorphous
from sepsim.build.datafile import read_data_file
from sepsim.build.pore import PoreError, build_pore, whole_molecules
from sepsim.build.replicate import ReplicateError, build_replicate, replicate_id
from sepsim.cli import main

N = (2, 2, 2)
REP_ID = "pe_cg_amorph_n96_c24_s3_rep222"


@pytest.fixture(scope="module")
def rep(tmp_path_factory):
    root = tmp_path_factory.mktemp("rep")
    src = build_amorphous("pe", "cg", 12, 24, 0.3, 3, root)
    vel = _with_velocities(src)
    return src, build_replicate(src / DATA_NAME, src, N, root), vel


def _lengths(df):
    return np.array([hi - lo for lo, hi in df.box])


def test_replicate_id():
    assert replicate_id("pe_cg_amorph_n40_c240_s1", 40, (2, 2, 2)) == (
        "pe_cg_amorph_n320_c240_s1_rep222"
    )
    assert replicate_id("ipp_aa_amorph_n40_c240_s1_from_ua", 40, (1, 1, 2)) == (
        "ipp_aa_amorph_n80_c240_s1_from_ua_rep112"
    )
    with pytest.raises(ReplicateError, match="not an amorphous"):
        replicate_id("pe_cg_pore_w5nm_n40_c240_s1", 40, N)
    with pytest.raises(ReplicateError, match="already replicated"):
        replicate_id("pe_cg_amorph_n320_c240_s1_rep222", 320, N)


def test_counts_ids_box_density(rep):
    src_dir, out, _ = rep
    src, df = read_data_file(src_dir / DATA_NAME), read_data_file(out / DATA_NAME)
    assert out.name == REP_ID
    r = int(np.prod(N))
    for key in ("atoms", "bonds", "angles"):
        assert df.counts[key] == r * src.counts[key]
    np.testing.assert_allclose(_lengths(df), np.array(N) * _lengths(src), atol=2e-8)
    assert [b[0] for b in df.box] == pytest.approx([b[0] for b in src.box], abs=1e-8)
    atoms, s_atoms = df.sorted_atoms(), src.sorted_atoms()
    n_src = len(s_atoms)
    assert np.array_equal(atoms[:, 0], np.arange(1, r * n_src + 1))
    mol = atoms[:, 1].astype(int)
    assert np.array_equal(mol, np.repeat(np.arange(1, 12 * r + 1), n_src // 12))
    assert np.array_equal(atoms[:, 2:4], np.tile(s_atoms[:, 2:4], (r, 1)))  # types, charges
    bonds, s_bonds = df.topology("Bonds"), src.topology("Bonds")
    k = np.repeat(np.arange(r), len(s_bonds))[:, None]
    expect = np.tile(s_bonds, (r, 1)) + np.hstack([k * len(s_bonds), 0 * k, k * n_src, k * n_src])
    assert np.array_equal(bonds, expect)
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    vol = float(np.prod(_lengths(df)))
    s_m = yaml.safe_load((src_dir / MANIFEST_NAME).read_text())
    assert m["density_g_cm3"] == pytest.approx(s_m["density_g_cm3"], rel=1e-6)
    assert m["total_mass_g_mol"] == pytest.approx(r * s_m["total_mass_g_mol"])
    assert m["density_g_cm3"] == pytest.approx(
        m["total_mass_g_mol"] / 6.02214076e23 / (vol * 1e-24), rel=1e-9
    )


def test_molecules_whole_across_seams_and_velocities(rep):
    src_dir, out, vel = rep
    src, df = read_data_file(src_dir / DATA_NAME), read_data_file(out / DATA_NAME)
    pos = df.unwrapped()  # LAMMPS's view: wrapped + image flags * box
    atoms = df.sorted_atoms()
    b = df.topology("Bonds")[:, 2:4].astype(int) - 1
    blen = np.linalg.norm(pos[b[:, 0]] - pos[b[:, 1]], axis=1)
    assert blen.max() < 0.5 * _lengths(src).min()
    s_atoms = src.sorted_atoms()
    whole = whole_molecules(s_atoms, src.topology("Bonds")[:, 2:4], _lengths(src))
    sb = src.topology("Bonds")[:, 2:4].astype(int) - 1
    s_len = np.linalg.norm(whole[sb[:, 0]] - whole[sb[:, 1]], axis=1)
    np.testing.assert_allclose(blen, np.tile(s_len, 8), atol=1e-5)
    # replica k (x fastest) is the whole source shifted by its image vector
    n_src = len(s_atoms)
    L = _lengths(src)
    for k, shift in enumerate([(i, j, m) for m in (0, 1) for j in (0, 1) for i in (0, 1)]):
        np.testing.assert_allclose(
            pos[k * n_src : (k + 1) * n_src], whole + np.array(shift) * L, atol=1e-5
        )
    assert np.all(atoms[:, 4:7] >= np.array([b[0] for b in df.box]) - 1e-6)
    v = np.array(df.sections["Velocities"], dtype=float)
    v = v[np.argsort(v[:, 0])]
    assert np.array_equal(v[:, 0], np.arange(1, 8 * n_src + 1))
    np.testing.assert_allclose(v[:, 1:], np.tile(vel, (8, 1)), rtol=1e-9)


def test_manifest_records_source_and_factors(rep):
    src_dir, out, _ = rep
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    s_m = yaml.safe_load((src_dir / MANIFEST_NAME).read_text())
    assert m["id"] == REP_ID and m["n_chains"] == 96
    assert m["counts"]["total"] == {k: 8 * v for k, v in s_m["counts"]["total"].items()}
    assert m["counts"]["per_chain"] == s_m["counts"]["per_chain"]
    assert m["formula"]["total"] == {k: 8 * v for k, v in s_m["formula"]["total"].items()}
    assert m["type_ids"] == s_m["type_ids"] and "growth" not in m
    rp = m["replicate"]
    assert rp["factors"] == [2, 2, 2] and rp["source_id"] == s_m["id"]
    assert "correlated" in rp["correlated"] and rp["max_bond_angstrom"] > 0
    s = m["source"]
    sha = hashlib.sha256((src_dir / DATA_NAME).read_bytes()).hexdigest()
    assert s["id"] == s_m["id"] and s["data_sha256"] == sha
    assert s["data_file"] == str(src_dir / DATA_NAME)


def test_bad_inputs_raise(rep, tmp_path):
    src_dir, out, _ = rep
    with pytest.raises(ReplicateError, match="already replicated"):
        build_replicate(out / DATA_NAME, out, N, tmp_path)
    with pytest.raises(ReplicateError, match="1..9"):
        build_replicate(src_dir / DATA_NAME, src_dir, (0, 2, 2), tmp_path)
    with pytest.raises(ReplicateError, match="nothing"):
        build_replicate(src_dir / DATA_NAME, src_dir, (1, 1, 1), tmp_path)
    with pytest.raises(PoreError, match="atoms"):  # data file of another system
        build_replicate(out / DATA_NAME, src_dir, N, tmp_path)
    wide = build_pore(src_dir / DATA_NAME, src_dir, 3.0, 1, tmp_path)
    with pytest.raises(ReplicateError, match="pore system"):
        build_replicate(wide / DATA_NAME, wide, N, tmp_path)


def test_cli_build_replicate(rep, tmp_path, capsys):
    src_dir, out, _ = rep
    argv = ["build", "replicate", "--data", str(src_dir / DATA_NAME), "--source", str(src_dir)]
    argv += ["--out", str(tmp_path), "--data-origin", "node:results/runs/x/prep/hold.data"]
    assert main(argv) == 0
    assert str(tmp_path / REP_ID) in capsys.readouterr().out
    assert (tmp_path / REP_ID / DATA_NAME).read_bytes() == (out / DATA_NAME).read_bytes()
    m = yaml.safe_load((tmp_path / REP_ID / MANIFEST_NAME).read_text())
    assert m["source"]["data_file"] == "node:results/runs/x/prep/hold.data"
    assert main([*argv[:6], "--n", "1", "1", "1", "--out", str(tmp_path)]) == 1
    assert "sepsim build replicate: error" in capsys.readouterr().err


def test_render_extend_reads_the_replicated_data(rep, tmp_path, monkeypatch, capsys):
    """No prep for a replicated system: extend reads systems/<id>/data.lmp given as --data,
    relative to the current directory (it does not exist relative to the run directory)."""
    import shutil

    _, out, _ = rep
    monkeypatch.chdir(tmp_path)
    shutil.copytree(out, tmp_path / "systems" / REP_ID)
    data = f"systems/{REP_ID}/data.lmp"
    argv = ["render", "extend", "--system", f"systems/{REP_ID}", "--data", data]
    assert main(argv) == 0
    deck = tmp_path / "results" / "runs" / REP_ID / "extend" / "in.extend"
    assert capsys.readouterr().out.strip().endswith("extend/in.extend")
    text = deck.read_text()
    assert f"read_data ../../../../{data} nocoeff" in text
    sha = hashlib.sha256((tmp_path / data).read_bytes()).hexdigest()
    assert sha in text and "fix md all npt temp 500 500" in text
    # and as a Slurm job (data path relative to the run directory in job.sh)
    assert main([*argv, "--job", "--time", "1:00:00"]) == 0
    job = (tmp_path / "jobs" / REP_ID / "extend" / "job.sh").read_text()
    assert f"../../../../{data}" in job


def test_pore_from_replicated_bulk_narrowed_with_small_bulk_runs(rep, tmp_path, capsys):
    """The wide pore keeps the replicate record, so narrowing reads the densities of the
    replica's source (the small bulk) under --bulk-root by default."""
    _, out, _ = rep
    wide = build_pore(out / DATA_NAME, out, 6.0, 1, tmp_path)
    assert wide.name == "pe_cg_pore500k_w6nm_n96_c24_s3_rep222"
    wm = yaml.safe_load((wide / MANIFEST_NAME).read_text())
    assert wm["replicate"]["source_id"] == "pe_cg_amorph_n12_c24_s3"
    assert wm["source"]["id"] == REP_ID
    _, sweep = _bulk_runs(tmp_path / "runs" / "pe_cg_amorph_n12_c24_s3")
    argv = ["build", "pore", "--data", str(wide / DATA_NAME), "--source", str(wide)]
    argv += [
        "--width-nm",
        "5",
        "--out",
        str(tmp_path / "sys"),
        "--bulk-root",
        str(tmp_path / "runs"),
    ]
    assert main(argv) == 0, capsys.readouterr().err
    narrow = tmp_path / "sys" / "pe_cg_pore_w5nm_n96_c24_s3_rep222"
    nm = yaml.safe_load((narrow / MANIFEST_NAME).read_text())
    lat = nm["pore"]["lateral"]
    assert lat["sources"]["sweep"]["run_dir"] == str(sweep)
    assert nm["source"]["source"]["id"] == REP_ID and nm["n_chains"] == 96
    np.testing.assert_allclose(
        lat["l_source_angstrom"], _lengths(read_data_file(wide / DATA_NAME))[:2]
    )
