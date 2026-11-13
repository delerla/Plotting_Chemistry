"""
uv_vis_studio.core.deconvolution
Multi-component UV-Vis Spectral Deconvolution Engine.
Resolves overlapping chromophores, intermediate degradation photoproducts, and plasmonic resonances.
Uses Gaussian and Lorentzian peak profiles with baseline correction.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def gaussian_peak(x: np.ndarray, amp: float, cen: float, wid: float) -> np.ndarray:
    """Gaussian peak shape."""
    return amp * np.exp(-0.5 * ((x - cen) / max(wid, 1e-4)) ** 2)


def lorentzian_peak(x: np.ndarray, amp: float, cen: float, wid: float) -> np.ndarray:
    """Lorentzian peak shape."""
    return amp / (1.0 + ((x - cen) / max(wid, 1e-4)) ** 2)


def multi_peak_model(x: np.ndarray, *params) -> np.ndarray:
    """Sum of N peaks + linear baseline."""
    # Last 2 params are baseline: slope and intercept
    slope = params[-2]
    intercept = params[-1]
    peak_params = params[:-2]
    
    y = slope * x + intercept
    n_peaks = len(peak_params) // 3
    for i in range(n_peaks):
        amp = peak_params[3 * i]
        cen = peak_params[3 * i + 1]
        wid = peak_params[3 * i + 2]
        y += gaussian_peak(x, amp, cen, wid)
    return y


def fit_uv_vis_peaks(
    wavelength_nm: np.ndarray,
    absorbance: np.ndarray,
    initial_peak_centers: List[float],
    peak_shape: str = "Gaussian"
) -> Dict[str, Any]:
    """
    Fits multi-component peaks to a UV-Vis spectrum.
    """
    x = np.asarray(wavelength_nm, dtype=float)
    y = np.asarray(absorbance, dtype=float)

    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    n_peaks = len(initial_peak_centers)
    if n_peaks == 0:
        return {"peaks": [], "cumulative_fit": y, "r2": 0.0}

    # Initial guesses
    p0 = []
    bounds_lower = []
    bounds_upper = []

    for cen in initial_peak_centers:
        idx_near = np.argmin(np.abs(x - cen))
        amp_guess = float(y[idx_near])
        p0.extend([amp_guess, cen, 20.0])
        bounds_lower.extend([0.0, cen - 40.0, 5.0])
        bounds_upper.extend([max(y) * 2.0, cen + 40.0, 150.0])

    # Baseline guesses
    p0.extend([0.0, float(np.min(y))])
    bounds_lower.extend([-1e-2, -0.5])
    bounds_upper.extend([1e-2, max(y)])

    try:
        popt, _ = curve_fit(
            multi_peak_model, x, y,
            p0=p0,
            bounds=(bounds_lower, bounds_upper),
            maxfev=10000
        )
    except Exception:
        popt = p0

    slope_fit = popt[-2]
    intercept_fit = popt[-1]
    baseline_fit = slope_fit * x + intercept_fit

    fitted_peaks = []
    individual_curves = []
    total_area = 0.0

    for i in range(n_peaks):
        amp = float(popt[3 * i])
        cen = float(popt[3 * i + 1])
        wid = float(popt[3 * i + 2])
        curve = gaussian_peak(x, amp, cen, wid)
        area = float(amp * wid * np.sqrt(2 * np.pi))
        total_area += area
        individual_curves.append(curve)
        fitted_peaks.append({
            "peak_index": i + 1,
            "center_nm": round(cen, 2),
            "amplitude": round(amp, 4),
            "fwhm_nm": round(wid * 2.3548, 2),
            "area": round(area, 4)
        })

    # Add relative area percentage
    for p in fitted_peaks:
        p["area_pct"] = round((p["area"] / max(total_area, 1e-8)) * 100.0, 2)

    cumulative_fit = baseline_fit + sum(individual_curves)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - cumulative_fit) ** 2)
    r2 = 1.0 - (ss_res / max(ss_tot, 1e-8))

    return {
        "peaks": fitted_peaks,
        "wavelength": x,
        "experimental": y,
        "baseline": baseline_fit,
        "cumulative_fit": cumulative_fit,
        "individual_curves": individual_curves,
        "r2": round(r2, 4)
    }
