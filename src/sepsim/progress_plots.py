"""PNG plots for `sepsim progress` (D45), drawn with matplotlib's Agg backend.

Each function takes plain arrays/dicts (from the progress report) and writes one PNG.
:func:`sepsim.progress.make_plots` decides which plots a run gets and skips the ones
whose inputs have not changed.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DPI = 110


def _save(fig, path: Path) -> Path:
    fig.tight_layout()
    tmp = path.with_name(path.stem + ".tmp.png")
    fig.savefig(tmp, dpi=DPI)
    plt.close(fig)
    tmp.replace(path)
    return path


def timeline(path, time_ns, density, pot_eng, boundaries, title="") -> Path:
    """Density and potential energy vs time, stage boundaries as vertical lines.

    ``boundaries``: list of (time_ns, label) where a segment starts.
    """
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5.5), sharex=True)
    a1.plot(time_ns, density, lw=0.6)
    a1.set_ylabel("density (g/cm³)")
    a2.plot(time_ns, pot_eng, lw=0.6, color="C1")
    a2.set_ylabel("PotEng (kcal/mol)")
    a2.set_xlabel("time (ns)")
    for t, label in boundaries:
        for ax in (a1, a2):
            ax.axvline(t, color="0.6", lw=0.5, ls="--")
        a1.annotate(
            label,
            (t, 1.0),
            xycoords=("data", "axes fraction"),
            rotation=90,
            fontsize=6,
            va="top",
            ha="right",
            color="0.35",
        )
    a1.set_title(title, fontsize=9)
    return _save(fig, Path(path))


def cn_curve(path, n_carbons, c_n, reference, tolerance=0.10, n_min=100, title="") -> Path:
    """C_n vs carbon-equivalent separation with the melt reference band (±tolerance)."""
    fig, ax = plt.subplots(figsize=(6, 4))
    lo, hi = reference
    ax.axhspan(
        (1 - tolerance) * lo,
        (1 + tolerance) * hi,
        color="C2",
        alpha=0.2,
        label=f"melt C∞ {lo:g} ±{tolerance:.0%}",
    )
    ax.plot(n_carbons, c_n, color="C0", label="hold average")
    ax.axvline(n_min, color="0.5", ls=":", lw=0.8, label=f"plateau n ≥ {n_min}")
    ax.set_xlabel("n (carbon equivalents)")
    ax.set_ylabel("C_n")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=8)
    return _save(fig, Path(path))


def cn_plateau_time(
    path, t_ns, plateau, reference, tolerance=0.10, title="", boundaries=()
) -> Path:
    """C_n plateau (n ≥ n_min) per frame across the hold; ``boundaries`` (ns) are drawn
    as dashed lines (e.g. where a hold extension starts, D47)."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    lo, hi = reference
    ax.axhspan(
        (1 - tolerance) * lo,
        (1 + tolerance) * hi,
        color="C2",
        alpha=0.2,
        label=f"melt C∞ {lo:g} ±{tolerance:.0%}",
    )
    ax.plot(t_ns, plateau, ".-", ms=2, lw=0.6)
    for k, t in enumerate(boundaries):
        ax.axvline(t, color="0.4", ls="--", lw=0.8, label="extension starts" if k == 0 else None)
    ax.set_xlabel("hold time (ns)")
    ax.set_ylabel("C_n plateau")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=8)
    return _save(fig, Path(path))


def ree_acf(path, lag_ns, acf, title="") -> Path:
    """End-to-end vector autocorrelation vs lag, with the 1/e line."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(lag_ns, acf)
    ax.axhline(np.exp(-1.0), color="C3", ls="--", lw=0.8, label="1/e")
    ax.axhline(0.0, color="0.6", lw=0.5)
    ax.set_xlabel("lag (ns)")
    ax.set_ylabel("<R(t)·R(0)>/<R²>")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=8)
    return _save(fig, Path(path))


def com_msd(path, lag_ns, msd_a2, rg2_a2, title="") -> Path:
    """Chain centre-of-mass MSD vs lag, with <Rg^2> as a horizontal line."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(lag_ns, msd_a2, label="COM MSD")
    ax.axhline(rg2_a2, color="C3", ls="--", lw=0.8, label="<Rg²>")
    ax.set_xlabel("lag (ns)")
    ax.set_ylabel("Å²")
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=8)
    return _save(fig, Path(path))


def _points(ax, pts, key, label_prefix, color):
    """Error-bar points {t_k, kind, mean, sem}: steps as circles, holds as squares."""
    for kind, marker in (("step", "o"), ("hold", "s"), ("cool", "v")):
        sel = [p for p in pts if p["kind"] == kind]
        if not sel:
            continue
        ax.errorbar(
            [p["t_c"] for p in sel],
            [p[key]["mean"] for p in sel],
            yerr=[p[key]["sem"] for p in sel],
            fmt=marker,
            ms=4,
            capsize=2,
            color=color,
            mfc="none" if kind == "step" else color,
            label=f"{label_prefix} {kind}",
        )


def vs_temperature(path, sweep, cool=(), quantities=("density",), title="") -> Path:
    """Sweep (and prep step-cool) points vs T in C, one panel per quantity.

    ``sweep`` / ``cool``: lists of {"t_c", "kind" (step/hold/cool), <quantity>: {mean, sem}}.
    """
    labels = {"density": "density (g/cm³)", "enthalpy": "H (kcal/mol)"}
    fig, axes = plt.subplots(
        len(quantities), 1, figsize=(6.5, 3.4 * len(quantities)), squeeze=False
    )
    for ax, q in zip(axes[:, 0], quantities, strict=True):
        s = [p for p in sweep if p.get(q)]
        c = [p for p in cool if p.get(q)]
        if c:
            _points(ax, c, q, "prep", "C1")
            ax.plot([p["t_c"] for p in c], [p[q]["mean"] for p in c], color="C1", lw=0.6)
        if s:
            _points(ax, s, q, "sweep", "C0")
            ax.plot([p["t_c"] for p in s], [p[q]["mean"] for p in s], color="C0", lw=0.6)
        ax.set_ylabel(labels.get(q, q))
        ax.set_xlabel("T (°C)")
        ax.legend(fontsize=7)
    axes[0, 0].set_title(title, fontsize=9)
    return _save(fig, Path(path))
