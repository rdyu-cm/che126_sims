# TLDR: resume here

**Project:** LAMMPS MD of Li-ion (EV) separator polymers, PE and isotactic PP, from 25 to 160 °C. Three resolutions:
- all-atom (L-OPLS / OPLS-AA)
- united-atom (TraPPE-UA)
- coarse-grained (SDK/SPICA, PE only)

The repo holds the build and analysis code, templates, and force-field parameters. Production runs on a separate workstation with a budget under 500 GPU-h.

**Status (2026-10-16):** design is done and was re-reviewed; every decision is in [`decisions.md`](decisions.md). **Nothing is implemented yet.** No plan step has started.

**Rules:**
- Every new design choice goes to the user before it's built.
- Work on a feature branch in a worktree, not on `main`.
- Pushing feature branches is fine. Merges to `main` need user approval.

**Next step:** implementation phase 0 (see "Implementation order" in `decisions.md`):
1. Set up uv deps and a conda env with packmol.
2. Then phase 1: force-field parameter YAMLs, with every number cited. The user reviews them at a checkpoint.

## Decisions at a glance
**Systems**
- Chains: 40 × C240 at every level (PE C240H482 / iPP 80-mer), ~29k atoms in all-atom.
- UA length series: C120 and C480.
- Long-chain coarse-grained PE: C1500 (C3000 in tier 3).

**Morphologies**
- Amorphous bulk.
- Crystal **slab with free surfaces** for Tm (infinite chains), ramped to ~200 °C.
- Slit pores (slab + gap in a 3D-periodic box):
  - widths 3/5/10 nm at AA/UA
  - 20–50 nm dry pore at CG
  - wall ablation: amorphous vs crystal-core + amorphous skin

**Electrolyte**
- 1 M LiPF6 in EC/DMC, all-atom only, ion charges ×0.8, NPT at 20 bar.
- Dry systems run at 1 atm; dry slabs are barostatted in x and y only, with z fixed. Wet pores are NPT aniso (x, y, z) at 20 bar.

**Protocol**
- One NPT sweep trajectory per system: ~10 °C steps of 1 ns each, plus holds of 5 ns at 25, 90, 130, and 160 °C.
- Thermal conductivity κ: rNEMD branch runs. Whether to use 4 or 2 temperatures is decided after the benchmark.
- Cp: dH/dT plus a VDOS quantum correction (all-atom).
- Timesteps: AA 1 fs flexible / UA 2 fs with SHAKE / CG 10 fs. Nosé–Hoover thermostat; NVE for κ and VDOS.
- 1 replica per system.
- **Tg is out of scope:** both polymers have Tg below 25 °C.
- Coarse-grained: standard SDK PE, with an early density-vs-T check against UA and experiment.

**Budget**
- Tiers T1 → T2 → T3; T1 + T2 ≈ 405 GPU-h. This rests on a guessed throughput, and the step-0 benchmark recalibrates it.

**Tooling**
- Python-native builder (no moltemplate); packmol only for the electrolyte.
- Python package plus a `sepsim` CLI and Jinja LAMMPS templates.
