# pe_cg_film_25C_n640_c240_s1_rep441 / puncture_25C_v0.3_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-rog, started 2026-11-13 10:33 PST, ended 2026-11-16 01:35 PST
- progress: 76.2% of 4,663,026 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 0.3 m/s, R 2 nm, travel 13.929078 nm
- speed: 14.32 ns/day (16.6 steps/s, running segment (last hour of thermo))
- log updated 2026-11-16 01:35 PST (7.4 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 43237 43238 missing on proc 0 at step 3553763`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 298.15 K, indenter clear of the film | done | 20,000 | 25.0 | 24.9 | 0.4702 ± 0.0000 | -70838.0 ± 41.8 | 44.8 ± 0.6 |  |
| 2 | Stage 2: indent at 0.3 m/s, R 2 nm, travel 13.929078 nm | running | 3,533,700/4,643,026 | 25.0 |  |  |  |  |  |
