# pe_ua_crystal_7x10x40_s1 / tensile_120C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-21 07:39 PST, ended 2026-11-21 08:20 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 35.62 ns/day (206.1 steps/s, Performance line of segment 2)
- log updated 2026-11-21 08:20 PST (2.1 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 120 C, 1e9 /s | done | 250,000 | 120.0 | 120.0 | 0.9541 ± 0.0049 | 10017.3 ± 249.5 | **yes** |
| 2 | Segment 2: tensile along y at 120 C, 1e9 /s | done | 250,000 | 120.0 | 119.9 | 0.9569 ± 0.0045 | 9884.1 ± 251.6 | **yes** |
