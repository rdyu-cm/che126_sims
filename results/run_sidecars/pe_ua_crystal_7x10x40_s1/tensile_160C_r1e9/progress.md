# pe_ua_crystal_7x10x40_s1 / tensile_160C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-18 11:08 PST, ended 2026-11-18 15:17 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 5.74 ns/day (33.2 steps/s, Performance line of segment 2)
- log updated 2026-11-18 15:16 PST (4.8 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 160 C, 1e9 /s | done | 250,000 | 160.0 | 160.0 | 0.9224 ± 0.0065 | 14863.9 ± 287.7 | **yes** |
| 2 | Segment 2: tensile along y at 160 C, 1e9 /s | done | 250,000 | 160.0 | 160.1 | 0.9258 ± 0.0059 | 14732.3 ± 292.5 | **yes** |
