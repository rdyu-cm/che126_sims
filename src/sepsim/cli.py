"""Command-line entry point for sepsim."""

from __future__ import annotations

import argparse
import sys

from sepsim import __version__

_NOT_IMPLEMENTED = "sepsim {cmd}: not implemented yet (see docs/decisions.md, Implementation order)"

_SUBCOMMANDS = {
    "build": "Build system configurations and LAMMPS data files.",
    "render": "Render LAMMPS input decks from Jinja templates.",
    "analyze": "Analyze trajectories and thermo output.",
}


def build_parser() -> argparse.ArgumentParser:
    """Return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="sepsim",
        description="LAMMPS MD tooling for PE/PP battery separators.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    for name, help_text in _SUBCOMMANDS.items():
        subparsers.add_parser(name, help=help_text, description=help_text)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the sepsim CLI and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    print(_NOT_IMPLEMENTED.format(cmd=args.command), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
