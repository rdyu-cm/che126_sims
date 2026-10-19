"""Parse thermo output blocks from LAMMPS log files."""

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
