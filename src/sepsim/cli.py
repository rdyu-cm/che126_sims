"""Command-line entry point for sepsim."""

from __future__ import annotations

import argparse
import sys

from sepsim import __version__
from sepsim.run import run_deck

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
    run_help = "Run a LAMMPS deck with `lmp` and write run_manifest.json."
    run = subparsers.add_parser(
        "run",
        help=run_help,
        description=run_help + " Arguments after `--` are passed to LAMMPS.",
        usage="%(prog)s DECK [--workdir DIR] [--lmp CMD] [--lmp-probe CMD] [--dry-run] [-- EXTRA_LMP_ARGS...]",
    )
    run.add_argument("deck", metavar="DECK", help="LAMMPS input deck")
    run.add_argument(
        "--workdir", metavar="DIR", help="directory to run in (default: the deck's directory)"
    )
    run.add_argument(
        "--lmp",
        metavar="CMD",
        help='launch command, e.g. "mpirun -np 8 lmp -sf gpu" (default: $SEPSIM_LMP or lmp);'
        " its first lmp*/lammps* token (else its first token) is queried with -h",
    )
    run.add_argument(
        "--lmp-probe",
        metavar="CMD",
        help="command queried with -h for the manifest, for wrappers and containers, e.g."
        ' "apptainer exec --rocm img.sif lmp" (default: $SEPSIM_LMP_PROBE)',
    )
    run.add_argument(
        "--dry-run", action="store_true", help="write the manifest and print the command only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the sepsim CLI and return a process exit code."""
    parser = build_parser()
    argv = list(sys.argv[1:] if argv is None else argv)
    extra: list[str] = []
    if "--" in argv:
        cut = argv.index("--")
        argv, extra = argv[:cut], argv[cut + 1 :]
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    if args.command == "run":
        return run_deck(
            args.deck,
            workdir=args.workdir,
            lmp=args.lmp,
            extra_args=extra,
            dry_run=args.dry_run,
            lmp_probe=args.lmp_probe,
        )
    if extra:
        parser.error("arguments after `--` are only accepted by `sepsim run`")
    print(_NOT_IMPLEMENTED.format(cmd=args.command), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
