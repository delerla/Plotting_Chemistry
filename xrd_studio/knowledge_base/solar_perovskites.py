"""
solar_perovskites.py - Crystallographic Bragg peaks for Metal-Halide Perovskite PV absorbers.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

SOLAR_PEROVSKITE_PRESETS = {
    "MAPbI₃ / FAPbI₃ Perovskite Film (PbI₂ Check)": {
        "domain": "solar_perovskites",
        "material_class": "Metal-Halide Perovskite Thin Film (ABX₃)",
        "two_theta_window": (10.0, 45.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Monitors moisture/light decomposition via PbI₂ (001) at 12.67° and photo-inactive δ-FAPbI₃ at 11.82°. High I(110)/I(220) indicates uniaxial (110) grain texturing.",
        "peaks": [
            {"label": "δ-FAPbI₃ (Hexagonal)", "hkl": "δ-(010)", "center": 11.82, "fwhm": 0.24, "amp": 320, "color": "#7f7f7f", "meaning": "Non-perovskite yellow polymorph impurity"},
            {"label": "PbI₂ (001) Impurity", "hkl": "PbI₂(001)", "center": 12.67, "fwhm": 0.22, "amp": 950, "color": "#d62728", "meaning": "Halide perovskite decomposition / excess PbI₂ phase"},
            {"label": "Perovskite (110)", "hkl": "(110)", "center": 14.08, "fwhm": 0.20, "amp": 5200, "color": "#1f77b4", "meaning": "Primary cubic/tetragonal perovskite (110)/(002) peak"},
            {"label": "Perovskite (112)", "hkl": "(112)", "center": 19.96, "fwhm": 0.25, "amp": 740, "color": "#2ca02c", "meaning": "Octahedral tilting diagnostic reflection"},
            {"label": "Perovskite (202)", "hkl": "(202)", "center": 24.48, "fwhm": 0.27, "amp": 820, "color": "#9467bd", "meaning": "3D framework corner-sharing plane"},
            {"label": "Perovskite (220)", "hkl": "(220)", "center": 28.44, "fwhm": 0.24, "amp": 2650, "color": "#ff7f0e", "meaning": "Second-order (110) harmonic (strain & texture probe)"},
            {"label": "Perovskite (310)", "hkl": "(310)", "center": 31.89, "fwhm": 0.28, "amp": 1280, "color": "#8c564b", "meaning": "High-angle lattice contraction/expansion gauge"},
            {"label": "Perovskite (224)", "hkl": "(224)", "center": 40.55, "fwhm": 0.30, "amp": 890, "color": "#17becf", "meaning": "High-angle Williamson-Hall strain point"},
        ],
    },
    "CsPbI₃ / Triple-Cation on FTO Glass": {
        "domain": "solar_perovskites",
        "material_class": "All-Inorganic / Multi-Cation Perovskite + FTO",
        "two_theta_window": (9.0, 40.0),
        "default_line_shape": "Pseudo-Voigt",
        "key_diagnostic": "Tracks γ-CsPbI₃ black phase stability against yellow δ-CsPbI₃ (9.88°, 13.10°), while using FTO SnO₂ (110) at 26.58° as internal 2θ calibration anchor.",
        "peaks": [
            {"label": "δ-CsPbI₃ (011)", "hkl": "δ-(011)", "center": 9.88, "fwhm": 0.25, "amp": 290, "color": "#e377c2", "meaning": "Yellow non-perovskite orthorhombic phase"},
            {"label": "PbI₂ (001)", "hkl": "PbI₂(001)", "center": 12.67, "fwhm": 0.22, "amp": 450, "color": "#d62728", "meaning": "Excess or degraded PbI₂ phase"},
            {"label": "γ-CsPbI₃ (110)", "hkl": "(110)", "center": 14.28, "fwhm": 0.23, "amp": 4100, "color": "#1f77b4", "meaning": "Photoactive black perovskite phase"},
            {"label": "FTO SnO₂ (110)", "hkl": "FTO(110)", "center": 26.58, "fwhm": 0.26, "amp": 1600, "color": "#7f7f7f", "meaning": "Transparent conductive oxide substrate internal standard"},
            {"label": "γ-CsPbI₃ (220)", "hkl": "(220)", "center": 28.78, "fwhm": 0.27, "amp": 2100, "color": "#ff7f0e", "meaning": "Second-order black perovskite reflection"},
            {"label": "FTO SnO₂ (200)", "hkl": "FTO(200)", "center": 37.80, "fwhm": 0.30, "amp": 1150, "color": "#8c564b", "meaning": "FTO substrate secondary peak"},
        ],
    },
}
