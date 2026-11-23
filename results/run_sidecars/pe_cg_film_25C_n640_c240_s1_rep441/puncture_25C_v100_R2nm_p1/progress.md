# pe_cg_film_25C_n640_c240_s1_rep441 / puncture_25C_v100_R2nm_p1

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-12 17:13 PST, ended 2026-11-12 18:17 PST
- progress: 100.0% of 33,929 MD steps; 2/2 segments done
- speed: 7.51 ns/day (8.7 steps/s, Performance line of segment 2)
- log updated 2026-11-12 18:17 PST (10.7 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 298.15 K, indenter clear of the film | done | 20,000 | 25.0 | 25.1 | 0.4702 ± 0.0000 | -69994.5 ± 26.6 | 35.1 ± 0.6 |  |
| 2 | Stage 2: indent at 100 m/s, R 2 nm, travel 13.929 nm | done | 13,929 | 25.0 | 25.1 | 0.4051 ± 0.0250 | -70979.2 ± 170.4 | 42.6 ± 2.0 | **yes** |
