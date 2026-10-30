# pe_cg_pore500k_w10nm_n40_c240_s1 / pore_relax

- status: **finished** (manifest: finished), node rdyu-server, started 2026-10-26 23:51 UTC, ended 2026-10-27 00:18 UTC
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 266.65 ns/day (308.6 steps/s, Performance line of segment 2)
- log updated 2026-10-27 00:18 UTC (3.7 d ago); report 2026-10-30 17:20 UTC on rdyu-server

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the opened slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface relaxation 5000 ps NVT at 500 K, box fixed | done | 500,000 | 226.9 | 226.7 | 0.2941 ± 0.0000 | 938.3 ± 6.9 | 24.1 ± 0.7 |  |
