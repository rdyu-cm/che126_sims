# pe_ua_amorph_n40_c240_s1 / prep

- status: **finished** (manifest: finished), node rdyu-server, started 2026-10-20 23:57 UTC, ended 2026-10-23 17:30 UTC
- progress: 100.0% of 18,570,000 MD steps; 14/14 segments done
- speed: 14.18 ns/day (82.0 steps/s, Performance line of segment 14)
- log updated 2026-10-23 17:30 UTC (7.0 d ago); report 2026-10-30 17:20 UTC on rdyu-server
- checks: D37 FAIL C_n 7.31 (drift); R_ee not decorrelated (0.47 at 10.0 ns); MSD/Rg2 0.63; drift seg 13

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: soft-core push-off | done | 20,000 | 226.9 | 226.9 | 0.3000 ± 0.0000 | 34844.6 ± 465.9 |  |
| 2 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 3 | Stage 4: NVT 100 ps at 500 K | done | 50,000 | 226.9 | 227.1 | 0.3000 ± 0.0000 | 24126.7 ± 284.6 |  |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 100,000 | 226.9 | 226.6 | 0.7544 ± 0.0004 | 23851.3 ± 200.3 | no |
| 5 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 400,000 | 226.9 | 227.1 | 0.7434 ± 0.0003 | 23686.9 ± 94.0 | no |
| 6 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | done | 10,000,000 | 226.9 | 226.8 | 0.7459 ± 0.0002 | 23612.5 ± 17.7 | no |
| 7 | Stage 7 cool 1/8 (474.8 K) | done | 1,000,000 | 201.6 | 201.5 | 0.7601 ± 0.0005 | 21779.5 ± 63.3 | no |
| 8 | Stage 7 cool 2/8 (449.5 K) | done | 1,000,000 | 176.4 | 176.4 | 0.7736 ± 0.0004 | 19982.3 ± 52.4 | no |
| 9 | Stage 7 cool 3/8 (424.3 K) | done | 1,000,000 | 151.2 | 151.2 | 0.7860 ± 0.0002 | 18133.4 ± 54.9 | no |
| 10 | Stage 7 cool 4/8 (399.1 K) | done | 1,000,000 | 125.9 | 125.9 | 0.8017 ± 0.0003 | 16224.8 ± 53.3 | no |
| 11 | Stage 7 cool 5/8 (373.8 K) | done | 1,000,000 | 100.7 | 100.7 | 0.8160 ± 0.0005 | 14201.6 ± 48.4 | no |
| 12 | Stage 7 cool 6/8 (348.6 K) | done | 1,000,000 | 75.5 | 75.5 | 0.8288 ± 0.0003 | 12387.5 ± 48.0 | no |
| 13 | Stage 7 cool 7/8 (323.4 K) | done | 1,000,000 | 50.2 | 50.3 | 0.8443 ± 0.0002 | 10386.7 ± 45.0 | **yes** |
| 14 | Stage 7 cool 8/8 (298.1 K) | done | 1,000,000 | 25.0 | 24.8 | 0.8582 ± 0.0003 | 8347.6 ± 43.8 | no |

## 500 K hold checks

- hold.dcd 2000 frames, every 10 ps (20.0 ns) (cached)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **7.307** vs melt 6.7 ±10% (within); halves 6.513 -> 8.100 (Δ +1.587 ± 0.372), drift **yes** -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.465 at 10.00 ns (half the hold); 1/e **not reached**; <R²> = 4257 Å²
- chain COM MSD(10.00 ns) = 427 Å² vs <Rg²> = 680 Å²: ratio **0.63**

## Plots

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

**500 K hold: C_n vs n**

![500 K hold: C_n vs n](progress_hold_cn.png)

**500 K hold: C_n plateau vs time**

![500 K hold: C_n plateau vs time](progress_hold_cn_time.png)

**500 K hold: end-to-end vector ACF**

![500 K hold: end-to-end vector ACF](progress_hold_ree_acf.png)

**500 K hold: chain COM MSD vs <Rg²>**

![500 K hold: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**step-cool density vs T (sweep overlaid once it exists)**

![step-cool density vs T (sweep overlaid once it exists)](progress_cool_vs_sweep.png)

