Fix review: merge f5a2c9cba6b6bab1242e381bed5b2960043eb45f

bus-nonce: e7256ceabcd0415fe1723aec6327b4db

## Scope

Round 1 handoff review of the hotfix r10-hotfix-main-ist-readset-2 at head f5a2c9cba6b6bab1242e381bed5b2960043eb45f (one commit on main 2b4515dc52821ad721225090d329c224dbddafae, one file: tools/ci/selftest_closures.json). No pull request exists yet, so there is no review packet and no CI run on this head to wait on or cite; every figure below is this seat's own re-measurement.

## Evidence

- Reproduction red at main, green at head: my own full traced `record` of all 113 gated instrument-self-tests steps, in a fresh `git clone --no-local` at 2b4515dc with no merge-driver config and BASH_ENV unset. It ran in two passes because the first was stopped at the 30-min background limit after 83 complete steps (0 FAIL, 0 broken traces); the second recorded the other 30 (`record --step` x30, 0 failed, 0 broken). The traces were kept (driver ev/rec.py, ev/rec2.py patch out the rmtree) and folded with the tool's own `fold`, then checked with its own `drift` against both tables (ev/cmp.py).
- RESULT main 2b4515dc table: 21 UNDER-SCOPED refusals over 113 measured steps (15 in pass 1, 6 in pass 2), touching exactly 16 steps, the same 16 the diff changes: policy-lint-mutants, field-coverage, verdict-bus, push-names-the-host, selftest-wiring, features-block, mutant-driver, programme-pulse, review-packet, tick-loop (probes, index, objects), hooks-setup, ci-predictor, prepr, open-pr, pr-args, update-pr. ev/drift-pass1-83steps-main-vs-head.txt, ev/drift-pass2-30steps-main-vs-head.txt.
- RESULT head f5a2c9cb table: 0 refusals over the same 113 measured steps.
- Real read set, not a widening: every entry the diff adds (files, probes, dirs, and tick-loop's index/objects False->True) is in my measured read set; unmeasured-added is empty for all 16 steps (ev/added-entries-vs-measured-pass1.txt, -pass2.txt). The diff's removals (`.mailmap` probes on ci-predictor/review-packet/verdict-bus, the junk `-c` probe on open-pr/pr-args/update-pr, push-names-the-host's selftest_* probes) are absent from my measurement, and the head table draws no refusal, so none is a narrowing the trace contradicts. tick-loop reading the index and the object store is measured in a CI-shaped fresh clone, so its widened selection (objects=True runs it on every PR) is the true read set.
- Mutation proof (table mutants against my measurement, ev/table-mutants.txt): unmutated head 0 refusals; tick-loop objects->False, index->False, drop field-coverage day_chart.mjs, drop policy-lint-mutants cfr_exclusions probe, drop programme-pulse dir tools/audit/seat, drop selftest-wiring r10_disinfection_setpoint_mutants.py: each KILLED with exactly one UNDER-SCOPED line. The body's "n/a: data-only" is right that no production predicate exists; these are the data's own mutants.
- Null control: the body's (old table False, new True) is confirmed by the main-table run above, which is the same comparison over a full independent trace.
- At head: `selftest_scope.py static` prints 113 gated step(s), 0 problem(s); `selftest_scope.py --self-test` 117 checks, 0 failed.
- Body figure `record --step <16 steps>`: 16 step(s), 0 failed, 0 broken: the fixer's run, not re-derived literally (its traces were removed); my own record of all 113 steps (0 failed, 0 broken) covers it.
- Body claim "prepr.sh does not call selftest_scope.py (grep: 0 matches)": `git grep -c selftest_scope 2b4515dc -- tools/pr/prepr.sh tools/audit/prepr.sh` rc=1, confirmed. Body figures `PRE-PR rc=0, MODE: FULL` and `STRUCTURE RATCHET PASSED`: not re-run (heavy gate; the diff is one JSON file under tools/ that no budget measures); not verified by this seat.
- Body's per-path merge attribution (#3497, #3458, #3462/#3471/#3476/#3470, #3501, #3488, #3355): not re-derived; it explains the drift and changes no number in the diff.
- Merge with main: `git merge-tree --write-tree origin/main f5a2c9cb` rc=0 (tree 80ca0ef6). origin/main has moved to c67ab5f0 (#3430, #3504) since the body's 2b4515dc; it merges cleanly, and re-checked before return against origin/main 19baca76 (merge-tree rc=0, tree 8464a132), so per the brief the train re-proves it on the current main.
- Head SHA in body equals the head measured (f5a2c9cba6b6bab1242e381bed5b2960043eb45f); the commit message carries no footer or trailer.
- VERSION, manifest version and RELEASE_NOTES.md heading: untouched (diff is one file). No golden fixture or claim file moved; env_drift not applicable.
- Red checks: the red is main's push-only `governance / instrument-self-tests` drift step, which is not in `merge_train.py owed-reds` (tests / coverage-ratchet, fast (3.14), mutation, typing, validate / validate-hacs). It is red at the merge base, so not INTRODUCED; the body names and answers it anyway.
- Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` empty.
- Class: one seam (the measured table); the enumeration is the full-job drift check itself, which I ran over all 113 steps: no step beyond the diff's 16 is under-scoped.

## Findings

- Follow-up: third instance of the stale self-test read-set family by the body's own count (#3487 and this one named; not re-derived): the body defers pricing a cheaper detector to a root-cause seat that it does not open or carry, and `defect-root-cause.md`/CLAUDE.md treat a third recurrence as owing a root-cause analysis. #3487 already carried the countermeasure (run `selftest_scope.py check` before handoff when a gated step's read set can change) to the group that owns the prepr self-test path; this instance belongs to that carry, not to this hotfix. That group is carries-open and `carry_audit.py check --pr-group R10-HOTFIX-MAIN-IST-READSET-2` reports no live receivable target (and #3394 has no owner), so the root-cause seat is the orchestrator's to dispatch (`defect-root-cause.md` step 2, a separate seat). Carry: dismissed: no live receivable destination; the countermeasure is already carried by #3487 to R10-HOTFIX-PREPR-WC-PAD and the root-cause seat is the orchestrator's dispatch, not this hotfix's

## Friction

none
