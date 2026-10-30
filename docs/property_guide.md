## Property guide: what each calculated quantity means

Reference values are approximate textbook values for amorphous or molten PE, to give a sense of scale. They have not been checked against a specific source. All boxes stay amorphous at every temperature. Real separator PE is semicrystalline below about 130 °C, so 25–130 °C here describes the amorphous phase only. CG and UA times are model times: CG dynamics in particular run several times faster than real PE, so only their trends with temperature are meaningful.

### Thermodynamic properties

1. **Density ρ(T).** Mean density of each NPT segment. Steps use their second half; holds drop their first 10%. The error is the SEM from the statistical inefficiency (D26). Amorphous PE is about 0.85 g/cm³ extrapolated to 25 °C and about 0.77–0.78 g/cm³ as a melt near 150–160 °C.

2. **Thermal expansion α_V.** α_V = (1/V) dV/dT, from SEM-weighted straight-line fits of volume against T over 25–160, 25–90 and 90–160 °C.
   - Errors are scaled by √χ²_red when χ²_red > 1, so curvature shows up as a large χ²_red and a larger error.
   - Expansion speeds up slightly with temperature, which is why the 25–160 °C fit is poor and the narrower windows are given.
   - Amorphous or molten PE is about 7–8 × 10⁻⁴ K⁻¹.

3. **Isothermal compressibility κ_T.** κ_T = (⟨V²⟩ − ⟨V⟩²)/(k_B T ⟨V⟩), from the volume fluctuations of each NPT hold. The bulk modulus is K = 1/κ_T. PE melt is roughly 1 GPa⁻¹ near 150 °C; CG models usually come out somewhat too compressible.

4. **Heat capacity Cp.** Cp = dH/dT per gram, fitted like α_V. It is classical. UA and CG remove degrees of freedom (hydrogens, atoms inside beads), so their Cp is far below real PE (about 2.3–2.6 J g⁻¹ K⁻¹ for the melt) and is not comparable to experiment. Only AA, with the quantum correction from the vibrational spectrum (VDOS, D12c), gives a meaningful Cp.

### Chain size and shape

5. **Rg and R_ee.** Radius of gyration (mass-weighted, all atoms of a chain) and end-to-end distance, averaged over every hold frame. In a melt they barely depend on temperature.

6. **C_n (characteristic ratio).** C_n = ⟨R_n²⟩/(n l²) for stretches of n backbone C–C bonds of length l = 1.54 Å.
   - It measures chain stiffness: 1 for a freely jointed chain, and higher with fixed bond angles and a preference for trans.
   - It levels off at C∞, about 6.7 for PE and 6.15 for iPP melts. We report the plateau for n ≥ 100 carbons (D37).
   - A higher C_n means stiffer, more extended chains: ⟨R²⟩ = C∞ n l².
   - Under the project rule, a C_n that misses the literature value in an equilibrated box is a property of the model, not a failure.

### Dynamics

7. **Bond reorientation time (P2 1/e).** ⟨P2(u(0)·u(t))⟩ of the backbone bond vectors, with the time at which it falls to 1/e. It measures how fast local segments reorient, which is set by local packing, not chain length. It speeds up strongly with temperature.

8. **Segment MSD, chain centre-of-mass MSD and D_COM.**
   - Mean-square displacement of backbone sites and of whole chains, combining the dense 0.1 ps bursts and the 10 ps hold frames (D46).
   - D_COM = slope/6 when the MSD is diffusive, meaning a log-slope of at least 0.9 over at least a factor of 2 in lag. Otherwise it is "not diffusive" and the largest slope is reported.
   - In a 12.5 ns hold the chains move less than their own size, so true chain diffusion would need much longer runs.

### Equilibration and quality checks

9. **D47 (chain mixing at 500 K).**
   - The criterion: the end-to-end vector ACF is below 1/e and the chain COM MSD is at least 2⟨Rg²⟩, at a lag of half the combined 500 K hold.
   - Very long chains such as C1500 cannot reach it in affordable time. They are accepted on a stable C_n plateau.

10. **Drift flags and hysteresis.** "drift seg …" marks segments whose thermo shows a significant trend over the analysis window; it is informational. Hysteresis is the largest density difference between the cooling and heating branches at the same T.

### Pores (stage 2, `sepsim analyze pore`, D51)

11. **Surface tension γ.** γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] (two interfaces), per segment. It uses a plain LJ cutoff with no tail correction (D48), so γ depends on the cutoff.

12. **Density profile ρ(z).** Profile across the film: whether the interior matches bulk density, film thickness from the Gibbs dividing surfaces, interfacial width, actual gap width against the nominal 5 nm, and the closest approach of atoms across the gap.

13. **Near-surface behaviour.** Segment mobility (in-plane and normal), bond reorientation, bond orientation relative to the surface and chain shape, near the surface against the interior and bulk.

14. **Finite-size check (D50).** The 40-chain and 2×2×2 (320-chain) pores are compared on the quantities above.

**Caveat.** The slit models a local patch of pore wall. Real separator pores are 30–100 nm across, curved and semicrystalline.
