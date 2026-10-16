# Design plan & decision register: PE/PP separator MD (LAMMPS, AA/UA/CG)

> **New chat? Start here.**
> - **Phase:** implementation. Phases 0 and 1 are done; the `sepsim run` wrapper and the core analysis library are also done (built in parallel).
> - **Rule from the user:** every design decision goes through the user. Ask, record, then build. Any new design choice that comes up during implementation is a checkpoint for the user too.
> - **Next action:** finish or restart phase 2 (see TLDR). Then ask the analysis-definition questions; the user was mid-clarification.
> - **Docs:** `docs/TLDR.md` is the short resume. This file is the full register, facts, and caveats. Keep both current.
> - **Last updated:** 2026-10-16 (phase 1 force fields done: OPLS/2020 replaces the L-OPLS hybrid; UA explicit methine H; flexible UA backbone; LAMMPS via CLI + manifest).

## Context
We want to characterize the separator polymers in EV Li-ion cells, starting with PE and isotactic PP, from 25 to 160 °C using LAMMPS MD at three resolutions:
- all-atom (OPLS/2020)
- united-atom (TraPPE-UA)
- coarse-grained (SDK/SPICA)

The properties are anything MD gives directly: density, thermal expansion (CTE), melting, crystallinity, chain mobility, pore collapse, thermal conductivity κ, and Cp. An ablation compares the dry separator with one that has electrolyte.

This repo holds the Python build and analysis code, LAMMPS input templates, force-field parameters, and the generated data files. Production runs on a separate workstation with a small budget (<500 GPU-h).

**Repo today:** the `sepsim` package skeleton (uv, src layout, CLI stubs, tests) plus these docs. LAMMPS and packmol are installed only on the machines that build or run systems, never in the repo (D16).

## Decided
| ID | Topic | Decision |
|---|---|---|
| D1 | Compute | Single workstation; ~1–5k core-h / <500 GPU-h; hardware unknown. The budget assumes 1 modern GPU, and step 0 is a benchmark to calibrate ns/day. |
| D2 | LAMMPS | User builds a recent stable release. We document the cmake line: MOLECULE, KSPACE, EXTRA-MOLECULE, CG-SPICA, plus KOKKOS or GPU. |
| D3 | Building | Build locally and commit the data files. |
| D4 | PP | Isotactic only. |
| D5 | Chains | 40 × C240 at all resolutions: PE C240H482 and an iPP 80-mer, both ~3.4 kg/mol. That is 722 AA atoms per chain, ~29k AA atoms, and a box ~6.4 nm (bigger than R_ee ~6 nm). UA has ~9.6k sites, CG PE ~3.2k beads. |
| D5c | Chain-length handling | UA length series C120/C240/C480. Long CG PE at C1500–C3000 (see O2). No backmapping. |
| D6 | Morphologies | Amorphous (rectangular box). Crystals: PE orthorhombic (rectangular) and iPP α (triclinic). Slit-pore systems. |
| D6b | Melting | AA/UA Tm comes from a **pure crystal slab with free surfaces** (vacuum gap; the published fix for superheating). These slabs ramp to **~200 °C**, and the rate is reported. CG PE: cool/heat cycles for crystallization and crystallinity. Expect PE (~130–135 °C) below iPP (~160–165 °C). Infinite chains have no chain-end depression, but the finite heating rate can still push Tm up somewhat. |
| D6c | Pore walls | Ablation: amorphous walls vs crystal core + amorphous skin. |
| D6d | Crystal build | Infinite chains bonded to their own periodic image along c, so no chain ends and the box is small. In slabs, the chain axis lies **in-plane** (x or y); chains can't cross the vacuum gap. |
| D7 | CG coverage | SDK PE only. PP is covered at AA/UA. |
| D8 | Scope | Tiered T1 → T2 → T3; stop when the budget runs out (matrix below). |
| D9 | BCs and pressure | Bulk: 3D PBC, NPT iso at **1 atm**. Pore/slab: polymer slab periodic in x,y with a gap along z in a 3D-periodic box. **Dry:** barostat x,y only at 1 atm, z fixed (never barostat across vacuum). **Wet:** the gap is full of liquid, so NPT aniso (x, y, z independently) at 20 bar. |
| D9c | Pore widths | AA/UA: 3, 5, 10 nm. CG PE: a dry 20–50 nm pore. |
| D10 | Electrolyte | 1 M LiPF6 in EC/DMC, AA only, OPLS-AA, ion charges ×0.8. **NPT aniso (x,y,z) at 20 bar across 25–160 °C** (sealed-cell order; above DMC's ~8 bar vapor pressure). This replaces the earlier fixed-volume plan, which would have given ~800 bar. No decomposition modeled. Used in pore systems only. |
| D11 | T protocol | Stepwise heating ramp 25→160 °C in ~10 °C steps, with holds at ~25/90/130/160 °C. |
| D12a | Timestep | AA 1 fs fully flexible. UA 2 fs with **flexible harmonic backbone bonds** (k from the GROMACS TraPPE implementation) and SHAKE only on the explicit methine C–H; the step-0 benchmark checks energy conservation, fallback 1 fs. (LAMMPS SHAKE can't rigidify a connected backbone; revised 2026-10-16.) CG 10 fs. |
| D12b | κ | rNEMD (Müller-Plathe), branched from hold snapshots; box replicated ~3× along the flux axis, run NVE. **The κ temperatures (4 or 2) are a template parameter, chosen after the benchmark.** κ is ≈60 GPU-h of the ~405. |
| D12c | Cp | Classical dH/dT. For AA, add a VDOS quantum-harmonic correction from a short NVE high-frequency velocity dump at the end of each hold. |
| D12d | Replicas | 1 per system. Hold properties get block-averaged error bars. Ramp Tm gets no uncertainty. |
| D12e | Durations | **Lean**. AA: 1 ns per ramp step × ~14 steps (≈10 K/ns), holds 4 × 5 ns, κ branches 4 × 3 ns, so ≈50 ns per system. UA/CG run 2–5× longer at the same cost. |
| D12f | Run structure | One NPT sweep trajectory per system gives density, CTE, classical Cp, Tm/crystallinity, pore width, MSD, bond reorientation, RDF/Rg, and VDOS. Separate runs are only the κ branches and the CG crystallization cycles. |
| D12g | Ensembles | Nosé–Hoover throughout: `fix npt`, iso for amorphous, aniso/tri for crystals, x,y-only for slabs, Tdamp 100·dt, Pdamp 1000·dt. NVE for the rNEMD and VDOS segments. |
| D13 | Repo | Python package + CLI + templated LAMMPS inputs (layout below). |
| D16 | Environment | **uv only, no conda.** The Python env comes from `pyproject.toml` + `uv.lock` (`uv sync`). The repo carries only git-transferable content. External binaries (LAMMPS; packmol, needed only for the T2 electrolyte fill) are installed on the compute or build machine and documented, not managed here. The dev machine is not a compute machine. |
| D14 | Tg | **Dropped from scope** (2026-10-16). PE Tg (~−120 to −30 °C) and iPP Tg (~−10 to 0 °C) are both below 25 °C, so both polymers are rubbery across the whole range. Report that; no sub-ambient runs. |
| D15 | CG validation | Standard SDK PE (fit near ambient). Run an **early CG density-vs-T check** against UA and experiment, and report the deviation. Revisit (e.g., tSPICA, Griffiths & Shinoda 2019) only if it's off by more than a few %. |

## Last-round decisions
| ID | Decision |
|---|---|
| O1 | **Python-native builder**: chain growth, tacticity, typing, and data files. packmol only fills the electrolyte; no moltemplate. |
| O2 | Long CG PE: **C1500 in T1**, C3000 in T3. |
| O3 | Tier contents **as drafted** (below). |
| G1 | Git: **commit the existing scaffold (pyproject.toml, main.py, README.md, .python-version) to main once**, then do all work on a feature branch in a worktree. **Pushing the feature branch to the remote is OK** (at phase checkpoints). Merges to main need user approval. |
| O4 | ~~L-OPLS hybrid~~ **Superseded by D17** (2026-10-16). |
| D17 | AA force field | **OPLS/2020 for both PE and iPP** (Ghahremanpour, Tirado-Rives & Jorgensen, JPCB 2022). It was refit for long and branched liquid alkanes, including CH branch points, heat capacity, and a check that hexadecane doesn't gel. One consistent FF for the PE-vs-PP comparison. Parameters come from the official 2024 JPCB SI file via moltemplate `oplsaa2024.lt`. The CT–CT–CT–CT "hydrocarbon" torsion is used, not the "butane only" variant. |
| D18 | UA iPP tacticity | **Explicit methine H** on each CH: bond and angle terms only (OPLS CT–HC values), no LJ, zero charge, SHAKE on C–H. The CH mass becomes 12.011. No improper. Chosen because the published improper-only TraPPE-UA iPP chains didn't fold. |
| D19 | FF sourcing | Curated YAMLs in `forcefields/`, one per FF, holding only the types we use. Every number cites its primary paper and carries a verbatim upstream excerpt line in `forcefields/_reference/`; tests check YAML against the excerpts. Sources: moltemplate (MIT), SPICA-tools (MIT), and wesbarnett/trappeua (no license; numeric lines only, attributed). TraPPE's mixing rule, 1-4 exclusion and 14 Å cutoff are cited to Martin & Siepmann 1998 without line-level verification (paywalled). |
| D20 | SPICA settings | `special_bonds lj 0.0 0.0 1.0 angle yes` and a 15 Å LJ cutoff, per SPICA's official `setup_lmp.py`. moltemplate's 0 0 0 / 9 Å is superseded. |
| D21 | Running LAMMPS | Command line (`lmp -in deck`), not the Python API. `sepsim run` is an optional wrapper that writes `run_manifest.json`: LAMMPS version and `lmp -h` package list, deck and input hashes, git commit/dirty state, and the command. Decks stay plain LAMMPS files runnable by hand. Runs belong under the gitignored `runs/` so manifests don't mark the repo dirty. Container and pinned LAMMPS release are decided at phase 3. |
| D22 | Amorphous builders (phase 2) | iPP is H-terminated, H–[CH2–CH(CH3)]80–H = C240H482. Chains are grown bead-by-bead in a periodic box at 0.3 g/cm³ with overlap checks, then compressed in LAMMPS. Backbone torsions start with a melt-like bias: p(t)=0.6, p(g±)=0.2, no g+g− pairs. Seeded and deterministic. |
| D23 | LAMMPS build | Pinned **`stable_22Jul2025_update6`** (GitHub tag; checked 2026-10-16 against the release list; `stable_30Sep2026` is newer but only two weeks old). Packages: MOLECULE, KSPACE, EXTRA-MOLECULE, CG-SPICA, **KOKKOS (CUDA) + GPU + OPENMP**; the step-0 benchmark picks the accelerator per resolution and run type, and the choice is recorded in the run manifest. KOKKOS covers lj/spica and dihedral opls; the GPU package offloads only pair forces and PPPM. **Packaging:** one committed build script (tag + cmake flags), used by an **Apptainer** definition pinned to a CUDA base image. The `.sif` is rebuilt from the repo, not committed; run with `--nv`. GPU arch and CUDA version are build parameters, since the workstation hardware is unknown. |
| D24 | Equilibration | Amorphous boxes go 0.3 g/cm³ → melt density with the **21-step protocol** (Larsen et al., Macromolecules 2011, 44, 6944; Pmax ≈ 50 kbar). The step table is to be sourced and cited in phase 3. |
| D25 | AA nonbonded | OPLS/2020: LJ cutoff **12 Å with analytic tail corrections**, PPPM at 1e-5 relative accuracy, geometric mixing, special_bonds lj/coul 0 0 0.5. TraPPE 14 Å with tail corrections and SPICA 15 Å per their sources. Tail corrections are invalid for slab/pore systems; see the pending list. |

## Experiment matrix (decided)
GPU-h figures are **rough guesses for 1 modern GPU** (AA 29k atoms ≈ 30 ns/day). Recalibrate after the step-0 benchmark.

| Tier | System | Res | Runs | ~GPU-h |
|---|---|---|---|---|
| T1 | PE, iPP amorphous bulk (40×C240) | AA | sweep + VDOS + κ (κ boxes are 3× larger, ~87k atoms) | 115 |
| T1 | PE, iPP crystal slab + gap (infinite chains, ~10–15k atoms) | AA | ramp to ~200 °C (Tm) | 30 |
| T1 | PE, iPP amorphous + crystal | UA | sweep (+κ amorphous) | 40 |
| T1 | PE amorphous C240 + long C1500 | CG | sweep + cool/heat cycles | 30 |
| T2 | Dry slit pore, amorphous walls, 3/5/10 nm, PE+iPP | AA | sweep, no κ | 120 |
| T2 | Same | UA | sweep | 30 |
| T2 | Wet pore, 5 nm, PE amorphous walls, LiPF6 EC/DMC (~47k atoms) | AA | sweep, NPT 20 bar | 40 |
| | **T1+T2 total** | | | **≈405** (~95 GPU-h headroom on a guessed throughput) |
| T3 | Crystal-core walls: pore series (wall ablation) | AA/UA | sweep | remaining |
| T3 | UA length series C120/C480 (C240 is already in T1) | UA | sweep | ~20 |
| T3 | CG PE 20–50 nm dry pore; CG C3000 | CG | sweep / cycles | ~30 |
| T3 | Wet pores: iPP, other widths, crystal walls | AA | sweep | remaining |

## Repo layout (D13)
```
docs/TLDR.md, docs/decisions.md        # resume + register (first deliverable)
pyproject.toml                          # uv; numpy, scipy, MDAnalysis, jinja2, matplotlib, pytest
src/sepsim/
  cli.py                                # `sepsim build|render|analyze ...`
  build/  chains.py (random-walk growth, tacticity), crystal.py (PE ortho, iPP α, infinite chains),
          slab.py (slab + gap, crystal-core+skin walls), electrolyte.py (packmol fill), datafile.py
  ff/     loplsaa.py, trappe_ua.py, spica.py, electrolyte.py  # typing + coeff emission
  lammps/ render.py + templates/*.in.j2 (minimize, compress_anneal, sweep, kappa_rnemd, cg_cycle, benchmark)
  analysis/ thermo.py (ρ, CTE, Tm onset fits, dH/dT), vdos.py (Cp quantum correction),
          mobility.py (MSD, P2(t)), order.py (crystallinity P2), kappa.py, pore.py (z density profile)
forcefields/<ff>/*.yaml                 # parameters + citations, single source of truth
systems/<system_id>/{data.lmp, manifest.yaml}   # generated, committed (D3)
results/                                # small processed CSVs/plots (committed); raw runs/ gitignored
tests/                                  # builder/FF/template unit tests
docs/LAMMPS_BUILD.md                    # cmake line for the workstation
```

## Implementation order (after approval; each phase ends with a user check)
0. **Done (2026-10-16).** Committed the scaffold, wrote the docs, and set up the uv package skeleton: `sepsim` CLI stubs, deps, lockfile, tests, ruff.
1. **Done (2026-10-16).** Force-field YAMLs (D17–D20), reference excerpts, `sepsim.ff.params` loader with conversion to LAMMPS real units, and tests (86 pass).
2. Builders for amorphous PE/iPP at all three resolutions, plus unit tests (atom counts, charge neutrality, tacticity, initial density).
3. LAMMPS templates: benchmark, compress/anneal, sweep. Write `docs/LAMMPS_BUILD.md`. Hand T1 benchmark inputs to the user, plus the early CG PE density-vs-T check (D15).
4. Crystal builders (infinite chains) + κ rNEMD + CG cycle templates.
5. **Core done (2026-10-16):** LAMMPS log parser, block averaging and fits, density, CTE, classical Cp, VDOS with quantum Cv correction, MSD, P2(t), and rNEMD κ, all tested on synthetic data. **Still to decide:** the crystallinity order parameter, Tm detection, pore-width definition, and κ slab-exclusion distance.
6. T2: slab/pore + electrolyte builders. T3 extensions.

## Verification
- **Unit tests:**
  - Builder outputs: composition, bonded topology, charges summing to 0, isotacticity check, triclinic cell for iPP α.
  - FF emission matches the YAML.
  - Templates render.
- **Smoke test, run by the user on the workstation:** `run 0` plus a 10 ps run for every input deck. Check for no lost atoms and sane energies.
- **Physics checks after T1:**
  - Amorphous PE at 25 °C is ~0.85 g/cm³; iPP amorphous is ~0.85–0.86.
  - The crystal density is close to the lattice value at 25 °C.
  - Melting is ordered PE < iPP.
  - CG PE density vs T is within a few % of UA and experiment (D15).
  - Amorphous AA PE at 25 °C shows no spurious ordering under OPLS/2020 (D17).
  - The κ T-profile is linear.
- **Analysis code:** validated on synthetic signals (known slope/kink, known MSD exponent).

## Pending user decisions
- Analysis definitions: crystallinity order parameter, Tm detection from ramps, pore width, κ slab-exclusion distance.
- T2: long-range dispersion treatment for slab/pore systems (no tail correction vs LJ-PPPM), since analytic tail corrections assume a homogeneous bulk.
- Phase 4: iPP α crystal source (paywalled coordinate table vs geometric construction + minimization + density check); PE setting angle 41° vs 45°.

## Verified facts (sources checked 2026-10-12, 2026-10-16)
- **SPICA in LAMMPS:** the package is CG-SPICA; `pair_style lj/spica` (`lj/sdk` is an alias); `angle_style spica`.
- **SDK models:** an SDK PE model exists (3 CH2 per bead, used for crystallization). There is no SDK PP model.
- **Other published CG PP models:** Martini 2 (Panizon 2015) and Sigalas 2022 iPP. These were not chosen.
- **TraPPE-UA iPP:** needs an improper torsion or explicit H to hold tacticity (D18). CH: σ 4.68 Å, ε/k 10 K; bends 112°/114°, k/k 62 500 K/rad²; verified against the GROMACS implementation.
- **L-OPLS (Siu 2012):** validated on linear alkanes only; superseded by OPLS/2020 (D17).
- **Crystal data (phase 4):** PE orthorhombic cell (Busing, 23 °C): a 7.4069, b 4.9491, c 2.5511 Å, Pnam, setting angle 41° (Bunn) or 45° (Chatani). iPP α: Natta–Corradini a 6.65, b 20.96, c 6.50 Å, β 99.8° (Turner-Jones: 6.66/20.78/6.495 Å/99.62°), 4 chains of 3₁ helices; α₂ = P2₁/c (ordered), α₁ = C2/c. No open-access iPP atom-coordinate table found, so it's a user decision at phase 4.
- **OPLS-AA LiPF6 in EC/DMC:** density is OK. Transport is underestimated unless the ion charges are scaled (×0.8 is common).
- **TraPPE battery-solvent extension:** exists; its ion parameters are unchecked.

## Physics caveats (state them in results)
- **κ:** only AA κ is physical. UA/CG lack vibrational modes.
- **Cp:** classical Cp is too high; the AA quantum correction addresses it.
- **Tm from ramps:** rate-inflated; report the rate.
- **Tg:** below the studied range for both polymers (D14).
- **Amorphous C240 walls:** effectively a supercooled melt, so they represent a post-shutdown separator.
- **Pore closure:** real closure is ≫ ns, so we measure wall mobility and narrowing trends vs width.
- **Chain length:** C240 is far below real Mw (10⁵–10⁶ g/mol). Only density, CTE, Cp, and κ are chain-length-converged.
- **Melting points:** iPP Tm (~160–165 °C) sits at the top of the range; PE Tm (~130–135 °C) is inside it.
- **Electrolyte at high T:** DMC boils at ~90 °C at 1 atm, so wet systems run at 20 bar. LiPF6 thermal decomposition is not modeled.
- **Crystal superheating:** periodic perfect crystals overshoot Tm by up to ~100 °C, which is why the slab has free surfaces.
