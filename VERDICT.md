Fix review: blocked c391823f01f996bb4324815e31424657cd311a20 ci-red: required pr-contract / pr-contract refuses the body, earlier-head reds CodeQL and tests / closures-autofix are unnamed under Red checks

bus-nonce: 19605c8141434db57dbbde6ae1f2f15d

Round 2 of review (third review pass: round 1 at d7b25eca, round 2 at 6ef8ac12, this re-review at the round-2 repair head c391823f01f996bb4324815e31424657cd311a20). Head measured: c391823f01f996bb4324815e31424657cd311a20. The PR head is still that SHA (PR API read, ev/pr-body.txt tail).

## Block

- `pr-contract / pr-contract` (job 128750387573, required: it is in `merge_train.py owed-reds` at this head, ev/owed-reds-live.txt) concluded failure at c391823f01f996bb4324815e31424657cd311a20. The base-restored policy_lint (pinned 73365699, the pre-ruling rule, by design) printed `record red-history 22 commit(s) ... every failure conclusion across them: CodeQL, tests / closures, tests / closures-autofix` and then `ERROR [pr-body] check \`CodeQL\` is red and \`## Red checks\` does not name it` and the same for `tests / closures-autofix`, `PR-BODY: 2 error(s)` (ev/pr-contract-log.txt).
- The gate's code run (job 128750588715) is red on exactly that: `FAIL pr-contract / pr-contract: failure (this run)` (ev/gate-code-run-tail.txt). `merge_train.py classify` ended `RED c391823f01f996bb4324815e31424657cd311a20 pending: none red: gate` (rc 1, ev/classify.txt).
- The body's `## Red checks` names `tests / closures` and `code-scanning alert 52 (js/insecure-temporary-file)`, but not the check-run names `CodeQL` (the earlier-head red that alert 52 caused) or `tests / closures-autofix` (red at an earlier head beside the UNDER-SCOPED closures). The PR cannot use its own relaxation here, because pr-contract runs the base's policy_lint, which is the design round 1 asked for. 
- Repair: a body edit only. Name `CodeQL` (alert 52, already answered) and `tests / closures-autofix` (the autofix lane's red at 6ef8ac12 beside the UNDER-SCOPED closures; `ci-autofix.md` lets it be answered by naming) under `## Red checks`, then let a pr-contract run re-check it. Nothing in the code needs to change: every code claim checked below held at this head.

## Findings

none

## Evidence

- Setup: `cloud-setup.sh --check`: OK. Roles current: `git diff <merge-base>...origin/main -- dev/governance/roles/` touches orchestrator.md and standing-dispatch.md only, not fix-review.md. Packet rendered (ev not copied; refusal: `required-red: required context gate concluded failure`, which was then the edit-run deferral `FAIL run(s) [42483640239] at this head are still being judged`; I waited for that code run to finish).
- Merge: `git merge-tree --write-tree origin/main c391823f01f996bb4324815e31424657cd311a20` exit 0, no conflict (closures.json resolved by its driver).
- All check runs at the head, read across every page (68 runs, ev/check-runs-all.txt). Not success or skipped: `gate` x3 (edit runs 128741159031 and 128745196734, code run 128750588715) and `pr-contract / pr-contract`. `tests / closures` success (the prior UNDER-SCOPED is gone); `codeql / Analyze (python|javascript-typescript|actions)` success; `CodeQL` success.
- Alert 52: I could not read the code-scanning API (HTTP 403 for this integration, ev/alert52.json). At this head, `codeql / Analyze (javascript-typescript)` and the `CodeQL` check run are green. The source no longer has the bare `path.join(os.tmpdir(), ...)` at the named-reds fixture (diff 6ef8ac12..c391823f01f996bb4324815e31424657cd311a20).
- Repair scope: `git diff --stat 6ef8ac12..c391823f01f996bb4324815e31424657cd311a20` = tests/closure.py (+4, budget_raise_gate.py to INERT_EXCEPT), tests/closures.json (+1 file, entities rc 0->1), tools/policy/policy_lint.mjs (+24/-5, mkdtemp and the tmpdir scan pin). Nothing else changed.
- Closure: tests/closures.json's tests/entities.py entry at the head lists gh_read.py, merge_train.py, budget_raise_gate.py and required-contexts.json.
- Self-tests at the head (ev/head-*.txt): policy_lint `FIXTURE ok: 93 error(s) hold 276 pins across 12 check classes`; rules_sync `RULES-SYNC ok` (the .claude/.cursor copies are in sync); review_packet `72 checks, 0 failed`; record_row `all checks passed`; structure `STRUCTURE RATCHET PASSED`.
- RESULT mutant redOwed `return true` first line: killed (rc 1, FIXTURE VACUOUS ..., ev/mut-redOwed-return-true.txt).
- RESULT mutant round-1 fail-closed `if (!names.length)`: killed (rc 1, `an owed-reds that exits 2 with a REFUSE line owed []`, ev/mut-failclosed-rc.txt).
- RESULT mutant alert arm removed: killed (ev/mut-alert-arm.txt). Job-half arm commented out: killed (ev/mut-jobhalf-arm.txt).
- RESULT mutant round-2 bare tmpdir at line 4525: killed (`line(s) 4525 join a name onto the shared tmpdir outside mkdtempSync`, ev/mut-tmpdir-bare.txt).
- RESULT mutant review_packet `--required-file` never passed: killed (3 FAIL, ev/mut-rp-required-dropped.txt).
- RESULT round-1 drive 1 (my own scratch drive, built here, not the fixer's): a worktree at the head with merge_train.py edited so `owed-reds` prints `bogus / name`, committed. Before the restore: `PR-BODY: 0 error(s)` (ev/drive1-before.txt). After running pr-contract.yml's own `Restore the check source from the base commit` script with PINNED=c391823f01f996bb4324815e31424657cd311a20: `Updated 1 path`, and then `PR-BODY: 3 error(s)`, for `tests / typing`, `tests / fast (3.14)` and `gate`. The non-required `tests / nightly-status` and `docs / links` are not owed (ev/drive1-after.txt). With PINNED=origin/main (whose merge_train has no owed-reds), 5 errors: fail closed (ev/drive1-pinned-main.txt).
- RESULT round-1 drive 2, an unreadable set: a `gh` on PATH that exits 1. `owed-reds` rc 2 `REFUSE proof: could not read main-protect-checks's required contexts`; policy_lint prints a skip note naming it and `PR-BODY: 5 error(s)`, so every red is owed (ev/drive2-unreadable.txt).
- RESULT null control at the base 73365699 with 7 reds (3 required, nightly-status, docs / links, an alert, budget-raise-gate): `PR-BODY: 7 error(s)`. At the head with the live set: `PR-BODY: 5 error(s)`. The alert and the job-half `budget-raise-gate` are still owed; nightly-status and docs / links are not (ev/null-base.txt, ev/head-live.txt).
- Figures not re-derived by me: the entities.py `3 of 2667 ENTITY CHECKS FAILED` recording, and mutant_run's 1144 s / 0 SURVIVED. Those are cited from the body. CI's `tests / closures` green at this head stands in for the recording.
- Policy files changed: defect-root-cause.md and fix-review.md. These merge only on tvofi's approving review; this verdict approves nothing.
