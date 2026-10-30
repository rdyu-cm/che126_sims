"""Cylindrical hole (D52): builder, deck, occupancy-map analysis."""

from __future__ import annotations

import re

import numpy as np
import pytest
import yaml
from _build_helpers import SYN_BULK, tiny_pores

from sepsim.analysis import hole as H
from sepsim.analysis.units import AVOGADRO
from sepsim.build.amorphous import DATA_NAME, MANIFEST_NAME
from sepsim.build.datafile import read_data_file
from sepsim.build.hole import HoleError, build_hole, hole_id
from sepsim.build.pore import lateral_lengths
from sepsim.lammps.render import RenderError, hole_plan, render_deck, resolve_params
from sepsim.progress import parse_deck

# --------------------------------------------------------------------------- synthetic films

L = np.array([130.0, 130.0, 200.0])
_A = 4.5  # lattice spacing: ~0.011 beads/A^3, the CG PE melt


def _lattice(seed=0):
    rng = np.random.default_rng(seed)
    g = np.arange(0.0, 130.0, _A)
    gz = np.arange(50.0, 150.0, _A)
    x, y, z = np.meshgrid(g, g, gz, indexing="ij")
    p = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    return p + rng.normal(0.0, 0.8, p.shape)


P = _lattice()


def _film(radius, centre=(65.0, 65.0), tilt=0.0, taper=0.0, pinch=None):
    """Beads of the lattice film outside a cylindrical void (optionally tilted along x,
    tapered: R(z) = radius + taper (z - 100), or plugged within |z - 100| < pinch)."""
    dz = P[:, 2] - 100.0
    dx = P[:, 0] - centre[0] - tilt * dz
    dy = P[:, 1] - centre[1]
    dx -= L[0] * np.round(dx / L[0])
    dy -= L[1] * np.round(dy / L[1])
    keep = np.hypot(dx, dy) >= radius + taper * dz
    if pinch is not None:
        keep |= np.abs(dz) < pinch
    return P[keep]


@pytest.mark.parametrize("radius", [10.0, 20.0, 30.0, 40.0])
def test_cylindrical_void_radius_within_one_bin(radius):
    f = H.analyse_frame(_film(radius), L, (65.0, 65.0), radius, 0.0)
    assert f.found
    assert f.r_eff == pytest.approx(radius, abs=H.BIN_A)
    assert np.all(np.abs(f.slab_r - radius) < 2 * H.BIN_A)
    assert f.thickness == pytest.approx(100.0, abs=5.0)
    assert np.hypot(*(f.centre - 65.0)) < H.BIN_A


def test_no_void_is_closed():
    f = H.analyse_frame(_film(0.0), L, (65.0, 65.0), 4.0, 0.0)
    assert not f.found and f.r_eff == 0.0 and f.r_min == 0.0


def test_tapered_void_r_min_below_r_eff():
    # R(z) from 15 A (bottom) to 35 A (top): the narrowest slab is below the projected radius
    f = H.analyse_frame(_film(25.0, taper=0.2), L, (65.0, 65.0), 25.0, 0.0)
    assert f.r_min < f.r_eff - 5.0
    assert f.r_min == pytest.approx(16.0, abs=4.0)


def test_tilted_void_slabs_see_the_full_radius():
    # tilted 0.3 (30 A across the film): each slab still sees R; the projection at 50%
    # keeps the bins void in more than half the slabs, so R_eff stays close to R as well
    f = H.analyse_frame(_film(30.0, tilt=0.3), L, (65.0, 65.0), 30.0, 0.0)
    assert np.all(np.abs(f.slab_r - 30.0) < 2 * H.BIN_A)
    assert f.r_eff <= 30.0 + H.BIN_A


def test_pinched_void_detected():
    f = H.analyse_frame(_film(30.0, pinch=15.0), L, (65.0, 65.0), 30.0, 0.0)
    assert f.r_eff > 20.0  # projection still shows a hole
    assert f.r_min < H.CLOSED_R_A  # the plug mid-thickness closes it
    mid = np.abs(f.slab_z) < 10.0
    assert np.all(f.slab_r[mid] < H.CLOSED_R_A)
    assert np.all(f.slab_r[np.abs(f.slab_z) > 25.0] > 25.0)


def test_hole_across_the_periodic_edge():
    film = _film(25.0, centre=(2.0, 128.0))
    f = H.analyse_frame(film, L, (126.0, 4.0), 25.0, 0.0)
    assert f.r_eff == pytest.approx(25.0, abs=H.BIN_A)
    c = np.mod(f.centre, 130.0)
    assert c == pytest.approx([2.0, 128.0], abs=H.BIN_A)
    # tracked again from its own centre: stable
    g = H.analyse_frame(film, L, f.centre, f.r_eff, 0.0)
    assert g.r_eff == pytest.approx(f.r_eff, abs=0.5)


def test_closure_detection_on_a_shrinking_series():
    times, r_min = [], []
    centre, r_ref = np.array([65.0, 65.0]), 30.0
    for k, radius in enumerate([30, 25, 20, 15, 12, 9, 0, 0, 0, 0, 0, 0, 0]):
        f = H.analyse_frame(_film(float(radius)), L, centre, max(r_ref, 4.0), 0.0)
        centre, r_ref = f.centre, f.r_eff
        times.append(0.05 * k)
        r_min.append(f.r_min)
    assert H.closure_time(times, r_min) == pytest.approx(0.30)
    assert H.closure_time(times[:9], r_min[:9]) is None  # 3 closed frames only
    assert H.closure_time([0, 1, 2], [5.0, 1.0, 1.0], n=2) == 1.0


def test_linear_rate():
    t = np.linspace(0, 5, 11)
    fit = H.linear_rate(t, 30.0 - 2.0 * t)
    assert fit["slope"] == pytest.approx(-2.0) and fit["slope_se"] == pytest.approx(0.0, abs=1e-9)
    assert H.linear_rate([0.0, 1.0], [1.0, 2.0]) is None


# --------------------------------------------------------------------------- builder


def _scaled_snapshot(narrow_dir, t_c, out_path, factor=None):
    """The narrow pore's data file with x, y scaled about the box centre to the D48 L(T)
    (standing in for pore/hold_<T>C.data)."""
    man = yaml.safe_load((narrow_dir / MANIFEST_NAME).read_text())
    df = read_data_file(narrow_dir / DATA_NAME)
    l_t = lateral_lengths(man["pore"]["lateral"], "heating", t_c + 273.15)
    lines = (narrow_dir / DATA_NAME).read_text().splitlines()
    out, section = [], None
    centre = [0.5 * (lo + hi) for lo, hi in df.box[:2]]
    f = [l_t[k] / (df.box[k][1] - df.box[k][0]) for k in (0, 1)] if factor is None else factor
    for line in lines:
        m = re.match(r"^\s*(\S+) (\S+) ([xy])lo [xy]hi$", line)
        if m:
            k = "xy".index(m.group(3))
            half = 0.5 * (df.box[k][1] - df.box[k][0]) * f[k]
            line = f"{centre[k] - half:.10f} {centre[k] + half:.10f} {'xy'[k]}lo {'xy'[k]}hi"
        elif line and not line[0].isdigit() and line[0] != "-":
            section = line.split()[0] if line.strip() else section
        elif section == "Atoms" and line.strip():
            t = line.split()
            for k in (0, 1):
                t[4 + k] = f"{centre[k] + (float(t[4 + k]) - centre[k]) * f[k]:.10f}"
            line = " ".join(t)
        out.append(line)
    text = "\n".join(out) + "\n"
    if "Velocities" not in text:  # as LAMMPS write_data, so the builder must carry them over
        v = np.random.default_rng(1).normal(0.0, 0.003, (df.counts["atoms"], 3))
        rows = "\n".join(f"{i + 1} {a:.10g} {b:.10g} {c:.10g}" for i, (a, b, c) in enumerate(v))
        head, tail = text.split("\nBonds\n")
        text = f"{head}\nVelocities\n\n{rows}\n\nBonds\n{tail}"
    out_path.write_text(text)
    return out_path


@pytest.fixture(scope="module")
def narrow(tmp_path_factory):
    root = tmp_path_factory.mktemp("hole")
    _, _, nar = tiny_pores("pe", "cg", 12, 24, root, width_nm=3.0, bulk_table=SYN_BULK)
    snap = _scaled_snapshot(nar, 160.0, root / "hold_160C.data")
    return root, nar, snap


def test_hole_id():
    assert (
        hole_id("pe_cg_pore_w5nm_n320_c240_s1_rep222", 3, 160)
        == "pe_cg_hole_r3nm_160C_n320_c240_s1_rep222"
    )
    assert hole_id("pe_cg_pore_w5nm_n40_c240_s1", 2.5, 25) == "pe_cg_hole_r2p5nm_25C_n40_c240_s1"
    with pytest.raises(HoleError):
        hole_id("pe_cg_amorph_n40_c240_s1", 3, 160)


def test_build_hole_box_mass_and_manifest(narrow, tmp_path):
    _, nar, snap = narrow
    out = build_hole(snap, nar, 0.5, 160.0, gap_nm=2.0, out=tmp_path)
    assert out.name == "pe_cg_hole_r0p5nm_160C_n12_c24_s3"
    src, df = read_data_file(snap), read_data_file(out / DATA_NAME)
    m = yaml.safe_load((out / MANIFEST_NAME).read_text())
    h = m["hole"]
    lx, ly = (df.box[k][1] - df.box[k][0] for k in (0, 1))
    assert np.array(df.box[:2]) == pytest.approx(np.array(src.box[:2]), abs=1e-8)
    mass = m["total_mass_g_mol"]
    masses = {int(r[0]): float(r[1]) for r in df.sections["Masses"]}
    assert sum(masses[int(t)] for t in df.sorted_atoms()[:, 2]) == pytest.approx(mass)
    assert df.counts == src.counts
    t_t = mass / AVOGADRO / (0.312 * lx * ly * 1e-24)  # rho_bulk(160 C) of SYN_BULK
    lz = df.box[2][1] - df.box[2][0]
    assert lz == pytest.approx(t_t * (1 + np.pi * 25.0 / (lx * ly)) + 20.0, abs=1e-6)
    assert h["lz_new"] == pytest.approx(lz)
    assert h["film_thickness_angstrom"] == pytest.approx(t_t)
    assert h["radius_nm"] == 0.5 and h["t_c"] == 160.0 and h["gap_angstrom"] == 20.0
    assert h["axis_angstrom"] == pytest.approx([0.5 * sum(df.box[0]), 0.5 * sum(df.box[1])])
    assert h["area"] == pytest.approx(lx * ly)
    assert h["source"]["id"] == nar.name and len(h["source"]["data_sha256"]) == 64
    assert m["pore"]["kind"] == "narrow"  # kept for provenance
    atoms = df.sorted_atoms()
    z = atoms[:, 6]
    assert z.min() >= df.box[2][0] and z.max() < df.box[2][1] and np.all(atoms[:, 9] == 0)
    # velocities and ids kept
    vel = sorted(src.sections["Velocities"], key=lambda r: int(r[0]))
    assert sorted(df.sections["Velocities"], key=lambda r: int(r[0])) == vel
    assert np.array_equal(df.topology("Bonds"), src.topology("Bonds"))


def test_build_hole_failures(narrow, tmp_path):
    root, nar, snap = narrow
    with pytest.raises(HoleError, match="beyond the new box"):
        build_hole(snap, nar, 0.5, 160.0, gap_nm=0.01, out=tmp_path)
    with pytest.raises(HoleError, match="160 C snapshot"):
        build_hole(snap, nar, 0.5, 90.0, out=tmp_path)
    with pytest.raises(HoleError, match="lateral rule"):  # 500 K box, not L(160 C)
        bad = _scaled_snapshot(nar, 160.0, root / "hold_160C_raw.data", factor=[1.0, 1.0])
        build_hole(bad, nar, 0.5, 160.0, out=tmp_path)
    with pytest.raises(HoleError, match="does not fit"):
        build_hole(snap, nar, 2.0, 160.0, out=tmp_path)
    with pytest.raises(HoleError, match="not a narrow pore"):
        wide = next(p for p in root.iterdir() if "_pore500k_" in p.name)
        build_hole(snap, wide, 0.5, 160.0, out=tmp_path)
    other = root / "snap.data"
    other.write_text(snap.read_text())
    with pytest.warns(UserWarning, match="no hold_<T>C"):
        build_hole(other, nar, 0.5, 160.0, out=tmp_path)


# --------------------------------------------------------------------------- deck


@pytest.fixture(scope="module")
def hole_sys(narrow, tmp_path_factory):
    _, nar, snap = narrow
    return build_hole(snap, nar, 0.5, 160.0, out=tmp_path_factory.mktemp("hsys"))


def test_free_deck_stages_and_parse(hole_sys, tmp_path):
    deck = tmp_path / "in.hole"
    text = render_deck("hole", hole_sys, preset="smoke")
    deck.write_text(text)
    assert "minimize" not in text and "npt" not in text and "pair_modify tail no" in text
    assert "pxx pyy pzz" in text
    assert "fix push all indent 0.5 cylinder z" in text and "v_r0 side out units box" in text
    assert "variable r0 equal ramp(0.0,5)" in text and "variable r0 equal 5\n" in text
    assert "spring/self" not in text and "change_box" not in text
    assert "write_data inflated.data" in text and "write_data hole_0.002ns.data" in text
    assert "dump hole all dcd 50 hole.dcd" in text
    assert "fix md all nvt temp 433.15 433.15" in text
    segs = parse_deck(deck)
    assert [s.name for s in segs] == [
        "Stage 1: inflate 2 ps NVT at 433.15 K, radial push r0 0",
        "Stage 2: hold at R 1 ps NVT at 433.15 K, push at r0 = 5 A",
        "Stage 3: hold at 160 C",
    ]
    assert [s.steps for s in segs] == [200, 100, 200]
    assert segs[2].run_steps == [100, 100] and "hole.dcd" in segs[2].dcd
    assert all(s.ensemble == "nvt" and s.t_target_k == 433.15 for s in segs)


def test_addforce_push_variant(hole_sys):
    text = render_deck("hole", hole_sys, preset="smoke", overrides={"push_style": "addforce"})
    assert (
        "fix push all addforce v_fx v_fy 0.0\n" in text and "indent" not in text.split("Stage 1")[1]
    )


def test_scaffold_ramp_release_deck(hole_sys, tmp_path):
    over = {
        "scaffold": "annulus",
        "scaffold_hold_ps": "1",
        "hole_grid_c": "160h,150,140h",
        "release_t_c": "150",
        "chunk_ps": "1",
    }
    text = render_deck("hole", hole_sys, preset="smoke", overrides=over)
    deck = tmp_path / "in.hole"
    deck.write_text(text)
    body = text.split("unfix push", 1)[1]
    assert "region scaffold cylinder z" in body and " 30 INF INF side out units box" in body
    assert body.index("group scaffold region scaffold") < body.index("Stage 3: scaffolded hold")
    assert "fix_modify scaffold energy yes" in body
    segs = parse_deck(deck)
    names = [s.name for s in segs]
    assert names[2].startswith("Stage 3: scaffolded hold")
    assert names[3:] == [
        "Stage 4: hold at 160 C",
        "Stage 5: step at 150 C",
        "Stage 6: step at 140 C",
        "Stage 7: hold at 140 C",
    ]
    assert [s.t_target_k for s in segs[3:]] == [433.15, 423.15, 413.15, 413.15]
    s5 = text.split("# ---- Stage 5")[1].split("# ---- Stage 6")[0]
    assert "scaffold released here)" in s5.splitlines()[0]
    assert s5.index("unfix scaffold") < s5.index("change_box")
    assert "fix scaffold scaffold" not in s5  # released: not re-anchored
    s6 = text.split("# ---- Stage 6")[1].split("# ---- Stage 7")[0]
    assert "scaffold released)" in s6.splitlines()[0] and "spring/self" not in s6


def test_dense_windows_at_start_and_release(hole_sys, tmp_path):
    over = {
        "scaffold": "annulus",
        "hole_grid_c": "160h,150h",
        "release_t_c": "150",
        "hole_hold_ps": "2.5",
        "dense_ps": "1.5",
    }
    text = render_deck("hole", hole_sys, preset="smoke", overrides=over)
    deck = tmp_path / "in.hole"
    deck.write_text(text)
    assert text.count("dump dense all dcd 10 ") == 2
    s1 = text.split("# ---- Stage 3")[1].split("# ---- Stage 4")[0]
    # runs: 1 ps (snapshot), 0.5 ps (dense window ends), 1 ps (snapshot at 2 ps), 0.5 ps (end)
    assert re.findall(r"^run (\d+)$", s1, re.MULTILINE) == ["100", "50", "50", "50"]
    assert s1.index("undump dense") < s1.index("write_data hole_0.002ns.data")
    assert "write_data hole_0.0015ns" not in s1
    seg = next(s for s in parse_deck(deck) if s.name == "Stage 3: hold at 160 C")
    assert seg.steps == 250 and set(seg.dcd) == {"hole.dcd", "hole_dense_s01.dcd"}
    s4 = text.split("# ---- Stage 4")[1]
    assert "hole_dense_s02.dcd" in s4 and "unfix scaffold" in s4
    off = render_deck("hole", hole_sys, preset="smoke", overrides={"dense_ps": "0"})
    assert "dense" not in off.split("Stage 3")[1]


def test_scaffold_held_through_ramp_is_reanchored(hole_sys):
    over = {"scaffold": "columns", "hole_grid_c": "160h,150h"}
    text = render_deck("hole", hole_sys, preset="smoke", overrides=over)
    assert "region scaffold union" in text
    s = text.split("step at 150 C")[1]
    assert s.index("unfix scaffold") < s.index("change_box") < s.index("fix scaffold scaffold")
    assert "scaffold held)" in s.splitlines()[0]


def test_hole_plan_errors(hole_sys):
    p = resolve_params("cg", "smoke", None, "hole")
    with pytest.raises(RenderError, match="needs a scaffold"):
        hole_plan(p | {"release_t_c": "130"}, 160.0)
    with pytest.raises(RenderError, match="not a point"):
        hole_plan(p | {"scaffold": "annulus", "release_t_c": "130"}, 160.0)
    with pytest.raises(RenderError, match="starts at"):
        hole_plan(p | {"hole_grid_c": "25h,160h"}, 160.0)
    with pytest.raises(RenderError, match="scaffold"):
        hole_plan(p | {"scaffold": "rings"}, 160.0)
    segs = hole_plan(p | {"hole_grid_c": "25h,35,45h", "scaffold": "annulus"}, 25.0)
    assert [(s["kind"], s["t_c"], s["new_t"], s["state"]) for s in segs] == [
        ("hold", 25.0, False, "held"),
        ("step", 35.0, True, "held"),
        ("step", 45.0, True, "held"),
        ("hold", 45.0, False, "held"),
    ]
    assert segs[-1]["end_ns"] == pytest.approx(0.006)


def test_hole_and_other_protocols_not_mixed(hole_sys, narrow):
    _, nar, _ = narrow
    with pytest.raises(RenderError, match="hole protocol is for hole systems"):
        render_deck("hole", nar, preset="smoke")
    with pytest.raises(RenderError, match="takes the hole protocol"):
        render_deck("pore", hole_sys, preset="smoke")


# --------------------------------------------------------------------------- analyze hole


def _opened(radius, centre=(65.0, 65.0)):
    """The lattice film with every bead pushed out by the area-preserving map
    r' = sqrt(r^2 + R^2) about ``centre`` (fixed bead count: a hole of radius R)."""
    p = P.copy()
    d = p[:, :2] - np.asarray(centre)
    d -= L[:2] * np.round(d / L[:2])
    r = np.hypot(d[:, 0], d[:, 1])
    scale = np.sqrt(r**2 + radius**2) / np.maximum(r, 1e-9)
    p[:, :2] = np.asarray(centre) + d * scale[:, None]
    return p


def _write_dcd(path, frames):
    import MDAnalysis as mda
    from MDAnalysis.coordinates.DCD import DCDWriter

    u = mda.Universe.empty(len(frames[0]), trajectory=True)
    with DCDWriter(str(path), len(frames[0])) as w:
        for pos in frames:
            u.atoms.positions = pos
            u.dimensions = [*L, 90.0, 90.0, 90.0]
            w.write(u.atoms)


def test_analyze_hole_end_to_end(hole_sys, tmp_path):
    from sepsim.analyze_hole import analyze_hole_cli

    # a 130 x 130 x 200 A system with the hole axis at (65, 65), R = 3 nm
    systems = tmp_path / "systems"
    man = yaml.safe_load((hole_sys / MANIFEST_NAME).read_text())
    sid = man["id"]
    man["box_angstrom"] = [[0.0, 130.0], [0.0, 130.0], [0.0, 200.0]]
    man["hole"] |= {"radius_nm": 3.0, "axis_angstrom": [65.0, 65.0], "ligament_angstrom": 70.0}
    man["hole"]["film_thickness_angstrom"] = 100.0
    (systems / sid).mkdir(parents=True)
    (systems / sid / MANIFEST_NAME).write_text(yaml.safe_dump(man))
    run = tmp_path / "runs" / sid / "hole_free"
    run.mkdir(parents=True)
    deck = render_deck(
        "hole", systems / sid, data=hole_sys / DATA_NAME, preset="smoke", overrides={"rho_r": "0"}
    )
    (run / "in.hole").write_text(deck)
    # smoke: inflate 2 ps + push hold 1 ps (frames every 0.5 ps: 7), production 2 ps (5 frames)
    infl = [_opened(r) for r in (0, 5, 10, 15, 20, 30, 30)]

    def radius(t_ps):  # closes linearly from 30 A at t0 to 0 at 1.2 ps
        return max(0.0, 30.0 * (1 - t_ps / 1.2))

    _write_dcd(run / "inflate.dcd", infl)
    _write_dcd(run / "hole.dcd", [_opened(radius(0.5 * k)) for k in range(9)])
    # dense window of segment 1: the first 1 ps every 0.1 ps (smoke preset)
    _write_dcd(run / "hole_dense_s01.dcd", [_opened(radius(0.1 * k)) for k in range(11)])
    out = tmp_path / "an"
    md = analyze_hole_cli(run, out=out, systems=systems)
    rep = yaml.safe_load((out / "results.json").read_text())
    assert md == out / "results.md" and "t_close" in md.read_text()
    assert {"hole_radius.png", "hole_maps.png", "thickness.png"} <= {p.name for p in out.iterdir()}
    t = [f["t_ns"] for f in rep["frames"]]
    # one row per time: inflate -3..0 ps (7), dense 0.1..1 ps (10), hole.dcd 1.5..4 ps (6)
    assert len(t) == 7 + 10 + 6 and t == sorted(t) and t[0] == pytest.approx(-0.003)
    assert t[6] == pytest.approx(0.0) and rep["frames"][6]["phase"] == "production"
    assert rep["frames"][7]["dcd"] == "hole_dense_s01.dcd" and t[7] == pytest.approx(0.0001)
    assert rep["r_after_inflation"]["mean"] == pytest.approx(30.0, abs=H.BIN_A)
    assert rep["r_t0"] == pytest.approx(30.0, abs=H.BIN_A)
    assert 0.0008 <= rep["t_close_ns"] <= 0.0012  # R_min < 3 A from ~1.1 ps
    # closing speed from the dense frames: -30 A / 1.2 ps = -2.5e4 A/ns
    assert rep["rate_initial"]["slope"] == pytest.approx(-2.5e4, rel=0.15)
    assert rep["free_shell"]["beads"] > 0 and rep["variant"] == "free"
    # comparison with itself (from the cached results.json is not used: out differs)
    md2 = analyze_hole_cli(run, compare=[run], out=tmp_path / "an2", systems=systems)
    assert "## Comparison" in md2.read_text()
    assert (tmp_path / "an2" / "compare_radius.png").is_file()


def test_tethered_mask_annulus_and_columns(hole_sys):
    from sepsim.analyze_hole import tethered_mask

    man = yaml.safe_load((hole_sys / MANIFEST_NAME).read_text())
    hole = man["hole"] | {"radius_nm": 3.0, "axis_angstrom": [65.0, 65.0]}
    box = [[0.0, 130.0], [0.0, 130.0], [0.0, 200.0]]
    p = resolve_params("cg", None, {"scaffold": "annulus"}, "hole")
    m = tethered_mask(P, L, hole, p, box)
    r = np.hypot(P[:, 0] - 65.0, P[:, 1] - 65.0)
    assert np.array_equal(m, r > 55.0)
    p = resolve_params("cg", None, {"scaffold": "columns"}, "hole")
    m = tethered_mask(P, L, hole, p, box)
    assert 0 < m.sum() < 0.1 * len(P) and r[m].min() > 55.0 - 1e-9
