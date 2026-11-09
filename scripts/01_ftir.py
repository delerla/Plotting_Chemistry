from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter

# Publication style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 13,
    'axes.linewidth': 1.6,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.size': 7,
    'xtick.major.width': 1.5,
    'xtick.minor.size': 4,
    'xtick.minor.width': 1.0,
    'ytick.major.size': 7,
    'ytick.major.width': 1.5,
    'lines.linewidth': 1.6,
})

BASE_DIR = Path(r"D:\Plotting_Chemistry")
DATA_FILE = BASE_DIR / "data" / "ftir" / "ftir_data.csv"
OUTPUT_FILE = BASE_DIR / "output" / "FTIR_Stacked_Publication.png"

def load_or_generate_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        x = df.iloc[:, 0].to_numpy()
        spectra = {col: df[col].to_numpy() for col in df.columns[1:]}
    else:
        print("[INFO] No CSV found in data/ftir. Generating benchmark spectra...")
        x = np.linspace(4000, 400, 2000)
        bands = {
            'Pristine P': [(2246, 12, 18), (1453, 10, 16), (1362, 8, 12)],
            'P+Ni': [(3268, 80, 20), (2246, 12, 16), (1637, 25, 24), (1385, 20, 20), (1298, 18, 18)],
            'P+Cu': [(2246, 12, 16), (1607, 20, 22), (1454, 15, 18), (1309, 15, 15), (1071, 15, 15)],
            'P+Co': [(2246, 12, 16), (1637, 28, 25), (1391, 20, 22), (1311, 16, 18)],
        }
        spectra = {}
        for name, p_list in bands.items():
            y = np.ones_like(x) * 100.0 + np.random.normal(0, 0.2, len(x))
            for center, width, depth in p_list:
                y -= depth * np.exp(-0.5 * ((x - center) / width) ** 2)
            spectra[name] = y
    return x, spectra

def main():
    x, spectra = load_or_generate_data()
    fig, ax = plt.subplots(figsize=(8.5, 6.8), dpi=300)
    
    labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']
    step_offset = 35.0
    current_offset = 0.0

    for idx, (name, y_raw) in enumerate(spectra.items()):
        y_smooth = savgol_filter(y_raw, window_length=11, polyorder=2)
        y_shifted = y_smooth + current_offset
        ax.plot(x, y_shifted, color='black', zorder=3)

        label_text = labels[idx] if idx < len(labels) else f'({idx+1})'
        y_label_pos = y_shifted[np.argmin(np.abs(x - 3900))] + 3
        ax.text(3920, y_label_pos, label_text, fontsize=15, fontweight='bold', va='bottom', ha='left')

        # Auto peak detection
        peaks, _ = find_peaks(-y_smooth, prominence=4.0, distance=int(len(x) * (40 / (x.max() - x.min()))))
        for p in peaks:
            peak_x = x[p]
            peak_y = y_shifted[p]
            if 600 <= peak_x <= 3600:
                ax.plot([peak_x, peak_x], [peak_y, peak_y - 6], color='gray', lw=0.8, ls='--', zorder=2)
                ax.text(peak_x, peak_y - 8, f'{int(round(peak_x))}', rotation=90, ha='center', va='top', fontsize=9, color='dimgray')

        current_offset += step_offset

    ax.set_xlim(4000, 400)
    ax.set_xticks(np.arange(4000, 399, -600))
    ax.minorticks_on()
    ax.tick_params(axis='x', which='both', top=True, direction='in', pad=7, labelsize=12)
    ax.set_yticks([])
    ax.tick_params(axis='y', which='both', left=True, right=True, direction='in')

    ax.set_xlabel(r'$\mathbf{Wavenumber\ (cm^{-1})}$', fontsize=14, labelpad=8)
    ax.set_ylabel(r'$\mathbf{Transmittance\ (\%)}$', fontsize=14, labelpad=12)

    for spine in ax.spines.values():
        spine.set_linewidth(1.6)

    plt.tight_layout()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE, dpi=600, bbox_inches='tight')
    print(f'[SUCCESS] Saved: {OUTPUT_FILE}')
    plt.close(fig)

if __name__ == '__main__':
    main()
