"""
02_xrd.py - Automated XRD Pattern Analysis, Scherrer Sizing, and LabPlot ASCII Export Engine
"""

import sys
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import matplotlib.pyplot as plt

from modules.export_utils import save_publication_figure, export_labplot_ascii
from modules.xrd_module import process_and_plot_xrd, generate_benchmark_xrd_data
DATA_FILE = BASE_DIR / "data" / "xrd" / "xrd_data.csv"
OUTPUT_DIR = BASE_DIR / "output" / "xrd"
ROOT_OUTPUT_FILE = BASE_DIR / "output" / "XRD_Stacked_Publication.png"


def main():
    print("=" * 70)
    print(" [2/5] Running XRD Crystallography Protocol")
    print("=" * 70)
    
    if DATA_FILE.exists():
        print(f"[INFO] Loading experimental data from: {DATA_FILE}")
        df = pd.read_csv(DATA_FILE)
    else:
        print("[WARN] Data file missing. Generating benchmark XRD patterns...")
        df = generate_benchmark_xrd_data()
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATA_FILE, index=False)

    fig, ax, fit_results, labplot_df = process_and_plot_xrd(
        df,
        offset_step=500.0,
        fit_range=(41.5, 45.0),
        wavelength_nm=0.15406,
        k_factor=0.9
    )

    print("\n[ANALYSIS] Scherrer Crystallite Size Deconvolution:")
    for sample, stats in fit_results.items():
        if 'Error' in stats:
            print(f"  * {sample}: {stats['Error']}")
        else:
            print(f"  * {sample}: 2-Theta = {stats['Peak_2Theta_deg']} deg, FWHM = {stats['FWHM_deg']} deg, D = {stats['Crystallite_Size_nm']} nm")

    # Export publication graphics (600 DPI PNG, SVG, PDF)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_base = OUTPUT_DIR / "XRD_Stacked_Publication"
    save_publication_figure(fig, out_base, dpi=600, formats=('png', 'svg', 'pdf'))
    
    # Root backward compatibility
    fig.savefig(ROOT_OUTPUT_FILE, dpi=600, bbox_inches='tight')
    print(f"[EXPORT] Backward-compatible root image: {ROOT_OUTPUT_FILE}")

    # Export LabPlot ASCII matrix
    ascii_out = OUTPUT_DIR / "XRD_Stacked_Matrix.dat"
    units = {'TwoTheta_deg': 'degrees'}
    for col in labplot_df.columns[1:]:
        units[col] = 'Counts'
        
    export_labplot_ascii(
        labplot_df,
        filepath=ascii_out,
        title="XRD Diffraction Stacked Patterns with Scherrer Analysis",
        units=units,
        comments=["Cu K-alpha radiation (lambda = 0.15406 nm)", "K = 0.9 shape factor"]
    )

    plt.close(fig)
    print("\n[COMPLETED] XRD analysis finished successfully.\n")


if __name__ == '__main__':
    main()
