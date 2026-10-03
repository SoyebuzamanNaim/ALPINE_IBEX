# Phase 01 Report — Requirements & Scope

## Plan
Read the prompt pack (00–22, STATE.json), read the challenge brief, attempt to verify against the official
NASA Space Apps page, separate challenge requirements from design guidance, define users, primary
scenario, non-goals, and a traceability matrix.

## Executed
- `docs/REQUIREMENTS.md` — CR (Brief §1) vs DD (Brief §2–10) vs assumptions vs our innovations.
- `docs/PROBLEM_DEFINITION.md` — one decision question; observed/derived/predicted/generated taxonomy.
- `docs/NON_GOALS.md` — explicit non-goals and known limitations.
- `docs/TRACEABILITY_MATRIX.md` — requirement → implementation → test.

## Findings
- The official challenge page (spaceappschallenge.org) is client-side rendered; a static fetch of the
  guessed slug returned 404 and the challenges index has no server-rendered text. The challenge title and
  summary were cross-checked through search-engine snippets of the official page only. Logged as a
  verification gap in REQUIREMENTS.md; it does not change the build because the brief is authoritative.
- No conflicts between phase files and the brief at this stage. One reconciliation noted: the master
  layout has `src/models/`; the brief requires `src/compute/model.py` as the training entry point. Both
  exist.
- Phase 11 lists a "suppressant" input. The brief's explorer does not include it and the solid-fuel
  flame-spread data does not systematically vary suppressants. Following the brief (logged as conflict C-1).

## Conflicts log
| ID | Phase file says | Brief says | Resolution |
|---|---|---|---|
| C-1 | Phase 11: inputs include suppressant, geometry | §2/§9: oxygen, pressure, flow, material | Follow brief; geometry shown for display/filter only (§6) |
| C-2 | Phase 10 suggests many endpoints | §7 requires /predict, /health, /experiments, /model, /boundary | Implement brief set + selected extras (/envelope/check, /counterfactual, /analyze, /sources/{id}) |
