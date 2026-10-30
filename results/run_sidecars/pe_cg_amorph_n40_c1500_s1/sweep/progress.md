# pe_cg_amorph_n40_c1500_s1 / sweep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-25 22:01 PDT, ended 2026-10-26 10:56 PDT
- progress: 100.0% of 17,000,000 MD steps; 18/18 segments done
- speed: 311.95 ns/day (361.1 steps/s, Performance line of segment 18)
- log updated 2026-10-26 10:56 PDT (4.0 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: drift seg 1,2,3,6,9,14; step!=hold 130 C; hyst max 0.11%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 2,500,000 | 25.0 | 25.0 | 0.8382 ± 0.0000 | -29359.7 ± 5.5 | **yes** |
| 2 | seg 02 step 35 C | done | 500,000 | 35.0 | 35.0 | 0.8326 ± 0.0000 | -27719.5 ± 12.6 | **yes** |
| 3 | seg 03 step 45 C | done | 500,000 | 45.0 | 45.0 | 0.8264 ± 0.0000 | -25868.8 ± 12.1 | **yes** |
| 4 | seg 04 step 55 C | done | 500,000 | 55.0 | 55.0 | 0.8208 ± 0.0000 | -24166.9 ± 13.0 | no |
| 5 | seg 05 step 65 C | done | 500,000 | 65.0 | 65.0 | 0.8153 ± 0.0000 | -22544.2 ± 12.9 | no |
| 6 | seg 06 step 75 C | done | 500,000 | 75.0 | 75.0 | 0.8097 ± 0.0000 | -20861.5 ± 13.4 | **yes** |
| 7 | seg 07 step 85 C | done | 500,000 | 85.0 | 85.1 | 0.8043 ± 0.0001 | -19255.1 ± 13.9 | no |
| 8 | seg 08 step 90 C | done | 500,000 | 90.0 | 90.0 | 0.8015 ± 0.0001 | -18398.5 ± 13.7 | no |
| 9 | seg 09 hold 90 C | done | 2,500,000 | 90.0 | 90.0 | 0.8015 ± 0.0000 | -18401.9 ± 6.0 | **yes** |
| 10 | seg 10 step 100 C | done | 500,000 | 100.0 | 100.0 | 0.7961 ± 0.0001 | -16786.7 ± 13.8 | no |
| 11 | seg 11 step 110 C | done | 500,000 | 110.0 | 110.0 | 0.7909 ± 0.0001 | -15233.5 ± 14.1 | no |
| 12 | seg 12 step 120 C | done | 500,000 | 120.0 | 120.0 | 0.7857 ± 0.0001 | -13630.7 ± 14.0 | no |
| 13 | seg 13 step 130 C | done | 500,000 | 130.0 | 130.0 | 0.7803 ± 0.0001 | -12029.8 ± 13.8 | no |
| 14 | seg 14 hold 130 C | done | 2,500,000 | 130.0 | 130.0 | 0.7801 ± 0.0000 | -11967.7 ± 6.3 | **yes** |
| 15 | seg 15 step 140 C | done | 500,000 | 140.0 | 140.0 | 0.7750 ± 0.0001 | -10393.8 ± 14.6 | no |
| 16 | seg 16 step 150 C | done | 500,000 | 150.0 | 150.1 | 0.7695 ± 0.0001 | -8813.3 ± 15.0 | no |
| 17 | seg 17 step 160 C | done | 500,000 | 160.0 | 160.0 | 0.7644 ± 0.0001 | -7238.5 ± 15.0 | no |
| 18 | seg 18 hold 160 C | done | 2,500,000 | 160.0 | 160.0 | 0.7645 ± 0.0000 | -7253.6 ± 6.6 | no |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7417 ± 0.0001 | outside sweep |  |
| 2 | 449.5 | 0.7552 ± 0.0001 | outside sweep |  |
| 3 | 424.3 | 0.7681 ± 0.0001 | 0.7689 | -0.111 |
| 4 | 399.1 | 0.7816 ± 0.0001 | 0.7824 | -0.106 |
| 5 | 373.8 | 0.7952 ± 0.0001 | 0.7957 | -0.073 |
| 6 | 348.6 | 0.8090 ± 0.0001 | 0.8094 | -0.052 |
| 7 | 323.4 | 0.8230 ± 0.0000 | 0.8235 | -0.054 |
| 8 | 298.1 | 0.8376 ± 0.0000 | 0.8382 | -0.070 |

## Sweep step vs following hold (flag: > 2 combined SEM)

| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |
|---|---|---|---|---|---|
| 90 | 0.8015 | 0.8015 | +0.0000 ± 0.0001 | -3.4 ± 15.0 | no |
| 130 | 0.7803 | 0.7801 | -0.0002 ± 0.0001 | +62.2 ± 15.2 | **yes** |
| 160 | 0.7644 | 0.7645 | +0.0001 ± 0.0001 | -15.1 ± 16.4 | no |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

