# TLDR: resume here

**Project:** LAMMPS MD of Li-ion (EV) separator polymers, PE and isotactic PP, from 25 to 160 °C. Three resolutions:
- all-atom (OPLS/2020)
- united-atom (TraPPE-UA)
- coarse-grained (SDK/SPICA, PE only)

The repo holds the build and analysis code, templates, and force-field parameters. Production runs on a separate workstation with a budget under 500 GPU-h.

**Status (2026-10-16):** design is done; every decision is in [`decisions.md`](decisions.md). **Done:**
- phase 0 (uv package skeleton)
- phase 1 (force-field YAMLs with verified sources)
- the `sepsim run` reproducibility wrapper
- the core analysis library

No system builders or LAMMPS templates exist yet.

**Rules:**
- Every new design choice goes to the user before it's built.
- Work on a feature branch in a worktree, not on `main`.
- Pushing feature branches is fine. Merges to `main` need user approval.

**In progress (paused 2026-10-16):** phase 2 amorphous builders. An implementer was running in local worktree `../che126_sims-phase2` (branch `feat/phase2-builders`, not pushed). If that work is gone, restart phase 2 from the D22 spec. Phase 3 decisions D23–D25 are made (LAMMPS stable_22Jul2025_update6, Apptainer, KOKKOS+GPU+OPENMP, 21-step, AA 12 Å).

**Next decisions to ask:**
- Phase 4 crystal source (iPP coordinates) and the PE setting angle.

Analysis definitions are decided (D26).

**Setup on any machine:**
```
uv sync && uv run pytest -q
```
No conda. LAMMPS (and packmol, for the T2 electrolyte) are installed only on the machines that build or run systems.

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
- Timesteps: AA 1 fs flexible / UA 2 fs (flexible backbone, SHAKE only on the explicit methine C–H; fallback 1 fs) / CG 10 fs.
- LAMMPS runs from the command line; the optional `sepsim run` writes a reproducibility manifest. Nosé–Hoover thermostat; NVE for κ and VDOS.
- 1 replica per system.
- **Tg is out of scope:** both polymers have Tg below 25 °C.
- Coarse-grained: standard SDK PE, with an early density-vs-T check against UA and experiment.

**Budget**
- Tiers T1 → T2 → T3; T1 + T2 ≈ 405 GPU-h. This rests on a guessed throughput, and the step-0 benchmark recalibrates it.

**Tooling**
- Python-native builder (no moltemplate); packmol only for the electrolyte.
- Python package plus a `sepsim` CLI and Jinja LAMMPS templates.
