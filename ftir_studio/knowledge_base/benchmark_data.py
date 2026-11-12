"""
benchmark_data.py - Physics-informed synthetic FTIR spectra benchmarks (%T) per materials domain.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

import numpy as np
import pandas as pd


def _gauss_band(x: np.ndarray, center: float, fwhm: float, amp: float) -> np.ndarray:
    sigma = max(fwhm / 2.35482, 1.0)
    return amp * np.exp(-0.5 * ((x - center) / sigma) ** 2)


def generate_benchmark_ftir(preset_name: str) -> pd.DataFrame:
    """Generates multi-sample synthetic FTIR transmittance (%T) spectra descending 4000 -> 400 cm-1."""
    rng = np.random.default_rng(2026)
    wn = np.linspace(4000.0, 400.0, 1800)

    def _to_transmittance(abs_curve: np.ndarray, slope_tilt: float = 0.0) -> np.ndarray:
        a = np.maximum(abs_curve + slope_tilt * (wn - 400.0) / 3600.0 + 0.015, 0.0)
        t_pct = 100.0 * (10.0 ** (-a)) + rng.normal(0.0, 0.18, len(wn))
        return np.clip(t_pct, 2.0, 100.0)

    if "Polymer / Metal-Salt" in preset_name or "Ni/Cu/Co" in preset_name:
        a1 = _gauss_band(wn, 2935, 55, 0.14) + _gauss_band(wn, 2245, 18, 0.24) + _gauss_band(wn, 1454, 26, 0.17) + _gauss_band(wn, 1368, 28, 0.11)
        a2 = _gauss_band(wn, 3320, 220, 0.22) + _gauss_band(wn, 2935, 55, 0.13) + _gauss_band(wn, 2245, 18, 0.19) + _gauss_band(wn, 1635, 38, 0.28) + _gauss_band(wn, 1454, 26, 0.14) + _gauss_band(wn, 1385, 34, 0.24) + _gauss_band(wn, 1295, 32, 0.16)
        a3 = _gauss_band(wn, 3290, 200, 0.18) + _gauss_band(wn, 2935, 55, 0.13) + _gauss_band(wn, 2245, 18, 0.18) + _gauss_band(wn, 1612, 34, 0.25) + _gauss_band(wn, 1454, 26, 0.18) + _gauss_band(wn, 1309, 30, 0.19) + _gauss_band(wn, 1071, 35, 0.15)
        return pd.DataFrame({
            "Wavenumber_cm-1": wn,
            "Pristine PAN Polymer": _to_transmittance(a1, 0.02),
            "PAN + Ni NPs Complex": _to_transmittance(a2, 0.03),
            "PAN + Cu NPs Complex": _to_transmittance(a3, 0.025),
        })

    if "PAN" in preset_name or "Stabilization" in preset_name:
        a_raw = _gauss_band(wn, 2938, 52, 0.16) + _gauss_band(wn, 2243, 18, 0.34) + _gauss_band(wn, 1453, 26, 0.20) + _gauss_band(wn, 1368, 28, 0.11)
        a_240 = _gauss_band(wn, 3340, 210, 0.08) + _gauss_band(wn, 2935, 55, 0.10) + _gauss_band(wn, 2243, 19, 0.19) + _gauss_band(wn, 1715, 34, 0.12) + _gauss_band(wn, 1598, 46, 0.25) + _gauss_band(wn, 1453, 28, 0.14) + _gauss_band(wn, 1368, 30, 0.15) + _gauss_band(wn, 1265, 36, 0.12)
        a_280 = _gauss_band(wn, 3360, 220, 0.10) + _gauss_band(wn, 2243, 20, 0.06) + _gauss_band(wn, 1715, 36, 0.15) + _gauss_band(wn, 1596, 52, 0.40) + _gauss_band(wn, 1372, 36, 0.24) + _gauss_band(wn, 1265, 38, 0.20)
        return pd.DataFrame({
            "Wavenumber_cm-1": wn,
            "As-Spun PAN Nanofibers": _to_transmittance(a_raw, 0.015),
            "Stabilized 240°C": _to_transmittance(a_240, 0.03),
            "Stabilized 280°C": _to_transmittance(a_280, 0.045),
        })

    if "UiO-66" in preset_name or "HKUST" in preset_name:
        if "HKUST" in preset_name:
            a1 = _gauss_band(wn, 3420, 240, 0.15) + _gauss_band(wn, 1642, 30, 0.36) + _gauss_band(wn, 1552, 24, 0.22) + _gauss_band(wn, 1374, 28, 0.38) + _gauss_band(wn, 1110, 24, 0.14) + _gauss_band(wn, 728, 22, 0.26)
            a2 = _gauss_band(wn, 3420, 260, 0.34) + _gauss_band(wn, 1708, 26, 0.16) + _gauss_band(wn, 1642, 32, 0.28) + _gauss_band(wn, 1552, 24, 0.18) + _gauss_band(wn, 1374, 28, 0.30) + _gauss_band(wn, 728, 22, 0.20)
            names = ("HKUST-1 Activated", "HKUST-1 Hydrated")
        else:
            a1 = _gauss_band(wn, 3440, 210, 0.09) + _gauss_band(wn, 1582, 32, 0.38) + _gauss_band(wn, 1506, 20, 0.26) + _gauss_band(wn, 1396, 30, 0.42) + _gauss_band(wn, 1156, 22, 0.13) + _gauss_band(wn, 745, 28, 0.24) + _gauss_band(wn, 662, 26, 0.22)
            a2 = a1 * 0.90 + _gauss_band(wn, 1692, 26, 0.22)
            names = ("UiO-66 Clean Framework", "UiO-66 Unwashed (Free H₂BDC)")
        return pd.DataFrame({
            "Wavenumber_cm-1": wn,
            names[0]: _to_transmittance(a1, 0.02),
            names[1]: _to_transmittance(a2, 0.025),
        })

    if "Perovskite" in preset_name or "Passivation" in preset_name:
        a_ctrl = _gauss_band(wn, 3380, 180, 0.06) + _gauss_band(wn, 1712, 18, 0.34) + _gauss_band(wn, 1622, 34, 0.10) + _gauss_band(wn, 1468, 20, 0.22) + _gauss_band(wn, 1352, 24, 0.19)
        a_pass = _gauss_band(wn, 3380, 180, 0.04) + _gauss_band(wn, 1735, 22, 0.14) + _gauss_band(wn, 1712, 18, 0.34) + _gauss_band(wn, 1682, 24, 0.24) + _gauss_band(wn, 1622, 34, 0.05) + _gauss_band(wn, 1468, 20, 0.22) + _gauss_band(wn, 1352, 24, 0.19)
        return pd.DataFrame({
            "Wavenumber_cm-1": wn,
            "Control Perovskite Film": _to_transmittance(a_ctrl, 0.015),
            "Passivated Perovskite (C=O Bound)": _to_transmittance(a_pass, 0.015),
        })

    # Catalysts / Metal Oxides / Silica
    a_sio = _gauss_band(wn, 3430, 260, 0.20) + _gauss_band(wn, 1630, 38, 0.14) + _gauss_band(wn, 1085, 55, 0.45) + _gauss_band(wn, 805, 30, 0.21) + _gauss_band(wn, 545, 50, 0.28)
    a_carb = a_sio * 0.92 + _gauss_band(wn, 1522, 36, 0.26) + _gauss_band(wn, 1384, 32, 0.24)
    return pd.DataFrame({
        "Wavenumber_cm-1": wn,
        "Calcined Oxide / SiO₂": _to_transmittance(a_sio, 0.02),
        "CO₂-Adsorbed Carbonate Catalyst": _to_transmittance(a_carb, 0.025),
    })
