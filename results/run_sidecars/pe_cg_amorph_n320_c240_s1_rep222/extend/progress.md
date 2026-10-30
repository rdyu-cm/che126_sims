# pe_cg_amorph_n320_c240_s1_rep222 / extend

- status: **cancelled/killed?** (manifest: started), node rdyu-rog, started 2026-10-29 04:25 PDT
- progress: 90.7% of 8,000,000 MD steps; 0/1 segments done; current: 1 Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm
- speed: 280.32 ns/day (324.4 steps/s, running segment (last hour of thermo))
- log updated 2026-10-29 10:34 PDT (23.6 h ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 9.18 (vs 6.7, drift); D47 PASS (ACF 0.09 at 36.3 ns; MSD/Rg2 2.65; 72.5 ns)
- note: ../prep/hold.dcd not found: chain checks use the extension alone

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm | running | 7,253,000/8,000,000 | 226.9 |  |  |  |  |

## 500 K hold checks (prep hold + extension, D47)

- hold_ext.dcd 7254 frames, every 10 ps (72.5 ns) (cached, computed 2026-10-29 12:40 PDT)
- extension running: rechecked at most every 2 h
- D37 C_n plateau (n ≥ 100 C, 200 frames): **9.184** vs melt 6.7 ±10% (**outside**); halves 8.950 -> 9.419 (Δ +0.470 ± 0.096), drift **yes** -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.087 at 36.27 ns (half the combined hold); 1/e at 10.88 ns; <R²> = 5217 Å²
- chain COM MSD(36.27 ns) = 2206 Å² vs <Rg²> = 831 Å²: ratio **2.65**
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

