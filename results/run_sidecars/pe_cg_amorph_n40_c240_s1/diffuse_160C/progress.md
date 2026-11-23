# pe_cg_amorph_n40_c240_s1 / diffuse_160C

- status: **interrupted** (manifest: interrupted), node rdyu-rog, started 2026-10-30 11:05 PDT, ended 2026-11-02 05:57 PST
- progress: 85.2% of 30,000,000 MD steps; 0/1 segments done; current: 1 Stage 1: NPT hold 300000 ps at 433.15 K
- speed: 84.01 ns/day (97.2 steps/s, running segment (last hour of thermo))
- log updated 2026-11-02 05:59 PST (21.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: D_COM diffusive 6e-07 cm²/s over 55.8–126 ns; η_Rouse 0.021 Pa·s; MSD/Rg2 5.15

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold 300000 ps at 433.15 K | running | 25,562,400/30,000,000 | 160.0 |  |  |  |  |

## NPT hold at 160 C: chain diffusion (D53)

- hold.dcd 2517 frames, every 100 ps (251.6 ns) (cached, computed 2026-11-02 04:50 PST)
- hold running: rechecked at most every 2 h
- D_COM diffusive 6e-07 cm²/s over 55.8–126 ns; η_Rouse 0.021 Pa·s
- D_COM = 6.01e-07 ± 3.3e-10 cm²/s (slope/6 of the COM MSD over 55.8–126 ns, local log-slope ≥ 0.9 and MSD ≥ 2⟨Rg²⟩; error: spread of the slopes of the two halves of the range)
- Rouse viscosity η_R = ρ_N k_B T ⟨R_ee²⟩/(36 D) ≈ 0.021 Pa·s (unentangled chains; a lower bound if they are entangled)
- C_n plateau (n ≥ 100 C, 200 frames): 9.755; halves 10.033 -> 9.476 (Δ -0.558 ± 0.338), drift no
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.006 at 125.80 ns (half the hold); 1/e at 16.84 ns; <R²> = 5598 Å²
- chain COM MSD(125.80 ns) = 4571 Å² vs <Rg²> = 888 Å²: ratio **5.15**

## Plots

**NPT hold at 160 C: C_n vs n**

![NPT hold at 160 C: C_n vs n](progress_hold_cn.png)

**NPT hold at 160 C: C_n plateau vs time**

![NPT hold at 160 C: C_n plateau vs time](progress_hold_cn_time.png)

**NPT hold at 160 C: chain COM MSD vs <Rg²>**

![NPT hold at 160 C: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**NPT hold at 160 C: end-to-end vector ACF**

![NPT hold at 160 C: end-to-end vector ACF](progress_hold_ree_acf.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

