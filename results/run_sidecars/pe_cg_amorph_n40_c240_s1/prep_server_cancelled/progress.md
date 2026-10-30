# pe_cg_amorph_n40_c240_s1 / prep_server_cancelled

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-10-21 19:55 UTC
- progress: 2.6% of 6,210,000 MD steps; 3/13 segments done; current: 4 Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2)
- speed: 127.65 ns/day (147.7 steps/s, running segment (last hour of thermo))
- log updated 2026-10-21 20:12 UTC (8.9 d ago); report 2026-10-30 17:20 UTC on rdyu-server

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 2 | Stage 4: NVT 100 ps at 500 K | done | 10,000 | 226.9 | 226.7 | 0.3000 ± 0.0000 | 1496.6 ± 39.0 |  |
| 3 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 40,000 | 226.9 | 227.0 | 0.7360 ± 0.0007 | 916.6 ± 22.4 | no |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | running | 111,582/160,000 | 226.9 |  |  |  |  |
| 5 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | pending | 2,000,000 | 226.9 |  |  |  |  |
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

