# pe_ua_crystal_7x10x40_s1 / tensile_150C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-21 09:00 PST, ended 2026-11-21 09:40 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 36.02 ns/day (208.5 steps/s, Performance line of segment 2)
- log updated 2026-11-21 09:40 PST (2.0 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 150 C, 1e9 /s | done | 250,000 | 150.0 | 149.9 | 0.9330 ± 0.0056 | 13485.8 ± 263.3 | **yes** |
| 2 | Segment 2: tensile along y at 150 C, 1e9 /s | done | 250,000 | 150.0 | 150.3 | 0.9380 ± 0.0049 | 13275.2 ± 250.4 | **yes** |
