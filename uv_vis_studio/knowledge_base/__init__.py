"""
uv_vis_studio.knowledge_base
"""
from .benchmarks import (
    UV_VIS_DOMAINS,
    generate_rhb_kinetics,
    generate_methylene_blue_kinetics,
    generate_mapbi3_tauc_spectrum,
    generate_tio2_tauc_spectrum,
    generate_gold_nanorods_spectrum,
)

__all__ = [
    "UV_VIS_DOMAINS",
    "generate_rhb_kinetics",
    "generate_methylene_blue_kinetics",
    "generate_mapbi3_tauc_spectrum",
    "generate_tio2_tauc_spectrum",
    "generate_gold_nanorods_spectrum",
]
