# pe_cg_film_160C_n640_c240_s1_rep441 / puncture_160C_v10_R2nm_c1

- status: **failed** (manifest: failed), node rdyu-rog, started 2026-11-14 20:36 PST, ended 2026-11-15 00:29 PST
- progress: 56.8% of 220,000 MD steps; 1/2 segments done; current: 2 Stage 2: indent at 10 m/s, R 2 nm, travel 20 nm
- speed: 7.58 ns/day (8.8 steps/s, running segment (last hour of thermo))
- log updated 2026-11-15 00:29 PST (8.4 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: ERROR in log
- log: `ERROR on proc 0: Bond atoms 21476 21477 missing on proc 0 at step 125039`

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 433.15 K, indenter clear of the film | done | 20,000 | 160.0 | 159.9 | 0.4338 ± 0.0000 | -12005.4 ± 58.3 | 64.2 ± 0.7 |  |
| 2 | Stage 2: indent at 10 m/s, R 2 nm, travel 20 nm | running | 105,000/200,000 | 160.0 |  |  |  |  |  |
