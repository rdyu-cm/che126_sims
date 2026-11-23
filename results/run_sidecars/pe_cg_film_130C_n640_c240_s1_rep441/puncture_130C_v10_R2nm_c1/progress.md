# pe_cg_film_130C_n640_c240_s1_rep441 / puncture_130C_v10_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-rog, started 2026-11-15 00:30 PST, ended 2026-11-15 04:38 PST
- progress: 59.0% of 220,000 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 10 m/s, R 2 nm, travel 20 nm
- speed: 7.46 ns/day (8.6 steps/s, running segment (last hour of thermo))
- log updated 2026-11-15 04:38 PST (8.3 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 35329 35330 missing on proc 0 at step 129731`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 403.15 K, indenter clear of the film | done | 20,000 | 130.0 | 130.1 | 0.4417 ± 0.0000 | -24085.6 ± 41.3 | 59.4 ± 0.7 |  |
| 2 | Stage 2: indent at 10 m/s, R 2 nm, travel 20 nm | running | 109,700/200,000 | 130.0 |  |  |  |  |  |
