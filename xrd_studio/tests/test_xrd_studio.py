"""
test_xrd_studio.py - Comprehensive Integration Test Suite for XRD Studio.
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

from core.background import extract_net_pattern
from core.calibration import apply_ka2_stripping, apply_two_theta_calibration
from core.interpretation import interpret_xrd_diagnostics
from core.peak_fitting import auto_detect_xrd_peaks, bragg_d_spacing, fit_xrd_peaks, scherrer_crystallite_size
from core.williamson_hall import compute_williamson_hall
from knowledge_base import ALL_XRD_DOMAINS
from knowledge_base.benchmark_data import generate_benchmark_xrd
from modules.export_utils import get_figure_bytes, get_labplot_ascii_bytes
from visualizer.plot_xrd import (
    render_williamson_hall_plot,
    render_xrd_deconvolution_plot,
    render_xrd_stacked_plot,
)


def run_suite():
    print("[RUNNING XRD STUDIO INTEGRATION SUITE]")

    # 1. Domain Benchmarks & AsLS / SNIP Baseline Stripping
    df_p25 = generate_benchmark_xrd("TiO₂ Anatase–Rutile Polymorphs (P25 / Calcined)")
    x = df_p25.iloc[:, 0].to_numpy(dtype=float)
    y = df_p25.iloc[:, 1].to_numpy(dtype=float)
    y_asls, bg_asls = extract_net_pattern(x, y, method="AsLS (Asymmetric Least Squares)", asls_lam=1e5, asls_p=0.004)
    y_snip, bg_snip = extract_net_pattern(x, y, method="SNIP (LLS Clipping)", snip_window=35)
    assert len(y_asls) == len(y) and np.all(np.isfinite(y_asls))
    assert float(np.nanmax(y_asls)) > 3000.0
    assert float(np.nanmedian(bg_asls)) > 40.0 and float(np.nanmedian(bg_snip)) > 30.0
    print("  [PASS] Domain Benchmarks + AsLS & SNIP Baseline Stripping")

    # 2. Bragg Law, Scherrer Equation (Instrumental Correction), & 2-Theta Alignment
    d_si = bragg_d_spacing(28.443, wavelength_A=1.540598)
    assert abs(d_si - 3.1355) < 0.01
    d_nm, beta_corr = scherrer_crystallite_size(0.35, 25.28, wavelength_nm=0.1540598, k_factor=0.9, beta_inst_deg=0.05)
    assert d_nm > 20.0 and beta_corr < 0.35
    x_cal, shift, msg = apply_two_theta_calibration(x, measured_peak_deg=28.543, target_peak_deg=28.443, mode="Zero-Shift (Δ2θ)")
    assert abs(shift + 0.100) < 1e-4 and "Zero-point" in msg
    y_ka1 = apply_ka2_stripping(x, y)
    assert len(y_ka1) == len(y) and np.all(np.isfinite(y_ka1))
    print("  [PASS] Bragg d-Spacing, Scherrer Broadening Subtraction, Kα2 Stripping & Alignment")

    # 3. Auto-Peak Detection & Multi-Peak Pseudo-Voigt Deconvolution (TiO2 P25)
    preset_tio2 = ALL_XRD_DOMAINS["Catalysts, Oxides & Metal NPs"]["TiO₂ Anatase–Rutile Polymorphs (P25 / Calcined)"]
    fit_res, comp_curves, peak_summary, r2, rwp = fit_xrd_peaks(
        x, y_asls, preset_tio2["peaks"], line_shape_mode="Pseudo-Voigt", beta_inst_deg=0.05
    )
    assert r2 > 0.98 and rwp < 20.0
    assert "Anatase (101)" in peak_summary and "Rutile (110)" in peak_summary
    detected = auto_detect_xrd_peaks(x, y_asls, min_prominence_pct=5.0, max_peaks=8)
    assert len(detected) >= 4
    print("  [PASS] Auto-Peak Detection & Pseudo-Voigt Multi-Peak Deconvolution")

    # 4. Williamson-Hall Microstrain & True Size Separation
    df_cu = generate_benchmark_xrd("FCC Metal Nanoparticles (Cu / Cu₂O Catalyst)")
    xc = df_cu.iloc[:, 0].to_numpy(dtype=float)
    yc = df_cu.iloc[:, 2].to_numpy(dtype=float)  # Cu strained sample
    yc_net, bg_c = extract_net_pattern(xc, yc, method="AsLS")
    preset_cu = ALL_XRD_DOMAINS["Catalysts, Oxides & Metal NPs"]["FCC Metal Nanoparticles (Cu / Cu₂O Catalyst)"]
    _, _, pk_cu, r2_cu, _ = fit_xrd_peaks(xc, yc_net, preset_cu["peaks"], line_shape_mode="Pseudo-Voigt", beta_inst_deg=0.05)
    wh = compute_williamson_hall(pk_cu)
    assert r2_cu > 0.97 and wh["valid"] and wh["n_peaks"] >= 4
    assert abs(wh["microstrain_percent"]) > 0.001
    print("  [PASS] Williamson–Hall Microstrain & Crystallite Separation Engine")

    # 5. Domain Diagnostics: Spurr-Myers Rutile Fraction, Perovskite PbI2 Index, & PAN/CNF d002
    diag_tio2 = interpret_xrd_diagnostics(peak_summary, wh, x, y_asls, bg_asls, "Catalysts, Oxides & Metal NPs", preset_tio2)
    assert "Spurr-Myers Rutile" in diag_tio2["metrics"]

    df_perov = generate_benchmark_xrd("MAPbI₃ / FAPbI₃ Perovskite Film (PbI₂ Check)")
    xp, yp = df_perov.iloc[:, 0].to_numpy(dtype=float), df_perov.iloc[:, 2].to_numpy(dtype=float)
    yp_net, bg_p = extract_net_pattern(xp, yp, method="AsLS")
    preset_perov = ALL_XRD_DOMAINS["Solar Perovskites & PV Absorbers"]["MAPbI₃ / FAPbI₃ Perovskite Film (PbI₂ Check)"]
    _, _, pk_perov, r2_p, _ = fit_xrd_peaks(xp, yp_net, preset_perov["peaks"])
    diag_perov = interpret_xrd_diagnostics(pk_perov, None, xp, yp_net, bg_p, "Solar Perovskites & PV Absorbers", preset_perov)
    assert r2_p > 0.97 and "PbI2 Fraction" in diag_perov["metrics"] and diag_perov["metrics"]["PbI2 Fraction"]["value"] > 15.0

    df_pan = generate_benchmark_xrd("Carbonized Nanofibers / Graphitic Carbon")
    xpan, ypan = df_pan.iloc[:, 0].to_numpy(dtype=float), df_pan.iloc[:, 3].to_numpy(dtype=float)
    ypan_net, bg_pan = extract_net_pattern(xpan, ypan, method="AsLS")
    preset_pan = ALL_XRD_DOMAINS["Polymers, PAN & Carbon Nanofibers"]["Carbonized Nanofibers / Graphitic Carbon"]
    _, _, pk_pan, _, _ = fit_xrd_peaks(xpan, ypan_net, preset_pan["peaks"])
    diag_pan = interpret_xrd_diagnostics(pk_pan, None, xpan, ypan_net, bg_pan, "Polymers, PAN & Carbon Nanofibers", preset_pan)
    assert "Interlayer d002" in diag_pan["metrics"] and 3.3 <= diag_pan["metrics"]["Interlayer d002"]["value"] <= 3.7
    print("  [PASS] Domain Crystallographic Intelligence (TiO₂ Spurr–Myers, Perovskite PbI₂, CNF d₀₀₂)")

    # 6. Dual-Panel, Stacked Waterfall, Williamson-Hall Plots & LabPlot/600 DPI Export
    fig_dec, lp_dec = render_xrd_deconvolution_plot(
        x, y, bg_asls, fit_res, comp_curves, peak_summary,
        preset_peaks=preset_tio2["peaks"], theme="Nature",
        plot_config={"title": "TiO2 P25 Test", "screen_dpi": 130, "stats_extras": {"r2": r2, "rwp": rwp}}
    )
    png_bytes = get_figure_bytes(fig_dec, "png", dpi=600)
    dat_bytes = get_labplot_ascii_bytes(lp_dec, title="XRD Test Matrix")
    assert len(png_bytes) > 10000 and b"Observed_Intensity" in dat_bytes
    plt.close(fig_dec)

    fig_stack, lp_stack = render_xrd_stacked_plot(df_p25, list(df_p25.columns[1:]), theme="ACS")
    assert len(lp_stack.columns) >= 3
    plt.close(fig_stack)

    fig_wh = render_williamson_hall_plot(wh, theme="Science")
    plt.close(fig_wh)
    print("  [PASS] Dual-Panel Deconvolution, Stacked Waterfall, Williamson–Hall & LabPlot Exports")

    # 7. Saudi Research Alliance Databank & Cross-Audit Verification (KAUST/KFUPM/KACST/IAU)
    from modules.institutional_verifier import verify_against_saudi_databank
    from knowledge_base.saudi_research_databank import SAUDI_INSTITUTIONS, list_benchmarks_for_institution

    assert "KFUPM" in SAUDI_INSTITUTIONS and "KACST" in SAUDI_INSTITUTIONS and "IAU" in SAUDI_INSTITUTIONS
    kfupm_bms = list_benchmarks_for_institution("KFUPM")
    assert len(kfupm_bms) >= 3

    # Test TiO2 P25 Bragg audit against KAUST/KFUPM/IAU reference
    audit_tio2 = verify_against_saudi_databank("XRD", peak_summary, material_hint="TiO2 Anatase")
    assert audit_tio2["matched"] and audit_tio2["match_percentage"] >= 60.0
    assert "IAU" in audit_tio2["institutions"] and "KAUST" in audit_tio2["institutions"]
    print("  [PASS] Saudi Research Alliance Databank & Cross-Audit Verification (KAUST/KFUPM/KACST/IAU)")

    print("\n[ALL 7 XRD STUDIO TESTS PASSED SUCCESSFULLY!]")


if __name__ == "__main__":
    run_suite()
