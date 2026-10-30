# ipp_ua_amorph_n40_c240_s1 / prep

- status: **cancelled/killed?** (manifest: started), node rdyu-rog, started 2026-10-21 13:13 PDT
- progress: 60.8% of 18,570,000 MD steps; 6/14 segments done; current: 7 Stage 7 cool 1/8 (474.8 K)
- speed: 12.36 ns/day (71.6 steps/s, running segment (last hour of thermo))
- log updated 2026-10-23 11:47 PDT (6.9 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 4.77 (vs 6.15); R_ee not decorrelated (0.45 at 10.0 ns); MSD/Rg2 1.05; drift seg 6

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: soft-core push-off | done | 20,000 | 226.9 | 226.8 | 0.3000 ± 0.0000 | 100357.7 ± 2372.9 |  |
| 2 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 3 | Stage 4: NVT 100 ps at 500 K | done | 50,000 | 226.9 | 227.4 | 0.3000 ± 0.0000 | 36435.5 ± 222.7 |  |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 100,000 | 226.9 | 226.6 | 0.7740 ± 0.0005 | 35265.2 ± 196.1 | no |
| 5 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 400,000 | 226.9 | 226.7 | 0.7624 ± 0.0008 | 35328.5 ± 90.8 | no |
| 6 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | done | 10,000,000 | 226.9 | 226.8 | 0.7636 ± 0.0002 | 35379.1 ± 18.4 | **yes** |
| 7 | Stage 7 cool 1/8 (474.8 K) | running | 722,077/1,000,000 | 201.6 |  |  |  |  |
| 8 | Stage 7 cool 2/8 (449.5 K) | pending | 1,000,000 | 176.4 |  |  |  |  |
| 9 | Stage 7 cool 3/8 (424.3 K) | pending | 1,000,000 | 151.2 |  |  |  |  |
| 10 | Stage 7 cool 4/8 (399.1 K) | pending | 1,000,000 | 125.9 |  |  |  |  |
| 11 | Stage 7 cool 5/8 (373.8 K) | pending | 1,000,000 | 100.7 |  |  |  |  |
| 12 | Stage 7 cool 6/8 (348.6 K) | pending | 1,000,000 | 75.5 |  |  |  |  |
| 13 | Stage 7 cool 7/8 (323.4 K) | pending | 1,000,000 | 50.2 |  |  |  |  |
| 14 | Stage 7 cool 8/8 (298.1 K) | pending | 1,000,000 | 25.0 |  |  |  |  |

## 500 K hold checks

- hold.dcd 2000 frames, every 10 ps (20.0 ns) (cached)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **4.774** vs melt 6.15 ±10% (**outside**); halves 4.675 -> 4.873 (Δ +0.198 ± 0.380), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.445 at 10.00 ns (half the hold); 1/e **not reached**; <R²> = 1846 Å²
- chain COM MSD(10.00 ns) = 323 Å² vs <Rg²> = 307 Å²: ratio **1.05**

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

