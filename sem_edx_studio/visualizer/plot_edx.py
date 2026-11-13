"""
sem_edx_studio.visualizer.plot_edx
Publication-grade Figure Generator for EDX Energy Spectra and Elemental Quantification.
"""

from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sem_edx_studio.modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def render_edx_publication_plot(
    edx_results: Dict[str, Any],
    theme: str = "ACS",
    font_size: int = 12,
    fig_size: Tuple[float, float] = (12.0, 5.5),
    dpi: int = 300
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    """
    Renders high-resolution 2-panel figure:
    (a) EDX Energy Spectrum with Characteristic Line Identification
    (b) Quantified Elemental Composition (Atomic % and Weight %)
    """
    set_publication_style()
    plt.rcParams.update({
        'font.size': font_size,
        'axes.labelsize': font_size + 1,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'legend.fontsize': font_size - 2
    })

    energy = edx_results["energy"]
    counts = edx_results["counts"]
    bg = edx_results["background"]
    df_quant = edx_results["df_quant"]
    detected = edx_results["detected_peaks"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size, dpi=dpi)

    # -------------------------------------------------------------
    # Panel (a): EDX Spectrum
    # -------------------------------------------------------------
    ax1.plot(energy, counts, color="#0f172a", lw=1.5, label="Raw EDX Spectrum")
    ax1.plot(energy, bg, color="gray", ls=":", lw=1.2, label="Bremsstrahlung Background")

    # Mark detected peaks
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    for idx, pk in enumerate(detected):
        c = palette[idx % len(palette)]
        ax1.axvline(pk["Peak_Energy_keV"], color=c, ls="--", lw=1.2, alpha=0.7)
        ax1.text(
            pk["Peak_Energy_keV"], pk["Peak_Counts"] * 1.05,
            pk["Line"],
            rotation=90, verticalalignment="bottom", horizontalalignment="center",
            fontsize=font_size - 2, fontweight="bold", color=c
        )

    ax1.set_xlabel(r"$\mathbf{X-Ray\ Energy\ (keV)}$", fontweight="bold")
    ax1.set_ylabel(r"$\mathbf{Counts}$", fontweight="bold")
    ax1.set_xlim(0.0, float(np.nanmax(energy)))
    ax1.set_ylim(0.0, float(np.nanmax(counts)) * 1.35)
    ax1.minorticks_on()
    ax1.tick_params(axis="both", which="both", direction="in", top=True, right=True)
    ax1.legend(loc="upper right", framealpha=0.92)
    ax1.text(0.04, 0.93, "(a)", transform=ax1.transAxes, fontsize=font_size + 3, fontweight="bold")

    # -------------------------------------------------------------
    # Panel (b): Composition Bar Chart
    # -------------------------------------------------------------
    if not df_quant.empty:
        elems = df_quant["Element"].tolist()
        at_pct = df_quant["Atomic_pct"].tolist()
        wt_pct = df_quant["Weight_pct"].tolist()

        x = np.arange(len(elems))
        width = 0.35

        bar1 = ax2.bar(x - width/2, at_pct, width, label="Atomic %", color=palette[0], edgecolor="black", lw=1.0)
        bar2 = ax2.bar(x + width/2, wt_pct, width, label="Weight %", color=palette[1] if len(palette) > 1 else "coral", edgecolor="black", lw=1.0)

        # Bar value labels
        for b in bar1:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width()/2., h + 1.0, f"{h:.1f}%", ha='center', va='bottom', fontsize=font_size - 2, fontweight='bold')
        for b in bar2:
            h = b.get_height()
            ax2.text(b.get_x() + b.get_width()/2., h + 1.0, f"{h:.1f}%", ha='center', va='bottom', fontsize=font_size - 2)

        ax2.set_xlabel(r"$\mathbf{Identified\ Element}$", fontweight="bold")
        ax2.set_ylabel(r"$\mathbf{Concentration\ (\%)}$", fontweight="bold")
        ax2.set_xticks(x)
        ax2.set_xticklabels(elems, fontweight="bold")
        ax2.set_ylim(0, max(max(at_pct), max(wt_pct)) * 1.25)
        ax2.legend(loc="upper right", framealpha=0.92)
    else:
        ax2.text(0.5, 0.5, "No elemental peaks matched above threshold", ha="center", va="center")

    ax2.text(0.04, 0.93, "(b)", transform=ax2.transAxes, fontsize=font_size + 3, fontweight="bold")

    for ax in (ax1, ax2):
        for spine in ax.spines.values():
            spine.set_linewidth(1.6)

    fig.tight_layout()
    return fig, (ax1, ax2)
