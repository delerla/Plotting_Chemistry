"""
polymers_pan.py - Vibrational Mode Libraries for PAN Nanofibers, Ladder Polymers & Polymer Composites.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

POLYMER_IR_PRESETS = {
    "PAN Nanofibers & Oxidative Stabilization": {
        "domain": "polymers_pan",
        "material_class": "Polyacrylonitrile (PAN) & Stabilized Ladder Fibers",
        "roi_window": (1200.0, 2400.0),
        "default_line_shape": "Gaussian",
        "key_diagnostic": "Evaluates oxidative cyclization Extent (E_s) from residual nitrile ν(C≡N) at ~2243 cm⁻¹ vs conjugated ladder ν(C=N/C=C) near ~1595 cm⁻¹ using extinction ratio f = 0.29.",
        "bands": [
            {"label": "ν(C≡N) Nitrile", "mode": "C≡N stretch", "center": 2243.0, "fwhm": 18.0, "color": "#1f77b4", "meaning": "Unreacted linear polyacrylonitrile nitrile group"},
            {"label": "ν(C=O) Pre-Oxidation", "mode": "C=O stretch", "center": 1715.0, "fwhm": 32.0, "color": "#ff7f0e", "meaning": "Oxidative carbonyl incorporation during thermal stabilization"},
            {"label": "ν(C=N/C=C) Ladder", "mode": "C=N / C=C", "center": 1598.0, "fwhm": 45.0, "color": "#d62728", "meaning": "Aromatized/cyclized naphthyridine ladder ring"},
            {"label": "δ(CH₂) Methylene Bend", "mode": "CH₂ scissor", "center": 1453.0, "fwhm": 26.0, "color": "#2ca02c", "meaning": "Aliphatic backbone -CH₂- scissoring mode"},
            {"label": "δ(C–H) Methine", "mode": "C–H bend", "center": 1368.0, "fwhm": 30.0, "color": "#9467bd", "meaning": "Aliphatic backbone -CH- deformation"},
            {"label": "ν(C–N/C–O) Skeletal", "mode": "C–N / C–C", "center": 1265.0, "fwhm": 34.0, "color": "#8c564b", "meaning": "Cross-linked oxygen-bridged / cyclized skeletal vibration"},
        ],
    },
    "Polymer / Metal-Salt Complex (PAN + Ni/Cu/Co)": {
        "domain": "polymers_pan",
        "material_class": "Coordination Polymer Nanofiber Composite",
        "roi_window": (1100.0, 2400.0),
        "default_line_shape": "Gaussian",
        "key_diagnostic": "Tracks transition-metal nitrate/acetate coordination onto PAN nitrile/carbonyl sites via shifted ν(C=O)/ν_as(NO₃⁻) bands (~1635, ~1385 cm⁻¹) and O–H hydration.",
        "bands": [
            {"label": "ν(C≡N) Free Nitrile", "mode": "C≡N stretch", "center": 2245.0, "fwhm": 18.0, "color": "#1f77b4", "meaning": "Unbound PAN nitrile stretch"},
            {"label": "δ(H₂O) / ν(C=N/C=O)", "mode": "M–Ligand / H₂O", "center": 1635.0, "fwhm": 38.0, "color": "#d62728", "meaning": "Metal-coordinated carbonyl/imine + hydrated salt bending"},
            {"label": "δ(CH₂) Backbone", "mode": "CH₂ bend", "center": 1454.0, "fwhm": 26.0, "color": "#2ca02c", "meaning": "Polymer hydrocarbon methylene scissoring"},
            {"label": "ν(NO₃⁻ / COO⁻)", "mode": "Salt anion", "center": 1385.0, "fwhm": 34.0, "color": "#ff7f0e", "meaning": "Counter-ion nitrate/acetate symmetric vibration"},
            {"label": "ν(C–N/C–O) Complex", "mode": "C–N / C–O", "center": 1295.0, "fwhm": 32.0, "color": "#9467bd", "meaning": "C–N skeletal / chelated acetate stretch"},
        ],
    },
}
