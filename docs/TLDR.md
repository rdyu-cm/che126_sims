# TLDR: resume here

**Project:** LAMMPS MD of Li-ion (EV) separator polymers, PE and isotactic PP, from 25 to 160 °C. Three resolutions:
- all-atom (OPLS/2020)
- united-atom (TraPPE-UA)
- coarse-grained (SDK/SPICA, PE only)

The repo holds the build and analysis code, templates, and force-field parameters. Production runs on a separate workstation with a budget under 500 GPU-h.

**Status (2026-10-20):** design is done; every decision is in [`decisions.md`](decisions.md). Phase 2 is merged; phase 3 is in progress.

**Done and merged into `main`:**
- phase 0: uv package skeleton
- phase 1: force-field YAMLs with verified sources
- the `sepsim run` reproducibility wrapper
- the analysis library: core, plus D26 definitions
- crystal data for iPP α₂ (Hikosaka & Seto 1973 Table Ia) and PE
- phase 2: amorphous builders at all three resolutions, T1 systems in `systems/`, LAMMPS image fixes (D29–D33; commit `0507798`)

- phase 3: render engine and templates (`_ff`, `prep`, `sweep`, `benchmark`) per D34–D39, chain check `sepsim.analysis.chain` (D37), Slurm run layout (D41) (commit `9054074`)

**In progress:** T1 production (D43). Large systems (AA PE, AA iPP from the relaxed UA box, CG C1500) queue on the rdyu-rog GPU with KOKKOS; small ones on CPU: iPP UA (rdyu-rog, 8 threads), CG C240 (rdyu-rog, 6), PE UA (rdyu-server, 4). Each sweep is chained to its prep (`--dependency=afterok`).

**Scope change (D40):** melting is dropped. No crystal-slab Tm ramps and no CG crystallization cycles (~60 GPU-h freed). Crystallinity is still monitored during sweeps. Whether phase 4 builds crystals at all is decided at phase 4.

**Next steps:**
1. D37 chain check after each prep; decide the CG criterion (CG C240 plateau ≈ 8.3, stable, vs melt 6.7).
2. CG density-vs-T check (D15) from the CG C240 sweep, then the T1 analyses.
3. Phase 4 needs a decision on whether to build crystals (D40) and, if so, the crystal-slab geometry.

**Rules:**
- Every new design choice goes to the user, with a plain-language recommendation, before it's built.
- Work on feature branches in worktrees under `../worktrees/` (i.e. `projects/worktrees/`), never on `main` directly.
- Runs go through Slurm (D41): submit from rdyu-server with `ssubmit`, fetch outputs with `scollect`; outputs land in the gitignored `results/runs/<system>/<stage>/`, job logs in `logs/`.
- Pushing feature branches is fine. Merges to `main` need user approval (squash merge).
- Never send the user's email to outside services.
- The copyrighted PDF lives in the gitignored `references/` and is never committed. Re-download it on the new machine if needed (Hikosaka & Seto, Polym. J. 1973, 5, 111).

**Setup on any machine:**
```
uv sync && uv run pytest -q
```
No conda. LAMMPS (and packmol, for the T2 electrolyte) are installed only on the machines that build or run systems.

## Running on the cluster
From the project root on rdyu-server (`ssubmit` syncs the project to rdyu-rog except the contents of `results/` and `logs/`). `--job` writes the deck and `job.sh` to `jobs/<system>/<stage>/`, which is synced; the job copies the deck into `results/runs/<system>/<stage>/`, runs it there with `uv run sepsim run` (writes `run_manifest.json`) and logs to `logs/%x-%j-%N.out`.
```
mkdir -p logs results                                  # once: Slurm needs logs/ on every node
S=systems/pe_ua_amorph_n40_c240_s1
uv run sepsim render prep  --system $S --job --node rdyu-server --cpus 12 --mem 8G --time 3-00:00:00
~/projects/slurm-setup/bin/ssubmit ~/projects/che126_sims jobs/pe_ua_amorph_n40_c240_s1/prep/job.sh
uv run sepsim render sweep --system $S --job --node rdyu-server --cpus 12 --mem 8G --time 7-00:00:00
~/projects/slurm-setup/bin/ssubmit ~/projects/che126_sims jobs/pe_ua_amorph_n40_c240_s1/sweep/job.sh --dependency=afterok:<prep job id>
~/projects/slurm-setup/bin/scollect ~/projects/che126_sims   # copy results/ and logs/ back
```
- Inputs made by an earlier stage (sweep reads `../prep/cooled.data`, benchmark `../prep/compressed.data`) exist only on the node that ran it, so pin a system's stages to one node (`--node`). Rendering before that file exists only warns; the job checks for it.
- Render, then `ssubmit` (not plain `sbatch`), so the deck reaches the other node. Re-render and resubmit after changes.
- Use `--partition gpu --accel kokkos --cpus 2` on the GPU (the GPU package aborts at device init, D43) and OpenMP threads on CPU (4–8 threads; scaling flattens beyond, D43).
- `--accel omp|mpi|gpu|kokkos` (default omp on `cpu`, gpu on `gpu`), `--ranks N` for MPI ranks (`mpirun` inside the image, no `srun --mpi=pmix`), `--partition gpu` adds `--gres=gpu:1`, `apptainer exec --rocm` and `HSA_OVERRIDE_GFX_VERSION=10.3.0`. The image is `$SEPSIM_SIF` (default `~/projects/installations/lammps/stable_22Jul2025_update6/lammps-rocm6.4.4-gfx1030.sif`). Benchmark variants need their own run directory, e.g. `--out results/runs/<system>/benchmark_gpu`, and `--set ensemble=nve --set dt_fs=1` for the D38 dt check.

## Monitoring runs (D45)
`sepsim progress` writes `progress.md`, `progress.json` and `progress_*.png` into each run directory: status (stalled/killed detection), segments done, ns/day, ETA, per-segment means, the prep-hold chain checks (D37 C_n, end-to-end ACF, COM MSD/⟨Rg²⟩), cooling-vs-heating hysteresis and sweep step-vs-hold flags.
```
uv run sepsim progress results/runs/pe_ua_amorph_n40_c240_s1/prep    # one run (--out DIR to write elsewhere)
uv run sepsim progress --all --summary results/progress.md            # every run on this node + one table
scripts/progress_update.sh                                            # one two-node pass -> results/progress.md
```
For updates every 10 min, add this line on rdyu-server with `crontab -e` (not installed by the repo):
```
*/10 * * * * /home/rdyu/projects/che126_sims/scripts/progress_update.sh
```
Each pass refreshes this node's runs, runs `sepsim progress --all` on rdyu-rog over ssh, pulls only its progress files into `results/progress/rdyu-rog/`, and writes `results/progress.md`. It holds a lock (an overlapping pass skips), times out each step after 300 s (a down node cannot hang it) and logs to `logs/progress_update.log`. rdyu-rog needs the `progress` code (synced by `ssubmit`).

## Decisions at a glance
**Systems**
- Chains: 40 × C240 at every level (PE C240H482 / iPP 80-mer), ~29k atoms in all-atom.
- UA length series: C120 and C480.
- Long-chain coarse-grained PE: C1500 (C3000 in tier 3).

**Morphologies**
- Amorphous bulk.
- ~~Crystal slab with free surfaces for Tm~~: dropped (D40).
- Slit pores (slab + gap in a 3D-periodic box):
  - widths 3/5/10 nm at AA/UA
  - 20–50 nm dry pore at CG
  - wall ablation: amorphous vs crystal-core + amorphous skin

**Electrolyte**
- 1 M LiPF6 in EC/DMC, all-atom only, ion charges ×0.8, NPT at 20 bar.
- Dry systems run at 1 atm; dry slabs are barostatted in x and y only, with z fixed. Wet pores are NPT aniso (x, y, z) at 20 bar.

**Protocol**
- Prep: soft-core push-off (AA/UA only; D34) → minimize → NVT 500 K → NPT 500 K (100 atm, then 1 atm; D35) → 500 K hold (AA 5 / UA 20 / CG 20 ns) → step-cool to 298 K (D36). Chain equilibration checked by ⟨R²(n)⟩/n (D37).
- One NPT sweep trajectory per system: 14 steps of ~10 °C (AA 1 / UA 2 / CG 5 ns) plus holds at 25, 90, 130, and 160 °C (AA 5 / UA 10 / CG 25 ns) (D36).
- Thermal conductivity κ: rNEMD branch runs. Whether to use 4 or 2 temperatures is decided after the benchmark.
- Cp: dH/dT plus a VDOS quantum correction (all-atom).
- Timesteps: AA 1 fs flexible / UA 2 fs (flexible backbone, SHAKE only on the explicit methine C–H; fallback 1 fs) / CG 10 fs.
- LAMMPS runs from the command line; the optional `sepsim run` writes a reproducibility manifest. Nosé–Hoover thermostat; NVE for κ and VDOS.
- 1 replica per system.
- **Tg is out of scope:** both polymers have Tg below 25 °C.
- Coarse-grained: standard SDK PE, with an early density-vs-T check against UA and experiment.

**Budget**
- Tiers T1 → T2 → T3; T1 + T2 ≈ 375 GPU-h (≈405 before melting was dropped). This rests on a guessed throughput, and the step-0 benchmark recalibrates it.

**Tooling**
- Python-native builder (no moltemplate); packmol only for the electrolyte.
- Python package plus a `sepsim` CLI and Jinja LAMMPS templates.
