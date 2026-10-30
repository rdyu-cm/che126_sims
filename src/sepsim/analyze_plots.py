"""PNG plots for `sepsim analyze sweep` (D49) and `sepsim analyze pore` (D51), drawn with
matplotlib's Agg backend.

Each function takes parts of the analysis report (plain dicts/lists) and writes one PNG.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib.ticker import NullFormatter

from sepsim.analysis.units import A3_CM3, AVOGADRO
from sepsim.progress_plots import _save, plt

_WINDOW_STYLE = {0: "-", 1: "--", 2: ":"}


def _err(ms):
    return ms["sem"] if ms.get("sem") is not None else 0.0


def _hold_colors(holds):
    return {h["t_c"]: f"C{k}" for k, h in enumerate(holds)}


def thermo_vs_t(path, segments, fits, mass_gmol, title="") -> Path:
    """Density and enthalpy vs T (steps open, holds filled) with the linear fits
    (density from the V(T) lines: rho = M / (N_A V))."""
    fig, axes = plt.subplots(2, 1, figsize=(6.5, 6.8), sharex=True)
    for ax, key, label in (
        (axes[0], "density", "density (g/cm³)"),
        (axes[1], "enthalpy", "H (kcal/mol)"),
    ):
        for kind, marker in (("step", "o"), ("hold", "s")):
            sel = [s for s in segments if s["kind"] == kind and s["stats"].get(key)]
            if sel:
                ax.errorbar(
                    [s["t_set_c"] for s in sel],
                    [s["stats"][key]["mean"] for s in sel],
                    yerr=[_err(s["stats"][key]) for s in sel],
                    fmt=marker,
                    ms=4,
                    capsize=2,
                    color="C0",
                    mfc="none" if kind == "step" else "C0",
                    label=kind,
                )
        ax.set_ylabel(label)
    for k, (a, c) in enumerate(zip((fits or {}).get("alpha_V", []), (fits or {}).get("cp", []))):
        lo, hi = a["window_c"]
        t = np.linspace(lo, hi, 50)
        tk = t + 273.15
        v = a["line"][0] * tk + a["line"][1]
        ls = _WINDOW_STYLE.get(k, "-")
        axes[0].plot(
            t,
            mass_gmol / (AVOGADRO * v * A3_CM3),
            color="C1",
            ls=ls,
            lw=0.9,
            label=f"fit {lo:g}–{hi:g} °C",
        )
        axes[1].plot(
            t,
            c["line"][0] * tk + c["line"][1],
            color="C1",
            ls=ls,
            lw=0.9,
            label=f"fit {lo:g}–{hi:g} °C",
        )
    for ax in axes:
        ax.legend(fontsize=7)
    axes[1].set_xlabel("T (°C)")
    axes[0].set_title(title, fontsize=9)
    return _save(fig, Path(path))


def kappa_vs_t(path, holds, title="") -> Path:
    """kappa_T (1/GPa) vs T at the holds, with SEM error bars."""
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.errorbar(
        [h["t_c"] for h in holds],
        [h["kappa"]["kappa_T_GPa"] for h in holds],
        yerr=[h["kappa"]["sem"] for h in holds],
        fmt="s-",
        ms=5,
        capsize=3,
    )
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("κ_T (GPa⁻¹)")
    ax.set_title(title, fontsize=9)
    return _save(fig, Path(path))


def fit_windows(path, fits, title="") -> Path:
    """alpha_V and Cp of each fit window as horizontal bars over the window (± 1 sigma)."""
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6, 5.4), sharex=True)
    for ax, rows, key, scale, label in (
        (a1, fits["alpha_V"], "alpha_V_per_K", 1e4, "α_V (10⁻⁴ K⁻¹)"),
        (a2, fits["cp"], "cp_J_gK", 1.0, "Cp classical (J g⁻¹ K⁻¹)"),
    ):
        for k, r in enumerate(rows):
            lo, hi = r["window_c"]
            y, e = r[key] * scale, r["err"] * scale
            ax.plot([lo, hi], [y, y], color=f"C{k}", lw=2, label=f"{lo:g}–{hi:g} °C")
            ax.fill_between([lo, hi], y - e, y + e, color=f"C{k}", alpha=0.2)
        ax.set_ylabel(label)
        ax.legend(fontsize=7)
    a2.set_xlabel("T (°C)")
    a1.set_title(title, fontsize=9)
    return _save(fig, Path(path))


def msd_curves(path, holds, title="") -> Path:
    """Backbone-site and chain COM MSD vs lag (log-log), one line per hold; the D_COM
    fit as a dashed 6 D t line where the COM MSD is diffusive."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    col = _hold_colors(holds)
    for h in holds:
        t, c = h["traj"]["curves"], col[h["t_c"]]
        a1.loglog(t["msd_lag_ps"], t["msd_A2"], color=c, label=f"{h['t_c']:g} °C")
        a2.loglog(t["com_lag_ps"], t["com_A2"], color=c, label=f"{h['t_c']:g} °C")
        cm = h["traj"]["com_msd"]
        if cm.get("diffusive"):
            lo, hi = cm["fit_ps"]
            x = np.geomspace(lo, hi, 20)
            d = cm["D_cm2_s"] / 1e-4  # back to A^2/ps
            a2.loglog(x, 6 * d * x, color=c, ls="--", lw=0.8)
    for ax, what in ((a1, "backbone-site MSD"), (a2, "chain COM MSD")):
        ax.set_xlabel("lag (ps)")
        ax.set_ylabel(f"{what} (Å²)")
        ax.legend(fontsize=7)
    fig.suptitle(title, fontsize=9)
    return _save(fig, Path(path))


def p2_curves(path, holds, title="") -> Path:
    """Bond-vector P2 autocorrelation vs lag (log x), one line per hold, 1/e marked."""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    col = _hold_colors(holds)
    for h in holds:
        t = h["traj"]["curves"]
        ax.semilogx(t["p2_lag_ps"], t["p2"], color=col[h["t_c"]], label=f"{h['t_c']:g} °C")
    ax.axhline(np.exp(-1.0), color="0.4", ls="--", lw=0.8, label="1/e")
    ax.axhline(0.0, color="0.6", lw=0.5)
    ax.set_xlabel("lag (ps)")
    ax.set_ylabel("⟨P2(u(0)·u(t))⟩")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=7)
    return _save(fig, Path(path))


def chain_vs_t(path, holds, title="") -> Path:
    """<Rg^2>^1/2, <R_ee^2>^1/2 and the C_n plateau vs T at the holds."""
    fig, axes = plt.subplots(3, 1, figsize=(6, 7), sharex=True)
    t = [h["t_c"] for h in holds]
    for ax, get, label in (
        (axes[0], lambda h: h["traj"]["rg"]["rg_A"], "Rg (Å)"),
        (axes[1], lambda h: h["traj"]["ree"]["ree_A"], "R_ee (Å)"),
        (axes[2], lambda h: h["traj"]["c_n"]["plateau"], "C_n plateau (n ≥ 100)"),
    ):
        vals = [get(h) for h in holds]
        ok = [k for k, v in enumerate(vals) if v]
        ax.errorbar(
            [t[k] for k in ok],
            [vals[k]["mean"] for k in ok],
            yerr=[_err(vals[k]) for k in ok],
            fmt="s-",
            ms=5,
            capsize=3,
        )
        ax.set_ylabel(label)
    axes[2].set_xlabel("T (°C)")
    axes[0].set_title(title, fontsize=9)
    return _save(fig, Path(path))


# --------------------------------------------------------------------------- pore (D51)

_LAYER_STYLE = {"surface": "-", "interior": "--"}


def gamma_vs_t(path, segments, fits, title="") -> Path:
    """gamma vs T: sweep steps open, holds filled, step-cool stages grey, with the fits."""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for kinds, marker, color, label in (
        (("cool",), "^", "0.55", "step-cool"),
        (("relax",), "v", "0.55", "500 K re-relaxation"),
        (("step",), "o", "C0", "sweep step"),
        (("hold",), "s", "C0", "sweep hold"),
    ):
        sel = [s for s in segments if s["kind"] in kinds]
        if sel:
            ax.errorbar(
                [s["t_set_c"] for s in sel],
                [s["stats"]["gamma"]["mean"] for s in sel],
                yerr=[_err(s["stats"]["gamma"]) for s in sel],
                fmt=marker,
                ms=4,
                capsize=2,
                color=color,
                mfc="none" if kinds == ("step",) else color,
                label=label,
            )
    for key, color in (("sweep", "C1"), ("cool", "0.4")):
        f = (fits or {}).get(key)
        if f:
            t = np.linspace(*f["window_c"], 50)
            ax.plot(
                t,
                f["line"][0] * (t + 273.15) + f["line"][1],
                color=color,
                lw=0.9,
                ls="-" if key == "sweep" else ":",
                label=f"fit {key}: {f['dgamma_dT_mN_mK']:.3f} ± {f['err']:.3f} mN/(m K)",
            )
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("γ (mN/m)")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=7)
    return _save(fig, Path(path))


def density_profiles(path, holds, title="") -> Path:
    """Symmetrized rho(z) at each hold, with the bulk density (dashed) and the Gibbs
    surfaces (dotted)."""
    fig, ax = plt.subplots(figsize=(7, 4))
    col = _hold_colors(holds)
    for h in holds:
        p, c = h["traj"]["profile"], col[h["t_c"]]
        ax.plot(p["z_A"], p["rho_sym"], color=c, lw=1, label=f"{h['t_c']:g} °C")
        bd = (h.get("bulk") or {}).get("density")
        if bd:
            ax.axhline(bd["mean"], color=c, ls="--", lw=0.7)
        for sgn in (-1, 1):
            ax.axvline(sgn * 0.5 * p["film_gibbs_A"], color=c, ls=":", lw=0.7)
    ax.set_xlabel("z − z_film (Å)")
    ax.set_ylabel("ρ (g/cm³)")
    ax.set_title(title + " (dashed: bulk; dotted: Gibbs surfaces)", fontsize=9)
    ax.legend(fontsize=7)
    return _save(fig, Path(path))


def gap_vs_t(path, holds, nominal_nm=None, title="") -> Path:
    """Gap width (Gibbs, 50%) and the clear gap (z gap, closest approach) vs T."""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    t = [h["t_c"] for h in holds]
    pr = [h["traj"]["profile"] for h in holds]
    ax.plot(t, [p["gap_gibbs_A"] / 10 for p in pr], "s-", label="Lz − t_Gibbs")
    ax.plot(t, [p["gap_50_A"] / 10 for p in pr], "o-", label="Lz − t_50%")
    ax.plot(t, [p["gap_z_A"]["mean"] / 10 for p in pr], "^-", label="z gap (mean)")
    ax.plot(t, [p["gap_z_A"]["min"] / 10 for p in pr], "^:", mfc="none", label="z gap (min)")
    ax.plot(t, [p["closest_A"]["mean"] / 10 for p in pr], "d-", label="closest (mean)")
    ax.plot(t, [p["closest_A"]["min"] / 10 for p in pr], "d:", mfc="none", label="closest (min)")
    if nominal_nm:
        ax.plot([25.0], [nominal_nm], "k*", ms=9, label=f"nominal {nominal_nm:g} nm at 25 °C")
    ax.set_xlabel("T (°C)")
    ax.set_ylabel("gap (nm)")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=7)
    return _save(fig, Path(path))


def msd_layers(path, holds, title="") -> Path:
    """Per-dimension MSD in-plane and normal, surface (solid) vs interior (dashed), with
    the bulk MSD/3 (dotted), one colour per hold."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    col = _hold_colors(holds)
    for h in holds:
        ly, c = h["traj"]["layers"], col[h["t_c"]]
        for name, ls in _LAYER_STYLE.items():
            cu = ly[name]["curves"]
            lab = f"{h['t_c']:g} °C {name}"
            a1.loglog(cu["lag_ps"], cu["xy_A2"], color=c, ls=ls, lw=1, label=lab)
            a2.loglog(cu["lag_ps"], cu["z_A2"], color=c, ls=ls, lw=1, label=lab)
        b = h.get("bulk") or {}
        if b.get("msd_lag_ps"):
            for ax in (a1, a2):
                ax.loglog(b["msd_lag_ps"], b["msd_per_dim_A2"], color=c, ls=":", lw=0.9)
    a1.set_ylabel("MSD per dimension (Å²)")
    for ax, what in ((a1, "in-plane (⟨Δx²⟩+⟨Δy²⟩)/2"), (a2, "normal ⟨Δz²⟩")):
        ax.set_xlabel("lag (ps)")
        ax.set_title(what + " (dotted: bulk MSD/3)", fontsize=8)
    a1.legend(fontsize=6)
    fig.suptitle(title, fontsize=9)
    return _save(fig, Path(path))


def p2_layers(path, holds, title="") -> Path:
    """Bond P2 autocorrelation, surface (solid) vs interior (dashed), one colour per hold."""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    col = _hold_colors(holds)
    for h in holds:
        ly = h["traj"]["layers"]
        for name, ls in _LAYER_STYLE.items():
            cu = ly[name]["curves"]
            ax.semilogx(
                cu["p2_lag_ps"],
                cu["p2"],
                color=col[h["t_c"]],
                ls=ls,
                label=f"{h['t_c']:g} °C {name}",
            )
    ax.axhline(np.exp(-1.0), color="0.4", ls=":", lw=0.8, label="1/e")
    ax.axhline(0.0, color="0.6", lw=0.5)
    ax.set_xlabel("lag (ps)")
    ax.set_ylabel("⟨P2(u(0)·u(t))⟩")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=6)
    return _save(fig, Path(path))


def p2z_profiles(path, holds, title="") -> Path:
    """<P2(cos theta_z)> of backbone bonds vs |z| from the film centre, Gibbs surface and
    layer boundary marked, one colour per hold."""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    col = _hold_colors(holds)
    for h in holds:
        c, p = h["traj"]["conformation"], h["traj"]["profile"]
        ax.plot(c["p2z_z_A"], c["p2z"], color=col[h["t_c"]], label=f"{h['t_c']:g} °C")
        ax.axvline(0.5 * p["film_gibbs_A"], color=col[h["t_c"]], ls=":", lw=0.7)
    ax.axhline(0.0, color="0.6", lw=0.5)
    ax.set_xlabel("|z − z_film| (Å)")
    ax.set_ylabel("⟨P2(cos θ_z)⟩")
    ax.set_title(title + " (dotted: Gibbs surface)", fontsize=9)
    ax.legend(fontsize=7)
    return _save(fig, Path(path))


def thermal_vs_t(path, thermal, title="") -> Path:
    """Film thickness (Gibbs) with the 25-160 C fit, interior plateau density with the
    bulk density, and the surface excess energy with gamma and gamma - T dgamma/dT, vs T
    (steps open, holds filled)."""
    pts = thermal["points"]
    fig, axes = plt.subplots(3, 1, figsize=(6.5, 8.5), sharex=True)

    def series(ax, key, color, label, fill=True):
        for kind, marker in (("step", "o"), ("hold", "s")):
            sel = [p for p in pts if p["kind"] == kind and p.get(key)]
            if sel:
                ax.errorbar(
                    [p["t_c"] for p in sel],
                    [p[key]["mean"] for p in sel],
                    yerr=[_err(p[key]) for p in sel],
                    fmt=marker,
                    ms=4,
                    capsize=2,
                    color=color,
                    mfc=color if kind == "hold" and fill else "none",
                    label=f"{label} ({kind})",
                )

    series(axes[0], "film_gibbs_A", "C0", "t_G")
    for k, a in enumerate(thermal.get("alpha", [])):
        if a.get("line"):
            lo, hi = a["window_c"]
            t = np.linspace(lo, hi, 50)
            axes[0].plot(
                t,
                a["line"][0] * (t + 273.15) + a["line"][1],
                color="C1",
                ls=_WINDOW_STYLE.get(k, "-"),
                lw=0.9,
                label=f"fit {lo:g}–{hi:g} °C: α_z {a['alpha_z_per_K'] * 1e4:.2f}e-4/K",
            )
    axes[0].set_ylabel("film thickness t_G (Å)")
    series(axes[1], "plateau", "C0", "film interior")
    series(axes[1], "bulk_density", "C3", "bulk")
    axes[1].set_ylabel("density (g/cm³)")
    series(axes[2], "e_s_mJ_m2", "C2", "e_s")
    series(axes[2], "gamma", "C0", "γ")
    g = [p for p in pts if p.get("gamma_minus_TdgdT") is not None]
    if g:
        axes[2].plot(
            [p["t_c"] for p in g],
            [p["gamma_minus_TdgdT"] for p in g],
            color="C1",
            lw=0.9,
            label="γ − T dγ/dT (fit)",
        )
    axes[2].set_ylabel("mN/m = mJ/m²")
    axes[2].set_xlabel("T (°C)")
    for ax in axes:
        ax.legend(fontsize=6)
    axes[0].set_title(title, fontsize=9)
    return _save(fig, Path(path))


# --------------------------------------------------------------------------- equilibration


def _smooth(x, width: int) -> np.ndarray:
    """Centred moving average (NaN at the ends)."""
    x = np.asarray(x, dtype=float)
    if width < 2 or len(x) < width:
        return x
    c = np.cumsum(np.r_[0.0, x])
    m = (c[width:] - c[:-width]) / width
    pad = width // 2
    return np.r_[np.full(pad, np.nan), m, np.full(len(x) - len(m) - pad, np.nan)]


def plot_timeseries(ax, conv, quantity, color="C0", t0=0.0, unit_ps=1000.0) -> bool:
    """One segment's convergence record (``results.json`` ``convergence`` entry) of one
    quantity on ``ax``: the series (thin), a moving average, block means +- SEM (black)
    and the analysis window shaded; time (t - t0) / unit_ps (default ns). False if the
    quantity is missing."""
    q = conv["quantities"].get(quantity)
    if q is None:
        return False
    t = (np.asarray(q["t_ps"]) - t0) / unit_ps
    ax.plot(t, q["value"], color=color, lw=0.3, alpha=0.35)
    ax.plot(t, _smooth(q["value"], max(1, len(t) // 25)), color=color, lw=0.9)
    b = q["blocks"]
    if b:
        ax.errorbar(
            [(x["t"] - t0) / unit_ps for x in b],
            [x["mean"] for x in b],
            yerr=[x["sem"] or 0.0 for x in b],
            fmt="o",
            ms=2.5,
            color="k",
            capsize=1.5,
            lw=0.7,
        )
    w0, w1 = ((w - t0) / unit_ps for w in conv["window"])
    ax.axvspan(w0, w1, color="C2", alpha=0.08, lw=0)
    return True


def plot_block_sem(ax, conv, quantity, color="C0", label=None) -> bool:
    """SEM of the window mean vs block length (``sem_vs_block`` of a hold's convergence
    entry), with the statistical-inefficiency SEM as a dashed line. False if missing."""
    curve = (conv.get("sem_vs_block") or {}).get(quantity)
    q = conv["quantities"].get(quantity)
    if not curve or q is None:
        return False
    ax.semilogx(
        [c["block_ps"] / 1000.0 for c in curve],
        [c["sem"] for c in curve],
        "o-",
        ms=3,
        color=color,
        label=label,
    )
    if q.get("sem"):
        ax.axhline(q["sem"], color=color, ls="--", lw=0.8)
    ax.xaxis.set_minor_formatter(NullFormatter())
    return True


_KIND_COLOR = {"relax": "C3", "cool": "C4", "step": "C0", "hold": "C1"}


def equilibration(path, segments, panels, title="") -> Path:
    """Thermo vs time over all segments (LAMMPS Time on one axis), one panel per quantity
    (:func:`plot_timeseries`), segment boundaries dotted."""
    panels = [(k, lab) for k, lab in panels if any(k in e["quantities"] for e in segments)]
    fig, axes = plt.subplots(len(panels), 1, figsize=(11, 1.9 * len(panels) + 0.6), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, (key, label) in zip(axes, panels, strict=True):
        for e in segments:
            plot_timeseries(ax, e, key, _KIND_COLOR.get(e["kind"], "C0"))
            ax.axvline(e["t_start_ps"] / 1000.0, color="0.7", ls=":", lw=0.5)
        ax.set_ylabel(label, fontsize=8)
    axes[-1].set_xlabel("time (ns)")
    axes[0].set_title(
        title + " (re-relax red / cool purple / step blue / hold orange; shaded: windows)",
        fontsize=9,
    )
    return _save(fig, Path(path))


def equilibration_holds(path, holds, panels, title="") -> Path:
    """Per hold (columns): each quantity vs time from the hold start
    (:func:`plot_timeseries`) and, in the last row, SEM vs block length
    (:func:`plot_block_sem`) of every quantity relative to its statistical-inefficiency
    SEM."""
    panels = [(k, lab) for k, lab in panels if any(k in e["quantities"] for e in holds)]
    fig, axes = plt.subplots(
        len(panels) + 1,
        len(holds),
        figsize=(3.2 * len(holds) + 0.8, 1.8 * (len(panels) + 1) + 0.6),
        squeeze=False,
    )
    for j, e in enumerate(holds):
        for i, (key, label) in enumerate(panels):
            ax = axes[i, j]
            plot_timeseries(ax, e, key, "C1", t0=e["t_start_ps"])
            if j == 0:
                ax.set_ylabel(label, fontsize=8)
            ax.tick_params(labelsize=7)
        axes[0, j].set_title(e["name"], fontsize=8)
        axes[-2, j].set_xlabel("time in hold (ns)", fontsize=8)
        ax = axes[-1, j]
        for k, (key, label) in enumerate(panels):
            q = e["quantities"].get(key)
            curve = (e.get("sem_vs_block") or {}).get(key)
            if q and q.get("sem") and curve:
                ax.semilogx(
                    [c["block_ps"] / 1000.0 for c in curve],
                    [c["sem"] / q["sem"] for c in curve],
                    "o-",
                    ms=2.5,
                    color=f"C{k}",
                    label=key,
                )
        ax.axhline(1.0, color="0.4", ls="--", lw=0.8)
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xlabel("block length (ns)", fontsize=8)
        ax.tick_params(labelsize=7)
        if j == 0:
            ax.set_ylabel("block SEM / SEM(g)", fontsize=8)
            ax.legend(fontsize=5)
    fig.suptitle(title, fontsize=9)
    return _save(fig, Path(path))


def film_vs_time(path, segments, title="") -> Path:
    """Pore film quantities per DCD frame vs time in the segment (holds; steps if given):
    Gibbs thickness, Gibbs gap, interior density and the closest approach across the
    slit, analysis window shaded."""
    rows = (
        ("film_gibbs_A", "t_G (Å)"),
        ("gap_gibbs_A", "gap Lz − t_G (Å)"),
        ("plateau", "interior ρ (g/cm³)"),
        ("closest_A", "closest approach (Å)"),
    )
    fig, axes = plt.subplots(len(rows), 1, figsize=(7.5, 8), sharex=True)
    for k, s in enumerate(segments):
        se, c = s["series"], f"C{k % 10}"
        for ax, (key, label) in zip(axes, rows, strict=True):
            ax.plot(se["t_ns"], se[key], color=c, lw=0.8, label=s["name"])
            ax.set_ylabel(label, fontsize=8)
        for ax in axes:
            ax.axvspan(se["window_ns"], se["t_ns"][-1], color=c, alpha=0.05, lw=0)
    axes[0].legend(fontsize=6, ncol=2)
    axes[-1].set_xlabel("time in segment (ns)")
    axes[0].set_title(title + " (shaded: analysis windows)", fontsize=9)
    return _save(fig, Path(path))


def relaxation_curves(path, items, title="") -> Path:
    """D56: end-to-end vector ACF (thick) and Rouse mode ACFs p = 1..5 (thin, lighter with
    p) vs lag (log x), one colour per hold, 1/e marked; inset p²τ_p vs p (1/e times
    reached; flat for Rouse scaling). ``items``: (T in C, traj dict) per hold."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    col = _hold_colors([{"t_c": t} for t, _ in items])
    ins = ax.inset_axes([0.07, 0.08, 0.3, 0.35])
    for t, tr in items:
        c = tr["curves"]
        lag = np.asarray(c["relax_lag_ps"]) / 1000.0
        ax.semilogx(lag, c["ree_acf"], color=col[t], lw=2.0, label=f"{t:g} °C R_ee")
        for k, acf in enumerate(c["rouse_acf"]):
            ax.semilogx(lag, acf, color=col[t], lw=0.8, alpha=max(0.25, 0.9 - 0.15 * k))
        modes = [m for m in tr["relaxation"]["rouse"] if m["reached"]]
        if modes:
            ins.plot(
                [m["p"] for m in modes],
                [m["p"] ** 2 * m["t_1e_ps"] / 1000.0 for m in modes],
                "o-",
                color=col[t],
                ms=3,
            )
    ax.axhline(np.exp(-1.0), color="0.4", ls="--", lw=0.8, label="1/e")
    ax.axhline(0.0, color="0.6", lw=0.5)
    ax.set_xlabel("lag (ns)")
    ax.set_ylabel("normalized ACF")
    ax.set_title(title + "\nthick: R_ee; thin: Rouse X_p, p = 1…5 (lighter = higher p)", fontsize=9)
    ax.legend(fontsize=7, loc="upper right")
    ins.set_xlabel("p", fontsize=7)
    ins.set_ylabel("p²τ_p (ns)", fontsize=7)
    ins.tick_params(labelsize=6)
    ins.set_ylim(bottom=0)
    ins.set_xticks(range(1, 6))
    ins.set_xlim(0.5, 5.5)
    return _save(fig, Path(path))
