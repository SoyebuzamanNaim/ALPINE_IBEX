# Model evaluation on the rebuilt dataset

Evaluated on the corrected data: `experiments_bass2_relabelled.csv` (158 rows) plus
`experiments_saffire_verified.csv` (21 rows). The 2 `marginal_spread` rows are dropped —
two examples cannot support a class — leaving **177 rows, 149 `spread` / 28 `no_spread`**,
in **82 groups**. Evaluation is leave-one-test-out, so no sweep's sibling rows ever sit in
both train and test. Figures are means over model seeds.

## Headline comparison

| Model | Balanced acc | Accuracy | macro-F1 | `no_spread` recall |
|---|---|---|---|---|
| Logistic regression, `class_weight="balanced"` | **0.7821** | 0.7797 | **0.6931** | **0.79** |
| Gradient boosting, balanced sample weights, depth 2 | 0.6434 | 0.7740 | 0.6245 | 0.45 |
| Gradient boosting, balanced sample weights, depth 3 | 0.5940 | 0.7721 | 0.5898 | 0.33 |
| Random forest, `class_weight="balanced"`, depth 4 | 0.5897 | 0.7853 | 0.5909 | 0.30 |
| Gradient boosting, current production config | 0.5398 | 0.8209 | 0.5420 | 0.18 |
| **Majority baseline (always `spread`)** | 0.5000 | **0.8418** | 0.4571 | 0.00 |

Two things follow immediately.

**Accuracy is the wrong headline.** The class balance is 84 % `spread`, so a model that always
answers `spread` scores 84.18 % — higher than every real model in the table. Any accuracy
figure quoted for this task has to be read against that baseline, not against 50 %.

**The production configuration is close to useless on correct labels.** Unweighted gradient
boosting reaches 0.5398 balanced accuracy, barely above the 0.5 floor, and recovers only 18 %
of extinction cases. It is nearly the majority-class predictor wearing a model's clothes. The
previous 83.45 % headline was accuracy on a corrupted oxygen column; the configuration itself
does not survive the correction.

## The result that matters: neither direction supports a safety claim

For a spacecraft fire-safety tool the expensive error is predicting `no_spread` for a condition
that actually spreads — a false assurance of safety.

| Model | False "safe" calls | `spread` recall | **`no_spread` precision** |
|---|---|---|---|
| Logistic balanced | 33 | 0.779 | **0.400** |
| GB weighted depth 2 | 24.7 | 0.834 | 0.339 |
| GB unweighted (production) | 7.0 | 0.953 | 0.344 |
| Majority (always `spread`) | 0 | 1.000 | 0.000 |

`no_spread` precision never exceeds **0.40**. When any of these models says a material will not
spread, it is wrong 60 to 66 % of the time. That is the one prediction the product exists to
make, and no configuration here makes it reliably.

The trade-off is also not escapable by tuning. Catching more extinctions means more false
assurances: logistic regression recovers 79 % of `no_spread` cases but issues 33 false "safe"
calls out of 149 true `spread` rows. Unweighted boosting cuts false assurances to 7 but then
detects almost no extinction at all.

## Why the ceiling exists

- **28 negatives.** The extinction cases are the informative ones, and most of BASS-II's
  extinctions occur at fan-pot settings below any velocity recorded in cm/s, so they are not
  recoverable as feature rows (see `docs/DATA_SOURCES.md` section 2c).
- **Irreducible label conflict.** Three feature-identical pairs carry opposite outcomes,
  because near the limit the result depends on whether a flame was already established before
  the flow changed. `oxygen_pct`, `pressure_kpa`, `flow_cm_s` and `material` cannot express
  that history.
- **Pressure is not identifiable.** All 158 BASS-II rows sit at 101.3 kPa; pressure varies only
  across the 21 Saffire rows.

## Recommendation

1. **Do not quote a classifier accuracy as evidence of predictive skill.** If a number is
   quoted, quote balanced accuracy against the 0.5 floor and the 0.8418 majority baseline
   together, plus `no_spread` precision.
2. **Lead with the parts that are sound.** The experimental-envelope guard and the
   nearest-real-experiment retrieval with resolvable NTRS citations do not depend on classifier
   skill, and the envelope guard is the honest answer to a question the data cannot settle.
3. **If a classifier ships, use the class-weighted linear model**, present it as a weak
   indicator rather than a decision aid, and show the confusion matrix beside it.
4. **The highest-value data work is more negatives**, not more model tuning. The Saffire rows
   already contributed 5; the remaining 229 unlabelled worksheet rows and the sources surveyed
   in `docs/DATA_SOURCES.md` are where a usable boundary would come from.

## Reproduce

Dataset: `data/processed/experiments_bass2_relabelled.csv`,
`data/processed/experiments_saffire_verified.csv`.
Scheme: `LeaveOneGroupOut` grouped by source test (BASS-II) or flight (Saffire), means over
seeds; logistic 1 seed (deterministic), boosting and forest 2 to 3 seeds.
