Fix review: merge 98beb50fd6e7de0142a2e2ec96c55a43475eb00b

bus-nonce: e592fb6997466fd66534b04143323292

Round 3. This is a delta review of `verdict/3089` round 2, which was blocked at `2fd46f26` with class-open. I judged from detached worktrees at `98beb50fd6e7de0142a2e2ec96c55a43475eb00b` with the finder's mutants (`verdict/3089:evidence/own-mutants.diff`), never the fixer's account.

## Summary

Round 2's class is closed at one seam. Under `HPO_UPDATE_BODY_ONLY`, `update_pr.sh` now refuses a run whose merges or row leave `H` other than `LIVE`. The refusal comes after the DIRTY main merge and after `ensure_row`, and before any push. `handoff_arm` passes `HPO_UPDATE_BODY_ONLY=$bonly` on its single launch line. So a body-only move that skipped the review freeze can no longer move a head under a merge verdict or a dispatched review. Both of the finder's mutants and both new guard mutants are killed, and the null controls are green.

## Evidence

- RESULT finder mutant A (`update_pr.sh` `|| MAIN=1` changed to `|| :`) gives `pr_args self-test: 172 checks, 2 failed`, rc=1: both "main conflicting with the head while gh answers CLEAN / an error" rows fail (ev/own-A-update_pr.txt). KILLED.
- RESULT finder mutant B (`[ -z "$bonly" ]` changed to `true` in `handoff_arm`) gives `cloud_relay self-test: 332 checks, 3 failed`, rc=1: the merge-verdict, held-line and reviewer-dispatched body-only rows fail (ev/own-B-cloud_relay.txt). KILLED.
- RESULT my own mutant (the `# mut:bodyonly` guard line deleted by sed from `update_pr.sh`) gives `pr_args self-test: 172 checks, 14 failed`, rc=1. The fails include "a relay body-only run on a DIRTY head whose merge of main is clean refuses, the head unmoved and nothing pushed". The 14 include rows the guard does not decide, because the in-test `mut:bodyonly` row cannot find its line and leaves the fixture moved; the harness's `update_pr-7`, below, is the clean kill (ev/own-C-guard-deleted.txt). KILLED.
- RESULT harness: the in-tree `dev/audit/harnesses/r10_seat_selftests_mutants.py update_pr-1 .. update_pr-7 cloud_relay-29 cloud_relay-57 cloud_relay-58` ran as one invocation at the head. All 10 are KILLED, `RESULT survivors=0`, rc=0. `cloud_relay-58`, the relay flag dropped, gives 332 checks, 4 failed. `update_pr-7` is the guard bypassed (ev/harness.txt). The body's "4 failed" for cloud_relay-58 re-derives.
- Null control at the head: `cloud_relay self-test: 332 checks, 0 failed`; `delivery_row self-test: 6 checks, 0 failed`; `pr_args self-test: 172 checks, 0 failed`, rc=0 (ev/null-*.txt). The body's 332/0, 6/0 and 172/0 re-derive. The row "null control: without HPO_UPDATE_BODY_ONLY a DIRTY pull request still absorbs main" passes inside that run.
- Class enumeration, using the body's rule: `grep -n update_pr tools/audit/seat/cloud_relay.sh` returns one production launch (line 524), and it carries the flag. Every other hit is a self-test fixture. `update_pr.sh` moves the head after `LIVE` in three places: the code-sha merge (not reachable with `-`), the main merge and `ensure_row`. All three come before the guard line (ev/class-and-delta.txt).
- Resolution delta: `git diff 39e9abd5 98beb50fd6e7de0142a2e2ec96c55a43475eb00b` is empty, and the seat, harness and row paths are unchanged from `9da59904` through the code head. The four main merges carry no resolution into this PR's files. The three-dot diff holds only the 8 seat, instrument, harness and row paths (ev/three-dot-files.txt).
- `git merge-tree --write-tree origin/main 98beb50fd6e7de0142a2e2ec96c55a43475eb00b`: rc=0, no conflict and no MERGE-CLAIM lines (ev/merge-tree.txt). origin/main `8e90d814` is the merge base.
- CI: `merge_train.py classify 98beb50fd6e7de0142a2e2ec96c55a43475eb00b --pr 3089` gives `GREEN 98beb50fd6e7de0142a2e2ec96c55a43475eb00b pending: none red: none`, rc=0, at 2026-11-04T12:26:15Z (ev/classify.txt). Of 55 check runs, the only concluded failure is `tests / nightly-status` (id 126549236918, 11:39:05Z), main's inherited red that round 2 established. The diff touches no file the slow lane reads. `pr-contract / pr-contract` runs 126569315397 (12:21:06Z) and 126570700658 (12:23:55Z) both started after that red and are green, and so are both `gate` runs. Under fix-review.md 11 this is not a root-cause block. The body's `## Red checks` cites the run at `2fd46f26` (126439441851) rather than this head's run, but it names the same check and answer, and the post-red pr-contract accepted it.
- `tests/structure.py`: STRUCTURE RATCHET PASSED. `throwaway_git.py --check`: 0 refused, 0 stale. `closure.py select`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
- VERSION, the manifest, RELEASE_NOTES.md, both claim files and `dev/governance/rules`: 0 paths in the three-dot diff. The roles diff since the merge base is empty. No `*_budgets.json` is in the diff.
- Review packet: no refusals; carry_audit gives 0 finding items (ev/review-packet.md).
- Not re-derived: the architecture score `dS +0.0000 NULL` (CI `arch-score` is green at this head) and the body's prepr rc=0.
- `## Head` names `98beb50fd6e7de0142a2e2ec96c55a43475eb00b`. `git ls-remote origin refs/heads/fix/r10-flow-body-only` still gives `98beb50fd6e7de0142a2e2ec96c55a43475eb00b` at verdict time.

## Findings

none
