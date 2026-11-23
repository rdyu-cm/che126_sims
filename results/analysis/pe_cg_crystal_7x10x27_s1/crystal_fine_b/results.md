# Crystal analysis: pe_cg_crystal_7x10x27_s1 / crystal_fine_b

- system: `pe_cg_crystal_7x10x27_s1` (cg); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_cg_crystal_7x10x27_s1/crystal_fine_b` (status finished, node rdyu-server, run code commit b969a5e8c3)
- analysis: `sepsim analyze crystal` (D59), code commit a3fc627969 (dirty), 2026-11-22 16:03 on rdyu-server
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

## Caveats

- A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.

## Plots

**cell lengths and density per hold**

![cell lengths and density per hold](cell.png)

**crystallinity and stem P2**

![crystallinity and stem P2](order.png)

