# ipp_ua_amorph_n40_c240_s1 / extend

- status: **cancelled/killed?** (manifest: started), node rdyu-rog, started 2026-10-23 12:05 PDT
- progress: 50.0% of 40,000,000 MD steps; 0/1 segments done; current: 1 Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm
- speed: 20.61 ns/day (119.3 steps/s, running segment (last hour of thermo))
- log updated 2026-10-26 11:02 PDT (4.0 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: D37 FAIL C_n 5.66 (drift); D47 PASS (ACF 0.19 at 30.0 ns; MSD/Rg2 2.06; 60.0 ns)

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm | running | 20,006,500/40,000,000 | 226.9 |  |  |  |  |

## 500 K hold checks (prep hold + extension, D47)

- hold.dcd 2000 frames + hold_ext.dcd 4002 frames, every 10 ps (60.0 ns combined) (cached, computed 2026-10-26 13:10 PDT)
- extension running: rechecked at most every 2 h
- D37 C_n plateau (n ≥ 100 C, 200 frames): **5.655** vs melt 6.15 ±10% (within); halves 4.949 -> 6.361 (Δ +1.412 ± 0.252), drift **yes** -> **FAIL**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.185 at 30.01 ns (half the combined hold); 1/e at 14.68 ns; <R²> = 2146 Å²
- chain COM MSD(30.01 ns) = 705 Å² vs <Rg²> = 343 Å²: ratio **2.06**
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

