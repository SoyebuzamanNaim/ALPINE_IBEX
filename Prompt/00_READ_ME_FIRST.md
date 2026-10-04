# FLARE-X Autonomous Prototype Agent Pack

This pack is designed to let an autonomous coding agent build a complete **research/demo prototype** of FLARE-X now:
data ingestion → baseline models → retrieval → agents → frontend → integration → validation → working demo.

## Competition-compliance boundary

NASA's 2026 public guidance says the solution intended for submission must be developed during the official hackathon window. Therefore:

- Treat the pre-hackathon build created by this pack as a **research/demo prototype**.
- Keep it in a separate repository from the eventual competition submission.
- Do not backdate, conceal, or misrepresent when prototype code was created.
- During the official build window, use the prototype as knowledge/reference and perform a clean-room rebuild for the submitted project unless you have explicit written approval that reuse is allowed.

## Goal

By the end, the prototype should include:

1. NASA PSI data ingestion
2. Data audit and harmonization
3. Baseline ML models
4. Evidence retrieval
5. Experimental-envelope detection
6. Counterfactual analysis
7. Agent orchestration
8. Backend API
9. Frontend
10. Integration
11. Scientific validation
12. Demo scenarios
13. Video-ready visuals
14. Complete documentation

## How to run

Give `01_MASTER_AUTOPILOT_PROMPT.md` to your coding agent and tell it to execute phase files in order.

The product spec, judging criteria, API contract and Definition of Done live in
`22_CHALLENGE_BRIEF_FLAME_IN_FREEFALL.md`. The agent must read it before Phase 01.

The agent must:
- validate each phase,
- write reports,
- repair failures,
- update STATE.json,
- stop if a phase cannot be scientifically validated,
- never invent NASA data or model metrics.
