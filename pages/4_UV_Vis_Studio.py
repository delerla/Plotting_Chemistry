"""
UV-Vis Intelligence Studio - Multi-Page Stream Navigation
Domain models for Photodegradation Reaction Kinetics, Tauc Plot Bandgap & Urbach Defect Tail Analysis.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STUDIO_DIR = ROOT_DIR / "uv_vis_studio"

for p in (str(STUDIO_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import runpy
runpy.run_path(str(STUDIO_DIR / "app_uv_vis.py"), run_name="__main__")
