"""
ftir_module.py - Fourier-Transform Infrared (FTIR) Processing, Stacking & Deconvolution Engine
Supports: Transmittance/Absorbance conversion, Baseline Zeroing, Normalization, and Journal Themes.
"""

from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def generate_benchmark_ftir_data() -> pd.DataFrame:
    """Generates benchmark multi-sample FTIR transmittance spectra."""
    wavenumbers = np.linspace(4000, 400, 2000)
    bands = {
        'Pristine Polymer': [(2246, 12, 18), (1453, 10, 16), (1362, 8, 12)],
        'Polymer + Ni NPs': [(3268, 80, 20), (2246, 12, 16), (1637, 25, 24), (1385, 20, 20), (1298, 18, 18)],
        'Polymer + Cu NPs': [(2246, 12, 16), (1607, 20, 22), (1454, 15, 18), (1309, 15, 15), (1071, 15, 15)],
        'Polymer + Co NPs': [(2246, 12, 16), (1637, 28, 25), (1391, 20, 22), (1311, 16, 18)],
    }
    
    data = {'Wavenumber': wavenumbers}
    np.random.seed(42)
    for name, p_list in bands.items():
        y = np.ones_like(wavenumbers) * 100.0 + np.random.normal(0, 0.2, len(wavenumbers))
        for center, width, depth in p_list:
            y -= depth * np.exp(-0.5 * ((wavenumbers - center) / width) ** 2)
        data[name] = np.clip(y, 10, 100)
        
    return pd.DataFrame(data)


def process_and_plot_ftir(
    df: pd.DataFrame,
    step_offset: float = 35.0,
    sg_window: int = 11,
    sg_poly: int = 2,
    prominence: float = 4.0,
    min_peak_wn: float = 600.0,
    max_peak_wn: float = 3600.0,
    mode: str = "Transmittance (%T)",
    normalization: str = "None",
    theme: str = "ACS",
    fig_size: Tuple[float, float] = (8.5, 7.0),
) -> Tuple[plt.Figure, plt.Axes, Dict[str, List[float]], pd.DataFrame]:
    """
    Advanced FTIR stacking with Savitzky-Golay filtering, mode toggling, normalization,
    and automatic vibrational peak annotation.
    """
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES['ACS'])
    
    x = df.iloc[:, 0].to_numpy().astype(float)
    # Ensure descending wavenumber order standard in vibrational spectroscopy
    if x[0] < x[-1]:
        sort_idx = np.argsort(x)[::-1]
        x = x[sort_idx]
        df_sorted = df.iloc[sort_idx].reset_index(drop=True)
    else:
        df_sorted = df.copy()

    sample_cols = list(df_sorted.columns[1:])
    
    if sg_window % 2 == 0:
        sg_window += 1
    sg_window = max(3, min(sg_window, len(x) - 1 if len(x) % 2 != 0 else len(x) - 2))

    fig, ax = plt.subplots(figsize=fig_size, dpi=300)
    labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)']
    
    current_offset = 0.0
    detected_peaks = {}
    labplot_dict = {'Wavenumber_cm-1': x}
    
    is_absorbance = "Absorbance" in mode

    for idx, name in enumerate(sample_cols):
        y_raw = df_sorted[name].to_numpy().astype(float)

        # Convert Transmittance to Absorbance if requested
        if is_absorbance:
            # A = -log10(T / 100) if T in %
            t_frac = np.clip(y_raw / 100.0, 1e-4, 1.0)
            y_proc = -np.log10(t_frac)
        else:
            y_proc = y_raw

        # Normalization
        if normalization == "Min-Max (0 to 1)":
            y_span = np.ptp(y_proc)
            if y_span > 0:
                y_proc = (y_proc - np.min(y_proc)) / y_span
        elif normalization == "Zero Baseline":
            y_proc = y_proc - np.min(y_proc)

        y_smooth = savgol_filter(y_proc, window_length=sg_window, polyorder=sg_poly)
        y_shifted = y_smooth + current_offset
        
        labplot_dict[f"{name}_Raw"] = y_raw
        labplot_dict[f"{name}_Processed"] = y_smooth
        labplot_dict[f"{name}_Stacked"] = y_shifted
        
        line_color = 'black' if theme == 'Monochrome' else palette[idx % len(palette)]
        ax.plot(x, y_shifted, color=line_color, lw=1.8, zorder=3, label=name)
        
        label_text = labels[idx] if idx < len(labels) else f'({idx+1})'
        target_idx = np.argmin(np.abs(x - 3900))
        y_label_pos = y_shifted[target_idx] + (1.5 if is_absorbance else 3.0)
        ax.text(3920, y_label_pos, f"{label_text} {name}", fontsize=12, fontweight='bold', va='bottom', ha='left')
        
        # Peak detection: in %T, peaks are absorption valleys; in Absorbance, they are peaks
        target_signal = y_smooth if is_absorbance else -y_smooth
        distance_pts = max(10, int(len(x) * (40 / (np.ptp(x) if np.ptp(x) > 0 else 3600))))
        prom_val = prominence * (0.05 if is_absorbance else 1.0)
        
        peaks, _ = find_peaks(target_signal, prominence=prom_val, distance=distance_pts)
        sample_peaks = []
        for p in peaks:
            peak_x = x[p]
            peak_y = y_shifted[p]
            if min_peak_wn <= peak_x <= max_peak_wn:
                sample_peaks.append(round(float(peak_x), 1))
                drop_len = 0.15 if is_absorbance else 6.0
                ax.plot([peak_x, peak_x], [peak_y, peak_y - drop_len], color='gray', lw=0.9, ls='--', zorder=2)
                ax.text(
                    peak_x, peak_y - drop_len * 1.3, f'{int(round(peak_x))}',
                    rotation=90, ha='center', va='top', fontsize=9, color='#333333', fontweight='semibold'
                )
        
        detected_peaks[name] = sample_peaks
        current_offset += step_offset

    ax.set_xlim(4000, 400)
    ax.set_xticks(np.arange(4000, 399, -600))
    ax.minorticks_on()
    ax.tick_params(axis='x', which='both', top=True, direction='in', pad=7, labelsize=11)
    ax.set_yticks([])
    ax.tick_params(axis='y', which='both', left=True, right=True, direction='in')

    ax.set_xlabel(r'$\mathbf{Wavenumber\ (cm^{-1})}$', fontsize=13, labelpad=8)
    ylabel = r'$\mathbf{Absorbance\ (a.u.)}$' if is_absorbance else r'$\mathbf{Transmittance\ (\%)}$'
    ax.set_ylabel(ylabel, fontsize=13, labelpad=12)

    for spine in ax.spines.values():
        spine.set_linewidth(1.6)

    fig.tight_layout()
    labplot_df = pd.DataFrame(labplot_dict)
    
    return fig, ax, detected_peaks, labplot_df
