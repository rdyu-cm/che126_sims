# pe_ua_crystal_7x10x40_s1 / tensile_90C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-18 02:51 PST, ended 2026-11-18 07:01 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 5.79 ns/day (33.5 steps/s, Performance line of segment 2)
- log updated 2026-11-18 07:01 PST (5.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 90 C, 1e9 /s | done | 250,000 | 90.0 | 90.0 | 0.9637 ± 0.0051 | 7412.1 ± 268.9 | **yes** |
| 2 | Segment 2: tensile along y at 90 C, 1e9 /s | done | 250,000 | 90.0 | 89.7 | 0.9678 ± 0.0040 | 7327.8 ± 244.9 | **yes** |
