# pe_cg_amorph_n40_c240_s1 / extend

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-26 10:57 PDT, ended 2026-10-26 16:45 PDT
- progress: 100.0% of 6,000,000 MD steps; 1/1 segments done
- speed: 235.89 ns/day (273.0 steps/s, Performance line of segment 1)
- log updated 2026-10-26 16:45 PDT (3.7 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 9.11 (vs 6.7); D47 PASS (ACF 0.14 at 40.0 ns; MSD/Rg2 2.56; 80.0 ns)

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold extension 60000 ps at 500 K, 1 atm | done | 6,000,000 | 226.9 | 226.9 | 0.7236 ± 0.0001 | 498.6 ± 1.8 | no |

## 500 K hold checks (prep hold + extension, D47)

- hold.dcd 2000 frames + hold_ext.dcd 6001 frames, every 10 ps (80.0 ns combined), computed 2026-10-26 16:46 PDT
- D37 C_n plateau (n ≥ 100 C, 200 frames): **9.110** vs melt 6.7 ±10% (**outside**); halves 9.419 -> 8.802 (Δ -0.617 ± 0.396), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.137 at 40.00 ns (half the combined hold); 1/e at 11.12 ns; <R²> = 5176 Å²
- chain COM MSD(40.00 ns) = 2120 Å² vs <Rg²> = 827 Å²: ratio **2.56**
- D47 (ACF < 1/e: yes; MSD ≥ 2 <Rg²>: yes) -> **PASS**

## Plots

**500 K hold + extension: C_n vs n**

![500 K hold + extension: C_n vs n](progress_hold_cn.png)

**500 K hold + extension: C_n plateau vs time (prep/extension boundary dashed)**

![500 K hold + extension: C_n plateau vs time (prep/extension boundary dashed)](progress_hold_cn_time.png)

**500 K hold + extension: chain COM MSD vs <Rg²>**

![500 K hold + extension: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**500 K hold + extension: end-to-end vector ACF**

![500 K hold + extension: end-to-end vector ACF](progress_hold_ree_acf.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

