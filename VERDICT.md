Fix review: blocked 5fb0a083bec51dd84b816c9b965c56c6365cb9f2 carry-missing: not carried to R10-COP-PARTLOAD, R10-HEAT-METER

bus-nonce: e678ff42b858dc9dd692e476c754eb67

Round 1 of review for #2712 (no earlier `Fix review:` on the PR). Measured head 5fb0a083bec51dd84b816c9b965c56c6365cb9f2, still the PR head when this was written. fix-review.md read from origin/main 2636ce9e9; `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Block

- **carry-missing (step 10).** The body's `## Forward-carry` lines 3 and 4 end `Carry: R10-COP-PARTLOAD` (the 38-40% DP optimality lead) and `Carry: R10-HEAT-METER` (the open-loop `dhw_temp_trajectory` tank seed). Neither group holds a carry from this PR, on origin/main or on the roster branch `handoff/audit-r10-roster` at 1558cf55f. The roster holds both findings under **R10-BUFFER-STORE** instead (commits e11909cff, 0b19947d0, appended 09:06Z, before the PR opened). The PR body was last edited at 19:53Z and now points elsewhere. So the stage the body names was never written, and the body names no roster-branch SHA for the reviewer to open (`finding-propagation.md` Enforcement). Repair: either append both carries to the groups the body names, or point the two body markers back at R10-BUFFER-STORE. Then state the roster SHA in the body. The UX-HEALTH and LEARNER-DEFAULT carries are present and state their control or re-measurement instruction. Evidence: `ev/carries.txt`.
- **The fix's coordinator wiring is unpinned (step 1, step 6).** Two mutants of added production lines in `_propagated_slab` survive the whole suite (`ev/mutants.txt`):
  - M3: `shared=... -> shared=False`.
  - M4: `space_served=... -> space_served=True`.
  
  Only `tests/features.py` reaches this code. Its `#2499` checks test `draw_range.space_draw_kw` with `shared`/`space_served` in isolation, never through the coordinator. The body's claim "a resistive element on the meter ... falls back to the plan's trajectory" is therefore not pinned. With M3 in place, an immersion element's draw is booked as heat-pump space heat into the slab, which is this finding's own bias class. Owed: a coordinator-level value check for the immersion/resistive case and for a mode not serving rooms.

## Findings

- M5 survives: removing the `dt_h <= HOUSE_LOSS_MAX_SAMPLE_HOURS` cap passes every check. The body declares this site (`coordinator.py:1008 CMP_BOUND*2`) as unkilled locally and owes it a survivor triage or a pin. At this head CI's `tests / mutation` is red, with 6 unpinned sites added by the diff, and `mutation-pins (1)/(2)` were still in progress. `draw_range.py:296 CMP_BOUND` is among the unpinned, although the body lists it as "pinned by mutation-autofix". Carry: R10-DEMAND-OVERBOOK
- The body's `max_class_loc` payment is mostly spent prose, which the body does not name. With the three trimmed coordinator-class comment blocks restored, `max_class_loc` is 8444 against the 8425 re-record. The code change alone moves it −5 and still passes the old budget of 8449 (`ev/structure_comments_restored.txt`). Spent prose is a payment `fixer.md` allows, and the ratchet only tightens, so nothing is gamed. But the body attributes the payment to the `_track_dhw` move, and the class loses about 19 lines of explanatory history it never mentions. Carry: dismissed: allowed payment class and the re-record only tightens; the body wording is a record nit, settled by the body repair above.
- `_track_dhw` is added with no blank line after the preceding method's closing `}` (`coordinator.py` near 7654). Carry: dismissed: style only, no check reads it.

## Evidence

- Mutation proof (step 1): M1 gives 2 of 4362 failed, the two named `#2499` checks, rc=1. M2 gives 1 of 4362 failed, the standby check, rc=1. The unmutated head passes all 4362 checks (`ev/features_*.txt`). The body's count is 4356; that was measured at an older merge (428a758e5), and main has since added 6 checks.
- My extra mutant M6 (dropping `space_share` from `space_draw_kw`) is killed by the resistive/split check.
- Harness (step 2): `dev/audit/harnesses/r10_demand_overbook.py`, sha1 f0575c58b587d9a41e922fb5393e1a30a7ddba0b, matching the body. It is the fixer's own instrument; there is no committed finder harness. The roster brief prescribes "root-cause by replay on synthetic installs", which this harness implements, and the PR lands it (fixer.md 18). It ran `--dp` at merge base fa4dad4a7 and at head from the same copy (`ev/harness_base.txt`, `ev/harness_head.txt`). My RESULT, base -> head (body in brackets):

  | arm | scale | plan/deliv |
  |---|---|---|
  | owner_i01 | 1.221 -> 0.616 [1.185 -> 0.628] | 1.674 -> 0.854 [1.634 -> 1.18] |
  | owner_i01_spread | 1.584 -> 0.733 [1.572 -> 0.724] | 1.847 -> 0.666 |
  | meter_half | 2.041 -> 1.289 [2.102 -> 1.247] | — |
  | meter_sat3 | 1.099 -> 0.994 [1.302 -> 1.099] | 1.25 -> 1.194 |
  | slab3x | 0.911 -> 0.888 | — |
  | owner_i03 | 1.0 / 1.0, 0 samples at both ends | — |

  The direction of every metered arm reproduces. The head reaches the oracle on owner_i01 (0.616 against oracle 0.619). The body's exact figures do not reproduce: they were taken at 428a758e5, and main's fa4dad4a7 merge since changed `inputs.py` and `coordinator.py` (+97/−24). Even the oracle arms, which the fix cannot move, differ (owner_i01_oracle plan/deliv 0.854 here against 1.193 in the body). I verified the body's figures as directions only, not as values.
- Null controls (step 3), all reproduced:
  - nometer_half is byte-identical at both ends (1.858 / 1.908).
  - The `*_oracle` arms are identical at both ends.
  - Flat-price ideal arms stay on the truth: null 1.011 -> 0.98, true0.5 0.511 -> 0.504, owner_ideal 0.611 -> 0.611.
  - The in-test nulls (no meter, no previous sample) pass.
- DP reference, owner_i01 last window:
  - Learned model: base plan 6.95 / DP 5.38 kWh (gap 0.0665); head 5.27 / 3.75 (gap 0.158).
  - True house: base DP 1.5 against plan 6.95 (gap 0.9027); head DP 3.75 against 5.27 (gap 0.1598).
  
  These differ from the body's values, for the same base reason. The qualitative claim (the plan still books more than the DP optimum) holds.
- Golden and claims (step 4): `GOLDEN_MODE=drift GOLDEN_REF=fa4dad4a7 tests/golden.py` prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `no committed fixture is stale`. Both claim files are untouched.
- Versions (step 5): `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (`ev/untouched.txt`).
- Class (step 6): the rule `grep -n "_open_loop_plan_value(" custom_components/heatpump_optimizer/*.py` returns the definition, the slab call (closed via `_propagated_slab`) and the tank seed at coordinator.py:6369. The tank seed is dispositioned in the body (`ev/class_census.txt`), so the class is closed.
- Double-count check: `prior_at` is captured before `_async_learn_house_heat_loss` advances `_last_house_sample_time`. Both callers of `_update_current_state` are consistent, and the light first refresh has no prior time, so it falls back to the plan. No double replay found.
- Head (step 7): the body's `## Head` names 53efa142e. It was followed by 398daa3e5 (the bot's `ci: pin killed mutants`) and 5fb0a083b (the delivery row). Neither changes production or test code.
- Structure: `python3 tests/structure.py` at head prints STRUCTURE RATCHET PASSED. The absolute values in the body come from an older budget base; the deltas match (−2, −1, −24, −2).
- Architecture (step 15): `score.py --diff fa4dad4a7 HEAD` prints `dS +0.3249 WORSENS (inadmissible: coord_footprint 2463->2465)`. The body quotes `dS +0.3168` without the verdict word, but it explains the +2 rise under `## Architecture score`, which is the gate's admission path. The `arch-score` check is green. `_propagated_slab` orchestrates: it reads, delegates to `draw_range` and `_replay_interval`, and falls back. The arithmetic lives in `draw_range.py`, which has no HA import. No step-17 breach.
- Merge (step 13): `git merge-tree --write-tree origin/main 5fb0a083b` exits 0. `LEDGER-MERGE: resolved tests/closures.json`; no claim-file conflict.
- CI on this head (step 11), run 40127348701: `tests / mutation` is failure. The body names it under `## Red checks` with step 6d's prediction as the cheaper detector, so the trigger is answered. Green: closures, fast (3.14), coverage, coverage-ratchet, arch-instrument, typing, browser, briefs, arch-score, budget-raise-gate, delivery-status, nightly-status, env-matrix, policy-docs, instrument-self-tests, hassfest, validate-hacs, codeql. `mutation-pins (1)/(2)` were still in progress.
