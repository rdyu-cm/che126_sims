"""Tests for `sepsim run` using a fake `lmp` executable (no real LAMMPS)."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import sepsim
import sepsim.run as sepsim_run
from sepsim.cli import main
from sepsim.run import parse_lmp_help, run_deck

LMP_HEADER = "Large-scale Atomic/Molecular Massively Parallel Simulator - "  # real `lmp -h`

FAKE_LMP = f"""#!{sys.executable}
import json, os, sys

args = sys.argv[1:]
log = os.environ.get("FAKE_LMP_LOG")
if log:
    with open(log, "a") as fh:
        fh.write(json.dumps(args) + "\\n")
if args == ["-h"]:
    print("Large-scale Atomic/Molecular Massively Parallel Simulator - 29 Aug 2024 - Update 1")
    print("Git info (stable / stable_29Aug2024_update1-0-g0123456789ab)")
    print()
    print("Installed packages:")
    print()
    print("KSPACE MOLECULE")
    print("CG-SPICA")
    print()
    print("List of individual style options included in this LAMMPS executable")
    sys.exit(0)
if "-in" in args:
    print("fake run ok")
    open("log.lammps", "w").close()
    sys.exit(int(os.environ.get("FAKE_LMP_EXIT", "0")))
sys.exit(1)
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calls(log):
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


@pytest.fixture
def fake_lmp(tmp_path, monkeypatch):
    """Path to an executable fake lmp; invocations are logged to tmp_path/calls.jsonl."""
    exe = tmp_path / "bin" / "lmp"
    exe.parent.mkdir()
    exe.write_text(FAKE_LMP)
    exe.chmod(0o755)
    monkeypatch.setenv("FAKE_LMP_LOG", str(tmp_path / "calls.jsonl"))
    monkeypatch.delenv("FAKE_LMP_EXIT", raising=False)
    monkeypatch.delenv("SEPSIM_LMP", raising=False)
    monkeypatch.delenv("SEPSIM_LMP_PROBE", raising=False)
    return exe


FAKE_MPIRUN = f"""#!{sys.executable}
import os, sys

args = sys.argv[1:]
if args[:1] == ["-np"]:
    args = args[2:]
os.execv(args[0], args)
"""


def make_exe(tmp_path, name, text):
    """Write an executable script tmp_path/bin/<name>."""
    exe = tmp_path / "bin" / name
    exe.parent.mkdir(exist_ok=True)
    exe.write_text(text)
    exe.chmod(0o755)
    return exe


@pytest.fixture
def deck(tmp_path):
    """A deck in tmp_path/sim that reads data, includes a file that includes another."""
    sim = tmp_path / "sim"
    sim.mkdir()
    (sim / "data.lmp").write_text("fake data\n")
    (sim / "settings.in").write_text("pair_style lj/cut 10.0\ninclude more.in  # nested\n")
    (sim / "more.in").write_text("molecule water water.mol\n")
    (sim / "water.mol").write_text("fake molecule\n")
    path = sim / "in.test"
    path.write_text(
        "# test deck\n"
        "units real\n"
        "read_data data.lmp &\n"
        "  extra/atom/types 1\n"
        "include settings.in\n"
        "read_restart ${restart_file}\n"
        "include missing.in\n"
        "run 0\n"
    )
    return path


def manifest(directory):
    return json.loads((directory / "run_manifest.json").read_text())


def test_manifest_fields_and_hashes(fake_lmp, deck, capsys):
    assert run_deck(deck, lmp=str(fake_lmp)) == 0
    sim = deck.parent
    m = manifest(sim)
    for key in [
        "sepsim_version",
        "python",
        "platform",
        "hostname",
        "git",
        "deck_git",
        "command",
        "cwd",
        "deck",
        "inputs",
        "lammps",
        "start_time",
        "end_time",
        "wall_time_s",
        "exit_code",
        "status",
    ]:
        assert key in m
    assert m["status"] == "finished" and m["exit_code"] == 0
    assert m["cwd"] == str(sim)
    assert m["command"] == [str(fake_lmp), "-in", str(deck)]
    assert m["deck"]["sha256"] == sha(deck)
    assert m["wall_time_s"] >= 0

    hashed = {f["path"]: f["sha256"] for f in m["inputs"]["files"]}
    for name in ["data.lmp", "settings.in", "more.in", "water.mol"]:  # include recursion
        assert hashed[str(sim / name)] == sha(sim / name)
    assert [u["arg"] for u in m["inputs"]["unresolved"]] == ["${restart_file}"]
    assert [x["path"] for x in m["inputs"]["missing"]] == [str(sim / "missing.in")]

    lammps = m["lammps"]
    assert lammps["version"] == LMP_HEADER + "29 Aug 2024 - Update 1"
    assert lammps["packages"] == ["KSPACE", "MOLECULE", "CG-SPICA"]
    assert lammps["help_sha256"] == sha(sim / "lmp_help.txt")

    assert (sim / "screen.out").read_text() == "fake run ok\n"
    assert (sim / "log.lammps").exists()
    assert "fake run ok" in capsys.readouterr().out
    assert "USER" not in json.dumps(m) and "environ" not in json.dumps(m)


def test_nonzero_exit_propagates(fake_lmp, deck, monkeypatch):
    monkeypatch.setenv("FAKE_LMP_EXIT", "3")
    assert run_deck(deck, lmp=str(fake_lmp)) == 3
    m = manifest(deck.parent)
    assert m["status"] == "failed" and m["exit_code"] == 3


def test_dry_run_does_not_execute(fake_lmp, deck, tmp_path):
    assert main(["run", str(deck), "--lmp", str(fake_lmp), "--dry-run"]) == 0
    assert all("-in" not in c for c in calls(tmp_path / "calls.jsonl"))
    m = manifest(deck.parent)
    assert m["status"] == "dry-run"
    assert not (deck.parent / "log.lammps").exists()


def test_missing_executable_returns_127(deck, tmp_path, capsys):
    rc = main(["run", str(deck), "--lmp", str(tmp_path / "no-such-lmp")])
    assert rc == 127
    m = manifest(deck.parent)
    assert m["status"] == "failed" and m["exit_code"] == 127
    assert m["lammps"]["error"]
    assert "cannot query LAMMPS" in capsys.readouterr().err


def test_extra_args_and_workdir(fake_lmp, deck, tmp_path):
    out = tmp_path / "out" / "run1"
    argv = ["run", str(deck), "--workdir", str(out), "--lmp", f"{fake_lmp}"]
    assert main([*argv, "--", "-var", "T", "300", "-sf", "gpu"]) == 0
    last = calls(tmp_path / "calls.jsonl")[-1]
    assert last == ["-in", str(deck), "-var", "T", "300", "-sf", "gpu"]
    assert (out / "log.lammps").exists() and (out / "run_manifest.json").exists()
    # Inputs resolve relative to the workdir, so the deck's neighbours are now missing.
    assert manifest(out)["inputs"]["files"] == []


def test_launcher_prefix_probes_lmp_token(fake_lmp, deck, tmp_path):
    """--lmp may carry a launcher prefix; -h goes to the lmp token only."""
    lmp = f"{shutil.which('env')} {fake_lmp}"
    assert run_deck(deck, lmp=lmp) == 0
    m = manifest(deck.parent)
    assert m["command"][:2] == [shutil.which("env"), str(fake_lmp)]
    assert m["lammps"]["executable"] == str(fake_lmp)
    assert m["lammps"]["probe"] == [str(fake_lmp)]


def test_mpirun_with_trailing_args_probes_lmp(fake_lmp, deck, tmp_path):
    """`mpirun -np 8 lmp -sf gpu`: -h goes to lmp, not to the trailing `gpu`."""
    mpirun = make_exe(tmp_path, "mpirun", FAKE_MPIRUN)
    lmp = f"{mpirun} -np 8 {fake_lmp} -sf gpu"
    assert run_deck(deck, lmp=lmp) == 0
    m = manifest(deck.parent)
    assert m["status"] == "finished"
    assert m["command"] == [str(mpirun), "-np", "8", str(fake_lmp), "-sf", "gpu", "-in", str(deck)]
    assert m["lammps"]["executable"] == str(fake_lmp)
    assert m["lammps"]["version"] == LMP_HEADER + "29 Aug 2024 - Update 1"
    assert m["lammps"]["packages"] == ["KSPACE", "MOLECULE", "CG-SPICA"]
    assert "error" not in m["lammps"]
    assert calls(tmp_path / "calls.jsonl") == [["-h"], ["-sf", "gpu", "-in", str(deck)]]


def test_probe_falls_back_to_first_token(fake_lmp, deck, tmp_path):
    """No lmp*/lammps* token: the first token is the executable."""
    custom = make_exe(tmp_path, "mysim", FAKE_LMP)
    assert run_deck(deck, lmp=f"{custom} -sf gpu") == 0
    m = manifest(deck.parent)
    assert m["lammps"]["executable"] == str(custom)
    assert m["lammps"]["version"] == LMP_HEADER + "29 Aug 2024 - Update 1"
    assert calls(tmp_path / "calls.jsonl") == [["-h"], ["-sf", "gpu", "-in", str(deck)]]


def test_lmp_probe_override_and_precedence(fake_lmp, deck, tmp_path, monkeypatch):
    """--lmp-probe beats $SEPSIM_LMP_PROBE, which beats the heuristic."""
    env_probe = make_exe(tmp_path, "envprobe", FAKE_LMP.replace("29 Aug 2024", "2 Aug 2023"))
    arg_probe = make_exe(tmp_path, "argprobe", FAKE_LMP.replace("29 Aug 2024", "7 Feb 2024"))
    log = tmp_path / "calls.jsonl"
    env = shutil.which("env")

    monkeypatch.setenv("SEPSIM_LMP_PROBE", f"{env} {env_probe}")
    assert main(["run", str(deck), "--lmp", str(fake_lmp)]) == 0
    m = manifest(deck.parent)
    assert m["lammps"]["probe"] == [env, str(env_probe)]
    assert m["lammps"]["executable"] == f"{env} {env_probe}"
    assert m["lammps"]["version"] == LMP_HEADER + "2 Aug 2023 - Update 1"
    assert m["command"] == [str(fake_lmp), "-in", str(deck)]
    assert calls(log) == [["-h"], ["-in", str(deck)]]

    log.unlink()
    assert main(["run", str(deck), "--lmp", str(fake_lmp), "--lmp-probe", str(arg_probe)]) == 0
    m = manifest(deck.parent)
    assert m["lammps"]["executable"] == str(arg_probe)
    assert m["lammps"]["version"] == LMP_HEADER + "7 Feb 2024 - Update 1"
    assert calls(log) == [["-h"], ["-in", str(deck)]]


def test_sepsim_lmp_env_var(fake_lmp, deck, monkeypatch):
    monkeypatch.setenv("SEPSIM_LMP", str(fake_lmp))
    assert main(["run", str(deck)]) == 0
    assert manifest(deck.parent)["command"][0] == str(fake_lmp)


def _git_repo(path):
    """Init a one-commit repo at ``path``; returns a git runner bound to it."""
    path.mkdir()

    def git(*args):
        return subprocess.run(
            [
                "git",
                "-c",
                "user.name=t",
                "-c",
                "user.email=t@t",
                "-c",
                "commit.gpgsign=false",
                *args,
            ],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    git("init", "-q", "-b", "trunk")
    (path / "in.deck").write_text("run 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "init")
    return git


def test_code_dir_is_the_sepsim_package():
    assert sepsim_run.CODE_DIR == Path(sepsim.__file__).resolve().parent


def test_git_info_from_code_repo(fake_lmp, tmp_path, monkeypatch):
    code = tmp_path / "code"
    git = _git_repo(code)
    monkeypatch.setattr(sepsim_run, "CODE_DIR", code)
    deck = tmp_path / "decks" / "in.deck"  # outside any repo
    deck.parent.mkdir()
    deck.write_text("run 0\n")
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    out = tmp_path / "out"  # keep outputs outside the repo so the tree stays clean

    assert run_deck(deck, workdir=out, lmp=str(fake_lmp)) == 0
    m = manifest(out)
    assert m["git"] == {"commit": git("rev-parse", "HEAD"), "dirty": False, "branch": "trunk"}
    assert m["deck_git"] == {"commit": None, "dirty": None, "branch": None}

    (code / "in.deck").write_text("run 1\n")
    assert run_deck(deck, workdir=out, lmp=str(fake_lmp)) == 0
    assert manifest(out)["git"]["dirty"] is True


def test_deck_git_only_when_different(fake_lmp, tmp_path, monkeypatch):
    code = tmp_path / "code"
    _git_repo(code)
    other = tmp_path / "other"
    other_git = _git_repo(other)
    out = tmp_path / "out"

    monkeypatch.setattr(sepsim_run, "CODE_DIR", code)
    assert run_deck(code / "in.deck", workdir=out, lmp=str(fake_lmp)) == 0
    assert manifest(out)["deck_git"] is None  # deck in the code repo

    assert run_deck(other / "in.deck", workdir=out, lmp=str(fake_lmp)) == 0
    assert manifest(out)["deck_git"]["commit"] == other_git("rev-parse", "HEAD")


def test_git_info_outside_repo(fake_lmp, deck, monkeypatch, tmp_path):
    monkeypatch.setattr(sepsim_run, "CODE_DIR", tmp_path)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    run_deck(deck, lmp=str(fake_lmp), dry_run=True)
    m = manifest(deck.parent)
    assert m["git"] == {"commit": None, "dirty": None, "branch": None}
    assert m["deck_git"] is None


def test_parse_lmp_help_without_markers():
    assert parse_lmp_help("nothing useful\n") == {"version": None, "packages": None}
