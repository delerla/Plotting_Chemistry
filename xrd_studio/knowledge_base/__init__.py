"""
knowledge_base/__init__.py - Registry of all XRD domain knowledge bases.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from .xrd_standards import (
    ANODE_WAVELENGTHS,
    CALIBRATION_STANDARDS,
    INSTRUMENT_BROADENING_PRESETS,
)
from .mofs import MOF_PRESETS
from .solar_perovskites import SOLAR_PEROVSKITE_PRESETS
from .catalysts_oxides import CATALYST_OXIDE_PRESETS
from .polymers_carbon import POLYMER_CARBON_PRESETS

ALL_XRD_DOMAINS = {
    "MOFs & Reticular Frameworks": MOF_PRESETS,
    "Solar Perovskites & PV Absorbers": SOLAR_PEROVSKITE_PRESETS,
    "Catalysts, Oxides & Metal NPs": CATALYST_OXIDE_PRESETS,
    "Polymers, PAN & Carbon Nanofibers": POLYMER_CARBON_PRESETS,
}

DOMAIN_OPTIONS = list(ALL_XRD_DOMAINS.keys())
