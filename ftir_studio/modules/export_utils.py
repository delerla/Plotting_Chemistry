"""
export_utils.py - Universal publication export, color themes, OriginLab, and LabPlot ASCII matrix formatter.
Includes 600 DPI raster, vector SVG/PDF, OriginLab (.dat & .xlsx), LabPlot (.dat) matrix, and ZIP archive bundling.
"""

import io
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Standard Scientific Journal Publication Palettes
PUBLICATION_PALETTES = {
    'Nature': ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F', '#8491B4', '#91D1C2', '#DC0000'],
    'Science': ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00', '#000000'],
    'ACS': ['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'],
    'RSC': ['#003366', '#B22222', '#2E8B57', '#DAA520', '#4B0082', '#4682B4', '#D2691E', '#708090'],
    'Monochrome': ['#000000', '#404040', '#737373', '#A6A6A6', '#D9D9D9']
}


def set_publication_style():
    """Sets standard academic publication style for matplotlib matching Nature/Science guidelines."""
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
        'lines.linewidth': 1.8,
        'legend.frameon': True,
        'legend.framealpha': 0.92,
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
    """Saves figure in publication-ready raster (600 DPI PNG) and vector (SVG, PDF) formats."""
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
    """Exports a pandas DataFrame into a formatted LabPlot-compatible ASCII matrix."""
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
    """Returns in-memory UTF-8 bytes for LabPlot ASCII download."""
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


def _get_origin_col_letter(idx: int) -> str:
    """Converts 0-based column index to Excel/Origin column notation (0 -> 'A', 25 -> 'Z', 26 -> 'AA')."""
    res = ""
    idx += 1
    while idx > 0:
        idx, remainder = divmod(idx - 1, 26)
        res = chr(65 + remainder) + res
    return res


def get_originlab_ascii_bytes(
    df: pd.DataFrame,
    title: str = "Materials Characterization Matrix",
    units: Optional[Dict[str, str]] = None,
    comments: Optional[Union[List[str], Dict[str, str]]] = None,
    designations: Optional[List[str]] = None,
    delimiter: str = "\t"
) -> bytes:
    """
    Returns in-memory UTF-8 bytes for an OriginLab-compatible ASCII matrix (.dat / .csv).

    Equipped with OriginLab's standard 4-tier column metadata structure:
      - Line 1: Short Names with Origin Column Designations (e.g. A(X), B(Y), C(Y)...)
      - Line 2: Long Names (descriptive column names)
      - Line 3: Units (physical dimensions)
      - Line 4: Comments (spectral/sample provenance)
      - Lines 5+: High-precision numerical data table

    Fully compatible with OriginLab 2018-2026+ drag-and-drop ingestion, File -> Import -> Single ASCII (impASC),
    and OriginLab Data Connectors without requiring manual column type mapping.
    """
    units = units or {}
    num_cols = len(df.columns)

    # 1. Establish Origin column designations: (X) for col 0, (Y) for cols 1..N-1 by default
    if designations and len(designations) == num_cols:
        col_desigs = [d if d.startswith('(') else f"({d})" for d in designations]
    else:
        col_desigs = ['(X)'] + ['(Y)'] * max(0, num_cols - 1)

    short_names = [f"{_get_origin_col_letter(i)}{col_desigs[i]}" for i in range(num_cols)]
    long_names = [str(col) for col in df.columns]
    unit_row = [str(units.get(col, "")) for col in df.columns]

    # Comments row
    if isinstance(comments, dict):
        comment_row = [str(comments.get(col, title)) for col in df.columns]
    elif isinstance(comments, list) and len(comments) == num_cols:
        comment_row = [str(c) for c in comments]
    elif isinstance(comments, list) and len(comments) > 0:
        comment_row = [str(comments[0])] + [str(comments[min(i, len(comments)-1)]) for i in range(1, num_cols)]
    else:
        comment_row = [title] * num_cols

    lines = [
        "# ==============================================================================",
        "# OriginLab Worksheet Data Matrix (.DAT)",
        "# Hub: Automated Materials Characterization & Spectroscopic Analysis Hub",
        f"# Title: {title}",
        f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Total Rows: {len(df)} | Total Columns: {num_cols}",
        "# OriginLab Drag & Drop Instructions:",
        "#   - Drag and drop this file directly into an empty OriginLab worksheet window.",
        "#   - Or use: File -> Import -> Single ASCII (impASC).",
        "#   - Column mapping: (X) = Independent Axis, (Y) = Dependent Profiles.",
        "# ==============================================================================",
    ]
    header_block = "\n".join(lines) + "\n"

    # OriginLab 4 metadata rows
    subheaders = [
        delimiter.join(short_names),
        delimiter.join(long_names),
        delimiter.join(unit_row),
        delimiter.join(comment_row),
    ]
    subheader_block = "\n".join(subheaders) + "\n"

    # Format data rows without pandas header
    data_str = df.to_csv(sep=delimiter, index=False, header=False)
    return (header_block + subheader_block + data_str).encode('utf-8')


def export_originlab_ascii(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    title: str = "Materials Characterization Matrix",
    units: Optional[Dict[str, str]] = None,
    comments: Optional[Union[List[str], Dict[str, str]]] = None,
    designations: Optional[List[str]] = None,
    delimiter: str = "\t"
) -> Path:
    """Exports a pandas DataFrame into a formatted OriginLab-compatible ASCII matrix (.dat)."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    content_bytes = get_originlab_ascii_bytes(
        df=df,
        title=title,
        units=units,
        comments=comments,
        designations=designations,
        delimiter=delimiter
    )
    with open(path, "wb") as f:
        f.write(content_bytes)
    print(f"[EXPORT] Saved OriginLab ASCII Matrix: {path}")
    return path


def get_originlab_excel_bytes(
    df: pd.DataFrame,
    title: str = "Materials Characterization Matrix",
    units: Optional[Dict[str, str]] = None,
    comments: Optional[Union[List[str], Dict[str, str]]] = None,
) -> bytes:
    """
    Exports a pandas DataFrame into an OriginLab-ready Excel (.xlsx) workbook.
    Configured with standard OriginLab 4-row header (Short Name, Long Name, Units, Comments)
    for seamless 1-click import into OriginLab worksheets.
    """
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "OriginLab_Data"

    num_cols = len(df.columns)
    units = units or {}
    short_names = [_get_origin_col_letter(i) for i in range(num_cols)]
    long_names = [str(col) for col in df.columns]
    unit_row = [str(units.get(col, "")) for col in df.columns]
    if isinstance(comments, dict):
        comment_row = [str(comments.get(col, title)) for col in df.columns]
    elif isinstance(comments, list) and len(comments) == num_cols:
        comment_row = [str(c) for c in comments]
    elif isinstance(comments, list) and len(comments) > 0:
        comment_row = [str(comments[0])] + [str(comments[min(i, len(comments) - 1)]) for i in range(1, num_cols)]
    else:
        comment_row = [title] * num_cols

    ws.append(short_names)
    ws.append(long_names)
    ws.append(unit_row)
    ws.append(comment_row)

    for row in df.itertuples(index=False, name=None):
        ws.append(list(row))

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def build_analysis_bundle_zip(
    fig: plt.Figure,
    base_name: str,
    labplot_df: pd.DataFrame,
    summary_data: Optional[Union[pd.DataFrame, Dict[str, Any]]] = None,
    title: str = "Materials Characterization Analysis",
    units: Optional[Dict[str, str]] = None,
    comments: Optional[List[str]] = None
) -> bytes:
    """
    Builds a complete, professional ZIP package containing:
    - 600 DPI publication PNG
    - Vector SVG (editable in Inkscape/Illustrator)
    - Vector PDF (ready for LaTeX publication)
    - OriginLab-compatible ASCII Matrix (.dat)
    - OriginLab-ready Excel Workbook (.xlsx)
    - LabPlot-compatible ASCII Matrix (.dat)
    - Summary Report (.csv or .txt)
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. 600 DPI PNG
        zf.writestr(f"{base_name}_600DPI.png", get_figure_bytes(fig, 'png', dpi=600))
        # 2. Vector SVG
        zf.writestr(f"{base_name}.svg", get_figure_bytes(fig, 'svg'))
        # 3. Vector PDF
        zf.writestr(f"{base_name}.pdf", get_figure_bytes(fig, 'pdf'))
        # 4. OriginLab ASCII Matrix (.dat)
        origin_bytes = get_originlab_ascii_bytes(labplot_df, title=title, units=units, comments=comments)
        zf.writestr(f"{base_name}_OriginLab_Matrix.dat", origin_bytes)
        # 5. OriginLab Excel Workbook (.xlsx)
        try:
            origin_xlsx = get_originlab_excel_bytes(labplot_df, title=title, units=units, comments=comments)
            zf.writestr(f"{base_name}_OriginLab.xlsx", origin_xlsx)
        except Exception as e:
            print(f"[WARN] Failed to write OriginLab Excel: {e}")
        # 6. LabPlot ASCII Matrix (.dat)
        dat_bytes = get_labplot_ascii_bytes(labplot_df, title=title, units=units, comments=comments)
        zf.writestr(f"{base_name}_LabPlot_Matrix.dat", dat_bytes)
        # 7. Summary Diagnostics
        if summary_data is not None:
            if isinstance(summary_data, pd.DataFrame):
                zf.writestr(f"{base_name}_Summary.csv", summary_data.to_csv(index=False))
            elif isinstance(summary_data, dict):
                lines = [f"{k}: {v}" for k, v in summary_data.items() if not isinstance(v, (dict, list))]
                zf.writestr(f"{base_name}_Metrics.txt", "\n".join(lines))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
