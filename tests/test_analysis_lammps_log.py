"""Tests for the LAMMPS log thermo parser."""

import numpy as np

from sepsim.analysis.lammps_log import read_thermo

LOG = """LAMMPS (2 Aug 2023)
units real
Per MPI rank memory allocation (min/avg/max) = 5.1 | 5.1 | 5.1 Mbytes
   Step          Temp          Volume
         0   300            1000.5
        10   301.5          1001.0
WARNING: Bond/angle/dihedral extent > half of periodic box length (src/domain.cpp:1)
        20   302            1001.5
Loop time of 1.23 on 4 procs for 20 steps with 100 atoms

Performance: 1.0 ns/day
fix 2 all npt temp 300 400 100 iso 1 1 1000
Per MPI rank memory allocation (min/avg/max) = 5.2 | 5.2 | 5.2 Mbytes
Step Temp Press Enthalpy
        20   302   1.0  -100.0
        30   350   -2.5e+01  -90.0
Loop time of 2.0 on 4 procs for 10 steps with 100 atoms
Total wall time: 0:00:03
"""


def test_two_runs_with_warning(tmp_path):
    path = tmp_path / "log.lammps"
    path.write_text(LOG)
    blocks = read_thermo(path)
    assert len(blocks) == 2
    assert list(blocks[0]) == ["Step", "Temp", "Volume"]
    np.testing.assert_array_equal(blocks[0]["Step"], [0, 10, 20])
    np.testing.assert_allclose(blocks[0]["Volume"], [1000.5, 1001.0, 1001.5])
    assert list(blocks[1]) == ["Step", "Temp", "Press", "Enthalpy"]
    np.testing.assert_allclose(blocks[1]["Press"], [1.0, -25.0])
    np.testing.assert_allclose(blocks[1]["Enthalpy"], [-100.0, -90.0])


def test_truncated_run_kept(tmp_path):
    path = tmp_path / "log.lammps"
    path.write_text(LOG.split("Loop time of 2.0")[0])
    blocks = read_thermo(path)
    assert len(blocks) == 2
    np.testing.assert_array_equal(blocks[1]["Step"], [20, 30])
