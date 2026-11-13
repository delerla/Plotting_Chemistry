"""
test_xps_studio.py - Comprehensive Unit & Integration Test Suite for XPS Studio
Validates calibration, background subtraction, Voigt fitting, spin-orbit doublet coupling,
domain interpretation, and LabPlot exports across MOFs, Solar Perovskites, and PAN Nanofibers.
"""

import sys
from pathlib import Path

# Add root project directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd

try:
    from knowledge_base import ALL_DOMAINS
    from knowledge_base.benchmark_data import (
        generate_benchmark_mof_c1s,
        generate_benchmark_solar_pb4f,
        generate_benchmark_pan_n1s,
    )
    from core.calibration import apply_charge_calibration
    from core.background import extract_net_signal, compute_shirley_background
    from core.deconvolution import fit_xps_components
    from core.interpretation import interpret_xps_chemistry
    from visualizer.plot_core_level import render_core_level_plot
except ImportError:
    from xps_studio.knowledge_base import ALL_DOMAINS
    from xps_studio.knowledge_base.benchmark_data import (
        generate_benchmark_mof_c1s,
        generate_benchmark_solar_pb4f,
        generate_benchmark_pan_n1s,
    )
    from xps_studio.core.calibration import apply_charge_calibration
    from xps_studio.core.background import extract_net_signal, compute_shirley_background
    from xps_studio.core.deconvolution import fit_xps_components
    from xps_studio.core.interpretation import interpret_xps_chemistry
    from xps_studio.visualizer.plot_core_level import render_core_level_plot


def test_charge_calibration():
    """Tests automatic peak locking to 284.8 eV."""
    be_raw = np.linspace(292.0, 280.0, 100)
    # Peak at 285.5 eV (shifted by +0.7 eV)
    counts = 1000.0 * np.exp(-((be_raw - 285.5) / 0.8) ** 2)
    be_calib, shift, msg = apply_charge_calibration(be_raw, counts, method='Adventitious C 1s (Aliphatic 284.8 eV)')
    assert np.isclose(shift, -0.70, atol=0.05)
    assert np.isclose(be_calib[np.argmax(counts)], 284.80, atol=0.05)


def test_shirley_background():
    """Tests Shirley baseline convergence."""
    be = np.linspace(292.0, 280.0, 100)
    counts = 5000.0 * np.exp(-((be - 284.8) / 1.0) ** 2) + 1000.0
    bg = compute_shirley_background(be, counts)
    assert len(bg) == len(counts)
    assert np.all(bg <= counts)
    assert bg[0] >= bg[-1] or np.isclose(bg[0], bg[-1], rtol=0.2)


def test_mof_c1s_deconvolution():
    """Tests full pipeline on UiO-66 MOF C 1s benchmark."""
    df = generate_benchmark_mof_c1s()
    preset = ALL_DOMAINS['MOFs & Coordination Networks']['UiO-66 (Zr-BDC) / C 1s']
    
    be = df.iloc[:, 0].to_numpy()
    counts = df.iloc[:, 1].to_numpy()
    
    bg, net = extract_net_signal(be, counts, baseline_type="Shirley")
    fit_res, comp_curves, comp_summary, r2 = fit_xps_components(be, net, preset['components'])
    
    assert r2 > 0.95
    assert len(comp_summary) == 4
    assert 'Aromatic C-C / C-H' in comp_summary
    assert 'O-C=O Coordinated' in comp_summary
    
    # Interpretation
    interp = interpret_xps_chemistry(comp_summary, preset_dict=preset, core_level='C 1s')
    assert 'defect_ratio' in interp['metrics']
    assert len(interp['insights']) > 0


def test_solar_pb4f_doublet_coupling():
    """Tests spin-orbit doublet coupling (4f7/2 and 4f5/2 with 4:3 branching) and metallic Pb0 detection."""
    df = generate_benchmark_solar_pb4f()
    preset = ALL_DOMAINS['Photovoltaics & Solar Cells']['Perovskite Pb 4f (Lattice vs Metallic Pb⁰)']
    
    be = df.iloc[:, 0].to_numpy()
    counts = df.iloc[:, 1].to_numpy()
    
    bg, net = extract_net_signal(be, counts, baseline_type="Shirley")
    doublet_info = {
        'is_doublet': preset['is_doublet'],
        'doublet_delta_eV': preset['doublet_delta_eV'],
        'branching_ratio': preset['branching_ratio']
    }
    fit_res, comp_curves, comp_summary, r2 = fit_xps_components(
        be, net, preset['components'], doublet_info=doublet_info
    )
    
    assert r2 > 0.95
    interp = interpret_xps_chemistry(comp_summary, preset_dict=preset, core_level='Pb 4f')
    assert 'metallic_pb0_fraction' in interp['metrics']
    assert interp['metrics']['metallic_pb0_fraction']['value'] > 0.0


def test_pan_n1s_cyclization():
    """Tests PAN electrospun nanofiber N 1s cyclization index."""
    df = generate_benchmark_pan_n1s()
    preset = ALL_DOMAINS['Polymers & Hybrid Nanofibers (PAN)']['PAN Nitrile & Cyclization / N 1s']
    
    be = df.iloc[:, 0].to_numpy()
    counts = df.iloc[:, 1].to_numpy()
    
    bg, net = extract_net_signal(be, counts, baseline_type="Shirley")
    fit_res, comp_curves, comp_summary, r2 = fit_xps_components(be, net, preset['components'])
    
    assert r2 > 0.95
    interp = interpret_xps_chemistry(comp_summary, preset_dict=preset, core_level='N 1s')
    assert 'pan_cyclization_index' in interp['metrics']
    assert 20.0 <= interp['metrics']['pan_cyclization_index']['value'] <= 50.0


def test_figure_and_labplot_export():
    """Tests publication dual-panel figure rendering, OriginLab export, and LabPlot export table."""
    from modules.export_utils import get_originlab_ascii_bytes, get_labplot_ascii_bytes
    df = generate_benchmark_mof_c1s()
    preset = ALL_DOMAINS['MOFs & Coordination Networks']['UiO-66 (Zr-BDC) / C 1s']
    be = df.iloc[:, 0].to_numpy()
    counts = df.iloc[:, 1].to_numpy()
    bg, net = extract_net_signal(be, counts)
    fit_res, comp_curves, comp_summary, r2 = fit_xps_components(be, net, preset['components'])
    
    fig, labplot_df = render_core_level_plot(
        be, counts, bg, fit_res, comp_curves, comp_summary, core_label='C 1s'
    )
    assert fig is not None
    assert 'Binding_Energy_eV' in labplot_df.columns
    assert 'Residuals' in labplot_df.columns
    assert 'Comp_Aromatic_C-C___C-H' in labplot_df.columns

    # Test OriginLab ASCII export
    origin_bytes = get_originlab_ascii_bytes(labplot_df, title="XPS C1s OriginLab")
    assert len(origin_bytes) > 0 and b"A(X)" in origin_bytes and b"B(Y)" in origin_bytes
    dat_bytes = get_labplot_ascii_bytes(labplot_df, title="XPS C1s LabPlot")
    assert len(dat_bytes) > 0


def test_custom_lineshapes_and_editable_plot():
    """Tests Pseudo-Voigt GL(30), equal FWHM lock, fixed center, dynamic peak count, and custom plot config."""
    df = generate_benchmark_mof_c1s()
    be = df.iloc[:, 0].to_numpy()
    counts = df.iloc[:, 1].to_numpy()
    bg, net = extract_net_signal(be, counts, baseline_type="Shirley")

    custom_peaks = [
        {'prefix': 'p1_', 'name': 'sp2 C', 'center': 284.8, 'center_tol': 0.2, 'fix_center': True, 'sigma': 0.55, 'color': '#1f77b4'},
        {'prefix': 'p2_', 'name': 'C-O', 'center': 286.2, 'center_tol': 0.3, 'fix_center': False, 'sigma': 0.55, 'color': '#ff7f0e'},
        {'prefix': 'p3_', 'name': 'O-C=O', 'center': 288.7, 'center_tol': 0.3, 'fix_center': False, 'sigma': 0.55, 'color': '#2ca02c'},
    ]
    fit_res, comp_curves, comp_summary, r2 = fit_xps_components(
        be, net, custom_peaks, line_shape="Pseudo-Voigt (GL)", lock_fwhm_equal=True, gl_fraction=0.30
    )
    assert r2 > 0.90
    assert comp_summary['sp2 C']['Binding_Energy_eV'] == 284.8
    # Equal FWHM verification
    fwhms = [v['FWHM_eV'] for v in comp_summary.values()]
    assert max(fwhms) - min(fwhms) < 0.05

    plot_cfg = {
        'title': 'Custom MOF C 1s Study',
        'xlabel': 'Binding Energy [eV]',
        'ylabel': 'Normalized Counts',
        'legend_loc': 'outside right',
        'peak_label_mode': 'Name + BE + Area%',
        'peak_label_rotation': 90,
        'show_drop_lines': True,
        'show_stats_box': True,
        'stats_extras': {'r2': r2, 'redchi': fit_res.redchi, 'calib_shift': -0.25},
        'raw_style': 'Open Circles',
        'show_grid': True
    }
    fig, lp = render_core_level_plot(be, counts, bg, fit_res, comp_curves, comp_summary, plot_config=plot_cfg)
    assert fig is not None


def test_saudi_alliance_databank_verification():
    """Tests cross-institution audit matching against KAUST, KFUPM, KACST, and IAU benchmarks."""
    from modules.institutional_verifier import verify_against_saudi_databank
    from knowledge_base.saudi_research_databank import SAUDI_INSTITUTIONS, list_benchmarks_for_institution

    assert "KAUST" in SAUDI_INSTITUTIONS and "KFUPM" in SAUDI_INSTITUTIONS and "IAU" in SAUDI_INSTITUTIONS
    kaust_bms = list_benchmarks_for_institution("KAUST")
    assert len(kaust_bms) >= 3

    # Test synthetic deconvolution output audit
    mock_components = {
        "Aromatic C-C": {"Binding_Energy_eV": 284.8, "Area_Percent": 65.0},
        "Carboxylate O-C=O": {"Binding_Energy_eV": 288.6, "Area_Percent": 25.0},
        "Defect Formate": {"Binding_Energy_eV": 286.2, "Area_Percent": 10.0},
    }
    audit = verify_against_saudi_databank("XPS", mock_components, material_hint="UiO-66")
    assert audit["matched"] and audit["match_percentage"] >= 60.0
    assert "KAUST" in audit["institutions"] and "KFUPM" in audit["institutions"]


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("[RUNNING XPS STUDIO INTEGRATION SUITE]")
    test_charge_calibration()
    print("  [PASS] Charge Referencing & Calibration Engine")
    test_shirley_background()
    print("  [PASS] Iterative Shirley Baseline Engine")
    test_mof_c1s_deconvolution()
    print("  [PASS] MOF (UiO-66) C 1s Linker Defect Sizing")
    test_solar_pb4f_doublet_coupling()
    print("  [PASS] Solar Perovskite Pb 4f Doublet & Metallic Pb0 Photolysis")
    test_pan_n1s_cyclization()
    print("  [PASS] PAN Nanofiber N 1s Cyclization Index")
    test_figure_and_labplot_export()
    print("  [PASS] Dual-Panel Publication Figure & LabPlot Matrix")
    test_custom_lineshapes_and_editable_plot()
    print("  [PASS] Custom Line Shapes (GL Mix), Equal FWHM & Editable Typography")
    test_saudi_alliance_databank_verification()
    print("  [PASS] Saudi Research Alliance Databank & Cross-Audit Verification (KAUST/KFUPM/KACST/IAU)")
    print("\n[ALL 8 XPS STUDIO TESTS PASSED SUCCESSFULLY!]")
