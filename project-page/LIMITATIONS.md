# FLARE-X Scientific Limitations

FLARE-X is a research and scientific decision-support prototype/concept. It is **not** certified engineering guidance, mission-control software, material-safety certification or operational emergency-response software.

Key limitations:

- NASA investigations cover specific fuels, materials, geometries, oxygen concentrations, pressures, airflow conditions, measurement methods and scales.
- Controlled microgravity experiments do not automatically represent full spacecraft fire scenarios.
- Models are experiment-family-specific and should primarily be used for interpolation inside validated domains.
- Model probability, evidence similarity, domain support and evidence strength are distinct quantities and should not be collapsed into one confidence score.
- Counterfactual model changes are not automatically causal proof.
- Feature importance is model explanation, not physical causality.
- Missing evidence must never be interpreted as evidence of safety.
- Search failure only means no compatible evidence was found in the currently indexed FLARE-X corpus; it does not prove relevant NASA research does not exist elsewhere.
- NASA observations, FLARE-X model inference and AI synthesis must remain visually and semantically distinct.
- Unvalidated or automatically extracted values should not be used as authoritative quantitative training data until verified.
- Frames or repeated measurements from one physical burn are not automatically independent experiments.

FLARE-X should abstain from reliable quantitative prediction when required inputs are missing, the model family is wrong, critical conditions are unsupported, local experimental coverage is insufficient, model validation is inadequate or provenance is broken.
