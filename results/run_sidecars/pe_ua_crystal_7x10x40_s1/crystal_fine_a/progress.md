# pe_ua_crystal_7x10x40_s1 / crystal_fine_a

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-20 16:01 PST, ended 2026-11-20 19:40 PST
- progress: 100.0% of 4,000,000 MD steps; 5/5 segments done
- speed: 52.63 ns/day (304.6 steps/s, Performance line of segment 5)
- log updated 2026-11-20 19:40 PST (2.6 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 2

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the lattice with the box relaxed | done | min |  |  |  |  |  |
| 2 | seg 01 hold 35 C | done | 1,000,000 | 35.0 | 35.1 | 1.0121 ± 0.0002 | 2527.4 ± 3.7 | **yes** |
| 3 | seg 02 hold 45 C | done | 1,000,000 | 45.0 | 45.0 | 1.0088 ± 0.0001 | 3234.9 ± 3.9 | no |
| 4 | seg 03 hold 55 C | done | 1,000,000 | 55.0 | 55.0 | 1.0060 ± 0.0001 | 3981.3 ± 4.4 | no |
| 5 | seg 04 hold 65 C | done | 1,000,000 | 65.0 | 64.8 | 1.0036 ± 0.0001 | 4686.3 ± 4.1 | no |
