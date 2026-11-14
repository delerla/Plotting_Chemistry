"""
app.py - XRD Studio: Lightweight, Apply-Driven Materials-Specific X-Ray Diffraction Intelligence
Authored & Maintained by Dr. Deler Langenberg (2026)
Dedicated for: MOFs & Frameworks, Solar Perovskites, Catalysts/Oxides, and Polymers/Carbons.
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
    from knowledge_base import (
        ALL_XRD_DOMAINS,
        ANODE_WAVELENGTHS,
        CALIBRATION_STANDARDS,
        DOMAIN_OPTIONS,
        INSTRUMENT_BROADENING_PRESETS,
    )
    from knowledge_base.benchmark_data import generate_benchmark_xrd
    from core.background import extract_net_pattern
    from core.calibration import apply_ka2_stripping, apply_two_theta_calibration
    from core.peak_fitting import auto_detect_xrd_peaks, fit_xrd_peaks
    from core.williamson_hall import compute_williamson_hall
    from core.interpretation import interpret_xrd_diagnostics
    from visualizer.plot_xrd import (
        render_williamson_hall_plot,
        render_xrd_deconvolution_plot,
        render_xrd_stacked_plot,
    )
    from knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        list_benchmarks_for_institution,
    )
    from modules.institutional_verifier import verify_against_saudi_databank
except ImportError:
    from xrd_studio.knowledge_base import (
        ALL_XRD_DOMAINS,
        ANODE_WAVELENGTHS,
        CALIBRATION_STANDARDS,
        DOMAIN_OPTIONS,
        INSTRUMENT_BROADENING_PRESETS,
    )
    from xrd_studio.knowledge_base.benchmark_data import generate_benchmark_xrd
    from xrd_studio.core.background import extract_net_pattern
    from xrd_studio.core.calibration import apply_ka2_stripping, apply_two_theta_calibration
    from xrd_studio.core.peak_fitting import auto_detect_xrd_peaks, fit_xrd_peaks
    from xrd_studio.core.williamson_hall import compute_williamson_hall
    from xrd_studio.core.interpretation import interpret_xrd_diagnostics
    from xrd_studio.visualizer.plot_xrd import (
        render_williamson_hall_plot,
        render_xrd_deconvolution_plot,
        render_xrd_stacked_plot,
    )
    from xrd_studio.knowledge_base.saudi_research_databank import (
        SAUDI_INSTITUTIONS,
        SAUDI_RESEARCH_BENCHMARKS,
        list_benchmarks_for_institution,
    )
    from xrd_studio.modules.institutional_verifier import verify_against_saudi_databank


st.set_page_config(
    page_title="XRD Studio - Dr. Deler Langenberg",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lightweight System CSS (No external network latency)
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    .xrd-header {
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
def _cached_benchmark_xrd(preset_name: str):
    return generate_benchmark_xrd(preset_name)


def _preset_to_peak_df(preset_peaks: list) -> pd.DataFrame:
    rows = []
    for idx, p in enumerate(preset_peaks):
        rows.append({
            "Label": str(p.get("label", f"Peak {idx + 1}")),
            "hkl": str(p.get("hkl", "")),
            "Center (2θ°)": round(float(p.get("center", 25.0)), 3),
            "FWHM Init (°)": round(float(p.get("fwhm", 0.30)), 3),
            "Shape": "Auto",
            "Fix 2θ": False,
            "Color": str(p.get("color", DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])),
            "Phase / Note": str(p.get("meaning", "Bragg reflection")),
        })
    return pd.DataFrame(rows)


def _compute_and_store_fit(
    x_raw: np.ndarray,
    y_raw_in: np.ndarray,
    phys: dict,
    peak_df: pd.DataFrame,
    active_preset: dict,
    preset_name: str,
    domain_choice: str,
    sample_name: str,
):
    """Runs K-alpha2 stripping, 2-theta calibration, baseline stripping, lmfit deconvolution & W-H analysis."""
    # Restrict fitting window
    w_min = float(phys["fit_win_min"])
    w_max = float(phys["fit_win_max"])
    mask_win = (x_raw >= w_min) & (x_raw <= w_max)
    if np.sum(mask_win) < 15:
        x_w, y_w = x_raw.copy(), y_raw_in.copy()
    else:
        x_w, y_w = x_raw[mask_win], y_raw_in[mask_win]

    # Sort ascending 2-theta
    ord_i = np.argsort(x_w)
    x_w = x_w[ord_i]
    y_w = y_w[ord_i]

    anode = ANODE_WAVELENGTHS.get(phys["anode_label"], list(ANODE_WAVELENGTHS.values())[0])
    lam_A = float(anode["lambda_A"]) if not phys["use_custom_lam"] else float(phys["custom_lam_A"])
    lam_nm = lam_A / 10.0

    # Optional K-alpha2 Rachinger stripping
    if phys["strip_ka2"] and float(anode.get("ka_ratio", 0.0)) > 0.0:
        y_proc = apply_ka2_stripping(
            x_w, y_w,
            lambda_a1=lam_A,
            lambda_a2=float(anode["ka2_A"]),
            ka_ratio=float(anode["ka_ratio"]),
        )
    else:
        y_proc = y_w.copy()

    # Optional 2-theta calibration
    calib_std = CALIBRATION_STANDARDS.get(phys["calib_std_label"])
    if phys["calib_mode"] == "None":
        x_calib, shift_applied, calib_status = x_w.copy(), 0.0, "Raw 2θ preserved (No alignment shift)"
    elif phys["calib_mode"] == "Manual Offset (Δ2θ)":
        x_calib, shift_applied, calib_status = apply_two_theta_calibration(
            x_w, 0.0, 0.0, mode="Manual", manual_shift_deg=float(phys["manual_shift_deg"])
        )
    else:
        target_val = float(phys["custom_target_2t"]) if calib_std == "custom" else float(calib_std or 28.443)
        x_calib, shift_applied, calib_status = apply_two_theta_calibration(
            x_w,
            measured_peak_deg=float(phys["measured_ref_2t"]),
            target_peak_deg=target_val,
            mode=phys["calib_mode"],
        )

    # Background stripping
    y_net, bg_curve = extract_net_pattern(
        x_calib,
        y_proc,
        method=phys["bg_method"],
        asls_lam=float(10 ** float(phys["asls_log_lam"])),
        asls_p=float(phys["asls_p"]),
        snip_window=int(phys["snip_window"]),
    )

    # Parse Peak Configs
    p_configs = []
    if peak_df is not None and not peak_df.empty:
        for _, row in peak_df.iterrows():
            lbl = str(row.get("Label", "")).strip()
            if not lbl:
                continue
            p_configs.append({
                "label": lbl,
                "hkl": str(row.get("hkl", "")),
                "center": float(row.get("Center (2θ°)", 25.0)),
                "fwhm": float(row.get("FWHM Init (°)", 0.30)),
                "shape": str(row.get("Shape", "Auto") or "Auto"),
                "fix_center": bool(row.get("Fix 2θ", False)),
                "color": str(row.get("Color", "#1f77b4")),
                "meaning": str(row.get("Phase / Note", "Bragg reflection")),
            })

    if not p_configs:
        p_configs = auto_detect_xrd_peaks(x_calib, y_net, min_prominence_pct=5.0, max_peaks=8)

    fit_res, comp_curves, peak_summary, r2, rwp = fit_xrd_peaks(
        x_calib,
        y_net,
        peak_configs=p_configs,
        wavelength_A=lam_A,
        wavelength_nm=lam_nm,
        k_factor=float(phys["k_scherrer"]),
        beta_inst_deg=float(phys["beta_inst_deg"]),
        broadening_mode=phys["broadening_mode"],
        line_shape_mode=phys["line_shape_mode"],
        center_tol_deg=float(phys["center_tol_deg"]),
        fwhm_bounds=(float(phys["fwhm_min"]), float(phys["fwhm_max"])),
        lock_fwhm_equal=bool(phys["lock_fwhm_equal"]),
        residual_baseline=phys["resid_bg_mode"],
    )

    wh_results = compute_williamson_hall(
        peak_summary,
        wavelength_nm=lam_nm,
        k_factor=float(phys["k_scherrer"]),
    )

    return {
        "x_calib": x_calib,
        "y_raw": y_proc,
        "y_net": y_net,
        "bg_curve": bg_curve,
        "fit_result": fit_res,
        "comp_curves": comp_curves,
        "peak_summary": peak_summary,
        "r2": r2,
        "rwp": rwp,
        "shift_applied": shift_applied,
        "calib_status": calib_status,
        "wh_results": wh_results,
        "lam_A": lam_A,
        "active_preset": active_preset,
        "preset_name": preset_name,
        "domain_choice": domain_choice,
        "sample_name": sample_name,
        "line_shape_mode": phys["line_shape_mode"],
    }


# ==============================================================================
# SESSION STATE DEFAULTS
# ==============================================================================
if "xrd_physics_cfg" not in st.session_state:
    st.session_state["xrd_physics_cfg"] = {
        "anode_label": "Cu Kα₁ (1.54060 Å)",
        "use_custom_lam": False,
        "custom_lam_A": 1.540598,
        "strip_ka2": False,
        "calib_mode": "None",
        "calib_std_label": "Si (111) Standard (28.443°)",
        "measured_ref_2t": 28.443,
        "custom_target_2t": 28.443,
        "manual_shift_deg": 0.0,
        "bg_method": "AsLS (Asymmetric Least Squares)",
        "asls_log_lam": 5.0,
        "asls_p": 0.004,
        "snip_window": 35,
        "line_shape_mode": "Pseudo-Voigt",
        "k_scherrer": 0.90,
        "beta_inst_deg": 0.05,
        "broadening_mode": "Gaussian Quadrature",
        "center_tol_deg": 0.70,
        "fwhm_min": 0.05,
        "fwhm_max": 6.00,
        "lock_fwhm_equal": False,
        "resid_bg_mode": "None (Fixed 0)",
        "fit_win_min": 5.0,
        "fit_win_max": 80.0,
    }

if "xrd_style_cfg" not in st.session_state:
    st.session_state["xrd_style_cfg"] = {
        "title": "",
        "xlabel": r"$\mathbf{2\theta\ (degrees)}$",
        "ylabel": r"$\mathbf{Intensity\ (a.u.)}$",
        "resid_ylabel": r"$\mathbf{Residual}$",
        "raw_label": "Observed Pattern",
        "bg_label": "Stripped Baseline",
        "env_label": "Total Profile Fit",
        "peak_label_mode": "hkl + 2θ + D (nm)",
        "show_hkl_ticks": True,
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
            <div style="font-size: 1.5rem;">💎</div>
            <div>
                <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; font-weight: 700;">Lead Author & Architect</div>
                <div style="font-size: 1.18rem; font-weight: 800; color: #38bdf8; line-height: 1.2;">Dr. Deler Langenberg</div>
            </div>
        </div>
        <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 7px;">
            XRD Studio • Crystallographic Deconvolution, Scherrer & Williamson–Hall Lab
        </div>
        <div style="display: flex; gap: 6px; margin-top: 9px;">
            <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="text-decoration: none; background: #334155; color: #f8fafc; padding: 3px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">GitHub</a>
            <a href="mailto:delerla@yahoo.de" style="text-decoration: none; background: #0284c7; color: #ffffff; padding: 3px 9px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">Email</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. Materials Domain & Phase")
    selected_domain = st.selectbox("Research Class:", DOMAIN_OPTIONS, key="xrd_domain_select")
    domain_presets = ALL_XRD_DOMAINS[selected_domain]
    selected_preset_name = st.selectbox("Reference Phase / Material:", list(domain_presets.keys()), key="xrd_preset_select")
    active_preset = domain_presets[selected_preset_name]

    with st.expander("🇸🇦 Saudi Alliance Databank (KFUPM, KACST, KAUST, IAU)", expanded=False):
        sq = st.text_input("🔍 Filter Materials / Literature:", placeholder="UiO-66, Perovskite, TiO2, MXene...", key="xrd_saudi_sq")
        inst_choice = st.selectbox(
            "Institution Focus:",
            ["All Saudi Alliance Partners", "KAUST", "KFUPM", "KACST", "IAU (iau.edu.sa)"],
            key="xrd_saudi_inst"
        )
        sub_code = inst_choice.split()[0] if "All" not in inst_choice else ""
        from knowledge_base.saudi_research_databank import search_saudi_databank
        bms = search_saudi_databank(query=sq, institution=sub_code, technique="XRD")
        if bms:
            bm_titles = [f"{b['material_name']} ({'/'.join(b['institutions'])})" for b in bms]
            sel_idx = st.selectbox("Institutional References:", range(len(bm_titles)), format_func=lambda i: bm_titles[i], key="xrd_saudi_bm_select")
            active_saudi_bm = bms[sel_idx]
            st.markdown(f"**Pillar:** *{active_saudi_bm['pillar']}*")
            st.markdown(f"**Partners:** {', '.join(active_saudi_bm['institutions'])}")
            st.caption(f"**Key Citation:** {active_saudi_bm['primary_citation']}")
            with st.expander("📖 Expected XRD Reflections", expanded=False):
                if "xrd_benchmarks" in active_saudi_bm:
                    for r in active_saudi_bm["xrd_benchmarks"].get("reflections", []):
                        st.markdown(f"- **{r.get('hkl')}**: `2θ = {r.get('two_theta'):.2f}°` (d = {r.get('d_A', 0.0):.2f} Å) • *{r.get('note', '')}*")
                    st.caption(active_saudi_bm["xrd_benchmarks"].get("diagnostic", ""))
        else:
            st.caption("No matching benchmarks found.")

    st.markdown("### 2. Diffractogram Source")
    uploaded_file = st.file_uploader(
        "Upload XRD Pattern (CSV, XY, DAT, TXT, ASC, Excel):",
        type=["csv", "txt", "dat", "xy", "asc", "xlsx", "xls"],
        key="xrd_uploader",
    )

    if uploaded_file is not None:
        df_active, _, meta = _cached_parse_file(uploaded_file.getvalue(), uploaded_file.name)
        if df_active is None or df_active.empty or df_active.shape[1] < 2:
            st.error("Could not extract 2θ & Intensity columns from file. Loading domain benchmark instead.")
            df_active = _cached_benchmark_xrd(selected_preset_name)
        else:
            st.success(f"Loaded: {uploaded_file.name} ({len(df_active)} pts, {df_active.shape[1] - 1} pattern(s))")
    else:
        df_active = _cached_benchmark_xrd(selected_preset_name)
        st.caption(f"⚡ Simulated multi-sample benchmark for `{selected_preset_name}`")

    st.markdown("---")
    st.markdown("### 3. Publication Typography & Style")
    selected_theme = st.selectbox("Journal Color Palette:", list(PUBLICATION_PALETTES.keys()), index=0, key="xrd_theme")

    st.markdown("---")
    with st.expander("📖 Citation & Attribution", expanded=False):
        st.markdown("""
        **Lead Author:** Dr. Deler Langenberg  
        **Contact:** [delerla@yahoo.de](mailto:delerla@yahoo.de)  
        **Repository:** [Plotting_Chemistry](https://github.com/delerla/Plotting_Chemistry)
        """)

    # Real-Time Domain Visitor Counter
    from modules.counter_module import (
        render_sidebar_counter,
        render_studio_navigation_bar,
        render_unified_studio_footer
    )
    render_sidebar_counter("xrd_studio")


# ==============================================================================
# MAIN WORKSPACE HEADER & UNIFIED ECOSYSTEM NAVIGATION
# ==============================================================================
render_studio_navigation_bar("xrd_studio")
st.markdown('<div class="xrd-header">💎 XRD Studio: X-Ray Diffraction Profile & Microstrain Suite</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="margin-bottom: 1.0rem;">
    <span class="badge badge-dark">{selected_domain}</span>
    <span class="badge badge-blue">{active_preset['material_class']}</span>
    <span class="badge badge-green">Apply-Driven • Lightweight Cached Rendering</span>
</div>
""", unsafe_allow_html=True)

sample_columns = list(df_active.columns[1:])
two_theta_full = df_active.iloc[:, 0].to_numpy(dtype=float)

# Manage Peak Table state synchronized with preset/file signature
preset_sig = f"{selected_domain}::{selected_preset_name}"
if st.session_state.get("xrd_peak_sig") != preset_sig:
    st.session_state["xrd_peak_df"] = _preset_to_peak_df(active_preset["peaks"])
    st.session_state["xrd_peak_sig"] = preset_sig
    w_def = active_preset.get("two_theta_window", (float(np.nanmin(two_theta_full)), float(np.nanmax(two_theta_full))))
    st.session_state["xrd_physics_cfg"]["fit_win_min"] = float(w_def[0])
    st.session_state["xrd_physics_cfg"]["fit_win_max"] = float(w_def[1])
    st.session_state["xrd_physics_cfg"]["line_shape_mode"] = active_preset.get("default_line_shape", "Pseudo-Voigt")
    st.session_state.pop("xrd_fit_cache", None)
    st.session_state.pop("xrd_export_cache", None)

tab_deconv, tab_stacked = st.tabs([
    "🔬 High-Res Deconvolution, Scherrer & Williamson–Hall",
    "📚 Multi-Sample Stacked Diffraction Waterfall",
])


# ==============================================================================
# TAB 1: HIGH-RES DECONVOLUTION, SCHERRER & WILLIAMSON-HALL
# ==============================================================================
with tab_deconv:
    active_sample_col = st.selectbox(
        "Select Target Pattern for Single-Pattern Profile Deconvolution:",
        sample_columns,
        index=0,
        key="xrd_active_sample_col",
    )

    y_col_raw = df_active[active_sample_col].to_numpy(dtype=float)
    valid_mask = np.isfinite(two_theta_full) & np.isfinite(y_col_raw)
    x_clean = two_theta_full[valid_mask]
    y_clean = y_col_raw[valid_mask]

    # 1. PHYSICS, RADIATION & BASELINE FORM (APPLY BUTTON)
    with st.expander("⚙️ Physics, Wavelength, Calibration & Baseline Stripping (Click Apply)", expanded=False):
        with st.form("xrd_physics_form"):
            p_cur = st.session_state["xrd_physics_cfg"]
            c1, c2, c3 = st.columns(3)
            with c1:
                anode_keys = list(ANODE_WAVELENGTHS.keys())
                anode_label = st.selectbox("X-Ray Anode Source:", anode_keys, index=anode_keys.index(p_cur["anode_label"]) if p_cur["anode_label"] in anode_keys else 0)
                use_custom_lam = st.checkbox("Override Wavelength (Å)", value=bool(p_cur["use_custom_lam"]))
                custom_lam_A = st.number_input("Custom λ (Å):", value=float(p_cur["custom_lam_A"]), min_value=0.1, max_value=5.0, step=0.001, format="%.5f")
                strip_ka2 = st.checkbox("Apply Rachinger Kα₂ Stripping", value=bool(p_cur["strip_ka2"]))

            with c2:
                calib_modes = ["None", "Zero-Shift (Δ2θ)", "Specimen Displacement (cos θ)", "Manual Offset (Δ2θ)"]
                calib_mode = st.selectbox("2θ Calibration Mode:", calib_modes, index=calib_modes.index(p_cur["calib_mode"]) if p_cur["calib_mode"] in calib_modes else 0)
                std_keys = list(CALIBRATION_STANDARDS.keys())
                calib_std_label = st.selectbox("Alignment Standard:", std_keys, index=std_keys.index(p_cur["calib_std_label"]) if p_cur["calib_std_label"] in std_keys else 1)
                ca, cb = st.columns(2)
                with ca:
                    measured_ref_2t = st.number_input("Measured Ref (°):", value=float(p_cur["measured_ref_2t"]), step=0.01, format="%.3f")
                with cb:
                    custom_target_2t = st.number_input("Custom Target (°):", value=float(p_cur["custom_target_2t"]), step=0.01, format="%.3f")
                manual_shift_deg = st.number_input("Manual Δ2θ Shift (°):", value=float(p_cur["manual_shift_deg"]), step=0.01, format="%.4f")

            with c3:
                bg_opts = ["AsLS (Asymmetric Least Squares)", "SNIP (LLS Clipping)", "Linear Endpoints", "Constant Min", "None (Zero Baseline)"]
                bg_method = st.selectbox("Background Engine:", bg_opts, index=bg_opts.index(p_cur["bg_method"]) if p_cur["bg_method"] in bg_opts else 0)
                ba, bb = st.columns(2)
                with ba:
                    asls_log_lam = st.number_input("AsLS Smooth log₁₀(λ):", value=float(p_cur["asls_log_lam"]), min_value=2.0, max_value=8.0, step=0.5)
                with bb:
                    asls_p = st.number_input("AsLS Asymmetry p:", value=float(p_cur["asls_p"]), min_value=0.0005, max_value=0.1, step=0.001, format="%.4f")
                snip_window = st.number_input("SNIP Half-Window (pts):", value=int(p_cur["snip_window"]), min_value=5, max_value=150, step=5)

            st.markdown("---")
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                ls_opts = ["Pseudo-Voigt", "Voigt", "Gaussian", "Lorentzian"]
                line_shape_mode = st.selectbox("Default Peak Profile:", ls_opts, index=ls_opts.index(p_cur["line_shape_mode"]) if p_cur["line_shape_mode"] in ls_opts else 0)
                k_scherrer = st.number_input("Scherrer Constant K:", value=float(p_cur["k_scherrer"]), min_value=0.50, max_value=1.20, step=0.01)
            with s2:
                beta_inst_deg = st.number_input("Instrumental FWHM β_inst (°):", value=float(p_cur["beta_inst_deg"]), min_value=0.0, max_value=0.50, step=0.01, format="%.3f")
                broadening_mode = st.selectbox("Broadening Subtraction:", ["Gaussian Quadrature", "Lorentzian Linear"], index=0 if "Gauss" in p_cur["broadening_mode"] else 1)
            with s3:
                fit_win_min = st.number_input("2θ Fit Window Min (°):", value=float(p_cur["fit_win_min"]), step=0.5)
                fit_win_max = st.number_input("2θ Fit Window Max (°):", value=float(p_cur["fit_win_max"]), step=0.5)
            with s4:
                center_tol_deg = st.number_input("Center Drift Tol (±°):", value=float(p_cur["center_tol_deg"]), min_value=0.05, max_value=5.0, step=0.05)
                fwhm_min = st.number_input("Min FWHM (°):", value=float(p_cur["fwhm_min"]), min_value=0.02, max_value=1.0, step=0.02)
                fwhm_max = st.number_input("Max FWHM (°):", value=float(p_cur["fwhm_max"]), min_value=0.2, max_value=15.0, step=0.2)

            r_col1, r_col2 = st.columns(2)
            with r_col1:
                lock_fwhm_equal = st.checkbox("Lock Equal FWHM Across Peaks", value=bool(p_cur["lock_fwhm_equal"]))
            with r_col2:
                resid_bg_mode = st.selectbox("Residual Baseline Term:", ["None (Fixed 0)", "Constant", "Linear"], index=0)

            apply_phys = st.form_submit_button("⚡ Apply Physics, Baseline & Run Fit", type="primary", use_container_width=True)
            if apply_phys:
                st.session_state["xrd_physics_cfg"].update({
                    "anode_label": anode_label,
                    "use_custom_lam": use_custom_lam,
                    "custom_lam_A": custom_lam_A,
                    "strip_ka2": strip_ka2,
                    "calib_mode": calib_mode,
                    "calib_std_label": calib_std_label,
                    "measured_ref_2t": measured_ref_2t,
                    "custom_target_2t": custom_target_2t,
                    "manual_shift_deg": manual_shift_deg,
                    "bg_method": bg_method,
                    "asls_log_lam": asls_log_lam,
                    "asls_p": asls_p,
                    "snip_window": snip_window,
                    "line_shape_mode": line_shape_mode,
                    "k_scherrer": k_scherrer,
                    "beta_inst_deg": beta_inst_deg,
                    "broadening_mode": broadening_mode,
                    "center_tol_deg": center_tol_deg,
                    "fwhm_min": fwhm_min,
                    "fwhm_max": fwhm_max,
                    "lock_fwhm_equal": lock_fwhm_equal,
                    "resid_bg_mode": resid_bg_mode,
                    "fit_win_min": fit_win_min,
                    "fit_win_max": fit_win_max,
                })
                st.session_state["xrd_trigger_fit"] = True

    # 2. EDITABLE PEAK TABLE + AUTO-DETECT (APPLY BUTTON)
    with st.expander("Peak Configuration, Auto-Finder & Fitting Table (Add / Edit / Fix 2θ)", expanded=False):
        ad1, ad2, ad3, ad4 = st.columns([1.2, 1.2, 1.0, 1.4])
        with ad1:
            prom_pct = st.number_input("Auto-Find Prominence (% max):", value=4.5, min_value=0.5, max_value=40.0, step=0.5)
        with ad2:
            min_dist = st.number_input("Min Peak Spacing (2θ°):", value=0.45, min_value=0.1, max_value=5.0, step=0.05)
        with ad3:
            max_pks = st.number_input("Max Peaks:", value=10, min_value=1, max_value=25, step=1)
        with ad4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Auto-Detect Peaks in Pattern", use_container_width=True):
                p_cfg = st.session_state["xrd_physics_cfg"]
                m_w = (x_clean >= float(p_cfg["fit_win_min"])) & (x_clean <= float(p_cfg["fit_win_max"]))
                xw_tmp = x_clean[m_w] if np.sum(m_w) > 10 else x_clean
                yw_tmp = y_clean[m_w] if np.sum(m_w) > 10 else y_clean
                ynet_tmp, _ = extract_net_pattern(xw_tmp, yw_tmp, method=p_cfg["bg_method"])
                detected = auto_detect_xrd_peaks(xw_tmp, ynet_tmp, min_prominence_pct=prom_pct, min_distance_deg=min_dist, max_peaks=int(max_pks))
                st.session_state["xrd_peak_df"] = _preset_to_peak_df(detected)
                st.session_state["xrd_trigger_fit"] = True
                st.rerun()

        edited_peak_df = st.data_editor(
            st.session_state["xrd_peak_df"],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Label": st.column_config.TextColumn("Component Name"),
                "hkl": st.column_config.TextColumn("(hkl) Plane"),
                "Center (2θ°)": st.column_config.NumberColumn("Center (2θ°)", min_value=1.0, max_value=160.0, format="%.3f"),
                "FWHM Init (°)": st.column_config.NumberColumn("Init FWHM (°)", min_value=0.03, max_value=15.0, format="%.3f"),
                "Shape": st.column_config.SelectboxColumn("Line Shape", options=["Auto", "Pseudo-Voigt", "Voigt", "Gaussian", "Lorentzian"]),
                "Fix 2θ": st.column_config.CheckboxColumn("Lock 2θ?"),
                "Color": st.column_config.TextColumn("Hex Color"),
                "Phase / Note": st.column_config.TextColumn("Crystallographic Note"),
            },
            key="xrd_peak_editor",
        )
        b_pk1, b_pk2 = st.columns([3, 1])
        with b_pk1:
            if st.button("🚀 Apply Peak Setup & Run Fit", type="primary", use_container_width=True):
                st.session_state["xrd_peak_df"] = edited_peak_df
                st.session_state["xrd_trigger_fit"] = True
        with b_pk2:
            if st.button("↺ Reset Preset Peaks", use_container_width=True):
                st.session_state["xrd_peak_df"] = _preset_to_peak_df(active_preset["peaks"])
                st.session_state["xrd_trigger_fit"] = True
                st.rerun()

    # 3. TYPOGRAPHY, LEGEND & FIGURE STYLING FORM (APPLY BUTTON - NO REFIT NEEDED!)
    with st.expander("🎨 Editable Typography, Axis Labels, Legend & Publication Style (Click Apply)", expanded=False):
        with st.form("xrd_style_form"):
            sc = st.session_state["xrd_style_cfg"]
            t1, t2, t3 = st.columns(3)
            with t1:
                st_title = st.text_input("Figure Title:", value=sc["title"], placeholder="e.g. High-Resolution XRD Profile")
                st_xlabel = st.text_input("X-Axis Label:", value=sc["xlabel"])
                st_ylabel = st.text_input("Y-Axis Label:", value=sc["ylabel"])
                st_res_y = st.text_input("Residual Y Label:", value=sc["resid_ylabel"])
            with t2:
                st_raw_lbl = st.text_input("Observed Legend Label:", value=sc["raw_label"])
                st_bg_lbl = st.text_input("Background Legend Label:", value=sc["bg_label"])
                st_env_lbl = st.text_input("Total Fit Legend Label:", value=sc["env_label"])
                pk_modes = ["hkl + 2θ + D (nm)", "hkl + d (Å)", "hkl Only", "Peak Name Only", "2θ Position Only", "None"]
                st_pk_mode = st.selectbox("Peak Callout Style:", pk_modes, index=pk_modes.index(sc["peak_label_mode"]) if sc["peak_label_mode"] in pk_modes else 0)
            with t3:
                loc_opts = ["upper right", "upper left", "best", "lower right", "lower left", "upper center"]
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
                st_show_leg = st.checkbox("Show Legend", value=bool(sc["show_legend"]))
            with z2:
                st_leg_frame = st.checkbox("Legend Box", value=bool(sc["legend_frame"]))
            with z3:
                st_hkl_ticks = st.checkbox("Show Ref Ticks", value=bool(sc["show_hkl_ticks"]))
            with z4:
                st_show_res = st.checkbox("Residual Panel", value=bool(sc["show_residual"]))
            with z5:
                st_stats_box = st.checkbox("Stats Inset", value=bool(sc["show_stats_box"]))

            xr1, xr2, xr3 = st.columns(3)
            with xr1:
                use_zoom = st.checkbox("Custom 2θ Zoom Range", value=(sc["x_min"] is not None))
            with xr2:
                z_min = st.number_input("2θ Zoom Min:", value=float(sc["x_min"] if sc["x_min"] is not None else st.session_state["xrd_physics_cfg"]["fit_win_min"]), step=1.0)
            with xr3:
                z_max = st.number_input("2θ Zoom Max:", value=float(sc["x_max"] if sc["x_max"] is not None else st.session_state["xrd_physics_cfg"]["fit_win_max"]), step=1.0)

            if st.form_submit_button("🎨 Apply Figure Style & Typography", use_container_width=True):
                st.session_state["xrd_style_cfg"].update({
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
                    "show_legend": st_show_leg,
                    "legend_frame": st_leg_frame,
                    "show_hkl_ticks": st_hkl_ticks,
                    "show_residual": st_show_res,
                    "show_stats_box": st_stats_box,
                    "x_min": z_min if use_zoom else None,
                    "x_max": z_max if use_zoom else None,
                })
                st.session_state.pop("xrd_export_cache", None)

    # RUN FIT IF TRIGGERED OR FIRST LOAD FOR THIS SAMPLE
    fit_cache_key = f"{preset_sig}::{active_sample_col}::{len(x_clean)}"
    need_fit = (
        st.session_state.pop("xrd_trigger_fit", False)
        or "xrd_fit_cache" not in st.session_state
        or st.session_state["xrd_fit_cache"].get("cache_key") != fit_cache_key
    )
    if need_fit:
        with st.spinner("Running crystallographic profile deconvolution & Scherrer sizing..."):
            try:
                fc_new = _compute_and_store_fit(
                    x_clean, y_clean,
                    phys=st.session_state["xrd_physics_cfg"],
                    peak_df=st.session_state["xrd_peak_df"],
                    active_preset=active_preset,
                    preset_name=selected_preset_name,
                    domain_choice=selected_domain,
                    sample_name=active_sample_col,
                )
                fc_new["cache_key"] = fit_cache_key
                st.session_state["xrd_fit_cache"] = fc_new
                st.session_state.pop("xrd_export_cache", None)
            except Exception as err:
                st.error(f"XRD Profile Fitting Error: {err}")

    # RENDER CACHED DECONVOLUTION OUTPUT (FAST)
    if "xrd_fit_cache" in st.session_state:
        fc = st.session_state["xrd_fit_cache"]
        st.caption(f"⚡ {fc['calib_status']} | Anode λ = {fc['lam_A']:.5f} Å | Profile = {fc['line_shape_mode']}")

        plot_cfg = dict(st.session_state["xrd_style_cfg"])
        plot_cfg["screen_dpi"] = 130
        plot_cfg["stats_extras"] = {
            "r2": fc["r2"],
            "rwp": fc["rwp"],
            "calib_shift": fc["shift_applied"],
        }

        fig_xrd, labplot_df = render_xrd_deconvolution_plot(
            fc["x_calib"],
            fc["y_raw"],
            fc["bg_curve"],
            fc["fit_result"],
            fc["comp_curves"],
            fc["peak_summary"],
            preset_peaks=fc["active_preset"].get("peaks"),
            theme=selected_theme,
            plot_config=plot_cfg,
        )
        st.pyplot(fig_xrd)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fit R²", f"{fc['r2']:.5f}")
        m2.metric("Profile R_wp", f"{fc['rwp']:.2f}%")
        m3.metric("Fitted Bragg Peaks", f"{len(fc['peak_summary'])}")
        m4.metric("Alignment Δ2θ", f"{fc['shift_applied']:+.3f}°")

        # Domain Interpretation + Williamson-Hall Section
        diag = interpret_xrd_diagnostics(
            fc["peak_summary"],
            fc["wh_results"],
            fc["x_calib"],
            fc["y_net"],
            fc["bg_curve"],
            domain_key=fc["domain_choice"],
            preset_dict=fc["active_preset"],
        )

        st.markdown("### 🧠 Automated Crystallographic Diagnostics & Structural Metrics")
        if diag["metrics"]:
            d_cols = st.columns(len(diag["metrics"]))
            for i_m, (_, mv) in enumerate(diag["metrics"].items()):
                with d_cols[i_m]:
                    st.metric(mv["name"], f"{mv['value']:.2f} {mv['unit']}".strip())

        if diag["insights"]:
            st.markdown('<div class="insight-card">', unsafe_allow_html=True)
            for ins in diag["insights"]:
                st.markdown(f"**✓ Structural Insight:** {ins}")
            st.markdown("</div>", unsafe_allow_html=True)

        if diag["warnings"]:
            for w_txt in diag["warnings"]:
                st.markdown(f'<div class="warning-box">⚠️ <b>Phase / Strain Notice:</b> {w_txt}</div>', unsafe_allow_html=True)

        # Williamson-Hall & Parameter Table
        col_tbl, col_wh = st.columns([1.45, 1.0])
        with col_tbl:
            st.markdown("#### 📊 Quantified Bragg Peak & Scherrer Table")
            rows = []
            for p_name, d in fc["peak_summary"].items():
                rows.append({
                    "Peak": p_name,
                    "hkl": d["hkl"],
                    "2θ (°)": d["TwoTheta_deg"],
                    "d (Å)": d["d_Spacing_A"],
                    "FWHM_corr (°)": d["FWHM_corr_deg"],
                    "D_Scherrer (nm)": d["Scherrer_D_nm"],
                    "η (Lorentz)": d["Eta_Lorentzian"],
                    "Area %": f"{d['Area_Percent']:.2f}%",
                    "Note": d["Meaning"],
                })
            quant_df = pd.DataFrame(rows)
            st.dataframe(quant_df, use_container_width=True)

        with col_wh:
            st.markdown("#### 📐 Williamson–Hall Microstrain Plot")
            wh = fc["wh_results"]
            if wh.get("valid"):
                fig_wh = render_williamson_hall_plot(wh, theme=selected_theme, screen_dpi=130)
                st.pyplot(fig_wh)
                plt.close(fig_wh)
            else:
                st.info(f"Williamson–Hall requires ≥3 distinct peaks: {wh.get('reason', '')}")

        # Saudi Research Alliance Cross-Auditing & Literature Verification
        saudi_verif = verify_against_saudi_databank(
            technique="XRD",
            fitted_components=fc["peak_summary"],
            material_hint=selected_preset_name
        )
        with st.expander(f"🏛️ Saudi Alliance Literature Benchmark: {saudi_verif['material_name']} ({saudi_verif['match_percentage']:.0f}% Match)", expanded=True):
            st.markdown(f"""
            <div style="background: #f8fafc; border-left: 5px solid {saudi_verif['verdict_color']}; padding: 10px 14px; border-radius: 6px; margin-bottom: 10px;">
                <span style="font-weight: 700; color: {saudi_verif['verdict_color']}; font-size: 1.0rem;">Audit: {saudi_verif['verdict']}</span> 
                <span style="font-size: 0.85rem; color: #64748b;">({saudi_verif['matched_count']}/{saudi_verif['total_ref_count']} verified reflections, {saudi_verif['match_percentage']:.0f}% literature fidelity)</span><br>
                <span style="font-size: 0.88rem; color: #1e293b; line-height: 1.45;">{saudi_verif['explanation']}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Research Centers:** {', '.join(saudi_verif['institutions'])} | **Pillar:** *{saudi_verif['pillar']}*")
            st.caption(f"**Primary Reference:** {saudi_verif['primary_citation']}")
            if saudi_verif['matches']:
                st.markdown("##### Correlated Literature Bragg Reflections")
                m_df = pd.DataFrame(saudi_verif['matches'])
                m_df.columns = ["Bragg (hkl) Facet", "Literature 2θ (°)", "Measured 2θ (°)", "Deviation |Δ2θ| (°)", "Audit Status"]
                st.dataframe(m_df, use_container_width=True)

        with st.expander("🔍 Search Full Saudi Alliance Literature & Peak Databank (KFUPM · KACST · KAUST · IAU)", expanded=False):
            from modules.saudi_search_ui import render_saudi_alliance_explorer
            render_saudi_alliance_explorer(active_technique="XRD")

        # ----------------------------------------------------------------------
        # PUBLICATION EXPORT CENTER
        # ----------------------------------------------------------------------
        st.markdown("#### 📥 Publication Export Center")
        clean_slug = fc["sample_name"].replace(" ", "_").replace("/", "_")
        zip_bytes = build_analysis_bundle_zip(
            fig_xrd,
            base_name=f"XRD_{clean_slug}",
            labplot_df=labplot_df,
            summary_data=quant_df,
            title=plot_cfg["title"] or f"XRD Profile Deconvolution: {fc['sample_name']}",
            units={"TwoTheta_deg": "deg", "Observed_Intensity": "Counts"},
        )
        st.download_button(
            "📦 Download Complete XRD Publication Package (.ZIP: OriginLab, LabPlot, PNG, SVG, PDF)",
            data=zip_bytes,
            file_name=f"XRD_{clean_slug}_Publication_Bundle.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
            key="dl_xrd_zip",
        )

        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
            st.download_button(
                "📊 Export OriginLab Matrix (.dat)",
                data=get_originlab_ascii_bytes(labplot_df, title="XRD Studio Profile Matrix", units={"TwoTheta_deg": "deg", "Observed_Intensity": "Counts"}),
                file_name=f"XRD_{clean_slug}_OriginLab.dat",
                mime="text/plain",
                use_container_width=True,
                key="xrd_origin_dat",
                help="OriginLab-compatible ASCII matrix with A(X), B(Y) column designations for direct drag & drop."
            )
            st.download_button(
                "📗 Export OriginLab Workbook (.xlsx)",
                data=get_originlab_excel_bytes(labplot_df, title="XRD Studio Profile Matrix", units={"TwoTheta_deg": "deg", "Observed_Intensity": "Counts"}),
                file_name=f"XRD_{clean_slug}_OriginLab.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="xrd_origin_xlsx",
                help="OriginLab-ready Excel workbook with 4-tier metadata header."
            )
            st.download_button(
                "📈 Export LabPlot Matrix (.dat)",
                data=get_labplot_ascii_bytes(labplot_df, title="XRD Studio Profile Matrix"),
                file_name=f"XRD_{clean_slug}_LabPlot.dat",
                mime="text/plain",
                use_container_width=True,
                key="xrd_labplot_dat",
                help="LabPlot ASCII data table with metadata header."
            )
        with c_right:
            st.markdown("**🖼️ Publication Graphics:**")
            st.download_button("🖼️ Export 600 DPI PNG", data=get_figure_bytes(fig_xrd, "png", dpi=600), file_name=f"XRD_{clean_slug}_600DPI.png", mime="image/png", use_container_width=True, key="xrd_png")
            st.download_button("📐 Export Vector SVG", data=get_figure_bytes(fig_xrd, "svg"), file_name=f"XRD_{clean_slug}.svg", mime="image/svg+xml", use_container_width=True, key="xrd_svg")
            st.download_button("📄 Export Vector PDF", data=get_figure_bytes(fig_xrd, "pdf"), file_name=f"XRD_{clean_slug}.pdf", mime="application/pdf", use_container_width=True, key="xrd_pdf")

        plt.close(fig_xrd)


# ==============================================================================
# TAB 2: MULTI-SAMPLE STACKED WATERFALL COMPARISON
# ==============================================================================
with tab_stacked:
    with st.form("xrd_stacked_form"):
        st.markdown("Configure multi-pattern waterfall stacking and legend labels, then click **Apply Stacked Plot**.")
        c_st1, c_st2, c_st3, c_st4 = st.columns(4)
        with c_st1:
            sel_cols_stack = st.multiselect("Patterns to Stack:", sample_columns, default=sample_columns)
        with c_st2:
            norm_stack = st.checkbox("Normalize Max Peak = 100%", value=True)
            strip_stack_bg = st.checkbox("Strip AsLS Background First", value=False)
        with c_st3:
            offset_stack = st.number_input("Vertical Offset (0 = Auto):", value=0.0, min_value=0.0, step=10.0)
            show_ref_guides = st.checkbox("Show Reference (hkl) Guides", value=True)
        with c_st4:
            stack_title = st.text_input("Waterfall Title:", value="")
            stack_legend_raw = st.text_input("Custom Legend Names (comma-sep):", value=", ".join(sample_columns))

        submitted_stack = st.form_submit_button("📚 Apply Stacked Plot", type="primary", use_container_width=True)

    custom_map = {}
    parsed_names = [s.strip() for s in stack_legend_raw.split(",") if s.strip()]
    for idx_s, orig_c in enumerate(sel_cols_stack):
        custom_map[orig_c] = parsed_names[idx_s] if idx_s < len(parsed_names) else orig_c

    if sel_cols_stack:
        stack_cfg = dict(st.session_state["xrd_style_cfg"])
        stack_cfg["title"] = stack_title
        stack_cfg["show_hkl_ticks"] = show_ref_guides
        stack_cfg["screen_dpi"] = 130
        if norm_stack:
            stack_cfg["ylabel"] = r"$\mathbf{Normalized\ Intensity\ (\%)}$"

        fig_stack, stack_lab_df = render_xrd_stacked_plot(
            df_active,
            selected_cols=sel_cols_stack,
            custom_labels=custom_map,
            offset_step=float(offset_stack),
            normalize_max=norm_stack,
            strip_bg=strip_stack_bg,
            preset_peaks=active_preset.get("peaks"),
            theme=selected_theme,
            plot_config=stack_cfg,
        )
        st.pyplot(fig_stack)

        st.markdown("#### 📥 Stacked Waterfall Export Center")
        d_left, d_right = st.columns(2)
        with d_left:
            st.markdown("**📊 Data Tables (OriginLab & LabPlot):**")
            st.download_button(
                "📊 Export OriginLab .DAT (Stacked)",
                data=get_originlab_ascii_bytes(stack_lab_df, title="XRD Stacked Waterfall Matrix", units={"TwoTheta_deg": "deg"}),
                file_name="XRD_Stacked_OriginLab.dat",
                mime="text/plain",
                use_container_width=True,
                key="xrd_stack_origin_dat"
            )
            st.download_button(
                "📗 Export OriginLab .XLSX (Stacked)",
                data=get_originlab_excel_bytes(stack_lab_df, title="XRD Stacked Waterfall Matrix", units={"TwoTheta_deg": "deg"}),
                file_name="XRD_Stacked_OriginLab.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="xrd_stack_origin_xlsx"
            )
            st.download_button(
                "📈 Export LabPlot .DAT (Stacked)",
                data=get_labplot_ascii_bytes(stack_lab_df, title="XRD Stacked Waterfall Matrix"),
                file_name="XRD_Stacked_LabPlot.dat",
                mime="text/plain",
                use_container_width=True,
                key="xrd_stack_labplot_dat"
            )
        with d_right:
            st.markdown("**🖼️ Publication Graphics:**")
            st.download_button("🖼️ Export 600 DPI PNG (Stacked)", data=get_figure_bytes(fig_stack, "png", dpi=600), file_name="XRD_Stacked_600DPI.png", mime="image/png", use_container_width=True, key="xrd_stack_png")
            st.download_button("📐 Export Vector SVG (Stacked)", data=get_figure_bytes(fig_stack, "svg"), file_name="XRD_Stacked.svg", mime="image/svg+xml", use_container_width=True, key="xrd_stack_svg")
        plt.close(fig_stack)
    else:
        st.warning("Select at least one pattern column above to display the stacked waterfall plot.")


# ==============================================================================
# UNIFIED INSTITUTIONAL FOOTER & MASTER GATEWAY REVIEW LINK
# ==============================================================================
render_unified_studio_footer(
    active_domain_key="xrd_studio",
    studio_title="XRD Crystallography Studio",
    studio_subtitle="X-Ray Diffraction Profile Deconvolution, Scherrer Sizing & Williamson–Hall Strain Intelligence"
)
