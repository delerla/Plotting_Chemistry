"""
deconvolution.py - Multi-Band FTIR Vibrational Deconvolution Engine via lmfit.
Supports Gaussian, Lorentzian, Pseudo-Voigt, and Voigt profiles + 2nd-derivative peak seeding.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional, Tuple
import lmfit
from lmfit.models import ConstantModel, GaussianModel, LinearModel, LorentzianModel, PseudoVoigtModel, VoigtModel
import numpy as np
from scipy.signal import find_peaks

try:
    from core.preprocessing import compute_second_derivative
except ImportError:
    from ftir_studio.core.preprocessing import compute_second_derivative


def _trapz(y: np.ndarray, x: np.ndarray) -> float:
    fn = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    return float(abs(fn(y, x)))


def _voigt_fwhm_olivero(sigma: float, gamma: float) -> float:
    fg = 2.354820045 * max(sigma, 1e-6)
    fl = 2.0 * max(gamma, 0.0)
    return float(0.5346 * fl + np.sqrt(0.2166 * (fl ** 2) + fg ** 2))


def auto_detect_ir_bands(
    wavenumber: np.ndarray,
    y_net: np.ndarray,
    min_prominence_pct: float = 5.0,
    min_distance_cm1: float = 22.0,
    max_bands: int = 12,
    use_second_deriv: bool = False,
    default_fwhm: float = 26.0,
) -> List[Dict[str, Any]]:
    """
    Automatically seeds IR band centers using absorbance prominence or inverted 2nd-derivative (-d2A/dnu2).
    Sorted descending from highest wavenumber to lowest wavenumber.
    """
    order = np.argsort(wavenumber)
    x = np.asarray(wavenumber[order], dtype=float)
    y = np.asarray(y_net[order], dtype=float)
    if len(x) < 12 or float(np.nanmax(y)) <= 1e-9:
        return []

    dx = max(float(np.nanmedian(np.abs(np.diff(x)))), 1e-3)
    dist_pts = max(int(round(min_distance_cm1 / dx)), 3)

    if use_second_deriv:
        sig = np.maximum(compute_second_derivative(x, y, window_len=15, polyorder=3), 0.0)
        prom = float(np.nanmax(sig)) * (float(min_prominence_pct) / 100.0)
        indices, props = find_peaks(sig, prominence=max(prom, 1e-12), distance=dist_pts)
        # Keep only bands where actual net absorbance is nontrivial (>= 3% of max)
        y_thr = float(np.nanmax(y)) * 0.03
        indices = np.array([idx for idx in indices if y[idx] >= y_thr], dtype=int)
    else:
        prom = float(np.nanmax(y)) * (float(min_prominence_pct) / 100.0)
        indices, props = find_peaks(y, prominence=max(prom, 1e-12), distance=dist_pts)

    if len(indices) == 0:
        idx_max = int(np.nanargmax(y))
        return [{
            "label": f"Band ({int(round(x[idx_max]))} cm⁻¹)",
            "mode": "IR Peak",
            "center": round(float(x[idx_max]), 1),
            "fwhm": round(float(default_fwhm), 1),
            "color": "#1f77b4",
            "meaning": "Auto-detected dominant IR band",
        }]

    score = y[indices]
    top_order = np.argsort(score)[::-1][: int(max_bands)]
    chosen_idx = indices[top_order]
    # Sort descending in wavenumber (standard IR display order)
    chosen_idx = chosen_idx[np.argsort(x[chosen_idx])[::-1]]

    palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"
    ]
    bands_out = []
    for k, idx in enumerate(chosen_idx):
        wn_val = float(x[idx])
        bands_out.append({
            "label": f"Band {int(round(wn_val))} cm⁻¹",
            "mode": "Vibrational Band",
            "center": round(wn_val, 1),
            "fwhm": round(float(default_fwhm), 1),
            "color": palette[k % len(palette)],
            "meaning": "Auto-detected vibrational peak / shoulder",
        })
    return bands_out


def fit_ir_bands(
    wavenumber: np.ndarray,
    y_net: np.ndarray,
    band_configs: List[Dict[str, Any]],
    line_shape_mode: str = "Gaussian",
    center_tol_cm1: float = 20.0,
    fwhm_bounds: Tuple[float, float] = (5.0, 220.0),
    lock_fwhm_equal: bool = False,
    residual_baseline: str = "None (Fixed 0)",
    max_nfev: int = 800,
) -> Tuple[Any, Dict[str, np.ndarray], Dict[str, Dict[str, Any]], float, float]:
    """
    Fits multiple vibrational absorption bands inside an FTIR ROI using lmfit.
    Returns (lmfit_result, comp_curves_dict, band_summary_dict, r2, rmse).
    """
    order = np.argsort(wavenumber)
    x = np.asarray(wavenumber[order], dtype=float)
    y = np.asarray(y_net[order], dtype=float)

    if len(x) < 10 or not band_configs:
        raise ValueError("Insufficient points or empty band configuration for FTIR deconvolution.")

    y_scale = max(float(np.nanmax(y)), 1e-4)
    f_lo = max(float(fwhm_bounds[0]), 2.0)
    f_hi = max(float(fwhm_bounds[1]), f_lo + 5.0)

    composite_model = None
    params = lmfit.Parameters()
    comp_prefixes: List[Tuple[str, Dict[str, Any], str]] = []
    shared_sigma_expr: Optional[str] = None

    rb_low = residual_baseline.lower()
    if "linear" in rb_low:
        bg_mod = LinearModel(prefix="bg_")
        composite_model = bg_mod
        params.update(bg_mod.make_params(slope=0.0, intercept=float(np.nanmin(y))))
    elif "const" in rb_low:
        bg_mod = ConstantModel(prefix="bg_")
        composite_model = bg_mod
        params.update(bg_mod.make_params(c=float(np.nanmin(y))))

    for i, b in enumerate(band_configs):
        prefix = f"b{i}_"
        b_shape = str(b.get("shape", "Auto") or "Auto")
        active_shape = line_shape_mode if b_shape == "Auto" else b_shape
        s_low = active_shape.lower()

        if "pseudo" in s_low:
            mod = PseudoVoigtModel(prefix=prefix)
            model_tag = "Pseudo-Voigt"
        elif "voigt" in s_low:
            mod = VoigtModel(prefix=prefix)
            model_tag = "Voigt"
        elif "lorentz" in s_low:
            mod = LorentzianModel(prefix=prefix)
            model_tag = "Lorentzian"
        else:
            mod = GaussianModel(prefix=prefix)
            model_tag = "Gaussian"

        composite_model = mod if composite_model is None else (composite_model + mod)

        c_init = float(np.clip(float(b.get("center", np.median(x))), float(x.min()), float(x.max())))
        fwhm_init = float(np.clip(float(b.get("fwhm", 25.0)), f_lo, f_hi))
        fix_c = bool(b.get("fix_center", False))

        near = np.abs(x - c_init) <= max(fwhm_init, 15.0)
        local_h = float(np.nanmax(y[near])) if np.any(near) else y_scale * 0.25
        area_init = max(local_h * fwhm_init * 1.1, y_scale * 0.1)

        p = mod.make_params()
        c_min = max(float(x.min()), c_init - center_tol_cm1)
        c_max = min(float(x.max()), c_init + center_tol_cm1)
        p[f"{prefix}center"].set(value=c_init, min=c_min, max=c_max, vary=not fix_c)
        p[f"{prefix}amplitude"].set(value=area_init, min=0.0, max=y_scale * (x.max() - x.min()) * 2.0)

        if model_tag == "Pseudo-Voigt":
            p[f"{prefix}sigma"].set(value=fwhm_init / 2.0, min=f_lo / 2.0, max=f_hi / 2.0)
            p[f"{prefix}fraction"].set(value=0.35, min=0.0, max=1.0)
        elif model_tag == "Voigt":
            p[f"{prefix}sigma"].set(value=fwhm_init / 2.5, min=f_lo / 4.0, max=f_hi / 2.0)
            p[f"{prefix}gamma"].set(value=fwhm_init * 0.15, min=0.0, max=f_hi / 2.0, vary=True)
        elif model_tag == "Lorentzian":
            p[f"{prefix}sigma"].set(value=fwhm_init / 2.0, min=f_lo / 2.0, max=f_hi / 2.0)
        else:
            p[f"{prefix}sigma"].set(value=fwhm_init / 2.35482, min=f_lo / 2.35482, max=f_hi / 2.35482)

        if lock_fwhm_equal:
            if shared_sigma_expr is None:
                shared_sigma_expr = f"{prefix}sigma"
            elif model_tag != "Voigt":
                p[f"{prefix}sigma"].set(expr=shared_sigma_expr)

        params.update(p)
        comp_prefixes.append((prefix, b, model_tag))

    fit_res = composite_model.fit(y, params, x=x, method="least_squares", max_nfev=int(max_nfev))
    y_best = np.asarray(fit_res.best_fit, dtype=float)

    ss_res = float(np.sum((y - y_best) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 1.0
    rmse = float(np.sqrt(ss_res / max(len(y), 1)))

    comps_eval = fit_res.eval_components(x=x)
    comp_curves: Dict[str, np.ndarray] = {}
    if "bg_" in comps_eval:
        comp_curves["_local_bg"] = np.asarray(comps_eval["bg_"], dtype=float)

    total_area = 0.0
    band_summary: Dict[str, Dict[str, Any]] = {}

    for prefix, b, model_tag in comp_prefixes:
        label = str(b.get("label", f"Band_{prefix}"))
        if label in band_summary:
            label = f"{label} ({prefix[:-1]})"

        y_comp = np.asarray(comps_eval.get(prefix, np.zeros_like(x)), dtype=float)
        comp_curves[label] = y_comp

        c_fit = float(fit_res.params[f"{prefix}center"].value)
        s_fit = float(fit_res.params[f"{prefix}sigma"].value)
        if model_tag == "Voigt":
            g_fit = float(fit_res.params[f"{prefix}gamma"].value)
            fwhm_fit = _voigt_fwhm_olivero(s_fit, g_fit)
        elif model_tag in ("Lorentzian", "Pseudo-Voigt"):
            fwhm_fit = 2.0 * s_fit
        else:
            fwhm_fit = 2.354820045 * s_fit

        area = max(_trapz(y_comp, x), 0.0)
        height = float(np.nanmax(y_comp)) if len(y_comp) else 0.0
        total_area += area

        band_summary[label] = {
            "Mode": str(b.get("mode", "")),
            "Line_Shape": model_tag,
            "Wavenumber_cm1": round(c_fit, 2),
            "FWHM_cm1": round(fwhm_fit, 2),
            "Peak_Absorbance": round(height, 4),
            "Integrated_Area": round(area, 4),
            "Area_Percent": 0.0,
            "Color": b.get("color", "#1f77b4"),
            "Meaning": b.get("meaning", "Vibrational absorption band"),
        }

    if total_area > 1e-9:
        for lbl in band_summary:
            band_summary[lbl]["Area_Percent"] = round(100.0 * band_summary[lbl]["Integrated_Area"] / total_area, 2)

    return fit_res, comp_curves, band_summary, float(max(min(r2, 1.0), 0.0)), float(rmse)
