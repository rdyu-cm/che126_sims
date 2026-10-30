# pe_aa_amorph_n40_c240_s1 / prep

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-21 12:36 PDT, ended 2026-10-24 01:09 PDT
- progress: 100.0% of 14,140,000 MD steps; 14/14 segments done
- speed: 5.44 ns/day (62.9 steps/s, Performance line of segment 14)
- log updated 2026-10-24 01:09 PDT (6.4 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 6.09 (drift); R_ee not decorrelated (0.72 at 2.5 ns); MSD/Rg2 0.16

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: soft-core push-off | done | 40,000 | 226.9 | 227.8 | 0.3000 ± 0.0000 | 182981.8 ± 6655.4 |  |
| 2 | Stage 2: minimize with the full force field | done | min |  |  |  |  |  |
| 3 | Stage 4: NVT 100 ps at 500 K | done | 100,000 | 226.9 | 226.9 | 0.3000 ± 0.0000 | 85782.8 ± 234.5 |  |
| 4 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 1/2) | done | 200,000 | 226.9 | 226.8 | 0.7223 ± 0.0009 | 85055.7 ± 186.0 | no |
| 5 | Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2) | done | 800,000 | 226.9 | 227.0 | 0.7130 ± 0.0005 | 84527.8 ± 98.2 | no |
| 6 | Stage 6: NPT hold 5000 ps at 500 K, 1 atm | done | 5,000,000 | 226.9 | 226.8 | 0.7144 ± 0.0002 | 84505.8 ± 38.2 | no |
| 7 | Stage 7 cool 1/8 (474.8 K) | done | 1,000,000 | 201.6 | 201.6 | 0.7297 ± 0.0004 | 79719.1 ± 80.0 | no |
| 8 | Stage 7 cool 2/8 (449.5 K) | done | 1,000,000 | 176.4 | 176.4 | 0.7457 ± 0.0004 | 75004.1 ± 79.9 | no |
| 9 | Stage 7 cool 3/8 (424.3 K) | done | 1,000,000 | 151.2 | 151.1 | 0.7640 ± 0.0004 | 69960.3 ± 82.0 | no |
| 10 | Stage 7 cool 4/8 (399.1 K) | done | 1,000,000 | 125.9 | 125.8 | 0.7807 ± 0.0004 | 65157.5 ± 73.6 | no |
| 11 | Stage 7 cool 5/8 (373.8 K) | done | 1,000,000 | 100.7 | 100.7 | 0.7978 ± 0.0007 | 60114.7 ± 77.1 | no |
| 12 | Stage 7 cool 6/8 (348.6 K) | done | 1,000,000 | 75.5 | 75.5 | 0.8143 ± 0.0003 | 55246.4 ± 67.7 | no |
| 13 | Stage 7 cool 7/8 (323.4 K) | done | 1,000,000 | 50.2 | 50.2 | 0.8321 ± 0.0005 | 50078.8 ± 68.1 | no |
| 14 | Stage 7 cool 8/8 (298.1 K) | done | 1,000,000 | 25.0 | 25.0 | 0.8483 ± 0.0004 | 45205.9 ± 73.3 | no |

## 500 K hold checks

- hold.dcd 500 frames, every 10 ps (5.0 ns) (cached)
- D37 C_n plateau (n ≥ 100 C, 200 frames): **6.087** vs melt 6.7 ±10% (within); halves 5.580 -> 6.594 (Δ +1.014 ± 0.215), drift **yes** -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.717 at 2.50 ns (half the hold); 1/e **not reached**; <R²> = 3554 Å²
- chain COM MSD(2.50 ns) = 96 Å² vs <Rg²> = 587 Å²: ratio **0.16**

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

