# ipp_ua_amorph_n40_c240_s1 / prep_server_cancelled

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-10-20 23:57 UTC
- progress: 14.7% of 18,570,000 MD steps; 5/14 segments done; current: 6 Stage 6: NPT hold 20000 ps at 500 K, 1 atm
- speed: 6.33 ns/day (36.6 steps/s, running segment (last hour of thermo))
- log updated 2026-10-21 20:12 UTC (8.9 d ago); report 2026-10-30 17:20 UTC on rdyu-server

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: soft-core push-off | done | 20,000 | 226.9 | 226.7 | 0.3000 ± 0.0000 | 99936.7 ± 2051.4 |  |
| 2 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 3 | Stage 4: NVT 100 ps at 500 K | done | 50,000 | 226.9 | 226.2 | 0.3000 ± 0.0000 | 36376.7 ± 327.5 |  |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 100,000 | 226.9 | 227.4 | 0.7720 ± 0.0007 | 35755.6 ± 193.5 | no |
| 5 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 400,000 | 226.9 | 226.9 | 0.7627 ± 0.0006 | 35526.6 ± 105.8 | no |
| 6 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | running | 2,155,935/10,000,000 | 226.9 |  |  |  |  |
| 7 | Stage 7 cool 1/8 (474.8 K) | pending | 1,000,000 | 201.6 |  |  |  |  |
| 8 | Stage 7 cool 2/8 (449.5 K) | pending | 1,000,000 | 176.4 |  |  |  |  |
| 9 | Stage 7 cool 3/8 (424.3 K) | pending | 1,000,000 | 151.2 |  |  |  |  |
| 10 | Stage 7 cool 4/8 (399.1 K) | pending | 1,000,000 | 125.9 |  |  |  |  |
| 11 | Stage 7 cool 5/8 (373.8 K) | pending | 1,000,000 | 100.7 |  |  |  |  |
| 12 | Stage 7 cool 6/8 (348.6 K) | pending | 1,000,000 | 75.5 |  |  |  |  |
| 13 | Stage 7 cool 7/8 (323.4 K) | pending | 1,000,000 | 50.2 |  |  |  |  |
| 14 | Stage 7 cool 8/8 (298.1 K) | pending | 1,000,000 | 25.0 |  |  |  |  |

## 500 K hold checks

- hold (segment 6) not complete yet

## Plots

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

