# pe_cg_amorph_n40_c240_s1 / cool

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-26 16:47 PDT, ended 2026-10-26 20:51 PDT
- progress: 100.0% of 4,000,000 MD steps; 8/8 segments done
- speed: 230.92 ns/day (267.3 steps/s, Performance line of segment 8)
- log updated 2026-10-26 20:51 PDT (3.6 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: drift seg 4,5,6,8; hyst max 0.11%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1 cool 1/8 (474.8 K) | done | 500,000 | 201.6 | 201.7 | 0.7367 ± 0.0002 | -124.7 ± 6.0 | no |
| 2 | Stage 1 cool 2/8 (449.5 K) | done | 500,000 | 176.4 | 176.2 | 0.7505 ± 0.0002 | -774.5 ± 6.2 | no |
| 3 | Stage 1 cool 3/8 (424.3 K) | done | 500,000 | 151.2 | 150.9 | 0.7639 ± 0.0002 | -1406.0 ± 5.7 | no |
| 4 | Stage 1 cool 4/8 (399.1 K) | done | 500,000 | 125.9 | 126.0 | 0.7777 ± 0.0002 | -2048.4 ± 5.8 | **yes** |
| 5 | Stage 1 cool 5/8 (373.8 K) | done | 500,000 | 100.7 | 100.8 | 0.7917 ± 0.0001 | -2718.3 ± 5.4 | **yes** |
| 6 | Stage 1 cool 6/8 (348.6 K) | done | 500,000 | 75.5 | 75.5 | 0.8056 ± 0.0001 | -3390.8 ± 5.3 | **yes** |
| 7 | Stage 1 cool 7/8 (323.4 K) | done | 500,000 | 50.2 | 50.4 | 0.8195 ± 0.0001 | -4056.0 ± 4.9 | no |
| 8 | Stage 1 cool 8/8 (298.1 K) | done | 500,000 | 25.0 | 24.8 | 0.8350 ± 0.0001 | -4797.8 ± 5.0 | **yes** |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7367 ± 0.0002 | outside sweep |  |
| 2 | 449.5 | 0.7505 ± 0.0002 | outside sweep |  |
| 3 | 424.3 | 0.7639 ± 0.0002 | 0.7648 | -0.112 |
| 4 | 399.1 | 0.7777 ± 0.0002 | 0.7779 | -0.034 |
| 5 | 373.8 | 0.7917 ± 0.0001 | 0.7920 | -0.031 |
| 6 | 348.6 | 0.8056 ± 0.0001 | 0.8060 | -0.054 |
| 7 | 323.4 | 0.8195 ± 0.0001 | 0.8199 | -0.049 |
| 8 | 298.1 | 0.8350 ± 0.0001 | 0.8346 | +0.044 |

## Plots

**step-cool density vs T (sweep overlaid once it exists)**

![step-cool density vs T (sweep overlaid once it exists)](progress_cool_vs_sweep.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

