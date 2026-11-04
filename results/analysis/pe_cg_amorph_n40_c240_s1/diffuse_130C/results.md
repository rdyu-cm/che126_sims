# Hold analysis: pe_cg_amorph_n40_c240_s1 / diffuse_130C

- system: `pe_cg_amorph_n40_c240_s1` (cg); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_cg_amorph_n40_c240_s1/diffuse_130C` (diffuse, status finished, node rdyu-rog, run code commit dc583962cf)
- analysis: `sepsim analyze hold` (D56), code commit 4b92aee8b9 (dirty), 2026-11-04 14:33 on rdyu-rog
- segment: Stage 1: NPT hold 300000 ps at 403.15 K (300 ns planned, complete); thermo window without the first 10% of rows, SEM from 100 ps block means (D55)

## Thermo

| window (ns) | T (°C) | density (g/cm³) | H (kcal/mol) | V (Å³) | κ_T (GPa⁻¹) |
|---|---|---|---|---|---|
| 270.00 | 130.01 ± 0.01 | 0.77580 ± 0.00004 | -1973.4 ± 2.4 | 288406 ± 16 | 1.482 ± 0.008 |

## Trajectory: mobility and chain size

3001 frames × 100 ps (300 ns).

| COM MSD max (Å²) at lag (ns) | D_COM (D55 criterion) | bond P2 1/e | Rg (Å) | R_ee (Å) | C_n plateau |
|---|---|---|---|---|---|
| 4881 at 150 | 5.31e-07 ± 1.8e-08 cm²/s (fit 71–150 ns) | 75.6 ps | 30.94 ± 0.15 | 78.3 ± 0.6 | 10.629 ± 0.149 |

- no burst DCDs (deck without D46 bursts): lags from the hold DCD only

## Chain relaxation (holds; D56)

End-to-end vector ACF ⟨R(t)·R(0)⟩/⟨R²⟩ and Rouse mode ACFs ⟨X_p(t)·X_p(0)⟩/⟨X_p²⟩, X_p = (1/N) Σ_n cos(pπ(n−½)/N) r_n over the backbone sites, every time origin, lags up to half the hold (150 ns here). Times in ns: the first 1/e crossing; if C stays above 1/e within the lag window the time is 'not reached' and only an exponential fit of ln C over 0.2 ≤ C ≤ 0.9 is given (marked extrap.: it extrapolates the early decay). τ_ee fit is that fit for R_ee. τ_1/τ_2 is 4 for Rouse chains. p²⟨X_p²⟩ (relative to p = 1, p = 2…5) is flat for an ideal Rouse chain; it falls at high p where the chain is stiffer than Gaussian on that scale. Crystallinity: D26 local alignment, fraction of backbone sites with p2 ≥ 0.4 (**uncalibrated, melt baseline**: no crystal reference, so the number is a baseline for an amorphous box, not a calibrated crystallinity) and the largest crystalline cluster (sites).

| T (°C) | τ_ee 1/e (ns) | τ_ee fit (ns) | τ_1 (ns) | τ_2 (ns) | τ_3 (ns) | τ_1/τ_2 (Rouse 4) | p²⟨X_p²⟩ / p=1 (p = 2…5) | crystallinity |
|---|---|---|---|---|---|---|---|---|
| 130 | 26.5 | 35.2 | 34.1 | 7.78 | 3.15 | 4.38 | 0.96 / 0.92 / 0.85 / 0.77 | 0.103 (max 0.131; cluster ≤ 86) |

CG times are model times: SDK PE chains move ≈ 4.07× faster than real PE (Hall et al. 2019; docs/experiment_comparison.md), so multiply by 4.07 before comparing with experiment.

## Caveats

- Relaxation times use lags up to half the analysed hold (150 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D_COM and relaxation times are model times (docs/experiment_comparison.md).

## Plots

**backbone-site and chain COM MSD**

![backbone-site and chain COM MSD](msd.png)

**bond P2 autocorrelation**

![bond P2 autocorrelation](p2_acf.png)

**end-to-end and Rouse mode ACFs, p²τ_p vs p**

![end-to-end and Rouse mode ACFs, p²τ_p vs p](relaxation.png)

