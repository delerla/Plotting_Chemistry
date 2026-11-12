"""
catalysts_oxides.py - Vibrational Libraries for Metal Oxides, Silica Supports & Surface Adsorbates.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

CATALYST_IR_PRESETS = {
    "Metal Oxide / Silica Support (Surface OH & Carbonates)": {
        "domain": "catalysts_oxides",
        "material_class": "Heterogeneous Catalyst / Oxide Support",
        "roi_window": (450.0, 1800.0),
        "default_line_shape": "Gaussian",
        "key_diagnostic": "Quantifies physisorbed H₂O (1630 cm⁻¹), surface bidentate/monodentate carbonates (1525 / 1385 cm⁻¹), Si–O–Si support siloxane bridge (~1085 cm⁻¹), and M–O lattice modes (<700 cm⁻¹).",
        "bands": [
            {"label": "δ(H₂O) Adsorbed Water", "mode": "H–O–H bend", "center": 1630.0, "fwhm": 38.0, "color": "#17becf", "meaning": "Surface-physisorbed molecular water"},
            {"label": "ν_as(CO₃²⁻) Carbonate", "mode": "Surface CO₃²⁻", "center": 1522.0, "fwhm": 36.0, "color": "#ff7f0e", "meaning": "Bidentate surface carbonate from CO₂ chemisorption"},
            {"label": "ν_s(CO₃²⁻ / NO₃⁻)", "mode": "Sym Carbonate", "center": 1384.0, "fwhm": 32.0, "color": "#9467bd", "meaning": "Symmetric carbonate or residual nitrate precursor"},
            {"label": "ν_as(Si–O–Si)", "mode": "Siloxane asym", "center": 1085.0, "fwhm": 55.0, "color": "#1f77b4", "meaning": "Silica / aluminosilicate network asymmetric stretch"},
            {"label": "ν_s(Si–O) / M–OH", "mode": "Si–OH / Si–O", "center": 805.0, "fwhm": 30.0, "color": "#2ca02c", "meaning": "Symmetric Si–O–Si / surface silanol bending"},
            {"label": "ν(M–O) Metal Oxide", "mode": "M–O lattice", "center": 545.0, "fwhm": 50.0, "color": "#d62728", "meaning": "Bulk metal-oxygen (Ti–O / Cu–O / Fe–O) lattice mode"},
        ],
    },
}
