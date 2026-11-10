"""
polymers_pan.py - Polyacrylonitrile (PAN), Nanofibers & Hybrid Composites Knowledge Bank
Covers: PAN electrospun fibers, PAN+MOFs, PAN+ZnO, nitrile C≡N, cyclization index, and nitrogen states.
"""

POLYMERS_PRESETS = {
    'PAN Electrospun Nanofibers / C 1s': {
        'core_level': 'C 1s',
        'calib_ref': 284.8,
        'description': 'Polyacrylonitrile (PAN) C 1s. Resolves aliphatic backbone, nitrile carbon, and additive/solvent residues.',
        'components': [
            {'prefix': 'c_aliphatic_', 'name': 'Aliphatic C-C / C-H', 'center': 284.8, 'center_tol': 0.20, 'sigma': 0.50, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'PAN polymer hydrocarbon backbone (-CH2-CH-)'},
            {'prefix': 'c_nitrile_', 'name': 'Nitrile C≡N', 'center': 285.6, 'center_tol': 0.25, 'sigma': 0.52, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Nitrile carbon in acrylonitrile units'},
            {'prefix': 'c_oxygenated_', 'name': 'C-O / Surface Oxidation', 'center': 286.6, 'center_tol': 0.30, 'sigma': 0.55, 'gamma': 0.25, 'color': '#ff7f0e', 'meaning': 'Hydroxyl/ether or residual spinning solvent (DMF)'},
            {'prefix': 'c_carbonyl_', 'name': 'C=O / Additive', 'center': 288.4, 'center_tol': 0.35, 'sigma': 0.58, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Carbonyl group from comonomer (itaconic/acrylic acid) or MOF linker'},
        ]
    },

    'PAN Nitrile & Cyclization / N 1s': {
        'core_level': 'N 1s',
        'calib_ref': 284.8,
        'description': 'Nitrogen 1s in PAN fibers. Quantifies pristine nitrile C≡N vs cyclized pyridine-like N and oxidation.',
        'components': [
            {'prefix': 'n_cyclized_imine_', 'name': 'Pyridine-like / Cyclized N', 'center': 398.5, 'center_tol': 0.25, 'sigma': 0.52, 'gamma': 0.25, 'color': '#d62728', 'meaning': 'Cyclized tetrahydropyridine ring formed during stabilization'},
            {'prefix': 'n_nitrile_', 'name': 'Pristine Nitrile C≡N', 'center': 399.4, 'center_tol': 0.25, 'sigma': 0.52, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Unreacted linear nitrile groups'},
            {'prefix': 'n_amine_amide_', 'name': 'Amide / Pyrrolic N', 'center': 400.5, 'center_tol': 0.30, 'sigma': 0.56, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Crosslinked or comonomer amine/amide groups'},
            {'prefix': 'n_quaternary_ox_', 'name': 'Quaternary / Oxidized N-O', 'center': 401.9, 'center_tol': 0.35, 'sigma': 0.65, 'gamma': 0.30, 'color': '#9467bd', 'meaning': 'Surface oxidized nitrogen species'},
        ],
        'interpretation_rules': [
            {'metric': 'cyclization_index', 'numerator': 'n_cyclized_imine_', 'denominator': ['n_nitrile_', 'n_cyclized_imine_'], 'unit': '%', 'description': 'Thermal cyclization degree (extent of ladder polymer formation)'}
        ]
    },

    'PAN+ZnO Composite / Zn 2p': {
        'core_level': 'Zn 2p',
        'calib_ref': 284.8,
        'is_doublet': True,
        'doublet_delta_eV': 23.10,
        'branching_ratio': 2.0,  # 2p3/2 : 2p1/2 = 2:1 = 2.0
        'description': 'Zinc 2p in PAN+ZnO hybrid nanofibers. Verifies Zn2+ coordination in wurtzite nanoparticles.',
        'components': [
            {'prefix': 'zn_2plus_32_', 'name': 'Zn²⁺ 2p₃/₂ (ZnO Lattice)', 'center': 1021.7, 'center_tol': 0.30, 'sigma': 0.60, 'gamma': 0.25, 'color': '#1f77b4', 'meaning': 'Zn(II) in ZnO wurtzite crystal embedded in PAN'},
            {'prefix': 'zn_2plus_12_', 'name': 'Zn²⁺ 2p₁/₂ (ZnO Lattice)', 'center': 1044.8, 'center_tol': 0.30, 'sigma': 0.60, 'gamma': 0.25, 'color': '#2ca02c', 'meaning': 'Spin-orbit partner (+23.10 eV)'},
        ]
    }
}
