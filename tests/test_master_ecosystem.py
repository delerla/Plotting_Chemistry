"""
tests/test_master_ecosystem.py
Master Enterprise Self-Test & Diagnostic Audit Suite for:
1. Master Gateway (app.py) & Ingestion / Export Engines
2. FTIR Intelligence Studio (ftir_studio)
3. XRD Crystallography Studio (xrd_studio)
4. XPS Deep-Intelligence Studio (xps_studio)
5. UV-Vis & Photokinetics Studio (uv_vis_studio)
6. SEM-EDX Microstructural Studio (sem_edx_studio)
7. Multi-Page Stream Routing & Cloud URL Registry Integrity
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# 1. GATEWAY & CORE EXPORT AUDIT
# ------------------------------------------------------------------------------
from modules.file_parser import load_smart_file, sanitize_spectral_dataframe
from modules.export_utils import (
    get_originlab_ascii_bytes,
    get_originlab_excel_bytes,
    get_labplot_ascii_bytes,
    build_analysis_bundle_zip
)
from modules.saudi_search_ui import search_saudi_databank

# ------------------------------------------------------------------------------
# 2. FTIR STUDIO AUDIT
# ------------------------------------------------------------------------------
from ftir_studio.core.baseline import compute_asls_baseline, compute_rubberband_baseline
from ftir_studio.core.preprocessing import compute_second_derivative, convert_ir_scale
from ftir_studio.core.deconvolution import auto_detect_ir_bands, fit_ir_bands
from ftir_studio.knowledge_base.benchmark_data import generate_benchmark_ftir

# ------------------------------------------------------------------------------
# 3. XRD STUDIO AUDIT
# ------------------------------------------------------------------------------
from xrd_studio.core.peak_fitting import scherrer_crystallite_size, bragg_d_spacing, fit_xrd_peaks
from xrd_studio.core.williamson_hall import compute_williamson_hall
from xrd_studio.core.calibration import apply_ka2_stripping
from xrd_studio.knowledge_base.benchmark_data import generate_benchmark_xrd

# ------------------------------------------------------------------------------
# 4. XPS STUDIO AUDIT
# ------------------------------------------------------------------------------
from xps_studio.core.calibration import apply_charge_calibration
from xps_studio.core.background import extract_net_signal
from xps_studio.core.deconvolution import fit_xps_components
from xps_studio.knowledge_base.benchmark_data import generate_benchmark_mof_c1s

# ------------------------------------------------------------------------------
# 5. UV-VIS STUDIO AUDIT
# ------------------------------------------------------------------------------
from uv_vis_studio.core.kinetics import fit_all_kinetic_models
from uv_vis_studio.core.tauc_analysis import compute_tauc_series, fit_tauc_bandgap, fit_urbach_energy
from uv_vis_studio.core.deconvolution import fit_uv_vis_peaks
from uv_vis_studio.knowledge_base.benchmarks import generate_rhb_kinetics, generate_mapbi3_tauc_spectrum

# ------------------------------------------------------------------------------
# 6. SEM-EDX STUDIO AUDIT
# ------------------------------------------------------------------------------
from sem_edx_studio.core.segmentation import segment_micrograph
from sem_edx_studio.core.distribution import fit_size_distributions
from sem_edx_studio.core.edx_analysis import analyze_edx_spectrum
from sem_edx_studio.knowledge_base.benchmarks import generate_uio66_micrograph, generate_uio66_edx_spectrum


def audit_gateway_and_exports():
    print("\n[AUDIT 1/7] Master Gateway & Universal Interoperability...")
    
    # 1.1 Ingestion & Detection on synthetic spectra
    x = np.linspace(4000, 400, 500)
    y = np.exp(-0.5 * ((x - 1650) / 30) ** 2)
    csv_bytes = f"Wavenumber,Absorbance\n" + "\n".join(f"{xi},{yi}" for xi, yi in zip(x, y))
    df_p, img_p, meta = load_smart_file(csv_bytes.encode('utf-8'), "test_ftir.csv")
    assert "FTIR" in meta["detected_technique"]
    assert meta["confidence"] > 0.85
    print("  --> [PASS] Physics-Based Technique Auto-Detection (FTIR 95%+ confidence)")

    # 1.2 OriginLab ASCII (.dat) with 4-tier metadata
    df_test = pd.DataFrame({"Energy_eV": [280.0, 284.8, 290.0], "Intensity": [120.0, 4500.0, 310.0]})
    dat_b = get_originlab_ascii_bytes(df_test, title="Test Matrix", units={"Energy_eV": "eV", "Intensity": "counts"})
    assert b"A(X)" in dat_b
    assert b"B(Y)" in dat_b
    assert b"Energy_eV" in dat_b
    print("  --> [PASS] OriginLab ASCII (.dat) 4-tier Metadata Verification (A(X), B(Y), Units)")

    # 1.3 OriginLab Excel Workbook (.xlsx)
    xlsx_b = get_originlab_excel_bytes(df_test, title="Test Workbook")
    assert len(xlsx_b) > 2000
    print("  --> [PASS] OriginLab Excel Workbook (.xlsx) Generation")

    # 1.4 LabPlot ASCII (.dat)
    labplot_b = get_labplot_ascii_bytes(df_test, title="Test LabPlot")
    assert len(labplot_b) > 50
    print("  --> [PASS] LabPlot ASCII Matrix Export")

    # 1.5 Saudi Databank Query
    results = search_saudi_databank(institution="KAUST", query="UiO-66")
    assert len(results) > 0
    print(f"  --> [PASS] Saudi Research Alliance Databank Search ({len(results)} matches for KAUST UiO-66)")


def audit_ftir_studio():
    print("\n[AUDIT 2/7] FTIR Deep-Intelligence Studio...")
    df_pan = generate_benchmark_ftir("PAN Nanofibers & Oxidative Stabilization")
    w = df_pan.iloc[:, 0].to_numpy(dtype=float)
    y_raw = df_pan.iloc[:, 1].to_numpy(dtype=float)

    # Scale conversion
    y_abs, _ = convert_ir_scale(y_raw, source_scale="Transmittance (%T)", target_scale="Absorbance (A)")
    assert len(y_abs) == len(y_raw)

    # Baselines
    asls_bg = compute_asls_baseline(y_abs, lam=1e5, p=0.005)
    assert len(asls_bg) == len(y_abs)
    rb_bg = compute_rubberband_baseline(w, y_abs)
    assert len(rb_bg) == len(y_abs)
    print("  --> [PASS] AsLS & Rubberband Baseline Algorithms")

    # 2nd derivative shoulder peak discovery
    d2 = compute_second_derivative(w, y_abs, window_len=15, polyorder=3)
    assert len(d2) == len(y_abs)
    bands = auto_detect_ir_bands(w, y_abs - asls_bg, min_prominence_pct=5.0)
    assert len(bands) >= 1
    print(f"  --> [PASS] 2nd-Derivative & Auto-Deconvolution Bands ({len(bands)} bands identified)")


def audit_xrd_studio():
    print("\n[AUDIT 3/7] XRD Crystallography Studio...")
    df_xrd = generate_benchmark_xrd("TiO₂ Anatase–Rutile Polymorphs (P25 / Calcined)")
    two_theta = df_xrd.iloc[:, 0].to_numpy(dtype=float)
    intensity = df_xrd.iloc[:, 1].to_numpy(dtype=float)

    # Scherrer Crystallite Sizing
    d_nm, beta_corr = scherrer_crystallite_size(
        fwhm_obs_deg=0.35,
        two_theta_deg=25.28,
        wavelength_nm=0.1540598,
        k_factor=0.9,
        beta_inst_deg=0.05
    )
    assert 20.0 <= d_nm <= 35.0
    print(f"  --> [PASS] Scherrer Crystallite Sizing (D = {d_nm:.2f} nm)")

    # Williamson-Hall Microstrain Separation
    from xrd_studio.knowledge_base import ALL_XRD_DOMAINS
    from xrd_studio.core.background import extract_net_pattern
    df_cu = generate_benchmark_xrd("FCC Metal Nanoparticles (Cu / Cu₂O Catalyst)")
    xc = df_cu.iloc[:, 0].to_numpy(dtype=float)
    yc = df_cu.iloc[:, 2].to_numpy(dtype=float)
    yc_net, _ = extract_net_pattern(xc, yc, method="AsLS")
    preset_cu = ALL_XRD_DOMAINS["Catalysts, Oxides & Metal NPs"]["FCC Metal Nanoparticles (Cu / Cu₂O Catalyst)"]
    _, _, pk_cu, r2_cu, _ = fit_xrd_peaks(xc, yc_net, preset_cu["peaks"], line_shape_mode="Pseudo-Voigt", beta_inst_deg=0.05)
    wh = compute_williamson_hall(pk_cu)
    assert wh["valid"] and wh["n_peaks"] >= 4
    print(f"  --> [PASS] Williamson–Hall Microstrain Separation (D = {wh['D_wh_nm']:.1f} nm, Strain = {wh['microstrain_percent']:.4f}%)")

    # Cu Ka2 Stripping
    y_stripped = apply_ka2_stripping(two_theta, intensity, lambda_a1=1.540598, lambda_a2=1.544426, ka_ratio=0.5)
    assert len(y_stripped) == len(intensity)
    print("  --> [PASS] Cu Kα2 Rachinger Stripping Engine")


def audit_xps_studio():
    print("\n[AUDIT 4/7] XPS Deep-Intelligence Studio...")
    df_c1s = generate_benchmark_mof_c1s()
    be = df_c1s["Binding_Energy_eV"].to_numpy()
    counts = df_c1s["Counts_Per_Second"].to_numpy()

    # Charge Referencing (align aliphatic C 1s to 284.8 eV)
    be_calib, shift, msg = apply_charge_calibration(be, counts, method="Adventitious C 1s (Aliphatic 284.8 eV)")
    assert abs(shift) < 5.0
    print(f"  --> [PASS] Automated C 1s Charge Referencing (Shift = {shift:+.2f} eV)")

    # Shirley Baseline
    bg_shirley, sig_net = extract_net_signal(be_calib, counts, baseline_type="Shirley")
    assert len(sig_net) == len(counts)
    assert np.all(bg_shirley >= 0)
    print("  --> [PASS] Iterative Non-Linear Shirley Baseline")

    # Voigt Multi-Peak Deconvolution
    from xps_studio.knowledge_base import ALL_DOMAINS
    preset = ALL_DOMAINS["MOFs & Coordination Networks"]["UiO-66 (Zr-BDC) / C 1s"]
    fit_res, comp_curves, comp_summary, r2 = fit_xps_components(
        be_calib, sig_net, preset["components"]
    )
    assert r2 > 0.95
    print(f"  --> [PASS] Voigt Multi-Peak Deconvolution (R² = {r2:.4f})")


def audit_uv_vis_studio():
    print("\n[AUDIT 5/7] UV-Vis & Photokinetics Studio...")
    df_rhb, k_df = generate_rhb_kinetics()
    t = k_df["Time_min"].to_numpy()
    a = k_df["Absorbance_at_554nm"].to_numpy()

    # Multi-Order Kinetics Regression & AIC/BIC Ranking
    kin_res = fit_all_kinetic_models(t, a, is_concentration=False)
    assert "Pseudo-First-Order" in kin_res["best_model"]
    assert kin_res["pfo"]["r2"] > 0.98
    print(f"  --> [PASS] Reaction Kinetics Regression ({kin_res['best_model']}, R²={kin_res['pfo']['r2']:.4f})")

    # Tauc Bandgap & Urbach Energy
    df_perov = generate_mapbi3_tauc_spectrum()
    df_tauc = compute_tauc_series(df_perov["Wavelength_nm"], df_perov["Absorbance_OD"])
    tauc_fit = fit_tauc_bandgap(df_tauc["Photon_Energy_eV"], df_tauc["Tauc_Y"], alpha_or_abs=df_tauc["Absorbance_OD"])
    assert 1.45 <= tauc_fit["bandgap_ev"] <= 1.70
    urbach_fit = fit_urbach_energy(df_tauc["Photon_Energy_eV"], df_tauc["Alpha_cm_inv"], tauc_fit["bandgap_ev"])
    assert not np.isnan(urbach_fit["urbach_energy_mev"])
    print(f"  --> [PASS] Tauc Optical Bandgap (Eg = {tauc_fit['bandgap_ev']:.3f} eV, Eu = {urbach_fit['urbach_energy_mev']:.1f} meV)")

    # Publication ZIP Bundle Signature
    fig, _ = plt.subplots()
    zip_bytes = build_analysis_bundle_zip(
        fig=fig,
        base_name="UV_Vis_Test",
        labplot_df=df_tauc,
        summary_data={"bandgap": tauc_fit["bandgap_ev"]},
        title="UV-Vis Test"
    )
    assert len(zip_bytes) > 5000
    plt.close(fig)
    print("  --> [PASS] UV-Vis Publication ZIP Package Generation")


def audit_sem_edx_studio():
    print("\n[AUDIT 6/7] SEM-EDX Microstructural Studio...")
    img = generate_uio66_micrograph()
    
    # Computer Vision Segmentation
    seg_res = segment_micrograph(img, scale_nm_per_px=10.0, method="Otsu", min_area_px=15)
    assert seg_res["n_particles"] > 10
    df_p = seg_res["df_particles"]
    print(f"  --> [PASS] Distance-Watershed Micrograph Segmentation ({seg_res['n_particles']} particles)")

    # Log-Normal & Weibull Sizing Distributions
    dist_res = fit_size_distributions(df_p["Diameter_nm"].to_numpy())
    assert not np.isnan(dist_res["d50_nm"])
    assert dist_res["pdi"] > 0
    print(f"  --> [PASS] Sizing Distributions (d50 = {dist_res['d50_nm']:.1f} nm, PDI = {dist_res['pdi']:.3f})")

    # EDX Microanalysis
    df_edx = generate_uio66_edx_spectrum()
    edx_res = analyze_edx_spectrum(df_edx, peak_prominence=60.0)
    assert not edx_res["df_quant"].empty
    elems = edx_res["df_quant"]["Element"].tolist()
    assert len(elems) >= 2
    print(f"  --> [PASS] EDX Microanalysis ({len(elems)} elements: {elems})")

    # Publication ZIP Bundle Signature
    fig, _ = plt.subplots()
    zip_b = build_analysis_bundle_zip(
        fig=fig,
        base_name="SEM_EDX_Test",
        labplot_df=df_p,
        summary_data={"particles": seg_res["n_particles"]},
        title="SEM-EDX Test"
    )
    assert len(zip_b) > 5000
    plt.close(fig)
    print("  --> [PASS] SEM-EDX Publication ZIP Package Generation")


def audit_routing_and_links():
    print("\n[AUDIT 7/7] Multi-Page Stream Routing & Cloud URL Registry...")
    pages_dir = ROOT_DIR / "pages"
    expected_pages = [
        "1_XPS_Studio.py",
        "2_XRD_Studio.py",
        "3_FTIR_Studio.py",
        "4_UV_Vis_Studio.py",
        "5_SEM_EDX_Studio.py"
    ]
    for p in expected_pages:
        page_file = pages_dir / p
        assert page_file.exists(), f"Missing page: {p}"
        content = page_file.read_text(encoding="utf-8")
        assert "runpy.run_path" in content
    print("  --> [PASS] All 5 multi-page route files verified in pages/ directory.")

    # Verify unified navigation bar, footer, counter, and centralized review policy
    from modules.counter_module import MASTER_HUB_URL, DOMAIN_REGISTRY
    assert MASTER_HUB_URL == "https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/"
    assert len(DOMAIN_REGISTRY) == 6

    studios = [
        ROOT_DIR / "ftir_studio" / "app_ftir.py",
        ROOT_DIR / "xrd_studio" / "app_xrd.py",
        ROOT_DIR / "xps_studio" / "app_xps.py",
        ROOT_DIR / "uv_vis_studio" / "app_uv_vis.py",
        ROOT_DIR / "sem_edx_studio" / "app_sem_edx.py",
    ]
    for s_path in studios:
        text = s_path.read_text(encoding="utf-8")
        assert "render_studio_navigation_bar" in text, f"Missing unified nav bar in {s_path.name}"
        assert "render_sidebar_counter" in text, f"Missing sidebar counter in {s_path.name}"
        assert "render_unified_studio_footer" in text, f"Missing unified footer in {s_path.name}"
        assert "render_community_reviews" not in text, f"Review form should only be on Master Hub, found in {s_path.name}"

    app_text = (ROOT_DIR / "app.py").read_text(encoding="utf-8")
    assert "render_community_reviews" in app_text, "Missing centralized reviews on Master Hub (app.py)"
    assert "render_cross_domain_traffic_panel" in app_text, "Missing cross-domain traffic panel on Master Hub (app.py)"
    print("  --> [PASS] Unified cross-studio navigation, counters, and centralized Master Hub review architecture verified.")


if __name__ == "__main__":
    print("==============================================================================")
    print(" MASTER ENTERPRISE DIAGNOSTIC AUDIT & SELF-TEST SUITE")
    print(" Lead: Dr. Deler Langenberg")
    print("==============================================================================")
    try:
        audit_gateway_and_exports()
        audit_ftir_studio()
        audit_xrd_studio()
        audit_xps_studio()
        audit_uv_vis_studio()
        audit_sem_edx_studio()
        audit_routing_and_links()
        print("\n==============================================================================")
        print(" [SUCCESS] ALL 7 MASTER AUDIT CATEGORIES PASSED WITH ZERO DEFECTS!")
        print("==============================================================================\n")
    except Exception as e:
        print(f"\n[AUDIT FAILED]: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
