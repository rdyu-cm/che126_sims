# pe_ua_amorph_n40_c240_s1 / sweep

- status: **finished** (manifest: finished), node rdyu-server, started 2026-10-30 15:50 UTC, ended 2026-11-04 22:09 UTC
- progress: 100.0% of 34,000,000 MD steps; 18/18 segments done
- speed: 10.91 ns/day (63.1 steps/s, Performance line of segment 18)
- log updated 2026-11-04 22:09 UTC (18.9 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: drift seg 2,5,11,13,16; step!=hold 90 C,130 C; hyst max 0.36%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 5,000,000 | 25.0 | 25.0 | 0.8620 ± 0.0005 | 8210.5 ± 17.6 | no |
| 2 | seg 02 step 35 C | done | 1,000,000 | 35.0 | 34.9 | 0.8561 ± 0.0008 | 8935.6 ± 22.5 | **yes** |
| 3 | seg 03 step 45 C | done | 1,000,000 | 45.0 | 45.0 | 0.8499 ± 0.0004 | 9784.4 ± 15.2 | no |
| 4 | seg 04 step 55 C | done | 1,000,000 | 55.0 | 55.1 | 0.8449 ± 0.0003 | 10591.7 ± 13.3 | no |
| 5 | seg 05 step 65 C | done | 1,000,000 | 65.0 | 65.0 | 0.8379 ± 0.0004 | 11439.9 ± 19.7 | **yes** |
| 6 | seg 06 step 75 C | done | 1,000,000 | 75.0 | 74.8 | 0.8328 ± 0.0003 | 12058.6 ± 7.7 | no |
| 7 | seg 07 step 85 C | done | 1,000,000 | 85.0 | 85.2 | 0.8283 ± 0.0005 | 12935.9 ± 14.6 | no |
| 8 | seg 08 step 90 C | done | 1,000,000 | 90.0 | 90.1 | 0.8229 ± 0.0003 | 13285.3 ± 9.4 | no |
| 9 | seg 09 hold 90 C | done | 5,000,000 | 90.0 | 90.1 | 0.8226 ± 0.0004 | 13371.7 ± 17.4 | no |
| 10 | seg 10 step 100 C | done | 1,000,000 | 100.0 | 100.1 | 0.8177 ± 0.0004 | 14131.2 ± 14.1 | no |
| 11 | seg 11 step 110 C | done | 1,000,000 | 110.0 | 110.0 | 0.8107 ± 0.0008 | 14989.2 ± 29.4 | **yes** |
| 12 | seg 12 step 120 C | done | 1,000,000 | 120.0 | 119.9 | 0.8058 ± 0.0004 | 15629.4 ± 10.9 | no |
| 13 | seg 13 step 130 C | done | 1,000,000 | 130.0 | 129.9 | 0.8009 ± 0.0004 | 16441.0 ± 7.4 | **yes** |
| 14 | seg 14 hold 130 C | done | 5,000,000 | 130.0 | 130.0 | 0.8001 ± 0.0002 | 16488.0 ± 9.2 | no |
| 15 | seg 15 step 140 C | done | 1,000,000 | 140.0 | 140.2 | 0.7947 ± 0.0002 | 17213.3 ± 9.0 | no |
| 16 | seg 16 step 150 C | done | 1,000,000 | 150.0 | 150.1 | 0.7894 ± 0.0003 | 18015.7 ± 8.9 | **yes** |
| 17 | seg 17 step 160 C | done | 1,000,000 | 160.0 | 159.9 | 0.7833 ± 0.0004 | 18710.1 ± 11.5 | no |
| 18 | seg 18 hold 160 C | done | 5,000,000 | 160.0 | 159.9 | 0.7830 ± 0.0002 | 18715.4 ± 7.3 | no |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7593 ± 0.0006 | outside sweep |  |
| 2 | 449.5 | 0.7728 ± 0.0003 | outside sweep |  |
| 3 | 424.3 | 0.7870 ± 0.0005 | 0.7887 | -0.207 |
| 4 | 399.1 | 0.8016 ± 0.0004 | 0.8024 | -0.094 |
| 5 | 373.8 | 0.8162 ± 0.0002 | 0.8172 | -0.121 |
| 6 | 348.6 | 0.8296 ± 0.0005 | 0.8326 | -0.357 |
| 7 | 323.4 | 0.8460 ± 0.0004 | 0.8473 | -0.152 |
| 8 | 298.1 | 0.8601 ± 0.0002 | 0.8620 | -0.212 |

## Sweep step vs following hold (flag: > 2 combined SEM)

| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |
|---|---|---|---|---|---|
| 90 | 0.8229 | 0.8226 | -0.0003 ± 0.0006 | +86.4 ± 19.8 | **yes** |
| 130 | 0.8009 | 0.8001 | -0.0009 ± 0.0004 | +47.0 ± 11.8 | **yes** |
| 160 | 0.7833 | 0.7830 | -0.0003 ± 0.0005 | +5.2 ± 13.6 | no |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

