# Hole: pe_cg_hole_r4nm_160C_n320_c240_s1_rep222 / hole_free

Nominal R 4 nm at 160 C, film 13.35 nm (R/h = 0.30), ligament 5.29 nm; variant: free.

Inflate 10 ns + push hold 10 ns (indent, K 0.5); grid `160h`; frames every 50 ps. Time 0 = start of production.

## Summary

| quantity | value |
|---|---|
| R_eff after inflation (last 20% of the push hold) | 4.43 nm |
| R_min after inflation | 4.10 nm |
| R_eff at t0 | 4.43 nm |
| t_close (R_min < 3 A for 5 frames) | 2.10 ns |
| dR_eff/dt, first 5 ns | 0.010 ± 0.007 nm/ns |
| dR_eff/dt, open period | 0.010 ± 0.007 nm/ns |
| final R_eff / R_min | 0.00 / 0.00 nm |
| film thickness t0 / final | 22.15 / 13.37 nm |

## Free shell

- beads with 4 < r < 6.5 nm at t0: 15317; areal density / far film: 0.799.
- bead MSD from t0 (COM removed): 1 ns: 572.8 A², 10 ns: 2198.7 A², end: 2873.9 A² (end = 20.00 ns)

## Per production segment (second half)

| # | kind | T (C) | scaffold | R_eff (nm) | R_min (nm) | open |
|---|---|---|---|---|---|---|
| 1 | hold | 160 | - | 0.00 | 0.00 | no |

## Caveats

- The scaffold is imposed harmonic tethers (fix spring/self) on the film outside R + d, a stand-in for the semicrystalline network that holds real separator pores open; it is not crystallinity, and its release is an emulation of melting, not a prediction of the shutdown temperature.
- The free film is the post-shutdown limit (a hole in an amorphous melt-like film).
- Times are CG model times (the SDK CG dynamics is faster than real PE by an unknown factor); compare runs with each other, not with experiment.
- All holes here have R < h (R/h <= 0.31), so closure is expected from the energy balance (R_c proportional to h, prefactor ~0.3-1 depending on rim geometry; Taylor & Michael 1973, Ilton et al. 2016): these runs measure closure kinetics (viscous scale ~ eta R / gamma), not the opening threshold.
- Finite size: the film is periodic in x, y; the ligament between the hole and its periodic images is L - 2R (given above; R = 4 nm leaves ~5 nm).
- gamma (and so the closure speed) depends on the plain LJ cutoff without tail correction (D48).

Figures: `hole_radius.png`, `hole_maps.png`, `thickness.png`
