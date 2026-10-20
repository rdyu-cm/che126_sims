"""Launch a LAMMPS deck as a subprocess and record a reproducibility manifest.

This is a convenience only: every deck stays a plain LAMMPS input that runs by hand
with ``lmp -in deck.in``. ``run_deck`` adds a ``run_manifest.json`` (code version, git
state, LAMMPS build, input-file hashes, timing, exit code) and a ``screen.out`` copy of
the terminal output. It records no usernames and no environment variables.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path

import sepsim
from sepsim import __version__

# Git state is taken from the code, so decks outside the repo still record the commit.
CODE_DIR = Path(sepsim.__file__).resolve().parent

MANIFEST_NAME = "run_manifest.json"
INFO_NAME = "lmp_info.txt"
INFO_INPUT = b"info configuration\n"
SCREEN_NAME = "screen.out"
EXIT_NO_LAMMPS = 127

# Commands whose first file argument is an input file; value = index of that argument.
# `molecule ID file ...` puts the file second.
_FILE_COMMANDS = {"read_data": 0, "read_restart": 0, "include": 0, "molecule": 1}


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file's contents."""
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def _deck_commands(text: str) -> list[list[str]]:
    """Split deck text into commands (comments stripped, ``&`` continuations joined)."""
    commands, pending = [], ""
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if line.endswith("&"):
            pending += line[:-1] + " "
            continue
        tokens = (pending + line).split()
        pending = ""
        if tokens:
            commands.append(tokens)
    if pending.split():
        commands.append(pending.split())
    return commands


def scan_inputs(deck: Path, workdir: Path) -> dict:
    """Best-effort list of files the deck reads, hashed.

    Follows ``read_data``, ``read_restart``, ``include`` (recursively) and ``molecule``.
    Paths are resolved relative to ``workdir`` (LAMMPS's cwd). Arguments containing a
    LAMMPS variable reference (``$``) cannot be resolved here and are listed verbatim.
    """
    files: list[dict] = []
    missing: list[dict] = []
    unresolved: list[dict] = []
    seen: set[Path] = set()

    def visit(path: Path) -> None:
        seen.add(path)
        for tokens in _deck_commands(path.read_text(errors="replace")):
            cmd, args = tokens[0], tokens[1:]
            idx = _FILE_COMMANDS.get(cmd)
            if idx is None or len(args) <= idx:
                continue
            arg = args[idx]
            entry = {"command": cmd, "arg": arg, "from": str(path)}
            if "$" in arg:
                unresolved.append(entry)
                continue
            target = (workdir / arg).resolve()
            if not target.is_file():
                missing.append({**entry, "path": str(target)})
                continue
            if target not in {Path(f["path"]) for f in files}:
                files.append({**entry, "path": str(target), "sha256": sha256_file(target)})
            if cmd == "include" and target not in seen:
                visit(target)

    visit(deck)
    return {"files": files, "missing": missing, "unresolved": unresolved}


def _git(args: list[str], cwd: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def git_info(directory: Path) -> dict:
    """Commit, dirty flag and branch of the git repo containing ``directory`` (or nulls)."""
    commit = _git(["rev-parse", "HEAD"], directory)
    if commit is None:
        return {"commit": None, "dirty": None, "branch": None}
    status = _git(["status", "--porcelain"], directory)
    return {
        "commit": commit,
        "dirty": None if status is None else bool(status),
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], directory),
    }


def parse_lmp_info(text: str) -> dict:
    """Extract version, git info and installed packages from ``info configuration`` output."""
    lines = text.splitlines()
    version = next((ln.strip() for ln in lines if ln.startswith("LAMMPS (")), None)
    git = next(
        (ln.split("Git info:", 1)[1].strip() for ln in lines if ln.startswith("Git info:")), None
    )
    packages = None
    for i, ln in enumerate(lines):
        if ln.strip() == "Installed packages:":
            packages = []
            for nxt in lines[i + 1 :]:
                if not nxt.strip():
                    if packages:
                        break
                    continue
                if nxt.rstrip().endswith(":"):
                    break
                packages.extend(nxt.split())
            break
    return {"version": version, "git": git, "packages": packages}


def lammps_executable(lmp_cmd: list[str]) -> str:
    """Pick the LAMMPS binary out of a launch command such as ``mpirun -np 8 lmp -sf gpu``.

    Returns the first token whose basename starts with ``lmp`` or ``lammps``, else the
    first token (a custom executable name).
    """
    for token in lmp_cmd:
        if os.path.basename(token).startswith(("lmp", "lammps")):
            return token
    return lmp_cmd[0]


def query_lammps(probe: list[str], workdir: Path) -> dict:
    """Feed ``info configuration`` to ``probe`` on stdin, save the output to ``lmp_info.txt``,
    and summarize it. (``lmp -h`` is avoided: GPU builds abort on hosts without a GPU.)
    """
    exe = shlex.join(probe)
    info: dict = {
        "executable": exe,
        "probe": list(probe),
        "info_sha256": None,
        "version": None,
        "git": None,
        "packages": None,
    }
    try:
        proc = subprocess.run(
            [*probe, "-nocite", "-log", "none"],
            input=INFO_INPUT,
            cwd=workdir,
            capture_output=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"
        return info
    info_path = workdir / INFO_NAME
    info_path.write_bytes(proc.stdout + proc.stderr)
    info["info_file"] = INFO_NAME
    info["info_sha256"] = sha256_file(info_path)
    info.update(parse_lmp_info((proc.stdout + proc.stderr).decode(errors="replace")))
    if proc.returncode != 0:
        info["error"] = f"'{exe}' (info configuration) exited with code {proc.returncode}"
    return info


def _write_manifest(workdir: Path, manifest: dict) -> None:
    path = workdir / MANIFEST_NAME
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def _tee(command: list[str], workdir: Path) -> int:
    """Run ``command`` in ``workdir``, streaming output to the terminal and screen.out."""
    with (
        open(workdir / SCREEN_NAME, "wb") as screen,
        subprocess.Popen(
            command, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        ) as proc,
    ):
        try:
            for line in proc.stdout:
                screen.write(line)
                sys.stdout.write(line.decode(errors="replace"))
                sys.stdout.flush()
        except KeyboardInterrupt:
            proc.terminate()
            proc.wait()
            raise
    return proc.returncode


def run_deck(
    deck: str | os.PathLike,
    workdir: str | os.PathLike | None = None,
    lmp: str | None = None,
    extra_args: tuple[str, ...] | list[str] = (),
    dry_run: bool = False,
    lmp_probe: str | None = None,
) -> int:
    """Run a LAMMPS deck via the ``lmp`` command line and write ``run_manifest.json``.

    ``lmp`` is a shell-style launch command (e.g. ``"mpirun -np 8 lmp -sf gpu"``);
    default ``$SEPSIM_LMP`` or ``lmp``. Its first token named ``lmp*``/``lammps*`` (else
    its first token) is queried with ``info configuration`` on stdin. ``lmp_probe`` (default ``$SEPSIM_LMP_PROBE``)
    overrides that query command for wrappers and containers, e.g.
    ``"apptainer exec --rocm img.sif lmp"``.
    Returns LAMMPS's exit code (0 for a dry run, 127 if LAMMPS cannot be queried).
    """
    deck_path = Path(deck)
    deck_abs = deck_path.resolve()
    if not deck_abs.is_file():
        print(f"sepsim run: deck not found: {deck}", file=sys.stderr)
        return 2
    wd = Path(workdir).resolve() if workdir is not None else deck_abs.parent
    lmp_cmd = shlex.split(lmp if lmp is not None else os.environ.get("SEPSIM_LMP", "lmp"))
    if not lmp_cmd:
        print("sepsim run: empty LAMMPS command", file=sys.stderr)
        return 2
    command = [*lmp_cmd, "-in", str(deck_abs), *extra_args]
    probe_cmd = lmp_probe if lmp_probe is not None else os.environ.get("SEPSIM_LMP_PROBE")
    probe = shlex.split(probe_cmd) if probe_cmd is not None else [lammps_executable(lmp_cmd)]
    if not probe:
        print("sepsim run: empty LAMMPS probe command", file=sys.stderr)
        return 2

    # Git state first: nothing written yet, so our own outputs can't mark the tree dirty.
    git = git_info(CODE_DIR)
    deck_top = _git(["rev-parse", "--show-toplevel"], deck_abs.parent)
    same_repo = deck_top == _git(["rev-parse", "--show-toplevel"], CODE_DIR)
    deck_git = None if same_repo else git_info(deck_abs.parent)
    wd.mkdir(parents=True, exist_ok=True)
    lammps = query_lammps(probe, wd)

    manifest = {
        "sepsim_version": __version__,
        "python": sys.version,
        "platform": platform.platform(),
        "hostname": platform.node(),
        "git": git,  # sepsim code repo
        "deck_git": deck_git,  # deck's repo, only if it differs from the code repo
        "command": command,
        "cwd": str(wd),
        "deck": {
            "path": str(deck_path),
            "resolved": str(deck_abs),
            "sha256": sha256_file(deck_abs),
        },
        "inputs": scan_inputs(deck_abs, wd),
        "lammps": lammps,
        "start_time": _now(),
        "end_time": None,
        "wall_time_s": None,
        "exit_code": None,
        "status": "started",
    }

    if dry_run:
        manifest.update(status="dry-run", end_time=manifest["start_time"])
        _write_manifest(wd, manifest)
        if "error" in lammps:
            print(f"sepsim run: warning: {lammps['error']}", file=sys.stderr)
        print(f"(cd {shlex.quote(str(wd))} && {shlex.join(command)})")
        return 0

    if "error" in lammps:
        manifest.update(status="failed", exit_code=EXIT_NO_LAMMPS, end_time=_now())
        _write_manifest(wd, manifest)
        print(
            f"sepsim run: cannot query LAMMPS with "
            f"'{lammps['executable']}' (info configuration): "
            f"{lammps['error']}\n"
            "Set --lmp or SEPSIM_LMP to a working LAMMPS command, or --lmp-probe or "
            "SEPSIM_LMP_PROBE to a command that runs the LAMMPS binary.",
            file=sys.stderr,
        )
        return EXIT_NO_LAMMPS

    _write_manifest(wd, manifest)
    t0 = time.monotonic()
    status = None
    try:
        code = _tee(command, wd)
    except KeyboardInterrupt:
        code, status = 130, "interrupted"
    except OSError as exc:
        code, status = EXIT_NO_LAMMPS, "failed"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        print(f"sepsim run: failed to launch {command[0]!r}: {exc}", file=sys.stderr)
    manifest.update(
        exit_code=code,
        status=status or ("finished" if code == 0 else "failed"),
        end_time=_now(),
        wall_time_s=round(time.monotonic() - t0, 3),
    )
    _write_manifest(wd, manifest)
    return code
