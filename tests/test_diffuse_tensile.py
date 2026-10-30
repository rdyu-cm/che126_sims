"""D53 `diffuse` and D54 `tensile` protocols: decks, stage naming, progress D_COM, analysis."""

import json
from pathlib import Path

import numpy as np
import pytest

from sepsim import progress as pg
from sepsim.analysis.mobility import msd
from sepsim.analysis.tensile import ATM_MPA, analyze_axis, moving_average, read_ave_time
from sepsim.analyze_tensile import analyze_tensile, render_markdown, write_results
from sepsim.cli import main
from sepsim.lammps.render import (
    RenderError,
    data_temperature_warning,
    default_stage,
    rate_label,
    render_deck,
    resolve_params,
)

REPO = Path(__file__).resolve().parents[1]
SYSTEMS = REPO / "systems"
CG = SYSTEMS / "pe_cg_amorph_n40_c240_s1"
UA = SYSTEMS / "pe_ua_amorph_n40_c240_s1"
HEAD = "   Step   Time   Temp   Density   Enthalpy   PotEng   CPU\n"


def commands(deck):
    out = []
    for raw in deck.splitlines():
        tokens = raw.split("#", 1)[0].split()
        if tokens:
            out.append(tokens)
    return out


def _deck(tmp_path, protocol, name, **kw):
    run = tmp_path / "runs" / CG.name / name
    run.mkdir(parents=True)
    deck = run / f"in.{protocol}"
    data = run / "../sweep/hold_25C.data"
    deck.write_text(render_deck(protocol, CG, data=data, deck_dir=run, require_data=False, **kw))
    return run, deck


# --------------------------------------------------------------------------- diffuse (D53)


def test_diffuse_deck_round_trip(tmp_path):
    _, deck = _deck(tmp_path, "diffuse", "diffuse_160C", overrides={"t_c": 160})
    text = deck.read_text()
    cmds = commands(text)
    assert ["read_data", "../sweep/hold_25C.data", "nocoeff"] in cmds
    assert "# ---- Stage 1: NPT hold 300000 ps at 433.15 K (diffuse" in text
    npt = ["fix", "md", "all", "npt", "temp", "433.15", "433.15", "1000", "iso", "1", "1"]
    assert [*npt, "10000"] in cmds
    assert not any(c[0] in ("velocity", "minimize") for c in cmds)
    assert [c for c in cmds if c[0] == "dump"] == [
        ["dump", "hold", "all", "dcd", "10000", "hold.dcd"]  # 100 ps at 10 fs
    ]
    assert [c[1] for c in cmds if c[0] == "run"] == ["2500000"] * 12
    assert [c[1] for c in cmds if c[0] == "write_data"] == [
        f"hold_{k}ns.data" for k in range(25, 301, 25)
    ]
    segs = pg.parse_deck(deck)
    assert len(segs) == 1
    s = segs[0]
    assert s.run_steps == [2_500_000] * 12 and s.steps == 30_000_000
    assert s.dcd == ["hold.dcd"] and s.dump_every == [10_000] and s.dt_fs == 10.0
    assert s.ensemble == "npt" and s.t_target_k == pytest.approx(433.15)
    assert s.name == "Stage 1: NPT hold 300000 ps at 433.15 K"


def test_diffuse_smoke_defaults_and_errors():
    smoke = commands(render_deck("diffuse", CG, data=CG / "data.lmp", preset="smoke"))
    assert [c[1] for c in smoke if c[0] == "run"] == ["100", "100"]
    assert [c[1] for c in smoke if c[0] == "write_data"] == [
        "hold_0.001ns.data",
        "hold_0.002ns.data",
    ]
    ua = resolve_params("ua", protocol="diffuse")
    assert ua["diffuse_ps"] < resolve_params("cg", protocol="diffuse")["diffuse_ps"]
    with pytest.raises(RenderError, match="must be > 0"):
        render_deck("diffuse", CG, data=CG / "data.lmp", overrides={"chunk_ps": 0})
    with pytest.raises(RenderError, match="--data"):
        render_deck("diffuse", CG, deck_dir=Path("results/runs/x/diffuse_25C"))


def test_stage_names_and_data_warning():
    assert default_stage("diffuse", "cg", {"t_c": "90"}) == "diffuse_90C"
    assert default_stage("diffuse", "cg") == "diffuse_25C"
    assert default_stage("tensile", "cg", {"t_c": "130"}) == "tensile_130C"
    assert default_stage("tensile", "cg", {"t_c": "130", "rate_per_s": "1e9"}) == (
        "tensile_130C_r1e9"
    )
    assert default_stage("sweep", "cg") == "sweep"
    assert rate_label(1e8) == "1e8" and rate_label(2.5e9) == "2.5e9" and rate_label(5) == "5"
    assert data_temperature_warning("diffuse", "../sweep/hold_90C.data", 90.0) is None
    assert "160 C sweep hold" in data_temperature_warning("tensile", "x/hold_160C.data", 25.0)
    assert data_temperature_warning("diffuse", "../extend/hold_ext_60ns.data", 25.0) is None
    assert data_temperature_warning("cool", "hold_160C.data", 25.0) is None


def test_cli_diffuse_and_tensile_jobs_per_temperature(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    base = ["--system", str(CG), "--job", "--time", "3-00:00:00", "--node", "n1", "--cpus", "2"]
    for t in (25, 90):
        args = ["render", "diffuse", *base, "--data", f"../sweep/hold_{t}C.data"]
        assert main([*args, "--set", f"t_c={t}"]) == 0
    assert (
        main(["render", "tensile", *base, "--data", "../sweep/hold_90C.data", "--set", "t_c=90"])
        == 0
    )
    rate = ["--set", "t_c=90", "--set", "rate_per_s=1e9"]
    assert main(["render", "tensile", *base, "--data", "../sweep/hold_90C.data", *rate]) == 0
    # a mismatched snapshot warns
    mismatch = ["--out", f"results/runs/{CG.name}/diffuse_odd"]
    assert main(["render", "diffuse", *base, "--data", "../sweep/hold_90C.data", *mismatch]) == 0
    err = capsys.readouterr().err
    assert "hold_90C.data is the 90 C sweep hold but t_c = 25 C" in err
    jobs = tmp_path / "jobs" / CG.name
    for stage, protocol, data in (
        ("diffuse_25C", "diffuse", "../sweep/hold_25C.data"),
        ("diffuse_90C", "diffuse", "../sweep/hold_90C.data"),
        ("tensile_90C", "tensile", "../sweep/hold_90C.data"),
        ("tensile_90C_r1e9", "tensile", "../sweep/hold_90C.data"),
    ):
        deck = (jobs / stage / f"in.{protocol}").read_text()
        assert next(c for c in commands(deck) if c[0] == "read_data")[1] == data
        job = (jobs / stage / "job.sh").read_text()
        assert f"RUN_DIR={tmp_path}/results/runs/{CG.name}/{stage}" in job
        assert f"if [ ! -f {data} ]" in job
    assert main(["render", "diffuse", "--system", str(CG)]) == 1
    assert "--data" in capsys.readouterr().err


def _write_dcd(path, frames):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(frames.shape[1], trajectory=True)
    with DCDWriter(str(path), frames.shape[1]) as w:
        for x in frames:
            u.atoms.positions = x
            u.dimensions = [70.0, 70.0, 70.0, 90.0, 90.0, 90.0]
            w.write(u.atoms)


def test_com_diffusion_of_a_random_walk():
    rng = np.random.default_rng(3)
    dt_ns, s = 0.1, 2.0  # frame interval, per-axis step SD (A)
    walk = np.cumsum(rng.normal(scale=s, size=(400, 200, 3)), axis=0)
    lags, m = msd(walk, dt_ns)
    d = pg.com_diffusion(lags, m, rg2_A2=10.0)
    assert d["diffusive"] and d["D_A2_ns"] == pytest.approx(s**2 / (2 * dt_ns), rel=0.1)
    assert d["D_cm2_s"] == pytest.approx(d["D_A2_ns"] * 1e-7)
    flag = pg.d_com_flag(d)
    assert flag.startswith("D_COM diffusive ") and "cm²/s over" in flag
    sub = pg.com_diffusion(lags[1:], 5.0 * lags[1:] ** 0.5, rg2_A2=1.0)  # subdiffusive
    assert not sub["diffusive"]
    assert pg.d_com_flag(sub).startswith("D_COM not diffusive (log-slope 0.50 at the longest lag")
    # D55: slope ~1 but the chains have not left their own size: not diffusive
    big = pg.com_diffusion(lags, m, rg2_A2=float(m[-1]))
    assert not big["diffusive"] and big["msd_rg2_end"] == pytest.approx(1.0)
    assert "MSD/Rg² 1.00" in pg.d_com_flag(big)
    eta = pg.rouse_viscosity(1e-7, 5000.0, 400.0, 40, 3.0e5)
    rho_n = 40 / 3.0e5 * 1e30
    assert eta == pytest.approx(rho_n * 1.380649e-23 * 400 * 5000e-20 / (36 * 1e-11))


def test_progress_reports_d_com_for_a_diffuse_run(tmp_path):
    """A synthetic hold.dcd whose chains random-walk as rigid bodies: `sepsim progress`
    flags D_COM (no D37/D47 verdicts), also while the hold runs."""
    from sepsim.build.datafile import read_data_file

    over = {"t_c": 160, "diffuse_ps": 1000.0, "chunk_ps": 500.0, "hold_dump_ps": 10.0}
    run, _ = _deck(tmp_path, "diffuse", "diffuse_160C", overrides=over)
    data = read_data_file(CG / "data.lmp")
    x0 = data.unwrapped()
    mol = data.sorted_atoms()[:, 1].astype(int)
    _, mol = np.unique(mol, return_inverse=True)
    rng = np.random.default_rng(0)
    s = 4.0  # A per axis per 10 ps frame: COM MSD at the longest lags >> 2 <Rg^2> (D55)
    steps = rng.normal(scale=s, size=(200, mol.max() + 1, 3))
    steps[0] = 0.0
    shift = np.cumsum(steps, axis=0)
    frames = np.stack([x0 + shift[k][mol] for k in range(200)]).astype(np.float32)
    _write_dcd(run / "hold.dcd", frames)
    log = ""
    for k in range(2):
        rows = "".join(
            f"  {k * 50000 + 5000 * j}  {10.0 * (k * 50000 + 5000 * j)}  433  0.76  -10  5"
            f"  {0.1 * j}\n"
            for j in range(11)
        )
        log += HEAD + rows
        if k == 0:
            log += "Loop time of 1 on 1 procs for 50000 steps with 3200 atoms\n"
    (run / "log.lammps").write_text(log)
    man = {"status": "started", "hostname": "n", "start_time": "2026-10-30T00:00:00+00:00"}
    (run / "run_manifest.json").write_text(json.dumps(man))
    r = pg.progress_report(run, systems=SYSTEMS, now=1e6, plots=False)
    h = r["hold"]
    assert h["state"] == "running" and h["diffuse"] and h["t_c"] == pytest.approx(160)
    assert h["n_chains"] == 40 and h["volume_A3"] == pytest.approx(70.0**3, rel=1e-5)
    d = h["d_com"]
    # MSD = 6 D t with D = s^2 / (2 * 10 ps); COM-drift removal over 40 chains: x (1 - 1/40)
    want = s**2 / (2 * 0.01) * (1 - 1 / 40)
    assert d["diffusive"] and d["D_A2_ns"] == pytest.approx(want, rel=0.35)
    assert d["eta_rouse_pa_s"] > 0
    assert r["flags"][0].startswith("D_COM diffusive")
    assert not any(f.startswith(("D37", "D47", "R_ee")) for f in r["flags"])
    md = pg.render_markdown(r)
    assert "chain diffusion (D53)" in md and "Rouse viscosity" in md and "PASS" not in md


# --------------------------------------------------------------------------- tensile (D54)


def test_tensile_deck_round_trip(tmp_path):
    _, deck = _deck(tmp_path, "tensile", "tensile_25C")
    text = deck.read_text()
    cmds = commands(text)
    assert [c for c in cmds if c[0] == "read_data"] == [
        ["read_data", "../sweep/hold_25C.data", "nocoeff"]
    ] * 3
    assert sum(c == ["clear"] for c in cmds) == 2
    # 0.5 / (1e8 /s * 10 fs) = 500,000 steps per axis; erate in 1/fs
    assert [c[1] for c in cmds if c[0] == "run"] == ["500000"] * 3
    deform = [c for c in cmds if c[:2] == ["fix", "pull"]]
    assert [c[5:] for c in deform] == [[a, "erate", "1e-07", "remap", "x"] for a in "xyz"]
    npt = [c for c in cmds if c[:4] == ["fix", "md", "all", "npt"]]
    assert len(npt) == 3
    for d, f in zip(deform, npt, strict=True):
        pulled = d[5]
        barostat = [t for t in f if t in ("x", "y", "z", "iso", "aniso", "tri")]
        assert pulled not in barostat and "iso" not in barostat and "aniso" not in barostat
        assert len(barostat) == 2 and f[-2] == "couple" and f[-1] == "".join(barostat)
        assert f[4:7] == ["temp", "298.15", "298.15"]
    ave = [c for c in cmds if c[0] == "fix" and len(c) > 3 and c[3] == "ave/time"]
    assert [c[-1] for c in ave] == ["tensile_x.txt", "tensile_y.txt", "tensile_z.txt"]
    assert ave[0][4:7] == ["1", "100", "100"]
    assert ["variable", "tx_l0", "equal", "$(lx)"] in cmds
    assert [c[-1] for c in cmds if c[0] == "dump"] == [f"tensile_{a}.dcd" for a in "xyz"]
    assert [c[4] for c in cmds if c[0] == "dump"] == ["10000"] * 3
    thermo = [c for c in cmds if c[0] == "thermo_style"]
    assert len(thermo) == 3 and all({"pxx", "pyy", "pzz"} <= set(t) for t in thermo)
    segs = pg.parse_deck(deck)
    assert [s.name for s in segs] == [
        f"Segment {k + 1}: tensile along {a} at 25 C, 1e8 /s" for k, a in enumerate("xyz")
    ]
    assert [s.steps for s in segs] == [500_000] * 3
    assert [s.dcd for s in segs] == [[f"tensile_{a}.dcd"] for a in "xyz"]
    assert all(s.ensemble == "npt" and s.sweep_index is None for s in segs)


def test_tensile_parameters_and_bulk_thermo_unchanged():
    smoke = commands(render_deck("tensile", CG, data=CG / "data.lmp", preset="smoke"))
    assert [c[1] for c in smoke if c[0] == "run"] == ["100"] * 3  # 0.01 at 1e10 /s
    one = commands(
        render_deck(
            "tensile",
            CG,
            data=CG / "data.lmp",
            overrides={"axes": "z", "rate_per_s": 1e9, "strain_max": 0.05},
        )
    )
    assert [c[1] for c in one if c[0] == "run"] == ["5000"] and ["clear"] not in one
    for bad, match in (
        ({"axes": "x,x"}, "axes"),
        ({"axes": "q"}, "axes"),
        ({"rate_per_s": 0}, "must be > 0"),
    ):
        with pytest.raises(RenderError, match=match):
            render_deck("tensile", CG, data=CG / "data.lmp", overrides=bad)
    # other bulk decks keep the thermo columns without the pressure tensor
    thermo = next(c for c in commands(render_deck("prep", UA)) if c[0] == "thermo_style")
    assert "pxx" not in thermo


def _ave_file(path, axis, eps, sigma_mpa, nu, l0=60.0, p_ref=1.0, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    p_ax = p_ref - sigma_mpa / ATM_MPA + noise * rng.normal(size=len(eps))
    lat = l0 * (1 + eps) ** (-nu)
    cols = {"x": None, "y": None, "z": None}
    for a in cols:
        cols[a] = l0 * (1 + eps) if a == axis else lat
    press = {a: (p_ax if a == axis else np.full(len(eps), p_ref)) for a in "xyz"}
    v = f"t{axis}"
    lines = [
        f"# Time-averaged data for fix {v}_avg",
        (
            f"# TimeStep v_{v}_e c_thermo_press[1] c_thermo_press[2] c_thermo_press[3]"
            f" v_{v}_lx v_{v}_ly v_{v}_lz c_thermo_temp"
        ),
    ]
    for k, e in enumerate(eps):
        lines.append(
            f"{100 * (k + 1)} {e:.8g} {press['x'][k]:.8g} {press['y'][k]:.8g}"
            f" {press['z'][k]:.8g} {cols['x'][k]:.8g} {cols['y'][k]:.8g} {cols['z'][k]:.8g} 298"
        )
    path.write_text("\n".join(lines) + "\n12000 0.5")  # a partly written last line


def test_tensile_axis_analysis_recovers_e_nu_and_flow(tmp_path):
    eps = np.linspace(0.0005, 0.5, 1000)
    # linear to the yield strain 0.05 at E = 400 MPa, then a 20 MPa plateau
    sigma = np.minimum(400.0 * eps, 20.0)
    _ave_file(tmp_path / "tensile_y.txt", "y", eps, sigma, nu=0.5)
    data = read_ave_time(tmp_path / "tensile_y.txt")
    assert len(data["e"]) == 1000 and set(data) >= {"pxx", "pyy", "pzz", "lx", "temp"}
    r = analyze_axis(data, "y", fit_max=0.02)
    assert r["E_MPa"] == pytest.approx(400.0, rel=1e-6)
    assert r["nu_fit"] == pytest.approx(0.5, abs=1e-6) and r["nu_run"] == pytest.approx(0.5)
    assert r["flow_MPa"] == pytest.approx(20.0, rel=1e-6)
    assert r["peak_MPa"] == pytest.approx(20.0, rel=1e-3)
    c = r["curves"]
    # nu = 0.5: A/A0 = 1/(1+e), engineering stress = sigma / (1 + e)
    assert np.allclose(c["sigma_eng"], sigma / (1 + eps), rtol=1e-6)
    assert np.allclose(c["lat_true_strain"], -0.5 * np.log1p(eps), atol=1e-6)
    assert np.nanmax(np.abs(c["nu_secant"] - 0.5)) < 1e-4
    # a short run: no flow stress
    short = analyze_axis({k: v[:100] for k, v in data.items()}, "y", fit_max=0.02)
    assert short["flow_MPa"] is None and short["E_MPa"] == pytest.approx(400.0, rel=1e-6)
    m, full = moving_average(np.arange(10.0), np.arange(10.0), 2.0)
    assert m[5] == 5.0 and not full[0] and full[5]


def test_analyze_tensile_report_and_cli(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)  # the default output directory is relative to the cwd
    run, _ = _deck(tmp_path, "tensile", "tensile_25C")
    eps = np.linspace(0.0005, 0.5, 1000)
    for k, (ax, e_mod) in enumerate((("x", 300.0), ("y", 400.0), ("z", 500.0))):
        _ave_file(run / f"tensile_{ax}.txt", ax, eps, e_mod * eps / (1 + 10 * eps), 0.4, seed=k)
    report, out = analyze_tensile([run], fit_max=0.01)
    assert out == Path("results/analysis") / CG.name / "tensile_25C"
    s = report["runs"][0]["summary"]
    assert s["E_MPa"]["n"] == 3 and s["E_MPa"]["mean"] == pytest.approx(400.0, rel=0.1)
    assert s["E_MPa"]["sd"] == pytest.approx(100.0, rel=0.15)
    assert s["nu_fit"]["mean"] == pytest.approx(0.4, abs=1e-6)
    assert not report["runs"][0]["notes"]
    md = render_markdown(report)
    assert "| mean ± SD |" in md and "Caveats" in md and "viscoelastic" in md
    write_results(report, tmp_path / "res")
    js = json.loads((tmp_path / "res" / "results.json").read_text())
    assert js["runs"][0]["axes"][0]["axis"] == "x"
    assert (tmp_path / out / "stress_strain.png").is_file()
    # CLI: two runs (same T and rate) pooled, written under --out
    run2 = run.parent / "tensile_25C_b"
    run2.mkdir()
    (run2 / "in.tensile").write_text((run / "in.tensile").read_text())
    _ave_file(run2 / "tensile_x.txt", "x", eps[:300], 350.0 * eps[:300], 0.45)
    assert main(["analyze", "tensile", str(run), str(run2), "--out", "cmp"]) == 0
    md = (tmp_path / "cmp" / "results.md").read_text()
    assert "Pooled over runs" in md and "tensile_25C_b" in md
    assert "axis y: tensile_y.txt not found" in md and "reached strain 0.150" in md
    assert (tmp_path / "cmp" / "stress_strain.png").is_file()
    assert (tmp_path / "cmp" / "poisson.png").is_file()
    assert main(["analyze", "tensile", str(tmp_path)]) == 1
    assert "no in.tensile" in capsys.readouterr().err
