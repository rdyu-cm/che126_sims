# pe_cg_crystal_7x10x27_s1 / tensile_90C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-16 20:59 PST, ended 2026-11-16 23:37 PST
- progress: 100.0% of 1,000,000 MD steps; 2/2 segments done
- speed: 91.99 ns/day (106.5 steps/s, Performance line of segment 2)
- log updated 2026-11-16 23:37 PST (6.5 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 90 C, 1e8 /s | done | 500,000 | 90.0 | 90.1 | 0.8521 ± 0.0037 | -6424.5 ± 117.0 | **yes** |
| 2 | Segment 2: tensile along y at 90 C, 1e8 /s | done | 500,000 | 90.0 | 90.0 | 0.8531 ± 0.0036 | -6411.5 ± 115.3 | **yes** |
