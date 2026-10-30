# System summary: status, equilibration checks, measured properties

Snapshot 2026-10-30 16:45 UTC, compiled by hand from each run's `progress.md` (`sepsim progress`) and `results/analysis/*/sweep/results.md` (`sepsim analyze sweep`, D49). From now on `scripts/summarize_systems.py` regenerates this file whenever a run or analysis finishes.

**Checks.**

- **D47 (equilibrated melt):** at 500 K, after the prep hold plus any extension, both must hold at a lag of half the combined hold:
  - the end-to-end vector autocorrelation (ACF) is below 1/e;
  - the chain centre-of-mass MSD is at least 2⟨Rg²⟩.
- **D37 (C_n):** the plateau of C_n (n ≥ 100 carbons) is compared with the melt C∞ (PE 6.7, iPP 6.15, ±10%) and checked for drift.
- **Project rule:** a system that passes D47 without drift is accepted even when C_n misses the literature value. That deviation is a property of the model, not a failure, and no extra compute is spent on it.
- **"drift seg …":** those segments show a significant trend in a thermo quantity over their analysis window. It is informational.

## Overview

| System | Res. | Polymer | Chains × length | Sites | Stage now | Status | Equilibration (500 K) | Sweep analysis |
|---|---|---|---|---|---|---|---|---|
| `pe_cg_amorph_n40_c240_s1` | CG | PE | 40 × C240 | 3,200 beads | done | prep, extend, cool and sweep finished | **D47 pass** at 80 ns (ACF 0.14, MSD/Rg² 2.56); C_n 9.11 | yes |
| `pe_cg_amorph_n40_c1500_s1` | CG | PE | 40 × C1500 | 20,000 beads | done | prep, extend (500 ns), cool and sweep finished | D47 not reachable (ACF 0.68, MSD/Rg² 0.12 at 500 ns); accepted on a C_n plateau of 7.4 with no drift | yes |
| `pe_cg_amorph_n320_c240_s1_rep222` | CG | PE | 320 × C240 (2×2×2) | 25,600 beads | done | extend finished at 72.5 ns (no own cool or sweep; the pore uses the small bulk's runs) | **D47 pass** at 72.5 ns (ACF 0.09, MSD/Rg² 2.65); C_n 9.18 | — |
| `pe_cg_pore_w5nm_n40_c240_s1` | CG | PE | 40 × C240 | 3,200 beads | done | wide pore relax and 5 nm pore run finished | from the C240 bulk (80 ns) | pore analysis being built |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | CG | PE | 320 × C240 | 25,600 beads | done | wide pore relax and 5 nm pore run finished | from the 2×2×2 bulk (72.5 ns) | pore analysis being built |
| `pe_ua_amorph_n40_c240_s1` | UA | PE | 40 × C240 | 9,600 | sweep | **running, 0.4%**; ETA Nov 5 04:00 UTC | **D47 pass** at 98 ns (ACF 0.16, MSD/Rg² 2.28); C_n 8.19 | after the sweep |
| `pe_aa_amorph_n40_c240_s1_from_ua` | AA | PE | 40 × C240 | 28,880 | prep | **running, 0.3%** on the GPU; ETA Nov 2 00:00 UTC; sweep queued after it (~Nov 8) | built from the D47-passed UA box (`hold_ext_70ns.data`, 90 ns at 500 K) | after the sweep |
| `ipp_ua_amorph_n40_c240_s1` | UA | iPP | 40 × C240 | 12,760 | sweep | **running, 40%** (8/18 segments, at the 90 °C hold); ETA Nov 3 00:10 UTC | **D47 pass** at 60 ns (ACF 0.19, MSD/Rg² 2.06); C_n 5.66 (within ±10%, drifting) | after the sweep |
| `ipp_aa_amorph_n40_c240_s1_from_ua` | AA | iPP | 40 × C240 | — | sweep | prep finished; sweep **not started**, queued on the GPU after the AA PE sweep (~Nov 15) | built from the D47-passed UA box (`hold_ext_40ns.data`, 60 ns at 500 K); prep C_n 5.58 (**D37 pass**) | after the sweep |

**Not started (stage 2):**
- UA 5 nm pores: PE after its sweep (~Nov 5), iPP after its sweep (~Nov 3). They run on separate nodes; PE takes priority where they would share one.
- AA pores: after the AA sweeps.

**Superseded (kept, not used):**
- `pe_aa_amorph_n40_c240_s1`: direct AA build, prep only, chains unrelaxed. Replaced by `_from_ua`.
- The C240 sweep and pores from the 20 ns box (`*_old_20ns_box`).
- The cancelled 3 nm and 10 nm narrow pores.
- The old unrelaxed PE UA sweep.
- The first AA iPP sweep, cancelled so PE could go first.

## Measured properties (bulk sweeps, holds)

### `pe_cg_amorph_n40_c240_s1` (CG PE C240, 80 ns at 500 K)

| T (°C) | ρ (g/cm³) | κ_T (GPa⁻¹) | Rg (Å) | R_ee (Å) | C_n | P2 1/e (ps) | COM MSD max at 12.5 ns (Å²) | D_COM (cm²/s) |
|---|---|---|---|---|---|---|---|---|
| 25 | 0.83453 ± 0.00003 | 1.000 ± 0.015 | 31.24 ± 0.12 | 77.1 ± 0.5 | 10.27 ± 0.08 | 122.9 | 177 | not diffusive |
| 90 | 0.79783 ± 0.00004 | 1.292 ± 0.022 | 32.21 ± 0.21 | 84.2 ± 1.0 | 11.78 ± 0.19 | 25.5 | 396 | 5.1e-07 (marginal) |
| 130 | 0.77580 ± 0.00005 | 1.502 ± 0.027 | 30.84 ± 0.34 | 77.6 ± 2.1 | 10.58 ± 0.36 | 12.7 | 523 | not diffusive |
| 160 | 0.75938 ± 0.00006 | 1.662 ± 0.031 | 30.80 ± 0.39 | 78.3 ± 1.4 | 10.70 ± 0.34 | 7.6 | 573 | not diffusive |

| Window (°C) | α_V (10⁻⁴ K⁻¹) | Cp (J g⁻¹ K⁻¹)* |
|---|---|---|
| 25–160 | 6.919 ± 0.034 | 0.828 ± 0.002 |
| 25–90 | 6.917 ± 0.022 | 0.840 ± 0.004 |
| 90–160 | 7.032 ± 0.040 | 0.817 ± 0.003 |

### `pe_cg_amorph_n40_c1500_s1` (CG PE C1500, 500 ns at 500 K)

| T (°C) | ρ (g/cm³) | κ_T (GPa⁻¹) | Rg (Å) | R_ee (Å) | C_n | P2 1/e (ps) | COM MSD max at 12.5 ns (Å²) | D_COM |
|---|---|---|---|---|---|---|---|---|
| 25 | 0.83817 ± 0.00001 | 0.995 ± 0.015 | 67.79 ± 0.11 | 175.1 ± 1.4 | 7.91 ± 0.03 | 127.6 | 22 | not diffusive |
| 90 | 0.80154 ± 0.00002 | 1.265 ± 0.022 | 70.28 ± 0.13 | 179.3 ± 1.0 | 8.46 ± 0.03 | 26.9 | 30 | not diffusive |
| 130 | 0.78019 ± 0.00002 | 1.435 ± 0.026 | 70.04 ± 0.16 | 185.2 ± 1.6 | 8.44 ± 0.03 | 14.3 | 37 | not diffusive |
| 160 | 0.76444 ± 0.00002 | 1.572 ± 0.029 | 68.89 ± 0.25 | 169.2 ± 1.9 | 8.06 ± 0.07 | 8.8 | 45 | not diffusive |

| Window (°C) | α_V (10⁻⁴ K⁻¹) | Cp (J g⁻¹ K⁻¹)* |
|---|---|---|
| 25–160 | 6.783 ± 0.017 | 0.815 ± 0.004 |
| 25–90 | 6.866 ± 0.013 | 0.838 ± 0.003 |
| 90–160 | 6.757 ± 0.027 | 0.793 ± 0.001 |

\* Classical Cp, not comparable to experiment for CG/UA: those models remove degrees of freedom. CG times (P2, MSD) are model times; CG dynamics run faster than real PE.

### UA and AA systems

Sweeps are running or queued; numbers are added as each sweep is analyzed.

## Pores (stage 2)

| System | Gap (nominal, 25 °C) | Gap at 500 K | Wall thickness | Lateral box (25 °C) | Status |
|---|---|---|---|---|---|
| `pe_cg_pore_w5nm_n40_c240_s1` | 5.0 nm | 4.68 nm | 6.5 nm | 6.4 × 6.4 nm | run finished; analysis (γ, ρ(z), gap, surface mobility) being built |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | 5.0 nm | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm | run finished; analysis being built |
