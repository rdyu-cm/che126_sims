# pe_cg_amorph_n40_c1500_s1 / cool

- status: **finished** (manifest: finished), node rdyu-rog, started 2026-10-25 19:02 PDT, ended 2026-10-25 22:01 PDT
- progress: 100.0% of 4,000,000 MD steps; 8/8 segments done
- speed: 312.74 ns/day (362.0 steps/s, Performance line of segment 8)
- log updated 2026-10-25 22:01 PDT (4.5 d ago); report 2026-10-30 10:10 PDT on rdyu-rog
- checks: drift seg 3,6,7,8; hyst max 0.11%

## Segments

Means ± SEM over the second half of each completed segment; drift = density halves of that window differ by > 2 SEM.

| # | segment | state | steps | T set (°C) | T (°C) | density (g/cm³) | H (kcal/mol) | drift |
|---|---|---|---|---|---|---|---|---|
| 1 | Stage 1 cool 1/8 (474.8 K) | done | 500,000 | 201.6 | 201.6 | 0.7417 ± 0.0001 | -453.2 ± 15.5 | no |
| 2 | Stage 1 cool 2/8 (449.5 K) | done | 500,000 | 176.4 | 176.3 | 0.7552 ± 0.0001 | -4425.9 ± 14.9 | no |
| 3 | Stage 1 cool 3/8 (424.3 K) | done | 500,000 | 151.2 | 151.2 | 0.7681 ± 0.0001 | -8324.9 ± 14.6 | **yes** |
| 4 | Stage 1 cool 4/8 (399.1 K) | done | 500,000 | 125.9 | 126.0 | 0.7816 ± 0.0001 | -12348.8 ± 14.3 | no |
| 5 | Stage 1 cool 5/8 (373.8 K) | done | 500,000 | 100.7 | 100.8 | 0.7952 ± 0.0001 | -16418.8 ± 13.5 | no |
| 6 | Stage 1 cool 6/8 (348.6 K) | done | 500,000 | 75.5 | 75.5 | 0.8090 ± 0.0001 | -20590.4 ± 13.2 | **yes** |
| 7 | Stage 1 cool 7/8 (323.4 K) | done | 500,000 | 50.2 | 50.3 | 0.8230 ± 0.0000 | -24794.1 ± 12.7 | **yes** |
| 8 | Stage 1 cool 8/8 (298.1 K) | done | 500,000 | 25.0 | 25.0 | 0.8376 ± 0.0000 | -29178.0 ± 11.9 | **yes** |

## Cooling (prep step-cool) vs heating (sweep) density

| cool step | T (K) | ρ cool | ρ sweep (interp.) | Δ (%) |
|---|---|---|---|---|
| 1 | 474.8 | 0.7417 ± 0.0001 | outside sweep |  |
| 2 | 449.5 | 0.7552 ± 0.0001 | outside sweep |  |
| 3 | 424.3 | 0.7681 ± 0.0001 | 0.7689 | -0.111 |
| 4 | 399.1 | 0.7816 ± 0.0001 | 0.7824 | -0.106 |
| 5 | 373.8 | 0.7952 ± 0.0001 | 0.7957 | -0.073 |
| 6 | 348.6 | 0.8090 ± 0.0001 | 0.8094 | -0.052 |
| 7 | 323.4 | 0.8230 ± 0.0000 | 0.8235 | -0.054 |
| 8 | 298.1 | 0.8376 ± 0.0000 | 0.8382 | -0.070 |

## Plots

**step-cool density vs T (sweep overlaid once it exists)**

![step-cool density vs T (sweep overlaid once it exists)](progress_cool_vs_sweep.png)

**density and PotEng vs time (segment starts marked)**

![density and PotEng vs time (segment starts marked)](progress_timeline.png)

