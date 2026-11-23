# pe_cg_crystal_7x10x27_s1 / tensile_160C_r1e9

- status: **finished** (manifest: finished), node rdyu-server, started 2026-11-23 17:30 UTC, ended 2026-11-23 17:44 UTC
- progress: 100.0% of 100,000 MD steps; 2/2 segments done
- speed: 104.75 ns/day (121.2 steps/s, Performance line of segment 2)
- log updated 2026-11-23 17:44 UTC (1.1 h ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 160 C, 1e9 /s | done | 50,000 | 160.0 | 160.1 | 0.8020 ± 0.0061 | -3613.4 ± 235.8 | **yes** |
| 2 | Segment 2: tensile along y at 160 C, 1e9 /s | done | 50,000 | 160.0 | 159.2 | 0.8060 ± 0.0031 | -3655.6 ± 121.6 | no |
