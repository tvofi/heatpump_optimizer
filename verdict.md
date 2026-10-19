Fix review: blocked 4c1352f05aa6797e06a7af5fdc456039756f2bcc architecture-unsound: departs from the R10-VENT-DETECTOR architect note (Shape: a detector input independent of the replay residual), and no roster edit-brief amends it (handoff/audit-r10-roster 95d31034f)

bus-nonce: aff6bc827020bb8860d4881c741a8f4b

Round 2. The one earlier `Fix review:` comment is round 1 (blocked 3aba8f1eb, vacuous-test, plus an architect-note item stated for the next round).
Head measured: 4c1352f05aa6797e06a7af5fdc456039756f2bcc (`ev/HEAD`). Base: the merge base fa16596c3 (current PR base). The body measured against dd27e7c1b; every figure re-derives at fa16596c3 too.
Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so this contract is current.

## Blocking -- architect note (step 15)

The roster's note for this group, is unchanged at handoff/audit-r10-roster 95d31034f, the tip at 05:58Z (and at 72470f36b before it):
"Shape: a detector input independent of the replay residual". It binds under fixer.md 17, which lists "a group's architect note followed".

The head keeps the replay residual as the detector's input and tracks a fitted reference instead. The body now names the departure, argues it, and leaves acceptance to the orchestrator.

I checked the argument and it holds:
- `const.py` defines no window, door or contact `CONF_*`.
- `CONF_INDOOR_HUMIDITY_ENTITY` is an optional entity (config_flow `_STORED`, group "mold").
- The cost is measured, and I re-derived it below: 100 W/K x 8 h is detected on 17 -> 0 of 20 arms, and 150 W/K x 4 h on 20 -> 16.

My judgement is that the departure looks sound. But a reviewer cannot amend a binding note, and the roster records no acceptance:
- The tip commit 72470f36b appended this PR's carry (2) to R10-NIGHT-FOLDS.
- It left R10-VENT-DETECTOR's `architect_note` and `brief` as they were.
- There is no orchestrator comment or review on the PR.

To clear this, the orchestrator runs `roster_edit.py edit-brief R10-VENT-DETECTOR` to amend the shape (or re-scopes the group). Nothing else in this verdict is open. A re-review after that edit needs only step 15 and the head check, as long as the head has not moved.

## Round-1 blocking 1 -- resolved

The two new sun checks drive the feed through `_async_learn_house_heat_loss`. Each mutant was applied to its own git worktree of the head, and the full `PYTHONPATH=tests/hastub python3 tests/features.py` was run (`ev/M*.log`, diffs in `ev/mutants/`):

| mutant | result | detail |
|---|---|---|
| M0, unmutated | ALL 4213 FEATURE CHECKS PASSED, rc 0 | |
| M10, sun regressor -> 0.0 | 1 of 4213 failed | FAIL `a bias scaling with the sun never trips the detector ...`; evidence trips at 2026-01-16T10:30 |
| M10b, `/ 1000.0` dropped | 1 of 4213 failed | the same check; sun slope -0.0013 against -1.33 |
| M10c, `or 0.0` dropped | 1 of 4213 failed | FAIL `an unknown irradiance feeds the detector as no sun`; TypeError |
| M11, heat regressor -> 0.0 (null control for the sun checks) | 3 of 4213 failed | only `the fourth trips ...`, `a tripped detector freezes ...` and `while frozen ...`; both sun checks pass |

Every count and kill set matches the body exactly. Production code (`custom_components/`) is byte-identical in the PR's own diff between round 1's head 3aba8f1eb and this head; only tests changed. So the round-1 mutants M1-M7 and M9 still apply as verified then.

## Verified at this head (my RESULT lines, in ev/)

### Finder's harness `ident_rolling.py` (step 2)

The harness is sha1 3755ee80dd71 at both ends. I ran P0/P1 x g0.4/0.6/1.0 at base fa16596c3 and at the head (`ev/ident/`, `ev/ident_vent_table.txt`):

- P0 g0.4 fix1.00: 0.187 -> 0.000.
- P1 g0.4 fix1.00: 0.172 -> 0.000.
- The P0 base maximum is 0.230.
- P1 fix2.00: 0.210/0.134/0.191 -> 0.006/0.009/0.013.
- Every other arm reads 0.000 at the head.
- Null (g0.6, g1.0, fix1.00): 0.000 at both ends.
- ua_bias fix1.00 is identical at both ends: P0 +0.5174, P1 +0.4374.

### Planted-window harness `r10_vent_bias_window.py`

The harness is sha1 c8d01ade at both ends and was copied into the base worktree. Each end printed 120 RESULT lines (`ev/window_*.txt`, `ev/window_summary.txt`):

- Worst no-window false_share: 0.617 (seed2.onoff.g0.4.ua1.0) -> 0.027 (seed2.onoff.g0.4.step4.ua1.0).
- At the head, the only non-zero no-window arms are 0.019 and 0.027, latching 6.50 and 9.00 h.
- Detected windows:

  | window | base | head |
  |---|---|---|
  | 300 W/K x 2 h | 20/20 | 20/20 |
  | 300 W/K x 8 h | 20/20 | 20/20 |
  | 300 W/K x 12 h | 20/20 | 20/20 |
  | 150 W/K x 4 h | 20/20 | 16/20 |
  | 100 W/K x 8 h | 17/20 | 0/20 |

### Companion

- Base: part1_failures=2, open_learning_gates=1, rc 1.
- Head: part1_failures=0, open_learning_gates=0, rc 0.

Files: `ev/companion_base.txt`, `ev/cheap.txt`.

### Scratch probe (the body's source, re-run by me as `ev/probe.py`)

Check schedule, tripped intervals per day:

| bias | head | sun regressor zeroed | heat regressor zeroed |
|---|---|---|---|
| 0.4 K | [0,0,0,0] | [0,19,18,18] | [0,0,0,0] |
| 0.7 K | [0,16,0,0] | | |
| 1.0 K | [0,20,0,0] | | |

Census schedule: the steady and heat-scaled arms at 0.1/0.4/1.0 K trip 0 intervals each. The sun-scaled arm trips 0, 27 and 107 intervals at 0.1, 0.4 and 1.0 K. Every arm is untripped at the end. All of these match the body (`ev/probe.txt`).

### Class rule (step 6)

`enumerate.py` prints `SEAMS 14 INSTANCE_CANDIDATES 1`. Its seams are dispositioned in the body, unchanged since round 1.

### Step 5

The diff against fa16596c3 touches no VERSION, manifest, RELEASE_NOTES, golden or claim file.

### Step 7

The body's `## Head` names 4c1352f05 first. Non-blocking: its second paragraph names `bd51be06273f...`, which does not exist in the repository (a superseded carry merge, by its wording).

### Step 10, forward-carry

Both carries are on R10-NIGHT-FOLDS.carry at 72470f36b:
- (1) The night predicate must sit after the `_vent_cusum.update` feed. Its control is `r10_vent_bias_window.py`.
- (2) The sun-scaled transient. Its controls are the probe and `ident_rolling.py --plant P1` fix2.00, each stated as a precondition. (2) was missing at the body's SHA 73bb15fe8, and the orchestrator appended it since.

### Step 11, CI at this head

The check-runs API listing is in `ev/check-runs.txt`. All 48 check-runs had concluded by 05:57:39Z: 33 success and 15 skipped. That includes `closures` (the scoped gate, success at 05:57:12Z) and both `pr-contract` runs. None is red. The mutation lane's log reads `0 survivor(s) of 3 evaluated = 0.0%`, `MUTATION TABLE PASSED`, with the NULL_COMMENT null control surviving. Earlier reds on the branch are named and answered under `## Red checks`.

### Step 12

I re-read the head before writing; `git ls-remote` at 05:58Z returns fix/r10-vent-detector-pr = 4c1352f05aa6797e06a7af5fdc456039756f2bcc.

### Step 13, merge

`git merge-tree --write-tree origin/main(2d843030a) 4c1352f05` gives rc 0 with empty stderr (`ev/merge-tree.*`). There is no conflict and no MERGE-CLAIM line.

### Step 14

The PR's file set is unchanged since round 1. Round 1 verified the earned instruments: closures inert_reads, the killed_by pins and the CMP_BOUND triage. Structure: `STRUCTURE RATCHET PASSED`.
