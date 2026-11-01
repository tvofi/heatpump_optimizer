Fix review: merge 1ac45d875522d5ab8040f8d89d1f05a7aeadda6d

bus-nonce: 49a95932a47964fb2060fc74e8691440

This is round 2: a scoped re-check of the red checks at the same head. The code review in the earlier verdict (refs/heads/verdict/3065) still stands, and I did not repeat it.

## Findings

- `governance / instrument-self-tests` is still concluded red at this head. The orchestrator's attempt 4 re-ran only `gate`. Job 124885182327 is the failure carried over from attempt 2. The body's `## Red checks` names this red and answers it. Cause: on runner image ubuntu-26.04, uutils coreutils refuses the `unrelated-sleep` symlink. Process state: (d). Cheaper detector: none. The fix is owned by #3086. The diff touches none of pr_args.sh, open_pr.sh or update_pr.sh. Main's push job 124813746788 at 6421fe135 fails steps 47, 50 and 73, the same three steps the body names, which confirms the red is main's and not this diff's. The body still calls #3086 "open", but it merged at 2026-11-01T12:08:34Z as 473fdfff2 on main's pr_args.sh, so main's next run carries the fix. Carry: dismissed: the red is answered in the body, the check is not among the required contexts that merge_train reads, and the cause is already fixed on main by #3086

## Evidence

- Head: `git ls-remote origin refs/pull/3065/head` = 1ac45d875522d5ab8040f8d89d1f05a7aeadda6d, both at the start and at the end of this review. It has not moved.
- CI: `merge_train.py classify 1ac45d875522d5ab8040f8d89d1f05a7aeadda6d` returned WAIT (rc 3) at 15:01:37Z, then `GREEN ... pending: none red: none` (rc 0) at 15:03:09Z (ev/classify.log).
- Check-runs: I read all pages, 81 runs (ev/check-runs.tsv), and took the latest run per context. `gate` succeeded (jobs 124885190055 and 124885183392). The latest `pr-contract / pr-contract` run started at 14:59:33Z and succeeded (job 124884555088). That is after the last red concluded (10:05:47Z), so that run checked the body that now carries `## Red checks`. Under step 11 a green run is the evidence. The only failure that is a latest run in its context is instrument-self-tests (see Findings). The red pr-contract rows that remain in the listing are earlier runs, superseded by later green runs.
- Workflow runs at this head (ev/runs.tsv): CI code 41287667687 attempt 4 concluded failure, because it carries the instrument-self-tests job. CI edit 41287668221 attempt 5 succeeded, and so did 41317846192 and 41317561452.
- Body: `python3 tools/audit/carry_audit.py pr 3065` reports 4 routed, 0 unrouted and 0 bad. Item f2b7b8d4 is dismissed as an evidence line recording verified behaviour (ev/carry_audit_pr.log).
- Merge: `git merge-tree --write-tree origin/main 1ac45d875522d5ab8040f8d89d1f05a7aeadda6d` exits 0 at origin/main e4c9e2016a455d787d3a7604ef88c803c3ba5c70 (ev/merge-tree.log).
- Review packet: rendered with rc 0 (ev/packet.log). Its gate digest read red at render time, before attempt 4 concluded, and the live re-read above supersedes it.
