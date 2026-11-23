# pe_ua_crystal_7x10x40_s1 / tensile_75C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-21 04:55 PST, ended 2026-11-21 05:37 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 34.47 ns/day (199.5 steps/s, Performance line of segment 2)
- log updated 2026-11-21 05:37 PST (2.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 75 C, 1e9 /s | done | 250,000 | 75.0 | 74.8 | 0.9704 ± 0.0046 | 5927.6 ± 254.3 | **yes** |
| 2 | Segment 2: tensile along y at 75 C, 1e9 /s | done | 250,000 | 75.0 | 75.2 | 0.9863 ± 0.0022 | 4737.7 ± 45.5 | no |
