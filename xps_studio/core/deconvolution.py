"""
deconvolution.py - Non-Linear Multi-Component Voigt & Spin-Orbit Doublet Fitting Engine
Powered by lmfit: encloses physical constraints (energy bounds, FWHM coupling, spin-orbit branching ratios).
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from lmfit.models import VoigtModel


def voigt_fwhm_olivero(sigma: float, gamma: float) -> float:
    """
    Computes accurate full width at half maximum (FWHM) of a Voigt profile
    using Olivero & Longbothum (1977) semi-empirical formula (accuracy > 0.02%):
        f_G = 2 * sigma * sqrt(2 * ln(2))
        f_L = 2 * gamma
        f_V = 0.5346 * f_L + sqrt(0.2166 * f_L^2 + f_G^2)
    """
    f_g = 2.0 * sigma * np.sqrt(2.0 * np.log(2.0))
    f_l = 2.0 * gamma
    return float(0.5346 * f_l + np.sqrt(0.2166 * (f_l ** 2) + (f_g ** 2)))


def fit_xps_components(
    x_be: np.ndarray,
    y_net: np.ndarray,
    components_cfg: List[Dict[str, Any]],
    doublet_info: Optional[Dict[str, Any]] = None,
    max_nfev: int = 4000
) -> Tuple[Any, Dict[str, np.ndarray], Dict[str, Dict[str, float]], float]:
    """
    Fits composite Voigt models to the net intensity spectrum.
    Enforces spin-orbit coupling where specified.
    
    Returns:
        (fit_result, component_curves_dict, parameters_summary_dict, r_squared)
    """
    if len(components_cfg) == 0:
        raise ValueError("At least one peak component configuration is required.")

    # 1. Build composite model
    composite_model = None
    for cfg in components_cfg:
        pfx = cfg['prefix']
        v = VoigtModel(prefix=pfx)
        composite_model = v if composite_model is None else composite_model + v

    params = composite_model.make_params()
    
    # Estimate total net area to scale initial amplitudes
    total_area = np.trapezoid(y_net, x_be) if hasattr(np, 'trapezoid') else np.trapz(y_net, x_be)
    est_amp = abs(total_area) / max(1, len(components_cfg))

    # 2. Configure initial parameters & physical boundary constraints
    for cfg in components_cfg:
        pfx = cfg['prefix']
        c_val = cfg['center']
        tol = cfg.get('center_tol', 0.35)
        
        params[f'{pfx}center'].set(value=c_val, min=c_val - tol, max=c_val + tol)
        params[f'{pfx}sigma'].set(value=cfg.get('sigma', 0.55), min=0.20, max=1.20)
        params[f'{pfx}gamma'].set(value=cfg.get('gamma', 0.25), min=0.05, max=0.85, vary=True)
        params[f'{pfx}amplitude'].set(value=cfg.get('amplitude', est_amp), min=10.0)

    # 3. Apply Spin-Orbit Doublet Constraints if applicable
    # (Coupling partner peak position and area branching ratio)
    if doublet_info and doublet_info.get('is_doublet'):
        delta_e = doublet_info.get('doublet_delta_eV', 0.0)
        ratio = doublet_info.get('branching_ratio', 1.0)
        
        # Link doublet pairs by naming convention or explicit partner specification
        for cfg in components_cfg:
            pfx = cfg['prefix']
            partner_pfx = cfg.get('partner_prefix')
            if partner_pfx and partner_pfx in [c['prefix'] for c in components_cfg]:
                # Expression constraint: Partner Center = Primary Center + Delta E
                params[f'{pfx}center'].set(expr=f'{partner_pfx}center + {delta_e}')
                # Expression constraint: Partner Amplitude = Primary Amplitude / Branching Ratio
                params[f'{pfx}amplitude'].set(expr=f'{partner_pfx}amplitude / {ratio}')
                # FWHM Coupling: Partner Sigma = Primary Sigma
                params[f'{pfx}sigma'].set(expr=f'{partner_pfx}sigma')

    # 4. Execute non-linear Levenberg-Marquardt least-squares optimization
    fit_result = composite_model.fit(y_net, params, x=x_be, method='leastsq', max_nfev=max_nfev)
    component_curves = fit_result.eval_components(x=x_be)
    
    # 5. Extract quantified metrics per component
    summary_dict = {}
    total_fit_area = 0.0
    
    for cfg in components_cfg:
        pfx = cfg['prefix']
        name = cfg['name']
        c_fitted = float(fit_result.params[f'{pfx}center'].value)
        s_fitted = float(fit_result.params[f'{pfx}sigma'].value)
        g_fitted = float(fit_result.params[f'{pfx}gamma'].value)
        amp_fitted = float(fit_result.params[f'{pfx}amplitude'].value)
        
        fwhm_val = voigt_fwhm_olivero(s_fitted, g_fitted)
        
        # Exact numerical area of this component
        curve = component_curves.get(pfx, np.zeros_like(x_be))
        area = abs(np.trapezoid(curve, x_be) if hasattr(np, 'trapezoid') else np.trapz(curve, x_be))
        total_fit_area += area
        
        summary_dict[name] = {
            'prefix': pfx,
            'Binding_Energy_eV': round(c_fitted, 3),
            'FWHM_eV': round(fwhm_val, 3),
            'Sigma_eV': round(s_fitted, 3),
            'Gamma_eV': round(g_fitted, 3),
            'Area_cps_eV': round(area, 2),
            'Amplitude': round(amp_fitted, 2),
            'Meaning': cfg.get('meaning', '')
        }

    # Relative percentage of each component
    for name in summary_dict:
        if total_fit_area > 0:
            summary_dict[name]['Area_Percent'] = round((summary_dict[name]['Area_cps_eV'] / total_fit_area) * 100.0, 2)
        else:
            summary_dict[name]['Area_Percent'] = 0.0

    residuals = y_net - fit_result.best_fit
    r2 = 1.0 - (np.var(residuals) / np.var(y_net)) if np.var(y_net) > 0 else 0.0

    return fit_result, component_curves, summary_dict, float(r2)
