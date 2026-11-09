R10-DISPATCH-AT-HANDOFF part 2: merge of origin/main into handoff/r10-dispatch-at-handoff-p2, resolving the one conflict in tools/audit/seat/cloud_dispatch.py. Behaviour unchanged by this repair; the original body's content (Carry 0, 4, 8, 11, 17, 18 work) stands.

## Head

e27484ffc9fb1f282974a35f02a470f657795e57

## Head note

Merge commit e27484ffc9fb1f282974a35f02a470f657795e57 merges origin/main 6457496aba7b1076b1ed60c374c5badafdf66fc1 into the previous tip 089f1da017e98a697a24e70c308f79beee9b8607. The one conflict, in the fix-review brief of cloud_dispatch.py, is resolved by union: main's merge-tree sentence (`git merge-tree --write-tree origin/main <head>`, block on main only on a conflict, never on a clean head behind main; commit bc59a13f6) plus this branch's `wait_ci` value (empty for a reviewer at the handoff, the full classify wait otherwise). Main's first merge (19865e5a8) and a second one (main moved during the repair, 6457496aba7b1076b1ed60c374c5badafdf66fc1) both applied; the second auto-merged.

## Mutation proof

Run on the merged cloud_dispatch.py, self-test restored after each:
- Main-side mutant: `block on main only when that reports a` changed to `block on main always, even when that reports a` fails "the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main"; so does dropping `origin/main` from the merge-tree command.
- Branch-side mutant: `subj_key = topic if at_handoff else pr` changed to `subj_key = pr` fails "a reviewer at the handoff returns on probe/revt-<topic>-<nonce8> with the subject `verdict <topic> <head>`".
- A cosmetic mutant (`"\n"` to `""` in the at-handoff wait_ci) survives: that value is whitespace, pinned by no check; stated, not claimed killed.

## Null control

The unmutated merged file: `python3 tools/audit/seat/cloud_dispatch.py --self-test` prints "146 checks, 0 failed". `git merge-tree --write-tree origin/main HEAD` exits 0 at the head before the push.

## Figures

- `python3 tools/audit/seat/cloud_dispatch.py --self-test`: 146 checks, 0 failed.
- Self-tests of every instrument the branch changes (three-dot `git diff --name-only origin/main...HEAD`), run at the first merge head: bus.sh 168/0, body_patch.sh 109/0, cloud_relay.sh 400/0, pr_args.sh 198/0, review_packet.py 78/0, roster_lib.py 67/0, open_pr.sh rc=0. The second main merge touched none of them (roster_sync.py only added lines).
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` was stopped by me at 76 KILLED, 1 SURVIVED (S14 pr_args.sh, an entry already on origin/main, not this branch's) before reaching this branch's added entries (cloud_dispatch-21..23, bus-16..18); not claimed.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` at this head: rc=0 (closures skipped), clean; origin/main unmoved since this run.

## Unpinned sites

None added by the merge; the resolution is pinned by the two mutants above.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Not yet given. This diff touches policy files (dev/governance/roles/fix-review.md, dev/governance/roles/standing-dispatch.md), all from the branch's original change; the merge adds none. It merges only on `@tvofi`'s approving review at its head (CLAUDE.md, "Where the policy is"). No approval is claimed here.
