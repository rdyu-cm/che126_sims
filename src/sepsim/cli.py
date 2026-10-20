"""Command-line entry point for sepsim."""

from __future__ import annotations

import argparse
import sys

from sepsim import __version__
from sepsim.run import run_deck

_NOT_IMPLEMENTED = "sepsim {cmd}: not implemented yet (see docs/decisions.md, Implementation order)"

_BUILD_HELP = "Build system configurations and LAMMPS data files."
_SUBCOMMANDS = {
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
    build = subparsers.add_parser("build", help=_BUILD_HELP, description=_BUILD_HELP)
    build.set_defaults(build_parser=build)
    kinds = build.add_subparsers(dest="kind", metavar="kind")
    amorph_help = "Grow an amorphous PE/iPP box and write data.lmp + manifest.yaml."
    am = kinds.add_parser("amorphous", help=amorph_help, description=amorph_help)
    am.add_argument("--polymer", required=True, choices=["pe", "ipp"])
    am.add_argument("--res", required=True, choices=["aa", "ua", "cg"], help="resolution")
    am.add_argument("--chains", type=int, default=40, help="number of chains (default 40)")
    am.add_argument("--carbons", type=int, default=240, help="carbons per chain (default 240)")
    am.add_argument(
        "--density", type=float, default=0.3, help="build density in g/cm^3 (default 0.3)"
    )
    am.add_argument("--seed", type=int, default=1, help="random seed (default 1)")
    am.add_argument("--out", default="systems", help="output root; files go to OUT/<system_id>/")
    conv_help = "Convert a relaxed UA PE/iPP box to all-atom by adding hydrogens (D32)."
    cv = kinds.add_parser("ua2aa", help=conv_help, description=conv_help)
    cv.add_argument("--data", required=True, help="relaxed UA data file (LAMMPS write_data)")
    cv.add_argument("--source", required=True, help="UA system directory holding its manifest.yaml")
    cv.add_argument("--out", default="systems", help="output root; files go to OUT/<system_id>/")
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
        " its first lmp*/lammps* token (else its first token) is queried with `info configuration`",
    )
    run.add_argument(
        "--lmp-probe",
        metavar="CMD",
        help="command queried with `info configuration` for the manifest, for wrappers and containers, e.g."
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
    if args.command == "build":
        return _build(args)
    print(_NOT_IMPLEMENTED.format(cmd=args.command), file=sys.stderr)
    return 2


def _build(args: argparse.Namespace) -> int:
    if args.kind is None:
        args.build_parser.print_help()
        return 2
    from sepsim.build.amorphous import build_amorphous
    from sepsim.build.growth import GrowthError
    from sepsim.build.ua2aa import convert_ua_to_aa

    try:
        if args.kind == "ua2aa":
            sysdir = convert_ua_to_aa(args.data, args.source, out=args.out)
        else:
            sysdir = build_amorphous(
                args.polymer,
                args.res,
                n_chains=args.chains,
                n_carbons=args.carbons,
                density=args.density,
                seed=args.seed,
                out=args.out,
            )
    except (GrowthError, ValueError, OSError) as exc:  # TopologyError is a ValueError
        print(f"sepsim build {args.kind}: error: {exc}", file=sys.stderr)
        return 1
    print(sysdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
