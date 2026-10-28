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

---

# Addendum: why the ceiling exists — `no_spread` is three phenomena, not one

Added after testing NASA's own published flammability boundary against the rebuilt rows.

## The published boundary

NTRS `20210011385` (BASS-II Summary Report) gives the boundary in closed form, Eq (6.1),
fitted to cast-PMMA rods over 13.6–22.2 % O2 and normalised to a base rod radius
`r_o = 0.318 cm` (the 1/4-inch rod):

```
X_O2 = 6*exp(-0.5*a) + 0.0167*a + 13.4          [vol %,  a in 1/s]
       |__ quenching __|  |blowoff|  |_ LOC _|

a = (3/2)*(U/r)*(r/r_o)**0.5                     size-normalised stretch rate
U/U_D = 1,  U_D = 2 cm/s                         quench / blowoff regime separator
```

Reproducing its stated minimum is a useful check: the equation bottoms out at
**13.61 % O2 for a = 8–12 1/s**, and the paper says *"The minimum in this boundary occurs at
a = 8 to 12 s–1 at approximately 13.5 percent O2."* The implementation is correct.

## Testing it against our 55 verified PMMA-rod rows

With **zero fitted parameters**, the published boundary agrees with our independently
transcribed outcomes on 50 of 55 rows — 90.9 %. That number is worthless:

```
true spread    -> pred spread  50 | pred no_spread   0
true no_spread -> pred spread   5 | pred no_spread   0
```

It predicts `spread` for every row. 90.9 % is exactly the base rate (50 of 55 rod rows are
`spread`), and the boundary catches **none** of the five negatives. This is the same trap as the
84.18 % majority baseline, one layer deeper.

## Why it misses — and this is the real finding

Reading the five negatives' own observations shows they are not boundary events at all:

| Row | O2 | Observation |
|---|---|---|
| `BASS2_O5b_5` | 14.2 | "Would not sustain a flame without igniter on" |
| `BASS2_P8_5/10/15` | 16.4 | "would not stay lit" |
| `BASS2_O3a_3` | 18.0 | "extinguished as soon as he turned flow down, probably overshot" |

Eq (6.1) describes **extinction of an established flame**. Four of those five never established
one. Classifying all 28 negatives by failure mode, read from each row's own observation text:

| Failure mode | Count | Share |
|---|---|---|
| **`ignition_failure`** — flame never established or never propagated | **17** | **61 %** |
| `quench_extinction` — established flame died as flow was reduced | 8 | 29 % |
| `blowoff_extinction` — established flame died as flow was raised | 3 | 11 % |

Only **11 of 28 (39 %)** are extinction-boundary events, and those split across two
**opposite** branches: 8 quench, 3 blowoff.

The mode is recorded per row in `failure_mode` with its evidence in
`failure_mode_evidence`, in both `experiments_bass2_relabelled.csv` and
`experiments_saffire_verified.csv`.

## What this means

`no_spread` is not a class. It pools at least three physical questions:

1. **Will it ignite at all?** — 61 % of the negative evidence. A materials-screening question.
2. **Once lit, will it survive reduced flow?** — the quenching branch, 8 rows.
3. **Once lit, will it survive increased flow?** — the blowoff branch, 3 rows.

A single classifier asked to separate `spread` from this mixture is being asked to learn three
different boundaries, in opposite directions in flow, from 28 examples. The 0.40 precision is
an average over one tractable sub-problem and two that are starved.

This supersedes the earlier framing in this report. The ceiling is not mainly "only 28
negatives" — it is that the 28 are not measurements of the same thing.

## Consequences for the product

- **Do not pool the modes.** Report them separately even if a model is only built for one.
- **Eq (6.1) is directly usable and citable** for the extinction question on PMMA rods, with no
  training and no accuracy claim. Report the user's **O2 margin above the boundary**, which is
  the operator-relevant quantity, rather than a class label.
- **Ignition is a separate model** and the current feature set
  (`oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`) omits what governs it: igniter energy,
  duration, and sample preheat. Those are recorded in the PSI table (`Radiometer gain`,
  ignition power and time in the Saffire tables) and are not yet features.
- **The envelope guard remains the honest core.** It answers "is this condition inside anything
  NASA has measured?" — a question the data can settle, unlike "is it safe?".
