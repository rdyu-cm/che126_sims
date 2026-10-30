# pe_cg_pore_w3nm_n40_c240_s1 / pore

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-10-26 16:36 UTC
- progress: 7.1% of 21,200,000 MD steps; 4/28 segments done; current: 5 Stage 3 cool 3/8 (424.3 K)
- speed: 265.52 ns/day (307.3 steps/s, running segment (last hour of thermo))
- log updated 2026-10-26 17:56 UTC (4.0 d ago); report 2026-10-30 17:20 UTC on rdyu-server

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the narrowed slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface re-relaxation 2000 ps NVT at 500 K after narrowing | done | 200,000 | 226.9 | 227.1 | 0.5168 ± 0.0000 | 997.7 ± 10.1 | 23.0 ± 1.0 |  |
| 3 | Stage 3 cool 1/8 (474.8 K) | done | 500,000 | 201.6 | 201.6 | 0.5232 ± 0.0000 | 293.6 ± 6.3 | 26.6 ± 0.6 |  |
| 4 | Stage 3 cool 2/8 (449.5 K) | done | 500,000 | 176.4 | 176.4 | 0.5298 ± 0.0000 | -321.4 ± 6.5 | 27.3 ± 0.7 |  |
| 5 | Stage 3 cool 3/8 (424.3 K) | running | 299,800/500,000 | 151.2 |  |  |  |  |  |
| 6 | Stage 3 cool 4/8 (399.1 K) | pending | 500,000 | 125.9 |  |  |  |  |  |
| 7 | Stage 3 cool 5/8 (373.8 K) | pending | 500,000 | 100.7 |  |  |  |  |  |
| 8 | Stage 3 cool 6/8 (348.6 K) | pending | 500,000 | 75.5 |  |  |  |  |  |
| 9 | Stage 3 cool 7/8 (323.4 K) | pending | 500,000 | 50.2 |  |  |  |  |  |
| 10 | Stage 3 cool 8/8 (298.1 K) | pending | 500,000 | 25.0 |  |  |  |  |  |
| 11 | seg 01 hold 25 C | pending | 2,500,000 | 25.0 |  |  |  |  |  |
| 12 | seg 02 step 35 C | pending | 500,000 | 35.0 |  |  |  |  |  |
| 13 | seg 03 step 45 C | pending | 500,000 | 45.0 |  |  |  |  |  |
| 14 | seg 04 step 55 C | pending | 500,000 | 55.0 |  |  |  |  |  |
| 15 | seg 05 step 65 C | pending | 500,000 | 65.0 |  |  |  |  |  |
| 16 | seg 06 step 75 C | pending | 500,000 | 75.0 |  |  |  |  |  |
| 17 | seg 07 step 85 C | pending | 500,000 | 85.0 |  |  |  |  |  |
| 18 | seg 08 step 90 C | pending | 500,000 | 90.0 |  |  |  |  |  |
| 19 | seg 09 hold 90 C | pending | 2,500,000 | 90.0 |  |  |  |  |  |
| 20 | seg 10 step 100 C | pending | 500,000 | 100.0 |  |  |  |  |  |
| 21 | seg 11 step 110 C | pending | 500,000 | 110.0 |  |  |  |  |  |
| 22 | seg 12 step 120 C | pending | 500,000 | 120.0 |  |  |  |  |  |
| 23 | seg 13 step 130 C | pending | 500,000 | 130.0 |  |  |  |  |  |
| 24 | seg 14 hold 130 C | pending | 2,500,000 | 130.0 |  |  |  |  |  |
| 25 | seg 15 step 140 C | pending | 500,000 | 140.0 |  |  |  |  |  |
| 26 | seg 16 step 150 C | pending | 500,000 | 150.0 |  |  |  |  |  |
| 27 | seg 17 step 160 C | pending | 500,000 | 160.0 |  |  |  |  |  |
| 28 | seg 18 hold 160 C | pending | 2,500,000 | 160.0 |  |  |  |  |  |
