# Scientific limitations

FLARE-X is a research prototype for examining curated microgravity combustion observations. It is not certified engineering software and must not be used to approve spacecraft materials, predict operational fire risk, or guide emergency response.

## Dataset and model

The canonical table has 200 observations. It is unevenly distributed across materials, source reports, geometries, and experimental campaigns. Four numeric/categorical model inputs cannot encode all factors that affect flame behavior, including sample geometry, flow direction, ignition history, and test procedure. Some observations at identical model inputs have conflicting outcomes; the application abstains on these cases.

The current model reports 76.0% grouped accuracy against an 81.5% majority-class baseline, with 35.6% balanced accuracy and zero recall for `marginal_spread`. It does not demonstrate useful predictive skill. The API blocks public estimates for otherwise eligible conditions as `model_unvalidated`. These figures describe this curated dataset and evaluation split; they are not a claim about physical predictive performance. See [the rebuilt evaluation](../reports/REBUILT_MODEL_EVALUATION.md).

## Evidence boundaries

- The envelope guard limits requests to observed material-specific conditions and their joint domain. It does not establish safety inside that domain.
- Sparse material evidence and contradictory outcomes produce abstentions. A missing observation is not evidence that a condition is safe.
- Nearest observations provide context, not proof that an untested condition behaves the same way.
- The published cast-PMMA boundary in the UI is a separate empirical relation. It describes extinction of an established flame under its published conditions; it does not predict ignition or generalize to other materials or geometries.
- Counterfactual sweeps show changes in the current mathematical model and retrieval results. They do not simulate controlled physical interventions.

## Appropriate use

Use FLARE-X to explore evidence, check source coverage, and identify questions for qualified researchers. Do not use it for flight certification, operational fire-safety decisions, emergency response, or claims of NASA endorsement. Confirm scientific claims against the cited source documents and the applicable test standard.
