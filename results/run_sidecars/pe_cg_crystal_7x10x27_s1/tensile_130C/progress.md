# pe_cg_crystal_7x10x27_s1 / tensile_130C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-16 23:37 PST, ended 2026-11-17 02:09 PST
- progress: 100.0% of 1,000,000 MD steps; 2/2 segments done
- speed: 94.58 ns/day (109.5 steps/s, Performance line of segment 2)
- log updated 2026-11-17 02:09 PST (6.4 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 130 C, 1e8 /s | done | 500,000 | 130.0 | 130.0 | 0.8395 ± 0.0056 | -5305.9 ± 163.7 | **yes** |
| 2 | Segment 2: tensile along y at 130 C, 1e8 /s | done | 500,000 | 130.0 | 130.0 | 0.8381 ± 0.0031 | -5278.7 ± 96.5 | **yes** |
