"""
peak_fitting.py - Multi-Peak XRD Profile Deconvolution, Bragg Law & Scherrer Crystallite Sizing Engine.
Supports Pseudo-Voigt (GL fraction), Voigt, Gaussian, and Lorentzian Bragg reflections via lmfit.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional, Tuple
import lmfit
from lmfit.models import GaussianModel, LinearModel, ConstantModel, LorentzianModel, PseudoVoigtModel, VoigtModel
import numpy as np
from scipy.signal import find_peaks


def _trapz(y: np.ndarray, x: np.ndarray) -> float:
    """NumPy 1.x / 2.x compatible trapezoidal integration."""
    fn = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    return float(fn(y, x))


def bragg_d_spacing(two_theta_deg: float, wavelength_A: float = 1.540598) -> float:
    """Calculates interplanar d-spacing in Angstroms via Bragg's Law: n*lambda = 2*d*sin(theta)."""
    if two_theta_deg <= 0.05 or two_theta_deg >= 179.9:
        return 0.0
    sin_th = np.sin(np.radians(two_theta_deg / 2.0))
    if sin_th <= 1e-8:
        return 0.0
    return float(wavelength_A / (2.0 * sin_th))


def correct_instrumental_broadening(
    fwhm_obs_deg: float,
    beta_inst_deg: float = 0.0,
    mode: str = "Gaussian Quadrature",
) -> float:
    """
    Subtracts instrumental broadening beta_inst from observed peak FWHM:
      - Gaussian Quadrature: sqrt(max(beta_obs^2 - beta_inst^2, 0))
      - Lorentzian Linear: max(beta_obs - beta_inst, 0)
    Returns strictly positive physical broadening (floor 0.015 deg for stability).
    """
    obs = max(float(fwhm_obs_deg), 0.015)
    inst = max(float(beta_inst_deg), 0.0)
    if inst <= 0.0:
        return obs

    if "lorentz" in mode.lower() or "linear" in mode.lower():
        corr = obs - inst
    else:
        corr = np.sqrt(max(obs ** 2 - inst ** 2, 0.0))
    return float(max(corr, 0.015))


def scherrer_crystallite_size(
    fwhm_obs_deg: float,
    two_theta_deg: float,
    wavelength_nm: float = 0.1540598,
    k_factor: float = 0.9,
    beta_inst_deg: float = 0.0,
    broadening_mode: str = "Gaussian Quadrature",
) -> Tuple[float, float]:
    """
    Computes physical broadening beta_corr (deg) and Scherrer crystallite size D (nm):
        D = (K * lambda) / (beta_corr_rad * cos(theta))
    Returns (D_nm, beta_corr_deg).
    """
    beta_corr_deg = correct_instrumental_broadening(fwhm_obs_deg, beta_inst_deg, broadening_mode)
    theta_rad = np.radians(two_theta_deg / 2.0)
    beta_rad = np.radians(beta_corr_deg)
    denom = beta_rad * np.cos(theta_rad)
    if denom <= 1e-9:
        return 0.0, beta_corr_deg
    d_nm = (float(k_factor) * float(wavelength_nm)) / float(denom)
    return float(d_nm), float(beta_corr_deg)


def _voigt_fwhm_olivero(sigma: float, gamma: float) -> float:
    """Computes exact Voigt FWHM via Olivero-Longbothum empirical formula."""
    fg = 2.354820045 * max(sigma, 1e-6)
    fl = 2.0 * max(gamma, 0.0)
    return float(0.5346 * fl + np.sqrt(0.2166 * (fl ** 2) + fg ** 2))


def auto_detect_xrd_peaks(
    two_theta: np.ndarray,
    y_net: np.ndarray,
    min_prominence_pct: float = 4.5,
    min_distance_deg: float = 0.45,
    max_peaks: int = 12,
    default_fwhm: float = 0.30,
) -> List[Dict[str, Any]]:
    """
    Automatically identifies prominent Bragg reflections in a background-stripped pattern.
    Returns a sorted list of peak dictionaries ready for editing and multi-peak lmfit refinement.
    """
    x = np.asarray(two_theta, dtype=float)
    y = np.asarray(y_net, dtype=float)
    if len(x) < 10 or float(np.nanmax(y)) <= 0:
        return []

    dx = float(np.nanmedian(np.abs(np.diff(np.sort(x)))))
    dx = max(dx, 1e-4)
    dist_pts = max(int(round(min_distance_deg / dx)), 3)
    prom = float(np.nanmax(y)) * (float(min_prominence_pct) / 100.0)

    indices, props = find_peaks(y, prominence=max(prom, 1e-6), distance=dist_pts)
    if len(indices) == 0:
        # Fallback to global maximum peak
        idx_max = int(np.nanargmax(y))
        return [{
            "label": f"Peak ({x[idx_max]:.2f}°)",
            "hkl": "",
            "center": round(float(x[idx_max]), 3),
            "fwhm": round(float(default_fwhm), 3),
            "amp": float(y[idx_max]),
            "meaning": "Auto-detected principal reflection",
        }]

    # Keep top N by prominence, then sort ascending in 2-theta
    proms = props.get("prominences", y[indices])
    top_order = np.argsort(proms)[::-1][: int(max_peaks)]
    chosen_idx = np.sort(indices[top_order])

    palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"
    ]
    peaks_out = []
    for k, idx in enumerate(chosen_idx):
        tt = float(x[idx])
        peaks_out.append({
            "label": f"Peak {k + 1} ({tt:.2f}°)",
            "hkl": "",
            "center": round(tt, 3),
            "fwhm": round(float(default_fwhm), 3),
            "amp": float(max(y[idx], 1.0)),
            "color": palette[k % len(palette)],
            "meaning": "Auto-detected Bragg reflection",
        })
    return peaks_out


def fit_xrd_peaks(
    two_theta: np.ndarray,
    y_net: np.ndarray,
    peak_configs: List[Dict[str, Any]],
    wavelength_A: float = 1.540598,
    wavelength_nm: float = 0.1540598,
    k_factor: float = 0.9,
    beta_inst_deg: float = 0.0,
    broadening_mode: str = "Gaussian Quadrature",
    line_shape_mode: str = "Pseudo-Voigt",
    center_tol_deg: float = 0.65,
    fwhm_bounds: Tuple[float, float] = (0.04, 6.0),
    lock_fwhm_equal: bool = False,
    residual_baseline: str = "None (Fixed 0)",
    max_nfev: int = 800,
) -> Tuple[Any, Dict[str, np.ndarray], Dict[str, Dict[str, Any]], float, float]:
    """
    Performs multi-peak XRD non-linear least-squares profile fitting using lmfit.
    Returns (lmfit_result, comp_curves_dict, peak_summary_dict, r2, r_wp_pct).
    """
    x = np.asarray(two_theta, dtype=float)
    y = np.asarray(y_net, dtype=float)

    if len(x) < 10 or not peak_configs:
        raise ValueError("Insufficient data points or empty peak configuration for XRD fitting.")

    order = np.argsort(x)
    x = x[order]
    y = y[order]

    y_scale = max(float(np.nanmax(y)), 1.0)
    fwhm_lo, fwhm_hi = max(float(fwhm_bounds[0]), 0.02), max(float(fwhm_bounds[1]), float(fwhm_bounds[0]) + 0.1)

    composite_model = None
    params = lmfit.Parameters()
    comp_prefixes: List[Tuple[str, Dict[str, Any], str]] = []
    shared_sigma_expr: Optional[str] = None

    # Optional residual local baseline
    rb_low = residual_baseline.lower()
    if "linear" in rb_low:
        bg_mod = LinearModel(prefix="bg_")
        composite_model = bg_mod
        params.update(bg_mod.make_params(slope=0.0, intercept=float(np.nanmin(y))))
    elif "const" in rb_low:
        bg_mod = ConstantModel(prefix="bg_")
        composite_model = bg_mod
        params.update(bg_mod.make_params(c=float(np.nanmin(y))))

    for i, pk in enumerate(peak_configs):
        prefix = f"p{i}_"
        pk_shape = str(pk.get("shape", "Auto") or "Auto")
        active_shape = line_shape_mode if pk_shape == "Auto" else pk_shape
        shape_low = active_shape.lower()

        if "pseudo" in shape_low or "pv" in shape_low:
            mod = PseudoVoigtModel(prefix=prefix)
            model_tag = "Pseudo-Voigt"
        elif "voigt" in shape_low:
            mod = VoigtModel(prefix=prefix)
            model_tag = "Voigt"
        elif "lorentz" in shape_low:
            mod = LorentzianModel(prefix=prefix)
            model_tag = "Lorentzian"
        else:
            mod = GaussianModel(prefix=prefix)
            model_tag = "Gaussian"

        composite_model = mod if composite_model is None else (composite_model + mod)

        c_init = float(pk.get("center", np.median(x)))
        c_init = float(np.clip(c_init, float(x.min()), float(x.max())))
        fwhm_init = float(np.clip(float(pk.get("fwhm", 0.30)), fwhm_lo, fwhm_hi))
        fix_c = bool(pk.get("fix_center", False))

        # Rough local height estimate
        near_mask = np.abs(x - c_init) <= max(fwhm_init * 1.5, 0.5)
        local_peak = float(np.nanmax(y[near_mask])) if np.any(near_mask) else y_scale * 0.2
        area_init = max(local_peak * fwhm_init * 1.15, y_scale * 0.01)

        p = mod.make_params()
        c_min = max(float(x.min()), c_init - center_tol_deg)
        c_max = min(float(x.max()), c_init + center_tol_deg)
        p[f"{prefix}center"].set(value=c_init, min=c_min, max=c_max, vary=not fix_c)
        p[f"{prefix}amplitude"].set(value=area_init, min=0.0, max=y_scale * (x.max() - x.min()) * 2.5)

        if model_tag == "Pseudo-Voigt":
            # lmfit PseudoVoigtModel uses sigma as HWHM so FWHM = 2 * sigma
            s_init = fwhm_init / 2.0
            s_lo, s_hi = fwhm_lo / 2.0, fwhm_hi / 2.0
            p[f"{prefix}sigma"].set(value=s_init, min=s_lo, max=s_hi)
            p[f"{prefix}fraction"].set(value=0.45, min=0.0, max=1.0)
        elif model_tag == "Voigt":
            s_init = fwhm_init / 2.5
            s_lo, s_hi = fwhm_lo / 4.0, fwhm_hi / 2.0
            p[f"{prefix}sigma"].set(value=s_init, min=s_lo, max=s_hi)
            p[f"{prefix}gamma"].set(value=s_init * 0.4, min=0.0, max=s_hi, vary=True)
        elif model_tag == "Gaussian":
            s_init = fwhm_init / 2.35482
            s_lo, s_hi = fwhm_lo / 2.35482, fwhm_hi / 2.35482
            p[f"{prefix}sigma"].set(value=s_init, min=s_lo, max=s_hi)
        else:  # Lorentzian
            s_init = fwhm_init / 2.0
            s_lo, s_hi = fwhm_lo / 2.0, fwhm_hi / 2.0
            p[f"{prefix}sigma"].set(value=s_init, min=s_lo, max=s_hi)

        if lock_fwhm_equal:
            if shared_sigma_expr is None:
                shared_sigma_expr = f"{prefix}sigma"
            elif model_tag == "Pseudo-Voigt" or model_tag == "Lorentzian" or model_tag == "Gaussian":
                p[f"{prefix}sigma"].set(expr=shared_sigma_expr)

        params.update(p)
        comp_prefixes.append((prefix, pk, model_tag))

    fit_res = composite_model.fit(y, params, x=x, method="least_squares", max_nfev=int(max_nfev))
    y_best = np.asarray(fit_res.best_fit, dtype=float)

    # Fit quality statistics
    ss_res = float(np.sum((y - y_best) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-12 else 1.0
    denom_rwp = float(np.sum(y ** 2))
    r_wp_pct = 100.0 * float(np.sqrt(ss_res / denom_rwp)) if denom_rwp > 1e-12 else 0.0

    # Extract per-component envelopes and physical metrics
    comps_eval = fit_res.eval_components(x=x)
    comp_curves: Dict[str, np.ndarray] = {}
    if "bg_" in comps_eval:
        comp_curves["_local_bg"] = np.asarray(comps_eval["bg_"], dtype=float)

    total_area = 0.0
    peak_summary: Dict[str, Dict[str, Any]] = {}

    for prefix, pk, model_tag in comp_prefixes:
        label = str(pk.get("label", f"Peak_{prefix}"))
        if label in peak_summary:
            label = f"{label} ({prefix[:-1]})"

        y_comp = np.asarray(comps_eval.get(prefix, np.zeros_like(x)), dtype=float)
        comp_curves[label] = y_comp

        center_fit = float(fit_res.params[f"{prefix}center"].value)
        sigma_fit = float(fit_res.params[f"{prefix}sigma"].value)

        if model_tag == "Voigt":
            gamma_fit = float(fit_res.params[f"{prefix}gamma"].value)
            fwhm_obs = _voigt_fwhm_olivero(sigma_fit, gamma_fit)
            eta_val = float(gamma_fit / max(sigma_fit + gamma_fit, 1e-9))
        elif model_tag == "Gaussian":
            fwhm_obs = 2.354820045 * sigma_fit
            eta_val = 0.0
        elif model_tag == "Lorentzian":
            fwhm_obs = 2.0 * sigma_fit
            eta_val = 1.0
        else:  # Pseudo-Voigt
            fwhm_obs = 2.0 * sigma_fit
            eta_val = float(fit_res.params[f"{prefix}fraction"].value)

        area = max(_trapz(y_comp, x), 0.0)
        height = float(np.nanmax(y_comp)) if len(y_comp) else 0.0
        integral_breadth = (area / height) if height > 1e-9 else fwhm_obs

        d_A = bragg_d_spacing(center_fit, wavelength_A=wavelength_A)
        d_nm, fwhm_corr = scherrer_crystallite_size(
            fwhm_obs,
            center_fit,
            wavelength_nm=wavelength_nm,
            k_factor=k_factor,
            beta_inst_deg=beta_inst_deg,
            broadening_mode=broadening_mode,
        )

        total_area += area
        peak_summary[label] = {
            "hkl": str(pk.get("hkl", "")),
            "Line_Shape": model_tag,
            "TwoTheta_deg": round(center_fit, 4),
            "d_Spacing_A": round(d_A, 4),
            "FWHM_obs_deg": round(fwhm_obs, 4),
            "FWHM_corr_deg": round(fwhm_corr, 4),
            "Integral_Breadth_deg": round(float(integral_breadth), 4),
            "Scherrer_D_nm": round(d_nm, 2),
            "Eta_Lorentzian": round(eta_val, 3),
            "Height_cts": round(height, 1),
            "Area": round(area, 2),
            "Area_Percent": 0.0,
            "Color": pk.get("color", "#1f77b4"),
            "Meaning": pk.get("meaning", "Bragg reflection"),
        }

    if total_area > 1e-9:
        for lbl in peak_summary:
            peak_summary[lbl]["Area_Percent"] = round(100.0 * peak_summary[lbl]["Area"] / total_area, 2)

    return fit_res, comp_curves, peak_summary, float(max(min(r2, 1.0), 0.0)), float(r_wp_pct)
