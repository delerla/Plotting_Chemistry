"""
sem_edx_studio.tests.test_sem_edx_studio
Automated Verification Suite for SEM-EDX Studio:
- Benchmark Ingestion
- Computer Vision Micrograph Segmentation
- Particle Sizing & Log-Normal Statistical Modeling
- EDX Peak Matching & Elemental Quantification
- OriginLab Matrix (.dat) & Workbook (.xlsx) Generation
"""

import sys
from pathlib import Path

STUDIO_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = STUDIO_DIR.parent

for p in (str(STUDIO_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import pandas as pd

from sem_edx_studio.knowledge_base.benchmarks import (
    SEM_EDX_DOMAINS,
    generate_uio66_micrograph,
    generate_perovskite_grains_micrograph,
    generate_uio66_edx_spectrum,
    generate_mapbi3_edx_spectrum
)
from sem_edx_studio.core.segmentation import segment_micrograph
from sem_edx_studio.core.distribution import fit_size_distributions
from sem_edx_studio.core.edx_analysis import analyze_edx_spectrum
from sem_edx_studio.modules.export_utils import get_originlab_ascii_bytes, get_originlab_excel_bytes


def test_benchmarks():
    print("[TEST 1] Verifying Curated SEM-EDX Domain Benchmarks...")
    img_uio = generate_uio66_micrograph()
    assert img_uio.ndim == 2 and img_uio.shape[0] > 100
    
    img_perov = generate_perovskite_grains_micrograph()
    assert img_perov.shape == (600, 800)

    df_uio_edx = generate_uio66_edx_spectrum()
    assert "Energy_keV" in df_uio_edx.columns

    df_mapbi3_edx = generate_mapbi3_edx_spectrum()
    assert not df_mapbi3_edx.empty
    print("  --> PASS: All benchmark images and spectra generated successfully.")


def test_segmentation():
    print("[TEST 2] Verifying Computer Vision Micrograph Segmentation...")
    img = generate_uio66_micrograph()
    res = segment_micrograph(img, scale_nm_per_px=10.0, method="Otsu", min_area_px=15)
    assert res["n_particles"] > 10
    assert not res["df_particles"].empty
    assert "Diameter_nm" in res["df_particles"].columns
    print(f"  --> PASS: Segmented {res['n_particles']} particles (Mean diameter = {res['df_particles']['Diameter_nm'].mean():.1f} nm).")


def test_distribution():
    print("[TEST 3] Verifying Particle Size Distribution & Log-Normal Fitting...")
    # Synthetic log-normal particle diameters
    np.random.seed(42)
    d = np.random.lognormal(mean=5.5, sigma=0.25, size=200)  # ~244 nm
    res = fit_size_distributions(d)
    assert not np.isnan(res["mean_nm"])
    assert not np.isnan(res["d50_nm"])
    assert res["pdi"] > 0
    assert "geometric_mean_nm" in res["lognormal"]
    print(f"  --> PASS: Fitted Log-Normal d50 = {res['d50_nm']:.1f} nm, PDI = {res['pdi']:.3f}.")


def test_edx_analysis():
    print("[TEST 4] Verifying EDX Spectral Line Identification & Quantification...")
    df_edx = generate_uio66_edx_spectrum()
    res = analyze_edx_spectrum(df_edx, peak_prominence=60.0)
    assert not res["df_quant"].empty
    elems = res["df_quant"]["Element"].tolist()
    assert "C" in elems or "O" in elems or "Zr" in elems
    assert res["df_quant"]["Atomic_pct"].sum() > 95.0
    print(f"  --> PASS: Identified elements {elems} with total At% = {res['df_quant']['Atomic_pct'].sum():.1f}%.")


def test_originlab_exports():
    print("[TEST 5] Verifying OriginLab Matrix (.dat) & Workbook (.xlsx) Exporters...")
    dummy_df = pd.DataFrame({
        "Particle_ID": [1, 2, 3],
        "Diameter_nm": [210.5, 320.1, 280.4],
        "Aspect_Ratio": [1.12, 1.25, 1.05]
    })
    
    dat_bytes = get_originlab_ascii_bytes(dummy_df, title="SEM Particle Sizing")
    assert len(dat_bytes) > 50
    assert b"A(X)" in dat_bytes

    xlsx_bytes = get_originlab_excel_bytes(dummy_df, title="SEM Particle Sizing")
    assert len(xlsx_bytes) > 1000
    print("  --> PASS: OriginLab .dat and .xlsx generated cleanly.")


if __name__ == "__main__":
    print("\n========================================================")
    print(" RUNNING SEM-EDX STUDIO COMPREHENSIVE VERIFICATION SUITE")
    print("========================================================")
    test_benchmarks()
    test_segmentation()
    test_distribution()
    test_edx_analysis()
    test_originlab_exports()
    print("\n[ALL 5 SEM-EDX STUDIO TESTS PASSED SUCCESSFULLY!]\n")
