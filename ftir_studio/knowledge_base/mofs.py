"""
mofs.py - Vibrational Spectroscopy Libraries for MOFs & Reticular Carboxylate Frameworks.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

MOF_IR_PRESETS = {
    "UiO-66 (Zr-BDC) & Linker-Defect Analysis": {
        "domain": "mofs",
        "material_class": "Zirconium Terephthalate MOF (fcu topology)",
        "roi_window": (500.0, 1850.0),
        "default_line_shape": "Gaussian",
        "key_diagnostic": "Uses Deacon splitting Δν = ν_as(COO⁻) − ν_s(COO⁻) (~180 cm⁻¹ bridging bidentate) and scans ~1695 cm⁻¹ for uncoordinated residual H₂BDC acid linker inside pores.",
        "bands": [
            {"label": "Free H₂BDC ν(C=O)", "mode": "Uncoord. Acid", "center": 1692.0, "fwhm": 26.0, "color": "#d62728", "meaning": "Residual unwashed terephthalic acid or dangling linker -COOH"},
            {"label": "ν_as(COO⁻) Carboxylate", "mode": "COO⁻ asym", "center": 1582.0, "fwhm": 32.0, "color": "#1f77b4", "meaning": "In-phase asymmetric carboxylate stretch bound to Zr₆ cluster"},
            {"label": "ν(C=C) Phenyl Ring", "mode": "Aromatic C=C", "center": 1506.0, "fwhm": 20.0, "color": "#2ca02c", "meaning": "1,4-benzene dicarboxylate aromatic skeletal vibration"},
            {"label": "ν_s(COO⁻) Carboxylate", "mode": "COO⁻ sym", "center": 1396.0, "fwhm": 30.0, "color": "#ff7f0e", "meaning": "Symmetric carboxylate stretch bound to Zr₆ node"},
            {"label": "δ(C–H) In-Plane Ring", "mode": "Ring C–H", "center": 1156.0, "fwhm": 22.0, "color": "#9467bd", "meaning": "BDC phenyl ring C–H deformation"},
            {"label": "μ₃-OH / Zr–O–Zr", "mode": "Node μ₃-O/OH", "center": 745.0, "fwhm": 28.0, "color": "#8c564b", "meaning": "Characteristic Zr₆(μ₃-O)₄(μ₃-OH)₄ cluster & C–H oop"},
            {"label": "ν(Zr–O) Cluster", "mode": "Zr–O stretch", "center": 662.0, "fwhm": 26.0, "color": "#17becf", "meaning": "Zr–(OC) longitudinal node framework mode"},
        ],
    },
    "HKUST-1 (Cu-BTC) & ZIF-8 Frameworks": {
        "domain": "mofs",
        "material_class": "Copper Trimesate / Imidazolate MOF",
        "roi_window": (600.0, 1800.0),
        "default_line_shape": "Gaussian",
        "key_diagnostic": "Verifies paddlewheel carboxylate bridging (~1645 / ~1375 cm⁻¹) and C–N/C–H ring preservation without hydrated linker protonation (~1710 cm⁻¹).",
        "bands": [
            {"label": "ν_as(COO⁻) Paddlewheel", "mode": "COO⁻ asym", "center": 1642.0, "fwhm": 30.0, "color": "#1f77b4", "meaning": "Cu₂(COO)₄ paddlewheel asymmetric carboxylate stretch"},
            {"label": "ν(C=C) Trimesate Ring", "mode": "Aromatic C=C", "center": 1552.0, "fwhm": 24.0, "color": "#2ca02c", "meaning": "1,3,5-benzenetricarboxylate ring stretch"},
            {"label": "ν_s(COO⁻) Trimesate", "mode": "COO⁻ sym", "center": 1374.0, "fwhm": 28.0, "color": "#ff7f0e", "meaning": "Symmetric coordinated carboxylate mode"},
            {"label": "ν(C–O) Carboxylate", "mode": "C–O stretch", "center": 1110.0, "fwhm": 24.0, "color": "#9467bd", "meaning": "Trimesate C–O skeletal mode"},
            {"label": "γ(C–H) Out-of-Plane", "mode": "Ring oop", "center": 728.0, "fwhm": 22.0, "color": "#d62728", "meaning": "Tri-substituted benzene out-of-plane C–H bend"},
        ],
    },
}
