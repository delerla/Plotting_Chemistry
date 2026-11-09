"""
uv_vis_module.py - UV-Vis Spectroscopy & Dye Photodegradation Kinetics Engine
"""

from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

from modules.export_utils import set_publication_style


def generate_benchmark_uv_vis_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates synthetic benchmark UV-Vis spectra and photodegradation kinetics data.
    Simulates dye (e.g., Rhodamine B, lambda_max = 554 nm) under photocatalytic degradation.
    """
    wavelengths = np.linspace(350, 750, 1000)
    times = [0, 15, 30, 45, 60, 90, 120]  # minutes
    k_true = 0.0215  # min^-1
    c0 = 10.0  # mg/L
    
    # Base spectra generation
    spectra_dict = {'Wavelength_nm': wavelengths}
    kinetics_rows = []
    
    np.random.seed(42)
    for t in times:
        # Pseudo-first-order concentration decay
        c_t = c0 * np.exp(-k_true * t)
        fraction = c_t / c0
        
        # Primary chromophore peak at 554 nm + secondary peak at 520 nm
        a_primary = 1.65 * fraction * np.exp(-0.5 * ((wavelengths - 554) / 28.0) ** 2)
        a_shoulder = 0.55 * fraction * np.exp(-0.5 * ((wavelengths - 520) / 18.0) ** 2)
        baseline = 0.04 + 0.01 * np.exp(-0.005 * (wavelengths - 350))
        noise = np.random.normal(0, 0.004, len(wavelengths))
        
        absorbance = np.clip(a_primary + a_shoulder + baseline + noise, 0, None)
        spectra_dict[f"{t} min"] = absorbance
        
        # Exact absorbance at 554 nm
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
    fig_size: Tuple[float, float] = (12.0, 5.5)
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes], Dict[str, any], pd.DataFrame, pd.DataFrame]:
    """
    Analyzes UV-Vis spectra and photodegradation kinetics.
    Produces dual-panel publication graphic:
        (a) Time-resolved UV-Vis spectra
        (b) Pseudo-first-order & Pseudo-second-order kinetic fitting
    Returns:
        fig, (ax1, ax2), kinetics_metrics, labplot_spectra_df, labplot_kinetics_df
    """
    set_publication_style()
    wavelengths = df_spectra.iloc[:, 0].to_numpy()
    time_cols = list(df_spectra.columns[1:])
    
    # Parse times from column names if not provided
    if time_points is None or len(time_points) != len(time_cols):
        extracted_times = []
        for c in time_cols:
            digits = ''.join(ch for ch in c if ch.isdigit() or ch == '.')
            extracted_times.append(float(digits) if digits else 0.0)
        time_points = extracted_times
        
    # Auto-detect lambda_max from first spectrum (t=0) if not specified
    first_spectrum = df_spectra[time_cols[0]].to_numpy()
    if lambda_target is None:
        idx_peak = np.argmax(first_spectrum)
        lambda_max = float(wavelengths[idx_peak])
    else:
        lambda_max = float(lambda_target)
        idx_peak = np.argmin(np.abs(wavelengths - lambda_max))

    # Calculate degradation ratios
    a_vals = []
    for c in time_cols:
        a_vals.append(float(df_spectra[c].iloc[idx_peak]))
    a_vals = np.array(a_vals)
    t_vals = np.array(time_points)
    
    a0 = a_vals[0] if a_vals[0] > 0 else 1.0
    c_ratio = np.clip(a_vals / a0, 1e-6, 1.0)
    c_t = initial_conc * c_ratio
    deg_efficiency = (1.0 - c_ratio) * 100.0
    
    # Pseudo-first-order: ln(C0 / Ct) = k_app * t
    ln_c0_ct = np.log(1.0 / c_ratio)
    res_pfo = linregress(t_vals, ln_c0_ct)
    k_pfo = res_pfo.slope
    r2_pfo = res_pfo.rvalue ** 2
    
    # Pseudo-second-order: 1/Ct - 1/C0 = k2 * t
    inv_ct_c0 = (1.0 / c_t) - (1.0 / initial_conc)
    res_pso = linregress(t_vals, inv_ct_c0)
    k_pso = res_pso.slope
    r2_pso = res_pso.rvalue ** 2
    
    metrics = {
        'lambda_max_nm': round(lambda_max, 1),
        'k_pseudo_first_order_min-1': round(float(k_pfo), 5),
        'R2_pseudo_first_order': round(float(r2_pfo), 4),
        'k_pseudo_second_order': round(float(k_pso), 6),
        'R2_pseudo_second_order': round(float(r2_pso), 4),
        'final_degradation_pct': round(float(deg_efficiency[-1]), 2),
    }

    # Plotting Dual-Panel Publication Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size, dpi=300)
    
    # Colormap for time progression
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(time_cols)))
    
    # Panel (a): UV-Vis Spectra
    for idx, (col, color) in enumerate(zip(time_cols, colors)):
        ax1.plot(wavelengths, df_spectra[col], color=color, lw=1.8, label=f"{time_points[idx]:.0f} min")
        
    ax1.axvline(lambda_max, color='crimson', ls=':', lw=1.4, alpha=0.85)
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
    ax1.legend(loc='upper right', framealpha=0.9, title='Irradiation Time', fontsize=9.5, title_fontsize=10)
    ax1.text(0.04, 0.93, '(a)', transform=ax1.transAxes, fontsize=15, fontweight='bold')
    
    # Panel (b): Kinetic Linear Fit (Pseudo-First-Order)
    t_fit = np.linspace(0, max(t_vals), 100)
    fit_line = res_pfo.slope * t_fit + res_pfo.intercept
    
    ax2.scatter(t_vals, ln_c0_ct, color='#1f77b4', s=55, edgecolor='black', lw=1.2, zorder=4, label='Experimental Data')
    ax2.plot(t_fit, fit_line, color='#d62728', lw=2.0, ls='-', zorder=3, label='Pseudo-First-Order Fit')
    
    fit_annotation = (
        f"$\\mathbf{{\\ln(C_0 / C_t) = k_{{app}} \\cdot t}}$\n"
        f"$k_{{app}} = {k_pfo:.4f}\\ \\mathbf{{min}}^{{-1}}$\n"
        f"$R^2 = {r2_pfo:.4f}$\n"
        f"Degradation = {deg_efficiency[-1]:.1f}%"
    )
    ax2.text(
        0.06, 0.65, fit_annotation, transform=ax2.transAxes,
        fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='square,pad=0.5', facecolor='#f7f7f7', edgecolor='#b0b0b0', lw=1.2)
    )
    
    ax2.set_xlabel(r'$\mathbf{Irradiation\ Time\ (min)}$', fontsize=13)
    ax2.set_ylabel(r'$\mathbf{\ln(C_0 / C_t)}$', fontsize=13)
    ax2.minorticks_on()
    ax2.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax2.legend(loc='lower right', framealpha=0.9, fontsize=10)
    ax2.text(0.04, 0.93, '(b)', transform=ax2.transAxes, fontsize=15, fontweight='bold')
    
    for ax in (ax1, ax2):
        for spine in ax.spines.values():
            spine.set_linewidth(1.6)

    fig.tight_layout()
    
    # LabPlot formatted tables
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
