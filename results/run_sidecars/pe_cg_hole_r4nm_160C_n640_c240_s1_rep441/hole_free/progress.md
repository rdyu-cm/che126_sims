# pe_cg_hole_r4nm_160C_n640_c240_s1_rep441 / hole_free

- status: **cancelled/killed?** (manifest: started), node rdyu-server, started 2026-11-09 19:02 UTC
- progress: 77.2% of 4,000,000 MD steps; 2/3 segments done; current: 3 Stage 3: hold at 160 C
- speed: 9.95 ns/day (11.5 steps/s, running segment (last hour of thermo))
- log updated 2026-11-13 17:40 UTC (10.0 d ago); report 2026-11-23 18:50 UTC on rdyu-server

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: inflate 10000 ps NVT at 433.15 K, radial push r0 0 | done | 1,000,000 | 160.0 | 160.0 | 0.1864 ± 0.0000 | -11328.4 ± 100.1 | 22.0 ± 0.9 |  |
| 2 | Stage 2: hold at R 10000 ps NVT at 433.15 K, push at r0 = 40 A | done | 1,000,000 | 160.0 | 160.0 | 0.1864 ± 0.0000 | -11124.3 ± 40.4 | 15.2 ± 0.4 |  |
| 3 | Stage 3: hold at 160 C | running | 1,086,700/2,000,000 | 160.0 |  |  |  |  |  |
