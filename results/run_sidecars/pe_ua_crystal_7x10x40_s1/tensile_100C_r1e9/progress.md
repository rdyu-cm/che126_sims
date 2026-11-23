# pe_ua_crystal_7x10x40_s1 / tensile_100C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-21 06:18 PST, ended 2026-11-21 06:59 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 35.50 ns/day (205.4 steps/s, Performance line of segment 2)
- log updated 2026-11-21 06:59 PST (2.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 100 C, 1e9 /s | done | 250,000 | 100.0 | 100.1 | 0.9622 ± 0.0049 | 8194.9 ± 263.1 | **yes** |
| 2 | Segment 2: tensile along y at 100 C, 1e9 /s | done | 250,000 | 100.0 | 100.0 | 0.9642 ± 0.0043 | 8204.1 ± 236.0 | **yes** |
