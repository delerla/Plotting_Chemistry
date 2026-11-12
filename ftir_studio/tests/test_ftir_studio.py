"""
test_ftir_studio.py - Comprehensive Integration Test Suite for FTIR Studio.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from core.baseline import extract_net_absorbance
from core.deconvolution import auto_detect_ir_bands, fit_ir_bands
from core.interpretation import interpret_ftir_chemistry
from core.preprocessing import (
    apply_atr_correction,
    apply_savgol_smooth,
    compute_second_derivative,
    convert_ir_scale,
    mask_co2_artifact,
)
from knowledge_base import ALL_FTIR_DOMAINS
from knowledge_base.benchmark_data import generate_benchmark_ftir
from modules.export_utils import get_figure_bytes, get_labplot_ascii_bytes
from visualizer.plot_ftir import (
    render_ftir_deconvolution_plot,
    render_ftir_stacked_plot,
    render_second_derivative_plot,
)


def run_suite():
    print("[RUNNING FTIR STUDIO INTEGRATION SUITE]")

    # 1. %T -> Absorbance Conversion, CO2 Artifact Masking & ATR Correction
    df_pan = generate_benchmark_ftir("PAN Nanofibers & Oxidative Stabilization")
    x = df_pan.iloc[:, 0].to_numpy(dtype=float)
    y_t = df_pan["Stabilized 240°C"].to_numpy(dtype=float)

    y_abs, src = convert_ir_scale(y_t, source_scale="Auto-Detect", target_scale="Absorbance (A)")
    assert src == "Transmittance (%T)" and float(np.nanmax(y_abs)) < 2.0
    y_t_roundtrip, _ = convert_ir_scale(y_abs, source_scale="Absorbance (A)", target_scale="Transmittance (%T)")
    assert np.allclose(y_t, y_t_roundtrip, atol=0.1)

    # Inject synthetic CO2 spike and verify removal
    y_spike = y_abs.copy()
    y_spike[(x >= 2330) & (x <= 2360)] = 1.5
    y_clean = mask_co2_artifact(x, y_spike)
    assert float(np.nanmax(y_clean[(x >= 2330) & (x <= 2360)])) < 0.25

    y_atr = apply_atr_correction(x, y_clean)
    assert y_atr[x.argmax()] > y_clean[x.argmax()]
    print("  [PASS] %T/Absorbance Conversion, CO2 Artifact Removal & ATR Correction")

    # 2. AsLS & Rubberband Baselines + 2nd Derivative Resolution
    y_asls, bg_asls = extract_net_absorbance(x, y_clean, method="AsLS (Asymmetric Least Squares)")
    y_rub, bg_rub = extract_net_absorbance(x, y_clean, method="Rubberband (Convex Hull)")
    assert np.all(np.isfinite(y_asls)) and np.all(np.isfinite(y_rub))
    d2 = compute_second_derivative(x, apply_savgol_smooth(y_asls, 9, 2))
    assert len(d2) == len(x) and np.all(np.isfinite(d2))
    print("  [PASS] AsLS & Rubberband Baselines + 2nd-Derivative Shoulder Resolution")

    # 3. ROI Multi-Band Deconvolution & PAN Cyclization Extent (E_s)
    roi_mask = (x >= 1200.0) & (x <= 2400.0)
    xr, yr = x[roi_mask], y_asls[roi_mask]
    preset_pan = ALL_FTIR_DOMAINS["Polymers, PAN & Stabilized Carbon"]["PAN Nanofibers & Oxidative Stabilization"]
    fit_res, comps, summary_pan, r2_pan, rmse_pan = fit_ir_bands(xr, yr, preset_pan["bands"], line_shape_mode="Gaussian")
    assert r2_pan > 0.96 and rmse_pan < 0.03
    assert "ν(C≡N) Nitrile" in summary_pan and "ν(C=N/C=C) Ladder" in summary_pan

    diag_pan = interpret_ftir_chemistry(summary_pan, "Polymers, PAN & Stabilized Carbon", preset_pan, x, y_asls)
    assert "Cyclization Index" in diag_pan["metrics"]
    assert 10.0 < diag_pan["metrics"]["Cyclization Index"]["value"] < 70.0
    print("  [PASS] PAN ROI Deconvolution & Quantitative Stabilization Index (E_s)")

    # 4. MOF Deacon Carboxylate Splitting + Unwashed H2BDC Detection
    df_mof = generate_benchmark_ftir("UiO-66 (Zr-BDC) & Linker-Defect Analysis")
    xm = df_mof.iloc[:, 0].to_numpy(dtype=float)
    ym_abs, _ = convert_ir_scale(df_mof["UiO-66 Unwashed (Free H₂BDC)"].to_numpy(dtype=float))
    ym_net, _ = extract_net_absorbance(xm, ym_abs, method="AsLS")
    m_roi = (xm >= 500.0) & (xm <= 1850.0)
    preset_mof = ALL_FTIR_DOMAINS["MOFs & Reticular Frameworks"]["UiO-66 (Zr-BDC) & Linker-Defect Analysis"]
    _, _, summary_mof, r2_mof, _ = fit_ir_bands(xm[m_roi], ym_net[m_roi], preset_mof["bands"])
    diag_mof = interpret_ftir_chemistry(summary_mof, "MOFs & Reticular Frameworks", preset_mof)
    assert r2_mof > 0.96 and "Deacon Splitting" in diag_mof["metrics"]
    assert 140.0 < diag_mof["metrics"]["Deacon Splitting"]["value"] < 210.0
    assert any("169" in w or "-COOH" in w for w in diag_mof["warnings"])
    print("  [PASS] MOF Deacon Carboxylate Splitting & Unwashed Acid Impurity Reasoning")

    # 5. Auto-Detection (Absorbance & 2nd Derivative) + Plots + LabPlot/600 DPI Export
    auto_b = auto_detect_ir_bands(xr, yr, min_prominence_pct=5.0, use_second_deriv=True)
    assert len(auto_b) >= 3

    fig_dec, lp_dec = render_ftir_deconvolution_plot(
        xr, y_clean[roi_mask], bg_asls[roi_mask], fit_res, comps, summary_pan,
        theme="Nature", plot_config={"title": "PAN 240C FTIR", "screen_dpi": 130, "stats_extras": {"r2": r2_pan, "rmse": rmse_pan}}
    )
    png_bytes = get_figure_bytes(fig_dec, "png", dpi=600)
    dat_bytes = get_labplot_ascii_bytes(lp_dec, title="FTIR Test Matrix")
    assert len(png_bytes) > 10000 and b"Observed_Absorbance" in dat_bytes
    plt.close(fig_dec)

    fig_stack, lp_stack, det_map = render_ftir_stacked_plot(
        df_pan, list(df_pan.columns[1:]), display_mode="Transmittance (%T)", theme="ACS"
    )
    assert len(det_map) == 3 and len(lp_stack.columns) >= 4
    plt.close(fig_stack)

    fig_d2 = render_second_derivative_plot(xr, yr, theme="Science")
    plt.close(fig_d2)
    print("  [PASS] 2nd-Deriv Auto-Seeding, Deconvolution/Stacked Plots & LabPlot/600 DPI Exports")

    # 6. Saudi Research Alliance Databank & Cross-Audit Verification (KAUST/KFUPM/KACST/IAU)
    from modules.institutional_verifier import verify_against_saudi_databank
    from knowledge_base.saudi_research_databank import SAUDI_INSTITUTIONS, list_benchmarks_for_institution

    assert "IAU" in SAUDI_INSTITUTIONS and "KAUST" in SAUDI_INSTITUTIONS
    iau_bms = list_benchmarks_for_institution("IAU")
    assert len(iau_bms) >= 2

    # Audit PAN FTIR fitted summary against KFUPM / KAUST / IAU benchmark
    audit_pan = verify_against_saudi_databank("FTIR", summary_pan, material_hint="PAN Nanofibers")
    assert audit_pan["matched"] and audit_pan["match_percentage"] >= 60.0
    assert "KFUPM" in audit_pan["institutions"] and "IAU" in audit_pan["institutions"]
    print("  [PASS] Saudi Research Alliance Databank & Cross-Audit Verification (KAUST/KFUPM/KACST/IAU)")

    print("\n[ALL 6 FTIR STUDIO TESTS PASSED SUCCESSFULLY!]")


if __name__ == "__main__":
    run_suite()
