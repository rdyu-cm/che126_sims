# Hole: pe_cg_hole_r3nm_25C_n320_c240_s1_rep222 / hole_ramp_held

Nominal R 3 nm at 25 C, film 12.94 nm (R/h = 0.23), ligament 6.88 nm; variant: annulus d=2.5 nm, held, ramp.

Inflate 20 ns + push hold 10 ns (indent, K 0.5); grid `25h,35,45,55,65,75,85,90h,100,110,120,130h,140,150,160h`; frames every 50 ps. Time 0 = start of production.

## Summary

| quantity | value |
|---|---|
| R_eff after inflation (last 20% of the push hold) | 3.03 nm |
| R_min after inflation | 2.87 nm |
| R_eff at t0 | 3.05 nm |
| t_close (R_min < 3 A for 5 frames) | 25.60 ns |
| dR_eff/dt, first 5 ns | -0.017 ± 0.001 nm/ns |
| dR_eff/dt, open period | 0.004 ± 0.000 nm/ns |
| final R_eff / R_min | 3.36 / 0.00 nm |
| film thickness t0 / final | 16.24 / 16.23 nm |

## Scaffold

- annulus, d = 2.5 nm, K = 5 kcal/mol/A²: 13808 tethered beads (53.9%); LAMMPS group count 13808 (matches).
- nearest tethered bead to the axis at t0: 55.00 A (>= R + d: ok); minimum while held: 53.08 A.

## Free shell

- beads with 3 < r < 5.5 nm at t0: 11581; areal density / far film: 0.889.
- bead MSD from t0 (COM removed): 1 ns: 66.8 A², 10 ns: 273.8 A², end: 845.0 A² (end = 68.00 ns)

## Per production segment (second half)

| # | kind | T (C) | scaffold | R_eff (nm) | R_min (nm) | open |
|---|---|---|---|---|---|---|
| 1 | hold | 25 | held | 2.92 | 2.19 | yes |
| 2 | step | 35 | held | 2.92 | 1.98 | yes |
| 3 | step | 45 | held | 2.94 | 1.95 | yes |
| 4 | step | 55 | held | 2.94 | 1.91 | yes |
| 5 | step | 65 | held | 2.97 | 1.80 | yes |
| 6 | step | 75 | held | 3.01 | 1.80 | yes |
| 7 | step | 85 | held | 2.98 | 1.82 | yes |
| 8 | step | 90 | held | 3.09 | 1.44 | yes |
| 9 | hold | 90 | held | 3.31 | 0.00 | no |
| 10 | step | 100 | held | 3.32 | 0.00 | no |
| 11 | step | 110 | held | 3.32 | 0.00 | no |
| 12 | step | 120 | held | 3.33 | 0.00 | no |
| 13 | step | 130 | held | 3.36 | 0.00 | no |
| 14 | hold | 130 | held | 3.33 | 0.00 | no |
| 15 | step | 140 | held | 3.36 | 0.00 | no |
| 16 | step | 150 | held | 3.39 | 0.00 | no |
| 17 | step | 160 | held | 3.37 | 0.00 | no |
| 18 | hold | 160 | held | 3.35 | 0.00 | no |

## Caveats

- The scaffold is imposed harmonic tethers (fix spring/self) on the film outside R + d, a stand-in for the semicrystalline network that holds real separator pores open; it is not crystallinity, and its release is an emulation of melting, not a prediction of the shutdown temperature.
- The free film is the post-shutdown limit (a hole in an amorphous melt-like film).
- CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; docs/experiment_comparison.md), so MSD, D_COM, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment. The 4.07 factor is for chain diffusion and is not established for hole closure: compare hole runs with each other, not with experiment.
- All holes here have R < h (R/h <= 0.31), so closure is expected from the energy balance (R_c proportional to h, prefactor ~0.3-1 depending on rim geometry; Taylor & Michael 1973, Ilton et al. 2016): these runs measure closure kinetics (viscous scale ~ eta R / gamma), not the opening threshold.
- Finite size: the film is periodic in x, y; the ligament between the hole and its periodic images is L - 2R (given above; R = 4 nm leaves ~5 nm).
- gamma (and so the closure speed) depends on the plain LJ cutoff without tail correction (D48).

Figures: `hole_radius.png`, `hole_maps.png`, `thickness.png`
