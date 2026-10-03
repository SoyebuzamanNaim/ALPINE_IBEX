# NASA Combustion Dataset Audit & Discovery Report (Phase 02)

> **Document Status:** Complete and verified against NASA Physical Sciences Informatics (PSI) and
> NASA Technical Reports Server (NTRS) APIs.

## 1. Executive Summary

This audit evaluated **23 priority microgravity combustion investigations** from the NASA Physical Sciences
Informatics (PSI) system and the NASA Technical Reports Server (NTRS).

### Key Scientific Decision
A major trap in applied AI projects is merging physically incompatible combustion experiments into an unscientific
"universal fire score." Our audit establishes a strict, scientifically defensible boundary:
1. **Core Modeling Shortlist (Solid Fuel Flame Spread & Extinction):**
   - **BASS (PSI-26)** and **BASS-II (PSI-25)**: The most rigorous, dense dataset of solid fuel combustion (PMMA rods,
     PMMA sheets, cotton/fiberglass fabric, Delrin) under systematically controlled oxygen concentrations (15–21%),
     pressures (~101 kPa), and ventilation flow velocities (0–55 cm/s) aboard the ISS Microgravity Science Glovebox.
   - **SAFFIRE (PSI-98, PSI-99, PSI-100)**: Autonomous, large-scale spacecraft fire experiments providing validation
     for thick PMMA slabs and SIBAL composite fabrics under varying oxygen and exploration atmospheric pressures.
   - **DARTFire / SIBAL Sounding Rocket & Drop Tower Experiments (NTRS 19960008415, 20080034883)**: Opposed and concurrent
     flow flame-spread limits over thin cellulosic fuels and PMMA sheets.
2. **Catalogued but Excluded from Core Flame-Spread Model:**
   - **Droplet Combustion (FLEX, FLEX-2, PSI-69/68)**: Involves liquid droplet diameter, d^2 vaporization rate, and
     gas-phase inert dilution. These physics are fundamentally incompatible with solid surface flame spread.
   - **Gaseous Diffusion Flames (SPICE, SLICE, ACME BRE/s-Flame/E-Field, PSI-107/106/20/22/23)**: Involve fuel mass flow
     rates, burner nozzles, and co-flow velocities.
   - **Smoke Detectors & Aerosols (SAME, SAME-R, DAFT, PSI-102/101/47)**: Measure particle size distributions and sensor
     obscuration, not flammability limits.

---

## 2. Shortlist Assessment

| Investigation | PSI ID | Exact NASA Title | Usable for Model? | Rationale |
|---|---|---|---|---|
| **BASS** | PSI-26 | Burning and Suppression of Solids | **YES** | Primary ISS experiment for solid fuel flame spread |
| **BASS-II** | PSI-25 | Burning and Suppression of Solids - II | **YES** | Adds N2 dilution (variable O2: 15–21%), flow velocities |
| **SAFFIRE-I** | PSI-98 | Spacecraft Fire Safety Experiment-I | **YES** | Large-scale solid flame spread validation |
| **SAFFIRE-II** | PSI-99 | Spacecraft Fire Experiment-II | **YES** | Material flammability in low-g |
| **SAFFIRE-III**| PSI-100 | Spacecraft Fire Experiment-III | **YES** | High-velocity spacecraft fire spread |
| **FLEX / FLEX-2** | PSI-69 / 68 | Flame Extinguishment Experiment (-2) | **NO** | Droplet physics (not solid fuel flame spread) |
| **SPICE** | PSI-107 | Smoke Point In Co-flow Experiment | **NO** | Gaseous co-flow smoke point (not solid fuel) |
| **SAME / SAME-R** | PSI-102 / 101 | Smoke Aerosol Measurement Experiment | **NO** | Sensor aerosol physics only |
| **SLICE** | PSI-106 | Structure and Liftoff In Combustion Experiment | **NO** | Gas burner flame liftoff |
| **ACME (BRE, s-Flame, E-Field)** | PSI-20, 23, 22 | Advanced Combustion via Microgravity Experiments | **NO** | Gaseous diffusion flames |

---

## 3. Detailed Investigation Audit

### ACME Flame Design (PSI-10)
- **Exact NASA Title:** Advanced Combustion via Microgravity Experiments / Flame Design
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-10](https://psi.nasa.gov/physci/repo/data/investigations/PSI-10)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Flames of Gaseous Fuels)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** The primary objectives of this flight experiment are: A. Obtain soot-inception limits of quasi-steady normal and inverse spherical diffusion flames as functions of flow rate, Zst, amount of inert (N2 or CO2), and pressure for C2H4 and CH4 flames. Identify the corresponding temperatures in hot regions. Obtain similar limits and temperatures for inverse and normal coflow flames. B. Obtain detailed measurements in quasi-steady normal and inverse spherical diffusion flames for C2H4 and CH4. Determine the effects of flow rate, Zst, amount of N2, and pressure on flame temperature, size, color, and soot volume fraction. Evaluate the possible existence of steady flames. C. Obtain extinction limits as functions of Zst, amount of N2, and pressure for normal and inverse spherical C2H4 and CH4 flames. Identify the corresponding temperatures in hot regions. Identify the presence of radiative or kinetic extinction. Evaluate whether pseudo-flammability limits can be obtained for these flames.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Soot extinction limits in spherical gas flames; excluded
### SAFFIRE-III (PSI-100)
- **Exact NASA Title:** Spacecraft Fire Experiment-III
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-100](https://psi.nasa.gov/physci/repo/data/investigations/PSI-100)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **YES**
- **Modeling Role:** Large-scale spacecraft environment benchmark and low-pressure validation
- **Key Variables:** oxygen_pct (18-24%), pressure_kpa (50-100 kPa), flow_cm_s (10-30 cm/s), sample_width_cm (5-40 cm), flame_growth_rate_cm_s
- **Sensory & Diagnostics:** Thermocouple arrays, pressure transducers, O2/CO2 sensors, radiometers; Calibrated digital cameras, video arrays, optical radiometry
- **Scientific Objective:** The objectives of this investigation were to: (1) determine how rapidly a large scale fire grows in low-gravity and (2) investigate the low-g flammability limits compared to those obtained in NASA’s normal gravity material flammability screening test.
- **Primary Citations:** NTRS 20200000557, NTRS 20180005168, NTRS 20240007488
- **Audit Findings:** Reference/Validation: High flow velocity spacecraft fire safety
### SAME-R (PSI-101)
- **Exact NASA Title:** Smoke Aerosol Measurement Experiment-Reflight
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-101](https://psi.nasa.gov/physci/repo/data/investigations/PSI-101)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (smoke sensor characterization)
- **Key Variables:** particle_count_concentration, mean_diameter_um, obscuration_pct
- **Sensory & Diagnostics:** Condensation particle counter, ionization detector, photoelectric detector; None or test cell monitoring
- **Scientific Objective:** Similar to the original SAME investigation, the primary objective of the SAME-R investigation was to quantify the sizes that the liquid smoke particulate achieves in low gravity and to relate the droplet size distribution to the smoke generation and smoke transport conditions in the experiment. One of the problems encountered during the SAME investigation was that after the thermal precipitators were returned to the ground, it was found that all the TEM grids were severely contaminated with some unidentified foreign particles, making these grids unusable although some of them showed shapes of certain types of smoke particles. Based on that experience the SAME-R investigation employed several modification covering new materials, extended operating conditions, and diagnostic equipments.
- **Primary Citations:** NASA PSI-102, NASA PSI-101
- **Audit Findings:** Smoke detection & aerosol sizing, reflight experiment
### SAME (PSI-102)
- **Exact NASA Title:** Smoke and Aerosol Measurement Experiment
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-102](https://psi.nasa.gov/physci/repo/data/investigations/PSI-102)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (smoke sensor characterization)
- **Key Variables:** particle_count_concentration, mean_diameter_um, obscuration_pct
- **Sensory & Diagnostics:** Condensation particle counter, ionization detector, photoelectric detector; None or test cell monitoring
- **Scientific Objective:** One of the major goals of this investigation was to quantify the sizes that the liquid smoke particulate achieves in low gravity and to relate the droplet size distribution to the smoke generation and smoke transport conditions in the experiment. A numerical code was to be developed to predict the smoke droplet growth as a function of the fuel pyrolysis rate, the thermodynamic properties of the pyrolysis vapor, and the flow environment.
- **Primary Citations:** NASA PSI-102, NASA PSI-101
- **Audit Findings:** Smoke detection & aerosol sizing, no flame-spread regime labels
### SLICE (PSI-106)
- **Exact NASA Title:** Structure and Liftoff In Combustion Experiment
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-106](https://psi.nasa.gov/physci/repo/data/investigations/PSI-106)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science ()
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** Objective: The objective of this investigation is to better understand the structure and stability of laminar diffusion flames in microgravity.  Specific objectives of this investigation were: 1. To investigate the structure of laminar diffusion flames in microgravity to understand the stabilizing mechanisms at the flames base. 2. Determine the liftoff velocity limits for different fuels and burner diameters. 3. Evaluate the impact of fuel dilution with nitrogen on soot formation and flame stability. 4. Quantify the effects of microgravity on flame length and radiative heat loss compared to normal gravity conditions. 5. Validate numerical models for flame dynamics, soot production, and thermal radiation in non-premixed flames.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Structure and liftoff in gaseous diffusion flames; incompatible with solid fuel
### SPICE (PSI-107)
- **Exact NASA Title:** Smoke Point In Co-flow Experiment
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-107](https://psi.nasa.gov/physci/repo/data/investigations/PSI-107)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Fire Safety)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** The objective of SPICE is to better understand the complex process of combustion by observing flames in a microgravity environment aboard the International Space Station (ISS) and analogous ground experiments.  Specific objectives were: (1) Identify the laminar smoke-point properties of non-buoyant jet diffusion flames under various co-flow conditions in microgravity. (2) Determine the effects of burner diameter and co-flow velocity on the luminous flame lengths and smoke points. (3) Quantify the sooting propensity of different fuels, such as ethylene, propane, and propylene mixtures. (4) Validate the correlation between luminous flame shape and residence time under microgravity conditions. (5) Investigate the impact of air and fuel flow rate variations on smoke point phenomena in space.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Gas co-flow laminar smoke point; gaseous fuel, incompatible with solid fuel
### SAME Simulation (PSI-115)
- **Exact NASA Title:** Utilization of the Smoke Aerosol Measurement Experiment Data for Advanced Modeling and Simulation of Smoke Generation in Micro-Gravity
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-115](https://psi.nasa.gov/physci/repo/data/investigations/PSI-115)
- **Flight Platform:** Not Applicable
- **Research Area:** Combustion Science (Smoke Aerosol, Combustion Simulation)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (smoke sensor characterization)
- **Key Variables:** particle_count_concentration, mean_diameter_um, obscuration_pct
- **Sensory & Diagnostics:** Condensation particle counter, ionization detector, photoelectric detector; None or test cell monitoring
- **Scientific Objective:** The objective of this investigation was to use numerical simulation to explore the influence of gravity on pyrolysis smoke growth from a fundamental perspective. The intention of this effort is to quantify the differences between microgravity and Earth gravity smoke, and to identify the fluid dynamic mechanisms that cause the differences.
- **Primary Citations:** NASA PSI-102, NASA PSI-101
- **Audit Findings:** Smoke generation modeling from SAME data
### Cool Flame Transitions (PSI-142)
- **Exact NASA Title:** Quantitative Studies of Cool Flame Transitions at Radiation / Stretch Extinction Using Counterflow Flames
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-142](https://psi.nasa.gov/physci/repo/data/investigations/PSI-142)
- **Flight Platform:** Not Applicable
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Contextual reference only
- **Key Variables:** temperature, flow_velocity, concentration
- **Sensory & Diagnostics:** Chamber sensors; Video/still photography
- **Scientific Objective:** By using the Flame Extinguishment (FLEX) experimental data from the Physical Sciences Informatics (PSI) system of combustion science, the purpose of this grant was to conduct new simulations and ground-based experiments using ozone-sensitized counterflow flames to:     1) Develop a new diagram of the flammability limits of diffusional cool flames affected by radiation, diffusion, and convection.     2) Bridge the knowledge gap between the flammability limits and extinction limits of hot flames and cool flames.     3) Verify the phenomena observed on the ISS flame extinguishment experiments.     4) Obtain new, quantitative data of extinction limit, flame temperature, and species distribution for the validation of kinetic and radiation models involving cool flames.     5) Extend the cool flame experiments from the original ISS droplet experiments to a more general ground-based combustion system involving radiation, diffusion, convection, and low-temperature chemistry while maintaining a one-dimensional geometry.
- **Primary Citations:** NASA PSI-142
- **Audit Findings:** Counterflow gaseous flames at radiation/stretch extinction
### ACME CFI-G (PSI-159)
- **Exact NASA Title:** Advanced Combustion via Microgravity Experiments / Cool Flames Investigation with Gases
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-159](https://psi.nasa.gov/physci/repo/data/investigations/PSI-159)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Flames of Gaseous Fuels)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** 1. Plan and support flight testing on the International Space Station (ISS). 2. Determine the conditions for which cool diffusion flames occur for propane, n-butane, and n-pentane; normal and inverse flames; and a broad range of Zst, Tad, and fluent flow rate. 3. Support the flight tests with advanced CFD simulations. 4. Identify or develop a chemical kinetics mechanism that yields good agreement between the CFD predictions and the ISS measurements. 5. Disseminate the results as widely as possible.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Cool flames with gaseous fuels; excluded
### ACME BRE (PSI-20)
- **Exact NASA Title:** Advanced Combustion via Microgravity Experiments - Burning Rate Emulator
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-20](https://psi.nasa.gov/physci/repo/data/investigations/PSI-20)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Flames of Gaseous Fuels)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** The BRE flight program seeks to establish the burning conditions in a quiescent microgravity ambient in terms of material properties. The specific flight objectives are as follows.   1. Observe burning behavior in long-duration microgravity for CH4/N2 and C2H4/N2mixtures on porous circular burners of 25  and 50 mm diameter. Consider O2/N2 ambients with various pressures and ambient O2 concentrations and pressures. NASA - considered atmosphere for human space missions will be examined: 14.7 psia, 21 % oxygen: 10.2 psia, 26.5 %; and 8.2 psia, 34 % oxygen. Emphasize fuel conditions that can be related to a diverse range of condensed fuels.   2. Consider the conditions of Objective 1 for ambients of O2/CO2 (desired).   3. Consider the conditions of Objectives 1 – 2 for extinction limits.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Burning Rate Emulator (gaseous burner emulating solids); gas-phase
### ACME CLD Flame (PSI-21)
- **Exact NASA Title:** Advanced Combustion via Microgravity Experiments / Coflow Laminar Diffusion Flame
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-21](https://psi.nasa.gov/physci/repo/data/investigations/PSI-21)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Flames of gaseous fuel)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** In order to provide the experimental data needed to allow rigorous testing of computational models at the extremes of the fuel dilution spectrum, we have the following objectives: A) Characterize the behavior of weak coflow diffusion flames of methane and ethylene, as a function of velocity and fuel dilution, through measurement of flame shape, lift-off heights, temperatures and extinction limits. B) Characterize the sooting tendencies of diffusion flames with long residence times, as a function of velocity and fuel dilution, through measurement of flame shape, gas temperatures in the soot-free portion of the flame, soot luminosity, soot temperatures, and soot volume fractions.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Coflow laminar diffusion flames with gaseous fuel; excluded
### ACME E-FIELD Flames (PSI-22)
- **Exact NASA Title:** Advanced Combustion via Microgravity Experiments Electric-Field Effects on Laminar Diffusion Flames
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-22](https://psi.nasa.gov/physci/repo/data/investigations/PSI-22)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Laminar Flames)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** The objective of this investigation is to better understand the relationship between electric field voltage and chemi-ion current, analyze the dynamic response of flames to electric field changes, evaluate soot formation, and characterize stabilized near-limit lifted flames.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Electric field effects on laminar diffusion flames; excluded
### ACME s-Flame (PSI-23)
- **Exact NASA Title:** Advanced Combustion via Microgravity Experiments-Structure and Response of Spherical Diffusion Flames
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-23](https://psi.nasa.gov/physci/repo/data/investigations/PSI-23)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Flames of gaseous fuels)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** A series of experiments is proposed with the following specific objectives, in both soot-free and sooty flames, to compare with detailed computational simulation to assess transport properties and detailed chemical kinetics (including chemiluminescence):     Objective A. Measure and characterize the transient structure (such as temperature and species distribution) of diffusion flames established at initially non-steady, spherical flame structures for mixtures of different H2/CH4/diluent ratios   (soot-free) and different C2H4/diluent ratios (sooty), for different flow rates.     Objective B. Determine the quasi-steady convective/chemical-kinetic extinction limits (low system Damköhler numbers) and radiative/chemical-kinetic extinction limits (high system Damköhler numbers) for mixtures of different H2/CH4/diluent ratios (soot-free) and different C2H4/diluent ratios (sooty).     Objective C. Determine the existence (for different Zeldovich number, Ze), onset (as a function Da), and nature (i.e. mode, frequency, amplitude) of pulsating instabilities theoretically predicted to occur in transient spherical diffusion flames using fuel/diluent mixtures that are above a critical Lewis number.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Spherical diffusion flames with gaseous fuels; excluded
### BASS-II (PSI-25)
- **Exact NASA Title:** Burning and Suppression of Solids - II
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **YES**
- **Modeling Role:** Primary training and validation dataset for solid-fuel flame spread and extinction
- **Key Variables:** oxygen_pct (15-21%), pressure_kpa (98-102 kPa), flow_cm_s (0-55 cm/s), fuel_thickness_mm (1-10 mm), burn_rate_mm_s, extinction_time_s
- **Sensory & Diagnostics:** CSA-CP (O2, CO), CDM (CO2), fan anemometers, radiometers; High-resolution video with data overlay, 35-mm still camera, broadband two-color pyrometry
- **Scientific Objective:** BASS-II results contribute to the combustion computational models used in the design of fire detection and suppression systems in microgravity and on Earth. Objectives Include:   1) Study the ignition, flame growth, flame spread, and extinction limits for solid fuels burning in low-velocity forced flows in microgravity.   2) Begin to bridge the gap between the normal gravity NASA-STD-6001 Test #1 method, ground-based microgravity tests, and actual material flammability in microgravity.   3) Provide SoFIE PIs with preliminary data to refine Science Requirements.   4)  Practical, realistic (thicker) fuels in typical geometries will be examined, including slabs, cylinders, and spherical sections.  The primary variables include:      • Forced flow velocity (speed and direction)      • Ambient oxygen concentration (via working volume nitrogen vitiation)      • Sample geometry (rods, spherical section, slabs, films, and fabric sheets
- **Primary Citations:** NTRS 20210011385, NTRS 20160000593, NTRS 20140011099, NTRS 20150008961
- **Audit Findings:** Primary: Solid fuel flammability, variable O2, pressure, and forced flow
### BASS (PSI-26)
- **Exact NASA Title:** Burning and Suppression of Solids
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-26](https://psi.nasa.gov/physci/repo/data/investigations/PSI-26)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **YES**
- **Modeling Role:** Primary training and validation dataset for solid-fuel flame spread and extinction
- **Key Variables:** oxygen_pct (15-21%), pressure_kpa (98-102 kPa), flow_cm_s (0-55 cm/s), fuel_thickness_mm (1-10 mm), burn_rate_mm_s, extinction_time_s
- **Sensory & Diagnostics:** CSA-CP (O2, CO), CDM (CO2), fan anemometers, radiometers; High-resolution video with data overlay, 35-mm still camera, broadband two-color pyrometry
- **Scientific Objective:** The two main objectives for BASS are to:     1.) Begin to bridge the gap between the normal gravity NASA-STD-6001 Test#1 method, ground-based microgravity tests, and actual material flammability in microgravity. The relation between these can be investigated by observing flames burning for the longer times available in flight. Practical, realistic (thicker) fuels in typical geometries will be examined, including wake flames which have characteristics of a fire burning behind another object (for example, a fire burning in tight area which may not be easily accessible).     2.) Assess the effectiveness of an inert, gaseous extinguishing agent (similar to that used on ISS) in putting out flames over different materials, geometries, preheating, and flow.
- **Primary Citations:** NTRS 20210011385, NTRS 20160000593, NTRS 20140011099, NTRS 20150008961
- **Audit Findings:** Primary: Solid fuel flame spread/extinction in microgravity flow duct
### CFI (PSI-39)
- **Exact NASA Title:** Cool Flames Investigation
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-39](https://psi.nasa.gov/physci/repo/data/investigations/PSI-39)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Droplets)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Contextual reference only
- **Key Variables:** temperature, flow_velocity, concentration
- **Sensory & Diagnostics:** Chamber sensors; Video/still photography
- **Scientific Objective:** The objectives of this investigation are to:     1) Examine the combustion behavior of n-dodecane and mixtures of n-dodecane/iso-dodecane at pressures ranging from 0.25 atm to 5 atm.     2) Analyze the effects of helium dilution on cool flame behavior.     3) Examine the behavior of combustion characteristics.     4) Investigate the relationship between droplet size, pressure, and flame extinction, and (5) understand the consequence of soot formation during cool flame combustion.
- **Primary Citations:** NASA PSI-39
- **Audit Findings:** Cool flames with droplet fuels; excluded
### DAFT / DAFT-2 (PSI-47)
- **Exact NASA Title:** Dust and Aerosol Measurement Feasibility Test / Dust and Aerosol Measurement Feasibility Test-2
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-47](https://psi.nasa.gov/physci/repo/data/investigations/PSI-47)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (smoke sensor characterization)
- **Key Variables:** particle_count_concentration, mean_diameter_um, obscuration_pct
- **Sensory & Diagnostics:** Condensation particle counter, ionization detector, photoelectric detector; None or test cell monitoring
- **Scientific Objective:** The focus of DAFT / DAFT-2 was to mitigate the risk for the Smoke Aerosol Measurement Experiment (SAME). SAME relied on a commercially available condensate nuclei counter, the TSI P-Trak,  to quantify smoke aerosols in a microgravity environment, however there were concerns that th P-Trak would not be reliable in microgravity as it relies on gravity to recycle isopropyl alcohol used in the measurement process. DAFT / DAFT-2 tests that a modified P-Trak particulate counter would be accurate in microgravity.  Summarized objectives include:     1) Demonstrate the Functionality of the Modified TSI P-Trak in Microgravity     2) Compare the TSI P-Trak Performance against the DustTrak control     3) Create and Analyze Aerosol Standards in Microgravity     4) Ensure the reliability of future aerosol experiments
- **Primary Citations:** NASA PSI-102, NASA PSI-101
- **Audit Findings:** Dust and aerosol measurement feasibility; sensor test
### SPICE Analysis (PSI-60)
- **Exact NASA Title:** Computational and Experimental Analysis of SPICE Data Sets
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-60](https://psi.nasa.gov/physci/repo/data/investigations/PSI-60)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Gaseous)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (gaseous burner incompatible with solid flame spread)
- **Key Variables:** fuel_flow_rate_sccm, coflow_velocity_cm_s, burner_diameter_mm, smoke_point_height_mm
- **Sensory & Diagnostics:** Mass flow controllers, thermocouple rakes, gas chromatography; Color video, chemiluminescence, soot incandescence
- **Scientific Objective:** This ground investigation  sought to increase understanding of the issues that control the large discrepancy between soot formation in 1g and in 0g flames.  The objective of this investigation was to integrate computational and experimental methods to derive temperature distributions and soot volume fractions from the Smoke Point in Coflow Experiment (SPICE) data available in PSI. By analyzing over 1600 raw DSLR images and incorporating advanced soot models, the study sought to improve understanding of soot formation, oxidation, radiative re-absorption, and aggregate growth in heavily sooting flames. The work further aimed to reconcile microgravity and normal gravity flame behavior, identify key physical and chemical processes influencing smoke point development, and provide a framework for evaluating model parameter sensitivity.
- **Primary Citations:** NTRS 20150008962, NASA PSI-107, NASA PSI-20
- **Audit Findings:** Computational and experimental analysis of SPICE data
### BASS Modeling (PSI-62)
- **Exact NASA Title:** Concurrent Flame Spread Modeling using Flamelet Generated Manifolds in Microgravity with Comparison to BASS Experiments using Two-Color Tomography
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-62](https://psi.nasa.gov/physci/repo/data/investigations/PSI-62)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **YES**
- **Modeling Role:** Primary training and validation dataset for solid-fuel flame spread and extinction
- **Key Variables:** oxygen_pct (15-21%), pressure_kpa (98-102 kPa), flow_cm_s (0-55 cm/s), fuel_thickness_mm (1-10 mm), burn_rate_mm_s, extinction_time_s
- **Sensory & Diagnostics:** CSA-CP (O2, CO), CDM (CO2), fan anemometers, radiometers; High-resolution video with data overlay, 35-mm still camera, broadband two-color pyrometry
- **Scientific Objective:** The objective of this research was to develop and validate new flamelet generated manifold (FGM) modeling techniques for concurrent flame spread in microgravity. Concurrent flame spread presented one of the greatest modeling challenges in combustion science due to the intricate coupling between heat transfer, mass transport, and chemical kinetics near the solid-vapor interface. Traditional modeling strategies often relied on hybridized turbulence and chemistry models that were not fully consistent and failed to capture important intermediate reaction pathways. To overcome these shortcomings, this PSI grant advanced the use of an unsteady flamelet generated manifold (UFGM) framework that reduced the complexity of reacting systems by mapping them into lower-dimensional manifolds. The research aimed to leverage this methodology to simulate solid fuel combustion processes with high fidelity, using the NASA Burning and Suppression of Solids (BASS and BASS-II) experiments as benchmarks. Ultimately, the long-term goal was to enable accurate prediction of flammability limits for spacecraft materials and to provide a tool that could also serve as a subgrid-scale model in large-eddy simulations of fires, supporting spacecraft safety and hazard mitigation.
- **Primary Citations:** NTRS 20210011385, NTRS 20160000593, NTRS 20140011099, NTRS 20150008961
- **Audit Findings:** Two-color pyrometry & numerical modeling of BASS PMMA flame spread
### FLEX-2 (PSI-68)
- **Exact NASA Title:** Flame Extinguishment Experiment - 2
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-68](https://psi.nasa.gov/physci/repo/data/investigations/PSI-68)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (droplet physics incompatible with solid fuel)
- **Key Variables:** droplet_diameter_mm, burn_rate_k, extinction_diameter_mm, ambient_O2, ambient_inert
- **Sensory & Diagnostics:** Radiometers, chamber pressure/temperature; High-speed back-lit imaging, color video
- **Scientific Objective:** The primary goal of the FLEX-2 flight experiments is to extend the results of FLEX-1 to fuels and environmental conditions that mimic real combustor conditions, as well as, provide benchmark experimental data on bi-component droplet combustion over a wide range of initial conditions in order to validate numerical simulations and to develop new theoretical models.  Detailed experimental objectives can be further itemized as:   1. Investigate the role of liquid-phase mixing on the burning characteristics of bi-component fuel droplets.   2. Examine the steady and unsteady liquid and gas-phase phenomena in pure fuel combustion.   3. Study flame extinction mechanisms and their boundaries.   4. Analyze the soot formation process, including soot volume fraction soot-shell dynamics.   5. Determine the influence of droplet interactions on the flammability limits and extinction behavior of droplet arrays.   6. Validate theoretical models of droplet combustion through comprehensive experimental data collection in microgravity environments.
- **Primary Citations:** NTRS 20140004923, NASA PSI-69
- **Audit Findings:** Droplet combustion, not solid flame spread; excluded from core model
### FLEX (PSI-69)
- **Exact NASA Title:** Flame Extinguishment Experiment
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire Safety)
- **Usable for Prototype Modeling:** **NO**
- **Modeling Role:** Excluded from core solid-fuel model (droplet physics incompatible with solid fuel)
- **Key Variables:** droplet_diameter_mm, burn_rate_k, extinction_diameter_mm, ambient_O2, ambient_inert
- **Sensory & Diagnostics:** Radiometers, chamber pressure/temperature; High-speed back-lit imaging, color video
- **Scientific Objective:** The FLEX (Flame Extinguishment Experiment) investigation aims to map the flammability limits of liquid fuels in microgravity environments, measure the effectiveness of various gaseous fire suppressants such as CO2, He, and SF6, and develop reliable predictive models for combustion limits under reduced gravity conditions. The mission seeks to validate and improve simplified models by incorporating detailed chemical reactions, heat transfer, and material movement, using both space-based data and extensive ground-based tests. Key flight experiment goals include obtaining high-resolution measurements of droplet burning rates, flame extinction behavior, heat radiation, soot levels, and temperature profiles, while systematically analyzing the effects of different ambient conditions and suppressant concentrations. These investigations are essential for advancing the fundamental understanding of combustion processes in microgravity and enhancing fire safety protocols for future space missions.
- **Primary Citations:** NTRS 20140004923, NASA PSI-69
- **Audit Findings:** Droplet combustion, not solid flame spread; excluded from core model
### SAFFIRE-I (PSI-98)
- **Exact NASA Title:** Spacecraft Fire Safety Experiment-I
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-98](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98)
- **Flight Platform:** International Space Station (ISS)
- **Research Area:** Combustion Science (Spacecraft Fire, Smoke Distribution)
- **Usable for Prototype Modeling:** **YES**
- **Modeling Role:** Large-scale spacecraft environment benchmark and low-pressure validation
- **Key Variables:** oxygen_pct (18-24%), pressure_kpa (50-100 kPa), flow_cm_s (10-30 cm/s), sample_width_cm (5-40 cm), flame_growth_rate_cm_s
- **Sensory & Diagnostics:** Thermocouple arrays, pressure transducers, O2/CO2 sensors, radiometers; Calibrated digital cameras, video arrays, optical radiometry
- **Scientific Objective:** The objectives of this investigation were to: (1) determine how rapidly a large scale fire grows in low-gravity and (2) investigate the low-g flammability limits compared to those obtained in NASA’s normal gravity material flammability screening test.
- **Primary Citations:** NTRS 20200000557, NTRS 20180005168, NTRS 20240007488
- **Audit Findings:** Reference/Validation: Large scale PMMA and SIBAL fabric flame spread on Cygnus
### SAFFIRE-II (PSI-99)
- **Exact NASA Title:** Spacecraft Fire Experiment-II
- **NASA URL:** [https://psi.nasa.gov/physci/repo/data/investigations/PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99)
- **Flight Platform:** Cygnus Spacecraft
- **Research Area:** Combustion Science (Surface Combustion)
- **Usable for Prototype Modeling:** **YES**
- **Modeling Role:** Large-scale spacecraft environment benchmark and low-pressure validation
- **Key Variables:** oxygen_pct (18-24%), pressure_kpa (50-100 kPa), flow_cm_s (10-30 cm/s), sample_width_cm (5-40 cm), flame_growth_rate_cm_s
- **Sensory & Diagnostics:** Thermocouple arrays, pressure transducers, O2/CO2 sensors, radiometers; Calibrated digital cameras, video arrays, optical radiometry
- **Scientific Objective:** The objectives of SAFFIRE-II are to determine how rapidly a large scale fire grows in low-gravity and to investigate the low-g flammability limits compared to those obtained in NASA’s normal gravity material flammability screening test.
- **Primary Citations:** NTRS 20200000557, NTRS 20180005168, NTRS 20240007488
- **Audit Findings:** Reference/Validation: Fabric and thick PMMA flammability tests in low-g


---

## 4. Data Access & Provenance Verification

- All PSI investigation records were queried live from `https://psi.nasa.gov/geode-py/ws/repo/search`.
- NTRS reports and summary documents were retrieved through `https://ntrs.nasa.gov/api/citations/`.
- Every report has an active SHA256 checksum in `data/metadata/source_manifest.csv`.
- No NASA fields, variables, experiment names, or URLs were fabricated.
