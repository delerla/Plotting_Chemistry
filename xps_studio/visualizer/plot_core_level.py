"""
plot_core_level.py - Publication-Grade Core-Level XPS Figure & Matrix Generator
Supports fully editable typography, custom legend labels/placement, multi-mode peak annotations,
drop-lines, scientific fit-quality boxes, scatter/line raw data rendering, and LabPlot ASCII export.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from modules.export_utils import PUBLICATION_PALETTES, set_publication_style


def _format_peak_annotation(name: str, metrics: Dict[str, Any], mode: str) -> str:
    """Formats on-plot peak annotation text according to user selection."""
    be = metrics.get('Binding_Energy_eV', 0.0)
    pct = metrics.get('Area_Percent', 0.0)
    if mode == "Name Only":
        return name
    elif mode == "Binding Energy (eV)":
        return f"{be:.2f} eV"
    elif mode == "Name + BE":
        return f"{name}\n({be:.2f} eV)"
    elif mode == "Name + BE + Area%":
        return f"{name}\n{be:.2f} eV ({pct:.1f}%)"
    return ""


def render_core_level_plot(
    x_be: np.ndarray,
    y_raw: np.ndarray,
    baseline: np.ndarray,
    fit_result: Any,
    components_curves: Dict[str, np.ndarray],
    components_summary: Dict[str, Dict[str, Any]],
    core_label: str = "C 1s",
    theme: str = "ACS",
    fig_size: Tuple[float, float] = (8.5, 7.5),
    plot_config: Optional[Dict[str, Any]] = None
) -> Tuple[plt.Figure, pd.DataFrame]:
    """
    Renders high-resolution XPS figure with configurable residuals panel,
    editable titles/axes/legend, and on-plot peak callouts.
    """
    set_publication_style()
    cfg = plot_config or {}
    palette = PUBLICATION_PALETTES.get(theme, PUBLICATION_PALETTES['ACS'])

    # Extract layout & typography config
    show_residuals = cfg.get('show_residuals', True)
    invert_xaxis = cfg.get('invert_xaxis', True)
    show_yticks = cfg.get('show_yticks', True)
    show_grid = cfg.get('show_grid', False)
    raw_style = cfg.get('raw_style', 'Open Circles')

    title_text = cfg.get('title', f"{core_label} High-Resolution Deconvolution")
    xlabel_text = cfg.get('xlabel', "Binding Energy (eV)")
    ylabel_text = cfg.get('ylabel', "Intensity (Counts / s)")
    res_ylabel_text = cfg.get('res_ylabel', "ΔI")

    title_fs = float(cfg.get('title_fontsize', 13.5))
    label_fs = float(cfg.get('label_fontsize', 12.5))
    tick_fs = float(cfg.get('tick_fontsize', 10.5))
    font_weight = 'bold' if cfg.get('font_bold', True) else 'normal'

    show_legend = cfg.get('show_legend', True)
    legend_title = cfg.get('legend_title', "Chemical States")
    legend_loc = cfg.get('legend_loc', "upper left")
    legend_fs = float(cfg.get('legend_fontsize', 8.8))
    legend_raw_label = cfg.get('legend_raw_label', "Experimental Data")
    legend_bg_label = cfg.get('legend_bg_label', "Shirley Baseline")
    legend_env_label = cfg.get('legend_env_label', "Envelope Fit")
    legend_include_stats = cfg.get('legend_include_stats', True)

    peak_label_mode = cfg.get('peak_label_mode', "None")
    peak_label_rot = int(cfg.get('peak_label_rotation', 0))
    peak_label_fs = float(cfg.get('peak_label_fontsize', 8.5))
    peak_label_offset_pct = float(cfg.get('peak_label_offset_pct', 5.0))
    show_drop_lines = cfg.get('show_drop_lines', False)

    show_stats_box = cfg.get('show_stats_box', False)
    stats_extras = cfg.get('stats_extras', {})

    actual_size = (float(cfg.get('fig_width', fig_size[0])), float(cfg.get('fig_height', fig_size[1])))

    # Ensure descending BE order internally for clean LabPlot output
    if x_be[0] < x_be[-1]:
        idx_rev = np.argsort(x_be)[::-1]
        x_be = x_be[idx_rev]
        y_raw = y_raw[idx_rev]
        baseline = baseline[idx_rev]
        best_fit = fit_result.best_fit[idx_rev]
        comp_curves_clean = {k: v[idx_rev] for k, v in components_curves.items()}
    else:
        best_fit = fit_result.best_fit
        comp_curves_clean = components_curves

    total_fit_with_bg = best_fit + baseline
    residuals = y_raw - total_fit_with_bg

    fig = plt.figure(figsize=actual_size, dpi=300)

    if show_residuals:
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 4.2], hspace=0.06)
        ax_res = fig.add_subplot(gs[0])
        ax_res.plot(x_be, residuals, color='#111111', lw=1.0)
        ax_res.axhline(0, color='gray', ls='--', lw=0.9, alpha=0.8)
        ax_res.set_ylabel(res_ylabel_text, fontsize=max(9.0, label_fs - 1.5), fontweight=font_weight, labelpad=6)
        ax_res.tick_params(axis='both', which='both', direction='in', top=True, right=True, labelbottom=False, labelsize=max(8.0, tick_fs - 1.0))
        if not show_yticks:
            ax_res.set_yticks([])
        if title_text.strip():
            ax_res.set_title(title_text, fontsize=title_fs, fontweight=font_weight, pad=10)
        ax_main = fig.add_subplot(gs[1], sharex=ax_res)
        axes_to_style = (ax_res, ax_main)
    else:
        ax_main = fig.add_subplot(111)
        if title_text.strip():
            ax_main.set_title(title_text, fontsize=title_fs, fontweight=font_weight, pad=10)
        axes_to_style = (ax_main,)

    # Plot Raw Experimental Data
    if raw_style == "Open Circles":
        ax_main.scatter(x_be, y_raw, facecolors='none', edgecolors='#111111', s=18, linewidths=0.9, alpha=0.85, label=legend_raw_label, zorder=2)
    elif raw_style == "Solid Dots":
        ax_main.scatter(x_be, y_raw, color='#111111', s=14, alpha=0.75, label=legend_raw_label, zorder=2)
    elif raw_style == "Thin Line":
        ax_main.plot(x_be, y_raw, color='#222222', lw=1.1, alpha=0.85, label=legend_raw_label, zorder=2)
    else:  # Dots + Line
        ax_main.plot(x_be, y_raw, color='#555555', lw=0.8, alpha=0.5, zorder=1)
        ax_main.scatter(x_be, y_raw, color='#111111', s=12, alpha=0.8, label=legend_raw_label, zorder=2)

    # Shirley Baseline
    if legend_bg_label.strip():
        ax_main.plot(x_be, baseline, color='#666666', lw=1.4, ls='--', label=legend_bg_label, zorder=3)
    else:
        ax_main.plot(x_be, baseline, color='#666666', lw=1.4, ls='--', zorder=3)

    # Total Fit Envelope
    env_color = '#111111' if theme == 'Monochrome' else 'crimson'
    ax_main.plot(x_be, total_fit_with_bg, color=env_color, lw=2.0, label=legend_env_label, zorder=5)

    labplot_dict = {
        'Binding_Energy_eV': x_be,
        'Experimental_CPS': y_raw,
        'Shirley_Baseline': baseline,
        'Envelope_Fit': total_fit_with_bg,
        'Residuals': residuals
    }

    y_span = float(np.nanmax(y_raw) - np.nanmin(baseline))
    if y_span <= 0:
        y_span = float(np.nanmax(y_raw)) or 1.0

    # Shaded Peak Components & Peak Annotations
    comp_list = list(components_summary.items())
    peak_top_max = float(np.nanmax(y_raw))

    for idx, (name, metrics) in enumerate(comp_list):
        pfx = metrics['prefix']
        curve = comp_curves_clean.get(pfx, np.zeros_like(x_be))
        comp_with_bg = curve + baseline

        # Use custom color if provided by component editor, else fallback to theme palette
        custom_col = metrics.get('Color')
        if theme == 'Monochrome':
            color = 'black'
        elif custom_col and isinstance(custom_col, str) and custom_col.startswith('#'):
            color = custom_col
        else:
            color = palette[idx % len(palette)]

        if legend_include_stats:
            lab_name = f"{name} ({metrics['Binding_Energy_eV']:.2f} eV, {metrics['Area_Percent']:.1f}%)"
        else:
            lab_name = name

        ax_main.plot(x_be, comp_with_bg, color=color, lw=1.5, ls='-', zorder=4)
        ax_main.fill_between(x_be, baseline, comp_with_bg, color=color, alpha=0.25, label=lab_name, zorder=3)

        # Clean column name for LabPlot
        safe_col_name = name.replace(' ', '_').replace('/', '_')
        labplot_dict[f"Comp_{safe_col_name}"] = comp_with_bg

        # On-plot Peak Labels & Drop Lines
        apex_idx = int(np.argmax(curve))
        apex_x = float(x_be[apex_idx])
        apex_y = float(comp_with_bg[apex_idx])
        apex_bg = float(baseline[apex_idx])

        if show_drop_lines:
            ax_main.plot([apex_x, apex_x], [apex_bg, apex_y], color=color, lw=1.0, ls=':', alpha=0.9, zorder=4)

        if peak_label_mode != "None":
            ann_text = _format_peak_annotation(name, metrics, peak_label_mode)
            y_offset = y_span * (peak_label_offset_pct / 100.0)
            y_ann = apex_y + y_offset
            peak_top_max = max(peak_top_max, y_ann + y_span * 0.12)

            if show_drop_lines:
                ax_main.annotate(
                    ann_text,
                    xy=(apex_x, apex_y),
                    xytext=(apex_x, y_ann),
                    ha='center',
                    va='bottom',
                    rotation=peak_label_rot,
                    fontsize=peak_label_fs,
                    fontweight='semibold',
                    color='#111111' if theme == 'Monochrome' else color,
                    arrowprops=dict(arrowstyle='-', color=color, lw=0.9, ls='--', shrinkA=0, shrinkB=2),
                    zorder=6
                )
            else:
                ax_main.text(
                    apex_x, y_ann, ann_text,
                    ha='center',
                    va='bottom',
                    rotation=peak_label_rot,
                    fontsize=peak_label_fs,
                    fontweight='semibold',
                    color='#111111' if theme == 'Monochrome' else color,
                    zorder=6
                )

    # Set Y-limits with generous headroom if peak annotations are enabled
    y_min_plot = float(np.nanmin(baseline)) - y_span * 0.04
    y_max_plot = max(float(np.nanmax(y_raw)) + y_span * 0.12, peak_top_max)
    ax_main.set_ylim(y_min_plot, y_max_plot)

    # Binding Energy Axis Orientation
    finite_be = x_be[np.isfinite(x_be)]
    if len(finite_be) >= 2:
        be_min, be_max = float(np.nanmin(finite_be)), float(np.nanmax(finite_be))
        if be_max > be_min:
            if invert_xaxis:
                ax_main.set_xlim(be_max, be_min)
            else:
                ax_main.set_xlim(be_min, be_max)

    ax_main.set_xlabel(xlabel_text, fontsize=label_fs, fontweight=font_weight, labelpad=8)
    ax_main.set_ylabel(ylabel_text, fontsize=label_fs, fontweight=font_weight, labelpad=10)
    ax_main.minorticks_on()
    ax_main.tick_params(axis='both', which='both', direction='in', top=True, right=True, labelsize=tick_fs)

    if not show_yticks:
        ax_main.set_yticks([])

    if show_grid:
        ax_main.grid(True, which='major', ls=':', lw=0.6, alpha=0.5, color='#94a3b8')

    # Legend Rendering
    if show_legend:
        if legend_loc == "outside right":
            ax_main.legend(
                loc='upper left', bbox_to_anchor=(1.02, 1.0),
                framealpha=0.94, fontsize=legend_fs,
                title=legend_title if legend_title.strip() else None,
                title_fontsize=legend_fs + 1.0
            )
        else:
            ax_main.legend(
                loc=legend_loc, framealpha=0.92, fontsize=legend_fs,
                title=legend_title if legend_title.strip() else None,
                title_fontsize=legend_fs + 1.0
            )

    # Scientific Fit Quality Box
    if show_stats_box:
        r2_val = stats_extras.get('r2', None)
        redchi_val = stats_extras.get('redchi', None)
        calib_val = stats_extras.get('calib_shift', None)
        lines = []
        if r2_val is not None:
            lines.append(f"$R^2$ = {r2_val:.4f}")
        if redchi_val is not None:
            lines.append(f"$\\chi^2_\\nu$ = {redchi_val:.2f}")
        if calib_val is not None and abs(calib_val) > 1e-4:
            lines.append(f"$\\Delta E_{{cal}}$ = {calib_val:+.2f} eV")
        if lines:
            stats_str = "\n".join(lines)
            box_x = 0.97 if legend_loc == "upper left" else 0.03
            box_ha = 'right' if legend_loc == "upper left" else 'left'
            ax_main.text(
                box_x, 0.95, stats_str,
                transform=ax_main.transAxes,
                ha=box_ha, va='top',
                fontsize=max(8.0, legend_fs),
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#cbd5e1', alpha=0.90),
                zorder=7
            )

    for ax in axes_to_style:
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)

    # Handle margins cleanly (especially with outside legend)
    if legend_loc == "outside right":
        fig.subplots_adjust(left=0.12, right=0.72, top=0.91, bottom=0.11, hspace=0.06)
    else:
        fig.subplots_adjust(left=0.12, right=0.96, top=0.92, bottom=0.11, hspace=0.06)

    labplot_df = pd.DataFrame(labplot_dict)
    return fig, labplot_df
