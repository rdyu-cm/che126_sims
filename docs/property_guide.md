## Property guide: what each calculated quantity means

Reference values are approximate textbook values for amorphous or molten PE, to give a sense of scale. They have not been checked against a specific source. All boxes stay amorphous at every temperature. Real separator PE is semicrystalline below about 130 °C, so 25–130 °C here describes the amorphous phase only. CG and UA times are model times: CG dynamics in particular run several times faster than real PE, so only their trends with temperature are meaningful.

### Comparability with experiment

A fair comparison needs amorphous or melt data at the same temperature and a similar chain length (our chains are C240, about 3.4 kg/mol, and C1500, about 21 kg/mol).

| Property | Comparable to experiment? | Compare against, and caveats |
|---|---|---|
| Density ρ(T), thermal expansion α_V | **Yes**, all resolutions | Melt data above Tm. Below Tm, the amorphous density extrapolated from the melt, not a semicrystalline sample. Accuracy is a property of the force field (SDK CG was fitted to density). |
| Compressibility κ_T (bulk modulus 1/κ_T) | **Yes** | Melt PVT data at 1 atm. CG models usually come out too compressible. |
| Surface tension γ, dγ/dT | **Yes** | Melt γ vs T at a similar molecular weight. SDK CG was partly fitted to γ. Our value depends on the cutoff (no tail correction at surfaces, D48), which tends to bias it low. |
| Chain size Rg, R_ee, C_n | **Yes** | Neutron-scattering melt data (PE C∞ ≈ 6.7–7.4). CG and UA come out high, which is a force-field result. |
| Heat capacity Cp | **AA only, after the quantum correction** (VDOS, D12c) | CG and UA remove degrees of freedom (H atoms, motions inside a bead), so their Cp is far too low. Classical MD gives every vibration k_B T, while real high-frequency C–H modes are mostly frozen, so classical AA Cp is too high until corrected. |
| Dynamics: D, viscosity, P2 times, MSD | **AA roughly; UA partly; CG only with a time-mapping factor** | CG runs several times faster than real PE (smoothed energy landscape). UA is also somewhat fast (no hydrogen friction). Temperature trends are meaningful; absolute CG times need scaling to one experimental or AA point. |
| Young's modulus, Poisson ratio, yield (tensile) | **Not against separator data** | Real separator stiffness and yield come from crystals, and MD strain rates (10⁸–10⁹ s⁻¹) are about 10⁹× faster than tests. Only the amorphous-phase response and its trends with temperature and rate. |
| Pores: surface structure, hole closure | **No direct experiment** | The mechanism, and comparisons within our own simulations. |

**Our numbers next to experiment, with sources:** `docs/experiment_comparison.md`. In short, CG PE density is about 2% low, α_V about 5% low, surface tension within 1–3%, κ_T 50–60% too high, Cp about 3× low (degrees of freedom), chains about 20% too large (C240), and dynamics about 4× too fast.

**Comparisons that hold at every resolution are the ones within our own simulations:** temperature trends from 25 to 160 °C, PE vs iPP at the same resolution, CG vs UA vs AA on the same property, and small vs 2×2×2 boxes. Most of the separator conclusions rest on these, not on absolute agreement with experiment.

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

8b. **Long-hold D_COM (`diffuse`, D53).** The same D_COM criterion on a dedicated 300 ns NPT hold at one sweep temperature (CG), checked by `sepsim progress` while it runs. Only once the MSD is diffusive (and well beyond ⟨Rg²⟩) is D_COM a chain self-diffusion coefficient. The Rouse estimate η_R = ρ_N k_B T ⟨R_ee²⟩/(36 D), with ρ_N the chain number density, converts it into a melt viscosity; it assumes unentangled chains, so for entangled ones it is a lower bound. For a PE melt of this chain length expect roughly 0.1 Pa·s (order of magnitude only); CG dynamics are faster, so CG viscosities come out lower.

8g. **End-to-end relaxation time τ_ee (D56).** ⟨R(t)·R(0)⟩/⟨R²⟩ of the chain end-to-end vectors over every time origin, with the lag at which it falls to 1/e. It is the time a chain takes to forget its overall orientation and is the longest single-chain relaxation time; chain-scale averages (Rg, R_ee, C_n) at a temperature are only equilibrated over holds of several τ_ee. The lags reach half the hold (CG sweep holds 12.5 ns, UA 5 ns, AA 2.5 ns).

8h. **Rouse modes and τ_p (D56).** X_p = (1/N) Σ_n cos(pπ(n−½)/N) r_n splits a chain into standing waves along its backbone: p = 1 is the whole chain, p = 2 each half, p = N/p beads per wave. Each mode decorrelates on its own time τ_p (1/e of ⟨X_p(t)·X_p(0)⟩/⟨X_p²⟩), so the faster high-p modes are measurable in a short hold even when τ_1 ≈ τ_ee is not. For an ideal, unentangled (Rouse) chain τ_p = τ_1/p², so τ_1/τ_2 = 4 and p²τ_p is flat; and ⟨X_p²⟩ ∝ 1/p², so p²⟨X_p²⟩ is flat (it falls at high p where the chain is stiffer than Gaussian). Real melts give τ_p ∝ p^−2.2…−2.4, so τ_1 estimated as p²τ_p from a high p is a lower bound. C240 PE is near the entanglement length, so Rouse scaling is only approximate. CG times are model times (× 4.07 for experiment).

8i. **"not reached" and "extrapolated" (D56).** A relaxation time whose ACF stays above 1/e out to the longest lag is "not reached". The table then gives only an exponential fit of ln C over 0.2 ≤ C ≤ 0.9, marked extrap.: it extends the early decay beyond the data, typically underestimates a stretched decay, and is an order-of-magnitude figure, not a measurement.

### Mechanical properties (`tensile`, `sepsim analyze tensile`, D54)

8c. **Stress–strain curve.** The box is stretched along one axis at a constant engineering strain rate (10⁸ or 10⁹ s⁻¹) while the other two axes are held at 1 atm; this is repeated along x, y and z from the same starting snapshot. True stress σ = −(P_axis − 1 atm), tension positive; engineering stress is σ times the current over the initial cross-section.

8d. **Apparent modulus E_app.** Slope of σ against strain up to `--fit-max` (default 0.02). For an amorphous melt above Tg this is a high-frequency, rate-dependent response, not an equilibrium modulus; it falls as the rate falls. Bulk semicrystalline PE is of order 1 GPa because of its crystallinity, which these boxes do not have; an amorphous PE melt has no equilibrium modulus at all.

8e. **Poisson ratio ν.** ν = −d ln L_lateral / d ln L_axis. A melt that flows at constant volume gives 0.5; glassy polymers about 0.33–0.4. At MD rates the lateral barostat lags the pull, which biases ν low at small strain.

8f. **Peak and flow stress.** The maximum of the smoothed σ (with its strain), and the mean σ over strains 0.3–0.5. In a melt there is no true yield: the plateau is a viscous flow stress, about 3η × strain rate for a simple liquid, so it scales with the rate.

### Equilibration and quality checks

9. **D47 (chain mixing at 500 K).**
   - The criterion: the end-to-end vector ACF is below 1/e and the chain COM MSD is at least 2⟨Rg²⟩, at a lag of half the combined 500 K hold.
   - Very long chains such as C1500 cannot reach it in affordable time. They are accepted on a stable C_n plateau.

9b. **Crystallinity monitor (D56).** The D26 local-alignment order on ≤ 50 frames per hold: each backbone site's mean P2 with the chord vectors of other stems within r_c (CG: 1.4 σ of the bead pair, 6.3 Å; UA/AA: 6.5 Å), counted as ordered if p2 ≥ 0.4, with the fraction of ordered sites and the largest connected cluster. The threshold is **uncalibrated** (no crystal reference has been simulated), so the number is a melt baseline, not a crystallinity: a box that stays amorphous keeps a small, constant fraction with small clusters, and a fraction or cluster that grows during a hold would flag ordering. The baseline depends on the model (CG beads with near-straight bond angles show more local alignment than UA).

10. **Drift flags and hysteresis.** "drift seg …" marks segments whose thermo shows a significant trend over the analysis window; it is informational. Hysteresis is the largest density difference between the cooling and heating branches at the same T.

### Pores (stage 2, `sepsim analyze pore`, D51)

11. **Surface tension γ.** γ = (Lz/2)[Pzz − (Pxx+Pyy)/2] (two interfaces), per segment. It uses a plain LJ cutoff with no tail correction (D48), so γ depends on the cutoff.

12. **Density profile ρ(z).** Profile across the film: whether the interior matches bulk density, film thickness from the Gibbs dividing surfaces, interfacial width, actual gap width against the nominal 5 nm, and the closest approach of atoms across the gap.

13. **Near-surface behaviour.** Segment mobility (in-plane and normal), bond reorientation, bond orientation relative to the surface and chain shape, near the surface against the interior and bulk.

14. **Finite-size check (D50).** The 40-chain and 2×2×2 (320-chain) pores are compared on the quantities above.

**Caveat.** The slit models a local patch of pore wall. Real separator pores are 30–100 nm across, curved and semicrystalline.

### Physical validity by system

The comparability table above is per property. Whether a property can actually be compared for a given system also depends on that system's own checks, so `results/summary.md` ("Physical validity by system") and `results/validity_overview.png` show one verdict per system and property:

- **comparable**: compare with the stated experimental data. The caveats still apply, and `docs/experiment_comparison.md` has the CG PE offsets.
- **trend**: only temperature, PE vs iPP, resolution and box-size trends are meaningful. Examples: chain size at a sweep temperature where the chains moved less than their own size in the hold (inherited from the 500 K melt), C1500 chain size (D47 not reached), tensile, film structure.
- **needs correction**: meaningful only after the stated correction. AA Cp needs the VDOS quantum correction (D12c). CG dynamics need times × 4.07 (Hall et al. 2019), recalibrated per temperature against UA/AA. UA dynamics need a UA→AA time-mapping factor.
- **not meaningful**: CG and UA Cp (removed degrees of freedom; use AA).
- **not yet computed**: the data do not exist yet. The reason gives the verdict once they do.

Offsets in density, κ_T and chain size are force-field properties with no principled correction; compare the UA and AA values instead. A verdict is flagged when the system's 500 K equilibration is not accepted. The rules live in one place, `scripts/validity.py`, which is the single source of truth for both the summary and the figure.
