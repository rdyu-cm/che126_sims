# pe_ua_crystal_7x10x40_s1 / tensile_130C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-18 07:01 PST, ended 2026-11-18 11:08 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 5.81 ns/day (33.6 steps/s, Performance line of segment 2)
- log updated 2026-11-18 11:08 PST (5.0 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 130 C, 1e9 /s | done | 250,000 | 130.0 | 130.1 | 0.9473 ± 0.0054 | 11217.5 ± 269.1 | **yes** |
| 2 | Segment 2: tensile along y at 130 C, 1e9 /s | done | 250,000 | 130.0 | 129.8 | 0.9515 ± 0.0045 | 10925.8 ± 229.7 | **yes** |
