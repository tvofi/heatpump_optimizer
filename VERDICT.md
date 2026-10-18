Fix review: blocked 3aba8f1eb2865de9d00edb9321185f387e4322f2 vacuous-test: zeroing the coordinator feed's sun regressor fails no check in tests/features.py, but it moves the finder's harness P1 fix2.00 from 0.006/0.009/0.013 to 0.095/0.106/0.114

bus-nonce: 76ef1cf5d26ce5c51a587237b32316a2

Round 1. The PR has no earlier `Fix review:` comment (PR and issue comments both empty).
Head measured: 3aba8f1eb2865de9d00edb9321185f387e4322f2 (`ev/HEAD`). At write time it is still the head of `fix/r10-vent-detector-pr`.
Base: the merge base c8cc75ea90a3bb38dbc6b8dbb7d27d9cce74cdd0. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so this reviewer's contract is current.

## Blocking 1 -- vacuous test (step 1)

The body says the coordinator's feed passes "sun (`solar_radiation * dt_h / 1000`)" because "an aperture error [leaves a residual] that scales with the sun". It also says the `R10-P5` census covers the sun-scaled bias. But the census calls `det.update(..., (_x, _q))` with its own regressors (`tests/features.py` ~58862). It never goes through `_async_learn_house_heat_loss`, so no check reads the feed's sun argument.

- M10, sun regressor zeroed at the feed (`(previous_state.solar_radiation or 0.0) * dt_h / 1000.0` -> `0.0`, coordinator.py:5107), full `tests/features.py` on a git archive of the head: `1 of 4188 FEATURE CHECKS FAILED`. That one failure is the #363 runner artifact, the same one the clean archive shows (`ev/mutants/M10.txt`, `clean.txt`). The mutant **survives**.
- The finder's harness shows the line matters. `ident_rolling.py --plant P1` on the M10 tree:

  | arm | head | M10 |
  |---|---|---|
  | fix2.00, g0.4 / 0.6 / 1.0 | 0.006 / 0.009 / 0.013 | 0.095 / 0.106 / 0.114 |
  | fix1.50, g1.0 | 0.000 | 0.004 |

  Files: `ev/mutants/M10_ident_P1_g*.txt`. So production behaviour the body credits to this line has no test that pins it.
- Contrast: M11 (heat regressor zeroed at the feed) is killed by `the fourth trips the detector through the real learner`, `a tripped detector freezes every learner with reason ventilation` and `while frozen, cold residuals feed the detector but never the model`.

Owed: a check that drives the sun term through the real feed. For example, a sun-scaled bias fed through `_async_learn_house_heat_loss` on a live coordinator that must not trip. It must kill M10, and should also bind the `/1000` scale and the `or 0.0` fallback.

## Blocking 2 -- architect note (step 15), stated for the next round

The roster's R10-VENT-DETECTOR architect note (handoff/audit-r10-roster @ 9a487b732) says "Shape: a detector input independent of the replay residual". It is binding under fixer.md 17. The head still feeds the replay residual and measures it from a fitted reference.

That may well be the better design: the brief's own wording is "a quantity the model bias cannot move". But the body never names the note's shape, never argues the departure, and cites no orchestrator amendment. Its alternatives section compares only a level fit with a regression. The cost of this shape is measured and real:

- the 100 W/K x 8 h window is detected in 17 of 20 arms at base and 0 of 20 at head;
- the 150 W/K x 4 h window drops from 20 of 20 to 16 of 20.

That makes it a shape choice the orchestrator should own. Owed: either a roster `edit-brief` amending the shape, or a body disposition that the orchestrator accepts.

The hunks outside the owning seam (drift.py, const.py, store.py) are disclosed. Every other group listing those files is ordered against R10-VENT-DETECTOR in the roster's `after` graph, so no missing after-edge.

## Verified (RESULT lines are mine, files in ev/)

### Mutation proof
On a git archive of the head, `PYTHONPATH=tests/hastub python3 tests/features.py`. The unmutated run gives `1 of 4188 FEATURE CHECKS FAILED` (the #363 artifact).

| mutant | result | kill set |
|---|---|---|
| M1 | killed, 7 failures | the body's 5, plus `the prior weighs as one sample` |
| M2 | killed, 4 | as the body says |
| M3 | killed, 2 | as the body says |
| M4 | killed, 6 | as the body says |
| M5 | killed | the 2 named checks, then Traceback rc 1 |
| M6 (upper clip dropped) | killed, 2 | `a warm glitch moves the reference no further than the clip allows` |
| M6b (lower clip dropped) | killed, 3 | as the body says |
| M7 (prior 2.0) | killed, 2 | `the prior weighs as one sample...`, values `[-0.1333], [0.6667]` exactly as quoted |
| M9, mine (`clip=` dropped from the construction) | killed, 4 | |
| M10, mine | **survives** | above |
| M11, mine | killed | above |

### Finder's harness `ident_rolling.py`
sha1 3755ee80dd71 at both ends, P0/P1 x g0.4/0.6/1.0. Every vent_tripped_share figure in the body re-derives exactly:

- P0 g0.4 fix1.00: 0.187 -> 0.000
- P1 g0.4 fix1.00: 0.172 -> 0.000
- P0 base maximum: 0.230
- P1 fix2.00: 0.210/0.134/0.191 -> 0.006/0.009/0.013
- every other arm at head: 0.000
- ua_bias fix1.00 identical at both ends: P0 +0.5174, P1 +0.4374

### Catch-up verifier `learner_v2.py --two-zone`
- ID02 g0.4 prod vent_share: 0.984/0.983 -> 0.000/0.000
- ua_bias: +0.1874/+0.1774 -> +0.5462/+0.5600
- every other RESULT line identical apart from load1

### Planted-window harness
Run at head, and on a base archive with the head's harness files added.

- Worst no-window false_share: 0.617 -> 0.027. The non-zero head arms are the onoff step4 arms, 0.019 and 0.027. The body's "0.019-0.030" upper end is a windowed arm's false_share, which is a minor imprecision.
- Detected windows out of 20:

  | window | base | head |
  |---|---|---|
  | 300 W/K x 2 h | 20 | 20 |
  | 300 W/K x 8 h | 20 | 20 |
  | 300 W/K x 12 h | 20 | 20 |
  | 150 W/K x 4 h | 20 | 16 |
  | 100 W/K x 8 h | 17 | 0 |

- held_share for 300 W/K x 12 h: 0.80-1.00 at head.
- Null (g1.0, ua1.0, no window): 0.000 on all 4 arms at both ends.

### Companion
- base: part1_failures=2 (59, 3), open_learning_gates=1, rc 1
- head: part1_failures=0, open_learning_gates=0, rc 0
- null bias 0.00/0.05 untripped, and the window trips at 98, at both ends

### Class rule (step 6)
`enumerate.py` prints `SEAMS 14 INSTANCE_CANDIDATES 1` at both ends. All 14 seams it returns are dispositioned in the body. `probe_vent_bias.py` reads PROBE FAIL at both ends, as the body says.

### Other checks
- **Structure** (head): `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.
- **Architecture score** (head): `score.py --diff c8cc75ea9` prints `dS +0.0000 NULL`.
- **Step 5:** VERSION, the manifest and RELEASE_NOTES are untouched (pr-contract: "no version edit"). No golden or claim file is in the diff.
- **Step 10, forward-carry:** present in R10-NIGHT-FOLDS' `carry` on handoff/audit-r10-roster, with the predicate stated as a precondition and the control harness named.
- **Step 11, CI at the head:** 78 check-runs. All completed success or skipped except `composed-proof`, which was still in_progress when I wrote this. No red at this head. pr-contract's range check reads `record red-history ... arch-score, env-matrix, mutation, nightly-status, validate-hacs`. Each is named and answered under `## Red checks`, and so is pr-contract at d0001a468.
- **Step 13, merge:** `git merge-tree --write-tree origin/main 3aba8f1eb` exits rc 0, tree 7bd70ea6. Its stderr reads `LEDGER-MERGE: resolved tests/closures.json`, the inert_reads set merge. No MERGE-CLAIM line, because no claim file conflicts.
- **Step 14:**
  - `tests/closures.json`: only the 2 new harness paths are added under `inert_reads["tests/harness_headers.py"]`, earned by the new files.
  - `killed_by` pins: M7 confirms the head commit's CONST pin.
  - The `survivor_triage` CMP_BOUND equivalence holds: `.side` is read once, and the two constructions use side -1 and +1.
- **Step 7:** the body's `## Head` names aa82837c5 as its latest head. 3aba8f1eb is mutation-autofix's bot commit over it, adding one ledger file.
