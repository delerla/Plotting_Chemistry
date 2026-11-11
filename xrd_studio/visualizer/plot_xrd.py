"""
plot_xrd.py - Publication-Grade Powder & Thin-Film XRD Visualizer.
Provides:
  1. Dual-Panel High-Resolution XRD Profile Deconvolution + Residual Plot
  2. Multi-Sample Stacked / Normalized Diffractogram Waterfall Comparison
  3. Williamson-Hall Microstrain & Crystallite Size Regression Plot
With full interactive typography, legend customization, (hkl) callouts, and LabPlot export.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style

DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#17becf", "#bcbd22", "#7f7f7f"
]

_UNICODE_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def _mpl_txt(text: str) -> str:
    """Converts Unicode subscript digits (e.g. TiO₂, Cu₂O) to Matplotlib mathtext $_2$ for clean Arial rendering."""
    s = str(text)
    if "$" in s:
        return s
    out = []
    for ch in s:
        if ch in "₀₁₂₃₄₅₆₇₈₉":
            out.append(f"$_{ch.translate(_UNICODE_SUB)}$")
        else:
            out.append(ch)
    return "".join(out)


def render_xrd_deconvolution_plot(
    two_theta: np.ndarray,
    y_raw: np.ndarray,
    bg_curve: np.ndarray,
    fit_result: Any,
    comp_curves: Dict[str, np.ndarray],
    peak_summary: Dict[str, Dict[str, Any]],
    preset_peaks: Optional[List[Dict[str, Any]]] = None,
    theme: str = "ACS",
    plot_config: Optional[Dict[str, Any]] = None,
) -> Tuple[plt.Figure, pd.DataFrame]:
    """
    Renders a journal-ready dual-panel XRD deconvolution figure with customizable typography,
    (hkl) reflection callouts, background trace, and residual panel.
    """
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    cfg = plot_config or {}

    fig_w = float(cfg.get("fig_width", 9.0))
    fig_h = float(cfg.get("fig_height", 6.4))
    screen_dpi = int(cfg.get("screen_dpi", 130))

    title = cfg.get("title", "")
    xlabel = cfg.get("xlabel", r"$\mathbf{2\theta\ (degrees)}$")
    ylabel = cfg.get("ylabel", r"$\mathbf{Intensity\ (a.u.)}$")
    resid_ylabel = cfg.get("resid_ylabel", r"$\mathbf{Residual}$")
    raw_label = cfg.get("raw_label", "Observed Pattern")
    bg_label = cfg.get("bg_label", "Stripped Baseline")
    env_label = cfg.get("env_label", "Total Profile Fit")

    title_size = int(cfg.get("title_size", 14))
    axis_label_size = int(cfg.get("axis_label_size", 13))
    tick_size = int(cfg.get("tick_size", 11))
    legend_size = int(cfg.get("legend_size", 9))
    annot_size = int(cfg.get("annot_size", 8))

    show_legend = bool(cfg.get("show_legend", True))
    legend_loc = str(cfg.get("legend_loc", "upper right"))
    legend_frame = bool(cfg.get("legend_frame", True))
    legend_cols = int(cfg.get("legend_cols", 1))
    peak_label_mode = str(cfg.get("peak_label_mode", "hkl + 2θ + D (nm)"))
    show_hkl_ticks = bool(cfg.get("show_hkl_ticks", False))
    show_resid = bool(cfg.get("show_residual", True))
    show_stats_box = bool(cfg.get("show_stats_box", True))
    lw = float(cfg.get("line_width", 1.8))

    order = np.argsort(two_theta)
    x = np.asarray(two_theta[order], dtype=float)
    y_obs = np.asarray(y_raw[order], dtype=float)
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

    # 1. Raw experimental trace
    ax_main.plot(x, y_obs, color="#222222", lw=max(lw * 0.85, 1.0), alpha=0.82, label=raw_label, zorder=2)

    # 2. Stripped Baseline
    ax_main.plot(x, bg, color="#64748b", lw=1.2, ls="--", alpha=0.88, label=bg_label, zorder=3)

    # 3. Fitted Peak Components
    labplot_dict: Dict[str, np.ndarray] = {
        "TwoTheta_deg": x,
        "Observed_Intensity": y_obs,
        "Background": bg,
        "Calculated_Envelope": y_calc,
        "Residual": resid,
    }

    y_span = max(float(np.nanmax(y_obs) - np.nanmin(bg)), 1.0)
    idx_c = 0
    for name, p_info in peak_summary.items():
        y_comp = comp_curves.get(name)
        if y_comp is None:
            continue
        y_plot = y_comp + bg
        color = p_info.get("Color", palette[idx_c % len(palette)])
        tt_val = float(p_info["TwoTheta_deg"])
        d_nm = float(p_info["Scherrer_D_nm"])
        hkl_str = str(p_info.get("hkl", "")).strip()

        leg_lbl = _mpl_txt(f"{name} ({tt_val:.2f}° | D={d_nm:.1f} nm)")
        ax_main.fill_between(x, bg, y_plot, color=color, alpha=0.22, zorder=3)
        ax_main.plot(x, y_plot, color=color, lw=1.35, label=leg_lbl, zorder=4)
        labplot_dict[f"Comp_{name.replace(' ', '_')}"] = y_plot

        # Peak Callout on Plot
        if peak_label_mode != "None":
            pk_y = float(np.nanmax(y_plot))
            if peak_label_mode == "Peak Name Only":
                txt = name
            elif peak_label_mode == "hkl Only":
                txt = hkl_str if hkl_str else name
            elif peak_label_mode == "2θ Position Only":
                txt = f"{tt_val:.2f}°"
            elif peak_label_mode == "hkl + d (Å)":
                txt = f"{hkl_str or name}\nd={p_info['d_Spacing_A']:.2f} Å"
            else:
                lbl_head = hkl_str if hkl_str else name
                txt = f"{lbl_head}\n{tt_val:.2f}° | {d_nm:.0f}nm"

            ax_main.annotate(
                _mpl_txt(txt),
                xy=(tt_val, pk_y),
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

    # 4. Total Calculated Envelope
    ax_main.plot(x, y_calc, color="#e11d48", lw=lw, ls="-", label=env_label, zorder=6)

    # 5. Optional Reference Tick Markers (sticks at base)
    if show_hkl_ticks and preset_peaks:
        y_base_tick = float(np.nanmin(bg)) - 0.04 * y_span
        for rp in preset_peaks:
            rc = float(rp.get("center", 0))
            if x.min() <= rc <= x.max():
                ax_main.plot([rc, rc], [y_base_tick, y_base_tick + 0.03 * y_span], color="#0284c7", lw=1.3, zorder=5)

    # Axis formatting
    x_min_cfg = cfg.get("x_min")
    x_max_cfg = cfg.get("x_max")
    xmin = float(x_min_cfg) if x_min_cfg is not None else float(x.min())
    xmax = float(x_max_cfg) if x_max_cfg is not None else float(x.max())
    if xmax > xmin:
        ax_main.set_xlim(xmin, xmax)

    y_top = max(float(np.nanmax(y_obs)), float(np.nanmax(y_calc))) + 0.16 * y_span
    y_bot = float(np.nanmin(bg)) - (0.06 * y_span if show_hkl_ticks else 0.03 * y_span)
    if y_top > y_bot:
        ax_main.set_ylim(y_bot, y_top)

    if title:
        ax_main.set_title(title, fontsize=title_size, fontweight="bold", pad=10)
    ax_main.set_ylabel(ylabel, fontsize=axis_label_size, labelpad=8)
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

    # Optional fit statistics inset
    stats_extras = cfg.get("stats_extras") or {}
    if show_stats_box and stats_extras:
        lines = []
        if "r2" in stats_extras:
            lines.append(f"R² = {stats_extras['r2']:.5f}")
        if "rwp" in stats_extras:
            lines.append(f"R_wp = {stats_extras['rwp']:.2f}%")
        if "calib_shift" in stats_extras and abs(stats_extras["calib_shift"]) > 1e-4:
            lines.append(f"Δ2θ = {stats_extras['calib_shift']:+.3f}°")
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
        ax_res.set_xlabel(xlabel, fontsize=axis_label_size, labelpad=8)
        ax_res.set_ylabel(resid_ylabel, fontsize=max(axis_label_size - 2, 9), labelpad=6)
        ax_res.minorticks_on()
        ax_res.tick_params(axis="both", which="both", direction="in", top=True, right=True, labelsize=max(tick_size - 1, 8))
        for sp in ax_res.spines.values():
            sp.set_linewidth(1.4)
    else:
        ax_main.set_xlabel(xlabel, fontsize=axis_label_size, labelpad=8)

    for sp in ax_main.spines.values():
        sp.set_linewidth(1.5)

    return fig, pd.DataFrame(labplot_dict)


def render_xrd_stacked_plot(
    df: pd.DataFrame,
    selected_cols: List[str],
    custom_labels: Optional[Dict[str, str]] = None,
    offset_step: float = 0.0,
    normalize_max: bool = True,
    strip_bg: bool = False,
    bg_method: str = "AsLS (Asymmetric Least Squares)",
    preset_peaks: Optional[List[Dict[str, Any]]] = None,
    theme: str = "ACS",
    plot_config: Optional[Dict[str, Any]] = None,
) -> Tuple[plt.Figure, pd.DataFrame]:
    """
    Renders a multi-sample stacked/offset XRD comparison plot with journal styling,
    optional baseline subtraction, normalization, custom legend names, and Bragg guides.
    """
    try:
        from core.background import extract_net_pattern
    except ImportError:
        from xrd_studio.core.background import extract_net_pattern

    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    cfg = plot_config or {}
    custom_labels = custom_labels or {}

    fig_w = float(cfg.get("fig_width", 9.0))
    fig_h = float(cfg.get("fig_height", 6.2))
    screen_dpi = int(cfg.get("screen_dpi", 130))

    title = cfg.get("title", "")
    xlabel = cfg.get("xlabel", r"$\mathbf{2\theta\ (degrees)}$")
    ylabel = cfg.get(
        "ylabel",
        r"$\mathbf{Normalized\ Intensity\ (\%)}$" if normalize_max else r"$\mathbf{Intensity\ (a.u.)}$",
    )
    title_size = int(cfg.get("title_size", 14))
    axis_label_size = int(cfg.get("axis_label_size", 13))
    tick_size = int(cfg.get("tick_size", 11))
    legend_size = int(cfg.get("legend_size", 10))
    show_legend = bool(cfg.get("show_legend", True))
    legend_loc = str(cfg.get("legend_loc", "upper right"))
    legend_frame = bool(cfg.get("legend_frame", True))
    show_hkl_ticks = bool(cfg.get("show_hkl_ticks", True))
    lw = float(cfg.get("line_width", 1.7))

    x_raw = df.iloc[:, 0].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=screen_dpi)

    labplot_dict: Dict[str, np.ndarray] = {"TwoTheta_deg": x_raw}
    valid_curves: List[Tuple[str, np.ndarray, np.ndarray]] = []

    max_span = 1.0
    for col in selected_cols:
        if col not in df.columns:
            continue
        y_col = df[col].to_numpy(dtype=float)
        mask = np.isfinite(x_raw) & np.isfinite(y_col)
        xc, yc = x_raw[mask], y_col[mask]
        if len(xc) < 5:
            continue
        ord_idx = np.argsort(xc)
        xc, yc = xc[ord_idx], yc[ord_idx]
        if strip_bg:
            yc, _ = extract_net_pattern(xc, yc, method=bg_method)
        if normalize_max:
            ym = float(np.nanmax(yc))
            if ym > 0:
                yc = (yc / ym) * 100.0
        max_span = max(max_span, float(np.nanmax(yc) - np.nanmin(yc)))
        valid_curves.append((col, xc, yc))

    auto_step = (max_span * 1.05) if offset_step <= 0.0 else float(offset_step)
    curr_offset = 0.0

    for idx, (col, xc, yc) in enumerate(valid_curves):
        disp_name = custom_labels.get(col, col)
        y_plot = yc + curr_offset
        color = "black" if theme == "Monochrome" else palette[idx % len(palette)]
        ax.plot(xc, y_plot, color=color, lw=lw, label=_mpl_txt(disp_name), zorder=3 + idx)
        labplot_dict[f"{disp_name.replace(' ', '_')}_Shifted"] = np.interp(x_raw, xc, y_plot)
        curr_offset += auto_step

    x_min_cfg = cfg.get("x_min")
    x_max_cfg = cfg.get("x_max")
    finite_x = x_raw[np.isfinite(x_raw)]
    xmin = float(x_min_cfg) if x_min_cfg is not None else float(np.nanmin(finite_x))
    xmax = float(x_max_cfg) if x_max_cfg is not None else float(np.nanmax(finite_x))
    if xmax > xmin:
        ax.set_xlim(xmin, xmax)

    # Optional vertical dashed reference lines for target (hkl) planes
    if show_hkl_ticks and preset_peaks:
        y_top_cur = ax.get_ylim()[1]
        for rp in preset_peaks[:8]:
            rc = float(rp.get("center", 0))
            if xmin <= rc <= xmax:
                ax.axvline(rc, color="#94a3b8", ls=":", lw=1.0, alpha=0.75, zorder=1)
                hkl_txt = str(rp.get("hkl", "") or rp.get("label", ""))
                if hkl_txt:
                    ax.text(
                        rc, y_top_cur * 0.98, f" {hkl_txt}",
                        rotation=90, va="top", ha="left",
                        fontsize=max(tick_size - 2.5, 7.5), color="#475569", fontweight="bold"
                    )

    if title:
        ax.set_title(title, fontsize=title_size, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=axis_label_size, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=axis_label_size, labelpad=10)
    ax.set_yticks([])
    ax.minorticks_on()
    ax.tick_params(axis="x", which="both", direction="in", top=True, labelsize=tick_size)
    ax.tick_params(axis="y", which="both", direction="in", left=True, right=True)

    if show_legend and valid_curves:
        ax.legend(loc=legend_loc, fontsize=legend_size, frameon=legend_frame, framealpha=0.92, edgecolor="#cbd5e1")

    for sp in ax.spines.values():
        sp.set_linewidth(1.5)

    fig.tight_layout()
    return fig, pd.DataFrame(labplot_dict)


def render_williamson_hall_plot(
    wh_results: Dict[str, Any],
    theme: str = "ACS",
    screen_dpi: int = 130,
) -> plt.Figure:
    """Renders Williamson-Hall microstrain regression (beta*cos(theta) vs 4*sin(theta))."""
    set_publication_style()
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES["ACS"])
    fig, ax = plt.subplots(figsize=(6.8, 4.4), dpi=screen_dpi)

    x_arr = wh_results["x_4sin"]
    y_arr = wh_results["y_bcos"]
    y_fit = wh_results["y_fit"]
    labels = wh_results["labels"]

    ax.scatter(x_arr, y_arr, s=64, color=palette[0], edgecolor="#0f172a", zorder=4, label="Fitted Bragg Peaks")
    x_line = np.linspace(0.0, max(float(np.max(x_arr)) * 1.08, 0.5), 100)
    y_line = wh_results["slope_epsilon"] * x_line + wh_results["intercept"]
    ax.plot(x_line, y_line, color="#e11d48", lw=1.8, ls="--", zorder=3, label="Williamson–Hall Fit")

    for xi, yi, lbl in zip(x_arr, y_arr, labels):
        ax.annotate(_mpl_txt(lbl), (xi, yi), xytext=(4, 5), textcoords="offset points", fontsize=8, fontweight="bold", color="#334155")

    d_txt = f"{wh_results['D_wh_nm']:.1f} nm" if np.isfinite(wh_results["D_wh_nm"]) and wh_results["D_wh_nm"] < 2000 else ">1000 nm"
    info = (
        f"Slope (ε) = {wh_results['microstrain_percent']:+.4f}%\n"
        f"Intercept D_WH ≈ {d_txt}\n"
        f"R² = {wh_results['r2_wh']:.4f}"
    )
    ax.text(
        0.04, 0.94, info,
        transform=ax.transAxes, va="top", ha="left", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#94a3b8", alpha=0.92),
    )

    ax.set_xlabel(r"$\mathbf{4\sin\theta}$", fontsize=12)
    ax.set_ylabel(r"$\mathbf{\beta_{corr}\cos\theta\ (rad)}$", fontsize=12)
    ax.set_title("Williamson–Hall Microstrain & Crystallite Size Analysis", fontsize=12, fontweight="bold")
    ax.minorticks_on()
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    return fig
