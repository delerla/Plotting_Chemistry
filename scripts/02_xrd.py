from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

BASE_DIR = Path(r"D:\Plotting_Chemistry")
DATA_FILE = BASE_DIR / "data" / "xrd" / "xrd_data.csv"
OUTPUT_FILE = BASE_DIR / "output" / "XRD_Stacked_Publication.png"

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
})

def lorentzian(x, x0, gamma, a, c):
    return a * (gamma**2 / ((x - x0)**2 + gamma**2)) + c

def scherrer_size(fwhm_deg, two_theta_deg, wavelength_nm=0.15406, k=0.9):
    theta_rad = np.radians(two_theta_deg / 2.0)
    beta_rad = np.radians(fwhm_deg)
    d_nm = (k * wavelength_nm) / (beta_rad * np.cos(theta_rad))
    return d_nm

def load_or_generate_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        two_theta = df.iloc[:, 0].to_numpy()
        patterns = {col: df[col].to_numpy() for col in df.columns[1:]}
    else:
        print("[INFO] No CSV found in data/xrd. Generating benchmark XRD spectra...")
        two_theta = np.linspace(10, 80, 2000)
        # Synthetic polymer and nanoparticle diffraction peaks
        def make_xrd(noise_level, peak_widths):
            y = np.random.normal(50, noise_level, len(two_theta))
            peaks = [(17.0, peak_widths[0], 250), (25.5, peak_widths[1], 150), (43.2, 0.4, 400), (50.4, 0.45, 300), (74.1, 0.5, 180)]
            for pos, fwhm, intensity in peaks:
                gamma = fwhm / 2.0
                y += intensity * (gamma**2 / ((two_theta - pos)**2 + gamma**2))
            return y
        patterns = {
            'Pristine': make_xrd(2.0, [2.5, 3.0]),
            'P-NPs #1': make_xrd(2.5, [2.2, 2.8]),
            'P-NPs #2': make_xrd(3.0, [2.0, 2.5])
        }
    return two_theta, patterns

def main():
    two_theta, patterns = load_or_generate_data()
    fig, ax = plt.subplots(figsize=(8.0, 6.0), dpi=300)

    offset_step = 500.0
    current_offset = 0.0
    colors = ['#1f77b4', '#d62728', '#2ca02c']

    for idx, (name, intensity) in enumerate(patterns.items()):
        y_shifted = intensity + current_offset
        c = colors[idx % len(colors)]
        ax.plot(two_theta, y_shifted, label=name, color='black', lw=1.5)
        
        # Calculate crystallite size on primary crystalline peak around 43.2 deg
        mask = (two_theta >= 41.5) & (two_theta <= 45.0)
        x_sub = two_theta[mask]
        y_sub = intensity[mask]
        try:
            p0 = [43.2, 0.3, np.max(y_sub) - np.min(y_sub), np.min(y_sub)]
            popt, _ = curve_fit(lorentzian, x_sub, y_sub, p0=p0, maxfev=5000)
            fwhm = 2 * popt[1]
            d_crystallite = scherrer_size(fwhm, popt[0])
            ax.text(two_theta[-1] - 1, y_shifted[-1] + 40, f"{name} (D ≈ {d_crystallite:.1f} nm)", 
                    ha='right', va='bottom', fontsize=11, fontweight='bold')
        except Exception:
            ax.text(two_theta[-1] - 1, y_shifted[-1] + 40, name, ha='right', va='bottom', fontsize=11, fontweight='bold')

        current_offset += offset_step

    ax.set_xlim(10, 80)
    ax.set_xlabel(r'$\mathbf{2\theta\ (degrees)}$', fontsize=14, labelpad=8)
    ax.set_ylabel(r'$\mathbf{Intensity\ (a.u.)}$', fontsize=14, labelpad=10)
    ax.set_yticks([])
    ax.minorticks_on()
    ax.tick_params(axis='x', which='both', top=True, direction='in')
    ax.tick_params(axis='y', which='both', left=True, right=True, direction='in')

    for spine in ax.spines.values():
        spine.set_linewidth(1.6)

    plt.tight_layout()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FILE, dpi=600, bbox_inches='tight')
    print(f'[SUCCESS] Saved: {OUTPUT_FILE}')
    plt.close(fig)

if __name__ == '__main__':
    main()
