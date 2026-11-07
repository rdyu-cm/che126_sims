# System summary: tested properties and equilibration checks

- Generated: 2026-11-07 03:13 UTC
- Git commit: 12944b8
- Inputs: runs `/home/rdyu/projects/che126_sims/results/runs`, `/home/rdyu/projects/che126_sims/results/progress/rdyu-rog`, `/home/rdyu/projects/che126_sims/results/run_sidecars`; analysis `/home/rdyu/projects/worktrees/hole-r4nm160-results/results/analysis`; systems `/home/rdyu/projects/worktrees/hole-r4nm160-results/systems`
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
| `pe_cg_amorph_n40_c240_s1` | CG | PE | bulk | 40 × C240 | 3,200 beads | done | finished: prep, extend, cool, sweep, `diffuse_25C` (interrupted, 92.5%), `diffuse_160C` (interrupted, 85.2%), `diffuse_90C` (interrupted, 58.7%), `diffuse_130C`, `tensile_160C_r1e9`, `tensile_90C_r1e9`, `tensile_25C_r1e9`, `tensile_130C_r1e9`, `tensile_25C`, `tensile_160C`, `tensile_90C`, `tensile_130C` | D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C`, extend, sweep, `tensile_130C`, `tensile_130C_r1e9`, `tensile_160C`, `tensile_160C_r1e9`, `tensile_25C`, `tensile_25C_r1e9`, `tensile_90C`, `tensile_90C_r1e9` |
| `pe_cg_amorph_n40_c1500_s1` | CG | PE | bulk | 40 × C1500 | 20,000 beads | done | finished: prep, extend, cool, sweep | D47 n/a (long CG chain); ACF 0.68 at 250.0 ns, MSD/⟨R<sub>g</sub>²⟩ 0.12; 500.0 ns at 500 K; no C<sub>n</sub> drift: accepted | 7.43 vs 6.7 (outside band, info); no drift (Δ +0.21 ± 0.30) | sweep |
| `pe_cg_amorph_n320_c240_s1_rep222` | CG | PE | bulk (derived) | 320 × C240 | 25,600 beads | done | finished: extend (stopped after D47 PASS) | D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_amorph_n640_c240_s1_rep441` | CG | PE | bulk (derived) | 640 × C240 | 51,200 beads | done | finished: extend | D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | extend |
| `pe_cg_pore500k_w10nm_n40_c240_s1` | CG | PE | pore (wide, 10 nm) | 40 × C240 | 3,200 beads | done | finished: `pore_relax` | from `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | no |
| `pe_cg_pore_w5nm_n40_c240_s1` | CG | PE | pore (narrow, 5 nm) | 40 × C240 | 3,200 beads | done | finished: pore | from `pe_cg_pore500k_w10nm_n40_c240_s1` ← `pe_cg_amorph_n40_c240_s1`: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | pore |
| `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` | CG | PE | pore (wide, 10 nm) | 320 × C240 | 25,600 beads | done | finished: `pore_relax` | from `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_hole_r2nm_160C_n320_c240_s1_rep222` | CG | PE | hole (R 2 nm, 160 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free` |
| `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 130 °C) | 320 × C240 | 25,600 beads | `hole_scaf_rel0_failed_20261102` | failed, 0.0% | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 160 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free` |
| `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 25 °C) | 320 × C240 | 25,600 beads | `hole_ramp_rel130_col` | running, 6.8% (0/20 segments, Stage 1: inflate 20000 ps NVT at 298.15 K, radial push r0 0); ETA 2026-11-14 07:15 UTC | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222` | CG | PE | hole (R 3 nm, 90 °C) | 320 × C240 | 25,600 beads | `hole_free_failed_20261102` | failed, 0.0% | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222` | CG | PE | hole (R 4 nm, 160 °C) | 320 × C240 | 25,600 beads | done | finished: `hole_free` | from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | `hole_free` |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | CG | PE | pore (narrow, 5 nm) | 320 × C240 | 25,600 beads | done | finished: pore | from `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | pore |
| `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` | CG | PE | pore (wide, 12 nm) | 640 × C240 | 51,200 beads | done | finished: `pore_relax` | from `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_cg_pore_w5nm_n640_c240_s1_rep441` | CG | PE | pore (narrow, 5 nm) | 640 × C240 | 51,200 beads | pore | running, 18.4% (4/17 segments, Stage 3 cool 3/8 (424.3 K)); ETA 2026-11-09 10:58 UTC | from `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | 8.93 vs 6.7 (outside band, info); no drift (Δ -0.06 ± 0.08) | no |
| `pe_ua_amorph_n40_c240_s1` | UA | PE | bulk | 40 × C240 | 9,600 | done | finished: prep, extend (stopped after D47 PASS), cool, sweep | D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | extend, sweep |
| `pe_ua_pore500k_w10nm_n40_c240_s1` | UA | PE | pore (wide, 10 nm) | 40 × C240 | 9,600 | done | finished: `pore_relax` | from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | no |
| `pe_ua_pore_w5nm_n40_c240_s1` | UA | PE | pore (narrow, 5 nm) | 40 × C240 | 9,600 | pore | running, 34.1% (12/28 segments, seg 03 step 45 C); ETA 2026-11-12 14:23 UTC | from `pe_ua_pore500k_w10nm_n40_c240_s1` ← `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | no |
| `pe_aa_amorph_n40_c240_s1_from_ua` | AA | PE | bulk (derived) | 40 × C240 | 28,880 | sweep | running, 33.0% (8/22 segments, seg 08 step 90 C); ETA 2026-11-11 14:35 UTC | from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | no |
| `ipp_ua_amorph_n40_c240_s1` | UA | iPP | bulk | 40 × C240 | 12,760 | done | finished: prep (cancelled/killed?, 60.8%), extend (stopped after D47 PASS), cool, sweep | D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | sweep |
| `ipp_ua_pore500k_w10nm_n40_c240_s1` | UA | iPP | pore (wide, 10 nm) | 40 × C240 | 12,760 | done | finished: `pore_relax` | from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | no |
| `ipp_ua_pore_w5nm_n40_c240_s1` | UA | iPP | pore (narrow, 5 nm) | 40 × C240 | 12,760 | pore | running, 65.6% (21/28 segments, seg 12 step 120 C); ETA 2026-11-08 16:16 UTC | from `ipp_ua_pore500k_w10nm_n40_c240_s1` ← `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | no |
| `ipp_aa_amorph_n40_c240_s1_from_ua` | AA | iPP | bulk (derived) | 40 × C240 | 28,880 | `sweep_failed_20261102` | failed, 0.0% | from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | no |

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

| System | ρ(T) | α<sub>V</sub> | κ<sub>T</sub> | C<sub>p</sub> | R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K | R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T | P2, segment MSD | D<sub>COM</sub>, viscosity | γ, dγ/dT | film structure | tensile E/ν/yield | hole closure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `pe_cg_amorph_n40_c240_s1` | comp | comp | comp | no | comp | trend | corr | corr | n/a | n/a | trend | n/a |
| `pe_cg_amorph_n40_c1500_s1` | comp | comp | comp | no | trend | trend | corr | todo | n/a | n/a | todo | n/a |
| `pe_cg_amorph_n320_c240_s1_rep222` | todo | todo | todo | no | comp | todo | todo | todo | n/a | n/a | todo | n/a |
| `pe_cg_amorph_n640_c240_s1_rep441` | todo | todo | todo | no | comp | todo | todo | todo | n/a | n/a | todo | n/a |
| `pe_cg_pore500k_w10nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_cg_pore_w5nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | trend | corr | n/a | comp | trend | n/a | todo |
| `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_cg_hole_r2nm_160C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend |
| `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend |
| `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | trend |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | n/a | n/a | n/a | n/a | n/a | trend | corr | n/a | comp | trend | n/a | todo |
| `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_cg_pore_w5nm_n640_c240_s1_rep441` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_ua_amorph_n40_c240_s1` | comp | comp | comp | no | comp | trend | corr | todo | n/a | n/a | todo | n/a |
| `pe_ua_pore500k_w10nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `pe_ua_pore_w5nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | comp | todo | n/a | todo |
| `pe_aa_amorph_n40_c240_s1_from_ua` | todo | todo | todo | todo | trend | todo | todo | todo | n/a | n/a | todo | n/a |
| `ipp_ua_amorph_n40_c240_s1` | comp | comp | comp | no | comp | trend | corr | todo | n/a | n/a | todo | n/a |
| `ipp_ua_pore500k_w10nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | todo | todo | n/a | todo |
| `ipp_ua_pore_w5nm_n40_c240_s1` | n/a | n/a | n/a | n/a | n/a | todo | todo | n/a | comp | todo | n/a | todo |
| `ipp_aa_amorph_n40_c240_s1_from_ua` | todo | todo | todo | todo | trend | todo | todo | todo | n/a | n/a | todo | n/a |

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
- **VDOS**: vibrational density of states (quantum correction for C<sub>p</sub>)
- **CG / UA / AA**: coarse-grained (SDK/SPICA) / united-atom (TraPPE-UA) / all-atom (OPLS)

<details><summary>Reasons per system</summary>

- `pe_cg_amorph_n40_c240_s1`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.18–0.60 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 9.11 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - D<sub>COM</sub>, viscosity: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; diffusive and COM MSD ≥ 2⟨R<sub>g</sub>²⟩ at 130, 160 °C; the Rouse viscosity is a lower bound if the chains are entangled; vs experiment: CG PE dynamics ≈ 4× too fast (`docs/experiment_comparison.md`)
  - tensile E/ν/yield: **trend**: not comparable to separator data (their stiffness/yield come from crystallinity; MD rates ~10⁹× faster): amorphous response, T and rate trends; vs experiment: amorphous: compare with G<sub>e</sub> ≈ 2.6 MPa (E ≈ 8 MPa), not separator GPa moduli (`docs/experiment_comparison.md`)
  - **comparable**: ρ(T) (vs experiment: CG PE ≈ 2% low (C1500 1–2%) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 21 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows; vs experiment: CG PE ≈ 5% low (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (vs experiment: CG PE 50–60% too compressible (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 9.11 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_amorph_n40_c1500_s1`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K: **trend**: D47 not reached (C1500: end-to-end ACF 0.68, COM MSD/⟨R<sub>g</sub>²⟩ 0.12 at 250 ns): accepted on the C<sub>n</sub> no-drift rule only, so the whole-chain size is not equilibrated; C<sub>n</sub> 7.43 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.00–0.01 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 7.43 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.01, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - **comparable**: ρ(T) (vs experiment: CG PE ≈ 2% low (C1500 1–2%) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 27 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows; vs experiment: CG PE ≈ 5% low (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (vs experiment: CG PE 50–60% too compressible (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_amorph_n320_c240_s1_rep222`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - not yet computed: ρ(T) (then comparable), α<sub>V</sub> (then comparable), κ<sub>T</sub> (then comparable), R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then comparable), P2, segment MSD (then needs correction): no sweep run yet
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): no sweep run yet; needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - **comparable**: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 9.18 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_amorph_n640_c240_s1_rep441`
  - C<sub>p</sub>: **not meaningful**: CG removes all motion inside a 3-CH<sub>2</sub> bead (a bead keeps 3 of 27 atomic degrees of freedom): classical C<sub>p</sub> per gram far too low. No principled correction (a hybrid vibrational add-on is only approximate): use AA; vs experiment: CG PE classical C<sub>p</sub> ≈ 65% low (`docs/experiment_comparison.md`)
  - not yet computed: ρ(T) (then comparable), α<sub>V</sub> (then comparable), κ<sub>T</sub> (then comparable), R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then comparable), P2, segment MSD (then needs correction): no sweep run yet
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): no sweep run yet; needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - **comparable**: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 8.93 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values)
- `pe_cg_pore500k_w10nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
- `pe_cg_pore_w5nm_n40_c240_s1`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.20–0.84 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 9.11 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - film structure: **trend**: no direct experiment: mechanism and within-simulation comparisons
  - not yet computed: hole closure (then trend): no hole run (D52)
  - **comparable**: γ, dγ/dT (finite size (D50) vs `pe_cg_pore_w5nm_n320_c240_s1_rep222`: Δγ up to +1.2 mN/m (3.0 combined SEM, at 130 °C); vs experiment: CG PE γ within 1–3% at 25–160 °C; dγ/dT ≈ 20% shallower (`docs/experiment_comparison.md`))
- `pe_cg_pore500k_w10nm_n320_c240_s1_rep222`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
- `pe_cg_hole_r2nm_160C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
- `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): hole runs `hole_free` failed 0%, `hole_free_failed_20261102` failed 0%, `hole_scaf_rel0` failed 0%, `hole_scaf_rel0_failed_20261102` failed 0%
- `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
- `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): hole runs `hole_free` running 94%, `hole_free_failed_20261102` failed 0%, `hole_ramp_held` failed 0%, `hole_ramp_held_failed_20261102` failed 0%, `hole_ramp_rel130` failed 0%, `hole_ramp_rel130_col` running 7%, `hole_ramp_rel130_d4` running 7%, `hole_ramp_rel130_failed_20261102` failed 0%
- `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
  - not yet computed: hole closure (then trend): hole runs `hole_free` failed 0%, `hole_free_failed_20261102` failed 0%
- `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222`
  - hole closure: **trend**: no direct experiment: closure mechanism and trends only
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no pore run yet
- `pe_cg_pore_w5nm_n320_c240_s1_rep222`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.21–0.65 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 9.18 is outside the melt band (6.7 ±10%): a property of the CG force field, not of the equilibration; vs experiment: CG PE chains too stiff: C<sub>n</sub> +25–45% (C240), ≈ +10% (C1500); R<sub>g</sub> ≈ +20% (C240) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: SDK CG dynamics are faster than real PE (smoothed landscape). Correction: multiply CG times (P2, MSD times) by 4.07, i.e. D<sub>real</sub> ≈ D<sub>CG</sub>/4.07, η<sub>real</sub> ≈ 4.07·η<sub>CG</sub> (Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901, 2019); the factor depends on T, so recalibrate per T against our own UA/AA at the same T once available; T trends as is; vs experiment: CG PE dynamics ≈ 4× too fast (P2: a different vector than ¹³C NMR C–H) (`docs/experiment_comparison.md`)
  - film structure: **trend**: no direct experiment: mechanism and within-simulation comparisons
  - not yet computed: hole closure (then trend): no hole run (D52)
  - **comparable**: γ, dγ/dT (finite size (D50) vs `pe_cg_pore_w5nm_n40_c240_s1`: Δγ up to -1.2 mN/m (3.0 combined SEM, at 130 °C); vs experiment: CG PE γ within 1–3% at 25–160 °C; dγ/dT ≈ 20% shallower (`docs/experiment_comparison.md`))
- `pe_cg_pore500k_w12nm_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
- `pe_cg_pore_w5nm_n640_c240_s1_rep441`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (pore running 18%)
  - not yet computed: hole closure (then trend): no hole run (D52)
- `pe_ua_amorph_n40_c240_s1`
  - C<sub>p</sub>: **not meaningful**: UA removes the H atoms (their degrees of freedom), so classical C<sub>p</sub> is not the real one (close to experiment only by accident). No principled correction (a hybrid vibrational add-on is only approximate): use AA
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.01–0.14 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA force field, not of the equilibration; no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: UA dynamics are faster than real PE (no hydrogen friction). Correction: a UA→AA time-mapping factor per T from our own AA at the same T (none published for this force field here); T trends as is
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.14, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - **comparable**: ρ(T) (vs experiment: TraPPE-UA PE ≈ 1.5–2% high (literature, 448 K) (`docs/experiment_comparison.md`); no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (no principled correction for the offset (model property): compare our UA/AA values); R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA force field, not of the equilibration; no principled correction for the offset (model property): compare our UA/AA values)
- `pe_ua_pore500k_w10nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
- `pe_ua_pore_w5nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - **comparable**: γ, dγ/dT
- `pe_aa_amorph_n40_c240_s1_from_ua`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K: **trend**: ua2aa box: the chain conformations were equilibrated with the UA force field (D32/D47) and only relaxed locally in AA; compare the UA row; C<sub>n</sub> 8.19 is outside the melt band (6.7 ±10%): a property of the UA (source box) force field, not of the equilibration
  - not yet computed: ρ(T) (then comparable), α<sub>V</sub> (then comparable), κ<sub>T</sub> (then comparable), C<sub>p</sub> (then needs correction), R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then comparable), P2, segment MSD (then comparable): no sweep analysis yet (sweep running 33%, `sweep_crashed_20261102` cancelled/killed? 0%)
  - not yet computed: D<sub>COM</sub>, viscosity (then comparable): no sweep analysis yet (sweep running 33%, `sweep_crashed_20261102` cancelled/killed? 0%); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
- `ipp_ua_amorph_n40_c240_s1`
  - C<sub>p</sub>: **not meaningful**: UA removes the H atoms (their degrees of freedom), so classical C<sub>p</sub> is not the real one (close to experiment only by accident). No principled correction (a hybrid vibrational add-on is only approximate): use AA
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T: **trend**: inherited from the 500 K melt: hold COM MSD/⟨R<sub>g</sub>²⟩ 0.00–0.10 < 1 at 25, 90, 130, 160 °C, so chains did not move their own size and R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> were not re-equilibrated at that T (T dependence not resolved); no principled correction for the offset (model property): compare our UA/AA values
  - P2, segment MSD: **needs correction**: UA dynamics are faster than real PE (no hydrogen friction). Correction: a UA→AA time-mapping factor per T from our own AA at the same T (none published for this force field here); T trends as is; P2 1/e not reached at 25 °C
  - not yet computed: D<sub>COM</sub>, viscosity (then needs correction): sweep holds too short (COM MSD/⟨R<sub>g</sub>²⟩ ≤ 0.10, 4/4 not diffusive); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)
  - **comparable**: ρ(T) (no principled correction for the offset (model property): compare our UA/AA values); α<sub>V</sub> (V(T) curved (χ²<sub>red</sub> 106 over 25–160 °C): α<sub>V</sub> depends on T, quote the 25–90 / 90–160 °C windows; no principled correction for the offset (model property): compare our UA/AA values); κ<sub>T</sub> (no principled correction for the offset (model property): compare our UA/AA values); R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K (no principled correction for the offset (model property): compare our UA/AA values)
- `ipp_ua_pore500k_w10nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: γ, dγ/dT (then comparable): no γ from the hold segments (`pore_relax` finished 100%)
  - not yet computed: hole closure (then trend): no hole run (D52)
- `ipp_ua_pore_w5nm_n40_c240_s1`
  - not yet computed: R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then trend), P2, segment MSD (then needs correction), film structure (then trend): no pore analysis (D51) yet
  - not yet computed: hole closure (then trend): no hole run (D52)
  - **comparable**: γ, dγ/dT
- `ipp_aa_amorph_n40_c240_s1_from_ua`
  - R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> 500 K: **trend**: ua2aa box: the chain conformations were equilibrated with the UA force field (D32/D47) and only relaxed locally in AA; compare the UA row
  - not yet computed: ρ(T) (then comparable), α<sub>V</sub> (then comparable), κ<sub>T</sub> (then comparable), C<sub>p</sub> (then needs correction), R<sub>g</sub>/R<sub>ee</sub>/C<sub>n</sub> sweep T (then comparable), P2, segment MSD (then comparable): no sweep analysis yet (sweep failed 0%, `sweep_failed_20261102` failed 0%)
  - not yet computed: D<sub>COM</sub>, viscosity (then comparable): no sweep analysis yet (sweep failed 0%, `sweep_failed_20261102` failed 0%); needs a long D53 diffuse hold
  - not yet computed: tensile E/ν/yield (then trend): no tensile run (D54)

</details>

## Pending and known items

- `pe_cg_hole_r3nm_130C_n320_c240_s1_rep222`: `hole_scaf_rel0_failed_20261102`: failed, 0.0%
- `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222`: `hole_ramp_rel130_col`: running, 6.8% (0/20 segments, Stage 1: inflate 20000 ps NVT at 298.15 K, radial push r0 0); ETA 2026-11-14 07:15 UTC
- `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222`: `hole_free_failed_20261102`: failed, 0.0%
- `pe_cg_pore_w5nm_n640_c240_s1_rep441`: pore: running, 18.4% (4/17 segments, Stage 3 cool 3/8 (424.3 K)); ETA 2026-11-09 10:58 UTC
- `pe_ua_pore_w5nm_n40_c240_s1`: pore: running, 34.1% (12/28 segments, seg 03 step 45 C); ETA 2026-11-12 14:23 UTC
- `pe_aa_amorph_n40_c240_s1_from_ua`: sweep: running, 33.0% (8/22 segments, seg 08 step 90 C); ETA 2026-11-11 14:35 UTC
- `ipp_ua_pore_w5nm_n40_c240_s1`: pore: running, 65.6% (21/28 segments, seg 12 step 120 C); ETA 2026-11-08 16:16 UTC
- `ipp_aa_amorph_n40_c240_s1_from_ua`: `sweep_failed_20261102`: failed, 0.0%

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

### `pe_cg_amorph_n40_c240_s1`

PE CG, bulk amorphous box, 40 chains × C240, 3,200 beads; grown chains (seed 1). Status: finished: prep, extend, cool, sweep, `diffuse_25C` (interrupted, 92.5%), `diffuse_160C` (interrupted, 85.2%), `diffuse_90C` (interrupted, 58.7%), `diffuse_130C`, `tensile_160C_r1e9`, `tensile_90C_r1e9`, `tensile_25C_r1e9`, `tensile_130C_r1e9`, `tensile_25C`, `tensile_160C`, `tensile_90C`, `tensile_130C`.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.56; 80.0 ns at 500 K; accepted | — | `extend` progress |
| ρ (g/cm³) | 0.83453 ± 0.00009 | 0.79783 ± 0.00007 | 0.77580 ± 0.00011 | 0.75938 ± 0.00009 | 500 K: 0.72370 ± 0.00007 | comp | `extend`, `sweep` |
| ρ (g/cm³), long hold (D53) | 0.83523 ± 0.00010 | 0.79797 ± 0.00009 | 0.77580 ± 0.00004 | 0.75957 ± 0.00005 | — | comp | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| κ<sub>T</sub> (GPa⁻¹) | 1.000 ± 0.015 | 1.292 ± 0.022 | 1.502 ± 0.027 | 1.662 ± 0.031 | 500 K: 2.146 ± 0.025 | comp | `extend`, `sweep` |
| κ<sub>T</sub> (GPa⁻¹), long hold (D53) | 1.011 ± 0.005 | 1.271 ± 0.008 | 1.482 ± 0.008 | 1.638 ± 0.010 | — | comp | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 6.966 ± 0.041 (χ²<sub>red</sub> 20.9); 25–90 °C: 6.925 ± 0.035 (χ²<sub>red</sub> 3.27); 90–160 °C: 7.047 ± 0.048 (χ²<sub>red</sub> 6.12) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 0.826 ± 0.003 (χ²<sub>red</sub> 9.87); 25–90 °C: 0.843 ± 0.008 (χ²<sub>red</sub> 7.98); 90–160 °C: 0.818 ± 0.006 (χ²<sub>red</sub> 5.07) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 9.11 (melt 6.7) | comp | `extend` progress |
| R<sub>g</sub> (Å) | 31.24 ± 0.12 | 32.21 ± 0.21 | 30.84 ± 0.34 | 30.80 ± 0.39 | — | trend | `sweep` |
| R<sub>g</sub> (Å), long hold (D53) | 35.13 ± 0.51 | 32.15 ± 0.42 | 30.94 ± 0.15 | 29.79 ± 0.28 | — | trend | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| R<sub>ee</sub> (Å) | 77.1 ± 0.5 | 84.2 ± 1.0 | 77.6 ± 2.1 | 78.3 ± 1.4 | — | trend | `sweep` |
| R<sub>ee</sub> (Å), long hold (D53) | 89.5 ± 1.9 | 80.6 ± 2.0 | 78.3 ± 0.6 | 74.8 ± 1.0 | — | trend | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| C<sub>n</sub> | 10.27 ± 0.08 | 11.78 ± 0.19 | 10.58 ± 0.36 | 10.70 ± 0.34 | — | trend | `sweep` |
| C<sub>n</sub>, long hold (D53) | 13.88 ± 0.52 | 11.42 ± 0.43 | 10.63 ± 0.15 | 9.75 ± 0.25 | — | trend | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| P2 1/e time (ps) | 123 | 25.5 | 12.7 | 7.61 | — | corr | `sweep` |
| P2 1/e time (ps), long hold (D53) | 144 | 82.3 | 75.6 | 72.5 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| segment MSD at 1 ns lag (Å²) | 158.2 | 275.7 | 355.3 | 397.7 | — | corr | `sweep` |
| segment MSD at 1 ns lag (Å²), long hold (D53) | 161.6 | 279.6 | 349.5 | 396.2 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| max chain COM MSD (Å²) at lag | 176.9 at 12.5 ns | 396 at 12.5 ns | 522.8 at 12.5 ns | 572.5 at 12.5 ns | — | corr | `sweep` |
| max chain COM MSD (Å²) at lag, long hold (D53) | 2019 at 138.8 ns | 2069 at 88 ns | 4881 at 150 ns | 4669 at 127.8 ns | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.18 | 0.38 | 0.55 | 0.60 | — | corr | `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag, long hold (D53) | 1.64 | 2.00 | 5.10 | 5.26 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.90) | not diffusive (slope 0.98) | not diffusive (slope 0.90) | not diffusive (slope 0.99) | — | corr | `sweep` |
| D<sub>COM</sub> (cm²/s), long hold (D53) | not diffusive (slope 0.95) | not diffusive (slope 1.04) | 5.31e-07 ± 1.8e-08 | 6.08e-07 ± 6.2e-09 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| η<sub>Rouse</sub>, Rouse viscosity estimate (Pa·s), long hold (D53) | — | — | 0.025 | 0.021 | — | corr | `diffuse_160C` progress, `diffuse_130C` progress |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached (extrap. 46.5) | not reached (extrap. 30.7) | not reached (extrap. 18.2) | not reached (extrap. 25.5) | — | corr | `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns), long hold (D53) | 94.7 | 37.9 | 26.5 | 16.8 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached (extrap. 103) | not reached (extrap. 46.1) | not reached (extrap. 25) | not reached (extrap. 33.1) | — | corr | `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns), long hold (D53) | 116 | 46.3 | 34.1 | 23.3 | — | corr | `diffuse_130C`, `diffuse_160C`, `diffuse_25C`, `diffuse_90C` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.168 | 0.112 | 0.103 | 0.094 | — | — | `sweep` |
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

**`diffuse_130C` analysis**

`sepsim analyze hold`, generated 2026-11-04 22:33 UTC on rdyu-rog, run finished; segment Stage 1: NPT hold 300000 ps at 403.15 K; 300 ns analysed of 300 ns planned (complete).

- Note: Relaxation times use lags up to half the analysed hold (150 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D<sub>COM</sub> and relaxation times are model times (`docs/experiment_comparison.md`).
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`diffuse_160C` analysis**

`sepsim analyze hold`, generated 2026-11-02 14:13 UTC on rdyu-rog, run started; segment Stage 1: NPT hold 300000 ps at 433.15 K; 255.6 ns analysed of 300 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (127.8 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D<sub>COM</sub> and relaxation times are model times (`docs/experiment_comparison.md`).
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`diffuse_25C` analysis**

`sepsim analyze hold`, generated 2026-11-02 14:13 UTC on rdyu-rog, run started; segment Stage 1: NPT hold 300000 ps at 298.15 K; 277.5 ns analysed of 300 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (138.8 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D<sub>COM</sub> and relaxation times are model times (`docs/experiment_comparison.md`).
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`diffuse_90C` analysis**

`sepsim analyze hold`, generated 2026-11-02 14:13 UTC on rdyu-rog, run started; segment Stage 1: NPT hold 300000 ps at 363.15 K; 176 ns analysed of 300 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (88 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D<sub>COM</sub> and relaxation times are model times (`docs/experiment_comparison.md`).
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`extend` analysis**

`sepsim analyze hold`, generated 2026-10-30 19:25 UTC on rdyu-server, run finished; segment Stage 1: NPT hold extension 60000 ps at 500 K, 1 atm; — ns analysed of 60 ns planned (complete).

- Note: CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D<sub>COM</sub> and relaxation times are model times (`docs/experiment_comparison.md`).
- Note: No trajectory results: `hold_ext.dcd` is not in this run directory (a run on another node may keep its DCD there) or could not be read.
- Note: ../prep/hold.dcd not found: chain checks use the extension alone
- Note: trajectory not available (`hold_ext.dcd` not found)

**`sweep` analysis** (CG PE C240, 80.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-10-30 19:22 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.83453 ± 0.00009 | 1.000 ± 0.015 | 31.24 ± 0.12 | 77.1 ± 0.5 | 10.27 ± 0.08 | 123 | 176.9 at 12.5 ns | not diffusive (slope 0.90) | yes |
| 90 | 0.79783 ± 0.00007 | 1.292 ± 0.022 | 32.21 ± 0.21 | 84.2 ± 1.0 | 11.78 ± 0.19 | 25.5 | 396 at 12.5 ns | not diffusive (slope 0.98) | yes |
| 130 | 0.77580 ± 0.00011 | 1.502 ± 0.027 | 30.84 ± 0.34 | 77.6 ± 2.1 | 10.58 ± 0.36 | 12.7 | 522.8 at 12.5 ns | not diffusive (slope 0.90) | yes |
| 160 | 0.75938 ± 0.00009 | 1.662 ± 0.031 | 30.80 ± 0.39 | 78.3 ± 1.4 | 10.70 ± 0.34 | 7.61 | 572.5 at 12.5 ns | not diffusive (slope 0.99) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 6.966 ± 0.041 | 20.9 | 0.826 ± 0.003 | 9.87 | 15 |
| 90–160 | 7.047 ± 0.048 | 6.12 | 0.818 ± 0.006 | 5.07 | 8 |
| 25–90 | 6.925 ± 0.035 | 3.27 | 0.843 ± 0.008 | 7.98 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; CG also drops degrees of freedom (all motion inside a 3-CH<sub>2</sub> bead), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: D37 chain check FAIL on the prep hold + extension: C<sub>n</sub> plateau 9.11 vs melt 6.7 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).
- Note: CG time is not real time: SDK beads move faster than the atoms they represent, so MSD, D<sub>COM</sub> and P2 times are model times (not rescaled).

**`tensile_130C` analysis**

`sepsim analyze tensile`, generated 2026-10-31 17:54 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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

`sepsim analyze tensile`, generated 2026-10-31 00:21 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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

`sepsim analyze tensile`, generated 2026-10-31 05:55 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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

`sepsim analyze tensile`, generated 2026-10-31 00:21 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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

`sepsim analyze tensile`, generated 2026-10-31 00:20 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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

`sepsim analyze tensile`, generated 2026-10-31 00:20 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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

`sepsim analyze tensile`, generated 2026-10-31 11:51 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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

`sepsim analyze tensile`, generated 2026-10-31 00:21 UTC; E<sub>app</sub> and ν fitted up to strain 0.02, flow σ = mean true stress over strain 0.3–0.5.

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
| ρ (g/cm³) | 0.83817 ± 0.00004 | 0.80154 ± 0.00006 | 0.78019 ± 0.00004 | 0.76444 ± 0.00003 | — | comp | `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.995 ± 0.015 | 1.265 ± 0.022 | 1.435 ± 0.026 | 1.572 ± 0.029 | — | comp | `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 6.809 ± 0.022 (χ²<sub>red</sub> 27.2); 25–90 °C: 6.862 ± 0.018 (χ²<sub>red</sub> 2.29); 90–160 °C: 6.797 ± 0.033 (χ²<sub>red</sub> 11.8) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 0.812 ± 0.003 (χ²<sub>red</sub> 72.7); 25–90 °C: 0.840 ± 0.005 (χ²<sub>red</sub> 14.9); 90–160 °C: 0.793 ± 0.001 (χ²<sub>red</sub> 2.48) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 7.43 (melt 6.7) | trend | `extend` progress |
| R<sub>g</sub> (Å) | 67.79 ± 0.11 | 70.28 ± 0.13 | 70.04 ± 0.16 | 68.89 ± 0.25 | — | trend | `sweep` |
| R<sub>ee</sub> (Å) | 175.1 ± 1.4 | 179.3 ± 1.0 | 185.2 ± 1.6 | 169.2 ± 1.9 | — | trend | `sweep` |
| C<sub>n</sub> | 7.91 ± 0.02 | 8.46 ± 0.03 | 8.44 ± 0.03 | 8.06 ± 0.07 | — | trend | `sweep` |
| P2 1/e time (ps) | 128 | 26.9 | 14.3 | 8.78 | — | corr | `sweep` |
| segment MSD at 1 ns lag (Å²) | 153.6 | 250.2 | 294.9 | 322.3 | — | corr | `sweep` |
| max chain COM MSD (Å²) at lag | 21.94 at 12.5 ns | 29.7 at 12.5 ns | 37.17 at 12.5 ns | 44.85 at 12.5 ns | — | todo | `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.00 | 0.01 | 0.01 | 0.01 | — | todo | `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.42) | not diffusive (slope 0.69) | not diffusive (slope 0.48) | not diffusive (slope 0.50) | — | todo | `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached | not reached | not reached | — | todo | `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | — | todo | `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.191 | 0.111 | 0.095 | 0.088 | — | — | `sweep` |

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

**`sweep` analysis** (CG PE C1500, 500.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-02 14:00 UTC on rdyu-rog, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.83817 ± 0.00004 | 0.995 ± 0.015 | 67.79 ± 0.11 | 175.1 ± 1.4 | 7.91 ± 0.02 | 128 | 21.94 at 12.5 ns | not diffusive (slope 0.42) | yes |
| 90 | 0.80154 ± 0.00006 | 1.265 ± 0.022 | 70.28 ± 0.13 | 179.3 ± 1.0 | 8.46 ± 0.03 | 26.9 | 29.7 at 12.5 ns | not diffusive (slope 0.69) | yes |
| 130 | 0.78019 ± 0.00004 | 1.435 ± 0.026 | 70.04 ± 0.16 | 185.2 ± 1.6 | 8.44 ± 0.03 | 14.3 | 37.17 at 12.5 ns | not diffusive (slope 0.48) | yes |
| 160 | 0.76444 ± 0.00003 | 1.572 ± 0.029 | 68.89 ± 0.25 | 169.2 ± 1.9 | 8.06 ± 0.07 | 8.78 | 44.85 at 12.5 ns | not diffusive (slope 0.50) | yes |

| Fit window (°C) | α<sub>V</sub> (10⁻⁴ K⁻¹) | χ²<sub>red</sub> of the α<sub>V</sub> fit | C<sub>p</sub> classical (J g⁻¹ K⁻¹) | χ²<sub>red</sub> of the C<sub>p</sub> fit | points in the fit |
|---|---|---|---|---|---|
| 25–160 | 6.809 ± 0.022 | 27.2 | 0.812 ± 0.003 | 72.7 | 15 |
| 90–160 | 6.797 ± 0.033 | 11.8 | 0.793 ± 0.001 | 2.48 | 8 |
| 25–90 | 6.862 ± 0.018 | 2.29 | 0.840 ± 0.005 | 14.9 | 8 |

- Note: C<sub>p</sub> is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k<sub>B</sub>/2 per quadratic term; CG also drops degrees of freedom (all motion inside a 3-CH<sub>2</sub> bead), so its C<sub>p</sub> per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep hold + extension (extend/progress.json: end-to-end ACF 0.68 at 250.0 ns, needs < 1/e; COM MSD/<R<sub>g</sub>²> 0.12, needs >= 2).
- Note: D37 chain check FAIL on the prep hold + extension: C<sub>n</sub> plateau 7.43 vs melt 6.7 ±10%.
- Note: α<sub>V</sub> and C<sub>p</sub> are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²<sub>red</sub>, and a large χ²<sub>red</sub> over 25–160 °C means α<sub>V</sub> or C<sub>p</sub> depends on T (compare the two half windows).
- Note: CG time is not real time: SDK beads move faster than the atoms they represent, so MSD, D<sub>COM</sub> and P2 times are model times (not rescaled).

</details>

### `pe_cg_amorph_n320_c240_s1_rep222`

PE CG, bulk amorphous box, replicated 2×2×2, 320 chains × C240, 25,600 beads; built from `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`). Status: finished: extend (stopped after D47 PASS).

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 9.18 (melt 6.7) | comp | `extend` progress |

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

- Sweep analysis: not analysed yet.

</details>

### `pe_cg_amorph_n640_c240_s1_rep441`

PE CG, bulk amorphous box, replicated 4×4×1, 640 chains × C240, 51,200 beads; built from `pe_cg_amorph_n40_c240_s1` (`extend/hold_ext_60ns.data`). Status: finished: extend.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted | — | `extend` progress |
| ρ (g/cm³) | — | — | — | — | 500 K: 0.72364 ± 0.00002 | todo | `extend` |
| κ<sub>T</sub> (GPa⁻¹) | — | — | — | — | 500 K: 2.118 ± 0.021 | todo | `extend` |
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

`sepsim analyze hold`, generated 2026-11-06 10:08 UTC on rdyu-rog, run finished; segment Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm; 80 ns analysed of 80 ns planned (complete).

- Note: Relaxation times use lags up to half the analysed hold (40 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D<sub>COM</sub> and relaxation times are model times (`docs/experiment_comparison.md`).
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

Pore analysis (`sepsim analyze pore`, generated 2026-10-30 19:29 UTC on rdyu-server):

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
- Note: CG time is not real time: SDK beads move faster than the atoms they represent, so MSD and P2 times are model times (not rescaled).

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

PE CG, film with a 3 nm-radius cylindrical hole at 130 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_130C.data`). Stage now: `hole_scaf_rel0_failed_20261102` (failed, 0.0%).

No analysed properties yet; pending: `hole_scaf_rel0_failed_20261102`: failed, 0.0%. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.5038 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_130C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC
- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_130C_n320_c240_s1_rep222/data.lmp`
- **`hole_scaf_rel0`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC
- **`hole_scaf_rel0_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_130C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | `hole_scaf_rel0_failed_20261102`: failed, 0.0% | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r3nm_160C_n320_c240_s1_rep222`

PE CG, film with a 3 nm-radius cylindrical hole at 160 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`). Status: finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.4949 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`
- **`hole_scaf_rel0`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC
- **`hole_scaf_rel0_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`
- **`hole_free`** (rdyu-server): finished; started 2026-11-02 20:16 UTC, ended 2026-11-05 05:32 UTC; reads `systems/pe_cg_hole_r3nm_160C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_free_failed_20261102` (failed, 0.0%), `hole_scaf_rel0` (failed, 0.0%), `hole_scaf_rel0_failed_20261102` (failed, 0.0%), `hole_free` | `hole_free` |

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


</details>

### `pe_cg_hole_r3nm_25C_n320_c240_s1_rep222`

PE CG, film with a 3 nm-radius cylindrical hole at 25 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_25C.data`). Stage now: `hole_ramp_rel130_col` (running, 6.8% (0/20 segments, Stage 1: inflate 20000 ps NVT at 298.15 K, radial push r0 0); ETA 2026-11-14 07:15 UTC).

No analysed properties yet; pending: `hole_ramp_rel130_col`: running, 6.8% (0/20 segments, Stage 1: inflate 20000 ps NVT at 298.15 K, radial push r0 0); ETA 2026-11-14 07:15 UTC. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

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

- **`hole_ramp_rel130`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_rel130_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_held`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_held_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_free`** (rdyu-server): running, 94.0% (2/3 segments, Stage 3: hold at 25 C); ETA 2026-11-07 08:33 UTC; started 2026-11-02 20:16 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_rel130_d4`** (rdyu-server): running, 6.8% (0/20 segments, Stage 1: inflate 20000 ps NVT at 298.15 K, radial push r0 0); ETA 2026-11-14 06:53 UTC; started 2026-11-06 14:44 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`
- **`hole_ramp_rel130_col`** (rdyu-server): running, 6.8% (0/20 segments, Stage 1: inflate 20000 ps NVT at 298.15 K, radial push r0 0); ETA 2026-11-14 07:15 UTC; started 2026-11-06 14:44 UTC; reads `systems/pe_cg_hole_r3nm_25C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | `hole_ramp_rel130_col`: running, 6.8% (0/20 segments, Stage 1: inflate 20000 ps NVT at 298.15 K, radial push r0 0); ETA 2026-11-14 07:15 UTC | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r3nm_90C_n320_c240_s1_rep222`

PE CG, film with a 3 nm-radius cylindrical hole at 90 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_90C.data`). Stage now: `hole_free_failed_20261102` (failed, 0.0%).

No analysed properties yet; pending: `hole_free_failed_20261102`: failed, 0.0%. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.5160 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_90C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC
- **`hole_free_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 18:40 UTC, ended 2026-11-02 18:40 UTC; reads `systems/pe_cg_hole_r3nm_90C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | `hole_free_failed_20261102`: failed, 0.0% | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_cg_hole_r4nm_160C_n320_c240_s1_rep222`

PE CG, film with a 4 nm-radius cylindrical hole at 160 °C, 320 chains × C240, 25,600 beads; built from `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`). Status: finished: `hole_free`.

No analysed properties yet. Equilibration: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field `sdk_cg`, box density 0.4577 g/cm³ (as built)
- Replicated 2×2×2 from `pe_cg_amorph_n40_c240_s1`
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: `pe_cg_pore_w5nm_n320_c240_s1_rep222` (`pore/hold_160C.data`) ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` (`pore_relax/relaxed.data`) ← `pe_cg_amorph_n320_c240_s1_rep222` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_cg_pore_w5nm_n320_c240_s1_rep222` ← `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` ← `pe_cg_amorph_n320_c240_s1_rep222`: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨R<sub>g</sub>²⟩ 2.65; 72.5 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **`hole_free`** (rdyu-server): finished; started 2026-11-02 20:16 UTC, ended 2026-11-07 03:09 UTC; reads `systems/pe_cg_hole_r4nm_160C_n320_c240_s1_rep222/data.lmp`

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | — | finished: `hole_free` | `hole_free` |

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

Pore analysis (`sepsim analyze pore`, generated 2026-10-30 19:35 UTC on rdyu-server):

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
- Note: CG time is not real time: SDK beads move faster than the atoms they represent, so MSD and P2 times are model times (not rescaled).

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

### `pe_cg_pore_w5nm_n640_c240_s1_rep441`

PE CG, 5 nm dry slit pore, 640 chains × C240, 51,200 beads; built from `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` (`pore_relax/relaxed.data`). Stage now: pore (running, 18.4% (4/17 segments, Stage 3 cool 3/8 (424.3 K)); ETA 2026-11-09 10:58 UTC).

No analysed properties yet; pending: pore: running, 18.4% (4/17 segments, Stage 3 cool 3/8 (424.3 K)); ETA 2026-11-09 10:58 UTC. Equilibration: from `pe_cg_pore500k_w12nm_n640_c240_s1_rep441` ← `pe_cg_amorph_n640_c240_s1_rep441`: D47 PASS; ACF 0.06 at 40.0 ns, MSD/⟨R<sub>g</sub>²⟩ 3.35; 80.0 ns at 500 K; accepted.

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

- **pore** (rdyu-rog): running, 18.4% (4/17 segments, Stage 3 cool 3/8 (424.3 K)); ETA 2026-11-09 10:58 UTC; started 2026-11-06 14:43 UTC

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.69 nm | 6.5 nm | 25.8 × 25.8 nm (25 °C) | — | pore: running, 18.4% (4/17 segments, Stage 3 cool 3/8 (424.3 K)); ETA 2026-11-09 10:58 UTC | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_ua_amorph_n40_c240_s1`

PE UA, bulk amorphous box, 40 chains × C240, 9,600 united atoms; grown chains (seed 1). Status: finished: prep, extend (stopped after D47 PASS), cool, sweep.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | — | `extend` progress |
| ρ (g/cm³) | 0.86142 ± 0.00045 | 0.82268 ± 0.00035 | 0.80014 ± 0.00016 | 0.78336 ± 0.00025 | 500 K: 0.74581 ± 0.00008 | comp | `extend`, `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.681 ± 0.033 | 0.884 ± 0.021 | 1.117 ± 0.023 | 1.192 ± 0.024 | 500 K: 1.632 ± 0.010 | comp | `extend`, `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 7.151 ± 0.057 (χ²<sub>red</sub> 5.03); 25–90 °C: 6.946 ± 0.200 (χ²<sub>red</sub> 6.04); 90–160 °C: 7.007 ± 0.067 (χ²<sub>red</sub> 1.19) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 2.431 ± 0.011 (χ²<sub>red</sub> 18.7); 25–90 °C: 2.439 ± 0.041 (χ²<sub>red</sub> 26.4); 90–160 °C: 2.385 ± 0.019 (χ²<sub>red</sub> 9.98) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 8.19 (melt 6.7) | comp | `extend` progress |
| R<sub>g</sub> (Å) | 29.33 ± 0.07 | 29.95 ± 0.10 | 30.91 ± 0.34 | 29.59 ± 0.14 | — | trend | `sweep` |
| R<sub>g</sub> (Å), 500 K hold | — | — | — | — | 500 K: 27.32 ± 0.46 | comp | `extend` |
| R<sub>ee</sub> (Å) | 72.9 ± 0.4 | 74.3 ± 1.3 | 78.9 ± 1.9 | 75.7 ± 0.8 | — | trend | `sweep` |
| R<sub>ee</sub> (Å), 500 K hold | — | — | — | — | 500 K: 68.7 ± 1.4 | comp | `extend` |
| C<sub>n</sub> | 9.21 ± 0.01 | 9.86 ± 0.14 | 10.86 ± 0.34 | 9.85 ± 0.10 | — | trend | `sweep` |
| C<sub>n</sub>, 500 K hold | — | — | — | — | 500 K: 8.19 ± 0.35 | comp | `extend` |
| P2 1/e time (ps) | 60.1 | 11.1 | 5.43 | 3.6 | 500 K: 6.96 | corr | `extend`, `sweep` |
| segment MSD at 1 ns lag (Å²) | 28.3 | 117.7 | 177.6 | 237.4 | 500 K: 365.1 | corr | `extend`, `sweep` |
| max chain COM MSD (Å²) at lag | 7.53 at 5 ns | 47.79 at 5 ns | 91.35 at 5 ns | 121.5 at 5 ns | 500 K: 1699 at 49.1 ns | todo | `extend`, `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.01 | 0.05 | 0.10 | 0.14 | 500 K: 2.28 | todo | `extend`, `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.84) | not diffusive (slope 0.83) | not diffusive (slope 0.89) | not diffusive (slope 0.96) | 500 K: not diffusive (slope 0.89) | todo | `extend`, `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached (extrap. 49.2) | not reached (extrap. 29.4) | not reached (extrap. 28.1) | 500 K: 19.3 | todo | `extend`, `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | 500 K: 25.9 | todo | `extend`, `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.122 | 0.053 | 0.036 | 0.030 | 500 K: 0.021 | — | `extend`, `sweep` |

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

`sepsim analyze hold`, generated 2026-10-30 19:25 UTC on rdyu-server, run started; segment Stage 1: NPT hold extension 80000 ps at 500 K, 1 atm; 98.19 ns analysed of 80 ns planned (not complete).

- Note: Relaxation times use lags up to half the analysed hold (49.1 ns); a time beyond that is 'not reached' and only the extrapolated exponential fit is given.
- Note: hold not complete: thermo and trajectory over the part run
- Note: no burst DCDs (deck without D46 bursts): lags from the hold DCD only

**`sweep` analysis** (UA PE C240, 98.2 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-04 22:10 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.86142 ± 0.00045 | 0.681 ± 0.033 | 29.33 ± 0.07 | 72.9 ± 0.4 | 9.21 ± 0.01 | 60.1 | 7.53 at 5 ns | not diffusive (slope 0.84) | yes |
| 90 | 0.82268 ± 0.00035 | 0.884 ± 0.021 | 29.95 ± 0.10 | 74.3 ± 1.3 | 9.86 ± 0.14 | 11.1 | 47.79 at 5 ns | not diffusive (slope 0.83) | yes |
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

PE UA, 5 nm dry slit pore, 40 chains × C240, 9,600 united atoms; built from `pe_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`). Stage now: pore (running, 34.1% (12/28 segments, seg 03 step 45 C); ETA 2026-11-12 14:23 UTC).

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `pe_ua_pore500k_w10nm_n40_c240_s1` ← `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted | — | `extend` progress of `pe_ua_amorph_n40_c240_s1` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 8.19 (melt 6.7) | n/a | `extend` progress of `pe_ua_amorph_n40_c240_s1` |
| γ, run monitor (mN/m) | 33.0 ± 2.8 | — | — | — | — | comp | `pore` progress |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- PE UA, 40 chains × C240 (C240H482), 9,600 atoms/beads, force field `trappe_ua`, box density 0.4387 g/cm³ (as built)
- Pore: narrow pore, nominal 5 nm, 4.68 nm at 500 K, wall 6.38 nm, clear gap 2.25 nm, area 44.8 nm²
- Built from: `pe_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`) ← `pe_ua_amorph_n40_c240_s1` (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from `pe_ua_pore500k_w10nm_n40_c240_s1` ← `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted
- C<sub>n</sub> plateau (D37): 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)

**Stages**

- **pore** (rdyu-server): running, 34.1% (12/28 segments, seg 03 step 45 C); ETA 2026-11-12 14:23 UTC; started 2026-11-04 22:15 UTC; reads `systems/pe_ua_pore_w5nm_n40_c240_s1/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 33.0 ± 2.8

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.68 nm | 6.4 nm | 6.4 × 6.4 nm (25 °C) | 25 °C 33.0 ± 2.8 | pore: running, 34.1% (12/28 segments, seg 03 step 45 C); ETA 2026-11-12 14:23 UTC | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `pe_aa_amorph_n40_c240_s1_from_ua`

PE AA, bulk amorphous box, converted from the relaxed UA box (ua2aa), 40 chains × C240, 28,880 atoms; built from `pe_ua_amorph_n40_c240_s1` (`hold_ext_70ns.data`). Stage now: sweep (running, 33.0% (8/22 segments, seg 08 step 90 C); ETA 2026-11-11 14:35 UTC).

No analysed properties yet; pending: sweep: running, 33.0% (8/22 segments, seg 08 step 90 C); ETA 2026-11-11 14:35 UTC. Equilibration: from `pe_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨R<sub>g</sub>²⟩ 2.28; 98.2 ns at 500 K; accepted.

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
- **sweep** (rdyu-rog): running, 33.0% (8/22 segments, seg 08 step 90 C); ETA 2026-11-11 14:35 UTC; started 2026-11-03 01:01 UTC; reads `../prep/cooled.data`
  - monitor flags: drift seg 4; hyst max 0.44%

- Sweep analysis: not analysed yet.

</details>

### `ipp_ua_amorph_n40_c240_s1`

iPP UA, bulk amorphous box, 40 chains × C240, 12,760 united atoms; grown chains (seed 1). Status: finished: prep (cancelled/killed?, 60.8%), extend (stopped after D47 PASS), cool, sweep.

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress |
| ρ (g/cm³) | 0.86029 ± 0.00022 | 0.83585 ± 0.00025 | 0.81456 ± 0.00045 | 0.79855 ± 0.00024 | — | comp | `sweep` |
| κ<sub>T</sub> (GPa⁻¹) | 0.582 ± 0.012 | 0.803 ± 0.027 | 1.122 ± 0.053 | 1.190 ± 0.034 | — | comp | `sweep` |
| α<sub>V</sub> (10⁻⁴ K⁻¹) | — | — | — | — | 25–160 °C: 5.755 ± 0.223 (χ²<sub>red</sub> 106); 25–90 °C: 4.434 ± 0.372 (χ²<sub>red</sub> 52.9); 90–160 °C: 6.619 ± 0.103 (χ²<sub>red</sub> 3.45) | comp | `sweep` |
| C<sub>p</sub>, classical (J g⁻¹ K⁻¹) | — | — | — | — | 25–160 °C: 2.511 ± 0.021 (χ²<sub>red</sub> 84); 25–90 °C: 2.409 ± 0.027 (χ²<sub>red</sub> 32.4); 90–160 °C: 2.657 ± 0.019 (χ²<sub>red</sub> 6.44) | no | `sweep` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 5.66 (melt 6.15) | comp | `extend` progress |
| R<sub>g</sub> (Å) | 19.47 ± 0.01 | 19.80 ± 0.01 | 19.75 ± 0.04 | 19.63 ± 0.06 | — | trend | `sweep` |
| R<sub>ee</sub> (Å) | 50.3 ± 0.1 | 50.8 ± 0.4 | 49.1 ± 0.2 | 49.7 ± 0.3 | — | trend | `sweep` |
| C<sub>n</sub> | 6.46 ± 0.00 | 6.64 ± 0.03 | 6.33 ± 0.03 | 6.32 ± 0.03 | — | trend | `sweep` |
| P2 1/e time (ps) | — | 1.78e+03 | 237 | 79.3 | — | corr | `sweep` |
| segment MSD at 1 ns lag (Å²) | 2.8 | 10.47 | 33.83 | 69.23 | — | corr | `sweep` |
| max chain COM MSD (Å²) at lag | 0.5077 at 5 ns | 2.678 at 5 ns | 14.66 at 5 ns | 37.52 at 5 ns | — | todo | `sweep` |
| chain COM MSD / ⟨R<sub>g</sub>²⟩ at the longest lag | 0.00 | 0.01 | 0.04 | 0.10 | — | todo | `sweep` |
| D<sub>COM</sub> (cm²/s) | not diffusive (slope 0.68) | not diffusive (slope 0.48) | not diffusive (slope 0.75) | not diffusive (slope 0.56) | — | todo | `sweep` |
| τ<sub>ee</sub>, end-to-end vector 1/e time (ns) | not reached | not reached | not reached | not reached (extrap. 24.3) | — | todo | `sweep` |
| τ<sub>1</sub>, slowest Rouse mode 1/e time (ns) | not reached | not reached | not reached | not reached | — | todo | `sweep` |
| ordered-site fraction (crystallinity monitor, uncalibrated) | 0.137 | 0.138 | 0.143 | 0.134 | — | — | `sweep` |

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

**`sweep` analysis** (UA iPP C240, 60.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-11-04 05:40 UTC on rdyu-rog, run finished.

| T (°C) | ρ (g/cm³) | κ<sub>T</sub> (GPa⁻¹) | R<sub>g</sub> (Å) | R<sub>ee</sub> (Å) | C<sub>n</sub> | P2 1/e time (ps) | max chain COM MSD (Å²) at lag | D<sub>COM</sub> (cm²/s) | trajectory analysed |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.86029 ± 0.00022 | 0.582 ± 0.012 | 19.47 ± 0.01 | 50.3 ± 0.1 | 6.46 ± 0.00 | — | 0.5077 at 5 ns | not diffusive (slope 0.68) | yes |
| 90 | 0.83585 ± 0.00025 | 0.803 ± 0.027 | 19.80 ± 0.01 | 50.8 ± 0.4 | 6.64 ± 0.03 | 1.78e+03 | 2.678 at 5 ns | not diffusive (slope 0.48) | yes |
| 130 | 0.81456 ± 0.00045 | 1.122 ± 0.053 | 19.75 ± 0.04 | 49.1 ± 0.2 | 6.33 ± 0.03 | 237 | 14.66 at 5 ns | not diffusive (slope 0.75) | yes |
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

iPP UA, 5 nm dry slit pore, 40 chains × C240, 12,760 united atoms; built from `ipp_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`). Stage now: pore (running, 65.6% (21/28 segments, seg 12 step 120 C); ETA 2026-11-08 16:16 UTC).

| Property | 25 °C | 90 °C | 130 °C | 160 °C | Other (500 K, fits) | Validity | Source |
|---|---|---|---|---|---|---|---|
| 500 K equilibration (D47) | — | — | — | — | from `ipp_ua_pore500k_w10nm_n40_c240_s1` ← `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational) | — | `extend` progress of `ipp_ua_amorph_n40_c240_s1` |
| C<sub>n</sub> plateau, 500 K (D37) | — | — | — | — | 500 K: 5.66 (melt 6.15) | n/a | `extend` progress of `ipp_ua_amorph_n40_c240_s1` |
| γ, run monitor (mN/m) | 20.1 ± 3.2 | 22.3 ± 3.5 | — | — | — | comp | `pore` progress |

<details><summary>Full analysis tables and checks</summary>

**Provenance**

- iPP UA, 40 chains × C240 (C240H482), 12,760 atoms/beads, force field `trappe_ua`, box density 0.4447 g/cm³ (as built)
- Pore: narrow pore, nominal 5 nm, 4.74 nm at 500 K, wall 6.36 nm, clear gap 2.62 nm, area 44.3 nm²
- Built from: `ipp_ua_pore500k_w10nm_n40_c240_s1` (`pore_relax/relaxed.data`) ← `ipp_ua_amorph_n40_c240_s1` (`extend/hold_ext_40ns.data`)

**Equilibration**

- Verdict: from `ipp_ua_pore500k_w10nm_n40_c240_s1` ← `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational)
- C<sub>n</sub> plateau (D37): 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)

**Stages**

- **pore** (rdyu-rog): running, 65.6% (21/28 segments, seg 12 step 120 C); ETA 2026-11-08 16:16 UTC; started 2026-11-04 10:09 UTC
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 20.1 ± 3.2; 90 °C 22.3 ± 3.5

| Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|
| narrow | 5 nm (at 25 °C) | 4.74 nm | 6.4 nm | 6.4 × 6.4 nm (25 °C) | 25 °C 20.1 ± 3.2; 90 °C 22.3 ± 3.5 | pore: running, 65.6% (21/28 segments, seg 12 step 120 C); ETA 2026-11-08 16:16 UTC | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (L<sub>z</sub>/2)[P<sub>zz</sub> − (P<sub>xx</sub>+P<sub>yy</sub>)/2]).

</details>

### `ipp_aa_amorph_n40_c240_s1_from_ua`

iPP AA, bulk amorphous box, converted from the relaxed UA box (ua2aa), 40 chains × C240, 28,880 atoms; built from `ipp_ua_amorph_n40_c240_s1` (`hold_ext_40ns.data`). Stage now: `sweep_failed_20261102` (failed, 0.0%).

No analysed properties yet; pending: `sweep_failed_20261102`: failed, 0.0%. Equilibration: from `ipp_ua_amorph_n40_c240_s1`: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨R<sub>g</sub>²⟩ 2.06; 60.0 ns at 500 K; accepted (C<sub>n</sub> drift over prep + extension, informational).

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
  - monitor flags: R<sub>ee</sub> not decorrelated (0.72 at 2.5 ns); MSD/R<sub>g</sub>² 0.25; drift seg 9,12
- **sweep** (rdyu-rog): failed, 0.0%; started 2026-11-02 14:06 UTC, ended 2026-11-02 14:06 UTC; reads `../prep/cooled.data`
- **`sweep_failed_20261102`** (rdyu-rog): failed, 0.0%; started 2026-11-02 14:06 UTC, ended 2026-11-02 14:06 UTC
- Superseded (not used): `sweep_cancelled_pe_first` (cancelled/killed?)

- Sweep analysis: not analysed yet.

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
