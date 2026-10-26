"""Tests for the sepsim command-line interface."""

import pytest

from sepsim import __version__
from sepsim.cli import main


def test_version_flag_prints_version(capsys):
    """`sepsim --version` exits 0 and prints the package version."""
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_analyze_without_analysis_prints_help(capsys):
    """`sepsim analyze` alone prints the analyze help and returns 2."""
    assert main(["analyze"]) == 2
    assert "sweep" in capsys.readouterr().out


def test_build_without_kind_prints_help(capsys):
    """`sepsim build` alone prints the build help and returns 2."""
    assert main(["build"]) == 2
    assert "amorphous" in capsys.readouterr().out


def test_render_without_protocol_prints_help(capsys):
    """`sepsim render` alone prints the render help and returns 2."""
    assert main(["render"]) == 2
    assert "prep" in capsys.readouterr().out


def test_no_arguments_prints_help(capsys):
    """With no subcommand the CLI prints help and returns 2."""
    assert main([]) == 2
    assert "usage: sepsim" in capsys.readouterr().out
