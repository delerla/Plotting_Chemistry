"""
sem_edx_studio.visualizer.plot_micrograph
Publication-grade Figure Generator for SEM Micrographs and Particle Segmentation Overlays.
"""

from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
from sem_edx_studio.modules.export_utils import set_publication_style


def render_micrograph_overlay_plot(
    raw_img: np.ndarray,
    overlay_rgb: np.ndarray,
    scale_nm_per_px: float = 1.0,
    font_size: int = 12,
    fig_size: Tuple[float, float] = (12.0, 5.5),
    dpi: int = 300
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    """
    Renders high-resolution 2-panel figure:
    (a) Raw Micrograph
    (b) Morphological Particle Boundary & Centroid Overlay
    """
    set_publication_style()
    plt.rcParams.update({
        'font.size': font_size,
        'axes.labelsize': font_size + 1
    })

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size, dpi=dpi)

    cmap = "gray" if raw_img.ndim == 2 else None
    ax1.imshow(raw_img, cmap=cmap)
    ax1.set_title(r"$\mathbf{(a)\ Raw\ SEM\ Micrograph}$", fontsize=font_size + 1)
    ax1.axis("off")

    # Draw scale bar on ax1 (e.g., 500 nm or 1 µm)
    h, w = raw_img.shape[:2]
    bar_nm = 500.0 if (w * scale_nm_per_px) > 800 else 200.0
    bar_px = bar_nm / scale_nm_per_px
    bar_x = w - bar_px - 30
    bar_y = h - 30
    ax1.plot([bar_x, bar_x + bar_px], [bar_y, bar_y], color="white", lw=4.5)
    ax1.text(
        bar_x + bar_px / 2.0, bar_y - 12,
        f"{bar_nm:.0f} nm",
        color="white", fontsize=font_size, fontweight="bold", ha="center"
    )

    ax2.imshow(overlay_rgb)
    ax2.set_title(r"$\mathbf{(b)\ Segmented\ Particles\ \&\ Centroids}$", fontsize=font_size + 1)
    ax2.axis("off")

    fig.tight_layout()
    return fig, (ax1, ax2)
