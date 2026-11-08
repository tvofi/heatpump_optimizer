Fix review: merge 6016f9dd6e0ff482d0e140946721657357653726

bus-nonce: 7cd814e94379735d9b3e6415de52c405

Round 1 (first-round adversarial fix review), PR #3308, group R10-MIN-POWER-FLOOR, head 6016f9dd6e0ff482d0e140946721657357653726 measured from detached worktrees at the head and at the merge base 6188936a8bdc58b510ecb8794ad86350283c49a7. The diff was judged against the approved design (design/r10-min-power-floor 23fbff36), not the design itself.

## Evidence

- RESULT head-measured=6016f9dd6e0ff482d0e140946721657357653726; `git ls-remote` just before writing the verdict shows the same head on fix/r10-min-power-floor (ev/heads-at-verdict.txt).
- RESULT role-file-current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` touches only orchestrator.md. I read fix-review.md from origin/main.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 6016f9dd` against origin/main 8a4cf2618 exits 0 and prints `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt` and `LEDGER-MERGE: resolved tests/closures.json`, with no conflict (ev/merge-tree.txt).
- RESULT harness (step 2): I ran the finder's harness as committed at d58242d8c (handoff-wip, the stop-report harness) and the extended copy this PR lands, at both base and head (ev/harness-{finder,landed}-{base,head}.txt). Every figure in the body re-derives:
  - clamp=True with DHW, `max_total`: 5.30 / 5.00 / 5.00 / 3.50 at base, and 3.50 in all four cells at the head. `total_below_min` is 0 at both ends.
  - Declared arm `clamp=on_off`: at base it equals the clamp=False lines (7 / 5 / 62 / 27 / 55 / 39 running steps below 2.5 kW). At the head, `total_below_min=0`, `space_only_below_min=0` and `max_total<=3.50` in all 8 cells.
  - The finder's own `space_steps_below_min` reads 3 / 1 / 3 in the head's clamp=True DHW cells, as the body discloses: those are mixed steps.
- RESULT null control (step 3), ev/null-control.txt: the 8 clamp=False lines are byte-identical base vs head under both harness copies, and so are the 4 clamp=True DHW-off lines. Flat-price cells sit beside every cost figure. Objectives (spread / flat) at the base and head are 38.844->39.056, 20.652->20.601, 67.571->67.364 and 39.167->39.167, as quoted. They are objective values and not a savings claim, as the body says. The clamp=True control arm is present and runs.
- RESULT mutation (step 1): I applied 11 mutants of my own, distinct from the fixer's table, to the head's production files, ran the #3289 features block after each, then restored the files (`git status` clean; ev/mutants.txt). All 11 were KILLED by named checks:
  - A: legacy true not read as on/off
  - B: the cap ignores DHW (max 4.34)
  - C: the raise ignores DHW (max 5.30)
  - D: DHW not projected in the joint arm
  - E: the publish left unclamped (8 steps below 2.5)
  - F: the scorer reverted to per-channel projection
  - G: probe `on_off` inverted
  - H: `duty_cycle_realizable` reverted to base's read
  - I: `learner_unmetered` reverted to base's read
  - J: the select's `modulating` ignored
  - K: the band's raise threshold moved
  - Of these, mutant F (`_realize_draw` scoring per-channel while the publish stays joint) is killed only by the unit check on `_realize_draw`; neither solve-level check notices it. That is a kill, not a survivor, and I record it only as the strength of the pin.
- RESULT features block at the head: `ALL 9 FEATURES BLOCK PASSED` (ev/block-head.txt).
- RESULT claims (step 4): `tests/env_drift.py --all 6188936a8` printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56`. The output shows `CLAIMED config_flow: 2 leaves moved`; those two leaves are the compressor_modulation leaves, plain and seeded. Every solver fixture is byte-identical, including winter_single_dhw (ev/env_drift-all.txt).
  - `config_flow.json` numstat is 20 insertions, 0 deletions.
  - `card_claimed_drift.txt` is untouched.
  - Plain `env_drift.py`: NO UNCLAIMED DRIFT, NO STALE FIXTURE.
- RESULT version (step 5): the diff from 6188936a8 to the head leaves VERSION, manifest.json and RELEASE_NOTES.md empty.
- RESULT class (step 6): I re-ran the body's enumerator grep at the head (ev/class-enum-head.txt). Every production site it returns is dispositioned in the body. The publish-path enumeration agrees: `_build_result` has two callers, the space-only publish (`_published_levels`, DHW absent) and the joint publish (`_realize_joint`). The scorer's `objective` and `objective_batch` both go through `_realize_draw`. `CONF_COMPRESSOR_MODULATION` and `CONF_CLAMP_PLANNED_LEVELS` are read only inside `declared_modulation`, as the design requires.
- RESULT other configurations (step 6), all checked by reading the code:
  - On a frequency-write install declared on_off, `planned_range` returns None (pinned in S4).
  - `p_min=0` is the identity.
  - The B x N batch broadcasts against the N-vector DHW (pinned).
  - A user who saves `auto` keeps base's clamp on 5 surfaces (pinned).
  - Legacy `clamp_planned_levels: true` now clamps on a fully metered install too. The design note (line 33) states that legacy true means on/off, so this is in the approved design, and the body's "declared on_off on any surface" covers it.
- RESULT structure (step 14): `tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `class_excess_loc` is 17560 at the base and 17558 at the head. The -2 is earned: the publish's two 3-line `_published_levels` statements inside HeatPumpOptimizer became one 4-line `_realize_joint` call, and the projection moved out of the class. No budget is raised.
- RESULT D5/D6 figures: `option_doc_coverage.py` at the head prints `option_fields_rendered=205`, `option_schema_keys_rendered=238` and `option_fields_undocumented=0`. `claims.py` regenerated the D6 register with no diff against the committed `46 selects` C125 row.
- RESULT carries (step 10): roster handoff/audit-r10-roster d96891da holds:
  - the group's three carries: the 3289 reply, the #3297 revalidation and the option_doc_coverage re-measure;
  - R10-I18N-DE's carry for the German label;
  - R10-USER-DOCS-VERIFY's carry for the docs row.
- RESULT red checks (step 11): pr-contract / pr-contract 128753384570 started at 14:02:20Z, after the last red concluded at 11:49:15Z, and is green. The body names `codeql / Analyze (actions)` (the CodeQL download outage) and `gate` (derived).
- RESULT CI (merge_train classify): every run exited 1, `RED 6016f9dd... pending: none red: gate` (ev/classify1.txt, ev/classify-log.txt).
  - The red is two stale `gate` jobs, 128721349979 and 128721563207, in the "CI edit" suites (runs 42471173865 and 42470643072). Their only failure line is `FAIL codeql / Analyze (actions): failure (run 42470642055)`.
  - That codeql job has since re-run green: 128753170500 succeeded at 14:02:17Z. The code suite's gate 128753622846 is green at 14:03:59Z, and every other context is green or skipped.
  - The red is therefore an infrastructure aggregate already answered in the body, not this patch. `classify` keeps the worst gate across suites (A5), so the train will not pass this head until those two edit-suite gate jobs are re-run. That re-run is the orchestrator's, carried below.
- RESULT harness provenance (step 9): the finder's harness was out of tree on handoff-wip (d58242d8c). It lands here, extended, in 08e52f9b0, and the body discloses the extension as the fixer's. I built no instrument of my own beyond the mutant driver, whose mutant list is in ev/mutants.txt.

## Findings

- Follow-up: the comment on `const.CONF_CLAMP_PLANNED_LEVELS` (const.py:802) still documents only `false` and absent. The diff makes `true` a declared on/off that clamps on any surface, including a fully metered one, and the docs row does not say so. Carry: R10-MIN-POWER-FLOOR
- Follow-up: merge_train classify stays RED at this head only on the two stale CI-edit-suite `gate` jobs (128721349979, 128721563207), which failed on the since-re-run-green `codeql / Analyze (actions)`. Re-run those two jobs before the train takes this head. Carry: R10-MIN-POWER-FLOOR
