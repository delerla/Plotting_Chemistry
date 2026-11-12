"""
solar_perovskites.py - Vibrational Spectroscopy Libraries for Halide Perovskites & Passivated Interfaces.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

SOLAR_PEROVSKITE_IR_PRESETS = {
    "FAPbI₃ / MAPbI₃ Perovskite + Lewis Base Passivation": {
        "domain": "solar_perovskites",
        "material_class": "Hybrid Organic-Inorganic Halide Perovskite",
        "roi_window": (1300.0, 1850.0),
        "default_line_shape": "Lorentzian",
        "key_diagnostic": "Tracks FA⁺ ν_as(C=N) at ~1712 cm⁻¹ (blue-shifts when α-FAPbI₃ converts to yellow δ-phase), MA⁺ δ_s(NH₃⁺) at 1468 cm⁻¹, and Lewis-base C=O coordination shifts (~1675–1730 cm⁻¹).",
        "bands": [
            {"label": "Free Additive ν(C=O)", "mode": "Free C=O", "center": 1735.0, "fwhm": 22.0, "color": "#ff7f0e", "meaning": "Uncoordinated ester/urea additive C=O stretch"},
            {"label": "FA⁺ ν_as(C=N)", "mode": "FA⁺ C=N", "center": 1712.0, "fwhm": 18.0, "color": "#1f77b4", "meaning": "Formamidinium C=N antisymmetric stretch (phase-sensitive)"},
            {"label": "Pb²⁺-Coord ν(C=O)", "mode": "Passivated C=O", "center": 1682.0, "fwhm": 24.0, "color": "#2ca02c", "meaning": "Red-shifted C=O bonded to undercoordinated Pb²⁺ defect"},
            {"label": "δ(H₂O) Moisture", "mode": "H–O–H bend", "center": 1622.0, "fwhm": 34.0, "color": "#d62728", "meaning": "Intercalated moisture bending mode"},
            {"label": "MA⁺ δ_s(NH₃⁺)", "mode": "MA⁺ NH₃⁺", "center": 1468.0, "fwhm": 20.0, "color": "#9467bd", "meaning": "Methylammonium symmetric ammonium bend"},
            {"label": "FA⁺ δ(NH₂) / ν(C–N)", "mode": "FA⁺ skeletal", "center": 1352.0, "fwhm": 24.0, "color": "#8c564b", "meaning": "Formamidinium N–H / C–N coupling"},
        ],
    },
}
