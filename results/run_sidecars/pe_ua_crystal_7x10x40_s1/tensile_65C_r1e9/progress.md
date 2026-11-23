# pe_ua_crystal_7x10x40_s1 / tensile_65C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-21 04:13 PST, ended 2026-11-21 04:55 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 34.20 ns/day (197.9 steps/s, Performance line of segment 2)
- log updated 2026-11-21 04:55 PST (2.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 65 C, 1e9 /s | done | 250,000 | 65.0 | 65.1 | 0.9737 ± 0.0047 | 5144.2 ± 247.8 | **yes** |
| 2 | Segment 2: tensile along y at 65 C, 1e9 /s | done | 250,000 | 65.0 | 65.0 | 0.9911 ± 0.0024 | 4369.6 ± 42.3 | **yes** |
