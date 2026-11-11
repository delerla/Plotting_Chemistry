"""
williamson_hall.py - Williamson-Hall Microstrain & Crystallite Size Separation Engine.
Implements Uniform Deformation Model (UDM): beta_corr * cos(theta) = (K * lambda / D) + 4 * epsilon * sin(theta).
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List
import numpy as np


def compute_williamson_hall(
    peak_summary: Dict[str, Dict[str, Any]],
    wavelength_nm: float = 0.1540598,
    k_factor: float = 0.9,
) -> Dict[str, Any]:
    """
    Performs Williamson-Hall linear regression over fitted Bragg reflections:
        Y = beta_corr_rad * cos(theta)
        X = 4 * sin(theta)
        Y = epsilon * X + (K * lambda / D_WH)
    Requires >= 3 distinct Bragg peaks for statistically meaningful regression.
    """
    labels: List[str] = []
    two_thetas: List[float] = []
    x_wh: List[float] = []
    y_wh: List[float] = []

    for label, p in peak_summary.items():
        tt = float(p.get("TwoTheta_deg", 0.0))
        fwhm_corr = float(p.get("FWHM_corr_deg", p.get("FWHM_deg", 0.0)))
        if tt <= 0.1 or fwhm_corr <= 1e-4:
            continue
        theta_rad = np.radians(tt / 2.0)
        beta_rad = np.radians(fwhm_corr)
        labels.append(label)
        two_thetas.append(tt)
        x_wh.append(4.0 * float(np.sin(theta_rad)))
        y_wh.append(beta_rad * float(np.cos(theta_rad)))

    n_pts = len(x_wh)
    if n_pts < 3:
        return {
            "valid": False,
            "reason": f"Requires ≥3 distinct Bragg reflections (currently {n_pts}).",
            "n_peaks": n_pts,
            "labels": labels,
            "x_4sin": np.array(x_wh, dtype=float),
            "y_bcos": np.array(y_wh, dtype=float),
        }

    x_arr = np.asarray(x_wh, dtype=float)
    y_arr = np.asarray(y_wh, dtype=float)

    if np.ptp(x_arr) < 1e-6:
        return {
            "valid": False,
            "reason": "Peaks span insufficient 2θ angular separation for Williamson-Hall regression.",
            "n_peaks": n_pts,
            "labels": labels,
            "x_4sin": x_arr,
            "y_bcos": y_arr,
        }

    slope, intercept = np.polyfit(x_arr, y_arr, 1)
    y_pred = slope * x_arr + intercept
    ss_res = float(np.sum((y_arr - y_pred) ** 2))
    ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
    r2_wh = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-18 else 0.0

    microstrain = float(slope)
    d_wh_nm = float((k_factor * wavelength_nm) / intercept) if intercept > 1e-8 else float("inf")

    return {
        "valid": True,
        "n_peaks": n_pts,
        "labels": labels,
        "two_thetas": np.array(two_thetas, dtype=float),
        "x_4sin": x_arr,
        "y_bcos": y_arr,
        "y_fit": y_pred,
        "slope_epsilon": microstrain,
        "microstrain_percent": microstrain * 100.0,
        "intercept": float(intercept),
        "D_wh_nm": d_wh_nm,
        "r2_wh": float(max(min(r2_wh, 1.0), 0.0)),
    }
