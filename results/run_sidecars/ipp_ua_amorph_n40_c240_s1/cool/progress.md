# ipp_ua_amorph_n40_c240_s1 / cool

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-26 11:02 PDT, ended 2026-10-28 00:16 PDT
- progress: 100.0% of 8,000,000 MD steps; 8/8 segments done
- speed: 9.73 ns/day (56.3 steps/s, Performance line of segment 8)
- log updated 2026-10-28 00:16 PDT (2.4 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: drift seg 4; hyst max 0.67%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1 cool 1/8 (474.8 K) | done | 1,000,000 | 201.6 | 201.5 | 0.7762 ± 0.0005 | 33155.9 ± 57.4 | no |
| 2 | Stage 1 cool 2/8 (449.5 K) | done | 1,000,000 | 176.4 | 176.4 | 0.7897 ± 0.0004 | 31102.5 ± 55.2 | no |
| 3 | Stage 1 cool 3/8 (424.3 K) | done | 1,000,000 | 151.2 | 151.0 | 0.8036 ± 0.0007 | 28822.3 ± 55.3 | no |
| 4 | Stage 1 cool 4/8 (399.1 K) | done | 1,000,000 | 125.9 | 125.9 | 0.8164 ± 0.0003 | 26693.8 ± 51.3 | **yes** |
| 5 | Stage 1 cool 5/8 (373.8 K) | done | 1,000,000 | 100.7 | 100.8 | 0.8274 ± 0.0005 | 24740.1 ± 48.9 | no |
| 6 | Stage 1 cool 6/8 (348.6 K) | done | 1,000,000 | 75.5 | 75.5 | 0.8374 ± 0.0006 | 22688.2 ± 47.7 | no |
| 7 | Stage 1 cool 7/8 (323.4 K) | done | 1,000,000 | 50.2 | 50.2 | 0.8504 ± 0.0003 | 20596.9 ± 47.2 | no |
| 8 | Stage 1 cool 8/8 (298.1 K) | done | 1,000,000 | 25.0 | 25.1 | 0.8599 ± 0.0002 | 18673.6 ± 45.1 | no |

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

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

**step-cool density vs T (sweep overlaid once it exists)**

![step-cool density vs T (sweep overlaid once it exists)](progress_cool_vs_sweep.png)

