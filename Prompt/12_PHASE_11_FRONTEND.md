# PHASE 11 — Frontend

## Goal
Create a polished science-first interface.

## Screens

### Home / Mission Control
Project story + analyze button.

### Scenario Lab
Inputs:
- material/fuel
- oxygen
- airflow
- pressure
- geometry
- suppressant
where supported.

### Fire Intelligence
Show:
- observed evidence
- model prediction
- uncertainty
- envelope status
- closest experiments

### Counterfactual Explorer
Interactive controls and comparison.

### NASA Experiment Atlas
Explore/filter experiments.

### Evidence Explorer
Full provenance and source details.

## Signature Visualization
NASA Experimental Fire Behaviour Map:
- NASA experiment points
- user scenario
- supported region
- extrapolation region

## UX Rules
- observed != predicted visually
- always show units
- always show sources
- warn on low evidence
- never show illustrative numbers as real

## Outputs
- app/
- docs/UI_SPEC.md
- reports/UI_QA.md

## Pass Criteria
A non-ML user can understand what is evidence, what is prediction, and how confident the system is.
