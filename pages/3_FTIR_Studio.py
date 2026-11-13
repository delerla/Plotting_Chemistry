"""
FTIR Spectroscopy Studio - Multi-Page Stream Navigation
ATR Correction, Advanced Baselines, 2nd-Derivative & Multi-Peak Deconvolution.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STUDIO_DIR = ROOT_DIR / "ftir_studio"

for p in (str(STUDIO_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import runpy
runpy.run_path(str(STUDIO_DIR / "app_ftir.py"), run_name="__main__")
