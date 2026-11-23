# pe_cg_film_25C_n640_c240_s1_rep441 / puncture_25C_v1_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-server, started 2026-11-13 21:58 UTC, ended 2026-11-14 23:28 UTC
- progress: 74.8% of 1,412,908 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 1 m/s, R 2 nm, travel 13.92908 nm
- speed: 10.13 ns/day (11.7 steps/s, running segment (last hour of thermo))
- log updated 2026-11-14 23:28 UTC (8.8 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 29583 29584 missing on proc 0 at step 1056247`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 298.15 K, indenter clear of the film | done | 20,000 | 25.0 | 25.1 | 0.4702 ± 0.0000 | -70914.7 ± 32.3 | 45.8 ± 0.6 |  |
| 2 | Stage 2: indent at 1 m/s, R 2 nm, travel 13.92908 nm | running | 1,036,200/1,392,908 | 25.0 |  |  |  |  |  |
