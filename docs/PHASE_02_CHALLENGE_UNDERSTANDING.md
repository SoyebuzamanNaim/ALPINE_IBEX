# Phase 2 — Challenge Understanding: Flame in Freefall

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Category:** Space Exploration (Advanced / Intermediate)  
> **Full brief release:** October 28, 2026 (Reconciliation milestone)

---

## 2.1 The Challenge in One Sentence

> **Turn a large, fragmented body of NASA microgravity-combustion experimental findings into an interactive AI system that helps people find, compare, prioritize, and understand evidence relevant to spacecraft fire safety.**

*Key distinction:* NASA does not say "Train the most accurate fire model imaginable." ML is an analytical component, but the explicit core is:  
`information overload → intelligent organization → interpretation → safety insight`.

---

## 2.2 The Three Problem Layers

* **Layer A — NASA already has the science:** NASA has accumulated decades of microgravity combustion research. We are not inventing combustion science from scratch.
* **Layer B — The knowledge is difficult to use:**
  - *Find:* Users struggle to locate experiments relevant to a particular question.
  - *Compare:* Experiments differ by material, fuel, oxygen, airflow, pressure, geometry, measurement type, and objective.
  - *Understand:* Turning experimental findings into useful safety understanding requires deep domain expertise.
* **Layer C — NASA wants the knowledge converted into safety insight:** The endpoint is not twelve PDFs, but what these experimental findings tell us about fire safety in human space exploration.

---

## 2.3 Deconstructing Every Important Word

| Official Concept | What It Means for Us |
| :--- | :--- |
| **Interactive** | User must actively explore, query, filter, compare, and alter conditions. Static report is insufficient. |
| **AI-powered** | AI must materially improve analysis or interpretation, not merely generate decorative text. |
| **Dashboard** | Information should be visually organized and operationally usable. |
| **Summarizes** | Condense experiments/results into understandable scientific representations. |
| **Ranks** | Prioritize experiments/findings according to relevance or defensible scientific criteria. |
| **Interprets** | Explain what experimental observations mean, not merely retrieve them. |
| **Findings** | Results from NASA combustion experiments are the core information substrate. |
| **Fire-safety insights** | Outputs must connect experimental evidence to safety-relevant understanding. |
| **Human space exploration** | Moon/Mars/deep-space crew safety is the context, not terrestrial firefighting. |

---

## 2.4 Four Explicitly Expected Functions

1. **FIND:** Evidence Retrieval Engine across diverse experiment files, reports, and metadata.
2. **SUMMARIZE:** Structured conversion of raw reports and sensor observations into clear parameter-outcome summaries.
3. **RANK:** Scientific Relevance Ranking based on query conditions (e.g. material, oxygen, airflow, pressure).
4. **INTERPRET:** Domain-aware reasoning explaining why results match or diverge, guarded by the Experimental Envelope.

---

## 2.5 What "Fire Safety Insights" Should Mean

FLARE-X does not claim to "certify" spacecraft safety (which requires formal certification boards). Instead, it delivers responsible decision-support insights:
- **Evidence insight:** Similar NASA experiments showed sustained combustion under comparable conditions.
- **Comparative insight:** Increasing airflow shifts the scenario closer to experiments exhibiting sustained propagation.
- **Confidence insight:** Evidence is strong because several NASA experiments occupy similar parameter conditions.
- **Uncertainty insight:** Few experiments exist at this pressure, so confidence is reduced.
- **Knowledge-gap insight:** NASA data provide limited coverage for this material/condition combination.

---

## 2.6 Central Workflow

```
USER QUESTION / SCENARIO
          │
          ▼
        FIND (Relevant NASA evidence)
          │
          ▼
       SUMMARIZE (What happened?)
          │
          ▼
        RANK (Which findings matter most?)
          │
          ▼
       COMPARE (How do experiments differ?)
          │
          ▼
      INTERPRET (What does the evidence imply?)
          │
          ▼
       EXPLAIN (Confidence + limitations + sources)
          │
          ▼
FIRE-SAFETY INSIGHT
```

---

## 2.7 Explicit Requirements vs Strategic Additions

| Feature / Element | Classification | Rationale |
| :--- | :--- | :--- |
| Interactive Dashboard | **Explicit Requirement** | Directly in NASA challenge summary |
| AI-Powered Summarize, Rank, Interpret | **Explicit Requirement** | Directly in NASA challenge summary |
| Microgravity Combustion Evidence Base | **Explicit Requirement** | Directly in NASA challenge summary |
| Human Spaceflight Safety Insights | **Explicit Requirement** | Directly in NASA challenge summary |
| ML Prediction (Flame Spread / Extinction) | Proposed Enhancement | Adds quantitative rigor to qualitative retrieval |
| Experimental Envelope Guard | Proposed Enhancement | Prevents hallucination & unphysical extrapolation |
| Counterfactual Analysis / Parameter Sweep | Proposed Enhancement | Allows exploring "what if ventilation changes" |
| Evidence Auditor & Traceability | Proposed Enhancement | Links every numerical output directly to NTRS/PSI sources |

---

## 2.8 Strategic Anti-Patterns (What NOT to Make)

- ❌ *PDF Chatbot:* Too shallow, hallucinates numbers, lacks quantitative comparison.
- ❌ *Static Experiment Database:* Insufficient AI and interpretation.
- ❌ *Single Standalone ML Classifier:* Fails to organize and interpret decades of findings.
- ❌ *Generic Fire Simulator / Animation:* Weak grounding in NASA empirical test points.
- ❌ *Single Universal "Fire-Risk Score":* Scientifically dubious without rigorous parameter-by-parameter bounds.

---

## 2.9 Phase 2 Acceptance Criteria (The 5-Question Test)

Every proposed feature must pass:
1. Does it help **find** evidence?
2. Does it help **compare** evidence?
3. Does it help **summarize / rank / interpret** evidence?
4. Does it create a **defensible fire-safety insight**?
5. Can that insight remain **traceable to NASA evidence**?

---

## 2.10 Video 1 (Prescreening) 15-Second Challenge Hook

> *"NASA has spent decades studying how fire behaves in microgravity. The problem is no longer a lack of experiments; it is turning that growing body of evidence into information that can be quickly found, compared, and understood. Flame in Freefall asks us to create an interactive, AI-powered dashboard that summarizes, ranks, and interprets those findings for human spaceflight fire safety."*
