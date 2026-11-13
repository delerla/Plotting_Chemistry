"""
uv_vis_studio.core.kinetics
Advanced Chemical Reaction & Photodegradation Kinetics Engine.
Supports Zero-Order, Pseudo-First-Order (Lagergren/Langmuir-Hinshelwood),
Pseudo-Second-Order (Ho-McKay), and Intraparticle Diffusion (Weber-Morris).
Includes AIC/BIC statistical model ranking and half-life (t1/2) calculations.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import linregress


def calculate_aic_bic(n: int, k_params: int, rss: float) -> Tuple[float, float]:
    """Calculates Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC)."""
    if n <= k_params or rss <= 0:
        return np.nan, np.nan
    aic = n * np.log(rss / n) + 2 * k_params
    bic = n * np.log(rss / n) + k_params * np.log(n)
    return aic, bic


def fit_all_kinetic_models(
    time_points: np.ndarray,
    absorbance_or_conc: np.ndarray,
    is_concentration: bool = False,
    c0_initial: float = 10.0
) -> Dict[str, Any]:
    """
    Fits multi-order reaction models to kinetic time-series data.
    
    Parameters:
    -----------
    time_points: Array of reaction/irradiation times (min or s).
    absorbance_or_conc: Measured absorbance values at lambda_max or calibrated concentrations.
    is_concentration: If True, array is already concentration in mg/L or uM.
    c0_initial: Assumed initial concentration for conversion if only absorbance is provided.
    
    Returns:
    --------
    Structured dictionary containing parameters for all kinetic models,
    regression lines, R2, AIC/BIC rankings, and best model recommendation.
    """
    t = np.asarray(time_points, dtype=float)
    y = np.asarray(absorbance_or_conc, dtype=float)
    
    # Sort by time
    idx_sort = np.argsort(t)
    t = t[idx_sort]
    y = y[idx_sort]
    
    y0 = y[0] if y[0] > 0 else 1.0
    
    if is_concentration:
        c_t = np.clip(y, 1e-7, None)
        c0 = y0
        fraction = np.clip(c_t / c0, 1e-6, 1.0)
    else:
        fraction = np.clip(y / y0, 1e-6, 1.0)
        c0 = c0_initial
        c_t = c0 * fraction

    n_pts = len(t)
    degradation_efficiency = (1.0 - fraction) * 100.0

    # -------------------------------------------------------------
    # 1. Zero-Order: (C0 - Ct) = k0 * t
    # -------------------------------------------------------------
    diff_zero = c0 - c_t
    res_zero = linregress(t, diff_zero)
    pred_zero = res_zero.slope * t + res_zero.intercept
    rss_zero = np.sum((diff_zero - pred_zero) ** 2)
    r2_zero = float(res_zero.rvalue ** 2) if not np.isnan(res_zero.rvalue) else 0.0
    aic_zero, bic_zero = calculate_aic_bic(n_pts, 2, rss_zero)
    k_zero = float(res_zero.slope)

    # -------------------------------------------------------------
    # 2. Pseudo-First-Order (PFO): ln(C0 / Ct) = k_pfo * t
    # -------------------------------------------------------------
    ln_c0_ct = np.log(1.0 / fraction)
    res_pfo = linregress(t, ln_c0_ct)
    pred_pfo = res_pfo.slope * t + res_pfo.intercept
    rss_pfo = np.sum((ln_c0_ct - pred_pfo) ** 2)
    r2_pfo = float(res_pfo.rvalue ** 2) if not np.isnan(res_pfo.rvalue) else 0.0
    aic_pfo, bic_pfo = calculate_aic_bic(n_pts, 2, rss_pfo)
    k_pfo = float(res_pfo.slope)
    t_half_pfo = (np.log(2) / k_pfo) if k_pfo > 1e-8 else np.nan

    # -------------------------------------------------------------
    # 3. Pseudo-Second-Order (PSO): (1 / Ct) - (1 / C0) = k_pso * t
    # -------------------------------------------------------------
    inv_ct_c0 = (1.0 / c_t) - (1.0 / c0)
    res_pso = linregress(t, inv_ct_c0)
    pred_pso = res_pso.slope * t + res_pso.intercept
    rss_pso = np.sum((inv_ct_c0 - pred_pso) ** 2)
    r2_pso = float(res_pso.rvalue ** 2) if not np.isnan(res_pso.rvalue) else 0.0
    aic_pso, bic_pso = calculate_aic_bic(n_pts, 2, rss_pso)
    k_pso = float(res_pso.slope)
    t_half_pso = (1.0 / (k_pso * c0)) if (k_pso > 1e-8 and c0 > 0) else np.nan

    # -------------------------------------------------------------
    # 4. Intraparticle Diffusion (Weber-Morris): qt = ki * t^0.5 + C
    # -------------------------------------------------------------
    t_sqrt = np.sqrt(t)
    res_weber = linregress(t_sqrt, diff_zero)
    pred_weber = res_weber.slope * t_sqrt + res_weber.intercept
    r2_weber = float(res_weber.rvalue ** 2) if not np.isnan(res_weber.rvalue) else 0.0

    # Best model selection by R^2
    r2_scores = {
        "Pseudo-First-Order (Langmuir-Hinshelwood)": r2_pfo,
        "Pseudo-Second-Order": r2_pso,
        "Zero-Order": r2_zero
    }
    best_model_name = max(r2_scores, key=r2_scores.get)

    # Detailed export DataFrame for LabPlot & OriginLab
    t_dense = np.linspace(0, float(np.max(t)), 100)
    kinetics_table = pd.DataFrame({
        "Time_min": t,
        "Normalized_Ct_C0": np.round(fraction, 5),
        "Concentration_mg_L": np.round(c_t, 4),
        "Degradation_Efficiency_pct": np.round(degradation_efficiency, 2),
        "ln_C0_Ct": np.round(ln_c0_ct, 5),
        "Fit_PFO_ln_C0_Ct": np.round(pred_pfo, 5),
        "Inv_Ct_minus_Inv_C0": np.round(inv_ct_c0, 5),
        "Fit_PSO_Inv": np.round(pred_pso, 5),
        "Zero_Order_C0_Ct": np.round(diff_zero, 5),
        "Fit_Zero_Order": np.round(pred_zero, 5)
    })

    return {
        "time_points": t,
        "absorbance": y,
        "c_t": c_t,
        "fraction": fraction,
        "degradation_efficiency": degradation_efficiency,
        "best_model": best_model_name,
        "zero_order": {
            "k": k_zero,
            "intercept": float(res_zero.intercept),
            "r2": r2_zero,
            "rss": rss_zero,
            "aic": aic_zero,
            "bic": bic_zero
        },
        "pfo": {
            "k": k_pfo,
            "intercept": float(res_pfo.intercept),
            "r2": r2_pfo,
            "rss": rss_pfo,
            "aic": aic_pfo,
            "bic": bic_pfo,
            "t_half": t_half_pfo
        },
        "pso": {
            "k": k_pso,
            "intercept": float(res_pso.intercept),
            "r2": r2_pso,
            "rss": rss_pso,
            "aic": aic_pso,
            "bic": bic_pso,
            "t_half": t_half_pso
        },
        "weber_morris": {
            "k_int": float(res_weber.slope),
            "intercept": float(res_weber.intercept),
            "r2": r2_weber
        },
        "table": kinetics_table,
        "t_dense": t_dense,
        "pfo_dense_fit": res_pfo.slope * t_dense + res_pfo.intercept,
        "pso_dense_fit": res_pso.slope * t_dense + res_pso.intercept
    }
