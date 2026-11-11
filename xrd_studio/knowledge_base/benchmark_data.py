"""
benchmark_data.py - Physics-informed synthetic XRD benchmark generators per materials domain.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

import numpy as np
import pandas as pd


def _pseudo_voigt(x: np.ndarray, center: float, fwhm: float, amp: float, eta: float = 0.45) -> np.ndarray:
    """Computes normalized-amplitude Pseudo-Voigt profile."""
    sigma = max(fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0))), 1e-4)
    gamma = max(fwhm / 2.0, 1e-4)
    gauss = np.exp(-0.5 * ((x - center) / sigma) ** 2)
    lorentz = (gamma ** 2) / ((x - center) ** 2 + gamma ** 2)
    return amp * (eta * lorentz + (1.0 - eta) * gauss)


def generate_benchmark_xrd(preset_name: str) -> pd.DataFrame:
    """Generates multi-sample synthetic benchmark XRD patterns tailored to the selected domain preset."""
    rng = np.random.default_rng(2026)

    if "UiO-66" in preset_name:
        two_theta = np.linspace(4.5, 35.0, 1600)
        bg = 240.0 * np.exp(-0.08 * (two_theta - 4.5)) + 90.0
        peaks_as_synth = [(7.36, 0.24, 4200), (8.48, 0.26, 1850), (12.01, 0.30, 720), (14.12, 0.32, 540), (14.74, 0.30, 610), (17.08, 0.34, 480), (25.68, 0.38, 950)]
        peaks_defective = [(7.38, 0.34, 3250), (8.50, 0.36, 1480), (12.03, 0.40, 560), (14.14, 0.42, 410), (14.76, 0.40, 470), (17.10, 0.44, 360), (25.70, 0.46, 760)]
        y1 = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.45) for c, w, a in peaks_as_synth) + rng.normal(0, 18, len(two_theta))
        y2 = bg * 1.15 + sum(_pseudo_voigt(two_theta, c, w, a, 0.55) for c, w, a in peaks_defective) + rng.normal(0, 18, len(two_theta))
        return pd.DataFrame({
            "TwoTheta_deg": two_theta,
            "UiO-66 Activated (Pristine)": np.maximum(y1, 0),
            "UiO-66 Modulated (Missing-Linker)": np.maximum(y2, 0),
        })

    if "ZIF-8" in preset_name or "HKUST-1" in preset_name:
        two_theta = np.linspace(4.5, 30.0, 1500)
        bg = 210.0 * np.exp(-0.09 * (two_theta - 4.5)) + 80.0
        if "ZIF-8" in preset_name:
            p1 = [(7.35, 0.22, 4800), (10.38, 0.24, 1450), (12.73, 0.25, 2150), (14.70, 0.28, 820), (16.44, 0.28, 980), (18.02, 0.30, 1280)]
            p2 = [(7.36, 0.31, 3600), (10.39, 0.33, 1120), (12.74, 0.34, 1680), (14.71, 0.36, 620), (16.45, 0.36, 740), (18.04, 0.38, 960)]
            names = ("ZIF-8 Microcrystals", "ZIF-8 Nano (<35 nm)")
        else:
            p1 = [(6.72, 0.24, 2600), (9.50, 0.26, 2200), (11.63, 0.28, 4500), (13.45, 0.30, 1350), (17.50, 0.34, 1100)]
            p2 = [(6.74, 0.34, 1750), (9.52, 0.36, 1520), (11.65, 0.38, 3050), (13.47, 0.40, 890), (17.52, 0.44, 710)]
            names = ("HKUST-1 Activated", "HKUST-1 Humid Aged")
        y1 = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.4) for c, w, a in p1) + rng.normal(0, 16, len(two_theta))
        y2 = bg * 1.2 + sum(_pseudo_voigt(two_theta, c, w, a, 0.5) for c, w, a in p2) + rng.normal(0, 16, len(two_theta))
        return pd.DataFrame({"TwoTheta_deg": two_theta, names[0]: np.maximum(y1, 0), names[1]: np.maximum(y2, 0)})

    if "Perovskite" in preset_name or "CsPbI" in preset_name:
        two_theta = np.linspace(9.0, 44.0, 1800)
        # Amorphous glass/substrate hump centered ~23 deg + low-angle air scatter
        bg = 180.0 * np.exp(-0.06 * (two_theta - 9.0)) + 260.0 * np.exp(-0.5 * ((two_theta - 23.0) / 5.5) ** 2) + 75.0
        fresh_peaks = [(12.67, 0.22, 260), (14.08, 0.20, 5200), (19.96, 0.25, 740), (24.48, 0.27, 820), (28.44, 0.24, 2650), (31.89, 0.28, 1280), (40.55, 0.30, 890)]
        aged_peaks = [(11.82, 0.26, 480), (12.67, 0.23, 2150), (14.10, 0.25, 3450), (19.98, 0.30, 490), (24.50, 0.31, 560), (28.46, 0.29, 1800), (31.91, 0.33, 860), (40.57, 0.36, 590)]
        y_fresh = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.5) for c, w, a in fresh_peaks) + rng.normal(0, 18, len(two_theta))
        y_aged = bg * 1.08 + sum(_pseudo_voigt(two_theta, c, w, a, 0.5) for c, w, a in aged_peaks) + rng.normal(0, 18, len(two_theta))
        return pd.DataFrame({
            "TwoTheta_deg": two_theta,
            "Fresh Perovskite Film": np.maximum(y_fresh, 0),
            "Light-Aged 500h (PbI₂)": np.maximum(y_aged, 0),
        })

    if "TiO₂" in preset_name or "Anatase" in preset_name:
        two_theta = np.linspace(20.0, 66.0, 1800)
        bg = 130.0 * np.exp(-0.04 * (two_theta - 20.0)) + 85.0
        p25 = [(25.28, 0.36, 4800), (27.45, 0.30, 1450), (36.08, 0.32, 620), (37.80, 0.38, 1050), (48.05, 0.40, 1520), (53.89, 0.42, 940), (55.06, 0.42, 910), (62.69, 0.45, 760)]
        rutile_rich = [(25.28, 0.33, 2350), (27.45, 0.26, 4300), (36.08, 0.28, 1750), (37.80, 0.35, 510), (48.05, 0.37, 740), (54.32, 0.32, 1950), (62.69, 0.42, 420)]
        y_p25 = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.45) for c, w, a in p25) + rng.normal(0, 18, len(two_theta))
        y_calc = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.55) for c, w, a in rutile_rich) + rng.normal(0, 18, len(two_theta))
        return pd.DataFrame({
            "TwoTheta_deg": two_theta,
            "TiO₂ P25 (Anatase-Rich)": np.maximum(y_p25, 0),
            "TiO₂ Calcined 750°C (Rutile-Rich)": np.maximum(y_calc, 0),
        })

    if "FCC" in preset_name or "Metal" in preset_name:
        two_theta = np.linspace(30.0, 80.0, 2000)
        bg = 110.0 * np.exp(-0.03 * (two_theta - 30.0)) + 65.0
        # Progressive strain + broadening: beta increases with tan(theta)
        cu_annealed = [(36.42, 0.44, 420), (43.30, 0.34, 4800), (50.43, 0.39, 2200), (61.34, 0.50, 250), (74.13, 0.49, 1380)]
        cu_strained = [(36.42, 0.50, 1250), (43.25, 0.52, 3900), (50.37, 0.61, 1780), (61.30, 0.65, 580), (74.04, 0.86, 1020)]
        y1 = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.45) for c, w, a in cu_annealed) + rng.normal(0, 15, len(two_theta))
        y2 = bg * 1.15 + sum(_pseudo_voigt(two_theta, c, w, a, 0.60) for c, w, a in cu_strained) + rng.normal(0, 16, len(two_theta))
        return pd.DataFrame({
            "TwoTheta_deg": two_theta,
            "Cu NPs Reduced (Low Strain)": np.maximum(y1, 0),
            "Cu/Cu₂O Catalyst (Strained)": np.maximum(y2, 0),
        })

    # Polymers, PAN & Carbon Nanofibers
    two_theta = np.linspace(10.0, 52.0, 1600)
    bg = 150.0 * np.exp(-0.04 * (two_theta - 10.0)) + 80.0
    pan_raw = [(16.92, 1.65, 3600), (25.45, 5.20, 1150), (29.50, 2.10, 780)]
    pan_stab = [(16.92, 2.30, 1050), (25.60, 4.10, 2850), (43.30, 4.50, 640)]
    cnf_carb = [(25.85, 3.30, 3900), (43.35, 3.70, 1250)]
    y_pan = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.15) for c, w, a in pan_raw) + rng.normal(0, 16, len(two_theta))
    y_stab = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.30) for c, w, a in pan_stab) + rng.normal(0, 16, len(two_theta))
    y_cnf = bg + sum(_pseudo_voigt(two_theta, c, w, a, 0.40) for c, w, a in cnf_carb) + rng.normal(0, 16, len(two_theta))
    return pd.DataFrame({
        "TwoTheta_deg": two_theta,
        "As-Spun PAN Nanofibers": np.maximum(y_pan, 0),
        "Oxidized 260°C (Ladder Polymer)": np.maximum(y_stab, 0),
        "Carbonized 900°C (CNFs)": np.maximum(y_cnf, 0),
    })
