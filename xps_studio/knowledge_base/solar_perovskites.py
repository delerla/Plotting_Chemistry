"""
solar_perovskites.py - Photovoltaics, Solar Energy & Halide Perovskite XPS Knowledge Bank
Covers: MAPbI3, FAPbI3, CsPbBr3, Pb0 photolysis degradation, halide vacancies, TiO2/SnO2 ETL.
"""

SOLAR_PRESETS = {
    'Perovskite Pb 4f (Lattice vs Metallic Pb⁰)': {
        'core_level': 'Pb 4f',
        'calib_ref': 284.8,
        'is_doublet': True,
        'doublet_delta_eV': 4.86,
        'branching_ratio': 1.333,  # 4f7/2 : 4f5/2 = 4:3 = 1.333
        'description': 'Lead 4f core level. Detects pristine perovskite Pb2+ vs metallic Pb0 clusters formed via photolysis/degradation.',
        'components': [
            {'prefix': 'pb_2plus_72_', 'name': 'Pb²⁺ 4f₇/₂ (Perovskite Lattice)', 'center': 138.4, 'center_tol': 0.30, 'sigma': 0.48, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Stoichiometric [PbI6] octahedra'},
            {'prefix': 'pb_2plus_52_', 'name': 'Pb²⁺ 4f₅/₂ (Perovskite Lattice)', 'center': 143.26, 'center_tol': 0.30, 'sigma': 0.48, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Spin-orbit partner (+4.86 eV)'},
            {'prefix': 'pb_zero_72_', 'name': 'Pb⁰ 4f₇/₂ (Metallic Defect)', 'center': 136.6, 'center_tol': 0.30, 'sigma': 0.45, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Metallic Pb0 non-radiative recombination center'},
            {'prefix': 'pb_zero_52_', 'name': 'Pb⁰ 4f₅/₂ (Metallic Defect)', 'center': 141.46, 'center_tol': 0.30, 'sigma': 0.45, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Spin-orbit partner (+4.86 eV)'},
        ],
        'interpretation_rules': [
            {'metric': 'pb0_degradation_ratio', 'numerator': 'pb_zero_72_', 'denominator': 'pb_2plus_72_', 'unit': '%', 'description': 'Metallic Pb0 photodecomposition / degradation fraction'},
        ]
    },

    'Perovskite I 3d (Iodide vs Triiodide I₃⁻)': {
        'core_level': 'I 3d',
        'calib_ref': 284.8,
        'is_doublet': True,
        'doublet_delta_eV': 11.50,
        'branching_ratio': 1.50,  # 3d5/2 : 3d3/2 = 3:2 = 1.50
        'description': 'Iodine 3d core level. Resolves pristine iodide I- from oxidized polyiodide (I3-) degradation products.',
        'components': [
            {'prefix': 'i_minus_52_', 'name': 'I⁻ 3d₅/₂ (Lattice Iodide)', 'center': 619.3, 'center_tol': 0.30, 'sigma': 0.52, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Coordinated I- in perovskite cage'},
            {'prefix': 'i_minus_32_', 'name': 'I⁻ 3d₃/₂ (Lattice Iodide)', 'center': 630.8, 'center_tol': 0.30, 'sigma': 0.52, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Spin-orbit partner (+11.50 eV)'},
            {'prefix': 'i_ox_52_', 'name': 'I₃⁻ / I⁰ 3d₅/₂ (Oxidized / Volatile)', 'center': 620.6, 'center_tol': 0.35, 'sigma': 0.55, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Photo-oxidized iodine species'},
            {'prefix': 'i_ox_32_', 'name': 'I₃⁻ / I⁰ 3d₃/₂ (Oxidized / Volatile)', 'center': 632.1, 'center_tol': 0.35, 'sigma': 0.55, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Spin-orbit partner (+11.50 eV)'},
        ]
    },

    'ETL TiO₂ / Ti 2p (Ti⁴⁺ vs Ti³⁺ Defect)': {
        'core_level': 'Ti 2p',
        'calib_ref': 284.8,
        'is_doublet': True,
        'doublet_delta_eV': 5.70,
        'branching_ratio': 2.0,  # 2p3/2 : 2p1/2 = 2:1 = 2.0
        'description': 'Titanium 2p core level in electron transport layer (ETL). Quantifies oxygen vacancy defects (Ti3+).',
        'components': [
            {'prefix': 'ti_4plus_32_', 'name': 'Ti⁴⁺ 2p₃/₂ (Stoichiometric TiO₂)', 'center': 458.6, 'center_tol': 0.30, 'sigma': 0.58, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Pristine Ti(IV) in TiO2 lattice'},
            {'prefix': 'ti_4plus_12_', 'name': 'Ti⁴⁺ 2p₁/₂ (Stoichiometric TiO₂)', 'center': 464.3, 'center_tol': 0.30, 'sigma': 0.58, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Spin-orbit partner (+5.70 eV)'},
            {'prefix': 'ti_3plus_32_', 'name': 'Ti³⁺ 2p₃/₂ (Oxygen Vacancy)', 'center': 457.0, 'center_tol': 0.35, 'sigma': 0.62, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Oxygen vacancy shallow donor defect'},
            {'prefix': 'ti_3plus_12_', 'name': 'Ti³⁺ 2p₁/₂ (Oxygen Vacancy)', 'center': 462.7, 'center_tol': 0.35, 'sigma': 0.62, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Spin-orbit partner (+5.70 eV)'},
        ],
        'interpretation_rules': [
            {'metric': 'oxygen_vacancy_ratio', 'numerator': 'ti_3plus_32_', 'denominator': 'ti_4plus_32_', 'unit': '%', 'description': 'Oxygen vacancy defect percentage in TiO2 ETL'}
        ]
    },

    'ETL SnO₂ / Sn 3d (Sn⁴⁺ vs Sn²⁺)': {
        'core_level': 'Sn 3d',
        'calib_ref': 284.8,
        'is_doublet': True,
        'doublet_delta_eV': 8.41,
        'branching_ratio': 1.5,  # 3d5/2 : 3d3/2 = 3:2 = 1.5
        'description': 'Tin 3d core level in SnO2 ETL or lead-free tin perovskite. Tracks Sn(IV) vs reduced Sn(II) defect states.',
        'components': [
            {'prefix': 'sn_4plus_52_', 'name': 'Sn⁴⁺ 3d₅/₂ (SnO₂)', 'center': 486.6, 'center_tol': 0.30, 'sigma': 0.55, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Pristine Sn(IV) in SnO2 ETL'},
            {'prefix': 'sn_4plus_32_', 'name': 'Sn⁴⁺ 3d₃/₂ (SnO₂)', 'center': 495.01, 'center_tol': 0.30, 'sigma': 0.55, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Spin-orbit partner (+8.41 eV)'},
            {'prefix': 'sn_2plus_52_', 'name': 'Sn²⁺ 3d₅/₂ (Sub-oxide / Defect)', 'center': 485.6, 'center_tol': 0.35, 'sigma': 0.58, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Sub-stoichiometric Sn(II) defect'},
            {'prefix': 'sn_2plus_32_', 'name': 'Sn²⁺ 3d₃/₂ (Sub-oxide / Defect)', 'center': 494.01, 'center_tol': 0.35, 'sigma': 0.58, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Spin-orbit partner (+8.41 eV)'},
        ]
    }
}
