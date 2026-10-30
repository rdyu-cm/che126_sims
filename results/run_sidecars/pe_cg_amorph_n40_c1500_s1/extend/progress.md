# pe_cg_amorph_n40_c1500_s1 / extend

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-24 06:18 PDT, ended 2026-10-25 19:01 PDT
- progress: 100.0% of 50,000,000 MD steps; 1/1 segments done
- speed: 324.99 ns/day (376.1 steps/s, Performance line of segment 1)
- log updated 2026-10-25 19:01 PDT (4.6 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 7.43 (vs 6.7); D47 FAIL (ACF 0.68 at 250.0 ns; MSD/Rg2 0.12; 500.0 ns); drift seg 1
- note: ../prep/hold.dcd has frames every 10 ps, the extension 100 ps: chain checks use the extension alone

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold extension 500000 ps at 500 K, 1 atm | done | 50,000,000 | 226.9 | 226.9 | 0.7287 ± 0.0000 | 3409.2 ± 1.6 | **yes** |

## 500 K hold checks (prep hold + extension, D47)

- hold_ext.dcd 5001 frames, every 100 ps (500.0 ns), computed 2026-10-25 19:10 PDT
- D37 C_n plateau (n ≥ 100 C, 200 frames): **7.426** vs melt 6.7 ±10% (**outside**); halves 7.324 -> 7.529 (Δ +0.205 ± 0.299), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.684 at 250.00 ns (half the combined hold); 1/e **not reached**; <R²> = 28913 Å²
- chain COM MSD(250.00 ns) = 519 Å² vs <Rg²> = 4323 Å²: ratio **0.12**
- D47 (ACF < 1/e: no; MSD ≥ 2 <Rg²>: no) -> **FAIL**

## Plots

**500 K hold + extension: C_n vs n**

![500 K hold + extension: C_n vs n](progress_hold_cn.png)

**500 K hold + extension: C_n plateau vs time**

![500 K hold + extension: C_n plateau vs time](progress_hold_cn_time.png)

**500 K hold + extension: chain COM MSD vs <Rg²>**

![500 K hold + extension: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**500 K hold + extension: end-to-end vector ACF**

![500 K hold + extension: end-to-end vector ACF](progress_hold_ree_acf.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

