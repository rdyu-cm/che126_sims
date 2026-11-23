# pe_ua_amorph_n40_c240_s1 / cool

- status: **finished** (manifest: finished), node rdyu-server, started 2026-10-29 11:30 UTC, ended 2026-10-30 15:50 UTC
- progress: 100.0% of 8,000,000 MD steps; 8/8 segments done
- speed: 12.90 ns/day (74.7 steps/s, Performance line of segment 8)
- log updated 2026-10-30 15:50 UTC (24.1 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: drift seg 3,4,7; hyst max 0.36%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1 cool 1/8 (474.8 K) | done | 1,000,000 | 201.6 | 201.6 | 0.7593 ± 0.0006 | 21761.3 ± 12.9 | no |
| 2 | Stage 1 cool 2/8 (449.5 K) | done | 1,000,000 | 176.4 | 176.3 | 0.7728 ± 0.0003 | 19922.4 ± 6.0 | no |
| 3 | Stage 1 cool 3/8 (424.3 K) | done | 1,000,000 | 151.2 | 151.2 | 0.7870 ± 0.0005 | 18140.4 ± 9.6 | **yes** |
| 4 | Stage 1 cool 4/8 (399.1 K) | done | 1,000,000 | 125.9 | 125.9 | 0.8016 ± 0.0004 | 16215.6 ± 15.8 | **yes** |
| 5 | Stage 1 cool 5/8 (373.8 K) | done | 1,000,000 | 100.7 | 100.8 | 0.8162 ± 0.0002 | 14289.5 ± 8.2 | no |
| 6 | Stage 1 cool 6/8 (348.6 K) | done | 1,000,000 | 75.5 | 75.4 | 0.8296 ± 0.0005 | 12330.7 ± 14.1 | no |
| 7 | Stage 1 cool 7/8 (323.4 K) | done | 1,000,000 | 50.2 | 50.2 | 0.8460 ± 0.0004 | 10303.4 ± 10.5 | **yes** |
| 8 | Stage 1 cool 8/8 (298.1 K) | done | 1,000,000 | 25.0 | 25.0 | 0.8601 ± 0.0002 | 8323.8 ± 7.2 | no |

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

## Plots

**step-cool density vs T (sweep overlaid once it exists)**

![step-cool density vs T (sweep overlaid once it exists)](progress_cool_vs_sweep.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

