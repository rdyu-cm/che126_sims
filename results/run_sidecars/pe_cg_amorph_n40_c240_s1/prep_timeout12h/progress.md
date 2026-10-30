# pe_cg_amorph_n40_c240_s1 / prep_timeout12h

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-10-20 23:57 UTC
- progress: 59.7% of 6,210,000 MD steps; 7/13 segments done; current: 8 Stage 7 cool 3/8 (424.3 K)
- speed: 78.62 ns/day (91.0 steps/s, running segment (last hour of thermo))
- log updated 2026-10-21 11:57 UTC (9.2 d ago); report 2026-10-30 17:20 UTC on rdyu-server
- checks: D37 FAIL C_n 8.28 (vs 6.7); R_ee not decorrelated (0.38 at 10.0 ns); MSD/Rg2 0.77; drift seg 5

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 2 | Stage 4: NVT 100 ps at 500 K | done | 10,000 | 226.9 | 224.8 | 0.3000 ± 0.0000 | 1518.8 ± 82.5 |  |
| 3 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 40,000 | 226.9 | 227.8 | 0.7361 ± 0.0006 | 908.3 ± 22.2 | no |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 160,000 | 226.9 | 226.5 | 0.7234 ± 0.0004 | 517.0 ± 10.8 | no |
| 5 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | done | 2,000,000 | 226.9 | 226.9 | 0.7234 ± 0.0001 | 506.8 ± 3.2 | **yes** |
| 6 | Stage 7 cool 1/8 (474.8 K) | done | 500,000 | 201.6 | 201.7 | 0.7372 ± 0.0002 | -129.9 ± 6.2 | no |
| 7 | Stage 7 cool 2/8 (449.5 K) | done | 500,000 | 176.4 | 176.2 | 0.7509 ± 0.0002 | -786.0 ± 6.0 | no |
| 8 | Stage 7 cool 3/8 (424.3 K) | running | 498,612/500,000 | 151.2 |  |  |  |  |
| 9 | Stage 7 cool 4/8 (399.1 K) | pending | 500,000 | 125.9 |  |  |  |  |
| 10 | Stage 7 cool 5/8 (373.8 K) | pending | 500,000 | 100.7 |  |  |  |  |
| 11 | Stage 7 cool 6/8 (348.6 K) | pending | 500,000 | 75.5 |  |  |  |  |
| 12 | Stage 7 cool 7/8 (323.4 K) | pending | 500,000 | 50.2 |  |  |  |  |
| 13 | Stage 7 cool 8/8 (298.1 K) | pending | 500,000 | 25.0 |  |  |  |  |

## 500 K hold checks

- hold.dcd 2000 frames, every 10 ps (20.0 ns) (cached)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **8.283** vs melt 6.7 ±10% (**outside**); halves 8.459 -> 8.106 (Δ -0.353 ± 0.204), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.376 at 10.00 ns (half the hold); 1/e **not reached**; <R²> = 4721 Å²
- chain COM MSD(10.00 ns) = 588 Å² vs <Rg²> = 766 Å²: ratio **0.77**

## Plots

**step-cool density vs T (sweep overlaid once it exists)**

![step-cool density vs T (sweep overlaid once it exists)](progress_cool_vs_sweep.png)

**500 K hold: C_n vs n**

![500 K hold: C_n vs n](progress_hold_cn.png)

**500 K hold: C_n plateau vs time**

![500 K hold: C_n plateau vs time](progress_hold_cn_time.png)

**500 K hold: chain COM MSD vs <Rg²>**

![500 K hold: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**500 K hold: end-to-end vector ACF**

![500 K hold: end-to-end vector ACF](progress_hold_ree_acf.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

