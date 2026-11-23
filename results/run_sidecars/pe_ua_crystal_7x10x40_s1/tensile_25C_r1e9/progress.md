# pe_ua_crystal_7x10x40_s1 / tensile_25C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-17 22:36 PST, ended 2026-11-18 02:51 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 5.66 ns/day (32.7 steps/s, Performance line of segment 2)
- log updated 2026-11-18 02:51 PST (5.3 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 25 C, 1e9 /s | done | 250,000 | 25.0 | 25.1 | 0.9856 ± 0.0043 | 1838.1 ± 198.3 | **yes** |
| 2 | Segment 2: tensile along y at 25 C, 1e9 /s | done | 250,000 | 25.0 | 25.4 | 0.9994 ± 0.0023 | 907.0 ± 44.6 | no |
