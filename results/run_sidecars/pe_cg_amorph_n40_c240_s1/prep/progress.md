# pe_cg_amorph_n40_c240_s1 / prep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-21 13:13 PDT, ended 2026-10-21 18:07 PDT
- progress: 100.0% of 6,210,000 MD steps; 13/13 segments done
- speed: 293.95 ns/day (340.2 steps/s, Performance line of segment 13)
- log updated 2026-10-21 18:07 PDT (8.7 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 9.02 (vs 6.7); R_ee 1/e 8.84 ns; MSD/Rg2 0.90; drift seg 6,10,12,13

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 2 | Stage 4: NVT 100 ps at 500 K | done | 10,000 | 226.9 | 228.1 | 0.3000 ± 0.0000 | 1525.2 ± 42.1 |  |
| 3 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 40,000 | 226.9 | 225.7 | 0.7363 ± 0.0007 | 858.9 ± 23.0 | no |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 160,000 | 226.9 | 227.1 | 0.7218 ± 0.0004 | 545.9 ± 11.8 | no |
| 5 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | done | 2,000,000 | 226.9 | 226.8 | 0.7234 ± 0.0001 | 506.4 ± 3.2 | no |
| 6 | Stage 7 cool 1/8 (474.8 K) | done | 500,000 | 201.6 | 201.8 | 0.7369 ± 0.0002 | -133.3 ± 6.4 | **yes** |
| 7 | Stage 7 cool 2/8 (449.5 K) | done | 500,000 | 176.4 | 176.4 | 0.7509 ± 0.0002 | -787.9 ± 6.0 | no |
| 8 | Stage 7 cool 3/8 (424.3 K) | done | 500,000 | 151.2 | 151.3 | 0.7647 ± 0.0002 | -1445.0 ± 5.9 | no |
| 9 | Stage 7 cool 4/8 (399.1 K) | done | 500,000 | 125.9 | 126.1 | 0.7778 ± 0.0002 | -2069.8 ± 5.6 | no |
| 10 | Stage 7 cool 5/8 (373.8 K) | done | 500,000 | 100.7 | 100.8 | 0.7920 ± 0.0001 | -2746.2 ± 5.6 | **yes** |
| 11 | Stage 7 cool 6/8 (348.6 K) | done | 500,000 | 75.5 | 75.6 | 0.8054 ± 0.0001 | -3397.9 ± 5.3 | no |
| 12 | Stage 7 cool 7/8 (323.4 K) | done | 500,000 | 50.2 | 50.3 | 0.8194 ± 0.0001 | -4066.0 ± 5.2 | **yes** |
| 13 | Stage 7 cool 8/8 (298.1 K) | done | 500,000 | 25.0 | 24.9 | 0.8333 ± 0.0001 | -4728.4 ± 4.9 | **yes** |

## 500 K hold checks

- hold.dcd 2000 frames, every 10 ps (20.0 ns) (cached)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **9.015** vs melt 6.7 ±10% (**outside**); halves 8.689 -> 9.341 (Δ +0.652 ± 0.493), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.312 at 10.00 ns (half the hold); 1/e at 8.84 ns; <R²> = 5171 Å²
- chain COM MSD(10.00 ns) = 727 Å² vs <Rg²> = 812 Å²: ratio **0.90**

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

