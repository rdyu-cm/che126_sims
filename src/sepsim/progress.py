"""Live progress of LAMMPS runs: `sepsim progress` (D45).

For a run directory ``results/runs/<system>/<stage>/`` (deck ``in.<protocol>``,
``log.lammps``, ``run_manifest.json``) this writes ``progress.md`` and
``progress.json``: status, planned vs completed segments, % of MD steps done,
ns/day and ETA, per-segment thermo means (second half of each segment, SEM from
the statistical inefficiency), the prep-hold chain checks (D37 C_n, end-to-end
vector decorrelation, chain COM MSD / <Rg^2>), the cooling-vs-heating density
hysteresis (prep step-cool vs sweep) and sweep step-vs-hold agreement.

Segments are the deck's ``run``/``minimize`` commands in order; LAMMPS writes one
thermo block per command, so the k-th block of the log belongs to the k-th
segment. Names come from the deck's comment headers (``# ---- Stage 6: ...``,
``# cool step 3/8: ...``, ``# ---- Segment 4: step at 55 C ...``).

Expensive results (the DCD analyses) are cached in ``progress.json``; a finished
hold's chain check is never recomputed. A run whose manifest is finished or failed,
or that has been silent for long, is not re-parsed while its files are unchanged.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import re
import warnings
from dataclasses import asdict, dataclass, field
from itertools import pairwise
from pathlib import Path

import numpy as np

from sepsim.analysis.lammps_log import LogRun, read_log
from sepsim.analysis.stats import timeseries_mean
from sepsim.run import MANIFEST_NAME, _deck_commands

REPORT_VERSION = 1
CHAIN_VERSION = 1  # bump to recompute cached hold chain checks
MD_NAME, JSON_NAME = "progress.md", "progress.json"
LOG_NAME = "log.lammps"
STALL_S = 30 * 60  # no log update for this long while not finished -> "stalled?"
KILLED_S = 6 * 3600  # ... and for this long -> "cancelled/killed?"
RATE_WINDOW_S = 3600  # ns/day of the running segment from its last hour of thermo rows
MAX_MSID_FRAMES = 200  # frames (evenly spaced) used for the D37 C_n check
N_SIGMA = 2.0  # step vs hold disagreement threshold, in combined SEMs
FINAL = {"finished", "failed", "interrupted", "dry-run", "cancelled/killed?"}

_HEADER = re.compile(r"^#\s*----\s*(.+?)\s*$")
_COOL = re.compile(r"^#\s*cool step (\d+)/(\d+):\s*([-\d.eE+]+)\s*K")
_VDOS = re.compile(r"^#\s*VDOS\b")
_SWEEP_SEG = re.compile(r"^Segment (\d+): (\w+) at ([-\d.eE+]+) C")
_SYSTEM = re.compile(r"^#\s*system\s+(\S+)\s+\((\w+)\)")


# --------------------------------------------------------------------------- deck


@dataclass
class Segment:
    """One ``run``/``minimize`` command of a deck."""

    index: int  # 1-based position among the deck's run/minimize commands
    name: str
    command: str  # "run" or "minimize"
    steps: int  # planned MD steps (0 for minimize)
    dt_fs: float
    ensemble: str | None  # npt, nvt, nve, langevin (from the active fixes)
    t_target_k: float | None
    dcd: list[str] = field(default_factory=list)  # active dcd dumps
    dump_every: list[int] = field(default_factory=list)  # their intervals (steps)
    cool_step: int | None = None  # prep step-cool stage k (1-based)
    sweep_index: int | None = None  # sweep "Segment N"
    sweep_kind: str | None = None  # "step" / "hold"
    t_c: float | None = None  # sweep segment temperature, C
    vdos: bool = False


def _short(header: str) -> str:
    """Header text up to the first "(" or " ->" (e.g. "Stage 6: NPT hold 20000 ps at 500 K")."""
    cut = len(header)
    for mark in ("(", " ->"):
        k = header.find(mark)
        if k > 0:
            cut = min(cut, k)
    return header[:cut].strip()


def parse_deck(path: str | Path) -> list[Segment]:
    """Planned segments of a rendered deck (no loops or variables in run lengths)."""
    segments: list[Segment] = []
    major, sub, cool = "", None, None
    dt_fs = 1.0  # LAMMPS default for units real
    fixes: dict[str, list[str]] = {}
    dumps: dict[str, tuple[str, int]] = {}
    lines = Path(path).read_text(errors="replace").splitlines()
    pending = []
    for raw in lines:
        s = raw.strip()
        if s.startswith("#"):
            if m := _HEADER.match(s):
                major, sub, cool = m.group(1), None, None
            elif m := _COOL.match(s):
                cool = int(m.group(1))
                sub = f"cool {m.group(1)}/{m.group(2)} ({float(m.group(3)):.1f} K)"
            elif _VDOS.match(s):
                sub = "VDOS NVE"
            continue
        pending.append(raw)
        if raw.split("#", 1)[0].rstrip().endswith("&"):
            continue
        commands, pending = _deck_commands("\n".join(pending)), []
        for tokens in commands:
            cmd = tokens[0]
            if cmd == "timestep":
                dt_fs = float(tokens[1])
            elif cmd == "fix" and len(tokens) >= 4:
                fixes[tokens[1]] = tokens[3:]
            elif cmd == "unfix":
                fixes.pop(tokens[1], None)
            elif cmd == "dump" and len(tokens) >= 6 and tokens[3] == "dcd":
                dumps[tokens[1]] = (tokens[5], int(tokens[4]))
            elif cmd == "undump":
                dumps.pop(tokens[1], None)
            elif cmd in ("run", "minimize"):
                segments.append(
                    _segment(len(segments) + 1, cmd, tokens, dt_fs, fixes, dumps, major, sub, cool)
                )
    # "(run j/n)" for headers with several runs (e.g. the two compression pressures)
    names = [s.name for s in segments]
    for k, s in enumerate(segments):
        n = names.count(s.name)
        if n > 1:
            s.name = f"{s.name} (run {names[: k + 1].count(s.name)}/{n})"
    return segments


def _segment(index, cmd, tokens, dt_fs, fixes, dumps, major, sub, cool) -> Segment:
    styles = [args[0] for args in fixes.values()]
    ensemble = next((e for e in ("npt", "nvt", "nve/limit", "nve") if e in styles), None)
    if ensemble == "nve/limit" or (ensemble is None and "langevin" in styles):
        ensemble = "langevin" if "langevin" in styles else "nve"
    t_target = None
    for args in fixes.values():
        if args[0] in ("npt", "nvt") and "temp" in args:
            t_target = float(args[args.index("temp") + 2])
        elif args[0] == "langevin" and len(args) >= 3:
            t_target = float(args[2])
    seg = Segment(
        index=index,
        name="",
        command=cmd,
        steps=int(float(tokens[1])) if cmd == "run" else 0,
        dt_fs=dt_fs,
        ensemble=None if cmd == "minimize" else ensemble,
        t_target_k=None if cmd == "minimize" or ensemble == "nve" else t_target,
        dcd=[f for f, _ in dumps.values()],
        dump_every=[n for _, n in dumps.values()],
        cool_step=cool,
        vdos=sub == "VDOS NVE",
    )
    if m := _SWEEP_SEG.match(major):
        seg.sweep_index, seg.sweep_kind, seg.t_c = int(m.group(1)), m.group(2), float(m.group(3))
        seg.name = f"seg {seg.sweep_index:02d} {seg.sweep_kind} {m.group(3)} C"
    elif sub and ":" in major:
        seg.name = f"{major.split(':', 1)[0]} {sub}"
    else:
        seg.name = _short(major) or f"run {index}"
    if seg.vdos and seg.sweep_index is not None:
        seg.name += " VDOS NVE"
    return seg


def deck_system(path: str | Path) -> tuple[str | None, str | None]:
    """(system id, resolution) from the deck header line ``# system <id> (<res>), ...``."""
    for line in Path(path).read_text(errors="replace").splitlines()[:10]:
        if m := _SYSTEM.match(line.strip()):
            return m.group(1), m.group(2)
    return None, None


# --------------------------------------------------------------------------- thermo stats


def _mean_sem(x) -> dict | None:
    x = np.asarray(x, dtype=float)
    if len(x) < 3:
        return None
    if np.ptp(x) == 0.0:  # NVT/NVE density: constant, no statistical inefficiency
        return {"mean": float(x[0]), "sem": 0.0}
    r = timeseries_mean(x)
    return {"mean": r.mean, "sem": r.sem}


def segment_stats(thermo: dict[str, np.ndarray]) -> dict:
    """Second-half means of a segment's thermo block, and a density drift flag.

    T (C), density (g/cm^3) and enthalpy (kcal/mol) as mean +- SEM
    (:func:`sepsim.analysis.stats.timeseries_mean`) over the second half of the
    rows. ``drift``: :func:`sepsim.analysis.chain.drift_check` on that same
    window's density (its two quarters differ by > 2 combined SEM), i.e. the
    averaging window itself is not stationary; None for constant density (NVT,
    NVE) or < 12 rows.
    """
    from sepsim.analysis.chain import drift_check

    n = len(thermo.get("Step", ()))
    out: dict = {"rows": n}
    if n < 6:
        return out
    half = slice(n // 2, None)
    for key, col, shift in (
        ("t_c", "Temp", -273.15),
        ("density", "Density", 0.0),
        ("enthalpy", "Enthalpy", 0.0),
    ):
        if col in thermo:
            ms = _mean_sem(thermo[col][half])
            if ms is not None:
                ms["mean"] += shift
            out[key] = ms
    rho = thermo.get("Density")
    if rho is not None and n - n // 2 >= 12 and np.ptp(rho[half]) > 0:
        try:
            a, b, delta, sem, drift = drift_check(rho[half])
            out["drift"] = {"first": a, "second": b, "delta": delta, "sem": sem, "drift": drift}
        except ValueError:  # a zero-variance quarter
            pass
    return out


# --------------------------------------------------------------------------- hold chain checks


def hold_chain_checks(
    dcd: Path, system_dir: Path, frame_ps: float, max_msid_frames: int = MAX_MSID_FRAMES
) -> dict:
    """D37 C_n check plus end-to-end decorrelation and COM MSD / <Rg^2> over a hold DCD.

    The DCD (LAMMPS ``dump dcd``, id-sorted, ``unwrap yes``) is streamed once; the
    C_n check uses up to ``max_msid_frames`` evenly spaced frames. Backbones from
    :func:`sepsim.analysis.chain.backbone_chains` on the system's data.lmp and
    manifest.yaml; molecules and masses from data.lmp.
    """
    import yaml
    from MDAnalysis.coordinates.DCD import DCDReader

    from sepsim.analysis.chain import (
        CARBONS_PER_SITE,
        MELT_C_INF_500K,
        backbone_chains,
        chain_com_rg2,
        com_msd_over_rg2,
        decorrelation_time,
        end_to_end_autocorrelation,
        msid_check,
    )
    from sepsim.analysis.mobility import msd
    from sepsim.build.datafile import read_data_file

    man = yaml.safe_load((system_dir / "manifest.yaml").read_text())
    chains = backbone_chains(system_dir / "data.lmp", man)
    atoms = read_data_file(system_dir / "data.lmp")
    sorted_atoms = atoms.sorted_atoms()
    mass_of = {int(r[0]): float(r[1]) for r in atoms.sections["Masses"]}
    masses = np.array([mass_of[int(t)] for t in sorted_atoms[:, 2]])
    _, molecule = np.unique(sorted_atoms[:, 1].astype(np.int64), return_inverse=True)
    first = np.array([c[0] for c in chains])
    last = np.array([c[-1] for c in chains])
    bb_rows = np.concatenate(chains)
    bb_chains, k = [], 0
    for c in chains:
        bb_chains.append(np.arange(k, k + len(c)))
        k += len(c)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        reader = DCDReader(str(dcd))
    try:
        n, n_atoms = reader.n_frames, reader.n_atoms
        if n_atoms != len(sorted_atoms):
            raise ValueError(f"{dcd.name}: {n_atoms} atoms, data.lmp has {len(sorted_atoms)}")
        if n < 6:
            raise ValueError(f"{dcd.name}: only {n} frames")
        keep = set(np.unique(np.linspace(0, n - 1, min(n, max_msid_frames)).round().astype(int)))
        ree = np.empty((n, len(chains), 3))
        com = np.empty((n, int(molecule.max()) + 1, 3))
        rg2 = np.empty((n, com.shape[1]))
        bb = []
        for f, ts in enumerate(reader):
            x = ts.positions.astype(float)
            ree[f] = x[last] - x[first]
            c, g = chain_com_rg2(x, molecule, masses)
            com[f], rg2[f] = c[0], g[0]
            if f in keep:
                bb.append(x[bb_rows])
    finally:
        reader.close()

    res = man["resolution"]
    cg = res == "cg"
    m = msid_check(
        np.stack(bb),
        bb_chains,
        reference=MELT_C_INF_500K[man["polymer"]],
        carbons_per_site=CARBONS_PER_SITE[res],
        bond_length=1.54 if cg else None,
    )
    dt_ns = frame_ps / 1000.0
    lags, acf = end_to_end_autocorrelation(ree, dt_ns)
    t_1e = decorrelation_time(lags, acf)
    lag_ns, msd_a2, rg2_mean, ratio = com_msd_over_rg2(com, rg2, dt_ns)
    msd_lags, msd_curve = msd(com - com.mean(axis=1, keepdims=True), dt_ns)
    return {
        "frames": n,
        "frame_ps": frame_ps,
        "hold_ns": (n - 1) * dt_ns,
        "msid": {
            "frames_used": len(bb),
            "plateau": m.plateau,
            "reference": list(m.reference),
            "within_reference": m.within_reference,
            "first_half": m.first_half,
            "second_half": m.second_half,
            "delta": m.delta,
            "delta_sem": m.delta_sem,
            "drift": m.drift,
            "passed": m.passed,
            "carbons_per_site": CARBONS_PER_SITE[res],
            "bond_length": 1.54 if cg else None,
        },
        "ree_acf": {
            "lag_ns": float(lags[-1]),
            "acf_at_lag": float(acf[-1]),
            "t_1e_ns": t_1e,
            "r2_mean_A2": float(np.mean(np.sum(ree**2, axis=2))),
        },
        "com_msd": {"lag_ns": lag_ns, "msd_A2": msd_a2, "rg2_A2": rg2_mean, "ratio": ratio},
        "curves": {  # for the plots (ACF and MSD thinned to <= MAX_CURVE points)
            "n_carbons": m.n_carbons.tolist(),
            "c_n": _round(m.c_n),
            "plateau_t_ns": (np.array(sorted(keep)) * dt_ns).tolist(),
            "plateau_t": _round(m.plateau_frames),
            "acf_lag_ns": _round(_thin(lags)),
            "acf": _round(_thin(acf)),
            "msd_lag_ns": _round(_thin(msd_lags)),
            "msd_A2": _round(_thin(msd_curve)),
        },
    }


MAX_CURVE = 400


def _thin(x) -> np.ndarray:
    x = np.asarray(x)
    return x[np.unique(np.linspace(0, len(x) - 1, min(len(x), MAX_CURVE)).round().astype(int))]


def _round(x, digits: int = 6) -> list[float]:
    return [float(f"{v:.{digits}g}") for v in np.asarray(x, dtype=float)]


# --------------------------------------------------------------------------- comparisons


def hysteresis(prep_segments: list[dict], sweep_segments: list[dict]) -> list[dict]:
    """Density of each prep step-cool stage vs the sweep density interpolated at its T.

    Sweep points: completed NPT segments (latest per target T, so a hold wins over
    the preceding step). ``delta_pct`` = (rho_cool - rho_sweep) / rho_sweep * 100;
    None outside the sweep's completed temperature range.
    """
    pts: dict[float, float] = {}
    for s in sweep_segments:
        rho = (s.get("stats") or {}).get("density")
        if s["state"] == "done" and s["ensemble"] == "npt" and rho and s["t_target_k"]:
            pts[round(s["t_target_k"], 3)] = rho["mean"]
    temps = sorted(pts)
    out = []
    for s in prep_segments:
        rho = (s.get("stats") or {}).get("density")
        if s.get("cool_step") is None or s["state"] != "done" or not rho:
            continue
        t = s["t_target_k"]
        row = {
            "cool_step": s["cool_step"],
            "t_k": t,
            "rho_cool": rho["mean"],
            "rho_cool_sem": rho["sem"],
            "rho_sweep": None,
            "delta_pct": None,
        }
        if temps and temps[0] - 1e-6 <= t <= temps[-1] + 1e-6:
            r = float(np.interp(t, temps, [pts[k] for k in temps]))
            row.update(rho_sweep=r, delta_pct=(rho["mean"] - r) / r * 100.0)
        out.append(row)
    return out


def step_vs_hold(sweep_segments: list[dict], n_sigma: float = N_SIGMA) -> list[dict]:
    """Each sweep step followed by a hold at the same T: density and enthalpy differences.

    ``flag`` if either |hold - step| exceeds ``n_sigma`` combined SEMs.
    """
    md = [s for s in sweep_segments if s.get("sweep_kind") and not s.get("vdos")]
    out = []
    for a, b in pairwise(md):
        if not (a["sweep_kind"] == "step" and b["sweep_kind"] == "hold" and a["t_c"] == b["t_c"]):
            continue
        if a["state"] != "done" or b["state"] != "done":
            continue
        row: dict = {"t_c": a["t_c"], "step": a["index"], "hold": b["index"], "flag": False}
        for key in ("density", "enthalpy"):
            x, y = (a.get("stats") or {}).get(key), (b.get("stats") or {}).get(key)
            if not x or not y:
                continue
            delta, sem = y["mean"] - x["mean"], float(np.hypot(x["sem"], y["sem"]))
            row[key] = {"step": x["mean"], "hold": y["mean"], "delta": delta, "sem": sem}
            row["flag"] |= bool(abs(delta) > n_sigma * sem)
        out.append(row)
    return out


# --------------------------------------------------------------------------- report


def _stat(path: Path) -> list[int] | None:
    try:
        st = path.stat()
    except OSError:
        return None
    return [st.st_size, st.st_mtime_ns]


def _iso(t: float | None) -> str | None:
    if t is None:
        return None
    return dt.datetime.fromtimestamp(t).astimezone().isoformat(timespec="seconds")


def find_deck(run_dir: Path, manifest: dict | None = None) -> Path | None:
    """The deck of a run directory: the manifest's deck, else the only ``in.*`` file."""
    if manifest and (p := (manifest.get("deck") or {}).get("path")):
        cand = run_dir / Path(p).name
        if cand.is_file():
            return cand
    decks = sorted(p for p in run_dir.glob("in.*") if p.is_file())
    return decks[0] if len(decks) == 1 else None


def find_runs(root: str | Path, include_benchmarks: bool = False) -> list[Path]:
    """Run directories ``root/<system>/<stage>/`` that hold a deck (benchmarks skipped)."""
    runs = []
    for d in sorted(Path(root).glob("*/*/")):
        decks = list(d.glob("in.*"))
        if not decks:
            continue
        if not include_benchmarks and all(p.name == "in.benchmark" for p in decks):
            continue
        runs.append(d)
    return runs


def out_dir_for(run_dir: Path, out: str | Path | None) -> Path:
    """Where a run's progress files go: the run directory, or OUT/<system>/<stage>/."""
    run_dir = Path(run_dir)
    if out is None:
        return run_dir
    return Path(out) / run_dir.resolve().parent.name / run_dir.resolve().name


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _rate(run: LogRun) -> float | None:
    """Steps/s of a thermo block from its Step and CPU (elapsed s) columns, last hour."""
    th = run.thermo
    step, cpu = th.get("Step"), th.get("CPU")
    if step is None or cpu is None or len(step) < 2:
        return None
    sel = np.flatnonzero(cpu >= cpu[-1] - RATE_WINDOW_S)
    k = sel[0] if len(sel) and sel[0] < len(cpu) - 1 else 0
    d_cpu = cpu[-1] - cpu[k]
    return float((step[-1] - step[k]) / d_cpu) if d_cpu > 0 else None


def _status(manifest: dict | None, log_age: float | None, has_log: bool, stall_s: float) -> str:
    ms = (manifest or {}).get("status")
    if ms in ("finished", "failed", "interrupted", "dry-run"):
        return ms
    if not has_log:
        return "not started" if manifest is None else "starting"
    if log_age is not None and log_age > max(stall_s, KILLED_S):
        return "cancelled/killed?"
    if log_age is not None and log_age > stall_s:
        return "stalled?"
    return "running"


def _segments_with_log(segments: list[Segment], log) -> tuple[list[dict], dict]:
    """Segment dicts with state (done/running/pending), steps done and stats."""
    rows, info = [], {"current": None, "extra_runs": 0, "rate": None, "last_perf": None}
    runs = log.runs if log else []
    info["extra_runs"] = max(0, len(runs) - len(segments))
    for k, seg in enumerate(segments):
        d = asdict(seg)
        run = runs[k] if k < len(runs) else None
        if run is None:
            d.update(state="pending", steps_done=0, stats=None)
        elif run.complete:
            stats = segment_stats(run.thermo) if seg.command == "run" else None
            d.update(state="done", steps_done=seg.steps, stats=stats)
            if run.ns_per_day is not None:
                info["last_perf"] = (run.ns_per_day, run.steps_per_s, k)
        else:
            step = run.thermo.get("Step")
            done = int(step[-1] - step[0]) if step is not None and len(step) else 0
            d.update(state="running", steps_done=min(done, seg.steps), stats=None)
            info["current"] = k
            info["rate"] = _rate(run)
        rows.append(d)
    if info["current"] is None:
        nxt = next((k for k, d in enumerate(rows) if d["state"] == "pending"), None)
        info["current"] = nxt
    return rows, info


def segments_for(run_dir: Path) -> list[dict] | None:
    """Segment dicts (with stats) of a run directory, parsed from its deck and log."""
    deck = find_deck(run_dir, load_json(run_dir / MANIFEST_NAME))
    if deck is None:
        return None
    log = read_log(run_dir / LOG_NAME) if (run_dir / LOG_NAME).is_file() else None
    return _segments_with_log(parse_deck(deck), log)[0]


def _sibling_segments(run_dir: Path, name: str, out: str | Path | None) -> list[dict] | None:
    """Segments of the sibling stage ``name``, from its progress.json if it is current."""
    sib = run_dir.resolve().parent / name
    if not (sib / LOG_NAME).is_file():
        return None
    cached = load_json(out_dir_for(sib, out) / JSON_NAME)
    if cached and cached.get("signature", {}).get(LOG_NAME) == _stat(sib / LOG_NAME):
        return cached.get("segments")
    return segments_for(sib)


def progress_report(
    run_dir: str | Path,
    out: str | Path | None = None,
    systems: str | Path = "systems",
    now: float | None = None,
    stall_s: float = STALL_S,
    plots: bool = True,
) -> dict:
    """Build the progress report dict of one run directory (see the module docstring)."""
    run_dir = Path(run_dir)
    now = dt.datetime.now().timestamp() if now is None else now
    out_dir = out_dir_for(run_dir, out)
    previous = load_json(out_dir / JSON_NAME) or {}
    cache = previous.get("cache", {}) if previous.get("version") == REPORT_VERSION else {}
    manifest = load_json(run_dir / MANIFEST_NAME)
    deck = find_deck(run_dir, manifest)
    log_path = run_dir / LOG_NAME
    log_st = _stat(log_path)
    log_mtime = log_st[1] / 1e9 if log_st else None
    log_age = now - log_mtime if log_mtime else None
    protocol = deck.name.split(".", 1)[1] if deck else None
    signature = {
        LOG_NAME: log_st,
        MANIFEST_NAME: _stat(run_dir / MANIFEST_NAME),
        "deck": _stat(deck) if deck else None,
    }
    sibling = {"sweep": "prep", "prep": "sweep"}.get(protocol)
    if sibling:
        signature[f"../{sibling}/{LOG_NAME}"] = _stat(run_dir.resolve().parent / sibling / LOG_NAME)

    status = _status(manifest, log_age, log_st is not None, stall_s)
    if (
        previous.get("version") == REPORT_VERSION
        and previous.get("signature") == signature
        and status in FINAL
        and previous.get("status") == status
        and all((out_dir / p["file"]).is_file() for p in previous.get("plots", {}).values())
    ):
        previous.update(generated=_iso(now), log_age_s=log_age)
        return previous

    system, resolution = deck_system(deck) if deck else (None, None)
    report: dict = {
        "version": REPORT_VERSION,
        "generated": _iso(now),
        "generated_on": platform.node(),
        "run_dir": str(run_dir.resolve()),
        "system": system or run_dir.resolve().parent.name,
        "resolution": resolution,
        "stage": run_dir.resolve().name,
        "protocol": protocol,
        "node": (manifest or {}).get("hostname") or platform.node(),
        "manifest_status": (manifest or {}).get("status"),
        "start_time": (manifest or {}).get("start_time"),
        "end_time": (manifest or {}).get("end_time"),
        "status": status,
        "log_mtime": _iso(log_mtime),
        "log_age_s": log_age,
        "signature": signature,
        "errors": [],
        "notes": [],
    }
    if deck is None:
        report["notes"].append("no deck (in.*) found")
        report.update(segments=[], flags=[], cache=cache)
        return report
    log = read_log(log_path) if log_st else None
    if log:
        report["errors"] = log.errors[-3:]
    segments = parse_deck(deck)
    rows, info = _segments_with_log(segments, log)
    if info["extra_runs"]:
        report["notes"].append(f"log has {info['extra_runs']} more runs than the deck")
    total = sum(s.steps for s in segments)
    done = sum(r["steps_done"] for r in rows)
    finished = status == "finished"
    cur = info["current"]
    report.update(
        segments=rows,
        n_segments=len(rows),
        n_done=sum(r["state"] == "done" for r in rows),
        steps_total=total,
        steps_done=total if finished else done,
        percent=100.0 if finished else (100.0 * done / total if total else None),
        current=None if finished or cur is None else {"index": cur + 1, "name": rows[cur]["name"]},
    )
    # speed: the running segment's thermo (last hour), else the last Performance line
    rate, src = info["rate"], "running segment (last hour of thermo)"
    seg_dt = rows[cur]["dt_fs"] if cur is not None else None
    if (rate is None or finished) and info["last_perf"]:
        _nsd, sps, k = info["last_perf"]
        rate, seg_dt, src = sps, rows[k]["dt_fs"], f"Performance line of segment {k + 1}"
    if rate and seg_dt:
        report["ns_per_day"] = rate * seg_dt * 86400e-6
        report["steps_per_s"] = rate
        report["speed_source"] = src
    if status == "running" and rate and log_mtime:
        remaining = total - done
        report["eta"] = _iso(log_mtime + remaining / rate)
        report["remaining_h"] = remaining / rate / 3600.0

    # prep hold chain checks, once the hold is complete
    hold = next((r for r in rows if "hold.dcd" in r["dcd"]), None) if protocol == "prep" else None
    if hold is not None:
        report["hold"] = _hold_checks(run_dir, hold, system, systems, manifest, cache, report)
    # cooling vs heating, sweep step vs hold
    prep_rows = sweep_rows = None
    if protocol == "sweep":
        prep_rows, sweep_rows = _sibling_segments(run_dir, "prep", out), rows
        report["step_vs_hold"] = step_vs_hold(rows)
    elif protocol == "prep":
        prep_rows, sweep_rows = rows, _sibling_segments(run_dir, "sweep", out)
    if prep_rows and sweep_rows:
        hyst = hysteresis(prep_rows, sweep_rows)
        if any(h["rho_sweep"] is not None for h in hyst):
            report["hysteresis"] = hyst
    report["cache"] = cache
    report["flags"] = _flags(report)
    if plots:
        report["plots"] = make_plots(
            report, log, prep_rows, sweep_rows, out_dir, previous.get("plots", {})
        )
    return report


def _key(data) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def _t_points(rows: list[dict] | None, cool: bool) -> list[dict]:
    """Completed NPT segments as plot points {t_c, kind, density, enthalpy}."""
    pts = []
    for s in rows or []:
        st = s.get("stats") or {}
        if s["state"] != "done" or s["ensemble"] != "npt" or not st.get("density"):
            continue
        if cool and s.get("cool_step") is not None:
            pts.append({"t_c": s["t_target_k"] - 273.15, "kind": "cool"})
        elif not cool and s.get("sweep_kind") and not s.get("vdos"):
            pts.append({"t_c": s["t_c"], "kind": s["sweep_kind"]})
        else:
            continue
        pts[-1].update(density=st["density"], enthalpy=st.get("enthalpy"))
    return pts


def _timeline_data(log, rows: list[dict], max_points: int = 6000):
    """Concatenated Time (ns), Density, PotEng of the MD runs, and segment start marks."""
    t, rho, pe, marks = [], [], [], []
    for k, run in enumerate(log.runs if log else []):
        th = run.thermo
        if k < len(rows) and rows[k]["command"] == "minimize":
            continue
        if not all(c in th for c in ("Time", "Density", "PotEng")) or not len(th["Time"]):
            continue
        t.append(th["Time"] / 1e6)
        rho.append(th["Density"])
        pe.append(th["PotEng"])
        if k < len(rows):
            marks.append((float(th["Time"][0] / 1e6), f"{rows[k]['index']}"))
    if not t:
        return None
    t, rho, pe = np.concatenate(t), np.concatenate(rho), np.concatenate(pe)
    stride = max(1, len(t) // max_points)
    return t[::stride], rho[::stride], pe[::stride], marks


def make_plots(report, log, prep_rows, sweep_rows, out_dir: Path, previous: dict) -> dict:
    """Draw the run's PNGs into ``out_dir``, skipping plots whose inputs are unchanged.

    Returns {name: {"file", "key", "title"}}; ``key`` hashes the plot's inputs (the
    log's size and mtime for the timeline).
    """
    from sepsim import progress_plots as pp

    title = f"{report['system']} / {report['stage']}"
    jobs = []  # (name, title, key, draw(path))
    if report["protocol"] == "prep" and _timeline_data(log, report["segments"], 1) is not None:
        jobs.append(
            (
                "timeline",
                "density and PotEng vs time (segment starts marked)",
                ["timeline", report["signature"][LOG_NAME]],
                lambda p: _draw_timeline(pp, p, log, report["segments"], title),
            )
        )
    hold = report.get("hold") or {}
    if "curves" in hold:
        c, ref = hold["curves"], hold["msid"]["reference"]
        hk = ["hold", _key(c), ref]
        jobs += [
            (
                "hold_cn",
                "500 K hold: C_n vs n",
                hk,
                lambda p: pp.cn_curve(p, c["n_carbons"], c["c_n"], ref, title=title),
            ),
            (
                "hold_cn_time",
                "500 K hold: C_n plateau vs time",
                hk,
                lambda p: pp.cn_plateau_time(
                    p, c["plateau_t_ns"], c["plateau_t"], ref, title=title
                ),
            ),
            (
                "hold_ree_acf",
                "500 K hold: end-to-end vector ACF",
                hk,
                lambda p: pp.ree_acf(p, c["acf_lag_ns"], c["acf"], title=title),
            ),
            (
                "hold_com_msd",
                "500 K hold: chain COM MSD vs <Rg²>",
                hk,
                lambda p: pp.com_msd(
                    p, c["msd_lag_ns"], c["msd_A2"], hold["com_msd"]["rg2_A2"], title=title
                ),
            ),
        ]
    cool, sweep = _t_points(prep_rows, cool=True), _t_points(sweep_rows, cool=False)
    if report["protocol"] == "prep" and cool:
        jobs.append(
            (
                "cool_vs_sweep",
                "step-cool density vs T (sweep overlaid once it exists)",
                ["cool", cool, sweep],
                lambda p: pp.vs_temperature(p, sweep, cool, ("density",), title=title),
            )
        )
    if report["protocol"] == "sweep" and sweep:
        jobs.append(
            (
                "sweep_vs_T",
                "sweep density and enthalpy vs T (prep step-cool overlaid)",
                ["sweep", sweep, cool],
                lambda p: pp.vs_temperature(p, sweep, cool, ("density", "enthalpy"), title=title),
            )
        )
    out = {}
    for name, desc, key_data, draw in jobs:
        key, file = _key(key_data), f"progress_{name}.png"
        old = previous.get(name, {})
        if not (old.get("key") == key and (out_dir / file).is_file()):
            out_dir.mkdir(parents=True, exist_ok=True)
            try:
                draw(out_dir / file)
            except (ValueError, OSError) as exc:
                report["notes"].append(f"plot {name} failed: {exc}")
                continue
        out[name] = {"file": file, "key": key, "title": desc}
    return out


def _draw_timeline(pp, path, log, rows, title):
    data = _timeline_data(log, rows)
    if data is None:
        raise ValueError("no Time/Density/PotEng thermo columns")
    t, rho, pe, marks = data
    return pp.timeline(path, t, rho, pe, marks, title=title)


def _hold_checks(run_dir, hold, system, systems, manifest, cache, report) -> dict:
    out = {"segment": hold["index"], "state": hold["state"]}
    if hold["state"] != "done":
        return out
    dcd = run_dir / "hold.dcd"
    entry = cache.get("hold_chain")
    start = (manifest or {}).get("start_time")
    if (
        entry
        and entry.get("version") == CHAIN_VERSION
        and entry.get("complete")
        and entry.get("start_time") == start
    ):
        out.update(entry["result"], cached=True)
        return out
    if not dcd.is_file():
        out["error"] = "hold.dcd not found"
        return out
    every = hold["dump_every"][hold["dcd"].index("hold.dcd")]
    frame_ps = every * hold["dt_fs"] / 1000.0
    try:
        result = hold_chain_checks(dcd, Path(systems) / system, frame_ps)
    except (OSError, ValueError, KeyError) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
    cache["hold_chain"] = {
        "version": CHAIN_VERSION,
        "complete": True,
        "start_time": start,
        "key": _stat(dcd),
        "result": result,
    }
    out.update(result, cached=False)
    return out


def _flags(report: dict) -> list[str]:
    flags = []
    hold = report.get("hold") or {}
    if "msid" in hold:
        m = hold["msid"]
        ok = "PASS" if m["passed"] else "FAIL"
        why = [] if m["within_reference"] else [f"vs {m['reference'][0]:g}"]
        if m["drift"]:
            why.append("drift")
        flags.append(f"D37 {ok} C_n {m['plateau']:.2f}" + (f" ({', '.join(why)})" if why else ""))
        a = hold["ree_acf"]
        t = a["t_1e_ns"]
        flags.append(
            f"R_ee 1/e {t:.2f} ns"
            if t is not None
            else f"R_ee not decorrelated ({a['acf_at_lag']:.2f} at {a['lag_ns']:.1f} ns)"
        )
        flags.append(f"MSD/Rg2 {hold['com_msd']['ratio']:.2f}")
    elif "error" in hold:
        flags.append(f"hold check: {hold['error'][:60]}")
    drift = [
        str(s["index"])
        for s in report.get("segments", [])
        if ((s.get("stats") or {}).get("drift") or {}).get("drift")
    ]
    if drift:
        flags.append("drift seg " + ",".join(drift))
    bad = [f"{r['t_c']:g} C" for r in report.get("step_vs_hold", []) if r["flag"]]
    if bad:
        flags.append("step!=hold " + ",".join(bad))
    hyst = [abs(r["delta_pct"]) for r in report.get("hysteresis", []) if r["delta_pct"] is not None]
    if hyst:
        flags.append(f"hyst max {max(hyst):.2f}%")
    if report.get("errors"):
        flags.append("ERROR in log")
    return flags


# --------------------------------------------------------------------------- markdown


def _pm(ms: dict | None, fmt: str) -> str:
    if not ms:
        return ""
    return f"{ms['mean']:{fmt}} ± {ms['sem']:{fmt}}"


def _age(s: float | None) -> str:
    if s is None:
        return "n/a"
    if s < 3600:
        return f"{s / 60:.0f} min"
    if s < 2 * 86400:
        return f"{s / 3600:.1f} h"
    return f"{s / 86400:.1f} d"


def _when(iso: str | None) -> str:
    """ISO timestamp (any offset) as local time of the machine rendering, with its zone."""
    if not iso:
        return ""
    t = dt.datetime.fromisoformat(iso)
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.UTC)
    return t.astimezone().strftime("%Y-%m-%d %H:%M %Z")


def render_markdown(r: dict) -> str:
    """progress.md for one report."""
    lines = [f"# {r['system']} / {r['stage']}", ""]
    lines.append(
        f"- status: **{r['status']}** (manifest: {r.get('manifest_status')}), "
        f"node {r['node']}, started {_when(r.get('start_time'))}"
        + (f", ended {_when(r['end_time'])}" if r.get("end_time") else "")
    )
    if r.get("percent") is not None:
        cur = r.get("current")
        lines.append(
            f"- progress: {r['percent']:.1f}% of {r['steps_total']:,} MD steps; "
            f"{r['n_done']}/{r['n_segments']} segments done"
            + (f"; current: {cur['index']} {cur['name']}" if cur else "")
        )
    if r.get("ns_per_day"):
        lines.append(
            f"- speed: {r['ns_per_day']:.2f} ns/day ({r['steps_per_s']:.1f} steps/s,"
            f" {r['speed_source']})"
        )
    if r.get("eta"):
        lines.append(f"- ETA: {_when(r['eta'])} ({r['remaining_h']:.1f} h left)")
    lines.append(
        f"- log updated {_when(r.get('log_mtime'))} ({_age(r.get('log_age_s'))} ago);"
        f" report {_when(r['generated'])} on {r['generated_on']}"
    )
    if r.get("flags"):
        lines.append("- checks: " + "; ".join(r["flags"]))
    for e in r.get("errors", []):
        lines.append(f"- log: `{e}`")
    for n in r.get("notes", []):
        lines.append(f"- note: {n}")
    segs = r.get("segments", [])
    if segs:
        lines += [
            "",
            "## Segments",
            "",
            (
                "Means ± SEM over the second half of each completed segment; drift = density"
                " halves of that window differ by > 2 SEM."
            ),
            "",
            (
                "| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) |"
                " H (kcal/mol) | drift |"
            ),
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for s in segs:
            st = s.get("stats") or {}
            tset = f"{s['t_target_k'] - 273.15:.1f}" if s.get("t_target_k") else ""
            steps = (
                f"{s['steps_done']:,}/{s['steps']:,}"
                if s["state"] == "running"
                else f"{s['steps']:,}"
                if s["command"] == "run"
                else "min"
            )
            d = st.get("drift")
            drift = "" if not d else ("**yes**" if d["drift"] else "no")
            tm = f"{st['t_c']['mean']:.1f}" if st.get("t_c") else ""
            lines.append(
                f"| {s['index']} | {s['name']} | {s['state']} | {steps} | {tset} | {tm} |"
                f" {_pm(st.get('density'), '.4f')} | {_pm(st.get('enthalpy'), '.1f')} |"
                f" {drift} |"
            )
    hold = r.get("hold")
    if hold:
        lines += ["", "## 500 K hold checks", ""]
        if hold["state"] != "done":
            lines.append(f"- hold (segment {hold['segment']}) not complete yet")
        elif "error" in hold:
            lines.append(f"- error: {hold['error']}")
        else:
            m, a, c = hold["msid"], hold["ree_acf"], hold["com_msd"]
            lines.append(
                f"- hold.dcd: {hold['frames']} frames every {hold['frame_ps']:g} ps"
                f" ({hold['hold_ns']:.1f} ns){' (cached)' if hold.get('cached') else ''}"
            )
            ref = m["reference"]
            drift = (
                "n/a"
                if m["drift"] is None
                else f"halves {m['first_half']:.3f} -> {m['second_half']:.3f}"
                f" (Δ {m['delta']:+.3f} ± {m['delta_sem']:.3f}),"
                f" drift {'**yes**' if m['drift'] else 'no'}"
            )
            lines.append(
                f"- D37 C_n plateau (n ≥ 100 C, {m['frames_used']} frames):"
                f" **{m['plateau']:.3f}** vs melt {ref[0]:g} ±10%"
                f" ({'within' if m['within_reference'] else '**outside**'}); {drift}"
                f" -> **{'PASS' if m['passed'] else 'FAIL'}**"
            )
            t = a["t_1e_ns"]
            lines.append(
                f"- end-to-end ACF <R(t)·R(0)>/<R²>: {a['acf_at_lag']:.3f} at"
                f" {a['lag_ns']:.2f} ns (half the hold); 1/e "
                + (f"at {t:.2f} ns" if t is not None else "**not reached**")
                + f"; <R²> = {a['r2_mean_A2']:.0f} Å²"
            )
            lines.append(
                f"- chain COM MSD({c['lag_ns']:.2f} ns) = {c['msd_A2']:.0f} Å² vs"
                f" <Rg²> = {c['rg2_A2']:.0f} Å²: ratio **{c['ratio']:.2f}**"
            )
    hyst = r.get("hysteresis")
    if hyst:
        lines += [
            "",
            "## Cooling (prep step-cool) vs heating (sweep) density",
            "",
            "| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |",
            "|---|---|---|---|---|",
        ]
        for h in hyst:
            rs = f"{h['rho_sweep']:.4f}" if h["rho_sweep"] is not None else "outside sweep"
            dp = f"{h['delta_pct']:+.3f}" if h["delta_pct"] is not None else ""
            lines.append(
                f"| {h['cool_step']} | {h['t_k']:.1f} | {h['rho_cool']:.4f} ± "
                f"{h['rho_cool_sem']:.4f} | {rs} | {dp} |"
            )
    svh = r.get("step_vs_hold")
    if svh:
        lines += [
            "",
            f"## Sweep step vs following hold (flag: > {N_SIGMA:g} combined SEM)",
            "",
            "| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |",
            "|---|---|---|---|---|---|",
        ]
        for v in svh:
            d, h = v.get("density"), v.get("enthalpy")
            lines.append(
                f"| {v['t_c']:g} | {d['step']:.4f} | {d['hold']:.4f} |"
                f" {d['delta']:+.4f} ± {d['sem']:.4f} |"
                + (f" {h['delta']:+.1f} ± {h['sem']:.1f} |" if h else " |")
                + f" {'**yes**' if v['flag'] else 'no'} |"
                if d
                else f"| {v['t_c']:g} | | | | |"
            )
    if r.get("plots"):
        lines += ["", "## Plots", ""]
        for p in r["plots"].values():
            lines += [f"**{p['title']}**", "", f"![{p['title']}]({p['file']})", ""]
    return "\n".join(lines) + "\n"


def summary_markdown(
    reports: list[dict], now: float | None = None, base: str | Path | None = None
) -> str:
    """One table across runs: system, stage, node, status, % done, ETA, ns/day, checks.

    With ``base`` (the summary's directory), stages link to each report's ``_md`` path.
    """
    now = dt.datetime.now().timestamp() if now is None else now
    lines = [
        f"# Run progress ({_when(_iso(now))})",
        "",
        ("| system | stage | node | status | % done | current | ETA | ns/day | log age | checks |"),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(reports, key=lambda r: (r["system"], r["stage"], r["node"])):
        pct = f"{r['percent']:.1f}" if r.get("percent") is not None else ""
        cur = r.get("current") or {}
        nsd = f"{r['ns_per_day']:.2f}" if r.get("ns_per_day") else ""
        stage = r["stage"]
        if base is not None and r.get("_md"):
            stage = f"[{stage}]({os.path.relpath(r['_md'], base)})"
        lm = r.get("log_mtime")
        age = now - dt.datetime.fromisoformat(lm).timestamp() if lm else None
        lines.append(
            f"| {r['system']} | {stage} | {r['node']} | {r['status']} | {pct} |"
            f" {cur.get('name', '')} | {_when(r.get('eta'))} | {nsd} |"
            f" {_age(age)} | {'; '.join(r.get('flags', []))} |"
        )
    return "\n".join(lines) + "\n"


def write_report(report: dict, out_dir: Path) -> None:
    """Write progress.json and progress.md atomically into ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in (
        (JSON_NAME, json.dumps(report, indent=1, sort_keys=True) + "\n"),
        (MD_NAME, render_markdown(report)),
    ):
        tmp = out_dir / (name + ".tmp")
        tmp.write_text(text)
        os.replace(tmp, out_dir / name)


def collect_reports(dirs) -> list[dict]:
    """Every progress.json under ``dirs`` (recursively)."""
    reports = []
    for d in dirs:
        for p in sorted(Path(d).rglob(JSON_NAME)):
            r = load_json(p)
            if r and r.get("version") == REPORT_VERSION:
                r["_md"] = str(p.with_name(MD_NAME))
                reports.append(r)
    return reports
