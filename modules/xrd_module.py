"""
xrd_module.py - X-Ray Diffraction (XRD) Profile Analysis and Scherrer Crystallite Sizing Engine
Supports: Background baseline stripping, Scherrer crystallite sizing, Normalization, and Themes.
"""

from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def lorentzian(x: np.ndarray, x0: float, gamma: float, a: float, c: float) -> np.ndarray:
    """Standard Lorentzian profile with baseline."""
    return a * (gamma**2 / ((x - x0)**2 + gamma**2)) + c


def scherrer_size(fwhm_deg: float, two_theta_deg: float, wavelength_nm: float = 0.15406, k: float = 0.9) -> float:
    """Computes crystallite size D (in nm) using the Scherrer equation."""
    theta_rad = np.radians(two_theta_deg / 2.0)
    beta_rad = np.radians(fwhm_deg)
    if beta_rad <= 0 or np.cos(theta_rad) <= 0:
        return 0.0
    return (k * wavelength_nm) / (beta_rad * np.cos(theta_rad))


def generate_benchmark_xrd_data() -> pd.DataFrame:
    """Generates benchmark multi-sample XRD pattern data."""
    two_theta = np.linspace(10, 80, 2000)
    
    def make_xrd(noise_level, peak_widths, seed=42):
        rng = np.random.default_rng(seed)
        y = rng.normal(50, noise_level, len(two_theta))
        peaks = [
            (17.0, peak_widths[0], 250),
            (25.5, peak_widths[1], 150),
            (43.2, 0.42, 420),
            (50.4, 0.48, 290),
            (74.1, 0.52, 170)
        ]
        for pos, fwhm, intensity in peaks:
            gamma = fwhm / 2.0
            y += intensity * (gamma**2 / ((two_theta - pos)**2 + gamma**2))
        return np.maximum(y, 0)
        
    patterns = {
        'TwoTheta': two_theta,
        'Pristine': make_xrd(2.0, [2.5, 3.0], seed=42),
        'P-NPs #1': make_xrd(2.5, [2.2, 2.8], seed=43),
        'P-NPs #2': make_xrd(3.0, [2.0, 2.5], seed=44)
    }
    return pd.DataFrame(patterns)


def process_and_plot_xrd(
    df: pd.DataFrame,
    offset_step: float = 500.0,
    fit_range: Tuple[float, float] = (41.5, 45.0),
    wavelength_nm: float = 0.15406,
    k_factor: float = 0.9,
    normalize_max: bool = False,
    theme: str = "ACS",
    fig_size: Tuple[float, float] = (8.0, 6.2)
) -> Tuple[plt.Figure, plt.Axes, Dict[str, Dict[str, float]], pd.DataFrame]:
    """
    Stacks XRD patterns, performs non-linear Lorentzian deconvolution on target Bragg reflection,
    calculates Scherrer crystallite size, and exports for publication and LabPlot.
    """
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES['ACS'])
    
    two_theta = df.iloc[:, 0].to_numpy().astype(float)
    sample_cols = list(df.columns[1:])
    
    fig, ax = plt.subplots(figsize=fig_size, dpi=300)
    current_offset = 0.0
    fit_results = {}
    labplot_dict = {'TwoTheta_deg': two_theta}
    
    for idx, name in enumerate(sample_cols):
        intensity = df[name].to_numpy().astype(float)
        
        # Optional normalization to max peak = 100%
        if normalize_max:
            i_max = np.max(intensity)
            if i_max > 0:
                intensity = (intensity / i_max) * 100.0
                
        y_shifted = intensity + current_offset
        
        labplot_dict[f"{name}_Raw"] = intensity
        labplot_dict[f"{name}_Stacked"] = y_shifted
        
        line_color = 'black' if theme == 'Monochrome' else palette[idx % len(palette)]
        ax.plot(two_theta, y_shifted, label=name, color=line_color, lw=1.6, zorder=3)
        
        # Deconvolution on specified Bragg peak window
        mask = (two_theta >= fit_range[0]) & (two_theta <= fit_range[1])
        x_sub = two_theta[mask]
        y_sub = intensity[mask]
        
        annotation_label = name
        if len(x_sub) > 5:
            try:
                peak_center_guess = x_sub[np.argmax(y_sub)]
                amp_guess = np.max(y_sub) - np.min(y_sub)
                p0 = [peak_center_guess, 0.3, amp_guess, np.min(y_sub)]
                popt, _ = curve_fit(lorentzian, x_sub, y_sub, p0=p0, maxfev=6000)
                
                center = float(popt[0])
                fwhm = float(abs(2 * popt[1]))
                d_crystallite = scherrer_size(fwhm, center, wavelength_nm=wavelength_nm, k=k_factor)
                
                fit_results[name] = {
                    'Peak_2Theta_deg': round(center, 3),
                    'FWHM_deg': round(fwhm, 4),
                    'FWHM_rad': round(np.radians(fwhm), 5),
                    'Crystallite_Size_nm': round(d_crystallite, 2)
                }
                annotation_label = f"{name} (D ≈ {d_crystallite:.1f} nm)"
                
                y_fit_shifted = lorentzian(x_sub, *popt) + current_offset
                ax.plot(x_sub, y_fit_shifted, color='crimson' if line_color != 'crimson' else '#ff7f0e', lw=1.8, ls='--', zorder=4)
            except Exception:
                fit_results[name] = {'Error': 'Fit did not converge'}
        
        ax.text(
            two_theta[-1] - 1.0, y_shifted[-1] + (15 if normalize_max else 45), annotation_label,
            ha='right', va='bottom', fontsize=11, fontweight='bold', color='#111111'
        )
        current_offset += (offset_step if not normalize_max else offset_step * 0.1)

    ax.set_xlim(two_theta.min(), two_theta.max())
    ax.set_xlabel(r'$\mathbf{2\theta\ (degrees)}$', fontsize=13, labelpad=8)
    ylabel = r'$\mathbf{Normalized\ Intensity\ (\%)}$' if normalize_max else r'$\mathbf{Intensity\ (a.u.)}$'
    ax.set_ylabel(ylabel, fontsize=13, labelpad=10)
    ax.set_yticks([])
    ax.minorticks_on()
    ax.tick_params(axis='x', which='both', top=True, direction='in', labelsize=11)
    ax.tick_params(axis='y', which='both', left=True, right=True, direction='in')

    for spine in ax.spines.values():
        spine.set_linewidth(1.6)

    fig.tight_layout()
    labplot_df = pd.DataFrame(labplot_dict)
    
    return fig, ax, fit_results, labplot_df
