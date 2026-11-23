# pe_cg_amorph_n40_c240_s1 / cavitation_130C_d150

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-09 20:07 PST, ended 2026-11-09 20:35 PST
- progress: 100.0% of 260,000 MD steps; 1/1 segments done
- speed: 131.99 ns/day (152.8 steps/s, Performance line of segment 1)
- log updated 2026-11-09 20:35 PST (13.6 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: triaxial tension at 130 C, 1e8 /s per axis | done | 260,000 | 130.0 | 129.9 | 0.4596 ± 0.0269 | -1711.2 ± 53.8 | 3.4 ± 2.2 | **yes** |
