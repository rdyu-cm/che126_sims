# Hold analysis: pe_cg_amorph_n40_c240_s1 / extend

- system: `pe_cg_amorph_n40_c240_s1` (cg); source run directory `/home/rdyu/projects/che126_sims/results/runs/pe_cg_amorph_n40_c240_s1/extend` (extend, status finished, node rdyu-rog, run code commit cb4513655e)
- analysis: `sepsim analyze hold` (D56), code commit 05d80a64df (dirty), 2026-10-30 19:25 on rdyu-server
- segment: Stage 1: NPT hold extension 60000 ps at 500 K, 1 atm (60 ns planned, complete); thermo window without the first 10% of rows, SEM from 100 ps block means (D55)
- note: ../prep/hold.dcd not found: chain checks use the extension alone

## Thermo

| window (ns) | T (°C) | density (g/cm³) | H (kcal/mol) | V (Å³) | κ_T (GPa⁻¹) |
|---|---|---|---|---|---|
| 54.00 | 226.84 ± 0.03 | 0.72370 ± 0.00007 | 492.6 ± 3.6 | 309173 ± 31 | 2.146 ± 0.025 |

## Trajectory: mobility and chain size

- trajectory not available (hold_ext.dcd not found)

## Chain relaxation (holds; D56)

No trajectory results.

## Caveats

- CG time is not real time: SDK beads move ≈ 4.07× faster than real PE, so MSD, D_COM and relaxation times are model times (docs/experiment_comparison.md).
- No trajectory results: hold_ext.dcd is not in this run directory (a run on another node may keep its DCD there) or could not be read.
