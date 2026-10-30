# System summary: tested properties and equilibration checks

- Generated: 2026-10-30 17:50 UTC
- Git commit: d1a7898 (dirty)
- Inputs: runs /home/rdyu/projects/che126_sims/results/runs, /home/rdyu/projects/che126_sims/results/progress/rdyu-rog; analysis /home/rdyu/projects/che126_sims/results/analysis; systems /home/rdyu/projects/worktrees/guide-link/systems
- Regenerate: `uv run --frozen python scripts/summarize_systems.py`

**Checks (legend)**

- **D37 C_n**: plateau of ⟨R²(n)⟩/(n l²) for n ≥ 100 carbons on the 500 K hold, compared with the melt C∞ at 500 K (PE 6.7, iPP 6.15, ±10%), and a drift test (second minus first half of the hold beyond 2 combined SEM).
- **D47**: end-to-end vector ACF < 1/e (0.368) **and** chain COM MSD ≥ 2⟨Rg²⟩, both at a lag of half the combined 500 K hold (prep hold + extension).
- **Rule**: a system that passes D47 is accepted even if its C_n misses the literature value; that miss is a model property, not a failure, and no more compute is spent on it. The C_n value vs literature and its drift (taken over prep hold + extension, so it includes the unrelaxed prep) are shown as "info".
- Long CG chains (C ≥ 1000, i.e. C1500): whole-chain relaxation is out of reach, so D47 does not apply (D47); they rely on correct construction and the C_n no-drift check.
- Pores and AA boxes converted from UA (ua2aa) inherit the equilibration of the bulk box they were built from.
- Run status comes from `sepsim progress` ("cancelled/killed?" = log silent > 6 h without a finished manifest; ETAs converted to UTC). Superseded systems and run directories (renamed old/cancelled runs, rebuilt sources) are listed separately and never used for the numbers.
- **"drift seg …"** (monitor flag): those segments show a significant trend in a thermo quantity over their analysis window. It is informational.

**Convergence figures:** [overview](convergence_overview.png), [`pe_cg_amorph_n40_c240_s1`](convergence/pe_cg_amorph_n40_c240_s1.png), [`pe_cg_amorph_n40_c1500_s1`](convergence/pe_cg_amorph_n40_c1500_s1.png), [`pe_cg_amorph_n320_c240_s1_rep222`](convergence/pe_cg_amorph_n320_c240_s1_rep222.png), [`pe_cg_pore500k_w10nm_n40_c240_s1`](convergence/pe_cg_pore500k_w10nm_n40_c240_s1.png), [`pe_cg_pore_w5nm_n40_c240_s1`](convergence/pe_cg_pore_w5nm_n40_c240_s1.png), [`pe_cg_pore500k_w10nm_n320_c240_s1_rep222`](convergence/pe_cg_pore500k_w10nm_n320_c240_s1_rep222.png), [`pe_cg_pore_w5nm_n320_c240_s1_rep222`](convergence/pe_cg_pore_w5nm_n320_c240_s1_rep222.png), [`pe_ua_amorph_n40_c240_s1`](convergence/pe_ua_amorph_n40_c240_s1.png), [`pe_aa_amorph_n40_c240_s1_from_ua`](convergence/pe_aa_amorph_n40_c240_s1_from_ua.png), [`ipp_ua_amorph_n40_c240_s1`](convergence/ipp_ua_amorph_n40_c240_s1.png), [`ipp_aa_amorph_n40_c240_s1_from_ua`](convergence/ipp_aa_amorph_n40_c240_s1_from_ua.png)

## Overview

| System | Res | Polymer | Kind | Chains × length | Sites | Stage now | Status | Equilibration (D47) | C_n plateau (D37) | Analysis |
|---|---|---|---|---|---|---|---|---|---|---|
| `pe_cg_amorph_n40_c240_s1` | CG | PE | bulk | 40 × C240 | 3,200 beads | done | finished: prep, extend, cool, sweep | D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | sweep |
| `pe_cg_amorph_n40_c1500_s1` | CG | PE | bulk | 40 × C1500 | 20,000 beads | done | finished: prep, extend, cool, sweep | D47 n/a (long CG chain); ACF 0.68 at 250.0 ns, MSD/⟨Rg²⟩ 0.12; 500.0 ns at 500 K; no C_n drift: accepted | 7.43 vs 6.7 (outside band, info); no drift (Δ +0.21 ± 0.30) | sweep |
| `pe_cg_amorph_n320_c240_s1_rep222` | CG | PE | bulk (derived) | 320 × C240 | 25,600 beads | done | finished: extend (stopped after D47 PASS) | D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨Rg²⟩ 2.65; 72.5 ns at 500 K; accepted (C_n drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_pore500k_w10nm_n40_c240_s1` | CG | PE | pore (wide, 10 nm) | 40 × C240 | 3,200 beads | done | finished: pore_relax | from pe_cg_amorph_n40_c240_s1: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | no |
| `pe_cg_pore_w5nm_n40_c240_s1` | CG | PE | pore (narrow, 5 nm) | 40 × C240 | 3,200 beads | done | finished: pore | from pe_cg_pore500k_w10nm_n40_c240_s1 ← pe_cg_amorph_n40_c240_s1: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted | 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40) | no |
| `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` | CG | PE | pore (wide, 10 nm) | 320 × C240 | 25,600 beads | done | finished: pore_relax | from pe_cg_amorph_n320_c240_s1_rep222: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨Rg²⟩ 2.65; 72.5 ns at 500 K; accepted (C_n drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | CG | PE | pore (narrow, 5 nm) | 320 × C240 | 25,600 beads | done | finished: pore | from pe_cg_pore500k_w10nm_n320_c240_s1_rep222 ← pe_cg_amorph_n320_c240_s1_rep222: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨Rg²⟩ 2.65; 72.5 ns at 500 K; accepted (C_n drift over prep + extension, informational) | 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10) | no |
| `pe_ua_amorph_n40_c240_s1` | UA | PE | bulk | 40 × C240 | 9,600 | sweep | running, 1.2% (0/18 segments, seg 01 hold 25 C); ETA 2026-11-07 17:04 UTC | D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨Rg²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | no |
| `pe_aa_amorph_n40_c240_s1_from_ua` | AA | PE | bulk (derived) | 40 × C240 | 28,880 | prep | running, 2.8% (4/14 segments, Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2)); ETA 2026-11-02 06:10 UTC | from pe_ua_amorph_n40_c240_s1: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨Rg²⟩ 2.28; 98.2 ns at 500 K; accepted | 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53) | no |
| `ipp_ua_amorph_n40_c240_s1` | UA | iPP | bulk | 40 × C240 | 12,760 | sweep | running, 41.0% (8/18 segments, seg 09 hold 90 C); ETA 2026-11-03 11:47 UTC | D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨Rg²⟩ 2.06; 60.0 ns at 500 K; accepted (C_n drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | no |
| `ipp_aa_amorph_n40_c240_s1_from_ua` | AA | iPP | bulk (derived) | 40 × C240 | 28,880 | sweep | not started (prep done) | from ipp_ua_amorph_n40_c240_s1: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨Rg²⟩ 2.06; 60.0 ns at 500 K; accepted (C_n drift over prep + extension, informational) | 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25) | no |

## Pending and known items

- `pe_cg_pore_w5nm_n40_c240_s1`: pore analysis not run
- `pe_cg_pore_w5nm_n320_c240_s1_rep222`: pore analysis not run
- `pe_ua_amorph_n40_c240_s1`: sweep: running, 1.2% (0/18 segments, seg 01 hold 25 C); ETA 2026-11-07 17:04 UTC
- `pe_aa_amorph_n40_c240_s1_from_ua`: prep: running, 2.8% (4/14 segments, Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2)); ETA 2026-11-02 06:10 UTC; sweep not started
- `ipp_ua_amorph_n40_c240_s1`: sweep: running, 41.0% (8/18 segments, seg 09 hold 90 C); ETA 2026-11-03 11:47 UTC
- `ipp_aa_amorph_n40_c240_s1_from_ua`: sweep not started

## Superseded (kept, not used)

- System `pe_cg_pore_w10nm_n40_c240_s1`: built from an earlier pe_cg_pore500k_w10nm_n40_c240_s1 (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)
- System `pe_cg_pore_w3nm_n40_c240_s1`: built from an earlier pe_cg_pore500k_w10nm_n40_c240_s1 (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)
- System `pe_aa_amorph_n40_c240_s1`: superseded by pe_aa_amorph_n40_c240_s1_from_ua (D47: AA is built from the relaxed UA box)
- Runs of `pe_cg_amorph_n40_c240_s1`: prep_server_cancelled (cancelled/killed?), prep_timeout12h (cancelled/killed?), sweep_old_20ns_box (finished)
- Runs of `pe_cg_amorph_n40_c1500_s1`: sweep_cancelled_unrelaxed (cancelled/killed?)
- Runs of `pe_cg_amorph_n320_c240_s1_rep222`: extend_cpu_job92_cancelled_48ns (cancelled/killed?)
- Runs of `pe_cg_pore500k_w10nm_n40_c240_s1`: pore_relax_old_20ns_box (finished)
- Runs of `pe_cg_pore_w5nm_n40_c240_s1`: pore_old_20ns_box_cancelled (cancelled/killed?)
- Runs of `pe_ua_amorph_n40_c240_s1`: sweep_old_unrelaxed_cancelled (cancelled/killed?)
- Runs of `ipp_ua_amorph_n40_c240_s1`: prep_server_cancelled (cancelled/killed?)
- Runs of `ipp_aa_amorph_n40_c240_s1_from_ua`: sweep_cancelled_pe_first (stalled?)

## Measured properties (bulk sweeps, holds)

### `pe_cg_amorph_n40_c240_s1` sweep (CG PE C240, 80.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-10-27 22:41 UTC on rdyu-server, run finished.

| T (°C) | ρ (g/cm³) | κ_T (GPa⁻¹) | Rg (Å) | R_ee (Å) | C_n | P2 1/e (ps) | COM MSD max (Å²) (lag) | D_COM (cm²/s) | traj |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.83453 ± 0.00003 | 1.000 ± 0.015 | 31.24 ± 0.12 | 77.1 ± 0.5 | 10.27 ± 0.08 | 123 | 176.9 (12.5 ns) | not diffusive (slope 0.90) | yes |
| 90 | 0.79783 ± 0.00004 | 1.292 ± 0.022 | 32.21 ± 0.21 | 84.2 ± 1.0 | 11.78 ± 0.19 | 25.5 | 396 (12.5 ns) | 5.12e-07 ± 2.2e-10 | yes |
| 130 | 0.77580 ± 0.00005 | 1.502 ± 0.027 | 30.84 ± 0.34 | 77.6 ± 2.1 | 10.58 ± 0.36 | 12.7 | 522.8 (12.5 ns) | not diffusive (slope 0.90) | yes |
| 160 | 0.75938 ± 0.00006 | 1.662 ± 0.031 | 30.80 ± 0.39 | 78.3 ± 1.4 | 10.70 ± 0.34 | 7.61 | 572.5 (12.5 ns) | not diffusive (slope 0.99) | yes |

| Fit window (°C) | α_V (10⁻⁴ K⁻¹) | χ²_red α | Cp classical (J g⁻¹ K⁻¹) | χ²_red Cp | points |
|---|---|---|---|---|---|
| 25–160 | 6.919 ± 0.034 | 49.7 | 0.828 ± 0.002 | 24 | 15 |
| 90–160 | 7.032 ± 0.040 | 9.99 | 0.817 ± 0.003 | 6.04 | 8 |
| 25–90 | 6.917 ± 0.022 | 5.05 | 0.840 ± 0.004 | 15.6 | 8 |

- Note: Cp is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k_B/2 per quadratic term; CG also drops degrees of freedom (all motion inside a 3-CH2 bead), so its Cp per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: D37 chain check FAIL on the prep hold + extension: C_n plateau 9.11 vs melt 6.7 ±10%.
- Note: α_V and Cp are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²_red, and a large χ²_red over 25–160 °C means α_V or Cp depends on T (compare the two half windows).
- Note: CG time is not real time: SDK beads move faster than the atoms they represent, so MSD, D_COM and P2 times are model times (not rescaled).

### `pe_cg_amorph_n40_c1500_s1` sweep (CG PE C1500, 500.0 ns at 500 K)

`sepsim analyze sweep`, generated 2026-10-26 20:41 UTC on rdyu-rog, run finished.

| T (°C) | ρ (g/cm³) | κ_T (GPa⁻¹) | Rg (Å) | R_ee (Å) | C_n | P2 1/e (ps) | COM MSD max (Å²) (lag) | D_COM (cm²/s) | traj |
|---|---|---|---|---|---|---|---|---|---|
| 25 | 0.83817 ± 0.00001 | 0.995 ± 0.015 | 67.79 ± 0.11 | 175.1 ± 1.4 | 7.91 ± 0.02 | 128 | 21.94 (12.5 ns) | not diffusive (slope 0.42) | yes |
| 90 | 0.80154 ± 0.00002 | 1.265 ± 0.022 | 70.28 ± 0.13 | 179.3 ± 1.0 | 8.46 ± 0.03 | 26.9 | 29.7 (12.5 ns) | not diffusive (slope 0.69) | yes |
| 130 | 0.78019 ± 0.00002 | 1.435 ± 0.026 | 70.04 ± 0.16 | 185.2 ± 1.6 | 8.44 ± 0.03 | 14.3 | 37.17 (12.5 ns) | not diffusive (slope 0.48) | yes |
| 160 | 0.76444 ± 0.00002 | 1.572 ± 0.029 | 68.89 ± 0.25 | 169.2 ± 1.9 | 8.06 ± 0.07 | 8.78 | 44.85 (12.5 ns) | not diffusive (slope 0.50) | yes |

| Fit window (°C) | α_V (10⁻⁴ K⁻¹) | χ²_red α | Cp classical (J g⁻¹ K⁻¹) | χ²_red Cp | points |
|---|---|---|---|---|---|
| 25–160 | 6.783 ± 0.017 | 76.8 | 0.815 ± 0.004 | 306 | 15 |
| 90–160 | 6.757 ± 0.027 | 29.5 | 0.793 ± 0.001 | 10.1 | 8 |
| 25–90 | 6.866 ± 0.013 | 12 | 0.838 ± 0.003 | 39.7 | 8 |

- Note: Cp is the classical dH/dT and is not comparable to experiment: classical MD gives every degree of freedom k_B/2 per quadratic term; CG also drops degrees of freedom (all motion inside a 3-CH2 bead), so its Cp per gram is not a property of the real polymer at all (reported for completeness and resolution comparisons only).
- Note: Chains may not be relaxed: the D47 criteria fail on the prep hold + extension (extend/progress.json: end-to-end ACF 0.68 at 250.0 ns, needs < 1/e; COM MSD/<Rg²> 0.12, needs >= 2).
- Note: D37 chain check FAIL on the prep hold + extension: C_n plateau 7.43 vs melt 6.7 ±10%.
- Note: α_V and Cp are linear fits in T over each window with SEM weights; a reduced χ² > 1 (curvature over the window, or SEMs too small) inflates the quoted errors by √χ²_red, and a large χ²_red over 25–160 °C means α_V or Cp depends on T (compare the two half windows).
- Note: CG time is not real time: SDK beads move faster than the atoms they represent, so MSD, D_COM and P2 times are model times (not rescaled).

Not analyzed yet: `pe_cg_amorph_n320_c240_s1_rep222`, `pe_ua_amorph_n40_c240_s1`, `pe_aa_amorph_n40_c240_s1_from_ua`, `ipp_ua_amorph_n40_c240_s1`, `ipp_aa_amorph_n40_c240_s1_from_ua`.

## Pores (stage 2)

| System | Kind | Gap (nominal) | Gap at 500 K | Wall thickness | Lateral box | γ per hold (mN/m, monitor) | Status | Analysis |
|---|---|---|---|---|---|---|---|---|
| `pe_cg_pore500k_w10nm_n40_c240_s1` | wide | 10 nm (at 500 K) | — | 6.7 nm (500 K) | 6.7 × 6.7 nm (500 K) | — | finished: pore_relax | no |
| `pe_cg_pore_w5nm_n40_c240_s1` | narrow | 5 nm (at 25 °C) | 4.68 nm | 6.5 nm | 6.4 × 6.4 nm (25 °C) | 25 °C 34.4 ± 0.4; 90 °C 31.1 ± 0.3; 130 °C 29.5 ± 0.3; 160 °C 27.8 ± 0.3 | finished: pore | no |
| `pe_cg_pore500k_w10nm_n320_c240_s1_rep222` | wide | 10 nm (at 500 K) | — | 13.5 nm (500 K) | 13.5 × 13.5 nm (500 K) | — | finished: pore_relax | no |
| `pe_cg_pore_w5nm_n320_c240_s1_rep222` | narrow | 5 nm (at 25 °C) | 4.37 nm | 12.9 nm | 12.9 × 12.9 nm (25 °C) | 25 °C 34.6 ± 0.3; 90 °C 30.5 ± 0.2; 130 °C 28.3 ± 0.2; 160 °C 28.2 ± 0.2 | finished: pore | no |

γ here is the `sepsim progress` second-half mean ± SEM of each hold segment (γ = (Lz/2)[Pzz − (Pxx+Pyy)/2]); the pore analysis, when present, follows.

## Per-system details

### `pe_cg_amorph_n40_c240_s1`

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field sdk_cg, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted
- C_n plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-21 20:13 UTC, ended 2026-10-22 01:07 UTC; reads `systems/pe_cg_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R_ee ACF 0.31 at 10.0 ns, 1/e at 8.84 ns; COM MSD/⟨Rg²⟩ 0.90); C_n 9.02 vs 6.7 (outside band, info); no drift (Δ +0.65 ± 0.49)
  - monitor flags: R_ee 1/e 8.84 ns; MSD/Rg2 0.90; drift seg 6,10,12,13
- **extend** (rdyu-rog): finished; started 2026-10-26 17:57 UTC, ended 2026-10-26 23:45 UTC; reads `../prep/hold.data`
  - 500 K hold 80.0 ns: D47 PASS (R_ee ACF 0.14 at 40.0 ns, 1/e at 11.12 ns; COM MSD/⟨Rg²⟩ 2.56); C_n 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)
- **cool** (rdyu-rog): finished; started 2026-10-26 23:47 UTC, ended 2026-10-27 03:51 UTC; reads `../extend/hold_ext_60ns.data`
  - monitor flags: drift seg 4,5,6,8; hyst max 0.11%
- **sweep** (rdyu-rog): finished; started 2026-10-27 03:52 UTC, ended 2026-10-27 22:32 UTC; reads `../cool/cooled.data`
  - monitor flags: drift seg 2,8,14; step!=hold 130 C; hyst max 0.11%
- Superseded (not used): prep_server_cancelled (cancelled/killed?); prep_timeout12h (cancelled/killed?); sweep_old_20ns_box (finished)

### `pe_cg_amorph_n40_c1500_s1`

**Provenance**

- PE CG, 40 chains × C1500 (C1500H3002), 20,000 atoms/beads, force field sdk_cg, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 n/a (long CG chain); ACF 0.68 at 250.0 ns, MSD/⟨Rg²⟩ 0.12; 500.0 ns at 500 K; no C_n drift: accepted
- C_n plateau (D37): 7.43 vs 6.7 (outside band, info); no drift (Δ +0.21 ± 0.30)

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-24 08:10 UTC, ended 2026-10-24 13:16 UTC; reads `systems/pe_cg_amorph_n40_c1500_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R_ee ACF 0.86 at 10.0 ns, 1/e not reached; COM MSD/⟨Rg²⟩ 0.03); C_n 5.58 vs 6.7 (outside band, info); drift (Δ +0.37 ± 0.09)
  - monitor flags: R_ee not decorrelated (0.86 at 10.0 ns); MSD/Rg2 0.03; drift seg 5,10,11,12
- **extend** (rdyu-rog): finished; started 2026-10-24 13:18 UTC, ended 2026-10-26 02:01 UTC; reads `../prep/hold.data`
  - 500 K hold 500.0 ns: D47 FAIL (R_ee ACF 0.68 at 250.0 ns, 1/e not reached; COM MSD/⟨Rg²⟩ 0.12); C_n 7.43 vs 6.7 (outside band, info); no drift (Δ +0.21 ± 0.30)
  - monitor flags: drift seg 1
- **cool** (rdyu-rog): finished; started 2026-10-26 02:02 UTC, ended 2026-10-26 05:01 UTC; reads `../extend/hold_ext_500ns.data`
  - monitor flags: drift seg 3,6,7,8; hyst max 0.11%
- **sweep** (rdyu-rog): finished; started 2026-10-26 05:01 UTC, ended 2026-10-26 17:56 UTC; reads `../cool/cooled.data`
  - monitor flags: drift seg 1,2,3,6,9,14; step!=hold 130 C; hyst max 0.11%
- Superseded (not used): sweep_cancelled_unrelaxed (cancelled/killed?)

### `pe_cg_amorph_n320_c240_s1_rep222`

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field sdk_cg, box density 0.7302 g/cm³ (as built)
- Replicated 2×2×2 from pe_cg_amorph_n40_c240_s1
- Built from: pe_cg_amorph_n40_c240_s1 (`extend/hold_ext_60ns.data`)

**Equilibration**

- Verdict: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨Rg²⟩ 2.65; 72.5 ns at 500 K; accepted (C_n drift over prep + extension, informational)
- C_n plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **extend** (rdyu-rog): stopped after D47 PASS (cancelled/killed?), 90.7%; started 2026-10-29 11:25 UTC; reads `systems/pe_cg_amorph_n320_c240_s1_rep222/data.lmp`
  - 500 K hold 72.5 ns: D47 PASS (R_ee ACF 0.09 at 36.3 ns, 1/e at 10.88 ns; COM MSD/⟨Rg²⟩ 2.65); C_n 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)
- Superseded (not used): extend_cpu_job92_cancelled_48ns (cancelled/killed?)

### `pe_cg_pore500k_w10nm_n40_c240_s1`

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field sdk_cg, box density 0.2941 g/cm³ (as built)
- Pore: wide pore, nominal 10 nm, wall 6.74 nm, clear gap 4.24 nm, area 45.4 nm²
- Built from: pe_cg_amorph_n40_c240_s1 (`extend/hold_ext_60ns.data`)

**Equilibration**

- Verdict: from pe_cg_amorph_n40_c240_s1: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted
- C_n plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **pore_relax** (rdyu-server): finished; started 2026-10-26 23:51 UTC, ended 2026-10-27 00:18 UTC; reads `systems/pe_cg_pore500k_w10nm_n40_c240_s1/data.lmp`
- Superseded (not used): pore_relax_old_20ns_box (finished)

### `pe_cg_pore_w10nm_n40_c240_s1` (superseded)

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field sdk_cg, box density 0.2964 g/cm³ (as built)
- Pore: narrow pore, nominal 10 nm, 9.69 nm at 500 K, wall 6.41 nm, clear gap 8.59 nm, area 46.0 nm²
- Built from: pe_cg_pore500k_w10nm_n40_c240_s1 (`pore_relax/relaxed.data`) ← pe_cg_amorph_n40_c240_s1 (`prep/hold.data`)
- **Stale source:** built from an earlier pe_cg_pore500k_w10nm_n40_c240_s1 (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)

**Equilibration**

- Verdict: from pe_cg_pore500k_w10nm_n40_c240_s1 ← pe_cg_amorph_n40_c240_s1: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted
- C_n plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **pore** (rdyu-rog): cancelled/killed?, 5.6%; started 2026-10-26 16:59 UTC; reads `systems/pe_cg_pore_w10nm_n40_c240_s1/data.lmp`

### `pe_cg_pore_w5nm_n40_c240_s1`

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field sdk_cg, box density 0.4286 g/cm³ (as built)
- Pore: narrow pore, nominal 5 nm, 4.68 nm at 500 K, wall 6.49 nm, clear gap 3.50 nm, area 45.4 nm²
- Built from: pe_cg_pore500k_w10nm_n40_c240_s1 (`pore_relax/relaxed.data`) ← pe_cg_amorph_n40_c240_s1 (`extend/hold_ext_60ns.data`)

**Equilibration**

- Verdict: from pe_cg_pore500k_w10nm_n40_c240_s1 ← pe_cg_amorph_n40_c240_s1: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted
- C_n plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **pore** (rdyu-rog): finished; started 2026-10-27 22:41 UTC, ended 2026-10-28 20:10 UTC; reads `systems/pe_cg_pore_w5nm_n40_c240_s1/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 34.4 ± 0.4; 90 °C 31.1 ± 0.3; 130 °C 29.5 ± 0.3; 160 °C 27.8 ± 0.3
- Superseded (not used): pore_old_20ns_box_cancelled (cancelled/killed?)

### `pe_cg_pore_w3nm_n40_c240_s1` (superseded)

**Provenance**

- PE CG, 40 chains × C240 (C240H482), 3,200 atoms/beads, force field sdk_cg, box density 0.5168 g/cm³ (as built)
- Pore: narrow pore, nominal 3 nm, 2.69 nm at 500 K, wall 6.41 nm, clear gap 1.59 nm, area 46.0 nm²
- Built from: pe_cg_pore500k_w10nm_n40_c240_s1 (`pore_relax/relaxed.data`) ← pe_cg_amorph_n40_c240_s1 (`prep/hold.data`)
- **Stale source:** built from an earlier pe_cg_pore500k_w10nm_n40_c240_s1 (its manifest changed since: rebuilt source; data `pore_relax/relaxed.data`)

**Equilibration**

- Verdict: from pe_cg_pore500k_w10nm_n40_c240_s1 ← pe_cg_amorph_n40_c240_s1: D47 PASS; ACF 0.14 at 40.0 ns, MSD/⟨Rg²⟩ 2.56; 80.0 ns at 500 K; accepted
- C_n plateau (D37): 9.11 vs 6.7 (outside band, info); no drift (Δ -0.62 ± 0.40)

**Stages**

- **pore** (rdyu-server): cancelled/killed?, 7.1%; started 2026-10-26 16:36 UTC; reads `systems/pe_cg_pore_w3nm_n40_c240_s1/data.lmp`

### `pe_cg_pore500k_w10nm_n320_c240_s1_rep222`

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field sdk_cg, box density 0.4176 g/cm³ (as built)
- Replicated 2×2×2 from pe_cg_amorph_n40_c240_s1
- Pore: wide pore, nominal 10 nm, wall 13.50 nm, clear gap 1.93 nm, area 182.3 nm²
- Built from: pe_cg_amorph_n320_c240_s1_rep222 (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from pe_cg_amorph_n320_c240_s1_rep222: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨Rg²⟩ 2.65; 72.5 ns at 500 K; accepted (C_n drift over prep + extension, informational)
- C_n plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **pore_relax** (rdyu-rog): finished; started 2026-10-29 17:38 UTC, ended 2026-10-29 18:02 UTC; reads `systems/pe_cg_pore500k_w10nm_n320_c240_s1_rep222/data.lmp`

### `pe_cg_pore_w5nm_n320_c240_s1_rep222`

**Provenance**

- PE CG, 320 chains × C240 (C240H482), 25,600 atoms/beads, force field sdk_cg, box density 0.5473 g/cm³ (as built)
- Replicated 2×2×2 from pe_cg_amorph_n40_c240_s1
- Pore: narrow pore, nominal 5 nm, 4.37 nm at 500 K, wall 12.94 nm, clear gap 1.70 nm, area 182.3 nm²
- Built from: pe_cg_pore500k_w10nm_n320_c240_s1_rep222 (`pore_relax/relaxed.data`) ← pe_cg_amorph_n320_c240_s1_rep222 (`extend/hold_ext_70ns.data`)

**Equilibration**

- Verdict: from pe_cg_pore500k_w10nm_n320_c240_s1_rep222 ← pe_cg_amorph_n320_c240_s1_rep222: D47 PASS; ACF 0.09 at 36.3 ns, MSD/⟨Rg²⟩ 2.65; 72.5 ns at 500 K; accepted (C_n drift over prep + extension, informational)
- C_n plateau (D37): 9.18 vs 6.7 (outside band, info); drift (Δ +0.47 ± 0.10)

**Stages**

- **pore** (rdyu-rog): finished; started 2026-10-29 18:08 UTC, ended 2026-10-30 12:05 UTC; reads `systems/pe_cg_pore_w5nm_n320_c240_s1_rep222/data.lmp`
  - γ per hold (monitor, second half of each segment, mN/m): 25 °C 34.6 ± 0.3; 90 °C 30.5 ± 0.2; 130 °C 28.3 ± 0.2; 160 °C 28.2 ± 0.2

### `pe_ua_amorph_n40_c240_s1`

**Provenance**

- PE UA, 40 chains × C240 (C240H482), 9,600 atoms/beads, force field trappe_ua, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨Rg²⟩ 2.28; 98.2 ns at 500 K; accepted
- C_n plateau (D37): 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)

**Stages**

- **prep** (rdyu-server): finished; started 2026-10-20 23:57 UTC, ended 2026-10-23 17:30 UTC; reads `systems/pe_ua_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R_ee ACF 0.47 at 10.0 ns, 1/e not reached; COM MSD/⟨Rg²⟩ 0.63); C_n 7.31 vs 6.7 (in band, info); drift (Δ +1.59 ± 0.37)
  - monitor flags: R_ee not decorrelated (0.47 at 10.0 ns); MSD/Rg2 0.63; drift seg 13
- **extend** (rdyu-server): stopped after D47 PASS (cancelled/killed?), 97.7%; started 2026-10-23 19:05 UTC; reads `../prep/hold.data`
  - 500 K hold 98.2 ns: D47 PASS (R_ee ACF 0.16 at 49.1 ns, 1/e at 19.27 ns; COM MSD/⟨Rg²⟩ 2.28); C_n 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)
- **cool** (rdyu-server): finished; started 2026-10-29 11:30 UTC, ended 2026-10-30 15:50 UTC; reads `../extend/hold_ext_70ns.data`
  - monitor flags: drift seg 3,4,7
- **sweep** (rdyu-server): running, 1.2% (0/18 segments, seg 01 hold 25 C); ETA 2026-11-07 17:04 UTC; started 2026-10-30 15:50 UTC; reads `../cool/cooled.data`
- Superseded (not used): sweep_old_unrelaxed_cancelled (cancelled/killed?)

### `pe_aa_amorph_n40_c240_s1` (superseded)

**Provenance**

- PE AA, 40 chains × C240 (C240H482), 28,880 atoms/beads, force field opls2020_aa, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)
- **Superseded** by pe_aa_amorph_n40_c240_s1_from_ua (D47: AA is built from the relaxed UA box)

**Equilibration**

- Verdict: D47 FAIL (prep hold only); ACF 0.72 at 2.5 ns, MSD/⟨Rg²⟩ 0.16; 5.0 ns at 500 K; not accepted
- C_n plateau (D37): 6.09 vs 6.7 (in band, info); drift (Δ +1.01 ± 0.22)

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-21 19:36 UTC, ended 2026-10-24 08:09 UTC; reads `systems/pe_aa_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 5.0 ns: D47 criteria on this hold FAIL (R_ee ACF 0.72 at 2.5 ns, 1/e not reached; COM MSD/⟨Rg²⟩ 0.16); C_n 6.09 vs 6.7 (in band, info); drift (Δ +1.01 ± 0.22)
  - monitor flags: R_ee not decorrelated (0.72 at 2.5 ns); MSD/Rg2 0.16

### `pe_aa_amorph_n40_c240_s1_from_ua`

**Provenance**

- PE AA, 40 chains × C240 (C240H482), 28,880 atoms/beads, force field opls2020_aa, box density 0.7452 g/cm³ (as built)
- Built: ua2aa (D32): carbons at UA positions; H placed geometrically
- Built from: pe_ua_amorph_n40_c240_s1 (`hold_ext_70ns.data`)

**Equilibration**

- Verdict: from pe_ua_amorph_n40_c240_s1: D47 PASS; ACF 0.16 at 49.1 ns, MSD/⟨Rg²⟩ 2.28; 98.2 ns at 500 K; accepted
- C_n plateau (D37): 8.19 vs 6.7 (outside band, info); no drift (Δ +0.79 ± 0.53)

**Stages**

- **prep** (rdyu-rog): running, 2.8% (4/14 segments, Stage 5: NPT compression at 500 K: 100 atm, then 1 atm (run 2/2)); ETA 2026-11-02 06:10 UTC; started 2026-10-30 16:16 UTC; reads `systems/pe_aa_amorph_n40_c240_s1_from_ua/data.lmp`

### `ipp_ua_amorph_n40_c240_s1`

**Provenance**

- iPP UA, 40 chains × C240 (C240H482), 12,760 atoms/beads, force field trappe_ua, box density 0.3000 g/cm³ (as built)
- Built: grown chains (seed 1, build density 0.3 g/cm³)

**Equilibration**

- Verdict: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨Rg²⟩ 2.06; 60.0 ns at 500 K; accepted (C_n drift over prep + extension, informational)
- C_n plateau (D37): 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)

**Stages**

- **prep** (rdyu-rog): cancelled/killed?, 60.8%; started 2026-10-21 20:13 UTC; reads `systems/ipp_ua_amorph_n40_c240_s1/data.lmp`
  - 500 K hold 20.0 ns: D47 criteria on this hold FAIL (R_ee ACF 0.45 at 10.0 ns, 1/e not reached; COM MSD/⟨Rg²⟩ 1.05); C_n 4.77 vs 6.15 (outside band, info); no drift (Δ +0.20 ± 0.38)
  - monitor flags: R_ee not decorrelated (0.45 at 10.0 ns); MSD/Rg2 1.05; drift seg 6
- **extend** (rdyu-rog): stopped after D47 PASS (cancelled/killed?), 50.0%; started 2026-10-23 19:05 UTC; reads `../prep/hold.data`
  - 500 K hold 60.0 ns: D47 PASS (R_ee ACF 0.19 at 30.0 ns, 1/e at 14.68 ns; COM MSD/⟨Rg²⟩ 2.06); C_n 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)
- **cool** (rdyu-rog): finished; started 2026-10-26 18:02 UTC, ended 2026-10-28 07:16 UTC; reads `../extend/hold_ext_40ns.data`
  - monitor flags: drift seg 4; hyst max 0.67%
- **sweep** (rdyu-rog): running, 41.0% (8/18 segments, seg 09 hold 90 C); ETA 2026-11-03 11:47 UTC; started 2026-10-28 07:16 UTC; reads `../cool/cooled.data`
  - monitor flags: drift seg 1,5,8; hyst max 0.67%
- Superseded (not used): prep_server_cancelled (cancelled/killed?)

### `ipp_aa_amorph_n40_c240_s1_from_ua`

**Provenance**

- iPP AA, 40 chains × C240 (C240H482), 28,880 atoms/beads, force field opls2020_aa, box density 0.7588 g/cm³ (as built)
- Built: ua2aa (D32): carbons at UA positions; H placed geometrically
- Built from: ipp_ua_amorph_n40_c240_s1 (`hold_ext_40ns.data`)

**Equilibration**

- Verdict: from ipp_ua_amorph_n40_c240_s1: D47 PASS; ACF 0.19 at 30.0 ns, MSD/⟨Rg²⟩ 2.06; 60.0 ns at 500 K; accepted (C_n drift over prep + extension, informational)
- C_n plateau (D37): 5.66 vs 6.15 (in band, info); drift (Δ +1.41 ± 0.25)
- Own prep hold (5.0 ns, information): C_n 5.58 vs 6.15 (in band, info); no drift (Δ -0.01 ± 0.16); R_ee ACF 0.72 at 2.5 ns; COM MSD/⟨Rg²⟩ 0.25

**Stages**

- **prep** (rdyu-rog): finished; started 2026-10-26 18:04 UTC, ended 2026-10-29 11:25 UTC; reads `systems/ipp_aa_amorph_n40_c240_s1_from_ua/data.lmp`
  - 500 K hold 5.0 ns: D47 criteria on this hold FAIL (R_ee ACF 0.72 at 2.5 ns, 1/e not reached; COM MSD/⟨Rg²⟩ 0.25); C_n 5.58 vs 6.15 (in band, info); no drift (Δ -0.01 ± 0.16)
  - monitor flags: R_ee not decorrelated (0.72 at 2.5 ns); MSD/Rg2 0.25; drift seg 9,12
- Superseded (not used): sweep_cancelled_pe_first (stalled?)


## Property guide: what each calculated quantity means

Reference values are approximate textbook values for amorphous or molten PE, to give a sense of scale. They have not been checked against a specific source. All boxes stay amorphous at every temperature. Real separator PE is semicrystalline below about 130 °C, so 25–130 °C here describes the amorphous phase only. CG and UA times are model times: CG dynamics in particular run several times faster than real PE, so only their trends with temperature are meaningful.

### Comparability with experiment

A fair comparison needs amorphous or melt data at the same temperature and a similar chain length (our chains are C240, about 3.4 kg/mol, and C1500, about 21 kg/mol).

| Property | Comparable to experiment? | Compare against, and caveats |
|---|---|---|
| Density ρ(T), thermal expansion α_V | **Yes**, all resolutions | Melt data above Tm. Below Tm, the amorphous density extrapolated from the melt, not a semicrystalline sample. Accuracy is a property of the force field (SDK CG was fitted to density). |
| Compressibility κ_T (bulk modulus 1/κ_T) | **Yes** | Melt PVT data at 1 atm. CG models usually come out too compressible. |
| Surface tension γ, dγ/dT | **Yes** | Melt γ vs T at a similar molecular weight. SDK CG was partly fitted to γ. Our value depends on the cutoff (no tail correction at surfaces, D48), which tends to bias it low. |
| Chain size Rg, R_ee, C_n | **Yes** | Neutron-scattering melt data (PE C∞ ≈ 6.7–7.4). CG and UA come out high, which is a force-field result. |
| Heat capacity Cp | **AA only, after the quantum correction** (VDOS, D12c) | CG and UA remove degrees of freedom (H atoms, motions inside a bead), so their Cp is far too low. Classical MD gives every vibration k_B T, while real high-frequency C–H modes are mostly frozen, so classical AA Cp is too high until corrected. |
| Dynamics: D, viscosity, P2 times, MSD | **AA roughly; UA partly; CG only with a time-mapping factor** | CG runs several times faster than real PE (smoothed energy landscape). UA is also somewhat fast (no hydrogen friction). Temperature trends are meaningful; absolute CG times need scaling to one experimental or AA point. |
| Young's modulus, Poisson ratio, yield (tensile) | **Not against separator data** | Real separator stiffness and yield come from crystals, and MD strain rates (10⁸–10⁹ s⁻¹) are about 10⁹× faster than tests. Only the amorphous-phase response and its trends with temperature and rate. |
| Pores: surface structure, hole closure | **No direct experiment** | The mechanism, and comparisons within our own simulations. |

**Our numbers next to experiment, with sources:** `docs/experiment_comparison.md`. In short, CG PE density is about 2% low, α_V about 5% low, surface tension within 1–3%, κ_T 50–60% too high, Cp about 3× low (degrees of freedom), chains about 20% too large (C240), and dynamics about 4× too fast.

**Comparisons that hold at every resolution are the ones within our own simulations:** temperature trends from 25 to 160 °C, PE vs iPP at the same resolution, CG vs UA vs AA on the same property, and small vs 2×2×2 boxes. Most of the separator conclusions rest on these, not on absolute agreement with experiment.

### Thermodynamic properties

1. **Density ρ(T).** Mean density of each NPT segment. Steps use their second half; holds drop their first 10%. The error is the SEM from the statistical inefficiency (D26). Amorphous PE is about 0.85 g/cm³ extrapolated to 25 °C and about 0.77–0.78 g/cm³ as a melt near 150–160 °C.

2. **Thermal expansion α_V.** α_V = (1/V) dV/dT, from SEM-weighted straight-line fits of volume against T over 25–160, 25–90 and 90–160 °C.
   - Errors are scaled by √χ²_red when χ²_red > 1, so curvature shows up as a large χ²_red and a larger error.
   - Expansion speeds up slightly with temperature, which is why the 25–160 °C fit is poor and the narrower windows are given.
   - Amorphous or molten PE is about 7–8 × 10⁻⁴ K⁻¹.

3. **Isothermal compressibility κ_T.** κ_T = (⟨V²⟩ − ⟨V⟩²)/(k_B T ⟨V⟩), from the volume fluctuations of each NPT hold. The bulk modulus is K = 1/κ_T. PE melt is roughly 1 GPa⁻¹ near 150 °C; CG models usually come out somewhat too compressible.

4. **Heat capacity Cp.** Cp = dH/dT per gram, fitted like α_V. It is classical. UA and CG remove degrees of freedom (hydrogens, atoms inside beads), so their Cp is far below real PE (about 2.3–2.6 J g⁻¹ K⁻¹ for the melt) and is not comparable to experiment. Only AA, with the quantum correction from the vibrational spectrum (VDOS, D12c), gives a meaningful Cp.

### Chain size and shape

5. **Rg and R_ee.** Radius of gyration (mass-weighted, all atoms of a chain) and end-to-end distance, averaged over every hold frame. In a melt they barely depend on temperature.

6. **C_n (characteristic ratio).** C_n = ⟨R_n²⟩/(n l²) for stretches of n backbone C–C bonds of length l = 1.54 Å.
   - It measures chain stiffness: 1 for a freely jointed chain, and higher with fixed bond angles and a preference for trans.
   - It levels off at C∞, about 6.7 for PE and 6.15 for iPP melts. We report the plateau for n ≥ 100 carbons (D37).
   - A higher C_n means stiffer, more extended chains: ⟨R²⟩ = C∞ n l².
   - Under the project rule, a C_n that misses the literature value in an equilibrated box is a property of the model, not a failure.

### Dynamics

7. **Bond reorientation time (P2 1/e).** ⟨P2(u(0)·u(t))⟩ of the backbone bond vectors, with the time at which it falls to 1/e. It measures how fast local segments reorient, which is set by local packing, not chain length. It speeds up strongly with temperature.

8. **Segment MSD, chain centre-of-mass MSD and D_COM.**
   - Mean-square displacement of backbone sites and of whole chains, combining the dense 0.1 ps bursts and the 10 ps hold frames (D46).
   - D_COM = slope/6 when the MSD is diffusive, meaning a log-slope of at least 0.9 over at least a factor of 2 in lag. Otherwise it is "not diffusive" and the largest slope is reported.
   - In a 12.5 ns hold the chains move less than their own size, so true chain diffusion would need much longer runs.

8b. **Long-hold D_COM (`diffuse`, D53).** The same D_COM criterion on a dedicated 300 ns NPT hold at one sweep temperature (CG), checked by `sepsim progress` while it runs. Only once the MSD is diffusive (and well beyond ⟨Rg²⟩) is D_COM a chain self-diffusion coefficient. The Rouse estimate η_R = ρ_N k_B T ⟨R_ee²⟩/(36 D), with ρ_N the chain number density, converts it into a melt viscosity; it assumes unentangled chains, so for entangled ones it is a lower bound. For a PE melt of this chain length expect roughly 0.1 Pa·s (order of magnitude only); CG dynamics are faster, so CG viscosities come out lower.

### Mechanical properties (`tensile`, `sepsim analyze tensile`, D54)

8c. **Stress–strain curve.** The box is stretched along one axis at a constant engineering strain rate (10⁸ or 10⁹ s⁻¹) while the other two axes are held at 1 atm; this is repeated along x, y and z from the same starting snapshot. True stress σ = −(P_axis − 1 atm), tension positive; engineering stress is σ times the current over the initial cross-section.

8d. **Apparent modulus E_app.** Slope of σ against strain up to `--fit-max` (default 0.02). For an amorphous melt above Tg this is a high-frequency, rate-dependent response, not an equilibrium modulus; it falls as the rate falls. Bulk semicrystalline PE is of order 1 GPa because of its crystallinity, which these boxes do not have; an amorphous PE melt has no equilibrium modulus at all.

8e. **Poisson ratio ν.** ν = −d ln L_lateral / d ln L_axis. A melt that flows at constant volume gives 0.5; glassy polymers about 0.33–0.4. At MD rates the lateral barostat lags the pull, which biases ν low at small strain.

8f. **Peak and flow stress.** The maximum of the smoothed σ (with its strain), and the mean σ over strains 0.3–0.5. In a melt there is no true yield: the plateau is a viscous flow stress, about 3η × strain rate for a simple liquid, so it scales with the rate.

### Equilibration and quality checks

9. **D47 (chain mixing at 500 K).**
   - The criterion: the end-to-end vector ACF is below 1/e and the chain COM MSD is at least 2⟨Rg²⟩, at a lag of half the combined 500 K hold.
   - Very long chains such as C1500 cannot reach it in affordable time. They are accepted on a stable C_n plateau.

10. **Drift flags and hysteresis.** "drift seg …" marks segments whose thermo shows a significant trend over the analysis window; it is informational. Hysteresis is the largest density difference between the cooling and heating branches at the same T.

### Pores (stage 2, `sepsim analyze pore`, D51)

11. **Surface tension γ.** γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] (two interfaces), per segment. It uses a plain LJ cutoff with no tail correction (D48), so γ depends on the cutoff.

12. **Density profile ρ(z).** Profile across the film: whether the interior matches bulk density, film thickness from the Gibbs dividing surfaces, interfacial width, actual gap width against the nominal 5 nm, and the closest approach of atoms across the gap.

13. **Near-surface behaviour.** Segment mobility (in-plane and normal), bond reorientation, bond orientation relative to the surface and chain shape, near the surface against the interior and bulk.

14. **Finite-size check (D50).** The 40-chain and 2×2×2 (320-chain) pores are compared on the quantities above.

**Caveat.** The slit models a local patch of pore wall. Real separator pores are 30–100 nm across, curved and semicrystalline.
