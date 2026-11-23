# pe_cg_film_25C_n640_c240_s1_rep441 / puncture_25C_v30_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-rog, started 2026-11-13 11:42 PST, ended 2026-11-13 13:49 PST
- progress: 92.6% of 66,430 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 30 m/s, R 2 nm, travel 13.929 nm
- speed: 6.90 ns/day (8.0 steps/s, running segment (last hour of thermo))
- log updated 2026-11-13 13:49 PST (9.9 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 31381 31382 missing on proc 0 at step 61566`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 298.15 K, indenter clear of the film | done | 20,000 | 25.0 | 25.1 | 0.4702 ± 0.0000 | -70914.7 ± 32.3 | 45.8 ± 0.6 |  |
| 2 | Stage 2: indent at 30 m/s, R 2 nm, travel 13.929 nm | running | 41,500/46,430 | 25.0 |  |  |  |  |  |
