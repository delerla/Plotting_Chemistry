# Materials Characterization & Spectroscopic Analysis Protocols

## 1. Fourier-Transform Infrared Spectroscopy (FTIR)
- **Signal:** Transmittance (%T) vs. Wavenumber (4000–400 cm⁻¹).
- **Processing:** Savitzky-Golay smoothing, peak valley detection, baseline stacking with discrete vertical offsets.

## 2. X-Ray Diffraction (XRD)
- **Signal:** Intensity (a.u.) vs. 2θ (degrees, Cu Kα, λ = 1.5406 Å).
- **Analysis:** FWHM deconvolution, Scherrer crystallite sizing:
  D = (K * λ) / (β * cos(θ))  [where K = 0.9, β in radians]

## 3. UV-Vis & Dye Photodegradation Kinetics
- **Signal:** Absorbance vs. Wavelength (200–800 nm).
- **Kinetics:** Tracking C_t / C_0 = A_t / A_0 at λ_max.
  - Pseudo-first-order: ln(C_0 / C_t) = k_app * t
  - Pseudo-second-order: 1/C_t - 1/C_0 = k_2 * t

## 4. X-Ray Photoelectron Spectroscopy (XPS)
- **Signal:** Counts/s vs. Binding Energy (eV), referenced to C 1s (284.8 eV).
- **Processing:** Shirley baseline subtraction, Voigt profile multi-peak fitting via lmfit.

## 5. SEM & EDX Microanalysis
- **SEM:** Particle sizing, thresholding/binarization, diameter distributions.
- **EDX:** Peak identification for characteristic Kα/Lα lines and elemental wt%/at% quantification.
