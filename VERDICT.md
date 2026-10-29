Fix review: merge 9742a6e5db2b44a7fcfabbae1f6c3b818f485fe0

bus-nonce: 29190de6e3e7d2eff9393c26aff3302d

Round 1. Docs-only triage record (one ruling file plus its delivery row); no production line, so no mutation proof applies. Head measured: 9742a6e5db2b44a7fcfabbae1f6c3b818f485fe0.

## Findings

None.

## Evidence

- RESULT replay: for each of f53ac2a39, 2fda9547e, c861c0e7b, 2a5bd4dd2 I ran `python3 tests/env_drift.py --merge-claim-file O A B` on tests/golden/claimed_drift.txt taken at (merge base, first parent, second parent): each exited 0 with `MERGE-CLAIM: resolved`, and the output is byte-equal to the merge's own claimed_drift.txt. The union under app_approve.sh's exact rule (`awk NF | sort -u` of both parents against the merge's file, lines 287-290) differs from the head in all four. The table in the ruling reproduces.
- Ruling shape against proposal-triage.md: one `## P290` entry with Verdict (ACCEPT with its destination, new fly-in R10-FLY-CARRY-CLAIM-DRIVER), Source, Instances beside their commands, Cost and Binding; the rule is run on each instance with a result; the REJECT of option (b) names its binding cost. P290 appears nowhere else on origin/main (git grep), and so does the fly-in name.
- Cost field: the ruling says neither tools/pr/app_approve.sh nor its instrument page has a policy_lint.mjs --budgets row; `node tools/policy/policy_lint.mjs --budgets` lists no app_approve row, so that holds.
- The check cited: app_approve.sh lines 282-290 compare got/want as the ruling quotes; env_drift.py merge_claim_file docstring carries the quoted "Union a branch's list ..." sentence.
- Could not re-derive: the "5 refusals" count and the ~4 h / 3 delta reviews figures come from the live merge_train/train.log on the orchestrator's machine, which is not in this checkout. Not verified by me.
- Merge with origin/main: `git merge-tree --write-tree origin/main HEAD` exits 0, no conflict (ev/merge-tree.txt). review_carry of the head against itself prints CARRY.
- CI on this head: 7 check runs, 1 skipped (arm), 6 queued (prelude, refresh, cancel-superseded, two runs each), none concluded; pr-contract and the body check have not run yet. This verdict is on the diff and the replay; the head's gates were not green at read time. Nothing is red, so no root-cause answer is owed yet.
- carry_audit at head: 0 findings. VERSION, manifest version and notes heading are untouched (the diff touches two files).
