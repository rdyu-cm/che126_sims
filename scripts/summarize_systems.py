"""Running markdown summary of every system: run status, equilibration checks, properties.

Reads (read-only) the `sepsim progress` reports (``<runs>/<system>/<stage>/progress.json``,
plus ``run_manifest.json``), the `sepsim analyze` results
(``<analysis>/<system>/<stage>/results.json``: ``sweep`` per D49, ``pore`` if present)
and the system manifests (``<systems>/<id>/manifest.yaml``), and writes one markdown file
(default ``results/summary.md``). Nothing is recomputed: every number comes from those
files, and anything missing is shown as "—".

    uv run --frozen python scripts/summarize_systems.py [--runs DIR ...] [--analysis DIR]
        [--systems DIR] [--out FILE]

``--runs`` may be given more than once (e.g. the server's ``results/runs`` plus a copy of
the other node's progress files); for the same system/stage the report with the most MD
steps done (then the newest log) wins.

Stage directories: ``prep``, ``extend``, ``cool``, ``sweep``, ``pore_relax``, ``pore``
(a suffix such as ``sweep_d47`` is the same stage). Directories whose suffix contains
``old``, ``cancel`` or ``timeout`` are superseded: listed, never used for results.
``bench*`` and ``smoke*`` directories are ignored.
"""

from __future__ import annotations

import argparse
import inspect
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from sepsim.analysis.chain import MELT_C_INF_500K, msid_check
from sepsim.progress import D47_ACF, D47_MSD_RG2

ROOT = Path(__file__).resolve().parents[1]
DASH = "—"

STAGES = ("prep", "extend", "cool", "sweep", "pore_relax", "pore")
IGNORED_PREFIXES = ("bench", "smoke")
SUPERSEDED_MARKERS = ("old", "cancel", "timeout")
POLYMER_ORDER = {"pe": 0, "ipp": 1}
RESOLUTION_ORDER = {"cg": 0, "ua": 1, "aa": 2}
POLYMER_NAME = {"pe": "PE", "ipp": "iPP"}
# D47: C1500-type CG chains cannot relax as a whole (>> us); they rely on the D37
# no-distortion check instead of the D47 criteria.
D47_EXEMPT_CG_CARBONS = 1000
_MSID = inspect.signature(msid_check).parameters
C_N_TOL = _MSID["tolerance"].default
C_N_MIN = _MSID["n_min"].default


# --------------------------------------------------------------------------- formatting


def fnum(x, spec: str = ".3g") -> str:
    if x is None or isinstance(x, bool):
        return DASH
    try:
        return format(int(x), spec) if spec.endswith("d") else format(float(x), spec)
    except (TypeError, ValueError):
        return DASH


def fpm(ms, spec: str = ".3g", sem_spec: str | None = None) -> str:
    """'mean ± sem' from a {mean, sem} dict (sem optional)."""
    if not isinstance(ms, dict) or ms.get("mean") is None:
        return DASH
    m = fnum(ms["mean"], spec)
    s = ms.get("sem")
    return m if s is None else f"{m} ± {fnum(s, sem_spec or spec)}"


def parse_time(s) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    try:
        t = datetime.fromisoformat(s)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def utc(s) -> str:
    t = parse_time(s)
    return t.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC") if t else DASH


def get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        elif isinstance(d, list) and isinstance(k, int) and -len(d) <= k < len(d):
            d = d[k]
        else:
            return default
        if d is None:
            return default
    return d


def cell(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return out


# --------------------------------------------------------------------------- loading


def load_json(path: Path) -> dict | None:
    try:
        d = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def load_yaml(path: Path) -> dict | None:
    try:
        d = yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError):
        return None
    return d if isinstance(d, dict) else None


def classify_stage(name: str) -> tuple[str | None, bool]:
    """(stage kind, superseded) of a run directory name; kind None = ignored/unknown."""
    if name.startswith(IGNORED_PREFIXES):
        return None, False
    kind = max((s for s in STAGES if name == s or name.startswith(s + "_")), key=len, default=None)
    if kind is None:
        return None, False
    suffix = name[len(kind) :]
    return kind, any(m in suffix for m in SUPERSEDED_MARKERS)


def _rank(run: dict) -> tuple:
    p = run.get("progress") or {}
    t = parse_time(p.get("log_mtime")) or parse_time(p.get("generated"))
    return (p.get("steps_done") or 0, t.timestamp() if t else 0.0)


def load_runs(roots: list[Path]) -> dict[str, dict[str, dict]]:
    """{system: {stage dir: run}}; a run has kind, superseded, progress, manifest, root."""
    runs: dict[str, dict[str, dict]] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for sdir in sorted(p for p in root.iterdir() if p.is_dir()):
            for rdir in sorted(p for p in sdir.iterdir() if p.is_dir()):
                kind, superseded = classify_stage(rdir.name)
                if kind is None:
                    continue
                prog = load_json(rdir / "progress.json")
                man = load_json(rdir / "run_manifest.json")
                if prog is None and man is None:
                    continue
                run = {
                    "dir": rdir.name,
                    "kind": kind,
                    "superseded": superseded,
                    "progress": prog,
                    "manifest": man,
                    "path": str(rdir),
                }
                old = runs.setdefault(sdir.name, {}).get(rdir.name)
                if old is None or _rank(run) > _rank(old):
                    runs[sdir.name][rdir.name] = run
    return runs


def load_analysis(root: Path) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    if not root.is_dir():
        return out
    for f in sorted(root.glob("*/*/results.json")):
        d = load_json(f)
        if d is not None:
            out.setdefault(f.parent.parent.name, {})[f.parent.name] = d
    return out


def load_systems(root: Path) -> dict[str, dict]:
    out = {}
    if root.is_dir():
        for f in sorted(root.glob("*/manifest.yaml")):
            m = load_yaml(f)
            if m is not None:
                m["_sha256"] = _sha256(f)
                out[f.parent.name] = m
    return out


def _sha256(path: Path) -> str | None:
    import hashlib

    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


# --------------------------------------------------------------------------- per system


def meta(sid: str, man: dict | None) -> dict:
    """Polymer, resolution, category from the manifest (else parsed from the id)."""
    parts = sid.split("_")
    man = man or {}
    pol = man.get("polymer") or (parts[0] if parts else None)
    res = man.get("resolution") or (parts[1] if len(parts) > 1 else None)
    pore = man.get("pore") if isinstance(man.get("pore"), dict) else None
    if pore is None and "pore" in sid:
        pore = {"kind": "wide" if "pore500k" in sid else "narrow"}
    if pore:
        category = 2 if pore.get("kind") == "wide" else 3
    elif man.get("conversion") or man.get("replicate") or man.get("source"):
        category = 1
    else:
        category = 0
    return {"polymer": pol, "resolution": res, "pore": pore, "category": category}


def sort_key(sid: str, m: dict, man: dict | None) -> tuple:
    """PE before iPP, CG/UA/AA, bulk before pores; bulk: built before derived, then
    chain length and count; pores: chain count, wide before narrow, then width."""
    man = man or {}
    pore = m["pore"] or {}
    head = (POLYMER_ORDER.get(m["polymer"], 9), RESOLUTION_ORDER.get(m["resolution"], 9))
    n, c = man.get("n_chains") or 0, man.get("n_carbons") or 0
    if not pore:
        return (*head, 0, m["category"], c, n, 0.0, sid)
    return (*head, 1, n, m["category"], -(pore.get("nominal_width_nm") or 0.0), 0, sid)


def current_runs(runs: dict[str, dict]) -> list[dict]:
    """Non-superseded runs in stage order (same stage: older start first)."""
    cur = [r for r in runs.values() if not r["superseded"]]

    def key(r):
        t = parse_time(get(r, "progress", "start_time") or get(r, "manifest", "start_time"))
        return (STAGES.index(r["kind"]), t.timestamp() if t else 0.0, r["dir"])

    return sorted(cur, key=key)


def is_done(run: dict | None) -> bool:
    """Finished, or an extension stopped (not running) after its D47 pass (D47: cancel
    once the checks pass and use the latest snapshot)."""
    st = get(run, "progress", "status")
    if st == "finished":
        return True
    return bool(
        run
        and run["kind"] == "extend"
        and get(run, "progress", "hold", "d47", "passed")
        and st not in ("running", "starting")
    )


def latest(runs: list[dict], kind: str) -> dict | None:
    sel = [r for r in runs if r["kind"] == kind]
    return sel[-1] if sel else None


def run_status(run: dict | None) -> str:
    if run is None:
        return "not started"
    p = run.get("progress")
    if p is None:
        st = get(run, "manifest", "status") or "unknown"
        return f"{st} (no progress.json)"
    st = p.get("status") or DASH
    d47 = get(p, "hold", "d47", "passed")
    if run["kind"] == "extend" and d47 and st in ("cancelled/killed?", "stalled?"):
        st = f"stopped after D47 PASS ({st})"
    if p.get("status") != "finished" and p.get("percent") is not None:
        st += f", {p['percent']:.1f}%"
    if p.get("status") == "running":
        n, tot, cur = p.get("n_done"), p.get("n_segments"), get(p, "current", "name")
        bits = [f"{n}/{tot} segments" if n is not None and tot else None, cur]
        bits = [b for b in bits if b]
        if bits:
            st += f" ({', '.join(bits)})"
        if p.get("eta"):
            st += f"; ETA {utc(p['eta'])}"
    return st


def source_info(man: dict | None) -> list[dict]:
    """Provenance chain [{id, data_file, manifest_sha256}, ...] nearest first."""
    out, src = [], (man or {}).get("source")
    while isinstance(src, dict):
        out.append(src)
        src = src.get("source")
    return out


def short_data(sid: str | None, path: str | None) -> str:
    """'extend/hold_ext_70ns.data' from a full or node-prefixed run path."""
    if not path:
        return DASH
    p = str(path).split(":", 1)[-1] if ":" in str(path)[:20] else str(path)
    if sid and f"/{sid}/" in "/" + p:
        return p.split(f"{sid}/", 1)[1]
    return p


def hold_checks(run: dict | None) -> dict | None:
    """The 500 K chain checks of a prep or extend run (from progress.json), normalized."""
    hold = get(run, "progress", "hold")
    if not isinstance(hold, dict) or not (hold.get("msid") or hold.get("ree_acf")):
        return None
    m = hold.get("msid") or {}
    a = hold.get("ree_acf") or {}
    c = hold.get("com_msd") or {}
    d47 = hold.get("d47")
    acf, ratio = a.get("acf_at_lag"), c.get("ratio")
    if d47 is None and acf is not None and ratio is not None:  # prep hold alone
        d47 = {
            "acf": acf,
            "lag_ns": a.get("lag_ns"),
            "ratio": ratio,
            "passed": bool(acf < D47_ACF and ratio >= D47_MSD_RG2),
            "computed_here": True,
        }
    return {
        "stage": run["dir"],
        "kind": run["kind"],
        "hold_ns": hold.get("hold_ns"),
        "complete": hold.get("state") == "done",
        "running": get(run, "progress", "status") in ("running", "stalled?", "starting"),
        "d47": d47,
        "t_1e_ns": a.get("t_1e_ns"),
        "plateau": m.get("plateau"),
        "reference": m.get("reference"),
        "within_reference": m.get("within_reference"),
        "drift": m.get("drift"),
        "delta": m.get("delta"),
        "delta_sem": m.get("delta_sem"),
        "error": hold.get("error"),
    }


def equilibration(sid: str, ctx: dict, seen: frozenset = frozenset()) -> dict:
    """Equilibration verdict: own extend (D47) > inherited from the source (ua2aa
    conversions, pores) > own prep hold only. Keys: basis, checks, accepted, text."""
    man = ctx["systems"].get(sid) or {}
    m = meta(sid, man)
    runs = current_runs(ctx["runs"].get(sid, {}))
    own_ext = hold_checks(latest(runs, "extend"))
    own_prep = hold_checks(latest(runs, "prep"))
    long_cg = m["resolution"] == "cg" and (man.get("n_carbons") or 0) >= D47_EXEMPT_CG_CARBONS
    if own_ext and own_ext.get("d47"):
        return _verdict("own", own_ext, long_cg, sid)
    src = source_info(man)
    if (man.get("conversion") or m["pore"]) and src and src[0].get("id") not in seen:
        parent = equilibration(src[0]["id"], ctx, seen | {sid})
        via = [src[0]["id"], *parent.get("via", [])]
        parent = dict(parent, basis="inherited", via=via)
        parent["text"] = f"from {' ← '.join(via)}: {parent.get('base_text', parent['text'])}"
        parent["own_prep"] = own_prep
        return parent
    if own_prep and own_prep.get("d47"):
        return _verdict("prep only", own_prep, long_cg, sid)
    return {"basis": None, "checks": own_ext or own_prep, "accepted": None, "text": DASH}


def _verdict(basis: str, ch: dict, long_cg: bool, sid: str) -> dict:
    d = ch["d47"]
    vals = (
        f"ACF {fnum(d.get('acf'), '.2f')} at {fnum(d.get('lag_ns'), '.1f')} ns,"
        f" MSD/⟨Rg²⟩ {fnum(d.get('ratio'), '.2f')}; {fnum(ch.get('hold_ns'), '.1f')} ns at 500 K"
    )
    drift = ch.get("drift")
    if long_cg:
        acc = drift is False
        head = "D47 n/a (long CG chain)"
        tail = "no C_n drift: accepted" if acc else "C_n drift: not accepted" if drift else DASH
        text = f"{head}; {vals}; {tail}"
    else:
        ok = bool(d.get("passed"))
        # D47 alone decides; the C_n drift spans the unrelaxed prep hold too, so it is informational
        acc = ok
        head = f"D47 {'PASS' if ok else 'FAIL'}"
        if basis == "prep only":
            head += f" ({ch['stage']} hold only)"
        if ch.get("running"):
            head += f" (so far; {ch['stage']} running)"
        tail = "accepted" if acc else "not accepted"
        if ok and drift:
            tail += " (C_n drift over prep + extension, informational)"
        text = f"{head}; {vals}; {tail}"
    return {"basis": basis, "checks": ch, "accepted": acc, "text": text, "base_text": text}


def cn_text(ch: dict | None, polymer: str | None) -> str:
    """C_n plateau vs the melt reference (informational) and the drift check."""
    if not ch or ch.get("plateau") is None:
        return DASH
    ref = ch.get("reference") or MELT_C_INF_500K.get(polymer or "")
    ref_s = fnum(ref[0], "g") if ref else DASH
    inside = ch.get("within_reference")
    band = "in band" if inside else "outside band" if inside is False else DASH
    drift = ch.get("drift")
    drift_s = "drift" if drift else "no drift" if drift is False else "drift n/a"
    dd = ""
    if ch.get("delta") is not None:
        dd = f" (Δ {fnum(ch['delta'], '+.2f')} ± {fnum(ch.get('delta_sem'), '.2f')})"
    return f"{fnum(ch['plateau'], '.2f')} vs {ref_s} ({band}, info); {drift_s}{dd}"


# --------------------------------------------------------------------------- rendering


def header(ctx: dict) -> list[str]:
    refs = ", ".join(
        f"{POLYMER_NAME.get(k, k)} {fnum(v[0], 'g')}" for k, v in MELT_C_INF_500K.items()
    )
    return [
        "# System summary: tested properties and equilibration checks",
        "",
        f"- Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        f"- Git commit: {ctx['commit']}",
        (
            f"- Inputs: runs {', '.join(str(r) for r in ctx['run_roots'])}; analysis"
            f" {ctx['analysis_root']}; systems {ctx['systems_root']}"
        ),
        "- Regenerate: `uv run --frozen python scripts/summarize_systems.py`",
        "",
        "**Checks (legend)**",
        "",
        (
            f"- **D37 C_n**: plateau of ⟨R²(n)⟩/(n l²) for n ≥ {C_N_MIN} carbons on the 500 K hold,"
            f" compared with the melt C∞ at 500 K ({refs}, ±{C_N_TOL:.0%}), and a drift test"
            " (second minus first half of the hold beyond 2 combined SEM)."
        ),
        (
            f"- **D47**: end-to-end vector ACF < 1/e ({D47_ACF:.3f}) **and** chain COM MSD ≥"
            f" {D47_MSD_RG2:g}⟨Rg²⟩, both at a lag of half the combined 500 K hold (prep hold +"
            " extension)."
        ),
        (
            "- **Rule**: a system that passes D47 is accepted even if its C_n misses the"
            " literature value; that miss is a model property, not a failure, and no more"
            " compute is spent on it. The C_n value vs literature and its drift (taken over"
            ' prep hold + extension, so it includes the unrelaxed prep) are shown as "info".'
        ),
        (
            f"- Long CG chains (C ≥ {D47_EXEMPT_CG_CARBONS}, i.e. C1500): whole-chain relaxation"
            " is out of reach, so D47 does not apply (D47); they rely on correct construction"
            " and the C_n no-drift check."
        ),
        (
            "- Pores and AA boxes converted from UA (ua2aa) inherit the equilibration of the"
            " bulk box they were built from."
        ),
        (
            '- Run status comes from `sepsim progress` ("cancelled/killed?" = log silent > 6 h'
            " without a finished manifest; ETAs converted to UTC). Superseded systems and run"
            " directories (renamed old/cancelled runs, rebuilt sources) are listed separately"
            " and never used for the numbers."
        ),
        (
            '- **"drift seg …"** (monitor flag): those segments show a significant trend in a'
            " thermo quantity over their analysis window. It is informational."
        ),
        "",
    ]


def overview(ctx: dict, order: list[str]) -> list[str]:
    rows = []
    for sid in order:
        if is_superseded(sid, ctx):
            continue
        man = ctx["systems"].get(sid) or {}
        m = ctx["meta"][sid]
        stage, status = stage_now(sid, ctx)
        eq = ctx["eq"][sid]
        ana = (
            ", ".join(
                st + (" (stale)" if (sid, st) in ctx["stale_analysis"] else "")
                for st in sorted(ctx["analysis"].get(sid, {}))
            )
            or "no"
        )
        n_at = get(man, "counts", "total", "atoms")
        sites = (
            DASH if n_at is None else f"{n_at:,}" + (" beads" if m["resolution"] == "cg" else "")
        )
        rows.append(
            [
                f"`{sid}`",
                (m["resolution"] or DASH).upper(),
                POLYMER_NAME.get(m["polymer"], m["polymer"] or DASH),
                kind_label(m),
                f"{man.get('n_chains', DASH)} × C{man.get('n_carbons', DASH)}",
                sites,
                stage,
                status,
                eq["text"],
                cn_text(eq.get("checks"), m["polymer"]),
                ana,
            ]
        )
    return [
        "## Overview",
        "",
        *table(
            [
                "System",
                "Res",
                "Polymer",
                "Kind",
                "Chains × length",
                "Sites",
                "Stage now",
                "Status",
                "Equilibration (D47)",
                "C_n plateau (D37)",
                "Analysis",
            ],
            rows,
        ),
        "",
    ]


def kind_label(m: dict) -> str:
    if m["pore"]:
        w = m["pore"].get("nominal_width_nm")
        return f"pore ({m['pore'].get('kind', DASH)}, {fnum(w, 'g')} nm)"
    return {0: "bulk", 1: "bulk (derived)"}.get(m["category"], DASH)


def provenance(sid: str, ctx: dict) -> list[str]:
    man = ctx["systems"].get(sid)
    if man is None:
        return ["- Manifest: not found in the systems directory."]
    out = []
    ff = get(man, "forcefield", "name") or DASH
    out.append(
        f"- {POLYMER_NAME.get(man.get('polymer'), DASH)} {str(man.get('resolution', DASH)).upper()},"
        f" {man.get('n_chains', DASH)} chains × C{man.get('n_carbons', DASH)}"
        f" ({get(man, 'formula', 'per_chain') or DASH}),"
        f" {fnum(get(man, 'counts', 'total', 'atoms'), ',d')} atoms/beads, force field {ff},"
        f" box density {fnum(man.get('density_g_cm3'), '.4f')} g/cm³ (as built)"
    )
    src = source_info(man)
    if man.get("growth"):
        out.append(
            f"- Built: grown chains (seed {man.get('seed', DASH)}, build density"
            f" {fnum(man.get('build_density_g_cm3'), 'g')} g/cm³)"
        )
    if man.get("conversion"):
        out.append(f"- Built: {get(man, 'conversion', 'method') or 'conversion'}")
    if man.get("replicate"):
        r = man["replicate"]
        f = "×".join(str(x) for x in r.get("factors") or []) or DASH
        out.append(f"- Replicated {f} from {r.get('source_id', DASH)}")
    pore = man.get("pore")
    if isinstance(pore, dict):
        bits = [
            f"{pore.get('kind', DASH)} pore, nominal {fnum(pore.get('nominal_width_nm'), 'g')} nm",
        ]
        if pore.get("width_500k_nm") is not None:
            bits.append(f"{fnum(pore['width_500k_nm'], '.2f')} nm at 500 K")
        if pore.get("wall_thickness_angstrom") is not None:
            bits.append(f"wall {fnum(pore['wall_thickness_angstrom'] / 10, '.2f')} nm")
        if pore.get("clear_gap_angstrom") is not None:
            bits.append(f"clear gap {fnum(pore['clear_gap_angstrom'] / 10, '.2f')} nm")
        if pore.get("area_angstrom2") is not None:
            bits.append(f"area {fnum(pore['area_angstrom2'] / 100, '.1f')} nm²")
        out.append("- Pore: " + ", ".join(bits))
    if src:
        chain = " ← ".join(
            f"{s.get('id', DASH)} (`{short_data(s.get('id'), s.get('data_file'))}`)" for s in src
        )
        out.append(f"- Built from: {chain}")
        stale = ctx["stale"].get(sid)
        if stale:
            out.append(f"- **Stale source:** {stale}")
    sup = ctx["superseded_by"].get(sid)
    if sup:
        out.append(f"- **Superseded** by {sup}")
    return out


def stage_lines(sid: str, ctx: dict) -> list[str]:
    allruns = ctx["runs"].get(sid, {})
    runs = current_runs(allruns)
    out = []
    for r in runs:
        p = r.get("progress") or {}
        node = p.get("node") or get(r, "manifest", "hostname") or DASH
        inp = [
            f.get("arg")
            for f in get(r, "manifest", "inputs", "files", default=[]) or []
            if f.get("command") == "read_data"
        ]
        line = f"- **{r['dir']}** ({node}): {run_status(r)}"
        if p.get("start_time"):
            line += f"; started {utc(p['start_time'])}"
        if p.get("end_time"):
            line += f", ended {utc(p['end_time'])}"
        if inp:
            line += "; reads " + ", ".join(f"`{short_input(x)}`" for x in inp if x)
        out.append(line)
        ch = hold_checks(r)
        if ch:
            d = ch.get("d47") or {}
            label = "D47" if not d.get("computed_here") else "D47 criteria on this hold"
            verdict = "PASS" if d.get("passed") else "FAIL" if d else DASH
            out.append(
                f"  - 500 K hold {fnum(ch.get('hold_ns'), '.1f')} ns"
                f"{' (so far)' if ch.get('running') else ''}: {label} {verdict}"
                f" (R_ee ACF {fnum(d.get('acf'), '.2f')} at {fnum(d.get('lag_ns'), '.1f')} ns,"
                f" {t1e(ch.get('t_1e_ns'))}; COM MSD/⟨Rg²⟩"
                f" {fnum(d.get('ratio'), '.2f')}); C_n {cn_text(ch, ctx['meta'][sid]['polymer'])}"
            )
        elif get(p, "hold", "error"):
            out.append(f"  - hold check error: {p['hold']['error']}")
        flags = [f for f in p.get("flags") or [] if not f.startswith(("D37", "D47"))]
        if flags:
            out.append(f"  - monitor flags: {'; '.join(flags)}")
        gam = pore_gamma_rows(p) if r["kind"] in ("pore", "pore_relax") else []
        if gam:
            out.append(
                "  - γ per hold (monitor, second half of each segment, mN/m): "
                + "; ".join(f"{t} °C {g}" for t, g in gam)
            )
    old = sorted((r for r in allruns.values() if r["superseded"]), key=lambda r: r["dir"])
    if old:
        out.append(
            "- Superseded (not used): "
            + "; ".join(
                f"{r['dir']} ({get(r, 'progress', 'status') or get(r, 'manifest', 'status') or DASH})"
                for r in old
            )
        )
    return out or ["- No runs found."]


def t1e(t) -> str:
    return "1/e not reached" if t is None else f"1/e at {fnum(t, '.2f')} ns"


def short_input(arg: str) -> str:
    """'systems/<id>/data.lmp' instead of '../../../../systems/<id>/data.lmp'."""
    return re.sub(r"^(\.\./)+(?=systems/)", "", arg)


def pore_gamma_rows(p: dict) -> list[tuple[str, str]]:
    rows = []
    for s in p.get("segments") or []:
        g = get(s, "stats", "gamma")
        if g and s.get("sweep_kind") == "hold":
            rows.append((fnum(s.get("t_c"), "g"), fpm(g, ".1f")))
    return rows


def sweep_section(res: dict) -> list[str]:
    segs = {s.get("index"): s for s in res.get("segments") or [] if isinstance(s, dict)}
    rows = []
    for h in res.get("holds") or []:
        t = h.get("traj") or {}
        seg = segs.get(h.get("index")) or {}
        com = t.get("com_msd") or {}
        if com.get("D_cm2_s") is not None:
            dcom = f"{fnum(com['D_cm2_s'], '.3g')} ± {fnum(com.get('D_err_cm2_s'), '.2g')}"
        elif com:
            dcom = f"not diffusive (slope {fnum(com.get('slope_end'), '.2f')})"
        else:
            dcom = DASH
        rows.append(
            [
                fnum(h.get("t_c"), "g"),
                fpm(get(seg, "stats", "density"), ".5f"),
                fpm(
                    {"mean": get(h, "kappa", "kappa_T_GPa"), "sem": get(h, "kappa", "sem")},
                    ".3f",
                ),
                fpm(get(t, "rg", "rg_A"), ".2f"),
                fpm(get(t, "ree", "ree_A"), ".1f"),
                fpm(get(t, "c_n", "plateau"), ".2f"),
                fnum(get(t, "p2", "t_1e_ps"), ".3g"),
                fnum(com.get("msd_at_max_A2"), ".4g")
                + (
                    f" ({fnum(com['lag_max_ps'] / 1000, 'g')} ns)"
                    if com.get("lag_max_ps") is not None
                    else ""
                ),
                dcom,
                "yes" if t.get("available") else "no" if t else DASH,
            ]
        )
    out = [
        (
            f"`sepsim analyze sweep`, generated {utc(res.get('generated'))}"
            f" on {res.get('generated_on', DASH)}, run {res.get('run_status', DASH)}."
        ),
        "",
    ]
    if rows:
        out += table(
            [
                "T (°C)",
                "ρ (g/cm³)",
                "κ_T (GPa⁻¹)",
                "Rg (Å)",
                "R_ee (Å)",
                "C_n",
                "P2 1/e (ps)",
                "COM MSD max (Å²) (lag)",
                "D_COM (cm²/s)",
                "traj",
            ],
            rows,
        )
        out.append("")
    fits = res.get("fits") or {}
    av = {tuple(f.get("window_c") or ()): f for f in fits.get("alpha_V") or []}
    cp = {tuple(f.get("window_c") or ()): f for f in fits.get("cp") or []}
    frows = []
    for w in sorted(
        set(av) | set(cp), key=lambda w: (-(w[1] - w[0]), w[0]) if len(w) == 2 else (0, 0)
    ):
        a, c = av.get(w, {}), cp.get(w, {})
        a_s = (
            f"{fnum(a['alpha_V_per_K'] * 1e4, '.3f')} ± {fnum((a.get('err') or 0) * 1e4, '.3f')}"
            if a.get("alpha_V_per_K") is not None
            else DASH
        )
        c_s = (
            f"{fnum(c['cp_J_gK'], '.3f')} ± {fnum(c.get('err'), '.3f')}"
            if c.get("cp_J_gK") is not None
            else DASH
        )
        frows.append(
            [
                "–".join(fnum(x, "g") for x in w) if w else DASH,
                a_s,
                fnum(a.get("chi2_red"), ".3g"),
                c_s,
                fnum(c.get("chi2_red"), ".3g"),
                fnum(a.get("n") or c.get("n"), "g"),
            ]
        )
    if frows:
        out += table(
            [
                "Fit window (°C)",
                "α_V (10⁻⁴ K⁻¹)",
                "χ²_red α",
                "Cp classical (J g⁻¹ K⁻¹)",
                "χ²_red Cp",
                "points",
            ],
            frows,
        )
        out.append("")
    notes = (
        list(res.get("caveats") or [])
        + list(fits.get("notes") or [])
        + list(res.get("notes") or [])
    )
    for n in notes:
        out.append(f"- Note: {n}")
    if notes:
        out.append("")
    return out


_POR_SKIP = {"plots", "curves", "run_git", "code_git", "method", "caveats", "notes", "version"}
_POR_KEYS = (
    "gamma",
    "tension",
    "width",
    "gap",
    "thick",
    "interface",
    "delta",
    "density",
    "plateau",
    "rho",
    "d_",
    "msd",
    "mobility",
    "t_c",
    "t_set",
)


def _flatten(d, prefix: str = "", depth: int = 0) -> dict[str, str]:
    """Scalars (and {mean, sem} pairs) of a nested dict as dotted keys; lists skipped."""
    out = {}
    if not isinstance(d, dict) or depth > 3:
        return out
    for k, v in d.items():
        if k in _POR_SKIP:
            continue
        key = f"{prefix}{k}"
        if isinstance(v, dict) and "mean" in v and not isinstance(v["mean"], (dict, list)):
            out[key] = fpm(v, ".4g")
        elif isinstance(v, dict):
            out.update(_flatten(v, key + ".", depth + 1))
        elif isinstance(v, bool) or v is None:
            continue
        elif isinstance(v, (int, float)):
            out[key] = fnum(v, ".4g")
        elif isinstance(v, str) and len(v) <= 40:
            out[key] = v
    return out


def _is_key(name: str) -> bool:
    n = name.lower()
    return any(k in n for k in _POR_KEYS)


def pore_section(res: dict) -> list[str]:
    """Generic: key scalars at the top level and a table per list of per-T records."""
    out = [
        (
            f"Pore analysis (`sepsim analyze pore`, generated {utc(res.get('generated'))}"
            f" on {res.get('generated_on', DASH)}):"
        ),
        "",
    ]
    top = {k: v for k, v in _flatten(res).items() if _is_key(k)}
    for k, v in top.items():
        out.append(f"- {k}: {v}")
    if top:
        out.append("")
    for name, val in res.items():
        if name in _POR_SKIP or not isinstance(val, list):
            continue
        recs = [_flatten(x) for x in val if isinstance(x, dict)]
        recs = [r for r in recs if r]
        if not recs:
            continue
        cols = []
        for r in recs:
            cols += [k for k in r if _is_key(k) and k not in cols]
        cols = cols[:12]
        if not cols:
            continue
        out.append(f"{name}:")
        out.append("")
        out += table(cols, [[r.get(c, DASH) for c in cols] for r in recs])
        out.append("")
    for n in list(res.get("caveats") or []) + list(res.get("notes") or []):
        out.append(f"- Note: {n}")
    if len(out) == 2:
        out.append("- (no recognised key numbers in results.json)")
    out.append("")
    return out


def system_section(sid: str, ctx: dict) -> list[str]:
    eq = ctx["eq"][sid]
    title = f"### `{sid}`" + (" (superseded)" if is_superseded(sid, ctx) else "")
    out = [title, "", "**Provenance**", "", *provenance(sid, ctx), ""]
    out += ["**Equilibration**", ""]
    out.append(f"- Verdict: {eq['text']}")
    out.append(f"- C_n plateau (D37): {cn_text(eq.get('checks'), ctx['meta'][sid]['polymer'])}")
    if eq.get("basis") == "inherited" and eq.get("own_prep"):
        op = eq["own_prep"]
        out.append(
            f"- Own {op['stage']} hold ({fnum(op.get('hold_ns'), '.1f')} ns, information):"
            f" C_n {cn_text(op, ctx['meta'][sid]['polymer'])}; R_ee ACF"
            f" {fnum(get(op, 'd47', 'acf'), '.2f')} at {fnum(get(op, 'd47', 'lag_ns'), '.1f')} ns;"
            f" COM MSD/⟨Rg²⟩ {fnum(get(op, 'd47', 'ratio'), '.2f')}"
        )
    out += ["", "**Stages**", "", *stage_lines(sid, ctx), ""]
    return out


# --------------------------------------------------------------------------- pending


def expected_stages(sid: str, ctx: dict) -> list[str]:
    man = ctx["systems"].get(sid) or {}
    m = ctx["meta"][sid]
    have = {r["kind"] for r in current_runs(ctx["runs"].get(sid, {}))}
    if m["pore"]:
        return ["pore_relax"] if m["pore"].get("kind") == "wide" else ["pore"]
    if man.get("replicate"):
        return ["extend"]
    if man.get("conversion"):
        return ["prep", "sweep"]
    exp = ["prep"]
    if m["resolution"] == "ua" or "extend" in have:
        exp += ["extend", "cool"]
    return exp + ["sweep"]


def is_superseded(sid: str, ctx: dict) -> bool:
    return bool(ctx["superseded_by"].get(sid) or ctx["stale"].get(sid))


def stage_items(sid: str, ctx: dict) -> list[tuple[str, dict | None]]:
    """Open expected stages: (kind, run or None), skipping stages a later one replaced."""
    runs = current_runs(ctx["runs"].get(sid, {}))
    exp = expected_stages(sid, ctx)
    out = []
    for i, kind in enumerate(exp):
        r = latest(runs, kind)
        if any(latest(runs, k) for k in exp[i + 1 :]):
            continue
        if not is_done(r):
            out.append((kind, r))
    return out


def stage_now(sid: str, ctx: dict) -> tuple[str, str]:
    runs = current_runs(ctx["runs"].get(sid, {}))
    items = stage_items(sid, ctx)
    if items:
        kind, r = items[0]
        if r is None:
            return kind, "not started" if not runs else f"not started ({runs[-1]['dir']} done)"
        return r["dir"], run_status(r)
    if not runs:
        return DASH, "not started"
    parts = []
    for r in runs:
        if get(r, "progress", "status") == "finished":
            parts.append(r["dir"])
        elif is_done(r):
            parts.append(f"{r['dir']} (stopped after D47 PASS)")
        else:
            parts.append(f"{r['dir']} ({run_status(r)})")
    return "done", "finished: " + ", ".join(parts)


def pending(ctx: dict, order: list[str]) -> list[str]:
    lines = []
    for sid in order:
        if is_superseded(sid, ctx):
            continue
        items = []
        for kind, r in stage_items(sid, ctx):
            items.append(f"{kind} not started" if r is None else f"{r['dir']}: {run_status(r)}")
        runs = current_runs(ctx["runs"].get(sid, {}))
        ana = ctx["analysis"].get(sid, {})
        for kind in ("sweep", "pore"):
            r = latest(runs, kind)
            if (
                r
                and get(r, "progress", "status") == "finished"
                and not any(a == r["dir"] or a == kind for a in ana)
            ):
                items.append(f"{kind} analysis not run")
        for (s, stage), why in ctx["stale_analysis"].items():
            if s == sid:
                items.append(f"{stage} analysis: {why}")
        eq = ctx["eq"][sid]
        if eq.get("accepted") is False:
            items.append("equilibration not accepted (see the verdict)")
        elif eq.get("accepted") is None:
            items.append("no equilibration verdict yet")
        if items:
            lines.append(f"- `{sid}`: " + "; ".join(items))
    return ["## Pending and known items", "", *(lines or ["- Nothing pending."]), ""]


def superseded(ctx: dict, order: list[str]) -> list[str]:
    lines = []
    for sid in order:
        if is_superseded(sid, ctx):
            why = ctx["superseded_by"].get(sid)
            why = f"superseded by {why}" if why else ctx["stale"][sid]
            lines.append(f"- System `{sid}`: {why}")
    for sid in order:
        old = sorted(
            (r for r in ctx["runs"].get(sid, {}).values() if r["superseded"]),
            key=lambda r: r["dir"],
        )
        if old:
            lines.append(
                f"- Runs of `{sid}`: "
                + ", ".join(
                    f"{r['dir']} ({get(r, 'progress', 'status') or get(r, 'manifest', 'status') or DASH})"
                    for r in old
                )
            )
    return ["## Superseded (kept, not used)", "", *(lines or ["- None."]), ""]


def _is_sweep(stage: str, res: dict) -> bool:
    """Sweep results (D49) by the analysis stage name; else by their 'fits' block."""
    kind, _ = classify_stage(stage)
    return kind == "sweep" or (kind is None and "fits" in res)


def properties(ctx: dict, order: list[str]) -> list[str]:
    out = ["## Measured properties (bulk sweeps, holds)", ""]
    missing = []
    for sid in order:
        m = ctx["meta"][sid]
        if m["pore"] or is_superseded(sid, ctx):
            continue
        ana = {k: v for k, v in ctx["analysis"].get(sid, {}).items() if _is_sweep(k, v)}
        if not ana:
            missing.append(f"`{sid}`")
            continue
        man = ctx["systems"].get(sid) or {}
        hold = get(ctx["eq"][sid], "checks", "hold_ns")
        for stage, res in sorted(ana.items()):
            desc = (
                f"{(m['resolution'] or DASH).upper()} {POLYMER_NAME.get(m['polymer'], DASH)}"
                f" C{man.get('n_carbons', DASH)}, {fnum(hold, '.1f')} ns at 500 K"
            )
            stale = ctx["stale_analysis"].get((sid, stage))
            out += [
                f"### `{sid}` {stage} ({desc})" + (f" **{stale}**" if stale else ""),
                "",
                *sweep_section(res),
            ]
    if missing:
        out += [f"Not analyzed yet: {', '.join(missing)}.", ""]
    return out


def lateral_box(pr: dict) -> str:
    """Square lateral box edge at 25 °C (narrow pores) or 500 K (wide pores)."""
    a25, a = pr.get("area_25c_angstrom2"), pr.get("area_angstrom2")
    if a25:
        e = fnum(a25**0.5 / 10, ".1f")
        return f"{e} × {e} nm (25 °C)"
    if a:
        e = fnum(a**0.5 / 10, ".1f")
        return f"{e} × {e} nm (500 K)"
    return DASH


def pores(ctx: dict, order: list[str]) -> list[str]:
    rows, details = [], []
    for sid in order:
        m = ctx["meta"][sid]
        if not m["pore"] or is_superseded(sid, ctx):
            continue
        pr = m["pore"]
        wall = pr.get("wall_thickness_angstrom")
        run = latest(current_runs(ctx["runs"].get(sid, {})), "pore") or latest(
            current_runs(ctx["runs"].get(sid, {})), "pore_relax"
        )
        gam = pore_gamma_rows(run.get("progress") or {}) if run else []
        stage, status = stage_now(sid, ctx)
        rows.append(
            [
                f"`{sid}`",
                pr.get("kind", DASH),
                f"{fnum(pr.get('nominal_width_nm'), 'g')} nm"
                + (" (at 500 K)" if pr.get("kind") == "wide" else " (at 25 °C)"),
                f"{fnum(pr.get('width_500k_nm'), '.2f')} nm"
                if pr.get("width_500k_nm") is not None
                else DASH,
                f"{fnum(wall / 10, '.1f')} nm" + (" (500 K)" if pr.get("kind") == "wide" else "")
                if wall is not None
                else DASH,
                lateral_box(pr),
                "; ".join(f"{t} °C {g}" for t, g in gam) or DASH,
                status if stage == "done" else f"{stage}: {status}",
                ", ".join(sorted(ctx["analysis"].get(sid, {}))) or "no",
            ]
        )
        for stage_name, res in sorted(ctx["analysis"].get(sid, {}).items()):
            if not _is_sweep(stage_name, res):
                details += [f"### `{sid}` {stage_name}", "", *pore_section(res)]
    if not rows:
        return []
    out = [
        "## Pores (stage 2)",
        "",
        *table(
            [
                "System",
                "Kind",
                "Gap (nominal)",
                "Gap at 500 K",
                "Wall thickness",
                "Lateral box",
                "γ per hold (mN/m, monitor)",
                "Status",
                "Analysis",
            ],
            rows,
        ),
        "",
        (
            "γ here is the `sepsim progress` second-half mean ± SEM of each hold segment"
            " (γ = (Lz/2)[Pzz − (Pxx+Pyy)/2]); the pore analysis, when present, follows."
        ),
        "",
    ]
    return out + details


# --------------------------------------------------------------------------- main


def git_commit(root: Path) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        d = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return DASH
    if r.returncode != 0:
        return DASH
    return r.stdout.strip() + (" (dirty)" if d.returncode == 0 and d.stdout.strip() else "")


def build_context(run_roots: list[Path], analysis_root: Path, systems_root: Path) -> dict:
    ctx = {
        "runs": load_runs(run_roots),
        "analysis": load_analysis(analysis_root),
        "systems": load_systems(systems_root),
        "run_roots": run_roots,
        "analysis_root": analysis_root,
        "systems_root": systems_root,
    }
    ids = set(ctx["systems"]) | set(ctx["runs"]) | set(ctx["analysis"])
    ctx["meta"] = {s: meta(s, ctx["systems"].get(s)) for s in ids}
    # a grown AA box is superseded by its ua2aa counterpart (D47: AA from the relaxed UA)
    ctx["superseded_by"] = {
        s: f"{s}_from_ua (D47: AA is built from the relaxed UA box)"
        for s in ids
        if f"{s}_from_ua" in ids and not ctx["runs"].get(s, {}).get("sweep")
    }
    # a system whose source manifest changed since it was built (source rebuilt)
    ctx["stale"] = {}
    for s in ids:
        src = source_info(ctx["systems"].get(s))
        if not src:
            continue
        sm = ctx["systems"].get(src[0].get("id"))
        want = src[0].get("manifest_sha256")
        if sm and want and sm.get("_sha256") and want != sm["_sha256"]:
            ctx["stale"][s] = (
                f"built from an earlier {src[0]['id']} (its manifest changed since: rebuilt"
                f" source; data `{short_data(src[0]['id'], src[0].get('data_file'))}`)"
            )
    # analysis older than the run it analysed
    ctx["stale_analysis"] = {}
    for s, stages in ctx["analysis"].items():
        for stage, res in stages.items():
            run = ctx["runs"].get(s, {}).get(stage)
            t_run = parse_time(get(run, "progress", "end_time")) or parse_time(
                get(run, "progress", "start_time")
            )
            t_ana = parse_time(res.get("generated"))
            if t_run and t_ana and t_ana < t_run:
                ctx["stale_analysis"][(s, stage)] = "older than the run: rerun the analysis"
    ctx["eq"] = {s: equilibration(s, ctx) for s in ids}
    ctx["commit"] = git_commit(ROOT)
    return ctx


def render(ctx: dict, guide: str | None = None) -> str:
    order = sorted(ctx["meta"], key=lambda s: sort_key(s, ctx["meta"][s], ctx["systems"].get(s)))
    lines = header(ctx) + overview(ctx, order) + pending(ctx, order) + superseded(ctx, order)
    lines += properties(ctx, order) + pores(ctx, order)
    lines += ["## Per-system details", ""]
    for sid in order:
        lines += system_section(sid, ctx)
    if guide:
        lines += ["", guide.strip(), ""]
    return "\n".join(lines).rstrip() + "\n"


def _path(p: str) -> Path:
    q = Path(p).expanduser()
    return q if q.is_absolute() else ROOT / q


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--runs", action="append", help="run root(s) (default results/runs)")
    ap.add_argument("--analysis", default="results/analysis")
    ap.add_argument("--systems", default="systems")
    ap.add_argument("--out", default="results/summary.md")
    ap.add_argument("--guide", default="docs/property_guide.md", help="appended at the end")
    a = ap.parse_args(argv)
    roots = [_path(r) for r in (a.runs or ["results/runs"])]
    ctx = build_context(roots, _path(a.analysis), _path(a.systems))
    out = _path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    guide_path = _path(a.guide)
    guide = guide_path.read_text() if guide_path.is_file() else None
    if guide is None:
        print(f"note: {guide_path} not found, property guide not appended", file=sys.stderr)
    out.write_text(render(ctx, guide))
    print(f"wrote {out} ({len(ctx['meta'])} systems)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
