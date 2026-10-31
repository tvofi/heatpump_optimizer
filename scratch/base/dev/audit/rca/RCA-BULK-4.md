# RCA-BULK-4: N-name-sort — entity families split by the name sort

Root-cause seat per `root-cause.md`, at `origin/main` `3490cb16`. Not posted. Helpers in `phaseC/bulk4/`: `name_sort_families.py` (enumerator) and `family_check.py` (prototype check), with outputs `history.out`, `main.out`, `null.out`, `demo.out` and `null_check.out`. The shared register cause is RCA-1736 §2 and RCA-BULK-2 §3, cited here and not repeated.

## 1. Instances: 8, not 6

| round | finding | issue | family definition the finder used | span (created→closed) | fixed at (first tag) |
|---|---|---|---|---|---|
| R1 | D8-03 | #174 | DHW semantic (`dhw_`/`hot_water_`/`mixed_`) | 2.96 h | `c2aa8af3` v6.2.17 |
| R2 | D8-04 | — | "ten hand-listed families" | no issue | partial by #205 |
| R3 | D8-03 | #797 | finder `FAMILIES` + trailing noun | 10.62 h | `a95556d3` v6.4.2 (Title Case only) |
| R4 | D8-01 | #945 | seven brief families, en spans | 34.70 h | `ad7bcdf` v6.4.4 (option E) |
| R5@`eaa2a06` | D8-02 | #1227 | name-prefix families vs key | 6.25 h | #1253 `cc4afbc7` v6.6.5 |
| R5@`1cc89e0` | D8-01 | #1333 | card-parsed plan family | 19.01 h | `9af8a477` v6.6.9 |
| R5@`1cc89e0` | D8-02 | #1334 | key prefixes + tariff pair, sv | 19.01 h | `9af8a477` v6.6.9 |
| R9 | D8-s3-01 | #1668 | production classes (accuracy, `_AccumulatingSensor`) | 42.00 h | `37fe3f63` (#1733) v6.7.10 |

- Register v2 is missing **#174** and **#1227**; its R5 rows come from the `1cc89e0` run only.
- If both R5 baselines are one round, round 5 had **3 instances**, which by the letter is the barrier trigger. That trigger was never applied to history (BULK-2 §3.1(6)); whether the two runs are one round is the owner's call.

## 2. Named cause

**Family membership is declared nowhere in production.** An entity's grouping exists only implicitly, and in two places that nobody keeps in step:

- the `translation_key` lead token, from which the id is built: `entity_id = <platform>.heat_pump_optimizer_<key>`, at `sensor.py:304`, `binary_sensor.py:82` and `button.py:77`;
- the display-name lead token in `translations/{en,sv}.json`. Since `ca711b56` (v5.0.0, 08-27) `_attr_has_entity_name = True` and the name comes from `translation_key` (`entity.py:100`).

So every round's finder invents a family list, and every fix pins exactly that list. `tests/entities.py` now holds six such blocks:

| block | family definition | sort key |
|---|---|---|
| L9051 #174 | DHW keys | — |
| L10251 #945 | English-prefix table `_CLUSTER_PREFIXES` | — |
| L10321 #1668 | `isinstance` classes | `casefold` |
| L10513 #1227 | literal id list | — |
| L10564 #1333 | card suffixes | — |
| L10649 #1334 | four hand-listed key prefixes plus two hand pairs | raw `sorted()`, codepoint, which puts `ä` before `å` |

No block measures any other block's families. Two measured consequences, from `git log`:

1. **Fixes split other definitions.**
   - #945 renamed names but not keys. Key-family splits in en went **1→6** (`history.out`, `ad7bcdf^1`→`ad7bcdf`), and that became #1227.
   - #1733 renamed `cost_total_heating` to "Lifetime Total Heating Cost". That split the `cost` key family (en **1→2**, sv **2→3**), and in the same PR the test table was edited to `"cost_total_heating": "Lifetime "` (`d39f764d`), so the check was changed to match the split.
2. **Splits outside every list stay unseen.**
   - `away` ("Away", "Away Mode", "Expected Return"; sv "Borta", "Bortaläge", "Förväntad hemkomst") has been split since `e4bc3756`, which is **36 releases**.
   - `compressor`-sv ("Kompressorstarter" / "Rådgivare för kompressorfrekvens") has been split since v5.0.0, which is **105 releases**.
   - No finder listed either family, and the D8 brief's step 3 names "DHW, tariff, learning, accuracy, ECL110, PV, card headline".

#1668's barrier section names the gap: *"a design decision on the canonical lead token per family."*

## 3. Process state

| level | state | evidence |
|---|---|---|
| each split landing | **(a)** | Nothing declares or checks a family when an entity is added or renamed. Option E (09-14) decided four listed families; it is not a rule. |
| fix and pinning (R4 onward) | **(c)** | `D8.md` step 3 (count splits for the seven listed families) and step 5 ("the matrix graduates… a `tests/` script") were obeyed: every fix graduated its finder's families. The result was six disjoint pins, two fix-induced splits (#945→#1227, #1733→`cost`) and two families never measured. A firmer instruction would not help. |
| class recognition | **(c)** | RCA-1736 §2 and BULK-2 §3, plus two unregistered instances (§1). Also: R4 pinned "accuracy stays split BY DESIGN" (`entities.py:10255`). R9 re-found accuracy as a two-member family, leaving out `optimization_score`, which made it a defect without contradicting the pin. |

## 4. Live at main: the enumerator

- **Family definition (KEY).** A family is the first underscore token of the `translation_key`, across platforms, with at least 2 members. This gives 13 families: `away 3`, `compressor 2`, `cost 7`, `dhw 9`, `ecl110 2`, `heat 2`, `learning 5`, `optimization 4`, `plan 7`, `solar 3`, `space 2`, `thermal 2`, `wood 2`.
- **Why the key.** It is the only in-code grouping: the entity_id is built from it, and #1227/#1333 renamed keys so that families share it. It is derived, not hand-listed.
- **Sort.** The whole 75-name roster (the registry's name view), en with `casefold`, sv with Swedish å<ä<ö after z.

```
3490cb16  key_families_split_en=2  (away, cost)
          key_families_split_sv=3  (away, compressor, cost)
          trail_families_split_en=13 / sv=15   (#797's partition, reference; owner declined it)
null  (names := keys)                        key_split en=0 sv=0
perturb "Learning Observed COP"=>"Observed COP"   en 2→3 (learning splits)
perturb "Expected Return"=>"Away Expected Return" en 2→1 (away heals)
```

Across the baselines (`history.out`), key splits en/sv were:

| SHA | en/sv |
|---|---|
| v5.0.0 | 0/4 |
| R2 | 0/6 |
| R3 | 1/6 |
| `ad7bcdf` | **6/10** |
| `cc4afbc7` | 2/6 |
| `9af8a477` | 1/2 |
| `37fe3f63` | **2/3** |

The class is **live**: 2 families split in en and 3 in sv at main, and one of them was created by the R9 fix itself.

## 5. Cost test

- **Rate.** 6 registered instances between 09-02 and 09-26 is **7.2 a month**; counting all 8 it is **9.6 a month**. 6 of 9 rounds had one (0.67 per round). A round runs every ~2.8 d (BULK-2 §3.3).
- **Per-instance cost.**
  - Issue span: median **19.0 h**, mean 19.2 h, total 134.6 h over 7 issues.
  - Each instance also used finder, verifier, judge, fixer and reviewer seats (wall-clock not measured).
  - Severity was low throughout, except #174 (medium).
- **Releases escaped.** Counted from v5.0.0 to the fix:

  | instance | releases |
  |---|---|
  | #174 | 51 |
  | #797 | 76 |
  | #945 | 78 |
  | #1227 | 86 |
  | #1333/#1334 | 90 |
  | #1668 | 104 |

  Still open: `away` 36, `compressor`-sv 105, `cost` 1.
- **Standing cost of the countermeasure.** `family_check.py` takes **4.9 ms** in-process and 0.043 s as its own process. It would run inside `tests/entities.py`, which already runs in the gate.
- **Verdict.** 0.005 s per run is less than 19 h × 0.67 per round by about seven orders of magnitude. **Build it.**

## 6. Countermeasure and demonstration

It addresses the (a) state at landing and the (c) state at fixing: one declaration and one check, in place of per-finder pins.

1. **Declaration (production).** The family is the key's lead token, plus an explicit `ENTITY_FAMILY_OVERRIDES` table in `const.py`. That table has 5 entries today: `diagnose_last_interval→prediction` and four meters `→lifetime`. Moving an entity between families becomes a visible edit to one table.
2. **Check (`tests/entities.py`).**
   - Every declared family with at least 2 members forms **one contiguous run** in the en and sv name sorts, using one collation.
   - Anchors: the roster has at least 60 names and there are at least 10 families.
   - The check replaces the contiguity parts of the six blocks. The line delta was estimated, not measured.
3. **Owner decision** on `away` and `compressor`-sv: rename, or record them on an ALLOW list.
4. **`D8.md` step 3 (policy).** "Families are the declared ones. An undeclared grouping is reported as a proposed declaration change, not a split."

Demonstration (`demo.out`). All runs use ALLOW = {away, compressor}, the two live splits nobody reported.

| instance | pre-fix | post-fix |
|---|---|---|
| #1334 | `9af8a477^1` **FAIL** rc=1 (sv `solar`, `dhw`, `space`; `boost` in en and sv) | `9af8a477` **PASS** rc=0 |
| #1668 (5 overrides declared) | `37fe3f63^1` **FAIL** rc=1 (en/sv `prediction`: "Diagnose Last Interval" / "Prediction Accuracy"; `lifetime` 3 runs) | `37fe3f63` **PASS** rc=0 |
| #1733 regression (the name moved, the declaration did not) | — | `37fe3f63` **FAIL** rc=1 on `cost`, en and sv |

Controls:
- **Null:** every name led by its declared family gives PASS rc=0.
- **Anti-skip:** an empty roster gives FAIL rc=1 on the ANCHOR check.
- **Main with nothing allowed:** FAIL on `away` (en/sv) and `compressor` (sv).

**Reach.** Keys alone catch #1334, the sv part of R2-D8-04, #945's key drift (which folds #1227 into #945) and #1733's regression. #174, #945-en, #1333 and #1668 need a declaration first; with the table, each becomes a one-line decision rather than a round-long finding. #797's partition stays refused by the owner.

## 7. Placement

- **New F7.4** (entity lane, after F7.1/F7.2, which touch `sensor.py` and `tests/entities.py`): the `const.py` overrides and the generic check. Neither file is code-owned.
- **Into F11.5:** the `D8.md` step-3 line, which is policy and needs owner approval.
- **Owner:** the decision on `away` and `compressor`, and whether R5's three instances trip the barrier.
- **Register:** add #174 and #1227 to N-name-sort.

## 8. Not measured

- Seat wall-clock per instance.
- HA's real `Intl.Collator` (approximated here).
- The device-page view, which sorts within entity categories.
- The net line delta of the replacement check.
