# pe_cg_amorph_n40_c240_s1 / cavitation_130C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-09 19:02 PST, ended 2026-11-09 19:05 PST
- progress: 100.0% of 26,000 MD steps; 1/1 segments done
- speed: 132.71 ns/day (153.6 steps/s, Performance line of segment 1)
- log updated 2026-11-09 19:05 PST (13.7 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: triaxial tension at 130 C, 1e9 /s per axis | done | 26,000 | 130.0 | 129.8 | 0.4549 ± 0.0267 | -2101.0 ± 14.8 | 0.5 ± 1.7 | **yes** |
