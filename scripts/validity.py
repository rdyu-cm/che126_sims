"""Physical validity of each property for each system: the single source of truth.

For every current system and every property we analyze, a verdict on whether the value
can be compared with experiment, and why not when it cannot:

- ``comparable``: compare with the stated experimental data (caveats in the reason);
- ``trend``: only temperature, PE-vs-iPP, resolution and box-size trends are meaningful;
- ``needs correction``: meaningful only after a stated correction (AA Cp after the VDOS
  quantum correction, D12c; CG/UA dynamics after a time-mapping factor);
- ``not meaningful``: the model cannot represent it (CG/UA Cp: degrees of freedom removed);
- ``not yet computed``: the data do not exist yet (the reason says what the verdict will be);
- ``n/a``: the property does not apply to this kind of system (e.g. γ of a bulk box).

A verdict is *flagged* (``flag``) when the system's 500 K equilibration verdict is not
"accepted" (D47; C1500 on the C_n no-drift rule), so every number from it is suspect.

How a verdict is reached (:func:`assess`):

1. :data:`BASE_RULES` gives the verdict and reason per (property, system kind,
   resolution), from the property guide's "Comparability with experiment" table
   (docs/property_guide.md).
2. The system's own check results then refine it (all read from the summary context,
   i.e. ``progress.json`` and ``results.json``; nothing is recomputed):

   - data missing → ``not yet computed`` (base verdict kept in the reason);
   - AA Cp → ``comparable`` once a VDOS-corrected Cp exists (:data:`VDOS_CP_KEYS`);
   - chain size at 500 K: ``comparable`` only if D47 passed on the system's own box
     (long CG chains: D47 not reached → ``trend``; ua2aa AA boxes: the chain
     conformations are the UA force field's → ``trend``); C_n outside the melt band is
     stated as a model property;
   - chain size at the sweep T: ``trend`` if any hold's chain COM MSD at the longest
     lag is below ⟨Rg²⟩ (chains did not move their own size: the size is inherited from
     the cooled 500 K melt, not re-equilibrated at that T);
   - chain diffusion D_COM: only a COM MSD that is diffusive *and* beyond ⟨Rg²⟩ (sweep
     hold or D53 ``diffuse`` hold) counts; else ``not yet computed``;
   - α_V: χ²_red ≫ 1 over 25–160 °C is noted (α_V depends on T: use the half windows);
   - pores: the 40-chain vs 2×2×2 γ difference (D50 finite-size check) is stated.

Used by ``scripts/summarize_systems.py`` ("Physical validity by system" section) and
``scripts/convergence_dashboard.py`` (``results/validity_overview.png``).
"""

from __future__ import annotations

COMPARABLE = "comparable"
TREND = "trend"
CORRECT = "needs correction"
NOT_MEANINGFUL = "not meaningful"
NOT_YET = "not yet computed"
NA = "n/a"
VERDICTS = (COMPARABLE, TREND, CORRECT, NOT_MEANINGFUL, NOT_YET, NA)
SHORT = {
    COMPARABLE: "comp",
    TREND: "trend",
    CORRECT: "corr",
    NOT_MEANINGFUL: "no",
    NOT_YET: "todo",
    NA: "n/a",
}
COLORS = {
    COMPARABLE: "#9fd89f",
    TREND: "#b9d3ee",
    CORRECT: "#f7d26a",
    NOT_MEANINGFUL: "#ee8a8a",
    NOT_YET: "#d9d9d9",
    NA: "#ffffff",
}
MEANING = {
    COMPARABLE: "comparable to experiment (with the stated data and caveats)",
    TREND: "trends only (T, PE vs iPP, resolution, box size)",
    CORRECT: "needs a correction first (VDOS quantum Cp; time mapping for CG/UA dynamics)",
    NOT_MEANINGFUL: "not meaningful for this model",
    NOT_YET: "not yet computed",
    NA: "does not apply",
}
FLAG_MARK = "!"  # appended to the short label of a flagged verdict

# (key, column label) in display order
PROPERTIES = (
    ("rho", "ρ(T)"),
    ("alpha", "α_V"),
    ("kappa", "κ_T"),
    ("cp", "Cp"),
    ("chain500", "Rg/R_ee/C_n 500 K"),
    ("chainT", "Rg/R_ee/C_n sweep T"),
    ("segdyn", "P2, segment MSD"),
    ("chaindyn", "D_COM, viscosity"),
    ("gamma", "γ, dγ/dT"),
    ("film", "film structure"),
    ("tensile", "tensile E/ν/yield"),
    ("hole", "hole closure"),
)
PROP_LABEL = dict(PROPERTIES)

CHAIN_RELAXED = 1.0  # hold COM MSD / <Rg^2> below this: chain size inherited (D45/D49)
# D_COM is chain self-diffusion only if the COM MSD is diffusive AND >= 2 <Rg^2> (as D47;
# docs/experiment_comparison.md: the log-slope criterion alone accepts the Rouse regime)
CHAIN_DIFFUSE = 2.0
EXPERIMENT_DOC = "docs/experiment_comparison.md"
_CG_CHAIN = "CG PE chains too stiff: C_n +25–45% (C240), ≈ +10% (C1500); Rg ≈ +20% (C240)"
# Measured offsets vs experiment (from EXPERIMENT_DOC; sources there), per (polymer, res).
EXPERIMENT_OFFSETS: dict[tuple[str, str], dict[str, str]] = {
    ("pe", "cg"): {
        "rho": "CG PE ≈ 2% low (C1500 1–2%)",
        "alpha": "CG PE ≈ 5% low",
        "kappa": "CG PE 50–60% too compressible",
        "cp": "CG PE classical Cp ≈ 65% low",
        "chain500": _CG_CHAIN,
        "chainT": _CG_CHAIN,
        "gamma": "CG PE γ within 1–3% at 25–160 °C; dγ/dT ≈ 20% shallower",
        "segdyn": "CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H)",
        "chaindyn": "CG PE dynamics ≈ 4× too fast",
        "tensile": "amorphous: compare with G_e ≈ 2.6 MPa (E ≈ 8 MPa), not separator GPa moduli",
    },
    ("pe", "ua"): {"rho": "TraPPE-UA PE ≈ 1.5–2% high (literature, 448 K)"},
}
# Static offsets of these properties (force-field properties) have no principled correction
OFFSET_ONLY = ("rho", "alpha", "kappa", "chain500", "chainT")
NO_CORRECTION = "no principled correction for the offset (model property): compare our UA/AA values"
CURVED_CHI2 = 10.0  # alpha_V / Cp chi2_red over 25-160 C above this: T-dependent
VDOS_CP_KEYS = ("cp_vdos", "cp_quantum")  # results.json keys of a quantum-corrected Cp
D47_EXEMPT_CG_CARBONS = 1000

_DENSITY = (
    COMPARABLE,
    (
        "vs melt PVT data above Tm; below Tm vs the amorphous density extrapolated from the"
        " melt (not a semicrystalline sample); accuracy is a force-field property"
    ),
)
_DYN_UA = (
    CORRECT,
    (
        "UA dynamics are faster than real PE (no hydrogen friction). Correction: a UA→AA"
        " time-mapping factor per T from our own AA at the same T (none published for this"
        " force field here); T trends as is"
    ),
)
CG_TIME_FACTOR = 4.07  # SDK PE melt: CG chains diffuse 4.07x faster (Hall et al. 2019)
_DYN_CG = (
    CORRECT,
    (
        "SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply"
        f" CG times (P2, MSD times) by {CG_TIME_FACTOR}, i.e. D_real ≈ D_CG/{CG_TIME_FACTOR},"
        f" η_real ≈ {CG_TIME_FACTOR}·η_CG (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150,"
        " 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA"
        " at the same T once available; T trends as is"
    ),
)
_DYN_AA = (
    COMPARABLE,
    "AA dynamics roughly comparable (with caution: force-field friction, finite box)",
)
_CHAIN = (
    COMPARABLE,
    "vs neutron-scattering melt data (PE C∞ ≈ 6.7–7.4, iPP ≈ 6.2) at similar chain length",
)
_NOT_BULK = (NA, "bulk property (pores: see film structure)")
_NOT_PORE = (NA, "pore property")

# BASE_RULES[property][system kind][resolution or "*"] -> (verdict, reason).
# System kind: "bulk" or "pore". From docs/property_guide.md, comparability table.
BASE_RULES: dict[str, dict[str, dict[str, tuple[str, str]]]] = {
    "rho": {"bulk": {"*": _DENSITY}, "pore": {"*": _NOT_BULK}},
    "alpha": {"bulk": {"*": _DENSITY}, "pore": {"*": _NOT_BULK}},
    "kappa": {
        "bulk": {
            "*": (COMPARABLE, "vs melt PVT data at 1 atm (bulk modulus 1/κ_T)"),
            "cg": (
                COMPARABLE,
                "vs melt PVT data at 1 atm; CG models usually come out too compressible",
            ),
        },
        "pore": {"*": _NOT_BULK},
    },
    "cp": {
        "bulk": {
            "cg": (
                NOT_MEANINGFUL,
                (
                    "CG removes all motion inside a 3-CH2 bead (a bead keeps 3 of 27 atomic"
                    " degrees of freedom): classical Cp per gram far too low. No principled"
                    " correction (a hybrid vibrational add-on is only approximate): use AA"
                ),
            ),
            "ua": (
                NOT_MEANINGFUL,
                (
                    "UA removes the H atoms (their degrees of freedom), so classical Cp is not"
                    " the real one (close to experiment only by accident). No principled"
                    " correction (a hybrid vibrational add-on is only approximate): use AA"
                ),
            ),
            "aa": (
                CORRECT,
                (
                    "classical Cp gives every vibration k_B T (fully flexible AA ≈ 2.4×"
                    " experiment). Correction: the VDOS quantum correction (D12c), then compare"
                    " with ATHAS melt Cp"
                ),
            ),
        },
        "pore": {"*": _NOT_BULK},
    },
    "chain500": {
        "bulk": {"*": _CHAIN},
        "pore": {"*": (NA, "the pore's chains come from its source box (see that row)")},
    },
    "chainT": {
        "bulk": {"*": _CHAIN},
        "pore": {"*": (TREND, "chain shape in a film vs bulk: no direct experiment")},
    },
    "segdyn": {
        "bulk": {"aa": _DYN_AA, "ua": _DYN_UA, "cg": _DYN_CG},
        "pore": {"aa": _DYN_AA, "ua": _DYN_UA, "cg": _DYN_CG},
    },
    "chaindyn": {
        "bulk": {"aa": _DYN_AA, "ua": _DYN_UA, "cg": _DYN_CG},
        "pore": {"*": _NOT_PORE},
    },
    "gamma": {
        "bulk": {"*": _NOT_PORE},
        "pore": {
            "*": (
                COMPARABLE,
                (
                    "vs melt γ(T) at similar molecular weight; cutoff-dependent (plain LJ"
                    " cutoff, no tail correction at surfaces, D48), which biases γ low"
                ),
            ),
            "cg": (
                COMPARABLE,
                (
                    "vs melt γ(T) at similar molecular weight; SDK CG was partly fitted to γ;"
                    " cutoff-dependent (plain LJ cutoff, no tail correction, D48), biased low"
                ),
            ),
        },
    },
    "film": {
        "bulk": {"*": _NOT_PORE},
        "pore": {"*": (TREND, "no direct experiment: mechanism and within-simulation comparisons")},
    },
    "tensile": {
        "bulk": {
            "*": (
                TREND,
                (
                    "not comparable to separator data (their stiffness/yield come from"
                    " crystallinity; MD rates ~10⁹× faster): amorphous response, T and rate trends"
                ),
            )
        },
        "pore": {"*": (NA, "bulk test")},
    },
    "hole": {
        "bulk": {"*": (NA, "pore/film protocol")},
        "pore": {"*": (TREND, "no direct experiment: closure mechanism and trends only")},
    },
}


# --------------------------------------------------------------------------- facts


def _get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def _runs(ctx: dict, sid: str, kind: str) -> list[dict]:
    """Current (non-superseded) runs of a stage kind, by directory name."""
    out = [
        r
        for r in (ctx["runs"].get(sid) or {}).values()
        if not r.get("superseded") and r.get("kind") == kind
    ]
    return sorted(out, key=lambda r: r["dir"])


def _run_state(run: dict) -> dict:
    p = run.get("progress") or {}
    return {
        "stage": run["dir"],
        "status": p.get("status") or _get(run, "manifest", "status") or "unknown",
        "percent": p.get("percent"),
    }


def _analysis(ctx: dict, sid: str, prefix: str) -> list[tuple[str, dict]]:
    ana = ctx["analysis"].get(sid) or {}
    return sorted((k, v) for k, v in ana.items() if k == prefix or k.startswith(prefix + "_"))


def hold_traj(h: dict) -> dict:
    """The per-hold trajectory block: ``traj`` of a sweep hold; for a pore hold (D51)
    ``film``, which has the same keys (``traj`` there holds the profiles/layers)."""
    t = h.get("traj") or {}
    if any(k in t for k in ("rg", "com_msd", "curves")):
        return t
    return h.get("film") or t


def hold_facts(res: dict | None) -> list[dict]:
    """Per hold of a sweep/pore results.json: T, chain-scale ratio, dynamics flags."""
    out = []
    for h in (res or {}).get("holds") or []:
        t = hold_traj(h)
        com = t.get("com_msd") or {}
        msd, rg2 = com.get("msd_at_max_A2"), _get(t, "rg", "rg2_A2", "mean")
        p2 = t.get("p2") or {}
        out.append(
            {
                "t_c": h.get("t_c"),
                "ratio": msd / rg2 if msd is not None and rg2 else None,
                "diffusive": com.get("diffusive") if com else None,
                "D_cm2_s": com.get("D_cm2_s"),
                "p2": bool(p2),
                "p2_reached": p2.get("t_1e_ps") is not None if p2 else None,
                "rg": _get(t, "rg", "rg_A", "mean") is not None,
                "kappa": _get(h, "kappa", "kappa_T_GPa") is not None,
            }
        )
    return out


def _gamma_holds(run: dict | None) -> list[dict]:
    out = []
    for s in _get(run, "progress", "segments") or []:
        g = _get(s, "stats", "gamma")
        if g and s.get("sweep_kind") == "hold" and g.get("mean") is not None:
            out.append({"t_c": s.get("t_c"), "mean": g["mean"], "sem": g.get("sem") or 0.0})
    return out


def finite_size_partner(sid: str) -> str | None:
    """The other box size of a D50 pair: 40-chain ↔ 2×2×2 (n320, ``_rep222``)."""
    if sid.endswith("_rep222"):
        return sid[: -len("_rep222")].replace("_n320_", "_n40_")
    if "_n40_" in sid:
        return sid.replace("_n40_", "_n320_") + "_rep222"
    return None


def system_facts(sid: str, ctx: dict) -> dict:
    """Everything the rules need about one system, from the summary context."""
    man = ctx["systems"].get(sid) or {}
    m = ctx["meta"][sid]
    eq = ctx["eq"].get(sid) or {}
    ch = eq.get("checks") or {}
    res_kind = (m.get("resolution") or "?").lower()
    pore = bool(m.get("pore"))
    sweep = _analysis(ctx, sid, "sweep")
    sweep_res = sweep[-1][1] if sweep else None
    pore_ana = _analysis(ctx, sid, "pore")
    pore_res = pore_ana[-1][1] if pore_ana else None
    sweep_runs = _runs(ctx, sid, "sweep")
    pore_runs = _runs(ctx, sid, "pore") or _runs(ctx, sid, "pore_relax")
    fits = (sweep_res or {}).get("fits") or {}
    chi2 = {
        q: {tuple(f.get("window_c") or ()): f.get("chi2_red") for f in fits.get(q) or []}
        for q in ("alpha_V", "cp")
    }
    vdos = any((sweep_res or {}).get(k) or fits.get(k) for k in VDOS_CP_KEYS)
    diffuse = []
    for r in _runs(ctx, sid, "diffuse"):
        hold = _get(r, "progress", "hold") or {}
        d = hold.get("d_com") or {}
        diffuse.append(
            {
                **_run_state(r),
                "t_c": hold.get("t_c"),
                "diffusive": d.get("diffusive"),
                "D_cm2_s": d.get("D_cm2_s"),
                "ratio": _get(hold, "com_msd", "ratio"),
                "eta": d.get("eta_rouse_pa_s"),
            }
        )
    partner = finite_size_partner(sid) if pore else None
    fs = None
    if partner and partner in ctx["meta"]:
        mine = {round(g["t_c"]): g for g in _gamma_holds(pore_runs[-1] if pore_runs else None)}
        p_runs = _runs(ctx, partner, "pore")
        theirs = {round(g["t_c"]): g for g in _gamma_holds(p_runs[-1] if p_runs else None)}
        fs = {
            "partner": partner,
            "pairs": [
                (
                    t,
                    mine[t]["mean"] - theirs[t]["mean"],
                    (mine[t]["sem"] ** 2 + theirs[t]["sem"] ** 2) ** 0.5,
                )
                for t in sorted(set(mine) & set(theirs))
            ],
        }
    return {
        "sid": sid,
        "res": res_kind,
        "polymer": m.get("polymer"),
        "kind": "pore" if pore else "bulk",
        "n_chains": man.get("n_chains"),
        "n_carbons": man.get("n_carbons"),
        "long_cg": res_kind == "cg" and (man.get("n_carbons") or 0) >= D47_EXEMPT_CG_CARBONS,
        "conversion": bool(man.get("conversion")),
        "accepted": eq.get("accepted"),
        "basis": eq.get("basis"),
        "d47": ch.get("d47") or {},
        "cn_plateau": ch.get("plateau"),
        "cn_within": ch.get("within_reference"),
        "cn_ref": ch.get("reference"),
        "sweep": sweep_res is not None,
        "sweep_runs": [_run_state(r) for r in sweep_runs],
        "holds": hold_facts(sweep_res if not pore else pore_res),
        "chi2": chi2,
        "vdos_cp": vdos,
        "pore_res": pore_res is not None,
        "pore_runs": [_run_state(r) for r in pore_runs],
        "gamma": _gamma_holds(pore_runs[-1] if pore_runs else None),
        "finite_size": fs,
        "diffuse": diffuse,
        "tensile_runs": [_run_state(r) for r in _runs(ctx, sid, "tensile")],
        "tensile_res": [k for k, _ in _analysis(ctx, sid, "tensile")],
        "hole_runs": [_run_state(r) for r in _runs(ctx, sid, "hole")],
    }


# --------------------------------------------------------------------------- rules


def base_rule(prop: str, kind: str, res: str) -> tuple[str, str]:
    by_res = BASE_RULES[prop][kind]
    return by_res.get(res) or by_res.get("*") or (NA, "no rule")


def _v(verdict: str, reason: str, value: str = "", note: str = "") -> dict:
    """A verdict: ``reason`` (full, incl. the base rule), ``note`` (the system-specific
    part only), ``value`` (a short figure label), ``then`` (for "not yet computed": the
    verdict once computed), ``flag`` (equilibration not accepted)."""
    return {
        "verdict": verdict,
        "reason": reason + note,
        "note": note.lstrip("; "),
        "flag": False,
        "value": value,
        "then": None,
    }


def _todo(base: tuple[str, str], why: str) -> dict:
    v = _v(NOT_YET, f"{why}; once computed: {base[0]} ({base[1]})")
    v.update(note=why, then=base[0])
    return v


def _runs_text(runs: list[dict]) -> str:
    def one(r):
        pct = f" {r['percent']:.0f}%" if r.get("percent") is not None else ""
        return f"{r['stage']} {r['status']}{pct}"

    return ", ".join(one(r) for r in runs)


def _sweep_missing(f: dict) -> str:
    if f["sweep_runs"]:
        return f"no sweep analysis yet ({_runs_text(f['sweep_runs'])})"
    return "no sweep run yet"


def _fmt(x, spec=".2f") -> str:
    return "?" if x is None else format(x, spec)


def assess(f: dict) -> dict[str, dict]:
    """{property: {verdict, reason, flag, value}} for one system's facts."""
    out = {}
    kind, res = f["kind"], f["res"]
    holds = f["holds"]
    for prop, _ in PROPERTIES:
        base = base_rule(prop, kind, res)
        if base[0] == NA:
            out[prop] = _v(*base)
            continue
        out[prop] = _RULES[prop](f, base, holds)
    # experiment offsets (EXPERIMENT_DOC) and the no-correction note for model offsets
    off = EXPERIMENT_OFFSETS.get((f["polymer"] or "", res), {})
    for prop, v in out.items():
        if v["verdict"] in (NA, NOT_YET):
            continue
        extra = ""
        if prop in off:
            extra += f"; vs experiment: {off[prop]} ({EXPERIMENT_DOC})"
        if prop in OFFSET_ONLY and res in ("cg", "ua"):
            extra += f"; {NO_CORRECTION}"
        v["reason"] += extra
        v["note"] = (v["note"] + extra).lstrip("; ")
    # equilibration not accepted: every computed verdict is suspect
    if f["accepted"] is not True:
        why = (
            "500 K equilibration NOT accepted"
            if f["accepted"] is False
            else "no 500 K equilibration verdict yet"
        )
        for v in out.values():
            if v["verdict"] not in (NA, NOT_YET, NOT_MEANINGFUL):
                v["flag"] = True
                v["reason"] = f"{why}: {v['reason']}"
    return out


def _thermo(f, base, holds, need_kappa=False):
    if not f["sweep"]:
        return _todo(base, _sweep_missing(f))
    if need_kappa and not any(h["kappa"] for h in holds):
        return _todo(base, "no κ_T in the sweep analysis")
    return _v(*base)


def _rule_rho(f, base, holds):
    return _thermo(f, base, holds)


def _rule_alpha(f, base, holds):
    v = _thermo(f, base, holds)
    if v["verdict"] == base[0]:
        c = f["chi2"]["alpha_V"].get((25.0, 160.0))
        if c is not None and c > CURVED_CHI2:
            note = (
                f"; V(T) curved (χ²_red {c:.0f} over 25–160 °C): α_V depends on T,"
                " quote the 25–90 / 90–160 °C windows"
            )
            v = _v(*base, value=f"χ²_red {c:.0f}", note=note)
    return v


def _rule_kappa(f, base, holds):
    return _thermo(f, base, holds, need_kappa=True)


def _rule_cp(f, base, holds):
    if base[0] == NOT_MEANINGFUL:
        return _v(*base)
    if not f["sweep"]:
        return _todo(base, _sweep_missing(f))
    if f["vdos_cp"]:
        return _v(COMPARABLE, "VDOS quantum-corrected Cp (D12c) vs melt Cp (≈ 2.3–2.6 J/gK)")
    return _v(*base)


def _cn_note(f) -> str:
    p, ref, within = f["cn_plateau"], f["cn_ref"], f["cn_within"]
    if p is None or within is not False:
        return ""
    r = ref[0] if ref else None
    ff = "UA (source box)" if f["conversion"] else f["res"].upper()
    return (
        f"; C_n {p:.2f} is outside the melt band ({_fmt(r, 'g')} ±10%): a property of the"
        f" {ff} force field, not of the equilibration"
    )


def _rule_chain500(f, base, holds):
    d = f["d47"]
    if f["cn_plateau"] is None and not d:
        return _todo(base, "no 500 K hold checks yet")
    note = _cn_note(f)
    if f["long_cg"]:
        return _v(
            TREND,
            f"D47 not reached (C1500: end-to-end ACF {_fmt(d.get('acf'))}, COM MSD/⟨Rg²⟩"
            f" {_fmt(d.get('ratio'))} at {_fmt(d.get('lag_ns'), '.0f')} ns): accepted on the"
            " C_n no-drift rule only, so the whole-chain size is not equilibrated",
            "D47 n/a",
            note,
        )
    if f["conversion"]:
        return _v(
            TREND,
            "ua2aa box: the chain conformations were equilibrated with the UA force field"
            " (D32/D47) and only relaxed locally in AA; compare the UA row",
            "from UA",
            note,
        )
    if d.get("passed"):
        return _v(base[0], f"D47 passed; {base[1]}", "D47 ok", note)
    return _v(TREND, "D47 not passed: chains not relaxed at 500 K", "D47 fail", note)


def _rule_chainT(f, base, holds):
    if f["kind"] == "pore" and not f["pore_res"]:
        return _todo(base, "no pore analysis (D51) yet")
    if f["kind"] == "bulk" and not f["sweep"]:
        return _todo(base, _sweep_missing(f))
    r = [(h["t_c"], h["ratio"]) for h in holds if h["ratio"] is not None]
    if not r:
        return _todo(base, "no trajectory analysis of the holds")
    lo, hi = min(v for _, v in r), max(v for _, v in r)
    rng = f"{lo:.2f}–{hi:.2f}"
    if lo < CHAIN_RELAXED:
        cold = ", ".join(f"{t:g}" for t, v in r if v < CHAIN_RELAXED)
        return _v(
            TREND,
            f"inherited from the 500 K melt: hold COM MSD/⟨Rg²⟩ {rng} < 1 at {cold} °C, so"
            " chains did not move their own size and Rg/R_ee/C_n were not re-equilibrated"
            " at that T (T dependence not resolved)",
            f"MSD/Rg² {rng}",
            _cn_note(f),
        )
    return _v(
        base[0],
        f"{base[1]}",
        f"MSD/Rg² {rng}",
        f"; chains moved ≥ ⟨Rg²⟩ in every hold ({rng})" + _cn_note(f),
    )


def _rule_segdyn(f, base, holds):
    if f["kind"] == "pore":
        if not f["pore_res"]:
            return _todo(base, "no pore analysis (D51) yet")
        return _v(*base)
    if not f["sweep"]:
        return _todo(base, _sweep_missing(f))
    p = [h for h in holds if h["p2"]]
    if not p:
        return _todo(base, "no trajectory analysis of the holds")
    miss = [h["t_c"] for h in p if not h["p2_reached"]]
    note = f"; P2 1/e not reached at {', '.join(f'{t:g}' for t in miss)} °C" if miss else ""
    return _v(*base, note=note)


def _rule_chaindyn(f, base, holds):
    good = [h for h in holds if h["diffusive"] and (h["ratio"] or 0) >= CHAIN_DIFFUSE]
    good_d = [d for d in f["diffuse"] if d["diffusive"] and (d["ratio"] or 0) >= CHAIN_DIFFUSE]
    if good or good_d:
        ts = [h["t_c"] for h in good] + [d["t_c"] for d in good_d]
        note = f"; diffusive and COM MSD ≥ 2⟨Rg²⟩ at {', '.join(_fmt(t, 'g') for t in ts)} °C"
        note += "; the Rouse viscosity is a lower bound if the chains are entangled"
        return _v(*base, note=note)
    why = []
    if holds:
        rr = [h["ratio"] for h in holds if h["ratio"] is not None]
        nd = sum(1 for h in holds if h["diffusive"] is False)
        if rr:
            why.append(
                f"sweep holds too short (COM MSD/⟨Rg²⟩ ≤ {max(rr):.2f}, {nd}/{len(holds)}"
                " not diffusive)"
            )
    elif not f["sweep"]:
        why.append(_sweep_missing(f))
    if f["diffuse"]:
        why.append("diffuse holds (D53): " + _runs_text(f["diffuse"]) + ", not diffusive yet")
    else:
        why.append("needs a long D53 diffuse hold")
    return _todo(base, "; ".join(why))


def _rule_gamma(f, base, holds):
    if not f["gamma"]:
        if f["pore_runs"]:
            return _todo(base, f"no γ from the hold segments ({_runs_text(f['pore_runs'])})")
        return _todo(base, "no pore run yet")
    fs = f["finite_size"]
    if fs and fs["pairs"]:
        worst = max(fs["pairs"], key=lambda p: abs(p[1]) / (p[2] or 1e-9))
        n_sig = abs(worst[1]) / (worst[2] or 1e-9)
        note = (
            f"; finite size (D50) vs {fs['partner']}: Δγ up to {worst[1]:+.1f} mN/m"
            f" ({n_sig:.1f} combined SEM, at {worst[0]:g} °C)"
        )
        return _v(*base, value=f"size Δγ {n_sig:.1f}σ", note=note)
    if fs:
        return _v(*base, note=f"; finite-size partner {fs['partner']} has no γ yet")
    return _v(*base)


def _rule_film(f, base, holds):
    if not f["pore_res"]:
        return _todo(base, "no pore analysis (D51) yet")
    return _v(*base)


def _rule_tensile(f, base, holds):
    if f["tensile_res"]:
        return _v(*base)
    if f["tensile_runs"]:
        return _todo(base, "tensile runs " + _runs_text(f["tensile_runs"]) + ", no analysis yet")
    return _todo(base, "no tensile run (D54)")


def _rule_hole(f, base, holds):
    if f["hole_runs"]:
        done = [r for r in f["hole_runs"] if r["status"] == "finished"]
        if done:
            return _v(*base)
        return _todo(base, "hole runs " + _runs_text(f["hole_runs"]))
    return _todo(base, "no hole run (D52)")


_RULES = {
    "rho": _rule_rho,
    "alpha": _rule_alpha,
    "kappa": _rule_kappa,
    "cp": _rule_cp,
    "chain500": _rule_chain500,
    "chainT": _rule_chainT,
    "segdyn": _rule_segdyn,
    "chaindyn": _rule_chaindyn,
    "gamma": _rule_gamma,
    "film": _rule_film,
    "tensile": _rule_tensile,
    "hole": _rule_hole,
}


def short(v: dict) -> str:
    return SHORT[v["verdict"]] + (FLAG_MARK if v["flag"] else "")


def system_validity(sid: str, ctx: dict) -> dict[str, dict]:
    return assess(system_facts(sid, ctx))


# --------------------------------------------------------------------------- markdown


def reason_lines(v: dict[str, dict]) -> list[str]:
    """Compact per-system reasons: non-comparable cells with their reason, "not yet
    computed" cells grouped by cause, comparable cells by name with system notes."""
    out = []
    for k, _ in PROPERTIES:
        c = v[k]
        if c["verdict"] in (TREND, CORRECT, NOT_MEANINGFUL):
            fl = " (flagged)" if c["flag"] else ""
            out.append(f"{PROP_LABEL[k]}: **{c['verdict']}**{fl}: {c['reason']}")
    todo: dict[str, list[str]] = {}
    for k, _ in PROPERTIES:
        if v[k]["verdict"] == NOT_YET:
            todo.setdefault(v[k]["note"], []).append(f"{PROP_LABEL[k]} (then {v[k]['then']})")
    for why, props in todo.items():
        out.append(f"not yet computed: {', '.join(props)}: {why}")
    comp = [
        PROP_LABEL[k]
        + (f" ({v[k]['note']})" if v[k]["note"] else "")
        + (" (flagged)" if v[k]["flag"] else "")
        for k, _ in PROPERTIES
        if v[k]["verdict"] == COMPARABLE
    ]
    if comp:
        out.append("**comparable**: " + "; ".join(comp))
    flagged = [c["reason"].split(":")[0] for c in v.values() if c["flag"]]
    if flagged:
        out.insert(0, f"**{flagged[0]}**: every computed property is flagged")
    return out


def markdown(ctx: dict, order: list[str], figure: str | None = None) -> list[str]:
    """The "Physical validity by system" summary section."""
    rows, details = [], []
    for sid in order:
        v = system_validity(sid, ctx)
        rows.append([f"`{sid}`", *(short(v[k]) for k, _ in PROPERTIES)])
        details.append(f"- `{sid}`")
        details += [f"  - {b}" for b in reason_lines(v)]
    head = ["System", *(lab for _, lab in PROPERTIES)]
    legend = "; ".join(f"**{SHORT[k]}** = {MEANING[k]}" for k in VERDICTS)
    return [
        "## Physical validity by system",
        "",
        (
            "Can each property be compared with experiment for this system? Rules:"
            " `scripts/validity.py` (single source of truth; base table = the property"
            " guide's comparability table, refined by each system's own checks; the"
            " comparison data and general caveats per property are in that table)."
            f" Our numbers next to experiment, with sources: [{EXPERIMENT_DOC}](../{EXPERIMENT_DOC})."
            + (f" Figure: [validity overview]({figure})." if figure else "")
        ),
        "",
        (
            f"Legend: {legend}; **{FLAG_MARK}** = flagged: the system's 500 K equilibration is"
            " not accepted (or has no verdict yet)."
        ),
        "",
        "| " + " | ".join(head) + " |",
        "|" + "---|" * len(head),
        *("| " + " | ".join(r) + " |" for r in rows),
        "",
        "<details><summary>Reasons per system</summary>",
        "",
        *details,
        "",
        "</details>",
        "",
    ]
