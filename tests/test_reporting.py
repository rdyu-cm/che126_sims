import numpy as np

from sepsim.reporting import (
    _f,
    _pm,
    dump_json,
    header_markdown,
    plots_markdown,
    trajectory_or_note,
    write_atomic,
)


def test_number_formatting():
    assert _pm(None, ".2f") == "" and _pm({}, ".2f") == ""
    assert _pm({"mean": 1.234, "sem": None}, ".2f") == "1.23"
    assert _pm({"mean": 1.234, "sem": 0.0112}, ".2f") == "1.23 ± 0.01"
    assert _f(None) == "n/a" and _f(1.234) == "1.23" and _f(1.25, ".1f") == "1.2"


def test_plots_and_header_markdown():
    assert plots_markdown(None) == [] and plots_markdown({}) == []
    assert plots_markdown({"a": {"file": "a.png", "title": "A"}}) == [
        "",
        "## Plots",
        "",
        "**A**",
        "",
        "![A](a.png)",
        "",
    ]
    r = {
        "system": "s",
        "stage": "extend",
        "resolution": "cg",
        "run_dir": "/r",
        "run_status": "finished",
        "run_node": "n",
        "run_git": {"commit": "0123456789abc"},
        "code_git": {"commit": "abcdef0123456", "dirty": True},
        "generated": "2026-11-06T10:20:30+00:00",
        "generated_on": "host",
    }
    assert header_markdown(r, "Hold analysis", "hold", "D56", "extend, ") == [
        "# Hold analysis: s / extend",
        "",
        (
            "- system: `s` (cg); source run directory `/r` (extend, status finished, node n,"
            " run code commit 0123456789)"
        ),
        (
            "- analysis: `sepsim analyze hold` (D56), code commit abcdef0123 (dirty),"
            " 2026-11-06 10:20 on host"
        ),
    ]
    r["run_git"] = r["code_git"] = None
    assert header_markdown(r, "Sweep analysis", "sweep", "D49")[2:] == [
        (
            "- system: `s` (cg); source run directory `/r` (status finished, node n, run code"
            " commit n/a)"
        ),
        "- analysis: `sepsim analyze sweep` (D49), code commit n/a, 2026-11-06 10:20 on host",
    ]


def test_json_and_atomic_write(tmp_path):
    assert dump_json({"b": np.float64(1.5), "a": np.arange(2)}) == (
        '{\n "a": [\n  0,\n  1\n ],\n "b": 1.5\n}\n'
    )
    write_atomic(tmp_path / "o", (("x.json", "{}\n"), ("x.md", "# x\n")))
    assert (tmp_path / "o" / "x.md").read_text() == "# x\n"
    assert sorted(p.name for p in (tmp_path / "o").iterdir()) == ["x.json", "x.md"]


def test_trajectory_or_note():
    def ok():
        return {"available": True}

    def boom():
        raise ValueError("boom")

    assert trajectory_or_note(True, {}, True, "hold", ok) == {"available": True}
    notes = [
        trajectory_or_note(False, {}, True, "hold", ok)["notes"],
        trajectory_or_note(True, None, True, "hold", ok)["notes"],
        trajectory_or_note(True, {}, False, "step", ok)["notes"],
        trajectory_or_note(True, {}, True, "hold", boom)["notes"],
    ]
    assert notes == [
        ["trajectory analysis skipped (--no-traj)"],
        ["trajectory not available (no system)"],
        ["step not complete"],
        ["trajectory failed: boom"],
    ]
