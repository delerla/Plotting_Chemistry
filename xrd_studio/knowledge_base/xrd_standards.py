"""
xrd_standards.py - Fundamental X-ray wavelengths, instrument standards, and crystallographic constants.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

ANODE_WAVELENGTHS = {
    "Cu Kα₁ (1.54060 Å)": {
        "lambda_A": 1.540598,
        "lambda_nm": 0.1540598,
        "ka2_A": 1.544426,
        "ka_ratio": 0.5,
        "description": "Monochromated or Kβ-filtered Cu Kα₁ source (standard laboratory diffractometer)",
    },
    "Cu Kα Weighted (1.54184 Å)": {
        "lambda_A": 1.54184,
        "lambda_nm": 0.154184,
        "ka2_A": 1.544426,
        "ka_ratio": 0.0,
        "description": "Weighted Cu Kα₁,₂ unresolved doublet (2:1 average)",
    },
    "Co Kα₁ (1.78897 Å)": {
        "lambda_A": 1.78897,
        "lambda_nm": 0.178897,
        "ka2_A": 1.79285,
        "ka_ratio": 0.5,
        "description": "Co anode for Fe/Mn/Co-rich catalysts & batteries (avoids Fe fluorescence)",
    },
    "Mo Kα₁ (0.70930 Å)": {
        "lambda_A": 0.70930,
        "lambda_nm": 0.070930,
        "ka2_A": 0.71359,
        "ka_ratio": 0.5,
        "description": "Short-wavelength Mo source for high-Q PDF / thick MOFs & perovskites",
    },
    "Cr Kα₁ (2.28970 Å)": {
        "lambda_A": 2.28970,
        "lambda_nm": 0.228970,
        "ka2_A": 2.29361,
        "ka_ratio": 0.5,
        "description": "Long-wavelength Cr source for high dispersion of low-angle Bragg peaks",
    },
    "Fe Kα₁ (1.93604 Å)": {
        "lambda_A": 1.93604,
        "lambda_nm": 0.193604,
        "ka2_A": 1.93998,
        "ka_ratio": 0.5,
        "description": "Fe anode source for Mn/Cr steels and ferrites",
    },
}

CALIBRATION_STANDARDS = {
    "None (Raw 2θ)": None,
    "Si (111) Standard (28.443°)": 28.443,
    "LaB₆ NIST 660c (110) (30.385°)": 30.385,
    "FTO Substrate SnO₂ (110) (26.580°)": 26.580,
    "FTO Substrate SnO₂ (101) (33.770°)": 33.770,
    "Corundum α-Al₂O₃ (104) (35.152°)": 35.152,
    "Custom Reference Peak": "custom",
}

INSTRUMENT_BROADENING_PRESETS = {
    "None / Ideal (0.00°)": 0.00,
    "High-Resolution LaB₆ / Synchrotron-Like (0.05°)": 0.05,
    "Standard Bragg-Brentano (0.09°)": 0.09,
    "Routine Powder Benchtop (0.14°)": 0.14,
}
