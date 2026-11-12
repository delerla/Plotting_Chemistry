"""
ir_standards.py - Fundamental Infrared Spectral Regions, Functional Group Libraries & Artifacts.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

IR_SPECTRAL_REGIONS = {
    "O–H / N–H Hydrogen-Bonding": (3650.0, 3100.0),
    "Aliphatic / Aromatic C–H": (3100.0, 2800.0),
    "Atmospheric CO₂ Artifact Band": (2390.0, 2295.0),
    "Triple-Bond Region (C≡N, C≡C)": (2270.0, 2100.0),
    "Carbonyl C=O (Acids, Esters, Ketones)": (1780.0, 1660.0),
    "Amide I / Imine C=N / Carboxylate ν_as": (1660.0, 1520.0),
    "Carboxylate ν_s / CH₂–CH₃ Bending": (1520.0, 1320.0),
    "Fingerprint C–O / C–N / Si–O–Si": (1320.0, 900.0),
    "Out-of-Plane Ring & M–O Lattice": (900.0, 400.0),
}

CO2_MASK_RANGE = (2295.0, 2390.0)
