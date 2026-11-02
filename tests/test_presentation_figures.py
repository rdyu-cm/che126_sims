"""scripts/presentation_figures.py: series lookup by id, empty inputs, a real-data smoke run."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"


def _load(name):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pf():
    return _load("presentation_figures")


def test_series_by_id(pf):
    s = pf.series_info("ipp_ua_amorph_n40_c240_s1")
    assert (s["polymer"], s["res"], s["kind"], s["primary"]) == ("ipp", "ua", "bulk", True)
    assert s["label"] == "UA iPP" and s["marker"] == "s" and s["color"] == pf.RES_COLOR["ua"]
    aa = pf.series_info("pe_aa_amorph_n40_c240_s1_from_ua")
    assert aa["res"] == "aa" and aa["primary"]
    assert pf.superseded("pe_aa_amorph_n40_c240_s1", {"pe_aa_amorph_n40_c240_s1_from_ua"})
    long = pf.series_info("pe_cg_amorph_n40_c1500_s1")
    assert not long["primary"] and long["label"] == "CG PE C1500" and long["mfc"] == "white"
    pore = pf.series_info("pe_cg_pore_w5nm_n320_c240_s1_rep222")
    assert pore["kind"] == "pore" and pore["width_nm"] == 5.0 and not pore["primary"]
    assert pf.series_info("pe_cg_pore500k_w10nm_n40_c240_s1")["kind"] == "wide_pore"
    assert pf.series_info("pe_cg_hole_r3nm_160C_n320_c240_s1_rep222")["kind"] == "hole"
    assert pf.series_info("not_an_id") is None


def test_empty_inputs_write_placeholders(pf, tmp_path):
    data = pf.load_data(tmp_path / "a", tmp_path / "s", [tmp_path / "r"])
    out = pf.build(data, tmp_path / "out", log=lambda *_: None)
    names = {p.name for p in out["written"]}
    for fig in ("fig1_convergence", "fig2_properties_vs_T", "fig3_structures", "fig4_mechanics"):
        assert {f"{fig}.png", f"{fig}.pdf", f"{fig}.svg"} <= names
    text = out["readme"].read_text()
    assert "## fig4_mechanics" in text and "Hole runs" not in text  # caption, not panel text
    assert out["infos"]["fig3_structures"]["d"]["pending"]


def test_hole_panel_uses_results(pf, tmp_path):
    d = tmp_path / "a" / "pe_cg_hole_r3nm_160C_n320_c240_s1_rep222" / "hole_free"
    d.mkdir(parents=True)
    frames = [{"t_ns": t, "phase": "production", "r_eff": 30.0 - 2 * t} for t in range(10)]
    res = {"radius_nominal_nm": 3.0, "t_c": 160.0, "variant": "free", "frames": frames}
    (d / "results.json").write_text(json.dumps(res))
    data = pf.load_data(tmp_path / "a", tmp_path / "s", [])
    out = pf.build(data, tmp_path / "out", only=["fig3"], log=lambda *_: None)
    info = out["infos"]["fig3_structures"]["d"]
    assert not info["pending"] and len(info["runs"]) == 1


@pytest.mark.skipif(
    not (REPO / "results/analysis/pe_cg_amorph_n40_c240_s1/sweep/results.json").is_file(),
    reason="committed CG analysis not present",
)
def test_real_data_smoke(pf, tmp_path):
    data = pf.load_data(REPO / "results/analysis", REPO / "systems", [])
    out = pf.build(data, tmp_path, only=["fig2", "fig4"], log=lambda *_: None)
    assert (tmp_path / "fig2_properties_vs_T.png").stat().st_size > 10_000
    info = out["infos"]["fig2_properties_vs_T"]
    assert "CG PE" in info["a"]["series"]
    rates = out["infos"]["fig4_mechanics"]["rates"]
    assert rates == [1e8, 1e9]


def test_summary_links_presentation(tmp_path):
    ss = _load("summarize_systems")
    assert ss.presentation_link(tmp_path) == []
    (tmp_path / "presentation").mkdir()
    (tmp_path / "presentation" / "README.md").write_text("x")
    assert "presentation/README.md" in ss.presentation_link(tmp_path)[0]
