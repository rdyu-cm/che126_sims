# Hole: pe_cg_hole_r3nm_90C_n320_c240_s1_rep222 / hole_free

Nominal R 3 nm at 90 C, film 13.13 nm (R/h = 0.23), ligament 7.07 nm; variant: free.

Inflate 10 ns + push hold 10 ns (indent, K 0.5); grid `90h`; frames every 50 ps. Time 0 = start of production.

## Summary

| quantity | value |
|---|---|
| R_eff after inflation (last 20% of the push hold) | 3.08 nm |
| R_min after inflation | 2.91 nm |
| R_eff at t0 | 3.11 nm |
| t_close (R_min < 3 A for 5 frames) | 0.13 ns |
| dR_eff/dt, first 5 ns | -13.065 ± 0.222 nm/ns |
| dR_eff/dt, open period | -13.065 ± 0.222 nm/ns |
| final R_eff / R_min | 0.00 / 0.00 nm |
| film thickness t0 / final | 16.68 / 13.18 nm |

## Free shell

- beads with 3 < r < 5.5 nm at t0: 10923; areal density / far film: 0.855.
- bead MSD from t0 (COM removed): 1 ns: 488.5 A², 10 ns: 1239.6 A², end: 1754.7 A² (end = 20.00 ns)

## Per production segment (second half)

| # | kind | T (C) | scaffold | R_eff (nm) | R_min (nm) | open |
|---|---|---|---|---|---|---|
| 1 | hold | 90 | - | 0.00 | 0.00 | no |

## Caveats

- The scaffold is imposed harmonic tethers (fix spring/self) on the film outside R + d, a stand-in for the semicrystalline network that holds real separator pores open; it is not crystallinity, and its release is an emulation of melting, not a prediction of the shutdown temperature.
- The free film is the post-shutdown limit (a hole in an amorphous melt-like film).
- CG time is not real time: SDK PE chains diffuse ≈ 4.07× faster than real PE (Hall et al. 2019; docs/experiment_comparison.md), so MSD, D_COM, P2 and relaxation times are model times (not rescaled); multiply chain-motion times by 4.07 before comparing with experiment. The 4.07 factor is for chain diffusion and is not established for hole closure: compare hole runs with each other, not with experiment.
- All holes here have R < h (R/h <= 0.31), so closure is expected from the energy balance (R_c proportional to h, prefactor ~0.3-1 depending on rim geometry; Taylor & Michael 1973, Ilton et al. 2016): these runs measure closure kinetics (viscous scale ~ eta R / gamma), not the opening threshold.
- Finite size: the film is periodic in x, y; the ligament between the hole and its periodic images is L - 2R (given above; R = 4 nm leaves ~5 nm).
- gamma (and so the closure speed) depends on the plain LJ cutoff without tail correction (D48).

Figures: `hole_radius.png`, `hole_maps.png`, `thickness.png`
