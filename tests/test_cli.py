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


@pytest.mark.parametrize("command", ["build", "render", "analyze"])
def test_subcommands_are_stubs(command, capsys):
    """Each subcommand is a stub: exit code 2 and a message on stderr."""
    assert main([command]) == 2
    assert "not implemented yet" in capsys.readouterr().err


def test_no_arguments_prints_help(capsys):
    """With no subcommand the CLI prints help and returns 2."""
    assert main([]) == 2
    assert "usage: sepsim" in capsys.readouterr().out
