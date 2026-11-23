# pe_cg_film_90C_n640_c240_s1_rep441 / puncture_90C_v300_R2nm_p1

- status: **failed** (manifest: failed), node rdyu-rog, started 2026-11-12 16:23 PST, ended 2026-11-12 17:09 PST
- progress: 98.3% of 24,725 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 300 m/s, R 2 nm, travel 14.175 nm
- speed: 6.76 ns/day (7.8 steps/s, running segment (last hour of thermo))
- log updated 2026-11-12 17:09 PST (10.7 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 39677 39678 missing on proc 0 at step 24371`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 363.15 K, indenter clear of the film | done | 20,000 | 90.0 | 90.0 | 0.4525 ± 0.0000 | -41481.2 ± 71.9 | 32.3 ± 1.1 |  |
| 2 | Stage 2: indent at 300 m/s, R 2 nm, travel 14.175 nm | running | 4,300/4,725 | 90.0 |  |  |  |  |  |
