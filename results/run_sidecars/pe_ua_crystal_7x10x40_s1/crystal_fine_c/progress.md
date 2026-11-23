# pe_ua_crystal_7x10x40_s1 / crystal_fine_c

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-20 23:19 PST, ended 2026-11-21 02:03 PST
- progress: 100.0% of 3,000,000 MD steps; 4/4 segments done
- speed: 52.82 ns/day (305.7 steps/s, Performance line of segment 4)
- log updated 2026-11-21 02:03 PST (2.4 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 4

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the lattice with the box relaxed | done | min |  |  |  |  |  |
| 2 | seg 01 hold 120 C | done | 1,000,000 | 120.0 | 119.9 | 0.9901 ± 0.0001 | 8797.0 ± 4.8 | no |
| 3 | seg 02 hold 140 C | done | 1,000,000 | 140.0 | 140.1 | 0.9837 ± 0.0001 | 10391.5 ± 5.1 | no |
| 4 | seg 03 hold 150 C | done | 1,000,000 | 150.0 | 150.1 | 0.9798 ± 0.0003 | 11218.4 ± 14.8 | **yes** |
