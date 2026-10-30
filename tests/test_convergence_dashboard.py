"""scripts/convergence_dashboard.py: statistics helpers, overview cells, dashboards render."""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cd():
    return _load("convergence_dashboard")


@pytest.fixture(scope="module")
def summ():
    return _load("summarize_systems")


# ---------------------------------------------------------------- synthetic inputs


def _manifest(root: Path, sid: str, **extra) -> None:
    parts = sid.split("_")
    m = {
        "id": sid,
        "polymer": parts[0],
        "resolution": parts[1],
        "n_chains": 40,
        "n_carbons": 240,
        "counts": {"total": {"atoms": 3200}},
        **extra,
    }
    (root / sid).mkdir(parents=True, exist_ok=True)
    (root / sid / "manifest.yaml").write_text(yaml.safe_dump(m))


def _hold(acf, ratio, plateau=9.1, drift=False):
    lag = np.linspace(0, 40, 50)
    return {
        "state": "done",
        "hold_ns": 80.0,
        "boundaries_ns": [20.0],
        "msid": {
            "plateau": plateau,
            "reference": [6.7, 6.7],
            "within_reference": False,
            "drift": drift,
            "delta": 0.3,
            "delta_sem": 0.2,
        },
        "ree_acf": {"acf_at_lag": acf, "lag_ns": 40.0, "t_1e_ns": 10.0},
        "com_msd": {"ratio": ratio, "rg2_A2": 900.0},
        "d47": {"acf": acf, "lag_ns": 40.0, "ratio": ratio, "passed": acf < 0.3679 and ratio >= 2},
        "curves": {
            "plateau_t_ns": list(np.linspace(0, 80, 40)),
            "plateau_t": list(plateau + 0.3 * np.sin(np.arange(40))),
            "acf_lag_ns": list(lag),
            "acf": list(np.exp(-lag / 15)),
            "msd_lag_ns": list(lag),
            "msd_A2": list(900 * ratio * lag / 40),
        },
    }


def _progress(root: Path, sid: str, stage: str, **report) -> Path:
    d = root / sid / stage
    d.mkdir(parents=True, exist_ok=True)
    base = {
        "system": sid,
        "stage": stage,
        "status": "finished",
        "percent": 100.0,
        "steps_done": 1000,
        "flags": [],
    }
    (d / "progress.json").write_text(json.dumps({**base, **report}))
    return d


SWEEP = [("hold", 25.0), ("step", 35.0), ("hold", 90.0)]


def _deck_and_log(d: Path, sid: str, segs, pore=False, trend=None, n=240, protocol="sweep"):
    """Deck with one run per segment and a matching log (stationary noise; ``trend``:
    {segment index: slope per row} for a drifting density/gamma)."""
    rng = np.random.default_rng(0)
    ens = "nvt temp {t} {t} 1000" if pore else "npt temp {t} {t} 1000 iso 1 1 10000"
    deck = [f"# system {sid} (cg), test", "timestep 10"]
    cols = "Step Time Temp Press PotEng Enthalpy Volume Density"
    if pore:
        cols += " Lz Pxx Pyy Pzz"
    log = []
    step = 0
    for k, (kind, tc) in enumerate(segs, start=1):
        tk = tc + 273.15
        deck += [
            f"# ---- Segment {k}: {kind} at {tc:g} C",
            "fix 1 all " + ens.format(t=tk),
            f"run {n * 100}",
            "unfix 1",
        ]
        log.append(cols)
        for i in range(n):
            slope = (trend or {}).get(k, 0.0)
            rho = 0.8 - 0.001 * tc + 1e-4 * rng.standard_normal() + slope * i
            if pore:
                rho = 0.5
            pzz = 20 * rng.standard_normal() + (slope * 1e5 * i if pore else 0)
            row = [
                step,
                step * 10.0,
                tk + rng.standard_normal(),
                1.0,
                -5000 + 10 * tc + rng.standard_normal(),
                -4000 + 10 * tc + rng.standard_normal() + (slope * 1e5 * i if not pore else 0),
                3e5 * (1 + 0.001 * tc),
                rho,
            ]
            if pore:
                row += [100.0, rng.standard_normal(), rng.standard_normal(), pzz]
            log.append(" ".join(f"{v:.8g}" for v in row))
            step += 100
        step -= 100
        log.append(f"Loop time of 1.0 on 1 procs for {n * 100} steps with 10 atoms")
    (d / f"in.{protocol}").write_text("\n".join(deck) + "\n")
    (d / "log.lammps").write_text("\n".join(log) + "\n")


@pytest.fixture
def tree(tmp_path):
    runs, systems, ana = tmp_path / "runs", tmp_path / "systems", tmp_path / "analysis"
    ana.mkdir()
    # bulk CG, passes D47, finished sweep with a drifting 90 C hold
    a = "pe_cg_amorph_n40_c240_s1"
    _manifest(systems, a)
    _progress(runs, a, "extend", hold=_hold(0.14, 2.56))
    d = _progress(runs, a, "sweep", hysteresis=[{"delta_pct": 0.8}, {"delta_pct": None}])
    _deck_and_log(d, a, SWEEP, trend={3: 2e-6})
    # sweep analysis: chain-scale ratios
    (ana / a / "sweep").mkdir(parents=True)
    holds = [
        {"t_c": t, "traj": {"com_msd": {"msd_at_max_A2": m}, "rg": {"rg2_A2": {"mean": 1000.0}}}}
        for t, m in ((25, 180.0), (90, 600.0))
    ]
    (ana / a / "sweep" / "results.json").write_text(json.dumps({"holds": holds}))
    # UA bulk failing D47, sweep never run, no hold curves
    b = "pe_ua_amorph_n40_c240_s1"
    _manifest(systems, b)
    h = _hold(0.47, 0.63)
    del h["curves"]
    _progress(runs, b, "prep", hold=h)
    # AA converted from UA (inherits), prep running
    c = "pe_aa_amorph_n40_c240_s1_from_ua"
    _manifest(systems, c, conversion={"method": "ua2aa"}, source={"id": b})
    _progress(runs, c, "prep", status="running", percent=12.0)
    # pore from the CG bulk
    p = "pe_cg_pore_w5nm_n40_c240_s1"
    _manifest(systems, p, pore={"kind": "narrow", "nominal_width_nm": 5}, source={"id": a})
    d = _progress(runs, p, "pore")
    _deck_and_log(d, p, SWEEP, pore=True, trend={1: 2e-6}, protocol="pore")
    return runs, ana, systems, tmp_path


# ---------------------------------------------------------------- statistics


def test_block_averages(cd):
    t = np.arange(100.0)
    x = np.r_[np.zeros(50), np.ones(50)] + 0.01 * np.random.default_rng(0).standard_normal(100)
    b = cd.block_averages(t, x, 5)
    assert len(b) == 5
    assert [round(v["mean"], 1) for v in b] == [0.0, 0.0, 0.5, 1.0, 1.0]
    assert b[0]["t"] == pytest.approx(9.5)
    assert all(v["sem"] > 0 for v in b)
    assert cd.block_averages(t[:8], x[:8], 5) == []  # blocks < 3 rows dropped


def test_sem_vs_block_white_noise(cd):
    x = np.random.default_rng(2).standard_normal(4096)
    ms = cd.mean_sem(x)
    curve = cd.sem_vs_block(x, 0.001, ms["sem"])
    assert [p["n_blocks"] for p in curve] == list(cd.SEM_BLOCKS)
    assert curve[0]["block_ns"] == pytest.approx(0.016)
    assert all(0.5 < p["ratio"] < 1.6 for p in curve)


def test_drift_trend_vs_stationary(cd):
    rng = np.random.default_rng(3)
    flat = rng.standard_normal(2000)
    trend = flat + np.linspace(0, 2, 2000)
    assert cd.halves_drift(flat)["drift"] is False
    assert cd.halves_drift(trend)["drift"] is True
    assert cd.halves_drift(np.ones(100)) is None  # constant (NVT density)
    rec = cd.quantity_record(np.arange(2000) * 0.001, trend, 0.1, 10, hold=True)
    assert rec["drift"] is True and len(rec["blocks"]) == 10
    assert rec["blocks"][0]["t"] > 0.2  # blocks over the window only (first 10% dropped)
    assert rec["sem_vs_block"]


# ---------------------------------------------------------------- overview


def test_overview_cells(cd, tree):
    runs, ana, systems, _ = tree
    ctx = cd.ss.build_context([runs], ana, systems)
    data = {s: cd.system_data(s, ctx, None) for s in ctx["meta"]}
    cells = {s: cd.overview_cells(s, ctx, data[s]) for s in ctx["meta"]}
    a = cells["pe_cg_amorph_n40_c240_s1"]
    assert a["acf"] == (cd.PASS, "0.14") and a["msd"] == (cd.PASS, "2.56")
    assert a["cn"][0] == cd.INFO and "9.10 vs 6.7" in a["cn"][1]
    assert a["sweep"] == (cd.PASS, "done") and a["prep"] == (cd.NA, "skipped")
    assert a["rho_drift"] == (cd.FLAG, "1/3") and a["h_drift"] == (cd.FLAG, "1/3")
    assert a["hyst"] == (cd.FLAG, "0.80%")
    assert a["prec"][0] == cd.PASS
    assert a["chain"] == (cd.FLAG, "0.18–0.60")
    assert a["gamma_drift"][0] == cd.NA and a["pore"][0] == cd.NA
    b = cells["pe_ua_amorph_n40_c240_s1"]
    assert b["acf"][0] == cd.FAIL and b["msd"][0] == cd.FAIL and "prep hold" in b["acf"][1]
    assert b["sweep"] == (cd.NOTRUN, "not started") and b["rho_drift"] == (cd.NOTRUN, "")
    assert b["chain"] == (cd.NOTRUN, "no analysis")
    c = cells["pe_aa_amorph_n40_c240_s1_from_ua"]
    assert c["acf"][0] == cd.FAIL and "inherited" in c["acf"][1]
    assert c["prep"] == (cd.RUN, "12%")
    p = cells["pe_cg_pore_w5nm_n40_c240_s1"]
    assert p["acf"] == (cd.PASS, "0.14\n(inherited)")
    assert p["gamma_drift"] == (cd.FLAG, "1/3")
    assert p["rho_drift"][0] == cd.NA and p["prec"][0] in (cd.PASS, cd.FLAG)
    assert p["pore"] == (cd.PASS, "done")


def test_build_writes_figures_and_summary_links(cd, summ, tree):
    runs, ana, systems, tmp = tree
    out = tmp / "out"
    res = cd.build([runs], ana, systems, out, cache_dir=tmp / "cache", log=lambda *_: None)
    assert (out / "convergence_overview.png").is_file()
    assert (out / "convergence_overview.svg").is_file()
    for sid in res["order"]:
        assert (out / "convergence" / f"{sid}.png").stat().st_size > 10_000
    assert list((tmp / "cache").glob("*.json"))
    res2 = cd.build([runs], ana, systems, out, cache_dir=tmp / "cache", log=lambda *_: None)
    assert res2["cells"] == res["cells"]  # from the cache
    # summary: links only to files that exist
    ctx = summ.build_context([runs], ana, systems)
    text = summ.render(ctx, base=out)
    assert "**Convergence figures:** [overview](convergence_overview.png)" in text
    assert "[`pe_cg_amorph_n40_c240_s1`](convergence/pe_cg_amorph_n40_c240_s1.png)" in text
    (out / "convergence" / "pe_cg_amorph_n40_c240_s1.png").unlink()
    text = summ.render(ctx, base=out)
    assert "convergence/pe_cg_amorph_n40_c240_s1.png" not in text
    assert "Convergence figures" not in summ.render(ctx, base=tmp / "empty")
    assert "Convergence figures" not in summ.render(ctx)


def test_pore_film_panels(cd, tree):
    """With a pore results.json 'convergence' list the film panels are mapped and drawn."""
    runs, ana, systems, tmp = tree
    p = "pe_cg_pore_w5nm_n40_c240_s1"
    t = list(np.linspace(0, 239, 50) * 1.0)  # ps, the first segment
    q = {
        "t_ps": t,
        "value": list(30 + np.zeros(50)),
        "blocks": [{"t": 100.0, "mean": 30, "sem": 1}],
        "drift": False,
    }
    conv = [
        {
            "name": "seg 01 hold 25 C",
            "t_start_ps": 0.0,
            "t_end_ps": 239.0,
            "window": [24, 239],
            "quantities": {"film_gibbs_A": q, "gap_gibbs_A": q, "plateau": q},
        }
    ]
    (ana / p / "pore").mkdir(parents=True)
    (ana / p / "pore" / "results.json").write_text(json.dumps({"convergence": conv}))
    ctx = cd.ss.build_context([runs], ana, systems)
    data = cd.system_data(p, ctx, None)
    film = cd.film_records(cd.analysis_for(p, ctx, "pore"), data["segments"])
    assert len(film) == 1 and set(film[0]["quantities"]) == set(cd.FILM_Q)
    assert film[0]["window"][0] == pytest.approx(0.024)
    out = tmp / "pore.png"
    cd.draw_dashboard(out, p, ctx, data)
    assert out.stat().st_size > 10_000


# ---------------------------------------------------------------- property convergence


def test_kappa_record_stationary_and_changing(cd):
    rng = np.random.default_rng(5)
    t = np.arange(4000) * 0.005
    v = 3e5 + 1000 * rng.standard_normal(4000)
    k = cd.kappa_record(t, v, 300.0)
    # kappa = var(V) / (kB T <V>): 1e6 A^6 / (4.14e-21 J * 3e5 A^3) = 0.805 / GPa
    assert k["kappa"] == pytest.approx(0.805, rel=0.08)
    assert k["drift"] is False and len(k["blocks"]) == cd.KAPPA_BLOCKS
    assert k["running"][-1][1] == pytest.approx(k["kappa"], rel=1e-6)
    v2 = 3e5 + np.r_[500 * rng.standard_normal(2000), 2000 * rng.standard_normal(2000)]
    assert cd.kappa_record(t, v2, 300.0)["drift"] is True
    assert cd.kappa_record(t, np.full(4000, 3e5), 300.0) is None  # NVT: constant volume
    assert cd.kappa_record(t[:20], v[:20], 300.0) is None  # too short


def test_log_slope_and_fit_residuals(cd):
    lag = np.logspace(-1, 4, 100)
    _x, s = cd.log_slope(lag, 3 * lag)
    assert np.allclose(s, 1.0)
    _x, s = cd.log_slope(lag, lag**0.5)
    assert np.allclose(s, 0.5)
    assert len(cd.log_slope(lag[:3], lag[:3])[0]) == 0
    res = {
        "segments": [
            {
                "done": True,
                "t_set_c": t,
                "stats": {"volume": {"mean": 2 * (t + 273.15) + 5 + d, "sem": 0.5}},
            }
            for t, d in ((25.0, 0.0), (90.0, 1.0), (160.0, -1.0))
        ],
        "fits": {"alpha_V": [{"window_c": [25.0, 160.0], "line": [2.0, 5.0], "chi2_red": 4.0}]},
    }
    r = cd.fit_residuals(res, "alpha_V")
    assert r[0]["t"] == [25.0, 90.0, 160.0]
    assert r[0]["resid"] == pytest.approx([0.0, 1.0, -1.0])
    assert cd.fit_residuals(None, "cp") == [] and cd.fit_residuals(res, "cp") == []


def _rich_sweep(ana, sid):
    lag = list(np.logspace(-1, 4, 60))
    holds = []
    for t, m, diff in ((25.0, 180.0, False), (90.0, 2400.0, True)):
        holds.append(
            {
                "t_c": t,
                "kappa": {"kappa_T_GPa": 1.0, "sem": 0.02},
                "traj": {
                    "com_msd": {
                        "msd_at_max_A2": m,
                        "diffusive": diff,
                        "slope_end": 0.9,
                        "D_cm2_s": 5e-7 if diff else None,
                    },
                    "rg": {"rg2_A2": {"mean": 1000.0}, "rg_A": {"mean": 31.0, "sem": 0.2}},
                    "ree": {"ree_A": {"mean": 77.0, "sem": 0.5}},
                    "c_n": {"plateau": {"mean": 10.0, "sem": 0.1}},
                    "p2": {"t_1e_ps": 120.0 if t > 50 else None},
                    "curves": {
                        "msd_lag_ps": lag,
                        "msd_A2": list(np.asarray(lag) ** 0.6),
                        "com_lag_ps": lag,
                        "com_A2": list(0.01 * np.asarray(lag)),
                        "p2_lag_ps": lag,
                        "p2": list(np.exp(-np.asarray(lag) / 100)),
                    },
                },
            }
        )
    res = {
        "holds": holds,
        "fits": {
            "alpha_V": [{"window_c": [25.0, 160.0], "line": [1.0, 0.0], "chi2_red": 49.7}],
            "cp": [{"window_c": [25.0, 160.0], "line": [1.0, 0.0], "chi2_red": 2.0}],
        },
        "segments": [],
    }
    (ana / sid / "sweep" / "results.json").write_text(json.dumps(res))


def test_new_overview_columns_and_extra_runs(cd, tree):
    runs, ana, systems, tmp = tree
    a = "pe_cg_amorph_n40_c240_s1"
    _rich_sweep(ana, a)
    hold = _hold(0.5, 0.3)
    hold.update(diffuse=True, t_c=160.0, d_com={"diffusive": False, "slope_max": 0.8})
    _progress(runs, a, "diffuse_160C", status="running", percent=40.0, hold=hold)
    _progress(runs, a, "tensile_25C_r1e9")
    (ana / a / "tensile_25C_r1e9").mkdir(parents=True)
    (ana / a / "tensile_25C_r1e9" / "results.json").write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "summary": {
                            "E_MPa": {"mean": 141.0, "sd": 133.0},
                            "nu_fit": {"mean": 0.46, "sd": 0.01},
                        }
                    }
                ]
            }
        )
    )
    ctx = cd.ss.build_context([runs], ana, systems)
    data = cd.system_data(a, ctx, None)
    c = cd.overview_cells(a, ctx, data)
    assert {k for k, _ in cd.COLUMNS} <= set(c)
    assert c["fit"] == (cd.INFO, "α 49.7 / Cp 2\ncurved in T")
    assert c["dyn"] == (cd.FLAG, "D_COM diffusive 1/2\nP2 1/e reached 1/2")
    assert c["diffuse"] == (cd.RUN, "160C 40%, not diff.")
    assert c["tensile"] == (cd.PASS, "25C_r1e9: E 141±133")
    assert c["hole"] == (cd.NA, "")
    assert c["kappa"][0] in (cd.PASS, cd.FLAG, cd.NOTRUN)
    p = cd.overview_cells(
        "pe_cg_pore_w5nm_n40_c240_s1", ctx, cd.system_data("pe_cg_pore_w5nm_n40_c240_s1", ctx, None)
    )
    assert p["kappa"] == (cd.NA, "") and p["fit"] == (cd.NA, "")
    assert p["dyn"] == (cd.NOTRUN, "no analysis")
    out = tmp / "dash.png"
    cd.draw_dashboard(out, a, ctx, data)  # with the extra row and all property panels
    assert out.stat().st_size > 10_000


def test_validity_overview_written(cd, tree):
    runs, ana, systems, tmp = tree
    out = tmp / "out2"
    res = cd.build([runs], ana, systems, out, cache_dir=None, log=lambda *_: None)
    assert (out / "validity_overview.png").stat().st_size > 10_000
    assert set(res["validity"]) == set(res["order"])
    v = res["validity"]["pe_cg_amorph_n40_c240_s1"]
    assert v["cp"]["verdict"] == "not meaningful"
    assert v["chainT"]["verdict"] == "trend"  # hold ratios 0.18 / 0.60 < 1
    assert res["validity"]["pe_cg_pore_w5nm_n40_c240_s1"]["rho"]["verdict"] == "n/a"
