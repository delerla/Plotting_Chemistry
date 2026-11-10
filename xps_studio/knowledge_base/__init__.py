"""
xps_studio.knowledge_base - Unified Spectral Knowledge & Domain Catalog
"""

from .scofield_rsf import SCOFIELD_RSF, get_rsf
from .mofs import MOF_PRESETS
from .solar_perovskites import SOLAR_PRESETS
from .polymers_pan import POLYMERS_PRESETS

ALL_DOMAINS = {
    'MOFs & Coordination Networks': MOF_PRESETS,
    'Photovoltaics & Solar Cells': SOLAR_PRESETS,
    'Polymers & Hybrid Nanofibers (PAN)': POLYMERS_PRESETS
}

def get_preset_by_name(name: str):
    """Searches across all domain presets for matching preset dict."""
    for domain, presets in ALL_DOMAINS.items():
        if name in presets:
            return presets[name], domain
    return None, None
