"""Tests for `sepsim analyze pore` (D51): gamma units and SEM, film centring across the
periodic boundary, density profiles and Gibbs surfaces on a tanh film, the clear gap,
layer-split MSD and P2, the bulk lookup, and the command end to end on a tiny fake pore
run directory."""

import json
from pathlib import Path

import numpy as np
import pytest

from sepsim import progress as pg
from sepsim.analysis.mobility import msd_by_class, p2_by_class
from sepsim.analysis.pore import (
    GRAMS_PER_A3,
    TANH_10_90,
    clear_gap,
    density_profile,
    film_centre,
    gibbs_thickness,
    interface_10_90,
    plateau_density,
    pore_width,
    relative_z,
    surface_layer,
    symmetrize,
    tanh_fit,
)
from sepsim.analyze_pore import (
    PL_TO_MN_M,
    find_bulk_analysis,
    gamma_fit,
    gamma_series,
    pore_window_stats,
)
from sepsim.cli import main

REPO = Path(__file__).resolve().parents[1]
PORE = REPO / "systems" / "pe_cg_pore_w5nm_n40_c240_s1"


def _ar1(rng, n, sigma, phi):
    e = rng.normal(0, sigma * np.sqrt(1 - phi**2), n)
    x = np.empty(n)
    x[0] = rng.normal(0, sigma)
    for k in range(1, n):
        x[k] = phi * x[k - 1] + e[k]
    return x


def test_gamma_units_and_series():
    # 1 atm A = 101325 Pa * 1e-10 m = 1.01325e-5 N/m = 0.0101325 mN/m; metal: 1 bar A = 0.01
    assert PL_TO_MN_M["real"] == pytest.approx(0.0101325, rel=1e-12)
    assert PL_TO_MN_M["metal"] == pytest.approx(0.01, rel=1e-12)
    th = {
        k: np.array([v]) for k, v in (("Pxx", -60.0), ("Pyy", -40.0), ("Pzz", 2.0), ("Lz", 100.0))
    }
    g = gamma_series(th, PL_TO_MN_M["real"])
    assert g[0] == pytest.approx(0.5 * 100.0 * (2.0 + 50.0) * 0.0101325)


def test_gamma_mean_and_sem_on_correlated_series():
    """A correlated pressure series with known mean gamma: the mean is recovered, the SEM
    (statistical inefficiency of the instantaneous gamma) matches the replica spread, and
    only the rows after the skip are used."""
    rng = np.random.default_rng(4)
    lz, n = 114.87, 3000
    gamma0 = 0.5 * lz * 60.0 * PL_TO_MN_M["real"]  # Pzz 0, Pxx = Pyy = -60 atm
    means, sems = [], []
    for _ in range(40):
        th = {
            "Step": np.arange(n),
            "Temp": np.full(n, 298.15),
            "Pxx": -60.0 + _ar1(rng, n, 30.0, 0.7),
            "Pyy": -60.0 + _ar1(rng, n, 30.0, 0.7),
            "Pzz": _ar1(rng, n, 30.0, 0.7),
            "Lz": np.full(n, lz),
            "Lx": np.full(n, 64.0),
            "Ly": np.full(n, 64.0),
        }
        th["Pzz"][:300] += 500.0  # equilibration transient, dropped by the 10% skip
        st = pore_window_stats(th, 0.10, PL_TO_MN_M["real"])
        means.append(st["gamma"]["mean"])
        sems.append(st["gamma"]["sem"])
    assert st["rows_used"] == n - 300 and st["lx"] == {"mean": 64.0, "sem": 0.0}
    assert np.mean(means) == pytest.approx(gamma0, abs=3 * np.std(means) / np.sqrt(40))
    assert np.mean(sems) == pytest.approx(np.std(means, ddof=1), rel=0.35)


def test_gamma_fit_slope_and_birge():
    pts = [
        {"t_set_c": t, "stats": {"gamma": {"mean": 35.0 - 0.05 * (t - 25), "sem": 0.3}}}
        for t in (25.0, 50.0, 90.0, 130.0, 160.0)
    ]
    f = gamma_fit(pts)
    assert f["dgamma_dT_mN_mK"] == pytest.approx(-0.05, rel=1e-9)
    assert f["gamma_25c_mN_m"] == pytest.approx(35.0, rel=1e-9)
    assert f["err"] == pytest.approx(f["err_unscaled"])  # chi2 ~ 0: no inflation
    noisy = [
        dict(p, stats={"gamma": {"mean": p["stats"]["gamma"]["mean"] + d, "sem": 0.3}})
        for p, d in zip(pts, (2.0, -2.0, 2.0, -2.0, 2.0), strict=True)
    ]
    g = gamma_fit(noisy)
    assert g["chi2_red"] > 1 and g["err"] == pytest.approx(
        g["err_unscaled"] * np.sqrt(g["chi2_red"])
    )
    assert gamma_fit(pts[:2]) is None


def _tanh_film(lz=120.0, h=30.0, delta=3.0, rp=0.83, n_bins=480):
    edges = np.linspace(-lz / 2, lz / 2, n_bins + 1)
    z = 0.5 * (edges[1:] + edges[:-1])
    return z, 0.5 * rp * (1.0 - np.tanh((np.abs(z) - h) / delta))


def test_gibbs_surfaces_and_widths_on_tanh_film():
    lz, h, delta, rp = 120.0, 30.0, 3.0, 0.83
    z, rho = _tanh_film(lz, h, delta, rp)
    # a symmetric tanh film: equimolar surfaces exactly at +-h
    assert gibbs_thickness(z, rho, rp) == pytest.approx(2 * h, rel=1e-6)
    p, t_g = plateau_density(z, rho, margin_A=15.0)
    assert p == pytest.approx(rp, rel=1e-4) and t_g == pytest.approx(2 * h, rel=1e-4)  # tanh tail
    pw = pore_width(z, rho, Lz_A=lz, bulk_density=rp)
    assert lz - pw.width == pytest.approx(2 * h, abs=1e-3)  # 50% crossings at +-h
    w = interface_10_90(z, rho, rp)
    for side in ("upper", "lower"):
        assert w[side]["width"] == pytest.approx(TANH_10_90 * delta, rel=2e-3)
        assert w[side]["z90"] == pytest.approx(h - delta * np.arctanh(0.8), abs=1e-2)
    fit = tanh_fit(z, rho, 0.8, 28.0)
    assert fit["delta_A"] == pytest.approx(delta, rel=1e-4) and fit["h_A"] == pytest.approx(h)
    assert fit["width_10_90_A"] == pytest.approx(2 * np.arctanh(0.8) * delta, rel=1e-4)
    asym = rho * (1 + 0.1 * np.sign(z))
    np.testing.assert_allclose(symmetrize(asym), rho, rtol=1e-12)


def test_film_centre_across_the_periodic_boundary():
    """A film whose centre is 5 A from the box edge (so it straddles the boundary), given
    in random periodic images: centre and relative z are recovered."""
    rng = np.random.default_rng(1)
    lz, c = 100.0, 5.0
    z_true = rng.uniform(-30.0, 30.0, 5000)
    z = c + z_true + lz * rng.integers(-2, 3, 5000)
    m = rng.uniform(12.0, 16.0, 5000)
    centre = film_centre(z, lz, m)
    expect = c + np.average(z_true, weights=m)
    assert np.mod(centre - expect + lz / 2, lz) - lz / 2 == pytest.approx(0.0, abs=1e-6)
    zr = relative_z(z, centre, lz)
    np.testing.assert_allclose(zr, z_true - np.average(z_true, weights=m), atol=1e-6)
    # no empty bin (a box filled to the brim): falls back to the emptiest bin, no crash
    assert 0.0 <= film_centre(rng.uniform(0, lz, 20000), lz) < lz


def test_density_profile_mass_and_layers():
    rng = np.random.default_rng(2)
    lz, area = 100.0, 50.0 * 50.0
    zr = rng.uniform(-20.0, 20.0, 4000)
    m = np.full(4000, 14.0)
    z, rho = density_profile(zr, m, area, lz, 200)
    assert np.sum(rho) * (z[1] - z[0]) * area / GRAMS_PER_A3 == pytest.approx(m.sum())
    assert np.allclose(z, -z[::-1])  # bins symmetric about the film centre
    with pytest.raises(ValueError):
        density_profile(zr, m, area, lz, 201)
    lab = surface_layer(np.array([0.0, 14.9, 15.1, -16.0, 31.0, -40.0]), 30.0, 15.0)
    assert lab.tolist() == [False, False, True, True, True, True]


def test_clear_gap_minimum_image():
    lx = ly = 40.0
    lz = 100.0
    film = np.array(
        [
            [1.0, 1.0, 30.0],  # top atom
            [39.0, 2.0, -30.0],  # bottom atom: dx = -2 by minimum image, dy = 1
            [20.0, 20.0, 0.0],
            [10.0, 30.0, -29.0],
        ]
    )
    gap, closest = clear_gap(film + [0, 0, 50.0], (lx, ly, lz), 50.0)
    assert gap == pytest.approx(lz - 60.0)
    assert closest == pytest.approx(np.sqrt(2.0**2 + 1.0**2 + 40.0**2))
    # far apart in xy: the window grows until the answer is exact
    far = np.array([[0.0, 0.0, 30.0], [20.0, 20.0, -30.0], [20.0, 20.0, 0.0]])
    _, d = clear_gap(far, (lx, ly, lz), 0.0, window_A=1.0)
    assert d == pytest.approx(np.sqrt(20.0**2 * 2 + 40.0**2))


def test_msd_and_p2_by_class_at_the_origin():
    """Class 0 sites move +1 A per frame in x, class 1 +2 A in z; one site changes class
    halfway: it counts with the class it has at each origin."""
    n, lags = 10, [1, 3]
    x = np.zeros((n, 3, 3))
    x[:, 0, 0] = np.arange(n)
    x[:, 1, 2] = 2.0 * np.arange(n)
    x[:, 2, 0] = np.arange(n)
    lab = np.zeros((n, 3), int)
    lab[:, 1] = 1
    lab[5:, 2] = 1
    lab[0, 0] = -1  # excluded origin
    s, c = msd_by_class(x, lab, lags, 2)
    assert c[:, 0].tolist() == [8 + 5, 6 + 5] and c[:, 1].tolist() == [9 + 4, 7 + 2]
    np.testing.assert_allclose(s[0, 0], [13 * 1.0, 0, 0])
    np.testing.assert_allclose(s[0, 1], [4 * 1.0, 0, 9 * 4.0])
    np.testing.assert_allclose(s[1, 0, 0] / c[1, 0], 9.0)
    # max_origins thins the origins evenly
    _, c2 = msd_by_class(x, lab, [1], 2, max_origins=3)
    assert c2.sum() == 3 * 3 - 1
    # bonds: one fixed (P2 = 1), one rotating 90 degrees per frame in xy (P2 1, -0.5, 1, ...)
    pos = np.zeros((6, 4, 3))
    pos[:, 1] = [0.0, 0.0, 1.0]
    ang = np.arange(6) * np.pi / 2
    pos[:, 3, 0], pos[:, 3, 1] = np.cos(ang), np.sin(ang)
    bl = np.tile([0, 1], (6, 1))
    s, c = p2_by_class(pos, np.array([0, 2]), np.array([1, 3]), bl, [1, 2], 2)
    np.testing.assert_allclose(s / c, [[1.0, -0.5], [1.0, 1.0]], atol=1e-12)


def test_surface_excess_energy_and_film_expansion():
    """e_s = (E_pore - (M_pore/M_bulk) E_bulk)/(2A) in mJ/m^2; alpha_z from t_G(T); film
    alpha_V = alpha_z + 2 alpha_L with alpha_L from the box area."""
    from sepsim.analyze_pore import KCAL_MOL_A2_TO_MJ_M2, pore_thermal

    assert KCAL_MOL_A2_TO_MJ_M2 == pytest.approx(694.77, rel=1e-4)
    temps, area0, h0 = (25.0, 90.0, 130.0, 160.0), 4000.0, 65.0
    pts, film, energies = [], {}, {}
    for i, t in enumerate(temps):
        lx = np.sqrt(area0) * (1 + 2e-4 * (t - 25))
        e_b = -5000.0 + 30.0 * (t - 25)
        e_s = 40.0 - 0.07 * (t - 25)  # mJ/m^2
        e_p = 2 * e_b + e_s * 2 * lx * lx / KCAL_MOL_A2_TO_MJ_M2
        pts.append(
            {
                "index": i,
                "kind": "hold",
                "t_set_c": t,
                "stats": {
                    "lx": {"mean": lx, "sem": 0.0},
                    "ly": {"mean": lx, "sem": 0.0},
                    "etotal": {"mean": e_p, "sem": 1.0},
                    "gamma": {"mean": 30.0, "sem": 0.2},
                },
            }
        )
        film[i] = {
            "film_gibbs_frames": {"mean": h0 * (1 + 5e-4 * (t - 25)), "sem": 0.01},
            "plateau": {"mean": 0.8, "sem": 1e-4},
        }
        energies[round(t, 3)] = {"etotal": {"mean": e_b, "sem": 0.5}}
    bulk = {"mass_gmol": 1000.0, "segments": [], "holds": []}
    th = pore_thermal(pts, film, bulk, energies, 2000.0, {"sweep": None})
    for p, t in zip(th["points"], temps, strict=True):
        assert p["e_s_mJ_m2"]["mean"] == pytest.approx(40.0 - 0.07 * (t - 25), rel=1e-9)
    a = th["alpha"][0]
    t_k = np.array(temps)
    assert a["alpha_z_per_K"] == pytest.approx(h0 * 5e-4 / np.mean(h0 * (1 + 5e-4 * (t_k - 25))))
    assert a["alpha_L_per_K"] == pytest.approx(2e-4, rel=0.03)  # (1/2A) dA/dT at the mean A
    assert a["alpha_V_film_per_K"] == pytest.approx(a["alpha_z_per_K"] + 2 * a["alpha_L_per_K"])
    assert th["cv"][0]["cv_J_gK"] > 0


def test_find_bulk_analysis(tmp_path):
    man = {
        "pore": {"lateral": {"sources": {"sweep": {"run_dir": "/x/runs/bulk_a/sweep"}}}},
        "source": {"id": "wide", "source": {"id": "bulk_b"}},
        "replicate": {"source_id": "bulk_c"},
    }
    assert find_bulk_analysis(man, tmp_path) is None
    for sid in ("bulk_c", "bulk_b", "bulk_a"):
        p = tmp_path / sid / "sweep" / "results.json"
        p.parent.mkdir(parents=True)
        p.write_text("{}")
        assert find_bulk_analysis(man, tmp_path) == p  # lateral source, then chain, replicate


# ---- end to end on a tiny fake pore run ----

GAMMA_P = (-60.0, -60.0, 0.0)  # Pxx, Pyy, Pzz (atm)


def _deck_text(box):
    (xlo, xhi), (ylo, yhi), _ = box
    cb = f"change_box all x final {xlo} {xhi} y final {ylo} {yhi} remap units box"
    lines = [
        "# sepsim 0.1.0 deck: pore",
        "# system pe_cg_pore_w5nm_n40_c240_s1 (cg), seed 1",
        "units real",
        "timestep 10",
        "thermo_style custom step time temp press vol density lx ly lz pxx pyy pzz cpu",
        "# ---- Stage 1: minimize the narrowed slab",
        "minimize 1e-4 1e-6 100 1000",
        "# ---- Stage 2: surface re-relaxation 1 ps NVT at 500 K after narrowing",
        cb,
        "fix md all nvt temp 500 500 1000",
        "run 100",
        "unfix md",
        "# ---- Stage 3: step-cool 500 -> 298.15 K in 2 steps",
    ]
    for k, t in ((1, 400.0), (2, 298.15)):
        lines += [f"# cool step {k}/2: {t} K", cb, f"fix md all nvt temp {t} {t} 1000", "run 100"]
        lines.append("unfix md")
    for i, kind, t in ((1, "hold", 25), (2, "step", 90), (3, "hold", 160)):
        stem = f"seg{i:02d}_{kind}_{t}C"
        lines += [
            f"# ---- Segment {i}: {kind} at {t} C ({t + 273.15:.2f} K), 1 ps -> {stem}.dcd",
            cb,
            f"fix md all nvt temp {t + 273.15:.2f} {t + 273.15:.2f} 1000",
            f"dump traj all dcd 10 {stem}.dcd",
        ]
        if kind == "hold":
            for k in (1, 2):
                lines += [f"dump burst all dcd 1 {stem}_burst{k:02d}.dcd", "run 10", "undump burst"]
                lines.append("run 40")
        else:
            lines.append("run 100")
        lines += ["undump traj", "unfix md"]
    return "\n".join(lines) + "\n"


def _log_text(rng, segments, lz):
    head = (
        "   Step   Time   Temp   Press   Volume   Density   Lx   Ly   Lz   Pxx   Pyy   Pzz   CPU\n"
    )
    out, step = "", 0
    for seg in segments:
        t = seg.t_target_k or 300.0
        for n in seg.run_steps:
            out += head
            for s in range(step, step + n + 1):
                p = np.array(GAMMA_P) + rng.normal(0, 20.0, 3)
                out += (
                    f" {s} {s * 10.0} {t} 1 4e5 0.5 67.4 67.4 {lz} {p[0]} {p[1]} {p[2]}"
                    f" {s * 0.01}\n"
                )
            out += f"Loop time of 1 on 1 procs for {n} steps with 3200 atoms\n"
            step += n
    return out


def _write_dcd(path, frames, dims):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(frames.shape[1], trajectory=True)
    with DCDWriter(str(path), frames.shape[1]) as w:
        for x in frames:
            u.atoms.positions = x
            u.dimensions = [*dims, 90.0, 90.0, 90.0]
            w.write(u.atoms)


@pytest.fixture(scope="module")
def fake_pore(tmp_path_factory):
    from sepsim.build.datafile import read_data_file

    root = tmp_path_factory.mktemp("runs")
    run = root / "pe_cg_pore_w5nm_n40_c240_s1" / "pore"
    run.mkdir(parents=True)
    df = read_data_file(PORE / "data.lmp")
    dims = [hi - lo for lo, hi in df.box]
    (run / "in.pore").write_text(_deck_text(df.box))
    segments = pg.parse_deck(run / "in.pore")
    rng = np.random.default_rng(12)
    (run / "log.lammps").write_text(_log_text(rng, segments, dims[2]))
    man = {"status": "finished", "hostname": "n", "deck": {"path": "in.pore"}}
    (run / "run_manifest.json").write_text(json.dumps(man))
    x0 = df.unwrapped()

    def walk(n, step, shift=0.0):
        x = x0 + np.cumsum(rng.normal(0, step, size=(n,) + x0.shape), axis=0)
        return (x + [0.0, 0.0, shift]).astype(np.float32)

    # 25 C: the film shifted by 0.45 Lz, so it straddles the periodic boundary in z
    _write_dcd(run / "seg01_hold_25C.dcd", walk(11, 0.3, 0.45 * dims[2]), dims)
    for k in (1, 2):
        _write_dcd(run / f"seg01_hold_25C_burst{k:02d}.dcd", walk(11, 0.05, 0.45 * dims[2]), dims)
    _write_dcd(run / "seg03_hold_160C.dcd", walk(11, 0.4), dims)  # no bursts at 160 C
    _write_dcd(run / "seg02_step_90C.dcd", walk(11, 0.3), dims)
    bulk = root / "bulk.json"
    lag = [0.1, 1.0, 10.0, 50.0]
    traj = {
        "available": True,
        "curves": {"msd_lag_ps": lag, "msd_A2": [0.3, 3.0, 30.0, 90.0]},
        "p2": {"t_1e_ps": 100.0},
        "rg": {"rg_A": {"mean": 30.0, "sem": 0.1}},
        "ree": {"ree_A": {"mean": 75.0, "sem": 1.0}},
        "segment_msd": {"msd_at_max_A2": 90.0, "lag_max_ps": 50.0},
        "com_msd": {"msd_at_max_A2": 9.0},
        "c_n": {"plateau": {"mean": 10.0, "sem": 0.1}},
    }
    bulk.write_text(
        json.dumps(
            {
                "system": "bulk",
                "segments": [
                    {"t_set_c": t, "kind": "hold", "stats": {"density": {"mean": d, "sem": 1e-4}}}
                    for t, d in ((25.0, 0.8345), (160.0, 0.7594))
                ],
                "holds": [{"t_c": t, "traj": traj} for t in (25.0, 160.0)],
            }
        )
    )
    return run, bulk, dims


def test_cli_analyze_pore_end_to_end(fake_pore, tmp_path, capsys):
    run, bulk, dims = fake_pore
    out = tmp_path / "out"
    args = ["analyze", "pore", str(run), "--out", str(out), "--systems", str(PORE.parent)]
    code = main([*args, "--bulk-analysis", str(bulk)])
    assert code == 0, capsys.readouterr().err
    assert capsys.readouterr().out.strip() == str(out / "results.md")
    r = json.loads((out / "results.json").read_text())
    kinds = [s["kind"] for s in r["segments"]]
    assert kinds == ["relax", "cool", "cool", "hold", "step", "hold"]
    gamma0 = 0.5 * dims[2] * 60.0 * PL_TO_MN_M["real"]
    for s in r["segments"]:
        g = s["stats"]["gamma"]
        assert abs(g["mean"] - gamma0) < 5 * g["sem"] + 1e-9
    assert r["segments"][3]["stats"]["rows_used"] == 91  # hold: first 10% dropped
    assert r["fits"]["sweep"]["n"] == 3 and r["fits"]["cool"] is None  # 2 cool stages only
    h25, h160 = r["holds"]
    for h in (h25, h160):
        t = h["traj"]
        assert t["available"] and h["film"]["available"]
        p = t["profile"]
        mass = p["film_gibbs_A"] * p["plateau"]["mean"] * p["area_A2"] / GRAMS_PER_A3
        assert mass == pytest.approx(134737.912, rel=1e-6)  # M = rho_p A t_G
        assert p["gap_gibbs_A"] + p["film_gibbs_A"] == pytest.approx(dims[2])
        assert 0.5 < p["plateau"]["mean"] < 0.95 and p["gap_gibbs_A"] > 20.0
        assert 0 < p["closest_A"]["min"] and p["gap_z_A"]["min"] <= p["closest_A"]["min"]
        ly = t["layers"]
        assert 0.2 < ly["surface_fraction"] < 0.8
        assert ly["surface"]["msd_at"][f"{ly['lag_max_ps']:g}"]["xy"] > 0
    # the straddling 25 C film gives the same profile as the unshifted one (same x0)
    assert h25["traj"]["profile"]["film_gibbs_A"] == pytest.approx(
        h160["traj"]["profile"]["film_gibbs_A"], rel=0.02
    )
    assert h25["traj"]["layers"]["bursts_used"] == 2 and h160["traj"]["layers"]["bursts_used"] == 0
    assert h25["bulk"]["density"]["mean"] == 0.8345
    th = r["thermal"]
    assert [p["t_c"] for p in th["points"]] == [25.0, 90.0, 160.0]
    assert all(p["film_gibbs_A"]["mean"] > 40 for p in th["points"])  # step 90 C from its DCD
    a = th["alpha"][0]
    assert a["window_c"] == [25.0, 160.0] and abs(a["alpha_z_per_K"]) < 1e-4  # same film
    assert a["alpha_L_per_K"] == pytest.approx(0.0, abs=1e-12)  # Lx constant in the fake log
    assert any("surface excess energy not computed" in n for n in th["notes"])  # no TotEng
    md = (out / "results.md").read_text()
    assert "## Density profile" in md and "plain LJ cutoff" in md and "| 25 | bulk |" in md
    for p in ("gamma_vs_T", "density_profile", "gap_vs_T", "msd_layers", "p2_layers"):
        assert (out / f"{p}.png").stat().st_size > 1000
    assert (out / "p2z_profile.png").is_file()
    for p in ("equilibration", "equilibration_holds", "film_vs_time", "thermal_vs_T"):
        assert (out / f"{p}.png").stat().st_size > 1000
    assert "## Equilibration" in md and "| drift |" in md
    assert {"gamma"} <= set(r["segments"][0]["drift"])
    assert set(r["segments"][3]["convergence"]) == {"gamma"}  # no PotEng in the fake log
    se = h25["traj"]["profile"]["series"]
    assert len(se["t_ns"]) == 11 and se["window_ns"] == pytest.approx(1e-4)  # frame 1 of 11
    conv = {c["name"]: c for c in r["convergence"]}
    c25 = conv["seg 01 hold 25 C"]
    assert {"gamma", "pzz", "T", "film_gibbs_A", "plateau"} <= set(c25["quantities"])
    g = c25["quantities"]["gamma"]
    assert len(g["t_ps"]) == len(g["value"]) <= 500 and len(g["blocks"]) == 8
    assert c25["window"][0] > c25["t_start_ps"]
    assert g["g"] >= 1 and "z" in g["halves"] and isinstance(g["drift"], bool)
    assert c25["sem_vs_block"]["gamma"] and conv["Stage 3 cool 1/2 (400.0 K)"]["kind"] == "cool"
    assert h25["traj"]["profile"]["frames"] == 10
    assert not (run / "results.md").exists()


def test_cli_analyze_pore_rejects_sweep_and_sweep_points_to_pore(fake_pore, tmp_path, capsys):
    run, _, _ = fake_pore
    assert main(["analyze", "sweep", str(run), "--out", str(tmp_path / "o")]) == 1
    assert "sepsim analyze pore" in capsys.readouterr().err
    sw = tmp_path / "x" / "sweep"
    sw.mkdir(parents=True)
    (sw / "in.sweep").write_text("# sepsim deck: sweep\n")
    assert main(["analyze", "pore", str(sw), "--out", str(tmp_path / "o")]) == 1
    assert "not a pore run" in capsys.readouterr().err


def test_no_traj_default_out_and_bulk_lookup(fake_pore, tmp_path, monkeypatch):
    from sepsim.analyze_pore import analyze_pore

    run, _, _ = fake_pore
    monkeypatch.chdir(tmp_path)
    r, out_dir = analyze_pore(run, systems=PORE.parent, traj=False, plots=False)
    assert out_dir == Path("results/analysis/pe_cg_pore_w5nm_n40_c240_s1/pore")
    assert all(not h["traj"]["available"] for h in r["holds"])
    assert r["bulk_analysis"] is None and any("bulk analysis" in n for n in r["notes"])
