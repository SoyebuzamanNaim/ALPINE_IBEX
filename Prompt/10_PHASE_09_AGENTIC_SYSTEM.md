# PHASE 09 — Agentic System

## Goal
Build bounded agents with explicit jobs.

## Agents

### 1. Scenario Interpreter
Natural language → structured schema.
Must expose ambiguity.

### 2. Evidence Retriever
Calls the retrieval engine.
Cannot invent evidence.

### 3. Model Router
Chooses the model based on scenario + requested output.

### 4. Experimental Envelope Guard
Checks support before prediction is presented.

### 5. Counterfactual Analyst
Runs controlled changes.

### 6. Evidence Auditor
Verifies:
- source
- model
- units
- confidence
- envelope
- assumptions

### 7. Explanation Composer
Converts verified structured outputs into readable language.

## Orchestration
Use explicit state machine, not unconstrained agent chatter.

## Agent Output Contract
All agents return structured JSON.

## Security / Reliability
- no arbitrary code execution from user prompts
- no unverified URLs as evidence
- no fabricated source IDs
- enforce schema validation

## Outputs
- src/agents/
- docs/AGENT_STATE_MACHINE.md
- docs/AGENT_CONTRACTS.md
- tests/test_agents.py

## Pass Criteria
Agents must fail safely and cannot bypass evidence/envelope controls.
