Fix review: merge 8b0f5c316903372f34e5194a9c5791fd9b8365ee

bus-nonce: 0c035d192d8bd46cd58a8a803f913bd2

## Summary

Review round 2 of #2946 (R10-CONFIGFLOW-PAGES arm D). Round 1 (`verdict/2946`, `d0033ecbe`) returned `blocked 324755c9f carry-missing: not carried to R10-ROUND-PLAYBOOK or R10-ARCH-SHAPES-CLASSIFIER`. Both carries now stand on `handoff/audit-r10-roster`, so that block is settled. The head moved 324755c9f -> 8b0f5c316 only by `closures-autofix`'s one-line `tests/closures.json` re-record, which the body describes. Measured head: `8b0f5c316903372f34e5194a9c5791fd9b8365ee`, the PR head at review time (`refs/pull/2946/head`). The dispatch brief's snapshot names 324755c9f, but the dispatch prompt and the PR name 8b0f5c316, so this verdict is on 8b0f5c316.

The fixer says arms A, A3', B, C and C2 and bug D7-s2-56 already merged as #2912, #2913 and #2915. I verified that claim against main with the finder's harness and the in-tree harness, below. This diff adds one production change (the unread `dr` import is dropped), two downward budget rows and the landed finder's harness. `Closes #2238` is earned: all twelve findings-table rows are dispositioned to merged pull requests that name them, and both carry destinations exist and state their control as a precondition.

## Evidence

- Role contract: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current. Review packet rendered locally (`review_packet.py render`, rc 0, `Refusals: none`, `CARRY-AUDIT: 3 routed, 0 unrouted`, `FIGURES: 15 resolved, 3 not verified, 0 refused`). The three not verified are `git diff` flag lines, which I re-ran myself.
- Interpreter: a venv built from `tests/requirements-ci.txt` on Python 3.14.6. The body states 3.14.7. All figures below are counts.
- Finder's harness `dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py`: sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf` at this head, the same as at `3930b421a`, so it is the finder's harness, landed byte-identical. I ran it at three trees (`ev/harness_runs.txt`):
  - RESULT pre-#2912 `aa1d6720e`: `wizard_fields=46 in_registry=44 spelled_twice=44 disagree=0 other_in_registry=20 other_spelled_twice=20 menu_disagree=0 golden_equal=1`. With `--bump heat_pump_cop_nominal`: `disagree=2` (`building_extras`, `thermal`).
  - RESULT merge base `66974d473`: `spelled_twice=0 other_spelled_twice=0 disagree=0 golden_equal=1`. With `--bump`: `disagree=0`.
  - RESULT head `8b0f5c316`: the same as the merge base. ARCH2-s5-F1 was fixed on main by #2915, as the body says.
- In-tree harness `dev/audit/harnesses/r10_configflow_pages.py` (D7-s2-56):
  - RESULT pre-#2912: `stale_slots=27` of `stored_rows=30`. `--null`: `shown_stored=19`. `--clear-required`: `type=menu errors=None stored_price_entity=None`.
  - RESULT base and head: `stale_slots=0`. `--null`: `shown_stored=19`, so the null control is flat. `--clear-required`: `type=form errors=price_entity_required stored_price_entity='sensor.price'`. D7-s2-56 was fixed on main by #2912.
- Mutation proof (step 1), with `tests/ci_ratchet.py`'s `compare()` over `archscore_metrics()` (`ev/checks.txt`):
  - RESULT base: `unused_boundary_imports 1 (budget 1)`, `literal_clone_copies 123 (budget 186)`, `grew 0`.
  - RESULT head: `0 (budget 0)`, `123 (budget 123)`, `grew 0`, `budget_problems []`.
  - Restoring `device_registry as dr` at the head gives `GREW archscore.unused_boundary_imports: 1 (budget 0)`, `grew 1`. The restore was undone, and the tree is clean. The check is not vacuous.
  - `grep -nE '\bdr\b'` over `config_flow.py` at the head prints nothing, so the import really was unread.
- Step 14 (earned movement): removing the mechanism (the mutant above) brings the metric back to 1, so the 1 -> 0 move is earned. `literal_clone_copies` already measures 123 at the merge base (`186` was a stale recorded row; the drop is #2915's arms C/C2, as the design note predicted, 185 -> 123). The row is re-recorded at a value the tree measures, and no instrument was changed. `score.py --diff 66974d473`: `Architecture score: dS +0.0000 NULL`, `unused_boundary_imports 1 -> 0 (gate only)`, which matches the design table's arm D row "0, gate only". I did not plant a new literal clone to show that 123 refuses growth. That is the ratchet's standing behaviour, and this diff does not change the instrument.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Steps 4 and 5: `git diff --name-only 66974d473...HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden/` prints nothing. No claim file or golden moves, so there is no drift to compare (`wizard_widgets` `golden_equal=1` at base and head).
- Diffstat: `git diff --stat 66974d473...814f944f1` reads `3 files changed, 162 insertions(+), 5 deletions(-)`, matching the body's figure, which the body says it took at the code head `814f944f1`. At 8b0f5c316 it reads `5 files changed, 164 insertions(+), 5 deletions(-)`, which adds the delivery row and the closures line.
- Scope: `python3 tests/closure.py select --diff 66974d473` prints `MODE: SCOPED -- 13 script(s) run, 20 scoped out.` This matches the body.
- Step 13: `git merge-tree --write-tree origin/main 8b0f5c316` gives rc 0 against `66974d473` (tree `56a4f7453`) and rc 0 against the moved `origin/main` `d074b94b0` (tree `f74cee54e`). No conflict, and no claim-file driver ran.
- Design (step 15): the approved note `32892dc67863` (`dev/programme/designs/R10-CONFIGFLOW-PAGES.md`, branch `design/R10-CONFIGFLOW-PAGES`) defines arm D as: drop `dr` and lower `unused_boundary_imports` 1 -> 0, and re-record `literal_clone_copies` at the head's measured value, with the merge-base figure, the head figure and the drop in the commit message. Commit `814f944f1`'s message carries "merge-base figure 123 ... head figure 123, drop 63", and `recorded_at` moves to `4b9ee5377`. The diff departs from the design nowhere. The added harness is a byte copy of the finder's, at the finder's path. No architecture breach was found.
- `Closes #2238`: I checked each of the issue's twelve findings rows against its merge commit on `origin/main` and searched the merged commits' messages and changed files for the finding id (`ev/disposition_prs.txt`):
  - D10-s1-51 #2290 `d8c13ac5b`
  - D2-s2-01 #2365 `413944b67` and #2368 `499f952b0`
  - D7-s2-01 #2527 `4b36dc730` (id in its tree, 10 hits)
  - D7-s2-51/52/53/54 #2379 `5756f2b15`
  - D7-s2-55 #2913 `ee4893758`
  - D7-s2-56 #2912 `ba19d13c4`
  - D7-s2-57 and D8-s1-01 #2819 `4f3c73020`
  - D7-s2-59 #2282 `4c01a3dc2`

  All are merged, and each names its id. D8-s1-01's finder harness `f1_active_now.py` at the head reads RESULT `heating_now_while_off=0 slot_steps_declared_off=0 snapshots=36 steps=192`, which matches the body (`ev/f1_active_now.txt`). The design's `close-2238` and `dr1-close-2238-disposition` carries are discharged by the body's list.
- Class (step 6): the issue's enumerator `enumerate_p2.py` at the head reads RESULT `F1_run_threshold=13 F2_learner_gate=8 F3_cop_law_fork=2 F4_entry_resolve=0 F5_clone=24 F6_hour_clock=2 F7_scrub_mixin=1 seams_total=50`, matching the body (`ev/enumerate_p2.txt`). The seams it returns that this diff does not touch are dispositioned in the body as findings fixed elsewhere, the classifier arm and the four probed instances (R10-ARCH-SHAPES-CLASSIFIER), and the eleven F5 clone classes (R10-ROUND-PLAYBOOK). Nothing is left open.
- `probes_p2.py` at the head stops at its sixth probe with `NameError: name 'defrost_interval' is not defined` (`ev/probes_p2.txt`), matching the body. Not re-derived: the body's scratch-copy figure `probes_failed=5 of probes_total=5`. I did not rebuild that scratch copy, so that number is the fixer's and is unverified here. The destination carries re-measure it as a precondition.
- Not re-derived either: the ledger-anchor figure (103 rows, 0 unresolved). I did not rebuild the stated `ast` rule. The figure belongs to earlier arms' carries (`ledger-rekey`), discharged in #2912/#2913, which this diff does not touch.
- Step 10, forward carries: both destinations exist on `handoff/audit-r10-roster` (tip `792e3bc45`). `494831e99` and `8c06d2836` are both ancestors of the tip.
  - Group R10-ARCH-SHAPES-CLASSIFIER `carry[6]` names the four probed instances and states "Precondition and control: re-measure at this stage's own merge base with ... probes_p2.py ... with defrost_interval bound", with a rebuilt null.
  - Group R10-ROUND-PLAYBOOK `carry[8]` names the eleven F5 classes, the `probes_p2.py` NameError and the dispatch-time roster-stage check, under "Precondition and control: re-measure at the stage's own merge base ...", with a null.
- Step 11, CI on the head, read from the check-runs API (`ev/check_runs.txt`): all 107 runs were completed at read time.
  - `pr-contract` went red twice at 10:31-10:32Z, and the body answers it under `## Red checks`. Runs that started after the last red concluded (10:39:22Z, 10:43:02Z) are green.
  - `tests / closures` was red on the previous head 324755c9f. It is UNDER-SCOPED (`INERT READS UNDER-APPROXIMATED`), answered by naming it (ci-autofix.md) and by naming the cheaper detector `ci_predict.py` and its gap.
  - `tests / nightly-status` is red. It grades main's nightly lanes, and this diff does not reach its inputs, so it is not this PR's.
  - `gate` is green (`123399915061`). `mutation` is green, but this diff writes one changed production line that only deletes an import name, so its table is not load-bearing here. `tests / ci-ratchet` is skipped on both PR runs, so the lowered rows are first graded on the push to main. My local `compare()` above stands in for it.
- Step 12: the head was re-read just before return as `8b0f5c316903372f34e5194a9c5791fd9b8365ee`.
- Path hygiene: the brief's home-path grep over this verdict and `ev/` prints nothing, and evidence paths are home-relative.

## Findings

- `tools/pr/ci_predict.py`'s inert-read model misses `tests/harness_headers.py`'s copy-census `rglob` read of a `.py` nested below `round*/D*/`. It printed "no closures ... red predicted" at `814f944f1`, and `tests / closures` then went red UNDER-SCOPED on `324755c9f`. The body names the gap and leaves it to the root-cause seat, and no open roster group owns it. `closures-autofix` repaired the red as `ci-autofix.md` assigns. The red-check trigger is answered in the body (`defect-root-cause.md`), and whether a countermeasure is worth building is the root-cause seat's decision, not this arm's. Carry: dismissed: red-check trigger answered in the body with the named detector and its gap; countermeasure decision belongs to the orchestrator's root-cause dispatch under defect-root-cause.md, outside arm D's scope
- #2238's issue body records "RCA: owed" for class P2 (round 10 instances leaked the barrier). Closing the issue does not discharge or erase it: the obligation is held in `dev/audit/config/bugclasses.json` class P2 (`trigger`, `rca` = `R9-P2`, `RCA-1499`, `RCA-R8-P2`, `R10-RCA-BUFFER-STORE`), which this diff does not touch, and the design scoped this group to dispositioning the findings rows. Carry: dismissed: the class RCA obligation lives in bugclasses.json P2, untouched by this PR and outside the group's design; closing #2238 does not remove it
