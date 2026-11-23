# pe_cg_amorph_n40_c240_s1 / tensile_130C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-31 04:50 PDT, ended 2026-10-31 10:54 PDT
- progress: 100.0% of 1,500,000 MD steps; 3/3 segments done
- speed: 60.65 ns/day (70.2 steps/s, Performance line of segment 3)
- log updated 2026-10-31 10:54 PDT (23.0 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 130 C, 1e8 /s | done | 500,000 | 130.0 | 130.0 | 0.7751 ± 0.0001 | -1988.5 ± 7.7 | no |
| 2 | Segment 2: tensile along y at 130 C, 1e8 /s | done | 500,000 | 130.0 | 130.0 | 0.7761 ± 0.0002 | -2057.2 ± 6.2 | **yes** |
| 3 | Segment 3: tensile along z at 130 C, 1e8 /s | done | 500,000 | 130.0 | 130.0 | 0.7747 ± 0.0001 | -2003.2 ± 13.1 | no |
