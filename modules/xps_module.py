"""
xps_module.py - High-Resolution XPS Shirley Baseline & Non-Linear Voigt Deconvolution Engine
Supports: C 1s / O 1s / N 1s core levels, Shirley baseline subtraction, and quantitative at% calculations.
"""

from typing import Dict, List, Optional, Tuple
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lmfit import CompositeModel, Parameters
from lmfit.models import VoigtModel

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def calculate_shirley_baseline(energy: np.ndarray, intensity: np.ndarray, max_iters: int = 30, tol: float = 1e-5) -> np.ndarray:
    """Computes iterative Shirley background for inelastic electron scattering."""
    is_ascending = energy[0] < energy[-1]
    if is_ascending:
        x = energy[::-1]
        y = intensity[::-1]
    else:
        x = energy.copy()
        y = intensity.copy()

    n_pts = len(x)
    k = min(5, max(1, n_pts // 15))
    y1 = np.mean(y[:k])
    y2 = np.mean(y[-k:])

    base = np.linspace(y1, y2, n_pts)

    for _ in range(max_iters):
        net = np.maximum(y - base, 0)
        total_area = np.trapezoid(net, -x) if hasattr(np, 'trapezoid') else np.trapz(net, -x)
        
        if total_area <= 0:
            break
            
        cum_area = np.zeros(n_pts)
        for i in range(n_pts):
            cum_area[i] = np.trapezoid(net[:i+1], -x[:i+1]) if hasattr(np, 'trapezoid') else np.trapz(net[:i+1], -x[:i+1])
            
        new_base = y2 + (y1 - y2) * (1.0 - cum_area / total_area)
        if np.max(np.abs(new_base - base)) < tol:
            base = new_base
            break
        base = new_base

    return base[::-1] if is_ascending else base


def generate_benchmark_xps_data() -> pd.DataFrame:
    """Generates synthetic high-resolution C 1s XPS spectrum."""
    be = np.linspace(292.0, 280.0, 600)
    bg = 1500.0 + 800.0 / (1.0 + np.exp(-(be - 285.5) / 1.2))
    
    def pseudo_voigt(x, x0, amp, fwhm_g, fwhm_l):
        sigma = fwhm_g / (2 * np.sqrt(2 * np.log(2)))
        gamma = fwhm_l / 2.0
        eta = 0.35
        g = np.exp(-0.5 * ((x - x0) / sigma) ** 2)
        l = (gamma**2) / ((x - x0)**2 + gamma**2)
        return amp * ((1 - eta) * g + eta * l)

    np.random.seed(42)
    p_cc = pseudo_voigt(be, 284.8, 14500, 1.15, 0.45)
    p_co = pseudo_voigt(be, 286.3, 4200, 1.20, 0.50)
    p_coo = pseudo_voigt(be, 287.8, 2100, 1.25, 0.50)
    p_acid = pseudo_voigt(be, 289.1, 1500, 1.30, 0.55)
    
    noise = np.random.normal(0, 120, len(be))
    total_counts = bg + p_cc + p_co + p_coo + p_acid + noise
    
    return pd.DataFrame({
        'Binding_Energy_eV': be,
        'Intensity_CPS': np.clip(total_counts, 0, None)
    })


def deconvolve_xps(
    df: pd.DataFrame,
    c1s_calibration: bool = True,
    expected_ref_be: float = 284.8,
    peak_configs: Optional[List[Dict[str, any]]] = None,
    theme: str = "ACS",
    fig_size: Tuple[float, float] = (8.5, 7.5)
) -> Tuple[plt.Figure, Dict[str, any], pd.DataFrame]:
    """Executes Shirley baseline subtraction and non-linear multi-peak Voigt deconvolution."""
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES['ACS'])
    
    be_raw = df.iloc[:, 0].to_numpy().astype(float)
    counts = df.iloc[:, 1].to_numpy().astype(float)
    
    sort_idx = np.argsort(be_raw)[::-1]
    be = be_raw[sort_idx]
    counts = counts[sort_idx]

    baseline = calculate_shirley_baseline(be, counts)
    net_intensity = np.maximum(counts - baseline, 0)

    be_shift = 0.0
    if c1s_calibration:
        near_c1s = (be >= 283.0) & (be <= 286.5)
        if np.any(near_c1s):
            raw_peak_pos = be[near_c1s][np.argmax(net_intensity[near_c1s])]
            be_shift = expected_ref_be - raw_peak_pos
            be = be + be_shift

    if peak_configs is None:
        peak_configs = [
            {'prefix': 'C_C_', 'name': 'C-C / C-H', 'center': 284.8, 'sigma': 0.55, 'gamma': 0.25, 'color': palette[0]},
            {'prefix': 'C_O_', 'name': 'C-O', 'center': 286.3, 'sigma': 0.58, 'gamma': 0.25, 'color': palette[1]},
            {'prefix': 'C_dbl_O_', 'name': 'C=O', 'center': 287.8, 'sigma': 0.60, 'gamma': 0.25, 'color': palette[2]},
            {'prefix': 'O_C_O_', 'name': 'O-C=O', 'center': 289.1, 'sigma': 0.62, 'gamma': 0.25, 'color': palette[3]},
        ]

    composite_model = None
    for cfg in peak_configs:
        v_model = VoigtModel(prefix=cfg['prefix'])
        composite_model = v_model if composite_model is None else composite_model + v_model

    params = composite_model.make_params()
    for cfg in peak_configs:
        pfx = cfg['prefix']
        params[f'{pfx}center'].set(value=cfg['center'], min=cfg['center'] - 0.45, max=cfg['center'] + 0.45)
        params[f'{pfx}sigma'].set(value=cfg.get('sigma', 0.55), min=0.2, max=1.2)
        params[f'{pfx}gamma'].set(value=cfg.get('gamma', 0.25), min=0.05, max=0.9, vary=True)
        params[f'{pfx}amplitude'].set(value=cfg.get('amplitude', 5000.0), min=100.0)

    fit_result = composite_model.fit(net_intensity, params, x=be, method='leastsq')
    peak_components = fit_result.eval_components(x=be)
    
    total_fitted_area = 0.0
    component_areas = {}
    
    for cfg in peak_configs:
        pfx = cfg['prefix']
        curve = peak_components[pfx]
        area = float(np.trapezoid(curve, -be) if hasattr(np, 'trapezoid') else np.trapz(curve, -be))
        component_areas[cfg['name']] = area
        total_fitted_area += area

    quant_results = []
    for cfg in peak_configs:
        name = cfg['name']
        pfx = cfg['prefix']
        cen = float(fit_result.params[f'{pfx}center'].value)
        sigma = float(fit_result.params[f'{pfx}sigma'].value)
        gamma = float(fit_result.params[f'{pfx}gamma'].value)
        f_g = 2.0 * sigma * np.sqrt(2.0 * np.log(2.0))
        f_l = 2.0 * gamma
        fwhm_calc = 0.5346 * f_l + np.sqrt(0.2166 * (f_l ** 2) + (f_g ** 2))
        
        area = component_areas[name]
        pct = (area / total_fitted_area * 100.0) if total_fitted_area > 0 else 0.0
        quant_results.append({
            'Component': name,
            'Binding_Energy_eV': round(cen, 2),
            'FWHM_eV': round(fwhm_calc, 2),
            'Integrated_Area': round(area, 1),
            'Atomic_Concentration_pct': round(pct, 2)
        })

    fig = plt.figure(figsize=fig_size, dpi=300)
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 4], hspace=0.08)
    
    ax_res = fig.add_subplot(gs[0])
    ax_main = fig.add_subplot(gs[1], sharex=ax_res)
    
    residuals = net_intensity - fit_result.best_fit
    ax_res.plot(be, residuals, color='black', lw=1.0)
    ax_res.axhline(0, color='gray', ls='--', lw=1.0)
    ax_res.set_ylabel(r'$\mathbf{\Delta I}$', fontsize=11)
    ax_res.tick_params(axis='both', which='both', direction='in', labelbottom=False)
    ax_res.set_title(r'$\mathbf{High-Resolution\ Core-Level\ Voigt\ Multi-Peak\ Deconvolution}$', fontsize=13, pad=10)
    
    total_fit_with_bg = fit_result.best_fit + baseline
    ax_main.scatter(be, counts, color='black', s=14, alpha=0.7, label='Experimental Counts', zorder=2)
    ax_main.plot(be, baseline, color='#7f7f7f', lw=1.6, ls='--', label='Shirley Baseline', zorder=3)
    ax_main.plot(be, total_fit_with_bg, color='crimson', lw=2.0, label='Envelope Fit', zorder=5)
    
    labplot_dict = {
        'Binding_Energy_eV': be,
        'Experimental_CPS': counts,
        'Shirley_Baseline': baseline,
        'Envelope_Fit': total_fit_with_bg,
        'Residuals': residuals
    }
    
    for idx, cfg in enumerate(peak_configs):
        name = cfg['name']
        pfx = cfg['prefix']
        comp_curve = peak_components[pfx] + baseline
        labplot_dict[f"Voigt_{pfx}"] = comp_curve
        color = cfg.get('color', palette[idx % len(palette)])
        ax_main.plot(be, comp_curve, color=color, lw=1.6, zorder=4)
        ax_main.fill_between(be, baseline, comp_curve, color=color, alpha=0.25, label=f"{name}")

    ax_main.set_xlim(np.max(be), np.min(be))
    ax_main.set_xlabel(r'$\mathbf{Binding\ Energy\ (eV)}$', fontsize=13, labelpad=8)
    ax_main.set_ylabel(r'$\mathbf{Intensity\ (Counts\ /\ s)}$', fontsize=13, labelpad=10)
    ax_main.minorticks_on()
    ax_main.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax_main.legend(loc='upper left', framealpha=0.92, fontsize=9.5)
    
    for ax in (ax_res, ax_main):
        for spine in ax.spines.values():
            spine.set_linewidth(1.6)

    fig.subplots_adjust(left=0.12, right=0.96, top=0.93, bottom=0.10, hspace=0.08)
    
    summary = {
        'be_shift_applied_eV': round(be_shift, 3),
        'chi_square': round(float(fit_result.chisqr), 2),
        'redchi': round(float(fit_result.redchi), 2),
        'r_squared': round(float(1.0 - (np.var(residuals) / np.var(net_intensity))), 4),
        'quantification_table': quant_results
    }
    
    labplot_df = pd.DataFrame(labplot_dict)
    return fig, summary, labplot_df
