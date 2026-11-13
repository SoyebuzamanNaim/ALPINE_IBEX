# Accuracy experiments and serving model

The serving model is the selected four-input **linear SVM, C=1.0**, with an **84.0% exploratory grouped selection score**, versus the **81.5% majority baseline**. Guarded research estimates are available. The full search procedure's nested accuracy is **25.5%**; this evaluates the selection procedure, not the fixed SVM alone. No independent external validation or operational safety is established.

- [Corrected complete experiment report](runs/20261113T111613601552Z/SUMMARY.md)
- [Latest complete run manifest](latest.json)
- [Current serving model card](../../docs/MODEL_CARDS.md)
- [Frontend and backend verification](../FRONTEND_INTEGRATION.md)
- [Historical initial report](INITIAL_SUMMARY.md)

The overlap-purging correction now removes matching-condition labels from inner selection and reports actual training sizes. Complete runs publish atomically from staging into immutable directories; an interruption preserves the previous completed bundle. Regression checks cover both fixes. The root-level CSV/JSON files and the original `models/accuracy_candidate_*` files preserve the first run; the immutable bundle linked above contains the corrected evaluation used by the serving metadata.
