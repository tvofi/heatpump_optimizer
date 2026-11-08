Fix review: merge 265309b18236ed020da6dd25b5efaca1f880af40

bus-nonce: bcd8a56faefc37c9c8ef2433f6030872

Round: first round. Reviewed at head 265309b18236ed020da6dd25b5efaca1f880af40 from a detached worktree, three-dot against merge base 7c9c4c154cda514f938fd503cde2779716caf251. The diff touches the code-owned `.github/workflows/ci.yml` and `tools/ci/`. It merges only on tvofi's approving review (or the mandate the body names), and this seat posts no approval.

## Findings

- The `gate` job's new comment in `.github/workflows/ci.yml` says the code run's gate "waits for them before it judges". At this head, after the main merge, `gate.judge` re-runs the deferring run and then defers to it at once, with no wait; `gate.py`'s module doc and the PR body both say so. This is a comment-only inaccuracy in a code-owned file and no behaviour depends on it. It is not worth re-opening the frozen branch. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Evidence

- CI: `merge_train.py classify 265309b18236ed020da6dd25b5efaca1f880af40 --pr 3303` printed `GREEN 265309b18236ed020da6dd25b5efaca1f880af40 pending: none red: none` (exit 0), in ev/classify.txt. The head has 68 check runs, all on one page, and none concluded red (ev/checks_all_pages.txt). No red check owes an answer, and the body's `## Red checks: none` matches.
- Merge: `git merge-tree --write-tree origin/main 265309b1...` exits 0 against origin/main e36e5327dde8. The ledger driver merged `tests/closures.json` as a set and printed `LEDGER-MERGE: resolved` (ev/merge_tree.txt).
- Self-tests: at the head, gate 86 checks with 0 failed and prelude 65 checks with 0 failed. At the base, gate 77 and prelude 62, also 0 failed. The head counts match the body's figures (ev/selftests_*.txt).
- Mutation proof, re-run at this head because the body says M5-M8 were taken before the main merge (ev/mutants.txt, driver ev/mut.py). Every mutant was killed:
  - M1 prelude 5 red; M2 prelude 1; M3 prelude 1; M4 prelude 1 and gate 7. These match the body.
  - M5 gate 2 red (body: 3); M6 gate 2 (body: 9); M7 gate 4 (body: 5); M8 gate 1 (body: 1). The counts differ from the body because, as it discloses, the gate tests now expect an at-once deferral. Every mutant is still killed.
  - My own mutants: R1, `waiting_on` drops `pending`, which would let a gate pass beside an unjudged deferring body run: gate 2 red. R2, `redispatch` re-runs a run that has not completed: gate 1 red. R3, `pending` takes the earliest run per kind instead of the latest: gate 4 red.
- Race drive with null control (ev/drive_states.txt, driver ev/drive.py). `prelude.defer_to` was driven over a code run that was queued (pending), in its units (running), had started `pr-contract` (running) and was completed (concluded):
  - Base: 40, 40, None, None. Beside a started `pr-contract` the edit run did not defer and waited, which is the race the brief names. At the base only `edit` defers (`kind == "edit"`, prelude.py:327).
  - Head: 40, 40, 40, None, with `BODY_KINDS = ('edit', 'review')`.
  - The judging-code-run null control (full workset, no wait) is the prelude self-test check `null: beside a JUDGING code run`. It is green at the head and is killed by M2.
- Gate verdicts across the three states, read from the self-test scenes and confirmed by the mutants:
  - Pending (a deferring run still at its own gate): the code gate defers at once and re-runs nothing.
  - Concluded deferring: the code gate re-runs the latest run of each kind once and defers at once.
  - Concluded with units run: it re-runs nothing and passes.
  - Pending deferred runs are in `waiting_on` for every gate, so no gate passes while one is unjudged (R1 is killed). A refused re-run, or one at the attempt cap, publishes red and never PASS.
  - Convergence depends on `gate-sweep.yml`'s `settle`, which re-runs a red gate that judged before another run's jobs finished (tools/ci/sweep.py). I traced both interleavings, code gate first and deferring gate first, and both end in a code gate attempt that redispatches. Attempts are bounded by `ATTEMPT_CAP`.
  - A held (`action_required`) code run is not in `UNFINISHED` (prelude.py:87), so it never absorbs a deferral.
- Permissions and data handling: the `gate` job goes from `actions: read` to `actions: write`. Its step `Restore the programs from the base` checks out `tools/ci/*.py` from the base SHA before it runs, so only main's programs hold the write token. PR-derived values reach the shell only as quoted env vars (`"$PR"`, `"$BASE"`, `"$KIND"`), and titles are parsed as data (`parse_title`). `tests/entities.py`'s workflow-hygiene check names `ci.yml:gate` in its refused-subjects null control. The new path is not exercised live on this PR: this PR's own edit runs ran main's programs. It first runs on the edit runs after the merge.
- Classification: the new tracked file `dev/audit/harnesses/r10_ci_slim/body_defer.py` is in `tests/closures.json` (CI `tests / closures` and `closure-scope` are green). The delivery row `dev/programme/delivery/3303.md` is in the diff. `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/structure_budgets.json` are untouched. `budget-raise-gate` is green.
- `## Head` names 265309b18236ed020da6dd25b5efaca1f880af40, the head I measured. Its second SHA, daa600e64c47, is an ancestor of the head.
- Forward carry: the body's id-shadowing finding is on roster group R10-HOTFIX-GATE-BUSY-DEFER, in its brief at roster d5d8c221e677 ("From r10-ci-edit-runner, body item 27233708 ..."). The text names the failing case, a body run numbered below its code run whose units are shadowed. That case is the control a later seat tests against.
- Class seams: the body's rule is `outputs()` sending every `kind != "code"` to `wait_sources`. It returns edit, review, label and kernel-points. Edit and review are closed in the diff, and label and kernel-points are dismissed in the body with a zero-sample count. I agree the rule returns those four kinds.
- Figures re-derived (ev/figures_rederived.txt). The body's $SAMPLE is in this branch's own history: `dev/audit/harnesses/r10_ci_slim/body_defer_sample.json` at commit 81375a031dbd, sha1 fb0d479ba40d694d8feeb5ffc864084fd89df034, which matches the body. A fresh `edit_runs.py --fetch` timed out at my 25 min cap (ev/fetch_attempt.txt). Running `body_defer.py` at this head reproduces every replay figure in the body exactly:
  - Since 05:00Z, edit: 70 runs, 70 deferred, 53 re-run; job-minutes 358 -> 426; prelude wait above the floor 12 -> 0; code-gate wait added 122. Review: 20 runs, 20 deferred, 19 re-run; 180 -> 57; prelude wait 127 -> 0.
  - Whole window, edit: 399 runs, 396 deferred, 271 re-run; 3524 -> 2187; prelude wait 2022 -> 0; code-gate wait added 625. Review: 99 runs, 95 deferred, 69 re-run; 889 -> 263; prelude wait 652 -> 2.
  - Prelude floor 0.45 min. Null control: code runs 368 (88 since 05:00Z), 0 deferred, job-minutes equal before and after.
  - Control at b4ec2f332fe3 (prelude sha1 72652866a927, identical to the merge base's copy): review runs 99, 0 deferred. That matches the body.
  - Not re-derived: the edit-gate p90 of 11.92 min against a median of 0.58, and the edit prelude median 0.48 / p75 0.52 / max 5.8 since 05:00Z. The body itself says no tree command prints them.
- The finder's harness: the packet names none. This is a CI-instrument group, and its tests are the gate and prelude self-tests plus the committed `body_defer.py`, which the fixer built and the body discloses as its own.
