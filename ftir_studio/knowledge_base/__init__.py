"""
knowledge_base/__init__.py - Registry of FTIR Vibrational Domain Knowledge Bases.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from .ir_standards import CO2_MASK_RANGE, IR_SPECTRAL_REGIONS
from .polymers_pan import POLYMER_IR_PRESETS
from .mofs import MOF_IR_PRESETS
from .solar_perovskites import SOLAR_PEROVSKITE_IR_PRESETS
from .catalysts_oxides import CATALYST_IR_PRESETS

ALL_FTIR_DOMAINS = {
    "Polymers, PAN & Stabilized Carbon": POLYMER_IR_PRESETS,
    "MOFs & Reticular Frameworks": MOF_IR_PRESETS,
    "Solar Perovskites & Passivation": SOLAR_PEROVSKITE_IR_PRESETS,
    "Catalysts, Metal Oxides & Silica": CATALYST_IR_PRESETS,
}

DOMAIN_OPTIONS = list(ALL_FTIR_DOMAINS.keys())
