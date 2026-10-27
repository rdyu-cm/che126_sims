# Sweep analysis: pe_cg_amorph_n40_c240_s1 / sweep

- system: `pe_cg_amorph_n40_c240_s1` (cg); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_cg_amorph_n40_c240_s1/sweep` (status finished, node rdyu-rog, run code commit 4d12e74601)
- analysis: `sepsim analyze sweep` (D49), code commit eb03f2965b (dirty), 2026-10-27 22:41 on rdyu-server
- windows: steps second half (50% of rows dropped); holds without the first 10% of rows; SEM from the statistical inefficiency (D26)
- system mass 134737.9 g/mol (from Density × Volume)

## Segments

| # | segment | T set (°C) | window (ns) | T (°C) | density (g/cm³) | H (kcal/mol) | V (Å³) |
|---|---|---|---|---|---|---|---|
| 1 | hold | 25 | 22.50 | 25.00 ± 0.03 | 0.83453 ± 0.00003 | -4785.9 ± 1.7 | 268105 ± 10 |
| 2 | step | 35 | 2.50 | 35.00 ± 0.10 | 0.82900 ± 0.00009 | -4520.0 ± 5.0 | 269893 ± 30 |
| 3 | step | 45 | 2.50 | 45.18 ± 0.09 | 0.82297 ± 0.00011 | -4236.0 ± 5.1 | 271871 ± 36 |
| 4 | step | 55 | 2.50 | 55.05 ± 0.10 | 0.81718 ± 0.00011 | -3953.8 ± 5.3 | 273799 ± 37 |
| 5 | step | 65 | 2.50 | 65.03 ± 0.10 | 0.81142 ± 0.00012 | -3680.3 ± 5.1 | 275742 ± 40 |
| 6 | step | 75 | 2.50 | 75.08 ± 0.10 | 0.80632 ± 0.00012 | -3439.2 ± 5.3 | 277485 ± 41 |
| 7 | step | 85 | 2.50 | 85.03 ± 0.12 | 0.80015 ± 0.00013 | -3123.8 ± 5.4 | 279627 ± 44 |
| 8 | step | 90 | 2.50 | 89.97 ± 0.12 | 0.79788 ± 0.00013 | -3031.5 ± 5.5 | 280423 ± 47 |
| 9 | hold | 90 | 22.50 | 89.96 ± 0.03 | 0.79783 ± 0.00004 | -3031.1 ± 1.8 | 280439 ± 16 |
| 10 | step | 100 | 2.50 | 99.93 ± 0.11 | 0.79234 ± 0.00014 | -2758.0 ± 5.5 | 282382 ± 49 |
| 11 | step | 110 | 2.50 | 109.99 ± 0.11 | 0.78677 ± 0.00014 | -2505.4 ± 5.7 | 284381 ± 50 |
| 12 | step | 120 | 2.50 | 120.06 ± 0.12 | 0.78129 ± 0.00015 | -2243.7 ± 5.7 | 286378 ± 53 |
| 13 | step | 130 | 2.50 | 130.09 ± 0.12 | 0.77603 ± 0.00016 | -1979.9 ± 5.8 | 288320 ± 58 |
| 14 | hold | 130 | 22.50 | 129.97 ± 0.04 | 0.77580 ± 0.00005 | -1970.4 ± 1.9 | 288406 ± 20 |
| 15 | step | 140 | 2.50 | 139.89 ± 0.12 | 0.76979 ± 0.00016 | -1691.1 ± 5.7 | 290657 ± 61 |
| 16 | step | 150 | 2.50 | 149.93 ± 0.13 | 0.76544 ± 0.00017 | -1465.0 ± 5.9 | 292311 ± 66 |
| 17 | step | 160 | 2.50 | 160.11 ± 0.13 | 0.75926 ± 0.00018 | -1187.5 ± 5.9 | 294690 ± 68 |
| 18 | hold | 160 | 22.50 | 159.99 ± 0.04 | 0.75938 ± 0.00006 | -1189.1 ± 2.0 | 294640 ± 23 |

## Isothermal compressibility (holds)

κ_T = (⟨V²⟩ − ⟨V⟩²)/(k_B T ⟨V⟩) over the hold window (NPT iso Nosé–Hoover), T the set point; SEM = statistical-inefficiency SEM of (V − ⟨V⟩)² (g given).

| T (°C) | κ_T (GPa⁻¹) | σ_V (Å³) | ⟨V⟩ (Å³) | g | samples |
|---|---|---|---|---|---|
| 25 | 1.000 ± 0.015 | 1050.6 | 268105 | 2.7 | 22501 |
| 90 | 1.292 ± 0.022 | 1347.7 | 280439 | 3.2 | 22501 |
| 130 | 1.502 ± 0.027 | 1552.7 | 288406 | 3.7 | 22501 |
| 160 | 1.662 ± 0.031 | 1711.5 | 294640 | 4.0 | 22501 |

## Thermal expansion and classical Cp (fits over the sweep)

Linear fits in T over each window, SEM-weighted, one point per temperature (hold where there is one): 25, 35, 45, 55, 65, 75, 85, 90, 100, 110, 120, 130, 140, 150, 160 °C. α_V = (1/⟨V⟩) dV/dT; Cp = dH/dT per gram; errors 1σ from the fit, scaled by √χ²_red when χ²_red > 1.

| window (°C) | points | α_V (10⁻⁴ K⁻¹) | χ²_red (V) | Cp (J g⁻¹ K⁻¹) | χ²_red (H) |
|---|---|---|---|---|---|
| 25–160 | 15 | 6.919 ± 0.034 | 49.72 | 0.828 ± 0.002 | 23.98 |
| 25–90 | 8 | 6.917 ± 0.022 | 5.05 | 0.840 ± 0.004 | 15.65 |
| 90–160 | 8 | 7.032 ± 0.040 | 9.99 | 0.817 ± 0.003 | 6.04 |

## Hold trajectories: mobility and chain size

Backbone sites (CG: beads; UA/AA: backbone carbons) and chains, positions relative to the system's mass centre. MSD and P2 combine the D46 bursts (0.1 ps frames, lags < the hold frame interval) with the hold DCD (lags up to half the hold). D_COM from an OLS line over the end of the COM MSD where the local log-slope stays ≥ 0.9 over a factor ≥ 2 in lag; else "not diffusive" (largest slope given). Rg mass-weighted over all atoms of a chain; C_n plateau over n ≥ 100 carbons (D37) on ≤ 500 frames.

| T (°C) | frames | bursts | MSD seg 10 ps / max (Å²) | COM MSD max (Å²) | D_COM (cm²/s) | P2 1/e (ps) | Rg (Å) | R_ee (Å) | C_n plateau |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 2501 × 10 ps | 25 | 10.3 / 816 (12.5 ns) | 177 | not diffusive (max log-slope 1.88) | 122.9 | 31.24 ± 0.12 | 77.1 ± 0.5 | 10.270 ± 0.084 |
| 90 | 2501 × 10 ps | 25 | 16.5 / 1280 (12.5 ns) | 396 | 5.12e-07 ± 2.2e-10 | 25.5 | 32.21 ± 0.21 | 84.2 ± 1.0 | 11.782 ± 0.190 |
| 130 | 2501 × 10 ps | 25 | 21.1 / 1602 (12.5 ns) | 523 | not diffusive (max log-slope 1.90) | 12.7 | 30.84 ± 0.34 | 77.6 ± 2.1 | 10.583 ± 0.358 |
| 160 | 2501 × 10 ps | 25 | 24.8 / 1570 (12.5 ns) | 573 | not diffusive (max log-slope 1.90) | 7.6 | 30.80 ± 0.39 | 78.3 ± 1.4 | 10.704 ± 0.344 |

## Caveats

- Cp is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k_B/2 per quadratic term; CG also drops degrees of freedom (all motion inside a 3-CH2 bead), so its Cp per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- D37 chain check FAIL on the prep hold + extension: C_n plateau 9.11 vs melt 6.7 ±10%.
- α_V and Cp are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²_red, and a large χ²_red over 25–160 °C means α_V or Cp depends on T (compare the two half windows).
- CG time is not real time: SDK beads move faster than the atoms they represent, so MSD, D_COM and P2 times are model times (not rescaled).

## Plots

**density and enthalpy vs T with the linear fits**

![density and enthalpy vs T with the linear fits](thermo_vs_T.png)

**κ_T vs T (holds)**

![κ_T vs T (holds)](kappa_T.png)

**α_V and Cp per fit window**

![α_V and Cp per fit window](alpha_V.png)

**backbone-site and chain COM MSD**

![backbone-site and chain COM MSD](msd.png)

**bond P2 autocorrelation**

![bond P2 autocorrelation](p2_acf.png)

**Rg, R_ee and C_n vs T**

![Rg, R_ee and C_n vs T](chain_vs_T.png)

