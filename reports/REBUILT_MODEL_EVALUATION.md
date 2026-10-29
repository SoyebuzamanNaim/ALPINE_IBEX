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

---

# Addendum 6: the R² 0.90 is real, and it does not apply to this tool

Addendum 4 offered flame spread rate as the honest number the classifier could not produce, at
R² = 0.9038. That figure holds up, but two checks made before putting it into the product show it
must not go there.

**It does not cover the operating range.** Three axes, all violated at once:

| | Olson fit | FLARE-X operates at |
|---|---|---|
| Oxygen | 21–100 % | **14.2–31 %** — 70 % of our rows sit below 21 % |
| Flow | quiescent, 0 cm/s | **1–25 cm/s** — not one of our rows is quiescent |
| Fuel | thin cellulose | mostly PMMA rods and fabrics |

Putting it in the tool would extrapolate on oxygen, flow and fuel simultaneously, which is the
exact failure the experimental-envelope guard exists to prevent. The guard would have to be
switched off to ship it.

**R² hides where the error is.** Spread rates run from 0.25 to 7.09 cm/s, so R² is dominated by
the high-oxygen points where the values are large:

| Form | R² | Mean relative error | **Relative error below 30 % O₂** |
|---|---|---|---|
| `(X_O2)^0.9 / τ` + intercept | **0.9038** | 31.2 % | **53.7 %** |
| same, through the origin | 0.8677 | 55.7 % | 118.0 % |
| free power law `0.033·X_O2^1.70·τ^-1.19` | 0.5052 | 28.6 % | **33.9 %** |
| `(X_O2)^0.9` fixed, log space | 0.7079 | 46.8 % | 76.0 % |

Near the flammability limit — the region a fire-safety tool exists for — the R² = 0.90 model is
wrong by about half. Its fitted intercept is also negative (−0.76 cm/s), which has no physical
meaning at the low end.

The free power law is the better model where it matters, and its oxygen exponent comes out at
**1.70 rather than the published 0.9**. That is not an error: the 0.9 correlation in NTRS
`20080034883` is for opposed flow, while Olson's tests are quiescent. Different regime, different
exponent.

## What was done

The model and its scope are saved in `models/spread_rate_meta.json` with
`applies_to_flare_x_operating_range: false` and the reason recorded. It is **not** wired into the
API or the site. R² = 0.9038 can be stated as a result for thin cellulose in quiescent
microgravity from 21 to 100 % oxygen, alongside the 54 % near-limit error, and not as a
capability of this tool.

---

# Addendum 7: the other 49 rows, checked against the documents

Forty-nine rows carried five NTRS identifiers other than BASS-II and Saffire. They were the
last untouched part of the dataset and the only remaining source of new negatives, so each was
checked against the document it named. The NTRS fulltext was pulled for all five, and where a
table existed the PDF page was rendered and read as an image rather than trusted to text
extraction.

## What the documents say

| Report | Claimed | What is in it |
|---|---|---|
| `20040053557` Bhattacharjee, *Extinction Criteria* | 11 rows at 16.2-21 % O₂, 0.3-25 cm/s | A four-page theory abstract (NASA/CP-2003-212376 pp. 201-204). The word "Table" does not occur. The only oxygen values anywhere are 21 %, 30 % and 50 %, all axis labels on figures derived from equations. No 18 %, no 17.5 %, no 16.2 %, no "quench", no "blowoff", no velocity in cm/s. |
| `19890014267` Ferkul, *Opposed flow... extinction* | 2 rows at 16.5 % and 15.8 % O₂, cited to "S. L. Olson, CR-182264" | A real TABLE I on p. 7 with **13 rows**. Neither 16.5 % nor 15.8 % appears in it. The author is Ferkul, not Olson. |
| `20080034883` Olson, Ruff & Miller, *Exploration Atmospheres* | 23 rows incl. 6 PMMA and 3 Nomex at 18-34 % O₂ | A real Table 1 with **6 microgravity limits** for three fuels. The fuels are Kimwipes, Ultem 1000, Nomex HT90-40 and Mylar G. **PMMA is not tested in this report at all.** Ultem and Mylar, which are, were absent from the dataset. |
| `20140011099` Ferkul et al., *BASS thickness & preheating* | 8 rows on a 1.2-cm slab and a 1.5-cm sphere | A 58-page slide deck with no table. Slabs and spheres are real subjects, but the stated conditions are not in it; one slide does give an exact condition. |
| `20160000593` Ferkul et al., *BASS-II results* | 5 rows on 6.35-mm Delrin rods | A 21-page programme overview. "Delrin" occurs zero times; "6.35" occurs zero times. It is also BASS-**II**, which the dataset labelled "BASS". |

Not one of the 49 could be supported. They share a signature: each report's rows form a clean
monotone ladder from `spread` through `marginal_spread` to `no_spread` as oxygen falls, with
smooth spread rates (1.85, 1.40, 0.85 / 2.45, 1.90, 1.35, 0.65) and burn durations. They are in
`src/ingestion/build_table.py` as hand-written literals, each with a page number and an exact
citation string that does not correspond to the document.

## The 21 rows that are really there

Transcribed from the rendered pages into `data/processed/experiments_reports_verified.csv`,
which carries the quote behind every value:

- **Ferkul TABLE I, 13 rows.** Thin cellulose laboratory wipes, half-thickness 0.0038 cm, 1 atm
  O₂/N₂, NASA Lewis Zero Gravity Facility, 5.18 s. The fuel is drawn through still oxidiser, so
  the tabulated fuel speed is the opposed relative velocity. 10 spread, **3 extinctions**: at
  14 % O₂ (6.08 and 4.19 cm/s) and, importantly, at 17 % O₂ and **0.81 cm/s** - a low-velocity
  quench, the branch BASS-II barely covers.
- **Olson Table 1, 6 microgravity rows**, each a 0g ULOI/0g MOC pair 1 % apart at 30 cm/s
  concurrent: Nomex HT90-40 23 %/22 % at 14.7 psia, Ultem 1000 24 %/23 % at 10.2 psia, Mylar G
  17 %/16 % at 10.2 psia. Three spread, three no_spread, two pressures, perfectly balanced. The
  six 1g columns are WSTF Test 1 data and are kept in the CSV but excluded from training.
- **Olson figure 2 caption, 1 row.** Kimwipes at 24 % O₂, 30 cm/s, 6.4 psia, "not near limit".
  The report never states Kimwipes' thickness, which is recorded as the reason it is excluded
  from modelling.
- **BASS slide 52, 1 row.** "Fuel: PMMA; 15-mm initial diameter; 17 % O₂/N₂; 1 atm... the flame
  goes out when the flow speed is zero." The only observation at **zero flow** anywhere in the
  dataset.

Two further BASS statements were left out for being ranges rather than values ("21 % to 22 %
O₂", "flow speeds around 15 cm/s"); recording those as exact numbers is the error being
corrected here.

That is 21 microgravity rows, 14 spread / **7 no_spread** - a far better balance than the
149/28 of the existing set - across three pressures (44.1, 70.3, 101.3 kPa) and flow from 0 to
30 cm/s.

## What they are worth

Scored by leave-one-group-out on the **original 177 rows only**, with the 21 new rows always in
the training fold so they are never tested on themselves:

| Model | New rows | Balanced acc | `no_spread` precision | Precision at threshold 0.80 |
|---|---|---|---|---|
| Gradient boosting d2 | excluded | 0.6372 | 0.562 | 0.692 (13 called safe) |
| Gradient boosting d2 | **included** | **0.6707** ±0.0089 | **0.677** ±0.010 | **0.818** (11 called safe) |
| Logistic, balanced | excluded | 0.7855 | 0.407 (22/54) | - |
| Logistic, balanced | **included** | **0.8090** | **0.468** (22/47) | - |

Both models improve, the gradient-boosting figures are stable over 10 seeds, and the direction
holds under both groupings tried. This is the first of ten attempts to move the number at all.

It is still not a safety claim. The counts are tiny and the intervals overlap:

| Claim | Count | 95 % Wilson CI |
|---|---|---|
| baseline precision | 9/16 = 0.562 | [0.332, 0.769] |
| augmented precision | 12/17 = 0.706 | [0.469, 0.867] |
| augmented at threshold 0.80 | 9/11 = 0.818 | **[0.523, 0.949]** |

An 0.818 resting on eleven predictions could as easily be 0.52. The honest reading is that 28
negatives became 35, the model got consistently but slightly better, and the data is still far
too thin to support "this material will not burn".

**A correction to Addendum 2.** It said pressure was constant at 101.3 kPa across the set. That
is true of BASS-II alone; the Saffire rows already spanned 54-73 kPa. The new rows widen that to
44.1 kPa, but pressure was never the missing axis it was described as.

## What this does to the shipped model

The 49 rows were not only in the evaluation track - they were 34 % of `cache/experiments.parquet`,
the file `src/compute/model.py` actually trains on. Removing them, changing nothing else:

```
n_train                145  ->  117
cv_accuracy         0.8345  ->  0.5470      majority baseline 0.5556
cv_balanced_acc     0.7622  ->  0.4093
```

**The advertised 83.45 % was a measurement of the fabricated rows.** Built as clean monotone
ladders, they were trivially separable, and they were a third of the training data. The same
pipeline, model and CV scheme on documented data scores below the majority baseline.

Two caveats pull in opposite directions and both matter. Only four report groups now remain, so
report-grouped CV trains on 21 rows whenever BASS-II is the held-out fold; that estimate is very
coarse and k fell from 5 to 4 for lack of groups. And this pipeline still ingests the superseded
96-row BASS-II extraction rather than the 158 PSI-verified rows, so its numbers are not the
honest track's numbers.

`tests/test_models.py::test_model_beats_majority_baseline` is now a strict `xfail` recording
that the requirement is not met, rather than a threshold quietly lowered until it passed.

## A coverage regression, and it is the real kind

The envelope guard is per material. PMMA's oxygen range was 15.5-20.8 % once the invented rows
went, so **the tool began refusing PMMA at 21 % oxygen - ordinary cabin air**, its single most
likely query. Reduced pressure for PMMA disappeared entirely; every sub-atmospheric PMMA row had
been invented. Thirteen tests failed because they encoded that coverage as real.

The fix is not to widen the guard. The PSI-verified BASS-II extraction genuinely covers PMMA
from 14.2 % to 22.2 % oxygen, so wiring it into the ingestion pipeline in place of the old
96-row block restores 21 % honestly. That swap needs `flow_direction` established per PI table
from the source, which is a separate piece of work and is not done here. Until it is, the
in-domain tests use 19 % PMMA and say in a comment why.

---

# Addendum 8: one dataset instead of two

Addendum 7 left the repository with two BASS-II datasets that disagreed. The ingestion pipeline
still used a 96-row block hardcoded from the report's appendix, while the evaluation track used
the 158 PSI-verified rows. The pipeline's oxygen column disagreed with NASA PSI on 77 of 81
comparable tests and stopped at 20.8 % for PMMA, which is why the envelope guard began refusing
PMMA at 21 % oxygen once the fabricated rows were removed. Having two datasets is what let that
go unnoticed, so this closes the gap.

## Flow direction, the one thing that blocked the swap

PSI-25 publishes the calibrated conditions but not the flow direction; the NTRS appendix tables
do, per test, in a column the PSI export drops. Reading it needed coordinates rather than plain
text, because the appendix tables are rotated. Counting the tokens per table:

| Table | PI | Opposed | Concurrent |
|---|---|---|---|
| A.1 | Bhattacharjee | 22 | 0 |
| A.2 | Ferkul | 0 | 3 |
| A.3 | Fernandez-Pello | 25 | **2** |
| A.4 | Miller | 20 | 0 |
| A.5 | Olson | 0 | 10 |
| A.6 | T'ien | 0 | 23 |

Five tables are uniform. Table A.3 has two exceptions, tests **P16 and P19**, both confirmed by
rendering that block of page 114 and reading it: P14, P15, P17 and P18 are opposed while P16 and
P19 are concurrent. The field used to default to `"opposed"` for every row that did not set it;
it is now `Optional` with no default, so a row whose source is silent records nothing rather
than a quiet assumption.

Table A.4 is Miller's, 52 rows. The old hardcoded block covered A.1, A.2, A.3, A.5 and A.6 and
left Miller out entirely.

## The Saffire rows, too

The evaluation track also carried 21 hand-transcribed Saffire rows that the pipeline never
ingested. They are in now, which is what makes the two tracks the same data. They are the only
rows at reduced cabin pressure, 54-73 kPa. Their geometry is read from the sample description
each row already carries - "cloth" and "jersey" are fabric, "sheet" is sheet, cast PMMA plates
are slabs - rather than assigned.

## Where the dataset stands

200 rows from **7 reports**, up from 4, which matters because report-grouped CV had been
reduced to four folds:

```
BASS-II        20210011385  158    Cotton-Fiberglass, Nomex, PMMA
Ferkul         19890014267   13    Cellulose
Saffire-I      20170008805   12    Cotton-Fiberglass, Nomex, PMMA, Silicone
Expl. Atmos.   20080034883    7    Cellulose, Mylar, Nomex, Ultem
Saffire-III    20210011521    6    Cotton, Cotton-Fiberglass, PMMA
Saffire-VI     20240002981    3    Cotton-Fiberglass, PMMA
BASS           20140011099    1    PMMA
```

163 spread, 35 no_spread, 2 marginal_spread. Oxygen 14.0-24.0 %, pressure 44.1-101.3 kPa, flow
0-45 cm/s. **Every row now carries `HAND_TRANSCRIBED_FROM_SOURCE`** - there is no longer a single
row in the dataset that cannot be traced to a rendered table or an exact statement.

PMMA's envelope is 14.2-22.2 % oxygen again, so **21 % oxygen on PMMA is back in range**, which
was the regression Addendum 7 recorded and could not fix.

## What it does to the headline

```
n_train                       117  ->  200
cv_accuracy                0.5470  ->  0.7600      majority baseline 0.8150
cv_balanced_accuracy       0.4093  ->  0.3557
report groups                   4  ->  7
```

The accuracy rises and the balanced accuracy falls, and both are explained by the same thing:
the set is now 163/35 rather than 65/41, so always answering `spread` scores 0.8150 and the
gradient-boosting configuration still does not beat it.
`test_models.py::test_model_beats_majority_baseline` stays a strict `xfail`. Nothing here
contradicts the ceiling: the binary leave-one-group-out numbers in Addendum 7 remain the ones
worth quoting, because accuracy on a set this imbalanced is not a measure of skill.

One property of the merged set is worth stating plainly. **Four groups of rows share identical
material, oxygen, pressure and flow and carry opposite outcomes.** No model with these four
features can be right about all of them; near the limit the result depends on whether a flame
was established before the flow changed, which the features do not express. That is a floor on
the achievable error, and it is in the data, not the model.
