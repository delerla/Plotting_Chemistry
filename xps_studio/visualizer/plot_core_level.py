"""
plot_core_level.py - Publication-Grade Core-Level XPS Figure & Matrix Generator
Generates dual-panel figures (Residuals + Deconvoluted Envelope) calibrated for 600 DPI,
journal color palettes, and formatted LabPlot ASCII tables.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def render_core_level_plot(
    x_be: np.ndarray,
    y_raw: np.ndarray,
    baseline: np.ndarray,
    fit_result: Any,
    components_curves: Dict[str, np.ndarray],
    components_summary: Dict[str, Dict[str, Any]],
    core_label: str = "C 1s",
    theme: str = "ACS",
    fig_size: Tuple[float, float] = (8.5, 7.5)
) -> Tuple[plt.Figure, pd.DataFrame]:
    """
    Renders high-resolution XPS figure with upper residual panel and lower core-level spectrum.
    Returns:
        (matplotlib_figure, labplot_dataframe)
    """
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES['ACS'])
    
    # Ensure descending BE order
    if x_be[0] < x_be[-1]:
        idx_rev = np.argsort(x_be)[::-1]
        x_be = x_be[idx_rev]
        y_raw = y_raw[idx_rev]
        baseline = baseline[idx_rev]
        best_fit = fit_result.best_fit[idx_rev]
        comp_curves_clean = {k: v[idx_rev] for k, v in components_curves.items()}
    else:
        best_fit = fit_result.best_fit
        comp_curves_clean = components_curves

    total_fit_with_bg = best_fit + baseline
    residuals = y_raw - total_fit_with_bg

    fig = plt.figure(figsize=fig_size, dpi=300)
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 4.2], hspace=0.08)
    
    # 1. Residuals Panel (Top)
    ax_res = fig.add_subplot(gs[0])
    ax_res.plot(x_be, residuals, color='black', lw=1.1)
    ax_res.axhline(0, color='gray', ls='--', lw=1.0, alpha=0.8)
    ax_res.set_ylabel(r'$\mathbf{\Delta I}$', fontsize=11, labelpad=6)
    ax_res.tick_params(axis='both', which='both', direction='in', labelbottom=False)
    ax_res.set_title(f"$\\mathbf{{{core_label}\\ High-Resolution\\ Voigt\\ Multi-Peak\\ Deconvolution}}$", fontsize=13, pad=10)
    
    # 2. Main Spectrum Panel (Bottom)
    ax_main = fig.add_subplot(gs[1], sharex=ax_res)
    
    # Raw Experimental Data
    ax_main.scatter(x_be, y_raw, color='#111111', s=16, alpha=0.75, label='Experimental Data', zorder=2)
    # Shirley Baseline
    ax_main.plot(x_be, baseline, color='#7f7f7f', lw=1.6, ls='--', label='Shirley Baseline', zorder=3)
    # Total Fit Envelope
    ax_main.plot(x_be, total_fit_with_bg, color='crimson', lw=2.0, label='Envelope Fit', zorder=5)

    # Shaded Peak Components
    labplot_dict = {
        'Binding_Energy_eV': x_be,
        'Experimental_CPS': y_raw,
        'Shirley_Baseline': baseline,
        'Envelope_Fit': total_fit_with_bg,
        'Residuals': residuals
    }

    comp_list = list(components_summary.items())
    for idx, (name, metrics) in enumerate(comp_list):
        pfx = metrics['prefix']
        curve = comp_curves_clean.get(pfx, np.zeros_like(x_be))
        comp_with_bg = curve + baseline
        
        color = 'black' if theme == 'Monochrome' else palette[idx % len(palette)]
        lab_name = f"{name} ({metrics['Binding_Energy_eV']:.1f} eV, {metrics['Area_Percent']:.1f}%)"
        
        ax_main.plot(x_be, comp_with_bg, color=color, lw=1.6, ls='-', zorder=4)
        ax_main.fill_between(x_be, baseline, comp_with_bg, color=color, alpha=0.25, label=lab_name, zorder=3)
        labplot_dict[f"Comp_{name.replace(' ', '_')}"] = comp_with_bg

    # Invert Binding Energy scale (standard XPS convention)
    finite_be = x_be[np.isfinite(x_be)]
    if len(finite_be) >= 2:
        ax_main.set_xlim(float(np.nanmax(finite_be)), float(np.nanmin(finite_be)))

    ax_main.set_xlabel(r'$\mathbf{Binding\ Energy\ (eV)}$', fontsize=13, labelpad=8)
    ax_main.set_ylabel(r'$\mathbf{Intensity\ (Counts\ /\ s)}$', fontsize=13, labelpad=10)
    ax_main.minorticks_on()
    ax_main.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax_main.legend(loc='upper left', framealpha=0.92, fontsize=9.2, title='Chemical States', title_fontsize=10)

    for ax in (ax_res, ax_main):
        for spine in ax.spines.values():
            spine.set_linewidth(1.6)

    fig.subplots_adjust(left=0.12, right=0.96, top=0.93, bottom=0.10, hspace=0.08)
    labplot_df = pd.DataFrame(labplot_dict)
    
    return fig, labplot_df
