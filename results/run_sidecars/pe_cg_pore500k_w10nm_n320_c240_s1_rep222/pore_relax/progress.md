# pe_cg_pore500k_w10nm_n320_c240_s1_rep222 / pore_relax

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-29 10:38 PDT, ended 2026-10-29 11:02 PDT
- progress: 100.0% of 500,000 MD steps; 2/2 segments done
- speed: 291.56 ns/day (337.5 steps/s, Performance line of segment 2)
- log updated 2026-10-29 11:02 PDT (23.1 h ago); report 2026-10-30 10:10 PDT on rdyu-rog

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1: minimize the opened slab | done | min |  |  |  |  |  |  |
| 2 | Stage 2: surface relaxation 5000 ps NVT at 500 K, box fixed | done | 500,000 | 226.9 | 226.8 | 0.4176 ± 0.0000 | 5864.2 ± 21.2 | 22.9 ± 0.5 |  |
