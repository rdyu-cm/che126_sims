"""Cavitation test (D58): deck, stage naming, sigma_h curve, voids, analysis CLI."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from sepsim import progress as pg
from sepsim.analysis import cavitation as C
from sepsim.analysis.tensile import ATM_MPA
from sepsim.analyze_cavitation import analyze_cavitation, render_markdown
from sepsim.cli import main
from sepsim.lammps.render import RenderError, data_temperature_warning, default_stage, render_deck

REPO = Path(__file__).resolve().parents[1]
CG = REPO / "systems" / "pe_cg_amorph_n40_c240_s1"


def commands(deck):
    out = []
    for raw in deck.splitlines():
        tokens = raw.split("#", 1)[0].split()
        if tokens:
            out.append(tokens)
    return out


def _deck(tmp_path, name, **kw):
    run = tmp_path / "runs" / CG.name / name
    run.mkdir(parents=True)
    deck = run / "in.cavitation"
    data = run / "../sweep/hold_25C.data"
    deck.write_text(
        render_deck("cavitation", CG, data=data, deck_dir=run, require_data=False, **kw)
    )
    return run, deck


# --------------------------------------------------------------------------- deck


def test_cavitation_deck_round_trip(tmp_path):
    _, deck = _deck(tmp_path, "cavitation_25C")
    text = deck.read_text()
    cmds = commands(text)
    assert ["read_data", "../sweep/hold_25C.data", "nocoeff"] in cmds
    assert ["boundary", "p", "p", "p"] in cmds
    assert ["fix", "md", "all", "nvt", "temp", "298.15", "298.15", "1000"] in cmds
    assert not any(c[0] == "fix" and "npt" in c for c in cmds)
    deform = [c for c in cmds if c[:2] == ["fix", "pull"]]
    assert deform == [
        [
            "fix",
            "pull",
            "all",
            "deform",
            "1",
            "x",
            "erate",
            "1e-07",
            "y",
            "erate",
            "1e-07",
            "z",
            "erate",
            "1e-07",
            "remap",
            "x",
        ]
    ]
    # 0.26 / (1e8 /s * 10 fs) = 260,000 steps
    assert [c[1] for c in cmds if c[0] == "run"] == ["260000"]
    ave = next(c for c in cmds if c[:2] == ["fix", "cave"])
    assert ave[3:7] == ["ave/time", "1", "100", "100"] and ave[-2:] == ["file", "cavitation.txt"]
    assert ave[7:10] == ["v_cav_e", "v_cav_ev", "c_thermo_press"]
    assert ["variable", "cav_ev", "equal", "vol/v_cav_v0-1"] in cmds
    assert ["dump", "cav", "all", "dcd", "1000", "cavitation.dcd"] in cmds
    assert ["write_data", "cavitated.data", "pair", "ij"] in cmds
    segs = pg.parse_deck(deck)
    assert [s.name for s in segs] == ["Segment 1: triaxial tension at 25 C, 1e8 /s per axis"]
    assert segs[0].steps == 260_000 and segs[0].ensemble == "nvt"
    assert segs[0].dcd == ["cavitation.dcd"] and segs[0].sweep_index is None


def test_cavitation_modes_smoke_and_names():
    uni = commands(
        render_deck(
            "cavitation", CG, data=CG / "data.lmp", overrides={"cav_mode": "uniaxial_fixed"}
        )
    )
    pull = next(c for c in uni if c[:2] == ["fix", "pull"])
    assert pull[4:] == ["1", "z", "erate", "1e-07", "remap", "x"]
    assert ["variable", "cav_l0", "equal", "$(lz)"] in uni
    smoke = commands(render_deck("cavitation", CG, data=CG / "data.lmp", preset="smoke"))
    assert [c[1] for c in smoke if c[0] == "run"] == ["100"]  # 0.01 at 1e10 /s
    for bad, match in (({"cav_mode": "biaxial"}, "cav_mode"), ({"rate_per_s": 0}, "> 0")):
        with pytest.raises(RenderError, match=match):
            render_deck("cavitation", CG, data=CG / "data.lmp", overrides=bad)
    assert default_stage("cavitation", "cg") == "cavitation_25C"
    assert default_stage("cavitation", "cg", {"t_c": "90", "rate_per_s": "1e9"}) == (
        "cavitation_90C_r1e9"
    )
    assert default_stage("cavitation", "cg", {"t_c": "160", "tag": "rep2"}) == (
        "cavitation_160C_rep2"
    )
    assert "160 C sweep hold" in data_temperature_warning("cavitation", "hold_160C.data", 25.0)
    with pytest.raises(RenderError, match="--data"):
        render_deck("cavitation", CG, deck_dir=Path("results/runs/x/cavitation_25C"))


# --------------------------------------------------------------------------- curve


def _cav_file(path, sigma_of_ev, rate=1e8, rows=1300, avg_ps=1.0, p_ref=1.0):
    """Synthetic cavitation.txt: triaxial eV(t) at ``rate`` per axis, P from sigma_h(eV)."""
    t = avg_ps * np.arange(1, rows + 1)
    e = rate * t * 1e-12
    ev = (1 + e) ** 3 - 1
    press = p_ref - sigma_of_ev(ev) / ATM_MPA
    lines = [
        "# Time-averaged data for fix cave",
        (
            "# TimeStep v_cav_e v_cav_ev c_thermo_press c_thermo_press[1] c_thermo_press[2]"
            " c_thermo_press[3] v_cav_lx v_cav_ly v_cav_lz c_thermo_temp c_thermo_pe"
        ),
    ]
    for k in range(rows):
        lines.append(
            f"{round(100 * t[k])} {e[k]:.10g} {ev[k]:.10g} {press[k]:.10g} {press[k]:.10g}"
            f" {press[k]:.10g} {press[k]:.10g} 70 70 70 298 -1000"
        )
    path.write_text("\n".join(lines) + "\n")


def _sigma(ev):
    return np.where(ev <= 0.1, 600.0 * ev, 5.0)


def test_curve_recovers_cavitation_stress(tmp_path):
    from sepsim.analysis.tensile import read_ave_time

    _cav_file(tmp_path / "cavitation.txt", _sigma)
    data = read_ave_time(tmp_path / "cavitation.txt", required=C.COLUMNS)
    assert {"e", "ev", "press", "pxx", "lx", "temp", "pe"} <= set(data)
    sigma = C.hydrostatic_stress(data["press"])
    c = C.analyze_curve(data["step"] * 10 / 1000.0, data["ev"], sigma)
    assert c["sigma_cav_MPa"] == pytest.approx(60.0, rel=0.02)
    assert c["ev_cav"] == pytest.approx(0.1, abs=0.003)
    assert c["plateau_MPa"] == pytest.approx(5.0, rel=1e-6)
    assert c["K_app_MPa"] == pytest.approx(600.0, rel=1e-6)
    assert c["drop_MPa"] == pytest.approx(c["sigma_cav_MPa"] - 5.0, rel=1e-6)
    assert not c["cav_at_end"]
    short = C.analyze_curve(np.arange(50.0), np.linspace(0, 0.05, 50), np.linspace(0, 30, 50))
    assert short["plateau_MPa"] is None and short["cav_at_end"]


# --------------------------------------------------------------------------- voids


def _lattice(a=2.0, n=32, seed=0):
    g = np.arange(n) * a + 0.5
    p = np.stack(np.meshgrid(g, g, g, indexing="ij"), axis=-1).reshape(-1, 3)
    return p + np.random.default_rng(seed).normal(0.0, 0.3, p.shape), np.full(3, n * a)


def _carve(p, lengths, centre, r):
    d = p - centre
    d -= lengths * np.round(d / lengths)
    return p[np.linalg.norm(d, axis=1) >= r]


def test_void_of_a_carved_sphere():
    p, lengths = _lattice()
    base = C.void_stats(p, lengths)
    assert base["phi_v"] == 0.0 and base["largest_A3"] == 0.0 and base["n_voids"] == 0
    want = 4.0 / 3.0 * math.pi * 10.0**3
    for centre in (lengths / 2 + 0.3, np.array([0.7, 32.0, 63.0]), np.array([0.2, 0.4, 63.0])):
        s = C.void_stats(_carve(p, lengths, centre, 10.0), lengths)
        # the sphere straddling one or three periodic faces is one void
        assert s["n_voids"] == 1
        assert s["phi_v"] == pytest.approx(want / np.prod(lengths), rel=0.10)
        assert s["r_void_A"] == pytest.approx(10.0, abs=1.0)


def test_periodic_label_merges_across_faces():
    m = np.zeros((10, 10, 10), bool)
    m[0, 4:6, 4:6] = m[9, 4:6, 4:6] = True  # one slab cut by the x face
    m[4:6, 4:6, 4:6] = True  # a separate void
    labels, n = C.periodic_label(m)
    assert n == 2 and labels[0, 4, 4] == labels[9, 4, 4] != labels[5, 5, 5]
    assert C.first_void([0.0, 0.1, 0.2], [0.0, 0.001, 0.0], [0.0, 5000.0, 0.0]) == 0.1
    assert C.first_void([0.0, 0.1], [0.0, 0.006], [0.0, 0.0]) == 0.1
    assert C.first_void([0.0, 0.1], [0.0, 0.001], [0.0, 1000.0]) is None


# --------------------------------------------------------------------------- report / CLI


def _write_dcd(path, frames, lengths):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(len(frames[0]), trajectory=True)
    with DCDWriter(str(path), len(frames[0])) as w:
        for pos, ln in zip(frames, lengths, strict=True):
            u.atoms.positions = pos
            u.dimensions = [*ln, 90.0, 90.0, 90.0]
            w.write(u.atoms)


def test_analyze_cavitation_report_and_cli(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)  # the default output directory is relative to the cwd
    run, _ = _deck(tmp_path, "cavitation_25C")
    _cav_file(run / "cavitation.txt", _sigma)
    report, out = analyze_cavitation([run])
    assert out == Path("results/analysis") / CG.name / "cavitation_25C"
    r = report["runs"][0]
    assert r["summary"]["sigma_cav_MPa"] == pytest.approx(60.0, rel=0.02)
    assert r["voids"] is None and any("void analysis skipped" in n for n in r["notes"])
    assert r["inv_kappa_MPa"] is None  # no sweep results.json here
    md = render_markdown(report)
    assert "Caveats" in md and "probe" in md and "| σ_cav (MPa) |" in md
    assert (out / "sigma_vs_strain.png").is_file() and (out / "cavitation_vs_T.png").is_file()
    # a replica (tag) with voids opening in its DCD, and 1/κ_T from a sweep analysis
    run2, _ = _deck(tmp_path, "cavitation_25C_rep2", overrides={"tag": "rep2"})
    _cav_file(run2 / "cavitation.txt", lambda ev: np.where(ev <= 0.12, 500.0 * ev, 4.0))
    p, lengths = _lattice()
    frames = [p, p * 1.01, _carve(p, lengths, lengths / 2, 12.0)]
    frames[2] = np.vstack([frames[2], np.repeat(frames[2][:1], len(p) - len(frames[2]), 0)])
    _write_dcd(run2 / "cavitation.dcd", frames, [lengths, lengths * 1.01, lengths * 1.02])
    sweep = tmp_path / "results/analysis" / CG.name / "sweep"
    sweep.mkdir(parents=True)
    hold = {"t_c": 25.0, "kappa": {"kappa_T_GPa": 0.8}}
    (sweep / "results.json").write_text(json.dumps({"holds": [hold]}))
    assert main(["analyze", "cavitation", str(run), str(run2), "--probe-a", "4"]) == 0
    cmp_dir = tmp_path / "results/analysis" / CG.name / "cavitation_compare"
    js = json.loads((cmp_dir / "results.json").read_text())
    v = js["runs"][1]["voids"]
    assert v["frames"] == 3 and v["ev"][1] == pytest.approx(1.01**3 - 1, rel=1e-4)
    assert v["ev_first_void"] == pytest.approx(1.02**3 - 1, rel=1e-4)
    assert js["runs"][0]["inv_kappa_MPa"] == pytest.approx(1250.0)
    (pooled,) = js["pooled"]
    assert pooled["runs"] == ["cavitation_25C", "cavitation_25C_rep2"]
    assert pooled["summary"]["sigma_cav_MPa"]["n"] == 2
    md = (cmp_dir / "results.md").read_text()
    assert "Pooled over runs" in md and "1/κ_T (sweep) 1250" in md
    assert (cmp_dir / "void_fraction.png").is_file()
    assert main(["analyze", "cavitation", str(tmp_path)]) == 1
    assert "no in.cavitation" in capsys.readouterr().err
