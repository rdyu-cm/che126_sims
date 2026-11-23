# pe_cg_film_160C_n640_c240_s1_rep441 / puncture_160C_v10_R2nm_p1

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-11 03:13 PST, ended 2026-11-11 08:18 PST
- progress: 100.0% of 168,960 MD steps; 2/2 segments done
- speed: 8.04 ns/day (9.3 steps/s, Performance line of segment 2)
- log updated 2026-11-11 08:18 PST (12.1 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: settle 200 ps NVT at 433.15 K, indenter clear of the film | done | 20,000 | 160.0 | 160.2 | 0.4338 ± 0.0000 | -11859.0 ± 72.5 | 26.1 ± 0.7 |  |
| 2 | Stage 2: indent at 10 m/s, R 2 nm, travel 14.896 nm | done | 148,960 | 160.0 | 160.0 | 0.2352 ± 0.0262 | -11862.4 ± 57.7 | 27.8 ± 0.4 | **yes** |
