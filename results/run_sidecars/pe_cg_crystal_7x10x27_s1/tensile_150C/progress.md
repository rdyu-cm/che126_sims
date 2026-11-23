# pe_cg_crystal_7x10x27_s1 / tensile_150C

- status: **finished** (manifest: finished), node rdyu-server, started 2026-11-22 02:33 UTC, ended 2026-11-22 05:43 UTC
- progress: 100.0% of 1,000,000 MD steps; 2/2 segments done
- speed: 82.39 ns/day (95.4 steps/s, Performance line of segment 2)
- log updated 2026-11-22 05:43 UTC (37.1 h ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 150 C, 1e8 /s | done | 500,000 | 150.0 | 150.0 | 0.8129 ± 0.0024 | -3919.4 ± 113.0 | no |
| 2 | Segment 2: tensile along y at 150 C, 1e8 /s | done | 500,000 | 150.0 | 150.0 | 0.8289 ± 0.0041 | -4561.4 ± 111.2 | **yes** |
