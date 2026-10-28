Fix review: blocked 75cfbce6f05150bae27908baae2372cf9d1e1870 claim-false: P228's every-failed-job rule excludes its own instance (gate job 122526090837 matches none of the three strings)
bus-nonce: 0f0b65e9d72a51220551954187dcc409

# Fix review -- PR #2900, triage s7 batch 45: rule P227-P231 (V141-V145)

Round 1. Reviewed head: 75cfbce6f05150bae27908baae2372cf9d1e1870, in a detached worktree at that
head. `dev/governance/roles/` has no diff between the merge base and origin/main.

## Results

- Ids: every heading is `## P<n>: <title>` with no proposal id, which is the contract's form
  (P219). Each `Source:` id resolves in the orchestrator's `proposals.md`: `## V141` to `## V145`
  are present, with sources orchestrator s8 and, for V145, a triage s8 escalation. P227-P231 do
  not collide with main (max P211), #2890 (P212-P215), #2891 (P216), #2892 (P217-P218) or #2898
  (P219-P226).
- Citations re-derived at the head (`ev/claims.txt`): `open_pr.sh:37,:55`,
  `pr_args.sh:141-152` and `:145`, `handoff_push.sh:114,:198`, `merge_train.py` (5,831 lines,
  `main_green` 2422-2450, `sweep_bots`' `gh pr merge` at 1110), `review_packet.py:122,:324`,
  `bus.sh:467,:692,:697`, and #2887's `fdf33f466` parents together with the failed ancestry test
  of `a5f40d84c`. All hold. The 47 roster-topic merges and the seven `-pr10`..`-pr16` PRs
  reproduce, as do the four s7 opener logs, 0 tracked `orch_sweep` files, 0 `loop` matches in
  `handover_prompt.py`, and pid 15079.
- Roster facts at `de410e4c9`: every group's stage, carry count and ownership matches the
  ruling's statements. That includes OPENPR-ATOMIC's carry 9 = P72, ORCH-BEATD's carry 1 naming
  the handoff job and heartbeat, and RECORD-HOLD-APPROVE's nightly.yml brief.
- ACCEPT carries (P227, P228, P229, P231) are given as `roster_edit.py append-carry` text in the
  ruling file, which `proposal-triage.md` routes through the orchestrator. The triage seat does not
  edit the roster, so no roster write is owed by this PR.
- `git merge-tree --write-tree origin/main <head>` exits 0 against `6e5995e51`. The diff touches
  only `s6-batch45.md` and its delivery row, so it has no file in common with #2898
  (`ev/merge-tree.txt`).
- Live check-runs (`ev/check-runs.txt`): 26 success, 9 skipped, 5 in progress, 0 failure. No red
  needs an answer yet.

## Findings

- F1 (blocking, claim-false): P228's narrowing makes the arm fire only when "every failed job of
  the run must match" one of three strings. The ruling also says "at the stamp would have re-run
  at 23:43Z". Neither holds for its own primary instance. Run 40596083060's attempt 1 has three
  failed jobs. `validate-hacs` matches `API rate limit exceeded for installation` and
  `env-matrix` matches `the GitHub API is unreachable`. `gate` (job 122526090837) matches none of
  the three; it fails on `FAIL governance / env-matrix: failure (this run)`
  (`ev/p228-instance.txt`). Under the carry as written, the v7.0.5 red is therefore left red, and
  the ruling's measured benefit (2 h 07 min of red main) is not bought. The 23:43Z time is also
  inconsistent with its own clock rule: 3600 s after the last failed job, which is `gate` at
  23:10:21Z, is about 00:10Z. Repair: exclude jobs whose failure only aggregates another failed
  job of the same run (the `gate` judge), or match on the failed required contexts rather than on
  every job. Then add a null control showing that a `gate` red over a non-infra failure is still
  not re-run. Carry: R10-FLOW-MAIN-GATE
- F2 (non-blocking): P228 says "2 h 24 min from the first failure to the re-run". The first
  failure, `validate-hacs`, completed at 22:37:27Z and attempt 2 started at 01:07:45Z, which is
  2 h 30 min. 2 h 24 min is measured from the second failure (`env-matrix`, 22:43:03Z). Carry: dismissed: correct the figure in the same re-cut as F1
- F3 (non-blocking): P227's count "22 branches; 18 absent" is a snapshot. The main checkout now
  holds 23 `fix/*-pr` branches, and 18 of them are still absent on origin with tips in
  origin/main. The argument stands. Carry: dismissed: snapshot figure, conclusion unchanged
- F4 (non-blocking): P231's merge-seat ledger entries (22:19Z, 22:44Z) are in out-of-tree state
  and were not re-read. The in-tree half (`merge_train.py:1110` discards the merge return) is
  verified. Carry: dismissed: out-of-tree log, in-tree mechanism verified
