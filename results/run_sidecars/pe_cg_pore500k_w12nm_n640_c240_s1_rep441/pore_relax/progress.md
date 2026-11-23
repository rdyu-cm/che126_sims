# pe_cg_pore500k_w12nm_n640_c240_s1_rep441 / pore_relax

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-06 02:23 PST, ended 2026-11-06 06:36 PST
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 28.45 ns/day (32.9 steps/s, Performance line of segment 2)
- log updated 2026-11-06 06:36 PST (17.2 d ago); report 2026-11-23 10:50 PST on rdyu-rog

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the opened slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface relaxation 5000 ps NVT at 500 K, box fixed | done | 500,000 | 226.9 | 226.9 | 0.2610 ± 0.0000 | 15609.8 ± 97.7 | 22.9 ± 0.2 |  |
