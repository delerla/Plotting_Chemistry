"""
plot_ftir.py - Publication-Grade FTIR Vibrational Spectroscopy Visualizer.
Provides:
  1. Dual-Panel High-Resolution ROI Deconvolution + Fit Residual Plot
  2. Multi-Sample Stacked Transmittance (%T) / Absorbance Comparison Waterfall
  3. Inverted Second-Derivative (-d2A/dnu2) Shoulder Resolution Plot
With full editable typography, custom legend text, wavenumber callouts, and LabPlot export.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style

try:
    from core.baseline import extract_net_absorbance
    from core.preprocessing import (
        apply_atr_correction,
        apply_savgol_smooth,
        compute_second_derivative,
        convert_ir_scale,
        mask_co2_artifact,
    )
except ImportError:
    from ftir_studio.core.baseline import extract_net_absorbance
    from ftir_studio.core.preprocessing import (
        apply_atr_correction,
        apply_savgol_smooth,
        compute_second_derivative,
        convert_ir_scale,
        mask_co2_artifact,
    )

DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"
]


def _mpl_txt(text: str) -> str:
    """Normalizes chemical subscripts/superscripts & symbols to Matplotlib mathtext cleanly for Arial."""
    s = str(text)
    if "$" in s:
        return s
    replacements = [
        ("⁻¹", "$^{-1}$"),
        ("²⁻", "$^{2-}$"),
        ("⁻", "$^{-}$"),
        ("⁺", "$^{+}$"),
        ("²", "$^2$"),
        ("₀", "$_0$"), ("₁", "$_1$"), ("₂", "$_2$"), ("₃", "$_3$"), ("₄", "$_4$"),
        ("≡", "$\\equiv$"),
        ("ν_as", "$\\nu_{as}$"),
        ("ν_s", "$\\nu_s$"),
        ("ν", "$\\nu$"),
        ("δ_s", "$\\delta_s$"),
        ("δ", "$\\delta$"),
        ("γ", "$\\gamma$"),
        ("μ₃", "$\\mu_3$"),
    ]
    for k, v in replacements:
        s = s.replace(k, v)
    return s


def render_ftir_deconvolution_plot(
    wavenumber: np.ndarray,
    y_abs: np.ndarray,
    bg_curve: np.ndarray,
    fit_result: Any,
    comp_curves: Dict[str, np.ndarray],
    band_summary: Dict[str, Dict[str, Any]],
    preset_bands: Optional[List[Dict[str, Any]]] = None,
    theme: str = "ACS",
    plot_config: Optional[Dict[str, Any]] = None,
) -> Tuple[plt.Figure, pd.DataFrame]:
    """
    Renders a journal-ready dual-panel FTIR deconvolution figure with customizable typography,
    vibrational band callouts, stripped baseline, and fit residual panel.
    """
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    cfg = plot_config or {}

    fig_w = float(cfg.get("fig_width", 9.0))
    fig_h = float(cfg.get("fig_height", 6.4))
    screen_dpi = int(cfg.get("screen_dpi", 130))

    title = cfg.get("title", "")
    xlabel = cfg.get("xlabel", r"$\mathbf{Wavenumber\ (cm^{-1})}$")
    ylabel = cfg.get("ylabel", r"$\mathbf{Absorbance\ (a.u.)}$")
    resid_ylabel = cfg.get("resid_ylabel", r"$\mathbf{Residual}$")
    raw_label = cfg.get("raw_label", "Observed Spectrum")
    bg_label = cfg.get("bg_label", "Stripped Baseline")
    env_label = cfg.get("env_label", "Total Band Envelope")

    title_size = int(cfg.get("title_size", 14))
    axis_label_size = int(cfg.get("axis_label_size", 13))
    tick_size = int(cfg.get("tick_size", 11))
    legend_size = int(cfg.get("legend_size", 9))
    annot_size = int(cfg.get("annot_size", 8))

    invert_x = bool(cfg.get("invert_x", True))
    show_legend = bool(cfg.get("show_legend", True))
    legend_loc = str(cfg.get("legend_loc", "upper right"))
    legend_frame = bool(cfg.get("legend_frame", True))
    legend_cols = int(cfg.get("legend_cols", 1))
    peak_label_mode = str(cfg.get("peak_label_mode", "Band + cm⁻¹ + Area%"))
    show_resid = bool(cfg.get("show_residual", True))
    show_stats_box = bool(cfg.get("show_stats_box", True))
    lw = float(cfg.get("line_width", 1.8))

    order = np.argsort(wavenumber)
    x = np.asarray(wavenumber[order], dtype=float)
    y_obs = np.asarray(y_abs[order], dtype=float)
    bg = np.asarray(bg_curve[order], dtype=float)
    y_calc = np.asarray(fit_result.best_fit, dtype=float) + bg
    resid = y_obs - y_calc

    if show_resid:
        fig = plt.figure(figsize=(fig_w, fig_h), dpi=screen_dpi, layout="constrained")
        gs = fig.add_gridspec(2, 1, height_ratios=[4.2, 1.0], hspace=0.05)
        ax_main = fig.add_subplot(gs[0])
        ax_res = fig.add_subplot(gs[1], sharex=ax_main)
    else:
        fig, ax_main = plt.subplots(figsize=(fig_w, fig_h), dpi=screen_dpi, layout="constrained")
        ax_res = None

    ax_main.plot(x, y_obs, color="#222222", lw=max(lw * 0.85, 1.0), alpha=0.82, label=_mpl_txt(raw_label), zorder=2)
    ax_main.plot(x, bg, color="#64748b", lw=1.2, ls="--", alpha=0.88, label=_mpl_txt(bg_label), zorder=3)

    labplot_dict: Dict[str, np.ndarray] = {
        "Wavenumber_cm-1": x,
        "Observed_Absorbance": y_obs,
        "Baseline": bg,
        "Calculated_Envelope": y_calc,
        "Residual": resid,
    }

    y_span = max(float(np.nanmax(y_obs) - np.nanmin(bg)), 1e-4)
    idx_c = 0
    for name, b_info in band_summary.items():
        y_comp = comp_curves.get(name)
        if y_comp is None:
            continue
        y_plot = y_comp + bg
        color = b_info.get("Color", palette[idx_c % len(palette)])
        wn_val = float(b_info["Wavenumber_cm1"])
        area_pct = float(b_info["Area_Percent"])

        leg_lbl = _mpl_txt(f"{name} ({wn_val:.0f} | {area_pct:.1f}%)")
        ax_main.fill_between(x, bg, y_plot, color=color, alpha=0.22, zorder=3)
        ax_main.plot(x, y_plot, color=color, lw=1.35, label=leg_lbl, zorder=4)
        labplot_dict[f"Band_{name.replace(' ', '_')}"] = y_plot

        if peak_label_mode != "None":
            pk_y = float(np.nanmax(y_plot))
            if peak_label_mode == "Band Name Only":
                txt = name
            elif peak_label_mode == "Wavenumber Only":
                txt = f"{wn_val:.0f}"
            elif peak_label_mode == "Band + cm⁻¹":
                txt = f"{name}\n{wn_val:.0f}"
            else:
                txt = f"{name}\n{wn_val:.0f} ({area_pct:.1f}%)"

            ax_main.annotate(
                _mpl_txt(txt),
                xy=(wn_val, pk_y),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=annot_size,
                fontweight="bold",
                color=color,
                bbox=dict(boxstyle="round,pad=0.16", fc="white", ec=color, alpha=0.80, lw=0.7),
                zorder=7,
            )
        idx_c += 1

    ax_main.plot(x, y_calc, color="#e11d48", lw=lw, ls="-", label=_mpl_txt(env_label), zorder=6)

    x_min_cfg = cfg.get("x_min")
    x_max_cfg = cfg.get("x_max")
    lo = float(x_min_cfg) if x_min_cfg is not None else float(x.min())
    hi = float(x_max_cfg) if x_max_cfg is not None else float(x.max())
    if hi > lo:
        ax_main.set_xlim(hi, lo) if invert_x else ax_main.set_xlim(lo, hi)

    y_top = max(float(np.nanmax(y_obs)), float(np.nanmax(y_calc))) + 0.16 * y_span
    y_bot = float(np.nanmin(bg)) - 0.04 * y_span
    if y_top > y_bot:
        ax_main.set_ylim(y_bot, y_top)

    if title:
        ax_main.set_title(_mpl_txt(title), fontsize=title_size, fontweight="bold", pad=10)
    ax_main.set_ylabel(_mpl_txt(ylabel), fontsize=axis_label_size, labelpad=8)
    ax_main.minorticks_on()
    ax_main.tick_params(axis="both", which="both", direction="in", top=True, right=True, labelsize=tick_size)

    if show_legend:
        ax_main.legend(
            loc=legend_loc,
            fontsize=legend_size,
            ncol=max(1, legend_cols),
            frameon=legend_frame,
            framealpha=0.92,
            edgecolor="#cbd5e1",
        )

    stats_extras = cfg.get("stats_extras") or {}
    if show_stats_box and stats_extras:
        lines = []
        if "r2" in stats_extras:
            lines.append(f"R² = {stats_extras['r2']:.5f}")
        if "rmse" in stats_extras:
            lines.append(f"RMSE = {stats_extras['rmse']:.4f}")
        if lines:
            ax_main.text(
                0.02, 0.96, "\n".join(lines),
                transform=ax_main.transAxes,
                va="top", ha="left",
                fontsize=max(legend_size - 0.5, 7.5),
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#94a3b8", alpha=0.90),
                zorder=8,
            )

    if ax_res is not None:
        plt.setp(ax_main.get_xticklabels(), visible=False)
        ax_res.axhline(0.0, color="#64748b", ls="--", lw=1.0, zorder=2)
        ax_res.plot(x, resid, color="#0284c7", lw=1.05, alpha=0.9, zorder=3)
        ax_res.set_xlabel(_mpl_txt(xlabel), fontsize=axis_label_size, labelpad=8)
        ax_res.set_ylabel(_mpl_txt(resid_ylabel), fontsize=max(axis_label_size - 2, 9), labelpad=6)
        ax_res.minorticks_on()
        ax_res.tick_params(axis="both", which="both", direction="in", top=True, right=True, labelsize=max(tick_size - 1, 8))
        for sp in ax_res.spines.values():
            sp.set_linewidth(1.4)
    else:
        ax_main.set_xlabel(_mpl_txt(xlabel), fontsize=axis_label_size, labelpad=8)

    for sp in ax_main.spines.values():
        sp.set_linewidth(1.5)

    return fig, pd.DataFrame(labplot_dict)


def render_ftir_stacked_plot(
    df: pd.DataFrame,
    selected_cols: List[str],
    custom_labels: Optional[Dict[str, str]] = None,
    display_mode: str = "Transmittance (%T)",
    normalize_mode: str = "None",
    offset_step: float = 0.0,
    sg_window: int = 9,
    mask_co2: bool = True,
    atr_correct: bool = False,
    strip_baseline: bool = False,
    annotate_peaks: bool = True,
    prominence_pct: float = 6.0,
    theme: str = "ACS",
    plot_config: Optional[Dict[str, Any]] = None,
) -> Tuple[plt.Figure, pd.DataFrame, Dict[str, List[float]]]:
    """
    Renders a publication-quality stacked FTIR comparison waterfall supporting %T or Absorbance,
    ATIR/CO2 cleaning, AsLS baseline stripping, Savitzky-Golay smoothing, and peak callouts.
    """
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    cfg = plot_config or {}
    custom_labels = custom_labels or {}

    fig_w = float(cfg.get("fig_width", 9.2))
    fig_h = float(cfg.get("fig_height", 6.6))
    screen_dpi = int(cfg.get("screen_dpi", 130))
    invert_x = bool(cfg.get("invert_x", True))

    is_abs = "absorbance" in display_mode.lower()
    title = cfg.get("title", "")
    xlabel = cfg.get("xlabel", r"$\mathbf{Wavenumber\ (cm^{-1})}$")
    ylabel = cfg.get(
        "ylabel",
        r"$\mathbf{Absorbance\ (a.u.)}$" if is_abs else r"$\mathbf{Transmittance\ (\%)}$",
    )
    title_size = int(cfg.get("title_size", 14))
    axis_label_size = int(cfg.get("axis_label_size", 13))
    tick_size = int(cfg.get("tick_size", 11))
    legend_size = int(cfg.get("legend_size", 10))
    show_legend = bool(cfg.get("show_legend", True))
    legend_loc = str(cfg.get("legend_loc", "upper right"))
    legend_frame = bool(cfg.get("legend_frame", True))
    lw = float(cfg.get("line_width", 1.7))

    x_raw = df.iloc[:, 0].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=screen_dpi, layout="constrained")

    labplot_dict: Dict[str, np.ndarray] = {"Wavenumber_cm-1": x_raw}
    valid_curves: List[Tuple[str, np.ndarray, np.ndarray]] = []
    detected_map: Dict[str, List[float]] = {}

    max_span = 0.05 if is_abs else 10.0
    for col in selected_cols:
        if col not in df.columns:
            continue
        yc_raw = df[col].to_numpy(dtype=float)
        mask = np.isfinite(x_raw) & np.isfinite(yc_raw)
        xc, yc = x_raw[mask], yc_raw[mask]
        if len(xc) < 8:
            continue
        ord_idx = np.argsort(xc)[::-1] if invert_x else np.argsort(xc)
        xc, yc = xc[ord_idx], yc[ord_idx]

        # Convert to absorbance internally for clean baseline/ATR/CO2 corrections
        y_abs, _ = convert_ir_scale(yc, source_scale="Auto-Detect", target_scale="Absorbance (A)")
        if mask_co2:
            y_abs = mask_co2_artifact(xc, y_abs)
        if atr_correct:
            y_abs = apply_atr_correction(xc, y_abs)
        if strip_baseline:
            y_abs, _ = extract_net_absorbance(xc, y_abs, method="AsLS (Asymmetric Least Squares)")
        if sg_window >= 5:
            y_abs = apply_savgol_smooth(y_abs, window_len=sg_window, polyorder=2)

        if is_abs:
            y_disp = y_abs
        else:
            y_disp, _ = convert_ir_scale(y_abs, source_scale="Absorbance (A)", target_scale="Transmittance (%T)")

        if normalize_mode == "Min-Max (0 to 1)":
            span = float(np.ptp(y_disp))
            if span > 1e-9:
                y_disp = (y_disp - float(np.min(y_disp))) / span
        elif normalize_mode == "Zero Baseline":
            y_disp = y_disp - float(np.min(y_disp))

        max_span = max(max_span, float(np.ptp(y_disp)))
        valid_curves.append((col, xc, y_disp))

    auto_step = (max_span * 1.08) if offset_step <= 0.0 else float(offset_step)
    curr_offset = 0.0
    prefix_tags = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)", "(h)"]

    for idx, (col, xc, yd) in enumerate(valid_curves):
        disp_name = custom_labels.get(col, col)
        tag = prefix_tags[idx] if idx < len(prefix_tags) else f"({idx + 1})"
        y_shifted = yd + curr_offset
        color = "black" if theme == "Monochrome" else palette[idx % len(palette)]

        ax.plot(xc, y_shifted, color=color, lw=lw, label=_mpl_txt(f"{tag} {disp_name}"), zorder=3 + idx)
        labplot_dict[f"{disp_name.replace(' ', '_')}_Stacked"] = np.interp(x_raw, xc, y_shifted)

        # Peak identification on curve
        sig_target = yd if is_abs else -yd
        dx = max(float(np.nanmedian(np.abs(np.diff(xc)))), 0.5)
        dist_pts = max(int(round(35.0 / dx)), 5)
        prom_val = max(float(np.ptp(yd)) * (float(prominence_pct) / 100.0), 1e-5)
        p_idxs, _ = find_peaks(sig_target, prominence=prom_val, distance=dist_pts)
        p_wns = [round(float(xc[p]), 1) for p in p_idxs if 450.0 <= xc[p] <= 3750.0]
        detected_map[disp_name] = p_wns

        if annotate_peaks:
            drop_len = max_span * 0.08
            for p in p_idxs:
                px, py = float(xc[p]), float(y_shifted[p])
                if 450.0 <= px <= 3700.0:
                    y_lbl_end = (py + drop_len) if is_abs else (py - drop_len)
                    ax.plot([px, px], [py, y_lbl_end], color="#64748b", ls="--", lw=0.85, zorder=2)
                    ax.text(
                        px,
                        y_lbl_end + (drop_len * 0.2 if is_abs else -drop_len * 0.2),
                        f"{int(round(px))}",
                        rotation=90,
                        ha="center",
                        va="bottom" if is_abs else "top",
                        fontsize=max(tick_size - 2.5, 7.5),
                        color="#334155",
                        fontweight="bold",
                    )

        curr_offset += auto_step

    x_min_cfg = cfg.get("x_min")
    x_max_cfg = cfg.get("x_max")
    finite_x = x_raw[np.isfinite(x_raw)]
    lo = float(x_min_cfg) if x_min_cfg is not None else float(np.nanmin(finite_x))
    hi = float(x_max_cfg) if x_max_cfg is not None else float(np.nanmax(finite_x))
    if hi > lo:
        ax.set_xlim(hi, lo) if invert_x else ax.set_xlim(lo, hi)

    if title:
        ax.set_title(_mpl_txt(title), fontsize=title_size, fontweight="bold", pad=10)
    ax.set_xlabel(_mpl_txt(xlabel), fontsize=axis_label_size, labelpad=8)
    ax.set_ylabel(_mpl_txt(ylabel), fontsize=axis_label_size, labelpad=10)
    ax.set_yticks([])
    ax.minorticks_on()
    ax.tick_params(axis="x", which="both", direction="in", top=True, labelsize=tick_size)
    ax.tick_params(axis="y", which="both", direction="in", left=True, right=True)

    if show_legend and valid_curves:
        ax.legend(loc=legend_loc, fontsize=legend_size, frameon=legend_frame, framealpha=0.92, edgecolor="#cbd5e1")

    for sp in ax.spines.values():
        sp.set_linewidth(1.5)

    return fig, pd.DataFrame(labplot_dict), detected_map


def render_second_derivative_plot(
    wavenumber: np.ndarray,
    y_net_abs: np.ndarray,
    invert_x: bool = True,
    theme: str = "ACS",
    screen_dpi: int = 130,
) -> plt.Figure:
    """Renders Absorbance + Inverted Second Derivative (-d2A/dnu2) to resolve overlapping IR bands."""
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.0, 4.8), dpi=screen_dpi, sharex=True, layout="constrained")

    order = np.argsort(wavenumber)
    x = np.asarray(wavenumber[order], dtype=float)
    y = np.asarray(y_net_abs[order], dtype=float)
    d2 = compute_second_derivative(x, y, window_len=15, polyorder=3)

    ax1.plot(x, y, color=palette[0], lw=1.6, label="Net Absorbance")
    ax1.set_ylabel("Absorbance (a.u.)", fontsize=11)
    ax1.set_title(_mpl_txt("2nd-Derivative Shoulder Resolution (-d²A/dν²)"), fontsize=12, fontweight="bold")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.minorticks_on()

    ax2.axhline(0.0, color="#64748b", ls="--", lw=0.9)
    ax2.plot(x, d2, color="#e11d48", lw=1.4, label=_mpl_txt("-d²A/dν² (Peak Centers = Maxima)"))
    ax2.set_ylabel(_mpl_txt("-d²A/dν²"), fontsize=11)
    ax2.set_xlabel(_mpl_txt("Wavenumber (cm⁻¹)"), fontsize=11)
    ax2.legend(loc="upper right", fontsize=9)
    ax2.minorticks_on()

    if invert_x:
        ax1.set_xlim(float(x.max()), float(x.min()))
    else:
        ax1.set_xlim(float(x.min()), float(x.max()))

    return fig
