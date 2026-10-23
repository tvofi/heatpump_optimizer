Fix review: merge 5d874ec6309675a391f1a97acf6e5a77781d3f78

bus-nonce: 33b2500ada6dadcf8525553744425a3b

Round 1. Roster batch PR #2667 (branch fix/audit-r10-roster-pr4), measured from a detached worktree at head `5d874ec6309675a391f1a97acf6e5a77781d3f78`; head re-read via `gh pr view 2667 --json headRefOid` immediately before publishing: unchanged. Merge base with origin/main: `12032c43cc321160ab0278f417c9575b786a03b4`. origin/main at review: `27b59c9f7975d1526529fe5aff21e8243caf19c5`.

Contract currency (fix-review.md, before step 1): `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (rc 0); the frozen contract is current.

RESULT diff-scope: `git diff 12032c43c...HEAD --name-only` prints exactly `dev/programme/delivery/2667.md` and `dev/programme/rosters/wave-r10-groups.json`; `--stat` 2 files, 105 insertions, 8 deletions (roster 104+/8-, row 1+). No carry file touched; nothing outside the roster, carries and the PR's own row.
RESULT structure: HEAD is a single-parent commit (`record: the delivery row for #2667`) on `7dc4f2f0f`, whose parents are `12032c43c` (main) and `3b4b615e0` (roster tip); `git diff HEAD^1 HEAD --name-only` prints only `dev/programme/delivery/2667.md`. The row reads `- [#2667](…/pull/2667) — **open**, …`.
RESULT brief_lint: `node tools/policy/brief_lint.mjs` at head rc 0, `TOTAL: 0 error(s) across 47 file(s)`; every ERROR line in its output is under a `tools/policy/fixtures/` section (awk filter over non-fixture sections prints none). The default set does not include the r10 roster, so also `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` rc 0, `TOTAL: 0 error(s) across 1 file(s)` — matches the body.
RESULT claim-files: `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` byte-identical to origin/main and to the merge base (`git diff --quiet`, rc 0 each).
RESULT version: `VERSION`, `custom_components/heatpump_optimizer/manifest.json`, `RELEASE_NOTES.md` untouched vs origin/main and merge base (rc 0 each).
RESULT figures: re-derived with the body's own jq against B=`12032c43c` (the body's origin/main), H=HEAD: 169 -> 171 groups, removed [], new [R10-FLY-INERT-LOAD-TIME, R10-FLY-NO-FOOTERS-PUSH-PATHS], changed [R10-CI-LAYOUT-P2, R10-FLY-NO-FOOTERS-EMITTERS, R10-FLY-OPENPR-ATOMIC, R10-FLY-RELAY-REVIEW-FF, R10-LOOP-CPU]; stages B {absorbed 1, done 95, in-progress 6, not-started 61, queued 6}, H {absorbed 1, done 96, in-progress 8, not-started 60, queued 6}; `git rev-list --count 12032c43c..3b4b615e0` 21; `git diff 12032c43c...3b4b615e0 --stat` 1 file, 104+/8-. All match the body.
RESULT null-control: `git diff --exit-code 09b7c7635c 12032c43c -- dev/programme/rosters/wave-r10-groups.json` rc 0: main's roster equals the roster's prior landed head, nothing on main overwritten.
RESULT conflict: `git merge-tree --write-tree origin/main(27b59c9f7) HEAD` rc 0, stderr empty.
RESULT checks: 40 check runs at the head (`commits/<head>/check-runs`, evidence/checks.tsv): none failure; all success, skipped or neutral (CodeQL neutral). pr-contract success. No red check, so no root-cause trigger owed; body `## Red checks: none` is consistent.
RESULT title: "Merge remote-tracking branch 'origin/handoff/audit-r10-roster' into fix/audit-r10-roster-pr4" carries no closing keyword. Body: "It closes nothing by keyword" — no `closes #N`/`fixes #N`/`resolves #N` form; #201 stays open.
RESULT forward-carry: body `## Forward-carry: none`; the PR is a roster landing and produces no finding — none owed.

Non-blocking notes:
- The roster branch has moved past this head: `origin/handoff/audit-r10-roster` is now `e4c92864f5d0777f588aa2af69824058fce15863`, 4 commits beyond `3b4b615e0` (`188b84162` append-carry R10-FLY-JIDOKA, `e3d124991` set-resume R10-FLY-JIDOKA note, `6322452d4` set-stage R10-FLY-JIDOKA in-progress, `e4c92864f` roster_sync: derive stages from pull requests). The orchestrator decides whether to update the batch; this verdict measures the PR head only. Carry: dismissed: orchestrator's batching decision, not a finding.
- Body `## Head` first sentence says `5d874ec6` "merges origin/main `12032c43c` into this PR's previous head, and then adds one commit"; `5d874ec6` is itself the single-parent row commit, and the merge is `7dc4f2f0f` (main + roster). The second paragraph states it correctly; wording only, no figure affected. Carry: dismissed: wording, no measurement changes.

Not run (by contract or n/a): mutation proof (no production or test code line; nothing to mutate), env_drift `--all` (no fixture or claim file touched), gate re-run (CI's heavy runs cited). The roster file may be on a code-owned path; any owner approval it needs is the orchestrator's.
