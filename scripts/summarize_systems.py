"""Running markdown summary of every system: run status, equilibration checks, properties.

Reads (read-only) the `sepsim progress` reports (``<runs>/<system>/<stage>/progress.json``,
plus ``run_manifest.json``), the `sepsim analyze` results
(``<analysis>/<system>/<stage>/results.json``: ``sweep`` per D49, ``pore`` if present)
and the system manifests (``<systems>/<id>/manifest.yaml``), and writes one markdown file
(default ``results/summary.md``). Nothing is recomputed: every number comes from those
files, and anything missing is shown as "—".

Layout: header and figure links, Overview, Physical validity by system, Pending, Superseded,
then "Systems": one subsection per system with a one-line description, a table of every
property obtained from it (all of its analyses, with the validity verdict and the source)
and, collapsed, the full analysis tables and checks; one abbreviation list above the first
system covers all of those tables. Symbols are written with HTML subscripts by
:func:`notation` (identifiers with underscores go into code spans).

    uv run --frozen python scripts/summarize_systems.py [--runs DIR ...] [--analysis DIR]
        [--systems DIR] [--out FILE]

``--runs`` may be given more than once (e.g. the server's ``results/runs`` plus a copy of
the other node's progress files); for the same system/stage the report with the most MD
steps done (then the newest log) wins.

Stage directories: ``prep``, ``extend``, ``cool``, ``sweep``, ``pore_relax``, ``pore``,
``diffuse`` (D53), ``tensile`` (D54), ``hole`` (D52) (a suffix such as ``sweep_d47`` or
``tensile_25C_r1e9`` is the same stage). Directories whose suffix contains
``old``, ``cancel`` or ``timeout`` are superseded: listed, never used for results.
``bench*`` and ``smoke*`` directories are ignored.
"""

from __future__ import annotations

import argparse
import inspect
import json
import math
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from sepsim.analysis.chain import MELT_C_INF_500K, msid_check
from sepsim.progress import D47_ACF, D47_MSD_RG2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validity

ROOT = Path(__file__).resolve().parents[1]
DASH = "—"

STAGES = ("prep", "extend", "cool", "sweep", "pore_relax", "pore", "diffuse", "tensile", "hole")
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


# --------------------------------------------------------------------------- notation

# Symbols written with an underscore (or run together) in labels and in the notes copied
# from results.json, and their HTML sub/superscript form; notation() rewrites them.
_SUB = (
    "χ²_red", "C_n", "R_ee", "R_n", "κ_T", "α_V", "α_L", "α_z", "D_COM", "D_real", "D_CG",
    "η_real", "η_CG", "η_Rouse", "η_R", "E_app", "τ_ee", "τ_p", "τ_1", "τ_2", "τ_3", "t_G",
    "t_50", "gap_G", "gap_50", "e_s", "k_B", "p_atm", "p_ext", "P_axis", "L_lateral",
    "L_axis", "R_eff", "R_min", "t_close", "G_e", "X_p", "ρ_N", "ρ_p", "Σ_n", "r_n",
    "σ_peak", "ε_peak", "CH_x", "E_pore", "E_bulk", "M_pore", "M_bulk",
)  # fmt: skip
NOTATION = {
    **{s: "{}<sub>{}</sub>".format(*s.split("_", 1)) for s in _SUB},
    "Rg2": "R<sub>g</sub>²",
    "Rg": "R<sub>g</sub>",
    "Cp": "C<sub>p</sub>",
    "Cv": "C<sub>v</sub>",
    "Pxx": "P<sub>xx</sub>",
    "Pyy": "P<sub>yy</sub>",
    "Pzz": "P<sub>zz</sub>",
    "Lz": "L<sub>z</sub>",
    "Tm": "T<sub>m</sub>",
    "Tg": "T<sub>g</sub>",
    "CH2": "CH<sub>2</sub>",
}
_NOTATION_RE = re.compile(
    r"(?<![A-Za-z0-9_])("
    + "|".join(re.escape(k) for k in sorted(NOTATION, key=len, reverse=True))
    + r")(?![A-Za-z0-9_])"
)
# kept verbatim: code spans, link targets, HTML tags
_PROTECTED_RE = re.compile(r"(`[^`]*`|\]\([^)]*\)|</?[A-Za-z]+>)")
_TOKEN_RE = re.compile(r"[\w./\-]+")


def _code_token(m: re.Match) -> str:
    """An identifier with an underscore left after the symbol mapping (system id, run
    directory, file name) goes into a code span so its underscores stay literal."""
    tok = m.group(0)
    core = tok.rstrip(".-")
    if "_" not in core or not core[:1].isalnum():
        return tok
    return f"`{core}`{tok[len(core) :]}"


def notation(line: str) -> str:
    """Summary notation for one markdown line: subscripted symbols (C<sub>n</sub>,
    κ<sub>T</sub>, …) and identifiers in code spans; code spans, link targets and HTML
    tags are left as they are."""
    parts = _PROTECTED_RE.split(line)
    for i in range(0, len(parts), 2):
        t = _NOTATION_RE.sub(lambda m: NOTATION[m.group(1)], parts[i])
        parts[i] = _TOKEN_RE.sub(_code_token, t)
    return "".join(parts)


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
    hole = man.get("hole") if isinstance(man.get("hole"), dict) else None
    if pore is None and "pore" in sid:
        pore = {"kind": "wide" if "pore500k" in sid else "narrow"}
    if pore:
        category = 2 if pore.get("kind") == "wide" else 3
    elif man.get("conversion") or man.get("replicate") or man.get("source"):
        category = 1
    else:
        category = 0
    return {"polymer": pol, "resolution": res, "pore": pore, "hole": hole, "category": category}


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
            f"- Inputs: runs {', '.join(f'`{r}`' for r in ctx['run_roots'])}; analysis"
            f" `{ctx['analysis_root']}`; systems `{ctx['systems_root']}`"
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
        "**Abbreviations:**",
        "",
        *(f"- **{a}**: {m}" for a, m in OVERVIEW_ABBREVIATIONS),
        "",
    ]


# Written out below the overview table
OVERVIEW_ABBREVIATIONS = (
    (
        "Res",
        (
            "resolution: CG = coarse-grained (SDK/SPICA, 3 carbons per bead), UA = united-atom"
            " (TraPPE-UA, CH_x groups as one site), AA = all-atom (OPLS, explicit hydrogens)"
        ),
    ),
    ("PE / iPP", "polyethylene / isotactic polypropylene"),
    ("Chains × length", "number of chains × backbone carbons per chain (C240 = 240 carbons)"),
    ("Sites", "interaction sites in the box: atoms (AA), united atoms (UA) or beads (CG)"),
    (
        "System id",
        (
            "`<polymer>_<res>_<kind>_n<chains>_c<carbons>_s<seed>`; amorph = bulk amorphous"
            " box; pore500k_w10nm = wide 10 nm pore made at 500 K; pore_w5nm = 5 nm dry slit pore;"
            " hole_r3nm_160C = film with a 3 nm-radius cylindrical hole at 160 °C; rep222 / rep441 ="
            " box replicated 2×2×2 / 4×4×1; from_ua = AA box converted from the relaxed UA box"
        ),
    ),
    (
        "prep / extend / cool / sweep",
        (
            "build and 500 K hold / longer 500 K hold (D47) /"
            " step-cool to 25 °C / 25–160 °C heating sweep with holds"
        ),
    ),
    ("D37, D47, …", "decision numbers in docs/decisions.md (the rule each check follows)"),
    (
        "D47 PASS",
        ("500 K melt accepted as equilibrated: end-to-end ACF < 1/e and chain COM MSD ≥ 2⟨Rg²⟩"),
    ),
    ("ACF", "autocorrelation function (here of the chain end-to-end vector)"),
    (
        "COM MSD / ⟨Rg²⟩",
        (
            "chain centre-of-mass mean-squared displacement over the mean squared"
            " radius of gyration (≥ 2: chains have moved about their own size)"
        ),
    ),
    (
        "C_n plateau (D37)",
        (
            "characteristic ratio of long sub-chains vs the PE melt value 6.7 ± 10%;"
            " informational (D47 decides acceptance)"
        ),
    ),
    ("Δ", "change between the first and second half of the hold (drift test)"),
)


def kind_label(m: dict) -> str:
    if m.get("hole"):
        h = m["hole"]
        return f"hole (R {fnum(h.get('radius_nm'), 'g')} nm, {fnum(h.get('t_c'), 'g')} °C)"
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
                    f" at {fnum(com['lag_max_ps'] / 1000, 'g')} ns"
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
                "P2 1/e time (ps)",
                "max chain COM MSD (Å²) at lag",
                "D_COM (cm²/s)",
                "trajectory analysed",
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
                "χ²_red of the α_V fit",
                "Cp classical (J g⁻¹ K⁻¹)",
                "χ²_red of the Cp fit",
                "points in the fit",
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


# Plain-word labels of the flattened results.json keys shown by pore_section()
POR_LABELS = {
    "fits.cool.dgamma_dT_mN_mK": "dγ/dT, cooling-branch fit (mN m⁻¹ K⁻¹)",
    "fits.cool.gamma_25c_mN_m": "γ at 25 °C, cooling-branch fit (mN/m)",
    "fits.sweep.dgamma_dT_mN_mK": "dγ/dT, heating-sweep fit (mN m⁻¹ K⁻¹)",
    "fits.sweep.gamma_25c_mN_m": "γ at 25 °C, heating-sweep fit (mN/m)",
    "generated_on": "analysis node",
    "pore.nominal_width_nm": "nominal gap width (nm)",
    "pore.wall_thickness_angstrom": "wall (film) thickness (Å)",
    "quantities.gamma": "γ (mN/m)",
    "t_end_ps": "segment end (ps)",
    "quantities.gap_gibbs_A": "gap between the Gibbs surfaces (Å)",
    "quantities.plateau": "film interior density (g/cm³)",
    "bulk.com_msd_at_max_A2": "bulk: max chain COM MSD (Å²)",
    "bulk.density": "bulk ρ (g/cm³)",
    "bulk.msd_at_max_A2": "bulk: max segment MSD (Å²)",
    "film.c_n.bond_length": "film: C_n bond length (Å)",
    "film.c_n.plateau": "film: C_n",
    "film.com_msd.lag_max_ps": "film: max lag (ps)",
    "film.com_msd.msd_at_max_A2": "film: max chain COM MSD (Å²)",
    "film.com_msd.msd_rg2_end": "film: chain COM MSD / ⟨Rg²⟩ at max lag",
    "film.com_msd.slope_end": "film: COM MSD log-slope at max lag",
    "film.com_msd.slope_max": "film: largest COM MSD log-slope",
    "film.crystallinity.largest_cluster": "film: largest ordered cluster, mean (sites)",
    "film.hold_ns": "film: hold length (ns)",
    "drift.gamma.delta": "γ drift: second − first half (mN/m)",
    "drift.gamma.first": "γ, first half (mN/m)",
    "drift.gamma.second": "γ, second half (mN/m)",
    "drift.gamma.sem": "SEM of the γ drift (mN/m)",
    "drift.pe.delta": "potential-energy drift: second − first half",
    "stats.density": "box density (g/cm³)",
    "stats.gamma": "γ (mN/m)",
    "stats.t_c": "T (°C)",
    "t_set_c": "set T (°C)",
    "t_c": "T (°C)",
}
POR_TABLES = {
    "convergence": "Convergence of the film quantities, per segment",
    "holds": "Per hold: film vs bulk",
    "segments": "Per segment",
}


def pore_label(key: str) -> str:
    """Plain-word column label of a flattened key; unknown keys verbatim (code span)."""
    if key in POR_LABELS:
        return POR_LABELS[key]
    m = re.fullmatch(r"convergence\.gamma\.block_sem\.(\d+)", key)
    if m:
        return f"SEM of γ from {m.group(1)} blocks (mN/m)"
    return f"`{key}`"


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
        out.append(f"- {pore_label(k)}: {v}")
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
        out.append(f"{POR_TABLES.get(name, f'`{name}`')}:")
        out.append("")
        out += table([pore_label(c) for c in cols], [[r.get(c, DASH) for c in cols] for r in recs])
        out.append("")
    for n in list(res.get("caveats") or []) + list(res.get("notes") or []):
        out.append(f"- Note: {n}")
    if len(out) == 2:
        out.append("- (no recognised key numbers in results.json)")
    out.append("")
    return out


def system_details(sid: str, ctx: dict) -> list[str]:
    """Provenance, equilibration checks and run list of one system."""
    eq = ctx["eq"][sid]
    out = ["**Provenance**", "", *provenance(sid, ctx), ""]
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
    if m.get("hole"):
        return ["hole"]
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


def pending_items(sid: str, ctx: dict) -> list[str]:
    """Open stages, missing analyses and equilibration problems of one system."""
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
    return items


def pending(ctx: dict, order: list[str]) -> list[str]:
    lines = []
    for sid in order:
        if is_superseded(sid, ctx):
            continue
        items = pending_items(sid, ctx)
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


PORE_HEADER = [
    "Kind",
    "Gap (nominal)",
    "Gap at 500 K",
    "Wall thickness",
    "Lateral box",
    "γ per hold (mN/m, monitor)",
    "Status",
    "Analysis",
]
PORE_GAMMA_NOTE = (
    "γ here is the `sepsim progress` second-half mean ± SEM of each hold segment"
    " (γ = (Lz/2)[Pzz − (Pxx+Pyy)/2])."
)


def pore_row(sid: str, ctx: dict) -> list[str]:
    """Geometry, monitor γ and status of a pore or hole system (PORE_HEADER columns)."""
    pr = ctx["meta"][sid]["pore"]
    wall = pr.get("wall_thickness_angstrom")
    runs = current_runs(ctx["runs"].get(sid, {}))
    run = latest(runs, "pore") or latest(runs, "pore_relax")
    gam = pore_gamma_rows(run.get("progress") or {}) if run else []
    stage, status = stage_now(sid, ctx)
    return [
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


# --------------------------------------------------------------------------- systems

T_COLS = (25.0, 90.0, 130.0, 160.0)
PROPS_HEADER = [
    "Property",
    *(f"{fnum(t, 'g')} °C" for t in T_COLS),
    "Other (500 K, fits)",
    "Validity",
    "Source",
]
# Row order of the per-system properties tables (row key = (base, variant); variant 0 =
# sweep / pore holds, 1 = long diffuse holds, a strain rate for tensile rows)
ROW_ORDER = (
    "d47",
    "rho",
    "kappa",
    "alpha",
    "cp",
    "cn500",
    "rg",
    "ree",
    "cn",
    "p2",
    "p2_surface",
    "p2_interior",
    "segmsd",
    "commsd",
    "msdrg",
    "dcom",
    "eta",
    "tauee",
    "tau1",
    "cryst",
    "gamma_mon",
    "gamma",
    "dgdt",
    "g25",
    "es",
    "film_h",
    "gap",
    "plateau",
    "iface",
    "closest",
    "alpha_film",
    "alpha_z",
    "cv_film",
    "E",
    "nu_fit",
    "nu_run",
    "peak",
    "peak_strain",
    "flow",
)
LONG = ", long hold (D53)"


def _t_col(t) -> float | None:
    if t is None:
        return None
    return next((c for c in T_COLS if abs(float(t) - c) < 0.5), None)


def _put(rows: dict, key: tuple, label: str, vkey: str | None, t, value: str, src: str, other=""):
    """Add one value to a properties-table row; a T outside T_COLS (or None) goes to the
    'other' column, prefixed by ``other``. A second value in the same cell is appended."""
    if value in (None, "", DASH):
        return
    r = rows.setdefault(key, {"label": label, "vkey": vkey, "cells": {}, "other": [], "src": []})
    col = _t_col(t)
    if col is None:
        r["other"].append(f"{other}: {value}" if other else value)
    else:
        r["cells"][col] = f"{r['cells'][col]}; {value}" if col in r["cells"] else value
    if src not in r["src"]:
        r["src"].append(src)


def _dcom(com: dict) -> str:
    if com.get("D_cm2_s") is not None:
        return f"{fnum(com['D_cm2_s'], '.3g')} ± {fnum(com.get('D_err_cm2_s'), '.2g')}"
    if com:
        return f"not diffusive (slope {fnum(com.get('slope_end'), '.2f')})"
    return DASH


def _relax(r) -> str:
    """1/e time in ns, or 'not reached' with the extrapolated fit."""
    if not isinstance(r, dict) or not r:
        return DASH
    if r.get("t_1e_ps") is not None:
        return fnum(r["t_1e_ps"] / 1000, ".3g")
    if r.get("tau_fit_ps") is not None:
        return f"not reached (extrap. {fnum(r['tau_fit_ps'] / 1000, '.3g')})"
    return "not reached"


def hold_quantities(t: dict, kappa: dict | None = None, density=None) -> list[tuple]:
    """(base key, label, validity key, value) of one hold: thermo, chain size, dynamics."""
    com = t.get("com_msd") or {}
    rouse = get(t, "relaxation", "rouse") or []
    r1 = next((x for x in rouse if isinstance(x, dict) and x.get("p") == 1), None)
    msd = DASH
    if com.get("msd_at_max_A2") is not None:
        msd = fnum(com["msd_at_max_A2"], ".4g")
        if com.get("lag_max_ps") is not None:
            msd += f" at {fnum(com['lag_max_ps'] / 1000, 'g')} ns"
    kap = {"mean": get(kappa, "kappa_T_GPa"), "sem": get(kappa, "sem")}
    return [
        ("rho", "ρ (g/cm³)", "rho", fpm(density, ".5f")),
        ("kappa", "κ_T (GPa⁻¹)", "kappa", fpm(kap, ".3f")),
        ("rg", "Rg (Å)", "chainT", fpm(get(t, "rg", "rg_A"), ".2f")),
        ("ree", "R_ee (Å)", "chainT", fpm(get(t, "ree", "ree_A"), ".1f")),
        ("cn", "C_n", "chainT", fpm(get(t, "c_n", "plateau"), ".2f")),
        ("p2", "P2 1/e time (ps)", "segdyn", fnum(get(t, "p2", "t_1e_ps"), ".3g")),
        (
            "segmsd",
            "segment MSD at 1 ns lag (Å²)",
            "segdyn",
            fnum(get(t, "segment_msd", "msd_1000ps_A2"), ".4g"),
        ),
        ("commsd", "max chain COM MSD (Å²) at lag", "chaindyn", msd),
        (
            "msdrg",
            "chain COM MSD / ⟨Rg²⟩ at the longest lag",
            "chaindyn",
            fnum(com.get("msd_rg2_end"), ".2f"),
        ),
        ("dcom", "D_COM (cm²/s)", "chaindyn", _dcom(com)),
        (
            "tauee",
            "τ_ee, end-to-end vector 1/e time (ns)",
            "chaindyn",
            _relax(get(t, "relaxation", "ree")),
        ),
        ("tau1", "τ_1, slowest Rouse mode 1/e time (ns)", "chaindyn", _relax(r1)),
        (
            "cryst",
            "ordered-site fraction (crystallinity monitor, uncalibrated)",
            None,
            fnum(get(t, "crystallinity", "fraction", "mean"), ".3f"),
        ),
    ]


MELT_HOLD = ", 500 K hold"


def _put_hold(rows, t, kappa, density, t_c, src, long=False, other="", melt=False):
    """The hold quantities as rows; a long hold (D53) gets its own rows, and so does the
    chain size of the 500 K melt hold (validity: chain size at 500 K)."""
    for base, label, vkey, val in hold_quantities(t or {}, kappa, density):
        key, lab = (base, 1 if long else 0), label + (LONG if long else "")
        if melt and base in ("rg", "ree", "cn"):
            key, lab, vkey = (base, 2), label + MELT_HOLD, "chain500"
        _put(rows, key, lab, vkey, t_c, val, src, other)


def _fit_text(window, value: str, chi2) -> str:
    w = "–".join(fnum(x, ".4g") for x in window or ()) or DASH
    return f"{w} °C: {value}" + (f" (χ²_red {fnum(chi2, '.3g')})" if chi2 is not None else "")


def _sweep_rows(rows: dict, stage: str, res: dict) -> None:
    src = f"`{stage}`"
    segs = {s.get("index"): s for s in res.get("segments") or [] if isinstance(s, dict)}
    for h in res.get("holds") or []:
        seg = segs.get(h.get("index")) or {}
        _put_hold(
            rows, h.get("traj"), h.get("kappa"), get(seg, "stats", "density"), h.get("t_c"), src
        )
    fits = res.get("fits") or {}
    for f in fits.get("alpha_V") or []:
        if f.get("alpha_V_per_K") is not None:
            v = f"{fnum(f['alpha_V_per_K'] * 1e4, '.3f')} ± {fnum((f.get('err') or 0) * 1e4, '.3f')}"
            _put(rows, ("alpha", 0), "α_V (10⁻⁴ K⁻¹)", "alpha", None,
                 _fit_text(f.get("window_c"), v, f.get("chi2_red")), src)  # fmt: skip
    for f in fits.get("cp") or []:
        if f.get("cp_J_gK") is not None:
            v = f"{fnum(f['cp_J_gK'], '.3f')} ± {fnum(f.get('err'), '.3f')}"
            _put(rows, ("cp", 0), "Cp, classical (J g⁻¹ K⁻¹)", "cp", None,
                 _fit_text(f.get("window_c"), v, f.get("chi2_red")), src)  # fmt: skip


def _hold_rows(rows: dict, stage: str, res: dict, long: bool) -> None:
    """A single-hold analysis (`sepsim analyze hold`: extend at 500 K, diffuse at one T)."""
    t_c = res.get("t_c")
    t_k = res.get("t_k")
    other = f"{fnum(t_k, 'g')} K" if t_k is not None else f"{fnum(t_c, 'g')} °C"
    _put_hold(rows, res.get("traj"), res.get("kappa"), get(res, "stats", "density"), t_c,
              f"`{stage}`", long=long, other=other, melt=not long)  # fmt: skip


def _rate_label(rate) -> str:
    try:
        e = round(math.log10(float(rate)))
    except (TypeError, ValueError):
        return DASH
    if abs(float(rate) - 10**e) > 1e-6 * 10**e:
        return f"{fnum(rate, '.2g')} s⁻¹"
    sup = str(e).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))
    return f"10{sup} s⁻¹"


TENSILE_ROWS = (
    ("E", "E_app (MPa)", "E_MPa", ".3g"),
    ("nu_fit", "ν, fit up to the E_app strain", "nu_fit", ".2f"),
    ("nu_run", "ν, whole run", "nu_run", ".2f"),
    ("peak", "σ_peak (MPa)", "peak_MPa", ".2g"),
    ("peak_strain", "ε_peak", "peak_strain", ".3f"),
    ("flow", "flow σ (MPa)", "flow_MPa", ".2g"),
)


def _tensile_rows(rows: dict, stage: str, res: dict) -> None:
    for run in res.get("runs") or []:
        rate = run.get("rate_per_s")
        summ = run.get("summary") or {}
        for base, label, k, spec in TENSILE_ROWS:
            d = summ.get(k) or {}
            if d.get("mean") is None:
                continue
            v = f"{fnum(d['mean'], spec)} ± {fnum(d.get('sd'), spec)}"
            lab = f"{label}, {_rate_label(rate)}, mean ± SD"
            _put(rows, (base, rate or 0), lab, "tensile", run.get("t_c"), v, f"`{stage}`")


def _pore_rows(rows: dict, stage: str, res: dict) -> None:
    src = f"`{stage}`"
    for h in res.get("holds") or []:
        t_c = h.get("t_c")
        _put_hold(rows, validity.hold_traj(h), None, None, t_c, src)
        prof = get(h, "traj", "profile") or {}
        film = prof.get("film_gibbs_frames") or (
            {"mean": prof["film_gibbs_A"]} if prof.get("film_gibbs_A") is not None else None
        )
        widths = [get(prof, "interface_10_90", s, "width") for s in ("lower", "upper")]
        widths = [w for w in widths if w is not None]
        for base, label, val in (
            ("film_h", "film thickness between the Gibbs surfaces (Å)", fpm(film, ".2f")),
            ("gap", "gap between the Gibbs surfaces (Å)", fnum(prof.get("gap_gibbs_A"), ".2f")),
            ("plateau", "film interior density (g/cm³)", fpm(prof.get("plateau"), ".4f")),
            (
                "iface",
                "interfacial width, 10–90 % (Å)",
                fnum(sum(widths) / len(widths), ".2f") if widths else DASH,
            ),
            ("closest", "closest approach across the gap (Å)", fnum(get(prof, "closest_A", "mean"), ".1f")),
        ):  # fmt: skip
            _put(rows, (base, 0), label, "film", t_c, val, src)
        lay = get(h, "traj", "layers") or {}
        for part in ("surface", "interior"):
            _put(rows, (f"p2_{part}", 0), f"P2 1/e time, {part} layer (ps)", "segdyn", t_c,
                 fnum(get(lay, part, "p2_t_1e_ps"), ".3g"), src)  # fmt: skip
    th = res.get("thermal") or {}
    for pt in th.get("points") or []:
        if pt.get("kind") != "hold":
            continue
        _put(
            rows,
            ("gamma", 0),
            "γ, analysis (mN/m)",
            "gamma",
            pt.get("t_c"),
            fpm(pt.get("gamma"), ".1f"),
            src,
        )
        _put(rows, ("es", 0), "e_s, surface excess energy (mJ/m²)", None, pt.get("t_c"),
             fpm(pt.get("e_s_mJ_m2"), ".1f"), src)  # fmt: skip
    names = {"sweep": "heating sweep", "cool": "cooling branch"}
    for branch, f in (res.get("fits") or {}).items():
        if not isinstance(f, dict) or f.get("dgamma_dT_mN_mK") is None:
            continue
        name = names.get(branch, branch)
        v = f"{fnum(f['dgamma_dT_mN_mK'], '.4f')} ± {fnum(f.get('err'), '.4f')}"
        _put(rows, ("dgdt", 0), "dγ/dT (mN m⁻¹ K⁻¹)", "gamma", None,
             f"{name} " + _fit_text(f.get("window_c"), v, f.get("chi2_red")), src)  # fmt: skip
        _put(rows, ("g25", 0), "γ at 25 °C from the dγ/dT fit (mN/m)", "gamma", None,
             f"{name}: {fnum(f.get('gamma_25c_mN_m'), '.2f')}", src)  # fmt: skip
    for f in th.get("alpha") or []:
        if f.get("alpha_V_film_per_K") is not None:
            _put(rows, ("alpha_film", 0), "film α_V (10⁻⁴ K⁻¹)", None, None,
                 _fit_text(f.get("window_c"), fnum(f["alpha_V_film_per_K"] * 1e4, ".3f"), None), src)  # fmt: skip
        if f.get("alpha_z_per_K") is not None:
            v = f"{fnum(f['alpha_z_per_K'] * 1e4, '.3f')} ± {fnum((f.get('alpha_z_err') or 0) * 1e4, '.3f')}"
            _put(rows, ("alpha_z", 0), "α_z, film-thickness expansion (10⁻⁴ K⁻¹)", None, None,
                 _fit_text(f.get("window_c"), v, f.get("chi2_red")), src)  # fmt: skip
    for f in th.get("cv") or []:
        if f.get("cv_J_gK") is not None:
            v = f"{fnum(f['cv_J_gK'], '.3f')} ± {fnum(f.get('err'), '.3f')}"
            _put(rows, ("cv_film", 0), "Cv of the film, classical (J g⁻¹ K⁻¹)", None, None,
                 _fit_text(f.get("window_c"), v, f.get("chi2_red")), src)  # fmt: skip


def property_rows(sid: str, ctx: dict) -> tuple[dict, bool]:
    """{row key: row} of every property obtained from one system, and whether any of
    them is the system's own (not only the equilibration inherited from its source)."""
    rows: dict = {}
    eq = ctx["eq"][sid]
    ch = eq.get("checks") or {}
    inherited = eq.get("basis") == "inherited"
    if eq.get("basis"):
        src = f"`{ch.get('stage', DASH)}` progress"
        if inherited:
            src += f" of `{(eq.get('via') or [DASH])[-1]}`"
        _put(rows, ("d47", 0), "500 K equilibration (D47)", None, None, eq["text"], src)
        if ch.get("plateau") is not None:
            ref = ch.get("reference") or MELT_C_INF_500K.get(ctx["meta"][sid]["polymer"] or "")
            v = fnum(ch["plateau"], ".2f") + (f" (melt {fnum(ref[0], 'g')})" if ref else "")
            _put(
                rows, ("cn500", 0), "C_n plateau, 500 K (D37)", "chain500", None, f"500 K: {v}", src
            )
    n_inherited = len(rows) if inherited else 0
    for stage, res in sorted(ctx["analysis"].get(sid, {}).items()):
        kind, _ = classify_stage(stage)
        if _is_sweep(stage, res):
            _sweep_rows(rows, stage, res)
        elif kind == "extend":
            _hold_rows(rows, stage, res, long=False)
        elif kind == "diffuse":
            _hold_rows(rows, stage, res, long=True)
        elif kind == "tensile":
            _tensile_rows(rows, stage, res)
        elif kind == "pore" or "thermal" in res:
            _pore_rows(rows, stage, res)
    runs = current_runs(ctx["runs"].get(sid, {}))
    for r in runs:
        if r["kind"] == "diffuse":
            eta = get(r, "progress", "hold", "d_com", "eta_rouse_pa_s")
            t_c = get(r, "progress", "hold", "t_c")
            _put(rows, ("eta", 1), "η_Rouse, Rouse viscosity estimate (Pa·s)" + LONG, "chaindyn",
                 t_c, fnum(eta, ".2g"), f"`{r['dir']}` progress")  # fmt: skip
    run = latest(runs, "pore") or latest(runs, "pore_relax")
    for t, g in pore_gamma_rows(run.get("progress") or {}) if run else []:
        _put(
            rows,
            ("gamma_mon", 0),
            "γ, run monitor (mN/m)",
            "gamma",
            t,
            g,
            f"`{run['dir']}` progress",
        )
    return rows, len(rows) > n_inherited


def _row_sort(key: tuple) -> tuple:
    base, variant = key
    return (ROW_ORDER.index(base) if base in ROW_ORDER else len(ROW_ORDER), variant)


def properties_table(sid: str, ctx: dict, rows: dict) -> list[str]:
    v = validity.system_validity(sid, ctx)
    out = []
    for key in sorted(rows, key=_row_sort):
        r = rows[key]
        out.append(
            [
                r["label"],
                *(r["cells"].get(t, DASH) for t in T_COLS),
                "; ".join(r["other"]) or DASH,
                validity.short(v[r["vkey"]]) if r["vkey"] in v else DASH,
                ", ".join(r["src"]),
            ]
        )
    return table(PROPS_HEADER, out)


def kind_text(sid: str, ctx: dict) -> str:
    """'bulk amorphous box' / '5 nm dry slit pore' / 'film with a … hole at …'."""
    m = ctx["meta"][sid]
    man = ctx["systems"].get(sid) or {}
    if m.get("hole"):
        h = m["hole"]
        return (
            f"film with a {fnum(h.get('radius_nm'), 'g')} nm-radius cylindrical hole at"
            f" {fnum(h.get('t_c'), 'g')} °C"
        )
    if m["pore"]:
        w = fnum(m["pore"].get("nominal_width_nm"), "g")
        if m["pore"].get("kind") == "wide":
            return f"wide {w} nm slit pore made at 500 K"
        return f"{w} nm dry slit pore"
    out = "bulk amorphous box"
    if man.get("replicate"):
        f = "×".join(str(x) for x in get(man, "replicate", "factors", default=[])) or DASH
        out += f", replicated {f}"
    if man.get("conversion"):
        out += ", converted from the relaxed UA box (ua2aa)"
    return out


SITE_NAME = {"cg": "beads", "ua": "united atoms", "aa": "atoms"}


def system_blurb(sid: str, ctx: dict) -> str:
    """One line: polymer, resolution, kind, size, provenance and current status."""
    m = ctx["meta"][sid]
    man = ctx["systems"].get(sid) or {}
    n_at = get(man, "counts", "total", "atoms")
    sites = f", {n_at:,} {SITE_NAME.get(m['resolution'], 'sites')}" if n_at is not None else ""
    src = source_info(man)
    if src:
        built = f"built from `{src[0].get('id', DASH)}` (`{short_data(src[0].get('id'), src[0].get('data_file'))}`)"
    elif man.get("growth"):
        built = f"grown chains (seed {man.get('seed', DASH)})"
    else:
        built = "provenance not recorded" if man else "no manifest"
    stage, status = stage_now(sid, ctx)
    now = f"Status: {status}" if stage == "done" else f"Stage now: {stage} ({status})"
    head = (
        f"{POLYMER_NAME.get(m['polymer'], m['polymer'] or DASH)}"
        f" {(m['resolution'] or DASH).upper()}, {kind_text(sid, ctx)},"
        f" {man.get('n_chains', DASH)} chains × C{man.get('n_carbons', DASH)}{sites}; {built}."
    )
    if is_superseded(sid, ctx):
        why = ctx["superseded_by"].get(sid)
        head += f" **Superseded** {f'by {why}' if why else 'as ' + ctx['stale'][sid]}; not used."
    return f"{head} {now}."


def analysis_details(sid: str, stage: str, res: dict, ctx: dict) -> list[str]:
    """The full tables and notes of one analysis of a system."""
    kind, _ = classify_stage(stage)
    stale = ctx["stale_analysis"].get((sid, stage))
    mark = f" **{stale}**" if stale else ""
    if _is_sweep(stage, res):
        m = ctx["meta"][sid]
        man = ctx["systems"].get(sid) or {}
        hold = get(ctx["eq"][sid], "checks", "hold_ns")
        desc = (
            f"{(m['resolution'] or DASH).upper()} {POLYMER_NAME.get(m['polymer'], DASH)}"
            f" C{man.get('n_carbons', DASH)}, {fnum(hold, '.1f')} ns at 500 K"
        )
        return [f"**`{stage}` analysis** ({desc}){mark}", "", *sweep_section(res)]
    if kind in ("extend", "diffuse"):
        return [f"**`{stage}` analysis**{mark}", "", *hold_section(res)]
    if kind == "tensile":
        return [f"**`{stage}` analysis**{mark}", "", *tensile_section(res)]
    return [f"**`{stage}` analysis**{mark}", "", *pore_section(res)]


def hold_section(res: dict) -> list[str]:
    """Run facts and notes of a single-hold analysis (the numbers are in the table)."""
    out = [
        (
            f"`sepsim analyze hold`, generated {utc(res.get('generated'))} on"
            f" {res.get('generated_on', DASH)}, run {res.get('run_status', DASH)};"
            f" segment {res.get('segment', DASH)}; {fnum(get(res, 'traj', 'hold_ns'), 'g')} ns"
            f" analysed of {fnum(res.get('planned_ns'), 'g')} ns planned"
            f" ({'complete' if res.get('complete') else 'not complete'})."
        ),
        "",
    ]
    notes = list(res.get("caveats") or []) + list(res.get("notes") or [])
    notes += list(get(res, "traj", "notes") or [])
    out += [f"- Note: {n}" for n in notes]
    return out + ([""] if notes else [])


def tensile_section(res: dict) -> list[str]:
    """Per-axis table of each tensile run, and the caveats."""
    out = [
        (
            f"`sepsim analyze tensile`, generated {utc(res.get('generated'))}; E_app and ν fitted"
            f" up to strain {fnum(res.get('fit_max'), 'g')}, flow σ = mean true stress over"
            f" strain {'–'.join(fnum(x, 'g') for x in res.get('flow_window') or ()) or DASH}."
        ),
        "",
    ]
    for run in res.get("runs") or []:
        out += [
            (
                f"{fnum(run.get('t_c'), 'g')} °C, {_rate_label(run.get('rate_per_s'))} to strain"
                f" {fnum(run.get('strain_max'), 'g')}, run {run.get('status', DASH)}"
                f" on {run.get('node', DASH)}:"
            ),
            "",
        ]
        rows = [
            [
                a.get("axis", DASH),
                fnum(a.get("strain_max"), ".3f"),
                f"{fnum(a.get('E_MPa'), '.3g')} ± {fnum(a.get('E_err_MPa'), '.2g')}",
                fnum(a.get("nu_fit"), ".2f"),
                fnum(a.get("nu_run"), ".2f"),
                fnum(a.get("peak_MPa"), ".2g"),
                fnum(a.get("peak_strain"), ".3f"),
                fnum(a.get("flow_MPa"), ".2g"),
                fnum(a.get("temp_mean_K"), ".1f"),
            ]
            for a in run.get("axes") or []
        ]
        out += table(
            [
                "pull axis",
                "strain reached",
                "E_app (MPa)",
                "ν, fit",
                "ν, whole run",
                "σ_peak (MPa)",
                "ε_peak",
                "flow σ (MPa)",
                "T (K)",
            ],
            rows,
        )
        out.append("")
    notes = list(res.get("caveats") or []) + [
        n for run in res.get("runs") or [] for n in run.get("notes") or []
    ]
    out += [f"- Note: {n}" for n in notes]
    return out + ([""] if notes else [])


def system_section(sid: str, ctx: dict) -> tuple[list[str], list[str]]:
    """### `<id>`: description, properties table, collapsible full tables and checks;
    returns (lines, properties table lines)."""
    m = ctx["meta"][sid]
    title = f"### `{sid}`" + (" (superseded)" if is_superseded(sid, ctx) else "")
    rows, own = property_rows(sid, ctx)
    out = [title, "", system_blurb(sid, ctx), ""]
    props = properties_table(sid, ctx, rows) if own else []
    if own:
        out += [*props, ""]
    else:
        items = [] if is_superseded(sid, ctx) else pending_items(sid, ctx)
        out += [
            (
                "No analysed properties yet"
                + (f"; pending: {'; '.join(items)}" if items else "")
                + f". Equilibration: {ctx['eq'][sid]['text']}."
            ),
            "",
        ]
    out += ["<details><summary>Full analysis tables and checks</summary>", ""]
    out += system_details(sid, ctx)
    if m["pore"]:
        out += [*table(PORE_HEADER, [pore_row(sid, ctx)]), "", PORE_GAMMA_NOTE, ""]
    ana = ctx["analysis"].get(sid, {})
    for stage, res in sorted(ana.items()):
        out += analysis_details(sid, stage, res, ctx)
    if (
        not m["pore"]
        and not is_superseded(sid, ctx)
        and not any(_is_sweep(k, v) for k, v in ana.items())
    ):
        out += ["- Sweep analysis: not analysed yet.", ""]
    out += ["</details>", ""]
    return out, props


# Definitions of every symbol and term in the per-system properties tables:
# (group, ((symbol, meaning, pattern to look for in the tables or None = always), ...))
PROPERTY_ABBREVIATIONS = (
    (
        "Table",
        (
            (
                "25 / 90 / 130 / 160 °C",
                "hold temperature (heating sweep, pore holds, long holds, tensile)",
                None,
            ),
            (
                "Other (500 K, fits)",
                "values not tied to those temperatures: the 500 K melt, fit windows (°C), rates",
                None,
            ),
            (
                "Validity",
                "this system's verdict for the property in the validity table above (codes below)",
                None,
            ),
            (
                "Source",
                "the analysis (`results/analysis/<system>/<stage>/results.json`) or run monitor the value comes from",
                None,
            ),
            (
                "mean ± SEM",
                "mean and standard error of the mean (block averages / statistical inefficiency), unless marked SD",
                None,
            ),
            ("SD", "standard deviation (tensile: over the x, y and z pulls of one run)", r"\bSD\b"),
            (
                "χ²_red",
                "reduced χ² of the SEM-weighted linear fit (> 1: curvature or SEMs too small; errors scaled by √χ²_red)",
                "χ²_red",
            ),
            (
                "progress",
                "the run monitor (`sepsim progress`, progress.json) rather than an analysis",
                "progress",
            ),
            (
                "long hold (D53)",
                "dedicated long NPT hold at one sweep temperature (`diffuse` run)",
                "long hold",
            ),
            (
                "not reached / extrap.",
                "the ACF stays above 1/e within the lags; extrap. = exponential fit of the early decay (order of magnitude only)",
                "extrap.",
            ),
            (
                "not diffusive (slope s)",
                "chain COM MSD log-slope below 0.9 at the longest lag, so no D_COM; s = that slope",
                "not diffusive",
            ),
        ),
    ),
    (
        "Equilibration and thermodynamics",
        (
            (
                "D47",
                "500 K chain-mixing criterion: end-to-end ACF < 1/e and chain COM MSD ≥ 2⟨Rg²⟩ at half the hold",
                "D47",
            ),
            ("ACF", "autocorrelation function (here of the chain end-to-end vector)", "ACF"),
            ("500 K", "the equilibrated melt hold (prep/extend) before cooling", "500 K"),
            ("ρ", "mass density (g/cm³)", "ρ"),
            ("κ_T", "isothermal compressibility from the volume fluctuations (GPa⁻¹)", "κ_T"),
            ("α_V", "volumetric thermal expansion coefficient (1/V) dV/dT (10⁻⁴ K⁻¹)", "α_V"),
            ("α_z", "linear expansion coefficient of the film thickness (10⁻⁴ K⁻¹)", "α_z"),
            ("Cp", "isobaric specific heat dH/dT, classical (J g⁻¹ K⁻¹)", r"\bCp\b"),
            ("Cv", "specific heat at constant volume dE/dT, classical (J g⁻¹ K⁻¹)", r"\bCv\b"),
        ),
    ),
    (
        "Chain size and dynamics",
        (
            ("Rg", "radius of gyration of a chain (Å)", r"\bRg"),
            ("R_ee", "chain end-to-end distance (Å)", "R_ee"),
            (
                "C_n",
                "characteristic ratio ⟨R_n²⟩/(n l²) for n ≥ 100 backbone carbons (D37); melt C∞ ≈ 6.7 (PE), 6.15 (iPP)",
                "C_n",
            ),
            (
                "P2",
                "backbone bond orientation autocorrelation (second Legendre polynomial); 1/e time = local reorientation time",
                r"\bP2\b",
            ),
            ("MSD", "mean-squared displacement (Å²)", "MSD"),
            ("COM", "chain centre of mass", "COM"),
            ("segment MSD", "MSD of the backbone sites (segmental mobility)", "segment MSD"),
            (
                "D_COM",
                "chain centre-of-mass self-diffusion coefficient (cm²/s), only when the MSD is diffusive",
                "D_COM",
            ),
            (
                "η_Rouse",
                "Rouse melt viscosity ρ_N k_B T ⟨R_ee²⟩/(36 D_COM) (Pa·s); a lower bound for entangled chains",
                "η_Rouse",
            ),
            (
                "τ_ee",
                "1/e time of the end-to-end vector ACF: the longest single-chain relaxation time (ns)",
                "τ_ee",
            ),
            ("τ_1", "1/e time of the slowest (p = 1) Rouse mode ACF (ns)", "τ_1"),
            (
                "ordered-site fraction",
                "D26 local-alignment order (p2 ≥ 0.4), uncalibrated melt baseline, not a crystallinity",
                "ordered-site",
            ),
        ),
    ),
    (
        "Surfaces and films (pores)",
        (
            ("γ", "surface tension per film surface (Lz/2)[Pzz − (Pxx+Pyy)/2] (mN/m)", "γ"),
            ("dγ/dT", "temperature slope of γ from a linear fit (mN m⁻¹ K⁻¹)", "dγ/dT"),
            ("e_s", "surface excess energy per unit area (mJ/m²), classical", "e_s"),
            (
                "Gibbs surfaces",
                "dividing surfaces of the film density profile; thickness and gap are measured between them",
                "Gibbs",
            ),
            (
                "interfacial width, 10–90 %",
                "distance over which the density rises from 10% to 90% of the interior value",
                "interfacial width",
            ),
            (
                "surface / interior layer",
                "sites within 15 Å of a Gibbs surface / the rest of the film",
                "layer",
            ),
        ),
    ),
    (
        "Mechanics (tensile)",
        (
            (
                "E_app",
                "apparent (high-frequency, rate-dependent) tensile modulus up to strain 0.02 (MPa)",
                "E_app",
            ),
            ("ν", "Poisson ratio −d ln L_lateral / d ln L_axis", "ν"),
            (
                "σ_peak, ε_peak",
                "maximum of the smoothed true stress (MPa) and its strain",
                "σ_peak",
            ),
            ("flow σ", "mean true stress over strains 0.3–0.5 (MPa)", "flow σ"),
            ("s⁻¹", "engineering strain rate of the pull", "s⁻¹"),
        ),
    ),
    (
        "Analyses (Source)",
        (
            ("`sweep`", "25–160 °C heating-sweep analysis (`sepsim analyze sweep`)", "`sweep"),
            ("`extend`", "500 K extension hold (D47; analysis: `sepsim analyze hold`)", "`extend"),
            ("`diffuse_<T>`", "long NPT hold at T (D53, `sepsim analyze hold`)", "`diffuse"),
            (
                "`tensile_<T>[_r1e9]`",
                "tensile runs at T (D54, `sepsim analyze tensile`; `_r1e9` = 10⁹ s⁻¹)",
                "`tensile",
            ),
            ("`pore`", "slit-pore analysis (D51, `sepsim analyze pore`)", "`pore`"),
            ("`prep`", "build and first 500 K hold", "`prep"),
        ),
    ),
)


def systems_abbreviations(text: str, codes: set[str]) -> list[str]:
    """Grouped definitions of the symbols used in the properties tables (``text``) and
    of the validity codes used (``codes``)."""
    out = ["**Abbreviations (all property tables below):**", ""]
    for group, entries in PROPERTY_ABBREVIATIONS:
        used = [(s, m) for s, m, pat in entries if pat is None or re.search(pat, text)]
        if used:
            out.append(f"- {group}")
            out += [f"  - **{s}**: {m}" for s, m in used]
    vc = [
        (validity.SHORT[k], validity.MEANING[k])
        for k in validity.VERDICTS
        if validity.SHORT[k] in codes
    ]
    if any(c.endswith(validity.FLAG_MARK) for c in codes):
        vc.append((validity.FLAG_MARK, "flagged: the system's 500 K equilibration is not accepted"))
    if vc:
        out.append("- Validity codes")
        out += [f"  - **{s}**: {m}" for s, m in vc]
    return out + [""]


def systems(ctx: dict, order: list[str]) -> list[str]:
    """## Systems: one subsection per system (current first, superseded last)."""
    cur = [s for s in order if not is_superseded(s, ctx)]
    sids = cur + [s for s in order if is_superseded(s, ctx)]
    secs = [system_section(s, ctx) for s in sids]
    tables = [ln for _, props in secs for ln in props[2:]]
    codes = set()
    for ln in tables:
        v = ln.strip().strip("|").split(" | ")[-2].strip()
        codes |= {v, v.removesuffix(validity.FLAG_MARK)}
    out = [
        "## Systems",
        "",
        (
            "One subsection per system, in the overview order (superseded systems last). Each"
            " has a one-line description, a table of every property obtained from the system"
            " (all of its analyses: sweep, 500 K extension, long diffuse holds, tensile runs,"
            " pore) and, collapsed, the full analysis tables and checks."
        ),
        "",
        *systems_abbreviations("\n".join(tables), codes),
    ]
    for sec, _ in secs:
        out += sec
    return out


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


def current_systems(ctx: dict, order: list[str]) -> list[str]:
    """Non-superseded systems with something to show (runs or an inherited verdict),
    in ``order``: the rows of the convergence and validity overviews."""
    return [
        s
        for s in order
        if not is_superseded(s, ctx) and (ctx["runs"].get(s) or ctx["eq"][s].get("checks"))
    ]


def convergence_links(base: Path | None, order: list[str]) -> list[str]:
    """'Convergence figures' line linking the files of scripts/convergence_dashboard.py
    (relative to ``base``, the summary's directory) that exist; none -> no line."""
    if base is None:
        return []
    links = []
    if (base / "convergence_overview.png").is_file():
        links.append("[overview](convergence_overview.png)")
    if (base / "validity_overview.png").is_file():
        links.append("[physical validity](validity_overview.png)")
    links += [
        f"[`{s}`](convergence/{s}.png)"
        for s in order
        if (base / "convergence" / f"{s}.png").is_file()
    ]
    return [f"**Convergence figures:** {', '.join(links)}", ""] if links else []


def presentation_link(base: Path | None) -> list[str]:
    """Link to the slide figures of scripts/presentation_figures.py, if written."""
    if base is None or not (base / "presentation" / "README.md").is_file():
        return []
    return [
        (
            "**Presentation figures:** [results/presentation](presentation/README.md)"
            " (`uv run --frozen python scripts/presentation_figures.py`)"
        ),
        "",
    ]


def render(ctx: dict, guide: str | None = None, base: Path | None = None) -> str:
    order = sorted(ctx["meta"], key=lambda s: sort_key(s, ctx["meta"][s], ctx["systems"].get(s)))
    lines = header(ctx) + presentation_link(base) + convergence_links(base, order)
    lines += overview(ctx, order)
    fig = "validity_overview.png" if base and (base / "validity_overview.png").is_file() else None
    lines += validity.markdown(ctx, current_systems(ctx, order), fig)
    lines += pending(ctx, order) + superseded(ctx, order)
    lines += systems(ctx, order)
    if guide:
        lines += ["", *guide.strip().splitlines(), ""]
    return "\n".join(notation(ln) for ln in lines).rstrip() + "\n"


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
    out.write_text(render(ctx, guide, out.parent))
    print(f"wrote {out} ({len(ctx['meta'])} systems)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
