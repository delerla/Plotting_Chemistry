"""
deconvolution.py - Non-Linear Multi-Component XPS Fitting Engine
Powered by lmfit: supports Voigt, Pseudo-Voigt (GL mix), Gaussian, and Lorentzian line shapes,
with physical constraints (center locking, FWHM bounds, equal-FWHM coupling, spin-orbit branching ratios).
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from lmfit.models import VoigtModel, PseudoVoigtModel, GaussianModel, LorentzianModel


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


def _make_peak_model(line_shape: str, prefix: str):
    """Instantiates lmfit peak model from string specification."""
    ls = line_shape.lower()
    if 'pseudo' in ls or 'gl' in ls:
        return PseudoVoigtModel(prefix=prefix)
    elif 'gauss' in ls:
        return GaussianModel(prefix=prefix)
    elif 'lorentz' in ls:
        return LorentzianModel(prefix=prefix)
    else:
        return VoigtModel(prefix=prefix)


def fit_xps_components(
    x_be: np.ndarray,
    y_net: np.ndarray,
    components_cfg: List[Dict[str, Any]],
    doublet_info: Optional[Dict[str, Any]] = None,
    line_shape: str = "Voigt",
    fwhm_bounds: Tuple[float, float] = (0.4, 3.0),
    lock_fwhm_equal: bool = False,
    gl_fraction: float = 0.30,
    max_nfev: int = 4000
) -> Tuple[Any, Dict[str, np.ndarray], Dict[str, Dict[str, Any]], float]:
    """
    Fits composite models to the net intensity spectrum.
    Enforces line shapes, FWHM bounds, center locking, and spin-orbit coupling.

    Returns:
        (fit_result, component_curves_dict, parameters_summary_dict, r_squared)
    """
    if len(components_cfg) == 0:
        raise ValueError("At least one peak component configuration is required.")

    # Ensure unique prefixes
    used_prefixes = set()
    clean_cfgs = []
    for idx, cfg in enumerate(components_cfg):
        c = cfg.copy()
        pfx = c.get('prefix', f'p{idx}_')
        if not pfx.endswith('_'):
            pfx += '_'
        if pfx in used_prefixes:
            pfx = f'pk{idx}_{pfx}'
        used_prefixes.add(pfx)
        c['prefix'] = pfx
        clean_cfgs.append(c)

    # 1. Build composite model
    composite_model = None
    for cfg in clean_cfgs:
        p_shape = cfg.get('line_shape', line_shape)
        m = _make_peak_model(p_shape, cfg['prefix'])
        composite_model = m if composite_model is None else composite_model + m

    params = composite_model.make_params()

    # Estimate total net area to scale initial amplitudes
    total_area = np.trapezoid(y_net, x_be) if hasattr(np, 'trapezoid') else np.trapz(y_net, x_be)
    est_amp = max(50.0, abs(total_area) / max(1, len(clean_cfgs)))

    fwhm_min, fwhm_max = fwhm_bounds
    sigma_min = max(0.05, fwhm_min / 2.35482)
    sigma_max = max(sigma_min + 0.05, fwhm_max / 2.0)

    # 2. Configure initial parameters & physical boundary constraints
    first_pfx = clean_cfgs[0]['prefix']
    for idx, cfg in enumerate(clean_cfgs):
        pfx = cfg['prefix']
        c_val = float(cfg['center'])
        tol = float(cfg.get('center_tol', 0.35))
        fix_center = bool(cfg.get('fix_center', False))
        p_shape = cfg.get('line_shape', line_shape).lower()

        if fix_center or tol <= 0.001:
            params[f'{pfx}center'].set(value=c_val, vary=False)
        else:
            params[f'{pfx}center'].set(value=c_val, min=c_val - tol, max=c_val + tol, vary=True)

        init_sigma = float(np.clip(cfg.get('sigma', 0.55), sigma_min, sigma_max))
        params[f'{pfx}sigma'].set(value=init_sigma, min=sigma_min, max=sigma_max)

        if f'{pfx}gamma' in params:
            init_gamma = float(np.clip(cfg.get('gamma', 0.25), 0.02, sigma_max))
            params[f'{pfx}gamma'].set(value=init_gamma, min=0.02, max=sigma_max, vary=True)

        if f'{pfx}fraction' in params:
            # PseudoVoigt fraction: 0 = pure Gaussian, 1 = pure Lorentzian
            params[f'{pfx}fraction'].set(value=float(cfg.get('gl_fraction', gl_fraction)), min=0.0, max=1.0, vary=True)

        params[f'{pfx}amplitude'].set(value=float(cfg.get('amplitude', est_amp)), min=0.0)

        # Global equal FWHM constraint (optional)
        if lock_fwhm_equal and idx > 0:
            params[f'{pfx}sigma'].set(expr=f'{first_pfx}sigma')
            if f'{pfx}gamma' in params and f'{first_pfx}gamma' in params:
                params[f'{pfx}gamma'].set(expr=f'{first_pfx}gamma')

    # 3. Apply Spin-Orbit Doublet Constraints if applicable
    if doublet_info and doublet_info.get('is_doublet'):
        delta_e = float(doublet_info.get('doublet_delta_eV', 0.0))
        ratio = float(doublet_info.get('branching_ratio', 1.0))

        valid_prefixes = {c['prefix'] for c in clean_cfgs}
        for cfg in clean_cfgs:
            pfx = cfg['prefix']
            partner_pfx = cfg.get('partner_prefix')
            if partner_pfx and partner_pfx in valid_prefixes:
                params[f'{pfx}center'].set(expr=f'{partner_pfx}center + {delta_e}')
                params[f'{pfx}amplitude'].set(expr=f'{partner_pfx}amplitude / {ratio}')
                params[f'{pfx}sigma'].set(expr=f'{partner_pfx}sigma')

    # 4. Execute non-linear Levenberg-Marquardt least-squares optimization
    fit_result = composite_model.fit(y_net, params, x=x_be, method='leastsq', max_nfev=max_nfev)
    component_curves = fit_result.eval_components(x=x_be)

    # 5. Extract quantified metrics per component
    summary_dict = {}
    total_fit_area = 0.0
    used_names = {}

    for cfg in clean_cfgs:
        pfx = cfg['prefix']
        raw_name = str(cfg.get('name', pfx)).strip() or pfx
        if raw_name in used_names:
            used_names[raw_name] += 1
            disp_name = f"{raw_name} ({used_names[raw_name]})"
        else:
            used_names[raw_name] = 1
            disp_name = raw_name

        c_fitted = float(fit_result.params[f'{pfx}center'].value)
        s_fitted = float(fit_result.params[f'{pfx}sigma'].value)
        g_fitted = float(fit_result.params[f'{pfx}gamma'].value) if f'{pfx}gamma' in fit_result.params else 0.0
        amp_fitted = float(fit_result.params[f'{pfx}amplitude'].value)
        p_shape = cfg.get('line_shape', line_shape).lower()

        if 'pseudo' in p_shape or 'gl' in p_shape or 'lorentz' in p_shape:
            fwhm_val = 2.0 * s_fitted
        elif 'gauss' in p_shape:
            fwhm_val = 2.0 * s_fitted * np.sqrt(2.0 * np.log(2.0))
        else:
            fwhm_val = voigt_fwhm_olivero(s_fitted, g_fitted)

        curve = component_curves.get(pfx, np.zeros_like(x_be))
        area = abs(np.trapezoid(curve, x_be) if hasattr(np, 'trapezoid') else np.trapz(curve, x_be))
        total_fit_area += area

        gl_mix_val = float(fit_result.params[f'{pfx}fraction'].value) if f'{pfx}fraction' in fit_result.params else (0.0 if 'gauss' in p_shape else 0.30)

        summary_dict[disp_name] = {
            'prefix': pfx,
            'Line_Shape': cfg.get('line_shape', line_shape),
            'Binding_Energy_eV': round(c_fitted, 3),
            'FWHM_eV': round(float(fwhm_val), 3),
            'Sigma_eV': round(s_fitted, 3),
            'Gamma_eV': round(g_fitted, 3),
            'GL_Mix': round(gl_mix_val, 3),
            'Area_cps_eV': round(area, 2),
            'Amplitude': round(amp_fitted, 2),
            'Color': cfg.get('color', '#1f77b4'),
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
