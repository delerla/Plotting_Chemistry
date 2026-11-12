"""
saudi_research_databank.py - Comprehensive Institutional Materials & Spectroscopy Knowledge Bank
Curated for: KFUPM, KACST, KAUST, and Imam Abdulrahman Bin Faisal University (IAU - iau.edu.sa).
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

# ==============================================================================
# 1. INSTITUTIONAL CENTERS & RESEARCH PILLARS
# ==============================================================================
SAUDI_INSTITUTIONS = {
    "KAUST": {
        "name": "King Abdullah University of Science and Technology",
        "location": "Thuwal, Makkah Province, Saudi Arabia",
        "badge": "KAUST",
        "website": "https://www.kaust.edu.sa",
        "flagship_centers": [
            "Advanced Membranes and Porous Materials Center (AMPM)",
            "KAUST Solar Center (KSC)",
            "KAUST Catalysis Center (KCC)",
            "Water Desalination and Reuse Center (WDRC)",
        ],
        "primary_focus": "Reticular chemistry (MOFs/COFs), ultra-high efficiency tandem perovskite PV, CO2 capture & conversion, and selective separation membranes.",
    },
    "KFUPM": {
        "name": "King Fahd University of Petroleum and Minerals",
        "location": "Dhahran, Eastern Province, Saudi Arabia",
        "badge": "KFUPM",
        "website": "https://www.kfupm.edu.sa",
        "flagship_centers": [
            "IRC for Membranes and Water Security",
            "IRC for Hydrogen and Energy Storage",
            "IRC for Renewable Energy and Power Systems",
            "Center of Research Excellence in Petroleum Refining & Petrochemicals (CREPP)",
        ],
        "primary_focus": "Electrospun polymer/carbon nanofiber membranes, harsh-environment desert solar cells, gas separation, and crude oil refining catalysis.",
    },
    "KACST": {
        "name": "King Abdulaziz City for Science and Technology",
        "location": "Riyadh, Saudi Arabia",
        "badge": "KACST",
        "website": "https://www.kacst.edu.sa",
        "flagship_centers": [
            "National Center for Carbon Capture and Utilization (NCCCU)",
            "National Center for Solar Energy Technologies",
            "Advanced Materials Research Center",
            "Energy & Water Research Institute",
        ],
        "primary_focus": "National strategic carbon capture, industrial solar deployment, water desalination membranes, and energy transition materials.",
    },
    "IAU": {
        "name": "Imam Abdulrahman Bin Faisal University (iau.edu.sa)",
        "location": "Dammam / Khobar, Eastern Province, Saudi Arabia",
        "badge": "IAU (iau.edu.sa)",
        "website": "https://www.iau.edu.sa",
        "flagship_centers": [
            "Institute for Research and Medical Consultations (IRMC) - Advanced Materials & Nanomaterials",
            "College of Science - Department of Chemistry (Applied Materials & Catalysis)",
            "College of Engineering - Environmental & Water Purification Laboratories",
        ],
        "primary_focus": "Photocatalytic degradation of industrial pollutants, nanocomposite water treatment membranes, metal oxide nanomaterials, and green catalytic synthesis.",
    },
}

RESEARCH_PILLARS = [
    "All Saudi Alliance Research",
    "Carbon Capture, Gas Separation & MOF Porous Frameworks",
    "Perovskite Photovoltaics & Desert-Resilient Solar Absorbers",
    "Water Desalination, Nanofiltration & Polymeric/Carbon Nanofibers",
    "Advanced Catalysis, CO2 Conversion & Metal Oxides",
    "2D Nanomaterials, MXenes & Functional Composites",
]


# ==============================================================================
# 2. CURATED RESEARCH DATABANK ENTRIES (CROSS-AUDITED BENCHMARKS)
# ==============================================================================
SAUDI_RESEARCH_BENCHMARKS = {
    # --------------------------------------------------------------------------
    # PILLAR 1: MOFs, COFs & CARBON CAPTURE
    # --------------------------------------------------------------------------
    "uio66_zr_framework": {
        "id": "uio66_zr_framework",
        "material_name": "UiO-66 (Zr-BDC) Defect-Engineered Framework",
        "pillar": "Carbon Capture, Gas Separation & MOF Porous Frameworks",
        "institutions": ["KAUST", "KFUPM", "KACST", "IAU"],
        "primary_citation": "KAUST AMPM / KFUPM IRC Hydrogen: Reticular defect engineering in Zr-MOFs for enhanced CO2 adsorption and water harvesting.",
        "literature_references": [
            "Eddaoudi et al. (KAUST AMPM), Chem. Mater. & JACS (Reticular porous frameworks for gas sorption).",
            "KFUPM IRC for Hydrogen and Energy Storage: Structural defect modulation of UiO-66 for gas separation.",
            "IAU IRMC / College of Science (iau.edu.sa): Adsorptive removal of organic pollutants using porous Zr-MOF composites.",
            "KACST NCCCU: Scalable solvothermal synthesis of water-stable Zr-MOFs for flue-gas CO2 scrubbers.",
        ],
        "chemical_formula": "Zr6O4(OH)4(BDC)6-x (x = linker defect missingness)",
        "keywords": ["uio-66", "uio66", "zirconium", "mof", "carbon capture", "co2", "framework", "kaust", "kfupm", "iau", "kacst"],
        "xps_benchmarks": {
            "core_level": "Zr 3d & C 1s",
            "binding_energies": {
                "Zr 3d5/2 (Zr-O Node)": 182.7,
                "Zr 3d3/2 (Spin-Orbit)": 185.1,
                "C 1s (Aromatic C-C/C-H)": 284.8,
                "C 1s (Carboxylate O-C=O)": 288.6,
                "C 1s (Defect / Residual Formate)": 286.2,
            },
            "ratio_diagnostic": "Ideal stoichiometric C_arom : C_carboxylate is 3.00:1.00 (6 aromatic C per 2 carboxylate C). Higher ratios indicate linker-missing defect sites or modulating mono-carboxylate ligands.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "(111)", "two_theta": 7.36, "d_A": 12.00, "note": "Primary fcu basal pore reflection"},
                {"hkl": "(200)", "two_theta": 8.48, "d_A": 10.42, "note": "Framework cubic lattice plane"},
                {"hkl": "(022)", "two_theta": 12.01, "d_A": 7.36, "note": "Node connectivity"},
                {"hkl": "(113)", "two_theta": 14.12, "d_A": 6.27, "note": "High-order linker-node correlation"},
                {"hkl": "(222)", "two_theta": 14.74, "d_A": 6.00, "note": "Second-order (111) harmonic"},
                {"hkl": "(006)", "two_theta": 25.68, "d_A": 3.47, "note": "Diagnostic cluster-cluster reflection"},
            ],
            "diagnostic": "Preservation of sharp (111) and (200) peaks confirms structural integrity; broadening or peak shifts indicate missing-cluster/linker defects or pore collapse.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 1692.0, "mode": "ν(C=O) Free -COOH", "diagnostic": "Indicates unwashed residual H2BDC linker inside pores"},
                {"wavenumber": 1582.0, "mode": "ν_as(COO⁻)", "diagnostic": "Asymmetric carboxylate coordination to Zr6 node"},
                {"wavenumber": 1506.0, "mode": "ν(C=C) Phenyl Ring", "diagnostic": "Aromatic skeletal ring vibration"},
                {"wavenumber": 1396.0, "mode": "ν_s(COO⁻)", "diagnostic": "Symmetric carboxylate stretch (Deacon splitting Δν ≈ 186 cm⁻¹)"},
                {"wavenumber": 745.0, "mode": "μ3-O / Zr-O-Zr", "diagnostic": "Characteristic Zr6 octahedral cluster mode"},
                {"wavenumber": 662.0, "mode": "ν(Zr-O)", "diagnostic": "Longitudinal node framework mode"},
            ],
            "diagnostic": "Deacon carboxylate splitting Δν = ν_as − ν_s ≈ 186 cm⁻¹ proves bridging bidentate coordination to the Zr6 node.",
        },
    },

    "zif8_sodalite_framework": {
        "id": "zif8_sodalite_framework",
        "material_name": "ZIF-8 (Zn-2-MeIM) Nanocrystals & Membranes",
        "pillar": "Carbon Capture, Gas Separation & MOF Porous Frameworks",
        "institutions": ["KAUST", "KFUPM", "KACST"],
        "primary_citation": "KAUST AMPM / KFUPM IRC Membranes: Nanoporous ZIF-8 sodalite mixed-matrix membranes for olefin/paraffin and CO2 separation.",
        "literature_references": [
            "Pinnau, Eddaoudi et al. (KAUST AMPM), Adv. Mater. & J. Membr. Sci. (C4 and C3 separation).",
            "KFUPM IRC for Membranes & Water Security: Sub-35 nm ZIF-8 seed layers for high-flux gas separation.",
            "KACST NCCCU: High-temperature hydrothermally stable ZIF-8 carbon capture sorbents.",
        ],
        "chemical_formula": "Zn(2-methylimidazolate)2",
        "keywords": ["zif-8", "zif8", "zinc", "zeolitic", "sodalite", "membrane", "gas separation", "kaust", "kfupm"],
        "xps_benchmarks": {
            "core_level": "Zn 2p & N 1s",
            "binding_energies": {
                "Zn 2p3/2": 1021.8,
                "Zn 2p1/2": 1044.9,
                "N 1s (C-N-Zn Imidazolate)": 399.1,
                "C 1s (Aromatic C-N)": 285.2,
                "C 1s (Methyl C-C)": 284.8,
            },
            "ratio_diagnostic": "Spin-orbit splitting ΔBE(Zn 2p) = 23.1 eV strictly verifies tetrahedral Zn(II) coordination.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "(011)", "two_theta": 7.35, "d_A": 12.02, "note": "Dominant SOD cage reflection"},
                {"hkl": "(002)", "two_theta": 10.38, "d_A": 8.51, "note": "Cubic lattice parameter indicator"},
                {"hkl": "(112)", "two_theta": 12.73, "d_A": 6.95, "note": "Fingerprint SOD plane"},
                {"hkl": "(022)", "two_theta": 14.70, "d_A": 6.02, "note": "Sodalite facet"},
                {"hkl": "(013)", "two_theta": 16.44, "d_A": 5.39, "note": "Mid-angle SOD facet"},
                {"hkl": "(222)", "two_theta": 18.02, "d_A": 4.92, "note": "Body-diagonal high-symmetry plane"},
            ],
            "diagnostic": "Sharp low-angle peaks (<15° 2θ) confirm sodalite cage periodicity; peak FWHM provides nanocrystal size via Scherrer sizing.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 3135.0, "mode": "ν(C-H) Imidazole Ring", "diagnostic": "Aromatic imidazolate C-H stretch"},
                {"wavenumber": 1584.0, "mode": "ν(C=N) Ring", "diagnostic": "2-methylimidazole C=N skeletal vibration"},
                {"wavenumber": 1458.0, "mode": "δ(CH3) Methyl", "diagnostic": "Methyl group deformation"},
                {"wavenumber": 1146.0, "mode": "ν(C-N) Imidazole", "diagnostic": "Intense characteristic ZIF-8 fingerprint"},
                {"wavenumber": 421.0, "mode": "ν(Zn-N)", "diagnostic": "Direct coordination node stretching"},
            ],
            "diagnostic": "The 421 cm⁻¹ Zn-N mode strictly proves successful metal-ligand coordination.",
        },
    },

    "hkust1_cu_framework": {
        "id": "hkust1_cu_framework",
        "material_name": "HKUST-1 / MOF-199 (Cu3(BTC)2) Paddle-Wheel MOF",
        "pillar": "Carbon Capture, Gas Separation & MOF Porous Frameworks",
        "institutions": ["KAUST", "KFUPM", "KACST"],
        "primary_citation": "KAUST AMPM / KFUPM Chemistry: Open metal site Cu-paddlewheel frameworks for selective CO2/CH4 and moisture-stabilized gas separation.",
        "literature_references": [
            "Eddaoudi et al. (KAUST AMPM), Chem. Soc. Rev. (Open metal sites in reticular materials).",
            "KFUPM Chemistry & IRC Membranes: Surface functionalization of HKUST-1 for methane storage.",
            "KACST NCCCU: Humidity-resilient mixed-linker copper MOFs for flue-gas CO2 capture.",
        ],
        "chemical_formula": "Cu3(BTC)2(H2O)3 [BTC = benzene-1,3,5-tricarboxylate]",
        "keywords": ["hkust-1", "hkust1", "mof-199", "copper", "paddle-wheel", "co2", "btc", "kaust", "kfupm"],
        "xps_benchmarks": {
            "core_level": "Cu 2p & O 1s",
            "binding_energies": {
                "Cu 2p3/2 (Cu²⁺ Paddle-Wheel)": 934.8,
                "Cu 2p1/2 (Cu²⁺)": 954.6,
                "Cu 2p3/2 Shake-Up Satellite": 943.2,
                "C 1s (Aromatic C-C)": 284.8,
                "C 1s (Carboxylate O-C=O)": 288.7,
                "O 1s (Cu-O Carboxylate)": 531.8,
            },
            "ratio_diagnostic": "Pronounced shake-up satellite at 943.2 eV is mandatory diagnostic proof of paramagnetic d⁹ Cu²⁺ state. Absence indicates unwanted reduction to Cu⁺ / Cu⁰.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "(200)", "two_theta": 6.72, "d_A": 13.14, "note": "Primary cubic paddlewheel low-angle reflection"},
                {"hkl": "(220)", "two_theta": 9.52, "d_A": 9.28, "note": "Diagnostic Fm-3m lattice reflection"},
                {"hkl": "(222)", "two_theta": 11.64, "d_A": 7.60, "note": "High-symmetry face diagonal"},
                {"hkl": "(400)", "two_theta": 13.46, "d_A": 6.57, "note": "Second-order cubic reflection"},
                {"hkl": "(420)", "two_theta": 15.06, "d_A": 5.88, "note": "Framework window aperture probe"},
            ],
            "diagnostic": "Preservation of low-angle reflections at 6.72° and 9.52° confirms intact open-metal site pore geometry.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 1645.0, "mode": "ν_as(COO⁻)", "diagnostic": "Asymmetric carboxylate coordination to Cu2 paddlewheel"},
                {"wavenumber": 1560.0, "mode": "ν(C=C) Benzene Ring", "diagnostic": "BTC aromatic core ring vibration"},
                {"wavenumber": 1445.0, "mode": "ν_s(COO⁻)", "diagnostic": "Symmetric carboxylate stretch (Deacon splitting Δν ≈ 200 cm⁻¹)"},
                {"wavenumber": 1375.0, "mode": "δ(C-H)", "diagnostic": "Aromatic C-H in-plane deformation"},
                {"wavenumber": 730.0, "mode": "ν(Cu-O)", "diagnostic": "Direct Cu-O paddlewheel coordination node"},
            ],
            "diagnostic": "Deacon splitting Δν = 200 cm⁻¹ strictly proves bridging bidentate coordination across the Cu-Cu dimeric node.",
        },
    },

    # --------------------------------------------------------------------------
    # PILLAR 2: PEROVSKITE PHOTOVOLTAICS & SOLAR
    # --------------------------------------------------------------------------
    "perovskite_fapbi3_solar": {
        "id": "perovskite_fapbi3_solar",
        "material_name": "FA0.85MA0.15PbI3 Perovskite & PbI2 Degradation",
        "pillar": "Perovskite Photovoltaics & Desert-Resilient Solar Absorbers",
        "institutions": ["KAUST", "KFUPM", "KACST"],
        "primary_citation": "KAUST Solar Center (KSC) / KACST Solar: High-performance tandem perovskite/silicon cells and desert outdoor stability testing.",
        "literature_references": [
            "De Wolf, Bakr et al. (KAUST Solar Center), Science & Nature Energy (Outdoor thermal & moisture stability in Saudi desert).",
            "KFUPM Renewable Energy: Compositional engineering of 2D/3D perovskite heterostructures for moisture barriers.",
            "KACST National Solar Technologies: Grid-connected utility-scale photovoltaic module reliability under high UV index.",
        ],
        "chemical_formula": "(FA)0.85(MA)0.15PbI3 (FA = CH(NH2)2⁺, MA = CH3NH3⁺)",
        "keywords": ["perovskite", "fapbi3", "mapbi3", "pbi2", "solar", "photovoltaic", "kaust", "ksc", "kfupm", "kacst"],
        "xps_benchmarks": {
            "core_level": "Pb 4f & I 3d",
            "binding_energies": {
                "Pb 4f7/2 (Perovskite Pb²⁺)": 138.4,
                "Pb 4f5/2 (Perovskite Pb²⁺)": 143.3,
                "Pb 4f7/2 (Metallic Pb⁰ Photolysis)": 136.6,
                "Pb 4f5/2 (Metallic Pb⁰ Photolysis)": 141.5,
                "I 3d5/2 (Iodide I⁻)": 619.1,
                "I 3d3/2 (Iodide I⁻)": 630.8,
            },
            "ratio_diagnostic": "Metallic Pb⁰ doublet at ~136.6 eV points to beam/photothermal reduction; Pb⁰ / (Pb⁰ + Pb²⁺) fraction quantifies photolytic degradation.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "δ-(010)", "two_theta": 11.82, "d_A": 7.48, "note": "Photo-inactive yellow hexagonal phase"},
                {"hkl": "PbI2(001)", "two_theta": 12.67, "d_A": 6.98, "note": "PbI2 decomposition impurity phase"},
                {"hkl": "α-(110)", "two_theta": 14.08, "d_A": 6.28, "note": "Primary black photoactive perovskite reflection"},
                {"hkl": "α-(112)", "two_theta": 19.96, "d_A": 4.44, "note": "Tetragonal/cubic lattice reflection"},
                {"hkl": "α-(220)", "two_theta": 28.44, "d_A": 3.14, "note": "Second-order (110) harmonic"},
                {"hkl": "α-(310)", "two_theta": 31.89, "d_A": 2.80, "note": "High-angle strain marker"},
            ],
            "diagnostic": "PbI2 (001) reflection at 12.67° tracks moisture/thermal degradation; I(PbI2)/[I(PbI2)+I(110)] gives quantitative degradation index.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 1735.0, "mode": "ν(C=O) Free Passivator", "diagnostic": "Uncoordinated additive ester/urea"},
                {"wavenumber": 1712.0, "mode": "ν_as(C=N) FA⁺", "diagnostic": "Formamidinium cation antisymmetric stretch (marker of black α-phase)"},
                {"wavenumber": 1682.0, "mode": "ν(C=O) Pb²⁺-Bound", "diagnostic": "Red-shifted C=O bound to undercoordinated surface Pb²⁺ defects"},
                {"wavenumber": 1622.0, "mode": "δ(H2O) Moisture", "diagnostic": "Hydrated moisture degradation band"},
                {"wavenumber": 1468.0, "mode": "δ_s(NH3⁺) MA⁺", "diagnostic": "Methylammonium symmetric umbrella deformation"},
            ],
            "diagnostic": "Red-shift of additive ν(C=O) by 30-50 cm⁻¹ confirms Lewis-base coordination passivating undercoordinated Pb²⁺ defect traps.",
        },
    },

    "cspbbr3_inorganic_perovskite": {
        "id": "cspbbr3_inorganic_perovskite",
        "material_name": "All-Inorganic CsPbBr3 Perovskite for Extreme Desert Durability",
        "pillar": "Perovskite Photovoltaics & Desert-Resilient Solar Absorbers",
        "institutions": ["KAUST", "KFUPM", "KACST"],
        "primary_citation": "KAUST KSC / KFUPM Physics: Moisture- and thermally-stable all-inorganic CsPbBr3 halide perovskite tandem and optoelectronic devices.",
        "literature_references": [
            "Bakr, De Wolf et al. (KAUST KSC), ACS Energy Lett. (All-inorganic perovskite thermal resilience >85°C).",
            "KFUPM IRC Renewable Energy: Spray-coated CsPbBr3 films for concentrated solar photodetectors.",
            "KACST Solar: Long-term operational photostability of lead halide perovskites without organic cation loss.",
        ],
        "chemical_formula": "CsPbBr3 (Cubic / Orthorhombic phase)",
        "keywords": ["cspbbr3", "inorganic perovskite", "cesium", "lead bromide", "solar", "desert", "kaust", "kfupm"],
        "xps_benchmarks": {
            "core_level": "Cs 3d, Pb 4f & Br 3d",
            "binding_energies": {
                "Cs 3d5/2": 724.2,
                "Cs 3d3/2": 738.1,
                "Pb 4f7/2 (Perovskite Pb²⁺)": 138.6,
                "Pb 4f5/2": 143.5,
                "Br 3d5/2": 68.3,
                "Br 3d3/2": 69.4,
            },
            "ratio_diagnostic": "Stoichiometric atomic ratio Cs : Pb : Br = 1.0 : 1.0 : 3.0 confirms phase-pure inorganic perovskite with minimal halide vacancies.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "(100)", "two_theta": 15.18, "d_A": 5.83, "note": "Characteristic low-angle cubic perovskite reflection"},
                {"hkl": "(110)", "two_theta": 21.56, "d_A": 4.12, "note": "Diagonal lattice plane reflection"},
                {"hkl": "(111)", "two_theta": 26.54, "d_A": 3.36, "note": "High-symmetry octahedron orientation"},
                {"hkl": "(200)", "two_theta": 30.68, "d_A": 2.91, "note": "High-intensity double harmonic reflection"},
                {"hkl": "(210)", "two_theta": 34.42, "d_A": 2.60, "note": "In-plane bromide distortion probe"},
            ],
            "diagnostic": "Sharp single peaks at 15.18° and 30.68° confirm pure cubic Pm-3m phase, while peak splitting indicates orthorhombic Pnma transition.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 1625.0, "mode": "δ(H-O-H)", "diagnostic": "Surface physisorbed water without lattice organic cation degradation"},
                {"wavenumber": 1385.0, "mode": "ν(Cs-Br / Acoustic)", "diagnostic": "Lattice phonon overtones"},
                {"wavenumber": 680.0, "mode": "Surface Hydroxyl", "diagnostic": "Surface passivating metal-OH interaction"},
            ],
            "diagnostic": "Absence of N-H/C-H organic bands (>2800 cm⁻¹) definitively verifies all-inorganic composition resistant to volatilization.",
        },
    },

    # --------------------------------------------------------------------------
    # PILLAR 3: CATALYSIS, CO2 CONVERSION & METAL OXIDES
    # --------------------------------------------------------------------------
    "tio2_catalyst_photocatalysis": {
        "id": "tio2_catalyst_photocatalysis",
        "material_name": "TiO2 Anatase-Rutile Nanocatalysts (P25 / Calcined)",
        "pillar": "Advanced Catalysis, CO2 Conversion & Metal Oxides",
        "institutions": ["KAUST", "KFUPM", "KACST", "IAU"],
        "primary_citation": "KAUST Catalysis / IAU IRMC / KFUPM CREPP: Phase junction engineering in Anatase/Rutile TiO2 for solar water splitting & water decontamination.",
        "literature_references": [
            "Gascon, Takanabe et al. (KAUST Catalysis Center), ACS Catalysis (Solar fuel and water splitting).",
            "KFUPM CREPP & Chemistry: Thermal phase evolution of titanium dioxide for photocatalytic desulfurization.",
            "IAU IRMC / College of Science (iau.edu.sa), Arabian J. Chem.: Silver and carbon-modified TiO2 nanocomposites for visible-light water decontamination.",
            "KACST Advanced Materials: Large-scale photocatalytic purification of industrial wastewater.",
        ],
        "chemical_formula": "TiO2 (Mixed Anatase + Rutile)",
        "keywords": ["tio2", "titania", "anatase", "rutile", "p25", "catalyst", "photocatalysis", "spurr-myers", "kaust", "kfupm", "iau", "kacst"],
        "xps_benchmarks": {
            "core_level": "Ti 2p & O 1s",
            "binding_energies": {
                "Ti 2p3/2 (Ti⁴⁺ Lattice)": 458.7,
                "Ti 2p1/2 (Ti⁴⁺ Lattice)": 464.4,
                "Ti 2p3/2 (Ti³⁺ Defect / Oxygen Vacancy)": 457.1,
                "O 1s (Ti-O Lattice)": 529.9,
                "O 1s (Surface Ti-OH / Oxygen Defect)": 531.5,
                "O 1s (Adsorbed H2O)": 533.0,
            },
            "ratio_diagnostic": "Ti³⁺ sub-band at ~457.1 eV and O_defect (~531.5 eV) quantify oxygen vacancies driving photocatalytic visible-light activity.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "Anatase (101)", "two_theta": 25.28, "d_A": 3.52, "note": "Primary Anatase photocatalytic facet (JCPDS 21-1272)"},
                {"hkl": "Rutile (110)", "two_theta": 27.45, "d_A": 3.25, "note": "Primary Rutile thermodynamic polymorph (JCPDS 21-1276)"},
                {"hkl": "Rutile (101)", "two_theta": 36.08, "d_A": 2.49, "note": "Rutile secondary reflection"},
                {"hkl": "Anatase (004)", "two_theta": 37.80, "d_A": 2.38, "note": "c-axis Anatase elongation probe"},
                {"hkl": "Anatase (200)", "two_theta": 48.05, "d_A": 1.89, "note": "a-axis facet plane"},
            ],
            "diagnostic": "Spurr-Myers equation W_R = 1 / (1 + 0.8 * I_A/I_R) computes exact weight fraction of Rutile vs. Anatase.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 3420.0, "mode": "ν(O-H) Physisorbed Water", "diagnostic": "Surface hydroxyls + physisorbed H2O"},
                {"wavenumber": 1630.0, "mode": "δ(H-O-H)", "diagnostic": "Molecular water scissor bending"},
                {"wavenumber": 1525.0, "mode": "ν_as(CO3²⁻)", "diagnostic": "Chemisorbed surface bidentate carbonate"},
                {"wavenumber": 1385.0, "mode": "ν_s(CO3²⁻)", "diagnostic": "Symmetric carbonate / residual nitrate precursor"},
                {"wavenumber": 545.0, "mode": "ν(Ti-O-Ti)", "diagnostic": "Bulk Ti-O octahedral lattice network"},
            ],
            "diagnostic": "Broad Ti-O lattice envelope below 800 cm⁻¹ with surface Ti-OH hydroxyls (3650-3200 cm⁻¹) essential for radical generation.",
        },
    },

    "cu2o_photocatalyst": {
        "id": "cu2o_photocatalyst",
        "material_name": "Cu/Cu2O/CuO Heterojunctions for CO2 Electroreduction & Solar Fuel",
        "pillar": "Advanced Catalysis, CO2 Conversion & Metal Oxides",
        "institutions": ["KAUST", "KFUPM", "KACST", "IAU"],
        "primary_citation": "KAUST Catalysis / KFUPM Hydrogen / IAU IRMC: Mixed-valence copper oxides for selective C2+ electrochemical reduction of CO2.",
        "literature_references": [
            "Sargent, Cavallo et al. (KAUST KCC), Nature Catalysis & ACS Catal. (Cu+ and Cu0 interface dynamics in CO2 conversion).",
            "KFUPM IRC for Hydrogen and Energy Storage: Nanostructured copper foam electrodes for electrochemical syngas production.",
            "IAU IRMC / College of Science (iau.edu.sa): Cuprous oxide nanoparticle thin films for solar-driven dye degradation.",
        ],
        "chemical_formula": "Cu2O / CuO / Cu composite",
        "keywords": ["cu2o", "cuo", "copper oxide", "co2 reduction", "electrocatalysis", "kaust", "kfupm", "iau", "kacst"],
        "xps_benchmarks": {
            "core_level": "Cu 2p & Cu LMM Auger",
            "binding_energies": {
                "Cu 2p3/2 (Cu⁺ in Cu2O / Cu⁰)": 932.4,
                "Cu 2p3/2 (Cu²⁺ in CuO)": 933.8,
                "Cu 2p3/2 Shake-Up Satellite (CuO)": 942.5,
                "Cu 2p1/2": 952.2,
                "O 1s (Cu2O Lattice)": 530.3,
                "O 1s (CuO Lattice)": 529.6,
            },
            "ratio_diagnostic": "Cu 2p3/2 alone cannot differentiate Cu⁰ (932.6 eV) from Cu⁺ (932.4 eV); modified Auger parameter α' = BE(Cu 2p3/2) + KE(Cu LMM) (1849.2 eV for Cu2O vs 1851.2 eV for Cu metal) is required.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "Cu2O (110)", "two_theta": 29.58, "d_A": 3.02, "note": "Low-index cuprous oxide reflection"},
                {"hkl": "Cu2O (111)", "two_theta": 36.44, "d_A": 2.46, "note": "Dominant active facet for C2+ selectivity"},
                {"hkl": "CuO (-111)", "two_theta": 35.54, "d_A": 2.52, "note": "Cupric oxide secondary phase"},
                {"hkl": "CuO (111)", "two_theta": 38.74, "d_A": 2.32, "note": "Tenorite phase indicator"},
                {"hkl": "Cu2O (200)", "two_theta": 42.32, "d_A": 2.13, "note": "Cubic Cu2O facet plane"},
                {"hkl": "Cu⁰ (111)", "two_theta": 43.32, "d_A": 2.09, "note": "Metallic copper core reflection"},
            ],
            "diagnostic": "Intensity ratio I(111)/I(200) for Cu2O evaluates facet orientation governing CO2-to-ethylene catalytic selectivity.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 612.0, "mode": "ν(Cu-O in Cu2O)", "diagnostic": "Characteristic vibrational mode of Cu(I) cuprous oxide"},
                {"wavenumber": 525.0, "mode": "ν(Cu-O in CuO)", "diagnostic": "Monoclinic tenorite Cu(II) oxide lattice band"},
                {"wavenumber": 1420.0, "mode": "ν_s(CO3²⁻)", "diagnostic": "Surface bicarbonate/carbonate during CO2 reduction"},
            ],
            "diagnostic": "Sharp absorption at 612 cm⁻¹ strictly distinguishes Cu2O from tenorite CuO (525 cm⁻¹).",
        },
    },

    # --------------------------------------------------------------------------
    # PILLAR 4: WATER MEMBRANES, DESALINATION & NANOFIBERS
    # --------------------------------------------------------------------------
    "pan_nanofibers_water_energy": {
        "id": "pan_nanofibers_water_energy",
        "material_name": "Electrospun PAN & Carbon Nanofibers (CNFs)",
        "pillar": "Water Desalination, Nanofiltration & Polymeric/Carbon Nanofibers",
        "institutions": ["KFUPM", "KAUST", "KACST", "IAU"],
        "primary_citation": "KFUPM IRC Membranes / KAUST WDRC / IAU Engineering: Electrospun polyacrylonitrile & carbon nanofiber membranes for oil-water separation and desalination.",
        "literature_references": [
            "KFUPM IRC for Membranes & Water Security, Desalination & J. Membr. Sci. (Superhydrophobic electrospun membranes).",
            "KAUST WDRC: Carbonized nanofiber networks for solar-driven interfacial steam generation.",
            "IAU College of Engineering / IRMC (iau.edu.sa): Heavy metal adsorption and dye separation on functionalized PAN nanofibers.",
            "KACST Advanced Materials: High-toughness carbonized electrospun electrodes for electrochemical desalination (CDI).",
        ],
        "chemical_formula": "(C3H3N)n -> Turbostratic Carbon (C)",
        "keywords": ["pan", "polyacrylonitrile", "cnf", "carbon nanofiber", "electrospun", "membrane", "desalination", "cyclization", "kfupm", "kaust", "iau", "kacst"],
        "xps_benchmarks": {
            "core_level": "C 1s & N 1s",
            "binding_energies": {
                "C 1s (Aliphatic C-C)": 284.8,
                "C 1s (Nitrile C≡N)": 285.5,
                "C 1s (Ladder C=N/C=C)": 286.3,
                "C 1s (Oxygenated C-O/C=O)": 288.2,
                "N 1s (Nitrile C≡N)": 399.4,
                "N 1s (Pyridinic N Ladder)": 398.5,
                "N 1s (Pyrrolic / Pyridone N)": 400.1,
                "N 1s (Graphitic / Quaternary N)": 401.3,
            },
            "ratio_diagnostic": "Conversion of Nitrile N (399.4 eV) into Pyridinic N (398.5 eV) quantifies thermal cyclization into ladder polymer.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "PAN (100)", "two_theta": 16.92, "d_A": 5.24, "note": "Semi-crystalline nitrile rod-like chain packing"},
                {"hkl": "Amorphous / (002)", "two_theta": 25.60, "d_A": 3.48, "note": "Conjugated ladder sheet stacking (grows with oxidation)"},
                {"hkl": "PAN (110)", "two_theta": 29.50, "d_A": 3.03, "note": "Secondary orthorhombic polymer reflection"},
                {"hkl": "Graphitic (100)", "two_theta": 43.35, "d_A": 2.09, "note": "In-plane sp² honeycomb ordering (La)"},
            ],
            "diagnostic": "Disappearance of sharp PAN (100) at 16.92° and emergence of broad graphitic (002) at ~25.8° measures cyclization into turbostratic carbon.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 2243.0, "mode": "ν(C≡N) Nitrile", "diagnostic": "Unreacted linear polyacrylonitrile nitrile group"},
                {"wavenumber": 1715.0, "mode": "ν(C=O) Pre-Oxidation", "diagnostic": "Oxygen uptake during thermal stabilization"},
                {"wavenumber": 1598.0, "mode": "ν(C=N / C=C) Ladder", "diagnostic": "Aromatized ladder polymer ring"},
                {"wavenumber": 1453.0, "mode": "δ(CH2)", "diagnostic": "Aliphatic methylene scissoring"},
                {"wavenumber": 1368.0, "mode": "δ(C-H)", "diagnostic": "Backbone methine deformation"},
                {"wavenumber": 1265.0, "mode": "ν(C-O / C-N)", "diagnostic": "Cross-linked skeletal ether/ladder mode"},
            ],
            "diagnostic": "Extent of Stabilization E_s = [0.29 · I(1598)] / [I(2243) + 0.29 · I(1598)] tracks chemical aromatization efficiency.",
        },
    },

    "go_rgo_desalination_membrane": {
        "id": "go_rgo_desalination_membrane",
        "material_name": "Graphene Oxide (GO) & Reduced rGO Desalination Membranes",
        "pillar": "Water Desalination, Nanofiltration & Polymeric/Carbon Nanofibers",
        "institutions": ["KAUST", "KFUPM", "KACST", "IAU"],
        "primary_citation": "KAUST AMPM / KFUPM IRC Membranes / IAU IRMC: 2D laminar graphene oxide nanosheet membranes for precise ion sieving and water purification.",
        "literature_references": [
            "Alshareef, Pinnau et al. (KAUST AMPM), Nat. Commun. & ACS Nano (Fast water transport through 2D laminar nanochannels).",
            "KFUPM IRC for Membranes & Water Security: Chemical cross-linking of GO membranes with diamines for swelling suppression in brine.",
            "IAU IRMC / College of Engineering (iau.edu.sa): Graphene oxide-chitosan hybrid hydrogels for toxic heavy metal decontamination.",
            "KACST Advanced Materials: Pilot-scale fabrication of laminar GO reverse-osmosis support layers.",
        ],
        "chemical_formula": "C10O1(OH)1(COOH)0.5 -> Reduced Graphene (rGO)",
        "keywords": ["go", "rgo", "graphene oxide", "membrane", "desalination", "water", "sieving", "kaust", "kfupm", "iau", "kacst"],
        "xps_benchmarks": {
            "core_level": "C 1s & O 1s",
            "binding_energies": {
                "C 1s (sp² C=C / C-C)": 284.6,
                "C 1s (Epoxy / Hydroxyl C-O)": 286.7,
                "C 1s (Carbonyl C=O)": 287.8,
                "C 1s (Carboxylate O-C=O)": 288.9,
                "O 1s (C-O / C=O)": 532.5,
            },
            "ratio_diagnostic": "Area ratio A(C-O + C=O) / A(sp² C-C) measures oxidation degree (~1.2 in pristine GO; drops to <0.3 upon thermal/chemical reduction to rGO).",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "GO (001)", "two_theta": 10.45, "d_A": 8.46, "note": "Hydrated interlayer d-spacing governed by intercalated oxygen groups and water"},
                {"hkl": "rGO (002)", "two_theta": 25.80, "d_A": 3.45, "note": "Restoration of π-π stacked graphitic interlayer lattice"},
                {"hkl": "Graphite (002)", "two_theta": 26.55, "d_A": 3.35, "note": "Pristine unoxidized graphite raw material indicator"},
            ],
            "diagnostic": "Complete shift of reflection from 26.55° (d = 3.35 Å) to 10.45° (d = 8.46 Å) confirms full chemical exfoliation and basal plane oxidation.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 3410.0, "mode": "ν(O-H)", "diagnostic": "Broad intermolecular hydrogen-bonded hydroxyls"},
                {"wavenumber": 1732.0, "mode": "ν(C=O) Carboxyl", "diagnostic": "Carbonyl/carboxyl at sheet edges"},
                {"wavenumber": 1622.0, "mode": "ν(C=C) sp² Core", "diagnostic": "Unoxidized aromatic skeletal graphitic domains"},
                {"wavenumber": 1225.0, "mode": "ν(C-O-C) Epoxy", "diagnostic": "Basal plane epoxide stretch"},
                {"wavenumber": 1050.0, "mode": "ν(C-O) Alkoxy", "diagnostic": "Aliphatic C-O stretching vibration"},
            ],
            "diagnostic": "Disappearance of epoxy (1225 cm⁻¹) and carboxyl (1732 cm⁻¹) bands strictly confirms reduction to rGO for water membrane durability.",
        },
    },

    # --------------------------------------------------------------------------
    # PILLAR 5: 2D MXENES & ADVANCED COMPOSITES
    # --------------------------------------------------------------------------
    "mxene_ti3c2tx_energy": {
        "id": "mxene_ti3c2tx_energy",
        "material_name": "Ti3C2Tx MXene 2D Nanoflakes (HF / LiF-HCl Etched)",
        "pillar": "2D Nanomaterials, MXenes & Functional Composites",
        "institutions": ["KAUST", "KFUPM", "KACST", "IAU"],
        "primary_citation": "KAUST Physical Science / KFUPM Hydrogen / IAU IRMC: 2D titanium carbide MXene electrodes and membranes for capacitive desalination & energy storage.",
        "literature_references": [
            "Alshareef et al. (KAUST AMPM), Adv. Mater. & ACS Nano (Conductive MXene membranes for electromagnetic shielding and supercapacitors).",
            "KFUPM IRC for Renewable Energy: High-rate pseudocapacitive MXene-polymer hybrid electrodes.",
            "IAU IRMC / College of Science (iau.edu.sa): MXene-supported metal nanoparticles for antimicrobial and water pollutant degradation.",
            "KACST Advanced Materials: Scalable synthesis of fluorine-minimized MXene delaminated nanosheets.",
        ],
        "chemical_formula": "Ti3C2Tx (Tx = -O, -OH, -F surface terminations)",
        "keywords": ["mxene", "ti3c2tx", "ti3c2", "2d", "titanium carbide", "delamination", "max phase", "kaust", "kfupm", "iau", "kacst"],
        "xps_benchmarks": {
            "core_level": "Ti 2p, C 1s & F 1s",
            "binding_energies": {
                "Ti 2p3/2 (Ti-C Carbidic)": 454.9,
                "Ti 2p3/2 (Ti-O Surface Tx)": 456.2,
                "Ti 2p3/2 (Ti-F Surface Tx)": 457.5,
                "Ti 2p3/2 (TiO2 Degradation Impurity)": 458.8,
                "C 1s (C-Ti Carbidic)": 281.8,
                "C 1s (Graphitic C-C)": 284.8,
                "F 1s (F-Ti Surface Termination)": 684.9,
            },
            "ratio_diagnostic": "Intense carbidic C-Ti peak at 281.8 eV and carbidic Ti-C at 454.9 eV are unique fingerprints of 2D MXene core. Emergence of TiO2 at 458.8 eV signals ambient oxidation.",
        },
        "xrd_benchmarks": {
            "wavelength_A": 1.54060,
            "reflections": [
                {"hkl": "(002)", "two_theta": 6.85, "d_A": 12.89, "note": "Primary delaminated basal plane reflection (shifts from 9.5° in Ti3AlC2 parent MAX phase)"},
                {"hkl": "(004)", "two_theta": 13.92, "d_A": 6.36, "note": "Second-order harmonic"},
                {"hkl": "(006)", "two_theta": 20.85, "d_A": 4.26, "note": "Third-order basal reflection"},
                {"hkl": "MAX (104)", "two_theta": 39.02, "d_A": 2.31, "note": "Parent Ti3AlC2 MAX phase peak (MUST completely disappear upon full Al etching)"},
            ],
            "diagnostic": "Disappearance of MAX phase (104) at 39.02° and downshift of (002) from 9.5° to 6.85° proves complete Al extraction and delamination.",
        },
        "ftir_benchmarks": {
            "bands": [
                {"wavenumber": 3435.0, "mode": "ν(O-H) Tx Termination", "diagnostic": "Hydroxyl surface terminations and intercalated water"},
                {"wavenumber": 1635.0, "mode": "δ(H-O-H)", "diagnostic": "Intercalated water bending"},
                {"wavenumber": 1080.0, "mode": "ν(C-F / C-O)", "diagnostic": "Surface functional group vibration"},
                {"wavenumber": 620.0, "mode": "ν(Ti-O)", "diagnostic": "Surface oxygen termination lattice mode"},
                {"wavenumber": 530.0, "mode": "ν(Ti-C)", "diagnostic": "Core carbidic layer stretching"},
            ],
            "diagnostic": "Strong Ti-O (620 cm⁻¹) and Ti-C (530 cm⁻¹) envelope with absence of bulk TiO2 indicates pristine terminated flakes.",
        },
    },
}


# ==============================================================================
# 3. ADVANCED SEARCH, FILTERING & CROSS-REFERENCING ENGINE
# ==============================================================================
def search_saudi_databank(
    query: str = "",
    institution: Optional[str] = None,
    technique: Optional[str] = None,
    pillar: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Comprehensive multi-field cross-referencing search engine for Saudi research benchmarks.
    Filters by:
    - query: searches material name, chemical formula, ID, keywords, citations, literature references, and diagnostic terms
    - institution: 'KAUST', 'KFUPM', 'KACST', 'IAU' (or None / 'All')
    - technique: 'XPS', 'XRD', 'FTIR' (or None / 'All')
    - pillar: research pillar name (or None / 'All')
    """
    results = []
    q = (query or "").strip().lower()
    inst_filter = institution.upper().strip() if (institution and "ALL" not in institution.upper()) else None
    
    tech_filter = None
    if technique and "ALL" not in technique.upper():
        if "XPS" in technique.upper():
            tech_filter = "xps"
        elif "XRD" in technique.upper():
            tech_filter = "xrd"
        elif "FTIR" in technique.upper():
            tech_filter = "ftir"

    pillar_filter = pillar.strip() if (pillar and "ALL" not in pillar.upper()) else None

    for b in SAUDI_RESEARCH_BENCHMARKS.values():
        # 1. Institution check
        if inst_filter and inst_filter not in b.get("institutions", []):
            continue

        # 2. Pillar check
        if pillar_filter and b.get("pillar") != pillar_filter:
            continue

        # 3. Technique check
        if tech_filter:
            tech_key = f"{tech_filter}_benchmarks"
            if tech_key not in b:
                continue

        # 4. Text Query matching across all metadata
        if q:
            match_found = False
            # Search in material name, formula, id
            if q in b.get("material_name", "").lower():
                match_found = True
            elif q in b.get("chemical_formula", "").lower():
                match_found = True
            elif q in b.get("id", "").lower():
                match_found = True
            elif q in b.get("primary_citation", "").lower():
                match_found = True
            elif any(q in kw.lower() for kw in b.get("keywords", [])):
                match_found = True
            elif any(q in ref.lower() for ref in b.get("literature_references", [])):
                match_found = True
            
            # Search in XPS core levels & binding energies
            if not match_found and "xps_benchmarks" in b:
                xps_data = b["xps_benchmarks"]
                if q in xps_data.get("core_level", "").lower() or q in xps_data.get("ratio_diagnostic", "").lower():
                    match_found = True
                elif any(q in k.lower() for k in xps_data.get("binding_energies", {}).keys()):
                    match_found = True

            # Search in XRD reflections
            if not match_found and "xrd_benchmarks" in b:
                xrd_data = b["xrd_benchmarks"]
                if q in xrd_data.get("diagnostic", "").lower():
                    match_found = True
                elif any(q in r.get("hkl", "").lower() or q in r.get("note", "").lower() for r in xrd_data.get("reflections", [])):
                    match_found = True

            # Search in FTIR bands
            if not match_found and "ftir_benchmarks" in b:
                ftir_data = b["ftir_benchmarks"]
                if q in ftir_data.get("diagnostic", "").lower():
                    match_found = True
                elif any(q in band.get("mode", "").lower() or q in band.get("diagnostic", "").lower() for band in ftir_data.get("bands", [])):
                    match_found = True

            if not match_found:
                continue

        results.append(b)

    return results


def list_benchmarks_for_institution(inst_code: str) -> List[Dict[str, Any]]:
    """Returns all benchmarks associated with a specific Saudi institution."""
    code = inst_code.upper().strip()
    return [b for b in SAUDI_RESEARCH_BENCHMARKS.values() if code in b["institutions"]]


def list_benchmarks_for_pillar(pillar_name: str) -> List[Dict[str, Any]]:
    """Returns all benchmarks in a specific research pillar."""
    if not pillar_name or "All" in pillar_name:
        return list(SAUDI_RESEARCH_BENCHMARKS.values())
    return [b for b in SAUDI_RESEARCH_BENCHMARKS.values() if b["pillar"] == pillar_name]


def get_benchmark_by_id(benchmark_id: str) -> Optional[Dict[str, Any]]:
    """Fetches benchmark metadata by unique ID."""
    return SAUDI_RESEARCH_BENCHMARKS.get(benchmark_id)


def audit_spectral_match(
    technique: str,
    experimental_peaks: List[float],
    benchmark_id: str,
    tolerance: float = 0.5,
) -> Dict[str, Any]:
    """
    Compares experimental peak positions against the curated institutional benchmark.
    technique: 'XPS' (eV), 'XRD' (degrees 2-theta), 'FTIR' (cm-1).
    tolerance: acceptable deviation threshold.
    """
    bm = get_benchmark_by_id(benchmark_id)
    if not bm:
        return {"matched": False, "reason": "Benchmark ID not found"}

    tech_key = f"{technique.lower()}_benchmarks"
    if tech_key not in bm:
        return {"matched": False, "reason": f"No {technique} reference in benchmark"}

    b_data = bm[tech_key]
    matches = []
    unmatched_ref = []

    if technique.upper() == "XPS":
        ref_peaks = b_data.get("binding_energies", {})
        for label, ref_be in ref_peaks.items():
            found = False
            for exp_p in experimental_peaks:
                diff = abs(exp_p - ref_be)
                if diff <= tolerance:
                    matches.append({
                        "label": label,
                        "ref_val": ref_be,
                        "exp_val": exp_p,
                        "diff": round(diff, 3),
                        "status": "Verified",
                    })
                    found = True
                    break
            if not found:
                unmatched_ref.append({"label": label, "ref_val": ref_be})

    elif technique.upper() == "XRD":
        ref_list = b_data.get("reflections", [])
        for r in ref_list:
            ref_tt = float(r["two_theta"])
            found = False
            for exp_p in experimental_peaks:
                diff = abs(exp_p - ref_tt)
                if diff <= tolerance:
                    matches.append({
                        "label": f"{r['hkl']} ({r.get('note', '')})",
                        "ref_val": ref_tt,
                        "exp_val": exp_p,
                        "diff": round(diff, 3),
                        "status": "Verified",
                    })
                    found = True
                    break
            if not found:
                unmatched_ref.append({"label": r["hkl"], "ref_val": ref_tt})

    elif technique.upper() == "FTIR":
        ref_list = b_data.get("bands", [])
        for b in ref_list:
            ref_wn = float(b["wavenumber"])
            found = False
            for exp_p in experimental_peaks:
                diff = abs(exp_p - ref_wn)
                if diff <= tolerance:
                    matches.append({
                        "label": f"{b['mode']} ({b.get('diagnostic', '')})",
                        "ref_val": ref_wn,
                        "exp_val": exp_p,
                        "diff": round(diff, 1),
                        "status": "Verified",
                    })
                    found = True
                    break
            if not found:
                unmatched_ref.append({"label": b["mode"], "ref_val": ref_wn})

    total_ref = len(matches) + len(unmatched_ref)
    match_pct = (100.0 * len(matches) / total_ref) if total_ref > 0 else 0.0

    return {
        "matched": match_pct >= 50.0,
        "match_percentage": round(match_pct, 1),
        "matches": matches,
        "unmatched": unmatched_ref,
        "benchmark_name": bm["material_name"],
        "institutions": bm["institutions"],
        "citation": bm["primary_citation"],
        "references": bm["literature_references"],
    }
