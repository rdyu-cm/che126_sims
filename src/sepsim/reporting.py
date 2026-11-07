"""Report plumbing shared by `sepsim analyze` (sweep, pore, hold, tensile, hole) and
`sepsim progress`: number formatting, the JSON encoder and atomic writes, the run and
analysis header (report dict and markdown lines), the "Plots" section, records of
trajectories that are not analysed, and the CG time caveat.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import platform
from pathlib import Path

import numpy as np

CG_TIME_NOTE = (
    "CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et"
    " al. 2019; docs/experiment_comparison.md), so MSD, D_COM, P2 and relaxation times are"
    " model times (not rescaled); multiply chain-motion times by 4.07 before comparing with"
    " experiment."
)


# --------------------------------------------------------------------------- formatting


def _f(x, fmt: str = ".2f") -> str:
    """``x`` formatted with ``fmt``, "n/a" for None."""
    return "n/a" if x is None else f"{x:{fmt}}"


def _pm(ms: dict | None, fmt: str) -> str:
    """ "mean ± SEM" of a {mean, sem} dict; the mean alone if its SEM is None, "" if no dict."""
    if not ms:
        return ""
    if ms.get("sem") is None:
        return f"{ms['mean']:{fmt}}"
    return f"{ms['mean']:{fmt}} ± {ms['sem']:{fmt}}"


def plots_markdown(plots: dict | None) -> list[str]:
    """The "## Plots" section: each plot's title and image ({name: {file, title}})."""
    if not plots:
        return []
    lines = ["", "## Plots", ""]
    for p in plots.values():
        lines += [f"**{p['title']}**", "", f"![{p['title']}]({p['file']})", ""]
    return lines


# --------------------------------------------------------------------------- files


def _json(x):
    """JSON encoder fallback for numpy scalars and arrays."""
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    raise TypeError(f"not JSON serializable: {type(x).__name__}")


def dump_json(report, default=_json) -> str:
    """The report as sorted, indented JSON text (as every report file is written)."""
    return json.dumps(report, indent=1, sort_keys=True, default=default) + "\n"


def write_atomic(out_dir: Path, files) -> None:
    """Write (name, text) pairs into ``out_dir``, each via a temporary file and os.replace."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in files:
        tmp = out_dir / (name + ".tmp")
        tmp.write_text(text)
        os.replace(tmp, out_dir / name)


# --------------------------------------------------------------------------- header


def report_header(
    version: int, run_dir: Path, manifest: dict | None, system: str, resolution
) -> dict:
    """Leading keys of an analysis report: version, generation time and host, the system,
    the source run directory (stage, status, node and git of the run from its manifest)
    and the analysis code's git state."""
    from sepsim.run import CODE_DIR, git_info

    run_dir = Path(run_dir)
    now = dt.datetime.now().astimezone()
    return {
        "version": version,
        "generated": now.isoformat(timespec="seconds"),
        "generated_on": platform.node(),
        "system": system,
        "resolution": resolution,
        "stage": run_dir.resolve().name,
        "run_dir": str(run_dir.resolve()),
        "run_status": (manifest or {}).get("status"),
        "run_node": (manifest or {}).get("hostname"),
        "run_git": (manifest or {}).get("git"),
        "code_git": git_info(CODE_DIR),
    }


def header_markdown(r: dict, title: str, command: str, decision: str, run_info: str = ""):
    """Title and the system / analysis lines of a results.md from :func:`report_header`
    keys; ``run_info`` is inserted before the run status (e.g. the protocol)."""
    cg, rg = r.get("code_git") or {}, r.get("run_git") or {}
    return [
        f"# {title}: {r['system']} / {r['stage']}",
        "",
        (
            f"- system: `{r['system']}` ({r.get('resolution')}); source run directory"
            f" `{r['run_dir']}` ({run_info}status {r.get('run_status')}, node"
            f" {r.get('run_node')}, run code commit {(rg.get('commit') or 'n/a')[:10]})"
        ),
        f"- analysis: `sepsim analyze {command}` ({decision}), code commit"
        f" {(cg.get('commit') or 'n/a')[:10]}"
        + (" (dirty)" if cg.get("dirty") else "")
        + f", {r['generated'][:16].replace('T', ' ')} on {r['generated_on']}",
    ]


# --------------------------------------------------------------------------- trajectories


def unavailable(note: str) -> dict:
    """A trajectory result that is not available, with the reason."""
    return {"available": False, "notes": [note]}


def load_system_arrays(system_dir: Path, notes: list[str]) -> dict | None:
    """:func:`sepsim.analysis.chain.system_arrays` of a system, or None with a note."""
    from sepsim.analysis.chain import system_arrays

    try:
        return system_arrays(system_dir)
    except (OSError, ValueError, KeyError) as exc:
        notes.append(f"system {system_dir} not usable: {exc}")
        return None


def trajectory_or_note(traj: bool, sys_arr, done: bool, what: str, compute) -> dict:
    """``compute()`` (a segment's trajectory results) unless trajectories are skipped
    (--no-traj), the system is not usable or the ``what`` (hold, step) is not complete;
    a failing ``compute`` (OSError, ValueError) becomes a note."""
    if not traj:
        return unavailable("trajectory analysis skipped (--no-traj)")
    if sys_arr is None:
        return unavailable("trajectory not available (no system)")
    if not done:
        return unavailable(f"{what} not complete")
    try:
        return compute()
    except (OSError, ValueError) as exc:
        return unavailable(f"trajectory failed: {exc}")
