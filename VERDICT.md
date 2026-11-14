Fix review: blocked a936a11d461cdf08ef8b9e098c3da27cecf9e249 head-moved: measured a936a11d461cdf08ef8b9e098c3da27cecf9e249, head is 3d56953499ef23b0d51f2eee7d0cc782d05b572a

bus-nonce: 0993e0f249830e04e92b3345e42c0654

## Block

The dispatch names a936a11d461cdf08ef8b9e098c3da27cecf9e249. But the handoff ref `handoff/r10-outside-supply-min-run-pause` and the body (BODY.md at handoff-body c1832f9c) both name 3d56953499ef23b0d51f2eee7d0cc782d05b572a, under `## Head`: "The reviewer's delta is `git diff 701a18e26661 3d56953499ef`". That commit existed before this dispatch: it was committed at 18:50Z and the dispatch at 20:05Z (`ev/refs_at_review.txt`). Step 7 requires the body's head to be the head measured, or to carry to it. `tools/audit/seat/review_carry.py a936a11d461cdf08ef8b9e098c3da27cecf9e249 3d56953499ef23b0d51f2eee7d0cc782d05b572a` prints FRESH-REVIEW, because the branch's own commit 3d5695349 changes the content (`ev/review_carry_a936_to_3d569.txt`). So a `merge` on a936a11d461cdf08ef8b9e098c3da27cecf9e249 would attach to a head nobody will push.

This is the block's only cause. The delta a936a11d461cdf08ef8b9e098c3da27cecf9e249..3d56953499ef23b0d51f2eee7d0cc782d05b572a is four new `killed_by` ledger pins under `supply_hold.py/`: `_freeze_span` RETURN_DEL cc6f4da1, `freeze_reason` BOOLOP a6b354ce, CMP_BOUND a6b354ce and RETURN_DEL a2686a80 (`ev/delta_a936_to_3d569.txt`). It touches no production code, and by step 12 a test or instrument delta never widens a round. Every figure under `## Evidence` carries to 3d56953499ef23b0d51f2eee7d0cc782d05b572a unchanged. One thing is owed: a re-dispatch at 3d56953499ef23b0d51f2eee7d0cc782d05b572a. That round's only delta is the four pins. Its only check is that the sites are real and killed. I already ran that check here: `ci_predict.py` lists exactly these 4 ADDED UNPINNED sites at a936a11d461cdf08ef8b9e098c3da27cecf9e249 and 0 at 3d56953499ef23b0d51f2eee7d0cc782d05b572a, and my mutants 0, 4, 5 and 6 kill the corresponding mutations. `_freeze_span` returning None crashes at `now + None`, as mutant 0's TypeError shows.

## Round

This is the third round of r10-outside-supply-min-run-pause. Round 1 at 5dea8264f2 returned mutation-vacuous, and round 2 at 701a18e266 returned merge. No re-cut is owed below the fourth round. Scope is the delta 701a18e2..a936a11d461cdf08ef8b9e098c3da27cecf9e249. `review_carry.py 701a18e2 a936a11d461cdf08ef8b9e098c3da27cecf9e249` prints FRESH-REVIEW (`ev/review_carry_701a_to_a936.txt`).

## Findings

## Evidence

- Head measured: a936a11d461cdf08ef8b9e098c3da27cecf9e249 (`ev/HEAD.txt`). Merge base: 43e95474559ca8e2188830f8775c1ddf52df964a. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- The delta is not only a merge. Besides the two merges of origin/main (62a0d672f and 934f6d683), it holds:
  - 874cb0168 (production): `supply_hold.freeze_reason` replaces `interval_held`, and `ArbiterState.held_at` becomes `held_until`.
  - 808f50df7: `class_excess_loc` 17526 -> 17525, downward.
  - b2dd26288: mutation-autofix's pins.
  - a936a11d461cdf08ef8b9e098c3da27cecf9e249: five pins dropped whose sites 874cb0168 removed.
  I reviewed 874cb0168 as in-scope production code (`ev/commit_874cb01.diff`).
- 874cb0168 keeps behaviour. The old test `now - held_at < 2*interval` and the new `now < held_at + 2*interval` are the same predicate, and `hold_supply`'s `now` is already UTC. The span is now taken from `inp.config` when the write is held, not from the coordinator's `_config` when queried. An options change reloads the entry and rebuilds `ArbiterState`, so the two cannot diverge. Dropping `config or {}` is safe: `hold_supply` reaches `_freeze_span` only after `_held_for` -> `supply_switch`, and that path already calls `EntryConfig.from_mapping(inp.config)` (pump_arbiter.py:1934). `_tail_freeze` keeps the cut reason first: mutant 11 drops it and is killed by "the cut reason outranks the unmetered tail freeze".
- Merge resolution: `git show --cc` of both merges, restricted to custom_components/, shows no hunk differing from both parents (`ev/merge_*_cc_custom_components.txt`). The production files merged textually, so no hand resolution touched production code.
- Each side's behaviour, re-run at a936a11d461cdf08ef8b9e098c3da27cecf9e249:
  - This branch's two blocks (`ev/mutant_cmd.sh`, preludes from `features_block.py --emit-prelude` at the head): `ALL 88 FEATURES BLOCK PASSED | ALL 60 FEATURES BLOCK PASSED` (`ev/baseline_blocks.txt`).
  - main's duty_switch block, from its import to the ceiling-probe marker: `ALL 59` at a936a11d461cdf08ef8b9e098c3da27cecf9e249 and `ALL 59` at main 43e95474, with the 59 ok lines identical (`ev/duty_switch_block_*.txt`, DUTY-BLOCK-IDENTICAL).
  - The whole `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 5416 FEATURE CHECKS PASSED`, rc 0 (`ev/features_full_head.log`).
- Mutation, my own: 15 of 15 killed by the group's command, and the worktree was clean afterwards (`ev/reviewer_mutants.txt`, driver `ev/mut.py`). They cover every predicate and assignment 874cb0168 adds:
  - `held_until` never set, a zero span, three intervals, one interval
  - `<`->`<=` and `<`->`>`
  - never frozen, and frozen forever once held
  - the freeze stamped on every non-None write
  - the coordinator dropping the held reason
  They also cover merged-state guards: the held flag never reset, the cut reason dropped, MIN_RUN `<`->`<=`, the gate removed, and a released entry retrying.
- Failing-first and the finder's harness. `early_cutoff_closed_loop.py` (sha1 39a4867b2afda697d041add836d69a9fd3e37401, `ev/harness_sha1.txt`) was re-run at a936a11d461cdf08ef8b9e098c3da27cecf9e249 with SUPPLY_HOLD=1:
  - Phase 7, NULL HOT LIGHT: all 12 rows equal the body's table after whitespace normalisation (`ev/phase7_compare.txt`, PHASE7-IDENTICAL; `ev/cl7*.txt`).
  - Phase 0 null control (CYCLE_PHASE_MIN=0): all 12 rows equal the body's table (PHASE0-IDENTICAL), and gate on equals gate off on all 6 pairs (`ev/phase0_compare.txt`, `ev/cl0.txt`).
  - Rule three's share was not re-run. It is the body's scratch-driver table from 5dea8264f2, and 874cb0168 does not touch `_ends_soon`.
- arch-score:
  - At the PR's current head b2dd2628 (`get_check_runs`), `arch-score / arch-score` is red. Re-run locally, the base's `gate.py --base 19baca76 --head b2dd2628` prints `dS -0.0006 WORSENS (inadmissible: coord_footprint 2492->2493)`, rc 1 (`ev/archscore_gate_prhead_b2dd2628.txt`).
  - At a936a11d461cdf08ef8b9e098c3da27cecf9e249 against 43e95474, it prints `Architecture score: dS +0.0000 NULL` and `PASS: ... no gate metric rose`, rc 0 (`ev/archscore_gate.txt`).
  - The movement is earned (step 14). A control commit that reverts only 874cb0168's coordinator.py hunk on a936a11d461cdf08ef8b9e098c3da27cecf9e249 reads `coord_footprint 2506->2507` and WORSENS (`ev/archscore_control_revert874.txt`). The pay is the config parse moving out of `_tail_freeze` into `supply_hold`, with semantics unchanged as above.
- Structure: `tests/structure.py` prints STRUCTURE RATCHET PASSED, with `class_excess_loc 17525 <= 17525` (`ev/structure.txt`). The budget diff against main moves `class_excess_loc` 17526->17525 and `max_class_loc` 7921->7919, both down. No raise (`ev/budget_diff_vs_main.txt`).
- Other checks:
  - ha_contract: stub rc 0 and venv-ha `--contracts-only` rc 0, 0 FAIL lines each. "StateMachine.get(None) raises" and "a restart's first write stamps last_changed anew" read ok against real HA (`ev/ha_contract_*.txt`).
  - deployment_shape: ALL PASSED.
  - The merged counts hold at a936a11d461cdf08ef8b9e098c3da27cecf9e249: 90 modules, 32 importing homeassistant at column 0, 109 package files (`ev/counts.txt`).
  - I did not re-derive the closure-pair census of 154.
- Class: the body's rule `git grep -n 'switch_supply('` returns coordinator.py:7832, early_cutoff.py:325 and the definition, the same as round 2. main's duty_switch.py and wear.py hold no `turn_on`, `turn_off` or `async_call` (`ev/class_rule.txt`). The class is closed.
- Merge: `git merge-tree --write-tree origin/main a936a11d461cdf08ef8b9e098c3da27cecf9e249` has rc 0 against origin/main 4145f2852642 (`ev/merge_tree.txt`). 3d56953499ef23b0d51f2eee7d0cc782d05b572a also merges cleanly (rc 0).
- VERSION, manifest, RELEASE_NOTES, golden fixtures and both claim files: the three-dot diff is empty (`ev/version_untouched.txt`).
- CI: no review packet and no CI run exist at a936a11d461cdf08ef8b9e098c3da27cecf9e249 or 3d56953499ef23b0d51f2eee7d0cc782d05b572a. PR #3512 still points at b2dd2628. Its reds there are arch-score, governance/instrument-self-tests, pr-contract and gate. None of them is in `merge_train.py owed-reds`, which prints coverage-ratchet, fast (3.14), mutation, typing and validate-hacs (`ev/owed_reds.txt`). `tests / mutation` is green at b2dd2628. Whether instrument-self-tests is INTRODUCED (`classify --pr`) is for the run at the pushed head. The available log tail is post-job cleanup only, so I could not read which step failed.
- Not re-run: the scoped gate (`MODE: SCOPED -- 24 script(s) run`), entities.py 2709, and the 17-mutant and 10-mutant blocks from round 2, whose lines 874cb0168 does not touch. My mutant 14 re-confirms one of the round-2 guards.

## Friction

none
