"""
polymers_carbon.py - Crystallographic libraries for PAN Nanofibers, Cyclized Ladder Polymers, and Graphitic Carbons.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

POLYMER_CARBON_PRESETS = {
    "PAN Nanofibers & Stabilization Evolution": {
        "domain": "polymers_carbon",
        "material_class": "Electrospun Semi-Crystalline Polymer (PAN)",
        "two_theta_window": (10.0, 45.0),
        "default_line_shape": "Gaussian",
        "key_diagnostic": "Tracks semicrystalline PAN (100) chain packing (~16.9°) collapse into the stabilized cyclized ladder/turbostratic (002) reflection (~25.4°) during thermal oxidation.",
        "peaks": [
            {"label": "PAN (100)", "hkl": "PAN(100)", "center": 16.92, "fwhm": 1.65, "amp": 3600, "color": "#1f77b4", "meaning": "Hexagonal rod-like nitrile chain packing (d ≈ 5.24 Å)"},
            {"label": "Amorphous / Cyclized (002)", "hkl": "(002)", "center": 25.45, "fwhm": 4.20, "amp": 1550, "color": "#ff7f0e", "meaning": "Amorphous halo + emerging conjugated ladder sheets (d ≈ 3.50 Å)"},
            {"label": "PAN (110)", "hkl": "PAN(110)", "center": 29.50, "fwhm": 2.10, "amp": 780, "color": "#2ca02c", "meaning": "Secondary orthorhombic/pseudohexagonal nitrile reflection"},
        ],
    },
    "Carbonized Nanofibers / Graphitic Carbon": {
        "domain": "polymers_carbon",
        "material_class": "Turbostratic / Graphitic Carbon",
        "two_theta_window": (10.0, 55.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Calculates interlayer spacing d₀₀₂ (3.354 Å for ideal graphite vs 3.45–3.65 Å for turbostratic CNFs), stacking height Lc from (002), and lateral crystal domain La from (100)/(101).",
        "peaks": [
            {"label": "Graphitic (002)", "hkl": "(002)", "center": 25.85, "fwhm": 3.40, "amp": 3900, "color": "#1f77b4", "meaning": "Graphene layer π-π stacking (yields d₀₀₂ and Lc)"},
            {"label": "Turbostratic (100)/(101)", "hkl": "(100)", "center": 43.35, "fwhm": 3.80, "amp": 1250, "color": "#d62728", "meaning": "In-plane sp² honey-comb domain ordering (La)"},
        ],
    },
}
