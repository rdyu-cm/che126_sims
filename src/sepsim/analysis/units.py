"""Physical constants and unit conversions for LAMMPS ``units real`` analysis.

Values are CODATA 2018 (Tiesinga et al., Rev. Mod. Phys. 93, 025010 (2021)).
kB, N_A, h and c are exact in the 2019 SI; the atomic mass constant is measured.
LAMMPS ``units real``: energy kcal/mol, length Angstrom, time fs, mass g/mol, T in K.
"""

KB_J_PER_K = 1.380649e-23  # Boltzmann constant, J/K (exact)
AVOGADRO = 6.02214076e23  # 1/mol (exact)
H_J_S = 6.62607015e-34  # Planck constant, J*s (exact)
C_M_PER_S = 299792458.0  # speed of light, m/s (exact)
AMU_KG = 1.66053906660e-27  # atomic mass constant, kg

KCAL_J = 4184.0  # thermochemical kilocalorie, J (the kcal LAMMPS real uses)
KB_KCAL_PER_MOL_K = KB_J_PER_K * AVOGADRO / KCAL_J  # ~1.987204e-3 kcal/(mol K)

ANGSTROM_M = 1e-10  # m per Angstrom
FS_S = 1e-15  # s per fs
A3_CM3 = 1e-24  # cm^3 per Angstrom^3
ANGSTROM_PER_FS_M_PER_S = ANGSTROM_M / FS_S  # 1 Angstrom/fs = 1e5 m/s
THZ_HZ = 1e12  # Hz per THz
THZ_CM1 = THZ_HZ / (C_M_PER_S * 100.0)  # cm^-1 per THz (~33.356)
