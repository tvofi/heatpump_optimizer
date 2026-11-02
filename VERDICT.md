Fix review: merge 221283d5d9993fdcf54684f138c61b0981bf90a7

bus-nonce: 9a79a1ec2b0f2bef74abe553b7932451

Round 1, record PR (triage batch 111, P369). Measured from a detached worktree at 221283d5d9993fdcf54684f138c61b0981bf90a7; origin/main is 8247a1ed1 (the PR base, not moved).

## Findings

- The PR title says "s9 batch 111" and the delivery row says "s9 batch 111", while the file heading says "session s10". The mismatch is cosmetic and changes no ruling. Carry: dismissed: label-only inconsistency in a record, no ruling or roster op depends on it.

## Evidence

- Three-dot diff: exactly two files, dev/programme/triage/s6-batch111.md (+75) and dev/programme/delivery/3159.md (+1, the PR's own row). No claim file, VERSION, manifest or RELEASE_NOTES change; no host path in added lines.
- git merge-tree --write-tree origin/main HEAD: rc=0, clean.
- Facts re-derived at origin/main: 8247a1ed is hpo-ledger[bot], 2026-11-02T02:34:55Z, "ci: record nightly kills", killed_by files only; df66556f is hpo-ledger[bot], 2026-11-01, same subject; the first-parent hpo-ledger count since 2026-10-12 is 28; MAIN_MOVED_TRIES = 3 at merge_train.py:651; nightly.yml mutation-ledger-push has timeout-minutes 10 and no train-hold read (the record beat reads it, HOLD_MAX_AGE_S=3600); merge_train.py names the hold as issue #2302; mutation_table.dispositions() merges killed_by and survivor_triage, and its header says the completeness check refuses a ledger that disagrees with the inventory in either direction.
- #3147 lists 2 files under custom_components/ (learner_progress.py, snapshots.py), as the file says. #3149, #3077 and #3153 were not re-read.
- Not re-derived: the seat-ledger line 3239 and the "4 pull requests, about 1 h" figure. Both live in the orchestrator's ledger and queue line, outside the tree. The file labels them as sourced there, and no ruling depends on exactness. No roster ruling is cited (no ACCEPT, no carry, no new group), so nothing needed checking at handoff/audit-r10-roster.
- The DEFER reason is testable: it names the figure (more than 10% of CI time, completion time, right-first-time or tokens, with baseline and null control) and the event (a ledger push exhausting --main-moved-tries on a custom_components/ PR) that would re-open it. The quantified claims ("28", "2 instances") are counts with the commands given. The file states the rate is unmeasured.
- Head section names 221283d5d9993fdcf54684f138c61b0981bf90a7 and the authored code head 52a88413. Red checks: none. CI at this head: merge_train.py classify exits 0, "GREEN 221283d5d9993fdcf54684f138c61b0981bf90a7 pending: none red: none". The earlier run was WAIT while gate and pr-contract were running; both concluded.
- review_packet: carry_audit 0 findings; figure_lint 1 resolved, 2 not verified (git show and git log resolve, flags unchecked), 0 refused.
- No mutation or both-ends harness applies: the PR changes no production code.
