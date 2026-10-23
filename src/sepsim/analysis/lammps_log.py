"""Parse thermo output blocks from LAMMPS log files."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_TERMINATOR = "Loop time"


def _is_float(token: str) -> bool:
    try:
        float(token)
    except ValueError:
        return False
    return True


def _is_header(line: str) -> bool:
    tokens = line.split()
    return bool(tokens) and tokens[0] == "Step" and not any(map(_is_float, tokens))


def _parse_row(line: str, ncol: int) -> list[float] | None:
    tokens = line.split()
    if len(tokens) != ncol:
        return None
    try:
        return [float(t) for t in tokens]
    except ValueError:
        return None


def read_thermo(path: str | Path) -> list[dict[str, np.ndarray]]:
    """Read every thermo block (one per ``run``/``minimize``) from a LAMMPS log.

    A block starts at the thermo column header: a line whose first token is
    ``Step`` and whose tokens are all non-numeric (e.g. ``Step Temp Press``).
    The header is used rather than the "Per MPI rank memory allocation" line
    because LAMMPS omits the latter for ``run N pre no`` and for ``run ...
    every`` iterations after the first.
    Rows are lines with the same number of tokens that all parse as floats;
    anything else (WARNINGs, fix output, ...) is skipped. A block ends at
    "Loop time" or at end of file (truncated run). Only one-line thermo styles
    are supported (not ``thermo_style multi``/``yaml``).

    Returns a list with one dict per block mapping column name -> 1-D float array.
    """
    blocks: list[dict[str, np.ndarray]] = []
    header: list[str] | None = None
    rows: list[list[float]] = []

    def close() -> None:
        if header is not None:
            data = np.array(rows, dtype=float).reshape(len(rows), len(header))
            blocks.append({name: data[:, i] for i, name in enumerate(header)})

    with open(path) as fh:
        for line in fh:
            if _is_header(line):
                close()
                header, rows = line.split(), []
            elif header is not None and line.startswith(_TERMINATOR):
                close()
                header = None
            elif header is not None:
                row = _parse_row(line, len(header))
                if row is not None:
                    rows.append(row)
    close()
    return blocks


@dataclass
class LogRun:
    """One ``run``/``minimize`` in a LAMMPS log: its thermo block and timing lines."""

    thermo: dict[str, np.ndarray]  # column name -> 1-D float array
    complete: bool  # closed by "Loop time" (False for the run in progress or a killed one)
    loop_time_s: float | None = None  # wall seconds from the "Loop time" line
    n_steps: int | None = None  # steps from the "Loop time" line
    ns_per_day: float | None = None  # from the "Performance:" line (absent for minimize)
    steps_per_s: float | None = None


@dataclass
class LammpsLog:
    """Result of :func:`read_log`."""

    runs: list[LogRun] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)  # lines starting with "ERROR"


_LOOP = re.compile(r"Loop time of\s+(\S+)\s+on\s+\d+\s+procs\s+for\s+(\d+)\s+steps")
_PERF_NS = re.compile(r"([\d.eE+-]+)\s+ns/day")
_PERF_STEPS = re.compile(r"([\d.eE+-]+)\s+timesteps/s")


def read_log(path: str | Path) -> LammpsLog:
    """Read thermo blocks as :func:`read_thermo` does, plus each run's timing and the errors.

    Each thermo block becomes a :class:`LogRun`; ``complete`` is True once its
    "Loop time" line is seen, which also gives the wall time and step count. A
    following "Performance:" line (MD runs only) gives ns/day and timesteps/s.
    """
    log = LammpsLog()
    header: list[str] | None = None
    rows: list[list[float]] = []

    def close(complete: bool) -> None:
        data = np.array(rows, dtype=float).reshape(len(rows), len(header))
        thermo = {name: data[:, i] for i, name in enumerate(header)}
        log.runs.append(LogRun(thermo=thermo, complete=complete))

    with open(path, errors="replace") as fh:
        for line in fh:
            if _is_header(line):
                if header is not None:
                    close(False)
                header, rows = line.split(), []
            elif header is not None and line.startswith(_TERMINATOR):
                close(True)
                header = None
                m = _LOOP.match(line)
                if m:
                    log.runs[-1].loop_time_s = float(m.group(1))
                    log.runs[-1].n_steps = int(m.group(2))
            elif header is not None:
                row = _parse_row(line, len(header))
                if row is not None:
                    rows.append(row)
            elif line.startswith("Performance:") and log.runs:
                ns, steps = _PERF_NS.search(line), _PERF_STEPS.search(line)
                log.runs[-1].ns_per_day = float(ns.group(1)) if ns else None
                log.runs[-1].steps_per_s = float(steps.group(1)) if steps else None
            if line.startswith("ERROR"):
                log.errors.append(line.strip())
    if header is not None:
        close(False)
    return log
