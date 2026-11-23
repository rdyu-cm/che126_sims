# pe_ua_pore500k_w10nm_n40_c240_s1 / pore_relax

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-03 21:54 PST, ended 2026-11-04 00:14 PST
- progress: 100.0% of 1,000,000 MD steps; 2/2 segments done
- speed: 20.62 ns/day (119.3 steps/s, Performance line of segment 2)
- log updated 2026-11-04 00:14 PST (19.4 d ago); report 2026-11-23 10:50 PST on rdyu-rog

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the opened slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface relaxation 2000 ps NVT at 500 K, box fixed | done | 1,000,000 | 226.9 | 226.8 | 0.2989 ± 0.0000 | 24496.8 ± 17.0 | 12.6 ± 6.2 |  |
