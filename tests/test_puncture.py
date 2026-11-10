"""Puncture test (D57): film builder, deck, analysis."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import yaml
from _build_helpers import SYN_BULK, tiny_pores
from test_hole import _scaled_snapshot

from sepsim.analysis import puncture as P
from sepsim.analysis.units import AVOGADRO
from sepsim.build.amorphous import DATA_NAME, MANIFEST_NAME
from sepsim.build.datafile import read_data_file
from sepsim.build.hole import HoleError, build_film, build_hole, film_id
from sepsim.cli import main
from sepsim.lammps.render import (
    PROTOCOLS,
    RenderError,
    default_stage,
    puncture_plan,
    render_deck,
    resolve_params,
)
from sepsim.progress import parse_deck

REPO = Path(__file__).resolve().parents[1]
CG = REPO / "systems" / "pe_cg_amorph_n40_c240_s1"


def commands(deck):
    out = []
    for raw in deck.splitlines():
        tokens = raw.split("#", 1)[0].split()
        if tokens:
            out.append(tokens)
    return out


@pytest.fixture(scope="module")
def pores(tmp_path_factory):
    root = tmp_path_factory.mktemp("film")
    bulk, wide, nar = tiny_pores("pe", "cg", 12, 24, root, width_nm=3.0, bulk_table=SYN_BULK)
    snap = _scaled_snapshot(nar, 160.0, root / "hold_160C.data")
    return root, bulk, wide, nar, snap


@pytest.fixture(scope="module")
def film_sys(pores, tmp_path_factory):
    _, _, _, nar, snap = pores
    return build_film(snap, nar, 160.0, out=tmp_path_factory.mktemp("fsys"))


# --------------------------------------------------------------------------- builder


def test_film_id():
    assert (
        film_id("pe_cg_pore_w5nm_n640_c240_s1_rep441", 160) == "pe_cg_film_160C_n640_c240_s1_rep441"
    )
    assert film_id("pe_cg_pore_w5nm_n40_c240_s1", 25) == "pe_cg_film_25C_n40_c240_s1"
    with pytest.raises(HoleError):
        film_id("pe_cg_amorph_n40_c240_s1", 160)


def test_build_film_box_and_manifest(pores, film_sys):
    _, _, _, nar, snap = pores
    assert film_sys.name == "pe_cg_film_160C_n12_c24_s3"
    src, df = read_data_file(snap), read_data_file(film_sys / DATA_NAME)
    m = yaml.safe_load((film_sys / MANIFEST_NAME).read_text())
    f = m["film"]
    assert "hole" not in m and m["pore"]["kind"] == "narrow"
    lx, ly = (df.box[k][1] - df.box[k][0] for k in (0, 1))
    assert np.array(df.box[:2]) == pytest.approx(np.array(src.box[:2]), abs=1e-8)
    t_t = m["total_mass_g_mol"] / AVOGADRO / (0.312 * lx * ly * 1e-24)  # rho_bulk(160 C)
    lz = df.box[2][1] - df.box[2][0]
    assert lz == pytest.approx(t_t + 50.0, abs=1e-6)  # t_T + 5 nm gap
    assert f["lz_new"] == pytest.approx(lz) and f["film_thickness_angstrom"] == pytest.approx(t_t)
    assert f["t_c"] == 160.0 and f["gap_angstrom"] == 50.0 and f["area"] == pytest.approx(lx * ly)
    assert f["bulk_density_g_cm3"] == pytest.approx(0.312)
    atoms = df.sorted_atoms()
    z = atoms[:, 6]
    assert z.min() >= df.box[2][0] and z.max() < df.box[2][1] and np.all(atoms[:, 9] == 0)
    assert f["film_z_extent_angstrom"][0] >= df.box[2][0]
    assert f["film_z_extent_angstrom"] == pytest.approx([z.min(), z.max()], abs=1e-6)
    assert f["source"]["id"] == nar.name and len(f["source"]["data_sha256"]) == 64
    assert m["source"] == f["source"]
    vel = sorted(src.sections["Velocities"], key=lambda r: int(r[0]))
    assert sorted(df.sections["Velocities"], key=lambda r: int(r[0])) == vel
    assert np.array_equal(df.topology("Bonds"), src.topology("Bonds"))


def test_build_film_failures(pores, film_sys, tmp_path):
    _, _, wide, nar, snap = pores
    with pytest.raises(HoleError, match="160 C snapshot"):
        build_film(snap, nar, 90.0, out=tmp_path)
    with pytest.raises(HoleError, match="not a narrow pore"):
        build_film(snap, wide, 160.0, out=tmp_path)
    with pytest.raises(HoleError, match="gap must be > 0"):
        build_film(snap, nar, 160.0, gap_nm=0.0, out=tmp_path)
    with pytest.raises(HoleError, match="already a film system"):
        build_film(snap, film_sys, 160.0, out=tmp_path)
    with pytest.raises(HoleError, match="already a film system"):
        build_hole(snap, film_sys, 0.5, 160.0, out=tmp_path)


def test_cli_build_film(pores, tmp_path, capsys):
    _, _, _, nar, snap = pores
    args = ["build", "film", "--data", str(snap), "--source", str(nar), "--t-c", "160"]
    assert main([*args, "--gap-nm", "3", "--out", str(tmp_path)]) == 0
    out = Path(capsys.readouterr().out.strip())
    assert out.name == "pe_cg_film_160C_n12_c24_s3"
    assert yaml.safe_load((out / MANIFEST_NAME).read_text())["film"]["gap_angstrom"] == 30.0


# --------------------------------------------------------------------------- deck


def test_puncture_deck_round_trip(film_sys, tmp_path):
    over = {"travel_nm": "13.5", "tag": "p2"}
    text = render_deck("puncture", film_sys, overrides=over)
    deck = tmp_path / "in.puncture"
    deck.write_text(text)
    cmds = commands(text)
    m = yaml.safe_load((film_sys / MANIFEST_NAME).read_text())
    box, zmax = m["box_angstrom"], m["film"]["film_z_extent_angstrom"][1]
    xc, yc = (0.5 * (box[k][0] + box[k][1]) for k in (0, 1))
    z0 = zmax + 10.0 + 20.0
    assert ["boundary", "p", "p", "m"] in cmds
    assert "pair_modify tail no" in text and "pxx pyy pzz" in text
    tip = next(c for c in cmds if c[:2] == ["fix", "tip"])
    assert tip[3:6] == ["indent", "1", "sphere"] and tip[8:] == ["v_zc", "20", "units", "box"]
    assert [float(t) for t in tip[6:8]] == pytest.approx([xc, yc])
    shaft = next(c for c in cmds if c[:2] == ["fix", "shaft"])
    assert shaft[3:7] == ["indent", "1", "cone", "z"] and shaft[9:] == [
        "20",
        "20",
        "v_zc",
        "v_zs",
        "units",
        "box",
    ]
    assert ["fix_modify", "tip", "energy", "yes"] in cmds
    assert ["fix_modify", "shaft", "energy", "yes"] in cmds
    assert ["variable", "zs", "equal", "v_zc+200"] in cmds
    zc = [c for c in cmds if c[:2] == ["variable", "zc"]]
    assert float(zc[0][3]) == pytest.approx(z0)
    # 13.5 nm at 1 m/s = 1e-5 A/fs, dt 10 fs: 135 A / 1e-4 A per step = 1,350,000 steps
    assert zc[1][3] == f"ramp({z0:.12g},{z0 - 135.0:.12g})"
    assert [c[1] for c in cmds if c[0] == "run"] == ["20000", "1350000"]
    ave = next(c for c in cmds if c[:2] == ["fix", "pave"])
    assert ave[3:7] == ["ave/time", "1", "1000", "1000"]
    assert ave[7:-2] == [
        "v_zc",
        "f_tip[1]",
        "f_tip[2]",
        "f_tip[3]",
        "f_shaft[1]",
        "f_shaft[2]",
        "f_shaft[3]",
        "f_tip",
        "f_shaft",
        "c_thermo_temp",
        "c_tnear",
        "c_tfar",
        "c_zmin",
        "c_zmax",
        "c_thermo_press[3]",
    ]
    assert ave[-2:] == ["file", "puncture.txt"]
    assert [c[-1] for c in cmds if c[0] == "dump"] == ["settle.dcd", "puncture.dcd"]
    assert [c[4] for c in cmds if c[0] == "dump"] == ["2000", "2000"]  # 20 ps
    assert ["write_data", "punctured.data", "pair", "ij"] in cmds
    assert "fix md all nvt temp 433.15 433.15 1000" in text and "temp/partial" not in text
    segs = parse_deck(deck)
    assert [s.name for s in segs] == [
        "Stage 1: settle 200 ps NVT at 433.15 K, indenter clear of the film",
        "Stage 2: indent at 1 m/s, R 2 nm, travel 13.5 nm",
    ]
    assert [s.steps for s in segs] == [20_000, 1_350_000]
    assert all(s.ensemble == "nvt" and s.t_target_k == pytest.approx(433.15) for s in segs)
    assert segs[1].dcd == ["puncture.dcd"]
    assert default_stage("puncture", "cg", over, m) == "puncture_160C_v1_R2nm_p2"
    assert default_stage("puncture", "cg", {"indent_v_m_s": "0.5"}, m) == "puncture_160C_v0.5_R2nm"
    with pytest.raises(RenderError, match="film manifest"):
        default_stage("puncture", "cg", None, None)


def test_puncture_auto_travel_smoke_and_partial(film_sys):
    m = yaml.safe_load((film_sys / MANIFEST_NAME).read_text())
    zmin, zmax = m["film"]["film_z_extent_angstrom"]
    p = resolve_params("cg", None, {"indent_v_m_s": "10"}, "puncture")
    plan = puncture_plan(p, m["film"], m["box_angstrom"])
    want = (zmax - zmin) + 20.0 + 20.0 + 20.0  # extent + 2 clearance + R + overshoot
    assert plan["auto"] and plan["travel"] == pytest.approx(want, abs=1e-3)  # whole steps
    assert plan["n_steps"] == round(want / 1e-3)
    smoke = commands(
        render_deck("puncture", film_sys, preset="smoke", overrides={"thermostat": "partial"})
    )
    # settle 1 ps; 1 nm at 100 m/s = 1e-3 A/fs: 10 A / 0.01 A per step = 1000 steps
    assert [c[1] for c in smoke if c[0] == "run"] == ["100", "1000"]
    assert ["compute", "tpart", "all", "temp/partial", "1", "1", "0"] in smoke
    assert ["fix_modify", "md", "temp", "tpart"] in smoke
    for bad, match in (
        ({"thermostat": "langevin"}, "thermostat"),
        ({"boundary": "p m p"}, "boundary"),
        ({"indent_r_nm": "0"}, "indent_r_nm"),
        ({"travel_nm": "-1"}, "travel_nm"),
    ):
        with pytest.raises(RenderError, match=match):
            render_deck("puncture", film_sys, overrides=bad)


def test_puncture_and_film_gating(pores, film_sys, tmp_path_factory):
    _, bulk, _, nar, snap = pores
    hole = build_hole(snap, nar, 0.5, 160.0, out=tmp_path_factory.mktemp("h"))
    for sysdir in (hole, nar, bulk):
        with pytest.raises(RenderError, match="puncture"):
            render_deck("puncture", sysdir, preset="smoke")
    with pytest.raises(RenderError, match="takes the puncture protocol, not hole"):
        render_deck("hole", film_sys, preset="smoke")
    with pytest.raises(RenderError, match="takes the puncture protocol, not pore"):
        render_deck("pore", film_sys, preset="smoke")
    with pytest.raises(RenderError, match="is for bulk systems"):
        render_deck("cavitation", nar, data=nar / DATA_NAME, preset="smoke")


def test_other_decks_keep_periodic_z(pores, tmp_path_factory):
    _, _, wide, nar, snap = pores
    hole = build_hole(snap, nar, 0.5, 160.0, out=tmp_path_factory.mktemp("h2"))
    where = {"pore_relax": wide, "pore": nar, "hole": hole}
    seen = set()
    for protocol in PROTOCOLS:
        if protocol == "puncture":
            continue
        sysdir = where.get(protocol, CG)
        text = render_deck(protocol, sysdir, data=sysdir / DATA_NAME, preset="smoke")
        boundary = [c for c in commands(text) if c[0] == "boundary"]
        assert boundary and all(c == ["boundary", "p", "p", "p"] for c in boundary), protocol
        assert "boundary =" not in text  # not a resolved parameter of these protocols
        seen.add(protocol)
    assert seen == set(PROTOCOLS) - {"puncture"}


# --------------------------------------------------------------------------- analysis


F_PEAK = 2.0  # nN


def _force(d):
    """Synthetic F(d) (nN): 0 above the film, linear to F_PEAK at 4 nm, down to 10% at
    6 nm, then flat."""
    d = np.asarray(d, dtype=float)
    up = F_PEAK * np.clip(d, 0.0, 4.0) / 4.0
    down = F_PEAK * (1.0 - 0.45 * np.clip(d - 4.0, 0.0, 2.0))
    return np.where(d <= 4.0, up, down)


def test_units():
    assert P.KCAL_MOL_A_NN * 1e3 == pytest.approx(69.48, rel=1e-3)  # pN
    assert P.KCAL_MOL_AJ == pytest.approx(6.948e-3, rel=1e-3)  # 1 kcal/mol in aJ
    f, flipped = P.indenter_force({"f_tip[3]": np.array([0.0, -10.0]), "f_shaft[3]": np.zeros(2)})
    assert flipped and f[1] == pytest.approx(10.0 * P.KCAL_MOL_A_NN)
    f, flipped = P.indenter_force({"f_tip[3]": np.array([0.0, 6.0]), "f_shaft[3]": np.ones(2)})
    assert not flipped and f[1] == pytest.approx(7.0 * P.KCAL_MOL_A_NN)
    assert P.depth_nm([50.0], 20.0, 40.0)[0] == pytest.approx(1.0)


def test_curve_peak_break_and_work():
    rng = np.random.default_rng(0)
    d = np.linspace(-1.0, 9.0, 1001)
    curve = P.analyze_curve(d, _force(d), rng.normal(0.0, 0.005, 50))
    assert curve["f_peak_nN"] == pytest.approx(F_PEAK, rel=0.05)  # smoothed sharp peak
    assert curve["d_peak_nm"] == pytest.approx(4.0, abs=0.02)
    assert -0.1 < curve["d_contact_nm"] < 0.05
    # 50% of F_peak on the way down at 4 + 0.5/0.45 nm, sustained beyond 0.5 nm
    assert curve["d_break_force_nm"] == pytest.approx(4.0 + 0.5 / 0.45, abs=0.05)
    assert curve["w_peak_aJ"] == pytest.approx(0.5 * F_PEAK * 4.0, rel=0.01)
    # signal iii: the beads under the tip vanish at the frame at 5.3 nm
    frame_d = np.linspace(-1.0, 9.0, 101)
    ahead = np.where(frame_d < 5.3 - 1e-9, 40, 1)
    ahead[frame_d < 0] = 0  # above the film: clear, but before contact
    b = P.break_through(curve, frame_d, ahead)
    assert b["d_break_clear_nm"] == pytest.approx(5.3)
    assert b["d_break_nm"] == pytest.approx(5.3)
    w = 0.5 * F_PEAK * 4.0 + 0.5 * (F_PEAK + float(_force(5.3))) * 1.3
    assert b["w_break_aJ"] == pytest.approx(w, rel=0.01)
    # material stays ahead: no break-through even though the force dropped
    stuck = P.break_through(curve, frame_d, np.full(len(frame_d), 30))
    assert stuck["d_break_nm"] is None and stuck["w_break_aJ"] is None
    # force never drops: no break
    rise = P.analyze_curve(d, F_PEAK * np.clip(d, 0, None))
    assert rise["d_break_force_nm"] is None and rise["peak_at_end"]


def test_image_flag_and_indenter_counts():
    zspan = np.array([50.0, 84.0, 90.0])
    assert P.image_rows(zspan, 100.0, 15.0, "p p p").tolist() == [False, False, True]
    assert not P.image_rows(zspan, 100.0, 15.0, "p p m").any()
    lengths, axis, zc, r = (100.0, 100.0, 300.0), (50.0, 50.0), 100.0, 20.0
    pos = np.array(
        [
            [50.0, 50.0, 105.0],  # shaft
            [50.0, 50.0, 81.0],  # tip sphere (bottom at 80)
            [149.0, 50.0, 90.0],  # r = 1 via the periodic image: in the tip
            [71.0, 50.0, 105.0],  # beside the shaft
            [50.0, 50.0, 79.0],  # just ahead of the tip
            [55.0, 50.0, 71.0],  # ahead (r 5 < R/2, 9 A below the tip)
            [61.0, 50.0, 75.0],  # r 11 > R/2: not ahead
        ]
    )
    assert P.inside_count(pos, axis, lengths, zc, r) == 3
    assert P.ahead_count(pos, axis, lengths, zc, r) == 2
    bonds = np.array([[0, 1], [3, 4]])
    st = P.max_bond_stretch(pos, bonds, lengths, 20.0)
    assert st == pytest.approx(np.hypot(21.0, 26.0) / 20.0 - 1.0)
    assert P.free_hole_radius([20.0, 25.0], 20.0) == pytest.approx([0.0, 15.0])


def _write_dcd(path, frames, lengths):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(len(frames[0]), trajectory=True)
    with DCDWriter(str(path), len(frames[0])) as w:
        for pos in frames:
            u.atoms.positions = pos
            u.dimensions = [*lengths, 90.0, 90.0, 90.0]
            w.write(u.atoms)


def _puncture_run(film_sys, run, z_top, tag=""):
    """A smoke puncture deck (travel 10 nm at 100 m/s) and a synthetic puncture.txt:
    settle rows with noise, then F(d) of :func:`_force` with d from the tip ramp."""
    over = {"travel_nm": "10"} | ({"tag": tag} if tag else {})
    run.mkdir(parents=True)
    deck = render_deck("puncture", film_sys, preset="smoke", overrides=over, deck_dir=run)
    (run / "in.puncture").write_text(deck)
    m = yaml.safe_load((film_sys / MANIFEST_NAME).read_text())
    p = resolve_params("cg", "smoke", over, "puncture")
    plan = puncture_plan(p, m["film"], m["box_angstrom"])
    rng = np.random.default_rng(1)
    lines = [
        "# Time-averaged data for fix pave",
        (
            "# TimeStep v_zc f_tip[1] f_tip[2] f_tip[3] f_shaft[1] f_shaft[2] f_shaft[3] f_tip"
            " f_shaft c_thermo_temp c_tnear c_tfar c_zmin c_zmax c_thermo_press[3]"
        ),
    ]
    for step in range(10, 100 + plan["n_steps"] + 1, 10):
        k = max(step - 100, 0)
        zc = plan["z0"] - plan["travel"] * k / plan["n_steps"]
        d = (z_top - (zc - plan["r_a"])) / 10.0
        f = (float(_force(d)) if step > 100 else rng.normal(0, 0.005)) / P.KCAL_MOL_A_NN
        lines.append(
            f"{step} {zc:.8g} 0 0 {0.7 * f:.8g} 0 0 {0.3 * f:.8g} 0 0 433 434 433"
            f" {z_top - 60.0:.8g} {z_top:.8g} 1"
        )
    (run / "puncture.txt").write_text("\n".join(lines) + "\n")
    return plan


def test_analyze_puncture_report_and_cli(film_sys, tmp_path, monkeypatch, capsys):
    from sepsim.analyze_puncture import analyze_puncture, write_results

    monkeypatch.chdir(tmp_path)
    m = yaml.safe_load((film_sys / MANIFEST_NAME).read_text())
    z_top = m["film"]["film_z_extent_angstrom"][1]
    runs = tmp_path / "runs" / film_sys.name
    plan = _puncture_run(film_sys, runs / "puncture_160C_v100_R2nm", z_top)
    report, out = analyze_puncture([runs / "puncture_160C_v100_R2nm"], systems=film_sys.parent)
    assert out == Path("results/analysis") / film_sys.name / "puncture_160C_v100_R2nm"
    r = report["runs"][0]
    c = r["curve"]
    assert c["f_peak_nN"] == pytest.approx(F_PEAK, rel=0.05)
    assert c["d_peak_nm"] == pytest.approx(4.0, abs=0.02)
    assert c["w_peak_aJ"] == pytest.approx(4.0, rel=0.01)
    assert c["d_break_force_nm"] == pytest.approx(4.0 + 0.5 / 0.45, abs=0.05)
    # no DCD: signal iii not available, so no break-through verdict
    assert r["break"]["d_break_nm"] is None and any("no puncture.dcd" in n for n in r["notes"])
    assert r["diagnostics"]["t_near_K"] == pytest.approx(434.0)
    assert "lz_growth_A" in r["diagnostics"] and not r["flags"]
    write_results(report, tmp_path / "res")
    js = json.loads((tmp_path / "res" / "results.json").read_text())
    assert js["runs"][0]["curve"]["f_peak_nN"] == pytest.approx(c["f_peak_nN"])
    md = (tmp_path / "res" / "results.md").read_text()
    assert "Caveats" in md and "chain pull-out" in md and "| F_peak |" in md
    for png in ("force_depth.png", "puncture_vs_T.png", "rate_radius.png", "diagnostics.png"):
        assert (out / png).is_file()
    # a second position with a DCD of the (static) film: frames, diagnostics, maps
    run2 = runs / "puncture_160C_v100_R2nm_p2"
    _puncture_run(film_sys, run2, z_top, tag="p2")
    df = read_data_file(film_sys / DATA_NAME)
    pos = df.sorted_atoms()[:, 4:7].astype(float)
    lengths = [df.box[k][1] - df.box[k][0] for k in range(3)]
    _write_dcd(run2 / "puncture.dcd", [pos] * 5, lengths)
    assert main(["analyze", "puncture", str(runs / "puncture_160C_v100_R2nm"), str(run2),
                 "--systems", str(film_sys.parent)]) == 0  # fmt: skip
    cmp_dir = tmp_path / "results/analysis" / film_sys.name / "puncture_compare"
    js = json.loads((cmp_dir / "results.json").read_text())
    r2 = js["runs"][1]
    assert len(r2["frames"]) == 5 and r2["frames"][1]["t_ps"] == pytest.approx(0.1)
    assert r2["frames"][1]["zc"] == pytest.approx(
        plan["z0"] - plan["travel"] * 10 / plan["n_steps"]
    )
    st = {f["stretch"] for f in r2["frames"]}
    assert len(st) == 1 and r2["diagnostics"]["max_bond_stretch"] < 0.2  # static frames
    assert r2["surfaces_from"].startswith("puncture.dcd")
    (pooled,) = js["pooled"]
    assert len(pooled["runs"]) == 2 and pooled["summary"]["f_peak_nN"]["n"] == 2
    assert (cmp_dir / "film_maps.png").is_file()
    assert main(["analyze", "puncture", str(tmp_path)]) == 1
    assert "no in.puncture" in capsys.readouterr().err
