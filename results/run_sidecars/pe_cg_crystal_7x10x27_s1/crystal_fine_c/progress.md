# pe_cg_crystal_7x10x27_s1 / crystal_fine_c

- status: **finished** (manifest: finished), node rdyu-server, started 2026-11-21 06:52 UTC, ended 2026-11-21 12:25 UTC
- progress: 100.0% of 3,000,000 MD steps; 4/4 segments done
- speed: 137.56 ns/day (159.2 steps/s, Performance line of segment 4)
- log updated 2026-11-21 12:25 UTC (2.3 d ago); report 2026-11-23 18:50 UTC on rdyu-server
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the lattice with the box relaxed | done | min |  |  |  |  |  |
| 2 | seg 01 hold 120 C | done | 1,000,000 | 120.0 | 120.0 | 0.8772 ± 0.0001 | -6052.1 ± 1.9 | **yes** |
| 3 | seg 02 hold 140 C | done | 1,000,000 | 140.0 | 139.9 | 0.8655 ± 0.0001 | -5420.9 ± 1.6 | no |
| 4 | seg 03 hold 150 C | done | 1,000,000 | 150.0 | 150.0 | 0.8594 ± 0.0001 | -5097.5 ± 2.1 | no |
