# FLARE-X Video Visual Asset Pack

This directory contains the production graphics, vector slides, and timeline configuration for the official 240-second prescreening video for NASA Space Apps Challenge 2026 ("Flame in Freefall").

## Master Asset Registry (22 Video Assets)

| Asset Name | Target Time | Core Purpose |
|---|:---:|---|
| `00_opener_microgravity_fire` | 0:00–0:10 | Opening microgravity-fire physics hook |
| `01_nasa_investigation_families` | 0:10–0:22 | BASS-II / FLEX / SPICE / SAFFIRE / SAME flight programs |
| `02_problem_fragmentation` | 0:22–0:29 | Fragmented evidence problem across NASA archives |
| `03_flarex_title_card` | 0:29–0:36 | FLARE-X project title reveal & mission subtitle |
| `04_team_card_template` | 0:36–0:42 | All 6 team names + registered functional roles |
| `05_mission_find_compare_model_verify_trace` | 0:42–0:52 | Core 6-step mission workflow overview |
| `06_research_question` | 0:52–0:02 | Flagship scientific question (PMMA at exploration atmospheres) |
| `07_heterogeneous_conditions` | 1:02–1:14 | Comparison problem across fuels, pressures, geometries |
| `08_search_vs_scientific_comparability` | 1:14–1:38 | Keyword similarity vs physical transport comparability |
| `09_scenario_interpretation` | 1:38–1:48 | Natural language prompt to structured scenario card |
| `10_combustion_family_router` | 1:48–1:58 | Adaptive routing across solid, liquid, gas, smoke families |
| `11_ranked_nasa_evidence` | 1:58–2:10 | Experiment ranking via hybrid BM25 + Gower physical similarity |
| `12_specialized_model_router` | 2:10–2:26 | SPICE-FL / FLEX-EX / conditional BASS-RG architecture |
| `13_experimental_envelope_guard` | 2:26–2:35 | Envelope Guard firewall: "FLARE-X knows when not to predict" |
| `14_support_map_inside` | 2:35–2:50 | Support Map: State 1 (21% O2 inside supported domain) |
| `15_support_map_near_boundary` | 2:50–3:05 | Support Map: State 2 (19% O2 near flammability boundary) |
| `16_support_map_outside` | 3:05–3:15 | Support Map: State 3 (17% O2 partial support) |
| `17_counterfactual_three_state_sequence` | 3:15–3:23 | Dynamic 3-state slider sequence (21% -> 18% -> 14% O2) |
| `18_prediction_withheld` | 3:23–3:32 | Signature moment: OUTSIDE DOMAIN / Reliable prediction withheld |
| `19_provenance_chain` | 3:32–3:43 | 3-tier provenance: NASA Obs != Model Inference != AI Synthesis |
| `20_end_card` | 3:43–3:49 | Final FLARE-X close: "Find the evidence. Know its limits." |
| `21_credits_disclosure_card` | 3:49–3:52 | Sources & disclosures: NASA PSI credits + Apache 2.0 |

## Specifications & Tokens
- See [`brand_tokens.json`](./brand_tokens.json) for hex tokens, font hierarchies (Orbitron, JetBrains Mono, Inter), and action/title/subtitle safe zones.
- See [`timeline.csv`](./timeline.csv) for duration and start/end timecodes.
- Open [`asset_gallery.html`](./asset_gallery.html) in any browser for an interactive, full-screen 16:9 1080p preview.

## Mandated Concept Disclaimers
All concept screens preserve labels such as `[ ILLUSTRATIVE CONCEPT UI ]`, `[ PROPOSED INTERACTION ]`, and `[ PLANNED MODEL ]`. No fabricated performance statistics ("95% accuracy") are permitted.
