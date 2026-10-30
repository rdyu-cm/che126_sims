"""scripts/summarize_systems.py: overview rows, D47 pass/fail rendering, missing data."""

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "summarize_systems.py"


@pytest.fixture(scope="module")
def summ():
    spec = importlib.util.spec_from_file_location("summarize_systems", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _manifest(root: Path, sid: str, **extra) -> None:
    parts = sid.split("_")
    m = {
        "id": sid,
        "polymer": parts[0],
        "resolution": parts[1],
        "n_chains": 40,
        "n_carbons": 240,
        "counts": {"total": {"atoms": 1234}},
        "density_g_cm3": 0.3,
        **extra,
    }
    (root / sid).mkdir(parents=True, exist_ok=True)
    (root / sid / "manifest.yaml").write_text(yaml.safe_dump(m))


def _progress(root: Path, sid: str, stage: str, **report) -> None:
    d = root / sid / stage
    d.mkdir(parents=True, exist_ok=True)
    base = {"system": sid, "stage": stage, "status": "finished", "percent": 100.0, "flags": []}
    (d / "progress.json").write_text(json.dumps({**base, **report}))


def _hold(acf, ratio, drift=False, plateau=8.2, within=False, d47=True, hold_ns=98.2):
    h = {
        "state": "done",
        "hold_ns": hold_ns,
        "msid": {
            "plateau": plateau,
            "reference": [6.7, 6.7],
            "within_reference": within,
            "drift": drift,
            "delta": 0.5,
            "delta_sem": 0.4,
        },
        "ree_acf": {"acf_at_lag": acf, "lag_ns": hold_ns / 2, "t_1e_ns": None},
        "com_msd": {"ratio": ratio},
    }
    if d47:
        h["d47"] = {
            "acf": acf,
            "lag_ns": hold_ns / 2,
            "ratio": ratio,
            "passed": acf < 0.3679 and ratio >= 2.0,
        }
    return h


def _sweep_results(root: Path, sid: str) -> None:
    d = root / sid / "sweep"
    d.mkdir(parents=True)
    res = {
        "generated": "2026-10-28T00:00:00+00:00",
        "run_status": "finished",
        "segments": [
            {"index": 1, "kind": "hold", "stats": {"density": {"mean": 0.8345, "sem": 3e-5}}}
        ],
        "holds": [
            {
                "index": 1,
                "t_c": 25.0,
                "kappa": {"kappa_T_GPa": 1.0, "sem": 0.015},
                "traj": {
                    "available": True,
                    "rg": {"rg_A": {"mean": 31.24, "sem": 0.12}},
                    "c_n": {"plateau": {"mean": 10.27, "sem": 0.08}},
                    "p2": {"t_1e_ps": 122.9},
                    "com_msd": {"diffusive": True, "D_cm2_s": 5.1e-7, "D_err_cm2_s": 2e-10},
                },
            },
            {"index": 2, "t_c": 90.0, "traj": {}},  # missing keys -> dashes
        ],
        "fits": {
            "alpha_V": [{"window_c": [25.0, 160.0], "alpha_V_per_K": 6.9e-4, "err": 3.4e-6}],
            "cp": [{"window_c": [25.0, 160.0], "cp_J_gK": 0.828, "err": 0.0025}],
        },
        "caveats": ["Cp is the classical dH/dT and is not comparable to experiment"],
    }
    (d / "results.json").write_text(json.dumps(res))


@pytest.fixture
def tree(tmp_path):
    systems, runs, ana = tmp_path / "systems", tmp_path / "runs", tmp_path / "analysis"
    # PE UA: prep + extend (D47 PASS, no drift) + sweep running; sweep analysis present
    _manifest(systems, "pe_ua_amorph_n40_c240_s1", growth={"params": {}}, seed=1)
    _progress(runs, "pe_ua_amorph_n40_c240_s1", "prep", hold=_hold(0.47, 0.63, d47=False))
    _progress(runs, "pe_ua_amorph_n40_c240_s1", "extend", hold=_hold(0.16, 2.28))
    _progress(
        runs,
        "pe_ua_amorph_n40_c240_s1",
        "sweep",
        status="running",
        percent=40.0,
        eta="2026-11-03T00:09:33+00:00",
    )
    _progress(runs, "pe_ua_amorph_n40_c240_s1", "sweep_old_unrelaxed_cancelled", status="x")
    _progress(runs, "pe_ua_amorph_n40_c240_s1", "bench_r1t1")
    _sweep_results(ana, "pe_ua_amorph_n40_c240_s1")
    # iPP UA: extend fails D47
    _manifest(systems, "ipp_ua_amorph_n40_c240_s1", growth={"params": {}})
    _progress(runs, "ipp_ua_amorph_n40_c240_s1", "extend", hold=_hold(0.45, 1.05))
    # CG C240: D47 PASS but C_n drift -> not accepted
    _manifest(systems, "pe_cg_amorph_n40_c240_s1", growth={"params": {}})
    _progress(runs, "pe_cg_amorph_n40_c240_s1", "extend", hold=_hold(0.1, 2.6, drift=True))
    # pore from the PE UA box: inherits; no runs at all
    _manifest(
        systems,
        "pe_ua_pore_w5nm_n40_c240_s1",
        pore={"kind": "narrow", "nominal_width_nm": 5.0},
        source={
            "id": "pe_ua_amorph_n40_c240_s1",
            "data_file": "x/pe_ua_amorph_n40_c240_s1/extend/hold_ext_70ns.data",
        },
    )
    # AA from UA with no manifest keys beyond the basics and no runs
    _manifest(systems, "pe_aa_amorph_n40_c240_s1", growth={"params": {}})
    _manifest(
        systems,
        "pe_aa_amorph_n40_c240_s1_from_ua",
        conversion={"method": "ua2aa"},
        source={"id": "pe_ua_amorph_n40_c240_s1", "data_file": "hold_ext_70ns.data"},
    )
    return {"systems": systems, "runs": runs, "analysis": ana, "tmp": tmp_path}


def _render(summ, tree):
    ctx = summ.build_context([tree["runs"]], tree["analysis"], tree["systems"])
    return ctx, summ.render(ctx)


def _overview_rows(text: str) -> list[list[str]]:
    sec = text.split("## Overview", 1)[1].split("## Pending", 1)[0]
    rows = [ln for ln in sec.splitlines() if ln.startswith("| ")][1:]
    rows = [[c.strip() for c in ln.strip("|").split(" | ")] for ln in rows]
    for r in rows:
        r[0] = r[0].strip("`")
    return rows


def test_overview_rows_and_order(summ, tree):
    _, text = _render(summ, tree)
    rows = _overview_rows(text)
    ids = [r[0] for r in rows]
    # PE before iPP; CG, UA, AA; bulk before pores; the superseded grown AA box is left out
    assert ids == [
        "pe_cg_amorph_n40_c240_s1",
        "pe_ua_amorph_n40_c240_s1",
        "pe_ua_pore_w5nm_n40_c240_s1",
        "pe_aa_amorph_n40_c240_s1_from_ua",
        "ipp_ua_amorph_n40_c240_s1",
    ]
    ua = rows[1]
    assert ua[1:6] == ["UA", "PE", "bulk", "40 × C240", "1,234"]
    assert ua[6] == "sweep"
    assert ua[7].startswith("running, 40.0%") and ua[7].endswith("ETA 2026-11-03 00:09 UTC")
    assert ua[10] == "sweep"
    assert rows[0][10] == "no"
    sup = text.split("## Superseded", 1)[1].split("##", 1)[0]
    assert "System `pe_aa_amorph_n40_c240_s1`: superseded by" in sup
    assert "Runs of `pe_ua_amorph_n40_c240_s1`: sweep_old_unrelaxed_cancelled (x)" in sup


def test_pass_fail_rendering(summ, tree):
    ctx, text = _render(summ, tree)
    rows = {r[0]: r for r in _overview_rows(text)}
    ua = rows["pe_ua_amorph_n40_c240_s1"][8]
    assert ua.startswith("D47 PASS") and "ACF 0.16" in ua and "MSD/⟨Rg²⟩ 2.28" in ua
    assert "98.2 ns at 500 K" in ua and ua.endswith("accepted")
    # C_n outside the band is information only, the drift is the check
    cn = rows["pe_ua_amorph_n40_c240_s1"][9]
    assert "8.20 vs 6.7 (outside band, info)" in cn and "no drift" in cn
    assert ctx["eq"]["pe_ua_amorph_n40_c240_s1"]["accepted"] is True
    ipp = rows["ipp_ua_amorph_n40_c240_s1"][8]
    assert ipp.startswith("D47 FAIL") and "not accepted" in ipp
    assert ctx["eq"]["ipp_ua_amorph_n40_c240_s1"]["accepted"] is False
    cg = rows["pe_cg_amorph_n40_c240_s1"]
    assert cg[8].startswith("D47 PASS") and "accepted (C_n drift" in cg[8]
    assert ctx["eq"]["pe_cg_amorph_n40_c240_s1"]["accepted"] is True
    assert "; drift" in cg[9]
    # pore and ua2aa inherit the source's verdict
    assert rows["pe_ua_pore_w5nm_n40_c240_s1"][8].startswith(
        "from pe_ua_amorph_n40_c240_s1: D47 PASS"
    )
    assert rows["pe_aa_amorph_n40_c240_s1_from_ua"][8].startswith("from pe_ua_amorph")


def test_prep_only_and_long_cg(summ, tree):
    _manifest(tree["systems"], "pe_cg_amorph_n40_c1500_s1", n_carbons=1500)
    m = yaml.safe_load(
        (tree["systems"] / "pe_cg_amorph_n40_c1500_s1" / "manifest.yaml").read_text()
    )
    m["n_carbons"] = 1500
    (tree["systems"] / "pe_cg_amorph_n40_c1500_s1" / "manifest.yaml").write_text(yaml.safe_dump(m))
    _progress(tree["runs"], "pe_cg_amorph_n40_c1500_s1", "extend", hold=_hold(0.68, 0.12))
    _manifest(tree["systems"], "pe_ua_amorph_n40_c120_s1")
    _progress(tree["runs"], "pe_ua_amorph_n40_c120_s1", "prep", hold=_hold(0.3, 2.5, d47=False))
    ctx, _ = _render(summ, tree)
    long = ctx["eq"]["pe_cg_amorph_n40_c1500_s1"]
    assert long["accepted"] is True and long["text"].startswith("D47 n/a")
    prep = ctx["eq"]["pe_ua_amorph_n40_c120_s1"]
    assert prep["basis"] == "prep only" and "prep hold only" in prep["text"]


def test_missing_data_and_pending(summ, tree):
    _, text = _render(summ, tree)
    rows = {r[0]: r for r in _overview_rows(text)}
    pore = rows["pe_ua_pore_w5nm_n40_c240_s1"]
    assert pore[6] == "pore" and pore[7] == "not started"
    # analysis table: the hold without data renders dashes, not an error
    sec = text.split("### `pe_ua_amorph_n40_c240_s1` sweep", 1)[1].split("###", 1)[0]
    assert "| 90 | — | — | — | — | — | — | — | — | — |" in sec
    assert "| 25 | 0.83450 ± 0.00003 | 1.000 ± 0.015 | 31.24 ± 0.12 |" in sec
    assert "| 25–160 | 6.900 ± 0.034 |" in sec
    assert "Note: Cp is the classical" in sec
    assert "bench_r1t1" not in text
    pend = text.split("## Pending and known items", 1)[1].split("##", 1)[0]
    assert "`pe_ua_pore_w5nm_n40_c240_s1`: pore not started" in pend
    assert "`pe_aa_amorph_n40_c240_s1_from_ua`: prep not started; sweep not started" in pend
    assert "`pe_ua_amorph_n40_c240_s1`: sweep: running" in pend
    assert "`ipp_ua_amorph_n40_c240_s1`: cool not started; sweep not started" in pend
    assert "pe_aa_amorph_n40_c240_s1:" not in pend  # superseded: not pending


def test_empty_and_broken_inputs(summ, tmp_path):
    (tmp_path / "runs" / "x_ua_y" / "prep").mkdir(parents=True)
    (tmp_path / "runs" / "x_ua_y" / "prep" / "progress.json").write_text("{not json")
    ctx = summ.build_context([tmp_path / "runs"], tmp_path / "none", tmp_path / "none")
    text = summ.render(ctx)
    assert "## Overview" in text and "- Nothing pending." in text
    assert "x_ua_y" not in text  # unreadable report and no manifest: nothing to show


def test_pore_results_generic(summ, tree):
    d = tree["analysis"] / "pe_ua_pore_w5nm_n40_c240_s1" / "pore"
    d.mkdir(parents=True)
    res = {
        "generated": "2026-10-30T00:00:00+00:00",
        "gap_width_nm": 4.8,
        "curves": {"z": [1, 2, 3]},
        "holds": [
            {"t_c": 25.0, "gamma_mN_m": {"mean": 34.4, "sem": 0.4}, "label": "x"},
            {"t_c": 90.0},
        ],
    }
    (d / "results.json").write_text(json.dumps(res))
    _, text = _render(summ, tree)
    sec = text.split("### `pe_ua_pore_w5nm_n40_c240_s1` pore", 1)[1].split("###", 1)[0]
    assert "gap_width_nm: 4.8" in sec
    assert "| t_c | gamma_mN_m |" in sec
    assert "| 25 | 34.4 ± 0.4 |" in sec and "| 90 | — |" in sec


def test_multiple_roots_and_cli(summ, tree, tmp_path):
    other = tmp_path / "rog"
    _progress(other, "ipp_ua_amorph_n40_c240_s1", "extend", steps_done=10, hold=_hold(0.1, 2.5))
    out = tmp_path / "out" / "summary.md"
    rc = summ.main(
        [
            "--runs", str(tree["runs"]),
            "--runs", str(other),
            "--analysis", str(tree["analysis"]),
            "--systems", str(tree["systems"]),
            "--out", str(out),
        ]
    )  # fmt: skip
    assert rc == 0
    text = out.read_text()
    assert "## Property guide" not in text  # no guide in the tmp project: skipped
    row = next(r for r in _overview_rows(text) if r[0] == "ipp_ua_amorph_n40_c240_s1")
    assert row[8].startswith("D47 PASS")  # the report with more steps done wins


def test_classify_stage(summ):
    assert summ.classify_stage("pore_relax") == ("pore_relax", False)
    assert summ.classify_stage("pore_relax_old_20ns_box") == ("pore_relax", True)
    assert summ.classify_stage("pore_old_20ns_box_cancelled") == ("pore", True)
    assert summ.classify_stage("sweep_d47") == ("sweep", False)
    assert summ.classify_stage("prep_timeout12h") == ("prep", True)
    assert summ.classify_stage("bench_r1t1") == (None, False)
    assert summ.classify_stage("smoke_gpu") == (None, False)


def test_guide_appended_and_d47_stop(summ, tree, tmp_path):
    # an extension cancelled after its D47 pass counts as done (not pending)
    _progress(
        tree["runs"],
        "ipp_ua_amorph_n40_c240_s1",
        "extend",
        status="cancelled/killed?",
        percent=50.0,
        hold=_hold(0.19, 2.06),
    )
    guide = tmp_path / "guide.md"
    guide.write_text("## Property guide: test\n\n1. **Density.**\n")
    out = tmp_path / "s.md"
    summ.main(
        [
            "--runs", str(tree["runs"]),
            "--analysis", str(tree["analysis"]),
            "--systems", str(tree["systems"]),
            "--guide", str(guide),
            "--out", str(out),
        ]
    )  # fmt: skip
    text = out.read_text()
    assert text.rstrip().endswith("1. **Density.**")
    row = next(r for r in _overview_rows(text) if r[0] == "ipp_ua_amorph_n40_c240_s1")
    assert row[6] == "cool" and row[7] == "not started (extend done)"
    pend = text.split("## Pending and known items", 1)[1].split("##", 1)[0]
    assert "extend:" not in pend


def test_eta_converted_to_utc(summ):
    assert summ.utc("2026-11-02T16:09:33-08:00") == "2026-11-03 00:09 UTC"
    assert summ.utc(None) == "—"
