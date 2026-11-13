"""
test_hub.py - Comprehensive Unit & Integration Test Suite for Materials Characterization Hub.
Tests all 5 analytical protocols, universal smart parser, and export bundles.
"""

import sys
from pathlib import Path

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd

from modules.export_utils import (
    build_analysis_bundle_zip,
    export_labplot_ascii,
    export_originlab_ascii,
    get_originlab_ascii_bytes,
    get_originlab_excel_bytes
)
from modules.file_parser import load_smart_file
from modules.ftir_module import generate_benchmark_ftir_data, process_and_plot_ftir
from modules.xrd_module import generate_benchmark_xrd_data, process_and_plot_xrd, scherrer_size
from modules.uv_vis_module import generate_benchmark_uv_vis_data, process_and_plot_uv_vis
from modules.xps_module import calculate_shirley_baseline, deconvolve_xps, generate_benchmark_xps_data
from modules.sem_edx_module import (
    analyze_edx_spectrum,
    analyze_sem_micrograph,
    generate_benchmark_edx_data,
    generate_benchmark_sem_image
)


def test_file_parser_auto_detection():
    """Verifies that all analytical techniques are detected accurately."""
    df_ftir, _, meta_ftir = load_smart_file(BASE_DIR / 'data' / 'ftir' / 'ftir_data.csv')
    assert meta_ftir['detected_technique'] == '1. FTIR Spectroscopy'
    assert meta_ftir['confidence'] >= 0.85

    df_xrd, _, meta_xrd = load_smart_file(BASE_DIR / 'data' / 'xrd' / 'xrd_data.csv')
    assert meta_xrd['detected_technique'] == '2. XRD Crystallography'
    assert meta_xrd['confidence'] >= 0.85

    df_uv, _, meta_uv = load_smart_file(BASE_DIR / 'data' / 'uv_vis' / 'uv_vis_spectra.csv')
    assert meta_uv['detected_technique'] == '3. UV-Vis & Dye Kinetics'
    assert meta_uv['confidence'] >= 0.85

    df_xps, _, meta_xps = load_smart_file(BASE_DIR / 'data' / 'xps' / 'c1s_high_res.csv')
    assert meta_xps['detected_technique'] == '4. XPS Core Deconvolution'
    assert meta_xps['confidence'] >= 0.80

    df_edx, _, meta_edx = load_smart_file(BASE_DIR / 'data' / 'sem_edx' / 'edx_spectrum.csv')
    assert meta_edx['detected_technique'] == '5. SEM & EDX Microanalysis'

    _, img_sem, meta_sem = load_smart_file(BASE_DIR / 'data' / 'sem_edx' / 'sem_micrograph.png')
    assert 'SEM' in meta_sem['detected_technique']
    assert img_sem is not None


def test_ftir_pipeline():
    """Tests FTIR spectral stacking, Savitzky-Golay filtering, and peak detection."""
    df = generate_benchmark_ftir_data()
    fig, ax, peaks_dict, labplot_df = process_and_plot_ftir(df, step_offset=30.0, mode="Transmittance (%T)")
    assert fig is not None
    assert len(peaks_dict) == 4
    # Pristine polymer should show nitrile band at ~2246 cm^-1
    pristine_peaks = peaks_dict['Pristine Polymer']
    assert any(2240 <= p <= 2255 for p in pristine_peaks)
    assert 'Wavenumber_cm-1' in labplot_df.columns


def test_xrd_scherrer():
    """Tests Scherrer equation crystallite size formula and Lorentzian profile fitting."""
    d_size = scherrer_size(fwhm_deg=0.42, two_theta_deg=43.2, wavelength_nm=0.15406, k=0.9)
    assert 18.0 <= d_size <= 22.0

    df = generate_benchmark_xrd_data()
    fig, ax, fit_results, labplot_df = process_and_plot_xrd(df, offset_step=400.0)
    assert fig is not None
    assert 'Pristine' in fit_results
    assert fit_results['Pristine']['Crystallite_Size_nm'] > 15.0


def test_uv_vis_kinetics():
    """Tests multi-order photodegradation kinetics and model ranking."""
    df_spectra, _ = generate_benchmark_uv_vis_data()
    fig, axes, metrics, _, labplot_kinetics = process_and_plot_uv_vis(df_spectra, lambda_target=554.0)
    assert fig is not None
    assert metrics['lambda_max_nm'] == 554.0
    assert metrics['R2_pseudo_first_order'] > 0.98
    assert metrics['final_degradation_pct'] > 80.0
    assert 'ln_C0_Ct' in labplot_kinetics.columns


def test_xps_shirley_and_voigt():
    """Tests iterative Shirley background subtraction and multi-peak Voigt fit."""
    df = generate_benchmark_xps_data()
    fig, summary, labplot_df = deconvolve_xps(df, c1s_calibration=True)
    assert fig is not None
    assert summary['r_squared'] > 0.98
    assert len(summary['quantification_table']) == 4
    # Dominant peak should be C-C / C-H with > 50 at%
    cc_row = next(r for r in summary['quantification_table'] if 'C-C' in r['Component'])
    assert cc_row['Atomic_Concentration_pct'] > 50.0


def test_sem_edx_microanalysis():
    """Tests SEM particle segmentation, thresholding, and EDX line matching."""
    img = generate_benchmark_sem_image()
    fig_sem, stats_sem, df_particles = analyze_sem_micrograph(img, scale_nm_per_pixel=2.5)
    assert stats_sem['Total_Count'] > 30
    assert stats_sem['Mean_Diameter_nm'] > 20.0

    df_edx = generate_benchmark_edx_data()
    fig_edx, res_edx, labplot_edx = analyze_edx_spectrum(df_edx)
    elements = [r['Element'] for r in res_edx['quantification']]
    assert 'Si' in elements or 'Cu' in elements or 'Ni' in elements


def test_originlab_and_labplot_export():
    """Tests generation of OriginLab matrix (.dat & .xlsx), LabPlot matrix, and complete ZIP bundle."""
    import zipfile
    import io
    import tempfile
    df_ftir = generate_benchmark_ftir_data()
    fig, ax, peaks, labplot_df = process_and_plot_ftir(df_ftir)

    # 1. Test OriginLab ASCII bytes and structure
    units = {'Wavenumber_cm-1': 'cm^-1'}
    origin_bytes = get_originlab_ascii_bytes(labplot_df, title="FTIR Benchmark Matrix", units=units)
    assert len(origin_bytes) > 0
    origin_text = origin_bytes.decode('utf-8')
    assert "OriginLab Worksheet Data Matrix" in origin_text
    assert "A(X)" in origin_text
    assert "B(Y)" in origin_text

    # 2. Test round-trip ingestion of exported OriginLab file via load_smart_file
    with tempfile.NamedTemporaryFile(suffix='.dat', delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        export_originlab_ascii(labplot_df, tmp_path, title="FTIR Benchmark Matrix", units=units)
        df_reloaded, _, meta_reloaded = load_smart_file(tmp_path)
        assert df_reloaded is not None
        assert len(df_reloaded) == len(labplot_df)
        assert meta_reloaded['detected_technique'] == '1. FTIR Spectroscopy'
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    # 3. Test OriginLab Excel workbook generation
    excel_bytes = get_originlab_excel_bytes(labplot_df, title="FTIR Excel", units=units)
    assert len(excel_bytes) > 0

    # 4. Test complete publication package ZIP bundle contents
    zip_bytes = build_analysis_bundle_zip(
        fig,
        base_name="Test_FTIR",
        labplot_df=labplot_df,
        summary_data=pd.DataFrame([{'Sample': 'A', 'Peak': 2246}])
    )
    assert len(zip_bytes) > 1000
    assert zip_bytes[:2] == b'PK'  # ZIP magic bytes

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        namelist = zf.namelist()
        assert "Test_FTIR_OriginLab_Matrix.dat" in namelist
        assert "Test_FTIR_OriginLab.xlsx" in namelist
        assert "Test_FTIR_LabPlot_Matrix.dat" in namelist
        assert "Test_FTIR_600DPI.png" in namelist
        assert "Test_FTIR.svg" in namelist
        assert "Test_FTIR.pdf" in namelist


def test_ragged_csv_and_nan_tolerance():
    """Verifies that datasets with empty leading columns and trailing NaNs process without NaN/Inf axis errors."""
    ragged_csv = """,2θ - °,PAN-1,MOF-2,PAN+MOFs,PAN+ZnO
,10.00,4694.07,10192.08,6931.74,2881.87
,10.01,4713.22,10952.57,6905.07,2794.03
,10.02,4826.22,11853.08,6950.89,2788.33
,10.03,4978.23,12918.91,6971.01,2768.00
,,,,,1490.13
"""
    from modules.file_parser import parse_delimited_text
    df_clean = parse_delimited_text(ragged_csv)
    assert '2θ - °' in df_clean.columns[0]
    assert len(df_clean) == 4
    
    # Must plot cleanly without 'Axis limits cannot be NaN or Inf'
    fig, ax, fit_results, lp_df = process_and_plot_xrd(df_clean)
    assert fig is not None
    assert ax.get_xlim()[0] < ax.get_xlim()[1]


def test_community_feedback_and_reviews():
    from modules.feedback_module import get_reviews_file_path, load_reviews, add_review, save_all_reviews
    from knowledge_base.saudi_research_databank import search_saudi_databank
    
    fp = get_reviews_file_path()
    revs = load_reviews(fp)
    assert isinstance(revs, list), "Expected reviews store to be a list"
    
    # Test submission of a user review and subsequent retrieval
    sample_rev = {
        "id": "rev_test",
        "name": "Dr. Verification User",
        "role": "Scientist",
        "institution": "KFUPM",
        "rating": 5,
        "category": "Academic Review",
        "subject": "Platform test",
        "comment": "Verified submission test",
        "date": "2026-11-12",
        "wishes": "Keep the platform pure with real reviews"
    }
    assert add_review(sample_rev, fp)
    updated_revs = load_reviews(fp)
    assert any(r.get("id") == "rev_test" for r in updated_revs)
    
    # Clean up test review so platform remains completely fresh for real users
    save_all_reviews([], fp)
    assert len(load_reviews(fp)) == 0
    
    # Test databank search integration
    uio_matches = search_saudi_databank("UiO-66")
    assert len(uio_matches) >= 1, "UiO-66 search failed"


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("[RUNNING TEST SUITE]")
    test_file_parser_auto_detection()
    print("  [PASS] Smart Ingestion & Technique Auto-Detection")
    test_ftir_pipeline()
    print("  [PASS] FTIR Spectroscopy Engine")
    test_xrd_scherrer()
    print("  [PASS] XRD Crystallography & Scherrer Sizing")
    test_ragged_csv_and_nan_tolerance()
    print("  [PASS] Ragged CSV & NaN/Inf Immunity")
    test_uv_vis_kinetics()
    print("  [PASS] UV-Vis Photodegradation Kinetics")
    test_xps_shirley_and_voigt()
    print("  [PASS] XPS Shirley Baseline & Voigt Deconvolution")
    test_sem_edx_microanalysis()
    print("  [PASS] SEM Particle Sizing & EDX Microanalysis")
    test_originlab_and_labplot_export()
    print("  [PASS] ZIP Package, OriginLab Matrix (.dat & .xlsx) & LabPlot ASCII Bundling")
    test_community_feedback_and_reviews()
    print("  [PASS] Community Reviews, Wishes & Search Databank Integration")
    print("\n[ALL 9 TESTS PASSED SUCCESSFULLY!]")
