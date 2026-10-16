# Design plan & decision register: PE/PP separator MD (LAMMPS, AA/UA/CG)

> **New chat? Start here.**
> - **Phase:** design complete and approved for documentation. **Nothing is implemented yet.**
> - **Rule from the user:** every design decision goes through the user. Ask, record, then build. Any new design choice that comes up during implementation is a checkpoint for the user too.
> - **Next action:** implementation phase 1, the force-field parameter YAMLs, with every number cited. The user reviews them at a checkpoint. Phase 0 is done.
> - **Docs:** `docs/TLDR.md` is the short resume. This file is the full register, facts, and caveats. Keep both current.
> - **Last updated:** 2026-10-16 (design review: Tg dropped, wet-pore barostat fixed, CG density check added; phase 0 done, uv-only env).

## Context
We want to characterize the separator polymers in EV Li-ion cells, starting with PE and isotactic PP, from 25 to 160 °C using LAMMPS MD at three resolutions:
- all-atom (OPLS-AA / L-OPLS)
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
| D12a | Timestep | AA 1 fs fully flexible. UA 2 fs with SHAKE on the fixed TraPPE bonds. CG 10 fs. |
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
| O4 | AA PP: **hybrid**, L-OPLS for CH2/CH3 + stock OPLS-AA for the methine CH; documented as a hybrid. PE is pure L-OPLS. |

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
1. Force-field parameter YAMLs, with every number cited. **Checkpoint:** user reviews the parameters.
2. Builders for amorphous PE/iPP at all three resolutions, plus unit tests (atom counts, charge neutrality, tacticity, initial density).
3. LAMMPS templates: benchmark, compress/anneal, sweep. Write `docs/LAMMPS_BUILD.md`. Hand T1 benchmark inputs to the user, plus the early CG PE density-vs-T check (D15).
4. Crystal builders (infinite chains) + κ rNEMD + CG cycle templates.
5. Analysis modules, tested on synthetic data.
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
  - The κ T-profile is linear.
- **Analysis code:** validated on synthetic signals (known slope/kink, known MSD exponent).

## Verified facts (sources checked 2026-10-12)
- **SPICA in LAMMPS:** the package is CG-SPICA; `pair_style lj/spica` (`lj/sdk` is an alias); `angle_style spica`.
- **SDK models:** an SDK PE model exists (3 CH2 per bead, used for crystallization). There is no SDK PP model.
- **Other published CG PP models:** Martini 2 (Panizon 2015) and Sigalas 2022 iPP. These were not chosen.
- **TraPPE-UA iPP:** needs an improper torsion or explicit H to hold tacticity. The CH parameters must be checked against Martin & Siepmann 1998/99.
- **L-OPLS (Siu 2012):** validated on linear alkanes only (see O4).
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
