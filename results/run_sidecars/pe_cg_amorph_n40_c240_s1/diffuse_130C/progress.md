# pe_cg_amorph_n40_c240_s1 / diffuse_130C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-02 19:07 UTC, ended 2026-11-04 19:34 UTC
- progress: 100.0% of 30,000,000 MD steps; 1/1 segments done
- speed: 222.21 ns/day (257.2 steps/s, Performance line of segment 1)
- log updated 2026-11-04 22:33 UTC (18.8 d ago); report 2026-11-23 18:50 UTC on rdyu-rog
- checks: D_COM diffusive 5.3e-07 cm²/s over 58.3–150 ns; η_Rouse 0.025 Pa·s; MSD/Rg2 5.10

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: NPT hold 300000 ps at 403.15 K | done | 30,000,000 | 130.0 | 130.0 | 0.7758 ± 0.0000 | -1974.9 ± 3.9 | no |

## NPT hold at 130 C: chain diffusion (D53)

- hold.dcd 3001 frames, every 100 ps (300.0 ns), computed 2026-11-04 22:40 UTC
- D_COM diffusive 5.3e-07 cm²/s over 58.3–150 ns; η_Rouse 0.025 Pa·s
- D_COM = 5.33e-07 ± 5.7e-09 cm²/s (slope/6 of the COM MSD over 58.3–150 ns, local log-slope ≥ 0.9 and MSD ≥ 2⟨Rg²⟩; error: spread of the slopes of the two halves of the range)
- Rouse viscosity η_R = ρ_N k_B T ⟨R_ee²⟩/(36 D) ≈ 0.0247 Pa·s (unentangled chains; a lower bound if they are entangled)
- C_n plateau (n ≥ 100 C, 200 frames): 10.656; halves 10.527 -> 10.784 (Δ +0.257 ± 0.277), drift no
- end-to-end ACF <R(t)·R(0)>/<R²>: 0.017 at 150.00 ns (half the hold); 1/e at 26.49 ns; <R²> = 6126 Å²
- chain COM MSD(150.00 ns) = 4881 Å² vs <Rg²> = 957 Å²: ratio **5.10**

## Plots

**NPT hold at 130 C: C_n vs n**

![NPT hold at 130 C: C_n vs n](progress_hold_cn.png)

**NPT hold at 130 C: C_n plateau vs time**

![NPT hold at 130 C: C_n plateau vs time](progress_hold_cn_time.png)

**NPT hold at 130 C: chain COM MSD vs <Rg²>**

![NPT hold at 130 C: chain COM MSD vs <Rg²>](progress_hold_com_msd.png)

**NPT hold at 130 C: end-to-end vector ACF**

![NPT hold at 130 C: end-to-end vector ACF](progress_hold_ree_acf.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

