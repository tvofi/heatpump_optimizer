Fix review: blocked 475e001874041628b919539bfdac006ba495da37 code-defect: postmerge owes a mark on every clean no-group merge; carry_fold lease and record_beat body wiring unpinned

bus-nonce: d5e5ccbac87ca9308cc357a9ef3588ea

Round 1 (first review of #3701; no reviewed head before this one).

## Block

1. **code-defect: `postmerge.postmerge`'s stage arm owes a `mark` on every merge that resolves to `no-group` with a clean sync.** The new arm raises `OSError("no group to queue")` for `group == rb.NO_GROUP` before it looks at `queued`. With `code == 0` that appends `("mark", "queue: no group to queue")` to `owed`, even though `queued` is empty. `merge_pr.sh:553` and `merge_train.py`'s `post_merge` run `postmerge.py` after every merge, and `record_beat.resolve_group` returns `no-group` for every `triage/*` and `record/*` branch (its own self-test rows). After this PR, each such merge prints `OWED mark: queue: no group to queue`, exits rc 1, which fails `merge_pr.sh`, and opens a `postmerge-owed` ledger event that nothing owes. Harness (reviewer-built, `ev/harness_nogroup.py`, run at the merge base `4ecca4cc58` and at the head): with sync rc 0, the base returns `rc 0 ... nothing owed`, ledger not opened; the head returns `rc 1`, `OWED mark: queue: no group to queue`, ledger opened. Null control in the same harness: with sync rc 1, both ends print the same `set-stage owed no-group` and `OWED stage` lines (`ev/nogroup-both-ends.txt`). No self-test row covers a clean no-group run. Fix shape: owe nothing when `queued` is empty, and pin it with a row covering a clean no-group run.
2. **mutation-vacuous: three production mutants on added lines survive**, so the body's claim that `carry_fold.py` and `record_beat.py` are "pinned instead by the mutant tables and rows" does not hold (`ev/mutants-out.txt`, driver `ev/mutants.py`, each mutant applied in place at the head, run with the file's own self-test, then restored):
   - M9 `carry_fold.py` `main`: `rc, lines = leased(a.state_dir, LEASE_WAIT_S, lambda: fold(...))` -> `rc, lines = fold(...)`. SURVIVED (`carry_fold self-test: 9 checks, 0 failed`). The real fold path never takes the lease, so Carry 7's fold side is off, and nothing fails.
   - M10 `record_beat.py` `facts`: drop `"body": d.get("body") or ""` from the return. SURVIVED (`record_beat self-test: 17 checks, 0 failed`).
   - M11 `record_beat.py` `facts`: drop `,body` from the `gh pr view --json` field list. SURVIVED (17 checks, 0 failed). `postmerge`'s self-test replaces `rb.facts` with a wrapper that injects `body` (its `go` helper), so in production an empty body would derive no marks, Carry 8 would do nothing, and no test would see it.

## Findings

- Note: stale-body: the `## Head` section names `513fbcd2c9` as the merge base and says the gate scope was re-run against it. The head's merge base is now `4ecca4cc580b1065e366bf12bd5a917d40d03c0e`, after the later main merge `809e0079c0`. The figures re-taken here at the head match the body. Carry: dismissed: the re-cut this block owes rewrites the body at its new head

## Evidence

- Head reviewed: `475e001874041628b919539bfdac006ba495da37` (`ev/HEAD.txt`), the PR head as read from the PR at review time; the body's `## Head` names the same SHA.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- `git merge-tree --write-tree origin/main 475e0018` exited rc 0 with no stderr (`ev/merge-tree.err`), so the head merges cleanly.
- `merge_train.py classify 475e0018 --pr 3701` printed `GREEN 475e001874041628b919539bfdac006ba495da37 pending: none red: none` (`ev/classify.txt`).
- `governance / instrument-self-tests` is red at the head and also red at the merge base: `merge_train.py introduced` printed `introduced: 0 ... head job 133816487439 failure base job 133799884479 failure` (`ev/introduced.txt`). It is inherited, so it is not this PR's finding.
- `tests / nightly-status` is red but outside the `owed-reds` set, so it is owed no answer.
- Self-tests re-run at the head (`ev/selftests-head.txt`) match every figure in the body: beat_jobs 291/0, postmerge 38/0, carry_fold 9/0, roster_lib 103/0, record_beat 17/0, cloud_relay 521/0.
- Thirteen of the reviewer's targeted mutants die, each on its named row (`ev/mutants-out.txt`). They cover these sites: M0 refuse's `event` call, M1 the refused skip, M2 the lease-yield break, M3 the `#refused` arm, M4 refused->done, M5 the persisted `roster-refused.json`, M6 LOCK_EX->LOCK_SH, M7 no wait loop, M8 carry_fold's `leased` ignoring the lease, M12 the marks derivation, M13 the dismissed-reason guard, M14 the already-marked skip, M15 the P435 refusal line.
- Carry 8 figure re-derived: `derive_marks` over the body's five `Carry N: built here` lines against `wave-r10-groups.json` at `0c8313fd16`, and at the current `origin/handoff/audit-r10-roster`, prints `5 ops; 0 owed` (`ev/carry8-figure.txt`, `ev/marks.py`).
- `VERSION`, the manifest version, `RELEASE_NOTES.md` and both claim files are untouched by the three-dot diff, which has 8 files, all under `tools/audit/seat/` plus `dev/programme/delivery/3701.md`.
- The PR names no finder's harness, because the carries are instrument work from the roster. The no-group harness is the reviewer's, disclosed as such.
- `cloud_relay` `fold_superseded` mutants: `mut:foldmerged` deleted: KILLED, 2 failed (`a stop whose fix/<topic>-pr merged into origin/main leaves the level`, `... and folds nothing ...`), `ev/cr-mut-foldmerged.log`. `mut:foldlater` replaced by an always-true test: KILLED, 2 failed (`null control: a handoff-body older than the stop keeps its OWED line`, and also an unrelated `PREDICTOR` null row), `ev/cr-mut-foldlater-always.log`. The body's own `mut:foldsuperseded` run was not repeated.
