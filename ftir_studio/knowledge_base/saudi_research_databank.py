"""
saudi_research_databank.py - Comprehensive Institutional Materials & Spectroscopy Knowledge Bank
Curated for: KFUPM, KACST, KAUST, and Imam Abdulrahman Bin Faisal University (IAU - iau.edu.sa).
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

from typing import Any, Dict, List, Optional

# ==============================================================================
# 1. INSTITUTIONAL CENTERS & RESEARCH PILLARS
# ==============================================================================
SAUDI_INSTITUTIONS = {
    "KAUST": {
        "name": "King Abdullah University of Science and Technology",
        "location": "Thuwal, Saudi Arabia",
        "badge": "KAUST",
        "flagship_centers": [
            "Advanced Membranes and Porous Materials Center (AMPM)",
            "KAUST Solar Center (KSC)",
            "KAUST Catalysis Center (KCC)",
            "Water Desalination and Reuse Center (WDRC)",
        ],
        "primary_focus": "Reticular chemistry (MOFs/COFs), ultra-high efficiency tandem perovskite PV, CO₂ capture & conversion, and selective separation membranes.",
    },
    "KFUPM": {
        "name": "King Fahd University of Petroleum and Minerals",
        "location": "Dhahran, Eastern Province, Saudi Arabia",
        "badge": "KFUPM",
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
    "Advanced Catalysis, CO₂ Conversion & Metal Oxides",
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
            "IAU IRMC / College of Science: Adsorptive removal of organic pollutants using porous Zr-MOF composites.",
        ],
        "chemical_formula": "Zr6O4(OH)4(BDC)6-x (x = linker defect missingness)",
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
                {"wavenumber": 421.0, "mode": "ν(Zn-N)", "diagnostic": "Direct tetrahedral Zn-N coordination bond"},
            ],
            "diagnostic": "Disappearance of free imidazole N-H band (3400-3200 cm⁻¹) confirms 100% deprotonation into Zn(2-MeIM)2.",
        },
    },

    # --------------------------------------------------------------------------
    # PILLAR 2: PEROVSKITE PHOTOVOLTAICS & SOLAR
    # --------------------------------------------------------------------------
    "perovskite_fapbi3_solar": {
        "id": "perovskite_fapbi3_solar",
        "material_name": "FAPbI3 / MAPbI3 Halide Perovskite (Desert-Resilient)",
        "pillar": "Perovskite Photovoltaics & Desert-Resilient Solar Absorbers",
        "institutions": ["KAUST", "KFUPM", "KACST"],
        "primary_citation": "KAUST Solar Center (KSC) / KFUPM Renewable Energy: Defect-passivated halide perovskites with >33% tandem efficiency and desert heat/UV tolerance.",
        "literature_references": [
            "De Wolf, Bakr, Laquai et al. (KAUST Solar Center), Science & Nature Energy (Perovskite/Si tandems).",
            "KFUPM IRC for Renewable Energy: High-temperature stability of multi-cation perovskites in extreme desert climates.",
            "KACST Solar Energy: Industrial encapsulation and outdoor aging of halide perovskite PV modules.",
        ],
        "chemical_formula": "FA0.85MA0.10Cs0.05Pb(I0.85Br0.15)3",
        "xps_benchmarks": {
            "core_level": "Pb 4f & I 3d",
            "binding_energies": {
                "Pb 4f7/2 (Perovskite Pb²⁺)": 138.4,
                "Pb 4f5/2 (Perovskite Pb²⁺)": 143.3,
                "Pb 4f7/2 (Metallic Pb⁰ Defect)": 136.6,
                "Pb 4f5/2 (Metallic Pb⁰ Defect)": 141.5,
                "I 3d5/2 (Halide I⁻)": 619.3,
                "I 3d3/2 (Halide I⁻)": 630.8,
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

    # --------------------------------------------------------------------------
    # PILLAR 3: CATALYSIS, CO2 CONVERSION & METAL OXIDES
    # --------------------------------------------------------------------------
    "tio2_catalyst_photocatalysis": {
        "id": "tio2_catalyst_photocatalysis",
        "material_name": "TiO2 Anatase-Rutile Nanocatalysts (P25 / Calcined)",
        "pillar": "Advanced Catalysis, CO₂ Conversion & Metal Oxides",
        "institutions": ["KAUST", "KFUPM", "KACST", "IAU"],
        "primary_citation": "KAUST Catalysis / IAU IRMC / KFUPM CREPP: Phase junction engineering in Anatase/Rutile TiO2 for solar water splitting & water decontamination.",
        "literature_references": [
            "Gascon, Takanabe et al. (KAUST Catalysis Center), ACS Catalysis (Solar fuel and water splitting).",
            "KFUPM CREPP & Chemistry: Thermal phase evolution of titanium dioxide for photocatalytic desulfurization.",
            "IAU IRMC / College of Science (iau.edu.sa), Arabian J. Chem.: Silver and carbon-modified TiO2 nanocomposites for visible-light water decontamination.",
            "KACST Advanced Materials: Large-scale photocatalytic purification of industrial wastewater.",
        ],
        "chemical_formula": "TiO2 (Mixed Anatase + Rutile)",
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
            "IAU College of Engineering / IRMC: Heavy metal adsorption and dye separation on functionalized PAN nanofibers.",
            "KACST Advanced Materials: High-toughness carbonized electrospun electrodes for electrochemical desalination (CDI).",
        ],
        "chemical_formula": "(C3H3N)n -> Turbostratic Carbon (C)",
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
}


# ==============================================================================
# 3. HELPER FUNCTIONS FOR DISCOVERY, VERIFICATION & AUDIT
# ==============================================================================
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
