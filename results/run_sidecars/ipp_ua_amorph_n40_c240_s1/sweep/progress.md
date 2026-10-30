# ipp_ua_amorph_n40_c240_s1 / sweep

- status: **running** (manifest: started), node rdyu-rog, started 2026-10-28 00:16 PDT
- progress: 40.5% of 34,000,000 MD steps; 8/18 segments done; current: 9 seg 09 hold 90 C
- speed: 11.43 ns/day (66.1 steps/s, running segment (last hour of thermo))
- ETA: 2026-11-02 22:05 PST (84.9 h left)
- log updated 2026-10-30 10:10 PDT (0 min ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: drift seg 1,5,8; hyst max 0.67%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 5,000,000 | 25.0 | 25.0 | 0.8606 ± 0.0003 | 18633.2 ± 19.6 | **yes** |
| 2 | seg 02 step 35 C | done | 1,000,000 | 35.0 | 35.0 | 0.8592 ± 0.0004 | 19351.4 ± 46.4 | no |
| 3 | seg 03 step 45 C | done | 1,000,000 | 45.0 | 45.0 | 0.8551 ± 0.0002 | 20115.0 ± 46.0 | no |
| 4 | seg 04 step 55 C | done | 1,000,000 | 55.0 | 54.9 | 0.8528 ± 0.0002 | 20866.6 ± 48.4 | no |
| 5 | seg 05 step 65 C | done | 1,000,000 | 65.0 | 65.2 | 0.8466 ± 0.0003 | 21715.9 ± 48.5 | **yes** |
| 6 | seg 06 step 75 C | done | 1,000,000 | 75.0 | 75.0 | 0.8432 ± 0.0005 | 22484.9 ± 47.4 | no |
| 7 | seg 07 step 85 C | done | 1,000,000 | 85.0 | 85.0 | 0.8398 ± 0.0003 | 23191.1 ± 48.3 | no |
| 8 | seg 08 step 90 C | done | 1,000,000 | 90.0 | 89.9 | 0.8384 ± 0.0006 | 23735.9 ± 50.7 | **yes** |
| 9 | seg 09 hold 90 C | running | 1,784,500/5,000,000 | 90.0 |  |  |  |  |
| 10 | seg 10 step 100 C | pending | 1,000,000 | 100.0 |  |  |  |  |
| 11 | seg 11 step 110 C | pending | 1,000,000 | 110.0 |  |  |  |  |
| 12 | seg 12 step 120 C | pending | 1,000,000 | 120.0 |  |  |  |  |
| 13 | seg 13 step 130 C | pending | 1,000,000 | 130.0 |  |  |  |  |
| 14 | seg 14 hold 130 C | pending | 5,000,000 | 130.0 |  |  |  |  |
| 15 | seg 15 step 140 C | pending | 1,000,000 | 140.0 |  |  |  |  |
| 16 | seg 16 step 150 C | pending | 1,000,000 | 150.0 |  |  |  |  |
| 17 | seg 17 step 160 C | pending | 1,000,000 | 160.0 |  |  |  |  |
| 18 | seg 18 hold 160 C | pending | 5,000,000 | 160.0 |  |  |  |  |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7762 ± 0.0005 | outside sweep |  |
| 2 | 449.5 | 0.7897 ± 0.0004 | outside sweep |  |
| 3 | 424.3 | 0.8036 ± 0.0007 | outside sweep |  |
| 4 | 399.1 | 0.8164 ± 0.0003 | outside sweep |  |
| 5 | 373.8 | 0.8274 ± 0.0005 | outside sweep |  |
| 6 | 348.6 | 0.8374 ± 0.0006 | 0.8430 | -0.666 |
| 7 | 323.4 | 0.8504 ± 0.0003 | 0.8539 | -0.408 |
| 8 | 298.1 | 0.8599 ± 0.0002 | 0.8606 | -0.086 |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

