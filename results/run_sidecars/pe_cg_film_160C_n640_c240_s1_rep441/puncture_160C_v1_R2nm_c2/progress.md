# pe_cg_film_160C_n640_c240_s1_rep441 / puncture_160C_v1_R2nm_c2

- status: **failed** (manifest: failed), node rdyu-rog, started 2026-11-13 13:52 PST, ended 2026-11-14 14:57 PST
- progress: 55.9% of 1,509,595 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 1 m/s, R 2 nm, travel 14.89595 nm
- speed: 8.33 ns/day (9.6 steps/s, running segment (last hour of thermo))
- log updated 2026-11-14 14:57 PST (8.8 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 21476 21477 missing on proc 0 at step 844250`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 433.15 K, indenter clear of the film | done | 20,000 | 160.0 | 159.8 | 0.4338 ± 0.0000 | -12504.4 ± 68.8 | 63.2 ± 0.9 |  |
| 2 | Stage 2: indent at 1 m/s, R 2 nm, travel 14.89595 nm | running | 824,200/1,489,595 | 160.0 |  |  |  |  |  |
