"""
mofs.py - Metal-Organic Frameworks (MOFs) XPS Knowledge Bank & Spectral Presets
Covers: UiO-66, ZIF-8, HKUST-1, MIL-series, MOF-5, and linker defect quantification.
"""

MOF_PRESETS = {
    'UiO-66 (Zr-BDC) / C 1s': {
        'core_level': 'C 1s',
        'calib_ref': 284.8,
        'description': 'Zr-terephthalate framework C 1s spectrum. Quantifies aromatic linker, defect linker, and carboxylate node coordination.',
        'components': [
            {'prefix': 'c_aromatic_', 'name': 'Aromatic C-C / C-H', 'center': 284.8, 'center_tol': 0.25, 'sigma': 0.52, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Terephthalate (BDC) benzene ring'},
            {'prefix': 'c_defect_', 'name': 'C-OH / Linker Defect', 'center': 286.2, 'center_tol': 0.35, 'sigma': 0.55, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Uncoordinated / missing-linker defect site'},
            {'prefix': 'c_carboxylate_', 'name': 'O-C=O Coordinated', 'center': 288.7, 'center_tol': 0.30, 'sigma': 0.58, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Carboxylate group bound to Zr6 node'},
            {'prefix': 'c_shakeup_', 'name': 'π -> π* Satellite', 'center': 291.5, 'center_tol': 0.50, 'sigma': 0.85, 'gamma': 0.30, 'color': '#9467bd', 'meaning': 'Aromatic ring shake-up transition'},
        ],
        'interpretation_rules': [
            {'metric': 'defect_ratio', 'numerator': 'c_defect_', 'denominator': ['c_aromatic_', 'c_carboxylate_'], 'unit': '%', 'description': 'Missing-linker defect density in UiO-66 framework'},
            {'metric': 'coord_ratio', 'numerator': 'c_carboxylate_', 'denominator': 'c_aromatic_', 'expected': 0.333, 'description': 'Stoichiometric carboxylate/benzene ratio (ideal = 2/6 = 0.333)'}
        ]
    },

    'UiO-66 (Zr-BDC) / Zr 3d': {
        'core_level': 'Zr 3d',
        'calib_ref': 284.8,
        'is_doublet': True,
        'doublet_delta_eV': 2.43,
        'branching_ratio': 1.5,  # 3d5/2 : 3d3/2 = 3:2 = 1.5
        'description': 'Zirconium 3d core level. Resolves fully coordinated Zr4+ cluster vs defective low-coordinate Zr sites.',
        'components': [
            {'prefix': 'zr_4plus_52_', 'name': 'Zr⁴⁺ 3d₅/₂ (Coordinated)', 'center': 182.8, 'center_tol': 0.30, 'sigma': 0.55, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Zr4+ in [Zr6O4(OH)4] oxo-cluster'},
            {'prefix': 'zr_4plus_32_', 'name': 'Zr⁴⁺ 3d₃/₂ (Coordinated)', 'center': 185.23, 'center_tol': 0.30, 'sigma': 0.55, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Spin-orbit partner (+2.43 eV)'},
            {'prefix': 'zr_defect_52_', 'name': 'Zr_defect 3d₅/₂ (Missing Linker)', 'center': 181.9, 'center_tol': 0.35, 'sigma': 0.60, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Low-coordinate Zr site (Lewis acid catalytic site)'},
            {'prefix': 'zr_defect_32_', 'name': 'Zr_defect 3d₃/₂ (Missing Linker)', 'center': 184.33, 'center_tol': 0.35, 'sigma': 0.60, 'gamma': 0.25, 'color': '#ff9896', 'meaning': 'Spin-orbit partner (+2.43 eV)'},
        ]
    },

    'MOF O 1s Cluster & Linker': {
        'core_level': 'O 1s',
        'calib_ref': 284.8,
        'description': 'Oxygen 1s deconvolution separating bridging cluster oxo/hydroxo from carboxylate linker oxygen.',
        'components': [
            {'prefix': 'o_bridging_', 'name': 'M-O-M Bridging (μ₃-O/OH)', 'center': 530.3, 'center_tol': 0.35, 'sigma': 0.60, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Inorganic node bridging oxo/hydroxyl groups'},
            {'prefix': 'o_coordinated_', 'name': 'C-O-M / C=O-M (Coordinated)', 'center': 531.8, 'center_tol': 0.35, 'sigma': 0.62, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Carboxylate oxygen coordinated to metal node'},
            {'prefix': 'o_free_acid_', 'name': 'Free -COOH / Defect', 'center': 533.2, 'center_tol': 0.40, 'sigma': 0.65, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Uncoordinated carboxylic acid terminal group'},
            {'prefix': 'o_water_', 'name': 'Adsorbed H₂O / Solvent', 'center': 534.3, 'center_tol': 0.50, 'sigma': 0.70, 'gamma': 0.30, 'color': '#9467bd', 'meaning': 'Physisorbed moisture or pores solvent'},
        ]
    },

    'ZIF-8 (Zn-Imidazolate) / N 1s': {
        'core_level': 'N 1s',
        'calib_ref': 284.8,
        'description': 'Zeolitic Imidazolate Framework (ZIF-8) nitrogen chemistry.',
        'components': [
            {'prefix': 'n_zn_coord_', 'name': 'Zn-N Coordinated (Imidazolate)', 'center': 398.9, 'center_tol': 0.30, 'sigma': 0.54, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Imidazolate ring nitrogen coordinated to Zn2+ node'},
            {'prefix': 'n_free_defect_', 'name': 'Uncoordinated C-NH Defect', 'center': 400.4, 'center_tol': 0.35, 'sigma': 0.58, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Protonated or uncoordinated 2-methylimidazole defect'},
        ]
    },

    'HKUST-1 (Cu-BTC) / Cu 2p': {
        'core_level': 'Cu 2p',
        'calib_ref': 284.8,
        'is_doublet': True,
        'doublet_delta_eV': 19.8,
        'branching_ratio': 2.0,  # 2p3/2 : 2p1/2 = 2:1 = 2.0
        'description': 'Copper paddlewheel framework. Resolves active Cu2+ paddlewheels vs reduced Cu+ defect sites and shake-up satellites.',
        'components': [
            {'prefix': 'cu_2plus_32_', 'name': 'Cu²⁺ 2p₃/₂ (Paddlewheel)', 'center': 934.7, 'center_tol': 0.35, 'sigma': 0.75, 'gamma': 0.30, 'color': '#1f77b4', 'meaning': 'Intact Cu(II) paddlewheel active site'},
            {'prefix': 'cu_1plus_32_', 'name': 'Cu⁺ / Cu⁰ 2p₃/₂ (Defect/Reduced)', 'center': 932.5, 'center_tol': 0.35, 'sigma': 0.70, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Reduced copper state (defects / vacuum degradation)'},
            {'prefix': 'cu_sat_1_', 'name': 'Cu²⁺ Satellite 1', 'center': 940.8, 'center_tol': 0.50, 'sigma': 1.10, 'gamma': 0.40, 'color': '#aec7e8', 'meaning': 'Characteristic open-shell d9 Cu(II) shake-up'},
            {'prefix': 'cu_sat_2_', 'name': 'Cu²⁺ Satellite 2', 'center': 943.9, 'center_tol': 0.50, 'sigma': 1.20, 'gamma': 0.40, 'color': '#aec7e8', 'meaning': 'Higher energy shake-up satellite'},
            {'prefix': 'cu_2plus_12_', 'name': 'Cu²⁺ 2p₁/₂', 'center': 954.5, 'center_tol': 0.40, 'sigma': 0.85, 'gamma': 0.30, 'color': '#393b79', 'meaning': 'Spin-orbit partner (+19.8 eV)'},
        ]
    }
}
