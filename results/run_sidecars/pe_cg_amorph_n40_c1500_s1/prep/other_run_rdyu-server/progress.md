# pe_cg_amorph_n40_c1500_s1 / prep

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-10-20 23:58 UTC
- progress: 23.4% of 6,210,000 MD steps; 4/13 segments done; current: 5 Stage 6: NPT hold 20000 ps at 500 K, 1 atm
- speed: 24.44 ns/day (28.3 steps/s, running segment (last hour of thermo))
- log updated 2026-10-21 19:54 UTC (8.9 d ago); report 2026-10-30 17:20 UTC on rdyu-server

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 2 | Stage 4: NVT 100 ps at 500 K | done | 10,000 | 226.9 | 226.6 | 0.3000 ± 0.0000 | 7654.7 ± 202.1 |  |
| 3 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 40,000 | 226.9 | 226.6 | 0.7394 ± 0.0003 | 6264.3 ± 55.3 | no |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 160,000 | 226.9 | 226.8 | 0.7255 ± 0.0002 | 4392.2 ± 27.8 | no |
| 5 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | running | 1,243,216/2,000,000 | 226.9 |  |  |  |  |
| 6 | Stage 7 cool 1/8 (474.8 K) | pending | 500,000 | 201.6 |  |  |  |  |
| 7 | Stage 7 cool 2/8 (449.5 K) | pending | 500,000 | 176.4 |  |  |  |  |
| 8 | Stage 7 cool 3/8 (424.3 K) | pending | 500,000 | 151.2 |  |  |  |  |
| 9 | Stage 7 cool 4/8 (399.1 K) | pending | 500,000 | 125.9 |  |  |  |  |
| 10 | Stage 7 cool 5/8 (373.8 K) | pending | 500,000 | 100.7 |  |  |  |  |
| 11 | Stage 7 cool 6/8 (348.6 K) | pending | 500,000 | 75.5 |  |  |  |  |
| 12 | Stage 7 cool 7/8 (323.4 K) | pending | 500,000 | 50.2 |  |  |  |  |
| 13 | Stage 7 cool 8/8 (298.1 K) | pending | 500,000 | 25.0 |  |  |  |  |

## 500 K hold checks

- hold (segment 5) not complete yet

## Plots

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

