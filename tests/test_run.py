"""Tests for `sepsim run` using a fake `lmp` executable (no real LAMMPS)."""

import hashlib
import json
import shutil
import subprocess
import sys

import pytest

from sepsim.cli import main
from sepsim.run import parse_lmp_help, run_deck

FAKE_LMP = f"""#!{sys.executable}
import json, os, sys

args = sys.argv[1:]
log = os.environ.get("FAKE_LMP_LOG")
if log:
    with open(log, "a") as fh:
        fh.write(json.dumps(args) + "\\n")
if args == ["-h"]:
    print("Large-scale Atomic/Molecular Massively Parallel Simulator - 29 Aug 2024 - Update 1")
    print("LAMMPS (29 Aug 2024 - Update 1)")
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
    assert lammps["version"] == "LAMMPS (29 Aug 2024 - Update 1)"
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


def test_launcher_prefix_uses_last_token(fake_lmp, deck, tmp_path):
    """--lmp may carry a launcher prefix; -h goes to the last token only."""
    lmp = f"{shutil.which('env')} {fake_lmp}"
    assert run_deck(deck, lmp=lmp) == 0
    m = manifest(deck.parent)
    assert m["command"][:2] == [shutil.which("env"), str(fake_lmp)]
    assert m["lammps"]["executable"] == str(fake_lmp)


def test_sepsim_lmp_env_var(fake_lmp, deck, monkeypatch):
    monkeypatch.setenv("SEPSIM_LMP", str(fake_lmp))
    assert main(["run", str(deck)]) == 0
    assert manifest(deck.parent)["command"][0] == str(fake_lmp)


def test_git_info(fake_lmp, tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

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
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    git("init", "-q", "-b", "trunk")
    deck = repo / "in.deck"
    deck.write_text("run 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "init")
    out = tmp_path / "out"  # keep outputs outside the repo so the tree stays clean

    assert run_deck(deck, workdir=out, lmp=str(fake_lmp)) == 0
    g = manifest(out)["git"]
    assert g == {"commit": git("rev-parse", "HEAD"), "dirty": False, "branch": "trunk"}

    deck.write_text("run 1\n")
    assert run_deck(deck, workdir=out, lmp=str(fake_lmp)) == 0
    assert manifest(out)["git"]["dirty"] is True


def test_git_info_outside_repo(fake_lmp, deck, monkeypatch, tmp_path):
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    run_deck(deck, lmp=str(fake_lmp), dry_run=True)
    assert manifest(deck.parent)["git"] == {"commit": None, "dirty": None, "branch": None}


def test_parse_lmp_help_without_markers():
    assert parse_lmp_help("nothing useful\n") == {"version": None, "packages": None}
