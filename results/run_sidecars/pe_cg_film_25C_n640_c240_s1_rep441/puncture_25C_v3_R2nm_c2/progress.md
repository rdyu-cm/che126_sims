# pe_cg_film_25C_n640_c240_s1_rep441 / puncture_25C_v3_R2nm_c2

- status: **failed** (manifest: failed), node rdyu-server, started 2026-11-15 08:36 UTC, ended 2026-11-15 18:05 UTC
- progress: 58.9% of 686,667 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 3 m/s, R 2 nm, travel 20.00001 nm
- speed: 9.47 ns/day (11.0 steps/s, running segment (last hour of thermo))
- log updated 2026-11-15 18:05 UTC (8.0 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 38630 38631 missing on proc 0 at step 404462`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 298.15 K, indenter clear of the film | done | 20,000 | 25.0 | 24.9 | 0.4702 ± 0.0000 | -71627.3 ± 31.7 | 47.6 ± 0.6 |  |
| 2 | Stage 2: indent at 3 m/s, R 2 nm, travel 20.00001 nm | running | 384,400/666,667 | 25.0 |  |  |  |  |  |
