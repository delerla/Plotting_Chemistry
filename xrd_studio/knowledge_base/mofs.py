"""
mofs.py - Crystallographic Bragg peak libraries for Metal-Organic Frameworks (MOFs).
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

MOF_PRESETS = {
    "UiO-66 (Zr-BDC) Framework": {
        "domain": "mofs",
        "material_class": "Zirconium Terephthalate MOF (fcu topology)",
        "two_theta_window": (5.0, 35.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Preserve sharp (111) and (200) reflections (<9° 2θ) to verify ordered octahedral framework; missing-linker defects broaden (111) or induce reo superlattice peaks (~4.3°–6°).",
        "peaks": [
            {"label": "UiO-66 (111)", "hkl": "(111)", "center": 7.36, "fwhm": 0.24, "amp": 4200, "color": "#1f77b4", "meaning": "Primary fcu (111) basal pore reflection (d ≈ 12.0 Å)"},
            {"label": "UiO-66 (200)", "hkl": "(200)", "center": 8.48, "fwhm": 0.26, "amp": 1850, "color": "#ff7f0e", "meaning": "Secondary fcu (200) framework plane (d ≈ 10.4 Å)"},
            {"label": "UiO-66 (022)", "hkl": "(022)", "center": 12.01, "fwhm": 0.30, "amp": 720, "color": "#2ca02c", "meaning": "In-plane Zr₆O₄(OH)₄ node periodicity"},
            {"label": "UiO-66 (113)", "hkl": "(113)", "center": 14.12, "fwhm": 0.32, "amp": 540, "color": "#9467bd", "meaning": "High-order linker-node correlation"},
            {"label": "UiO-66 (222)", "hkl": "(222)", "center": 14.74, "fwhm": 0.30, "amp": 610, "color": "#8c564b", "meaning": "Second-order (111) harmonic"},
            {"label": "UiO-66 (004)", "hkl": "(004)", "center": 17.08, "fwhm": 0.34, "amp": 480, "color": "#17becf", "meaning": "Second-order (200) harmonic"},
            {"label": "UiO-66 (006)/(117)", "hkl": "(006)", "center": 25.68, "fwhm": 0.38, "amp": 950, "color": "#d62728", "meaning": "Intense cluster-cluster diagnostic reflection"},
        ],
    },
    "ZIF-8 (Zn-2-MeIM) Sodalite MOF": {
        "domain": "mofs",
        "material_class": "Zeolitic Imidazolate Framework (SOD topology)",
        "two_theta_window": (5.0, 30.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Diagnostic sodalite planes (011), (002), (112), and (222). Peak broadening signals nanocrystal downsizing (<50 nm); loss of (011) intensity indicates pore collapse or Zn(OH)₂ hydrolysis.",
        "peaks": [
            {"label": "ZIF-8 (011)", "hkl": "(011)", "center": 7.35, "fwhm": 0.22, "amp": 4800, "color": "#1f77b4", "meaning": "Dominant SOD cage reflection (d ≈ 12.0 Å)"},
            {"label": "ZIF-8 (002)", "hkl": "(002)", "center": 10.38, "fwhm": 0.24, "amp": 1450, "color": "#ff7f0e", "meaning": "Cubic lattice parameter indicator (a ≈ 17.0 Å)"},
            {"label": "ZIF-8 (112)", "hkl": "(112)", "center": 12.73, "fwhm": 0.25, "amp": 2150, "color": "#2ca02c", "meaning": "Strong SOD framework fingerprint"},
            {"label": "ZIF-8 (022)", "hkl": "(022)", "center": 14.70, "fwhm": 0.28, "amp": 820, "color": "#9467bd", "meaning": "Sodalite cage facet plane"},
            {"label": "ZIF-8 (013)", "hkl": "(013)", "center": 16.44, "fwhm": 0.28, "amp": 980, "color": "#8c564b", "meaning": "Mid-angle structural plane"},
            {"label": "ZIF-8 (222)", "hkl": "(222)", "center": 18.02, "fwhm": 0.30, "amp": 1280, "color": "#d62728", "meaning": "High-symmetry body-diagonal plane"},
        ],
    },
    "HKUST-1 (Cu-BTC) Framework": {
        "domain": "mofs",
        "material_class": "Copper(II) Trimesate MOF (tbo topology)",
        "two_theta_window": (5.0, 28.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Dehydration shifts (200)/(222) ratios; moisture exposure breaks Cu-carboxylate bonds causing amorphous broad humps and Cu₂O (~36.4°) emergence.",
        "peaks": [
            {"label": "HKUST-1 (200)", "hkl": "(200)", "center": 6.72, "fwhm": 0.24, "amp": 2600, "color": "#1f77b4", "meaning": "Hydration-sensitive (200) cage plane"},
            {"label": "HKUST-1 (220)", "hkl": "(220)", "center": 9.50, "fwhm": 0.26, "amp": 2200, "color": "#ff7f0e", "meaning": "Paddlewheel dimer connectivity reflection"},
            {"label": "HKUST-1 (222)", "hkl": "(222)", "center": 11.63, "fwhm": 0.28, "amp": 4500, "color": "#2ca02c", "meaning": "Primary maximum reflection in Cu-BTC"},
            {"label": "HKUST-1 (400)", "hkl": "(400)", "center": 13.45, "fwhm": 0.30, "amp": 1350, "color": "#9467bd", "meaning": "Second-order (200) spacing"},
            {"label": "HKUST-1 (333)/(511)", "hkl": "(333)", "center": 17.50, "fwhm": 0.34, "amp": 1100, "color": "#d62728", "meaning": "Superposition of pore-wall reflections"},
        ],
    },
}
