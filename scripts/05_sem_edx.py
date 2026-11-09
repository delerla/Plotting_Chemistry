"""
05_sem_edx.py - Automated SEM Particle Sizing & EDX Microanalysis Engine
"""

import sys
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import cv2
import pandas as pd
import matplotlib.pyplot as plt

from modules.export_utils import save_publication_figure, export_labplot_ascii
from modules.sem_edx_module import (
    analyze_sem_micrograph,
    analyze_edx_spectrum,
    generate_benchmark_sem_image,
    generate_benchmark_edx_data
)
SEM_FILE = BASE_DIR / "data" / "sem_edx" / "sem_micrograph.png"
EDX_FILE = BASE_DIR / "data" / "sem_edx" / "edx_spectrum.csv"
OUTPUT_DIR = BASE_DIR / "output" / "sem_edx"


def main():
    print("=" * 70)
    print(" [5/5] Running SEM & EDX Microanalysis Protocol")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # ----------------- Part A: SEM Image Analysis -----------------
    print("\n--- Part A: SEM Particle Segmentation & Sizing ---")
    if SEM_FILE.exists():
        print(f"[INFO] Loading SEM image from: {SEM_FILE}")
        sem_img = cv2.imread(str(SEM_FILE))
    else:
        print("[WARN] SEM image missing. Generating benchmark micrograph...")
        sem_img = generate_benchmark_sem_image()
        SEM_FILE.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(SEM_FILE), sem_img)

    fig_sem, stats_sem, df_particles = analyze_sem_micrograph(
        sem_img,
        scale_nm_per_pixel=2.5,
        min_area_px=25
    )

    print("[ANALYSIS] Particle Statistics:")
    print(f"  * Detected Count: {stats_sem['Total_Count']}")
    print(f"  * Mean Diameter: {stats_sem['Mean_Diameter_nm']} +/- {stats_sem['Std_Diameter_nm']} nm")
    print(f"  * Median (D50): {stats_sem['Median_Diameter_nm']} nm")
    print(f"  * D10: {stats_sem['D10_nm']} nm | D90: {stats_sem['D90_nm']} nm")

    # Export SEM graphics (600 DPI PNG, SVG, PDF)
    out_base_sem = OUTPUT_DIR / "SEM_Particle_Sizing_Publication"
    save_publication_figure(fig_sem, out_base_sem, dpi=600, formats=('png', 'svg', 'pdf'))

    # Export LabPlot ASCII matrix for particle measurements
    ascii_out_sem = OUTPUT_DIR / "SEM_Particle_Distribution_Matrix.dat"
    units_sem = {
        'Particle_ID': '#',
        'Area_px': 'px^2',
        'Diameter_nm': 'nm',
        'Circularity': 'dimensionless',
        'Centroid_Y': 'px',
        'Centroid_X': 'px'
    }
    export_labplot_ascii(
        df_particles,
        filepath=ascii_out_sem,
        title="SEM Particle Morphological Sizing and Area Distribution",
        units=units_sem,
        comments=[
            f"Total Particles: {stats_sem['Total_Count']}",
            f"Mean Diameter: {stats_sem['Mean_Diameter_nm']} nm, Std: {stats_sem['Std_Diameter_nm']} nm"
        ]
    )
    plt.close(fig_sem)

    # ----------------- Part B: EDX Microanalysis -----------------
    print("\n--- Part B: EDX Spectrum Elemental Quantification ---")
    if EDX_FILE.exists():
        print(f"[INFO] Loading EDX spectrum from: {EDX_FILE}")
        df_edx = pd.read_csv(EDX_FILE)
    else:
        print("[WARN] EDX spectrum missing. Generating benchmark spectrum...")
        df_edx = generate_benchmark_edx_data()
        EDX_FILE.parent.mkdir(parents=True, exist_ok=True)
        df_edx.to_csv(EDX_FILE, index=False)

    fig_edx, res_edx, labplot_edx = analyze_edx_spectrum(
        df_edx,
        prominence=80.0,
        peak_tolerance_keV=0.16
    )

    print("\n[QUANTIFICATION] Elemental Composition Table:")
    for row in res_edx['quantification']:
        safe_transition = str(row['Transition']).replace('α', '-alpha').replace('β', '-beta')
        print(f"  * {row['Element']:<3} ({safe_transition:<8}): Peak = {row['Peak_Energy_keV']} keV | Wt% = {row['Weight_Percent_wt']}% | At% = {row['Atomic_Percent_at']}%")

    # Export EDX graphics (600 DPI PNG, SVG, PDF)
    out_base_edx = OUTPUT_DIR / "EDX_Spectrum_Quantification_Publication"
    save_publication_figure(fig_edx, out_base_edx, dpi=600, formats=('png', 'svg', 'pdf'))

    # Export LabPlot ASCII matrix for EDX spectrum
    ascii_out_edx = OUTPUT_DIR / "EDX_Spectrum_Matrix.dat"
    export_labplot_ascii(
        labplot_edx,
        filepath=ascii_out_edx,
        title="Energy-Dispersive X-Ray Spectroscopy (EDX) Spectrum",
        units={'Energy_keV': 'keV', 'Counts': 'Counts'},
        comments=["Identified elements: " + ", ".join(f"{r['Element']} ({r['Weight_Percent_wt']} wt%)" for r in res_edx['quantification'])]
    )
    plt.close(fig_edx)

    print("\n[COMPLETED] SEM & EDX microanalysis finished successfully.\n")


if __name__ == '__main__':
    main()
