"""PNG plots for `sepsim analyze sweep` (D49), drawn with matplotlib's Agg backend.

Each function takes parts of the analysis report (plain dicts/lists) and writes one PNG.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

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
