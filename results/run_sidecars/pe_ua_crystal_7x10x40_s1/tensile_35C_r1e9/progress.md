# pe_ua_crystal_7x10x40_s1 / tensile_35C_r1e9

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-21 02:03 PST, ended 2026-11-21 02:47 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 33.03 ns/day (191.2 steps/s, Performance line of segment 2)
- log updated 2026-11-21 02:47 PST (2.3 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: tensile along x at 35 C, 1e9 /s | done | 250,000 | 35.0 | 34.9 | 0.9812 ± 0.0043 | 2659.3 ± 215.5 | **yes** |
| 2 | Segment 2: tensile along y at 35 C, 1e9 /s | done | 250,000 | 35.0 | 35.1 | 0.9898 ± 0.0068 | 1223.2 ± 96.0 | no |
