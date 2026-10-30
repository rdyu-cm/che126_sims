# pe_aa_amorph_n40_c240_s1_from_ua / prep

- status: **running** (manifest: started), node rdyu-rog, started 2026-10-30 09:16 PDT
- progress: 1.7% of 14,140,000 MD steps; 3/14 segments done; current: 4 Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2)
- speed: 5.66 ns/day (65.6 steps/s, running segment (last hour of thermo))
- ETA: 2026-11-01 20:02 PST (58.9 h left)
- log updated 2026-10-30 10:10 PDT (0 min ago); report 2026-10-30 10:10 PDT on rdyu-rog

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: soft-core push-off | done | 40,000 | 226.9 | 227.6 | 0.7452 ± 0.0000 | 448581.8 ± 37273.3 |  |
| 2 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 3 | Stage 4: NVT 100 ps at 500 K | done | 100,000 | 226.9 | 227.2 | 0.7452 ± 0.0000 | 85738.1 ± 257.2 |  |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | running | 103,916/200,000 | 226.9 |  |  |  |  |
| 5 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | pending | 800,000 | 226.9 |  |  |  |  |
| 6 | Stage 6: NPT hold 5000 ps at 500 K, 1 atm | pending | 5,000,000 | 226.9 |  |  |  |  |
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

