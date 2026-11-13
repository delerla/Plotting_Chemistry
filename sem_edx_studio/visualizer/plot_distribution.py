"""
sem_edx_studio.visualizer.plot_distribution
Publication-grade Figure Generator for Particle Size Distributions.
Plots Histogram + Log-Normal / Gaussian Fits, d10/d50/d90 percentiles, and PDI.
"""

from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
from sem_edx_studio.modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def render_size_distribution_plot(
    diameters_nm: np.ndarray,
    dist_stats: Dict[str, Any],
    theme: str = "ACS",
    font_size: int = 12,
    fig_size: Tuple[float, float] = (8.0, 5.5),
    dpi: int = 300
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Renders high-resolution publication size histogram with fitted Log-Normal and Gaussian models.
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

    fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)

    # Histogram normalized to density
    n_bins = max(10, min(30, int(len(diameters_nm) / 4)))
    counts, bins, _ = ax.hist(
        diameters_nm, bins=n_bins, density=True,
        color=primary_color, alpha=0.55, edgecolor="black", lw=1.2,
        label="Particle Counts"
    )

    # Log-Normal PDF
    if "x_dense" in dist_stats and "pdf_lognormal" in dist_stats:
        ax.plot(
            dist_stats["x_dense"], dist_stats["pdf_lognormal"],
            color="crimson", lw=2.2, ls="-",
            label=f"Log-Normal Fit ($d_{{50}} = {dist_stats['d50_nm']:.1f}\\ nm$)"
        )

    # Percentile lines
    ax.axvline(dist_stats["d50_nm"], color="crimson", ls="--", lw=1.5, alpha=0.85)

    stats_box = (
        f"$\\mathbf{{N = {dist_stats['count']}\\ particles}}$\n"
        f"Mean = {dist_stats['mean_nm']:.1f} ± {dist_stats['std_nm']:.1f} nm\n"
        f"Median ($d_{{50}}$) = {dist_stats['d50_nm']:.1f} nm\n"
        f"$d_{{10}}$ = {dist_stats['d10_nm']:.1f} nm | $d_{{90}}$ = {dist_stats['d90_nm']:.1f} nm\n"
        f"PDI = {dist_stats['pdi']:.3f}"
    )

    ax.text(
        0.60, 0.92, stats_box, transform=ax.transAxes,
        fontsize=font_size - 1, verticalalignment="top",
        bbox=dict(boxstyle="square,pad=0.5", facecolor="#f8fafc", edgecolor="#94a3b8", lw=1.2)
    )

    ax.set_xlabel(r"$\mathbf{Particle\ Diameter\ (nm)}$", fontweight="bold")
    ax.set_ylabel(r"$\mathbf{Probability\ Density}$", fontweight="bold")
    ax.minorticks_on()
    ax.tick_params(axis="both", which="both", direction="in", top=True, right=True)
    ax.legend(loc="upper left", framealpha=0.92)

    for spine in ax.spines.values():
        spine.set_linewidth(1.6)

    fig.tight_layout()
    return fig, ax
