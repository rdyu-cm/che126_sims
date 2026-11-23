# pe_cg_film_130C_n640_c240_s1_rep441 / puncture_130C_v1_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-server, started 2026-11-13 21:58 UTC, ended 2026-11-15 18:25 UTC
- progress: 75.7% of 1,534,644 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 1 m/s, R 2 nm, travel 15.14644 nm
- speed: 6.18 ns/day (7.2 steps/s, running segment (last hour of thermo))
- log updated 2026-11-15 18:25 UTC (8.0 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 16601 16602 missing on proc 0 at step 1161728`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 403.15 K, indenter clear of the film | done | 20,000 | 130.0 | 130.1 | 0.4417 ± 0.0000 | -24085.6 ± 41.3 | 59.4 ± 0.7 |  |
| 2 | Stage 2: indent at 1 m/s, R 2 nm, travel 15.14644 nm | running | 1,141,700/1,514,644 | 130.0 |  |  |  |  |  |
