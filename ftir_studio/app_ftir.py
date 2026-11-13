"""
app.py - FTIR Studio: Lightweight, Apply-Driven Materials-Specific Infrared Spectroscopy Platform
Authored & Maintained by Dr. Deler Langenberg (2026)
Dedicated for: PAN/Polymers, MOFs & Carboxylate Frameworks, Solar Perovskites, and Catalysts/Oxides.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PKG_DIR = Path(__file__).resolve().parent
for _p in (str(PKG_DIR), str(BASE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from modules.export_utils import (
    PUBLICATION_PALETTES,
    build_analysis_bundle_zip,
    get_figure_bytes,
    get_labplot_ascii_bytes,
    get_originlab_ascii_bytes,
    get_originlab_excel_bytes,
)
from modules.file_parser import load_smart_file

try:
    from knowledge_base import ALL_FTIR_DOMAINS, DOMAIN_OPTIONS
    from knowledge_base.benchmark_data import generate_benchmark_ftir
    from core.baseline import extract_net_absorbance
    from core.deconvolution import auto_detect_ir_bands, fit_ir_bands
    from core.interpretation import interpret_ftir_chemistry
    from core.preprocessing import (
        apply_atr_correction,
        apply_savgol_smooth,
        convert_ir_scale,
        mask_co2_artifact,
    )
    from visualizer.plot_ftir import (
        render_ftir_deconvolution_plot,
        render_ftir_stacked_plot,
        render_second_derivative_plot,
    )
    from knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        list_benchmarks_for_institution,
    )
    from modules.institutional_verifier import verify_against_saudi_databank
except ImportError:
    from ftir_studio.knowledge_base import ALL_FTIR_DOMAINS, DOMAIN_OPTIONS
    from ftir_studio.knowledge_base.benchmark_data import generate_benchmark_ftir
    from ftir_studio.core.baseline import extract_net_absorbance
    from ftir_studio.core.deconvolution import auto_detect_ir_bands, fit_ir_bands
    from ftir_studio.core.interpretation import interpret_ftir_chemistry
    from ftir_studio.core.preprocessing import (
        apply_atr_correction,
        apply_savgol_smooth,
        convert_ir_scale,
        mask_co2_artifact,
    )
    from ftir_studio.visualizer.plot_ftir import (
        render_ftir_deconvolution_plot,
        render_ftir_stacked_plot,
        render_second_derivative_plot,
    )
    from ftir_studio.knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        list_benchmarks_for_institution,
    )
    from ftir_studio.modules.institutional_verifier import verify_against_saudi_databank


st.set_page_config(
    page_title="FTIR Studio - Dr. Deler Langenberg",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lightweight System CSS (No blocking external fonts)
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    .ftir-header {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f2b48;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }
    .profile-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        border-radius: 8px;
        padding: 13px;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
    .insight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0284c7;
        padding: 11px 15px;
        border-radius: 6px;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 9px 13px;
        border-radius: 6px;
        color: #92400e;
        margin-top: 8px;
        font-size: 0.89rem;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.73rem;
        font-weight: 600;
    }
    .badge-dark { background: #1e293b; color: #f8fafc; }
    .badge-blue { background: #e0f2fe; color: #0284c7; }
    .badge-green { background: #dcfce7; color: #16a34a; }
</style>
""", unsafe_allow_html=True)

DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"
]


@st.cache_data(show_spinner=False)
def _cached_parse_file(raw_bytes: bytes, filename: str):
    return load_smart_file(raw_bytes, filename=filename)


@st.cache_data(show_spinner=False)
def _cached_benchmark_ftir(preset_name: str):
    return generate_benchmark_ftir(preset_name)


def _preset_to_band_df(bands: list) -> pd.DataFrame:
    rows = []
    for idx, b in enumerate(bands):
        rows.append({
            "Label": str(b.get("label", f"Band {idx + 1}")),
            "Mode": str(b.get("mode", "")),
            "Center (cm⁻¹)": round(float(b.get("center", 1600.0)), 1),
            "FWHM Init (cm⁻¹)": round(float(b.get("fwhm", 28.0)), 1),
            "Shape": "Auto",
            "Fix ν": False,
            "Color": str(b.get("color", DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])),
            "Assignment": str(b.get("meaning", "Vibrational mode")),
        })
    return pd.DataFrame(rows)


def _compute_and_store_ir_fit(
    x_raw: np.ndarray,
    y_raw_in: np.ndarray,
    phys: dict,
    band_df: pd.DataFrame,
    active_preset: dict,
    preset_name: str,
    domain_choice: str,
    sample_name: str,
):
    """Pre-processes full IR trace -> ROI cropping -> baseline stripping -> lmfit deconvolution."""
    ord_i = np.argsort(x_raw)
    x_full = x_raw[ord_i]
    y_full = y_raw_in[ord_i]

    # Convert to Absorbance (beer-lambert quantitative deconvolution space)
    y_abs_full, detected_src = convert_ir_scale(
        y_full,
        source_scale=phys["input_scale"],
        target_scale="Absorbance (A)",
    )
    if phys["mask_co2"]:
        y_abs_full = mask_co2_artifact(x_full, y_abs_full)
    if phys["atr_correct"]:
        y_abs_full = apply_atr_correction(x_full, y_abs_full)
    if int(phys["sg_window"]) >= 5:
        y_abs_full = apply_savgol_smooth(y_abs_full, window_len=int(phys["sg_window"]), polyorder=2)

    # Full-range baseline for diagnostic O-H checks
    y_abs_full_net, _ = extract_net_absorbance(
        x_full, y_abs_full,
        method=phys["bg_method"],
        asls_lam=float(10 ** float(phys["asls_log_lam"])),
        asls_p=float(phys["asls_p"]),
    )

    # Restrict fitting ROI window
    w_min = float(min(phys["roi_min"], phys["roi_max"]))
    w_max = float(max(phys["roi_min"], phys["roi_max"]))
    mask_roi = (x_full >= w_min) & (x_full <= w_max)
    if np.sum(mask_roi) < 15:
        x_roi, y_roi = x_full.copy(), y_abs_full.copy()
    else:
        x_roi, y_roi = x_full[mask_roi], y_abs_full[mask_roi]

    y_net, bg_curve = extract_net_absorbance(
        x_roi, y_roi,
        method=phys["bg_method"],
        asls_lam=float(10 ** float(phys["asls_log_lam"])),
        asls_p=float(phys["asls_p"]),
    )

    # Parse band config table (keep only bands within ROI window +- 40 cm-1 or auto-detect)
    b_configs = []
    if band_df is not None and not band_df.empty:
        for _, row in band_df.iterrows():
            lbl = str(row.get("Label", "")).strip()
            if not lbl:
                continue
            c_val = float(row.get("Center (cm⁻¹)", 1600.0))
            if (x_roi.min() - 40.0) <= c_val <= (x_roi.max() + 40.0):
                b_configs.append({
                    "label": lbl,
                    "mode": str(row.get("Mode", "")),
                    "center": c_val,
                    "fwhm": float(row.get("FWHM Init (cm⁻¹)", 26.0)),
                    "shape": str(row.get("Shape", "Auto") or "Auto"),
                    "fix_center": bool(row.get("Fix ν", False)),
                    "color": str(row.get("Color", "#1f77b4")),
                    "meaning": str(row.get("Assignment", "Vibrational mode")),
                })

    if not b_configs:
        b_configs = auto_detect_ir_bands(x_roi, y_net, min_prominence_pct=5.0, max_bands=8)

    fit_res, comp_curves, band_summary, r2, rmse = fit_ir_bands(
        x_roi,
        y_net,
        band_configs=b_configs,
        line_shape_mode=phys["line_shape_mode"],
        center_tol_cm1=float(phys["center_tol_cm1"]),
        fwhm_bounds=(float(phys["fwhm_min"]), float(phys["fwhm_max"])),
        lock_fwhm_equal=bool(phys["lock_fwhm_equal"]),
        residual_baseline=phys["resid_bg_mode"],
    )

    return {
        "x_full": x_full,
        "y_abs_full_net": y_abs_full_net,
        "x_roi": x_roi,
        "y_abs_roi": y_roi,
        "y_net": y_net,
        "bg_curve": bg_curve,
        "fit_result": fit_res,
        "comp_curves": comp_curves,
        "band_summary": band_summary,
        "r2": r2,
        "rmse": rmse,
        "detected_src": detected_src,
        "active_preset": active_preset,
        "preset_name": preset_name,
        "domain_choice": domain_choice,
        "sample_name": sample_name,
        "line_shape_mode": phys["line_shape_mode"],
    }


# ==============================================================================
# SESSION STATE DEFAULTS
# ==============================================================================
if "ftir_physics_cfg" not in st.session_state:
    st.session_state["ftir_physics_cfg"] = {
        "input_scale": "Auto-Detect",
        "mask_co2": True,
        "atr_correct": False,
        "sg_window": 9,
        "bg_method": "AsLS (Asymmetric Least Squares)",
        "asls_log_lam": 6.0,
        "asls_p": 0.004,
        "line_shape_mode": "Gaussian",
        "roi_min": 1200.0,
        "roi_max": 2400.0,
        "center_tol_cm1": 22.0,
        "fwhm_min": 6.0,
        "fwhm_max": 180.0,
        "lock_fwhm_equal": False,
        "resid_bg_mode": "None (Fixed 0)",
    }

if "ftir_style_cfg" not in st.session_state:
    st.session_state["ftir_style_cfg"] = {
        "title": "",
        "xlabel": r"$\mathbf{Wavenumber\ (cm^{-1})}$",
        "ylabel": r"$\mathbf{Absorbance\ (a.u.)}$",
        "resid_ylabel": r"$\mathbf{Residual}$",
        "raw_label": "Observed Absorbance",
        "bg_label": "Stripped Baseline",
        "env_label": "Total Band Envelope",
        "peak_label_mode": "Band + cm⁻¹ + Area%",
        "invert_x": True,
        "show_legend": True,
        "legend_loc": "upper right",
        "legend_frame": True,
        "legend_cols": 1,
        "show_residual": True,
        "show_stats_box": True,
        "title_size": 14,
        "axis_label_size": 13,
        "tick_size": 11,
        "legend_size": 9,
        "annot_size": 8,
        "fig_width": 9.2,
        "fig_height": 6.4,
        "line_width": 1.8,
        "x_min": None,
        "x_max": None,
    }


# ==============================================================================
# SIDEBAR: AUTHORSHIP, DOMAIN & WORKSPACE CONTROLS
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="profile-card">
        <div style="display: flex; align-items: center; gap: 9px;">
            <div style="font-size: 1.5rem;">🧪</div>
            <div>
                <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700;">Lead Author & Architect</div>
                <div style="font-size: 1.18rem; font-weight: 800; color: #38bdf8; line-height: 1.2;">Dr. Deler Langenberg</div>
            </div>
        </div>
        <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 7px;">
            FTIR Studio • Vibrational Deconvolution, ATR & Cyclization Intelligence
        </div>
        <div style="display: flex; gap: 6px; margin-top: 9px;">
            <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="text-decoration: none; background: #334155; color: #f8fafc; padding: 3px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">GitHub</a>
            <a href="mailto:delerla@yahoo.de" style="text-decoration: none; background: #0284c7; color: #ffffff; padding: 3px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">Email</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. Materials Domain & Band Preset")
    selected_domain = st.selectbox("Research Class:", DOMAIN_OPTIONS, key="ftir_domain_select")
    domain_presets = ALL_FTIR_DOMAINS[selected_domain]
    selected_preset_name = st.selectbox("Material Chemistry Preset:", list(domain_presets.keys()), key="ftir_preset_select")
    active_preset = domain_presets[selected_preset_name]

    with st.expander("🇸🇦 Saudi Alliance Databank (KFUPM, KACST, KAUST, IAU)", expanded=False):
        sq = st.text_input("🔍 Filter Materials / Literature:", placeholder="UiO-66, Perovskite, TiO2, MXene...", key="ftir_saudi_sq")
        inst_choice = st.selectbox(
            "Institution Focus:",
            ["All Saudi Alliance Partners", "KAUST", "KFUPM", "KACST", "IAU (iau.edu.sa)"],
            key="ftir_saudi_inst"
        )
        sub_code = inst_choice.split()[0] if "All" not in inst_choice else ""
        from knowledge_base.saudi_research_databank import search_saudi_databank
        bms = search_saudi_databank(query=sq, institution=sub_code, technique="FTIR")
        if bms:
            bm_titles = [f"{b['material_name']} ({'/'.join(b['institutions'])})" for b in bms]
            sel_idx = st.selectbox("Institutional References:", range(len(bm_titles)), format_func=lambda i: bm_titles[i], key="ftir_saudi_bm_select")
            active_saudi_bm = bms[sel_idx]
            st.markdown(f"**Pillar:** *{active_saudi_bm['pillar']}*")
            st.markdown(f"**Partners:** {', '.join(active_saudi_bm['institutions'])}")
            st.caption(f"**Key Citation:** {active_saudi_bm['primary_citation']}")
            with st.expander("📖 Expected FTIR Vibrational Bands", expanded=False):
                if "ftir_benchmarks" in active_saudi_bm:
                    for b in active_saudi_bm["ftir_benchmarks"].get("bands", []):
                        st.markdown(f"- **{b.get('mode')}**: `{b.get('wavenumber'):.0f} cm⁻¹` • *{b.get('diagnostic', '')}*")
                    st.caption(active_saudi_bm["ftir_benchmarks"].get("diagnostic", ""))
        else:
            st.caption("No matching benchmarks found.")

    st.markdown("### 2. Spectrum Data Source")
    uploaded_file = st.file_uploader(
        "Upload FTIR Spectrum (CSV, DPT, ASC, DAT, TXT, Excel):",
        type=["csv", "txt", "dat", "dpt", "asc", "xlsx", "xls"],
        key="ftir_uploader",
    )

    if uploaded_file is not None:
        df_active, _, _ = _cached_parse_file(uploaded_file.getvalue(), uploaded_file.name)
        if df_active is None or df_active.empty or df_active.shape[1] < 2:
            st.error("Could not extract Wavenumber & Signal columns. Loading domain benchmark instead.")
            df_active = _cached_benchmark_ftir(selected_preset_name)
        else:
            st.success(f"Loaded: {uploaded_file.name} ({len(df_active)} pts, {df_active.shape[1] - 1} spectrum/a)")
    else:
        df_active = _cached_benchmark_ftir(selected_preset_name)
        st.caption(f"⚡ Simulated multi-sample benchmark for `{selected_preset_name}`")

    selected_theme = st.selectbox("Publication Theme:", list(PUBLICATION_PALETTES.keys()), index=0, key="ftir_theme")


# ==============================================================================
# MAIN WORKSPACE HEADER
# ==============================================================================
try:
    st.page_link("app.py", label="← Return to Materials Characterization Master Gateway", icon="🏠")
except Exception:
    st.markdown('<a href="https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding: 7px 16px; margin-bottom: 12px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #38bdf8 !important; border: 1px solid #334155; border-radius: 6px; text-decoration: none !important; font-weight: 600; font-size: 0.88rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">🏠 ⟵ Return to Master Materials Characterization Gateway</a>', unsafe_allow_html=True)
st.markdown('<div class="ftir-header">🧪 FTIR Studio: Vibrational Deconvolution & Chemical Intelligence</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="margin-bottom: 1.0rem;">
    <span class="badge badge-dark">{selected_domain}</span>
    <span class="badge badge-blue">{active_preset['material_class']}</span>
    <span class="badge badge-green">Apply-Driven • ATR / CO₂ / 2nd-Deriv Ready</span>
</div>
""", unsafe_allow_html=True)

sample_columns = list(df_active.columns[1:])
wn_full = df_active.iloc[:, 0].to_numpy(dtype=float)

preset_sig = f"{selected_domain}::{selected_preset_name}"
if st.session_state.get("ftir_band_sig") != preset_sig:
    st.session_state["ftir_band_df"] = _preset_to_band_df(active_preset["bands"])
    st.session_state["ftir_band_sig"] = preset_sig
    roi_def = active_preset.get("roi_window", (450.0, 3800.0))
    st.session_state["ftir_physics_cfg"]["roi_min"] = float(min(roi_def))
    st.session_state["ftir_physics_cfg"]["roi_max"] = float(max(roi_def))
    st.session_state["ftir_physics_cfg"]["line_shape_mode"] = active_preset.get("default_line_shape", "Gaussian")
    st.session_state.pop("ftir_fit_cache", None)
    st.session_state.pop("ftir_export_cache", None)

tab_deconv, tab_stacked = st.tabs([
    "🔬 Quantitative ROI Deconvolution & 2nd-Derivative Lab",
    "📚 Multi-Sample Stacked Transmittance / Absorbance Waterfall",
])


# ==============================================================================
# TAB 1: QUANTITATIVE ROI DECONVOLUTION & 2ND DERIVATIVE
# ==============================================================================
with tab_deconv:
    active_sample_col = st.selectbox(
        "Select Target Spectrum for ROI Band Deconvolution:",
        sample_columns,
        index=len(sample_columns) - 1 if len(sample_columns) > 1 else 0,
        key="ftir_active_sample",
    )

    y_col_raw = df_active[active_sample_col].to_numpy(dtype=float)
    valid_mask = np.isfinite(wn_full) & np.isfinite(y_col_raw)
    x_clean = wn_full[valid_mask]
    y_clean = y_col_raw[valid_mask]

    # 1. SPECTROSCOPIC PHYSICS & BASELINE FORM (APPLY BUTTON)
    with st.expander("⚙️ Beer–Lambert Scale, ATR/CO₂ Cleaning & Baseline Engine (Click Apply)", expanded=False):
        with st.form("ftir_physics_form"):
            pc = st.session_state["ftir_physics_cfg"]
            c1, c2, c3 = st.columns(3)
            with c1:
                scale_opts = ["Auto-Detect", "Transmittance (%T)", "Absorbance (A)"]
                input_scale = st.selectbox("Raw Data Scale:", scale_opts, index=scale_opts.index(pc["input_scale"]) if pc["input_scale"] in scale_opts else 0)
                mask_co2 = st.checkbox("Remove Atmospheric CO₂ Artifact (2390–2295 cm⁻¹)", value=bool(pc["mask_co2"]))
                atr_correct = st.checkbox("Apply ATR Penetration-Depth Correction (× ν/1000)", value=bool(pc["atr_correct"]))
            with c2:
                bg_opts = ["AsLS (Asymmetric Least Squares)", "Rubberband (Convex Hull)", "Linear Endpoints", "Constant Min", "None (Zero Baseline)"]
                bg_method = st.selectbox("Baseline Engine:", bg_opts, index=bg_opts.index(pc["bg_method"]) if pc["bg_method"] in bg_opts else 0)
                ba, bb = st.columns(2)
                with ba:
                    asls_log_lam = st.number_input("AsLS Smooth log₁₀(λ):", value=float(pc["asls_log_lam"]), min_value=3.0, max_value=9.0, step=0.5)
                with bb:
                    asls_p = st.number_input("AsLS Asymmetry p:", value=float(pc["asls_p"]), min_value=0.0005, max_value=0.1, step=0.001, format="%.4f")
                sg_window = st.number_input("Savitzky–Golay Smooth Window (0 = Off):", value=int(pc["sg_window"]), min_value=0, max_value=35, step=2)
            with c3:
                ls_opts = ["Gaussian", "Lorentzian", "Pseudo-Voigt", "Voigt"]
                line_shape_mode = st.selectbox("Default Band Shape:", ls_opts, index=ls_opts.index(pc["line_shape_mode"]) if pc["line_shape_mode"] in ls_opts else 0)
                ra, rb = st.columns(2)
                with ra:
                    roi_min = st.number_input("ROI Min (cm⁻¹):", value=float(pc["roi_min"]), step=50.0)
                with rb:
                    roi_max = st.number_input("ROI Max (cm⁻¹):", value=float(pc["roi_max"]), step=50.0)
                resid_bg_mode = st.selectbox("Residual Local Baseline:", ["None (Fixed 0)", "Constant", "Linear"], index=0)

            b1, b2, b3, b4 = st.columns(4)
            with b1:
                center_tol_cm1 = st.number_input("Center Drift Tol (±cm⁻¹):", value=float(pc["center_tol_cm1"]), min_value=2.0, max_value=120.0, step=2.0)
            with b2:
                fwhm_min = st.number_input("Min FWHM (cm⁻¹):", value=float(pc["fwhm_min"]), min_value=2.0, max_value=40.0, step=1.0)
            with b3:
                fwhm_max = st.number_input("Max FWHM (cm⁻¹):", value=float(pc["fwhm_max"]), min_value=20.0, max_value=400.0, step=10.0)
            with b4:
                st.markdown("<br>", unsafe_allow_html=True)
                lock_fwhm_equal = st.checkbox("Lock Equal Band FWHM", value=bool(pc["lock_fwhm_equal"]))

            if st.form_submit_button("⚡ Apply Physics, Baseline & Run Fit", type="primary", use_container_width=True):
                st.session_state["ftir_physics_cfg"].update({
                    "input_scale": input_scale,
                    "mask_co2": mask_co2,
                    "atr_correct": atr_correct,
                    "sg_window": sg_window,
                    "bg_method": bg_method,
                    "asls_log_lam": asls_log_lam,
                    "asls_p": asls_p,
                    "line_shape_mode": line_shape_mode,
                    "roi_min": roi_min,
                    "roi_max": roi_max,
                    "center_tol_cm1": center_tol_cm1,
                    "fwhm_min": fwhm_min,
                    "fwhm_max": fwhm_max,
                    "lock_fwhm_equal": lock_fwhm_equal,
                    "resid_bg_mode": resid_bg_mode,
                })
                st.session_state["ftir_trigger_fit"] = True

    # 2. BAND SETUP, 2ND-DERIVATIVE AUTO-SEED & TABLE (APPLY BUTTON)
    with st.expander("Vibrational Band Configuration & Auto-Finder (Add / Delete / Fix ν)", expanded=False):
        ad1, ad2, ad3, ad4 = st.columns([1.1, 1.1, 1.0, 1.5])
        with ad1:
            prom_pct = st.number_input("Auto-Seed Prominence (%):", value=5.0, min_value=1.0, max_value=40.0, step=1.0)
        with ad2:
            min_dist_cm1 = st.number_input("Min Spacing (cm⁻¹):", value=22.0, min_value=5.0, max_value=150.0, step=2.0)
        with ad3:
            use_d2_seed = st.checkbox("Use 2nd-Deriv (-d²A/dν²) Shoulders", value=False)
        with ad4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Auto-Detect Bands in ROI", use_container_width=True):
                pcfg = st.session_state["ftir_physics_cfg"]
                y_a, _ = convert_ir_scale(y_clean, source_scale=pcfg["input_scale"], target_scale="Absorbance (A)")
                lo_r, hi_r = min(pcfg["roi_min"], pcfg["roi_max"]), max(pcfg["roi_min"], pcfg["roi_max"])
                m_r = (x_clean >= lo_r) & (x_clean <= hi_r)
                xr = x_clean[m_r] if np.sum(m_r) > 10 else x_clean
                ya_r = y_a[m_r] if np.sum(m_r) > 10 else y_a
                ynet_r, _ = extract_net_absorbance(xr, ya_r, method=pcfg["bg_method"])
                detected = auto_detect_ir_bands(xr, ynet_r, min_prominence_pct=prom_pct, min_distance_cm1=min_dist_cm1, use_second_deriv=use_d2_seed)
                st.session_state["ftir_band_df"] = _preset_to_band_df(detected)
                st.session_state["ftir_trigger_fit"] = True
                st.rerun()

        edited_band_df = st.data_editor(
            st.session_state["ftir_band_df"],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Label": st.column_config.TextColumn("Band Label"),
                "Mode": st.column_config.TextColumn("Vibrational Mode"),
                "Center (cm⁻¹)": st.column_config.NumberColumn("Center (cm⁻¹)", min_value=200.0, max_value=4500.0, format="%.1f"),
                "FWHM Init (cm⁻¹)": st.column_config.NumberColumn("Init FWHM (cm⁻¹)", min_value=2.0, max_value=400.0, format="%.1f"),
                "Shape": st.column_config.SelectboxColumn("Shape", options=["Auto", "Gaussian", "Lorentzian", "Pseudo-Voigt", "Voigt"]),
                "Fix ν": st.column_config.CheckboxColumn("Lock ν?"),
                "Color": st.column_config.TextColumn("Hex Color"),
                "Assignment": st.column_config.TextColumn("Chemical Assignment"),
            },
            key="ftir_band_editor",
        )
        b_col1, b_col2 = st.columns([3, 1])
        with b_col1:
            if st.button("🚀 Apply Band Setup & Run Fit", type="primary", use_container_width=True):
                st.session_state["ftir_band_df"] = edited_band_df
                st.session_state["ftir_trigger_fit"] = True
        with b_col2:
            if st.button("↺ Reset Domain Bands", use_container_width=True):
                st.session_state["ftir_band_df"] = _preset_to_band_df(active_preset["bands"])
                st.session_state["ftir_trigger_fit"] = True
                st.rerun()

    # 3. EDITABLE TYPOGRAPHY & STYLE FORM (APPLY BUTTON)
    with st.expander("🎨 Editable Typography, Axis Labels, Wavenumber Direction & Legend (Click Apply)", expanded=False):
        with st.form("ftir_style_form"):
            sc = st.session_state["ftir_style_cfg"]
            t1, t2, t3 = st.columns(3)
            with t1:
                st_title = st.text_input("Figure Title:", value=sc["title"], placeholder="e.g. FTIR Deconvolution of PAN Nanofibers")
                st_xlabel = st.text_input("X-Axis Label:", value=sc["xlabel"])
                st_ylabel = st.text_input("Y-Axis Label:", value=sc["ylabel"])
                st_res_y = st.text_input("Residual Y Label:", value=sc["resid_ylabel"])
            with t2:
                st_raw_lbl = st.text_input("Observed Legend:", value=sc["raw_label"])
                st_bg_lbl = st.text_input("Baseline Legend:", value=sc["bg_label"])
                st_env_lbl = st.text_input("Envelope Legend:", value=sc["env_label"])
                pk_modes = ["Band + cm⁻¹ + Area%", "Band + cm⁻¹", "Band Name Only", "Wavenumber Only", "None"]
                st_pk_mode = st.selectbox("Band Callout Format:", pk_modes, index=pk_modes.index(sc["peak_label_mode"]) if sc["peak_label_mode"] in pk_modes else 0)
            with t3:
                loc_opts = ["upper right", "upper left", "best", "lower right", "lower left"]
                st_leg_loc = st.selectbox("Legend Position:", loc_opts, index=loc_opts.index(sc["legend_loc"]) if sc["legend_loc"] in loc_opts else 0)
                f1, f2 = st.columns(2)
                with f1:
                    st_fig_w = st.number_input("Fig Width (in):", value=float(sc["fig_width"]), min_value=5.0, max_value=16.0, step=0.2)
                    st_ax_fs = st.number_input("Axis Label pt:", value=int(sc["axis_label_size"]), min_value=8, max_value=24, step=1)
                    st_leg_fs = st.number_input("Legend pt:", value=int(sc["legend_size"]), min_value=6, max_value=18, step=1)
                with f2:
                    st_fig_h = st.number_input("Fig Height (in):", value=float(sc["fig_height"]), min_value=3.5, max_value=14.0, step=0.2)
                    st_tk_fs = st.number_input("Tick Font pt:", value=int(sc["tick_size"]), min_value=7, max_value=20, step=1)
                    st_ann_fs = st.number_input("Callout pt:", value=int(sc["annot_size"]), min_value=6, max_value=16, step=1)

            z1, z2, z3, z4, z5 = st.columns(5)
            with z1:
                st_inv_x = st.checkbox("Descending ν (4000→400)", value=bool(sc["invert_x"]))
            with z2:
                st_show_leg = st.checkbox("Show Legend", value=bool(sc["show_legend"]))
            with z3:
                st_leg_frame = st.checkbox("Legend Box", value=bool(sc["legend_frame"]))
            with z4:
                st_show_res = st.checkbox("Residual Panel", value=bool(sc["show_residual"]))
            with z5:
                st_stats_box = st.checkbox("Stats Inset", value=bool(sc["show_stats_box"]))

            if st.form_submit_button("🎨 Apply Figure Style & Typography", use_container_width=True):
                st.session_state["ftir_style_cfg"].update({
                    "title": st_title,
                    "xlabel": st_xlabel,
                    "ylabel": st_ylabel,
                    "resid_ylabel": st_res_y,
                    "raw_label": st_raw_lbl,
                    "bg_label": st_bg_lbl,
                    "env_label": st_env_lbl,
                    "peak_label_mode": st_pk_mode,
                    "legend_loc": st_leg_loc,
                    "fig_width": st_fig_w,
                    "fig_height": st_fig_h,
                    "axis_label_size": st_ax_fs,
                    "tick_size": st_tk_fs,
                    "legend_size": st_leg_fs,
                    "annot_size": st_ann_fs,
                    "invert_x": st_inv_x,
                    "show_legend": st_show_leg,
                    "legend_frame": st_leg_frame,
                    "show_residual": st_show_res,
                    "show_stats_box": st_stats_box,
                })
                st.session_state.pop("ftir_export_cache", None)

    # RUN FIT ONLY WHEN TRIGGERED OR SAMPLE CHANGES
    fit_cache_key = f"{preset_sig}::{active_sample_col}::{len(x_clean)}"
    need_fit = (
        st.session_state.pop("ftir_trigger_fit", False)
        or "ftir_fit_cache" not in st.session_state
        or st.session_state["ftir_fit_cache"].get("cache_key") != fit_cache_key
    )
    if need_fit:
        with st.spinner("Running vibrational band deconvolution & chemical diagnostics..."):
            try:
                fc_new = _compute_and_store_ir_fit(
                    x_clean, y_clean,
                    phys=st.session_state["ftir_physics_cfg"],
                    band_df=st.session_state["ftir_band_df"],
                    active_preset=active_preset,
                    preset_name=selected_preset_name,
                    domain_choice=selected_domain,
                    sample_name=active_sample_col,
                )
                fc_new["cache_key"] = fit_cache_key
                st.session_state["ftir_fit_cache"] = fc_new
                st.session_state.pop("ftir_export_cache", None)
            except Exception as err:
                st.error(f"FTIR Deconvolution Error: {err}")

    # RENDER FROM CACHED FIT
    if "ftir_fit_cache" in st.session_state:
        fc = st.session_state["ftir_fit_cache"]
        st.caption(f"⚡ Source detected as `{fc['detected_src']}` → converted to Absorbance | Profile = {fc['line_shape_mode']}")

        plot_cfg = dict(st.session_state["ftir_style_cfg"])
        plot_cfg["screen_dpi"] = 130
        plot_cfg["stats_extras"] = {"r2": fc["r2"], "rmse": fc["rmse"]}

        fig_ir, labplot_df = render_ftir_deconvolution_plot(
            fc["x_roi"],
            fc["y_abs_roi"],
            fc["bg_curve"],
            fc["fit_result"],
            fc["comp_curves"],
            fc["band_summary"],
            preset_bands=fc["active_preset"].get("bands"),
            theme=selected_theme,
            plot_config=plot_cfg,
        )
        st.pyplot(fig_ir)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fit R²", f"{fc['r2']:.5f}")
        m2.metric("Fit RMSE (A)", f"{fc['rmse']:.4f}")
        m3.metric("Active IR Bands", f"{len(fc['band_summary'])}")
        m4.metric("ROI Span", f"{int(fc['x_roi'].max())}–{int(fc['x_roi'].min())} cm⁻¹")

        diag = interpret_ftir_chemistry(
            fc["band_summary"],
            domain_key=fc["domain_choice"],
            preset_dict=fc["active_preset"],
            wavenumber_full=fc["x_full"],
            absorbance_full=fc["y_abs_full_net"],
        )

        st.markdown("### 🧠 Automated Vibrational Chemistry Reasoning")
        if diag["metrics"]:
            d_cols = st.columns(len(diag["metrics"]))
            for idx_m, (_, mv) in enumerate(diag["metrics"].items()):
                with d_cols[idx_m]:
                    st.metric(mv["name"], f"{mv['value']:.2f} {mv['unit']}".strip())

        if diag["insights"]:
            st.markdown('<div class="insight-card">', unsafe_allow_html=True)
            for ins in diag["insights"]:
                st.markdown(f"**✓ Chemical Insight:** {ins}")
            st.markdown("</div>", unsafe_allow_html=True)

        if diag["warnings"]:
            for w_txt in diag["warnings"]:
                st.markdown(f'<div class="warning-box">⚠️ <b>Spectral Notice:</b> {w_txt}</div>', unsafe_allow_html=True)

        col_tbl, col_d2 = st.columns([1.45, 1.0])
        with col_tbl:
            st.markdown("#### 📊 Deconvolved Vibrational Band Table")
            rows = []
            for b_name, d in fc["band_summary"].items():
                rows.append({
                    "Band": b_name,
                    "Mode": d["Mode"],
                    "Center (cm⁻¹)": d["Wavenumber_cm1"],
                    "FWHM (cm⁻¹)": d["FWHM_cm1"],
                    "Peak Height (A)": d["Peak_Absorbance"],
                    "Area %": f"{d['Area_Percent']:.2f}%",
                    "Assignment": d["Meaning"],
                })
            quant_df = pd.DataFrame(rows)
            st.dataframe(quant_df, use_container_width=True)

        with col_d2:
            st.markdown("#### 🔎 2nd-Derivative Shoulder Resolver")
            fig_d2 = render_second_derivative_plot(
                fc["x_roi"],
                fc["y_net"],
                invert_x=bool(plot_cfg["invert_x"]),
                theme=selected_theme,
                screen_dpi=130,
            )
            st.pyplot(fig_d2)
            plt.close(fig_d2)

        # Saudi Research Alliance Cross-Auditing & Literature Verification
        saudi_verif = verify_against_saudi_databank(
            technique="FTIR",
            fitted_components=fc["band_summary"],
            material_hint=selected_preset_name
        )
        with st.expander(f"🏛️ Saudi Alliance Literature Benchmark: {saudi_verif['material_name']} ({saudi_verif['match_percentage']:.0f}% Match)", expanded=True):
            st.markdown(f"""
            <div style="background: #f8fafc; border-left: 5px solid {saudi_verif['verdict_color']}; padding: 10px 14px; border-radius: 6px; margin-bottom: 10px;">
                <span style="font-weight: 700; color: {saudi_verif['verdict_color']}; font-size: 1.0rem;">Audit: {saudi_verif['verdict']}</span> 
                <span style="font-size: 0.85rem; color: #64748b;">({saudi_verif['matched_count']}/{saudi_verif['total_ref_count']} verified vibrational bands, {saudi_verif['match_percentage']:.0f}% literature fidelity)</span><br>
                <span style="font-size: 0.88rem; color: #1e293b; line-height: 1.45;">{saudi_verif['explanation']}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Research Centers:** {', '.join(saudi_verif['institutions'])} | **Pillar:** *{saudi_verif['pillar']}*")
            st.caption(f"**Primary Reference:** {saudi_verif['primary_citation']}")
            if saudi_verif['matches']:
                st.markdown("##### Correlated Literature Vibrational Modes")
                m_df = pd.DataFrame(saudi_verif['matches'])
                m_df.columns = ["Vibrational Mode", "Literature ν (cm⁻¹)", "Measured ν (cm⁻¹)", "Deviation |Δν| (cm⁻¹)", "Audit Status"]
                st.dataframe(m_df, use_container_width=True)

        with st.expander("🔍 Search Full Saudi Alliance Literature & Peak Databank (KFUPM · KACST · KAUST · IAU)", expanded=False):
            from modules.saudi_search_ui import render_saudi_alliance_explorer
            render_saudi_alliance_explorer(active_technique="FTIR")

        # ----------------------------------------------------------------------
        # PUBLICATION EXPORT CENTER
        # ----------------------------------------------------------------------
        st.markdown("#### 📥 Publication Export Center")
        slug = fc["sample_name"].replace(" ", "_").replace("/", "_")
        zip_bytes = build_analysis_bundle_zip(
            fig_ir,
            base_name=f"FTIR_{slug}",
            labplot_df=labplot_df,
            summary_data=quant_df,
            title=plot_cfg["title"] or f"FTIR Deconvolution: {fc['sample_name']}",
            units={"Wavenumber_cm-1": "cm-1", "Observed_Absorbance": "a.u."},
        )
        st.download_button(
            "📦 Download Complete FTIR Publication Package (.ZIP: OriginLab, LabPlot, PNG, SVG, PDF)",
            data=zip_bytes,
            file_name=f"FTIR_{slug}_Publication_Bundle.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
            key="dl_ftir_zip",
        )

        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
            st.download_button(
                "📊 Export OriginLab Matrix (.dat)",
                data=get_originlab_ascii_bytes(labplot_df, title="FTIR Studio Matrix", units={"Wavenumber_cm-1": "cm-1", "Observed_Absorbance": "a.u."}),
                file_name=f"FTIR_{slug}_OriginLab.dat",
                mime="text/plain",
                use_container_width=True,
                key="ftir_origin_dat",
                help="OriginLab-compatible ASCII matrix with A(X), B(Y) column designations for direct drag & drop."
            )
            st.download_button(
                "📗 Export OriginLab Workbook (.xlsx)",
                data=get_originlab_excel_bytes(labplot_df, title="FTIR Studio Matrix", units={"Wavenumber_cm-1": "cm-1", "Observed_Absorbance": "a.u."}),
                file_name=f"FTIR_{slug}_OriginLab.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="ftir_origin_xlsx",
                help="OriginLab-ready Excel workbook with 4-tier metadata header."
            )
            st.download_button(
                "📈 Export LabPlot Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_df, title="FTIR Studio Matrix"),
                file_name=f"FTIR_{slug}_LabPlot.dat",
                mime="text/plain",
                use_container_width=True,
                key="ftir_labplot_dat",
                help="LabPlot ASCII data table with metadata header."
            )
        with c_right:
            st.markdown("**🖼️ Publication Graphics:**")
            st.download_button("🖼️ Export 600 DPI PNG", data=get_figure_bytes(fig_ir, "png", dpi=600), file_name=f"FTIR_{slug}_600DPI.png", mime="image/png", use_container_width=True, key="ftir_png")
            st.download_button("📐 Export Vector SVG", data=get_figure_bytes(fig_ir, "svg"), file_name=f"FTIR_{slug}.svg", mime="image/svg+xml", use_container_width=True, key="ftir_svg")
            st.download_button("📄 Export Vector PDF", data=get_figure_bytes(fig_ir, "pdf"), file_name=f"FTIR_{slug}.pdf", mime="application/pdf", use_container_width=True, key="ftir_pdf")

        plt.close(fig_ir)


# ==============================================================================
# TAB 2: MULTI-SAMPLE STACKED WATERFALL COMPARISON
# ==============================================================================
with tab_stacked:
    with st.form("ftir_stacked_form"):
        st.markdown("Configure full-spectrum FTIR waterfall stacking, display scale (`%T` or `Absorbance`), and labels, then click **Apply Stacked Plot**.")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            sel_cols_stack = st.multiselect("Spectra to Stack:", sample_columns, default=sample_columns)
            disp_mode_stack = st.selectbox("Display Y-Scale:", ["Transmittance (%T)", "Absorbance (A)"])
        with s2:
            norm_stack = st.selectbox("Normalization:", ["None", "Min-Max (0 to 1)", "Zero Baseline"])
            strip_stack_bg = st.checkbox("Strip AsLS Baseline First", value=False)
            atr_stack = st.checkbox("Apply ATR Correction", value=False)
        with s3:
            offset_stack = st.number_input("Vertical Offset (0 = Auto):", value=0.0, min_value=0.0, step=5.0)
            sg_stack = st.number_input("Savitzky–Golay Window:", value=9, min_value=0, max_value=31, step=2)
            ann_peaks_stack = st.checkbox("Annotate Peak Wavenumbers", value=True)
        with s4:
            stack_title = st.text_input("Waterfall Title:", value="")
            stack_legend_raw = st.text_input("Custom Legend Names (comma-sep):", value=", ".join(sample_columns))
            prom_stack = st.number_input("Peak Tag Prominence (%):", value=7.0, min_value=1.0, max_value=40.0, step=1.0)

        st.form_submit_button("📚 Apply Stacked Plot", type="primary", use_container_width=True)

    custom_map = {}
    parsed_names = [s.strip() for s in stack_legend_raw.split(",") if s.strip()]
    for idx_s, orig_c in enumerate(sel_cols_stack):
        custom_map[orig_c] = parsed_names[idx_s] if idx_s < len(parsed_names) else orig_c

    if sel_cols_stack:
        stack_cfg = dict(st.session_state["ftir_style_cfg"])
        stack_cfg["title"] = stack_title
        stack_cfg["screen_dpi"] = 130
        stack_cfg["ylabel"] = (
            r"$\mathbf{Absorbance\ (a.u.)}$" if "Absorbance" in disp_mode_stack else r"$\mathbf{Transmittance\ (\%)}$"
        )

        fig_stack, stack_lab_df, det_peaks_map = render_ftir_stacked_plot(
            df_active,
            selected_cols=sel_cols_stack,
            custom_labels=custom_map,
            display_mode=disp_mode_stack,
            normalize_mode=norm_stack,
            offset_step=float(offset_stack),
            sg_window=int(sg_stack),
            mask_co2=bool(st.session_state["ftir_physics_cfg"]["mask_co2"]),
            atr_correct=atr_stack,
            strip_baseline=strip_stack_bg,
            annotate_peaks=ann_peaks_stack,
            prominence_pct=float(prom_stack),
            theme=selected_theme,
            plot_config=stack_cfg,
        )
        st.pyplot(fig_stack)

        with st.expander("📋 Auto-Detected Wavenumbers per Spectrum (cm⁻¹)", expanded=False):
            for s_lbl, wn_list in det_peaks_map.items():
                st.write(f"**{s_lbl}:** {', '.join(str(int(round(v))) for v in wn_list) or 'None'}")

        st.markdown("#### 📥 Stacked Waterfall Export Center")
        d_left, d_right = st.columns(2)
        with d_left:
            st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
            st.download_button(
                "📊 Export OriginLab .DAT (Stacked)",
                data=get_originlab_ascii_bytes(stack_lab_df, title="FTIR Stacked Waterfall Matrix", units={"Wavenumber_cm-1": "cm-1"}),
                file_name="FTIR_Stacked_OriginLab.dat",
                mime="text/plain",
                use_container_width=True,
                key="ftir_stack_origin_dat"
            )
            st.download_button(
                "📗 Export OriginLab .XLSX (Stacked)",
                data=get_originlab_excel_bytes(stack_lab_df, title="FTIR Stacked Waterfall Matrix", units={"Wavenumber_cm-1": "cm-1"}),
                file_name="FTIR_Stacked_OriginLab.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="ftir_stack_origin_xlsx"
            )
            st.download_button(
                "📈 Export LabPlot .DAT (Stacked)",
                data=get_labplot_ascii_bytes(stack_lab_df, title="FTIR Stacked Waterfall Matrix"),
                file_name="FTIR_Stacked_LabPlot.dat",
                mime="text/plain",
                use_container_width=True,
                key="ftir_stack_labplot_dat"
            )
        with d_right:
            st.markdown("**🖼️ Publication Graphics:**")
            st.download_button("🖼️ Export 600 DPI PNG (Stacked)", data=get_figure_bytes(fig_stack, "png", dpi=600), file_name="FTIR_Stacked_600DPI.png", mime="image/png", use_container_width=True, key="ftir_stack_png")
            st.download_button("📐 Export Vector SVG (Stacked)", data=get_figure_bytes(fig_stack, "svg"), file_name="FTIR_Stacked.svg", mime="image/svg+xml", use_container_width=True, key="ftir_stack_svg")
        plt.close(fig_stack)
    else:
        st.warning("Select at least one spectrum column above to render the stacked waterfall.")


# ==============================================================================
# COMMUNITY REVIEWS, USER WISHES & PEER FEEDBACK
# ==============================================================================
from modules.feedback_module import render_community_reviews
render_community_reviews(active_app_name="FTIR Studio")

# ==============================================================================
# INSTITUTIONAL FOOTER
# ==============================================================================
st.markdown("""
<div style="margin-top: 3.5rem; padding-top: 1.2rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.83rem; line-height: 1.6;">
    <strong>FTIR Studio</strong> • Vibrational Deconvolution, ATR Correction & Chemical State Intelligence<br>
    Engineered & Maintained by <strong>Dr. Deler Langenberg</strong> •
    <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 600;">GitHub Repository</a> •
    <a href="mailto:delerla@yahoo.de" style="color: #0284c7; text-decoration: none; font-weight: 600;">Contact: delerla@yahoo.de</a><br>
    <small style="color: #94a3b8;">© 2026 Dr. Deler Langenberg (MIT License).</small>
</div>
""", unsafe_allow_html=True)
