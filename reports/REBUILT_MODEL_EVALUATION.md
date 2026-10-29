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
- **Ignition is a separate model**, and the current feature set
  (`oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`) omits what governs it: igniter energy,
  duration, and sample preheat. **Correction, 2026-10-29:** an earlier version of this line said
  those are recorded in the PSI table. They are not — see Addendum 3.
- **The envelope guard remains the honest core.** It answers "is this condition inside anything
  NASA has measured?" — a question the data can settle, unlike "is it safe?".

---

# Addendum 2: everything tried to raise accuracy, and what each did

Run on 2026-10-29 on the corrected data (177 rows, 149 `spread` / 28 `no_spread`, 82 groups,
leave-one-test-out, class-weighted logistic unless stated). Baseline to beat: **0.7821 balanced
accuracy**, `no_spread` precision 0.400.

| Attempt | Balanced acc | Verdict |
|---|---|---|
| Baseline — `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material` | **0.7821** | — |
| + regime flag `U/U_D` (U_D = 2 cm/s) | 0.7821 | **no change at all** |
| Stretch rate `log a` in place of raw flow (rods) | 0.5800 vs 0.5900 baseline | slightly worse |
| + Damköhler group `X_O2·P/a` (rods) | 0.5700 | worse |
| Margin to NASA's published boundary (rods) | 0.7700 vs 0.5900 | better, but see below |
| Split: extinction only, ignition failures dropped | 0.5714 | **much worse** |
| Split: ignition failures only | 0.7598 | about the same as pooled |
| Split: quench branch only | 0.5419 | worst |

Nothing raised the headline. Three of these are worth stating plainly.

**The physics reparameterisation did not help.** Replacing velocity with the stretch rate
`a = (3/2)(U/r)(r/r_o)^½` is what the literature says the boundary is a function of, and it made
the model slightly worse. The reason is visible in the data: BASS-II flew only three rod
diameters, and within each one `log a` is a monotone transform of flow, so it carries almost no
information the model did not already have. The reparameterisation matters when comparing
across geometries; it earns nothing inside one.

**Separating the failure modes made things worse, not better.** This was the opposite of the
expectation. Dropping the 17 ignition failures and keeping only the 11 true extinction events
sends `no_spread` precision from 0.400 to **0.091**. Read the other way: the model's apparent
skill comes almost entirely from the ignition failures, which sit at low oxygen (14.2 to 16.4 %)
and are separable by oxygen alone. **The flammability boundary itself — the quench and blowoff
branches, the scientifically interesting part — is not learnable from these four features with
11 examples.**

**The margin feature is the one thing that helped, and it is partly circular.** Feeding the model
its distance from Eq (6.1) lifts rod balanced accuracy from 0.59 to 0.77. But Eq (6.1) was fitted
by NASA to BASS-II rod extinction data, so on BASS-II rods the feature partly encodes the answer.
It also rests on 5 negatives, and its `no_spread` precision is still only 0.235. It is a good way
to *present* the physics, as the tool already does, and not evidence of a better classifier.

## The threshold sweep: there is no usable operating point

A safety tool does not need a label, it needs to know when it may say "safe". Sweeping the
decision threshold on P(`no_spread`):

| Threshold | Declares "will not spread" | Coverage | Precision | False-safe calls |
|---|---|---|---|---|
| 0.50 | 55 | 31.1 % | 40.0 % | 33 |
| 0.70 | 22 | 12.4 % | 36.4 % | 14 |
| 0.80 | 10 | 5.6 % | 50.0 % | 5 |
| 0.85 | 4 | 2.3 % | 50.0 % | 2 |
| 0.90 | 1 | 0.6 % | 0.0 % | 1 |
| ≥ 0.93 | 0 | 0 % | — | 0 |

**No threshold reaches 80 % precision.** Past 0.93 the model never declares anything safe at all.
There is no operating point at which "this will not spread" is trustworthy, so abstention is not
a design preference here — it is the only honest output.

## Conclusion

The headline stays at **0.7821 balanced accuracy**, and it is not improvable with this data. The
remaining levers are data, not modelling: more extinction observations at known cm/s velocities,
and the ignition-governing inputs (igniter power, duration, preheat) that are recorded in the PSI
table but are not yet features.


---

# Addendum 3: the igniter lever does not exist

Addendum 2 closed by naming the ignition-governing inputs as the most promising remaining data
work, on the understanding that the PSI table recorded them. It does not.

| Source | Igniter power or duration? |
|---|---|
| `PSI-25_Experimental_table_BASS-II.csv` | no — 16 columns, none igniter-related |
| `PSI-25_BASS-II_Test_Matrices.xlsx` | no — the same 16 columns |
| `PSI-26_Experimental_table_BASS.csv` | no — 6 columns |
| BASS-II observation text | 8 of 158 rows mention a number near "ignit", mostly false matches |

**No BASS-II row has igniter data.** The `Radiometer gain` column named earlier is a camera
setting, not igniter power.

Igniter data does exist for Saffire, in NTRS `20170008805` Table I, and has been added to
`experiments_saffire_verified.csv` as `ignition_power_w`, `ignition_time_s` and
`ignition_source` — 12 of 21 rows, the Saffire I and II samples.

It settles the question rather than opening it:

| Igniter setting | Outcomes |
|---|---|
| **80 W / 9.2 s** | **5 `no_spread`, 3 `spread`** |
| 97 W / 30 s | 2 `marginal_spread` |
| 182 W / 8 s | 2 `spread` |

At 80 W for 9.2 s the same igniter produced both outcomes: the four silicone samples recorded
"Insignificant" burn with ~0 burn length, while the two cotton-fiberglass samples burned their
full 29 cm. Within that flight the igniter was held constant and the outcome was set by the
material. Igniter energy carries no discriminative information here, and it is present on 12 of
177 rows, so no model fit was run — the table above is the result.

The honest position is that **the ignition sub-problem cannot be attacked with the available
data at all.** 17 of 28 negatives are ignition failures, and nothing in the record describes the
ignition conditions that produced them for BASS-II. That is a limit of what NASA published, not
of the modelling.

---

# Addendum 4: the Olson thesis — no negatives, but a target that does work

Addendum 2 named more extinction data as the only remaining lever, and NTRS `19880006471`
(NASA TM-100195, Olson, *The Effect of Microgravity on Flame Spread Over a Thin Fuel*) was the
best candidate: microgravity, and its abstract promises oxygen "from the limiting oxygen
concentration to 100 percent".

**It does not supply negatives.** Appendix A has four tables and every row in all four carries a
non-zero flame spread rate — each is a test in which the flame spread. The abstract line is the
reason: the tables *start at* the limiting oxygen concentration, so the lowest row of each is the
last condition that still burned, not a failure. Adding these rows would take the balance from
149/28 to roughly 193/28 and make the classification problem worse.

The OCR text layer is also unusable for this report — `OA9` for `0.49`, `a. 55` for `0.55`, and
the column structure flattened to one value per line with no row identifier to anchor on. The
rows below were read from the PDF pages rendered at 3× with PyMuPDF, the same way the Saffire
tables were read.

## What it is good for

Flame spread **rate** is a continuous target with no class imbalance, and on this data it is
strongly predictable. 44 individual microgravity measurements, Tables A-I and A-III, oxygen 21 to
100 %, two fuel thicknesses, quiescent, 1 atm. Leave-one-out:

| Model | R² | MAE (cm/s) |
|---|---|---|
| Linear in O₂ and thickness | 0.8640 | 0.441 |
| Quadratic | 0.9079 | 0.328 |
| Cubic | **0.9404** | 0.265 |
| **Literature form, (O₂)^0.9 / thickness** | **0.9038** | 0.421 |

The last line is the one worth quoting. `(O₂)^0.9` is the published correlation exponent reported
in NTRS `20080034883`, and dividing by fuel thickness is the thermally-thin scaling. A **single
physically-derived feature reaches R² = 0.90** on held-out measurements. The cubic edges it out
at 0.9404 but spends ten polynomial terms on 44 points to do so; the literature form is the more
defensible number and cannot overfit.

Saved as `data/processed/experiments_olson_spread_rate.csv`, kept separate from the
classification table because every row is a positive.

## What this means for the headline

Classification accuracy is still 0.7821 balanced and still not improvable — this source cannot
move it. But "how fast will it spread, given oxygen and thickness" is a question the published
data answers well, and **R² = 0.90 from NASA's own correlation form** is an honest, checkable
number of the kind the classifier cannot produce.

---

# Addendum 5: 1-g thresholds — the transfer makes microgravity worse

The last untried lever was the 1-g flammability-threshold literature. It is attractive because a
(ULOI, MOC) pair is a *bracketing* measurement: at MOC the sample did not burn, at ULOI it did.
Every pair therefore yields one labelled row on each side of the boundary, which is the most
informative kind of observation, and the 1-g literature has many of them.

29 pairs were read from NTRS `20110008636` (Hirsch et al.), Tables 2, 3, 5 and 6, from the
rendered PDF pages, giving **58 rows at a perfect 29/29 balance** — saved as
`data/processed/experiments_1g_thresholds.csv`. Two materials overlap with the microgravity set:
PMMA (extruded ¼-inch rod, the same geometry we have) and silicone (MQ).

Codex had warned that 1-g and 0-g data are not exchangeable. The test was built so that warning
could be checked rather than argued: the 1-g rows go into training only, and **scoring is always
on held-out microgravity groups**, so no gain can come from the 1-g rows being easy.

| Training set | Balanced acc | Accuracy | `no_spread` recall | `no_spread` precision |
|---|---|---|---|---|
| Microgravity only | **0.7821** | 0.7797 | 0.786 | 0.400 |
| + 58 1-g rows | 0.6774 | 0.8475 | 0.429 | **0.522** |
| + 58 1-g rows, with a gravity flag | 0.5356 | 0.7797 | 0.179 | 0.238 |

**Adding 1-g data makes microgravity prediction worse**, by 0.10 balanced accuracy, and adding a
gravity indicator makes it much worse, by 0.25. The reason is visible in the numbers themselves:
the 1-g boundary for extruded PMMA rod sits at 18–19 % O₂, while NASA's microgravity boundary for
cast PMMA rod sits at 13.4 %. The model learns the 1-g threshold and misapplies it, calling
conditions non-flammable that microgravity data shows burning. With only two gravity levels and
two shared materials there is not enough overlap to identify the offset, so the flag makes the
model worse rather than letting it separate the regimes.

One honest nuance: without the flag, `no_spread` **precision rose to 0.522**, the highest figure
seen anywhere in this work, while recall fell to 0.429. The model became more reluctant to
declare anything safe, and was right more often when it did. That is a different operating point
rather than a better model, and it is still too unreliable to carry a safety claim.

The rows are kept because they are correctly transcribed and cited, and because the comparison
above is worth being able to re-run. They are **not** merged into the training table.
