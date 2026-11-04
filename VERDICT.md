Fix review: blocked 9e2f045e6c6d8de6c76c403d25f5555fea8c1e4d ci-red-cancelled: PR #3209 was closed unmerged at 2026-11-04T22:51:11Z and the head's gate runs were cancelled, so classify exits 1 (RED) with no failing check of the diff's own

bus-nonce: fe57f1b0fb77097ad99b4d2ae36c0b42

Round 1. Head measured: 9e2f045e6c6d8de6c76c403d25f5555fea8c1e4d (still the PR head at close).

## Block
`merge_train.py classify 9e2f045e6c6d8de6c76c403d25f5555fea8c1e4d --pr 3209` exited 1 (`RED ... red: gate`). The red checks are `gate` x2, `budget-raise-gate` and `arch-score`, all `cancelled`, plus `tests / nightly-status` `failure`. The PR is `state: closed`, `merged: false`, closed_at 22:51:11Z, so the cancellations follow the close. nightly-status grades main and the diff (a triage file and a delivery row) touches nothing it reads, so it owes no answer. The content below is sound; if the PR is reopened and the gate reruns green, this block lifts and the content findings are the whole review.

## Evidence
- Diff is two new files (`dev/programme/triage/s6-batch119.md`, `dev/programme/delivery/3209.md`), three-dot against the merge base. `git merge-tree --write-tree origin/main` exit 0, no conflict (ev/merge-tree.txt).
- carry_audit at the head: 0 findings. figure_lint: 1 command not verified (a `git diff --stat` it does not flag-check), 0 refused.
- Verdict grammar vs proposal-triage.md: one `## P383` entry with Verdict, Source, Instances, Cost, Binding; ACCEPT names both destinations and carry text citing `triage: dev/programme/triage/s6-batch119.md#P383`. The cost names the `--budgets` position (neither file is policy, so no row), and the entry says so.
- ACCEPT destinations exist in `origin/handoff/audit-r10-roster`: R10-CLOSEOUT-CLEANUP (stage in-progress, PR 3085) and R10-FLY-STANDING-CONTRACTS (in-progress, PR 3197). Neither is at `resume.stage: done`.
- Code citations re-derived: `tools/audit/worktree_gc.sh` is 701 lines on origin/main and at d1e7dbbbb; at 5e6d43ae1 `cwd_inside()` is at line 545 and its call `cwd_inside "$real"` at line 752; `merge_pr.sh` line 301 at d1e7dbbbb reads `bash tools/audit/worktree_gc.sh $R 2>&1 | tail -1`; `beatd.py` line 336 at fe2077441 is the `subprocess.Popen(... cwd=cwd ...)`; `beatd.jobs.json` there has 9 `"orch"` lines. All cited commits resolve.
- Not re-derivable here (session-local logs, transcripts, host `lsof`/`stat` fixtures, the held-worktree reproduction, timings, inode values, 387 processes, 104 min): not verified, and the entry's own Instances list them as session facts.

## Findings
- Follow-up: the entry cites `s7/triage-queue-s7.txt` and P382 in `s6-batch118.md` (#3204); neither is in origin/main (no `s6-batch118.md`, no queue file in the tree), so "highest ruled is P382" and "no unruled line" cannot be checked from the tree, and P383 collides if #3204 renumbers. Carry: dismissed: record-only; the orchestrator renumbers P383 at merge if #3204 lands first, and the PR is closed
- Follow-up: the entry's carries require the held-worktree reproduction (class B holder keeps; mutant restoring the `onremote` condition fails arm a); a fixer in R10-CLOSEOUT-CLEANUP should re-run it at its own base, since the table is a snapshot. Carry: R10-CLOSEOUT-CLEANUP
