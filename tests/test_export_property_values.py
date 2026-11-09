"""scripts/export_property_values.py: rows per stage kind, units, exclusions, wide pivot."""

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_property_values.py"


@pytest.fixture(scope="module")
def exp():
    spec = importlib.util.spec_from_file_location("export_property_values", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclass annotations resolve through sys.modules
    spec.loader.exec_module(mod)
    return mod


def _ms(mean, sem, **extra):
    return {"mean": mean, "sem": sem, **extra}


CONVERGENCE = [
    {
        "kind": "hold",
        "quantities": {"density": {"blocks": [{"mean": 9.0, "sem": 1.0}], "g": 16.0}},
    }
]


def _traj(rouse=True):
    t = {
        "available": True,
        "frames": 2501,
        "rg": {"rg_A": _ms(31.2, 0.12), "rg2_A2": _ms(976.0, 7.8)},
        "ree": {"ree_A": _ms(77.1, 0.5), "ree2_A2": _ms(5940.0, 81.0)},
        "c_n": {"plateau": _ms(10.27, 0.08), "n_min": 100},
        "crystallinity": {
            "fraction": {"mean": 0.168, "sd": 0.014},
            "fraction_last": 0.179,
            "largest_cluster": {"mean": 281.5, "max": 492},
            "p2_mean": 0.150,
        },
        "p2": {"t_1e_ps": 122.9, "at_max": 0.03, "lag_max_ps": 12500.0},
        "segment_msd": {
            "msd_1ps_A2": 2.56,
            "msd_10ps_A2": 10.3,
            "msd_1000ps_A2": 158.2,
            "msd_at_max_A2": 815.8,
            "lag_max_ps": 12500.0,
        },
        "com_msd": {
            "diffusive": True,
            "D_cm2_s": 6.08e-7,
            "D_err_cm2_s": 6.2e-9,
            "msd_at_max_A2": 4669.0,
            "msd_rg2_end": 5.26,
            "slope_end": 0.99,
        },
        "curves": {"msd_A2": list(range(184)), "msd_lag_ps": list(range(184))},
        "relaxation": {
            "ree": {"t_1e_ps": None, "tau_fit_ps": 46492.0, "extrapolated": True},
            "tau1_from_p": {"4": 103954.0},
        },
    }
    if rouse:
        t["relaxation"]["rouse"] = [
            {"p": 1, "amp_A2": 295.8, "p2_amp_A2": 295.8, "t_1e_ps": None, "tau_fit_ps": 1e5,
             "extrapolated": True},
            {"p": 2, "amp_A2": 93.5, "p2_amp_A2": 373.8, "t_1e_ps": 6497.1, "tau_fit_ps": 6492.0,
             "extrapolated": False},
        ]  # fmt: skip
    return t


def _stats(density, volume):
    return {
        "density": _ms(density, 9e-5, sem_lower_bound=False),
        "volume": _ms(volume, 28.0),
        "enthalpy": _ms(-4785.9, 4.4),
        "t_c": _ms(25.004, 0.03),
        "rows": 25001,
    }


def _sweep():
    seg = lambda i, kind, t, rho: {
        "index": i,
        "segment": i,
        "kind": kind,
        "name": f"seg {i:02d} {kind} {t:g} C",
        "t_set_c": t,
        "t_k": t + 273.15,
        "stats": _stats(rho, 268105.0),
        "drift": {"density": {"delta": 1e-4, "drift": False}},
        "convergence": {"density": {"block_sem": {"8": 9e-5}, "sem": 8.7e-5}},
    }
    kappa = {"kappa_T_GPa": 1.0, "sem": 0.0145, "g": 2.4, "samples": 22501, "V_mean_A3": 1.0}
    return {
        "system": "pe_cg_amorph_n40_c240_s1",
        "stage": "sweep",
        "version": 1,
        "convergence": CONVERGENCE,
        "segments": [seg(1, "hold", 25.0, 0.83453), seg(2, "step", 90.0, 0.80), seg(3, "hold", 90.0, 0.799)],
        "holds": [
            {"index": 1, "t_c": 25.0, "kappa": kappa, "traj": _traj()},
            {"index": 3, "t_c": 90.0, "kappa": {**kappa, "kappa_T_GPa": 1.2}, "traj": _traj()},
        ],
        "steps": [{"index": 2, "t_c": 90.0, "kappa": kappa, "traj": {"rg": {"rg_A": _ms(32.0, 0.3)}}}],
        "fits": {
            "alpha_V": [
                {"window_c": [25.0, 160.0], "alpha_V_per_K": 6.966e-4, "err": 4.1e-6,
                 "err_unscaled": 9e-7, "alpha_L_per_K": 2.322e-4, "chi2_red": 20.9, "n": 15},
                {"window_c": [25.0, 90.0], "alpha_V_per_K": 6.925e-4, "err": 3.5e-6,
                 "alpha_L_per_K": 2.308e-4},
            ],
            "cp": [{"window_c": [90.0, 160.0], "cp_J_gK": 0.818, "err": 0.006, "cp_kcal_molK": 26.3}],
        },
        "brand_new_number": 42.0,
    }  # fmt: skip


def _hold(stage, t_c):
    return {
        "system": "pe_cg_amorph_n40_c240_s1",
        "stage": stage,
        "t_c": t_c,
        "stats": _stats(0.7596, 294569.0),
        "kappa": {"kappa_T_GPa": 1.638, "sem": 0.008},
        "traj": _traj(rouse=False),
        "convergence": CONVERGENCE,
    }


def _pore():
    stats = {
        "density": _ms(0.47, 0.0),
        "lx": _ms(79.1, 0.0),
        "ly": _ms(79.1, 0.0),
        "pe": _ms(-1500.0, 2.0),
        "etotal": _ms(-200.0, 2.0),
        "pxx": _ms(-20.0, 3.0),
        "pyy": _ms(-21.0, 3.0),
        "pzz": _ms(1.0, 1.0),
        "gamma": _ms(32.9, 0.6, sem_lower_bound=True),
    }
    profile = {
        "plateau": _ms(0.8357, 0.00025),
        "film_gibbs_frames": _ms(64.79, 0.02),
        "film_gibbs_A": 64.789,
        "film_50_A": 64.7,
        "gap_50_A": 50.1,
        "gap_gibbs_A": 50.09,
        "gap_z_A": {"mean": 40.0, "min": 35.0},
        "closest_A": {"mean": 38.0, "min": 30.0},
        "interface_10_90": {"lower": {"width": 6.0, "z10": 1.0}, "upper": {"width": 6.1}},
        "tanh": {"delta_A": 2.58, "delta_err_A": 0.04, "width_10_90_A": 5.67, "h_A": 64.0},
        "rho_sym": [0.1] * 228,
        "z_A": [0.5] * 228,
    }
    return {
        "system": "pe_cg_pore_w5nm_n40_c240_s1",
        "stage": "pore",
        "units": "real",
        "segments": [
            {"index": None, "segment": 3, "kind": "cool", "name": "Stage 3 cool 1/8 (474.8 K)",
             "t_set_c": 201.61875, "stats": stats},
            {"index": 1, "segment": 11, "kind": "hold", "name": "seg 01 hold 25 C", "t_set_c": 25.0,
             "stats": stats, "convergence": {"gamma": {"sem": 1.0}}},
        ],
        "holds": [
            {
                "index": 1,
                "t_c": 25.0,
                "bulk": {"density": _ms(0.8345, 1e-4)},
                "film": _traj(rouse=False),
                "traj": {
                    "profile": profile,
                    "conformation": {
                        "p2z_layer": {"surface": _ms(-0.2, 0.01), "interior": _ms(0.0, 0.01)},
                        "p2z": [0.0] * 35,
                        "rg": {"surface": {"rg_z2_A2": _ms(75.0, 2.3), "chains_mean": 20.0}},
                    },
                    "layers": {
                        "surface": {"msd_at": {"10": {"xy": 5.5, "z": 4.5}}, "p2_t_1e_ps": 80.0},
                        "surface_fraction": 0.3,
                        "layer_A": 10.0,
                    },
                },
            }
        ],
        "fits": {
            "sweep": {"window_c": [25.0, 160.0], "dgamma_dT_mN_mK": -0.0459, "err": 0.0057,
                      "gamma_25c_mN_m": 33.97, "chi2_red": 1.2},
            "cool": {"window_c": [25.0, 201.61875], "dgamma_dT_mN_mK": -0.0436, "err": 0.0077,
                     "gamma_25c_mN_m": 33.35},
        },
        "thermal": {
            "alpha": [{"window_c": [25.0, 160.0], "alpha_z_per_K": 2.6e-4, "alpha_z_err": 1e-5,
                       "alpha_V_film_per_K": 7.2e-4, "alpha_L_per_K": 2.3e-4}],
            "cv": [{"window_c": [25.0, 160.0], "cv_J_gK": 0.70, "err": 0.02, "bulk_cp_J_gK": 0.83}],
            "points": [{"index": 1, "kind": "hold", "t_c": 25.0, "e_s_mJ_m2": _ms(56.9, 1.1),
                        "gamma_minus_TdgdT": 48.5, "gamma": _ms(32.9, 0.6)}],
            "surface_entropy_mJ_m2K": {"mean": 0.0459, "err": 0.0057},
        },
        "pore": {"nominal_width_nm": 5.0, "lz_new_angstrom": 114.9},
    }  # fmt: skip


def _hole():
    frames = [
        {"phase": "inflate", "t_ns": -20.0, "area": 0.0, "drift": 0.0, "r_eff": 0.0},
        {"phase": "production", "t_ns": 0.0, "area": 2890.0, "drift": 0.3, "r_eff": 30.3},
        {"phase": "production", "t_ns": 10.0, "area": 100.0, "drift": 4.0, "r_eff": 5.0},
        {"phase": "production", "t_ns": 20.0, "area": 0.0, "drift": 3.4, "r_eff": 0.0},
    ]
    return {
        "system": "pe_cg_hole_r3nm_25C_n320_c240_s1_rep222",
        "stage": "hole_free",
        "t_c": 25.0,
        "radius_nominal_nm": 3.0,
        "ligament_angstrom": 68.8,
        "r_after_inflation": {"mean": 30.2, "r_min_mean": 28.7},
        "r_t0": 30.3,
        "t_close_ns": 0.195,
        "rate_initial": {"slope": -80.5, "slope_se": 3.0, "intercept": 30.0, "n": 4},
        "rate_open": {"slope": -80.5, "slope_se": 3.0},
        "r_final": 0.0,
        "r_min_final": 0.0,
        "thickness_t0": 162.6,
        "thickness_final": 129.7,
        "free_shell": {"areal_density_ratio": 0.888, "beads": 11585, "msd": {"1 ns": 386.4, "end": 1383.4}},
        "frames": frames,
        "per_segment": [{"index": 1, "kind": "hold", "t_c": 25.0, "r_eff": 0.0, "r_min": 0.0}],
        "params": {"inflate_ps": 10000.0},
    }  # fmt: skip


def _tensile(stage, t_c, rate):
    axis = lambda ax, e: {
        "axis": ax,
        "E_MPa": e,
        "E_err_MPa": 70.0,
        "nu_fit": 0.46,
        "nu_run": 0.50,
        "peak_MPa": 8.46,
        "peak_strain": 0.333,
        "peak_at_end": False,
        "flow_MPa": 3.86,
        "strain_max": 0.5,
        "temp_mean_K": 298.1,
        "curves": {"strain": [0.0, 0.25, 0.5], "nu_secant": [None, 0.48, 0.51]},
    }
    return {
        "runs": [
            {
                "stage": stage,
                "t_c": t_c,
                "rate_per_s": rate,
                "axes": [axis("x", -71.9), axis("y", -12.0)],
                "summary": {"E_MPa": {"mean": -54.8, "sd": 37.2, "n": 2}},
            }
        ],
        "pooled": [],
        "fit_max": 0.02,
    }


def _write(root: Path, sid: str, stage: str, data: dict) -> None:
    d = root / "analysis" / sid / stage
    d.mkdir(parents=True, exist_ok=True)
    (d / "results.json").write_text(json.dumps(data))


@pytest.fixture
def tree(tmp_path):
    sid = "pe_cg_amorph_n40_c240_s1"
    _write(tmp_path, sid, "sweep", _sweep())
    _write(tmp_path, sid, "extend", _hold("extend", 226.85))
    _write(tmp_path, sid, "diffuse_160C", _hold("diffuse_160C", 160.0))
    _write(tmp_path, sid, "tensile_25C_r1e9", _tensile("tensile_25C_r1e9", 25.0, 1e9))
    _write(tmp_path, "pe_cg_pore_w5nm_n40_c240_s1", "pore", _pore())
    _write(tmp_path, "pe_cg_hole_r3nm_25C_n320_c240_s1_rep222", "hole_free", _hole())
    _write(tmp_path, sid, "bench_old", {"x": 1.0})  # unknown stage kind: skipped
    systems = tmp_path / "systems"
    for s, extra in (
        (sid, {}),
        ("pe_cg_pore_w5nm_n40_c240_s1", {"pore": {"nominal_width_nm": 5}}),
        ("pe_cg_hole_r3nm_25C_n320_c240_s1_rep222", {"pore": {}, "hole": {"radius_nm": 3}}),
    ):
        (systems / s).mkdir(parents=True)
        (systems / s / "manifest.yaml").write_text(
            yaml.safe_dump({"id": s, "polymer": "pe", "resolution": "cg", **extra})
        )
    return tmp_path


def _find(rows, **kw):
    return [r for r in rows if all(r[k] == v for k, v in kw.items())]


def _one(rows, **kw):
    hit = _find(rows, **kw)
    assert len(hit) == 1, (kw, hit)
    return hit[0]


def test_sweep_rows(exp, tree):
    ex = exp.export(tree / "analysis", tree / "systems")
    sw = _find(ex.rows, stage="sweep")
    r = _one(sw, segment="seg 01 hold 25 C", property="Density ρ(T)")
    assert (r["value"], r["err"], r["err_kind"], r["unit"]) == (0.83453, 9e-5, "sem", "g/cm³")
    assert (r["T_C"], r["resolution"], r["polymer"], r["kind"]) == ("25", "cg", "pe", "amorph")
    assert r["source_key"] == "segments[0].stats.density.mean"
    # step and hold at the same T stay apart; the step's kappa / traj rows land on it
    assert _one(sw, segment="seg 02 step 90 C", property="Density ρ(T)")["value"] == 0.80
    assert _one(sw, segment="seg 02 step 90 C", property="Radius of gyration Rg")["value"] == 32.0
    k = _one(sw, segment="seg 03 hold 90 C", property="Bulk modulus K")
    assert k["value"] == pytest.approx(1 / 1.2) and k["unit"] == "GPa"
    kt = _one(sw, segment="seg 01 hold 25 C", property="Isothermal compressibility κ_T")
    assert (kt["value"], kt["err"], kt["unit"]) == (1.0, 0.0145, "1/GPa")
    a = _one(sw, property="Volumetric thermal expansion α_V", T_lo_C="25", T_hi_C="90")
    assert (a["value"], a["err_kind"], a["segment"], a["T_C"]) == (6.925e-4, "fit_err", "fit", "")
    al = _one(sw, property="Linear thermal expansion α_L", T_hi_C="160")
    assert al["err"] == pytest.approx(4.1e-6 / 3)
    cp = _find(sw, property="Classical heat capacity Cp", T_lo_C="90")
    assert {r["unit"] for r in cp} == {"J/(g K)", "kcal/(mol K)"}
    h1 = _find(sw, segment="seg 01 hold 25 C")
    rouse = {r["quantity"]: r for r in h1 if r["property"].startswith("Rouse")}
    assert rouse["<X_p²> p=2"]["value"] == 93.5
    assert rouse["tau_p p=2 (1/e)"]["value"] == 6497.1
    assert "tau_p p=1 (1/e)" not in rouse  # null: no row
    assert rouse["tau_p p=1 (exp. fit)"]["note"].startswith("extrapolated")
    assert not rouse["tau_p p=2 (exp. fit)"]["note"]
    assert rouse["tau_1 = p²tau_p from p=4"]["value"] == 103954.0
    msd = {r["quantity"]: r["value"] for r in h1 if r["property"] == "Segment MSD"}
    assert msd == {
        "MSD(1 ps)": 2.56,
        "MSD(10 ps)": 10.3,
        "MSD(1000 ps)": 158.2,
        "MSD(longest lag)": 815.8,
        "longest lag": 12500.0,
    }
    d = _one(h1, property="Chain self-diffusion D_COM")
    assert (d["value"], d["err"], d["unit"]) == (6.08e-7, 6.2e-9, "cm²/s")
    cr = _one(
        h1, property="Crystallinity (local P2 order)", quantity="ordered fraction (p2 >= threshold)"
    )
    assert (cr["err"], cr["err_kind"]) == (0.014, "sd")


def test_exclusions_and_unmapped(exp, tree):
    ex = exp.export(tree / "analysis", tree / "systems")
    keys = " ".join(r["source_key"] for r in ex.rows)
    assert not any(r["source_key"].endswith(".g") for r in ex.rows)
    for bad in (
        "convergence",
        "blocks",
        "samples",
        "chi2_red",
        "err_unscaled",
        "drift.",
        "curves.msd",
        "bulk.",
        "fraction_last",
        "t_c.mean",
        "rows",
        "pore.",
    ):
        assert bad not in keys, bad  # fmt: skip
    # equilibration checks and long curves never become rows
    assert not {r["property"] for r in ex.rows} & {"Drift flags", "D47 chain mixing (500 K)"}
    assert all(r["property"] != "Density profile ρ(z)" for r in ex.rows)
    # the NVT film's box density / volume / enthalpy are not material properties
    assert not _find(ex.rows, stage="pore", property="Density ρ(T)")
    # unknown numeric keys are reported, known ones are not
    assert "brand_new_number" in ex.unmapped
    assert all("convergence" not in k for k in ex.unmapped)
    assert len(ex.unmapped) == 1, ex.unmapped
    # every property name is a "Computed" row of the property table
    table = ROOT_TABLE.read_text()
    assert all(f"| {p} |" in table for p in {r["property"] for r in ex.rows})


ROOT_TABLE = Path(__file__).resolve().parents[1] / "docs" / "property_table.md"


def test_holds_tensile_pore_hole(exp, tree):
    ex = exp.export(tree / "analysis", tree / "systems")
    rows = ex.rows
    ext = _one(rows, stage="extend", property="Density ρ(T)")
    assert (ext["T_C"], ext["segment"], ext["stage_kind"]) == ("226.85", "hold", "extend")
    assert _one(rows, stage="diffuse_160C", property="Bulk modulus K")["value"] == pytest.approx(
        1 / 1.638
    )
    # tensile: per axis plus the mean ± SD row, rate in its own column
    e = _find(rows, stage="tensile_25C_r1e9", property="Apparent Young's modulus E_app")
    assert {(r["axis_or_layer"], r["value"], r["err_kind"]) for r in e} == {
        ("x", -71.9, "fit_err"),
        ("y", -12.0, "fit_err"),
        ("mean ± SD over axes", -54.8, "sd"),
    }
    assert {r["strain_rate_per_s"] for r in e} == {"1e+09"} and {r["T_C"] for r in e} == {"25"}
    sec = _one(
        rows, stage="tensile_25C_r1e9", axis_or_layer="x", property="Secant Poisson ratio ν(ε)"
    )
    assert (sec["value"], sec["note"]) == (0.51, "strain 0.5")
    # pore
    pore = _find(rows, stage="pore")
    assert {r["kind"] for r in pore} == {"pore"}
    g = _one(pore, segment="seg 01 hold 25 C", property="Surface tension γ(T)")
    assert (g["value"], g["unit"], g["note"]) == (32.9, "mN/m", "SEM is a lower bound")
    assert (
        _one(pore, segment="Stage 3 cool 1/8 (474.8 K)", property="Surface tension γ(T)")["T_C"]
        == "201.619"
    )
    assert _one(pore, property="Interior (plateau) density")["value"] == 0.8357
    gib = _one(pore, property="Gibbs film thickness", quantity="h_Gibbs")
    assert (gib["value"], gib["err"], gib["unit"]) == (64.79, 0.02, "Å")
    w = _find(pore, property="Interfacial width (10–90 and tanh)", quantity="w_10-90")
    assert {r["axis_or_layer"] for r in w} == {"lower", "upper"}
    assert len(_find(pore, property="Pore / gap width")) == 4
    lm = _one(pore, property="Layer-resolved MSD (xy, z)", quantity="MSD_z(10 ps)")
    assert (lm["axis_or_layer"], lm["value"]) == ("surface", 4.5)
    assert _one(pore, property="Radius of gyration Rg", quantity="Rg")["axis_or_layer"] == "film"
    dg = _one(
        pore, property="dγ/dT and γ(25 °C)", quantity="dgamma/dT", segment="fit (cool branch)"
    )
    assert (dg["T_lo_C"], dg["T_hi_C"], dg["value"]) == ("25", "201.619", -0.0436)
    assert _one(pore, property="Surface entropy")["T_hi_C"] == "160"
    assert _one(pore, property="Film heat capacity Cv")["unit"] == "J/(g K)"
    assert _one(pore, property="Surface excess energy e_s", quantity="e_s")["T_C"] == "25"
    # hole
    hole = _find(rows, stage="hole_free")
    assert {r["kind"] for r in hole} == {"hole"}
    tc = _one(hole, property="Closure time t_close")
    assert (tc["value"], tc["unit"], tc["T_C"]) == (0.195, "ns", "25")
    rate = _one(hole, property="Closure speed dR/dt", quantity="dR_eff/dt (first 5 ns)")
    assert (rate["value"], rate["err"], rate["unit"]) == (-80.5, 3.0, "Å/ns")
    area = {r["quantity"]: r["value"] for r in _find(hole, property="Hole area A(t)")}
    assert area == {"A at t0": 2890.0, "A at the end": 0.0}  # inflate frame not used
    drift = {r["quantity"]: r["value"] for r in _find(hole, property="Centroid drift")}
    assert drift["centre drift (max)"] == 4.0
    assert _one(hole, property="Free-shell MSD", quantity="MSD(1 ns)")["value"] == 386.4
    seg = _one(hole, segment="seg 1 hold", property="Hole radius R_eff(t)")
    assert seg["T_C"] == "25"


def test_cli_writes_long_and_wide(exp, tree, tmp_path, capsys):
    out = tmp_path / "out"
    rc = exp.main(
        ["--analysis-dir", str(tree / "analysis"), "--systems", str(tree / "systems"),
         "--runs-dir", str(tree / "runs"), "--out-dir", str(out)]
    )  # fmt: skip
    assert rc == 0
    printed = capsys.readouterr().out
    assert "brand_new_number" in printed
    with (out / "property_values.csv").open(encoding="utf-8") as fh:
        long = list(csv.DictReader(fh))
    assert list(long[0]) == exp.LONG_COLUMNS
    with (out / "property_values_wide.csv").open(encoding="utf-8") as fh:
        wide = list(csv.DictReader(fh))
    row = _one(wide, stage="sweep", segment="seg 01 hold 25 C")
    assert float(row["Density ρ(T): density [g/cm³]"]) == 0.83453
    assert float(row["Isothermal compressibility κ_T: kappa_T [1/GPa]"]) == 1.0
    # one wide row per key; tensile axes are separate rows
    keys = [tuple(r[c] for c in exp.WIDE_KEY) for r in wide]
    assert len(keys) == len(set(keys))
    assert len(_find(wide, stage="tensile_25C_r1e9")) == 3
    assert len(long) == sum(
        1 for r in wide for c, v in r.items() if c not in exp.WIDE_KEY and v != ""
    )


def _progress(root: Path, sid: str, stage: str, data: dict) -> None:
    d = root / "runs" / sid / stage
    d.mkdir(parents=True, exist_ok=True)
    (d / "progress.json").write_text(json.dumps(data))


HYST = [
    {"cool_step": 1, "t_k": 474.76875, "rho_cool": 0.7367, "rho_cool_sem": 2e-4,
     "rho_sweep": None, "delta_pct": None},
    {"cool_step": 3, "t_k": 424.30625, "rho_cool": 0.7639, "rho_cool_sem": 0.000168,
     "rho_sweep": 0.76475, "delta_pct": -0.1118},
    {"cool_step": 8, "t_k": 298.15, "rho_cool": 0.83497, "rho_cool_sem": 9e-5,
     "rho_sweep": 0.83460, "delta_pct": 0.0441},
]  # fmt: skip


@pytest.fixture
def runs(tree):
    sid = "pe_cg_amorph_n40_c240_s1"
    _progress(tree, sid, "sweep", {"hysteresis": HYST})
    _progress(tree, sid, "sweep_old_20ns", {"hysteresis": HYST})  # no analysis dir: ignored
    _progress(tree, sid, "diffuse_160C", {"hold": {"d_com": {"eta_rouse_pa_s": 0.0247}}})
    _progress(tree, sid, "extend", {"hold": {"d_com": {"diffusive": False}}})  # no eta: no row
    return tree / "runs"


def test_progress_rows(exp, tree, runs):
    ex = exp.export(tree / "analysis", tree / "systems", runs)
    hy = _find(ex.rows, property="Cooling/heating hysteresis")
    assert {r["stage"] for r in hy} == {"sweep"} and {r["stage_kind"] for r in hy} == {"sweep"}
    assert {r["segment"] for r in hy} == {"cool vs sweep"}
    assert len(hy) == 2 * 3 + 1  # null delta_pct entry skipped
    rc = _one(hy, T_C="25", quantity="rho (cooling)")
    assert (rc["value"], rc["err"], rc["err_kind"], rc["unit"]) == (0.83497, 9e-5, "sem", "g/cm³")
    assert rc["source_key"] == "progress.json:hysteresis[2].rho_cool"
    rs = _one(hy, T_C="151.156", quantity="rho (sweep)")
    assert (rs["value"], rs["err"], rs["err_kind"]) == (0.76475, "", "")
    dp = _find(hy, quantity="delta_pct = (rho_cool - rho_sweep)/rho_sweep")
    assert {(r["T_C"], r["value"], r["unit"]) for r in dp} == {
        ("151.156", -0.1118, "%"),
        ("25", 0.0441, "%"),
    }
    mx = _one(hy, quantity="max |delta_pct|")
    assert (mx["value"], mx["T_C"], mx["unit"]) == (0.1118, "", "%")
    assert "151.156" in mx["note"]
    eta = _one(ex.rows, property="Rouse viscosity η_R")
    assert (eta["stage"], eta["segment"], eta["T_C"]) == ("diffuse_160C", "hold", "160")
    assert (eta["value"], eta["unit"]) == (0.0247, "Pa·s")
    assert eta["source_key"] == "progress.json:hold.d_com.eta_rouse_pa_s"
    table = ROOT_TABLE.read_text()
    assert "| Cooling/heating hysteresis |" in table and "| Rouse viscosity η_R |" in table


def test_progress_missing_runs_dir(exp, tree):
    base = exp.export(tree / "analysis", tree / "systems")
    missing = exp.export(tree / "analysis", tree / "systems", tree / "no_runs_here")
    assert base.rows == missing.rows
    assert not _find(base.rows, property="Rouse viscosity η_R")
