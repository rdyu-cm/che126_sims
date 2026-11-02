"""Presentation figures (one slide each) from the committed analysis outputs.

    uv run --frozen python scripts/presentation_figures.py [--analysis DIR] [--systems DIR]
        [--runs DIR ...] [--out DIR] [--only fig1 ...]

Writes ``<out>/<name>.png`` (300 dpi), ``.pdf`` and ``.svg`` plus ``<out>/README.md`` (one
caption per figure) into ``results/presentation/`` by default:

- ``fig1_convergence``: sweep density vs time with the analysis windows, SEM vs block
  length per hold, 500 K end-to-end vector ACF, pore surface-tension running means;
- ``fig2_properties_vs_T``: density, alpha_V / kappa_T, gamma(T) and relaxation times
  (Arrhenius axis) against the experimental values of docs/experiment_comparison.md;
- ``fig3_structures``: bulk box and slit-pore snapshots, rho(z) across the film, the
  cylindrical-hole radius (or a "pending" panel);
- ``fig4_mechanics``: CG tensile stress-strain curves, peak/flow stress and E_app vs T.

Inputs are only ``<analysis>/<system>/<stage>/results.json``, ``systems/*/manifest.yaml``
and ``data.lmp``, the run ``progress.json`` copies (``results/run_sidecars``,
``results/progress/rdyu-rog``) and, where present locally, ``results/runs`` snapshots
(``hold_<T>C.data``). Series are found by system id (``<polymer>_<res>_amorph_...``,
``..._pore_w5nm_...``, ``..._hole_...``), so UA/AA and iPP results appear once their
results.json exist. Colour = resolution, marker = polymer, black = experiment.
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
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
import summarize_systems as ss

from sepsim.build.datafile import read_data_file

ROOT = ss.ROOT
FORMATS = ("png", "pdf", "svg")
DPI = 300
FIGSIZE = (13.33, 7.5)  # a 16:9 slide
CG_TIME_FACTOR = 4.07  # SDK PE dynamics are ~4.07x faster than real PE (Hall et al. 2019)
INV_E = float(np.exp(-1.0))
HOLD_TS = (25.0, 90.0, 130.0, 160.0)

RES_COLOR = {"cg": "#0072B2", "ua": "#D55E00", "aa": "#009E73"}  # Okabe-Ito
RES_NAME = {"cg": "CG", "ua": "UA", "aa": "AA"}
POLY_MARKER = {"pe": "o", "ipp": "s"}
POLY_NAME = ss.POLYMER_NAME
EXP_KW = {"color": "black", "zorder": 1}

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 12,
        "legend.fontsize": 9.5,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "lines.linewidth": 1.6,
        "lines.markersize": 6,
        "errorbar.capsize": 2.5,
        "legend.frameon": False,
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
        "gamma_line": {  # LLDPE melt: gamma = a + b * t(C), mN/m [V]
            "a": 39.05,
            "b": -0.0725,
            "source": "LLDPE melt, Moreira et al. 2003",
        },
        "gamma_points": {  # Wu compilation, unverified
            "points": [(25.0, 35.4), (90.0, 31.7), (130.0, 29.4), (160.0, 27.7)],
            "source": "Wu compilation (unverified)",
        },
        "D_com": {  # cm^2/s, short PE melt, read from a graph (+-30 %)
            "t_c": 175.0,
            "value": 1.8e-7,
            "rel_err": 0.30,
            "source": "Pearson et al. 1987",
        },
        # amorphous rubber E ~ 3 G_e, G_e = 2.6 MPa at 140 C (Fetters, Lohse, Colby 2007)
        "E_rubber_MPa": 8.0,
    },
    "ipp": {},
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
    if rep or p["n"] != 40:
        variant.append(f"{p['n']} chains")
    primary = not variant
    label = f"{RES_NAME[p['res']]} {POLY_NAME.get(p['polymer'], p['polymer'])}"
    if variant:
        label += " " + ", ".join(variant)
    color = RES_COLOR.get(p["res"], "0.4")
    return p | {
        "sid": sid,
        "label": label,
        "primary": primary,
        "color": color,
        "marker": POLY_MARKER.get(p["polymer"], "D"),
        "mfc": color if primary else "white",
        "ls": "-" if primary else "--",
    }


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


# ------------------------------------------------------------------ helpers
def t_color(t_c: float) -> tuple:
    """Temperature colour (25 C dark violet .. 160 C orange), shared by every T legend."""
    frac = (float(t_c) - 25.0) / (160.0 - 25.0)
    return plt.get_cmap("plasma")(0.08 + 0.72 * min(max(frac, 0.0), 1.0))


def panel_label(ax, letter: str, title: str = "") -> None:
    ax.set_title(f"({letter}) {title}".rstrip(), loc="left", fontweight="bold", fontsize=12)


def no_data(ax, msg: str) -> None:
    ax.text(
        0.5,
        0.5,
        msg,
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=11,
        color="0.35",
        wrap=True,
        bbox={"boxstyle": "round,pad=0.6", "fc": "0.96", "ec": "0.75", "ls": "--"},
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


def chain_relax_500k(sid: str, data: dict) -> dict | None:
    """500 K end-to-end vector ACF of the combined prep hold + extension: the extend
    analysis (``traj.curves``) if it has a trajectory, else the extend run's progress.json
    ``hold.curves`` (``sepsim progress``)."""
    res = g(data["analysis"], sid, "extend")
    tr = g(res, "traj")
    if g(tr, "available") and g(tr, "curves", "ree_acf"):
        c = tr["curves"]
        return {
            "lag_ns": np.asarray(c["relax_lag_ps"], float) / 1000.0,
            "acf": np.asarray(c["ree_acf"], float),
            "t_1e_ns": (g(tr, "relaxation", "ree", "t_1e_ps") or np.nan) / 1000.0,
            "hold_ns": tr.get("hold_ns"),
            "p2_t_1e_ps": g(tr, "p2", "t_1e_ps"),
            "source": f"results/analysis/{sid}/extend/results.json",
        }
    runs = ss.current_runs(data["runs"].get(sid, {}))
    run = ss.latest(runs, "extend")
    hold = g(run, "progress", "hold")
    if not g(hold, "curves", "acf"):
        return None
    t1 = g(hold, "ree_acf", "t_1e_ns")
    return {
        "lag_ns": np.asarray(hold["curves"]["acf_lag_ns"], float),
        "acf": np.asarray(hold["curves"]["acf"], float),
        "t_1e_ns": np.nan if t1 is None else float(t1),
        "hold_ns": hold.get("hold_ns"),
        "p2_t_1e_ps": None,
        "source": f"{sid}/{run['dir']}/progress.json (hold.curves)",
    }


def _legend_handles(series: list[dict], extra: list | None = None) -> list:
    h = [
        Line2D(
            [],
            [],
            color=s["color"],
            marker=s["marker"],
            mfc=s["mfc"],
            ls=s["ls"],
            label=s["label"],
        )
        for s in series
    ]
    return h + (extra or [])


def _t_legend(ax, ts, loc="best", title="T", **kw) -> None:
    h = [Line2D([], [], color=t_color(t), lw=2.2, label=f"{t:g} °C") for t in ts]
    leg = ax.legend(handles=h, loc=loc, title=title, **kw)
    ax.add_artist(leg)


# ================================================================== figure 1
def fig1_convergence(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE, constrained_layout=True)
    info: dict = {}
    rep = main_bulk(data)
    _f1_sweep(axes[0, 0], rep, info)
    _f1_sem(axes[0, 1], rep, info)
    _f1_acf(axes[1, 0], data, info)
    _f1_gamma(axes[1, 1], data, info)
    return save(fig, out, "fig1_convergence"), info


def _f1_sweep(ax, rep, info) -> None:
    panel_label(ax, "a", "Bulk sweep: density vs time")
    if rep is None:
        no_data(ax, "no bulk sweep results.json")
        return
    res = rep["results"]["sweep"]
    conv = res.get("convergence") or []
    info["a"] = {"sid": rep["sid"], "label": rep["label"]}
    tset = []
    for c in conv:
        q = g(c, "quantities", "density")
        if not q:
            continue
        t = np.asarray(q["t_ps"], float) / 1000.0
        ax.plot(t, q["value"], color=rep["color"], lw=0.5, alpha=0.55, zorder=2)
        t0, t1 = c["t_start_ps"] / 1000.0, c["t_end_ps"] / 1000.0
        w0 = c["window"][0] / 1000.0
        if c["kind"] == "hold":
            tc = float(re.search(r"([0-9.]+) C", c["name"])[1])
            ax.axvspan(t0, t1, color=t_color(tc), alpha=0.10, lw=0, zorder=0)
            ax.axvspan(w0, t1, color=t_color(tc), alpha=0.18, lw=0, zorder=0)
            ax.text(
                0.5 * (t0 + t1),
                1.0,
                f"hold\n{tc:g} °C",
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=9,
                color=t_color(tc),
            )
            b = q.get("blocks") or []
            bt = [x["t"] / 1000.0 for x in b]
            ax.errorbar(
                bt,
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
        m = re.search(r"([0-9.]+) C", c["name"])
        if m:
            tset.append((t0, t1, float(m[1])))
    ax.set_xlabel("sweep time (ns, model time)")
    ax.set_ylabel(r"density (g cm$^{-3}$)")
    lo = min(min(g(c, "quantities", "density", "value") or [1]) for c in conv)
    hi = max(max(g(c, "quantities", "density", "value") or [0]) for c in conv)
    ax.set_ylim(lo - 0.003, hi + 0.25 * (hi - lo))
    ax.set_xlim(0, max(c["t_end_ps"] for c in conv) / 1000.0)
    handles = [
        Line2D([], [], color=rep["color"], lw=0.8, label=f"{rep['label']} (thinned trace)"),
        Line2D([], [], color="black", marker="o", ms=3, ls="", label="block means ± SEM"),
        plt.Rectangle((0, 0), 1, 1, fc="0.6", alpha=0.45, label="analysis windows"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=9)
    n_steps = sum(c["kind"] == "step" for c in conv)
    info["a"].update(n_steps=n_steps, n_holds=len(conv) - n_steps)


def _f1_sem(ax, rep, info) -> None:
    panel_label(ax, "b", "Hold SEM vs block length (density)")
    if rep is None:
        no_data(ax, "no bulk sweep results.json")
        return
    conv = [c for c in rep["results"]["sweep"].get("convergence") or [] if c["kind"] == "hold"]
    ts = []
    for c in conv:
        rows = g(c, "sem_vs_block", "density")
        if not rows:
            continue
        tc = float(re.search(r"([0-9.]+) C", c["name"])[1])
        ts.append(tc)
        bl = np.array([r["block_ps"] for r in rows]) / 1000.0
        sem = np.array([r["sem"] for r in rows]) * 1e5
        ax.plot(bl, sem, marker="o", color=t_color(tc), ms=5)
        ref = g(c, "quantities", "density", "sem")
        if ref:
            ax.axhline(ref * 1e5, color=t_color(tc), ls=":", lw=1.2)
    if not ts:
        no_data(ax, "no sem_vs_block in the sweep results.json")
        return
    ax.axvline(0.1, color="0.3", ls="--", lw=1)
    ax.text(0.105, 0.03, "100 ps blocks (D55)", transform=ax.get_xaxis_transform(), va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(0.07, None)
    ax.set_ylim(0, None)
    ax.set_xlabel("block length (ns)")
    ax.set_ylabel(r"SEM of the hold mean ($10^{-5}$ g cm$^{-3}$)")
    _t_legend(
        ax, ts, loc="upper left", title=f"{rep['label']} holds", ncols=2, bbox_to_anchor=(0.1, 1.0)
    )
    ax.legend(
        handles=[
            Line2D([], [], color="0.3", marker="o", label="SEM from n block means"),
            Line2D([], [], color="0.3", ls=":", label="reported SEM"),
        ],
        loc="lower right",
    )
    info["b"] = {"ts": ts}


def _f1_acf(ax, data, info) -> None:
    panel_label(ax, "c", "500 K chain relaxation: end-to-end vector ACF")
    bulk = [
        s
        for s in (series_info(sid) for sid in sorted(data["ids"], key=_order))
        if s and s["kind"] == "bulk" and not superseded(s["sid"], data["ids"])
    ]
    shown = []
    for s in bulk:
        if "rep" in s["suffix"] or s["suffix"].startswith("_from"):
            continue  # derived boxes: replicas / conversions of a shown box
        r = chain_relax_500k(s["sid"], data)
        if r is None:
            continue
        ok = r["lag_ns"] > 0
        ax.plot(
            r["lag_ns"][ok],
            r["acf"][ok],
            color=s["color"],
            ls=s["ls"],
            marker=s["marker"],
            mfc=s["mfc"],
            ms=4.5,
            markevery=0.12,
            label=s["label"],
        )
        if np.isfinite(r["t_1e_ns"]):
            ax.plot(r["t_1e_ns"], INV_E, marker="*", color=s["color"], ms=13, mec="black", mew=0.6)
        shown.append(s | {"relax": r})
    if not shown:
        no_data(ax, "no 500 K chain curves")
        return
    ax.axhline(INV_E, color="0.3", ls="--", lw=1)
    ax.text(0.012, INV_E + 0.02, "1/e", color="0.3")
    ax.set_xscale("log")
    ax.set_xlim(0.01, None)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("lag (ns, model time; CG real time ≈ 4.07×)")
    ax.set_ylabel(
        r"$\langle \mathbf{R}_{ee}(0)\cdot\mathbf{R}_{ee}(t)\rangle/\langle R_{ee}^2\rangle$"
    )
    h = _legend_handles(
        shown, [Line2D([], [], color="0.4", marker="*", ms=11, ls="", label="1/e time")]
    )
    ax.legend(handles=h, loc="lower left")
    info["c"] = [
        {
            "label": s["label"],
            "t_1e_ns": s["relax"]["t_1e_ns"],
            "hold_ns": s["relax"]["hold_ns"],
            "source": s["relax"]["source"],
        }
        for s in shown
    ]


def _f1_gamma(ax, data, info) -> None:
    panel_label(ax, "d", "Slit pore: surface tension running mean per hold")
    pores = find_series(data, "pore", "pore")
    if not pores:
        no_data(ax, "no pore results.json")
        return
    ts = set()
    rows = []
    for s in pores:
        res = s["results"]["pore"]
        for c in res.get("convergence") or []:
            if c["kind"] != "hold":
                continue
            q = g(c, "quantities", "gamma")
            if not q:
                continue
            tc = float(re.search(r"([0-9.]+) C", c["name"])[1])
            ts.add(tc)
            t = np.asarray(q["t_ps"], float)
            v = np.asarray(q["value"], float)
            sel = t >= c["window"][0] + 2000.0  # running mean after its first 2 ns
            tt = (t[sel] - c["t_start_ps"]) / 1000.0
            run = np.cumsum(v[sel]) / np.arange(1, sel.sum() + 1)
            ax.plot(tt, run, color=t_color(tc), ls=s["ls"], lw=1.6)
            b = [x for x in q.get("blocks") or [] if x["t"] >= c["window"][0]]
            ax.errorbar(
                [(x["t"] - c["t_start_ps"]) / 1000.0 for x in b],
                [x["mean"] for x in b],
                [x["sem"] for x in b],
                fmt=s["marker"],
                mfc=t_color(tc) if s["primary"] else "white",
                color=t_color(tc),
                ms=4,
                lw=0.7,
                alpha=0.6,
            )
            rows.append((s["label"], tc, q.get("mean"), q.get("sem")))
    if not ts:
        no_data(ax, "no hold gamma series in the pore results.json")
        return
    ax.set_xlabel("time in hold (ns, model time)")
    ax.set_ylabel(r"$\gamma$ (mN m$^{-1}$ per surface)")
    lo = min(r[2] for r in rows if r[2] is not None)
    hi = max(r[2] for r in rows if r[2] is not None)
    ax.set_ylim(lo - 5, hi + 5)
    _t_legend(ax, sorted(ts), loc="upper right", title="T", ncols=4)
    pl = [
        Line2D(
            [],
            [],
            color="0.3",
            ls=s["ls"],
            marker=s["marker"],
            mfc="0.3" if s["primary"] else "white",
            label=f"{s['label']} {s['width_nm']:g} nm pore",
        )
        for s in pores
    ]
    pl.append(Line2D([], [], color="0.3", lw=0, label="lines: running mean; symbols: blocks"))
    ax.legend(handles=pl, loc="lower right", fontsize=9)
    info["d"] = {"pores": [s["label"] for s in pores], "rows": rows}


# ================================================================== figure 2
def fig2_properties(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig = plt.figure(figsize=FIGSIZE, constrained_layout=True)
    gs = fig.add_gridspec(2, 2)
    info: dict = {}
    sweeps = find_series(data, "bulk", "sweep")
    _f2_density(fig.add_subplot(gs[0, 0]), sweeps, info)
    sub = gs[0, 1].subgridspec(2, 1, hspace=0.05)
    ax_a = fig.add_subplot(sub[0])
    ax_k = fig.add_subplot(sub[1], sharex=ax_a)
    _f2_alpha_kappa(ax_a, ax_k, sweeps, info)
    _f2_gamma(fig.add_subplot(gs[1, 0]), data, info)
    _f2_dynamics(fig.add_subplot(gs[1, 1]), data, sweeps, info)
    return save(fig, out, "fig2_properties_vs_T"), info


def _exp_polymers(series: list[dict]) -> list[str]:
    return sorted({s["polymer"] for s in series}, key=lambda p: ss.POLYMER_ORDER.get(p, 9))


def _f2_density(ax, sweeps, info) -> None:
    panel_label(ax, "a", "Density (1 atm)")
    if not sweeps:
        no_data(ax, "no bulk sweeps")
        return
    for s in sweeps:
        segs = s["results"]["sweep"].get("segments") or []
        t = [x["t_set_c"] for x in segs]
        rho = [g(x, "stats", "density", "mean") for x in segs]
        ax.plot(t, rho, color=s["color"], ls=s["ls"], lw=1.2, zorder=2)
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
    extra = []
    for pol in _exp_polymers(sweeps):
        e = EXPERIMENT.get(pol, {})
        if "density_athas" in e:
            (t1, r1), (t2, r2) = e["density_athas"]
            tk = np.linspace(298.15, 433.15, 50)  # linear in specific volume between the two
            v = 1 / r1 + (1 / r2 - 1 / r1) * (tk - t1) / (t2 - t1)
            ax.plot(tk - 273.15, 1 / v, color="black", lw=1, ls=":", zorder=1)
            extra.append(
                Line2D([], [], color="black", ls=":", label=f"{POLY_NAME[pol]} ATHAS amorphous")
            )
        if "density" in e:
            p = np.array(e["density"]["points"])
            ax.errorbar(p[:, 0], p[:, 1], p[:, 2], fmt="x", ms=8, mew=1.6, **EXP_KW)
            extra.append(
                Line2D([], [], color="black", marker="x", ls="", label=f"{POLY_NAME[pol]} expt.")
            )
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"$\rho$ (g cm$^{-3}$)")
    ax.legend(handles=_legend_handles(sweeps, extra), loc="upper right")
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


def _f2_alpha_kappa(ax_a, ax_k, sweeps, info) -> None:
    panel_label(ax_a, "b", r"Thermal expansion $\alpha_V$ and compressibility $\kappa_T$")
    if not sweeps:
        no_data(ax_a, "no bulk sweeps")
        ax_k.set_visible(False)
        return
    info["b"] = {"alpha": {}, "kappa": {}}
    n = len(sweeps)
    for i, s in enumerate(sweeps):
        off = (i - (n - 1) / 2) * 0.05
        for f in g(s, "results", "sweep", "fits", "alpha_V") or []:
            w0, w1 = f["window_c"]
            a, e = f["alpha_V_per_K"] * 1e4, (f.get("err") or 0) * 1e4
            full = (w1 - w0) > 100
            y = a + off * 0
            ax_a.plot(
                [w0, w1],
                [y, y],
                color=s["color"],
                ls=s["ls"],
                lw=1.0 if full else 3.0,
                alpha=0.6 if full else 1.0,
                solid_capstyle="butt",
            )
            if full:
                info["b"]["alpha"].setdefault(s["label"], []).append((w0, w1, a, e))
                continue
            ax_a.errorbar(
                0.5 * (w0 + w1) + off * 40,
                a,
                e,
                fmt=s["marker"],
                color=s["color"],
                mfc=s["mfc"],
                ms=5,
            )
            info["b"]["alpha"].setdefault(s["label"], []).append((w0, w1, a, e))
        hs = [h for h in g(s, "results", "sweep", "holds") or [] if h.get("kappa")]
        ax_k.errorbar(
            [h["t_c"] + off * 40 for h in hs],
            [h["kappa"]["kappa_T_GPa"] for h in hs],
            [h["kappa"].get("sem") or 0 for h in hs],
            fmt=s["marker"],
            color=s["color"],
            mfc=s["mfc"],
            ls=s["ls"],
            lw=1.2,
        )
        info["b"]["kappa"][s["label"]] = [(h["t_c"], h["kappa"]["kappa_T_GPa"]) for h in hs]
    for pol in _exp_polymers(sweeps):
        e = EXPERIMENT.get(pol, {})
        if "alpha_V" in e:
            lo, hi = e["alpha_V"]["band"]
            w0, w1 = e["alpha_V"]["window"]
            ax_a.fill_between([w0, w1], lo, hi, color="0.2", alpha=0.15, lw=0, zorder=0)
            ax_a.text(w1, hi, f"{POLY_NAME[pol]} expt. ", ha="right", va="bottom", fontsize=9)
        if "kappa_T" in e:
            p = np.array(e["kappa_T"]["points"])
            ax_k.plot(p[:, 0], p[:, 1], "x", ms=8, mew=1.6, **EXP_KW)
            ax_k.text(p[-1, 0] + 4, p[-1, 1], "expt.", va="center", fontsize=9)
    ax_a.set_ylabel(r"$\alpha_V$ ($10^{-4}$ K$^{-1}$)")
    ax_a.tick_params(labelbottom=False)
    ymin, ymax = ax_a.get_ylim()
    ax_a.set_ylim(min(ymin, 6.6), max(ymax, 7.8))
    ax_a.text(
        0.01,
        0.04,
        "thick: 25–90 / 90–160 °C fits, thin: 25–160 °C",
        transform=ax_a.transAxes,
        fontsize=8.5,
        color="0.35",
    )
    ax_k.set_ylabel(r"$\kappa_T$ (GPa$^{-1}$)")
    ax_k.set_xlabel("T (°C)")
    ax_k.set_xlim(15, 180)
    ax_k.set_ylim(0.8, None)


def _f2_gamma(ax, data, info) -> None:
    panel_label(ax, "c", r"Surface tension $\gamma(T)$, 5 nm slit pores")
    pores = find_series(data, "pore", "pore")
    if not pores:
        no_data(ax, "no pore results.json")
        return
    info["c"] = {}
    for i, s in enumerate(pores):
        res = s["results"]["pore"]
        hs = [x for x in res.get("segments") or [] if x.get("kind") == "hold"]
        off = (i - (len(pores) - 1) / 2) * 2.0
        tc = np.array([x["t_set_c"] for x in hs])
        gm = np.array([g(x, "stats", "gamma", "mean") for x in hs], float)
        ge = np.array([g(x, "stats", "gamma", "sem") or 0 for x in hs], float)
        ax.errorbar(tc + off, gm, ge, fmt=s["marker"], color=s["color"], mfc=s["mfc"], ms=6)
        fit = g(res, "fits", "sweep")
        if fit and fit.get("line"):
            b, a = fit["line"]
            tt = np.array(fit["window_c"])
            ax.plot(tt, a + b * (tt + 273.15), color=s["color"], ls=s["ls"], lw=1)  # fit in K
        info["c"][s["label"]] = {
            "holds": list(zip(tc.tolist(), gm.tolist(), ge.tolist(), strict=True)),
            "dgdT": g(fit, "dgamma_dT_mN_mK"),
            "dgdT_err": g(fit, "err"),
        }
    extra = []
    for pol in _exp_polymers(pores):
        e = EXPERIMENT.get(pol, {})
        if "gamma_line" in e:
            gl = e["gamma_line"]
            tt = np.array([25.0, 160.0])
            ax.plot(tt, gl["a"] + gl["b"] * tt, **EXP_KW, lw=1.2)
            extra.append(Line2D([], [], color="black", label=f"{POLY_NAME[pol]} {gl['source']}"))
        if "gamma_points" in e:
            p = np.array(e["gamma_points"]["points"])
            ax.plot(p[:, 0], p[:, 1], "x", ms=8, mew=1.6, **EXP_KW)
            extra.append(
                Line2D(
                    [],
                    [],
                    color="black",
                    marker="x",
                    ls="",
                    label=f"{POLY_NAME[pol]} {e['gamma_points']['source']}",
                )
            )
    handles = [
        Line2D(
            [],
            [],
            color=s["color"],
            marker=s["marker"],
            mfc=s["mfc"],
            ls=s["ls"],
            label=f"{s['label']} (holds ± SEM, sweep fit)",
        )
        for s in pores
    ]
    ax.legend(handles=handles + extra, loc="upper right")
    ax.set_xlabel("T (°C)")
    ax.set_ylabel(r"$\gamma$ (mN m$^{-1}$)")
    ax.set_xlim(15, 175)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo - 1, hi + 4)


def _relax_points(data: dict, s: dict) -> dict:
    """tau_ee (1/e of the end-to-end ACF), tau_P2 (bond P2 1/e) and D_COM per T for a bulk
    series: diffuse runs first (long holds), else the sweep holds; 500 K from the extend."""
    ana = data["analysis"].get(s["sid"], {})
    by_t: dict[float, dict] = {}
    sweep = ana.get("sweep") or {}
    for h in sweep.get("holds") or []:
        tr = h.get("traj") or {}
        if not tr.get("available"):
            continue
        r = by_t.setdefault(float(h["t_c"]), {})
        r["p2_ps"] = g(tr, "p2", "t_1e_ps")
        ree = g(tr, "relaxation", "ree") or {}
        if ree.get("reached") and ree.get("t_1e_ps"):
            r["ree_ns"], r["ree_src"] = ree["t_1e_ps"] / 1000.0, "sweep"
        elif ree.get("tau_fit_ps"):
            r["ree_ex_ns"] = ree["tau_fit_ps"] / 1000.0
    for stage, res in sorted(ana.items()):
        if not stage.startswith("diffuse_"):
            continue
        tr = res.get("traj") or {}
        if not tr.get("available") or res.get("t_c") is None:
            continue
        r = by_t.setdefault(float(res["t_c"]), {})
        ree = g(tr, "relaxation", "ree") or {}
        if ree.get("reached") and ree.get("t_1e_ps"):
            r["ree_ns"], r["ree_src"] = ree["t_1e_ps"] / 1000.0, stage
            r.pop("ree_ex_ns", None)
        if r.get("p2_ps") is None:
            r["p2_ps"] = g(tr, "p2", "t_1e_ps")
        com = tr.get("com_msd") or {}
        if com.get("diffusive") and com.get("D_cm2_s"):
            r["D"] = (
                com["D_cm2_s"],
                com.get("D_err_cm2_s"),
                stage,
                res.get("traj", {}).get("hold_ns"),
            )
    hot = chain_relax_500k(s["sid"], data)
    if hot is not None:
        r = by_t.setdefault(226.85, {})
        if np.isfinite(hot["t_1e_ns"]):
            r["ree_ns"], r["ree_src"] = hot["t_1e_ns"], "500 K extend"
        if hot.get("p2_t_1e_ps"):
            r["p2_ps"] = hot["p2_t_1e_ps"]
    return by_t


def _f2_dynamics(ax, data, sweeps, info) -> None:
    panel_label(ax, "d", "Dynamics: relaxation times (model time)")
    bulk = [
        s
        for s in (series_info(sid) for sid in sorted(data["ids"], key=_order))
        if s
        and s["kind"] == "bulk"
        and not superseded(s["sid"], data["ids"])
        and "rep" not in s["suffix"]
    ]
    info["d"] = {}
    plotted = []
    for s in bulk:
        pts = _relax_points(data, s)
        if not pts:
            continue
        ts = sorted(pts)
        x = np.array([1000.0 / (t + 273.15) for t in ts])
        ree = np.array([pts[t].get("ree_ns", np.nan) for t in ts], float)
        rex = np.array([pts[t].get("ree_ex_ns", np.nan) for t in ts], float)
        p2 = np.array([(pts[t].get("p2_ps") or np.nan) / 1000.0 for t in ts], float)
        any_pt = False
        for y, ls in ((ree, s["ls"]), (p2, ":")):
            ok = np.isfinite(y)
            if ok.any():
                ax.plot(x[ok], y[ok], marker=s["marker"], color=s["color"], mfc=s["mfc"], ls=ls)
                any_pt = True
        ok = np.isfinite(rex)
        if ok.any():
            ax.plot(
                x[ok], rex[ok], marker=s["marker"], color=s["color"], fillstyle="left", ls="", ms=8
            )
            any_pt = True
        if any_pt:
            plotted.append(s)
        info["d"][s["label"]] = pts
    if not plotted:
        no_data(ax, "no hold / diffuse / extend relaxation data")
        return
    ax.set_yscale("log")
    ax.set_xlabel(r"1000 / T (K$^{-1}$)")
    ax.set_ylabel("relaxation time (ns, model time)")
    ax.set_xlim(1.9, 3.45)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo / 1.5, hi * 40)
    top = ax.secondary_xaxis(
        "top",
        functions=(
            lambda v: 1000.0 / np.maximum(v, 1e-9) - 273.15,
            lambda c: 1000.0 / (np.asarray(c) + 273.15),
        ),
    )
    top.set_xticks([25, 90, 130, 160, 227])
    top.set_xlabel("T (°C)", fontsize=10)
    if any(s["res"] == "cg" for s in plotted):
        right = ax.secondary_yaxis(
            "right", functions=(lambda v: v * CG_TIME_FACTOR, lambda v: v / CG_TIME_FACTOR)
        )
        right.set_ylabel(r"CG × 4.07 ≈ real PE time (ns)", fontsize=10)
        ax.spines["right"].set_visible(True)
    ax.text(2.6, 4, r"$\tau_{ee}$: end-to-end vector 1/e", fontsize=9.5, color="0.25")
    ax.text(2.75, 4e-3, r"$\tau_{P2}$: bond reorientation 1/e", fontsize=9.5, color="0.25")
    extra = [
        Line2D([], [], color="0.3", ls="-", label=r"$\tau_{ee}$ (reached)"),
        Line2D(
            [],
            [],
            color="0.3",
            marker="o",
            fillstyle="left",
            ls="",
            label=r"$\tau_{ee}$ extrap. (fit)",
        ),
        Line2D([], [], color="0.3", ls=":", label=r"$\tau_{P2}$"),
    ]
    h = _legend_handles(plotted, extra)
    ax.legend(handles=h, loc="lower left", bbox_to_anchor=(0.0, 0.1), ncols=2, fontsize=9)
    # D_COM: diffusive runs only, with the CG time mapping and experiment
    lines = []
    for s in plotted:
        for t, r in sorted(info["d"][s["label"]].items()):
            if "D" not in r:
                continue
            d, _, _, _ = r["D"]
            txt = f"{s['label']} {t:g} °C: $D_{{COM}}$ = {d:.2g} cm$^2$/s"
            if s["res"] == "cg":
                txt += f" (÷4.07 → {d / CG_TIME_FACTOR:.2g})"
            lines.append(txt)
    e = EXPERIMENT.get("pe", {}).get("D_com")
    if lines and e:
        lines.append(
            f"expt. PE {e['t_c']:g} °C ≈ {e['value']:.2g} cm$^2$/s ±{e['rel_err']:.0%}"
            f" ({e['source']})"
        )
    if lines:
        ax.text(
            0.02,
            0.97,
            "\n".join(lines),
            transform=ax.transAxes,
            fontsize=8.5,
            va="top",
            bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": "0.7"},
        )


# ================================================================== figure 3
def chain_colors(mol: np.ndarray) -> np.ndarray:
    """Well-separated colour per molecule id (golden-ratio hue steps)."""
    ids, inv = np.unique(mol, return_inverse=True)
    pal = np.array(
        [colorsys.hsv_to_rgb((0.6 + 0.618034 * i) % 1.0, 0.75, 0.9) for i in range(len(ids))]
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


def snapshot(sid: str, data: dict, stage: str, prefer: str = "hold_25C.data") -> dict | None:
    """Wrapped positions, molecule ids, bonds and box of a system: a local run snapshot
    (``<runs>/<sid>/<stage>/<prefer>``) if present, else ``systems/<sid>/data.lmp``."""
    cands = [Path(r) / sid / stage / prefer for r in data["run_roots"]]
    cands.append(data["systems_root"] / sid / "data.lmp")
    path = next((p for p in cands if p.is_file()), None)
    if path is None:
        return None
    df = read_data_file(path)
    a = df.sorted_atoms()
    lo = np.array([b[0] for b in df.box])
    L = np.array([b[1] - b[0] for b in df.box])
    pos = lo + np.mod(df.unwrapped() - lo, L)
    bonds = df.topology("Bonds")
    pairs = bonds[:, 2:4] - 1 if bonds.shape[1] >= 4 else np.zeros((0, 2), int)
    return {
        "pos": pos,
        "mol": a[:, 1].astype(int),
        "pairs": pairs,
        "lo": lo,
        "L": L,
        "path": path,
        "local_run": path.name != "data.lmp",
    }


def _short(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return "/".join(path.parts[-5:])  # results/runs/<system>/<stage>/<file>


def fig3_structures(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig = plt.figure(figsize=FIGSIZE, constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.25])
    info: dict = {}
    _f3_bulk(fig.add_subplot(gs[0, 0], projection="3d"), data, info)
    _f3_pore(fig.add_subplot(gs[0, 1]), data, info)
    _f3_profile(fig.add_subplot(gs[1, 0]), data, info)
    _f3_hole(fig.add_subplot(gs[1, 1]), data, info)
    return save(fig, out, "fig3_structures"), info


def _f3_bulk(ax, data, info) -> None:
    rep = main_bulk(data)
    sid = rep["sid"] if rep else None
    snap = snapshot(sid, data, "sweep") if sid else None
    ax.set_title(
        f"(a) Bulk amorphous box, {rep['label'] if rep else ''}",
        loc="left",
        fontweight="bold",
        fontsize=12,
    )
    if snap is None:
        ax.set_axis_off()
        ax.text2D(0.5, 0.5, "no snapshot", transform=ax.transAxes, ha="center")
        return
    pos, L, lo = snap["pos"], snap["L"], snap["lo"]
    col = chain_colors(snap["mol"])
    i, j = snap["pairs"].T
    d = np.abs(pos[i] - pos[j])
    ok = np.all(d < 0.5 * L, axis=1)
    from mpl_toolkits.mplot3d.art3d import Line3DCollection

    segs = np.stack([pos[i[ok]], pos[j[ok]]], axis=1)
    lc = Line3DCollection(segs, colors=col[i[ok]], linewidths=1.3, alpha=0.95)
    lc.set_rasterized(True)
    ax.add_collection3d(lc)
    sc = ax.scatter(*pos.T, c=col, s=5, depthshade=True, edgecolors="none")
    sc.set_rasterized(True)
    hi = lo + L
    for a in range(3):  # box edges
        for b0 in (lo[(a + 1) % 3], hi[(a + 1) % 3]):
            for c0 in (lo[(a + 2) % 3], hi[(a + 2) % 3]):
                p = np.zeros((2, 3))
                p[:, a] = [lo[a], hi[a]]
                p[:, (a + 1) % 3] = b0
                p[:, (a + 2) % 3] = c0
                ax.plot(*p.T, color="black", lw=0.8)
    ax.set_box_aspect(tuple(L))
    ax.view_init(elev=22, azim=35)
    ax.set_axis_off()
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    n_chains = len(np.unique(snap["mol"]))
    ax.text2D(
        0.0,
        0.0,
        f"{n_chains} chains, {len(pos):,} beads; box {L[0] / 10:.1f} nm;"
        f" {'25 °C hold end' if snap['local_run'] else 'as built'}",
        transform=ax.transAxes,
        fontsize=9.5,
        color="0.3",
    )
    info["a"] = {
        "sid": sid,
        "label": rep["label"],
        "source": _short(snap["path"]),
        "local_run": snap["local_run"],
        "n_chains": n_chains,
        "beads": len(pos),
        "box_nm": float(L[0] / 10),
    }


def _main_pore(data) -> dict | None:
    pores = [s for s in find_series(data, "pore", "pore") if s["primary"]]
    if pores:
        return pores[0]
    ids = [sid for sid in sorted(data["systems"], key=_order)]
    for sid in ids:
        s = series_info(sid)
        if s and s["kind"] == "pore" and s["primary"]:
            return s
    return None


def _f3_pore(ax, data, info) -> None:
    pore = _main_pore(data)
    panel_label(ax, "b", f"Slit pore, side view along x{': ' + pore['label'] if pore else ''}")
    snap = snapshot(pore["sid"], data, "pore") if pore else None
    if snap is None:
        no_data(ax, "no pore snapshot")
        return
    pos, L, lo = snap["pos"].copy(), snap["L"], snap["lo"]
    zc = gap_center(pos[:, 2], lo[2], L[2])
    if zc is not None:  # gap mid-cell
        pos[:, 2] = lo[2] + np.mod(pos[:, 2] + lo[2] + L[2] / 2 - zc - lo[2], L[2])
    col = chain_colors(snap["mol"])
    shade = 0.55 + 0.45 * (pos[:, 0] - lo[0]) / L[0]  # depth cue along the line of sight
    colc = np.clip(col * shade[:, None], 0, 1)
    order = np.argsort(pos[:, 0])
    i, j = snap["pairs"].T
    d = np.abs(pos[i] - pos[j])
    ok = np.all(d < 0.5 * L, axis=1)
    ny, nz = 3, 3
    for iy in range(-(ny // 2), ny // 2 + 1):
        for iz in range(-(nz // 2), nz // 2 + 1):
            off = np.array([0.0, iy * L[1], iz * L[2]])
            p = pos + off
            segs = np.stack([p[i[ok]][:, [2, 1]], p[j[ok]][:, [2, 1]]], axis=1)
            lc = LineCollection(segs, colors=colc[i[ok]], linewidths=0.9, zorder=2)
            lc.set_rasterized(True)
            ax.add_collection(lc)
            sc = ax.scatter(p[order, 2], p[order, 1], c=colc[order], s=2.5, lw=0, zorder=3)
            sc.set_rasterized(True)
            rect = plt.Rectangle(
                (lo[2] + off[2], lo[1] + off[1]),
                L[2],
                L[1],
                fill=False,
                ec="black" if (iy, iz) == (0, 0) else "0.6",
                lw=1.6 if (iy, iz) == (0, 0) else 0.6,
                zorder=4,
            )
            ax.add_patch(rect)
    ax.set_aspect("equal")
    ax.set_xlim(lo[2] - L[2] - 3, lo[2] + 2 * L[2] + 3)
    ax.set_ylim(lo[1] - L[1] - 3, lo[1] + 2 * L[1] + 22)
    ax.set_xlabel("z (Å), across the film; gap centred (black: cell, grey: periodic images)")
    ax.set_ylabel("y (Å)")
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    width = g(data["systems"], pore["sid"], "pore", "nominal_width_nm")
    ax.annotate(
        "",
        xy=(lo[2] + L[2] / 2 + 25, lo[1] + L[1] * 2.0 + 2),
        xytext=(lo[2] + L[2] / 2 - 25, lo[1] + L[1] * 2.0 + 2),
        arrowprops={"arrowstyle": "<->", "color": "black", "lw": 1.2},
    )
    ax.text(
        lo[2] + L[2] / 2,
        lo[1] + L[1] * 2.0 + 3.5,
        f"gap ≈ {width:g} nm" if width else "gap",
        ha="center",
        va="bottom",
        fontsize=10,
    )
    ax.text(
        0.99,
        0.985,
        "25 °C hold end" if snap["local_run"] else "as built (500 K, before the sweep)",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color="0.25",
    )
    info["b"] = {
        "sid": pore["sid"],
        "label": pore["label"],
        "source": _short(snap["path"]),
        "local_run": snap["local_run"],
        "width_nm": width,
    }


def _f3_profile(ax, data, info) -> None:
    panel_label(ax, "c", r"Density profile $\rho(z)$ across the film vs bulk")
    pores = find_series(data, "pore", "pore")
    if not pores:
        no_data(ax, "no pore results.json")
        return
    ts = set()
    info["c"] = {}
    for s in pores:
        for h in s["results"]["pore"].get("holds") or []:
            p = g(h, "traj", "profile")
            if not p or not p.get("rho_sym"):
                continue
            tc = float(h["t_c"])
            ts.add(tc)
            z = np.asarray(p["z_A"], float) / 10.0
            ax.plot(z, p["rho_sym"], color=t_color(tc), ls=s["ls"], lw=1.4)
            bulk = g(h, "bulk", "density", "mean")
            if bulk:
                ax.axhline(bulk, color=t_color(tc), ls=":", lw=0.9, alpha=0.8)
            info["c"].setdefault(s["label"], []).append(
                (tc, g(p, "plateau", "mean"), bulk, p.get("film_gibbs_A"), p.get("gap_gibbs_A"))
            )
    if not ts:
        no_data(ax, "no rho(z) profiles stored")
        return
    ax.set_xlabel("z from the film centre (nm)")
    ax.set_ylabel(r"$\rho$ (g cm$^{-3}$)")
    ax.set_ylim(0, 1.08)
    ax.set_xlim(left=0)
    _t_legend(ax, sorted(ts), loc="upper right", title="T", ncols=2)
    h = [Line2D([], [], color="0.3", ls=s["ls"], label=f"{s['label']} film") for s in pores] + [
        Line2D([], [], color="0.3", ls=":", label="bulk density (same T)")
    ]
    ax.legend(handles=h, loc="center left")


def hole_results(data: dict) -> list[dict]:
    out = []
    for sid in sorted(data["analysis"], key=_order):
        if "_hole" not in sid:
            continue
        for stage, res in sorted(data["analysis"][sid].items()):
            if res.get("frames") is not None and res.get("radius_nominal_nm") is not None:
                out.append({"sid": sid, "stage": stage, "res": res})
    return out


def _f3_hole(ax, data, info) -> None:
    panel_label(ax, "d", r"Cylindrical hole: $R_{eff}(t)$, free vs scaffolded")
    holes = hole_results(data)
    if not holes:
        built = sorted(sid for sid in data["systems"] if "_hole" in sid)
        desc = []
        for sid in built:
            m = re.search(r"_r([0-9.]+)nm_([0-9]+)C", sid)
            if m:
                desc.append(f"R = {m[1]} nm at {m[2]} °C")
        msg = "Hole runs pending\n(no results/analysis/*hole*/ yet)"
        if desc:
            msg += "\n\nbuilt: " + "; ".join(desc[:3])
            if len(desc) > 3:
                msg += ";\n" + "; ".join(desc[3:])
        no_data(ax, msg)
        info["d"] = {"pending": True, "built": desc}
        return
    info["d"] = {"pending": False, "runs": []}
    for h in holes:
        r = h["res"]
        fr = [f for f in r["frames"] if f.get("phase") == "production"]
        if not fr:
            continue
        t = np.array([f["t_ns"] for f in fr])
        reff = np.array([f["r_eff"] for f in fr]) / 10.0
        tc = float(r.get("t_c") or 0)
        free = str(r.get("variant", "free")).startswith("free")
        lab = f"R₀ {r['radius_nominal_nm']:g} nm, {tc:g} °C, {r.get('variant', '')}"
        ax.plot(t, reff, color=t_color(tc), ls="-" if free else "--", label=lab)
        info["d"]["runs"].append(
            {"label": lab, "t_close_ns": r.get("t_close_ns"), "sid": h["sid"], "stage": h["stage"]}
        )
    ax.set_xlabel("production time (ns, model time)")
    ax.set_ylabel(r"$R_{eff}$ (nm)")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right", fontsize=8.5)


# ================================================================== figure 4
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


def fig4_mechanics(data: dict, out: Path) -> tuple[list[Path], dict]:
    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE, constrained_layout=True)
    runs = tensile_runs(data)
    info: dict = {"runs": []}
    if not runs:
        for ax in axes.flat:
            no_data(ax, "no tensile results.json")
        return save(fig, out, "fig4_mechanics"), info
    rep = next((r for r in runs if r["primary"]), runs[0])
    mine = [r for r in runs if r["sid"] == rep["sid"]]
    rates = sorted({r["rate"] for r in mine})
    ymax = 0.0
    for k, (ax, rate) in enumerate(zip(axes[0], rates[:2], strict=False)):
        panel_label(ax, "ab"[k], f"{rep['label']}: stress–strain at {_rate_label(rate)}")
        for r in sorted((r for r in mine if r["rate"] == rate), key=lambda r: r["t_c"]):
            x, m, lo, hi = axis_mean_curve(r["run"])
            ax.fill_between(x, lo, hi, color=t_color(r["t_c"]), alpha=0.18, lw=0)
            ax.plot(x, m, color=t_color(r["t_c"]), label=f"{r['t_c']:g} °C")
            ymax = max(ymax, float(hi.max()))
        ax.set_xlabel("engineering strain")
        ax.set_ylabel("true stress (MPa)")
        ax.axhline(0, color="0.6", lw=0.6)
        ax.legend(title="axis mean (band: x/y/z range)", loc="upper left", ncols=2)
    for ax in axes[0]:
        ax.set_ylim(-3, ymax * 1.25)
        ax.set_xlim(0, None)
    if len(rates) < 2:
        no_data(axes[0, 1], "second strain rate pending")
    # (c) peak / flow stress vs T, (d) E_app vs T: every tensile series
    axc, axd = axes[1]
    panel_label(axc, "c", "Peak and flow stress vs T")
    panel_label(axd, "d", r"Apparent modulus $E_{app}$ (fit to strain 0.02)")
    rate_mfc = {}
    for s_sid in dict.fromkeys(r["sid"] for r in runs):
        rs = [r for r in runs if r["sid"] == s_sid]
        s = rs[0]
        for rate in sorted({r["rate"] for r in rs}):
            sel = sorted((r for r in rs if r["rate"] == rate), key=lambda r: r["t_c"])
            fast = rate >= max(rates)
            mfc = s["color"] if fast else "white"
            rate_mfc[rate] = fast
            tc = np.array([r["t_c"] for r in sel])
            for key, ls, mk in (("peak_MPa", "-", s["marker"]), ("flow_MPa", "--", "v")):
                m = np.array([g(r["run"], "summary", key, "mean") for r in sel], float)
                sd = np.array([g(r["run"], "summary", key, "sd") or 0 for r in sel], float)
                axc.errorbar(tc, m, sd, fmt=mk, ls=ls, color=s["color"], mfc=mfc, lw=1.3)
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
                ms=7,
                lw=1.3,
                zorder=3,
            )
            for r in sel:
                ea = [a.get("E_MPa") for a in r["run"].get("axes") or []]
                axd.plot([r["t_c"] + dx] * len(ea), ea, ".", color=s["color"], alpha=0.5, ms=5)
            for r in sel:
                info["runs"].append(
                    {
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
    hc = [
        Line2D([], [], color="0.3", marker="o", ls="-", label="peak (max of smoothed σ)"),
        Line2D([], [], color="0.3", marker="v", ls="--", label="flow (mean σ, strain 0.3–0.5)"),
    ] + [
        Line2D(
            [],
            [],
            color="0.3",
            marker="o",
            ls="",
            mfc="0.3" if f else "white",
            label=f"rate {_rate_label(rt)}",
        )
        for rt, f in sorted(rate_mfc.items())
    ]
    axc.legend(handles=hc, loc="upper right", ncols=2, fontsize=9)
    lo, hi = axc.get_ylim()
    axc.set_ylim(lo, hi * 3)
    e_rub = EXPERIMENT["pe"].get("E_rubber_MPa")
    if e_rub:
        axd.axhline(e_rub, color="black", ls="--", lw=1.2)
        axd.text(
            18,
            e_rub + 45,
            f"amorphous PE rubber E ≈ 3G$_e$ ≈ {e_rub:g} MPa (Fetters et al.)",
            fontsize=9,
        )
    axd.axhline(0, color="0.6", lw=0.6)
    axd.set_xlabel("T (°C)")
    axd.set_ylabel(r"$E_{app}$ (MPa)")
    hd = [
        Line2D(
            [],
            [],
            color="0.3",
            marker="o",
            ls="",
            mfc="0.3" if f else "white",
            label=f"{_rate_label(rt)}: mean ± sd over x/y/z",
        )
        for rt, f in sorted(rate_mfc.items())
    ] + [Line2D([], [], color="0.3", marker=".", ls="", alpha=0.5, label="single axes")]
    axd.legend(handles=hd, loc="lower left", fontsize=9)
    info["rep"] = rep["label"]
    info["rates"] = rates
    return save(fig, out, "fig4_mechanics"), info


# ================================================================== captions
def _fmt(x, spec=".3g") -> str:
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else format(x, spec)


def caption_fig1(info: dict) -> str:
    a = info.get("a") or {}
    c = info.get("c") or []
    acf = "; ".join(
        f"{r['label']} τ_ee(1/e) = {_fmt(r['t_1e_ns'], '.3g')} ns over a {_fmt(r['hold_ns'], '.4g')}"
        f" ns hold"
        for r in c
    )
    pores = ", ".join((info.get("d") or {}).get("pores") or []) or "none yet"
    return (
        "**Figure 1. Equilibration evidence.** "
        f"(a) {a.get('label', 'Bulk')} heating sweep (25→160 °C, {a.get('n_steps', '?')} 5 ns"
        f" steps and {a.get('n_holds', '?')} 25 ns holds): thinned density trace; light"
        " colour = hold, darker band / grey = the analysis window (holds without their first"
        " 10 %, steps their second half, D49), black = 8 block means ± SEM per hold. "
        "(b) SEM of each hold's mean density from n = 128 … 4 block means vs block length,"
        " against the reported SEM (dotted). The block SEM rises from the 0.2 ns blocks and"
        " reaches the reported value at 1–3 ns blocks (the slow ≈1–2 ns barostat/volume tail"
        " found by the audit); the 4-block points scatter (only 4 samples). D55 therefore"
        " computes SEMs on 100 ps block means. "
        f"(c) End-to-end vector ACF at 500 K over the combined prep hold + extension ({acf});"
        " D47 requires ACF < 1/e and COM MSD ≥ 2⟨Rg²⟩ at half the hold. C1500 is shown as the"
        " long-chain case for which D47 is out of reach (accepted on a C_n no-drift rule)."
        " CG and UA times are model times (CG real ≈ 4.07× longer; UA needs its own mapping). "
        f"(d) Slit-pore surface tension per 25 ns hold ({pores}): running mean of the stored"
        " (thinned) γ series over the analysis window (drawn from 2 ns into the window, where"
        " the running mean of a few points is still noise) and the 8 per-segment block means ±"
        " SEM (symbols, inside the window). The stored series are thinned to ≤ 500 points"
        " per segment, so the running mean is that of the thinned trace, not of every"
        " thermo row. Sources: results/analysis/*/sweep|pore|extend/results.json"
        " (``convergence``, ``sem_vs_block``, ``traj.curves``) and the extend runs'"
        " progress.json ``hold.curves`` where the extend analysis has no trajectory."
    )


def caption_fig2(info: dict) -> str:
    a = info.get("a") or {}
    holds = a.get("holds") or {}
    cg = next((v for k, v in holds.items() if k == "CG PE"), None)
    dens = ""
    if cg:
        dens = (
            " (CG PE C240: " + " / ".join(f"{r:.4f}" for _, r in cg) + " g/cm³ at 25/90/130/160 °C)"
        )
    c = info.get("c") or {}
    gam = "; ".join(
        f"{k}: dγ/dT = {_fmt(v.get('dgdT'), '.3f')} ± {_fmt(v.get('dgdT_err'), '.3f')} mN m⁻¹ K⁻¹"
        for k, v in c.items()
    )
    return (
        "**Figure 2. Properties vs temperature, model vs experiment** (colour = resolution:"
        " CG blue, UA vermillion, AA green; marker = polymer: PE circle, iPP square; open /"
        " dashed = C1500 or a larger box; black = experiment). "
        f"(a) Density along the heating sweep; holds ± SEM as symbols{dens}. Experiment:"
        " amorphous PE 0.852 / ≈0.814 / ≈0.790 / ≈0.774–0.781 g/cm³ (ATHAS amorphous line,"
        " Gaur & Wunderlich 1981; SANS densities; Tait fit, Padilha Júnior et al. 2015) and"
        " the ATHAS two-point line (dotted). CG PE is ≈2 % low (C1500 1–2 %): a force-field"
        " offset with no principled correction (validity: comparable). No iPP reference values"
        " are tabulated yet in docs/experiment_comparison.md, so iPP series will appear"
        " without an experimental curve until they are added to ``EXPERIMENT``. "
        "(b) Top: α_V from the linear V(T) fits (thick bars: 25–90 and 90–160 °C windows,"
        " thin: 25–160 °C); V(T) is curved (χ²_red ≈ 21), so the windowed values are the ones"
        " to quote. Grey band: experiment 7.0–7.5 × 10⁻⁴ K⁻¹ [derived from SANS densities /"
        " Tait]; CG ≈5 % low. Bottom: κ_T from hold volume fluctuations vs experiment 0.94 /"
        " 1.08 GPa⁻¹ at 130 / 160 °C (Tait fit of Sato PVT data); CG is 50–60 % too"
        " compressible, typical of CG. "
        f"(c) γ per surface from the 25 ns holds of both 5 nm pores ± SEM and the sweep fits ({gam})."
        " Experiment: LLDPE melt γ = 39.05 − 0.0725·t (Moreira et al. 2003, solid line;"
        " drawn over the full range although the data are melt values) and the Wu compilation"
        " (crosses, unverified). γ uses a plain 15 Å LJ cutoff without tail correction, so it is"
        " cutoff-dependent; the agreement (1–3 %) partly reflects SDK being fitted to surface"
        " tension; dγ/dT is ≈20 % shallower than experiment. "
        "(d) Relaxation times on an Arrhenius axis (top: °C), in model time: τ_ee = 1/e time"
        " of the end-to-end vector ACF (solid; 300 ns diffuse runs at 25/90/160 °C, 500 K from"
        " the extension), open symbols = exponential-fit extrapolations where the ACF never"
        " reached 1/e in a 25 ns sweep hold (order of magnitude, typically an underestimate),"
        " τ_P2 = bond P2 1/e time (dotted; CG bead–bead vector, UA C–C bond: different"
        " vectors, not the ¹³C NMR C–H vector). Right axis: CG times × 4.07 ≈ real PE time"
        " (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019; the factor depends on"
        " T and should be recalibrated against UA/AA). The box lists D_COM only where the"
        " COM MSD is diffusive and ≥ 2⟨Rg²⟩, with the 4.07 mapping, next to Pearson et al."
        " 1987 (short PE melt, read from a graph, ±30 %). Validity: CG dynamics need the time"
        " correction (corr); the diffuse holds at 25/90 °C were interrupted (277/176 ns)."
    )


def caption_fig3(info: dict) -> str:
    a, b, _c, d = (info.get(k) or {} for k in "abcd")
    src_a = a.get("source", "n/a")
    src_b = b.get("source", "n/a")
    hole = (
        "(d) Placeholder: the cylindrical-hole production runs have not run yet"
        f" (built: {'; '.join(d.get('built') or []) or 'none'}). When"
        " results/analysis/*hole*/<stage>/results.json appear, this panel shows R_eff(t) of"
        " the production phase (solid = free, dashed = scaffolded), coloured by T."
        if d.get("pending", True)
        else "(d) Effective hole radius R_eff = √(A/π) of the projected hole vs production time"
        " (solid = free, dashed = scaffolded; colour = T). CG model times: compare runs with"
        " each other, not with experiment; the scaffold is a set of imposed springs, not"
        " crystallinity."
    )
    return (
        "**Figure 3. Structures.** "
        f"(a) {a.get('label', 'Bulk')} box ({a.get('n_chains', '?')} chains,"
        f" {a.get('beads', 0):,} beads, {_fmt(a.get('box_nm'), '.1f')} nm), each chain one colour,"
        f" bonds drawn, wrapped into the cell; from ``{src_a}``"
        f"{' (local run snapshot, end of the 25 °C hold)' if a.get('local_run') else ''}. "
        f"(b) {b.get('label', '')} {_fmt(b.get('width_nm'), 'g')} nm slit pore seen along x"
        " (z across the image), shifted along z so the gap is mid-cell, with 3 × 3 periodic"
        " images (y, z; grey outlines) so the film reads as a continuous sheet; depth-shaded;"
        f" from ``{src_b}``. "
        "(c) Symmetrised density profile ρ(z) about the film centre for every hold (colour ="
        " T; solid 40-chain, dashed 320-chain 2×2×2 pore), with the bulk density at the same"
        " T (dotted): the film interior matches bulk within ≈0.2 % (40 chains) and better for"
        " the thicker 320-chain film; interfaces are ≈6 Å wide (10–90 %). Film structure is a"
        " trend-level property (validity: trend); the slit is a local patch of an amorphous"
        " wall, whereas real separator pores are 30–100 nm, curved and semicrystalline. " + hole
    )


def caption_fig4(info: dict) -> str:
    errs = [e for r in info.get("runs") or [] for e in (r.get("E_err") or []) if e is not None]
    sds = [g(r, "E", "sd") for r in info.get("runs") or [] if g(r, "E", "sd") is not None]
    noise = (
        f"fit errors {min(errs):.0f}–{max(errs):.0f} MPa, axis spread up to {max(sds):.0f} MPa"
        if errs and sds
        else "large"
    )
    return (
        f"**Figure 4. Mechanics ({info.get('rep', 'CG PE')} tensile).** The box is stretched"
        " along x, y and z in turn from the same snapshot at a constant engineering strain"
        " rate with the lateral axes at 1 atm. (a, b) Axis-mean smoothed true stress vs strain"
        " at 25/90/130/160 °C (band = range over the three axes) at 10⁸ and 10⁹ s⁻¹. "
        "(c) Peak stress (max of the smoothed σ) and flow stress (mean σ over strain 0.3–0.5)"
        " vs T, mean ± sd over the axes; both scale with the rate (viscous flow stress ≈"
        " 3η × rate), so they are rate-dependent and not a yield stress. "
        f"(d) Apparent modulus from the slope up to strain 0.02: not resolvable at this box"
        f" size — the noise ({noise}; i.e. ±70–450 MPa) dwarfs the ≈8 MPa expected for an"
        " amorphous PE rubber (E ≈ 3G_e, G_e = 2.6 MPa at 140 °C; Fetters, Lohse, Colby 2007),"
        " and several axes give negative slopes. The boxes are amorphous melts above Tg at MD"
        " rates ~10⁹× faster than experiment: these numbers show T and rate trends only"
        " (validity: trend) and are **not comparable to semicrystalline separator data**"
        " (Celgard E ≈ 0.25 GPa, tensile strength ≈ 165 MPa MD; Gor et al. 2014), whose"
        " stiffness and strength come from crystallinity."
    )


def write_readme(out: Path, infos: dict) -> Path:
    lines = [
        "# Presentation figures",
        "",
        (
            "Regenerate: `uv run --frozen python scripts/presentation_figures.py` (reads only"
            " results/analysis/**/results.json, systems/*/manifest.yaml and data.lmp, the run"
            " progress.json copies and local results/runs snapshots where present). Each figure"
            " is written as PNG (300 dpi), PDF and SVG. Experimental values and their sources:"
            " [docs/experiment_comparison.md](../../docs/experiment_comparison.md); per-system"
            ' validity: [summary](../summary.md) ("Physical validity by system").'
        ),
        "",
        (
            "Style: colour = resolution (CG blue, UA vermillion, AA green), marker = polymer (PE"
            " circle, iPP square), open/dashed = C1500 or a replicated (320-chain) box, black ="
            " experiment; temperatures 25 → 160 °C run dark violet → orange. CG dynamics are"
            " ≈4.07× faster than real PE, so every CG time is labelled model time. UA/AA and iPP"
            " series are added automatically once their results.json exist."
        ),
        "",
    ]
    caps = {
        "fig1_convergence": caption_fig1,
        "fig2_properties_vs_T": caption_fig2,
        "fig3_structures": caption_fig3,
        "fig4_mechanics": caption_fig4,
    }
    for name, fn in caps.items():
        if name not in infos:
            continue
        lines += [f"## {name}", "", f"![{name}]({name}.png)", "", fn(infos[name]), ""]
        lines += [
            f"Files: [{name}.png]({name}.png), [{name}.pdf]({name}.pdf), [{name}.svg]({name}.svg)",
            "",
        ]
    p = out / "README.md"
    p.write_text("\n".join(lines).rstrip() + "\n")
    return p


# ================================================================== main
FIGURES = {
    "fig1": ("fig1_convergence", fig1_convergence),
    "fig2": ("fig2_properties_vs_T", fig2_properties),
    "fig3": ("fig3_structures", fig3_structures),
    "fig4": ("fig4_mechanics", fig4_mechanics),
}


def load_data(analysis: Path, systems: Path, run_roots: list[Path]) -> dict:
    ana = ss.load_analysis(analysis)
    sysm = ss.load_systems(systems)
    roots = [r for r in run_roots if r.is_dir()]
    return {
        "analysis": ana,
        "systems": sysm,
        "runs": ss.load_runs(roots),
        "run_roots": roots,
        "systems_root": systems,
        "ids": set(ana) | set(sysm),
    }


def build(data: dict, out: Path, only: list[str] | None = None, log=print) -> dict:
    infos, written = {}, []
    for key, (name, fn) in FIGURES.items():
        if only and key not in only and name not in only:
            continue
        paths, info = fn(data, out)
        infos[name] = info
        written += paths
        log(f"wrote {paths[0]} (+ {', '.join(p.suffix for p in paths[1:])})")
    readme = write_readme(out, infos) if not only else None
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
    a = ap.parse_args(argv)
    runs = a.runs or ["results/runs", "results/run_sidecars", "results/progress/rdyu-rog"]
    data = load_data(ss._path(a.analysis), ss._path(a.systems), [ss._path(r) for r in runs])
    build(data, ss._path(a.out), a.only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
