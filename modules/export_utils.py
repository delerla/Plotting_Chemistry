"""
export_utils.py - Universal publication export and LabPlot ASCII matrix formatter
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import matplotlib.pyplot as plt
import pandas as pd


def set_publication_style():
    """Sets standard high-quality academic publication style for matplotlib."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'Liberation Sans'],
        'font.size': 12,
        'axes.labelsize': 13,
        'axes.labelweight': 'bold',
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',
        'axes.linewidth': 1.6,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.size': 6.5,
        'xtick.major.width': 1.4,
        'xtick.minor.size': 3.5,
        'xtick.minor.width': 0.9,
        'ytick.major.size': 6.5,
        'ytick.major.width': 1.4,
        'ytick.minor.size': 3.5,
        'ytick.minor.width': 0.9,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'lines.linewidth': 1.6,
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.edgecolor': '0.7',
        'legend.fontsize': 10,
        'figure.autolayout': False,
    })


def save_publication_figure(
    fig: plt.Figure,
    base_filepath: Union[str, Path],
    dpi: int = 600,
    formats: Tuple[str, ...] = ('png', 'svg', 'pdf'),
    close_fig: bool = False
) -> Dict[str, Path]:
    """
    Saves figure in publication-ready raster (600 DPI PNG) and vector (SVG, PDF) formats.
    Returns dict mapping format extension to Path.
    """
    base_path = Path(base_filepath).with_suffix('')
    base_path.parent.mkdir(parents=True, exist_ok=True)
    saved_files = {}

    for fmt in formats:
        out_file = base_path.with_suffix(f'.{fmt}')
        fig.savefig(out_file, dpi=dpi, bbox_inches='tight', format=fmt)
        saved_files[fmt] = out_file
        print(f"[EXPORT] Saved {fmt.upper()}: {out_file}")

    if close_fig:
        plt.close(fig)

    return saved_files


def export_labplot_ascii(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    title: str = "Materials Characterization Matrix",
    units: Optional[Dict[str, str]] = None,
    comments: Optional[List[str]] = None,
    delimiter: str = "\t"
) -> Path:
    """
    Exports a pandas DataFrame into a formatted LabPlot-compatible ASCII matrix.
    Includes metadata headers readable by LabPlot, OriginLab, and QtiPlot.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    units = units or {}
    comments = comments or []

    lines = [
        "# ==============================================================================",
        "# LabPlot ASCII Matrix / Data Table",
        "# Hub: Automated Materials Characterization & Spectroscopic Analysis Hub",
        f"# Title: {title}",
        f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Total Rows: {len(df)} | Total Columns: {len(df.columns)}",
    ]
    for c in comments:
        lines.append(f"# Note: {c}")

    lines.append("# ------------------------------------------------------------------------------")
    lines.append("# Column Definitions:")
    for idx, col in enumerate(df.columns, start=1):
        unit_str = f" [{units[col]}]" if col in units else ""
        lines.append(f"# Column {idx}: {col}{unit_str}")
    lines.append("# ==============================================================================")

    header_block = "\n".join(lines) + "\n"

    # Write header followed by DataFrame data
    with open(path, "w", encoding="utf-8") as f:
        f.write(header_block)
        df.to_csv(f, sep=delimiter, index=False)

    print(f"[EXPORT] Saved LabPlot ASCII Matrix: {path}")
    return path


def get_figure_bytes(fig: plt.Figure, fmt: str, dpi: int = 600) -> bytes:
    """Returns in-memory byte buffer for Streamlit export buttons."""
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()


def get_labplot_ascii_bytes(
    df: pd.DataFrame,
    title: str = "Materials Characterization Matrix",
    units: Optional[Dict[str, str]] = None,
    comments: Optional[List[str]] = None,
    delimiter: str = "\t"
) -> bytes:
    """Returns in-memory UTF-8 bytes for LabPlot ASCII download in Streamlit."""
    units = units or {}
    comments = comments or []
    lines = [
        "# ==============================================================================",
        "# LabPlot ASCII Matrix / Data Table",
        "# Hub: Automated Materials Characterization & Spectroscopic Analysis Hub",
        f"# Title: {title}",
        f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Total Rows: {len(df)} | Total Columns: {len(df.columns)}",
    ]
    for c in comments:
        lines.append(f"# Note: {c}")
    lines.append("# ------------------------------------------------------------------------------")
    lines.append("# Column Definitions:")
    for idx, col in enumerate(df.columns, start=1):
        unit_str = f" [{units[col]}]" if col in units else ""
        lines.append(f"# Column {idx}: {col}{unit_str}")
    lines.append("# ==============================================================================")
    header_block = "\n".join(lines) + "\n"
    csv_str = df.to_csv(sep=delimiter, index=False)
    return (header_block + csv_str).encode('utf-8')
