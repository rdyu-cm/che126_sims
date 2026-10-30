# pe_cg_amorph_n40_c240_s1 / sweep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-21 18:07 PDT, ended 2026-10-22 08:06 PDT
- progress: 100.0% of 17,000,000 MD steps; 18/18 segments done
- speed: 281.91 ns/day (326.3 steps/s, Performance line of segment 18)
- log updated 2026-10-22 08:06 PDT (8.1 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: drift seg 1,7,9,12; step!=hold 130 C; hyst max 0.10%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 2,500,000 | 25.0 | 25.0 | 0.8342 ± 0.0000 | -4767.9 ± 2.2 | **yes** |
| 2 | seg 02 step 35 C | done | 500,000 | 35.0 | 35.0 | 0.8292 ± 0.0001 | -4535.2 ± 4.9 | no |
| 3 | seg 03 step 45 C | done | 500,000 | 45.0 | 44.7 | 0.8231 ± 0.0001 | -4258.8 ± 5.2 | no |
| 4 | seg 04 step 55 C | done | 500,000 | 55.0 | 54.9 | 0.8176 ± 0.0001 | -3967.9 ± 5.1 | no |
| 5 | seg 05 step 65 C | done | 500,000 | 65.0 | 65.0 | 0.8120 ± 0.0001 | -3713.9 ± 5.3 | no |
| 6 | seg 06 step 75 C | done | 500,000 | 75.0 | 74.9 | 0.8064 ± 0.0001 | -3435.3 ± 5.1 | no |
| 7 | seg 07 step 85 C | done | 500,000 | 85.0 | 84.8 | 0.8011 ± 0.0001 | -3175.4 ± 5.4 | **yes** |
| 8 | seg 08 step 90 C | done | 500,000 | 90.0 | 89.9 | 0.7981 ± 0.0001 | -3033.0 ± 5.4 | no |
| 9 | seg 09 hold 90 C | done | 2,500,000 | 90.0 | 90.1 | 0.7982 ± 0.0001 | -3044.6 ± 2.4 | **yes** |
| 10 | seg 10 step 100 C | done | 500,000 | 100.0 | 100.1 | 0.7927 ± 0.0001 | -2785.3 ± 5.5 | no |
| 11 | seg 11 step 110 C | done | 500,000 | 110.0 | 109.8 | 0.7865 ± 0.0001 | -2494.6 ± 5.5 | no |
| 12 | seg 12 step 120 C | done | 500,000 | 120.0 | 120.0 | 0.7817 ± 0.0001 | -2264.1 ± 5.6 | **yes** |
| 13 | seg 13 step 130 C | done | 500,000 | 130.0 | 129.9 | 0.7765 ± 0.0002 | -2018.8 ± 5.8 | no |
| 14 | seg 14 hold 130 C | done | 2,500,000 | 130.0 | 130.0 | 0.7760 ± 0.0001 | -1985.9 ± 2.6 | no |
| 15 | seg 15 step 140 C | done | 500,000 | 140.0 | 140.1 | 0.7707 ± 0.0002 | -1733.1 ± 5.7 | no |
| 16 | seg 16 step 150 C | done | 500,000 | 150.0 | 150.1 | 0.7653 ± 0.0002 | -1474.6 ± 5.7 | no |
| 17 | seg 17 step 160 C | done | 500,000 | 160.0 | 160.0 | 0.7596 ± 0.0002 | -1203.7 ± 6.0 | no |
| 18 | seg 18 hold 160 C | done | 2,500,000 | 160.0 | 160.0 | 0.7596 ± 0.0001 | -1200.6 ± 2.6 | no |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7369 ± 0.0002 | outside sweep |  |
| 2 | 449.5 | 0.7509 ± 0.0002 | outside sweep |  |
| 3 | 424.3 | 0.7647 ± 0.0002 | 0.7646 | +0.008 |
| 4 | 399.1 | 0.7778 ± 0.0002 | 0.7783 | -0.069 |
| 5 | 373.8 | 0.7920 ± 0.0001 | 0.7922 | -0.028 |
| 6 | 348.6 | 0.8054 ± 0.0001 | 0.8061 | -0.086 |
| 7 | 323.4 | 0.8194 ± 0.0001 | 0.8202 | -0.097 |
| 8 | 298.1 | 0.8333 ± 0.0001 | 0.8342 | -0.104 |

## Sweep step vs following hold (flag: > 2 combined SEM)

| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |
|---|---|---|---|---|---|
| 90 | 0.7981 | 0.7982 | +0.0001 ± 0.0001 | -11.6 ± 5.9 | no |
| 130 | 0.7765 | 0.7760 | -0.0005 ± 0.0002 | +32.9 ± 6.3 | **yes** |
| 160 | 0.7596 | 0.7596 | +0.0000 ± 0.0002 | +3.2 ± 6.5 | no |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

