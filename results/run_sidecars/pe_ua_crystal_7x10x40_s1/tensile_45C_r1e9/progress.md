# pe_ua_crystal_7x10x40_s1 / tensile_45C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-21 02:47 PST, ended 2026-11-21 03:30 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 33.71 ns/day (195.1 steps/s, Performance line of segment 2)
- log updated 2026-11-21 03:30 PST (2.3 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 45 C, 1e9 /s | done | 250,000 | 45.0 | 45.2 | 0.9786 ± 0.0041 | 3489.3 ± 218.5 | **yes** |
| 2 | Segment 2: tensile along y at 45 C, 1e9 /s | done | 250,000 | 45.0 | 45.0 | 0.9958 ± 0.0029 | 2848.0 ± 52.6 | **yes** |
