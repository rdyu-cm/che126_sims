"""scripts/collect_sidecars.py: sidecar copies, job scripts, data manifest, merge, reuse."""

import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "collect_sidecars.py"


@pytest.fixture(scope="module")
def cs():
    spec = importlib.util.spec_from_file_location("collect_sidecars", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(
    root: Path, system: str, stage: str, host: str, deck: str = "run 10\n", start: str = "t0"
) -> Path:
    d = root / system / stage
    d.mkdir(parents=True)
    (d / f"in.{stage.split('_')[0]}").write_text(deck)
    manifest = {
        "hostname": host,
        "status": "finished",
        "start_time": start,
        "deck": {
            "path": f"in.{stage.split('_')[0]}",
            "sha256": hashlib.sha256(deck.encode()).hexdigest(),
        },
    }
    (d / "run_manifest.json").write_text(json.dumps(manifest))
    (d / "progress.json").write_text(json.dumps({"cache": {"curves": [1, 2, 3]}}))
    (d / "progress.md").write_text("# progress\n")
    (d / "log.lammps").write_text("thermo\n")
    (d / "screen.out").write_text("screen\n")
    (d / "traj.dcd").write_bytes(b"\x00" * 1000)
    (d / "hold_25C.data").write_text("snapshot\n")
    (d / "restart.a").write_bytes(b"r")
    (d / "x.restart").write_bytes(b"r")
    return d


@pytest.fixture
def tree(tmp_path):
    server = tmp_path / "proj" / "results" / "runs"
    rog = tmp_path / "rogcopy"
    jobs = tmp_path / "proj" / "jobs"
    _run(server, "pe_cg", "sweep", "rdyu-server")
    (server / "pe_cg" / "sweep" / "lmp_info.txt").write_text("server info\n")
    _run(server, "pe_cg", "bench_r1t1", "rdyu-server")
    _run(server, "pe_cg", "sweep_old_20ns_box", "rdyu-server", deck="old box\n")
    # Renamed after the run: its job dir keeps the original name (same deck).
    _run(server, "pe_cg", "extend_job92_cancelled", "rdyu-server", deck="ext\n")
    (server / "pe_cg" / ".claude").mkdir()
    # Ran on rog: the server holds a copy (with lmp_info.txt), rog's copy is preferred.
    _run(server, "pe_ua", "prep", "rdyu-rog", deck="server copy\n")
    (server / "pe_ua" / "prep" / "lmp_info.txt").write_text("info\n")
    _run(rog, "pe_ua", "prep", "rdyu-rog", deck="rog deck\n")
    _run(rog, "pe_ua", "smoke_gpu", "rdyu-rog")
    # Two different runs with one name: an abandoned server attempt and the later rog run.
    _run(server, "pe_cg", "prep", "rdyu-server", deck="server attempt\n", start="t1")
    (server / "pe_cg" / "prep" / "lmp_info.txt").write_text("server info\n")
    _run(rog, "pe_cg", "prep", "rdyu-rog", deck="rog run\n", start="t2")
    for system, stage, deck in [
        ("pe_cg", "sweep", "run 10\n"),
        ("pe_cg", "bench_r1t1", "x"),
        ("pe_ua", "prep", "stale\n"),
        ("pe_cg", "extend_job92", "ext\n"),
    ]:
        j = jobs / system / stage
        j.mkdir(parents=True)
        (j / "job.sh").write_text("#!/bin/bash\n")
        (j / f"in.{stage.split('_')[0]}").write_text(deck)
    (jobs / "analysis").mkdir()
    (jobs / "analysis" / "c240_sweep.sh").write_text("x")
    return {"server": server, "rog": rog, "jobs": jobs, "tmp": tmp_path}


def _rows(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def test_sidecars_copied_bench_skipped_job_picked_up(cs, tree):
    out = tree["tmp"] / "out"
    s = cs.collect_sidecars(
        [("rdyu-server", tree["server"]), ("rdyu-rog", tree["rog"])], tree["jobs"], out
    )
    sweep = out / "pe_cg" / "sweep"
    assert sorted(p.name for p in sweep.iterdir()) == [
        "in.sweep",
        "job",
        "lmp_info.txt",
        "progress.json",
        "progress.md",
        "run_manifest.json",
    ]
    assert sorted(p.name for p in (sweep / "job").iterdir()) == ["in.sweep", "job.sh"]
    assert (out / "pe_cg" / "sweep_old_20ns_box" / "in.sweep").is_file()
    assert not (out / "pe_cg" / "bench_r1t1").exists()
    assert not (out / "pe_ua" / "smoke_gpu").exists()
    assert not (out / "pe_cg" / ".claude").exists()
    assert not (out / "analysis").exists()
    assert not list(out.rglob("*.dcd")) and not list(out.rglob("log.lammps"))
    # Rog ran pe_ua/prep: its deck wins; lmp_info.txt only exists in the server copy.
    prep = out / "pe_ua" / "prep"
    assert (prep / "in.prep").read_text() == "rog deck\n"
    assert (prep / "lmp_info.txt").read_text() == "info\n"
    index = {(r["system"], r["stage"]): r for r in _rows(out / "index.tsv") if not r["copy"]}
    assert index[("pe_ua", "prep")]["ran_on"] == "rdyu-rog"
    assert index[("pe_ua", "prep")]["sources"] == "rdyu-rog,rdyu-server"
    assert index[("pe_ua", "prep")]["job_deck_matches"] == "no"
    assert index[("pe_cg", "sweep")]["job_deck_matches"] == "yes"
    # Prefix fallback only when the deck matches: sweep_old_20ns_box gets no job/.
    assert not (out / "pe_cg" / "sweep_old_20ns_box" / "job").exists()
    assert (out / "pe_cg" / "extend_job92_cancelled" / "job" / "job.sh").is_file()
    assert index[("pe_cg", "extend_job92_cancelled")]["job"] == "extend_job92"
    assert index[("pe_cg", "extend_job92_cancelled")]["job_deck_matches"] == "yes"
    # Distinct runs are never mixed: the later one is the main copy, no lmp_info borrowed.
    cprep = out / "pe_cg" / "prep"
    assert (cprep / "in.prep").read_text() == "rog run\n"
    assert not (cprep / "lmp_info.txt").exists()
    assert (cprep / "other_run_rdyu-server" / "in.prep").read_text() == "server attempt\n"
    assert (cprep / "other_run_rdyu-server" / "lmp_info.txt").is_file()
    rows = [r for r in _rows(out / "index.tsv") if r["stage"] == "prep" and r["system"] == "pe_cg"]
    assert [(r["copy"], r["ran_on"]) for r in rows] == [
        ("", "rdyu-rog"),
        ("other_run_rdyu-server", "rdyu-server"),
    ]
    assert any("2 different runs" in w for w in s["warnings"])
    assert s["runs"] == 6 and not s["big"]


def test_manifest_rows_and_sha(cs, tree):
    tsv = tree["tmp"] / "m.tsv"
    st = cs.build_manifest(tsv, "rdyu-server", [tree["server"]], [], False)
    rows = _rows(tsv)
    paths = {r["path"]: r for r in rows}
    dcd = "results/runs/pe_cg/sweep/traj.dcd"
    assert paths[dcd]["sha256"] == hashlib.sha256(b"\x00" * 1000).hexdigest()
    assert paths[dcd]["bytes"] == "1000" and paths[dcd]["kind"] == "dcd"
    assert paths["results/runs/pe_cg/sweep/log.lammps"]["kind"] == "log"
    assert paths["results/runs/pe_cg/sweep/screen.out"]["kind"] == "screen"
    assert paths["results/runs/pe_cg/sweep/hold_25C.data"]["kind"] == "data"
    assert not any("restart" in p or "bench_" in p for p in paths)
    assert {r["node"] for r in rows} == {"rdyu-server"}
    assert list(rows[0]) == list(cs.COLUMNS)
    assert st["hashed"] == 5 * 4  # five runs x (dcd, data, log, screen)


def test_skip_existing_reuses_unchanged_rows(cs, tree):
    tsv = tree["tmp"] / "m.tsv"
    cs.build_manifest(tsv, "rdyu-server", [tree["server"]], [], False)
    # Poison one sha: reused only if size+mtime are unchanged.
    rows = _rows(tsv)
    for r in rows:
        r["sha256"] = "reused"
    cs.write_tsv(tsv, rows)
    dcd = tree["server"] / "pe_cg" / "sweep" / "traj.dcd"
    dcd.write_bytes(b"\x01" * 2000)
    os.utime(dcd, (2_000_000_000, 2_000_000_000))
    st = cs.build_manifest(tsv, "rdyu-server", [tree["server"]], [], True)
    assert st["hashed"] == 1 and st["reused"] == 19
    paths = {r["path"]: r for r in _rows(tsv)}
    new = paths["results/runs/pe_cg/sweep/traj.dcd"]
    assert new["sha256"] == hashlib.sha256(b"\x01" * 2000).hexdigest()
    assert new["mtime_utc"] == "2033-05-18T03:33:20Z"
    assert paths["results/runs/pe_cg/sweep/log.lammps"]["sha256"] == "reused"


def test_merge_other_node(cs, tree):
    rog_tsv = tree["tmp"] / "rog.tsv"
    cs.build_manifest(rog_tsv, "rdyu-rog", [tree["rog"]], [], False)
    tsv = tree["tmp"] / "m.tsv"
    cs.build_manifest(tsv, "rdyu-server", [tree["server"]], [rog_tsv], False)
    rows = _rows(tsv)
    nodes = [r["node"] for r in rows]
    assert nodes.count("rdyu-rog") == 8 and nodes.count("rdyu-server") == 20
    # A server rerun keeps the merged rog rows; a new rog TSV replaces them.
    cs.build_manifest(tsv, "rdyu-server", [tree["server"]], [], True)
    assert [r["node"] for r in _rows(tsv)].count("rdyu-rog") == 8
    cs.write_tsv(rog_tsv, _rows(rog_tsv)[:1])
    cs.build_manifest(tsv, "rdyu-server", None, [rog_tsv], False)
    assert [r["node"] for r in _rows(tsv)].count("rdyu-rog") == 1


def test_cli_no_sidecars(cs, tree, capsys):
    tsv = tree["tmp"] / "cli.tsv"
    out = tree["tmp"] / "cliout"
    rc = cs.main(
        [
            "--runs",
            f"rdyu-rog={tree['rog']}",
            "--node-label",
            "rdyu-rog",
            "--no-sidecars",
            "--manifest",
            str(tsv),
            "--out",
            str(out),
            "--jobs",
            str(tree["jobs"]),
        ]
    )
    assert rc == 0 and not out.exists()
    assert len(_rows(tsv)) == 8
    assert "rdyu-rog: 8 rows" in capsys.readouterr().out
