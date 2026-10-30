# Comparison with experiment (CG PE, 2026-10-30)

This compares the CG PE results (SDK/SPICA; C240 unless noted) with experimental amorphous or melt data at the same temperature and 1 atm. Two independent checks went into it:

- **Calculation audit:** every reported number was recomputed from the raw logs and trajectories with independent code. All agree to the printed digits, with no unit, sign or formula errors.
- **Literature check:** reference values were checked against primary sources. **[V]** means read directly from the source. **[D]** means derived by arithmetic from [V] values. Unverified values are marked "unverified".

UA and AA rows will be added when those sweeps are analyzed.

## Property by property

| Property | Our CG value | Experiment (amorphous/melt) | Difference | Cause |
|---|---|---|---|---|
| Density ρ (g/cm³) at 25 / 90 / 130 / 160 °C | 0.8345 / 0.7978 / 0.7758 / 0.7594 (C1500: 0.8382 / 0.8015 / 0.7802 / 0.7644) | 0.852 / ≈0.814 / ≈0.790 / ≈0.774–0.781 [V/D: ATHAS amorphous line, SANS densities, Tait fit] | ≈ −2 % (C1500 −1 to −2 %) | Force field |
| α_V (10⁻⁴ K⁻¹), 25–160 °C | 6.92 ± 0.03 (C1500 6.78) | 7.0–7.5 [D: SANS densities, Tait] | ≈ −5 % | Force field |
| κ_T (GPa⁻¹) at 130 / 160 °C | 1.50 / 1.66 (C1500 1.44 / 1.57) | 0.94 / 1.08 [D: Tait, Sato PVT data] | +50–60 % (model too compressible) | Force field (typical of CG) |
| Cp (J g⁻¹ K⁻¹) | 0.83 (classical; the NPT fluctuation formula gives the same within 1–2 %) | 2.20 (25 °C), 2.40 (90), 2.52 (130), 2.61 (160) [V/D: ATHAS] | ≈ −65 % | **Removed degrees of freedom:** a CG bead keeps 3 of the 27 atomic degrees of freedom of (CH₂)₃. Real Cp is quantum (C–H stretches ≈ 0 % excited at 300 K). Classical equipartition: fully flexible AA ≈ 2.4× experiment; flexible UA near experiment by accident; CG ≈ 1/3 per CH₂. Not a calculation error. |
| Surface tension γ (mN/m) at 25 / 90 / 130 / 160 °C | 34.4 / 31.1 / 29.5 / 27.9 (5 nm pore; 2×2×2 pore within ≈1 mN/m) | ≈35.4 / 31.7 / 29.4 / 27.7 (Wu compilation, unverified); LLDPE melt: 29.6 at 130 °C, 27.5 at 160 °C [V: Moreira 2003] | within 1–3 % | SDK CG was fitted partly to surface tension. Our value depends on the cutoff (no tail correction at the surface). |
| dγ/dT (mN m⁻¹ K⁻¹) | −0.048 | −0.057 (Wu, unverified) to −0.0725 (LLDPE) [V] | ≈20 % shallower | Force field and short chains |
| C_n plateau / C∞ | C240: 9.1 at 500 K, 10–12 at the holds; C1500: 7.9–8.5 | C∞ 7.38 at 140 °C, 8.26 at 25 °C; d ln⟨R²⟩/dT = −1.2 × 10⁻³ K⁻¹ [V: Fetters, Lohse, Colby] | C240 +25 to +45 %; C1500 ≈ +10 % | Force field (chains too stiff). The per-hold C240 values are also frozen in from the melt: chains moved < 1 Rg per hold. |
| Rg (Å) | C240 30.8–32.2; C1500 67.8–70.3 | C240 ≈ 25–26.5, C1500 ≈ 66 at 140 °C [D from ⟨R²⟩/M = 1.25 Å² mol/g] | C240 ≈ +20 %; C1500 ≈ +5 % | Same as C_n |
| Bond reorientation (P2 1/e) | 7.6 ps at 160 °C (bead–bead vector, CG time) | C–H vector ≈ 5 ps at 400 K (¹³C NMR) [V: Qiu & Ediger 2000] | not comparable | Different vectors, and CG time is faster |
| Dynamics time scale | — | SDK PE melt chains diffuse 4.07× faster than experiment; CG times are usually multiplied by 4.07 [V: Hall et al. 2019/2020] | — | Coarse graining smooths the energy landscape |
| Chain diffusion D (C240) | not yet measured (300 ns diffuse runs in progress). The 90 °C sweep "D_COM" of 5.1 × 10⁻⁷ cm²/s is **not** real diffusion: chains moved only 0.38 Rg². Fix in progress. | ≈1.8 × 10⁻⁷ cm²/s at 175 °C (Pearson 1987, read from a graph, ±30 %); η₀ ≈ 0.06–0.1 Pa·s at 140–175 °C [D] | — | Compare after the 4.07× time scaling |
| Plateau modulus / amorphous stiffness | tensile runs in progress | G_e = 2.6 MPa at 140 °C, so an amorphous rubber has E ≈ 3G_e ≈ 8 MPa [V: Fetters, Lohse, Colby]. Semicrystalline separators: E ≈ 0.25 GPa (Celgard 3501, compression) [V: Gor 2014]; tensile strength 165 MPa along the machine direction (Celgard H2010) [V] | — | Our boxes are amorphous, so MPa-scale, rate-dependent moduli are expected, not the GPa of real films |

## Errors in the reported uncertainties (found by the audit; fix in progress)

- **SEMs too small:**
  - The statistical-inefficiency SEM of thermo series is 1.3–3.5× too small for density and volume, 1.7–2.6× for enthalpy and 1.3–2.2× for surface tension (holds). Barostat ringing makes the volume autocorrelation go negative at 3–4 ps, and the estimator stops there, missing a slow tail of ≈1–2 ns.
  - The fix is to compute the inefficiency on 100 ps block means, which matches Flyvbjerg–Petersen blocking.
  - Mean values, κ_T and its SEM, and the α_V and Cp fit values and their Birge-scaled errors are unaffected.
- **D_COM "diffusive" verdict too loose:** the old criterion (log-slope ≥ 0.9 over a factor 2 in lag) accepts the sub-diffusive Rouse regime. The fix also requires COM MSD ≥ 2⟨Rg²⟩, the D47 criterion.

## Sources

- **ATHAS heat capacity, PE:** Gaur & Wunderlich, J. Phys. Chem. Ref. Data 10, 119 (1981), https://doi.org/10.1063/1.555636. Melt/amorphous PE: Cp = 0.04325·T + 17.919 J mol⁻¹ K⁻¹ (per CH₂); amorphous ρ 0.8519 at 298 K, 0.7835 at Tm⁰ = 414.6 K.
- **ATHAS heat capacity, iPP:** Gaur & Wunderlich, J. Phys. Chem. Ref. Data 10, 1051 (1981), https://doi.org/10.1063/1.555650. Cp = 0.151291·T + 42.956 J mol⁻¹ K⁻¹ (per C₃H₆).
- **Chain dimensions:** Fetters, Lohse, Colby, "Chain Dimensions and Entanglement Spacings", in Mark (ed.), Physical Properties of Polymers Handbook, 2nd ed., Springer (2007). Gives C∞, ⟨R²⟩/M, M_e, G_e and melt densities.
- **Tait fits (PE, iPP):** Padilha Júnior et al., Polímeros 25(3) (2015), https://doi.org/10.1590/0104-1428.1621, fitted to Sato et al. PVT data. iPP Tait: Kowalska, Polimery 51, 862 (2006).
- **Melt surface tension:** Moreira et al., Polímeros 13(1), 45 (2003). LLDPE: γ = 39.05 − 0.0725·t(°C) mN/m. Wu's compilation (J. Macromol. Sci. C10, 1, 1974) was not accessible.
- **Segmental dynamics (¹³C NMR):** Qiu & Ediger, J. Polym. Sci. B 38, 2634 (2000).
- **Short PE melt diffusion:** Pearson et al., Macromolecules 20, 1133 (1987). Friction and WLF tables compiled in Luettmer-Strathmann, arXiv:cond-mat/9911250.
- **SDK PE time scaling (4.07×):** Hall, Sirk, Klein, Shinoda, J. Chem. Phys. 150, 244901 (2019); Hall et al., Polymers 12, 447 (2020).
- **SDK parameterization:** Shinoda, DeVane, Klein, Mol. Simul. 33, 27 (2007).
- **Separator mechanics:** Gor et al., J. Electrochem. Soc. 161, F3065 (2014); Polymers 16, 1174 (2024).
- **TraPPE-UA PE density and diffusion:** Ley-Flores et al., arXiv:2404.09676 (2024). TraPPE-UA overestimates PE melt density by ≈1.5–2 % at C300–C1000, 448 K.
- **L-OPLS:** Siu, Pluhackova, Böckmann, J. Chem. Theory Comput. 8, 1459 (2012).
