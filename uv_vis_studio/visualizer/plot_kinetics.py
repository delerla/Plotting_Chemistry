"""
uv_vis_studio.visualizer.plot_kinetics
Publication-grade Figure Generator for UV-Vis Spectra and Reaction Kinetics.
Follows Nature/Science/ACS editorial guidelines with customizable typography.
"""

from typing import Dict, Any, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from uv_vis_studio.modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def render_kinetics_publication_plot(
    df_spectra: pd.DataFrame,
    kinetics_result: Dict[str, Any],
    lambda_target: float,
    time_points: List[float],
    theme: str = "ACS",
    font_size: int = 12,
    fig_size: Tuple[float, float] = (12.0, 5.5),
    dpi: int = 300,
    title_override: str = ""
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    """
    Renders high-resolution 2-panel publication figure:
    (a) UV-Vis Spectral Decay Series
    (b) Kinetic Regression & Mechanism Comparison
    """
    set_publication_style()
    plt.rcParams.update({
        'font.size': font_size,
        'axes.labelsize': font_size + 1,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'legend.fontsize': font_size - 2
    })

    wavelengths = df_spectra.iloc[:, 0].to_numpy().astype(float)
    time_cols = list(df_spectra.columns[1:])
    n_series = len(time_cols)

    # Colormap selection
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    cmap_name = "viridis" if theme != "Monochrome" else "Greys_r"
    colors = plt.get_cmap(cmap_name)(np.linspace(0.15, 0.85, max(n_series, 2)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size, dpi=dpi)

    # -------------------------------------------------------------
    # Panel (a): Spectral decay
    # -------------------------------------------------------------
    first_spectrum = df_spectra[time_cols[0]].to_numpy().astype(float)
    for idx, (col, color) in enumerate(zip(time_cols, colors)):
        t_label = f"{time_points[idx]:.0f} min" if idx < len(time_points) else col
        ax1.plot(wavelengths, df_spectra[col], color=color, lw=1.8, label=t_label)

    ax1.axvline(lambda_target, color='crimson', ls=':', lw=1.5, alpha=0.85)
    max_y = float(np.nanmax(first_spectrum)) if len(first_spectrum) > 0 else 1.0
    ax1.text(
        lambda_target + 8, max_y * 0.94,
        f"$\\mathbf{{\\lambda_{{max}} = {lambda_target:.0f}\\ nm}}$",
        color='crimson', fontsize=font_size, fontweight='bold'
    )

    ax1.set_xlabel(r'$\mathbf{Wavelength\ (nm)}$', fontweight='bold')
    ax1.set_ylabel(r'$\mathbf{Absorbance\ (a.u.)}$', fontweight='bold')
    
    finite_wl = wavelengths[np.isfinite(wavelengths)]
    if len(finite_wl) >= 2:
        ax1.set_xlim(float(np.nanmin(finite_wl)), float(np.nanmax(finite_wl)))
    ax1.set_ylim(0, max_y * 1.15)
    ax1.minorticks_on()
    ax1.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax1.legend(loc='upper right', framealpha=0.92, title='Time', fontsize=font_size - 2)
    ax1.text(0.04, 0.93, '(a)', transform=ax1.transAxes, fontsize=font_size + 3, fontweight='bold')

    # -------------------------------------------------------------
    # Panel (b): Kinetic Regression
    # -------------------------------------------------------------
    t_vals = kinetics_result["time_points"]
    ln_c0_ct = np.log(1.0 / kinetics_result["fraction"])
    pfo = kinetics_result["pfo"]
    pso = kinetics_result["pso"]
    best_model = kinetics_result["best_model"]

    t_dense = kinetics_result["t_dense"]
    pfo_dense = kinetics_result["pfo_dense_fit"]

    ax2.scatter(
        t_vals, ln_c0_ct,
        color='#1f77b4', s=65, edgecolor='black', lw=1.2, zorder=4,
        label='Experimental Data'
    )
    ax2.plot(
        t_dense, pfo_dense,
        color='crimson', lw=2.0, ls='-', zorder=3,
        label=f'PFO Fit (R² = {pfo["r2"]:.4f})'
    )

    t_half_str = f"$t_{{1/2}} = {pfo['t_half']:.1f}\\ \\mathbf{{min}}$" if not np.isnan(pfo['t_half']) else ""
    summary_box = (
        f"$\\mathbf{{Mechanism:\\ {best_model}}}$\n"
        f"$k_{{app}} = {pfo['k']:.4f}\\ \\mathbf{{min}}^{{-1}}$\n"
        f"$R^2_{{PFO}} = {pfo['r2']:.4f}$\n"
        f"$R^2_{{PSO}} = {pso['r2']:.4f}\n"
        f"Degradation = {kinetics_result['degradation_efficiency'][-1]:.1f}%\n"
        f"{t_half_str}"
    ).strip()

    ax2.text(
        0.06, 0.65, summary_box, transform=ax2.transAxes,
        fontsize=font_size - 1, verticalalignment='top',
        bbox=dict(boxstyle='square,pad=0.5', facecolor='#f8f9fa', edgecolor='#b0b0b0', lw=1.2)
    )

    ax2.set_xlabel(r'$\mathbf{Irradiation\ Time\ (min)}$', fontweight='bold')
    ax2.set_ylabel(r'$\mathbf{\ln(C_0 / C_t)}$', fontweight='bold')
    ax2.minorticks_on()
    ax2.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax2.legend(loc='lower right', framealpha=0.92, fontsize=font_size - 1)
    ax2.text(0.04, 0.93, '(b)', transform=ax2.transAxes, fontsize=font_size + 3, fontweight='bold')

    for ax in (ax1, ax2):
        for spine in ax.spines.values():
            spine.set_linewidth(1.6)

    if title_override:
        fig.suptitle(title_override, fontsize=font_size + 2, fontweight='bold')

    fig.tight_layout()
    return fig, (ax1, ax2)
