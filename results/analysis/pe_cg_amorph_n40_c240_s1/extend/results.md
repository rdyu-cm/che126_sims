# Hold analysis: pe_cg_amorph_n40_c240_s1 / extend

- system: `pe_cg_amorph_n40_c240_s1` (cg); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_cg_amorph_n40_c240_s1/extend` (extend, status finished, node rdyu-rog, run code commit cb4513655e)
- analysis: `sepsim analyze hold` (D56), code commit e27e3a6c62 (dirty), 2026-11-09 18:57 on rdyu-server
- segment: Stage 1: NPT hold extension 60000 ps at 500 K, 1 atm (60 ns planned, complete); thermo window without the first 10% of rows, SEM from 100 ps block means (D55)
- trajectory: `/home/rdyu/projects/che126_sims/results/runs/pe_cg_amorph_n40_c240_s1/prep/hold.dcd` read ahead of the hold DCD as one continuous trajectory (D47)

## Thermo

| window (ns) | T (°C) | density (g/cm³) | H (kcal/mol) | V (Å³) | κ_T (GPa⁻¹) |
|---|---|---|---|---|---|
| 54.00 | 226.84 ± 0.03 | 0.72370 ± 0.00007 | 492.6 ± 3.6 | 309173 ± 31 | 2.146 ± 0.024 |

## Trajectory: mobility and chain size

8001 frames × 10 ps (80 ns); parts: hold.dcd 2000, hold_ext.dcd 6001.

| COM MSD max (Å²) at lag (ns) | D_COM (D55 criterion) | bond P2 1/e | Rg (Å) | R_ee (Å) | C_n plateau |
|---|---|---|---|---|---|
| 2120 at 40 | not diffusive (log-slope 0.91 at the longest lag, MSD/⟨Rg²⟩ 2.56) | 8.5 ps | 28.75 ± 0.34 | 71.9 ± 1.3 | 9.121 ± 0.299 |

- no burst DCDs (deck without D46 bursts): lags from the hold DCD only

## Chain relaxation (holds; D56)

End-to-end vector ACF ⟨R(t)·R(0)⟩/⟨R²⟩ and Rouse mode ACFs ⟨X_p(t)·X_p(0)⟩/⟨X_p²⟩, X_p = (1/N) Σ_n cos(pπ(n−½)/N) r_n over the backbone sites, every time origin, lags up to half the hold (40 ns here). Times in ns: the first 1/e crossing; if C stays above 1/e within the lag window the time is 'not reached' and only an exponential fit of ln C over 0.2 ≤ C ≤ 0.9 is given (marked extrap.: it extrapolates the early decay). τ_ee fit is that fit for R_ee. τ_1/τ_2 is 4 for Rouse chains. p²⟨X_p²⟩ (relative to p = 1, p = 2…5) is flat for an ideal Rouse chain; it falls at high p where the chain is stiffer than Gaussian on that scale. Crystallinity: D26 local alignment, fraction of backbone sites with p2 ≥ 0.4 (**uncalibrated, melt baseline**: no crystal reference, so the number is a baseline for an amorphous box, not a calibrated crystallinity) and the largest crystalline cluster (sites).

| T (°C) | τ_ee 1/e (ns) | τ_ee fit (ns) | τ_1 (ns) | τ_2 (ns) | τ_3 (ns) | τ_1/τ_2 (Rouse 4) | p²⟨X_p²⟩ / p=1 (p = 2…5) | crystallinity |
|---|---|---|---|---|---|---|---|---|
| 226.85 | 11.1 | 13.9 | 14.5 | 3.36 | 1.21 | 4.31 | 0.96 / 0.88 / 0.86 / 0.80 | 0.093 (max 0.110; cluster ≤ 56) |

CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; docs/experiment_comparison.md), so MSD, D_COM, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.

## Caveats

- Relaxation times use lags up to half the analysed hold (40 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; docs/experiment_comparison.md), so MSD, D_COM, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.

## Plots

**backbone-site and chain COM MSD**

![backbone-site and chain COM MSD](msd.png)

**bond P2 autocorrelation**

![bond P2 autocorrelation](p2_acf.png)

**end-to-end and Rouse mode ACFs, p²τ_p vs p**

![end-to-end and Rouse mode ACFs, p²τ_p vs p](relaxation.png)

