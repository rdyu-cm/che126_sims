"""Tests for `sepsim analyze sweep` (D49): kappa_T, MSD stitching, the D_COM criterion
and the command end to end on a tiny fake sweep run directory."""

import json
from pathlib import Path

import numpy as np
import pytest

from sepsim import progress as pg
from sepsim.analysis.mobility import (
    average_curves,
    diffusion_coefficient,
    mean_over_batches,
    msd,
    p2_autocorrelation,
    stitch_curves,
)
from sepsim.analysis.thermo import isothermal_compressibility
from sepsim.analysis.units import A3_CM3, AVOGADRO, KB_J_PER_K
from sepsim.cli import main

REPO = Path(__file__).resolve().parents[1]
CG = REPO / "systems" / "pe_cg_amorph_n40_c240_s1"


def _ar1(rng, n, sigma, phi):
    """Stationary AR(1) series with marginal std sigma and lag-1 correlation phi."""
    e = rng.normal(0, sigma * np.sqrt(1 - phi**2), n)
    x = np.empty(n)
    x[0] = rng.normal(0, sigma)
    for k in range(1, n):
        x[k] = phi * x[k - 1] + e[k]
    return x


def test_kappa_formula_and_units():
    v = 1000.0 + np.array([-2.0, 0.0, 2.0, 0.0] * 10)
    c = isothermal_compressibility(v, 300.0)
    var = np.mean((v - v.mean()) ** 2)
    expected = var / (KB_J_PER_K * 300.0 * v.mean()) * 1e-21  # A^3/J -> 1/GPa
    assert c.kappa_T == pytest.approx(expected, rel=1e-12)
    assert c.V_mean == pytest.approx(1000.0) and c.V_std == pytest.approx(np.sqrt(2.0))
    with pytest.raises(ValueError):
        isothermal_compressibility([1.0, 2.0], 300.0)


def test_kappa_on_correlated_gaussian_volume():
    """A Gaussian volume series with known variance: kappa_T is recovered and the SEM
    (statistical inefficiency of (V - <V>)^2) matches the spread over replicas."""
    rng = np.random.default_rng(7)
    t, v0 = 400.0, 2.7e5
    kappa = 1.2  # 1/GPa -> sigma_V^2 = kappa k_B T V * 1e21 (A^6)
    sigma = np.sqrt(kappa * 1e21 * KB_J_PER_K * t * v0)
    est = [isothermal_compressibility(v0 + _ar1(rng, 4000, sigma, 0.8), t) for _ in range(60)]
    k = np.array([e.kappa_T for e in est])
    sem = np.array([e.kappa_T_sem for e in est])
    assert k.mean() == pytest.approx(kappa, rel=0.02)
    assert np.mean(sem) == pytest.approx(k.std(ddof=1), rel=0.35)
    assert all(e.g > 2.0 for e in est)  # correlated: g well above 1


def test_stitch_and_average_curves():
    short = (np.arange(11) * 0.1, np.arange(11) * 1.0)
    long_ = (np.arange(6) * 0.5, 100.0 + np.arange(6))
    lags, vals, src = stitch_curves(*short, *long_)
    np.testing.assert_allclose(lags, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0, 1.5, 2.0, 2.5])
    np.testing.assert_allclose(vals[:5], [0, 1, 2, 3, 4])
    assert vals[5] == 101.0  # the long curve wins from its first nonzero lag
    assert src.tolist() == [0] * 5 + [1] * 5
    a = (np.arange(3) * 0.1, np.array([0.0, 1.0, 2.0]), 3)
    b = (np.arange(2) * 0.1, np.array([0.0, 4.0]), 2)
    lags, avg = average_curves([a, b])
    np.testing.assert_allclose(avg, [0.0, (2 * 1.0 + 1 * 4.0) / 3, 2.0])  # origins n - m


def test_mean_over_batches_equals_unbatched():
    rng = np.random.default_rng(3)
    r = np.cumsum(rng.normal(size=(40, 37, 3)), axis=0)
    for fn in (msd, p2_autocorrelation):
        _, full = fn(r, 0.5, 20)
        _, part = mean_over_batches(fn, r, 0.5, 20, batch_elems=64 * 3 * 4)  # 4 per batch
        np.testing.assert_allclose(part, full, rtol=1e-10, atol=1e-12)


def test_diffusion_criterion():
    rng = np.random.default_rng(5)
    d, dt = 0.25, 1.0
    r = np.cumsum(rng.normal(0, np.sqrt(2 * d * dt), size=(2000, 300, 3)), axis=0)
    lags, m = msd(r, dt, 500)
    fit = diffusion_coefficient(lags, m)
    assert fit.diffusive and fit.D == pytest.approx(d, rel=0.05)
    assert fit.t_end == pytest.approx(500.0) and fit.t_end / fit.t_start >= 2.0
    # subdiffusive (t^0.5): not diffusive, max slope reported
    t = np.arange(0, 1000.0)
    sub = diffusion_coefficient(t, 3.0 * np.sqrt(t))
    assert not sub.diffusive and sub.D is None and sub.slope_max == pytest.approx(0.5, abs=0.02)
    # crossover t^0.5 -> t: local slope (6Dt + 5 sqrt t)/(6Dt + 10 sqrt t) passes 0.9 near t = 180
    fit = diffusion_coefficient(t, 6 * 0.5 * t + 10.0 * np.sqrt(t))
    assert fit.diffusive and 120 < fit.t_start < 300 and fit.D == pytest.approx(0.5, rel=0.1)
    # slope >= 0.9 only over less than a factor 2 at the end: not diffusive
    late = np.where(t < 700, np.sqrt(t), np.sqrt(700) * (t / 700))
    assert not diffusion_coefficient(t, late).diffusive


# ---- end to end on a tiny fake sweep ----

GRID = [(1, "hold", 25), (2, "step", 50), (3, "hold", 90), (4, "hold", 130), (5, "hold", 160)]


def _deck_text():
    lines = [
        "# sepsim 0.1.0 deck: sweep",
        "# system pe_cg_amorph_n40_c240_s1 (cg), seed 1",
        "timestep 10",
        "thermo_style custom step time temp press enthalpy vol density cpu",
    ]
    for i, kind, t in GRID:
        stem = f"seg{i:02d}_{kind}_{t}C"
        lines += [
            "",
            f"# ---- Segment {i}: {kind} at {t} C ({t + 273.15:.2f} K), 1 ps -> {stem}.dcd",
            f"fix md all npt temp {t + 273.15:.2f} {t + 273.15:.2f} 1000 iso 1 1 10000",
            f"dump traj all dcd 10 {stem}.dcd",
        ]
        if kind == "hold":
            for k in (1, 2):
                lines += [
                    f"dump burst all dcd 1 {stem}_burst{k:02d}.dcd",
                    "run 10",
                    "undump burst",
                    "run 40",
                ]
        else:
            lines.append("run 100")
        lines += ["undump traj", "unfix md"]
    return "\n".join(lines) + "\n"


MASS = 134737.9


def _volume(t_c):
    return 2.68e5 * (1 + 7e-4 * (t_c - 25.0))


def _log_text(rng, segments):
    head = "   Step   Time   Temp   Press   Enthalpy   Volume   Density   CPU\n"
    out, step = "", 0
    for seg in segments:
        t_c = seg.t_c
        for n in seg.run_steps:
            out += head
            for s in range(step, step + n + 1):
                v = _volume(t_c) + rng.normal(0, 1000.0)
                h = -4770.0 + 27.0 * (t_c - 25.0) + rng.normal(0, 50.0)
                rho = MASS / (AVOGADRO * v * A3_CM3)
                out += f" {s} {s * 10.0} {t_c + 273.15} 1 {h} {v} {rho} {s * 0.01}\n"
            out += f"Loop time of 1 on 1 procs for {n} steps with 3200 atoms\n"
            step += n
    return out


def _write_dcd(path, frames):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(frames.shape[1], trajectory=True)
    with DCDWriter(str(path), frames.shape[1]) as w:
        for x in frames:
            u.atoms.positions = x
            u.dimensions = [100.0, 100.0, 100.0, 90.0, 90.0, 90.0]
            w.write(u.atoms)


@pytest.fixture(scope="module")
def fake_sweep(tmp_path_factory):
    from sepsim.build.datafile import read_data_file

    root = tmp_path_factory.mktemp("runs")
    run = root / "pe_cg_amorph_n40_c240_s1" / "sweep"
    run.mkdir(parents=True)
    (run / "in.sweep").write_text(_deck_text())
    segments = pg.parse_deck(run / "in.sweep")
    rng = np.random.default_rng(11)
    (run / "log.lammps").write_text(_log_text(rng, segments))
    man = {"status": "finished", "hostname": "n", "deck": {"path": "in.sweep"}}
    (run / "run_manifest.json").write_text(json.dumps(man))
    x0 = read_data_file(CG / "data.lmp").unwrapped()

    def walk(n, step):
        return (x0 + np.cumsum(rng.normal(0, step, size=(n,) + x0.shape), axis=0)).astype(
            np.float32
        )

    _write_dcd(run / "seg01_hold_25C.dcd", walk(11, 0.3))  # hold at 25 C: 0.1 ps frames
    for k in (1, 2):
        _write_dcd(run / f"seg01_hold_25C_burst{k:02d}.dcd", walk(11, 0.05))
    _write_dcd(run / "seg05_hold_160C.dcd", walk(11, 0.4))  # no bursts at 160 C
    return run


def test_cli_analyze_sweep_end_to_end(fake_sweep, tmp_path, capsys):
    out = tmp_path / "out"
    code = main(
        ["analyze", "sweep", str(fake_sweep), "--out", str(out), "--systems", str(CG.parent)]
    )
    assert code == 0, capsys.readouterr().err
    assert capsys.readouterr().out.strip() == str(out / "results.md")
    r = json.loads((out / "results.json").read_text())
    assert [s["index"] for s in r["segments"]] == [1, 2, 3, 4, 5]
    assert r["mass_gmol"] == pytest.approx(MASS, rel=1e-6)
    hold = r["segments"][0]["stats"]
    assert hold["rows"] == 101 and hold["rows_used"] == 91  # first 10% dropped
    assert r["segments"][1]["stats"]["rows_used"] == 51  # step: second half
    # kappa_T from the volume noise (sigma 1000 A^3)
    for h in r["holds"]:
        expect = 1000.0**2 / (KB_J_PER_K * (h["t_c"] + 273.15) * _volume(h["t_c"])) * 1e-21
        assert h["kappa"]["kappa_T_GPa"] == pytest.approx(expect, rel=0.4)
    whole = r["fits"]["alpha_V"][0]
    assert whole["window_c"] == [25.0, 160.0] and whole["n"] == 5
    t_mean = np.mean([t for _, _, t in GRID])  # alpha_V = (1/<V>) dV/dT over the points
    assert whole["alpha_V_per_K"] == pytest.approx(7e-4 / (1 + 7e-4 * (t_mean - 25)), rel=0.05)
    assert r["fits"]["cp"][0]["cp_J_gK"] == pytest.approx(27.0 * 4184 / MASS, rel=0.1)
    t25, t90, _, t160 = (h["traj"] for h in r["holds"])
    assert t25["available"] and t25["bursts"] == {"listed": 2, "used": 2}
    assert t25["frames"] == 11 and t25["frame_ps"] == pytest.approx(0.1)
    c = t25["curves"]
    src = np.array(c["msd_src"])
    lags = np.array(c["msd_lag_ps"])
    assert (src[lags < 0.1 - 1e-9] == 0).all() and (src[lags >= 0.1 - 1e-9] == 1).all()
    assert lags[0] == pytest.approx(0.01)  # burst frames
    assert t25["c_n"]["plateau"]["mean"] > 1.0 and t25["rg"]["rg_A"]["mean"] > 10.0
    assert not t90["available"] and "trajectory not available" in t90["notes"][0]
    assert t160["available"] and t160["bursts"]["used"] == 0
    assert any("burst DCDs not found" in n for n in t160["notes"])
    md = (out / "results.md").read_text()
    assert "## Isothermal compressibility" in md and "trajectory not available" in md
    assert "not comparable to experiment" in md
    assert set(r["segments"][0]["drift"]) == {"density", "enthalpy"}
    assert set(r["segments"][0]["convergence"]) == {"density", "enthalpy"}
    assert "## Equilibration" in md and "| drift |" in md
    c = r["convergence"][0]
    assert c["kind"] == "hold" and set(c["quantities"]) == {"T", "density", "volume", "enthalpy"}
    assert c["window"][0] > c["t_start_ps"] and c["sem_vs_block"]["density"]
    for p in ("equilibration", "equilibration_holds"):
        assert (out / f"{p}.png").stat().st_size > 1000
    for p in ("thermo_vs_T", "kappa_T", "alpha_V", "msd", "p2_acf", "chain_vs_T"):
        assert (out / f"{p}.png").stat().st_size > 1000
    assert not (fake_sweep / "results.md").exists()


def test_drift_flags_and_block_convergence():
    from sepsim.analyze import block_averages, block_convergence, drift_flags

    rng = np.random.default_rng(9)
    flat = _ar1(rng, 4000, 1.0, 0.5)
    ramp = flat + np.linspace(0.0, 3.0, 4000)
    d = drift_flags({"flat": flat, "ramp": ramp, "const": np.ones(4000)}, 0.1)
    assert not d["flat"]["drift"] and d["ramp"]["drift"] and "const" not in d
    c = block_convergence(flat, 0.1)
    assert c["converged"] and set(c["block_sem"]) == {"32", "16", "8"}
    assert c["block_sem"]["32"] == pytest.approx(c["sem"], rel=0.5)
    b = block_averages(np.arange(4000.0), ramp)
    assert len(b) == 8 and b[-1]["mean"] > b[0]["mean"]


def test_cli_analyze_rejects_pore_and_missing(tmp_path, capsys):
    run = tmp_path / "x" / "pore"
    run.mkdir(parents=True)
    (run / "in.pore").write_text("# sepsim deck: pore\n")
    assert main(["analyze", "sweep", str(run), "--out", str(tmp_path / "o")]) == 1
    assert "pore runs" in capsys.readouterr().err
    empty = tmp_path / "y" / "sweep"
    empty.mkdir(parents=True)
    assert main(["analyze", "sweep", str(empty)]) == 1
    assert "no deck" in capsys.readouterr().err
    assert main(["analyze"]) == 2


def test_no_traj_and_default_out(fake_sweep, tmp_path, monkeypatch):
    from sepsim.analyze import analyze_sweep

    monkeypatch.chdir(tmp_path)
    r, out_dir = analyze_sweep(fake_sweep, systems=CG.parent, traj=False, plots=False)
    assert out_dir == Path("results/analysis/pe_cg_amorph_n40_c240_s1/sweep")
    assert all(not h["traj"]["available"] for h in r["holds"])
    assert "plots" not in r
