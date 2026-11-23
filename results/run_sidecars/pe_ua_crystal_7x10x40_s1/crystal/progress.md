# pe_ua_crystal_7x10x40_s1 / crystal

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-17 05:48 PST, ended 2026-11-17 22:36 PST
- progress: 100.0% of 4,000,000 MD steps; 5/5 segments done
- speed: 11.50 ns/day (66.6 steps/s, Performance line of segment 5)
- log updated 2026-11-17 22:36 PST (5.5 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 5

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the lattice with the box relaxed | done | min |  |  |  |  |  |
| 2 | seg 01 hold 25 C | done | 1,000,000 | 25.0 | 24.9 | 1.0139 ± 0.0002 | 1767.2 ± 3.7 | no |
| 3 | seg 02 hold 90 C | done | 1,000,000 | 90.0 | 89.8 | 0.9974 ± 0.0001 | 6499.5 ± 5.0 | no |
| 4 | seg 03 hold 130 C | done | 1,000,000 | 130.0 | 130.0 | 0.9868 ± 0.0001 | 9578.1 ± 5.0 | no |
| 5 | seg 04 hold 160 C | done | 1,000,000 | 160.0 | 160.0 | 0.9762 ± 0.0001 | 12113.1 ± 11.1 | **yes** |
