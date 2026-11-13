"""
sem_edx_studio.knowledge_base.benchmarks
Curated domain benchmarks for SEM Micrographs & EDX Elemental Microanalysis.
Covers MOFs (UiO-66, ZIF-8), Halide Perovskites, Electrospun Nanofibers, and Core-Shell Nanostructures.
"""

from typing import Dict, Any, Tuple
import cv2
import numpy as np
import pandas as pd


SEM_EDX_DOMAINS: Dict[str, Dict[str, Any]] = {
    "Metal-Organic Framework: UiO-66 Octahedra": {
        "material_class": "Zirconium MOF (Zr6O4(OH)4(BDC)6)",
        "morphology": "Interpenetrated Octahedral Nanocrystals",
        "expected_diameter_nm": 320.0,
        "edx_elements": ["C", "O", "Zr"],
        "expected_zr_c_ratio": 0.125,
        "description": "High-symmetry octahedral nanocrystals synthesized via modulated solvothermal synthesis. Sizing distribution reveals uniform crystal growth.",
        "reference": "KAUST Advanced Membranes & Porous Materials / Chem. Mater."
    },
    "Zeolitic Imidazolate Framework: ZIF-8 Dodecahedra": {
        "material_class": "Zinc MOF (Zn(2-methylimidazolate)2)",
        "morphology": "Rhombic Dodecahedral Crystals",
        "expected_diameter_nm": 185.0,
        "edx_elements": ["C", "N", "Zn"],
        "description": "Narrowly distributed sub-200 nm ZIF-8 particles for gas separation and guest molecule encapsulation.",
        "reference": "KFUPM Center of Research Excellence in Nanotechnology"
    },
    "Solar Perovskite: MAPbI3 Polycrystalline Thin Film": {
        "material_class": "Lead Halide Perovskite (CH3NH3PbI3)",
        "morphology": "Dense Polycrystalline Compact Grains",
        "expected_diameter_nm": 450.0,
        "edx_elements": ["C", "N", "Pb", "I"],
        "expected_i_pb_ratio": 3.0,
        "description": "Planar solar cell absorber morphology. Grain size analysis and EDX I/Pb stoichiometric defect validation.",
        "reference": "KACST Sustainable Energy / Nature Photonics"
    },
    "Polymer Nanotechnology: Electrospun PAN Nanofibers": {
        "material_class": "Polyacrylonitrile (PAN) Precursor Web",
        "morphology": "Continuous 1D Cylindrical Nanofibers",
        "expected_diameter_nm": 210.0,
        "edx_elements": ["C", "N"],
        "description": "Electrospun nanofiber mat before thermal stabilization. Feret diameter analysis calculates fiber diameter distribution.",
        "reference": "IAU Carbon Nanotechnology Laboratory"
    },
    "Bimetallic Catalyst: Pt-Ni Core-Shell Nanocages": {
        "material_class": "Electrocatalytic Nanoparticles (Pt3Ni)",
        "morphology": "Truncated Octahedral Nanocages",
        "expected_diameter_nm": 28.0,
        "edx_elements": ["Pt", "Ni", "C"],
        "description": "High-surface-area ORR electrocatalyst for proton-exchange membrane fuel cells. EDX maps Pt/Ni atomic ratios.",
        "reference": "ACS Nano / KAUST Catalysis Center"
    }
}


def generate_uio66_micrograph(width: int = 800, height: int = 600, n_particles: int = 90) -> np.ndarray:
    """Generates synthetic high-resolution SEM micrograph of UiO-66 octahedral crystals."""
    np.random.seed(42)
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    bg = 45 + 15 * xx + 10 * yy + np.random.normal(0, 7, (height, width))
    img = np.clip(bg, 0, 255).astype(np.uint8)

    # Log-normal distribution of crystal sizes centered at ~320 nm (equivalent radius ~22 px)
    radii = np.random.lognormal(mean=3.0, sigma=0.28, size=n_particles)
    radii = np.clip(radii, 10, 42).astype(int)

    for r in radii:
        cx = np.random.randint(r + 10, width - r - 10)
        cy = np.random.randint(r + 10, height - r - 10)
        # Create an approximate faceted octahedral polygon
        n_pts = 6
        angles = np.linspace(0, 2 * np.pi, n_pts, endpoint=False) + np.random.uniform(0, np.pi/3)
        pts = np.array([
            [cx + r * np.cos(a) * np.random.uniform(0.85, 1.15),
             cy + r * np.sin(a) * np.random.uniform(0.85, 1.15)]
            for a in angles
        ], dtype=np.int32)

        # Facet shading
        base_val = np.random.randint(160, 215)
        cv2.fillPoly(img, [pts], int(base_val))
        # Edge highlight typical of SEM secondary electron edge effect
        cv2.polylines(img, [pts], isClosed=True, color=int(min(255, base_val + 40)), thickness=2)

    return cv2.GaussianBlur(img, (3, 3), 0.7)


def generate_perovskite_grains_micrograph(width: int = 800, height: int = 600) -> np.ndarray:
    """Generates synthetic SEM top-view of compact polycrystalline perovskite grains."""
    np.random.seed(101)
    # Voronoi tessellation to mimic compact grains
    n_seeds = 110
    seeds_x = np.random.randint(10, width - 10, n_seeds)
    seeds_y = np.random.randint(10, height - 10, n_seeds)
    
    img = np.full((height, width), 160, dtype=np.uint8)
    # Create grain boundaries
    for i in range(n_seeds):
        cx, cy = seeds_x[i], seeds_y[i]
        r = np.random.randint(18, 48)
        color = int(np.random.randint(130, 210))
        cv2.circle(img, (cx, cy), r, color, -1)
        cv2.circle(img, (cx, cy), r, int(color + 35), 2)

    noise = np.random.normal(0, 10, (height, width))
    img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)
    return cv2.GaussianBlur(img, (3, 3), 0.8)


def generate_uio66_edx_spectrum() -> pd.DataFrame:
    """Generates synthetic EDX spectrum for UiO-66 (C, O, Zr)."""
    energy = np.linspace(0.1, 10.0, 2000)
    bg = 420.0 * np.exp(-0.48 * energy) + 35.0 / (energy + 0.25)
    
    peaks = [
        (0.277, 0.08, 2800),   # C Kα
        (0.525, 0.09, 3900),   # O Kα
        (2.042, 0.12, 4200),   # Zr Lα
        (2.124, 0.12, 1400),   # Zr Lβ
        (2.302, 0.13, 600),    # Zr Lγ
    ]
    y = bg.copy()
    for pos, fwhm, amp in peaks:
        sig = fwhm / 2.355
        y += amp * np.exp(-0.5 * ((energy - pos) / sig) ** 2)

    np.random.seed(42)
    y += np.random.normal(0, 16, len(energy))
    return pd.DataFrame({"Energy_keV": np.round(energy, 4), "Counts": np.clip(np.round(y, 1), 0, None)})


def generate_mapbi3_edx_spectrum() -> pd.DataFrame:
    """Generates synthetic EDX spectrum for MAPbI3 Perovskite (C, N, Pb, I)."""
    energy = np.linspace(0.1, 12.0, 2400)
    bg = 380.0 * np.exp(-0.42 * energy) + 30.0 / (energy + 0.2)
    
    peaks = [
        (0.277, 0.08, 1200),   # C Kα
        (0.392, 0.09, 850),    # N Kα
        (2.342, 0.13, 4900),   # Pb Mα
        (3.937, 0.15, 6800),   # I Lα
        (4.221, 0.16, 2100),   # I Lβ
        (10.551, 0.22, 3100),  # Pb Lα
    ]
    y = bg.copy()
    for pos, fwhm, amp in peaks:
        sig = fwhm / 2.355
        y += amp * np.exp(-0.5 * ((energy - pos) / sig) ** 2)

    np.random.seed(77)
    y += np.random.normal(0, 18, len(energy))
    return pd.DataFrame({"Energy_keV": np.round(energy, 4), "Counts": np.clip(np.round(y, 1), 0, None)})
