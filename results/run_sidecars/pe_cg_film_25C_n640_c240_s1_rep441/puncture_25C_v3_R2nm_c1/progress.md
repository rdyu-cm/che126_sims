# pe_cg_film_25C_n640_c240_s1_rep441 / puncture_25C_v3_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-server, started 2026-11-14 23:28 UTC, ended 2026-11-15 08:36 UTC
- progress: 58.6% of 686,667 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 3 m/s, R 2 nm, travel 20.00001 nm
- speed: 10.54 ns/day (12.2 steps/s, running segment (last hour of thermo))
- log updated 2026-11-15 08:36 UTC (8.4 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 41479 41480 missing on proc 0 at step 402370`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 298.15 K, indenter clear of the film | done | 20,000 | 25.0 | 25.1 | 0.4702 ± 0.0000 | -70914.7 ± 32.3 | 45.8 ± 0.6 |  |
| 2 | Stage 2: indent at 3 m/s, R 2 nm, travel 20.00001 nm | running | 382,300/666,667 | 25.0 |  |  |  |  |  |
