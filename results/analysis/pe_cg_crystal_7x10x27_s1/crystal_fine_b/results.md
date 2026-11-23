# Crystal analysis: pe_cg_crystal_7x10x27_s1 / crystal_fine_b

- system: `pe_cg_crystal_7x10x27_s1` (cg); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_cg_crystal_7x10x27_s1/crystal_fine_b` (status finished, node rdyu-server, run code commit b969a5e8c3)
- analysis: `sepsim analyze crystal` (D59), code commit 8b68bd2293 (dirty), 2026-11-23 17:44 on rdyu-server
- 140 stems x 27 sites, 7 x 10 x 27 repeats of pe_orthorhombic_busing (a 7.4069, b 4.9491, c 2.5511 Å at 23 °C, 0.9963 g/cm³, 18.33 Å² per chain)
- crystallinity: D26 local P2 with ring chords, r_c 6.31 Å, threshold 0.745 (**calibrated (calibration_cg_pe.json, 2026-11-17)**); stable hold: last frame fraction ≥ 0.8 and stem P2 ≥ 0.8

## Holds

Thermo after the first 10% of each hold (mean ± SEM). a = Lx/na, b = Ly/nb, c = Lz/nz (CG: rise per bead; UA: the 2-CH2 repeat). ρ/ρ_exp and A/A_exp against the Busing cell (0.9963 g/cm³, 18.33 Å²).

| T (°C) | a (Å) | b (Å) | c (Å) | a/b | ρ (g/cm³) | ρ/ρ_exp | A/chain (Å²) | A/A_exp | drift | crystalline (mean; first → last) | stem P2 (last) | largest cluster (last) | stable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 75.0 | 8.8237 ± 0.0005 | 5.0932 ± 0.0002 | 3.4484 ± 0.0001 | 1.732 | 0.9018 ± 0.0000 | 0.905 | 22.47 ± 0.00 | 1.226 | a_A, a_over_b | 1.000; 1.000 → 1.000 | 0.964 | 1.000 | True |
| 85.0 | 8.8576 ± 0.0004 | 5.1128 ± 0.0003 | 3.4421 ± 0.0002 | 1.732 | 0.8965 ± 0.0000 | 0.900 | 22.64 ± 0.00 | 1.235 | none | 0.999; 1.000 → 0.999 | 0.962 | 0.999 | True |
| 100.0 | 8.9107 ± 0.0005 | 5.1438 ± 0.0003 | 3.4322 ± 0.0002 | 1.732 | 0.8884 ± 0.0000 | 0.892 | 22.92 ± 0.00 | 1.250 | none | 0.999; 0.999 → 0.999 | 0.961 | 0.999 | True |
| 110.0 | 8.9475 ± 0.0006 | 5.1655 ± 0.0004 | 3.4249 ± 0.0003 | 1.732 | 0.8829 ± 0.0000 | 0.886 | 23.11 ± 0.00 | 1.261 | none | 0.998; 0.999 → 0.998 | 0.950 | 0.998 | True |

## Thermal expansion (stable holds)

Holds 75, 85, 100, 110 °C; α = d ln L/dT, OLS.

| quantity | α (10⁻⁴ K⁻¹) |
|---|---|
| a | 3.985 ± 0.039 |
| b | 4.035 ± 0.049 |
| c | -1.954 ± 0.041 |
| V | 6.064 ± 0.050 |

## Elastic constants (strain fluctuations)

Per hold (after the first 10%): ε_i = (L_i − ⟨L_i⟩)/⟨L_i⟩, S_ij = ⟨V⟩⟨ε_i ε_j⟩/(k_B T) with T the set point, over the normal strains of the orthogonal box (shear fixed; normal–shear couplings assumed zero by symmetry); E_i = 1/S_ii, ν_ij = −S_ij/S_ii, C = S⁻¹. ± is the bootstrap standard error over 100-row blocks (1000 draws). Rate-free (static, isothermal) constants; x, y transverse, z along the stems.

| T (°C) | blocks | E_x (GPa) | E_y (GPa) | E_z (GPa) | ν_xy | ν_yx | ν_xz | ν_yz | C11 | C22 | C33 | C12 | C13 | C23 | stable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 75 | 90 | 1.72 ± 0.05 | 1.72 ± 0.06 | 6.03 ± 0.15 | 0.183 ± 0.025 | 0.183 ± 0.023 | 0.155 ± 0.007 | 0.154 ± 0.006 | 2.0 ± 0.0 | 2.0 ± 0.0 | 7.6 ± 0.2 | 0.6 ± 0.0 | 1.4 ± 0.1 | 1.4 ± 0.1 | True |
| 85 | 90 | 1.64 ± 0.06 | 1.70 ± 0.05 | 5.50 ± 0.15 | 0.223 ± 0.024 | 0.232 ± 0.025 | 0.152 ± 0.008 | 0.162 ± 0.008 | 2.0 ± 0.1 | 2.1 ± 0.0 | 7.0 ± 0.2 | 0.7 ± 0.0 | 1.4 ± 0.1 | 1.4 ± 0.1 | True |
| 100 | 90 | 1.51 ± 0.05 | 1.54 ± 0.05 | 4.89 ± 0.14 | 0.175 ± 0.032 | 0.179 ± 0.031 | 0.176 ± 0.009 | 0.180 ± 0.011 | 1.9 ± 0.0 | 1.9 ± 0.0 | 6.5 ± 0.2 | 0.6 ± 0.1 | 1.4 ± 0.1 | 1.4 ± 0.1 | True |
| 110 | 90 | 1.31 ± 0.04 | 1.38 ± 0.05 | 4.40 ± 0.19 | 0.205 ± 0.027 | 0.217 ± 0.028 | 0.185 ± 0.012 | 0.188 ± 0.009 | 1.7 ± 0.0 | 1.8 ± 0.0 | 6.2 ± 0.2 | 0.6 ± 0.0 | 1.4 ± 0.1 | 1.5 ± 0.1 | True |

Halves check: E from the first vs the second half of the window (each with its own bootstrap error); **flag** when they differ by more than 2σ.

| T (°C) | E_x 1st → 2nd | E_y 1st → 2nd | E_z 1st → 2nd | flagged |
|---|---|---|---|---|
| 75 | 1.72 ± 0.06 → 1.72 ± 0.07 | 1.65 ± 0.08 → 1.79 ± 0.08 | 6.12 ± 0.20 → 5.94 ± 0.22 | none |
| 85 | 1.64 ± 0.08 → 1.63 ± 0.07 | 1.73 ± 0.07 → 1.68 ± 0.07 | 5.34 ± 0.21 → 5.67 ± 0.21 | none |
| 100 | 1.51 ± 0.07 → 1.52 ± 0.07 | 1.59 ± 0.07 → 1.50 ± 0.07 | 4.72 ± 0.19 → 5.08 ± 0.19 | none |
| 110 | 1.26 ± 0.05 → 1.36 ± 0.07 | 1.35 ± 0.06 → 1.42 ± 0.07 | 4.28 ± 0.31 → 4.52 ± 0.18 | none |

## Caveats

- A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E_app; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- E_z is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

## Plots

**cell lengths and density per hold**

![cell lengths and density per hold](cell.png)

**crystallinity and stem P2**

![crystallinity and stem P2](order.png)

**elastic moduli from strain fluctuations**

![elastic moduli from strain fluctuations](elastic.png)

