**Source:** the class RCA for N-name-sort in [RCA-BULK-4.md](https://github.com/tvofi/heatpump_optimizer/blob/handoff/audit-r9-alt/handoff/round9/state/alt/rca/RCA-BULK-4.md). It was conducted 2026-09-28 because register v2 found the class had recurred in 6 of 9 rounds with no RCA. Measured at origin/main `3490cb16`. The enumerator, prototype check and outputs are in `rca/bulk4/` on `handoff/audit-r9-alt`.

## What

Entity families split apart in the alphabetical name sort. That is 8 instances: #174, R2 D8-04, #797, #945, #1227, #1333, #1334 and #1668. The cause is that **family membership is declared nowhere in production.** Two implicit groupings drift apart:
- the `translation_key` lead token, from which the entity_id is built;
- the display-name lead token in `translations/{en,sv}.json`.

Each finder invented its own family list, and each fix pinned exactly that list. `tests/entities.py` holds six such blocks with five family definitions and two sort keys, and none measures another's families. Two consequences, measured:
- **Fixes split other families.** #945 took key-family splits in English from 1 to 6, which became #1227. #1733 split the `cost` family (en 1→2, sv 2→3) and edited the test table to accept it.
- **Families nobody listed stay split.** `away` has been split for 36 releases, and `compressor` in Swedish for 105.

**Live at main** (families by key lead token, 13 of them):

| arm | en split | sv split |
|---|---|---|
| main | 2 (`away`, `cost`) | 3 (`away`, `compressor`, `cost`) |
| null (names := keys) | 0 | 0 |
| perturb "Learning Observed COP" → "Observed COP" | 3 | — |
| perturb "Expected Return" → "Away Expected Return" | 1 | — |

**Process state:**
- (a) at each landing: nothing declares or checks a family.
- (c) at fixing: `D8.md` step 3 and step 5 were obeyed and produced disjoint pins.
- (c) for recognition: see RCA-1736 §2.

**Cost:**
- 7.2 instances per month registered (9.6 with all 8).
- Median issue span 19.0 h.
- 51 to 104 releases carried each instance.
- The check costs 4.9 ms per run inside the existing gate.

## Fix shape (R9-F7.4)

- **Declaration** in `const.py`: a family is the key's lead token plus an explicit override table (5 entries today).
- **One generic check** in `tests/entities.py`: every declared family of 2 or more forms one contiguous run in the English and Swedish name sorts under one collation, with anchors so an empty roster fails. It replaces the contiguity parts of the six blocks.
- **Demonstration** (`demo.out`):
  - #1334 fails at `9af8a477^1` and passes at `9af8a477`.
  - #1668, with its overrides declared, fails at `37fe3f63^1` and passes at `37fe3f63`.
  - #1733's own `cost` split fails at `37fe3f63`.
  - The null passes, and the empty roster fails its anchor.

## For tvofi

1. Rename, or explicitly allow, the `away` and Swedish `compressor` splits.
2. Round 5 ran twice, at baselines `eaa2a06` and `1cc89e0`. If the two runs count as one round, round 5 had 3 instances, which by the letter of the rule is the barrier trigger.
3. The `D8.md` step-3 wording ("families are the declared ones") is policy. It rides R9-EG-R1's policy asks.

## Disposition

Scheduled: **R9-F7.4**, after R9-F7.2 (`sensor.py` and `tests/entities.py`).
