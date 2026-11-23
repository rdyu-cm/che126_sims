# pe_cg_crystal_7x10x27_s1 / tensile_160C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-17 02:09 PST, ended 2026-11-17 04:39 PST
- progress: 100.0% of 1,000,000 MD steps; 2/2 segments done
- speed: 96.87 ns/day (112.1 steps/s, Performance line of segment 2)
- log updated 2026-11-17 04:39 PST (6.3 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 160 C, 1e8 /s | done | 500,000 | 160.0 | 159.9 | 0.8198 ± 0.0029 | -4208.1 ± 83.6 | no |
| 2 | Segment 2: tensile along y at 160 C, 1e8 /s | done | 500,000 | 160.0 | 160.0 | 0.8043 ± 0.0031 | -3384.6 ± 127.6 | **yes** |
