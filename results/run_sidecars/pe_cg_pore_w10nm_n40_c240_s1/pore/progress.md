# pe_cg_pore_w10nm_n40_c240_s1 / pore

- status: **cancelled/killed?** (manifest: started), node rdyu-rog, started 2026-10-26 09:59 PDT
- progress: 5.6% of 21,200,000 MD steps; 3/28 segments done; current: 4 Stage 3 cool 2/8 (449.5 K)
- speed: 294.46 ns/day (340.8 steps/s, running segment (last hour of thermo))
- log updated 2026-10-26 10:56 PDT (4.0 d ago); report 2026-10-30 10:10 PDT on rdyu-rog

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the narrowed slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface re-relaxation 2000 ps NVT at 500 K after narrowing | done | 200,000 | 226.9 | 226.8 | 0.2964 ± 0.0000 | 986.3 ± 10.7 | 21.0 ± 1.1 |  |
| 3 | Stage 3 cool 1/8 (474.8 K) | done | 500,000 | 201.6 | 201.7 | 0.3001 ± 0.0000 | 314.6 ± 6.9 | 26.0 ± 0.7 |  |
| 4 | Stage 3 cool 2/8 (449.5 K) | running | 488,500/500,000 | 176.4 |  |  |  |  |  |
| 5 | Stage 3 cool 3/8 (424.3 K) | pending | 500,000 | 151.2 |  |  |  |  |  |
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
