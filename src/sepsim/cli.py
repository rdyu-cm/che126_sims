"""Command-line entry point for sepsim."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sepsim import __version__
from sepsim.run import run_deck

_NOT_IMPLEMENTED = "sepsim {cmd}: not implemented yet (see docs/decisions.md, Implementation order)"

_BUILD_HELP = "Build system configurations and LAMMPS data files."
_RENDER_HELP = "Render LAMMPS input decks from Jinja templates."
_SUBCOMMANDS = {
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
    pore_help = (
        "Open a dry slit pore in an equilibrated bulk box (D44): molecules made whole, slab"
        " centred, Lz increased by the pore width; x, y, ids, types and topology kept."
    )
    po = kinds.add_parser("pore", help=pore_help, description=pore_help)
    po.add_argument(
        "--data", required=True, help="equilibrated bulk data file (e.g. prep/cooled.data)"
    )
    po.add_argument(
        "--source", required=True, help="bulk system directory holding its manifest.yaml"
    )
    po.add_argument(
        "--width-nm",
        type=float,
        required=True,
        help="nominal (mass-equivalent) pore width in nm: Lz_new = wall + width",
    )
    po.add_argument(
        "--replicate-z",
        type=int,
        default=1,
        help="replicate the bulk box along z before opening (thick wall; default 1)",
    )
    po.add_argument(
        "--data-origin",
        help="where the data file came from, recorded in the manifest"
        " (e.g. rdyu-rog:results/runs/<id>/prep/cooled.data; default: --data as given)",
    )
    po.add_argument("--out", default="systems", help="output root; files go to OUT/<system_id>/")
    render = subparsers.add_parser("render", help=_RENDER_HELP, description=_RENDER_HELP)
    render.set_defaults(render_parser=render)
    protocols = render.add_subparsers(dest="protocol", metavar="protocol")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--system", required=True, help="system directory holding manifest.yaml")
    common.add_argument(
        "--out",
        help="run directory, where LAMMPS runs (default: results/runs/<system_id>/<protocol> under"
        " the current directory); the deck reads the data file by a path relative to it",
    )
    common.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="override a deck parameter (repeatable); the deck header lists every parameter",
    )
    common.add_argument(
        "--preset", choices=["smoke"], help="smoke: ps-scale stages (and ~100 minimize steps)"
    )
    job = common.add_argument_group(
        "Slurm job (D41)",
        "--job writes the deck and job.sh to jobs/<system_id>/<stage>/ (synced by ssubmit;"
        " results/ is not), with the run directory (--out) under results/runs/. Run from the"
        " project root, render before submitting, then: ~/projects/slurm-setup/bin/ssubmit"
        " <project> jobs/<system_id>/<stage>/job.sh. Inputs made by earlier stages exist only"
        " on the node that ran them: pin a system's stages to one node with --node.",
    )
    job.add_argument("--job", action="store_true", help="also write a Slurm job script")
    job.add_argument("--partition", choices=["cpu", "gpu"], help="Slurm partition (default cpu)")
    job.add_argument("--cpus", type=int, help="CPUs for the job, all ranks (default 4)")
    job.add_argument("--ranks", type=int, help="MPI ranks (default: --cpus for mpi, else 1)")
    job.add_argument("--mem", help="memory, always passed to sbatch (default 4G)")
    job.add_argument("--time", help="wall-time limit, required with --job (e.g. 2-00:00:00)")
    job.add_argument("--node", help="pin to one node (sbatch -w), e.g. rdyu-server")
    job.add_argument(
        "--accel",
        choices=["omp", "mpi", "gpu", "kokkos"],
        help="omp: -sf omp (threads per rank = cpus/ranks); mpi: mpirun -np RANKS in the image;"
        " gpu: -sf gpu -pk gpu 1; kokkos: -k on g 1 -sf kk (default: omp on cpu, gpu on gpu)",
    )
    protocol_help = {
        "prep": "Prep deck for an amorphous box: push-off (not CG), minimize, NVT 500 K, NPT"
        " compression, NPT hold, step-cool to 298.15 K (D24, D28, D31). Writes OUT/in.prep.",
        "sweep": "Temperature sweep (D11, D36): NPT 1 atm through 25-160 C, 14 steps + 4 holds"
        " (sweep_grid_c), DCD per segment, write_data at each hold end, AA VDOS NVE"
        " velocity dumps after each hold (D12c, D39), a dense 10 ps burst at 0.1 ps every"
        " 1 ns of each hold (D46). Writes OUT/in.sweep.",
        "benchmark": "Benchmark (D38): NPT 500 K, 1000-step warm-up + 2000 timed steps;"
        " --set ensemble=nve for the dt energy-drift check (100 ps NVE, --set dt_fs=...)."
        " Writes OUT/in.benchmark.",
        "pore": "Dry slit pore (D44): minimize, surface relaxation at 25 C (AA 1 / UA 2 / CG"
        " 5 ns), then the bulk sweep grid with its bursts; NPT on x,y only (couple xy, z fixed), plain LJ"
        " cutoff without tail correction (AA 14 A), thermo adds pxx pyy pzz."
        " Writes OUT/in.pore.",
    }
    data_help = {
        "prep": "data file to start from (default: SYSTEM/data.lmp)",
        "sweep": "data file to start from (default: OUT/../prep/cooled.data)",
        "benchmark": "data file to start from (default: OUT/../prep/compressed.data)",
        "pore": "data file to start from (default: SYSTEM/data.lmp)",
    }
    for name, help_text in protocol_help.items():
        pr = protocols.add_parser(name, help=help_text, description=help_text, parents=[common])
        pr.add_argument("--data", help=data_help[name])
    for name, help_text in _SUBCOMMANDS.items():
        subparsers.add_parser(name, help=help_text, description=help_text)
    prog_help = (
        "Write progress.md, progress.json and PNG plots for run directories (D45): status,"
        " segments done, ns/day, ETA, per-segment means, prep-hold chain checks, cooling vs"
        " heating hysteresis, sweep step vs hold."
    )
    pg = subparsers.add_parser("progress", help=prog_help, description=prog_help)
    pg.set_defaults(progress_parser=pg)
    pg.add_argument("run_dirs", nargs="*", metavar="RUN_DIR", help="run directories")
    pg.add_argument("--all", action="store_true", help="every ROOT/<system>/<stage>/ with a deck")
    pg.add_argument(
        "--root", default="results/runs", help="runs root for --all (default %(default)s)"
    )
    pg.add_argument(
        "--out",
        metavar="DIR",
        help="write to DIR/<system>/<stage>/ instead of into the run directories",
    )
    pg.add_argument(
        "--systems", default="systems", help="system directories root (default %(default)s)"
    )
    pg.add_argument("--summary", metavar="PATH", help="also write one markdown table of all runs")
    pg.add_argument(
        "--collect",
        action="append",
        default=[],
        metavar="DIR",
        help="summarize the progress.json files under DIR (repeatable) instead of the runs"
        " processed here",
    )
    pg.add_argument(
        "--stall-min",
        type=float,
        default=30.0,
        help="minutes without a log update before a run is 'stalled?' (default %(default)s)",
    )
    pg.add_argument("--no-plots", action="store_true", help="skip the PNG plots")
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
    if args.command == "render":
        return _render(args)
    if args.command == "progress":
        return _progress(args)
    print(_NOT_IMPLEMENTED.format(cmd=args.command), file=sys.stderr)
    return 2


def _build(args: argparse.Namespace) -> int:
    if args.kind is None:
        args.build_parser.print_help()
        return 2
    from sepsim.build.amorphous import build_amorphous
    from sepsim.build.growth import GrowthError
    from sepsim.build.pore import build_pore
    from sepsim.build.ua2aa import convert_ua_to_aa

    try:
        if args.kind == "ua2aa":
            sysdir = convert_ua_to_aa(args.data, args.source, out=args.out)
        elif args.kind == "pore":
            sysdir = build_pore(
                args.data,
                args.source,
                args.width_nm,
                replicate_z=args.replicate_z,
                out=args.out,
                data_origin=args.data_origin,
            )
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


def _progress(args: argparse.Namespace) -> int:
    from sepsim import progress as pg

    if not (args.run_dirs or args.all or args.collect):
        args.progress_parser.print_help()
        return 2
    dirs = [Path(d) for d in args.run_dirs]
    if args.all:
        dirs += pg.find_runs(args.root)
    reports, code = [], 0
    for d in dirs:
        try:
            report = pg.progress_report(
                d,
                out=args.out,
                systems=args.systems,
                stall_s=args.stall_min * 60,
                plots=not args.no_plots,
            )
            out_dir = pg.out_dir_for(d, args.out)
            pg.write_report(report, out_dir)
        except Exception as exc:  # noqa: BLE001 - one bad run directory must not stop the loop
            print(f"sepsim progress: {d}: {type(exc).__name__}: {exc}", file=sys.stderr)
            code = 1
            continue
        report["_md"] = str(out_dir / pg.MD_NAME)
        reports.append(report)
        print(f"{out_dir / pg.MD_NAME}: {report['status']}")
    if args.summary:
        if args.collect:
            reports = pg.collect_reports(args.collect)
        path = Path(args.summary)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(pg.summary_markdown(reports, base=path.parent))
        print(path)
    return code


_JOB_OPTS = ("partition", "cpus", "ranks", "mem", "time", "node", "accel")


def _render(args: argparse.Namespace) -> int:
    if args.protocol is None:
        args.render_parser.print_help()
        return 2
    import yaml

    from sepsim.lammps.render import (
        DEFAULT_INPUT,
        RenderError,
        default_data,
        parse_overrides,
        write_deck,
    )
    from sepsim.lammps.slurm import JobError, JobOptions, job_dir_for, write_job

    given = [k for k in _JOB_OPTS if getattr(args, k) is not None]
    if given and not args.job:
        print(f"sepsim render {args.protocol}: error: --{given[0]} needs --job", file=sys.stderr)
        return 1
    try:
        manifest = yaml.safe_load((Path(args.system) / "manifest.yaml").read_text())
        run_dir = Path(args.out or Path("results") / "runs" / manifest["id"] / args.protocol)
        out = run_dir
        if args.job:
            opts = JobOptions(**{k: getattr(args, k) for k in given}).resolved()
            project = Path.cwd().resolve()
            run_dir = run_dir.resolve()
            out = job_dir_for(project, run_dir)
        data = Path(args.data) if args.data else default_data(args.protocol, args.system, run_dir)
        # A defaulted input from an earlier stage may not exist yet (chained jobs).
        missing_ok = args.data is None and args.protocol in DEFAULT_INPUT
        if missing_ok and not data.is_file():
            print(
                f"sepsim render {args.protocol}: warning: {data} does not exist yet"
                " (made by an earlier stage); the deck header records no hash for it",
                file=sys.stderr,
            )
        deck = write_deck(
            args.protocol,
            args.system,
            out,
            data=data,
            overrides=parse_overrides(args.overrides),
            preset=args.preset,
            run_dir=run_dir,
            require_data=not missing_ok,
        )
        print(deck)
        if args.job:
            data_ref = os.path.relpath(data.resolve(), run_dir)
            job = write_job(args.protocol, manifest["id"], project, out, run_dir, data_ref, opts)
            print(job)
    except (RenderError, JobError, OSError, KeyError, yaml.YAMLError) as exc:
        print(f"sepsim render {args.protocol}: error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
