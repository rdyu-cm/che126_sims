# pe_cg_amorph_n640_c240_s1_rep441 / extend

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-02 11:07 PST, ended 2026-11-06 02:06 PST
- progress: 100.0% of 8,000,000 MD steps; 1/1 segments done
- speed: 25.29 ns/day (29.3 steps/s, Performance line of segment 1)
- log updated 2026-11-06 02:07 PST (17.4 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: D37 FAIL C_n 8.93 (vs 6.7); D47 PASS (ACF 0.06 at 40.0 ns; MSD/Rg2 3.35; 80.0 ns)
- note: ../prep/hold.dcd not found: chain checks use the extension alone

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm | done | 8,000,000 | 226.9 | 226.8 | 0.7237 ± 0.0000 | 7925.5 ± 22.9 | no |

## 500 K hold checks (prep hold + extension, D47)

- hold_ext.dcd 801 frames, every 100 ps (80.0 ns), computed 2026-11-06 02:09 PST
- D37 C_n plateau (n ≥ 100 C, 200 frames): **8.935** vs melt 6.7 ±10% (**outside**); halves 8.967 -> 8.903 (Δ -0.065 ± 0.080), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.057 at 40.00 ns (half the combined hold); 1/e at 10.69 ns; <R²> = 5088 Å²
- chain COM MSD(40.00 ns) = 2723 Å² vs <Rg²> = 814 Å²: ratio **3.35**
- D47 (ACF < 1/e: yes; MSD ≥ 2 <Rg²>: yes) -> **PASS**

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

