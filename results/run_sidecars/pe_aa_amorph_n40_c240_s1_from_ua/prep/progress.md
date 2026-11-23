# pe_aa_amorph_n40_c240_s1_from_ua / prep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-30 09:16 PDT, ended 2026-11-01 23:57 PST
- progress: 100.0% of 14,140,000 MD steps; 14/14 segments done
- speed: 5.07 ns/day (58.7 steps/s, Performance line of segment 14)
- log updated 2026-11-01 23:57 PST (21.5 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: D37 FAIL C_n 8.57 (vs 6.7, drift); R_ee not decorrelated (0.82 at 2.5 ns); MSD/Rg2 0.08; drift seg 7,9; hyst max 0.44%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: soft-core push-off | done | 40,000 | 226.9 | 227.6 | 0.7452 ± 0.0000 | 448581.8 ± 9182.3 |  |
| 2 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 3 | Stage 4: NVT 100 ps at 500 K | done | 100,000 | 226.9 | 227.2 | 0.7452 ± 0.0000 | 85738.1 ± 49.7 |  |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 200,000 | 226.9 | 227.0 | 0.7258 ± 0.0010 | 84381.5 ± 39.9 | no |
| 5 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 800,000 | 226.9 | 227.0 | 0.7145 ± 0.0004 | 84405.8 ± 15.0 | no |
| 6 | Stage 6: NPT hold 5000 ps at 500 K, 1 atm | done | 5,000,000 | 226.9 | 226.9 | 0.7159 ± 0.0002 | 84397.4 ± 11.4 | no |
| 7 | Stage 7 cool 1/8 (474.8 K) | done | 1,000,000 | 201.6 | 201.6 | 0.7314 ± 0.0004 | 79674.0 ± 17.9 | **yes** |
| 8 | Stage 7 cool 2/8 (449.5 K) | done | 1,000,000 | 176.4 | 176.5 | 0.7466 ± 0.0003 | 74800.4 ± 12.5 | no |
| 9 | Stage 7 cool 3/8 (424.3 K) | done | 1,000,000 | 151.2 | 151.2 | 0.7619 ± 0.0007 | 70032.0 ± 18.4 | **yes** |
| 10 | Stage 7 cool 4/8 (399.1 K) | done | 1,000,000 | 125.9 | 125.8 | 0.7790 ± 0.0005 | 65029.4 ± 21.1 | no |
| 11 | Stage 7 cool 5/8 (373.8 K) | done | 1,000,000 | 100.7 | 100.7 | 0.7975 ± 0.0003 | 60135.1 ± 10.4 | no |
| 12 | Stage 7 cool 6/8 (348.6 K) | done | 1,000,000 | 75.5 | 75.4 | 0.8147 ± 0.0003 | 55228.8 ± 20.4 | no |
| 13 | Stage 7 cool 7/8 (323.4 K) | done | 1,000,000 | 50.2 | 50.3 | 0.8313 ± 0.0006 | 50114.1 ± 25.4 | no |
| 14 | Stage 7 cool 8/8 (298.1 K) | done | 1,000,000 | 25.0 | 25.0 | 0.8474 ± 0.0005 | 45195.1 ± 39.7 | no |

## 500 K hold checks

- hold.dcd 500 frames, every 10 ps (5.0 ns) (cached, computed 2026-10-31 12:20 PDT)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **8.571** vs melt 6.7 ±10% (**outside**); halves 8.899 -> 8.244 (Δ -0.654 ± 0.142), drift **yes** -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.817 at 2.50 ns (half the hold); 1/e **not reached**; <R²> = 4920 Å²
- chain COM MSD(2.50 ns) = 65 Å² vs <Rg²> = 784 Å²: ratio **0.08**

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7314 ± 0.0004 | outside sweep |  |
| 2 | 449.5 | 0.7466 ± 0.0003 | outside sweep |  |
| 3 | 424.3 | 0.7619 ± 0.0007 | 0.7646 | -0.346 |
| 4 | 399.1 | 0.7790 ± 0.0005 | 0.7816 | -0.334 |
| 5 | 373.8 | 0.7975 ± 0.0003 | 0.7979 | -0.058 |
| 6 | 348.6 | 0.8147 ± 0.0003 | 0.8173 | -0.317 |
| 7 | 323.4 | 0.8313 ± 0.0006 | 0.8347 | -0.409 |
| 8 | 298.1 | 0.8474 ± 0.0005 | 0.8512 | -0.436 |

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

