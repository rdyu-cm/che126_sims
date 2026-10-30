# pe_cg_amorph_n40_c1500_s1 / prep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-24 01:10 PDT, ended 2026-10-24 06:16 PDT
- progress: 100.0% of 6,210,000 MD steps; 13/13 segments done
- speed: 288.63 ns/day (334.1 steps/s, Performance line of segment 13)
- log updated 2026-10-24 06:16 PDT (6.2 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 5.58 (vs 6.7, drift); R_ee not decorrelated (0.86 at 10.0 ns); MSD/Rg2 0.03; drift seg 5,10,11,12

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 2 | Stage 4: NVT 100 ps at 500 K | done | 10,000 | 226.9 | 226.9 | 0.3000 ± 0.0000 | 7529.8 ± 115.2 |  |
| 3 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 40,000 | 226.9 | 227.0 | 0.7395 ± 0.0003 | 6296.5 ± 55.7 | no |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 160,000 | 226.9 | 226.9 | 0.7256 ± 0.0002 | 4330.7 ± 27.7 | no |
| 5 | Stage 6: NPT hold 20000 ps at 500 K, 1 atm | done | 2,000,000 | 226.9 | 226.9 | 0.7264 ± 0.0000 | 4100.2 ± 8.0 | **yes** |
| 6 | Stage 7 cool 1/8 (474.8 K) | done | 500,000 | 201.6 | 201.6 | 0.7398 ± 0.0001 | 142.1 ± 15.4 | no |
| 7 | Stage 7 cool 2/8 (449.5 K) | done | 500,000 | 176.4 | 176.5 | 0.7534 ± 0.0001 | -3837.3 ± 14.9 | no |
| 8 | Stage 7 cool 3/8 (424.3 K) | done | 500,000 | 151.2 | 151.2 | 0.7672 ± 0.0001 | -7952.5 ± 14.4 | no |
| 9 | Stage 7 cool 4/8 (399.1 K) | done | 500,000 | 125.9 | 125.9 | 0.7810 ± 0.0001 | -12080.1 ± 13.9 | no |
| 10 | Stage 7 cool 5/8 (373.8 K) | done | 500,000 | 100.7 | 100.7 | 0.7950 ± 0.0001 | -16268.0 ± 13.7 | **yes** |
| 11 | Stage 7 cool 6/8 (348.6 K) | done | 500,000 | 75.5 | 75.5 | 0.8090 ± 0.0001 | -20452.2 ± 13.3 | **yes** |
| 12 | Stage 7 cool 7/8 (323.4 K) | done | 500,000 | 50.2 | 50.2 | 0.8234 ± 0.0000 | -24817.9 ± 12.9 | **yes** |
| 13 | Stage 7 cool 8/8 (298.1 K) | done | 500,000 | 25.0 | 25.0 | 0.8381 ± 0.0000 | -29228.1 ± 12.4 | no |

## 500 K hold checks

- hold.dcd 2000 frames, every 10 ps (20.0 ns) (cached, computed 2026-10-24 03:00 PDT)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **5.580** vs melt 6.7 ±10% (**outside**); halves 5.394 -> 5.767 (Δ +0.373 ± 0.094), drift **yes** -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.859 at 10.00 ns (half the hold); 1/e **not reached**; <R²> = 21732 Å²
- chain COM MSD(10.00 ns) = 84 Å² vs <Rg²> = 3239 Å²: ratio **0.03**

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

