# System summary: tested properties and equilibration checks

- Generated: 2026-11-25 18:22 UTC
- Git commit: 28ccf81
- Inputs: runs `/home/rdyu/projects/che126_sims/results/runs`, `/home/rdyu/projects/che126_sims/results/run_sidecars`, `/home/rdyu/projects/che126_sims/results/progress/rdyu-rog`; analysis `/home/rdyu/projects/worktrees/puncture-wall-results/results/analysis`; systems `/home/rdyu/projects/worktrees/puncture-wall-results/systems`
- Regenerate: `uv run --frozen python scripts/summarize_systems.py`

**Checks (legend)**

- **D37 C<sub>n</sub>**: plateau of ⟨R²(n)⟩/(n l²) for n ≥ 100 carbons on the 500 K hold, compared with the melt C∞ at 500 K (PE 6.7, iPP 6.15, ±10%), and a drift test (second minus first half of the hold beyond 2 combined SEM).
- **D47**: end-to-end vector ACF < 1/e (0.368) **and** chain COM MSD ≥ 2⟨R<sub>g</sub>²⟩, both at a lag of half the combined 500 K hold (prep hold + extension).
- **Rule**: a system that passes D47 is accepted even if its C<sub>n</sub> misses the literature value; that miss is a model property, not a failure, and no more compute is spent on it. The C<sub>n</sub> value vs literature and its drift (taken over prep hold + extension, so it includes the unrelaxed prep) are shown as "info".
- Long CG chains (C ≥ 1000, i.e. C1500): whole-chain relaxation is out of reach, so D47 does not apply (D47); they rely on correct construction and the C<sub>n</sub> no-drift check.
- Pores and AA boxes converted from UA (ua2aa) inherit the equilibration of the bulk box they were built from.
- Run status comes from `sepsim progress` ("cancelled/killed?" = log silent > 6 h without a finished manifest; ETAs converted to UTC). Superseded systems and run directories (renamed old/cancelled runs, rebuilt sources) are listed separately and never used for the numbers.
- **"drift seg …"** (monitor flag): those segments show a significant trend in a thermo quantity over their analysis window. It is informational.

**Presentation figures:** [results/presentation](presentation/README.md) (`uv run --frozen python scripts/presentation_figures.py`)

**Convergence figures:** [overview](convergence_overview.png), [physical validity](validity_overview.png), [`pe_cg_amorph_n40_c240_s1`](convergence/pe_cg_amorph_n40_c240_s1.png), [`pe_cg_amorph_n40_c1500_s1`](convergence/pe_cg_amorph_n40_c1500_s1.png), [`pe_cg_amorph_n320_c240_s1_rep222`](convergence/pe_cg_amorph_n320_c240_s1_rep222.png), [`pe_cg_pore500k_w10nm_n40_c240_s1`](convergence/pe_cg_pore500k_w10nm_n40_c240_s1.png), [`pe_cg_pore_w5nm_n40_c240_s1`](convergence/pe_cg_pore_w5nm_n40_c240_s1.png), [`pe_cg_pore500k_w10nm_n320_c240_s1_rep222`](convergence/pe_cg_pore500k_w10nm_n320_c240_s1_rep222.png), [`pe_cg_pore_w5nm_n320_c240_s1_rep222`](convergence/pe_cg_pore_w5nm_n320_c240_s1_rep222.png), [`pe_ua_amorph_n40_c240_s1`](convergence/pe_ua_amorph_n40_c240_s1.png), [`pe_aa_amorph_n40_c240_s1_from_ua`](convergence/pe_aa_amorph_n40_c240_s1_from_ua.png), [`ipp_ua_amorph_n40_c240_s1`](convergence/ipp_ua_amorph_n40_c240_s1.png), [`ipp_aa_amorph_n40_c240_s1_from_ua`](convergence/ipp_aa_amorph_n40_c240_s1_from_ua.png)

## Overview

| System | Res | Polymer | Kind | Chains × length | Sites | Stage now | Status | Equilibration (D47) | C<sub>n</sub> plateau (D37) | Analysis |
|---|---|---|---|---|---|---|---|---|---|---|
| `pe_cg_crystal_7x10x27_s1` | CG | PE | crystal | 140 × C81 | 3,780 beads | done | finished: crystal, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c`, `tensile_25C`, `tensile_90C`, `tensile_130C`, `tensile_160C`, `tensile_75C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_85C`, `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_140C`, `tensile_150C`, `tensile_25C_r1e9`, `tensile_90C_r1e9`, `tensile_160C_r1e9`, `tensile_130C_r1e9` | crystal (no 500 K melt): 15/15 holds stable, 25–160 °C | — | crystal, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c`, `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_130C`, `tensile_130C_r1e9`, `tensile_140C`, `tensile_150C`, `tensile_160C`, `tensile_160C_r1e9`, `tensile_25C`, `tensile_25C_r1e9`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_75C`, `tensile_85C`, `tensile_90C`, `tensile_90C_r1e9` |
| `pe_cg_amorph_n40_c240_s1` | CG | PE | bulk | 40 × C240 | 3,200 beads | done | finished: prep, extend, cool, sweep, `diffuse_25C` (interrupted, 92.5%), `diffuse_160C` (interrupted, 85.2%), `diffuse_90C` (interrupted, 58.7%), `diffuse_130C`, `tensile_160C_r1e9`, `tensile_90C_r1e9`, `tensile_25C_r1e9`, `tensile_130C_r1e9`, `tensile_25C`, `tensile_160C`, `tensile_90C`, `tensile_130C` | D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | `cavitation_compare`, `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C`, extend, sweep, `tensile_130C`, `tensile_130C_r1e9`, `tensile_160C`, `tensile_160C_r1e9`, `tensile_25C`, `tensile_25C_r1e9`, `tensile_90C`, `tensile_90C_r1e9` |
| `pe_cg_amorph_n40_c1500_s1` | CG | PE | bulk | 40 × C1500 | 20,000 beads | done | finished: prep, extend, cool, sweep | D47 n/a (long CG chain); ACF 0.68 at 250.0 ns, MSD/⟨R<sub>g</sub>²⟩ 0.12; 500.0 ns at 500 K; no C<sub>n</sub> drift: accepted | 7.43 vs 6.7 (outside band, info); no drift (Δ +0.21 ± 0.30) | extend, sweep |
| `pe_cg_amorph_n320_c240_s1_rep222` | CG | PE | bulk (derived) | 320 × C240 | 25,600 beads | done | finished: extend (stopped after D47 PASS) | D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | extend |
| `pe_cg_amorph_n640_c240_s1_rep441` | CG | PE | bulk (derived) | 640 × C240 | 51,200 beads | done | finished: extend | D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | extend |
| `pe_cg_pore500k_w10nm_n40_c240_s1` | CG | PE | pore (wide, 10 nm) | 40 × C240 | 3,200 beads | done | finished: `pore_relax` | from `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | no |
| `pe_cg_pore_w5nm_n40_c240_s1` | CG | PE | pore (narrow, 5 nm) | 40 × C240 | 3,200 beads | done | finished: pore | from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | pore |
| `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` | CG | PE | pore (wide, 10 nm) | 320 × C240 | 25,600 beads | done | finished: `pore_relax` | from `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_hole_r2nm_160C_n320_c240_s1_rep222` | CG | PE | hole (R 2 nm, 160 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free` |
| `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 130 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free`, `hole_scaf_rel0` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free`, `hole_scaf_rel0` |
| `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 160 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free_gap5nm`, `hole_free`, `hole_scaf_rel0` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free`, `hole_scaf_rel0` |
| `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 25 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_ramp_rel130_failed_20261102` (failed, 0.0%), `hole_ramp_held_failed_20261102` (failed, 0.0%), `hole_free_failed_20261102` (failed, 0.0%), `hole_free`, `hole_ramp_rel130_d4`, `hole_ramp_rel130_col`, `hole_ramp_rel130`, `hole_ramp_held` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free`, `hole_ramp_held`, `hole_ramp_rel130`, `hole_ramp_rel130_col`, `hole_ramp_rel130_d4` |
| `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 90 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_free` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free` |
| `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222` | CG | PE | hole (R 4 nm, 160 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free_gap5nm`, `hole_free` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free` |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | CG | PE | pore (narrow, 5 nm) | 320 × C240 | 25,600 beads | done | finished: pore | from `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | pore |
| `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` | CG | PE | pore (wide, 12 nm) | 640 × C240 | 51,200 beads | done | finished: `pore_relax` | from `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_110C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_120C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_130C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_140C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_150C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_160C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_25C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_55C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_75C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_film_90C_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | not started | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_hole_r2nm_160C_n640_c240_s1_rep441` | CG | PE | hole (R 2 nm, 160 °C) | 640 × C240 | 51,200 beads | done | finished: `hole_free` | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_hole_r3nm_160C_n640_c240_s1_rep441` | CG | PE | hole (R 3 nm, 160 °C) | 640 × C240 | 51,200 beads | done | finished: `hole_free_gap5nm` (cancelled/killed?, 18.5%), `hole_free` | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | `hole_free` |
| `pe_cg_hole_r3nm_25C_n640_c240_s1_rep441` | CG | PE | hole (R 3 nm, 25 °C) | 640 × C240 | 51,200 beads | done | finished: `hole_free` | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_hole_r4nm_160C_n640_c240_s1_rep441` | CG | PE | hole (R 4 nm, 160 °C) | 640 × C240 | 51,200 beads | `hole_free` | cancelled/killed?, 77.2% | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_hole_r5nm_160C_n640_c240_s1_rep441` | CG | PE | hole (R 5 nm, 160 °C) | 640 × C240 | 51,200 beads | done | finished: `hole_free_gap5nm` (cancelled/killed?, 18.3%), `hole_free` | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | `hole_free` |
| `pe_cg_hole_r5nm_25C_n640_c240_s1_rep441` | CG | PE | hole (R 5 nm, 25 °C) | 640 × C240 | 51,200 beads | done | finished: `hole_free` | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_hole_r6nm_160C_n640_c240_s1_rep441` | CG | PE | hole (R 6 nm, 160 °C) | 640 × C240 | 51,200 beads | done | finished: `hole_free_gap5nm` (cancelled/killed?, 18.4%), `hole_free` | from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | `hole_free` |
| `pe_cg_pore_w5nm_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | done | finished: pore, `pore_55C`, `pore_120C`, `pore_75C`, `pore_150C`, `pore_110C`, `pore_140C` | from `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | pore |
| `pe_ua_crystal_7x10x40_s1` | UA | PE | crystal | 140 × C80 | 11,200 | done | finished: crystal, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c`, `tensile_25C_r1e9`, `tensile_90C_r1e9`, `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9` | crystal (no 500 K melt): 15/15 holds stable, 25–160 °C | — | crystal, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c`, `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_130C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_90C_r1e9` |
| `pe_ua_amorph_n40_c240_s1` | UA | PE | bulk | 40 × C240 | 9,600 | done | finished: prep, extend (stopped after D47 PASS), cool, sweep | D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | extend, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, sweep |
| `pe_ua_pore500k_w10nm_n40_c240_s1` | UA | PE | pore (wide, 10 nm) | 40 × C240 | 9,600 | done | finished: `pore_relax` | from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | no |
| `pe_ua_pore_w5nm_n40_c240_s1` | UA | PE | pore (narrow, 5 nm) | 40 × C240 | 9,600 | done | finished: pore | from `pe_ua_pore500k_w10nm_n40_c240_s1` ← `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | pore |
| `pe_aa_crystal_5x7x12_s1` | AA | PE | bulk | — × C— | — | prep | not started (crystal done) | — | — | no |
| `pe_aa_amorph_n40_c240_s1_from_ua` | AA | PE | bulk (derived) | 40 × C240 | 28,880 | done | finished: prep, `sweep_crashed_20261102` (cancelled/killed?, 0.1%), sweep | from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | sweep |
| `ipp_ua_amorph_n40_c240_s1` | UA | iPP | bulk | 40 × C240 | 12,760 | done | finished: prep (cancelled/killed?, 60.8%), extend (stopped after D47 PASS), cool, sweep | D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | extend, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, sweep |
| `ipp_ua_pore500k_w10nm_n40_c240_s1` | UA | iPP | pore (wide, 10 nm) | 40 × C240 | 12,760 | done | finished: `pore_relax` | from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | no |
| `ipp_ua_pore_w5nm_n40_c240_s1` | UA | iPP | pore (narrow, 5 nm) | 40 × C240 | 12,760 | done | finished: pore | from `ipp_ua_pore500k_w10nm_n40_c240_s1` ← `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | pore |
| `ipp_aa_amorph_n40_c240_s1_from_ua` | AA | iPP | bulk (derived) | 40 × C240 | 28,880 | done | finished: prep, `sweep_failed_20261102` (failed, 0.0%), sweep | from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | sweep |

**Abbreviations:**

- **Res**: resolution: CG = coarse-grained (SDK/SPICA, 3 carbons per bead), UA = united-atom (TraPPE-UA, CH<sub>x</sub> groups as one site), AA = all-atom (OPLS, explicit hydrogens)
- **PE / iPP**: polyethylene / isotactic polypropylene
- **Chains × length**: number of chains × backbone carbons per chain (C240 = 240 carbons)
- **Sites**: interaction sites in the box: atoms (AA), united atoms (UA) or beads (CG)
- **System id**: `<polymer>_<res>_<kind>_n<chains>_c<carbons>_s<seed>`; amorph = bulk amorphous box; `pore500k_w10nm` = wide 10 nm pore made at 500 K; `pore_w5nm` = 5 nm dry slit pore; `hole_r3nm_160C` = film with a 3 nm-radius cylindrical hole at 160 °C; rep222 / rep441 = box replicated 2×2×2 / 4×4×1; `from_ua` = AA box converted from the relaxed UA box
- **prep / extend / cool / sweep**: build and 500 K hold / longer 500 K hold (D47) / step-cool to 25 °C / 25–160 °C heating sweep with holds
- **D37, D47, …**: decision numbers in docs/decisions.md (the rule each check follows)
- **D47 PASS**: 500 K melt accepted as equilibrated: end-to-end ACF < 1/e and chain COM MSD ≥ 2⟨R<sub>g</sub>²⟩
- **ACF**: autocorrelation function (here of the chain end-to-end vector)
- **COM MSD / ⟨R<sub>g</sub>²⟩**: chain centre-of-mass mean-squared displacement over the mean squared radius of gyration (≥ 2: chains have moved about their own size)
- **C<sub>n</sub> plateau (D37)**: characteristic ratio of long sub-chains vs the PE melt value 6.7 ± 10%; informational (D47 decides acceptance)
- **Δ**: change between the first and second half of the hold (drift test)

## Physical validity by system

Can each property be compared with experiment for this system? Rules: `scripts/validity.py` (single source of truth; base table = the property guide's comparability table, refined by each system's own checks; the comparison data and general caveats per property are in that table). Our numbers next to experiment, with sources: [`docs/experiment_comparison.md`](../docs/experiment_comparison.md). Figure: [validity overview](validity_overview.png).

Legend: **comp** = comparable to experiment (with the stated data and caveats); **trend** = trends only (T, PE vs iPP, resolution, box size); **corr** = needs a correction first (VDOS quantum C<sub>p</sub>; time mapping for CG/UA dynamics); **no** = not meaningful for this model; **todo** = not yet computed; **n/a** = does not apply; **!** = flagged: the system's 500 K equilibration is not accepted (or has no verdict yet).

| System | ρ(T) | α<sub>V</sub> | κ<sub>T</sub> | C<sub>p</sub> | R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K | R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T | P2, segment MSD | D<sub>COM</sub>, viscosity | γ, dγ/dT | film structure | tensile E/ν/yield | hole closure | puncture `F/d_break` | cavitation `σ_cav` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `pe_cg_crystal_7x10x27_s1` | comp | trend | n/a | no | n/a | n/a | n/a | n/a | n/a | n/a | trend | n/a | n/a | n/a |
| `pe_cg_amorph_n40_c240_s1` | comp | comp | comp | no | comp | trend | corr | corr | n/a | n/a | trend | n/a | n/a | trend |
| `pe_cg_amorph_n40_c1500_s1` | comp | comp | comp | no | trend | trend | corr | todo | n/a | n/a | todo | n/a | n/a | todo |
| `pe_cg_amorph_n320_c240_s1_rep222` | todo | todo | todo | no | comp | todo | todo | todo | n/a | n/a | todo | n/a | n/a | todo |
| `pe_cg_amorph_n640_c240_s1_rep441` | todo | todo | todo | no | comp | todo | todo | todo | n/a | n/a | todo | n/a | n/a | todo |
| `pe_cg_pore500k_w10nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_pore_w5nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | trend | corr | n/a | comp | trend | n/a | todo | todo | n/a |
| `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_hole_r2nm_160C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | trend | corr | n/a | comp | trend | n/a | todo | todo | n/a |
| `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_110C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_120C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_130C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_140C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_150C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_160C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_25C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_55C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_75C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_film_90C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_hole_r2nm_160C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r3nm_160C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r3nm_25C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r4nm_160C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_cg_hole_r5nm_160C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r5nm_25C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_hole_r6nm_160C_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend | todo | n/a |
| `pe_cg_pore_w5nm_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | trend | corr | n/a | comp | trend | n/a | todo | todo | n/a |
| `pe_ua_crystal_7x10x40_s1` | comp | trend | n/a | no | n/a | n/a | n/a | n/a | n/a | n/a | trend | n/a | n/a | n/a |
| `pe_ua_amorph_n40_c240_s1` | comp | comp | comp | no | comp | trend | corr | todo | n/a | n/a | todo | n/a | n/a | todo |
| `pe_ua_pore500k_w10nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `pe_ua_pore_w5nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | trend | corr | n/a | comp | trend | n/a | todo | todo | n/a |
| `pe_aa_crystal_5x7x12_s1` | todo | todo | todo | todo | todo | todo | todo | todo | n/a | n/a | todo | n/a | n/a | todo |
| `pe_aa_amorph_n40_c240_s1_from_ua` | comp | comp | comp | corr | trend | trend | comp | todo | n/a | n/a | todo | n/a | n/a | todo |
| `ipp_ua_amorph_n40_c240_s1` | comp | comp | comp | no | comp | trend | corr | todo | n/a | n/a | todo | n/a | n/a | todo |
| `ipp_ua_pore500k_w10nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo | todo | n/a |
| `ipp_ua_pore_w5nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | trend | corr | n/a | comp | trend | n/a | todo | todo | n/a |
| `ipp_aa_amorph_n40_c240_s1_from_ua` | comp | comp | comp | corr | trend | trend | comp | todo | n/a | n/a | todo | n/a | n/a | todo |

**Abbreviations:**

- **ρ(T)**: mass density vs temperature (g/cm³)
- **α<sub>V</sub>**: volumetric thermal expansion coefficient, (1/V) dV/dT (10⁻⁴ K⁻¹)
- **κ<sub>T</sub>**: isothermal compressibility, from volume fluctuations (GPa⁻¹)
- **C<sub>p</sub>**: isobaric specific heat capacity, dH/dT (J g⁻¹ K⁻¹)
- **R<sub>g</sub>**: radius of gyration of a chain
- **R<sub>ee</sub>**: chain end-to-end distance
- **C<sub>n</sub>**: characteristic ratio ⟨R<sub>ee</sub>²⟩ / (n l²), chain stiffness (n bonds of length l)
- **500 K**: the equilibrated melt hold (prep/extend) before cooling
- **sweep T**: the 25–160 °C heating-sweep holds
- **P2**: bond orientation autocorrelation (second Legendre polynomial), local segment reorientation
- **MSD**: mean-squared displacement
- **segment MSD**: MSD of backbone sites (segmental mobility)
- **D<sub>COM</sub>**: chain centre-of-mass self-diffusion coefficient
- **γ**: surface tension of the free film surface (mN/m), from the pressure anisotropy
- **dγ/dT**: temperature slope of γ (mN m⁻¹ K⁻¹)
- **film structure**: pore film density profile ρ(z), thickness, gap width, interfacial width
- **E**: Young's (tensile) modulus
- **ν**: Poisson ratio
- **yield**: peak / flow stress of the tensile curve
- **hole closure**: closure time and speed of a cylindrical hole through the film (D52)
- **puncture `F/d_break`**: peak indenter force and break-through depth of a film puncture test (D57)
- **cavitation `σ_cav`**: peak hydrostatic tension before voids open, triaxial tension (D58)
- **VDOS**: vibrational density of states (quantum correction for C<sub>p</sub>)
- **CG / UA / AA**: coarse-grained (SDK/SPICA) / united-atom (TraPPE-UA) / all-atom (OPLS)

<details><summary>Reasons per system</summary>

- `pe_cg_crystal_7x10x27_s1`
  - α<sub>V</sub>: **trend**: no in-repo reference for the thermal expansion of crystalline PE: model value of a perfect periodic crystal (anisotropic: `α_a`, `α_b`, `α_c`), T and resolution trends only; α<sub>V</sub> 5.5–6.8 ×10⁻⁴ K⁻¹ over the crystal analyses' T windows (25–160, 35–65, 75–110, 120–150 °C)
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA
  - tensile E/ν/yield: **trend**: perfect periodic single crystal pulled transverse to the chains (D59: x, y only) at MD rates: E is the interchain transverse modulus and the peak the ideal transverse strength of a defect-free crystal; not comparable to separator data (semicrystalline, defects, ~10⁹× slower tests): T and rate trends only
  - **comparable**: ρ(T) (25 °C hold ρ 0.927 g/cm³ = 0.930 × the cell; 0.927 → 0.853 g/cm³ over 25–160 °C; no principled correction for the offset (model property))
- `pe_cg_amorph_n40_c240_s1`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.18–0.60 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 9.11 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - D<sub>COM</sub>, viscosity: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; diffusive and COM MSD ≥ 2⟨R<sub>g</sub>²⟩ at 130, 160 °C; the Rouse viscosity is a lower bound if the chains are entangled; vs experiment: CG PE dynamics ≈ 4× too fast (`docs/experiment_comparison.md`)
  - tensile E/ν/yield: **trend**: not comparable to separator data (their stiffness/yield come from crystallinity; MD rates ~10⁹× faster): amorphous response, T and rate trends; vs experiment: amorphous: compare with G<sub>e</sub> ≈ 2.6 MPa (E ≈ 8 MPa), not separator GPa moduli (`docs/experiment_comparison.md`)
  - cavitation `σ_cav`: **trend**: melt under fast affine triaxial tension (MD rates, small box): not the cavitation of a stretched semicrystalline separator; T and rate trends
  - **comparable**: ρ(T) (vs experiment: CG PE ≈ 2% low (C1500 1–2%) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 21 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows; vs experiment: CG PE ≈ 5% low (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (vs experiment: CG PE 50–60% too compressible (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 9.11 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_amorph_n40_c1500_s1`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K: **trend**: D47 not reached (C1500: end-to-end ACF 0.68, COM MSD/⟨R<sub>g</sub>²⟩ 0.12 at 250 ns): accepted on the C<sub>n</sub> no-drift rule only, so the whole-chain size is not equilibrated; C<sub>n</sub> 7.43 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.00–0.01 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 7.43 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.01, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
  - **comparable**: ρ(T) (vs experiment: CG PE ≈ 2% low (C1500 1–2%) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 27 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows; vs experiment: CG PE ≈ 5% low (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (vs experiment: CG PE 50–60% too compressible (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_amorph_n320_c240_s1_rep222`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - not yet computed: ρ(T) (then comparable), α<sub>V</sub> (then comparable), κ<sub>T</sub> (then comparable), R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then comparable), P2, segment MSD (then needs correction): no sweep run yet
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): no sweep run yet; needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
  - **comparable**: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 9.18 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_amorph_n640_c240_s1_rep441`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - not yet computed: ρ(T) (then comparable), α<sub>V</sub> (then comparable), κ<sub>T</sub> (then comparable), R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then comparable), P2, segment MSD (then needs correction): no sweep run yet
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): no sweep run yet; needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
  - **comparable**: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 8.93 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_pore500k_w10nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_pore_w5nm_n40_c240_s1`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.20–0.84 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 9.11 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - film structure: **trend**: no direct experiment: mechanism and within-simulation comparisons
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
  - **comparable**: γ, dγ/dT (finite size (D50) vs `pe_cg_pore_w5nm_n320_c240_s1_rep222`: Δγ up to +1.2 mN/m (3.0 combined SEM, at 130 °C); vs experiment: CG PE γ within 1–3% at 25–160 °C; dγ/dT ≈ 20% shallower (`docs/experiment_comparison.md`))
- `pe_cg_pore500k_w10nm_n320_c240_s1_rep222`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r2nm_160C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_pore_w5nm_n320_c240_s1_rep222`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.21–0.65 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 9.18 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - film structure: **trend**: no direct experiment: mechanism and within-simulation comparisons
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
  - **comparable**: γ, dγ/dT (finite size (D50) vs `pe_cg_pore_w5nm_n40_c240_s1`: Δγ up to -1.2 mN/m (3.0 combined SEM, at 130 °C); vs experiment: CG PE γ within 1–3% at 25–160 °C; dγ/dT ≈ 20% shallower (`docs/experiment_comparison.md`))
- `pe_cg_pore500k_w12nm_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_110C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_120C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_130C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_140C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_150C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_160C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_25C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_55C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_75C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_film_90C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r2nm_160C_n640_c240_s1_rep441`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r3nm_160C_n640_c240_s1_rep441`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r3nm_25C_n640_c240_s1_rep441`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r4nm_160C_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): hole runs `hole_free` cancelled/killed? 77%, `hole_free_gap5nm` cancelled/killed? 9%
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r5nm_160C_n640_c240_s1_rep441`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r5nm_25C_n640_c240_s1_rep441`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_hole_r6nm_160C_n640_c240_s1_rep441`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_cg_pore_w5nm_n640_c240_s1_rep441`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.07–0.24 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 8.93 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - film structure: **trend**: no direct experiment: mechanism and within-simulation comparisons
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
  - **comparable**: γ, dγ/dT (vs experiment: CG PE γ within 1–3% at 25–160 °C; dγ/dT ≈ 20% shallower (`docs/experiment_comparison.md`))
- `pe_ua_crystal_7x10x40_s1`
  - α<sub>V</sub>: **trend**: no in-repo reference for the thermal expansion of crystalline PE: model value of a perfect periodic crystal (anisotropic: `α_a`, `α_b`, `α_c`), T and resolution trends only; α<sub>V</sub> 2.8–3.5 ×10⁻⁴ K⁻¹ over the crystal analyses' T windows (25–160, 35–65, 75–110, 120–150 °C)
  - C<sub>p</sub>: **not meaningful**: UA removes the H atoms (their degrees of freedom), so classical C<sub>p</sub> is not the real one (close to experiment only by accident). No principled correction (a hybrid vibrational add-on is only approximate): use AA
  - tensile E/ν/yield: **trend**: perfect periodic single crystal pulled transverse to the chains (D59: x, y only) at MD rates: E is the interchain transverse modulus and the peak the ideal transverse strength of a defect-free crystal; not comparable to separator data (semicrystalline, defects, ~10⁹× slower tests): T and rate trends only
  - **comparable**: ρ(T) (25 °C hold ρ 1.014 g/cm³ = 1.018 × the cell; 1.014 → 0.976 g/cm³ over 25–160 °C; no principled correction for the offset (model property))
- `pe_ua_amorph_n40_c240_s1`
  - C<sub>p</sub>: **not meaningful**: UA removes the H atoms (their degrees of freedom), so classical C<sub>p</sub> is not the real one (close to experiment only by accident). No principled correction (a hybrid vibrational add-on is only approximate): use AA
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.01–0.14 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA force field, not of the equilibration; no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: UA dynamics are faster than real PE (no hydrogen friction). Correction: a UA→AA time-mapping factor per T from our own AA at the same T (none published for this force field here); T trends as is
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.14, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
  - **comparable**: ρ(T) (vs experiment: TraPPE-UA PE ≈ 1.5–2% high (literature, 448 K) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (no principled correction for the offset (model property): compare our UA/AA values); R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA force field, not of the equilibration; no principled correction for the offset (model property): compare our UA/AA values)
- `pe_ua_pore500k_w10nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `pe_ua_pore_w5nm_n40_c240_s1`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.02–0.21 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA force field, not of the equilibration; no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: UA dynamics are faster than real PE (no hydrogen friction). Correction: a UA→AA time-mapping factor per T from our own AA at the same T (none published for this force field here); T trends as is
  - film structure: **trend**: no direct experiment: mechanism and within-simulation comparisons
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
  - **comparable**: γ, dγ/dT
- `pe_aa_crystal_5x7x12_s1`
  - not yet computed: ρ(T) (then comparable), α<sub>V</sub> (then comparable), κ<sub>T</sub> (then comparable), C<sub>p</sub> (then needs correction), R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then comparable), P2, segment MSD (then comparable): no sweep run yet
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (then comparable): no 500 K hold checks yet
  - not yet computed: D<sub>COM</sub>, viscosity (then comparable): no sweep run yet; needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
- `pe_aa_amorph_n40_c240_s1_from_ua`
  - C<sub>p</sub>: **needs correction**: classical C<sub>p</sub> gives every vibration k<sub>B</sub> T (fully flexible AA ≈ 2.4× experiment). Correction: the VDOS quantum correction (D12c), then compare with ATHAS melt C<sub>p</sub>
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K: **trend**: ua2aa box: the chain conformations were equilibrated with the UA force field (D32/D47) and only relaxed locally in AA; compare the UA row; C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA (source box) force field, not of the equilibration
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.00–0.05 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA (source box) force field, not of the equilibration
  - not yet computed: D<sub>COM</sub>, viscosity (then comparable): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.05, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
  - **comparable**: ρ(T); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 16 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows); κ<sub>T</sub>; P2, segment MSD
- `ipp_ua_amorph_n40_c240_s1`
  - C<sub>p</sub>: **not meaningful**: UA removes the H atoms (their degrees of freedom), so classical C<sub>p</sub> is not the real one (close to experiment only by accident). No principled correction (a hybrid vibrational add-on is only approximate): use AA
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.00–0.10 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: UA dynamics are faster than real PE (no hydrogen friction). Correction: a UA→AA time-mapping factor per T from our own AA at the same T (none published for this force field here); T trends as is; P2 1/e not reached at 25 °C
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.10, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
  - **comparable**: ρ(T) (no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 106 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows; no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (no principled correction for the offset (model property): compare our UA/AA values); R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (no principled correction for the offset (model property): compare our UA/AA values)
- `ipp_ua_pore500k_w10nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
- `ipp_ua_pore_w5nm_n40_c240_s1`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.00–0.41 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: UA dynamics are faster than real PE (no hydrogen friction). Correction: a UA→AA time-mapping factor per T from our own AA at the same T (none published for this force field here); T trends as is
  - film structure: **trend**: no direct experiment: mechanism and within-simulation comparisons
  - not yet computed: hole closure (then trend): no hole run (D52)
  - not yet computed: puncture `F/d_break` (then trend): no puncture run (D57)
  - **comparable**: γ, dγ/dT
- `ipp_aa_amorph_n40_c240_s1_from_ua`
  - C<sub>p</sub>: **needs correction**: classical C<sub>p</sub> gives every vibration k<sub>B</sub> T (fully flexible AA ≈ 2.4× experiment). Correction: the VDOS quantum correction (D12c), then compare with ATHAS melt C<sub>p</sub>
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K: **trend**: ua2aa box: the chain conformations were equilibrated with the UA force field (D32/D47) and only relaxed locally in AA; compare the UA row
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.00–0.11 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved)
  - not yet computed: D<sub>COM</sub>, viscosity (then comparable): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.11, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - not yet computed: cavitation `σ_cav` (then trend): no cavitation run (D58)
  - **comparable**: ρ(T); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 17 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows); κ<sub>T</sub>; P2, segment MSD (P2 1/e not reached at 25 °C)

</details>

## Pending and known items

- `pe_cg_film_110C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_120C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_130C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_140C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_150C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_160C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_25C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_55C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_75C_n640_c240_s1_rep441`: pore not started
- `pe_cg_film_90C_n640_c240_s1_rep441`: pore not started
- `pe_cg_hole_r4nm_160C_n640_c240_s1_rep441`: `hole_free`: cancelled/killed?, 77.2%
- `pe_aa_crystal_5x7x12_s1`: prep not started; sweep not started; crystal analysis not run; no equilibration verdict yet

## Superseded (kept, not used)

- System `pe_cg_pore_w10nm_n40_c240_s1`: built from an earlier `pe_cg_pore500k_w10nm_n40_c240_s1` (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)
- System `pe_cg_pore_w3nm_n40_c240_s1`: built from an earlier `pe_cg_pore500k_w10nm_n40_c240_s1` (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)
- System `pe_aa_amorph_n40_c240_s1`: superseded by `pe_aa_amorph_n40_c240_s1_from_ua` (D47: AA is built from the relaxed UA box)
- Runs of `pe_cg_amorph_n40_c240_s1`: `prep_server_cancelled` (cancelled/killed?), `prep_timeout12h` (cancelled/killed?), `sweep_old_20ns_box` (finished)
- Runs of `pe_cg_amorph_n40_c1500_s1`: `sweep_cancelled_unrelaxed` (cancelled/killed?)
- Runs of `pe_cg_amorph_n320_c240_s1_rep222`: `extend_cpu_job92_cancelled_48ns` (cancelled/killed?)
- Runs of `pe_cg_pore500k_w10nm_n40_c240_s1`: `pore_relax_old_20ns_box` (finished)
- Runs of `pe_cg_pore_w5nm_n40_c240_s1`: `pore_old_20ns_box_cancelled` (cancelled/killed?)
- Runs of `pe_ua_amorph_n40_c240_s1`: `sweep_old_unrelaxed_cancelled` (cancelled/killed?)
- Runs of `ipp_ua_amorph_n40_c240_s1`: `prep_server_cancelled` (cancelled/killed?)
- Runs of `ipp_aa_amorph_n40_c240_s1_from_ua`: `sweep_cancelled_pe_first` (cancelled/killed?)

## Systems

One subsection per system, in the overview order (superseded systems last). Each has a one-line description, a table of every property obtained from the system (all of its analyses: sweep, 500 K extension, long diffuse holds, tensile runs, pore) and, collapsed, the full analysis tables and checks.

**Abbreviations (all property tables below):**

- Table
  - **25 / 90 / 130 / 160 °C**: hold temperature (heating sweep, pore holds, long holds, tensile)
  - **Other (500 K, fits)**: values not tied to those temperatures: the 500 K melt, fit windows (°C), rates
  - **Validity**: this system's verdict for the property in the validity table above (codes below)
  - **Source**: the analysis (`results/analysis/<system>/<stage>/results.json`) or run monitor the value comes from
  - **mean ± SEM**: mean and standard error of the mean (block averages / statistical inefficiency), unless marked SD
  - **SD**: standard deviation (tensile: over the x, y and z pulls of one run)
  - **χ²<sub>red</sub>**: reduced χ² of the SEM-weighted linear fit (> 1: curvature or SEMs too small; errors scaled by √χ²<sub>red</sub>)
  - **progress**: the run monitor (`sepsim progress`, progress.json) rather than an analysis
  - **long hold (D53)**: dedicated long NPT hold at one sweep temperature (`diffuse` run)
  - **not reached / extrap.**: the ACF stays above 1/e within the lags; extrap. = exponential fit of the early decay (order of magnitude only)
  - **not diffusive (slope s)**: chain COM MSD log-slope below 0.9 at the longest lag, so no D<sub>COM</sub>; s = that slope
- Equilibration and thermodynamics
  - **D47**: 500 K chain-mixing criterion: end-to-end ACF < 1/e and chain COM MSD ≥ 2⟨R<sub>g</sub>²⟩ at half the hold
  - **ACF**: autocorrelation function (here of the chain end-to-end vector)
  - **500 K**: the equilibrated melt hold (prep/extend) before cooling
  - **ρ**: mass density (g/cm³)
  - **κ<sub>T</sub>**: isothermal compressibility from the volume fluctuations (GPa⁻¹)
  - **α<sub>V</sub>**: volumetric thermal expansion coefficient (1/V) dV/dT (10⁻⁴ K⁻¹)
  - **α<sub>z</sub>**: linear expansion coefficient of the film thickness (10⁻⁴ K⁻¹)
  - **C<sub>p</sub>**: isobaric specific heat dH/dT, classical (J g⁻¹ K⁻¹)
  - **C<sub>v</sub>**: specific heat at constant volume dE/dT, classical (J g⁻¹ K⁻¹)
- Chain size and dynamics
  - **R<sub>g</sub>**: radius of gyration of a chain (Å)
  - **R<sub>ee</sub>**: chain end-to-end distance (Å)
  - **C<sub>n</sub>**: characteristic ratio ⟨R<sub>n</sub>²⟩/(n l²) for n ≥ 100 backbone carbons (D37); melt C∞ ≈ 6.7 (PE), 6.15 (iPP)
  - **P2**: backbone bond orientation autocorrelation (second Legendre polynomial); 1/e time = local reorientation time
  - **MSD**: mean-squared displacement (Å²)
  - **COM**: chain centre of mass
  - **segment MSD**: MSD of the backbone sites (segmental mobility)
  - **D<sub>COM</sub>**: chain centre-of-mass self-diffusion coefficient (cm²/s), only when the MSD is diffusive
  - **η<sub>Rouse</sub>**: Rouse melt viscosity ρ<sub>N</sub> k<sub>B</sub> T ⟨R<sub>ee</sub>²⟩/(36 D<sub>COM</sub>) (Pa·s); a lower bound for entangled chains
  - **τ<sub>ee</sub>**: 1/e time of the end-to-end vector ACF: the longest single-chain relaxation time (ns)
  - **τ<sub>1</sub>**: 1/e time of the slowest (p = 1) Rouse mode ACF (ns)
  - **ordered-site fraction**: D26 local-alignment order (p2 ≥ 0.4), uncalibrated melt baseline, not a crystallinity
- Surfaces and films (pores)
  - **γ**: surface tension per film surface (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2] (mN/m)
  - **dγ/dT**: temperature slope of γ from a linear fit (mN m⁻¹ K⁻¹)
  - **e<sub>s</sub>**: surface excess energy per unit area (mJ/m²), classical
  - **Gibbs surfaces**: dividing surfaces of the film density profile; thickness and gap are measured between them
  - **interfacial width, 10–90 %**: distance over which the density rises from 10% to 90% of the interior value
  - **surface / interior layer**: sites within 15 Å of a Gibbs surface / the rest of the film
- Mechanics (tensile)
  - **E<sub>app</sub>**: apparent (high-frequency, rate-dependent) tensile modulus up to strain 0.02 (MPa)
  - **ν**: Poisson ratio −d ln L<sub>lateral</sub> / d ln L<sub>axis</sub>
  - **σ<sub>peak</sub>, ε<sub>peak</sub>**: maximum of the smoothed true stress (MPa) and its strain
  - **flow σ**: mean true stress over strains 0.3–0.5 (MPa)
  - **s⁻¹**: engineering strain rate of the pull
- Analyses (Source)
  - **`sweep`**: 25–160 °C heating-sweep analysis (`sepsim analyze sweep`)
  - **`extend`**: 500 K extension hold (D47; analysis: `sepsim analyze hold`)
  - **`diffuse_<T>`**: long NPT hold at T (D53, `sepsim analyze hold`)
  - **`tensile_<T>[_r1e9]`**: tensile runs at T (D54, `sepsim analyze tensile`; `_r1e9` = 10⁹ s⁻¹)
  - **`pore`**: slit-pore analysis (D51, `sepsim analyze pore`)
  - **`prep`**: build and first 500 K hold
- Validity codes
  - **comp**: comparable to experiment (with the stated data and caveats)
  - **trend**: trends only (T, PE vs iPP, resolution, box size)
  - **corr**: needs a correction first (VDOS quantum C<sub>p</sub>; time mapping for CG/UA dynamics)
  - **no**: not meaningful for this model
  - **todo**: not yet computed
  - **n/a**: does not apply
  - **!**: flagged: the system's 500 K equilibration is not accepted

### `pe_cg_crystal_7x10x27_s1`

PE CG, periodic crystal of straight stems (7×10×27 cell repeats, D59), 140 chains × C81, 3,780 beads; provenance not recorded. Status: finished: crystal, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c`, `tensile_25C`, `tensile_90C`, `tensile_130C`, `tensile_160C`, `tensile_75C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_85C`, `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_140C`, `tensile_150C`, `tensile_25C_r1e9`, `tensile_90C_r1e9`, `tensile_160C_r1e9`, `tensile_130C_r1e9`.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| ρ (g/cm³) | 0.92695 ± 0.00003 | 0.89377 ± 0.00004 | 0.87145 ± 0.00004 | 0.85323 ± 0.00005 | 35 °C: 0.92208 ± 0.00003; 45 °C: 0.91713 ± 0.00003; 55 °C: 0.91211 ± 0.00003; 65 °C: 0.90702 ± 0.00004; 75 °C: 0.90179 ± 0.00003; 85 °C: 0.89654 ± 0.00004; 100 °C: 0.88838 ± 0.00004; 110 °C: 0.88290 ± 0.00004; 120 °C: 0.87719 ± 0.00004; 140 °C: 0.86552 ± 0.00005; 150 °C: 0.85944 ± 0.00005 | comp | `crystal`, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 6.106 ± 0.217; 35–65 °C: 5.482 ± 0.051; 75–110 °C: 6.064 ± 0.050; 120–150 °C: 6.810 ± 0.077 | trend | `crystal`, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c` |
| crystallinity (ordered-site fraction) | 1.000 | 0.999 | 0.996 | 0.987 | 35 °C: 1.000; 45 °C: 1.000; 55 °C: 1.000; 65 °C: 1.000; 75 °C: 1.000; 85 °C: 0.999; 100 °C: 0.999; 110 °C: 0.998; 120 °C: 0.997; 140 °C: 0.994; 150 °C: 0.991 | — | `crystal`, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c` |
| E<sub>app</sub> (MPa), 10⁸ s⁻¹, mean ± SD | 1.91e+03 ± 18.6 | 1.1e+03 ± 6.15 | 885 ± 115 | 773 ± 235 | 1.13e+03 ± 185; 993 ± 498; 1.03e+03 ± 122; 1.09e+03 ± 16.1; 941 ± 181; 1.55e+03 ± 426; 1.56e+03 ± 236; 1.58e+03 ± 266; 1.22e+03 ± 419; 1.43e+03 ± 41.6; 1.4e+03 ± 104 | trend | `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_130C`, `tensile_140C`, `tensile_150C`, `tensile_160C`, `tensile_25C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_75C`, `tensile_85C`, `tensile_90C` |
| E<sub>app</sub> (MPa), 10⁹ s⁻¹, mean ± SD | 2.05e+03 ± 302 | 1.48e+03 ± 243 | 1.06e+03 ± 368 | 1.01e+03 ± 0.0604 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| ν, fit up to the E<sub>app</sub> strain, 10⁸ s⁻¹, mean ± SD | 0.18 ± 0.03 | 0.23 ± 0.03 | 0.22 ± 0.07 | 0.21 ± 0.08 | 0.21 ± 0.04; 0.25 ± 0.07; 0.19 ± 0.00; 0.20 ± 0.00; 0.22 ± 0.01; 0.21 ± 0.05; 0.20 ± 0.05; 0.20 ± 0.04; 0.23 ± 0.06; 0.19 ± 0.02; 0.19 ± 0.00 | trend | `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_130C`, `tensile_140C`, `tensile_150C`, `tensile_160C`, `tensile_25C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_75C`, `tensile_85C`, `tensile_90C` |
| ν, fit up to the E<sub>app</sub> strain, 10⁹ s⁻¹, mean ± SD | 0.21 ± 0.08 | 0.18 ± 0.07 | 0.31 ± 0.10 | 0.20 ± 0.07 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| ν, whole run, 10⁸ s⁻¹, mean ± SD | 0.45 ± 0.00 | 0.44 ± 0.00 | 0.47 ± 0.01 | 0.44 ± 0.03 | 0.44 ± 0.00; 0.44 ± 0.00; 0.45 ± 0.00; 0.47 ± 0.02; 0.45 ± 0.03; 0.45 ± 0.00; 0.44 ± 0.00; 0.44 ± 0.00; 0.44 ± 0.00; 0.44 ± 0.00; 0.44 ± 0.00 | trend | `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_130C`, `tensile_140C`, `tensile_150C`, `tensile_160C`, `tensile_25C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_75C`, `tensile_85C`, `tensile_90C` |
| ν, whole run, 10⁹ s⁻¹, mean ± SD | 0.45 ± 0.00 | 0.44 ± 0.00 | 0.42 ± 0.01 | 0.42 ± 0.01 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| σ<sub>peak</sub> (MPa), 10⁸ s⁻¹, mean ± SD | 48 ± 1.6 | 40 ± 1.8 | 35 ± 1.4 | 30 ± 1.4 | 39 ± 1.7; 37 ± 1.5; 36 ± 1.6; 33 ± 2; 32 ± 1.6; 47 ± 2; 46 ± 1.7; 45 ± 1.7; 43 ± 1.8; 42 ± 1.8; 41 ± 2 | trend | `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_130C`, `tensile_140C`, `tensile_150C`, `tensile_160C`, `tensile_25C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_75C`, `tensile_85C`, `tensile_90C` |
| σ<sub>peak</sub> (MPa), 10⁹ s⁻¹, mean ± SD | 58 ± 1.2 | 43 ± 0.78 | 38 ± 1.3 | 34 ± 2.6 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| ε<sub>peak</sub>, 10⁸ s⁻¹, mean ± SD | 0.368 ± 0.053 | 0.328 ± 0.011 | 0.321 ± 0.004 | 0.246 ± 0.024 | 0.349 ± 0.027; 0.359 ± 0.002; 0.336 ± 0.050; 0.295 ± 0.058; 0.288 ± 0.031; 0.331 ± 0.012; 0.374 ± 0.013; 0.336 ± 0.010; 0.365 ± 0.032; 0.358 ± 0.010; 0.327 ± 0.012 | trend | `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_130C`, `tensile_140C`, `tensile_150C`, `tensile_160C`, `tensile_25C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_75C`, `tensile_85C`, `tensile_90C` |
| ε<sub>peak</sub>, 10⁹ s⁻¹, mean ± SD | 0.041 ± 0.003 | 0.205 ± 0.245 | 0.289 ± 0.019 | 0.256 ± 0.003 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| flow σ (MPa), 10⁸ s⁻¹, mean ± SD | 46 ± 2.1 | 38 ± 2.1 | 26 ± 0.35 | 10 ± 14 | 35 ± 1.9; 33 ± 0.51; 28 ± 0.84; 24 ± 2.3; 12 ± 6.4; 45 ± 2.1; 44 ± 1.9; 43 ± 1.9; 42 ± 1.9; 41 ± 2.1; 39 ± 1.9 | trend | `tensile_100C`, `tensile_110C`, `tensile_120C`, `tensile_130C`, `tensile_140C`, `tensile_150C`, `tensile_160C`, `tensile_25C`, `tensile_35C`, `tensile_45C`, `tensile_55C`, `tensile_65C`, `tensile_75C`, `tensile_85C`, `tensile_90C` |
| flow σ (MPa), 10⁹ s⁻¹, mean ± SD | 47 ± 1.7 | 39 ± 1.8 | 28 ± 1.4 | 15 ± 5.9 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 140 chains × C81 (C81H162), 3,780 atoms/beads, force field `sdk_cg`, box density 1.0493 g/cm³ (as built)

**Equilibration**

- Verdict: crystal (no 500 K melt): 15/15 holds stable, 25–160 °C
- C<sub>n</sub> plateau (D37): —

**Stages**

- **crystal** (rdyu-rog): finished; started 2026-11-16 19:55 UTC, ended 2026-11-17 02:17 UTC; reads `systems/pe_cg_crystal_7x10x27_s1/data.lmp`
- **`crystal_fine_a`** (rdyu-server): finished; started 2026-11-21 05:34 UTC, ended 2026-11-21 13:57 UTC; reads `systems/pe_cg_crystal_7x10x27_s1/data.lmp`
- **`crystal_fine_b`** (rdyu-server): finished; started 2026-11-21 05:36 UTC, ended 2026-11-21 13:43 UTC; reads `systems/pe_cg_crystal_7x10x27_s1/data.lmp`
- **`crystal_fine_c`** (rdyu-server): finished; started 2026-11-21 06:52 UTC, ended 2026-11-21 12:25 UTC; reads `systems/pe_cg_crystal_7x10x27_s1/data.lmp`
  - monitor flags: drift seg 2
- **`tensile_25C`** (rdyu-rog): finished; started 2026-11-17 02:17 UTC, ended 2026-11-17 04:59 UTC; reads `../crystal/hold_25C.data`
  - monitor flags: drift seg 1,2
- **`tensile_90C`** (rdyu-rog): finished; started 2026-11-17 04:59 UTC, ended 2026-11-17 07:37 UTC; reads `../crystal/hold_90C.data`
  - monitor flags: drift seg 1,2
- **`tensile_130C`** (rdyu-rog): finished; started 2026-11-17 07:37 UTC, ended 2026-11-17 10:09 UTC; reads `../crystal/hold_130C.data`
  - monitor flags: drift seg 1,2
- **`tensile_160C`** (rdyu-rog): finished; started 2026-11-17 10:09 UTC, ended 2026-11-17 12:39 UTC; reads `../crystal/hold_160C.data`
  - monitor flags: drift seg 2
- **`tensile_75C`** (rdyu-server): finished; started 2026-11-21 13:43 UTC, ended 2026-11-21 16:45 UTC; reads `../crystal_fine_b/hold_75C.data`
  - monitor flags: drift seg 1,2
- **`tensile_35C`** (rdyu-server): finished; started 2026-11-21 13:57 UTC, ended 2026-11-21 17:10 UTC; reads `../crystal_fine_a/hold_35C.data`
  - monitor flags: drift seg 1,2
- **`tensile_45C`** (rdyu-server): finished; started 2026-11-21 16:45 UTC, ended 2026-11-21 19:55 UTC; reads `../crystal_fine_a/hold_45C.data`
  - monitor flags: drift seg 1,2
- **`tensile_55C`** (rdyu-server): finished; started 2026-11-21 17:10 UTC, ended 2026-11-21 20:32 UTC; reads `../crystal_fine_a/hold_55C.data`
  - monitor flags: drift seg 1,2
- **`tensile_65C`** (rdyu-server): finished; started 2026-11-21 19:56 UTC, ended 2026-11-21 23:16 UTC; reads `../crystal_fine_a/hold_65C.data`
  - monitor flags: drift seg 1,2
- **`tensile_85C`** (rdyu-server): finished; started 2026-11-21 20:32 UTC, ended 2026-11-22 00:02 UTC; reads `../crystal_fine_b/hold_85C.data`
  - monitor flags: drift seg 1,2
- **`tensile_100C`** (rdyu-server): finished; started 2026-11-21 23:16 UTC, ended 2026-11-22 02:33 UTC; reads `../crystal_fine_b/hold_100C.data`
  - monitor flags: drift seg 1,2
- **`tensile_110C`** (rdyu-server): finished; started 2026-11-22 00:02 UTC, ended 2026-11-22 03:34 UTC; reads `../crystal_fine_b/hold_110C.data`
  - monitor flags: drift seg 2
- **`tensile_120C`** (rdyu-server): finished; started 2026-11-22 02:32 UTC, ended 2026-11-22 04:18 UTC; reads `../crystal_fine_c/hold_120C.data`
- **`tensile_140C`** (rdyu-server): finished; started 2026-11-22 02:32 UTC, ended 2026-11-22 05:20 UTC; reads `../crystal_fine_c/hold_140C.data`
  - monitor flags: drift seg 1,2
- **`tensile_150C`** (rdyu-server): finished; started 2026-11-22 02:33 UTC, ended 2026-11-22 05:43 UTC; reads `../crystal_fine_c/hold_150C.data`
  - monitor flags: drift seg 2
- **`tensile_25C_r1e9`** (rdyu-server): finished; started 2026-11-23 17:30 UTC, ended 2026-11-23 17:39 UTC; reads `../crystal/hold_25C.data`
  - monitor flags: drift seg 1,2
- **`tensile_90C_r1e9`** (rdyu-server): finished; started 2026-11-23 17:30 UTC, ended 2026-11-23 17:44 UTC; reads `../crystal/hold_90C.data`
  - monitor flags: drift seg 1,2
- **`tensile_160C_r1e9`** (rdyu-server): finished; started 2026-11-23 17:30 UTC, ended 2026-11-23 17:44 UTC; reads `../crystal/hold_160C.data`
  - monitor flags: drift seg 1
- **`tensile_130C_r1e9`** (rdyu-server): finished; started 2026-11-23 17:30 UTC, ended 2026-11-23 17:44 UTC; reads `../crystal/hold_130C.data`
  - monitor flags: drift seg 1,2

**`crystal` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:26 UTC on rdyu-server, run finished; crystallinity calibrated (`calibration_cg_pe.json`, 2026-11-17).

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 25 | yes | 1.000 | 0.92695 ± 0.00003 | 8.668 ± 0.0003 | 5.005 ± 0.0002 | 3.4756 ± 8e-05 | `a_A`, `a_over_b` |
| 90 | yes | 0.999 | 0.89377 ± 0.00004 | 8.876 ± 0.0007 | 5.123 ± 0.0004 | 3.4385 ± 0.0003 | — |
| 130 | yes | 0.996 | 0.87145 ± 0.00004 | 9.028 ± 0.0008 | 5.211 ± 0.0004 | 3.4087 ± 0.0003 | — |
| 160 | yes | 0.987 | 0.85323 ± 0.00005 | 9.160 ± 0.0007 | 5.286 ± 0.0005 | 3.3830 ± 0.0003 | `area_per_chain_A2` |

- α<sub>V</sub> 6.106 ± 0.217 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`crystal_fine_a` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:26 UTC on rdyu-server, run finished; crystallinity calibrated (`calibration_cg_pe.json`, 2026-11-17).

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 35 | yes | 1.000 | 0.92208 ± 0.00003 | 8.697 ± 0.0004 | 5.021 ± 0.0002 | 3.4709 ± 0.0001 | `a_A`, `a_over_b` |
| 45 | yes | 1.000 | 0.91713 ± 0.00003 | 8.728 ± 0.0003 | 5.038 ± 0.0002 | 3.4655 ± 0.0001 | — |
| 55 | yes | 1.000 | 0.91211 ± 0.00003 | 8.759 ± 0.0004 | 5.056 ± 0.0003 | 3.4601 ± 0.0002 | — |
| 65 | yes | 1.000 | 0.90702 ± 0.00004 | 8.791 ± 0.0005 | 5.074 ± 0.0003 | 3.4545 ± 0.0002 | — |

- α<sub>V</sub> 5.482 ± 0.051 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`crystal_fine_b` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:26 UTC on rdyu-server, run finished; crystallinity calibrated (`calibration_cg_pe.json`, 2026-11-17).

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 75 | yes | 1.000 | 0.90179 ± 0.00003 | 8.824 ± 0.0005 | 5.093 ± 0.0002 | 3.4484 ± 0.0001 | `a_A`, `a_over_b` |
| 85 | yes | 0.999 | 0.89654 ± 0.00004 | 8.858 ± 0.0004 | 5.113 ± 0.0003 | 3.4421 ± 0.0002 | — |
| 100 | yes | 0.999 | 0.88838 ± 0.00004 | 8.911 ± 0.0005 | 5.144 ± 0.0003 | 3.4322 ± 0.0002 | — |
| 110 | yes | 0.998 | 0.88290 ± 0.00004 | 8.947 ± 0.0006 | 5.166 ± 0.0004 | 3.4249 ± 0.0003 | — |

- α<sub>V</sub> 6.064 ± 0.050 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`crystal_fine_c` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:26 UTC on rdyu-server, run finished; crystallinity calibrated (`calibration_cg_pe.json`, 2026-11-17).

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 120 | yes | 0.997 | 0.87719 ± 0.00004 | 8.987 ± 0.0006 | 5.188 ± 0.0004 | 3.4171 ± 0.0003 | — |
| 140 | yes | 0.994 | 0.86552 ± 0.00005 | 9.069 ± 0.0006 | 5.235 ± 0.0005 | 3.4012 ± 0.0003 | `a_over_b` |
| 150 | yes | 0.991 | 0.85944 ± 0.00005 | 9.114 ± 0.0006 | 5.260 ± 0.0005 | 3.3921 ± 0.0003 | — |

- α<sub>V</sub> 6.810 ± 0.077 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`tensile_100C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

100 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1e+03 ± 68 | 0.24 | 0.44 | 40 | 0.330 | 37 | 373.2 |
| y | 0.500 | 1.26e+03 ± 58 | 0.18 | 0.44 | 38 | 0.368 | 34 | 373.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_110C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

110 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.35e+03 ± 50 | 0.20 | 0.45 | 39 | 0.357 | 33 | 383.2 |
| y | 0.500 | 640 ± 58 | 0.30 | 0.44 | 36 | 0.360 | 32 | 383.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_120C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

120 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.11e+03 ± 59 | 0.19 | 0.45 | 37 | 0.301 | 28 | 393.1 |
| y | 0.500 | 942 ± 68 | 0.20 | 0.45 | 35 | 0.371 | 29 | 393.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_130C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

130 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 804 ± 63 | 0.27 | 0.47 | 36 | 0.324 | 25 | 403.2 |
| y | 0.500 | 967 ± 66 | 0.17 | 0.46 | 34 | 0.318 | 26 | 403.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_130C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:45 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

130 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 804 ± 1.8e+02 | 0.38 | 0.42 | 39 | 0.276 | 29 | 403.1 |
| y | 0.500 | 1.32e+03 ± 1.7e+02 | 0.24 | 0.43 | 37 | 0.303 | 27 | 403.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_140C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

140 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.1e+03 ± 63 | 0.20 | 0.45 | 35 | 0.336 | 25 | 413.2 |
| y | 0.500 | 1.07e+03 ± 53 | 0.21 | 0.48 | 32 | 0.254 | 22 | 413.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_150C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

150 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 813 ± 62 | 0.23 | 0.43 | 33 | 0.310 | 7.2 | 423.2 |
| y | 0.500 | 1.07e+03 ± 56 | 0.22 | 0.47 | 31 | 0.266 | 16 | 423.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_160C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

160 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 939 ± 60 | 0.16 | 0.46 | 31 | 0.263 | 20 | 433.2 |
| y | 0.500 | 607 ± 62 | 0.27 | 0.42 | 29 | 0.229 | 0.83 | 433.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_160C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:45 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

160 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.01e+03 ± 2.1e+02 | 0.14 | 0.41 | 36 | 0.254 | 19 | 433.4 |
| y | 0.500 | 1.01e+03 ± 1.8e+02 | 0.25 | 0.42 | 32 | 0.258 | 11 | 432.8 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_25C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

25 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.92e+03 ± 52 | 0.16 | 0.44 | 49 | 0.330 | 48 | 298.2 |
| y | 0.500 | 1.89e+03 ± 52 | 0.20 | 0.45 | 47 | 0.406 | 45 | 298.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_25C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:45 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

25 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 2.26e+03 ± 1.8e+02 | 0.27 | 0.45 | 57 | 0.039 | 48 | 298.3 |
| y | 0.500 | 1.83e+03 ± 1.3e+02 | 0.15 | 0.45 | 58 | 0.043 | 45 | 298.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_35C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

35 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.25e+03 ± 65 | 0.25 | 0.44 | 48 | 0.340 | 47 | 308.1 |
| y | 0.500 | 1.85e+03 ± 50 | 0.17 | 0.45 | 45 | 0.323 | 44 | 308.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_45C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

45 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.39e+03 ± 58 | 0.24 | 0.44 | 47 | 0.383 | 45 | 318.1 |
| y | 0.500 | 1.73e+03 ± 53 | 0.17 | 0.45 | 44 | 0.365 | 43 | 318.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_55C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

55 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.77e+03 ± 53 | 0.17 | 0.44 | 46 | 0.343 | 44 | 328.2 |
| y | 0.500 | 1.4e+03 ± 56 | 0.23 | 0.44 | 43 | 0.329 | 42 | 328.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_65C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

65 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 928 ± 54 | 0.27 | 0.44 | 45 | 0.342 | 43 | 338.2 |
| y | 0.500 | 1.52e+03 ± 61 | 0.19 | 0.44 | 42 | 0.387 | 40 | 338.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_75C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

75 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.46e+03 ± 54 | 0.20 | 0.44 | 43 | 0.351 | 42 | 348.1 |
| y | 0.500 | 1.4e+03 ± 62 | 0.17 | 0.44 | 41 | 0.364 | 39 | 348.3 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_85C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

85 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.48e+03 ± 60 | 0.18 | 0.44 | 42 | 0.318 | 40 | 358.1 |
| y | 0.500 | 1.33e+03 ± 55 | 0.19 | 0.44 | 39 | 0.335 | 38 | 358.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_90C` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

90 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.1e+03 ± 62 | 0.21 | 0.43 | 42 | 0.335 | 40 | 363.2 |
| y | 0.500 | 1.09e+03 ± 69 | 0.26 | 0.44 | 39 | 0.320 | 37 | 363.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_90C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:45 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

90 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-server:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 1.65e+03 ± 1.5e+02 | 0.22 | 0.44 | 44 | 0.379 | 40 | 363.2 |
| y | 0.500 | 1.31e+03 ± 1.5e+02 | 0.13 | 0.44 | 43 | 0.032 | 37 | 363.0 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

</details>

### `pe_cg_amorph_n40_c240_s1`

PE CG, bulk amorphous box, 40 chains × C240, 3,200 beads; grown chains (seed 1). Status: finished: prep, extend, cool, sweep, `diffuse_25C` (interrupted, 92.5%), `diffuse_160C` (interrupted, 85.2%), `diffuse_90C` (interrupted, 58.7%), `diffuse_130C`, `tensile_160C_r1e9`, `tensile_90C_r1e9`, `tensile_25C_r1e9`, `tensile_130C_r1e9`, `tensile_25C`, `tensile_160C`, `tensile_90C`, `tensile_130C`.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | — | `extend` progress |
| ρ (g/cm³) | 0.83453 ± 0.00009 | 0.79783 ± 0.00007 | 0.77580 ± 0.00011 | 0.75938 ± 0.00009 | 500 K: 0.72370 ± 0.00007 | comp | `extend`, `sweep` |
| ρ (g/cm³), long hold (D53) | 0.83523 ± 0.00010 | 0.79797 ± 0.00009 | 0.77580 ± 0.00004 | 0.75957 ± 0.00005 | — | comp | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| κ<sub>T</sub> (GPa⁻¹) | 1.000 ± 0.015 | 1.292 ± 0.019 | 1.502 ± 0.027 | 1.662 ± 0.026 | 500 K: 2.146 ± 0.024 | comp | `extend`, `sweep` |
| κ<sub>T</sub> (GPa⁻¹), long hold (D53) | 1.011 ± 0.005 | 1.271 ± 0.007 | 1.482 ± 0.007 | 1.638 ± 0.008 | — | comp | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 6.966 ± 0.041 (χ²<sub>red</sub> 20.9); 25–90 °C: 6.925 ± 0.035 (χ²<sub>red</sub> 3.27); 90–160 °C: 7.047 ± 0.048 (χ²<sub>red</sub> 6.12) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 0.826 ± 0.003 (χ²<sub>red</sub> 9.87); 25–90 °C: 0.843 ± 0.008 (χ²<sub>red</sub> 7.98); 90–160 °C: 0.818 ± 0.006 (χ²<sub>red</sub> 5.07) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 9.11 (melt 6.7) | comp | `extend` progress |
| R<sub>g</sub> (Å) | 31.24 ± 0.12 | 32.21 ± 0.21 | 30.84 ± 0.34 | 30.80 ± 0.39 | — | trend | `sweep` |
| R<sub>g</sub> (Å), long hold (D53) | 35.13 ± 0.51 | 32.15 ± 0.42 | 30.94 ± 0.15 | 29.79 ± 0.28 | — | trend | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| R<sub>g</sub> (Å), 500 K hold | — | — | — | — | 500 K: 28.75 ± 0.34 | comp | `extend` |
| R<sub>ee</sub> (Å) | 77.1 ± 0.5 | 84.2 ± 1.0 | 77.6 ± 2.1 | 78.3 ± 1.4 | — | trend | `sweep` |
| R<sub>ee</sub> (Å), long hold (D53) | 89.5 ± 1.9 | 80.6 ± 2.0 | 78.3 ± 0.6 | 74.8 ± 1.0 | — | trend | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| R<sub>ee</sub> (Å), 500 K hold | — | — | — | — | 500 K: 71.9 ± 1.3 | comp | `extend` |
| C<sub>n</sub> | 10.27 ± 0.08 | 11.78 ± 0.19 | 10.58 ± 0.36 | 10.70 ± 0.34 | — | trend | `sweep` |
| C<sub>n</sub>, long hold (D53) | 13.88 ± 0.52 | 11.42 ± 0.43 | 10.63 ± 0.15 | 9.75 ± 0.25 | — | trend | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| C<sub>n</sub>, 500 K hold | — | — | — | — | 500 K: 9.12 ± 0.30 | comp | `extend` |
| P2 1/e time (ps) | 123 | 25.5 | 12.7 | 7.61 | 500 K: 8.47 | corr | `extend`, `sweep` |
| P2 1/e time (ps), long hold (D53) | 144 | 82.3 | 75.6 | 72.5 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| segment MSD at 1 ns lag (Å²) | 158.2 | 275.7 | 355.3 | 397.7 | 500 K: 501.2 | corr | `extend`, `sweep` |
| segment MSD at 1 ns lag (Å²), long hold (D53) | 161.6 | 279.6 | 349.5 | 396.2 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| max chain COM MSD (Å²) at lag | 176.9 at 12.5 ns | 396 at 12.5 ns | 522.8 at 12.5 ns | 572.5 at 12.5 ns | 500 K: 2120 at 40 ns | corr | `extend`, `sweep` |
| max chain COM MSD (Å²) at lag, long hold (D53) | 2019 at 138.8 ns | 2069 at 88 ns | 4881 at 150 ns | 4669 at 127.8 ns | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.18 | 0.38 | 0.55 | 0.60 | 500 K: 2.56 | corr | `extend`, `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag, long hold (D53) | 1.64 | 2.00 | 5.10 | 5.26 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.90) | not diffusive (slope 0.98) | not diffusive (slope 0.90) | not diffusive (slope 0.99) | 500 K: not diffusive (slope 0.91) | corr | `extend`, `sweep` |
| D<sub>COM</sub> (cm²/s), long hold (D53) | not diffusive (slope 0.95) | not diffusive (slope 1.04) | 5.31e-07 ± 1.8e-08 | 6.08e-07 ± 6.2e-09 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| η<sub>Rouse</sub>, Rouse viscosity estimate (Pa·s), long hold (D53) | — | — | 0.025 | 0.021 | — | corr | `diffuse_160C` progress, `diffuse_130C` progress |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached (extrap. 46.5) | not reached (extrap. 30.7) | not reached (extrap. 18.2) | not reached (extrap. 25.5) | 500 K: 11.1 | corr | `extend`, `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns), long hold (D53) | 94.7 | 37.9 | 26.5 | 16.8 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached (extrap. 103) | not reached (extrap. 46.1) | not reached (extrap. 25) | not reached (extrap. 33.1) | 500 K: 14.5 | corr | `extend`, `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns), long hold (D53) | 116 | 46.3 | 34.1 | 23.3 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.168 | 0.112 | 0.103 | 0.094 | 500 K: 0.093 | — | `extend`, `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated), long hold (D53) | 0.192 | 0.116 | 0.103 | 0.093 | — | — | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| E<sub>app</sub> (MPa), 10⁸ s⁻¹, mean ± SD | -54.8 ± 37.2 | 184 ± 81.2 | -23.2 ± 163 | 64.5 ± 38.8 | — | trend | `tensile_130C`, `tensile_160C`, `tensile_25C`, `tensile_90C` |
| E<sub>app</sub> (MPa), 10⁹ s⁻¹, mean ± SD | 141 ± 133 | 183 ± 261 | -179 ± 450 | 19.1 ± 376 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| ν, fit up to the E<sub>app</sub> strain, 10⁸ s⁻¹, mean ± SD | 0.45 ± 0.04 | 0.44 ± 0.05 | 0.45 ± 0.11 | 0.52 ± 0.05 | — | trend | `tensile_130C`, `tensile_160C`, `tensile_25C`, `tensile_90C` |
| ν, fit up to the E<sub>app</sub> strain, 10⁹ s⁻¹, mean ± SD | 0.46 ± 0.01 | 0.44 ± 0.09 | 0.70 ± 0.15 | 0.48 ± 0.28 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| ν, whole run, 10⁸ s⁻¹, mean ± SD | 0.50 ± 0.00 | 0.50 ± 0.00 | 0.50 ± 0.00 | 0.50 ± 0.00 | — | trend | `tensile_130C`, `tensile_160C`, `tensile_25C`, `tensile_90C` |
| ν, whole run, 10⁹ s⁻¹, mean ± SD | 0.50 ± 0.00 | 0.50 ± 0.00 | 0.50 ± 0.00 | 0.50 ± 0.00 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| σ<sub>peak</sub> (MPa), 10⁸ s⁻¹, mean ± SD | 6.4 ± 2.2 | 5.2 ± 0.71 | 5.2 ± 0.88 | 4.8 ± 0.9 | — | trend | `tensile_130C`, `tensile_160C`, `tensile_25C`, `tensile_90C` |
| σ<sub>peak</sub> (MPa), 10⁹ s⁻¹, mean ± SD | 19 ± 3.7 | 13 ± 0.25 | 12 ± 0.44 | 11 ± 1.3 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| ε<sub>peak</sub>, 10⁸ s⁻¹, mean ± SD | 0.249 ± 0.123 | 0.442 ± 0.045 | 0.367 ± 0.079 | 0.428 ± 0.089 | — | trend | `tensile_130C`, `tensile_160C`, `tensile_25C`, `tensile_90C` |
| ε<sub>peak</sub>, 10⁹ s⁻¹, mean ± SD | 0.446 ± 0.023 | 0.408 ± 0.027 | 0.383 ± 0.105 | 0.399 ± 0.072 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |
| flow σ (MPa), 10⁸ s⁻¹, mean ± SD | 2.3 ± 1.6 | 2.4 ± 0.24 | 2.7 ± 0.87 | 2.1 ± 0.58 | — | trend | `tensile_130C`, `tensile_160C`, `tensile_25C`, `tensile_90C` |
| flow σ (MPa), 10⁹ s⁻¹, mean ± SD | 12 ± 3.4 | 7.1 ± 0.25 | 7 ± 0.6 | 5.4 ± 0.55 | — | trend | `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_90C_r1e9` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field `sdk_cg`, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-21 20:13 UTC, ended 2026-10-22 01:07 UTC; reads `systems/pe_cg_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.31 at 10.0 ns, 1/e at 8.84 ns; COM MSD/⟨R<sub>g</sub>²⟩ 0.90); C<sub>n</sub> 9.02 vs 6.7 (outside band, info); no drift (Δ +0.65 ± 0.49)
  - monitor flags: R<sub>ee</sub> 1/e 8.84 ns; MSD/R<sub>g</sub>² 0.90; drift seg 6,10,12,13
- **extend** (rdyu-rog): finished; started 2026-10-26 17:57 UTC, ended 2026-10-26 23:45 UTC; reads `../prep/hold.data`
  - 500 K hold 80.0 ns: D47 PASS (R<sub>ee</sub> ACF 0.14 at 40.0 ns, 1/e at 11.12 ns; COM MSD/⟨R<sub>g</sub>²⟩ 2.56); C<sub>n</sub> 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)
- **cool** (rdyu-rog): finished; started 2026-10-26 23:47 UTC, ended 2026-10-27 03:51 UTC; reads `../extend/hold_ext_60ns.data`
  - monitor flags: drift seg 4,5,6,8; hyst max 0.11%
- **sweep** (rdyu-rog): finished; started 2026-10-27 03:52 UTC, ended 2026-10-27 22:32 UTC; reads `../cool/cooled.data`
  - monitor flags: drift seg 2,8,14; step!=hold 130 C; hyst max 0.11%
- **`diffuse_25C`** (rdyu-rog): interrupted, 92.5%; started 2026-10-30 18:01 UTC, ended 2026-11-02 13:57 UTC; reads `../sweep/hold_25C.data`
  - 500 K hold 273.2 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.28 at 136.6 ns, 1/e at 95.70 ns; COM MSD/⟨R<sub>g</sub>²⟩ 1.61); C<sub>n</sub> 13.87 vs 6.7 (outside band, info); no drift (Δ +0.01 ± 1.05)
  - monitor flags: D<sub>COM</sub> not diffusive (log-slope 0.91 at the longest lag, MSD/R<sub>g</sub>² 1.61); MSD/R<sub>g</sub>² 1.61
- **`diffuse_160C`** (rdyu-rog): interrupted, 85.2%; started 2026-10-30 18:05 UTC, ended 2026-11-02 13:57 UTC; reads `../sweep/hold_160C.data`
  - 500 K hold 251.6 ns: D47 criteria on this hold PASS (R<sub>ee</sub> ACF 0.01 at 125.8 ns, 1/e at 16.84 ns; COM MSD/⟨R<sub>g</sub>²⟩ 5.15); C<sub>n</sub> 9.75 vs 6.7 (outside band, info); no drift (Δ -0.56 ± 0.34)
  - monitor flags: D<sub>COM</sub> diffusive 6e-07 cm²/s over 55.8–126 ns; η<sub>Rouse</sub> 0.021 Pa·s; MSD/R<sub>g</sub>² 5.15
- **`diffuse_90C`** (rdyu-rog): interrupted, 58.7%; started 2026-10-31 17:54 UTC, ended 2026-11-02 13:57 UTC; reads `../sweep/hold_90C.data`
  - 500 K hold 174.2 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.08 at 87.1 ns, 1/e at 37.79 ns; COM MSD/⟨R<sub>g</sub>²⟩ 1.98); C<sub>n</sub> 11.42 vs 6.7 (outside band, info); drift (Δ -1.10 ± 0.52)
  - monitor flags: D<sub>COM</sub> not diffusive (log-slope 1.03 at the longest lag, MSD/R<sub>g</sub>² 1.98); MSD/R<sub>g</sub>² 1.98
- **`diffuse_130C`** (rdyu-rog): finished; started 2026-11-02 19:07 UTC, ended 2026-11-04 19:34 UTC; reads `../sweep/hold_130C.data`
  - 500 K hold 300.0 ns: D47 criteria on this hold PASS (R<sub>ee</sub> ACF 0.02 at 150.0 ns, 1/e at 26.49 ns; COM MSD/⟨R<sub>g</sub>²⟩ 5.10); C<sub>n</sub> 10.66 vs 6.7 (outside band, info); no drift (Δ +0.26 ± 0.28)
  - monitor flags: D<sub>COM</sub> diffusive 5.3e-07 cm²/s over 58.3–150 ns; η<sub>Rouse</sub> 0.025 Pa·s; MSD/R<sub>g</sub>² 5.10
- **`tensile_160C_r1e9`** (rdyu-rog): finished; started 2026-10-30 17:26 UTC, ended 2026-10-30 18:00 UTC; reads `../sweep/hold_160C.data`
- **`tensile_90C_r1e9`** (rdyu-rog): finished; started 2026-10-30 17:26 UTC, ended 2026-10-30 18:01 UTC; reads `../sweep/hold_90C.data`
- **`tensile_25C_r1e9`** (rdyu-rog): finished; started 2026-10-30 17:26 UTC, ended 2026-10-30 18:05 UTC; reads `../sweep/hold_25C.data`
- **`tensile_130C_r1e9`** (rdyu-rog): finished; started 2026-10-30 18:00 UTC, ended 2026-10-30 18:34 UTC; reads `../sweep/hold_130C.data`
- **`tensile_25C`** (rdyu-rog): finished; started 2026-10-30 18:34 UTC, ended 2026-10-31 00:19 UTC; reads `../sweep/hold_25C.data`
  - monitor flags: drift seg 1,2
- **`tensile_160C`** (rdyu-rog): finished; started 2026-10-31 00:19 UTC, ended 2026-10-31 05:54 UTC; reads `../sweep/hold_160C.data`
  - monitor flags: drift seg 2
- **`tensile_90C`** (rdyu-rog): finished; started 2026-10-31 05:54 UTC, ended 2026-10-31 11:50 UTC; reads `../sweep/hold_90C.data`
- **`tensile_130C`** (rdyu-rog): finished; started 2026-10-31 11:50 UTC, ended 2026-10-31 17:54 UTC; reads `../sweep/hold_130C.data`
  - monitor flags: drift seg 2
- Superseded (not used): `prep_server_cancelled` (cancelled/killed?); `prep_timeout12h` (cancelled/killed?); `sweep_old_20ns_box` (finished)

**`cavitation_compare` analysis**

Pore analysis (`sepsim analyze pore`, generated 2026-11-10 19:19 UTC on —):

`pooled`:

| `summary.plateau_MPa` | T (°C) |
|---|---|
| 16.32 | 25 |
| 19.44 | 25 |
| 31.79 | 25 |
| 16.32 | 90 |
| 22.39 | 90 |
| 14.56 | 130 |
| 20.53 | 130 |
| 11.57 | 160 |
| 13.53 | 160 |
| 18.82 | 160 |

`runs`:

| `curve.plateau_MPa` | `curve.t_cav_ps` | `summary.plateau_MPa` | T (°C) |
|---|---|---|---|
| 14.19 | 448 | 14.19 | 130 |
| 14.73 | 583 | 14.73 | 130 |
| 14.78 | 506 | 14.78 | 130 |
| 20.98 | 55 | 20.98 | 130 |
| 20.65 | 53 | 20.65 | 130 |
| 19.97 | 60 | 19.97 | 130 |
| 13.57 | 527 | 13.57 | 160 |
| 12.92 | 440 | 12.92 | 160 |
| 14.09 | 548 | 14.09 | 160 |
| 11.57 | 4872 | 11.57 | 160 |
| 18.28 | 69 | 18.28 | 160 |
| 20.04 | 50 | 20.04 | 160 |
| 18.14 | 71 | 18.14 | 160 |
| 18.61 | 518 | 18.61 | 25 |
| 19.77 | 523 | 19.77 | 25 |
| 19.93 | 499 | 19.93 | 25 |
| 16.32 | 4580 | 16.32 | 25 |
| 32.54 | 62 | 32.54 | 25 |
| 32.91 | 60 | 32.91 | 25 |
| 29.92 | 61 | 29.92 | 25 |
| 16.96 | 513 | 16.96 | 90 |
| 15.76 | 507 | 15.76 | 90 |
| 16.23 | 525 | 16.23 | 90 |
| 21.65 | 62 | 21.65 | 90 |
| 23.35 | 57 | 23.35 | 90 |
| 22.16 | 63 | 22.16 | 90 |

- Note: The box is an amorphous melt (no crystallinity): cavitation of a melt under fast triaxial tension, not the cavitation of the amorphous layers between lamellae of a stretched semicrystalline separator.
- Note: MD strain rates (10⁸–10¹⁰ s⁻¹ per axis) are many orders of magnitude above experiment, and CG time runs ≈ 4× fast: `σ_cav` is rate-inflated.
- Note: The strain is homogeneous and affine (fix deform with remap x): the box cannot neck or localise beyond its size, and NVT removes the heat of the deformation.
- Note: Voids are defined by a probe: space farther than the probe radius from every bead centre, swept by the probe sphere, on a 2 Å grid; the volumes depend on the probe radius (--probe-a).
- Note: A small periodic box holds about one void: after cavitation it grows as a single cavity, so the plateau stress is box-size dependent (compare the 2×2×2 box).
- Note: Plain LJ cutoff without tail correction: the missing attractive tail grows in magnitude as the density drops, biasing `σ_h` low at large strain.

**`diffuse_130C` analysis**

`sepsim analyze hold`, generated 2026-11-07 03:41 UTC on rdyu-server, run finished; segment Stage 1: NPT hold 300000 ps at 403.15 K; 300 ns analysed of 300 ns planned (complete).

- Note: Relaxation times use lags up to half the analysed hold (150 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: log block 7 (Stage 1: NPT hold 300000 ps at 403.15 K, run 7/12) has 700000 steps, the deck plans 2500000: thermo may be assigned to the wrong segment
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`diffuse_160C` analysis**

`sepsim analyze hold`, generated 2026-11-07 03:42 UTC on rdyu-server, run interrupted; segment Stage 1: NPT hold 300000 ps at 433.15 K; 255.6 ns analysed of 300 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (127.8 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`diffuse_25C` analysis**

`sepsim analyze hold`, generated 2026-11-07 03:41 UTC on rdyu-server, run interrupted; segment Stage 1: NPT hold 300000 ps at 298.15 K; 277.5 ns analysed of 300 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (138.8 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`diffuse_90C` analysis**

`sepsim analyze hold`, generated 2026-11-07 03:41 UTC on rdyu-server, run interrupted; segment Stage 1: NPT hold 300000 ps at 363.15 K; 176 ns analysed of 300 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (88 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`extend` analysis**

`sepsim analyze hold`, generated 2026-11-09 18:57 UTC on rdyu-server, run finished; segment Stage 1: NPT hold extension 60000 ps at 500 K, 1 atm; 80 ns analysed of 60 ns planned (complete).

- Note: Relaxation times use lags up to half the analysed hold (40 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`sweep` analysis** (CG PE C240, 80.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-07 03:38 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.83453 ± 0.00009 | 1.000 ± 0.015 | 31.24 ± 0.12 | 77.1 ± 0.5 | 10.27 ± 0.08 | 123 | 176.9 at 12.5 ns | not diffusive (slope 0.90) | yes |
| 90 | 0.79783 ± 0.00007 | 1.292 ± 0.019 | 32.21 ± 0.21 | 84.2 ± 1.0 | 11.78 ± 0.19 | 25.5 | 396 at 12.5 ns | not diffusive (slope 0.98) | yes |
| 130 | 0.77580 ± 0.00011 | 1.502 ± 0.027 | 30.84 ± 0.34 | 77.6 ± 2.1 | 10.58 ± 0.36 | 12.7 | 522.8 at 12.5 ns | not diffusive (slope 0.90) | yes |
| 160 | 0.75938 ± 0.00009 | 1.662 ± 0.026 | 30.80 ± 0.39 | 78.3 ± 1.4 | 10.70 ± 0.34 | 7.61 | 572.5 at 12.5 ns | not diffusive (slope 0.99) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 6.966 ± 0.041 | 20.9 | 0.826 ± 0.003 | 9.87 | 15 |
| 90–160 | 7.047 ± 0.048 | 6.12 | 0.818 ± 0.006 | 5.07 | 8 |
| 25–90 | 6.925 ± 0.035 | 3.27 | 0.843 ± 0.008 | 7.98 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; CG also drops degrees of freedom (all motion inside a 3-CH<sub>2</sub> bead), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: D37 chain check FAIL on the prep hold + extension: C<sub>n</sub> plateau 9.11 vs melt 6.7 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.

**`tensile_130C` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:58 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

130 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 164 ± 76 | 0.40 | 0.50 | 4.3 | 0.289 | 1.7 | 403.1 |
| y | 0.500 | -93.7 ± 78 | 0.37 | 0.50 | 6 | 0.365 | 3 | 403.2 |
| z | 0.500 | -140 ± 74 | 0.58 | 0.50 | 5.2 | 0.446 | 3.3 | 403.1 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

**`tensile_130C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:58 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

130 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | -134 ± 2e+02 | 0.85 | 0.50 | 12 | 0.279 | 6.8 | 403.3 |
| y | 0.500 | 248 ± 1.4e+02 | 0.56 | 0.50 | 12 | 0.383 | 7.7 | 403.4 |
| z | 0.500 | -650 ± 1.8e+02 | 0.68 | 0.50 | 12 | 0.488 | 6.6 | 402.8 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

**`tensile_160C` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:58 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

160 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 34.1 ± 67 | 0.57 | 0.50 | 5.8 | 0.325 | 2.4 | 433.1 |
| y | 0.500 | 51.3 ± 69 | 0.48 | 0.50 | 4.3 | 0.489 | 2.4 | 433.1 |
| z | 0.500 | 108 ± 78 | 0.51 | 0.50 | 4.2 | 0.469 | 1.4 | 433.1 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

**`tensile_160C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:59 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

160 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 43.2 ± 1.9e+02 | 0.38 | 0.50 | 11 | 0.403 | 5.2 | 433.3 |
| y | 0.500 | 382 ± 1.8e+02 | 0.27 | 0.50 | 12 | 0.469 | 6 | 432.9 |
| z | 0.500 | -368 ± 2.3e+02 | 0.80 | 0.50 | 9.8 | 0.326 | 4.9 | 433.0 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

**`tensile_25C` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:58 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

25 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | -71.9 ± 73 | 0.46 | 0.50 | 8.5 | 0.333 | 3.9 | 298.1 |
| y | 0.500 | -12 ± 72 | 0.49 | 0.50 | 4 | 0.108 | 0.61 | 298.1 |
| z | 0.500 | -80.4 ± 66 | 0.42 | 0.50 | 6.6 | 0.306 | 2.5 | 298.1 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

**`tensile_25C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:58 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

25 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 91.3 ± 2.1e+02 | 0.45 | 0.50 | 18 | 0.470 | 12 | 298.1 |
| y | 0.500 | 292 ± 2.2e+02 | 0.47 | 0.50 | 16 | 0.425 | 8.3 | 298.1 |
| z | 0.500 | 39.7 ± 1.7e+02 | 0.46 | 0.50 | 23 | 0.443 | 15 | 297.9 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

**`tensile_90C` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:58 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

90 °C, 10⁸ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 268 ± 80 | 0.39 | 0.50 | 4.9 | 0.429 | 2.4 | 363.1 |
| y | 0.500 | 179 ± 76 | 0.49 | 0.50 | 4.7 | 0.492 | 2.1 | 363.1 |
| z | 0.500 | 106 ± 71 | 0.43 | 0.50 | 6 | 0.404 | 2.6 | 363.1 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

**`tensile_90C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-09 18:58 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

90 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | -64.9 ± 1.5e+02 | 0.52 | 0.50 | 13 | 0.377 | 7.3 | 363.3 |
| y | 0.500 | 455 ± 3e+02 | 0.34 | 0.50 | 13 | 0.422 | 7.1 | 363.1 |
| z | 0.500 | 160 ± 2.5e+02 | 0.48 | 0.50 | 14 | 0.425 | 6.8 | 363.2 |

- Note: The box is an amorphous melt above T<sub>g</sub> (T<sub>g</sub> is below 25 °C for PE, D14), so the response is viscoelastic and rate-dependent: these are not the moduli of a semicrystalline separator, whose stiffness and yield come from its crystallinity.
- Note: E<sub>app</sub> is the apparent (high-frequency) modulus at the simulated strain rate, many orders of magnitude above experiment; it falls with the rate.
- Note: There is no true yield in a melt: the peak or plateau is a viscous flow stress (≈ 3 η × rate for a Newtonian melt), again rate-dependent.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt) lags the imposed strain, so the lateral contraction trails the axial extension (ν low at small strain); a fully relaxed melt approaches ν = 0.5.
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.

</details>

### `pe_cg_amorph_n40_c1500_s1`

PE CG, bulk amorphous box, 40 chains × C1500, 20,000 beads; grown chains (seed 1). Status: finished: prep, extend, cool, sweep.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 n/a (long CG chain); ACF 0.68 at 250.0 ns, MSD/⟨R<sub>g</sub>²⟩ 0.12; 500.0 ns at 500 K; no C<sub>n</sub> drift: accepted | — | `extend` progress |
| ρ (g/cm³) | 0.83817 ± 0.00004 | 0.80154 ± 0.00006 | 0.78019 ± 0.00004 | 0.76444 ± 0.00003 | 500 K: 0.72853 ± 0.00014 | comp | `extend`, `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.995 ± 0.014 | 1.265 ± 0.020 | 1.435 ± 0.024 | 1.572 ± 0.026 | 500 K: 2.098 ± 0.010 | comp | `extend`, `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 6.809 ± 0.022 (χ²<sub>red</sub> 27.2); 25–90 °C: 6.862 ± 0.018 (χ²<sub>red</sub> 2.29); 90–160 °C: 6.797 ± 0.033 (χ²<sub>red</sub> 11.8) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 0.812 ± 0.003 (χ²<sub>red</sub> 72.7); 25–90 °C: 0.840 ± 0.005 (χ²<sub>red</sub> 14.9); 90–160 °C: 0.793 ± 0.001 (χ²<sub>red</sub> 2.48) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 7.43 (melt 6.7) | trend | `extend` progress |
| R<sub>g</sub> (Å) | 67.79 ± 0.11 | 70.28 ± 0.13 | 70.04 ± 0.16 | 68.89 ± 0.25 | — | trend | `sweep` |
| R<sub>g</sub> (Å), 500 K hold | — | — | — | — | 500 K: 65.75 ± 0.71 | trend | `extend` |
| R<sub>ee</sub> (Å) | 175.1 ± 1.4 | 179.3 ± 1.0 | 185.2 ± 1.6 | 169.2 ± 1.9 | — | trend | `sweep` |
| R<sub>ee</sub> (Å), 500 K hold | — | — | — | — | 500 K: 170.0 ± 2.4 | trend | `extend` |
| C<sub>n</sub> | 7.91 ± 0.02 | 8.46 ± 0.03 | 8.44 ± 0.03 | 8.06 ± 0.07 | — | trend | `sweep` |
| C<sub>n</sub>, 500 K hold | — | — | — | — | 500 K: 7.43 ± 0.16 | trend | `extend` |
| P2 1/e time (ps) | 128 | 26.9 | 14.3 | 8.78 | 500 K: 68.7 | corr | `extend`, `sweep` |
| segment MSD at 1 ns lag (Å²) | 153.6 | 250.2 | 294.9 | 322.3 | 500 K: 415.8 | corr | `extend`, `sweep` |
| max chain COM MSD (Å²) at lag | 21.94 at 12.5 ns | 29.7 at 12.5 ns | 37.17 at 12.5 ns | 44.85 at 12.5 ns | 500 K: 518.9 at 250 ns | todo | `extend`, `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.00 | 0.01 | 0.01 | 0.01 | 500 K: 0.12 | todo | `extend`, `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.42) | not diffusive (slope 0.69) | not diffusive (slope 0.48) | not diffusive (slope 0.50) | 500 K: not diffusive (slope 0.99) | todo | `extend`, `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached | not reached | not reached | 500 K: not reached (extrap. 1.04e+03) | todo | `extend`, `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | 500 K: not reached (extrap. 1.63e+03) | todo | `extend`, `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.191 | 0.111 | 0.095 | 0.088 | 500 K: 0.089 | — | `extend`, `sweep` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 40 chains × C1500 (C1500H3002), 20,000 atoms/beads, force field `sdk_cg`, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 n/a (long CG chain); ACF 0.68 at 250.0 ns, MSD/⟨R<sub>g</sub>²⟩ 0.12; 500.0 ns at 500 K; no C<sub>n</sub> drift: accepted
- C<sub>n</sub> plateau (D37): 7.43 vs 6.7 (outside band, info); no drift (Δ +0.21 ± 0.30)

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-24 08:10 UTC, ended 2026-10-24 13:16 UTC; reads `systems/pe_cg_amorph_n40_c1500_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.86 at 10.0 ns, 1/e not reached; COM MSD/⟨R<sub>g</sub>²⟩ 0.03); C<sub>n</sub> 5.58 vs 6.7 (outside band, info); drift (Δ +0.37 ± 0.09)
  - monitor flags: R<sub>ee</sub> not decorrelated (0.86 at 10.0 ns); MSD/R<sub>g</sub>² 0.03; drift seg 5,10,11,12
- **extend** (rdyu-rog): finished; started 2026-10-24 13:18 UTC, ended 2026-10-26 02:01 UTC; reads `../prep/hold.data`
  - 500 K hold 500.0 ns: D47 FAIL (R<sub>ee</sub> ACF 0.68 at 250.0 ns, 1/e not reached; COM MSD/⟨R<sub>g</sub>²⟩ 0.12); C<sub>n</sub> 7.43 vs 6.7 (outside band, info); no drift (Δ +0.21 ± 0.30)
  - monitor flags: drift seg 1
- **cool** (rdyu-rog): finished; started 2026-10-26 02:02 UTC, ended 2026-10-26 05:01 UTC; reads `../extend/hold_ext_500ns.data`
  - monitor flags: drift seg 3,6,7,8; hyst max 0.11%
- **sweep** (rdyu-rog): finished; started 2026-10-26 05:01 UTC, ended 2026-10-26 17:56 UTC; reads `../cool/cooled.data`
  - monitor flags: drift seg 1,2,3,6,9,14; step!=hold 130 C; hyst max 0.11%
- Superseded (not used): `sweep_cancelled_unrelaxed` (cancelled/killed?)

**`extend` analysis**

`sepsim analyze hold`, generated 2026-11-09 19:34 UTC on rdyu-server, run finished; segment Stage 1: NPT hold extension 500000 ps at 500 K, 1 atm; 500 ns analysed of 500 ns planned (complete).

- Note: Relaxation times use lags up to half the analysed hold (250 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: ../prep/hold.dcd has frames every 10 ps, the extension 100 ps: chain checks use the extension alone
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`sweep` analysis** (CG PE C1500, 500.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-07 03:50 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.83817 ± 0.00004 | 0.995 ± 0.014 | 67.79 ± 0.11 | 175.1 ± 1.4 | 7.91 ± 0.02 | 128 | 21.94 at 12.5 ns | not diffusive (slope 0.42) | yes |
| 90 | 0.80154 ± 0.00006 | 1.265 ± 0.020 | 70.28 ± 0.13 | 179.3 ± 1.0 | 8.46 ± 0.03 | 26.9 | 29.7 at 12.5 ns | not diffusive (slope 0.69) | yes |
| 130 | 0.78019 ± 0.00004 | 1.435 ± 0.024 | 70.04 ± 0.16 | 185.2 ± 1.6 | 8.44 ± 0.03 | 14.3 | 37.17 at 12.5 ns | not diffusive (slope 0.48) | yes |
| 160 | 0.76444 ± 0.00003 | 1.572 ± 0.026 | 68.89 ± 0.25 | 169.2 ± 1.9 | 8.06 ± 0.07 | 8.78 | 44.85 at 12.5 ns | not diffusive (slope 0.50) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 6.809 ± 0.022 | 27.2 | 0.812 ± 0.003 | 72.7 | 15 |
| 90–160 | 6.797 ± 0.033 | 11.8 | 0.793 ± 0.001 | 2.48 | 8 |
| 25–90 | 6.862 ± 0.018 | 2.29 | 0.840 ± 0.005 | 14.9 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; CG also drops degrees of freedom (all motion inside a 3-CH<sub>2</sub> bead), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep hold + extension (extend/progress.json: end-to-end ACF 0.68 at 250.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.12, needs >= 2).
- Note: D37 chain check FAIL on the prep hold + extension: C<sub>n</sub> plateau 7.43 vs melt 6.7 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.

</details>

### `pe_cg_amorph_n320_c240_s1_rep222`

PE CG, bulk amorphous box, replicated 2×2×2, 320 chains × C240, 25,600 beads; built from `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`). Status: finished: extend (stopped after D47 PASS).

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress |
| ρ (g/cm³) | — | — | — | — | 500 K: 0.72370 ± 0.00004 | todo | `extend` |
| κ<sub>T</sub> (GPa⁻¹) | — | — | — | — | 500 K: 2.132 ± 0.021 | todo | `extend` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 9.18 (melt 6.7) | comp | `extend` progress |
| R<sub>g</sub> (Å), 500 K hold | — | — | — | — | 500 K: 28.83 ± 0.15 | comp | `extend` |
| R<sub>ee</sub> (Å), 500 K hold | — | — | — | — | 500 K: 72.2 ± 0.7 | comp | `extend` |
| C<sub>n</sub>, 500 K hold | — | — | — | — | 500 K: 9.17 ± 0.13 | comp | `extend` |
| P2 1/e time (ps) | — | — | — | — | 500 K: 8.48 | todo | `extend` |
| segment MSD at 1 ns lag (Å²) | — | — | — | — | 500 K: 518.2 | todo | `extend` |
| max chain COM MSD (Å²) at lag | — | — | — | — | 500 K: 2206 at 36.27 ns | todo | `extend` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | — | — | — | — | 500 K: 2.65 | todo | `extend` |
| D<sub>COM</sub> (cm²/s) | — | — | — | — | 500 K: not diffusive (slope 0.90) | todo | `extend` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | — | — | — | — | 500 K: 10.9 | todo | `extend` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | — | — | — | — | 500 K: 14.5 | todo | `extend` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | — | — | — | — | 500 K: 0.092 | — | `extend` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.7302 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Built from: `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`)

**Equilibration**

- Verdict: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **extend** (rdyu-rog): stopped after D47 PASS (cancelled/killed?), 90.7%; started 2026-10-29 11:25 UTC; reads `systems/pe_cg_amorph_n320_c240_s1_rep222/data.lmp`
  - 500 K hold 72.5 ns: D47 PASS (R<sub>ee</sub> ACF 0.09 at 36.3 ns, 1/e at 10.88 ns; COM MSD/⟨R<sub>g</sub>²⟩ 2.65); C<sub>n</sub> 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)
- Superseded (not used): `extend_cpu_job92_cancelled_48ns` (cancelled/killed?)

**`extend` analysis**

`sepsim analyze hold`, generated 2026-11-09 18:46 UTC on rdyu-server, run started; segment Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm; 72.53 ns analysed of 80 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (36.27 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: hold not complete: thermo and trajectory over the part run
- Note: ../prep/hold.dcd not found: chain checks use the extension alone
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

- Sweep analysis: not analysed yet.

</details>

### `pe_cg_amorph_n640_c240_s1_rep441`

PE CG, bulk amorphous box, replicated 4×4×1, 640 chains × C240, 51,200 beads; built from `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`). Status: finished: extend.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | — | `extend` progress |
| ρ (g/cm³) | — | — | — | — | 500 K: 0.72364 ± 0.00002 | todo | `extend` |
| κ<sub>T</sub> (GPa⁻¹) | — | — | — | — | 500 K: 2.118 ± 0.022 | todo | `extend` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 8.93 (melt 6.7) | comp | `extend` progress |
| R<sub>g</sub> (Å), 500 K hold | — | — | — | — | 500 K: 28.53 ± 0.05 | comp | `extend` |
| R<sub>ee</sub> (Å), 500 K hold | — | — | — | — | 500 K: 71.3 ± 0.2 | comp | `extend` |
| C<sub>n</sub>, 500 K hold | — | — | — | — | 500 K: 8.94 ± 0.04 | comp | `extend` |
| P2 1/e time (ps) | — | — | — | — | 500 K: 68.3 | todo | `extend` |
| segment MSD at 1 ns lag (Å²) | — | — | — | — | 500 K: 533.8 | todo | `extend` |
| max chain COM MSD (Å²) at lag | — | — | — | — | 500 K: 2723 at 40 ns | todo | `extend` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | — | — | — | — | 500 K: 3.35 | todo | `extend` |
| D<sub>COM</sub> (cm²/s) | — | — | — | — | 500 K: not diffusive (slope 0.97) | todo | `extend` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | — | — | — | — | 500 K: 10.7 | todo | `extend` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | — | — | — | — | 500 K: 14.5 | todo | `extend` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | — | — | — | — | 500 K: 0.092 | — | `extend` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.7302 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Built from: `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`)

**Equilibration**

- Verdict: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **extend** (rdyu-rog): finished; started 2026-11-02 19:07 UTC, ended 2026-11-06 10:06 UTC; reads `systems/pe_cg_amorph_n640_c240_s1_rep441/data.lmp`
  - 500 K hold 80.0 ns: D47 PASS (R<sub>ee</sub> ACF 0.06 at 40.0 ns, 1/e at 10.69 ns; COM MSD/⟨R<sub>g</sub>²⟩ 3.35); C<sub>n</sub> 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**`extend` analysis**

`sepsim analyze hold`, generated 2026-11-07 06:28 UTC on rdyu-server, run finished; segment Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm; 80 ns analysed of 80 ns planned (complete).

- Note: Relaxation times use lags up to half the analysed hold (40 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: log block 2 (Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm, run 2/8) has 100000 steps, the deck plans 1000000: thermo may be assigned to the wrong segment
- Note: ../prep/hold.dcd not found: chain checks use the extension alone
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

- Sweep analysis: not analysed yet.

</details>

### `pe_cg_pore500k_w10nm_n40_c240_s1`

PE CG, wide 10 nm slit pore made at 500 K, 40 chains × C240, 3,200 beads; built from `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`). Status: finished: `pore_relax`.

No analysed properties yet. Equilibration: from `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field `sdk_cg`, box density 0.2941 g/cm³ (as built)
- Pore: wide pore, nominal 10 nm, wall 6.74 nm, clear gap 4.24 nm, area 45.4 nm²
- Built from: `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`)

**Equilibration**

- Verdict: from `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **`pore_relax`** (rdyu-server): finished; started 2026-10-26 23:51 UTC, ended 2026-10-27 00:18 UTC; reads `systems/pe_cg_pore500k_w10nm_n40_c240_s1/data.lmp`
- Superseded (not used): `pore_relax_old_20ns_box` (finished)

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| wide | 10 nm (at 500 K) | — | 6.7 nm (500 K) | 6.7 × 6.7 nm (500 K) | — | finished: `pore_relax` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_pore_w5nm_n40_c240_s1`

PE CG, 5 nm dry slit pore, 40 chains × C240, 3,200 beads; built from `pe_cg_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`). Status: finished: pore.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | — | `extend` progress of `pe_cg_amorph_n40_c240_s1` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 9.11 (melt 6.7) | n/a | `extend` progress of `pe_cg_amorph_n40_c240_s1` |
| R<sub>g</sub> (Å) | 32.39 ± 0.48 | 32.54 ± 0.13 | 29.25 ± 0.17 | 27.31 ± 0.15 | — | trend | `pore` |
| R<sub>ee</sub> (Å) | 81.6 ± 1.3 | 82.1 ± 0.9 | 71.2 ± 1.1 | 66.6 ± 0.5 | — | trend | `pore` |
| C<sub>n</sub> | 11.25 ± 0.39 | 11.89 ± 0.15 | 9.09 ± 0.14 | 7.85 ± 0.12 | — | trend | `pore` |
| P2 1/e time (ps) | 85.8 | 18.3 | 9.12 | 6.04 | — | corr | `pore` |
| P2 1/e time, surface layer (ps) | 58.7 | 13 | 6.77 | 4.57 | — | corr | `pore` |
| P2 1/e time, interior layer (ps) | 116 | 24.6 | 12.4 | 7.93 | — | corr | `pore` |
| segment MSD at 1 ns lag (Å²) | 204.1 | 327.6 | 406.7 | 474.7 | — | corr | `pore` |
| max chain COM MSD (Å²) at lag | 211.1 at 12.5 ns | 432.7 at 12.5 ns | 470.1 at 12.5 ns | 627.2 at 12.5 ns | — | n/a | `pore` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.20 | 0.41 | 0.55 | 0.84 | — | n/a | `pore` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.97) | not diffusive (slope 0.97) | not diffusive (slope 0.71) | not diffusive (slope 0.84) | — | n/a | `pore` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached (extrap. 46.4) | not reached (extrap. 39.7) | not reached (extrap. 18.7) | 11.5 | — | n/a | `pore` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached (extrap. 66.8) | not reached (extrap. 45.1) | not reached (extrap. 24.9) | not reached (extrap. 15.1) | — | n/a | `pore` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.181 | 0.128 | 0.110 | 0.109 | — | — | `pore` |
| γ, run monitor (mN/m) | 34.4 ± 0.4 | 31.1 ± 0.3 | 29.5 ± 0.3 | 27.8 ± 0.3 | — | comp | `pore` progress |
| γ, analysis (mN/m) | 34.8 ± 0.4 | 31.4 ± 0.4 | 29.4 ± 0.3 | 27.7 ± 0.5 | — | comp | `pore` |
| dγ/dT (mN m⁻¹ K⁻¹) | — | — | — | — | cooling branch 25–201.6 °C: -0.0436 ± 0.0077 (χ²<sub>red</sub> 2.42); heating sweep 25–160 °C: -0.0459 ± 0.0057 (χ²<sub>red</sub> 2.86) | comp | `pore` |
| γ at 25 °C from the dγ/dT fit (mN/m) | — | — | — | — | cooling branch: 33.35; heating sweep: 33.97 | comp | `pore` |
| e<sub>s</sub>, surface excess energy (mJ/m²) | 56.9 ± 1.1 | 56.7 ± 0.6 | 55.7 ± 0.6 | 54.7 ± 0.5 | — | — | `pore` |
| film thickness between the Gibbs surfaces (Å) | 64.79 ± 0.02 | 65.83 ± 0.03 | 66.47 ± 0.02 | 66.95 ± 0.03 | — | trend | `pore` |
| gap between the Gibbs surfaces (Å) | 50.09 | 49.05 | 48.41 | 47.93 | — | trend | `pore` |
| film interior density (g/cm³) | 0.8357 ± 0.0003 | 0.7983 ± 0.0004 | 0.7758 ± 0.0003 | 0.7595 ± 0.0003 | — | trend | `pore` |
| interfacial width, 10–90 % (Å) | 6.05 | 7.45 | 8.08 | 8.49 | — | trend | `pore` |
| closest approach across the gap (Å) | 43.4 | 40.8 | 38.9 | 37.7 | — | trend | `pore` |
| film α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 7.090; 25–90 °C: 7.095; 90–160 °C: 7.065 | — | `pore` |
| α<sub>z</sub>, film-thickness expansion (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 2.444 ± 0.045 (χ²<sub>red</sub> 1.88); 25–90 °C: 2.456 ± 0.093 (χ²<sub>red</sub> 1.36); 90–160 °C: 2.378 ± 0.139 (χ²<sub>red</sub> 2.67) | — | `pore` |
| C<sub>v</sub> of the film, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 0.834 ± 0.005 (χ²<sub>red</sub> 15.6); 25–90 °C: 0.856 ± 0.006 (χ²<sub>red</sub> 3.18); 90–160 °C: 0.810 ± 0.004 (χ²<sub>red</sub> 2.9) | — | `pore` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field `sdk_cg`, box density 0.4286 g/cm³ (as built)
- Pore: narrow pore, nominal 5 nm, 4.68 nm at 500 K, wall 6.49 nm, clear gap 3.50 nm, area 45.4 nm²
- Built from: `pe_cg_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **pore** (rdyu-rog): finished; started 2026-10-27 22:41 UTC, ended 2026-10-28 20:10 UTC; reads `systems/pe_cg_pore_w5nm_n40_c240_s1/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 34.4 ± 0.4; 90 °C 31.1 ± 0.3; 130 °C 29.5 ± 0.3; 160 °C 27.8 ± 0.3
- Superseded (not used): `pore_old_20ns_box_cancelled` (cancelled/killed?)

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.68 nm | 6.5 nm | 6.4 × 6.4 nm (25 °C) | 25 °C 34.4 ± 0.4; 90 °C 31.1 ± 0.3; 130 °C 29.5 ± 0.3; 160 °C 27.8 ± 0.3 | finished: pore | pore |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`pore` analysis**

Pore analysis (`sepsim analyze pore`, generated 2026-11-09 19:02 UTC on rdyu-server):

- dγ/dT, cooling-branch fit (mN m⁻¹ K⁻¹): -0.04361
- γ at 25 °C, cooling-branch fit (mN/m): 33.35
- dγ/dT, heating-sweep fit (mN m⁻¹ K⁻¹): -0.04593
- γ at 25 °C, heating-sweep fit (mN/m): 33.97
- analysis node: rdyu-server
- nominal gap width (nm): 5
- wall (film) thickness (Å): 64.87

Convergence of the film quantities, per segment:

| γ (mN/m) | segment end (ps) | gap between the Gibbs surfaces (Å) | film interior density (g/cm³) |
|---|---|---|---|
| 22.45 ± 0.9947 | 2000 | — | — |
| 25.13 ± 0.7263 | 7000 | — | — |
| 26.01 ± 1.142 | 1.2e+04 | — | — |
| 28.25 ± 0.8884 | 1.7e+04 | — | — |
| 30.88 ± 0.8475 | 2.2e+04 | — | — |
| 30.42 ± 0.8187 | 2.7e+04 | — | — |
| 30.37 ± 1.047 | 3.2e+04 | — | — |
| 30.68 ± 0.6895 | 3.7e+04 | — | — |
| 34.6 ± 0.8353 | 4.2e+04 | — | — |
| 34.8 ± 0.392 | 6.7e+04 | 50.08 ± 0.01947 | 0.8357 ± 0.0002516 |
| 31.22 ± 0.8525 | 7.2e+04 | 50.03 ± 0.07868 | 0.8312 ± 0.001004 |
| 30.97 ± 0.8237 | 7.7e+04 | 49.91 ± 0.1257 | 0.8257 ± 0.001595 |
| 32.85 ± 0.6149 | 8.2e+04 | 49.53 ± 0.1358 | 0.817 ± 0.001698 |
| 29.81 ± 0.7127 | 8.7e+04 | 49.6 ± 0.1152 | 0.8141 ± 0.001442 |
| 31.65 ± 1.198 | 9.2e+04 | 49.13 ± 0.0902 | 0.8049 ± 0.001101 |
| 31.74 ± 0.6691 | 9.7e+04 | 49.18 ± 0.09695 | 0.8013 ± 0.001184 |
| 32.32 ± 0.7869 | 1.02e+05 | 49.16 ± 0.09992 | 0.7997 ± 0.001215 |
| 31.35 ± 0.3634 | 1.27e+05 | 49.05 ± 0.02965 | 0.7983 ± 0.0003596 |
| 30.39 ± 0.7782 | 1.32e+05 | 48.75 ± 0.1024 | 0.791 ± 0.00123 |
| 29.54 ± 1.41 | 1.37e+05 | 48.66 ± 0.09192 | 0.7862 ± 0.001096 |
| 30.49 ± 0.5967 | 1.42e+05 | 48.3 ± 0.08593 | 0.7783 ± 0.001004 |
| 26.91 ± 0.839 | 1.47e+05 | 48.36 ± 0.109 | 0.7753 ± 0.001269 |
| 29.38 ± 0.3146 | 1.72e+05 | 48.41 ± 0.02362 | 0.7758 ± 0.0002756 |
| 28.21 ± 0.7374 | 1.77e+05 | 48.5 ± 0.131 | 0.773 ± 0.001542 |
| 26.86 ± 0.7429 | 1.82e+05 | 47.97 ± 0.1155 | 0.764 ± 0.001307 |
| 26.64 ± 0.9123 | 1.87e+05 | 48.03 ± 0.1378 | 0.7608 ± 0.001574 |
| 27.73 ± 0.4971 | 2.12e+05 | 47.92 ± 0.02683 | 0.7595 ± 0.0003043 |

Per hold: film vs bulk:

| bulk: max chain COM MSD (Å²) | bulk ρ (g/cm³) | bulk: max segment MSD (Å²) | film: C<sub>n</sub> bond length (Å) | film: C<sub>n</sub> | film: max lag (ps) | film: max chain COM MSD (Å²) | film: chain COM MSD / ⟨R<sub>g</sub>²⟩ at max lag | film: COM MSD log-slope at max lag | film: largest COM MSD log-slope | film: largest ordered cluster, mean (sites) | film: hold length (ns) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 176.9 | 0.8345 ± 8.727e-05 | 815.8 | 1.54 | 11.25 ± 0.3888 | 1.25e+04 | 211.1 | 0.2012 | 0.9678 | 1.887 | 222.7 | 25 |
| 396 | 0.7978 ± 7.309e-05 | 1280 | 1.54 | 11.89 ± 0.1456 | 1.25e+04 | 432.7 | 0.4087 | 0.9676 | 1.899 | 66.86 | 25 |
| 522.8 | 0.7758 ± 0.0001085 | 1602 | 1.54 | 9.091 ± 0.1361 | 1.25e+04 | 470.1 | 0.5497 | 0.7131 | 1.905 | 34.68 | 25 |
| 572.5 | 0.7594 ± 9.246e-05 | 1570 | 1.54 | 7.853 ± 0.1223 | 1.25e+04 | 627.2 | 0.8411 | 0.8435 | 1.909 | 31.88 | 25 |

Per segment:

| γ drift: second − first half (mN/m) | γ, first half (mN/m) | γ, second half (mN/m) | SEM of the γ drift (mN/m) | potential-energy drift: second − first half | box density (g/cm³) | γ (mN/m) | T (°C) | set T (°C) | SEM of γ from 16 blocks (mN/m) | SEM of γ from 32 blocks (mN/m) | SEM of γ from 8 blocks (mN/m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.9598 | 21.98 | 22.94 | 2.02 | 2.651 | 0.4286 ± 0 | 22.45 ± 0.9947 | 227.1 ± 0.2308 | 226.9 | — | — | — |
| -0.6257 | 25.45 | 24.82 | 1.398 | -0.6361 | 0.4337 ± 0 | 25.13 ± 0.7263 | 201.5 ± 0.134 | 201.6 | — | — | — |
| 1.166 | 25.43 | 26.6 | 2.076 | 6.21 | 0.4391 ± 0 | 26.01 ± 1.142 | 176.3 ± 0.1338 | 176.4 | — | — | — |
| 2.043 | 27.22 | 29.26 | 1.505 | -50.26 | 0.4443 ± 0 | 28.25 ± 0.8884 | 151.2 ± 0.1246 | 151.2 | — | — | — |
| 1.968 | 29.9 | 31.87 | 1.3 | -14.02 | 0.4497 ± 0 | 30.88 ± 0.8475 | 126 ± 0.1174 | 125.9 | — | — | — |
| -0.7384 | 30.77 | 30.03 | 1.713 | -3.364 | 0.455 ± 0 | 30.42 ± 0.8187 | 100.7 ± 0.1227 | 100.7 | — | — | — |
| -2.786 | 31.77 | 28.99 | 1.805 | 17.01 | 0.4604 ± 0 | 30.37 ± 1.047 | 75.37 ± 0.1016 | 75.46 | — | — | — |
| -0.3235 | 30.83 | 30.51 | 1.779 | -35.2 | 0.4656 ± 0 | 30.68 ± 0.6895 | 50.1 ± 0.1189 | 50.23 | — | — | — |
| -0.9835 | 35.09 | 34.11 | 1.831 | -13.86 | 0.4715 ± 0 | 34.6 ± 0.8353 | 25.01 ± 0.09525 | 25 | — | — | — |
| -0.2355 | 34.92 | 34.68 | 0.8049 | -36.14 | 0.4713 ± 0 | 34.8 ± 0.392 | 25.01 ± 0.0288 | 25 | 0.3692 | 0.3877 | 0.3797 |
| -0.2695 | 31.36 | 31.09 | 1.553 | 2.585 | 0.4692 ± 0 | 31.22 ± 0.8525 | 35.09 ± 0.08888 | 35 | — | — | — |
| 0.6347 | 30.65 | 31.29 | 1.856 | 12.08 | 0.4669 ± 0 | 30.97 ± 0.8237 | 45.1 ± 0.1146 | 45 | — | — | — |
| 0.4811 | 32.62 | 33.1 | 1.321 | 43.31 | 0.4648 ± 0 | 32.85 ± 0.6149 | 54.89 ± 0.09451 | 55 | — | — | — |
| 0.6537 | 29.47 | 30.13 | 1.59 | -3.954 | 0.4626 ± 0 | 29.81 ± 0.7127 | 65.03 ± 0.1045 | 65 | — | — | — |
| -1.911 | 32.59 | 30.68 | 1.756 | 26.66 | 0.4606 ± 0 | 31.65 ± 1.198 | 75.11 ± 0.1006 | 75 | — | — | — |
| -0.9776 | 32.23 | 31.25 | 1.23 | -14.56 | 0.4583 ± 0 | 31.74 ± 0.6691 | 85.01 ± 0.1033 | 85 | — | — | — |
| -0.4907 | 32.57 | 32.08 | 1.874 | -2.074 | 0.4574 ± 0 | 32.32 ± 0.7869 | 90 ± 0.135 | 90 | — | — | — |
| -0.5424 | 31.62 | 31.08 | 0.7835 | 6.874 | 0.4574 ± 0 | 31.35 ± 0.3634 | 89.98 ± 0.0367 | 90 | 0.3991 | 0.3527 | 0.4154 |
| -0.9834 | 30.87 | 29.88 | 1.452 | 6.223 | 0.4553 ± 0 | 30.39 ± 0.7782 | 99.88 ± 0.1484 | 100 | — | — | — |
| -4.408 | 31.74 | 27.34 | 1.999 | 14.72 | 0.4532 ± 0 | 29.54 ± 1.41 | 109.9 ± 0.1164 | 110 | — | — | — |
| 1.428 | 29.76 | 31.19 | 1.426 | -0.3803 | 0.451 ± 0 | 30.49 ± 0.5967 | 120.2 ± 0.1779 | 120 | — | — | — |
| 1.11 | 26.34 | 27.45 | 1.659 | -6.85 | 0.4489 ± 0 | 26.91 ± 0.839 | 130.1 ± 0.1171 | 130 | — | — | — |
| 0.49 | 29.13 | 29.62 | 0.6433 | -19.36 | 0.4489 ± 0 | 29.38 ± 0.3146 | 130 ± 0.04118 | 130 | 0.3354 | 0.2942 | 0.3991 |
| -0.5579 | 28.5 | 27.94 | 1.803 | -17.77 | 0.4466 ± 0 | 28.21 ± 0.7374 | 140.1 ± 0.1298 | 140 | — | — | — |
| 1.035 | 26.35 | 27.39 | 1.335 | 3.087 | 0.4449 ± 0 | 26.86 ± 0.7429 | 149.9 ± 0.1638 | 150 | — | — | — |
| 2.241 | 25.53 | 27.77 | 1.568 | -2.887 | 0.4426 ± 0 | 26.64 ± 0.9123 | 160 ± 0.1235 | 160 | — | — | — |
| -0.4206 | 27.94 | 27.52 | 0.9022 | 4.176 | 0.4426 ± 0 | 27.73 ± 0.4971 | 159.9 ± 0.04166 | 160 | 0.4081 | 0.3592 | 0.3825 |

- Note: γ uses a plain LJ cutoff without tail correction (D44/D48: `pair_modify tail no`, CG 15 Å, UA/AA 14 Å), so it is cutoff-dependent and lower than a full-dispersion (LJ-PPPM or tail-corrected) value; compare it across our runs, not directly with experiment.
- Note: γ is the mechanical (pressure-tensor) value per surface, (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2] with two film surfaces; the fits are SEM-weighted linear fits in T with errors scaled by √χ²<sub>red</sub> when χ²<sub>red</sub> > 1.
- Note: The slit is a local patch of a pore wall: real separator pores are 30–100 nm and their walls semicrystalline (D50); these walls are amorphous (melt-like or post-shutdown).
- Note: Layers: surface = within 15 Å of either Gibbs surface on the film side (or outside it), interior = the rest, assigned at each time origin; sites leave their layer at long lags, so long-lag layer MSDs mix layers. MSDs are per dimension: in-plane (⟨Δx²⟩+⟨Δy²⟩)/2, normal ⟨Δz²⟩, bulk MSD/3 (isotropic).
- Note: C<sub>v</sub> = dE/dT (total energy, NVT, per gram) and the surface excess energy are classical: C<sub>v</sub> is not comparable to experiment for the same reasons as the bulk C<sub>p</sub> (classical equipartition; UA/CG drop degrees of freedom). e<sub>s</sub> = (E<sub>pore</sub> − (M<sub>pore</sub>/M<sub>bulk</sub>) E<sub>bulk</sub>(T))/(2A) compares the NVT film with the NPT bulk at 1 atm (PV ≈ 0) at the same set T; the film's lateral box follows the bulk density (D48).
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.

</details>

### `pe_cg_pore500k_w10nm_n320_c240_s1_rep222`

PE CG, wide 10 nm slit pore made at 500 K, 320 chains × C240, 25,600 beads; built from `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`). Status: finished: `pore_relax`.

No analysed properties yet. Equilibration: from `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.4176 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: wide pore, nominal 10 nm, wall 13.50 nm, clear gap 1.93 nm, area 182.3 nm²
- Built from: `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`pore_relax`** (rdyu-rog): finished; started 2026-10-29 17:38 UTC, ended 2026-10-29 18:02 UTC; reads `systems/pe_cg_pore500k_w10nm_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| wide | 10 nm (at 500 K) | — | 13.5 nm (500 K) | 13.5 × 13.5 nm (500 K) | — | finished: `pore_relax` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r2nm_160C_n320_c240_s1_rep222`

PE CG, film with a 2 nm-radius cylindrical hole at 160 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`). Status: finished: `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.5254 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free`** (rdyu-server): finished; started 2026-11-02 20:16 UTC, ended 2026-11-05 06:33 UTC; reads `systems/pe_cg_hole_r2nm_160C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_free` | `hole_free` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 133.5
- `free_shell.areal_density_ratio`: 0.8527
- `free_shell.msd.1 ns`: 467.4
- `free_shell.msd.10 ns`: 1602
- `free_shell.msd.end`: 2418
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- T (°C): 160
- `t_close_ns`: 0.035
- `thickness_final`: 134.3
- `thickness_t0`: 149.9

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 134.9 | — |
| 134.8 | — |
| 133.9 | — |
| 134.2 | — |
| 134 | — |
| 134.9 | — |
| 133.9 | — |
| 134.2 | — |
| 134 | — |
| 134 | — |
| 134.2 | — |
| 134.8 | — |
| 134.2 | — |
| 133 | — |
| 134.2 | — |
| 133.8 | — |
| 133.7 | — |
| 134 | — |
| 134.4 | — |
| 134.9 | — |
| 135.2 | — |
| 133.9 | — |
| 134.8 | — |
| 134.5 | — |
| 133.9 | — |
| 134.3 | — |
| 133.4 | — |
| 134.9 | — |
| 134.7 | — |
| 134.3 | — |
| 132.9 | — |
| 134.3 | — |
| 133.6 | — |
| 135 | — |
| 134.2 | — |
| 134.2 | — |
| 134.6 | — |
| 133.8 | — |
| 134.5 | — |
| 134.4 | — |
| 134.9 | — |
| 134.9 | — |
| 135.1 | — |
| 134.6 | — |
| 135.5 | — |
| 134.2 | — |
| 134 | — |
| 134.7 | — |
| 134 | — |
| 134.5 | — |
| 134.9 | — |
| 134.7 | — |
| 134.1 | — |
| 133.4 | — |
| 135.7 | — |
| 135.1 | — |
| 134.9 | — |
| 134.4 | — |
| 134.8 | — |
| 135.2 | — |
| 134.4 | — |
| 135.2 | — |
| 135.3 | — |
| 135.6 | — |
| 135.5 | — |
| 136.1 | — |
| 135.3 | — |
| 135.9 | — |
| 134.7 | — |
| 135.6 | — |
| 136 | — |
| 135.4 | — |
| 136.7 | — |
| 135.8 | — |
| 136.1 | — |
| 136.3 | — |
| 136.6 | — |
| 136.1 | — |
| 137.6 | — |
| 136 | — |
| 136.1 | — |
| 137.2 | — |
| 136.6 | — |
| 136.4 | — |
| 137.6 | — |
| 137.3 | — |
| 137.1 | — |
| 136.7 | — |
| 137.1 | — |
| 136.4 | — |
| 137.3 | — |
| 138.2 | — |
| 137.3 | — |
| 137 | — |
| 137.6 | — |
| 136.4 | — |
| 137.6 | — |
| 137.2 | — |
| 138.7 | — |
| 138 | — |
| 137.8 | — |
| 138.1 | — |
| 137.9 | — |
| 139.6 | — |
| 138.4 | — |
| 138 | — |
| 139.2 | — |
| 138.6 | — |
| 138.5 | — |
| 138.3 | — |
| 138.2 | — |
| 138.6 | — |
| 138.7 | — |
| 138.2 | — |
| 138.3 | — |
| 139.5 | — |
| 138.8 | — |
| 139.5 | — |
| 138.7 | — |
| 139.1 | — |
| 138.9 | — |
| 139 | — |
| 140 | — |
| 140.4 | — |
| 139.8 | — |
| 140.2 | — |
| 139.4 | — |
| 139.9 | — |
| 138.7 | — |
| 140.7 | — |
| 139.9 | — |
| 140.6 | — |
| 140.5 | — |
| 140.6 | — |
| 140.1 | — |
| 141.6 | — |
| 140.6 | — |
| 140.8 | — |
| 141.1 | — |
| 141.8 | — |
| 141.1 | — |
| 141 | — |
| 140.8 | — |
| 141.6 | — |
| 141.5 | — |
| 141.9 | — |
| 142.6 | — |
| 141.8 | — |
| 142.7 | — |
| 142 | — |
| 142.2 | — |
| 142.6 | — |
| 142.8 | — |
| 141.8 | — |
| 143.5 | — |
| 143 | — |
| 143.1 | — |
| 143.3 | — |
| 143.6 | — |
| 142.8 | — |
| 143 | — |
| 143.6 | — |
| 143.6 | — |
| 142.8 | — |
| 144.3 | — |
| 143.4 | — |
| 143.7 | — |
| 143.5 | — |
| 143.3 | — |
| 144.6 | — |
| 145 | — |
| 145.1 | — |
| 144.5 | — |
| 145 | — |
| 144.2 | — |
| 144.3 | — |
| 145.7 | — |
| 146.3 | — |
| 145.4 | — |
| 145 | — |
| 145.5 | — |
| 145.2 | — |
| 145.4 | — |
| 146.6 | — |
| 146.1 | — |
| 145.7 | — |
| 146.1 | — |
| 147.1 | — |
| 146.6 | — |
| 147.2 | — |
| 147.8 | — |
| 146.6 | — |
| 147.9 | — |
| 147.5 | — |
| 146.7 | — |
| 147.5 | — |
| 147.5 | — |
| 147.8 | — |
| 148 | — |
| 148.4 | — |
| 147.9 | — |
| 146.9 | — |
| 147.8 | — |
| 148.7 | — |
| 148.5 | — |
| 149.8 | — |
| 148.4 | — |
| 149.1 | — |
| 148.9 | — |
| 149.3 | — |
| 148.3 | — |
| 149.1 | — |
| 148.9 | — |
| 148.5 | — |
| 148 | — |
| 150 | — |
| 148.5 | — |
| 149.4 | — |
| 148.5 | — |
| 149.7 | — |
| 148.6 | — |
| 149.8 | — |
| 149 | — |
| 150 | — |
| 150 | — |
| 148.6 | — |
| 148.9 | — |
| 149 | — |
| 148.5 | — |
| 148.1 | — |
| 148.3 | — |
| 147 | — |
| 148.2 | — |
| 148.3 | — |
| 148 | — |
| 149 | — |
| 149 | — |
| 148.2 | — |
| 148 | — |
| 147.6 | — |
| 147.9 | — |
| 148.4 | — |
| 149.6 | — |
| 148.9 | — |
| 148.7 | — |
| 149.4 | — |
| 148.4 | — |
| 147 | — |
| 149 | — |
| 149.2 | — |
| 150.4 | — |
| 148.9 | — |
| 150.4 | — |
| 148.3 | — |
| 148.8 | — |
| 148.2 | — |
| 148.8 | — |
| 147.4 | — |
| 149 | — |
| 147.7 | — |
| 148.5 | — |
| 148.4 | — |
| 148.4 | — |
| 149.1 | — |
| 148.8 | — |
| 148.4 | — |
| 147.9 | — |
| 149.4 | — |
| 148.2 | — |
| 147.6 | — |
| 148.5 | — |
| 148.2 | — |
| 149.4 | — |
| 149.1 | — |
| 147.8 | — |
| 149 | — |
| 148 | — |
| 148.5 | — |
| 148.8 | — |
| 149 | — |
| 148.1 | — |
| 149.3 | — |
| 149.4 | — |
| 149.5 | — |
| 148.8 | — |
| 148.5 | — |
| 147.9 | — |
| 148.6 | — |
| 148.8 | — |
| 148.5 | — |
| 148.8 | — |
| 148.7 | — |
| 148.8 | — |
| 149.3 | — |
| 148.6 | — |
| 148.9 | — |
| 149.2 | — |
| 148.9 | — |
| 150.1 | — |
| 150.1 | — |
| 149.1 | — |
| 149.5 | — |
| 150.2 | — |
| 149.7 | — |
| 149.6 | — |
| 148.3 | — |
| 150 | — |
| 148.7 | — |
| 148.3 | — |
| 149.6 | — |
| 148.2 | — |
| 149.4 | — |
| 148.3 | — |
| 148.2 | — |
| 147.6 | — |
| 148.2 | — |
| 149.2 | — |
| 149.5 | — |
| 149.4 | — |
| 150 | — |
| 149.8 | — |
| 150.3 | — |
| 149.1 | — |
| 150.3 | — |
| 149.7 | — |
| 148.5 | — |
| 148.9 | — |
| 149.3 | — |
| 150.4 | — |
| 150.8 | — |
| 149.1 | — |
| 149.3 | — |
| 150.4 | — |
| 150.9 | — |
| 149.3 | — |
| 149.1 | — |
| 148.4 | — |
| 148.9 | — |
| 148.5 | — |
| 149.5 | — |
| 149.1 | — |
| 149.8 | — |
| 149.3 | — |
| 150.1 | — |
| 149.3 | — |
| 150.6 | — |
| 151.1 | — |
| 150 | — |
| 149.9 | — |
| 148.7 | — |
| 148.8 | — |
| 149.7 | — |
| 149.2 | — |
| 149.3 | — |
| 149.8 | — |
| 149.8 | — |
| 148.7 | — |
| 150.5 | — |
| 150 | — |
| 148.9 | — |
| 149.9 | — |
| 149.1 | — |
| 149 | — |
| 149.4 | — |
| 148.7 | — |
| 148.4 | — |
| 150.2 | — |
| 149 | — |
| 148.9 | — |
| 149.2 | — |
| 148.7 | — |
| 149 | — |
| 149 | — |
| 148.9 | — |
| 147.6 | — |
| 149 | — |
| 149.4 | — |
| 149.5 | — |
| 148.8 | — |
| 149 | — |
| 149.5 | — |
| 149.2 | — |
| 148.3 | — |
| 148.8 | — |
| 149.1 | — |
| 149.7 | — |
| 149.6 | — |
| 148.8 | — |
| 149.8 | — |
| 150.4 | — |
| 149.3 | — |
| 149 | — |
| 148.6 | — |
| 149.2 | — |
| 150 | — |
| 150.3 | — |
| 150.8 | — |
| 151 | — |
| 150 | — |
| 148.8 | — |
| 149.9 | 0 |
| 148.9 | 18.32 |
| 148.1 | 32.26 |
| 145.9 | 44.66 |
| 143 | 58.34 |
| 141.5 | 71.6 |
| 141.8 | 84.8 |
| 140.9 | 94.85 |
| 139.9 | 107.4 |
| 139.3 | 119.3 |
| 137 | 127.5 |
| 137 | 136.5 |
| 137.3 | 143.6 |
| 138 | 147.4 |
| 137.4 | 154.1 |
| 136.8 | 161.5 |
| 136.3 | 168.1 |
| 136.6 | 172.8 |
| 136.6 | 175.1 |
| 136.9 | 181.2 |
| 136.3 | 187.7 |
| 136 | 193 |
| 136.2 | 200.4 |
| 136.1 | 203.9 |
| 136.5 | 206.3 |
| 136.3 | 209.7 |
| 136.4 | 211.1 |
| 136.3 | 213.1 |
| 135.9 | 217.3 |
| 135.5 | 222.8 |
| 135.4 | 226.2 |
| 135.9 | 228.8 |
| 136 | 232.4 |
| 135.4 | 236.2 |
| 136.4 | 241.4 |
| 135.4 | 242 |
| 135.6 | 249.1 |
| 135.2 | 247.6 |
| 136.1 | 250 |
| 136.2 | 250.9 |
| 136.5 | 258.2 |
| 136 | 257.3 |
| 135.1 | 258.7 |
| 135 | 263.1 |
| 134.8 | 265.9 |
| 135.7 | 269.2 |
| 135.8 | 267.4 |
| 135.6 | 264.8 |
| 135.9 | 267 |
| 135.2 | 269.8 |
| 135.5 | 271.7 |
| 135.5 | 271.5 |
| 134.6 | 271.6 |
| 135.6 | 278.5 |
| 136.1 | 283.7 |
| 135.4 | 285.4 |
| 135.7 | 285.3 |
| 135.3 | 287.9 |
| 136.4 | 289.3 |
| 136 | 291.4 |
| 135.8 | 295.1 |
| 135.5 | 296.9 |
| 135.3 | 300.7 |
| 135.5 | 304 |
| 136.1 | 307.4 |
| 135.6 | 307.3 |
| 135 | 304.7 |
| 135.7 | 307.8 |
| 135.6 | 304.3 |
| 135.8 | 307.7 |
| 135.1 | 307.2 |
| 135.4 | 307.6 |
| 134.7 | 313.6 |
| 134.2 | 320.9 |
| 135.3 | 320.1 |
| 135.8 | 322.7 |
| 135.8 | 327.8 |
| 134.3 | 330.4 |
| 135.2 | 331.7 |
| 135.5 | 332.4 |
| 134.9 | 335.2 |
| 135.3 | 336.8 |
| 135 | 332 |
| 135.2 | 336.4 |
| 135.3 | 337.7 |
| 135.2 | 337.9 |
| 134.2 | 336.2 |
| 135.5 | 336.6 |
| 134.7 | 339.4 |
| 134.5 | 340.6 |
| 134.2 | 342.9 |
| 133.8 | 344.5 |
| 134.3 | 342.9 |
| 135 | 341.5 |
| 135.5 | 344.8 |
| 135.4 | 351.4 |
| 134.9 | 351.5 |
| 135.2 | 349.9 |
| 135.2 | 353.7 |
| 135.9 | 359.4 |
| 134.9 | 365.9 |
| 135.7 | 368.6 |
| 135.5 | 365 |
| 135.4 | 364.9 |
| 134.8 | 368.3 |
| 135.7 | 368 |
| 135.6 | 368.6 |
| 135.4 | 367.5 |
| 135.4 | 367.2 |
| 135.4 | 367 |
| 135.7 | 366.7 |
| 135.5 | 369 |
| 135 | 372.3 |
| 135.1 | 375.6 |
| 135.9 | 376.8 |
| 135.7 | 375.7 |
| 135.1 | 378.6 |
| 134.8 | 379.3 |
| 134.7 | 379.9 |
| 135.6 | 385.1 |
| 135 | 384.5 |
| 134.8 | 388.8 |
| 134.8 | 394.1 |
| 135 | 391.4 |
| 135 | 392.3 |
| 134.7 | 389.4 |
| 134.5 | 391.6 |
| 134.6 | 396.7 |
| 134.7 | 395.2 |
| 134.9 | 391.2 |
| 134.5 | 397.6 |
| 134.4 | 396.7 |
| 135.5 | 394.6 |
| 134.9 | 395.8 |
| 134.9 | 395.1 |
| 134.9 | 398.8 |
| 134.1 | 397.4 |
| 134.7 | 398.5 |
| 134.8 | 399.1 |
| 134.6 | 395.6 |
| 134.3 | 396.4 |
| 134.6 | 399.4 |
| 134.4 | 402.6 |
| 134 | 401.8 |
| 135.1 | 403.3 |
| 134.6 | 404.3 |
| 134.8 | 404.2 |
| 134.7 | 407 |
| 134.9 | 407.9 |
| 134.5 | 414.1 |
| 134.4 | 413 |
| 133.7 | 409 |
| 133.7 | 412.2 |
| 134.7 | 410.8 |
| 134.6 | 415 |
| 134.9 | 413.6 |
| 135.2 | 418.1 |
| 134.5 | 420.3 |
| 134.9 | 418.2 |
| 133.8 | 420 |
| 135.1 | 427.1 |
| 134.5 | 423.4 |
| 134.9 | 428.8 |
| 135 | 435.5 |
| 135.2 | 435.2 |
| 135.1 | 434.9 |
| 134.5 | 438.9 |
| 133.9 | 435.1 |
| 134.8 | 436.4 |
| 134.7 | 437.3 |
| 134.6 | 442.7 |
| 134.8 | 442.9 |
| 134.6 | 448.8 |
| 135.5 | 460.7 |
| 135.4 | 460.3 |
| 134.5 | 464.8 |
| 134.6 | 464.6 |
| 133.9 | 461.3 |
| 134.5 | 465.5 |
| 134.7 | 469.1 |
| 134.6 | 471.8 |
| 134.6 | 470.2 |
| 134.5 | 467.9 |
| 135 | 468.7 |
| 135.1 | 467.4 |
| 134.7 | 472 |
| 134.8 | 469.5 |
| 135 | 472.1 |
| 134.1 | 474.2 |
| 134.3 | 471.4 |
| 134 | 475.6 |
| 134 | 474.6 |
| 134.7 | 469.5 |
| 134.7 | 466.3 |
| 134.5 | 466.4 |
| 134 | 467 |
| 135.1 | 467.4 |
| 134.4 | 468.6 |
| 134.2 | 468.8 |
| 133.6 | 465.1 |
| 134.6 | 467.4 |
| 134.6 | 462.2 |
| 134.9 | 465.1 |
| 134.7 | 467.3 |
| 135.3 | 463.9 |
| 134.8 | 470.3 |
| 133.8 | 473.9 |
| 133.7 | 474 |
| 134 | 472.8 |
| 134.6 | 479.2 |
| 135.1 | 480.1 |
| 134.7 | 484.3 |
| 135.3 | 481.9 |
| 133.8 | 483.7 |
| 133.7 | 486 |
| 133.7 | 489.7 |
| 134.3 | 492.1 |
| 135 | 490.7 |
| 134.8 | 493.9 |
| 134.8 | 491.5 |
| 134.7 | 495.4 |
| 134.7 | 492.5 |
| 134.8 | 495.6 |
| 134.8 | 497.9 |
| 133.6 | 501.7 |
| 133.1 | 502.6 |
| 134.1 | 502 |
| 134.5 | 503 |
| 134.5 | 504.1 |
| 133.9 | 502.9 |
| 134.4 | 506.1 |
| 134.8 | 502.5 |
| 135.1 | 509.5 |
| 134.3 | 511.9 |
| 134.3 | 512.1 |
| 133.7 | 512.9 |
| 133.7 | 509.4 |
| 134.1 | 514 |
| 135.2 | 517.3 |
| 135.4 | 518 |
| 134.4 | 516.3 |
| 134.7 | 522.2 |
| 135.1 | 522.2 |
| 134.8 | 524.9 |
| 135 | 523.8 |
| 134.9 | 525.9 |
| 135 | 525.3 |
| 134.9 | 524.8 |
| 134.9 | 522.6 |
| 134.5 | 519.5 |
| 134.7 | 521.9 |
| 134 | 520 |
| 134.2 | 521.9 |
| 134.2 | 518 |
| 134.8 | 520.9 |
| 134.5 | 522.3 |
| 133.9 | 525.9 |
| 134.8 | 526.3 |
| 134.3 | 519.8 |
| 134.8 | 518.8 |
| 134.8 | 518.8 |
| 134.6 | 522.7 |
| 134.5 | 528.3 |
| 134.9 | 529.9 |
| 134.2 | 528.7 |
| 134.4 | 529.7 |
| 134.4 | 530 |
| 134.5 | 535.8 |
| 135 | 534.3 |
| 135.3 | 534.3 |
| 135.3 | 542.3 |
| 133.7 | 542 |
| 133.3 | 547.4 |
| 134.3 | 550.2 |
| 134 | 554.3 |
| 135 | 557.9 |
| 135 | 558.7 |
| 134 | 558.1 |
| 134.5 | 560.7 |
| 134 | 562.3 |
| 134.4 | 566.2 |
| 134.5 | 560 |
| 134.1 | 560.7 |
| 134.1 | 564.1 |
| 134.8 | 566.6 |
| 133.6 | 562.7 |
| 133.9 | 563 |
| 134 | 557.6 |
| 135.1 | 556.7 |
| 134.6 | 554.3 |
| 133.6 | 553.7 |
| 133.3 | 554.5 |
| 133.9 | 554.6 |
| 134 | 556.6 |
| 134.6 | 556.8 |
| 135.1 | 557.6 |
| 134.3 | 559.1 |
| 134.8 | 563.6 |
| 134.5 | 566.3 |
| 134.9 | 565.1 |
| 134 | 569.9 |
| 135 | 574.3 |
| 135.2 | 571.4 |
| 135 | 571.7 |
| 135.3 | 580 |
| 134.6 | 581.3 |
| 133.7 | 582.1 |
| 133.3 | 586.8 |
| 133.3 | 588.7 |
| 134.2 | 588.5 |
| 134.8 | 597.6 |
| 134.3 | 600.9 |
| 134.7 | 602.6 |
| 134.4 | 609.9 |
| 133.9 | 613.3 |
| 134.9 | 609 |
| 134 | 607.7 |
| 134.7 | 603 |
| 134.6 | 597.4 |
| 135.6 | 591.9 |
| 135 | 591.6 |
| 134.4 | 590.6 |
| 134.7 | 593.1 |
| 134.5 | 593 |
| 133.9 | 597.1 |
| 133.5 | 596.7 |
| 133.4 | 596.9 |
| 133.7 | 602.9 |
| 135.2 | 601.2 |
| 134.9 | 602 |
| 133.5 | 605.9 |
| 133.6 | 603.2 |
| 133.3 | 606 |
| 133.9 | 612.6 |
| 133.5 | 607.7 |
| 133.3 | 610.6 |
| 133.6 | 610.9 |
| 133.5 | 609.8 |
| 133.7 | 608.9 |
| 133.9 | 606.7 |
| 133.5 | 600.4 |
| 133.7 | 602.5 |
| 134.8 | 601.6 |
| 134.8 | 601.2 |
| 133.9 | 597 |
| 133.5 | 593.5 |
| 133.7 | 593.7 |
| 134.6 | 599.6 |
| 134.9 | 601 |
| 134.7 | 599.5 |
| 134.3 | 597.7 |
| 133.7 | 598.2 |
| 133.9 | 599.6 |
| 134.2 | 603.9 |
| 135 | 606.5 |
| 135.6 | 608.4 |
| 134.5 | 608.8 |
| 134.4 | 608.2 |
| 133.9 | 607.3 |
| 133.5 | 608 |
| 133.7 | 616.9 |
| 134.1 | 620.7 |
| 133 | 620.7 |
| 133.7 | 619.9 |
| 134.3 | 620 |
| 134.7 | 627.8 |
| 133.6 | 625.1 |
| 133.9 | 630.6 |
| 134.2 | 633.2 |
| 133.9 | 634 |
| 134.5 | 638.9 |
| 134.4 | 633.7 |
| 134.6 | 627.3 |
| 134 | 624.2 |
| 133.6 | 626.4 |
| 134 | 621.4 |
| 134 | 623.2 |
| 134 | 625.6 |
| 133.9 | 622.8 |
| 133.9 | 625 |
| 134.4 | 629.8 |
| 134.2 | 626.8 |
| 134.1 | 626.7 |
| 133.9 | 631 |
| 133.6 | 634.7 |
| 134 | 644.5 |
| 134.1 | 641.3 |
| 134 | 640.4 |
| 134.4 | 642.5 |
| 134.3 | 642.1 |
| 133.8 | 641.9 |
| 134.1 | 647.2 |
| 134.9 | 647.7 |
| 134.2 | 641.9 |
| 134.1 | 640.1 |
| 134.2 | 642.9 |
| 134.6 | 641 |
| 134.5 | 640.5 |
| 134 | 642.8 |
| 133.9 | 645.2 |
| 134.8 | 648 |
| 134.7 | 657.6 |
| 134 | 655.9 |
| 135.5 | 660.3 |
| 134.3 | 680.2 |
| 135.1 | 683 |
| 134.4 | 700.9 |
| 133.6 | 714.6 |
| 134.7 | 725 |
| 135 | 736.8 |
| 133.7 | 738.2 |
| 133.3 | 750.4 |
| 134.4 | 751.8 |
| 134.3 | 756.2 |
| 134.5 | 742.2 |
| 133.6 | 730.2 |
| 134.1 | 747 |
| 133.8 | 757.3 |
| 133.3 | 772.1 |
| 133.6 | 785.4 |
| 134.1 | 793.6 |
| 133.2 | 802.5 |
| 133.9 | 797.5 |
| 134.4 | 800.9 |
| 134.2 | 820.7 |
| 134 | 783.1 |
| 134.3 | 810.7 |
| 133.9 | 815.6 |
| 133.7 | 836.9 |
| 133.3 | 842 |
| 133.5 | 830.9 |
| 134.3 | 842 |
| 133.6 | 851.7 |
| 133.7 | 844.3 |
| 132.9 | 876 |
| 132.2 | 907.5 |
| 132.7 | 917.3 |
| 133.8 | 905.4 |
| 133.3 | 888.8 |
| 133.7 | 889.7 |
| 133.7 | 916.2 |
| 133 | 936 |
| 133.2 | 944 |
| 133.8 | 973.3 |
| 134.2 | 966 |
| 133.4 | 993.7 |
| 134.3 | 996.5 |
| 133.4 | 1036 |
| 133.4 | 1041 |
| 133.7 | 1024 |
| 133.2 | 1015 |
| 133.4 | 1011 |
| 133 | 1041 |
| 132.7 | 1029 |
| 133.8 | 1035 |
| 132.8 | 1015 |
| 132.7 | 1043 |
| 133.7 | 1042 |
| 133.3 | 1052 |
| 134.3 | 1030 |
| 134.3 | 1044 |
| 133.6 | 1051 |
| 133.9 | 1057 |
| 135.1 | 1077 |
| 133.8 | 1079 |
| 134.1 | 1098 |
| 133.8 | 1111 |
| 132.9 | 1114 |
| 132.9 | 1115 |
| 133.2 | 1098 |
| 134.2 | 1108 |
| 133.8 | 1112 |
| 133.8 | 1125 |
| 134.1 | 1124 |
| 135.2 | 1154 |
| 134.2 | 1163 |
| 134.6 | 1190 |
| 134 | 1198 |
| 134.6 | 1182 |
| 133.5 | 1190 |
| 135.3 | 1201 |
| 133.7 | 1199 |
| 134.3 | 1204 |
| 133.7 | 1204 |
| 134.3 | 1194 |
| 134.5 | 1213 |
| 134.5 | 1218 |
| 134 | 1254 |
| 134.1 | 1269 |
| 134.4 | 1250 |
| 134.6 | 1258 |
| 134.2 | 1273 |
| 134.6 | 1284 |
| 133.4 | 1276 |
| 133.7 | 1293 |
| 133.7 | 1309 |
| 133.8 | 1298 |
| 134.2 | 1293 |
| 134.1 | 1311 |
| 134.8 | 1349 |
| 134.1 | 1370 |
| 134.8 | 1372 |
| 134.2 | 1349 |
| 133.6 | 1333 |
| 134.1 | 1333 |
| 134.2 | 1349 |
| 134.4 | 1341 |
| 133.8 | 1353 |
| 134.5 | 1331 |
| 134.2 | 1307 |
| 134.4 | 1334 |
| 135.2 | 1382 |
| 133.8 | 1406 |
| 134.8 | 1414 |
| 134.5 | 1416 |
| 133.5 | 1447 |
| 133.9 | 1462 |
| 134.7 | 1467 |
| 133.6 | 1452 |
| 133.3 | 1468 |
| 134.9 | 1459 |
| 133.1 | 1453 |
| 133.6 | 1430 |
| 134.4 | 1448 |
| 134.6 | 1470 |
| 134 | 1471 |
| 134.2 | 1458 |
| 132.6 | 1465 |
| 133.9 | 1466 |
| 132.8 | 1492 |
| 133.7 | 1523 |
| 134.4 | 1506 |
| 134.4 | 1527 |
| 133.7 | 1548 |
| 134.3 | 1546 |
| 133.5 | 1567 |
| 133.7 | 1562 |
| 133.8 | 1540 |
| 134.2 | 1556 |
| 133.6 | 1568 |
| 133.5 | 1551 |
| 134.2 | 1565 |
| 134 | 1566 |
| 134 | 1596 |
| 134.3 | 1582 |
| 133.7 | 1580 |
| 134.1 | 1559 |
| 134 | 1549 |
| 134.6 | 1575 |
| 133.1 | 1596 |
| 134.2 | 1607 |
| 133.4 | 1621 |
| 133.5 | 1613 |
| 134 | 1588 |
| 133.5 | 1624 |
| 133.4 | 1615 |
| 133.6 | 1618 |
| 133.6 | 1640 |
| 133.4 | 1655 |
| 134.5 | 1615 |
| 134.2 | 1602 |
| 133.8 | 1612 |
| 133.9 | 1613 |
| 134.4 | 1607 |
| 133.9 | 1620 |
| 134.4 | 1626 |
| 133.6 | 1630 |
| 134.3 | 1630 |
| 134.3 | 1661 |
| 134.6 | 1637 |
| 134.1 | 1617 |
| 133.2 | 1644 |
| 133.8 | 1661 |
| 133.9 | 1669 |
| 133.7 | 1673 |
| 134.5 | 1664 |
| 134.5 | 1684 |
| 133.4 | 1671 |
| 134.1 | 1675 |
| 133.7 | 1686 |
| 134.8 | 1670 |
| 134.1 | 1680 |
| 134.5 | 1670 |
| 133.7 | 1665 |
| 134.6 | 1664 |
| 133.5 | 1676 |
| 133.3 | 1694 |
| 134.1 | 1675 |
| 134.4 | 1694 |
| 133.2 | 1687 |
| 134.7 | 1702 |
| 133.9 | 1670 |
| 134.2 | 1689 |
| 134.7 | 1674 |
| 133.5 | 1700 |
| 134.3 | 1684 |
| 133.9 | 1681 |
| 133.7 | 1696 |
| 134.1 | 1735 |
| 134.1 | 1734 |
| 134 | 1767 |
| 133.4 | 1749 |
| 134.1 | 1764 |
| 133.9 | 1780 |
| 134.5 | 1805 |
| 134.3 | 1791 |
| 134.3 | 1806 |
| 134.3 | 1795 |
| 134.3 | 1805 |
| 133.4 | 1822 |
| 133.9 | 1844 |
| 133.9 | 1832 |
| 133.2 | 1825 |
| 134.4 | 1809 |
| 134.3 | 1807 |
| 133.7 | 1828 |
| 134.8 | 1853 |
| 134.5 | 1881 |
| 134.6 | 1868 |
| 134.4 | 1875 |
| 133.1 | 1889 |
| 133.7 | 1895 |
| 133 | 1895 |
| 134 | 1913 |
| 134 | 1923 |
| 134.8 | 1920 |
| 134.2 | 1906 |
| 133.2 | 1933 |
| 134.5 | 1919 |
| 133.7 | 1934 |
| 133.6 | 1921 |
| 134.6 | 1939 |
| 133.5 | 1925 |
| 133.6 | 1917 |
| 133.9 | 1912 |
| 134.6 | 1933 |
| 134 | 1921 |
| 133.4 | 1918 |
| 133.8 | 1899 |
| 133.8 | 1922 |
| 133.9 | 1918 |
| 134.6 | 1925 |
| 133.2 | 1927 |
| 133.6 | 1927 |
| 135 | 1923 |
| 133.4 | 1923 |
| 133.7 | 1930 |
| 134.7 | 1973 |
| 134.5 | 1966 |
| 134.2 | 1951 |
| 133.7 | 1976 |
| 133.9 | 1957 |
| 133.9 | 1942 |
| 135.3 | 1973 |
| 133.4 | 1997 |
| 134.3 | 1982 |
| 133.9 | 1998 |
| 134.2 | 1995 |
| 134.3 | 1990 |
| 133.6 | 2020 |
| 133.9 | 2017 |
| 134 | 2034 |
| 133.7 | 2025 |
| 134.1 | 2031 |
| 134 | 2030 |
| 133.6 | 2021 |
| 134 | 2039 |
| 134.3 | 2051 |
| 134.3 | 2050 |
| 134.7 | 2041 |
| 133.9 | 2035 |
| 134.8 | 2060 |
| 134.4 | 2064 |
| 134.6 | 2061 |
| 134.1 | 2052 |
| 133.3 | 2082 |
| 134.3 | 2125 |
| 134.5 | 2126 |
| 133.9 | 2129 |
| 134.2 | 2132 |
| 134.6 | 2133 |
| 134.5 | 2152 |
| 133.4 | 2139 |
| 134.8 | 2138 |
| 133.3 | 2124 |
| 133.4 | 2135 |
| 134.2 | 2119 |
| 134 | 2135 |
| 133.3 | 2137 |
| 134.7 | 2149 |
| 134.4 | 2136 |
| 133.2 | 2144 |
| 134.5 | 2160 |
| 133.5 | 2187 |
| 133.6 | 2194 |
| 135.4 | 2211 |
| 134.1 | 2174 |
| 133.5 | 2167 |
| 133 | 2176 |
| 134.3 | 2196 |
| 133.7 | 2178 |
| 133.3 | 2173 |
| 133.8 | 2177 |
| 133.5 | 2178 |
| 134 | 2168 |
| 134 | 2177 |
| 134.1 | 2195 |
| 133.8 | 2194 |
| 133.7 | 2166 |
| 134.3 | 2176 |
| 133.6 | 2168 |
| 134.3 | 2178 |
| 134 | 2212 |
| 133.4 | 2233 |
| 133.7 | 2219 |
| 133.9 | 2221 |
| 133.2 | 2243 |
| 134 | 2257 |
| 134 | 2249 |
| 134.3 | 2228 |
| 134.1 | 2216 |
| 134 | 2239 |
| 133.7 | 2255 |
| 133.9 | 2256 |
| 133.9 | 2287 |
| 133.5 | 2288 |
| 134.2 | 2288 |
| 133.8 | 2284 |
| 133.9 | 2303 |
| 134.1 | 2301 |
| 133.9 | 2300 |
| 134.4 | 2354 |
| 134.1 | 2353 |
| 134.1 | 2365 |
| 133.4 | 2356 |
| 133.7 | 2363 |
| 134.4 | 2365 |
| 133.1 | 2343 |
| 133.9 | 2352 |
| 135.1 | 2343 |
| 133.6 | 2334 |
| 134 | 2345 |
| 133.5 | 2372 |
| 134.2 | 2368 |
| 134.7 | 2355 |
| 134.5 | 2354 |
| 134.2 | 2360 |
| 133.7 | 2351 |
| 134.1 | 2352 |
| 134.4 | 2346 |
| 135.8 | 2364 |
| 133.9 | 2378 |
| 134.2 | 2413 |
| 134.1 | 2432 |
| 134.6 | 2404 |
| 134.2 | 2388 |
| 134.9 | 2412 |
| 133.9 | 2397 |
| 133.9 | 2408 |
| 134.8 | 2443 |
| 134.3 | 2418 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |


</details>

### `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222`

PE CG, film with a 3 nm-radius cylindrical hole at 130 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_130C.data`). Status: finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free`, `hole_scaf_rel0`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.2904 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_130C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_130C_n320_c240_s1_rep222/data.lmp`
- **`hole_scaf_rel0_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_130C_n320_c240_s1_rep222/data.lmp`
- **`hole_free`** (rdyu-rog): finished; started 2026-11-12 14:02 UTC, ended 2026-11-12 18:20 UTC; reads `systems/pe_cg_hole_r3nm_130C_n320_c240_s1_rep222/data.lmp`
- **`hole_scaf_rel0`** (rdyu-rog): finished; started 2026-11-12 23:27 UTC, ended 2026-11-13 04:34 UTC; reads `systems/pe_cg_hole_r3nm_130C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free`, `hole_scaf_rel0` | `hole_free`, `hole_scaf_rel0` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 132.5
- `free_shell.areal_density_ratio`: 0.8565
- `free_shell.msd.1 ns`: 576.2
- `free_shell.msd.10 ns`: 1517
- `free_shell.msd.end`: 2181
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- T (°C): 130
- `t_close_ns`: 0.12
- `thickness_final`: 133.7
- `thickness_t0`: 166

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 133 | — |
| 133 | — |
| 134 | — |
| 133.1 | — |
| 132.5 | — |
| 132.1 | — |
| 133.5 | — |
| 133.4 | — |
| 133.8 | — |
| 132.7 | — |
| 133.7 | — |
| 133 | — |
| 132.9 | — |
| 132.5 | — |
| 133 | — |
| 133.2 | — |
| 132.2 | — |
| 133.5 | — |
| 132.9 | — |
| 132.5 | — |
| 133.1 | — |
| 132.8 | — |
| 134.1 | — |
| 132.9 | — |
| 133.1 | — |
| 133.9 | — |
| 133.8 | — |
| 133.2 | — |
| 133.2 | — |
| 134.4 | — |
| 134.2 | — |
| 134.6 | — |
| 134.2 | — |
| 134.2 | — |
| 134 | — |
| 134.6 | — |
| 135.1 | — |
| 134.8 | — |
| 133.6 | — |
| 133.9 | — |
| 134.7 | — |
| 134.8 | — |
| 135.2 | — |
| 134.1 | — |
| 134.9 | — |
| 135.9 | — |
| 134.5 | — |
| 135.4 | — |
| 135.6 | — |
| 135.2 | — |
| 135.2 | — |
| 134.5 | — |
| 135.2 | — |
| 134.6 | — |
| 135.5 | — |
| 134.7 | — |
| 135.4 | — |
| 136.3 | — |
| 136.6 | — |
| 136.2 | — |
| 136.4 | — |
| 136.2 | — |
| 136.5 | — |
| 135.8 | — |
| 136 | — |
| 136.6 | — |
| 136.1 | — |
| 136 | — |
| 137.7 | — |
| 136.8 | — |
| 137.6 | — |
| 137 | — |
| 137.8 | — |
| 137.3 | — |
| 137.3 | — |
| 137.2 | — |
| 137.3 | — |
| 138.2 | — |
| 138.6 | — |
| 138.7 | — |
| 138.7 | — |
| 140.3 | — |
| 139.5 | — |
| 138.5 | — |
| 139.1 | — |
| 139.7 | — |
| 139.8 | — |
| 138.9 | — |
| 140.6 | — |
| 140.8 | — |
| 139.4 | — |
| 140.6 | — |
| 140.9 | — |
| 140 | — |
| 140.2 | — |
| 140.8 | — |
| 138.6 | — |
| 140.5 | — |
| 140.7 | — |
| 141.3 | — |
| 141.4 | — |
| 141.4 | — |
| 142.7 | — |
| 142.4 | — |
| 142.6 | — |
| 141.7 | — |
| 143.6 | — |
| 142.5 | — |
| 142.2 | — |
| 141.9 | — |
| 142.8 | — |
| 142.5 | — |
| 144 | — |
| 143.6 | — |
| 143.4 | — |
| 143.8 | — |
| 144.1 | — |
| 143.4 | — |
| 144.7 | — |
| 144.2 | — |
| 142.9 | — |
| 144.4 | — |
| 144.8 | — |
| 145.9 | — |
| 145.6 | — |
| 146 | — |
| 145.1 | — |
| 145.5 | — |
| 145.2 | — |
| 145.5 | — |
| 145.9 | — |
| 147.5 | — |
| 147.5 | — |
| 146.5 | — |
| 147.8 | — |
| 148.3 | — |
| 147.8 | — |
| 148 | — |
| 146.9 | — |
| 148 | — |
| 149.1 | — |
| 149.2 | — |
| 149 | — |
| 149.4 | — |
| 148.7 | — |
| 149.5 | — |
| 148.9 | — |
| 151.1 | — |
| 150.4 | — |
| 149.9 | — |
| 150.6 | — |
| 151.3 | — |
| 151 | — |
| 151.6 | — |
| 152.5 | — |
| 152.5 | — |
| 152.3 | — |
| 151.6 | — |
| 150.7 | — |
| 151.9 | — |
| 153.4 | — |
| 153.6 | — |
| 154.2 | — |
| 153.8 | — |
| 154.2 | — |
| 152.1 | — |
| 153.6 | — |
| 153.9 | — |
| 154.4 | — |
| 155.1 | — |
| 154.7 | — |
| 155.1 | — |
| 154.3 | — |
| 157.1 | — |
| 156.9 | — |
| 157.7 | — |
| 156.9 | — |
| 157.2 | — |
| 157.7 | — |
| 157.2 | — |
| 158 | — |
| 158.5 | — |
| 159.4 | — |
| 159.2 | — |
| 160.3 | — |
| 160.2 | — |
| 160.3 | — |
| 161.5 | — |
| 161.2 | — |
| 162.2 | — |
| 160.8 | — |
| 160.5 | — |
| 162.9 | — |
| 163 | — |
| 163.5 | — |
| 163.9 | — |
| 162.5 | — |
| 164.1 | — |
| 164.4 | — |
| 163.8 | — |
| 164.9 | — |
| 164.6 | — |
| 163.9 | — |
| 165.6 | — |
| 163.5 | — |
| 164.3 | — |
| 163.7 | — |
| 164.8 | — |
| 163.7 | — |
| 166.4 | — |
| 164.7 | — |
| 164 | — |
| 165.3 | — |
| 165.3 | — |
| 166 | — |
| 164.4 | — |
| 166.1 | — |
| 163.9 | — |
| 165 | — |
| 165.1 | — |
| 163.5 | — |
| 164.9 | — |
| 164.5 | — |
| 165 | — |
| 166.1 | — |
| 165.1 | — |
| 166.3 | — |
| 164.4 | — |
| 165.1 | — |
| 164.7 | — |
| 164.3 | — |
| 164.5 | — |
| 164.7 | — |
| 166.1 | — |
| 166.8 | — |
| 167.2 | — |
| 166.6 | — |
| 166.5 | — |
| 166.4 | — |
| 165.8 | — |
| 165.1 | — |
| 164.8 | — |
| 165.1 | — |
| 166 | — |
| 166.1 | — |
| 164.8 | — |
| 166.5 | — |
| 165.6 | — |
| 166.1 | — |
| 166.9 | — |
| 166.3 | — |
| 165.4 | — |
| 166.5 | — |
| 165.4 | — |
| 166.2 | — |
| 166.4 | — |
| 165.6 | — |
| 164.5 | — |
| 166.7 | — |
| 165.9 | — |
| 164.5 | — |
| 165.5 | — |
| 166.1 | — |
| 164.5 | — |
| 165.2 | — |
| 166.6 | — |
| 165.1 | — |
| 164.9 | — |
| 166.2 | — |
| 166.4 | — |
| 165.4 | — |
| 163.6 | — |
| 165.2 | — |
| 165.2 | — |
| 164.4 | — |
| 166.4 | — |
| 164.9 | — |
| 165.9 | — |
| 165.8 | — |
| 165.5 | — |
| 166 | — |
| 166.1 | — |
| 165.8 | — |
| 166.1 | — |
| 165.5 | — |
| 164.2 | — |
| 166.1 | — |
| 165.5 | — |
| 164.4 | — |
| 165.8 | — |
| 164.7 | — |
| 167.1 | — |
| 165.9 | — |
| 166.2 | — |
| 163.9 | — |
| 163.8 | — |
| 165.3 | — |
| 164.8 | — |
| 165.4 | — |
| 165.1 | — |
| 165.6 | — |
| 165.5 | — |
| 165.2 | — |
| 166.2 | — |
| 165.7 | — |
| 164.2 | — |
| 166.3 | — |
| 166.1 | — |
| 165.2 | — |
| 166.5 | — |
| 166.6 | — |
| 165.7 | — |
| 165.9 | — |
| 165.9 | — |
| 164.8 | — |
| 165.5 | — |
| 165.5 | — |
| 167 | — |
| 165.7 | — |
| 166.8 | — |
| 166.8 | — |
| 164.5 | — |
| 165.5 | — |
| 166.4 | — |
| 165.7 | — |
| 166.9 | — |
| 167.7 | — |
| 166.7 | — |
| 165.6 | — |
| 166.2 | — |
| 166.9 | — |
| 167.2 | — |
| 167.7 | — |
| 166.7 | — |
| 167.4 | — |
| 166.8 | — |
| 165.2 | — |
| 167.1 | — |
| 165.9 | — |
| 167.4 | — |
| 166.3 | — |
| 166.6 | — |
| 165.8 | — |
| 166.3 | — |
| 166.9 | — |
| 167 | — |
| 166.7 | — |
| 166.2 | — |
| 166 | — |
| 166.7 | — |
| 167.3 | — |
| 166 | — |
| 167.2 | — |
| 165.9 | — |
| 166.7 | — |
| 167.6 | — |
| 166.8 | — |
| 165.1 | — |
| 167.8 | — |
| 165.4 | — |
| 164.9 | — |
| 165.4 | — |
| 166.1 | — |
| 166.1 | — |
| 165.8 | — |
| 166.1 | — |
| 166.5 | — |
| 165.4 | — |
| 166.3 | — |
| 167.5 | — |
| 166.3 | — |
| 165.7 | — |
| 165.2 | — |
| 165.6 | — |
| 165.6 | — |
| 165.3 | — |
| 166.1 | — |
| 166 | — |
| 165.4 | — |
| 164.4 | — |
| 164.5 | — |
| 165.7 | — |
| 165 | — |
| 166.1 | — |
| 166.3 | — |
| 166.2 | — |
| 165.3 | — |
| 165 | — |
| 166 | — |
| 165.4 | — |
| 168.4 | — |
| 167.1 | — |
| 167.7 | — |
| 166.9 | — |
| 166.3 | — |
| 166.5 | — |
| 166.2 | — |
| 165.2 | — |
| 165.8 | — |
| 167.8 | — |
| 166 | 0 |
| 165.8 | 16.99 |
| 165.9 | 27.38 |
| 164.5 | 37.95 |
| 158.8 | 48.17 |
| 157.6 | 61.8 |
| 155.2 | 74.59 |
| 154.3 | 83.33 |
| 152.7 | 93.81 |
| 152.2 | 102.4 |
| 151.4 | 113.1 |
| 150.1 | 123.5 |
| 148.3 | 134.2 |
| 147.8 | 140.8 |
| 148.2 | 147.4 |
| 147.3 | 154.7 |
| 146.5 | 161.9 |
| 145.9 | 169.2 |
| 145.6 | 177.3 |
| 145.4 | 186.6 |
| 145.3 | 196.3 |
| 144.2 | 203.9 |
| 143.9 | 211.8 |
| 144.3 | 218.5 |
| 143.8 | 224.8 |
| 143.3 | 231.9 |
| 142.9 | 242.8 |
| 141.3 | 250.2 |
| 140.3 | 260.2 |
| 139.7 | 271 |
| 138.3 | 274.4 |
| 138.8 | 276.8 |
| 137.7 | 282 |
| 138.5 | 286 |
| 137.5 | 292.2 |
| 136.6 | 295.7 |
| 137 | 301.1 |
| 136.5 | 304.5 |
| 137 | 303 |
| 137 | 303 |
| 136.4 | 305.2 |
| 136.4 | 309.5 |
| 136.8 | 318.1 |
| 137.3 | 319.6 |
| 137 | 327.3 |
| 137.2 | 332.9 |
| 136.5 | 331.9 |
| 137.5 | 332.6 |
| 137 | 334 |
| 137.1 | 337 |
| 137.3 | 338.6 |
| 137.3 | 341.1 |
| 137.6 | 342.8 |
| 138.1 | 347.1 |
| 136.8 | 351.5 |
| 136.8 | 355.1 |
| 136.4 | 356.5 |
| 136.7 | 362 |
| 136.1 | 366 |
| 135.7 | 368.6 |
| 135.2 | 371.9 |
| 134.8 | 376.3 |
| 135.7 | 382.2 |
| 135.2 | 384.6 |
| 136.1 | 379.4 |
| 135.7 | 380.9 |
| 135.6 | 382.2 |
| 135.9 | 384.7 |
| 135.5 | 388.3 |
| 135.7 | 392.3 |
| 135.6 | 395.6 |
| 134.5 | 398.8 |
| 134.5 | 400.4 |
| 135.6 | 402.5 |
| 136.4 | 408.8 |
| 135.4 | 409.5 |
| 135.3 | 407.2 |
| 135 | 405.3 |
| 135.4 | 408.2 |
| 135.4 | 410.2 |
| 135.2 | 414.1 |
| 134.6 | 416.9 |
| 135.4 | 413.8 |
| 135.1 | 413.8 |
| 135.2 | 417.6 |
| 136.2 | 419.7 |
| 135.6 | 425.8 |
| 136 | 424.7 |
| 135 | 429.1 |
| 135.3 | 432.4 |
| 135.2 | 436.3 |
| 135.8 | 433.7 |
| 135 | 435.6 |
| 135.4 | 441.6 |
| 135.6 | 445.3 |
| 134 | 446.2 |
| 134.8 | 445.7 |
| 135.9 | 442.9 |
| 134.9 | 444.8 |
| 135 | 449 |
| 134.2 | 455.2 |
| 133.9 | 454 |
| 134.7 | 452.3 |
| 135.1 | 449.4 |
| 134.6 | 455.8 |
| 134.8 | 456.1 |
| 134.3 | 456.7 |
| 135 | 454.9 |
| 135.1 | 455.1 |
| 134.1 | 462.2 |
| 133.8 | 467.6 |
| 133.7 | 467.6 |
| 134.1 | 472.8 |
| 135.1 | 472.6 |
| 134.6 | 472.3 |
| 134.1 | 475.5 |
| 133.6 | 477.1 |
| 135.3 | 477.9 |
| 135.5 | 483.8 |
| 135.5 | 482.8 |
| 134.7 | 480.8 |
| 135.2 | 484.8 |
| 134.7 | 486.9 |
| 134.2 | 489.1 |
| 134.1 | 493.1 |
| 134 | 485.9 |
| 135.2 | 487.7 |
| 135.2 | 488.6 |
| 135.1 | 484.9 |
| 134.9 | 489.7 |
| 135 | 490.4 |
| 134.7 | 486.3 |
| 135.3 | 483.8 |
| 134.9 | 488.8 |
| 135.1 | 486.7 |
| 134.7 | 491.5 |
| 135.6 | 490.8 |
| 134.5 | 497.9 |
| 135.3 | 499.5 |
| 134.3 | 502.2 |
| 134.7 | 500.1 |
| 134.9 | 495 |
| 135.4 | 498.5 |
| 135.7 | 499 |
| 135.2 | 503.3 |
| 135.5 | 504.8 |
| 135.3 | 508 |
| 135.3 | 513.2 |
| 134.9 | 513.8 |
| 134.6 | 511.3 |
| 134.1 | 512.9 |
| 134.2 | 517.3 |
| 134.4 | 517.9 |
| 135 | 521.6 |
| 134.5 | 520.6 |
| 134.1 | 523 |
| 133.9 | 521.5 |
| 133.9 | 523 |
| 134.9 | 523 |
| 134.6 | 524.6 |
| 133.9 | 529.6 |
| 133.6 | 529.3 |
| 134 | 524.5 |
| 135 | 524.5 |
| 135.8 | 523 |
| 134.9 | 524.7 |
| 135 | 528.4 |
| 134.9 | 530 |
| 134.8 | 529.2 |
| 134.7 | 531.5 |
| 134.6 | 533.4 |
| 134.5 | 537.3 |
| 134.1 | 541.3 |
| 133.9 | 540.9 |
| 134.1 | 539.9 |
| 134.6 | 543.3 |
| 133.8 | 543.9 |
| 134.6 | 546.5 |
| 135 | 544.2 |
| 134.3 | 548.4 |
| 134.6 | 545.6 |
| 134.2 | 546 |
| 133.6 | 548 |
| 133.7 | 551.7 |
| 134 | 557.9 |
| 134.7 | 555.5 |
| 135.1 | 557.3 |
| 134.6 | 563.6 |
| 134.7 | 563.5 |
| 134.2 | 566.4 |
| 133 | 567 |
| 133.6 | 568.1 |
| 134.3 | 567.7 |
| 134.2 | 566.6 |
| 133.9 | 571 |
| 134.2 | 569.5 |
| 133.9 | 571.7 |
| 134.3 | 572.9 |
| 134.5 | 573.4 |
| 134.3 | 575.2 |
| 134.6 | 576.2 |
| 134 | 581.3 |
| 134.5 | 580.7 |
| 133.6 | 577.8 |
| 133.9 | 578.6 |
| 134.3 | 580.3 |
| 134.6 | 580.7 |
| 134.4 | 582.9 |
| 134 | 583.8 |
| 133.6 | 585.1 |
| 134 | 584.8 |
| 133.5 | 585.1 |
| 134.4 | 585.3 |
| 134.4 | 583.3 |
| 134.1 | 584.5 |
| 133.7 | 587.5 |
| 134.3 | 585.5 |
| 133.9 | 589.9 |
| 134 | 585.6 |
| 134 | 588.5 |
| 134.1 | 586.6 |
| 134.5 | 589.8 |
| 134.7 | 589.1 |
| 134.2 | 585.3 |
| 134.4 | 591 |
| 134.4 | 593.4 |
| 135.3 | 593 |
| 134.2 | 595.1 |
| 134.4 | 601.5 |
| 134.6 | 598.7 |
| 134.6 | 597.6 |
| 134.8 | 599.4 |
| 134.3 | 596.7 |
| 133.7 | 594.4 |
| 134 | 598.3 |
| 135.2 | 602.1 |
| 134.8 | 600.5 |
| 134.2 | 602.3 |
| 134.4 | 607.9 |
| 134.2 | 607.7 |
| 134.3 | 612.7 |
| 133.9 | 613.3 |
| 133.6 | 613.8 |
| 134.8 | 610.1 |
| 134.1 | 607.1 |
| 133.8 | 609.9 |
| 134 | 609.4 |
| 133.7 | 608.9 |
| 133.9 | 613 |
| 135.2 | 613.5 |
| 134.7 | 616.3 |
| 134.3 | 622.9 |
| 133.7 | 626 |
| 134.1 | 628.3 |
| 133.9 | 631.4 |
| 134.1 | 630.1 |
| 133.9 | 630.8 |
| 134.4 | 629.2 |
| 133.9 | 629.5 |
| 134 | 629.2 |
| 134.5 | 626.9 |
| 135.2 | 628.3 |
| 134.4 | 633.6 |
| 134.1 | 634.2 |
| 134.1 | 635.6 |
| 133.8 | 634.4 |
| 134 | 631.9 |
| 134.6 | 634.9 |
| 134.1 | 635.1 |
| 132.9 | 638.9 |
| 133 | 638.4 |
| 133.9 | 643.5 |
| 134.1 | 645.8 |
| 134.5 | 646.8 |
| 133.8 | 648 |
| 133.3 | 647.6 |
| 134.6 | 649.4 |
| 134.7 | 650 |
| 133 | 649.6 |
| 134.1 | 649.4 |
| 133.9 | 654.6 |
| 133.8 | 656.7 |
| 134.1 | 657.7 |
| 135.5 | 662.7 |
| 134.2 | 668.9 |
| 134.5 | 666.7 |
| 134.2 | 666.4 |
| 133.8 | 668.5 |
| 134.3 | 669.9 |
| 133.9 | 669 |
| 134.2 | 665.2 |
| 133.7 | 663.2 |
| 134.2 | 666 |
| 133.2 | 665.5 |
| 133.8 | 666.5 |
| 134.1 | 667.6 |
| 133.7 | 668.8 |
| 133.8 | 666.4 |
| 134.5 | 664.7 |
| 134.9 | 660.8 |
| 133.9 | 659.8 |
| 134.1 | 662 |
| 134.1 | 662.1 |
| 134.5 | 664.7 |
| 134.5 | 662 |
| 134.4 | 664.8 |
| 134.1 | 665.7 |
| 134.5 | 664.1 |
| 134.3 | 662.1 |
| 134.4 | 665.2 |
| 134 | 665.6 |
| 133.5 | 666.2 |
| 133.7 | 664.4 |
| 133.8 | 662 |
| 134.5 | 662.1 |
| 133.7 | 661.1 |
| 134.1 | 660.1 |
| 133.8 | 658.2 |
| 134 | 657.1 |
| 134.6 | 660.9 |
| 133.6 | 664.4 |
| 134.2 | 668.1 |
| 134.8 | 668.8 |
| 134.3 | 674 |
| 134 | 678.1 |
| 133.2 | 680.8 |
| 133.6 | 678.8 |
| 133.8 | 678.9 |
| 133.7 | 675.8 |
| 134 | 679.6 |
| 134.3 | 680 |
| 134 | 673.5 |
| 132.5 | 673.3 |
| 133.3 | 668.7 |
| 133.4 | 668.8 |
| 134.7 | 664.8 |
| 134.2 | 668.6 |
| 134.3 | 667 |
| 132.6 | 663.6 |
| 133.2 | 664.1 |
| 134.2 | 663.7 |
| 134.4 | 660.3 |
| 134.4 | 657.3 |
| 134 | 662.9 |
| 133.6 | 663 |
| 133.5 | 661.2 |
| 134.1 | 658.5 |
| 134 | 665 |
| 133.6 | 665.5 |
| 133.3 | 665.8 |
| 133.6 | 666.3 |
| 133.6 | 667.9 |
| 133.6 | 667.7 |
| 133.7 | 668.3 |
| 134.2 | 670.7 |
| 133.1 | 668.9 |
| 133.5 | 670.7 |
| 133.8 | 674.6 |
| 134 | 672.6 |
| 133.7 | 672.1 |
| 134.1 | 675.3 |
| 134 | 675.3 |
| 133.8 | 675.5 |
| 132.6 | 674 |
| 133.2 | 678.8 |
| 133.7 | 680.5 |
| 133.5 | 678.4 |
| 133.6 | 687.4 |
| 133.1 | 691.8 |
| 133.9 | 690.9 |
| 134.6 | 694.1 |
| 133.7 | 694.4 |
| 133.7 | 697 |
| 133.5 | 704.2 |
| 134 | 700.7 |
| 134.2 | 700.5 |
| 134.2 | 701 |
| 133.7 | 705.4 |
| 133.3 | 708.8 |
| 133.7 | 707.9 |
| 134.2 | 704.6 |
| 134.1 | 704.2 |
| 134.4 | 708.4 |
| 134.2 | 709.7 |
| 133.9 | 712.6 |
| 133.4 | 712.2 |
| 133.7 | 711.1 |
| 133 | 709.6 |
| 133.4 | 711.7 |
| 133.2 | 715.8 |
| 133.4 | 716.1 |
| 133.5 | 718.3 |
| 133.5 | 716.3 |
| 134.2 | 715.9 |
| 133.9 | 724 |
| 134 | 729.7 |
| 134.1 | 731.5 |
| 133.7 | 733.5 |
| 134.3 | 731.9 |
| 134.5 | 735.3 |
| 134.2 | 731.5 |
| 133.1 | 747.9 |
| 133.5 | 762.6 |
| 133.3 | 765.2 |
| 133.7 | 757.1 |
| 133.8 | 764.6 |
| 133.7 | 768.6 |
| 133.4 | 775.5 |
| 133.5 | 791 |
| 133.8 | 791.7 |
| 133.8 | 805 |
| 134.1 | 807.5 |
| 132.8 | 820.9 |
| 132.5 | 834.1 |
| 134.1 | 837 |
| 133.9 | 847.3 |
| 133 | 860 |
| 132.8 | 871.8 |
| 134.2 | 884.4 |
| 133.7 | 907.8 |
| 133.3 | 905.9 |
| 133 | 889.1 |
| 133.7 | 898.2 |
| 133.4 | 911.5 |
| 133.9 | 918.6 |
| 133.5 | 940.3 |
| 133.6 | 962 |
| 133.3 | 964.6 |
| 132 | 974.1 |
| 133.5 | 973 |
| 133.6 | 978 |
| 133.6 | 967.2 |
| 133.1 | 981 |
| 133 | 980.3 |
| 133.4 | 995.2 |
| 133.2 | 1017 |
| 132.5 | 1040 |
| 132.6 | 1052 |
| 132.9 | 1057 |
| 132.6 | 1060 |
| 133.8 | 1050 |
| 134.4 | 1066 |
| 133.8 | 1069 |
| 133.4 | 1085 |
| 133.2 | 1102 |
| 133.4 | 1100 |
| 133.3 | 1091 |
| 132.2 | 1109 |
| 132.7 | 1113 |
| 134 | 1111 |
| 133.3 | 1104 |
| 132.9 | 1103 |
| 133.4 | 1103 |
| 132.5 | 1105 |
| 133.3 | 1109 |
| 133.7 | 1112 |
| 133.6 | 1130 |
| 133.5 | 1106 |
| 132.5 | 1129 |
| 133.5 | 1129 |
| 133.7 | 1122 |
| 133.5 | 1148 |
| 133.5 | 1153 |
| 133.1 | 1172 |
| 132.6 | 1171 |
| 132.8 | 1181 |
| 133.3 | 1158 |
| 132.6 | 1169 |
| 133 | 1196 |
| 133.2 | 1232 |
| 132.6 | 1236 |
| 133.3 | 1243 |
| 133.3 | 1222 |
| 133.2 | 1219 |
| 132.6 | 1228 |
| 132.9 | 1238 |
| 133.4 | 1266 |
| 132.7 | 1260 |
| 133 | 1253 |
| 132.3 | 1265 |
| 133.3 | 1271 |
| 132.3 | 1282 |
| 132.6 | 1304 |
| 133 | 1296 |
| 133 | 1311 |
| 132.5 | 1322 |
| 133.1 | 1324 |
| 132.7 | 1311 |
| 132.3 | 1320 |
| 132.6 | 1331 |
| 132.6 | 1329 |
| 133 | 1342 |
| 133.3 | 1331 |
| 133.4 | 1332 |
| 132.7 | 1335 |
| 133.2 | 1346 |
| 132.7 | 1357 |
| 133.5 | 1350 |
| 131.7 | 1370 |
| 132.7 | 1354 |
| 133.1 | 1371 |
| 133.1 | 1356 |
| 132.5 | 1383 |
| 133.5 | 1394 |
| 132.7 | 1388 |
| 133 | 1408 |
| 132.5 | 1424 |
| 132.8 | 1408 |
| 133.1 | 1412 |
| 133.5 | 1399 |
| 132.8 | 1390 |
| 133.5 | 1393 |
| 133.6 | 1414 |
| 133.5 | 1413 |
| 132.8 | 1403 |
| 132.4 | 1402 |
| 132.3 | 1397 |
| 133.4 | 1402 |
| 133.6 | 1408 |
| 132.5 | 1425 |
| 134 | 1427 |
| 133.5 | 1429 |
| 133.3 | 1419 |
| 133.2 | 1418 |
| 133.3 | 1420 |
| 132.6 | 1436 |
| 133.4 | 1455 |
| 133.2 | 1457 |
| 133.6 | 1458 |
| 133.1 | 1447 |
| 133.6 | 1460 |
| 132.9 | 1462 |
| 132.9 | 1463 |
| 133 | 1482 |
| 133.7 | 1494 |
| 132.8 | 1486 |
| 132.7 | 1490 |
| 133.3 | 1496 |
| 133.5 | 1491 |
| 133.4 | 1519 |
| 133.9 | 1496 |
| 133.4 | 1498 |
| 133.6 | 1523 |
| 133.6 | 1514 |
| 133.6 | 1501 |
| 133.3 | 1495 |
| 132.2 | 1502 |
| 133.4 | 1513 |
| 132.7 | 1519 |
| 133.3 | 1527 |
| 132.5 | 1514 |
| 133.4 | 1509 |
| 133 | 1509 |
| 133.5 | 1516 |
| 132 | 1508 |
| 133.8 | 1534 |
| 133.5 | 1521 |
| 132.7 | 1504 |
| 132.3 | 1508 |
| 132.8 | 1513 |
| 133.7 | 1517 |
| 133.3 | 1512 |
| 132.6 | 1510 |
| 132.6 | 1523 |
| 133 | 1523 |
| 133.2 | 1536 |
| 133.4 | 1536 |
| 133.3 | 1543 |
| 133.1 | 1537 |
| 133.5 | 1530 |
| 133.3 | 1513 |
| 133 | 1525 |
| 133.5 | 1516 |
| 132.9 | 1540 |
| 133 | 1539 |
| 133.4 | 1550 |
| 133.2 | 1532 |
| 133.2 | 1568 |
| 133.3 | 1585 |
| 133.3 | 1575 |
| 133.5 | 1570 |
| 133.3 | 1539 |
| 133.7 | 1553 |
| 132.2 | 1555 |
| 133.4 | 1562 |
| 133.2 | 1579 |
| 133.5 | 1597 |
| 132.9 | 1595 |
| 132.9 | 1616 |
| 133.4 | 1637 |
| 134.2 | 1644 |
| 133.4 | 1673 |
| 133.1 | 1665 |
| 132.6 | 1667 |
| 133.3 | 1681 |
| 133.2 | 1696 |
| 133.1 | 1697 |
| 133.9 | 1697 |
| 133.3 | 1691 |
| 133.8 | 1708 |
| 132.6 | 1697 |
| 133.7 | 1684 |
| 133.7 | 1689 |
| 133 | 1680 |
| 132.9 | 1698 |
| 133.2 | 1733 |
| 133.3 | 1735 |
| 132.8 | 1746 |
| 134.2 | 1771 |
| 134 | 1785 |
| 133.1 | 1781 |
| 133 | 1785 |
| 133 | 1794 |
| 133.2 | 1808 |
| 132.6 | 1802 |
| 132.4 | 1820 |
| 132.3 | 1823 |
| 133.1 | 1838 |
| 133.3 | 1839 |
| 133.1 | 1863 |
| 134 | 1840 |
| 133 | 1820 |
| 132.3 | 1823 |
| 133.6 | 1833 |
| 132.8 | 1802 |
| 133 | 1804 |
| 132.7 | 1816 |
| 133.3 | 1822 |
| 132.9 | 1834 |
| 133.3 | 1848 |
| 133.3 | 1810 |
| 133.6 | 1826 |
| 133.2 | 1834 |
| 132.9 | 1853 |
| 133.1 | 1842 |
| 132.7 | 1870 |
| 132.2 | 1860 |
| 132.5 | 1860 |
| 132.3 | 1854 |
| 133.1 | 1847 |
| 132.8 | 1841 |
| 133.2 | 1867 |
| 133.2 | 1858 |
| 133.2 | 1827 |
| 133.9 | 1828 |
| 132.4 | 1824 |
| 133.1 | 1835 |
| 133.2 | 1834 |
| 132.7 | 1845 |
| 132.9 | 1820 |
| 132.2 | 1831 |
| 131.6 | 1836 |
| 132.8 | 1815 |
| 133.2 | 1836 |
| 133.5 | 1819 |
| 133.3 | 1847 |
| 133.2 | 1847 |
| 133.1 | 1853 |
| 133.4 | 1870 |
| 132.7 | 1859 |
| 133 | 1861 |
| 132.8 | 1838 |
| 133.4 | 1835 |
| 133.9 | 1838 |
| 133.3 | 1847 |
| 133.5 | 1868 |
| 133.8 | 1848 |
| 133.4 | 1850 |
| 133.6 | 1854 |
| 132.5 | 1868 |
| 133 | 1862 |
| 133.2 | 1847 |
| 132.9 | 1854 |
| 132.9 | 1868 |
| 133.1 | 1910 |
| 133.1 | 1902 |
| 132.5 | 1910 |
| 133 | 1922 |
| 132.6 | 1903 |
| 133.2 | 1936 |
| 133 | 1945 |
| 133 | 1954 |
| 133 | 1956 |
| 133.5 | 1960 |
| 133.7 | 1977 |
| 133 | 1948 |
| 133.7 | 1949 |
| 133.5 | 1949 |
| 133.2 | 1967 |
| 133.1 | 1927 |
| 133.9 | 1956 |
| 133.4 | 1982 |
| 133.4 | 1984 |
| 133.5 | 1996 |
| 133.4 | 2004 |
| 133.4 | 2000 |
| 133.5 | 1990 |
| 133.1 | 1987 |
| 133.1 | 1969 |
| 133.4 | 1974 |
| 133 | 1978 |
| 132.6 | 1988 |
| 132.6 | 1991 |
| 132.4 | 1976 |
| 133.1 | 1977 |
| 132.2 | 1974 |
| 132.5 | 1983 |
| 132.9 | 1990 |
| 132.1 | 1982 |
| 133.2 | 1990 |
| 132.2 | 1988 |
| 133 | 2009 |
| 132.7 | 1998 |
| 132.5 | 2019 |
| 133 | 1999 |
| 132.1 | 1990 |
| 133.2 | 1989 |
| 133.4 | 2020 |
| 133.2 | 1996 |
| 132.8 | 2019 |
| 132.6 | 2032 |
| 132.4 | 2043 |
| 133.2 | 2030 |
| 132 | 2036 |
| 133.4 | 2047 |
| 133.6 | 2034 |
| 133.3 | 2043 |
| 133.8 | 2035 |
| 132.8 | 2042 |
| 133.4 | 2036 |
| 132.4 | 2042 |
| 132.9 | 2044 |
| 133.4 | 2037 |
| 133.4 | 2024 |
| 132.5 | 2019 |
| 132.4 | 2029 |
| 133.1 | 2037 |
| 132.7 | 2040 |
| 132.8 | 2032 |
| 131.9 | 2049 |
| 133.7 | 2036 |
| 132.9 | 2027 |
| 133.4 | 2063 |
| 132.5 | 2071 |
| 132.2 | 2082 |
| 133.2 | 2088 |
| 133.4 | 2107 |
| 132.7 | 2114 |
| 132.3 | 2137 |
| 132.7 | 2149 |
| 132.9 | 2149 |
| 133.8 | 2162 |
| 133.3 | 2184 |
| 133.6 | 2158 |
| 133.2 | 2135 |
| 133.3 | 2135 |
| 133.5 | 2155 |
| 132.1 | 2172 |
| 133.6 | 2202 |
| 132.9 | 2193 |
| 133.7 | 2181 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 130 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 130 |


**`hole_scaf_rel0` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 132.5
- `free_shell.areal_density_ratio`: 0.7586
- `free_shell.msd.1 ns`: 543.5
- `free_shell.msd.10 ns`: 1358
- `free_shell.msd.end`: 1951
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: 130
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 1e+04
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `scaffold.d_nm`: 2.5
- `scaffold.nearest_tethered_r_held_min`: 53.65
- `scaffold.nearest_tethered_r_t0`: 55
- `scaffold.tethered_fraction`: 0.5829
- T (°C): 130
- `t_close_ns`: 0.05
- `thickness_final`: 132.5
- `thickness_t0`: 168.8

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 133 | — |
| 133.5 | — |
| 133.1 | — |
| 133 | — |
| 133.3 | — |
| 133 | — |
| 133.2 | — |
| 133.4 | — |
| 133.3 | — |
| 132.8 | — |
| 132 | — |
| 133.5 | — |
| 134.5 | — |
| 133.1 | — |
| 133.6 | — |
| 133.9 | — |
| 133.5 | — |
| 133.8 | — |
| 132.6 | — |
| 133.2 | — |
| 133.1 | — |
| 133.7 | — |
| 133 | — |
| 133.6 | — |
| 134 | — |
| 133.5 | — |
| 133.6 | — |
| 133.7 | — |
| 134.1 | — |
| 133.4 | — |
| 134.4 | — |
| 133.6 | — |
| 132.6 | — |
| 134.1 | — |
| 133.8 | — |
| 134.5 | — |
| 134.2 | — |
| 134 | — |
| 134.5 | — |
| 134.6 | — |
| 133.9 | — |
| 134.2 | — |
| 134.6 | — |
| 134.4 | — |
| 135.1 | — |
| 134.5 | — |
| 135.5 | — |
| 135.4 | — |
| 134.1 | — |
| 135.6 | — |
| 135 | — |
| 135.7 | — |
| 136.3 | — |
| 135.2 | — |
| 134.9 | — |
| 134.7 | — |
| 135.1 | — |
| 134.4 | — |
| 135.2 | — |
| 136.4 | — |
| 136.1 | — |
| 136.9 | — |
| 137.1 | — |
| 136.5 | — |
| 136.6 | — |
| 136.5 | — |
| 136.5 | — |
| 137.4 | — |
| 136.7 | — |
| 136.8 | — |
| 137.4 | — |
| 137.4 | — |
| 137.8 | — |
| 137.6 | — |
| 138.2 | — |
| 137.7 | — |
| 137.6 | — |
| 138.3 | — |
| 138.1 | — |
| 138.5 | — |
| 138.6 | — |
| 140 | — |
| 139.2 | — |
| 139.9 | — |
| 139.6 | — |
| 139.7 | — |
| 139.5 | — |
| 139.8 | — |
| 138.9 | — |
| 139.6 | — |
| 140.1 | — |
| 139.5 | — |
| 139.9 | — |
| 140.8 | — |
| 139.5 | — |
| 140.4 | — |
| 140.7 | — |
| 140.4 | — |
| 141 | — |
| 141 | — |
| 141.6 | — |
| 140.1 | — |
| 141.9 | — |
| 141.5 | — |
| 142.3 | — |
| 141.2 | — |
| 142.3 | — |
| 142.4 | — |
| 142.4 | — |
| 143.1 | — |
| 142.4 | — |
| 142.9 | — |
| 144.4 | — |
| 144.6 | — |
| 143.7 | — |
| 143 | — |
| 143.9 | — |
| 144.8 | — |
| 143.5 | — |
| 145.4 | — |
| 145.1 | — |
| 144.1 | — |
| 145.4 | — |
| 145.6 | — |
| 144.3 | — |
| 146.4 | — |
| 144.8 | — |
| 146.4 | — |
| 145.9 | — |
| 145 | — |
| 146.3 | — |
| 146.1 | — |
| 146.9 | — |
| 147.2 | — |
| 146.7 | — |
| 147.9 | — |
| 147.2 | — |
| 147.9 | — |
| 146.3 | — |
| 147.6 | — |
| 147.3 | — |
| 148.8 | — |
| 149 | — |
| 149.3 | — |
| 147.7 | — |
| 149.8 | — |
| 150.2 | — |
| 151.5 | — |
| 151.3 | — |
| 151.1 | — |
| 151.1 | — |
| 152.1 | — |
| 151.2 | — |
| 150.2 | — |
| 150.8 | — |
| 151.3 | — |
| 151.8 | — |
| 151.3 | — |
| 152.3 | — |
| 152.8 | — |
| 153.4 | — |
| 152.5 | — |
| 153.7 | — |
| 153 | — |
| 154.8 | — |
| 154.7 | — |
| 155.8 | — |
| 154.8 | — |
| 156.3 | — |
| 154.8 | — |
| 157.4 | — |
| 157.3 | — |
| 156.6 | — |
| 157.5 | — |
| 156.4 | — |
| 155.9 | — |
| 156.9 | — |
| 157.2 | — |
| 156.8 | — |
| 157 | — |
| 157.5 | — |
| 158.5 | — |
| 158.2 | — |
| 159.8 | — |
| 160.9 | — |
| 160.4 | — |
| 160.6 | — |
| 160.4 | — |
| 160.6 | — |
| 160.6 | — |
| 161.9 | — |
| 160.7 | — |
| 161.6 | — |
| 162.9 | — |
| 162.8 | — |
| 161.8 | — |
| 162.5 | — |
| 163.9 | — |
| 163.7 | — |
| 164.8 | — |
| 166 | — |
| 165.3 | — |
| 165.1 | — |
| 165.4 | — |
| 165.7 | — |
| 165.5 | — |
| 165.7 | — |
| 165.3 | — |
| 164.9 | — |
| 165.6 | — |
| 165 | — |
| 166 | — |
| 163.2 | — |
| 165.3 | — |
| 165 | — |
| 165.9 | — |
| 165.2 | — |
| 164.1 | — |
| 165.7 | — |
| 164.7 | — |
| 164.7 | — |
| 164.7 | — |
| 165.6 | — |
| 165.1 | — |
| 165.7 | — |
| 165.4 | — |
| 165.3 | — |
| 164.3 | — |
| 164.7 | — |
| 164.6 | — |
| 164.4 | — |
| 164.5 | — |
| 164.7 | — |
| 164.1 | — |
| 165.4 | — |
| 165 | — |
| 165.4 | — |
| 164.5 | — |
| 163.2 | — |
| 163.6 | — |
| 166.2 | — |
| 165.6 | — |
| 165.4 | — |
| 165 | — |
| 165.8 | — |
| 165.7 | — |
| 166.9 | — |
| 165.6 | — |
| 165.5 | — |
| 166.4 | — |
| 166 | — |
| 165 | — |
| 166.1 | — |
| 166.8 | — |
| 164.8 | — |
| 165.1 | — |
| 164.3 | — |
| 166.2 | — |
| 166.7 | — |
| 165.9 | — |
| 165 | — |
| 165.6 | — |
| 164.6 | — |
| 165 | — |
| 165.2 | — |
| 165.9 | — |
| 165.3 | — |
| 166.3 | — |
| 165.8 | — |
| 165.1 | — |
| 165.1 | — |
| 165.7 | — |
| 166.3 | — |
| 164.3 | — |
| 164.7 | — |
| 164.6 | — |
| 164.5 | — |
| 165.2 | — |
| 164.9 | — |
| 166.1 | — |
| 166.6 | — |
| 167.8 | — |
| 165.9 | — |
| 165.9 | — |
| 164.9 | — |
| 165.8 | — |
| 164.5 | — |
| 165.1 | — |
| 166 | — |
| 168.4 | — |
| 166.1 | — |
| 164.8 | — |
| 164.9 | — |
| 165.4 | — |
| 164.9 | — |
| 164.9 | — |
| 165.8 | — |
| 165.8 | — |
| 166.6 | — |
| 165.3 | — |
| 166 | — |
| 166.7 | — |
| 167.3 | — |
| 166.9 | — |
| 167.6 | — |
| 167.5 | — |
| 166.3 | — |
| 166.6 | — |
| 167.2 | — |
| 167.2 | — |
| 165.9 | — |
| 167 | — |
| 166.7 | — |
| 168.4 | — |
| 167.6 | — |
| 167.9 | — |
| 167.1 | — |
| 167.6 | — |
| 168.5 | — |
| 167.9 | — |
| 166.8 | — |
| 168.1 | — |
| 167.7 | — |
| 166.6 | — |
| 167.8 | — |
| 166.6 | — |
| 168.1 | — |
| 168.2 | — |
| 166 | — |
| 166.1 | — |
| 166 | — |
| 167.9 | — |
| 166.9 | — |
| 166.4 | — |
| 166.4 | — |
| 165 | — |
| 167.5 | — |
| 167.1 | — |
| 166.5 | — |
| 164.8 | — |
| 165.9 | — |
| 166 | — |
| 165.9 | — |
| 164.9 | — |
| 166.9 | — |
| 165.8 | — |
| 165.1 | — |
| 166.4 | — |
| 166.2 | — |
| 167.3 | — |
| 167.5 | — |
| 167.7 | — |
| 166.6 | — |
| 166 | — |
| 166.7 | — |
| 166.1 | — |
| 166.6 | — |
| 166.4 | — |
| 164.3 | — |
| 165.4 | — |
| 167 | — |
| 167.2 | — |
| 166.8 | — |
| 165.1 | — |
| 166.6 | — |
| 166.6 | — |
| 167.5 | — |
| 167.3 | — |
| 166.5 | — |
| 167.7 | — |
| 167.6 | — |
| 168.1 | — |
| 167.2 | — |
| 167.7 | — |
| 167.4 | — |
| 168.1 | — |
| 168 | — |
| 167.5 | — |
| 167.3 | — |
| 166.9 | — |
| 166.4 | — |
| 168.1 | — |
| 167.7 | — |
| 166.5 | — |
| 167.3 | — |
| 167.1 | — |
| 167.9 | — |
| 167.8 | — |
| 167.6 | — |
| 167.7 | — |
| 167.1 | — |
| 169.2 | — |
| 166.8 | — |
| 167.2 | — |
| 167 | — |
| 165.9 | — |
| 166.5 | — |
| 167.3 | — |
| 167.6 | — |
| 168.3 | — |
| 169.1 | — |
| 168.6 | — |
| 169.1 | — |
| 169 | — |
| 168.4 | — |
| 169.2 | — |
| 169.2 | — |
| 168.9 | — |
| 168.7 | — |
| 168.9 | — |
| 168.8 | — |
| 169.1 | — |
| 169 | — |
| 168.7 | — |
| 168.9 | — |
| 169.3 | — |
| 168.5 | — |
| 168.8 | — |
| 168.3 | — |
| 169.2 | — |
| 169.1 | — |
| 168.8 | — |
| 169.1 | — |
| 168.9 | — |
| 168.6 | — |
| 168.9 | — |
| 168.7 | — |
| 169 | — |
| 168.8 | — |
| 169.2 | — |
| 168.7 | — |
| 168.9 | — |
| 169 | — |
| 168.6 | — |
| 168.5 | — |
| 169.1 | — |
| 168.4 | — |
| 168.4 | — |
| 168.9 | — |
| 168.6 | — |
| 168.6 | — |
| 169.2 | — |
| 168.6 | — |
| 168.6 | — |
| 168.5 | — |
| 168.9 | — |
| 168.9 | — |
| 169.1 | — |
| 169.3 | — |
| 169 | — |
| 168.6 | — |
| 169.1 | — |
| 168.5 | — |
| 168.6 | — |
| 169 | — |
| 168.7 | — |
| 169.2 | — |
| 169.2 | — |
| 169.1 | — |
| 168.9 | — |
| 169.3 | — |
| 169.3 | — |
| 169.2 | — |
| 169.3 | — |
| 169 | — |
| 169.3 | — |
| 168.8 | — |
| 169.2 | — |
| 168.7 | — |
| 169.4 | — |
| 169.4 | — |
| 168.9 | — |
| 168.4 | — |
| 169.2 | — |
| 168.3 | — |
| 168.7 | — |
| 169.2 | — |
| 169 | — |
| 169.2 | — |
| 168.7 | — |
| 169 | — |
| 169.2 | — |
| 168.7 | — |
| 168.8 | — |
| 168.7 | — |
| 168.8 | — |
| 169.1 | — |
| 168.5 | — |
| 169.5 | — |
| 168.7 | — |
| 168.8 | — |
| 168.7 | — |
| 169 | — |
| 169.2 | — |
| 169.3 | — |
| 169.1 | — |
| 169 | — |
| 169 | — |
| 169.2 | — |
| 169.2 | — |
| 169.4 | — |
| 168.7 | — |
| 169 | — |
| 169 | — |
| 168.9 | — |
| 169.1 | — |
| 168.7 | — |
| 169 | — |
| 169.2 | — |
| 169.5 | — |
| 168.6 | — |
| 168.5 | — |
| 168.9 | — |
| 168.3 | — |
| 168.8 | — |
| 168.8 | — |
| 169.4 | — |
| 168.9 | — |
| 169 | — |
| 168.9 | — |
| 169.4 | — |
| 169 | — |
| 169 | — |
| 169.2 | — |
| 169.2 | — |
| 169.1 | — |
| 168.6 | — |
| 168.5 | — |
| 169.1 | — |
| 168.9 | — |
| 169.1 | — |
| 168.8 | — |
| 168.9 | — |
| 168.8 | — |
| 169.1 | — |
| 168.8 | — |
| 169 | — |
| 169.1 | — |
| 169.1 | — |
| 169 | — |
| 168.6 | — |
| 169.1 | — |
| 169.2 | — |
| 169.1 | — |
| 168.7 | — |
| 168.9 | — |
| 168.8 | — |
| 168.3 | — |
| 169.4 | — |
| 169.2 | — |
| 168.7 | — |
| 169.3 | — |
| 169.1 | — |
| 169 | — |
| 169.2 | — |
| 168.5 | — |
| 169 | — |
| 169.3 | — |
| 169.1 | — |
| 169.2 | — |
| 168.3 | — |
| 168.6 | — |
| 168.8 | — |
| 168.3 | — |
| 168.8 | — |
| 169.1 | — |
| 168.8 | — |
| 169.2 | — |
| 168.9 | — |
| 169.2 | — |
| 169 | — |
| 168.8 | — |
| 168.6 | — |
| 168.7 | — |
| 168.9 | — |
| 169.3 | — |
| 169.1 | — |
| 169.1 | — |
| 169.1 | — |
| 168.6 | — |
| 169 | — |
| 169 | — |
| 169.1 | — |
| 169 | — |
| 169 | — |
| 169.1 | — |
| 169.3 | — |
| 169 | — |
| 169.1 | — |
| 169.3 | — |
| 168.7 | — |
| 169 | — |
| 169.3 | — |
| 168.7 | — |
| 169.2 | — |
| 169.1 | — |
| 169.3 | — |
| 168.6 | — |
| 168.9 | — |
| 169.1 | — |
| 168.8 | 0 |
| 167.8 | 16.54 |
| 165.8 | 28.53 |
| 161.5 | 39.68 |
| 159.8 | 51.56 |
| 156.9 | 64.65 |
| 154.1 | 76.05 |
| 152 | 83.25 |
| 151.3 | 91.1 |
| 150.3 | 101.4 |
| 150 | 112 |
| 149.7 | 120.4 |
| 149.7 | 125.6 |
| 149.5 | 134.3 |
| 148.3 | 145.6 |
| 146.8 | 157.1 |
| 144.9 | 167.7 |
| 144.3 | 173 |
| 142.4 | 176.9 |
| 142.9 | 182.9 |
| 142.4 | 187 |
| 142.6 | 188.6 |
| 142.6 | 196.6 |
| 141.9 | 203.7 |
| 142 | 208.8 |
| 140.8 | 211.8 |
| 140.2 | 215.9 |
| 140.9 | 217.4 |
| 139.9 | 221.1 |
| 140.8 | 225.9 |
| 141 | 226.9 |
| 140.6 | 230 |
| 140.2 | 232 |
| 139.6 | 235.3 |
| 138.4 | 240.6 |
| 139.2 | 245.5 |
| 138.4 | 249.5 |
| 138.1 | 255.9 |
| 137.7 | 258.3 |
| 137.9 | 261.3 |
| 137.5 | 263.9 |
| 137.6 | 268.7 |
| 136.9 | 271.9 |
| 137.1 | 274.9 |
| 138.8 | 281.3 |
| 137.6 | 285.5 |
| 137.6 | 290.4 |
| 136.2 | 293.1 |
| 137.3 | 293.7 |
| 136.8 | 291.7 |
| 137.1 | 294.9 |
| 137.2 | 296 |
| 137.6 | 297.4 |
| 137.8 | 300.7 |
| 136.9 | 305.1 |
| 136.3 | 309.1 |
| 137.6 | 313.4 |
| 136.4 | 319.3 |
| 136.8 | 324.4 |
| 136.1 | 321.5 |
| 136.8 | 328.3 |
| 137.2 | 330.5 |
| 136.8 | 335.1 |
| 136.5 | 337.5 |
| 136.9 | 337.5 |
| 136.6 | 338 |
| 137.3 | 343.3 |
| 136.1 | 345.4 |
| 136.2 | 349.5 |
| 136.4 | 351.9 |
| 135.3 | 353.5 |
| 135.6 | 354.8 |
| 136.2 | 353 |
| 136 | 351.5 |
| 135.7 | 359.2 |
| 135.7 | 362 |
| 135.8 | 364 |
| 136.6 | 365.5 |
| 135.1 | 364.2 |
| 134.5 | 367.9 |
| 135.2 | 369.7 |
| 135.4 | 372.6 |
| 135.9 | 372.2 |
| 135.7 | 378.9 |
| 136.3 | 382.3 |
| 134.9 | 384.1 |
| 135.4 | 386.9 |
| 135.5 | 388.5 |
| 133.8 | 383.9 |
| 135.1 | 387.3 |
| 134.7 | 386.7 |
| 134.6 | 388.1 |
| 135.6 | 390.9 |
| 134.9 | 395 |
| 134.5 | 396.9 |
| 134.9 | 393.8 |
| 134.7 | 396.9 |
| 134.8 | 399.7 |
| 134.5 | 398 |
| 134.6 | 395.9 |
| 134.8 | 395.4 |
| 135.4 | 394.6 |
| 134.5 | 396.8 |
| 134.7 | 397.1 |
| 134.6 | 396.8 |
| 135.5 | 397.8 |
| 134.7 | 397.4 |
| 135.1 | 394.9 |
| 134.5 | 392.8 |
| 135.7 | 395 |
| 135.5 | 397.2 |
| 134.6 | 400 |
| 134.7 | 401.3 |
| 134.7 | 404 |
| 134 | 405.5 |
| 134.5 | 409.9 |
| 134.6 | 414 |
| 135 | 413.5 |
| 134.7 | 413.7 |
| 134.8 | 418.1 |
| 134.9 | 420.4 |
| 135.8 | 421.7 |
| 135.8 | 424.5 |
| 136.1 | 427.1 |
| 135 | 435.8 |
| 134 | 439 |
| 134.4 | 443.5 |
| 134.4 | 444.5 |
| 133.9 | 448.5 |
| 134.2 | 446.3 |
| 134.8 | 443 |
| 134.8 | 439.5 |
| 134.6 | 443.6 |
| 133.7 | 444.2 |
| 133.9 | 445.9 |
| 134.9 | 446.5 |
| 134.3 | 445.8 |
| 133.9 | 447.4 |
| 135.3 | 454 |
| 134 | 456.6 |
| 133.5 | 456.5 |
| 133.4 | 457.4 |
| 135.1 | 462.6 |
| 134.6 | 465.5 |
| 134.6 | 466.1 |
| 133.4 | 471.6 |
| 133.7 | 476.5 |
| 134.9 | 479.6 |
| 134.5 | 476.7 |
| 134.8 | 475.5 |
| 133.6 | 477.8 |
| 133.2 | 479.1 |
| 133.5 | 480.6 |
| 134 | 477.8 |
| 133.3 | 475.8 |
| 133.4 | 478 |
| 133.7 | 478 |
| 134.2 | 481.4 |
| 133.7 | 483.2 |
| 132.7 | 483.9 |
| 132.8 | 488.7 |
| 133.1 | 486.9 |
| 133.1 | 483.3 |
| 133.4 | 479.5 |
| 133.5 | 479.7 |
| 134.2 | 481.4 |
| 133.7 | 486.3 |
| 133.1 | 487.2 |
| 133.5 | 490.9 |
| 133.3 | 491 |
| 134.6 | 495.4 |
| 134.5 | 494.2 |
| 134.7 | 497.3 |
| 135.1 | 499.9 |
| 134.5 | 501.8 |
| 133.4 | 500.9 |
| 133.4 | 501.8 |
| 133.6 | 506.2 |
| 134.2 | 511.5 |
| 133.5 | 508.5 |
| 133.8 | 511.2 |
| 133.3 | 511.1 |
| 134.1 | 509.4 |
| 133.4 | 512.1 |
| 133.5 | 510.6 |
| 133.2 | 512.2 |
| 133.7 | 516.5 |
| 133.8 | 517.2 |
| 133.9 | 520.1 |
| 133.5 | 526.1 |
| 134 | 526 |
| 133.5 | 528.4 |
| 133.7 | 531.1 |
| 133.3 | 536.3 |
| 133.6 | 534.5 |
| 133.6 | 536.1 |
| 133.5 | 532.8 |
| 133.3 | 533.1 |
| 133.3 | 536.9 |
| 133.5 | 540.6 |
| 133.4 | 543.5 |
| 134.1 | 543 |
| 133.8 | 543.9 |
| 133.8 | 541.6 |
| 133.4 | 538.3 |
| 133.4 | 536 |
| 134.1 | 531.8 |
| 134.1 | 530.3 |
| 134 | 531.7 |
| 133.7 | 534 |
| 133.6 | 535.4 |
| 133.7 | 532.1 |
| 134.4 | 531.2 |
| 133.8 | 536.9 |
| 133.1 | 542.6 |
| 133.3 | 543.8 |
| 134.1 | 547.4 |
| 134.1 | 547.9 |
| 133.3 | 550.6 |
| 133.3 | 548.6 |
| 134 | 552.1 |
| 133.4 | 551.1 |
| 134.2 | 548.5 |
| 134.3 | 548.7 |
| 133.4 | 546.5 |
| 133.4 | 548.7 |
| 133.6 | 543.1 |
| 134.2 | 545.8 |
| 134.1 | 548.6 |
| 134.4 | 547.4 |
| 134 | 548.7 |
| 133 | 545.1 |
| 132.9 | 547 |
| 133.8 | 543.5 |
| 133.2 | 545.9 |
| 133.5 | 546.1 |
| 133.8 | 546.6 |
| 132.9 | 546.1 |
| 133.9 | 549 |
| 134.1 | 546.5 |
| 134.2 | 545.8 |
| 134 | 549.6 |
| 133.7 | 549.9 |
| 133.3 | 547 |
| 133.9 | 544.6 |
| 133.9 | 546.3 |
| 133.4 | 544.5 |
| 134.4 | 543.9 |
| 133.9 | 546 |
| 133 | 549 |
| 133.8 | 550.2 |
| 133.7 | 556.1 |
| 133.6 | 557.2 |
| 133.4 | 558.6 |
| 133.3 | 564.4 |
| 133.1 | 565.4 |
| 132.4 | 569.9 |
| 133.4 | 573.1 |
| 133.2 | 572.2 |
| 132.6 | 570.1 |
| 132.7 | 573.5 |
| 133.6 | 571.5 |
| 134 | 570.7 |
| 133.4 | 573.2 |
| 134.2 | 576.4 |
| 133.9 | 575.8 |
| 133.2 | 577.6 |
| 132.9 | 577.4 |
| 132.8 | 580.5 |
| 133.4 | 586.4 |
| 132.6 | 585.6 |
| 132.7 | 589.5 |
| 132.8 | 593.1 |
| 133 | 595.4 |
| 132.9 | 600.8 |
| 133 | 598.8 |
| 132.9 | 605.5 |
| 132.9 | 605.4 |
| 133.2 | 606.5 |
| 133.1 | 606.5 |
| 132.7 | 607.6 |
| 132.5 | 606.3 |
| 133.7 | 607.9 |
| 133.2 | 610.9 |
| 133.3 | 615.6 |
| 132.8 | 619.4 |
| 132.7 | 619.6 |
| 132.9 | 622.7 |
| 132.7 | 625 |
| 132.6 | 628.2 |
| 132.8 | 625.8 |
| 132.3 | 629.9 |
| 132.4 | 628.2 |
| 133.8 | 631.1 |
| 132.7 | 636.2 |
| 132.9 | 635.5 |
| 132.3 | 636.4 |
| 132.4 | 636.9 |
| 131.8 | 638.6 |
| 132.3 | 644.2 |
| 132.6 | 646.8 |
| 133.2 | 646.4 |
| 133.1 | 648.5 |
| 132.6 | 645.7 |
| 132.6 | 643.8 |
| 132.1 | 647.1 |
| 132.7 | 644.2 |
| 132.5 | 642.2 |
| 132.8 | 643.4 |
| 132.7 | 643.6 |
| 132.9 | 645.4 |
| 132.7 | 643.1 |
| 132.4 | 639.4 |
| 132.8 | 642.1 |
| 132.5 | 643.3 |
| 132.7 | 645.7 |
| 132.5 | 647.9 |
| 132.6 | 646.6 |
| 132.3 | 647.6 |
| 133 | 652.4 |
| 133.1 | 656 |
| 132.4 | 658.3 |
| 132.9 | 658 |
| 133.2 | 661.5 |
| 131.6 | 661.1 |
| 132.1 | 663.7 |
| 132.2 | 663.2 |
| 132 | 658.2 |
| 132.2 | 654.6 |
| 132.6 | 653.6 |
| 132 | 652.4 |
| 132.4 | 654.3 |
| 133 | 649 |
| 132.8 | 653.1 |
| 132.8 | 654.4 |
| 133.3 | 658.1 |
| 133.1 | 658.9 |
| 133.2 | 654.4 |
| 133.1 | 657.7 |
| 132.8 | 656.3 |
| 132.8 | 653 |
| 132.4 | 654.7 |
| 132.8 | 656.7 |
| 132 | 657.3 |
| 132.3 | 659.7 |
| 133 | 658.3 |
| 133.3 | 665.4 |
| 132.8 | 660.6 |
| 132 | 663.2 |
| 132.6 | 672.2 |
| 132.4 | 674 |
| 132.3 | 677.7 |
| 132.4 | 678 |
| 132.1 | 678.3 |
| 133.2 | 677.2 |
| 132.9 | 675.6 |
| 132.7 | 679.8 |
| 132 | 683.2 |
| 132.9 | 683.6 |
| 132.7 | 680.3 |
| 132.6 | 677 |
| 132 | 678.1 |
| 132.1 | 672.5 |
| 132.8 | 669.3 |
| 132.3 | 669.3 |
| 133.1 | 667.7 |
| 133 | 667 |
| 133 | 667.6 |
| 133.4 | 668.3 |
| 133.3 | 666.9 |
| 132.5 | 668 |
| 134 | 669.4 |
| 133.2 | 671.4 |
| 132.8 | 671.4 |
| 132.5 | 676.9 |
| 133.2 | 676 |
| 133.3 | 682.7 |
| 133 | 686 |
| 133.3 | 691.3 |
| 133 | 694.1 |
| 132.8 | 697 |
| 132.5 | 692.9 |
| 133.3 | 693.1 |
| 132.9 | 694.1 |
| 133.5 | 700.4 |
| 133.1 | 700.9 |
| 133.1 | 700.8 |
| 132.8 | 698.8 |
| 132.5 | 699.3 |
| 133 | 697.6 |
| 132.2 | 700.7 |
| 132.8 | 704.7 |
| 132.7 | 705.5 |
| 133.3 | 704.5 |
| 132.9 | 701 |
| 133 | 701.8 |
| 133.8 | 708.2 |
| 133.3 | 709.5 |
| 133.7 | 710.1 |
| 133.6 | 706.8 |
| 133.7 | 706.5 |
| 133.2 | 691.5 |
| 132.9 | 702.2 |
| 133.6 | 706 |
| 132.8 | 715.6 |
| 133.6 | 719.3 |
| 132.8 | 734.2 |
| 132.8 | 746.6 |
| 132.8 | 755.7 |
| 133.3 | 744.3 |
| 133 | 756.1 |
| 133.2 | 743.8 |
| 133.8 | 763 |
| 133.6 | 757.8 |
| 132.7 | 763.3 |
| 133.9 | 765.5 |
| 134.2 | 778.4 |
| 134.1 | 778.2 |
| 133.5 | 780.2 |
| 133.4 | 778.4 |
| 132.7 | 789.7 |
| 133.9 | 800.2 |
| 133.8 | 808.9 |
| 133.7 | 827.1 |
| 132.9 | 819.8 |
| 133.1 | 823.7 |
| 132.9 | 819.5 |
| 133.8 | 828.6 |
| 133.8 | 838.4 |
| 133.7 | 812.6 |
| 133.2 | 822.5 |
| 133.5 | 831.3 |
| 133.3 | 839.2 |
| 133.4 | 867.7 |
| 133.6 | 876.8 |
| 132.4 | 872.2 |
| 133 | 883.9 |
| 132.8 | 905.7 |
| 133.2 | 893 |
| 133.3 | 891.1 |
| 132.8 | 911 |
| 133.8 | 918.5 |
| 132.3 | 916.4 |
| 132.5 | 919.3 |
| 132.9 | 929.3 |
| 132.8 | 938.1 |
| 133.4 | 938 |
| 133 | 942 |
| 132.2 | 954.9 |
| 133.7 | 962.8 |
| 132.9 | 954.3 |
| 133.3 | 968.5 |
| 132.5 | 961.2 |
| 132.7 | 978.7 |
| 132.6 | 969.2 |
| 132.2 | 975.7 |
| 132 | 982.2 |
| 132.5 | 992.4 |
| 133.2 | 1012 |
| 132.9 | 1023 |
| 132.5 | 1013 |
| 132.4 | 980.4 |
| 132.6 | 993.8 |
| 132.8 | 1035 |
| 133.2 | 1026 |
| 132.4 | 1030 |
| 132 | 1048 |
| 133.1 | 1041 |
| 132.2 | 1053 |
| 132.1 | 1062 |
| 132.9 | 1048 |
| 132.5 | 1058 |
| 133.2 | 1048 |
| 132.2 | 1064 |
| 132.7 | 1061 |
| 132.7 | 1064 |
| 132.3 | 1063 |
| 133.7 | 1072 |
| 132.7 | 1097 |
| 132.2 | 1102 |
| 132.8 | 1110 |
| 132.3 | 1113 |
| 132.2 | 1117 |
| 131.5 | 1110 |
| 133.1 | 1113 |
| 133.7 | 1120 |
| 132.5 | 1133 |
| 132.8 | 1133 |
| 133 | 1112 |
| 133.4 | 1124 |
| 132.9 | 1144 |
| 132.6 | 1161 |
| 132.3 | 1161 |
| 133.9 | 1159 |
| 132.9 | 1170 |
| 134 | 1194 |
| 132.8 | 1198 |
| 133.3 | 1200 |
| 133.2 | 1208 |
| 133.1 | 1207 |
| 132.9 | 1223 |
| 133.4 | 1217 |
| 132.6 | 1234 |
| 133.4 | 1232 |
| 133.7 | 1248 |
| 132.8 | 1245 |
| 133.1 | 1233 |
| 132.7 | 1251 |
| 133.1 | 1250 |
| 133 | 1265 |
| 132.9 | 1254 |
| 132.9 | 1279 |
| 133.1 | 1253 |
| 133.3 | 1262 |
| 133.3 | 1260 |
| 132.7 | 1246 |
| 132.9 | 1236 |
| 133.7 | 1256 |
| 133.1 | 1268 |
| 132.9 | 1261 |
| 133.3 | 1286 |
| 132.3 | 1288 |
| 133.2 | 1295 |
| 133.3 | 1302 |
| 133.3 | 1308 |
| 132.6 | 1317 |
| 133.2 | 1329 |
| 132.3 | 1320 |
| 132.7 | 1308 |
| 133.1 | 1311 |
| 133.1 | 1314 |
| 132.4 | 1284 |
| 133.1 | 1292 |
| 132.7 | 1313 |
| 133.1 | 1313 |
| 133.3 | 1321 |
| 133 | 1297 |
| 132.9 | 1311 |
| 132.5 | 1317 |
| 133.1 | 1313 |
| 132.4 | 1310 |
| 133.4 | 1317 |
| 133.5 | 1321 |
| 134 | 1324 |
| 133.2 | 1316 |
| 132.9 | 1328 |
| 133.3 | 1325 |
| 133.4 | 1327 |
| 133 | 1323 |
| 132.8 | 1337 |
| 133.2 | 1339 |
| 133.5 | 1342 |
| 134.2 | 1334 |
| 133.7 | 1331 |
| 133.8 | 1347 |
| 134.1 | 1346 |
| 133.5 | 1356 |
| 133.8 | 1345 |
| 133.8 | 1344 |
| 134.2 | 1352 |
| 133.3 | 1358 |
| 133.6 | 1366 |
| 132.8 | 1386 |
| 133.7 | 1392 |
| 132.9 | 1396 |
| 133.6 | 1418 |
| 133.1 | 1415 |
| 133.5 | 1400 |
| 133.5 | 1404 |
| 133.6 | 1427 |
| 133.8 | 1437 |
| 133.6 | 1445 |
| 133.6 | 1439 |
| 133.9 | 1416 |
| 133.6 | 1410 |
| 133.4 | 1407 |
| 133.8 | 1414 |
| 133.2 | 1425 |
| 133.7 | 1436 |
| 132.8 | 1440 |
| 133.5 | 1434 |
| 132.8 | 1438 |
| 133.6 | 1430 |
| 132.6 | 1438 |
| 133.8 | 1462 |
| 133.3 | 1475 |
| 132.6 | 1480 |
| 132.9 | 1486 |
| 132.4 | 1478 |
| 133.1 | 1483 |
| 133.1 | 1478 |
| 132.7 | 1486 |
| 132.5 | 1495 |
| 133 | 1479 |
| 132.6 | 1466 |
| 132.3 | 1485 |
| 132.9 | 1488 |
| 132.6 | 1496 |
| 132.8 | 1484 |
| 133.2 | 1503 |
| 133 | 1510 |
| 133.2 | 1526 |
| 133.3 | 1531 |
| 132.7 | 1529 |
| 132.8 | 1542 |
| 133 | 1549 |
| 133.2 | 1576 |
| 133.4 | 1571 |
| 132.6 | 1560 |
| 133 | 1553 |
| 132.3 | 1554 |
| 134 | 1558 |
| 132.9 | 1573 |
| 133.4 | 1556 |
| 132.7 | 1548 |
| 132.6 | 1548 |
| 132.6 | 1541 |
| 133.1 | 1553 |
| 133.5 | 1587 |
| 133 | 1605 |
| 132.9 | 1593 |
| 133.1 | 1620 |
| 133.1 | 1626 |
| 133 | 1623 |
| 132.5 | 1634 |
| 133.1 | 1613 |
| 132.2 | 1625 |
| 133.2 | 1631 |
| 132.9 | 1647 |
| 132.3 | 1635 |
| 132.8 | 1633 |
| 132.2 | 1646 |
| 133.1 | 1637 |
| 132.3 | 1650 |
| 132.4 | 1651 |
| 131.2 | 1667 |
| 133.2 | 1659 |
| 133.1 | 1641 |
| 132.9 | 1660 |
| 132.2 | 1649 |
| 132.3 | 1653 |
| 132.1 | 1650 |
| 133.5 | 1667 |
| 132.3 | 1665 |
| 133.4 | 1672 |
| 133 | 1669 |
| 133.8 | 1682 |
| 133.2 | 1689 |
| 133 | 1686 |
| 132.6 | 1671 |
| 133.2 | 1702 |
| 132.8 | 1692 |
| 132.7 | 1704 |
| 132.6 | 1702 |
| 133.3 | 1708 |
| 133 | 1742 |
| 132.7 | 1757 |
| 133.8 | 1767 |
| 133.3 | 1763 |
| 134 | 1772 |
| 133.4 | 1778 |
| 133 | 1781 |
| 133.3 | 1785 |
| 133 | 1792 |
| 132.6 | 1799 |
| 132.9 | 1782 |
| 132.1 | 1768 |
| 132.4 | 1779 |
| 133.1 | 1785 |
| 133 | 1784 |
| 133.4 | 1788 |
| 132.9 | 1781 |
| 132.4 | 1763 |
| 133 | 1760 |
| 133.2 | 1764 |
| 133.9 | 1776 |
| 132.8 | 1796 |
| 133.5 | 1781 |
| 133.8 | 1803 |
| 133.4 | 1778 |
| 133.8 | 1798 |
| 133.6 | 1807 |
| 133.1 | 1798 |
| 132.7 | 1795 |
| 132.8 | 1801 |
| 132.3 | 1813 |
| 132.9 | 1825 |
| 133 | 1844 |
| 133.3 | 1834 |
| 133.5 | 1849 |
| 133.4 | 1850 |
| 133.8 | 1850 |
| 133.1 | 1852 |
| 133.1 | 1843 |
| 133.5 | 1843 |
| 133.4 | 1840 |
| 134 | 1840 |
| 133.9 | 1857 |
| 132.7 | 1878 |
| 132.5 | 1864 |
| 133.5 | 1868 |
| 132.4 | 1859 |
| 133.7 | 1874 |
| 133.4 | 1857 |
| 133.5 | 1872 |
| 133 | 1871 |
| 132.8 | 1870 |
| 133.4 | 1877 |
| 132.6 | 1893 |
| 133.2 | 1887 |
| 132.7 | 1877 |
| 132.8 | 1896 |
| 133.2 | 1880 |
| 133.3 | 1867 |
| 133.4 | 1875 |
| 133.4 | 1887 |
| 133.4 | 1891 |
| 133.3 | 1901 |
| 133 | 1898 |
| 132.7 | 1886 |
| 133.9 | 1907 |
| 133.1 | 1926 |
| 133.9 | 1935 |
| 133.9 | 1903 |
| 133.1 | 1905 |
| 133.3 | 1918 |
| 133.1 | 1923 |
| 133.1 | 1930 |
| 134.1 | 1916 |
| 134.2 | 1898 |
| 133.6 | 1902 |
| 133.7 | 1913 |
| 133 | 1924 |
| 132.6 | 1920 |
| 133 | 1911 |
| 132.7 | 1895 |
| 132.7 | 1926 |
| 133 | 1944 |
| 133.7 | 1930 |
| 133.2 | 1907 |
| 132.3 | 1912 |
| 133.1 | 1916 |
| 132.7 | 1934 |
| 133 | 1931 |
| 133.3 | 1934 |
| 132.1 | 1946 |
| 133 | 1927 |
| 132.7 | 1936 |
| 132.6 | 1953 |
| 133.8 | 1947 |
| 132.8 | 1943 |
| 133.7 | 1925 |
| 133.2 | 1907 |
| 132.9 | 1936 |
| 133.5 | 1931 |
| 133.1 | 1940 |
| 133.4 | 1951 |
| 132 | 1947 |
| 133.1 | 1951 |
| 133.1 | 1949 |
| 132.5 | 1951 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 130 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 130 |


</details>

### `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222`

PE CG, film with a 3 nm-radius cylindrical hole at 160 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`). Status: finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free_gap5nm`, `hole_free`, `hole_scaf_rel0`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.2857 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`
- **`hole_scaf_rel0_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`
- **`hole_free_gap5nm`** (rdyu-server): finished; started 2026-11-02 20:16 UTC, ended 2026-11-05 05:32 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`
- **`hole_free`** (rdyu-server): finished; started 2026-11-12 02:42 UTC, ended 2026-11-14 15:51 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`
- **`hole_scaf_rel0`** (rdyu-rog): finished; started 2026-11-12 18:21 UTC, ended 2026-11-12 23:27 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free_gap5nm`, `hole_free`, `hole_scaf_rel0` | `hole_free`, `hole_scaf_rel0` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 133.5
- `free_shell.areal_density_ratio`: 0.8489
- `free_shell.msd.1 ns`: 642.2
- `free_shell.msd.10 ns`: 1620
- `free_shell.msd.end`: 2393
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- T (°C): 160
- `t_close_ns`: 0.105
- `thickness_final`: 134.1
- `thickness_t0`: 167.8

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 134.8 | — |
| 134.1 | — |
| 134 | — |
| 134 | — |
| 134.4 | — |
| 135 | — |
| 134.5 | — |
| 134.1 | — |
| 134.7 | — |
| 134.4 | — |
| 133.8 | — |
| 135.1 | — |
| 135.1 | — |
| 133.6 | — |
| 135 | — |
| 133.5 | — |
| 134 | — |
| 133.6 | — |
| 134.5 | — |
| 134.3 | — |
| 133.9 | — |
| 133.6 | — |
| 134.6 | — |
| 134.5 | — |
| 132.9 | — |
| 133 | — |
| 135 | — |
| 133.4 | — |
| 134.6 | — |
| 133.9 | — |
| 133.9 | — |
| 134.6 | — |
| 134.3 | — |
| 135.1 | — |
| 133.7 | — |
| 134 | — |
| 134.5 | — |
| 135 | — |
| 134.6 | — |
| 135.4 | — |
| 136 | — |
| 135.2 | — |
| 136.7 | — |
| 135.4 | — |
| 136.4 | — |
| 135 | — |
| 136.3 | — |
| 135.8 | — |
| 135.8 | — |
| 136.2 | — |
| 135.7 | — |
| 136.7 | — |
| 135.7 | — |
| 136.2 | — |
| 135.7 | — |
| 136.1 | — |
| 137.1 | — |
| 137.2 | — |
| 136.9 | — |
| 137.1 | — |
| 137.7 | — |
| 138.9 | — |
| 136.4 | — |
| 137.5 | — |
| 137.3 | — |
| 137.5 | — |
| 137.2 | — |
| 138.9 | — |
| 138.1 | — |
| 138.2 | — |
| 137.8 | — |
| 137.9 | — |
| 139.6 | — |
| 138.2 | — |
| 137.9 | — |
| 139 | — |
| 139.7 | — |
| 138.9 | — |
| 139.6 | — |
| 139.1 | — |
| 139.3 | — |
| 139 | — |
| 139 | — |
| 139.6 | — |
| 139.8 | — |
| 140.1 | — |
| 139.6 | — |
| 138.9 | — |
| 140.5 | — |
| 139.8 | — |
| 140.5 | — |
| 140.6 | — |
| 140 | — |
| 141.6 | — |
| 140.8 | — |
| 142 | — |
| 140.9 | — |
| 141.3 | — |
| 142.1 | — |
| 142.7 | — |
| 142.5 | — |
| 142.1 | — |
| 142.4 | — |
| 142.5 | — |
| 142.5 | — |
| 142.8 | — |
| 142.5 | — |
| 142.8 | — |
| 142.7 | — |
| 142.7 | — |
| 141.8 | — |
| 144.1 | — |
| 144.5 | — |
| 145.3 | — |
| 144.2 | — |
| 144 | — |
| 145.6 | — |
| 144.8 | — |
| 145.5 | — |
| 146.3 | — |
| 145.1 | — |
| 146 | — |
| 145.8 | — |
| 146.2 | — |
| 145.1 | — |
| 146.7 | — |
| 147.1 | — |
| 147.7 | — |
| 148 | — |
| 148.1 | — |
| 149.1 | — |
| 149.2 | — |
| 148.9 | — |
| 148.8 | — |
| 148.6 | — |
| 150.1 | — |
| 149.7 | — |
| 150.7 | — |
| 151.3 | — |
| 149.9 | — |
| 149.4 | — |
| 150.2 | — |
| 150.3 | — |
| 150.5 | — |
| 151.7 | — |
| 150.4 | — |
| 152.8 | — |
| 151.5 | — |
| 152 | — |
| 152.1 | — |
| 152.8 | — |
| 154.8 | — |
| 153.4 | — |
| 154.5 | — |
| 154.3 | — |
| 153 | — |
| 152.8 | — |
| 152.9 | — |
| 152.9 | — |
| 153.9 | — |
| 154.5 | — |
| 155.1 | — |
| 154.3 | — |
| 155.2 | — |
| 155.4 | — |
| 156.3 | — |
| 155.5 | — |
| 157.5 | — |
| 157.3 | — |
| 156.9 | — |
| 157.9 | — |
| 158.4 | — |
| 156.8 | — |
| 157.1 | — |
| 158.9 | — |
| 158.8 | — |
| 159.4 | — |
| 159.7 | — |
| 158.2 | — |
| 159.4 | — |
| 159.7 | — |
| 159.6 | — |
| 161.4 | — |
| 160.6 | — |
| 160.7 | — |
| 160.8 | — |
| 160.1 | — |
| 160.8 | — |
| 161.9 | — |
| 162.9 | — |
| 163 | — |
| 163.7 | — |
| 163.3 | — |
| 162 | — |
| 162 | — |
| 163.2 | — |
| 165 | — |
| 166.5 | — |
| 165.9 | — |
| 165.9 | — |
| 164.3 | — |
| 168.1 | — |
| 165.5 | — |
| 165.6 | — |
| 167.6 | — |
| 166.6 | — |
| 165.5 | — |
| 165.8 | — |
| 166.2 | — |
| 168.3 | — |
| 165.8 | — |
| 166.7 | — |
| 167.1 | — |
| 166.5 | — |
| 165.8 | — |
| 166.9 | — |
| 166.5 | — |
| 167.9 | — |
| 165.9 | — |
| 165.1 | — |
| 166.3 | — |
| 165.7 | — |
| 167.5 | — |
| 168.1 | — |
| 166.5 | — |
| 168.2 | — |
| 168 | — |
| 167.4 | — |
| 167.5 | — |
| 165.8 | — |
| 166.2 | — |
| 165.3 | — |
| 166 | — |
| 166.7 | — |
| 166.5 | — |
| 167.7 | — |
| 166.8 | — |
| 166.9 | — |
| 168.7 | — |
| 168 | — |
| 166.5 | — |
| 166.2 | — |
| 167.2 | — |
| 166.3 | — |
| 166.8 | — |
| 166.7 | — |
| 166.9 | — |
| 165.2 | — |
| 165.3 | — |
| 166.5 | — |
| 166.1 | — |
| 167.4 | — |
| 167.5 | — |
| 165.9 | — |
| 167.8 | — |
| 166.2 | — |
| 167.7 | — |
| 167 | — |
| 166.6 | — |
| 168 | — |
| 166.9 | — |
| 166.3 | — |
| 167.2 | — |
| 165.8 | — |
| 167.5 | — |
| 169 | — |
| 168.6 | — |
| 167.7 | — |
| 167.8 | — |
| 168.2 | — |
| 164.9 | — |
| 167.7 | — |
| 166.4 | — |
| 167 | — |
| 167.3 | — |
| 166.5 | — |
| 166.5 | — |
| 169.5 | — |
| 167.3 | — |
| 166.8 | — |
| 168 | — |
| 165.8 | — |
| 167.8 | — |
| 167.7 | — |
| 166.9 | — |
| 166.6 | — |
| 166.4 | — |
| 168 | — |
| 167.2 | — |
| 168.1 | — |
| 168.1 | — |
| 165.8 | — |
| 167.2 | — |
| 167.9 | — |
| 167.6 | — |
| 167.7 | — |
| 166.1 | — |
| 166.4 | — |
| 167 | — |
| 168.2 | — |
| 168.8 | — |
| 167.5 | — |
| 166.6 | — |
| 166.5 | — |
| 166.8 | — |
| 168.4 | — |
| 166.8 | — |
| 167 | — |
| 167.6 | — |
| 168.3 | — |
| 167.4 | — |
| 168 | — |
| 167.6 | — |
| 167.4 | — |
| 167.2 | — |
| 167.6 | — |
| 166.9 | — |
| 167.3 | — |
| 167.8 | — |
| 166 | — |
| 168.4 | — |
| 166.2 | — |
| 167.2 | — |
| 166.7 | — |
| 167.7 | — |
| 169.9 | — |
| 167.6 | — |
| 166 | — |
| 167.3 | — |
| 168.1 | — |
| 168.2 | — |
| 167.2 | — |
| 167.2 | — |
| 167.9 | — |
| 168.7 | — |
| 168.1 | — |
| 167.5 | — |
| 167.5 | — |
| 167.9 | — |
| 166.9 | — |
| 167.9 | — |
| 168.1 | — |
| 167.2 | — |
| 167.9 | — |
| 167.1 | — |
| 168.2 | — |
| 167.9 | — |
| 168.1 | — |
| 167.1 | — |
| 167.5 | — |
| 166.1 | — |
| 166.7 | — |
| 167.3 | — |
| 167.3 | — |
| 168.3 | — |
| 168.2 | — |
| 167.7 | — |
| 167.7 | — |
| 169.3 | — |
| 169.5 | — |
| 168.7 | — |
| 166.2 | — |
| 167.8 | — |
| 167.9 | — |
| 167.5 | — |
| 167.3 | — |
| 166.9 | — |
| 168 | — |
| 169.3 | — |
| 168.7 | — |
| 168.3 | — |
| 168.4 | — |
| 168.3 | — |
| 168.2 | — |
| 168.1 | — |
| 168.6 | — |
| 167.3 | — |
| 168 | — |
| 170.6 | — |
| 168.1 | — |
| 170 | — |
| 167.7 | — |
| 168.5 | — |
| 167.6 | — |
| 168.3 | — |
| 168 | — |
| 167.1 | — |
| 168.7 | — |
| 168.3 | — |
| 168.9 | — |
| 168.2 | — |
| 169.4 | — |
| 170.4 | — |
| 169.8 | — |
| 169.3 | — |
| 170.5 | — |
| 167.8 | — |
| 168.1 | — |
| 168.5 | — |
| 168 | — |
| 167.8 | 0 |
| 167.5 | 19.14 |
| 165.4 | 34.88 |
| 162.9 | 49.14 |
| 160.8 | 61.63 |
| 157.7 | 74.89 |
| 156.2 | 89.5 |
| 156.2 | 102.9 |
| 155.2 | 116.4 |
| 152.8 | 127 |
| 152.5 | 140.5 |
| 151.1 | 154.3 |
| 149.4 | 167 |
| 148.9 | 179.6 |
| 148 | 192.5 |
| 147.2 | 204 |
| 147.6 | 213 |
| 146.8 | 216.5 |
| 145.8 | 229.4 |
| 145.2 | 238.9 |
| 144.7 | 246.3 |
| 144.1 | 254.5 |
| 143.1 | 266.4 |
| 142.3 | 280 |
| 140.9 | 289 |
| 140.6 | 297.3 |
| 141.3 | 303.7 |
| 140.2 | 314.3 |
| 139.9 | 323.8 |
| 138.6 | 329.3 |
| 139.7 | 337.1 |
| 139.4 | 342.8 |
| 139.8 | 343.1 |
| 139.2 | 346.6 |
| 138.2 | 348.8 |
| 139 | 356.7 |
| 138.1 | 363.9 |
| 138.2 | 371 |
| 137.8 | 372.4 |
| 138.5 | 374.6 |
| 137.8 | 376.9 |
| 137.9 | 387.2 |
| 138.5 | 389.5 |
| 137.9 | 387.9 |
| 138.5 | 393.2 |
| 138 | 398.1 |
| 137.9 | 401.5 |
| 138 | 409.9 |
| 137.8 | 413.1 |
| 136.8 | 406.7 |
| 137.5 | 406.7 |
| 137.8 | 407.9 |
| 137 | 410.3 |
| 136.5 | 417.1 |
| 137.2 | 420.7 |
| 138 | 421 |
| 137.3 | 423.8 |
| 137.4 | 432.7 |
| 137.4 | 439.4 |
| 137.5 | 444.6 |
| 137.1 | 440.2 |
| 137.4 | 443 |
| 137.7 | 450.9 |
| 137.8 | 450.8 |
| 137 | 449.3 |
| 136.9 | 451.5 |
| 137.3 | 452.6 |
| 136.3 | 454.1 |
| 136.7 | 454.8 |
| 136.2 | 460.8 |
| 136.7 | 463.2 |
| 136.1 | 465.2 |
| 135.5 | 466.4 |
| 137.3 | 469.6 |
| 137.7 | 466.8 |
| 136.3 | 468.6 |
| 136 | 473.8 |
| 135.7 | 479.3 |
| 136.8 | 480 |
| 136.8 | 482 |
| 136.7 | 482.1 |
| 135.8 | 486.8 |
| 136.1 | 489 |
| 136.5 | 488.3 |
| 136.1 | 494.5 |
| 136.3 | 495 |
| 136.4 | 495.7 |
| 135.6 | 504.1 |
| 135.6 | 507.4 |
| 136.5 | 513.8 |
| 135.8 | 512.9 |
| 136.7 | 515.6 |
| 136.7 | 516.8 |
| 136 | 518.9 |
| 135.6 | 522.7 |
| 136.6 | 524 |
| 136.3 | 523.8 |
| 135.6 | 523.8 |
| 136 | 521.1 |
| 136 | 520.5 |
| 135.7 | 519.9 |
| 136.1 | 520.8 |
| 135.7 | 526.4 |
| 134.9 | 524.9 |
| 136 | 525.2 |
| 134.8 | 524.6 |
| 135.3 | 522.1 |
| 135.6 | 519.8 |
| 136.1 | 517.8 |
| 136.3 | 517.4 |
| 135.8 | 517.4 |
| 134.8 | 519.1 |
| 134.7 | 517.9 |
| 136.1 | 517.8 |
| 136.2 | 518.1 |
| 137 | 518.4 |
| 136 | 522.3 |
| 135.6 | 526.4 |
| 135.4 | 529.3 |
| 136.2 | 531.7 |
| 136 | 532.7 |
| 135.3 | 530.6 |
| 135.8 | 534.1 |
| 135.1 | 540.7 |
| 135.4 | 547.5 |
| 134.9 | 552.1 |
| 134.7 | 549.8 |
| 134.5 | 549.9 |
| 135 | 551.1 |
| 134.4 | 555.6 |
| 134.9 | 560.4 |
| 134.2 | 563 |
| 134.7 | 562.2 |
| 135.2 | 564.6 |
| 135.1 | 558.7 |
| 134.6 | 561.4 |
| 134.9 | 558.9 |
| 135.1 | 561.6 |
| 135.2 | 566.5 |
| 135.2 | 565 |
| 135.1 | 568.6 |
| 134.8 | 566.2 |
| 134.9 | 570.4 |
| 135.3 | 572.1 |
| 134.2 | 573.2 |
| 134.7 | 576.5 |
| 135.9 | 575.6 |
| 136 | 579.4 |
| 135.8 | 585.4 |
| 136.1 | 589.2 |
| 135.1 | 589 |
| 135.2 | 592.6 |
| 134.6 | 594 |
| 135 | 596.1 |
| 135.4 | 588.4 |
| 135.6 | 594.5 |
| 135.4 | 599.2 |
| 136.3 | 604.6 |
| 134.8 | 608.9 |
| 135.2 | 607.5 |
| 136.3 | 601.2 |
| 135.6 | 598.5 |
| 134.9 | 604.7 |
| 135.5 | 609.7 |
| 135.8 | 607.3 |
| 136.3 | 604.3 |
| 136.3 | 603.6 |
| 136.1 | 607.8 |
| 135.4 | 610.7 |
| 136.6 | 606.8 |
| 136.6 | 605.9 |
| 137 | 614.8 |
| 137 | 618.5 |
| 135.9 | 618.8 |
| 136.3 | 619 |
| 136.3 | 617.1 |
| 136.9 | 613.9 |
| 136.1 | 616.6 |
| 134.2 | 617.4 |
| 134.8 | 622 |
| 134.7 | 620 |
| 135.2 | 623.2 |
| 135.9 | 625.8 |
| 135.2 | 628.1 |
| 135.9 | 630 |
| 134.9 | 635.3 |
| 135.2 | 636.7 |
| 134.6 | 634.5 |
| 134.5 | 634.5 |
| 135.4 | 633.2 |
| 135.5 | 632.7 |
| 135.4 | 635.3 |
| 135.2 | 637.1 |
| 135 | 635.5 |
| 135.6 | 644.9 |
| 134.7 | 644.9 |
| 134.5 | 646.1 |
| 134.8 | 648.1 |
| 135 | 645.3 |
| 135.9 | 645.3 |
| 135.6 | 642.2 |
| 134.5 | 644.7 |
| 135.8 | 650.4 |
| 135.2 | 653.1 |
| 135.4 | 652.6 |
| 134.7 | 658.4 |
| 134.5 | 661.2 |
| 134.6 | 660.5 |
| 136.5 | 659 |
| 136 | 656.5 |
| 135.6 | 662.6 |
| 135.2 | 667.3 |
| 135.1 | 670.7 |
| 135.2 | 668.1 |
| 135.4 | 665.5 |
| 135.3 | 663.5 |
| 134.6 | 659.9 |
| 134.4 | 669.8 |
| 134.6 | 669.6 |
| 136.1 | 664.3 |
| 136.2 | 661.3 |
| 135.8 | 658.4 |
| 135.1 | 656.8 |
| 135.4 | 652.4 |
| 136.1 | 652.8 |
| 135.6 | 651.7 |
| 135.9 | 655.8 |
| 135.1 | 661.8 |
| 135 | 666.5 |
| 134.8 | 665.4 |
| 135.6 | 668.4 |
| 136.5 | 669.6 |
| 136.1 | 669 |
| 135.4 | 668.5 |
| 135.1 | 668.9 |
| 135.2 | 669.1 |
| 135.4 | 670.5 |
| 135 | 671.3 |
| 135.3 | 673.3 |
| 135.6 | 677.4 |
| 135 | 677.1 |
| 135.3 | 675.9 |
| 135.1 | 678.2 |
| 135.2 | 680.4 |
| 135.6 | 677.1 |
| 135.8 | 680.3 |
| 136 | 682.8 |
| 134.6 | 689 |
| 134.4 | 687.8 |
| 134.8 | 688.6 |
| 135.3 | 689.4 |
| 135 | 690.8 |
| 135.2 | 694.9 |
| 134 | 696.1 |
| 135.6 | 697.7 |
| 135.3 | 696.1 |
| 134.8 | 693.6 |
| 134.3 | 698.3 |
| 135.5 | 699.3 |
| 135 | 705 |
| 134 | 706.4 |
| 135.2 | 708.2 |
| 135.5 | 706 |
| 134.2 | 710.7 |
| 133.8 | 714.4 |
| 134.7 | 712.6 |
| 134.7 | 712.7 |
| 135.2 | 709.2 |
| 135.7 | 711.8 |
| 134.9 | 712.8 |
| 135.1 | 711 |
| 135 | 710.1 |
| 135.4 | 707.8 |
| 134.9 | 708.5 |
| 135.6 | 716.7 |
| 134.4 | 718.8 |
| 134.1 | 720.6 |
| 135.8 | 723.3 |
| 135.4 | 731.5 |
| 135.5 | 728.1 |
| 136.3 | 727.8 |
| 135.3 | 723.7 |
| 136.3 | 720.8 |
| 135.3 | 721.1 |
| 135.5 | 722.8 |
| 135.9 | 722.3 |
| 135.6 | 719.9 |
| 135.9 | 720.7 |
| 134.9 | 719.6 |
| 135.2 | 718.2 |
| 135.4 | 719.6 |
| 134.7 | 719.3 |
| 135.9 | 716.7 |
| 135.9 | 715.6 |
| 134.8 | 715.4 |
| 135 | 719.9 |
| 134.3 | 725.2 |
| 135.1 | 725.3 |
| 135.7 | 724.5 |
| 135.8 | 729.7 |
| 136.2 | 723.2 |
| 135.1 | 726.7 |
| 135.5 | 720.9 |
| 135.5 | 721 |
| 135.5 | 723.3 |
| 136.1 | 726.5 |
| 135.7 | 725.2 |
| 135.8 | 724.8 |
| 135.5 | 722.2 |
| 135.1 | 728.7 |
| 134.6 | 733.5 |
| 134.5 | 731.8 |
| 135 | 734.5 |
| 135.7 | 737.7 |
| 135.5 | 745.8 |
| 135.3 | 752.2 |
| 135.4 | 752.1 |
| 135 | 753.5 |
| 135.5 | 751.6 |
| 135.5 | 753.1 |
| 135.7 | 754.3 |
| 135.7 | 753.9 |
| 135.2 | 752.3 |
| 135.2 | 751.8 |
| 135.6 | 748 |
| 135.8 | 751.8 |
| 135.9 | 748.6 |
| 134.6 | 743.7 |
| 134.8 | 744.6 |
| 133.9 | 746.9 |
| 134.4 | 750.7 |
| 134.7 | 755.4 |
| 134 | 761.3 |
| 134 | 761.7 |
| 133.7 | 765.5 |
| 133.7 | 771.8 |
| 134.4 | 767.8 |
| 135.5 | 770.8 |
| 135.8 | 771.5 |
| 135.7 | 776.4 |
| 134.4 | 780.2 |
| 135.2 | 781.4 |
| 135.7 | 778.4 |
| 136 | 775.1 |
| 136.2 | 784.8 |
| 135.3 | 781.2 |
| 136 | 781.1 |
| 135.1 | 788.8 |
| 135.5 | 790.5 |
| 136.4 | 785.7 |
| 136 | 783.9 |
| 135.2 | 791.3 |
| 135.9 | 792.3 |
| 135 | 794.7 |
| 135.2 | 796 |
| 135.8 | 801.8 |
| 135.1 | 802.5 |
| 134.6 | 802.5 |
| 134.7 | 809.8 |
| 134.4 | 812.9 |
| 135.2 | 812.5 |
| 135 | 815.7 |
| 134.9 | 823.9 |
| 136 | 826.6 |
| 135.3 | 829.5 |
| 135.1 | 828.7 |
| 135.2 | 826.8 |
| 134.5 | 824.9 |
| 134.5 | 823.6 |
| 134 | 820.5 |
| 133.5 | 814.9 |
| 135.5 | 817 |
| 134.5 | 814.3 |
| 134.2 | 815.8 |
| 134.8 | 817.8 |
| 134.8 | 819.7 |
| 134.1 | 819 |
| 134.3 | 819 |
| 134.6 | 818.9 |
| 135.1 | 825.2 |
| 134.8 | 830.7 |
| 134.3 | 828.9 |
| 134.3 | 830.3 |
| 134.6 | 834.3 |
| 135.4 | 836.6 |
| 134.8 | 843.1 |
| 133.7 | 850.4 |
| 133.9 | 850.8 |
| 134.3 | 848 |
| 134.9 | 843.7 |
| 134.7 | 843.6 |
| 134.8 | 841.1 |
| 135.2 | 842.8 |
| 135.7 | 838.5 |
| 134.4 | 839.6 |
| 134.9 | 840.6 |
| 134.1 | 842.7 |
| 134.3 | 839.5 |
| 134.7 | 839.9 |
| 134.6 | 841.2 |
| 134.5 | 839.7 |
| 133.5 | 844 |
| 135.5 | 833.4 |
| 134.6 | 843.1 |
| 135.3 | 860.3 |
| 134.4 | 875.7 |
| 134.2 | 901.4 |
| 134.4 | 905.3 |
| 134.2 | 914.5 |
| 134.1 | 928.1 |
| 134.2 | 933.9 |
| 133.1 | 941.9 |
| 133.8 | 953.7 |
| 134.7 | 960.7 |
| 132.8 | 965.9 |
| 133.7 | 967 |
| 134.2 | 977.2 |
| 133.8 | 971.4 |
| 134.1 | 980 |
| 134.6 | 991.8 |
| 135.4 | 998.4 |
| 133.4 | 989.8 |
| 133.8 | 988.5 |
| 133.7 | 993.8 |
| 134.5 | 1012 |
| 134 | 1030 |
| 134 | 1038 |
| 134.1 | 1036 |
| 134.9 | 1038 |
| 134.2 | 1033 |
| 134.6 | 1032 |
| 134.6 | 1048 |
| 134.2 | 1067 |
| 133.9 | 1077 |
| 133.2 | 1067 |
| 134.1 | 1061 |
| 133.8 | 1070 |
| 133.3 | 1060 |
| 133.1 | 1068 |
| 133.6 | 1090 |
| 133.5 | 1074 |
| 133.3 | 1081 |
| 134.1 | 1090 |
| 133.2 | 1092 |
| 134.1 | 1103 |
| 133.2 | 1102 |
| 133.1 | 1096 |
| 133.7 | 1097 |
| 133.1 | 1114 |
| 133.9 | 1118 |
| 134.8 | 1132 |
| 133.3 | 1129 |
| 133 | 1138 |
| 134.3 | 1154 |
| 133.3 | 1156 |
| 133 | 1199 |
| 133.3 | 1191 |
| 134.5 | 1197 |
| 134.1 | 1210 |
| 133.6 | 1203 |
| 133.5 | 1211 |
| 134.4 | 1198 |
| 134.3 | 1213 |
| 132.9 | 1226 |
| 133.2 | 1214 |
| 134.2 | 1220 |
| 132.9 | 1230 |
| 132.4 | 1244 |
| 133.3 | 1252 |
| 133.6 | 1255 |
| 134.3 | 1252 |
| 133 | 1265 |
| 133.6 | 1266 |
| 133.8 | 1272 |
| 134.1 | 1270 |
| 133.2 | 1297 |
| 133.5 | 1295 |
| 133.6 | 1285 |
| 133 | 1280 |
| 134.4 | 1285 |
| 134 | 1295 |
| 134.5 | 1305 |
| 133.5 | 1295 |
| 134.2 | 1314 |
| 134.4 | 1307 |
| 134.6 | 1314 |
| 134.1 | 1330 |
| 134.5 | 1323 |
| 134.3 | 1308 |
| 133.3 | 1333 |
| 133.5 | 1336 |
| 133.7 | 1343 |
| 134.6 | 1362 |
| 134.3 | 1371 |
| 134.4 | 1382 |
| 133.7 | 1359 |
| 133.9 | 1377 |
| 133.3 | 1373 |
| 133.5 | 1389 |
| 133.8 | 1388 |
| 135 | 1398 |
| 135.3 | 1399 |
| 134.3 | 1397 |
| 134.9 | 1388 |
| 134.5 | 1394 |
| 135 | 1395 |
| 134.5 | 1403 |
| 133.2 | 1427 |
| 133.9 | 1421 |
| 134.2 | 1444 |
| 133.4 | 1448 |
| 134.8 | 1452 |
| 133.9 | 1446 |
| 133.7 | 1463 |
| 135 | 1478 |
| 134.7 | 1461 |
| 134.3 | 1470 |
| 134.7 | 1484 |
| 133.9 | 1494 |
| 134.7 | 1516 |
| 134.8 | 1502 |
| 134.6 | 1517 |
| 134.9 | 1537 |
| 134.7 | 1526 |
| 134.8 | 1526 |
| 134.3 | 1537 |
| 134.8 | 1546 |
| 134.8 | 1546 |
| 135.4 | 1551 |
| 135 | 1542 |
| 134.8 | 1563 |
| 134 | 1569 |
| 134.6 | 1578 |
| 135.3 | 1588 |
| 133.8 | 1583 |
| 134.6 | 1589 |
| 134.1 | 1592 |
| 134.4 | 1583 |
| 135 | 1592 |
| 134.3 | 1606 |
| 134.6 | 1610 |
| 134.6 | 1616 |
| 134.4 | 1635 |
| 134.9 | 1656 |
| 134.5 | 1664 |
| 135.1 | 1628 |
| 134.8 | 1641 |
| 135.1 | 1638 |
| 135.2 | 1628 |
| 134.6 | 1641 |
| 134.8 | 1640 |
| 134.4 | 1652 |
| 134.9 | 1632 |
| 134.4 | 1631 |
| 134.6 | 1645 |
| 134.5 | 1664 |
| 134.6 | 1648 |
| 134.4 | 1638 |
| 135 | 1622 |
| 134.5 | 1628 |
| 134.2 | 1620 |
| 134 | 1632 |
| 134.5 | 1613 |
| 133.6 | 1661 |
| 134.2 | 1644 |
| 134.2 | 1668 |
| 134.9 | 1664 |
| 134.2 | 1658 |
| 133.8 | 1678 |
| 135.1 | 1677 |
| 135.5 | 1655 |
| 134.1 | 1666 |
| 134.5 | 1680 |
| 134.9 | 1687 |
| 133.9 | 1707 |
| 134.3 | 1698 |
| 135.2 | 1691 |
| 133.7 | 1682 |
| 135.5 | 1683 |
| 134 | 1701 |
| 134.8 | 1711 |
| 135.3 | 1730 |
| 133.4 | 1704 |
| 134.8 | 1707 |
| 134.8 | 1718 |
| 134.6 | 1731 |
| 134.1 | 1747 |
| 134.2 | 1751 |
| 134.2 | 1750 |
| 135 | 1748 |
| 134 | 1721 |
| 134.1 | 1749 |
| 133.7 | 1772 |
| 133.9 | 1805 |
| 135.1 | 1771 |
| 133.6 | 1753 |
| 134.5 | 1784 |
| 134.8 | 1775 |
| 134.8 | 1771 |
| 134.4 | 1762 |
| 134.2 | 1763 |
| 134.2 | 1776 |
| 133.3 | 1775 |
| 134.1 | 1772 |
| 133.1 | 1795 |
| 133.7 | 1801 |
| 133.1 | 1823 |
| 134.3 | 1802 |
| 134.4 | 1802 |
| 134.1 | 1809 |
| 133.9 | 1811 |
| 134.7 | 1801 |
| 133.6 | 1824 |
| 134 | 1831 |
| 133.6 | 1829 |
| 134.3 | 1826 |
| 133.6 | 1829 |
| 133.1 | 1838 |
| 133.4 | 1849 |
| 134.2 | 1840 |
| 133.6 | 1854 |
| 133.7 | 1855 |
| 134.5 | 1856 |
| 133.7 | 1859 |
| 134.1 | 1871 |
| 133.1 | 1881 |
| 132.7 | 1872 |
| 133.7 | 1884 |
| 134.4 | 1880 |
| 133.5 | 1891 |
| 134 | 1883 |
| 133.3 | 1891 |
| 133.3 | 1895 |
| 133.1 | 1898 |
| 133.8 | 1919 |
| 133.5 | 1913 |
| 134.1 | 1924 |
| 132.9 | 1951 |
| 133.3 | 1953 |
| 134.2 | 1970 |
| 134 | 2001 |
| 133.3 | 1989 |
| 134.2 | 2008 |
| 132.9 | 1996 |
| 133 | 1977 |
| 132.8 | 1984 |
| 134.5 | 2007 |
| 133.5 | 2014 |
| 134.3 | 1998 |
| 133.8 | 2004 |
| 134 | 2019 |
| 133.9 | 2019 |
| 134.2 | 2012 |
| 133.6 | 2010 |
| 135 | 1997 |
| 133.7 | 1986 |
| 134.9 | 2016 |
| 133.2 | 2021 |
| 133.6 | 2026 |
| 134.2 | 2026 |
| 134.1 | 2018 |
| 133.9 | 2026 |
| 133.4 | 2024 |
| 133.5 | 2000 |
| 134.3 | 2023 |
| 134.5 | 2020 |
| 133.2 | 2022 |
| 134.3 | 2037 |
| 133.2 | 2064 |
| 133.7 | 2055 |
| 132.9 | 2058 |
| 133.3 | 2052 |
| 133.5 | 2067 |
| 133.4 | 2060 |
| 134.8 | 2077 |
| 133.8 | 2066 |
| 133.4 | 2073 |
| 133.7 | 2073 |
| 134.3 | 2061 |
| 133.8 | 2080 |
| 133.8 | 2086 |
| 134.4 | 2077 |
| 133.9 | 2059 |
| 133.8 | 2062 |
| 133.4 | 2063 |
| 134.4 | 2056 |
| 134.9 | 2056 |
| 134.9 | 2059 |
| 134 | 2087 |
| 134 | 2076 |
| 133.9 | 2076 |
| 134.5 | 2078 |
| 132.7 | 2101 |
| 134.3 | 2084 |
| 133.8 | 2079 |
| 134.8 | 2086 |
| 133.9 | 2084 |
| 134.2 | 2084 |
| 134.6 | 2081 |
| 133.7 | 2082 |
| 133.5 | 2073 |
| 133.2 | 2087 |
| 133.8 | 2089 |
| 134.2 | 2118 |
| 134.7 | 2112 |
| 134.1 | 2122 |
| 135 | 2118 |
| 135.3 | 2127 |
| 133.7 | 2141 |
| 133.5 | 2142 |
| 133.7 | 2133 |
| 134.2 | 2144 |
| 132.9 | 2163 |
| 134.5 | 2168 |
| 134.5 | 2168 |
| 135 | 2159 |
| 134.1 | 2200 |
| 135 | 2198 |
| 133.6 | 2179 |
| 133.8 | 2190 |
| 133.5 | 2188 |
| 134.5 | 2189 |
| 134.7 | 2217 |
| 134.4 | 2196 |
| 134.3 | 2221 |
| 134.3 | 2192 |
| 134.5 | 2182 |
| 134.2 | 2187 |
| 134.4 | 2216 |
| 134.2 | 2223 |
| 134.4 | 2215 |
| 134.4 | 2234 |
| 134.9 | 2239 |
| 133.7 | 2218 |
| 134.9 | 2227 |
| 133.7 | 2235 |
| 134.7 | 2268 |
| 134.5 | 2271 |
| 134.7 | 2272 |
| 134.3 | 2293 |
| 135.4 | 2270 |
| 134.5 | 2279 |
| 133.5 | 2300 |
| 135.1 | 2311 |
| 134.3 | 2304 |
| 134.4 | 2332 |
| 134 | 2329 |
| 134.9 | 2320 |
| 134.5 | 2328 |
| 134 | 2327 |
| 133.3 | 2350 |
| 133.8 | 2348 |
| 133.5 | 2359 |
| 135.2 | 2347 |
| 133.6 | 2353 |
| 134 | 2349 |
| 134.3 | 2355 |
| 134.8 | 2352 |
| 134.1 | 2361 |
| 134.5 | 2358 |
| 134.1 | 2393 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |


**`hole_scaf_rel0` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 133.5
- `free_shell.areal_density_ratio`: 0.7649
- `free_shell.msd.1 ns`: 597.9
- `free_shell.msd.10 ns`: 1476
- `free_shell.msd.end`: 2282
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: 160
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 1e+04
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `scaffold.d_nm`: 2.5
- `scaffold.nearest_tethered_r_held_min`: 53.12
- `scaffold.nearest_tethered_r_t0`: 55
- `scaffold.tethered_fraction`: 0.5852
- T (°C): 160
- `t_close_ns`: 0.05
- `thickness_final`: 134.5
- `thickness_t0`: 166.9

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 134.5 | — |
| 134.7 | — |
| 133.8 | — |
| 133.8 | — |
| 134.1 | — |
| 134.2 | — |
| 133.8 | — |
| 134.4 | — |
| 133.9 | — |
| 133.5 | — |
| 134.4 | — |
| 134.5 | — |
| 134.7 | — |
| 134.2 | — |
| 134.1 | — |
| 135.3 | — |
| 134.5 | — |
| 134.8 | — |
| 134.3 | — |
| 134.4 | — |
| 134.5 | — |
| 134.1 | — |
| 134.7 | — |
| 134 | — |
| 134.1 | — |
| 134.7 | — |
| 134.8 | — |
| 134.2 | — |
| 134 | — |
| 134.7 | — |
| 134.6 | — |
| 134.6 | — |
| 134.7 | — |
| 134.2 | — |
| 133.7 | — |
| 134.9 | — |
| 134.9 | — |
| 134.9 | — |
| 135.5 | — |
| 135.8 | — |
| 135.3 | — |
| 135 | — |
| 135.3 | — |
| 136.1 | — |
| 134.9 | — |
| 135.9 | — |
| 135.3 | — |
| 135.5 | — |
| 135.9 | — |
| 135.5 | — |
| 136.1 | — |
| 135.8 | — |
| 135.9 | — |
| 136.9 | — |
| 136.4 | — |
| 136.1 | — |
| 136.6 | — |
| 136.8 | — |
| 137.3 | — |
| 136.8 | — |
| 137 | — |
| 137.1 | — |
| 137.1 | — |
| 136.9 | — |
| 136.6 | — |
| 137.5 | — |
| 136.8 | — |
| 138.2 | — |
| 137.5 | — |
| 136.6 | — |
| 139.4 | — |
| 137.8 | — |
| 138 | — |
| 138.4 | — |
| 138.8 | — |
| 138.1 | — |
| 138.3 | — |
| 139 | — |
| 139.7 | — |
| 139.7 | — |
| 139.4 | — |
| 139.1 | — |
| 139 | — |
| 140 | — |
| 139.6 | — |
| 140.6 | — |
| 139.5 | — |
| 138.9 | — |
| 140 | — |
| 139.6 | — |
| 140.9 | — |
| 140.9 | — |
| 140 | — |
| 140.1 | — |
| 141 | — |
| 141.4 | — |
| 141.1 | — |
| 141.9 | — |
| 142.1 | — |
| 143 | — |
| 142.9 | — |
| 142.8 | — |
| 142.3 | — |
| 142.7 | — |
| 142.4 | — |
| 144 | — |
| 143.5 | — |
| 143.7 | — |
| 144.7 | — |
| 144.9 | — |
| 144 | — |
| 143.4 | — |
| 143.8 | — |
| 144.3 | — |
| 145.1 | — |
| 145.2 | — |
| 144.9 | — |
| 144.9 | — |
| 145.3 | — |
| 144.7 | — |
| 145.9 | — |
| 145.9 | — |
| 146.9 | — |
| 145.5 | — |
| 146 | — |
| 146.5 | — |
| 146.6 | — |
| 147 | — |
| 147.4 | — |
| 146.4 | — |
| 147.3 | — |
| 148.3 | — |
| 147.5 | — |
| 148.6 | — |
| 147.9 | — |
| 148.3 | — |
| 147.7 | — |
| 147.6 | — |
| 148.9 | — |
| 149 | — |
| 149.8 | — |
| 148.6 | — |
| 150.2 | — |
| 149.5 | — |
| 150.1 | — |
| 151.5 | — |
| 150.2 | — |
| 150.3 | — |
| 151.8 | — |
| 151 | — |
| 152.5 | — |
| 153.7 | — |
| 152.2 | — |
| 153.3 | — |
| 154.5 | — |
| 153.3 | — |
| 153.6 | — |
| 154.5 | — |
| 154.9 | — |
| 154.2 | — |
| 155.7 | — |
| 154.4 | — |
| 154.6 | — |
| 154.8 | — |
| 154.3 | — |
| 155.3 | — |
| 156.6 | — |
| 157.1 | — |
| 157.8 | — |
| 157.4 | — |
| 157.6 | — |
| 158.8 | — |
| 157.6 | — |
| 158.3 | — |
| 157.6 | — |
| 159.1 | — |
| 159.6 | — |
| 158 | — |
| 159.8 | — |
| 161 | — |
| 159.8 | — |
| 161.6 | — |
| 161.1 | — |
| 160.8 | — |
| 161.2 | — |
| 159.7 | — |
| 163.5 | — |
| 160.5 | — |
| 162.1 | — |
| 161.6 | — |
| 162.2 | — |
| 162 | — |
| 163.4 | — |
| 166 | — |
| 165.3 | — |
| 164.4 | — |
| 165.5 | — |
| 164.4 | — |
| 166.5 | — |
| 165.8 | — |
| 164.9 | — |
| 167.7 | — |
| 166.4 | — |
| 165.8 | — |
| 166.4 | — |
| 165.3 | — |
| 165.6 | — |
| 166.4 | — |
| 166.6 | — |
| 166.3 | — |
| 166.9 | — |
| 167.5 | — |
| 165.3 | — |
| 167.6 | — |
| 167.2 | — |
| 166.4 | — |
| 165 | — |
| 165.9 | — |
| 166.5 | — |
| 167 | — |
| 167.8 | — |
| 168.3 | — |
| 167.1 | — |
| 166.9 | — |
| 167.6 | — |
| 167.6 | — |
| 166.6 | — |
| 167.6 | — |
| 166.7 | — |
| 166.2 | — |
| 165.8 | — |
| 166.9 | — |
| 166.7 | — |
| 166.5 | — |
| 166.9 | — |
| 167.1 | — |
| 168.7 | — |
| 169.3 | — |
| 166.3 | — |
| 165.9 | — |
| 166.4 | — |
| 166.7 | — |
| 166 | — |
| 167.6 | — |
| 167.3 | — |
| 164.8 | — |
| 167.3 | — |
| 166.3 | — |
| 166 | — |
| 166.8 | — |
| 166 | — |
| 166.5 | — |
| 167.3 | — |
| 167.7 | — |
| 167.8 | — |
| 166.5 | — |
| 167.6 | — |
| 167 | — |
| 167 | — |
| 167.4 | — |
| 167.9 | — |
| 168.6 | — |
| 166.9 | — |
| 166 | — |
| 167.6 | — |
| 167.3 | — |
| 167.4 | — |
| 165.8 | — |
| 167.9 | — |
| 166.4 | — |
| 167.9 | — |
| 167 | — |
| 167 | — |
| 167.1 | — |
| 167.6 | — |
| 167.2 | — |
| 168 | — |
| 166.4 | — |
| 166.7 | — |
| 167.4 | — |
| 167 | — |
| 167.5 | — |
| 167.6 | — |
| 167.3 | — |
| 166 | — |
| 167.3 | — |
| 167.6 | — |
| 167.6 | — |
| 165.9 | — |
| 167.8 | — |
| 166.9 | — |
| 169 | — |
| 168.3 | — |
| 167.7 | — |
| 167.8 | — |
| 169.2 | — |
| 169 | — |
| 168.8 | — |
| 167.9 | — |
| 167.7 | — |
| 167.6 | — |
| 169 | — |
| 166.8 | — |
| 167.9 | — |
| 169.4 | — |
| 167.5 | — |
| 167.3 | — |
| 168.7 | — |
| 165.5 | — |
| 166.5 | — |
| 167 | — |
| 165.6 | — |
| 165.9 | — |
| 167.4 | — |
| 167 | — |
| 166.5 | — |
| 166.9 | — |
| 167 | — |
| 167.4 | — |
| 167.3 | — |
| 166.7 | — |
| 166.6 | — |
| 166.6 | — |
| 167.1 | — |
| 165.2 | — |
| 167.3 | — |
| 167 | — |
| 168.4 | — |
| 168 | — |
| 167.7 | — |
| 167.9 | — |
| 168.3 | — |
| 167.8 | — |
| 167.7 | — |
| 166.7 | — |
| 167 | — |
| 167.1 | — |
| 165.9 | — |
| 168.6 | — |
| 167.8 | — |
| 167.7 | — |
| 166.9 | — |
| 167.8 | — |
| 167 | — |
| 167.8 | — |
| 168.3 | — |
| 166.2 | — |
| 167.8 | — |
| 168.2 | — |
| 167.1 | — |
| 166 | — |
| 166.8 | — |
| 166.7 | — |
| 168.2 | — |
| 166.1 | — |
| 167.2 | — |
| 167.5 | — |
| 167 | — |
| 167.2 | — |
| 164.9 | — |
| 168.4 | — |
| 166.5 | — |
| 166.6 | — |
| 168.5 | — |
| 167.8 | — |
| 167.2 | — |
| 166.7 | — |
| 167.2 | — |
| 167 | — |
| 166.2 | — |
| 168 | — |
| 167.9 | — |
| 167.1 | — |
| 169.4 | — |
| 168.2 | — |
| 168.2 | — |
| 168 | — |
| 168.1 | — |
| 168.2 | — |
| 168.4 | — |
| 167.7 | — |
| 168.4 | — |
| 168 | — |
| 168.4 | — |
| 168.7 | — |
| 167.9 | — |
| 167.4 | — |
| 167.6 | — |
| 165.9 | — |
| 165.7 | — |
| 167.6 | — |
| 168.7 | — |
| 167.7 | — |
| 168.6 | — |
| 168.5 | — |
| 169.8 | — |
| 169 | — |
| 168.6 | — |
| 168.9 | — |
| 167.8 | — |
| 166.9 | — |
| 166.7 | — |
| 166.8 | — |
| 166.9 | — |
| 167.4 | — |
| 167 | — |
| 166.9 | — |
| 167.1 | — |
| 166.6 | — |
| 166.9 | — |
| 166.6 | — |
| 167.2 | — |
| 167.2 | — |
| 167.1 | — |
| 167 | — |
| 166.8 | — |
| 167 | — |
| 166.7 | — |
| 166.8 | — |
| 167.1 | — |
| 166.9 | — |
| 166.6 | — |
| 166.9 | — |
| 166.9 | — |
| 167 | — |
| 167.2 | — |
| 167.1 | — |
| 167.1 | — |
| 167.1 | — |
| 166.9 | — |
| 166.7 | — |
| 166.7 | — |
| 166.9 | — |
| 166.9 | — |
| 166.7 | — |
| 166.8 | — |
| 166.9 | — |
| 166.9 | — |
| 166.9 | — |
| 167.2 | — |
| 167 | — |
| 166.6 | — |
| 167 | — |
| 167.1 | — |
| 167.4 | — |
| 167 | — |
| 166.8 | — |
| 167.1 | — |
| 166.8 | — |
| 166.7 | — |
| 167.1 | — |
| 167 | — |
| 166.6 | — |
| 166.8 | — |
| 166.6 | — |
| 166.9 | — |
| 166.9 | — |
| 166.9 | — |
| 167.2 | — |
| 166.8 | — |
| 166.8 | — |
| 167.1 | — |
| 166.9 | — |
| 167 | — |
| 166.6 | — |
| 166.6 | — |
| 166.8 | — |
| 166.8 | — |
| 166.5 | — |
| 167.1 | — |
| 166.9 | — |
| 166.8 | — |
| 166.6 | — |
| 166.7 | — |
| 167.1 | — |
| 166.9 | — |
| 166.8 | — |
| 166.9 | — |
| 167 | — |
| 166.9 | — |
| 167.2 | — |
| 166.9 | — |
| 166.8 | — |
| 167.1 | — |
| 167.1 | — |
| 166.9 | — |
| 166.7 | — |
| 167.1 | — |
| 167 | — |
| 167 | — |
| 167.4 | — |
| 167.2 | — |
| 167.1 | — |
| 166.8 | — |
| 167.1 | — |
| 166.8 | — |
| 167 | — |
| 166.9 | — |
| 166.9 | — |
| 167.1 | — |
| 166.8 | — |
| 166.9 | — |
| 167.4 | — |
| 167.1 | — |
| 166.9 | — |
| 166.8 | — |
| 166.9 | — |
| 166.9 | — |
| 167.3 | — |
| 167 | — |
| 166.8 | — |
| 167.1 | — |
| 167.1 | — |
| 167.1 | — |
| 167.2 | — |
| 167 | — |
| 166.9 | — |
| 166.7 | — |
| 166.8 | — |
| 167 | — |
| 167.2 | — |
| 166.9 | — |
| 166.9 | — |
| 167.1 | — |
| 166.9 | — |
| 166.9 | — |
| 166.9 | — |
| 167.1 | — |
| 166.7 | — |
| 166.7 | — |
| 167.1 | — |
| 167.2 | — |
| 166.8 | — |
| 167.1 | — |
| 167.2 | — |
| 166.9 | — |
| 166.5 | — |
| 167 | — |
| 167 | — |
| 166.9 | — |
| 167.3 | — |
| 167.3 | — |
| 167.3 | — |
| 167.2 | — |
| 167 | — |
| 167 | — |
| 167.1 | — |
| 167 | — |
| 167.1 | — |
| 166.8 | — |
| 167 | — |
| 167 | — |
| 167 | — |
| 167.1 | — |
| 167 | — |
| 166.8 | — |
| 167.1 | — |
| 166.9 | — |
| 167.2 | — |
| 167.3 | — |
| 167.1 | — |
| 166.9 | — |
| 167.1 | — |
| 166.9 | — |
| 167.1 | — |
| 167.1 | — |
| 167.3 | — |
| 167 | — |
| 166.9 | — |
| 166.9 | — |
| 167.1 | — |
| 166.9 | — |
| 166.9 | — |
| 166.9 | — |
| 167.1 | — |
| 166.6 | — |
| 167 | — |
| 167 | — |
| 166.9 | — |
| 167 | — |
| 167.1 | — |
| 167.2 | — |
| 166.8 | — |
| 166.8 | — |
| 166.8 | — |
| 167.3 | — |
| 167.2 | — |
| 166.6 | — |
| 166.8 | — |
| 166.6 | — |
| 166.8 | — |
| 166.9 | — |
| 167 | — |
| 166.8 | — |
| 166.8 | — |
| 166.8 | — |
| 167 | — |
| 166.6 | — |
| 167.1 | — |
| 167.2 | — |
| 166.9 | 0 |
| 165.8 | 19.86 |
| 163.8 | 33.97 |
| 160.7 | 45.77 |
| 157.3 | 57.88 |
| 156.7 | 69.93 |
| 155 | 82.51 |
| 153.8 | 93.86 |
| 152.8 | 106.2 |
| 150.9 | 115.3 |
| 149.4 | 126.4 |
| 148.8 | 137.1 |
| 147 | 149.9 |
| 144.8 | 161.9 |
| 144.5 | 170.6 |
| 143.5 | 181.1 |
| 142.4 | 184.9 |
| 141.8 | 195.5 |
| 140.1 | 203.2 |
| 141.3 | 213.2 |
| 139.9 | 221 |
| 138.7 | 226.2 |
| 140.1 | 228.8 |
| 139.6 | 232.8 |
| 140.4 | 238.2 |
| 140.2 | 245.3 |
| 138.5 | 251.2 |
| 139.9 | 256.7 |
| 139.8 | 261.2 |
| 139.1 | 261.4 |
| 140.6 | 261.8 |
| 138.7 | 260.5 |
| 138.9 | 265.9 |
| 139 | 269 |
| 138.1 | 277 |
| 138.2 | 286.2 |
| 138.4 | 293.6 |
| 138.8 | 294.8 |
| 138.8 | 297.2 |
| 138.1 | 302.7 |
| 138.4 | 308.1 |
| 137.9 | 312.2 |
| 139.1 | 315 |
| 138.9 | 319.1 |
| 137.9 | 321 |
| 137.7 | 323 |
| 137.1 | 326 |
| 138.1 | 325.7 |
| 137.4 | 324.6 |
| 138.5 | 327.2 |
| 137.3 | 329.9 |
| 138.4 | 334.2 |
| 138.3 | 338.2 |
| 138.4 | 341.2 |
| 137.3 | 339 |
| 137.6 | 342.1 |
| 136.6 | 348.7 |
| 137.1 | 350.9 |
| 137.9 | 352.9 |
| 137.7 | 353.7 |
| 137.9 | 353.9 |
| 137.7 | 356.2 |
| 137.9 | 357.4 |
| 138 | 354.8 |
| 138 | 352.8 |
| 138.3 | 357.8 |
| 137.2 | 362 |
| 137.1 | 368.2 |
| 138.2 | 374.7 |
| 137.6 | 378.4 |
| 137.1 | 378.3 |
| 136.9 | 382.2 |
| 136.7 | 384.8 |
| 136.7 | 387.5 |
| 137.3 | 388.5 |
| 136.9 | 389.2 |
| 137.1 | 392.6 |
| 137.4 | 401.3 |
| 136.1 | 405.2 |
| 137.1 | 405.8 |
| 137.5 | 405.4 |
| 137.5 | 410 |
| 138 | 412.5 |
| 137.6 | 416.2 |
| 138.1 | 421.2 |
| 138.3 | 423 |
| 137.4 | 423.6 |
| 137 | 421.4 |
| 136.8 | 422.1 |
| 136 | 421 |
| 136.9 | 421.6 |
| 136.7 | 424.7 |
| 137 | 429.4 |
| 136.7 | 430.8 |
| 136.7 | 433.9 |
| 136.8 | 435.7 |
| 135.8 | 439.6 |
| 136 | 442.5 |
| 136.8 | 447.5 |
| 136.6 | 450.6 |
| 136.2 | 448.7 |
| 137.1 | 451.1 |
| 136.3 | 453.3 |
| 135.9 | 456 |
| 136.6 | 453.7 |
| 137 | 455.5 |
| 136.7 | 458.3 |
| 137.1 | 463.3 |
| 136.9 | 461.7 |
| 136.3 | 467 |
| 136 | 467.7 |
| 136.5 | 469 |
| 137.6 | 469.6 |
| 137 | 473.1 |
| 136.5 | 472.3 |
| 137 | 476.7 |
| 136 | 482.5 |
| 135.4 | 490.3 |
| 135.9 | 491.6 |
| 135.3 | 487.1 |
| 136 | 489.4 |
| 136 | 490.4 |
| 135.6 | 493.6 |
| 135.3 | 492.7 |
| 137.1 | 495.3 |
| 137.2 | 496.1 |
| 137.1 | 493.8 |
| 135.8 | 492.6 |
| 135.7 | 489.7 |
| 136.7 | 491.1 |
| 135.6 | 488.8 |
| 135.9 | 484.9 |
| 136.2 | 490.9 |
| 135.7 | 485.5 |
| 135.9 | 482.4 |
| 135.3 | 485 |
| 135.6 | 482.8 |
| 136.2 | 485.2 |
| 136.7 | 484.7 |
| 135.9 | 483.3 |
| 135.5 | 490.8 |
| 134.4 | 492.5 |
| 134 | 493.8 |
| 134.6 | 494.5 |
| 134.9 | 499 |
| 136.3 | 497.7 |
| 136.5 | 497.7 |
| 136.6 | 499.9 |
| 136.6 | 500.5 |
| 136.2 | 506.5 |
| 136.5 | 511 |
| 136.7 | 513.3 |
| 136 | 521.6 |
| 136.2 | 523.4 |
| 135.9 | 523.7 |
| 135.8 | 527.9 |
| 136.2 | 528.8 |
| 136.7 | 529.9 |
| 136.6 | 531 |
| 136 | 533.3 |
| 136.5 | 530.6 |
| 137 | 533.2 |
| 136.2 | 535.8 |
| 135 | 538.1 |
| 135.4 | 542 |
| 136.4 | 544.3 |
| 135.3 | 548.7 |
| 135.2 | 548.1 |
| 135.9 | 555.5 |
| 134.8 | 562.6 |
| 135.8 | 566.4 |
| 136.2 | 570.3 |
| 135.7 | 566.9 |
| 134.9 | 566.7 |
| 134.8 | 564.2 |
| 134.8 | 568.5 |
| 135.2 | 573.3 |
| 136.1 | 573.9 |
| 135.5 | 571.6 |
| 135.9 | 577.8 |
| 135.2 | 578.1 |
| 135.9 | 577.7 |
| 136.1 | 578.1 |
| 136.5 | 574.4 |
| 136 | 574.1 |
| 135.3 | 573.3 |
| 136.4 | 573.2 |
| 137 | 575.2 |
| 136.2 | 578.7 |
| 135.5 | 579.3 |
| 135.7 | 580.1 |
| 135.9 | 580.9 |
| 136 | 583.1 |
| 135.4 | 585.2 |
| 134 | 585.1 |
| 135.2 | 589.5 |
| 135.8 | 591.9 |
| 136.2 | 588.6 |
| 136.1 | 590.9 |
| 135 | 594.4 |
| 136 | 597.9 |
| 135.2 | 604 |
| 135.5 | 606.5 |
| 135.9 | 612 |
| 136.3 | 613.9 |
| 135.4 | 610.2 |
| 135.5 | 613.2 |
| 136.4 | 617.7 |
| 135.7 | 625.3 |
| 135.7 | 622.6 |
| 134.9 | 620.1 |
| 133.8 | 619.6 |
| 135.6 | 616.8 |
| 136.4 | 618.2 |
| 134.8 | 617.7 |
| 134.7 | 616.4 |
| 134.7 | 614.7 |
| 136.1 | 609.6 |
| 136.2 | 609.1 |
| 135.7 | 605.6 |
| 135.3 | 607.6 |
| 135.4 | 603.6 |
| 134.6 | 606.7 |
| 135.2 | 610.5 |
| 135.7 | 610.6 |
| 135.3 | 618.9 |
| 135.3 | 620.8 |
| 134.9 | 620.6 |
| 135.1 | 624.1 |
| 134.8 | 629.2 |
| 135.1 | 632.8 |
| 135.3 | 631 |
| 135.3 | 631.3 |
| 134.9 | 626.2 |
| 135.6 | 627 |
| 135.5 | 629.1 |
| 136 | 629.3 |
| 134.8 | 637.1 |
| 135.3 | 641.9 |
| 135.1 | 640.3 |
| 134.7 | 635.4 |
| 135.6 | 634.5 |
| 136 | 631.5 |
| 135.4 | 631 |
| 135.5 | 633.8 |
| 135.4 | 635.8 |
| 135.7 | 640.4 |
| 135.2 | 641.1 |
| 135.1 | 639.6 |
| 135.8 | 638.4 |
| 135.1 | 639.7 |
| 135.1 | 641.7 |
| 135.7 | 648.1 |
| 135.9 | 646.8 |
| 135.4 | 649.2 |
| 135.3 | 649.4 |
| 135 | 652.4 |
| 135.4 | 652.7 |
| 135.4 | 653 |
| 135.4 | 651.3 |
| 134.9 | 653.7 |
| 135 | 654.4 |
| 134.8 | 654.1 |
| 135.9 | 651.1 |
| 135.2 | 647.3 |
| 135.5 | 645.5 |
| 135 | 643.2 |
| 134.7 | 646 |
| 134.8 | 648 |
| 135.1 | 649.7 |
| 135.1 | 652.1 |
| 135.4 | 655.9 |
| 135.2 | 657.5 |
| 134.3 | 656.4 |
| 134.5 | 658.7 |
| 135.2 | 662.7 |
| 134.6 | 663.7 |
| 135.1 | 660.3 |
| 135 | 657.6 |
| 135.9 | 656.4 |
| 135.9 | 654.9 |
| 135.4 | 656.9 |
| 134.8 | 663 |
| 135.5 | 662.9 |
| 134.8 | 664.4 |
| 134.3 | 665.3 |
| 135.8 | 666 |
| 135.5 | 674.5 |
| 134.7 | 673.1 |
| 135.3 | 675.6 |
| 135.1 | 681.1 |
| 135.1 | 683.5 |
| 134.9 | 683.4 |
| 134.8 | 683.2 |
| 134.4 | 684 |
| 134.6 | 685 |
| 135 | 688.1 |
| 134.2 | 687 |
| 135 | 686.3 |
| 134.3 | 684.1 |
| 135.2 | 680 |
| 135 | 676.5 |
| 135.3 | 672.2 |
| 134.4 | 674.4 |
| 134.7 | 677.3 |
| 135.1 | 677.3 |
| 135.2 | 673.9 |
| 134.9 | 675.7 |
| 134.9 | 672 |
| 134.6 | 670.8 |
| 135.4 | 672.6 |
| 134.8 | 669.7 |
| 134.9 | 672.3 |
| 135.2 | 668 |
| 135.5 | 667.7 |
| 135.3 | 671.4 |
| 134.5 | 673.6 |
| 134.4 | 673.8 |
| 135.1 | 670.7 |
| 135.8 | 668 |
| 134.8 | 665.3 |
| 134.1 | 666.4 |
| 134.4 | 665.8 |
| 134.7 | 669 |
| 135.2 | 672.1 |
| 133.7 | 670.7 |
| 134.3 | 675 |
| 134.3 | 672.7 |
| 133.5 | 676.5 |
| 135.1 | 679.9 |
| 134.6 | 677.2 |
| 134.4 | 677.1 |
| 134.3 | 677.6 |
| 134 | 675.2 |
| 134.1 | 677.4 |
| 133.8 | 679.1 |
| 133.6 | 687.7 |
| 133.8 | 687.9 |
| 134.8 | 689.1 |
| 134.1 | 684 |
| 134.7 | 686.7 |
| 134.9 | 681.7 |
| 134.6 | 681.7 |
| 134.8 | 680.4 |
| 134.9 | 679.2 |
| 134.7 | 679.3 |
| 134.6 | 680.5 |
| 134.5 | 679.8 |
| 134.6 | 682.9 |
| 134.2 | 687.3 |
| 134.5 | 690.1 |
| 134.9 | 689.6 |
| 134.1 | 688.8 |
| 134.5 | 688.5 |
| 134.1 | 689.7 |
| 133.5 | 691.5 |
| 132.3 | 691.4 |
| 133.4 | 689.9 |
| 133.7 | 692.9 |
| 134.4 | 691 |
| 134 | 696.6 |
| 133.3 | 694.5 |
| 133.8 | 694.6 |
| 132.9 | 695.5 |
| 132.5 | 696.3 |
| 133.6 | 695.4 |
| 134.1 | 695.1 |
| 134.5 | 699.2 |
| 133.5 | 703.2 |
| 133.3 | 707.3 |
| 133.2 | 708.4 |
| 133.7 | 707 |
| 133.9 | 708.2 |
| 134 | 705.4 |
| 133.7 | 708.1 |
| 132.8 | 709.6 |
| 133.1 | 715.5 |
| 133.5 | 716.3 |
| 134.3 | 719.3 |
| 134.6 | 720.1 |
| 133.9 | 720.9 |
| 133.4 | 715.9 |
| 134 | 713.1 |
| 134.4 | 711.4 |
| 133.9 | 713.3 |
| 133.8 | 718.2 |
| 134.5 | 720.9 |
| 134.2 | 725.2 |
| 135.2 | 730.2 |
| 134.5 | 728 |
| 135 | 729.7 |
| 134.8 | 728.3 |
| 134.2 | 732 |
| 134.4 | 733.4 |
| 134.3 | 734.8 |
| 134.7 | 734.7 |
| 134.8 | 734.2 |
| 134.3 | 732.6 |
| 134.5 | 732.7 |
| 133.7 | 740.9 |
| 134.3 | 740 |
| 133.2 | 748.3 |
| 133.9 | 734.4 |
| 133.5 | 719.2 |
| 133.2 | 736.8 |
| 134.3 | 742.8 |
| 134.2 | 761.9 |
| 134.4 | 778.4 |
| 133.5 | 784.4 |
| 133.3 | 796 |
| 133.3 | 815.1 |
| 133.5 | 816.2 |
| 132.6 | 825.7 |
| 133.2 | 824.1 |
| 133.6 | 824.5 |
| 133.6 | 834 |
| 133.3 | 812.8 |
| 132.8 | 828 |
| 133 | 832.2 |
| 133.6 | 840.1 |
| 132.8 | 840.5 |
| 133.4 | 852.9 |
| 133.6 | 849.8 |
| 132.8 | 836.8 |
| 134.8 | 840.8 |
| 132.8 | 871.8 |
| 133.6 | 867.6 |
| 132.6 | 887.3 |
| 133.3 | 902.8 |
| 134 | 901.1 |
| 132.8 | 904.1 |
| 133.8 | 920.6 |
| 133.7 | 920 |
| 133 | 922.8 |
| 133.9 | 935.4 |
| 133.7 | 929.9 |
| 133.4 | 936.4 |
| 133.6 | 951.7 |
| 133 | 956 |
| 133 | 955.5 |
| 133.4 | 974.4 |
| 133.5 | 997.2 |
| 133.9 | 995.8 |
| 133.7 | 1006 |
| 133.2 | 992.6 |
| 133.8 | 1004 |
| 133.8 | 996 |
| 132.1 | 1003 |
| 132.3 | 1005 |
| 133 | 1022 |
| 133.5 | 1007 |
| 134.1 | 1019 |
| 134 | 1015 |
| 133.2 | 1024 |
| 134.1 | 1038 |
| 133.5 | 1067 |
| 133.8 | 1065 |
| 134.2 | 1084 |
| 133.3 | 1101 |
| 133.2 | 1100 |
| 134.2 | 1109 |
| 134.4 | 1111 |
| 134.4 | 1112 |
| 133.5 | 1118 |
| 134.1 | 1128 |
| 134.3 | 1122 |
| 133.4 | 1120 |
| 133.8 | 1148 |
| 133.9 | 1168 |
| 133.9 | 1185 |
| 134.6 | 1177 |
| 133.4 | 1183 |
| 134.9 | 1195 |
| 134.3 | 1183 |
| 134.5 | 1172 |
| 135.1 | 1184 |
| 133.8 | 1208 |
| 134.3 | 1200 |
| 133.5 | 1197 |
| 134.2 | 1212 |
| 133 | 1217 |
| 134.3 | 1214 |
| 133.9 | 1215 |
| 134.6 | 1221 |
| 134.4 | 1228 |
| 134.3 | 1222 |
| 134.2 | 1229 |
| 134.4 | 1223 |
| 134 | 1236 |
| 134.4 | 1238 |
| 134.6 | 1251 |
| 134.4 | 1244 |
| 134.1 | 1261 |
| 134.2 | 1270 |
| 134.8 | 1277 |
| 133 | 1292 |
| 134.3 | 1293 |
| 134.6 | 1301 |
| 134.2 | 1321 |
| 134.4 | 1306 |
| 133.7 | 1334 |
| 133.8 | 1326 |
| 133.7 | 1327 |
| 134.3 | 1327 |
| 134.4 | 1328 |
| 134.1 | 1330 |
| 134.8 | 1352 |
| 134.7 | 1319 |
| 134.4 | 1334 |
| 134.3 | 1362 |
| 134.8 | 1354 |
| 134.5 | 1353 |
| 134 | 1348 |
| 133.8 | 1360 |
| 134.1 | 1346 |
| 134.2 | 1339 |
| 134.4 | 1340 |
| 134.4 | 1353 |
| 134 | 1341 |
| 134.6 | 1337 |
| 133.6 | 1362 |
| 134.3 | 1340 |
| 134.9 | 1322 |
| 134.9 | 1340 |
| 134.7 | 1333 |
| 133.9 | 1357 |
| 134.4 | 1360 |
| 133.8 | 1358 |
| 133.7 | 1369 |
| 134.3 | 1378 |
| 134.3 | 1371 |
| 134.5 | 1352 |
| 134.9 | 1352 |
| 133.7 | 1369 |
| 133.7 | 1383 |
| 133.1 | 1409 |
| 133.6 | 1413 |
| 133.8 | 1427 |
| 133.8 | 1416 |
| 134 | 1416 |
| 133.5 | 1395 |
| 134 | 1397 |
| 134.7 | 1387 |
| 133.9 | 1391 |
| 134.7 | 1418 |
| 134.1 | 1405 |
| 133.4 | 1434 |
| 133.6 | 1447 |
| 133.4 | 1467 |
| 134 | 1466 |
| 134.5 | 1468 |
| 134.3 | 1496 |
| 133.8 | 1492 |
| 134 | 1475 |
| 133.6 | 1487 |
| 134.1 | 1494 |
| 133.8 | 1479 |
| 134.3 | 1473 |
| 134.5 | 1472 |
| 134 | 1484 |
| 132.8 | 1476 |
| 134 | 1451 |
| 134.3 | 1440 |
| 134.1 | 1468 |
| 132.6 | 1472 |
| 134.6 | 1476 |
| 133.9 | 1491 |
| 133.9 | 1513 |
| 133.8 | 1504 |
| 133.6 | 1494 |
| 134.2 | 1462 |
| 134 | 1466 |
| 133.6 | 1480 |
| 133.5 | 1489 |
| 134.1 | 1485 |
| 134.4 | 1480 |
| 134.5 | 1483 |
| 134.1 | 1482 |
| 134.2 | 1477 |
| 133.3 | 1488 |
| 133.5 | 1500 |
| 133.7 | 1528 |
| 134.3 | 1505 |
| 133.9 | 1499 |
| 133.6 | 1499 |
| 133.9 | 1487 |
| 133.2 | 1479 |
| 133.9 | 1492 |
| 133.7 | 1504 |
| 133.8 | 1518 |
| 133.1 | 1523 |
| 133.3 | 1516 |
| 133.6 | 1513 |
| 133.6 | 1507 |
| 134.8 | 1532 |
| 133.7 | 1535 |
| 133.2 | 1534 |
| 133.3 | 1543 |
| 132.9 | 1565 |
| 133.7 | 1558 |
| 133.7 | 1560 |
| 134.2 | 1572 |
| 133.7 | 1569 |
| 134.3 | 1583 |
| 134.4 | 1603 |
| 134.2 | 1606 |
| 133.5 | 1632 |
| 134.1 | 1629 |
| 133.7 | 1641 |
| 133 | 1659 |
| 134.3 | 1653 |
| 133.9 | 1651 |
| 133.4 | 1674 |
| 133.5 | 1672 |
| 133.9 | 1679 |
| 133.8 | 1678 |
| 134 | 1692 |
| 133.8 | 1687 |
| 133.2 | 1677 |
| 133.3 | 1697 |
| 134 | 1701 |
| 134.2 | 1702 |
| 133.4 | 1732 |
| 133.3 | 1728 |
| 133.9 | 1711 |
| 134.1 | 1742 |
| 134.6 | 1749 |
| 133.9 | 1776 |
| 134 | 1779 |
| 134.4 | 1781 |
| 133.6 | 1776 |
| 134.5 | 1777 |
| 134.1 | 1808 |
| 134.5 | 1790 |
| 134.9 | 1784 |
| 134 | 1783 |
| 133.8 | 1790 |
| 134 | 1782 |
| 135 | 1800 |
| 134.3 | 1799 |
| 134.4 | 1810 |
| 133.9 | 1821 |
| 134.1 | 1814 |
| 133.7 | 1821 |
| 134.8 | 1789 |
| 134.1 | 1811 |
| 133.7 | 1794 |
| 133.4 | 1805 |
| 132.7 | 1819 |
| 133.7 | 1816 |
| 134.2 | 1825 |
| 135.1 | 1794 |
| 134.1 | 1805 |
| 134.1 | 1815 |
| 134.9 | 1822 |
| 134.5 | 1824 |
| 133.9 | 1853 |
| 133.1 | 1846 |
| 134.2 | 1855 |
| 133.7 | 1869 |
| 133.5 | 1876 |
| 133.6 | 1868 |
| 133.5 | 1856 |
| 135.5 | 1859 |
| 133.9 | 1845 |
| 133.9 | 1862 |
| 134.5 | 1895 |
| 134.5 | 1882 |
| 134.3 | 1913 |
| 133.9 | 1888 |
| 133.1 | 1899 |
| 134.4 | 1909 |
| 134.1 | 1899 |
| 133.6 | 1895 |
| 133.3 | 1907 |
| 134.2 | 1922 |
| 134.5 | 1909 |
| 134.2 | 1912 |
| 134 | 1917 |
| 134.2 | 1930 |
| 133.4 | 1959 |
| 134.7 | 1980 |
| 133.9 | 1961 |
| 133.8 | 1952 |
| 133.3 | 1962 |
| 134.2 | 1970 |
| 134.2 | 1960 |
| 133.4 | 1982 |
| 134.3 | 1968 |
| 134.2 | 1976 |
| 133.7 | 1969 |
| 133.5 | 1981 |
| 134.3 | 1988 |
| 134.8 | 1995 |
| 134 | 2022 |
| 134.8 | 2045 |
| 134.3 | 2051 |
| 134.9 | 2081 |
| 134.7 | 2057 |
| 134.3 | 2074 |
| 134.6 | 2053 |
| 133.5 | 2047 |
| 134.2 | 2052 |
| 134.7 | 2044 |
| 134.6 | 2050 |
| 134.3 | 2024 |
| 133.9 | 2031 |
| 133.6 | 2043 |
| 133.7 | 2060 |
| 134.3 | 2031 |
| 134.3 | 2041 |
| 133.6 | 2041 |
| 133.8 | 2039 |
| 133.5 | 2036 |
| 133.7 | 2048 |
| 134.7 | 2057 |
| 134.5 | 2040 |
| 132.5 | 2045 |
| 133.6 | 2051 |
| 133.5 | 2042 |
| 134.5 | 2074 |
| 134.2 | 2090 |
| 133.7 | 2070 |
| 132.8 | 2075 |
| 134.1 | 2093 |
| 133.3 | 2096 |
| 134.5 | 2104 |
| 133.4 | 2094 |
| 134.1 | 2101 |
| 133.3 | 2081 |
| 133.7 | 2072 |
| 132.8 | 2087 |
| 133.8 | 2118 |
| 134 | 2110 |
| 134 | 2116 |
| 134.5 | 2116 |
| 134 | 2098 |
| 134.3 | 2109 |
| 134.2 | 2108 |
| 133.3 | 2086 |
| 134.2 | 2098 |
| 134.6 | 2132 |
| 134 | 2144 |
| 133.5 | 2144 |
| 133.7 | 2178 |
| 134.5 | 2172 |
| 134.7 | 2172 |
| 134.1 | 2166 |
| 134.3 | 2169 |
| 133.4 | 2158 |
| 133.4 | 2150 |
| 133.7 | 2139 |
| 133.6 | 2156 |
| 133.8 | 2162 |
| 134.2 | 2179 |
| 134.6 | 2176 |
| 134.3 | 2212 |
| 133.4 | 2236 |
| 135.2 | 2253 |
| 134.4 | 2267 |
| 134.5 | 2282 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |


</details>

### `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222`

PE CG, film with a 3 nm-radius cylindrical hole at 25 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_25C.data`). Status: finished: `hole_ramp_rel130_failed_20261102` (failed, 0.0%), `hole_ramp_held_failed_20261102` (failed, 0.0%), `hole_free_failed_20261102` (failed, 0.0%), `hole_free`, `hole_ramp_rel130_d4`, `hole_ramp_rel130_col`, `hole_ramp_rel130`, `hole_ramp_held`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.5360 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_25C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_ramp_rel130_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_held_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_free`** (rdyu-server): finished; started 2026-11-02 20:16 UTC, ended 2026-11-07 06:28 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_rel130_d4`** (rdyu-server): finished; started 2026-11-06 14:44 UTC, ended 2026-11-12 02:42 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_rel130_col`** (rdyu-server): finished; started 2026-11-06 14:44 UTC, ended 2026-11-12 02:03 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_rel130`** (rdyu-rog): finished; started 2026-11-11 13:28 UTC, ended 2026-11-11 23:38 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_held`** (rdyu-rog): finished; started 2026-11-11 23:38 UTC, ended 2026-11-12 09:41 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_ramp_rel130_failed_20261102` (failed, 0.0%), `hole_ramp_held_failed_20261102` (failed, 0.0%), `hole_free_failed_20261102` (failed, 0.0%), `hole_free`, `hole_ramp_rel130_d4`, `hole_ramp_rel130_col`, `hole_ramp_rel130`, `hole_ramp_held` | `hole_free`, `hole_ramp_held`, `hole_ramp_rel130`, `hole_ramp_rel130_col`, `hole_ramp_rel130_d4` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 129.4
- `free_shell.areal_density_ratio`: 0.8879
- `free_shell.msd.1 ns`: 386.4
- `free_shell.msd.10 ns`: 1036
- `free_shell.msd.end`: 1383
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- T (°C): 25
- `t_close_ns`: 0.195
- `thickness_final`: 129.7
- `thickness_t0`: 162.6

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 129.8 | — |
| 129.6 | — |
| 130.2 | — |
| 130 | — |
| 130.2 | — |
| 129.5 | — |
| 129.8 | — |
| 129.5 | — |
| 129.8 | — |
| 129.7 | — |
| 130.1 | — |
| 129.7 | — |
| 129.4 | — |
| 130.1 | — |
| 130.3 | — |
| 129.4 | — |
| 129.9 | — |
| 128.9 | — |
| 129.6 | — |
| 129.2 | — |
| 129.6 | — |
| 129.3 | — |
| 129.8 | — |
| 129.8 | — |
| 130.2 | — |
| 130 | — |
| 129.5 | — |
| 129.7 | — |
| 129.6 | — |
| 129.8 | — |
| 129.5 | — |
| 129.7 | — |
| 129.7 | — |
| 130 | — |
| 130.5 | — |
| 130.1 | — |
| 130.6 | — |
| 130.2 | — |
| 130.7 | — |
| 130.5 | — |
| 131.3 | — |
| 131.2 | — |
| 130.9 | — |
| 130.7 | — |
| 130.9 | — |
| 131.5 | — |
| 131.3 | — |
| 131.5 | — |
| 131.6 | — |
| 132.2 | — |
| 131.5 | — |
| 131.7 | — |
| 132 | — |
| 131.7 | — |
| 132 | — |
| 132.1 | — |
| 132.6 | — |
| 132.6 | — |
| 132.1 | — |
| 132.4 | — |
| 132 | — |
| 132.5 | — |
| 132.2 | — |
| 132.4 | — |
| 132.2 | — |
| 132.7 | — |
| 132.6 | — |
| 133.6 | — |
| 133.2 | — |
| 133.3 | — |
| 133 | — |
| 133.4 | — |
| 133.1 | — |
| 133.4 | — |
| 133.3 | — |
| 133.4 | — |
| 134.1 | — |
| 133.9 | — |
| 134.2 | — |
| 134.7 | — |
| 134.5 | — |
| 134.4 | — |
| 135.1 | — |
| 135.3 | — |
| 134.9 | — |
| 135.8 | — |
| 135.7 | — |
| 134.8 | — |
| 135.3 | — |
| 135.7 | — |
| 134.9 | — |
| 135.4 | — |
| 135.7 | — |
| 136 | — |
| 136.9 | — |
| 137 | — |
| 137.1 | — |
| 136.9 | — |
| 137.4 | — |
| 137.8 | — |
| 137.2 | — |
| 137.3 | — |
| 137.4 | — |
| 137.4 | — |
| 137.9 | — |
| 137.9 | — |
| 138.2 | — |
| 139 | — |
| 139.1 | — |
| 138.6 | — |
| 139.1 | — |
| 139.4 | — |
| 139.8 | — |
| 139.4 | — |
| 140.8 | — |
| 140.3 | — |
| 139.3 | — |
| 140.2 | — |
| 139.8 | — |
| 140.9 | — |
| 140.5 | — |
| 140.7 | — |
| 140.9 | — |
| 141 | — |
| 141.2 | — |
| 141.4 | — |
| 141.9 | — |
| 141.7 | — |
| 142 | — |
| 142.4 | — |
| 142.5 | — |
| 142.3 | — |
| 142.5 | — |
| 142.9 | — |
| 143 | — |
| 142.9 | — |
| 144.2 | — |
| 143.8 | — |
| 144.4 | — |
| 144.4 | — |
| 144.3 | — |
| 145.2 | — |
| 145 | — |
| 144.7 | — |
| 145.5 | — |
| 145.4 | — |
| 145.6 | — |
| 146.1 | — |
| 146.6 | — |
| 147.3 | — |
| 147.2 | — |
| 147.6 | — |
| 146.7 | — |
| 147.3 | — |
| 147.3 | — |
| 147.4 | — |
| 147.9 | — |
| 148 | — |
| 148.3 | — |
| 148.7 | — |
| 148 | — |
| 148.8 | — |
| 149.2 | — |
| 149.4 | — |
| 150.1 | — |
| 149.2 | — |
| 149.4 | — |
| 150.7 | — |
| 151 | — |
| 151.2 | — |
| 150.4 | — |
| 150.9 | — |
| 151.9 | — |
| 152.1 | — |
| 153.4 | — |
| 153 | — |
| 153.5 | — |
| 153.1 | — |
| 153.7 | — |
| 153.6 | — |
| 154.8 | — |
| 154.9 | — |
| 154.3 | — |
| 155.4 | — |
| 155 | — |
| 156.3 | — |
| 156.2 | — |
| 156.5 | — |
| 156.8 | — |
| 157.2 | — |
| 158.6 | — |
| 158.8 | — |
| 158.2 | — |
| 157.7 | — |
| 158.6 | — |
| 160.4 | — |
| 160.2 | — |
| 160.7 | — |
| 161 | — |
| 160.6 | — |
| 160.5 | — |
| 161.5 | — |
| 161.8 | — |
| 161.8 | — |
| 161.2 | — |
| 161.6 | — |
| 159.8 | — |
| 161 | — |
| 161.6 | — |
| 160.5 | — |
| 162 | — |
| 161.4 | — |
| 161.4 | — |
| 161.3 | — |
| 161.1 | — |
| 160.3 | — |
| 160.7 | — |
| 160.9 | — |
| 161.1 | — |
| 161.1 | — |
| 161.6 | — |
| 161.7 | — |
| 161.4 | — |
| 160.9 | — |
| 160.8 | — |
| 161.1 | — |
| 160.5 | — |
| 161.3 | — |
| 161.8 | — |
| 160.3 | — |
| 160.7 | — |
| 161.2 | — |
| 159.5 | — |
| 159.9 | — |
| 160.1 | — |
| 162.1 | — |
| 161.7 | — |
| 162 | — |
| 161.1 | — |
| 161.6 | — |
| 161.9 | — |
| 161.5 | — |
| 163 | — |
| 162 | — |
| 161.1 | — |
| 161.2 | — |
| 162.2 | — |
| 163.1 | — |
| 162 | — |
| 162.8 | — |
| 161.3 | — |
| 162.1 | — |
| 162.9 | — |
| 162.4 | — |
| 160.5 | — |
| 162 | — |
| 162.9 | — |
| 161.6 | — |
| 162.1 | — |
| 161.5 | — |
| 162.2 | — |
| 162 | — |
| 160.8 | — |
| 161 | — |
| 160.8 | — |
| 161.7 | — |
| 161.1 | — |
| 163.1 | — |
| 161.6 | — |
| 161.4 | — |
| 160.6 | — |
| 161.6 | — |
| 160.8 | — |
| 160.9 | — |
| 160.6 | — |
| 160.3 | — |
| 161.7 | — |
| 161 | — |
| 161.8 | — |
| 162.3 | — |
| 161.2 | — |
| 160.6 | — |
| 161.5 | — |
| 161.6 | — |
| 161 | — |
| 160.9 | — |
| 161.3 | — |
| 161.6 | — |
| 161.6 | — |
| 160.9 | — |
| 161.9 | — |
| 162.1 | — |
| 161.9 | — |
| 161.4 | — |
| 162.6 | — |
| 162.7 | — |
| 162 | — |
| 161.5 | — |
| 161.7 | — |
| 161.2 | — |
| 162.9 | — |
| 162.1 | — |
| 161.7 | — |
| 162.3 | — |
| 162 | — |
| 161.5 | — |
| 162.5 | — |
| 162.4 | — |
| 161.6 | — |
| 163.6 | — |
| 162.3 | — |
| 161.8 | — |
| 161.3 | — |
| 161.7 | — |
| 161.6 | — |
| 161.1 | — |
| 162 | — |
| 163.1 | — |
| 161.9 | — |
| 161.9 | — |
| 161.9 | — |
| 161.6 | — |
| 161.6 | — |
| 161.9 | — |
| 161 | — |
| 161.2 | — |
| 161.1 | — |
| 161.1 | — |
| 162.3 | — |
| 161.5 | — |
| 161.3 | — |
| 162.5 | — |
| 162 | — |
| 161.8 | — |
| 161.3 | — |
| 161.5 | — |
| 161.4 | — |
| 162.8 | — |
| 162.8 | — |
| 162.7 | — |
| 162 | — |
| 161.8 | — |
| 162.2 | — |
| 162.4 | — |
| 161.3 | — |
| 161.5 | — |
| 162.7 | — |
| 163 | — |
| 162.9 | — |
| 162.2 | — |
| 161.3 | — |
| 163.5 | — |
| 162.1 | — |
| 162.3 | — |
| 161.4 | — |
| 160.4 | — |
| 162.7 | — |
| 161.2 | — |
| 161.8 | — |
| 161.2 | — |
| 162.5 | — |
| 160.9 | — |
| 162.4 | — |
| 162.8 | — |
| 161.1 | — |
| 163.2 | — |
| 162.4 | — |
| 163.6 | — |
| 161.7 | — |
| 161.4 | — |
| 161.9 | — |
| 162 | — |
| 160.5 | — |
| 161.5 | — |
| 162.9 | — |
| 162.3 | — |
| 161.8 | — |
| 162.5 | — |
| 161.3 | — |
| 163.1 | — |
| 162.7 | — |
| 161.8 | — |
| 161.5 | — |
| 162.2 | — |
| 160.5 | — |
| 160.4 | — |
| 161.2 | — |
| 162 | — |
| 162.5 | — |
| 159.9 | — |
| 160.8 | — |
| 160.4 | — |
| 160.9 | — |
| 161.6 | — |
| 161.1 | — |
| 160.8 | — |
| 160.1 | — |
| 161.6 | — |
| 161.8 | — |
| 161.1 | — |
| 162.6 | 0 |
| 161.7 | 9.174 |
| 160.1 | 14.54 |
| 159 | 21 |
| 157.4 | 27.68 |
| 155.2 | 31.56 |
| 155.4 | 34.28 |
| 155.6 | 37.72 |
| 154.8 | 41.42 |
| 153.3 | 45.65 |
| 153.8 | 50 |
| 153.1 | 55.57 |
| 152.6 | 60.26 |
| 152.7 | 64.22 |
| 151.4 | 66.9 |
| 152.1 | 70.42 |
| 151.4 | 73.47 |
| 150.6 | 77.16 |
| 150 | 80.89 |
| 149.1 | 85.4 |
| 148.8 | 91.09 |
| 148.7 | 94.48 |
| 147.8 | 98.32 |
| 148.2 | 102 |
| 147.6 | 105.7 |
| 146.6 | 110.8 |
| 146.3 | 114.2 |
| 145 | 118.6 |
| 145 | 123.3 |
| 145.3 | 127.8 |
| 144.8 | 134.3 |
| 143.6 | 141.1 |
| 142.6 | 147.2 |
| 142 | 152.3 |
| 141.4 | 157 |
| 141.3 | 161.8 |
| 140.9 | 167.9 |
| 140.4 | 171.8 |
| 139.9 | 178 |
| 139.5 | 186 |
| 139.1 | 193.2 |
| 138.1 | 200.7 |
| 137.9 | 202.6 |
| 136.9 | 205.5 |
| 136.9 | 211.3 |
| 137.6 | 215.1 |
| 137.2 | 217.2 |
| 136.5 | 226.8 |
| 135.6 | 229.1 |
| 135.3 | 228.8 |
| 135.5 | 229.3 |
| 135.1 | 230.5 |
| 135.3 | 232.5 |
| 135.2 | 234 |
| 134.8 | 234.8 |
| 134.9 | 236.7 |
| 135.4 | 239.1 |
| 135.9 | 240.7 |
| 134.3 | 239.9 |
| 134.7 | 246.9 |
| 134.6 | 249.1 |
| 133.9 | 252.7 |
| 134.4 | 251.4 |
| 133.3 | 253.5 |
| 134 | 255.3 |
| 134.1 | 254.5 |
| 134.1 | 259.3 |
| 133.7 | 259.3 |
| 134.2 | 259.6 |
| 133.7 | 260.3 |
| 134.4 | 259.5 |
| 133.9 | 262 |
| 133.7 | 263.9 |
| 133.9 | 263.1 |
| 133.8 | 264.5 |
| 133.5 | 267.9 |
| 132.9 | 268.4 |
| 133.1 | 271.4 |
| 133.5 | 271.7 |
| 133.7 | 271.1 |
| 133.3 | 275.5 |
| 133 | 276.7 |
| 132.9 | 278.3 |
| 133.2 | 279 |
| 133.5 | 281.1 |
| 133.3 | 283.9 |
| 132.9 | 283.6 |
| 133.7 | 286.9 |
| 133.7 | 287.1 |
| 133.1 | 290 |
| 133.3 | 291.9 |
| 133.3 | 295.4 |
| 133 | 296.9 |
| 133.6 | 296.5 |
| 133.4 | 299.3 |
| 133 | 301.5 |
| 133.2 | 302.9 |
| 133.2 | 306.1 |
| 133 | 310.3 |
| 132.4 | 311.4 |
| 132.3 | 312.7 |
| 132.7 | 312.2 |
| 132.2 | 314.1 |
| 132.6 | 317.2 |
| 132.5 | 315.1 |
| 132.9 | 310.2 |
| 132.8 | 315.6 |
| 132.3 | 316.4 |
| 132.4 | 318.1 |
| 131.9 | 319.3 |
| 132.5 | 319 |
| 131.5 | 323.1 |
| 132.3 | 321.4 |
| 132.5 | 320.9 |
| 132.2 | 323.3 |
| 132.4 | 327.6 |
| 132.2 | 327 |
| 132 | 325.6 |
| 132 | 324 |
| 132.1 | 329.3 |
| 132.3 | 331.3 |
| 131.8 | 333.5 |
| 132.1 | 334.8 |
| 132.4 | 338.2 |
| 131.7 | 337.2 |
| 132.4 | 339.1 |
| 132 | 338.5 |
| 131 | 342 |
| 130.9 | 341.4 |
| 131.4 | 340.9 |
| 131 | 341.4 |
| 131.3 | 342.2 |
| 131.1 | 342.6 |
| 131.3 | 344.1 |
| 131.2 | 343.6 |
| 131.2 | 344.6 |
| 131.5 | 346.7 |
| 130.7 | 346.4 |
| 131.7 | 347.6 |
| 131.3 | 349.1 |
| 131.2 | 350.5 |
| 130.6 | 352.3 |
| 131.1 | 354.7 |
| 130.9 | 359 |
| 131 | 360.7 |
| 130.8 | 356.5 |
| 132.1 | 355.3 |
| 131.7 | 355.8 |
| 131.7 | 360.5 |
| 131 | 366.3 |
| 131.5 | 362.7 |
| 132.1 | 362.4 |
| 131.7 | 365.9 |
| 131.3 | 366.8 |
| 131.9 | 365.7 |
| 131.9 | 361.8 |
| 131.9 | 361.5 |
| 131.8 | 363.4 |
| 132.2 | 366.2 |
| 131.3 | 366.7 |
| 131.2 | 369.3 |
| 132.3 | 367.8 |
| 132.8 | 367.3 |
| 131.9 | 366.7 |
| 132.4 | 366.1 |
| 132.2 | 365.2 |
| 131.3 | 366.4 |
| 131.6 | 368.3 |
| 131.4 | 370.9 |
| 132.4 | 368.5 |
| 132.3 | 372 |
| 132 | 374.6 |
| 131.6 | 372.8 |
| 131.5 | 371.8 |
| 131.7 | 370.4 |
| 131.7 | 375.9 |
| 131.7 | 376.7 |
| 131.7 | 376.7 |
| 132.3 | 377.3 |
| 132.5 | 375.9 |
| 131.7 | 375.7 |
| 131.1 | 375.4 |
| 131.2 | 375 |
| 131.3 | 375.9 |
| 131.2 | 377.9 |
| 131.6 | 380.5 |
| 131.9 | 381.4 |
| 131.9 | 383.1 |
| 131.4 | 383.2 |
| 131.3 | 384.3 |
| 131.4 | 387 |
| 132.3 | 386.3 |
| 132 | 387 |
| 131.9 | 386.6 |
| 131.6 | 387.8 |
| 131.9 | 387.9 |
| 131.9 | 384.3 |
| 131.6 | 384.7 |
| 132.1 | 386.3 |
| 131.8 | 387.3 |
| 131.5 | 386.4 |
| 131.6 | 391.8 |
| 131.4 | 390.6 |
| 131 | 394.2 |
| 131 | 392.7 |
| 131.5 | 394.8 |
| 132 | 395.9 |
| 131.7 | 398.9 |
| 131.3 | 400.9 |
| 131.3 | 403.9 |
| 131.7 | 403.3 |
| 131.7 | 400 |
| 131.6 | 400.1 |
| 132 | 399.6 |
| 132.1 | 398.1 |
| 132 | 402.2 |
| 131.9 | 405.9 |
| 131.4 | 409 |
| 131.7 | 410.2 |
| 131.4 | 409.1 |
| 131.9 | 407.7 |
| 131.4 | 405.7 |
| 131.6 | 405.4 |
| 131.6 | 406.3 |
| 132 | 408 |
| 131.9 | 409.2 |
| 131.7 | 410.8 |
| 131.8 | 412.6 |
| 131.4 | 413 |
| 131.8 | 412.4 |
| 131.4 | 415.3 |
| 131.6 | 417 |
| 132.2 | 416 |
| 131.9 | 417.8 |
| 131.6 | 419.1 |
| 130.8 | 422.3 |
| 131.5 | 422.6 |
| 131.8 | 422.5 |
| 131.5 | 420.1 |
| 131.7 | 420.1 |
| 131.4 | 422.7 |
| 132.1 | 420.5 |
| 131.6 | 422.2 |
| 131.5 | 423.8 |
| 131.5 | 425.4 |
| 131.2 | 425.2 |
| 131.2 | 422.2 |
| 131.9 | 421.5 |
| 131.3 | 418.6 |
| 131.7 | 425.4 |
| 130.5 | 428 |
| 131.6 | 429.3 |
| 131.8 | 429 |
| 131.6 | 430.3 |
| 131.6 | 434.2 |
| 130.7 | 437.3 |
| 131.8 | 437.3 |
| 131.5 | 437.3 |
| 130.7 | 438.2 |
| 130.6 | 440.1 |
| 131.4 | 435.4 |
| 131.2 | 437 |
| 131.8 | 439.8 |
| 131.1 | 440.3 |
| 131.8 | 439.9 |
| 131.2 | 437.8 |
| 132.1 | 437.5 |
| 132 | 437.7 |
| 131.9 | 439.1 |
| 131.5 | 442.3 |
| 131.6 | 438.8 |
| 131.1 | 442.1 |
| 131.1 | 441.4 |
| 131 | 444.4 |
| 130.8 | 447.7 |
| 131.2 | 451 |
| 130.6 | 452.3 |
| 131.8 | 451.3 |
| 132.2 | 451.3 |
| 131.1 | 454 |
| 130.8 | 453.5 |
| 132.2 | 450.9 |
| 131.1 | 450.3 |
| 131.2 | 453.4 |
| 131 | 455.3 |
| 132.2 | 456.9 |
| 131.7 | 457.6 |
| 130.4 | 458.3 |
| 130.3 | 460.9 |
| 130.7 | 459.8 |
| 131.5 | 460 |
| 130.9 | 462.7 |
| 130.7 | 464.3 |
| 130.6 | 460.5 |
| 131.9 | 457.7 |
| 131.7 | 458.7 |
| 130.7 | 463.8 |
| 130.6 | 460.3 |
| 130.3 | 462.6 |
| 131.1 | 464 |
| 130.9 | 466.7 |
| 130.1 | 466.4 |
| 130.8 | 464.9 |
| 130.9 | 462.5 |
| 131 | 463.5 |
| 129.8 | 464.8 |
| 130.1 | 467.8 |
| 130.9 | 463.2 |
| 130.4 | 464.1 |
| 130.1 | 465.7 |
| 130.5 | 462.6 |
| 130.5 | 461.4 |
| 130 | 462 |
| 130.3 | 463.4 |
| 130.3 | 464.6 |
| 130.2 | 468.2 |
| 131.3 | 465.4 |
| 130.9 | 467.8 |
| 130.7 | 470.2 |
| 130.6 | 470.4 |
| 130.6 | 469.3 |
| 131.5 | 471.8 |
| 130.9 | 473.8 |
| 131 | 477.9 |
| 130.6 | 484.5 |
| 130.3 | 487 |
| 130.4 | 487.2 |
| 130.5 | 487.8 |
| 130.7 | 483.5 |
| 131.9 | 487.4 |
| 130.8 | 488.1 |
| 130.7 | 489.7 |
| 130.4 | 489.7 |
| 130.6 | 490 |
| 130.4 | 493.4 |
| 130.6 | 494.7 |
| 130.2 | 493.6 |
| 130.6 | 491.7 |
| 130.6 | 492.1 |
| 130.2 | 494.2 |
| 130.5 | 495 |
| 130.6 | 495 |
| 130.3 | 494.6 |
| 130.4 | 492.3 |
| 130.4 | 493.3 |
| 129.9 | 494.9 |
| 129.7 | 496.8 |
| 129.8 | 494.9 |
| 129.9 | 494.6 |
| 130 | 491.7 |
| 130.5 | 490.5 |
| 130.8 | 490 |
| 131.2 | 490.3 |
| 130.3 | 490.4 |
| 130.3 | 490.6 |
| 130.1 | 492.1 |
| 130.1 | 492.4 |
| 129.8 | 491.3 |
| 130.3 | 487.8 |
| 130.6 | 490.4 |
| 130.5 | 491.8 |
| 130.4 | 491.2 |
| 130.2 | 488.1 |
| 130.7 | 492 |
| 130.2 | 492.8 |
| 130.8 | 490.2 |
| 130.1 | 490.7 |
| 130.8 | 491.7 |
| 129.9 | 495.4 |
| 130 | 498.9 |
| 129.7 | 500.9 |
| 131.2 | 498.8 |
| 130.8 | 497.3 |
| 130.9 | 498.1 |
| 130.3 | 501 |
| 130.8 | 501.4 |
| 130.9 | 504.8 |
| 131 | 501.6 |
| 131.1 | 503.2 |
| 130.6 | 503.6 |
| 130.3 | 504 |
| 130.3 | 504.9 |
| 130.3 | 505.2 |
| 130.6 | 505.4 |
| 131 | 506.1 |
| 130.2 | 510.1 |
| 129.9 | 510.3 |
| 129.9 | 508.2 |
| 130.6 | 508.9 |
| 130.5 | 508.4 |
| 130.4 | 504.8 |
| 130.4 | 505 |
| 130.4 | 505.7 |
| 130.4 | 508.2 |
| 130.3 | 510 |
| 130.5 | 506.5 |
| 130 | 505.8 |
| 130.5 | 504.5 |
| 130.5 | 505.6 |
| 129.9 | 511.2 |
| 130.2 | 514.6 |
| 130.5 | 516.6 |
| 130.2 | 515.2 |
| 130.4 | 520.3 |
| 130.1 | 531.2 |
| 130.9 | 533.7 |
| 130.8 | 538.9 |
| 130.1 | 545.9 |
| 130.7 | 561.6 |
| 130.4 | 557.2 |
| 130.5 | 553.1 |
| 131.1 | 563 |
| 131.2 | 566.3 |
| 130.1 | 578.9 |
| 130.2 | 574.4 |
| 130 | 578.1 |
| 130.3 | 600 |
| 129.8 | 604 |
| 130.2 | 610.7 |
| 130.3 | 606.9 |
| 130.4 | 614.9 |
| 129.9 | 613 |
| 130.1 | 614.9 |
| 130.2 | 631.7 |
| 130.2 | 642.4 |
| 130 | 644.6 |
| 130.7 | 636.8 |
| 130.4 | 642 |
| 129.9 | 646.4 |
| 129.8 | 657.2 |
| 130.5 | 655.7 |
| 129.9 | 657.8 |
| 130.5 | 661.1 |
| 130.1 | 675.2 |
| 129.4 | 670.6 |
| 130 | 674 |
| 130.2 | 676.4 |
| 129.6 | 678 |
| 129.8 | 684.7 |
| 129.7 | 693.4 |
| 130.1 | 690.4 |
| 130.2 | 696.4 |
| 130.1 | 702.6 |
| 129.8 | 700.3 |
| 129.6 | 716.2 |
| 130.2 | 717.4 |
| 130.2 | 701.3 |
| 129.3 | 713.9 |
| 130.3 | 704 |
| 130.3 | 717.3 |
| 129.7 | 720.3 |
| 130.1 | 717.4 |
| 129.8 | 726.5 |
| 129.9 | 728.1 |
| 130 | 712.7 |
| 130.1 | 727.7 |
| 129.8 | 721.2 |
| 129.9 | 737 |
| 129.3 | 739.8 |
| 129.5 | 736.9 |
| 129.7 | 742 |
| 130.2 | 744.3 |
| 131 | 747.2 |
| 129.9 | 756.3 |
| 129.6 | 752.6 |
| 130 | 746.4 |
| 129.8 | 760.2 |
| 129.9 | 750.5 |
| 129.9 | 767.1 |
| 130.4 | 774.3 |
| 130 | 775.5 |
| 130.1 | 791 |
| 129.7 | 801.7 |
| 129.9 | 793.3 |
| 129.6 | 797.5 |
| 130 | 798.3 |
| 130 | 805.5 |
| 129.3 | 811.4 |
| 129.6 | 810.1 |
| 130 | 818 |
| 130 | 828.9 |
| 130 | 838.3 |
| 130.1 | 844.3 |
| 129.8 | 840 |
| 130 | 836.7 |
| 130.1 | 845.8 |
| 130 | 838 |
| 130 | 838.7 |
| 129.4 | 836.2 |
| 130.2 | 833.3 |
| 129.8 | 825.5 |
| 129.5 | 828 |
| 129.7 | 852.6 |
| 129.7 | 849.9 |
| 129.8 | 848.4 |
| 129.4 | 857.9 |
| 129.3 | 860.9 |
| 129.3 | 868.7 |
| 129.7 | 878.6 |
| 129.6 | 865.5 |
| 129.6 | 873.3 |
| 129.5 | 875.7 |
| 129.2 | 872.8 |
| 129.6 | 883.9 |
| 129.5 | 880.1 |
| 129.5 | 880.8 |
| 129.5 | 888.4 |
| 129.6 | 894.1 |
| 129.5 | 889.7 |
| 129.7 | 895.8 |
| 129.1 | 903.9 |
| 129.6 | 915.6 |
| 130.3 | 907.3 |
| 129.1 | 905.9 |
| 129.2 | 906.5 |
| 129.1 | 903.1 |
| 129.7 | 898.2 |
| 129.7 | 905.5 |
| 129.1 | 903.7 |
| 130.1 | 914.6 |
| 129.3 | 918 |
| 129.4 | 929.3 |
| 129.7 | 929.6 |
| 129.8 | 927.1 |
| 129.2 | 939.5 |
| 129.6 | 938.7 |
| 129.3 | 941.4 |
| 129.4 | 940.1 |
| 129.2 | 928.8 |
| 129.4 | 937 |
| 128.8 | 928.6 |
| 129.9 | 928.5 |
| 129.8 | 946 |
| 129.5 | 952.1 |
| 129.9 | 934.1 |
| 129.5 | 940.7 |
| 129.6 | 941.7 |
| 129.3 | 942.5 |
| 129 | 964.8 |
| 129.1 | 968 |
| 129.3 | 962.8 |
| 129.9 | 976.6 |
| 129.8 | 974.4 |
| 129.3 | 985.9 |
| 129.8 | 986.5 |
| 129.5 | 992.2 |
| 129.4 | 1003 |
| 129.8 | 983.5 |
| 129.9 | 1000 |
| 129.6 | 999 |
| 129.7 | 985.9 |
| 129.4 | 1001 |
| 129.9 | 1004 |
| 129.8 | 1006 |
| 129.6 | 1014 |
| 129.5 | 1014 |
| 129.4 | 1012 |
| 129 | 1023 |
| 129.7 | 1027 |
| 130 | 1040 |
| 129.5 | 1036 |
| 129.7 | 1039 |
| 129.4 | 1056 |
| 129.9 | 1039 |
| 129.7 | 1048 |
| 129.7 | 1036 |
| 130.1 | 1044 |
| 130 | 1047 |
| 129.6 | 1047 |
| 129.9 | 1051 |
| 130 | 1058 |
| 130.3 | 1050 |
| 130.2 | 1035 |
| 129.9 | 1048 |
| 130.7 | 1058 |
| 130.1 | 1058 |
| 129.8 | 1055 |
| 129.9 | 1065 |
| 130 | 1048 |
| 129.6 | 1053 |
| 129.4 | 1070 |
| 129.5 | 1071 |
| 129.6 | 1074 |
| 129.4 | 1080 |
| 130 | 1073 |
| 129.4 | 1078 |
| 129.7 | 1072 |
| 129.7 | 1079 |
| 129.7 | 1078 |
| 129.7 | 1078 |
| 129.4 | 1091 |
| 129.8 | 1092 |
| 129.6 | 1108 |
| 129.4 | 1098 |
| 129.8 | 1100 |
| 129.8 | 1101 |
| 130 | 1114 |
| 129.4 | 1108 |
| 129.4 | 1096 |
| 129.7 | 1097 |
| 129.4 | 1090 |
| 129.6 | 1089 |
| 129.6 | 1105 |
| 129.6 | 1095 |
| 129.4 | 1112 |
| 129.1 | 1115 |
| 129.2 | 1123 |
| 129.6 | 1105 |
| 129.4 | 1099 |
| 129.8 | 1095 |
| 129.7 | 1108 |
| 129.5 | 1106 |
| 129.6 | 1109 |
| 129.7 | 1119 |
| 130.3 | 1107 |
| 130.1 | 1125 |
| 129.3 | 1128 |
| 129.9 | 1124 |
| 129.6 | 1114 |
| 129.6 | 1112 |
| 130.1 | 1128 |
| 129.8 | 1119 |
| 130.3 | 1109 |
| 129.5 | 1101 |
| 130 | 1108 |
| 129.8 | 1104 |
| 129.6 | 1101 |
| 129.4 | 1097 |
| 130 | 1097 |
| 129.9 | 1095 |
| 129.3 | 1097 |
| 130 | 1101 |
| 130.2 | 1117 |
| 129.7 | 1121 |
| 130.2 | 1123 |
| 129.8 | 1121 |
| 128.7 | 1109 |
| 129.9 | 1108 |
| 129.5 | 1126 |
| 128.9 | 1130 |
| 129.5 | 1134 |
| 129.4 | 1146 |
| 130 | 1147 |
| 129.5 | 1153 |
| 129.8 | 1147 |
| 129.9 | 1150 |
| 130 | 1162 |
| 129.8 | 1172 |
| 129.9 | 1173 |
| 129.9 | 1183 |
| 129.9 | 1176 |
| 129.6 | 1177 |
| 130.1 | 1182 |
| 129.8 | 1181 |
| 129.8 | 1182 |
| 129.7 | 1169 |
| 130 | 1170 |
| 130.2 | 1165 |
| 129.9 | 1171 |
| 129.8 | 1166 |
| 130.1 | 1161 |
| 129.7 | 1156 |
| 129.9 | 1161 |
| 129.4 | 1160 |
| 129.6 | 1165 |
| 129.4 | 1177 |
| 129.6 | 1184 |
| 129.9 | 1196 |
| 129.8 | 1197 |
| 130.2 | 1192 |
| 129.5 | 1198 |
| 130 | 1197 |
| 129.6 | 1197 |
| 129.7 | 1206 |
| 129.5 | 1203 |
| 129.5 | 1203 |
| 129.8 | 1198 |
| 129.3 | 1188 |
| 129.9 | 1192 |
| 129.6 | 1191 |
| 129.7 | 1186 |
| 129.7 | 1195 |
| 129.7 | 1204 |
| 129.7 | 1199 |
| 129.6 | 1209 |
| 129.6 | 1204 |
| 129.6 | 1200 |
| 129.3 | 1210 |
| 129.4 | 1207 |
| 129.7 | 1205 |
| 129.5 | 1216 |
| 129.4 | 1216 |
| 129.7 | 1217 |
| 129.8 | 1222 |
| 129.6 | 1214 |
| 129.7 | 1220 |
| 129.6 | 1228 |
| 130.1 | 1230 |
| 130 | 1240 |
| 130 | 1236 |
| 130.1 | 1243 |
| 129.2 | 1253 |
| 130.4 | 1244 |
| 130 | 1266 |
| 130.2 | 1260 |
| 130.2 | 1271 |
| 129.6 | 1264 |
| 129.6 | 1267 |
| 130.2 | 1276 |
| 130 | 1268 |
| 130.6 | 1279 |
| 130 | 1295 |
| 130 | 1288 |
| 130.4 | 1288 |
| 129.9 | 1304 |
| 130 | 1295 |
| 129.7 | 1292 |
| 130.4 | 1288 |
| 129.8 | 1298 |
| 129.7 | 1302 |
| 129.6 | 1303 |
| 130 | 1300 |
| 130.2 | 1303 |
| 129.7 | 1303 |
| 130.1 | 1304 |
| 129.5 | 1301 |
| 129.9 | 1301 |
| 130.4 | 1296 |
| 129.5 | 1295 |
| 129.6 | 1303 |
| 129.8 | 1295 |
| 129.3 | 1310 |
| 129.6 | 1304 |
| 129.2 | 1327 |
| 129.5 | 1318 |
| 129.8 | 1329 |
| 129.3 | 1334 |
| 129.6 | 1340 |
| 129.5 | 1337 |
| 129.5 | 1324 |
| 130.1 | 1318 |
| 130.3 | 1317 |
| 129.9 | 1325 |
| 129.7 | 1334 |
| 129.4 | 1343 |
| 129.8 | 1343 |
| 129.9 | 1350 |
| 129.6 | 1355 |
| 130 | 1355 |
| 129.9 | 1359 |
| 129.9 | 1358 |
| 129.3 | 1351 |
| 130 | 1356 |
| 130 | 1371 |
| 129.5 | 1368 |
| 129.2 | 1366 |
| 129.8 | 1368 |
| 129.6 | 1370 |
| 129.6 | 1373 |
| 129.9 | 1380 |
| 129.7 | 1383 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 25 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 25 |


**`hole_ramp_held` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 129.4
- `free_shell.areal_density_ratio`: 0.889
- `free_shell.msd.1 ns`: 66.83
- `free_shell.msd.10 ns`: 273.8
- `free_shell.msd.end`: 845
- `free_shell.msd.end_ns`: 68
- `params.hole_hold_ps`: 1e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `scaffold.d_nm`: 2.5
- `scaffold.nearest_tethered_r_held_min`: 53.08
- `scaffold.nearest_tethered_r_t0`: 55
- `scaffold.tethered_fraction`: 0.5394
- T (°C): 25
- `t_close_ns`: 25.6
- `thickness_final`: 162.3
- `thickness_t0`: 162.4

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 129.8 | — |
| 129.3 | — |
| 129.7 | — |
| 129.7 | — |
| 129.8 | — |
| 129.8 | — |
| 130 | — |
| 129.8 | — |
| 130.2 | — |
| 129.9 | — |
| 129.5 | — |
| 130.3 | — |
| 129.9 | — |
| 130.1 | — |
| 130.1 | — |
| 129.6 | — |
| 129.7 | — |
| 129.7 | — |
| 129.9 | — |
| 129.9 | — |
| 129.7 | — |
| 129.9 | — |
| 130.2 | — |
| 129.8 | — |
| 129.9 | — |
| 129.7 | — |
| 129.5 | — |
| 129.4 | — |
| 128.9 | — |
| 129.2 | — |
| 130.2 | — |
| 129.6 | — |
| 129.3 | — |
| 130 | — |
| 129.4 | — |
| 129.8 | — |
| 129.4 | — |
| 129.7 | — |
| 129.7 | — |
| 129.7 | — |
| 129.9 | — |
| 129.3 | — |
| 129.5 | — |
| 130.2 | — |
| 129.5 | — |
| 129.8 | — |
| 129.3 | — |
| 129.2 | — |
| 129.4 | — |
| 129.6 | — |
| 129.9 | — |
| 130 | — |
| 129.8 | — |
| 129.3 | — |
| 129.9 | — |
| 129.7 | — |
| 129.5 | — |
| 130.1 | — |
| 129.8 | — |
| 129.5 | — |
| 130.4 | — |
| 129.9 | — |
| 130 | — |
| 129.8 | — |
| 129.9 | — |
| 130.2 | — |
| 129.9 | — |
| 129.9 | — |
| 130.1 | — |
| 129.5 | — |
| 130.5 | — |
| 129.9 | — |
| 130.5 | — |
| 130.3 | — |
| 130.5 | — |
| 129.9 | — |
| 130.5 | — |
| 131.2 | — |
| 130.5 | — |
| 130.4 | — |
| 130.5 | — |
| 130.5 | — |
| 131.1 | — |
| 131.3 | — |
| 131.5 | — |
| 130.2 | — |
| 130.6 | — |
| 130.8 | — |
| 131.4 | — |
| 131.4 | — |
| 131.5 | — |
| 131.4 | — |
| 131 | — |
| 131.8 | — |
| 131.2 | — |
| 131.2 | — |
| 131.3 | — |
| 131.8 | — |
| 131.7 | — |
| 132 | — |
| 131.7 | — |
| 131.6 | — |
| 131.6 | — |
| 131.8 | — |
| 131.9 | — |
| 132.2 | — |
| 132.4 | — |
| 131.7 | — |
| 132 | — |
| 132.6 | — |
| 132.5 | — |
| 132.9 | — |
| 132.2 | — |
| 132.7 | — |
| 132.3 | — |
| 132.4 | — |
| 132.5 | — |
| 132.3 | — |
| 132.2 | — |
| 132.7 | — |
| 132.1 | — |
| 132 | — |
| 133 | — |
| 132 | — |
| 132.5 | — |
| 132.9 | — |
| 133 | — |
| 132.7 | — |
| 132.4 | — |
| 132.8 | — |
| 132.9 | — |
| 133.6 | — |
| 133 | — |
| 133.4 | — |
| 133.4 | — |
| 133.7 | — |
| 133.4 | — |
| 133.8 | — |
| 133.3 | — |
| 133.9 | — |
| 133.7 | — |
| 134.2 | — |
| 134 | — |
| 133.8 | — |
| 133.7 | — |
| 133.6 | — |
| 133.6 | — |
| 134.7 | — |
| 133.8 | — |
| 134.6 | — |
| 134.2 | — |
| 134.5 | — |
| 133.4 | — |
| 134.1 | — |
| 133.9 | — |
| 134 | — |
| 133.9 | — |
| 134.5 | — |
| 135 | — |
| 134.6 | — |
| 134.1 | — |
| 134.9 | — |
| 135.4 | — |
| 135 | — |
| 135.2 | — |
| 135.5 | — |
| 135.8 | — |
| 135.1 | — |
| 134.6 | — |
| 135.5 | — |
| 135.3 | — |
| 135.7 | — |
| 134.9 | — |
| 135.1 | — |
| 136.1 | — |
| 136.1 | — |
| 136 | — |
| 135.3 | — |
| 135.4 | — |
| 136.1 | — |
| 136.9 | — |
| 136.8 | — |
| 136.1 | — |
| 136.7 | — |
| 136.5 | — |
| 136.9 | — |
| 137.1 | — |
| 137 | — |
| 136.5 | — |
| 137.1 | — |
| 137.3 | — |
| 137.2 | — |
| 137.1 | — |
| 137.3 | — |
| 136.7 | — |
| 137 | — |
| 137.2 | — |
| 137.2 | — |
| 136.6 | — |
| 137.9 | — |
| 137.2 | — |
| 137.5 | — |
| 137.1 | — |
| 137.6 | — |
| 138.2 | — |
| 137.7 | — |
| 138.5 | — |
| 138.3 | — |
| 138.8 | — |
| 137.9 | — |
| 138.1 | — |
| 138.2 | — |
| 138.1 | — |
| 138.4 | — |
| 139.4 | — |
| 139.4 | — |
| 139.2 | — |
| 138.6 | — |
| 139 | — |
| 139.4 | — |
| 139.1 | — |
| 139.2 | — |
| 139.9 | — |
| 139.1 | — |
| 139 | — |
| 139.4 | — |
| 140.1 | — |
| 140.1 | — |
| 139.1 | — |
| 140.2 | — |
| 141 | — |
| 140.9 | — |
| 141 | — |
| 140.8 | — |
| 140.5 | — |
| 140.1 | — |
| 140.9 | — |
| 140.9 | — |
| 140.6 | — |
| 140.6 | — |
| 140.4 | — |
| 141.6 | — |
| 140.9 | — |
| 142.2 | — |
| 141 | — |
| 141.3 | — |
| 140.9 | — |
| 141.5 | — |
| 140.8 | — |
| 141.6 | — |
| 141.1 | — |
| 141.8 | — |
| 142.2 | — |
| 141.9 | — |
| 142.7 | — |
| 141.8 | — |
| 142.1 | — |
| 142.4 | — |
| 143.2 | — |
| 141.6 | — |
| 141.3 | — |
| 142.1 | — |
| 142.5 | — |
| 141.8 | — |
| 142.5 | — |
| 143.3 | — |
| 143.6 | — |
| 143.6 | — |
| 144.3 | — |
| 144.3 | — |
| 144.1 | — |
| 143.5 | — |
| 144.4 | — |
| 143.9 | — |
| 144.5 | — |
| 144.3 | — |
| 144.9 | — |
| 144.8 | — |
| 144.3 | — |
| 144.4 | — |
| 145.6 | — |
| 145.3 | — |
| 144.6 | — |
| 145.5 | — |
| 145.4 | — |
| 145.7 | — |
| 145.4 | — |
| 145.7 | — |
| 146.6 | — |
| 146.6 | — |
| 146.5 | — |
| 146.8 | — |
| 146.4 | — |
| 147.5 | — |
| 146.7 | — |
| 146.3 | — |
| 147.1 | — |
| 147.8 | — |
| 148 | — |
| 147.6 | — |
| 147.5 | — |
| 147.9 | — |
| 148.3 | — |
| 148.3 | — |
| 148.3 | — |
| 148.9 | — |
| 148.5 | — |
| 148.6 | — |
| 148.5 | — |
| 147.9 | — |
| 148.8 | — |
| 147.9 | — |
| 148.7 | — |
| 148.8 | — |
| 148.7 | — |
| 149.2 | — |
| 149.6 | — |
| 149.6 | — |
| 149.4 | — |
| 149.4 | — |
| 149.3 | — |
| 149.1 | — |
| 150.1 | — |
| 149.7 | — |
| 150 | — |
| 150.7 | — |
| 150.1 | — |
| 150.9 | — |
| 150.7 | — |
| 150.3 | — |
| 151.6 | — |
| 151.8 | — |
| 151.8 | — |
| 151.6 | — |
| 152.7 | — |
| 152.6 | — |
| 152.2 | — |
| 153 | — |
| 153.2 | — |
| 153.3 | — |
| 153.5 | — |
| 153.2 | — |
| 153 | — |
| 152.5 | — |
| 154 | — |
| 153.9 | — |
| 152.8 | — |
| 153.6 | — |
| 154.3 | — |
| 154.2 | — |
| 153.9 | — |
| 153.4 | — |
| 154.2 | — |
| 154.1 | — |
| 154.7 | — |
| 154.7 | — |
| 154.5 | — |
| 155 | — |
| 155.3 | — |
| 154.9 | — |
| 155.9 | — |
| 155.3 | — |
| 155 | — |
| 155.7 | — |
| 155 | — |
| 156.8 | — |
| 156.2 | — |
| 157 | — |
| 155.9 | — |
| 156.6 | — |
| 156.9 | — |
| 156 | — |
| 156.4 | — |
| 155.9 | — |
| 156.6 | — |
| 157.3 | — |
| 157.3 | — |
| 158.2 | — |
| 158.3 | — |
| 158.2 | — |
| 158.5 | — |
| 159 | — |
| 157.7 | — |
| 158.6 | — |
| 158.8 | — |
| 160.5 | — |
| 159.1 | — |
| 159.5 | — |
| 159.9 | — |
| 159.4 | — |
| 159.4 | — |
| 160.5 | — |
| 159.2 | — |
| 160 | — |
| 160.2 | — |
| 161 | — |
| 159.9 | — |
| 162.8 | — |
| 161.7 | — |
| 161.7 | — |
| 160.9 | — |
| 161 | — |
| 161.6 | — |
| 162.5 | — |
| 162.1 | — |
| 161.8 | — |
| 162.1 | — |
| 162.8 | — |
| 161.6 | — |
| 162.1 | — |
| 162.4 | — |
| 162.1 | — |
| 161 | — |
| 161.8 | — |
| 161.8 | — |
| 161.9 | — |
| 161.1 | — |
| 161.2 | — |
| 160.1 | — |
| 160.5 | — |
| 160.9 | — |
| 161.2 | — |
| 160.4 | — |
| 160.4 | — |
| 162.1 | — |
| 161.5 | — |
| 161.7 | — |
| 162 | — |
| 162.6 | — |
| 163.1 | — |
| 162.6 | — |
| 162.5 | — |
| 162 | — |
| 161.6 | — |
| 160.8 | — |
| 161.6 | — |
| 161.3 | — |
| 161.2 | — |
| 162.3 | — |
| 161.6 | — |
| 162.6 | — |
| 161 | — |
| 162.1 | — |
| 161.3 | — |
| 161.5 | — |
| 161.8 | — |
| 161.5 | — |
| 162 | — |
| 161.4 | — |
| 162.3 | — |
| 161.7 | — |
| 161.4 | — |
| 161.9 | — |
| 162.3 | — |
| 162.8 | — |
| 162.1 | — |
| 161.8 | — |
| 162.2 | — |
| 162.7 | — |
| 162.6 | — |
| 163.3 | — |
| 161.9 | — |
| 162.7 | — |
| 161.1 | — |
| 161.6 | — |
| 161.5 | — |
| 161.6 | — |
| 162.1 | — |
| 162.2 | — |
| 162.5 | — |
| 161.1 | — |
| 162.1 | — |
| 160.8 | — |
| 163.3 | — |
| 161.6 | — |
| 162 | — |
| 161.8 | — |
| 162.4 | — |
| 161.5 | — |
| 162.5 | — |
| 161.8 | — |
| 162.6 | — |
| 162.7 | — |
| 163.1 | — |
| 162.4 | — |
| 162.8 | — |
| 163.4 | — |
| 163.2 | — |
| 162 | — |
| 161.6 | — |
| 162.1 | — |
| 162 | — |
| 162.2 | — |
| 163 | — |
| 163.1 | — |
| 162.1 | — |
| 161.6 | — |
| 163.9 | — |
| 163.7 | — |
| 162.4 | — |
| 163 | — |
| 163.3 | — |
| 162 | — |
| 162 | — |
| 161.2 | — |
| 160.9 | — |
| 161.3 | — |
| 161.8 | — |
| 162.7 | — |
| 163.3 | — |
| 163.1 | — |
| 161.6 | — |
| 163.1 | — |
| 161.8 | — |
| 162.8 | — |
| 162.9 | — |
| 163.3 | — |
| 162 | — |
| 163.3 | — |
| 162.4 | — |
| 161.9 | — |
| 162.7 | — |
| 161.6 | — |
| 161.5 | — |
| 161.5 | — |
| 162 | — |
| 163 | — |
| 162.2 | — |
| 161.4 | — |
| 164.4 | — |
| 163.5 | — |
| 161.3 | — |
| 162.8 | — |
| 161.7 | — |
| 163 | — |
| 162.6 | — |
| 162.1 | — |
| 161.8 | — |
| 162.7 | — |
| 161.9 | — |
| 161.3 | — |
| 161.9 | — |
| 161.7 | — |
| 160.6 | — |
| 162 | — |
| 162.1 | — |
| 163.1 | — |
| 162.5 | — |
| 161.6 | — |
| 162.2 | — |
| 162 | — |
| 161.8 | — |
| 163 | — |
| 161.9 | — |
| 162.8 | — |
| 161.9 | — |
| 161.7 | — |
| 162.7 | — |
| 161.4 | — |
| 161.9 | — |
| 161.8 | — |
| 161.4 | — |
| 161.3 | — |
| 161.4 | — |
| 161.3 | — |
| 161.1 | — |
| 161 | — |
| 162.4 | — |
| 161.7 | — |
| 161.6 | — |
| 161.9 | — |
| 161.4 | — |
| 161.7 | — |
| 162 | — |
| 162.1 | — |
| 161.2 | — |
| 161.9 | — |
| 161.6 | — |
| 161.5 | — |
| 161.3 | — |
| 161.4 | — |
| 160.9 | — |
| 161.5 | — |
| 161.3 | — |
| 161.2 | — |
| 160.9 | — |
| 162.2 | — |
| 160.9 | — |
| 161.7 | — |
| 161.5 | — |
| 161.7 | — |
| 160.4 | — |
| 163.6 | — |
| 162.6 | — |
| 161.9 | — |
| 161.9 | — |
| 162.2 | — |
| 161.8 | — |
| 161.6 | — |
| 162.3 | — |
| 162.4 | 0 |
| 162.3 | 6.914 |
| 162 | 9.561 |
| 161.9 | 10.64 |
| 162 | 11.84 |
| 162.1 | 12.02 |
| 162 | 12.63 |
| 162.2 | 13.71 |
| 162.2 | 15.32 |
| 162.3 | 15.79 |
| 162 | 16.74 |
| 162.2 | 17.45 |
| 162 | 18.26 |
| 162.1 | 19.57 |
| 162.1 | 19.69 |
| 161.9 | 19.93 |
| 162.4 | 20.32 |
| 161.9 | 20.94 |
| 162.3 | 21.5 |
| 162.2 | 22.76 |
| 162.3 | 23.41 |
| 162 | 24.1 |
| 161.9 | 24.65 |
| 161.8 | 25.12 |
| 161.7 | 26.29 |
| 162.3 | 26.76 |
| 161.8 | 27.08 |
| 162 | 27.41 |
| 162.2 | 27.83 |
| 162.1 | 28.22 |
| 161.8 | 28.63 |
| 161.9 | 29.91 |
| 162 | 30.52 |
| 161.8 | 30.83 |
| 162 | 31.96 |
| 162.3 | 31.28 |
| 161.8 | 32.51 |
| 162 | 32.25 |
| 162 | 31.74 |
| 162 | 31.44 |
| 162.2 | 31.67 |
| 162.2 | 32.55 |
| 161.9 | 32.24 |
| 162.1 | 32.71 |
| 161.9 | 33.14 |
| 161.9 | 33.93 |
| 162.1 | 34.12 |
| 162.2 | 33.87 |
| 162.3 | 33.56 |
| 161.9 | 33.61 |
| 161.7 | 33.01 |
| 162 | 33.58 |
| 162.2 | 34.24 |
| 161.7 | 34.05 |
| 162 | 34.57 |
| 161.5 | 34.84 |
| 161.9 | 34.76 |
| 162.1 | 35.6 |
| 162 | 35.32 |
| 161.7 | 34.97 |
| 162 | 35.64 |
| 161.8 | 35.92 |
| 162.1 | 35.87 |
| 162 | 36.21 |
| 162 | 35.84 |
| 161.9 | 35.45 |
| 162.2 | 35.76 |
| 162.2 | 36.43 |
| 161.9 | 37.24 |
| 162 | 37.69 |
| 162 | 37.79 |
| 162.4 | 38.65 |
| 162.1 | 38.5 |
| 162.2 | 38.68 |
| 162 | 38.18 |
| 161.8 | 39.73 |
| 162 | 39.79 |
| 162.1 | 39.56 |
| 162.1 | 39.55 |
| 161.9 | 40.04 |
| 162.3 | 39.45 |
| 162.1 | 39.12 |
| 162.1 | 38.77 |
| 161.9 | 39.15 |
| 162.4 | 39.15 |
| 162 | 40.05 |
| 162 | 40.76 |
| 162.1 | 40.77 |
| 161.9 | 39.97 |
| 162 | 40.54 |
| 161.9 | 41.46 |
| 161.9 | 42.99 |
| 162.2 | 43.53 |
| 162 | 44.01 |
| 161.9 | 43.64 |
| 162.1 | 43.1 |
| 162.3 | 42.77 |
| 162 | 41.93 |
| 161.8 | 42.27 |
| 161.8 | 43.09 |
| 162.4 | 44.48 |
| 161.9 | 44.34 |
| 161.8 | 44.75 |
| 162.1 | 45.62 |
| 162.2 | 47.05 |
| 162 | 48.79 |
| 161.5 | 49.12 |
| 162 | 49.74 |
| 161.6 | 48.79 |
| 162.1 | 49.68 |
| 161.9 | 49.21 |
| 161.7 | 49.45 |
| 161.8 | 49.26 |
| 161.9 | 49.83 |
| 162 | 48.48 |
| 162.1 | 49.34 |
| 161.8 | 49.46 |
| 161.6 | 50.09 |
| 161.7 | 50.13 |
| 161.8 | 51.01 |
| 161.7 | 50.28 |
| 161.8 | 50.8 |
| 161.6 | 50.42 |
| 162 | 50.61 |
| 161.8 | 51.9 |
| 161.8 | 51.34 |
| 161.7 | 52.98 |
| 161.7 | 52.98 |
| 161.9 | 53.24 |
| 162 | 54.71 |
| 161.5 | 53.92 |
| 161.7 | 53.31 |
| 161.5 | 52.99 |
| 161.7 | 54.38 |
| 161.6 | 54.39 |
| 162.1 | 55.07 |
| 162.1 | 54.98 |
| 162 | 54.51 |
| 162.1 | 54.49 |
| 161.8 | 54.01 |
| 162.2 | 54.06 |
| 161.9 | 52.91 |
| 161.8 | 52.54 |
| 161.9 | 52.15 |
| 162 | 52.65 |
| 161.8 | 52.35 |
| 161.8 | 53.58 |
| 161.6 | 54.06 |
| 161.8 | 54.07 |
| 161.6 | 53.71 |
| 161.4 | 54.09 |
| 161.8 | 53.74 |
| 161.8 | 54.19 |
| 161.9 | 54.08 |
| 161.8 | 53.66 |
| 161.9 | 54.35 |
| 161.5 | 55.34 |
| 161.8 | 55.76 |
| 161.7 | 54.59 |
| 161.8 | 53.93 |
| 161.9 | 54.97 |
| 162 | 55.17 |
| 161.9 | 55.02 |
| 162.4 | 55.13 |
| 161.8 | 55.92 |
| 161.5 | 55.36 |
| 161.9 | 54.58 |
| 161.9 | 54.55 |
| 161.9 | 56.61 |
| 161.7 | 57.25 |
| 161.9 | 57.96 |
| 162.1 | 59.04 |
| 161.8 | 57.93 |
| 161.8 | 56.76 |
| 161.7 | 56.39 |
| 162 | 57.5 |
| 161.8 | 57.79 |
| 161.8 | 57.69 |
| 161.9 | 57.89 |
| 161.5 | 59.02 |
| 161.7 | 59.84 |
| 161.9 | 60.81 |
| 162 | 60.87 |
| 162.1 | 61.05 |
| 162.2 | 60.84 |
| 161.9 | 60.92 |
| 161.9 | 61.95 |
| 161.5 | 62.49 |
| 161.8 | 62.32 |
| 161.8 | 63.55 |
| 161.5 | 64.01 |
| 161.8 | 63.56 |
| 161.7 | 64.32 |
| 161.7 | 64.73 |
| 161.6 | 65.54 |
| 161.6 | 65.78 |
| 161.6 | 66.6 |
| 161.7 | 65.98 |
| 161.7 | 65.95 |
| 161.9 | 66.75 |
| 161.8 | 66.83 |
| 161.7 | 65.13 |
| 161.8 | 67.08 |
| 161.7 | 66.42 |
| 162 | 66.7 |
| 161.7 | 67.81 |
| 161.8 | 69.55 |
| 161.9 | 69.83 |
| 161.6 | 71.49 |
| 161.8 | 71.53 |
| 161.4 | 69.85 |
| 161.8 | 70.4 |
| 161.9 | 69.95 |
| 161.7 | 70.42 |
| 161.7 | 72.55 |
| 161.6 | 70.81 |
| 161.8 | 69.64 |
| 161.4 | 69.31 |
| 161.7 | 69.46 |
| 161.6 | 69.63 |
| 161.6 | 69.39 |
| 161.9 | 68.77 |
| 161.6 | 70.28 |
| 162.1 | 70.93 |
| 162 | 71.21 |
| 161.6 | 70.38 |
| 161.8 | 70.64 |
| 161.8 | 71.35 |
| 161.8 | 70.76 |
| 161.8 | 69.84 |
| 161.9 | 70.54 |
| 161.6 | 69.32 |
| 161.6 | 68.15 |
| 161.7 | 70.38 |
| 161.6 | 70.31 |
| 161.7 | 72.14 |
| 161.6 | 72.62 |
| 161.7 | 72.67 |
| 161.9 | 72.25 |
| 162 | 73 |
| 162 | 72.84 |
| 161.8 | 72.47 |
| 161.6 | 71.91 |
| 161.6 | 72.49 |
| 161.8 | 72.98 |
| 162.2 | 73.13 |
| 161.7 | 74 |
| 161.7 | 74.26 |
| 161.9 | 74.53 |
| 162 | 74.96 |
| 161.6 | 73.63 |
| 161.9 | 75.08 |
| 162 | 74.21 |
| 161.6 | 74.69 |
| 161.8 | 74.92 |
| 161.9 | 75.61 |
| 161.9 | 76.47 |
| 161.6 | 75.61 |
| 162.1 | 75.36 |
| 161.5 | 75.87 |
| 161.9 | 76.44 |
| 161.6 | 76.38 |
| 161.8 | 77.22 |
| 162 | 78.21 |
| 161.7 | 79.06 |
| 161.9 | 77.57 |
| 161.7 | 77.61 |
| 161.9 | 78.39 |
| 161.6 | 78.74 |
| 161.8 | 78.5 |
| 161.4 | 78.56 |
| 161.7 | 79.81 |
| 161.8 | 80.31 |
| 161.9 | 79.44 |
| 162 | 80 |
| 162 | 80.82 |
| 162 | 82.13 |
| 162.1 | 82.5 |
| 161.9 | 81.83 |
| 161.7 | 81.21 |
| 161.6 | 81.17 |
| 161.9 | 81.09 |
| 161.8 | 80.45 |
| 161.5 | 79.63 |
| 161.9 | 78.03 |
| 162.1 | 77.8 |
| 161.6 | 79.68 |
| 161.7 | 79.55 |
| 161.5 | 77.66 |
| 161.5 | 76.12 |
| 161.5 | 75.92 |
| 161.7 | 77.5 |
| 161.9 | 79.57 |
| 161.6 | 80.14 |
| 162 | 80.09 |
| 161.4 | 79.81 |
| 162.2 | 79.77 |
| 162 | 80.53 |
| 161.7 | 81.17 |
| 161.6 | 81.35 |
| 161.8 | 81 |
| 161.7 | 81.53 |
| 162 | 83.23 |
| 161.8 | 83.92 |
| 161.8 | 84.01 |
| 161.8 | 82.6 |
| 161.6 | 82.06 |
| 161.8 | 82.69 |
| 161.7 | 83.96 |
| 161.6 | 85.54 |
| 161.6 | 86.68 |
| 161.9 | 88.31 |
| 162 | 88.04 |
| 162 | 88.4 |
| 161.8 | 89.76 |
| 161.8 | 88.87 |
| 161.6 | 88.48 |
| 161.9 | 88.13 |
| 162 | 88.43 |
| 161.7 | 89.68 |
| 161.9 | 93.12 |
| 161.8 | 94.07 |
| 161.8 | 92.82 |
| 161.7 | 92.8 |
| 162 | 93.81 |
| 162.1 | 93.88 |
| 161.9 | 93.43 |
| 161.8 | 92.92 |
| 161.9 | 93.07 |
| 162.1 | 92.97 |
| 161.6 | 93.33 |
| 161.9 | 92.95 |
| 161.7 | 92.96 |
| 161.9 | 93.83 |
| 162 | 93.45 |
| 161.6 | 94.8 |
| 161.6 | 95.28 |
| 161.7 | 94.55 |
| 161.8 | 94.9 |
| 161.9 | 95.15 |
| 162.1 | 95.36 |
| 162.1 | 96.63 |
| 161.8 | 96.55 |
| 161.3 | 98.32 |
| 161.7 | 99.05 |
| 161.8 | 99.38 |
| 162 | 99.45 |
| 162.1 | 100.5 |
| 161.9 | 100.9 |
| 161.8 | 100.8 |
| 161.6 | 98.82 |
| 161.8 | 100.9 |
| 161.9 | 101.4 |
| 161.6 | 101.6 |
| 161.9 | 101 |
| 161.8 | 101.1 |
| 161.9 | 103.1 |
| 161.9 | 102.1 |
| 162.1 | 103.3 |
| 161.8 | 104.8 |
| 161.9 | 105.6 |
| 162 | 104.3 |
| 162 | 105.7 |
| 161.7 | 105 |
| 161.8 | 104 |
| 161.7 | 104.7 |
| 161.6 | 105.5 |
| 162.1 | 106.4 |
| 162.1 | 104.4 |
| 161.3 | 104.2 |
| 161.8 | 104.1 |
| 161.6 | 105 |
| 161.8 | 106.3 |
| 162 | 107.7 |
| 161.7 | 107.4 |
| 162 | 108.8 |
| 161.5 | 107.8 |
| 161.6 | 106.9 |
| 161.9 | 106.2 |
| 161.9 | 106.3 |
| 161.6 | 104.8 |
| 161.9 | 106.1 |
| 161.6 | 107.6 |
| 162 | 107.3 |
| 161.9 | 105.9 |
| 161.5 | 106.9 |
| 161.7 | 106 |
| 161.8 | 106.6 |
| 161.8 | 107.9 |
| 161.8 | 107 |
| 161.9 | 107.3 |
| 161.9 | 107.2 |
| 161.9 | 106.7 |
| 162 | 106.3 |
| 161.9 | 104.9 |
| 161.4 | 104.7 |
| 161.9 | 105.7 |
| 161.3 | 108 |
| 161.7 | 108.3 |
| 161.8 | 107.7 |
| 162.1 | 110 |
| 162.3 | 112.8 |
| 161.9 | 117.4 |
| 161.6 | 121.8 |
| 161.6 | 122.6 |
| 161.6 | 121.7 |
| 161.6 | 123.7 |
| 161.7 | 128.9 |
| 161.8 | 133.2 |
| 161.8 | 138.2 |
| 161.8 | 138.3 |
| 161.7 | 137.8 |
| 162 | 135.6 |
| 161.7 | 136.9 |
| 161.9 | 137.1 |
| 161.8 | 138.5 |
| 161.9 | 138 |
| 162.1 | 139.3 |
| 162.1 | 139.5 |
| 162.2 | 139.7 |
| 162 | 145.3 |
| 162 | 144.2 |
| 161.8 | 146.6 |
| 161.9 | 144.8 |
| 161.6 | 148.4 |
| 161.7 | 148.9 |
| 161.9 | 151 |
| 161.9 | 149.5 |
| 161.8 | 151.6 |
| 161.8 | 150.5 |
| 161.9 | 149.2 |
| 161.8 | 148.7 |
| 162 | 147.9 |
| 162.1 | 151.1 |
| 161.7 | 152.2 |
| 161.8 | 152.1 |
| 162.1 | 151.5 |
| 161.5 | 155.5 |
| 161.9 | 157 |
| 162.1 | 160.7 |
| 161.9 | 157.9 |
| 162 | 157.7 |
| 161.9 | 159.7 |
| 161.7 | 164.6 |
| 161.7 | 161.3 |
| 162.4 | 167.2 |
| 161.9 | 163.5 |
| 161.8 | 167.2 |
| 162 | 172.7 |
| 162 | 174.9 |
| 161.6 | 175.5 |
| 161.8 | 176.6 |
| 161.8 | 172.9 |
| 162.1 | 175.9 |
| 161.9 | 176.6 |
| 161.8 | 178.6 |
| 161.7 | 183.1 |
| 161.9 | 182.3 |
| 162 | 182 |
| 162 | 184.9 |
| 161.9 | 184.3 |
| 161.7 | 192.5 |
| 162.3 | 186.3 |
| 162 | 187.5 |
| 162 | 189.7 |
| 162.1 | 190.5 |
| 162 | 192.7 |
| 162 | 196.4 |
| 162.1 | 197.7 |
| 161.8 | 199.3 |
| 161.1 | 199.1 |
| 161.9 | 200.1 |
| 162 | 206.4 |
| 162.1 | 208 |
| 161.9 | 213.4 |
| 161.9 | 208.4 |
| 161.8 | 210.7 |
| 161.9 | 211.7 |
| 161.9 | 210.1 |
| 161.9 | 212 |
| 161.7 | 216 |
| 161.5 | 216.5 |
| 161.9 | 225.1 |
| 161.8 | 226.6 |
| 162 | 228.7 |
| 161.7 | 223.8 |
| 162.3 | 231.2 |
| 161.8 | 229.4 |
| 161.7 | 227.6 |
| 161.9 | 224.1 |
| 161.9 | 227.9 |
| 162.1 | 228.7 |
| 162 | 227.3 |
| 162.1 | 231 |
| 161.8 | 236.5 |
| 162.1 | 235.6 |
| 162.2 | 231.6 |
| 161.8 | 238.6 |
| 161.7 | 233 |
| 162.4 | 236.8 |
| 162.1 | 230 |
| 161.6 | 233.9 |
| 162 | 234.5 |
| 161.7 | 237.9 |
| 162.1 | 240.5 |
| 162.4 | 241.3 |
| 162 | 239.6 |
| 161.7 | 236.5 |
| 161.6 | 239.4 |
| 161.8 | 236.9 |
| 162.4 | 238.2 |
| 161.9 | 241.3 |
| 161.8 | 237.8 |
| 162 | 240.5 |
| 161.8 | 241.1 |
| 162.1 | 245.4 |
| 161.8 | 241.2 |
| 162.1 | 245.2 |
| 161.5 | 251.6 |
| 161.9 | 256.2 |
| 161.6 | 258.3 |
| 161.7 | 262.4 |
| 162 | 265 |
| 161.9 | 268.2 |
| 161.7 | 265.6 |
| 161.6 | 268.9 |
| 161.9 | 267.6 |
| 161.6 | 262.7 |
| 161.8 | 264.9 |
| 162.1 | 266.7 |
| 161.1 | 262.9 |
| 162.1 | 267.8 |
| 161.8 | 265.6 |
| 161.8 | 265.4 |
| 161.8 | 269.9 |
| 162.1 | 270.2 |
| 162.2 | 269 |
| 162.1 | 273.8 |
| 161.8 | 275 |
| 162 | 273.6 |
| 161.8 | 274.9 |
| 161.9 | 272.7 |
| 161.9 | 274.6 |
| 161.9 | 266.1 |
| 162.1 | 273.4 |
| 161.9 | 270.9 |
| 161.9 | 273.3 |
| 161.9 | 273.3 |
| 162 | 273.7 |
| 162 | 270.4 |
| 162.2 | 273.3 |
| 162 | 278.7 |
| 161.8 | 278.4 |
| 162.2 | 284 |
| 161.8 | 280 |
| 161.9 | 273.6 |
| 161.9 | 272.9 |
| 161.8 | 273.2 |
| 162 | 274.2 |
| 162 | 273.7 |
| 162 | 273.8 |
| 161.9 | 276.6 |
| 161.8 | 274.6 |
| 161.8 | 273.2 |
| 162 | 278.4 |
| 162 | 282.3 |
| 161.8 | 276.3 |
| 161.9 | 279.9 |
| 162.4 | 282.4 |
| 161.9 | 280.7 |
| 161.9 | 287.5 |
| 161.7 | 289.4 |
| 162 | 296.5 |
| 162 | 294.4 |
| 162 | 301.1 |
| 161.9 | 294.2 |
| 161.7 | 296.4 |
| 161.8 | 298.5 |
| 162 | 297.9 |
| 161.9 | 301.2 |
| 161.9 | 301.8 |
| 161.5 | 304.6 |
| 161.3 | 301.2 |
| 161.9 | 303.4 |
| 162 | 314.7 |
| 161.4 | 307.5 |
| 161.9 | 303.9 |
| 161.6 | 303.8 |
| 161.6 | 305.4 |
| 161.8 | 306.1 |
| 161.9 | 301.5 |
| 161.2 | 300.4 |
| 162 | 310 |
| 161.1 | 311.1 |
| 161.8 | 308.8 |
| 161.8 | 308.2 |
| 161.6 | 305.4 |
| 161.8 | 306 |
| 162.3 | 305.7 |
| 161.8 | 307.9 |
| 161.6 | 308.7 |
| 161.6 | 307.6 |
| 161.4 | 307.3 |
| 161.6 | 314.1 |
| 162.1 | 312.5 |
| 161.7 | 308.4 |
| 161.5 | 314.2 |
| 161.9 | 318 |
| 161.7 | 310.7 |
| 162.2 | 313.3 |
| 161.8 | 316.5 |
| 161.8 | 314.6 |
| 161.8 | 321.8 |
| 162.1 | 316.3 |
| 161.8 | 321.3 |
| 162 | 321.3 |
| 161.8 | 321.1 |
| 161.5 | 319 |
| 161.8 | 319.4 |
| 161.8 | 321 |
| 161.9 | 319.9 |
| 162.1 | 325.2 |
| 162 | 330.1 |
| 161.7 | 336.1 |
| 161.7 | 330.1 |
| 162.1 | 319.7 |
| 161.4 | 320.5 |
| 161.9 | 322 |
| 161.5 | 320.9 |
| 161.8 | 322.7 |
| 161.5 | 323.1 |
| 161.7 | 322 |
| 161.7 | 325 |
| 161.7 | 320.3 |
| 161.6 | 327.6 |
| 161.9 | 329.5 |
| 161.4 | 338.6 |
| 161.9 | 344.2 |
| 161.5 | 339.5 |
| 161.7 | 338 |
| 161.3 | 341.4 |
| 161.4 | 341.3 |
| 161.6 | 346 |
| 161.3 | 347.4 |
| 161.4 | 351.7 |
| 161.6 | 356.3 |
| 161.5 | 359.5 |
| 161.5 | 355.7 |
| 161.5 | 355.9 |
| 161.8 | 363.5 |
| 161.6 | 366.4 |
| 162.1 | 368.7 |
| 161.8 | 368.5 |
| 161.9 | 365.9 |
| 161.4 | 383.3 |
| 162 | 383.4 |
| 162.4 | 379.4 |
| 161.9 | 377.8 |
| 162 | 381.2 |
| 161.9 | 376.1 |
| 161.5 | 373.5 |
| 161.6 | 373.1 |
| 161.5 | 368 |
| 161.8 | 371.1 |
| 161.6 | 370.8 |
| 161.7 | 371.8 |
| 161.4 | 370.3 |
| 161.6 | 365.8 |
| 161.4 | 369.3 |
| 161.3 | 368 |
| 161.7 | 371.3 |
| 161.6 | 367.4 |
| 161.6 | 365.8 |
| 161.6 | 368.5 |
| 161.6 | 371.5 |
| 161.3 | 372.3 |
| 161.1 | 378 |
| 161.6 | 377.3 |
| 161.6 | 379.1 |
| 161.5 | 373.6 |
| 161.6 | 364.8 |
| 161.8 | 371.8 |
| 161.3 | 370.1 |
| 161.6 | 373.9 |
| 161.7 | 376.1 |
| 161.5 | 376.8 |
| 161.5 | 380.7 |
| 161.7 | 378 |
| 161.3 | 381.9 |
| 161.6 | 383 |
| 161.4 | 378.2 |
| 161.4 | 386 |
| 161.1 | 385.8 |
| 161.4 | 384 |
| 161.7 | 377.8 |
| 161.8 | 380 |
| 161.6 | 378.4 |
| 160.9 | 378.3 |
| 161.6 | 379.1 |
| 161.7 | 384.4 |
| 162.1 | 387.9 |
| 161.8 | 385.6 |
| 161.4 | 380.7 |
| 161.9 | 372.9 |
| 161.9 | 379.7 |
| 161.5 | 382 |
| 161.9 | 382.7 |
| 161.4 | 380.2 |
| 161.6 | 374.4 |
| 161.4 | 381.1 |
| 161.6 | 381.1 |
| 161.5 | 382.2 |
| 160.9 | 385.3 |
| 161.6 | 382 |
| 161.4 | 382.8 |
| 161.4 | 380.6 |
| 161.4 | 383.8 |
| 161.6 | 392.6 |
| 161.8 | 393.5 |
| 161.7 | 403 |
| 162.3 | 402.2 |
| 161.5 | 401 |
| 161.8 | 393.5 |
| 161.5 | 394.9 |
| 161.5 | 395.4 |
| 161.7 | 397.5 |
| 161.3 | 391.5 |
| 161.6 | 395.1 |
| 161.4 | 392.9 |
| 161.5 | 394.2 |
| 161.6 | 398 |
| 161.4 | 401.4 |
| 161.6 | 397.4 |
| 161.9 | 396.8 |
| 161.9 | 394.3 |
| 161.6 | 393.4 |
| 161.7 | 388.9 |
| 161 | 393.4 |
| 161.7 | 399.6 |
| 161.6 | 391.9 |
| 161.6 | 393 |
| 161.9 | 393.6 |
| 161.5 | 398.8 |
| 162 | 399.3 |
| 161.3 | 410.1 |
| 161.9 | 407.2 |
| 161.9 | 409.2 |
| 161.6 | 409.4 |
| 161.4 | 408.7 |
| 162 | 413.6 |
| 161.7 | 411.5 |
| 161.7 | 407.4 |
| 161.5 | 408 |
| 161.8 | 408.7 |
| 161.9 | 411.7 |
| 162.1 | 413 |
| 161.4 | 415 |
| 161.9 | 419.2 |
| 161.9 | 421.2 |
| 161.7 | 417.3 |
| 162 | 419.4 |
| 161.5 | 418.9 |
| 161.8 | 424.1 |
| 161.3 | 415.6 |
| 161.7 | 409.6 |
| 161.7 | 414.8 |
| 161.6 | 417.3 |
| 161.7 | 421.5 |
| 161.7 | 418.6 |
| 161.9 | 417.5 |
| 161.5 | 418.2 |
| 161.3 | 419.6 |
| 161.1 | 418.5 |
| 161.6 | 421.4 |
| 161.6 | 418.3 |
| 161.6 | 425.3 |
| 161.3 | 420.7 |
| 161.5 | 424.8 |
| 161.7 | 423.8 |
| 162.2 | 417.3 |
| 161.4 | 423.1 |
| 161.9 | 426 |
| 161 | 425.2 |
| 161.6 | 429.3 |
| 161.4 | 431 |
| 161.5 | 424.9 |
| 161.1 | 426.7 |
| 161.2 | 426.5 |
| 161.6 | 429.3 |
| 161.3 | 429.5 |
| 161.5 | 444.2 |
| 161 | 439.5 |
| 161.4 | 437.7 |
| 161.5 | 435.1 |
| 161.5 | 442.7 |
| 161.2 | 439.9 |
| 161.3 | 445.5 |
| 160.9 | 443 |
| 161.5 | 435.2 |
| 160.8 | 445.3 |
| 161.5 | 434.4 |
| 161.4 | 433.8 |
| 161.8 | 439.9 |
| 161.8 | 443.6 |
| 161.6 | 445.4 |
| 161.6 | 440.6 |
| 161.5 | 447.8 |
| 161.7 | 454.1 |
| 161.8 | 450.6 |
| 161.6 | 458.1 |
| 161.7 | 458.6 |
| 161.3 | 452 |
| 161.8 | 452.1 |
| 161.5 | 456.2 |
| 161.2 | 450.7 |
| 161.5 | 448.7 |
| 161.7 | 451.8 |
| 161.9 | 454.1 |
| 161.6 | 454.2 |
| 162 | 453.2 |
| 161.8 | 457.8 |
| 161.8 | 457.8 |
| 162.1 | 452.8 |
| 161.9 | 456.8 |
| 161.8 | 461 |
| 161.5 | 459.8 |
| 162.1 | 463.1 |
| 161.5 | 462 |
| 162.1 | 467.6 |
| 162 | 469.2 |
| 161.9 | 467.8 |
| 161.6 | 464.4 |
| 161.7 | 465.6 |
| 161.9 | 470.4 |
| 162 | 467.6 |
| 161.9 | 461.3 |
| 161.8 | 464.1 |
| 161.8 | 473.8 |
| 162.2 | 477.5 |
| 161.9 | 479.8 |
| 161.4 | 479.7 |
| 161.7 | 482.1 |
| 162 | 480.3 |
| 161.8 | 475.9 |
| 161.8 | 479.5 |
| 161.5 | 485.9 |
| 161.7 | 491 |
| 161.5 | 485.8 |
| 161.8 | 480.7 |
| 161.6 | 477.2 |
| 161.5 | 479.5 |
| 161.8 | 485.6 |
| 162.3 | 490.4 |
| 161.6 | 485.6 |
| 161.9 | 491.5 |
| 161.7 | 490.5 |
| 161.9 | 489.9 |
| 161.9 | 493.7 |
| 162.3 | 494.8 |
| 161.5 | 493.8 |
| 161.8 | 493.8 |
| 161.9 | 487.9 |
| 161.8 | 498 |
| 162 | 490.6 |
| 161.9 | 491.8 |
| 162 | 494 |
| 161.8 | 484.7 |
| 161.9 | 491.5 |
| 162 | 490.2 |
| 162.5 | 495.8 |
| 161.6 | 494.7 |
| 161.9 | 494.3 |
| 162.3 | 498 |
| 162.1 | 508.3 |
| 162 | 514.6 |
| 162.2 | 511.1 |
| 162.3 | 522.5 |
| 162.4 | 520.3 |
| 162.2 | 514 |
| 162 | 531.4 |
| 162.4 | 527.2 |
| 162.3 | 523.2 |
| 162.6 | 518 |
| 162.5 | 515.9 |
| 162.2 | 527.8 |
| 162 | 523.1 |
| 162.1 | 525 |
| 162.1 | 522.5 |
| 162.4 | 528.3 |
| 162.3 | 525 |
| 162.3 | 526.2 |
| 162.1 | 531.1 |
| 162.3 | 530.7 |
| 162.4 | 529 |
| 162.3 | 534.1 |
| 162.2 | 540 |
| 162.1 | 540.6 |
| 162.2 | 539.6 |
| 162.2 | 541 |
| 162 | 548.9 |
| 162.5 | 551.5 |
| 162.4 | 545.3 |
| 162.1 | 548.3 |
| 162.3 | 546.1 |
| 162.2 | 539.7 |
| 162.1 | 545.1 |
| 162.1 | 554.7 |
| 162.2 | 553.3 |
| 162.3 | 556.3 |
| 162.6 | 554.1 |
| 162.4 | 564.3 |
| 162 | 564.9 |
| 162.4 | 564.8 |
| 162.3 | 574.6 |
| 162.4 | 568.6 |
| 162.3 | 566.3 |
| 162.5 | 571.5 |
| 162.1 | 575.4 |
| 162.3 | 562.4 |
| 162.5 | 568.4 |
| 162.3 | 577.7 |
| 162.5 | 580.5 |
| 162.4 | 583.3 |
| 162.4 | 584.6 |
| 162.2 | 583.6 |
| 162.2 | 582.1 |
| 162.5 | 581.8 |
| 162.2 | 585.2 |
| 162.4 | 591.8 |
| 162.6 | 596.7 |
| 162.1 | 591.6 |
| 162.1 | 597.5 |
| 162.1 | 594.2 |
| 162.4 | 597.9 |
| 162.3 | 603.2 |
| 162.6 | 593.1 |
| 162.2 | 597.6 |
| 162.7 | 599.5 |
| 162.6 | 599.1 |
| 162.2 | 586.6 |
| 162.6 | 599.3 |
| 162.2 | 596.5 |
| 162.3 | 590.3 |
| 162.5 | 589.3 |
| 162 | 596.7 |
| 162.3 | 590.6 |
| 162.4 | 589 |
| 162.4 | 591.6 |
| 162.5 | 596.9 |
| 162.3 | 594.1 |
| 162.5 | 590.4 |
| 162.5 | 591.6 |
| 162.2 | 590.7 |
| 162.1 | 592.6 |
| 162.3 | 597.2 |
| 162.5 | 603.7 |
| 162.4 | 585.6 |
| 162.3 | 576.7 |
| 162.2 | 572.3 |
| 162.4 | 572.7 |
| 162.4 | 580.2 |
| 162.6 | 583.7 |
| 162.2 | 578.3 |
| 162.3 | 575.5 |
| 162.4 | 588.2 |
| 162.2 | 583.8 |
| 162.4 | 592.2 |
| 162.3 | 584.2 |
| 162.6 | 578.4 |
| 162.2 | 583.7 |
| 162.4 | 585.4 |
| 162.5 | 582.4 |
| 162.4 | 580.1 |
| 162.7 | 578.1 |
| 162.3 | 581.5 |
| 162.6 | 581.2 |
| 162.7 | 578.3 |
| 162.4 | 581.9 |
| 162.3 | 586.4 |
| 162.4 | 587.4 |
| 162.5 | 585.8 |
| 162.5 | 590 |
| 162.4 | 585.8 |
| 162.7 | 585.6 |
| 162.5 | 588.5 |
| 162.2 | 577.9 |
| 162.3 | 588.8 |
| 162.4 | 591.9 |
| 162.3 | 589.6 |
| 162.5 | 586.2 |
| 162.3 | 585.8 |
| 162.3 | 578 |
| 162.6 | 577.2 |
| 162.9 | 577.6 |
| 162.7 | 579.8 |
| 163 | 581.4 |
| 162.7 | 581.1 |
| 162.4 | 572.4 |
| 162.2 | 576.9 |
| 162.7 | 573.8 |
| 162.4 | 569.5 |
| 162.5 | 574.5 |
| 162.9 | 580.9 |
| 162.4 | 586.6 |
| 162.8 | 583.4 |
| 162.7 | 583.4 |
| 162.6 | 583.9 |
| 162.9 | 593.5 |
| 162.7 | 594 |
| 162.6 | 590.4 |
| 162.4 | 591.2 |
| 162.3 | 586.7 |
| 162.6 | 582.4 |
| 162.6 | 575.3 |
| 162.3 | 574.8 |
| 162.7 | 580.7 |
| 162.9 | 585.4 |
| 162.2 | 589.9 |
| 162.7 | 591.2 |
| 162.8 | 590.1 |
| 162.7 | 589.4 |
| 162.4 | 581 |
| 162.5 | 577.2 |
| 162.3 | 577.2 |
| 162.4 | 581.7 |
| 162.5 | 583.1 |
| 162.6 | 588.6 |
| 162.6 | 592.5 |
| 162.4 | 584.2 |
| 162.6 | 586.4 |
| 162.3 | 584.7 |
| 162.1 | 583.9 |
| 162.4 | 578.1 |
| 162.5 | 577.4 |
| 162.3 | 576.8 |
| 162.2 | 575.3 |
| 162.8 | 568.8 |
| 162.4 | 578.8 |
| 162.8 | 584.7 |
| 162.5 | 578.3 |
| 162 | 581 |
| 162.3 | 579.8 |
| 162.1 | 578.8 |
| 162.1 | 581.8 |
| 162.3 | 593.6 |
| 162.3 | 584.3 |
| 162.1 | 577.3 |
| 162.2 | 595.3 |
| 162.2 | 596.5 |
| 162.3 | 603.3 |
| 162.4 | 608.1 |
| 162 | 609.5 |
| 162.5 | 604.1 |
| 162.4 | 600.1 |
| 162.8 | 596.8 |
| 162 | 601.6 |
| 162.3 | 596.3 |
| 162.2 | 601.7 |
| 162.4 | 592.1 |
| 162.3 | 595.8 |
| 162.4 | 587.4 |
| 161.9 | 585.4 |
| 162.3 | 594.4 |
| 162.4 | 591.2 |
| 162.3 | 598.9 |
| 162.3 | 598.7 |
| 162.9 | 605.1 |
| 162.2 | 604.6 |
| 162.1 | 602.3 |
| 162.4 | 602.5 |
| 162.4 | 609.2 |
| 162.3 | 608.3 |
| 162 | 615.1 |
| 162.5 | 610.8 |
| 162.4 | 607.8 |
| 162.2 | 606 |
| 162.2 | 613.8 |
| 162.5 | 612.7 |
| 162.4 | 609.3 |
| 162.3 | 613.7 |
| 162.3 | 615.4 |
| 162.7 | 601.8 |
| 162.7 | 608.4 |
| 162.5 | 600.9 |
| 162.5 | 609.1 |
| 162.4 | 617.1 |
| 162.6 | 614.9 |
| 162.4 | 607.1 |
| 162.3 | 604.1 |
| 162.4 | 605.9 |
| 162 | 610.2 |
| 162.3 | 611.2 |
| 162.4 | 612.1 |
| 162.2 | 612.9 |
| 162.7 | 612.5 |
| 162.3 | 617.8 |
| 162.3 | 625.9 |
| 162.8 | 612.7 |
| 162.4 | 612.2 |
| 162 | 617 |
| 162.6 | 612.9 |
| 162.4 | 612.2 |
| 162.3 | 616.4 |
| 162.5 | 618.5 |
| 162.6 | 617.6 |
| 162.6 | 620 |
| 162.3 | 619.4 |
| 162.8 | 621.3 |
| 162.8 | 615.4 |
| 162.1 | 621.3 |
| 162.2 | 624.4 |
| 162.1 | 618.4 |
| 162.3 | 615.2 |
| 162.1 | 617.7 |
| 162.5 | 617.6 |
| 162.2 | 621.7 |
| 162.3 | 626.6 |
| 162.3 | 617.7 |
| 162.6 | 623.3 |
| 162.5 | 626 |
| 162.8 | 632.1 |
| 162.8 | 631.9 |
| 163.1 | 634.9 |
| 162.7 | 629.2 |
| 162.9 | 638.1 |
| 162.6 | 641.2 |
| 162.4 | 641.2 |
| 162.6 | 648 |
| 162.6 | 652.6 |
| 162.9 | 642.6 |
| 163.1 | 645.9 |
| 162.5 | 641.8 |
| 162.4 | 646.3 |
| 162.5 | 653.4 |
| 162.4 | 650.9 |
| 162.6 | 648.4 |
| 162.6 | 647.9 |
| 162.6 | 644.2 |
| 162.5 | 649.2 |
| 162.6 | 645.9 |
| 162.7 | 635.3 |
| 162.5 | 641.5 |
| 162.3 | 650.4 |
| 162.7 | 653.8 |
| 162.4 | 644.1 |
| 162.6 | 653.2 |
| 162.3 | 646.1 |
| 162.8 | 653 |
| 162.7 | 651.1 |
| 162.4 | 653.1 |
| 162.4 | 662.6 |
| 163 | 665 |
| 162.8 | 655.7 |
| 162.4 | 655.9 |
| 162.3 | 652.4 |
| 162.5 | 656.2 |
| 162.6 | 656.7 |
| 162.2 | 663.5 |
| 162.8 | 660.5 |
| 162.6 | 660.5 |
| 162.4 | 665.6 |
| 163 | 661.4 |
| 162.6 | 674.7 |
| 162.5 | 665.6 |
| 162.7 | 657.1 |
| 162.3 | 655.1 |
| 162.1 | 651.4 |
| 162.3 | 657.3 |
| 162.4 | 657.9 |
| 162.6 | 670.8 |
| 162.4 | 669.4 |
| 162.5 | 660.5 |
| 162.3 | 664 |
| 162.4 | 674 |
| 162.5 | 670 |
| 162 | 671.1 |
| 162.7 | 665.7 |
| 162.7 | 670.8 |
| 163 | 664 |
| 162.4 | 663 |
| 162.2 | 676.3 |
| 162.3 | 666 |
| 162.7 | 666.4 |
| 162.2 | 661.7 |
| 162.1 | 660.6 |
| 162.7 | 654.7 |
| 162.4 | 666.1 |
| 162.9 | 666 |
| 162.2 | 670.4 |
| 162.7 | 662.2 |
| 162.5 | 662.6 |
| 162.6 | 660.2 |
| 162.3 | 663.3 |
| 162.6 | 676.7 |
| 162.6 | 668.1 |
| 162.7 | 663.6 |
| 163.4 | 668.3 |
| 162.2 | 653.6 |
| 162.7 | 653.2 |
| 163.2 | 668.6 |
| 162.6 | 676.8 |
| 162.5 | 675 |
| 162.6 | 676.4 |
| 162.2 | 675.2 |
| 162.1 | 679.5 |
| 162.1 | 679.8 |
| 161.9 | 683.6 |
| 162.3 | 690.6 |
| 162.3 | 683.7 |
| 162.4 | 679.9 |
| 162.3 | 673.6 |
| 162.3 | 673.6 |
| 162.3 | 675.6 |
| 162.4 | 680.3 |
| 162.5 | 667.5 |
| 162.1 | 669.7 |
| 162.4 | 670.9 |
| 162.4 | 687.5 |
| 162.3 | 677.2 |
| 162.3 | 684.9 |
| 162.3 | 697 |
| 162.5 | 701.7 |
| 162.1 | 694.7 |
| 162.6 | 702.4 |
| 162.3 | 698.6 |
| 162.2 | 703.6 |
| 162.1 | 712 |
| 162.4 | 704.5 |
| 162.7 | 712.5 |
| 162.2 | 692.8 |
| 162.5 | 699.2 |
| 162.3 | 696.4 |
| 162.4 | 696.6 |
| 162.5 | 704.2 |
| 162.4 | 709.6 |
| 162.4 | 709.6 |
| 162.3 | 706.7 |
| 162.3 | 714.3 |
| 162.2 | 708.4 |
| 162.3 | 709.7 |
| 162 | 699.1 |
| 162.9 | 706.1 |
| 162 | 712.8 |
| 162.3 | 709.7 |
| 162.1 | 704.8 |
| 162.4 | 699.9 |
| 162.1 | 700.2 |
| 162.2 | 685.8 |
| 162.2 | 695.1 |
| 162.5 | 701 |
| 162.2 | 697.9 |
| 162.3 | 714.1 |
| 162.3 | 710.3 |
| 162.2 | 712.9 |
| 162.4 | 716.4 |
| 162.8 | 715 |
| 162.3 | 708.9 |
| 162.7 | 709.7 |
| 162.8 | 707.5 |
| 162.1 | 725.5 |
| 162.6 | 729 |
| 162.5 | 727 |
| 162.7 | 731.1 |
| 162.5 | 711.9 |
| 162.8 | 711.6 |
| 162.3 | 707 |
| 162.3 | 712.6 |
| 163.2 | 699.6 |
| 162.4 | 696.6 |
| 162.2 | 689.3 |
| 162.4 | 686.2 |
| 162.8 | 682.9 |
| 162.4 | 688.7 |
| 162.4 | 697.9 |
| 162.5 | 699.1 |
| 162.2 | 688.1 |
| 162.5 | 685 |
| 162.8 | 694.5 |
| 162.5 | 690.7 |
| 162.3 | 699.9 |
| 162.2 | 700 |
| 162.1 | 701.4 |
| 162.1 | 692 |
| 162.4 | 690.6 |
| 162.4 | 681.1 |
| 162 | 671 |
| 162.3 | 668.9 |
| 162.5 | 668 |
| 161.9 | 667.9 |
| 162 | 667.9 |
| 162.4 | 675 |
| 162.1 | 677.6 |
| 162.5 | 671.3 |
| 162.3 | 674.5 |
| 162.3 | 678.2 |
| 162.5 | 676.2 |
| 162.2 | 672.3 |
| 162.8 | 677.1 |
| 162.5 | 683.2 |
| 162.1 | 687.9 |
| 162.3 | 709.4 |
| 162 | 703.8 |
| 162.4 | 699.1 |
| 162.6 | 694.2 |
| 162.7 | 692.7 |
| 162.8 | 698.3 |
| 162.4 | 702.8 |
| 162.7 | 705.5 |
| 162.1 | 715 |
| 162.5 | 710.6 |
| 163 | 710.5 |
| 162.4 | 706.7 |
| 162.7 | 715.5 |
| 163 | 705 |
| 162.6 | 711.5 |
| 162.6 | 700 |
| 162.3 | 693.9 |
| 162.2 | 701.2 |
| 161.9 | 698.4 |
| 162.7 | 715.4 |
| 162.1 | 709.5 |
| 162.5 | 702.5 |
| 162.4 | 701.1 |
| 162.4 | 702.9 |
| 162.3 | 701.7 |
| 162 | 698.8 |
| 162.8 | 706.1 |
| 162.4 | 715.1 |
| 162.4 | 708 |
| 162.7 | 708.9 |
| 162.4 | 716.5 |
| 162.4 | 700.5 |
| 162.1 | 705 |
| 162.1 | 704.1 |
| 162.4 | 708.7 |
| 162.3 | 707.2 |
| 162.3 | 705 |
| 162.2 | 700.8 |
| 162.3 | 708.4 |
| 162.5 | 703.4 |
| 162.7 | 705.8 |
| 162.2 | 698.7 |
| 162.7 | 694.7 |
| 162.5 | 704.3 |
| 161.9 | 699.3 |
| 162.5 | 705.8 |
| 161.9 | 716.1 |
| 162.5 | 705 |
| 162.3 | 710.5 |
| 162.3 | 705.4 |
| 162.1 | 713.8 |
| 162 | 711.2 |
| 162.9 | 707.4 |
| 162.6 | 713.4 |
| 162.4 | 702.1 |
| 162.3 | 706.4 |
| 162.3 | 701.6 |
| 162.2 | 701.1 |
| 162.2 | 693.3 |
| 162.3 | 696.9 |
| 162.2 | 689.4 |
| 162.3 | 696.2 |
| 162.5 | 687.1 |
| 162.2 | 704.4 |
| 162.3 | 714.3 |
| 161.7 | 719.2 |
| 162.1 | 723.1 |
| 162.2 | 716.6 |
| 162.5 | 719.5 |
| 162.1 | 733.3 |
| 162.3 | 730.2 |
| 162.1 | 726.4 |
| 162.1 | 721.1 |
| 162.4 | 733.2 |
| 162 | 726.7 |
| 162.5 | 727.4 |
| 162.4 | 731.2 |
| 162.6 | 732.9 |
| 162.6 | 728.3 |
| 162.7 | 737.6 |
| 162.4 | 753.2 |
| 162 | 758.6 |
| 162.1 | 760.4 |
| 162.4 | 765.9 |
| 162.1 | 743.7 |
| 162.3 | 751.6 |
| 162.3 | 745.5 |
| 162 | 747.5 |
| 162.3 | 746 |
| 162.4 | 744.6 |
| 162.5 | 747.4 |
| 162.2 | 737 |
| 162.5 | 762.8 |
| 162.6 | 764.6 |
| 162.6 | 762 |
| 162.2 | 760.6 |
| 162.3 | 763.4 |
| 162.3 | 758.8 |
| 162.7 | 750.4 |
| 162.2 | 758.1 |
| 162.2 | 754 |
| 162.2 | 747.5 |
| 162 | 753.5 |
| 162 | 759.8 |
| 162.1 | 760 |
| 162.2 | 762.4 |
| 162.1 | 765 |
| 162.3 | 754.6 |
| 162.3 | 757.7 |
| 162.7 | 758.9 |
| 162.9 | 752.3 |
| 162.2 | 760.8 |
| 162.7 | 747.9 |
| 162.4 | 766.7 |
| 162.4 | 757.6 |
| 162.3 | 753.4 |
| 162.7 | 751.4 |
| 162.3 | 749 |
| 162.6 | 748.8 |
| 162.1 | 744.5 |
| 162.1 | 744 |
| 162.5 | 742.9 |
| 162.1 | 746.1 |
| 162.4 | 745.9 |
| 162.2 | 757.9 |
| 162.3 | 749.6 |
| 161.7 | 757.7 |
| 162.5 | 756.7 |
| 162.9 | 745.2 |
| 162.4 | 743.6 |
| 162 | 735.8 |
| 162.6 | 746.1 |
| 162.3 | 749.7 |
| 162.4 | 741.9 |
| 162.2 | 734.3 |
| 162.3 | 738 |
| 162.2 | 742.1 |
| 162.2 | 741.1 |
| 163 | 742.8 |
| 162.4 | 737.9 |
| 162.8 | 739.8 |
| 162.5 | 730.7 |
| 162.3 | 736.4 |
| 162.4 | 731.2 |
| 162.6 | 732.7 |
| 162.5 | 734.6 |
| 162.7 | 730.9 |
| 162.5 | 728.8 |
| 162.7 | 730.3 |
| 162.6 | 725.6 |
| 163.1 | 736.4 |
| 162.3 | 730.9 |
| 162.3 | 729.3 |
| 162.5 | 723.7 |
| 162.2 | 732.8 |
| 162.3 | 741.2 |
| 162.3 | 734.2 |
| 162.4 | 724.6 |
| 162.2 | 721.3 |
| 162.5 | 728.9 |
| 162.2 | 730.6 |
| 162.1 | 728.6 |
| 162.3 | 724.1 |
| 162.2 | 725.3 |
| 162.6 | 733.8 |
| 163 | 728.2 |
| 162.7 | 723.6 |
| 161.9 | 723.8 |
| 162.4 | 749.1 |
| 162.4 | 750.1 |
| 162.3 | 739.3 |
| 162.3 | 751.8 |
| 162.2 | 746.4 |
| 162.5 | 743 |
| 162.2 | 744.8 |
| 162.4 | 741.4 |
| 162.5 | 746.7 |
| 162.4 | 740.4 |
| 162.3 | 750.9 |
| 162.1 | 741.2 |
| 162 | 740.7 |
| 162.6 | 746.6 |
| 161.9 | 755.5 |
| 162.3 | 758.2 |
| 161.9 | 753.5 |
| 163 | 750.2 |
| 162.5 | 733.3 |
| 162.6 | 734.9 |
| 162.5 | 740.9 |
| 162.4 | 747.9 |
| 162.4 | 746.2 |
| 162.2 | 738.3 |
| 162 | 744.2 |
| 162.1 | 753.1 |
| 162.2 | 750.4 |
| 162.2 | 750 |
| 162.3 | 746.5 |
| 162.3 | 747.6 |
| 162.3 | 752.8 |
| 162.1 | 766.3 |
| 162.2 | 771.5 |
| 162.4 | 765.9 |
| 162.8 | 771.6 |
| 162.4 | 771.6 |
| 162.3 | 764.3 |
| 162 | 772.6 |
| 162 | 759.5 |
| 162.3 | 754.5 |
| 162.3 | 751.3 |
| 162.8 | 752.2 |
| 162.3 | 767.8 |
| 162.4 | 770.1 |
| 162.1 | 777 |
| 162 | 788.4 |
| 162 | 779.6 |
| 163 | 770.4 |
| 162.3 | 764.2 |
| 162.2 | 770.3 |
| 162.5 | 760.8 |
| 162.9 | 771.9 |
| 162.9 | 778.1 |
| 162.5 | 774.8 |
| 162.8 | 776.8 |
| 162.6 | 777.5 |
| 162.1 | 774.2 |
| 162.3 | 776.6 |
| 162.4 | 778.8 |
| 161.9 | 778.4 |
| 162.2 | 766.8 |
| 162.5 | 773.7 |
| 162.7 | 774.4 |
| 162.4 | 778.9 |
| 162.4 | 772.4 |
| 162.1 | 775.1 |
| 162.3 | 781.2 |
| 162.3 | 780 |
| 162.2 | 790.1 |
| 162.6 | 795.9 |
| 162.5 | 783.9 |
| 162.2 | 786.7 |
| 162.3 | 789.1 |
| 162.5 | 787 |
| 162.5 | 780.6 |
| 162.4 | 774.6 |
| 162.3 | 771.9 |
| 162.1 | 775 |
| 162.6 | 766.9 |
| 162.4 | 775.7 |
| 162.2 | 781.8 |
| 162.8 | 779.4 |
| 162.4 | 767.6 |
| 162.6 | 764.7 |
| 162.6 | 763 |
| 163 | 764.6 |
| 162.7 | 770.6 |
| 162.5 | 781.6 |
| 162.5 | 780.6 |
| 162.4 | 787.2 |
| 162.1 | 794.8 |
| 162.3 | 799 |
| 162.2 | 796.9 |
| 162.6 | 801.2 |
| 162.4 | 798.7 |
| 163.2 | 796.9 |
| 162.6 | 796.2 |
| 162.1 | 791.2 |
| 162.8 | 794.9 |
| 162.7 | 791.5 |
| 162.2 | 786.1 |
| 163.1 | 788.1 |
| 162.4 | 790.1 |
| 162.6 | 793.8 |
| 162.1 | 794.4 |
| 162.7 | 784.8 |
| 163 | 796.8 |
| 162.6 | 792.9 |
| 163.4 | 791.5 |
| 163.3 | 792.9 |
| 162.7 | 794.7 |
| 162.3 | 784.2 |
| 162.6 | 785.9 |
| 162.4 | 783.6 |
| 162.7 | 779.4 |
| 162.9 | 791.6 |
| 163 | 798 |
| 163 | 806.9 |
| 162.5 | 810.7 |
| 162.5 | 814.5 |
| 162.6 | 815.4 |
| 162.5 | 811.3 |
| 162.8 | 811.4 |
| 162.5 | 812.9 |
| 162.2 | 815.4 |
| 162.7 | 804.7 |
| 162.6 | 800.8 |
| 162.8 | 809.2 |
| 163.1 | 805 |
| 163.1 | 807.5 |
| 162.7 | 814.5 |
| 162.2 | 809.9 |
| 162.2 | 805.6 |
| 162.1 | 802.3 |
| 162 | 815.5 |
| 162.3 | 799.1 |
| 162.3 | 798.3 |
| 162.1 | 811 |
| 162.5 | 810.3 |
| 161.9 | 804.2 |
| 162.3 | 803 |
| 162.4 | 805 |
| 162.2 | 817.8 |
| 162.3 | 824.1 |
| 162.3 | 814.3 |
| 162.2 | 815.5 |
| 162.4 | 811.8 |
| 162.4 | 812.2 |
| 162 | 804 |
| 161.7 | 819.5 |
| 162.5 | 805.5 |
| 162.5 | 830.5 |
| 162.1 | 821.3 |
| 162.1 | 814.1 |
| 162.2 | 803.4 |
| 162.3 | 800.6 |
| 162.7 | 812.6 |
| 162.5 | 813.5 |
| 162.1 | 804.1 |
| 162.1 | 811.7 |
| 162 | 809.5 |
| 162.5 | 813.8 |
| 163.1 | 818 |
| 162.4 | 817.1 |
| 162.6 | 808.4 |
| 162.5 | 805.4 |
| 162.2 | 818.6 |
| 162.2 | 828.5 |
| 162.2 | 831.9 |
| 162.1 | 838 |
| 162.4 | 835.4 |
| 162.4 | 825.1 |
| 162.5 | 834.6 |
| 162.7 | 839.9 |
| 162 | 832.5 |
| 162.7 | 819.2 |
| 162.8 | 820.9 |
| 162.1 | 829.8 |
| 162.4 | 826.4 |
| 162.4 | 824.1 |
| 162.4 | 817.2 |
| 162.8 | 813.2 |
| 162.2 | 821.8 |
| 162.5 | 817.3 |
| 162.5 | 819.2 |
| 162.3 | 824.1 |
| 162.7 | 827.7 |
| 162.5 | 830.7 |
| 162.1 | 830.5 |
| 163 | 827.5 |
| 162.2 | 828.9 |
| 162.3 | 824.5 |
| 161.9 | 832.8 |
| 162.2 | 833.5 |
| 162.5 | 819.3 |
| 162.2 | 823 |
| 162.3 | 813.6 |
| 162.4 | 812.4 |
| 162.2 | 807.4 |
| 162.3 | 811 |
| 162.4 | 798.8 |
| 162.3 | 795.5 |
| 162.5 | 796.2 |
| 162.5 | 809.4 |
| 162.5 | 809.5 |
| 162.5 | 816.5 |
| 162.4 | 831.7 |
| 162.8 | 829.2 |
| 162 | 827.6 |
| 161.9 | 837.2 |
| 162.2 | 829.7 |
| 162.2 | 833.8 |
| 162.2 | 827.4 |
| 162.7 | 831.2 |
| 162.3 | 831.3 |
| 162.2 | 831.7 |
| 162.2 | 830.7 |
| 162.7 | 835.2 |
| 162.7 | 838.3 |
| 162.4 | 834.4 |
| 162 | 839.4 |
| 162.4 | 835.6 |
| 162.7 | 828.9 |
| 162.7 | 832.1 |
| 162.4 | 824.1 |
| 162.7 | 822.8 |
| 162.3 | 819.1 |
| 162.2 | 824.6 |
| 162 | 830.9 |
| 162.4 | 827.6 |
| 162.4 | 816.6 |
| 161.7 | 816.3 |
| 161.8 | 815.1 |
| 162.8 | 812.1 |
| 162.4 | 809.6 |
| 162.6 | 816 |
| 162.1 | 816.8 |
| 162.1 | 827.9 |
| 162.1 | 826.8 |
| 162.1 | 821.3 |
| 162.8 | 820.4 |
| 162.2 | 823.3 |
| 162.5 | 829.6 |
| 162.5 | 814.6 |
| 162.4 | 820.3 |
| 162 | 837.9 |
| 162.2 | 834.9 |
| 161.9 | 841.4 |
| 161.9 | 848.4 |
| 162.4 | 839.5 |
| 162.1 | 844.5 |
| 162 | 846.3 |
| 162.3 | 845 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |


**`hole_ramp_rel130` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 129.4
- `free_shell.areal_density_ratio`: 0.876
- `free_shell.msd.1 ns`: 57.53
- `free_shell.msd.10 ns`: 221
- `free_shell.msd.end`: 3159
- `free_shell.msd.end_ns`: 68
- `params.hole_hold_ps`: 1e+04
- `params.release_t_c`: 130
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `scaffold.d_nm`: 2.5
- `scaffold.nearest_tethered_r_held_min`: 53.1
- `scaffold.nearest_tethered_r_t0`: 55
- `scaffold.tethered_fraction`: 0.5436
- T (°C): 25
- `t_close_ns`: 33.25
- `thickness_final`: 134.2
- `thickness_t0`: 163.4

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 129.8 | — |
| 129.8 | — |
| 130 | — |
| 129.9 | — |
| 130.2 | — |
| 130.4 | — |
| 130 | — |
| 129.7 | — |
| 130 | — |
| 130.3 | — |
| 129.9 | — |
| 129.6 | — |
| 129.8 | — |
| 129.6 | — |
| 130.1 | — |
| 130.2 | — |
| 129.7 | — |
| 130.3 | — |
| 130.3 | — |
| 129.9 | — |
| 129.6 | — |
| 129.7 | — |
| 129.9 | — |
| 129.6 | — |
| 130 | — |
| 130.1 | — |
| 129.8 | — |
| 129.8 | — |
| 129.8 | — |
| 130.1 | — |
| 130.2 | — |
| 129.8 | — |
| 129.9 | — |
| 130 | — |
| 130.4 | — |
| 130.2 | — |
| 129.8 | — |
| 130.3 | — |
| 130.3 | — |
| 130.1 | — |
| 129.9 | — |
| 130.2 | — |
| 129.9 | — |
| 130.2 | — |
| 130.1 | — |
| 130.4 | — |
| 130.3 | — |
| 130.1 | — |
| 129.6 | — |
| 129.9 | — |
| 129.9 | — |
| 130 | — |
| 129.6 | — |
| 129.9 | — |
| 129.7 | — |
| 130.2 | — |
| 130 | — |
| 129.3 | — |
| 129.8 | — |
| 129.8 | — |
| 129.9 | — |
| 130.2 | — |
| 130.2 | — |
| 130.1 | — |
| 130.1 | — |
| 130.4 | — |
| 130.1 | — |
| 130.7 | — |
| 130.6 | — |
| 130.1 | — |
| 130.4 | — |
| 130.8 | — |
| 130.6 | — |
| 130.2 | — |
| 131.2 | — |
| 130 | — |
| 130.7 | — |
| 130.4 | — |
| 130.6 | — |
| 131.2 | — |
| 131.1 | — |
| 130.3 | — |
| 130.2 | — |
| 130.5 | — |
| 129.8 | — |
| 130.7 | — |
| 130.9 | — |
| 131 | — |
| 131.5 | — |
| 130.7 | — |
| 131 | — |
| 131.7 | — |
| 131.3 | — |
| 131.7 | — |
| 130.7 | — |
| 131.9 | — |
| 131.5 | — |
| 131.5 | — |
| 131 | — |
| 131.6 | — |
| 131.6 | — |
| 132 | — |
| 131.8 | — |
| 131.9 | — |
| 132.2 | — |
| 131.7 | — |
| 131.9 | — |
| 131.4 | — |
| 131.7 | — |
| 131.4 | — |
| 132.2 | — |
| 131.3 | — |
| 131.8 | — |
| 131.8 | — |
| 132.1 | — |
| 132.4 | — |
| 133 | — |
| 132.2 | — |
| 132.6 | — |
| 132.8 | — |
| 132.6 | — |
| 133 | — |
| 132.9 | — |
| 132.9 | — |
| 133.4 | — |
| 133.1 | — |
| 132.9 | — |
| 133 | — |
| 133.4 | — |
| 133.4 | — |
| 133.5 | — |
| 133.1 | — |
| 133.3 | — |
| 133.5 | — |
| 133.3 | — |
| 133.5 | — |
| 133.5 | — |
| 133.5 | — |
| 133.3 | — |
| 133.5 | — |
| 134.2 | — |
| 133.3 | — |
| 133.6 | — |
| 133.9 | — |
| 133.8 | — |
| 134.1 | — |
| 134.6 | — |
| 134.1 | — |
| 133.8 | — |
| 134.3 | — |
| 134 | — |
| 134.1 | — |
| 135.7 | — |
| 135.6 | — |
| 134.7 | — |
| 135.1 | — |
| 135 | — |
| 135.6 | — |
| 135.1 | — |
| 135.5 | — |
| 134.7 | — |
| 134.7 | — |
| 134.9 | — |
| 135.9 | — |
| 134.8 | — |
| 134.6 | — |
| 135.1 | — |
| 135.3 | — |
| 135.6 | — |
| 135.3 | — |
| 136 | — |
| 136.2 | — |
| 136 | — |
| 135.2 | — |
| 135.9 | — |
| 136.2 | — |
| 135.7 | — |
| 136.3 | — |
| 136.5 | — |
| 136.2 | — |
| 136.1 | — |
| 136.7 | — |
| 137.7 | — |
| 136.3 | — |
| 137.7 | — |
| 137.3 | — |
| 136.6 | — |
| 136.7 | — |
| 136.3 | — |
| 136.7 | — |
| 136.6 | — |
| 136.5 | — |
| 137.1 | — |
| 137 | — |
| 136.9 | — |
| 137.4 | — |
| 137.2 | — |
| 138.1 | — |
| 137.4 | — |
| 137.1 | — |
| 137.6 | — |
| 137.9 | — |
| 137.7 | — |
| 138.1 | — |
| 137.6 | — |
| 137.7 | — |
| 137.7 | — |
| 137.9 | — |
| 138.1 | — |
| 138.4 | — |
| 139.5 | — |
| 138.4 | — |
| 139.8 | — |
| 138.4 | — |
| 138.6 | — |
| 139.3 | — |
| 139.1 | — |
| 139.3 | — |
| 139.9 | — |
| 138.6 | — |
| 139.4 | — |
| 139.6 | — |
| 139.6 | — |
| 140.3 | — |
| 140.6 | — |
| 139.9 | — |
| 139.9 | — |
| 139.7 | — |
| 140.4 | — |
| 140.7 | — |
| 140.7 | — |
| 141.1 | — |
| 140.2 | — |
| 140.3 | — |
| 141.1 | — |
| 140.6 | — |
| 141.1 | — |
| 141.3 | — |
| 141.6 | — |
| 141.9 | — |
| 142.2 | — |
| 141.7 | — |
| 141.4 | — |
| 141.8 | — |
| 141.8 | — |
| 142.9 | — |
| 142.9 | — |
| 143.1 | — |
| 142.4 | — |
| 142.6 | — |
| 143.4 | — |
| 142.5 | — |
| 144.2 | — |
| 142.7 | — |
| 142.6 | — |
| 143.4 | — |
| 143.3 | — |
| 143.6 | — |
| 144.1 | — |
| 144.3 | — |
| 144.5 | — |
| 143.6 | — |
| 144.4 | — |
| 144.1 | — |
| 144 | — |
| 143.7 | — |
| 144.5 | — |
| 144.8 | — |
| 144.8 | — |
| 144.6 | — |
| 144.2 | — |
| 144 | — |
| 144.9 | — |
| 145.4 | — |
| 144.9 | — |
| 145.2 | — |
| 143.9 | — |
| 144.2 | — |
| 145.4 | — |
| 145.8 | — |
| 145.4 | — |
| 146 | — |
| 146 | — |
| 145.8 | — |
| 146.7 | — |
| 146.3 | — |
| 145.8 | — |
| 146.3 | — |
| 147.5 | — |
| 146.7 | — |
| 146.2 | — |
| 146.7 | — |
| 147.3 | — |
| 146.9 | — |
| 146.8 | — |
| 147.4 | — |
| 147.4 | — |
| 146.9 | — |
| 147 | — |
| 146.7 | — |
| 147.1 | — |
| 148.3 | — |
| 148.3 | — |
| 148.1 | — |
| 148.4 | — |
| 148.8 | — |
| 148.1 | — |
| 148.3 | — |
| 148.2 | — |
| 149 | — |
| 148.5 | — |
| 149.7 | — |
| 148.8 | — |
| 148.4 | — |
| 149.3 | — |
| 149.1 | — |
| 149.5 | — |
| 150.4 | — |
| 150 | — |
| 151 | — |
| 150.3 | — |
| 150 | — |
| 150 | — |
| 150.4 | — |
| 150.8 | — |
| 149.5 | — |
| 150 | — |
| 150.2 | — |
| 151.1 | — |
| 151.1 | — |
| 151.3 | — |
| 151.1 | — |
| 150.2 | — |
| 151.3 | — |
| 152.9 | — |
| 152 | — |
| 152.1 | — |
| 152.7 | — |
| 151.3 | — |
| 152.2 | — |
| 154.1 | — |
| 153.3 | — |
| 152.2 | — |
| 152.9 | — |
| 152.2 | — |
| 153.1 | — |
| 153.1 | — |
| 153.2 | — |
| 153.4 | — |
| 154.9 | — |
| 153.4 | — |
| 153.5 | — |
| 153.4 | — |
| 153.8 | — |
| 154 | — |
| 154 | — |
| 154.7 | — |
| 155.4 | — |
| 154.5 | — |
| 155.2 | — |
| 154.9 | — |
| 155.6 | — |
| 155.4 | — |
| 155.7 | — |
| 155.8 | — |
| 156.9 | — |
| 156.9 | — |
| 156.2 | — |
| 155.3 | — |
| 156.1 | — |
| 157.1 | — |
| 158.1 | — |
| 158.1 | — |
| 157.1 | — |
| 157.3 | — |
| 157.1 | — |
| 157.9 | — |
| 158.5 | — |
| 158.3 | — |
| 158 | — |
| 158.9 | — |
| 158.9 | — |
| 160.4 | — |
| 159.6 | — |
| 159.9 | — |
| 160 | — |
| 158.4 | — |
| 160.3 | — |
| 160.3 | — |
| 160 | — |
| 159.3 | — |
| 159.3 | — |
| 160.7 | — |
| 159.7 | — |
| 160.9 | — |
| 161.3 | — |
| 162.4 | — |
| 161.9 | — |
| 162.2 | — |
| 161.8 | — |
| 162 | — |
| 161.9 | — |
| 163 | — |
| 162.8 | — |
| 162 | — |
| 161.8 | — |
| 162.7 | — |
| 161.4 | — |
| 162.2 | — |
| 161.7 | — |
| 162.3 | — |
| 162.1 | — |
| 161.3 | — |
| 162.8 | — |
| 161.3 | — |
| 161.1 | — |
| 163.1 | — |
| 162 | — |
| 161.8 | — |
| 162.3 | — |
| 163.1 | — |
| 162.1 | — |
| 161.9 | — |
| 161.4 | — |
| 162 | — |
| 162 | — |
| 162.6 | — |
| 162.4 | — |
| 162.5 | — |
| 163.6 | — |
| 162 | — |
| 162.7 | — |
| 161.9 | — |
| 162 | — |
| 161.5 | — |
| 162.6 | — |
| 162.6 | — |
| 162.2 | — |
| 162.2 | — |
| 161.4 | — |
| 161.5 | — |
| 162.2 | — |
| 161 | — |
| 161.7 | — |
| 162.8 | — |
| 161.5 | — |
| 160.8 | — |
| 161.4 | — |
| 163 | — |
| 162.5 | — |
| 161.8 | — |
| 161.5 | — |
| 161.4 | — |
| 161 | — |
| 161.7 | — |
| 162.3 | — |
| 161.8 | — |
| 163.5 | — |
| 162.6 | — |
| 160.7 | — |
| 161.6 | — |
| 160.6 | — |
| 161.9 | — |
| 160.8 | — |
| 161.1 | — |
| 161.4 | — |
| 161.8 | — |
| 160.3 | — |
| 162 | — |
| 160.8 | — |
| 161.6 | — |
| 161.6 | — |
| 161.7 | — |
| 162.3 | — |
| 162.3 | — |
| 162 | — |
| 162.8 | — |
| 162.9 | — |
| 161.6 | — |
| 161.6 | — |
| 162 | — |
| 162.8 | — |
| 162 | — |
| 160.8 | — |
| 161 | — |
| 161.5 | — |
| 162.7 | — |
| 161.7 | — |
| 162.1 | — |
| 160.4 | — |
| 162.3 | — |
| 160.4 | — |
| 161.7 | — |
| 161.5 | — |
| 161.8 | — |
| 161 | — |
| 161.3 | — |
| 161.6 | — |
| 161.7 | — |
| 161.3 | — |
| 161.7 | — |
| 162.4 | — |
| 162.2 | — |
| 162.2 | — |
| 163.7 | — |
| 162.5 | — |
| 161.8 | — |
| 162.1 | — |
| 162.7 | — |
| 162.9 | — |
| 160.6 | — |
| 162.2 | — |
| 161.9 | — |
| 162.6 | — |
| 163 | — |
| 162.8 | — |
| 161.9 | — |
| 162.4 | — |
| 162.6 | — |
| 162.8 | — |
| 162.1 | — |
| 161.8 | — |
| 162.3 | — |
| 162.4 | — |
| 161.1 | — |
| 160.8 | — |
| 161.7 | — |
| 162.7 | — |
| 160.5 | — |
| 161.5 | — |
| 161 | — |
| 161.9 | — |
| 161.1 | — |
| 162.1 | — |
| 161.3 | — |
| 162 | — |
| 161.8 | — |
| 161.3 | — |
| 162.4 | — |
| 161.9 | — |
| 162 | — |
| 162.3 | — |
| 161.9 | — |
| 162.8 | — |
| 161.6 | — |
| 162 | — |
| 163.3 | — |
| 162.8 | — |
| 164.2 | — |
| 162.6 | — |
| 162.1 | — |
| 163.3 | — |
| 162.8 | — |
| 162.3 | — |
| 162.5 | — |
| 163.1 | — |
| 161.3 | — |
| 162.6 | — |
| 162.4 | — |
| 163.4 | — |
| 163.2 | — |
| 162 | — |
| 161.8 | — |
| 162 | — |
| 161.4 | — |
| 161.7 | — |
| 162.6 | — |
| 162.1 | — |
| 162.9 | — |
| 162.1 | — |
| 163.4 | — |
| 162.6 | — |
| 162 | — |
| 162.9 | — |
| 161.6 | — |
| 161.3 | — |
| 162.2 | — |
| 161.5 | — |
| 162 | — |
| 161.9 | — |
| 162.4 | — |
| 162.1 | — |
| 162.4 | — |
| 162.3 | — |
| 162.5 | — |
| 161.8 | — |
| 161.9 | — |
| 160.8 | — |
| 162.4 | — |
| 162.2 | — |
| 162.1 | — |
| 161.7 | — |
| 161.6 | — |
| 162.6 | — |
| 161.6 | — |
| 161.8 | — |
| 162 | — |
| 162.9 | — |
| 163.1 | — |
| 162.2 | — |
| 163.4 | 0 |
| 163.3 | 6.892 |
| 163 | 9.627 |
| 163.1 | 11.22 |
| 162.9 | 12.91 |
| 163.7 | 13.47 |
| 163.2 | 14.98 |
| 163.1 | 15.32 |
| 163.4 | 15.29 |
| 163.2 | 15.66 |
| 163 | 16.09 |
| 163.5 | 17.3 |
| 163.3 | 17.48 |
| 163.1 | 18.36 |
| 163.3 | 18.63 |
| 163.3 | 19.49 |
| 163.5 | 19.9 |
| 163.3 | 20.36 |
| 163.3 | 20.38 |
| 162.9 | 20.79 |
| 163.3 | 21.04 |
| 163.1 | 21.91 |
| 162.9 | 22.7 |
| 163.1 | 22.33 |
| 163.3 | 22.47 |
| 163.3 | 23.15 |
| 163.1 | 24.25 |
| 163 | 24.57 |
| 162.5 | 24.52 |
| 162.9 | 25.83 |
| 162.9 | 25.38 |
| 163 | 25.36 |
| 163.2 | 25.97 |
| 162.8 | 27.06 |
| 163.4 | 28.08 |
| 163 | 27.69 |
| 163.1 | 27.91 |
| 163.1 | 28.3 |
| 163 | 28.82 |
| 162.8 | 28.02 |
| 163.3 | 27.92 |
| 162.7 | 28.45 |
| 163 | 28.86 |
| 163.2 | 29.48 |
| 163.4 | 29.73 |
| 162.9 | 29.8 |
| 163.4 | 30.09 |
| 163.4 | 31.24 |
| 163.4 | 30.62 |
| 163.2 | 30.28 |
| 162.9 | 29.94 |
| 163.2 | 29.94 |
| 162.8 | 30.68 |
| 163.4 | 31.05 |
| 163.2 | 30.81 |
| 162.9 | 32.07 |
| 163.2 | 32.95 |
| 163.1 | 34.08 |
| 163.2 | 34.51 |
| 163.3 | 33.97 |
| 163 | 33.89 |
| 163.3 | 32.89 |
| 163.2 | 33.68 |
| 163.1 | 34.97 |
| 163.1 | 35.69 |
| 163.1 | 36 |
| 163.4 | 35.9 |
| 163.1 | 35.86 |
| 163 | 35.87 |
| 163.3 | 36.37 |
| 162.8 | 37.03 |
| 163 | 35.84 |
| 163.2 | 36.25 |
| 163.3 | 36.98 |
| 163 | 36.77 |
| 163 | 37.97 |
| 163 | 37.11 |
| 163 | 37.3 |
| 163.1 | 37.15 |
| 162.9 | 37.23 |
| 162.9 | 37.58 |
| 163 | 36.93 |
| 163.3 | 38.46 |
| 162.8 | 37.48 |
| 162.8 | 38.03 |
| 163.4 | 38.21 |
| 162.9 | 38.78 |
| 163.4 | 39.62 |
| 163.1 | 39.9 |
| 163.2 | 39.98 |
| 163.1 | 39.87 |
| 162.9 | 38.59 |
| 163.2 | 38.23 |
| 163.1 | 38.09 |
| 163.1 | 39.11 |
| 163.1 | 40.86 |
| 163 | 42.69 |
| 163 | 42.1 |
| 162.9 | 42.75 |
| 163.4 | 43.4 |
| 163.2 | 42.92 |
| 162.9 | 42.6 |
| 162.9 | 44.15 |
| 163.4 | 45.19 |
| 162.7 | 45.6 |
| 162.8 | 45.91 |
| 163.4 | 45.3 |
| 162.9 | 45.97 |
| 163.2 | 46 |
| 163.1 | 45.88 |
| 163.1 | 45.45 |
| 163.1 | 45.64 |
| 162.8 | 44.75 |
| 162.8 | 44.97 |
| 162.8 | 44.94 |
| 163.2 | 44.84 |
| 162.4 | 44.05 |
| 163.3 | 44.67 |
| 163.3 | 45.87 |
| 163.4 | 46.67 |
| 162.6 | 46.88 |
| 163 | 47.33 |
| 162.9 | 46.98 |
| 163.3 | 45.95 |
| 163.1 | 45.16 |
| 163.3 | 45.47 |
| 163.1 | 46.57 |
| 163 | 45.62 |
| 163.1 | 46.03 |
| 162.9 | 46.23 |
| 163.5 | 46.84 |
| 163 | 45.79 |
| 162.7 | 46.87 |
| 162.8 | 46.85 |
| 162.9 | 48.87 |
| 162.7 | 48.81 |
| 163.1 | 48.86 |
| 162.8 | 48.59 |
| 162.8 | 48.08 |
| 162.8 | 47.06 |
| 163.1 | 46.76 |
| 162.7 | 45.91 |
| 163 | 44.54 |
| 163.1 | 45.9 |
| 163 | 48.29 |
| 163.2 | 48.39 |
| 163.1 | 47.88 |
| 162.9 | 48.43 |
| 163.4 | 47.98 |
| 162.5 | 47.81 |
| 162.9 | 47.67 |
| 163 | 48.35 |
| 163 | 48.65 |
| 162.6 | 47.86 |
| 162.7 | 48.3 |
| 162.8 | 48.14 |
| 162.9 | 48.18 |
| 162.8 | 49.11 |
| 163 | 49.5 |
| 163.1 | 49.6 |
| 162.9 | 49.38 |
| 162.9 | 49.53 |
| 162.9 | 49.62 |
| 162.9 | 50.55 |
| 163 | 51.46 |
| 162.9 | 51.33 |
| 163 | 50.27 |
| 163.1 | 51.39 |
| 162.9 | 53.03 |
| 162.8 | 53.62 |
| 163.1 | 53.17 |
| 162.8 | 53.06 |
| 162.9 | 53.18 |
| 162.8 | 52.93 |
| 163.1 | 52.29 |
| 163.2 | 51.7 |
| 162.9 | 51.44 |
| 162.8 | 51.58 |
| 162.8 | 52.84 |
| 162.8 | 52.85 |
| 162.6 | 53.07 |
| 162.8 | 54.05 |
| 162.6 | 55.12 |
| 163 | 54.48 |
| 163.1 | 54.66 |
| 162.8 | 54.84 |
| 162.8 | 54.48 |
| 163.1 | 56.21 |
| 162.9 | 56.63 |
| 162.9 | 55.48 |
| 163 | 55.67 |
| 162.7 | 56.02 |
| 163.2 | 56.59 |
| 162.8 | 56.75 |
| 163.3 | 56.77 |
| 162.7 | 58.33 |
| 162.6 | 58.27 |
| 162.8 | 58.79 |
| 162.9 | 56.66 |
| 162.8 | 57.07 |
| 162.8 | 57.53 |
| 163.1 | 57.5 |
| 163 | 57.32 |
| 162.7 | 57.53 |
| 162.8 | 56.87 |
| 163.2 | 57.6 |
| 162.9 | 57.91 |
| 163 | 57.82 |
| 162.9 | 58.11 |
| 162.7 | 57.98 |
| 162.6 | 59.34 |
| 162.9 | 59.36 |
| 162.8 | 58.93 |
| 163 | 58.04 |
| 163 | 60.4 |
| 162.6 | 59.87 |
| 162.7 | 59.81 |
| 162.9 | 59.7 |
| 162.8 | 59.25 |
| 162.9 | 57.56 |
| 162.9 | 57.71 |
| 162.7 | 59.19 |
| 162.8 | 59.26 |
| 162.7 | 58.82 |
| 162.7 | 59.53 |
| 162.8 | 59.39 |
| 163.1 | 59.55 |
| 162.9 | 60.6 |
| 163.3 | 60.68 |
| 163.1 | 61.47 |
| 163.2 | 60.7 |
| 162.6 | 60.82 |
| 162.5 | 59.65 |
| 162.8 | 58.99 |
| 162.9 | 59.11 |
| 162.9 | 59.85 |
| 162.9 | 61.53 |
| 163 | 61.57 |
| 163.2 | 60.79 |
| 163.1 | 61.19 |
| 162.8 | 61.89 |
| 163.1 | 64.16 |
| 163.2 | 62.45 |
| 163.1 | 62.48 |
| 162.7 | 61.43 |
| 163.1 | 61.91 |
| 162.9 | 64.05 |
| 162.9 | 63.43 |
| 162.9 | 64.43 |
| 162.7 | 64.26 |
| 163.2 | 63.6 |
| 163 | 64.04 |
| 163 | 63.81 |
| 162.8 | 65.7 |
| 162.7 | 66.9 |
| 162.8 | 66.43 |
| 162.9 | 65.34 |
| 163 | 65.57 |
| 163.1 | 65.63 |
| 162.5 | 66.35 |
| 162.7 | 65.71 |
| 162.8 | 65.13 |
| 162.9 | 65.07 |
| 163.1 | 65.03 |
| 163.1 | 65.75 |
| 162.8 | 66.69 |
| 162.5 | 66.88 |
| 162.8 | 66.75 |
| 162.8 | 66.26 |
| 163.1 | 66.31 |
| 163.1 | 66.11 |
| 162.7 | 66.18 |
| 162.9 | 67.79 |
| 162.8 | 69.19 |
| 163 | 67.86 |
| 163.4 | 68.46 |
| 163 | 70.44 |
| 162.7 | 68.22 |
| 162.8 | 69.4 |
| 163.1 | 70.31 |
| 162.9 | 69.08 |
| 162.8 | 68.11 |
| 163.1 | 69.45 |
| 162.6 | 69.15 |
| 162.8 | 69.44 |
| 163 | 69.67 |
| 162.8 | 70.76 |
| 162.9 | 70.38 |
| 162.6 | 69.7 |
| 162.6 | 71.85 |
| 162.9 | 71.55 |
| 163.1 | 71.82 |
| 162.8 | 71.6 |
| 163 | 71.63 |
| 163.1 | 71.88 |
| 162.7 | 72.78 |
| 162.6 | 72.53 |
| 162.7 | 71.39 |
| 162.8 | 72.06 |
| 162.7 | 72.46 |
| 163 | 72.71 |
| 163.1 | 73.76 |
| 162.9 | 74.25 |
| 162.6 | 74.09 |
| 162.7 | 74.46 |
| 163.1 | 75.39 |
| 162.8 | 76.27 |
| 162.7 | 76.78 |
| 162.7 | 76.39 |
| 162.6 | 75.49 |
| 162.9 | 75.16 |
| 163 | 76.05 |
| 162.9 | 75.23 |
| 162.6 | 75.54 |
| 162.9 | 75.6 |
| 162.8 | 76.85 |
| 162.8 | 75.98 |
| 162.6 | 76.93 |
| 163.4 | 77.35 |
| 162.7 | 78.7 |
| 163.1 | 78.79 |
| 162.7 | 79.15 |
| 162.8 | 78.73 |
| 162.7 | 77.77 |
| 163.2 | 79.2 |
| 162.8 | 79.63 |
| 163.2 | 78.85 |
| 163 | 80.32 |
| 162.8 | 79.75 |
| 163.2 | 79 |
| 162.8 | 79.64 |
| 162.9 | 79.92 |
| 162.7 | 79.88 |
| 162.7 | 79.68 |
| 163.2 | 80.35 |
| 162.9 | 80.37 |
| 162.9 | 80.23 |
| 163 | 80.75 |
| 163.2 | 81.24 |
| 163 | 79.78 |
| 162.2 | 79.52 |
| 162.9 | 80.61 |
| 162.9 | 80.34 |
| 162.5 | 82.63 |
| 162.9 | 84.1 |
| 162.8 | 83.1 |
| 162.7 | 83.84 |
| 162.6 | 83.28 |
| 163.1 | 83.05 |
| 163 | 82.69 |
| 162.9 | 81.55 |
| 162.8 | 81.55 |
| 162.8 | 83.76 |
| 163.2 | 83.69 |
| 162.9 | 82.93 |
| 162.8 | 81.58 |
| 163 | 82 |
| 163 | 83.65 |
| 163 | 84.57 |
| 163.2 | 84 |
| 162.6 | 83.91 |
| 162.7 | 83.96 |
| 162.8 | 82.68 |
| 163 | 82.65 |
| 162.8 | 82.15 |
| 162.8 | 82.49 |
| 162.9 | 82.13 |
| 163 | 82.3 |
| 162.9 | 83.48 |
| 162.8 | 85.22 |
| 163 | 84.68 |
| 163 | 84.09 |
| 163.1 | 83.67 |
| 162.9 | 84.01 |
| 162.8 | 84.22 |
| 163 | 84.04 |
| 162.9 | 84.33 |
| 162.5 | 84.23 |
| 162.8 | 85.62 |
| 163 | 84.55 |
| 162.7 | 83.89 |
| 162.8 | 83.66 |
| 162.9 | 82.89 |
| 163 | 82.63 |
| 162.8 | 82.73 |
| 163.1 | 83.12 |
| 162.5 | 83.63 |
| 163.1 | 84.19 |
| 163.2 | 83.79 |
| 162.7 | 82.89 |
| 162.8 | 83.17 |
| 162.7 | 84.82 |
| 162.7 | 84.82 |
| 162.8 | 85.12 |
| 163 | 86.07 |
| 162.9 | 86.03 |
| 162.9 | 86.6 |
| 162.9 | 86.87 |
| 163.1 | 87.07 |
| 162.9 | 85.88 |
| 162.9 | 87.22 |
| 162.9 | 86.33 |
| 162.8 | 89.37 |
| 163 | 89.86 |
| 162.6 | 92.55 |
| 162.7 | 96.59 |
| 162.9 | 95.63 |
| 162.7 | 96.5 |
| 162.8 | 96.44 |
| 162.6 | 101.9 |
| 162.8 | 100.5 |
| 162.9 | 102.7 |
| 163.1 | 100.8 |
| 162.9 | 101.3 |
| 162.9 | 104.3 |
| 162.6 | 107.8 |
| 162.7 | 108.2 |
| 162.9 | 104.8 |
| 162.8 | 106.5 |
| 162.6 | 106.4 |
| 163.1 | 111.1 |
| 163.1 | 110.7 |
| 162.9 | 112.8 |
| 163.1 | 116.6 |
| 163 | 115.8 |
| 163.4 | 116.5 |
| 162.9 | 117.6 |
| 163.1 | 116.5 |
| 162.6 | 117.1 |
| 162.6 | 119.1 |
| 163.1 | 120.2 |
| 163 | 122.3 |
| 162.7 | 121 |
| 162.8 | 122.9 |
| 163.4 | 121 |
| 163 | 121.8 |
| 162.7 | 125.1 |
| 162.8 | 127.3 |
| 162.8 | 124.5 |
| 163.1 | 126.6 |
| 162.8 | 128.7 |
| 162.6 | 129 |
| 162.5 | 128.5 |
| 162.6 | 129.6 |
| 163 | 133.9 |
| 162.8 | 127 |
| 163.1 | 127.4 |
| 162.9 | 128.8 |
| 162.9 | 129.2 |
| 162.8 | 130.9 |
| 163 | 130.5 |
| 162.9 | 129.6 |
| 162.9 | 131.4 |
| 162.9 | 131.9 |
| 163.1 | 129.5 |
| 162.9 | 134.8 |
| 163 | 133.5 |
| 162.9 | 133.2 |
| 162.9 | 134 |
| 163.1 | 132.5 |
| 162.7 | 131.9 |
| 162.9 | 134.2 |
| 162.7 | 137.1 |
| 162.6 | 137.3 |
| 163.1 | 136.4 |
| 163.1 | 139 |
| 162.9 | 137.7 |
| 162.8 | 139.6 |
| 163.2 | 143.5 |
| 162.7 | 145.5 |
| 162.8 | 147.1 |
| 163.1 | 150.1 |
| 162.8 | 142.8 |
| 162.8 | 144.8 |
| 162.9 | 144.7 |
| 162.6 | 148.1 |
| 162.8 | 144.9 |
| 162.8 | 146.4 |
| 162.7 | 147.7 |
| 162.5 | 146.9 |
| 163 | 152.5 |
| 162.6 | 152.7 |
| 162.9 | 148.6 |
| 162.8 | 149.2 |
| 162.7 | 151.1 |
| 162.9 | 145.3 |
| 163 | 152.1 |
| 162.9 | 149.9 |
| 162.9 | 151.9 |
| 162.8 | 148.5 |
| 162.5 | 152.8 |
| 162.8 | 152.9 |
| 162.8 | 152.3 |
| 162.8 | 154.3 |
| 162.8 | 154.8 |
| 163 | 158.2 |
| 162.8 | 160.4 |
| 162.9 | 161.6 |
| 163.4 | 164 |
| 162.9 | 162.2 |
| 163 | 164.2 |
| 162.7 | 167.7 |
| 163.1 | 166.4 |
| 163 | 167 |
| 163 | 167.4 |
| 162.9 | 165.9 |
| 163.1 | 172.3 |
| 162.5 | 172.6 |
| 163 | 171.7 |
| 162.7 | 172.4 |
| 162.6 | 171.4 |
| 162.4 | 177.3 |
| 163 | 172.9 |
| 162.8 | 178.5 |
| 163.2 | 181.5 |
| 162.8 | 184.1 |
| 162.6 | 184.9 |
| 163.1 | 185.9 |
| 162.8 | 187.8 |
| 162.9 | 186.6 |
| 162.5 | 186.5 |
| 163 | 189.7 |
| 162.6 | 182.7 |
| 162.5 | 184.5 |
| 162.8 | 185.4 |
| 162.8 | 184.1 |
| 163 | 186.9 |
| 162.6 | 191.2 |
| 163 | 193.9 |
| 163.1 | 194.3 |
| 162.8 | 194.4 |
| 162.7 | 193.5 |
| 162.6 | 196.1 |
| 162.7 | 197.2 |
| 162.9 | 192.6 |
| 163.1 | 193.8 |
| 162.6 | 195.6 |
| 162.6 | 197.4 |
| 162.9 | 197.8 |
| 162.9 | 196.1 |
| 163 | 197.1 |
| 162.7 | 197.6 |
| 162.9 | 204 |
| 162.9 | 204.5 |
| 162.8 | 203.6 |
| 162.2 | 207.9 |
| 162.9 | 210.6 |
| 162.9 | 211.3 |
| 162.6 | 209.3 |
| 162.7 | 206.3 |
| 162.5 | 211.8 |
| 162.4 | 212 |
| 162.4 | 212 |
| 162.6 | 211.9 |
| 163 | 217 |
| 162.5 | 216.5 |
| 162.6 | 218.1 |
| 162.8 | 215.8 |
| 162.6 | 220.7 |
| 162.4 | 225.1 |
| 162.9 | 221 |
| 162.7 | 220.5 |
| 162.6 | 218.4 |
| 163 | 215.2 |
| 162.5 | 218.9 |
| 162.4 | 219.6 |
| 162.9 | 220.3 |
| 163 | 224.2 |
| 162.9 | 226.2 |
| 162.5 | 228.7 |
| 162.8 | 231.2 |
| 162.8 | 240.1 |
| 163 | 237.7 |
| 162.8 | 244.3 |
| 162.7 | 244.3 |
| 162.5 | 240.9 |
| 163.2 | 244.7 |
| 162.5 | 247.7 |
| 162.8 | 248 |
| 162.9 | 246.9 |
| 162.7 | 241.8 |
| 162.5 | 244.6 |
| 162.6 | 246 |
| 162.5 | 243.9 |
| 162.6 | 242.8 |
| 163 | 246 |
| 162.9 | 246.1 |
| 162.9 | 244.6 |
| 162.5 | 247.6 |
| 163 | 251.4 |
| 163.4 | 248.3 |
| 162.6 | 252.4 |
| 162.9 | 252.6 |
| 162.7 | 251.3 |
| 161.9 | 248.7 |
| 162.9 | 252 |
| 162.7 | 246.6 |
| 162.7 | 247 |
| 162.7 | 251.5 |
| 162.7 | 248.9 |
| 162.9 | 254.1 |
| 162.7 | 255.2 |
| 162.6 | 259.6 |
| 162.8 | 260 |
| 162.6 | 256.6 |
| 163 | 252 |
| 163 | 258.1 |
| 163 | 255.7 |
| 162.9 | 255.1 |
| 162.8 | 257.2 |
| 162.7 | 258.1 |
| 162.9 | 264.3 |
| 163.2 | 260.4 |
| 163 | 263.1 |
| 162.8 | 264.1 |
| 162.6 | 263.6 |
| 163 | 260.9 |
| 162.8 | 258.5 |
| 162.9 | 264.9 |
| 163 | 260.7 |
| 163.2 | 267.5 |
| 163.2 | 266.8 |
| 162.9 | 260.7 |
| 162.9 | 261.9 |
| 162.8 | 258.8 |
| 162.8 | 258 |
| 162.8 | 261.4 |
| 162.4 | 263.2 |
| 162.9 | 266.9 |
| 162.4 | 271.8 |
| 163.1 | 275.3 |
| 162.8 | 274 |
| 162.8 | 278 |
| 162.5 | 271.9 |
| 162.7 | 271.5 |
| 162.1 | 278.1 |
| 162.5 | 281 |
| 163.2 | 280.2 |
| 163 | 280.7 |
| 162.8 | 279.3 |
| 162.7 | 282.3 |
| 162.8 | 286.4 |
| 162.9 | 289.8 |
| 162.6 | 283.6 |
| 162.8 | 289 |
| 162.8 | 291.4 |
| 162.7 | 296.2 |
| 162.8 | 292 |
| 162.9 | 289.4 |
| 162.9 | 289.1 |
| 162.8 | 285.1 |
| 162.5 | 285.4 |
| 163.1 | 285.2 |
| 162.8 | 288.8 |
| 162.7 | 288.9 |
| 162.6 | 286 |
| 162.8 | 290.1 |
| 162.7 | 288 |
| 162.7 | 290.7 |
| 162.7 | 295.8 |
| 162.6 | 297.3 |
| 162.7 | 298.1 |
| 162.9 | 298.9 |
| 162.6 | 299.1 |
| 162.7 | 303.5 |
| 162.5 | 305.1 |
| 162.9 | 308.2 |
| 162.7 | 309.7 |
| 163 | 309.5 |
| 162.6 | 305.6 |
| 162.9 | 310.9 |
| 162.5 | 310.9 |
| 162.9 | 311.5 |
| 163.1 | 309.6 |
| 162.8 | 311.9 |
| 162.6 | 316.2 |
| 162.5 | 315.1 |
| 162.7 | 319.1 |
| 162.6 | 310.7 |
| 162.8 | 314.6 |
| 162.5 | 312.9 |
| 162.8 | 316.3 |
| 162.6 | 317.9 |
| 162.7 | 313.6 |
| 162.6 | 315.8 |
| 162.7 | 316.2 |
| 162.8 | 314.2 |
| 162.9 | 318.8 |
| 163.1 | 321.1 |
| 162.8 | 322 |
| 162.1 | 318.5 |
| 162.8 | 324.1 |
| 162.5 | 323.8 |
| 162.7 | 326.2 |
| 162.7 | 319.5 |
| 162.8 | 320.6 |
| 162.8 | 322.2 |
| 162.7 | 325.9 |
| 162.7 | 327.3 |
| 163.1 | 322.8 |
| 162.9 | 324.3 |
| 162.8 | 327.2 |
| 162.7 | 324.6 |
| 163 | 328.3 |
| 162.7 | 322.9 |
| 162.3 | 313.8 |
| 162.7 | 318 |
| 162.6 | 316.3 |
| 162.7 | 315.4 |
| 162.4 | 317.9 |
| 162.7 | 328.3 |
| 162.6 | 323.9 |
| 163.1 | 327.6 |
| 162.8 | 326.7 |
| 162.5 | 326.7 |
| 162.8 | 329.4 |
| 162.8 | 329.5 |
| 163 | 327.6 |
| 162.8 | 331.3 |
| 162.1 | 337.9 |
| 162.9 | 339.7 |
| 163 | 341.2 |
| 162.7 | 339 |
| 163 | 340 |
| 162.8 | 337.8 |
| 163.2 | 341.5 |
| 163 | 340.4 |
| 162.8 | 344.5 |
| 162.9 | 341.5 |
| 163.5 | 343.3 |
| 162.7 | 345.2 |
| 163.2 | 342.7 |
| 163.1 | 346.1 |
| 163.1 | 349.3 |
| 162.8 | 348.3 |
| 163.1 | 352.3 |
| 163.1 | 355.6 |
| 162.9 | 355 |
| 162.8 | 352.7 |
| 162.8 | 353.6 |
| 162.8 | 356.1 |
| 162.8 | 354.1 |
| 163 | 358.3 |
| 162.4 | 357.2 |
| 162.7 | 351.7 |
| 162.5 | 356.2 |
| 162.5 | 359.1 |
| 162.9 | 357.2 |
| 162.9 | 354.1 |
| 162.6 | 356.4 |
| 163.2 | 353.5 |
| 162.9 | 352 |
| 162.6 | 352.1 |
| 162.7 | 361.7 |
| 162.6 | 361.2 |
| 163 | 360.1 |
| 163 | 362 |
| 163.1 | 356.6 |
| 162.9 | 365.1 |
| 162.9 | 360.7 |
| 162.8 | 359 |
| 163 | 357.2 |
| 163.2 | 361.6 |
| 162.9 | 359.5 |
| 162.9 | 353.5 |
| 163 | 363.3 |
| 162.8 | 360.1 |
| 163 | 358 |
| 163.1 | 359.5 |
| 162.9 | 362.8 |
| 163 | 362.2 |
| 162.9 | 359 |
| 163 | 360.4 |
| 163.6 | 357.2 |
| 163 | 373.8 |
| 163.1 | 367 |
| 163.1 | 372.1 |
| 163 | 375.8 |
| 163.3 | 377.7 |
| 163.2 | 371.6 |
| 163 | 378.6 |
| 163.1 | 376.8 |
| 163.1 | 371.7 |
| 163.3 | 374 |
| 163.4 | 374.4 |
| 163.1 | 379.7 |
| 162.9 | 383.7 |
| 163.1 | 379.3 |
| 163.3 | 378.7 |
| 162.9 | 378.7 |
| 163 | 385.6 |
| 162.4 | 394 |
| 163.1 | 391.4 |
| 163.3 | 401.7 |
| 163.1 | 404.5 |
| 163.2 | 400.9 |
| 163 | 403.9 |
| 162.9 | 398.8 |
| 162.9 | 390.4 |
| 162.9 | 391.6 |
| 163 | 397.2 |
| 162.7 | 400.2 |
| 163.1 | 402.3 |
| 163.1 | 401.8 |
| 163 | 405.3 |
| 163.5 | 408.1 |
| 163.4 | 416.4 |
| 163.3 | 423.3 |
| 163.6 | 425.5 |
| 163 | 422.7 |
| 163.5 | 423.5 |
| 163.1 | 415.3 |
| 163.1 | 415.3 |
| 163 | 409.4 |
| 162.8 | 413.4 |
| 162.5 | 412.5 |
| 162.6 | 415.9 |
| 162.6 | 419.7 |
| 162.5 | 418.7 |
| 162.8 | 412.6 |
| 162.9 | 419.7 |
| 162.9 | 419.8 |
| 162.9 | 415.2 |
| 163.1 | 416.5 |
| 162.9 | 420.9 |
| 163 | 420.8 |
| 162.9 | 414.2 |
| 163 | 420.1 |
| 162.9 | 414.8 |
| 162.9 | 402.6 |
| 162.5 | 413.2 |
| 163 | 424.3 |
| 162.8 | 426.6 |
| 163.1 | 425.1 |
| 162.6 | 415.9 |
| 162.8 | 413.2 |
| 162.9 | 412.6 |
| 162.8 | 410.8 |
| 162.6 | 407.4 |
| 162.4 | 409.9 |
| 162.5 | 408.5 |
| 162.8 | 410.6 |
| 163 | 407.3 |
| 162.7 | 410.5 |
| 162.6 | 407.7 |
| 162.7 | 410.4 |
| 162.8 | 411.4 |
| 162.9 | 408.9 |
| 162.7 | 407.5 |
| 162.8 | 403.8 |
| 162.7 | 407.6 |
| 162.6 | 417.4 |
| 162.6 | 416.3 |
| 163.1 | 421.7 |
| 162.7 | 426.4 |
| 162.9 | 426.7 |
| 163.2 | 435.4 |
| 163.2 | 435.6 |
| 163.4 | 435.1 |
| 163.1 | 439.9 |
| 162.9 | 441.9 |
| 163.4 | 440 |
| 163 | 433.7 |
| 162.7 | 440.3 |
| 163.2 | 441.9 |
| 162.9 | 447.9 |
| 163.3 | 451.7 |
| 162.5 | 449 |
| 162.4 | 440.5 |
| 163.1 | 450.3 |
| 162.9 | 449.6 |
| 162.5 | 449.2 |
| 162.6 | 436.8 |
| 163 | 441.8 |
| 163 | 439.9 |
| 163.1 | 436.5 |
| 163 | 432.6 |
| 162.2 | 428.9 |
| 162.8 | 435.2 |
| 162.8 | 439.8 |
| 163 | 450.2 |
| 162.5 | 453 |
| 162.6 | 456.5 |
| 162.9 | 451.4 |
| 162.9 | 447.9 |
| 163.1 | 458.9 |
| 162.5 | 447.6 |
| 162.9 | 447.3 |
| 162.7 | 452.7 |
| 163 | 448.8 |
| 162.7 | 447.4 |
| 162.8 | 448.5 |
| 163 | 446.6 |
| 163.1 | 457 |
| 162.9 | 452.6 |
| 162.7 | 453.5 |
| 163.2 | 455.2 |
| 163 | 453.4 |
| 162.8 | 456.6 |
| 162.9 | 447 |
| 163.2 | 449.8 |
| 163 | 457.1 |
| 163.2 | 455.9 |
| 162.6 | 450 |
| 162.9 | 453.2 |
| 162.7 | 454.2 |
| 163 | 454.3 |
| 162.7 | 450.6 |
| 163.2 | 448.3 |
| 163.2 | 444.4 |
| 162.9 | 450.1 |
| 163 | 441.7 |
| 162.9 | 435.7 |
| 163.4 | 436.5 |
| 163.2 | 435.3 |
| 163 | 438.9 |
| 162.9 | 437.9 |
| 163.3 | 446 |
| 163.1 | 441.7 |
| 163.4 | 438.8 |
| 162.6 | 440.2 |
| 162.5 | 442.8 |
| 162.8 | 437.3 |
| 162.9 | 433.8 |
| 162.9 | 435.9 |
| 162.8 | 439.1 |
| 163.2 | 436.1 |
| 162.9 | 441.8 |
| 163 | 444 |
| 163 | 446.5 |
| 162.7 | 446.7 |
| 163 | 445.1 |
| 163 | 443.7 |
| 163.2 | 450.5 |
| 163.1 | 454.2 |
| 162.9 | 453.8 |
| 163.3 | 454.8 |
| 163.2 | 453.3 |
| 163.1 | 453.7 |
| 163 | 451.9 |
| 163.1 | 455.4 |
| 162.7 | 461.2 |
| 162.9 | 461.3 |
| 162.9 | 455 |
| 162.9 | 467.1 |
| 163 | 468 |
| 162.5 | 467.6 |
| 163.1 | 471.3 |
| 162.9 | 472 |
| 162.8 | 472.1 |
| 163 | 472.5 |
| 162.6 | 473.3 |
| 162.5 | 469.3 |
| 162.6 | 473.3 |
| 162.8 | 477.3 |
| 163 | 472.2 |
| 163.1 | 477.1 |
| 162.7 | 471.7 |
| 163 | 474.9 |
| 163.1 | 478.2 |
| 162.9 | 472.3 |
| 162.8 | 476.5 |
| 163.4 | 475.5 |
| 162.6 | 479.4 |
| 162.9 | 482 |
| 163.3 | 486.8 |
| 163.3 | 486.3 |
| 163 | 487.6 |
| 163 | 488.1 |
| 163 | 493.9 |
| 163.3 | 484.5 |
| 163.4 | 489.1 |
| 163 | 495.4 |
| 163 | 491.5 |
| 163.1 | 500.1 |
| 163.3 | 500.5 |
| 163.3 | 492.1 |
| 163.3 | 492.1 |
| 163.3 | 491 |
| 163.4 | 486.1 |
| 163.2 | 499.8 |
| 163.3 | 504.6 |
| 163.3 | 497.7 |
| 163.3 | 501.3 |
| 162.8 | 505.1 |
| 163.3 | 492.6 |
| 163.2 | 490.8 |
| 163.2 | 495.8 |
| 163 | 501.1 |
| 163.4 | 500.8 |
| 163.1 | 494.7 |
| 163 | 487.1 |
| 163.4 | 488.5 |
| 162.9 | 489 |
| 162.8 | 486.6 |
| 162.9 | 485.6 |
| 163.2 | 483.9 |
| 163 | 491 |
| 163.3 | 495 |
| 162.6 | 498.3 |
| 162.6 | 497.1 |
| 162.7 | 499.5 |
| 163 | 507.1 |
| 163.1 | 502 |
| 163.3 | 503.7 |
| 163.4 | 498.2 |
| 163.4 | 497.4 |
| 163.2 | 496.4 |
| 163 | 493.3 |
| 162.5 | 489.4 |
| 163.4 | 491.2 |
| 163.1 | 483.4 |
| 162.9 | 492.4 |
| 163.3 | 500.8 |
| 163 | 502 |
| 162.7 | 500.6 |
| 163.1 | 509.9 |
| 163.5 | 509.9 |
| 163.3 | 509 |
| 163.2 | 504.5 |
| 163.1 | 498.4 |
| 163.2 | 503.9 |
| 163.1 | 514.1 |
| 163.4 | 504.8 |
| 163.2 | 505.8 |
| 163.1 | 512.7 |
| 163.1 | 511.1 |
| 163.3 | 509.9 |
| 163.7 | 514.3 |
| 164.1 | 518.2 |
| 163.5 | 513.3 |
| 163.5 | 520.1 |
| 163.9 | 524.6 |
| 163.7 | 519.9 |
| 164 | 518.6 |
| 164.4 | 518.9 |
| 163.4 | 518.9 |
| 163.6 | 526.5 |
| 163.6 | 515.8 |
| 163.4 | 520.7 |
| 163.7 | 528.8 |
| 163.9 | 533.1 |
| 163.5 | 534 |
| 163.8 | 535.3 |
| 164 | 534.4 |
| 163.8 | 538 |
| 164 | 530.7 |
| 164 | 526.8 |
| 163.6 | 532.4 |
| 164.2 | 532.6 |
| 164 | 539.3 |
| 164 | 543.5 |
| 163.9 | 542.9 |
| 163.4 | 541.7 |
| 163.7 | 549.3 |
| 163.9 | 544.5 |
| 163.9 | 547.8 |
| 163.9 | 541.3 |
| 163.5 | 551.6 |
| 163.6 | 557 |
| 163.9 | 551.8 |
| 164.2 | 551.8 |
| 164 | 546.1 |
| 163.9 | 550 |
| 163.8 | 555.2 |
| 163.8 | 555 |
| 163.8 | 549.1 |
| 163.7 | 546.9 |
| 163.8 | 544.7 |
| 164.1 | 551.1 |
| 163.9 | 549.8 |
| 164.1 | 560.3 |
| 164.3 | 557.3 |
| 163.8 | 557.1 |
| 164 | 562 |
| 163.8 | 566.5 |
| 164.1 | 566.6 |
| 163.4 | 567.1 |
| 164 | 572.3 |
| 164.2 | 562.5 |
| 164 | 560 |
| 164 | 565.8 |
| 164.3 | 570.2 |
| 164.2 | 565.6 |
| 164.4 | 569.1 |
| 163.8 | 565.2 |
| 164.1 | 583.5 |
| 164.5 | 579.2 |
| 163.8 | 586.5 |
| 164.1 | 593.1 |
| 164 | 581.4 |
| 164 | 586.9 |
| 164 | 586 |
| 164.2 | 585.3 |
| 164.1 | 585.7 |
| 163.5 | 597.6 |
| 164.1 | 596.9 |
| 163.8 | 588.3 |
| 164 | 583 |
| 164.1 | 590.4 |
| 163.8 | 583.4 |
| 163.9 | 584.1 |
| 164.1 | 587 |
| 163.8 | 581.9 |
| 164.3 | 578 |
| 163.8 | 586 |
| 164.3 | 586.6 |
| 163.9 | 589.2 |
| 164.1 | 591 |
| 163.8 | 585.2 |
| 163.8 | 593.6 |
| 163.8 | 597.2 |
| 163.8 | 602.3 |
| 163.7 | 600.8 |
| 163.9 | 599.8 |
| 163.7 | 604.8 |
| 163.8 | 602.5 |
| 163.8 | 601.4 |
| 164 | 603.5 |
| 163.8 | 596.5 |
| 163.8 | 601.8 |
| 164 | 598.8 |
| 164.2 | 603.6 |
| 163.9 | 602.7 |
| 163.6 | 604.5 |
| 163.7 | 603.5 |
| 163.8 | 605.9 |
| 164.2 | 600.1 |
| 163.5 | 604.9 |
| 164.2 | 602.6 |
| 163.7 | 596.4 |
| 163.5 | 597.4 |
| 163.5 | 592.6 |
| 163.6 | 589.5 |
| 163.4 | 594.2 |
| 163.9 | 603.1 |
| 163.9 | 612.6 |
| 163.9 | 623.2 |
| 163.7 | 617.7 |
| 164 | 613.7 |
| 163.8 | 606.2 |
| 163.6 | 603.4 |
| 164.3 | 607.7 |
| 163.8 | 619.4 |
| 163.8 | 616.7 |
| 164.1 | 619.8 |
| 163.8 | 623.4 |
| 163.7 | 615.9 |
| 163.8 | 631.9 |
| 164 | 622.2 |
| 163.7 | 617.5 |
| 163.9 | 613.1 |
| 164 | 617.3 |
| 163.9 | 614.1 |
| 164 | 615.3 |
| 164 | 612 |
| 164.3 | 616.8 |
| 164 | 607.1 |
| 163.8 | 618.6 |
| 163.5 | 618.3 |
| 163.9 | 613.9 |
| 162.3 | 617.1 |
| 157.3 | 619.6 |
| 153.5 | 619.6 |
| 150.6 | 627.4 |
| 149.1 | 631.8 |
| 149.7 | 638.7 |
| 148.1 | 640.2 |
| 146.1 | 646.4 |
| 144.9 | 649.9 |
| 145.3 | 653.2 |
| 143.1 | 655.7 |
| 143.6 | 657.9 |
| 142.3 | 664.1 |
| 142.1 | 666.7 |
| 140.8 | 669 |
| 141.2 | 673.2 |
| 141.9 | 675.7 |
| 141.4 | 678.8 |
| 139.8 | 682.7 |
| 140.3 | 689.7 |
| 139.5 | 692.4 |
| 139.7 | 698.3 |
| 139.8 | 697.6 |
| 139.1 | 697.7 |
| 138.5 | 699 |
| 138.9 | 700.2 |
| 138.4 | 700.5 |
| 138.2 | 701.8 |
| 138.7 | 702.5 |
| 138.5 | 699.8 |
| 138.3 | 711.7 |
| 138 | 717.7 |
| 137.6 | 723 |
| 137.9 | 725.2 |
| 138.4 | 721.3 |
| 138.2 | 724.9 |
| 138.7 | 720.9 |
| 138 | 720.9 |
| 137.5 | 720.7 |
| 137.6 | 716.4 |
| 137.4 | 724.3 |
| 137.5 | 727.2 |
| 137 | 734.5 |
| 137 | 735.7 |
| 136.5 | 737.2 |
| 137.2 | 736.8 |
| 137.1 | 736 |
| 136.4 | 734.8 |
| 136.6 | 737.2 |
| 136.9 | 739.9 |
| 135.2 | 740 |
| 137.2 | 742.7 |
| 137.1 | 740.1 |
| 136.8 | 742.2 |
| 136.6 | 746.6 |
| 136.4 | 742.6 |
| 137 | 743 |
| 136.6 | 742.9 |
| 136.9 | 748.6 |
| 136 | 749.6 |
| 135.7 | 748.5 |
| 135.5 | 753.3 |
| 135.7 | 754.1 |
| 135.1 | 758.1 |
| 135.1 | 760.3 |
| 135.1 | 758.4 |
| 135.3 | 759.4 |
| 135.3 | 760 |
| 135 | 759 |
| 135.7 | 757.4 |
| 135.2 | 760.6 |
| 135 | 762.1 |
| 135.8 | 762.2 |
| 134.4 | 764.8 |
| 134.4 | 763.9 |
| 134.1 | 758.5 |
| 135.7 | 757.9 |
| 135.5 | 758.1 |
| 134.7 | 763.5 |
| 134.8 | 763.1 |
| 134.9 | 763.9 |
| 135.3 | 766.7 |
| 135.1 | 769.9 |
| 134.8 | 769.9 |
| 135 | 776.7 |
| 134.1 | 779.2 |
| 134.2 | 777.8 |
| 134.4 | 780.8 |
| 134 | 780.3 |
| 134.7 | 781.1 |
| 134.7 | 779.2 |
| 134.4 | 785.7 |
| 133.2 | 791.3 |
| 134.6 | 794.6 |
| 134.4 | 796.5 |
| 134.4 | 798.9 |
| 134.4 | 804.6 |
| 134.7 | 808.1 |
| 133.4 | 814.3 |
| 134 | 811.3 |
| 132.9 | 815.3 |
| 134.3 | 821.7 |
| 133.9 | 824.2 |
| 133.2 | 825.5 |
| 133.9 | 828.9 |
| 133.2 | 829.5 |
| 135.1 | 830.1 |
| 134.2 | 832.3 |
| 133.9 | 835.5 |
| 133.8 | 837.2 |
| 133.1 | 837.2 |
| 133 | 840.3 |
| 134.2 | 845.7 |
| 133.7 | 845.2 |
| 133.8 | 844.3 |
| 134 | 845.1 |
| 132.9 | 849.4 |
| 134.7 | 847.4 |
| 133.8 | 847.1 |
| 133.6 | 848.6 |
| 134.4 | 847.2 |
| 134.2 | 852.9 |
| 134 | 854.4 |
| 134.1 | 855 |
| 133.8 | 848.1 |
| 134 | 845.8 |
| 133.7 | 846.7 |
| 134.2 | 847.4 |
| 134.5 | 845.2 |
| 134.1 | 847.9 |
| 134.7 | 845 |
| 134 | 844.4 |
| 133.7 | 839.7 |
| 133.8 | 836.6 |
| 134.2 | 836.8 |
| 134 | 841.8 |
| 133.6 | 847.5 |
| 132.6 | 850.4 |
| 133.9 | 853.6 |
| 133.8 | 855.4 |
| 134.1 | 849.7 |
| 133.8 | 857 |
| 134.3 | 853.9 |
| 134.5 | 860.3 |
| 133.7 | 863.3 |
| 134.2 | 864.6 |
| 134.1 | 864.3 |
| 134.7 | 858.2 |
| 134.8 | 859.2 |
| 134.2 | 860.7 |
| 133.6 | 864 |
| 133.4 | 870.3 |
| 133.6 | 872.3 |
| 133.6 | 874.6 |
| 132.9 | 873.1 |
| 132.9 | 875.2 |
| 133.8 | 880.2 |
| 133.1 | 878.7 |
| 132.8 | 879.7 |
| 133.5 | 884.2 |
| 133.8 | 883.5 |
| 133.7 | 879.2 |
| 133 | 879.5 |
| 133.4 | 880.6 |
| 133.5 | 878 |
| 133.5 | 873.3 |
| 134.8 | 869.2 |
| 133.5 | 871.4 |
| 133.4 | 878.2 |
| 132.9 | 877.4 |
| 133.6 | 884.1 |
| 133.1 | 884.6 |
| 132.9 | 886.1 |
| 133.2 | 880.9 |
| 132.7 | 877.3 |
| 133 | 882.9 |
| 134.2 | 883.8 |
| 133.9 | 882.9 |
| 133.8 | 885.7 |
| 134.9 | 889.4 |
| 133.5 | 894.1 |
| 133.5 | 900 |
| 133.4 | 908.3 |
| 133.3 | 911 |
| 133.8 | 908.1 |
| 133.4 | 905.2 |
| 133.8 | 903.2 |
| 132.9 | 901.3 |
| 133.9 | 898 |
| 134.2 | 897.6 |
| 134.2 | 897.1 |
| 133.7 | 899.7 |
| 133.4 | 906.6 |
| 133.8 | 910.8 |
| 133.5 | 914.9 |
| 133.1 | 914.3 |
| 133.9 | 918.7 |
| 133.5 | 919.2 |
| 133.8 | 920 |
| 134.7 | 919.3 |
| 133.8 | 917.5 |
| 134.1 | 919.5 |
| 133.4 | 921.7 |
| 133.1 | 921 |
| 133.3 | 915.7 |
| 133.7 | 909.6 |
| 134.3 | 911.3 |
| 133.1 | 915.8 |
| 133.5 | 913.6 |
| 133.9 | 911.4 |
| 133 | 914.3 |
| 133 | 917.8 |
| 133.3 | 915.3 |
| 134.1 | 916.6 |
| 133.2 | 914.8 |
| 132.5 | 915.7 |
| 133.4 | 919 |
| 133.1 | 916.3 |
| 134.4 | 914.4 |
| 133.2 | 921.1 |
| 133.2 | 925.1 |
| 132.6 | 928.6 |
| 133.1 | 924.8 |
| 132.9 | 931.1 |
| 134 | 933.7 |
| 132.6 | 934.1 |
| 132.5 | 935.1 |
| 133 | 934.2 |
| 132.9 | 939.6 |
| 132.7 | 940.8 |
| 132.2 | 939.4 |
| 133.6 | 937.5 |
| 133.4 | 934.1 |
| 133.7 | 935.3 |
| 133 | 935.6 |
| 132.7 | 937 |
| 133.2 | 933.9 |
| 133 | 934.3 |
| 132.5 | 937.7 |
| 132.6 | 936.3 |
| 133.1 | 936.3 |
| 133.7 | 936.6 |
| 134 | 936.4 |
| 133.6 | 937.2 |
| 132.5 | 928.9 |
| 133 | 932 |
| 132.9 | 932.7 |
| 133.5 | 932.9 |
| 133.4 | 930.6 |
| 132.3 | 936 |
| 133.6 | 933.9 |
| 133.4 | 942.4 |
| 133.6 | 949.9 |
| 132.9 | 954.9 |
| 133.2 | 953.8 |
| 132.1 | 952.7 |
| 132.4 | 955 |
| 132.2 | 953.2 |
| 132.4 | 959.8 |
| 132.4 | 967.6 |
| 132.7 | 963.1 |
| 132.6 | 960.2 |
| 133.1 | 965.8 |
| 133.7 | 966.1 |
| 132.2 | 966.5 |
| 132.8 | 964.6 |
| 133 | 971.9 |
| 132.7 | 976.3 |
| 132.2 | 972.2 |
| 132.7 | 974 |
| 132.8 | 975.6 |
| 132 | 976.6 |
| 132.6 | 974.5 |
| 132.7 | 974.4 |
| 132.5 | 973.8 |
| 132.3 | 975.7 |
| 133.1 | 976.1 |
| 132.5 | 980.5 |
| 132.9 | 986.1 |
| 132.6 | 989.4 |
| 133 | 986.9 |
| 133.6 | 989.2 |
| 133.3 | 989.6 |
| 133.4 | 991.6 |
| 133.2 | 990.5 |
| 132.7 | 992.5 |
| 133.1 | 996.7 |
| 133.3 | 999.1 |
| 132.8 | 1002 |
| 132.1 | 1005 |
| 132.8 | 1007 |
| 132.4 | 1007 |
| 132.8 | 1009 |
| 132.9 | 1007 |
| 132.2 | 1009 |
| 132.7 | 1000 |
| 133.1 | 1002 |
| 133.3 | 999.3 |
| 132.1 | 1003 |
| 132.5 | 1008 |
| 132.6 | 1011 |
| 133 | 1016 |
| 132.8 | 1014 |
| 132.1 | 1009 |
| 132.5 | 1009 |
| 132 | 1009 |
| 132.1 | 1010 |
| 132.5 | 1011 |
| 132.6 | 1015 |
| 132.2 | 1018 |
| 132 | 1015 |
| 131.8 | 1017 |
| 132.1 | 1013 |
| 133.2 | 1015 |
| 132.3 | 1011 |
| 133 | 1017 |
| 133.5 | 1016 |
| 132.7 | 1024 |
| 132.7 | 1021 |
| 132.5 | 1017 |
| 133.3 | 1012 |
| 133.6 | 1010 |
| 132.7 | 1012 |
| 132.1 | 1013 |
| 132.1 | 1015 |
| 132.9 | 1010 |
| 132.8 | 1012 |
| 133.4 | 1014 |
| 133 | 1013 |
| 132.4 | 1013 |
| 132.1 | 1015 |
| 133.1 | 1012 |
| 133 | 1011 |
| 132.7 | 1009 |
| 131.9 | 1011 |
| 132.2 | 1008 |
| 132.3 | 1007 |
| 132.8 | 1008 |
| 133.5 | 1011 |
| 132.9 | 1013 |
| 132.8 | 1010 |
| 133.7 | 1009 |
| 133.3 | 1009 |
| 133.1 | 1018 |
| 133 | 1018 |
| 132.5 | 1020 |
| 132.8 | 1027 |
| 133 | 1030 |
| 132.6 | 1028 |
| 133.4 | 1031 |
| 133.3 | 1031 |
| 132.6 | 1028 |
| 132.1 | 1026 |
| 132.8 | 1029 |
| 133.1 | 1029 |
| 132.8 | 1028 |
| 131.4 | 1026 |
| 132.1 | 1028 |
| 132.3 | 1031 |
| 133.3 | 1026 |
| 132.5 | 1034 |
| 132.5 | 1038 |
| 132.8 | 1040 |
| 133.1 | 1043 |
| 133.8 | 1044 |
| 133.9 | 1041 |
| 133 | 1042 |
| 133.2 | 1047 |
| 134 | 1045 |
| 134.2 | 1043 |
| 134.4 | 1044 |
| 133.6 | 1047 |
| 133.8 | 1043 |
| 133.5 | 1047 |
| 133.1 | 1044 |
| 133.4 | 1047 |
| 133.5 | 1049 |
| 133.4 | 1054 |
| 133.2 | 1053 |
| 132.1 | 1056 |
| 133.4 | 1055 |
| 133 | 1050 |
| 132.6 | 1051 |
| 132.7 | 1047 |
| 132.1 | 1049 |
| 132.8 | 1052 |
| 133.3 | 1053 |
| 133.3 | 1057 |
| 133 | 1055 |
| 132.7 | 1057 |
| 133.2 | 1062 |
| 133 | 1067 |
| 132.7 | 1066 |
| 133.1 | 1060 |
| 133.1 | 1056 |
| 133 | 1059 |
| 132.8 | 1062 |
| 133.2 | 1061 |
| 134.2 | 1051 |
| 133.6 | 1051 |
| 133.5 | 1068 |
| 132.3 | 1070 |
| 132.6 | 1080 |
| 133.7 | 1104 |
| 132.7 | 1118 |
| 133.3 | 1104 |
| 133.2 | 1114 |
| 133 | 1128 |
| 133.3 | 1140 |
| 132.7 | 1131 |
| 133.2 | 1160 |
| 133.2 | 1174 |
| 133.7 | 1197 |
| 133.8 | 1209 |
| 133.3 | 1212 |
| 132.7 | 1211 |
| 132.7 | 1228 |
| 133.8 | 1233 |
| 133.4 | 1242 |
| 132.7 | 1256 |
| 133 | 1274 |
| 133.1 | 1267 |
| 133.5 | 1247 |
| 132.5 | 1260 |
| 133.4 | 1277 |
| 134.2 | 1286 |
| 133.6 | 1297 |
| 133.5 | 1315 |
| 134.1 | 1330 |
| 133.7 | 1322 |
| 133.3 | 1338 |
| 133 | 1350 |
| 133.2 | 1348 |
| 133.4 | 1355 |
| 133.1 | 1361 |
| 133 | 1360 |
| 132.7 | 1374 |
| 132.6 | 1382 |
| 132.7 | 1411 |
| 133.2 | 1408 |
| 133.1 | 1406 |
| 133.1 | 1402 |
| 132.3 | 1415 |
| 132.8 | 1419 |
| 132.9 | 1423 |
| 132.7 | 1435 |
| 133 | 1425 |
| 133.3 | 1430 |
| 133.3 | 1426 |
| 132.9 | 1428 |
| 133 | 1425 |
| 133.8 | 1429 |
| 132.8 | 1429 |
| 133.5 | 1431 |
| 133.3 | 1421 |
| 132.9 | 1441 |
| 133.1 | 1446 |
| 133.2 | 1475 |
| 133.6 | 1487 |
| 133.6 | 1474 |
| 133.5 | 1485 |
| 132.6 | 1489 |
| 131.8 | 1483 |
| 132.8 | 1480 |
| 132.9 | 1498 |
| 133.8 | 1520 |
| 132.8 | 1521 |
| 133.9 | 1531 |
| 133.8 | 1562 |
| 133.6 | 1575 |
| 133.1 | 1580 |
| 133.2 | 1584 |
| 132.5 | 1589 |
| 133.2 | 1585 |
| 133 | 1590 |
| 134.4 | 1617 |
| 133.3 | 1637 |
| 132.8 | 1647 |
| 133.4 | 1655 |
| 133 | 1651 |
| 132.7 | 1648 |
| 132.8 | 1628 |
| 133 | 1618 |
| 133.3 | 1609 |
| 132.8 | 1623 |
| 132.8 | 1618 |
| 133.9 | 1639 |
| 134 | 1653 |
| 133 | 1670 |
| 132.7 | 1695 |
| 133.5 | 1707 |
| 134.2 | 1715 |
| 133.6 | 1713 |
| 133.3 | 1709 |
| 134 | 1706 |
| 133.6 | 1716 |
| 132.9 | 1720 |
| 133.3 | 1716 |
| 133.8 | 1723 |
| 133.3 | 1751 |
| 133.1 | 1756 |
| 133.2 | 1736 |
| 133.3 | 1742 |
| 133.5 | 1754 |
| 132.8 | 1747 |
| 133.2 | 1767 |
| 133.1 | 1785 |
| 133.7 | 1772 |
| 132.8 | 1775 |
| 133.8 | 1781 |
| 133.7 | 1795 |
| 134.1 | 1779 |
| 134.3 | 1785 |
| 133.7 | 1779 |
| 133.3 | 1775 |
| 133.2 | 1776 |
| 132.7 | 1791 |
| 133.1 | 1780 |
| 133.5 | 1801 |
| 133.4 | 1798 |
| 133.1 | 1806 |
| 133.8 | 1792 |
| 133.5 | 1798 |
| 133 | 1812 |
| 132.8 | 1834 |
| 133.1 | 1851 |
| 132.6 | 1854 |
| 133.9 | 1882 |
| 133 | 1879 |
| 133 | 1873 |
| 133.4 | 1850 |
| 132.9 | 1851 |
| 132.6 | 1840 |
| 133.3 | 1855 |
| 133 | 1872 |
| 133.5 | 1863 |
| 132.7 | 1861 |
| 132.8 | 1891 |
| 132.6 | 1901 |
| 133.8 | 1898 |
| 133.2 | 1884 |
| 133.3 | 1905 |
| 133.1 | 1898 |
| 133.7 | 1914 |
| 134 | 1897 |
| 133.6 | 1909 |
| 133.7 | 1918 |
| 132.7 | 1940 |
| 132.9 | 1952 |
| 133 | 1960 |
| 133.7 | 1966 |
| 132.9 | 1955 |
| 133.1 | 1968 |
| 133.2 | 1993 |
| 133.4 | 1980 |
| 133.1 | 1976 |
| 132.9 | 1986 |
| 132.9 | 1991 |
| 133.2 | 2001 |
| 133.2 | 2029 |
| 133.7 | 2015 |
| 133.3 | 2009 |
| 133 | 2015 |
| 132.8 | 2007 |
| 132.4 | 2001 |
| 133.8 | 2014 |
| 133.3 | 2026 |
| 133.7 | 2039 |
| 133.1 | 2052 |
| 132.3 | 2052 |
| 132.8 | 2044 |
| 132.7 | 2028 |
| 132.8 | 2071 |
| 133.2 | 2066 |
| 133.5 | 2079 |
| 133.2 | 2084 |
| 132.9 | 2095 |
| 133.4 | 2096 |
| 132.3 | 2077 |
| 133.2 | 2086 |
| 132.9 | 2071 |
| 133 | 2088 |
| 132.6 | 2091 |
| 133.1 | 2102 |
| 133.8 | 2091 |
| 133 | 2106 |
| 133.8 | 2090 |
| 133.4 | 2100 |
| 132.9 | 2083 |
| 134.2 | 2103 |
| 133.2 | 2106 |
| 133 | 2106 |
| 133.3 | 2100 |
| 133.8 | 2115 |
| 133.8 | 2116 |
| 133 | 2129 |
| 133.1 | 2133 |
| 133.7 | 2132 |
| 133.3 | 2140 |
| 132.2 | 2146 |
| 133.3 | 2152 |
| 133.3 | 2167 |
| 133.1 | 2189 |
| 133.3 | 2183 |
| 132.4 | 2190 |
| 133.2 | 2188 |
| 133.5 | 2211 |
| 133 | 2214 |
| 132.7 | 2256 |
| 133.4 | 2246 |
| 132.8 | 2232 |
| 133.8 | 2217 |
| 133.8 | 2187 |
| 133.3 | 2173 |
| 133.6 | 2169 |
| 133.7 | 2163 |
| 132.6 | 2177 |
| 132.6 | 2183 |
| 133.5 | 2188 |
| 132.6 | 2209 |
| 133.2 | 2232 |
| 133.6 | 2226 |
| 132.8 | 2246 |
| 133.9 | 2224 |
| 133.3 | 2227 |
| 133.1 | 2231 |
| 133.2 | 2222 |
| 133.4 | 2230 |
| 133.6 | 2229 |
| 133.4 | 2252 |
| 133.9 | 2242 |
| 133.6 | 2220 |
| 134.2 | 2237 |
| 134.1 | 2208 |
| 133.5 | 2231 |
| 133.7 | 2218 |
| 133.3 | 2219 |
| 133.9 | 2211 |
| 133.5 | 2208 |
| 133.4 | 2219 |
| 134.5 | 2235 |
| 133.5 | 2226 |
| 133.3 | 2242 |
| 133.9 | 2230 |
| 133.8 | 2243 |
| 134 | 2251 |
| 132.8 | 2267 |
| 133.8 | 2257 |
| 132.5 | 2271 |
| 133.7 | 2254 |
| 133 | 2249 |
| 133.8 | 2255 |
| 132.8 | 2249 |
| 133.7 | 2247 |
| 133.8 | 2245 |
| 134.1 | 2273 |
| 134.1 | 2269 |
| 133.3 | 2285 |
| 133.2 | 2286 |
| 134.4 | 2281 |
| 133.8 | 2282 |
| 133.5 | 2279 |
| 134.7 | 2299 |
| 134.1 | 2304 |
| 134.5 | 2304 |
| 133.8 | 2321 |
| 133.9 | 2329 |
| 133.4 | 2343 |
| 134.1 | 2330 |
| 133.5 | 2333 |
| 133.6 | 2323 |
| 133.8 | 2327 |
| 133.9 | 2333 |
| 133.3 | 2328 |
| 133.2 | 2318 |
| 132.7 | 2327 |
| 132.9 | 2334 |
| 132.9 | 2338 |
| 133.1 | 2333 |
| 133.4 | 2324 |
| 133.7 | 2360 |
| 133.3 | 2357 |
| 134.1 | 2348 |
| 134.1 | 2374 |
| 134 | 2381 |
| 134.5 | 2372 |
| 134.1 | 2386 |
| 134.3 | 2394 |
| 133.9 | 2395 |
| 133.3 | 2377 |
| 133.2 | 2377 |
| 133.5 | 2389 |
| 133.4 | 2407 |
| 133.3 | 2420 |
| 133.8 | 2405 |
| 134.1 | 2407 |
| 133.6 | 2394 |
| 134.7 | 2403 |
| 134 | 2405 |
| 133.6 | 2409 |
| 133.3 | 2444 |
| 133.6 | 2453 |
| 133.2 | 2448 |
| 133.6 | 2457 |
| 133.5 | 2468 |
| 134.3 | 2470 |
| 133.6 | 2454 |
| 134.5 | 2454 |
| 132.9 | 2450 |
| 133.5 | 2484 |
| 134.5 | 2465 |
| 134.1 | 2455 |
| 133.6 | 2487 |
| 134.7 | 2491 |
| 134.7 | 2487 |
| 133.7 | 2492 |
| 134.8 | 2510 |
| 135.1 | 2523 |
| 133.4 | 2517 |
| 134.2 | 2511 |
| 133.6 | 2534 |
| 133.9 | 2510 |
| 135 | 2522 |
| 133.4 | 2532 |
| 134.3 | 2537 |
| 134.4 | 2553 |
| 133.9 | 2544 |
| 134.5 | 2564 |
| 134.3 | 2554 |
| 134.4 | 2557 |
| 134.3 | 2586 |
| 135.9 | 2573 |
| 134.8 | 2551 |
| 134.3 | 2579 |
| 133.8 | 2582 |
| 134.5 | 2603 |
| 134.4 | 2596 |
| 133.3 | 2587 |
| 134.2 | 2597 |
| 134.4 | 2577 |
| 132.9 | 2611 |
| 133.8 | 2620 |
| 134.1 | 2626 |
| 133.8 | 2647 |
| 133.6 | 2651 |
| 134.6 | 2653 |
| 133.8 | 2646 |
| 133 | 2646 |
| 134.1 | 2647 |
| 134 | 2633 |
| 134 | 2645 |
| 133.6 | 2647 |
| 134.1 | 2643 |
| 134.3 | 2612 |
| 133.8 | 2628 |
| 134 | 2645 |
| 134.3 | 2636 |
| 134.6 | 2656 |
| 133.8 | 2644 |
| 134.1 | 2659 |
| 134.7 | 2657 |
| 134.1 | 2631 |
| 133.9 | 2600 |
| 135.2 | 2614 |
| 133.4 | 2663 |
| 133.1 | 2661 |
| 134 | 2664 |
| 133.3 | 2671 |
| 134.5 | 2666 |
| 134.1 | 2680 |
| 134.3 | 2665 |
| 133.3 | 2649 |
| 133.7 | 2655 |
| 134.9 | 2686 |
| 135.5 | 2684 |
| 134 | 2653 |
| 134.2 | 2645 |
| 134 | 2624 |
| 135.3 | 2642 |
| 134.6 | 2655 |
| 133.6 | 2670 |
| 134.5 | 2645 |
| 134.7 | 2647 |
| 134.6 | 2666 |
| 133.6 | 2707 |
| 133.1 | 2687 |
| 134.2 | 2705 |
| 134.5 | 2707 |
| 133.7 | 2718 |
| 134 | 2701 |
| 134 | 2703 |
| 134 | 2710 |
| 134.4 | 2727 |
| 134.1 | 2725 |
| 134.5 | 2719 |
| 134.2 | 2733 |
| 134.6 | 2728 |
| 133.5 | 2719 |
| 133.9 | 2734 |
| 134.5 | 2737 |
| 133.1 | 2743 |
| 134.2 | 2772 |
| 134 | 2769 |
| 135.3 | 2789 |
| 133.6 | 2820 |
| 134 | 2840 |
| 133.5 | 2837 |
| 133.7 | 2839 |
| 133.3 | 2877 |
| 134.3 | 2886 |
| 133.9 | 2856 |
| 133.7 | 2835 |
| 133.9 | 2856 |
| 133.7 | 2876 |
| 134.1 | 2849 |
| 135.3 | 2842 |
| 134.5 | 2855 |
| 134.4 | 2878 |
| 135.1 | 2896 |
| 134.7 | 2876 |
| 133.3 | 2884 |
| 133.4 | 2882 |
| 133.9 | 2895 |
| 134.3 | 2905 |
| 133.1 | 2912 |
| 133.3 | 2921 |
| 133.7 | 2911 |
| 134.3 | 2896 |
| 134.4 | 2926 |
| 134 | 2908 |
| 134.3 | 2913 |
| 134.7 | 2913 |
| 135.1 | 2893 |
| 134.9 | 2911 |
| 134.6 | 2912 |
| 134.4 | 2913 |
| 134.7 | 2932 |
| 134.8 | 2928 |
| 134.5 | 2920 |
| 133.8 | 2948 |
| 133.9 | 2932 |
| 133 | 2953 |
| 134.9 | 2961 |
| 133.7 | 2970 |
| 133.6 | 2982 |
| 134.4 | 2962 |
| 133.9 | 2965 |
| 134.3 | 2982 |
| 133.9 | 2990 |
| 133.7 | 3021 |
| 133.3 | 3002 |
| 133.7 | 3009 |
| 134.2 | 2999 |
| 134.6 | 3034 |
| 133.8 | 3038 |
| 134.2 | 3020 |
| 135.5 | 3025 |
| 134.3 | 3046 |
| 134.5 | 3040 |
| 133.6 | 3032 |
| 133.4 | 3017 |
| 133.7 | 3037 |
| 133.8 | 3040 |
| 133.6 | 3038 |
| 134.4 | 3047 |
| 133.8 | 3015 |
| 133.4 | 3024 |
| 134.6 | 3045 |
| 133.9 | 3040 |
| 134.8 | 3020 |
| 134 | 3041 |
| 134.3 | 3031 |
| 134.8 | 3048 |
| 134.2 | 3023 |
| 134.7 | 3044 |
| 133.6 | 3059 |
| 134.4 | 3053 |
| 134.1 | 3024 |
| 133.4 | 3016 |
| 133.6 | 2985 |
| 134.5 | 3001 |
| 134.3 | 3001 |
| 134.8 | 3025 |
| 134.6 | 3063 |
| 135.1 | 3080 |
| 134.7 | 3102 |
| 133.9 | 3100 |
| 134.5 | 3098 |
| 134.4 | 3105 |
| 133.7 | 3123 |
| 134.9 | 3094 |
| 133.6 | 3131 |
| 134.4 | 3088 |
| 133.9 | 3092 |
| 134.7 | 3097 |
| 134.3 | 3092 |
| 134.4 | 3068 |
| 134.2 | 3067 |
| 133.9 | 3076 |
| 134.7 | 3128 |
| 134.1 | 3116 |
| 134.4 | 3113 |
| 134.3 | 3118 |
| 134.3 | 3125 |
| 135 | 3138 |
| 133.7 | 3146 |
| 134 | 3129 |
| 133.3 | 3150 |
| 134.3 | 3128 |
| 133.8 | 3125 |
| 134.5 | 3128 |
| 134 | 3100 |
| 134.9 | 3122 |
| 134 | 3104 |
| 134.8 | 3098 |
| 134 | 3091 |
| 134.5 | 3114 |
| 134.2 | 3104 |
| 134.7 | 3114 |
| 134.2 | 3159 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |


**`hole_ramp_rel130_col` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 129.4
- `free_shell.areal_density_ratio`: 0.8913
- `free_shell.msd.1 ns`: 189.9
- `free_shell.msd.10 ns`: 649.5
- `free_shell.msd.end`: 3166
- `free_shell.msd.end_ns`: 68
- `params.hole_hold_ps`: 1e+04
- `params.release_t_c`: 130
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `scaffold.d_nm`: 2.5
- `scaffold.nearest_tethered_r_held_min`: 52.11
- `scaffold.nearest_tethered_r_t0`: 53.84
- `scaffold.tethered_fraction`: 0.1159
- T (°C): 25
- `t_close_ns`: 1.37
- `thickness_final`: 134.7
- `thickness_t0`: 161.4

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 129.8 | — |
| 129.8 | — |
| 129.5 | — |
| 129.6 | — |
| 129.2 | — |
| 129.9 | — |
| 129.7 | — |
| 129.6 | — |
| 130 | — |
| 129.7 | — |
| 129.6 | — |
| 129.8 | — |
| 129.6 | — |
| 131.1 | — |
| 129.6 | — |
| 130 | — |
| 129.5 | — |
| 129.6 | — |
| 130 | — |
| 129.6 | — |
| 129.3 | — |
| 129.9 | — |
| 128.8 | — |
| 129.4 | — |
| 129.8 | — |
| 129.3 | — |
| 129.9 | — |
| 129.5 | — |
| 129.8 | — |
| 130 | — |
| 129.5 | — |
| 130.4 | — |
| 129.5 | — |
| 129.9 | — |
| 130.1 | — |
| 129.8 | — |
| 130 | — |
| 129.9 | — |
| 129.8 | — |
| 129.5 | — |
| 130 | — |
| 129.3 | — |
| 129.3 | — |
| 129.4 | — |
| 129.1 | — |
| 129.6 | — |
| 129.6 | — |
| 130 | — |
| 129.8 | — |
| 129.8 | — |
| 131 | — |
| 129.8 | — |
| 129.9 | — |
| 129.5 | — |
| 130 | — |
| 130.4 | — |
| 130.2 | — |
| 130.2 | — |
| 129.4 | — |
| 129.7 | — |
| 130 | — |
| 130.3 | — |
| 130.4 | — |
| 130.2 | — |
| 130.3 | — |
| 130.2 | — |
| 129.6 | — |
| 130.2 | — |
| 130.1 | — |
| 130 | — |
| 130.3 | — |
| 129.8 | — |
| 130.5 | — |
| 130.1 | — |
| 130.6 | — |
| 130.3 | — |
| 130.4 | — |
| 130.6 | — |
| 130.6 | — |
| 130.7 | — |
| 130.7 | — |
| 131.5 | — |
| 130.5 | — |
| 130.6 | — |
| 131.9 | — |
| 131.1 | — |
| 131.1 | — |
| 131.2 | — |
| 130.3 | — |
| 131.6 | — |
| 131.7 | — |
| 131.7 | — |
| 131.1 | — |
| 131.4 | — |
| 131.5 | — |
| 131.5 | — |
| 131.3 | — |
| 131.8 | — |
| 131.6 | — |
| 132.1 | — |
| 131.5 | — |
| 131.6 | — |
| 131.6 | — |
| 132.1 | — |
| 132 | — |
| 131.9 | — |
| 132 | — |
| 131.6 | — |
| 132.4 | — |
| 132.2 | — |
| 131.9 | — |
| 131.8 | — |
| 132.3 | — |
| 132.7 | — |
| 132.4 | — |
| 132.3 | — |
| 132.5 | — |
| 132.9 | — |
| 131.8 | — |
| 131.9 | — |
| 132.5 | — |
| 132.4 | — |
| 133.1 | — |
| 132.8 | — |
| 133 | — |
| 133.3 | — |
| 133.3 | — |
| 133.4 | — |
| 134.1 | — |
| 133.3 | — |
| 133.3 | — |
| 133.1 | — |
| 133.4 | — |
| 133.6 | — |
| 133.5 | — |
| 133.9 | — |
| 133.9 | — |
| 134 | — |
| 133 | — |
| 133.5 | — |
| 134.1 | — |
| 134 | — |
| 133.7 | — |
| 134 | — |
| 133.6 | — |
| 133.8 | — |
| 133.4 | — |
| 133.4 | — |
| 134 | — |
| 134.5 | — |
| 133.8 | — |
| 133.7 | — |
| 133.6 | — |
| 134.2 | — |
| 133.7 | — |
| 134 | — |
| 134.6 | — |
| 134.4 | — |
| 134.8 | — |
| 134.3 | — |
| 134.6 | — |
| 134.3 | — |
| 134.1 | — |
| 134.3 | — |
| 134.2 | — |
| 134.9 | — |
| 135.1 | — |
| 135.1 | — |
| 134.8 | — |
| 134.6 | — |
| 135 | — |
| 135.9 | — |
| 136.3 | — |
| 135.3 | — |
| 135 | — |
| 136 | — |
| 135.8 | — |
| 135.9 | — |
| 136.2 | — |
| 135.5 | — |
| 136.5 | — |
| 136.4 | — |
| 136 | — |
| 135.9 | — |
| 135.8 | — |
| 136.8 | — |
| 136.7 | — |
| 136.8 | — |
| 136.8 | — |
| 136.7 | — |
| 137 | — |
| 137.1 | — |
| 137.6 | — |
| 137.9 | — |
| 137.4 | — |
| 137.8 | — |
| 136.8 | — |
| 137.8 | — |
| 137.8 | — |
| 137.6 | — |
| 138.3 | — |
| 138.9 | — |
| 138.1 | — |
| 138.2 | — |
| 137.5 | — |
| 137.9 | — |
| 138.2 | — |
| 138.6 | — |
| 138.5 | — |
| 137.8 | — |
| 137.6 | — |
| 138.3 | — |
| 138.5 | — |
| 138.8 | — |
| 138.2 | — |
| 138.5 | — |
| 138.4 | — |
| 139.3 | — |
| 139.1 | — |
| 138.2 | — |
| 138.8 | — |
| 139.6 | — |
| 139.8 | — |
| 140.4 | — |
| 140.4 | — |
| 140.7 | — |
| 140.2 | — |
| 140.1 | — |
| 140 | — |
| 140.5 | — |
| 140.1 | — |
| 140.5 | — |
| 140.1 | — |
| 140.1 | — |
| 140.1 | — |
| 141.1 | — |
| 140.1 | — |
| 140.8 | — |
| 141.2 | — |
| 141.5 | — |
| 141.7 | — |
| 140.7 | — |
| 141 | — |
| 141.9 | — |
| 141.7 | — |
| 142.3 | — |
| 141.8 | — |
| 140.9 | — |
| 141.2 | — |
| 140.8 | — |
| 142.1 | — |
| 142.1 | — |
| 141.1 | — |
| 142.1 | — |
| 141.9 | — |
| 142.3 | — |
| 142.3 | — |
| 142.3 | — |
| 142.5 | — |
| 142.5 | — |
| 142.5 | — |
| 142 | — |
| 142.7 | — |
| 143.2 | — |
| 142.6 | — |
| 144.2 | — |
| 143.9 | — |
| 143 | — |
| 143.9 | — |
| 143.6 | — |
| 144.1 | — |
| 143.7 | — |
| 144.1 | — |
| 144.2 | — |
| 144.3 | — |
| 143.9 | — |
| 144.8 | — |
| 145.4 | — |
| 145.4 | — |
| 145.4 | — |
| 145.4 | — |
| 145.3 | — |
| 145.7 | — |
| 145.2 | — |
| 145.4 | — |
| 144.6 | — |
| 145.2 | — |
| 145.9 | — |
| 145.7 | — |
| 145.1 | — |
| 146.3 | — |
| 146.2 | — |
| 146.6 | — |
| 147.3 | — |
| 146.8 | — |
| 147.4 | — |
| 146.6 | — |
| 147.8 | — |
| 146.9 | — |
| 147.4 | — |
| 147.9 | — |
| 147.2 | — |
| 148.3 | — |
| 148.3 | — |
| 147.5 | — |
| 147.4 | — |
| 148.7 | — |
| 149 | — |
| 147.5 | — |
| 147.6 | — |
| 147.8 | — |
| 147.9 | — |
| 147.8 | — |
| 149.1 | — |
| 148.4 | — |
| 148 | — |
| 148.4 | — |
| 148.9 | — |
| 149.1 | — |
| 149.1 | — |
| 149.4 | — |
| 148.9 | — |
| 150 | — |
| 149.4 | — |
| 149.7 | — |
| 149.3 | — |
| 150.5 | — |
| 149.4 | — |
| 150.1 | — |
| 150.4 | — |
| 151.4 | — |
| 151.3 | — |
| 150.3 | — |
| 150.6 | — |
| 151.3 | — |
| 151.6 | — |
| 151.8 | — |
| 152.2 | — |
| 152.1 | — |
| 151.5 | — |
| 152 | — |
| 152.3 | — |
| 152.5 | — |
| 152.5 | — |
| 153 | — |
| 152.9 | — |
| 153.3 | — |
| 152.9 | — |
| 153.4 | — |
| 152.8 | — |
| 152 | — |
| 152.9 | — |
| 153 | — |
| 153.6 | — |
| 153.9 | — |
| 153.1 | — |
| 153.7 | — |
| 154.2 | — |
| 153.7 | — |
| 154.5 | — |
| 154.5 | — |
| 154.5 | — |
| 154 | — |
| 154.2 | — |
| 155.2 | — |
| 154.1 | — |
| 155.2 | — |
| 156 | — |
| 155.6 | — |
| 156.7 | — |
| 156.5 | — |
| 156.5 | — |
| 156.7 | — |
| 156.3 | — |
| 156.4 | — |
| 157.1 | — |
| 156.6 | — |
| 156.9 | — |
| 156.8 | — |
| 158.6 | — |
| 158.3 | — |
| 158.1 | — |
| 158.2 | — |
| 158.4 | — |
| 158.3 | — |
| 158.9 | — |
| 159.9 | — |
| 159.1 | — |
| 159 | — |
| 160.3 | — |
| 159.3 | — |
| 159.7 | — |
| 160.8 | — |
| 161.1 | — |
| 160.7 | — |
| 159.3 | — |
| 160.2 | — |
| 160.3 | — |
| 160.3 | — |
| 160.4 | — |
| 161.3 | — |
| 160.6 | — |
| 160.9 | — |
| 161.6 | — |
| 161.8 | — |
| 161.5 | — |
| 161 | — |
| 160.6 | — |
| 160.7 | — |
| 161.6 | — |
| 161.7 | — |
| 162.8 | — |
| 162.5 | — |
| 162.4 | — |
| 162.7 | — |
| 161.4 | — |
| 160 | — |
| 160.4 | — |
| 161.6 | — |
| 162.1 | — |
| 160.5 | — |
| 161.2 | — |
| 160.3 | — |
| 162 | — |
| 160.8 | — |
| 161.2 | — |
| 160.7 | — |
| 161.2 | — |
| 160.4 | — |
| 161.3 | — |
| 161.1 | — |
| 160.1 | — |
| 161.1 | — |
| 161.8 | — |
| 161.3 | — |
| 161.2 | — |
| 160.2 | — |
| 161.4 | — |
| 161.6 | — |
| 162.3 | — |
| 161.9 | — |
| 163 | — |
| 161.4 | — |
| 163.5 | — |
| 162.6 | — |
| 161.6 | — |
| 162 | — |
| 161 | — |
| 162.9 | — |
| 161.6 | — |
| 162.1 | — |
| 163.1 | — |
| 161.4 | — |
| 161.7 | — |
| 161.8 | — |
| 161.8 | — |
| 160.3 | — |
| 162.5 | — |
| 161.4 | — |
| 161.7 | — |
| 161.6 | — |
| 161.4 | — |
| 161.7 | — |
| 161.5 | — |
| 162.1 | — |
| 161.4 | — |
| 160.9 | — |
| 161.4 | — |
| 162.2 | — |
| 161.3 | — |
| 162.2 | — |
| 161.5 | — |
| 162 | — |
| 161.7 | — |
| 162.7 | — |
| 162.1 | — |
| 162.3 | — |
| 160.7 | — |
| 161.4 | — |
| 162.7 | — |
| 162.3 | — |
| 161.9 | — |
| 161.3 | — |
| 163.3 | — |
| 162.3 | — |
| 160.8 | — |
| 160.9 | — |
| 161.1 | — |
| 162.6 | — |
| 161.4 | — |
| 160.5 | — |
| 161.1 | — |
| 162.6 | — |
| 161.7 | — |
| 161.4 | — |
| 161.9 | — |
| 163.1 | — |
| 163.4 | — |
| 163 | — |
| 162.9 | — |
| 164.2 | — |
| 163 | — |
| 162.4 | — |
| 162 | — |
| 161.3 | — |
| 160.9 | — |
| 162.8 | — |
| 162.3 | — |
| 163 | — |
| 162.1 | — |
| 162 | — |
| 162.1 | — |
| 161.9 | — |
| 161 | — |
| 161.7 | — |
| 161.4 | — |
| 162 | — |
| 161.5 | — |
| 162 | — |
| 161.2 | — |
| 161.7 | — |
| 161.3 | — |
| 161.7 | — |
| 161.8 | — |
| 162.2 | — |
| 161.7 | — |
| 161.7 | — |
| 162 | — |
| 162.3 | — |
| 162.3 | — |
| 161.2 | — |
| 161.4 | — |
| 162.2 | — |
| 162.3 | — |
| 161.7 | — |
| 161.7 | — |
| 162.4 | — |
| 161.9 | — |
| 161.9 | — |
| 161.5 | — |
| 162 | — |
| 162.6 | — |
| 163.7 | — |
| 161.9 | — |
| 161.9 | — |
| 162.8 | — |
| 163 | — |
| 162.5 | — |
| 161.8 | — |
| 161.1 | — |
| 162 | — |
| 161.8 | — |
| 162 | — |
| 161.6 | — |
| 162.6 | — |
| 162 | — |
| 161.5 | — |
| 161.5 | — |
| 161.9 | — |
| 162.2 | — |
| 163.4 | — |
| 161.2 | — |
| 161.2 | — |
| 162.3 | — |
| 162.5 | — |
| 162.8 | — |
| 162.8 | — |
| 161.4 | — |
| 163.4 | — |
| 163.1 | — |
| 162.2 | — |
| 162 | — |
| 162.5 | — |
| 161.2 | — |
| 162.1 | — |
| 160.5 | — |
| 161.3 | — |
| 162 | — |
| 162.4 | — |
| 162.2 | — |
| 161.8 | — |
| 163.5 | — |
| 163.1 | — |
| 161.8 | — |
| 162.6 | — |
| 162.9 | — |
| 162.4 | — |
| 162 | — |
| 161.9 | — |
| 161.5 | — |
| 161.9 | — |
| 161.7 | — |
| 162.4 | — |
| 163.8 | — |
| 161.7 | — |
| 163.6 | — |
| 162.4 | — |
| 162.8 | — |
| 163.5 | — |
| 162.2 | — |
| 161.4 | 0 |
| 161.3 | 8.062 |
| 160.6 | 12.66 |
| 159.6 | 15.48 |
| 159.7 | 17.13 |
| 160 | 18.93 |
| 159.4 | 21.73 |
| 159.1 | 23.81 |
| 159.5 | 25.5 |
| 159.8 | 27.24 |
| 159.6 | 29.07 |
| 159.1 | 29.69 |
| 158.3 | 31.59 |
| 159 | 33.53 |
| 159 | 34.48 |
| 159.1 | 35.3 |
| 158.4 | 36.36 |
| 158.6 | 38.83 |
| 158.2 | 40.77 |
| 157.9 | 43.42 |
| 158.3 | 44.59 |
| 157.7 | 44.63 |
| 158 | 44.51 |
| 157 | 46.67 |
| 157.1 | 49.16 |
| 157.7 | 50.51 |
| 157 | 51.82 |
| 157.3 | 53.37 |
| 157.6 | 54.07 |
| 156.9 | 54.81 |
| 157.1 | 55.32 |
| 158.3 | 57.19 |
| 157.3 | 58.36 |
| 157 | 57.69 |
| 157.4 | 58.85 |
| 157 | 59.78 |
| 156.9 | 61.09 |
| 157.2 | 63.37 |
| 157.4 | 63.72 |
| 157.6 | 62.77 |
| 156.8 | 64.6 |
| 156 | 66.35 |
| 157.4 | 67.74 |
| 157.7 | 67.99 |
| 157.2 | 69.25 |
| 156.4 | 70.56 |
| 156.8 | 72.71 |
| 156.9 | 74.69 |
| 157.3 | 74.33 |
| 156.9 | 74.76 |
| 156.5 | 75.9 |
| 156.7 | 77.92 |
| 156.5 | 79.04 |
| 155.9 | 80.48 |
| 156.3 | 80.66 |
| 156.6 | 79.55 |
| 156.5 | 79.1 |
| 156.1 | 81.25 |
| 156.5 | 82.19 |
| 156.2 | 82.21 |
| 156.5 | 81.86 |
| 156.3 | 82.08 |
| 156.3 | 82.93 |
| 156.5 | 84.43 |
| 156.4 | 84.89 |
| 155.6 | 88.37 |
| 155.8 | 89.32 |
| 156 | 88.9 |
| 155.2 | 89.99 |
| 155.9 | 91.21 |
| 155.8 | 92.15 |
| 155.9 | 94.06 |
| 155.7 | 95.96 |
| 156.2 | 96.06 |
| 156.5 | 96.39 |
| 156.4 | 96.33 |
| 156.5 | 97.02 |
| 156.3 | 99.29 |
| 155.4 | 100.7 |
| 155.5 | 102.4 |
| 155.3 | 101.9 |
| 154.2 | 101 |
| 156 | 101.9 |
| 155.6 | 101.9 |
| 156.5 | 102.9 |
| 155.7 | 103.4 |
| 156.2 | 104.5 |
| 155.3 | 105.5 |
| 154.4 | 106.8 |
| 155.1 | 108.6 |
| 155.4 | 107.3 |
| 156 | 108.2 |
| 155.8 | 105.5 |
| 155.4 | 106.6 |
| 155.8 | 109 |
| 156 | 109.2 |
| 156.2 | 111.1 |
| 155.2 | 111.6 |
| 155.8 | 111.2 |
| 155.5 | 113.3 |
| 155.8 | 115.4 |
| 155.2 | 115.8 |
| 155.3 | 115.2 |
| 155.5 | 117.6 |
| 155.1 | 119.2 |
| 155.4 | 120.6 |
| 155.9 | 121.6 |
| 156.4 | 121.2 |
| 155.7 | 122.1 |
| 155.5 | 124.5 |
| 154.7 | 126.6 |
| 155.1 | 126.1 |
| 155.2 | 126.3 |
| 155.6 | 127.2 |
| 155.8 | 129.5 |
| 156 | 128 |
| 155.7 | 128 |
| 156.1 | 128.8 |
| 155.8 | 129.1 |
| 155.8 | 131 |
| 155.4 | 133.6 |
| 156.6 | 131.8 |
| 155.7 | 133.3 |
| 155.8 | 134.9 |
| 155.1 | 135.2 |
| 155.2 | 139.3 |
| 155.1 | 139.4 |
| 154 | 139.3 |
| 155.2 | 138 |
| 155.4 | 137.3 |
| 155.6 | 138.5 |
| 154.7 | 139.1 |
| 154.2 | 140.5 |
| 154.7 | 142.9 |
| 154.7 | 144.7 |
| 155.5 | 143 |
| 155 | 141.9 |
| 155.3 | 142.4 |
| 154.9 | 142 |
| 154.8 | 142.4 |
| 154.7 | 142.8 |
| 154.8 | 144.7 |
| 154.6 | 144.3 |
| 153.9 | 146.1 |
| 153.7 | 145.5 |
| 154 | 147.4 |
| 154.6 | 147.5 |
| 153.7 | 149.4 |
| 154.4 | 151.7 |
| 154.4 | 153.3 |
| 154 | 152 |
| 153.7 | 154.2 |
| 153.8 | 155.1 |
| 154.5 | 154.6 |
| 154 | 158 |
| 154.2 | 157.8 |
| 153.5 | 158.6 |
| 153.8 | 158.1 |
| 153 | 157.6 |
| 153.8 | 157.6 |
| 154.3 | 159.9 |
| 153.3 | 159 |
| 153.8 | 163.8 |
| 153.6 | 162 |
| 154.8 | 162 |
| 154 | 162.6 |
| 153.7 | 164.2 |
| 153.8 | 164.5 |
| 153.9 | 164.3 |
| 153.2 | 166.6 |
| 154.2 | 168.9 |
| 153.1 | 169.6 |
| 152.9 | 172.7 |
| 153.4 | 175.5 |
| 152.8 | 178.1 |
| 152.8 | 177.7 |
| 153 | 178 |
| 154.4 | 176.4 |
| 153.7 | 175.5 |
| 153.8 | 176.1 |
| 153 | 179.9 |
| 153.7 | 183.1 |
| 152.9 | 186.7 |
| 152.6 | 184.4 |
| 152.6 | 183.7 |
| 152.9 | 181.3 |
| 153.5 | 180.9 |
| 152.7 | 184 |
| 152.4 | 184.5 |
| 152 | 186.5 |
| 153.2 | 186.7 |
| 154 | 185.7 |
| 152.4 | 184.5 |
| 153.3 | 185.1 |
| 153.3 | 184.4 |
| 152.3 | 183.2 |
| 152.7 | 186.7 |
| 152.4 | 189.5 |
| 152.4 | 188.8 |
| 151.8 | 189.1 |
| 152.6 | 189.9 |
| 152.1 | 188.5 |
| 152 | 192.5 |
| 151.9 | 195.1 |
| 152.2 | 196.8 |
| 152 | 195.3 |
| 152.8 | 194.5 |
| 152.8 | 196.3 |
| 151.4 | 197.2 |
| 152 | 198.6 |
| 152.1 | 201 |
| 151.2 | 203.1 |
| 152.2 | 205.7 |
| 152.4 | 204.7 |
| 151.9 | 203.8 |
| 149.7 | 203.7 |
| 151.5 | 202.8 |
| 151.3 | 202 |
| 151.3 | 200.1 |
| 151.7 | 204 |
| 150.8 | 205.3 |
| 151.3 | 209.1 |
| 151.5 | 209.3 |
| 150.8 | 208.4 |
| 151 | 208.2 |
| 150.3 | 207.7 |
| 151.3 | 207.1 |
| 151.8 | 210.4 |
| 150.1 | 210.1 |
| 150.7 | 214.9 |
| 151 | 215.9 |
| 151.3 | 213.6 |
| 152.6 | 212.9 |
| 151.9 | 212.2 |
| 151.6 | 210 |
| 152.5 | 212 |
| 151 | 211.8 |
| 152.5 | 212.7 |
| 152.7 | 210.6 |
| 152.3 | 211.4 |
| 151 | 213.6 |
| 150.5 | 215.2 |
| 152 | 216.4 |
| 152.6 | 215.9 |
| 151.7 | 217 |
| 151.5 | 214.3 |
| 150.9 | 212.6 |
| 150.7 | 214.7 |
| 151.2 | 215.5 |
| 150.6 | 218.4 |
| 150.8 | 221.1 |
| 151.8 | 222.1 |
| 151.7 | 221.2 |
| 151 | 220.6 |
| 152.1 | 222.2 |
| 151.6 | 222.7 |
| 152.4 | 225.5 |
| 151.1 | 225.4 |
| 151.1 | 224.1 |
| 152 | 225.7 |
| 151.6 | 227.5 |
| 151.1 | 228.3 |
| 151.2 | 227.6 |
| 152.2 | 228.5 |
| 151.6 | 228.9 |
| 152.2 | 229.3 |
| 150.1 | 231 |
| 149.8 | 236.2 |
| 150 | 238.1 |
| 150.7 | 237.3 |
| 151 | 239.9 |
| 150.5 | 241.6 |
| 150.1 | 239.5 |
| 149.6 | 241.1 |
| 149.7 | 241.9 |
| 149.3 | 248.5 |
| 149.1 | 253 |
| 148.8 | 253.3 |
| 150.5 | 256.4 |
| 149.8 | 261.4 |
| 149.6 | 263 |
| 149.5 | 261 |
| 148.3 | 263.3 |
| 149.4 | 265.6 |
| 148.8 | 268.4 |
| 148.1 | 270.4 |
| 147.6 | 270.9 |
| 148.6 | 273.4 |
| 147.5 | 275.9 |
| 147.4 | 274.6 |
| 146.9 | 273.9 |
| 148.6 | 278.4 |
| 147.4 | 280.7 |
| 146.6 | 279.4 |
| 147.4 | 281.4 |
| 146.3 | 282 |
| 146.8 | 282.9 |
| 146.1 | 283.9 |
| 146.5 | 280.9 |
| 146.5 | 284.7 |
| 147.3 | 285.4 |
| 147.5 | 284.1 |
| 147.2 | 287 |
| 147.8 | 285.8 |
| 148.2 | 288.2 |
| 146.7 | 291.2 |
| 147.3 | 291.9 |
| 147.7 | 291.1 |
| 147 | 292.6 |
| 147.9 | 293.3 |
| 146.9 | 296.3 |
| 146.9 | 295.8 |
| 147.6 | 293.8 |
| 147.5 | 294.9 |
| 147.7 | 295.9 |
| 148.1 | 298.9 |
| 147.7 | 296.8 |
| 148.2 | 298.8 |
| 146.4 | 304.9 |
| 147.5 | 310.4 |
| 147.7 | 309.6 |
| 147.6 | 306.9 |
| 147.6 | 305.8 |
| 147.5 | 308.4 |
| 147.2 | 311.8 |
| 148.1 | 310.6 |
| 147.3 | 311 |
| 147.4 | 311.8 |
| 147.6 | 309.3 |
| 147.2 | 311.7 |
| 147.2 | 314.1 |
| 146.6 | 317.6 |
| 146.4 | 319.2 |
| 146.7 | 321.3 |
| 146.6 | 320.5 |
| 147 | 316.8 |
| 146.9 | 318 |
| 147.1 | 318.5 |
| 146.5 | 319.6 |
| 146.9 | 324.2 |
| 147.5 | 323.1 |
| 147 | 324.1 |
| 146.2 | 323.7 |
| 146.9 | 325 |
| 146.1 | 325.5 |
| 146.5 | 323.6 |
| 146.1 | 324.3 |
| 145.9 | 326.2 |
| 145.9 | 327.9 |
| 146.2 | 326 |
| 145.8 | 326.5 |
| 146.8 | 328.3 |
| 145.9 | 327.3 |
| 146.1 | 329.6 |
| 146.5 | 328.8 |
| 146.3 | 329.1 |
| 145.8 | 330.5 |
| 145.7 | 331.1 |
| 146.1 | 329.1 |
| 145.5 | 328.3 |
| 143.8 | 327.9 |
| 145.3 | 328.3 |
| 145.2 | 331.2 |
| 145.2 | 333.5 |
| 145.1 | 330.8 |
| 144.8 | 329.8 |
| 145.2 | 334.8 |
| 145.7 | 333.6 |
| 145.5 | 332.6 |
| 144.1 | 333.2 |
| 143.9 | 337.1 |
| 143 | 338.4 |
| 144.5 | 338.6 |
| 143.8 | 338.2 |
| 143.3 | 338.7 |
| 144.9 | 338.8 |
| 143.6 | 339.9 |
| 144 | 345.1 |
| 141.9 | 346.3 |
| 142.8 | 345.3 |
| 142.4 | 341.5 |
| 143.2 | 342.5 |
| 143.6 | 345.2 |
| 144 | 348.1 |
| 141.6 | 347.3 |
| 141.4 | 346.9 |
| 141.9 | 346.5 |
| 142.1 | 344.3 |
| 143.8 | 345.7 |
| 143.4 | 346.4 |
| 143 | 344.3 |
| 144 | 342.8 |
| 143.9 | 341.1 |
| 143.5 | 341.6 |
| 144.5 | 345.2 |
| 144.3 | 343.4 |
| 144.1 | 343 |
| 143.9 | 345.3 |
| 143.8 | 348.4 |
| 143.3 | 349.6 |
| 142 | 346.8 |
| 140.9 | 354 |
| 142.7 | 354.9 |
| 143.6 | 358.5 |
| 141.9 | 367.2 |
| 140.6 | 369.4 |
| 140.1 | 370.4 |
| 140.8 | 370 |
| 141.1 | 371.2 |
| 138.9 | 373.9 |
| 139.3 | 376.6 |
| 140.2 | 387.7 |
| 140 | 391 |
| 139.7 | 387 |
| 140.2 | 389.4 |
| 138.2 | 398.2 |
| 139.2 | 400.5 |
| 140.1 | 397.5 |
| 139.9 | 406.7 |
| 141.5 | 404.9 |
| 140.3 | 409.5 |
| 140 | 409.4 |
| 138.9 | 413.2 |
| 138.7 | 424.7 |
| 139.8 | 420.2 |
| 139.1 | 423.8 |
| 139 | 436.5 |
| 139.4 | 433.2 |
| 139.7 | 435.1 |
| 139.1 | 440.6 |
| 139.3 | 443.4 |
| 139.4 | 436.5 |
| 139.2 | 443 |
| 139.6 | 447.5 |
| 139.8 | 444.7 |
| 139.2 | 441.4 |
| 139.2 | 446.8 |
| 138.7 | 446 |
| 140.1 | 446.1 |
| 138.2 | 443.7 |
| 138 | 452.3 |
| 139.7 | 446.1 |
| 138.7 | 454 |
| 138.2 | 455.2 |
| 138.9 | 454.9 |
| 138.3 | 467.5 |
| 138 | 471.2 |
| 137.4 | 477.9 |
| 139 | 470.3 |
| 139 | 470.3 |
| 139.1 | 476.1 |
| 139.5 | 482.4 |
| 139.4 | 485.6 |
| 140 | 488.7 |
| 138 | 498.1 |
| 138.4 | 505.3 |
| 137.9 | 504.5 |
| 139.7 | 508.2 |
| 137.4 | 512 |
| 138.1 | 514.1 |
| 137.2 | 520.9 |
| 139.1 | 524.8 |
| 138.4 | 526.7 |
| 138.1 | 527.7 |
| 139.3 | 527.8 |
| 139.3 | 521.8 |
| 139.1 | 528 |
| 138.8 | 527.7 |
| 138.4 | 529.3 |
| 137.3 | 531.9 |
| 138 | 537.2 |
| 137.5 | 536.4 |
| 137.1 | 533 |
| 138 | 539.5 |
| 138.6 | 543.4 |
| 139.1 | 543.1 |
| 139 | 547.1 |
| 139 | 556.1 |
| 137.1 | 546.5 |
| 137.2 | 549.8 |
| 137.1 | 556.3 |
| 137.1 | 561 |
| 136.5 | 570 |
| 138.2 | 565.6 |
| 137.6 | 570.2 |
| 137 | 573 |
| 138.2 | 562.8 |
| 136.6 | 573.4 |
| 137.2 | 578.7 |
| 137.3 | 579.1 |
| 136.7 | 583.3 |
| 138.1 | 578.6 |
| 137.4 | 579.6 |
| 137.8 | 572.6 |
| 137.3 | 575.8 |
| 137.4 | 580.6 |
| 136.6 | 586.2 |
| 136.4 | 583.1 |
| 135.4 | 583.8 |
| 137 | 589.5 |
| 137 | 588.3 |
| 136.1 | 596 |
| 137.3 | 601.3 |
| 137.1 | 606.3 |
| 135.8 | 610 |
| 136.2 | 615.7 |
| 136.4 | 606.1 |
| 136.2 | 611.7 |
| 136.3 | 609.3 |
| 135.9 | 612.5 |
| 136.4 | 609.9 |
| 137.2 | 614.8 |
| 137.1 | 614.9 |
| 136.1 | 612.2 |
| 137.8 | 606.9 |
| 137.2 | 605.4 |
| 134.8 | 606.6 |
| 136.4 | 607.2 |
| 135.8 | 616.2 |
| 137.9 | 619.4 |
| 136.2 | 617.2 |
| 137.4 | 612.4 |
| 137.5 | 612.8 |
| 137.5 | 621.8 |
| 137.7 | 622.6 |
| 137.6 | 623.7 |
| 136.7 | 620.2 |
| 138.3 | 622.9 |
| 136.9 | 625.5 |
| 137.2 | 627.6 |
| 136.2 | 627.9 |
| 137 | 634.3 |
| 136.5 | 631.9 |
| 137.2 | 638.7 |
| 136.4 | 643.6 |
| 136.8 | 641.3 |
| 136.3 | 644.8 |
| 138.2 | 654.1 |
| 136.8 | 651.8 |
| 137.3 | 657.9 |
| 136.9 | 654.4 |
| 136.4 | 648.5 |
| 136.5 | 654.1 |
| 136.7 | 650.8 |
| 137.3 | 654.8 |
| 137 | 658.4 |
| 137 | 649.2 |
| 137.1 | 644.4 |
| 136.9 | 640.7 |
| 134.9 | 643.2 |
| 134.6 | 641.3 |
| 136.2 | 636.8 |
| 135.1 | 637.2 |
| 135.5 | 633.5 |
| 136.2 | 629.8 |
| 137.7 | 626.4 |
| 135.5 | 627.9 |
| 135.8 | 640.6 |
| 137.8 | 636.9 |
| 136.6 | 650.8 |
| 137.9 | 649.5 |
| 139 | 657.7 |
| 138.4 | 657 |
| 137.7 | 665.9 |
| 137.9 | 660.2 |
| 136.1 | 660.6 |
| 136.3 | 662.6 |
| 135.8 | 660.9 |
| 136.4 | 656.1 |
| 136.1 | 662.3 |
| 137.6 | 661.9 |
| 134.9 | 658.7 |
| 135.2 | 659.7 |
| 136.8 | 670.5 |
| 136.1 | 673.9 |
| 136.2 | 664.1 |
| 136.2 | 666.2 |
| 136.7 | 668.7 |
| 135.1 | 662.3 |
| 136.1 | 660.8 |
| 135.7 | 660.7 |
| 137.4 | 667.1 |
| 134.8 | 669.8 |
| 135.3 | 672.4 |
| 136.5 | 671.3 |
| 135.3 | 668.9 |
| 135.7 | 670.6 |
| 135.8 | 666.9 |
| 135 | 680.2 |
| 136.9 | 680.1 |
| 134.4 | 682.3 |
| 135.2 | 678.7 |
| 135.7 | 677.9 |
| 135.9 | 683.2 |
| 135.3 | 690.9 |
| 135.9 | 687.7 |
| 135.3 | 687.2 |
| 134.5 | 692.1 |
| 135.5 | 690.7 |
| 135.7 | 695.9 |
| 135.2 | 700.8 |
| 135.5 | 702.8 |
| 136.2 | 693.7 |
| 137 | 692.6 |
| 136 | 691 |
| 136.4 | 691.5 |
| 136.2 | 700.3 |
| 136 | 697.8 |
| 136.7 | 698.3 |
| 138.3 | 700.9 |
| 135.8 | 699.1 |
| 135.8 | 700.6 |
| 136.4 | 706 |
| 137.5 | 698.3 |
| 137.6 | 704 |
| 136.6 | 699.2 |
| 136 | 702.9 |
| 137.1 | 710.2 |
| 137.6 | 703.7 |
| 136.4 | 710 |
| 137.2 | 710.8 |
| 137.8 | 719.7 |
| 136.6 | 724.9 |
| 136.3 | 736.1 |
| 135.9 | 736.1 |
| 136.3 | 735.6 |
| 136.9 | 735.7 |
| 135.6 | 741.9 |
| 135.5 | 754.4 |
| 136.5 | 744.1 |
| 137.2 | 743.5 |
| 135.3 | 744.1 |
| 135.5 | 743.6 |
| 135.8 | 737.8 |
| 137.1 | 732.2 |
| 136.5 | 730.6 |
| 136.4 | 731.9 |
| 136.4 | 732.7 |
| 136.4 | 734.6 |
| 135.7 | 722.8 |
| 135.3 | 722.9 |
| 135.6 | 728.3 |
| 137.4 | 726.9 |
| 138.6 | 725.2 |
| 135 | 717.4 |
| 135.3 | 720 |
| 137.1 | 728.7 |
| 134.8 | 722.6 |
| 134.6 | 725.1 |
| 135.9 | 733.5 |
| 137.4 | 732.4 |
| 135.3 | 745.5 |
| 136.2 | 749.3 |
| 136 | 752.1 |
| 137.2 | 751.6 |
| 134.9 | 742.1 |
| 137 | 742.5 |
| 135.2 | 746.7 |
| 134.8 | 739.2 |
| 136.3 | 734.1 |
| 136.9 | 737 |
| 137.7 | 736.9 |
| 137.1 | 736.3 |
| 136.4 | 751.4 |
| 135.9 | 754.2 |
| 136.2 | 758.1 |
| 137.6 | 756 |
| 136.6 | 758 |
| 139.8 | 761.5 |
| 136.1 | 769.6 |
| 135.3 | 768.2 |
| 138.2 | 765.4 |
| 135.1 | 776.4 |
| 135.2 | 771.6 |
| 134.4 | 786.5 |
| 135.1 | 794.8 |
| 136.2 | 790.8 |
| 136.4 | 786.6 |
| 136.9 | 782.8 |
| 136 | 795.8 |
| 137.1 | 790.9 |
| 136.6 | 794.3 |
| 136.8 | 800.7 |
| 135.9 | 794.9 |
| 136 | 797.6 |
| 136.9 | 803.7 |
| 138.3 | 799.8 |
| 137.7 | 802 |
| 136.3 | 801 |
| 136.5 | 803.7 |
| 135.1 | 805.5 |
| 137 | 808.4 |
| 137.1 | 813.3 |
| 137 | 817.7 |
| 136.7 | 827.3 |
| 136.2 | 830 |
| 136.1 | 821.6 |
| 136.1 | 826.7 |
| 137.1 | 821.7 |
| 135.7 | 818.1 |
| 137.5 | 831.4 |
| 137 | 836.7 |
| 136.9 | 836.3 |
| 137 | 838.8 |
| 137.4 | 852.2 |
| 136.2 | 836.6 |
| 137.2 | 829.2 |
| 136.2 | 829.8 |
| 135.2 | 823.8 |
| 136.1 | 818.4 |
| 135.7 | 830.4 |
| 135.7 | 836.6 |
| 135.5 | 830.3 |
| 135.2 | 833.6 |
| 134.7 | 824.2 |
| 135.9 | 823.4 |
| 137.1 | 831.5 |
| 135.6 | 830.6 |
| 136.4 | 834.1 |
| 136.1 | 844.8 |
| 135.1 | 831.8 |
| 136.8 | 832.3 |
| 136.3 | 845.4 |
| 137.2 | 840.7 |
| 136.6 | 841.3 |
| 137.8 | 841.1 |
| 136.7 | 834.1 |
| 136 | 840 |
| 137.2 | 831.9 |
| 135 | 828.7 |
| 136.7 | 832.7 |
| 136.9 | 836.9 |
| 136.8 | 832.3 |
| 137.9 | 834.4 |
| 138.2 | 843.8 |
| 136.8 | 831.8 |
| 136.5 | 832.7 |
| 137.1 | 837 |
| 137.3 | 842.5 |
| 136.9 | 848.7 |
| 137.7 | 848.2 |
| 136.2 | 855.6 |
| 137.7 | 856.3 |
| 136.9 | 865.1 |
| 136.4 | 869.4 |
| 136.8 | 869.3 |
| 136.7 | 867 |
| 136.6 | 868 |
| 136.7 | 872.6 |
| 137 | 872.7 |
| 135.7 | 866 |
| 135.9 | 877.9 |
| 137.2 | 884.6 |
| 136.4 | 880.4 |
| 135.5 | 878.4 |
| 137.4 | 880.8 |
| 136.9 | 885.7 |
| 136.1 | 885.4 |
| 136.4 | 894.8 |
| 136.2 | 896.4 |
| 135.9 | 909.4 |
| 135.9 | 907.8 |
| 136.1 | 916 |
| 135 | 904.7 |
| 136.4 | 904.7 |
| 136.5 | 914.2 |
| 137.6 | 914.6 |
| 137.1 | 905.8 |
| 137.7 | 902.7 |
| 136.9 | 900.3 |
| 137.1 | 909.8 |
| 136.9 | 910 |
| 135.4 | 904.8 |
| 135.6 | 899.8 |
| 136.4 | 900 |
| 136.5 | 905 |
| 136.3 | 899.1 |
| 137.7 | 905.6 |
| 137.2 | 915.5 |
| 136.7 | 912.3 |
| 136.2 | 920.6 |
| 137 | 905.1 |
| 135.5 | 904.6 |
| 136.2 | 891.9 |
| 136.6 | 894.3 |
| 137.2 | 891.4 |
| 136.3 | 899.2 |
| 136.8 | 901.5 |
| 136.2 | 902.4 |
| 136 | 910 |
| 136.5 | 907.3 |
| 135.8 | 907.6 |
| 136.3 | 906.1 |
| 138 | 917.6 |
| 134.7 | 921.4 |
| 136.4 | 924.7 |
| 137 | 920.7 |
| 135.2 | 929.5 |
| 135.4 | 936 |
| 136 | 939.1 |
| 137.2 | 941.3 |
| 136.9 | 928.3 |
| 136.9 | 924.3 |
| 137.2 | 919.3 |
| 137.2 | 934.1 |
| 136.9 | 949.9 |
| 137.9 | 950.4 |
| 137 | 956.9 |
| 137 | 949.7 |
| 136.8 | 955 |
| 137.7 | 954.2 |
| 136.7 | 969.7 |
| 135.8 | 969.9 |
| 138 | 966.5 |
| 136.6 | 962.2 |
| 137.8 | 959.5 |
| 136.1 | 971.1 |
| 135.7 | 974 |
| 137.8 | 979 |
| 136.4 | 976.4 |
| 135.9 | 973.8 |
| 136.8 | 977.3 |
| 136.7 | 977.1 |
| 136.8 | 978.5 |
| 137.5 | 975.7 |
| 137.3 | 975.1 |
| 138.1 | 971 |
| 137.4 | 977.3 |
| 136.6 | 974.9 |
| 138.4 | 980.6 |
| 136.5 | 979.2 |
| 136.7 | 978 |
| 138.2 | 980.1 |
| 136.2 | 983.5 |
| 135.7 | 990.2 |
| 136.1 | 987.3 |
| 136.2 | 985.1 |
| 136 | 987.7 |
| 135.8 | 989.6 |
| 136.1 | 996 |
| 135.7 | 994.6 |
| 136.9 | 987 |
| 135.7 | 985.6 |
| 135.6 | 987.7 |
| 136.7 | 985.8 |
| 135.7 | 975.5 |
| 137.9 | 980.1 |
| 136.8 | 993.9 |
| 136.1 | 1001 |
| 137 | 1004 |
| 136.4 | 1003 |
| 138 | 998.7 |
| 134.9 | 1021 |
| 136.6 | 1023 |
| 137.1 | 1027 |
| 138 | 1018 |
| 137 | 1017 |
| 137.9 | 1023 |
| 137.4 | 1027 |
| 137.8 | 1035 |
| 137.8 | 1011 |
| 136.9 | 1021 |
| 137.4 | 1028 |
| 137.7 | 1025 |
| 136.6 | 1028 |
| 135.8 | 1026 |
| 138 | 1023 |
| 136.2 | 1032 |
| 136.8 | 1025 |
| 137.8 | 1029 |
| 138.2 | 1039 |
| 137.7 | 1031 |
| 137 | 1036 |
| 136.5 | 1034 |
| 135.2 | 1053 |
| 136 | 1053 |
| 135.9 | 1051 |
| 134 | 1052 |
| 135.1 | 1054 |
| 137.3 | 1063 |
| 136.8 | 1073 |
| 136.8 | 1077 |
| 138 | 1069 |
| 137.5 | 1062 |
| 137.5 | 1065 |
| 137.1 | 1056 |
| 137.8 | 1057 |
| 137.4 | 1058 |
| 138.4 | 1055 |
| 137.5 | 1061 |
| 138.2 | 1060 |
| 136.3 | 1063 |
| 136.6 | 1059 |
| 136.5 | 1048 |
| 136.6 | 1048 |
| 136.5 | 1053 |
| 136.9 | 1055 |
| 134.3 | 1060 |
| 137.3 | 1061 |
| 134.8 | 1064 |
| 136.7 | 1068 |
| 136 | 1072 |
| 135.7 | 1071 |
| 137.8 | 1080 |
| 137.1 | 1076 |
| 137.2 | 1069 |
| 136.5 | 1059 |
| 135.8 | 1069 |
| 136.1 | 1073 |
| 138.3 | 1083 |
| 136.7 | 1083 |
| 137.4 | 1091 |
| 136.4 | 1096 |
| 136.4 | 1100 |
| 136.9 | 1098 |
| 136.3 | 1093 |
| 138.8 | 1095 |
| 137.1 | 1093 |
| 137 | 1092 |
| 135 | 1093 |
| 135.4 | 1093 |
| 136.4 | 1090 |
| 135.6 | 1093 |
| 136.9 | 1088 |
| 136.8 | 1098 |
| 136.9 | 1104 |
| 136.1 | 1103 |
| 137.3 | 1100 |
| 136.8 | 1104 |
| 135.8 | 1102 |
| 135.4 | 1092 |
| 135.8 | 1098 |
| 134.6 | 1086 |
| 136.2 | 1089 |
| 136.9 | 1086 |
| 135.7 | 1091 |
| 134.9 | 1088 |
| 137.5 | 1083 |
| 135 | 1087 |
| 136.7 | 1090 |
| 137 | 1092 |
| 135.3 | 1097 |
| 135.4 | 1105 |
| 136.6 | 1118 |
| 135 | 1130 |
| 136.5 | 1124 |
| 134.8 | 1129 |
| 136.3 | 1134 |
| 136.7 | 1127 |
| 136.5 | 1129 |
| 136.6 | 1132 |
| 137.6 | 1134 |
| 136.1 | 1133 |
| 137.3 | 1123 |
| 137 | 1130 |
| 137.1 | 1130 |
| 136.5 | 1130 |
| 136.1 | 1141 |
| 136.2 | 1142 |
| 135 | 1149 |
| 135.4 | 1145 |
| 135.2 | 1140 |
| 136.9 | 1151 |
| 136.3 | 1144 |
| 137 | 1149 |
| 137.1 | 1152 |
| 139 | 1140 |
| 136.8 | 1142 |
| 136.1 | 1144 |
| 135.5 | 1161 |
| 137.5 | 1147 |
| 138.4 | 1152 |
| 137.9 | 1154 |
| 137 | 1152 |
| 135.6 | 1139 |
| 134.6 | 1149 |
| 137.2 | 1159 |
| 136.8 | 1155 |
| 135.5 | 1164 |
| 137 | 1168 |
| 136.8 | 1157 |
| 135.7 | 1165 |
| 135.8 | 1169 |
| 136.1 | 1170 |
| 134.7 | 1173 |
| 136.4 | 1157 |
| 137.5 | 1160 |
| 135.8 | 1164 |
| 134.8 | 1155 |
| 136.8 | 1153 |
| 135.5 | 1156 |
| 134.8 | 1147 |
| 136.2 | 1155 |
| 136.3 | 1156 |
| 136.4 | 1159 |
| 138.3 | 1158 |
| 136.2 | 1176 |
| 136.4 | 1181 |
| 136.6 | 1192 |
| 134.7 | 1205 |
| 134.6 | 1200 |
| 135.1 | 1201 |
| 135.6 | 1195 |
| 136.6 | 1218 |
| 138.2 | 1224 |
| 135.6 | 1217 |
| 135 | 1214 |
| 138.2 | 1216 |
| 136 | 1225 |
| 136.3 | 1224 |
| 137.2 | 1237 |
| 136.6 | 1239 |
| 136.2 | 1248 |
| 137.2 | 1257 |
| 136.7 | 1261 |
| 137.2 | 1257 |
| 137.2 | 1262 |
| 137.1 | 1249 |
| 137.7 | 1236 |
| 134.5 | 1243 |
| 136.4 | 1245 |
| 137.1 | 1244 |
| 135.9 | 1238 |
| 137 | 1240 |
| 135.3 | 1236 |
| 135.3 | 1243 |
| 136.6 | 1252 |
| 138.7 | 1240 |
| 135.9 | 1240 |
| 136.1 | 1235 |
| 135.5 | 1233 |
| 138.1 | 1238 |
| 136.9 | 1245 |
| 135.9 | 1250 |
| 136.3 | 1259 |
| 136.3 | 1246 |
| 136.1 | 1232 |
| 136.5 | 1251 |
| 136.5 | 1248 |
| 135.9 | 1262 |
| 136 | 1259 |
| 136.7 | 1272 |
| 135.4 | 1269 |
| 136.3 | 1277 |
| 137.6 | 1272 |
| 137.1 | 1278 |
| 136.2 | 1269 |
| 135.7 | 1270 |
| 137.4 | 1277 |
| 138.5 | 1287 |
| 135.7 | 1284 |
| 136.2 | 1282 |
| 135.9 | 1297 |
| 136.8 | 1303 |
| 135.1 | 1298 |
| 135.2 | 1299 |
| 136.5 | 1304 |
| 137.3 | 1313 |
| 136.9 | 1298 |
| 136.3 | 1295 |
| 136.8 | 1312 |
| 136.9 | 1303 |
| 138.3 | 1323 |
| 137.1 | 1311 |
| 138.4 | 1320 |
| 137.7 | 1309 |
| 137.4 | 1314 |
| 137.9 | 1315 |
| 135.8 | 1299 |
| 138.6 | 1304 |
| 136.4 | 1297 |
| 137.3 | 1309 |
| 136.5 | 1304 |
| 137.4 | 1316 |
| 136.4 | 1315 |
| 137.4 | 1304 |
| 136.6 | 1307 |
| 136.2 | 1311 |
| 135.1 | 1316 |
| 136.1 | 1304 |
| 135 | 1325 |
| 135.4 | 1317 |
| 136.8 | 1324 |
| 135.8 | 1337 |
| 136.2 | 1342 |
| 136.2 | 1336 |
| 135.9 | 1326 |
| 135.8 | 1334 |
| 136.3 | 1338 |
| 137.1 | 1342 |
| 136 | 1336 |
| 137.3 | 1341 |
| 137.9 | 1348 |
| 136.4 | 1339 |
| 138.5 | 1345 |
| 137.7 | 1343 |
| 136.8 | 1338 |
| 138.1 | 1343 |
| 136.9 | 1354 |
| 135.9 | 1345 |
| 137.5 | 1355 |
| 138.1 | 1355 |
| 137.6 | 1348 |
| 138 | 1340 |
| 135.3 | 1329 |
| 137.4 | 1334 |
| 135.8 | 1328 |
| 136.6 | 1345 |
| 137.3 | 1344 |
| 135.4 | 1331 |
| 136.7 | 1338 |
| 135.8 | 1319 |
| 137.3 | 1327 |
| 137.1 | 1322 |
| 136.6 | 1317 |
| 136 | 1323 |
| 137.1 | 1323 |
| 137.4 | 1328 |
| 136.9 | 1346 |
| 135.1 | 1355 |
| 136.9 | 1360 |
| 139.1 | 1351 |
| 137.3 | 1369 |
| 138.2 | 1365 |
| 137.5 | 1381 |
| 137.7 | 1357 |
| 139 | 1363 |
| 137.1 | 1379 |
| 137.6 | 1381 |
| 137.5 | 1368 |
| 138.2 | 1359 |
| 137.5 | 1349 |
| 136.8 | 1350 |
| 135.5 | 1340 |
| 137.8 | 1338 |
| 135.5 | 1330 |
| 138.4 | 1328 |
| 137.6 | 1335 |
| 137.5 | 1345 |
| 137.5 | 1337 |
| 138.1 | 1343 |
| 136.5 | 1334 |
| 137.1 | 1339 |
| 137.8 | 1338 |
| 139.9 | 1340 |
| 137.2 | 1345 |
| 137.3 | 1354 |
| 136.9 | 1361 |
| 136 | 1360 |
| 136.9 | 1351 |
| 136.8 | 1344 |
| 138.1 | 1356 |
| 137.7 | 1356 |
| 137.9 | 1356 |
| 139.1 | 1363 |
| 138.8 | 1363 |
| 137.3 | 1377 |
| 138 | 1387 |
| 139.5 | 1378 |
| 137.3 | 1378 |
| 137.5 | 1392 |
| 138.7 | 1391 |
| 136.8 | 1386 |
| 137.2 | 1384 |
| 137.1 | 1381 |
| 137.1 | 1383 |
| 135.6 | 1382 |
| 135.6 | 1385 |
| 136 | 1389 |
| 134.9 | 1384 |
| 135.6 | 1385 |
| 135.4 | 1385 |
| 134.8 | 1391 |
| 135.5 | 1386 |
| 136.5 | 1391 |
| 136.4 | 1391 |
| 135.8 | 1386 |
| 135.7 | 1390 |
| 135.4 | 1391 |
| 136.4 | 1397 |
| 135.6 | 1391 |
| 136.1 | 1390 |
| 135.5 | 1386 |
| 134.9 | 1390 |
| 134.9 | 1394 |
| 134.9 | 1395 |
| 135.6 | 1395 |
| 136 | 1394 |
| 134.8 | 1394 |
| 134.5 | 1398 |
| 135.4 | 1395 |
| 134.4 | 1393 |
| 134.6 | 1384 |
| 134.3 | 1390 |
| 135 | 1386 |
| 134.7 | 1384 |
| 135.5 | 1387 |
| 134.6 | 1388 |
| 134.9 | 1390 |
| 134.4 | 1397 |
| 134.6 | 1394 |
| 133.8 | 1390 |
| 134.8 | 1390 |
| 135 | 1391 |
| 134.8 | 1392 |
| 134.6 | 1392 |
| 134.4 | 1395 |
| 135.4 | 1394 |
| 134.6 | 1391 |
| 134.2 | 1395 |
| 134.1 | 1400 |
| 133.8 | 1402 |
| 134.2 | 1409 |
| 133.9 | 1406 |
| 133.9 | 1406 |
| 133.9 | 1413 |
| 134.2 | 1417 |
| 134.1 | 1419 |
| 133.4 | 1411 |
| 134.3 | 1415 |
| 134.3 | 1417 |
| 134.6 | 1416 |
| 134.4 | 1418 |
| 134.5 | 1424 |
| 135.1 | 1421 |
| 134.2 | 1426 |
| 134.3 | 1434 |
| 133.5 | 1431 |
| 133.7 | 1437 |
| 134 | 1437 |
| 134.4 | 1435 |
| 133.3 | 1433 |
| 133.4 | 1433 |
| 133.3 | 1431 |
| 133.4 | 1424 |
| 133.8 | 1426 |
| 133.9 | 1427 |
| 133.5 | 1431 |
| 133.6 | 1437 |
| 133.1 | 1438 |
| 133.1 | 1436 |
| 133.8 | 1433 |
| 132.9 | 1432 |
| 134.1 | 1428 |
| 133.5 | 1433 |
| 133.1 | 1434 |
| 133.1 | 1436 |
| 134 | 1435 |
| 133.2 | 1438 |
| 133.4 | 1441 |
| 133.3 | 1439 |
| 133.6 | 1438 |
| 134 | 1432 |
| 133.5 | 1438 |
| 133 | 1441 |
| 132.7 | 1443 |
| 132.9 | 1450 |
| 133.4 | 1451 |
| 133.4 | 1452 |
| 132.8 | 1453 |
| 133.2 | 1460 |
| 132.8 | 1464 |
| 133.1 | 1465 |
| 133.4 | 1473 |
| 133.2 | 1467 |
| 132.8 | 1466 |
| 133 | 1466 |
| 133.9 | 1466 |
| 133.3 | 1467 |
| 132.8 | 1472 |
| 132.8 | 1476 |
| 133.7 | 1477 |
| 134.5 | 1476 |
| 133.8 | 1477 |
| 133.6 | 1483 |
| 134 | 1483 |
| 133.6 | 1482 |
| 133.6 | 1480 |
| 133.3 | 1477 |
| 133 | 1468 |
| 133.8 | 1469 |
| 134 | 1469 |
| 134.1 | 1466 |
| 133.5 | 1470 |
| 133.1 | 1469 |
| 133.8 | 1467 |
| 133.8 | 1468 |
| 133.9 | 1466 |
| 133.4 | 1475 |
| 133 | 1477 |
| 134 | 1478 |
| 134 | 1476 |
| 133.7 | 1470 |
| 133.9 | 1471 |
| 134 | 1469 |
| 133.8 | 1467 |
| 133.8 | 1468 |
| 134.3 | 1466 |
| 133.6 | 1467 |
| 133.1 | 1474 |
| 134.2 | 1474 |
| 134 | 1476 |
| 134.1 | 1470 |
| 133 | 1475 |
| 133.1 | 1471 |
| 133.8 | 1471 |
| 133.6 | 1467 |
| 133.5 | 1470 |
| 133.8 | 1468 |
| 134.1 | 1468 |
| 133.9 | 1467 |
| 134.1 | 1465 |
| 133.7 | 1468 |
| 133.4 | 1468 |
| 134.3 | 1470 |
| 134.1 | 1469 |
| 133.9 | 1470 |
| 134.2 | 1466 |
| 134.2 | 1466 |
| 133.7 | 1466 |
| 134.4 | 1460 |
| 134 | 1466 |
| 133.8 | 1473 |
| 134.1 | 1476 |
| 133.5 | 1474 |
| 134.1 | 1473 |
| 133.8 | 1470 |
| 133.8 | 1468 |
| 134.3 | 1473 |
| 133 | 1472 |
| 133.1 | 1477 |
| 133 | 1477 |
| 133.4 | 1478 |
| 133.2 | 1480 |
| 133.2 | 1485 |
| 133.4 | 1484 |
| 133.5 | 1485 |
| 133.6 | 1486 |
| 133.2 | 1481 |
| 133.7 | 1479 |
| 133.3 | 1474 |
| 133.9 | 1476 |
| 132.9 | 1473 |
| 133.1 | 1468 |
| 133.4 | 1464 |
| 132.9 | 1461 |
| 132.8 | 1461 |
| 132.7 | 1460 |
| 134.1 | 1457 |
| 133.4 | 1461 |
| 132.8 | 1460 |
| 132.6 | 1459 |
| 133.1 | 1463 |
| 133.2 | 1464 |
| 133.2 | 1464 |
| 132.9 | 1461 |
| 133 | 1462 |
| 134 | 1467 |
| 134.3 | 1462 |
| 134.3 | 1461 |
| 133.7 | 1457 |
| 134 | 1460 |
| 133.6 | 1459 |
| 132.8 | 1460 |
| 132.6 | 1460 |
| 134.3 | 1460 |
| 134.3 | 1458 |
| 134.2 | 1459 |
| 134.1 | 1458 |
| 133.8 | 1459 |
| 133.5 | 1462 |
| 134.5 | 1461 |
| 134 | 1463 |
| 133.5 | 1456 |
| 133 | 1459 |
| 133.7 | 1461 |
| 134 | 1462 |
| 133.7 | 1465 |
| 133.4 | 1459 |
| 133.7 | 1462 |
| 133.4 | 1457 |
| 133.9 | 1453 |
| 133.7 | 1456 |
| 133.5 | 1460 |
| 132.9 | 1461 |
| 133.3 | 1461 |
| 133.3 | 1463 |
| 133.2 | 1462 |
| 133.1 | 1457 |
| 133.1 | 1461 |
| 133.2 | 1460 |
| 132.7 | 1458 |
| 132.8 | 1458 |
| 132.3 | 1457 |
| 132.7 | 1453 |
| 132.9 | 1449 |
| 133.1 | 1456 |
| 134.2 | 1457 |
| 133.4 | 1468 |
| 133.7 | 1471 |
| 133.5 | 1472 |
| 133.8 | 1478 |
| 133.8 | 1480 |
| 133.7 | 1479 |
| 133.8 | 1479 |
| 133.7 | 1480 |
| 134.2 | 1478 |
| 133.6 | 1471 |
| 133.1 | 1468 |
| 133.7 | 1470 |
| 133.9 | 1465 |
| 133.8 | 1474 |
| 133.6 | 1476 |
| 133.3 | 1476 |
| 133.2 | 1476 |
| 133.4 | 1480 |
| 133.3 | 1479 |
| 133.5 | 1473 |
| 133.8 | 1472 |
| 133.8 | 1474 |
| 133.3 | 1480 |
| 133.6 | 1478 |
| 132.8 | 1476 |
| 133.3 | 1481 |
| 133 | 1486 |
| 133.5 | 1494 |
| 132.9 | 1489 |
| 133.1 | 1492 |
| 132.9 | 1494 |
| 133.7 | 1490 |
| 133.5 | 1496 |
| 133.1 | 1492 |
| 133.1 | 1493 |
| 133.2 | 1500 |
| 133.6 | 1501 |
| 133.3 | 1500 |
| 133 | 1494 |
| 133.4 | 1492 |
| 133.5 | 1489 |
| 133.6 | 1490 |
| 133.6 | 1487 |
| 133.6 | 1490 |
| 132.8 | 1490 |
| 133.3 | 1494 |
| 133.3 | 1496 |
| 132.9 | 1492 |
| 133.4 | 1495 |
| 133.3 | 1493 |
| 133.2 | 1493 |
| 133.8 | 1489 |
| 133.1 | 1491 |
| 132.9 | 1489 |
| 132.5 | 1492 |
| 132.5 | 1493 |
| 132.9 | 1495 |
| 132.7 | 1489 |
| 132.6 | 1485 |
| 132.8 | 1480 |
| 133.3 | 1474 |
| 134.2 | 1468 |
| 134.1 | 1470 |
| 133.5 | 1470 |
| 134.2 | 1475 |
| 133.7 | 1479 |
| 132.9 | 1484 |
| 133.5 | 1489 |
| 133.5 | 1484 |
| 133.2 | 1486 |
| 134.1 | 1486 |
| 134 | 1490 |
| 133 | 1496 |
| 133.3 | 1493 |
| 133.4 | 1491 |
| 133 | 1486 |
| 133.6 | 1492 |
| 132.8 | 1489 |
| 132.7 | 1491 |
| 133.2 | 1496 |
| 133.8 | 1497 |
| 133.9 | 1493 |
| 133.6 | 1491 |
| 133.3 | 1499 |
| 133.5 | 1500 |
| 133.6 | 1503 |
| 133 | 1507 |
| 132.5 | 1501 |
| 132.5 | 1500 |
| 132 | 1495 |
| 132.2 | 1501 |
| 133.3 | 1499 |
| 133.5 | 1499 |
| 132.8 | 1496 |
| 133.2 | 1504 |
| 132.9 | 1504 |
| 132.5 | 1498 |
| 133.1 | 1496 |
| 132.6 | 1496 |
| 133.6 | 1495 |
| 132.9 | 1497 |
| 133 | 1498 |
| 133.1 | 1498 |
| 133.3 | 1499 |
| 133.1 | 1503 |
| 133.7 | 1506 |
| 133.5 | 1503 |
| 132.7 | 1499 |
| 133.6 | 1503 |
| 132.8 | 1499 |
| 133.3 | 1501 |
| 132.7 | 1504 |
| 132.8 | 1506 |
| 132.9 | 1505 |
| 132.9 | 1504 |
| 133.1 | 1500 |
| 133.7 | 1503 |
| 133.3 | 1501 |
| 132.6 | 1502 |
| 133.7 | 1507 |
| 134.1 | 1506 |
| 133.4 | 1510 |
| 133.6 | 1512 |
| 133 | 1510 |
| 133.7 | 1507 |
| 134.5 | 1513 |
| 134 | 1522 |
| 134 | 1526 |
| 133.7 | 1526 |
| 133.3 | 1529 |
| 133.2 | 1539 |
| 133.4 | 1542 |
| 133.6 | 1536 |
| 133.5 | 1541 |
| 132.7 | 1539 |
| 132.7 | 1531 |
| 133.2 | 1532 |
| 133.3 | 1535 |
| 133.4 | 1540 |
| 133.3 | 1530 |
| 132.8 | 1538 |
| 133.7 | 1541 |
| 133.9 | 1539 |
| 133.6 | 1543 |
| 133 | 1541 |
| 133.6 | 1536 |
| 134.5 | 1534 |
| 134.5 | 1537 |
| 134.2 | 1543 |
| 132.7 | 1545 |
| 133.2 | 1540 |
| 133.5 | 1539 |
| 133 | 1538 |
| 132.8 | 1543 |
| 132.2 | 1549 |
| 132.5 | 1556 |
| 132.6 | 1558 |
| 132.9 | 1559 |
| 132.7 | 1562 |
| 132.7 | 1565 |
| 132.9 | 1565 |
| 132.9 | 1566 |
| 133.2 | 1568 |
| 132.8 | 1556 |
| 132.9 | 1563 |
| 132.8 | 1569 |
| 132.7 | 1583 |
| 133.3 | 1592 |
| 132.6 | 1593 |
| 133.3 | 1579 |
| 133.1 | 1582 |
| 133.4 | 1587 |
| 133.4 | 1585 |
| 133.2 | 1603 |
| 133 | 1619 |
| 133.4 | 1598 |
| 132.7 | 1609 |
| 133.6 | 1623 |
| 133.1 | 1627 |
| 133.1 | 1636 |
| 132.8 | 1640 |
| 131.9 | 1621 |
| 131.7 | 1639 |
| 132.6 | 1640 |
| 133.7 | 1657 |
| 132.9 | 1647 |
| 132.3 | 1639 |
| 133.8 | 1647 |
| 132.3 | 1660 |
| 132.9 | 1683 |
| 133.1 | 1697 |
| 133.6 | 1694 |
| 132.8 | 1694 |
| 133.2 | 1718 |
| 132.4 | 1721 |
| 132.9 | 1720 |
| 133.4 | 1709 |
| 132.5 | 1725 |
| 132.6 | 1734 |
| 133.4 | 1744 |
| 132.8 | 1755 |
| 132.7 | 1739 |
| 132.9 | 1745 |
| 133.2 | 1734 |
| 132.2 | 1761 |
| 132.8 | 1754 |
| 132.3 | 1771 |
| 132.2 | 1774 |
| 133.3 | 1767 |
| 133.4 | 1756 |
| 131.6 | 1766 |
| 132.4 | 1785 |
| 133.2 | 1781 |
| 132.8 | 1771 |
| 133.4 | 1782 |
| 132.5 | 1758 |
| 132.9 | 1784 |
| 132.6 | 1786 |
| 133.4 | 1808 |
| 133.2 | 1812 |
| 132.3 | 1834 |
| 132.7 | 1827 |
| 132.5 | 1827 |
| 133.2 | 1826 |
| 133.6 | 1835 |
| 133.4 | 1835 |
| 133.7 | 1837 |
| 132.4 | 1854 |
| 132.8 | 1861 |
| 133 | 1877 |
| 132.9 | 1886 |
| 132.7 | 1887 |
| 132.9 | 1903 |
| 132.9 | 1898 |
| 133.6 | 1914 |
| 133.4 | 1919 |
| 132.9 | 1910 |
| 131.7 | 1933 |
| 132.7 | 1932 |
| 132.7 | 1911 |
| 132.6 | 1929 |
| 132.5 | 1915 |
| 133.2 | 1922 |
| 133.3 | 1927 |
| 132.2 | 1921 |
| 133.1 | 1929 |
| 132.7 | 1925 |
| 132.8 | 1944 |
| 133.5 | 1942 |
| 132.9 | 1922 |
| 132.9 | 1918 |
| 134.1 | 1915 |
| 133.2 | 1911 |
| 132.5 | 1929 |
| 132.9 | 1917 |
| 132.1 | 1912 |
| 133.1 | 1928 |
| 132.5 | 1909 |
| 132.7 | 1926 |
| 133 | 1930 |
| 133 | 1922 |
| 133 | 1923 |
| 132.7 | 1908 |
| 132.7 | 1929 |
| 132.9 | 1926 |
| 132.9 | 1933 |
| 133.2 | 1938 |
| 133.1 | 1927 |
| 133.2 | 1932 |
| 133.2 | 1922 |
| 133.5 | 1926 |
| 132.8 | 1921 |
| 132.2 | 1927 |
| 134.3 | 1945 |
| 133 | 1951 |
| 132.5 | 1972 |
| 132.4 | 1960 |
| 133.4 | 1964 |
| 133.1 | 1962 |
| 133.3 | 1977 |
| 133.5 | 1999 |
| 133.8 | 2010 |
| 133.4 | 2020 |
| 132.4 | 2022 |
| 134 | 2024 |
| 133.1 | 2029 |
| 132.4 | 2028 |
| 132.8 | 2041 |
| 133.1 | 2038 |
| 132.5 | 2041 |
| 133.5 | 2051 |
| 134.1 | 2059 |
| 132.4 | 2048 |
| 133.1 | 2069 |
| 133.9 | 2071 |
| 133.6 | 2100 |
| 132.4 | 2098 |
| 132.6 | 2082 |
| 132.9 | 2080 |
| 133.1 | 2065 |
| 133.4 | 2082 |
| 133.2 | 2092 |
| 132.9 | 2101 |
| 133.5 | 2093 |
| 133.1 | 2082 |
| 132.9 | 2111 |
| 133.6 | 2106 |
| 133.7 | 2106 |
| 133 | 2125 |
| 132.2 | 2121 |
| 132.6 | 2135 |
| 132.4 | 2135 |
| 132.8 | 2132 |
| 132.9 | 2154 |
| 132.7 | 2142 |
| 132.9 | 2148 |
| 132.5 | 2161 |
| 132.9 | 2146 |
| 133.2 | 2142 |
| 132.6 | 2142 |
| 132.7 | 2146 |
| 132.5 | 2142 |
| 132.4 | 2149 |
| 132.5 | 2138 |
| 133 | 2159 |
| 133.4 | 2153 |
| 133.5 | 2152 |
| 133.4 | 2174 |
| 133.9 | 2174 |
| 133.1 | 2159 |
| 133.2 | 2152 |
| 133.1 | 2185 |
| 133.5 | 2206 |
| 132.2 | 2228 |
| 133.5 | 2219 |
| 133 | 2217 |
| 132.8 | 2221 |
| 132.9 | 2223 |
| 133.1 | 2219 |
| 133 | 2225 |
| 134.3 | 2219 |
| 133.8 | 2231 |
| 133.7 | 2226 |
| 133.8 | 2219 |
| 133.3 | 2215 |
| 133.6 | 2224 |
| 133.9 | 2250 |
| 133 | 2260 |
| 132.6 | 2253 |
| 132.4 | 2241 |
| 133.6 | 2257 |
| 133.4 | 2246 |
| 132.9 | 2257 |
| 133.6 | 2259 |
| 133.5 | 2259 |
| 133.4 | 2267 |
| 133.5 | 2281 |
| 132.8 | 2265 |
| 133.2 | 2288 |
| 133 | 2287 |
| 133.4 | 2273 |
| 133.6 | 2298 |
| 133.1 | 2316 |
| 133.8 | 2312 |
| 133.2 | 2310 |
| 134.1 | 2312 |
| 133.5 | 2303 |
| 133.2 | 2288 |
| 133.3 | 2304 |
| 133.3 | 2299 |
| 133.9 | 2323 |
| 133.1 | 2334 |
| 133.3 | 2337 |
| 133.9 | 2340 |
| 133.3 | 2324 |
| 133 | 2336 |
| 133.4 | 2348 |
| 134 | 2347 |
| 133 | 2348 |
| 133.7 | 2367 |
| 133.4 | 2360 |
| 133.9 | 2348 |
| 133.1 | 2359 |
| 133.2 | 2380 |
| 133.4 | 2362 |
| 133.8 | 2349 |
| 134.3 | 2367 |
| 133.1 | 2373 |
| 133.2 | 2372 |
| 133.5 | 2381 |
| 133.1 | 2387 |
| 133.4 | 2395 |
| 133.6 | 2405 |
| 133.3 | 2438 |
| 133.1 | 2406 |
| 133.4 | 2405 |
| 133.6 | 2433 |
| 133.4 | 2435 |
| 133.8 | 2450 |
| 134 | 2442 |
| 133.5 | 2445 |
| 133 | 2432 |
| 133 | 2422 |
| 133.7 | 2433 |
| 134 | 2449 |
| 133.5 | 2443 |
| 134 | 2424 |
| 134.2 | 2428 |
| 133.4 | 2477 |
| 132.7 | 2484 |
| 133.6 | 2515 |
| 133.3 | 2514 |
| 132.7 | 2538 |
| 133.8 | 2518 |
| 134 | 2534 |
| 133.2 | 2540 |
| 133.2 | 2514 |
| 132.9 | 2505 |
| 133 | 2501 |
| 133.4 | 2499 |
| 133 | 2511 |
| 133.6 | 2510 |
| 134.1 | 2540 |
| 134 | 2512 |
| 133.6 | 2524 |
| 134 | 2511 |
| 133.1 | 2519 |
| 133.9 | 2502 |
| 134.2 | 2525 |
| 133.7 | 2538 |
| 134.2 | 2556 |
| 133.3 | 2555 |
| 133.6 | 2555 |
| 133.9 | 2559 |
| 134.2 | 2565 |
| 133.7 | 2567 |
| 133.7 | 2582 |
| 133.8 | 2568 |
| 133.7 | 2569 |
| 133.5 | 2566 |
| 134.2 | 2555 |
| 133.6 | 2553 |
| 133.4 | 2571 |
| 133.3 | 2585 |
| 133 | 2616 |
| 133.8 | 2623 |
| 133.6 | 2636 |
| 133.9 | 2633 |
| 133.5 | 2660 |
| 134.1 | 2670 |
| 134.1 | 2686 |
| 133.4 | 2672 |
| 133.9 | 2658 |
| 133.9 | 2661 |
| 134.1 | 2688 |
| 134.2 | 2703 |
| 134.1 | 2711 |
| 134.2 | 2691 |
| 134.3 | 2730 |
| 134.5 | 2716 |
| 134.1 | 2708 |
| 133.7 | 2706 |
| 133.8 | 2693 |
| 134.9 | 2673 |
| 135.5 | 2677 |
| 134.6 | 2670 |
| 134.6 | 2665 |
| 133.8 | 2663 |
| 134.3 | 2692 |
| 133.9 | 2695 |
| 133.9 | 2698 |
| 134.5 | 2726 |
| 133.9 | 2724 |
| 133.5 | 2724 |
| 133.8 | 2730 |
| 134 | 2725 |
| 132.7 | 2706 |
| 133.7 | 2711 |
| 132.9 | 2748 |
| 133.4 | 2749 |
| 134.2 | 2741 |
| 133.2 | 2743 |
| 133.4 | 2754 |
| 133.6 | 2742 |
| 133 | 2767 |
| 133.6 | 2771 |
| 133.5 | 2754 |
| 132.9 | 2755 |
| 133 | 2733 |
| 134 | 2710 |
| 134.2 | 2724 |
| 133.7 | 2719 |
| 133.8 | 2737 |
| 133.3 | 2757 |
| 133.7 | 2780 |
| 133.5 | 2767 |
| 133.6 | 2771 |
| 134.8 | 2773 |
| 133.7 | 2767 |
| 133.7 | 2766 |
| 133.5 | 2782 |
| 134.2 | 2785 |
| 134 | 2793 |
| 134.5 | 2801 |
| 133.7 | 2784 |
| 134 | 2784 |
| 133.9 | 2788 |
| 133.7 | 2789 |
| 133.7 | 2781 |
| 134.4 | 2793 |
| 134.2 | 2812 |
| 133.9 | 2802 |
| 133.8 | 2783 |
| 133.6 | 2769 |
| 133.7 | 2773 |
| 133.5 | 2754 |
| 134.2 | 2755 |
| 134 | 2766 |
| 133.2 | 2767 |
| 134.3 | 2755 |
| 134.1 | 2757 |
| 134 | 2768 |
| 133.6 | 2787 |
| 133.9 | 2797 |
| 133.2 | 2765 |
| 134.2 | 2789 |
| 134 | 2775 |
| 134.2 | 2779 |
| 134.2 | 2786 |
| 133.7 | 2796 |
| 134.1 | 2779 |
| 133 | 2796 |
| 133.9 | 2762 |
| 133.6 | 2768 |
| 133.7 | 2764 |
| 133.8 | 2776 |
| 134.1 | 2805 |
| 133.6 | 2786 |
| 133.6 | 2817 |
| 133.6 | 2832 |
| 133.8 | 2828 |
| 134.2 | 2834 |
| 134.4 | 2823 |
| 134.6 | 2820 |
| 134.5 | 2835 |
| 133.4 | 2820 |
| 133.1 | 2823 |
| 132.7 | 2842 |
| 134.9 | 2874 |
| 133.7 | 2855 |
| 133.4 | 2863 |
| 133.9 | 2861 |
| 133.8 | 2845 |
| 133.9 | 2858 |
| 133.7 | 2868 |
| 134.1 | 2871 |
| 134.3 | 2900 |
| 132.9 | 2879 |
| 133.1 | 2853 |
| 134.1 | 2873 |
| 134.3 | 2851 |
| 133.5 | 2875 |
| 134.5 | 2894 |
| 133.6 | 2906 |
| 134.2 | 2899 |
| 134.4 | 2884 |
| 134.4 | 2880 |
| 134.4 | 2855 |
| 133.7 | 2870 |
| 133.6 | 2869 |
| 133.6 | 2862 |
| 133.8 | 2865 |
| 133.6 | 2858 |
| 134.2 | 2893 |
| 134.1 | 2891 |
| 134.7 | 2865 |
| 135 | 2881 |
| 134.1 | 2902 |
| 134.2 | 2910 |
| 134 | 2913 |
| 134.5 | 2916 |
| 133.8 | 2914 |
| 134.2 | 2933 |
| 134.5 | 2949 |
| 133.3 | 2953 |
| 133.9 | 2950 |
| 134.2 | 2950 |
| 133.9 | 2928 |
| 134.2 | 2942 |
| 134.5 | 2992 |
| 134.6 | 2976 |
| 133.1 | 2993 |
| 133.5 | 3007 |
| 133.9 | 3017 |
| 134.1 | 3017 |
| 133.1 | 3002 |
| 134.6 | 3024 |
| 133.4 | 3008 |
| 134.3 | 3001 |
| 134.1 | 3013 |
| 134 | 3010 |
| 133.9 | 3011 |
| 133.8 | 3015 |
| 134.6 | 3003 |
| 133.8 | 3003 |
| 134.3 | 3013 |
| 135 | 3026 |
| 133.8 | 3020 |
| 133.5 | 3016 |
| 134.1 | 2998 |
| 133.9 | 2984 |
| 134.1 | 3001 |
| 133.9 | 3008 |
| 134 | 2980 |
| 133.3 | 2993 |
| 133.1 | 2977 |
| 133.3 | 2940 |
| 133.4 | 2956 |
| 133.7 | 2953 |
| 133.8 | 2968 |
| 133.8 | 2973 |
| 133.9 | 2974 |
| 133.8 | 2985 |
| 134.4 | 2967 |
| 133.8 | 2966 |
| 134.2 | 2997 |
| 134.6 | 3019 |
| 133.1 | 2985 |
| 133.4 | 2998 |
| 133.8 | 3001 |
| 133.9 | 3025 |
| 133.9 | 3031 |
| 133.2 | 3021 |
| 133.4 | 3017 |
| 133.6 | 3036 |
| 134.2 | 3081 |
| 134.2 | 3081 |
| 134.2 | 3095 |
| 134.2 | 3083 |
| 134 | 3057 |
| 133.9 | 3053 |
| 134.2 | 3060 |
| 134.7 | 3057 |
| 133.4 | 3056 |
| 134.2 | 3054 |
| 134.9 | 3051 |
| 134 | 3036 |
| 134.9 | 3046 |
| 134 | 3034 |
| 133.1 | 3051 |
| 134.1 | 3059 |
| 133.6 | 3071 |
| 134.9 | 3099 |
| 133.9 | 3094 |
| 134 | 3124 |
| 134 | 3102 |
| 134.5 | 3109 |
| 134.6 | 3089 |
| 133.6 | 3078 |
| 134.2 | 3083 |
| 134 | 3092 |
| 133.6 | 3112 |
| 133.4 | 3117 |
| 134.5 | 3127 |
| 134.8 | 3150 |
| 133.5 | 3160 |
| 133.7 | 3158 |
| 134.1 | 3157 |
| 134.1 | 3159 |
| 134.2 | 3149 |
| 133.5 | 3169 |
| 134.5 | 3179 |
| 133.9 | 3150 |
| 133.2 | 3153 |
| 134.1 | 3177 |
| 134.9 | 3192 |
| 133.7 | 3187 |
| 133.4 | 3204 |
| 134 | 3217 |
| 134.1 | 3210 |
| 134.1 | 3157 |
| 134 | 3185 |
| 134.7 | 3166 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |


**`hole_ramp_rel130_d4` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 129.4
- `free_shell.areal_density_ratio`: 0.4929
- `free_shell.msd.1 ns`: 252.9
- `free_shell.msd.10 ns`: 665.9
- `free_shell.msd.end`: 3536
- `free_shell.msd.end_ns`: 68
- `params.hole_hold_ps`: 1e+04
- `params.release_t_c`: 130
- `params.scaffold_d_nm`: 4
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `scaffold.d_nm`: 4
- `scaffold.nearest_tethered_r_held_min`: 68.29
- `scaffold.nearest_tethered_r_t0`: 70
- `scaffold.tethered_fraction`: 0.1594
- T (°C): 25
- `t_close_ns`: 0.5
- `thickness_final`: 134.1
- `thickness_t0`: 161.4

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 129.8 | — |
| 129.8 | — |
| 129.5 | — |
| 129.6 | — |
| 129.2 | — |
| 129.9 | — |
| 129.7 | — |
| 129.6 | — |
| 130 | — |
| 129.7 | — |
| 129.6 | — |
| 129.8 | — |
| 129.6 | — |
| 131.1 | — |
| 129.6 | — |
| 130 | — |
| 129.5 | — |
| 129.6 | — |
| 130 | — |
| 129.6 | — |
| 129.3 | — |
| 129.9 | — |
| 128.8 | — |
| 129.4 | — |
| 129.8 | — |
| 129.3 | — |
| 129.9 | — |
| 129.5 | — |
| 129.8 | — |
| 130 | — |
| 129.5 | — |
| 130.4 | — |
| 129.5 | — |
| 129.9 | — |
| 130.1 | — |
| 129.8 | — |
| 130 | — |
| 129.9 | — |
| 129.8 | — |
| 129.5 | — |
| 130 | — |
| 129.3 | — |
| 129.3 | — |
| 129.4 | — |
| 129.1 | — |
| 129.6 | — |
| 129.6 | — |
| 130 | — |
| 129.8 | — |
| 129.8 | — |
| 131 | — |
| 129.8 | — |
| 129.9 | — |
| 129.5 | — |
| 130 | — |
| 130.4 | — |
| 130.2 | — |
| 130.2 | — |
| 129.4 | — |
| 129.7 | — |
| 130 | — |
| 130.3 | — |
| 130.4 | — |
| 130.2 | — |
| 130.3 | — |
| 130.2 | — |
| 129.6 | — |
| 130.2 | — |
| 130.1 | — |
| 130 | — |
| 130.3 | — |
| 129.8 | — |
| 130.5 | — |
| 130.1 | — |
| 130.6 | — |
| 130.3 | — |
| 130.4 | — |
| 130.6 | — |
| 130.6 | — |
| 130.7 | — |
| 130.7 | — |
| 131.5 | — |
| 130.5 | — |
| 130.6 | — |
| 131.9 | — |
| 131.1 | — |
| 131.1 | — |
| 131.2 | — |
| 130.3 | — |
| 131.6 | — |
| 131.7 | — |
| 131.7 | — |
| 131.1 | — |
| 131.4 | — |
| 131.5 | — |
| 131.5 | — |
| 131.3 | — |
| 131.8 | — |
| 131.6 | — |
| 132.1 | — |
| 131.5 | — |
| 131.6 | — |
| 131.6 | — |
| 132.1 | — |
| 132 | — |
| 131.9 | — |
| 132 | — |
| 131.6 | — |
| 132.4 | — |
| 132.2 | — |
| 131.9 | — |
| 131.8 | — |
| 132.3 | — |
| 132.7 | — |
| 132.4 | — |
| 132.3 | — |
| 132.5 | — |
| 132.9 | — |
| 131.8 | — |
| 131.9 | — |
| 132.5 | — |
| 132.4 | — |
| 133.1 | — |
| 132.8 | — |
| 133 | — |
| 133.3 | — |
| 133.3 | — |
| 133.4 | — |
| 134.1 | — |
| 133.3 | — |
| 133.3 | — |
| 133.1 | — |
| 133.4 | — |
| 133.6 | — |
| 133.5 | — |
| 133.9 | — |
| 133.9 | — |
| 134 | — |
| 133 | — |
| 133.5 | — |
| 134.1 | — |
| 134 | — |
| 133.7 | — |
| 134 | — |
| 133.6 | — |
| 133.8 | — |
| 133.4 | — |
| 133.4 | — |
| 134 | — |
| 134.5 | — |
| 133.8 | — |
| 133.7 | — |
| 133.6 | — |
| 134.2 | — |
| 133.7 | — |
| 134 | — |
| 134.6 | — |
| 134.4 | — |
| 134.8 | — |
| 134.3 | — |
| 134.6 | — |
| 134.3 | — |
| 134.1 | — |
| 134.3 | — |
| 134.2 | — |
| 134.9 | — |
| 135.1 | — |
| 135.1 | — |
| 134.8 | — |
| 134.6 | — |
| 135 | — |
| 135.9 | — |
| 136.3 | — |
| 135.3 | — |
| 135 | — |
| 136 | — |
| 135.8 | — |
| 135.9 | — |
| 136.2 | — |
| 135.5 | — |
| 136.5 | — |
| 136.4 | — |
| 136 | — |
| 135.9 | — |
| 135.8 | — |
| 136.8 | — |
| 136.7 | — |
| 136.8 | — |
| 136.8 | — |
| 136.7 | — |
| 137 | — |
| 137.1 | — |
| 137.6 | — |
| 137.9 | — |
| 137.4 | — |
| 137.8 | — |
| 136.8 | — |
| 137.8 | — |
| 137.8 | — |
| 137.6 | — |
| 138.3 | — |
| 138.9 | — |
| 138.1 | — |
| 138.2 | — |
| 137.5 | — |
| 137.9 | — |
| 138.2 | — |
| 138.6 | — |
| 138.5 | — |
| 137.8 | — |
| 137.6 | — |
| 138.3 | — |
| 138.5 | — |
| 138.8 | — |
| 138.2 | — |
| 138.5 | — |
| 138.4 | — |
| 139.3 | — |
| 139.1 | — |
| 138.2 | — |
| 138.8 | — |
| 139.6 | — |
| 139.8 | — |
| 140.4 | — |
| 140.4 | — |
| 140.7 | — |
| 140.2 | — |
| 140.1 | — |
| 140 | — |
| 140.5 | — |
| 140.1 | — |
| 140.5 | — |
| 140.1 | — |
| 140.1 | — |
| 140.1 | — |
| 141.1 | — |
| 140.1 | — |
| 140.8 | — |
| 141.2 | — |
| 141.5 | — |
| 141.7 | — |
| 140.7 | — |
| 141 | — |
| 141.9 | — |
| 141.7 | — |
| 142.3 | — |
| 141.8 | — |
| 140.9 | — |
| 141.2 | — |
| 140.8 | — |
| 142.1 | — |
| 142.1 | — |
| 141.1 | — |
| 142.1 | — |
| 141.9 | — |
| 142.3 | — |
| 142.3 | — |
| 142.3 | — |
| 142.5 | — |
| 142.5 | — |
| 142.5 | — |
| 142 | — |
| 142.7 | — |
| 143.2 | — |
| 142.6 | — |
| 144.2 | — |
| 143.9 | — |
| 143 | — |
| 143.9 | — |
| 143.6 | — |
| 144.1 | — |
| 143.7 | — |
| 144.1 | — |
| 144.2 | — |
| 144.3 | — |
| 143.9 | — |
| 144.8 | — |
| 145.4 | — |
| 145.4 | — |
| 145.4 | — |
| 145.4 | — |
| 145.3 | — |
| 145.7 | — |
| 145.2 | — |
| 145.4 | — |
| 144.6 | — |
| 145.2 | — |
| 145.9 | — |
| 145.7 | — |
| 145.1 | — |
| 146.3 | — |
| 146.2 | — |
| 146.6 | — |
| 147.3 | — |
| 146.8 | — |
| 147.4 | — |
| 146.6 | — |
| 147.8 | — |
| 146.9 | — |
| 147.4 | — |
| 147.9 | — |
| 147.2 | — |
| 148.3 | — |
| 148.3 | — |
| 147.5 | — |
| 147.4 | — |
| 148.7 | — |
| 149 | — |
| 147.5 | — |
| 147.6 | — |
| 147.8 | — |
| 147.9 | — |
| 147.8 | — |
| 149.1 | — |
| 148.4 | — |
| 148 | — |
| 148.4 | — |
| 148.9 | — |
| 149.1 | — |
| 149.1 | — |
| 149.4 | — |
| 148.9 | — |
| 150 | — |
| 149.4 | — |
| 149.7 | — |
| 149.3 | — |
| 150.5 | — |
| 149.4 | — |
| 150.1 | — |
| 150.4 | — |
| 151.4 | — |
| 151.3 | — |
| 150.3 | — |
| 150.6 | — |
| 151.3 | — |
| 151.6 | — |
| 151.8 | — |
| 152.2 | — |
| 152.1 | — |
| 151.5 | — |
| 152 | — |
| 152.3 | — |
| 152.5 | — |
| 152.5 | — |
| 153 | — |
| 152.9 | — |
| 153.3 | — |
| 152.9 | — |
| 153.4 | — |
| 152.8 | — |
| 152 | — |
| 152.9 | — |
| 153 | — |
| 153.6 | — |
| 153.9 | — |
| 153.1 | — |
| 153.7 | — |
| 154.2 | — |
| 153.7 | — |
| 154.5 | — |
| 154.5 | — |
| 154.5 | — |
| 154 | — |
| 154.2 | — |
| 155.2 | — |
| 154.1 | — |
| 155.2 | — |
| 156 | — |
| 155.6 | — |
| 156.7 | — |
| 156.5 | — |
| 156.5 | — |
| 156.7 | — |
| 156.3 | — |
| 156.4 | — |
| 157.1 | — |
| 156.6 | — |
| 156.9 | — |
| 156.8 | — |
| 158.6 | — |
| 158.3 | — |
| 158.1 | — |
| 158.2 | — |
| 158.4 | — |
| 158.3 | — |
| 158.9 | — |
| 159.9 | — |
| 159.1 | — |
| 159 | — |
| 160.3 | — |
| 159.3 | — |
| 159.7 | — |
| 160.8 | — |
| 161.1 | — |
| 160.7 | — |
| 159.3 | — |
| 160.2 | — |
| 160.3 | — |
| 160.3 | — |
| 160.4 | — |
| 161.3 | — |
| 160.6 | — |
| 160.9 | — |
| 161.6 | — |
| 161.8 | — |
| 161.5 | — |
| 161 | — |
| 160.6 | — |
| 160.7 | — |
| 161.6 | — |
| 161.7 | — |
| 162.8 | — |
| 162.5 | — |
| 162.4 | — |
| 162.7 | — |
| 161.4 | — |
| 160 | — |
| 160.4 | — |
| 161.6 | — |
| 162.1 | — |
| 160.5 | — |
| 161.2 | — |
| 160.3 | — |
| 162 | — |
| 160.8 | — |
| 161.2 | — |
| 160.7 | — |
| 161.2 | — |
| 160.4 | — |
| 161.3 | — |
| 161.1 | — |
| 160.1 | — |
| 161.1 | — |
| 161.8 | — |
| 161.3 | — |
| 161.2 | — |
| 160.2 | — |
| 161.4 | — |
| 161.6 | — |
| 162.3 | — |
| 161.9 | — |
| 163 | — |
| 161.4 | — |
| 163.5 | — |
| 162.6 | — |
| 161.6 | — |
| 162 | — |
| 161 | — |
| 162.9 | — |
| 161.6 | — |
| 162.1 | — |
| 163.1 | — |
| 161.4 | — |
| 161.7 | — |
| 161.8 | — |
| 161.8 | — |
| 160.3 | — |
| 162.5 | — |
| 161.4 | — |
| 161.7 | — |
| 161.6 | — |
| 161.4 | — |
| 161.7 | — |
| 161.5 | — |
| 162.1 | — |
| 161.4 | — |
| 160.9 | — |
| 161.4 | — |
| 162.2 | — |
| 161.3 | — |
| 162.2 | — |
| 161.5 | — |
| 162 | — |
| 161.7 | — |
| 162.7 | — |
| 162.1 | — |
| 162.3 | — |
| 160.7 | — |
| 161.4 | — |
| 162.7 | — |
| 162.3 | — |
| 161.9 | — |
| 161.3 | — |
| 163.3 | — |
| 162.3 | — |
| 160.8 | — |
| 160.9 | — |
| 161.1 | — |
| 162.6 | — |
| 161.4 | — |
| 160.5 | — |
| 161.1 | — |
| 162.6 | — |
| 161.7 | — |
| 161.4 | — |
| 161.9 | — |
| 163.1 | — |
| 163.4 | — |
| 163 | — |
| 162.9 | — |
| 164.2 | — |
| 163 | — |
| 162.4 | — |
| 162 | — |
| 161.3 | — |
| 160.9 | — |
| 162.8 | — |
| 162.3 | — |
| 163 | — |
| 162.1 | — |
| 162 | — |
| 162.1 | — |
| 161.9 | — |
| 161 | — |
| 161.7 | — |
| 161.4 | — |
| 162 | — |
| 161.5 | — |
| 162 | — |
| 161.2 | — |
| 161.7 | — |
| 161.3 | — |
| 161.7 | — |
| 161.8 | — |
| 162.2 | — |
| 161.7 | — |
| 161.7 | — |
| 162 | — |
| 162.3 | — |
| 162.3 | — |
| 161.2 | — |
| 161.4 | — |
| 162.2 | — |
| 162.3 | — |
| 161.7 | — |
| 161.7 | — |
| 162.4 | — |
| 161.9 | — |
| 161.9 | — |
| 161.5 | — |
| 162 | — |
| 162.6 | — |
| 163.7 | — |
| 161.9 | — |
| 161.9 | — |
| 162.8 | — |
| 163 | — |
| 162.5 | — |
| 161.8 | — |
| 161.1 | — |
| 162 | — |
| 161.8 | — |
| 162 | — |
| 161.6 | — |
| 162.6 | — |
| 162 | — |
| 161.5 | — |
| 161.5 | — |
| 161.9 | — |
| 162.2 | — |
| 163.4 | — |
| 161.2 | — |
| 161.2 | — |
| 162.3 | — |
| 162.5 | — |
| 162.8 | — |
| 162.8 | — |
| 161.4 | — |
| 163.4 | — |
| 163.1 | — |
| 162.2 | — |
| 162 | — |
| 162.5 | — |
| 161.2 | — |
| 162.1 | — |
| 160.5 | — |
| 161.3 | — |
| 162 | — |
| 162.4 | — |
| 162.2 | — |
| 161.8 | — |
| 163.5 | — |
| 163.1 | — |
| 161.8 | — |
| 162.6 | — |
| 162.9 | — |
| 162.4 | — |
| 162 | — |
| 161.9 | — |
| 161.5 | — |
| 161.9 | — |
| 161.7 | — |
| 162.4 | — |
| 163.8 | — |
| 161.7 | — |
| 163.6 | — |
| 162.4 | — |
| 162.8 | — |
| 163.5 | — |
| 162.2 | — |
| 161.4 | 0 |
| 161.5 | 8.013 |
| 159.3 | 12.27 |
| 158.5 | 15.45 |
| 158.1 | 18.75 |
| 158.5 | 21.11 |
| 157.9 | 22.76 |
| 157.8 | 23.79 |
| 156.4 | 25.53 |
| 157.3 | 27.86 |
| 157.1 | 29.26 |
| 157.3 | 31.11 |
| 157.2 | 33.05 |
| 156.5 | 34.73 |
| 156.8 | 35.92 |
| 156.7 | 37.72 |
| 155.9 | 38.52 |
| 156.3 | 39.59 |
| 156.2 | 40.55 |
| 154.9 | 41.22 |
| 155.8 | 42.97 |
| 156.4 | 45.4 |
| 155.7 | 47.64 |
| 155.9 | 49.48 |
| 155.4 | 50.93 |
| 154.8 | 52.82 |
| 155 | 53.99 |
| 153.2 | 55.45 |
| 154.7 | 55.45 |
| 153.9 | 57.29 |
| 153.8 | 59.81 |
| 154.2 | 61.71 |
| 153.7 | 63.93 |
| 152.9 | 64.41 |
| 153.8 | 66.33 |
| 153.1 | 66.96 |
| 153 | 68.14 |
| 152.6 | 68.89 |
| 152.5 | 69.73 |
| 152.1 | 70.5 |
| 152.3 | 70.72 |
| 153 | 71.17 |
| 152.4 | 72.39 |
| 152.7 | 73.6 |
| 151.9 | 74.83 |
| 151.6 | 76.3 |
| 152.7 | 77.38 |
| 152.1 | 78.43 |
| 151.5 | 80.07 |
| 151.1 | 80.78 |
| 150.8 | 81.86 |
| 151 | 83.73 |
| 150.9 | 86.49 |
| 150.4 | 87.95 |
| 151.2 | 87.81 |
| 151.1 | 86.51 |
| 151.4 | 85.97 |
| 150.8 | 88.89 |
| 151.1 | 92.16 |
| 149.9 | 93.69 |
| 149.5 | 94.03 |
| 150.5 | 94.78 |
| 150.5 | 94.48 |
| 150.5 | 94.52 |
| 149.9 | 96.28 |
| 150.8 | 98 |
| 150 | 97.89 |
| 149.9 | 100.5 |
| 149 | 102.6 |
| 149.2 | 104.4 |
| 149.1 | 105.6 |
| 149.1 | 105.7 |
| 148.9 | 107.2 |
| 150.6 | 109.7 |
| 149.5 | 111.6 |
| 148.6 | 113.6 |
| 149.1 | 113.7 |
| 149.4 | 115.2 |
| 148.8 | 117.7 |
| 148 | 121.6 |
| 148 | 124.1 |
| 148.6 | 125.4 |
| 148.3 | 125.2 |
| 148.6 | 126 |
| 148.6 | 128.3 |
| 148.6 | 131.1 |
| 148.1 | 133.9 |
| 146 | 137.7 |
| 146.9 | 139.2 |
| 145.9 | 139.8 |
| 146.9 | 140 |
| 144.9 | 142.8 |
| 147.6 | 142.6 |
| 147.2 | 144.1 |
| 147.4 | 146.1 |
| 144.1 | 151.5 |
| 143 | 154.7 |
| 143.2 | 153.6 |
| 143.8 | 154.6 |
| 142.1 | 158.2 |
| 142.5 | 160.7 |
| 144.5 | 163 |
| 142.4 | 166.6 |
| 142.9 | 167.8 |
| 142.2 | 170.4 |
| 140.8 | 173.6 |
| 140.4 | 175.6 |
| 141.3 | 178.4 |
| 140.7 | 178 |
| 140.4 | 181.6 |
| 140.5 | 184.1 |
| 141.1 | 184.4 |
| 140.7 | 184 |
| 140 | 185.7 |
| 140.3 | 187.1 |
| 140.5 | 189.2 |
| 140.2 | 190.5 |
| 140.3 | 193 |
| 139.4 | 195 |
| 138.8 | 196.6 |
| 138.1 | 198.3 |
| 137.3 | 198 |
| 137.5 | 198.7 |
| 137.7 | 200.4 |
| 138.2 | 202.7 |
| 138.5 | 203.4 |
| 137.2 | 203.2 |
| 138.4 | 204.3 |
| 137 | 205 |
| 138.5 | 206.6 |
| 138.3 | 207.8 |
| 136.6 | 207.7 |
| 137.2 | 208.7 |
| 137 | 209.4 |
| 137.7 | 210.7 |
| 135.4 | 212.3 |
| 138.2 | 212.5 |
| 134.4 | 215.2 |
| 136.8 | 216 |
| 136.7 | 215.5 |
| 134.2 | 217.8 |
| 133.4 | 217.1 |
| 134.7 | 218.5 |
| 133.7 | 218.9 |
| 132.6 | 219.3 |
| 133.7 | 221 |
| 132.7 | 221.4 |
| 133.6 | 223.2 |
| 134.3 | 223.3 |
| 133.9 | 222.5 |
| 134.3 | 225.2 |
| 131.9 | 227 |
| 133.6 | 226.9 |
| 132.8 | 227.8 |
| 133.8 | 227.5 |
| 132.6 | 227.4 |
| 133.6 | 227.3 |
| 133.1 | 228.3 |
| 132.2 | 228.8 |
| 133.4 | 228.4 |
| 134.2 | 228.4 |
| 132.6 | 228.1 |
| 133.5 | 228.9 |
| 132.5 | 229.6 |
| 134.5 | 229.3 |
| 134.1 | 231 |
| 132.8 | 232.9 |
| 133.1 | 234.4 |
| 133 | 236.7 |
| 133 | 236.6 |
| 134.1 | 239.4 |
| 132.2 | 238.6 |
| 134.6 | 238.2 |
| 133.8 | 237.2 |
| 134 | 239.3 |
| 133.7 | 237.7 |
| 132.7 | 238.3 |
| 132.4 | 239.4 |
| 132.2 | 239.8 |
| 132.9 | 240.7 |
| 134 | 241.2 |
| 132.8 | 244.8 |
| 130.9 | 245 |
| 133 | 242.9 |
| 133.1 | 243.4 |
| 132.5 | 245.4 |
| 131.9 | 248 |
| 132.4 | 247.9 |
| 131.9 | 245.9 |
| 132.3 | 247.8 |
| 132.1 | 247.7 |
| 132 | 245.3 |
| 132.5 | 246.2 |
| 132.1 | 248.8 |
| 131.7 | 249.6 |
| 131.3 | 252.9 |
| 131.4 | 253.5 |
| 131.7 | 251.6 |
| 132.7 | 250.3 |
| 132.3 | 250.8 |
| 132.8 | 252.9 |
| 132 | 254.3 |
| 132.9 | 254.1 |
| 133.2 | 256.5 |
| 132.8 | 258 |
| 132.8 | 258 |
| 131.8 | 259.3 |
| 131.9 | 259.6 |
| 132.8 | 257 |
| 132.5 | 257.8 |
| 131.4 | 260.3 |
| 131.7 | 259.7 |
| 132.1 | 261.2 |
| 130.9 | 262.6 |
| 131.8 | 261.8 |
| 132.1 | 262.4 |
| 132.5 | 263.4 |
| 132.1 | 259.7 |
| 132.1 | 258.9 |
| 130.9 | 261 |
| 131.7 | 263.1 |
| 131 | 261.4 |
| 131.8 | 265.2 |
| 130.8 | 267.3 |
| 131.5 | 267.2 |
| 131.3 | 266.5 |
| 131.8 | 264.7 |
| 132 | 264.9 |
| 132.9 | 265.2 |
| 132.4 | 266.8 |
| 132.2 | 268.1 |
| 130.8 | 268.4 |
| 132.1 | 269.1 |
| 132.4 | 269.1 |
| 131.7 | 271.7 |
| 131.6 | 270.2 |
| 131.9 | 269.3 |
| 130.3 | 271.2 |
| 130.8 | 274.7 |
| 131.4 | 275.4 |
| 131.3 | 272.9 |
| 131.4 | 274.2 |
| 132.3 | 275.1 |
| 130.2 | 274.4 |
| 131.5 | 273.4 |
| 131.8 | 275.8 |
| 131.2 | 278.7 |
| 130.8 | 279.2 |
| 131.2 | 277.3 |
| 131.2 | 275.9 |
| 131.7 | 276.5 |
| 132 | 278 |
| 131.1 | 278.2 |
| 130.6 | 279.6 |
| 131.3 | 281.6 |
| 131.1 | 281 |
| 131.2 | 283.1 |
| 130.8 | 282.3 |
| 132.4 | 281.7 |
| 131 | 280.5 |
| 131.6 | 278.8 |
| 131.9 | 280.4 |
| 131 | 280.9 |
| 130.5 | 281.5 |
| 130.9 | 280.9 |
| 131.5 | 280.2 |
| 130.2 | 280.6 |
| 132.5 | 281 |
| 130.6 | 280 |
| 132 | 281 |
| 131.6 | 283.7 |
| 131.5 | 283.8 |
| 130.7 | 285 |
| 131.5 | 285.4 |
| 131.3 | 285.7 |
| 132.2 | 283.3 |
| 132.2 | 281.8 |
| 131.4 | 281.4 |
| 131 | 283.6 |
| 131.4 | 284.5 |
| 132.2 | 285.8 |
| 131.2 | 285.8 |
| 131.6 | 286.1 |
| 132.5 | 283.9 |
| 131.7 | 284.5 |
| 132.5 | 288.1 |
| 131.5 | 289.5 |
| 131.2 | 287.3 |
| 131.9 | 290.3 |
| 131.8 | 293.5 |
| 131.7 | 293 |
| 131.5 | 291.5 |
| 131.8 | 292 |
| 132.9 | 291.4 |
| 132.4 | 289.8 |
| 132.4 | 291.3 |
| 132.9 | 293.8 |
| 132.3 | 294.3 |
| 131.9 | 293.4 |
| 131.4 | 293.3 |
| 131.5 | 292.1 |
| 131.5 | 292.1 |
| 131.4 | 292.6 |
| 131.5 | 291.4 |
| 129.8 | 292.3 |
| 130.2 | 294 |
| 130.7 | 294.1 |
| 130.5 | 294.5 |
| 131 | 297.9 |
| 130.7 | 297.4 |
| 130.6 | 298 |
| 131.4 | 298.7 |
| 129.9 | 302.8 |
| 130.1 | 301 |
| 130.2 | 298.5 |
| 128.9 | 298.7 |
| 129.5 | 302.1 |
| 129.8 | 301.5 |
| 130.7 | 298.5 |
| 131.3 | 298 |
| 131.2 | 299.2 |
| 130 | 302.2 |
| 130.3 | 300.2 |
| 130.5 | 302.3 |
| 129.6 | 304.6 |
| 131.4 | 304.7 |
| 130 | 302.5 |
| 130.4 | 301.6 |
| 129.7 | 301.5 |
| 130.5 | 303 |
| 129.6 | 301.9 |
| 131.1 | 302.5 |
| 130.7 | 302.2 |
| 130.6 | 303.1 |
| 131.2 | 305.4 |
| 129.2 | 307.8 |
| 130.2 | 308.2 |
| 128.9 | 307.9 |
| 130.1 | 309.3 |
| 129.8 | 306.7 |
| 130.7 | 303.6 |
| 130.8 | 303.1 |
| 130.2 | 306.6 |
| 128.6 | 309.1 |
| 129.4 | 308.8 |
| 129.9 | 307 |
| 128.5 | 310.3 |
| 129.8 | 311.1 |
| 129.3 | 312.8 |
| 130.6 | 311.7 |
| 130.3 | 311.4 |
| 130.3 | 313.2 |
| 129.1 | 312.6 |
| 128.8 | 313.8 |
| 129.1 | 313.2 |
| 129.9 | 312.3 |
| 131.6 | 311.2 |
| 128.1 | 313.2 |
| 130.3 | 313 |
| 129.3 | 314.5 |
| 129.5 | 314.7 |
| 129.9 | 313.3 |
| 128.5 | 313.5 |
| 129.2 | 315.5 |
| 129.1 | 316.7 |
| 129.3 | 315.2 |
| 129.2 | 313.3 |
| 128.8 | 313.9 |
| 127.8 | 313.7 |
| 129.9 | 315.1 |
| 129.2 | 314.1 |
| 128.9 | 316.3 |
| 127.4 | 318.5 |
| 128.7 | 316.1 |
| 129.7 | 318.2 |
| 128.7 | 317.4 |
| 129.1 | 317.7 |
| 128 | 320.1 |
| 128.4 | 319.7 |
| 127.9 | 321.5 |
| 127.5 | 320.4 |
| 128.7 | 320.9 |
| 126.8 | 321.3 |
| 127 | 323.3 |
| 127.4 | 324.4 |
| 127.9 | 320.7 |
| 127.1 | 321.6 |
| 128 | 323.3 |
| 128.8 | 322.4 |
| 128.9 | 322.1 |
| 129.1 | 322.6 |
| 128.2 | 325.9 |
| 130.7 | 325.8 |
| 128.3 | 325.4 |
| 128.6 | 327.4 |
| 128.9 | 327.7 |
| 128.2 | 328 |
| 127 | 328.9 |
| 127.7 | 331.9 |
| 127.4 | 331.6 |
| 129 | 332.5 |
| 128.6 | 338.2 |
| 128.1 | 339.9 |
| 127.9 | 339.3 |
| 127.7 | 344.9 |
| 127.2 | 347 |
| 129.1 | 344.2 |
| 129.2 | 345 |
| 128.7 | 349.8 |
| 129.5 | 353.1 |
| 128.7 | 355.6 |
| 127.8 | 360.8 |
| 127.9 | 364.8 |
| 127.8 | 369.3 |
| 127.4 | 371.4 |
| 128.1 | 373.7 |
| 127.1 | 371.2 |
| 128 | 377.6 |
| 126.5 | 382.5 |
| 128.5 | 385.8 |
| 129.1 | 390.2 |
| 127.8 | 393.9 |
| 128 | 398.3 |
| 127.4 | 400 |
| 126.5 | 403.8 |
| 125.8 | 410.2 |
| 127.3 | 411.5 |
| 127.3 | 410.4 |
| 127.2 | 412.5 |
| 127.3 | 421.5 |
| 126.7 | 420.5 |
| 127.8 | 427.3 |
| 127.5 | 427.1 |
| 126.2 | 430.9 |
| 127.4 | 432.9 |
| 126.4 | 441.7 |
| 127.2 | 446.6 |
| 126.3 | 451.2 |
| 128.2 | 444.4 |
| 127.5 | 445.9 |
| 126.7 | 448.6 |
| 127.7 | 452.9 |
| 127.4 | 460.7 |
| 127.5 | 457.4 |
| 127.2 | 461.1 |
| 126.9 | 459.1 |
| 128 | 461.4 |
| 127 | 464.7 |
| 127.1 | 461.9 |
| 127.2 | 469.6 |
| 127.8 | 472.4 |
| 127.5 | 480.1 |
| 127 | 481.8 |
| 127.1 | 480.6 |
| 126.5 | 485.9 |
| 128.1 | 481.7 |
| 128 | 484.2 |
| 127 | 485.6 |
| 127.4 | 489.4 |
| 127.3 | 483.3 |
| 127.6 | 487.5 |
| 127.3 | 488.9 |
| 127.7 | 498.6 |
| 126.6 | 501.6 |
| 125.8 | 499.7 |
| 127.5 | 500.8 |
| 126.5 | 502.1 |
| 128.8 | 511.5 |
| 127.4 | 518.4 |
| 126.5 | 521.7 |
| 126.9 | 518.4 |
| 128.6 | 519.5 |
| 128.8 | 522.5 |
| 127.8 | 519.1 |
| 126.6 | 524.6 |
| 127.5 | 522.6 |
| 127.2 | 524.5 |
| 128.7 | 526.3 |
| 127.6 | 528.3 |
| 127.1 | 526.1 |
| 127.2 | 529 |
| 128.1 | 529.7 |
| 127.5 | 536.4 |
| 127.3 | 535.6 |
| 128.6 | 536.8 |
| 127.9 | 538.7 |
| 127.2 | 545.4 |
| 127.1 | 543.9 |
| 127 | 542.3 |
| 127.9 | 535.5 |
| 126.8 | 542.5 |
| 126.2 | 544.9 |
| 126.8 | 540.9 |
| 127.2 | 550.4 |
| 126.5 | 552.9 |
| 126.2 | 555.1 |
| 126.8 | 553.9 |
| 126 | 558.1 |
| 127.2 | 555 |
| 128.3 | 552 |
| 129.1 | 552.5 |
| 127.5 | 558.7 |
| 128.8 | 564.1 |
| 128.5 | 570.4 |
| 126.9 | 575 |
| 128.3 | 582.4 |
| 125.8 | 589.9 |
| 126 | 589.3 |
| 126.9 | 586.7 |
| 127.1 | 584.3 |
| 126.8 | 587.1 |
| 126.8 | 587 |
| 125.7 | 588 |
| 127.1 | 594.2 |
| 127.7 | 598.6 |
| 126.2 | 596.6 |
| 127.3 | 605 |
| 127.2 | 607.6 |
| 127.2 | 604 |
| 126.6 | 601 |
| 127.7 | 602.6 |
| 127.6 | 609.1 |
| 127.2 | 611.3 |
| 127.1 | 611.5 |
| 127.3 | 616.1 |
| 126 | 617.3 |
| 127 | 610.1 |
| 127.9 | 620.7 |
| 126.8 | 613.5 |
| 127.5 | 617.3 |
| 127.5 | 616.5 |
| 127.9 | 621.1 |
| 126 | 629.8 |
| 127.5 | 629.8 |
| 126.9 | 637 |
| 127.1 | 645.5 |
| 126.8 | 644 |
| 127.9 | 639.3 |
| 129.9 | 639.9 |
| 127.3 | 641.3 |
| 126.9 | 644 |
| 126.5 | 646.9 |
| 126.9 | 651.7 |
| 127.3 | 655.2 |
| 127.5 | 655.8 |
| 127.5 | 658.9 |
| 125.5 | 655.4 |
| 127.2 | 652.2 |
| 126.3 | 651 |
| 126.8 | 657.6 |
| 126.6 | 664.4 |
| 125.6 | 654.9 |
| 127.4 | 657.3 |
| 128.2 | 656.5 |
| 128 | 667.1 |
| 125.6 | 664.4 |
| 126.8 | 666.3 |
| 125.2 | 663.5 |
| 125.7 | 664.2 |
| 126.6 | 666 |
| 126.8 | 665.9 |
| 126.1 | 665.4 |
| 126.5 | 670.2 |
| 126.6 | 674.6 |
| 125.2 | 678.9 |
| 126.7 | 669.8 |
| 126.8 | 674.5 |
| 126.6 | 676.3 |
| 127.5 | 667.3 |
| 128.2 | 674.7 |
| 128.9 | 670.7 |
| 127 | 678.9 |
| 126.1 | 682.6 |
| 125.9 | 690.6 |
| 126.1 | 694.2 |
| 126.3 | 696.4 |
| 125.8 | 691.3 |
| 126.8 | 697.1 |
| 126.5 | 693.4 |
| 128.1 | 690.7 |
| 126.5 | 698.6 |
| 126.5 | 708.3 |
| 126.8 | 709.6 |
| 128.1 | 712.3 |
| 127.9 | 717 |
| 126.7 | 709 |
| 126.7 | 717.2 |
| 126.2 | 728.3 |
| 126 | 724.6 |
| 126.2 | 729.1 |
| 127.8 | 734.1 |
| 127.3 | 737.2 |
| 127.4 | 740.2 |
| 126.1 | 747.2 |
| 126.2 | 744.7 |
| 126.7 | 748.8 |
| 128.2 | 746.1 |
| 127.5 | 744.8 |
| 127 | 743.7 |
| 127.8 | 744.9 |
| 127.7 | 750.2 |
| 128.6 | 745.8 |
| 128.4 | 738.3 |
| 127.6 | 741.1 |
| 127.5 | 747.9 |
| 128.2 | 748 |
| 127.3 | 742 |
| 128.2 | 742.2 |
| 127.3 | 746.9 |
| 127.1 | 743.4 |
| 127.5 | 749.4 |
| 128.5 | 756.6 |
| 126.7 | 756.4 |
| 127.6 | 754.3 |
| 127.2 | 758.1 |
| 125.9 | 761.2 |
| 126 | 763.2 |
| 125.8 | 760.4 |
| 127 | 757 |
| 127.1 | 764 |
| 127.9 | 769.2 |
| 126.7 | 765.7 |
| 127.3 | 771.4 |
| 128.2 | 772.3 |
| 126.8 | 773 |
| 126.4 | 768.5 |
| 127.1 | 769.2 |
| 126.4 | 778.6 |
| 127.4 | 781 |
| 125.6 | 786.9 |
| 126.1 | 789.6 |
| 125.8 | 789.9 |
| 126.7 | 789.6 |
| 127.5 | 791.1 |
| 126.8 | 789.8 |
| 125.1 | 788.3 |
| 127.7 | 793.5 |
| 127.1 | 790.6 |
| 127.4 | 795.4 |
| 126.2 | 799.4 |
| 127.5 | 801.2 |
| 127 | 804 |
| 127.3 | 799.4 |
| 127.3 | 807.6 |
| 128.2 | 803.4 |
| 127.1 | 815.2 |
| 126.3 | 814.6 |
| 128 | 818.6 |
| 127.3 | 817.6 |
| 126.9 | 825 |
| 128.1 | 827.5 |
| 129.5 | 834.1 |
| 128.7 | 835.1 |
| 127.6 | 842.9 |
| 125.7 | 842.7 |
| 128.2 | 840.9 |
| 127.1 | 841.8 |
| 127.6 | 845.2 |
| 127.1 | 845.2 |
| 126.6 | 850.8 |
| 127.7 | 855.9 |
| 126.9 | 855.8 |
| 127.1 | 857.1 |
| 127.7 | 857.7 |
| 127.6 | 858.9 |
| 125.8 | 858.3 |
| 127.2 | 862.3 |
| 128.1 | 863.1 |
| 127.6 | 866.1 |
| 127 | 859.7 |
| 128.6 | 859.6 |
| 128.3 | 857.6 |
| 126.8 | 857.8 |
| 127.9 | 852.6 |
| 127 | 854 |
| 127.4 | 851 |
| 128.3 | 851.8 |
| 128.5 | 853.1 |
| 127.5 | 851.5 |
| 127.3 | 855.6 |
| 128.2 | 861.9 |
| 128.5 | 859.9 |
| 127.7 | 853.3 |
| 128.7 | 854.5 |
| 127.1 | 862.1 |
| 127.5 | 862.6 |
| 127.5 | 863.9 |
| 128 | 862.5 |
| 127.4 | 859.3 |
| 126.1 | 865.1 |
| 128.6 | 858.6 |
| 126.9 | 869.3 |
| 127.7 | 863.7 |
| 127.4 | 858.5 |
| 128.1 | 860.5 |
| 126.6 | 858.2 |
| 128.2 | 850.4 |
| 129.4 | 852.1 |
| 128.3 | 850.1 |
| 126.8 | 859.7 |
| 128.3 | 860.1 |
| 126.3 | 869.6 |
| 128.1 | 868.3 |
| 127.2 | 875.7 |
| 127.5 | 873.6 |
| 128.1 | 882.4 |
| 126.9 | 887.3 |
| 127.6 | 893.3 |
| 126.5 | 892.2 |
| 128.1 | 889.6 |
| 128 | 891.2 |
| 127 | 891 |
| 127.4 | 894.4 |
| 127.6 | 890.4 |
| 128 | 894.9 |
| 127.4 | 906.1 |
| 127.6 | 911.6 |
| 128.5 | 908.5 |
| 128.7 | 899.9 |
| 128.7 | 902.6 |
| 127.7 | 908.5 |
| 127 | 903.2 |
| 128.2 | 892 |
| 128.9 | 898.9 |
| 127.6 | 899.2 |
| 128 | 902.1 |
| 128.6 | 901.1 |
| 125.7 | 904.2 |
| 127.5 | 901.9 |
| 127.2 | 912.2 |
| 127.6 | 915.2 |
| 127.3 | 917.7 |
| 128.3 | 914.3 |
| 129.2 | 910.9 |
| 129 | 911.7 |
| 127.8 | 914.2 |
| 128.7 | 922.4 |
| 128.4 | 923.3 |
| 129.3 | 918.8 |
| 126.7 | 919.3 |
| 127.8 | 924.9 |
| 125.8 | 931.8 |
| 127.2 | 923.5 |
| 128.6 | 934.5 |
| 127.2 | 940.4 |
| 127 | 941.4 |
| 128.2 | 950.3 |
| 126.8 | 946.5 |
| 127.6 | 949.1 |
| 127.6 | 944.2 |
| 127.3 | 943.6 |
| 128.6 | 947.2 |
| 127.6 | 949.1 |
| 128.3 | 948.8 |
| 127.5 | 948 |
| 127.7 | 948.9 |
| 129.5 | 957.1 |
| 127.7 | 961.4 |
| 128.8 | 961.9 |
| 128.9 | 960 |
| 129.7 | 968.1 |
| 129 | 961 |
| 127.5 | 963.6 |
| 128 | 962.3 |
| 128.4 | 964.4 |
| 127.4 | 964.8 |
| 127.4 | 973 |
| 127 | 976.9 |
| 128.7 | 976.1 |
| 127.8 | 980.4 |
| 127.9 | 979.7 |
| 127.3 | 973.6 |
| 127.7 | 969.3 |
| 127.6 | 974.6 |
| 129.7 | 980.9 |
| 128.9 | 993.2 |
| 128.4 | 994.9 |
| 128.8 | 995.2 |
| 128.3 | 1001 |
| 129.1 | 1011 |
| 128.8 | 999.8 |
| 126.2 | 1007 |
| 127.4 | 1010 |
| 129.2 | 1001 |
| 128.2 | 1010 |
| 128.2 | 1016 |
| 129.3 | 1013 |
| 128.9 | 1029 |
| 128.3 | 1024 |
| 129 | 1033 |
| 128.9 | 1034 |
| 129.8 | 1038 |
| 127.4 | 1034 |
| 128.5 | 1030 |
| 128.4 | 1036 |
| 130.2 | 1040 |
| 127.9 | 1044 |
| 127.9 | 1049 |
| 127.1 | 1050 |
| 128.1 | 1059 |
| 128.1 | 1056 |
| 128.8 | 1051 |
| 129.4 | 1046 |
| 129.1 | 1045 |
| 126.8 | 1042 |
| 127 | 1046 |
| 128 | 1057 |
| 129.8 | 1063 |
| 128.6 | 1068 |
| 128.3 | 1065 |
| 128.2 | 1057 |
| 129.4 | 1058 |
| 130.1 | 1061 |
| 128.5 | 1072 |
| 128.2 | 1075 |
| 130.2 | 1073 |
| 127.7 | 1075 |
| 128.6 | 1085 |
| 127.6 | 1093 |
| 128.4 | 1095 |
| 129.2 | 1101 |
| 128.4 | 1094 |
| 128.6 | 1090 |
| 129 | 1097 |
| 127.7 | 1097 |
| 129.7 | 1097 |
| 129.7 | 1105 |
| 128.6 | 1112 |
| 129.2 | 1114 |
| 126.6 | 1113 |
| 128.3 | 1117 |
| 127.5 | 1123 |
| 129.7 | 1118 |
| 129 | 1120 |
| 130.3 | 1115 |
| 128 | 1122 |
| 129.3 | 1121 |
| 129.3 | 1132 |
| 129.9 | 1118 |
| 127.9 | 1120 |
| 127.6 | 1111 |
| 127.9 | 1120 |
| 128.6 | 1119 |
| 127.7 | 1124 |
| 130.2 | 1128 |
| 129.6 | 1129 |
| 128.5 | 1123 |
| 129.5 | 1122 |
| 127.8 | 1122 |
| 127.9 | 1130 |
| 129.1 | 1120 |
| 127 | 1131 |
| 127.5 | 1132 |
| 127.9 | 1130 |
| 128.3 | 1129 |
| 127.5 | 1130 |
| 128.5 | 1131 |
| 128.1 | 1134 |
| 129.3 | 1141 |
| 128.8 | 1147 |
| 129.4 | 1147 |
| 128.8 | 1143 |
| 129.7 | 1149 |
| 127.9 | 1151 |
| 128.5 | 1148 |
| 127.6 | 1143 |
| 128.5 | 1136 |
| 127.2 | 1134 |
| 127.9 | 1138 |
| 127.2 | 1155 |
| 128.1 | 1147 |
| 128 | 1147 |
| 128.4 | 1147 |
| 129.2 | 1155 |
| 128.1 | 1154 |
| 128 | 1150 |
| 128.8 | 1158 |
| 128.8 | 1162 |
| 129.7 | 1169 |
| 128.5 | 1170 |
| 130.1 | 1164 |
| 130.8 | 1176 |
| 128.1 | 1175 |
| 129.1 | 1180 |
| 129 | 1176 |
| 128.7 | 1185 |
| 129.9 | 1189 |
| 129.5 | 1182 |
| 129.4 | 1190 |
| 128.3 | 1191 |
| 129.4 | 1197 |
| 127.9 | 1195 |
| 129 | 1206 |
| 129.4 | 1202 |
| 130 | 1211 |
| 128.9 | 1212 |
| 129.3 | 1198 |
| 128.3 | 1207 |
| 129.4 | 1196 |
| 128 | 1206 |
| 129.1 | 1204 |
| 129.5 | 1197 |
| 129.7 | 1197 |
| 131.5 | 1200 |
| 127.5 | 1210 |
| 129.1 | 1210 |
| 129.1 | 1209 |
| 128.8 | 1208 |
| 127.2 | 1205 |
| 128.6 | 1207 |
| 128.1 | 1221 |
| 129.4 | 1224 |
| 127.9 | 1233 |
| 129.8 | 1229 |
| 129.5 | 1225 |
| 129 | 1220 |
| 127.9 | 1226 |
| 128.2 | 1224 |
| 128.8 | 1218 |
| 128.7 | 1224 |
| 128.2 | 1222 |
| 129.2 | 1222 |
| 128.8 | 1229 |
| 128.2 | 1238 |
| 127.4 | 1235 |
| 128.2 | 1248 |
| 128.5 | 1247 |
| 128.5 | 1248 |
| 128.7 | 1246 |
| 128.8 | 1245 |
| 128.1 | 1262 |
| 129.2 | 1259 |
| 128.3 | 1254 |
| 128.1 | 1249 |
| 129.2 | 1254 |
| 128.1 | 1265 |
| 127.8 | 1261 |
| 128.3 | 1260 |
| 128.2 | 1258 |
| 128.4 | 1263 |
| 129.4 | 1264 |
| 128.1 | 1266 |
| 128.7 | 1255 |
| 128.3 | 1255 |
| 127.9 | 1252 |
| 127.7 | 1255 |
| 129.5 | 1246 |
| 127.9 | 1244 |
| 129.4 | 1250 |
| 127.1 | 1246 |
| 127.3 | 1244 |
| 128.3 | 1247 |
| 128.5 | 1251 |
| 128.4 | 1261 |
| 129.7 | 1253 |
| 129.9 | 1268 |
| 128.5 | 1278 |
| 128.9 | 1287 |
| 130 | 1281 |
| 128.6 | 1269 |
| 128.6 | 1274 |
| 128.2 | 1274 |
| 128.1 | 1289 |
| 128.2 | 1294 |
| 129.7 | 1296 |
| 128.2 | 1303 |
| 127.4 | 1314 |
| 126.8 | 1312 |
| 128.4 | 1312 |
| 127.4 | 1312 |
| 127.4 | 1307 |
| 126.3 | 1313 |
| 128.3 | 1320 |
| 128.5 | 1318 |
| 128.9 | 1314 |
| 130 | 1317 |
| 129.5 | 1313 |
| 129.2 | 1322 |
| 127.1 | 1331 |
| 129.2 | 1338 |
| 128.1 | 1334 |
| 129 | 1333 |
| 129.6 | 1334 |
| 129.4 | 1341 |
| 128.6 | 1337 |
| 128.5 | 1350 |
| 128.6 | 1347 |
| 128.9 | 1343 |
| 128.6 | 1336 |
| 128.1 | 1347 |
| 127.1 | 1360 |
| 128.7 | 1356 |
| 128.3 | 1356 |
| 130.3 | 1355 |
| 130.9 | 1354 |
| 128.9 | 1363 |
| 129.1 | 1352 |
| 129.3 | 1349 |
| 129.4 | 1353 |
| 127.6 | 1358 |
| 128.4 | 1346 |
| 127.3 | 1348 |
| 128.8 | 1360 |
| 128.5 | 1366 |
| 129.7 | 1370 |
| 129.5 | 1367 |
| 128.4 | 1361 |
| 131.3 | 1357 |
| 130.6 | 1355 |
| 129.7 | 1355 |
| 128.7 | 1358 |
| 127.8 | 1354 |
| 126.9 | 1366 |
| 128.2 | 1363 |
| 129.2 | 1363 |
| 129.6 | 1363 |
| 129.4 | 1370 |
| 129.6 | 1375 |
| 130.4 | 1373 |
| 129.7 | 1380 |
| 128.8 | 1381 |
| 128.8 | 1376 |
| 129.6 | 1368 |
| 128.2 | 1378 |
| 128.5 | 1376 |
| 128.7 | 1376 |
| 128.7 | 1375 |
| 128.8 | 1389 |
| 127.8 | 1389 |
| 128.7 | 1377 |
| 127.7 | 1379 |
| 127.8 | 1371 |
| 128.2 | 1380 |
| 128.6 | 1371 |
| 128 | 1380 |
| 130.3 | 1394 |
| 129 | 1390 |
| 129.4 | 1389 |
| 129 | 1395 |
| 127.3 | 1386 |
| 129.2 | 1399 |
| 129 | 1403 |
| 129.9 | 1391 |
| 128.4 | 1402 |
| 130 | 1405 |
| 130.2 | 1408 |
| 129.6 | 1402 |
| 128.3 | 1420 |
| 130 | 1421 |
| 129 | 1415 |
| 127.7 | 1415 |
| 128 | 1427 |
| 129 | 1434 |
| 128 | 1436 |
| 128.8 | 1434 |
| 129.1 | 1436 |
| 129.3 | 1438 |
| 129.1 | 1446 |
| 129.4 | 1445 |
| 129.4 | 1444 |
| 128.8 | 1457 |
| 129 | 1459 |
| 129.6 | 1460 |
| 129.1 | 1466 |
| 128.2 | 1471 |
| 128.4 | 1472 |
| 128.4 | 1462 |
| 128.7 | 1469 |
| 131 | 1473 |
| 126.5 | 1476 |
| 127.2 | 1475 |
| 130.4 | 1474 |
| 129.8 | 1473 |
| 128.3 | 1479 |
| 128.2 | 1466 |
| 130.3 | 1458 |
| 129.6 | 1453 |
| 129.1 | 1454 |
| 129.5 | 1454 |
| 126.9 | 1451 |
| 129.2 | 1452 |
| 129.7 | 1443 |
| 130.1 | 1438 |
| 130 | 1435 |
| 129 | 1435 |
| 130 | 1458 |
| 128.9 | 1458 |
| 127.3 | 1473 |
| 130.1 | 1471 |
| 129.4 | 1482 |
| 129.3 | 1490 |
| 130.4 | 1493 |
| 130.5 | 1481 |
| 129.4 | 1485 |
| 128.8 | 1489 |
| 130.1 | 1489 |
| 129.6 | 1483 |
| 129.4 | 1492 |
| 130 | 1500 |
| 128.7 | 1504 |
| 129.8 | 1500 |
| 129.1 | 1500 |
| 129.5 | 1505 |
| 129.4 | 1491 |
| 128.7 | 1483 |
| 129 | 1485 |
| 129.4 | 1489 |
| 131.3 | 1480 |
| 129.9 | 1486 |
| 130.2 | 1493 |
| 129.3 | 1499 |
| 128.7 | 1495 |
| 127.7 | 1503 |
| 128.7 | 1509 |
| 127.4 | 1508 |
| 129.3 | 1506 |
| 128.2 | 1500 |
| 129 | 1505 |
| 128.4 | 1519 |
| 129.8 | 1509 |
| 128.9 | 1519 |
| 129.6 | 1516 |
| 128.7 | 1517 |
| 129.6 | 1513 |
| 129.6 | 1524 |
| 128.8 | 1529 |
| 130.2 | 1529 |
| 128.9 | 1520 |
| 130.1 | 1539 |
| 128.8 | 1537 |
| 130.4 | 1541 |
| 129.6 | 1543 |
| 128.3 | 1526 |
| 129.4 | 1529 |
| 129.7 | 1545 |
| 129.1 | 1539 |
| 130.4 | 1552 |
| 130.4 | 1545 |
| 131.4 | 1545 |
| 130.7 | 1549 |
| 130.5 | 1552 |
| 129.5 | 1552 |
| 128.9 | 1549 |
| 130 | 1548 |
| 129.5 | 1553 |
| 129.2 | 1560 |
| 128.5 | 1552 |
| 128.1 | 1554 |
| 130.8 | 1567 |
| 130.9 | 1557 |
| 131.4 | 1565 |
| 129.1 | 1576 |
| 129.2 | 1576 |
| 129.4 | 1566 |
| 129.2 | 1559 |
| 129.9 | 1559 |
| 130.1 | 1552 |
| 130.1 | 1556 |
| 129.9 | 1546 |
| 130.8 | 1548 |
| 129.2 | 1552 |
| 129.9 | 1551 |
| 132.3 | 1551 |
| 133 | 1551 |
| 131.9 | 1553 |
| 132.8 | 1555 |
| 132.8 | 1553 |
| 132.6 | 1561 |
| 132.7 | 1562 |
| 132.2 | 1565 |
| 132.4 | 1567 |
| 133.3 | 1567 |
| 132.1 | 1570 |
| 133 | 1568 |
| 131.5 | 1565 |
| 132 | 1568 |
| 133 | 1567 |
| 132.6 | 1563 |
| 133.8 | 1565 |
| 133.4 | 1566 |
| 133.7 | 1567 |
| 133.2 | 1570 |
| 133.3 | 1567 |
| 133.2 | 1570 |
| 133 | 1574 |
| 133.4 | 1574 |
| 132.7 | 1579 |
| 133.4 | 1586 |
| 132.9 | 1587 |
| 132.4 | 1589 |
| 132.6 | 1591 |
| 132.3 | 1598 |
| 133.5 | 1604 |
| 133.1 | 1610 |
| 133.6 | 1612 |
| 133.9 | 1605 |
| 134.6 | 1604 |
| 134 | 1606 |
| 134.2 | 1605 |
| 134.3 | 1606 |
| 133.9 | 1605 |
| 133.6 | 1603 |
| 132.7 | 1600 |
| 134.1 | 1594 |
| 134.5 | 1594 |
| 134.7 | 1587 |
| 134.2 | 1593 |
| 133.8 | 1595 |
| 134.3 | 1593 |
| 134.1 | 1595 |
| 134.5 | 1589 |
| 134.3 | 1593 |
| 133.6 | 1594 |
| 133.5 | 1592 |
| 134.1 | 1597 |
| 133.7 | 1601 |
| 133.5 | 1605 |
| 133.6 | 1609 |
| 134 | 1611 |
| 134.4 | 1608 |
| 133.9 | 1611 |
| 133.9 | 1611 |
| 134.4 | 1613 |
| 133.4 | 1612 |
| 133.4 | 1611 |
| 133.8 | 1614 |
| 134.8 | 1616 |
| 134.2 | 1620 |
| 132.6 | 1620 |
| 133.2 | 1619 |
| 134.1 | 1620 |
| 134.3 | 1619 |
| 134.9 | 1621 |
| 133.2 | 1622 |
| 134.1 | 1626 |
| 134.7 | 1624 |
| 135 | 1623 |
| 134.6 | 1623 |
| 133.7 | 1625 |
| 133.4 | 1628 |
| 134.6 | 1628 |
| 134.3 | 1627 |
| 134 | 1628 |
| 133.4 | 1624 |
| 133.3 | 1627 |
| 133.8 | 1629 |
| 133.6 | 1630 |
| 133.3 | 1630 |
| 133.6 | 1633 |
| 133.5 | 1632 |
| 133.4 | 1634 |
| 134.5 | 1637 |
| 133 | 1637 |
| 134.5 | 1634 |
| 133.4 | 1634 |
| 133.5 | 1636 |
| 132.5 | 1640 |
| 132.8 | 1645 |
| 132.6 | 1646 |
| 133 | 1645 |
| 133.3 | 1643 |
| 133.4 | 1641 |
| 132.6 | 1641 |
| 133.3 | 1644 |
| 133.1 | 1645 |
| 134.4 | 1647 |
| 133.7 | 1649 |
| 132.8 | 1651 |
| 133 | 1657 |
| 133.4 | 1651 |
| 133.4 | 1647 |
| 132.8 | 1651 |
| 133.1 | 1646 |
| 133 | 1644 |
| 133.2 | 1645 |
| 133.2 | 1644 |
| 133.2 | 1645 |
| 132.6 | 1643 |
| 132.8 | 1643 |
| 133.3 | 1648 |
| 132.6 | 1648 |
| 133.9 | 1649 |
| 133.9 | 1651 |
| 133.1 | 1648 |
| 132.7 | 1647 |
| 132.8 | 1652 |
| 132.9 | 1650 |
| 132.7 | 1646 |
| 132.8 | 1643 |
| 133.5 | 1643 |
| 132.4 | 1646 |
| 132.7 | 1645 |
| 132.7 | 1642 |
| 133 | 1646 |
| 132.8 | 1648 |
| 132.8 | 1646 |
| 132.9 | 1655 |
| 133.1 | 1656 |
| 133.1 | 1657 |
| 133.7 | 1654 |
| 133.4 | 1655 |
| 133 | 1651 |
| 132.8 | 1653 |
| 132.9 | 1653 |
| 132.5 | 1652 |
| 133.8 | 1653 |
| 133.2 | 1650 |
| 133.2 | 1648 |
| 133.3 | 1649 |
| 133.1 | 1654 |
| 133.1 | 1659 |
| 133.4 | 1654 |
| 133.1 | 1656 |
| 132.5 | 1653 |
| 132.6 | 1650 |
| 133.2 | 1649 |
| 133.1 | 1657 |
| 133.7 | 1655 |
| 132.9 | 1657 |
| 132.8 | 1655 |
| 132.7 | 1656 |
| 133.4 | 1658 |
| 133.6 | 1661 |
| 133.3 | 1660 |
| 133.5 | 1656 |
| 132.8 | 1656 |
| 133 | 1656 |
| 133.4 | 1658 |
| 132.8 | 1656 |
| 132.8 | 1659 |
| 133.4 | 1660 |
| 133.2 | 1661 |
| 133.7 | 1663 |
| 133 | 1665 |
| 132.7 | 1666 |
| 132.5 | 1671 |
| 132.8 | 1669 |
| 132.8 | 1663 |
| 132.8 | 1664 |
| 132.8 | 1665 |
| 133.2 | 1663 |
| 132.6 | 1662 |
| 132.3 | 1668 |
| 132.6 | 1666 |
| 133 | 1675 |
| 133.2 | 1677 |
| 133.1 | 1679 |
| 132.4 | 1676 |
| 132.9 | 1674 |
| 132.9 | 1672 |
| 133.1 | 1674 |
| 132.7 | 1671 |
| 133.1 | 1670 |
| 132.7 | 1670 |
| 132.8 | 1671 |
| 133.2 | 1670 |
| 133.3 | 1670 |
| 132.8 | 1674 |
| 132.6 | 1671 |
| 132.9 | 1673 |
| 132.9 | 1669 |
| 132.8 | 1673 |
| 132.5 | 1672 |
| 132.2 | 1673 |
| 132.6 | 1674 |
| 132.3 | 1674 |
| 132.8 | 1674 |
| 132.8 | 1671 |
| 132.8 | 1674 |
| 132.7 | 1680 |
| 132.9 | 1683 |
| 132.6 | 1683 |
| 132.5 | 1682 |
| 132.8 | 1680 |
| 132.6 | 1674 |
| 133.1 | 1678 |
| 132.4 | 1675 |
| 133.3 | 1684 |
| 133.6 | 1685 |
| 132.8 | 1686 |
| 132.8 | 1691 |
| 133.2 | 1691 |
| 132.8 | 1692 |
| 132.3 | 1693 |
| 133.3 | 1689 |
| 134 | 1685 |
| 132.9 | 1683 |
| 133.8 | 1683 |
| 133.3 | 1685 |
| 132.9 | 1687 |
| 133.4 | 1687 |
| 133.4 | 1687 |
| 133 | 1685 |
| 132.3 | 1683 |
| 133 | 1684 |
| 132.9 | 1682 |
| 132.9 | 1686 |
| 132.6 | 1685 |
| 132.5 | 1688 |
| 132.5 | 1689 |
| 132.4 | 1692 |
| 132.7 | 1694 |
| 132.5 | 1698 |
| 132.8 | 1699 |
| 132.8 | 1693 |
| 133.2 | 1695 |
| 133.3 | 1701 |
| 133.3 | 1699 |
| 132.9 | 1699 |
| 132.6 | 1696 |
| 132.8 | 1690 |
| 132.7 | 1695 |
| 133.4 | 1695 |
| 133.4 | 1693 |
| 133.6 | 1691 |
| 133.5 | 1690 |
| 133.7 | 1696 |
| 133.7 | 1700 |
| 133.1 | 1700 |
| 132.5 | 1703 |
| 132.5 | 1700 |
| 133.2 | 1696 |
| 132.6 | 1694 |
| 132.6 | 1694 |
| 132.5 | 1702 |
| 132.3 | 1700 |
| 132 | 1702 |
| 132.2 | 1705 |
| 132.6 | 1707 |
| 132.6 | 1710 |
| 133.3 | 1713 |
| 132.6 | 1716 |
| 132.5 | 1718 |
| 132.6 | 1712 |
| 132.9 | 1716 |
| 132.4 | 1718 |
| 132.7 | 1723 |
| 132.9 | 1720 |
| 132.5 | 1716 |
| 132 | 1718 |
| 132.3 | 1717 |
| 133.3 | 1718 |
| 132.5 | 1717 |
| 132.2 | 1721 |
| 132.7 | 1720 |
| 133.4 | 1724 |
| 132.8 | 1731 |
| 133.4 | 1730 |
| 132.9 | 1733 |
| 132.5 | 1737 |
| 131.9 | 1736 |
| 133.4 | 1742 |
| 133 | 1747 |
| 132.4 | 1749 |
| 132.6 | 1748 |
| 132.6 | 1753 |
| 133.2 | 1749 |
| 133.1 | 1751 |
| 132.6 | 1755 |
| 133.5 | 1753 |
| 133.2 | 1755 |
| 133.4 | 1756 |
| 133.2 | 1754 |
| 133.1 | 1750 |
| 133.4 | 1745 |
| 133.2 | 1745 |
| 133.4 | 1750 |
| 133 | 1751 |
| 133 | 1753 |
| 132.4 | 1750 |
| 132.8 | 1748 |
| 132.5 | 1748 |
| 132.8 | 1750 |
| 132.2 | 1755 |
| 132.7 | 1755 |
| 132.6 | 1752 |
| 132.6 | 1752 |
| 133.1 | 1754 |
| 132.8 | 1754 |
| 132.9 | 1752 |
| 132.8 | 1752 |
| 133.3 | 1753 |
| 133.5 | 1754 |
| 133.5 | 1757 |
| 132.9 | 1755 |
| 132 | 1751 |
| 133.3 | 1752 |
| 133.2 | 1749 |
| 133 | 1753 |
| 132.6 | 1749 |
| 132.5 | 1745 |
| 132.9 | 1749 |
| 133.5 | 1751 |
| 133.2 | 1753 |
| 133 | 1749 |
| 132.4 | 1748 |
| 133.5 | 1749 |
| 133.4 | 1751 |
| 132.8 | 1750 |
| 132.8 | 1751 |
| 132.8 | 1756 |
| 132.8 | 1752 |
| 133.8 | 1747 |
| 133.2 | 1746 |
| 133.2 | 1746 |
| 133.4 | 1747 |
| 133.3 | 1750 |
| 133.5 | 1751 |
| 133.1 | 1748 |
| 132.7 | 1756 |
| 133.1 | 1760 |
| 132.9 | 1760 |
| 132.7 | 1763 |
| 133.4 | 1764 |
| 132.7 | 1760 |
| 132.8 | 1755 |
| 132.3 | 1760 |
| 132.5 | 1751 |
| 132.4 | 1752 |
| 132.8 | 1747 |
| 133 | 1747 |
| 132.5 | 1752 |
| 132.8 | 1753 |
| 132.5 | 1751 |
| 132.9 | 1747 |
| 133 | 1749 |
| 132.6 | 1756 |
| 132.8 | 1755 |
| 132.9 | 1752 |
| 133.3 | 1753 |
| 132.6 | 1755 |
| 132.9 | 1753 |
| 132.9 | 1755 |
| 132.4 | 1758 |
| 132.3 | 1751 |
| 132.8 | 1757 |
| 132.9 | 1759 |
| 132.8 | 1759 |
| 132.1 | 1760 |
| 131.7 | 1759 |
| 132.5 | 1755 |
| 132.8 | 1758 |
| 132.9 | 1760 |
| 132.1 | 1757 |
| 132.5 | 1755 |
| 132.6 | 1748 |
| 133.1 | 1747 |
| 132.5 | 1749 |
| 132.5 | 1750 |
| 132.3 | 1751 |
| 133.4 | 1756 |
| 132.7 | 1750 |
| 132.4 | 1756 |
| 132 | 1758 |
| 132.9 | 1760 |
| 132.4 | 1756 |
| 132.9 | 1754 |
| 132.8 | 1756 |
| 133 | 1754 |
| 132.6 | 1761 |
| 132.8 | 1763 |
| 132.8 | 1767 |
| 132.9 | 1778 |
| 132.9 | 1775 |
| 133.3 | 1790 |
| 132.6 | 1782 |
| 132.1 | 1784 |
| 133.2 | 1794 |
| 133 | 1805 |
| 133.4 | 1809 |
| 133 | 1803 |
| 132.9 | 1806 |
| 133.3 | 1806 |
| 132.2 | 1800 |
| 132 | 1804 |
| 132.8 | 1819 |
| 132.7 | 1806 |
| 132.5 | 1806 |
| 132.3 | 1806 |
| 132.6 | 1824 |
| 132.2 | 1831 |
| 133.1 | 1824 |
| 132.7 | 1836 |
| 132.6 | 1843 |
| 132.4 | 1837 |
| 132.6 | 1883 |
| 132.3 | 1903 |
| 132.2 | 1879 |
| 133 | 1884 |
| 132.7 | 1867 |
| 132.9 | 1883 |
| 133 | 1895 |
| 133.1 | 1914 |
| 132.6 | 1911 |
| 132.4 | 1923 |
| 133.4 | 1917 |
| 133.4 | 1908 |
| 133.6 | 1909 |
| 133.3 | 1900 |
| 133.5 | 1909 |
| 133.6 | 1897 |
| 132.8 | 1909 |
| 133.4 | 1906 |
| 133.2 | 1916 |
| 132.6 | 1920 |
| 132.8 | 1931 |
| 132.2 | 1939 |
| 132.3 | 1951 |
| 132.6 | 1954 |
| 133.1 | 1961 |
| 133.7 | 1962 |
| 133.2 | 1970 |
| 133.2 | 1973 |
| 133 | 1978 |
| 133.3 | 1991 |
| 132.8 | 1983 |
| 133.1 | 1971 |
| 132.5 | 1985 |
| 132.7 | 1978 |
| 132.4 | 1983 |
| 132.1 | 1979 |
| 132.2 | 1991 |
| 133.1 | 1990 |
| 132.3 | 1999 |
| 133.6 | 1999 |
| 133.2 | 2008 |
| 133.2 | 2024 |
| 132.4 | 2020 |
| 133.2 | 2027 |
| 133.5 | 2017 |
| 133.6 | 2018 |
| 132.4 | 2034 |
| 132.3 | 2044 |
| 132.9 | 2063 |
| 132.8 | 2061 |
| 132.8 | 2082 |
| 133.2 | 2076 |
| 132.9 | 2092 |
| 132.7 | 2083 |
| 133.2 | 2081 |
| 133.4 | 2105 |
| 132.9 | 2111 |
| 132.9 | 2102 |
| 132.2 | 2112 |
| 132.7 | 2099 |
| 133.7 | 2088 |
| 133.3 | 2094 |
| 133.6 | 2108 |
| 132.9 | 2118 |
| 132.8 | 2133 |
| 133.1 | 2124 |
| 133.9 | 2112 |
| 132.9 | 2140 |
| 133.3 | 2175 |
| 133 | 2182 |
| 133.1 | 2174 |
| 133 | 2181 |
| 132.7 | 2183 |
| 132.5 | 2176 |
| 132.8 | 2172 |
| 133.1 | 2155 |
| 132.6 | 2172 |
| 132.9 | 2183 |
| 132.1 | 2190 |
| 133.5 | 2172 |
| 132.5 | 2185 |
| 133.2 | 2176 |
| 132.3 | 2191 |
| 133 | 2200 |
| 132.9 | 2200 |
| 132.6 | 2197 |
| 133.3 | 2206 |
| 132.9 | 2201 |
| 133 | 2207 |
| 133.9 | 2211 |
| 133.2 | 2224 |
| 133.9 | 2208 |
| 133 | 2218 |
| 133 | 2216 |
| 133.1 | 2230 |
| 133.4 | 2246 |
| 133.1 | 2251 |
| 132.3 | 2277 |
| 133.5 | 2310 |
| 132.7 | 2318 |
| 132.7 | 2310 |
| 133.2 | 2306 |
| 132.8 | 2315 |
| 133.5 | 2324 |
| 133.1 | 2325 |
| 132.9 | 2327 |
| 133.9 | 2330 |
| 132.7 | 2331 |
| 132.3 | 2337 |
| 132.9 | 2361 |
| 132.6 | 2364 |
| 133.7 | 2358 |
| 132.9 | 2372 |
| 132.8 | 2372 |
| 133.7 | 2343 |
| 132.6 | 2348 |
| 132.8 | 2341 |
| 132.6 | 2368 |
| 133.2 | 2383 |
| 133.4 | 2374 |
| 132.4 | 2371 |
| 133.5 | 2366 |
| 133.1 | 2369 |
| 133.5 | 2358 |
| 132.8 | 2370 |
| 132.9 | 2382 |
| 132 | 2387 |
| 132.3 | 2375 |
| 133.3 | 2362 |
| 132.2 | 2376 |
| 132.8 | 2395 |
| 134 | 2401 |
| 133.3 | 2418 |
| 132.9 | 2428 |
| 133 | 2441 |
| 133 | 2419 |
| 132.7 | 2421 |
| 132.1 | 2421 |
| 133 | 2433 |
| 133.3 | 2424 |
| 133.6 | 2418 |
| 132.5 | 2420 |
| 133.5 | 2405 |
| 133.2 | 2402 |
| 133.7 | 2404 |
| 133.5 | 2398 |
| 133.9 | 2419 |
| 133.4 | 2410 |
| 132.3 | 2418 |
| 133.1 | 2429 |
| 133.6 | 2422 |
| 133.5 | 2417 |
| 133.6 | 2408 |
| 132.9 | 2397 |
| 133.4 | 2410 |
| 133.6 | 2418 |
| 133.2 | 2427 |
| 132.2 | 2433 |
| 133.6 | 2430 |
| 133.5 | 2459 |
| 133 | 2448 |
| 133.2 | 2452 |
| 133.2 | 2474 |
| 132.9 | 2485 |
| 133.8 | 2473 |
| 133.3 | 2481 |
| 132.9 | 2505 |
| 131.9 | 2491 |
| 132.8 | 2481 |
| 132.6 | 2491 |
| 132.8 | 2495 |
| 133.5 | 2500 |
| 133.1 | 2491 |
| 133.5 | 2499 |
| 132.5 | 2495 |
| 132.3 | 2489 |
| 132.6 | 2489 |
| 133.3 | 2496 |
| 132.2 | 2492 |
| 132.7 | 2510 |
| 133.1 | 2503 |
| 132.9 | 2476 |
| 133.5 | 2488 |
| 133.7 | 2488 |
| 132.4 | 2491 |
| 133.1 | 2506 |
| 132.1 | 2506 |
| 133.3 | 2485 |
| 132.8 | 2481 |
| 132.6 | 2501 |
| 132.7 | 2486 |
| 132.6 | 2522 |
| 133.3 | 2532 |
| 133.2 | 2524 |
| 132.7 | 2534 |
| 133.2 | 2550 |
| 133 | 2587 |
| 132.6 | 2592 |
| 133.3 | 2596 |
| 133.9 | 2578 |
| 133.4 | 2583 |
| 133.2 | 2587 |
| 133.3 | 2581 |
| 133.8 | 2576 |
| 134.1 | 2592 |
| 134.1 | 2621 |
| 133.5 | 2612 |
| 132.6 | 2597 |
| 132.4 | 2594 |
| 133.5 | 2585 |
| 131.9 | 2573 |
| 132.9 | 2584 |
| 132.7 | 2589 |
| 132.5 | 2568 |
| 133.3 | 2590 |
| 132.8 | 2602 |
| 133.8 | 2604 |
| 134.4 | 2591 |
| 134.5 | 2611 |
| 134.3 | 2616 |
| 134 | 2627 |
| 134.4 | 2634 |
| 133.2 | 2625 |
| 133.7 | 2617 |
| 132.9 | 2638 |
| 134 | 2619 |
| 134.3 | 2619 |
| 134.3 | 2629 |
| 134 | 2633 |
| 133 | 2636 |
| 133.9 | 2646 |
| 134.3 | 2666 |
| 133.5 | 2664 |
| 133.7 | 2674 |
| 133.8 | 2688 |
| 133.6 | 2670 |
| 133.6 | 2686 |
| 133.5 | 2693 |
| 133.1 | 2690 |
| 133.1 | 2693 |
| 133.8 | 2692 |
| 133.6 | 2698 |
| 133.3 | 2700 |
| 133.9 | 2698 |
| 133.9 | 2684 |
| 133.3 | 2675 |
| 134.3 | 2674 |
| 133.8 | 2682 |
| 133.4 | 2700 |
| 134 | 2708 |
| 133.6 | 2727 |
| 133.8 | 2740 |
| 132.9 | 2715 |
| 131.9 | 2724 |
| 132.9 | 2721 |
| 134.5 | 2727 |
| 133.7 | 2722 |
| 133.3 | 2753 |
| 133.4 | 2774 |
| 134.4 | 2781 |
| 133.7 | 2761 |
| 133.9 | 2775 |
| 134.7 | 2755 |
| 134.1 | 2763 |
| 134.3 | 2745 |
| 134 | 2737 |
| 132.9 | 2765 |
| 134.6 | 2773 |
| 134.5 | 2766 |
| 134.7 | 2757 |
| 134.5 | 2744 |
| 133.7 | 2758 |
| 133.9 | 2784 |
| 134.1 | 2780 |
| 134.3 | 2794 |
| 134.7 | 2794 |
| 133.5 | 2778 |
| 133.6 | 2777 |
| 134 | 2775 |
| 133.2 | 2810 |
| 133.9 | 2833 |
| 133.8 | 2818 |
| 134.1 | 2814 |
| 133.5 | 2815 |
| 133 | 2832 |
| 132.2 | 2815 |
| 134.2 | 2822 |
| 134.2 | 2827 |
| 134 | 2842 |
| 134.2 | 2835 |
| 133.7 | 2819 |
| 134.4 | 2818 |
| 133.8 | 2817 |
| 134.2 | 2831 |
| 133.4 | 2832 |
| 133.7 | 2842 |
| 134 | 2830 |
| 133.8 | 2842 |
| 133.8 | 2834 |
| 133.9 | 2842 |
| 134.1 | 2851 |
| 132.9 | 2870 |
| 134.1 | 2853 |
| 134.6 | 2860 |
| 133.9 | 2862 |
| 133.3 | 2866 |
| 134.2 | 2881 |
| 134.6 | 2909 |
| 134.7 | 2895 |
| 133.1 | 2885 |
| 135.4 | 2892 |
| 135 | 2922 |
| 133.1 | 2929 |
| 133.7 | 2910 |
| 134.3 | 2900 |
| 134.3 | 2908 |
| 134.2 | 2910 |
| 134.7 | 2918 |
| 134 | 2895 |
| 134.7 | 2906 |
| 133.9 | 2919 |
| 133.9 | 2909 |
| 134.4 | 2912 |
| 133.5 | 2916 |
| 134 | 2938 |
| 133.9 | 2936 |
| 134 | 2952 |
| 133.6 | 2951 |
| 134.1 | 2947 |
| 133.8 | 2929 |
| 133.7 | 2937 |
| 133.9 | 2951 |
| 132.5 | 2960 |
| 132.9 | 2987 |
| 133.3 | 2983 |
| 134 | 2988 |
| 134 | 3008 |
| 133.7 | 2992 |
| 133.9 | 2996 |
| 133 | 3002 |
| 133 | 3017 |
| 133.2 | 3033 |
| 132.9 | 3026 |
| 134.2 | 3024 |
| 133.2 | 3034 |
| 134 | 3062 |
| 133.3 | 3068 |
| 133.6 | 3062 |
| 134.1 | 3061 |
| 133.3 | 3067 |
| 133.4 | 3081 |
| 133.7 | 3077 |
| 134.3 | 3119 |
| 134.6 | 3097 |
| 133.4 | 3085 |
| 133.7 | 3101 |
| 133 | 3094 |
| 133.4 | 3111 |
| 133.7 | 3136 |
| 133.9 | 3141 |
| 133.5 | 3139 |
| 134.3 | 3139 |
| 133.7 | 3123 |
| 133.2 | 3142 |
| 133.8 | 3176 |
| 134.3 | 3176 |
| 134.1 | 3170 |
| 133.7 | 3180 |
| 132.9 | 3158 |
| 133.2 | 3181 |
| 133.9 | 3176 |
| 134.6 | 3163 |
| 133.6 | 3166 |
| 133.1 | 3192 |
| 134 | 3177 |
| 134.2 | 3158 |
| 133.9 | 3167 |
| 134.1 | 3180 |
| 133.7 | 3185 |
| 133.9 | 3184 |
| 133.8 | 3191 |
| 133.2 | 3200 |
| 134.3 | 3263 |
| 133.3 | 3267 |
| 134.6 | 3276 |
| 133.3 | 3289 |
| 133.6 | 3298 |
| 133.9 | 3284 |
| 133.5 | 3270 |
| 133.7 | 3266 |
| 134.8 | 3288 |
| 134 | 3270 |
| 133.6 | 3261 |
| 133.5 | 3264 |
| 133.9 | 3285 |
| 133.7 | 3281 |
| 134.2 | 3293 |
| 134.4 | 3301 |
| 133.6 | 3316 |
| 133.5 | 3300 |
| 133.7 | 3300 |
| 134.7 | 3298 |
| 134.4 | 3312 |
| 133 | 3318 |
| 133.7 | 3308 |
| 133.2 | 3337 |
| 133.7 | 3335 |
| 134.1 | 3357 |
| 133.4 | 3371 |
| 134.1 | 3384 |
| 134.3 | 3377 |
| 134.3 | 3358 |
| 133.8 | 3370 |
| 133.5 | 3364 |
| 133.1 | 3370 |
| 134.5 | 3374 |
| 134.5 | 3370 |
| 133.9 | 3368 |
| 134 | 3385 |
| 133.9 | 3364 |
| 133.7 | 3376 |
| 133.2 | 3379 |
| 133.6 | 3389 |
| 133.8 | 3387 |
| 134.1 | 3391 |
| 133.4 | 3376 |
| 133.3 | 3363 |
| 134 | 3361 |
| 134.3 | 3357 |
| 134.6 | 3357 |
| 134.7 | 3362 |
| 133.9 | 3373 |
| 133.9 | 3396 |
| 134.5 | 3370 |
| 134.1 | 3399 |
| 133.9 | 3402 |
| 134.5 | 3393 |
| 133.5 | 3378 |
| 135.7 | 3394 |
| 133.6 | 3398 |
| 133.3 | 3415 |
| 133.1 | 3401 |
| 133.5 | 3420 |
| 133.3 | 3447 |
| 133.6 | 3430 |
| 134.1 | 3406 |
| 132.8 | 3423 |
| 134.1 | 3453 |
| 134 | 3439 |
| 134.6 | 3442 |
| 133.8 | 3428 |
| 133.8 | 3453 |
| 133.4 | 3451 |
| 134.7 | 3452 |
| 133.7 | 3443 |
| 134 | 3461 |
| 134.9 | 3452 |
| 133.9 | 3467 |
| 133.8 | 3501 |
| 133.3 | 3488 |
| 134.5 | 3476 |
| 134.6 | 3473 |
| 134.9 | 3456 |
| 134.8 | 3440 |
| 134.5 | 3461 |
| 133.8 | 3458 |
| 134.2 | 3479 |
| 134 | 3442 |
| 133.7 | 3441 |
| 134.3 | 3464 |
| 134 | 3486 |
| 134.1 | 3469 |
| 133.9 | 3463 |
| 133.6 | 3476 |
| 134 | 3497 |
| 134 | 3499 |
| 134.2 | 3516 |
| 132.9 | 3491 |
| 133.5 | 3498 |
| 133.3 | 3489 |
| 134 | 3495 |
| 134.1 | 3510 |
| 134.5 | 3548 |
| 133.4 | 3546 |
| 133.1 | 3526 |
| 133.5 | 3529 |
| 133.8 | 3510 |
| 133.6 | 3511 |
| 133.7 | 3513 |
| 134.4 | 3528 |
| 133.9 | 3528 |
| 134.3 | 3531 |
| 133.8 | 3512 |
| 133 | 3520 |
| 133.6 | 3531 |
| 134.1 | 3536 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 10 | 25 |
| 12 | 35 |
| 14 | 45 |
| 16 | 55 |
| 18 | 65 |
| 20 | 75 |
| 22 | 85 |
| 24 | 90 |
| 34 | 90 |
| 36 | 100 |
| 38 | 110 |
| 40 | 120 |
| 42 | 130 |
| 52 | 130 |
| 54 | 140 |
| 56 | 150 |
| 58 | 160 |
| 68 | 160 |


</details>

### `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222`

PE CG, film with a 3 nm-radius cylindrical hole at 90 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_90C.data`). Status: finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.2968 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_90C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_90C_n320_c240_s1_rep222/data.lmp`
- **`hole_free`** (rdyu-rog): finished; started 2026-11-12 09:41 UTC, ended 2026-11-12 14:02 UTC; reads `systems/pe_cg_hole_r3nm_90C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_free` | `hole_free` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 131.3
- `free_shell.areal_density_ratio`: 0.8548
- `free_shell.msd.1 ns`: 488.5
- `free_shell.msd.10 ns`: 1240
- `free_shell.msd.end`: 1755
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- T (°C): 90
- `t_close_ns`: 0.13
- `thickness_final`: 131.8
- `thickness_t0`: 166.8

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 131.8 | — |
| 131.7 | — |
| 131.7 | — |
| 131.4 | — |
| 131.5 | — |
| 132.2 | — |
| 132.4 | — |
| 132.5 | — |
| 131.5 | — |
| 132 | — |
| 131.8 | — |
| 132.3 | — |
| 131.9 | — |
| 132.6 | — |
| 132.4 | — |
| 132 | — |
| 131.3 | — |
| 131.8 | — |
| 131.5 | — |
| 132.2 | — |
| 131.8 | — |
| 131.8 | — |
| 131.7 | — |
| 132.5 | — |
| 132.3 | — |
| 132.5 | — |
| 131.7 | — |
| 131.5 | — |
| 131.6 | — |
| 132.2 | — |
| 132.5 | — |
| 132.3 | — |
| 131.4 | — |
| 132.1 | — |
| 131.9 | — |
| 132.8 | — |
| 133 | — |
| 132.7 | — |
| 132.3 | — |
| 132.6 | — |
| 133 | — |
| 133.5 | — |
| 133.2 | — |
| 132.8 | — |
| 132.8 | — |
| 132.6 | — |
| 132.6 | — |
| 133.2 | — |
| 132.9 | — |
| 133.2 | — |
| 133.5 | — |
| 132.7 | — |
| 133.5 | — |
| 133.7 | — |
| 133.5 | — |
| 133.1 | — |
| 134.2 | — |
| 134.4 | — |
| 134.5 | — |
| 134.4 | — |
| 134.2 | — |
| 134.2 | — |
| 135.1 | — |
| 134.1 | — |
| 134.6 | — |
| 134.4 | — |
| 135.1 | — |
| 135.8 | — |
| 135.7 | — |
| 135 | — |
| 135.4 | — |
| 135.2 | — |
| 136.3 | — |
| 135.1 | — |
| 136 | — |
| 135.7 | — |
| 136.4 | — |
| 137 | — |
| 136.2 | — |
| 136.7 | — |
| 136.6 | — |
| 136.6 | — |
| 136.6 | — |
| 136.5 | — |
| 136.6 | — |
| 137.3 | — |
| 137.4 | — |
| 137.3 | — |
| 137.8 | — |
| 138.1 | — |
| 138.4 | — |
| 138.3 | — |
| 138.8 | — |
| 138.6 | — |
| 138 | — |
| 139.7 | — |
| 139.2 | — |
| 139.3 | — |
| 140.1 | — |
| 138.6 | — |
| 139.6 | — |
| 139.6 | — |
| 139.9 | — |
| 140.1 | — |
| 140.5 | — |
| 140.7 | — |
| 140.5 | — |
| 140.5 | — |
| 140.6 | — |
| 140.8 | — |
| 141.5 | — |
| 141.3 | — |
| 141.4 | — |
| 141.8 | — |
| 141.1 | — |
| 142.5 | — |
| 143 | — |
| 141.9 | — |
| 142.6 | — |
| 142.4 | — |
| 143 | — |
| 143.1 | — |
| 143.1 | — |
| 143.8 | — |
| 142.7 | — |
| 143.2 | — |
| 143.6 | — |
| 143.4 | — |
| 144.3 | — |
| 144.8 | — |
| 145.3 | — |
| 146.3 | — |
| 145 | — |
| 144.1 | — |
| 146.7 | — |
| 145.8 | — |
| 145.7 | — |
| 146.4 | — |
| 147 | — |
| 147.2 | — |
| 146.8 | — |
| 147.8 | — |
| 146.5 | — |
| 147.2 | — |
| 147.8 | — |
| 147.3 | — |
| 148.5 | — |
| 147.2 | — |
| 148.7 | — |
| 149.1 | — |
| 149.5 | — |
| 149.9 | — |
| 148.9 | — |
| 149.2 | — |
| 150.8 | — |
| 150.9 | — |
| 150.8 | — |
| 150.7 | — |
| 150.5 | — |
| 150.8 | — |
| 151.4 | — |
| 151.4 | — |
| 150.7 | — |
| 153 | — |
| 152.6 | — |
| 152.8 | — |
| 153.5 | — |
| 154 | — |
| 154.1 | — |
| 154.5 | — |
| 154.6 | — |
| 154.3 | — |
| 154.6 | — |
| 154.5 | — |
| 154.3 | — |
| 155.6 | — |
| 156.6 | — |
| 156.8 | — |
| 157.2 | — |
| 156.4 | — |
| 156.5 | — |
| 157.5 | — |
| 157.2 | — |
| 158 | — |
| 159.3 | — |
| 158.8 | — |
| 159.1 | — |
| 159.2 | — |
| 160 | — |
| 159.1 | — |
| 160.1 | — |
| 160.3 | — |
| 160.7 | — |
| 162.8 | — |
| 160.6 | — |
| 162.9 | — |
| 161 | — |
| 163.1 | — |
| 161.8 | — |
| 162.5 | — |
| 162.8 | — |
| 163.3 | — |
| 164 | — |
| 163.5 | — |
| 164.2 | — |
| 163.7 | — |
| 164.4 | — |
| 165.6 | — |
| 165.4 | — |
| 164.2 | — |
| 163.8 | — |
| 165.2 | — |
| 164.5 | — |
| 164.2 | — |
| 165.9 | — |
| 164.4 | — |
| 165.1 | — |
| 163.7 | — |
| 165.5 | — |
| 163.9 | — |
| 164.7 | — |
| 164.4 | — |
| 165.2 | — |
| 165.6 | — |
| 165.2 | — |
| 164.6 | — |
| 164.3 | — |
| 164.3 | — |
| 164.8 | — |
| 162.7 | — |
| 164.3 | — |
| 164.5 | — |
| 162.7 | — |
| 164.8 | — |
| 163.5 | — |
| 163 | — |
| 164.6 | — |
| 164.7 | — |
| 164.2 | — |
| 165.2 | — |
| 164.3 | — |
| 164.1 | — |
| 164.9 | — |
| 165.3 | — |
| 165.7 | — |
| 163.5 | — |
| 164.8 | — |
| 165 | — |
| 165.4 | — |
| 165.1 | — |
| 164.7 | — |
| 164.6 | — |
| 164.4 | — |
| 165.4 | — |
| 165.7 | — |
| 164.7 | — |
| 164.1 | — |
| 164.3 | — |
| 164.2 | — |
| 164.8 | — |
| 164.3 | — |
| 164.4 | — |
| 163.4 | — |
| 164.7 | — |
| 163.4 | — |
| 164 | — |
| 165.1 | — |
| 164.1 | — |
| 164.8 | — |
| 163.4 | — |
| 164.3 | — |
| 164.1 | — |
| 164.5 | — |
| 165.1 | — |
| 164.5 | — |
| 164.5 | — |
| 165.1 | — |
| 163.9 | — |
| 163.8 | — |
| 165 | — |
| 164.8 | — |
| 164.6 | — |
| 164.3 | — |
| 163.5 | — |
| 164.5 | — |
| 165.6 | — |
| 165.4 | — |
| 164.6 | — |
| 162.7 | — |
| 163.6 | — |
| 165 | — |
| 165.7 | — |
| 165.6 | — |
| 165.5 | — |
| 166.4 | — |
| 164.5 | — |
| 165.2 | — |
| 165.2 | — |
| 166.2 | — |
| 167.6 | — |
| 164.9 | — |
| 164.4 | — |
| 165.2 | — |
| 165.1 | — |
| 165 | — |
| 164.3 | — |
| 164.4 | — |
| 164.3 | — |
| 165.5 | — |
| 165.1 | — |
| 164.3 | — |
| 164.4 | — |
| 165.8 | — |
| 164 | — |
| 165.5 | — |
| 164.5 | — |
| 163.3 | — |
| 164.9 | — |
| 164.3 | — |
| 166.1 | — |
| 165 | — |
| 165.8 | — |
| 163.7 | — |
| 163.4 | — |
| 166.1 | — |
| 164.5 | — |
| 163.7 | — |
| 164.5 | — |
| 165 | — |
| 164.2 | — |
| 166.5 | — |
| 164.5 | — |
| 164.9 | — |
| 164.4 | — |
| 165.8 | — |
| 165.6 | — |
| 165.5 | — |
| 165.4 | — |
| 165.8 | — |
| 164.5 | — |
| 165.4 | — |
| 165 | — |
| 165.9 | — |
| 165.4 | — |
| 165.7 | — |
| 165.7 | — |
| 165.1 | — |
| 164.9 | — |
| 164.5 | — |
| 163.6 | — |
| 163.6 | — |
| 164.1 | — |
| 165.3 | — |
| 164.5 | — |
| 165.7 | — |
| 164.9 | — |
| 163.7 | — |
| 163.9 | — |
| 164.5 | — |
| 164.9 | — |
| 164 | — |
| 163.2 | — |
| 165.6 | — |
| 165.6 | — |
| 165.5 | — |
| 165.2 | — |
| 165.6 | — |
| 164.9 | — |
| 162.7 | — |
| 162.4 | — |
| 163 | — |
| 163.1 | — |
| 165.6 | — |
| 165.3 | — |
| 164.5 | — |
| 165.2 | — |
| 164.6 | — |
| 164.2 | — |
| 162.7 | — |
| 164.2 | — |
| 163.7 | — |
| 164.7 | — |
| 164 | — |
| 165.2 | — |
| 165.5 | — |
| 163.1 | — |
| 165.4 | — |
| 165.7 | — |
| 164.1 | — |
| 165 | — |
| 163.7 | — |
| 163.9 | — |
| 164.5 | — |
| 165.2 | — |
| 165.4 | — |
| 163.5 | — |
| 165.1 | — |
| 163.9 | — |
| 164.9 | — |
| 164.7 | — |
| 166.8 | 0 |
| 165.5 | 13.59 |
| 164 | 23.02 |
| 161.6 | 31.65 |
| 159.4 | 41.59 |
| 158.7 | 51.16 |
| 156.7 | 59.48 |
| 154.2 | 65.1 |
| 154.3 | 70.33 |
| 154.1 | 76.29 |
| 152.8 | 83.95 |
| 152 | 92.59 |
| 151.8 | 100.4 |
| 149.3 | 110.2 |
| 148.1 | 117.9 |
| 147.5 | 125.8 |
| 146.1 | 133.6 |
| 145.9 | 144.6 |
| 145.4 | 152.5 |
| 145.2 | 156.1 |
| 144.6 | 161.7 |
| 143.8 | 167.6 |
| 143.7 | 172.6 |
| 142.7 | 182.9 |
| 142.9 | 190.4 |
| 141.6 | 199.6 |
| 140.5 | 210.4 |
| 139.9 | 222.3 |
| 140.2 | 230.6 |
| 140 | 234.7 |
| 139.4 | 239.4 |
| 138.2 | 246 |
| 137.1 | 251 |
| 137.1 | 257.7 |
| 136.8 | 261.4 |
| 136.3 | 266.9 |
| 135.1 | 274.3 |
| 135 | 275 |
| 134.8 | 275.4 |
| 134.5 | 279.4 |
| 135.6 | 280.8 |
| 135.2 | 284.5 |
| 134.5 | 291.1 |
| 134.8 | 295.2 |
| 135.1 | 298.3 |
| 135.6 | 305.9 |
| 136.2 | 309.3 |
| 135.2 | 311.1 |
| 135.3 | 308.5 |
| 134.8 | 312 |
| 136.1 | 312.3 |
| 135.9 | 313.8 |
| 134.4 | 316.8 |
| 134.2 | 323.4 |
| 134.3 | 324.8 |
| 134.8 | 327 |
| 134.6 | 328.4 |
| 134.4 | 333.5 |
| 134.1 | 338.5 |
| 133.8 | 342.6 |
| 133.3 | 345.5 |
| 132.8 | 348.8 |
| 133.5 | 355.3 |
| 133.3 | 350.6 |
| 133.7 | 352 |
| 134.2 | 356.8 |
| 133.3 | 356.4 |
| 133.5 | 357.2 |
| 133.3 | 355.2 |
| 133.6 | 355.6 |
| 133.6 | 359.6 |
| 133.5 | 363.4 |
| 133.2 | 364.4 |
| 134 | 363.9 |
| 133.9 | 366.7 |
| 134.9 | 367.2 |
| 133.4 | 367.5 |
| 133.9 | 369.3 |
| 134.1 | 369.1 |
| 133.4 | 372 |
| 133.3 | 374.9 |
| 133.4 | 374.7 |
| 133.7 | 376 |
| 133.4 | 374.3 |
| 133.7 | 377 |
| 133.7 | 378.4 |
| 133.2 | 383.5 |
| 133.3 | 388 |
| 133.2 | 392.4 |
| 133.8 | 393.1 |
| 133.4 | 393.4 |
| 133.4 | 391.9 |
| 133.1 | 393.4 |
| 133 | 390.5 |
| 132.9 | 390.3 |
| 133.5 | 389.6 |
| 133.2 | 390.8 |
| 133 | 396.2 |
| 132.7 | 395.8 |
| 133 | 394.1 |
| 132.5 | 391.3 |
| 134 | 390.7 |
| 133.6 | 391.7 |
| 133.5 | 396.1 |
| 133.2 | 394.2 |
| 133.7 | 394.4 |
| 133.6 | 398.5 |
| 133.3 | 402.3 |
| 133 | 405.1 |
| 133.2 | 406.9 |
| 133.4 | 407.9 |
| 133.4 | 407.8 |
| 133.6 | 409.1 |
| 133.7 | 411.7 |
| 133.7 | 412.3 |
| 133.3 | 413 |
| 133.4 | 410.9 |
| 133.8 | 410.9 |
| 133.8 | 412.5 |
| 133.4 | 417.2 |
| 134.1 | 415.5 |
| 134 | 413.5 |
| 134.1 | 413.4 |
| 133.5 | 418 |
| 133 | 420.6 |
| 132.5 | 421.7 |
| 133.8 | 421.5 |
| 134.1 | 425.2 |
| 133.2 | 431.8 |
| 133.2 | 434.2 |
| 133.4 | 432.7 |
| 133.8 | 431.9 |
| 133.3 | 432.5 |
| 133.4 | 436.4 |
| 133.1 | 435.1 |
| 133.9 | 436.2 |
| 133.5 | 437.3 |
| 132.9 | 440 |
| 133.1 | 443.8 |
| 132.9 | 442.3 |
| 133.3 | 442.7 |
| 133.9 | 442.4 |
| 134 | 441.9 |
| 133.8 | 442 |
| 133.9 | 441.5 |
| 133.7 | 445.8 |
| 133.8 | 449.1 |
| 133.5 | 453 |
| 133.3 | 451.5 |
| 134.4 | 446.5 |
| 133.4 | 451.7 |
| 133 | 449.7 |
| 133 | 451 |
| 134 | 452.7 |
| 133 | 451.9 |
| 132.8 | 457.8 |
| 132.8 | 456.4 |
| 132.5 | 462.4 |
| 132.7 | 462.5 |
| 133.2 | 461.4 |
| 132.2 | 460.6 |
| 133.2 | 461 |
| 133.1 | 460.2 |
| 133.3 | 456.5 |
| 132.9 | 457.1 |
| 133.5 | 460.9 |
| 133.2 | 464.6 |
| 133.5 | 468.6 |
| 133.5 | 469.4 |
| 132.9 | 469.6 |
| 132.3 | 470.1 |
| 132.7 | 471.3 |
| 132.6 | 468.5 |
| 133 | 469.4 |
| 133.3 | 468.7 |
| 132.8 | 468.7 |
| 132.7 | 469.4 |
| 133 | 469.5 |
| 132.6 | 470.1 |
| 132.8 | 468.5 |
| 133.2 | 468 |
| 133.3 | 468.6 |
| 132.7 | 472.7 |
| 132.5 | 476.9 |
| 131.9 | 476.1 |
| 132.8 | 473.4 |
| 133 | 475.8 |
| 132.1 | 479.6 |
| 132.8 | 480.7 |
| 132.5 | 481.4 |
| 133.7 | 478.5 |
| 132.9 | 477.3 |
| 132.2 | 478.2 |
| 133 | 478.8 |
| 132.4 | 481.7 |
| 132.6 | 483.5 |
| 132.8 | 479.3 |
| 132.6 | 481.1 |
| 132.9 | 483.8 |
| 133.1 | 482.5 |
| 132.5 | 488.5 |
| 132.8 | 490.4 |
| 132.2 | 489.1 |
| 131.9 | 491.1 |
| 133.2 | 488.3 |
| 133.4 | 487.8 |
| 133 | 488.3 |
| 132.5 | 490.4 |
| 133.1 | 494.7 |
| 133.1 | 490.8 |
| 132.6 | 491.6 |
| 131.8 | 489.6 |
| 132.2 | 491.6 |
| 132.6 | 494.8 |
| 133.3 | 494.2 |
| 133.1 | 496.1 |
| 132.9 | 494.5 |
| 132.4 | 494.5 |
| 132.2 | 497.9 |
| 132.1 | 500 |
| 132 | 498.8 |
| 132.6 | 498.5 |
| 132.5 | 496.2 |
| 131.9 | 497.3 |
| 132.8 | 495.4 |
| 131.6 | 500.9 |
| 131.7 | 505.1 |
| 131.7 | 500.6 |
| 132.2 | 498.7 |
| 132.4 | 501.3 |
| 131.9 | 501.3 |
| 132.1 | 507.1 |
| 131.7 | 508.9 |
| 132.6 | 508.1 |
| 132.9 | 507.9 |
| 132.3 | 514.2 |
| 132.5 | 517.9 |
| 132.5 | 521.6 |
| 132.3 | 524.8 |
| 133.2 | 519.9 |
| 132.3 | 519.4 |
| 131.9 | 514 |
| 132.4 | 516.3 |
| 132 | 516.1 |
| 132.6 | 516.9 |
| 132.9 | 517.9 |
| 132.3 | 518.2 |
| 133.4 | 520.6 |
| 132.8 | 524.8 |
| 132.9 | 525.9 |
| 133.4 | 527.6 |
| 132.2 | 525.3 |
| 133.4 | 530.4 |
| 133.4 | 528 |
| 132.4 | 531.1 |
| 132.3 | 532.3 |
| 132.4 | 535.2 |
| 133 | 532.6 |
| 133.5 | 532.5 |
| 132.4 | 535 |
| 132.4 | 538.4 |
| 132.6 | 535.9 |
| 133.2 | 536.1 |
| 133.2 | 536.7 |
| 133.3 | 535.1 |
| 131.7 | 537 |
| 132 | 539 |
| 133.1 | 540.3 |
| 132.7 | 536.6 |
| 132.4 | 543.6 |
| 132.8 | 544.8 |
| 132.9 | 543.2 |
| 132.3 | 543.7 |
| 132.4 | 543.4 |
| 132.7 | 546.1 |
| 132.8 | 549.7 |
| 132.2 | 548.5 |
| 132.3 | 547.2 |
| 132.5 | 545.8 |
| 132.2 | 545.5 |
| 132.4 | 548 |
| 132.7 | 550.9 |
| 132 | 551.8 |
| 133.1 | 551.4 |
| 133.2 | 551.7 |
| 133.3 | 551.5 |
| 132.6 | 554 |
| 131.9 | 557.9 |
| 132.1 | 554.4 |
| 132.1 | 555.8 |
| 132.3 | 555.1 |
| 131.8 | 558.1 |
| 131.4 | 557.3 |
| 131.8 | 556.3 |
| 132.3 | 557.3 |
| 132.3 | 556.5 |
| 131.9 | 559.1 |
| 131.8 | 559.9 |
| 132.5 | 561.3 |
| 132.3 | 563.3 |
| 131.5 | 568.5 |
| 131.6 | 569.8 |
| 132.2 | 568.8 |
| 133 | 568.4 |
| 132.7 | 574.1 |
| 131.7 | 576.5 |
| 131.7 | 579.2 |
| 132.3 | 582.9 |
| 131.9 | 579.5 |
| 132.7 | 582.1 |
| 131.6 | 588.9 |
| 131.4 | 589.6 |
| 132.5 | 589.7 |
| 131.8 | 581.6 |
| 132.1 | 579.6 |
| 132 | 579.4 |
| 131.6 | 581.4 |
| 133 | 578.4 |
| 132.2 | 577.3 |
| 133 | 578.9 |
| 132.6 | 576.7 |
| 132.8 | 577.7 |
| 132.4 | 580.9 |
| 131.7 | 585.3 |
| 131.8 | 583.8 |
| 131.7 | 587.4 |
| 131.8 | 585.7 |
| 132 | 588.7 |
| 132.8 | 591.4 |
| 132.3 | 592.6 |
| 132.3 | 594.7 |
| 131.3 | 594.1 |
| 132.1 | 593 |
| 132.5 | 589.4 |
| 132 | 591.1 |
| 132.1 | 587.7 |
| 131.3 | 591.1 |
| 131.8 | 595.6 |
| 131.2 | 597.4 |
| 132 | 597.4 |
| 132.8 | 590.5 |
| 132.2 | 588.3 |
| 132.4 | 590.1 |
| 132.1 | 594.2 |
| 131.9 | 597 |
| 132.2 | 595.3 |
| 131.7 | 596.1 |
| 131.5 | 598.2 |
| 132.3 | 598.8 |
| 132 | 593.5 |
| 132.4 | 594.4 |
| 132.4 | 594.5 |
| 131.8 | 596.6 |
| 132.4 | 597.3 |
| 131.4 | 597.9 |
| 132.1 | 596.1 |
| 132.7 | 598.1 |
| 132.7 | 598 |
| 132.4 | 601.5 |
| 131.3 | 600 |
| 132.4 | 601.1 |
| 132.3 | 604.8 |
| 132.7 | 604.6 |
| 132.5 | 604 |
| 132.6 | 607.9 |
| 132.9 | 612.2 |
| 132.4 | 615.3 |
| 132.2 | 615.2 |
| 132.1 | 614.6 |
| 132.9 | 613.8 |
| 132.9 | 615.8 |
| 133 | 616.4 |
| 132.6 | 616.3 |
| 132.7 | 615.1 |
| 132.6 | 617 |
| 132.9 | 616.6 |
| 132.2 | 619.2 |
| 132 | 619 |
| 132.3 | 617.9 |
| 132.7 | 618 |
| 132 | 624.3 |
| 132.4 | 628.3 |
| 132.1 | 626.2 |
| 132.9 | 625.3 |
| 132.3 | 629.2 |
| 132.2 | 633 |
| 131.7 | 633.1 |
| 132.2 | 635.2 |
| 132.4 | 635.6 |
| 132.3 | 625.6 |
| 132.6 | 623.8 |
| 132.1 | 622.6 |
| 132 | 621.5 |
| 132.8 | 618.7 |
| 132.4 | 616.4 |
| 132.1 | 620.2 |
| 132.2 | 626.6 |
| 133 | 624.2 |
| 132.7 | 625.8 |
| 131.5 | 628.9 |
| 132.4 | 628.6 |
| 132.1 | 641.1 |
| 132.5 | 649 |
| 132.4 | 651.5 |
| 131.9 | 659.1 |
| 131.9 | 661.8 |
| 131 | 680.2 |
| 131.3 | 693.9 |
| 131.7 | 687.6 |
| 131.8 | 695.9 |
| 131.2 | 695.9 |
| 131.8 | 707.5 |
| 132.2 | 708.4 |
| 131 | 709.1 |
| 131.3 | 712.2 |
| 131.3 | 722.4 |
| 132.2 | 724.5 |
| 131.5 | 737.3 |
| 131.3 | 737.4 |
| 130.6 | 734 |
| 131.4 | 752.6 |
| 131 | 751.2 |
| 131.7 | 746.9 |
| 131.2 | 754.6 |
| 131.5 | 765.7 |
| 131.1 | 773.6 |
| 131.4 | 765.3 |
| 132 | 767.1 |
| 132.6 | 773.8 |
| 132.2 | 774.5 |
| 131.3 | 781.5 |
| 131.9 | 784.2 |
| 132 | 782.2 |
| 132 | 785 |
| 131.1 | 794.2 |
| 131.7 | 798.8 |
| 132.2 | 801.1 |
| 131.2 | 807.3 |
| 131.9 | 803.4 |
| 132.4 | 803 |
| 131.9 | 812.6 |
| 132.5 | 807.8 |
| 131.4 | 813.8 |
| 132.4 | 827.8 |
| 132 | 833.9 |
| 132.7 | 857.9 |
| 131.4 | 843.8 |
| 132.4 | 843.6 |
| 132.7 | 851.9 |
| 132.1 | 857.1 |
| 132.5 | 862.5 |
| 132.2 | 856.4 |
| 131.5 | 868.6 |
| 131.7 | 867.5 |
| 132.5 | 870.1 |
| 132.3 | 884 |
| 131.9 | 888.4 |
| 132 | 891 |
| 131.9 | 908.7 |
| 131.3 | 918.1 |
| 131.7 | 912.6 |
| 132.6 | 914.9 |
| 132.1 | 923.1 |
| 132.2 | 930.9 |
| 132.3 | 930.3 |
| 131.4 | 932.1 |
| 131.7 | 931.6 |
| 131.8 | 930.1 |
| 132 | 956.2 |
| 132.4 | 951 |
| 131.5 | 947.8 |
| 131.8 | 945.9 |
| 131.7 | 951.2 |
| 131.9 | 953.6 |
| 132 | 963.1 |
| 131.4 | 967.5 |
| 132.1 | 975.5 |
| 132.2 | 981.6 |
| 132.1 | 989.5 |
| 132 | 988.5 |
| 131.6 | 995 |
| 132.4 | 989.6 |
| 131.4 | 1000 |
| 133 | 1005 |
| 132.3 | 1014 |
| 131.9 | 1013 |
| 132 | 1010 |
| 132.1 | 1015 |
| 132 | 996.8 |
| 132.5 | 1006 |
| 132.2 | 1011 |
| 132 | 1018 |
| 131.6 | 1034 |
| 131.5 | 1036 |
| 131.5 | 1037 |
| 132.5 | 1039 |
| 132.3 | 1032 |
| 132 | 1038 |
| 131.7 | 1035 |
| 132.7 | 1022 |
| 132.1 | 1030 |
| 133 | 1032 |
| 132 | 1051 |
| 131.2 | 1051 |
| 131.7 | 1055 |
| 131.7 | 1070 |
| 131.3 | 1079 |
| 130.8 | 1092 |
| 131.6 | 1077 |
| 131.3 | 1068 |
| 131.3 | 1082 |
| 131.6 | 1086 |
| 131.4 | 1085 |
| 131.4 | 1083 |
| 131.8 | 1090 |
| 132.8 | 1099 |
| 131.8 | 1108 |
| 131.9 | 1111 |
| 132.2 | 1103 |
| 131.5 | 1112 |
| 132.6 | 1125 |
| 131.8 | 1116 |
| 131.3 | 1122 |
| 130.5 | 1119 |
| 132.3 | 1127 |
| 131.7 | 1124 |
| 131.4 | 1143 |
| 131.9 | 1147 |
| 131.3 | 1149 |
| 131.8 | 1162 |
| 131.8 | 1159 |
| 132.6 | 1157 |
| 131 | 1164 |
| 131.6 | 1160 |
| 131.1 | 1161 |
| 132 | 1168 |
| 131.5 | 1171 |
| 132.1 | 1171 |
| 132.3 | 1175 |
| 131.8 | 1183 |
| 131.9 | 1193 |
| 131.2 | 1207 |
| 131.5 | 1208 |
| 132.3 | 1204 |
| 132.4 | 1204 |
| 132.7 | 1216 |
| 132.1 | 1213 |
| 132 | 1217 |
| 131.6 | 1229 |
| 131.6 | 1231 |
| 131.9 | 1241 |
| 132.3 | 1240 |
| 131.7 | 1229 |
| 131.6 | 1232 |
| 130.6 | 1240 |
| 131.5 | 1231 |
| 131.9 | 1233 |
| 132.4 | 1218 |
| 132.7 | 1226 |
| 131.3 | 1242 |
| 131.9 | 1240 |
| 131.3 | 1241 |
| 131.4 | 1237 |
| 132.1 | 1231 |
| 132.2 | 1220 |
| 131.9 | 1226 |
| 132.2 | 1229 |
| 131.7 | 1226 |
| 131.9 | 1219 |
| 131.1 | 1220 |
| 131.6 | 1223 |
| 131.9 | 1221 |
| 131.6 | 1219 |
| 131.4 | 1236 |
| 131.8 | 1240 |
| 132.2 | 1245 |
| 131.8 | 1259 |
| 131.9 | 1255 |
| 131.7 | 1243 |
| 131.6 | 1244 |
| 132.5 | 1246 |
| 132.1 | 1268 |
| 130.8 | 1268 |
| 131.9 | 1261 |
| 131.7 | 1279 |
| 132.5 | 1276 |
| 132.3 | 1277 |
| 131.9 | 1281 |
| 131.9 | 1294 |
| 132.1 | 1291 |
| 132.3 | 1307 |
| 132.3 | 1311 |
| 132.4 | 1326 |
| 132.5 | 1327 |
| 131.9 | 1327 |
| 131.9 | 1332 |
| 131.3 | 1337 |
| 132.3 | 1335 |
| 131.6 | 1313 |
| 132.2 | 1316 |
| 131.8 | 1330 |
| 132.2 | 1339 |
| 132.7 | 1340 |
| 131.6 | 1334 |
| 131.4 | 1323 |
| 130.8 | 1331 |
| 130.8 | 1328 |
| 131.3 | 1344 |
| 131.1 | 1347 |
| 132.1 | 1353 |
| 132 | 1357 |
| 132.4 | 1354 |
| 131.7 | 1367 |
| 131.6 | 1373 |
| 131.4 | 1369 |
| 131.9 | 1371 |
| 131.6 | 1384 |
| 131.8 | 1373 |
| 131.5 | 1393 |
| 131.4 | 1376 |
| 131.2 | 1393 |
| 131.5 | 1403 |
| 131.9 | 1404 |
| 132.6 | 1397 |
| 131.4 | 1403 |
| 132.4 | 1390 |
| 132.6 | 1383 |
| 131.4 | 1365 |
| 132 | 1377 |
| 131.8 | 1379 |
| 131.8 | 1375 |
| 132.2 | 1383 |
| 132.2 | 1389 |
| 132.4 | 1391 |
| 132.1 | 1406 |
| 131.8 | 1407 |
| 131.6 | 1394 |
| 131.9 | 1395 |
| 131.8 | 1402 |
| 131.8 | 1408 |
| 131.8 | 1406 |
| 131.5 | 1416 |
| 132.2 | 1398 |
| 131.6 | 1394 |
| 131.9 | 1408 |
| 132.1 | 1419 |
| 131.5 | 1426 |
| 132.1 | 1450 |
| 131.7 | 1444 |
| 132.2 | 1432 |
| 131.5 | 1448 |
| 131.8 | 1460 |
| 131.7 | 1457 |
| 131.8 | 1453 |
| 131.3 | 1434 |
| 132 | 1445 |
| 131 | 1453 |
| 131.8 | 1435 |
| 132.6 | 1441 |
| 132.6 | 1429 |
| 131.9 | 1455 |
| 132.5 | 1450 |
| 132.8 | 1452 |
| 132.2 | 1454 |
| 132.9 | 1443 |
| 132.9 | 1448 |
| 132.3 | 1458 |
| 132.2 | 1452 |
| 131.9 | 1434 |
| 132 | 1442 |
| 131.7 | 1432 |
| 132.5 | 1451 |
| 132.3 | 1447 |
| 132.3 | 1454 |
| 132.4 | 1456 |
| 131.6 | 1462 |
| 131.7 | 1466 |
| 131.7 | 1467 |
| 132.2 | 1476 |
| 131.7 | 1488 |
| 131.7 | 1495 |
| 132.2 | 1484 |
| 132.2 | 1506 |
| 132.2 | 1504 |
| 132.5 | 1507 |
| 132.5 | 1510 |
| 132.7 | 1516 |
| 132.2 | 1511 |
| 132.7 | 1498 |
| 132.2 | 1508 |
| 132.4 | 1518 |
| 133 | 1519 |
| 132.6 | 1534 |
| 132.6 | 1540 |
| 131.8 | 1539 |
| 132.1 | 1564 |
| 132 | 1565 |
| 132.4 | 1576 |
| 131.7 | 1592 |
| 131.4 | 1579 |
| 131.8 | 1581 |
| 132 | 1587 |
| 132.1 | 1575 |
| 131.7 | 1587 |
| 132.1 | 1589 |
| 131.9 | 1598 |
| 132.3 | 1577 |
| 131.9 | 1588 |
| 131.5 | 1609 |
| 132.3 | 1615 |
| 131.5 | 1614 |
| 132 | 1621 |
| 132.2 | 1626 |
| 131.3 | 1619 |
| 131.7 | 1630 |
| 132.2 | 1637 |
| 131 | 1626 |
| 131.9 | 1645 |
| 131.8 | 1633 |
| 132.4 | 1629 |
| 132.1 | 1633 |
| 131.2 | 1651 |
| 131 | 1659 |
| 130.8 | 1663 |
| 132 | 1658 |
| 131.4 | 1671 |
| 131.9 | 1665 |
| 131 | 1680 |
| 131.2 | 1677 |
| 131.3 | 1654 |
| 131.8 | 1666 |
| 131.2 | 1672 |
| 130.8 | 1674 |
| 131.5 | 1659 |
| 131.1 | 1671 |
| 131 | 1674 |
| 131.8 | 1676 |
| 131.5 | 1686 |
| 131.9 | 1671 |
| 132 | 1672 |
| 132.1 | 1687 |
| 132.4 | 1698 |
| 131.6 | 1700 |
| 131.5 | 1708 |
| 131.9 | 1702 |
| 131.7 | 1719 |
| 131.8 | 1722 |
| 132 | 1732 |
| 131.9 | 1735 |
| 132 | 1732 |
| 131.9 | 1725 |
| 131.8 | 1733 |
| 132.9 | 1748 |
| 131.7 | 1762 |
| 132.4 | 1749 |
| 130.9 | 1746 |
| 131.8 | 1759 |
| 131.7 | 1747 |
| 131.1 | 1753 |
| 132 | 1748 |
| 131.8 | 1755 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 90 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 90 |


</details>

### `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222`

PE CG, film with a 4 nm-radius cylindrical hole at 160 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`). Status: finished: `hole_free_gap5nm`, `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.2729 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free_gap5nm`** (rdyu-server): finished; started 2026-11-02 20:16 UTC, ended 2026-11-07 03:09 UTC; reads `systems/pe_cg_hole_r4nm_160C_n320_c240_s1_rep222/data.lmp`
- **`hole_free`** (rdyu-server): finished; started 2026-11-12 02:07 UTC, ended 2026-11-14 15:02 UTC; reads `systems/pe_cg_hole_r4nm_160C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_free_gap5nm`, `hole_free` | `hole_free` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 133.5
- `free_shell.areal_density_ratio`: 0.7986
- `free_shell.msd.1 ns`: 572.8
- `free_shell.msd.10 ns`: 2199
- `free_shell.msd.end`: 2874
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- T (°C): 160
- `t_close_ns`: 2.1
- `thickness_final`: 133.7
- `thickness_t0`: 221.5

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 134.7 | — |
| 134 | — |
| 134.4 | — |
| 133.5 | — |
| 134.5 | — |
| 133.9 | — |
| 134.7 | — |
| 134.5 | — |
| 133.9 | — |
| 134.5 | — |
| 134.1 | — |
| 134.2 | — |
| 133.8 | — |
| 135.5 | — |
| 133.9 | — |
| 132.9 | — |
| 134 | — |
| 133.6 | — |
| 134.8 | — |
| 133.9 | — |
| 134.1 | — |
| 134.6 | — |
| 135 | — |
| 134.4 | — |
| 134.7 | — |
| 133.9 | — |
| 133.8 | — |
| 134.8 | — |
| 134.6 | — |
| 134.4 | — |
| 135.8 | — |
| 135.2 | — |
| 135.5 | — |
| 135.7 | — |
| 136.1 | — |
| 135.3 | — |
| 135.7 | — |
| 135.7 | — |
| 135.4 | — |
| 135.2 | — |
| 135.5 | — |
| 136.7 | — |
| 136.5 | — |
| 136.7 | — |
| 137.9 | — |
| 135.9 | — |
| 137.8 | — |
| 135.8 | — |
| 137.4 | — |
| 137.3 | — |
| 137.6 | — |
| 137.4 | — |
| 136.9 | — |
| 138.8 | — |
| 138.8 | — |
| 137.6 | — |
| 138.6 | — |
| 138 | — |
| 138 | — |
| 138.8 | — |
| 138.4 | — |
| 139.6 | — |
| 139.6 | — |
| 138.6 | — |
| 139.1 | — |
| 138.7 | — |
| 139.7 | — |
| 140 | — |
| 140.8 | — |
| 140.8 | — |
| 140.6 | — |
| 141 | — |
| 140.9 | — |
| 142.9 | — |
| 141.5 | — |
| 142.1 | — |
| 142.8 | — |
| 143.1 | — |
| 143.4 | — |
| 143.3 | — |
| 143.8 | — |
| 144.1 | — |
| 144 | — |
| 144.6 | — |
| 143.7 | — |
| 144.9 | — |
| 145.8 | — |
| 145.5 | — |
| 145.7 | — |
| 146.2 | — |
| 145.1 | — |
| 144.1 | — |
| 145.9 | — |
| 145.6 | — |
| 146.7 | — |
| 147 | — |
| 146.1 | — |
| 145.8 | — |
| 147.3 | — |
| 147 | — |
| 149 | — |
| 148.2 | — |
| 148.7 | — |
| 148.6 | — |
| 149.7 | — |
| 150 | — |
| 149.9 | — |
| 151.7 | — |
| 150.8 | — |
| 150.1 | — |
| 152 | — |
| 150.2 | — |
| 151 | — |
| 151 | — |
| 151.6 | — |
| 152.2 | — |
| 154 | — |
| 152.3 | — |
| 153.2 | — |
| 153.2 | — |
| 153.4 | — |
| 154.3 | — |
| 154.4 | — |
| 154 | — |
| 155.3 | — |
| 155.1 | — |
| 157.1 | — |
| 156.5 | — |
| 156.7 | — |
| 155.9 | — |
| 157.3 | — |
| 157.4 | — |
| 159 | — |
| 159.1 | — |
| 159.2 | — |
| 158.9 | — |
| 159.9 | — |
| 159.9 | — |
| 160.9 | — |
| 160.4 | — |
| 161.1 | — |
| 162.5 | — |
| 163.2 | — |
| 162.1 | — |
| 161.9 | — |
| 162.9 | — |
| 162.8 | — |
| 165.1 | — |
| 165.2 | — |
| 164.7 | — |
| 164.6 | — |
| 165.8 | — |
| 166.7 | — |
| 167.1 | — |
| 166.9 | — |
| 167.4 | — |
| 168.7 | — |
| 169.4 | — |
| 168.7 | — |
| 168.8 | — |
| 170.2 | — |
| 170.1 | — |
| 171.3 | — |
| 169.7 | — |
| 172.5 | — |
| 173 | — |
| 173.5 | — |
| 173.9 | — |
| 175.6 | — |
| 176.1 | — |
| 175.5 | — |
| 175 | — |
| 178.3 | — |
| 178 | — |
| 179.5 | — |
| 180.8 | — |
| 179.1 | — |
| 179.9 | — |
| 180.2 | — |
| 181.6 | — |
| 183.1 | — |
| 179.9 | — |
| 183 | — |
| 185.2 | — |
| 185.5 | — |
| 185 | — |
| 186.5 | — |
| 185.2 | — |
| 185.6 | — |
| 190 | — |
| 189.4 | — |
| 189.1 | — |
| 189 | — |
| 190.3 | — |
| 189.6 | — |
| 192.1 | — |
| 191.8 | — |
| 191.7 | — |
| 194.5 | — |
| 194.8 | — |
| 195.7 | — |
| 196.3 | — |
| 196.6 | — |
| 197.1 | — |
| 202.9 | — |
| 210.8 | — |
| 220 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | — |
| 221.5 | 0 |
| 221.5 | 18.74 |
| 221.5 | 33.26 |
| 221.5 | 44.06 |
| 221.5 | 53.44 |
| 221.5 | 62.48 |
| 221.5 | 71.42 |
| 221.5 | 79.06 |
| 221.5 | 86.93 |
| 221.5 | 95.47 |
| 221.5 | 101.5 |
| 221.5 | 107.6 |
| 221.5 | 114.9 |
| 221.5 | 119.5 |
| 221.5 | 123.4 |
| 221.5 | 127.9 |
| 221.5 | 133.5 |
| 221.5 | 138.1 |
| 221.5 | 142 |
| 221.5 | 145.6 |
| 221.5 | 150.6 |
| 221.5 | 156.4 |
| 221.5 | 160.8 |
| 221.5 | 164.8 |
| 221.5 | 169.7 |
| 221.5 | 175.5 |
| 221.5 | 179.6 |
| 221.5 | 183.1 |
| 221.5 | 186 |
| 221.5 | 191.9 |
| 221.5 | 196.7 |
| 221.5 | 200.2 |
| 221.5 | 203.2 |
| 221.5 | 206.9 |
| 221.5 | 209.6 |
| 221.5 | 212.2 |
| 221.5 | 216.6 |
| 221.5 | 219.7 |
| 221.5 | 223.2 |
| 221.5 | 225.1 |
| 221.5 | 227.5 |
| 221.5 | 231.3 |
| 221.5 | 234 |
| 221.5 | 236.7 |
| 221.5 | 238.5 |
| 221.5 | 242.5 |
| 221.5 | 244.1 |
| 221.5 | 246.5 |
| 221.5 | 248.4 |
| 221.5 | 252 |
| 221.5 | 258.9 |
| 221.5 | 261.4 |
| 221.5 | 263 |
| 221.5 | 263.3 |
| 221.5 | 264.7 |
| 221.5 | 271.3 |
| 221.5 | 279.4 |
| 221.5 | 285.1 |
| 221.5 | 292.9 |
| 221.5 | 295.6 |
| 221.5 | 300.7 |
| 221.5 | 301.7 |
| 221.5 | 302.2 |
| 221.5 | 301.4 |
| 221.5 | 302.6 |
| 221.5 | 302.8 |
| 221.5 | 305.8 |
| 221.5 | 311.5 |
| 221.5 | 318.1 |
| 221.5 | 321.3 |
| 221.5 | 322.9 |
| 221.5 | 326.3 |
| 221.5 | 327.7 |
| 221.5 | 326.3 |
| 221.5 | 334.1 |
| 221.5 | 341 |
| 221.5 | 347 |
| 221.5 | 350.9 |
| 221.5 | 351.4 |
| 221.5 | 357 |
| 221.5 | 359.8 |
| 221.5 | 364.2 |
| 221.5 | 370.3 |
| 221.5 | 372.6 |
| 221.5 | 377.1 |
| 221.5 | 378.2 |
| 221.5 | 378.2 |
| 221.5 | 380.1 |
| 221.5 | 383 |
| 221.5 | 384.6 |
| 221.5 | 382.9 |
| 221.5 | 385.1 |
| 221.5 | 388.6 |
| 221.5 | 391 |
| 221.5 | 392.1 |
| 221.5 | 392.4 |
| 221.5 | 391.3 |
| 221.5 | 393.5 |
| 221.5 | 396.2 |
| 221.5 | 398.4 |
| 221.5 | 401.4 |
| 221.5 | 403.3 |
| 221.5 | 403.8 |
| 221.5 | 405.2 |
| 221.5 | 408 |
| 221.5 | 411.1 |
| 221.5 | 412.7 |
| 221.5 | 409.7 |
| 221.5 | 409.7 |
| 221.5 | 412.5 |
| 221.5 | 414.1 |
| 221.5 | 415.2 |
| 221.5 | 415.2 |
| 221.5 | 416.2 |
| 221.5 | 421.5 |
| 221.5 | 428.4 |
| 221.5 | 434.1 |
| 221.5 | 437.1 |
| 221.5 | 436 |
| 221.5 | 435.5 |
| 221.5 | 437.8 |
| 221.5 | 441.2 |
| 221.5 | 448 |
| 221.5 | 453.9 |
| 221.5 | 459 |
| 221.5 | 464.5 |
| 221.5 | 465 |
| 221.5 | 467.6 |
| 221.5 | 467.9 |
| 221.5 | 469.7 |
| 221.5 | 469.8 |
| 221.5 | 471.6 |
| 221.5 | 470.5 |
| 221.5 | 475.5 |
| 221.5 | 480.4 |
| 221.5 | 484.7 |
| 221.5 | 487.1 |
| 221.5 | 492.3 |
| 221.5 | 493 |
| 221.5 | 493.9 |
| 221.5 | 501.3 |
| 221.5 | 508.1 |
| 221.5 | 511.4 |
| 221.5 | 509.4 |
| 221.5 | 511.6 |
| 221.5 | 512.5 |
| 221.5 | 513 |
| 221.5 | 511.5 |
| 221.5 | 507.4 |
| 221.5 | 506.4 |
| 221.5 | 506.2 |
| 221.5 | 504.4 |
| 221.5 | 504.3 |
| 221.5 | 503.4 |
| 221.5 | 503.8 |
| 221.5 | 503.9 |
| 221.5 | 504.5 |
| 221.5 | 503.7 |
| 221.5 | 503 |
| 221.5 | 500.3 |
| 221.5 | 503.3 |
| 221.5 | 501.4 |
| 221.5 | 502.6 |
| 221.5 | 507.4 |
| 221.5 | 507 |
| 221.5 | 509.9 |
| 221.5 | 517.3 |
| 221.5 | 527.1 |
| 221.5 | 534.6 |
| 221.5 | 538.1 |
| 221.5 | 536.9 |
| 221.5 | 536.5 |
| 221.5 | 535.2 |
| 221.5 | 532.8 |
| 221.5 | 534.6 |
| 221.5 | 537.3 |
| 221.5 | 538.6 |
| 221.5 | 544.8 |
| 221.5 | 553.2 |
| 221.5 | 560 |
| 221.5 | 562.7 |
| 221.5 | 563.4 |
| 221.5 | 558.7 |
| 221.5 | 554.5 |
| 221.5 | 552.5 |
| 221.5 | 553.5 |
| 221.5 | 556.8 |
| 221.5 | 560.4 |
| 221.5 | 564.9 |
| 221.5 | 568.2 |
| 221.5 | 568.7 |
| 221.5 | 568.7 |
| 221.5 | 567.7 |
| 221.5 | 568.3 |
| 221.5 | 567.9 |
| 221.5 | 562.9 |
| 221.5 | 562.6 |
| 221.5 | 564.8 |
| 221.5 | 568.4 |
| 221.5 | 568.7 |
| 221.5 | 572.8 |
| 221.5 | 570.8 |
| 221.5 | 572.8 |
| 221.5 | 571.9 |
| 221.5 | 570.7 |
| 221.5 | 571.4 |
| 221.5 | 576.1 |
| 221.5 | 577.1 |
| 221.5 | 580.3 |
| 221.5 | 581.2 |
| 221.5 | 578.2 |
| 221.5 | 573.4 |
| 221.5 | 578.9 |
| 221.5 | 581.8 |
| 221.5 | 582.9 |
| 221.5 | 586.8 |
| 221.5 | 588.6 |
| 221.5 | 588.8 |
| 221.5 | 589.6 |
| 221.5 | 589.3 |
| 221.5 | 595 |
| 221.5 | 598.2 |
| 221.5 | 598.2 |
| 221.5 | 601.4 |
| 221.5 | 600.8 |
| 221.5 | 603.3 |
| 221.5 | 604.4 |
| 221.5 | 601.4 |
| 221.5 | 601.8 |
| 221.5 | 603.8 |
| 221.5 | 609.6 |
| 221.5 | 609.6 |
| 221.5 | 613.6 |
| 221.5 | 610 |
| 221.5 | 611.3 |
| 221.5 | 614.5 |
| 221.5 | 616.6 |
| 221.5 | 621.4 |
| 221.5 | 622.2 |
| 221.5 | 626.5 |
| 221.5 | 630 |
| 221.5 | 636.1 |
| 221.5 | 641.1 |
| 221.5 | 648.6 |
| 221.5 | 656.5 |
| 221.5 | 656.8 |
| 221.5 | 654.9 |
| 221.5 | 651.4 |
| 221.5 | 652.3 |
| 221.5 | 652.8 |
| 221.5 | 652.7 |
| 221.5 | 649.9 |
| 221.5 | 652.4 |
| 221.5 | 653.7 |
| 221.5 | 655.8 |
| 221.5 | 657.1 |
| 221.5 | 662.8 |
| 221.5 | 666 |
| 221.5 | 667.3 |
| 221.5 | 668.2 |
| 221.5 | 665.4 |
| 221.5 | 667.3 |
| 221.5 | 667.9 |
| 221.5 | 670.7 |
| 221.5 | 673.5 |
| 221.5 | 678.8 |
| 221.5 | 679.9 |
| 221.5 | 680.2 |
| 221.5 | 678.8 |
| 221.5 | 674.9 |
| 221.5 | 675.8 |
| 221.5 | 682.5 |
| 221.5 | 682.7 |
| 221.5 | 688.4 |
| 221.5 | 694.3 |
| 221.5 | 700.1 |
| 221.5 | 698.9 |
| 221.5 | 698.1 |
| 221.5 | 694.2 |
| 221.5 | 695.5 |
| 221.5 | 694.9 |
| 221.5 | 699 |
| 221.5 | 701.4 |
| 221.5 | 703.4 |
| 221.5 | 703.6 |
| 221.5 | 704 |
| 221.5 | 707.3 |
| 220.6 | 706.3 |
| 221.5 | 704.6 |
| 221.5 | 704.9 |
| 221.5 | 703.8 |
| 221.5 | 702.2 |
| 221.5 | 705.1 |
| 221.5 | 712.2 |
| 221.5 | 717.8 |
| 221.5 | 719.7 |
| 221.5 | 719.5 |
| 221.5 | 720.1 |
| 221.5 | 725.9 |
| 221.5 | 729.2 |
| 221.5 | 736 |
| 221.5 | 740.3 |
| 221.5 | 739.3 |
| 221.5 | 736.3 |
| 221.5 | 731.9 |
| 221.5 | 730.7 |
| 221.3 | 732.6 |
| 221.5 | 736.6 |
| 221.5 | 736.2 |
| 221.5 | 738.9 |
| 221.5 | 741.3 |
| 221.5 | 745.7 |
| 221.5 | 750.3 |
| 221.5 | 748.2 |
| 221.5 | 746.1 |
| 221.5 | 747.7 |
| 221.5 | 746.7 |
| 221.5 | 752.2 |
| 221.5 | 757.7 |
| 221.5 | 765.5 |
| 221.5 | 766 |
| 221.5 | 765.7 |
| 221.5 | 766.6 |
| 221.5 | 762.1 |
| 221.5 | 766.3 |
| 221.5 | 764.1 |
| 221.5 | 761.5 |
| 221.5 | 759.7 |
| 221.5 | 760.7 |
| 221.5 | 764.4 |
| 221.5 | 767.7 |
| 221.5 | 776.2 |
| 221.5 | 776.5 |
| 221.5 | 777.8 |
| 221.5 | 779.9 |
| 221.5 | 781.2 |
| 221.5 | 779.1 |
| 221.5 | 781.7 |
| 221.5 | 780.1 |
| 221.5 | 781.7 |
| 221.5 | 785.1 |
| 221.5 | 790.4 |
| 221.5 | 791.5 |
| 221 | 789.6 |
| 221.5 | 789.4 |
| 221.5 | 786.9 |
| 221.5 | 788.4 |
| 221.5 | 788.3 |
| 221.5 | 790.5 |
| 221.5 | 793.7 |
| 221.5 | 800.7 |
| 221.5 | 802.1 |
| 221.5 | 804.4 |
| 221.5 | 805.4 |
| 221.5 | 809.5 |
| 221.5 | 809 |
| 221 | 812.1 |
| 221.5 | 811.6 |
| 221.5 | 814 |
| 221.5 | 814 |
| 221.5 | 819.6 |
| 221.5 | 820.2 |
| 221.5 | 828.9 |
| 221.5 | 831.2 |
| 221.5 | 834.9 |
| 221.5 | 836.4 |
| 221.5 | 833.9 |
| 221.5 | 841 |
| 221.1 | 843 |
| 221.5 | 843.2 |
| 221.5 | 842.9 |
| 221.5 | 840.1 |
| 221.5 | 832.8 |
| 221.5 | 834.2 |
| 221.5 | 830.4 |
| 221.5 | 831.4 |
| 221.3 | 838.9 |
| 221.5 | 844.6 |
| 221.5 | 849.1 |
| 221.5 | 845 |
| 221.5 | 843.7 |
| 221.5 | 845.6 |
| 221.2 | 849.3 |
| 221.5 | 851.7 |
| 221.5 | 853.1 |
| 221.5 | 847.1 |
| 221.5 | 846.8 |
| 221.5 | 844.7 |
| 220.7 | 848.1 |
| 218.9 | 850.2 |
| 221.5 | 854.2 |
| 221.5 | 856.2 |
| 221.5 | 851.9 |
| 221.5 | 851.9 |
| 221.5 | 850.8 |
| 221.5 | 851.9 |
| 221.5 | 848.7 |
| 221.5 | 851.8 |
| 221.5 | 856.7 |
| 221.5 | 860.4 |
| 221.5 | 862.9 |
| 221.5 | 887.9 |
| 221.5 | 919.7 |
| 221.5 | 944.6 |
| 221.5 | 956.8 |
| 221.5 | 1003 |
| 221.5 | 1017 |
| 219.4 | 1039 |
| 219 | 1071 |
| 218.9 | 1108 |
| 212.7 | 1102 |
| 203.4 | 1118 |
| 199.9 | 1118 |
| 205.1 | 1114 |
| 215.4 | 1115 |
| 219.5 | 1163 |
| 220.9 | 1153 |
| 219.2 | 1153 |
| 217.6 | 1194 |
| 216.1 | 1208 |
| 215.1 | 1234 |
| 194 | 1249 |
| 188.4 | 1231 |
| 196.7 | 1237 |
| 215.7 | 1265 |
| 206.6 | 1279 |
| 201.5 | 1282 |
| 187.2 | 1279 |
| 169.9 | 1284 |
| 148.3 | 1288 |
| 136.8 | 1334 |
| 129.8 | 1332 |
| 127.1 | 1334 |
| 130.8 | 1315 |
| 127.2 | 1321 |
| 128.4 | 1344 |
| 127.9 | 1343 |
| 128 | 1343 |
| 126.7 | 1357 |
| 124.3 | 1373 |
| 127.9 | 1372 |
| 126.8 | 1366 |
| 126.4 | 1379 |
| 120.9 | 1376 |
| 119.7 | 1390 |
| 121.3 | 1379 |
| 119.4 | 1381 |
| 117.8 | 1416 |
| 119.7 | 1428 |
| 118.7 | 1443 |
| 114.8 | 1449 |
| 115.4 | 1478 |
| 115.8 | 1483 |
| 116.1 | 1506 |
| 114.2 | 1520 |
| 118.6 | 1516 |
| 118.8 | 1531 |
| 120.9 | 1535 |
| 120.3 | 1533 |
| 120.4 | 1555 |
| 122 | 1579 |
| 120.2 | 1594 |
| 119.7 | 1594 |
| 126.4 | 1603 |
| 124.3 | 1618 |
| 127 | 1644 |
| 124.3 | 1656 |
| 125.3 | 1691 |
| 126.7 | 1687 |
| 127 | 1705 |
| 130.2 | 1690 |
| 130.4 | 1700 |
| 126.6 | 1723 |
| 126.5 | 1749 |
| 128.6 | 1750 |
| 129.4 | 1748 |
| 130.2 | 1758 |
| 129.4 | 1785 |
| 131.3 | 1786 |
| 131 | 1805 |
| 128.6 | 1815 |
| 130.5 | 1813 |
| 131.3 | 1842 |
| 129.4 | 1846 |
| 130.1 | 1877 |
| 130 | 1883 |
| 131.8 | 1914 |
| 131.4 | 1911 |
| 130.4 | 1912 |
| 130.8 | 1926 |
| 131.8 | 1912 |
| 132 | 1906 |
| 130.4 | 1928 |
| 131.8 | 1909 |
| 131.5 | 1897 |
| 129.3 | 1906 |
| 130.2 | 1916 |
| 129.5 | 1915 |
| 128.6 | 1913 |
| 129.5 | 1926 |
| 130.8 | 1947 |
| 128.8 | 1941 |
| 129.5 | 1957 |
| 130.2 | 1972 |
| 129.6 | 1969 |
| 129.6 | 1998 |
| 129.2 | 2018 |
| 128 | 2035 |
| 125.7 | 2003 |
| 128.6 | 2004 |
| 127.2 | 2019 |
| 128 | 2040 |
| 128.8 | 2021 |
| 125.8 | 1999 |
| 127.7 | 1989 |
| 129.1 | 2009 |
| 129.2 | 1997 |
| 129 | 2006 |
| 129.6 | 2012 |
| 128.5 | 2020 |
| 128.1 | 2047 |
| 128.1 | 2062 |
| 128.3 | 2046 |
| 127.9 | 2062 |
| 128.7 | 2046 |
| 127.9 | 2058 |
| 127.1 | 2060 |
| 128.5 | 2031 |
| 129 | 2055 |
| 128.3 | 2054 |
| 129.4 | 2049 |
| 129.1 | 2063 |
| 127.8 | 2051 |
| 128.5 | 2080 |
| 128.3 | 2086 |
| 129.4 | 2087 |
| 128.6 | 2115 |
| 128.5 | 2109 |
| 130.7 | 2125 |
| 130 | 2126 |
| 129.5 | 2133 |
| 130.6 | 2120 |
| 130.5 | 2126 |
| 129.6 | 2121 |
| 131.3 | 2117 |
| 130.7 | 2122 |
| 131 | 2112 |
| 130.9 | 2125 |
| 130.3 | 2116 |
| 131.4 | 2152 |
| 130.7 | 2147 |
| 132.3 | 2160 |
| 131.7 | 2149 |
| 129.5 | 2182 |
| 131 | 2191 |
| 130.7 | 2164 |
| 130.9 | 2157 |
| 129.4 | 2158 |
| 130.2 | 2154 |
| 129.2 | 2163 |
| 129.2 | 2199 |
| 129.2 | 2167 |
| 129.2 | 2168 |
| 127.8 | 2158 |
| 129.2 | 2177 |
| 129.6 | 2180 |
| 129.2 | 2188 |
| 129.7 | 2203 |
| 129.4 | 2232 |
| 129.1 | 2238 |
| 128.5 | 2248 |
| 128.4 | 2271 |
| 129.1 | 2228 |
| 128 | 2246 |
| 128.8 | 2271 |
| 130.2 | 2258 |
| 129.6 | 2305 |
| 128.5 | 2330 |
| 128.2 | 2312 |
| 130.4 | 2297 |
| 130.1 | 2350 |
| 129.8 | 2399 |
| 129.4 | 2369 |
| 129.6 | 2383 |
| 128.7 | 2379 |
| 128.9 | 2376 |
| 129 | 2370 |
| 130.6 | 2355 |
| 129.3 | 2349 |
| 129.6 | 2374 |
| 129.9 | 2349 |
| 129.3 | 2365 |
| 130.8 | 2373 |
| 130.8 | 2349 |
| 130.5 | 2374 |
| 131 | 2382 |
| 131.3 | 2385 |
| 132.1 | 2386 |
| 132.5 | 2386 |
| 132.3 | 2399 |
| 132.5 | 2385 |
| 131.6 | 2384 |
| 132.1 | 2401 |
| 133.4 | 2407 |
| 130.9 | 2424 |
| 131.7 | 2425 |
| 132.1 | 2436 |
| 132.4 | 2476 |
| 131.8 | 2490 |
| 131.8 | 2466 |
| 131.5 | 2489 |
| 131.1 | 2501 |
| 131.6 | 2487 |
| 132.3 | 2480 |
| 130.9 | 2527 |
| 130.6 | 2498 |
| 131.5 | 2511 |
| 130.6 | 2512 |
| 130.9 | 2519 |
| 132 | 2529 |
| 131.5 | 2506 |
| 130.6 | 2518 |
| 130.2 | 2540 |
| 130.6 | 2547 |
| 130.4 | 2592 |
| 131.2 | 2567 |
| 129.1 | 2550 |
| 130.8 | 2549 |
| 130.6 | 2549 |
| 130.5 | 2582 |
| 130 | 2579 |
| 130.5 | 2601 |
| 130.2 | 2573 |
| 130.9 | 2566 |
| 131.4 | 2545 |
| 130.5 | 2546 |
| 130 | 2564 |
| 129.5 | 2551 |
| 130.5 | 2552 |
| 130.5 | 2561 |
| 131.3 | 2555 |
| 129.4 | 2534 |
| 130.4 | 2557 |
| 130.5 | 2557 |
| 130.9 | 2608 |
| 130.6 | 2607 |
| 131.2 | 2598 |
| 131.6 | 2591 |
| 131.8 | 2610 |
| 132 | 2603 |
| 132.4 | 2606 |
| 132.8 | 2616 |
| 132.1 | 2644 |
| 132.6 | 2634 |
| 132 | 2655 |
| 132.8 | 2620 |
| 133.3 | 2664 |
| 133.2 | 2662 |
| 133 | 2654 |
| 133.9 | 2672 |
| 133.2 | 2684 |
| 132.6 | 2653 |
| 132.4 | 2643 |
| 132.8 | 2651 |
| 132.4 | 2646 |
| 132.3 | 2654 |
| 131.2 | 2653 |
| 133.2 | 2658 |
| 131.6 | 2655 |
| 133.1 | 2681 |
| 132.1 | 2665 |
| 132.5 | 2677 |
| 132.1 | 2674 |
| 131.6 | 2664 |
| 133.2 | 2650 |
| 132.3 | 2661 |
| 131.4 | 2691 |
| 132.2 | 2701 |
| 131.5 | 2703 |
| 130.5 | 2731 |
| 131.4 | 2707 |
| 131.7 | 2707 |
| 131.2 | 2723 |
| 131.2 | 2741 |
| 131.6 | 2746 |
| 131.8 | 2750 |
| 132.4 | 2728 |
| 130.5 | 2712 |
| 132.5 | 2696 |
| 132.3 | 2724 |
| 131.9 | 2718 |
| 132.6 | 2713 |
| 131.5 | 2720 |
| 132.4 | 2723 |
| 131.3 | 2735 |
| 130.8 | 2783 |
| 132.8 | 2784 |
| 132.2 | 2801 |
| 131.7 | 2763 |
| 133 | 2768 |
| 131.6 | 2789 |
| 132 | 2804 |
| 133.8 | 2780 |
| 132.2 | 2805 |
| 133.7 | 2805 |
| 133.5 | 2816 |
| 133.5 | 2827 |
| 133 | 2799 |
| 132.4 | 2784 |
| 133 | 2799 |
| 134.1 | 2804 |
| 133.4 | 2782 |
| 133.6 | 2775 |
| 132 | 2783 |
| 132.2 | 2775 |
| 132.8 | 2760 |
| 132.8 | 2764 |
| 133.1 | 2774 |
| 133.8 | 2761 |
| 133.4 | 2789 |
| 133 | 2805 |
| 132.9 | 2790 |
| 133.9 | 2785 |
| 132.7 | 2783 |
| 133.3 | 2820 |
| 134.6 | 2806 |
| 134 | 2805 |
| 134.6 | 2797 |
| 134 | 2813 |
| 133 | 2849 |
| 132.4 | 2861 |
| 132.4 | 2843 |
| 133.1 | 2830 |
| 133.2 | 2841 |
| 133.9 | 2831 |
| 133.8 | 2853 |
| 132.5 | 2841 |
| 132.7 | 2858 |
| 133.4 | 2857 |
| 131.2 | 2831 |
| 132.4 | 2829 |
| 133.1 | 2845 |
| 132.9 | 2859 |
| 132.2 | 2862 |
| 132.5 | 2854 |
| 132.3 | 2844 |
| 133.1 | 2811 |
| 133.4 | 2821 |
| 133.2 | 2815 |
| 132.3 | 2835 |
| 131.9 | 2830 |
| 133.2 | 2839 |
| 133.3 | 2855 |
| 132.5 | 2856 |
| 132.9 | 2858 |
| 133.7 | 2866 |
| 134.6 | 2843 |
| 133.8 | 2848 |
| 133 | 2874 |
| 133.5 | 2878 |
| 133.7 | 2874 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |


</details>

### `pe_cg_pore_w5nm_n320_c240_s1_rep222`

PE CG, 5 nm dry slit pore, 320 chains × C240, 25,600 beads; built from `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`). Status: finished: pore.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress of `pe_cg_amorph_n320_c240_s1_rep222` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 9.18 (melt 6.7) | n/a | `extend` progress of `pe_cg_amorph_n320_c240_s1_rep222` |
| R<sub>g</sub> (Å) | 33.24 ± 0.29 | 32.34 ± 0.06 | 30.75 ± 0.11 | 29.95 ± 0.07 | — | trend | `pore` |
| R<sub>ee</sub> (Å) | 83.6 ± 0.8 | 81.2 ± 0.2 | 77.2 ± 0.8 | 75.0 ± 0.3 | — | trend | `pore` |
| C<sub>n</sub> | 12.12 ± 0.25 | 11.59 ± 0.04 | 10.46 ± 0.12 | 9.88 ± 0.07 | — | trend | `pore` |
| P2 1/e time (ps) | 100 | 21.1 | 10.7 | 6.8 | — | corr | `pore` |
| P2 1/e time, surface layer (ps) | 59.4 | 13.2 | 6.69 | 4.59 | — | corr | `pore` |
| P2 1/e time, interior layer (ps) | 116 | 24.8 | 12.8 | 7.84 | — | corr | `pore` |
| segment MSD at 1 ns lag (Å²) | 193.1 | 323.6 | 390.3 | 442.2 | — | corr | `pore` |
| max chain COM MSD (Å²) at lag | 226.9 at 12.5 ns | 417.5 at 12.5 ns | 514.9 at 12.5 ns | 584.8 at 12.5 ns | — | n/a | `pore` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.21 | 0.40 | 0.54 | 0.65 | — | n/a | `pore` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.90) | not diffusive (slope 0.74) | not diffusive (slope 0.88) | not diffusive (slope 0.74) | — | n/a | `pore` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached (extrap. 49.6) | not reached (extrap. 31.7) | not reached (extrap. 23.5) | not reached (extrap. 18.3) | — | n/a | `pore` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached (extrap. 72.1) | not reached (extrap. 42.6) | not reached (extrap. 32.9) | not reached (extrap. 22.3) | — | n/a | `pore` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.181 | 0.124 | 0.107 | 0.102 | — | — | `pore` |
| γ, run monitor (mN/m) | 34.6 ± 0.3 | 30.5 ± 0.2 | 28.3 ± 0.2 | 28.2 ± 0.2 | — | comp | `pore` progress |
| γ, analysis (mN/m) | 34.4 ± 0.3 | 30.3 ± 0.3 | 28.3 ± 0.3 | 27.9 ± 0.3 | — | comp | `pore` |
| dγ/dT (mN m⁻¹ K⁻¹) | — | — | — | — | cooling branch 25–201.6 °C: -0.0492 ± 0.0044 (χ²<sub>red</sub> 1.63); heating sweep 25–160 °C: -0.0520 ± 0.0035 (χ²<sub>red</sub> 1.99) | comp | `pore` |
| γ at 25 °C from the dγ/dT fit (mN/m) | — | — | — | — | cooling branch: 33.13; heating sweep: 33.94 | comp | `pore` |
| e<sub>s</sub>, surface excess energy (mJ/m²) | 57.6 ± 1.2 | 56.4 ± 1.0 | 54.6 ± 0.9 | 53.8 ± 0.8 | — | — | `pore` |
| film thickness between the Gibbs surfaces (Å) | 129.34 ± 0.01 | 131.29 ± 0.01 | 132.53 ± 0.02 | 133.55 ± 0.02 | — | trend | `pore` |
| gap between the Gibbs surfaces (Å) | 50.01 | 48.06 | 46.82 | 45.80 | — | trend | `pore` |
| film interior density (g/cm³) | 0.8347 ± 0.0001 | 0.7980 ± 0.0001 | 0.7758 ± 0.0001 | 0.7592 ± 0.0001 | — | trend | `pore` |
| interfacial width, 10–90 % (Å) | 6.83 | 8.12 | 8.77 | 9.27 | — | trend | `pore` |
| closest approach across the gap (Å) | 40.8 | 36.6 | 34.2 | 32.1 | — | trend | `pore` |
| film α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 6.996; 25–90 °C: 6.920; 90–160 °C: 7.099 | — | `pore` |
| α<sub>z</sub>, film-thickness expansion (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 2.350 ± 0.020 (χ²<sub>red</sub> 4.98); 25–90 °C: 2.282 ± 0.026 (χ²<sub>red</sub> 1.68); 90–160 °C: 2.412 ± 0.047 (χ²<sub>red</sub> 4.66) | — | `pore` |
| C<sub>v</sub> of the film, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 0.830 ± 0.003 (χ²<sub>red</sub> 34.5); 25–90 °C: 0.843 ± 0.003 (χ²<sub>red</sub> 4.36); 90–160 °C: 0.814 ± 0.003 (χ²<sub>red</sub> 10.2) | — | `pore` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.5473 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **pore** (rdyu-rog): finished; started 2026-10-29 18:08 UTC, ended 2026-10-30 12:05 UTC; reads `systems/pe_cg_pore_w5nm_n320_c240_s1_rep222/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 34.6 ± 0.3; 90 °C 30.5 ± 0.2; 130 °C 28.3 ± 0.2; 160 °C 28.2 ± 0.2

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | 25 °C 34.6 ± 0.3; 90 °C 30.5 ± 0.2; 130 °C 28.3 ± 0.2; 160 °C 28.2 ± 0.2 | finished: pore | pore |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`pore` analysis**

Pore analysis (`sepsim analyze pore`, generated 2026-11-09 19:06 UTC on rdyu-server):

- dγ/dT, cooling-branch fit (mN m⁻¹ K⁻¹): -0.04916
- γ at 25 °C, cooling-branch fit (mN/m): 33.13
- dγ/dT, heating-sweep fit (mN m⁻¹ K⁻¹): -0.05203
- γ at 25 °C, heating-sweep fit (mN/m): 33.94
- analysis node: rdyu-server
- nominal gap width (nm): 5
- wall (film) thickness (Å): 129.4

Convergence of the film quantities, per segment:

| γ (mN/m) | segment end (ps) | gap between the Gibbs surfaces (Å) | film interior density (g/cm³) |
|---|---|---|---|
| 21.35 ± 0.7542 | 2000 | — | — |
| 24.1 ± 0.9296 | 7000 | — | — |
| 25.71 ± 0.523 | 1.2e+04 | — | — |
| 27.18 ± 0.4801 | 1.7e+04 | — | — |
| 27.93 ± 0.4862 | 2.2e+04 | — | — |
| 29.94 ± 0.6236 | 2.7e+04 | — | — |
| 28.91 ± 0.7415 | 3.2e+04 | — | — |
| 32.84 ± 0.573 | 3.7e+04 | — | — |
| 32.96 ± 0.4332 | 4.2e+04 | — | — |
| 34.37 ± 0.2606 | 6.7e+04 | 50.01 ± 0.01073 | 0.8347 ± 6.918e-05 |
| 32.45 ± 0.8993 | 7.2e+04 | 49.7 ± 0.04118 | 0.829 ± 0.0002634 |
| 32.15 ± 0.6487 | 7.7e+04 | 49.43 ± 0.0459 | 0.8232 ± 0.000291 |
| 33.45 ± 0.8371 | 8.2e+04 | 49.18 ± 0.07175 | 0.8178 ± 0.0004537 |
| 31.48 ± 1.28 | 8.7e+04 | 48.88 ± 0.04374 | 0.812 ± 0.000272 |
| 29.94 ± 0.9641 | 9.2e+04 | 48.59 ± 0.04409 | 0.8068 ± 0.000272 |
| 31.24 ± 1.188 | 9.7e+04 | 48.33 ± 0.05575 | 0.8012 ± 0.0003406 |
| 31.73 ± 0.3995 | 1.02e+05 | 48.08 ± 0.05318 | 0.7981 ± 0.0003225 |
| 30.29 ± 0.2551 | 1.27e+05 | 48.06 ± 0.01489 | 0.798 ± 9.059e-05 |
| 30.08 ± 0.5442 | 1.32e+05 | 47.54 ± 0.04992 | 0.7912 ± 0.0002993 |
| 27.95 ± 0.9133 | 1.37e+05 | 47.51 ± 0.0775 | 0.7872 ± 0.000462 |
| 27.94 ± 0.9542 | 1.42e+05 | 47.13 ± 0.04279 | 0.7814 ± 0.0002539 |
| 27.88 ± 0.8321 | 1.47e+05 | 46.9 ± 0.0531 | 0.7762 ± 0.0003122 |
| 28.33 ± 0.2754 | 1.72e+05 | 46.82 ± 0.01447 | 0.7758 ± 8.463e-05 |
| 27.77 ± 0.6439 | 1.77e+05 | 46.51 ± 0.04776 | 0.77 ± 0.0002769 |
| 26.71 ± 0.5037 | 1.82e+05 | 46.21 ± 0.06293 | 0.7654 ± 0.0003627 |
| 27.17 ± 0.6873 | 1.87e+05 | 45.83 ± 0.06763 | 0.7593 ± 0.000385 |
| 27.89 ± 0.3265 | 2.12e+05 | 45.8 ± 0.01776 | 0.7592 ± 0.000101 |

Per hold: film vs bulk:

| bulk: max chain COM MSD (Å²) | bulk ρ (g/cm³) | bulk: max segment MSD (Å²) | film: C<sub>n</sub> bond length (Å) | film: C<sub>n</sub> | film: max lag (ps) | film: max chain COM MSD (Å²) | film: chain COM MSD / ⟨R<sub>g</sub>²⟩ at max lag | film: COM MSD log-slope at max lag | film: largest COM MSD log-slope | film: largest ordered cluster, mean (sites) | film: hold length (ns) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 176.9 | 0.8345 ± 8.727e-05 | 815.8 | 1.54 | 12.12 ± 0.2496 | 1.25e+04 | 226.9 | 0.2054 | 0.9025 | 1.883 | 1207 | 25 |
| 396 | 0.7978 ± 7.309e-05 | 1280 | 1.54 | 11.59 ± 0.0421 | 1.25e+04 | 417.5 | 0.3992 | 0.7425 | 1.894 | 130.2 | 25 |
| 522.8 | 0.7758 ± 0.0001085 | 1602 | 1.54 | 10.46 ± 0.1211 | 1.25e+04 | 514.9 | 0.5445 | 0.8757 | 1.9 | 66.12 | 25 |
| 572.5 | 0.7594 ± 9.246e-05 | 1570 | 1.54 | 9.879 ± 0.06527 | 1.25e+04 | 584.8 | 0.652 | 0.7406 | 1.905 | 55.26 | 25 |

Per segment:

| γ drift: second − first half (mN/m) | γ, first half (mN/m) | γ, second half (mN/m) | SEM of the γ drift (mN/m) | potential-energy drift: second − first half | box density (g/cm³) | γ (mN/m) | T (°C) | set T (°C) | SEM of γ from 16 blocks (mN/m) | SEM of γ from 32 blocks (mN/m) | SEM of γ from 8 blocks (mN/m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.7805 | 20.94 | 21.72 | 1.409 | 88.38 | 0.5473 ± 0 | 21.35 ± 0.7542 | 226.8 ± 0.08685 | 226.9 | — | — | — |
| 2.887 | 22.65 | 25.53 | 1.191 | 55.82 | 0.5539 ± 0 | 24.1 ± 0.9296 | 201.7 ± 0.06163 | 201.6 | — | — | — |
| -0.7558 | 26.08 | 25.33 | 0.9213 | -72.46 | 0.5608 ± 0 | 25.71 ± 0.523 | 176.4 ± 0.04591 | 176.4 | — | — | — |
| 0.2044 | 27.08 | 27.29 | 1.255 | 65.81 | 0.5674 ± 0 | 27.18 ± 0.4801 | 151.1 ± 0.04342 | 151.2 | — | — | — |
| 0.2607 | 27.79 | 28.05 | 0.9345 | -19.57 | 0.5742 ± 0 | 27.93 ± 0.4862 | 126 ± 0.08114 | 125.9 | — | — | — |
| 0.2747 | 29.8 | 30.08 | 1.401 | -40.07 | 0.5811 ± 0 | 29.94 ± 0.6236 | 100.6 ± 0.047 | 100.7 | — | — | — |
| 2.448 | 27.68 | 30.13 | 1.064 | -34.43 | 0.5879 ± 0 | 28.91 ± 0.7415 | 75.44 ± 0.03726 | 75.46 | — | — | — |
| 1.088 | 32.3 | 33.39 | 1.013 | 6.566 | 0.5947 ± 0 | 32.84 ± 0.573 | 50.23 ± 0.03451 | 50.23 | — | — | — |
| -0.8975 | 33.4 | 32.51 | 0.8381 | 67.47 | 0.6021 ± 0 | 32.96 ± 0.4332 | 25 ± 0.03132 | 25 | — | — | — |
| 0.4505 | 34.15 | 34.6 | 0.5245 | -114.4 | 0.6019 ± 0 | 34.37 ± 0.2606 | 24.99 ± 0.01112 | 25 | 0.249 | 0.2323 | 0.1421 |
| -3.082 | 33.99 | 30.91 | 1.481 | 59.26 | 0.5992 ± 0 | 32.45 ± 0.8993 | 35.03 ± 0.04371 | 35 | — | — | — |
| -0.1437 | 32.21 | 32.07 | 1.375 | 85.82 | 0.5963 ± 0 | 32.15 ± 0.6487 | 44.97 ± 0.03199 | 45 | — | — | — |
| -0.9225 | 33.91 | 32.99 | 1.799 | -7.338 | 0.5935 ± 0 | 33.45 ± 0.8371 | 55.05 ± 0.03356 | 55 | — | — | — |
| 1.722 | 30.63 | 32.35 | 2.703 | 51.62 | 0.5907 ± 0 | 31.48 ± 1.28 | 64.99 ± 0.03444 | 65 | — | — | — |
| 3.128 | 28.37 | 31.5 | 1.03 | 120.7 | 0.5883 ± 0 | 29.94 ± 0.9641 | 74.94 ± 0.03522 | 75 | — | — | — |
| -3.432 | 32.96 | 29.53 | 1.336 | -10.74 | 0.5852 ± 0 | 31.24 ± 1.188 | 84.99 ± 0.03624 | 85 | — | — | — |
| 1.023 | 31.21 | 32.23 | 0.9912 | 50.75 | 0.5842 ± 0 | 31.73 ± 0.3995 | 89.93 ± 0.03647 | 90 | — | — | — |
| 0.4551 | 30.06 | 30.52 | 0.5153 | 36.54 | 0.5842 ± 0 | 30.29 ± 0.2551 | 89.98 ± 0.01424 | 90 | 0.2182 | 0.2274 | 0.2792 |
| -1.048 | 30.61 | 29.56 | 0.8736 | 13.75 | 0.5814 ± 0 | 30.08 ± 0.5442 | 100 ± 0.06816 | 100 | — | — | — |
| 1.092 | 27.39 | 28.48 | 1.721 | 3.134 | 0.5787 ± 0 | 27.95 ± 0.9133 | 110 ± 0.04061 | 110 | — | — | — |
| 1.709 | 27.08 | 28.79 | 1.672 | 4.031 | 0.576 ± 0 | 27.94 ± 0.9542 | 120 ± 0.04072 | 120 | — | — | — |
| 2.532 | 26.62 | 29.15 | 0.8656 | 41.56 | 0.5732 ± 0 | 27.88 ± 0.8321 | 130 ± 0.04536 | 130 | — | — | — |
| 0.1682 | 28.24 | 28.41 | 0.5518 | 6.52 | 0.5732 ± 0 | 28.33 ± 0.2754 | 130 ± 0.01768 | 130 | 0.2414 | 0.2477 | 0.2073 |
| 0.381 | 27.57 | 27.95 | 1.149 | -3.695 | 0.5703 ± 0 | 27.77 ± 0.6439 | 140 ± 0.04145 | 140 | — | — | — |
| -0.6453 | 27.03 | 26.39 | 0.9828 | -13.84 | 0.5682 ± 0 | 26.71 ± 0.5037 | 150 ± 0.05068 | 150 | — | — | — |
| 1.214 | 26.56 | 27.77 | 1.176 | 64.9 | 0.5653 ± 0 | 27.17 ± 0.6873 | 159.9 ± 0.05815 | 160 | — | — | — |
| 0.5819 | 27.6 | 28.18 | 0.6834 | -28.32 | 0.5653 ± 0 | 27.89 ± 0.3265 | 160 ± 0.01583 | 160 | 0.3493 | 0.2562 | 0.3769 |

- Note: γ uses a plain LJ cutoff without tail correction (D44/D48: `pair_modify tail no`, CG 15 Å, UA/AA 14 Å), so it is cutoff-dependent and lower than a full-dispersion (LJ-PPPM or tail-corrected) value; compare it across our runs, not directly with experiment.
- Note: γ is the mechanical (pressure-tensor) value per surface, (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2] with two film surfaces; the fits are SEM-weighted linear fits in T with errors scaled by √χ²<sub>red</sub> when χ²<sub>red</sub> > 1.
- Note: The slit is a local patch of a pore wall: real separator pores are 30–100 nm and their walls semicrystalline (D50); these walls are amorphous (melt-like or post-shutdown).
- Note: Layers: surface = within 15 Å of either Gibbs surface on the film side (or outside it), interior = the rest, assigned at each time origin; sites leave their layer at long lags, so long-lag layer MSDs mix layers. MSDs are per dimension: in-plane (⟨Δx²⟩+⟨Δy²⟩)/2, normal ⟨Δz²⟩, bulk MSD/3 (isotropic).
- Note: C<sub>v</sub> = dE/dT (total energy, NVT, per gram) and the surface excess energy are classical: C<sub>v</sub> is not comparable to experiment for the same reasons as the bulk C<sub>p</sub> (classical equipartition; UA/CG drop degrees of freedom). e<sub>s</sub> = (E<sub>pore</sub> − (M<sub>pore</sub>/M<sub>bulk</sub>) E<sub>bulk</sub>(T))/(2A) compares the NVT film with the NPT bulk at 1 atm (PV ≈ 0) at the same set T; the film's lateral box follows the bulk density (D48).
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.

</details>

### `pe_cg_pore500k_w12nm_n640_c240_s1_rep441`

PE CG, wide 12 nm slit pore made at 500 K, 640 chains × C240, 51,200 beads; built from `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`). Status: finished: `pore_relax`.

No analysed properties yet. Equilibration: from `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.2610 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: wide pore, nominal 12 nm, wall 6.76 nm, clear gap 1.82 nm, area 731.0 nm²
- Built from: `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`pore_relax`** (rdyu-rog): finished; started 2026-11-06 10:23 UTC, ended 2026-11-06 14:36 UTC; reads `systems/pe_cg_pore500k_w12nm_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| wide | 12 nm (at 500 K) | — | 6.8 nm (500 K) | 27.0 × 27.0 nm (500 K) | — | finished: `pore_relax` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_110C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_110C/hold_110C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4471 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_110C/hold_110C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_120C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_120C/hold_120C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4444 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_120C/hold_120C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_130C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_130C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4417 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_130C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_140C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_140C/hold_140C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4388 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_140C/hold_140C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_150C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_150C/hold_150C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4367 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_150C/hold_150C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_160C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4338 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_25C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_25C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4702 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_25C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_55C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_55C/hold_55C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4618 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_55C/hold_55C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_75C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_75C/hold_75C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4566 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore_75C/hold_75C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_film_90C_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_90C.data`). Stage now: pore (not started).

No analysed properties yet; pending: pore not started. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4525 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_90C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- No runs found.

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: not started | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r2nm_160C_n640_c240_s1_rep441`

PE CG, film with a 2 nm-radius cylindrical hole at 160 °C, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`). Status: finished: `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.1889 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`hole_free`** (rdyu-server): finished; started 2026-11-11 11:40 UTC, ended 2026-11-13 21:58 UTC; reads `systems/pe_cg_hole_r2nm_160C_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | finished: `hole_free` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r3nm_160C_n640_c240_s1_rep441`

PE CG, film with a 3 nm-radius cylindrical hole at 160 °C, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`). Status: finished: `hole_free_gap5nm` (cancelled/killed?, 18.5%), `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.1878 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`hole_free_gap5nm`** (rdyu-rog): cancelled/killed?, 18.5%; started 2026-11-09 07:12 UTC; reads `systems/pe_cg_hole_r3nm_160C_n640_c240_s1_rep441/data.lmp`
- **`hole_free`** (rdyu-rog): finished; started 2026-11-09 19:02 UTC, ended 2026-11-11 21:03 UTC; reads `systems/pe_cg_hole_r3nm_160C_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | finished: `hole_free_gap5nm` (cancelled/killed?, 18.5%), `hole_free` | `hole_free` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 66.59
- `free_shell.areal_density_ratio`: 0.1655
- `free_shell.msd.1 ns`: 527.7
- `free_shell.msd.10 ns`: 2149
- `free_shell.msd.end`: 3633
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `plateau.r_eff`: 85.84
- `plateau.r_eff_sd`: 0.7369
- `plateau.r_min`: 76.48
- T (°C): 160
- `thickness_final`: 103.3
- `thickness_t0`: 92.71

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 67.26 | — |
| 66.85 | — |
| 67.31 | — |
| 66.95 | — |
| 67.18 | — |
| 67.31 | — |
| 67 | — |
| 67.18 | — |
| 66.96 | — |
| 67.01 | — |
| 67.52 | — |
| 67.24 | — |
| 67.39 | — |
| 66.89 | — |
| 66.88 | — |
| 66.51 | — |
| 67.17 | — |
| 67.17 | — |
| 67.37 | — |
| 67.21 | — |
| 66.88 | — |
| 67.19 | — |
| 67.46 | — |
| 67.48 | — |
| 66.89 | — |
| 67.12 | — |
| 67.15 | — |
| 67.1 | — |
| 67.08 | — |
| 67.07 | — |
| 67.2 | — |
| 67.69 | — |
| 67.45 | — |
| 67.2 | — |
| 67.44 | — |
| 67.51 | — |
| 67.12 | — |
| 67.31 | — |
| 67.44 | — |
| 67.39 | — |
| 67.61 | — |
| 67.22 | — |
| 67.3 | — |
| 67.38 | — |
| 67.36 | — |
| 67.48 | — |
| 67.58 | — |
| 68.05 | — |
| 67.52 | — |
| 67.74 | — |
| 67.64 | — |
| 67.76 | — |
| 67.35 | — |
| 68.06 | — |
| 68.15 | — |
| 67.87 | — |
| 67.84 | — |
| 68.23 | — |
| 67.87 | — |
| 67.74 | — |
| 68.05 | — |
| 68.24 | — |
| 68.54 | — |
| 68.03 | — |
| 67.83 | — |
| 68.08 | — |
| 68.15 | — |
| 68.1 | — |
| 67.98 | — |
| 67.81 | — |
| 68.2 | — |
| 68.15 | — |
| 68.11 | — |
| 68.05 | — |
| 68.68 | — |
| 68.1 | — |
| 68.26 | — |
| 68.01 | — |
| 68.55 | — |
| 68.5 | — |
| 68.42 | — |
| 68.09 | — |
| 68.18 | — |
| 67.89 | — |
| 68.67 | — |
| 69.08 | — |
| 68.82 | — |
| 68.53 | — |
| 68.64 | — |
| 68.34 | — |
| 68.37 | — |
| 68.47 | — |
| 68.59 | — |
| 68.72 | — |
| 68.61 | — |
| 68.83 | — |
| 68.63 | — |
| 68.6 | — |
| 69.09 | — |
| 69.04 | — |
| 69.25 | — |
| 69.09 | — |
| 68.82 | — |
| 69.05 | — |
| 69.72 | — |
| 69.03 | — |
| 69.53 | — |
| 68.97 | — |
| 69.68 | — |
| 69.73 | — |
| 69.85 | — |
| 68.79 | — |
| 69.42 | — |
| 69.47 | — |
| 69.26 | — |
| 69.76 | — |
| 69.71 | — |
| 70.25 | — |
| 70.11 | — |
| 70.18 | — |
| 70.31 | — |
| 70.16 | — |
| 70.07 | — |
| 70.18 | — |
| 70.11 | — |
| 70.29 | — |
| 69.79 | — |
| 70.19 | — |
| 70.35 | — |
| 70.8 | — |
| 70.96 | — |
| 70.41 | — |
| 70.63 | — |
| 70.1 | — |
| 70.84 | — |
| 70.48 | — |
| 70.14 | — |
| 70.12 | — |
| 70.32 | — |
| 70.35 | — |
| 70.55 | — |
| 70.72 | — |
| 71.36 | — |
| 70.91 | — |
| 71.6 | — |
| 71.16 | — |
| 70.78 | — |
| 71.14 | — |
| 71.17 | — |
| 71.99 | — |
| 71.55 | — |
| 71.64 | — |
| 71.4 | — |
| 72 | — |
| 72.19 | — |
| 71.03 | — |
| 71.67 | — |
| 72.21 | — |
| 71.77 | — |
| 72.42 | — |
| 72.18 | — |
| 72.12 | — |
| 72.71 | — |
| 71.92 | — |
| 72.46 | — |
| 72.36 | — |
| 72.73 | — |
| 72.52 | — |
| 72.88 | — |
| 71.97 | — |
| 72.51 | — |
| 72.63 | — |
| 72.42 | — |
| 72.72 | — |
| 72.97 | — |
| 73.52 | — |
| 73.13 | — |
| 73.4 | — |
| 73.68 | — |
| 74.02 | — |
| 74.58 | — |
| 74.07 | — |
| 74.23 | — |
| 74.16 | — |
| 73.97 | — |
| 73.95 | — |
| 75.15 | — |
| 74.87 | — |
| 74.93 | — |
| 75.19 | — |
| 75.29 | — |
| 75.01 | — |
| 74.25 | — |
| 75.24 | — |
| 75.15 | — |
| 74.65 | — |
| 75.83 | — |
| 74.91 | — |
| 75.04 | — |
| 74.46 | — |
| 74.91 | — |
| 75.86 | — |
| 76.04 | — |
| 75.2 | — |
| 75.22 | — |
| 75.61 | — |
| 75.89 | — |
| 75.66 | — |
| 74.83 | — |
| 74.84 | — |
| 75.48 | — |
| 76.29 | — |
| 76.18 | — |
| 76.36 | — |
| 76.43 | — |
| 77.01 | — |
| 76.97 | — |
| 77.41 | — |
| 78.31 | — |
| 77.76 | — |
| 78.3 | — |
| 77.77 | — |
| 78.94 | — |
| 78.44 | — |
| 78.45 | — |
| 78.27 | — |
| 77.57 | — |
| 78 | — |
| 78.37 | — |
| 79.02 | — |
| 78.11 | — |
| 77.46 | — |
| 79.2 | — |
| 79.45 | — |
| 78.36 | — |
| 78.39 | — |
| 78.84 | — |
| 78.76 | — |
| 79.15 | — |
| 79.1 | — |
| 79.06 | — |
| 79.51 | — |
| 79.73 | — |
| 79.79 | — |
| 80.46 | — |
| 79.97 | — |
| 79.9 | — |
| 81.02 | — |
| 80.84 | — |
| 81.28 | — |
| 81.61 | — |
| 80.52 | — |
| 80.56 | — |
| 81.22 | — |
| 80.97 | — |
| 81.31 | — |
| 80.73 | — |
| 81.2 | — |
| 81.27 | — |
| 80.99 | — |
| 81.42 | — |
| 81.7 | — |
| 81.29 | — |
| 82.19 | — |
| 82.06 | — |
| 82.27 | — |
| 81.91 | — |
| 82.33 | — |
| 82.08 | — |
| 82.61 | — |
| 82.25 | — |
| 82.66 | — |
| 82.71 | — |
| 82 | — |
| 82.18 | — |
| 82.88 | — |
| 83 | — |
| 83.01 | — |
| 83.95 | — |
| 83.57 | — |
| 83.57 | — |
| 84.21 | — |
| 84.85 | — |
| 84.65 | — |
| 84.39 | — |
| 83.69 | — |
| 82.84 | — |
| 82.94 | — |
| 84.63 | — |
| 84.69 | — |
| 84.33 | — |
| 83.79 | — |
| 84.31 | — |
| 84.07 | — |
| 83.27 | — |
| 83.2 | — |
| 83.84 | — |
| 84.61 | — |
| 83.81 | — |
| 83.3 | — |
| 83.64 | — |
| 84.17 | — |
| 83.15 | — |
| 85.11 | — |
| 85.1 | — |
| 83.94 | — |
| 84.33 | — |
| 84.11 | — |
| 83.6 | — |
| 84.49 | — |
| 84.5 | — |
| 84.81 | — |
| 85.14 | — |
| 85.12 | — |
| 84.75 | — |
| 85.63 | — |
| 85.36 | — |
| 85.58 | — |
| 85.83 | — |
| 85.76 | — |
| 86.87 | — |
| 85.64 | — |
| 85.28 | — |
| 86.84 | — |
| 86.56 | — |
| 86.23 | — |
| 84.17 | — |
| 85.63 | — |
| 86.56 | — |
| 86.18 | — |
| 86.19 | — |
| 86.66 | — |
| 86.6 | — |
| 87.69 | — |
| 87.52 | — |
| 87.35 | — |
| 87.27 | — |
| 87.52 | — |
| 87.1 | — |
| 86.96 | — |
| 88.39 | — |
| 87.37 | — |
| 88.77 | — |
| 88.21 | — |
| 87.95 | — |
| 88.03 | — |
| 88.4 | — |
| 88.8 | — |
| 87.87 | — |
| 88.33 | — |
| 88.15 | — |
| 88.07 | — |
| 88.55 | — |
| 88.69 | — |
| 88.75 | — |
| 89.41 | — |
| 89.41 | — |
| 89.54 | — |
| 88.28 | — |
| 88.54 | — |
| 87.98 | — |
| 89.1 | — |
| 89.64 | — |
| 89.05 | — |
| 89.27 | — |
| 90.45 | — |
| 90.51 | — |
| 90.21 | — |
| 90.16 | — |
| 90.12 | — |
| 91.28 | — |
| 91.29 | — |
| 91.16 | — |
| 89.56 | — |
| 89.57 | — |
| 90.73 | — |
| 90.02 | — |
| 90.51 | — |
| 91.08 | — |
| 91.89 | — |
| 92.45 | — |
| 91 | — |
| 92.12 | — |
| 91.61 | — |
| 91.33 | — |
| 91.3 | — |
| 90.61 | — |
| 91.44 | — |
| 90.37 | — |
| 91.01 | — |
| 90.71 | — |
| 90.05 | — |
| 90.64 | — |
| 90.49 | — |
| 89.71 | — |
| 90.46 | — |
| 90.47 | — |
| 91.2 | — |
| 90.44 | — |
| 90.71 | — |
| 92.71 | 0 |
| 91.92 | 23.22 |
| 92.38 | 37.93 |
| 92.25 | 49.56 |
| 91.47 | 56.5 |
| 91.82 | 65.4 |
| 92.77 | 72.64 |
| 92.42 | 87.03 |
| 92.13 | 94.38 |
| 91.44 | 95.59 |
| 91.08 | 95.34 |
| 90.88 | 109 |
| 90.75 | 113.7 |
| 90.16 | 119.6 |
| 90.14 | 122.8 |
| 90.33 | 128.6 |
| 90.41 | 128.2 |
| 90.23 | 132.7 |
| 89.92 | 141.1 |
| 90.21 | 149.6 |
| 90.16 | 152 |
| 90.27 | 151.2 |
| 89.72 | 157.3 |
| 89.65 | 162.3 |
| 90.62 | 163.1 |
| 91.17 | 166.3 |
| 91.05 | 172.1 |
| 90.84 | 172.5 |
| 91.12 | 175.7 |
| 91.23 | 180 |
| 91.14 | 189.2 |
| 91.65 | 189.9 |
| 92.02 | 191.4 |
| 91.56 | 196.2 |
| 92.2 | 197.3 |
| 93.19 | 188.8 |
| 92.86 | 192.6 |
| 92.32 | 208 |
| 92.91 | 218.9 |
| 92.9 | 223.2 |
| 92.63 | 216.7 |
| 92.6 | 219.6 |
| 92.04 | 216.7 |
| 92.7 | 212.9 |
| 91.6 | 218.4 |
| 91.56 | 226.8 |
| 92.07 | 244.5 |
| 91.72 | 241.2 |
| 91.77 | 246.5 |
| 92.49 | 247.7 |
| 91.84 | 240.8 |
| 91.44 | 229.5 |
| 91.28 | 230.2 |
| 91.91 | 234.1 |
| 91.15 | 229.9 |
| 91.5 | 233.9 |
| 91.08 | 251.5 |
| 90.9 | 262.4 |
| 90.83 | 272.4 |
| 90.98 | 280.4 |
| 91.35 | 290.8 |
| 91.64 | 287.5 |
| 90.92 | 291.2 |
| 91.34 | 291 |
| 91.45 | 293.9 |
| 91.75 | 293.1 |
| 91.22 | 292.8 |
| 91.66 | 293.9 |
| 91.01 | 310 |
| 91.58 | 303.3 |
| 91.43 | 310.4 |
| 92.53 | 297.8 |
| 92.96 | 292.4 |
| 92.74 | 295.8 |
| 92.67 | 293.6 |
| 92.63 | 296.3 |
| 91.93 | 304.6 |
| 92.09 | 310.9 |
| 92.41 | 313.7 |
| 91.96 | 310.9 |
| 92.03 | 330.5 |
| 92.5 | 340.3 |
| 92.55 | 338.3 |
| 91.64 | 342.3 |
| 92.32 | 347.5 |
| 92.83 | 342.3 |
| 93.65 | 355.8 |
| 92.79 | 349.2 |
| 92.62 | 337 |
| 92.62 | 338.4 |
| 92.94 | 349.3 |
| 93.26 | 355 |
| 92.53 | 356 |
| 92.82 | 348.8 |
| 91.66 | 354.9 |
| 92.43 | 360.7 |
| 92.69 | 375.4 |
| 91.11 | 375.8 |
| 92.14 | 388.3 |
| 92.62 | 413.1 |
| 92.44 | 415.6 |
| 92.55 | 425.1 |
| 93.01 | 425.4 |
| 92.45 | 446.4 |
| 92.98 | 456.5 |
| 92.52 | 458.6 |
| 93.31 | 455.4 |
| 93.11 | 470.9 |
| 93.88 | 456.9 |
| 94.66 | 452.5 |
| 93.8 | 448.3 |
| 93.56 | 452.4 |
| 93.61 | 455.1 |
| 93.06 | 461.4 |
| 93.22 | 468.8 |
| 93.43 | 476.7 |
| 93.66 | 479.8 |
| 92.68 | 476.3 |
| 93.28 | 481 |
| 93.21 | 475.6 |
| 92.94 | 482.8 |
| 93.17 | 465.9 |
| 93.17 | 469.8 |
| 93.2 | 482.6 |
| 91.5 | 480.4 |
| 92.06 | 475.7 |
| 91.75 | 474.4 |
| 92.23 | 483.3 |
| 91.44 | 486.2 |
| 92.19 | 500.2 |
| 91.44 | 500.1 |
| 91.85 | 493 |
| 91.8 | 495.1 |
| 91.41 | 489.7 |
| 92.07 | 486.6 |
| 92.04 | 467.7 |
| 91.97 | 450.5 |
| 91.45 | 450.8 |
| 91.57 | 455 |
| 91.57 | 465.2 |
| 91.12 | 459.2 |
| 91.47 | 460.3 |
| 91.44 | 462.1 |
| 91.61 | 469.1 |
| 91.39 | 473.1 |
| 92.09 | 477.5 |
| 91.82 | 471.7 |
| 91.41 | 487.7 |
| 91.89 | 502.6 |
| 92.12 | 493.7 |
| 92.62 | 485.9 |
| 91.49 | 472.4 |
| 91.98 | 461.4 |
| 91.9 | 444.1 |
| 91.94 | 437.1 |
| 92.24 | 454.5 |
| 91.86 | 453.5 |
| 92.07 | 466.9 |
| 92.9 | 467.3 |
| 93.32 | 488.5 |
| 92.44 | 510.5 |
| 92.67 | 507 |
| 92.46 | 479.3 |
| 92.13 | 461.9 |
| 91.67 | 465.1 |
| 92.2 | 470.2 |
| 92.83 | 458.5 |
| 93.06 | 469.4 |
| 92.42 | 468.9 |
| 92.5 | 444.1 |
| 92.45 | 454.7 |
| 92.87 | 462.4 |
| 93.25 | 446.3 |
| 92.32 | 446.4 |
| 92.97 | 451.2 |
| 93.4 | 470.7 |
| 94.07 | 483.6 |
| 94.09 | 517.9 |
| 94.47 | 517 |
| 94.11 | 519.1 |
| 94.34 | 515.5 |
| 93.72 | 497.9 |
| 94.36 | 498.2 |
| 94.9 | 498.8 |
| 93.77 | 504.2 |
| 93.86 | 513.9 |
| 94.07 | 509.5 |
| 94.44 | 506.3 |
| 94.28 | 493.8 |
| 95.2 | 498.6 |
| 94.57 | 509.4 |
| 95.14 | 525.8 |
| 94.87 | 528 |
| 93.97 | 526.6 |
| 94.28 | 528.6 |
| 94.71 | 537.2 |
| 94.53 | 531.9 |
| 94.18 | 527.4 |
| 93.99 | 519.7 |
| 93.95 | 530.6 |
| 93.94 | 527.7 |
| 94 | 542.2 |
| 93.58 | 524.4 |
| 93.27 | 529.1 |
| 93.13 | 537 |
| 93.43 | 537.2 |
| 93.1 | 541.8 |
| 92.68 | 538 |
| 93.61 | 538.3 |
| 92.98 | 542.1 |
| 93.77 | 553.6 |
| 92.6 | 546.7 |
| 92.87 | 550.1 |
| 93.79 | 557.8 |
| 93.1 | 561.9 |
| 94.14 | 575.6 |
| 94 | 565.1 |
| 93.23 | 551.5 |
| 94.32 | 555.6 |
| 93.96 | 573 |
| 92.53 | 569 |
| 93.49 | 559.9 |
| 93.91 | 557.3 |
| 94.07 | 562.8 |
| 94.25 | 566.2 |
| 94.35 | 574.8 |
| 93.9 | 573 |
| 94.12 | 569.4 |
| 93.97 | 566.8 |
| 94.63 | 569.8 |
| 93.96 | 566.4 |
| 94.48 | 593.1 |
| 94.65 | 581.9 |
| 94.05 | 583.9 |
| 94.63 | 578 |
| 93.81 | 551.8 |
| 93.64 | 544.3 |
| 93.95 | 557.4 |
| 93.34 | 549.6 |
| 92.81 | 565.5 |
| 92.68 | 573.8 |
| 92.71 | 582.2 |
| 92.85 | 584.1 |
| 92.65 | 575.5 |
| 93.17 | 580.9 |
| 93.73 | 587.8 |
| 93.78 | 609.9 |
| 93.54 | 623.5 |
| 93.03 | 611.8 |
| 93.43 | 619.8 |
| 93.17 | 633.1 |
| 93.18 | 636.2 |
| 94.14 | 621.5 |
| 93.59 | 612.2 |
| 93.68 | 600.2 |
| 93.7 | 595.6 |
| 94 | 617.6 |
| 94.78 | 613 |
| 94.56 | 616.5 |
| 93.91 | 624.6 |
| 93.92 | 616.9 |
| 94.21 | 586.1 |
| 93.67 | 585.2 |
| 94.27 | 600.5 |
| 93.79 | 600.9 |
| 94.14 | 591.4 |
| 94.19 | 597.2 |
| 94.2 | 587.6 |
| 93.73 | 576.2 |
| 93.98 | 589.9 |
| 93.7 | 596 |
| 94.03 | 607.3 |
| 93.71 | 623.3 |
| 93.41 | 642.9 |
| 93.83 | 631.5 |
| 93.16 | 631.6 |
| 93.34 | 630.1 |
| 93.39 | 633.5 |
| 93.41 | 631.1 |
| 93.12 | 642.5 |
| 93.57 | 631.2 |
| 93.69 | 610.8 |
| 93.98 | 619.9 |
| 93.76 | 619.3 |
| 93.63 | 620.1 |
| 93.57 | 633.2 |
| 93.24 | 624.3 |
| 93.42 | 615.9 |
| 93.59 | 608.9 |
| 93.17 | 626.1 |
| 93.8 | 623.7 |
| 93.71 | 616.9 |
| 93.21 | 624.8 |
| 93.62 | 631.5 |
| 93.64 | 625.4 |
| 93.74 | 644.8 |
| 93.5 | 628.3 |
| 93.72 | 637.1 |
| 93.6 | 643.9 |
| 93.89 | 656.4 |
| 93.53 | 647.3 |
| 93.43 | 657.7 |
| 93.39 | 647.4 |
| 93.94 | 657.6 |
| 94.12 | 654.3 |
| 94.14 | 652.5 |
| 93.24 | 642.7 |
| 94.02 | 628.2 |
| 94.04 | 622 |
| 93.63 | 608.5 |
| 93.03 | 614.7 |
| 93.33 | 600.7 |
| 92.57 | 582.1 |
| 93.25 | 606.3 |
| 92.77 | 618 |
| 92.21 | 606.7 |
| 91.68 | 621.5 |
| 93.04 | 625.5 |
| 93.02 | 640.4 |
| 92.29 | 630.6 |
| 92.74 | 642.8 |
| 93.01 | 653.7 |
| 93.37 | 650.3 |
| 93.81 | 663.4 |
| 93.22 | 691.1 |
| 93.32 | 682.5 |
| 93.57 | 685 |
| 93.87 | 684.6 |
| 93.49 | 678 |
| 92.61 | 672 |
| 92.95 | 687.3 |
| 92.94 | 688.9 |
| 92.9 | 687.1 |
| 92.83 | 697.8 |
| 92.53 | 701.6 |
| 92.74 | 707.6 |
| 93.13 | 715.2 |
| 93.09 | 723.9 |
| 93.62 | 715.4 |
| 94.51 | 718.5 |
| 93.49 | 719.1 |
| 92.42 | 735.8 |
| 93.17 | 757.4 |
| 93.45 | 766.5 |
| 93.6 | 761.3 |
| 93.25 | 749.9 |
| 93.35 | 745.7 |
| 94.12 | 734.4 |
| 94.34 | 728.4 |
| 94.03 | 728.6 |
| 94.91 | 746.7 |
| 93.84 | 763.5 |
| 93.56 | 780.2 |
| 93.96 | 773.3 |
| 93.97 | 771.4 |
| 94.51 | 761.5 |
| 94.44 | 752.2 |
| 94.86 | 742.2 |
| 94.61 | 732.7 |
| 94.46 | 745.5 |
| 95.31 | 745.5 |
| 94.92 | 761.5 |
| 95.16 | 756.5 |
| 94.33 | 747.1 |
| 93.69 | 745.2 |
| 93.47 | 763.6 |
| 93.37 | 770.9 |
| 93.35 | 750 |
| 93.64 | 732.9 |
| 93.29 | 743.4 |
| 94.04 | 755.5 |
| 93.4 | 746.2 |
| 94.57 | 740.2 |
| 93.95 | 738.2 |
| 93.43 | 746.7 |
| 93.19 | 741.8 |
| 93.27 | 759.4 |
| 93.57 | 783.7 |
| 93.36 | 778.2 |
| 93.17 | 777.9 |
| 92.9 | 782.5 |
| 92.5 | 768.2 |
| 91.83 | 750.5 |
| 91.45 | 750.2 |
| 92.71 | 742.7 |
| 92.37 | 759.2 |
| 93.3 | 780.6 |
| 92.81 | 776 |
| 93.6 | 772.7 |
| 93.88 | 798.3 |
| 93.12 | 780 |
| 92.81 | 769.7 |
| 92.98 | 759.2 |
| 92.65 | 759.3 |
| 93.14 | 769.7 |
| 92.46 | 767.7 |
| 93.05 | 775.2 |
| 93.25 | 767.1 |
| 93.23 | 769.4 |
| 93.2 | 770.8 |
| 93.47 | 772.8 |
| 93.76 | 740.1 |
| 92.93 | 802.7 |
| 92.79 | 820.3 |
| 93.47 | 820.3 |
| 93.81 | 757.8 |
| 93.32 | 740.1 |
| 94.07 | 727.6 |
| 93.53 | 763.3 |
| 93.95 | 741.8 |
| 94.4 | 762.3 |
| 95.76 | 774.3 |
| 93.9 | 824 |
| 93.92 | 761.1 |
| 94.24 | 805.3 |
| 95.74 | 787.5 |
| 96.14 | 819.1 |
| 95.9 | 826.6 |
| 95.75 | 907.8 |
| 95.01 | 867.3 |
| 96 | 911.3 |
| 94.97 | 943.3 |
| 94.99 | 973 |
| 95.18 | 992.5 |
| 95.31 | 1005 |
| 94.56 | 1077 |
| 93.95 | 1110 |
| 96.13 | 1112 |
| 94.56 | 1133 |
| 96.96 | 1103 |
| 96.08 | 1171 |
| 96.13 | 1219 |
| 96.2 | 1170 |
| 96.49 | 1213 |
| 95.62 | 1309 |
| 96.07 | 1263 |
| 97.04 | 1250 |
| 95.79 | 1244 |
| 94.78 | 1306 |
| 96.04 | 1405 |
| 95.72 | 1433 |
| 95.81 | 1337 |
| 96.17 | 1325 |
| 95.39 | 1300 |
| 95.85 | 1357 |
| 96.47 | 1351 |
| 94.35 | 1284 |
| 94.51 | 1244 |
| 95.69 | 1266 |
| 95.91 | 1331 |
| 95.35 | 1347 |
| 97.41 | 1384 |
| 97.56 | 1382 |
| 96.6 | 1272 |
| 95.07 | 1221 |
| 95.59 | 1309 |
| 95.83 | 1309 |
| 96.63 | 1296 |
| 95.98 | 1281 |
| 96.55 | 1339 |
| 96.76 | 1292 |
| 96.19 | 1418 |
| 96.96 | 1418 |
| 96.58 | 1426 |
| 97.69 | 1535 |
| 98.03 | 1480 |
| 98.34 | 1488 |
| 97.92 | 1483 |
| 98.39 | 1472 |
| 95.72 | 1467 |
| 95.89 | 1543 |
| 95.61 | 1498 |
| 96.01 | 1500 |
| 96.09 | 1442 |
| 97.47 | 1472 |
| 97.58 | 1569 |
| 97.6 | 1551 |
| 97.37 | 1521 |
| 96.43 | 1561 |
| 95.99 | 1510 |
| 96.47 | 1527 |
| 97.4 | 1609 |
| 98.09 | 1710 |
| 96.75 | 1675 |
| 96.33 | 1812 |
| 96.4 | 1745 |
| 96.1 | 1739 |
| 96.99 | 1839 |
| 97.45 | 1895 |
| 98.86 | 1886 |
| 98.85 | 1877 |
| 98.03 | 1875 |
| 98.11 | 1844 |
| 98.4 | 1950 |
| 99.23 | 1887 |
| 99.65 | 2019 |
| 99.2 | 2012 |
| 99.85 | 2011 |
| 99.67 | 1974 |
| 98.58 | 1974 |
| 99.08 | 2018 |
| 99.58 | 1961 |
| 100.8 | 1963 |
| 100.5 | 1983 |
| 99.02 | 2039 |
| 100.3 | 2085 |
| 100.2 | 2057 |
| 99.43 | 2000 |
| 97.47 | 1925 |
| 97.66 | 1841 |
| 98.34 | 1915 |
| 100.8 | 2009 |
| 100.1 | 1901 |
| 99.84 | 1913 |
| 99.62 | 1966 |
| 99.83 | 2116 |
| 99.75 | 2152 |
| 100 | 2133 |
| 99.06 | 2201 |
| 99.2 | 2270 |
| 98.77 | 2273 |
| 99.33 | 2218 |
| 98.55 | 2195 |
| 99.64 | 2190 |
| 98.53 | 2218 |
| 99.56 | 2231 |
| 99.49 | 2069 |
| 98.81 | 2092 |
| 99.22 | 2129 |
| 99.36 | 2181 |
| 98.82 | 2134 |
| 99.21 | 2106 |
| 98.54 | 2156 |
| 99.44 | 2240 |
| 100.3 | 2269 |
| 100.3 | 2245 |
| 99.43 | 2283 |
| 100.6 | 2299 |
| 98.85 | 2251 |
| 100.5 | 2255 |
| 98.88 | 2344 |
| 99.51 | 2369 |
| 99.36 | 2386 |
| 98.38 | 2383 |
| 100.4 | 2458 |
| 99.65 | 2405 |
| 99.86 | 2438 |
| 99.42 | 2512 |
| 98.61 | 2418 |
| 100.6 | 2267 |
| 100.4 | 2300 |
| 100.8 | 2222 |
| 100.1 | 2104 |
| 99.63 | 2169 |
| 98.66 | 2070 |
| 98.25 | 2013 |
| 99.09 | 2209 |
| 99.53 | 2330 |
| 100 | 2158 |
| 100.1 | 2142 |
| 101.8 | 2149 |
| 101.6 | 2219 |
| 100.5 | 2248 |
| 99.48 | 2263 |
| 100.5 | 2245 |
| 100.2 | 2234 |
| 101.2 | 2286 |
| 100.7 | 2298 |
| 101.2 | 2331 |
| 100.5 | 2215 |
| 99.92 | 2103 |
| 101.6 | 2207 |
| 100.7 | 2234 |
| 100.8 | 2256 |
| 100.6 | 2262 |
| 101.2 | 2291 |
| 99.94 | 2385 |
| 99.98 | 2399 |
| 99.92 | 2374 |
| 99.98 | 2273 |
| 99.66 | 2266 |
| 99.92 | 2258 |
| 100.1 | 2298 |
| 101.8 | 2398 |
| 101.7 | 2464 |
| 100 | 2484 |
| 100.6 | 2499 |
| 100.8 | 2356 |
| 100.7 | 2407 |
| 100.4 | 2383 |
| 99.5 | 2402 |
| 100.7 | 2523 |
| 101.2 | 2557 |
| 99.8 | 2552 |
| 100.1 | 2554 |
| 99.55 | 2391 |
| 101 | 2345 |
| 101.5 | 2292 |
| 101.2 | 2388 |
| 102.5 | 2595 |
| 100.5 | 2370 |
| 100.2 | 2465 |
| 101.7 | 2430 |
| 102.7 | 2439 |
| 99.98 | 2386 |
| 99.9 | 2367 |
| 99.83 | 2396 |
| 100.8 | 2604 |
| 100.8 | 2516 |
| 101.8 | 2529 |
| 100.8 | 2517 |
| 100.7 | 2494 |
| 100.1 | 2523 |
| 101 | 2485 |
| 100.8 | 2503 |
| 100.5 | 2547 |
| 99.51 | 2592 |
| 99.32 | 2522 |
| 99.94 | 2562 |
| 100.1 | 2616 |
| 99.67 | 2613 |
| 99.01 | 2630 |
| 100.1 | 2653 |
| 99.38 | 2708 |
| 100.5 | 2748 |
| 100.7 | 2758 |
| 100.1 | 2631 |
| 100.6 | 2538 |
| 100.6 | 2529 |
| 101.4 | 2454 |
| 99.52 | 2543 |
| 100.4 | 2534 |
| 100.1 | 2583 |
| 101.7 | 2539 |
| 101.9 | 2630 |
| 101.7 | 2598 |
| 100.4 | 2599 |
| 100.3 | 2696 |
| 100.7 | 2604 |
| 100.6 | 2552 |
| 100.1 | 2487 |
| 101.4 | 2607 |
| 100.1 | 2576 |
| 100.1 | 2480 |
| 100.6 | 2599 |
| 100.9 | 2679 |
| 100.1 | 2494 |
| 102.1 | 2468 |
| 101.7 | 2606 |
| 100.9 | 2775 |
| 101.8 | 2680 |
| 101.9 | 2761 |
| 101.2 | 2624 |
| 101 | 2556 |
| 100.1 | 2596 |
| 101 | 2652 |
| 100.9 | 2707 |
| 99.98 | 2683 |
| 101.7 | 2857 |
| 102.5 | 2959 |
| 101.4 | 2953 |
| 102.2 | 3084 |
| 101.9 | 3117 |
| 103.1 | 3132 |
| 102.1 | 3156 |
| 102.9 | 3158 |
| 102.8 | 3147 |
| 103.5 | 3167 |
| 103 | 3102 |
| 102.6 | 3019 |
| 101.8 | 2879 |
| 102 | 2972 |
| 101.8 | 2915 |
| 103.6 | 2899 |
| 103.9 | 2974 |
| 103.1 | 2891 |
| 102.5 | 2848 |
| 104 | 2918 |
| 102.9 | 2937 |
| 102.6 | 2914 |
| 101.6 | 2844 |
| 101.3 | 2946 |
| 101.6 | 3065 |
| 101.6 | 3012 |
| 101.6 | 2961 |
| 101.9 | 2984 |
| 102.8 | 2973 |
| 101.4 | 2889 |
| 101.5 | 2839 |
| 103 | 2965 |
| 102.4 | 2943 |
| 102.3 | 2921 |
| 103.5 | 3005 |
| 103.9 | 3077 |
| 102.6 | 2988 |
| 103 | 2960 |
| 101.7 | 3046 |
| 103.6 | 3092 |
| 103.2 | 3009 |
| 103.5 | 3120 |
| 103.3 | 3063 |
| 103.3 | 3123 |
| 101.6 | 3131 |
| 103.8 | 3017 |
| 102.4 | 2967 |
| 103.1 | 2973 |
| 102.6 | 2757 |
| 101.1 | 2818 |
| 102.5 | 2870 |
| 102.2 | 2926 |
| 102.7 | 2955 |
| 101.7 | 2900 |
| 101.3 | 2988 |
| 102.7 | 2979 |
| 102.3 | 2967 |
| 102.7 | 2978 |
| 102.7 | 2976 |
| 101.2 | 2916 |
| 102.3 | 2983 |
| 102.5 | 2876 |
| 102.6 | 2902 |
| 102.2 | 3030 |
| 103.8 | 3129 |
| 104.2 | 3027 |
| 104.8 | 3080 |
| 104.5 | 2990 |
| 105.3 | 3109 |
| 104.8 | 3172 |
| 104.5 | 3103 |
| 103.3 | 3113 |
| 104.1 | 3138 |
| 102.7 | 3144 |
| 103.9 | 3258 |
| 104.4 | 3186 |
| 104.3 | 3089 |
| 104.4 | 3224 |
| 104.1 | 3187 |
| 102.7 | 3109 |
| 103 | 3085 |
| 103.1 | 3157 |
| 103.7 | 3302 |
| 104 | 3217 |
| 102.7 | 3100 |
| 103 | 3179 |
| 102.8 | 3271 |
| 103.4 | 3200 |
| 104.2 | 3213 |
| 104.3 | 3288 |
| 104.2 | 3274 |
| 103.4 | 3265 |
| 103.7 | 3214 |
| 102.2 | 3135 |
| 102.3 | 3343 |
| 102.1 | 3490 |
| 101.7 | 3491 |
| 101.2 | 3429 |
| 100.2 | 3511 |
| 101.4 | 3550 |
| 103.8 | 3618 |
| 104 | 3636 |
| 103.3 | 3633 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |


</details>

### `pe_cg_hole_r3nm_25C_n640_c240_s1_rep441`

PE CG, film with a 3 nm-radius cylindrical hole at 25 °C, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_25C.data`). Status: finished: `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.2015 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_25C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`hole_free`** (rdyu-rog): finished; started 2026-11-11 21:03 UTC, ended 2026-11-14 00:05 UTC; reads `systems/pe_cg_hole_r3nm_25C_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | finished: `hole_free` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r4nm_160C_n640_c240_s1_rep441`

PE CG, film with a 4 nm-radius cylindrical hole at 160 °C, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`). Stage now: `hole_free` (cancelled/killed?, 77.2%).

No analysed properties yet; pending: `hole_free`: cancelled/killed?, 77.2%. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.1864 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`hole_free_gap5nm`** (rdyu-server): cancelled/killed?, 8.6%; started 2026-11-09 07:12 UTC; reads `systems/pe_cg_hole_r4nm_160C_n640_c240_s1_rep441/data.lmp`
- **`hole_free`** (rdyu-server): cancelled/killed?, 77.2%; started 2026-11-09 19:02 UTC; reads `systems/pe_cg_hole_r4nm_160C_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | `hole_free`: cancelled/killed?, 77.2% | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r5nm_160C_n640_c240_s1_rep441`

PE CG, film with a 5 nm-radius cylindrical hole at 160 °C, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`). Status: finished: `hole_free_gap5nm` (cancelled/killed?, 18.3%), `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.1846 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`hole_free_gap5nm`** (rdyu-rog): cancelled/killed?, 18.3%; started 2026-11-09 07:13 UTC; reads `systems/pe_cg_hole_r5nm_160C_n640_c240_s1_rep441/data.lmp`
- **`hole_free`** (rdyu-rog): finished; started 2026-11-09 19:02 UTC, ended 2026-11-11 21:12 UTC; reads `systems/pe_cg_hole_r5nm_160C_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | finished: `hole_free_gap5nm` (cancelled/killed?, 18.3%), `hole_free` | `hole_free` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 66.59
- `free_shell.areal_density_ratio`: 0.1571
- `free_shell.msd.1 ns`: 606.3
- `free_shell.msd.10 ns`: 2024
- `free_shell.msd.end`: 2665
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `plateau.r_eff`: 85.44
- `plateau.r_eff_sd`: 0.9926
- `plateau.r_min`: 75.93
- T (°C): 160
- `thickness_final`: 104.7
- `thickness_t0`: 95.68

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 67.25 | — |
| 66.82 | — |
| 66.87 | — |
| 66.86 | — |
| 67.15 | — |
| 67.11 | — |
| 66.84 | — |
| 67.17 | — |
| 67.09 | — |
| 66.96 | — |
| 66.97 | — |
| 67.22 | — |
| 67.28 | — |
| 67.55 | — |
| 67.27 | — |
| 67 | — |
| 67.18 | — |
| 67.12 | — |
| 67.34 | — |
| 67.25 | — |
| 67.12 | — |
| 67.06 | — |
| 67.34 | — |
| 67.03 | — |
| 67.2 | — |
| 67.21 | — |
| 67.24 | — |
| 67.46 | — |
| 67.25 | — |
| 67.4 | — |
| 67.58 | — |
| 67.87 | — |
| 67.85 | — |
| 67.69 | — |
| 67.66 | — |
| 67.96 | — |
| 67.72 | — |
| 68.36 | — |
| 68.08 | — |
| 68.16 | — |
| 68.1 | — |
| 68.01 | — |
| 68.2 | — |
| 67.86 | — |
| 68.3 | — |
| 68.19 | — |
| 68.44 | — |
| 68.07 | — |
| 68.13 | — |
| 68.27 | — |
| 68.42 | — |
| 68.36 | — |
| 68.36 | — |
| 67.86 | — |
| 68.79 | — |
| 68.13 | — |
| 68.14 | — |
| 68.84 | — |
| 68.41 | — |
| 68.79 | — |
| 69.28 | — |
| 68.86 | — |
| 68.95 | — |
| 69.09 | — |
| 68.74 | — |
| 68.59 | — |
| 69.02 | — |
| 68.79 | — |
| 68.73 | — |
| 68.53 | — |
| 68.77 | — |
| 69.5 | — |
| 69.92 | — |
| 69.65 | — |
| 70.22 | — |
| 70.02 | — |
| 69.98 | — |
| 69.98 | — |
| 69.96 | — |
| 69.54 | — |
| 69.64 | — |
| 70.36 | — |
| 69.93 | — |
| 70.37 | — |
| 70.69 | — |
| 70.94 | — |
| 70.8 | — |
| 71.31 | — |
| 70.59 | — |
| 70.68 | — |
| 71.31 | — |
| 71.42 | — |
| 70.85 | — |
| 71.42 | — |
| 71.28 | — |
| 71.64 | — |
| 71.3 | — |
| 71.33 | — |
| 71.35 | — |
| 71.23 | — |
| 71.87 | — |
| 71.25 | — |
| 71.74 | — |
| 71.92 | — |
| 72.04 | — |
| 71.93 | — |
| 73.03 | — |
| 72.42 | — |
| 73.01 | — |
| 72.81 | — |
| 72.91 | — |
| 73.05 | — |
| 73.11 | — |
| 72.58 | — |
| 72.73 | — |
| 73.18 | — |
| 73.34 | — |
| 72.71 | — |
| 72.91 | — |
| 73.58 | — |
| 73.67 | — |
| 73.68 | — |
| 74.12 | — |
| 74.18 | — |
| 74.59 | — |
| 74.07 | — |
| 73.76 | — |
| 74.97 | — |
| 74.31 | — |
| 74.63 | — |
| 75.91 | — |
| 75.03 | — |
| 74.92 | — |
| 74.61 | — |
| 74.78 | — |
| 75.55 | — |
| 75.43 | — |
| 75.51 | — |
| 76 | — |
| 76.18 | — |
| 77.01 | — |
| 76.62 | — |
| 76.9 | — |
| 77.31 | — |
| 76.98 | — |
| 76.96 | — |
| 77 | — |
| 78.11 | — |
| 77.63 | — |
| 77.71 | — |
| 77.26 | — |
| 77.37 | — |
| 77.03 | — |
| 76.54 | — |
| 77.82 | — |
| 77.82 | — |
| 78.49 | — |
| 79.23 | — |
| 79.16 | — |
| 79.12 | — |
| 79.47 | — |
| 80.03 | — |
| 80.7 | — |
| 80.49 | — |
| 80.06 | — |
| 78.53 | — |
| 79.22 | — |
| 79.88 | — |
| 80.03 | — |
| 79.61 | — |
| 79.54 | — |
| 80.54 | — |
| 79.72 | — |
| 80.1 | — |
| 80.24 | — |
| 80.54 | — |
| 81.14 | — |
| 80.7 | — |
| 81.48 | — |
| 81.24 | — |
| 82.07 | — |
| 81.54 | — |
| 81.57 | — |
| 81.27 | — |
| 81.78 | — |
| 82.16 | — |
| 82.11 | — |
| 82.7 | — |
| 82.07 | — |
| 82.25 | — |
| 82 | — |
| 81.65 | — |
| 82.13 | — |
| 81.47 | — |
| 82.35 | — |
| 82.88 | — |
| 84.01 | — |
| 82.89 | — |
| 83.57 | — |
| 82.68 | — |
| 82.5 | — |
| 84.03 | — |
| 82.61 | — |
| 82.95 | — |
| 83.52 | — |
| 83.16 | — |
| 84.01 | — |
| 84 | — |
| 84.69 | — |
| 84.75 | — |
| 84.63 | — |
| 84.83 | — |
| 84.1 | — |
| 85.47 | — |
| 84.4 | — |
| 83.88 | — |
| 84.8 | — |
| 85.77 | — |
| 85.41 | — |
| 85.3 | — |
| 85.35 | — |
| 85.48 | — |
| 85.61 | — |
| 84.93 | — |
| 85.51 | — |
| 85.84 | — |
| 85.45 | — |
| 85.83 | — |
| 85.3 | — |
| 86.46 | — |
| 86.48 | — |
| 86.1 | — |
| 86.36 | — |
| 85.51 | — |
| 85.32 | — |
| 86.08 | — |
| 85.77 | — |
| 87.31 | — |
| 86.33 | — |
| 86.19 | — |
| 87.76 | — |
| 87.94 | — |
| 88.17 | — |
| 87.55 | — |
| 88.01 | — |
| 86.93 | — |
| 87.31 | — |
| 87.79 | — |
| 87.41 | — |
| 87.43 | — |
| 87.46 | — |
| 87.54 | — |
| 88.23 | — |
| 88.24 | — |
| 89.2 | — |
| 88.79 | — |
| 88.78 | — |
| 88.62 | — |
| 87.19 | — |
| 86.73 | — |
| 86.54 | — |
| 87.05 | — |
| 87.32 | — |
| 86.95 | — |
| 87.29 | — |
| 87.26 | — |
| 88.11 | — |
| 87.44 | — |
| 87.46 | — |
| 87.45 | — |
| 86.69 | — |
| 87.36 | — |
| 87.05 | — |
| 88.11 | — |
| 87.9 | — |
| 88.1 | — |
| 87.92 | — |
| 87.11 | — |
| 87.81 | — |
| 88.5 | — |
| 88.33 | — |
| 88.75 | — |
| 89.18 | — |
| 89.15 | — |
| 90.02 | — |
| 89.66 | — |
| 90.19 | — |
| 88.76 | — |
| 89.13 | — |
| 89.18 | — |
| 88.51 | — |
| 89.44 | — |
| 89.32 | — |
| 88.94 | — |
| 88.42 | — |
| 87.86 | — |
| 88.07 | — |
| 88.21 | — |
| 88.93 | — |
| 89.98 | — |
| 89.97 | — |
| 89.62 | — |
| 89.74 | — |
| 90.8 | — |
| 90.25 | — |
| 89.01 | — |
| 89.62 | — |
| 89.61 | — |
| 88.59 | — |
| 87.3 | — |
| 87.86 | — |
| 89.06 | — |
| 90.08 | — |
| 89.39 | — |
| 89.35 | — |
| 91.52 | — |
| 90.83 | — |
| 91.01 | — |
| 91.65 | — |
| 90.99 | — |
| 90.17 | — |
| 91.13 | — |
| 89.91 | — |
| 90.45 | — |
| 90.33 | — |
| 89.65 | — |
| 89.32 | — |
| 90.27 | — |
| 90.02 | — |
| 90.64 | — |
| 91.55 | — |
| 90.95 | — |
| 91 | — |
| 89.96 | — |
| 90.68 | — |
| 90.84 | — |
| 92.2 | — |
| 91.92 | — |
| 92.02 | — |
| 91.89 | — |
| 91.95 | — |
| 92.74 | — |
| 91.57 | — |
| 91.73 | — |
| 91.88 | — |
| 91.36 | — |
| 90.38 | — |
| 91.26 | — |
| 90.6 | — |
| 91.24 | — |
| 91.32 | — |
| 91.52 | — |
| 91.68 | — |
| 92.91 | — |
| 92.95 | — |
| 93.3 | — |
| 90.91 | — |
| 92.04 | — |
| 91.9 | — |
| 92.57 | — |
| 91.21 | — |
| 91.83 | — |
| 91.61 | — |
| 91.7 | — |
| 91.87 | — |
| 92.47 | — |
| 92.37 | — |
| 93.26 | — |
| 92.54 | — |
| 93.01 | — |
| 93.14 | — |
| 93.06 | — |
| 92.38 | — |
| 92.6 | — |
| 92.54 | — |
| 92.02 | — |
| 92.01 | — |
| 93.7 | — |
| 92.99 | — |
| 91.31 | — |
| 91.6 | — |
| 92.73 | — |
| 92 | — |
| 93.66 | — |
| 93.67 | — |
| 93.4 | — |
| 93.74 | — |
| 92.58 | — |
| 94.1 | — |
| 93.39 | — |
| 94.12 | — |
| 93.93 | — |
| 95.34 | — |
| 95.39 | — |
| 93.78 | — |
| 93.51 | — |
| 94.6 | — |
| 95.55 | — |
| 94.67 | — |
| 95.51 | — |
| 95.68 | 0 |
| 95.12 | 27.39 |
| 95.4 | 41.31 |
| 95.42 | 56.22 |
| 95.51 | 73.18 |
| 95.83 | 93.61 |
| 95.09 | 102.1 |
| 95.8 | 111.8 |
| 96.05 | 115.8 |
| 95.75 | 123.6 |
| 95.73 | 131.5 |
| 95.99 | 137.5 |
| 95.05 | 146.2 |
| 95.12 | 153.2 |
| 95.02 | 153.5 |
| 95.24 | 159.8 |
| 94.44 | 173 |
| 93.9 | 182.8 |
| 93.27 | 181.1 |
| 94.22 | 185.2 |
| 94.02 | 190.5 |
| 94.23 | 198.2 |
| 94.22 | 210.4 |
| 93.8 | 225.6 |
| 93.7 | 241.9 |
| 94.07 | 250.9 |
| 94.02 | 262.5 |
| 93.92 | 269.8 |
| 95.09 | 276.7 |
| 94.64 | 270.1 |
| 94.46 | 276 |
| 94.38 | 277.3 |
| 94.65 | 279.1 |
| 94.54 | 284.9 |
| 95.14 | 280 |
| 95.6 | 282.5 |
| 94.79 | 284.6 |
| 94.96 | 295.2 |
| 95.66 | 292.6 |
| 95.33 | 294.9 |
| 94.43 | 302.3 |
| 94.49 | 307.3 |
| 94.97 | 314.9 |
| 94.89 | 316.9 |
| 94.84 | 328.3 |
| 95.02 | 337.7 |
| 95.41 | 331.6 |
| 95.57 | 326.9 |
| 95.64 | 329.7 |
| 95.8 | 333.1 |
| 95.82 | 335.1 |
| 95.72 | 336.9 |
| 95.97 | 333.4 |
| 96 | 331.7 |
| 95.04 | 336.8 |
| 94.71 | 348.4 |
| 95 | 355.9 |
| 94.66 | 367.9 |
| 94.81 | 386.4 |
| 95.27 | 400.3 |
| 96.3 | 406.8 |
| 94.99 | 413.4 |
| 95.17 | 410.1 |
| 95.25 | 393.7 |
| 94.85 | 391 |
| 94.6 | 383.7 |
| 95.8 | 387.4 |
| 95.8 | 400.8 |
| 96.08 | 425.3 |
| 95.66 | 429.4 |
| 94.99 | 437.6 |
| 94.85 | 444.6 |
| 94.77 | 435.6 |
| 94.41 | 442.9 |
| 94.88 | 448.4 |
| 94.44 | 452.1 |
| 95.07 | 449.9 |
| 94.81 | 441.1 |
| 94.74 | 444.6 |
| 94.91 | 435.7 |
| 94.84 | 445 |
| 94.96 | 447.5 |
| 94.92 | 441 |
| 95.05 | 434.8 |
| 95.48 | 426.1 |
| 95.11 | 431.7 |
| 95.38 | 451 |
| 95.35 | 449 |
| 94.9 | 438.4 |
| 94.85 | 444.5 |
| 94.44 | 447.7 |
| 94.74 | 461.1 |
| 94.45 | 471.3 |
| 93.67 | 478.9 |
| 94.4 | 489 |
| 94.97 | 485.8 |
| 94.04 | 476.4 |
| 94.34 | 472.7 |
| 94.23 | 473 |
| 94.51 | 467.7 |
| 94.34 | 477 |
| 94.57 | 473.6 |
| 94.91 | 486.9 |
| 94.59 | 498.3 |
| 94.24 | 491.5 |
| 94.27 | 468.9 |
| 93.64 | 460.8 |
| 93.82 | 459.4 |
| 94.91 | 465.7 |
| 94.91 | 470.1 |
| 95.05 | 471.9 |
| 95.05 | 477.4 |
| 94.99 | 474.8 |
| 95.24 | 476 |
| 94.83 | 470.2 |
| 94.99 | 462.7 |
| 94.59 | 461.2 |
| 94.44 | 457.4 |
| 94.98 | 460.3 |
| 94.82 | 456.5 |
| 94.79 | 464.1 |
| 94.34 | 468.1 |
| 94.23 | 478.4 |
| 93.88 | 474.9 |
| 94.66 | 474.2 |
| 94.41 | 483 |
| 94.78 | 501.3 |
| 94.85 | 513.2 |
| 94.77 | 505.4 |
| 94.73 | 504.6 |
| 95.01 | 511.8 |
| 94.97 | 512.5 |
| 94.91 | 501.5 |
| 94.93 | 497.6 |
| 94.77 | 503.6 |
| 94.94 | 493.7 |
| 95.29 | 505.3 |
| 94.7 | 510.1 |
| 94.36 | 497.5 |
| 95.06 | 503.3 |
| 94.63 | 506 |
| 94.76 | 514.6 |
| 94.79 | 510.6 |
| 94.07 | 507.9 |
| 94.39 | 508.3 |
| 94.86 | 500.9 |
| 94.48 | 494.8 |
| 94.3 | 487 |
| 94.6 | 506.5 |
| 94.69 | 512.1 |
| 95.02 | 514.4 |
| 95.62 | 521.3 |
| 95.66 | 524.1 |
| 94.57 | 523.8 |
| 94.83 | 527.1 |
| 95.53 | 526.3 |
| 94.76 | 535.9 |
| 94.85 | 536.7 |
| 95.09 | 541.6 |
| 94.17 | 541.2 |
| 94.27 | 546.1 |
| 93.74 | 538.6 |
| 92.87 | 544.7 |
| 93.71 | 551 |
| 92.79 | 557.2 |
| 92.51 | 546.7 |
| 93.2 | 552.9 |
| 92.9 | 565.6 |
| 93.39 | 568.1 |
| 93.5 | 582.6 |
| 93.92 | 585 |
| 93.78 | 596.3 |
| 93.85 | 583.3 |
| 94.3 | 596.5 |
| 94.46 | 596 |
| 93.94 | 592.3 |
| 94.26 | 592.4 |
| 94.44 | 579 |
| 92.91 | 561.5 |
| 93.28 | 552.1 |
| 92.85 | 545.6 |
| 93.43 | 545.3 |
| 93.55 | 546.2 |
| 93.34 | 560.3 |
| 93.82 | 567.5 |
| 93.32 | 573.5 |
| 94.38 | 586.1 |
| 94.44 | 588.9 |
| 94.51 | 578.6 |
| 94.01 | 579.7 |
| 94.65 | 588.5 |
| 94.37 | 594.9 |
| 94.67 | 584.2 |
| 95.16 | 591.6 |
| 94.8 | 583.9 |
| 95.53 | 579.9 |
| 94.93 | 583.3 |
| 95.76 | 594 |
| 95 | 596.2 |
| 94.91 | 596 |
| 95.67 | 606.3 |
| 95.31 | 616 |
| 95.71 | 632.3 |
| 95.27 | 633.6 |
| 95.81 | 627.3 |
| 95.45 | 649.8 |
| 95.28 | 650.9 |
| 95.56 | 655.9 |
| 95.68 | 673.6 |
| 95.75 | 681.6 |
| 95.43 | 667.9 |
| 95.67 | 671.1 |
| 95.8 | 658.2 |
| 95.09 | 682.5 |
| 95.15 | 672.7 |
| 95.28 | 694.7 |
| 95.31 | 698 |
| 95.3 | 696.8 |
| 94.79 | 693.7 |
| 95.34 | 682.4 |
| 94.39 | 676.6 |
| 95.13 | 678.5 |
| 95.73 | 680.8 |
| 94.58 | 692.4 |
| 95.14 | 710.1 |
| 94.61 | 713.8 |
| 93.92 | 709.6 |
| 93.82 | 695.8 |
| 93.78 | 688.6 |
| 92.93 | 689 |
| 93.75 | 693.4 |
| 94.28 | 701.8 |
| 94.2 | 702.3 |
| 94.22 | 704.5 |
| 94.82 | 721.3 |
| 95.32 | 721.1 |
| 95.1 | 713.2 |
| 95.21 | 717.7 |
| 94.97 | 703.8 |
| 94.99 | 696.2 |
| 94.99 | 693.6 |
| 94.77 | 697.6 |
| 94.14 | 687.7 |
| 94.33 | 680.3 |
| 94.24 | 678.2 |
| 94.24 | 690.6 |
| 93.9 | 687.6 |
| 94.33 | 677.6 |
| 93.85 | 688.7 |
| 94.25 | 700.7 |
| 93.62 | 703.2 |
| 94.33 | 716.4 |
| 94.18 | 733 |
| 94.15 | 750.4 |
| 94.13 | 755.5 |
| 93.8 | 756 |
| 95.02 | 772.9 |
| 94.68 | 781.8 |
| 93.85 | 787.5 |
| 93.95 | 791.7 |
| 95.2 | 777 |
| 95.11 | 782.6 |
| 95.04 | 773.2 |
| 94.88 | 766.9 |
| 94.46 | 764.4 |
| 94.58 | 750.8 |
| 94.59 | 742.8 |
| 94.77 | 732.9 |
| 94.95 | 721.9 |
| 95.34 | 716.3 |
| 95.34 | 717.4 |
| 95.9 | 734.9 |
| 95.04 | 715.2 |
| 94.79 | 699.6 |
| 94.92 | 695.2 |
| 95.03 | 689.4 |
| 94.77 | 689.9 |
| 95.07 | 692.7 |
| 94.86 | 678 |
| 94.67 | 678.5 |
| 94.32 | 685.2 |
| 94.63 | 687.6 |
| 95.6 | 682.1 |
| 95.03 | 691.1 |
| 95.62 | 699.4 |
| 95.76 | 719.9 |
| 95.64 | 715.2 |
| 95.2 | 718.6 |
| 96.29 | 731.5 |
| 95.56 | 737.2 |
| 96.51 | 727.7 |
| 96.15 | 724.6 |
| 96.54 | 724.5 |
| 95.46 | 717.2 |
| 96.29 | 716.4 |
| 95.41 | 704.7 |
| 95 | 696.7 |
| 95.04 | 682.8 |
| 94.85 | 690.9 |
| 94.84 | 698.7 |
| 96.3 | 696.6 |
| 95.28 | 696.1 |
| 97.12 | 704 |
| 96.87 | 693.2 |
| 96.21 | 697.1 |
| 95.69 | 697.1 |
| 95.61 | 699.6 |
| 95.73 | 702 |
| 95.37 | 711.4 |
| 95.79 | 711 |
| 95.48 | 712.8 |
| 95.93 | 724.8 |
| 95.61 | 735.7 |
| 96.15 | 739.9 |
| 97.12 | 751.8 |
| 97.25 | 756 |
| 97.39 | 742.3 |
| 97.83 | 734.7 |
| 97.56 | 727.6 |
| 97.27 | 740.2 |
| 97.13 | 747.7 |
| 97.49 | 752.1 |
| 97.62 | 755.9 |
| 96.67 | 768.4 |
| 97.22 | 767.6 |
| 96.85 | 769.5 |
| 96.64 | 760.5 |
| 96.34 | 772.9 |
| 96.22 | 785.1 |
| 96.07 | 788.9 |
| 96.31 | 783.8 |
| 95.53 | 788.9 |
| 95.54 | 800.9 |
| 96.02 | 803.5 |
| 95.86 | 826.6 |
| 96.21 | 828.5 |
| 95.6 | 840.2 |
| 95.91 | 849.3 |
| 95.31 | 870.8 |
| 94.93 | 881.1 |
| 94.84 | 858 |
| 94.89 | 850.6 |
| 94.62 | 854.6 |
| 94.65 | 858.7 |
| 95.27 | 850.8 |
| 95.41 | 842 |
| 94.95 | 834.5 |
| 95.46 | 827.3 |
| 95.7 | 820.7 |
| 94.48 | 812 |
| 95.11 | 813.3 |
| 95.95 | 803.3 |
| 94.69 | 808.7 |
| 95.28 | 824 |
| 95.7 | 805.8 |
| 95.81 | 812.2 |
| 95.38 | 823.2 |
| 95.54 | 820.9 |
| 95.73 | 817.7 |
| 95.17 | 827.1 |
| 95.28 | 834.4 |
| 95.38 | 820.7 |
| 94.97 | 807.7 |
| 94.47 | 814.7 |
| 94.47 | 815.6 |
| 94.17 | 809.5 |
| 93.96 | 801.4 |
| 94.22 | 813.4 |
| 95.05 | 791.6 |
| 95.63 | 783.1 |
| 95.48 | 769.8 |
| 95.87 | 767.5 |
| 96.51 | 762.3 |
| 96.23 | 753.6 |
| 96.54 | 753.1 |
| 96.32 | 750.3 |
| 96.69 | 752.4 |
| 96.55 | 745.2 |
| 97.07 | 761.2 |
| 97.36 | 741.9 |
| 97.75 | 727.9 |
| 96.91 | 737.7 |
| 96.61 | 745.8 |
| 96.68 | 748.6 |
| 96.19 | 743.5 |
| 95.93 | 738.7 |
| 96.76 | 742 |
| 96.65 | 751.7 |
| 96.09 | 764.6 |
| 95.95 | 778.5 |
| 96.81 | 775.8 |
| 96.17 | 778.7 |
| 96.03 | 779.3 |
| 94.92 | 773.1 |
| 94.85 | 783.5 |
| 95.13 | 770.8 |
| 95.15 | 777.6 |
| 95.6 | 784.8 |
| 95.72 | 789 |
| 95.35 | 795.8 |
| 94.81 | 804.8 |
| 94.9 | 837.8 |
| 94.89 | 819 |
| 95.23 | 898.7 |
| 94.63 | 949.1 |
| 94.53 | 954.1 |
| 96.44 | 1100 |
| 96.36 | 1034 |
| 95.51 | 1012 |
| 96.69 | 960 |
| 96.84 | 1013 |
| 96.94 | 1024 |
| 95.99 | 1047 |
| 95.82 | 1018 |
| 96.06 | 1031 |
| 95.85 | 1070 |
| 97.18 | 1088 |
| 96.33 | 1036 |
| 96.51 | 1124 |
| 97.68 | 1112 |
| 96.16 | 1067 |
| 96.85 | 1054 |
| 98.74 | 988.4 |
| 97.3 | 996.8 |
| 98.05 | 1110 |
| 96.99 | 1083 |
| 96.44 | 1061 |
| 97.62 | 1127 |
| 98.61 | 1020 |
| 97.42 | 941.4 |
| 98.14 | 1021 |
| 97.83 | 1065 |
| 96.58 | 1081 |
| 97.57 | 1097 |
| 97.67 | 1165 |
| 97.01 | 1079 |
| 95.81 | 1002 |
| 97.84 | 1040 |
| 97.29 | 1110 |
| 96.89 | 1167 |
| 97.27 | 1170 |
| 96.74 | 1197 |
| 97.04 | 1150 |
| 96.77 | 1166 |
| 97.32 | 1193 |
| 97.97 | 1242 |
| 97.19 | 1192 |
| 98.18 | 1235 |
| 97.16 | 1279 |
| 97.44 | 1298 |
| 96.28 | 1375 |
| 98.3 | 1341 |
| 97.8 | 1334 |
| 97.49 | 1370 |
| 97.66 | 1442 |
| 97.98 | 1559 |
| 96.98 | 1509 |
| 98.76 | 1450 |
| 98.03 | 1403 |
| 97.13 | 1370 |
| 97.62 | 1407 |
| 98.11 | 1404 |
| 97.88 | 1364 |
| 96.98 | 1378 |
| 96.13 | 1370 |
| 96.99 | 1398 |
| 97.49 | 1471 |
| 98.02 | 1508 |
| 97.83 | 1508 |
| 97.3 | 1491 |
| 97.74 | 1515 |
| 98.19 | 1445 |
| 98.27 | 1531 |
| 97.32 | 1527 |
| 97.62 | 1515 |
| 97.91 | 1412 |
| 97.97 | 1342 |
| 98.97 | 1377 |
| 99.13 | 1416 |
| 98.8 | 1407 |
| 99.3 | 1312 |
| 98.34 | 1351 |
| 99.39 | 1393 |
| 99.84 | 1402 |
| 97.7 | 1366 |
| 96.76 | 1334 |
| 97.25 | 1353 |
| 96.52 | 1451 |
| 98.09 | 1506 |
| 97.78 | 1514 |
| 97.86 | 1474 |
| 97.07 | 1523 |
| 98.74 | 1531 |
| 98.89 | 1506 |
| 99.93 | 1507 |
| 99.41 | 1510 |
| 98.06 | 1519 |
| 99.27 | 1670 |
| 99.45 | 1646 |
| 98.82 | 1623 |
| 99.57 | 1579 |
| 97.71 | 1523 |
| 96.44 | 1532 |
| 98.21 | 1589 |
| 98.26 | 1599 |
| 97.97 | 1670 |
| 98.45 | 1729 |
| 97.59 | 1699 |
| 98.9 | 1837 |
| 99.01 | 1755 |
| 97.9 | 1807 |
| 98.05 | 1820 |
| 97.99 | 1749 |
| 98.15 | 1678 |
| 98.43 | 1632 |
| 97.59 | 1689 |
| 99.11 | 1747 |
| 98.25 | 1731 |
| 97.59 | 1730 |
| 97.94 | 1726 |
| 98.78 | 1748 |
| 98.71 | 1763 |
| 99.8 | 1735 |
| 100.6 | 1730 |
| 99.78 | 1740 |
| 99.76 | 1723 |
| 98.85 | 1678 |
| 97.28 | 1795 |
| 98.03 | 1811 |
| 97.53 | 1844 |
| 98.19 | 1783 |
| 100.2 | 1767 |
| 99.48 | 1773 |
| 97.44 | 1770 |
| 98.52 | 1798 |
| 98.95 | 1778 |
| 99.33 | 1776 |
| 98.65 | 1810 |
| 97.83 | 1883 |
| 98.33 | 1943 |
| 99.69 | 1931 |
| 99.06 | 1885 |
| 98.71 | 1951 |
| 99.33 | 1935 |
| 99.56 | 1957 |
| 99.34 | 1959 |
| 99.37 | 1908 |
| 99.93 | 1925 |
| 99.18 | 1932 |
| 100.1 | 1998 |
| 100.1 | 1923 |
| 99.86 | 1991 |
| 101.4 | 2074 |
| 99.07 | 2061 |
| 99.37 | 2104 |
| 99.17 | 2103 |
| 100.1 | 2074 |
| 99.02 | 2041 |
| 99.29 | 1980 |
| 99.23 | 2040 |
| 98.74 | 2024 |
| 99.47 | 2062 |
| 97.67 | 1975 |
| 98.81 | 1991 |
| 97.48 | 1924 |
| 98.44 | 1904 |
| 98.52 | 1940 |
| 99.71 | 2011 |
| 99.57 | 2078 |
| 98.54 | 2116 |
| 98.7 | 2172 |
| 98.4 | 2071 |
| 98.3 | 2021 |
| 97.68 | 1950 |
| 100.3 | 1989 |
| 99 | 1966 |
| 98.19 | 1962 |
| 99.04 | 2045 |
| 99.07 | 2045 |
| 99.97 | 2136 |
| 101.7 | 2178 |
| 102 | 2213 |
| 100.7 | 2077 |
| 100.4 | 2043 |
| 99.98 | 1998 |
| 99.33 | 2091 |
| 99.73 | 2168 |
| 101.2 | 2203 |
| 99.95 | 2252 |
| 101.5 | 2202 |
| 99.19 | 2199 |
| 98.78 | 2103 |
| 97.91 | 2078 |
| 97.25 | 2130 |
| 98.13 | 2194 |
| 99.3 | 2235 |
| 100.6 | 2171 |
| 99.33 | 2185 |
| 98.32 | 2221 |
| 101.2 | 2243 |
| 101.3 | 2216 |
| 99.12 | 2217 |
| 99.48 | 2163 |
| 100.5 | 2238 |
| 100.2 | 2265 |
| 100.5 | 2308 |
| 101.3 | 2262 |
| 100.6 | 2216 |
| 99.58 | 2088 |
| 99.47 | 2036 |
| 99.37 | 2089 |
| 99.43 | 2202 |
| 100.2 | 2168 |
| 100.5 | 2133 |
| 100.5 | 2149 |
| 99.88 | 2206 |
| 99.8 | 2285 |
| 99.48 | 2357 |
| 99.96 | 2320 |
| 100.3 | 2275 |
| 99.28 | 2247 |
| 99.27 | 2352 |
| 101.2 | 2423 |
| 99.35 | 2466 |
| 98.7 | 2332 |
| 99 | 2296 |
| 100.7 | 2519 |
| 102.3 | 2493 |
| 99.8 | 2349 |
| 101.6 | 2332 |
| 100.8 | 2402 |
| 100.8 | 2443 |
| 100.3 | 2327 |
| 101.7 | 2434 |
| 104.3 | 2461 |
| 103.7 | 2514 |
| 103.2 | 2413 |
| 101.4 | 2320 |
| 101.8 | 2346 |
| 102.4 | 2236 |
| 102.3 | 2225 |
| 100.9 | 2235 |
| 100.9 | 2281 |
| 101 | 2315 |
| 104.3 | 2422 |
| 103 | 2476 |
| 103.4 | 2510 |
| 103 | 2484 |
| 103.1 | 2429 |
| 102.5 | 2421 |
| 101.6 | 2404 |
| 101.4 | 2339 |
| 102.4 | 2309 |
| 101 | 2448 |
| 103.6 | 2505 |
| 101.9 | 2536 |
| 100.9 | 2490 |
| 102 | 2532 |
| 101.5 | 2552 |
| 102.5 | 2604 |
| 100.6 | 2535 |
| 101.3 | 2544 |
| 100.4 | 2588 |
| 102.1 | 2622 |
| 102.1 | 2682 |
| 101.8 | 2628 |
| 101 | 2620 |
| 100.3 | 2623 |
| 101.7 | 2638 |
| 100.7 | 2618 |
| 102.2 | 2583 |
| 100.7 | 2552 |
| 100.3 | 2565 |
| 101.1 | 2566 |
| 101.1 | 2584 |
| 101.9 | 2562 |
| 100.7 | 2628 |
| 102.6 | 2646 |
| 102.5 | 2669 |
| 102.9 | 2676 |
| 102.2 | 2595 |
| 100.3 | 2559 |
| 101.4 | 2572 |
| 101.2 | 2585 |
| 101.6 | 2649 |
| 100.8 | 2624 |
| 99.82 | 2513 |
| 100 | 2607 |
| 100 | 2565 |
| 99.87 | 2506 |
| 99.36 | 2483 |
| 99.53 | 2451 |
| 100.3 | 2417 |
| 100.3 | 2456 |
| 99.98 | 2500 |
| 100.7 | 2482 |
| 101.2 | 2497 |
| 100.2 | 2526 |
| 101.1 | 2541 |
| 102.3 | 2553 |
| 102 | 2481 |
| 102.1 | 2400 |
| 101.8 | 2361 |
| 101.8 | 2441 |
| 100.5 | 2431 |
| 103.1 | 2502 |
| 102 | 2526 |
| 101.5 | 2582 |
| 101.1 | 2655 |
| 102.1 | 2649 |
| 103 | 2630 |
| 101.9 | 2565 |
| 102 | 2695 |
| 102.3 | 2592 |
| 101.6 | 2630 |
| 103.5 | 2612 |
| 102.8 | 2525 |
| 102.8 | 2582 |
| 101.9 | 2534 |
| 102.9 | 2553 |
| 104.1 | 2676 |
| 103 | 2680 |
| 103.9 | 2628 |
| 103.3 | 2592 |
| 102.9 | 2490 |
| 103.1 | 2479 |
| 104.3 | 2575 |
| 103.2 | 2562 |
| 103 | 2463 |
| 102 | 2501 |
| 104.1 | 2408 |
| 103.1 | 2479 |
| 101.8 | 2449 |
| 101.2 | 2475 |
| 102.9 | 2512 |
| 102.3 | 2587 |
| 103.6 | 2499 |
| 102.3 | 2451 |
| 103.8 | 2545 |
| 103.4 | 2552 |
| 103.1 | 2683 |
| 102.8 | 2657 |
| 104.8 | 2746 |
| 103.4 | 2855 |
| 103.7 | 2835 |
| 103.2 | 2759 |
| 101.7 | 2619 |
| 102.1 | 2687 |
| 102 | 2682 |
| 103.7 | 2708 |
| 103.1 | 2618 |
| 104.4 | 2660 |
| 104 | 2634 |
| 103.6 | 2731 |
| 103.7 | 2654 |
| 103.8 | 2680 |
| 104.2 | 2663 |
| 103.8 | 2650 |
| 103.6 | 2653 |
| 102.6 | 2598 |
| 104.7 | 2665 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |


</details>

### `pe_cg_hole_r5nm_25C_n640_c240_s1_rep441`

PE CG, film with a 5 nm-radius cylindrical hole at 25 °C, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_25C.data`). Status: finished: `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.1979 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_25C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`hole_free`** (rdyu-rog): finished; started 2026-11-11 21:12 UTC, ended 2026-11-14 00:25 UTC; reads `systems/pe_cg_hole_r5nm_25C_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | finished: `hole_free` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r6nm_160C_n640_c240_s1_rep441`

PE CG, film with a 6 nm-radius cylindrical hole at 160 °C, 640 chains × C240, 51,200 beads; built from `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`). Status: finished: `hole_free_gap5nm` (cancelled/killed?, 18.4%), `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.1824 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore_w5nm_n640_c240_s1_rep441` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n640_c240_s1_rep441` ← `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **`hole_free_gap5nm`** (rdyu-rog): cancelled/killed?, 18.4%; started 2026-11-09 07:14 UTC; reads `systems/pe_cg_hole_r6nm_160C_n640_c240_s1_rep441/data.lmp`
- **`hole_free`** (rdyu-rog): finished; started 2026-11-09 19:02 UTC, ended 2026-11-11 22:34 UTC; reads `systems/pe_cg_hole_r6nm_160C_n640_c240_s1_rep441/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | finished: `hole_free_gap5nm` (cancelled/killed?, 18.4%), `hole_free` | `hole_free` |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`hole_free` analysis**

Pore analysis (`sepsim analyze pore`, generated — on —):

- `film_thickness_angstrom`: 66.59
- `free_shell.areal_density_ratio`: 0.2484
- `free_shell.msd.1 ns`: 565.3
- `free_shell.msd.10 ns`: 1620
- `free_shell.msd.end`: 2862
- `free_shell.msd.end_ns`: 20
- `params.hole_grid_c`: 
- `params.hole_hold_ps`: 2e+04
- `params.release_t_c`: none
- `params.scaffold_d_nm`: 2.5
- `params.scaffold_hold_ps`: 0
- `params.scaffold_k`: 5
- `params.wall_hold_ps`: 1e+04
- `plateau.r_eff`: 87.58
- `plateau.r_eff_sd`: 1.106
- `plateau.r_min`: 77.96
- T (°C): 160
- `thickness_final`: 106.8
- `thickness_t0`: 98.2

`frames`:

| `thickness` | `shell_msd` |
|---|---|
| 67.26 | — |
| 67.21 | — |
| 67.75 | — |
| 67.25 | — |
| 67.78 | — |
| 66.96 | — |
| 67.21 | — |
| 67.01 | — |
| 67.39 | — |
| 67.27 | — |
| 66.93 | — |
| 67.56 | — |
| 67.03 | — |
| 66.9 | — |
| 67.06 | — |
| 67.41 | — |
| 67.47 | — |
| 67.54 | — |
| 67.41 | — |
| 67.59 | — |
| 67.56 | — |
| 67.6 | — |
| 67.19 | — |
| 67.65 | — |
| 67.46 | — |
| 67.21 | — |
| 67.72 | — |
| 67.59 | — |
| 67.47 | — |
| 67.68 | — |
| 67.47 | — |
| 67.34 | — |
| 67.77 | — |
| 67.93 | — |
| 68.3 | — |
| 67.81 | — |
| 68.32 | — |
| 68.32 | — |
| 68.12 | — |
| 68.55 | — |
| 67.69 | — |
| 67.61 | — |
| 68.24 | — |
| 68.91 | — |
| 68.8 | — |
| 68.29 | — |
| 68.07 | — |
| 68.61 | — |
| 68.59 | — |
| 68.53 | — |
| 68.65 | — |
| 68.63 | — |
| 68.85 | — |
| 68.49 | — |
| 68.69 | — |
| 69.17 | — |
| 69.14 | — |
| 69.19 | — |
| 69.28 | — |
| 69.47 | — |
| 69.25 | — |
| 69.29 | — |
| 68.91 | — |
| 69.07 | — |
| 69.38 | — |
| 69.36 | — |
| 69.27 | — |
| 69.23 | — |
| 69.56 | — |
| 69.75 | — |
| 69.93 | — |
| 69.73 | — |
| 70.24 | — |
| 70.15 | — |
| 69.83 | — |
| 71.28 | — |
| 71.16 | — |
| 70.89 | — |
| 71.18 | — |
| 70.9 | — |
| 71.26 | — |
| 70.87 | — |
| 71 | — |
| 70.81 | — |
| 71.38 | — |
| 71.6 | — |
| 71.42 | — |
| 71.54 | — |
| 71.5 | — |
| 71.9 | — |
| 72.62 | — |
| 72.46 | — |
| 72.64 | — |
| 72.31 | — |
| 72.93 | — |
| 72.94 | — |
| 72.59 | — |
| 72.51 | — |
| 73.06 | — |
| 73.06 | — |
| 73.23 | — |
| 72.74 | — |
| 72.99 | — |
| 73.16 | — |
| 73.3 | — |
| 73.43 | — |
| 73.22 | — |
| 73.98 | — |
| 74.1 | — |
| 73.75 | — |
| 73.69 | — |
| 73.94 | — |
| 74.24 | — |
| 74.35 | — |
| 74.06 | — |
| 74.88 | — |
| 74.64 | — |
| 74.25 | — |
| 74.57 | — |
| 75.3 | — |
| 75.19 | — |
| 75.21 | — |
| 75.21 | — |
| 75.92 | — |
| 75.42 | — |
| 75.22 | — |
| 75.81 | — |
| 75.84 | — |
| 76.4 | — |
| 76.38 | — |
| 76.67 | — |
| 76.65 | — |
| 77.23 | — |
| 76.65 | — |
| 76.15 | — |
| 77.25 | — |
| 76.66 | — |
| 76.99 | — |
| 77.37 | — |
| 78.21 | — |
| 78.66 | — |
| 78.47 | — |
| 78.57 | — |
| 77.74 | — |
| 78.53 | — |
| 78.99 | — |
| 79.18 | — |
| 79.08 | — |
| 79.19 | — |
| 78.69 | — |
| 79.57 | — |
| 80.24 | — |
| 80.38 | — |
| 80.7 | — |
| 80.36 | — |
| 80.51 | — |
| 80.92 | — |
| 81.07 | — |
| 81.77 | — |
| 81.96 | — |
| 81.68 | — |
| 81.43 | — |
| 82.06 | — |
| 82.42 | — |
| 82.12 | — |
| 82.84 | — |
| 83.11 | — |
| 83.17 | — |
| 82.17 | — |
| 82.01 | — |
| 82.72 | — |
| 82.44 | — |
| 82.31 | — |
| 83.14 | — |
| 83.04 | — |
| 83.14 | — |
| 83.76 | — |
| 83.81 | — |
| 84.5 | — |
| 84.29 | — |
| 84.34 | — |
| 85.09 | — |
| 85.43 | — |
| 85.68 | — |
| 86.29 | — |
| 85.8 | — |
| 85.96 | — |
| 85.37 | — |
| 84.64 | — |
| 85.17 | — |
| 85.65 | — |
| 85.67 | — |
| 85.32 | — |
| 85.49 | — |
| 86.27 | — |
| 87.24 | — |
| 86.82 | — |
| 87.3 | — |
| 87.54 | — |
| 86.53 | — |
| 87.22 | — |
| 87.44 | — |
| 87.82 | — |
| 87.91 | — |
| 88.13 | — |
| 88.45 | — |
| 87.7 | — |
| 87.74 | — |
| 88.35 | — |
| 89.01 | — |
| 88.24 | — |
| 89.09 | — |
| 88.76 | — |
| 88.29 | — |
| 88.58 | — |
| 87.87 | — |
| 88.56 | — |
| 88.72 | — |
| 88.9 | — |
| 88.95 | — |
| 88.57 | — |
| 88.23 | — |
| 88.47 | — |
| 89.01 | — |
| 89.36 | — |
| 90.37 | — |
| 89.59 | — |
| 89.95 | — |
| 89.85 | — |
| 90.11 | — |
| 90.64 | — |
| 91.03 | — |
| 90.27 | — |
| 91.06 | — |
| 90.34 | — |
| 90.22 | — |
| 91.05 | — |
| 90.86 | — |
| 90.98 | — |
| 91.31 | — |
| 90.43 | — |
| 90.32 | — |
| 89.95 | — |
| 90.63 | — |
| 90.9 | — |
| 90.9 | — |
| 91.51 | — |
| 91.59 | — |
| 91.51 | — |
| 90.7 | — |
| 90.49 | — |
| 91.84 | — |
| 91.57 | — |
| 91.41 | — |
| 90.62 | — |
| 91.51 | — |
| 90.7 | — |
| 91.97 | — |
| 90.88 | — |
| 92.6 | — |
| 93.18 | — |
| 92.28 | — |
| 92.19 | — |
| 92.29 | — |
| 91.89 | — |
| 92.37 | — |
| 91.62 | — |
| 91.15 | — |
| 91.32 | — |
| 90.99 | — |
| 91.22 | — |
| 90.21 | — |
| 91.26 | — |
| 91.46 | — |
| 93.67 | — |
| 92.21 | — |
| 92.62 | — |
| 93.25 | — |
| 93.21 | — |
| 92.17 | — |
| 92.67 | — |
| 92.89 | — |
| 92.82 | — |
| 92.25 | — |
| 92.02 | — |
| 92.02 | — |
| 91.51 | — |
| 92.67 | — |
| 92.92 | — |
| 93.15 | — |
| 93.95 | — |
| 92.1 | — |
| 93.33 | — |
| 93.27 | — |
| 92.92 | — |
| 92.9 | — |
| 93.34 | — |
| 92.23 | — |
| 93.16 | — |
| 92.33 | — |
| 93.18 | — |
| 93.27 | — |
| 92.98 | — |
| 93.18 | — |
| 94.54 | — |
| 94.31 | — |
| 94.83 | — |
| 94.51 | — |
| 94.65 | — |
| 93.84 | — |
| 93.06 | — |
| 92.86 | — |
| 93.19 | — |
| 94.05 | — |
| 92.26 | — |
| 93.32 | — |
| 93.63 | — |
| 93.22 | — |
| 93.04 | — |
| 93.32 | — |
| 93.63 | — |
| 93.91 | — |
| 93.76 | — |
| 94.36 | — |
| 94.48 | — |
| 93.94 | — |
| 93.95 | — |
| 93.75 | — |
| 93.6 | — |
| 94.25 | — |
| 94.82 | — |
| 93.35 | — |
| 94.35 | — |
| 94.31 | — |
| 95.1 | — |
| 94.9 | — |
| 95.15 | — |
| 95.53 | — |
| 95.36 | — |
| 95.93 | — |
| 94.88 | — |
| 93.74 | — |
| 94.96 | — |
| 94.84 | — |
| 95.08 | — |
| 96.37 | — |
| 96.41 | — |
| 95.84 | — |
| 95.69 | — |
| 95.51 | — |
| 93.98 | — |
| 94.57 | — |
| 95.56 | — |
| 94.26 | — |
| 95.89 | — |
| 95.15 | — |
| 95.11 | — |
| 95.08 | — |
| 95.44 | — |
| 94.93 | — |
| 94.57 | — |
| 95.02 | — |
| 94.69 | — |
| 93.65 | — |
| 93.52 | — |
| 93.89 | — |
| 96.22 | — |
| 95.48 | — |
| 95.5 | — |
| 94.79 | — |
| 95.55 | — |
| 96.16 | — |
| 97.27 | — |
| 97.34 | — |
| 97.22 | — |
| 98.24 | — |
| 98.14 | — |
| 97.82 | — |
| 96.35 | — |
| 97.12 | — |
| 97.32 | — |
| 97.64 | — |
| 97.92 | — |
| 96.12 | — |
| 96.74 | — |
| 97.01 | — |
| 97.04 | — |
| 97.8 | — |
| 98.5 | — |
| 97.1 | — |
| 98.43 | — |
| 98.42 | — |
| 97.46 | — |
| 96.63 | — |
| 96.69 | — |
| 97.44 | — |
| 97.97 | — |
| 99.27 | — |
| 98.41 | — |
| 98.59 | — |
| 98.2 | 0 |
| 98.33 | 26.23 |
| 98.86 | 42.43 |
| 98.2 | 57.38 |
| 97.54 | 68.82 |
| 97.65 | 77.65 |
| 97.6 | 86.06 |
| 96.31 | 95.61 |
| 96.99 | 103.3 |
| 96.47 | 112 |
| 96.64 | 118.8 |
| 96.93 | 125.8 |
| 96.5 | 126.4 |
| 96.9 | 134.8 |
| 97.02 | 135.9 |
| 96.29 | 147.5 |
| 95.81 | 155.2 |
| 96.71 | 162.9 |
| 96.96 | 173.4 |
| 95.97 | 176.8 |
| 95.98 | 180.7 |
| 97.1 | 185.4 |
| 97.28 | 194.5 |
| 97.47 | 194.7 |
| 96.62 | 198.9 |
| 96.12 | 201.3 |
| 96.62 | 211 |
| 96.85 | 218.2 |
| 97.67 | 219.3 |
| 97.57 | 220.3 |
| 97.74 | 231.5 |
| 97.06 | 242.6 |
| 97.48 | 248.9 |
| 97.29 | 254.3 |
| 96.7 | 259 |
| 97.64 | 266 |
| 97.42 | 274.2 |
| 97.12 | 274.2 |
| 97.8 | 266.6 |
| 97.05 | 270 |
| 97.37 | 262.1 |
| 97.02 | 260.4 |
| 97.5 | 262.2 |
| 97.19 | 263 |
| 96.3 | 260.7 |
| 97.55 | 259.6 |
| 97.69 | 268.6 |
| 97.37 | 273.8 |
| 97.88 | 280 |
| 97.46 | 282.3 |
| 97.08 | 289.6 |
| 96.51 | 298.9 |
| 96.31 | 299.8 |
| 96.79 | 307.7 |
| 96.39 | 313.8 |
| 96.45 | 310.5 |
| 96.72 | 311.8 |
| 96.87 | 309.6 |
| 96.39 | 308.8 |
| 96.29 | 309.3 |
| 96.43 | 310.7 |
| 96.12 | 314.5 |
| 96.78 | 321.4 |
| 97.21 | 320.5 |
| 96.67 | 326.6 |
| 97.96 | 329.1 |
| 97.77 | 336.7 |
| 98.02 | 334.5 |
| 97.71 | 337.4 |
| 97.6 | 343.1 |
| 98.37 | 346 |
| 98.66 | 350 |
| 98.18 | 345.5 |
| 98.19 | 341.2 |
| 97.72 | 334.7 |
| 97.02 | 335.1 |
| 97.32 | 335.6 |
| 96.9 | 331.8 |
| 96.97 | 336.8 |
| 96.53 | 339.1 |
| 96.67 | 337.5 |
| 96.63 | 342.8 |
| 97.22 | 345.4 |
| 97.55 | 344.2 |
| 96.88 | 344 |
| 97.15 | 355.9 |
| 96.88 | 355.8 |
| 97.49 | 362.4 |
| 98.03 | 362.7 |
| 97.58 | 366 |
| 97.56 | 367.4 |
| 97.05 | 371.6 |
| 97.8 | 373.2 |
| 97.17 | 371.4 |
| 97.14 | 368.1 |
| 97.08 | 364.1 |
| 97.24 | 370.2 |
| 97.22 | 379.8 |
| 97.18 | 383.3 |
| 97.34 | 387 |
| 97.09 | 378.9 |
| 97.22 | 381.2 |
| 97.28 | 385.5 |
| 96.59 | 391.8 |
| 96.73 | 392.7 |
| 96.51 | 392.8 |
| 95.89 | 397.6 |
| 97.03 | 404.6 |
| 96.44 | 409.7 |
| 97.07 | 418.1 |
| 96.54 | 428.4 |
| 96.21 | 433 |
| 95.65 | 431.3 |
| 96.24 | 437.2 |
| 96.55 | 428.3 |
| 95.84 | 430.6 |
| 96.61 | 434 |
| 96.81 | 434.9 |
| 95.5 | 442.5 |
| 95.89 | 442.3 |
| 95.97 | 440.3 |
| 97.2 | 436.1 |
| 97.15 | 436.7 |
| 97.3 | 438.7 |
| 98.21 | 434.2 |
| 97.08 | 437.1 |
| 96.76 | 442.6 |
| 97.2 | 445.2 |
| 97.24 | 451.7 |
| 96.95 | 455.4 |
| 97.49 | 463.1 |
| 97.35 | 465.7 |
| 97.34 | 459.7 |
| 97.37 | 458.4 |
| 96.08 | 456.5 |
| 96.53 | 461.5 |
| 96.16 | 469.7 |
| 97.21 | 467.9 |
| 96.58 | 463.5 |
| 96.47 | 466.2 |
| 95.79 | 465.5 |
| 96.32 | 459.7 |
| 96.26 | 467.7 |
| 96.59 | 478.9 |
| 96.31 | 477.4 |
| 96.4 | 482.8 |
| 96.94 | 484.3 |
| 96.16 | 487.7 |
| 96.12 | 482.1 |
| 96.06 | 486.6 |
| 96.77 | 487.8 |
| 96.38 | 481.5 |
| 96.23 | 475.4 |
| 96.8 | 472.5 |
| 96.59 | 480.5 |
| 96.9 | 488.4 |
| 96.86 | 489.4 |
| 95.99 | 486 |
| 96.49 | 492.5 |
| 95.84 | 487.8 |
| 96.32 | 492.2 |
| 96.41 | 492.3 |
| 97.33 | 501.1 |
| 96.69 | 503.6 |
| 96.35 | 516.6 |
| 97.17 | 516.7 |
| 96.42 | 511.8 |
| 96.56 | 512.5 |
| 96.75 | 514.6 |
| 96.56 | 515.4 |
| 96.83 | 517.4 |
| 96.95 | 523.7 |
| 96.19 | 522 |
| 96.62 | 529.4 |
| 96.92 | 535.7 |
| 96.47 | 541.4 |
| 97.09 | 543.5 |
| 96.89 | 539 |
| 96.36 | 542.5 |
| 95.81 | 548.6 |
| 96.3 | 551.5 |
| 96.83 | 555.3 |
| 97.65 | 556.8 |
| 96.86 | 552.3 |
| 96.8 | 541.5 |
| 96.53 | 552.9 |
| 96.84 | 554.8 |
| 96.26 | 552.5 |
| 97.58 | 560.7 |
| 97.03 | 565.7 |
| 97.87 | 561.2 |
| 97.77 | 559.6 |
| 96.68 | 559.4 |
| 96.92 | 565.1 |
| 96.79 | 564.9 |
| 97.03 | 570.2 |
| 97.66 | 579 |
| 97.73 | 580 |
| 97.2 | 568.9 |
| 97.19 | 564.9 |
| 97.92 | 565.3 |
| 97.43 | 566.3 |
| 97.59 | 567.4 |
| 97.43 | 577.2 |
| 97.13 | 579.5 |
| 97.41 | 581.2 |
| 97.58 | 586.4 |
| 97.23 | 583.2 |
| 97.52 | 583.1 |
| 98.16 | 581.3 |
| 97.47 | 581.8 |
| 98.32 | 589.3 |
| 97.59 | 588.5 |
| 97.05 | 592.8 |
| 96.44 | 592.5 |
| 97.38 | 590.2 |
| 97.21 | 594.3 |
| 96.92 | 598.9 |
| 97.26 | 603.4 |
| 97.42 | 602.9 |
| 96.9 | 606.5 |
| 96.76 | 607 |
| 96.93 | 616.6 |
| 97.29 | 610.6 |
| 97.01 | 605.2 |
| 97.25 | 603.8 |
| 97.05 | 602.2 |
| 96.88 | 602.7 |
| 97.07 | 599.5 |
| 96.95 | 606.2 |
| 96.38 | 606.7 |
| 96.59 | 611.8 |
| 97.36 | 612.1 |
| 97.85 | 611.5 |
| 97.72 | 617.1 |
| 97.75 | 630.1 |
| 97.49 | 624.7 |
| 96.95 | 623.6 |
| 97.17 | 623.8 |
| 97.49 | 629.4 |
| 97.01 | 628.7 |
| 97.31 | 633.1 |
| 97.61 | 634.1 |
| 97.2 | 632.8 |
| 96.68 | 628.9 |
| 97.04 | 631.9 |
| 96.78 | 631.1 |
| 97.21 | 636.8 |
| 97.48 | 637.4 |
| 97.45 | 630 |
| 97.47 | 635.6 |
| 97.16 | 630.5 |
| 96.53 | 623.4 |
| 97.07 | 626.5 |
| 96.08 | 628.6 |
| 96.22 | 626.5 |
| 96.55 | 641.3 |
| 96.71 | 643.3 |
| 96.95 | 642.5 |
| 97.15 | 638.2 |
| 97.46 | 643.6 |
| 98.2 | 643.4 |
| 97.73 | 651 |
| 97.34 | 647.5 |
| 97.27 | 650.3 |
| 97.21 | 651.4 |
| 97.65 | 662.4 |
| 97.54 | 666.7 |
| 97.52 | 672.5 |
| 97.42 | 676.8 |
| 97.71 | 676.3 |
| 97.63 | 691.9 |
| 97.85 | 695.7 |
| 97.32 | 696.6 |
| 96.36 | 687 |
| 96.59 | 687.1 |
| 97.14 | 686.1 |
| 96.78 | 690.9 |
| 96.81 | 689.7 |
| 96.78 | 685 |
| 96.78 | 685.7 |
| 96.99 | 676.6 |
| 96.24 | 670.2 |
| 96.8 | 665.4 |
| 97.01 | 668.7 |
| 96.62 | 667.9 |
| 96.87 | 664.1 |
| 97.26 | 669.5 |
| 97.22 | 675 |
| 96.58 | 675.8 |
| 97.35 | 667.3 |
| 97.64 | 659 |
| 97.02 | 655.6 |
| 97.1 | 661.7 |
| 96.95 | 659.1 |
| 96.95 | 654.7 |
| 96.47 | 658.9 |
| 97.34 | 659.8 |
| 97.42 | 657.4 |
| 97.18 | 662 |
| 97.39 | 668.8 |
| 98.42 | 667.6 |
| 99.03 | 666.1 |
| 98.23 | 664.7 |
| 98.75 | 665.9 |
| 98.71 | 680.9 |
| 98.31 | 677.2 |
| 98 | 674.6 |
| 98.16 | 674.4 |
| 97.98 | 670.7 |
| 97.8 | 668.3 |
| 98.82 | 662.9 |
| 98.54 | 663.6 |
| 98.53 | 665.6 |
| 98.08 | 667.6 |
| 97.8 | 664.5 |
| 97.69 | 656.7 |
| 97.3 | 649.1 |
| 96.67 | 636.8 |
| 97.04 | 645 |
| 96.88 | 646.8 |
| 96.83 | 636.9 |
| 96.9 | 636.9 |
| 96.57 | 643.3 |
| 97.08 | 641.4 |
| 97.16 | 636.3 |
| 95.71 | 634.6 |
| 97 | 641.1 |
| 97.18 | 637.2 |
| 96.76 | 631.3 |
| 96.97 | 634.1 |
| 96.81 | 628.6 |
| 97.65 | 636 |
| 97.72 | 631.7 |
| 97.75 | 634.5 |
| 97.76 | 633.6 |
| 97.13 | 643.1 |
| 97.24 | 647.3 |
| 97.41 | 650.8 |
| 96.82 | 651.2 |
| 96.98 | 641.9 |
| 97.08 | 645.6 |
| 96.02 | 643 |
| 96.64 | 640.7 |
| 96.88 | 647 |
| 96.71 | 643.1 |
| 96.15 | 644.3 |
| 96.55 | 653.3 |
| 96.37 | 656.8 |
| 96.07 | 653.7 |
| 96.61 | 664.9 |
| 96.14 | 663.5 |
| 96.63 | 671.4 |
| 97.42 | 676.7 |
| 96.87 | 687.5 |
| 97.71 | 693.6 |
| 98.25 | 692.6 |
| 98.01 | 695.2 |
| 98.38 | 707.4 |
| 98.28 | 704.8 |
| 98.66 | 704.7 |
| 98.38 | 706.5 |
| 97.97 | 719.1 |
| 98.06 | 727.8 |
| 98.69 | 725.9 |
| 98.49 | 727.6 |
| 98 | 723.1 |
| 98.27 | 714.2 |
| 98.02 | 700.5 |
| 97.48 | 690.8 |
| 97.9 | 684.6 |
| 97.64 | 678.1 |
| 97.21 | 681.3 |
| 96.94 | 682.9 |
| 97.11 | 693.9 |
| 96.76 | 688.4 |
| 97.12 | 679.5 |
| 97.04 | 683.4 |
| 97.11 | 689.8 |
| 97.62 | 692.2 |
| 97.9 | 691.9 |
| 97.24 | 690.7 |
| 97.4 | 689 |
| 97.22 | 695.7 |
| 97.37 | 693.9 |
| 97.23 | 687.5 |
| 97.83 | 682.7 |
| 96.81 | 680.5 |
| 96.82 | 679.1 |
| 96.82 | 682.8 |
| 96.21 | 680.4 |
| 96.29 | 685.6 |
| 96.7 | 671.5 |
| 96.5 | 673.9 |
| 97.29 | 682.5 |
| 96.92 | 684.3 |
| 97.07 | 693.7 |
| 96.94 | 699.9 |
| 97.3 | 696.7 |
| 96.7 | 697.3 |
| 97.21 | 700.8 |
| 98.06 | 729.4 |
| 96.87 | 729.2 |
| 97.41 | 762 |
| 97.34 | 760.5 |
| 99 | 771.7 |
| 98.57 | 805.3 |
| 98.89 | 804.6 |
| 97.82 | 804.8 |
| 99.19 | 837.4 |
| 99.05 | 828.2 |
| 99.21 | 862.8 |
| 99.16 | 858.7 |
| 97.77 | 837.7 |
| 98.19 | 836.5 |
| 97.82 | 849.3 |
| 98.05 | 839.6 |
| 97.15 | 848 |
| 98.88 | 869.6 |
| 99.08 | 906.5 |
| 98.83 | 883.5 |
| 98.92 | 920.3 |
| 98.92 | 898.3 |
| 97.72 | 915.3 |
| 98.27 | 920.8 |
| 98.39 | 916.3 |
| 98.65 | 921.1 |
| 98.61 | 925.6 |
| 97.92 | 949.7 |
| 97.66 | 976.4 |
| 99.09 | 995.8 |
| 97.82 | 978.5 |
| 97.9 | 972.3 |
| 98.32 | 999.1 |
| 98.89 | 998.2 |
| 98.2 | 1019 |
| 97.34 | 1026 |
| 97.48 | 1018 |
| 98.3 | 1045 |
| 97.58 | 1021 |
| 98.65 | 1043 |
| 99.19 | 1042 |
| 98.81 | 1029 |
| 98.72 | 1016 |
| 98.9 | 1076 |
| 100.3 | 1119 |
| 100 | 1098 |
| 99.34 | 1090 |
| 100 | 1128 |
| 99.2 | 1127 |
| 99.75 | 1143 |
| 99.93 | 1168 |
| 99.84 | 1191 |
| 99.95 | 1176 |
| 99.11 | 1182 |
| 99.09 | 1190 |
| 98.9 | 1163 |
| 99.53 | 1166 |
| 99.35 | 1180 |
| 99.56 | 1185 |
| 98.31 | 1165 |
| 99.53 | 1180 |
| 100.3 | 1171 |
| 99.37 | 1176 |
| 97.83 | 1116 |
| 97.7 | 1109 |
| 99.65 | 1150 |
| 98.24 | 1136 |
| 99.58 | 1165 |
| 97.94 | 1152 |
| 100.1 | 1200 |
| 98.7 | 1165 |
| 100 | 1192 |
| 98.88 | 1205 |
| 98.91 | 1200 |
| 98.52 | 1235 |
| 99.42 | 1250 |
| 99.32 | 1269 |
| 100.2 | 1309 |
| 100.7 | 1283 |
| 99.44 | 1221 |
| 99.41 | 1224 |
| 100.6 | 1206 |
| 99.46 | 1196 |
| 99.11 | 1224 |
| 99.05 | 1256 |
| 98.98 | 1268 |
| 100.1 | 1266 |
| 98.85 | 1260 |
| 99.26 | 1278 |
| 100.9 | 1338 |
| 101.4 | 1332 |
| 100.9 | 1332 |
| 100.9 | 1338 |
| 102.1 | 1401 |
| 101.5 | 1425 |
| 100.5 | 1373 |
| 99.46 | 1349 |
| 102.1 | 1387 |
| 102.3 | 1403 |
| 102.4 | 1388 |
| 100.8 | 1361 |
| 101 | 1404 |
| 100.5 | 1366 |
| 99.55 | 1380 |
| 99.1 | 1370 |
| 99.34 | 1385 |
| 101.5 | 1431 |
| 100 | 1407 |
| 100 | 1453 |
| 100.1 | 1475 |
| 101 | 1474 |
| 101.3 | 1519 |
| 100.3 | 1508 |
| 98.76 | 1500 |
| 100.5 | 1466 |
| 99.53 | 1486 |
| 99.75 | 1500 |
| 100.3 | 1531 |
| 98.75 | 1499 |
| 99.69 | 1517 |
| 99.43 | 1564 |
| 100.2 | 1568 |
| 99.73 | 1568 |
| 98.68 | 1513 |
| 100.5 | 1515 |
| 99.51 | 1522 |
| 100.3 | 1552 |
| 100 | 1495 |
| 98.48 | 1482 |
| 100.1 | 1489 |
| 98.87 | 1550 |
| 98.84 | 1523 |
| 99.93 | 1574 |
| 100.5 | 1568 |
| 100.5 | 1552 |
| 99.51 | 1530 |
| 99.99 | 1558 |
| 98.8 | 1549 |
| 98.16 | 1602 |
| 100.2 | 1612 |
| 99.52 | 1633 |
| 98.96 | 1616 |
| 100.4 | 1646 |
| 99.98 | 1651 |
| 100.3 | 1669 |
| 101.7 | 1668 |
| 100.9 | 1685 |
| 101.3 | 1698 |
| 103.1 | 1696 |
| 100.9 | 1624 |
| 101.4 | 1620 |
| 99.99 | 1603 |
| 100.4 | 1634 |
| 100.6 | 1652 |
| 99.97 | 1664 |
| 100 | 1655 |
| 99.58 | 1664 |
| 101.1 | 1644 |
| 100.6 | 1611 |
| 102.3 | 1620 |
| 102.3 | 1640 |
| 102.9 | 1634 |
| 102.3 | 1696 |
| 104.1 | 1716 |
| 102.8 | 1723 |
| 100.9 | 1719 |
| 100.8 | 1708 |
| 100.8 | 1739 |
| 101.7 | 1754 |
| 100.8 | 1756 |
| 101.3 | 1752 |
| 99.74 | 1726 |
| 101.2 | 1726 |
| 100.8 | 1711 |
| 101.6 | 1769 |
| 101.3 | 1719 |
| 101.9 | 1695 |
| 100.4 | 1672 |
| 99.92 | 1668 |
| 101.2 | 1695 |
| 99.79 | 1658 |
| 100.6 | 1684 |
| 100.5 | 1662 |
| 99.45 | 1667 |
| 101.9 | 1730 |
| 101.9 | 1696 |
| 100.7 | 1684 |
| 99.84 | 1686 |
| 100.7 | 1713 |
| 100.2 | 1736 |
| 101 | 1738 |
| 101 | 1712 |
| 101.1 | 1718 |
| 101.1 | 1764 |
| 100.7 | 1759 |
| 101.3 | 1757 |
| 102.4 | 1803 |
| 102.4 | 1812 |
| 103.5 | 1823 |
| 102 | 1876 |
| 102 | 1848 |
| 102.5 | 1838 |
| 101.3 | 1838 |
| 101.1 | 1787 |
| 101.4 | 1827 |
| 101.2 | 1843 |
| 100.7 | 1834 |
| 102.5 | 1867 |
| 102 | 1892 |
| 101.2 | 1856 |
| 103.8 | 1836 |
| 103.6 | 1949 |
| 102.6 | 1906 |
| 101.9 | 1932 |
| 101.7 | 1920 |
| 101.6 | 1916 |
| 101.7 | 1901 |
| 101.7 | 1927 |
| 102 | 1934 |
| 103.9 | 1935 |
| 102.7 | 1937 |
| 102.5 | 1951 |
| 101.8 | 1953 |
| 102.7 | 1993 |
| 102.8 | 2009 |
| 103 | 2046 |
| 103.1 | 2035 |
| 103 | 2053 |
| 102.8 | 2077 |
| 103.5 | 2064 |
| 102.8 | 2121 |
| 101.7 | 2128 |
| 101.5 | 2129 |
| 104.2 | 2126 |
| 101 | 2079 |
| 100.6 | 2105 |
| 102.6 | 2089 |
| 101.9 | 2047 |
| 102.1 | 2056 |
| 100.5 | 2081 |
| 101.9 | 2107 |
| 103.1 | 2082 |
| 102.5 | 2088 |
| 101.5 | 2092 |
| 102 | 2111 |
| 102.1 | 2086 |
| 100.6 | 2122 |
| 103.1 | 2152 |
| 102.9 | 2163 |
| 102.5 | 2193 |
| 102.8 | 2176 |
| 102.4 | 2154 |
| 101.9 | 2175 |
| 103 | 2166 |
| 102.2 | 2148 |
| 102.6 | 2120 |
| 103.2 | 2177 |
| 103.1 | 2166 |
| 102.3 | 2175 |
| 104.2 | 2244 |
| 103.4 | 2240 |
| 103.9 | 2294 |
| 103.9 | 2259 |
| 103.8 | 2270 |
| 104.5 | 2262 |
| 103.8 | 2297 |
| 102.2 | 2219 |
| 102.3 | 2235 |
| 103.9 | 2266 |
| 103.4 | 2256 |
| 103.1 | 2261 |
| 102.8 | 2298 |
| 103.5 | 2323 |
| 103.3 | 2341 |
| 102.6 | 2395 |
| 103.8 | 2416 |
| 104.8 | 2433 |
| 104.8 | 2389 |
| 104.2 | 2400 |
| 102.5 | 2335 |
| 102.5 | 2341 |
| 103.7 | 2365 |
| 105.2 | 2364 |
| 103.8 | 2372 |
| 103.7 | 2343 |
| 103.2 | 2386 |
| 105.5 | 2477 |
| 103.7 | 2481 |
| 103.7 | 2485 |
| 103.5 | 2495 |
| 103.3 | 2436 |
| 103.2 | 2472 |
| 103.8 | 2482 |
| 102.9 | 2476 |
| 104.2 | 2509 |
| 104.7 | 2554 |
| 104.1 | 2514 |
| 103.8 | 2532 |
| 104 | 2619 |
| 104.1 | 2632 |
| 103.5 | 2616 |
| 103.9 | 2530 |
| 103.2 | 2528 |
| 104.8 | 2505 |
| 103.4 | 2532 |
| 104 | 2554 |
| 102.7 | 2525 |
| 103.7 | 2579 |
| 103.4 | 2556 |
| 103.7 | 2525 |
| 104.6 | 2506 |
| 104.8 | 2502 |
| 104.1 | 2557 |
| 103.3 | 2574 |
| 103.8 | 2603 |
| 104.4 | 2565 |
| 104.1 | 2539 |
| 103.9 | 2525 |
| 102.6 | 2505 |
| 103.1 | 2518 |
| 102.9 | 2609 |
| 103.4 | 2545 |
| 102.7 | 2529 |
| 103.5 | 2570 |
| 104.5 | 2583 |
| 104.4 | 2574 |
| 105.3 | 2615 |
| 106 | 2618 |
| 105 | 2641 |
| 105.1 | 2630 |
| 105.5 | 2582 |
| 105.7 | 2629 |
| 106.5 | 2676 |
| 104.4 | 2650 |
| 104.8 | 2658 |
| 104.8 | 2650 |
| 105.3 | 2658 |
| 106.2 | 2676 |
| 106 | 2667 |
| 105.3 | 2692 |
| 105.8 | 2687 |
| 105.8 | 2697 |
| 106.2 | 2735 |
| 107 | 2728 |
| 107.2 | 2678 |
| 108.2 | 2713 |
| 106.3 | 2753 |
| 106.4 | 2718 |
| 106.8 | 2698 |
| 106.8 | 2704 |
| 106.6 | 2745 |
| 107.6 | 2719 |
| 105 | 2663 |
| 105.2 | 2715 |
| 104.6 | 2697 |
| 107.7 | 2793 |
| 106.1 | 2783 |
| 106.4 | 2800 |
| 106.9 | 2840 |
| 106.8 | 2862 |

`per_segment`:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |

Per segment:

| `end_ns` | T (°C) |
|---|---|
| 20 | 160 |


</details>

### `pe_cg_pore_w5nm_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`). Status: finished: pore, `pore_55C`, `pore_120C`, `pore_75C`, `pore_150C`, `pore_110C`, `pore_140C`.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | — | `extend` progress of `pe_cg_amorph_n640_c240_s1_rep441` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 8.93 (melt 6.7) | n/a | `extend` progress of `pe_cg_amorph_n640_c240_s1_rep441` |
| R<sub>g</sub> (Å) | 31.51 ± 0.07 | 30.61 ± 0.04 | 29.24 ± 0.03 | 28.73 ± 0.04 | — | trend | `pore` |
| R<sub>ee</sub> (Å) | 77.7 ± 0.1 | 75.9 ± 0.2 | 72.0 ± 0.2 | 70.0 ± 0.3 | — | trend | `pore` |
| C<sub>n</sub> | 10.59 ± 0.05 | 10.11 ± 0.03 | 9.14 ± 0.03 | 8.82 ± 0.04 | — | trend | `pore` |
| P2 1/e time (ps) | 77.7 | 18.2 | 9.02 | 6.04 | — | corr | `pore` |
| P2 1/e time, surface layer (ps) | 54.7 | 13.3 | 6.73 | 4.64 | — | corr | `pore` |
| P2 1/e time, interior layer (ps) | 103 | 23.9 | 12.2 | 7.83 | — | corr | `pore` |
| segment MSD at 1 ns lag (Å²) | 217.2 | 347.3 | 424.1 | 487.5 | — | corr | `pore` |
| max chain COM MSD (Å²) at lag | 68.05 at 2.5 ns | 124.8 at 2.5 ns | 154.4 at 2.5 ns | 196.6 at 2.5 ns | — | n/a | `pore` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.07 | 0.13 | 0.18 | 0.24 | — | n/a | `pore` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.73) | not diffusive (slope 0.73) | not diffusive (slope 0.65) | not diffusive (slope 0.75) | — | n/a | `pore` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached (extrap. 29.7) | not reached (extrap. 15.2) | not reached (extrap. 10.3) | not reached (extrap. 8.41) | — | n/a | `pore` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached (extrap. 20.2) | not reached (extrap. 16) | — | n/a | `pore` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.174 | 0.126 | 0.114 | 0.108 | — | — | `pore` |
| γ, run monitor (mN/m) | — | — | — | — | 27.4 ± 0.2 | comp | `pore_140C` progress |
| γ, analysis (mN/m) | 34.4 ± 0.4 | 30.8 ± 0.3 | 28.1 ± 0.1 | 26.5 ± 0.1 | — | comp | `pore` |
| dγ/dT (mN m⁻¹ K⁻¹) | — | — | — | — | cooling branch 25–201.6 °C: -0.0556 ± 0.0011 (χ²<sub>red</sub> 0.925); heating sweep 25–160 °C: -0.0590 ± 0.0028 (χ²<sub>red</sub> 1.11) | comp | `pore` |
| γ at 25 °C from the dγ/dT fit (mN/m) | — | — | — | — | cooling branch: 34.10; heating sweep: 34.37 | comp | `pore` |
| film thickness between the Gibbs surfaces (Å) | 64.53 ± 0.01 | 65.48 ± 0.01 | 66.09 ± 0.01 | 66.58 ± 0.01 | — | trend | `pore` |
| gap between the Gibbs surfaces (Å) | 50.00 | 49.05 | 48.44 | 47.95 | — | trend | `pore` |
| film interior density (g/cm³) | 0.8346 ± 0.0001 | 0.7982 ± 0.0001 | 0.7761 ± 0.0001 | 0.7597 ± 0.0001 | — | trend | `pore` |
| interfacial width, 10–90 % (Å) | 7.45 | 8.67 | 9.65 | 10.17 | — | trend | `pore` |
| closest approach across the gap (Å) | 37.9 | 35.1 | 32.4 | 30.8 | — | trend | `pore` |
| film α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 6.935; 90–160 °C: 7.059 | — | `pore` |
| α<sub>z</sub>, film-thickness expansion (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 2.302 ± 0.034 (χ²<sub>red</sub> 12); 90–160 °C: 2.368 ± 0.059 (χ²<sub>red</sub> 7.41) | — | `pore` |
| C<sub>v</sub> of the film, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 0.820 ± 0.005 (χ²<sub>red</sub> 34.2); 90–160 °C: 0.813 ± 0.006 (χ²<sub>red</sub> 17.9) | — | `pore` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 640 chains × C240 (C240H482), 51,200 atoms/beads, force field `sdk_cg`, box density 0.4276 g/cm³ (as built)
- Replicated 4×4×1 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.69 nm at 500 K, wall 6.45 nm, clear gap 2.08 nm, area 731.0 nm²
- Built from: `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n640_c240_s1_rep441` (`extend/hold_ext_80ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08)

**Stages**

- **pore** (rdyu-rog): finished; started 2026-11-06 14:43 UTC, ended 2026-11-09 07:03 UTC; reads `systems/pe_cg_pore_w5nm_n640_c240_s1_rep441/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 34.3 ± 0.5; 90 °C 30.5 ± 0.4; 130 °C 28.0 ± 0.1; 160 °C 26.3 ± 0.2
- **`pore_55C`** (rdyu-rog): finished; started 2026-11-23 20:56 UTC, ended 2026-11-24 04:02 UTC; reads `../pore/hold_25C.data`
  - γ per hold (monitor, second half of each segment, mN/m): 55 °C 32.8 ± 0.2
- **`pore_120C`** (rdyu-server): finished; started 2026-11-23 20:56 UTC, ended 2026-11-24 17:00 UTC; reads `../pore/hold_90C.data`
  - γ per hold (monitor, second half of each segment, mN/m): 120 °C 30.0 ± 0.3
- **`pore_75C`** (rdyu-server): finished; started 2026-11-23 20:56 UTC, ended 2026-11-24 08:53 UTC; reads `../pore/hold_25C.data`
  - γ per hold (monitor, second half of each segment, mN/m): 75 °C 31.6 ± 0.3
- **`pore_150C`** (rdyu-server): finished; started 2026-11-23 23:03 UTC, ended 2026-11-24 09:42 UTC; reads `../pore/hold_130C.data`
  - γ per hold (monitor, second half of each segment, mN/m): 150 °C 27.4 ± 0.2
- **`pore_110C`** (rdyu-rog): finished; started 2026-11-23 23:29 UTC, ended 2026-11-24 06:34 UTC; reads `../pore/hold_90C.data`
  - γ per hold (monitor, second half of each segment, mN/m): 110 °C 29.3 ± 0.2
- **`pore_140C`** (rdyu-rog): finished; started 2026-11-23 23:50 UTC, ended 2026-11-24 06:41 UTC; reads `../pore/hold_130C.data`
  - γ per hold (monitor, second half of each segment, mN/m): 140 °C 27.4 ± 0.2

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | 140 °C 27.4 ± 0.2 | finished: pore, `pore_55C`, `pore_120C`, `pore_75C`, `pore_150C`, `pore_110C`, `pore_140C` | pore |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`pore` analysis**

Pore analysis (`sepsim analyze pore`, generated 2026-11-09 07:04 UTC on rdyu-rog):

- dγ/dT, cooling-branch fit (mN m⁻¹ K⁻¹): -0.05555
- γ at 25 °C, cooling-branch fit (mN/m): 34.1
- dγ/dT, heating-sweep fit (mN m⁻¹ K⁻¹): -0.05904
- γ at 25 °C, heating-sweep fit (mN/m): 34.37
- analysis node: rdyu-rog
- nominal gap width (nm): 5
- wall (film) thickness (Å): 64.53

Convergence of the film quantities, per segment:

| γ (mN/m) | segment end (ps) | gap between the Gibbs surfaces (Å) | film interior density (g/cm³) |
|---|---|---|---|
| 23.11 ± 0.465 | 2000 | — | — |
| 24.39 ± 0.1951 | 7000 | — | — |
| 25.6 ± 0.1821 | 1.2e+04 | — | — |
| 27.01 ± 0.181 | 1.7e+04 | — | — |
| 28.77 ± 0.22 | 2.2e+04 | — | — |
| 29.54 ± 0.2845 | 2.7e+04 | — | — |
| 31.39 ± 0.1899 | 3.2e+04 | — | — |
| 32.13 ± 0.5001 | 3.7e+04 | — | — |
| 34.14 ± 0.1464 | 4.2e+04 | — | — |
| 34.41 ± 0.3971 | 4.7e+04 | 50 ± 0.006909 | 0.8346 ± 8.942e-05 |
| 30.59 ± 0.203 | 5.2e+04 | 49.09 ± 0.02778 | 0.7987 ± 0.0003413 |
| 30.76 ± 0.261 | 5.7e+04 | 49.05 ± 0.007832 | 0.7982 ± 9.642e-05 |
| 28.27 ± 0.2116 | 6.2e+04 | 48.4 ± 0.02649 | 0.7756 ± 0.0003111 |
| 28.05 ± 0.1207 | 6.7e+04 | 48.44 ± 0.006745 | 0.7761 ± 8.021e-05 |
| 26.63 ± 0.208 | 7.2e+04 | 47.92 ± 0.02852 | 0.7593 ± 0.0003236 |
| 26.5 ± 0.1346 | 7.7e+04 | 47.95 ± 0.008599 | 0.7597 ± 9.934e-05 |

Per hold: film vs bulk:

| film: C<sub>n</sub> bond length (Å) | film: C<sub>n</sub> | film: max lag (ps) | film: max chain COM MSD (Å²) | film: chain COM MSD / ⟨R<sub>g</sub>²⟩ at max lag | film: COM MSD log-slope at max lag | film: largest COM MSD log-slope | film: largest ordered cluster, mean (sites) | film: hold length (ns) | `film.segment_msd.lag_max_ps` | `film.segment_msd.msd_1000ps_A2` | `film.segment_msd.msd_10ps_A2` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.54 | 10.59 ± 0.05075 | 2500 | 68.05 | 0.06853 | 0.73 | 1.89 | 785 | 5 | 2500 | 217.2 | 13.53 |
| 1.54 | 10.11 ± 0.03369 | 2500 | 124.8 | 0.1332 | 0.7265 | 1.9 | 137 | 5 | 2500 | 347.3 | 21.09 |
| 1.54 | 9.143 ± 0.02638 | 2500 | 154.4 | 0.1806 | 0.6464 | 1.907 | 79.68 | 5 | 2500 | 424.1 | 26.53 |
| 1.54 | 8.816 ± 0.03691 | 2500 | 196.6 | 0.2383 | 0.7452 | 1.911 | 63.2 | 5 | 2500 | 487.5 | 30.77 |

Per segment:

| γ drift: second − first half (mN/m) | γ, first half (mN/m) | γ, second half (mN/m) | SEM of the γ drift (mN/m) | potential-energy drift: second − first half | box density (g/cm³) | γ (mN/m) | T (°C) | set T (°C) | SEM of γ from 16 blocks (mN/m) | SEM of γ from 32 blocks (mN/m) | SEM of γ from 8 blocks (mN/m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| -0.6448 | 23.43 | 22.78 | 0.8011 | -61.18 | 0.4276 ± 0 | 23.11 ± 0.465 | 226.9 ± 0.05576 | 226.9 | — | — | — |
| 0.01328 | 24.39 | 24.4 | 0.3907 | -55.33 | 0.4327 ± 0 | 24.39 ± 0.1951 | 201.6 ± 0.03528 | 201.6 | — | — | — |
| -0.1563 | 25.69 | 25.53 | 0.3214 | 140.5 | 0.4381 ± 0 | 25.6 ± 0.1821 | 176.4 ± 0.04006 | 176.4 | — | — | — |
| 0.4077 | 26.8 | 27.21 | 0.3845 | 54.67 | 0.4433 ± 0 | 27.01 ± 0.181 | 151.2 ± 0.03233 | 151.2 | — | — | — |
| 0.3292 | 28.61 | 28.94 | 0.614 | 32.02 | 0.4486 ± 0 | 28.77 ± 0.22 | 125.9 ± 0.02921 | 125.9 | — | — | — |
| -0.619 | 29.84 | 29.22 | 0.5366 | -123.8 | 0.454 ± 0 | 29.54 ± 0.2845 | 100.7 ± 0.02633 | 100.7 | — | — | — |
| -0.2141 | 31.5 | 31.29 | 0.3521 | -87.22 | 0.4593 ± 0 | 31.39 ± 0.1899 | 75.46 ± 0.03011 | 75.46 | — | — | — |
| 1.519 | 31.36 | 32.88 | 0.4015 | -15.41 | 0.4646 ± 0 | 32.13 ± 0.5001 | 50.25 ± 0.02729 | 50.23 | — | — | — |
| -0.307 | 34.29 | 33.98 | 0.3046 | 41.76 | 0.4704 ± 0 | 34.14 ± 0.1464 | 24.96 ± 0.04086 | 25 | — | — | — |
| -0.5956 | 34.71 | 34.12 | 0.532 | -172.3 | 0.4702 ± 0 | 34.41 ± 0.3971 | 24.98 ± 0.01955 | 25 | 0.2656 | 0.217 | 0.3022 |
| -0.2241 | 30.7 | 30.48 | 0.4217 | 6.89 | 0.4564 ± 0 | 30.59 ± 0.203 | 89.94 ± 0.02755 | 90 | — | — | — |
| -0.1438 | 30.83 | 30.68 | 0.4536 | 28.02 | 0.4564 ± 0 | 30.76 ± 0.261 | 89.97 ± 0.01952 | 90 | 0.1893 | 0.1532 | 0.2313 |
| 0.6536 | 27.95 | 28.6 | 0.4238 | -26.46 | 0.4478 ± 0 | 28.27 ± 0.2116 | 130 ± 0.02979 | 130 | — | — | — |
| -0.1511 | 28.13 | 27.97 | 0.2659 | 22.9 | 0.4478 ± 0 | 28.05 ± 0.1207 | 130 ± 0.024 | 130 | 0.1311 | 0.1325 | 0.1247 |
| -0.5004 | 26.87 | 26.37 | 0.3908 | 25.85 | 0.4416 ± 0 | 26.63 ± 0.208 | 160.1 ± 0.03246 | 160 | — | — | — |
| -0.2905 | 26.64 | 26.35 | 0.2693 | 132.9 | 0.4416 ± 0 | 26.5 ± 0.1346 | 160 ± 0.02391 | 160 | 0.124 | 0.1461 | 0.1319 |

- Note: γ uses a plain LJ cutoff without tail correction (D44/D48: `pair_modify tail no`, CG 15 Å, UA/AA 14 Å), so it is cutoff-dependent and lower than a full-dispersion (LJ-PPPM or tail-corrected) value; compare it across our runs, not directly with experiment.
- Note: γ is the mechanical (pressure-tensor) value per surface, (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2] with two film surfaces; the fits are SEM-weighted linear fits in T with errors scaled by √χ²<sub>red</sub> when χ²<sub>red</sub> > 1.
- Note: The slit is a local patch of a pore wall: real separator pores are 30–100 nm and their walls semicrystalline (D50); these walls are amorphous (melt-like or post-shutdown).
- Note: Layers: surface = within 15 Å of either Gibbs surface on the film side (or outside it), interior = the rest, assigned at each time origin; sites leave their layer at long lags, so long-lag layer MSDs mix layers. MSDs are per dimension: in-plane (⟨Δx²⟩+⟨Δy²⟩)/2, normal ⟨Δz²⟩, bulk MSD/3 (isotropic).
- Note: C<sub>v</sub> = dE/dT (total energy, NVT, per gram) and the surface excess energy are classical: C<sub>v</sub> is not comparable to experiment for the same reasons as the bulk C<sub>p</sub> (classical equipartition; UA/CG drop degrees of freedom). e<sub>s</sub> = (E<sub>pore</sub> − (M<sub>pore</sub>/M<sub>bulk</sub>) E<sub>bulk</sub>(T))/(2A) compares the NVT film with the NPT bulk at 1 atm (PV ≈ 0) at the same set T; the film's lateral box follows the bulk density (D48).
- Note: CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; `docs/experiment_comparison.md`), so MSD, D<sub>COM</sub>, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment.
- Note: bulk analysis results.json not found: no bulk comparison

</details>

### `pe_ua_crystal_7x10x40_s1`

PE UA, periodic crystal of straight stems (7×10×40 cell repeats, D59), 140 chains × C80, 11,200 united atoms; provenance not recorded. Status: finished: crystal, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c`, `tensile_25C_r1e9`, `tensile_90C_r1e9`, `tensile_130C_r1e9`, `tensile_160C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| ρ (g/cm³) | 1.01447 ± 0.00047 | 0.99779 ± 0.00028 | 0.98689 ± 0.00006 | 0.97640 ± 0.00020 | 35 °C: 1.01239 ± 0.00024; 45 °C: 1.00893 ± 0.00011; 55 °C: 1.00593 ± 0.00007; 65 °C: 1.00354 ± 0.00006; 75 °C: 1.00280 ± 0.00031; 85 °C: 0.99926 ± 0.00011; 100 °C: 0.99474 ± 0.00013; 110 °C: 0.99257 ± 0.00010; 120 °C: 0.99076 ± 0.00054; 140 °C: 0.98367 ± 0.00009; 150 °C: 0.98024 ± 0.00041 | comp | `crystal`, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 2.791 ± 0.137; 35–65 °C: 2.948 ± 0.157; 75–110 °C: 2.936 ± 0.177; 120–150 °C: 3.537 ± 0.013 | trend | `crystal`, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c` |
| crystallinity (ordered-site fraction) | 1.000 | 1.000 | 0.999 | 0.998 | 35 °C: 1.000; 45 °C: 1.000; 55 °C: 1.000; 65 °C: 1.000; 75 °C: 1.000; 85 °C: 1.000; 100 °C: 1.000; 110 °C: 1.000; 120 °C: 1.000; 140 °C: 0.999; 150 °C: 0.999 | — | `crystal`, `crystal_fine_a`, `crystal_fine_b`, `crystal_fine_c` |
| E<sub>app</sub> (MPa), 10⁹ s⁻¹, mean ± SD | 4.11e+03 ± 276 | 3.17e+03 ± 242 | 3.03e+03 ± 343 | 2.58e+03 ± 125 | 3.13e+03 ± 224; 2.92e+03 ± 455; 2.84e+03 ± 506; 2.74e+03 ± 20; 2.68e+03 ± 14.5; 3.97e+03 ± 236; 3.61e+03 ± 455; 3.58e+03 ± 140; 3.38e+03 ± 32.3; 3.23e+03 ± 238; 3.21e+03 ± 367 | trend | `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_130C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_90C_r1e9` |
| ν, fit up to the E<sub>app</sub> strain, 10⁹ s⁻¹, mean ± SD | 0.25 ± 0.05 | 0.24 ± 0.13 | 0.27 ± 0.00 | 0.33 ± 0.04 | 0.26 ± 0.08; 0.24 ± 0.03; 0.29 ± 0.05; 0.22 ± 0.03; 0.28 ± 0.06; 0.26 ± 0.00; 0.31 ± 0.11; 0.23 ± 0.04; 0.31 ± 0.04; 0.24 ± 0.08; 0.19 ± 0.06 | trend | `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_130C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_90C_r1e9` |
| ν, whole run, 10⁹ s⁻¹, mean ± SD | 0.49 ± 0.02 | 0.47 ± 0.00 | 0.46 ± 0.01 | 0.43 ± 0.01 | 0.47 ± 0.01; 0.49 ± 0.04; 0.46 ± 0.00; 0.45 ± 0.00; 0.45 ± 0.01; 0.48 ± 0.01; 0.50 ± 0.02; 0.48 ± 0.01; 0.50 ± 0.03; 0.49 ± 0.02; 0.49 ± 0.02 | trend | `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_130C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_90C_r1e9` |
| σ<sub>peak</sub> (MPa), 10⁹ s⁻¹, mean ± SD | 3.1e+02 ± 40 | 2.6e+02 ± 33 | 2.1e+02 ± 13 | 1.4e+02 ± 12 | 2.4e+02 ± 13; 2.4e+02 ± 14; 2.4e+02 ± 25; 1.9e+02 ± 19; 1.6e+02 ± 24; 2.9e+02 ± 9.4; 2.8e+02 ± 29; 2.9e+02 ± 19; 2.7e+02 ± 29; 2.6e+02 ± 21; 2.6e+02 ± 25 | trend | `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_130C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_90C_r1e9` |
| ε<sub>peak</sub>, 10⁹ s⁻¹, mean ± SD | 0.137 ± 0.013 | 0.120 ± 0.009 | 0.101 ± 0.009 | 0.091 ± 0.006 | 0.119 ± 0.011; 0.118 ± 0.011; 0.116 ± 0.006; 0.090 ± 0.006; 0.089 ± 0.006; 0.306 ± 0.265; 0.127 ± 0.007; 0.307 ± 0.238; 0.125 ± 0.002; 0.125 ± 0.016; 0.122 ± 0.018 | trend | `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_130C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_90C_r1e9` |
| flow σ (MPa), 10⁹ s⁻¹, mean ± SD | 96 ± 11 | 69 ± 6.2 | 56 ± 4.8 | 43 ± 3.3 | 67 ± 6.8; 45 ± 30; 60 ± 6; 53 ± 6.4; 48 ± 3.5; 1.2e+02 ± 23; 63 ± 43; 1.2e+02 ± 40; 59 ± 40; 78 ± 3.9; 76 ± 0.21 | trend | `tensile_100C_r1e9`, `tensile_110C_r1e9`, `tensile_120C_r1e9`, `tensile_130C_r1e9`, `tensile_140C_r1e9`, `tensile_150C_r1e9`, `tensile_160C_r1e9`, `tensile_25C_r1e9`, `tensile_35C_r1e9`, `tensile_45C_r1e9`, `tensile_55C_r1e9`, `tensile_65C_r1e9`, `tensile_75C_r1e9`, `tensile_85C_r1e9`, `tensile_90C_r1e9` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE UA, 140 chains × C80 (C80H160), 11,200 atoms/beads, force field `trappe_ua`, box density 0.9963 g/cm³ (as built)

**Equilibration**

- Verdict: crystal (no 500 K melt): 15/15 holds stable, 25–160 °C
- C<sub>n</sub> plateau (D37): —

**Stages**

- **crystal** (rdyu-rog): finished; started 2026-11-17 13:48 UTC, ended 2026-11-18 06:36 UTC; reads `systems/pe_ua_crystal_7x10x40_s1/data.lmp`
  - monitor flags: drift seg 5
- **`crystal_fine_a`** (rdyu-rog): finished; started 2026-11-21 00:01 UTC, ended 2026-11-21 03:40 UTC; reads `systems/pe_ua_crystal_7x10x40_s1/data.lmp`
  - monitor flags: drift seg 2
- **`crystal_fine_b`** (rdyu-rog): finished; started 2026-11-21 03:40 UTC, ended 2026-11-21 07:19 UTC; reads `systems/pe_ua_crystal_7x10x40_s1/data.lmp`
  - monitor flags: drift seg 2,3,4
- **`crystal_fine_c`** (rdyu-rog): finished; started 2026-11-21 07:19 UTC, ended 2026-11-21 10:03 UTC; reads `systems/pe_ua_crystal_7x10x40_s1/data.lmp`
  - monitor flags: drift seg 4
- **`tensile_25C_r1e9`** (rdyu-rog): finished; started 2026-11-18 06:36 UTC, ended 2026-11-18 10:51 UTC; reads `../crystal/hold_25C.data`
  - monitor flags: drift seg 1
- **`tensile_90C_r1e9`** (rdyu-rog): finished; started 2026-11-18 10:51 UTC, ended 2026-11-18 15:01 UTC; reads `../crystal/hold_90C.data`
  - monitor flags: drift seg 1,2
- **`tensile_130C_r1e9`** (rdyu-rog): finished; started 2026-11-18 15:01 UTC, ended 2026-11-18 19:08 UTC; reads `../crystal/hold_130C.data`
  - monitor flags: drift seg 1,2
- **`tensile_160C_r1e9`** (rdyu-rog): finished; started 2026-11-18 19:08 UTC, ended 2026-11-18 23:17 UTC; reads `../crystal/hold_160C.data`
  - monitor flags: drift seg 1,2
- **`tensile_35C_r1e9`** (rdyu-rog): finished; started 2026-11-21 10:03 UTC, ended 2026-11-21 10:47 UTC; reads `../crystal_fine_a/hold_35C.data`
  - monitor flags: drift seg 1
- **`tensile_45C_r1e9`** (rdyu-rog): finished; started 2026-11-21 10:47 UTC, ended 2026-11-21 11:30 UTC; reads `../crystal_fine_a/hold_45C.data`
  - monitor flags: drift seg 1,2
- **`tensile_55C_r1e9`** (rdyu-rog): finished; started 2026-11-21 11:31 UTC, ended 2026-11-21 12:13 UTC; reads `../crystal_fine_a/hold_55C.data`
  - monitor flags: drift seg 1,2
- **`tensile_65C_r1e9`** (rdyu-rog): finished; started 2026-11-21 12:13 UTC, ended 2026-11-21 12:55 UTC; reads `../crystal_fine_a/hold_65C.data`
  - monitor flags: drift seg 1,2
- **`tensile_75C_r1e9`** (rdyu-rog): finished; started 2026-11-21 12:55 UTC, ended 2026-11-21 13:37 UTC; reads `../crystal_fine_b/hold_75C.data`
  - monitor flags: drift seg 1
- **`tensile_85C_r1e9`** (rdyu-rog): finished; started 2026-11-21 13:37 UTC, ended 2026-11-21 14:18 UTC; reads `../crystal_fine_b/hold_85C.data`
  - monitor flags: drift seg 1
- **`tensile_100C_r1e9`** (rdyu-rog): finished; started 2026-11-21 14:18 UTC, ended 2026-11-21 14:59 UTC; reads `../crystal_fine_b/hold_100C.data`
  - monitor flags: drift seg 1,2
- **`tensile_110C_r1e9`** (rdyu-rog): finished; started 2026-11-21 14:59 UTC, ended 2026-11-21 15:39 UTC; reads `../crystal_fine_b/hold_110C.data`
  - monitor flags: drift seg 1,2
- **`tensile_120C_r1e9`** (rdyu-rog): finished; started 2026-11-21 15:39 UTC, ended 2026-11-21 16:20 UTC; reads `../crystal_fine_c/hold_120C.data`
  - monitor flags: drift seg 1,2
- **`tensile_140C_r1e9`** (rdyu-rog): finished; started 2026-11-21 16:20 UTC, ended 2026-11-21 17:00 UTC; reads `../crystal_fine_c/hold_140C.data`
  - monitor flags: drift seg 1,2
- **`tensile_150C_r1e9`** (rdyu-rog): finished; started 2026-11-21 17:00 UTC, ended 2026-11-21 17:40 UTC; reads `../crystal_fine_c/hold_150C.data`
  - monitor flags: drift seg 1,2

**`crystal` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:26 UTC on rdyu-server, run finished; crystallinity uncalibrated, melt baseline.

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 25 | yes | 1.000 | 1.01447 ± 0.00047 | 7.877 ± 0.006 | 4.550 ± 0.003 | 2.5623 ± 9e-05 | `c_A`, density, `volume_A3`, `area_per_chain_A2` |
| 90 | yes | 1.000 | 0.99779 ± 0.00028 | 7.952 ± 0.001 | 4.592 ± 0.001 | 2.5569 ± 7e-05 | density, `volume_A3`, `area_per_chain_A2` |
| 130 | yes | 0.999 | 0.98689 ± 0.00006 | 8.004 ± 0.0008 | 4.622 ± 0.0004 | 2.5521 ± 0.0001 | — |
| 160 | yes | 0.998 | 0.97640 ± 0.00020 | 8.058 ± 0.001 | 4.652 ± 0.0007 | 2.5455 ± 0.0002 | — |

- α<sub>V</sub> 2.791 ± 0.137 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`crystal_fine_a` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:26 UTC on rdyu-server, run finished; crystallinity uncalibrated, melt baseline.

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 35 | yes | 1.000 | 1.01239 ± 0.00024 | 7.879 ± 0.004 | 4.560 ± 0.002 | 2.5619 ± 8e-05 | density, `volume_A3`, `area_per_chain_A2` |
| 45 | yes | 1.000 | 1.00893 ± 0.00011 | 7.901 ± 0.002 | 4.564 ± 0.0007 | 2.5609 ± 4e-05 | — |
| 55 | yes | 1.000 | 1.00593 ± 0.00007 | 7.920 ± 0.003 | 4.568 ± 0.002 | 2.5600 ± 4e-05 | density, `volume_A3`, `area_per_chain_A2` |
| 65 | yes | 1.000 | 1.00354 ± 0.00006 | 7.923 ± 0.0009 | 4.579 ± 0.0008 | 2.5592 ± 3e-05 | — |

- α<sub>V</sub> 2.948 ± 0.157 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`crystal_fine_b` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:27 UTC on rdyu-server, run finished; crystallinity uncalibrated, melt baseline.

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 75 | yes | 1.000 | 1.00280 ± 0.00031 | 7.929 ± 0.001 | 4.580 ± 0.001 | 2.5586 ± 6e-05 | density, `volume_A3`, `area_per_chain_A2` |
| 85 | yes | 1.000 | 0.99926 ± 0.00011 | 7.946 ± 0.001 | 4.588 ± 0.0005 | 2.5577 ± 8e-05 | — |
| 100 | yes | 1.000 | 0.99474 ± 0.00013 | 7.967 ± 0.001 | 4.600 ± 0.0006 | 2.5558 ± 3e-05 | — |
| 110 | yes | 1.000 | 0.99257 ± 0.00010 | 7.977 ± 0.001 | 4.606 ± 0.0009 | 2.5549 ± 0.0001 | `c_A`, `area_per_chain_A2` |

- α<sub>V</sub> 2.936 ± 0.177 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`crystal_fine_c` analysis**

`sepsim analyze crystal`, generated 2026-11-23 18:27 UTC on rdyu-server, run finished; crystallinity uncalibrated, melt baseline.

| T (°C) | stable | crystallinity | ρ (g/cm³) | a (Å) | b (Å) | c (Å) | drift |
|---|---|---|---|---|---|---|---|
| 120 | yes | 1.000 | 0.99076 ± 0.00054 | 7.987 ± 0.003 | 4.610 ± 0.002 | 2.5538 ± 0.0004 | `a_A`, `b_A`, `c_A`, density, `volume_A3`, `area_per_chain_A2` |
| 140 | yes | 0.999 | 0.98367 ± 0.00009 | 8.021 ± 0.001 | 4.630 ± 0.0004 | 2.5505 ± 9e-05 | — |
| 150 | yes | 0.999 | 0.98024 ± 0.00041 | 8.038 ± 0.002 | 4.640 ± 0.001 | 2.5483 ± 0.0003 | `a_A`, `b_A`, `c_A`, density, `volume_A3`, `area_per_chain_A2` |

- α<sub>V</sub> 3.537 ± 0.013 × 10⁻⁴ K⁻¹ (from the volume)

- Note: A periodic perfect crystal of infinite stems has no surfaces, ends or defects to nucleate melting: it superheats, so a hold or ramp that stays crystalline bounds its stability from above; it is not the melting point.
- Note: CG (SDK) beads carry no setting angle: the stems pack as the model prefers (a/b = √3 is hexagonal); a, b and c of the CG crystal are not the orthorhombic PE cell.
- Note: The barostat is anisotropic (x, y, z independent, couple none); the stems stay along z only while the crystal holds.
- Note: Elastic constants from the box-length fluctuations of the NPT holds (Parrinello-Rahman/Ray strain-fluctuation formula, T = the set point): the box is orthogonal, so the shear strains are fixed and only the normal-normal block of the compliance is sampled; it equals the normal block of the full S only if the normal-shear couplings vanish, assumed here by the orthorhombic (or pseudo-hexagonal, stems along z) symmetry. They are static (zero-rate, isothermal) constants of the model crystal, to compare with the rate-dependent tensile E<sub>app</sub>; they rest on the MTK (Nose-Hoover) barostat sampling the NPT ensemble (Pdamp 1000 dt, frames 1 ps apart), and fluctuation estimates converge slowly: the halves check flags E that differ by more than 2 sigma between the first and second half of the hold.
- Note: `E_z` is along the covalent stems, each bonded to its own periodic image (infinite chains with no ends or folds): a model property, an upper bound for real crystalline stems.

**`tensile_100C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

100 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.28e+03 ± 2.1e+02 | 0.21 | 0.47 | 2.5e+02 | 0.111 | 72 | 373.2 |
| y | 0.500 | 2.97e+03 ± 2.2e+02 | 0.31 | 0.48 | 2.3e+02 | 0.127 | 62 | 373.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_110C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

110 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.25e+03 ± 1.7e+02 | 0.22 | 0.46 | 2.5e+02 | 0.110 | 66 | 383.2 |
| y | 0.500 | 2.6e+03 ± 2.3e+02 | 0.27 | 0.52 | 2.3e+02 | 0.126 | 24 | 383.3 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_120C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

120 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.2e+03 ± 2.5e+02 | 0.26 | 0.46 | 2.6e+02 | 0.112 | 64 | 393.1 |
| y | 0.500 | 2.48e+03 ± 2.6e+02 | 0.33 | 0.47 | 2.2e+02 | 0.121 | 56 | 393.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_130C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

130 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.27e+03 ± 2.5e+02 | 0.27 | 0.45 | 2.2e+02 | 0.095 | 60 | 403.1 |
| y | 0.500 | 2.79e+03 ± 2.8e+02 | 0.27 | 0.46 | 2e+02 | 0.108 | 53 | 403.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_140C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

140 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 2.75e+03 ± 2.4e+02 | 0.20 | 0.45 | 2e+02 | 0.094 | 57 | 413.1 |
| y | 0.500 | 2.73e+03 ± 2.4e+02 | 0.24 | 0.45 | 1.7e+02 | 0.086 | 48 | 413.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_150C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

150 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 2.67e+03 ± 2.2e+02 | 0.32 | 0.45 | 1.8e+02 | 0.093 | 51 | 423.1 |
| y | 0.500 | 2.69e+03 ± 2.5e+02 | 0.24 | 0.45 | 1.5e+02 | 0.085 | 46 | 423.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_160C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

160 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 2.67e+03 ± 2.5e+02 | 0.36 | 0.43 | 1.5e+02 | 0.096 | 45 | 433.2 |
| y | 0.500 | 2.49e+03 ± 2.9e+02 | 0.31 | 0.44 | 1.4e+02 | 0.087 | 40 | 433.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_25C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

25 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 4.3e+03 ± 1.3e+02 | 0.21 | 0.48 | 3.3e+02 | 0.147 | 1e+02 | 298.3 |
| y | 0.500 | 3.91e+03 ± 1.8e+02 | 0.28 | 0.51 | 2.8e+02 | 0.128 | 89 | 298.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_35C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

35 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 4.14e+03 ± 2e+02 | 0.26 | 0.48 | 3e+02 | 0.119 | 99 | 308.1 |
| y | 0.500 | 3.8e+03 ± 1.4e+02 | 0.26 | 0.49 | 2.9e+02 | 0.494 | 1.3e+02 | 308.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_45C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

45 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.93e+03 ± 2.6e+02 | 0.23 | 0.48 | 3e+02 | 0.122 | 94 | 318.1 |
| y | 0.500 | 3.29e+03 ± 2.2e+02 | 0.38 | 0.51 | 2.6e+02 | 0.132 | 33 | 318.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_55C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

55 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.68e+03 ± 2.1e+02 | 0.20 | 0.48 | 3.1e+02 | 0.139 | 92 | 328.2 |
| y | 0.500 | 3.48e+03 ± 1.6e+02 | 0.26 | 0.49 | 2.8e+02 | 0.475 | 1.5e+02 | 328.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_65C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

65 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.41e+03 ± 2.1e+02 | 0.34 | 0.48 | 3e+02 | 0.127 | 87 | 338.2 |
| y | 0.500 | 3.36e+03 ± 2.2e+02 | 0.28 | 0.52 | 2.5e+02 | 0.124 | 31 | 338.3 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_75C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

75 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.4e+03 ± 2.3e+02 | 0.18 | 0.47 | 2.8e+02 | 0.114 | 81 | 348.1 |
| y | 0.500 | 3.07e+03 ± 2.3e+02 | 0.30 | 0.50 | 2.5e+02 | 0.136 | 75 | 348.2 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_85C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:15 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

85 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.47e+03 ± 2.2e+02 | 0.15 | 0.47 | 2.8e+02 | 0.110 | 76 | 358.1 |
| y | 0.500 | 2.95e+03 ± 2.1e+02 | 0.23 | 0.51 | 2.5e+02 | 0.135 | 76 | 358.3 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

**`tensile_90C_r1e9` analysis**

`sepsim analyze tensile`, generated 2026-11-23 17:16 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

90 °C, 10⁹ s⁻¹ to strain 0.5, run finished on rdyu-rog:

| pull axis | strain reached | E<sub>app</sub> (MPa) | ν, fit | ν, whole run | σ<sub>peak</sub> (MPa) | ε<sub>peak</sub> | flow σ (MPa) | T (K) |
|---|---|---|---|---|---|---|---|---|
| x | 0.500 | 3.34e+03 ± 1.7e+02 | 0.15 | 0.47 | 2.8e+02 | 0.114 | 74 | 363.1 |
| y | 0.500 | 3e+03 ± 2e+02 | 0.34 | 0.48 | 2.3e+02 | 0.127 | 65 | 363.1 |

- Note: The box is a defect-free periodic single crystal (D59: straight stems along z, each bonded to its own periodic image; no chain ends, amorphous phase, grain boundaries or lamellar interfaces), so these are not the moduli of a semicrystalline separator.
- Note: The load is transverse to the chain axis (x, y): E<sub>app</sub> is the transverse modulus of the crystal, governed by the interchain non-bonded (van der Waals) interactions, and much lower than the modulus along the covalent chain axis (z, not a default axis).
- Note: E<sub>app</sub> is the apparent modulus at the simulated strain rate, many orders of magnitude above experiment; E<sub>app</sub> and the peak stress are rate-dependent.
- Note: The peak is the transverse yield or failure of a perfect crystal (an ideal strength: no defects or interfaces to start it), not the yield stress of a separator; the flow stress after it is that of the yielded crystal, not a viscous melt flow.
- Note: ν is biased at high rate: the lateral barostat (Pdamp = 1000 dt, the two lateral axes independent, couple none) lags the imposed strain. The two lateral axes are inequivalent (one transverse, one along the stems) and contract differently, so ν, their mean, is not an isotropic Poisson ratio (per-axis lateral strains in results.json).
- Note: Stress is -(P<sub>axis</sub> - p<sub>atm</sub>) from the virial pressure tensor averaged over `avg_ps`; the axes of one run start from the same snapshot, so their spread is not a full independent-sample error.
- Note: --fit steepest: E<sub>app</sub> comes from the steepest window before the peak, which skips a soft toe at small strain (e.g. the UA crystal at 1e9 /s); the maximum over windows biases E<sub>app</sub> up by about its noise.

</details>

### `pe_ua_amorph_n40_c240_s1`

PE UA, bulk amorphous box, 40 chains × C240, 9,600 united atoms; grown chains (seed 1). Status: finished: prep, extend (stopped after D47 PASS), cool, sweep.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | — | `extend` progress |
| ρ (g/cm³) | 0.86142 ± 0.00045 | 0.82268 ± 0.00035 | 0.80014 ± 0.00016 | 0.78336 ± 0.00025 | 500 K: 0.74581 ± 0.00008; 0.81729 ± 0.00018; 0.81170 ± 0.00026; 0.80559 ± 0.00021; 0.79360 ± 0.00026; 0.78838 ± 0.00023; 0.85720 ± 0.00021; 0.85081 ± 0.00028; 0.84468 ± 0.00034; 0.83691 ± 0.00023; 0.83182 ± 0.00023; 0.82523 ± 0.00033 | comp | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.681 ± 0.036 | 0.884 ± 0.026 | 1.117 ± 0.023 | 1.192 ± 0.024 | 500 K: 1.632 ± 0.012; 0.900 ± 0.023; 1.029 ± 0.026; 1.018 ± 0.029; 1.178 ± 0.029; 1.199 ± 0.030; 0.662 ± 0.026; 0.716 ± 0.026; 0.789 ± 0.042; 0.794 ± 0.031; 0.801 ± 0.039; 0.895 ± 0.032 | comp | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 7.151 ± 0.057 (χ²<sub>red</sub> 5.03); 25–90 °C: 6.946 ± 0.200 (χ²<sub>red</sub> 6.04); 90–160 °C: 7.007 ± 0.067 (χ²<sub>red</sub> 1.19) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 2.431 ± 0.011 (χ²<sub>red</sub> 18.7); 25–90 °C: 2.439 ± 0.041 (χ²<sub>red</sub> 26.4); 90–160 °C: 2.385 ± 0.019 (χ²<sub>red</sub> 9.98) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 8.19 (melt 6.7) | comp | `extend` progress |
| R<sub>g</sub> (Å) | 29.33 ± 0.07 | 29.95 ± 0.10 | 30.91 ± 0.34 | 29.59 ± 0.14 | 29.22 ± 0.10; 29.78 ± 0.13; 30.81 ± 0.18; 30.27 ± 0.15; 28.89 ± 0.41; 29.66 ± 0.05; 29.49 ± 0.06; 29.73 ± 0.05; 30.14 ± 0.07; 29.99 ± 0.06; 30.03 ± 0.08 | trend | `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| R<sub>g</sub> (Å), 500 K hold | — | — | — | — | 500 K: 27.32 ± 0.46 | comp | `extend` |
| R<sub>ee</sub> (Å) | 72.9 ± 0.4 | 74.3 ± 1.3 | 78.9 ± 1.9 | 75.7 ± 0.8 | 73.4 ± 0.5; 76.4 ± 0.7; 80.1 ± 0.9; 77.3 ± 0.5; 70.8 ± 1.0; 71.8 ± 0.4; 72.7 ± 0.3; 73.2 ± 0.2; 78.3 ± 0.6; 78.5 ± 0.7; 75.5 ± 0.8 | trend | `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| R<sub>ee</sub> (Å), 500 K hold | — | — | — | — | 500 K: 68.7 ± 1.4 | comp | `extend` |
| C<sub>n</sub> | 9.21 ± 0.01 | 9.86 ± 0.14 | 10.86 ± 0.34 | 9.85 ± 0.10 | 9.35 ± 0.12; 9.92 ± 0.09; 10.81 ± 0.20; 10.39 ± 0.13; 9.11 ± 0.31; 9.34 ± 0.04; 9.26 ± 0.06; 9.49 ± 0.03; 10.19 ± 0.07; 10.07 ± 0.05; 9.97 ± 0.05 | trend | `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| C<sub>n</sub>, 500 K hold | — | — | — | — | 500 K: 8.19 ± 0.35 | comp | `extend` |
| P2 1/e time (ps) | 60.1 | 11.1 | 5.43 | 3.6 | 500 K: 6.96; 8.8; 7.76; 6.46; 4.83; 4.12; 43.2; 32; 24.6; 18.9; 15.6; 12.7 | corr | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| segment MSD at 1 ns lag (Å²) | 28.3 | 117.7 | 177.6 | 237.4 | 500 K: 365.1; 128; 150.5; 167.3; 204.1; 223.6; 36.62; 47.32; 60.99; 75.1; 89.86; 102.9 | corr | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| max chain COM MSD (Å²) at lag | 7.53 at 5 ns | 47.79 at 5 ns | 91.35 at 5 ns | 121.5 at 5 ns | 500 K: 1699 at 49.1 ns; 51.52 at 5 ns; 59.96 at 5 ns; 74.06 at 5 ns; 88.79 at 5 ns; 101.8 at 5 ns; 10.57 at 5 ns; 14.94 at 5 ns; 20.07 at 5 ns; 28.63 at 5 ns; 32.17 at 5 ns; 40.92 at 5 ns | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.01 | 0.05 | 0.10 | 0.14 | 500 K: 2.28; 0.06; 0.07; 0.08; 0.10; 0.12; 0.01; 0.02; 0.02; 0.03; 0.04; 0.05 | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.84) | not diffusive (slope 0.83) | not diffusive (slope 0.89) | not diffusive (slope 0.96) | 500 K: not diffusive (slope 0.89); not diffusive (slope 0.83); not diffusive (slope 0.93); not diffusive (slope 0.81); not diffusive (slope 0.66); not diffusive (slope 0.92); not diffusive (slope 0.69); not diffusive (slope 0.84); not diffusive (slope 0.54); not diffusive (slope 0.61); not diffusive (slope 0.49); not diffusive (slope 0.93) | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached (extrap. 49.2) | not reached (extrap. 29.4) | not reached (extrap. 28.1) | 500 K: 19.3; not reached (extrap. 42.7); not reached (extrap. 39.7); not reached (extrap. 48.1); not reached (extrap. 28.9); not reached (extrap. 18.2); not reached; not reached; not reached; not reached; not reached; not reached (extrap. 165) | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | 500 K: 25.9; not reached; not reached; not reached; not reached; not reached (extrap. 89.8); not reached; not reached; not reached; not reached; not reached; not reached | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.122 | 0.053 | 0.036 | 0.030 | 500 K: 0.021; 0.045; 0.045; 0.036; 0.032; 0.029; 0.141; 0.116; 0.105; 0.064; 0.063; 0.050 | — | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE UA, 40 chains × C240 (C240H482), 9,600 atoms/beads, force field `trappe_ua`, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)

**Stages**

- **prep** (rdyu-server): finished; started 2026-10-20 23:57 UTC, ended 2026-10-23 17:30 UTC; reads `systems/pe_ua_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.47 at 10.0 ns, 1/e not reached; COM MSD/⟨R<sub>g</sub>²⟩ 0.63); C<sub>n</sub> 7.31 vs 6.7 (in band, info); drift (Δ +1.59 ± 0.37)
  - monitor flags: R<sub>ee</sub> not decorrelated (0.47 at 10.0 ns); MSD/R<sub>g</sub>² 0.63; drift seg 13
- **extend** (rdyu-server): stopped after D47 PASS (cancelled/killed?), 97.7%; started 2026-10-23 19:05 UTC; reads `../prep/hold.data`
  - 500 K hold 98.2 ns: D47 PASS (R<sub>ee</sub> ACF 0.16 at 49.1 ns, 1/e at 19.27 ns; COM MSD/⟨R<sub>g</sub>²⟩ 2.28); C<sub>n</sub> 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)
- **cool** (rdyu-server): finished; started 2026-10-29 11:30 UTC, ended 2026-10-30 15:50 UTC; reads `../extend/hold_ext_70ns.data`
  - monitor flags: drift seg 3,4,7; hyst max 0.36%
- **sweep** (rdyu-server): finished; started 2026-10-30 15:50 UTC, ended 2026-11-04 22:09 UTC; reads `../cool/cooled.data`
  - monitor flags: drift seg 2,5,11,13,16; step!=hold 90 C,130 C; hyst max 0.36%
- Superseded (not used): `sweep_old_unrelaxed_cancelled` (cancelled/killed?)

**`extend` analysis**

`sepsim analyze hold`, generated 2026-11-09 18:54 UTC on rdyu-server, run started; segment Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm; 98.19 ns analysed of 80 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (49.1 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`fine_100C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:37 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 100 | 0.81729 ± 0.00018 | 0.900 ± 0.023 | 29.22 ± 0.10 | 73.4 ± 0.5 | 9.35 ± 0.12 | 8.8 | 51.52 at 5 ns | not diffusive (slope 0.83) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_110C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:37 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 110 | 0.81170 ± 0.00026 | 1.029 ± 0.026 | 29.78 ± 0.13 | 76.4 ± 0.7 | 9.92 ± 0.09 | 7.76 | 59.96 at 5 ns | not diffusive (slope 0.93) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_120C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:37 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 120 | 0.80559 ± 0.00021 | 1.018 ± 0.029 | 30.81 ± 0.18 | 80.1 ± 0.9 | 10.81 ± 0.20 | 6.46 | 74.06 at 5 ns | not diffusive (slope 0.81) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_140C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:37 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 140 | 0.79360 ± 0.00026 | 1.178 ± 0.029 | 30.27 ± 0.15 | 77.3 ± 0.5 | 10.39 ± 0.13 | 4.83 | 88.79 at 5 ns | not diffusive (slope 0.66) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_150C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:38 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 150 | 0.78838 ± 0.00023 | 1.199 ± 0.030 | 28.89 ± 0.41 | 70.8 ± 1.0 | 9.11 ± 0.31 | 4.12 | 101.8 at 5 ns | not diffusive (slope 0.92) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_35C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:35 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 35 | 0.85720 ± 0.00021 | 0.662 ± 0.026 | 29.66 ± 0.05 | 71.8 ± 0.4 | 9.34 ± 0.04 | 43.2 | 10.57 at 5 ns | not diffusive (slope 0.69) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_45C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:35 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 45 | 0.85081 ± 0.00028 | 0.716 ± 0.026 | 29.49 ± 0.06 | 72.7 ± 0.3 | 9.26 ± 0.06 | 32 | 14.94 at 5 ns | not diffusive (slope 0.84) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_55C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:35 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 55 | 0.84468 ± 0.00034 | 0.789 ± 0.042 | 29.73 ± 0.05 | 73.2 ± 0.2 | 9.49 ± 0.03 | 24.6 | 20.07 at 5 ns | not diffusive (slope 0.54) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_65C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:36 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 65 | 0.83691 ± 0.00023 | 0.794 ± 0.031 | 30.14 ± 0.07 | 78.3 ± 0.6 | 10.19 ± 0.07 | 18.9 | 28.63 at 5 ns | not diffusive (slope 0.61) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_75C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:36 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 75 | 0.83182 ± 0.00023 | 0.801 ± 0.039 | 29.99 ± 0.06 | 78.5 ± 0.7 | 10.07 ± 0.05 | 15.6 | 32.17 at 5 ns | not diffusive (slope 0.49) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_85C` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-22 18:36 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 85 | 0.82523 ± 0.00033 | 0.895 ± 0.032 | 30.03 ± 0.08 | 75.5 ± 0.8 | 9.97 ± 0.05 | 12.7 | 40.92 at 5 ns | not diffusive (slope 0.93) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.47 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.63, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 7.31 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`sweep` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-07 03:43 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.86142 ± 0.00045 | 0.681 ± 0.036 | 29.33 ± 0.07 | 72.9 ± 0.4 | 9.21 ± 0.01 | 60.1 | 7.53 at 5 ns | not diffusive (slope 0.84) | yes |
| 90 | 0.82268 ± 0.00035 | 0.884 ± 0.026 | 29.95 ± 0.10 | 74.3 ± 1.3 | 9.86 ± 0.14 | 11.1 | 47.79 at 5 ns | not diffusive (slope 0.83) | yes |
| 130 | 0.80014 ± 0.00016 | 1.117 ± 0.023 | 30.91 ± 0.34 | 78.9 ± 1.9 | 10.86 ± 0.34 | 5.43 | 91.35 at 5 ns | not diffusive (slope 0.89) | yes |
| 160 | 0.78336 ± 0.00025 | 1.192 ± 0.024 | 29.59 ± 0.14 | 75.7 ± 0.8 | 9.85 ± 0.10 | 3.6 | 121.5 at 5 ns | not diffusive (slope 0.96) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 7.151 ± 0.057 | 5.03 | 2.431 ± 0.011 | 18.7 | 15 |
| 90–160 | 7.007 ± 0.067 | 1.19 | 2.385 ± 0.019 | 9.98 | 8 |
| 25–90 | 6.946 ± 0.200 | 6.04 | 2.439 ± 0.041 | 26.4 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: D37 chain check FAIL on the prep hold + extension: C<sub>n</sub> plateau 8.19 vs melt 6.7 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

</details>

### `pe_ua_pore500k_w10nm_n40_c240_s1`

PE UA, wide 10 nm slit pore made at 500 K, 40 chains × C240, 9,600 united atoms; built from `pe_ua_amorph_n40_c240_s1` (`extend/hold_ext_70ns.data`). Status: finished: `pore_relax`.

No analysed properties yet. Equilibration: from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE UA, 40 chains × C240 (C240H482), 9,600 atoms/beads, force field `trappe_ua`, box density 0.2989 g/cm³ (as built)
- Pore: wide pore, nominal 10 nm, wall 6.70 nm, clear gap 2.71 nm, area 44.8 nm²
- Built from: `pe_ua_amorph_n40_c240_s1` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)

**Stages**

- **`pore_relax`** (rdyu-rog): finished; started 2026-11-04 05:54 UTC, ended 2026-11-04 08:14 UTC; reads `systems/pe_ua_pore500k_w10nm_n40_c240_s1/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| wide | 10 nm (at 500 K) | — | 6.7 nm (500 K) | 6.7 × 6.7 nm (500 K) | — | finished: `pore_relax` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_ua_pore_w5nm_n40_c240_s1`

PE UA, 5 nm dry slit pore, 40 chains × C240, 9,600 united atoms; built from `pe_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`). Status: finished: pore.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `pe_ua_pore500k_w10nm_n40_c240_s1` ← `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | — | `extend` progress of `pe_ua_amorph_n40_c240_s1` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 8.19 (melt 6.7) | n/a | `extend` progress of `pe_ua_amorph_n40_c240_s1` |
| R<sub>g</sub> (Å) | 27.85 ± 0.17 | 27.96 ± 0.11 | 25.56 ± 0.20 | 25.94 ± 0.12 | — | trend | `pore` |
| R<sub>ee</sub> (Å) | 68.9 ± 1.1 | 70.2 ± 0.8 | 61.3 ± 1.0 | 61.8 ± 0.5 | — | trend | `pore` |
| C<sub>n</sub> | 8.10 ± 0.10 | 8.38 ± 0.14 | 6.62 ± 0.12 | 6.93 ± 0.08 | — | trend | `pore` |
| P2 1/e time (ps) | 43.3 | 8.46 | 4.51 | 3.11 | — | corr | `pore` |
| P2 1/e time, surface layer (ps) | 35.5 | 7.31 | 4.12 | 2.84 | — | corr | `pore` |
| P2 1/e time, interior layer (ps) | 51.1 | 9.63 | 4.96 | 3.48 | — | corr | `pore` |
| segment MSD at 1 ns lag (Å²) | 54.34 | 171.7 | 265.3 | 317.6 | — | corr | `pore` |
| max chain COM MSD (Å²) at lag | 16.23 at 5 ns | 76.55 at 5 ns | 115.9 at 5 ns | 140.4 at 5 ns | — | n/a | `pore` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.02 | 0.10 | 0.18 | 0.21 | — | n/a | `pore` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.64) | not diffusive (slope 0.80) | not diffusive (slope 0.58) | not diffusive (slope 0.62) | — | n/a | `pore` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached (extrap. 32.2) | not reached (extrap. 14.4) | not reached (extrap. 15.3) | — | n/a | `pore` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached (extrap. 34.2) | not reached (extrap. 28.6) | — | n/a | `pore` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.119 | 0.054 | 0.042 | 0.033 | — | — | `pore` |
| γ, run monitor (mN/m) | 33.0 ± 2.8 | 26.2 ± 2.5 | 22.3 ± 2.6 | 13.3 ± 3.0 | — | comp | `pore` progress |
| γ, analysis (mN/m) | 32.3 ± 1.9 | 25.0 ± 1.9 | 24.2 ± 1.9 | 17.8 ± 2.7 | — | comp | `pore` |
| dγ/dT (mN m⁻¹ K⁻¹) | — | — | — | — | cooling branch 25–201.6 °C: -0.0732 ± 0.0374 (χ²<sub>red</sub> 1.06); heating sweep 25–160 °C: -0.1031 ± 0.0191 (χ²<sub>red</sub> 0.632) | comp | `pore` |
| γ at 25 °C from the dγ/dT fit (mN/m) | — | — | — | — | cooling branch: 31.59; heating sweep: 33.24 | comp | `pore` |
| film thickness between the Gibbs surfaces (Å) | 64.91 ± 0.05 | 66.21 ± 0.03 | 67.09 ± 0.03 | 67.84 ± 0.03 | — | trend | `pore` |
| gap between the Gibbs surfaces (Å) | 48.85 | 47.55 | 46.68 | 45.93 | — | trend | `pore` |
| film interior density (g/cm³) | 0.8466 ± 0.0007 | 0.8046 ± 0.0003 | 0.7795 ± 0.0003 | 0.7599 ± 0.0004 | — | trend | `pore` |
| interfacial width, 10–90 % (Å) | 5.59 | 7.10 | 8.19 | 8.69 | — | trend | `pore` |
| closest approach across the gap (Å) | 41.8 | 37.9 | 35.6 | 34.3 | — | trend | `pore` |
| film α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 8.023; 25–90 °C: 7.703; 90–160 °C: 8.056 | — | `pore` |
| α<sub>z</sub>, film-thickness expansion (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 3.271 ± 0.073 (χ²<sub>red</sub> 2.01); 25–90 °C: 3.070 ± 0.118 (χ²<sub>red</sub> 0.461); 90–160 °C: 3.387 ± 0.148 (χ²<sub>red</sub> 3.04) | — | `pore` |
| C<sub>v</sub> of the film, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 2.423 ± 0.008 (χ²<sub>red</sub> 20.7); 25–90 °C: 2.481 ± 0.009 (χ²<sub>red</sub> 2.26); 90–160 °C: 2.375 ± 0.011 (χ²<sub>red</sub> 6.89) | — | `pore` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE UA, 40 chains × C240 (C240H482), 9,600 atoms/beads, force field `trappe_ua`, box density 0.4387 g/cm³ (as built)
- Pore: narrow pore, nominal 5 nm, 4.68 nm at 500 K, wall 6.38 nm, clear gap 2.25 nm, area 44.8 nm²
- Built from: `pe_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`) ← `pe_ua_amorph_n40_c240_s1` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_ua_pore500k_w10nm_n40_c240_s1` ← `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)

**Stages**

- **pore** (rdyu-server): finished; started 2026-11-04 22:15 UTC, ended 2026-11-11 11:40 UTC; reads `systems/pe_ua_pore_w5nm_n40_c240_s1/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 33.0 ± 2.8; 90 °C 26.2 ± 2.5; 130 °C 22.3 ± 2.6; 160 °C 13.3 ± 3.0

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.68 nm | 6.4 nm | 6.4 × 6.4 nm (25 °C) | 25 °C 33.0 ± 2.8; 90 °C 26.2 ± 2.5; 130 °C 22.3 ± 2.6; 160 °C 13.3 ± 3.0 | finished: pore | pore |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`pore` analysis**

Pore analysis (`sepsim analyze pore`, generated 2026-11-11 11:40 UTC on rdyu-server):

- dγ/dT, cooling-branch fit (mN m⁻¹ K⁻¹): -0.0732
- γ at 25 °C, cooling-branch fit (mN/m): 31.59
- dγ/dT, heating-sweep fit (mN m⁻¹ K⁻¹): -0.1031
- γ at 25 °C, heating-sweep fit (mN/m): 33.24
- analysis node: rdyu-server
- nominal gap width (nm): 5
- wall (film) thickness (Å): 63.76

Convergence of the film quantities, per segment:

| γ (mN/m) | segment end (ps) | gap between the Gibbs surfaces (Å) | film interior density (g/cm³) |
|---|---|---|---|
| 14.15 ± 8.87 | 1000 | — | — |
| 24.65 ± 6.983 | 3000 | — | — |
| 25.29 ± 5.955 | 5000 | — | — |
| 11.88 ± 6.455 | 7000 | — | — |
| 17.11 ± 7.961 | 9000 | — | — |
| 25.19 ± 6.635 | 1.1e+04 | — | — |
| 31.34 ± 5.448 | 1.3e+04 | — | — |
| 25.98 ± 5.2 | 1.5e+04 | — | — |
| 35.78 ± 5.323 | 1.7e+04 | — | — |
| 32.26 ± 1.85 | 2.7e+04 | 48.84 ± 0.05456 | 0.8466 ± 0.0007095 |
| 28.94 ± 6.919 | 2.9e+04 | 48.71 ± 0.08034 | 0.841 ± 0.001041 |
| 36.53 ± 5.28 | 3.1e+04 | 48.41 ± 0.06009 | 0.8331 ± 0.0007658 |
| 32.71 ± 7.928 | 3.3e+04 | 48.23 ± 0.1443 | 0.8276 ± 0.001815 |
| 31.48 ± 5.431 | 3.5e+04 | 48.2 ± 0.1367 | 0.8227 ± 0.001717 |
| 34.45 ± 5.55 | 3.7e+04 | 47.85 ± 0.1096 | 0.8149 ± 0.00136 |
| 30.01 ± 6.449 | 3.9e+04 | 47.58 ± 0.09315 | 0.8087 ± 0.001145 |
| 23.15 ± 5.557 | 4.1e+04 | 47.53 ± 0.1924 | 0.8045 ± 0.002351 |
| 25.03 ± 1.899 | 5.1e+04 | 47.54 ± 0.02638 | 0.8046 ± 0.0003212 |
| 27.55 ± 5.79 | 5.3e+04 | 47.11 ± 0.1334 | 0.7961 ± 0.001584 |
| 25.83 ± 5.774 | 5.5e+04 | 46.63 ± 0.1511 | 0.7859 ± 0.001759 |
| 27.4 ± 5.434 | 5.7e+04 | 46.63 ± 0.1611 | 0.7828 ± 0.001879 |
| 25.93 ± 5.885 | 5.9e+04 | 46.67 ± 0.1294 | 0.7795 ± 0.0015 |
| 24.21 ± 1.909 | 6.9e+04 | 46.67 ± 0.03295 | 0.7795 ± 0.0003821 |
| 12.93 ± 5.915 | 7.1e+04 | 46.45 ± 0.1289 | 0.7735 ± 0.001487 |
| 17.29 ± 5.939 | 7.3e+04 | 46.31 ± 0.1234 | 0.7684 ± 0.001407 |
| 21.14 ± 5.759 | 7.5e+04 | 46.03 ± 0.2186 | 0.7612 ± 0.002463 |
| 17.76 ± 2.719 | 8.5e+04 | 45.92 ± 0.03516 | 0.7599 ± 0.0003959 |

Per hold: film vs bulk:

| bulk: max chain COM MSD (Å²) | bulk ρ (g/cm³) | bulk: max segment MSD (Å²) | film: C<sub>n</sub> | film: max lag (ps) | film: max chain COM MSD (Å²) | film: chain COM MSD / ⟨R<sub>g</sub>²⟩ at max lag | film: COM MSD log-slope at max lag | film: largest COM MSD log-slope | film: largest ordered cluster, mean (sites) | film: hold length (ns) | `film.segment_msd.lag_max_ps` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 7.53 | 0.8614 ± 0.0004505 | 82.09 | 8.098 ± 0.09729 | 5000 | 16.23 | 0.02091 | 0.6378 | 1.846 | 616.9 | 10 | 5000 |
| 47.79 | 0.8227 ± 0.0003516 | 317.3 | 8.376 ± 0.14 | 5000 | 76.55 | 0.09795 | 0.8047 | 1.866 | 89.68 | 10 | 5000 |
| 91.35 | 0.8001 ± 0.000164 | 493.1 | 6.618 ± 0.1234 | 5000 | 115.9 | 0.1775 | 0.581 | 1.877 | 48.12 | 10 | 5000 |
| 121.5 | 0.7834 ± 0.0002476 | 585.6 | 6.933 ± 0.07937 | 5000 | 140.4 | 0.2087 | 0.6211 | 1.883 | 26.26 | 10 | 5000 |

Per segment:

| γ drift: second − first half (mN/m) | γ, first half (mN/m) | γ, second half (mN/m) | SEM of the γ drift (mN/m) | potential-energy drift: second − first half | box density (g/cm³) | γ (mN/m) | T (°C) | set T (°C) | SEM of γ from 16 blocks (mN/m) | SEM of γ from 32 blocks (mN/m) | SEM of γ from 8 blocks (mN/m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| -17.07 | 23.37 | 6.298 | 17.59 | -19.64 | 0.4387 ± 0 | 14.15 ± 8.87 | 227.1 ± 0.1813 | 226.9 | — | — | — |
| -13.98 | 31.87 | 17.89 | 15.42 | -33.13 | 0.4439 ± 0 | 24.65 ± 6.983 | 201.4 ± 0.1393 | 201.6 | — | — | — |
| 11.26 | 19.93 | 31.18 | 11.91 | -34.1 | 0.4492 ± 0 | 25.29 ± 5.955 | 176.4 ± 0.1146 | 176.4 | — | — | — |
| 0.1092 | 11.78 | 11.89 | 14.99 | 37.4 | 0.4547 ± 0 | 11.88 ± 6.455 | 151 ± 0.1311 | 151.2 | — | — | — |
| -20.05 | 27.06 | 7.005 | 12.08 | 45.04 | 0.4603 ± 0 | 17.11 ± 7.961 | 125.9 ± 0.104 | 125.9 | — | — | — |
| -18.8 | 34.41 | 15.6 | 13.46 | -0.7573 | 0.4658 ± 0 | 25.19 ± 6.635 | 100.7 ± 0.1336 | 100.7 | — | — | — |
| 6.967 | 27.71 | 34.67 | 11.22 | 20.74 | 0.4709 ± 0 | 31.34 ± 5.448 | 75.44 ± 0.1513 | 75.46 | — | — | — |
| 1.59 | 25.21 | 26.8 | 10.42 | 31.04 | 0.4771 ± 0 | 25.98 ± 5.2 | 50.18 ± 0.08576 | 50.23 | — | — | — |
| -0.5519 | 36.11 | 35.56 | 10.66 | -112.4 | 0.4824 ± 0 | 35.78 ± 5.323 | 24.98 ± 0.09559 | 25 | — | — | — |
| 3.074 | 30.73 | 33.8 | 3.815 | -76.66 | 0.4831 ± 0 | 32.26 ± 1.85 | 24.97 ± 0.02635 | 25 | 1.589 | 1.667 | 1.342 |
| -0.5853 | 29.46 | 28.87 | 12.66 | -32.36 | 0.4809 ± 0 | 28.94 ± 6.919 | 35.16 ± 0.0991 | 35 | — | — | — |
| 0.1647 | 36.54 | 36.7 | 10.57 | 9.172 | 0.4786 ± 0 | 36.53 ± 5.28 | 44.88 ± 0.08437 | 45 | — | — | — |
| -26.99 | 46.22 | 19.23 | 12.59 | -70.38 | 0.4767 ± 0 | 32.71 ± 7.928 | 55.14 ± 0.08761 | 55 | — | — | — |
| 12.97 | 25.36 | 38.32 | 10.85 | -52.55 | 0.4741 ± 0 | 31.48 ± 5.431 | 64.97 ± 0.09815 | 65 | — | — | — |
| -0.172 | 34.64 | 34.47 | 12.5 | -42.36 | 0.4721 ± 0 | 34.45 ± 5.55 | 75.02 ± 0.09263 | 75 | — | — | — |
| -4.904 | 32.08 | 27.17 | 12.73 | -57.47 | 0.4704 ± 0 | 30.01 ± 6.449 | 84.9 ± 0.0884 | 85 | — | — | — |
| 5.339 | 20.75 | 26.09 | 14.78 | 32.52 | 0.4683 ± 0 | 23.15 ± 5.557 | 90 ± 0.09579 | 90 | — | — | — |
| 1.934 | 24.07 | 26 | 3.706 | 5.409 | 0.4683 ± 0 | 25.03 ± 1.899 | 89.99 ± 0.04449 | 90 | 1.521 | 1.499 | 1.906 |
| 10.56 | 22.23 | 32.78 | 12.38 | -32.38 | 0.4664 ± 0 | 27.55 ± 5.79 | 99.88 ± 0.1098 | 100 | — | — | — |
| -10.61 | 30.91 | 20.3 | 11.55 | -61.49 | 0.4638 ± 0 | 25.83 ± 5.774 | 109.8 ± 0.1006 | 110 | — | — | — |
| 4.223 | 24.93 | 29.15 | 11.28 | -29.28 | 0.4619 ± 0 | 27.4 ± 5.434 | 120.1 ± 0.1037 | 120 | — | — | — |
| -11.16 | 31.76 | 20.6 | 11.77 | -7.994 | 0.4597 ± 0 | 25.93 ± 5.885 | 130.1 ± 0.1233 | 130 | — | — | — |
| -1.866 | 25.15 | 23.29 | 3.819 | 10.33 | 0.4597 ± 0 | 24.21 ± 1.909 | 130 ± 0.03881 | 130 | 1.561 | 1.917 | 1.689 |
| 0.5416 | 12.71 | 13.25 | 11.85 | 7.758 | 0.4577 ± 0 | 12.93 ± 5.915 | 140 ± 0.1145 | 140 | — | — | — |
| -14.72 | 24.67 | 9.95 | 12.62 | 30.1 | 0.4556 ± 0 | 17.29 ± 5.939 | 150.1 ± 0.1149 | 150 | — | — | — |
| -7.77 | 24.97 | 17.2 | 12.12 | -4.911 | 0.4531 ± 0 | 21.14 ± 5.759 | 160 ± 0.114 | 160 | — | — | — |
| -8.162 | 21.85 | 13.69 | 4.72 | 7.416 | 0.4531 ± 0 | 17.76 ± 2.719 | 160 ± 0.04042 | 160 | 2.144 | 1.717 | 2.542 |

- Note: γ uses a plain LJ cutoff without tail correction (D44/D48: `pair_modify tail no`, CG 15 Å, UA/AA 14 Å), so it is cutoff-dependent and lower than a full-dispersion (LJ-PPPM or tail-corrected) value; compare it across our runs, not directly with experiment.
- Note: γ is the mechanical (pressure-tensor) value per surface, (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2] with two film surfaces; the fits are SEM-weighted linear fits in T with errors scaled by √χ²<sub>red</sub> when χ²<sub>red</sub> > 1.
- Note: The slit is a local patch of a pore wall: real separator pores are 30–100 nm and their walls semicrystalline (D50); these walls are amorphous (melt-like or post-shutdown).
- Note: Layers: surface = within 15 Å of either Gibbs surface on the film side (or outside it), interior = the rest, assigned at each time origin; sites leave their layer at long lags, so long-lag layer MSDs mix layers. MSDs are per dimension: in-plane (⟨Δx²⟩+⟨Δy²⟩)/2, normal ⟨Δz²⟩, bulk MSD/3 (isotropic).
- Note: C<sub>v</sub> = dE/dT (total energy, NVT, per gram) and the surface excess energy are classical: C<sub>v</sub> is not comparable to experiment for the same reasons as the bulk C<sub>p</sub> (classical equipartition; UA/CG drop degrees of freedom). e<sub>s</sub> = (E<sub>pore</sub> − (M<sub>pore</sub>/M<sub>bulk</sub>) E<sub>bulk</sub>(T))/(2A) compares the NVT film with the NPT bulk at 1 atm (PV ≈ 0) at the same set T; the film's lateral box follows the bulk density (D48).
- Note: bulk energies not available: /home/rdyu/projects/che126_sims/results/runs/pe_ua_amorph_n40_c240_s1/sweep/in.sweep: bulk uses a tail correction, the pore does not (D48)

</details>

### `pe_aa_crystal_5x7x12_s1`

PE AA, bulk amorphous box, — chains × C—; no manifest. Stage now: prep (not started (crystal done)).

No analysed properties yet; pending: prep not started; sweep not started; crystal analysis not run; no equilibration verdict yet. Equilibration: —.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- Manifest: not found in the systems directory.

**Equilibration**

- Verdict: —
- C<sub>n</sub> plateau (D37): —

**Stages**

- **crystal** (rdyu-server): finished; started 2026-11-23 18:39 UTC, ended 2026-11-23 23:03 UTC; reads `../../../../../worktrees/aa-crystal-test/systems/pe_aa_crystal_5x7x12_s1/data.lmp`

- Sweep analysis: not analysed yet.

</details>

### `pe_aa_amorph_n40_c240_s1_from_ua`

PE AA, bulk amorphous box, converted from the relaxed UA box (ua2aa), 40 chains × C240, 28,880 atoms; built from `pe_ua_amorph_n40_c240_s1` (`hold_ext_70ns.data`). Status: finished: prep, `sweep_crashed_20261102` (cancelled/killed?, 0.1%), sweep.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | — | `extend` progress of `pe_ua_amorph_n40_c240_s1` |
| ρ (g/cm³) | 0.85115 ± 0.00038 | 0.80722 ± 0.00024 | 0.77870 ± 0.00024 | 0.75916 ± 0.00019 | — | comp | `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.544 ± 0.046 | 0.771 ± 0.038 | 0.954 ± 0.048 | 1.104 ± 0.037 | — | comp | `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 8.694 ± 0.099 (χ²<sub>red</sub> 15.5); 25–90 °C: 8.272 ± 0.197 (χ²<sub>red</sub> 9.43); 90–160 °C: 8.720 ± 0.077 (χ²<sub>red</sub> 2.3) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 6.119 ± 0.014 (χ²<sub>red</sub> 31.5); 25–90 °C: 6.175 ± 0.035 (χ²<sub>red</sub> 26.7); 90–160 °C: 6.066 ± 0.016 (χ²<sub>red</sub> 14.6) | corr | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 8.19 (melt 6.7) | trend | `extend` progress of `pe_ua_amorph_n40_c240_s1` |
| R<sub>g</sub> (Å) | 27.70 ± 0.01 | 27.74 ± 0.05 | 27.62 ± 0.06 | 28.17 ± 0.08 | — | trend | `sweep` |
| R<sub>ee</sub> (Å) | 70.7 ± 0.1 | 69.7 ± 0.4 | 70.4 ± 0.3 | 67.3 ± 0.8 | — | trend | `sweep` |
| C<sub>n</sub> | 8.18 ± 0.01 | 8.16 ± 0.04 | 8.13 ± 0.04 | 8.36 ± 0.08 | — | trend | `sweep` |
| P2 1/e time (ps) | 161 | 19.9 | 8.86 | 5.94 | — | comp | `sweep` |
| segment MSD at 1 ns lag (Å²) | 12.48 | 59.28 | 118 | 154.1 | — | comp | `sweep` |
| max chain COM MSD (Å²) at lag | 1.436 at 2.5 ns | 11.29 at 2.5 ns | 26.6 at 2.5 ns | 40.46 at 2.5 ns | — | todo | `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.00 | 0.01 | 0.03 | 0.05 | — | todo | `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.49) | not diffusive (slope 0.78) | not diffusive (slope 0.83) | not diffusive (slope 0.85) | — | todo | `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached | not reached | not reached (extrap. 39.1) | — | todo | `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | — | todo | `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.134 | 0.095 | 0.056 | 0.048 | — | — | `sweep` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE AA, 40 chains × C240 (C240H482), 28,880 atoms/beads, force field `opls2020_aa`, box density 0.7452 g/cm³ (as built)
- Built: ua2aa (D32): carbons at UA positions; H placed geometrically
- Built from: `pe_ua_amorph_n40_c240_s1` (`hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)
- Own prep hold (5.0 ns, information): C<sub>n</sub> 8.57 vs 6.7 (outside band, info); drift (Δ -0.65 ± 0.14); R<sub>ee</sub> ACF 0.82 at 2.5 ns; COM MSD/⟨R<sub>g</sub>²⟩ 0.08

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-30 16:16 UTC, ended 2026-11-02 07:57 UTC; reads `systems/pe_aa_amorph_n40_c240_s1_from_ua/data.lmp`
  - 500 K hold 5.0 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.82 at 2.5 ns, 1/e not reached; COM MSD/⟨R<sub>g</sub>²⟩ 0.08); C<sub>n</sub> 8.57 vs 6.7 (outside band, info); drift (Δ -0.65 ± 0.14)
  - monitor flags: R<sub>ee</sub> not decorrelated (0.82 at 2.5 ns); MSD/R<sub>g</sub>² 0.08; drift seg 7,9; hyst max 0.44%
- **`sweep_crashed_20261102`** (rdyu-rog): cancelled/killed?, 0.1%; started 2026-11-02 18:52 UTC; reads `../prep/cooled.data`
- **sweep** (rdyu-rog): finished; started 2026-11-03 01:01 UTC, ended 2026-11-11 13:28 UTC; reads `../prep/cooled.data`
  - monitor flags: drift seg 4,14,19; step!=hold 90 C,130 C,160 C; hyst max 0.44%

**`sweep` analysis** (AA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-11 16:20 UTC on rdyu-rog, run started.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.85115 ± 0.00038 | 0.544 ± 0.046 | 27.70 ± 0.01 | 70.7 ± 0.1 | 8.18 ± 0.01 | 161 | 1.436 at 2.5 ns | not diffusive (slope 0.49) | yes |
| 90 | 0.80722 ± 0.00024 | 0.771 ± 0.038 | 27.74 ± 0.05 | 69.7 ± 0.4 | 8.16 ± 0.04 | 19.9 | 11.29 at 2.5 ns | not diffusive (slope 0.78) | yes |
| 130 | 0.77870 ± 0.00024 | 0.954 ± 0.048 | 27.62 ± 0.06 | 70.4 ± 0.3 | 8.13 ± 0.04 | 8.86 | 26.6 at 2.5 ns | not diffusive (slope 0.83) | yes |
| 160 | 0.75916 ± 0.00019 | 1.104 ± 0.037 | 28.17 ± 0.08 | 67.3 ± 0.8 | 8.36 ± 0.08 | 5.94 | 40.46 at 2.5 ns | not diffusive (slope 0.85) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 8.694 ± 0.099 | 15.5 | 6.119 ± 0.014 | 31.5 | 15 |
| 90–160 | 8.720 ± 0.077 | 2.3 | 6.066 ± 0.016 | 14.6 | 8 |
| 25–90 | 8.272 ± 0.197 | 9.43 | 6.175 ± 0.035 | 26.7 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term, so the stiff C–H/C–C modes that are quantum-frozen at these T make AA C<sub>p</sub> too high; it needs the VDOS quantum correction (D12c), not done here.
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.82 at 2.5 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.08, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 8.57 vs melt 6.7 ±10% (drift).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

</details>

### `ipp_ua_amorph_n40_c240_s1`

iPP UA, bulk amorphous box, 40 chains × C240, 12,760 united atoms; grown chains (seed 1). Status: finished: prep (cancelled/killed?, 60.8%), extend (stopped after D47 PASS), cool, sweep.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress |
| ρ (g/cm³) | 0.86029 ± 0.00022 | 0.83585 ± 0.00025 | 0.81456 ± 0.00045 | 0.79855 ± 0.00024 | 500 K: 0.76325 ± 0.00009; 0.83081 ± 0.00052; 0.82536 ± 0.00027; 0.81999 ± 0.00038; 0.80920 ± 0.00037; 0.80333 ± 0.00029; 0.85946 ± 0.00030; 0.85664 ± 0.00049; 0.85065 ± 0.00052; 0.84700 ± 0.00043; 0.84259 ± 0.00019; 0.83892 ± 0.00068 | comp | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.582 ± 0.025 | 0.803 ± 0.026 | 1.122 ± 0.063 | 1.190 ± 0.034 | 500 K: 1.620 ± 0.020; 0.966 ± 0.057; 0.936 ± 0.033; 1.016 ± 0.058; 1.118 ± 0.053; 1.181 ± 0.045; 0.598 ± 0.025; 0.640 ± 0.021; 0.703 ± 0.034; 0.718 ± 0.033; 0.689 ± 0.025; 0.914 ± 0.116 | comp | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 5.755 ± 0.223 (χ²<sub>red</sub> 106); 25–90 °C: 4.434 ± 0.372 (χ²<sub>red</sub> 52.9); 90–160 °C: 6.619 ± 0.103 (χ²<sub>red</sub> 3.45) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 2.511 ± 0.021 (χ²<sub>red</sub> 84); 25–90 °C: 2.409 ± 0.027 (χ²<sub>red</sub> 32.4); 90–160 °C: 2.657 ± 0.019 (χ²<sub>red</sub> 6.44) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 5.66 (melt 6.15) | comp | `extend` progress |
| R<sub>g</sub> (Å) | 19.47 ± 0.01 | 19.80 ± 0.01 | 19.75 ± 0.04 | 19.63 ± 0.06 | 19.79 ± 0.03; 19.70 ± 0.03; 19.84 ± 0.03; 19.81 ± 0.03; 19.25 ± 0.10; 19.48 ± 0.01; 19.48 ± 0.01; 19.57 ± 0.02; 19.71 ± 0.01; 19.75 ± 0.01; 19.79 ± 0.02 | trend | `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| R<sub>g</sub> (Å), 500 K hold | — | — | — | — | 500 K: 18.51 ± 0.49 | comp | `extend` |
| R<sub>ee</sub> (Å) | 50.3 ± 0.1 | 50.8 ± 0.4 | 49.1 ± 0.2 | 49.7 ± 0.3 | 50.1 ± 0.2; 49.3 ± 0.4; 49.9 ± 0.2; 49.7 ± 0.3; 46.5 ± 0.5; 50.2 ± 0.1; 50.2 ± 0.1; 50.6 ± 0.1; 49.4 ± 0.1; 49.4 ± 0.1; 49.8 ± 0.3 | trend | `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| R<sub>ee</sub> (Å), 500 K hold | — | — | — | — | 500 K: 46.3 ± 1.7 | comp | `extend` |
| C<sub>n</sub> | 6.46 ± 0.00 | 6.64 ± 0.03 | 6.33 ± 0.03 | 6.32 ± 0.03 | 6.58 ± 0.02; 6.36 ± 0.08; 6.46 ± 0.05; 6.45 ± 0.03; 5.84 ± 0.13; 6.45 ± 0.01; 6.44 ± 0.01; 6.54 ± 0.02; 6.50 ± 0.01; 6.48 ± 0.01; 6.51 ± 0.03 | trend | `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| C<sub>n</sub>, 500 K hold | — | — | — | — | 500 K: 5.64 ± 0.45 | comp | `extend` |
| P2 1/e time (ps) | — | 1.78e+03 | 237 | 79.3 | 500 K: 17.2; 1.08e+03; 650; 387; 170; 110; 4.07e+03; 2.85e+03 | corr | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_75C`, `fine_85C`, `sweep` |
| segment MSD at 1 ns lag (Å²) | 2.8 | 10.47 | 33.83 | 69.23 | 500 K: 179.4; 13.86; 18.53; 24.56; 40.74; 54.85; 2.998; 3.275; 4.253; 5.587; 6.999; 8.857 | corr | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| max chain COM MSD (Å²) at lag | 0.5077 at 5 ns | 2.678 at 5 ns | 14.66 at 5 ns | 37.52 at 5 ns | 500 K: 705.3 at 30.01 ns; 4.602 at 5 ns; 6.978 at 5 ns; 10.74 at 5 ns; 18.44 at 5 ns; 25.32 at 5 ns; 0.4589 at 5 ns; 0.597 at 5 ns; 0.8763 at 5 ns; 1.077 at 5 ns; 1.435 at 5 ns; 1.979 at 5 ns | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.00 | 0.01 | 0.04 | 0.10 | 500 K: 2.06; 0.01; 0.02; 0.03; 0.05; 0.07; 0.00; 0.00; 0.00; 0.00; 0.00; 0.01 | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.68) | not diffusive (slope 0.48) | not diffusive (slope 0.75) | not diffusive (slope 0.56) | 500 K: not diffusive (slope 0.91); not diffusive (slope 0.80); not diffusive (slope 0.80); not diffusive (slope 1.11); not diffusive (slope 0.71); not diffusive (slope 0.74); not diffusive (slope 0.35); not diffusive (slope 0.58); not diffusive (slope 0.79); not diffusive (slope 0.51); not diffusive (slope 0.37); not diffusive (slope 0.53) | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached | not reached | not reached (extrap. 24.3) | 500 K: 14.7; not reached; not reached; not reached; not reached (extrap. 116); not reached (extrap. 46); not reached; not reached; not reached; not reached; not reached; not reached | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | 500 K: 19.9; not reached; not reached; not reached; not reached; not reached; not reached; not reached; not reached; not reached; not reached; not reached | todo | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.137 | 0.138 | 0.143 | 0.134 | 500 K: 0.138; 0.138; 0.140; 0.148; 0.143; 0.136; 0.143; 0.143; 0.140; 0.136; 0.140; 0.137 | — | `extend`, `fine_100C`, `fine_110C`, `fine_120C`, `fine_140C`, `fine_150C`, `fine_35C`, `fine_45C`, `fine_55C`, `fine_65C`, `fine_75C`, `fine_85C`, `sweep` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- iPP UA, 40 chains × C240 (C240H482), 12,760 atoms/beads, force field `trappe_ua`, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)

**Stages**

- **prep** (rdyu-rog): cancelled/killed?, 60.8%; started 2026-10-21 20:13 UTC; reads `systems/ipp_ua_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.45 at 10.0 ns, 1/e not reached; COM MSD/⟨R<sub>g</sub>²⟩ 1.05); C<sub>n</sub> 4.77 vs 6.15 (outside band, info); no drift (Δ +0.20 ± 0.38)
  - monitor flags: R<sub>ee</sub> not decorrelated (0.45 at 10.0 ns); MSD/R<sub>g</sub>² 1.05
- **extend** (rdyu-rog): stopped after D47 PASS (cancelled/killed?), 50.0%; started 2026-10-23 19:05 UTC; reads `../prep/hold.data`
  - 500 K hold 60.0 ns: D47 PASS (R<sub>ee</sub> ACF 0.19 at 30.0 ns, 1/e at 14.68 ns; COM MSD/⟨R<sub>g</sub>²⟩ 2.06); C<sub>n</sub> 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)
- **cool** (rdyu-rog): finished; started 2026-10-26 18:02 UTC, ended 2026-10-28 07:16 UTC; reads `../extend/hold_ext_40ns.data`
  - monitor flags: drift seg 4; hyst max 0.67%
- **sweep** (rdyu-rog): finished; started 2026-10-28 07:16 UTC, ended 2026-11-04 05:33 UTC; reads `../cool/cooled.data`
  - monitor flags: drift seg 1,5,8,12,13,16; step!=hold 90 C,130 C; hyst max 0.67%
- Superseded (not used): `prep_server_cancelled` (cancelled/killed?)

**`extend` analysis**

`sepsim analyze hold`, generated 2026-11-09 18:52 UTC on rdyu-server, run started; segment Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm; 60.01 ns analysed of 80 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (30.01 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`fine_100C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:32 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 100 | 0.83081 ± 0.00052 | 0.966 ± 0.057 | 19.79 ± 0.03 | 50.1 ± 0.2 | 6.58 ± 0.02 | 1.08e+03 | 4.602 at 5 ns | not diffusive (slope 0.80) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_110C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:33 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 110 | 0.82536 ± 0.00027 | 0.936 ± 0.033 | 19.70 ± 0.03 | 49.3 ± 0.4 | 6.36 ± 0.08 | 650 | 6.978 at 5 ns | not diffusive (slope 0.80) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_120C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:33 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 120 | 0.81999 ± 0.00038 | 1.016 ± 0.058 | 19.84 ± 0.03 | 49.9 ± 0.2 | 6.46 ± 0.05 | 387 | 10.74 at 5 ns | not diffusive (slope 1.11) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_140C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:33 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 140 | 0.80920 ± 0.00037 | 1.118 ± 0.053 | 19.81 ± 0.03 | 49.7 ± 0.3 | 6.45 ± 0.03 | 170 | 18.44 at 5 ns | not diffusive (slope 0.71) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_150C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:33 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 150 | 0.80333 ± 0.00029 | 1.181 ± 0.045 | 19.25 ± 0.10 | 46.5 ± 0.5 | 5.84 ± 0.13 | 110 | 25.32 at 5 ns | not diffusive (slope 0.74) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_35C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:31 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 35 | 0.85946 ± 0.00030 | 0.598 ± 0.025 | 19.48 ± 0.01 | 50.2 ± 0.1 | 6.45 ± 0.01 | — | 0.4589 at 5 ns | not diffusive (slope 0.35) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_45C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:32 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 45 | 0.85664 ± 0.00049 | 0.640 ± 0.021 | 19.48 ± 0.01 | 50.2 ± 0.1 | 6.44 ± 0.01 | — | 0.597 at 5 ns | not diffusive (slope 0.58) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_55C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:32 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 55 | 0.85065 ± 0.00052 | 0.703 ± 0.034 | 19.57 ± 0.02 | 50.6 ± 0.1 | 6.54 ± 0.02 | — | 0.8763 at 5 ns | not diffusive (slope 0.79) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_65C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:32 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 65 | 0.84700 ± 0.00043 | 0.718 ± 0.033 | 19.71 ± 0.01 | 49.4 ± 0.1 | 6.50 ± 0.01 | — | 1.077 at 5 ns | not diffusive (slope 0.51) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_75C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:32 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 75 | 0.84259 ± 0.00019 | 0.689 ± 0.025 | 19.75 ± 0.01 | 49.4 ± 0.1 | 6.48 ± 0.01 | 4.07e+03 | 1.435 at 5 ns | not diffusive (slope 0.37) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`fine_85C` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-23 03:32 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 85 | 0.83892 ± 0.00068 | 0.914 ± 0.116 | 19.79 ± 0.02 | 49.8 ± 0.3 | 6.51 ± 0.03 | 2.85e+03 | 1.979 at 5 ns | not diffusive (slope 0.53) | yes |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

**`sweep` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-07 03:47 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.86029 ± 0.00022 | 0.582 ± 0.025 | 19.47 ± 0.01 | 50.3 ± 0.1 | 6.46 ± 0.00 | — | 0.5077 at 5 ns | not diffusive (slope 0.68) | yes |
| 90 | 0.83585 ± 0.00025 | 0.803 ± 0.026 | 19.80 ± 0.01 | 50.8 ± 0.4 | 6.64 ± 0.03 | 1.78e+03 | 2.678 at 5 ns | not diffusive (slope 0.48) | yes |
| 130 | 0.81456 ± 0.00045 | 1.122 ± 0.063 | 19.75 ± 0.04 | 49.1 ± 0.2 | 6.33 ± 0.03 | 237 | 14.66 at 5 ns | not diffusive (slope 0.75) | yes |
| 160 | 0.79855 ± 0.00024 | 1.190 ± 0.034 | 19.63 ± 0.06 | 49.7 ± 0.3 | 6.32 ± 0.03 | 79.3 | 37.52 at 5 ns | not diffusive (slope 0.56) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 5.755 ± 0.223 | 106 | 2.511 ± 0.021 | 84 | 15 |
| 90–160 | 6.619 ± 0.103 | 3.45 | 2.657 ± 0.019 | 6.44 | 8 |
| 25–90 | 4.434 ± 0.372 | 52.9 | 2.409 ± 0.027 | 32.4 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; UA also drops degrees of freedom (the hydrogens), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.45 at 10.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 1.05, needs >= 2).
- Note: D37 chain check FAIL on the prep 500 K hold: C<sub>n</sub> plateau 4.77 vs melt 6.15 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

</details>

### `ipp_ua_pore500k_w10nm_n40_c240_s1`

iPP UA, wide 10 nm slit pore made at 500 K, 40 chains × C240, 12,760 united atoms; built from `ipp_ua_amorph_n40_c240_s1` (`extend/hold_ext_40ns.data`). Status: finished: `pore_relax`.

No analysed properties yet. Equilibration: from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- iPP UA, 40 chains × C240 (C240H482), 12,760 atoms/beads, force field `trappe_ua`, box density 0.3032 g/cm³ (as built)
- Pore: wide pore, nominal 10 nm, wall 6.66 nm, clear gap 5.90 nm, area 44.3 nm²
- Built from: `ipp_ua_amorph_n40_c240_s1` (`extend/hold_ext_40ns.data`)

**Equilibration**

- Verdict: from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)

**Stages**

- **`pore_relax`** (rdyu-rog): finished; started 2026-11-04 05:54 UTC, ended 2026-11-04 10:02 UTC; reads `systems/ipp_ua_pore500k_w10nm_n40_c240_s1/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| wide | 10 nm (at 500 K) | — | 6.7 nm (500 K) | 6.7 × 6.7 nm (500 K) | — | finished: `pore_relax` | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `ipp_ua_pore_w5nm_n40_c240_s1`

iPP UA, 5 nm dry slit pore, 40 chains × C240, 12,760 united atoms; built from `ipp_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`). Status: finished: pore.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `ipp_ua_pore500k_w10nm_n40_c240_s1` ← `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress of `ipp_ua_amorph_n40_c240_s1` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 5.66 (melt 6.15) | n/a | `extend` progress of `ipp_ua_amorph_n40_c240_s1` |
| R<sub>g</sub> (Å) | 19.47 ± 0.04 | 19.78 ± 0.05 | 19.53 ± 0.25 | 19.32 ± 0.09 | — | trend | `pore` |
| R<sub>ee</sub> (Å) | 48.2 ± 0.2 | 49.7 ± 0.5 | 48.9 ± 0.8 | 47.6 ± 0.9 | — | trend | `pore` |
| C<sub>n</sub> | 6.03 ± 0.04 | 6.28 ± 0.09 | 6.08 ± 0.25 | 5.92 ± 0.15 | — | trend | `pore` |
| P2 1/e time (ps) | — | 508 | 84 | 35.1 | — | corr | `pore` |
| P2 1/e time, surface layer (ps) | — | 241 | 49.9 | 24.2 | — | corr | `pore` |
| P2 1/e time, interior layer (ps) | — | 954 | 128 | 47.1 | — | corr | `pore` |
| segment MSD at 1 ns lag (Å²) | 5.419 | 31.84 | 95.15 | 155 | — | corr | `pore` |
| max chain COM MSD (Å²) at lag | 0.9156 at 5 ns | 13.38 at 5 ns | 64.77 at 5 ns | 153.2 at 5 ns | — | n/a | `pore` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.00 | 0.03 | 0.17 | 0.41 | — | n/a | `pore` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.38) | not diffusive (slope 0.80) | not diffusive (slope 1.11) | not diffusive (slope 1.16) | — | n/a | `pore` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached | not reached (extrap. 23.8) | not reached (extrap. 15.1) | — | n/a | `pore` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached (extrap. 36) | not reached (extrap. 25.3) | — | n/a | `pore` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.153 | 0.157 | 0.164 | 0.159 | — | — | `pore` |
| γ, run monitor (mN/m) | 20.1 ± 3.2 | 22.3 ± 3.5 | 27.3 ± 2.8 | 17.2 ± 3.8 | — | comp | `pore` progress |
| γ, analysis (mN/m) | 20.6 ± 2.1 | 25.2 ± 2.8 | 25.3 ± 2.1 | 16.4 ± 2.6 | — | comp | `pore` |
| dγ/dT (mN m⁻¹ K⁻¹) | — | — | — | — | cooling branch 25–201.6 °C: -0.0821 ± 0.0456 (χ²<sub>red</sub> 0.448); heating sweep 25–160 °C: 0.0001 ± 0.0300 (χ²<sub>red</sub> 2.1) | comp | `pore` |
| γ at 25 °C from the dγ/dT fit (mN/m) | — | — | — | — | cooling branch: 33.43; heating sweep: 23.01 | comp | `pore` |
| film thickness between the Gibbs surfaces (Å) | 64.52 ± 0.06 | 65.81 ± 0.06 | 66.94 ± 0.04 | 67.63 ± 0.04 | — | trend | `pore` |
| gap between the Gibbs surfaces (Å) | 49.05 | 47.76 | 46.64 | 45.95 | — | trend | `pore` |
| film interior density (g/cm³) | 0.8480 ± 0.0008 | 0.8152 ± 0.0007 | 0.7883 ± 0.0005 | 0.7695 ± 0.0004 | — | trend | `pore` |
| interfacial width, 10–90 % (Å) | 6.69 | 7.07 | 8.46 | 8.44 | — | trend | `pore` |
| closest approach across the gap (Å) | 40.2 | 37.5 | 35.0 | 34.0 | — | trend | `pore` |
| film α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 7.389; 25–90 °C: 6.127; 90–160 °C: 8.338 | — | `pore` |
| α<sub>z</sub>, film-thickness expansion (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 3.489 ± 0.091 (χ²<sub>red</sub> 2.16); 25–90 °C: 3.082 ± 0.287 (χ²<sub>red</sub> 2.7); 90–160 °C: 3.846 ± 0.142 (χ²<sub>red</sub> 0.896) | — | `pore` |
| C<sub>v</sub> of the film, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 2.616 ± 0.017 (χ²<sub>red</sub> 68.9); 25–90 °C: 2.516 ± 0.025 (χ²<sub>red</sub> 20.7); 90–160 °C: 2.734 ± 0.015 (χ²<sub>red</sub> 6.8) | — | `pore` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- iPP UA, 40 chains × C240 (C240H482), 12,760 atoms/beads, force field `trappe_ua`, box density 0.4447 g/cm³ (as built)
- Pore: narrow pore, nominal 5 nm, 4.74 nm at 500 K, wall 6.36 nm, clear gap 2.62 nm, area 44.3 nm²
- Built from: `ipp_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`) ← `ipp_ua_amorph_n40_c240_s1` (`extend/hold_ext_40ns.data`)

**Equilibration**

- Verdict: from `ipp_ua_pore500k_w10nm_n40_c240_s1` ← `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)

**Stages**

- **pore** (rdyu-rog): finished; started 2026-11-04 10:09 UTC, ended 2026-11-08 15:24 UTC; reads `systems/ipp_ua_pore_w5nm_n40_c240_s1/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 20.1 ± 3.2; 90 °C 22.3 ± 3.5; 130 °C 27.3 ± 2.8; 160 °C 17.2 ± 3.8

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.74 nm | 6.4 nm | 6.4 × 6.4 nm (25 °C) | 25 °C 20.1 ± 3.2; 90 °C 22.3 ± 3.5; 130 °C 27.3 ± 2.8; 160 °C 17.2 ± 3.8 | finished: pore | pore |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

**`pore` analysis**

Pore analysis (`sepsim analyze pore`, generated 2026-11-08 15:25 UTC on rdyu-rog):

- dγ/dT, cooling-branch fit (mN m⁻¹ K⁻¹): -0.08207
- γ at 25 °C, cooling-branch fit (mN/m): 33.43
- dγ/dT, heating-sweep fit (mN m⁻¹ K⁻¹): 0.0001078
- γ at 25 °C, heating-sweep fit (mN/m): 23.01
- analysis node: rdyu-rog
- nominal gap width (nm): 5
- wall (film) thickness (Å): 63.57

Convergence of the film quantities, per segment:

| γ (mN/m) | segment end (ps) | gap between the Gibbs surfaces (Å) | film interior density (g/cm³) |
|---|---|---|---|
| 4.071 ± 15.26 | 1000 | — | — |
| 14.22 ± 6.636 | 3000 | — | — |
| 26.9 ± 6.55 | 5000 | — | — |
| 20.66 ± 6.556 | 7000 | — | — |
| 33.63 ± 9.637 | 9000 | — | — |
| 27.3 ± 6.532 | 1.1e+04 | — | — |
| 25.05 ± 7.863 | 1.3e+04 | — | — |
| 26.29 ± 14.01 | 1.5e+04 | — | — |
| 34.89 ± 7.273 | 1.7e+04 | — | — |
| 20.58 ± 2.127 | 2.7e+04 | 49.05 ± 0.07066 | 0.848 ± 0.000927 |
| 7.968 ± 6.816 | 2.9e+04 | 48.69 ± 0.07318 | 0.8423 ± 0.0009522 |
| 30.2 ± 7.409 | 3.1e+04 | 48.61 ± 0.08966 | 0.8386 ± 0.001161 |
| 31.73 ± 5.691 | 3.3e+04 | 48.42 ± 0.1198 | 0.8347 ± 0.001523 |
| 20.26 ± 10.08 | 3.5e+04 | 48.55 ± 0.1377 | 0.8322 ± 0.001769 |
| 27.05 ± 5.861 | 3.7e+04 | 47.86 ± 0.1145 | 0.8213 ± 0.001431 |
| 20.56 ± 6.855 | 3.9e+04 | 47.61 ± 0.09388 | 0.8159 ± 0.001162 |
| 33.76 ± 5.69 | 4.1e+04 | 47.68 ± 0.1356 | 0.8142 ± 0.001669 |
| 25.16 ± 2.752 | 5.1e+04 | 47.76 ± 0.07297 | 0.8152 ± 0.000883 |
| 26.65 ± 5.967 | 5.3e+04 | 47.5 ± 0.1285 | 0.8094 ± 0.001574 |
| 41.21 ± 6.253 | 5.5e+04 | 47.18 ± 0.1817 | 0.8012 ± 0.002188 |
| 24.49 ± 6.298 | 5.7e+04 | 46.91 ± 0.1351 | 0.794 ± 0.001615 |
| 21.9 ± 6.115 | 5.9e+04 | 46.65 ± 0.1247 | 0.7885 ± 0.001467 |
| 25.26 ± 2.087 | 6.9e+04 | 46.63 ± 0.0387 | 0.7883 ± 0.0004541 |
| 23.05 ± 6.526 | 7.1e+04 | 46.64 ± 0.1576 | 0.7837 ± 0.001851 |
| 23.03 ± 6.323 | 7.3e+04 | 46.04 ± 0.2002 | 0.7733 ± 0.002289 |
| 14.21 ± 6.313 | 7.5e+04 | 46.01 ± 0.1245 | 0.7703 ± 0.001428 |
| 16.35 ± 2.609 | 8.5e+04 | 45.94 ± 0.0384 | 0.7695 ± 0.0004363 |

Per hold: film vs bulk:

| bulk: max chain COM MSD (Å²) | bulk ρ (g/cm³) | bulk: max segment MSD (Å²) | film: C<sub>n</sub> | film: max lag (ps) | film: max chain COM MSD (Å²) | film: chain COM MSD / ⟨R<sub>g</sub>²⟩ at max lag | film: COM MSD log-slope at max lag | film: largest COM MSD log-slope | film: largest ordered cluster, mean (sites) | film: hold length (ns) | `film.segment_msd.lag_max_ps` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5077 | 0.8603 ± 0.0002246 | 5.316 | 6.035 ± 0.03643 | 5000 | 0.9156 | 0.002415 | 0.381 | 1.886 | 173.2 | 10 | 5000 |
| 2.678 | 0.8359 ± 0.0002528 | 26.4 | 6.281 ± 0.08707 | 5000 | 13.38 | 0.03419 | 0.8013 | 1.898 | 157.7 | 10 | 5000 |
| 14.66 | 0.8146 ± 0.0004459 | 98.56 | 6.084 ± 0.2473 | 5000 | 64.77 | 0.1699 | 1.115 | 1.908 | 186.5 | 10 | 5000 |
| 37.52 | 0.7986 ± 0.0002361 | 203.6 | 5.918 ± 0.1503 | 5000 | 153.2 | 0.4104 | 1.162 | 1.915 | 117.7 | 10 | 5000 |

Per segment:

| γ drift: second − first half (mN/m) | γ, first half (mN/m) | γ, second half (mN/m) | SEM of the γ drift (mN/m) | potential-energy drift: second − first half | box density (g/cm³) | γ (mN/m) | T (°C) | set T (°C) | SEM of γ from 16 blocks (mN/m) | SEM of γ from 32 blocks (mN/m) | SEM of γ from 8 blocks (mN/m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| -52.83 | 30.65 | -22.18 | 17.73 | -41.96 | 0.4447 ± 0 | 4.071 ± 15.26 | 226.9 ± 0.202 | 226.9 | — | — | — |
| -8.413 | 18.27 | 9.859 | 14.29 | 9.516 | 0.4497 ± 0 | 14.22 ± 6.636 | 201.5 ± 0.132 | 201.6 | — | — | — |
| -0.949 | 27.09 | 26.14 | 13.79 | 10.7 | 0.4549 ± 0 | 26.9 ± 6.55 | 176.3 ± 0.1473 | 176.4 | — | — | — |
| -1.04 | 21.17 | 20.13 | 15.91 | -1.162 | 0.4602 ± 0 | 20.66 ± 6.556 | 151.1 ± 0.1049 | 151.2 | — | — | — |
| -30.11 | 48.59 | 18.48 | 14.45 | 78.95 | 0.4651 ± 0 | 33.63 ± 9.637 | 126.1 ± 0.1007 | 125.9 | — | — | — |
| -5.457 | 29.9 | 24.44 | 13.46 | -40.77 | 0.4692 ± 0 | 27.3 ± 6.532 | 100.6 ± 0.1009 | 100.7 | — | — | — |
| 26.31 | 11.89 | 38.2 | 14.53 | -91.52 | 0.473 ± 0 | 25.05 ± 7.863 | 75.62 ± 0.1057 | 75.46 | — | — | — |
| 34.95 | 8.475 | 43.43 | 15.52 | 23.92 | 0.4779 ± 0 | 26.29 ± 14.01 | 50.15 ± 0.09133 | 50.23 | — | — | — |
| 2.894 | 33.32 | 36.21 | 11.7 | -38.32 | 0.4814 ± 0 | 34.89 ± 7.273 | 25.01 ± 0.07178 | 25 | — | — | — |
| -1.431 | 21.3 | 19.87 | 4.69 | -23.39 | 0.4817 ± 0 | 20.58 ± 2.127 | 25.05 ± 0.02698 | 25 | 1.899 | 1.89 | 1.574 |
| 9.381 | 2.914 | 12.29 | 12.95 | 40.53 | 0.4812 ± 0 | 7.968 ± 6.816 | 35.09 ± 0.07758 | 35 | — | — | — |
| -9.269 | 35.07 | 25.8 | 15.5 | 38.64 | 0.4797 ± 0 | 30.2 ± 7.409 | 44.88 ± 0.08259 | 45 | — | — | — |
| 2.703 | 30.44 | 33.15 | 13.23 | -37.83 | 0.4788 ± 0 | 31.73 ± 5.691 | 55.09 ± 0.07883 | 55 | — | — | — |
| 27.7 | 6.488 | 34.19 | 12.73 | 44.42 | 0.4765 ± 0 | 20.26 ± 10.08 | 64.87 ± 0.07947 | 65 | — | — | — |
| 7.168 | 23.55 | 30.72 | 17.54 | -15.8 | 0.4752 ± 0 | 27.05 ± 5.861 | 74.99 ± 0.08085 | 75 | — | — | — |
| -2.687 | 21.66 | 18.97 | 13.2 | -17.19 | 0.4739 ± 0 | 20.56 ± 6.855 | 85 ± 0.08576 | 85 | — | — | — |
| 12.59 | 27.47 | 40.05 | 12.24 | -1.275 | 0.4724 ± 0 | 33.76 ± 5.69 | 90.05 ± 0.08448 | 90 | — | — | — |
| -8.08 | 29.2 | 21.12 | 4.677 | -54.99 | 0.4724 ± 0 | 25.16 ± 2.752 | 90.03 ± 0.02895 | 90 | 2.622 | 2.347 | 2.661 |
| 16.13 | 18.79 | 34.92 | 12.02 | 23.9 | 0.4708 ± 0 | 26.65 ± 5.967 | 100.1 ± 0.08792 | 100 | — | — | — |
| -9.225 | 45.74 | 36.52 | 12.52 | -31.35 | 0.4684 ± 0 | 41.21 ± 6.253 | 110.1 ± 0.09459 | 110 | — | — | — |
| -0.4101 | 24.62 | 24.21 | 15.07 | -12.81 | 0.466 ± 0 | 24.49 ± 6.298 | 120.2 ± 0.09214 | 120 | — | — | — |
| -18.39 | 31.26 | 12.86 | 12.79 | -80.56 | 0.4646 ± 0 | 21.9 ± 6.115 | 130 ± 0.09649 | 130 | — | — | — |
| 5.545 | 22.52 | 28.06 | 4.156 | 22.3 | 0.4646 ± 0 | 25.26 ± 2.087 | 130 ± 0.03547 | 130 | 1.186 | 1.33 | 1.475 |
| -1.277 | 23.81 | 22.53 | 18.12 | 64.43 | 0.4618 ± 0 | 23.05 ± 6.526 | 140.3 ± 0.1826 | 140 | — | — | — |
| 1.938 | 21.95 | 23.89 | 15.26 | 20.29 | 0.4598 ± 0 | 23.03 ± 6.323 | 150.1 ± 0.104 | 150 | — | — | — |
| -14.61 | 21.58 | 6.969 | 12.79 | 8.868 | 0.4582 ± 0 | 14.21 ± 6.313 | 160.1 ± 0.1077 | 160 | — | — | — |
| 4.463 | 14.08 | 18.54 | 4.851 | -11.81 | 0.4582 ± 0 | 16.35 ± 2.609 | 160 ± 0.0388 | 160 | 2.096 | 2.199 | 2.401 |

- Note: γ uses a plain LJ cutoff without tail correction (D44/D48: `pair_modify tail no`, CG 15 Å, UA/AA 14 Å), so it is cutoff-dependent and lower than a full-dispersion (LJ-PPPM or tail-corrected) value; compare it across our runs, not directly with experiment.
- Note: γ is the mechanical (pressure-tensor) value per surface, (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2] with two film surfaces; the fits are SEM-weighted linear fits in T with errors scaled by √χ²<sub>red</sub> when χ²<sub>red</sub> > 1.
- Note: The slit is a local patch of a pore wall: real separator pores are 30–100 nm and their walls semicrystalline (D50); these walls are amorphous (melt-like or post-shutdown).
- Note: Layers: surface = within 15 Å of either Gibbs surface on the film side (or outside it), interior = the rest, assigned at each time origin; sites leave their layer at long lags, so long-lag layer MSDs mix layers. MSDs are per dimension: in-plane (⟨Δx²⟩+⟨Δy²⟩)/2, normal ⟨Δz²⟩, bulk MSD/3 (isotropic).
- Note: C<sub>v</sub> = dE/dT (total energy, NVT, per gram) and the surface excess energy are classical: C<sub>v</sub> is not comparable to experiment for the same reasons as the bulk C<sub>p</sub> (classical equipartition; UA/CG drop degrees of freedom). e<sub>s</sub> = (E<sub>pore</sub> − (M<sub>pore</sub>/M<sub>bulk</sub>) E<sub>bulk</sub>(T))/(2A) compares the NVT film with the NPT bulk at 1 atm (PV ≈ 0) at the same set T; the film's lateral box follows the bulk density (D48).
- Note: bulk energies not available: /home/rdyu/projects/che126_sims/results/runs/ipp_ua_amorph_n40_c240_s1/sweep/in.sweep: bulk uses a tail correction, the pore does not (D48)

</details>

### `ipp_aa_amorph_n40_c240_s1_from_ua`

iPP AA, bulk amorphous box, converted from the relaxed UA box (ua2aa), 40 chains × C240, 28,880 atoms; built from `ipp_ua_amorph_n40_c240_s1` (`hold_ext_40ns.data`). Status: finished: prep, `sweep_failed_20261102` (failed, 0.0%), sweep.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress of `ipp_ua_amorph_n40_c240_s1` |
| ρ (g/cm³) | 0.86809 ± 0.00022 | 0.82739 ± 0.00055 | 0.80231 ± 0.00023 | 0.78281 ± 0.00036 | — | comp | `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.468 ± 0.017 | 0.927 ± 0.081 | 0.967 ± 0.043 | 1.157 ± 0.063 | — | comp | `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 7.637 ± 0.110 (χ²<sub>red</sub> 17.2); 25–90 °C: 7.190 ± 0.268 (χ²<sub>red</sub> 13.8); 90–160 °C: 7.830 ± 0.235 (χ²<sub>red</sub> 6.45) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 5.927 ± 0.016 (χ²<sub>red</sub> 40.9); 25–90 °C: 5.968 ± 0.038 (χ²<sub>red</sub> 36.3); 90–160 °C: 5.886 ± 0.034 (χ²<sub>red</sub> 37.9) | corr | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 5.66 (melt 6.15) | trend | `extend` progress of `ipp_ua_amorph_n40_c240_s1` |
| R<sub>g</sub> (Å) | 17.71 ± 0.01 | 18.19 ± 0.06 | 17.91 ± 0.08 | 17.41 ± 0.04 | — | trend | `sweep` |
| R<sub>ee</sub> (Å) | 45.9 ± 0.1 | 48.2 ± 0.3 | 47.5 ± 0.6 | 43.2 ± 0.2 | — | trend | `sweep` |
| C<sub>n</sub> | 5.47 ± 0.01 | 5.88 ± 0.04 | 5.59 ± 0.09 | 4.94 ± 0.02 | — | trend | `sweep` |
| P2 1/e time (ps) | — | 238 | 69.4 | 35.8 | — | comp | `sweep` |
| segment MSD at 1 ns lag (Å²) | 3.379 | 26.68 | 63.87 | 93.85 | — | comp | `sweep` |
| max chain COM MSD (Å²) at lag | 0.4307 at 2.5 ns | 4.91 at 2.5 ns | 19.55 at 2.5 ns | 33.02 at 2.5 ns | — | todo | `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.00 | 0.01 | 0.06 | 0.11 | — | todo | `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.46) | not diffusive (slope 0.85) | not diffusive (slope 0.58) | not diffusive (slope 0.68) | — | todo | `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached | not reached | not reached (extrap. 18.4) | — | todo | `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | — | todo | `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.085 | 0.091 | 0.100 | 0.109 | — | — | `sweep` |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- iPP AA, 40 chains × C240 (C240H482), 28,880 atoms/beads, force field `opls2020_aa`, box density 0.7588 g/cm³ (as built)
- Built: ua2aa (D32): carbons at UA positions; H placed geometrically
- Built from: `ipp_ua_amorph_n40_c240_s1` (`hold_ext_40ns.data`)

**Equilibration**

- Verdict: from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)
- Own prep hold (5.0 ns, information): C<sub>n</sub> 5.58 vs 6.15 (in band, info); no drift (Δ -0.01 ± 0.16); R<sub>ee</sub> ACF 0.72 at 2.5 ns; COM MSD/⟨R<sub>g</sub>²⟩ 0.25

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-26 18:04 UTC, ended 2026-10-29 11:25 UTC; reads `systems/ipp_aa_amorph_n40_c240_s1_from_ua/data.lmp`
  - 500 K hold 5.0 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.72 at 2.5 ns, 1/e not reached; COM MSD/⟨R<sub>g</sub>²⟩ 0.25); C<sub>n</sub> 5.58 vs 6.15 (in band, info); no drift (Δ -0.01 ± 0.16)
  - monitor flags: R<sub>ee</sub> not decorrelated (0.72 at 2.5 ns); MSD/R<sub>g</sub>² 0.25; drift seg 9,12; hyst max 0.33%
- **`sweep_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 14:06 UTC, ended 2026-11-02 14:06 UTC; reads `../prep/cooled.data`
- **sweep** (rdyu-rog): finished; started 2026-11-13 04:34 UTC, ended 2026-11-20 06:02 UTC; reads `../prep/cooled.data`
  - monitor flags: drift seg 3,6,8; step!=hold 90 C,130 C,160 C; hyst max 0.33%
- Superseded (not used): `sweep_cancelled_pe_first` (cancelled/killed?)

**`sweep` analysis** (AA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-21 06:53 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.86809 ± 0.00022 | 0.468 ± 0.017 | 17.71 ± 0.01 | 45.9 ± 0.1 | 5.47 ± 0.01 | — | 0.4307 at 2.5 ns | not diffusive (slope 0.46) | yes |
| 90 | 0.82739 ± 0.00055 | 0.927 ± 0.081 | 18.19 ± 0.06 | 48.2 ± 0.3 | 5.88 ± 0.04 | 238 | 4.91 at 2.5 ns | not diffusive (slope 0.85) | yes |
| 130 | 0.80231 ± 0.00023 | 0.967 ± 0.043 | 17.91 ± 0.08 | 47.5 ± 0.6 | 5.59 ± 0.09 | 69.4 | 19.55 at 2.5 ns | not diffusive (slope 0.58) | yes |
| 160 | 0.78281 ± 0.00036 | 1.157 ± 0.063 | 17.41 ± 0.04 | 43.2 ± 0.2 | 4.94 ± 0.02 | 35.8 | 33.02 at 2.5 ns | not diffusive (slope 0.68) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 7.637 ± 0.110 | 17.2 | 5.927 ± 0.016 | 40.9 | 15 |
| 90–160 | 7.830 ± 0.235 | 6.45 | 5.886 ± 0.034 | 37.9 | 8 |
| 25–90 | 7.190 ± 0.268 | 13.8 | 5.968 ± 0.038 | 36.3 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term, so the stiff C–H/C–C modes that are quantum-frozen at these T make AA C<sub>p</sub> too high; it needs the VDOS quantum correction (D12c), not done here.
- Note: Chains may not be relaxed: the D47 criteria fail on the prep 500 K hold (prep/progress.json: end-to-end ACF 0.72 at 2.5 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.25, needs >= 2).
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).

</details>

### `pe_cg_pore_w10nm_n40_c240_s1` (superseded)

PE CG, 10 nm dry slit pore, 40 chains × C240, 3,200 beads; built from `pe_cg_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`). **Superseded** as built from an earlier `pe_cg_pore500k_w10nm_n40_c240_s1` (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`); not used. Stage now: pore (cancelled/killed?, 5.6%).

No analysed properties yet. Equilibration: from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field `sdk_cg`, box density 0.2964 g/cm³ (as built)
- Pore: narrow pore, nominal 10 nm, 9.69 nm at 500 K, wall 6.41 nm, clear gap 8.59 nm, area 46.0 nm²
- Built from: `pe_cg_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n40_c240_s1` (`prep/hold.data`)
- **Stale source:** built from an earlier `pe_cg_pore500k_w10nm_n40_c240_s1` (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)

**Equilibration**

- Verdict: from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **pore** (rdyu-rog): cancelled/killed?, 5.6%; started 2026-10-26 16:59 UTC; reads `systems/pe_cg_pore_w10nm_n40_c240_s1/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 10 nm (at 25 °C) | 9.69 nm | 6.4 nm | 6.5 × 6.5 nm (25 °C) | — | pore: cancelled/killed?, 5.6% | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_pore_w3nm_n40_c240_s1` (superseded)

PE CG, 3 nm dry slit pore, 40 chains × C240, 3,200 beads; built from `pe_cg_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`). **Superseded** as built from an earlier `pe_cg_pore500k_w10nm_n40_c240_s1` (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`); not used. Stage now: pore (cancelled/killed?, 7.1%).

No analysed properties yet. Equilibration: from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted.

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field `sdk_cg`, box density 0.5168 g/cm³ (as built)
- Pore: narrow pore, nominal 3 nm, 2.69 nm at 500 K, wall 6.41 nm, clear gap 1.59 nm, area 46.0 nm²
- Built from: `pe_cg_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n40_c240_s1` (`prep/hold.data`)
- **Stale source:** built from an earlier `pe_cg_pore500k_w10nm_n40_c240_s1` (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)

**Equilibration**

- Verdict: from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **pore** (rdyu-server): cancelled/killed?, 7.1%; started 2026-10-26 16:36 UTC; reads `systems/pe_cg_pore_w3nm_n40_c240_s1/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 3 nm (at 25 °C) | 2.69 nm | 6.4 nm | 6.5 × 6.5 nm (25 °C) | — | pore: cancelled/killed?, 7.1% | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_aa_amorph_n40_c240_s1` (superseded)

PE AA, bulk amorphous box, 40 chains × C240, 28,880 atoms; grown chains (seed 1). **Superseded** by `pe_aa_amorph_n40_c240_s1_from_ua` (D47: AA is built from the relaxed UA box); not used. Stage now: sweep (not started (prep done)).

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 FAIL (prep hold only); ACF 0.72 at 2.5 ns, MSD/⟨R<sub>g</sub>²⟩ 0.16; 5.0 ns at 500 K; not accepted | — | `prep` progress |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 6.09 (melt 6.7) | trend! | `prep` progress |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE AA, 40 chains × C240 (C240H482), 28,880 atoms/beads, force field `opls2020_aa`, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)
- **Superseded** by `pe_aa_amorph_n40_c240_s1_from_ua` (D47: AA is built from the relaxed UA box)

**Equilibration**

- Verdict: D47 FAIL (prep hold only); ACF 0.72 at 2.5 ns, MSD/⟨R<sub>g</sub>²⟩ 0.16; 5.0 ns at 500 K; not accepted
- C<sub>n</sub> plateau (D37): 6.09 vs 6.7 (in band, info); drift (Δ +1.01 ± 0.22)

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-21 19:36 UTC, ended 2026-10-24 08:09 UTC; reads `systems/pe_aa_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 5.0 ns: D47 criteria on this hold FAIL (R<sub>ee</sub> ACF 0.72 at 2.5 ns, 1/e not reached; COM MSD/⟨R<sub>g</sub>²⟩ 0.16); C<sub>n</sub> 6.09 vs 6.7 (in band, info); drift (Δ +1.01 ± 0.22)
  - monitor flags: R<sub>ee</sub> not decorrelated (0.72 at 2.5 ns); MSD/R<sub>g</sub>² 0.16

</details>


## Property guide: what each calculated quantity means

Reference values are approximate textbook values for amorphous or molten PE, to give a sense of scale. They have not been checked against a specific source. All boxes stay amorphous at every temperature. Real separator PE is semicrystalline below about 130 °C, so 25–130 °C here describes the amorphous phase only. CG and UA times are model times: CG dynamics in particular run several times faster than real PE, so only their trends with temperature are meaningful.

### Comparability with experiment

A fair comparison needs amorphous or melt data at the same temperature and a similar chain length (our chains are C240, about 3.4 kg/mol, and C1500, about 21 kg/mol).

| Property | Comparable to experiment? | Compare against, and caveats |
|---|---|---|
| Density ρ(T), thermal expansion α<sub>V</sub> | **Yes**, all resolutions | Melt data above T<sub>m</sub>. Below T<sub>m</sub>, the amorphous density extrapolated from the melt, not a semicrystalline sample. Accuracy is a property of the force field (SDK CG was fitted to density). |
| Compressibility κ<sub>T</sub> (bulk modulus 1/κ<sub>T</sub>) | **Yes** | Melt PVT data at 1 atm. CG models usually come out too compressible. |
| Surface tension γ, dγ/dT | **Yes** | Melt γ vs T at a similar molecular weight. SDK CG was partly fitted to γ. Our value depends on the cutoff (no tail correction at surfaces, D48), which tends to bias it low. |
| Chain size R<sub>g</sub>, R<sub>ee</sub>, C<sub>n</sub> | **Yes** | Neutron-scattering melt data (PE C∞ ≈ 6.7–7.4). CG and UA come out high, which is a force-field result. |
| Heat capacity C<sub>p</sub> | **AA only, after the quantum correction** (VDOS, D12c) | CG and UA remove degrees of freedom (H atoms, motions inside a bead), so their C<sub>p</sub> is far too low. Classical MD gives every vibration k<sub>B</sub> T, while real high-frequency C–H modes are mostly frozen, so classical AA C<sub>p</sub> is too high until corrected. |
| Dynamics: D, viscosity, P2 times, MSD | **AA roughly; UA partly; CG only with a time-mapping factor** | CG runs several times faster than real PE (smoothed energy landscape). UA is also somewhat fast (no hydrogen friction). Temperature trends are meaningful; absolute CG times need scaling to one experimental or AA point. |
| Young's modulus, Poisson ratio, yield (tensile) | **Not against separator data** | Real separator stiffness and yield come from crystals, and MD strain rates (10⁸–10⁹ s⁻¹) are about 10⁹× faster than tests. Only the amorphous-phase response and its trends with temperature and rate. |
| Pores: surface structure, hole closure | **No direct experiment** | The mechanism, and comparisons within our own simulations. |
| Puncture (`F_peak`, `d_break`, W), cavitation (`σ_cav`, `ε_cav`) | **Not against separator data** | nm-scale amorphous melt under MD rates (10³–10⁴× faster puncture, 10⁸ s⁻¹ tension), no bond breaking: T, rate and size trends only. |

**Our numbers next to experiment, with sources:** `docs/experiment_comparison.md`. In short, CG PE density is about 2% low, α<sub>V</sub> about 5% low, surface tension within 1–3%, κ<sub>T</sub> 50–60% too high, C<sub>p</sub> about 3× low (degrees of freedom), chains about 20% too large (C240), and dynamics about 4× too fast.

**Comparisons that hold at every resolution are the ones within our own simulations:** temperature trends from 25 to 160 °C, PE vs iPP at the same resolution, CG vs UA vs AA on the same property, and small vs 2×2×2 boxes. Most of the separator conclusions rest on these, not on absolute agreement with experiment.

### Thermodynamic properties

1. **Density ρ(T).** Mean density of each NPT segment. Steps use their second half; holds drop their first 10%. The error is the SEM from the statistical inefficiency (D26). Amorphous PE is about 0.85 g/cm³ extrapolated to 25 °C and about 0.77–0.78 g/cm³ as a melt near 150–160 °C.

2. **Thermal expansion α<sub>V</sub>.** α<sub>V</sub> = (1/V) dV/dT, from SEM-weighted straight-line fits of volume against T over 25–160, 25–90 and 90–160 °C.
   - Errors are scaled by √χ²<sub>red</sub> when χ²<sub>red</sub> > 1, so curvature shows up as a large χ²<sub>red</sub> and a larger error.
   - Expansion speeds up slightly with temperature, which is why the 25–160 °C fit is poor and the narrower windows are given.
   - Amorphous or molten PE is about 7–8 × 10⁻⁴ K⁻¹.

3. **Isothermal compressibility κ<sub>T</sub>.** κ<sub>T</sub> = (⟨V²⟩ − ⟨V⟩²)/(k<sub>B</sub> T ⟨V⟩), from the volume fluctuations of each NPT hold. The bulk modulus is K = 1/κ<sub>T</sub>. PE melt is roughly 1 GPa⁻¹ near 150 °C; CG models usually come out somewhat too compressible.

4. **Heat capacity C<sub>p</sub>.** C<sub>p</sub> = dH/dT per gram, fitted like α<sub>V</sub>. It is classical. UA and CG remove degrees of freedom (hydrogens, atoms inside beads), so their C<sub>p</sub> is far below real PE (about 2.3–2.6 J g⁻¹ K⁻¹ for the melt) and is not comparable to experiment. Only AA, with the quantum correction from the vibrational spectrum (VDOS, D12c), gives a meaningful C<sub>p</sub>.

### Chain size and shape

5. **R<sub>g</sub> and R<sub>ee</sub>.** Radius of gyration (mass-weighted, all atoms of a chain) and end-to-end distance, averaged over every hold frame. In a melt they barely depend on temperature.

6. **C<sub>n</sub> (characteristic ratio).** C<sub>n</sub> = ⟨R<sub>n</sub>²⟩/(n l²) for stretches of n backbone C–C bonds of length l = 1.54 Å.
   - It measures chain stiffness: 1 for a freely jointed chain, and higher with fixed bond angles and a preference for trans.
   - It levels off at C∞, about 6.7 for PE and 6.15 for iPP melts. We report the plateau for n ≥ 100 carbons (D37).
   - A higher C<sub>n</sub> means stiffer, more extended chains: ⟨R²⟩ = C∞ n l².
   - Under the project rule, a C<sub>n</sub> that misses the literature value in an equilibrated box is a property of the model, not a failure.

### Dynamics

7. **Bond reorientation time (P2 1/e).** ⟨P2(u(0)·u(t))⟩ of the backbone bond vectors, with the time at which it falls to 1/e. It measures how fast local segments reorient, which is set by local packing, not chain length. It speeds up strongly with temperature.

8. **Segment MSD, chain centre-of-mass MSD and D<sub>COM</sub>.**
   - Mean-square displacement of backbone sites and of whole chains, combining the dense 0.1 ps bursts and the 10 ps hold frames (D46).
   - D<sub>COM</sub> = slope/6 when the MSD is diffusive, meaning a log-slope of at least 0.9 over at least a factor of 2 in lag. Otherwise it is "not diffusive" and the largest slope is reported.
   - In a 12.5 ns hold the chains move less than their own size, so true chain diffusion would need much longer runs.

8b. **Long-hold D<sub>COM</sub> (`diffuse`, D53).** The same D<sub>COM</sub> criterion on a dedicated 300 ns NPT hold at one sweep temperature (CG), checked by `sepsim progress` while it runs. Only once the MSD is diffusive (and well beyond ⟨R<sub>g</sub>²⟩) is D<sub>COM</sub> a chain self-diffusion coefficient. The Rouse estimate η<sub>R</sub> = ρ<sub>N</sub> k<sub>B</sub> T ⟨R<sub>ee</sub>²⟩/(36 D), with ρ<sub>N</sub> the chain number density, converts it into a melt viscosity; it assumes unentangled chains, so for entangled ones it is a lower bound. For a PE melt of this chain length expect roughly 0.1 Pa·s (order of magnitude only); CG dynamics are faster, so CG viscosities come out lower.

8g. **End-to-end relaxation time τ<sub>ee</sub> (D56).** ⟨R(t)·R(0)⟩/⟨R²⟩ of the chain end-to-end vectors over every time origin, with the lag at which it falls to 1/e. It is the time a chain takes to forget its overall orientation and is the longest single-chain relaxation time; chain-scale averages (R<sub>g</sub>, R<sub>ee</sub>, C<sub>n</sub>) at a temperature are only equilibrated over holds of several τ<sub>ee</sub>. The lags reach half the hold (CG sweep holds 12.5 ns, UA 5 ns, AA 2.5 ns).

8h. **Rouse modes and τ<sub>p</sub> (D56).** X<sub>p</sub> = (1/N) Σ<sub>n</sub> cos(pπ(n−½)/N) r<sub>n</sub> splits a chain into standing waves along its backbone: p = 1 is the whole chain, p = 2 each half, p = N/p beads per wave. Each mode decorrelates on its own time τ<sub>p</sub> (1/e of ⟨X<sub>p</sub>(t)·X<sub>p</sub>(0)⟩/⟨X<sub>p</sub>²⟩), so the faster high-p modes are measurable in a short hold even when τ<sub>1</sub> ≈ τ<sub>ee</sub> is not. For an ideal, unentangled (Rouse) chain τ<sub>p</sub> = τ<sub>1</sub>/p², so τ<sub>1</sub>/τ<sub>2</sub> = 4 and p²τ<sub>p</sub> is flat; and ⟨X<sub>p</sub>²⟩ ∝ 1/p², so p²⟨X<sub>p</sub>²⟩ is flat (it falls at high p where the chain is stiffer than Gaussian). Real melts give τ<sub>p</sub> ∝ p^−2.2…−2.4, so τ<sub>1</sub> estimated as p²τ<sub>p</sub> from a high p is a lower bound. C240 PE is near the entanglement length, so Rouse scaling is only approximate. CG times are model times (× 4.07 for experiment).

8i. **"not reached" and "extrapolated" (D56).** A relaxation time whose ACF stays above 1/e out to the longest lag is "not reached". The table then gives only an exponential fit of ln C over 0.2 ≤ C ≤ 0.9, marked extrap.: it extends the early decay beyond the data, typically underestimates a stretched decay, and is an order-of-magnitude figure, not a measurement.

### Mechanical properties (`tensile`, `sepsim analyze tensile`, D54)

8c. **Stress–strain curve.** The box is stretched along one axis at a constant engineering strain rate (10⁸ or 10⁹ s⁻¹) while the other two axes are held at 1 atm; this is repeated along x, y and z from the same starting snapshot. True stress σ = −(P<sub>axis</sub> − 1 atm), tension positive; engineering stress is σ times the current over the initial cross-section.

8d. **Apparent modulus E<sub>app</sub>.** Slope of σ against strain up to `--fit-max` (default 0.02). For an amorphous melt above T<sub>g</sub> this is a high-frequency, rate-dependent response, not an equilibrium modulus; it falls as the rate falls. Bulk semicrystalline PE is of order 1 GPa because of its crystallinity, which these boxes do not have; an amorphous PE melt has no equilibrium modulus at all.

8e. **Poisson ratio ν.** ν = −d ln L<sub>lateral</sub> / d ln L<sub>axis</sub>. A melt that flows at constant volume gives 0.5; glassy polymers about 0.33–0.4. At MD rates the lateral barostat lags the pull, which biases ν low at small strain.

8f. **Peak and flow stress.** The maximum of the smoothed σ (with its strain), and the mean σ over strains 0.3–0.5. In a melt there is no true yield: the plateau is a viscous flow stress, about 3η × strain rate for a simple liquid, so it scales with the rate.

### Puncture and cavitation (`puncture`, `cavitation`, D57, D58)

8j. **Force–depth curve (puncture).** A hemispherical-tipped cylinder (radius R) is driven down through the free film at constant speed. F is the z force on the indenter (nN); depth d is how far the tip bottom is below the undisturbed film top at the start. Contact is where F first rises above the noise.

8k. **`F_peak` and `d_break`.** `F_peak` is the maximum of F averaged over 0.5 nm of depth. Break-through needs both the force to fall below half of `F_peak` (for 0.5 nm) and no material left just ahead of the tip; `d_break` is the depth where both hold. The tip passing the film's bottom surface is reported too. A melt film parts by chains pulling out and flowing, not by bonds breaking.

8l. **Puncture energy W.** ∫F dd from contact to the peak and to break-through, in aJ (1 aJ = 1 nN·nm = 144 kcal/mol). Rate-dependent like `F_peak`.

8m. **Re-seal.** After break-through the hole around the indenter column can close again by surface tension (a melt heals); the free radius √(R<sub>eff</sub>² − R²) about the axis and the time it stays below 3 Å.

8n. **Cavitation stress `σ_cav` and strain `ε_V`,cav.** The box is stretched equally along x, y and z at a fixed rate; `σ_h` = −(P − 1 atm) is the hydrostatic tension. It rises roughly as `K_app`·`ε_V`, peaks at `σ_cav` when a void opens, drops and settles to a plateau as the void grows. `K_app` is the initial slope (compare with 1/κ<sub>T</sub>).

8o. **Void fraction `φ_v`.** Space farther than a probe radius (4 Å) from every bead centre, swept by the probe, on a 2 Å grid, minus its value before stretching; the largest void's volume gives `R_void`. The first void (`R_void` > 1 nm for 3 frames in a row) gives a second, structural cavitation strain next to the pressure-based one. Both depend on the rate and, after cavitation, on the box size (one void per small box).

### Equilibration and quality checks

9. **D47 (chain mixing at 500 K).**
   - The criterion: the end-to-end vector ACF is below 1/e and the chain COM MSD is at least 2⟨R<sub>g</sub>²⟩, at a lag of half the combined 500 K hold.
   - Very long chains such as C1500 cannot reach it in affordable time. They are accepted on a stable C<sub>n</sub> plateau.

9b. **Crystallinity monitor (D56).** The D26 local-alignment order on ≤ 50 frames per hold: each backbone site's mean P2 with the chord vectors of other stems within `r_c` (CG: 1.4 σ of the bead pair, 6.3 Å; UA/AA: 6.5 Å), counted as ordered if p2 ≥ 0.4, with the fraction of ordered sites and the largest connected cluster. The threshold is **uncalibrated** (no crystal reference has been simulated), so the number is a melt baseline, not a crystallinity: a box that stays amorphous keeps a small, constant fraction with small clusters, and a fraction or cluster that grows during a hold would flag ordering. The baseline depends on the model (CG beads with near-straight bond angles show more local alignment than UA).

10. **Drift flags and hysteresis.** "drift seg …" marks segments whose thermo shows a significant trend over the analysis window; it is informational. Hysteresis is the largest density difference between the cooling and heating branches at the same T.

### Pores (stage 2, `sepsim analyze pore`, D51)

11. **Surface tension γ.** γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2] (two interfaces), per segment. It uses a plain LJ cutoff with no tail correction (D48), so γ depends on the cutoff.

12. **Density profile ρ(z).** Profile across the film: whether the interior matches bulk density, film thickness from the Gibbs dividing surfaces, interfacial width, actual gap width against the nominal 5 nm, and the closest approach of atoms across the gap.

13. **Near-surface behaviour.** Segment mobility (in-plane and normal), bond reorientation, bond orientation relative to the surface and chain shape, near the surface against the interior and bulk.

14. **Finite-size check (D50).** The 40-chain and 2×2×2 (320-chain) pores are compared on the quantities above.

### Finite hole (stage 2, `sepsim analyze hole`, D52)

15. **Hole radius R<sub>eff</sub>(t).** The beads are projected along z onto a 2 Å grid (lightly smoothed); the hole is the connected region near the tracked hole centre where the count is below half the undisturbed film's. R<sub>eff</sub> = √(A/π) from its area A. Centroid drift is how far the hole centre has wandered from where it was opened.

16. **R(z) and R<sub>min</sub>.** The same per 10 Å slab through the film interior. R<sub>min</sub> is the narrowest slab. A hole can be plugged inside while still open at both surfaces (R<sub>min</sub> ≈ 0 with R<sub>eff</sub> > 0), and the rim is usually wider at the surfaces.

17. **Closure time t<sub>close</sub> and closure speed dR/dt.** Closed means R<sub>min</sub> < 3 Å for 5 frames in a row (25 ps in the dense 5 ps window at the start of production and of a release, 250 ps after it). dR/dt is fitted over the first 5 ns and over the whole open period. In a viscous film the hole closes at roughly constant speed, about γ/η. These are CG model times, so compare runs with each other, not with experiment.

18. **Plateau radius.** For a hole that stays open, the mean R<sub>eff</sub> over the last quarter of the run.

19. **Scaffold checks.** The tethered beads (count, fraction, nearest to the axis, which must be at least R + d), and the "free shell" between R and R + d: its bead density against the far film (rim build-up) and how far its beads move (MSD), compared between free and scaffolded runs. The scaffold is a set of imposed springs standing in for the crystalline network. It is not crystallinity, and releasing it emulates melting rather than predicting a shutdown temperature.

All holes here are smaller than the film thickness (R/h ≤ 0.31), so surface tension is expected to close them. The runs measure how fast, not whether.

**Caveat.** The slit models a local patch of pore wall. Real separator pores are 30–100 nm across, curved and semicrystalline.

### Physical validity by system

The comparability table above is per property. Whether a property can actually be compared for a given system also depends on that system's own checks, so `results/summary.md` ("Physical validity by system") and `results/validity_overview.png` show one verdict per system and property:

- **comparable**: compare with the stated experimental data. The caveats still apply, and `docs/experiment_comparison.md` has the CG PE offsets.
- **trend**: only temperature, PE vs iPP, resolution and box-size trends are meaningful. Examples: chain size at a sweep temperature where the chains moved less than their own size in the hold (inherited from the 500 K melt), C1500 chain size (D47 not reached), tensile, film structure.
- **needs correction**: meaningful only after the stated correction. AA C<sub>p</sub> needs the VDOS quantum correction (D12c). CG dynamics need times × 4.07 (Hall et al. 2019), recalibrated per temperature against UA/AA. UA dynamics need a UA→AA time-mapping factor.
- **not meaningful**: CG and UA C<sub>p</sub> (removed degrees of freedom; use AA).
- **not yet computed**: the data do not exist yet. The reason gives the verdict once they do.

Offsets in density, κ<sub>T</sub> and chain size are force-field properties with no principled correction; compare the UA and AA values instead. A verdict is flagged when the system's 500 K equilibration is not accepted. The rules live in one place, `scripts/validity.py`, which is the single source of truth for both the summary and the figure.
