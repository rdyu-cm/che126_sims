# ipp_ua_amorph_n40_c240_s1 / sweep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-28 00:16 PDT, ended 2026-11-03 21:33 PST
- progress: 100.0% of 34,000,000 MD steps; 18/18 segments done
- speed: 7.95 ns/day (46.0 steps/s, Performance line of segment 18)
- log updated 2026-11-03 21:33 PST (19.6 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,5,8,12,13,16; step!=hold 90 C,130 C; hyst max 0.67%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 5,000,000 | 25.0 | 25.0 | 0.8606 ± 0.0003 | 18633.2 ± 9.0 | **yes** |
| 2 | seg 02 step 35 C | done | 1,000,000 | 35.0 | 35.0 | 0.8592 ± 0.0004 | 19351.4 ± 6.3 | no |
| 3 | seg 03 step 45 C | done | 1,000,000 | 45.0 | 45.0 | 0.8551 ± 0.0002 | 20115.0 ± 6.7 | no |
| 4 | seg 04 step 55 C | done | 1,000,000 | 55.0 | 54.9 | 0.8528 ± 0.0002 | 20866.6 ± 4.1 | no |
| 5 | seg 05 step 65 C | done | 1,000,000 | 65.0 | 65.2 | 0.8466 ± 0.0004 | 21715.9 ± 5.8 | **yes** |
| 6 | seg 06 step 75 C | done | 1,000,000 | 75.0 | 75.0 | 0.8432 ± 0.0005 | 22484.9 ± 20.5 | no |
| 7 | seg 07 step 85 C | done | 1,000,000 | 85.0 | 85.0 | 0.8398 ± 0.0003 | 23191.1 ± 7.5 | no |
| 8 | seg 08 step 90 C | done | 1,000,000 | 90.0 | 89.9 | 0.8384 ± 0.0007 | 23735.9 ± 8.7 | **yes** |
| 9 | seg 09 hold 90 C | done | 5,000,000 | 90.0 | 90.0 | 0.8356 ± 0.0004 | 23686.2 ± 21.7 | no |
| 10 | seg 10 step 100 C | done | 1,000,000 | 100.0 | 100.0 | 0.8316 ± 0.0005 | 24457.8 ± 9.4 | no |
| 11 | seg 11 step 110 C | done | 1,000,000 | 110.0 | 110.1 | 0.8251 ± 0.0008 | 25329.7 ± 9.9 | no |
| 12 | seg 12 step 120 C | done | 1,000,000 | 120.0 | 119.8 | 0.8188 ± 0.0011 | 26189.6 ± 13.6 | **yes** |
| 13 | seg 13 step 130 C | done | 1,000,000 | 130.0 | 130.0 | 0.8118 ± 0.0009 | 27220.4 ± 7.8 | **yes** |
| 14 | seg 14 hold 130 C | done | 5,000,000 | 130.0 | 130.0 | 0.8151 ± 0.0006 | 26989.3 ± 20.6 | no |
| 15 | seg 15 step 140 C | done | 1,000,000 | 140.0 | 140.0 | 0.8078 ± 0.0003 | 27905.9 ± 13.2 | no |
| 16 | seg 16 step 150 C | done | 1,000,000 | 150.0 | 150.0 | 0.8025 ± 0.0005 | 28845.1 ± 34.5 | **yes** |
| 17 | seg 17 step 160 C | done | 1,000,000 | 160.0 | 160.1 | 0.7982 ± 0.0005 | 29679.1 ± 16.7 | no |
| 18 | seg 18 hold 160 C | done | 5,000,000 | 160.0 | 160.0 | 0.7983 ± 0.0003 | 29654.4 ± 13.2 | no |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7762 ± 0.0005 | outside sweep |  |
| 2 | 449.5 | 0.7897 ± 0.0003 | outside sweep |  |
| 3 | 424.3 | 0.8036 ± 0.0006 | 0.8020 | +0.191 |
| 4 | 399.1 | 0.8164 ± 0.0003 | 0.8166 | -0.027 |
| 5 | 373.8 | 0.8274 ± 0.0004 | 0.8311 | -0.454 |
| 6 | 348.6 | 0.8374 ± 0.0006 | 0.8430 | -0.666 |
| 7 | 323.4 | 0.8504 ± 0.0004 | 0.8539 | -0.408 |
| 8 | 298.1 | 0.8599 ± 0.0002 | 0.8606 | -0.086 |

## Sweep step vs following hold (flag: > 2 combined SEM)

| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |
|---|---|---|---|---|---|
| 90 | 0.8384 | 0.8356 | -0.0028 ± 0.0007 | -49.7 ± 23.4 | **yes** |
| 130 | 0.8118 | 0.8151 | +0.0033 ± 0.0011 | -231.1 ± 22.0 | **yes** |
| 160 | 0.7982 | 0.7983 | +0.0001 ± 0.0006 | -24.7 ± 21.3 | no |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

