Fix review: merge a59a124a6d7c65fa38545024a7d8c2ff765f2aa7

bus-nonce: 822e9869e2af5ab0c49ef3e93fb68f78

## Evidence
- Scope: full (round 1; no earlier verdict). The diff is instrument, test and body only (tools/audit/seat/*, delivery row); no custom_components/, VERSION, claim file or budget touched.
- classify at head: GREEN (pending none, red none). `git merge-tree --write-tree origin/main <head>` rc 0, no conflict.
- `body_push.sh --self-test`: 49 checks, 0 failed, including the precondition (recorded base differs from origin/main tip), the null control (equal bases), mut:bpbase (its deletion falls back to origin/main), the unreadable-base refusal with nothing pushed, and the no-PR / no-open-PR arms (ev/body_push_selftest.txt).
- `pr_args.sh --self-test` run to my 230 s timeout (rc=124, truncated, no FAIL row); the new open_pr arms (recorded base at p2, origin/main at p1, mut:opbase) and update_pr arms (recorded base, mut:updbase, unreadable base refuses) all printed ok (ev/pr_args_selftest.txt). The full self-test is CI's (`instrument-self-tests` green), not re-run here.
- Read of production lines: `pr_recorded_base` validates a 40-hex sha and fetches it if absent; update_pr.sh and open_pr.sh have R and N set before use; body_push.sh's `keep_refused` exists at line 123. Both mutant markers sit on the lines that carry the behaviour.
- Commits carry no footer, trailer or session link.
