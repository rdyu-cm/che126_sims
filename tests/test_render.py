"""LAMMPS deck rendering: coefficients, styles, prep stages, overrides, presets, CLI."""

import hashlib
import re
from pathlib import Path

import pytest
import yaml

from sepsim.build.datafile import read_data_file
from sepsim.cli import main
from sepsim.ff.params import FORCEFIELD_DIR, load_forcefield
from sepsim.lammps.render import (
    DEFAULTS,
    PRESETS,
    PROTOCOL_DEFAULTS,
    RenderError,
    parse_overrides,
    render_deck,
    resolve_params,
    write_deck,
)

REPO = Path(__file__).resolve().parents[1]
SYSTEMS = sorted(p.parent for p in (REPO / "systems").glob("*/manifest.yaml"))
IDS = [p.name for p in SYSTEMS]
FIVE = {
    "pe_aa_amorph_n40_c240_s1",
    "pe_ua_amorph_n40_c240_s1",
    "ipp_ua_amorph_n40_c240_s1",
    "pe_cg_amorph_n40_c240_s1",
    "pe_cg_amorph_n40_c1500_s1",
}


def sysdir(sid):
    return REPO / "systems" / sid


def manifest(path):
    return yaml.safe_load((path / "manifest.yaml").read_text())


def commands(deck):
    """Deck commands as token lists (comments stripped)."""
    out = []
    for raw in deck.splitlines():
        tokens = raw.split("#", 1)[0].split()
        if tokens:
            out.append(tokens)
    return out


def first(deck, name):
    return next(c for c in commands(deck) if c[0] == name)


def same(a, b):
    """Token lists equal, numbers compared as floats."""
    if len(a) != len(b):
        return False
    for x, y in zip(a, b, strict=True):
        try:
            if float(x) != pytest.approx(float(y), rel=1e-12, abs=0):
                return False
        except ValueError:
            if x != y:
                return False
    return True


def test_all_five_committed_systems_present():
    assert FIVE <= set(IDS)


@pytest.mark.parametrize("path", SYSTEMS, ids=IDS)
def test_coeff_lines_match_committed_data_file(path):
    """Masses and every coefficient section rendered from the YAML equal the data file's."""
    deck = render_deck("prep", path)
    df = read_data_file(path / "data.lmp")
    cmds = commands(deck)
    # The full pair block appears once in setup (and again after a push-off); take the first.
    n_types = df.counts["atom types"]

    def rows(name):
        return [c[1:] for c in cmds if c[0] == name]

    masses = rows("mass")
    assert len(masses) == n_types
    assert all(same(m, r) for m, r in zip(masses, df.sections["Masses"], strict=True))

    pairs = rows("pair_coeff")
    if "PairIJ Coeffs" in df.sections:
        want = df.sections["PairIJ Coeffs"]
        got = pairs[: len(want)]
    else:
        want = df.sections["Pair Coeffs"]
        got = pairs[: len(want)]
        assert all(p[0] == p[1] for p in got)
        got = [p[1:] for p in got]
    assert len(want) > 0
    assert all(same(g, w) for g, w in zip(got, want, strict=True))

    for cmd, section in [
        ("bond_coeff", "Bond Coeffs"),
        ("angle_coeff", "Angle Coeffs"),
        ("dihedral_coeff", "Dihedral Coeffs"),
    ]:
        got, want = rows(cmd), df.sections.get(section, [])
        assert len(got) == len(want), section
        assert all(same(g, w) for g, w in zip(got, want, strict=True)), section


@pytest.mark.parametrize("path", SYSTEMS, ids=IDS)
def test_styles_special_bonds_and_cutoff_from_manifest(path):
    m = manifest(path)
    st = m["lammps_styles"]
    deck = render_deck("prep", path)
    params = resolve_params(m["resolution"])
    cmds = commands(deck)
    assert ["units", "real"] in cmds and ["atom_style", "full"] in cmds
    full_pair = [c for c in cmds if c[0] == "pair_style" and c[1] == st["pair"]]
    assert full_pair and all(float(c[2]) == params["lj_cutoff"] for c in full_pair)
    for kind in ("bond", "angle", "dihedral", "improper"):
        lines = [c for c in cmds if c[0] == f"{kind}_style"]
        assert lines == ([] if st[kind] == "none" else [[f"{kind}_style", st[kind]]])
    sb = first(deck, "special_bonds")
    want = []
    for key in ("lj", "coul"):
        if key in st["special_bonds"]:
            want += [key, *map(str, st["special_bonds"][key])]
    if st["special_bonds"].get("angle"):
        want += ["angle", "yes"]
    assert same(sb[1:], want)
    pm = [c for c in cmds if c[0] == "pair_modify"]
    if st["mixing"] == "none":
        assert all("mix" not in c for c in pm)
    else:
        assert pm and all(c[1:3] == ["mix", st["mixing"]] for c in pm)
    assert all(("tail" in c) == params["tail"] for c in pm)
    rd = first(deck, "read_data")
    assert rd[2] == "nocoeff" and Path(rd[1]) == (path / "data.lmp").resolve()
    assert ["neighbor", "2", "bin"] in cmds
    assert ["neigh_modify", "delay", "0", "every", "1", "check", "yes"] in cmds
    assert not any(c[0] in ("package", "suffix") for c in cmds)


def test_lj_cutoffs_equal_forcefield_recommendations():
    ffs = {"aa": "opls2020_aa", "ua": "trappe_ua", "cg": "sdk_cg"}
    checked = 0
    for res, name in ffs.items():
        rec = load_forcefield(FORCEFIELD_DIR / f"{name}.yaml").recommended
        if "lj_cutoff" in rec:
            assert DEFAULTS[res]["lj_cutoff"] == rec["lj_cutoff"]
            checked += 1
        if "tail_correction" in rec:
            assert DEFAULTS[res]["tail"] == rec["tail_correction"]
    assert checked == 2  # TraPPE 14, SPICA 15; OPLS ships no LJ cutoff (D25 sets 12)
    assert DEFAULTS["aa"]["lj_cutoff"] == 12.0 and DEFAULTS["aa"]["kspace_accuracy"] == 1e-5
    assert [DEFAULTS[r]["dt_fs"] for r in ("aa", "ua", "cg")] == [1.0, 2.0, 10.0]
    assert [DEFAULTS[r]["tail"] for r in ("aa", "ua", "cg")] == [True, True, False]


def test_header_lists_parameters_and_hashes():
    path = sysdir("pe_ua_amorph_n40_c240_s1")
    deck = render_deck("prep", path)
    sha = hashlib.sha256((path / "manifest.yaml").read_bytes()).hexdigest()
    assert "# system pe_ua_amorph_n40_c240_s1 (ua), seed 1" in deck
    assert f"manifest.yaml sha256 {sha}" in deck
    for key, value in resolve_params("ua").items():
        assert f"#   {key} = {value}\n" in deck
    assert deck == render_deck("prep", path)  # deterministic


def stage(deck, n):
    """Text of prep stage n (from its banner to the next banner)."""
    parts = re.split(r"^# ---- Stage (\d+):", deck, flags=re.MULTILINE)
    found = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
    return found.get(n)


def test_cg_has_no_pushoff():
    for sid in ("pe_cg_amorph_n40_c240_s1", "pe_cg_amorph_n40_c1500_s1"):
        deck = render_deck("prep", sysdir(sid))
        assert "pair_style soft" not in deck and "fix adapt" not in deck.replace("_adapt", "")
        assert stage(deck, 1) is None and stage(deck, 2) is not None
        assert "pushoff.data" not in deck
    with pytest.raises(RenderError, match="spica"):
        render_deck("prep", sysdir("pe_cg_amorph_n40_c240_s1"), overrides={"pushoff": "yes"})


def test_aa_pushoff_drops_kspace_and_restores_full_ff():
    deck = render_deck("prep", sysdir("pe_aa_amorph_n40_c240_s1"))
    push = stage(deck, 1)
    cmds = commands(push)
    names = [c[0] for c in cmds]
    assert names.index("kspace_style") < names.index("pair_style")
    assert ["kspace_style", "none"] in cmds
    assert ["pair_style", "soft", "3"] in cmds and ["pair_coeff", "*", "*", "0.0"] in cmds
    assert ["variable", "A", "equal", "ramp(0,50)"] in cmds
    assert [
        "fix",
        "pushoff_adapt",
        "all",
        "adapt",
        "1",
        "pair",
        "soft",
        "a",
        "*",
        "*",
        "v_A",
    ] in cmds
    assert ["fix", "pushoff_nve", "all", "nve/limit", "0.1"] in cmds
    assert ["fix", "pushoff_lang", "all", "langevin", "500", "500", "50", "1"] in cmds
    assert ["timestep", "0.5"] in cmds and ["run", "40000"] in cmds  # 20 ps at 0.5 fs
    # after the run: full pair style, all coefficients, PPPM, production timestep
    after = commands(push.split("unfix pushoff_adapt", 1)[1])
    assert ["pair_style", "lj/cut/coul/long", "12"] in after
    assert ["pair_modify", "mix", "geometric", "tail", "yes"] in after
    assert sum(c[0] == "pair_coeff" for c in after) == 3
    assert ["kspace_style", "pppm", "1e-05"] in after
    assert ["timestep", "1"] in after and ["write_data", "pushoff.data"] in after


def test_ua_pushoff_parameters():
    push = commands(stage(render_deck("prep", sysdir("pe_ua_amorph_n40_c240_s1")), 1))
    assert ["pair_style", "soft", "4"] in push
    assert ["timestep", "1"] in push and ["run", "20000"] in push
    assert not any(c[0] == "kspace_style" for c in push)


def test_shake_only_where_manifest_has_constrained_bonds():
    ipp = render_deck("prep", sysdir("ipp_ua_amorph_n40_c240_s1"))
    assert ["fix", "shake", "all", "shake", "0.0001", "20", "0", "b", "2"] in commands(ipp)
    # defined after the push-off fixes and the minimization, before any MD with it
    assert ipp.index("fix shake") > ipp.index("minimize") > ipp.index("unfix pushoff_lang")
    assert ipp.index("fix shake") < ipp.index("fix md")
    for sid in ("pe_ua_amorph_n40_c240_s1", "pe_aa_amorph_n40_c240_s1", "pe_cg_amorph_n40_c240_s1"):
        assert not any("shake" in c for c in commands(render_deck("prep", sysdir(sid))))


@pytest.mark.parametrize("path", SYSTEMS, ids=IDS)
def test_prep_stages_and_outputs(path):
    m = manifest(path)
    res = m["resolution"]
    p = resolve_params(res)
    deck = render_deck("prep", path)
    cmds = commands(deck)
    dt = p["dt_fs"]

    def nsteps(ps):
        return str(round(ps * 1000 / dt))

    assert ["minimize", "0.0001", "1e-06", "10000", "100000"] in cmds
    outs = [c[1] for c in cmds if c[0] == "write_data"]
    want = ["minimized.data", "relaxed.data", "compressed.data", "hold.data", "cooled.data"]
    assert outs == (["pushoff.data"] if res != "cg" else []) + want
    assert [c[1] for c in cmds if c[0] == "write_restart"] == [
        o.replace(".data", ".restart") for o in outs
    ]
    tdamp, pdamp = str(round(100 * dt)), str(round(1000 * dt))
    s4 = commands(stage(deck, 4))
    assert ["fix", "md", "all", "nvt", "temp", "500", "500", tdamp] in s4
    assert ["run", nsteps(100)] in s4 and ["thermo", nsteps(1)] in s4
    s5 = commands(stage(deck, 5))
    npt = [c for c in s5 if c[:4] == ["fix", "md", "all", "npt"]]
    assert [c[9] for c in npt] == ["100", "1"]
    assert all(c[4:12] == ["temp", "500", "500", tdamp, "iso", c[9], c[9], pdamp] for c in npt)
    assert all("drag" not in c for c in npt)
    runs = [c[1] for c in s5 if c[0] == "run"]
    total = {"aa": 1000, "ua": 1000, "cg": 2000}[res]
    assert runs == [nsteps(total * 0.2), nsteps(total * 0.8)]
    s6 = commands(stage(deck, 6))
    hold = {"aa": 5000, "ua": 20000, "cg": 20000}[res]
    assert ["run", nsteps(hold)] in s6
    assert ["dump", "hold", "all", "dcd", nsteps(10), "hold.dcd"] in s6
    assert ["dump_modify", "hold", "unwrap", "yes"] in s6
    s7 = commands(stage(deck, 7))
    temps = [float(c[5]) for c in s7 if c[:4] == ["fix", "md", "all", "npt"]]
    assert len(temps) == 8
    assert temps == pytest.approx([500 - (500 - 298.15) * k / 8 for k in range(1, 9)])
    per_step = {"aa": 1000, "ua": 2000, "cg": 5000}[res]
    assert [c[1] for c in s7 if c[0] == "run"] == [nsteps(per_step)] * 8
    assert ["dump", "cool", "all", "dcd", nsteps(100), "cool.dcd"] in s7
    thermo = first(deck, "thermo_style")
    assert " ".join(thermo[2:]) == (
        "step time temp press pe ke etotal enthalpy vol density lx ly lz "
        "evdwl ecoul elong ebond eangle edihed cpu"
    )


def test_overrides_and_smoke_preset():
    path = sysdir("pe_ua_amorph_n40_c240_s1")
    deck = render_deck("prep", path, overrides={"hold_ps": "100", "tail": "no", "t_final": 300})
    assert ["run", "50000"] in commands(stage(deck, 6))
    assert "tail yes" not in deck
    assert "# cool step 8/8: 300 K" in deck
    smoke = render_deck("prep", path, preset="smoke")
    assert "(preset smoke)" in smoke
    assert ["minimize", "0.0001", "1e-06", "100", "1000"] in commands(smoke)
    assert ["run", "2000"] in commands(stage(smoke, 1))  # 2 ps push-off at 1 fs
    assert ["run", "500"] in commands(stage(smoke, 6))  # 1 ps hold at 2 fs
    # overrides apply on top of the preset
    both = render_deck("prep", path, preset="smoke", overrides={"hold_ps": "2"})
    assert ["run", "1000"] in commands(stage(both, 6))
    # every preset key belongs to some protocol's table
    assert set(PRESETS["smoke"]) <= set().union(*(t["aa"] for t in PROTOCOL_DEFAULTS.values()))


@pytest.mark.parametrize(
    ("overrides", "match"),
    [
        ({"no_such_key": "1"}, "unknown parameter"),
        ({"hold_ps": "long"}, "expected float"),
        ({"tail": "maybe"}, "boolean"),
        ({"hold_ps": "0.0003"}, "whole number"),
    ],
)
def test_bad_overrides_raise(overrides, match):
    with pytest.raises(RenderError, match=match):
        render_deck("prep", sysdir("pe_ua_amorph_n40_c240_s1"), overrides=overrides)


def test_parse_overrides():
    assert parse_overrides(["hold_ps=10", "kspace_accuracy=1e-4"]) == {
        "hold_ps": "10",
        "kspace_accuracy": "1e-4",
    }
    with pytest.raises(RenderError):
        parse_overrides(["hold_ps"])
    with pytest.raises(RenderError):
        render_deck("prep", sysdir("pe_ua_amorph_n40_c240_s1"), preset="nope")
    with pytest.raises(RenderError):
        render_deck("bench", sysdir("pe_ua_amorph_n40_c240_s1"))


def test_write_deck_uses_data_path_relative_to_run_dir(tmp_path):
    path = sysdir("ipp_ua_amorph_n40_c240_s1")
    out = tmp_path / "a" / "b"
    deck = write_deck("prep", path, out)
    assert deck == out / "in.prep"
    rel = first(deck.read_text(), "read_data")[1]
    assert not Path(rel).is_absolute()
    assert (out / rel).resolve() == (path / "data.lmp").resolve()


def test_cli_render_prep(tmp_path, monkeypatch, capsys):
    path = sysdir("pe_cg_amorph_n40_c240_s1")
    monkeypatch.chdir(tmp_path)
    assert main(["render", "prep", "--system", str(path), "--preset", "smoke"]) == 0
    deck = tmp_path / "results" / "runs" / "pe_cg_amorph_n40_c240_s1" / "prep" / "in.prep"
    assert capsys.readouterr().out.strip() == str(
        Path("results/runs/pe_cg_amorph_n40_c240_s1/prep/in.prep")
    )
    assert "(preset smoke)" in deck.read_text()

    data = tmp_path / "other.data"
    data.write_text((path / "data.lmp").read_text())
    out = tmp_path / "custom"
    args = ["render", "prep", "--system", str(path), "--data", str(data), "--out", str(out)]
    assert main([*args, "--set", "hold_ps=50", "--set", "nvt_ps=10"]) == 0
    text = (out / "in.prep").read_text()
    assert first(text, "read_data")[1] == "../other.data"
    assert "#   hold_ps = 50.0" in text and "#   nvt_ps = 10.0" in text


@pytest.mark.parametrize(
    "extra",
    [
        ["--set", "bogus=1"],
        ["--set", "hold_ps"],
        ["--data", "missing.data"],
    ],
)
def test_cli_render_errors_exit_1(extra, tmp_path, capsys):
    path = sysdir("pe_ua_amorph_n40_c240_s1")
    args = ["render", "prep", "--system", str(path), "--out", str(tmp_path), *extra]
    assert main(args) == 1
    assert "sepsim render prep: error" in capsys.readouterr().err
    assert not (tmp_path / "in.prep").exists()


def test_cli_render_missing_system_exit_1(tmp_path, capsys):
    assert main(["render", "prep", "--system", str(tmp_path / "nope")]) == 1
    assert "error" in capsys.readouterr().err


# ---- sweep (D11, D36, D39, D12c) ----

CELSIUS = [25, 35, 45, 55, 65, 75, 85, 90, 100, 110, 120, 130, 140, 150, 160]
HOLDS_C = [25, 90, 130, 160]


def segments_of(deck):
    """(kind, T/K, run steps, dcd every, dcd file) per sweep segment, in order."""
    parts = re.split(r"^# ---- Segment \d+: (step|hold) at ", deck, flags=re.MULTILINE)
    out = []
    for kind, body in zip(parts[1::2], parts[2::2], strict=True):
        cmds = commands(body)
        dump = next(c for c in cmds if c[:2] == ["dump", "traj"])
        npt = [c for c in cmds if c[:4] == ["fix", "md", "all", "npt"]]
        t = float(re.match(r"\S+ C \((\S+) K\)", body).group(1))
        assert all(float(c[5]) == t == float(c[6]) for c in npt)
        run = next(c for c in cmds if c[0] == "run")
        out.append((kind, t, int(run[1]), int(dump[4]), dump[5], body))
    return out


@pytest.mark.parametrize("path", SYSTEMS, ids=IDS)
def test_sweep_grid_durations_and_outputs(path):
    m = manifest(path)
    res = m["resolution"]
    p = resolve_params(res, protocol="sweep")
    dt = p["dt_fs"]
    deck = render_deck("sweep", path, data=path / "data.lmp")
    segs = segments_of(deck)
    kinds = [s[0] for s in segs]
    assert kinds.count("step") == 14 and kinds.count("hold") == 4
    # 25 C hold first; a step to every later point; the hold continues at its point
    temps_c = [round(s[1] - 273.15, 6) for s in segs]
    assert [t for t, k in zip(temps_c, kinds, strict=True) if k == "step"] == CELSIUS[1:]
    assert [t for t, k in zip(temps_c, kinds, strict=True) if k == "hold"] == HOLDS_C
    assert kinds[0] == "hold" and all(
        temps_c[i - 1] == temps_c[i] for i in range(1, len(segs)) if kinds[i] == "hold"
    )
    step_ps, hold_ps = {"aa": (1000, 5000), "ua": (2000, 10000), "cg": (5000, 25000)}[res]
    for kind, t_k, nrun, every, dcd, body in segs:
        ps, frame = (step_ps, 100) if kind == "step" else (hold_ps, 10)
        assert nrun == round(ps * 1000 / dt) and every == round(frame * 1000 / dt)
        assert dcd.endswith(".dcd") and "dump_modify traj unwrap yes" in body
        if kind == "hold":
            label = f"{round(t_k - 273.15)}C"
            want = ["write_data", f"hold_{label}.data"] + (["pair", "ij"] if res == "cg" else [])
            assert want in commands(body)
    assert len({s[4] for s in segs}) == 18  # one DCD per segment
    cmds = commands(deck)
    # NPT iso at 1 atm, Tdamp 100 dt, Pdamp 1000 dt; no velocity create (velocities kept)
    npt = [c for c in cmds if c[:4] == ["fix", "md", "all", "npt"]]
    assert all(
        c[7:12] == [str(round(100 * dt)), "iso", "1", "1", str(round(1000 * dt))] for c in npt
    )
    assert len(npt) == 15  # a hold after its step keeps the running fix
    assert not any(c[0] == "velocity" for c in cmds)
    assert ["thermo", str(round(1000 / dt))] in cmds
    assert " ".join(first(deck, "thermo_style")[2:]) == " ".join(
        first(render_deck("prep", path), "thermo_style")[2:]
    )
    # VDOS NVE segments after each hold, AA only
    vdos = [c for c in cmds if c[:3] == ["dump", "vel", "all"]]
    if res == "aa":
        assert len(vdos) == 4
        assert all(
            c[3:5] == ["custom", "4"] and c[6:] == ["id", "type", "vx", "vy", "vz"] for c in vdos
        )
        assert [c[5] for c in vdos] == [f"vdos_{t}C.dump.gz" for t in HOLDS_C]
        assert sum(c == ["fix", "vdos", "all", "nve"] for c in cmds) == 4
        assert cmds.count(["run", "10000"]) == 4  # 10 ps at 1 fs
    else:
        assert not vdos and "nve" not in deck
    # every fix md is unfixed before an NVE segment or the next target
    assert sum(c[:2] == ["unfix", "md"] for c in cmds) == len(npt)


def test_sweep_vdos_follows_hold_write_and_restores_timestep():
    deck = render_deck(
        "sweep",
        sysdir("pe_aa_amorph_n40_c240_s1"),
        data=sysdir("pe_aa_amorph_n40_c240_s1") / "data.lmp",
    )
    seg = segments_of(deck)[0][5]
    names = [" ".join(c[:2]) for c in commands(seg)]
    order = [
        "unfix md",
        "write_data hold_25C.data",
        "fix vdos",
        "dump vel",
        "run 10000",
        "unfix vdos",
    ]
    pos = [names.index(o) for o in order]
    assert pos == sorted(pos)
    assert ["dump_modify", "vel", "sort", "id"] in commands(seg)
    assert commands(seg)[-2:] == [["timestep", "1"], ["thermo", "1000"]]
    # vdos dt and dump interval are overridable; no gzip on request
    d2 = render_deck(
        "sweep",
        sysdir("pe_aa_amorph_n40_c240_s1"),
        data=sysdir("pe_aa_amorph_n40_c240_s1") / "data.lmp",
        overrides={"vdos_dt_fs": "0.5", "vdos_gzip": "no"},
    )
    assert [
        "dump",
        "vel",
        "all",
        "custom",
        "8",
        "vdos_25C.dump",
        "id",
        "type",
        "vx",
        "vy",
        "vz",
    ] in commands(d2)
    assert ["timestep", "0.5"] in commands(d2) and ["run", "20000"] in commands(d2)


def test_sweep_shake_and_header_grid():
    path = sysdir("ipp_ua_amorph_n40_c240_s1")
    deck = render_deck("sweep", path, data=path / "data.lmp")
    assert ["fix", "shake", "all", "shake", "0.0001", "20", "0", "b", "2"] in commands(deck)
    assert deck.index("fix shake") < deck.index("fix md")
    assert (
        "# Sweep grid (25h,35,45,55,65,75,85,90h,100,110,120,130h,140,150,160h; h = hold): 14 steps + 4 holds at 1 atm"
        in deck
    )
    assert re.search(
        r"^#   1 +hold +25 +298\.15 +10000 +10 +seg01_hold_25C\.dcd hold_25C\.data$",
        deck,
        re.MULTILINE,
    )
    assert re.search(r"^#   18 +hold +160 +433\.15 ", deck, re.MULTILINE)
    for key, value in resolve_params("ua", protocol="sweep").items():
        assert f"#   {key} = {value}\n" in deck
    assert "t_melt" not in deck  # prep-only parameters are not listed


def test_sweep_smoke_preset_and_grid_override():
    path = sysdir("pe_ua_amorph_n40_c240_s1")
    smoke = segments_of(render_deck("sweep", path, data=path / "data.lmp", preset="smoke"))
    assert [(k, round(t - 273.15, 6), n, e) for k, t, n, e, _, _ in smoke] == [
        ("step", 35, 500, 250),
        ("step", 45, 500, 250),
        ("hold", 45, 1000, 250),
    ]
    custom = render_deck(
        "sweep", path, data=path / "data.lmp", overrides={"sweep_grid_c": "25, 50h"}
    )
    assert [s[0] for s in segments_of(custom)] == ["step", "hold"]
    for bad in ("25", "25,abc", ""):
        with pytest.raises(RenderError, match="sweep_grid_c"):
            render_deck("sweep", path, data=path / "data.lmp", overrides={"sweep_grid_c": bad})


def test_sweep_default_data_is_prep_cooled(tmp_path):
    path = sysdir("pe_cg_amorph_n40_c240_s1")
    run = tmp_path / "runs" / "x" / "sweep"
    with pytest.raises(RenderError, match="no such file"):
        write_deck("sweep", path, run)
    (tmp_path / "runs" / "x" / "prep").mkdir(parents=True)
    (tmp_path / "runs" / "x" / "prep" / "cooled.data").write_text((path / "data.lmp").read_text())
    deck = write_deck("sweep", path, run).read_text()
    assert first(deck, "read_data") == ["read_data", "../prep/cooled.data", "nocoeff"]
    with pytest.raises(RenderError, match="data file"):
        render_deck("sweep", path)  # no run directory, no default


# ---- benchmark (D38) ----


@pytest.mark.parametrize("path", SYSTEMS, ids=IDS)
def test_benchmark_npt_warmup_and_timed(path):
    res = manifest(path)["resolution"]
    dt = DEFAULTS[res]["dt_fs"]
    deck = render_deck("benchmark", path, data=path / "data.lmp")
    cmds = commands(deck)
    assert [c[1] for c in cmds if c[0] == "run"] == ["1000", "2000"]
    assert ["thermo", "100"] in cmds
    tdamp, pdamp = str(round(100 * dt)), str(round(1000 * dt))
    assert ["fix", "md", "all", "npt", "temp", "500", "500", tdamp, "iso", "1", "1", pdamp] in cmds
    assert not any(c[0] in ("dump", "write_data", "velocity", "package", "suffix") for c in cmds)
    assert ("fix shake" in deck) == bool(manifest(path).get("shake_bond_types"))


def test_benchmark_nve_dt_check():
    path = sysdir("ipp_ua_amorph_n40_c240_s1")
    for dt, n in (("2", "50000"), ("1", "100000")):
        deck = render_deck(
            "benchmark", path, data=path / "data.lmp", overrides={"ensemble": "nve", "dt_fs": dt}
        )
        cmds = commands(deck)
        assert ["fix", "md", "all", "nve"] in cmds and "npt" not in deck
        assert [c[1] for c in cmds if c[0] == "run"] == ["1000", n]  # warm-up + 100 ps
        assert ["timestep", dt] in cmds
        assert ["fix", "shake", "all", "shake", "0.0001", "20", "0", "b", "2"] in cmds
    pe = render_deck(
        "benchmark",
        sysdir("pe_ua_amorph_n40_c240_s1"),
        data=path / "data.lmp",
        overrides={"ensemble": "nve"},
    )
    assert "fix shake" not in pe
    with pytest.raises(RenderError, match="ensemble"):
        render_deck("benchmark", path, data=path / "data.lmp", overrides={"ensemble": "nvt"})


def test_benchmark_smoke_and_default_data(tmp_path, monkeypatch, capsys):
    path = sysdir("pe_cg_amorph_n40_c240_s1")
    smoke = render_deck("benchmark", path, data=path / "data.lmp", preset="smoke")
    assert [c[1] for c in commands(smoke) if c[0] == "run"] == ["100", "200"]
    monkeypatch.chdir(tmp_path)
    # default input: the prep run's compressed.data, which may not exist yet (warning)
    assert main(["render", "benchmark", "--system", str(path)]) == 0
    io = capsys.readouterr()
    assert "does not exist yet" in io.err
    deck = (tmp_path / "results/runs/pe_cg_amorph_n40_c240_s1/benchmark/in.benchmark").read_text()
    assert first(deck, "read_data")[1] == "../prep/compressed.data"
    assert "sha256 n/a: not present at render time" in deck
    # an explicit --data must exist
    assert main(["render", "benchmark", "--system", str(path), "--data", "nope.data"]) == 1


# ---- Slurm job scripts (D41) ----


def render_job(tmp_path, monkeypatch, protocol="prep", sid="pe_ua_amorph_n40_c240_s1", *extra):
    monkeypatch.chdir(tmp_path)
    args = ["render", protocol, "--system", str(sysdir(sid)), "--job", "--time", "1:00:00", *extra]
    assert main(args) == 0
    job = tmp_path / "jobs" / sid / protocol / "job.sh"
    return job.read_text(), job


def sbatch(text):
    return [ln.split(None, 1)[1] for ln in text.splitlines() if ln.startswith("#SBATCH ")]


def launch(text):
    """(--lmp command, --lmp-probe command) from job.sh."""
    lmp = re.search(r'--lmp "([^"]*)"', text).group(1)
    probe = re.search(r'--lmp-probe "([^"]*)"', text).group(1)
    return lmp, probe


def test_job_cpu_omp_default(tmp_path, monkeypatch, capsys):
    text, job = render_job(tmp_path, monkeypatch)
    root = tmp_path.resolve()
    sid = "pe_ua_amorph_n40_c240_s1"
    sb = sbatch(text)
    assert "--partition=cpu" in sb and "--cpus-per-task=4" in sb and "--ntasks=1" in sb
    assert "--mem=4G" in sb and "--time=1:00:00" in sb
    assert f"--output={root}/logs/%x-%j-%N.out" in sb
    assert f"--job-name={sid}-prep" in sb
    assert not any(s.startswith(("--gres", "--nodelist")) for s in sb)
    assert "--rocm" not in text and "HSA_OVERRIDE_GFX_VERSION" not in text
    assert "srun" not in text and "pmix" not in text
    assert "export OMP_NUM_THREADS=4" in text
    lmp, probe = launch(text)
    assert lmp == "apptainer exec $SEPSIM_SIF lmp -sf omp -pk omp 4"
    assert probe == "apptainer exec $SEPSIM_SIF lmp"
    assert 'exec uv run --frozen --project "$REPO" sepsim run in.prep' in text
    assert (
        "SEPSIM_SIF:-$HOME/projects/installations/lammps/stable_22Jul2025_update6/lammps-rocm6.4.4-gfx1030.sif"
        in text
    )
    # deck next to job.sh in the synced jobs/ tree; the job runs it in results/runs/
    assert (job.parent / "in.prep").is_file() and job.stat().st_mode & 0o111
    assert f"RUN_DIR={root}/results/runs/{sid}/prep" in text
    assert f"JOB_DIR={root}/jobs/{sid}/prep" in text
    assert 'cd "$RUN_DIR"' in text and 'cp "$JOB_DIR/in.prep" in.prep' in text
    assert not (tmp_path / "results" / "runs" / sid / "prep" / "in.prep").exists()
    rd = first((job.parent / "in.prep").read_text(), "read_data")[1]
    assert rd == f"../../../../systems/{sid}/data.lmp" or (
        (root / "results/runs" / sid / "prep" / rd).resolve()
        == (sysdir(sid) / "data.lmp").resolve()
    )
    assert f"if [ ! -f {rd} ]" in text
    assert f"ssubmit {root} jobs/{sid}/prep/job.sh" in text
    out = capsys.readouterr().out.split()
    assert out == [str(job.parent / "in.prep"), str(job)]


@pytest.mark.parametrize(
    ("extra", "want_lmp", "ntasks", "cpt", "omp"),
    [
        (["--accel", "mpi", "--cpus", "8"], "apptainer exec $SEPSIM_SIF mpirun -np 8 lmp", 8, 1, 1),
        (
            ["--accel", "omp", "--cpus", "12", "--ranks", "3"],
            "apptainer exec $SEPSIM_SIF mpirun -np 3 --bind-to none lmp -sf omp -pk omp 4",
            3,
            4,
            4,
        ),
        (
            ["--partition", "gpu"],
            "apptainer exec --rocm $SEPSIM_SIF lmp -sf gpu -pk gpu 1",
            1,
            4,
            4,
        ),
        (
            ["--partition", "gpu", "--accel", "gpu", "--ranks", "2"],
            "apptainer exec --rocm $SEPSIM_SIF mpirun -np 2 --bind-to none lmp -sf gpu -pk gpu 1",
            2,
            2,
            2,
        ),
        (
            ["--partition", "gpu", "--accel", "kokkos", "--cpus", "2"],
            "apptainer exec --rocm $SEPSIM_SIF lmp -k on g 1 -sf kk -pk kokkos newton on neigh half",
            1,
            2,
            2,
        ),
    ],
)
def test_job_accel_and_partition(tmp_path, monkeypatch, extra, want_lmp, ntasks, cpt, omp):
    text, _ = render_job(tmp_path, monkeypatch, "prep", "pe_ua_amorph_n40_c240_s1", *extra)
    sb = sbatch(text)
    lmp, probe = launch(text)
    assert lmp == want_lmp
    assert f"--ntasks={ntasks}" in sb and f"--cpus-per-task={cpt}" in sb
    assert f"export OMP_NUM_THREADS={omp}" in text
    assert any(s.startswith("--mem=") for s in sb)
    gpu = "--partition=gpu" in sb
    assert ("--gres=gpu:1" in sb) == gpu
    assert ("export HSA_OVERRIDE_GFX_VERSION=10.3.0" in text) == gpu
    assert probe == (
        "apptainer exec --rocm $SEPSIM_SIF lmp" if gpu else "apptainer exec $SEPSIM_SIF lmp"
    )
    assert ("--rocm" in text) == gpu


def test_job_node_mem_out_and_sweep_input(tmp_path, monkeypatch):
    sid = "pe_cg_amorph_n40_c240_s1"
    out = "results/runs/pe_cg_amorph_n40_c240_s1/sweep_t2"
    monkeypatch.chdir(tmp_path)
    args = ["render", "sweep", "--system", str(sysdir(sid)), "--job", "--time", "2-00:00:00"]
    args += ["--node", "rdyu-server", "--mem", "6000M", "--out", out]
    assert main(args) == 0
    job = tmp_path / "jobs" / sid / "sweep_t2" / "job.sh"
    text = job.read_text()
    sb = sbatch(text)
    assert "--nodelist=rdyu-server" in sb and "--mem=6000M" in sb
    assert f"--job-name={sid}-sweep_t2" in sb
    assert f"RUN_DIR={tmp_path.resolve()}/{out}" in text
    assert "if [ ! -f ../prep/cooled.data ]" in text
    assert first((job.parent / "in.sweep").read_text(), "read_data")[1] == "../prep/cooled.data"


@pytest.mark.parametrize(
    ("extra", "match"),
    [
        (["--accel", "gpu"], "needs --partition gpu"),
        (["--partition", "gpu", "--accel", "omp"], "needs --partition cpu"),
        (["--cpus", "6", "--ranks", "4"], "must divide"),
        (["--partition", "gpu", "--accel", "kokkos", "--ranks", "2"], "1 rank"),
        (["--mem", "lots"], "--mem"),
        (["--out", "elsewhere/run"], "results/runs"),
    ],
)
def test_job_option_errors(tmp_path, monkeypatch, capsys, extra, match):
    monkeypatch.chdir(tmp_path)
    args = ["render", "prep", "--system", str(sysdir("pe_ua_amorph_n40_c240_s1")), "--job"]
    assert main([*args, "--time", "1:00:00", *extra]) == 1
    assert match in capsys.readouterr().err
    assert not (tmp_path / "jobs").exists()


def test_job_requires_time_and_job_flag(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    base = ["render", "prep", "--system", str(sysdir("pe_ua_amorph_n40_c240_s1"))]
    assert main([*base, "--job"]) == 1
    assert "--time is required" in capsys.readouterr().err
    assert main([*base, "--cpus", "4"]) == 1
    assert "--cpus needs --job" in capsys.readouterr().err


def test_job_guards_and_rolling_restarts(tmp_path):
    """--no-requeue, refuse to overwrite a finished run, uv --frozen; decks write restarts."""
    from sepsim.lammps.slurm import JobOptions, job_script

    opts = JobOptions(partition="cpu", cpus=4, mem="4G", time="1-00:00:00", accel="omp").resolved()
    run_dir = tmp_path / "results" / "runs" / "x" / "prep"
    text = job_script(
        "prep", "x", tmp_path, tmp_path / "jobs" / "x" / "prep", run_dir, "in.data", opts
    )
    assert "#SBATCH --no-requeue" in text
    assert '"status": "finished"' in text
    assert "uv run --frozen" in text
    sysdir = REPO / "systems" / "pe_ua_amorph_n40_c240_s1"
    for protocol in ("prep", "sweep"):
        deck = render_deck(protocol, sysdir, data=sysdir / "data.lmp")
        assert "restart 500000 restart.a restart.b" in deck  # 1 ns at 2 fs
