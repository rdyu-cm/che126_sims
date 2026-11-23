# pe_cg_film_90C_n640_c240_s1_rep441 / puncture_90C_v10_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-rog, started 2026-11-14 14:57 PST, ended 2026-11-14 20:36 PST
- progress: 75.3% of 220,000 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 10 m/s, R 2 nm, travel 20 nm
- speed: 6.29 ns/day (7.3 steps/s, running segment (last hour of thermo))
- log updated 2026-11-14 20:36 PST (8.6 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 19811 19812 missing on proc 0 at step 165793`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 363.15 K, indenter clear of the film | done | 20,000 | 90.0 | 90.1 | 0.4525 ± 0.0000 | -41860.7 ± 74.5 | 57.3 ± 0.7 |  |
| 2 | Stage 2: indent at 10 m/s, R 2 nm, travel 20 nm | running | 145,700/200,000 | 90.0 |  |  |  |  |  |
