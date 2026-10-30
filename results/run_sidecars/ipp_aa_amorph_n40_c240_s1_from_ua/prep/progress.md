# ipp_aa_amorph_n40_c240_s1_from_ua / prep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-26 11:04 PDT, ended 2026-10-29 04:25 PDT
- progress: 100.0% of 14,140,000 MD steps; 14/14 segments done
- speed: 5.12 ns/day (59.2 steps/s, Performance line of segment 14)
- log updated 2026-10-29 04:25 PDT (29.7 h ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 PASS C_n 5.58; R_ee not decorrelated (0.72 at 2.5 ns); MSD/Rg2 0.25; drift seg 9,12

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: soft-core push-off | done | 40,000 | 226.9 | 226.2 | 0.7588 ± 0.0000 | 481630.0 ± 40827.1 |  |
| 2 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 3 | Stage 4: NVT 100 ps at 500 K | done | 100,000 | 226.9 | 226.2 | 0.7588 ± 0.0000 | 88091.1 ± 356.3 |  |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 200,000 | 226.9 | 226.8 | 0.7545 ± 0.0004 | 88656.7 ± 198.8 | no |
| 5 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 800,000 | 226.9 | 226.9 | 0.7431 ± 0.0005 | 88025.6 ± 94.8 | no |
| 6 | Stage 6: NPT hold 5000 ps at 500 K, 1 atm | done | 5,000,000 | 226.9 | 226.9 | 0.7426 ± 0.0002 | 88097.9 ± 37.9 | no |
| 7 | Stage 7 cool 1/8 (474.8 K) | done | 1,000,000 | 201.6 | 201.6 | 0.7578 ± 0.0007 | 83478.8 ± 79.1 | no |
| 8 | Stage 7 cool 2/8 (449.5 K) | done | 1,000,000 | 176.4 | 176.5 | 0.7733 ± 0.0004 | 78755.4 ± 80.9 | no |
| 9 | Stage 7 cool 3/8 (424.3 K) | done | 1,000,000 | 151.2 | 151.2 | 0.7876 ± 0.0009 | 73941.1 ± 76.5 | **yes** |
| 10 | Stage 7 cool 4/8 (399.1 K) | done | 1,000,000 | 125.9 | 125.9 | 0.8050 ± 0.0006 | 69147.3 ± 78.1 | no |
| 11 | Stage 7 cool 5/8 (373.8 K) | done | 1,000,000 | 100.7 | 100.7 | 0.8207 ± 0.0003 | 64457.3 ± 73.2 | no |
| 12 | Stage 7 cool 6/8 (348.6 K) | done | 1,000,000 | 75.5 | 75.5 | 0.8362 ± 0.0005 | 59646.3 ± 70.8 | **yes** |
| 13 | Stage 7 cool 7/8 (323.4 K) | done | 1,000,000 | 50.2 | 50.2 | 0.8519 ± 0.0003 | 54901.0 ± 67.8 | no |
| 14 | Stage 7 cool 8/8 (298.1 K) | done | 1,000,000 | 25.0 | 25.0 | 0.8654 ± 0.0002 | 50088.5 ± 61.6 | no |

## 500 K hold checks

- hold.dcd 500 frames, every 10 ps (5.0 ns) (cached, computed 2026-10-27 15:00 PDT)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **5.576** vs melt 6.15 ±10% (within); halves 5.582 -> 5.570 (Δ -0.012 ± 0.160), drift no -> **PASS**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.718 at 2.50 ns (half the hold); 1/e **not reached**; <R²> = 2117 Å²
- chain COM MSD(2.50 ns) = 84 Å² vs <Rg²> = 331 Å²: ratio **0.25**

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

