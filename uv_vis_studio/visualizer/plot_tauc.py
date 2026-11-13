"""
uv_vis_studio.visualizer.plot_tauc
Publication-grade Figure Generator for Optical Absorbance & Tauc Plot Bandgap Analysis.
"""

from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from uv_vis_studio.modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def render_tauc_publication_plot(
    df_tauc: pd.DataFrame,
    tauc_fit: Dict[str, Any],
    urbach_fit: Dict[str, Any],
    transition_label: str = "Direct Allowed (n = 1/2)",
    theme: str = "ACS",
    font_size: int = 12,
    fig_size: Tuple[float, float] = (12.0, 5.5),
    dpi: int = 300,
    title_override: str = ""
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    """
    Renders high-resolution 2-panel publication figure:
    (a) Optical Absorbance Spectrum vs Wavelength (nm)
    (b) Tauc Plot: (alpha * hv)^(1/n) vs Photon Energy (eV) with Eg extrapolation
    """
    set_publication_style()
    plt.rcParams.update({
        'font.size': font_size,
        'axes.labelsize': font_size + 1,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'legend.fontsize': font_size - 2
    })

    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    primary_color = palette[0]
    secondary_color = palette[1] if len(palette) > 1 else "crimson"

    wl = df_tauc["Wavelength_nm"].to_numpy().astype(float)
    abs_vals = df_tauc["Absorbance_OD"].to_numpy().astype(float)
    energy = df_tauc["Photon_Energy_eV"].to_numpy().astype(float)
    tauc_y = df_tauc["Tauc_Y"].to_numpy().astype(float)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size, dpi=dpi)

    # -------------------------------------------------------------
    # Panel (a): Optical Absorbance Spectrum
    # -------------------------------------------------------------
    ax1.plot(wl, abs_vals, color=primary_color, lw=2.2, label='Absorbance')
    ax1.set_xlabel(r'$\mathbf{Wavelength\ (nm)}$', fontweight='bold')
    ax1.set_ylabel(r'$\mathbf{Absorbance\ (O.D.)}$', fontweight='bold')
    
    finite_wl = wl[np.isfinite(wl)]
    if len(finite_wl) >= 2:
        ax1.set_xlim(float(np.nanmin(finite_wl)), float(np.nanmax(finite_wl)))
    ax1.set_ylim(0, float(np.nanmax(abs_vals)) * 1.15)
    ax1.minorticks_on()
    ax1.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    ax1.legend(loc='upper right', framealpha=0.92)
    ax1.text(0.04, 0.93, '(a)', transform=ax1.transAxes, fontsize=font_size + 3, fontweight='bold')

    # Absorption onset marker if bandgap is determined
    eg = tauc_fit.get("bandgap_ev", np.nan)
    lam_onset = tauc_fit.get("lambda_onset_nm", np.nan)
    if not np.isnan(lam_onset) and min(wl) <= lam_onset <= max(wl):
        ax1.axvline(lam_onset, color='crimson', ls='--', lw=1.5, alpha=0.85)
        ax1.text(
            lam_onset + 6, max(abs_vals) * 0.85,
            f"$\\mathbf{{\\lambda_{{onset}} = {lam_onset:.0f}\\ nm}}$",
            color='crimson', fontsize=font_size - 1, fontweight='bold'
        )

    # -------------------------------------------------------------
    # Panel (b): Tauc Plot & Extrapolation Tangent
    # -------------------------------------------------------------
    ax2.plot(energy, tauc_y, color='#0f766e', lw=2.0, label=r'Experimental $(\alpha h\nu)^{1/n}$')

    if "tangent_energy" in tauc_fit and len(tauc_fit["tangent_energy"]) > 0:
        ax2.plot(
            tauc_fit["tangent_energy"], tauc_fit["tangent_y"],
            color='crimson', lw=2.2, ls='--',
            label=f'Linear Extrapolation (R² = {tauc_fit["r2"]:.4f})'
        )

    if not np.isnan(eg):
        ax2.scatter([eg], [0.0], color='crimson', s=80, zorder=5, edgecolor='black', lw=1.2)
        ax2.axvline(eg, color='gray', ls=':', lw=1.0, alpha=0.7)

    # Notation
    eu_mev = urbach_fit.get("urbach_energy_mev", np.nan)
    eu_str = f"$E_U = {eu_mev:.1f}\\ \\mathbf{{meV}}$" if not np.isnan(eu_mev) else ""
    tauc_annotation = (
        f"$\\mathbf{{Bandgap\\ (E_g):\\ {eg:.3f}\\ eV}}$\n"
        f"$\\lambda_{{onset}} = {lam_onset:.1f}\\ \\mathbf{{nm}}$\n"
        f"Transition: {transition_label.split('(')[0].strip()}\n"
        f"{eu_str}"
    ).strip()

    ax2.text(
        0.06, 0.88, tauc_annotation, transform=ax2.transAxes,
        fontsize=font_size - 1, verticalalignment='top',
        bbox=dict(boxstyle='square,pad=0.5', facecolor='#f8fafc', edgecolor='#94a3b8', lw=1.2)
    )

    y_label_tex = r'$\mathbf{(\alpha h\nu)^2\ (cm^{-1}\cdot eV)^2}$' if "Direct Allowed" in transition_label else r'$\mathbf{(\alpha h\nu)^{1/n}\ (a.u.)}$'
    ax2.set_xlabel(r'$\mathbf{Photon\ Energy\ h\nu\ (eV)}$', fontweight='bold')
    ax2.set_ylabel(y_label_tex, fontweight='bold')
    
    finite_e = energy[np.isfinite(energy)]
    if len(finite_e) >= 2:
        e_lo = max(0.5, float(np.nanmin(finite_e)))
        e_hi = float(np.nanmax(finite_e))
        ax2.set_xlim(e_lo, e_hi)
    ax2.set_ylim(0, float(np.nanmax(tauc_y)) * 1.15)
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
