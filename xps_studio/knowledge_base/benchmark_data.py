"""
benchmark_data.py - High-Fidelity Synthetic Benchmarks for MOFs, Solar Cells & PAN Polymers
Enables immediate 1-click testing and demonstration of domain intelligence.
"""

import numpy as np
import pandas as pd


def generate_benchmark_mof_c1s() -> pd.DataFrame:
    """Generates synthetic high-resolution C 1s spectrum for UiO-66 (Zr-BDC) MOF."""
    np.random.seed(42)
    be = np.linspace(293.0, 281.0, 400)
    
    # 4 components: Aromatic C-C (284.8), C-O defect (286.2), Carboxylate O-C=O (288.7), Shake-up (291.5)
    p1 = 35000.0 * np.exp(-4.0 * np.log(2.0) * ((be - 284.8) / 0.85) ** 2)
    p2 = 6200.0 * np.exp(-4.0 * np.log(2.0) * ((be - 286.2) / 0.90) ** 2)
    p3 = 11800.0 * np.exp(-4.0 * np.log(2.0) * ((be - 288.7) / 0.95) ** 2)
    p4 = 1500.0 * np.exp(-4.0 * np.log(2.0) * ((be - 291.5) / 1.50) ** 2)
    
    # Shirley-like background
    bg = 2800.0 + 3500.0 / (1.0 + np.exp((be - 285.5) / 1.2))
    noise = np.random.normal(0, 180.0, len(be))
    cps = p1 + p2 + p3 + p4 + bg + noise
    
    return pd.DataFrame({'Binding_Energy_eV': be, 'Counts_Per_Second': np.maximum(cps, 100.0)})


def generate_benchmark_solar_pb4f() -> pd.DataFrame:
    """Generates synthetic Pb 4f spectrum for degraded perovskite film with metallic Pb0 defects."""
    np.random.seed(101)
    be = np.linspace(146.0, 134.0, 450)
    
    # Pb2+ doublet: 4f7/2 (138.4 eV), 4f5/2 (143.26 eV) with 4:3 area ratio
    pb2_72 = 28000.0 * np.exp(-4.0 * np.log(2.0) * ((be - 138.40) / 0.80) ** 2)
    pb2_52 = (28000.0 / 1.333) * np.exp(-4.0 * np.log(2.0) * ((be - 143.26) / 0.80) ** 2)
    
    # Metallic Pb0 defect doublet (136.60 eV & 141.46 eV)
    pb0_72 = 2900.0 * np.exp(-4.0 * np.log(2.0) * ((be - 136.60) / 0.72) ** 2)
    pb0_52 = (2900.0 / 1.333) * np.exp(-4.0 * np.log(2.0) * ((be - 141.46) / 0.72) ** 2)
    
    bg = 1500.0 + 3200.0 / (1.0 + np.exp((be - 139.5) / 1.5))
    noise = np.random.normal(0, 150.0, len(be))
    cps = pb2_72 + pb2_52 + pb0_72 + pb0_52 + bg + noise
    
    return pd.DataFrame({'Binding_Energy_eV': be, 'Counts_Per_Second': np.maximum(cps, 100.0)})


def generate_benchmark_pan_n1s() -> pd.DataFrame:
    """Generates synthetic N 1s spectrum for thermally stabilized electrospun PAN nanofibers."""
    np.random.seed(88)
    be = np.linspace(405.0, 395.0, 350)
    
    # Nitrile (399.4 eV), Cyclized imine (398.5 eV), Amide (400.5 eV), Oxidized N (402.0 eV)
    p_nitrile = 18500.0 * np.exp(-4.0 * np.log(2.0) * ((be - 399.4) / 0.88) ** 2)
    p_imine = 7800.0 * np.exp(-4.0 * np.log(2.0) * ((be - 398.5) / 0.88) ** 2)
    p_amide = 2400.0 * np.exp(-4.0 * np.log(2.0) * ((be - 400.5) / 0.95) ** 2)
    p_ox = 1100.0 * np.exp(-4.0 * np.log(2.0) * ((be - 402.0) / 1.20) ** 2)
    
    bg = 1200.0 + 1600.0 / (1.0 + np.exp((be - 399.0) / 1.1))
    noise = np.random.normal(0, 110.0, len(be))
    cps = p_nitrile + p_imine + p_amide + p_ox + bg + noise
    
    return pd.DataFrame({'Binding_Energy_eV': be, 'Counts_Per_Second': np.maximum(cps, 80.0)})
