"""
01_ftir.py - Automated FTIR Stack Plotting and LabPlot ASCII Export Engine
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

from modules.export_utils import save_publication_figure, export_labplot_ascii, export_originlab_ascii
from modules.file_parser import load_smart_file
from modules.ftir_module import process_and_plot_ftir, generate_benchmark_ftir_data
DEFAULT_DATA_FILE = BASE_DIR / "data" / "ftir" / "ftir_data.csv"
OUTPUT_DIR = BASE_DIR / "output" / "ftir"
ROOT_OUTPUT_FILE = BASE_DIR / "output" / "FTIR_Stacked_Publication.png"


def main():
    print("=" * 70)
    print(" [1/5] Running FTIR Spectroscopy Protocol")
    print("=" * 70)
    
    target_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA_FILE
    
    if target_file.exists():
        print(f"[INFO] Ingesting file via Smart Parser: {target_file}")
        df, _, meta = load_smart_file(target_file)
        if df is None or df.empty:
            print("[WARN] Parsing produced empty dataframe. Generating benchmark spectra...")
            df = generate_benchmark_ftir_data()
        else:
            print(f"[INFO] Successfully cleaned {meta['rows']} rows from {meta['format']}. Identified: {meta['detected_technique']}")
    else:
        print("[WARN] Data file missing. Generating benchmark spectra...")
        df = generate_benchmark_ftir_data()
        DEFAULT_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATA_FILE, index=False)

    fig, ax, detected_peaks, labplot_df = process_and_plot_ftir(
        df,
        step_offset=35.0,
        sg_window=11,
        sg_poly=2,
        prominence=4.0
    )

    print("\n[ANALYSIS] Detected Principal Bands (cm^-1):")
    for sample, peaks in detected_peaks.items():
        print(f"  * {sample}: {peaks}")

    # Export publication graphics (600 DPI PNG, SVG, PDF)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_base = OUTPUT_DIR / "FTIR_Stacked_Publication"
    saved_graphics = save_publication_figure(fig, out_base, dpi=600, formats=('png', 'svg', 'pdf'))
    
    # Also save to root output for backward compatibility
    fig.savefig(ROOT_OUTPUT_FILE, dpi=600, bbox_inches='tight')
    print(f"[EXPORT] Backward-compatible root image: {ROOT_OUTPUT_FILE}")

    # Export formatted ASCII matrix for LabPlot
    ascii_out = OUTPUT_DIR / "FTIR_Stacked_Matrix.dat"
    units = {'Wavenumber': 'cm^-1'}
    for col in labplot_df.columns[1:]:
        units[col] = '%' if 'Raw' in col or 'Smoothed' in col else 'offset a.u.'
        
    export_labplot_ascii(
        labplot_df,
        filepath=ascii_out,
        title="FTIR Stacked Spectra with Savitzky-Golay Filtering",
        units=units,
        comments=["Savitzky-Golay Window=11, Polyorder=2", "Stacked with discrete 35% offsets"]
    )

    # Export formatted ASCII matrix for OriginLab
    origin_out = OUTPUT_DIR / "FTIR_Stacked_OriginLab.dat"
    export_originlab_ascii(
        labplot_df,
        filepath=origin_out,
        title="FTIR Stacked Spectra with Savitzky-Golay Filtering",
        units=units,
        comments=["Savitzky-Golay Window=11, Polyorder=2", "Stacked with discrete 35% offsets"]
    )

    plt.close(fig)
    print("\n[COMPLETED] FTIR analysis finished successfully.\n")


if __name__ == '__main__':
    main()
