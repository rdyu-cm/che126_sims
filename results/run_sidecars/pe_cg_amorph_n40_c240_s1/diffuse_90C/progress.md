# pe_cg_amorph_n40_c240_s1 / diffuse_90C

- status: **interrupted** (manifest: interrupted), node rdyu-rog, started 2026-10-31 10:54 PDT, ended 2026-11-02 05:57 PST
- progress: 58.7% of 30,000,000 MD steps; 0/1 segments done; current: 1 Stage 1: NPT hold 300000 ps at 363.15 K
- speed: 89.71 ns/day (103.8 steps/s, running segment (last hour of thermo))
- log updated 2026-11-02 05:59 PST (21.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: D_COM not diffusive (log-slope 1.03 at the longest lag, MSD/Rg² 1.98); MSD/Rg2 1.98

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold 300000 ps at 363.15 K | running | 17,607,300/30,000,000 | 90.0 |  |  |  |  |

## NPT hold at 90 C: chain diffusion (D53)

- hold.dcd 1743 frames, every 100 ps (174.2 ns) (cached, computed 2026-11-02 05:30 PST)
- hold running: rechecked at most every 2 h
- D_COM not diffusive (log-slope 1.03 at the longest lag, MSD/Rg² 1.98)
- COM MSD local log-slope 1.03 at the longest lag (max 1.03); diffusive needs ≥ 0.9 over a factor ≥ 2 in lag with COM MSD ≥ 2⟨Rg²⟩
- C_n plateau (n ≥ 100 C, 200 frames): 11.422; halves 11.972 -> 10.872 (Δ -1.099 ± 0.519), drift **yes**
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.079 at 87.10 ns (half the hold); 1/e at 37.79 ns; <R²> = 6488 Å²
- chain COM MSD(87.10 ns) = 2049 Å² vs <Rg²> = 1033 Å²: ratio **1.98**

## Plots

**NPT hold at 90 C: C_n vs n**

![NPT hold at 90 C: C_n vs n](progress_hold_cn.png)

**NPT hold at 90 C: C_n plateau vs time**

![NPT hold at 90 C: C_n plateau vs time](progress_hold_cn_time.png)

**NPT hold at 90 C: chain COM MSD vs <Rg²>**

![NPT hold at 90 C: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**NPT hold at 90 C: end-to-end vector ACF**

![NPT hold at 90 C: end-to-end vector ACF](progress_hold_ree_acf.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

