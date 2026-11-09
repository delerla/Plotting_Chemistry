"""
sem_edx_module.py - SEM Micrograph Particle Sizing & EDX Spectral Quantification Engine
"""

from typing import Dict, List, Optional, Tuple
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import seaborn as sns
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.morphology import closing, disk, remove_small_objects

from modules.export_utils import set_publication_style


# Characteristic X-ray emission lines (in keV)
CHARACTERISTIC_LINES = {
    'C Kα': 0.277,
    'N Kα': 0.392,
    'O Kα': 0.525,
    'Na Kα': 1.041,
    'Mg Kα': 1.253,
    'Al Kα': 1.486,
    'Si Kα': 1.739,
    'P Kα': 2.013,
    'S Kα': 2.307,
    'Cl Kα': 2.621,
    'Ti Kα': 4.510,
    'Cr Kα': 5.411,
    'Fe Kα': 6.398,
    'Co Kα': 6.924,
    'Ni Kα': 7.471,
    'Cu Kα': 8.040,
    'Zn Kα': 8.630,
}

ATOMIC_WEIGHTS = {
    'C': 12.011,
    'N': 14.007,
    'O': 15.999,
    'Na': 22.990,
    'Mg': 24.305,
    'Al': 26.982,
    'Si': 28.085,
    'P': 30.974,
    'S': 32.065,
    'Cl': 35.453,
    'Ti': 47.867,
    'Cr': 51.996,
    'Fe': 55.845,
    'Co': 58.933,
    'Ni': 58.693,
    'Cu': 63.546,
    'Zn': 65.380,
}


def generate_benchmark_sem_image(width: int = 800, height: int = 600, n_particles: int = 120) -> np.ndarray:
    """Generates a realistic synthetic SEM micrograph with nanoparticles."""
    np.random.seed(42)
    # Background with slight gradient and texture
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    bg = 50 + 20 * xx + 15 * yy + np.random.normal(0, 8, (height, width))
    img = np.clip(bg, 0, 255).astype(np.uint8)

    # Place particles (bright spheres with gaussian intensity)
    radii = np.random.lognormal(mean=2.6, sigma=0.35, size=n_particles)
    radii = np.clip(radii, 8, 38).astype(int)

    for r in radii:
        cx = np.random.randint(r + 5, width - r - 5)
        cy = np.random.randint(r + 5, height - r - 5)
        
        y_coords, x_coords = np.ogrid[:height, :width]
        dist_sq = (x_coords - cx) ** 2 + (y_coords - cy) ** 2
        mask = dist_sq <= r ** 2
        intensity = 180 + np.random.randint(-20, 20) - 80 * (dist_sq / (r**2 + 1e-5))
        img[mask] = np.clip(np.maximum(img[mask], intensity[mask]), 0, 255)

    # Blur slightly for SEM electron scatter look
    img = cv2.GaussianBlur(img, (3, 3), 0.8)
    return img


def generate_benchmark_edx_data() -> pd.DataFrame:
    """
    Generates synthetic benchmark EDX spectrum of a metal-oxide / catalyst nanocomposite:
    Contains C (0.28 keV), O (0.52 keV), Si (1.74 keV), Ni (7.47 keV), Cu (8.04 keV).
    """
    energy = np.linspace(0.1, 10.0, 2000)
    
    # Bremsstrahlung continuous X-ray background
    bg = 350.0 * np.exp(-0.45 * energy) + 30.0 / (energy + 0.2)
    
    # Characteristic lines (energy, fwhm_keV, intensity)
    peaks = [
        (0.277, 0.08, 1200),  # C Kα
        (0.525, 0.09, 3400),  # O Kα
        (1.739, 0.11, 4800),  # Si Kα
        (7.471, 0.14, 2600),  # Ni Kα
        (8.040, 0.15, 3900),  # Cu Kα
    ]
    
    y = bg.copy()
    for pos, fwhm, amp in peaks:
        sigma = fwhm / 2.355
        y += amp * np.exp(-0.5 * ((energy - pos) / sigma) ** 2)
        
    np.random.seed(42)
    y += np.random.normal(0, 18, len(energy))
    y = np.clip(y, 0, None)
    
    return pd.DataFrame({
        'Energy_keV': energy,
        'Counts': y
    })


def analyze_sem_micrograph(
    img: np.ndarray,
    scale_nm_per_pixel: float = 2.5,
    min_area_px: int = 25,
    fig_size: Tuple[float, float] = (12.0, 5.5)
) -> Tuple[plt.Figure, Dict[str, any], pd.DataFrame]:
    """
    Performs automated particle segmentation, thresholding, and size distribution analysis on SEM image.
    Returns:
        fig, summary_stats, particle_measurements_df
    """
    set_publication_style()
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # Preprocessing: bilateral filter / gaussian filter to preserve edges
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
    thresh_val = threshold_otsu(blurred)
    binary = blurred > thresh_val
    
    # Morphological cleanup
    cleaned = closing(binary, disk(2))
    cleaned = remove_small_objects(cleaned, min_size=min_area_px)
    
    # Label connected components
    labeled_img = label(cleaned)
    regions = regionprops(labeled_img)
    
    particles_data = []
    annotated_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    for idx, prop in enumerate(regions):
        area_px = prop.area
        if area_px < min_area_px:
            continue
            
        d_eq_px = 2.0 * np.sqrt(area_px / np.pi)
        d_eq_nm = d_eq_px * scale_nm_per_pixel
        perimeter_px = prop.perimeter
        circularity = 4 * np.pi * area_px / (perimeter_px ** 2 + 1e-6)
        
        particles_data.append({
            'Particle_ID': idx + 1,
            'Area_px': area_px,
            'Diameter_nm': round(d_eq_nm, 2),
            'Circularity': round(min(circularity, 1.0), 3),
            'Centroid_Y': int(prop.centroid[0]),
            'Centroid_X': int(prop.centroid[1]),
        })
        
        # Draw bounding circle/contour on annotated image
        cy, cx = int(prop.centroid[0]), int(prop.centroid[1])
        cv2.circle(annotated_img, (cx, cy), int(d_eq_px / 2.0), (255, 60, 60), 2)

    df_particles = pd.DataFrame(particles_data)
    diameters = df_particles['Diameter_nm'].to_numpy() if len(df_particles) > 0 else np.array([0.0])
    
    stats = {
        'Total_Count': len(df_particles),
        'Mean_Diameter_nm': round(float(np.mean(diameters)), 2),
        'Std_Diameter_nm': round(float(np.std(diameters)), 2),
        'Median_Diameter_nm': round(float(np.median(diameters)), 2),
        'D10_nm': round(float(np.percentile(diameters, 10)), 2),
        'D50_nm': round(float(np.percentile(diameters, 50)), 2),
        'D90_nm': round(float(np.percentile(diameters, 90)), 2),
    }

    # Plot Dual-Panel Publication Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size, dpi=300)
    
    # Left: Segmented image
    ax1.imshow(annotated_img)
    ax1.set_title(r'$\mathbf{(a)\ Segmented\ Micrograph\ with\ Overlays}$', fontsize=12, pad=10)
    ax1.axis('off')
    
    # Right: Particle size distribution histogram
    sns.histplot(diameters, kde=True, ax=ax2, color='#1f77b4', edgecolor='black', bins=18, stat='density', alpha=0.6)
    ax2.set_title(r'$\mathbf{(b)\ Particle\ Size\ Distribution}$', fontsize=12, pad=10)
    ax2.set_xlabel(r'$\mathbf{Equivalent\ Spherical\ Diameter\ (nm)}$', fontsize=12)
    ax2.set_ylabel(r'$\mathbf{Probability\ Density}$', fontsize=12)
    ax2.minorticks_on()
    ax2.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    
    stat_box = (
        f"Count = {stats['Total_Count']}\n"
        f"Mean = {stats['Mean_Diameter_nm']:.1f} ± {stats['Std_Diameter_nm']:.1f} nm\n"
        f"Median = {stats['Median_Diameter_nm']:.1f} nm\n"
        f"D10 = {stats['D10_nm']:.1f} nm\n"
        f"D90 = {stats['D90_nm']:.1f} nm"
    )
    ax2.text(
        0.95, 0.95, stat_box, transform=ax2.transAxes,
        fontsize=10, va='top', ha='right',
        bbox=dict(boxstyle='square,pad=0.5', facecolor='#f7f7f7', edgecolor='#b0b0b0', lw=1.2)
    )
    
    for spine in ax2.spines.values():
        spine.set_linewidth(1.6)

    fig.tight_layout()
    return fig, stats, df_particles


def analyze_edx_spectrum(
    df: pd.DataFrame,
    prominence: float = 80.0,
    peak_tolerance_keV: float = 0.16,
    fig_size: Tuple[float, float] = (9.5, 6.0)
) -> Tuple[plt.Figure, Dict[str, any], pd.DataFrame]:
    """
    Performs peak detection, characteristic line identification, and semi-quantitative elemental wt%/at% estimation.
    Returns:
        fig, quantification_dict, labplot_df
    """
    set_publication_style()
    energy = df.iloc[:, 0].to_numpy().astype(float)
    counts = df.iloc[:, 1].to_numpy().astype(float)
    
    peaks, props = find_peaks(counts, prominence=prominence, distance=20)
    
    matched_elements = []
    used_labels = set()
    
    for p in peaks:
        p_energy = energy[p]
        p_count = counts[p]
        
        # Find best characteristic line match
        best_diff = peak_tolerance_keV
        best_match = None
        for name, line_keV in CHARACTERISTIC_LINES.items():
            diff = abs(p_energy - line_keV)
            if diff < best_diff and name not in used_labels:
                best_diff = diff
                best_match = name
                
        if best_match:
            used_labels.add(best_match)
            elem_sym = best_match.split()[0]
            matched_elements.append({
                'Peak_Index': p,
                'Identified_Line': best_match,
                'Element': elem_sym,
                'Energy_keV': round(float(p_energy), 3),
                'Theoretical_keV': round(CHARACTERISTIC_LINES[best_match], 3),
                'Net_Intensity': round(float(props['prominences'][np.where(peaks == p)[0][0]]), 1)
            })

    # Semi-quantitative estimation
    total_net = sum(item['Net_Intensity'] for item in matched_elements) if matched_elements else 1.0
    quant_table = []
    
    # Calculate weight percentages (proportional to net intensity) and atomic percentages
    sum_molar = 0.0
    for item in matched_elements:
        elem = item['Element']
        wt_pct = (item['Net_Intensity'] / total_net) * 100.0
        m_weight = ATOMIC_WEIGHTS.get(elem, 28.0)
        moles = wt_pct / m_weight
        sum_molar += moles
        item['wt_pct'] = wt_pct
        item['moles'] = moles

    for item in matched_elements:
        at_pct = (item['moles'] / sum_molar * 100.0) if sum_molar > 0 else 0.0
        quant_table.append({
            'Element': item['Element'],
            'Transition': item['Identified_Line'],
            'Peak_Energy_keV': item['Energy_keV'],
            'Weight_Percent_wt': round(item['wt_pct'], 2),
            'Atomic_Percent_at': round(at_pct, 2)
        })

    # Plot EDX Spectrum
    fig, ax = plt.subplots(figsize=fig_size, dpi=300)
    ax.plot(energy, counts, color='#1f77b4', lw=1.6, label='EDX Signal')
    ax.fill_between(energy, 0, counts, color='#1f77b4', alpha=0.15)
    
    # Annotate identified peaks
    for item in matched_elements:
        px = item['Energy_keV']
        py = counts[item['Peak_Index']]
        ax.plot([px, px], [py, py + max(counts) * 0.08], color='crimson', lw=1.2, ls='--')
        ax.text(
            px, py + max(counts) * 0.09,
            f"{item['Identified_Line']}\n({px:.2f} keV)",
            ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='crimson'
        )

    ax.set_xlim(energy.min(), energy.max())
    ax.set_ylim(0, max(counts) * 1.25)
    ax.set_xlabel(r'$\mathbf{Energy\ (keV)}$', fontsize=13, labelpad=8)
    ax.set_ylabel(r'$\mathbf{Intensity\ (Counts)}$', fontsize=13, labelpad=10)
    ax.minorticks_on()
    ax.tick_params(axis='both', which='both', direction='in', top=True, right=True)
    
    for spine in ax.spines.values():
        spine.set_linewidth(1.6)

    fig.tight_layout()
    
    quant_df = pd.DataFrame(quant_table)
    labplot_df = pd.DataFrame({
        'Energy_keV': energy,
        'Counts': counts
    })
    
    return fig, {'quantification': quant_table}, labplot_df
