"""
catalysts_oxides.py - Crystallographic libraries for Mixed-Phase TiO2, FCC Metals, and Electrocatalysts.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

CATALYST_OXIDE_PRESETS = {
    "TiO₂ Anatase–Rutile Polymorphs (P25 / Calcined)": {
        "domain": "catalysts_oxides",
        "material_class": "Semiconductor Photocatalyst (Anatase + Rutile)",
        "two_theta_window": (20.0, 66.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Quantifies Anatase-to-Rutile phase transformation via the Spurr–Myers equation using Anatase (101) at 25.28° and Rutile (110) at 27.45°.",
        "peaks": [
            {"label": "Anatase (101)", "hkl": "A(101)", "center": 25.28, "fwhm": 0.36, "amp": 4800, "color": "#1f77b4", "meaning": "Primary Anatase photocatalyst reflection (JCPDS 21-1272)"},
            {"label": "Rutile (110)", "hkl": "R(110)", "center": 27.45, "fwhm": 0.30, "amp": 1450, "color": "#d62728", "meaning": "Primary Rutile thermodynamic polymorph (JCPDS 21-1276)"},
            {"label": "Rutile (101)", "hkl": "R(101)", "center": 36.08, "fwhm": 0.32, "amp": 620, "color": "#ff7f0e", "meaning": "Rutile secondary plane"},
            {"label": "Anatase (004)", "hkl": "A(004)", "center": 37.80, "fwhm": 0.38, "amp": 1050, "color": "#2ca02c", "meaning": "c-axis Anatase crystallite elongation probe"},
            {"label": "Anatase (200)", "hkl": "A(200)", "center": 48.05, "fwhm": 0.40, "amp": 1520, "color": "#9467bd", "meaning": "a-axis Anatase facet plane"},
            {"label": "Anatase (105)", "hkl": "A(105)", "center": 53.89, "fwhm": 0.42, "amp": 940, "color": "#8c564b", "meaning": "High-angle Anatase peak"},
            {"label": "Anatase (211)", "hkl": "A(211)", "center": 55.06, "fwhm": 0.42, "amp": 910, "color": "#17becf", "meaning": "High-angle Anatase doublet companion"},
            {"label": "Anatase (204)", "hkl": "A(204)", "center": 62.69, "fwhm": 0.45, "amp": 760, "color": "#e377c2", "meaning": "High-angle Williamson-Hall strain anchor"},
        ],
    },
    "FCC Metal Nanoparticles (Cu / Cu₂O Catalyst)": {
        "domain": "catalysts_oxides",
        "material_class": "Metallic / Partially Oxidized Nanocatalyst",
        "two_theta_window": (30.0, 80.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Measures FCC metallic Cu (111)/(200)/(220) crystallite size, microstrain via Williamson-Hall plot, and surface cuprous oxide Cu₂O (111) passivating layer at 36.42°.",
        "peaks": [
            {"label": "Cu₂O (111)", "hkl": "Cu₂O(111)", "center": 36.42, "fwhm": 0.48, "amp": 850, "color": "#ff7f0e", "meaning": "Surface cuprous oxide phase (d ≈ 2.46 Å)"},
            {"label": "Cu (111)", "hkl": "Cu(111)", "center": 43.30, "fwhm": 0.42, "amp": 4600, "color": "#1f77b4", "meaning": "Close-packed FCC Cu(111) basal facet"},
            {"label": "Cu (200)", "hkl": "Cu(200)", "center": 50.43, "fwhm": 0.48, "amp": 2150, "color": "#2ca02c", "meaning": "FCC Cu(200) reflection (a ≈ 3.615 Å)"},
            {"label": "Cu₂O (220)", "hkl": "Cu₂O(220)", "center": 61.34, "fwhm": 0.55, "amp": 420, "color": "#8c564b", "meaning": "Oxide secondary reflection"},
            {"label": "Cu (220)", "hkl": "Cu(220)", "center": 74.13, "fwhm": 0.58, "amp": 1280, "color": "#d62728", "meaning": "High-angle FCC reflection ideal for strain separation"},
        ],
    },
}
