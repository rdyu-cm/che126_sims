# pe_cg_pore500k_w10nm_n40_c240_s1 / pore_relax

- status: **finished** (manifest: finished), node rdyu-server, started 2026-10-26 16:07 UTC, ended 2026-10-26 16:32 UTC
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 288.40 ns/day (333.8 steps/s, Performance line of segment 2)
- log updated 2026-10-26 16:32 UTC (4.0 d ago); report 2026-10-30 17:20 UTC on rdyu-server

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the opened slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface relaxation 5000 ps NVT at 500 K, box fixed | done | 500,000 | 226.9 | 226.7 | 0.2899 ± 0.0000 | 968.8 ± 6.7 | 24.1 ± 0.6 |  |
