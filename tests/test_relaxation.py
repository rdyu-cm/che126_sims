"""Tests for the D56 chain-relaxation analysis: Rouse modes, relaxation times, the
crystallinity monitor and `sepsim analyze hold` end to end on a fake extend run."""

import json
from pathlib import Path

import numpy as np
import pytest

from sepsim.analysis.chain import mode_autocorrelation, relaxation_time, rouse_modes
from sepsim.analyze import crystal_parameters, crystallinity_monitor
from sepsim.cli import main

REPO = Path(__file__).resolve().parents[1]
CG = REPO / "systems" / "pe_cg_amorph_n40_c240_s1"
CG_MAN = {"polymer": "pe", "resolution": "cg", "forcefield": {"file": "sdk_cg.yaml"}}


def _ou(rng, n_frames, shape, tau, sigma):
    """Stationary Ornstein-Uhlenbeck series (exact discretization, unit frame time)."""
    a = np.exp(-1.0 / tau)
    x = np.empty((n_frames, *shape))
    x[0] = rng.normal(0, sigma, shape)
    noise = rng.normal(0, sigma * np.sqrt(1 - a**2), (n_frames, *shape))
    for k in range(1, n_frames):
        x[k] = a * x[k - 1] + noise[k]
    return x


def test_rouse_modes_recover_prescribed_ou_modes():
    """Positions built from prescribed Rouse modes (OU processes, tau_p = tau_1/p^2,
    <X_p^2> ~ 1/p^2) by the inverse cosine transform: rouse_modes returns the modes, the
    1/e times match tau_p within 10% and p^2 <X_p^2> is flat."""
    rng = np.random.default_rng(1)
    n_frames, n_chains, n = 8000, 40, 30
    p_max, tau1 = 5, 100.0
    x0 = np.cumsum(rng.normal(0, 0.1, (n_frames, n_chains, 3)), axis=0)  # COM walk
    modes = np.stack(
        [_ou(rng, n_frames, (n_chains, 3), tau1 / p**2, 3.0 / p) for p in range(1, p_max + 1)],
        axis=2,
    )  # (frames, chains, p, 3)
    extra = rng.normal(0, 0.05, (n_frames, n_chains, 4, 3))  # p = 6..9: white noise
    beads = np.arange(1, n + 1) - 0.5
    cos = np.cos(np.pi * np.arange(1, p_max + 5)[:, None] * beads[None, :] / n)  # (p, n)
    all_modes = np.concatenate([modes, extra], axis=2)
    r = x0[:, :, None, :] + 2.0 * np.einsum("pn,fcpk->fcnk", cos, all_modes)
    pos = r.reshape(n_frames, n_chains * n, 3)
    chains = [np.arange(c * n, (c + 1) * n) for c in range(n_chains)]
    got = rouse_modes(pos, chains, p_max)
    np.testing.assert_allclose(got, modes, atol=1e-9)
    lags, acf, amp, p2_amp = mode_autocorrelation(got, 1.0, 1000)
    assert acf.shape == (p_max, 1001) and np.allclose(acf[:, 0], 1.0)
    for k in range(p_max):
        rt = relaxation_time(lags, acf[k])
        assert rt["reached"] and not rt["extrapolated"]
        assert rt["t_1e"] == pytest.approx(tau1 / (k + 1) ** 2, rel=0.10)
        assert rt["tau_fit"] == pytest.approx(tau1 / (k + 1) ** 2, rel=0.10)
    np.testing.assert_allclose(amp, [3 * 9.0 / p**2 for p in range(1, 6)], rtol=0.1)
    np.testing.assert_allclose(p2_amp / p2_amp[0], 1.0, atol=0.1)


def test_relaxation_time_on_exact_exponential():
    t = np.arange(0, 1000) * 0.1
    c = np.exp(-t / 20.0)
    rt = relaxation_time(t, c)
    assert rt["reached"] and not rt["extrapolated"]
    assert rt["t_1e"] == pytest.approx(20.0, rel=1e-3)
    assert rt["tau_fit"] == pytest.approx(20.0, rel=1e-9)
    assert rt["fit_t"][0] == pytest.approx(-20 * np.log(0.9), abs=0.1)
    assert rt["fit_t"][1] == pytest.approx(-20 * np.log(0.2), abs=0.1)
    # crossing beyond the lag window (lags to half tau): not reached, fit extrapolates
    short = t <= 10.0
    rt = relaxation_time(t[short], c[short])
    assert not rt["reached"] and rt["t_1e"] is None and rt["extrapolated"]
    assert rt["tau_fit"] == pytest.approx(20.0, rel=1e-9)
    assert rt["acf_at_max"] == pytest.approx(np.exp(-0.5)) and rt["lag_max"] == 10.0
    # noise back above 0.2 after the first drop below it is not fitted
    noisy = c.copy()
    noisy[t > 50] = 0.5
    assert relaxation_time(t, noisy)["tau_fit"] == pytest.approx(20.0, rel=1e-9)
    # no decay at all: no fit
    flat = relaxation_time(t[:5], np.ones(5))
    assert flat["tau_fit"] is None and not flat["reached"]


def _straight_chains(nx, length, spacing, step):
    """nx * nx parallel straight chains along z on a square lattice."""
    xy = np.stack(np.meshgrid(np.arange(nx), np.arange(nx), indexing="ij"), -1).reshape(-1, 2)
    xy = xy * spacing
    z = np.arange(length) * step
    pos = np.concatenate(
        [np.column_stack([np.full(length, a), np.full(length, b), z]) for a, b in xy]
    )
    chains = [np.arange(k * length, (k + 1) * length) for k in range(len(xy))]
    return pos, chains


def test_crystallinity_monitor_aligned_vs_random():
    par = crystal_parameters(CG_MAN)
    assert par["r_c_A"] == pytest.approx(1.4 * 4.506) and par["l_proj_A"] == pytest.approx(3.64)
    assert crystal_parameters({"polymer": "pe", "resolution": "ua"})["r_c_A"] == 6.5
    assert crystal_parameters({"polymer": "ipp", "resolution": "aa"})["half_span"] == 3
    nx, length, spacing, step = 9, 20, 4.8, 3.6
    pos, chains = _straight_chains(nx, length, spacing, step)
    box = np.array([nx * spacing, nx * spacing, length * step, 90.0, 90.0, 90.0])
    tr = {"bb": np.stack([pos, pos]), "box": np.stack([box, box])}
    aligned = crystallinity_monitor(tr, chains, CG_MAN)
    assert aligned["available"] and aligned["frames"] == 2
    assert aligned["fraction"]["mean"] > 0.95 and aligned["largest_cluster"]["max"] > 1000
    assert aligned["label"] == "uncalibrated, melt baseline" and aligned["threshold"] == 0.4
    # random walks with the same bond length in the same box: amorphous
    rng = np.random.default_rng(4)
    steps = rng.normal(size=(len(chains), length, 3))
    steps *= step / np.linalg.norm(steps, axis=2, keepdims=True)
    start = rng.uniform(0, box[:3], (len(chains), 1, 3))
    walk = (start + np.cumsum(steps, axis=1)).reshape(-1, 3)
    rnd = crystallinity_monitor({"bb": walk[None], "box": box[None]}, chains, CG_MAN)
    assert rnd["fraction"]["mean"] < 0.3 and abs(rnd["p2_mean"]) < 0.15


# ---- `sepsim analyze hold` end to end on a fake extend run ----

EXT_DECK = """# sepsim 0.1.0 deck: extend
# system pe_cg_amorph_n40_c240_s1 (cg), seed 1
read_data ../prep/hold.data nocoeff
timestep 10
thermo_style custom step time temp press enthalpy vol density cpu

# ---- Stage 1: NPT hold extension 1 ps at 500 K, 1 atm (D47) -> hold_ext.dcd
fix md all npt temp 500 500 1000 iso 1 1 10000
dump hold_ext all dcd 10 hold_ext.dcd
dump_modify hold_ext unwrap yes
run 50
write_data hold_ext_0ns.data pair ij
run 50
undump hold_ext
unfix md
"""


def _log(rng, runs):
    head = "   Step   Time   Temp   Press   Enthalpy   Volume   Density   CPU\n"
    out, step = "", 0
    for n in runs:
        out += head
        for s in range(step, step + n + 1):
            v = 2.9e5 + rng.normal(0, 1000.0)
            out += f" {s} {s * 10.0} 500 1 {-3000 + rng.normal(0, 50)} {v} 0.77 {s * 0.01}\n"
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
def fake_extend(tmp_path_factory):
    from sepsim.build.datafile import read_data_file

    root = tmp_path_factory.mktemp("runs") / "pe_cg_amorph_n40_c240_s1"
    run, prep = root / "extend", root / "prep"
    run.mkdir(parents=True)
    prep.mkdir()
    (run / "in.extend").write_text(EXT_DECK)
    rng = np.random.default_rng(2)
    (run / "log.lammps").write_text(_log(rng, [50, 50]))
    (run / "run_manifest.json").write_text(json.dumps({"status": "finished", "hostname": "n"}))
    x0 = read_data_file(CG / "data.lmp").unwrapped()
    walk = (x0 + np.cumsum(rng.normal(0, 0.3, size=(21,) + x0.shape), axis=0)).astype(np.float32)
    _write_dcd(prep / "hold.dcd", walk[:11])
    _write_dcd(run / "hold_ext.dcd", walk[10:])  # starts with the prep's last frame
    return run


def test_cli_analyze_hold_end_to_end(fake_extend, tmp_path, capsys):
    out = tmp_path / "out"
    args = ["analyze", "hold", str(fake_extend), "--out", str(out), "--systems", str(CG.parent)]
    assert main(args) == 0, capsys.readouterr().err
    assert capsys.readouterr().out.strip() == str(out / "results.md")
    r = json.loads((out / "results.json").read_text())
    assert r["protocol"] == "extend" and r["complete"] and r["t_c"] == pytest.approx(226.85)
    assert r["stats"]["rows"] == 101 and r["kappa"]["kappa_T_GPa"] > 0
    t = r["traj"]
    assert t["available"] and t["frames"] == 21  # 11 prep + 10 (repeated frame dropped)
    assert [p["frames"] for p in t["parts"]] == [11, 10]
    assert t["boundaries_ps"] == [pytest.approx(1.05)]
    assert r["combined_with"][0].endswith("prep/hold.dcd")
    rx = t["relaxation"]
    assert rx["lag_max_ps"] == pytest.approx(1.0) and len(rx["rouse"]) == 5
    assert t["crystallinity"]["available"] and not t["com_msd"]["diffusive"]
    md = (out / "results.md").read_text()
    assert "# Hold analysis" in md and "## Chain relaxation (holds; D56)" in md
    assert "read ahead of the hold DCD" in md and "4.07" in md
    for p in ("msd", "p2_acf", "relaxation"):
        assert (out / f"{p}.png").stat().st_size > 1000
    assert not (fake_extend / "results.md").exists()


def test_analyze_hold_extension_alone_and_rejects_sweep(fake_extend, tmp_path, capsys):
    from sepsim.analyze_hold import analyze_hold

    alone = tmp_path / "x" / "extend"
    alone.mkdir(parents=True)
    for f in ("in.extend", "log.lammps", "hold_ext.dcd"):
        (alone / f).write_bytes((fake_extend / f).read_bytes())
    r, _ = analyze_hold(alone, out=tmp_path / "o", systems=CG.parent, plots=False)
    assert r["traj"]["frames"] == 11 and not r["combined_with"]
    assert any("extension alone" in n for n in r["notes"])
    sweep = tmp_path / "y" / "sweep"
    sweep.mkdir(parents=True)
    (sweep / "in.sweep").write_text("# sepsim deck: sweep\n")
    assert main(["analyze", "hold", str(sweep), "--out", str(tmp_path / "o2")]) == 1
    assert "not an isothermal hold" in capsys.readouterr().err
