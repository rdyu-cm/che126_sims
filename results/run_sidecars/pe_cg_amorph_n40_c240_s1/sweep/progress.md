# pe_cg_amorph_n40_c240_s1 / sweep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-26 20:52 PDT, ended 2026-10-27 15:32 PDT
- progress: 100.0% of 17,000,000 MD steps; 18/18 segments done
- speed: 233.23 ns/day (269.9 steps/s, Performance line of segment 18)
- log updated 2026-10-27 15:32 PDT (2.8 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: drift seg 2,8,14; step!=hold 130 C; hyst max 0.11%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 2,500,000 | 25.0 | 25.0 | 0.8346 ± 0.0000 | -4789.6 ± 2.2 | no |
| 2 | seg 02 step 35 C | done | 500,000 | 35.0 | 35.0 | 0.8290 ± 0.0001 | -4520.0 ± 5.0 | **yes** |
| 3 | seg 03 step 45 C | done | 500,000 | 45.0 | 45.2 | 0.8230 ± 0.0001 | -4236.0 ± 5.1 | no |
| 4 | seg 04 step 55 C | done | 500,000 | 55.0 | 55.0 | 0.8172 ± 0.0001 | -3953.8 ± 5.3 | no |
| 5 | seg 05 step 65 C | done | 500,000 | 65.0 | 65.0 | 0.8114 ± 0.0001 | -3680.3 ± 5.1 | no |
| 6 | seg 06 step 75 C | done | 500,000 | 75.0 | 75.1 | 0.8063 ± 0.0001 | -3439.2 ± 5.3 | no |
| 7 | seg 07 step 85 C | done | 500,000 | 85.0 | 85.0 | 0.8001 ± 0.0001 | -3123.8 ± 5.4 | no |
| 8 | seg 08 step 90 C | done | 500,000 | 90.0 | 90.0 | 0.7979 ± 0.0001 | -3031.5 ± 5.5 | **yes** |
| 9 | seg 09 hold 90 C | done | 2,500,000 | 90.0 | 90.0 | 0.7979 ± 0.0001 | -3038.7 ± 2.4 | no |
| 10 | seg 10 step 100 C | done | 500,000 | 100.0 | 99.9 | 0.7923 ± 0.0001 | -2758.0 ± 5.5 | no |
| 11 | seg 11 step 110 C | done | 500,000 | 110.0 | 110.0 | 0.7868 ± 0.0001 | -2505.4 ± 5.7 | no |
| 12 | seg 12 step 120 C | done | 500,000 | 120.0 | 120.1 | 0.7813 ± 0.0001 | -2243.7 ± 5.7 | no |
| 13 | seg 13 step 130 C | done | 500,000 | 130.0 | 130.1 | 0.7760 ± 0.0002 | -1979.9 ± 5.8 | no |
| 14 | seg 14 hold 130 C | done | 2,500,000 | 130.0 | 129.9 | 0.7756 ± 0.0001 | -1961.7 ± 2.6 | **yes** |
| 15 | seg 15 step 140 C | done | 500,000 | 140.0 | 139.9 | 0.7698 ± 0.0002 | -1691.1 ± 5.7 | no |
| 16 | seg 16 step 150 C | done | 500,000 | 150.0 | 149.9 | 0.7654 ± 0.0002 | -1465.0 ± 5.9 | no |
| 17 | seg 17 step 160 C | done | 500,000 | 160.0 | 160.1 | 0.7593 ± 0.0002 | -1187.5 ± 5.9 | no |
| 18 | seg 18 hold 160 C | done | 2,500,000 | 160.0 | 160.0 | 0.7595 ± 0.0001 | -1197.4 ± 2.7 | no |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7367 ± 0.0002 | outside sweep |  |
| 2 | 449.5 | 0.7505 ± 0.0002 | outside sweep |  |
| 3 | 424.3 | 0.7639 ± 0.0002 | 0.7648 | -0.112 |
| 4 | 399.1 | 0.7777 ± 0.0002 | 0.7779 | -0.034 |
| 5 | 373.8 | 0.7917 ± 0.0001 | 0.7920 | -0.031 |
| 6 | 348.6 | 0.8056 ± 0.0001 | 0.8060 | -0.054 |
| 7 | 323.4 | 0.8195 ± 0.0001 | 0.8199 | -0.049 |
| 8 | 298.1 | 0.8350 ± 0.0001 | 0.8346 | +0.044 |

## Sweep step vs following hold (flag: > 2 combined SEM)

| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |
|---|---|---|---|---|---|
| 90 | 0.7979 | 0.7979 | +0.0000 ± 0.0001 | -7.2 ± 6.0 | no |
| 130 | 0.7760 | 0.7756 | -0.0004 ± 0.0002 | +18.2 ± 6.3 | **yes** |
| 160 | 0.7593 | 0.7595 | +0.0003 ± 0.0002 | -9.9 ± 6.5 | no |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

