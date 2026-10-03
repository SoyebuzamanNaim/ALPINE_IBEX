# Evidence Bundle Schema (Phase 06)

> **Document Status:** Authoritative specification for evidence retrieval bundles in FLARE-X.

## 1. Overview
The Evidence Retrieval Engine combines **structured nearest-neighbor search over verified experiments**
with **BM25 semantic search over the NASA report corpus**.
Per Phase 06 instructions: *numerical science is never converted into embeddings when structured querying is superior.*

## 2. Schema Specification

An `EvidenceBundle` contains:
1. `scenario`: The requested input parameters (`oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`).
2. `nearest_experiments`: Array of top-$K$ real NASA experiments closest in feature space:
   - `experiment_id`: String
   - `investigation`: String (e.g. `BASS-II`)
   - `material`: String
   - `oxygen_pct`: Float
   - `pressure_kpa`: Float
   - `flow_cm_s`: Float
   - `outcome`: Categorical (`no_spread`, `marginal_spread`, `spread`)
   - `distance`: Float (normalized Euclidean distance)
   - `report_id`: String
   - `source_url`: String (resolvable citation)
   - `source_page`: Integer (optional)
   - `source_table`: String (optional)
   - `matched_variables`: List of strings where requested condition closely matched observation
   - `mismatched_variables`: List of strings where condition differed
   - `similarity_explanation`: Human-readable summary of similarity
3. `cited_reports`: Dictionary of unique report documents supporting the nearest experiments:
   - `report_id`: String
   - `title`: String
   - `abstract`: String
   - `source_url`: String
   - `supporting_passage`: Relevant excerpt extracted from abstract/conclusions
4. `scientific_caveats`: List of domain caveats (e.g. flow direction differences, scale effects).

## 3. Distance Metric Formulation

Let $x = (\text{O}_2, p, v)$ be the input vector and $x^{(j)}$ be experiment $j$.
$$\Delta \text{O}_2 = \frac{|\text{O}_2 - \text{O}_2^{(j)}|}{\max(\text{O}_2) - \min(\text{O}_2)}$$
$$\Delta p = \frac{|p - p^{(j)}|}{\max(p) - \min(p)}$$
$$\Delta v = \frac{|v - v^{(j)}|}{\max(v) - \min(v)}$$

$$\text{Material Penalty } M = \begin{cases} 0 & \text{if } \text{material} = \text{material}^{(j)} \\ 10.0 & \text{otherwise} \end{cases}$$

$$\text{Distance } d = \sqrt{(\Delta \text{O}_2)^2 + (\Delta p)^2 + (\Delta v)^2} + M$$
