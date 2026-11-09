"""Flatten the `sepsim analyze` results into tidy CSVs of final property values.

Reads (read-only) every ``<analysis>/<system>/<stage>/results.json`` and the system
manifests (``<systems>/<id>/manifest.yaml``, for polymer / resolution / kind) and writes

- ``property_values.csv`` (long): one row per value, with its error, unit and the dotted
  path into results.json it came from;
- ``property_values_wide.csv``: one row per (system, stage, segment, T or fit window,
  strain rate, axis/layer), one column per "property: quantity [unit]" (values only).

Nothing is recomputed: values are copied as stored, in the units results.json uses
(lengths Å, energies kcal/mol per system, pressures atm, times ps; hole radii Å and hole
times ns). The few exceptions are labelled in ``source_key``: the bulk modulus K = 1/κ_T,
α_L's error (= α_V error / 3), the hole area and centroid drift at t0/end and the end
value of the secant Poisson curve (read off the stored per-frame/curve data).

Every row belongs to a "Computed" property of ``docs/property_table.md`` (``property`` is
the table's name verbatim), except the equilibration checks (D47, D24, drift flags,
step-vs-hold). JSON keys map to properties through the explicit rule tables below, never
by generic flattening; numeric keys that match neither a rule nor an ignore pattern are
printed as "unmapped" so new keys show up. Curves are represented by their scalar
summaries (no curve points); convergence blocks, block SEMs, statistical inefficiency,
sample counts and fit diagnostics are left out.

Two properties exist only in the run progress files
(``<runs>/<system>/<stage>/progress.json``, read only for stages that have an analysis
dir): the cooling-vs-sweep density hysteresis (``hysteresis``, sweep stage) and the Rouse
viscosity (``hold.d_com.eta_rouse_pa_s``, extend/diffuse). A missing runs dir or
progress.json is skipped silently.

    uv run --frozen python scripts/export_property_values.py [--analysis-dir DIR]
        [--systems DIR] [--runs-dir DIR] [--out-dir DIR]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

LONG_COLUMNS = [
    "system",
    "resolution",
    "polymer",
    "kind",
    "stage",
    "stage_kind",
    "segment",
    "T_C",
    "T_lo_C",
    "T_hi_C",
    "strain_rate_per_s",
    "axis_or_layer",
    "property",
    "quantity",
    "value",
    "err",
    "err_kind",
    "unit",
    "note",
    "source_key",
]
WIDE_KEY = [
    "system",
    "resolution",
    "polymer",
    "kind",
    "stage",
    "stage_kind",
    "segment",
    "T_C",
    "T_lo_C",
    "T_hi_C",
    "strain_rate_per_s",
    "axis_or_layer",
]
STAGE_KINDS = ("sweep", "extend", "diffuse", "tensile", "hole", "pore")

# Property names exactly as in docs/property_table.md.
RHO = "Density ρ(T)"
VOL = "Volume V(T), box lengths"
ALPHA_V = "Volumetric thermal expansion α_V"
ALPHA_L = "Linear thermal expansion α_L"
KAPPA = "Isothermal compressibility κ_T"
BULK_K = "Bulk modulus K"
ENTH = "Enthalpy H(T)"
ENERGY = "Potential / total energy"
PRESS = "Pressure tensor Pxx, Pyy, Pzz"
CP = "Classical heat capacity Cp"
RG = "Radius of gyration Rg"
REE = "End-to-end distance R_ee"
CN = "Characteristic ratio C_n / C∞"
CRYST = "Crystallinity (local P2 order)"
P2MEAN = "Mean local order ⟨p2⟩"
TAU_P2 = "Bond reorientation ACF / τ_P2"
SEG_MSD = "Segment MSD"
COM_MSD = "Chain COM MSD and MSD/⟨Rg²⟩"
D_COM = "Chain self-diffusion D_COM"
TAU_EE = "End-to-end relaxation time τ_ee"
ETA_R = "Rouse viscosity η_R"
HYST = "Cooling/heating hysteresis"
ROUSE_X = "Rouse modes X_p, amplitudes ⟨X_p²⟩"
ROUSE_T = "Rouse times τ_p and τ_1 from p²τ_p"
STRESS = "Stress–strain curve (true and engineering)"
E_APP = "Apparent Young's modulus E_app"
NU = "Poisson ratio ν (fit and whole run)"
NU_SEC = "Secant Poisson ratio ν(ε)"
PEAK = "Peak stress and peak strain"
FLOW = "Flow stress"
GAMMA = "Surface tension γ(T)"
DGDT = "dγ/dT and γ(25 °C)"
S_ENT = "Surface entropy"
E_S = "Surface excess energy e_s"
CV = "Film heat capacity Cv"
ALPHA_Z = "Film thermal expansion α_z, α_V(film)"
PLATEAU = "Interior (plateau) density"
GIBBS = "Gibbs film thickness"
WIDTH = "Interfacial width (10–90 and tanh)"
GAP = "Pore / gap width"
CLOSEST = "Closest approach across the gap"
P2Z = "Bond orientation P2z(z)"
SHAPE = "Chain shape near the surface"
LAYER_MSD = "Layer-resolved MSD (xy, z)"
LAYER_P2 = "Layer-resolved bond reorientation"
SURF_FRAC = "Surface fraction"
R_EFF = "Hole radius R_eff(t)"
AREA = "Hole area A(t)"
SLAB = "Slab radii R(z) and R_min"
T_CLOSE = "Closure time t_close"
DRDT = "Closure speed dR/dt"
R_FINAL = "Plateau / final radius"
THICK = "Film thickness over time"
DRIFT = "Centroid drift"
LIGAMENT = "Ligament"
RIM = "Free-shell rim build-up"
SHELL_MSD = "Free-shell MSD"
TETHER = "Scaffold tether stats"


# --------------------------------------------------------------------------- rules


@dataclass(frozen=True)
class Rule:
    """One JSON leaf -> one row. ``pattern`` is a regex matched (fullmatch) against the
    leaf's path relative to the record; ``quantity`` / ``axis`` are format templates over
    the regex groups (``{0}``, ``{1}``...) and the leaf's parent dict (``{parent[p]}``).
    ``err`` names the sibling key holding the error (scaled by ``err_scale``); ``note``
    is (sibling flag key, text) added when the flag is true."""

    pattern: str
    prop: str
    quantity: str
    unit: str
    err: str | None = None
    err_kind: str = ""
    axis: str = ""
    note: tuple[str, str] | None = None
    err_scale: float = 1.0


def prefixed(prefix: str, rules: list[Rule], axis: str | None = None) -> list[Rule]:
    """The same rules under a sub-dict (``prefix`` is a literal path such as ``traj.``)."""
    out = []
    for r in rules:
        kw = {k: getattr(r, k) for k in Rule.__dataclass_fields__}
        kw["pattern"] = re.escape(prefix) + f"(?:{r.pattern})"
        if axis is not None and not r.axis:
            kw["axis"] = axis
        out.append(Rule(**kw))
    return out


def under(prefix: str, patterns: list[str]) -> list[str]:
    """Ignore patterns under a sub-dict (``prefix`` is a literal path such as ``traj.``)."""
    return [re.escape(prefix) + f"(?:{p})" for p in patterns]


def ms(path: str, prop: str, quantity: str, unit: str, err: str = "sem", **kw) -> Rule:
    """A {mean, sem|sd} dict at ``path``."""
    kind = {"sem": "sem", "sd": "sd"}.get(err, "fit_err")
    return Rule(re.escape(path) + r"\.mean", prop, quantity, unit, err, kind, **kw)


EXTRAP = ("extrapolated", "extrapolated (exp. fit beyond the data)")

# Segment thermo statistics (sweep segments, extend/diffuse holds, pore segments).
BULK_STATS = [
    ms("stats.density", RHO, "density", "g/cm³"),
    ms("stats.volume", VOL, "V", "Å³"),
    ms("stats.enthalpy", ENTH, "H (whole system)", "kcal/mol"),
]
FILM_STATS = [
    ms("stats.lx", VOL, "Lx", "Å"),
    ms("stats.ly", VOL, "Ly", "Å"),
    ms("stats.pe", ENERGY, "PE (whole system)", "kcal/mol"),
    ms("stats.etotal", ENERGY, "E_total (whole system)", "kcal/mol"),
    ms("stats.pxx", PRESS, "Pxx", "atm"),
    ms("stats.pyy", PRESS, "Pyy", "atm"),
    ms("stats.pzz", PRESS, "Pzz", "atm"),
    ms("stats.gamma", GAMMA, "gamma", "mN/m"),
]
KAPPA_RULES = [Rule(r"kappa\.kappa_T_GPa", KAPPA, "kappa_T", "1/GPa", "sem", "sem")]

# Chain analysis of a trajectory (sweep holds/steps, extend/diffuse, pore film chains).
TRAJ_RULES = [
    ms("rg.rg_A", RG, "Rg", "Å"),
    ms("rg.rg2_A2", RG, "<Rg²>", "Å²"),
    ms("ree.ree_A", REE, "R_ee", "Å"),
    ms("ree.ree2_A2", REE, "<R_ee²>", "Å²"),
    ms("c_n.plateau", CN, "C_inf (C_n plateau, n >= n_min)", ""),
    ms("crystallinity.fraction", CRYST, "ordered fraction (p2 >= threshold)", "", err="sd"),
    Rule(r"crystallinity\.largest_cluster\.mean", CRYST, "largest cluster (mean)", "sites"),
    Rule(r"crystallinity\.largest_cluster\.max", CRYST, "largest cluster (max)", "sites"),
    Rule(r"crystallinity\.p2_mean", P2MEAN, "<p2>", ""),
    Rule(r"p2\.t_1e_ps", TAU_P2, "tau_P2 (1/e)", "ps"),
    Rule(r"segment_msd\.msd_(\d+)ps_A2", SEG_MSD, "MSD({0} ps)", "Å²"),
    Rule(r"segment_msd\.msd_at_max_A2", SEG_MSD, "MSD(longest lag)", "Å²"),
    Rule(r"segment_msd\.lag_max_ps", SEG_MSD, "longest lag", "ps"),
    Rule(r"com_msd\.msd_at_max_A2", COM_MSD, "COM MSD(longest lag)", "Å²"),
    Rule(r"com_msd\.msd_rg2_end", COM_MSD, "COM MSD/<Rg²> (longest lag)", ""),
    Rule(r"com_msd\.D_cm2_s", D_COM, "D_COM", "cm²/s", "D_err_cm2_s", "fit_err"),
    Rule(r"relaxation\.ree\.t_1e_ps", TAU_EE, "tau_ee (1/e)", "ps"),
    Rule(r"relaxation\.ree\.tau_fit_ps", TAU_EE, "tau_ee (exp. fit)", "ps", note=EXTRAP),
    Rule(r"relaxation\.rouse\[\d+\]\.amp_A2", ROUSE_X, "<X_p²> p={parent[p]}", "Å²"),
    Rule(r"relaxation\.rouse\[\d+\]\.p2_amp_A2", ROUSE_X, "p²<X_p²> p={parent[p]}", "Å²"),
    Rule(r"relaxation\.rouse\[\d+\]\.t_1e_ps", ROUSE_T, "tau_p p={parent[p]} (1/e)", "ps"),
    Rule(
        r"relaxation\.rouse\[\d+\]\.tau_fit_ps",
        ROUSE_T,
        "tau_p p={parent[p]} (exp. fit)",
        "ps",
        note=EXTRAP,
    ),
    Rule(r"relaxation\.tau1_from_p\.(\d+)", ROUSE_T, "tau_1 = p²tau_p from p={0}", "ps"),
]
TRAJ_IGNORE = [
    r"(rg|ree)\..*",  # sem siblings are read with their mean
    r"c_n\.(bond_length|frames|n_min)",
    r"crystallinity\.(fraction_(first|last|max)|frames|half_span|l_proj_A|r_c_A|sites|threshold)",
    r"p2\.(at_max|lag_max_ps)",
    r"com_msd\.(lag_max_ps|slope_end|slope_max|t_start_ps|t_end_ps|D_err_cm2_s)",
    r"relaxation\.(lag_max_ps|ree\.acf_at_max)",
    r"relaxation\.rouse\[\d+\]\.(acf_at_max|p)",
    r"bursts\..*|frame_ps|frames|frames_total|hold_ns|window_ns|parts\[\d+\]\.frames",
]

# Density profile across the film (pore segments and holds).
PROFILE_RULES = [
    ms("plateau", PLATEAU, "rho_plateau", "g/cm³"),
    ms("film_gibbs_frames", GIBBS, "h_Gibbs", "Å"),
    Rule(r"film_50_A", GIBBS, "h_50 (50% crossings)", "Å"),
    Rule(r"interface_10_90\.(lower|upper)\.width", WIDTH, "w_10-90", "Å", axis="{0}"),
    Rule(r"tanh\.delta_A", WIDTH, "tanh delta", "Å", "delta_err_A", "fit_err"),
    Rule(r"tanh\.width_10_90_A", WIDTH, "tanh 10-90 width", "Å"),
    Rule(r"gap_50_A", GAP, "gap at 50% density", "Å"),
    Rule(r"gap_gibbs_A", GAP, "gap at the Gibbs surfaces", "Å"),
    Rule(r"gap_z_A\.mean", GAP, "clear z gap (mean)", "Å"),
    Rule(r"gap_z_A\.min", GAP, "clear z gap (min)", "Å"),
    Rule(r"closest_A\.mean", CLOSEST, "closest approach (mean)", "Å"),
    Rule(r"closest_A\.min", CLOSEST, "closest approach (min)", "Å"),
]
PROFILE_IGNORE = [
    r"area_A2|bin_A|frames|lz_A|plateau_region_A|film_gibbs_A",
    r"interface_10_90\.(lower|upper)\.z(10|90)",
    r"tanh\.(h_A|rho_p|delta_err_A)",
]
LAYERS = r"(surface|interior|film)"
PORE_TRAJ_RULES = [
    *prefixed("profile.", PROFILE_RULES),
    ms("conformation.p2z_layer.surface", P2Z, "P2z", "", axis="surface"),
    ms("conformation.p2z_layer.interior", P2Z, "P2z", "", axis="interior"),
    Rule(
        rf"conformation\.rg\.{LAYERS}\.rg_z2_A2\.mean",
        SHAPE,
        "Rg_z²",
        "Å²",
        "sem",
        "sem",
        axis="{0}",
    ),
    Rule(
        rf"conformation\.rg\.{LAYERS}\.rg_xy2_half_A2\.mean",
        SHAPE,
        "Rg_xy²/2",
        "Å²",
        "sem",
        "sem",
        axis="{0}",
    ),
    Rule(
        rf"layers\.{LAYERS}\.msd_at\.(\d+)\.(xy|z)", LAYER_MSD, "MSD_{2}({1} ps)", "Å²", axis="{0}"
    ),
    Rule(rf"layers\.{LAYERS}\.p2_t_1e_ps", LAYER_P2, "tau_P2 (1/e)", "ps", axis="{0}"),
    Rule(r"layers\.surface_fraction", SURF_FRAC, "surface fraction", "", axis="surface"),
]
PORE_TRAJ_IGNORE = [
    *under("profile.", PROFILE_IGNORE),
    r"profile\.drift\..*",
    r"conformation\.rg\.\w+\.chains_mean",
    rf"layers\.({LAYERS}\.p2_at_max|layer_A|lag_max_ps|bursts_used|origins_per_lag\.\w+)",
    r"frame_ps|frames|hold_ns",
]

TENSILE_AXIS_RULES = [
    Rule(r"E_MPa", E_APP, "E_app", "MPa", "E_err_MPa", "fit_err"),
    Rule(r"nu_fit", NU, "nu (fit, strain <= fit_max)", ""),
    Rule(r"nu_run", NU, "nu (whole run)", ""),
    Rule(r"peak_MPa", PEAK, "peak stress", "MPa", note=("peak_at_end", "peak at the end")),
    Rule(r"peak_strain", PEAK, "peak strain", "", note=("peak_at_end", "peak at the end")),
    Rule(r"flow_MPa", FLOW, "flow stress", "MPa"),
    Rule(r"strain_max", STRESS, "max strain reached", ""),
]
TENSILE_SUMMARY_RULES = [
    Rule(r"E_MPa\.mean", E_APP, "E_app", "MPa", "sd", "sd"),
    Rule(r"nu_fit\.mean", NU, "nu (fit, strain <= fit_max)", "", "sd", "sd"),
    Rule(r"nu_run\.mean", NU, "nu (whole run)", "", "sd", "sd"),
    Rule(r"peak_MPa\.mean", PEAK, "peak stress", "MPa", "sd", "sd"),
    Rule(r"peak_strain\.mean", PEAK, "peak strain", "", "sd", "sd"),
    Rule(r"flow_MPa\.mean", FLOW, "flow stress", "MPa", "sd", "sd"),
]

HOLE_RULES = [
    Rule(r"r_after_inflation\.mean", R_EFF, "R_eff after inflation", "Å"),
    Rule(r"r_after_inflation\.r_min_mean", SLAB, "R_min after inflation", "Å"),
    Rule(r"r_t0", R_EFF, "R_eff at t0", "Å"),
    Rule(r"t_close_ns", T_CLOSE, "t_close", "ns"),
    Rule(r"rate_initial\.slope", DRDT, "dR_eff/dt (first 5 ns)", "Å/ns", "slope_se", "fit_err"),
    Rule(r"rate_open\.slope", DRDT, "dR_eff/dt (open period)", "Å/ns", "slope_se", "fit_err"),
    Rule(r"plateau\.r_eff", R_FINAL, "plateau R_eff (last quarter)", "Å", "r_eff_sd", "sd"),
    Rule(r"plateau\.r_min", R_FINAL, "plateau R_min (last quarter)", "Å"),
    Rule(r"r_final", R_FINAL, "final R_eff", "Å"),
    Rule(r"r_min_final", R_FINAL, "final R_min", "Å"),
    Rule(r"thickness_t0", THICK, "thickness at t0", "Å"),
    Rule(r"thickness_final", THICK, "final thickness", "Å"),
    Rule(r"ligament_angstrom", LIGAMENT, "ligament min(Lx,Ly) - 2R (nominal)", "Å"),
    Rule(r"free_shell\.areal_density_ratio", RIM, "shell / far-film areal density", ""),
    Rule(r"free_shell\.beads", RIM, "beads in the shell at t0", "beads"),
    Rule(r"free_shell\.msd\.(\d+) ns", SHELL_MSD, "MSD({0} ns)", "Å²"),
    Rule(r"free_shell\.msd\.end", SHELL_MSD, "MSD(end of run)", "Å²"),
    Rule(r"free_shell\.msd\.end_ns", SHELL_MSD, "end of run", "ns"),
    Rule(r"scaffold\.tethered", TETHER, "tethered beads", "beads"),
    Rule(r"scaffold\.tethered_fraction", TETHER, "tethered fraction", ""),
    Rule(r"scaffold\.nearest_tethered_r_t0", TETHER, "nearest tethered bead r at t0", "Å"),
    Rule(r"scaffold\.nearest_tethered_r_held_min", TETHER, "nearest tethered r (held, min)", "Å"),
]
HOLE_IGNORE = [
    r"radius_nominal_nm|t_c|film_thickness_angstrom|production_ns|version",
    r"params\..*|dcds\[\d+\]\..*|frames\[\d+\]\..*",
    r"rate_(initial|open)\.(intercept|n|slope_se)|plateau\.(r_eff_sd|window_ns.*)",
    r"free_shell\.r_(in|out)",
    r"scaffold\.(d_nm|k|lammps_group_count)",
    r"segments\[\d+\]\..*",
]
HOLE_SEGMENT_RULES = [
    Rule(r"r_eff", R_EFF, "R_eff (2nd-half mean)", "Å"),
    Rule(r"r_min", SLAB, "R_min (2nd-half mean)", "Å"),
]

# Paths dropped everywhere (convergence-only data, metadata, curves, fit diagnostics).
GLOBAL_IGNORE = re.compile(
    r"(^|\.)(convergence|drift|curves|series|blocks|sem_vs_block|block_sem|plots|method|"
    r"code_git|run_git|kappa)\b"
    r"|(^|\.)(g|samples|chi2_red|err_unscaled|n|sem|sd|err|sem_lower_bound|rows|rows_used|"
    r"window_ps|index|segment|t_k|t_set_c|t_c|version|mass_gmol|planned_ns|fit_points_c|"
    r"line|window_c)$"
    r"|(^|\.)stats\.t_c\.|(^|\.)bulk\.|\.V_(mean|std)_A3$|(^|\.)avg_ps$|(^|\.)p_atm$"
)


# --------------------------------------------------------------------------- walking


def leaves(obj, path: str = ""):
    """(path, value, parent dict) of every numeric scalar (bools and lists skipped)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                yield p, v, obj
            elif isinstance(v, (dict, list)):
                yield from leaves(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, dict):
                yield from leaves(v, f"{path}[{i}]")


def join(base: str, rel: str) -> str:
    if not base:
        return rel
    return base + rel if rel.startswith("[") else f"{base}.{rel}"


def normalise(path: str) -> str:
    """Key shape for the unmapped report: list indices and numeric keys collapsed."""
    p = re.sub(r"\[\d+\]", "[]", path)
    return re.sub(r"\.\d+(?=\.|$)", ".<n>", p)


def fnum(x) -> float | None:
    if x is None or isinstance(x, bool):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


class Exporter:
    def __init__(self):
        self.rows: list[dict] = []
        self.handled: set[str] = set()  # full paths of the current file mapped or ignored
        self.unmapped: dict[str, set[str]] = defaultdict(set)  # normalised path -> stages

    def record(self, obj, base: str, ctx: dict, rules: list[Rule], ignore=()) -> None:
        """Rows for one record (a dict at ``base`` with context ``ctx``)."""
        if not isinstance(obj, dict):
            return
        ign = [re.compile(p) for p in ignore]
        for rel, value, parent in leaves(obj):
            full = join(base, rel)
            for rule in rules:
                m = re.fullmatch(rule.pattern, rel)
                if m:
                    self._emit(rule, m, value, parent, full, ctx)
                    self.handled.add(full)
                    break
            else:
                if any(p.fullmatch(rel) for p in ign):
                    self.handled.add(full)

    def _emit(self, rule: Rule, m: re.Match, value, parent: dict, full: str, ctx: dict):
        v = fnum(value)
        if v is None:
            return
        groups = m.groups()
        err = fnum(parent.get(rule.err)) if rule.err else None
        if err is not None:
            err *= rule.err_scale
        notes = []
        if rule.note and parent.get(rule.note[0]) is True:
            notes.append(rule.note[1])
        if rule.err == "sem" and parent.get("sem_lower_bound") is True:
            notes.append("SEM is a lower bound")
        self.add(
            ctx,
            rule.prop,
            rule.quantity.format(*groups, parent=parent),
            v,
            err,
            rule.err_kind if err is not None else "",
            rule.unit,
            full,
            axis=rule.axis.format(*groups, parent=parent) if rule.axis else None,
            note="; ".join(notes),
        )

    def add(self, ctx, prop, quantity, value, err, err_kind, unit, source, axis=None, note=""):
        row = {c: "" for c in LONG_COLUMNS} | ctx
        if axis:
            row["axis_or_layer"] = axis
        row |= {
            "property": prop,
            "quantity": quantity,
            "value": value,
            "err": "" if err is None else err,
            "err_kind": err_kind if err is not None else "",
            "unit": unit,
            "note": note,
            "source_key": source,
        }
        self.rows.append(row)

    def finish_file(self, data: dict, stage: str) -> None:
        """Record numeric keys of this file that no rule or ignore pattern covered."""
        for path, _, _ in leaves(data):
            if path not in self.handled and not GLOBAL_IGNORE.search(path):
                self.unmapped[normalise(path)].add(stage)
        self.handled = set()


# --------------------------------------------------------------------------- per kind


def tval(x) -> str:
    v = fnum(x)
    return "" if v is None else f"{round(v, 3):g}"


def rate(x) -> str:
    v = fnum(x)
    return "" if v is None else f"{v:g}"


def window(ctx: dict, w) -> dict:
    if isinstance(w, list) and len(w) == 2:
        return ctx | {"T_lo_C": tval(w[0]), "T_hi_C": tval(w[1])}
    return ctx


def add_kappa_k(ex: Exporter, start: int) -> None:
    """K = 1/κ_T (error propagated) next to every κ_T row emitted since ``start``."""
    for row in list(ex.rows[start:]):
        if row["property"] == KAPPA and row["value"]:
            k = 1.0 / row["value"]
            err = row["err"] * k * k if row["err"] != "" else None
            ctx = {c: row[c] for c in WIDE_KEY}
            ex.add(
                ctx,
                BULK_K,
                "K = 1/kappa_T",
                k,
                err,
                row["err_kind"],
                "GPa",
                row["source_key"] + " (1/x)",
                note=row["note"],
            )


def export_sweep(ex: Exporter, d: dict, ctx: dict) -> None:
    segs = d.get("segments") or []
    seg_ctx = {}
    for i, s in enumerate(segs):
        c = ctx | {"segment": s.get("name", f"seg {i + 1}"), "T_C": tval(s.get("t_set_c"))}
        seg_ctx[s.get("index")] = c
        ex.record(s, f"segments[{i}]", c, BULK_STATS, [r"stats\..*", r"done"])
    for key in ("holds", "steps"):
        for j, e in enumerate(d.get(key) or []):
            c = seg_ctx.get(e.get("index")) or ctx | {
                "segment": f"{key} {e.get('index')}",
                "T_C": tval(e.get("t_c")),
            }
            n = len(ex.rows)
            ex.record(
                e,
                f"{key}[{j}]",
                c,
                KAPPA_RULES + prefixed("traj.", TRAJ_RULES),
                under("traj.", TRAJ_IGNORE),
            )
            add_kappa_k(ex, n)
    fits = d.get("fits") or {}
    for k, f in enumerate(fits.get("alpha_V") or []):
        c = window(ctx | {"segment": "fit"}, f.get("window_c"))
        ex.record(
            f,
            f"fits.alpha_V[{k}]",
            c,
            [
                Rule(r"alpha_V_per_K", ALPHA_V, "alpha_V", "1/K", "err", "fit_err"),
                Rule(
                    r"alpha_L_per_K",
                    ALPHA_L,
                    "alpha_L = alpha_V/3",
                    "1/K",
                    "err",
                    "fit_err",
                    err_scale=1 / 3,
                ),
            ],
        )
    for k, f in enumerate(fits.get("cp") or []):
        c = window(ctx | {"segment": "fit"}, f.get("window_c"))
        ex.record(
            f,
            f"fits.cp[{k}]",
            c,
            [
                Rule(r"cp_J_gK", CP, "Cp (classical)", "J/(g K)", "err", "fit_err"),
                Rule(r"cp_kcal_molK", CP, "Cp (classical, whole system)", "kcal/(mol K)"),
            ],
        )


def hold_ctx(d: dict, ctx: dict) -> dict:
    return ctx | {"segment": "hold", "T_C": tval(d.get("t_c"))}


def export_hold(ex: Exporter, d: dict, ctx: dict) -> None:
    c = hold_ctx(d, ctx)
    n = len(ex.rows)
    ex.record(
        d,
        "",
        c,
        BULK_STATS + KAPPA_RULES + prefixed("traj.", TRAJ_RULES),
        [r"stats\..*", *under("traj.", TRAJ_IGNORE)],
    )
    add_kappa_k(ex, n)


def export_pore(ex: Exporter, d: dict, ctx: dict) -> None:
    segs = d.get("segments") or []
    seg_ctx = {}
    seg_ignore = [
        r"stats\.(density|volume|enthalpy)\.\w+",  # box (film + vacuum) values of an NVT slab
        *under("profile.", PROFILE_IGNORE),
        r"profile\.drift\..*",
    ]
    for i, s in enumerate(segs):
        c = ctx | {"segment": s.get("name", f"seg {i + 1}"), "T_C": tval(s.get("t_set_c"))}
        if s.get("index") is not None:
            seg_ctx[s["index"]] = c
        ex.record(
            s, f"segments[{i}]", c, FILM_STATS + prefixed("profile.", PROFILE_RULES), seg_ignore
        )
    for j, h in enumerate(d.get("holds") or []):
        c = seg_ctx.get(h.get("index")) or ctx | {
            "segment": f"hold {h.get('index')}",
            "T_C": tval(h.get("t_c")),
        }
        ex.record(
            h,
            f"holds[{j}]",
            c,
            prefixed("traj.", PORE_TRAJ_RULES) + prefixed("film.", TRAJ_RULES, axis="film"),
            under("traj.", PORE_TRAJ_IGNORE) + under("film.", TRAJ_IGNORE),
        )
    fits = d.get("fits") or {}
    for branch in ("sweep", "cool"):
        f = fits.get(branch)
        if isinstance(f, dict):
            c = window(ctx | {"segment": f"fit ({branch} branch)"}, f.get("window_c"))
            ex.record(
                f,
                f"fits.{branch}",
                c,
                [
                    Rule(r"dgamma_dT_mN_mK", DGDT, "dgamma/dT", "mN/(m K)", "err", "fit_err"),
                    Rule(r"gamma_25c_mN_m", DGDT, "gamma(25 C) from the fit", "mN/m"),
                ],
            )
    th = d.get("thermal") or {}
    for k, a in enumerate(th.get("alpha") or []):
        c = window(ctx | {"segment": "fit"}, a.get("window_c"))
        ex.record(
            a,
            f"thermal.alpha[{k}]",
            c,
            [
                Rule(r"alpha_z_per_K", ALPHA_Z, "alpha_z", "1/K", "alpha_z_err", "fit_err"),
                Rule(r"alpha_V_film_per_K", ALPHA_Z, "alpha_V(film) = alpha_z + 2 alpha_L", "1/K"),
            ],
            [r"alpha_L_per_K|alpha_z_err(_unscaled)?|bulk_alpha_V_(per_K|err)|h_mean_A"],
        )
    for k, cv in enumerate(th.get("cv") or []):
        c = window(ctx | {"segment": "fit"}, cv.get("window_c"))
        ex.record(
            cv,
            f"thermal.cv[{k}]",
            c,
            [Rule(r"cv_J_gK", CV, "Cv (film)", "J/(g K)", "err", "fit_err")],
            [r"bulk_cp_(J_gK|err)"],
        )
    for k, p in enumerate(th.get("points") or []):
        c = seg_ctx.get(p.get("index")) or ctx | {
            "segment": f"{p.get('kind', 'point')} {p.get('index')}",
            "T_C": tval(p.get("t_c")),
        }
        ex.record(
            p,
            f"thermal.points[{k}]",
            c,
            [
                ms("e_s_mJ_m2", E_S, "e_s", "mJ/m²"),
                Rule(r"gamma_minus_TdgdT", E_S, "gamma - T dgamma/dT (check)", "mJ/m²"),
            ],
            [r"(pe|etotal|gamma|plateau|film_gibbs_A|bulk_density)\.\w+|area_A2|lx_A"],
        )
    se = th.get("surface_entropy_mJ_m2K")
    if isinstance(se, dict):
        c = window(
            ctx | {"segment": "fit (sweep branch)"}, (fits.get("sweep") or {}).get("window_c")
        )
        ex.record(
            se,
            "thermal.surface_entropy_mJ_m2K",
            c,
            [Rule(r"mean", S_ENT, "-dgamma/dT", "mJ/(m² K)", "err", "fit_err")],
        )
    ex.record(d.get("pore"), "pore", ctx, [], [r".*"])  # build geometry: inputs, not results


def export_hole(ex: Exporter, d: dict, ctx: dict) -> None:
    c = ctx | {"segment": "production", "T_C": tval(d.get("t_c"))}
    ex.record(d, "", c, HOLE_RULES, HOLE_IGNORE + [r"per_segment\[\d+\]\..*"])
    frames = d.get("frames") or []
    prod = [(i, f) for i, f in enumerate(frames) if f.get("phase") == "production"]
    if prod:
        (i0, f0), (i1, f1) = prod[0], prod[-1]
        for i, f, label in ((i0, f0, "at t0"), (i1, f1, "at the end")):
            if fnum(f.get("area")) is not None:
                ex.add(c, AREA, f"A {label}", f["area"], None, "", "Å²", f"frames[{i}].area")
            if fnum(f.get("drift")) is not None:
                ex.add(
                    c,
                    DRIFT,
                    f"centre drift {label}",
                    f["drift"],
                    None,
                    "",
                    "Å",
                    f"frames[{i}].drift",
                )
        drifts = [(fnum(f.get("drift")), i) for i, f in prod if fnum(f.get("drift")) is not None]
        if drifts:
            v, i = max(drifts)
            ex.add(
                c,
                DRIFT,
                "centre drift (max)",
                v,
                None,
                "",
                "Å",
                f"max over production frames[].drift (frames[{i}])",
            )
    for k, s in enumerate(d.get("per_segment") or []):
        sc = ctx | {
            "segment": f"seg {s.get('index')} {s.get('kind', '')}".strip(),
            "T_C": tval(s.get("t_c")),
        }
        ex.record(s, f"per_segment[{k}]", sc, HOLE_SEGMENT_RULES, [r"start_ns|end_ns|frames"])


def export_tensile(ex: Exporter, d: dict, ctx: dict) -> None:
    for i, r in enumerate(d.get("runs") or []):
        rc = ctx | {"T_C": tval(r.get("t_c")), "strain_rate_per_s": rate(r.get("rate_per_s"))}
        for j, a in enumerate(r.get("axes") or []):
            ac = rc | {"axis_or_layer": a.get("axis", str(j))}
            base = f"runs[{i}].axes[{j}]"
            ex.record(
                a,
                base,
                ac,
                TENSILE_AXIS_RULES,
                [r"E_err_MPa|E_intercept_MPa|fit_max|fit_rows|temp_mean_K"],
            )
            sec = ((a.get("curves") or {}).get("nu_secant")) or []
            strain = ((a.get("curves") or {}).get("strain")) or []
            last = [k for k, v in enumerate(sec) if fnum(v) is not None]
            if last:
                k = last[-1]
                e = fnum(strain[k]) if k < len(strain) else None
                ex.add(
                    ac,
                    NU_SEC,
                    "nu_secant at the last strain",
                    sec[k],
                    None,
                    "",
                    "",
                    f"{base}.curves.nu_secant[{k}]",
                    note="" if e is None else f"strain {e:.3g}",
                )
        ex.record(
            r.get("summary"),
            f"runs[{i}].summary",
            rc | {"axis_or_layer": "mean ± SD over axes"},
            TENSILE_SUMMARY_RULES,
        )
        ex.record(r, f"runs[{i}]", rc, [], [r"strain_max|rate_per_s"])
    for i, p in enumerate(d.get("pooled") or []):
        pc = ctx | {
            "T_C": tval(p.get("t_c")),
            "strain_rate_per_s": rate(p.get("rate_per_s")),
            "axis_or_layer": "pooled mean ± SD (" + ", ".join(p.get("runs") or []) + ")",
        }
        ex.record(p.get("summary"), f"pooled[{i}].summary", pc, TENSILE_SUMMARY_RULES)
    ex.record(d, "", ctx, [], [r"fit_max|smooth_strain|flow_window.*"])


EXPORTERS = {
    "sweep": export_sweep,
    "extend": export_hold,
    "diffuse": export_hold,
    "pore": export_pore,
    "hole": export_hole,
    "tensile": export_tensile,
}


# --------------------------------------------------------------------------- progress.json

PROGRESS = "progress.json"


def export_hysteresis(ex: Exporter, prog: dict, ctx: dict) -> None:
    """Per-T cooling vs sweep densities and the largest |delta_pct| (null deltas skipped)."""
    best = None
    for i, h in enumerate(prog.get("hysteresis") or []):
        if not isinstance(h, dict) or fnum(h.get("delta_pct")) is None:
            continue
        t_k = fnum(h.get("t_k"))
        c = ctx | {"segment": "cool vs sweep", "T_C": "" if t_k is None else tval(t_k - 273.15)}
        src = f"{PROGRESS}:hysteresis[{i}]"
        sem = fnum(h.get("rho_cool_sem"))
        for key, quantity, unit, err in (
            ("rho_cool", "rho (cooling)", "g/cm³", sem),
            ("rho_sweep", "rho (sweep)", "g/cm³", None),
            ("delta_pct", "delta_pct = (rho_cool - rho_sweep)/rho_sweep", "%", None),
        ):
            v = fnum(h.get(key))
            if v is not None:
                ex.add(c, HYST, quantity, v, err, "sem", unit, f"{src}.{key}")
        d = fnum(h["delta_pct"])
        if best is None or abs(d) > abs(best[0]):
            best = (d, i, c["T_C"])
    if best is not None:
        d, i, t = best
        ex.add(
            ctx | {"segment": "cool vs sweep"},
            HYST,
            "max |delta_pct|",
            abs(d),
            None,
            "",
            "%",
            f"max |{PROGRESS}:hysteresis[].delta_pct| (hysteresis[{i}])",
            note=f"at {t} C, delta_pct {d:+.4g}",
        )


def export_eta_rouse(ex: Exporter, prog: dict, ctx: dict) -> None:
    d_com = (prog.get("hold") or {}).get("d_com") or {}
    v = fnum(d_com.get("eta_rouse_pa_s")) if isinstance(d_com, dict) else None
    if v is not None:
        ex.add(ctx, ETA_R, "eta_R", v, None, "", "Pa·s", f"{PROGRESS}:hold.d_com.eta_rouse_pa_s")


def load_progress(runs_dir: Path | None, sid: str, stage: str) -> dict | None:
    if runs_dir is None:
        return None
    try:
        d = json.loads((runs_dir / sid / stage / PROGRESS).read_text())
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def export_progress(ex: Exporter, runs_dir: Path | None, data: dict, ctx: dict) -> None:
    """Rows from the run's progress.json for an analysed (system, stage)."""
    sk, stage = ctx["stage_kind"], ctx["stage"]
    if sk not in ("sweep", "extend", "diffuse") or (sk == "sweep" and stage != "sweep"):
        return
    prog = load_progress(runs_dir, ctx["system"], stage)
    if prog is None:
        return
    if sk == "sweep":
        export_hysteresis(ex, prog, ctx)
    else:
        export_eta_rouse(ex, prog, hold_ctx(data, ctx))


# --------------------------------------------------------------------------- metadata


def load_yaml(path: Path) -> dict | None:
    try:
        d = yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError):
        return None
    return d if isinstance(d, dict) else None


def system_meta(sid: str, man: dict | None) -> dict:
    """Resolution, polymer, kind (amorph / pore / hole) from the manifest, else the id."""
    parts = sid.split("_")
    man = man or {}
    if isinstance(man.get("hole"), dict):
        kind = "hole"
    elif isinstance(man.get("pore"), dict):
        kind = "pore"
    else:
        kind = parts[2] if len(parts) > 2 else ""
    return {
        "resolution": man.get("resolution") or (parts[1] if len(parts) > 1 else ""),
        "polymer": man.get("polymer") or (parts[0] if parts else ""),
        "kind": kind,
    }


def stage_kind(stage: str) -> str | None:
    return next((k for k in STAGE_KINDS if stage == k or stage.startswith(k + "_")), None)


# --------------------------------------------------------------------------- output


def export(analysis_dir: Path, systems_dir: Path, runs_dir: Path | None = None) -> Exporter:
    ex = Exporter()
    for f in sorted(analysis_dir.glob("*/*/results.json")):
        sid, stage = f.parent.parent.name, f.parent.name
        sk = stage_kind(stage)
        if sk is None:
            print(f"skipped (unknown stage kind): {f}", file=sys.stderr)
            continue
        try:
            data = json.loads(f.read_text())
        except (OSError, ValueError) as e:
            print(f"skipped (unreadable): {f}: {e}", file=sys.stderr)
            continue
        meta = system_meta(sid, load_yaml(systems_dir / sid / "manifest.yaml"))
        ctx = {"system": sid, **meta, "stage": stage, "stage_kind": sk}
        EXPORTERS[sk](ex, data, ctx)
        ex.finish_file(data, stage)
        export_progress(ex, runs_dir, data, ctx)
    return ex


def wide_rows(rows: list[dict]) -> tuple[list[str], list[dict]]:
    groups: dict[tuple, dict] = {}
    columns: dict[str, None] = {}
    for r in rows:
        key = tuple(r[c] for c in WIDE_KEY)
        col = f"{r['property']}: {r['quantity']}" + (f" [{r['unit']}]" if r["unit"] else "")
        columns.setdefault(col)
        groups.setdefault(key, dict(zip(WIDE_KEY, key, strict=True)))[col] = r["value"]
    return WIDE_KEY + list(columns), list(groups.values())


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, restval="")
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--analysis-dir", type=Path, default=ROOT / "results" / "analysis")
    ap.add_argument("--systems", type=Path, default=ROOT / "systems")
    ap.add_argument("--runs-dir", type=Path, default=ROOT / "results" / "runs")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "results")
    args = ap.parse_args(argv)

    ex = export(args.analysis_dir, args.systems, args.runs_dir)
    long_path = args.out_dir / "property_values.csv"
    wide_path = args.out_dir / "property_values_wide.csv"
    write_csv(long_path, LONG_COLUMNS, ex.rows)
    cols, wide = wide_rows(ex.rows)
    write_csv(wide_path, cols, wide)
    print(f"{long_path}: {len(ex.rows)} rows")
    print(f"{wide_path}: {len(wide)} rows x {len(cols)} columns")
    counts = Counter(r["property"] for r in ex.rows)
    print(f"{len(counts)} properties with values")
    if ex.unmapped:
        print("unmapped numeric keys (not exported):")
        for path, stages in sorted(ex.unmapped.items()):
            print(
                f"  {path}  ({', '.join(sorted(stages)[:3])}{', ...' if len(stages) > 3 else ''})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
