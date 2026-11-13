"""
SEM-EDX Intelligence Studio - Multi-Page Stream Navigation
Domain models for Micrograph Particle Sizing, Morphological Segmentation & EDX Elemental Microanalysis.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STUDIO_DIR = ROOT_DIR / "sem_edx_studio"

for p in (str(STUDIO_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import runpy
runpy.run_path(str(STUDIO_DIR / "app_sem_edx.py"), run_name="__main__")
