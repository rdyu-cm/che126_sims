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
