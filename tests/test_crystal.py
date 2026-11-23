"""Tests for the D59 crystal reference: `sepsim build crystal`, the `crystal` deck (and
tensile on crystals), ring crystallinity, the calibration record and `sepsim analyze
crystal` end to end on a synthetic run."""

import json
import math
from pathlib import Path

import numpy as np
import pytest
import yaml

import sepsim.analyze as an
from sepsim.analysis.order import crystallinity
from sepsim.analysis.units import AVOGADRO
from sepsim.analyze_crystal import (
    analyze_crystal,
    crystal_arrays,
    elastic_constants,
    elastic_markdown,
    equal_error,
    setting_markdown,
    setting_summary,
    stem_setting,
    write_calibration,
)
from sepsim.build.crystal import CrystalError, build_crystal, crystal_id
from sepsim.build.datafile import read_data_file
from sepsim.cli import main
from sepsim.lammps.render import RenderError, default_stage, render_deck, resolve_params
from sepsim.progress import parse_deck

REPO = Path(__file__).resolve().parents[1]
CG_BULK = REPO / "systems" / "pe_cg_amorph_n40_c240_s1"
BUSING = {"a": 7.4069, "b": 4.9491, "c": 2.5511}
CG_RISE = 3.64 * math.sin(math.radians(173.0) / 2)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    root = tmp_path_factory.mktemp("crystal")
    return {
        "cg": build_crystal("cg", out=root),
        "ua": build_crystal("ua", out=root),
        "small": build_crystal("cg", 5, 7, 10, out=root),
        "root": root,
    }


@pytest.fixture(autouse=True)
def no_calibration(tmp_path, monkeypatch):
    """Tests see no calibration record unless they write one (a committed record would
    otherwise change the monitor's threshold)."""
    monkeypatch.setattr(an, "CALIBRATION_DIR", tmp_path / "calibration")


def manifest(path):
    return yaml.safe_load((path / "manifest.yaml").read_text())


def commands(deck):
    return [t for t in (raw.split("#", 1)[0].split() for raw in deck.splitlines()) if t]


# --------------------------------------------------------------------------- builder


def test_ids_counts_and_lattice_densities(built):
    cg, ua = manifest(built["cg"]), manifest(built["ua"])
    assert built["cg"].name == crystal_id("cg", 7, 10, 27) == "pe_cg_crystal_7x10x27_s1"
    assert built["ua"].name == "pe_ua_crystal_7x10x40_s1"
    assert cg["n_chains"] == ua["n_chains"] == 140  # 2 chains per a x b cell
    assert cg["counts"]["total"]["atoms"] == 140 * 27
    assert ua["counts"]["total"]["atoms"] == 140 * 80
    for m in (cg, ua):
        per = m["counts"]["per_chain"]
        assert per["bonds"] == per["atoms"] == per["angles"]  # rings: no ends
    assert (
        ua["counts"]["per_chain"]["dihedrals"] == 80 and cg["counts"]["per_chain"]["dihedrals"] == 0
    )
    # UA: the Busing cell, 4 CH2 per a x b x c
    assert ua["density_g_cm3"] == pytest.approx(0.9963, abs=2e-4)
    assert ua["density_g_cm3"] == pytest.approx(ua["crystal"]["lattice"]["density_g_cm3"], abs=2e-4)
    # CG: 2 CM beads (42.0804 g/mol) per a x b x rise
    vol = BUSING["a"] * BUSING["b"] * CG_RISE * 1e-24
    assert cg["density_g_cm3"] == pytest.approx(2 * 42.0804 / AVOGADRO / vol, rel=1e-9)
    assert cg["crystal"]["rise_per_site_A"] == pytest.approx(CG_RISE)
    assert cg["crystal"]["cg"]["rise_A"] == pytest.approx(3.6332, abs=1e-4)
    box = cg["crystal"]["box_lengths_A"]
    assert box == pytest.approx([7 * BUSING["a"], 10 * BUSING["b"], 27 * CG_RISE])
    assert cg["crystal"]["area_per_chain_A2"] == pytest.approx(BUSING["a"] * BUSING["b"] / 2)
    assert cg["formula"]["per_chain"] == "C81H162" and set(cg["type_ids"]["atom"]) == {"CM"}
    assert set(ua["type_ids"]["atom"]) == {"CH2"}
    assert ua["crystal"]["ua"]["angle_deg"] == pytest.approx(
        2 * math.degrees(math.asin(BUSING["c"] / (2 * 1.54)))
    )


@pytest.mark.parametrize("res", ["cg", "ua"])
def test_stems_are_rings_bonded_across_z(built, res):
    m = manifest(built[res])
    df = read_data_file(built[res] / "data.lmp")
    atoms = df.sorted_atoms()
    lengths = np.array([hi - lo for lo, hi in df.box])
    x = atoms[:, 4:7]
    assert np.all(atoms[:, 7:10] == 0)  # written inside the box
    bonds = df.topology("Bonds")[:, 2:4] - 1
    deg = np.bincount(bonds.ravel(), minlength=len(atoms))
    assert np.all(deg == 2)  # every site has two bonded neighbours: no chain ends
    mol = atoms[:, 1].astype(int)
    assert np.all(mol[bonds[:, 0]] == mol[bonds[:, 1]])
    d = x[bonds[:, 1]] - x[bonds[:, 0]]
    across = np.abs(d[:, 2]) > lengths[2] / 2  # the bond to the stem's own z image
    assert np.bincount(mol[bonds[across, 0]]).tolist()[1:] == [1] * m["n_chains"]
    d -= lengths * np.round(d / lengths)
    want = CG_RISE if res == "cg" else 1.54
    assert np.linalg.norm(d, axis=1) == pytest.approx(np.full(len(d), want), abs=1e-5)
    # each stem's bond vectors (minimum image) add up to one box length along z
    tot = np.zeros((m["n_chains"] + 1, 3))
    np.add.at(tot, mol[bonds[:, 0]], d)
    assert tot[1:] == pytest.approx(np.tile([0.0, 0.0, lengths[2]], (m["n_chains"], 1)), abs=1e-4)
    angles = df.topology("Angles")
    assert len(angles) == len(atoms) and len(df.topology("Dihedrals")) == (
        len(atoms) if res == "ua" else 0
    )


def test_ua_setting_angle_and_bond_angle(built):
    df = read_data_file(built["ua"] / "data.lmp")
    x = df.sorted_atoms()[:, 4:7]
    lengths = np.array([hi - lo for lo, hi in df.box])
    for stem, sign in ((0, 1.0), (1, -1.0)):  # chain at (0, 0), then the one at (1/2, 1/2)
        s = x[80 * stem : 80 * stem + 3]
        a = s[0] - s[1]
        b = s[2] - s[1]
        a -= lengths * np.round(a / lengths)
        b -= lengths * np.round(b / lengths)
        ang = math.degrees(math.acos(a @ b / np.linalg.norm(a) / np.linalg.norm(b)))
        assert ang == pytest.approx(2 * math.degrees(math.asin(BUSING["c"] / 3.08)), abs=1e-3)
        u = -a[:2] / np.linalg.norm(a[:2])  # zigzag direction in the xy plane
        assert math.degrees(math.atan2(u[0], sign * u[1])) % 180 == pytest.approx(41.0, abs=1e-3)


def test_builder_options_and_refusals(built, tmp_path):
    lat = build_crystal("cg", lateral=(60.0, 60.0), out=tmp_path)
    assert lat.name == "pe_cg_crystal_8x12x27_s1"
    assert manifest(lat)["crystal"]["lateral_request_A"] == [60.0, 60.0]
    with pytest.raises(CrystalError, match="every length must exceed"):
        build_crystal("cg", 4, 10, 27, out=tmp_path)
    with pytest.raises(CrystalError, match="every length must exceed"):
        build_crystal("ua", 7, 10, 12, out=tmp_path)  # Lz 30.6 A < 2 (14 + 2)
    with pytest.raises(CrystalError, match="resolution"):
        build_crystal("aa", out=tmp_path)
    with pytest.raises(CrystalError, match="not both"):
        build_crystal("cg", na=7, lateral=(60.0, 60.0), out=tmp_path)


def test_cli_build_crystal(tmp_path, capsys):
    assert (
        main(
            [
                "build",
                "crystal",
                "--res",
                "cg",
                "--na",
                "5",
                "--nb",
                "7",
                "--nz",
                "10",
                "--out",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert capsys.readouterr().out.strip() == str(tmp_path / "pe_cg_crystal_5x7x10_s1")
    assert main(["build", "crystal", "--res", "cg", "--na", "2", "--out", str(tmp_path)]) == 1
    assert "every length must exceed" in capsys.readouterr().err


# --------------------------------------------------------------------------- deck


def test_crystal_deck_holds_aniso_and_outputs(built):
    deck = render_deck("crystal", built["cg"])
    cmds = commands(deck)
    assert [
        "fix",
        "relax",
        "all",
        "box/relax",
        "aniso",
        "1",
        "couple",
        "none",
        "vmax",
        "0.001",
    ] in cmds
    md = [c for c in cmds if c[:3] == ["fix", "md", "all"]]
    assert len(md) == 4
    for c, t in zip(md, (298.15, 363.15, 403.15, 433.15), strict=True):
        assert c[3:8] == ["npt", "temp", str(t), str(t), "1000"]
        assert c[8:] == ["aniso", "1", "1", "10000", "couple", "none"]
    assert [c[1] for c in cmds if c[0] == "write_data"] == [
        "minimized.data",
        "hold_25C.data",
        "hold_90C.data",
        "hold_130C.data",
        "hold_160C.data",
    ]
    assert [
        "velocity",
        "all",
        "create",
        "298.15",
        "1",
        "mom",
        "yes",
        "rot",
        "no",
        "dist",
        "gaussian",
    ] in cmds
    assert cmds.index(["reset_timestep", "0"]) < cmds.index(
        next(c for c in cmds if c[0] == "velocity")
    )
    assert ["pair_style", "lj/spica", "15"] in cmds and "pxx" in first(cmds, "thermo_style")


def first(cmds, name):
    return next(c for c in cmds if c[0] == name)


def test_crystal_deck_segments_parse(built, tmp_path):
    for res, steps in (("cg", 1_000_000), ("ua", 1_000_000)):
        path = tmp_path / f"in.crystal.{res}"
        path.write_text(render_deck("crystal", built[res]))
        segs = parse_deck(path)
        assert [s.command for s in segs] == ["minimize"] + ["run"] * 4
        holds = segs[1:]
        assert [s.sweep_kind for s in holds] == ["hold"] * 4
        assert [s.t_c for s in holds] == [25.0, 90.0, 130.0, 160.0]
        assert all(s.steps == steps and s.ensemble == "npt" for s in holds)
        assert [s.dcd for s in holds] == [
            ["seg01_hold_25C.dcd"],
            ["seg02_hold_90C.dcd"],
            ["seg03_hold_130C.dcd"],
            ["seg04_hold_160C.dcd"],
        ]
        assert holds[0].dump_every == [1000 if res == "cg" else 5000]


def test_crystal_deck_ramp_smoke_and_bad_params(built, tmp_path):
    deck = render_deck("crystal", built["ua"], preset="smoke", overrides={"ramp": "yes"})
    path = tmp_path / "in.crystal"
    path.write_text(deck)
    segs = parse_deck(path)
    assert [s.steps for s in segs[1:]] == [1000] * 4 + [500]
    assert segs[-1].name.startswith("Segment 5: ramp from 160 to 200 C")
    assert segs[-1].sweep_kind is None and segs[-1].dcd == ["seg05_ramp_160C_200C.dcd"]
    assert "fix md all npt temp 433.15 473.15 200 aniso 1 1 2000 couple none" in deck
    assert "write_data ramp_200C.data" in deck
    assert resolve_params("cg", None, None, "crystal")["crystal_hold_ps"] == 10000.0
    assert resolve_params("ua", None, None, "crystal")["crystal_hold_ps"] == 2000.0
    for bad, match in (
        ({"crystal_grid_c": "25,25"}, "distinct"),
        ({"crystal_grid_c": "25,x"}, "bad point"),
        ({"ramp": "yes", "ramp_to_c": "150"}, "above the last hold"),
        ({"crystal_hold_ps": "0"}, "must be > 0"),
    ):
        with pytest.raises(RenderError, match=match):
            resolve_params("cg", None, bad, "crystal")
    no_relax = render_deck("crystal", built["cg"], overrides={"min_box_relax": "no"})
    assert "box/relax" not in no_relax


def test_crystal_gating_and_tensile(built, tmp_path):
    for protocol in ("prep", "sweep", "benchmark", "extend", "diffuse", "cavitation", "pore"):
        with pytest.raises(RenderError, match="crystal system"):
            render_deck(protocol, built["cg"], data=built["cg"] / "data.lmp", preset="smoke")
    with pytest.raises(RenderError, match="for crystal systems"):
        render_deck("crystal", CG_BULK)
    deck = render_deck("tensile", built["cg"], data=built["cg"] / "data.lmp", preset="smoke")
    md = [c for c in commands(deck) if c[:2] == ["fix", "md"]]
    # default axes x, y only (z would stretch the infinite stems), lateral couple none
    assert len(md) == 2 and all(c[-2:] == ["couple", "none"] for c in md)
    assert [c[5] for c in commands(deck) if c[:3] == ["fix", "pull", "all"]] == ["x", "y"]
    assert "#   axes = x,y" in deck and "independent (crystal, D59)" in deck
    assert "stretches the infinite covalent stems" not in deck
    with_z = render_deck(
        "tensile",
        built["cg"],
        data=built["cg"] / "data.lmp",
        preset="smoke",
        overrides={"axes": "x,y,z"},
    )
    assert [c[5] for c in commands(with_z) if c[:3] == ["fix", "pull", "all"]] == ["x", "y", "z"]
    assert with_z.count("stretches the infinite covalent stems") == 1
    bulk = render_deck("tensile", CG_BULK, data=CG_BULK / "data.lmp", preset="smoke")
    assert [c[-1] for c in commands(bulk) if c[:2] == ["fix", "md"]] == ["yz", "xz", "xy"]
    assert "coupled" in bulk and "D59" not in bulk


# --------------------------------------------------------------------------- crystallinity


def _frame(system):
    arr = crystal_arrays(system)
    df = read_data_file(system / "data.lmp")
    box = np.array([hi - lo for lo, hi in df.box])
    return arr, df.sorted_atoms()[:, 4:7], box


@pytest.mark.parametrize("res", ["cg", "ua"])
def test_perfect_crystal_ring_fraction_one_cluster(built, res):
    arr, x, box = _frame(built[res])
    par = an.crystal_parameters(arr["manifest"])
    order = np.concatenate(arr["chains"])
    cid = np.concatenate([np.full(len(c), k) for k, c in enumerate(arr["chains"])])
    r = crystallinity(
        x[order],
        cid,
        box,
        r_c=par["r_c_A"],
        threshold=0.4,
        half_span=par["half_span"],
        l_proj=par["l_proj_A"],
        ring=True,
    )
    assert r.n_sites == len(x)  # ring chords: no chain-end sites
    assert r.fraction == pytest.approx(1.0) and np.nanmin(r.p2) == pytest.approx(1.0)
    assert r.n_clusters == 1 and r.largest_cluster == len(x)
    lin = crystallinity(
        x[order],
        cid,
        box,
        r_c=par["r_c_A"],
        threshold=0.4,
        half_span=par["half_span"],
        l_proj=par["l_proj_A"],
    )
    assert lin.n_sites == len(x) - 2 * len(arr["chains"])  # without ring: two end sites


def _record(threshold, r_c=6.3084, ff="sdk_cg.yaml"):
    return {"threshold": threshold, "r_c_A": r_c, "forcefield": {"file": ff}, "date": "2026-11-13"}


def test_calibration_record_round_trip_and_monitor(built, tmp_path):
    man = manifest(built["small"])
    assert an.crystal_calibration(man) is None
    assert an.monitor_settings(man)["label"] == an.CRYSTAL_LABEL
    # synthetic distributions: crystal p2 near 1, melt near 0
    rng = np.random.default_rng(3)
    c = np.clip(rng.normal(0.93, 0.04, 5000), -0.5, 1.0)
    m = np.clip(rng.normal(0.05, 0.2, 5000), -0.5, 1.0)
    thr, err = equal_error(c, m)
    assert 0.6 < thr < 0.85 and err < 0.01
    path = write_calibration(_record(thr), an.calibration_path("cg"))
    assert path == an.CALIBRATION_DIR / "calibration_cg_pe.json"
    rec = an.crystal_calibration(man)
    assert rec["threshold"] == pytest.approx(thr) and rec["_path"] == path
    st = an.monitor_settings(man)
    assert st["threshold"] == pytest.approx(thr) and st["label"].startswith("calibrated (")
    assert st["calibration"] == "calibration_cg_pe.json"
    # the D56 monitor on the perfect crystal (linear chords) with the calibrated threshold
    arr, x, box = _frame(built["small"])
    tr = {"bb": x[None], "box": np.array([[*box, 90.0, 90.0, 90.0]])}
    mon = an.crystallinity_monitor(tr, arr["chains"], man)
    assert mon["fraction"]["mean"] == pytest.approx(1.0) and mon["threshold"] == pytest.approx(thr)
    assert mon["label"].startswith("calibrated") and mon["calibration"] == "calibration_cg_pe.json"
    # a record of another force-field file is ignored; UA has no record
    write_calibration(_record(thr, ff="other.yaml"), path)
    assert an.crystal_calibration(man) is None
    assert an.monitor_settings(manifest(built["ua"]))["label"] == an.CRYSTAL_LABEL


# --------------------------------------------------------------------------- analyze crystal

HOLDS_C = (25.0, 90.0, 130.0, 160.0)
ALPHA = {"a": 4e-4, "b": 3e-4, "c": -1e-4}


def _box(box0, t_c):
    return box0 * np.array([1 + ALPHA[k] * (t_c - 25.0) for k in "abc"])


def _write_dcd(path, frames, boxes):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(frames.shape[1], trajectory=True)
    with DCDWriter(str(path), frames.shape[1]) as w:
        for x, b in zip(frames, boxes, strict=True):
            u.atoms.positions = x
            u.dimensions = [*b, 90.0, 90.0, 90.0]
            w.write(u.atoms)


def _fake_run(built, root, melted_160=True):
    """A crystal run of the small CG crystal: the smoke deck with 20 ps holds, a log whose
    box follows ALPHA, DCDs of the scaled lattice (+ noise); the 160 C hold has melted
    (random positions)."""
    system = built["small"]
    run = root / "runs" / system.name / "crystal"
    run.mkdir(parents=True)
    deck = render_deck(
        "crystal",
        system,
        preset="smoke",
        overrides={"crystal_hold_ps": "20", "crystal_dump_ps": "2", "thermo_ps": "0.1"},
    )
    (run / "in.crystal").write_text(deck)
    man = manifest(system)
    mass = man["total_mass_g_mol"]
    _arr, x0, box0 = _frame(system)
    rng = np.random.default_rng(5)
    head = "   Step   Time   Temp   Press   Volume   Density   Lx   Ly   Lz   CPU\n"
    log, step = head + "  0 0 0 0 1 1 1 1 1 0\n  10 0 0 0 1 1 1 1 1 0\n", 0
    log += "Loop time of 1 on 1 procs for 10 steps with 700 atoms\n"
    for k, t_c in enumerate(HOLDS_C):
        box = _box(box0, t_c)
        log += head
        for s in range(step, step + 2001, 10):
            b = box * (1 + rng.normal(0, 2e-4, 3))
            v = float(np.prod(b))
            log += (
                f" {s} {s * 10.0} {t_c + 273.15 + rng.normal(0, 2)} 1 {v}"
                f" {mass / AVOGADRO / (v * 1e-24)} {b[0]} {b[1]} {b[2]} 0\n"
            )
        log += "Loop time of 1 on 1 procs for 2000 steps with 700 atoms\n"
        step += 2000
        frames = np.array([x0 * box / box0 + rng.normal(0, 0.1, x0.shape) for _ in range(11)])
        if melted_160 and t_c == 160.0:
            frames = rng.uniform(0, box, (11, *x0.shape))
        _write_dcd(run / f"seg{k + 1:02d}_hold_{t_c:g}C.dcd", frames.astype(np.float32), [box] * 11)
    (run / "log.lammps").write_text(log)
    (run / "run_manifest.json").write_text(json.dumps({"status": "finished", "hostname": "n"}))
    systems = root / "systems"
    systems.mkdir()
    (systems / system.name).symlink_to(system)
    (systems / CG_BULK.name).symlink_to(CG_BULK)
    return run, systems


def _fake_melt(root, systems):
    """A melt sweep hold of the committed CG C240 box: one hold DCD of its data file."""
    run = root / "melt" / "sweep"
    run.mkdir(parents=True)
    (run / "in.sweep").write_text(
        "# sepsim 0.1.0 deck: sweep\n# system pe_cg_amorph_n40_c240_s1 (cg), seed 1\n"
        "timestep 10\n\n# ---- Segment 1: hold at 25 C (298.15 K), 2 ps -> seg01_hold_25C.dcd\n"
        "fix md all npt temp 298.15 298.15 1000 iso 1 1 10000\n"
        "dump traj all dcd 50 seg01_hold_25C.dcd\nrun 200\nundump traj\nunfix md\n"
    )
    df = read_data_file(CG_BULK / "data.lmp")
    box = np.array([hi - lo for lo, hi in df.box])
    rng = np.random.default_rng(6)
    x0 = df.unwrapped()
    frames = np.array([x0 + rng.normal(0, 0.2, x0.shape) for _ in range(5)], dtype=np.float32)
    _write_dcd(run / "seg01_hold_25C.dcd", frames, [box] * 5)
    return run


def test_analyze_crystal_end_to_end_and_calibration(built, tmp_path, capsys):
    run, systems = _fake_run(built, tmp_path)
    out = tmp_path / "out"
    r, out_dir = analyze_crystal(run, out=out, systems=systems)
    assert out_dir == out and r["settings"]["label"] == an.CRYSTAL_LABEL
    holds = r["holds"]
    assert [h["t_set_c"] for h in holds] == list(HOLDS_C) and all(h["done"] for h in holds)
    assert [h["stable"] for h in holds] == [True, True, True, False]
    o = holds[0]["order"]
    assert o["fraction"]["mean"] > 0.99 and o["stem_p2"]["last"] > 0.95
    assert o["largest_cluster_fraction"]["last"] > 0.99
    assert holds[3]["order"]["fraction_last"] < 0.2
    c = holds[0]["cell"]
    assert c["a_A"]["mean"] == pytest.approx(BUSING["a"], rel=1e-3)
    assert c["c_A"]["mean"] == pytest.approx(CG_RISE, rel=1e-3)
    assert c["area_vs_exp"] == pytest.approx(1.0, rel=2e-3)
    assert c["density"]["mean"] == pytest.approx(
        manifest(built["small"])["density_g_cm3"], rel=2e-3
    )
    ex = r["expansion"]
    assert ex["holds"] == [25.0, 90.0, 130.0]  # the melted hold is left out
    for k in "abc":
        assert ex[f"{k}_A"]["alpha_per_K"] == pytest.approx(ALPHA[k], rel=0.08, abs=2e-5)
    assert ex["volume_A3"]["alpha_per_K"] == pytest.approx(sum(ALPHA.values()), rel=0.08)
    # the CLI with --calibrate writes the record and reports with its threshold
    melt = _fake_melt(tmp_path, systems)
    cal = tmp_path / "cal.json"
    args = [
        "analyze",
        "crystal",
        str(run),
        "--out",
        str(out),
        "--systems",
        str(systems),
        "--calibrate",
        str(melt),
        "--calibration-out",
        str(cal),
    ]
    assert main(args) == 0, capsys.readouterr().err
    assert capsys.readouterr().out.split() == [str(cal), str(out / "results.md")]
    rec = json.loads(cal.read_text())
    assert rec["crystal"]["holds_c"] == [25.0, 90.0, 130.0]  # stem P2 of the 160 C hold fails
    assert rec["r_c_A"] == pytest.approx(1.4 * 4.506) and 0.3 < rec["threshold"] < 1.0
    assert rec["error_rate"] < 0.02
    assert [s["factor"] for s in rec["r_c_scan"]] == [1.2, 1.4, 1.6]
    assert rec["melt"]["runs"][0]["system"] == "pe_cg_amorph_n40_c240_s1"
    assert {f["name"] for f in rec["crystal"]["files"]} >= {"in.crystal", "log.lammps"}
    res = json.loads((out / "results.json").read_text())
    assert res["settings"]["threshold"] == pytest.approx(rec["threshold"])
    assert res["settings"]["label"].startswith("calibrated (cal.json")
    md = (out / "results.md").read_text()
    assert "## Calibration (D59)" in md and "## Thermal expansion (stable holds)" in md
    for p in ("cell", "order", "calibration"):
        assert (out / f"{p}.png").stat().st_size > 1000
    assert not (run / "results.md").exists()


def test_analyze_crystal_refuses_other_runs(tmp_path, capsys):
    assert main(["analyze", "crystal", str(tmp_path)]) == 1
    assert "no in.crystal" in capsys.readouterr().err


def test_progress_parses_crystal_run_without_gamma(built, tmp_path):
    from sepsim.progress import progress_report

    run, systems = _fake_run(built, tmp_path, melted_160=False)
    rep = progress_report(run, out=tmp_path / "prog", systems=systems, plots=False)
    assert rep["protocol"] == "crystal" and rep["n_segments"] == 5 and rep["n_done"] == 5
    assert [r["name"] for r in rep["segments"]][1:] == [
        f"seg 0{k} hold {t:g} C" for k, t in enumerate(HOLDS_C, 1)
    ]
    assert all("gamma" not in (r.get("stats") or {}) for r in rep["segments"])


# --------------------------------------------------------------------------- review additions


@pytest.mark.parametrize("sid", ["pe_cg_crystal_7x10x27_s1", "pe_ua_crystal_7x10x40_s1"])
def test_committed_angles_dihedrals_are_ring_tuples(sid):
    system = REPO / "systems" / sid
    m = manifest(system)
    n = m["crystal"]["sites_per_stem"]
    df = read_data_file(system / "data.lmp")
    mol = df.sorted_atoms()[:, 1].astype(int)
    for section, size in (("Angles", 3), ("Dihedrals", 4)):
        rows = df.topology(section)
        if section == "Dihedrals" and m["resolution"] == "cg":
            assert len(rows) == 0
            continue
        ids = rows[:, 2:] - 1
        assert ids.shape == (m["n_chains"] * n, size)
        assert np.all(mol[ids] == mol[ids[:, :1]])  # one stem per tuple
        local = ids - (mol[ids[:, 0]][:, None] - 1) * n  # 0-based position within the stem
        # consecutive around the ring, in either direction (the angle at site 0 is (1, 0, n-1))
        backward = (local[:, 1] - local[:, 0]) % n != 1
        local[backward] = local[backward, ::-1]
        start = local[:, 0]
        want = (start[:, None] + np.arange(size)[None, :]) % n
        assert np.array_equal(local, want)
        keys = {(int(s), int(k)) for s, k in zip(mol[ids[:, 0]], start, strict=True)}
        assert len(keys) == len(ids)  # every start once per stem: no duplicates
        assert all(len(set(t)) == size for t in local.tolist())


def test_ring_equals_linear_on_interior_sites_of_a_perturbed_crystal(built):
    from sepsim.analysis.order import chord_vectors

    arr, x, box = _frame(built["small"])
    x = x + np.random.default_rng(11).normal(0, 0.3, x.shape)
    par = an.crystal_parameters(arr["manifest"])
    order = np.concatenate(arr["chains"])
    cid = np.concatenate([np.full(len(c), k) for k, c in enumerate(arr["chains"])])
    kw = {"r_c": par["r_c_A"], "threshold": 0.4, "half_span": 1, "l_proj": par["l_proj_A"]}
    ring = crystallinity(x[order], cid, box, ring=True, **kw)
    lin = crystallinity(x[order], cid, box, **kw)
    interior = ~np.isnan(chord_vectors(x[order], cid, box, 1)[:, 0])
    u_ring = chord_vectors(x[order], cid, box, 1, ring=True)
    u_lin = chord_vectors(x[order], cid, box, 1)
    assert np.allclose(u_ring[interior], u_lin[interior])
    assert np.isnan(lin.p2[~interior]).all() and not np.isnan(ring.p2).any()
    same = interior & (ring.n_neighbours == lin.n_neighbours)  # no end site among neighbours
    assert same.sum() > 0.5 * interior.sum()
    assert np.allclose(ring.p2[same], lin.p2[same])
    assert 0.8 < np.nanmean(ring.p2) < 1.0  # perturbed, still crystalline


def test_calibration_records_rejected_or_ignored(built):
    man = manifest(built["small"])
    path = an.calibration_path("cg")
    path.parent.mkdir(parents=True, exist_ok=True)
    good = _record(0.7) | {"forcefield": dict(man["forcefield"])}
    write_calibration(good, path)
    assert an.crystal_calibration(man)["threshold"] == 0.7
    cases = [
        ({k: v for k, v in good.items() if k != "forcefield"}, "names no force-field file"),
        (good | {"forcefield": {}}, "names no force-field file"),
        (good | {"forcefield": {"file": "sdk_cg.yaml", "sha256": "0" * 64}}, "force field changed"),
    ]
    for rec, why in cases:
        write_calibration(rec, path)
        notes = []
        assert an.crystal_calibration(man, notes) is None and why in notes[0]
    # a record with the file but no sha256 still applies (nothing to compare)
    write_calibration(good | {"forcefield": {"file": "sdk_cg.yaml"}}, path)
    assert an.crystal_calibration(man) is not None
    path.write_text("{not json")
    notes = []
    assert an.crystal_calibration(man, notes) is None and "unreadable" in notes[0]
    st = an.monitor_settings(man)
    assert st["threshold"] == an.CRYSTAL_THRESHOLD and "unreadable" in st["calibration_note"]
    arr, x, box = _frame(built["small"])
    tr = {"bb": x[None], "box": np.array([[*box, 90.0, 90.0, 90.0]])}
    mon = an.crystallinity_monitor(tr, arr["chains"], man)  # does not abort
    assert mon["available"] and mon["label"] == an.CRYSTAL_LABEL
    assert "ignored" in mon["calibration_note"]


def test_tensile_stage_name_and_minimized_pair_ij(built):
    man = manifest(built["cg"])
    assert default_stage("tensile", "cg", None, man) == "tensile_25C"
    assert default_stage("tensile", "cg", {"t_c": "90"}, man) == "tensile_90C"
    deck = render_deck("tensile", built["cg"], data=built["cg"] / "data.lmp")
    assert all(c[-2:] == ["couple", "none"] for c in commands(deck) if c[:2] == ["fix", "md"])
    assert ["write_data", "minimized.data", "pair", "ij"] in commands(
        render_deck("crystal", built["cg"])
    )
    assert ["write_data", "minimized.data"] in commands(render_deck("crystal", built["ua"]))


def test_analyze_crystal_needs_resolution_for_default_calibration_path(built, tmp_path):
    from sepsim.analyze_crystal import CrystalAnalysisError

    run, systems = _fake_run(built, tmp_path)
    deck = run / "in.crystal"
    deck.write_text(deck.read_text().replace(" (cg), seed", ", seed", 1))
    melt = _fake_melt(tmp_path, systems)
    with pytest.raises(CrystalAnalysisError, match="names no resolution"):
        analyze_crystal(run, out=tmp_path / "o", systems=systems, calibrate=[melt], plots=False)


def test_elastic_constants_recover_known_compliance():
    """Correlated Gaussian strains (AR(1), 10-row correlation) with covariance S k_B T / V
    of a chosen orthorhombic compliance: E, nu and C come back within their bootstrap
    errors, the errors are of the expected size, the halves agree."""
    e_mod, nu = np.array([2.0, 3.0, 50.0]), {"xy": 0.3, "xz": 0.02, "yz": 0.03}
    s = np.diag(1.0 / e_mod)
    s[0, 1] = s[1, 0] = -nu["xy"] / e_mod[0]
    s[0, 2] = s[2, 0] = -nu["xz"] / e_mod[0]
    s[1, 2] = s[2, 1] = -nu["yz"] / e_mod[1]
    t_k, l0 = 300.0, np.array([50.0, 50.0, 100.0])
    cov = s * 1e-9 * 1.380649e-23 * t_k / (np.prod(l0) * 1e-30)  # 1/GPa -> strain^2
    chol = np.linalg.cholesky(cov)
    rng = np.random.default_rng(11)
    n, phi = 40000, 0.9
    z = rng.normal(size=(n, 3)) @ chol.T
    eps = np.empty_like(z)
    eps[0] = z[0]
    for k in range(1, n):
        eps[k] = phi * eps[k - 1] + math.sqrt(1 - phi**2) * z[k]
    lx, ly, lz = (l0 * (1 + eps)).T
    lx = np.r_[np.full(n // 9, 60.0), lx]  # an off-equilibrium start the 10% skip drops
    ly, lz = np.r_[np.full(n // 9, 40.0), ly], np.r_[np.full(n // 9, 90.0), lz]
    r = elastic_constants(lx, ly, lz, t_k, block=100)
    assert r["blocks"] == 400 and r["volume_A3"] == pytest.approx(np.prod(l0), rel=1e-4)
    g2 = (1 + phi**2) / (1 - phi**2)  # statistical inefficiency of eps^2
    for i, a in enumerate("xyz"):
        e = r["E_GPa"][a]
        assert abs(e["mean"] - e_mod[i]) < 4 * e["sem"]
        assert 0.5 < e["sem"] / e_mod[i] / math.sqrt(2 * g2 / 36000) < 2.0
    assert r["nu"]["xy"]["mean"] == pytest.approx(nu["xy"], abs=4 * r["nu"]["xy"]["sem"])
    assert r["nu"]["yx"]["mean"] == pytest.approx(nu["xy"] * e_mod[1] / e_mod[0], rel=0.1)
    c = np.linalg.inv(s)
    for key, ms in r["C_GPa"].items():
        i, j = int(key[0]) - 1, int(key[1]) - 1
        assert abs(ms["mean"] - c[i, j]) < 4 * ms["sem"] + 1e-6
    assert r["halves_disagree"] == []
    assert elastic_constants(lx[-700:], ly[-700:], lz[-700:], t_k, block=100) is None  # 6 blocks
    assert elastic_constants(lx, ly, np.full(len(lz), 90.0), t_k, block=100) is None
    md = "\n".join(elastic_markdown({"holds": [{"t_set_c": 25.0, "stable": True, "elastic": r}]}))
    assert "## Elastic constants (strain fluctuations)" in md and "| 25 | 400 |" in md


# --------------------------------------------------------------------------- setting angle


def _setting(arr, x, box):
    phi, within = stem_setting(x, [*box, 90.0, 90.0, 90.0], arr["chains"])
    return setting_summary(phi[None], within[None], arr["sublattice"]), phi


def _rotate_stems(arr, x, box, angles):
    """Each stem's xy offsets from its axis rotated by its angle (rad) about the axis."""
    y = x.copy()
    for c, t in zip(arr["chains"], angles, strict=True):
        d = x[c, :2] - x[c[0], :2]
        d -= box[:2] * np.round(d / box[:2])
        d -= d.mean(0)
        rot = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
        y[c, :2] = x[c, :2] - d + d @ rot.T
    return y


def test_setting_angle_perfect_parallel_random(built):
    arr, x, box = _frame(built["ua"])
    assert arr["sublattice"].tolist() == [1, -1] * 70  # the builder's alternating order
    s, _ = _setting(arr, x, box)
    assert s["phi_A_deg"] == pytest.approx(41.0, abs=1e-3)
    assert s["phi_B_deg"] == pytest.approx(-41.0, abs=1e-3)
    assert s["herringbone_deg"] == pytest.approx(41.0, abs=1e-3)
    assert s["H"] == pytest.approx(math.sin(math.radians(82.0)), abs=1e-5)
    assert s["abs_phi_deg"] == pytest.approx(41.0, abs=1e-3)
    for k in ("across_sd_A_deg", "across_sd_B_deg", "within_sd_deg"):
        assert s[k] == pytest.approx(0.0, abs=1e-3)
    # every stem at +41: centre stems rotated by +82 deg about their axes
    par = _rotate_stems(arr, x, box, np.where(arr["sublattice"] < 0, math.radians(-82.0), 0.0))
    p, phi_par = _setting(arr, par, box)
    assert phi_par == pytest.approx(np.full(140, 41.0), abs=1e-3)
    assert p["H"] == pytest.approx(0.0, abs=1e-5) and p["herringbone_deg"] == pytest.approx(
        0.0, abs=1e-3
    )
    # hold convention: frame 0 (the herringbone start) is dropped from the hold values
    f0 = stem_setting(x, [*box, 90.0, 90.0, 90.0], arr["chains"])
    fp = stem_setting(par, [*box, 90.0, 90.0, 90.0], arr["chains"])
    h = setting_summary(
        np.array([f0[0]] + [fp[0]] * 4), np.array([f0[1]] + [fp[1]] * 4), arr["sublattice"]
    )
    assert h["frames"] == 5 and h["frames_used"] == 4
    assert h["H"] == pytest.approx(0.0, abs=1e-5) and sum(h["hist_A"]) == 4 * 70
    assert h["first"]["H"] == pytest.approx(math.sin(math.radians(82.0)), abs=1e-5)
    assert h["series_H"][0] == pytest.approx(h["first"]["H"]) and len(h["series_H"]) == 5
    rng = np.random.default_rng(3)
    rnd = _rotate_stems(arr, x, box, rng.uniform(0, 2 * math.pi, 140))
    assert abs(_setting(arr, rnd, box)[0]["H"]) < 0.1


def test_setting_angle_cg_not_available(built, tmp_path):
    run, systems = _fake_run(built, tmp_path)
    r, _ = analyze_crystal(run, out=tmp_path / "out", systems=systems, plots=False)
    assert all(
        h["setting_angle"] == {"available": False, "notes": ["no setting angle at CG"]}
        for h in r["holds"]
    )
    assert "No setting angle at CG" in "\n".join(setting_markdown(r))
