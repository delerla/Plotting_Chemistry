"""
scofield_rsf.py - Scofield Relative Sensitivity Factors (Al Kα X-ray source, 1486.6 eV)
Standard empirical and theoretical cross-sections relative to C 1s = 1.000.
Used for quantitative elemental atomic percentage (at%) calculations.
"""

SCOFIELD_RSF = {
    # Core levels: Element_Orbital: RSF
    'C 1s': 1.000,
    'O 1s': 2.930,
    'N 1s': 1.800,
    'F 1s': 4.430,
    'Cl 2p': 2.285,
    'Cl 2p3/2': 1.520,
    'Br 3d': 2.840,
    'I 3d': 19.50,
    'I 3d5/2': 11.50,
    'S 2p': 1.680,
    'P 2p': 1.190,
    'Si 2p': 0.817,
    'Ti 2p': 7.910,
    'Ti 2p3/2': 5.220,
    'V 2p3/2': 6.370,
    'Cr 2p3/2': 7.690,
    'Mn 2p3/2': 9.170,
    'Fe 2p3/2': 10.82,
    'Co 2p3/2': 12.64,
    'Ni 2p3/2': 14.61,
    'Cu 2p3/2': 16.73,
    'Zn 2p': 18.92,
    'Zn 2p3/2': 12.60,
    'Zr 3d': 7.040,
    'Zr 3d5/2': 4.140,
    'Mo 3d': 9.500,
    'Mo 3d5/2': 5.620,
    'Ru 3d5/2': 7.420,
    'Pd 3d5/2': 9.530,
    'Ag 3d5/2': 10.66,
    'Sn 3d': 25.10,
    'Sn 3d5/2': 14.80,
    'Cs 3d5/2': 18.40,
    'Ce 3d5/2': 28.50,
    'Au 4f': 17.10,
    'Au 4f7/2': 9.580,
    'Pt 4f': 15.30,
    'Pt 4f7/2': 8.570,
    'Pb 4f': 22.75,
    'Pb 4f7/2': 12.80,
    'Bi 4f7/2': 14.40,
}


def get_rsf(core_level: str) -> float:
    """Returns Scofield RSF value, defaulting to 1.00 if unlisted."""
    for key, val in SCOFIELD_RSF.items():
        if key.lower() == core_level.lower():
            return val
        if core_level.lower().replace(" ", "") == key.lower().replace(" ", ""):
            return val
    return 1.000
