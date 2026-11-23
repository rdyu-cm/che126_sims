# pe_cg_film_25C_n640_c240_s1_rep441 / puncture_25C_v1_R2nm_c2

- status: **failed** (manifest: failed), node rdyu-server, started 2026-11-14 15:51 UTC, ended 2026-11-16 12:24 UTC
- progress: 58.4% of 2,020,000 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 1 m/s, R 2 nm, travel 20 nm
- speed: 5.32 ns/day (6.2 steps/s, running segment (last hour of thermo))
- log updated 2026-11-16 12:24 UTC (7.3 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 2878 2879 missing on proc 0 at step 1180563`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 298.15 K, indenter clear of the film | done | 20,000 | 25.0 | 24.9 | 0.4702 ± 0.0000 | -71627.3 ± 31.7 | 47.6 ± 0.6 |  |
| 2 | Stage 2: indent at 1 m/s, R 2 nm, travel 20 nm | running | 1,160,500/2,000,000 | 25.0 |  |  |  |  |  |
