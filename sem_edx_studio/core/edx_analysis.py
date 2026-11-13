"""
sem_edx_studio.core.edx_analysis
Energy-Dispersive X-Ray Spectroscopy (EDX) Microanalysis & Elemental Quantification.
Matches characteristic X-ray lines (Kα, Lα, Mα), performs background stripping,
computes Weight % and Atomic %, and evaluates stoichiometric ratios.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
try:
    from scipy.integrate import trapezoid as _trapz
except ImportError:
    _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))


CHARACTERISTIC_LINES: Dict[str, float] = {
    'C Kα': 0.277,
    'N Kα': 0.392,
    'O Kα': 0.525,
    'F Kα': 0.677,
    'Na Kα': 1.041,
    'Mg Kα': 1.253,
    'Al Kα': 1.486,
    'Si Kα': 1.739,
    'P Kα': 2.013,
    'S Kα': 2.307,
    'Cl Kα': 2.621,
    'K Kα': 3.312,
    'Ca Kα': 3.690,
    'Ti Kα': 4.510,
    'Cr Kα': 5.411,
    'Mn Kα': 5.898,
    'Fe Kα': 6.398,
    'Co Kα': 6.924,
    'Ni Kα': 7.471,
    'Cu Kα': 8.040,
    'Zn Kα': 8.630,
    'Zr Lα': 2.042,
    'Zr Lβ': 2.124,
    'I Lα': 3.937,
    'I Lβ': 4.221,
    'Pb Mα': 2.342,
    'Pb Lα': 10.551,
    'Pt Mα': 2.048,
    'Au Mα': 2.120,
    'Au Lα': 9.713,
}

ATOMIC_WEIGHTS: Dict[str, float] = {
    'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998, 'Na': 22.990,
    'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974, 'S': 32.065,
    'Cl': 35.453, 'K': 39.098, 'Ca': 40.078, 'Ti': 47.867, 'Cr': 51.996,
    'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546,
    'Zn': 65.380, 'Zr': 91.224, 'I': 126.904, 'Pt': 195.084, 'Au': 196.967,
    'Pb': 207.200,
}


def analyze_edx_spectrum(
    df_edx: pd.DataFrame,
    peak_prominence: float = 80.0,
    target_elements: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Identifies elemental peaks, calculates net integrated intensities,
    and returns quantified Weight % and Atomic %.
    """
    energy = df_edx.iloc[:, 0].to_numpy().astype(float)
    counts = df_edx.iloc[:, 1].to_numpy().astype(float)

    # Estimate background using polynomial baseline
    bg = 300.0 * np.exp(-0.45 * np.maximum(energy, 0.1)) + 25.0 / (energy + 0.2)
    net_counts = np.clip(counts - bg, 0, None)

    # Peak finding
    peaks_idx, props = find_peaks(counts, prominence=peak_prominence, distance=15)

    detected_elements: List[Dict[str, Any]] = []
    matched_element_names = set()

    for idx in peaks_idx:
        e_peak = float(energy[idx])
        c_peak = float(counts[idx])

        # Match with characteristic lines within 0.08 keV tolerance
        best_match = None
        min_dist = 0.09
        for line_name, line_e in CHARACTERISTIC_LINES.items():
            dist = abs(e_peak - line_e)
            if dist < min_dist:
                min_dist = dist
                best_match = (line_name, line_e)

        if best_match is not None:
            elem_sym = best_match[0].split()[0]
            # If target_elements is given, only accept specified elements
            if target_elements is not None and elem_sym not in target_elements:
                continue

            # Estimate net peak area using local window
            w = 8
            i_start = max(0, idx - w)
            i_end = min(len(energy), idx + w + 1)
            area = float(_trapz(net_counts[i_start:i_end], energy[i_start:i_end]))

            detected_elements.append({
                "Element": elem_sym,
                "Line": best_match[0],
                "Peak_Energy_keV": round(e_peak, 3),
                "Library_Energy_keV": round(best_match[1], 3),
                "Net_Area": max(area, 10.0),
                "Peak_Counts": round(c_peak, 1)
            })
            matched_element_names.add(elem_sym)

    if not detected_elements:
        return {
            "df_quant": pd.DataFrame(),
            "detected_peaks": [],
            "stoichiometry": {},
            "energy": energy,
            "counts": counts,
            "background": bg
        }

    # Aggregate by element (sum net areas if multiple lines detected)
    elem_dict = {}
    for item in detected_elements:
        elem = item["Element"]
        elem_dict[elem] = elem_dict.get(elem, 0.0) + item["Net_Area"]

    # Quantitative calculation: Weight % and Atomic %
    total_area = sum(elem_dict.values())
    quant_rows = []
    for elem, area in elem_dict.items():
        wt_pct = (area / max(total_area, 1e-6)) * 100.0
        at_weight = ATOMIC_WEIGHTS.get(elem, 50.0)
        quant_rows.append({
            "Element": elem,
            "Net_Intensity": round(area, 1),
            "Weight_pct": wt_pct,
            "Atomic_Weight": at_weight,
            "Atomic_Moles": wt_pct / at_weight
        })

    df_quant = pd.DataFrame(quant_rows)
    total_moles = df_quant["Atomic_Moles"].sum()
    df_quant["Atomic_pct"] = (df_quant["Atomic_Moles"] / max(total_moles, 1e-8)) * 100.0
    df_quant["Weight_pct"] = df_quant["Weight_pct"].round(2)
    df_quant["Atomic_pct"] = df_quant["Atomic_pct"].round(2)
    df_quant = df_quant.drop(columns=["Atomic_Moles"])

    # Calculate key stoichiometric ratios
    stoichiometry = {}
    at_map = dict(zip(df_quant["Element"], df_quant["Atomic_pct"]))
    if "I" in at_map and "Pb" in at_map and at_map["Pb"] > 0:
        stoichiometry["I_to_Pb"] = round(at_map["I"] / at_map["Pb"], 2)
    if "Zr" in at_map and "C" in at_map and at_map["C"] > 0:
        stoichiometry["Zr_to_C"] = round(at_map["Zr"] / at_map["C"], 3)
    if "Zn" in at_map and "N" in at_map and at_map["N"] > 0:
        stoichiometry["Zn_to_N"] = round(at_map["Zn"] / at_map["N"], 3)

    return {
        "df_quant": df_quant,
        "detected_peaks": detected_elements,
        "stoichiometry": stoichiometry,
        "energy": energy,
        "counts": counts,
        "background": bg
    }
