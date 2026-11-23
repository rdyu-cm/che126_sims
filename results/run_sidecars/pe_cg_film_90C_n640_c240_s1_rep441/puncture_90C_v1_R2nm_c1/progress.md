# pe_cg_film_90C_n640_c240_s1_rep441 / puncture_90C_v1_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-server, started 2026-11-13 18:34 UTC, ended 2026-11-15 12:50 UTC
- progress: 78.6% of 1,437,426 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 1 m/s, R 2 nm, travel 14.17426 nm
- speed: 6.27 ns/day (7.3 steps/s, running segment (last hour of thermo))
- log updated 2026-11-15 12:50 UTC (8.2 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 32370 32371 missing on proc 0 at step 1130463`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 363.15 K, indenter clear of the film | done | 20,000 | 90.0 | 89.8 | 0.4525 ± 0.0000 | -42292.9 ± 37.2 | 57.3 ± 0.7 |  |
| 2 | Stage 2: indent at 1 m/s, R 2 nm, travel 14.17426 nm | running | 1,110,400/1,417,426 | 90.0 |  |  |  |  |  |
