"""scripts/validity.py: the physical-validity rule table and its data-driven refinements."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


@pytest.fixture(scope="module")
def va():
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("validity", SCRIPTS / "validity.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _hold(t_c, ratio, diffusive=False, p2=True):
    return {
        "t_c": t_c,
        "ratio": ratio,
        "diffusive": diffusive,
        "D_cm2_s": 5e-7 if diffusive else None,
        "p2": p2,
        "p2_reached": p2,
        "rg": True,
        "kappa": True,
    }


def _facts(**kw):
    f = {
        "sid": "pe_cg_amorph_n40_c240_s1",
        "res": "cg",
        "polymer": "pe",
        "kind": "bulk",
        "n_chains": 40,
        "n_carbons": 240,
        "long_cg": False,
        "conversion": False,
        "accepted": True,
        "basis": "own",
        "d47": {"acf": 0.14, "ratio": 2.56, "lag_ns": 40.0, "passed": True},
        "cn_plateau": 9.11,
        "cn_within": False,
        "cn_ref": [6.7, 6.7],
        "sweep": True,
        "sweep_runs": [{"stage": "sweep", "status": "finished", "percent": 100.0}],
        "holds": [_hold(25.0, 0.18), _hold(90.0, 0.38, diffusive=True)],
        "chi2": {"alpha_V": {(25.0, 160.0): 49.7}, "cp": {(25.0, 160.0): 24.0}},
        "vdos_cp": False,
        "pore_res": False,
        "pore_runs": [],
        "gamma": [],
        "finite_size": None,
        "diffuse": [],
        "tensile_runs": [],
        "tensile_res": [],
        "hole_runs": [],
    }
    f.update(kw)
    return f


def test_rule_table_covers_every_property(va):
    for prop, _ in va.PROPERTIES:
        for kind in ("bulk", "pore"):
            for res in ("cg", "ua", "aa"):
                verdict, reason = va.base_rule(prop, kind, res)
                assert verdict in va.VERDICTS and reason


def test_cp_cg_not_meaningful_aa_needs_correction(va):
    cg = va.assess(_facts())["cp"]
    assert cg["verdict"] == va.NOT_MEANINGFUL and "use AA" in cg["reason"]
    aa = va.assess(_facts(res="aa", sid="pe_aa_x"))["cp"]
    assert aa["verdict"] == va.CORRECT and "VDOS" in aa["reason"] and "D12c" in aa["reason"]
    assert va.assess(_facts(res="aa", vdos_cp=True))["cp"]["verdict"] == va.COMPARABLE
    todo = va.assess(_facts(res="aa", sweep=False, sweep_runs=[]))["cp"]
    assert todo["verdict"] == va.NOT_YET and todo["then"] == va.CORRECT
    assert va.assess(_facts(res="ua"))["cp"]["verdict"] == va.NOT_MEANINGFUL


def test_chain_size_at_sweep_t_inherited(va):
    v = va.assess(_facts())["chainT"]
    assert v["verdict"] == va.TREND
    assert "inherited from the 500 K melt" in v["reason"] and "0.18–0.38" in v["reason"]
    assert "outside the melt band" in v["reason"]  # C_n model property stated
    ok = va.assess(_facts(holds=[_hold(25.0, 1.4), _hold(90.0, 2.1)]))["chainT"]
    assert ok["verdict"] == va.COMPARABLE


def test_chain_size_500k(va):
    assert va.assess(_facts())["chain500"]["verdict"] == va.COMPARABLE
    c1500 = va.assess(
        _facts(long_cg=True, n_carbons=1500, d47={"acf": 0.68, "ratio": 0.12, "passed": False})
    )["chain500"]
    assert c1500["verdict"] == va.TREND and "D47 not reached" in c1500["reason"]
    conv = va.assess(_facts(res="aa", conversion=True))["chain500"]
    assert conv["verdict"] == va.TREND and "UA force field" in conv["reason"]
    assert "UA (source box)" in conv["reason"]  # its C_n is the UA box's


def test_dynamics_corrections(va):
    v = va.assess(_facts())
    assert v["segdyn"]["verdict"] == va.CORRECT and "4.07" in v["segdyn"]["reason"]
    # diffusive by the log-slope but COM MSD < 2 <Rg^2>: not chain diffusion yet
    assert v["chaindyn"]["verdict"] == va.NOT_YET and "D53" in v["chaindyn"]["reason"]
    v = va.assess(_facts(holds=[_hold(160.0, 2.5, diffusive=True)]))["chaindyn"]
    assert v["verdict"] == va.CORRECT and "D_real ≈ D_CG/4.07" in v["reason"]
    d = [
        {
            "stage": "diffuse_160C",
            "status": "running",
            "percent": 40.0,
            "t_c": 160.0,
            "diffusive": False,
            "D_cm2_s": None,
            "ratio": 0.3,
            "eta": None,
        }
    ]
    v = va.assess(_facts(diffuse=d))["chaindyn"]
    assert v["verdict"] == va.NOT_YET and "diffuse_160C running 40%" in v["reason"]
    assert va.assess(_facts(res="aa"))["segdyn"]["verdict"] == va.COMPARABLE
    assert va.assess(_facts(res="ua"))["segdyn"]["verdict"] == va.CORRECT


def test_thermo_offsets_and_curvature(va):
    v = va.assess(_facts())
    assert v["rho"]["verdict"] == va.COMPARABLE
    assert "no principled correction" in v["kappa"]["reason"]
    assert "experiment_comparison.md" in v["kappa"]["reason"]
    assert "curved" in v["alpha"]["reason"] and v["alpha"]["value"]
    assert va.assess(_facts(sweep=False))["rho"]["verdict"] == va.NOT_YET


def test_pore_gamma_comparable_with_caveat_and_finite_size(va):
    f = _facts(
        sid="pe_cg_pore_w5nm_n40_c240_s1",
        kind="pore",
        holds=[],
        gamma=[{"t_c": 25.0, "mean": 34.4, "sem": 0.4}],
        pore_runs=[{"stage": "pore", "status": "finished", "percent": 100.0}],
        finite_size={"partner": "pe_cg_pore_w5nm_n320_c240_s1_rep222", "pairs": [(25, -0.2, 0.5)]},
    )
    v = va.assess(f)
    g = v["gamma"]
    assert g["verdict"] == va.COMPARABLE and "cutoff" in g["reason"]
    assert "finite size (D50)" in g["reason"] and "n320" in g["reason"]
    assert v["rho"]["verdict"] == va.NA and v["tensile"]["verdict"] == va.NA
    assert v["film"]["verdict"] == va.NOT_YET and v["film"]["then"] == va.TREND
    assert v["hole"]["verdict"] == va.NOT_YET
    assert va.assess(dict(f, pore_res=True))["film"]["verdict"] == va.TREND
    assert va.finite_size_partner("pe_cg_pore_w5nm_n40_c240_s1") == (
        "pe_cg_pore_w5nm_n320_c240_s1_rep222"
    )
    assert va.finite_size_partner("pe_cg_pore_w5nm_n320_c240_s1_rep222") == (
        "pe_cg_pore_w5nm_n40_c240_s1"
    )


def test_tensile_trend(va):
    assert va.assess(_facts())["tensile"]["verdict"] == va.NOT_YET
    v = va.assess(_facts(tensile_res=["tensile_25C"]))["tensile"]
    assert v["verdict"] == va.TREND and "crystallinity" in v["reason"]


def test_not_accepted_flags(va):
    v = va.assess(_facts(accepted=False))
    assert v["rho"]["flag"] and "NOT accepted" in v["rho"]["reason"]
    assert not v["cp"]["flag"]  # not meaningful anyway
    assert va.short(v["rho"]) == "comp!"
    lines = va.reason_lines(v)
    assert lines[0].startswith("**500 K equilibration NOT accepted**")


def test_missing_everything(va):
    f = _facts(
        sweep=False,
        sweep_runs=[],
        holds=[],
        d47={},
        cn_plateau=None,
        chi2={"alpha_V": {}, "cp": {}},
        accepted=None,
    )
    v = va.assess(f)
    assert all(x["verdict"] in (va.NOT_YET, va.NA, va.NOT_MEANINGFUL) for x in v.values())
    assert not any(x["flag"] for x in v.values())


def test_pore_hold_film_block(va):
    """Pore results (D51) keep the chain/dynamics block under 'film', not 'traj'."""
    h = {
        "t_c": 25.0,
        "traj": {"profile": {}, "layers": {}},
        "film": {
            "com_msd": {"msd_at_max_A2": 300.0, "diffusive": False},
            "rg": {"rg2_A2": {"mean": 1000.0}},
            "p2": {"t_1e_ps": 100.0},
        },
    }
    (f,) = va.hold_facts({"holds": [h]})
    assert f["ratio"] == pytest.approx(0.3) and f["p2_reached"] is True
    assert va.hold_traj({"traj": {"rg": {}}}) == {"rg": {}}
