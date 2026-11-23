# pe_cg_film_160C_n640_c240_s1_rep441 / puncture_160C_v10_R2nm_c1dt5

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-15 04:38 PST, ended 2026-11-15 17:49 PST
- progress: 100.0% of 440,000 MD steps; 2/2 segments done
- speed: 4.00 ns/day (9.2 steps/s, Performance line of segment 2)
- log updated 2026-11-15 17:49 PST (7.7 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 433.15 K, indenter clear of the film | done | 40,000 | 160.0 | 160.4 | 0.4338 ± 0.0000 | -11840.8 ± 55.5 | 64.9 ± 0.7 |  |
| 2 | Stage 2: indent at 10 m/s, R 2 nm, travel 20 nm | done | 400,000 | 160.0 | 160.1 | 0.1547 ± 0.0942 | -11857.2 ± 507.5 | 57.7 ± 1.7 | **yes** |
