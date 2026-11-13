"""
uv_vis_studio.knowledge_base.benchmarks
Curated domain benchmarks for UV-Vis Spectroscopy, Photodegradation Kinetics, and Tauc Bandgap Analysis.
Covers Perovskites, Quantum Dots, Photocatalysts (RhB, MB, 4-NP), and Plasmonic Nanomaterials.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


UV_VIS_DOMAINS: Dict[str, Dict[str, Any]] = {
    "Photocatalysis: Rhodamine B (RhB) Degradation": {
        "material_class": "Photocatalyst (TiO2 / BiOBr)",
        "target_analyte": "Rhodamine B (RhB)",
        "lambda_max": 554.0,
        "mode": "kinetics",
        "description": "Photocatalytic degradation of RhB dye under simulated solar irradiation. Features spectral decay at 554 nm and N-deethylation hypsochromic shifts.",
        "expected_order": "Pseudo-First-Order",
        "reference": "KAUST Catalysis Center / ACS Appl. Mater. Interfaces"
    },
    "Photocatalysis: Methylene Blue (MB) Bleaching": {
        "material_class": "Polymer/MOF Nanocomposite (UiO-66 / g-C3N4)",
        "target_analyte": "Methylene Blue (MB)",
        "lambda_max": 664.0,
        "mode": "kinetics",
        "description": "Rapid photocatalytic decolorization of cationic dye MB. Shows monomer peak at 664 nm and dimer shoulder at 612 nm.",
        "expected_order": "Pseudo-First-Order",
        "reference": "KFUPM Center of Excellence in Nanotechnology"
    },
    "Catalytic Reduction: 4-Nitrophenol (4-NP) to 4-AP": {
        "material_class": "Noble Metal Nanocatalyst (Au/Pd NPs on MOF)",
        "target_analyte": "4-Nitrophenol / 4-Nitrophenolate",
        "lambda_max": 400.0,
        "mode": "kinetics",
        "description": "NaBH4-mediated reduction of 4-nitrophenolate (400 nm) to 4-aminophenol (300 nm). Features well-defined isosbestic points.",
        "expected_order": "Pseudo-First-Order",
        "reference": "KACST Advanced Materials Laboratory"
    },
    "Solar Perovskite: MAPbI3 Thin Film (Tauc Bandgap)": {
        "material_class": "Halide Perovskite (CH3NH3PbI3)",
        "target_analyte": "Direct Bandgap Optical Absorption",
        "lambda_max": 780.0,
        "mode": "tauc",
        "tauc_transition": "Direct Allowed (n=1/2)",
        "literature_bandgap_eV": 1.58,
        "description": "Optical absorbance spectrum of MAPbI3 perovskite for solar cells. Used for Tauc plot direct bandgap extrapolation and Urbach defect tail analysis.",
        "reference": "Nature Energy / KAU Photovoltaics Group"
    },
    "Quantum Dots: CsPbBr3 All-Inorganic Perovskite": {
        "material_class": "Colloidal Perovskite Nanocrystals (CsPbBr3)",
        "target_analyte": "Exciton Absorption & Bandgap",
        "lambda_max": 510.0,
        "mode": "tauc",
        "tauc_transition": "Direct Allowed (n=1/2)",
        "literature_bandgap_eV": 2.38,
        "description": "Green-emitting perovskite quantum dots with sharp excitonic absorption peak at 505-512 nm and steep absorption edge.",
        "reference": "IAU College of Science / ACS Nano"
    },
    "Semiconductor Oxide: TiO2 / ZnO Nanoparticles": {
        "material_class": "Wide-Bandgap Metal Oxide (Anatase TiO2)",
        "target_analyte": "Indirect Optical Bandgap",
        "lambda_max": 380.0,
        "mode": "tauc",
        "tauc_transition": "Indirect Allowed (n=2)",
        "literature_bandgap_eV": 3.20,
        "description": "UV-active semiconductor benchmark. Indirect transition extrapolation of (alpha*hv)^0.5 vs photon energy.",
        "reference": "Materials Chemistry & Physics"
    },
    "Plasmonics: Gold Nanorods (Transverse & Longitudinal LSPR)": {
        "material_class": "Plasmonic Nanomaterials (Au NRs)",
        "target_analyte": "Surface Plasmon Resonance",
        "lambda_max": 780.0,
        "mode": "plasmon",
        "description": "Colloidal gold nanorods displaying transverse LSPR (~520 nm) and tunable longitudinal LSPR (~780 nm) for photothermal applications.",
        "reference": "Nano Letters / KAUST Core Labs"
    }
}


def generate_rhb_kinetics() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generates synthetic high-fidelity benchmark spectra for Rhodamine B degradation."""
    wavelengths = np.linspace(350, 750, 1000)
    times = [0, 10, 20, 30, 45, 60, 90, 120]
    c0 = 10.0
    k_true = 0.0245

    np.random.seed(42)
    spectra_dict = {"Wavelength_nm": wavelengths}
    kinetics_rows = []

    for t in times:
        c_t = c0 * np.exp(-k_true * t)
        frac = c_t / c0
        # Hypsochromic shift as deethylation occurs: peak shifts from 554 to 548 nm
        peak_center = 554.0 - (1.0 - frac) * 6.0
        a_main = 1.72 * frac * np.exp(-0.5 * ((wavelengths - peak_center) / 26.0) ** 2)
        a_shoulder = 0.58 * frac * np.exp(-0.5 * ((wavelengths - 518) / 18.0) ** 2)
        base = 0.035 + 0.012 * np.exp(-0.004 * (wavelengths - 350))
        noise = np.random.normal(0, 0.003, len(wavelengths))
        
        abs_spectrum = np.clip(a_main + a_shoulder + base + noise, 0, None)
        spectra_dict[f"{t} min"] = abs_spectrum
        
        idx_max = np.argmin(np.abs(wavelengths - 554.0))
        kinetics_rows.append({
            "Time_min": t,
            "Concentration_mg_L": round(c_t, 3),
            "Absorbance_at_554nm": round(float(abs_spectrum[idx_max]), 4)
        })

    return pd.DataFrame(spectra_dict), pd.DataFrame(kinetics_rows)


def generate_methylene_blue_kinetics() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generates benchmark spectra for Methylene Blue degradation."""
    wavelengths = np.linspace(400, 800, 1000)
    times = [0, 15, 30, 45, 60, 90, 120]
    c0 = 15.0
    k_true = 0.0210

    np.random.seed(101)
    spectra_dict = {"Wavelength_nm": wavelengths}
    kinetics_rows = []

    for t in times:
        c_t = c0 * np.exp(-k_true * t)
        frac = c_t / c0
        a_monomer = 1.85 * frac * np.exp(-0.5 * ((wavelengths - 664.0) / 24.0) ** 2)
        a_dimer = 0.95 * frac * np.exp(-0.5 * ((wavelengths - 612.0) / 20.0) ** 2)
        base = 0.04
        noise = np.random.normal(0, 0.003, len(wavelengths))
        
        abs_spectrum = np.clip(a_monomer + a_dimer + base + noise, 0, None)
        spectra_dict[f"{t} min"] = abs_spectrum
        
        idx_max = np.argmin(np.abs(wavelengths - 664.0))
        kinetics_rows.append({
            "Time_min": t,
            "Concentration_mg_L": round(c_t, 3),
            "Absorbance_at_664nm": round(float(abs_spectrum[idx_max]), 4)
        })

    return pd.DataFrame(spectra_dict), pd.DataFrame(kinetics_rows)


def generate_mapbi3_tauc_spectrum() -> pd.DataFrame:
    """Generates synthetic absorbance and transmittance spectrum for MAPbI3 perovskite."""
    wavelengths = np.linspace(350, 950, 1200)
    h_c = 1239.84193  # nm * eV
    hv = h_c / wavelengths  # eV
    
    eg_true = 1.58  # eV
    eu_true = 0.016  # Urbach energy in eV (16 meV)
    
    # Absorption coefficient model:
    # Above Eg: sqrt(hv - Eg)
    # Below Eg: Urbach tail exp((hv - Eg)/Eu)
    alpha = np.zeros_like(hv)
    for i, e in enumerate(hv):
        if e >= eg_true:
            alpha[i] = 2.4e4 * np.sqrt(e - eg_true) + 3.0e3 * (e - eg_true) + 1.2e3
        else:
            alpha[i] = 1.2e3 * np.exp((e - eg_true) / eu_true)
            
    # Convert alpha to simulated optical absorbance (assuming thickness d ~ 300 nm)
    d_cm = 300e-7  # 300 nm in cm
    absorbance = (alpha * d_cm) / np.log(10)
    absorbance += 0.03 + np.random.normal(0, 0.002, len(wavelengths))
    absorbance = np.clip(absorbance, 0.001, None)
    
    # Transmittance: T = 10^(-A)
    transmittance = 10 ** (-absorbance) * 100.0

    return pd.DataFrame({
        "Wavelength_nm": wavelengths,
        "Absorbance_OD": np.round(absorbance, 4),
        "Transmittance_pct": np.round(transmittance, 2),
        "Photon_Energy_eV": np.round(hv, 4)
    })


def generate_tio2_tauc_spectrum() -> pd.DataFrame:
    """Generates synthetic absorbance spectrum for Anatase TiO2 (Indirect bandgap ~3.20 eV)."""
    wavelengths = np.linspace(300, 600, 1000)
    h_c = 1239.84193
    hv = h_c / wavelengths
    eg_true = 3.20
    
    alpha = np.zeros_like(hv)
    for i, e in enumerate(hv):
        if e >= eg_true:
            alpha[i] = 1.8e4 * ((e - eg_true) ** 2) + 800.0
        else:
            alpha[i] = 800.0 * np.exp((e - eg_true) / 0.060)
            
    d_cm = 400e-7
    absorbance = (alpha * d_cm) / np.log(10)
    absorbance += 0.02 + np.random.normal(0, 0.002, len(wavelengths))
    absorbance = np.clip(absorbance, 0.001, None)

    return pd.DataFrame({
        "Wavelength_nm": wavelengths,
        "Absorbance_OD": np.round(absorbance, 4),
        "Photon_Energy_eV": np.round(hv, 4)
    })


def generate_gold_nanorods_spectrum() -> pd.DataFrame:
    """Generates synthetic spectrum for Au Nanorods with transverse and longitudinal LSPR."""
    wavelengths = np.linspace(400, 950, 1000)
    # Transverse SPR at 520 nm
    t_spr = 0.55 * np.exp(-0.5 * ((wavelengths - 520.0) / 22.0) ** 2)
    # Longitudinal SPR at 785 nm
    l_spr = 1.65 * np.exp(-0.5 * ((wavelengths - 785.0) / 45.0) ** 2)
    base = 0.08 + 0.04 * np.exp(-0.005 * (wavelengths - 400))
    noise = np.random.normal(0, 0.003, len(wavelengths))
    
    absorbance = np.clip(t_spr + l_spr + base + noise, 0, None)
    return pd.DataFrame({
        "Wavelength_nm": wavelengths,
        "Absorbance_OD": np.round(absorbance, 4)
    })
