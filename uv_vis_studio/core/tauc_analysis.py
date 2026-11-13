"""
uv_vis_studio.core.tauc_analysis
Tauc Plot Optical Bandgap & Urbach Energy Defect Extraction Engine.
Supports:
- Direct Allowed (n = 1/2) -> (alpha * hv)^2
- Indirect Allowed (n = 2) -> (alpha * hv)^0.5
- Direct Forbidden (n = 3/2) -> (alpha * hv)^(2/3)
- Indirect Forbidden (n = 3) -> (alpha * hv)^(1/3)
- Automated inflection point detection & tangent line extrapolation
- Urbach tail energy (Eu) defect state density quantification
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import linregress


H_C_CONST = 1239.84193  # Planck's constant * c in eV * nm

TRANSITION_MODES: Dict[str, float] = {
    "Direct Allowed (n = 1/2)": 2.0,       # (alpha * hv)^2
    "Indirect Allowed (n = 2)": 0.5,      # (alpha * hv)^0.5
    "Direct Forbidden (n = 3/2)": 2.0 / 3.0,
    "Indirect Forbidden (n = 3)": 1.0 / 3.0
}


def compute_tauc_series(
    wavelength_nm: np.ndarray,
    absorbance: np.ndarray,
    transition_mode: str = "Direct Allowed (n = 1/2)",
    film_thickness_nm: float = 300.0
) -> pd.DataFrame:
    """
    Computes photon energy, absorption coefficient (alpha), and (alpha * hv)^(1/n).
    """
    wl = np.asarray(wavelength_nm, dtype=float)
    abs_vals = np.asarray(absorbance, dtype=float)

    # Sort in ascending energy (descending wavelength)
    sort_idx = np.argsort(wl)[::-1]
    wl = wl[sort_idx]
    abs_vals = abs_vals[sort_idx]

    # Mask valid values
    mask = (wl > 0) & (abs_vals >= 0) & np.isfinite(wl) & np.isfinite(abs_vals)
    wl = wl[mask]
    abs_vals = abs_vals[mask]

    energy_ev = H_C_CONST / wl
    # alpha in cm^-1: alpha = 2.303 * A / (d in cm)
    d_cm = (film_thickness_nm * 1e-7) if film_thickness_nm > 0 else 1.0
    alpha = (2.302585 * abs_vals) / d_cm
    
    exponent = TRANSITION_MODES.get(transition_mode, 2.0)
    tauc_y = (alpha * energy_ev) ** exponent

    return pd.DataFrame({
        "Wavelength_nm": np.round(wl, 2),
        "Photon_Energy_eV": np.round(energy_ev, 4),
        "Absorbance_OD": np.round(abs_vals, 4),
        "Alpha_cm_inv": np.round(alpha, 1),
        "Tauc_Y": np.round(tauc_y, 4)
    })


def fit_tauc_bandgap(
    energy_ev: np.ndarray,
    tauc_y: np.ndarray,
    alpha_or_abs: Optional[np.ndarray] = None,
    fit_energy_range: Optional[Tuple[float, float]] = None
) -> Dict[str, Any]:
    """
    Fits the linear absorption edge on a Tauc plot and extrapolates to Y=0 to determine Eg.
    If fit_energy_range is None, automatically finds the linear region starting from the
    absorption edge inflection point (max dA/dE).
    """
    e = np.asarray(energy_ev, dtype=float)
    y = np.asarray(tauc_y, dtype=float)

    valid = np.isfinite(e) & np.isfinite(y) & (y >= 0)
    e = e[valid]
    y = y[valid]

    if len(e) < 5:
        return {"bandgap_ev": np.nan, "r2": 0.0, "slope": 0.0, "intercept": 0.0}

    # Sort by energy ascending
    idx_sort = np.argsort(e)
    e = e[idx_sort]
    y = y[idx_sort]

    if fit_energy_range is not None:
        e_min, e_max = fit_energy_range
        mask = (e >= e_min) & (e <= e_max)
        if np.sum(mask) < 3:
            mask = np.ones_like(e, dtype=bool)
    else:
        # Automated window: locate fundamental absorption edge inflection
        if alpha_or_abs is not None:
            a_arr = np.asarray(alpha_or_abs, dtype=float)[valid][idx_sort]
            da = np.gradient(a_arr, e)
            edge_idx = int(np.argmax(da))
        else:
            # Fallback to derivative of tauc_y
            dy = np.gradient(y, e)
            # Find first major inflection point above baseline
            edge_idx = int(np.argmax(dy[:int(len(dy) * 0.75)])) if len(dy) > 10 else int(np.argmax(dy))

        window = max(5, int(len(e) * 0.05))
        idx_start = max(0, edge_idx)
        idx_end = min(len(e), edge_idx + window + 1)
        mask = np.zeros_like(e, dtype=bool)
        mask[idx_start:idx_end] = True

    e_fit = e[mask]
    y_fit = y[mask]

    res = linregress(e_fit, y_fit)
    slope = float(res.slope)
    intercept = float(res.intercept)
    r2 = float(res.rvalue ** 2) if not np.isnan(res.rvalue) else 0.0

    if slope > 0:
        bandgap_ev = float(-intercept / slope)
    else:
        bandgap_ev = np.nan

    # Generate extrapolation tangent line from Eg down to max fit point
    e_tangent_start = max(0.5, bandgap_ev) if not np.isnan(bandgap_ev) else e_fit[0]
    e_tangent_end = e_fit[-1] + (e_fit[-1] - e_fit[0]) * 0.5
    e_tangent = np.linspace(e_tangent_start, e_tangent_end, 50)
    y_tangent = slope * e_tangent + intercept
    y_tangent = np.clip(y_tangent, 0, None)

    return {
        "bandgap_ev": round(bandgap_ev, 3) if not np.isnan(bandgap_ev) else np.nan,
        "lambda_onset_nm": round(H_C_CONST / bandgap_ev, 1) if (bandgap_ev and bandgap_ev > 0) else np.nan,
        "slope": slope,
        "intercept": intercept,
        "r2": round(r2, 4),
        "fit_e_min": float(e_fit[0]),
        "fit_e_max": float(e_fit[-1]),
        "tangent_energy": e_tangent,
        "tangent_y": y_tangent
    }


def fit_urbach_energy(
    energy_ev: np.ndarray,
    alpha_cm_inv: np.ndarray,
    bandgap_ev: float,
    tail_window_ev: float = 0.20
) -> Dict[str, Any]:
    """
    Fits the Urbach defect tail below the optical bandgap: ln(alpha) = ln(alpha0) + (hv / Eu).
    Eu is returned in meV.
    """
    e = np.asarray(energy_ev, dtype=float)
    a = np.asarray(alpha_cm_inv, dtype=float)

    if np.isnan(bandgap_ev) or bandgap_ev <= 0:
        return {"urbach_energy_mev": np.nan, "r2": 0.0}

    # Region below Eg: [Eg - tail_window, Eg - 0.02]
    e_tail_min = bandgap_ev - tail_window_ev
    e_tail_max = bandgap_ev - 0.015

    mask = (e >= e_tail_min) & (e <= e_tail_max) & (a > 0)
    if np.sum(mask) < 3:
        return {"urbach_energy_mev": np.nan, "r2": 0.0}

    e_fit = e[mask]
    ln_alpha = np.log(a[mask])

    res = linregress(e_fit, ln_alpha)
    slope = float(res.slope)
    r2 = float(res.rvalue ** 2) if not np.isnan(res.rvalue) else 0.0

    if abs(slope) > 1e-6:
        eu_ev = 1.0 / abs(slope)
        eu_mev = eu_ev * 1000.0  # in meV
    else:
        eu_mev = np.nan

    return {
        "urbach_energy_mev": round(eu_mev, 2) if not np.isnan(eu_mev) else np.nan,
        "slope": slope,
        "intercept": float(res.intercept),
        "r2": round(r2, 4),
        "fit_energy": e_fit,
        "fit_ln_alpha": res.slope * e_fit + res.intercept
    }
