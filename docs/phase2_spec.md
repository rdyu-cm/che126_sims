# Phase 2 spec: amorphous system builders

Approved spec (decisions D5, D5c, D7, D12a, D17–D19, D22). Partial work is on branch `feat/phase2-builders` (commit `94527b9`): `src/sepsim/build/growth.py` and `src/sepsim/build/topology.py` exist, import cleanly and pass ruff. They have **not** been reviewed or tested. Still missing: the data-file writer, the CLI, tests, and the generated systems.

## Fixed choices
- **Systems:** `n_chains × n_carbons`, both parameters, default 40 × 240.
  - PE = n-C240H482.
  - iPP = H–[CH2–CH(CH3)]80–H, isotactic and H-terminated (C240H482).
  - Also needed: CG long PE (40 × C1500 → 500 beads per chain) and the UA length series (C120, C480).
- **Resolutions:**
  - **AA:** OPLS/2020 (`forcefields/opls2020_aa.yaml`).
  - **UA:** TraPPE-UA (`forcefields/trappe_ua.yaml`). An explicit H sits on every iPP methine, with bond and angle terms only, no LJ, q = 0. CH mass is 12.011. Backbone bonds are flexible harmonic; only the CH–H bond is constrained with SHAKE.
  - **CG:** SDK PE only (`forcefields/sdk_cg.yaml`): CT–CM…CM–CT, 3 carbons per bead. CG iPP must raise a clear error.
- **Packing:**
  - Grow heavy atoms bead by bead in a periodic box at 0.3 g/cm³ (parameter), with overlap checks against all placed atoms (cell list, minimum image).
  - Place hydrogens geometrically afterwards.
  - Compression to melt density happens later in LAMMPS (push-off, minimize, NPT compression at 500 K; D24).
- **Growth torsions:**
  - Melt-like RIS bias: p(t) = 0.6, p(g±) = 0.2 (parameters).
  - Reject consecutive g+g−/g−g+.
  - Each torsion gets ±10° Gaussian jitter around its RIS state (D29).
  - Growth overlap thresholds (AA): heavy–heavy 3.0 Å, heavy–H 2.0 Å, H–H 1.6 Å (D29). LAMMPS minimization removes the close H contacts.
  - On repeated overlap failure, backtrack a few beads; restart the chain if needed.
  - Deterministic from one integer seed.
- **Geometry:** use the FF equilibrium values.
  - **AA/UA:** C–C 1.529/1.54 Å; C–C–C 112.7°/114° (UA CH vertex 112°).
  - **CG:** bonds 3.64/3.65 Å; each angle drawn from the FF's own Boltzmann distribution at 500 K, P(θ) ∝ sin θ · exp(−E(θ)/kT) (D29), with E the full LAMMPS `angle_style spica` energy (D33): K(θ−θ0)² plus the 1–3 repulsion, i.e. the lj/spica energy of the end-bead pair (CM–CM or CM–CT) at r13(θ) from the two bond lengths, shifted by its minimum and zero beyond r_min. This gives melt-like chain size (C240 R_ee ≈ 66–68 Å, C1500 ≈ 180 Å) and no tight angles (min θ ≈ 65° in 40×C1500). The earlier 10° spread gave chains 4–5× too extended; the harmonic-only weight let a few angles close to ~20° (1–3 distance 1.6 Å).
  - **AA H placement:** C–H 1.09 Å, near-tetrahedral (exactness not critical; minimization follows).
- **iPP torsions (D30):** a meso-dyad rule replaces the generic RIS bias: dyads are (t, g+) or (g−, t), and the helix hand reverses at each junction with probability `ipp_p_reversal`, calibrated so overlap-checked grown chains give the iPP melt C∞ ≈ 6.15 (D42). `ipp_p_reversal = 0.50`. iPP growth ignores intra-chain pairs ≤ 6 bonds apart (D31); the local strain is removed by a soft-core push-off at the start of the phase 3 prep deck.
- **AA iPP (D32):** not grown directly; produced by `sepsim build ua2aa` from a LAMMPS-relaxed UA iPP box.
- **iPP chirality:** every CH has the same configuration. The signed volume of (methyl − C, H − C, next − prev backbone) must have a consistent sign along the chain; define it precisely and test it.

## Outputs, per system, in `systems/<system_id>/`
- **`data.lmp`:** atom_style full.
  - Masses, plus coefficient sections in LAMMPS real units from `sepsim.ff.params.to_lammps_real`. Use Pair Coeffs for mixed FFs, PairIJ Coeffs for SDK, plus Bond/Angle/Dihedral Coeffs.
  - All bonds, angles, and the proper dihedrals the FF defines: AA includes H; UA never includes the explicit H; CG has no dihedrals.
  - Every entry must map to exactly one FF type, or fail loudly.
- **`manifest.yaml`:**
  - id, polymer, resolution, n_chains, n_carbons, seed, build density, box, counts, total mass, formula
  - FF file name and sha256
  - sepsim version, git commit and dirty flag
  - growth parameters, SHAKE bond types, LAMMPS styles
- **system_id:** `{polymer}_{res}_amorph_n{chains}_c{carbons}_s{seed}`, e.g. `pe_aa_amorph_n40_c240_s1`.
- **CLI:** `sepsim build amorphous --polymer {pe,ipp} --res {aa,ua,cg} [--chains 40] [--carbons 240] [--density 0.3] [--seed 1] [--out systems/]`.
- **Generate T1 systems (seed 1):**
  - pe/ipp × aa/ua at 40 × 240
  - pe cg at 40 × 240
  - pe cg at 40 × 1500
  - Report file sizes before committing; don't commit any file > 20 MB without asking.

## Tests (small systems for speed)
- **Counts:**
  - AA atoms per chain = 3n + 2.
  - UA PE = n; UA iPP = n + n/3 − 1 (the last unit's CH becomes a CH2, so there are n/3 − 1 methines).
  - CG = n/3.
  - Bond/angle/dihedral counts match the linear-chain formulas.
- **Physical consistency:**
  - Charge neutrality (AA).
  - Total mass equals the formula mass.
  - Box volume matches the target density.
- **No overlaps:** minimum non-bonded heavy-atom distance > 2.5 Å (AA), 3.0 Å (UA), 3.5 Å (CG), excluding 1-2/1-3/1-4.
- **Geometry:**
  - Bond lengths equal r0.
  - Angles within tolerance.
  - Torsion statistics roughly match the RIS probabilities.
- **Isotacticity:** check AA and UA; a flipped-methyl fixture must fail.
- **Topology:** every bonded entry maps to a defined type; UA dihedrals never include the H.
- **Determinism:** same seed gives identical bytes; a different seed gives different output.
- **Errors:** the data file parses back; CG iPP raises.

## Rules for the implementer
Work in a worktree under `/home/rdyu/projects/worktrees/`. Use uv only and numpy/scipy. Ask before adding any dependency. Don't edit `docs/`. Report every design choice made beyond this spec, for user approval.
