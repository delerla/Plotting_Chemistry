"""
uv_vis_studio.tests.test_uv_vis_studio
Automated Verification Suite for UV-Vis Studio:
- Benchmark Ingestion
- Multi-Order Reaction Kinetics
- Tauc Plot Bandgap Extrapolation & Urbach Energy
- Multi-Peak Deconvolution
- OriginLab ASCII (.dat) & Workbook (.xlsx) Generation
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

from uv_vis_studio.knowledge_base.benchmarks import (
    UV_VIS_DOMAINS,
    generate_rhb_kinetics,
    generate_methylene_blue_kinetics,
    generate_mapbi3_tauc_spectrum,
    generate_tio2_tauc_spectrum,
    generate_gold_nanorods_spectrum,
)
from uv_vis_studio.core.kinetics import fit_all_kinetic_models
from uv_vis_studio.core.tauc_analysis import compute_tauc_series, fit_tauc_bandgap, fit_urbach_energy
from uv_vis_studio.core.deconvolution import fit_uv_vis_peaks
from uv_vis_studio.modules.export_utils import get_originlab_ascii_bytes, get_originlab_excel_bytes


def test_benchmarks():
    print("[TEST 1] Verifying Curated UV-Vis Domain Benchmarks...")
    df_rhb, k_rhb = generate_rhb_kinetics()
    assert not df_rhb.empty and df_rhb.shape[1] >= 8
    assert not k_rhb.empty

    df_mb, k_mb = generate_methylene_blue_kinetics()
    assert not df_mb.empty

    df_mapbi3 = generate_mapbi3_tauc_spectrum()
    assert "Photon_Energy_eV" in df_mapbi3.columns

    df_tio2 = generate_tio2_tauc_spectrum()
    assert not df_tio2.empty

    df_au = generate_gold_nanorods_spectrum()
    assert not df_au.empty
    print("  --> PASS: All 5 benchmark series generated successfully.")


def test_reaction_kinetics():
    print("[TEST 2] Verifying Multi-Order Reaction Kinetics Engine...")
    t = np.array([0, 10, 20, 30, 45, 60, 90, 120])
    # Synthetic first order decay
    c0 = 10.0
    c_t = c0 * np.exp(-0.025 * t)
    
    res = fit_all_kinetic_models(t, c_t, is_concentration=True)
    assert res["best_model"] == "Pseudo-First-Order (Langmuir-Hinshelwood)"
    assert res["pfo"]["r2"] > 0.99
    assert abs(res["pfo"]["k"] - 0.025) < 0.005
    assert not res["table"].empty
    print(f"  --> PASS: Optimal model = {res['best_model']}, k_app = {res['pfo']['k']:.4f} min^-1 (R2={res['pfo']['r2']:.4f})")


def test_tauc_bandgap_and_urbach():
    print("[TEST 3] Verifying Tauc Bandgap & Urbach Defect Engine...")
    df_perov = generate_mapbi3_tauc_spectrum()
    wl = df_perov["Wavelength_nm"].to_numpy()
    abs_vals = df_perov["Absorbance_OD"].to_numpy()

    df_tauc = compute_tauc_series(wl, abs_vals, transition_mode="Direct Allowed (n = 1/2)")
    assert "Tauc_Y" in df_tauc.columns

    fit_res = fit_tauc_bandgap(df_tauc["Photon_Energy_eV"], df_tauc["Tauc_Y"], alpha_or_abs=df_tauc["Absorbance_OD"])
    eg = fit_res["bandgap_ev"]
    assert 1.45 <= eg <= 1.70, f"Expected Eg ~1.58 eV, got {eg}"
    assert fit_res["r2"] > 0.90

    urbach_res = fit_urbach_energy(df_tauc["Photon_Energy_eV"], df_tauc["Alpha_cm_inv"], bandgap_ev=eg)
    assert not np.isnan(urbach_res["urbach_energy_mev"])
    print(f"  --> PASS: MAPbI3 Eg = {eg:.3f} eV, lambda_onset = {fit_res['lambda_onset_nm']} nm, Eu = {urbach_res['urbach_energy_mev']:.1f} meV")


def test_deconvolution():
    print("[TEST 4] Verifying Multi-Component Peak Deconvolution...")
    wl = np.linspace(400, 800, 400)
    # 2 peaks at 520 nm and 660 nm
    y = 1.0 * np.exp(-0.5 * ((wl - 520) / 25) ** 2) + 1.5 * np.exp(-0.5 * ((wl - 660) / 20) ** 2)
    res = fit_uv_vis_peaks(wl, y, [515.0, 665.0])
    assert len(res["peaks"]) == 2
    assert res["r2"] > 0.98
    print(f"  --> PASS: Deconvolved 2 chromophores with R2 = {res['r2']:.4f}")


def test_originlab_exports():
    print("[TEST 5] Verifying OriginLab Matrix (.dat) & Workbook (.xlsx) Exporters...")
    _, k_df = generate_rhb_kinetics()
    
    # OriginLab ASCII (.dat)
    dat_bytes = get_originlab_ascii_bytes(k_df, title="UV-Vis Matrix")
    assert len(dat_bytes) > 100
    assert b"A(X)" in dat_bytes
    assert b"B(Y)" in dat_bytes

    # OriginLab Excel Workbook (.xlsx)
    xlsx_bytes = get_originlab_excel_bytes(k_df, title="UV-Vis Matrix")
    assert len(xlsx_bytes) > 1000
    print("  --> PASS: OriginLab .dat and .xlsx generated cleanly.")


if __name__ == "__main__":
    print("\n=======================================================")
    print(" RUNNING UV-VIS STUDIO COMPREHENSIVE VERIFICATION SUITE")
    print("=======================================================")
    test_benchmarks()
    test_reaction_kinetics()
    test_tauc_bandgap_and_urbach()
    test_deconvolution()
    test_originlab_exports()
    print("\n[ALL 5 UV-VIS STUDIO TESTS PASSED SUCCESSFULLY!]\n")
