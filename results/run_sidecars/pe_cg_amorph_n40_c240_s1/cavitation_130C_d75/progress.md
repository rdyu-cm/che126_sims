# pe_cg_amorph_n40_c240_s1 / cavitation_130C_d75

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-09 20:35 PST, ended 2026-11-09 21:03 PST
- progress: 100.0% of 260,000 MD steps; 1/1 segments done
- speed: 135.20 ns/day (156.5 steps/s, Performance line of segment 1)
- log updated 2026-11-09 21:03 PST (13.6 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: triaxial tension at 130 C, 1e8 /s per axis | done | 260,000 | 130.0 | 130.4 | 0.4589 ± 0.0269 | -1703.1 ± 69.6 | -14.9 ± 0.6 | **yes** |
