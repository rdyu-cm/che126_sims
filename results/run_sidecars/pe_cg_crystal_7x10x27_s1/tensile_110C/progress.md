# pe_cg_crystal_7x10x27_s1 / tensile_110C

- status: **finished** (manifest: finished), node rdyu-server, started 2026-11-22 00:02 UTC, ended 2026-11-22 03:34 UTC
- progress: 100.0% of 1,000,000 MD steps; 2/2 segments done
- speed: 66.85 ns/day (77.4 steps/s, Performance line of segment 2)
- log updated 2026-11-22 03:34 UTC (39.3 h ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 110 C, 1e8 /s | done | 500,000 | 110.0 | 110.2 | 0.8448 ± 0.0024 | -5843.0 ± 70.6 | no |
| 2 | Segment 2: tensile along y at 110 C, 1e8 /s | done | 500,000 | 110.0 | 110.1 | 0.8430 ± 0.0024 | -5782.7 ± 81.0 | **yes** |
