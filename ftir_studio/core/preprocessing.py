"""
preprocessing.py - FTIR Scale Detection, ATR Depth Correction, CO2 Artifact Removal & 2nd Derivative Engine.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Tuple
import numpy as np
from scipy.signal import savgol_filter


def detect_ir_scale(y: np.ndarray) -> str:
    """Heuristically distinguishes % Transmittance vs Absorbance units."""
    arr = np.asarray(y, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return "Absorbance (A)"
    med = float(np.median(arr))
    mx = float(np.max(arr))
    if mx > 12.0 or med > 15.0:
        return "Transmittance (%T)"
    return "Absorbance (A)"


def convert_ir_scale(
    y: np.ndarray,
    source_scale: str = "Auto-Detect",
    target_scale: str = "Absorbance (A)",
) -> Tuple[np.ndarray, str]:
    """
    Converts FTIR intensities cleanly between Transmittance (%T) and Absorbance (A):
        A = -log10(T / 100)   |   %T = 100 * 10^(-A)
    Returns (converted_array, resolved_source_scale).
    """
    arr = np.asarray(y, dtype=float)
    src = detect_ir_scale(arr) if "auto" in source_scale.lower() else source_scale

    src_is_t = "transmittance" in src.lower()
    tgt_is_t = "transmittance" in target_scale.lower()

    if src_is_t and not tgt_is_t:
        t_frac = np.clip(arr / 100.0, 1e-4, 1.5)
        out = -np.log10(t_frac)
        return np.maximum(out, 0.0), src
    if not src_is_t and tgt_is_t:
        a_clip = np.clip(arr, -0.2, 4.0)
        return np.clip(100.0 * (10.0 ** (-a_clip)), 0.0, 110.0), src
    return arr.copy(), src


def apply_atr_correction(
    wavenumber: np.ndarray,
    absorbance: np.ndarray,
    ref_wn: float = 1000.0,
) -> np.ndarray:
    """
    Applies ATR pathlength dispersion correction (d_p proportional to 1 / wavenumber):
        A_corr(nu) = A(nu) * (nu / ref_wn)
    Corrects overstated low-wavenumber bands relative to transmission spectra.
    """
    wn = np.asarray(wavenumber, dtype=float)
    abs_arr = np.asarray(absorbance, dtype=float)
    factor = np.maximum(wn, 100.0) / max(float(ref_wn), 100.0)
    return abs_arr * factor


def mask_co2_artifact(
    wavenumber: np.ndarray,
    signal: np.ndarray,
    low_wn: float = 2295.0,
    high_wn: float = 2390.0,
) -> np.ndarray:
    """
    Linearly bridges over atmospheric CO2 asymmetric stretch spikes (2295-2390 cm-1)
    to prevent false peak identification or baseline distortion.
    """
    wn = np.asarray(wavenumber, dtype=float)
    y = np.asarray(signal, dtype=float).copy()
    mask = (wn >= low_wn) & (wn <= high_wn)
    if np.sum(mask) < 3 or np.all(mask):
        return y

    keep = ~mask
    order = np.argsort(wn[keep])
    y[mask] = np.interp(wn[mask], wn[keep][order], y[keep][order])
    return y


def apply_savgol_smooth(
    y: np.ndarray,
    window_len: int = 9,
    polyorder: int = 2,
) -> np.ndarray:
    """Applies Savitzky-Golay smoothing safely across arbitrary array lengths."""
    arr = np.asarray(y, dtype=float)
    n = len(arr)
    if n < 7 or window_len < 3:
        return arr.copy()
    w = int(window_len)
    if w % 2 == 0:
        w += 1
    w = min(w, n if n % 2 == 1 else n - 1)
    p = min(int(polyorder), w - 1)
    if w <= p or w < 3:
        return arr.copy()
    return savgol_filter(arr, window_length=w, polyorder=p)


def compute_second_derivative(
    wavenumber: np.ndarray,
    absorbance: np.ndarray,
    window_len: int = 15,
    polyorder: int = 3,
) -> np.ndarray:
    """
    Computes inverted Savitzky-Golay second derivative (-d2A / dnu2) vs ascending/descending wavenumber.
    Local maxima of -d2A/dnu2 pinpoint overlapping vibrational shoulders objectively.
    """
    wn = np.asarray(wavenumber, dtype=float)
    y = np.asarray(absorbance, dtype=float)
    n = len(y)
    if n < 11:
        return np.zeros_like(y)

    w = int(window_len)
    if w % 2 == 0:
        w += 1
    w = max(5, min(w, n if n % 2 == 1 else n - 1))
    p = min(max(2, int(polyorder)), w - 1)

    order = np.argsort(wn)
    dx = max(float(np.nanmedian(np.abs(np.diff(wn[order])))), 1e-3)
    d2_sorted = savgol_filter(y[order], window_length=w, polyorder=p, deriv=2, delta=dx)
    out = np.empty_like(d2_sorted)
    out[order] = -d2_sorted
    return out
