# pe_cg_amorph_n40_c240_s1 / tensile_25C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-30 11:34 PDT, ended 2026-10-30 17:19 PDT
- progress: 100.0% of 1,500,000 MD steps; 3/3 segments done
- speed: 63.73 ns/day (73.8 steps/s, Performance line of segment 3)
- log updated 2026-10-30 17:19 PDT (23.8 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1,2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 25 C, 1e8 /s | done | 500,000 | 25.0 | 25.0 | 0.8360 ± 0.0004 | -4918.2 ± 17.2 | **yes** |
| 2 | Segment 2: tensile along y at 25 C, 1e8 /s | done | 500,000 | 25.0 | 25.0 | 0.8343 ± 0.0002 | -4791.1 ± 5.7 | **yes** |
| 3 | Segment 3: tensile along z at 25 C, 1e8 /s | done | 500,000 | 25.0 | 24.9 | 0.8355 ± 0.0002 | -4879.3 ± 11.2 | no |
