# pe_ua_crystal_7x10x40_s1 / crystal_fine_b

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-20 19:40 PST, ended 2026-11-20 23:19 PST
- progress: 100.0% of 4,000,000 MD steps; 5/5 segments done
- speed: 52.56 ns/day (304.2 steps/s, Performance line of segment 5)
- log updated 2026-11-20 23:19 PST (2.5 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2,3,4

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the lattice with the box relaxed | done | min |  |  |  |  |  |
| 2 | seg 01 hold 75 C | done | 1,000,000 | 75.0 | 75.0 | 1.0024 ± 0.0001 | 5413.6 ± 4.3 | **yes** |
| 3 | seg 02 hold 85 C | done | 1,000,000 | 85.0 | 84.9 | 0.9992 ± 0.0002 | 6195.8 ± 11.7 | **yes** |
| 4 | seg 03 hold 100 C | done | 1,000,000 | 100.0 | 100.0 | 0.9949 ± 0.0001 | 7346.4 ± 4.6 | **yes** |
| 5 | seg 04 hold 110 C | done | 1,000,000 | 110.0 | 110.0 | 0.9925 ± 0.0001 | 8063.8 ± 4.7 | no |
