Fix review: blocked a0250fc36517a51c90b2f36046ed1ca1253ca153 mutation-survivor: the run elapsed is not pinned as a clock read; prepr.sh summary_end elapsed=2s constant and the final PRE-PR line's elapsed deleted both leave prepr --self-test 574/0

bus-nonce: 94003d9dedf0fd8b8dddc881acad39ab

## Block

Round 1 (first review, full three-dot diff against merge base dbdc71faea358a95a7b33840ed252b0d8a646a31).

C3 claims that the `PRE-PR:` result line "carries the run's elapsed". Two mutants on added `tools/pr/prepr.sh` lines survive `bash tools/pr/prepr.sh --self-test`. Each ran alone in a fresh worktree of the head. Diffs and logs are in `ev/mut2/`.

- pp4b, in `summary_end`: `rc=$rc elapsed=${SECONDS}s; full log` replaced by `rc=$rc elapsed=2s; full log`. A made-up constant in place of the clock read gives rc=0, 574 passed, 0 failed. The two checks on this field are the tail-line glob `elapsed='[0-9]*'s` and `[ "${t:-0}" -ge 2 ]` after a 2 s sleep. Both accept any constant of 2 or more, so the self-test cannot tell a measured run time from an asserted one. The body's `summary_end` mutant deletes the field and is killed. Replacing the clock read with a value is not killed.
- pp5, in the main flow's final stdout line: `echo "PRE-PR: $(git rev-parse HEAD) $digest elapsed=${SECONDS}s"` reverted to `echo "PRE-PR: $(git rev-parse HEAD) $digest"`. This gives rc=0, 574 passed, 0 failed. This added line is pinned by no check, and the body's `## Unpinned sites` does not list it.

Repair: drive the clock and assert on it. Bash's `SECONDS` is assignable, so the fixture can set `SECONDS=1000` before `summary_end` and assert `elapsed=` of 1000 or more. A constant then fails, and a real read passes. Do the same for the main-flow line: extend the existing `$flow` text check, or test the line directly. pp4b and pp5 are the failing cases, and the unmutated head is the null control.

## Findings

(none beyond the block)

## Evidence

- RESULT: head a0250fc36517a51c90b2f36046ed1ca1253ca153 is the live PR head (`ev/head-live.txt`), and it is what was measured.
- RESULT: `git merge-tree --write-tree origin/main a0250fc365...` rc=0, merges cleanly (`ev/merge-tree.txt`).
- RESULT: `env PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --self-test` at the head: rc=0, 114 ok, 0 FAIL (`ev/ci_predict-selftest.txt`). `bash tools/pr/prepr.sh --self-test`: rc=0, 574 passed, 0 failed (`ev/prepr-selftest.txt`). Both re-derive the body's figures.
- RESULT, timing measured rather than asserted (C3): `step` computes `[$((SECONDS - STEP_MARK))s]`, and `say` resets `STEP_MARK=$SECONDS` at every verdict line. Every `step` duration is therefore a real clock interval since the previous verdict line, which includes unlabelled work between lines, e.g. `take_slot`'s wait before `diff mutants`. Skips (`say skip`) and WARN lines (`say WARN`) print no duration, so a skipped step reports no made-up or zero figure. A killed run prints no step line. These mutants were killed: pp1 (`[0s]` constant), pp2 (run time `$SECONDS` in place of the delta), pp3 (no `STEP_MARK` reset in `say`). The per-step field is pinned.
- RESULT, C4 mutants killed (rc=1 each, `ev/mut/`): cp1 (`if spent >= budget:` changed to `if False:`), cp2 (timing source: `spent += 0.0`), cp3 (replay order reversed), cp4 (`env_seconds` `v > 0` changed to `v >= 0`).
- RESULT, pp4 in the parallel batch: the elapsed check did not kill it. It went red only on `this repository's own wired hooks pass (null control)`, a `stop-selfcheck.sh` failure under 8 parallel self-tests. `stop-selfcheck.sh` does not read `PRE-PR` or `elapsed`. Re-run alone as pp4b, it survives. Carry: dismissed: evidence, not a finding (load flake, not reproduced alone, not this diff's)
- RESULT, exit status: C3 changes only printed strings. `step` still sets rc=1 on a non-zero rc, and `summary_end` and the final `exit $rc` are unchanged. C4: in `ci_predict.py`, rc comes only from `is_red` over predictions (`predict`'s `return (1 if any(is_red...` ), and notes are printed only. A step left past `STEP_REPLAY_BUDGET` enters no prediction, only the `LEFT TO CI` note. A step that is replayed and red still predicts red as before. On a diff whose keyed steps exceed 600 s, prepr no longer predicts a red in the unreplayed tail. That is C4's stated design (RCA R10-RCA-OPEN-PREPR-SLOW, triage P768). `governance / instrument-self-tests` is not in `merge_train.py owed-reds` (`ev/owed-reds.txt`), and CI still runs every step. No required check, ratchet, budget or closure is loosened. `tests/closures.json` only classifies the new harness. No `*_budgets.json`, `VERSION`, manifest or notes heading is touched.
- RESULT: the `prepr_6d_arms.py` harness's `run_arms` replacement is behaviourally identical to `ci_predict.run_arms` apart from the `ARM` timing line. Its `ci_tree_run` and `replay_step` wraps match every call site's positional shape (lines 651, 673, 1197, 1301).
- Not re-derived: the body's C4 wall-clock figures (wall_s 3202/2670, ARM step-replay 1440.4/808.1, the currency.py null control 334/340). Each run takes about an hour on this container. CI's heavy runs are cited, not re-run.
- CI: `merge_train.py classify a0250fc365... --pr 3908` printed `WAIT a0250fc36517a51c90b2f36046ed1ca1253ca153 pending: gate red: none` from 08:38 to 09:08 UTC (`ev/classify.txt`). The block does not turn on it.
