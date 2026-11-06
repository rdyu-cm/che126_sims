"""Result figures from the committed analysis outputs (CG/UA/AA PE and iPP, 25-160 C).

    uv run --frozen python scripts/presentation_figures.py [--analysis DIR] [--systems DIR]
        [--runs DIR ...] [--out DIR] [--only fig1 ...] [--no-render] [--hole-preview DIR]

Writes ``<out>/<name>.png`` (300 dpi), ``.pdf`` and ``.svg`` plus ``<out>/README.md`` (one
caption per figure) into ``results/presentation/`` by default (appendix figures in
``<out>/appendix/``):

- ``fig1_models``: PyMOL renders of one PE segment at AA / UA / CG resolution and of a CG
  bulk box, the simulation workflow, and the system-size table;
- ``fig2_equilibration``: 500 K chain relaxation (end-to-end ACF, COM MSD / Rg^2), the
  sweep density trace, pore gamma running means; appendix ``fig2_1_cn_sem`` (C_n plateau
  block means, block SEM vs block length);
- ``fig3_thermo``: rho(T), local alpha_V(T), kappa_T, cooling-vs-heating hysteresis, against
  experiment; appendix ``fig3_1_cp_chain_length`` (classical Cp, C1500 vs C240) and
  ``fig3_2_convergence`` (hold running-mean density and kappa_T vs time);
- ``fig4_chains``: Rg and C_n vs T, C_n(n) (with the 5 ns sweep steps when the sweep
  results.json has ``steps``); appendix ``fig4_1_ree_length`` (R_ee vs T, C240 vs C1500
  <R_ee^2>/M, ordered-site fraction);
- ``fig5_pore``: slit-pore render, gamma(T), segment MSD by layer, bond orientation;
  appendix ``fig5_1_pore_checks`` (rho vs z - z_Gibbs, chain shape by layer, interfacial
  width);
- ``fig6_dynamics``: D_COM vs T, tau_ee / tau_1 (CG x 4.07 ≈ real time); appendix
  ``fig6_1_dynamics_curves`` (segment MSD, long-hold COM MSD, P2 times, Rouse spectrum);
- ``fig7_mechanics``: CG tensile stress-strain, peak/flow stress, E_app;
- ``fig8_holes``: cylindrical-hole snapshots, R_eff(t), R(z), closure vs R/h (pending
  placeholders until ``sepsim analyze hole`` results exist).

Inputs: ``<analysis>/<system>/<stage>/results.json``, ``systems/*/manifest.yaml`` and
``data.lmp``, the run ``progress.json`` copies (``results/run_sidecars``,
``results/progress/rdyu-rog``) and, where present locally, ``results/runs`` snapshots
(``hold_<T>C.data``, extend snapshots). Series are found by system id
(``<polymer>_<res>_amorph_...``, ``..._pore_w5nm_...``, ``..._hole_...``), so UA/AA and iPP
results appear once their results.json exist. Colour = resolution (CG blue, UA vermillion,
AA green), marker = polymer (PE circle, iPP square), black = experiment; in panels resolved
by temperature, colour = T (25 C dark -> 160 C orange, 500 K grey) and line style =
resolution (CG solid, UA dashed, AA dotted). Molecular renders use PyMOL (``pymol`` on
PATH) and are cached in ``<out>/renders/``.
"""

from __future__ import annotations

import argparse
import colorsys
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import itertools

import pymol_render as pr
import summarize_systems as ss
import validity

from sepsim.analysis.stats import timeseries_mean
from sepsim.analysis.thermo import isothermal_compressibility, thermal_expansion
from sepsim.build.datafile import read_data_file

ROOT = ss.ROOT
FORMATS = ("png", "pdf", "svg")
DPI = 300
FIG23 = (13.0, 7.8)  # 2 x 3 panels
FIG33 = (13.0, 11.6)  # 3 x 3 panels
FIG22 = (11.0, 8.0)  # 2 x 2 panels
FIG22L = (11.0, 8.9)  # 2 x 2 panels below a shared legend row
FIG12 = (11.0, 4.6)  # 1 x 2 appendix panels
FIG13 = (15.0, 5.6)  # 1 x 3 panels below a shared legend row
APPENDIX = "appendix"  # appendix figures: <out>/appendix/fig<N>_<k>_<name>.*
CG_TIME_FACTOR = 4.07  # SDK PE dynamics are ~4.07x faster than real PE (Hall et al. 2019)
INV_E = float(np.exp(-1.0))
HOLD_TS = (25.0, 90.0, 130.0, 160.0)
T500_C = 226.85
GREY_500K = "0.5"
A2PS_TO_CM2S = 1e-4  # 1 A^2/ps = 1e-4 cm^2/s
CH2_G = 14.027

RES_COLOR = {"cg": "#0072B2", "ua": "#D55E00", "aa": "#009E73"}  # Okabe-Ito
RES_NAME = {"cg": "CG", "ua": "UA", "aa": "AA"}
RES_LS = {"cg": "-", "ua": "--", "aa": ":"}
POLY_MARKER = {"pe": "o", "ipp": "s"}
POLY_NAME = ss.POLYMER_NAME
EXP_KW = {"color": "black", "zorder": 1}

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 12,
        "legend.fontsize": 9.5,
        "legend.title_fontsize": 9.5,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "lines.linewidth": 2.0,
        "lines.markersize": 6.5,
        "errorbar.capsize": 2.5,
        "legend.frameon": False,
        "legend.handlelength": 1.8,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    }
)


# ------------------------------------------------------------------ experiment (sourced)
# Values copied from docs/experiment_comparison.md ([V] read from the source, [D] derived);
# add rows here (e.g. iPP) when that document gains them. Never invent values.
EXPERIMENT = {
    "pe": {
        "density": {  # amorphous / melt PE, g/cm^3; (T_C, rho, half range)
            "points": [(25.0, 0.852, 0.0), (90.0, 0.814, 0.0), (130.0, 0.790, 0.0)]
            + [(160.0, 0.7775, 0.0035)],
            "source": "ATHAS amorphous line, SANS densities, Tait fit (Gaur & Wunderlich"
            " 1981; Padilha Junior et al. 2015)",
        },
        # ATHAS amorphous PE: 0.8519 g/cm^3 at 298 K and 0.7835 at Tm0 = 414.6 K
        "density_athas": ((298.0, 0.8519), (414.6, 0.7835)),
        "alpha_V": {  # 1e-4 / K over 25-160 C, [D]
            "band": (7.0, 7.5),
            "window": (25.0, 160.0),
            "source": "SANS densities, Tait fit [D]",
        },
        "kappa_T": {  # GPa^-1, [D] from the Tait fit of Sato PVT data
            "points": [(130.0, 0.94), (160.0, 1.08)],
            "source": "Tait fit of Sato PVT data (Padilha Junior et al. 2015) [D]",
        },
        # ATHAS melt Cp per repeat unit: a*T + b J/mol/K, unit mass g/mol [V]
        "cp_athas": {"a": 0.04325, "b": 17.919, "unit_g": 14.027, "source": "ATHAS PE"},
        "gamma_line": {  # LLDPE melt: gamma = a + b * t(C), mN/m [V]
            "a": 39.05,
            "b": -0.0725,
            "source": "LLDPE melt, Moreira et al. 2003",
        },
        "D_com": {  # cm^2/s, short PE melt, read from a graph (+-30 %)
            "t_c": 175.0,
            "value": 1.8e-7,
            "rel_err": 0.30,
            "source": "Pearson et al. 1987",
        },
        # C_inf (Fetters, Lohse, Colby 2007) [V]: 8.26 at 25 C, 7.38 at 140 C
        "c_inf": [(25.0, 8.26), (140.0, 7.38)],
        "c_melt_500k": 6.7,  # D37 melt reference at 500 K
        # <R^2>/M = 1.25 A^2 mol/g at 140 C (Fetters et al.) [V]
        "r2_over_m": {"t_c": 140.0, "value": 1.25},
        # C240 Rg at 140 C, 25-26.5 A [D from <R^2>/M]
        "rg_c240": {"t_c": 140.0, "lo": 25.0, "hi": 26.5},
        # amorphous rubber E ~ 3 G_e, G_e = 2.6 MPa at 140 C (Fetters, Lohse, Colby 2007)
        "E_rubber_MPa": 8.0,
    },
    "ipp": {
        "cp_athas": {"a": 0.151291, "b": 42.956, "unit_g": 42.080, "source": "ATHAS iPP"},
        "c_melt_500k": 6.15,
    },
}


# ------------------------------------------------------------------ series by system id
ID_RE = re.compile(
    r"^(?P<polymer>[a-z]+)_(?P<res>cg|ua|aa)_(?P<kind>[a-z0-9]+(?:_[rw][0-9.]+nm)?"
    r"(?:_[0-9]+C)?)_n(?P<n>\d+)_c(?P<c>\d+)_s(?P<seed>\d+)(?P<suffix>.*)$"
)


def parse_id(sid: str) -> dict | None:
    """polymer, resolution, kind (bulk/pore/wide pore/hole), chains, carbons, suffix."""
    m = ID_RE.match(sid)
    if not m:
        return None
    k = m["kind"]
    if k.startswith("amorph"):
        kind = "bulk"
    elif k.startswith("pore500k"):
        kind = "wide_pore"
    elif k.startswith("pore"):
        kind = "pore"
    elif k.startswith("hole"):
        kind = "hole"
    else:
        kind = k
    w = re.search(r"_w([0-9.]+)nm", sid)
    return {
        "polymer": m["polymer"],
        "res": m["res"],
        "kind": kind,
        "n": int(m["n"]),
        "c": int(m["c"]),
        "suffix": m["suffix"],
        "width_nm": float(w[1]) if w else None,
    }


def series_info(sid: str) -> dict | None:
    """Plot identity of a system: label and style. Primary = 40 x C240 (UA-derived AA
    included); other chain lengths / replicated boxes are drawn open and dashed."""
    p = parse_id(sid)
    if p is None:
        return None
    rep = "rep" in p["suffix"]
    variant = []
    if p["c"] != 240:
        variant.append(f"C{p['c']}")
    cg_c240 = p["res"] == "cg" and p["c"] == 240  # named "CG PE C240" next to C1500
    other_box = rep or p["n"] != 40
    primary = not variant and not other_box
    base = f"{RES_NAME[p['res']]} {POLY_NAME.get(p['polymer'], p['polymer'])}"
    if cg_c240:
        base += " C240"
    if variant:
        base += " " + ", ".join(variant)
    chains = f"({p['n']} chains)"
    # box size only in the label of the non-40-chain boxes; chains_label always has it
    label = f"{base} {chains}" if other_box else base
    color = RES_COLOR.get(p["res"], "0.4")
    return p | {
        "sid": sid,
        "label": label,
        "base": base,
        "chains_label": f"{base} {chains}",
        "primary": primary,
        "color": color,
        "marker": POLY_MARKER.get(p["polymer"], "D"),
        "mfc": color if primary else "white",
        "ls": "-" if primary else "--",
        "rls": RES_LS.get(p["res"], "-"),
    }


def pore_label(s: dict, suffix: str = "") -> str:
    """Pore series label with width and chain count, e.g. "CG PE C240 5 nm pore (40
    chains)" (``suffix`` goes after "pore", e.g. " film")."""
    w = f" {s['width_nm']:g} nm" if s.get("width_nm") else ""
    return f"{s['base']}{w} pore{suffix} ({s['n']} chains)"


def _order(sid: str) -> tuple:
    p = parse_id(sid) or {}
    return (
        ss.POLYMER_ORDER.get(p.get("polymer"), 9),
        ss.RESOLUTION_ORDER.get(p.get("res"), 9),
        0 if (series_info(sid) or {}).get("primary") else 1,
        p.get("c", 0),
        p.get("n", 0),
        sid,
    )


def superseded(sid: str, ids) -> bool:
    """A grown AA box is superseded by its ua2aa ``_from_ua`` counterpart (D47)."""
    return f"{sid}_from_ua" in ids


def find_series(data: dict, kind: str, stage: str) -> list[dict]:
    """Series of systems of ``kind`` that have ``<analysis>/<sid>/<stage>/results.json``
    (``stage`` may be a prefix ending in ``_``, e.g. ``tensile_``)."""
    ana = data["analysis"]
    out = []
    for sid in sorted(ana, key=_order):
        info = series_info(sid)
        if info is None or info["kind"] != kind or superseded(sid, ana):
            continue
        if stage.endswith("_"):
            stages = {k: v for k, v in ana[sid].items() if k.startswith(stage)}
        else:
            stages = {stage: ana[sid][stage]} if stage in ana[sid] else {}
        if stages:
            out.append(info | {"results": stages})
    return out


def bulk_systems(data: dict, rep: bool = False, derived: bool = True) -> list[dict]:
    """Every known bulk system (analysis, manifest or run), not superseded; replicated
    boxes only with ``rep``; ``_from_ua`` conversions only with ``derived``."""
    ids = data["ids"] | set(data["runs"])
    out = []
    for sid in sorted(ids, key=_order):
        s = series_info(sid)
        if not s or s["kind"] != "bulk" or superseded(sid, ids):
            continue
        if "rep" in s["suffix"] and not rep:
            continue
        if s["suffix"].startswith("_from") and not derived:
            continue
        out.append(s)
    return out


# ------------------------------------------------------------------ helpers
def t_color(t_c: float) -> tuple | str:
    """Temperature colour (25 C dark violet .. 160 C orange, 500 K grey), shared by every
    T legend."""
    if float(t_c) > 200.0:
        return GREY_500K
    frac = (float(t_c) - 25.0) / (160.0 - 25.0)
    return plt.get_cmap("plasma")(0.08 + 0.72 * min(max(frac, 0.0), 1.0))


def t_label(t_c: float) -> str:
    return "500 K" if float(t_c) > 200.0 else f"{float(t_c):g} °C"


def panel_label(ax, letter: str, title: str = "") -> None:
    ax.set_title(f"({letter}) {title}".rstrip(), loc="left", fontweight="bold", fontsize=12)


def no_data(ax, msg: str, pending: bool = False) -> None:
    """Placeholder: grey dashed box with the reason (``pending``: data not produced yet)."""
    ax.text(
        0.5,
        0.5,
        ("PENDING\n" if pending else "") + msg,
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=10.5,
        color="0.35",
        wrap=True,
        bbox={"boxstyle": "round,pad=0.6", "fc": "0.965", "ec": "0.7", "ls": "--"},
    )
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def save(fig, out_dir: Path, name: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in FORMATS:
        p = out_dir / f"{name}.{ext}"
        fig.savefig(p, dpi=DPI if ext == "png" else 150, bbox_inches="tight")
        paths.append(p)
    plt.close(fig)
    return paths


def g(d, *keys, default=None):
    return ss.get(d, *keys, default=default)


def hold_segments(res: dict) -> list[dict]:
    return [s for s in res.get("segments") or [] if s.get("kind") == "hold"]


def main_bulk(data: dict) -> dict | None:
    """The representative bulk system: the first primary bulk sweep (PE, CG first)."""
    sweeps = [s for s in find_series(data, "bulk", "sweep") if s["primary"]]
    return sweeps[0] if sweeps else None


def _legend_handles(series: list[dict], extra: list | None = None, ls: bool = True) -> list:
    h = [
        Line2D(
            [],
            [],
            color=s["color"],
            marker=s["marker"],
            mfc=s["mfc"],
            ls=s["ls"] if ls else "",
            label=s["label"],
        )
        for s in series
    ]
    return h + (extra or [])


def _t_legend(ax, ts, loc="best", title="T", **kw) -> None:
    h = [Line2D([], [], color=t_color(t), lw=2.4, label=t_label(t)) for t in ts]
    leg = ax.legend(handles=h, loc=loc, title=title, **kw)
    ax.add_artist(leg)


def _res_ls_handles(resolutions) -> list:
    return [
        Line2D([], [], color="0.3", ls=RES_LS[r], label=RES_NAME[r])
        for r in ("cg", "ua", "aa")
        if r in resolutions
    ]


def fig_legend(fig, rows: list[list], **kw) -> None:
    """One shared legend above the panels, one row per list of handles (e.g. series, then
    the style keys); short rows are padded with blank entries."""
    rows = [r for r in rows if r]
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    blank = Line2D([], [], ls="", label=" ")
    grid = [r + [blank] * (ncols - len(r)) for r in rows]
    handles = [grid[i][c] for c in range(ncols) for i in range(len(grid))]  # column-major
    fig.legend(
        handles=handles,
        loc="outside upper center",
        ncols=ncols,
        fontsize=9.5,
        columnspacing=1.2,
        handletextpad=0.5,
        **kw,
    )


def legend_rows(handles: list, n: int) -> list[list]:
    """``handles`` cut into rows of ``n`` (for :func:`fig_legend`)."""
    return [handles[k : k + n] for k in range(0, len(handles), n)]


def _key(label: str, marker: str = "", ls: str = "", mfc: str = "0.3", **kw) -> Line2D:
    """Grey style-key handle (marker fill, line style) for a shared legend."""
    return Line2D(
        [], [], color="0.3", marker=marker or None, ls=ls or "", mfc=mfc, label=label, **kw
    )


def _fmt(x, spec=".3g") -> str:
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else format(x, spec)


def _tc_of(name: str) -> float | None:
    m = re.search(r"([0-9.]+) C\b", name)
    return float(m[1]) if m else None


def arrhenius_axes(ax, cg: bool, ticks=(25, 90, 130, 160, 227)) -> None:
    """1000/T x axis with a °C top axis; with ``cg`` a right axis in CG model time (the
    main axis carries CG x 4.07 ≈ real time)."""
    ax.set_yscale("log")
    ax.set_xlabel(r"1000 / T (K$^{-1}$)")
    ax.set_xlim(1.9, 3.45)
    top = ax.secondary_xaxis(
        "top",
        functions=(
            lambda v: 1000.0 / np.maximum(v, 1e-9) - 273.15,
            lambda c: 1000.0 / (np.asarray(c) + 273.15),
        ),
    )
    top.set_xticks(list(ticks))
    top.set_xticklabels([("500 K" if t > 200 else f"{t:g}") for t in ticks], fontsize=10)
    top.set_xlabel("T (°C)", fontsize=10.5)
    if cg:  # the main axis shows CG x 4.07 (Fig. 6 convention); right: CG model time
        right = ax.secondary_yaxis(
            "right", functions=(lambda v: v / CG_TIME_FACTOR, lambda v: v * CG_TIME_FACTOR)
        )
        right.set_ylabel("CG model time (ns)", fontsize=10.5)
        ax.spines["right"].set_visible(True)


# ------------------------------------------------------------------ data access
def runs_of(data: dict, sid: str) -> list[dict]:
    return ss.current_runs(data["runs"].get(sid, {}))


def hold500(sid: str, data: dict) -> dict | None:
    """500 K chain data of the combined prep hold + extension: curves from the extend
    analysis (``traj.curves``) if it has a trajectory, else from the extend (or prep) run's
    progress.json ``hold`` (``sepsim progress``)."""
    out: dict = {}
    runs = runs_of(data, sid)
    run = ss.latest(runs, "extend") or ss.latest(runs, "prep")
    hold = g(run, "progress", "hold") or {}
    if g(hold, "curves", "acf"):
        c = hold["curves"]
        rg2 = g(hold, "com_msd", "rg2_A2")
        out |= {
            "lag_ns": np.asarray(c["acf_lag_ns"], float),
            "acf": np.asarray(c["acf"], float),
            "t_1e_ns": g(hold, "ree_acf", "t_1e_ns"),
            "hold_ns": hold.get("hold_ns"),
            "msd_lag_ns": np.asarray(c.get("msd_lag_ns") or [], float),
            "msd_rg2": (np.asarray(c.get("msd_A2") or [], float) / rg2) if rg2 else None,
            "d47": hold.get("d47"),
            "cn_n": np.asarray(c.get("n_carbons") or [], float),
            "cn": np.asarray(c.get("c_n") or [], float),
            "plateau_t_ns": np.asarray(c.get("plateau_t_ns") or [], float),
            "plateau_t": np.asarray(c.get("plateau_t") or [], float),
            "boundaries_ns": hold.get("boundaries_ns") or [],
            "cn_plateau": g(hold, "msid", "plateau"),
            "cn_ref": g(hold, "msid", "reference"),
            "rg_A": float(np.sqrt(rg2)) if rg2 else None,
            "ree_A": (
                float(np.sqrt(g(hold, "ree_acf", "r2_mean_A2")))
                if g(hold, "ree_acf", "r2_mean_A2")
                else None
            ),
            "source": f"{sid}/{run['dir']}/progress.json (hold)",
            "density": ((g(run, "progress", "segments") or [{}])[0] or {}).get("stats"),
        }
    res = g(data["analysis"], sid, "extend")
    tr = g(res, "traj")
    if g(tr, "available") and g(tr, "curves", "ree_acf"):
        c = tr["curves"]
        rg2 = g(tr, "rg", "rg2_A2", "mean")
        out |= {
            "lag_ns": np.asarray(c["relax_lag_ps"], float) / 1000.0,
            "acf": np.asarray(c["ree_acf"], float),
            "t_1e_ns": (g(tr, "relaxation", "ree", "t_1e_ps") or np.nan) / 1000.0,
            "hold_ns": tr.get("hold_ns"),
            "source": f"results/analysis/{sid}/extend/results.json",
            "traj": tr,
            "rg_A": g(tr, "rg", "rg_A", "mean"),
            "ree_A": g(tr, "ree", "ree_A", "mean"),
            "ree2_A2": g(tr, "ree", "ree2_A2", "mean"),
            "cn_plateau": g(tr, "c_n", "plateau", "mean") or out.get("cn_plateau"),
        }
        if c.get("com_A2") and rg2:
            out["msd_lag_ns"] = np.asarray(c["com_lag_ps"], float) / 1000.0
            out["msd_rg2"] = np.asarray(c["com_A2"], float) / rg2
    if res and g(res, "stats", "density"):
        out["density"] = res["stats"]
    if not out:
        return None
    t1 = out.get("t_1e_ns")
    out["t_1e_ns"] = np.nan if t1 is None else float(t1)
    return out


def long_holds(data: dict, sid: str) -> list[dict]:
    """``diffuse_<T>C`` analyses (D53) with a trajectory, sorted by T."""
    ana = data["analysis"].get(sid, {})
    out = []
    for stage, res in ana.items():
        if stage.startswith("diffuse_") and res.get("t_c") is not None:
            out.append({"stage": stage, "t_c": float(res["t_c"]), "res": res})
    return sorted(out, key=lambda r: r["t_c"])


def sweep_holds(s: dict | None, data: dict) -> list[dict]:
    res = g(data["analysis"], s["sid"], "sweep") if s else None
    return [h for h in (res or {}).get("holds") or [] if g(h, "traj", "available")]


def sweep_steps(s: dict | None, data: dict) -> list[dict]:
    """The sweep's 5 ns steps with static chain results (results.json ``steps``: index,
    t_c, kappa, traj); empty for analyses that predate the per-step extension."""
    res = g(data["analysis"], s["sid"], "sweep") if s else None
    return [st for st in (res or {}).get("steps") or [] if g(st, "traj", "available")]


def relaxed(tr: dict) -> bool:
    """Chains moved at least their own size in the hold (COM MSD >= <Rg^2>)."""
    return (g(tr, "com_msd", "msd_rg2_end") or 0.0) >= validity.CHAIN_RELAXED


def mass_per_chain(s: dict) -> float:
    """g/mol of one chain: PE C_nH_{2n+2}; iPP (C3H6)_{n/3} + 2 H ends."""
    return s["c"] * CH2_G + 2 * 1.008


def validity_text(data: dict, sids: list[str], props: list[str]) -> str:
    """Per-system verdicts (scripts/validity.py) for ``props`` of the systems shown."""
    ctx = data.get("ctx")
    if ctx is None or not sids:
        return ""
    parts = []
    for sid in dict.fromkeys(sids):
        if sid not in ctx.get("meta", {}):
            continue
        try:
            v = validity.system_validity(sid, ctx)
        except Exception:  # noqa: BLE001, S112 - validity rules must never break the figures
            continue
        cells = []
        for k in props:
            c = v.get(k)
            if not c or c["verdict"] == validity.NA:
                continue
            txt = f"{validity.PROP_LABEL[k]} {c['verdict']}" + (" (flagged)" if c["flag"] else "")
            if c["verdict"] in (validity.TREND, validity.CORRECT, validity.NOT_MEANINGFUL):
                why = re.split(r";|\(", str(c.get("reason") or ""))[0].strip()
                if why:
                    txt += f" ({why})"
            cells.append(txt)
        if cells:
            label = (series_info(sid) or {}).get("label", sid)
            parts.append(f"{label} (`{sid}`): " + "; ".join(cells))
    if not parts:
        return ""
    return " **Validity** (scripts/validity.py): " + " | ".join(parts) + "."


# ------------------------------------------------------------------ snapshots
def chain_colors(mol: np.ndarray) -> np.ndarray:
    """Well-separated colour per molecule id (golden-ratio hue steps)."""
    ids, inv = np.unique(mol, return_inverse=True)
    pal = np.array(
        [colorsys.hsv_to_rgb((0.6 + 0.618034 * i) % 1.0, 0.7, 0.9) for i in range(len(ids))]
    )
    return pal[inv]


def gap_center(z, lo, length, bin_width=2.0, empty=0.1):
    """z of the middle of the largest low-density periodic run of the z histogram (the
    slit-pore gap), or None (same rule as scripts/ovito_view.gap_center, which needs OVITO)."""
    nbins = max(8, int(length / bin_width))
    counts, _ = np.histogram(np.mod(z - lo, length), bins=nbins, range=(0.0, length))
    low = counts <= empty * np.percentile(counts, 90)
    if low.all() or not low.any():
        return None
    start = int(np.argmin(low))
    ring = np.roll(low, -start)
    best_len, best_end, run = 0, 0, 0
    for i, v in enumerate(ring):
        run = run + 1 if v else 0
        if run > best_len:
            best_len, best_end = run, i
    mid = (best_end + 1 - best_len / 2 + start) * length / nbins
    return lo + mid % length


def read_snapshot(path: Path) -> dict:
    df = read_data_file(path)
    a = df.sorted_atoms()
    lo = np.array([b[0] for b in df.box])
    L = np.array([b[1] - b[0] for b in df.box])
    unw = df.unwrapped()
    pos = lo + np.mod(unw - lo, L)
    bonds = df.topology("Bonds")
    pairs = bonds[:, 2:4] - 1 if bonds.shape[1] >= 4 else np.zeros((0, 2), int)
    masses = {int(r[0]): float(r[1]) for r in df.sections.get("Masses", [])}
    return {
        "pos": pos,
        "unwrapped": unw,
        "mol": a[:, 1].astype(int),
        "type": a[:, 2].astype(int),
        "mass": np.array([masses.get(int(t), 0.0) for t in a[:, 2]]),
        "pairs": pairs,
        "lo": lo,
        "L": L,
        "path": path,
        "local_run": path.name != "data.lmp",
    }


def snapshot(sid: str, data: dict, stage: str, prefer: str = "hold_25C.data") -> dict | None:
    """Wrapped positions, molecule ids, bonds and box of a system: a local run snapshot
    (``<runs>/<sid>/<stage>/<prefer>``) if present, else ``systems/<sid>/data.lmp``."""
    cands = [Path(r) / sid / stage / prefer for r in data["run_roots"]]
    cands.append(data["systems_root"] / sid / "data.lmp")
    path = next((p for p in cands if p.is_file()), None)
    return read_snapshot(path) if path else None


def _short(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return "/".join(path.parts[-4:])


def rot_matrix(azim_deg: float, elev_deg: float) -> np.ndarray:
    """Camera rotation: turn about z by ``azim``, then tilt about x by ``elev`` (view from
    above the x-y plane at ``elev``)."""
    a, e = np.radians(azim_deg), np.radians(elev_deg)
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return rx @ rz


def _render_dir(data: dict) -> Path:
    return data["out"] / "renders"


def autocrop(img: np.ndarray, pad: float = 0.03) -> np.ndarray:
    """Crop the white margin of a render (keeps ``pad`` of the content size around it)."""
    rgb = img[..., :3]
    mask = (rgb < 0.97).any(axis=-1)
    if not mask.any():
        return img
    ys, xs = np.flatnonzero(mask.any(axis=1)), np.flatnonzero(mask.any(axis=0))
    py, px = int(pad * (ys[-1] - ys[0])) + 4, int(pad * (xs[-1] - xs[0])) + 4
    return img[
        max(ys[0] - py, 0) : min(ys[-1] + py + 1, img.shape[0]),
        max(xs[0] - px, 0) : min(xs[-1] + px + 1, img.shape[1]),
    ]


def show_render(ax, png: Path | None, status: str, title: str, letter: str, note: str = ""):
    panel_label(ax, letter, title)
    if png is None:
        no_data(ax, f"render not available\n({status})")
        return
    ax.imshow(autocrop(plt.imread(png)), interpolation="lanczos")
    ax.set_axis_off()
    if note:
        ax.text(
            0.0, -0.02, note, transform=ax.transAxes, ha="left", va="top", fontsize=9.5, color="0.3"
        )


# ================================================================== figure 1: models
SEG_CARBONS = 15
SIGMA_HALF = {"CH2": 1.975, "CH3": 1.875, "bead": 2.253}  # TraPPE-UA sigma/2; SDK CM sigma/2


def _min_image_chain(p: np.ndarray, L: np.ndarray) -> np.ndarray:
    """Make consecutive positions continuous (minimum image along the list)."""
    out = p.copy()
    for i in range(1, len(p)):
        d = out[i] - out[i - 1]
        out[i] = out[i - 1] + d - L * np.round(d / L)
    return out


def segment_models(data: dict) -> dict | None:
    """One PE segment (first chain, carbons 1-15, incl. the CH3 end) at AA, UA and CG
    resolution, rotated to its principal axes. AA: the ua2aa box (carbons at the UA
    positions, explicit H). UA: the ua2aa source snapshot if present locally (checked to
    coincide with the AA carbons), else the AA carbons (identical by construction, D32).
    CG: centres of the same carbons in groups of 3 (the SDK 3-carbon bead mapping)."""
    aa_sid = next(
        (
            s["sid"]
            for s in bulk_systems(data)
            if s["res"] == "aa" and s["polymer"] == "pe" and s["suffix"].startswith("_from_ua")
        ),
        None,
    )
    if aa_sid is None or not (data["systems_root"] / aa_sid / "data.lmp").is_file():
        return None
    aa = read_snapshot(data["systems_root"] / aa_sid / "data.lmp")
    L = aa["L"]
    heavy = aa["mass"] > 2.0
    mol1 = aa["mol"] == aa["mol"].min()
    cidx = np.flatnonzero(mol1 & heavy)[:SEG_CARBONS]
    cpos = _min_image_chain(aa["unwrapped"][cidx], L)
    cset = {int(i): k for k, i in enumerate(cidx)}
    hpos, hbond = [], []
    for a, b in aa["pairs"]:
        for c, h in ((int(a), int(b)), (int(b), int(a))):
            if c in cset and not heavy[h]:
                d = aa["unwrapped"][h] - aa["unwrapped"][c]
                d -= L * np.round(d / L)
                hpos.append(cpos[cset[c]] + d)
                hbond.append(cset[c])
    # UA source snapshot (same segment), if local
    src = g(data["systems"], aa_sid, "source") or {}
    ua_path, dev = None, None
    for r in data["run_roots"]:
        base = Path(r) / str(src.get("id", ""))
        if src.get("data_file") and base.is_dir():
            hit = sorted(base.glob(f"*/{src['data_file']}"))
            if hit:
                ua_path = hit[0]
                break
    if ua_path is not None:
        ua = read_snapshot(ua_path)
        uidx = np.flatnonzero(ua["mol"] == ua["mol"].min())[:SEG_CARBONS]
        upos = _min_image_chain(ua["unwrapped"][uidx], L)
        d = upos - cpos
        d -= d[0]
        dev = float(np.abs(d).max())
    c0 = cpos.mean(axis=0)
    _, _, vt = np.linalg.svd(cpos - c0)
    if np.linalg.det(vt) < 0:
        vt[2] *= -1
    rot = lambda p: (np.asarray(p) - c0) @ vt.T
    c = rot(cpos)
    h = rot(np.array(hpos)) if hpos else np.zeros((0, 3))
    beads = np.array([c[3 * k : 3 * k + 3].mean(axis=0) for k in range(SEG_CARBONS // 3)])
    return {
        "aa_sid": aa_sid,
        "ua_sid": src.get("id"),
        "carbons": c,
        "h": h,
        "h_bond": np.array(hbond, int),
        "beads": beads,
        "ua_path": ua_path,
        "matched": dev is not None and dev < 0.01,
        "dev_A": dev,
    }


def _seg_view(m: dict, size) -> list[str]:
    allp = np.vstack([m["carbons"], m["h"]]) if len(m["h"]) else m["carbons"]
    half_w = float(np.abs(allp[:, 0]).max()) + 3.0
    half_h = float(np.abs(allp[:, 1]).max()) + 3.0
    return pr.view_lines(half_w, half_h, *size, depth=40.0)


def render_segments(data: dict, m: dict) -> dict[str, tuple]:
    size = (1600, 800)
    n = len(m["carbons"])
    chain_b = np.array([[i, i + 1] for i in range(n - 1)])
    view = _seg_view(m, size)
    rgb = {k: matplotlib.colors.to_rgb(v) for k, v in RES_COLOR.items()}
    out = {}
    enabled = data.get("render", True)
    rdir = _render_dir(data)
    # AA: carbons + explicit hydrogens
    pos = np.vstack([m["carbons"], m["h"]])
    elem = ["C"] * n + ["H"] * len(m["h"])
    bonds = np.vstack([chain_b, np.c_[m["h_bond"], np.arange(n, n + len(m["h"]))]])
    files = {"aa.pdb": pr.pdb_text(pos, elem, np.ones(len(pos)), bonds)}
    body = pr.style_lines() + [
        "load aa.pdb, aa",
        "hide everything",
        "show sticks",
        "show spheres",
        "set stick_radius, 0.15",
        "set sphere_scale, 0.32",
        "set sphere_scale, 0.24, elem H",
        f"set_color aac, [{rgb['aa'][0]:.3f}, {rgb['aa'][1]:.3f}, {rgb['aa'][2]:.3f}]",
        "color aac, elem C",
        "color white, elem H",
        *view,
    ]
    out["aa"] = pr.render("seg_aa", files, body, rdir, size, enabled)
    # UA: CH2 / CH3 sites, faint CG bead outlines
    names = ["C3" if i == 0 else "C2" for i in range(n)]
    files = {
        "ua.pdb": pr.pdb_text(m["carbons"], "C", np.ones(n), chain_b, names=names),
        "map.pdb": pr.pdb_text(m["beads"], "C", np.ones(len(m["beads"]))),
    }
    body = pr.style_lines() + [
        "load ua.pdb, ua",
        "load map.pdb, cgmap",
        "hide everything",
        f"alter ua and name C2, vdw={SIGMA_HALF['CH2']}",
        f"alter ua and name C3, vdw={SIGMA_HALF['CH3']}",
        f"alter cgmap, vdw={SIGMA_HALF['bead'] * 1.25:.3f}",
        "rebuild",
        "show sticks, ua",
        "show spheres, ua",
        "set stick_radius, 0.3, ua",
        "set sphere_scale, 0.62, ua",
        f"set_color uac, [{rgb['ua'][0]:.3f}, {rgb['ua'][1]:.3f}, {rgb['ua'][2]:.3f}]",
        "set_color uac3, [0.62, 0.27, 0.0]",
        "color uac, ua",
        "color uac3, ua and name C3",
        "show spheres, cgmap",
        f"set_color cgc, [{rgb['cg'][0]:.3f}, {rgb['cg'][1]:.3f}, {rgb['cg'][2]:.3f}]",
        "color cgc, cgmap",
        "set sphere_transparency, 0.82, cgmap",
        *view,
    ]
    out["ua"] = pr.render("seg_ua", files, body, rdir, size, enabled)
    # CG: 3-carbon beads with the carbon backbone inside
    nb = len(m["beads"])
    bnames = ["CT"] + ["CM"] * (nb - 1)
    files = {
        "cg.pdb": pr.pdb_text(
            m["beads"], "C", np.ones(nb), [[i, i + 1] for i in range(nb - 1)], names=bnames
        ),
        "bb.pdb": pr.pdb_text(m["carbons"], "C", np.ones(n), chain_b),
    }
    body = pr.style_lines() + [
        "load cg.pdb, cg",
        "load bb.pdb, bb",
        "hide everything",
        f"alter cg, vdw={SIGMA_HALF['bead']}",
        "rebuild",
        "show sticks, cg",
        "show spheres, cg",
        "set stick_radius, 0.45, cg",
        "set sphere_scale, 0.9, cg",
        f"set_color cgc, [{rgb['cg'][0]:.3f}, {rgb['cg'][1]:.3f}, {rgb['cg'][2]:.3f}]",
        "set_color cgt, [0.0, 0.30, 0.55]",
        "color cgc, cg",
        "color cgt, cg and name CT",
        "set sphere_transparency, 0.45, cg",
        "show sticks, bb",
        "set stick_radius, 0.12, bb",
        "color grey40, bb",
        *view,
    ]
    out["cg"] = pr.render("seg_cg", files, body, rdir, size, enabled)
    return out


def bulk_render(data: dict, sid: str, snap: dict, name: str) -> tuple:
    """Perspective-like (orthoscopic, oblique) render of a wrapped bulk box, chains coloured."""
    size = (1200, 1050)
    rot = rot_matrix(32.0, -68.0)
    ctr = snap["lo"] + snap["L"] / 2
    pos = (snap["pos"] - ctr) @ rot.T
    corners = (pr.box_corners(snap["lo"], snap["lo"] + snap["L"]) - ctr) @ rot.T
    i, j = snap["pairs"].T
    ok = np.all(np.abs(snap["pos"][i] - snap["pos"][j]) < 0.5 * snap["L"], axis=1)
    resi = snap["mol"] - snap["mol"].min()
    cols = chain_colors(snap["mol"])
    pal = np.array([cols[np.flatnonzero(resi == k)[0]] for k in range(resi.max() + 1)])
    files = {"box.pdb": pr.pdb_text(pos, "C", resi, snap["pairs"][ok])}
    half_w = float(np.abs(corners[:, 0]).max()) + 4
    half_h = float(np.abs(corners[:, 1]).max()) + 4
    body = pr.style_lines(outline=False) + [
        "load box.pdb, box",
        "hide everything",
        f"alter box, vdw={SIGMA_HALF['bead']}",
        "rebuild",
        "show sticks",
        "show spheres",
        "set stick_radius, 0.7",
        "set sphere_scale, 0.42",
        *pr.color_lines("box", pal, np.arange(len(pal)), "ch"),
        *pr.cgo_cylinders("cell", pr.box_edges(corners), 0.45, (0, 0, 0)),
        "set ray_shadows, 1",
        *pr.view_lines(half_w, half_h, *size, depth=float(np.abs(corners).max()) + 30),
    ]
    return pr.render(name, files, body, _render_dir(data), size, data.get("render", True))


def _wf_box(ax, xy, w, h, text, fc, ec="0.25", fs=9.5, bold=False):
    x, y = xy
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.008,rounding_size=0.02",
            fc=fc,
            ec=ec,
            lw=1.2,
        )
    )
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else None)


def _wf_arrow(ax, p, q, **kw):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle="-|>", mutation_scale=13, lw=1.4, color=kw.pop("color", "0.25"), **kw
        )
    )


def _f1_workflow(ax) -> None:
    panel_label(ax, "e", "Workflow")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    main = "#E8F1F8"
    br = "#FBEFE6"
    xl, w, h = 0.245, 0.47, 0.14
    steps = [
        (0.90, "build amorphous box\n(AA: from relaxed UA)"),
        (0.69, "500 K melt hold (D47)\nACF < 1/e, MSD ≥ 2⟨R$_g^2$⟩"),
        (0.48, "step-cool 500 K → 25 °C"),
        (0.27, "heating sweep 25→160 °C\nholds 25/90/130/160 °C"),
    ]
    for y, t in steps:
        _wf_box(ax, (xl, y), w, h, t, main, fs=9)
    for (y0, _), (y1, _) in itertools.pairwise(steps):
        _wf_arrow(ax, (xl, y0 - h / 2), (xl, y1 + h / 2))
    xr, wr, hr = 0.765, 0.45, 0.13
    branches = [
        (0.80, "5 nm slit pore (D48)\nown cool + sweep"),
        (0.58, "cylindrical hole (D52)\nR = 2–4 nm"),
        (0.36, "tensile x/y/z (D54)\n10$^8$, 10$^9$ s$^{-1}$"),
        (0.14, "long holds (D53)\n300 ns, diffusion"),
    ]
    for y, t in branches:
        _wf_box(ax, (xr, y), wr, hr, t, br, fs=9)
    _wf_arrow(ax, (xl + w / 2, 0.69), (xr - wr / 2, 0.80))
    _wf_arrow(ax, (xr, 0.80 - hr / 2), (xr, 0.58 + hr / 2))
    ax.text(xr + 0.015, 0.69, "pore hold", fontsize=8, color="0.35", va="center")
    for y in (0.36, 0.14):
        _wf_arrow(ax, (xl + w / 2, 0.27), (xr - wr / 2, y))
    ax.text(
        0.02,
        0.03,
        "PE and iPP at CG (PE only), UA, AA; branches start from snapshots",
        fontsize=8.5,
        color="0.35",
        transform=ax.transAxes,
    )


def system_table_rows(data: dict) -> list[dict]:
    """Size and cost of every current bulk and 5 nm pore system with a run."""
    rows = []
    ids = data["ids"] | set(data["runs"])
    stale = set(g(data, "ctx", "stale") or {}) | set(g(data, "ctx", "superseded_by") or {})
    for sid in sorted(ids, key=_order):
        s = series_info(sid)
        if not s or s["kind"] not in ("bulk", "pore") or superseded(sid, ids) or sid in stale:
            continue
        runs = runs_of(data, sid)
        if not runs:
            continue
        man = data["systems"].get(sid) or {}
        ns = 0.0
        for r in runs:
            p = r.get("progress") or {}
            dt = next((x.get("dt_fs") for x in p.get("segments") or [] if x.get("dt_fs")), None)
            if dt and p.get("steps_done"):
                ns += p["steps_done"] * dt * 1e-6
        nsd = None
        for kind in ("sweep", "pore", "extend", "prep"):
            r = ss.latest(runs, kind)
            if g(r, "progress", "ns_per_day"):
                nsd = r["progress"]["ns_per_day"]
                break
        box = man.get("box_angstrom") or []
        lens = [b[1] - b[0] for b in box]
        rho = None
        if s["kind"] == "bulk":
            for h in hold_segments(g(data["analysis"], sid, "sweep") or {}):
                if h.get("t_set_c") == 25.0:
                    rho = g(h, "stats", "density", "mean")
            if rho is None:
                rho = g(hold500(sid, data) or {}, "density", "density", "mean")
            for r in reversed(runs):
                for seg in reversed(g(r, "progress", "segments") or []):
                    rho = rho or g(seg, "stats", "density", "mean")
        if rho and man.get("total_mass_g_mol") and len(lens) == 3:
            vol = man["total_mass_g_mol"] / 6.02214076e23 / rho * 1e24  # A^3
            aspect = np.array(lens) / np.prod(lens) ** (1 / 3)
            lens = list(aspect * vol ** (1 / 3))
        if len(lens) == 3:
            bx = (
                f"{lens[0] / 10:.1f}³"
                if max(lens) - min(lens) < 0.05 * max(lens)
                else (
                    f"{lens[0] / 10:.1f}²×{lens[2] / 10:.1f}"
                    if abs(lens[0] - lens[1]) < 0.01 * lens[0]
                    else "×".join(f"{v / 10:.1f}" for v in lens)
                )
            )
        else:
            bx = "—"
        name = f"{RES_NAME[s['res']]} {POLY_NAME.get(s['polymer'], s['polymer'])}"
        name += f" {s['n']}×C{s['c']}"
        if s["kind"] == "pore":
            name += f", {s['width_nm']:g} nm pore"
        rows.append(
            {
                "sid": sid,
                "name": name,
                "sites": g(man, "counts", "total", "atoms"),
                "box": bx,
                "ns": ns,
                "nsd": nsd,
                "res": s["res"],
            }
        )
    return rows


def _f1_table(ax, data, info) -> None:
    panel_label(ax, "f", "Systems: size and cost")
    ax.set_axis_off()
    rows = system_table_rows(data)
    if not rows:
        no_data(ax, "no runs found")
        return
    cells = [
        [
            r["name"],
            f"{r['sites']:,}" if r["sites"] else "—",
            r["box"],
            f"{r['ns']:,.0f}" if r["ns"] >= 1 else f"{r['ns']:.2g}",
            f"{r['nsd']:.0f}" if r["nsd"] else "—",
        ]
        for r in rows
    ]
    tab = ax.table(
        cellText=cells,
        colLabels=["system", "sites", "box (nm)", "ns", "ns/day"],
        loc="upper center",
        cellLoc="right",
        colLoc="right",
        colWidths=[0.43, 0.14, 0.19, 0.12, 0.12],
        bbox=[0.0, 0.0, 1.0, 0.98],
    )
    tab.auto_set_font_size(False)
    tab.set_fontsize(8.8)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("0.85")
        cell.set_linewidth(0.6)
        if c == 0:
            cell.set_text_props(ha="left")
            cell._loc = "left"
        if r == 0:
            cell.set_text_props(fontweight="bold")
            cell.set_facecolor("0.93")
        elif c == 0:
            cell.get_text().set_color(RES_COLOR.get(rows[r - 1]["res"], "black"))
    info["f"] = rows


def fig1_models(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig = plt.figure(figsize=(13.0, 7.6), layout="constrained")
    gs = fig.add_gridspec(2, 1, height_ratios=[0.62, 1.0])
    top = gs[0].subgridspec(1, 3)
    bot = gs[1].subgridspec(1, 3, width_ratios=[0.85, 1.1, 1.25])
    info: dict = {}
    m = segment_models(data)
    titles = {
        "aa": ("a", "AA (OPLS): C + explicit H"),
        "ua": ("b", "UA (TraPPE): CH$_2$/CH$_3$ sites"),
        "cg": ("c", "CG (SDK): 3-carbon beads"),
    }
    rend = render_segments(data, m) if m else {}
    for k, (key, (letter, title)) in enumerate(titles.items()):
        ax = fig.add_subplot(top[k])
        if m is None:
            panel_label(ax, letter, title)
            no_data(ax, "no ua2aa AA PE box (systems/pe_aa_*_from_ua)")
            continue
        png, st = rend[key]
        note = {
            "aa": f"{SEG_CARBONS} backbone C, {len(m['h'])} H",
            "ua": f"{SEG_CARBONS} sites; faint blue = CG beads",
            "cg": f"{len(m['beads'])} beads of the same segment",
        }[key]
        show_render(ax, png, st, title, letter, note)
        info.setdefault("render", {})[key] = st
    if m:
        info["seg"] = {
            "aa_sid": m["aa_sid"],
            "ua_sid": m["ua_sid"],
            "matched": m["matched"],
            "dev_A": m["dev_A"],
            "ua_path": _short(m["ua_path"]) if m["ua_path"] else None,
            "n_h": len(m["h"]),
        }
    # (d) bulk box
    ax = fig.add_subplot(bot[0])
    cg = next((s for s in bulk_systems(data, derived=False) if s["res"] == "cg"), None)
    rep = main_bulk(data) or cg
    snap = snapshot(rep["sid"], data, "sweep") if rep else None
    if snap is None:
        panel_label(ax, "d", "Bulk box")
        no_data(ax, "no snapshot")
    else:
        png, st = bulk_render(data, rep["sid"], snap, f"bulk_{rep['sid']}")
        n_ch = len(np.unique(snap["mol"]))
        show_render(
            ax,
            png,
            st,
            f"{rep['label']} bulk box",
            "d",
            f"{n_ch} chains, {len(snap['pos']):,} beads, {snap['L'][0] / 10:.1f} nm;"
            f" {'25 °C hold end' if snap['local_run'] else 'as built'}",
        )
        info["d"] = {
            "sid": rep["sid"],
            "label": rep["label"],
            "source": _short(snap["path"]),
            "local_run": snap["local_run"],
            "n_chains": n_ch,
            "beads": len(snap["pos"]),
            "box_nm": float(snap["L"][0] / 10),
            "status": st,
        }
    _f1_workflow(fig.add_subplot(bot[1]))
    _f1_table(fig.add_subplot(bot[2]), data, info)
    return save(fig, out, "fig1_models"), info


# ================================================================== figure 2: equilibration
def chain_series_500k(data: dict) -> list[dict]:
    """Bulk systems with 500 K chain data (replicated boxes excluded; AA conversions kept)."""
    out = []
    for s in bulk_systems(data):
        h = hold500(s["sid"], data)
        if h is not None:
            out.append(s | {"h500": h})
    return out


def _f2_acf(ax, series, info) -> None:
    panel_label(ax, "a", "500 K: end-to-end vector ACF")
    shown = [s for s in series if len(s["h500"].get("acf", [])) > 1]
    if not shown:
        no_data(ax, "no 500 K chain curves")
        return
    for s in shown:
        r = s["h500"]
        ok = r["lag_ns"] > 0
        ax.plot(r["lag_ns"][ok], r["acf"][ok], color=s["color"], ls=s["ls"], label=s["label"])
        if np.isfinite(r["t_1e_ns"]):
            ax.plot(
                r["t_1e_ns"],
                INV_E,
                marker=s["marker"],
                color=s["color"],
                mfc=s["mfc"],
                ms=9,
                mec="black",
                mew=0.8,
                zorder=4,
            )
    ax.axhline(INV_E, color="0.4", ls=":", lw=1.3)
    ax.text(0.98, INV_E + 0.02, "1/e", color="0.3", transform=ax.get_yaxis_transform(), ha="right")
    ax.set_xscale("log")
    ax.set_xlim(0.01, None)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("time interval Δt (ns, model time)")
    ax.set_ylabel(
        r"$\langle\mathbf{R}_{ee}(t)\cdot\mathbf{R}_{ee}(t+\Delta t)\rangle/\langle R_{ee}^2\rangle$"
    )
    info["a"] = [
        {
            "sid": s["sid"],
            "label": s["label"],
            "t_1e_ns": s["h500"]["t_1e_ns"],
            "hold_ns": s["h500"].get("hold_ns"),
            "source": s["h500"]["source"],
        }
        for s in shown
    ]


def _f2_msd(ax, series, info) -> None:
    panel_label(ax, "b", "500 K: chain COM MSD / ⟨R$_g^2$⟩")
    shown = [s for s in series if s["h500"].get("msd_rg2") is not None]
    if not shown:
        no_data(ax, "no 500 K COM MSD curves")
        return
    info["b"] = []
    for s in shown:
        r = s["h500"]
        x, y = r["msd_lag_ns"], r["msd_rg2"]
        ok = (x > 0) & (y > 0)
        ax.plot(x[ok], y[ok], color=s["color"], ls=s["ls"], label=s["label"])
        d = r.get("d47") or {}
        if d.get("lag_ns") and d.get("ratio"):
            ax.plot(
                d["lag_ns"],
                d["ratio"],
                marker=s["marker"],
                color=s["color"],
                mfc=s["mfc"],
                ms=9,
                mec="black",
                mew=0.8,
                zorder=4,
            )
        info["b"].append({"label": s["label"], "d47": d})
    ax.axhline(2.0, color="0.4", ls=":", lw=1.3)
    ax.text(0.012, 2.35, "D47: 2⟨R$_g^2$⟩", color="0.3", fontsize=10)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.01, None)
    ax.set_xlabel("time interval Δt (ns, model time)")
    ax.set_ylabel(r"COM MSD / $\langle R_g^2\rangle$")


CN_BLOCKS = 8  # block means of the 500 K C_n plateau series (appendix Fig. 2.1 a)


def _f2_cn(ax, series, info) -> None:
    panel_label(ax, "a", "500 K: C$_n$ plateau (n ≥ 100), block means")
    shown = [s for s in series if len(s["h500"].get("plateau_t", [])) >= 2 * CN_BLOCKS]
    if not shown:
        no_data(ax, "no C_n plateau series")
        return
    pols = []
    info["a"] = []
    for s in shown:
        r = s["h500"]
        t, y = r["plateau_t_ns"], r["plateau_t"]
        edges = np.linspace(t[0], t[-1], CN_BLOCKS + 1)
        rows = []
        for b0, b1 in itertools.pairwise(edges):
            sel = (t >= b0) & (t <= b1) if b1 == edges[-1] else (t >= b0) & (t < b1)
            if sel.sum() < 3:
                continue
            m = timeseries_mean(y[sel])
            rows.append((0.5 * (b0 + b1), m.mean, m.sem))
        x, m, e = (np.array(v) for v in zip(*rows, strict=True))
        ax.errorbar(x, m, e, fmt=s["marker"], color=s["color"], mfc=s["mfc"], ls=s["ls"], lw=1.4)
        for b in r.get("boundaries_ns") or []:
            ax.axvline(b, color=s["color"], ls=":", lw=1.0, alpha=0.7)
        if s["polymer"] not in pols:
            pols.append(s["polymer"])
        info["a"].append(
            {
                "label": s["label"],
                "plateau": r.get("cn_plateau"),
                "ref": r.get("cn_ref"),
                "blocks": rows,
                "block_ns": float(edges[1] - edges[0]),
            }
        )
    refs = []
    for pol in pols:
        ref = EXPERIMENT.get(pol, {}).get("c_melt_500k")
        if ref:
            ax.axhspan(0.9 * ref, 1.1 * ref, color="0.5", alpha=0.13, lw=0)
            ax.axhline(ref, color="black", lw=1.4, ls="--")
            refs.append(f"{POLY_NAME[pol]} {ref:g}")
    ax.set_xlabel("time at 500 K, block centre (ns, model time)")
    ax.set_ylabel("C$_n$ plateau, block mean ± SEM")
    ax.set_xscale("log")
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + 0.35 * (hi - lo))
    ax.legend(
        handles=_legend_handles(shown)
        + [Line2D([], [], color="0.4", ls=":", lw=1, label="prep | extension")]
        + (
            [
                Line2D(
                    [],
                    [],
                    color="black",
                    ls="--",
                    label=f"melt C$_\\infty$ ± 10 % ({', '.join(refs)})",
                )
            ]
            if refs
            else []
        ),
        loc="upper left",
        fontsize=8.5,
        ncols=3,
        columnspacing=0.8,
    )


def _f2_sweep(ax, rep, info) -> None:
    panel_label(ax, "c", "Sweep density trace (25 → 160 °C)")
    if rep is None:
        no_data(ax, "no bulk sweep results.json")
        return
    res = rep["results"]["sweep"]
    conv = res.get("convergence") or []
    info["c"] = {"sid": rep["sid"], "label": rep["label"]}
    for c in conv:
        q = g(c, "quantities", "density")
        if not q:
            continue
        t = np.asarray(q["t_ps"], float) / 1000.0
        ax.plot(t, q["value"], color=rep["color"], lw=0.5, alpha=0.5, zorder=2)
        t0, t1 = c["t_start_ps"] / 1000.0, c["t_end_ps"] / 1000.0
        w0 = c["window"][0] / 1000.0
        if c["kind"] == "hold":
            tc = _tc_of(c["name"])
            ax.axvspan(t0, t1, color=t_color(tc), alpha=0.10, lw=0, zorder=0)
            ax.axvspan(w0, t1, color=t_color(tc), alpha=0.20, lw=0, zorder=0)
            ax.text(
                0.5 * (t0 + t1),
                0.985,
                f"{tc:g} °C",
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=9.5,
                color=t_color(tc),
                fontweight="bold",
            )
            b = q.get("blocks") or []
            ax.errorbar(
                [x["t"] / 1000.0 for x in b],
                [x["mean"] for x in b],
                [x["sem"] for x in b],
                fmt="o",
                ms=3,
                color="black",
                lw=0.8,
                zorder=3,
            )
        else:
            ax.axvspan(w0, t1, color="0.85", alpha=0.6, lw=0, zorder=0)
    ax.set_xlabel("sweep time (ns, model time)")
    ax.set_ylabel(r"$\rho$ (g cm$^{-3}$)")
    lo = min(min(g(c, "quantities", "density", "value") or [1]) for c in conv)
    hi = max(max(g(c, "quantities", "density", "value") or [0]) for c in conv)
    ax.set_ylim(lo - 0.003, hi + 0.18 * (hi - lo))
    ax.set_xlim(0, max(c["t_end_ps"] for c in conv) / 1000.0)
    ax.legend(
        handles=[
            Line2D([], [], color=rep["color"], lw=0.9, label=rep["label"]),
            Line2D([], [], color="black", marker="o", ms=3, ls="", label="block means ± SEM"),
            Patch(fc="0.6", alpha=0.45, label="analysis windows"),
        ],
        loc="lower left",
        fontsize=9,
    )
    n_steps = sum(c["kind"] == "step" for c in conv)
    info["c"].update(n_steps=n_steps, n_holds=len(conv) - n_steps)


def _f2_sem(ax, rep, info) -> None:
    panel_label(ax, "b", f"Hold SEM vs block length (D55), {rep['label'] if rep else ''}")
    if rep is None:
        no_data(ax, "no bulk sweep results.json")
        return
    conv = [c for c in rep["results"]["sweep"].get("convergence") or [] if c["kind"] == "hold"]
    ts = []
    for c in conv:
        rows = g(c, "sem_vs_block", "density")
        if not rows:
            continue
        tc = _tc_of(c["name"])
        ts.append(tc)
        bl = np.array([r["block_ps"] for r in rows]) / 1000.0
        sem = np.array([r["sem"] for r in rows]) * 1e5
        ax.plot(bl, sem, marker="o", color=t_color(tc), ms=5)
        ref = g(c, "quantities", "density", "sem")
        if ref:
            ax.axhline(ref * 1e5, color=t_color(tc), ls=":", lw=1.3)
    if not ts:
        no_data(ax, "no sem_vs_block in the sweep results.json")
        return
    ax.axvline(0.1, color="0.3", ls="--", lw=1)
    ax.text(
        0.105, 0.03, "100 ps\nblocks", transform=ax.get_xaxis_transform(), va="bottom", fontsize=9.5
    )
    ax.set_xscale("log")
    ax.set_xlim(0.07, None)
    ax.set_ylim(0, None)
    ax.set_xlabel("block length (ns)")
    ax.set_ylabel(r"SEM of hold $\rho$ ($10^{-5}$ g cm$^{-3}$)")
    _t_legend(ax, ts, loc="upper left", title=None, ncols=2, bbox_to_anchor=(0.12, 1.0))
    ax.legend(
        handles=[
            Line2D([], [], color="0.3", marker="o", label="from block means"),
            Line2D([], [], color="0.3", ls=":", label="reported SEM"),
        ],
        loc="lower right",
        fontsize=9,
    )
    info["b"] = {"ts": ts, "label": rep["label"]}


def _f2_gamma(ax, data, info) -> None:
    panel_label(ax, "d", "Slit pore: γ running mean per hold")
    pores = find_series(data, "pore", "pore")
    if not pores:
        no_data(ax, "no pore results.json", pending=True)
        return
    ts = set()
    rows = []
    for s in pores:
        for c in s["results"]["pore"].get("convergence") or []:
            q = g(c, "quantities", "gamma")
            if c["kind"] != "hold" or not q:
                continue
            tc = _tc_of(c["name"])
            ts.add(tc)
            t = np.asarray(q["t_ps"], float)
            v = np.asarray(q["value"], float)
            win = t >= c["window"][0]
            run = np.cumsum(v[win]) / np.arange(1, win.sum() + 1)
            sel = t[win] >= c["window"][0] + 4000.0  # drawn after its first 4 ns
            tt = (t[win][sel] - c["t_start_ps"]) / 1000.0
            ax.plot(
                tt,
                run[sel],
                color=t_color(tc),
                ls=s["ls"],
                lw=1.8,
            )
            rows.append((s["label"], tc, q.get("mean"), q.get("sem")))
    if not ts:
        no_data(ax, "no hold γ series in the pore results.json")
        return
    ax.set_xlabel("time in hold (ns, model time)")
    ax.set_ylabel(r"$\gamma$ running mean (mN m$^{-1}$)")
    lo = min(r[2] for r in rows if r[2] is not None)
    hi = max(r[2] for r in rows if r[2] is not None)
    ax.set_ylim(lo - 3.5, hi + 4.0)
    _t_legend(ax, sorted(ts), loc="upper center", title=None, ncols=4, fontsize=9)
    ax.legend(
        handles=[Line2D([], [], color="0.3", ls=s["ls"], label=pore_label(s)) for s in pores],
        loc="lower right",
        fontsize=9,
    )
    info["d"] = {
        "pores": [pore_label(s) for s in pores],
        "sids": [s["sid"] for s in pores],
        "rows": rows,
    }


def fig2_equilibration(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(2, 2, figsize=FIG22L, layout="constrained")
    info: dict = {}
    series = chain_series_500k(data)
    _f2_acf(axes[0, 0], series, info)
    _f2_msd(axes[0, 1], series, info)
    rep = main_bulk(data)
    _f2_sweep(axes[1, 0], rep, info)
    _f2_gamma(axes[1, 1], data, info)
    shared = [
        s
        for s in series
        if s["h500"].get("msd_rg2") is not None or len(s["h500"].get("acf", [])) > 1
    ]
    fig_legend(
        fig,
        [
            _legend_handles(shared),
            [
                _key("solid / filled: 40 × C240 box", "o", "-"),
                _key("dashed / open: CG PE C1500", "o", "--", mfc="white"),
                _key("black edge: 1/e time (a), half the hold (b)", "o", ms=8, mec="black"),
            ],
        ],
    )
    info["sids"] = [s["sid"] for s in series]
    paths = save(fig, out, "fig2_equilibration")
    # appendix Fig. 2.1: C_n plateau block means, hold SEM vs block length
    fig, axes = plt.subplots(1, 2, figsize=FIG12, layout="constrained")
    app: dict = {}
    _f2_cn(axes[0], series, app)
    _f2_sem(axes[1], rep, app)
    info["appendix"] = {"fig2_1_cn_sem": app}
    paths += save(fig, out / APPENDIX, "fig2_1_cn_sem")
    return paths, info


# ================================================================== figure 3: thermo
def _exp_polymers(series: list[dict]) -> list[str]:
    return sorted({s["polymer"] for s in series}, key=lambda p: ss.POLYMER_ORDER.get(p, 9))


LONG_KW = {"fillstyle": "top", "ms": 8}  # long holds (D53): half-filled symbols


def _f3_density(ax, sweeps, info) -> None:
    panel_label(ax, "a", "Density at 1 atm")
    if not sweeps:
        no_data(ax, "no bulk sweeps", pending=True)
        return
    for s in sweeps:
        segs = s["results"]["sweep"].get("segments") or []
        ax.plot(
            [x["t_set_c"] for x in segs],
            [g(x, "stats", "density", "mean") for x in segs],
            color=s["color"],
            ls=s["ls"],
            lw=1.5,
            zorder=2,
        )
        hs = hold_segments(s["results"]["sweep"])
        ax.errorbar(
            [x["t_set_c"] for x in hs],
            [g(x, "stats", "density", "mean") for x in hs],
            [g(x, "stats", "density", "sem") for x in hs],
            fmt=s["marker"],
            color=s["color"],
            mfc=s["mfc"],
            zorder=3,
        )
    for pol in _exp_polymers(sweeps):
        e = EXPERIMENT.get(pol, {})
        if "density" in e:
            p = np.array(e["density"]["points"])
            ax.errorbar(p[:, 0], p[:, 1], p[:, 2], fmt="x", ms=8, mew=1.8, **EXP_KW)
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"$\rho$ (g cm$^{-3}$)")
    info["a"] = {
        "series": [s["label"] for s in sweeps],
        "holds": {
            s["label"]: [
                (x["t_set_c"], g(x, "stats", "density", "mean"))
                for x in hold_segments(s["results"]["sweep"])
            ]
            for s in sweeps
        },
    }


def _window_bars(ax, sweeps, key, val, scale, info_key, info) -> None:
    """Fit-window bars (thick: 25-90 / 90-160 °C, thin: 25-160 °C) with error bars."""
    n = len(sweeps)
    info[info_key] = {}
    for i, s in enumerate(sweeps):
        off = (i - (n - 1) / 2) * 6.0
        for f in g(s, "results", "sweep", "fits", key) or []:
            w0, w1 = f["window_c"]
            a, e = f[val] * scale, (f.get("err") or 0) * scale
            full = (w1 - w0) > 100
            ax.plot(
                [w0, w1],
                [a, a],
                color=s["color"],
                ls=s["ls"],
                lw=1.3 if full else 3.5,
                alpha=0.6 if full else 1.0,
                solid_capstyle="butt",
            )
            if not full:
                ax.errorbar(
                    0.5 * (w0 + w1) + off,
                    a,
                    e,
                    fmt=s["marker"],
                    color=s["color"],
                    mfc=s["mfc"],
                    ms=6,
                )
            info[info_key].setdefault(s["label"], []).append((w0, w1, a, e, f.get("chi2_red")))


ALPHA_WINDOW = 5  # consecutive sweep temperatures per local alpha_V fit (~40 K)


def local_alpha(res: dict, n: int = ALPHA_WINDOW) -> list[tuple]:
    """Local alpha_V (1/K) from sliding windows of ``n`` consecutive sweep temperatures:
    V(T) per T from the segment volume mean / SEM (the hold where a T has a step and a
    hold), SEM-weighted linear fit per window (unscaled covariance error), alpha_V =
    slope / mean V. Rows (window centre = mean T in °C, alpha_V, err, T_lo, T_hi)."""
    pts: dict[float, dict] = {}
    kinds: dict[float, str] = {}
    for x in res.get("segments") or []:
        v = g(x, "stats", "volume")
        tc = round(float(x["t_set_c"]), 3)
        if not v or v.get("mean") is None or kinds.get(tc) == "hold":
            continue
        pts[tc], kinds[tc] = v, x.get("kind")
    ts = sorted(pts)
    if len(ts) < n:
        return []
    v = np.array([pts[t]["mean"] for t in ts], float)
    e = np.array([pts[t].get("sem") or 0.0 for t in ts], float)
    e = np.where(e > 0, e, e[e > 0].min() if (e > 0).any() else 1.0)
    tk = np.array(ts) + 273.15
    out = []
    for k in range(len(ts) - n + 1):
        sl = slice(k, k + n)
        te = thermal_expansion(tk[sl], v[sl], e[sl])
        out.append((float(np.mean(ts[sl])), te.alpha_V, te.alpha_V_err, ts[k], ts[k + n - 1]))
    return out


def _full_alpha(s: dict) -> dict | None:
    """The 25-160 °C alpha_V fit of a sweep (results.json ``fits.alpha_V``)."""
    for f in g(s, "results", "sweep", "fits", "alpha_V") or []:
        if list(f.get("window_c") or []) == [25.0, 160.0]:
            return f
    return None


def _f3_alpha(ax, sweeps, info) -> None:
    panel_label(ax, "b", r"Local thermal expansion $\alpha_V$ (40 K windows)")
    if not sweeps:
        no_data(ax, "no bulk sweeps", pending=True)
        return
    info["b"] = {}
    n = len(sweeps)
    for i, s in enumerate(sweeps):
        rows = local_alpha(s["results"]["sweep"])
        if not rows:
            continue
        off = (i - (n - 1) / 2) * 1.2
        x, a, e = (np.array([r[k] for r in rows]) for k in range(3))
        ax.errorbar(
            x + off,
            a * 1e4,
            e * 1e4,
            fmt=s["marker"],
            color=s["color"],
            mfc=s["mfc"],
            ls=s["ls"],
            lw=1.4,
            ms=5.5,
        )
        full = _full_alpha(s)
        info["b"][s["label"]] = {
            "local": [(r[0], r[1] * 1e4, r[2] * 1e4) for r in rows],
            "full": (full["alpha_V_per_K"] * 1e4, (full.get("err") or 0) * 1e4) if full else None,
        }
    for pol in _exp_polymers(sweeps):
        e = EXPERIMENT.get(pol, {})
        if "alpha_V" in e:
            lo, hi = e["alpha_V"]["band"]
            w0, w1 = e["alpha_V"]["window"]
            ax.fill_between([w0, w1], lo, hi, color="0.2", alpha=0.15, lw=0, zorder=0)
            ax.text(
                w1 - 2, hi + 0.05, f"{POLY_NAME[pol]} expt.", ha="right", va="bottom", fontsize=9.5
            )
    ax.set_ylabel(r"$\alpha_V$ ($10^{-4}$ K$^{-1}$)")
    ax.set_xlabel("window centre T (°C)")
    ax.set_xlim(15, 170)


def _f3_kappa(ax, data, sweeps, info) -> None:
    panel_label(ax, "c", r"Compressibility $\kappa_T$")
    if not sweeps:
        no_data(ax, "no bulk sweeps", pending=True)
        return
    info["c"] = {}
    n = len(sweeps)
    for i, s in enumerate(sweeps):
        off = (i - (n - 1) / 2) * 3.0
        hs = [h for h in g(s, "results", "sweep", "holds") or [] if h.get("kappa")]
        st = [x for x in g(s, "results", "sweep", "steps") or [] if x.get("kappa")]
        if st:  # 5 ns sweep steps: small markers, one plain line through steps and holds
            line = sorted(hs + st, key=lambda x: x["t_c"])
            ax.plot(
                [x["t_c"] + off for x in line],
                [x["kappa"]["kappa_T_GPa"] for x in line],
                color=s["color"],
                ls=s["ls"],
                lw=1.1,
            )
            ax.errorbar(
                [x["t_c"] + off for x in st],
                [x["kappa"]["kappa_T_GPa"] for x in st],
                [x["kappa"].get("sem") or 0 for x in st],
                fmt=s["marker"],
                color=s["color"],
                mfc=s["mfc"],
                ms=STEP_MS,
                elinewidth=0.8,
                capsize=1.5,
                ls="",
            )
            info["c_steps"] = True
            info.setdefault("c_step_rows", {})[s["label"]] = [
                (x["t_c"], x["kappa"]["kappa_T_GPa"]) for x in st
            ]
        ax.errorbar(
            [h["t_c"] + off for h in hs],
            [h["kappa"]["kappa_T_GPa"] for h in hs],
            [h["kappa"].get("sem") or 0 for h in hs],
            fmt=s["marker"],
            color=s["color"],
            mfc=s["mfc"],
            ls="" if st else s["ls"],
            lw=1.5,
            zorder=3,
        )
        info["c"][s["label"]] = [(h["t_c"], h["kappa"]["kappa_T_GPa"]) for h in hs]
        lh = [r for r in long_holds(data, s["sid"]) if g(r, "res", "kappa", "kappa_T_GPa")]
        if lh:
            info["c_long"] = True
            ax.errorbar(
                [r["t_c"] + off + 4 for r in lh],
                [r["res"]["kappa"]["kappa_T_GPa"] for r in lh],
                [r["res"]["kappa"].get("sem") or 0 for r in lh],
                fmt=s["marker"],
                color=s["color"],
                ls="",
                **LONG_KW,
            )
            info["c"][s["label"] + " long"] = [
                (r["t_c"], r["res"]["kappa"]["kappa_T_GPa"]) for r in lh
            ]
    for pol in _exp_polymers(sweeps):
        e = EXPERIMENT.get(pol, {})
        if "kappa_T" in e:
            p = np.array(e["kappa_T"]["points"])
            ax.plot(p[:, 0], p[:, 1], "x", ms=9, mew=1.8, **EXP_KW)
    ax.set_ylabel(r"$\kappa_T$ (GPa$^{-1}$)")
    ax.set_xlabel("T (°C)")
    ax.set_xlim(15, 175)


def cp_athas(pol: str, t_c: np.ndarray) -> np.ndarray | None:
    e = EXPERIMENT.get(pol, {}).get("cp_athas")
    if not e:
        return None
    return (e["a"] * (np.asarray(t_c) + 273.15) + e["b"]) / e["unit_g"]


def _f3_cp(ax, sweeps, info) -> None:
    panel_label(ax, "a", r"Heat capacity $C_p$ (classical)")
    if not sweeps:
        no_data(ax, "no bulk sweeps", pending=True)
        return
    _window_bars(ax, sweeps, "cp", "cp_J_gK", 1.0, "a", info)
    # quantum (VDOS) corrected Cp of AA, when an analysis provides it
    extra = []
    for s in sweeps:
        res = s["results"]["sweep"]
        for key in validity.VDOS_CP_KEYS:
            q = g(res, "fits", key) or res.get(key)
            for f in q if isinstance(q, list) else ([q] if isinstance(q, dict) else []):
                if f.get("cp_J_gK") is None:
                    continue
                w0, w1 = f.get("window_c") or (25.0, 160.0)
                ax.plot([w0, w1], [f["cp_J_gK"]] * 2, color=s["color"], lw=3.5, ls=":")
                info.setdefault("a_vdos", []).append((s["label"], w0, w1, f["cp_J_gK"]))
    if info.get("a_vdos"):
        extra.append(Line2D([], [], color="0.3", lw=3, ls=":", label="AA, VDOS-corrected"))
    tt = np.linspace(25, 160, 50)
    for pol in _exp_polymers(sweeps):
        y = cp_athas(pol, tt)
        if y is not None:
            ax.plot(tt, y, color="black", lw=1.8, ls="-" if pol == "pe" else "--")
            extra.append(
                Line2D(
                    [],
                    [],
                    color="black",
                    ls="-" if pol == "pe" else "--",
                    label=f"{POLY_NAME[pol]} expt. (ATHAS)",
                )
            )
    extra += [
        Line2D([], [], color="0.3", lw=3.5, label="25–90 / 90–160 °C fit"),
        Line2D([], [], color="0.3", lw=1.3, alpha=0.6, label="25–160 °C fit"),
    ]
    ax.set_ylim(0, 3.6)
    ax.set_xlim(15, 170)
    ax.set_xlabel("fit window T (°C)")
    ax.set_ylabel(r"$C_p$ (J g$^{-1}$ K$^{-1}$)")
    ax.text(
        0.03,
        0.47,
        "CG/UA: removed degrees of freedom,\nnot comparable (validity: no)",
        transform=ax.transAxes,
        fontsize=9.5,
        color="0.3",
    )
    ax.legend(
        handles=_legend_handles(sweeps, ls=False) + extra,
        loc="upper left",
        fontsize=8.5,
        ncols=3,
        columnspacing=0.8,
    )


def _f3_hysteresis(ax, data, info) -> list[dict]:
    panel_label(ax, "d", "Step-cool vs heating sweep: Δρ")
    shown = []
    for s in bulk_systems(data, rep=True):
        run = ss.latest(runs_of(data, s["sid"]), "sweep")
        rows = [r for r in g(run, "progress", "hysteresis") or [] if r.get("delta_pct") is not None]
        if not rows:
            continue
        t = np.array([r["t_k"] - 273.15 for r in rows])
        d = np.array([r["delta_pct"] for r in rows])
        e = np.array([100 * (r.get("rho_cool_sem") or 0) / (r.get("rho_sweep") or 1) for r in rows])
        ax.errorbar(t, d, e, fmt=s["marker"], color=s["color"], mfc=s["mfc"], ls=s["ls"], lw=1.5)
        shown.append(s)
        info.setdefault("d", {})[s["label"]] = list(zip(t.tolist(), d.tolist(), strict=True))
    if not shown:
        no_data(ax, "no hysteresis rows (sweep progress.json)", pending=True)
        return []
    ax.axhline(0, color="0.5", lw=0.9)
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"$(\rho_{cool} - \rho_{heat})/\rho_{heat}$ (%)")
    lim = max(0.2, 1.3 * max(abs(v) for vals in info["d"].values() for _, v in vals))
    ax.set_ylim(-lim, lim)
    ax.set_xlim(15, 165)
    return shown


def _f3_size(ax, data, info) -> None:
    panel_label(ax, "b", "Chain length: ρ vs CG PE C240")
    cg = [s for s in bulk_systems(data, rep=True, derived=False) if s["res"] == "cg"]
    ref = next((s for s in cg if s["primary"]), None)
    if ref is None:
        no_data(ax, "no CG C240 reference", pending=True)
        return

    def rho_by_t(s):
        out = {}
        for x in g(data["analysis"], s["sid"], "sweep", "segments") or []:
            out[round(x["t_set_c"], 1)] = (
                g(x, "stats", "density", "mean"),
                g(x, "stats", "density", "sem"),
            )
        h = hold500(s["sid"], data)
        d = g(h or {}, "density", "density")
        if d and d.get("mean"):
            out[T500_C] = (d["mean"], d.get("sem"))
        return out

    r0 = rho_by_t(ref)
    shown = []
    info["b"], info["b_box"] = {}, {}
    for s in cg:
        if s is ref:
            continue
        r1 = rho_by_t(s)
        ts = sorted(t for t in r1 if t in r0 and r1[t][0] and r0[t][0])
        if not ts:
            continue
        d = np.array([100 * (r1[t][0] / r0[t][0] - 1) for t in ts])
        if s["c"] == ref["c"]:  # same chains, larger box: box size, noted in the caption
            info["b_box"][s["label"]] = list(zip(ts, d.tolist(), strict=True))
            continue
        e = np.array([100 * np.hypot(r1[t][1] or 0, r0[t][1] or 0) / r0[t][0] for t in ts], float)
        x = np.array(ts)
        sweep_pts = x < 200
        ax.errorbar(
            x[sweep_pts],
            d[sweep_pts],
            e[sweep_pts],
            fmt=s["marker"],
            color=s["color"],
            mfc=s["mfc"],
            ls=s["ls"],
            lw=1.5,
            ms=5,
        )
        if (~sweep_pts).any():
            ax.errorbar(
                x[~sweep_pts],
                d[~sweep_pts],
                e[~sweep_pts],
                fmt="D",
                color=s["color"],
                mfc=s["mfc"],
                ms=8,
            )
        shown.append(s)
        info["b"][s["label"]] = list(zip(x.tolist(), d.tolist(), strict=True))
    if not shown:
        no_data(ax, "only one CG chain length has densities", pending=True)
        return
    ax.axhline(0, color=ref["color"], lw=1.2)
    ax.text(20, 0.02, ref["label"] + " (reference)", color=ref["color"], fontsize=9.5, va="bottom")
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"$\rho_{\rm C1500}/\rho_{\rm C240} - 1$ (%)")
    ax.set_xticks([25, 90, 130, 160, T500_C], ["25", "90", "130", "160", "500 K"])
    ax.legend(
        handles=_legend_handles(shown)
        + [Line2D([], [], color="0.3", marker="D", mfc="white", ls="", label="500 K melt hold")],
        loc="center right",
        fontsize=9,
    )
    info["b_alpha"] = {
        s["label"]: [
            (f["window_c"], f["alpha_V_per_K"] * 1e4)
            for f in g(data["analysis"], s["sid"], "sweep", "fits", "alpha_V") or []
        ]
        for s in [ref, *shown]
    }


CONV_LS = ("-", "--", "-.", ":")  # appendix Fig. 3.2: line style = model (sweep order)
CONV_MIN_NS = 0.5  # running estimates drawn from 0.5 ns into the analysis window


def hold_convergence(s: dict) -> list[dict]:
    """Per sweep hold: running mean density and growing-window kappa_T vs time in the
    hold, from the thinned ``convergence`` series of the sweep results.json (analysis
    window only, i.e. after the hold's first 10 %)."""
    out = []
    holds = {float(h["t_c"]): h for h in g(s, "results", "sweep", "holds") or []}
    for c in g(s, "results", "sweep", "convergence") or []:
        rho, vol = g(c, "quantities", "density"), g(c, "quantities", "volume")
        if c.get("kind") != "hold" or not rho or not vol:
            continue
        tc = _tc_of(c["name"])
        t = (np.asarray(rho["t_ps"], float) - c["t_start_ps"]) / 1000.0
        w = np.asarray(rho["t_ps"], float) >= c["window"][0]
        r, v, t = np.asarray(rho["value"], float)[w], np.asarray(vol["value"], float)[w], t[w]
        run = np.cumsum(r) / np.arange(1, len(r) + 1)
        n0 = max(10, int(np.searchsorted(t, t[0] + CONV_MIN_NS)))
        idx = np.unique(np.linspace(n0, len(v), 40).astype(int))
        kap = np.array([isothermal_compressibility(v[:k], tc + 273.15).kappa_T for k in idx])
        out.append(
            {
                "t_c": tc,
                "t_ns": t,
                "rho_run": run,
                "k_t_ns": t[idx - 1],
                "kappa": kap,
                "kappa_stored": g(holds.get(tc), "kappa", "kappa_T_GPa"),
                "n": len(v),
                "dt_ps": float(np.median(np.diff(rho["t_ps"]))),
            }
        )
    return out


def fig3_2_convergence(sweeps: list[dict], out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.0), layout="constrained")
    info: dict = {"series": {}}
    prim = [s for s in sweeps if s["primary"]]
    shown, ts = [], set()
    for k, s in enumerate(prim):
        rows = hold_convergence(s)
        if not rows:
            continue
        ls = CONV_LS[k % len(CONV_LS)]
        shown.append((s, ls))
        for r in rows:
            ts.add(r["t_c"])
            sel = r["t_ns"] >= r["t_ns"][0] + CONV_MIN_NS
            axes[0].plot(
                r["t_ns"][sel],
                100 * (r["rho_run"][sel] / r["rho_run"][-1] - 1),
                color=t_color(r["t_c"]),
                ls=ls,
                lw=1.6,
            )
            axes[1].plot(r["k_t_ns"], r["kappa"], color=t_color(r["t_c"]), ls=ls, lw=1.6)
        info["series"][s["label"]] = [
            {
                "t_c": r["t_c"],
                "hold_ns": float(r["t_ns"][-1]),
                "window_start_ns": float(r["t_ns"][0]),
                "kappa_end": float(r["kappa"][-1]),
                "kappa_stored": r["kappa_stored"],
                "n": r["n"],
                "dt_ps": r["dt_ps"],
                "rho_dev_half": float(
                    100 * (r["rho_run"][len(r["rho_run"]) // 2] / r["rho_run"][-1] - 1)
                ),
            }
            for r in rows
        ]
    panel_label(axes[0], "a", "Running mean density per hold")
    panel_label(axes[1], "b", r"$\kappa_T$ from a growing window")
    if not shown:
        for ax in axes:
            no_data(ax, "no sweep hold convergence series", pending=True)
    else:
        axes[0].axhline(0, color="0.5", lw=0.9)
        axes[0].set_ylabel(r"$\bar\rho(t)/\bar\rho_{\rm hold} - 1$ (%)")
        axes[1].set_ylabel(r"$\kappa_T$ (GPa$^{-1}$)")
        for ax in axes:
            ax.set_xlabel("time in hold (ns, model time)")
            ax.set_xlim(0, None)
        fig_legend(
            fig,
            [
                [Line2D([], [], color=t_color(t), lw=2.4, label=t_label(t)) for t in sorted(ts)]
                + [Line2D([], [], color="0.3", ls=ls, lw=1.6, label=s["label"]) for s, ls in shown]
            ],
            handlelength=3.2,
        )
    info["skipped"] = [s["label"] for s in prim if s["label"] not in info["series"]]
    return save(fig, out / APPENDIX, "fig3_2_convergence"), info


def fig3_thermo(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(2, 2, figsize=FIG22L, layout="constrained")
    info: dict = {}
    sweeps = find_series(data, "bulk", "sweep")
    _f3_density(axes[0, 0], sweeps, info)
    _f3_alpha(axes[0, 1], sweeps, info)
    _f3_kappa(axes[1, 0], data, sweeps, info)
    hyst = _f3_hysteresis(axes[1, 1], data, info)
    legend = list({s["sid"]: s for s in [*sweeps, *hyst]}.values())
    legend.sort(key=lambda s: _order(s["sid"]))
    extra = [
        _key("solid / filled: 40 × C240 box", "o", "-"),
        _key("dashed / open: CG PE C1500", "o", "--", mfc="white"),
    ]
    if info.get("c_long"):
        extra.append(_key("half-filled: long hold (D53), κ$_T$", "o", **LONG_KW))
    if info.get("c_steps"):
        extra.append(_key("small markers: 5 ns sweep steps, κ$_T$", "o", ms=STEP_MS))
    exp_h = []
    for pol in _exp_polymers(sweeps):
        e = EXPERIMENT.get(pol, {})
        if "density" in e or "kappa_T" in e:
            exp_h.append(
                Line2D([], [], color="black", marker="x", ls="", label=f"{POLY_NAME[pol]} expt.")
            )
        if "alpha_V" in e:
            exp_h.append(Patch(fc="0.2", alpha=0.15, label=f"{POLY_NAME[pol]} expt. α$_V$"))
    if sweeps or hyst:
        fig_legend(fig, [_legend_handles(legend), extra, exp_h])
    info["sids"] = [s["sid"] for s in sweeps]
    paths = save(fig, out, "fig3_thermo")
    # appendix Fig. 3.1: classical Cp, chain length; Fig. 3.2: hold convergence
    fig, axes = plt.subplots(1, 2, figsize=FIG12, layout="constrained")
    app: dict = {}
    _f3_cp(axes[0], sweeps, app)
    _f3_size(axes[1], data, app)
    paths += save(fig, out / APPENDIX, "fig3_1_cp_chain_length")
    p2, conv = fig3_2_convergence(sweeps, out)
    info["appendix"] = {"fig3_1_cp_chain_length": app, "fig3_2_convergence": conv}
    return paths + p2, info


# ================================================================== figure 4: chains
def _traj_point(tr: dict, t_c: float, src: str) -> dict:
    ser = g(tr, "c_n", "series", "plateau") or []
    rgs = g(tr, "rg", "series", "rg2_A2") or []
    k = max(1, len(ser) // 10)
    return {
        "t_c": t_c,
        "src": src,
        "rg": g(tr, "rg", "rg_A", "mean"),
        "rg_sem": g(tr, "rg", "rg_A", "sem"),
        "ree": g(tr, "ree", "ree_A", "mean"),
        "ree_sem": g(tr, "ree", "ree_A", "sem"),
        "ree2": g(tr, "ree", "ree2_A2", "mean"),
        "ree2_sem": g(tr, "ree", "ree2_A2", "sem"),
        "cn": g(tr, "c_n", "plateau", "mean"),
        "cn_sem": g(tr, "c_n", "plateau", "sem"),
        "cn_first": float(np.mean(ser[:k])) if ser else None,
        "cn_last": float(np.mean(ser[-k:])) if ser else None,
        "rg_first": float(np.sqrt(np.mean(rgs[:k]))) if rgs else None,
        "rg_last": float(np.sqrt(np.mean(rgs[-k:]))) if rgs else None,
        "relaxed": relaxed(tr),
        "msd_rg2": g(tr, "com_msd", "msd_rg2_end"),
        "cryst": g(tr, "crystallinity") if g(tr, "crystallinity", "available") else None,
        "hold_ns": tr.get("hold_ns"),
    }


def chain_points(data: dict, s: dict) -> list[dict]:
    """Chain size per T of a bulk system: sweep holds, 5 ns sweep steps (results.json
    ``steps``, when the analysis has them), long holds (D53), 500 K melt."""
    pts = [_traj_point(h["traj"], float(h["t_c"]), "sweep") for h in sweep_holds(s, data)]
    pts += [_traj_point(st["traj"], float(st["t_c"]), "step") for st in sweep_steps(s, data)]
    for r in long_holds(data, s["sid"]):
        tr = g(r, "res", "traj") or {}
        if tr.get("available"):
            pts.append(_traj_point(tr, r["t_c"], "long"))
    h = hold500(s["sid"], data)
    if h:
        tr = h.get("traj")
        if tr:
            p = _traj_point(tr, T500_C, "500K")
        else:
            p = {
                "t_c": T500_C,
                "src": "500K",
                "rg": h.get("rg_A"),
                "ree": h.get("ree_A"),
                "ree2": (h["ree_A"] ** 2) if h.get("ree_A") else None,
                "cn": h.get("cn_plateau"),
                "relaxed": bool(g(h, "d47", "passed")),
                "cryst": None,
            }
        p["relaxed"] = True  # the 500 K melt is the equilibrated reference (D47)
        pts.append(p)
    return pts


LONG_DX = 4.0  # x offset (°C) of the long-hold points next to the sweep holds
STEP_MS = 4.0  # marker size of the 5 ns sweep steps (holds: 7)


def draw_chain_points(ax, s: dict, pts: list[dict], val, err) -> None:
    """Fig. 4 points of one series: a plain line through the sweep (holds and steps in T
    order) to the 500 K melt; sweep holds open, steps small open (both inherit the chain
    shape), long holds (D53) filled at +4 °C, the 500 K melt a filled diamond."""
    sw = sorted((p for p in pts if p["src"] in ("sweep", "step", "500K")), key=lambda p: p["t_c"])
    ax.plot([p["t_c"] for p in sw], [val(p) for p in sw], color=s["color"], ls=s["ls"], lw=1.1)
    for p in pts:
        if p["src"] == "step":
            ax.errorbar(
                p["t_c"],
                val(p),
                err(p) or 0,
                fmt=s["marker"],
                color=s["color"],
                mfc="white",
                ms=STEP_MS,
                elinewidth=0.8,
                capsize=1.5,
                zorder=2,
            )
            continue
        ax.errorbar(
            p["t_c"] + (LONG_DX if p["src"] == "long" else 0.0),
            val(p),
            err(p) or 0,
            fmt="D" if p["src"] == "500K" else s["marker"],
            color=s["color"],
            mfc=s["color"] if p["src"] in ("long", "500K") else "white",
            ms=7,
            zorder=3,
        )


def long_hold_ns(series: list[dict]) -> tuple[float, float, bool] | None:
    """(shortest, longest) long-hold length in ns over the series, and whether all long
    holds are CG; None without long holds."""
    rows = [(p.get("hold_ns"), s["res"]) for s in series for p in s["pts"] if p["src"] == "long"]
    ns = [h for h, _ in rows if h]
    if not ns:
        return None
    return min(ns), max(ns), all(r == "cg" for _, r in rows)


def _chain_panel(ax, data, series, key, ylabel, letter, title, info, exp=None) -> None:
    panel_label(ax, letter, title)
    shown = []
    info[letter] = {}
    for s in series:
        pts = [p for p in s["pts"] if p.get(key) is not None]
        if not pts:
            continue
        shown.append(s)
        draw_chain_points(ax, s, pts, lambda p: p[key], lambda p: p.get(key + "_sem"))
        info[letter][s["label"]] = [(p["t_c"], p["src"], p[key], p["relaxed"]) for p in pts]
    if not shown:
        no_data(ax, "no chain-size data", pending=True)
        return
    extra = []
    if exp:
        extra = exp(ax)
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(ylabel)
    ax.set_xticks([25, 90, 130, 160, T500_C], ["25", "90", "130", "160", "500 K"])
    ax.set_xlim(10, 245)
    return shown, extra


def _point_keys(long: tuple | None = None, steps: bool = False) -> list:
    """Fig. 4 point-style keys: what each fill / size / shape is."""
    h = [_key("open: sweep hold (chains inherited from 500 K)", "o", mfc="white")]
    if long:
        lo, hi, cg = long
        h.append(
            _key(
                f"filled: long hold, {lo:.0f}–{hi:.0f} ns{', CG only' if cg else ''}"
                " (chains moved ≥ own size)",
                "o",
            )
        )
    if steps:
        h.append(_key("small open: 5 ns sweep step", "o", mfc="white", ms=STEP_MS))
    return h + [_key("diamond: 500 K melt", "D")]


EXP_PT = {"ms": 8, "mfc": "black", "mec": "black", "capsize": 4, **EXP_KW}  # Fig. 4 expt.


def exp_key() -> Line2D:
    """Fig. 4 / 4.1 legend entry: experiment in black with the polymer's marker."""
    return Line2D(
        [], [], color="black", marker="o", ls="", label="black: experiment (circle PE, square iPP)"
    )


def _exp_rg(ax):
    e = EXPERIMENT["pe"]["rg_c240"]
    ax.errorbar(
        e["t_c"],
        0.5 * (e["lo"] + e["hi"]),
        0.5 * (e["hi"] - e["lo"]),
        fmt=POLY_MARKER["pe"],
        **EXP_PT,
    )
    return []


def _exp_ree(ax):
    e = EXPERIMENT["pe"]["r2_over_m"]
    m = 240 * CH2_G + 2 * 1.008
    ax.errorbar(e["t_c"], np.sqrt(e["value"] * m), fmt=POLY_MARKER["pe"], **EXP_PT)
    return []


def _exp_cn(ax):
    pts = np.array(EXPERIMENT["pe"]["c_inf"])
    ax.errorbar(pts[:, 0], pts[:, 1], fmt=POLY_MARKER["pe"], **EXP_PT)
    ax.errorbar(T500_C, EXPERIMENT["pe"]["c_melt_500k"], fmt=POLY_MARKER["pe"], **EXP_PT)
    ipp = EXPERIMENT["ipp"].get("c_melt_500k")
    if ipp:  # the only sourced iPP value: the D37 melt reference at 500 K
        ax.errorbar(T500_C + 7, ipp, fmt=POLY_MARKER["ipp"], **EXP_PT)
    return []


def _f4_cn_n(ax, data, series, info) -> None:
    panel_label(ax, "c", "C$_n$(n): internal distances")
    rep = next((s for s in series if s["res"] == "cg"), series[0] if series else None)
    shown_t, res_seen = set(), set()
    info["c"] = {}
    for s in series:
        for h in sweep_holds(s, data) if s is rep else []:
            c = g(h, "traj", "curves")
            if c and c.get("cn"):
                tc = float(h["t_c"])
                ax.plot(c["cn_n"], c["cn"], color=t_color(tc), ls=s["rls"], lw=1.6)
                shown_t.add(tc)
                res_seen.add(s["res"])
        h5 = hold500(s["sid"], data)
        if h5 is not None and len(h5.get("cn", [])) > 1:
            ax.plot(h5["cn_n"], h5["cn"], color=GREY_500K, ls=s["rls"], lw=2.2)
            shown_t.add(T500_C)
            res_seen.add(s["res"])
            info["c"][s["label"]] = h5.get("cn_plateau")
    if not shown_t:
        no_data(ax, "no C_n(n) curves stored", pending=True)
        return
    ax.axhline(EXPERIMENT["pe"]["c_inf"][1][1], color="black", ls="--", lw=1.2)
    ax.text(
        238,
        EXPERIMENT["pe"]["c_inf"][1][1] - 0.15,
        "PE C$_\\infty$ 7.38 (140 °C)",
        ha="right",
        va="top",
        fontsize=9.5,
    )
    ax.axvline(100, color="0.6", ls=":", lw=1)
    ax.text(102, 0.4, "plateau n ≥ 100", fontsize=9, color="0.4")
    ax.set_xlabel("n (backbone carbons)")
    ax.set_ylabel(r"C$_n$ = ⟨R$_n^2$⟩ / (n l$^2$)")
    ax.set_xlim(0, 240)
    ax.set_ylim(0, max(ax.get_ylim()[1], 12) * 1.38)
    _t_legend(
        ax,
        sorted(shown_t),
        loc="upper left",
        title=f"{rep['label']} holds" if rep else None,
        ncols=3,
        fontsize=9,
    )
    ax.legend(
        handles=_res_ls_handles(res_seen),
        loc="upper right",
        bbox_to_anchor=(1, 0.8),
        ncols=3,
        fontsize=9,
    )


def _f4_cryst(ax, data, series, info) -> None:
    panel_label(ax, "c", "Ordered-site fraction vs T")
    info["c"] = {}
    shown = []
    for s in series:
        pts = [p for p in s["pts"] if p.get("cryst")]
        if not pts:
            continue
        shown.append(s)
        draw_chain_points(
            ax,
            s,
            pts,
            lambda p: p["cryst"]["fraction"]["mean"],
            lambda p: p["cryst"]["fraction"].get("sd"),
        )
        info["c"][s["label"]] = [
            (
                p["t_c"],
                p["src"],
                p["cryst"]["fraction"]["mean"],
                p["cryst"]["largest_cluster"]["max"],
                p["cryst"].get("fraction_first"),
                p["cryst"].get("fraction_last"),
            )
            for p in pts
        ]
    films = []
    for s in find_series(data, "pore", "pore"):
        hs = [
            h
            for h in s["results"]["pore"].get("holds") or []
            if g(h, "film", "crystallinity", "available")
        ]
        if not hs:
            continue
        films.append(s)
        ax.errorbar(
            [h["t_c"] - 4 for h in hs],
            [h["film"]["crystallinity"]["fraction"]["mean"] for h in hs],
            [h["film"]["crystallinity"]["fraction"].get("sd") or 0 for h in hs],
            fmt="v",
            color=s["color"],
            mfc=s["mfc"],
            ls=":",
            lw=1.2,
        )
        info["c"][s["label"] + " film"] = [
            (h["t_c"], h["film"]["crystallinity"]["fraction"]["mean"]) for h in hs
        ]
    if not shown and not films:
        no_data(ax, "no crystallinity monitor stored", pending=True)
        return
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("fraction of sites with p2 ≥ 0.4")
    ax.set_xticks([25, 90, 130, 160, T500_C], ["25", "90", "130", "160", "500 K"])
    ax.set_xlim(10, 245)
    ax.set_ylim(0, None)
    if films:  # pore films are unique to this panel: small in-panel key
        ax.legend(
            handles=[
                Line2D(
                    [],
                    [],
                    color=s["color"],
                    marker="v",
                    mfc=s["mfc"],
                    ls=":",
                    label=pore_label(s, " film"),
                )
                for s in films
            ],
            loc="upper right",
            fontsize=8.5,
        )
    ax.text(
        0.02,
        0.03,
        "uncalibrated threshold: a melt baseline, not crystallinity",
        transform=ax.transAxes,
        fontsize=8.5,
        color="0.35",
    )


def _f4_length(ax, data, info) -> None:
    panel_label(ax, "b", "C240 vs C1500: ⟨R$_{ee}^2$⟩/M")
    info["b"] = {}
    shown = []
    for s in bulk_systems(data, derived=False):
        if s["res"] != "cg":
            continue
        pts = [p for p in chain_points(data, s) if p.get("ree2") and p["src"] != "step"]
        if not pts:
            continue
        m = mass_per_chain(s)
        shown.append(s)
        draw_chain_points(
            ax, s, pts, lambda p, m=m: p["ree2"] / m, lambda p, m=m: (p.get("ree2_sem") or 0) / m
        )
        info["b"][s["label"]] = [(p["t_c"], p["src"], p["ree2"] / m) for p in pts]
    if not shown:
        no_data(ax, "no CG chain sizes", pending=True)
        return
    e = EXPERIMENT["pe"]["r2_over_m"]
    ax.errorbar(e["t_c"], e["value"], fmt=POLY_MARKER["pe"], **EXP_PT)
    ax.text(e["t_c"] + 6, e["value"], "PE melt expt.", va="center", fontsize=9.5)
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"⟨R$_{ee}^2$⟩ / M (Å$^2$ mol g$^{-1}$)")
    ax.set_xticks([25, 90, 130, 160, T500_C], ["25", "90", "130", "160", "500 K"])
    ax.set_xlim(10, 245)
    ax.set_ylim(0, None)
    info["b_series"] = shown


def fig4_chains(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(1, 3, figsize=FIG13, layout="constrained")
    info: dict = {}
    series = [s | {"pts": chain_points(data, s)} for s in bulk_systems(data) if s["primary"]]
    series = [s for s in series if s["pts"]]
    keys = {
        "long": long_hold_ns(series),
        "steps": any(p["src"] == "step" for s in series for p in s["pts"]),
    }
    info["keys"] = keys
    shown = {}
    for ax, key, lab, letter, title, exp in (
        (axes[0], "rg", r"R$_g$ (Å)", "a", "Radius of gyration", _exp_rg),
        (axes[1], "cn", r"C$_n$ plateau (n ≥ 100)", "b", "Characteristic ratio", _exp_cn),
    ):
        r = _chain_panel(ax, data, series, key, lab, letter, title, info, exp)
        if r:
            shown |= {s["sid"]: s for s in r[0]}
    _f4_cn_n(axes[2], data, series, info)
    if series:
        fig_legend(
            fig,
            legend_rows(
                _legend_handles(list(shown.values()) or series, ls=False)
                + [exp_key()]
                + _point_keys(**keys)
                + [_key("line: joins the sweep points", ls="-", lw=1.2)],
                4,
            ),
        )
    info["long_drift"] = {
        s["label"]: [p for p in s["pts"] if p["src"] == "long" and p.get("cn_first")]
        for s in series
        if any(p["src"] == "long" for p in s["pts"])
    }
    info["sids"] = [s["sid"] for s in series]
    paths = save(fig, out, "fig4_chains")
    # appendix Fig. 4.1: R_ee vs T, C240 vs C1500 <R_ee^2>/M, ordered-site fraction
    fig, axes = plt.subplots(1, 3, figsize=FIG13, layout="constrained")
    app: dict = {"long": keys["long"], "steps": keys["steps"]}
    r = _chain_panel(
        axes[0],
        data,
        series,
        "ree",
        r"R$_{ee}$ = ⟨R$_{ee}^2$⟩$^{1/2}$ (Å)",
        "a",
        "End-to-end distance",
        app,
        _exp_ree,
    )
    _f4_length(axes[1], data, app)
    _f4_cryst(axes[2], data, series, app)
    # shared legend: models (a, c), the CG chain lengths of (b) by line style, point keys
    models = list((r[0] if r else []) or [])
    lengths = [
        Line2D(
            [], [], color=s["color"], ls=s["ls"], marker=s["marker"], mfc="white", label=s["label"]
        )
        for s in app.pop("b_series", [])
        if not s["primary"]
    ]
    if models or lengths:
        fig_legend(
            fig,
            legend_rows(
                _legend_handles(models, ls=False)
                + lengths
                + [exp_key()]
                + _point_keys(**keys)
                + [_key("line: joins the sweep points (dashed: C1500)", ls="-")],
                4,
            ),
        )
    info["appendix"] = {"fig4_1_ree_length": app}
    paths += save(fig, out / APPENDIX, "fig4_1_ree_length")
    return paths, info


# ================================================================== figure 5: pore
def _main_pore(data) -> dict | None:
    pores = [s for s in find_series(data, "pore", "pore") if s["primary"]]
    if pores:
        return pores[0]
    for sid in sorted(data["systems"], key=_order):
        s = series_info(sid)
        if s and s["kind"] == "pore" and s["primary"]:
            return s
    return None


def pore_render(data: dict, pore: dict, snap: dict) -> tuple:
    """Side view along x of a slit pore: gap centred, 3 x 3 periodic images in y, z (central
    cell coloured by chain, images light grey), the central gap shaded."""
    size = (1500, 1150)
    pos, L, lo = snap["pos"].copy(), snap["L"], snap["lo"]
    zc = gap_center(pos[:, 2], lo[2], L[2])
    if zc is not None:  # gap mid-cell
        pos[:, 2] = lo[2] + np.mod(pos[:, 2] - zc + L[2] / 2 - lo[2] + lo[2] - lo[2], L[2])
    i, j = snap["pairs"].T
    ok = np.all(np.abs(pos[i] - pos[j]) < 0.5 * L, axis=1)
    pairs = snap["pairs"][ok]
    ctr = lo + L / 2
    # camera: look along -x -> image horizontal = z, vertical = y; camera frame (z, y, -x)
    to_cam = lambda p: np.c_[p[:, 2] - ctr[2], p[:, 1] - ctr[1], -(p[:, 0] - ctr[0])]
    n = len(pos)
    all_pos, all_resi, all_pairs = [], [], []
    k = 0
    for iy in (-1, 0, 1):
        for iz in (-1, 0, 1):
            p = pos + np.array([0.0, iy * L[1], iz * L[2]])
            all_pos.append(to_cam(p))
            img = (iy, iz) != (0, 0)
            all_resi.append(np.full(n, 0) if img else snap["mol"] - snap["mol"].min() + 1)
            all_pairs.append(pairs + k * n)
            k += 1
    allp = np.vstack(all_pos)
    resi = np.concatenate(all_resi)
    cols = chain_colors(snap["mol"])
    m0 = snap["mol"] - snap["mol"].min() + 1
    pal = np.zeros((m0.max() + 1, 3))
    pal[0] = (0.80, 0.80, 0.80)
    for c_, m in zip(cols, m0, strict=True):
        pal[m] = c_
    files = {"pore.pdb": pr.pdb_text(allp, "C", resi, np.vstack(all_pairs))}
    half_w, half_h = 0.98 * L[2], 1.2 * L[1]
    cell = pr.box_corners(lo, lo + L)
    cell = to_cam(cell)
    width = g(data["systems"], pore["sid"], "pore", "nominal_width_nm")
    gap_half = 10 * (width or 5.0) / 2
    back = -L[0] / 2 - 3
    quad = [
        (-gap_half, -half_h * 2, back),
        (gap_half, -half_h * 2, back),
        (gap_half, half_h * 2, back),
        (-gap_half, half_h * 2, back),
    ]
    body = pr.style_lines(outline=False) + [
        "load pore.pdb, pore",
        "hide everything",
        f"alter pore, vdw={SIGMA_HALF['bead']}",
        "rebuild",
        "show sticks",
        "show spheres",
        "set stick_radius, 0.7",
        "set sphere_scale, 0.42",
        *pr.color_lines("pore", pal, np.arange(len(pal)), "ch"),
        *pr.cgo_quad("gap", quad, (0.55, 0.75, 0.95), 0.45),
        *pr.cgo_cylinders("cell", pr.box_edges(cell), 0.6, (0, 0, 0)),
        *pr.view_lines(half_w, half_h, *size, depth=L[0] + 40),
    ]
    png, st = pr.render(
        f"pore_{pore['sid']}", files, body, _render_dir(data), size, data.get("render", True)
    )
    return png, st, {"gap_nm": width}


def _f5_render(ax, data, info) -> None:
    pore = _main_pore(data)
    title = f"{pore_label(pore)}, side view" if pore else "Slit pore"
    snap = snapshot(pore["sid"], data, "pore") if pore else None
    if snap is None:
        panel_label(ax, "a", title)
        no_data(ax, "no pore snapshot", pending=True)
        return
    png, st, extra = pore_render(data, pore, snap)
    show_render(
        ax,
        png,
        st,
        title,
        "a",
        f"z →, gap shaded; periodic images grey; {'25 °C hold end' if snap['local_run'] else 'as built'}",
    )
    info["a"] = {
        "sid": pore["sid"],
        "label": pore["label"],
        "source": _short(snap["path"]),
        "local_run": snap["local_run"],
        "status": st,
    } | extra


def _f5_profile(ax, pores, info) -> None:
    panel_label(ax, "a", r"$\rho$ vs distance from the Gibbs surface")
    ts = set()
    info["a"] = {}
    for s in pores:
        for h in s["results"]["pore"].get("holds") or []:
            p = g(h, "traj", "profile")
            hz = (p or {}).get("film_gibbs_A")
            if not p or not p.get("rho_sym") or not hz:
                continue
            tc = float(h["t_c"])
            ts.add(tc)
            z = (np.asarray(p["z_A"], float) - hz / 2) / 10.0  # each film's own Gibbs surface
            ax.plot(z, p["rho_sym"], color=t_color(tc), ls=s["ls"], lw=1.6)
            bulk = g(h, "bulk", "density", "mean")
            if bulk and s["primary"]:
                ax.plot([-6.5, -0.5], [bulk, bulk], color=t_color(tc), ls=":", lw=1.4)
            info["a"].setdefault(pore_label(s), []).append(
                (tc, g(p, "plateau", "mean"), bulk, hz, p.get("gap_gibbs_A"))
            )
    if not ts:
        no_data(ax, "no ρ(z) profiles stored", pending=True)
        return
    ax.axvline(0, color="0.5", lw=0.9, ls=":")
    ax.set_xlabel("z − z$_{Gibbs}$ (nm; < 0 inside the film)")
    ax.set_ylabel(r"$\rho$ (g cm$^{-3}$)")
    ax.set_xlim(-6.6, 2.5)
    ax.set_ylim(0, 1.25)
    _t_legend(
        ax, sorted(ts), loc="upper left", title=None, ncols=4, fontsize=8.5, columnspacing=0.8
    )
    ax.legend(
        handles=[Line2D([], [], color="0.3", ls=":", label="bulk (same T)")],
        loc="upper left",
        bbox_to_anchor=(0, 0.9),
        fontsize=8.5,
    )


def _f5_gamma(ax, pores, info) -> None:
    panel_label(ax, "b", r"Surface tension $\gamma(T)$")
    info["b"] = {}
    for i, s in enumerate(pores):
        res = s["results"]["pore"]
        hs = hold_segments(res)
        off = (i - (len(pores) - 1) / 2) * 3.0
        tc = np.array([x["t_set_c"] for x in hs])
        gm = np.array([g(x, "stats", "gamma", "mean") for x in hs], float)
        ge = np.array([g(x, "stats", "gamma", "sem") or 0 for x in hs], float)
        ax.errorbar(tc + off, gm, ge, fmt=s["marker"], color=s["color"], mfc=s["mfc"], ms=7)
        fit = g(res, "fits", "sweep")
        if fit and fit.get("line"):
            b, a = fit["line"]
            tt = np.array(fit["window_c"])
            ax.plot(tt, a + b * (tt + 273.15), color=s["color"], ls=s["ls"], lw=1.4)  # fit in K
        info["b"][pore_label(s)] = {
            "sid": s["sid"],
            "res": s["res"],
            "polymer": s["polymer"],
            "holds": list(zip(tc.tolist(), gm.tolist(), ge.tolist(), strict=True)),
            "dgdT": g(fit, "dgamma_dT_mN_mK"),
            "dgdT_err": g(fit, "err"),
        }
    for pol in _exp_polymers(pores):
        gl = EXPERIMENT.get(pol, {}).get("gamma_line")
        if gl:
            tt = np.array([25.0, 160.0])
            ax.plot(tt, gl["a"] + gl["b"] * tt, **EXP_KW, lw=1.6)
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"$\gamma$ (mN m$^{-1}$)")
    ax.set_xlim(15, 175)


def _f5_interface(ax, pores, info) -> None:
    panel_label(ax, "c", "Interfacial width (10–90 %)")
    info["c"] = {}
    for s in pores:
        hs = [h for h in s["results"]["pore"].get("holds") or [] if g(h, "traj", "profile")]
        if not hs:
            continue
        t = [h["t_c"] for h in hs]
        w = [
            np.mean(
                [g(h, "traj", "profile", "interface_10_90", k, "width") for k in ("lower", "upper")]
            )
            for h in hs
        ]
        tw = [g(h, "traj", "profile", "tanh", "width_10_90_A") for h in hs]
        ax.plot(t, w, color=s["color"], ls="-", marker=s["marker"], mfc=s["mfc"])
        if all(v is not None for v in tw):
            ax.plot(t, tw, color=s["color"], ls=":", marker=s["marker"], mfc="white", ms=5)
        info["c"][pore_label(s)] = list(zip(t, [float(x) for x in w], tw, strict=True))
    if not info["c"]:
        no_data(ax, "no profile widths", pending=True)
        return
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("10–90 % width (Å)")
    _lo, hi = ax.get_ylim()
    ax.set_ylim(0, hi * 1.3)
    ax.legend(
        handles=[
            Line2D([], [], color="0.3", ls="-", label="from the profile"),
            Line2D([], [], color="0.3", ls=":", label="tanh fit"),
        ],
        loc="lower right",
        fontsize=8.5,
    )


def _bulk_msd_at(h: dict, lag_ps: float) -> float | None:
    b = h.get("bulk") or {}
    x, y = b.get("msd_lag_ps"), b.get("msd_per_dim_A2")
    if not x or not y:
        return None
    return float(np.interp(np.log(lag_ps), np.log(np.asarray(x, float)), np.asarray(y, float)))


MSD_LAYERS = (("surface", "xy", "-"), ("surface", "z", "--"), ("interior", "xy", ":"))


def _f5_mobility(ax, pores, info, lag: str = "1000") -> None:
    panel_label(ax, "c", "Segment MSD at Δt = 1 ns by layer")
    info["c"] = {}
    for s in pores:
        hs = [
            h for h in s["results"]["pore"].get("holds") or [] if g(h, "traj", "layers", "surface")
        ]
        if not hs:
            continue
        t = np.array([h["t_c"] for h in hs])
        rows = {}
        for layer, comp, ls in MSD_LAYERS:
            y = [g(h, "traj", "layers", layer, "msd_at", lag, comp) for h in hs]
            ax.plot(t, y, color=s["color"], ls=ls, marker=s["marker"], mfc=s["mfc"])
            rows[f"{layer}_{comp}"] = y
        yb = [_bulk_msd_at(h, float(lag)) for h in hs]
        if s["primary"] and all(v is not None for v in yb):
            ax.plot(t, yb, color="0.45", ls="-", lw=2.5, alpha=0.6, zorder=0)
            rows["bulk"] = yb
        info["c"][pore_label(s)] = {"t": t.tolist()} | rows
    if not info["c"]:
        no_data(ax, "no layer dynamics stored", pending=True)
        return
    ax.set_yscale("log")
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("MSD per dimension at Δt = 1 ns (Å$^2$)")
    ax.legend(  # layers are unique to this panel: in-panel key (line style = layer here)
        handles=[
            Line2D([], [], color="0.3", ls="-", label="surface, in-plane"),
            Line2D([], [], color="0.3", ls="--", label="surface, normal"),
            Line2D([], [], color="0.3", ls=":", label="interior, in-plane"),
            Line2D([], [], color="0.45", lw=2.5, alpha=0.6, label="bulk (MSD/3)"),
        ],
        loc="upper left",
        fontsize=8.5,
        ncols=2,
        title="line style = layer (this panel)",
        title_fontsize=8.5,
    )
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi * 3)


def _f5_p2z(ax, pores, info) -> None:
    panel_label(ax, "d", r"Bond orientation $\langle P_2(\cos\theta_z)\rangle$")
    ts = set()
    info["d"] = {}
    for s in pores:
        for h in s["results"]["pore"].get("holds") or []:
            c = g(h, "traj", "conformation")
            hz = g(h, "traj", "profile", "film_gibbs_A")
            if not c or not c.get("p2z") or not hz:
                continue
            tc = float(h["t_c"])
            ts.add(tc)
            z = (np.asarray(c["p2z_z_A"], float) - hz / 2) / 10.0
            ax.plot(z, c["p2z"], color=t_color(tc), ls=s["ls"], lw=1.6)
            info["d"].setdefault(pore_label(s), []).append(
                (tc, g(c, "p2z_layer", "surface", "mean"), g(c, "p2z_layer", "interior", "mean"))
            )
    if not ts:
        no_data(ax, "no P2(z) stored", pending=True)
        return
    ax.axhline(0, color="0.5", lw=0.9)
    ax.axvline(0, color="0.5", lw=0.9, ls=":")
    ax.text(0.1, -0.06, "Gibbs\nsurface", fontsize=9, color="0.4", va="top")
    ax.text(
        0.02,
        0.04,
        "−0.5: bonds parallel to the surface",
        transform=ax.transAxes,
        fontsize=9,
        color="0.35",
    )
    ax.set_xlabel("z − z$_{Gibbs}$ (nm; < 0 inside the film)")
    ax.set_ylabel(r"$\langle P_2(\cos\theta_z)\rangle$")
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo - 0.04, max(hi, 0.05) + 0.12)
    _t_legend(
        ax, sorted(ts), loc="upper left", title=None, ncols=4, fontsize=8.5, columnspacing=0.8
    )


def _f5_flatten(ax, pores, info) -> None:
    panel_label(ax, "b", "Chain shape by layer")
    info["b"] = {}
    for s in pores:
        hs = [
            h for h in s["results"]["pore"].get("holds") or [] if g(h, "traj", "conformation", "rg")
        ]
        if not hs:
            continue
        t = [h["t_c"] for h in hs]
        rows = {}
        for layer, ls in (("surface", "-"), ("interior", ":")):
            r = [
                g(h, "traj", "conformation", "rg", layer, "rg_z2_A2", "mean")
                / g(h, "traj", "conformation", "rg", layer, "rg_xy2_half_A2", "mean")
                for h in hs
            ]
            ax.plot(t, r, color=s["color"], ls=ls, marker=s["marker"], mfc=s["mfc"])
            rows[layer] = r
        info["b"][pore_label(s)] = {"t": t} | rows
    if not info["b"]:
        no_data(ax, "no chain-shape data stored", pending=True)
        return
    ax.axhline(1.0, color="0.45", lw=2.5, alpha=0.6, zorder=0)
    ax.text(160, 1.03, "isotropic (bulk)", fontsize=9, color="0.35", va="bottom", ha="right")
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"R$_{g,z}^2$ / (R$_{g,xy}^2$/2)")
    ax.set_ylim(0, 1.6)
    ax.legend(
        handles=[
            Line2D([], [], color="0.3", ls="-", label="surface chains"),
            Line2D([], [], color="0.3", ls=":", label="interior chains"),
        ],
        loc="upper left",
        ncols=2,
        fontsize=8.5,
    )


def _pore_legend(fig, pores: list[dict], extra: list) -> None:
    """Shared Fig. 5 / 5.1 legend, one row: each pore series (colour = model, marker =
    polymer) with its box-size style (solid / filled 40 chains, dashed / open 320), then
    the extra keys."""

    def label(s):
        style = "solid / filled" if s["primary"] else "dashed / open"
        n = f"{s['n']} chains" + (", 2×2×2" if "rep222" in s["suffix"] else "")
        w = f" {s['width_nm']:g} nm" if s.get("width_nm") else ""
        return f"{s['base']}{w} pore ({n}): {style}"

    fig_legend(
        fig,
        [
            [
                Line2D(
                    [],
                    [],
                    color=s["color"],
                    marker=s["marker"],
                    mfc=s["mfc"],
                    ls=s["ls"],
                    label=label(s),
                )
                for s in pores
            ]
            + extra
        ],
    )


def fig5_pore(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(2, 2, figsize=FIG22L, layout="constrained")
    info: dict = {}
    pores = find_series(data, "pore", "pore")
    _f5_render(axes[0, 0], data, info)
    for ax, fn, letter in (
        (axes[0, 1], _f5_gamma, "b"),
        (axes[1, 0], _f5_mobility, "c"),
        (axes[1, 1], _f5_p2z, "d"),
    ):
        if not pores:
            panel_label(ax, letter, "")
            no_data(ax, "no pore results.json", pending=True)
            continue
        fn(ax, pores, info)
    if pores:
        extra = []
        if any(EXPERIMENT.get(p, {}).get("gamma_line") for p in _exp_polymers(pores)):
            extra.append(
                Line2D([], [], color="black", lw=1.6, label="PE expt. γ (LLDPE melt, Moreira)")
            )
        _pore_legend(fig, pores, extra)
    info["sids"] = [s["sid"] for s in pores]
    paths = save(fig, out, "fig5_pore")
    # appendix Fig. 5.1 (checks): rho(z - z_Gibbs), chain shape by layer, interfacial width
    fig, axes = plt.subplots(1, 3, figsize=FIG13, layout="constrained")
    app: dict = {}
    for ax, fn, letter in (
        (axes[0], _f5_profile, "a"),
        (axes[1], _f5_flatten, "b"),
        (axes[2], _f5_interface, "c"),
    ):
        if not pores:
            panel_label(ax, letter, "")
            no_data(ax, "no pore results.json", pending=True)
            continue
        fn(ax, pores, app)
    if pores:
        _pore_legend(fig, pores, [])
    info["appendix"] = {"fig5_1_pore_checks": app}
    paths += save(fig, out / APPENDIX, "fig5_1_pore_checks")
    return paths, info


# ================================================================== figure 6: dynamics
def _guide(ax, x0, y0, x1, slope, label, **kw) -> None:
    xs = np.array([x0, x1])
    ax.plot(xs, y0 * (xs / x0) ** slope, color="0.35", lw=1.2, ls="-.", **kw)
    ax.text(x1, y0 * (x1 / x0) ** slope, f" {label}", fontsize=9.5, color="0.3", va="center")


def tfac(s: dict) -> float:
    """Fig. 6 / 6.1 time convention: CG times x 4.07 (≈ real PE time, Hall et al. 2019),
    UA/AA as simulated (no mapping yet). Divide diffusion coefficients by it."""
    return CG_TIME_FACTOR if s.get("res") == "cg" else 1.0


TIME_LABEL = "CG × 4.07 ≈ real, UA model"  # axis-label suffix of every Fig. 6 time


def _f6_seg_msd(ax, data, series, info) -> None:
    panel_label(ax, "a", "Segment MSD (bulk holds)")
    ts, res_seen = set(), set()
    info["a"] = {}
    for s in series:
        curves = [(float(h["t_c"]), g(h, "traj", "curves")) for h in sweep_holds(s, data)]
        curves.append((T500_C, g((hold500(s["sid"], data) or {}).get("traj"), "curves")))
        for tc, c in curves:
            if not c or not c.get("msd_A2"):
                continue
            x = np.asarray(c["msd_lag_ps"], float) / 1000.0 * tfac(s)
            y = np.asarray(c["msd_A2"], float)
            ok = (x > 0) & (y > 0)
            ax.plot(x[ok], y[ok], color=t_color(tc), ls=s["rls"], lw=1.8)
            ts.add(tc)
            res_seen.add(s["res"])
            if tc < 200:
                info["a"].setdefault(s["label"], []).append(tc)
    if not ts:
        no_data(ax, "no segment MSD curves", pending=True)
        return
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(f"time interval Δt (ns; {TIME_LABEL})")
    ax.set_ylabel("backbone-site MSD (Å$^2$)")
    _guide(ax, 0.2, 15, 8.0, 0.5, "t$^{1/2}$")
    info["a_ts"] = sorted(ts)
    info["a_res"] = res_seen


def _f6_com(ax, data, series, info) -> None:
    panel_label(ax, "b", "Chain COM MSD / ⟨R$_g^2$⟩, long holds")
    ts, res_seen = set(), set()
    info["b"] = {}
    for s in series:
        for h in sweep_holds(s, data):
            c = g(h, "traj", "curves")
            rg2 = g(h, "traj", "rg", "rg2_A2", "mean")
            if c and c.get("com_A2") and rg2:
                x = np.asarray(c["com_lag_ps"], float) / 1000.0 * tfac(s)
                y = np.asarray(c["com_A2"], float) / rg2
                ok = (x > 0) & (y > 0)
                ax.plot(x[ok], y[ok], color=t_color(h["t_c"]), ls=s["rls"], lw=1.0, alpha=0.45)
        for r in long_holds(data, s["sid"]):
            tr = g(r, "res", "traj") or {}
            c, rg2 = tr.get("curves") or {}, g(tr, "rg", "rg2_A2", "mean")
            if not c.get("com_A2") or not rg2:
                continue
            x = np.asarray(c["com_lag_ps"], float) / 1000.0 * tfac(s)
            y = np.asarray(c["com_A2"], float) / rg2
            ok = (x > 0) & (y > 0)
            ax.plot(x[ok], y[ok], color=t_color(r["t_c"]), ls=s["rls"], lw=2.4)
            ts.add(r["t_c"])
            res_seen.add(s["res"])
            info["b"].setdefault(s["label"], []).append(
                (
                    r["t_c"],
                    tr.get("hold_ns"),
                    g(tr, "com_msd", "msd_rg2_end"),
                    g(tr, "com_msd", "diffusive"),
                )
            )
    if not ts:
        no_data(ax, "no long-hold (D53) COM MSD yet", pending=True)
        return
    for yv, lab, f in ((1.0, "⟨R$_g^2$⟩", 0.55), (2.0, "2⟨R$_g^2$⟩ (D55 criterion)", 1.12)):
        ax.axhline(yv, color="0.45", ls=":", lw=1.2)
        ax.text(0.042, yv * f, lab, fontsize=9, color="0.35", va="bottom" if f > 1 else "top")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.04, None)
    ax.set_xlabel(f"time interval Δt (ns; {TIME_LABEL})")
    ax.set_ylabel(r"COM MSD / $\langle R_g^2\rangle$")
    _guide(ax, 0.4, 1.5e-4, 12.0, 1.0, "t$^1$")
    ax.set_ylim(1e-4, None)


def _d_points(data: dict, s: dict) -> list[dict]:
    """D_COM per T (model time): diffusive long holds (D53 criterion), else MSD/(6t) at
    the longest lag as an upper bound; the 500 K melt from the extension."""
    out = []
    for r in long_holds(data, s["sid"]):
        com = g(r, "res", "traj", "com_msd") or {}
        if com.get("diffusive") and com.get("D_cm2_s"):
            out.append(
                {
                    "t_c": r["t_c"],
                    "D": com["D_cm2_s"],
                    "err": com.get("D_err_cm2_s"),
                    "bound": False,
                    "src": r["stage"],
                }
            )
        elif com.get("msd_at_max_A2") and com.get("lag_max_ps"):
            out.append(
                {
                    "t_c": r["t_c"],
                    "D": com["msd_at_max_A2"] / (6 * com["lag_max_ps"]) * A2PS_TO_CM2S,
                    "bound": True,
                    "src": r["stage"],
                }
            )
    h = hold500(s["sid"], data)
    if h:
        com = g(h.get("traj"), "com_msd") or {}
        if com.get("diffusive") and com.get("D_cm2_s"):
            out.append(
                {
                    "t_c": T500_C,
                    "D": com["D_cm2_s"],
                    "err": com.get("D_err_cm2_s"),
                    "bound": False,
                    "src": "500 K",
                }
            )
        elif com.get("msd_at_max_A2"):
            out.append(
                {
                    "t_c": T500_C,
                    "D": com["msd_at_max_A2"] / (6 * com["lag_max_ps"]) * A2PS_TO_CM2S,
                    "bound": True,
                    "src": "500 K",
                }
            )
        elif g(h, "d47", "ratio") and g(h, "d47", "lag_ns") and h.get("rg_A"):
            msd = h["d47"]["ratio"] * h["rg_A"] ** 2
            out.append(
                {
                    "t_c": T500_C,
                    "D": msd / (6 * h["d47"]["lag_ns"] * 1000) * A2PS_TO_CM2S,
                    "bound": True,
                    "src": "500 K (progress)",
                }
            )
    return sorted(out, key=lambda p: p["t_c"])


def _f6_dcom(ax, data, series, info) -> list[dict]:
    panel_label(ax, "a", "Chain self-diffusion D$_{COM}$")
    info["a"] = {}
    shown = []
    for s in series:
        pts = _d_points(data, s)
        if not pts:
            continue
        shown.append(s)
        f = tfac(s)
        info["a"][s["label"]] = [p | {"D_shown": p["D"] / f, "factor": f} for p in pts]
        for p in pts:
            d = p["D"] / f
            ax.errorbar(
                p["t_c"],
                d,
                0 if p["bound"] else (p.get("err") or 0) / f,
                fmt=s["marker"],
                color=s["color"],
                mfc="white" if p["bound"] else s["color"],
                ms=8,
                zorder=3,
            )
    if not shown:
        no_data(ax, "no long holds yet", pending=True)
        return []
    e = EXPERIMENT["pe"]["D_com"]
    ax.errorbar(e["t_c"], e["value"], e["value"] * e["rel_err"], fmt=POLY_MARKER["pe"], **EXP_PT)
    ax.text(e["t_c"] + 5, e["value"], "PE expt.\n(Pearson 1987)", fontsize=9, va="center")
    ax.set_yscale("log")
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"D$_{COM}$ (cm$^2$ s$^{-1}$; CG ÷ 4.07 ≈ real, UA model)")
    ax.set_xticks([25, 90, 130, 160, T500_C], ["25", "90", "130", "160", "500 K"])
    ax.set_xlim(10, 245)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo / 1.5, hi * 1.5)
    return shown


def _p2_rows(data: dict, s: dict) -> list[tuple]:
    rows = [(float(h["t_c"]), g(h, "traj", "p2", "t_1e_ps"), "sweep") for h in sweep_holds(s, data)]
    for r in long_holds(data, s["sid"]):  # only if the frames resolve the 1/e time
        tr = g(r, "res", "traj") or {}
        t1 = g(tr, "p2", "t_1e_ps")
        if t1 and t1 >= 2 * (tr.get("frame_ps") or 0):
            rows.append((r["t_c"], t1, "long"))
    tr = (hold500(s["sid"], data) or {}).get("traj")
    if g(tr, "p2", "t_1e_ps"):
        rows.append((T500_C, tr["p2"]["t_1e_ps"], "500K"))
    return [r for r in rows if r[1]]


def _inv_t(t_c) -> np.ndarray:
    return 1000.0 / (np.asarray(t_c, float) + 273.15)


def _f6_p2(ax, data, series, info) -> None:
    panel_label(ax, "c", "Bond reorientation time τ$_{P2}$")
    info["c"] = {}
    any_cg = False
    shown = []
    for s in series:
        rows = _p2_rows(data, s)
        if not rows:
            continue
        shown.append(s)
        any_cg |= s["res"] == "cg"
        f = tfac(s)
        main = sorted((r for r in rows if r[2] != "long"), key=lambda r: r[0])
        ax.plot(
            _inv_t([r[0] for r in main]),
            [r[1] / 1000 * f for r in main],
            color=s["color"],
            marker=s["marker"],
            mfc=s["mfc"],
            ls="-",
        )
        lh = [r for r in rows if r[2] == "long"]
        if lh:
            ax.plot(
                _inv_t([r[0] for r in lh]),
                [r[1] / 1000 * f for r in lh],
                color=s["color"],
                marker=s["marker"],
                ls="",
                **LONG_KW,
            )
        info["c"][s["label"] + " bulk"] = rows
    for p in find_series(data, "pore", "pore"):
        hs = [
            h for h in p["results"]["pore"].get("holds") or [] if g(h, "traj", "layers", "surface")
        ]
        if not hs:
            continue
        any_cg |= p["res"] == "cg"
        t = _inv_t([h["t_c"] for h in hs])
        for layer, ls in (("surface", "--"), ("interior", ":")):
            y = [g(h, "traj", "layers", layer, "p2_t_1e_ps") for h in hs]
            ax.plot(
                t,
                np.array(y, float) / 1000 * tfac(p),
                color=p["color"],
                ls=ls,
                marker="v",
                mfc=p["mfc"],
                ms=6,
            )
            info["c"][f"{pore_label(p)} {layer}"] = list(
                zip([h["t_c"] for h in hs], y, strict=True)
            )
    if not info["c"]:
        no_data(ax, "no P2 times stored", pending=True)
        return
    arrhenius_axes(ax, any_cg)
    ax.set_ylabel(f"τ$_{{P2}}$ (ns; {TIME_LABEL})")
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo / 1.5, hi * 4)
    h = [
        Line2D([], [], color="0.3", ls="-", marker="o", label="bulk"),
        Line2D([], [], color="0.3", ls="--", marker="v", label="pore surface layer"),
        Line2D([], [], color="0.3", ls=":", marker="v", label="pore interior"),
        Line2D([], [], color="0.3", marker="v", mfc="white", ls="", label="open: 320-chain pore"),
    ]
    ax.legend(handles=h, loc="upper left", fontsize=8.5, ncols=2, columnspacing=0.8)


def _relax_rows(data: dict, s: dict) -> list[dict]:
    """tau_ee and tau_1 (Rouse p = 1) per T in model ns: reached 1/e times, or
    extrapolated fits."""

    def one(tr, t_c, src):
        ree = g(tr, "relaxation", "ree") or {}
        r1 = (g(tr, "relaxation", "rouse") or [{}])[0]
        row = {"t_c": t_c, "src": src}
        for key, d in (("ee", ree), ("r1", r1)):
            if d.get("reached") and d.get("t_1e_ps"):
                row[key] = (d["t_1e_ps"] / 1000, False)
            elif d.get("tau_fit_ps"):
                row[key] = (d["tau_fit_ps"] / 1000, True)
        return row

    rows = [one(h["traj"], float(h["t_c"]), "sweep") for h in sweep_holds(s, data)]
    rows += [
        one(r["res"]["traj"], r["t_c"], "long")
        for r in long_holds(data, s["sid"])
        if g(r, "res", "traj", "available")
    ]
    h = hold500(s["sid"], data)
    if h:
        if h.get("traj"):
            rows.append(one(h["traj"], T500_C, "500K"))
        elif np.isfinite(h["t_1e_ns"]):
            rows.append({"t_c": T500_C, "src": "500K", "ee": (h["t_1e_ns"], False)})
    return rows


def _f6_tau(ax, data, series, info) -> list[dict]:
    panel_label(ax, "b", "Chain relaxation: τ$_{ee}$ and Rouse τ$_1$")
    info["b"] = {}
    shown = []
    for s in series:
        rows = _relax_rows(data, s)
        if not any("ee" in r or "r1" in r for r in rows):
            continue
        shown.append(s)
        info["b"][s["label"]] = rows
        f = tfac(s)
        for key, ls, dx in (("ee", "-", 0.0), ("r1", "--", 0.012)):
            pts = sorted((r for r in rows if key in r), key=lambda r: r["t_c"])
            x = _inv_t([r["t_c"] for r in pts]) + dx
            main = [r["src"] != "long" for r in pts]
            ax.plot(
                x[main],
                [r[key][0] * f for r, m in zip(pts, main, strict=True) if m],
                color=s["color"],
                ls=ls,
                lw=1.2,
                alpha=0.7,
            )
            for xi, r in zip(x, pts, strict=True):
                ax.plot(
                    xi,
                    r[key][0] * f,
                    marker=s["marker"] if key == "ee" else "^",
                    color=s["color"],
                    mfc="white" if r[key][1] else s["color"],
                    ms=8 if r["src"] == "long" else 6.5,
                    mec="black" if r["src"] == "long" else s["color"],
                    ls="",
                )
    if not shown:
        no_data(ax, "no relaxation times stored", pending=True)
        return []
    arrhenius_axes(ax, any(s["res"] == "cg" for s in shown))
    ax.set_ylabel(f"relaxation time (ns; {TIME_LABEL})")
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo / 1.5, hi * 2)
    return shown


def _f6_rouse(ax, data, series, info) -> None:
    panel_label(ax, "d", "Rouse mode spectrum τ$_p$")
    info["d"] = {}
    handles: list = []
    for s in series:
        cands = [(r["t_c"], g(r, "res", "traj")) for r in long_holds(data, s["sid"])]
        h5 = hold500(s["sid"], data)
        if h5 and h5.get("traj"):
            cands.append((T500_C, h5["traj"]))
        for t_c, tr in cands:
            modes = g(tr, "relaxation", "rouse") or []
            pts = [
                (
                    m["p"],
                    (m["t_1e_ps"] if m.get("reached") else m.get("tau_fit_ps")),
                    m.get("reached"),
                )
                for m in modes
            ]
            pts = [p for p in pts if p[1]]
            if len(pts) < 2:
                continue
            p = np.array([x[0] for x in pts], float)
            tau = np.array([x[1] for x in pts], float) / 1000 * tfac(s)
            reached = np.array([bool(x[2]) for x in pts])
            col = t_color(t_c)
            line = ax.plot(p, tau, color=col, ls=s["rls"], lw=1.6)[0]
            ax.plot(p[reached], tau[reached], marker=s["marker"], color=col, ls="", ms=7)
            ax.plot(
                p[~reached], tau[~reached], marker=s["marker"], color=col, mfc="white", ls="", ms=7
            )
            fit = (
                np.polyfit(np.log(p[reached]), np.log(tau[reached]), 1)[0]
                if reached.sum() >= 2
                else None
            )
            key = f"{s['label']} {t_label(t_c)}"
            info["d"][key] = {"tau_ns": tau.tolist(), "slope": fit, "reached": reached.tolist()}
            handles.append(
                Line2D(
                    [],
                    [],
                    color=col,
                    ls=line.get_linestyle(),
                    marker=s["marker"],
                    label=key + (f": p$^{{{fit:.2f}}}$" if fit is not None else ""),
                )
            )
    if not info["d"]:
        no_data(ax, "no Rouse modes stored (long holds / 500 K)", pending=True)
        return
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"])
    ax.minorticks_off()
    ax.set_xlabel("Rouse mode p")
    ax.set_ylabel(f"τ$_p$ (ns; {TIME_LABEL})")
    lo, hi = ax.get_ylim()
    tmin = min(min(v["tau_ns"]) for v in info["d"].values())  # guide below every curve
    _guide(ax, 1.1, tmin * 4.0, 1.9, -2.0, "p$^{-2}$\n(Rouse)")
    ax.set_ylim(lo / 400, hi * 1.5)  # room for the key below the curves
    ax.legend(  # one curve per hold: in-panel key with the fitted exponents
        handles=handles,
        loc="lower right",
        fontsize=8.5,
        title="fit over reached modes",
        title_fontsize=8.5,
    )


def fig6_dynamics(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.6), layout="constrained")
    info: dict = {}
    series = [s for s in bulk_systems(data) if s["primary"]]
    shown = _f6_dcom(axes[0], data, series, info)
    shown += [s for s in _f6_tau(axes[1], data, series, info) if s not in shown]
    shown.sort(key=lambda s: _order(s["sid"]))
    if shown:
        fig_legend(
            fig,
            legend_rows(
                _legend_handles(shown, ls=False)
                + [
                    _key("filled: diffusive (COM MSD ≥ 2⟨R$_g^2$⟩)", "o"),
                    _key("open in (a): upper bound MSD/6Δt", "o", mfc="white"),
                    Line2D(
                        [], [], color="black", marker="o", ls="", label="black: experiment (PE)"
                    ),
                    _key("τ$_{ee}$ (1/e), solid", "o", "-"),
                    _key("Rouse τ$_1$, dashed", "^", "--"),
                    _key("open in (b): extrapolated fit", "^", mfc="white"),
                    _key("black edge: long hold", "o", ms=8, mec="black"),
                ],
                4,
            ),
        )
    info["sids"] = [s["sid"] for s in series]
    paths = save(fig, out, "fig6_dynamics")
    # appendix Fig. 6.1: segment MSD, long-hold COM MSD, tau_P2, Rouse spectrum
    fig, axes = plt.subplots(2, 2, figsize=FIG22L, layout="constrained")
    app: dict = {}
    _f6_seg_msd(axes[0, 0], data, series, app)
    _f6_com(axes[0, 1], data, series, app)
    _f6_p2(axes[1, 0], data, series, app)
    _f6_rouse(axes[1, 1], data, series, app)
    ts = sorted(set(app.pop("a_ts", [])) | {r[0] for v in app.get("b", {}).values() for r in v})
    res = app.pop("a_res", set()) | {s["res"] for s in series if s["label"] in app.get("b", {})}
    pshown = [s for s in series if s["label"] + " bulk" in app.get("c", {})]
    fig_legend(
        fig,
        legend_rows(
            [Line2D([], [], color=t_color(t), lw=2.4, label=t_label(t)) for t in ts]
            + _res_ls_handles(res)
            + _legend_handles(pshown, ls=False)
            + [
                Line2D([], [], color="0.4", lw=2.4, label="(b) thick: long hold"),
                Line2D([], [], color="0.4", lw=1, alpha=0.5, label="(b) thin: 25 ns sweep hold"),
                _key("open (d): extrapolated", "o", mfc="white"),
            ]
            + (
                [_key("half-filled (c): long hold", "o", **LONG_KW)]
                if any(
                    r[2] == "long"
                    for k, v in app.get("c", {}).items()
                    if k.endswith(" bulk")
                    for r in v
                )
                else []
            ),
            5,
        ),
    )
    info["appendix"] = {"fig6_1_dynamics_curves": app}
    paths += save(fig, out / APPENDIX, "fig6_1_dynamics_curves")
    return paths, info


# ================================================================== figure 7: mechanics
def tensile_runs(data: dict) -> list[dict]:
    """One record per (system, tensile stage): series info, T, rate, per-axis curves."""
    out = []
    for s in find_series(data, "bulk", "tensile_"):
        for stage, res in sorted(s["results"].items()):
            for run in res.get("runs") or []:
                if run.get("t_c") is None or not run.get("rate_per_s"):
                    continue
                out.append(
                    s
                    | {
                        "stage": stage,
                        "run": run,
                        "t_c": float(run["t_c"]),
                        "rate": float(run["rate_per_s"]),
                    }
                )
    return out


def axis_mean_curve(run: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Strain grid, axis-mean smoothed true stress and its min/max over the axes."""
    axes = [a for a in run.get("axes") or [] if g(a, "curves", "strain")]
    smax = min(max(a["curves"]["strain"]) for a in axes)
    grid = np.linspace(0, smax, 400)
    ys = []
    for a in axes:
        c = a["curves"]
        y = c.get("sigma_smooth") or c["sigma_true"]
        ys.append(np.interp(grid, c["strain"], y))
    ys = np.array(ys)
    return grid, ys.mean(0), ys.min(0), ys.max(0)


def _rate_label(rate: float) -> str:
    e = round(np.log10(rate))
    return f"$10^{{{e}}}$ s$^{{-1}}$"


def fig7_mechanics(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(2, 2, figsize=FIG22, layout="constrained")
    runs = tensile_runs(data)
    info: dict = {"runs": []}
    if not runs:
        for ax, letter in zip(axes.flat, "abcd", strict=True):
            panel_label(ax, letter)
            no_data(ax, "no tensile results.json", pending=True)
        return save(fig, out, "fig7_mechanics"), info
    rep = next((r for r in runs if r["primary"]), runs[0])
    mine = [r for r in runs if r["sid"] == rep["sid"]]
    rates = sorted({r["rate"] for r in mine})
    ymax = 0.0
    ts = set()
    for k, ax in enumerate(axes[0]):
        panel_label(
            ax,
            "ab"[k],
            f"{rep['label']}: stress–strain"
            + (f", {_rate_label(rates[k])}" if k < len(rates) else ""),
        )
        if k >= len(rates):
            no_data(ax, "second strain rate pending", pending=True)
            continue
        for r in sorted((r for r in mine if r["rate"] == rates[k]), key=lambda r: r["t_c"]):
            x, m, lo, hi = axis_mean_curve(r["run"])
            ax.fill_between(x, lo, hi, color=t_color(r["t_c"]), alpha=0.15, lw=0)
            ax.plot(x, m, color=t_color(r["t_c"]), lw=1.8)
            ts.add(r["t_c"])
            ymax = max(ymax, float(hi.max()))
        ax.set_xlabel("engineering strain")
        ax.set_ylabel("true stress (MPa)")
        ax.axhline(0, color="0.6", lw=0.8)
    for k, ax in enumerate(axes[0][: len(rates)]):
        ax.set_ylim(-3, ymax * 1.3)
        ax.set_xlim(0, None)
        _t_legend(
            ax,
            sorted(ts),
            loc="upper left",
            title="mean of x/y/z (band: range)",
            ncols=4,
            fontsize=9,
            columnspacing=0.8,
        )
    axc, axd = axes[1]
    panel_label(axc, "c", "Peak and flow stress")
    panel_label(axd, "d", r"Apparent modulus $E_{app}$ (strain ≤ 0.02)")
    fast_of = {}
    for s_sid in dict.fromkeys(r["sid"] for r in runs):
        rs = [r for r in runs if r["sid"] == s_sid]
        s = rs[0]
        for rate in sorted({r["rate"] for r in rs}):
            sel = sorted((r for r in rs if r["rate"] == rate), key=lambda r: r["t_c"])
            fast = rate >= max(rates)
            mfc = s["color"] if fast else "white"
            fast_of[rate] = fast
            tc = np.array([r["t_c"] for r in sel])
            for key, ls, mk in (("peak_MPa", "-", s["marker"]), ("flow_MPa", "--", "v")):
                m = np.array([g(r["run"], "summary", key, "mean") for r in sel], float)
                sd = np.array([g(r["run"], "summary", key, "sd") or 0 for r in sel], float)
                axc.errorbar(tc, m, sd, fmt=mk, ls=ls, color=s["color"], mfc=mfc, lw=1.6, ms=7)
            e_m = np.array([g(r["run"], "summary", "E_MPa", "mean") for r in sel], float)
            e_sd = np.array([g(r["run"], "summary", "E_MPa", "sd") or 0 for r in sel], float)
            dx = 3.0 if fast else -3.0
            axd.errorbar(
                tc + dx,
                e_m,
                e_sd,
                fmt=s["marker"],
                color=s["color"],
                mfc=mfc,
                ms=8,
                lw=1.4,
                zorder=3,
            )
            for r in sel:
                ea = [a.get("E_MPa") for a in r["run"].get("axes") or []]
                axd.plot([r["t_c"] + dx] * len(ea), ea, ".", color=s["color"], alpha=0.45, ms=6)
                info["runs"].append(
                    {
                        "sid": r["sid"],
                        "label": s["label"],
                        "t_c": r["t_c"],
                        "rate": rate,
                        "peak": g(r["run"], "summary", "peak_MPa"),
                        "flow": g(r["run"], "summary", "flow_MPa"),
                        "E": g(r["run"], "summary", "E_MPa"),
                        "E_err": [a.get("E_err_MPa") for a in r["run"].get("axes") or []],
                    }
                )
    axc.set_yscale("log")
    axc.set_xlabel("T (°C)")
    axc.set_ylabel("stress (MPa)")
    rate_h = [
        Line2D(
            [],
            [],
            color="0.3",
            marker="o",
            ls="",
            mfc="0.3" if f else "white",
            label=f"rate {_rate_label(rt)}",
        )
        for rt, f in sorted(fast_of.items())
    ]
    axc.legend(
        handles=[
            Line2D([], [], color="0.3", marker="o", ls="-", label="peak (max smoothed σ)"),
            Line2D([], [], color="0.3", marker="v", ls="--", label="flow (mean σ, ε 0.3–0.5)"),
        ]
        + rate_h,
        loc="upper right",
        ncols=2,
        fontsize=9,
        columnspacing=0.8,
    )
    lo, hi = axc.get_ylim()
    axc.set_ylim(lo, hi * 4)
    e_rub = EXPERIMENT["pe"].get("E_rubber_MPa")
    if e_rub:
        axd.axhline(e_rub, color="black", ls="--", lw=1.5)
        axd.text(18, e_rub + 40, f"amorphous PE rubber E ≈ 3G$_e$ ≈ {e_rub:g} MPa", fontsize=9.5)
    axd.axhline(0, color="0.6", lw=0.8)
    axd.set_xlabel("T (°C)")
    axd.set_ylabel(r"$E_{app}$ (MPa)")
    axd.legend(
        handles=[
            Line2D(
                [],
                [],
                color="0.3",
                marker="o",
                ls="",
                mfc="0.3" if f else "white",
                label=f"{_rate_label(rt)}: mean ± sd (x/y/z)",
            )
            for rt, f in sorted(fast_of.items())
        ]
        + [Line2D([], [], color="0.3", marker=".", ls="", alpha=0.5, label="single axes")],
        loc="lower left",
        fontsize=9,
    )
    axd.text(
        0.98,
        0.97,
        "not resolvable at this box size",
        transform=axd.transAxes,
        ha="right",
        va="top",
        fontsize=9.5,
        color="0.3",
    )
    info["rep"] = rep["label"]
    info["rates"] = rates
    info["sids"] = sorted({r["sid"] for r in runs})
    return save(fig, out, "fig7_mechanics"), info


# ================================================================== figure 8: holes
def hole_results(data: dict) -> list[dict]:
    out = []
    for sid in sorted(data["analysis"], key=_order):
        if "_hole" not in sid:
            continue
        for stage, res in sorted(data["analysis"][sid].items()):
            if res.get("frames") is not None and res.get("radius_nominal_nm") is not None:
                out.append({"sid": sid, "stage": stage, "res": res})
    return out


def _hole_label(r: dict) -> str:
    v = str(r.get("variant", "free"))
    v = "free" if v.startswith("free") else ("scaffold" + (", released" if "released" in v else ""))
    return f"R$_0$ {r['radius_nominal_nm']:g} nm, {float(r.get('t_c') or 0):g} °C, {v}"


def _built_holes(data: dict) -> list[str]:
    desc = []
    for sid in sorted(sid for sid in data["systems"] if "_hole" in sid):
        m = re.search(r"_r([0-9.]+)nm_([0-9]+)C", sid)
        if m:
            desc.append(f"R {m[1]} nm / {m[2]} °C" + (" (thin film)" if "rep441" in sid else ""))
    return desc


def hole_snapshots(data: dict) -> tuple[list[tuple[str, Path]], str]:
    """(label, data file) pairs for the snapshot strip: a hole run's ``inflated.data`` and its
    latest ``hole_<ns>ns.data``; else the --hole-preview directory (smoke test)."""

    def pick(d: Path) -> list[tuple[str, Path]]:
        out = []
        if (d / "inflated.data").is_file():
            out.append(("after inflation (open)", d / "inflated.data"))
        snaps = sorted(
            d.glob("hole_*ns.data"), key=lambda p: float(re.search(r"hole_([0-9.]+)ns", p.name)[1])
        )
        if snaps:
            ns = re.search(r"hole_([0-9.]+)ns", snaps[-1].name)[1]
            out.append((f"production, {ns} ns", snaps[-1]))
        return out

    for root in data["run_roots"]:
        for d in sorted(Path(root).glob("*_hole_*/*")):
            if d.is_dir() and len(pick(d)) == 2:
                return pick(d), f"{d.parent.name}/{d.name}"
    prev = data.get("hole_preview")
    if prev and Path(prev).is_dir() and len(pick(Path(prev))) == 2:
        return pick(Path(prev)), "smoke test"
    return [], ""


def hole_render(data: dict, snap: dict, name: str) -> tuple:
    """Top view (along -z) of a film with a hole: beads coloured by chain, cell outlined."""
    size = (1000, 1000)
    ctr = snap["lo"] + snap["L"] / 2
    pos = snap["pos"] - ctr
    i, j = snap["pairs"].T
    ok = np.all(np.abs(snap["pos"][i] - snap["pos"][j]) < 0.5 * snap["L"], axis=1)
    resi = snap["mol"] - snap["mol"].min()
    cols = chain_colors(snap["mol"])
    pal = np.zeros((resi.max() + 1, 3))
    pal[resi] = cols
    files = {"film.pdb": pr.pdb_text(pos, "C", resi, snap["pairs"][ok])}
    half = snap["L"][:2].max() / 2 + 3
    corners = pr.box_corners(-snap["L"] / 2, snap["L"] / 2)
    corners[:, 2] = snap["L"][2] / 2 + 5
    body = pr.style_lines(outline=False) + [
        "load film.pdb, film",
        "hide everything",
        f"alter film, vdw={SIGMA_HALF['bead']}",
        "rebuild",
        "show spheres",
        "set sphere_scale, 0.5",
        *pr.color_lines("film", pal, np.arange(len(pal)), "ch"),
        *pr.cgo_cylinders("cell", pr.box_edges(corners), 0.8, (0, 0, 0)),
        *pr.view_lines(half, half, *size, depth=snap["L"][2] + 50),
    ]
    return pr.render(name, files, body, _render_dir(data), size, data.get("render", True))


def _f8_snapshots(fig, spec, data, info) -> None:
    sub = spec.subgridspec(1, 2, wspace=0.02)
    axl, axr = fig.add_subplot(sub[0]), fig.add_subplot(sub[1])
    snaps, src = hole_snapshots(data)
    if not snaps:
        panel_label(axl, "a", "Hole snapshots (top view)")
        no_data(axl, "no hole snapshots\n(inflated.data, hole_<ns>ns.data)", pending=True)
        axr.set_axis_off()
        info["a"] = {"pending": True}
        return
    info["a"] = {"source": src, "files": [], "status": []}
    for k, (ax, (lab, path)) in enumerate(zip((axl, axr), snaps, strict=True)):
        snap = read_snapshot(path)
        tag = re.sub(r"[^A-Za-z0-9]+", "_", src)
        png, st = hole_render(data, snap, f"hole_{tag}_{path.stem}")
        title = "Hole snapshots (top view)" if k == 0 else ""
        if k == 0:
            show_render(ax, png, st, title, "a", lab)
        else:
            if png is None:
                no_data(ax, f"render not available ({st})")
            else:
                ax.imshow(autocrop(plt.imread(png)), interpolation="lanczos")
                ax.set_axis_off()
                ax.text(
                    0.0,
                    -0.02,
                    lab,
                    transform=ax.transAxes,
                    ha="left",
                    va="top",
                    fontsize=9.5,
                    color="0.3",
                )
        info["a"]["files"].append(_short(path))
        info["a"]["status"].append(st)
    if src == "smoke test":
        axr.text(
            1.0,
            1.02,
            "SMOKE TEST (ps-scale stages)",
            transform=axr.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="#B22222",
            fontweight="bold",
        )


def _f8_reff(ax, holes, info) -> None:
    panel_label(ax, "b", r"Hole radius $R_{eff}(t)$")
    info["b"] = []
    for h in holes:
        r = h["res"]
        fr = [f for f in r["frames"] if f.get("phase") == "production"]
        if not fr:
            continue
        free = str(r.get("variant", "free")).startswith("free")
        tc = float(r.get("t_c") or 0)
        ax.plot(
            [f["t_ns"] for f in fr],
            np.array([f["r_eff"] for f in fr]) / 10.0,
            color=t_color(tc),
            ls="-" if free else "--",
            label=_hole_label(r),
        )
        if r.get("t_close_ns") is not None:
            ax.plot(r["t_close_ns"], 0, marker="v", color=t_color(tc), ms=9, mec="black")
        info["b"].append(
            {
                "sid": h["sid"],
                "stage": h["stage"],
                "label": _hole_label(r),
                "t_close_ns": r.get("t_close_ns"),
                "rate": g(r, "rate_initial"),
            }
        )
    ax.set_xlabel("production time (ns, model time)")
    ax.set_ylabel(r"$R_{eff}$ (nm)")
    ax.set_ylim(bottom=-0.1)
    ax.legend(
        loc="upper right",
        fontsize=8.5,
        title="solid: free, dashed: scaffold; ▼ t$_{close}$",
        title_fontsize=8.5,
    )


def _f8_rz(ax, holes, info) -> None:
    panel_label(ax, "c", "R(z) through the film")
    h = next(
        (
            h
            for h in holes
            if any(f.get("slab_r") for f in h["res"]["frames"] if f.get("phase") == "production")
        ),
        None,
    )
    if h is None:
        no_data(ax, "no R(z) slabs stored", pending=True)
        return
    r = h["res"]
    fr = [f for f in r["frames"] if f.get("phase") == "production" and f.get("slab_r")]
    t_end = r.get("t_close_ns") or fr[-1]["t_ns"]
    fr = [f for f in fr if f["t_ns"] <= t_end] or fr
    idx = sorted({round(v) for v in np.linspace(0, len(fr) - 1, min(5, len(fr)))})
    cmap = plt.get_cmap("cividis")
    for k, i in enumerate(idx):
        f = fr[i]
        z = np.asarray(f["slab_z"], float)
        ax.plot(
            np.asarray(f["slab_r"], float) / 10,
            (z - z.mean()) / 10,
            marker="o",
            ms=4,
            color=cmap(k / max(len(idx) - 1, 1)),
            label=f"t = {f['t_ns']:.3g} ns",
        )
    ax.set_xlabel("R (nm)")
    ax.set_ylabel("z from the film centre (nm)")
    ax.set_xlim(left=0)
    ax.legend(loc="upper right", fontsize=9, title=_hole_label(r), title_fontsize=8.5)
    info["c"] = {"sid": h["sid"], "stage": h["stage"], "times": [fr[i]["t_ns"] for i in idx]}


def _f8_outcome(ax, holes, info) -> None:
    panel_label(ax, "d", "Closure vs R/h")
    rows = []
    for h in holes:
        r = h["res"]
        hh = r.get("film_thickness_angstrom")
        r0 = r.get("r_t0") or (r["radius_nominal_nm"] * 10)
        if not hh or not r0 or r.get("production_ns") is None and r.get("t_close_ns") is None:
            continue
        rows.append(
            {
                "sid": h["sid"],
                "stage": h["stage"],
                "x": r0 / hh,
                "t_c": float(r.get("t_c") or 0),
                "closed": r.get("t_close_ns") is not None,
                "t_close": r.get("t_close_ns"),
                "t_end": r.get("production_ns"),
                "free": str(r.get("variant", "free")).startswith("free"),
                "thin": "rep441" in h["sid"],
            }
        )
    info["d"] = rows
    if not rows:
        no_data(ax, "no hole runs with production frames", pending=True)
        return
    ax.axvspan(0.3, 1.0, color="0.5", alpha=0.12, lw=0)
    ax.axvline(1.0, color="black", ls="--", lw=1.3)
    ax.text(
        0.31,
        0.97,
        "R$_c$/h ≈ 0.3–1\n(Ilton 2016; Taylor &\nMichael 1973)",
        transform=ax.get_xaxis_transform(),
        fontsize=8.5,
        va="top",
    )
    top = max([q["t_close"] or 0 for q in rows] + [q["t_end"] or 0 for q in rows]) * 1.6 or 1
    for q in rows:
        y = q["t_close"] if q["closed"] else (q["t_end"] or top)
        ax.plot(
            q["x"],
            y,
            marker="o" if q["free"] else "s",
            ms=9,
            color=t_color(q["t_c"]),
            mfc=t_color(q["t_c"]) if q["closed"] else "white",
            mec="black" if q["thin"] else t_color(q["t_c"]),
            ls="",
        )
        if not q["closed"]:
            ax.annotate(
                "",
                xy=(q["x"], y * 1.5),
                xytext=(q["x"], y),
                arrowprops={"arrowstyle": "->", "color": t_color(q["t_c"])},
            )
    ys = [q["t_close"] if q["closed"] else (q["t_end"] or top) for q in rows]
    if max(ys) > 10 * max(min(ys), 1e-9):
        ax.set_yscale("log")
    else:
        ax.set_ylim(0, max(ys) * 1.8)
    ax.set_xlim(0, max(1.2, max(q["x"] for q in rows) * 1.15))
    ax.set_xlabel("R$_0$ / h (hole radius / film thickness)")
    ax.set_ylabel("t$_{close}$ or run length (ns, model time)")
    ts = sorted({q["t_c"] for q in rows})
    _t_legend(ax, ts, loc="lower right", title=None, fontsize=9)
    ax.legend(
        handles=[
            Line2D([], [], color="0.3", marker="o", ls="", label="closed (t$_{close}$)"),
            Line2D([], [], color="0.3", marker="o", mfc="white", ls="", label="open at run end"),
            Line2D([], [], color="0.3", marker="s", ls="", label="scaffolded"),
            Line2D([], [], color="0.6", marker="o", mec="black", ls="", label="thin film (4×4×1)"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.0, 0.8),
        fontsize=8.5,
    )


def fig8_holes(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig = plt.figure(figsize=FIG22, layout="constrained")
    gs = fig.add_gridspec(2, 2)
    info: dict = {}
    _f8_snapshots(fig, gs[0, 0], data, info)
    holes = hole_results(data)
    info["pending"] = not holes
    info["built"] = _built_holes(data)
    axes = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
    if not holes:
        built = info["built"]
        msg = "no `sepsim analyze hole` results yet"
        if built:
            msg += (
                "\nbuilt: "
                + "; ".join(built[:3])
                + (";\n" + "; ".join(built[3:]) if len(built) > 3 else "")
            )
        for ax, (letter, title) in zip(
            axes,
            (
                ("b", r"Hole radius $R_{eff}(t)$"),
                ("c", "R(z) through the film"),
                ("d", "Closure vs R/h"),
            ),
            strict=True,
        ):
            panel_label(ax, letter, title)
            no_data(ax, msg, pending=True)
    else:
        _f8_reff(axes[0], holes, info)
        _f8_rz(axes[1], holes, info)
        _f8_outcome(axes[2], holes, info)
    info["sids"] = sorted({h["sid"] for h in holes})
    return save(fig, out, "fig8_holes"), info


# ================================================================== captions
def _join(items) -> str:
    return "; ".join(i for i in items if i) or "none yet"


def caption_fig1(info: dict, data: dict) -> str:
    seg = info.get("seg") or {}
    d = info.get("d") or {}
    rend = info.get("render") or {}
    if seg.get("matched"):
        same = (
            f"the same segment at every resolution: carbons 1–{SEG_CARBONS} of the first chain of"
            f" the ua2aa box `{seg.get('aa_sid')}`, whose carbons coincide with the UA source"
            f" snapshot ``{seg.get('ua_path')}`` (max deviation {_fmt(seg.get('dev_A'), '.1g')} Å)"
        )
    elif seg:
        same = (
            f"carbons 1–{SEG_CARBONS} of the first chain of `{seg.get('aa_sid')}`; the UA panel"
            " uses the same carbon positions (ua2aa places AA carbons at the UA sites, D32), as"
            " the UA source snapshot is not available locally"
        )
    else:
        same = "no ua2aa AA box available"
    rows = info.get("f") or []
    return (
        "**Figure 1. Models and workflow.** "
        f"(a–c) PyMOL renders of {same}, rotated to its principal axes: (a) AA (OPLS) carbons"
        f" (green) with {seg.get('n_h', 'their')} explicit H; (b) UA (TraPPE) CH₂/CH₃ sites"
        " (σ/2 spheres, scaled; CH₃ end darker), with the CG bead positions of the same carbons"
        " as faint blue spheres; (c) CG (SDK): the centres of the same carbons in groups of 3"
        " (the SDK 3-carbon mapping; CT end bead darker) with the carbon backbone inside. Panel"
        " (c) is a geometric mapping of the segment, not a CG trajectory frame (the CG boxes were"
        " built independently). "
        f"(d) {d.get('label', 'CG')} bulk box ({d.get('n_chains', '?')} chains,"
        f" {d.get('beads', 0):,} beads, {_fmt(d.get('box_nm'), '.1f')} nm), chains coloured,"
        f" wrapped into the cell; from ``{d.get('source', 'n/a')}``. "
        "(e) Workflow: build (soft push-off for AA/UA; AA from the relaxed UA box, ua2aa) →"
        " 500 K NPT melt hold, extended until D47 passes (end-to-end ACF < 1/e and chain COM"
        " MSD ≥ 2⟨R<sub>g</sub>²⟩ at half the hold) → step-cool to 25 °C → heating sweep 25 →"
        " 160 °C (~10 °C steps, holds at 25/90/130/160 °C) → branches: 5 nm slit pore (cut"
        " from the 500 K box, D48), cylindrical hole through the pore film (D52), tensile"
        " pulls (D54), 300 ns long holds for chain diffusion (D53). "
        f"(f) Every current bulk and 5 nm pore system ({len(rows)} rows; colour = resolution):"
        " interaction sites, box edge (bulk: from the 25 °C hold density, else the latest run"
        " density; pores: the NVT box), total simulated time over all current runs"
        " (progress.json steps × timestep; CG times are model time) and the throughput of the"
        " main production run. Render status:"
        f" {', '.join(f'{k} {v}' for k, v in rend.items()) or 'n/a'}."
    )


DT_DEF = (
    "Δt is the time interval between the two compared frames, averaged over all time"
    " origins in the hold."
)


def caption_fig2(info: dict, data: dict) -> str:
    a = info.get("a") or []
    acf = _join(
        f"{r['label']} τ<sub>ee</sub> = {_fmt(r['t_1e_ns'], '.3g')} ns over"
        f" {_fmt(r['hold_ns'], '.4g')} ns"
        for r in a
    )
    c = info.get("c") or {}
    d = info.get("d") or {}
    return (
        "**Figure 2. Equilibration evidence.** (a, b) 500 K melt hold (prep + extension"
        " combined) per bulk system (colour = model, marker = polymer; dashed / open = CG PE"
        " C1500): (a) end-to-end vector autocorrelation"
        " ⟨**R**<sub>ee</sub>(t)·**R**<sub>ee</sub>(t+Δt)⟩/⟨R<sub>ee</sub>²⟩ with its 1/e"
        f" time (black-edged markers; {acf}; 'nan' = not reached: C1500 and the 5 ns AA"
        " preps); (b) chain COM MSD / ⟨R<sub>g</sub>²⟩ vs Δt with the D47 threshold 2 and"
        f" the value at half the hold (black-edged markers). {DT_DEF} CG and UA times are"
        " model times (CG ≈ 4.07× faster than real PE; UA needs its own mapping). The AA"
        " curves are the short ua2aa preps (AA conformations come from UA; validity: trend)."
        f" (c) {c.get('label', 'CG PE C240')} heating sweep: thinned density trace, holds"
        " shaded by T (dark band = analysis window: holds without their first 10 %, steps"
        " their second half; grey = step windows), black = block means ± SEM. (d) Slit-pore"
        " γ per surface: running mean over each hold's analysis window (drawn from 4 ns into"
        " it), colour = T, line style = box size (solid = 40 chains, dashed = 320 chains,"
        f" 2×2×2): {' and '.join(d.get('pores') or ['none'])}. The C<sub>n</sub> plateau vs"
        " time and the"
        " hold SEM vs block length are in appendix Fig. 2.1. Sources:"
        " results/analysis/*/{sweep,extend,pore}/results.json and the extend/prep"
        " progress.json ``hold`` curves."
        + validity_text(
            data, (info.get("sids") or []) + (d.get("sids") or []), ["chain500", "gamma"]
        )
    )


def caption_fig2_1(info: dict, data: dict) -> str:
    a = info.get("a") or []
    cn = _join(
        f"{r['label']} {_fmt(r['plateau'], '.3g')} ({_fmt(r['block_ns'], '.2g')} ns blocks)"
        for r in a
    )
    b = info.get("b") or {}
    return (
        "**Figure 2.1 (appendix). Chain-shape and density-error convergence.** (a) 500 K"
        " melt hold: C<sub>n</sub> plateau (mean C<sub>n</sub> over n ≥ 100 carbons) as"
        f" block means, each series cut into {CN_BLOCKS} equal-time blocks, ± the SEM of"
        " each block from the statistical inefficiency of its samples (D26), drawn at the"
        " block centre (log axis); dotted verticals = prep | extension boundary; dashed ="
        " melt C∞ ± 10 % (PE 6.7, iPP 6.15; D37). Whole-hold plateaus and block lengths:"
        f" {cn}. (b) {b.get('label', 'CG PE C240')} sweep holds: SEM of the hold mean"
        " density from block means vs block length (D55 check) against the reported SEM"
        " (dotted): the block SEM levels off only at 1–3 ns blocks (slow barostat/volume"
        " tail); D55 computes SEMs from 100 ps block means. At 130 and 160 °C the block SEM"
        " is still rising at the longest blocks, so the reported SEMs of those holds may be"
        " underestimated by 20–40 %."
    )


def caption_fig3(info: dict, data: dict) -> str:
    a = info.get("a") or {}
    holds = a.get("holds") or {}
    dens = _join(f"{k}: " + " / ".join(f"{r:.4f}" for _, r in v) for k, v in holds.items())
    b = info.get("b") or {}
    full = _join(
        f"{k} {v['full'][0]:.2f} ± {v['full'][1]:.2f}" for k, v in b.items() if v.get("full")
    )
    rng = _join(
        f"{k} {min(x[1] for x in v['local']):.1f}–{max(x[1] for x in v['local']):.1f}"
        for k, v in b.items()
        if v.get("local")
    )
    ipp = next((v["local"] for k, v in b.items() if "iPP" in k and v.get("local")), None)
    glass = ""
    if ipp:
        lo = [x for x in ipp if x[0] < 70]
        hi = [x for x in ipp if x[0] > 90]
        if lo and hi:
            glass = (
                f" UA iPP rises from {min(x[1] for x in lo):.1f}–{max(x[1] for x in lo):.1f}"
                f" below 70 °C to {min(x[1] for x in hi):.1f}–{max(x[1] for x in hi):.1f} above"
                " 90 °C: an apparent glass transition of the UA iPP model on this heating"
                " sweep (rate- and history-dependent), so its single 25–160 °C value is an"
                " average over two regimes."
            )
    kap = info.get("c") or {}
    kua = _join(
        f"{k} " + " / ".join(f"{v:.2f}" for _, v in rows)
        for k, rows in kap.items()
        if k.startswith("UA")
    )
    return (
        "**Figure 3. Bulk thermodynamics vs experiment** (colour = model, marker = polymer;"
        " solid / filled = 40 × C240 boxes, dashed / open = CG PE C1500; black = experiment;"
        " one shared legend). "
        f"(a) Density along the heating sweep at 1 atm, holds ± SEM as symbols ({dens} g/cm³"
        " at 25/90/130/160 °C). PE expt. (×): amorphous PE 0.852 / ≈0.814 / ≈0.790 /"
        " ≈0.774–0.781 g/cm³ at 25/90/130/160 °C, from the ATHAS data bank amorphous line"
        " (Gaur & Wunderlich 1981; the 25 °C point), SANS densities and a Tait fit (Padilha"
        " Júnior et al. 2015). CG PE is ≈2 % low (C1500 1–2 %): a force-field offset. No iPP"
        " density, κ<sub>T</sub> or α<sub>V</sub> reference is tabulated in"
        " docs/experiment_comparison.md yet, so UA iPP is shown without an experimental"
        " reference in (a–c). (b) Local α<sub>V</sub> (10⁻⁴ K⁻¹): for each window of"
        f" {ALPHA_WINDOW} consecutive sweep temperatures (≈40 K; 35 K where the window"
        " contains 90 °C, as the grid is 25, 35, …, 85, 90, 100, …, 160 °C) a linear V(T)"
        " fit weighted by 1/SEM² of the per-segment volume means (the hold where a T has"
        " both a step and a hold), α<sub>V</sub> = slope / mean V, error bar = 1σ from the"
        " unscaled fit covariance, drawn at the window's mean T (small x offsets per model)."
        f" Local ranges: {rng}.{glass} Full 25–160 °C fits (results.json fits.alpha_V,"
        f" Birge-scaled errors): {full}. Grey band: PE experiment 7.0–7.5 over 25–160 °C"
        " [derived from SANS densities / Tait]. (c) κ<sub>T</sub> from the hold volume"
        " fluctuations ± SEM; half-filled = the CG long holds (D53), which agree"
        " with the 25 ns holds; experiment 0.94 / 1.08 GPa⁻¹ at 130 / 160 °C (Tait fit of"
        " Sato PVT data [D]); CG is 50–60 % too compressible, UA closer"
        f" ({kua} GPa⁻¹ at 25/90/130/160 °C). The CG 90 and 130 °C values may be slight"
        " underestimates (κ<sub>T</sub> still rising at the end of the hold; appendix"
        " Fig. 3.2)."
        + (
            " Small markers joined by the plain line: κ<sub>T</sub> of each 5 ns sweep step"
            " over its second half (same estimator); steps are 5 ns, so their κ<sub>T</sub>"
            " is noisier."
            if info.get("c_steps")
            else ""
        )
        + " (d) Cooling-branch minus heating-branch"
        " density at the same T. Protocol: 500 K melt → cooled to 25 °C in 8 steps of 5 ns"
        " (≈25 K each) → heating sweep 25 → 160 °C in 10 °C steps with long holds at"
        " 25/90/130/160 °C; the comparison is at the cooling-step temperatures (25, 50, 76,"
        " 101, 126, 151 °C), the heating-branch density interpolated in T (sweep"
        " progress.json ``hysteresis``; error = cooling-step SEM). Classical C<sub>p</sub>"
        " and the chain-length effect are in appendix Fig. 3.1, convergence of the hold"
        " density and κ<sub>T</sub> in appendix Fig. 3.2."
        + validity_text(data, info.get("sids") or [], ["rho", "alpha", "kappa"])
    )


def caption_fig3_1(info: dict, data: dict) -> str:
    box = _join(
        f"{k} {d:+.3f} % at {t_label(t)} vs CG PE C240 (40 chains)"
        for k, rows in (info.get("b_box") or {}).items()
        for t, d in rows
    )
    return (
        "**Figure 3.1 (appendix). Heat capacity and chain length.** (a) Classical"
        " C<sub>p</sub> = dH/dT per fit window (thick: 25–90 / 90–160 °C, thin: 25–160 °C)"
        " vs the ATHAS melt lines (PE: 0.04325·T + 17.919 J mol⁻¹ K⁻¹ per CH₂; iPP:"
        " 0.151291·T + 42.956 per C₃H₆; Gaur & Wunderlich 1981): CG and UA remove degrees of"
        " freedom, so their classical C<sub>p</sub> is not comparable (validity: no); AA with"
        " the VDOS quantum correction (D12c) will be drawn dotted when its results.json"
        " provides it. (b) Chain-length effect: CG PE C1500 density relative to CG PE C240"
        " at the same set T (sweep segments ± combined SEM; diamond = 500 K melt hold): "
        + _join(
            f"{k} {min(v for _, v in rows):+.2f} to {max(v for _, v in rows):+.2f} %"
            for k, rows in (info.get("b") or {}).items()
            if rows
        )
        + " (longer chains: fewer chain ends, denser). α<sub>V</sub> per window: "
        + _join(
            f"{k} " + ", ".join(f"{w[0]:g}–{w[1]:g} °C {v:.2f}" for w, v in vv)
            for k, vv in (info.get("b_alpha") or {}).items()
        )
        + f". Box size (not drawn): {box}; the 2×2×2 (320-chain) box has no sweep, so the"
        " box-size check along T is the pore comparison of Fig. 5."
        + validity_text(data, info.get("sids") or [], ["cp"])
    )


def caption_fig3_2(info: dict, data: dict) -> str:
    rows = info.get("series") or {}
    dev = _join(f"{k} {max(abs(r['rho_dev_half']) for r in v):.2f} %" for k, v in rows.items() if v)
    kd = [
        100 * (r["kappa_end"] / r["kappa_stored"] - 1)
        for v in rows.values()
        for r in v
        if r.get("kappa_stored")
    ]
    kdev = f"{min(kd):+.0f} to {max(kd):+.0f} %" if kd else "n/a"
    samp = _join(
        f"{k} every {v[0]['dt_ps']:g} ps over {v[0]['hold_ns']:.0f} ns holds"
        for k, v in rows.items()
        if v
    )
    skipped = info.get("skipped") or []
    return (
        "**Figure 3.2 (appendix). Bulk sweep holds: properties vs simulation time.** Holds at"
        " 25/90/130/160 °C (colour = T; line style = model: "
        + ", ".join(
            f"{k} {n}"
            for k, n in zip(rows, ("solid", "dashed", "dash-dot", "dotted"), strict=False)
        )
        + "), from the thinned per-hold time series stored in the sweep results.json"
        f" ``convergence`` ({samp}), over the analysis window (after the hold's first 10 %),"
        " drawn from 0.5 ns into it. (a) Running (cumulative) mean density relative to the"
        " whole-window mean: at half the hold the running mean is within " + dev + " of the"
        " final value. (b) κ<sub>T</sub> = ⟨δV²⟩/(k<sub>B</sub>T⟨V⟩) from the volume"
        " fluctuations of a window growing from the analysis-window start to time t. In (b)"
        " the CG κ<sub>T</sub> at 90 and 130 °C is still rising at the end of the 25 ns"
        " holds (about 1.25 → 1.4–1.5 GPa⁻¹), while 25 and 160 °C level off. The volume"
        " fluctuates slowly enough that a 25 ns hold may not sample it fully, so those"
        " κ<sub>T</sub> values may be slight underestimates. These curves use the thinned"
        " series stored in results.json, whose final κ<sub>T</sub> differs from the"
        f" full-resolution value by up to ±13 % (here {kdev}), so read them for the trend,"
        " not the value. AA sweeps are not finished"
        + (f"; no convergence series for {', '.join(skipped)}" if skipped else "")
        + ". The run logs are not needed (results.json only)."
    )


STEP_CHAIN_TXT = (
    " Small open = 5 ns sweep steps (static properties over the second half of each step,"
    " joined to the holds by the plain line): in 5 ns at low T the chain shape is largely"
    " inherited (chains do not relax), so the steps mostly track the inherited conformation."
)


def _fill_txt(keys: dict) -> str:
    """Fig. 4 / 4.1 caption: what open / filled / diamond points are."""
    long = keys.get("long")
    txt = (
        " Open = sweep hold (chains inherited from 500 K: COM MSD < ⟨R<sub>g</sub>²⟩ in the"
        " hold, so the T dependence is not resolved; validity: trend);"
    )
    if long:
        lo, hi, cg = long
        txt += (
            f" filled = long hold (D53, {lo:.0f}–{hi:.0f} ns{', CG only' if cg else ''}; chains"
            " moved ≥ their own size; drawn at +4 °C);"
        )
    txt += " diamond = 500 K melt."
    return txt + (STEP_CHAIN_TXT if keys.get("steps") else "")


EXP_TXT = " Experiment in black with the polymer's marker (circle PE, square iPP)."


def caption_fig4(info: dict, data: dict) -> str:
    drift = [
        f"{k} {p['t_c']:g} °C: C<sub>n</sub> {p['cn_first']:.1f} → {p['cn_last']:.1f},"
        f" R<sub>g</sub> {p['rg_first']:.1f} → {p['rg_last']:.1f} Å"
        for k, pts in (info.get("long_drift") or {}).items()
        for p in pts
    ]
    return (
        "**Figure 4. Chain dimensions** (primary 40 × C240 boxes; colour = model, marker ="
        " polymer, diamond = 500 K melt, black = experiment; one shared legend). (a)"
        " R<sub>g</sub> and (b) C<sub>n</sub> plateau (n ≥ 100) ± SEM vs T: sweep holds (25"
        " ns CG, 10 ns UA), long holds and the 500 K melt."
        + _fill_txt(info.get("keys") or {})
        + " Long-hold drift from the first to the last 10 % of the hold: "
        + _join(drift)
        + "; the 25 °C CG long-hold rise of R<sub>g</sub> and C<sub>n</sub> goes with the"
        " onset of local ordering shown in appendix Fig. 4.1c. iPP chains are shorter in"
        " backbone (80 monomers, 160 backbone carbons), hence the smaller sizes."
        + EXP_TXT
        + " C240 PE R<sub>g</sub> 25–26.5 Å at 140 °C [D from ⟨R²⟩/M = 1.25 Å² mol/g], PE C∞"
        " 8.26 (25 °C) and 7.38 (140 °C) (Fetters, Lohse, Colby 2007) and the 500 K melt"
        " value 6.7 used by D37; iPP: only the 500 K melt C∞ = 6.15 (D37) is sourced (square,"
        " drawn just right of 500 K). CG PE C<sub>n</sub> of 10–14 vs the experimental 7.4 is"
        " a known CG over-stiffening (CG chains ≈20 % too large, a force-field property). (c)"
        " C<sub>n</sub>(n) internal-distance curves: CG PE C240 sweep holds (colour = T) and"
        " every system's 500 K melt (grey; line style = model; iPP curves end at 160 backbone"
        " carbons); dashed = PE C∞ 7.38 (140 °C). R<sub>ee</sub>, the C240 vs C1500"
        " ⟨R<sub>ee</sub>²⟩/M and the ordered-site fraction are in appendix Fig. 4.1."
        + validity_text(data, info.get("sids") or [], ["chain500", "chainT"])
    )


def caption_fig4_1(info: dict, data: dict) -> str:
    excess = []
    for k, rows in (info.get("b") or {}).items():
        v = [100 * (x / EXPERIMENT["pe"]["r2_over_m"]["value"] - 1) for _, _, x in rows]
        if v:
            excess.append(f"{k} {min(v):+.0f} to {max(v):+.0f} %")
    c = info.get("c") or {}
    fdrift = _join(
        f"{k} {t:g} °C {f0:.3f} → {f1:.3f}"
        for k, rows in c.items()
        if not k.endswith("film")
        for t, src, _, _, f0, f1 in rows
        if src == "long" and f0 is not None and f1 is not None
    )
    cryst = _join(
        f"{k}: "
        + ", ".join(
            f"{t_label(t)}{' long' if src == 'long' else ''} {v:.3f}"
            for t, src, v, *_ in rows
            if src != "step"
        )
        for k, rows in c.items()
        if not k.endswith("film")
    )
    return (
        "**Figure 4.1 (appendix). End-to-end distance, chain length and local order.**"
        " Symbols as in Fig. 4."
        + _fill_txt({"long": info.get("long"), "steps": info.get("steps")})
        + EXP_TXT
        + " (a) R<sub>ee</sub> = ⟨R<sub>ee</sub>²⟩<sup>1/2</sup> ± SEM vs T for the primary"
        " boxes; experiment: C240 PE R<sub>ee</sub> ≈ 65 Å at 140 °C [D from ⟨R²⟩/M = 1.25"
        " Å² mol/g, Fetters, Lohse, Colby 2007]. (b) ⟨R<sub>ee</sub>²⟩/M for CG PE C240 and"
        " C1500 (dashed) vs the PE melt value 1.25 Å² mol/g (140 °C; "
        + _join(excess)
        + "); the C1500 values are all inherited (D47 not reachable for C1500, validity:"
        " trend). (c) Ordered-site fraction (D26 local alignment, p2 ≥ 0.4, uncalibrated: a"
        " melt baseline, not a crystallinity) ± sd over frames: bulk sweep holds, long holds"
        f" and the 500 K melt ({cryst}) and the pore films (triangles, −4 °C). Long-hold first"
        f" → last frame: {fdrift}. The 25 °C CG long hold's largest ordered cluster grows to"
        " 672 of 3,200 beads (vs ≤ 492 in the sweep hold): the onset of local ordering that"
        " goes with its R<sub>g</sub> / C<sub>n</sub> rise in Fig. 4."
    )


def caption_fig5(info: dict, data: dict) -> str:
    a = info.get("a") or {}
    b = info.get("b") or {}
    gam = _join(
        f"{k}: dγ/dT = {_fmt(v.get('dgdT'), '.3f')} ± {_fmt(v.get('dgdT_err'), '.3f')} mN m⁻¹ K⁻¹"
        for k, v in b.items()
    )
    gl = EXPERIMENT["pe"]["gamma_line"]
    shallow = [
        100 * (1 - v["dgdT"] / gl["b"])
        for v in b.values()
        if v.get("dgdT") is not None and v.get("polymer") == "pe" and v.get("res") == "cg"
    ]
    slope = (
        f"CG dγ/dT is {min(shallow):.0f}–{max(shallow):.0f} % shallower than the Moreira slope"
        f" {gl['b']:g} mN m⁻¹ K⁻¹"
        if shallow
        else "no CG fit"
    )
    ua = [k for k, v in b.items() if v.get("res") != "cg"]
    ratios = [
        a_ / b_
        for v in (info.get("c") or {}).values()
        for a_, b_ in zip(v.get("surface_xy") or [], v.get("interior_xy") or [], strict=False)
        if a_ and b_
    ]
    mob = f"{min(ratios):.1f}–{max(ratios):.1f}" if ratios else "n/a"
    return (
        "**Figure 5. Dry 5 nm slit pores** (colour = model, marker = polymer; solid / filled"
        " = 40 chains, dashed / open = 320 chains (2×2×2); colour = T in (d); one shared"
        f" legend). (a) PyMOL side view along x of {a.get('label', 'the pore')} from"
        f" ``{a.get('source', 'n/a')}``: gap centred and shaded blue, the cell outlined in"
        " black with its chains coloured, periodic images (3 × 3 in y, z) in grey so the film"
        " reads as a continuous sheet. (b) γ per surface from the 25 ns holds ± SEM and the"
        f" SEM-weighted sweep fits ({gam}). Experiment (black line): LLDPE melt γ = 39.05 −"
        " 0.0725·t (Moreira et al. 2003). γ uses a plain 15 Å LJ cutoff without tail"
        " correction (cutoff-dependent); the 1–3 % agreement of γ partly reflects SDK being"
        f" fitted to γ; {slope}."
        + (
            f" UA pores: {', '.join(ua)}."
            if ua
            else " The UA PE and UA iPP 5 nm pores are not analysed yet and will appear when"
            " their results.json exist."
        )
        + " (c) Segment MSD per dimension at Δt = 1 ns by layer (surface = within 15 Å of a"
        " Gibbs surface; line style = layer in this panel): surface in-plane mobility is"
        f" {mob} × the interior; motion normal to the surface is suppressed. {DT_DEF} CG"
        " model times. (d) ⟨P2(cos θ<sub>z</sub>)⟩ of the bonds vs distance from the Gibbs"
        " surface: bonds lie parallel to the surface (negative) within ≈1.5 nm of it. The"
        " density profiles, chain shape and interfacial width are in appendix Fig. 5.1. The"
        " slit models a local patch of an amorphous wall; real separator pores are 30–100 nm,"
        " curved and semicrystalline."
        + validity_text(data, info.get("sids") or [], ["gamma", "film", "chainT", "segdyn"])
    )


def caption_fig5_1(info: dict, data: dict) -> str:
    return (
        "**Figure 5.1 (appendix). Slit-pore checks** (symbols and line styles as in Fig. 5)."
        " (a) Symmetrised ρ(z) per hold vs the distance from each film's own Gibbs dividing"
        " surface, so the 40- and 320-chain films overlay (colour = T); dotted = the bulk"
        " density at the same T: the film interior matches bulk within ≈0.2 %. (b) Chain"
        " shape R<sub>g,z</sub>²/(R<sub>g,xy</sub>²/2) of surface and interior chains (1 ="
        " isotropic): surface chains are flattened (≈0.2); the 40-chain film is thin enough"
        " that its interior chains are also compressed. (c) 10–90 % interfacial width from"
        " the profile (solid) and from the tanh fit (dotted): the interface broadens with T"
        " and is wider in the larger film."
    )


def caption_fig6(info: dict, data: dict) -> str:
    a = info.get("a") or {}
    dl = _join(
        f"{k} {t_label(p['t_c'])}: {p['D_shown']:.2g} cm²/s"
        + (f" (model {p['D']:.2g})" if p["factor"] != 1 else "")
        for k, pts in a.items()
        for p in pts
        if not p["bound"]
    )
    return (
        "**Figure 6. Chain dynamics** (colour = model, marker = polymer; one shared legend)."
        " **Time convention (this figure and appendix Fig. 6.1):** CG times are multiplied by"
        " 4.07 (and D divided by 4.07) to approximate real PE time (SDK PE dynamics ≈ 4.07×"
        " faster; Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019; one constant"
        " for every T and quantity, an approximation to be recalibrated against UA/AA); UA"
        " times are shown as simulated (no mapping yet; UA also runs fast without H"
        " friction); right axes give CG model time. (a) D<sub>COM</sub> vs T: filled where"
        " the COM MSD is diffusive and ≥ 2⟨R<sub>g</sub>²⟩ (D55 criterion; "
        + dl
        + "); open = MSD/(6Δt) at the longest Δt, an upper bound while the MSD is still"
        " sub-diffusive (each marker is one hold). Experiment (black circle): short PE melt ≈1.8"
        " × 10⁻⁷ cm²/s at 175 °C (Pearson et al. 1987, read from a graph, ±30 %). (b)"
        " τ<sub>ee</sub> (end-to-end 1/e, circles, solid) and Rouse τ<sub>1</sub> (triangles,"
        " dashed) vs 1000/T: the 25 ns sweep holds give exponential-fit extrapolations (open;"
        " not reached, order of magnitude, typically low); the long holds (black edge) and the"
        " 500 K extension reach 1/e. Segment MSD, the long-hold COM MSD, bond P2 times and the"
        " Rouse spectrum are in appendix Fig. 6.1."
        + validity_text(data, info.get("sids") or [], ["segdyn", "chaindyn"])
    )


def caption_fig6_1(info: dict, data: dict) -> str:
    b = info.get("b") or {}
    lh = _join(
        f"{k} {t_label(t)} {_fmt(ns, '.0f')} ns (MSD/⟨R<sub>g</sub>²⟩ {_fmt(m, '.2f')} at the"
        f" longest Δt{', diffusive' if dif else ''})"
        for k, rows in b.items()
        for t, ns, m, dif in rows
    )
    d = info.get("d") or {}
    sl = _join(f"{k} p^{v['slope']:.2f}" for k, v in d.items() if v.get("slope") is not None)
    return (
        "**Figure 6.1 (appendix). Dynamics curves** (time convention as in Fig. 6: CG × 4.07"
        f" ≈ real, UA as simulated; colour = T, line style = model). {DT_DEF} (a)"
        " Backbone-site MSD vs Δt in the 25 ns sweep holds (grey = 500 K extension) with a"
        " t<sup>1/2</sup> (Rouse) guide. (b) Chain COM MSD / ⟨R<sub>g</sub>²⟩ vs Δt in the"
        f" long holds (D53; thick: {lh}) and the sweep holds (thin): only the long holds reach"
        " the diffusive t¹ regime beyond 2⟨R<sub>g</sub>²⟩. (c) Bond P2 1/e time vs 1000/T"
        " (top: °C; right: CG model time): bulk sweep holds (solid), the 500 K UA extension,"
        " and the pore surface layer (dashed) and interior (dotted): surface bonds reorient"
        " ≈2× faster. CG bead–bead vector, UA C–C bond (not the ¹³C NMR C–H vector). Long-hold"
        " P2 times are omitted: their 100 ps frames do not resolve the 1/e time (no D46"
        " bursts). (d) Rouse mode times τ<sub>p</sub> (p = 1–5) of the long holds and the UA"
        f" 500 K extension vs the Rouse p⁻² line; fitted exponents over the reached modes: {sl}"
        " (real melts: p<sup>−2.2…−2.4</sup>; C240 is near the entanglement length)."
    )


def caption_fig7(info: dict, data: dict) -> str:
    errs = [e for r in info.get("runs") or [] for e in (r.get("E_err") or []) if e is not None]
    sds = [g(r, "E", "sd") for r in info.get("runs") or [] if g(r, "E", "sd") is not None]
    noise = (
        f"fit errors {min(errs):.0f}–{max(errs):.0f} MPa, axis spread up to {max(sds):.0f} MPa"
        if errs and sds
        else "large"
    )
    return (
        f"**Figure 7. Mechanics ({info.get('rep', 'CG PE')} tensile, D54).** The box is"
        " stretched along x, y and z in turn from the same hold snapshot at a constant"
        " engineering strain rate with the lateral axes at 1 atm. (a, b) Axis-mean smoothed"
        " true stress vs strain at 25/90/130/160 °C (band = range over the three axes) at"
        " 10⁸ and 10⁹ s⁻¹. (c) Peak stress (max of the smoothed σ) and flow stress (mean σ over"
        " strain 0.3–0.5) vs T, mean ± sd over the axes; both scale with the rate (viscous"
        " flow stress ≈ 3η × rate), so they are not a yield stress. (d) Apparent modulus from"
        f" the slope up to strain 0.02: not resolvable at this box size ({noise}), against the"
        " ≈8 MPa of an amorphous PE rubber (E ≈ 3G<sub>e</sub>, G<sub>e</sub> = 2.6 MPa at"
        " 140 °C; Fetters, Lohse, Colby 2007); several axes give negative slopes. Amorphous"
        " melts above Tg at rates ~10⁹× faster than tests: T and rate trends only (validity:"
        " trend), **not comparable to semicrystalline separator data** (Celgard E ≈ 0.25 GPa,"
        " tensile strength ≈ 165 MPa MD; Gor et al. 2014)."
        + validity_text(data, info.get("sids") or [], ["tensile"])
    )


def caption_fig8(info: dict, data: dict) -> str:
    a = info.get("a") or {}
    if a.get("pending"):
        snap = "(a) pending: no hole snapshots (``inflated.data``, ``hole_<ns>ns.data``) found."
    else:
        smoke = a.get("source") == "smoke test"
        snap = (
            "(a) PyMOL top views (along z, chains coloured, cell outlined) of a hole run: after"
            " inflation (hole open) and the latest production snapshot"
            + (
                " — **smoke test** (R = 3 nm, 160 °C, 2×2×2 film; 2 ns inflation, 1 ns"
                " scaffolded hold, released at t₀, 1 ns free; ps-scale stages, not a"
                " production run): the hole closed within ≈0.05 ns of the release."
                if smoke
                else f" ({a.get('source')})."
            )
        )
    if info.get("pending"):
        rest = (
            " (b–d) **Pending**: no ``sepsim analyze hole`` results.json yet (built: "
            + _join(info.get("built") or [])
            + "). When they appear: (b) R<sub>eff</sub> = √(A/π) of the projected hole vs"
            " production time (colour = T; solid free, dashed scaffolded; ▼ = t<sub>close</sub>);"
            " (c) R(z) through the film at up to five times before closure (one run); (d)"
            " closure outcome vs R₀/h: t<sub>close</sub> (filled) or run length (open, still"
            " open), with the expected critical R<sub>c</sub>/h ≈ 0.3–1 (Taylor & Michael 1973;"
            " Ilton et al. 2016) and the 4×4×1 thin-film (rep441) critical-size scan marked."
        )
    else:
        rest = (
            " (b) R<sub>eff</sub> = √(A/π) of the projected hole vs production time (colour ="
            " T; solid free, dashed scaffolded; ▼ = t<sub>close</sub>). (c) R(z) per 10 Å slab"
            " through the film at up to five times before closure. (d) t<sub>close</sub>"
            " (filled) or run length (open: still open) vs R₀/h; band = the expected critical"
            " R<sub>c</sub>/h ≈ 0.3–1 (Taylor & Michael 1973; Ilton et al. 2016); black edge ="
            " thin film (4×4×1)."
        )
    return (
        "**Figure 8. Cylindrical hole through the free film (D52).** "
        + snap
        + rest
        + " CG model times: compare runs with each other, not with experiment; the scaffold"
        " is imposed springs, not crystallinity, and releasing it emulates melting."
    )


CAPTIONS = {
    "fig1_models": caption_fig1,
    "fig2_equilibration": caption_fig2,
    "fig3_thermo": caption_fig3,
    "fig4_chains": caption_fig4,
    "fig5_pore": caption_fig5,
    "fig6_dynamics": caption_fig6,
    "fig7_mechanics": caption_fig7,
    "fig8_holes": caption_fig8,
}
# appendix figures (``<out>/appendix/``): name -> (parent figure, caption); their info is
# ``infos[parent]["appendix"][name]``
APPENDIX_CAPTIONS = {
    "fig2_1_cn_sem": ("fig2_equilibration", caption_fig2_1),
    "fig3_1_cp_chain_length": ("fig3_thermo", caption_fig3_1),
    "fig3_2_convergence": ("fig3_thermo", caption_fig3_2),
    "fig4_1_ree_length": ("fig4_chains", caption_fig4_1),
    "fig5_1_pore_checks": ("fig5_pore", caption_fig5_1),
    "fig6_1_dynamics_curves": ("fig6_dynamics", caption_fig6_1),
}


def write_readme(out: Path, infos: dict, data: dict) -> Path:
    lines = [
        "# Result figures",
        "",
        (
            "Regenerate: `uv run --frozen python scripts/presentation_figures.py --runs"
            " /home/rdyu/projects/che126_sims/results/runs --runs results/run_sidecars --runs"
            " /home/rdyu/projects/che126_sims/results/progress/rdyu-rog [--hole-preview DIR]`"
            " (reads only results/analysis/**/results.json, systems/*/manifest.yaml and"
            " data.lmp, the run progress.json copies and local run snapshots; panels without"
            " data show a PENDING placeholder and fill in once their results.json appear)."
            " Each figure is PNG (300 dpi), PDF and SVG; molecular renders use PyMOL and are"
            " cached in [renders/](renders/). Experimental values and sources:"
            " [docs/experiment_comparison.md](../../docs/experiment_comparison.md); per-system"
            ' validity: [summary](../summary.md) ("Physical validity by system"), rules in'
            " scripts/validity.py."
        ),
        "",
        (
            "Style: colour = resolution (CG blue, UA vermillion, AA green), marker = polymer"
            " (PE circle, iPP square), open/dashed = C1500 or a replicated (320-chain) box,"
            " black = experiment; in temperature-resolved panels colour = T (25 °C dark violet"
            " → 160 °C orange, 500 K grey) and line style = resolution (CG solid, UA dashed,"
            " AA dotted); half-filled symbols = long holds (D53) where marked. Figures 2–4 use"
            " one shared legend row above the panels (series, then the line-style and"
            " marker-fill keys); a panel keeps an in-panel key only for what is unique to it."
            " MSD / ACF axes use the time interval Δt between the two compared frames,"
            " averaged over all time origins. Error bars are SEM unless stated. CG dynamics"
            " are model time (≈4.07× faster than real PE). Appendix figures (supporting"
            " panels) are in [appendix/](appendix/), captions at the end."
        ),
        "",
    ]
    for name, fn in CAPTIONS.items():
        if name not in infos:
            continue
        lines += [f"## {name}", "", f"![{name}]({name}.png)", "", fn(infos[name], data), ""]
        lines += [
            f"Files: [{name}.png]({name}.png), [{name}.pdf]({name}.pdf), [{name}.svg]({name}.svg)",
            "",
        ]
    app = [
        (name, parent, fn)
        for name, (parent, fn) in APPENDIX_CAPTIONS.items()
        if name in (infos.get(parent) or {}).get("appendix", {})
    ]
    if app:
        lines += ["## Appendix", ""]
    for name, parent, fn in app:
        f = f"{APPENDIX}/{name}"
        lines += [f"### {name}", "", f"![{name}]({f}.png)", ""]
        lines += [fn(infos[parent]["appendix"][name], data), ""]
        lines += [f"Files: [{name}.png]({f}.png), [{name}.pdf]({f}.pdf), [{name}.svg]({f}.svg)", ""]
    p = out / "README.md"
    p.write_text("\n".join(lines).rstrip() + "\n")
    return p


# ================================================================== main
FIGURES = {
    "fig1": ("fig1_models", fig1_models),
    "fig2": ("fig2_equilibration", fig2_equilibration),
    "fig3": ("fig3_thermo", fig3_thermo),
    "fig4": ("fig4_chains", fig4_chains),
    "fig5": ("fig5_pore", fig5_pore),
    "fig6": ("fig6_dynamics", fig6_dynamics),
    "fig7": ("fig7_mechanics", fig7_mechanics),
    "fig8": ("fig8_holes", fig8_holes),
}


def load_data(
    analysis: Path,
    systems: Path,
    run_roots: list[Path],
    out: Path | None = None,
    render: bool = True,
    hole_preview: Path | None = None,
) -> dict:
    ana = ss.load_analysis(analysis)
    sysm = ss.load_systems(systems)
    roots = [r for r in run_roots if r.is_dir()]
    data = {
        "analysis": ana,
        "systems": sysm,
        "runs": ss.load_runs(roots),
        "run_roots": roots,
        "systems_root": systems,
        "ids": set(ana) | set(sysm),
        "out": out or ROOT / "results" / "presentation",
        "render": render,
        "hole_preview": hole_preview,
    }
    try:
        data["ctx"] = ss.build_context(roots, analysis, systems)
    except Exception:  # noqa: BLE001 - captions then omit the validity verdicts
        data["ctx"] = None
    return data


def build(data: dict, out: Path, only: list[str] | None = None, log=print) -> dict:
    data["out"] = out
    infos, written = {}, []
    for key, (name, fn) in FIGURES.items():
        if only and key not in only and name not in only:
            continue
        paths, info = fn(data, out)
        infos[name] = info
        written += paths
        for stem in dict.fromkeys(p.with_suffix("") for p in paths):
            log(
                f"wrote {stem}.{{{','.join(p.suffix[1:] for p in paths if p.with_suffix('') == stem)}}}"
            )
    readme = write_readme(out, infos, data) if not only else None
    if readme:
        log(f"wrote {readme}")
    return {"infos": infos, "written": written, "readme": readme}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--analysis", default="results/analysis")
    ap.add_argument("--systems", default="systems")
    ap.add_argument(
        "--runs",
        action="append",
        help="run root(s) for progress.json and snapshots (default results/runs,"
        " results/run_sidecars, results/progress/rdyu-rog)",
    )
    ap.add_argument("--out", default="results/presentation")
    ap.add_argument("--only", nargs="+", metavar="FIG", help="e.g. fig1 fig3 (no README)")
    ap.add_argument("--no-render", action="store_true", help="skip PyMOL (cached renders reused)")
    ap.add_argument(
        "--hole-preview",
        help="hole run directory (inflated.data + hole_<ns>ns.data) for a labelled smoke-test"
        " preview in fig8 (a) when no hole run snapshot is found",
    )
    a = ap.parse_args(argv)
    runs = a.runs or ["results/runs", "results/run_sidecars", "results/progress/rdyu-rog"]
    out = ss._path(a.out)
    data = load_data(
        ss._path(a.analysis),
        ss._path(a.systems),
        [ss._path(r) for r in runs],
        out=out,
        render=not a.no_render,
        hole_preview=Path(a.hole_preview) if a.hole_preview else None,
    )
    build(data, out, a.only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
