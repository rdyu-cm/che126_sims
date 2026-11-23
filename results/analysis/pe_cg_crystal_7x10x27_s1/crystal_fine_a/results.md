# Crystal analysis: pe_cg_crystal_7x10x27_s1 / crystal_fine_a

- system: `pe_cg_crystal_7x10x27_s1` (cg); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_cg_crystal_7x10x27_s1/crystal_fine_a` (status finished, node rdyu-server, run code commit b969a5e8c3)
- analysis: `sepsim analyze crystal` (D59), code commit a3fc627969, 2026-11-22 16:03 on rdyu-server
- 140 stems x 27 sites, 7 x 10 x 27 repeats of pe_orthorhombic_busing (a 7.4069, b 4.9491, c 2.5511 Å at 23 °C, 0.9963 g/cm³, 18.33 Å² per chain)
- crystallinity: D26 local P2 with ring chords, r_c 6.31 Å, threshold 0.745 (**calibrated (calibration_cg_pe.json, 2026-11-17)**); stable hold: last frame fraction ≥ 0.8 and stem P2 ≥ 0.8

## Holds

Thermo after the first 10% of each hold (mean ± SEM). a = Lx/na, b = Ly/nb, c = Lz/nz (CG: rise per bead; UA: the 2-CH2 repeat). ρ/ρ_exp and A/A_exp against the Busing cell (0.9963 g/cm³, 18.33 Å²).

| T (°C) | a (Å) | b (Å) | c (Å) | a/b | ρ (g/cm³) | ρ/ρ_exp | A/chain (Å²) | A/A_exp | drift | crystalline (mean; first → last) | stem P2 (last) | largest cluster (last) | stable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 35.0 | 8.6974 ± 0.0004 | 5.0208 ± 0.0002 | 3.4709 ± 0.0001 | 1.732 | 0.9221 ± 0.0000 | 0.926 | 21.83 ± 0.00 | 1.191 | a_A, a_over_b | 1.000; 1.000 → 1.000 | 0.970 | 1.000 | True |
| 45.0 | 8.7276 ± 0.0003 | 5.0382 ± 0.0002 | 3.4655 ± 0.0001 | 1.732 | 0.9171 ± 0.0000 | 0.921 | 21.99 ± 0.00 | 1.200 | none | 1.000; 1.000 → 1.000 | 0.970 | 1.000 | True |
| 55.1 | 8.7588 ± 0.0004 | 5.0557 ± 0.0003 | 3.4601 ± 0.0002 | 1.732 | 0.9121 ± 0.0000 | 0.916 | 22.14 ± 0.00 | 1.208 | none | 1.000; 1.000 → 1.000 | 0.968 | 1.000 | True |
| 65.0 | 8.7909 ± 0.0005 | 5.0738 ± 0.0003 | 3.4545 ± 0.0002 | 1.733 | 0.9070 ± 0.0000 | 0.910 | 22.30 ± 0.00 | 1.217 | none | 1.000; 1.000 → 1.000 | 0.964 | 1.000 | True |

## Thermal expansion (stable holds)

Holds 35, 45, 55, 65 °C; α = d ln L/dT, OLS.

| quantity | α (10⁻⁴ K⁻¹) |
|---|---|
| a | 3.559 ± 0.042 |
| b | 3.494 ± 0.028 |
| c | -1.570 ± 0.018 |
| V | 5.482 ± 0.051 |

## Caveats

- A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.

## Plots

**cell lengths and density per hold**

![cell lengths and density per hold](cell.png)

**crystallinity and stem P2**

![crystallinity and stem P2](order.png)

