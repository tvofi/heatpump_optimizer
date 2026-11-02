Fix review: merge 9e7b016f71214991bbea0076f0d83a891d68acc1

bus-nonce: 9231bb78e95a7851984bb237381f5b78

Delta review of 9e7b016f7 against the merge verdict at 71a7f87e2. Host: Linux (cloud container), detached worktree at the head.

## Summary

1. `review_carry.py 71a7f87e2 9e7b016f7` prints `FRESH-REVIEW` (rc 1): five branch-only commits (b354aa665, b5f3cd536, 3c00ec8cc, 1a94fa629, 9e7b016f7). The first reason is that b354aa665 is not the automatic merge of its parents: it is the hand union of the Relay paragraph conflict in standing-dispatch.md. I reviewed that and the items below.
2. Compression commit 3c00ec8cc: read line by line. It changes only the Relay paragraph (3 insertions, 4 deletions). Every clause of the union paragraph is kept: `cloud_relay.sh pass --confirm`, `bus.sh confirm` on merge verdicts carried to the live head, report each `handoff-body/<topic>`, and the beat-job sentence (takes over once a cycle's log agrees; never inline). Only "run", the full path, "return" and "one" were dropped.
3. Policy lint: `policy_lint.mjs --budgets` rc 0; standing-dispatch.md is 39 lines (cap 39), 2036 bytes by `wc -lc`. No `*_budgets.json` differs from origin/main.
4. Main merges: the merge base equals origin/main (279cb497f); the three-dot diff is 20 files, all the branch's own (17 modified on main, 3 added: the field-figures harness, its verdicts fixture and the delivery row). Claim files, VERSION, RELEASE_NOTES and manifest are identical to origin/main. `git merge-tree --write-tree origin/main HEAD` is clean. The only hand resolution in the range is the Relay union, which is sound.
5. Body: `## Head` names this head; `## Red checks` owes nothing new, since no check has concluded red at this head.

## Findings

- The body's `## Head` keeps a stale second paragraph naming `660332d10` and says the merge base "stays 8fcaf47e1"; the merge base is now 279cb497f. Cosmetic, the figures in it are unaffected. Carry: dismissed: the first paragraph names the live head correctly, and the three-dot file list it describes is still 20 files.
- The four seat-mutant pins cloud_relay-8, cloud_relay-25, cloud_relay-26 and tick_loop-1 remain NOT RUN, as the previous verdict found; the two re-keyable ones (tick_loop-1, cloud_relay-25) and cloud_relay-8 are still owed a re-target. Carry: R10-FLY-RELAY-REVIEW-FF

## Evidence

- Self-tests at the head, Linux: carry_audit 313/0, bus 128/0 (the 14 macOS fails do not occur on Linux), tick_loop 26/0, cloud_relay 316/0 (ev/selftests.log).
- CI: `merge_train.py classify` returned WAIT with only `gate` pending, then `GREEN 9e7b016f71214991bbea0076f0d83a891d68acc1 pending: none red: none` (rc 0) (ev/classify.log).
- Head at the end: ev/head_at_end.log.
- The standing-dispatch.md change needs the owner's approving review as code-owned policy; the body's `## Approval` says so. That follows this verdict.
