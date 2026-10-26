"""Slurm job scripts for rendered decks on the two-node cluster (D41).

There is no shared filesystem: ``ssubmit`` mirrors the project to the other node except
the contents of ``results/`` and ``logs/``. So a job's deck must live outside
``results/``: ``sepsim render <protocol> --job`` writes the deck and ``job.sh`` to
``jobs/<system>/<stage>/`` (gitignored, synced by ``ssubmit``), and the job copies the
deck into its run directory ``results/runs/<system>/<stage>/`` (outputs, fetched by
``scollect``) and runs it there through ``sepsim run`` (``run_manifest.json``). Paths
in the deck are relative to the run directory; paths in ``job.sh`` are absolute (the
project has the same absolute path on every node).

LAMMPS runs from the Apptainer image (``$SEPSIM_SIF``) with one of four accelerator
modes. MPI runs ``mpirun`` inside the container; ``srun --mpi=pmix`` is not used
because the container's OpenMPI against the host's pmix is unverified.
"""

from __future__ import annotations

import math
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from sepsim import __version__

PARTITIONS = ("cpu", "gpu")
ACCELS = ("omp", "mpi", "gpu", "kokkos")
GPU_ACCELS = ("gpu", "kokkos")
DEFAULT_SIF = (
    "$HOME/projects/installations/lammps/stable_22Jul2025_update6/lammps-rocm6.4.4-gfx1030.sif"
)
SSUBMIT = "~/projects/slurm-setup/bin/ssubmit"
JOB_NAME = "job.sh"
_MEM = re.compile(r"^[1-9][0-9]*[KMGT]?$")


class JobError(ValueError):
    """Inconsistent job options or layout."""


def default_mem(n_atoms: int, ranks: int = 1) -> str:
    """Slurm memory for a run of ``n_atoms`` on ``ranks`` MPI ranks: about twice an estimate of
    100 MB + 15 kB/atom per rank plus 200 MB for the job wrapper, in whole GB, at least 1G.
    Measured resident sizes (2026-10-26): CG C240 pore 3,200 atoms 70 MB; PE UA 9,600 atoms
    85 MB per rank (2 ranks); iPP UA 12,760 atoms 135 MB; CG C1500 20,000 atoms KOKKOS 290 MB."""
    est_mb = ranks * (100 + 0.015 * n_atoms) + 200
    return f"{max(1, math.ceil(2 * est_mb / 1024))}G"


@dataclass
class JobOptions:
    partition: str = "cpu"
    cpus: int = 4
    mem: str | None = None  # default: default_mem(n_atoms, ranks)
    time: str = ""
    node: str | None = None
    accel: str | None = None  # default: omp on cpu, gpu on gpu
    ranks: int | None = None  # default: cpus for mpi, else 1

    def resolved(self, n_atoms: int | None = None) -> JobOptions:
        """Fill defaults and check consistency (``n_atoms`` sizes the default memory)."""
        if self.partition not in PARTITIONS:
            raise JobError(f"partition {self.partition!r} not in {', '.join(PARTITIONS)}")
        accel = self.accel or ("gpu" if self.partition == "gpu" else "omp")
        if accel not in ACCELS:
            raise JobError(f"accel {accel!r} not in {', '.join(ACCELS)}")
        if (accel in GPU_ACCELS) != (self.partition == "gpu"):
            raise JobError(
                f"--accel {accel} needs --partition {'gpu' if accel in GPU_ACCELS else 'cpu'}"
                " (gpu and kokkos run on the gpu partition, omp and mpi on cpu)"
            )
        if self.cpus < 1:
            raise JobError("--cpus must be >= 1")
        ranks = self.ranks if self.ranks is not None else (self.cpus if accel == "mpi" else 1)
        if ranks < 1 or self.cpus % ranks:
            raise JobError(f"--ranks {ranks} must divide --cpus {self.cpus}")
        if accel == "kokkos" and ranks != 1:
            raise JobError("--accel kokkos runs 1 rank (no GPU-aware MPI in the image)")
        mem = self.mem or (default_mem(n_atoms, ranks) if n_atoms else "4G")
        if not _MEM.match(mem):
            raise JobError(f"--mem {mem!r}: expected e.g. 4G or 4000M")
        if not self.time or any(c.isspace() for c in self.time):
            raise JobError("--time is required with --job (e.g. 2-00:00:00 or 12:00:00)")
        if self.node is not None and not re.match(r"^[A-Za-z0-9_.-]+$", self.node):
            raise JobError(f"--node {self.node!r}: expected one node name")
        return JobOptions(self.partition, self.cpus, mem, self.time, self.node, accel, ranks)


def job_dir_for(project: Path, run_dir: Path) -> Path:
    """``<project>/results/runs/<rest>`` -> ``<project>/jobs/<rest>`` (absolute)."""
    runs = project / "results" / "runs"
    try:
        rest = run_dir.relative_to(runs)
    except ValueError:
        raise JobError(
            f"with --job the run directory must be under {runs} (scollect fetches results/),"
            f" got {run_dir}"
        ) from None
    if not rest.parts:
        raise JobError(f"run directory {run_dir} must be below {runs}")
    return project / "jobs" / rest


def lammps_commands(opts: JobOptions) -> tuple[str, str]:
    """(launch command, probe command) with ``$SEPSIM_SIF`` left for the shell."""
    rocm = " --rocm" if opts.partition == "gpu" else ""
    exe = f"apptainer exec{rocm} $SEPSIM_SIF"  # sepsim run splits it (no spaces, checked)
    threads = opts.cpus // opts.ranks
    mpi = ""
    if opts.ranks > 1:
        # inside the container; no binding when a rank runs several threads
        mpi = f"mpirun -np {opts.ranks}" + (" --bind-to none" if threads > 1 else "") + " "
    sfx = {
        "omp": f" -sf omp -pk omp {threads}",
        "mpi": "",
        "gpu": " -sf gpu -pk gpu 1",
        "kokkos": " -k on g 1 -sf kk -pk kokkos newton on neigh half",
    }[opts.accel]
    return f"{exe} {mpi}lmp{sfx}", f"{exe} lmp"


def job_script(
    protocol: str,
    system_id: str,
    project: Path,
    job_dir: Path,
    run_dir: Path,
    data_ref: str,
    opts: JobOptions,
) -> str:
    """Text of ``job.sh`` (``opts`` must be ``resolved()``)."""
    deck = f"in.{protocol}"
    stage = run_dir.name
    threads = opts.cpus // opts.ranks
    lmp, probe = lammps_commands(opts)
    q = shlex.quote
    rel_job = job_dir.relative_to(project) / JOB_NAME
    node_hint = f" (pinned to {opts.node})" if opts.node else ""
    sb = [
        f"--job-name={system_id}-{stage}",
        f"--partition={opts.partition}",
        "--nodes=1",
        f"--ntasks={opts.ranks}",
        f"--cpus-per-task={threads}",
        f"--mem={opts.mem}",
        f"--time={opts.time}",
        "--no-requeue",  # a requeued job would restart from scratch over the first attempt
    ]
    if opts.partition == "gpu":
        sb.append("--gres=gpu:1")
    if opts.node:
        sb.append(f"--nodelist={opts.node}")
    sb.append(f"--output={project}/logs/%x-%j-%N.out")
    lines = ["#!/bin/bash", *(f"#SBATCH {s}" for s in sb)]
    lines += [
        (
            f"# sepsim {__version__} job: {protocol} for {system_id}{node_hint},"
            f" {opts.accel}, {opts.ranks} rank(s) x {threads} thread(s)"
        ),
        "# Submit from rdyu-server in the project root (ssubmit syncs jobs/, not results/):",
        f"#   {SSUBMIT} {project} {rel_job}",
        "# Fetch outputs afterwards: ~/projects/slurm-setup/bin/scollect " + str(project),
        "# Inputs under results/ (earlier stages) exist only on the node that made them:",
        "# keep a system's stages on one node (--node / -w).",
        "set -euo pipefail",
        f"REPO={q(str(project))}",
        f"JOB_DIR={q(str(job_dir))}",
        f"RUN_DIR={q(str(run_dir))}",
        f'SEPSIM_SIF="${{SEPSIM_SIF:-{DEFAULT_SIF}}}"',
        'command -v uv >/dev/null || export PATH="$HOME/.local/bin:$PATH"',
        "",
        'if [ ! -f "$SEPSIM_SIF" ] || [[ "$SEPSIM_SIF" =~ [[:space:]] ]]; then',
        '    echo "error: LAMMPS image not found or path has spaces: $SEPSIM_SIF" >&2',
        "    exit 1",
        "fi",
        'mkdir -p "$RUN_DIR"',
        'cd "$RUN_DIR"',
        'if [ -f run_manifest.json ] && grep -q \'"status": "finished"\' run_manifest.json; then',
        '    echo "error: $RUN_DIR already holds a finished run; move it away to rerun" >&2',
        "    exit 1",
        "fi",
        f'cp "$JOB_DIR/{deck}" {deck}',
        f"if [ ! -f {q(data_ref)} ]; then",
        (
            f'    echo "error: input data {data_ref} (relative to $RUN_DIR) not found on'
            ' $(hostname -s); run the earlier stage on this node (--node)" >&2'
        ),
        "    exit 1",
        "fi",
        f"export OMP_NUM_THREADS={threads}",
    ]
    if opts.partition == "gpu":
        lines += [
            "# Slurm sets ROCR_VISIBLE_DEVICES=0 (the RX 6800S); gfx1032 runs as gfx1030 (D23)",
            "export HSA_OVERRIDE_GFX_VERSION=10.3.0",
        ]
    lines += [
        'echo "job ${SLURM_JOB_ID:-none} on $(hostname -s) in $RUN_DIR, started $(date -Is)"',
        f'exec uv run --frozen --project "$REPO" sepsim run {deck} \\',
        f'    --lmp "{lmp}" \\',
        f'    --lmp-probe "{probe}"',
    ]
    return "\n".join(lines) + "\n"


def write_job(
    protocol: str,
    system_id: str,
    project: Path,
    job_dir: Path,
    run_dir: Path,
    data_ref: str,
    opts: JobOptions,
) -> Path:
    """Write ``job_dir/job.sh`` (executable); return its path."""
    text = job_script(protocol, system_id, project, job_dir, run_dir, data_ref, opts)
    job_dir.mkdir(parents=True, exist_ok=True)
    path = job_dir / JOB_NAME
    path.write_text(text, newline="\n")
    path.chmod(0o755)
    return path
