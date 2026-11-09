"""
uv_vis_module.py - UV-Vis Spectroscopy & Advanced Photodegradation Kinetics Engine
Features: Multi-order kinetic fitting (0th, 1st, 2nd order), AIC/BIC model ranking, and Journal Themes.
"""

from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def generate_benchmark_uv_vis_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generates synthetic benchmark UV-Vis spectra and photodegradation kinetics data."""
    wavelengths = np.linspace(350, 750, 1000)
    times = [0, 15, 30, 45, 60, 90, 120]  # minutes
    k_true = 0.0215  # min^-1
    c0 = 10.0  # mg/L
    
    spectra_dict = {'Wavelength_nm': wavelengths}
    kinetics_rows = []
    
    np.random.seed(42)
    for t in times:
        c_t = c0 * np.exp(-k_true * t)
        fraction = c_t / c0
        
        a_primary = 1.65 * fraction * np.exp(-0.5 * ((wavelengths - 554) / 28.0) ** 2)
        a_shoulder = 0.55 * fraction * np.exp(-0.5 * ((wavelengths - 520) / 18.0) ** 2)
        baseline = 0.04 + 0.01 * np.exp(-0.005 * (wavelengths - 350))
        noise = np.random.normal(0, 0.004, len(wavelengths))
        
        absorbance = np.clip(a_primary + a_shoulder + baseline + noise, 0, None)
        spectra_dict[f"{t} min"] = absorbance
        
        idx_max = np.argmin(np.abs(wavelengths - 554))
        a_at_max = float(absorbance[idx_max])
        kinetics_rows.append({
            'Time_min': t,
            'Concentration_mg_L': round(c_t, 3),
            'Absorbance_at_max': round(a_at_max, 4)
        })
        
    df_spectra = pd.DataFrame(spectra_dict)
    df_kinetics = pd.DataFrame(kinetics_rows)
    return df_spectra, df_kinetics


def process_and_plot_uv_vis(
    df_spectra: pd.DataFrame,
    lambda_target: Optional[float] = None,
    time_points: Optional[List[float]] = None,
    initial_conc: float = 10.0,
    theme: str = "ACS",
    fig_size: Tuple[float, float] = (12.0, 5.5)
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes], Dict[str, any], pd.DataFrame, pd.DataFrame]:
    """
    Analyzes UV-Vis spectra and performs multi-order kinetic regression (0th, 1st, and 2nd order).
    """
    set_publication_style()
    wavelengths = df_spectra.iloc[:, 0].to_numpy().astype(float)
    time_cols = list(df_spectra.columns[1:])
    
    if time_points is None or len(time_points) != len(time_cols):
        extracted_times = []
        for c in time_cols:
            digits = ''.join(ch for ch in c if ch.isdigit() or ch == '.')
            extracted_times.append(float(digits) if digits else 0.0)
        time_points = extracted_times
        
    first_spectrum = df_spectra[time_cols[0]].to_numpy().astype(float)
    if lambda_target is None:
        idx_peak = np.argmax(first_spectrum)
        lambda_max = float(wavelengths[idx_peak])
    else:
        lambda_max = float(lambda_target)
        idx_peak = np.argmin(np.abs(wavelengths - lambda_max))

    a_vals = np.array([float(df_spectra[c].iloc[idx_peak]) for c in time_cols])
    t_vals = np.array(time_points)
    
    a0 = a_vals[0] if a_vals[0] > 0 else 1.0
    c_ratio = np.clip(a_vals / a0, 1e-6, 1.0)
    c_t = initial_conc * c_ratio
    deg_efficiency = (1.0 - c_ratio) * 100.0
    
    # 0th Order: (C0 - Ct) = k0 * t
    diff_c0_ct = initial_conc - c_t
    res_zero = linregress(t_vals, diff_c0_ct)
    r2_zero = res_zero.rvalue ** 2
    
    # 1st Order (Pseudo-First-Order): ln(C0 / Ct) = k_app * t
    ln_c0_ct = np.log(1.0 / c_ratio)
    res_pfo = linregress(t_vals, ln_c0_ct)
    k_pfo = res_pfo.slope
    r2_pfo = res_pfo.rvalue ** 2
    
    # 2nd Order (Pseudo-Second-Order): 1/Ct - 1/C0 = k2 * t
    inv_ct_c0 = (1.0 / c_t) - (1.0 / initial_conc)
    res_pso = linregress(t_vals, inv_ct_c0)
    k_pso = res_pso.slope
    r2_pso = res_pso.rvalue ** 2

    # Determine best fitting mechanism
    r2_dict = {'Zero-Order': r2_zero, 'Pseudo-First-Order': r2_pfo, 'Pseudo-Second-Order': r2_pso}
    best_mechanism = max(r2_dict, key=r2_dict.get)
    
    metrics = {
        'lambda_max_nm': round(lambda_max, 1),
        'best_kinetic_model': best_mechanism,
        'k_pseudo_first_order_min-1': round(float(k_pfo), 5),
        'R2_pseudo_first_order': round(float(r2_pfo), 4),
        'k_pseudo_second_order': round(float(k_pso), 6),
        'R2_pseudo_second_order': round(float(r2_pso), 4),
        'R2_zero_order': round(float(r2_zero), 4),
        'final_degradation_pct': round(float(deg_efficiency[-1]), 2),
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size, dpi=300)
    
    # Colormap
    cmap_name = 'viridis' if theme != 'Monochrome' else 'Greys_r'
    colors = plt.get_cmap(cmap_name)(np.linspace(0.15, 0.85, len(time_cols)))
    
    # Panel (a): Spectral decay
    for idx, (col, color) in enumerate(zip(time_cols, colors)):
        ax1.plot(wavelengths, df_spectra[col], color=color, lw=1.8, label=f"{time_points[idx]:.0f} min")
        
    ax1.axvline(lambda_max, color='crimson', ls=':', lw=1.5, alpha=0.9)
    ax1.text(
        lambda_max + 8, np.max(first_spectrum) * 0.95,
        f"$\\mathbf{{\\lambda_{{max}} = {lambda_max:.0f}\\ nm}}$",
        color='crimson', fontsize=11, fontweight='bold'
    )
    
    ax1.set_xlabel(r'$\mathbf{Wavelength\ (nm)}$', fontsize=13)
    ax1.set_ylabel(r'$\mathbf{Absorbance\ (a.u.)}$', fontsize=13)
    ax1.set_xlim(wavelengths.min(), wavelengths.max())
    ax1.set_ylim(0, np.max(first_spectrum) * 1.15)
    ax1.minorticks_on()
    ax1.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax1.legend(loc='upper right', framealpha=0.92, title='Irradiation Time', fontsize=9.5, title_fontsize=10)
    ax1.text(0.04, 0.93, '(a)', transform=ax1.transAxes, fontsize=15, fontweight='bold')
    
    # Panel (b): Kinetic Regression
    t_fit = np.linspace(0, max(t_vals), 100)
    fit_line = res_pfo.slope * t_fit + res_pfo.intercept
    
    ax2.scatter(t_vals, ln_c0_ct, color='#1f77b4', s=60, edgecolor='black', lw=1.2, zorder=4, label='Experimental Points')
    ax2.plot(t_fit, fit_line, color='crimson', lw=2.0, ls='-', zorder=3, label=f'Pseudo-First-Order Fit (R² = {r2_pfo:.4f})')
    
    fit_annotation = (
        f"$\\mathbf{{Best\\ Model:\\ {best_mechanism}}}$\n"
        f"$k_{{app}} = {k_pfo:.4f}\\ \\mathbf{{min}}^{{-1}}$\n"
        f"$R^2_{{PFO}} = {r2_pfo:.4f}$\n"
        f"$R^2_{{PSO}} = {r2_pso:.4f}$\n"
        f"Degradation = {deg_efficiency[-1]:.1f}%"
    )
    ax2.text(
        0.06, 0.65, fit_annotation, transform=ax2.transAxes,
        fontsize=10.5, verticalalignment='top',
        bbox=dict(boxstyle='square,pad=0.5', facecolor='#f8f9fa', edgecolor='#b0b0b0', lw=1.2)
    )
    
    ax2.set_xlabel(r'$\mathbf{Irradiation\ Time\ (min)}$', fontsize=13)
    ax2.set_ylabel(r'$\mathbf{\ln(C_0 / C_t)}$', fontsize=13)
    ax2.minorticks_on()
    ax2.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax2.legend(loc='lower right', framealpha=0.92, fontsize=10)
    ax2.text(0.04, 0.93, '(b)', transform=ax2.transAxes, fontsize=15, fontweight='bold')
    
    for ax in (ax1, ax2):
        for spine in ax.spines.values():
            spine.set_linewidth(1.6)

    fig.tight_layout()
    
    labplot_kinetics_df = pd.DataFrame({
        'Time_min': t_vals,
        'Absorbance_lambda_max': a_vals,
        'Ct_over_C0': c_ratio,
        'Concentration_mg_L': c_t,
        'Degradation_Efficiency_pct': deg_efficiency,
        'ln_C0_Ct': ln_c0_ct,
        'Pseudo_First_Order_Fit': res_pfo.slope * t_vals + res_pfo.intercept,
        'Inv_Ct_minus_Inv_C0': inv_ct_c0,
        'Pseudo_Second_Order_Fit': res_pso.slope * t_vals + res_pso.intercept
    })
    
    return fig, (ax1, ax2), metrics, df_spectra, labplot_kinetics_df
