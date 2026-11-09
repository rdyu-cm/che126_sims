## Property table

Every quantity the repo calculates, one row each. Macro: a bulk or continuum property measurable on a lab sample. Micro: a molecular, chain or nanometre-scale property. "Code only" means the function exists in `src/sepsim/analysis/` but nothing calls it yet. Definitions in more detail: `docs/property_guide.md`.

| Property | Compact definition | Macro / Micro | Category | Status |
|---|---|---|---|---|
| Density ρ(T) | Mean mass/volume of each NPT segment (SEM from statistical inefficiency) | Macro | Bulk thermodynamics | Computed |
| Volume V(T), box lengths | Mean box volume and Lx/Ly/Lz per segment | Macro | Bulk thermodynamics | Computed |
| Volumetric thermal expansion α_V | (1/V) dV/dT from weighted linear fits over 25–160, 25–90, 90–160 °C | Macro | Bulk thermodynamics | Computed |
| Linear thermal expansion α_L | α_V/3 for the isotropic bulk | Macro | Bulk thermodynamics | Computed |
| Isothermal compressibility κ_T | (⟨V²⟩−⟨V⟩²)/(k_B T⟨V⟩) from NPT volume fluctuations | Macro | Bulk thermodynamics | Computed |
| Bulk modulus K | 1/κ_T | Macro | Bulk thermodynamics | Computed |
| Enthalpy H(T) | Mean of E + PV per segment | Macro | Bulk thermodynamics | Computed |
| Potential / total energy | Mean potential and total energy per segment | Macro | Bulk thermodynamics | Computed |
| Pressure tensor Pxx, Pyy, Pzz | Mean diagonal pressure components per segment | Macro | Bulk thermodynamics | Computed |
| Classical heat capacity Cp | dH/dT per gram from a linear fit of H vs T | Macro | Bulk thermodynamics | Computed |
| Quantum-corrected Cp (AA) | Classical Cp minus the harmonic quantum correction weighted by the VDOS | Macro | Bulk thermodynamics | Code only (not run yet) |
| Vibrational density of states (VDOS) | Fourier transform of the mass-weighted velocity ACF | Micro | Bulk thermodynamics | Code only (not run yet) |
| Thermal conductivity κ (rNEMD) | −J/(dT/dz) from a Müller-Plathe reverse-NEMD temperature profile | Macro | Transport | Code only (not run yet) |
| Melting point T_m | Crystalline fraction vs T on a heating ramp, cross-checked with V(T) and H(T) | Macro | Phase behaviour | Code only (not run yet) |
| Cooling/heating hysteresis | Largest density difference between the cooling and heating branches at the same T | Macro | Phase behaviour | Computed |
| Radius of gyration Rg | Mass-weighted RMS distance of a chain's atoms from its centre of mass | Micro | Chain structure | Computed |
| End-to-end distance R_ee | RMS distance between the two chain ends | Micro | Chain structure | Computed |
| Mean-square internal distances ⟨R²(n)⟩/n | Mean-square distance between backbone sites i and i+n, divided by n | Micro | Chain structure | Computed |
| Characteristic ratio C_n / C∞ | ⟨R_n²⟩/(n l²); the plateau for n ≥ 100 is reported as C∞ | Micro | Chain structure | Computed |
| Crystallinity (local P2 order) | Fraction of backbone sites with local stem alignment p2 ≥ 0.4, plus the largest cluster (uncalibrated melt baseline) | Micro | Chain structure | Computed |
| Mean local order ⟨p2⟩ | Mean of the local alignment order parameter over all sites | Micro | Chain structure | Computed |
| Methine inversions (iPP tacticity) | Number of methine carbons whose chirality flipped from the start | Micro | Chain structure | Code only (not run yet) |
| Bond reorientation ACF / τ_P2 | ⟨P2(u(0)·u(t))⟩ of backbone bonds; time to fall to 1/e | Micro | Dynamics | Computed |
| Segment MSD | MSD of backbone sites (reported at 1, 10, 1000 ps and at the longest lag) | Micro | Dynamics | Computed |
| Chain COM MSD and MSD/⟨Rg²⟩ | MSD of chain centres of mass, and its ratio to the chain size | Micro | Dynamics | Computed |
| Chain self-diffusion D_COM | Slope/6 of the COM MSD where the log-slope is ≥ 0.9 over a factor ≥ 2 in lag | Micro (borderline) | Dynamics | Computed |
| Rouse viscosity η_R | ρ_N k_B T⟨R_ee²⟩/(36 D_COM); a lower bound if the chains are entangled | Macro | Dynamics | Computed |
| End-to-end relaxation time τ_ee | Time for ⟨R(t)·R(0)⟩/⟨R²⟩ to fall to 1/e (longest single-chain time) | Micro | Dynamics | Computed |
| Rouse modes X_p, amplitudes ⟨X_p²⟩ | Cosine-transform normal modes along the chain; p²⟨X_p²⟩ tests Gaussian statistics | Micro | Dynamics | Computed |
| Rouse times τ_p and τ_1 from p²τ_p | 1/e decorrelation time of each mode; τ_1 estimated from higher modes | Micro | Dynamics | Computed |
| Stress–strain curve (true and engineering) | σ = −(P_axis − 1 atm) during a constant-rate uniaxial pull; engineering stress = σ·A/A0 | Macro | Mechanics | Computed |
| Apparent Young's modulus E_app | Slope of σ vs strain up to 2% strain (depends on the rate) | Macro | Mechanics | Computed |
| Poisson ratio ν (fit and whole run) | −d ln L_lateral / d ln L_axis over the ≤2% window and over the whole run | Macro | Mechanics | Computed |
| Secant Poisson ratio ν(ε) | Running −ln(L_lat/L_lat0)/ln(L/L0) along the curve | Macro | Mechanics | Computed |
| Peak stress and peak strain | Maximum of the smoothed σ and the strain where it occurs | Macro | Mechanics | Computed |
| Flow stress | Mean σ over strains 0.3–0.5 (viscous plateau ≈ 3η × rate) | Macro | Mechanics | Computed |
| Surface tension γ(T) | (Lz/2)[Pzz − (Pxx+Pyy)/2] for the film's two surfaces (plain cutoff, no tail correction) | Macro | Interface / film | Computed |
| dγ/dT and γ(25 °C) | Linear fits of γ vs T on the sweep and cooling branches | Macro | Interface / film | Computed |
| Surface entropy | −dγ/dT | Macro | Interface / film | Computed |
| Surface excess energy e_s | (E_pore − (M_pore/M_bulk)E_bulk)/(2A), checked against γ − T dγ/dT | Macro | Interface / film | Computed |
| Film heat capacity Cv | dE/dT of the NVT film per gram, compared with bulk Cp | Macro | Interface / film | Computed |
| Film thermal expansion α_z, α_V(film) | (1/h) dh/dT of the Gibbs thickness; α_V = α_z + 2α_L (α_L imposed) | Macro | Interface / film | Computed |
| Density profile ρ(z) | Mass density across the film, symmetrised about the film centre | Micro | Interface / film | Computed |
| Interior (plateau) density | Median density of bins above 80% of the maximum, compared with bulk | Macro | Interface / film | Computed |
| Gibbs film thickness | ∫ρ dz / plateau density (equimolar dividing surfaces) | Micro | Interface / film | Computed |
| Interfacial width (10–90 and tanh) | Distance between the 10% and 90% density crossings; tanh-fit width δ | Micro | Interface / film | Computed |
| Pore / gap width | Gap between the films at 50% density, at the Gibbs surfaces, and the clear z gap | Micro | Interface / film | Computed |
| Closest approach across the gap | Minimum atom–atom distance across the slit | Micro | Interface / film | Computed |
| Local pore widths (x–y map) | Pore width per x–y column of the density grid | Micro | Interface / film | Code only (not run yet) |
| Bond orientation P2z(z) | ⟨P2(cos θ)⟩ of bonds against the surface normal, as a profile and per layer | Micro | Interface / film | Computed |
| Chain shape near the surface | Rg_z² and Rg_xy²/2 of surface vs interior chains | Micro | Interface / film | Computed |
| Layer-resolved MSD (xy, z) | In-plane and normal segment MSD for surface vs interior vs whole film | Micro | Interface / film | Computed |
| Layer-resolved bond reorientation | τ_P2 for the surface layer vs the interior | Micro | Interface / film | Computed |
| Surface fraction | Fraction of sites within the surface layer depth | Micro | Interface / film | Computed |
| Hole radius R_eff(t) | √(A/π) of the hole in the z-projected bead-occupancy map | Micro (nm-scale) | Hole closure | Computed |
| Hole area A(t) | Area of the connected low-occupancy region around the tracked centre | Micro (nm-scale) | Hole closure | Computed |
| Slab radii R(z) and R_min | The same radius per 10 Å slab; R_min is the narrowest slab | Micro (nm-scale) | Hole closure | Computed |
| Closure time t_close | First time R_min < 3 Å for 5 frames in a row | Macro (borderline) | Hole closure | Computed |
| Closure speed dR/dt | Slope of R vs t over the first 5 ns and over the open period (≈ γ/η) | Macro (borderline) | Hole closure | Computed |
| Plateau / final radius | Mean R_eff over the last quarter of the run; R and R_min at the end | Micro (nm-scale) | Hole closure | Computed |
| Film thickness over time | Thickness between the 50% plateau crossings of the z profile | Micro | Hole closure | Computed |
| Centroid drift | How far the hole centre has moved from the build axis | Micro | Hole closure | Computed |
| Ligament | Narrowest film strip between the hole and its periodic image (min(Lx,Ly) − 2R) | Micro | Hole closure | Computed |
| Free-shell rim build-up | Bead areal density in the R…R+d shell relative to the far film | Micro | Hole closure | Computed |
| Free-shell MSD | How far beads in the free shell move, free vs scaffolded runs | Micro | Hole closure | Computed |
| Scaffold tether stats | Count and fraction of tethered beads; nearest one to the axis (must be ≥ R + d) | Micro | Hole closure | Computed |
| D47 chain mixing (500 K) | R_ee ACF < 1/e and COM MSD ≥ 2⟨Rg²⟩ at half the 500 K hold | Micro | Equilibration check | Computed |
| D24 MSID check | ⟨R²(n)⟩/n vs n compared with the experimental C∞ range | Micro | Equilibration check | Computed |
| Drift flags | Significant first- vs second-half change in density, H, PE or γ within a segment | Macro | Equilibration check | Computed |
| Step-vs-hold agreement | Agreement between the short sweep step and the long hold at the same T | Macro | Equilibration check | Computed |
