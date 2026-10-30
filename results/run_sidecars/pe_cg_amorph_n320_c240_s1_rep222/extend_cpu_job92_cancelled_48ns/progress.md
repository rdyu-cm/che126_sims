# pe_cg_amorph_n320_c240_s1_rep222 / extend_cpu_job92_cancelled_48ns

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-10-26 23:51 UTC
- progress: 61.5% of 8,000,000 MD steps; 0/1 segments done; current: 1 Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm
- speed: 20.03 ns/day (23.2 steps/s, running segment (last hour of thermo))
- log updated 2026-10-29 11:28 UTC (29.9 h ago); report 2026-10-30 17:20 UTC on rdyu-server
- checks: D37 FAIL C_n 9.06 (vs 6.7); D47 FAIL (ACF 0.15 at 24.6 ns; MSD/Rg2 1.81; 49.2 ns)
- note: ../prep/hold.dcd not found: chain checks use the extension alone

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm | running | 4,916,900/8,000,000 | 226.9 |  |  |  |  |

## 500 K hold checks (prep hold + extension, D47)

- hold_ext.dcd 4917 frames, every 10 ps (49.2 ns) (cached, computed 2026-10-29 12:40 UTC)
- extension running: rechecked at most every 2 h
- D37 C_n plateau (n ≥ 100 C, 200 frames): **9.059** vs melt 6.7 ±10% (**outside**); halves 9.118 -> 9.000 (Δ -0.118 ± 0.185), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.150 at 24.58 ns (half the combined hold); 1/e at 10.76 ns; <R²> = 5166 Å²
- chain COM MSD(24.58 ns) = 1489 Å² vs <Rg²> = 823 Å²: ratio **1.81**
- D47 (ACF < 1/e: yes; MSD ≥ 2 <Rg²>: no) -> **FAIL**

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

