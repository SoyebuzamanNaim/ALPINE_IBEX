# Non-Goals and Prototype Limitations

## Non-goals

- **Not a certification tool.** It does not replace NASA-STD-6001 testing or any material qualification.
- **No universal fire-risk score.** Only the published regime classes are predicted.
- **No extrapolation.** Requests outside the training min/max (or unseen materials) are refused.
- **No physics simulation / CFD.** The model is a statistical summary of published tests.
- **No gas-phase droplet / gaseous flame tasks** (FLEX, ACME, SPICE) in the core model. They are
  catalogued in Phase 02 but not merged into the solid-fuel flame-spread table, because their variables
  (droplet diameter, burner, fuel jet) are not scientifically compatible with solid flame spread.
- **No causal claims.** Counterfactual sweeps show how the *model* changes, not proof of mechanism.
- **No chat-over-PDF.** The LLM (if configured) only words an explanation of a structured result.
- **No real-time spacecraft telemetry.**

## Prototype limitations (known up front)

- The training set is small (dozens to low hundreds of rows) and hand-extracted from PDF tables/figures;
  extraction errors are possible and every row records how it was extracted.
- Published microgravity data is clustered in a few materials and facilities; most of the 4-D input space
  is empty. The envelope guard is per-feature min/max, so some in-range combinations are still sparse;
  a kNN sparse-region warning flags these.
- Different gravity environments (ISS, drop tower, sounding rocket, parabolic flight) have different test
  durations; short-duration tests may misclassify slow near-limit flames.
- This is a pre-hackathon research prototype and must be kept separate from the competition submission.
