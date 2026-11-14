Fix review: blocked 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf root-cause-unrecorded: tests / fast (3.14) red at this head, unanswered by the body (pr-contract refuses); the red is a Saturday wall-clock test inherited from main, not this diff

bus-nonce: 2b5c2b4965555d7759dbed12e3d1c519

Round 3 is a delta review over the reviewed head ef7e3373e763942a38982c679541c5aa750b3935. The head 0f191f49a8 is a merge. Its first parent is ef7e3373e7. Its second parent is a3c9c90cee, which is the handoff branch (round-3 commits f6813b73..ac5ca58c, already merged with main e23124ff at 428c7b8673) merged with origin/main 50373173d4. I measured in a detached worktree at 0f191f49a8. This is round 3, counted from the round-2 verdict at ef7e3373e7.

## Block

The delta's code is sound. Every round-2 finding is resolved, and nothing in the delta is open (Evidence). The one block is CI's owed-red contract:

- At this head, `tests / fast (3.14)` concluded `failure` (job 132252007494, MODE: FULL, forced because tools/ci/selftest_closures.json changed). The failing check is `tests/features.py`'s only FAIL: `a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked` (ev/ci_fast_head.log.gz).
- That check is in the set `merge_train.py owed-reds` prints (ev/owed_reds.txt). `pr-contract / pr-contract` (job 132265340874) started at 00:47Z, after the red concluded at 00:35Z. It printed `red checks the body must answer: ,tests / fast (3.14)` and concluded `failure` (ev/ci_pr_contract.log). The body's `## Red checks` says none is owed, so the trigger is unanswered (fix-review.md step 11).
- The cause is not this diff. `git diff 50373173d4 0f191f49a8 -- tests/ custom_components/` prints nothing. Main's `tests / fast (3.14)` at 50373173d4 (job 132244017151, started 2026-11-13T23:48Z, a Friday) concluded `success`.
- The check's fixture `_chg_seq` anchors on the real clock. At tests/features.py:62334-62336 it calls `dt_util.now()`, then `start += timedelta(days=(5 - start.weekday()) % 7)`, which is the "on a Saturday" case. Blame: b6696bd6e6 and d2184d4061, merged by #3444. Today, 2026-11-14, is a Saturday.
- Local run at this head today: `PYTHONPATH=tests/hastub python3 tests/features.py` gives the same single FAIL, with 5707 ok, rc 1 (ev/features_sat_fail.txt, ev/features_sat.log.gz). This reproduces CI.
- My shifted-clock control is void: dt_util.now shifted back one day globally (ev/friday_shift.py) crashed at check 63 with a TypeError in an unrelated time-sensitive check (ev/features_fri.log.gz). So the Friday half rests on main's green CI run over byte-identical tests/ and custom_components/, not on a local run.
- I name the class root-cause-unrecorded, not detectable, because no cheaper detector than this check shows a calendar-day red before the handoff. The remedy is for the body to answer it under `## Red checks`: name `tests / fast (3.14)`, the cause above with its #3444 origin, and either "no cheaper detector exists: this check is the cheapest", or a re-run on a weekday, which leaves the test unfixed. The test's wall-clock anchor is carried below. Fixing it in this PR would be outside its scope.

## Findings

- tests/features.py:62334-62336 (`_chg_seq`, from #3444) builds its fixture from the real `dt_util.now()` and weekday. The check "a charge-start dip that recovers is learned as neither a draw nor usage …" fails on a Saturday run, with main's code unchanged, and so reddens `tests / fast (3.14)` (an owed required check) on every PR and main push tested on a Saturday. Control: main's identical tests/ and custom_components/ were green on Friday 2026-11-13 (job 132244017151), and red today at this head both in CI and locally (ev/features_sat_fail.txt). The fix is to anchor the fixture on a fixed datetime, as the file's other Saturday cases do (lines 17489, 56767, 71761). Carry: dismissed: no receivable owner exists, because R10-OUTSIDE-DHW-CHARGE-SETTLE (the group whose #3444 added it) is at stage done and no live roster group or carries file owns tests/features.py's DHW draw-learning checks; the orchestrator owes a hotfix group or a carry-<N>.json, which a probe-only reviewer cannot create

## Evidence

- ev/HEAD.txt: 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf. The PR body `## Head` names this head, and the API read of the PR at verdict time gave head.sha 0f191f49a8 (step 7).
- Round-2 block (introduced-red under GITHUB_BASE_REF): resolved. `self_test` now pops GITHUB_BASE_REF and SELFTEST_BASE for the run and restores them afterwards. RESULT at head:
  - unset: `selftest_scope self-test: 148 checks, 0 failed`, rc 0 (ev/selftest.txt).
  - `GITHUB_BASE_REF=main`: 148 checks, 0 failed, rc 0 (ev/selftest_with_GITHUB_BASE_REF.txt).
  - `GITHUB_BASE_REF=nosuchref SELFTEST_BASE=nosuch`: 148 checks, 0 failed (ev/selftest_with_bogus_bases.txt).
  - The regression is pinned: `selftest_scope_mutants.sh` now runs its baseline and every mutant under exported `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch`, and its mutant "the self-test leaks the caller's base selectors" is refused.
- RESULT `sh tools/ci/selftest_scope_mutants.sh` at head: 35 `== ` lines, 35 `self-test rc 1`, `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0 (ev/selftest_scope_mutants.txt). This matches the body's 35. The `FAIL` and `1 failed` lines in that log are the mutants' own refusals, not a baseline red. I re-ran it alone after my own driver had finished, because the two had overlapped once (ev/selftest_scope_mutants_rerun.txt): 35 `== `, 35 refused, `every mutant refused`, rc 0.
- RESULT, my own mutant driver (ev/own_mutants.py, mine, not the finder's; the PR names no finder harness and none is owed for an instrument fix, which round 1 already recorded). Every mutant ran under `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch` (ev/own_mutants.txt):
  - KILLED pop-only-GITHUB_BASE_REF (148 checks, 1 failed).
  - KILLED pop-only-SELFTEST_BASE (148 checks, 1 failed).
  - KILLED union_entries-keeps-unmeasured-steps.
  - KILLED drift-probe-own-dirs-removed.
  - SURVIVED int-guard-passes-None. This is equivalent on its own: the guard only acts when `self_test` returns non-int, and the script's mutant "the self-test wrapper returns nothing" already pins that pair. Not a finding.
- Resolution read-back per parent (`git merge-tree --write-tree --name-only origin/main ef7e3373e7` conflicts in 4 paths: .claude/workflows/audit-find.js, dev/audit/config/bugclasses.json, dev/audit/config/finding.schema.json, tools/ci/selftest_scope_mutants.sh):
  - selftest_scope_mutants.sh keeps both sides' mutants. Main's four were retargeted to this branch's `union_entry` spellings, and each one still applies once, because the script asserts the count and refuses each one.
  - The class lists keep both main's N-provisional-gate-red-read-final and this branch's R10-SELFTEST-TABLE-SHRINK. `fold_ledger.py check`: 56 classes, 0 violation(s), rc 0 (ev/fold_ledger_check.txt).
- tools/ci/selftest_closures.json: the head's blob 84846dffa2 equals a3c9c90cee's, and it is not main's e81ad4d9d5 (ev/closures_blobs.txt). Per parent (ev/closures_per_parent.py, mine; ev/closures_per_parent.txt):
  - Against origin/main and a3c9c90cee: 0 reads and 0 flags lost, 114 steps each.
  - Against main, the head only adds: one step gains the probe `HEAD`, `objects: true` and git `diff` (ev/closures_vs_main.diff). That is over-approximation, which is safe. The body's line "main's re-recorded table (#3557) at this head" is loose on this point, but no figure depends on it.
  - Against ef7e3373e7, the only reads gone are throwaway-git-helper `probes`. Main's own re-record (#3557) dropped them, so this PR did not remove them.
  - The PR's own shrink guard accepts both ends: `SELFTEST_BASE=origin/main python3 -I tools/ci/selftest_scope.py static` gives `114 gated step(s), 0 problem(s)`, rc 0 (ev/static.txt), which matches the body's figure. `SELFTEST_BASE=ef7e3373e7…` gives 114 gated steps, 0 problems, rc 0 (ev/static_vs_reviewed_head.txt).
- `git merge-tree --write-tree origin/main 0f191f49a8`: rc 0, merges cleanly (ev/mergetree.txt).
- Step 12 scope: the PR's own diff against the merge base is 8 files. None is in custom_components/; the custom_components/, golden and budget paths in `git diff ef7e3373e7 0f191f49a8` are main's. The delta is instrument, test and record only, so the review is not widened. Step 5/14: the PR's own diff touches no VERSION, manifest, notes heading, claim file, budget or tests/closures.json.
- Owed reds (ev/owed_reds.txt): `governance / instrument-self-tests` is not in the set. Step 11's INTRODUCED exception is judged by classify below.
- CI: `merge_train.py classify 0f191f49a8 --pr 3551` printed `WAIT … pending: gate red: none` (rc 3) on every poll from 00:10Z to 00:51Z. At 00:52:54Z it printed `RED 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf pending: none red: gate` (rc 1) (ev/classify.log). The live check-runs at 00:52Z: `tests / fast (3.14)` failure, `pr-contract / pr-contract` failure, `gate` failure, and a second `gate` in_progress (ev/checks_not_green.txt). `governance / instrument-self-tests` concluded success at this head, so the round-2 introduced red is gone in CI too. `git ls-remote origin refs/pull/3551/head` printed 0f191f49a8 at 00:52Z.
