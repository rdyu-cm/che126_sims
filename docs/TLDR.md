# TLDR: resume here

**Project:** LAMMPS MD of Li-ion (EV) separator polymers, PE and isotactic PP, from 25 to 160 °C. Three resolutions:
- all-atom (OPLS/2020)
- united-atom (TraPPE-UA)
- coarse-grained (SDK/SPICA, PE only)

The repo holds the build and analysis code, templates, and force-field parameters. Production runs on a separate workstation with a budget under 500 GPU-h.

**Status (2026-10-26):** design is done; every decision is in [`decisions.md`](decisions.md). Phase 2 is merged; phase 3 is in progress; stage 2 dry pores follow D48 (made at 500 K, then narrowed; NVT with the bulk lateral area) with one 5 nm dry width and a CG finite-size check (D50).

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
1. D47: the UA chains are not relaxed after the 20 ns prep hold. Extend PE UA and iPP UA at 500 K (`extend`) until end-to-end ACF < 1/e and COM MSD ≥ 2⟨Rg²⟩ (expected ~60–80 ns more), then `cool` the latest snapshot, rerun the sweeps, build AA from the relaxed UA box (`ua2aa`) and the pores from it.
2. D37 chain check after each prep; decide the CG criterion (CG C240 plateau ≈ 8.3, stable, vs melt 6.7). C1500 relies on correct construction + the no-distortion check (D47).
3. CG density-vs-T check (D15) from the CG C240 sweep, then the T1 analyses (`sepsim analyze sweep`, D49; run it where the hold DCDs are).
4. Dry pores (D48, D50: one dry width, 5 nm): CG C240 first (its bulk sweep is done): `pore_relax` on `systems/pe_cg_pore500k_w10nm_n40_c240_s1`, narrow to 5 nm, `pore` on CPU (commands below). CG finite-size check (D50): the same 5 nm pore from a 2×2×2 replicated bulk (320 chains), decorrelated by a 500 K `extend` first; compare γ, the density profile and surface vs interior mobility. UA/AA: one 5 nm pore each, sized from that check; UA after D47 passes and the UA sweeps are rerun (wide pore from the extension snapshot), AA later on the GPU after the AA preps.
5. Phase 4 needs a decision on whether to build crystals (D40) and, if so, the crystal-slab geometry.

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
uv run sepsim render prep  --system $S --job --node rdyu-server --cpus 12 --time 3-00:00:00
~/projects/slurm-setup/bin/ssubmit ~/projects/che126_sims jobs/pe_ua_amorph_n40_c240_s1/prep/job.sh
uv run sepsim render sweep --system $S --job --node rdyu-server --cpus 12 --time 7-00:00:00
~/projects/slurm-setup/bin/ssubmit ~/projects/che126_sims jobs/pe_ua_amorph_n40_c240_s1/sweep/job.sh --dependency=afterok:<prep job id>
~/projects/slurm-setup/bin/scollect ~/projects/che126_sims   # copy results/ and logs/ back
```
- Dry pores (D48), in four steps: (1) open a wide pore in the 500 K bulk box, (2) relax it at 500 K with the box fixed (`pore_relax`), (3) narrow the relaxed state to each width (nominal at 25 °C; the bulk densities for the per-T lateral box are read from the bulk runs under `results/runs/<bulk id>/`, so build where those logs are, after `scollect`), (4) run `pore` (500 K re-relaxation, the prep's step-cool, the sweep; NVT, Lz fixed, x/y by `change_box` at each T). The pore decks read the system's `data.lmp`, so they run on either node:
  ```
  B=pe_cg_amorph_n40_c240_s1; W=pe_cg_pore500k_w10nm_n40_c240_s1
  uv run sepsim build pore --data results/runs/$B/prep/hold.data --source systems/$B --width-nm 10   # --replicate-z 2 for a thick wall; UA: --data .../extend/hold_ext_<N>ns.data
  uv run sepsim render pore_relax --system systems/$W --job --node rdyu-rog --cpus 6 --time 1-00:00:00
  uv run sepsim build pore --data results/runs/$W/pore_relax/relaxed.data --source systems/$W --width-nm 5   # D50: 5 nm only; UA: --bulk-hold .../extend --bulk-cool .../cool --bulk-sweep .../sweep_d47
  uv run sepsim render pore --system systems/pe_cg_pore_w5nm_n40_c240_s1 --job --node rdyu-rog --cpus 6 --time 7-00:00:00
  ```
- CG finite-size check (D50): replicate the 500 K bulk box 2×2×2 (`sepsim build replicate`, id `..._n320_..._rep222`; molecules whole across the seams, velocities kept), decorrelate the correlated copies with a 500 K `extend` (no prep: give the system's own `data.lmp`), then the pore chain above from its latest snapshot. Narrowing reads the densities of the **small** bulk's runs by default (`results/runs/pe_cg_amorph_n40_c240_s1/{prep,sweep}`; the lateral rule is intensive):
  ```
  uv run sepsim build replicate --data results/runs/$B/prep/hold.data --source systems/$B --n 2 2 2
  R=pe_cg_amorph_n320_c240_s1_rep222
  uv run sepsim render extend --system systems/$R --data systems/$R/data.lmp --job --node rdyu-rog --cpus 6 --time 7-00:00:00
  uv run sepsim build pore --data results/runs/$R/extend/hold_ext_<N>ns.data --source systems/$R --width-nm 10
  ```
- Extended 500 K hold (D47), then re-cool and sweep from it. `extend` reads `../prep/hold.data` and writes `hold_ext.dcd` plus a snapshot `hold_ext_<ns>ns.data` every `chunk_ps` (default 10 ns of `extend_ps` = 80 ns). Watch `sepsim progress` on the extend run (it rechecks prep hold + extension at most every 2 h and prints `D47 PASS/FAIL`); once it passes, `scancel` the job and cool the latest snapshot. Relative `--data` paths of these stages are relative to the run directory, as below (move the old `sweep/` away first, or use `--out .../sweep_d47`):
  ```
  uv run sepsim render extend --system $S --job --node rdyu-server --cpus 4 --time 7-00:00:00   # --set extend_ps=80000 --set chunk_ps=10000
  uv run sepsim render cool   --system $S --data ../extend/hold_ext_60ns.data --job --node rdyu-server --cpus 4 --time 2-00:00:00
  uv run sepsim render sweep  --system $S --data ../cool/cooled.data --job --node rdyu-server --cpus 4 --time 7-00:00:00
  ```
- Chain diffusion (D53) and tensile tests (D54) per sweep temperature, from the sweep's `hold_<T>C.data` (on the node that has it; the CG C240 sweep ran on rdyu-rog and was collected to rdyu-server). Stage directories default to `diffuse_<T>C`, `tensile_<T>C` and `tensile_<T>C_r<rate>` (from `--set t_c=`/`rate_per_s=`). `sepsim progress` flags D_COM on a diffuse run; `sepsim analyze tensile` gives E_app, ν, peak and flow stress:
  ```
  S=systems/pe_cg_amorph_n40_c240_s1
  uv run sepsim render diffuse --system $S --data ../sweep/hold_90C.data --set t_c=90 --job --node rdyu-server --cpus 2 --time 3-00:00:00   # CG 300 ns, hold.dcd + hold_<ns>ns.data every 25 ns
  uv run sepsim render tensile --system $S --data ../sweep/hold_90C.data --set t_c=90 --job --node rdyu-rog --cpus 2 --time 1-00:00:00     # x, y, z to strain 0.5 at 1e8 /s
  uv run sepsim render tensile --system $S --data ../sweep/hold_90C.data --set t_c=90 --set rate_per_s=1e9 --job --node rdyu-rog --cpus 2 --time 06:00:00
  uv run sepsim analyze tensile results/runs/pe_cg_amorph_n40_c240_s1/tensile_90C [more run dirs] [--fit-max 0.02]
  ```
- Sweep and pore holds write a dense 10 ps burst at 0.1 ps every 1 ns into `segNN_hold_XXC_burstKK.dcd` (D46); `--set burst_period_ps=0` turns them off.
- Inputs made by an earlier stage (sweep reads `../prep/cooled.data`, benchmark `../prep/compressed.data`, extend `../prep/hold.data`) exist only on the node that ran it, so pin a system's stages to one node (`--node`). Rendering before that file exists only warns; the job checks for it.
- Render, then `ssubmit` (not plain `sbatch`), so the deck reaches the other node. Re-render and resubmit after changes.
- Use `--partition gpu --accel kokkos --cpus 2` on the GPU (the GPU package aborts at device init, D43) and OpenMP threads on CPU (4–8 threads; scaling flattens beyond, D43).
- `--accel omp|mpi|gpu|kokkos` (default omp on `cpu`, gpu on `gpu`), `--ranks N` for MPI ranks (`mpirun` inside the image, no `srun --mpi=pmix`), `--partition gpu` adds `--gres=gpu:1`, `apptainer exec --rocm` and `HSA_OVERRIDE_GFX_VERSION=10.3.0`. The image is `$SEPSIM_SIF` (default `~/projects/installations/lammps/stable_22Jul2025_update6/lammps-rocm6.4.4-gfx1030.sif`). Benchmark variants need their own run directory, e.g. `--out results/runs/<system>/benchmark_gpu`, and `--set ensemble=nve --set dt_fs=1` for the D38 dt check.

## Monitoring runs (D45)
`sepsim progress` writes `progress.md`, `progress.json` and `progress_*.png` into each run directory: status (stalled/killed detection), segments done, ns/day, ETA, per-segment means, the prep-hold chain checks (D37 C_n, end-to-end ACF, COM MSD/⟨Rg²⟩; for an extend run on prep hold + extension with the D47 verdict), cooling-vs-heating hysteresis and sweep step-vs-hold flags. A chunked hold (D46 bursts, D47 chunks) is one segment.
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

**Convergence figures (all checks on 1–2 pages):** `uv run --frozen python scripts/convergence_dashboard.py` writes `results/convergence_overview.png` (every current system × every check: D47, C_n, stage status, sweep drift, hysteresis, hold precision, pore γ drift, chain-scale relaxation) and `results/convergence/<system>.png` (500 K chain checks, cool/sweep/pore thermo with analysis windows, block averages and drift flags, SEM vs block size; pore film panels once `sepsim analyze pore` has run); `scripts/summarize_systems.py` links them from `results/summary.md` when present. The overview also has κ_T halves, α_V/Cp fit χ²_red, hold dynamics (D_COM diffusive, P2 1/e) and diffuse/tensile/hole columns; each dashboard adds κ_T running/block/halves, α_V/Cp fit residuals, MSD/log-slope/P2 per hold, chain-scale relaxation and Rg/R_ee/C_n vs T.

**Physical validity (can a property be compared with experiment, per system):** `scripts/validity.py` holds the rules (single source of truth); the same script run writes `results/validity_overview.png`, and `results/summary.md` has the matrix with per-system reasons ("Physical validity by system").

**Viewing trajectories (OVITO in the browser):** `scripts/viewer.sh` on rdyu-server starts Jupyter Lab (localhost only) on `scripts/view.ipynb`; from the laptop `ssh -N -L 8888:localhost:8888 rdyu-server` and open the printed URL. Or open `scripts/view.ipynb` in VS Code (Remote-SSH; the notebook's default kernel is `ovito-viewer`, registered once with the line in `viewer.sh`; Remote Settings `"python.venvFolders": ["projects/installations"]` lets VS Code find the environment; setting `"jupyter.widgetScriptSources": ["jsdelivr.com", "unpkg.com"]`). Paste a DCD path (VS Code *Copy Path*, or `rdyu-rog:<path>`) into `v.load_path(...)`; the notebook (`scripts/ovito_view.py`) loads the system's `data.lmp` plus that DCD and draws it with `STYLE` (top of `ovito_view.py`: wrap into the box, color by chain or `"z"` for pores, hydrogens hidden, radii, bond width, camera) in a rotatable viewport with a frame slider. `node="rdyu-rog"` copies that DCD into `results/viewer/rdyu-rog/` first (delete the copies when done). It runs in its own environment, `../installations/ovito-viewer` (ovito 3.17.0, ipywidgets, jupyterlab; setup line in `viewer.sh`), not the project's.

## Analysing a sweep (D49)
`sepsim analyze sweep` reads a finished bulk sweep run directory (deck, log, hold and burst DCDs) and writes `results.md`, `results.json` and PNGs into `results/analysis/<system>/<stage>/`: per-segment T/density/enthalpy (mean ± SEM; steps second half, holds minus their first 10%), κ_T from the hold volume fluctuations, α_V and classical Cp fits (25–160, 25–90, 90–160 °C), and per hold the backbone-site and chain COM MSD (bursts + hold DCD), D_COM if diffusive, bond P2 1/e time, Rg, R_ee and the C_n plateau. Holds whose DCD is not on this node are reported as "trajectory not available"; pore runs go to `sepsim analyze pore`.
```
uv run sepsim analyze sweep results/runs/pe_cg_amorph_n40_c240_s1/sweep               # --no-traj: thermo only; --max-frames N (C_n frames, default 500); --out DIR
```

## Analysing a pore (D51)
`sepsim analyze pore` does the same for a finished dry-pore run (`in.pore`) into `results/analysis/<system>/pore/`. Per segment (500 K re-relaxation, step-cool, sweep): Lx, Ly, Pxx, Pyy, Pzz and γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] with dγ/dT fits. Per hold: ρ(z) about the film centre, interior plateau vs bulk density, Gibbs and 50% film thickness, gap width, 10–90/tanh interfacial widths, clear gap; surface layer (15 Å from each Gibbs surface) vs interior in-plane/normal MSD, bond P2 1/e, ⟨P2(cos θ_z)⟩ vs z, Rg_z² vs Rg_xy²/2; the whole-film `analyze sweep` dynamics next to the bulk hold. Over the sweep grid: film thickness and interior density vs T, α_z and the film α_V vs bulk α_V, classical Cv, surface excess energy e_s vs γ − T dγ/dT. The bulk reference comes from the pore manifest (`results/analysis/<bulk>/sweep/results.json`, so run `analyze sweep` on the bulk first; `--bulk-analysis` overrides), bulk energies from the bulk sweep run directory.

Both commands also check equilibration (D51). `equilibration.png` shows thermo vs time over all segments, with the analysis windows shaded and block averages ± SEM. `equilibration_holds.png` shows per-hold zooms and SEM vs block length; pores add `film_vs_time.png`. A `drift` column flags windows whose halves differ by > 2 SEM (sweep: density, enthalpy; pore: γ, PE, film thickness). The results.md "Equilibration" section separates local quantities from chain-scale ones (chain COM MSD vs ⟨Rg²⟩ per hold). `results.json` holds the `convergence` records that the cross-run dashboards are drawn from.
```
uv run sepsim analyze pore results/runs/pe_cg_pore_w5nm_n40_c240_s1/pore             # --no-traj; --max-frames N (profile frames, default 500); --out DIR; --bulk-analysis PATH
```

## Chain relaxation and analysing a hold (D56)
Both analyses now report, per hold (pores: whole film), the end-to-end vector and Rouse mode (p = 1–5) relaxation times (1/e, or "not reached" with an extrapolated exponential fit; τ_1 ≈ p²τ_p from the reached modes), p²⟨X_p²⟩, `relaxation.png`, block series of Rg²/R_ee²/C_n for the dashboard, and a crystallinity monitor (D26 alignment, fixed p2 ≥ 0.4: uncalibrated, a melt baseline). `sepsim analyze hold` does the same for an `extend` (500 K; `../prep/hold.dcd` read ahead of `hold_ext.dcd`) or `diffuse` run, plus the hold thermo, κ_T and D_COM (D55 criterion); run it where the hold DCD is:
```
uv run sepsim analyze hold results/runs/pe_ua_amorph_n40_c240_s1/extend              # --max-frames N; --out DIR; --systems DIR
```

**Snapshots for showing the pores (PNG/movie, headless):** `scripts/render_snapshots.py`, run with the OVITO environment's Python; topology from the DCD path like the viewer, look from `ovito_view.STYLE`; pores default to a side view along x (z across the image, the films as walls left and right of the gap), all colored by chain (CG drawn as beads on bonds); pores are shifted so the gap sits in the middle of the cell (`--no-center` to skip) and drawn with periodic images (`--images NX NY NZ`; pore defaults 1 3 3 for side views, 2 2 2 for perspective; the cell outlined in black, images in grey); `--highlight N` colors N random whole chains and greys out the rest (file suffix `_hl<N>`). Bulk defaults to a perspective view. Output in the gitignored `results/figures/<system>/<stage>/`. Views `side`, `side_zup`, `front`, `top`, `perspective`; `--frames last|first,last|0,50,last|N` (N evenly spaced); `--movie mp4|gif|png` (OVITO's built-in encoder, ~1.5 s per 1600×1000 frame on 2 threads). Renders take ~0.5–2 s per image on 2 CPU threads (`--threads`, default 2).
```
~/projects/installations/ovito-viewer/bin/python scripts/render_snapshots.py \
    results/runs/pe_cg_pore_w5nm_n40_c240_s1/pore/relax.dcd --frames first,last --views side,perspective --highlight 8
```
OVITO 3.17 (pip) needs a Vulkan driver for every renderer (Tachyon too). rdyu-server has none, so a user-space Mesa lavapipe (software Vulkan) copy lives in `../installations/vulkan-lavapipe` (extracted from the Ubuntu `mesa-vulkan-drivers` package, no root; see its README.txt); the script uses it automatically. `sudo apt install mesa-vulkan-drivers` would make it unnecessary.

## Run sidecars and data manifest
In git: `results/run_sidecars/<system>/<stage>/` holds each run's small files (`in.*` deck, `run_manifest.json`, `progress.json`/`progress.md`, `lmp_info.txt`, and the Slurm `job/job.sh` + deck from `jobs/`), for every run on both nodes including superseded/cancelled stages (bench/smoke skipped); `index.tsv` lists which node ran each and whether the job deck matches the run's deck. Two different runs under one name (e.g. the server's abandoned `pe_cg_amorph_n40_c1500_s1/prep` vs rdyu-rog's real one) are kept apart: the latest is the main copy, the other goes to `other_run_<node>/`. `results/data_manifest.tsv` lists node, path, bytes, sha256, mtime and kind of the large outputs that stay on the nodes (`*.dcd`, `*.data` snapshots, `log.lammps`, `screen.out`; restarts are not listed). Trajectories, snapshots and thermo logs are **not** in git yet (archive location undecided); files of a run still running are snapshots, so rerun after it ends. Regenerate (stdlib only; `--skip-existing` rehashes only changed files):
```
scp scripts/collect_sidecars.py rdyu-rog:/tmp/ && ssh rdyu-rog 'cd ~/projects/che126_sims && nice -n 15 ionice -c3 \
    ~/.local/bin/uv run --frozen python /tmp/collect_sidecars.py --runs rdyu-rog=results/runs \
    --node-label rdyu-rog --no-sidecars --manifest /tmp/data_manifest_rog.tsv' && scp rdyu-rog:/tmp/data_manifest_rog.tsv /tmp/
rsync -a --prune-empty-dirs --include='*/' --include='in.*' --include='run_manifest.json' --include='progress.json' \
    --include='progress.md' --include='lmp_info.txt' --exclude='*' rdyu-rog:projects/che126_sims/results/runs/ /tmp/rog_runs/
nice -n 15 ionice -c3 uv run --frozen python scripts/collect_sidecars.py --runs rdyu-server=results/runs \
    --runs rdyu-rog=/tmp/rog_runs --node-label rdyu-server --skip-existing --merge /tmp/data_manifest_rog.tsv
```
(Without `--runs` it reads `results/runs` and the `results/progress/rdyu-rog/` copy, which lacks `lmp_info.txt`.) Delete stale `results/run_sidecars/` first if runs were renamed.

## Decisions at a glance
**Systems**
- Chains: 40 × C240 at every level (PE C240H482 / iPP 80-mer), ~29k atoms in all-atom.
- UA length series: C120 and C480.
- Long-chain coarse-grained PE: C1500 (C3000 in tier 3).

**Morphologies**
- Amorphous bulk.
- ~~Crystal slab with free surfaces for Tm~~: dropped (D40).
- Slit pores (slab + gap in a 3D-periodic box; D44/D48: wall = one equilibrated 500 K bulk box, gap opened along z, plain LJ cutoff without tail correction, AA 14 Å):
  - dry: one width, 5 nm, at every resolution (D50: walls further apart than the 1.4–1.5 nm cutoff do not interact, so dry widths barely differ); width varies only for wet pores (D48: cut wide from the 500 K box, relaxed there, then narrowed; w defined at 25 °C)
  - CG C240 finite-size check (D50): 40 chains vs a 2×2×2 replicated box (320 chains, film and lateral size ×2): γ, density profile, surface vs interior mobility
  - caveat: our walls are amorphous; real separator pore walls are semicrystalline (phase 4)
  - wall ablation: amorphous vs crystal-core + amorphous skin

**Electrolyte**
- 1 M LiPF6 in EC/DMC, all-atom only, ion charges ×0.8, NPT at 20 bar.
- Dry pores run NVT with z fixed and x, y following the bulk thermal expansion (D48; no barostat). Wet pores are NPT aniso (x, y, z) at 20 bar.

**Protocol**
- Prep: soft-core push-off (AA/UA only; D34) → minimize → NVT 500 K → NPT 500 K (100 atm, then 1 atm; D35) → 500 K hold (AA 5 / UA 20 / CG 20 ns) → step-cool to 298 K (D36). Chain equilibration checked by ⟨R²(n)⟩/n (D37). UA: hold extended until end-to-end ACF < 1/e and COM MSD ≥ 2⟨Rg²⟩, then re-cooled (D47).
- One NPT sweep trajectory per system: 14 steps of ~10 °C (AA 1 / UA 2 / CG 5 ns) plus holds at 25, 90, 130, and 160 °C (AA 5 / UA 10 / CG 25 ns) (D36). Holds add a 10 ps burst at 0.1 ps every 1 ns (D46).
- Dry pores (D48): wide pore relaxed NVT at 500 K (AA 1 / UA 2 / CG 5 ns), narrowed, then minimize, 500 K re-relaxation (AA 0.5 / UA 1 / CG 2 ns), the prep's step-cool and the same sweep, all NVT with L_xy(T) from the bulk density; γ from the pressure tensor.
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
