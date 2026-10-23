"""Tests for `sepsim progress` (D45): deck/log parsing, stats, comparisons, reports, plots."""

import json
import os
from pathlib import Path

import numpy as np
import pytest

from sepsim import progress as pg
from sepsim import progress_plots as pp
from sepsim.analysis.lammps_log import read_log
from sepsim.cli import main
from sepsim.lammps.render import render_deck

REPO = Path(__file__).resolve().parents[1]
SYSTEMS = REPO / "systems"
UA = SYSTEMS / "pe_ua_amorph_n40_c240_s1"
CG = SYSTEMS / "pe_cg_amorph_n40_c240_s1"


def _deck(tmp_path, protocol, system=UA, **kw):
    run = tmp_path / system.name / protocol
    run.mkdir(parents=True)
    deck = run / f"in.{protocol}"
    deck.write_text(render_deck(protocol, system, deck_dir=run, require_data=False, **kw))
    return run, deck


def test_parse_prep_deck(tmp_path):
    _, deck = _deck(tmp_path, "prep")
    segs = pg.parse_deck(deck)
    assert [s.command for s in segs[:2]] == ["run", "minimize"]
    assert segs[0].name == "Stage 1: soft-core push-off" and segs[0].dt_fs == 1.0
    assert segs[0].ensemble == "langevin" and segs[1].steps == 0
    names = [s.name for s in segs]
    assert any(n.endswith("(run 1/2)") for n in names) and any(
        n.endswith("(run 2/2)") for n in names
    )
    hold = [s for s in segs if "hold.dcd" in s.dcd]
    assert len(hold) == 1 and hold[0].ensemble == "npt" and hold[0].t_target_k == 500.0
    assert hold[0].dump_every[0] * hold[0].dt_fs / 1000 == 10.0  # 10 ps frames (D28)
    cool = [s for s in segs if s.cool_step]
    assert [s.cool_step for s in cool] == list(range(1, 9))
    assert cool[-1].t_target_k == pytest.approx(298.15) and "cool.dcd" in cool[0].dcd
    assert sum(s.steps for s in segs) == 18_570_000  # UA: 20 ps at 1 fs + 37 ns at 2 fs
    assert pg.deck_system(deck) == ("pe_ua_amorph_n40_c240_s1", "ua")


def test_parse_sweep_deck_with_vdos(tmp_path):
    _, deck = _deck(tmp_path, "sweep", overrides={"vdos": True})
    segs = pg.parse_deck(deck)
    md = [s for s in segs if not s.vdos]
    assert len(md) == 18 and [s.sweep_index for s in md] == list(range(1, 19))
    assert md[0].sweep_kind == "hold" and md[0].t_c == 25.0 and md[0].name == "seg 01 hold 25 C"
    assert md[8].sweep_kind == "hold" and md[8].ensemble == "npt"  # fix md continues
    vdos = [s for s in segs if s.vdos]
    assert len(vdos) == 4 and all(s.ensemble == "nve" and s.dt_fs == 1.0 for s in vdos)
    assert vdos[0].t_target_k is None and vdos[0].name.endswith("VDOS NVE")


LOG = """LAMMPS (22 Jul 2025)
   Step          Time           Temp          Density        Enthalpy        PotEng          CPU
         0   0              300            0.8            -10             5              0
        10   20             301            0.8            -11             6              1
        20   40             299            0.8            -12             7              2
Loop time of 2.5 on 4 procs for 20 steps with 100 atoms

Performance: 1.5 ns/day, 16 hours/ns, 8.0 timesteps/s, 1 katom-step/s
   Step          Time           Temp          Density        Enthalpy        PotEng          CPU
        20   40             299            0.8            -12             7              0
        30   60             300            0.81           -13             8              5
ERROR: something (src/x.cpp:1)
"""


def test_read_log_runs_performance_and_errors(tmp_path):
    p = tmp_path / "log.lammps"
    p.write_text(LOG)
    log = read_log(p)
    assert [r.complete for r in log.runs] == [True, False]
    first = log.runs[0]
    assert first.n_steps == 20 and first.loop_time_s == 2.5
    assert first.ns_per_day == 1.5 and first.steps_per_s == 8.0
    np.testing.assert_array_equal(log.runs[1].thermo["Step"], [20, 30])
    assert log.errors == ["ERROR: something (src/x.cpp:1)"]


def test_segment_stats_guards_constant_density():
    n = 200
    rng = np.random.default_rng(0)
    th = {
        "Step": np.arange(n, dtype=float),
        "Temp": 500 + rng.normal(size=n),
        "Density": np.full(n, 0.3),
        "Enthalpy": rng.normal(size=n),
    }
    st = pg.segment_stats(th)
    assert st["density"] == {"mean": 0.3, "sem": 0.0} and "drift" not in st
    assert st["t_c"]["mean"] == pytest.approx(500 - 273.15, abs=0.5)
    th["Density"] = 0.8 + 0.001 * rng.normal(size=n)
    assert pg.segment_stats(th)["drift"]["drift"] is False
    th["Density"] = th["Density"] + np.linspace(0, 0.05, n)
    assert pg.segment_stats(th)["drift"]["drift"] is True
    assert pg.segment_stats({"Step": np.arange(3.0)}) == {"rows": 3}


def _seg(index, t_k, rho, h=0.0, sem=1e-4, **kw):
    d = {"index": index, "state": "done", "ensemble": "npt", "t_target_k": t_k, "vdos": False}
    d["stats"] = {"density": {"mean": rho, "sem": sem}, "enthalpy": {"mean": h, "sem": 1.0}}
    return {**d, **kw}


def test_hysteresis_interpolates_sweep_and_skips_out_of_range():
    prep = [_seg(1, 474.0, 0.70, cool_step=1), _seg(2, 330.0, 0.801, cool_step=2)]
    sweep = [
        _seg(1, 300.0, 0.83, sweep_kind="hold", t_c=26.85),
        _seg(2, 360.0, 0.77, sweep_kind="step", t_c=86.85),
        _seg(3, 360.0, 0.79, sweep_kind="hold", t_c=86.85),  # the hold wins at 360 K
    ]
    rows = pg.hysteresis(prep, sweep)
    assert rows[0]["rho_sweep"] is None and rows[0]["delta_pct"] is None
    assert rows[1]["rho_sweep"] == pytest.approx(0.81)
    assert rows[1]["delta_pct"] == pytest.approx((0.801 - 0.81) / 0.81 * 100)


def test_step_vs_hold_flags_beyond_sems():
    segs = [
        _seg(8, 363.15, 0.800, sweep_kind="step", t_c=90.0),
        _seg(9, 363.15, 0.8001, sweep_kind="hold", t_c=90.0),
        _seg(10, 373.15, 0.79, sweep_kind="step", t_c=100.0),
        _seg(13, 403.15, 0.770, sweep_kind="step", t_c=130.0),
        _seg(14, 403.15, 0.775, sweep_kind="hold", t_c=130.0),
    ]
    rows = pg.step_vs_hold(segs)
    assert [(r["t_c"], r["flag"]) for r in rows] == [(90.0, False), (130.0, True)]


DECK = """# sepsim 0.1.0 deck: prep
# system demo_sys (ua), seed 1
timestep 2
thermo_style custom step time temp density enthalpy pe cpu

# ---- Stage 4: NVT 1 ps at 500 K
fix md all nvt temp 500 500 200
run 30
unfix md

# ---- Stage 7: step-cool 500 -> 300 K in 2 steps
# cool step 1/2: 400 K
fix md all npt temp 400 400 200 iso 1 1 2000
run 30
unfix md
# cool step 2/2: 300 K
fix md all npt temp 300 300 200 iso 1 1 2000
run 40
unfix md
"""


def _rows(step0, n, stride=10):
    return "".join(
        f"  {step0 + stride * k}  {2.0 * (step0 + stride * k)}  300  0.8  -10  5  {float(k)}\n"
        for k in range(n)
    )


HEAD = "   Step   Time   Temp   Density   Enthalpy   PotEng   CPU\n"


def _run_dir(tmp_path, status="started", finish=False):
    run = tmp_path / "runs" / "demo_sys" / "prep"
    run.mkdir(parents=True)
    (run / "in.prep").write_text(DECK)
    log = HEAD + _rows(0, 4) + "Loop time of 3 on 1 procs for 30 steps with 10 atoms\n"
    log += "Performance: 1.0 ns/day, 24 hours/ns, 10.0 timesteps/s\n"
    log += HEAD + (_rows(30, 11, stride=3) if finish else _rows(30, 2))
    if finish:
        log += "Loop time of 1 on 1 procs for 30 steps with 10 atoms\n" + HEAD + _rows(60, 11, 4)
        log += "Loop time of 4 on 1 procs for 40 steps with 10 atoms\n"
    (run / "log.lammps").write_text(log)
    man = {"status": status, "hostname": "nodeA", "start_time": "2026-10-20T00:00:00+00:00"}
    (run / "run_manifest.json").write_text(json.dumps(man))
    return run


def test_report_running_eta_and_stalled(tmp_path):
    run = _run_dir(tmp_path)
    mtime = (run / "log.lammps").stat().st_mtime
    r = pg.progress_report(run, now=mtime + 60, plots=False)
    assert r["status"] == "running" and r["node"] == "nodeA" and r["system"] == "demo_sys"
    assert r["steps_total"] == 100 and r["steps_done"] == 40 and r["percent"] == 40.0
    assert r["current"] == {"index": 2, "name": "Stage 7 cool 1/2 (400.0 K)"}
    assert r["steps_per_s"] == pytest.approx(10.0)  # 10 steps per CPU second
    assert r["remaining_h"] == pytest.approx(60 / 10 / 3600)
    assert r["segments"][0]["state"] == "done" and r["segments"][2]["state"] == "pending"
    assert pg.progress_report(run, now=mtime + 3600, plots=False)["status"] == "stalled?"
    gone = pg.progress_report(run, now=mtime + 2 * 86400, plots=False)
    assert gone["status"] == "cancelled/killed?" and "eta" not in gone


def test_report_finished_writes_files_plots_and_reuses(tmp_path):
    run = _run_dir(tmp_path, status="finished", finish=True)
    out = tmp_path / "out"
    r = pg.progress_report(run, out=out)
    assert r["status"] == "finished" and r["percent"] == 100.0 and r["n_done"] == 3
    od = pg.out_dir_for(run, out)
    assert od == out / "demo_sys" / "prep"
    pg.write_report(r, od)
    assert set(r["plots"]) == {"timeline", "cool_vs_sweep"}
    for p in r["plots"].values():
        assert (od / p["file"]).stat().st_size > 1000
    md = (od / "progress.md").read_text()
    assert "**finished**" in md and "progress_timeline.png" in md
    assert not (run / "progress.md").exists()  # --out keeps the run directory clean
    stamp = (od / "progress_timeline.png").stat().st_mtime_ns
    again = pg.progress_report(run, out=out)
    assert again["signature"] == r["signature"]
    assert (od / "progress_timeline.png").stat().st_mtime_ns == stamp  # not redrawn
    summary = pg.summary_markdown(pg.collect_reports([out]), base=out)
    assert "| demo_sys | [prep](demo_sys/prep/progress.md) | nodeA | finished | 100.0 |" in summary


def test_report_without_log_or_deck(tmp_path):
    run = tmp_path / "x" / "prep"
    run.mkdir(parents=True)
    assert pg.progress_report(run, plots=False)["notes"] == ["no deck (in.*) found"]
    (run / "in.prep").write_text(DECK)
    assert pg.progress_report(run, plots=False)["status"] == "not started"


def _write_dcd(path, frames):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(frames.shape[1], trajectory=True)
    with DCDWriter(str(path), frames.shape[1]) as w:
        for x in frames:
            u.atoms.positions = x
            u.dimensions = [100.0, 100.0, 100.0, 90.0, 90.0, 90.0]
            w.write(u.atoms)


def test_hold_chain_checks_on_cg_system(tmp_path):
    from sepsim.analysis.chain import backbone_chains, characteristic_ratio
    from sepsim.build.datafile import read_data_file

    x0 = read_data_file(CG / "data.lmp").unwrapped()
    rng = np.random.default_rng(0)
    frames = np.stack([x0 + 0.05 * rng.normal(size=x0.shape) for _ in range(12)])
    _write_dcd(tmp_path / "hold.dcd", frames.astype(np.float32))
    res = pg.hold_chain_checks(tmp_path / "hold.dcd", CG, frame_ps=10.0)
    assert res["frames"] == 12 and res["hold_ns"] == pytest.approx(0.11)
    chains = backbone_chains(CG / "data.lmp", CG / "manifest.yaml")
    nc, c_n = characteristic_ratio(x0, chains, carbons_per_site=3, bond_length=1.54)
    assert res["msid"]["plateau"] == pytest.approx(c_n[nc >= 100].mean(), rel=0.01)
    assert res["ree_acf"]["acf_at_lag"] > 0.99  # frozen chains stay correlated
    assert res["ree_acf"]["t_1e_ns"] is None
    assert res["com_msd"]["ratio"] < 0.01
    assert len(res["curves"]["plateau_t"]) == 12


def test_plots_from_synthetic_inputs(tmp_path):
    t = np.linspace(0, 1, 50)
    files = [
        pp.timeline(tmp_path / "a.png", t, 0.8 + 0 * t, -t, [(0.0, "1"), (0.5, "2")]),
        pp.cn_curve(tmp_path / "b.png", np.arange(1, 80), np.full(79, 6.5), (6.7, 6.7)),
        pp.cn_plateau_time(tmp_path / "c.png", t, 6.5 + 0 * t, (6.7, 6.7)),
        pp.ree_acf(tmp_path / "d.png", t, np.exp(-t / 0.3)),
        pp.com_msd(tmp_path / "e.png", t, 100 * t, 50.0),
        pp.vs_temperature(
            tmp_path / "f.png",
            [{"t_c": 25.0, "kind": "hold", "density": {"mean": 0.85, "sem": 0.001}}],
            [{"t_c": 50.0, "kind": "cool", "density": {"mean": 0.84, "sem": 0.001}}],
        ),
    ]
    assert all(f.stat().st_size > 1000 for f in files)
    assert not list(tmp_path.glob("*.tmp.png"))


def test_cli_progress(tmp_path, capsys):
    assert main(["progress"]) == 2
    run = _run_dir(tmp_path, status="finished", finish=True)
    out, summary = tmp_path / "out", tmp_path / "s" / "progress.md"
    args = ["progress", "--all", "--root", str(tmp_path / "runs"), "--out", str(out)]
    assert main([*args, "--no-plots", "--summary", str(summary)]) == 0
    assert (out / "demo_sys" / "prep" / "progress.json").is_file()
    assert "demo_sys" in summary.read_text()
    assert main(["progress", "--summary", str(summary), "--collect", str(out)]) == 0
    assert os.path.relpath(out / "demo_sys" / "prep" / "progress.md", summary.parent) in (
        summary.read_text()
    )
    assert not (run / "progress.json").exists()


def test_extra_burst_dumps_are_listed_not_fatal(tmp_path):
    text = DECK.replace(
        "fix md all npt temp 300 300 200 iso 1 1 2000\n",
        "fix md all npt temp 300 300 200 iso 1 1 2000\n"
        "dump burst all dcd 50 seg01_hold_25C_burst1.dcd\ndump_modify burst unwrap yes\n",
    ).replace("run 40\n", "run 40\nundump burst\n")
    (tmp_path / "in.prep").write_text(text)
    segs = pg.parse_deck(tmp_path / "in.prep")
    assert segs[-1].dcd == ["seg01_hold_25C_burst1.dcd"] and segs[-1].steps == 40
    assert segs[-2].dcd == [] and sum(s.steps for s in segs) == 100
