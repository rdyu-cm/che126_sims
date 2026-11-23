# pe_cg_film_130C_n640_c240_s1_rep441 / puncture_130C_v10_R2nm_p1

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-10 21:38 PST, ended 2026-11-11 03:12 PST
- progress: 100.0% of 171,464 MD steps; 2/2 segments done
- speed: 7.39 ns/day (8.6 steps/s, Performance line of segment 2)
- log updated 2026-11-11 03:12 PST (12.3 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 403.15 K, indenter clear of the film | done | 20,000 | 130.0 | 129.8 | 0.4417 ± 0.0000 | -24527.3 ± 63.9 | 27.3 ± 1.7 |  |
| 2 | Stage 2: indent at 10 m/s, R 2 nm, travel 15.1464 nm | done | 151,464 | 130.0 | 130.0 | 0.2410 ± 0.0266 | -24569.4 ± 27.6 | 28.4 ± 0.3 | **yes** |
