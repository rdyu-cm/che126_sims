# pe_cg_amorph_n40_c240_s1 / cavitation_160C

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-11-09 21:03 PST, ended 2026-11-09 21:34 PST
- progress: 100.0% of 260,000 MD steps; 1/1 segments done
- speed: 121.55 ns/day (140.7 steps/s, Performance line of segment 1)
- log updated 2026-11-09 21:34 PST (13.6 d ago); report 2026-11-23 10:50 PST on rdyu-rog
- checks: drift seg 1

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM. γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] per surface.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | γ (mN/m) | drift |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Segment 1: triaxial tension at 160 C, 1e8 /s per axis | done | 260,000 | 160.0 | 159.8 | 0.4520 ± 0.0265 | -895.6 ± 26.1 | 7.7 ± 2.7 | **yes** |
