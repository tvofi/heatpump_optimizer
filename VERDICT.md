Fix review: blocked 19c3f4f85cad138f99c63309ac1717ae8d601439 class-open: pr_host_refusal measures every topic in one shared scratch tree, so two refusals measured at once call a head's own break the host's, close a true host refusal, and leave a wrong answer cached for main

bus-nonce: 23a4ce0c97187d9a619ca95ac73e344f

Round 2 of this hotfix (round 1 blocked `4b91c2f9f705b76db9e041e1c88ad12bb79147f8`, class-open). Scope: the delta, `tools/audit/seat/open_pr.sh`, `pr_args.sh` and `instruments/open_pr.sh.md`; no production (`custom_components/`) delta is the branch's own, so nothing widened. Reviewed from a detached worktree at the head.

## Block

1. **The predicate's unguarded domain: overlapping measurements.** `pr_step_sig` builds its worktree at `<cache>/tree`, and `op_host_refusal` passes one cache for every topic (`$(dirname -- "$D")/selftest-main`, i.e. `$HPO_STATE_DIR/pr/selftest-main`). The only lock held is the per-branch one, and the body says the run is outside prepr's heavy slot, so two topics refused during the same host fault (the case the hotfix exists for; one measurement is ~6 to 11 minutes by the body's figures) remove and replace each other's tree mid-run. Measured with `ev/race-probe.sh` (the reviewer's probe, a stand-in self-test in the fixture shape of the suite's own; `ev/race-probe.log`, three trials each, all alike):
   - cold cache, a clean head and a head-broken head overlapping: the head-broken head reads **0, the host's**. This is round 1's class (a head's own break called the host's), reached by timing instead of by path.
   - warm cache, overlapping: a true host refusal reads 1, the head's, so its PR closes: #3508's defect.
   - after a cold overlap the cached `<main sha>.sig` holds the corrupted run's rows; alone and unraced, both clean heads then read 1 until main moves or the file is removed.
   - control, sequential: clean heads 0, broken head 1.
   With the real self-test two corrupted runs are less likely to agree row for row than with a stand-in, so the first bullet is shown on the stand-in only; the second and third need only one run to be disturbed. Owed: a scratch tree no other run can touch (one per invocation, or the cache under a lock), main's answer written only from an undisturbed run, and an arm that overlaps two measurements and fails on today's code.
2. **Surviving reviewer mutant, same repair.** Deleting `[ ! -f "$w/tools/audit/prepr.sh" ] || st=tools/audit/prepr.sh` in `pr_step_sig` leaves the suite at 235 checks, 0 failed (`ev/selftest-m8.log`). No tree at this head holds `tools/audit/prepr.sh`, so the branch is unexercised: pin it with an arm or drop it.

## Findings

none beyond the block.

## Evidence

- No review packet and no CI exist before the pull request opens; nothing was waited on, and step 11 has no check run to read. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`. Body `## Red checks`: none.
- Head: body `## Head` names `19c3f4f85cad138f99c63309ac1717ae8d601439`; `refs/heads/handoff/r10-hotfix-openpr-host-refusal` still pointed at it when this verdict was written. Role contract diff merge-base...origin/main under `dev/governance/roles/`: empty.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 (origin/main `43e95474559ca8e2188830f8775c1ddf52df964a`, merge base `005eed2573da9e946fa4838de147401d0ff36cc1`).
- RESULT mutation proof, in-suite: `bash tools/audit/seat/pr_args.sh --self-test` at the head, 235 checks, 0 failed, rc 0 (`ev/selftest-head.log`); every `mut:host*` and `ret:*` arm the body names prints ok.
- RESULT null control: `open_pr.sh` from `4b91c2f9` with `pr_step_sig` and `pr_host_refusal` removed, under the head's arms: 235 checks, 19 failed, among them "a self-test refusal the head's own commit causes still closes the PR, under the host fault" (`ev/selftest-null.log`). The body's figure holds.
- RESULT reviewer mutants (diffs in `ev/mutants-diff.log`, failing rows in `ev/mutant-fails.txt`): m1 compare exit status only, killed, 2 failed, the inputs arm reads 0 of 60; m2 FAIL rows dropped from the signature, killed, 2 failed, 0 of 60; m3 `rm -f "$c"/*.sig` removed, killed, 1 failed; m6 `OP_REFUSED=1` removed, killed, 3 failed; m8 survives (Block 2).
- RESULT round 1's class, by path: `selftest_inputs` evaluated from prepr's text at the head returns 60 entries (`ev/selftest_inputs.txt`); the arm reads 60 of 60 as the head's. The comparison is of two trees, not of names, so no entry is left to a list. Closed for sequential runs; open under overlap (Block 1).
- Seam rule, close sites: `git grep -n -E "gh pr close" -- tools .github .claude` returns the two lines the body states; `pr_host_refusal` has one caller, `op_host_refusal` (`ev/cheap-checks.log`).
- Scoped gate: `closure.py select` prints `MODE: SCOPED -- 1 script(s) run`, `tests/doc_claims.py`, which passes (343 checks); `tests/structure.py` passes. `VERSION`, notes heading, `custom_components/` and goldens: no change in merge-base...head; no claim file touched, so `env_drift.py --all` was not run.
- Log shape read against the tree, not the stub: prepr's `say` prints `  REFUSE   self-test ...` and app_push's `die` prints `app_push: REFUSE: the body did not pass tools/pr/prepr.sh...`, both matching the classifier's patterns.
- Not re-derived: the body's real-tree measurements (664 s for the two signatures, 346 s and 542 passed for prepr's self-test on main) were not re-run; they are the fixer's.
- The finding still has no committed finder's harness; the probe above is the reviewer's, disclosed as such.
