# ipp_aa_amorph_n40_c240_s1_from_ua / sweep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-13 04:34 UTC, ended 2026-11-20 06:02 UTC
- progress: 100.0% of 34,040,000 MD steps; 22/22 segments done
- speed: 2.05 ns/day (23.8 steps/s, Performance line of segment 22)
- log updated 2026-11-20 06:02 UTC (3.5 d ago); report 2026-11-23 18:50 UTC on rdyu-rog
- checks: drift seg 3,6,8; step!=hold 90 C,130 C,160 C; hyst max 0.33%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 5,000,000 | 25.0 | 25.0 | 0.8682 ± 0.0004 | 49999.2 ± 9.5 | no |
| 2 | seg 01 hold 25 C VDOS NVE | done | 10,000 |  | 26.0 | 0.8704 ± 0.0000 | 49514.2 ± 0.9 |  |
| 3 | seg 02 step 35 C | done | 1,000,000 | 35.0 | 35.0 | 0.8641 ± 0.0006 | 51818.4 ± 13.0 | **yes** |
| 4 | seg 03 step 45 C | done | 1,000,000 | 45.0 | 45.0 | 0.8571 ± 0.0004 | 53690.5 ± 12.0 | no |
| 5 | seg 04 step 55 C | done | 1,000,000 | 55.0 | 55.0 | 0.8515 ± 0.0004 | 55572.3 ± 10.9 | no |
| 6 | seg 05 step 65 C | done | 1,000,000 | 65.0 | 65.0 | 0.8466 ± 0.0007 | 57538.9 ± 29.8 | **yes** |
| 7 | seg 06 step 75 C | done | 1,000,000 | 75.0 | 74.9 | 0.8385 ± 0.0004 | 59420.2 ± 13.6 | no |
| 8 | seg 07 step 85 C | done | 1,000,000 | 85.0 | 85.0 | 0.8297 ± 0.0005 | 61505.5 ± 11.3 | **yes** |
| 9 | seg 08 step 90 C | done | 1,000,000 | 90.0 | 90.0 | 0.8277 ± 0.0006 | 62186.6 ± 20.6 | no |
| 10 | seg 09 hold 90 C | done | 5,000,000 | 90.0 | 90.1 | 0.8283 ± 0.0006 | 62371.0 ± 12.9 | no |
| 11 | seg 09 hold 90 C VDOS NVE | done | 10,000 |  | 90.3 | 0.8267 ± 0.0000 | 62258.1 ± 2.1 |  |
| 12 | seg 10 step 100 C | done | 1,000,000 | 100.0 | 99.9 | 0.8199 ± 0.0006 | 64258.8 ± 14.7 | no |
| 13 | seg 11 step 110 C | done | 1,000,000 | 110.0 | 110.0 | 0.8130 ± 0.0004 | 66282.8 ± 18.6 | no |
| 14 | seg 12 step 120 C | done | 1,000,000 | 120.0 | 120.1 | 0.8100 ± 0.0005 | 68084.9 ± 10.8 | no |
| 15 | seg 13 step 130 C | done | 1,000,000 | 130.0 | 130.1 | 0.8025 ± 0.0005 | 70061.9 ± 12.9 | no |
| 16 | seg 14 hold 130 C | done | 5,000,000 | 130.0 | 130.0 | 0.8020 ± 0.0003 | 69949.3 ± 12.5 | no |
| 17 | seg 14 hold 130 C VDOS NVE | done | 10,000 |  | 130.3 | 0.8018 ± 0.0000 | 69715.7 ± 1.9 |  |
| 18 | seg 15 step 140 C | done | 1,000,000 | 140.0 | 140.0 | 0.7947 ± 0.0006 | 71932.5 ± 18.6 | no |
| 19 | seg 16 step 150 C | done | 1,000,000 | 150.0 | 150.0 | 0.7885 ± 0.0007 | 73886.5 ± 11.9 | no |
| 20 | seg 17 step 160 C | done | 1,000,000 | 160.0 | 159.9 | 0.7814 ± 0.0004 | 75746.5 ± 16.0 | no |
| 21 | seg 18 hold 160 C | done | 5,000,000 | 160.0 | 160.0 | 0.7831 ± 0.0002 | 75538.6 ± 10.9 | no |
| 22 | seg 18 hold 160 C VDOS NVE | done | 10,000 |  | 160.2 | 0.7862 ± 0.0000 | 75797.1 ± 1.7 |  |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7578 ± 0.0006 | outside sweep |  |
| 2 | 449.5 | 0.7733 ± 0.0005 | outside sweep |  |
| 3 | 424.3 | 0.7876 ± 0.0011 | 0.7878 | -0.034 |
| 4 | 399.1 | 0.8050 ± 0.0006 | 0.8053 | -0.032 |
| 5 | 373.8 | 0.8207 ± 0.0004 | 0.8194 | +0.163 |
| 6 | 348.6 | 0.8362 ± 0.0007 | 0.8380 | -0.225 |
| 7 | 323.4 | 0.8519 ± 0.0003 | 0.8542 | -0.275 |
| 8 | 298.1 | 0.8654 ± 0.0002 | 0.8682 | -0.327 |

## Sweep step vs following hold (flag: > 2 combined SEM)

| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |
|---|---|---|---|---|---|
| 90 | 0.8277 | 0.8283 | +0.0006 ± 0.0009 | +184.4 ± 24.3 | **yes** |
| 130 | 0.8025 | 0.8020 | -0.0005 ± 0.0006 | -112.7 ± 18.0 | **yes** |
| 160 | 0.7814 | 0.7831 | +0.0017 ± 0.0005 | -208.0 ± 19.4 | **yes** |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

