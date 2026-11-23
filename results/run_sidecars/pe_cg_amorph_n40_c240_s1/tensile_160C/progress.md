# pe_cg_amorph_n40_c240_s1 / tensile_160C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-30 17:19 PDT, ended 2026-10-30 22:54 PDT
- progress: 100.0% of 1,500,000 MD steps; 3/3 segments done
- speed: 64.44 ns/day (74.6 steps/s, Performance line of segment 3)
- log updated 2026-10-30 22:54 PDT (23.5 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 160 C, 1e8 /s | done | 500,000 | 160.0 | 159.9 | 0.7585 ± 0.0002 | -1217.6 ± 8.6 | no |
| 2 | Segment 2: tensile along y at 160 C, 1e8 /s | done | 500,000 | 160.0 | 159.8 | 0.7589 ± 0.0003 | -1227.9 ± 5.4 | **yes** |
| 3 | Segment 3: tensile along z at 160 C, 1e8 /s | done | 500,000 | 160.0 | 160.0 | 0.7589 ± 0.0002 | -1202.5 ± 7.4 | no |
