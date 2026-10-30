# pe_ua_amorph_n40_c240_s1 / cool

- status: **finished** (manifest: finished), node rdyu-server, started 2026-10-29 11:30 UTC, ended 2026-10-30 15:50 UTC
- progress: 100.0% of 8,000,000 MD steps; 8/8 segments done
- speed: 12.90 ns/day (74.7 steps/s, Performance line of segment 8)
- log updated 2026-10-30 15:50 UTC (1.5 h ago); report 2026-10-30 17:20 UTC on rdyu-server
- checks: drift seg 3,4,7

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1 cool 1/8 (474.8 K) | done | 1,000,000 | 201.6 | 201.6 | 0.7593 ± 0.0005 | 21761.3 ± 52.8 | no |
| 2 | Stage 1 cool 2/8 (449.5 K) | done | 1,000,000 | 176.4 | 176.3 | 0.7728 ± 0.0003 | 19922.4 ± 54.1 | no |
| 3 | Stage 1 cool 3/8 (424.3 K) | done | 1,000,000 | 151.2 | 151.2 | 0.7870 ± 0.0003 | 18140.4 ± 52.6 | **yes** |
| 4 | Stage 1 cool 4/8 (399.1 K) | done | 1,000,000 | 125.9 | 125.9 | 0.8016 ± 0.0003 | 16215.6 ± 48.5 | **yes** |
| 5 | Stage 1 cool 5/8 (373.8 K) | done | 1,000,000 | 100.7 | 100.8 | 0.8162 ± 0.0003 | 14289.5 ± 49.4 | no |
| 6 | Stage 1 cool 6/8 (348.6 K) | done | 1,000,000 | 75.5 | 75.4 | 0.8296 ± 0.0004 | 12330.7 ± 45.8 | no |
| 7 | Stage 1 cool 7/8 (323.4 K) | done | 1,000,000 | 50.2 | 50.2 | 0.8460 ± 0.0004 | 10303.4 ± 47.7 | **yes** |
| 8 | Stage 1 cool 8/8 (298.1 K) | done | 1,000,000 | 25.0 | 25.0 | 0.8601 ± 0.0002 | 8323.8 ± 47.2 | no |

## Plots

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

**step-cool density vs T (sweep overlaid once it exists)**

![step-cool density vs T (sweep overlaid once it exists)](progress_cool_vs_sweep.png)

