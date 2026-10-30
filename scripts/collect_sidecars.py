"""Copy the small per-run sidecars into git and checksum the big run outputs.

Sidecars (committed, ``--out``, default ``results/run_sidecars``): for every run directory
``<root>/<system>/<stage>/`` of each ``--runs`` root, the ``in.*`` decks,
``run_manifest.json``, ``progress.json``, ``progress.md`` and ``lmp_info.txt`` go to
``<out>/<system>/<stage>/``, and the Slurm script ``<jobs>/<system>/<stage>/job.sh`` (plus
its ``in.*``) to ``<out>/<system>/<stage>/job/`` (for a stage renamed after the run, e.g.
``sweep_old_unrelaxed_cancelled``, the job dir under the original name is used if its deck
matches the run's deck sha256). ``bench_*``/``smoke_*`` stages, hidden
directories and ``jobs/analysis`` are skipped; superseded stages (``*_old_*``,
``*_cancelled*``) are kept. When a system/stage is in several roots, each file is taken
from the root of the node that ran it (``hostname`` in ``run_manifest.json``) first, then
from the other roots in order. ``<out>/index.tsv`` records, per run, the node that ran it,
its status, where the files came from and whether the job deck matches the run's deck.

Data manifest (``--manifest``, default ``results/data_manifest.tsv``): node, path (relative
to the project root, i.e. ``results/runs/...``), bytes, sha256, mtime (UTC), kind for the
large files that stay on the compute nodes: ``*.dcd`` (dcd), ``*.data`` (data, snapshots),
``log.lammps`` (log), ``screen.out`` (screen). Restart files are regenerable and not listed.
Only the ``--runs`` roots labelled ``--node-label`` are hashed (files on *this* node); rows
of other nodes already in the manifest are kept, and ``--merge other.tsv`` adds the rows of
a TSV made on another node. ``--skip-existing`` reuses a row whose size and mtime are
unchanged. Files that change while being hashed (a running job) are skipped and reported.

    uv run --frozen python scripts/collect_sidecars.py [--runs [LABEL=]DIR ...] [--jobs DIR]
        [--out DIR] [--manifest TSV] [--node-label LABEL] [--merge TSV ...]
        [--skip-existing] [--no-sidecars] [--no-hash]

Stdlib only, so it can be copied to the other node and run there, e.g. on rdyu-rog::

    cd ~/projects/che126_sims && nice -n 15 ionice -c3 ~/.local/bin/uv run --frozen \\
        python /tmp/collect_sidecars.py --runs rdyu-rog=results/runs --node-label rdyu-rog \\
        --no-sidecars --manifest /tmp/data_manifest_rog.tsv

then, on the server, ``... collect_sidecars.py --skip-existing --merge data_manifest_rog.tsv``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

CHUNK = 8 * 1024 * 1024
SIDECAR_NAMES = ("run_manifest.json", "progress.json", "progress.md", "lmp_info.txt")
SKIP_STAGE_PREFIXES = ("bench_", "smoke_")
SKIP_JOB_SYSTEMS = ("analysis",)
MAX_BYTES = 2 * 1024 * 1024
COLUMNS = ("node", "path", "bytes", "sha256", "mtime_utc", "kind")
INDEX_COLUMNS = (
    "system",
    "stage",
    "copy",
    "ran_on",
    "status",
    "sources",
    "files",
    "job",
    "job_deck_matches",
)


def _main_checkout() -> Path:
    """The main checkout (also from a git worktree); the cwd outside a repository."""
    here = Path(__file__).resolve().parent
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=here,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return Path(out).parent
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd()


def _worktree_root() -> Path:
    return Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- run discovery


def skip_stage(stage: str) -> bool:
    return stage.startswith(SKIP_STAGE_PREFIXES) or stage in ("bench", "smoke")


def run_dirs(root: Path):
    """Yield (system, stage, path) for every run directory under ``root``."""
    if not root.is_dir():
        return
    for sysdir in sorted(root.iterdir()):
        if not sysdir.is_dir() or sysdir.name.startswith("."):
            continue
        for stagedir in sorted(sysdir.iterdir()):
            if not stagedir.is_dir() or stagedir.name.startswith("."):
                continue
            if skip_stage(stagedir.name):
                continue
            yield sysdir.name, stagedir.name, stagedir


def sidecar_files(d: Path) -> list[Path]:
    files = [p for p in sorted(d.glob("in.*")) if p.is_file()]
    files += [d / n for n in SIDECAR_NAMES if (d / n).is_file()]
    return files


def read_manifest(d: Path) -> dict:
    try:
        return json.loads((d / "run_manifest.json").read_text())
    except (OSError, ValueError):
        return {}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
        if hasattr(os, "posix_fadvise"):  # don't push production jobs out of the page cache
            os.posix_fadvise(f.fileno(), 0, 0, os.POSIX_FADV_DONTNEED)
    return h.hexdigest()


# --------------------------------------------------------------------------- sidecars


def deck_matches(jdir: Path, deck: dict) -> str:
    """'yes'/'no' if the job dir's copy of the run's deck matches its sha256, else ''."""
    if not deck.get("path") or not deck.get("sha256"):
        return ""
    jdeck = jdir / Path(deck["path"]).name
    if not jdeck.is_file():
        return ""
    return "yes" if _sha256(jdeck) == deck["sha256"] else "no"


def find_job_dir(jobs: Path | None, system: str, stage: str, deck: dict) -> Path | None:
    """``jobs/<system>/<stage>``; for a renamed stage (``sweep_old_unrelaxed_cancelled``)
    the job dir under its original name (a prefix, longest first), but only if its deck
    matches the run's deck sha256."""
    if jobs is None or not (jobs / system).is_dir():
        return None
    exact = jobs / system / stage
    if (exact / "job.sh").is_file():
        return exact
    prefixes = [
        d
        for d in (jobs / system).iterdir()
        if (d / "job.sh").is_file() and stage.startswith(d.name + "_")
    ]
    for d in sorted(prefixes, key=lambda d: -len(d.name)):
        if deck_matches(d, deck) == "yes":
            return d
    return None


def attach_job(
    jobs: Path | None, system: str, stage: str, manifest: dict, dest: Path, row: dict, warnings
) -> int:
    """Copy the run's Slurm job dir into ``dest/job``; fill ``row``; return files copied."""
    deck = manifest.get("deck") or {}
    jdir = None if system in SKIP_JOB_SYSTEMS else find_job_dir(jobs, system, stage, deck)
    if jdir is None:
        return 0
    n = 0
    jdest = dest / "job"
    jdest.mkdir(parents=True, exist_ok=True)
    for p in [jdir / "job.sh", *sorted(jdir.glob("in.*"))]:
        if p.is_file():
            shutil.copy2(p, jdest / p.name)
            n += 1
    row["job"] = "yes" if jdir.name == stage else jdir.name
    row["job_deck_matches"] = deck_matches(jdir, deck)
    if row["job_deck_matches"] == "no":
        warnings.append(
            f"{system}/{stage}: job deck in jobs/{system}/{jdir.name} differs from the"
            " run's deck (re-rendered after the run?)"
        )
    return n


def group_copies(by_label: dict[str, Path]) -> list[dict]:
    """Group the copies of one system/stage by run identity (hostname, start_time).

    Each group lists its labels with the node that ran it first; groups are ordered
    latest start first (the main copy). Copies without a manifest join the main group.
    """
    groups: dict[tuple, dict] = {}
    orphans = []
    for lbl, d in by_label.items():
        m = read_manifest(d)
        if not m:
            orphans.append(lbl)
            continue
        key = (m.get("hostname", ""), m.get("start_time", ""))
        g = groups.setdefault(key, {"manifest": m, "ran_on": key[0], "start": key[1], "labels": []})
        g["labels"].append(lbl)
        if lbl == key[0]:
            g["manifest"] = m  # the copy on the node that ran it
    out = sorted(groups.values(), key=lambda g: g["start"], reverse=True)
    if not out:
        out = [{"manifest": {}, "ran_on": "", "start": "", "labels": []}]
    out[0]["labels"] += orphans
    for g in out:
        g["order"] = sorted(g["labels"], key=lambda lbl: lbl != g["ran_on"])
    return out


def collect_sidecars(roots: list[tuple[str, Path]], jobs: Path | None, out: Path) -> dict:
    """Copy sidecars of every run in ``roots`` into ``out``; return a summary."""
    runs: dict[tuple[str, str], dict[str, Path]] = {}
    for label, root in roots:
        for system, stage, d in run_dirs(root):
            runs.setdefault((system, stage), {})[label] = d

    index_rows, warnings, big = [], [], []
    n_files = 0
    for (system, stage), by_label in sorted(runs.items()):
        groups = group_copies(by_label)
        if len(groups) > 1:
            warnings.append(
                f"{system}/{stage}: {len(groups)} different runs with this name ("
                + ", ".join(f"{g['ran_on'] or '?'} {g['start'] or '?'}" for g in groups)
                + "); the latest is the main copy, the others go to other_run_<node>/"
            )
        for i, group in enumerate(groups):
            manifest, ran_on, order = group["manifest"], group["ran_on"], group["order"]
            if not manifest:
                warnings.append(f"{system}/{stage}: no run_manifest.json ({','.join(order)})")
            copy = "" if i == 0 else f"other_run_{order[0]}"
            dest = out / system / stage / copy if copy else out / system / stage
            chosen: dict[str, tuple[str, Path]] = {}
            for lbl in order:
                for p in sidecar_files(by_label[lbl]):
                    chosen.setdefault(p.name, (lbl, p))
            for name, (lbl, p) in sorted(chosen.items()):
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest / name)
                n_files += 1
                if p.stat().st_size > MAX_BYTES:
                    big.append((dest / name, p.stat().st_size))
            row = {
                "system": system,
                "stage": stage,
                "copy": copy,
                "ran_on": ran_on,
                "status": manifest.get("status", ""),
                "sources": ",".join(lbl for lbl in order if lbl in {c[0] for c in chosen.values()}),
                "files": str(len(chosen)),
                "job": "no",
                "job_deck_matches": "",
            }
            if i == 0:
                n_files += attach_job(jobs, system, stage, manifest, dest, row, warnings)
            index_rows.append(row)

    if index_rows:
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "index.tsv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=INDEX_COLUMNS, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(index_rows)
    return {"runs": len(index_rows), "files": n_files, "warnings": warnings, "big": big}


# --------------------------------------------------------------------------- data manifest


def kind_of(name: str) -> str | None:
    if name.endswith(".dcd"):
        return "dcd"
    if name.endswith(".data"):
        return "data"
    if name == "log.lammps":
        return "log"
    if name == "screen.out":
        return "screen"
    return None


def _mtime(st: os.stat_result) -> str:
    return datetime.fromtimestamp(int(st.st_mtime), UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_tsv(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: (r["node"], r["path"]))
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows({k: r[k] for k in COLUMNS} for r in rows)
    tmp.replace(path)


def hash_node(
    roots: list[Path],
    node: str,
    previous: dict[tuple[str, str], dict],
    skip_existing: bool,
) -> tuple[list[dict], dict]:
    """Rows for the large files under ``roots`` on this node."""
    rows, stats = [], {"hashed_bytes": 0, "hashed": 0, "reused": 0, "in_flux": []}
    for root in roots:
        rroot = root.resolve()
        prefix = rroot.relative_to(rroot.parents[1])  # <project>/results/runs -> results/runs
        for _system, _stage, d in run_dirs(root):
            for p in sorted(d.iterdir()):
                kind = kind_of(p.name)
                if kind is None or not p.is_file():
                    continue
                rel = (prefix / p.relative_to(root)).as_posix()
                st = p.stat()
                row = {
                    "node": node,
                    "path": rel,
                    "bytes": str(st.st_size),
                    "mtime_utc": _mtime(st),
                    "kind": kind,
                }
                old = previous.get((node, rel))
                if (
                    skip_existing
                    and old
                    and old["bytes"] == row["bytes"]
                    and old["mtime_utc"] == row["mtime_utc"]
                    and old.get("sha256")
                ):
                    row["sha256"] = old["sha256"]
                    stats["reused"] += 1
                    rows.append(row)
                    continue
                digest = _sha256(p)
                st2 = p.stat()
                if (st2.st_size, st2.st_mtime) != (st.st_size, st.st_mtime):
                    stats["in_flux"].append(rel)
                    continue
                row["sha256"] = digest
                stats["hashed"] += 1
                stats["hashed_bytes"] += st.st_size
                rows.append(row)
    return rows, stats


def build_manifest(
    manifest: Path,
    node: str,
    roots: list[Path] | None,
    merge: list[Path],
    skip_existing: bool,
) -> dict:
    existing = {(r["node"], r["path"]): r for r in read_tsv(manifest)}
    stats: dict = {}
    combined = dict(existing)
    if roots is not None:
        rows, stats = hash_node(roots, node, existing, skip_existing)
        combined = {k: r for k, r in existing.items() if r["node"] != node}
        combined.update({(r["node"], r["path"]): r for r in rows})
    for m in merge:
        other = read_tsv(m)
        nodes = {r["node"] for r in other}
        combined = {k: r for k, r in combined.items() if r["node"] not in nodes}
        combined.update({(r["node"], r["path"]): r for r in other})
    write_tsv(manifest, list(combined.values()))
    per_node: dict[str, list[int]] = {}
    for r in combined.values():
        c = per_node.setdefault(r["node"], [0, 0])
        c[0] += 1
        c[1] += int(r["bytes"])
    stats["per_node"] = per_node
    return stats


# --------------------------------------------------------------------------- CLI


def parse_root(spec: str, default_label: str) -> tuple[str, Path]:
    label, sep, path = spec.partition("=")
    if not sep:
        return default_label, Path(spec)
    return label, Path(path)


def main(argv: list[str] | None = None) -> int:
    main_root = _main_checkout()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--runs",
        action="append",
        metavar="[LABEL=]DIR",
        help="run root (repeatable); LABEL defaults to --node-label. Default: "
        "rdyu-server=<main>/results/runs, "
        "rdyu-rog=<main>/results/progress/rdyu-rog",
    )
    ap.add_argument("--jobs", type=Path, default=main_root / "jobs")
    ap.add_argument("--out", type=Path, default=_worktree_root() / "results" / "run_sidecars")
    ap.add_argument(
        "--manifest", type=Path, default=_worktree_root() / "results" / "data_manifest.tsv"
    )
    ap.add_argument("--node-label", default=socket.gethostname())
    ap.add_argument(
        "--merge",
        type=Path,
        action="append",
        default=[],
        help="TSV from another node to merge (its nodes' rows replace ours)",
    )
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="reuse manifest rows whose size and mtime are unchanged",
    )
    ap.add_argument("--no-sidecars", action="store_true", help="only write the manifest")
    ap.add_argument(
        "--no-hash", action="store_true", help="do not hash this node's files (e.g. only --merge)"
    )
    args = ap.parse_args(argv)

    if args.runs:
        roots = [parse_root(s, args.node_label) for s in args.runs]
    else:
        roots = [
            ("rdyu-server", main_root / "results" / "runs"),
            ("rdyu-rog", main_root / "results" / "progress" / "rdyu-rog"),
        ]
    for label, root in roots:
        if not root.is_dir():
            print(f"warning: run root {label}={root} not found", file=sys.stderr)

    if not args.no_sidecars:
        s = collect_sidecars(roots, args.jobs if args.jobs.is_dir() else None, args.out)
        print(f"sidecars: {s['runs']} runs, {s['files']} files -> {args.out}")
        for w in s["warnings"]:
            print(f"  note: {w}")
        for p, n in s["big"]:
            print(f"  WARNING: {p} is {n / 1e6:.1f} MB (> 2 MB)")

    hash_roots = None if args.no_hash else [r for lbl, r in roots if lbl == args.node_label]
    if hash_roots is not None or args.merge:
        st = build_manifest(
            args.manifest, args.node_label, hash_roots, args.merge, args.skip_existing
        )
        if hash_roots is not None:
            print(
                f"hashed on {args.node_label}: {st['hashed']} files "
                f"({st['hashed_bytes'] / 1e9:.2f} GB), reused {st['reused']}"
            )
            for rel in st["in_flux"]:
                print(f"  skipped (changed while hashing): {rel}")
        for node, (n, b) in sorted(st["per_node"].items()):
            print(f"manifest {args.manifest}: {node}: {n} rows, {b / 1e9:.2f} GB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
