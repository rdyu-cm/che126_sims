# pe_cg_film_160C_n640_c240_s1_rep441 / puncture_160C_v3_R2nm_c1

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-14 07:43 PST, ended 2026-11-14 23:55 PST
- progress: 100.0% of 516,532 MD steps; 2/2 segments done
- speed: 7.64 ns/day (8.8 steps/s, Performance line of segment 2)
- log updated 2026-11-14 23:55 PST (8.5 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 433.15 K, indenter clear of the film | done | 20,000 | 160.0 | 159.9 | 0.4338 ± 0.0000 | -12005.4 ± 58.3 | 64.2 ± 0.7 |  |
| 2 | Stage 2: indent at 3 m/s, R 2 nm, travel 14.89596 nm | done | 496,532 | 160.0 | 160.1 | 0.3343 ± 0.0588 | -11053.0 ± 213.1 | 58.4 ± 1.2 | **yes** |
