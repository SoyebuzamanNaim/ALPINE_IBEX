# Outcome labeling protocol

This is a curation protocol for FLARE-X research labels. It is not a material-safety standard.
A label describes a particular reported observation and test history; it does not certify a
material or predict what happens under another protocol.

| Label | Indexed interpretation | Inference limit |
|---|---|---|
| `no_spread` | The curated record describes failure to sustain spread, failure to ignite, or extinction at a reported condition. | Ignition failure and extinction of an established flame are different observations. Neither implies inherent safety. |
| `marginal_spread` | The curated record describes limited, unstable or intermittent propagation. | The label alone does not establish a threshold, spread rate or operational hazard level. |
| `spread` | The curated record describes sustained propagation or continued burning under its test conditions. | It does not quantify an operational spacecraft fire scenario. |

## Source and interpretation

Preserve the source observation text, test identifier, citation, oxygen basis, geometry,
flow direction and available ignition history. Do not turn keyword matches into new labels
without reading the full observation. A sentence containing both initial burning and later
extinction cannot be reduced safely by taking its first matching keyword.

BASS-II conditions come from PSI-25; outcome labels were hand assigned from the report's
observations. They are curated interpretations, not an outcome column supplied by PSI.
The legacy canonical table's `outcome_interpreted` flag does not consistently encode this:
its current false values must not be presented as proof that these labels are direct
measurements. The application displays source text and identifies the outcome as a curated
label. Scientific review of the label assignments remains necessary.

## Multiple conditions in one burn

A velocity ramp or oxygen-depletion sequence is one evolving experiment. A record may
index one condition along it. Do not count repeated conditions as independent burns, infer
an ignition limit from a later extinction, or use initial oxygen as post-burn oxygen.
If the source does not tie an outcome to an exact condition, leave the label unresolved in
the curation worksheet rather than adding a training row.

## Review and regeneration

A reviewer should record the quoted observation, page/table/test, interpretation reason,
oxygen basis, and whether ignition preceded the indexed condition. Exclude ambiguous or
unverifiable assignments from any future canonical rebuild. Any accepted label or condition
change requires ingestion validation, retraining, regenerated evaluation and model card,
artifact verification, and the API/browser regression suites. Never change labels to
increase prediction accuracy.
