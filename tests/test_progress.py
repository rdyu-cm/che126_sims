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


# ---- chunked holds (D46) and hold extensions (D47) ----

PORE = SYSTEMS / "pe_ua_pore_w10nm_n40_c240_s1"


@pytest.mark.parametrize(("protocol", "system"), [("sweep", UA), ("pore", PORE)])
def test_parse_chunked_holds_are_one_segment(tmp_path, protocol, system):
    """A hold run in 1 ns chunks with bursts (D46) is one segment listing its burst files."""
    _, deck = _deck(tmp_path, protocol, system=system)
    segs = pg.parse_deck(deck)
    md = [s for s in segs if s.sweep_index is not None]
    assert [s.sweep_index for s in md] == list(range(1, 19))
    holds = [s for s in md if s.sweep_kind == "hold"]
    assert len(holds) == 4
    for h in holds:
        stem = f"seg{h.sweep_index:02d}_hold_{h.t_c:g}C"
        assert h.steps == 5_000_000 and h.run_steps == [5_000, 495_000] * 10  # UA 10 ns
        assert h.dcd == [f"{stem}.dcd"] + [f"{stem}_burst{k:02d}.dcd" for k in range(1, 11)]
        assert h.dump_every == [5_000] + [50] * 10
        assert h.name == f"seg {h.sweep_index:02d} hold {h.t_c:g} C"  # no "(run j/n)"
    steps = [s for s in md if s.sweep_kind == "step"]
    assert all(len(s.run_steps) == 1 and s.steps == 1_000_000 for s in steps)
    # every deck run command is accounted for exactly once
    text = deck.read_text()
    runs = [int(ln.split()[1]) for ln in text.splitlines() if ln.startswith("run ")]
    assert [n for s in segs for n in s.run_steps if s.command == "run"] == runs
    if protocol == "pore":
        assert [s.command for s in segs[:2]] == ["minimize", "run"]
        assert segs[1].name.startswith("Stage 2: surface relaxation")


def test_unchunked_sweep_parses_as_before(tmp_path):
    """burst_period_ps=0 (decks before D46, e.g. the finished CG C240 sweep): one run per segment."""
    _, deck = _deck(tmp_path, "sweep", system=CG, overrides={"burst_period_ps": 0})
    segs = pg.parse_deck(deck)
    assert len(segs) == 18 and all(len(s.run_steps) == 1 for s in segs)
    assert [s.dcd for s in segs] == [[s.dcd[0]] for s in segs]


CHUNK_DECK = """# sepsim 0.1.0 deck: sweep
# system demo_sys (ua), seed 1
timestep 2
thermo_style custom step time temp density enthalpy pe cpu

# ---- Segment 1: hold at 25 C (298.15 K), 0.06 ps
fix md all npt temp 298.15 298.15 200 iso 1 1 2000
dump traj all dcd 10 seg01_hold_25C.dcd
dump_modify traj unwrap yes
dump burst all dcd 1 seg01_hold_25C_burst01.dcd
dump_modify burst unwrap yes
run 10
undump burst
run 20
dump burst all dcd 1 seg01_hold_25C_burst02.dcd
dump_modify burst unwrap yes
run 10
undump burst
run 20
undump traj
unfix md
write_data hold_25C.data

# ---- Segment 2: step at 35 C (308.15 K), 0.02 ps
fix md all npt temp 308.15 308.15 200 iso 1 1 2000
dump traj all dcd 10 seg02_step_35C.dcd
run 40
undump traj
unfix md
"""


def _block(step0, n, rho, stride=1, cpu0=0.0):
    rows = "".join(
        f"  {step0 + stride * k}  {2.0 * (step0 + stride * k)}  298  {rho[k]}  -10  5"
        f"  {cpu0 + 0.1 * k}\n"
        for k in range(n)
    )
    return HEAD + rows


def test_chunked_hold_log_state_stats_and_eta(tmp_path):
    run = tmp_path / "runs" / "demo_sys" / "sweep"
    run.mkdir(parents=True)
    (run / "in.sweep").write_text(CHUNK_DECK)
    segs = pg.parse_deck(run / "in.sweep")
    assert len(segs) == 2 and segs[0].run_steps == [10, 20, 10, 20] and segs[0].steps == 60
    assert segs[0].dcd == [
        "seg01_hold_25C.dcd",
        "seg01_hold_25C_burst01.dcd",
        "seg01_hold_25C_burst02.dcd",
    ]
    rho = 0.80 + 0.001 * np.arange(61)  # one row per step across the hold
    loop = "Loop time of 1 on 1 procs for 10 steps with 10 atoms\n"
    perf = "Performance: 1.0 ns/day, 24 hours/ns, 10.0 timesteps/s\n"
    blocks = [(0, 11), (10, 21), (30, 11), (40, 21)]  # each block repeats the previous last step
    log = ""
    for k, (s0, n) in enumerate(blocks[:3]):
        log += _block(s0, n, rho[s0 : s0 + n]) + (loop + perf if k < 2 else "")
    (run / "log.lammps").write_text(log[: log.rindex("\n", 0, -1) + 1])  # third chunk running
    man = {"status": "started", "hostname": "n", "start_time": "2026-10-23T00:00:00+00:00"}
    (run / "run_manifest.json").write_text(json.dumps(man))
    mtime = (run / "log.lammps").stat().st_mtime
    r = pg.progress_report(run, now=mtime + 10, plots=False)
    hold = r["segments"][0]
    assert r["n_segments"] == 2 and hold["state"] == "running" and r["current"]["index"] == 1
    assert hold["steps_done"] == 30 + 9  # two complete chunk runs + 9 steps of the third
    assert r["steps_total"] == 100 and r["percent"] == pytest.approx(39.0)
    assert r["remaining_h"] == pytest.approx(61 / 10 / 3600)  # 10 steps per CPU second
    assert "log has" not in " ".join(r["notes"])
    # whole hold done: stats over the 61 distinct rows (second half: steps 30..60)
    log = "".join(_block(s0, n, rho[s0 : s0 + n]) + loop + perf for s0, n in blocks)
    log += _block(60, 41, np.full(41, 0.7), cpu0=0.0)
    (run / "log.lammps").write_text(log)
    r = pg.progress_report(run, now=mtime + 10, plots=False)
    hold = r["segments"][0]
    assert hold["state"] == "done" and hold["stats"]["rows"] == 61
    assert hold["stats"]["density"]["mean"] == pytest.approx(rho[30:].mean(), rel=1e-3)
    assert r["segments"][1]["state"] == "running" and r["current"]["index"] == 2


def _extend_layout(tmp_path, ext_frames: int, chunks: int = 2):
    """runs/<CG system>/{prep/hold.dcd (8 frames), extend/{in.extend, hold_ext.dcd}}."""
    from sepsim.build.datafile import read_data_file

    root = tmp_path / "runs" / CG.name
    prep, ext = root / "prep", root / "extend"
    prep.mkdir(parents=True)
    ext.mkdir()
    (prep / "in.prep").write_text(render_deck("prep", CG, deck_dir=prep, require_data=False))
    over = {"extend_ps": 100.0 * chunks, "chunk_ps": 100.0}
    (ext / "in.extend").write_text(
        render_deck("extend", CG, deck_dir=ext, require_data=False, overrides=over)
    )
    x0 = read_data_file(CG / "data.lmp").unwrapped()
    rng = np.random.default_rng(1)
    frames = np.stack([x0 + 0.05 * rng.normal(size=x0.shape) for _ in range(8 + ext_frames)])
    frames = frames.astype(np.float32)
    _write_dcd(prep / "hold.dcd", frames[:8])
    # the extension starts from the prep's last state: its first frame repeats it
    _write_dcd(ext / "hold_ext.dcd", frames[7 : 8 + ext_frames])
    man = {"status": "started", "hostname": "n", "start_time": "2026-10-23T00:00:00+00:00"}
    (ext / "run_manifest.json").write_text(json.dumps(man))
    return ext, frames


def _extend_log(ext, done_chunks: int, chunks: int = 2):
    steps = 10_000  # 100 ps at 10 fs
    log = ""
    for k in range(chunks if done_chunks == chunks else done_chunks + 1):
        log += _block(k * steps, 11, np.full(11, 0.75), stride=steps // 10)
        if k < done_chunks:
            log += "Loop time of 1 on 1 procs for 10000 steps with 10 atoms\n"
    (ext / "log.lammps").write_text(log)


def test_extend_monitor_concatenates_prep_hold_and_throttles(tmp_path):
    ext, frames = _extend_layout(tmp_path, ext_frames=6)
    _extend_log(ext, done_chunks=1)
    segs = pg.parse_deck(ext / "in.extend")
    assert len(segs) == 1 and segs[0].run_steps == [10_000, 10_000]
    assert segs[0].dcd == ["hold_ext.dcd"] and segs[0].name.startswith("Stage 1: NPT hold ext")
    t0 = 1_000_000.0
    out = tmp_path / "out"
    r = pg.progress_report(ext, out=out, systems=SYSTEMS, now=t0, plots=False)
    h = r["hold"]
    assert h["state"] == "running" and h["extend"] and not h["cached"]
    # 8 prep frames + 6 new extension frames (its first frame repeats the prep's last)
    assert h["parts"] == [
        {"file": "hold.dcd", "frames": 8},
        {"file": "hold_ext.dcd", "frames": 6},
    ]
    assert h["frames"] == 14 and h["hold_ns"] == pytest.approx(0.13)
    assert h["boundaries_ns"] == [pytest.approx(0.075)]
    assert h["ree_acf"]["lag_ns"] == pytest.approx(0.07)  # half the combined trajectory
    d = h["d47"]
    assert d["passed"] is False and d["acf"] > 0.99 and d["ratio"] < 0.01
    flag = next(f for f in r["flags"] if f.startswith("D47"))
    assert flag.startswith("D47 FAIL (ACF 1.00 at 0.1 ns; MSD/Rg2 0.00; 0.1 ns)")
    assert not any(f.startswith("R_ee") for f in r["flags"])
    md = pg.render_markdown(r)
    assert "prep hold + extension, D47" in md and "hold.dcd 8 frames + hold_ext.dcd 6" in md
    pg.write_report(r, pg.out_dir_for(ext, out))

    def again(dt_s, **kw):
        res = pg.progress_report(ext, out=out, systems=SYSTEMS, now=t0 + dt_s, plots=False, **kw)
        pg.write_report(res, pg.out_dir_for(ext, out))
        return res["hold"]

    # the trajectory grows: not rechecked within 2 h, rechecked after
    _write_dcd(ext / "hold_ext.dcd", np.concatenate([frames[7:], frames[-2:]]))  # 2 more
    h = again(3600)
    assert h["cached"] and h["frames"] == 14 and h["computed_at"] == t0
    h = again(3 * 3600)
    assert not h["cached"] and h["frames"] == 16 and h["computed_at"] == t0 + 3 * 3600
    # unchanged trajectory: kept even after 2 h
    h = again(9 * 3600)
    assert h["cached"] and h["computed_at"] == t0 + 3 * 3600
    # the extension finishes: final computation, then never again
    _extend_log(ext, done_chunks=2)
    man = {"status": "finished", "start_time": "2026-10-23T00:00:00+00:00"}
    (ext / "run_manifest.json").write_text(json.dumps(man))
    h = again(9 * 3600 + 60)
    assert h["state"] == "done" and not h["cached"]
    with (ext / "log.lammps").open("a") as fh:  # force a re-parse of the finished run
        fh.write("Total wall time: 0:00:09\n")
    h = again(30 * 86400)
    assert h["cached"] and h["computed_at"] == t0 + 9 * 3600 + 60


def test_extend_monitor_without_prep_hold_and_plots(tmp_path):
    ext, _ = _extend_layout(tmp_path, ext_frames=7)
    (ext.parent / "prep" / "hold.dcd").unlink()
    _extend_log(ext, done_chunks=1)
    r = pg.progress_report(ext, out=tmp_path / "out", systems=SYSTEMS, now=1e6)
    assert r["hold"]["parts"] == [{"file": "hold_ext.dcd", "frames": 8}]
    assert r["hold"]["boundaries_ns"] == []
    assert any("../prep/hold.dcd not found" in n for n in r["notes"])
    assert {"timeline", "hold_cn", "hold_cn_time", "hold_ree_acf", "hold_com_msd"} <= set(
        r["plots"]
    )
    assert r["plots"]["hold_cn"]["title"].startswith("500 K hold + extension")


def test_d47_criteria():
    def res(acf, ratio):
        return {"ree_acf": {"acf_at_lag": acf, "lag_ns": 50.0}, "com_msd": {"ratio": ratio}}

    assert pg.d47_criteria(res(0.30, 2.1))["passed"] is True
    no_acf = pg.d47_criteria(res(0.40, 2.5))
    assert no_acf["passed"] is False and not no_acf["acf_passed"] and no_acf["msd_passed"]
    no_msd = pg.d47_criteria(res(0.10, 1.99))
    assert no_msd["passed"] is False and no_msd["acf_passed"] and not no_msd["msd_passed"]


def test_prep_hold_check_unchanged_for_prep(tmp_path):
    """The prep keeps the single-hold check: no concatenation, no D47 flag."""
    from sepsim.build.datafile import read_data_file

    x0 = read_data_file(CG / "data.lmp").unwrapped()
    rng = np.random.default_rng(2)
    frames = np.stack([x0 + 0.05 * rng.normal(size=x0.shape) for _ in range(8)])
    _write_dcd(tmp_path / "hold.dcd", frames.astype(np.float32))
    res = pg.hold_chain_checks(tmp_path / "hold.dcd", CG, frame_ps=10.0)
    assert res["parts"] == [{"file": "hold.dcd", "frames": 8}] and res["boundaries_ns"] == []
    assert "d47" not in res


def test_input_stage_picks_the_cooling_run(tmp_path):
    (tmp_path / "in.sweep").write_text("units real\nread_data ../cool/cooled.data nocoeff\n")
    assert pg._input_stage(tmp_path / "in.sweep") == "cool"
    (tmp_path / "in.sweep").write_text("read_data /abs/cooled.data nocoeff\n")
    assert pg._input_stage(tmp_path / "in.sweep") is None
