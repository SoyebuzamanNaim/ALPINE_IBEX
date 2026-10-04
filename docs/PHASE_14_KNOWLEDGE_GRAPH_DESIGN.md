# Phase 14 — Knowledge Graph Design: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Multi-investigation relational intelligence connecting NASA experiments, materials, conditions, phenomena, outcomes, documents, model runs, and claims into a unified scientific knowledge graph. Operates within a hybrid architecture where PostgreSQL remains the ground truth for numerical data and the graph governs semantic relationships and multi-hop provenance.

---

## Executive Summary & Guiding Principle

The knowledge graph is not implemented because “graph databases” sound sophisticated. Its explicit purpose is to:
> **Allow FLARE-X to resolve multi-hop scientific relationships that are cumbersome in flat tables and unreliable when left entirely to dense semantic embeddings.**

---

## 14.1 Target Multi-Hop Relational Queries

The graph answers questions that span multiple NASA flight investigations:
* *Which NASA experiments tested PMMA under opposed flow below 18% oxygen?*
* *Which SAFFIRE large-scale tests provide spacecraft-scale context for this BASS-II small-scale burn?*
* *Which peer-reviewed NASA reports document this exact flight run?*
* *Which machine learning model version was trained on this specific subset of flight tests?*
* *Which historical flight experiments directly contradict this claim?*

---

## 14.2 The Hybrid Storage Architecture

FLARE-X does not deploy a graph-only system. We enforce a balanced tripartite architecture:

```
                            HYBRID STORAGE ENGINE
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  [RELATIONAL (SQL)]           [VECTOR STORE]           [KNOWLEDGE GRAPH]
  • Exact numerical values     • Raw document chunks    • Entity relationships
  • Tabular sensor series      • Dense semantic search  • Multi-hop provenance
  • Model parameter weights    • Unstructured reports   • Contradiction tracking
```

*Rule:* Relational tables remain the authoritative source of truth for numerical measurements. The Knowledge Graph is the authority for **semantic topology and provenance relationships**.

---

## 14.3 Canonical Node Taxonomy

The knowledge graph contains 17 strictly typed node classes:

```
                             CANONICAL NODE TYPES
                                      │
  ├── Physical Domain:      Investigation, Experiment, ConditionSet
  ├── Chemical / Material:  Material, Fuel, MaterialFamily, CombustionFamily
  ├── Hardware / Scale:     Geometry, MeasurementType
  ├── Physics Phenomena:    Phenomenon, Outcome
  ├── Source Documents:     Document, SourceFile, Evidence
  └── Inference & Claims:   Model, ModelRun, Claim
```

---

## 14.4–14.21 Node Specifications & The ConditionSet Invariant

### 1. `Investigation` Node
* Root entity representing a major NASA flight project:
  - `BASS-II` (PSI-25, DOI: `10.2514/6.2014-3677`)
  - `FLEX` (PSI-69, Droplet Combustion)
  - `SPICE` (PSI-107, Gaseous Smoke Point)
  - `SAFFIRE-I` (PSI-98, Spacecraft Fire Safety)
  - `SAME` (PSI-102, Smoke Aerosol Measurement)

### 2. `Experiment` Node
* Represents an independent physical microgravity burn:
  - Properties: `experiment_id`, `test_id`, `run_id`, `flight_increment`, `chamber_hardware`.

### 3. `ConditionSet` Node (Multivariate Invariant)
* Rather than scattering isolated edges (`Experiment -> 18% O2`, `Experiment -> 20 cm/s`), conditions are encapsulated in a single node:
  ```json
  {
    "condition_set_id": "cs_bass2_031",
    "oxygen_fraction": 0.18,
    "pressure_kpa": 101.3,
    "airflow_m_s": 0.20,
    "flow_direction": "opposed"
  }
  ```
  $$\text{Experiment 31} \xrightarrow{\texttt{TESTED\_UNDER}} \text{ConditionSet 31}$$
* Preserves multivariate environmental co-occurrence.

### 4. `Material` & `MaterialFamily` Nodes
* Represents combustible solids and chemical hierarchies:
  $$\text{PMMA} \xrightarrow{\texttt{MEMBER\_OF}} \text{Acrylic Polymer} \xrightarrow{\texttt{MEMBER\_OF}} \text{Thermoplastic}$$

### 5. `Fuel` & `CombustionFamily` Nodes
* Gaseous and liquid fuels linked to canonical combustion modes:
  $$\text{Methane} \xrightarrow{\texttt{HAS\_PHASE}} \text{Gas} \quad \text{and} \quad \text{Experiment} \xrightarrow{\texttt{BELONGS\_TO}} \text{GAS\_DIFFUSION\_FLAME}$$

### 6. `Phenomenon` vs. `Outcome` Nodes
* Distinguishes the physical question from the experimental result:
  - **Phenomenon:** What was studied (`FLAME_SPREAD`, `EXTINCTION`, `SOOT_FORMATION`).
  - **Outcome:** What actually occurred (`SUSTAINED_PROPAGATION`, `COMPLETE_BURNOUT`, `SELF_EXTINGUISHED`).
  $$\text{Experiment 31} \xrightarrow{\texttt{STUDIES}} \text{FLAME\_SPREAD} \quad \text{and} \quad \text{Experiment 31} \xrightarrow{\texttt{OBSERVED}} \text{SUSTAINED\_PROPAGATION}$$

### 7. `Claim`, `Evidence`, and `ModelRun` Nodes
* Fully connects inference and provenance:
  $$\text{ModelRun} \xrightarrow{\texttt{SUPPORTS}} \text{Claim} \xleftarrow{\texttt{SUPPORTS}} \text{Evidence} \xrightarrow{\texttt{ABOUT}} \text{Experiment}$$

---

## 14.22 Core Relationship Vocabulary

The graph uses a closed, controlled vocabulary of 21 canonical edge types:

| Relationship Edge | Source $\to$ Target | Semantic Meaning |
| :--- | :--- | :--- |
| `CONTAINS` | Investigation $\to$ Experiment | NASA project contains discrete test runs |
| `TESTED_UNDER` | Experiment $\to$ ConditionSet | Hardware atmosphere and flow parameters |
| `USES_MATERIAL` | Experiment $\to$ Material | Solid combustible sample mounted in duct |
| `USES_FUEL` | Experiment $\to$ Fuel | Liquid droplet or gaseous burner fuel |
| `MEMBER_OF` | Material $\to$ MaterialFamily | Polymer chemical hierarchy |
| `STUDIES` | Experiment $\to$ Phenomenon | Physical focus of the investigation |
| `OBSERVED` | Experiment $\to$ Outcome | Ground truth physical observation |
| `MEASURED` | Experiment $\to$ MeasurementType | Specific sensor channel logged |
| `DOCUMENTED_IN` | Experiment $\to$ Document | NASA technical report describing burn |
| `EXTRACTED_FROM`| Evidence $\to$ SourceFile | Data parsed from verified CSV/PDF |
| `SUPPORTS` | Evidence / ModelRun $\to$ Claim | Direct factual backing for claim |
| `CONTRADICTS` | Evidence $\to$ Claim / Evidence | Physical or model disagreement |
| `TRAINED_ON` | Model $\to$ Dataset Manifest | Source dataset used to train ML pipeline |
| `PRODUCED` | Model $\to$ ModelRun | Model execution instance |

*Prohibition:* Free-form, ad-hoc edge creation by LLMs is strictly banned.

---

## 14.23 Edge Provenance & Metadata

Every relationship edge carries provenance attributes:
* `source_evidence_id`: Canonical evidence ID establishing the link.
* `verification_status`: `VERIFIED` vs. `AUTO_EXTRACTED_UNVERIFIED`.
* `source_locator`: Table row, PDF page, or video timestamp.

---

## 14.28–14.32 Graph Query Workflows

### Query 1: Finding Material-Phenomenon Overlap
$$\text{PMMA} \xleftarrow{\texttt{USES\_MATERIAL}} \text{Experiments} \xrightarrow{\texttt{STUDIES}} \text{FLAME\_SPREAD}$$

### Query 2: Cross-Scale Spacecraft Context (BASS $\to$ SAFFIRE)
$$\text{BASS-II Exp} \xrightarrow{\texttt{USES\_MATERIAL}} \text{PMMA} \xleftarrow{\texttt{USES\_MATERIAL}} \text{SAFFIRE-I Exp}$$
Surfaces spacecraft-scale fire observations alongside benchtop duct tests.

### Query 3: Multi-Hop Provenance ("Why Should I Trust This?")
$$\text{Claim} \xleftarrow{\texttt{SUPPORTS}} \text{Evidence} \xrightarrow{\texttt{ABOUT}} \text{Experiment} \xrightarrow{\texttt{DOCUMENTED\_IN}} \text{NASA NTRS Report}$$

### Query 4: Automated Contradiction Resolution
$$\text{Claim} \xleftarrow{\texttt{SUPPORTS}} \text{Evidence A (Sustained)} \quad \text{and} \quad \text{Claim} \xleftarrow{\texttt{CONTRADICTS}} \text{Evidence B (Extinguished)}$$
Graph immediately returns both experiments and executes condition comparison.

---

## 14.43–14.44 Practical MVP Storage Schema (PostgreSQL)

For the competition build, the graph is implemented via high-performance relational tables without requiring dedicated Neo4j hosting:

```sql
CREATE TABLE kg_entities (
    entity_id VARCHAR(64) PRIMARY KEY,
    entity_type VARCHAR(32) NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE kg_relationships (
    relationship_id VARCHAR(64) PRIMARY KEY,
    source_entity_id VARCHAR(64) REFERENCES kg_entities(entity_id),
    relation_type VARCHAR(32) NOT NULL,
    target_entity_id VARCHAR(64) REFERENCES kg_entities(entity_id),
    evidence_id VARCHAR(64),
    verification_status VARCHAR(32) DEFAULT 'VERIFIED',
    metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_kg_rel_source ON kg_relationships(source_entity_id, relation_type);
CREATE INDEX idx_kg_rel_target ON kg_relationships(target_entity_id, relation_type);
```

---

## 14.46 Contextual Neighborhood Graph Visualization (UI Spec)

The frontend avoids cluttered "hairball" graph renders. It renders **focused 2-hop contextual subgraphs**:

```
                       [PMMA]
                      /      \
           USES_MATERIAL    USES_MATERIAL
                    /          \
        [BASS-II Test 31]      [SAFFIRE-I Burn 2]
                │                      │
             OBSERVED               OBSERVED
                ▼                      ▼
      [Steady Flame Spread]   [Rapid Flame Growth]
         (Small Duct)           (Spacecraft Scale)
```

---

## 14.49 Parameterized Graph Query Templates

To ensure stability and security, the system executes pre-compiled query templates rather than raw text-to-Cypher:
* `get_experiments_by_material(material_id, phenomenon_id)`
* `get_cross_scale_context(material_id, baseline_investigation)`
* `get_contradicting_evidence(claim_id)`
* `get_claim_provenance_tree(claim_id)`

---

## 14.53 Video 1 Pitch Narration (20–25 Seconds)

> *"FLARE-X builds a scientific knowledge graph connecting NASA investigations, individual flight experiments, materials, atmospheric conditions, phenomena, outcomes, and source documents.*
> 
> *This allows the system to reason across separate spaceflight programs without conflating small-scale duct tests with large-scale spacecraft burns."*

---

## 14.55 Canonical Master Graph Architecture

```
                     NASA INVESTIGATION
                            │
                         CONTAINS
                            ▼
                        EXPERIMENT
                 ┌──────────┼──────────┐
                 │          │          │
          USES_MATERIAL  TESTED_UNDER STUDIES
                 │          │          │
                 ▼          ▼          ▼
              MATERIAL   CONDITION   PHENOMENON
                 │                     │
              MEMBER_OF                │
                 ▼                     │
          MATERIAL FAMILY              │
                                       │
                        EXPERIMENT ─OBSERVED→ OUTCOME
                            │
                      DOCUMENTED_IN
                            ▼
                         DOCUMENT
                            │
                       EXTRACTED_TO
                            ▼
                         EVIDENCE
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
              SUPPORTS             CONTRADICTS
                 │                     │
                 └──────────► CLAIM ◄──┘
                                ▲
                                │
                           SUPPORTED_BY
                                │
                           MODEL RUN
                                │
                          INSTANCE_OF
                                ▼
                              MODEL
                                │
                           TRAINED_ON
                                ▼
                         NASA DATASET
```

---

## 14.56 Phase 14 Locked Decisions Matrix

| Decision | Status | Rationale |
| :--- | :---: | :--- |
| **Hybrid SQL + Vector + Graph** | ✅ Locked | Best-in-class storage for each data modality |
| **Relational as Numerical Truth** | ✅ Locked | Prevents floating-point drift across graph layers |
| **ConditionSet Node Architecture** | ✅ Locked | Preserves multivariate environmental co-occurrence |
| **Phenomenon vs Outcome Separation** | ✅ Locked | Clarifies what was studied vs. what occurred |
| **Controlled Edge Vocabulary (21 Types)**| ✅ Locked | Eliminates unstructured relationship hallucination |
| **Edge-Level Provenance** | ✅ Locked | Every graph link traces to a source locator |
| **Contextual Neighborhood Visuals** | ✅ Locked | 2-hop focused subgraphs over spaghetti visualizers |
| **Parameterized Query Templates** | ✅ Locked | Deterministic graph traversal over raw LLM queries |
| **Cross-Scale Linking (BASS $\to$ SAFFIRE)**| ✅ Locked | Connects benchtop physics to vehicle-level risk |

---

## ✅ Phase 14 Status: COMPLETE

The Scientific Knowledge Graph design is formally codified and locked.
