# pe_ua_amorph_n40_c240_s1 / extend

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-10-23 19:05 UTC
- progress: 97.7% of 40,000,000 MD steps; 0/1 segments done; current: 1 Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm
- speed: 12.43 ns/day (71.9 steps/s, running segment (last hour of thermo))
- log updated 2026-10-29 11:30 UTC (29.8 h ago); report 2026-10-30 17:20 UTC on rdyu-server
- checks: D37 FAIL C_n 8.19 (vs 6.7); D47 PASS (ACF 0.16 at 49.1 ns; MSD/Rg2 2.28; 98.2 ns)

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm | running | 39,097,000/40,000,000 | 226.9 |  |  |  |  |

## 500 K hold checks (prep hold + extension, D47)

- hold.dcd 2000 frames + hold_ext.dcd 7820 frames, every 10 ps (98.2 ns combined) (cached, computed 2026-10-29 12:40 UTC)
- extension running: rechecked at most every 2 h
- D37 C_n plateau (n ≥ 100 C, 200 frames): **8.194** vs melt 6.7 ±10% (**outside**); halves 7.797 -> 8.590 (Δ +0.793 ± 0.526), drift no -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.163 at 49.10 ns (half the combined hold); 1/e at 19.27 ns; <R²> = 4724 Å²
- chain COM MSD(49.10 ns) = 1699 Å² vs <Rg²> = 746 Å²: ratio **2.28**
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

