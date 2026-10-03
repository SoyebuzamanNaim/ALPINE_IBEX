# Phase 07 Validation: Experimental Envelope Guard

## Test Execution Summary
- **Test File:** `tests/test_envelope.py`
- **Total Tests:** 6
- **Status:** PASS (6/6 passing in 0.47s)

## Verification Matrix

| Test Case | Scenario / Query | Expected Domain Status | Result | Nearest Evidence Included? |
|---|---|---|---|---|
| `test_in_domain_standard_condition` | PMMA, 21% O2, 101.3 kPa, 5 cm/s | `in_domain` / `boundary` | PASS | YES (3 nearest experiments) |
| `test_boundary_condition` | PMMA, 16.5% O2, 101.3 kPa, 3 cm/s | `boundary` | PASS | YES (Near extinction warning generated) |
| `test_global_out_of_range_refusal` | PMMA, 40.0% O2, 101.3 kPa, 5 cm/s | `extrapolation` | PASS | YES (Refusal triggered, 3 nearest retained) |
| `test_unsupported_material_refusal` | Kapton, 21.0% O2, 101.3 kPa, 5 cm/s | `unsupported_category` | PASS | YES (Refusal triggered, 3 nearest retained) |
| `test_per_material_out_of_range` | Nomex, 17.0% O2, 101.3 kPa, 5 cm/s | `extrapolation` | PASS | YES (Nomex bounded to [20.8, 34.0]% O2) |
| `test_sparse_region_detection` | PMMA, 32.0% O2, 60.0 kPa, 34 cm/s | `sparse_region_warning` | PASS | YES (kNN mean distance computed) |

## Pass Criteria Verification
1. **Never extrapolate without refusal:** All out-of-bounds parameters yield `in_training_range: false`, `prediction: null`, and explicit reason breakdown. (VERIFIED)
2. **Never hide nearest evidence:** On refusal, the top 3 nearest historical microgravity experiments are still attached so operators see what NASA has actually tested. (VERIFIED)
3. **Categorical enforcement:** Unseen materials are rejected with `unsupported_category` rather than silently defaulting or failing. (VERIFIED)
4. **Sparse region awareness:** Within-box points that lack nearby data trigger a warning via 3-NN distance calculation. (VERIFIED)
