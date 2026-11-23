# pe_cg_amorph_n40_c240_s1 / diffuse_25C

- status: **interrupted** (manifest: interrupted), node rdyu-rog, started 2026-10-30 11:01 PDT, ended 2026-11-02 05:57 PST
- progress: 92.5% of 30,000,000 MD steps; 0/1 segments done; current: 1 Stage 1: NPT hold 300000 ps at 298.15 K
- speed: 90.53 ns/day (104.8 steps/s, running segment (last hour of thermo))
- log updated 2026-11-02 05:59 PST (21.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: D_COM not diffusive (log-slope 0.91 at the longest lag, MSD/Rg² 1.61); MSD/Rg2 1.61

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold 300000 ps at 298.15 K | running | 27,752,800/30,000,000 | 25.0 |  |  |  |  |

## NPT hold at 25 C: chain diffusion (D53)

- hold.dcd 2733 frames, every 100 ps (273.2 ns) (cached, computed 2026-11-02 04:50 PST)
- hold running: rechecked at most every 2 h
- D_COM not diffusive (log-slope 0.91 at the longest lag, MSD/Rg² 1.61)
- COM MSD local log-slope 0.91 at the longest lag (max 1.01); diffusive needs ≥ 0.9 over a factor ≥ 2 in lag with COM MSD ≥ 2⟨Rg²⟩
- C_n plateau (n ≥ 100 C, 200 frames): 13.866; halves 13.860 -> 13.871 (Δ +0.011 ± 1.050), drift no
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.282 at 136.60 ns (half the hold); 1/e at 95.70 ns; <R²> = 8012 Å²
- chain COM MSD(136.60 ns) = 1984 Å² vs <Rg²> = 1233 Å²: ratio **1.61**

## Plots

**NPT hold at 25 C: C_n vs n**

![NPT hold at 25 C: C_n vs n](progress_hold_cn.png)

**NPT hold at 25 C: C_n plateau vs time**

![NPT hold at 25 C: C_n plateau vs time](progress_hold_cn_time.png)

**NPT hold at 25 C: chain COM MSD vs <Rg²>**

![NPT hold at 25 C: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**NPT hold at 25 C: end-to-end vector ACF**

![NPT hold at 25 C: end-to-end vector ACF](progress_hold_ree_acf.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

