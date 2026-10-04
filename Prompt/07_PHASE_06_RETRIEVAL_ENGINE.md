# PHASE 06 — Evidence Retrieval Engine

## Goal
Retrieve NASA experiments and documents relevant to a scenario.

## Architecture
Scenario
→ structured filters
→ candidate experiments
→ semantic retrieval on descriptions/docs
→ reranking
→ evidence bundle

## Important
Do not convert numerical science into embeddings when structured querying is superior.

## Evidence Bundle
Must include:
- investigation
- experiment ID
- source URL
- source file
- matched variables
- mismatched variables
- similarity explanation
- retrieval score
- scientific caveat

## Evaluation
Build a manually reviewed query set and evaluate:
- Precision@K
- citation correctness
- scientific relevance
- false-positive retrievals

## Outputs
- src/retrieval/
- docs/EVIDENCE_BUNDLE_SCHEMA.md
- reports/RETRIEVAL_EVAL.md
- tests/test_retrieval.py

## Pass Criteria
No evidence bundle may contain an invented experiment or source.
