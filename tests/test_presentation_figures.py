"""scripts/presentation_figures.py: series lookup by id, empty inputs (pending placeholders),
synthetic hole results, PyMOL helpers, and a real-data smoke run."""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
APPENDIX_FIGS = (
    "fig2_1_cn_sem",
    "fig3_1_cp_chain_length",
    "fig3_2_convergence",
    "fig4_1_ree_length",
)
ALL_FIGS = (
    "fig1_models",
    "fig2_equilibration",
    "fig3_thermo",
    "fig4_chains",
    "fig5_pore",
    "fig6_dynamics",
    "fig7_mechanics",
    "fig8_holes",
)


def _load(name):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pf():
    return _load("presentation_figures")


@pytest.fixture(scope="module")
def prm():
    return _load("pymol_render")


def test_series_by_id(pf):
    s = pf.series_info("ipp_ua_amorph_n40_c240_s1")
    assert (s["polymer"], s["res"], s["kind"], s["primary"]) == ("ipp", "ua", "bulk", True)
    assert s["label"] == "UA iPP" and s["marker"] == "s" and s["color"] == pf.RES_COLOR["ua"]
    assert s["rls"] == "--"
    aa = pf.series_info("pe_aa_amorph_n40_c240_s1_from_ua")
    assert aa["res"] == "aa" and aa["primary"]
    assert pf.superseded("pe_aa_amorph_n40_c240_s1", {"pe_aa_amorph_n40_c240_s1_from_ua"})
    long = pf.series_info("pe_cg_amorph_n40_c1500_s1")
    assert not long["primary"] and long["label"] == "CG PE C1500" and long["mfc"] == "white"
    pore = pf.series_info("pe_cg_pore_w5nm_n320_c240_s1_rep222")
    assert pore["kind"] == "pore" and pore["width_nm"] == 5.0 and not pore["primary"]
    assert pore["label"] == "CG PE C240 (320 chains)"
    assert pf.pore_label(pore) == "CG PE C240 5 nm pore (320 chains)"
    small = pf.series_info("pe_cg_pore_w5nm_n40_c240_s1")
    assert small["label"] == "CG PE C240" and small["chains_label"] == "CG PE C240 (40 chains)"
    assert pf.pore_label(small) == "CG PE C240 5 nm pore (40 chains)"
    assert pf.series_info("pe_cg_amorph_n640_c240_s1_rep441")["label"] == "CG PE C240 (640 chains)"
    assert pf.series_info("pe_cg_pore500k_w10nm_n40_c240_s1")["kind"] == "wide_pore"
    assert pf.series_info("pe_cg_hole_r3nm_160C_n320_c240_s1_rep222")["kind"] == "hole"
    assert pf.series_info("pe_cg_amorph_n40_c240_s1")["label"] == "CG PE C240"
    assert pf.series_info("not_an_id") is None
    assert pf.t_color(226.85) == pf.GREY_500K and pf.t_label(226.85) == "500 K"


def test_empty_inputs_write_placeholders(pf, tmp_path):
    data = pf.load_data(tmp_path / "a", tmp_path / "s", [tmp_path / "r"], render=False)
    out = pf.build(data, tmp_path / "out", log=lambda *_: None)
    names = {p.name for p in out["written"]}
    for fig in ALL_FIGS:
        assert {f"{fig}.png", f"{fig}.pdf", f"{fig}.svg"} <= names
    for fig in APPENDIX_FIGS:
        assert (tmp_path / "out" / "appendix" / f"{fig}.png").is_file()
    text = out["readme"].read_text()
    for fig in ALL_FIGS + APPENDIX_FIGS:
        assert f"## {fig}" in text
    assert out["infos"]["fig8_holes"]["pending"] and out["infos"]["fig8_holes"]["a"]["pending"]


def _hole_result(t_c=160.0, variant="free", closes=True, r0=30.0):
    frames = []
    for k in range(12):
        t = 0.1 * k
        r = max(r0 - 40.0 * t, 0.0) if closes else r0 - 2.0 * t
        frames.append(
            {
                "t_ns": t,
                "phase": "production",
                "r_eff": r,
                "r_min": r * 0.9,
                "slab_z": [40.0, 50.0, 60.0, 70.0],
                "slab_r": [r * 1.1, r * 0.9, r * 0.9, r * 1.1],
            }
        )
    return {
        "radius_nominal_nm": r0 / 10,
        "t_c": t_c,
        "variant": variant,
        "film_thickness_angstrom": 130.0,
        "r_t0": r0,
        "t_close_ns": 0.8 if closes else None,
        "production_ns": 1.1,
        "frames": frames,
    }


def test_hole_panels_use_results(pf, tmp_path):
    runs = {
        ("pe_cg_hole_r3nm_160C_n320_c240_s1_rep222", "hole_free"): _hole_result(),
        ("pe_cg_hole_r3nm_25C_n320_c240_s1_rep222", "hole_ramp_held"): _hole_result(
            25.0, "annulus d=2.5 nm, held, ramp", closes=False
        ),
        ("pe_cg_hole_r8nm_160C_n640_c240_s1_rep441", "hole_free"): _hole_result(r0=80.0),
    }
    for (sid, stage), res in runs.items():
        d = tmp_path / "a" / sid / stage
        d.mkdir(parents=True)
        (d / "results.json").write_text(json.dumps(res))
    data = pf.load_data(tmp_path / "a", tmp_path / "s", [], render=False)
    out = pf.build(data, tmp_path / "out", only=["fig8"], log=lambda *_: None)
    info = out["infos"]["fig8_holes"]
    assert not info["pending"] and len(info["b"]) == 3
    assert info["c"]["times"][0] == 0.0 and len(info["c"]["times"]) <= 5
    rows = {r["sid"]: r for r in info["d"]}
    assert rows["pe_cg_hole_r3nm_160C_n320_c240_s1_rep222"]["closed"]
    assert not rows["pe_cg_hole_r3nm_25C_n320_c240_s1_rep222"]["closed"]
    assert rows["pe_cg_hole_r8nm_160C_n640_c240_s1_rep441"]["thin"]
    assert rows["pe_cg_hole_r3nm_160C_n320_c240_s1_rep222"]["x"] == pytest.approx(30 / 130)
    caption = pf.caption_fig8(info, data)
    assert "Pending" not in caption and "R₀/h" in caption


def test_pdb_writer_and_render_fallback(prm, tmp_path, monkeypatch):
    pos = np.array([[0.0, 0.0, 0.0], [1.5, 0.0, 0.0], [2.0, 1.4, 0.0]])
    txt = prm.pdb_text(pos, "C", [1, 1, 2], [[0, 1], [1, 2]], names=["C3", "C2", "C2"])
    lines = txt.splitlines()
    assert lines[0].startswith("HETATM    1  C3 ") and lines[0][30:38].strip() == "0.000"
    assert "CONECT    1    2" in txt and lines[-1] == "END"
    assert len(prm.box_edges(prm.box_corners([0, 0, 0], [1, 1, 1]))) == 12
    monkeypatch.setattr(prm, "pymol_exe", lambda: None)
    png, status = prm.render("x", {"a.pdb": txt}, ["load a.pdb"], tmp_path, (64, 48))
    assert png is None and status == "no pymol on PATH"
    (tmp_path / "x.png").write_bytes(b"old")
    png, status = prm.render("x", {"a.pdb": txt}, ["load a.pdb"], tmp_path, (64, 48))
    assert png == tmp_path / "x.png" and status.startswith("stale cache")


@pytest.mark.skipif(shutil.which("pymol") is None, reason="pymol not installed")
def test_pymol_render_and_cache(prm, tmp_path):
    pos = np.array([[0.0, 0.0, 0.0], [1.5, 0.0, 0.0], [2.0, 1.4, 0.0]])
    files = {"a.pdb": prm.pdb_text(pos, "C", [1, 1, 1], [[0, 1], [1, 2]])}
    body = [*prm.style_lines(), "load a.pdb, a", "show sticks", *prm.view_lines(4, 3, 80, 60, 10)]
    png, status = prm.render("t", files, body, tmp_path, (80, 60))
    assert status == "rendered" and png.stat().st_size > 0
    assert prm.render("t", files, body, tmp_path, (80, 60))[1] == "cached"


@pytest.mark.skipif(
    not (REPO / "results/analysis/pe_cg_amorph_n40_c240_s1/sweep/results.json").is_file(),
    reason="committed CG analysis not present",
)
def test_real_data_smoke(pf, tmp_path):
    data = pf.load_data(
        REPO / "results/analysis", REPO / "systems", [REPO / "results/run_sidecars"], render=False
    )
    out = pf.build(
        data, tmp_path, only=["fig2", "fig3", "fig4", "fig5", "fig6", "fig7"], log=lambda *_: None
    )
    assert (tmp_path / "fig3_thermo.png").stat().st_size > 10_000
    infos = out["infos"]
    assert "CG PE C240" in infos["fig3_thermo"]["a"]["series"]
    assert infos["fig7_mechanics"]["rates"] == [1e8, 1e9]
    assert any(r["t_1e_ns"] > 0 for r in infos["fig2_equilibration"]["a"])
    assert "CG PE C240" in infos["fig4_chains"]["a"]
    gam = infos["fig5_pore"]["b"]
    assert gam["CG PE C240 5 nm pore (40 chains)"]["dgdT"] < 0
    assert gam["CG PE C240 5 nm pore (320 chains)"]["dgdT"] < 0
    cap5 = pf.caption_fig5(infos["fig5_pore"], data)
    assert "Wu" not in cap5 and "% shallower than the Moreira slope" in cap5
    d = infos["fig6_dynamics"]["a"]["CG PE C240"]
    assert any(not p["bound"] for p in d)  # the diffusive 130/160 C long holds
    assert all(p["D_shown"] == pytest.approx(p["D"] / pf.CG_TIME_FACTOR) for p in d)
    longs = infos["fig6_dynamics"]["appendix"]["fig6_1_dynamics_curves"]["b"]["CG PE C240"]
    assert {t for t, *_ in longs} == {25.0, 90.0, 130.0, 160.0}
    # local alpha_V: one point per window of 5 consecutive sweep temperatures, CG ~7e-4/K
    loc = infos["fig3_thermo"]["b"]["CG PE C240"]["local"]
    assert len(loc) == 11 and all(6.0 < a < 8.0 for _, a, _ in loc)
    for name, info in infos.items():
        assert pf.CAPTIONS[name](info, data).startswith("**Figure")
    for name, (parent, fn) in pf.APPENDIX_CAPTIONS.items():
        assert (tmp_path / "appendix" / f"{name}.png").is_file()
        assert fn(infos[parent]["appendix"][name], data).startswith("**Figure")


def _with_steps(src: Path, dst: Path, sid: str) -> None:
    """Copy an analysis tree and give ``sid``'s sweep a synthetic ``steps`` list (the
    per-step extension of `sepsim analyze sweep`): each step takes the nearest hold's
    kappa and static chain results, scaled slightly with T."""
    shutil.copytree(src, dst)
    p = dst / sid / "sweep" / "results.json"
    r = json.loads(p.read_text())
    holds = r["holds"]
    steps = []
    for seg in r["segments"]:
        if seg["kind"] != "step":
            continue
        h = min(holds, key=lambda h: abs(h["t_c"] - seg["t_set_c"]))
        f = 1 + 0.001 * (seg["t_set_c"] - h["t_c"])
        tr = {k: h["traj"][k] for k in ("rg", "ree", "c_n", "crystallinity")}
        tr = json.loads(json.dumps(tr))
        tr["rg"]["rg_A"]["mean"] *= f
        tr["available"], tr["frames"] = True, 25
        kap = dict(h["kappa"], kappa_T_GPa=h["kappa"]["kappa_T_GPa"] * f)
        steps.append({"index": seg["index"], "t_c": seg["t_set_c"], "kappa": kap, "traj": tr})
    r["steps"] = steps
    p.write_text(json.dumps(r))


@pytest.mark.skipif(
    not (REPO / "results/analysis/pe_cg_amorph_n40_c240_s1/sweep/results.json").is_file(),
    reason="committed CG analysis not present",
)
def test_sweep_steps_drawn_when_present(pf, tmp_path):
    sid = "pe_cg_amorph_n40_c240_s1"
    _with_steps(REPO / "results/analysis", tmp_path / "a", sid)
    data = pf.load_data(tmp_path / "a", REPO / "systems", [], render=False)
    out = pf.build(data, tmp_path / "out", only=["fig3", "fig4"], log=lambda *_: None)
    f3, f4 = out["infos"]["fig3_thermo"], out["infos"]["fig4_chains"]
    assert f3["c_steps"] and len(f3["c_step_rows"]["CG PE C240"]) == 14
    assert "5 ns sweep step" in pf.caption_fig3(f3, data)
    assert f4["keys"]["steps"] and f4["keys"]["long"][2]  # long holds: CG only
    rows = f4["a"]["CG PE C240"]
    assert sum(src == "step" for _, src, *_ in rows) == 14
    assert all(not rel for _, src, _, rel in rows if src == "step")  # inherited
    assert "Small open = 5 ns sweep steps" in pf.caption_fig4(f4, data)
    app = f4["appendix"]["fig4_1_ree_length"]
    assert "step" not in {src for _, src, _ in app["b"]["CG PE C240"]}  # 4.1b: no steps
    assert "Small open" in pf.caption_fig4_1(app, data)
    # without the key (the committed results.json files): no step points or captions
    data0 = pf.load_data(REPO / "results/analysis", REPO / "systems", [], render=False)
    out0 = pf.build(data0, tmp_path / "out0", only=["fig3", "fig4"], log=lambda *_: None)
    assert not out0["infos"]["fig3_thermo"].get("c_steps")
    assert not out0["infos"]["fig4_chains"]["keys"]["steps"]
    assert "5 ns sweep step" not in pf.caption_fig4(out0["infos"]["fig4_chains"], data0)


def test_summary_links_presentation(tmp_path):
    ss = _load("summarize_systems")
    assert ss.presentation_link(tmp_path) == []
    (tmp_path / "presentation").mkdir()
    (tmp_path / "presentation" / "README.md").write_text("x")
    assert "presentation/README.md" in ss.presentation_link(tmp_path)[0]
