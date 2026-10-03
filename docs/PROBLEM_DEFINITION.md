# Problem Definition

## Decision problem

> *"Given an atmosphere (oxygen fraction, pressure), an imposed flow, and a material, what flame-spread
> regime did published microgravity experiments observe nearby — and is there enough data here to say
> anything at all?"*

This is narrower than an "AI fire dashboard". FLARE-X answers one question, for one class of
experiments (solid-fuel flame spread / flammability limits in microgravity), with one quantitative model,
and refuses outside the published data envelope.

## Why it matters

Without buoyancy, a flame's oxygen supply comes only from imposed (ventilation) flow and diffusion.
Materials can therefore be *more* or *less* flammable in microgravity than in Earth-based tests,
depending on flow. Spacecraft atmospheres (e.g. exploration atmospheres with reduced pressure and raised
O₂) push conditions away from 1-g test experience.

## What the user gets

| Output | Kind | Provenance shown |
|---|---|---|
| Training table rows | **Observed** (extracted from NTRS reports) | report ID, URL, page/table/figure, extraction method |
| Regime class + probabilities | **Model prediction** | model type, `n_train`, CV accuracy and scheme |
| In-range / out-of-range status | **Rule** (training min/max) | offending feature, value, train min/max |
| Nearest experiments | **Observed** (retrieval over the table) | distance, report ID, URL |
| Explanation text | **Generated** (template or bounded LLM) | labelled as AI/template-written; numbers checked |

## Success criteria

- Every number on screen traces back to a table row, the trained artifact, or the metrics file.
- Out-of-range requests never show a probability bar.
- The cross-validated accuracy is grouped by report and printed beside the majority baseline.
