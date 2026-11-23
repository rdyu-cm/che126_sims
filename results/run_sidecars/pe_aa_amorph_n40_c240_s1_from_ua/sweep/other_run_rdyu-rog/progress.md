# pe_aa_amorph_n40_c240_s1_from_ua / sweep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-02 17:01 PST, ended 2026-11-11 05:28 PST
- progress: 100.0% of 34,040,000 MD steps; 22/22 segments done
- speed: 2.14 ns/day (24.8 steps/s, Performance line of segment 22)
- log updated 2026-11-11 05:28 PST (12.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 4,14,19; step!=hold 90 C,130 C,160 C; hyst max 0.44%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | seg 01 hold 25 C | done | 5,000,000 | 25.0 | 24.9 | 0.8512 ± 0.0006 | 45034.3 ± 27.3 | no |
| 2 | seg 01 hold 25 C VDOS NVE | done | 10,000 |  | 26.8 | 0.8531 ± 0.0000 | 45672.1 ± 2.0 |  |
| 3 | seg 02 step 35 C | done | 1,000,000 | 35.0 | 35.1 | 0.8468 ± 0.0003 | 46894.6 ± 13.3 | no |
| 4 | seg 03 step 45 C | done | 1,000,000 | 45.0 | 44.9 | 0.8383 ± 0.0007 | 48976.2 ± 26.7 | **yes** |
| 5 | seg 04 step 55 C | done | 1,000,000 | 55.0 | 55.0 | 0.8314 ± 0.0004 | 50879.4 ± 13.5 | no |
| 6 | seg 05 step 65 C | done | 1,000,000 | 65.0 | 65.0 | 0.8249 ± 0.0003 | 52946.3 ± 21.0 | no |
| 7 | seg 06 step 75 C | done | 1,000,000 | 75.0 | 75.0 | 0.8176 ± 0.0004 | 54912.4 ± 11.6 | no |
| 8 | seg 07 step 85 C | done | 1,000,000 | 85.0 | 85.0 | 0.8126 ± 0.0003 | 56761.9 ± 11.8 | no |
| 9 | seg 08 step 90 C | done | 1,000,000 | 90.0 | 90.0 | 0.8072 ± 0.0003 | 57855.2 ± 13.6 | no |
| 10 | seg 09 hold 90 C | done | 5,000,000 | 90.0 | 90.0 | 0.8072 ± 0.0003 | 57921.4 ± 9.6 | no |
| 11 | seg 09 hold 90 C VDOS NVE | done | 10,000 |  | 91.4 | 0.8080 ± 0.0000 | 58366.8 ± 1.8 |  |
| 12 | seg 10 step 100 C | done | 1,000,000 | 100.0 | 99.9 | 0.7983 ± 0.0005 | 59969.0 ± 19.1 | no |
| 13 | seg 11 step 110 C | done | 1,000,000 | 110.0 | 110.0 | 0.7926 ± 0.0003 | 61753.0 ± 14.6 | no |
| 14 | seg 12 step 120 C | done | 1,000,000 | 120.0 | 119.9 | 0.7861 ± 0.0005 | 63819.9 ± 21.6 | **yes** |
| 15 | seg 13 step 130 C | done | 1,000,000 | 130.0 | 130.1 | 0.7794 ± 0.0008 | 65719.9 ± 23.5 | no |
| 16 | seg 14 hold 130 C | done | 5,000,000 | 130.0 | 130.0 | 0.7785 ± 0.0002 | 65777.7 ± 13.3 | no |
| 17 | seg 14 hold 130 C VDOS NVE | done | 10,000 |  | 129.6 | 0.7792 ± 0.0000 | 65192.8 ± 1.6 |  |
| 18 | seg 15 step 140 C | done | 1,000,000 | 140.0 | 140.0 | 0.7730 ± 0.0005 | 67723.6 ± 16.1 | no |
| 19 | seg 16 step 150 C | done | 1,000,000 | 150.0 | 149.9 | 0.7653 ± 0.0005 | 69673.6 ± 17.6 | **yes** |
| 20 | seg 17 step 160 C | done | 1,000,000 | 160.0 | 160.0 | 0.7595 ± 0.0004 | 71426.9 ± 14.3 | no |
| 21 | seg 18 hold 160 C | done | 5,000,000 | 160.0 | 160.0 | 0.7590 ± 0.0002 | 71569.5 ± 9.2 | no |
| 22 | seg 18 hold 160 C VDOS NVE | done | 10,000 |  | 160.5 | 0.7638 ± 0.0000 | 71166.1 ± 1.2 |  |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7314 ± 0.0004 | outside sweep |  |
| 2 | 449.5 | 0.7466 ± 0.0003 | outside sweep |  |
| 3 | 424.3 | 0.7619 ± 0.0007 | 0.7646 | -0.346 |
| 4 | 399.1 | 0.7790 ± 0.0005 | 0.7816 | -0.334 |
| 5 | 373.8 | 0.7975 ± 0.0003 | 0.7979 | -0.058 |
| 6 | 348.6 | 0.8147 ± 0.0003 | 0.8173 | -0.317 |
| 7 | 323.4 | 0.8313 ± 0.0006 | 0.8347 | -0.409 |
| 8 | 298.1 | 0.8474 ± 0.0005 | 0.8512 | -0.436 |

## Sweep step vs following hold (flag: > 2 combined SEM)

| T (°C) | ρ step | ρ hold | Δρ ± SEM | ΔH ± SEM (kcal/mol) | flag |
|---|---|---|---|---|---|
| 90 | 0.8072 | 0.8072 | +0.0000 ± 0.0004 | +66.1 ± 16.6 | **yes** |
| 130 | 0.7794 | 0.7785 | -0.0009 ± 0.0008 | +57.8 ± 27.1 | **yes** |
| 160 | 0.7595 | 0.7590 | -0.0005 ± 0.0004 | +142.6 ± 17.1 | **yes** |

## Plots

**sweep density and enthalpy vs T (prep step-cool overlaid)**

![sweep density and enthalpy vs T (prep step-cool overlaid)](progress_sweep_vs_T.png)

