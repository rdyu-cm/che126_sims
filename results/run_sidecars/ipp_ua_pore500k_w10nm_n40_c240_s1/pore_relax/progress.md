# ipp_ua_pore500k_w10nm_n40_c240_s1 / pore_relax

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-03 21:54 PST, ended 2026-11-04 02:02 PST
- progress: 100.0% of 1,000,000 MD steps; 2/2 segments done
- speed: 11.97 ns/day (69.2 steps/s, Performance line of segment 2)
- log updated 2026-11-04 02:02 PST (19.4 d ago); report 2026-11-23 10:50 PST on rdyu-rog

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the opened slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface relaxation 2000 ps NVT at 500 K, box fixed | done | 1,000,000 | 226.9 | 226.9 | 0.3032 ± 0.0000 | 36099.7 ± 17.5 | 17.0 ± 6.7 |  |
