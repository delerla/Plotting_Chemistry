"""
file_parser.py - Universal Scientific Data Ingestion, Smart Header Cleaning & Technique Classifier
Supports: CSV, TSV, TXT, DAT, ASC, DPT, PRN, XY, Excel (.xlsx, .xls), OriginLab exports, and Micrographs.
"""

import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


def detect_file_encoding(file_bytes: bytes) -> str:
    """Tries decoding bytes to find valid text encoding."""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'utf-16', 'ascii']
    for enc in encodings:
        try:
            file_bytes[:4096].decode(enc)
            return enc
        except Exception:
            continue
    return 'utf-8'


def clean_origin_excel(wb_or_df: Union[pd.DataFrame, pd.ExcelFile]) -> pd.DataFrame:
    """
    Cleans Excel files exported from OriginLab or standard spreadsheets.
    OriginLab frequently exports tables with:
      Row 0: Short Name (e.g. A, B, C)
      Row 1: Long Name (e.g. Wavenumber, Sample 1)
      Row 2: Units (e.g. cm-1, %)
      Row 3: Comments
      Row 4+: Numerical data
    """
    if isinstance(wb_or_df, pd.ExcelFile):
        # Pick first non-empty sheet
        df_raw = wb_or_df.parse(wb_or_df.sheet_names[0], header=None)
    else:
        df_raw = wb_or_df.copy()

    if df_raw.empty:
        return df_raw

    # Find the first row where mostly numbers appear
    numeric_start_row = None
    for r_idx in range(min(20, len(df_raw))):
        row_vals = df_raw.iloc[r_idx].dropna().tolist()
        if not row_vals:
            continue
        num_count = sum(1 for v in row_vals if is_number(v))
        if len(row_vals) > 0 and (num_count / len(row_vals)) >= 0.5:
            numeric_start_row = r_idx
            break

    if numeric_start_row is None:
        numeric_start_row = 1

    # Extract headers from rows above numeric_start_row
    col_names = []
    num_cols = df_raw.shape[1]
    
    for c_idx in range(num_cols):
        parts = []
        for r_idx in range(numeric_start_row):
            val = str(df_raw.iloc[r_idx, c_idx]).strip()
            if val and val.lower() not in ['nan', 'none', f'col {c_idx+1}']:
                # Avoid duplicate single-letter Short Names like 'A', 'B' if Long Name exists
                if len(val) == 1 and val.isalpha() and r_idx == 0 and numeric_start_row > 1:
                    continue
                parts.append(val)
        
        if parts:
            if len(parts) >= 2 and parts[1] and not parts[1].startswith('('):
                name = f"{parts[0]} ({parts[1]})"
            else:
                name = " - ".join(parts)
        else:
            name = f"Column_{c_idx+1}"
        col_names.append(name)

    # Clean data section
    data_df = df_raw.iloc[numeric_start_row:].copy().reset_index(drop=True)
    data_df.columns = sanitize_column_names(col_names)

    # Convert all columns to numeric where possible
    for col in data_df.columns:
        data_df[col] = pd.to_numeric(
            data_df[col].astype(str).str.replace(',', '.').str.strip(),
            errors='coerce'
        )

    # Drop entirely empty rows and columns
    data_df = data_df.dropna(how='all').dropna(axis=1, how='all')
    return sanitize_spectral_dataframe(data_df)


def sanitize_spectral_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes scientific spectral dataframes:
    1. Removes empty columns and trailing/leading whitespace from headers.
    2. Detects and drops auto-generated index columns (e.g. 'Unnamed: 0', 0-indexed integers).
    3. Coerces all data columns to numeric float values.
    4. Drops rows where the independent variable (X axis / Column 0) is NaN or infinite.
    5. Drops rows where all intensity/signal values (Y columns) are NaN.
    6. Ensures finite coordinates for plotting and fitting.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    clean_df = df.copy()

    # 1. Clean column headers
    clean_df.columns = [re.sub(r'[\r\n\t]+', ' ', str(c)).strip() for c in clean_df.columns]

    # 2. Check if column 0 is a dummy index or entirely NaN
    if clean_df.shape[1] > 1:
        c0 = clean_df.columns[0].lower()
        s0 = clean_df.iloc[:, 0]
        
        is_mostly_nan = s0.isna().mean() > 0.4
        
        is_seq_int = False
        non_null_s0 = s0.dropna()
        if len(non_null_s0) > 3:
            try:
                diffs = np.diff(non_null_s0.astype(float))
                if np.allclose(diffs, 1.0, atol=1e-3) and non_null_s0.iloc[0] in [0, 1]:
                    is_seq_int = True
            except Exception:
                pass

        is_unnamed = c0.startswith('unnamed') or c0 in ['', 'none', 'index', 'idx', 'row', 'col_1', 'col 1']
        
        # If column 0 is an index/unnamed and column 1 has data, drop column 0
        if (is_mostly_nan or is_seq_int or (is_unnamed and not is_number(clean_df.columns[1]))) and clean_df.shape[1] > 2:
            clean_df = clean_df.iloc[:, 1:]
        elif is_mostly_nan and clean_df.shape[1] > 1:
            clean_df = clean_df.iloc[:, 1:]

    # 3. Coerce all columns to numeric
    for col in clean_df.columns:
        if clean_df[col].dtype == object:
            clean_df[col] = pd.to_numeric(
                clean_df[col].astype(str).str.replace(',', '.').str.strip(),
                errors='coerce'
            )
        else:
            clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')

    # 4. Drop entirely empty columns
    clean_df = clean_df.dropna(axis=1, how='all')

    if clean_df.empty or clean_df.shape[1] < 1:
        return clean_df

    # 5. Drop rows where X is NaN, None, or infinite
    x_col = clean_df.columns[0]
    clean_df = clean_df[clean_df[x_col].notna() & np.isfinite(clean_df[x_col])]

    # 6. Drop rows where all Y columns are NaN
    if clean_df.shape[1] > 1:
        clean_df = clean_df[clean_df.iloc[:, 1:].notna().any(axis=1)]

    return clean_df.reset_index(drop=True)


def is_number(s: Any) -> bool:
    """Checks whether an entity can be parsed into float."""
    try:
        val = str(s).strip().replace(',', '.')
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def sanitize_column_names(names: List[str]) -> List[str]:
    """Ensures unique, clean column header strings."""
    seen = {}
    clean = []
    for n in names:
        base = re.sub(r'[\r\n\t]+', ' ', str(n)).strip()
        if not base or base.lower() == 'nan':
            base = "Column"
        if base in seen:
            seen[base] += 1
            clean.append(f"{base}_{seen[base]}")
        else:
            seen[base] = 1
            clean.append(base)
    return clean


def parse_delimited_text(text: str) -> pd.DataFrame:
    """
    Robust text parser that automatically strips comment headers,
    finds table start, determines delimiter, recognizes OriginLab headers,
    and normalizes European vs US decimals.
    """
    lines = text.splitlines()
    if not lines:
        return pd.DataFrame()

    delimiters = ['\t', ',', ';', ' ']
    first_data_idx = -1
    best_delimiter = ','
    
    # 1. Search for first data row (mostly numeric)
    for idx, line in enumerate(lines[:120]):
        line_clean = line.strip()
        if not line_clean or line_clean.startswith(('#', '//', ';', '*', '%', '!', '@')):
            continue

        for d in delimiters:
            parts = [p.strip() for p in (line_clean.split(d) if d != ' ' else re.split(r'\s+', line_clean)) if p.strip()]
            num_count = sum(1 for p in parts if is_number(p))
            if len(parts) >= 2 and (num_count / len(parts)) >= 0.5:
                first_data_idx = idx
                best_delimiter = d
                break
        if first_data_idx != -1:
            break

    if first_data_idx == -1:
        # Fallback to standard pandas read
        try:
            raw_fallback = pd.read_csv(io.StringIO(text), sep=None, engine='python')
            return sanitize_spectral_dataframe(raw_fallback)
        except Exception:
            return pd.DataFrame()

    # Sample data line to know number of columns
    sample_data_line = lines[first_data_idx].strip()
    if best_delimiter == ' ':
        sample_parts = [p.strip() for p in re.split(r'\s+', sample_data_line) if p.strip()]
    else:
        sample_parts = [p.strip() for p in sample_data_line.split(best_delimiter)]
    num_cols = len(sample_parts)

    # 2. Extract potential headers in lines before first_data_idx
    header_rows = []
    for r in range(max(0, first_data_idx - 6), first_data_idx):
        h_line = lines[r].strip().lstrip('#//;*!%@ ')
        if not h_line:
            continue
        if best_delimiter == ' ':
            parts = [p.strip() for p in re.split(r'\s+', h_line) if p.strip()]
        else:
            parts = [p.strip() for p in h_line.split(best_delimiter)]
        if parts and any(parts):
            header_rows.append(parts)

    col_names = []
    # Check for OriginLab style metadata rows (Short Name, Long Name, Units, Comments)
    origin_long_names = None
    origin_units = None

    for row in header_rows:
        label = row[0].lower() if row else ''
        if 'long name' in label or 'name' == label:
            # Drop the label prefix if it is an extra column
            origin_long_names = row[1:] if len(row) > num_cols else row
        elif 'unit' in label:
            origin_units = row[1:] if len(row) > num_cols else row

    # Also detect OriginLab 4-row header with column designations (e.g., A(X), B(Y), etc.)
    if not origin_long_names and len(header_rows) >= 2:
        for idx_h, h_row in enumerate(header_rows):
            if len(h_row) == num_cols and any(re.search(r'\([xyzXYZ]\)', item) for item in h_row):
                if idx_h + 1 < len(header_rows) and len(header_rows[idx_h + 1]) == num_cols:
                    origin_long_names = header_rows[idx_h + 1]
                if idx_h + 2 < len(header_rows) and len(header_rows[idx_h + 2]) == num_cols:
                    origin_units = header_rows[idx_h + 2]
                break

    if origin_long_names and len(origin_long_names) == num_cols:
        for idx, nm in enumerate(origin_long_names):
            u = origin_units[idx] if origin_units and idx < len(origin_units) else ""
            if u and u.lower() not in ['nan', 'none', '']:
                col_names.append(f"{nm} ({u})")
            else:
                col_names.append(nm)
    elif header_rows:
        # Use the closest header row before data that matches column count
        for row in reversed(header_rows):
            if len(row) == num_cols:
                col_names = row
                break
            elif len(row) > num_cols and len(row[1:]) == num_cols:
                col_names = row[1:]
                break

    if not col_names or len(col_names) != num_cols:
        col_names = [f"Col_{i+1}" for i in range(num_cols)]

    # 3. Read data from first_data_idx onwards
    valid_data_lines = []
    for line in lines[first_data_idx:]:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith(('#', '//', ';', '*', '%', '!', '@')):
            continue
        if best_delimiter == ' ':
            parts = [p.strip() for p in re.split(r'\s+', line_clean) if p.strip()]
        else:
            parts = [p.strip() for p in line_clean.split(best_delimiter)]
        # Check if line contains at least one number
        num_count = sum(1 for p in parts if is_number(p))
        if len(parts) == 0 or num_count == 0:
            continue
        valid_data_lines.append(best_delimiter.join(parts))

    joined_data = "\n".join(valid_data_lines)
    df = pd.read_csv(
        io.StringIO(joined_data),
        sep=best_delimiter if best_delimiter != ' ' else r'\s+',
        engine='python',
        header=None,
        decimal=',' if (best_delimiter != ',' and any(',' in l for l in valid_data_lines[:5])) else '.'
    )
    
    actual_cols = min(df.shape[1], len(col_names))
    df = df.iloc[:, :actual_cols]
    df.columns = sanitize_column_names(col_names[:actual_cols])
    
    # Coerce to float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return sanitize_spectral_dataframe(df)


def load_smart_file(
    file_input: Union[str, Path, io.BytesIO, bytes],
    filename: str = ""
) -> Tuple[Optional[pd.DataFrame], Optional[np.ndarray], Dict[str, Any]]:
    """
    Universal ingestion function for scientific files.
    Returns:
        (dataframe_or_None, image_or_None, metadata_dict)
    """
    if isinstance(file_input, (str, Path)):
        p = Path(file_input)
        filename = filename or p.name
        ext = p.suffix.lower()
    else:
        ext = Path(filename).suffix.lower() if filename else ""

    metadata = {
        'filename': filename,
        'format': 'unknown',
        'detected_technique': None,
        'confidence': 0.0,
        'reason': '',
        'rows': 0,
        'columns': []
    }

    # Handle image file inputs for SEM
    img_exts = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp']
    if ext in img_exts:
        import cv2
        if isinstance(file_input, (str, Path)):
            img = cv2.imread(str(file_input), cv2.IMREAD_GRAYSCALE)
        elif isinstance(file_input, (io.BytesIO, bytes)):
            raw_bytes = file_input.getvalue() if isinstance(file_input, io.BytesIO) else file_input
            file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        else:
            img = None

        if img is not None:
            metadata.update({
                'format': 'image',
                'detected_technique': '5. SEM & EDX Microanalysis (SEM)',
                'confidence': 0.98,
                'reason': f"Image file format ({ext or 'raster'}) recognized as SEM micrograph.",
                'image_shape': img.shape
            })
            return None, img, metadata

    # Read binary bytes
    if isinstance(file_input, (str, Path)):
        with open(p, 'rb') as f:
            raw_bytes = f.read()
    elif isinstance(file_input, io.BytesIO):
        raw_bytes = file_input.getvalue()
    else:
        raw_bytes = file_input

    # Check for Excel
    if ext in ['.xlsx', '.xls'] or raw_bytes[:4] == b'PK\x03\x04' or raw_bytes[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
        try:
            excel_file = pd.ExcelFile(io.BytesIO(raw_bytes))
            df = clean_origin_excel(excel_file)
            metadata['format'] = 'Excel Spreadsheet'
        except Exception as e:
            metadata['error'] = f"Failed to parse Excel: {e}"
            return None, None, metadata
    else:
        enc = detect_file_encoding(raw_bytes)
        try:
            text = raw_bytes.decode(enc)
            df = parse_delimited_text(text)
            metadata['format'] = f'Delimited Text ({enc})'
        except Exception as e:
            metadata['error'] = f"Failed to parse text: {e}"
            return None, None, metadata

    if df is not None and not df.empty:
        df = sanitize_spectral_dataframe(df)
        metadata['rows'] = len(df)
        metadata['columns'] = list(df.columns)
        tech, conf, reason = detect_technique(df, filename)
        metadata['detected_technique'] = tech
        metadata['confidence'] = conf
        metadata['reason'] = reason
        return df, None, metadata

    return None, None, metadata


def detect_technique(df: pd.DataFrame, filename: str = "") -> Tuple[str, float, str]:
    """
    Intelligently identifies the characterization method from spectral physics signatures and column headers.
    """
    cols_lower = [str(c).lower() for c in df.columns]
    all_cols_str = " ".join(cols_lower)
    fname_lower = filename.lower()
    
    first_col = df.iloc[:, 0].dropna()
    first_col = first_col[np.isfinite(first_col)]
    if len(first_col) == 0:
        return "Unknown", 0.0, "Empty data"
        
    x_min, x_max = float(np.nanmin(first_col)), float(np.nanmax(first_col))
    x_ptp = abs(x_max - x_min)

    # 1. FTIR Spectroscopy
    ftir_keywords = ['wavenumber', 'cm-1', 'cm^-1', '%t', 'transmittance', 'ftir', 'ir spectrum', 'attenuance']
    ftir_name_hit = any(k in all_cols_str or k in fname_lower for k in ftir_keywords)
    if ftir_name_hit or (350 <= x_min <= 700 and 3500 <= x_max <= 4500 and x_ptp >= 1500):
        conf = 0.95 if ftir_name_hit else 0.88
        reason = f"Identified FTIR: X-axis spans {x_min:.0f} to {x_max:.0f} cm⁻¹ (mid-IR vibrational spectrum)."
        return "1. FTIR Spectroscopy", conf, reason

    # 2. XRD Crystallography
    xrd_keywords = ['2theta', 'two theta', 'two-theta', '2-theta', '2θ', 'two_theta', 'theta', 'xrd', 'diffraction', 'degree']
    xrd_name_hit = any(k in all_cols_str or k in fname_lower for k in xrd_keywords)
    if xrd_name_hit or (5 <= x_min <= 30 and 45 <= x_max <= 140 and x_ptp <= 120):
        conf = 0.95 if xrd_name_hit else 0.85
        reason = f"Identified XRD: 2θ angle signature ({x_min:.1f}° to {x_max:.1f}°) characteristic of Bragg diffraction."
        return "2. XRD Crystallography", conf, reason

    # 3. UV-Vis & Photodegradation Kinetics
    uv_keywords = ['wavelength', 'nm', 'absorbance', 'abs', 'od', 'uv-vis', 'uv_vis', 'uvvis', 'degradation', 'kinetics']
    uv_name_hit = any(k in all_cols_str or k in fname_lower for k in uv_keywords)
    if uv_name_hit or (180 <= x_min <= 400 and 650 <= x_max <= 1100 and x_ptp >= 200):
        conf = 0.95 if uv_name_hit else 0.85
        reason = f"Identified UV-Vis: Optical wavelength range ({x_min:.0f} to {x_max:.0f} nm) for electronic absorption."
        return "3. UV-Vis & Dye Kinetics", conf, reason

    # 4. XPS Core-Level Deconvolution
    xps_keywords = ['binding energy', 'binding_energy', 'be (ev)', 'be_ev', 'kinetic energy', 'cps', 'counts/s', 'xps', 'c 1s', 'o 1s', 'n 1s']
    xps_name_hit = any(k in all_cols_str or k in fname_lower for k in xps_keywords)
    if xps_name_hit or ('cps' in all_cols_str or (270 <= x_min <= 300 and 280 <= x_max <= 315)):
        conf = 0.95 if xps_name_hit else 0.82
        reason = f"Identified XPS: Binding energy profile ({x_min:.1f} to {x_max:.1f} eV) matches core-level electron emission."
        return "4. XPS Core Deconvolution", conf, reason

    # 5. EDX Microanalysis
    edx_keywords = ['kev', 'energy (kev)', 'edx', 'eds', 'energy_kev', 'x-ray energy']
    edx_name_hit = any(k in all_cols_str or k in fname_lower for k in edx_keywords)
    if edx_name_hit or (0 <= x_min <= 1.0 and 5.0 <= x_max <= 25.0):
        conf = 0.92 if edx_name_hit else 0.80
        reason = f"Identified EDX: X-ray energy dispersion ({x_min:.2f} to {x_max:.2f} keV)."
        return "5. SEM & EDX Microanalysis", conf, reason

    # Fallback
    return "1. FTIR Spectroscopy", 0.50, "Default selection: please verify target technique."
