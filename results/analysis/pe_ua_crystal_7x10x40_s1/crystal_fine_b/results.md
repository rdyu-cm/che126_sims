# Crystal analysis: pe_ua_crystal_7x10x40_s1 / crystal_fine_b

- system: `pe_ua_crystal_7x10x40_s1` (ua); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_ua_crystal_7x10x40_s1/crystal_fine_b` (status finished, node rdyu-rog, run code commit b969a5e8c3)
- analysis: `sepsim analyze crystal` (D59), code commit b969a5e8c3 (dirty), 2026-11-21 10:26 on rdyu-rog
- 140 stems x 80 sites, 7 x 10 x 40 repeats of pe_orthorhombic_busing (a 7.4069, b 4.9491, c 2.5511 Å at 23 °C, 0.9963 g/cm³, 18.33 Å² per chain)
- crystallinity: D26 local P2 with ring chords, r_c 6.50 Å, threshold 0.4 (**uncalibrated, melt baseline**); stable hold: last frame fraction ≥ 0.8 and stem P2 ≥ 0.8

## Holds

Thermo after the first 10% of each hold (mean ± SEM). a = Lx/na, b = Ly/nb, c = Lz/nz (CG: rise per bead; UA: the 2-CH2 repeat). ρ/ρ_exp and A/A_exp against the Busing cell (0.9963 g/cm³, 18.33 Å²).

| T (°C) | a (Å) | b (Å) | c (Å) | a/b | ρ (g/cm³) | ρ/ρ_exp | A/chain (Å²) | A/A_exp | drift | crystalline (mean; first → last) | stem P2 (last) | largest cluster (last) | stable |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 74.9 | 7.9288 ± 0.0010 | 4.5800 ± 0.0015 | 2.5586 ± 0.0001 | 1.731 | 1.0028 ± 0.0003 | 1.007 | 18.16 ± 0.01 | 0.991 | density, volume_A3, area_per_chain_A2 | 1.000; 1.000 → 1.000 | 0.979 | 1.000 | True |
| 85.0 | 7.9457 ± 0.0012 | 4.5881 ± 0.0005 | 2.5577 ± 0.0001 | 1.732 | 0.9993 ± 0.0001 | 1.003 | 18.23 ± 0.00 | 0.994 | none | 1.000; 1.000 → 1.000 | 0.977 | 1.000 | True |
| 100.0 | 7.9665 ± 0.0012 | 4.6001 ± 0.0006 | 2.5558 ± 0.0000 | 1.732 | 0.9947 ± 0.0001 | 0.998 | 18.32 ± 0.00 | 1.000 | none | 1.000; 1.000 → 1.000 | 0.976 | 1.000 | True |
| 110.0 | 7.9775 ± 0.0011 | 4.6056 ± 0.0009 | 2.5549 ± 0.0001 | 1.732 | 0.9926 ± 0.0001 | 0.996 | 18.37 ± 0.00 | 1.002 | c_A, area_per_chain_A2 | 1.000; 1.000 → 1.000 | 0.975 | 1.000 | True |

## Thermal expansion (stable holds)

Holds 75, 85, 100, 110 °C; α = d ln L/dT, OLS.

| quantity | α (10⁻⁴ K⁻¹) |
|---|---|
| a | 1.744 ± 0.097 |
| b | 1.613 ± 0.085 |
| c | -0.423 ± 0.018 |
| V | 2.936 ± 0.177 |

## Caveats

- A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.

## Plots

**cell lengths and density per hold**

![cell lengths and density per hold](cell.png)

**crystallinity and stem P2**

![crystallinity and stem P2](order.png)

