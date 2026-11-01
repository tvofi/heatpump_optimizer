Record PR in the R10-TRIAGE-S6 record lane (as #3094 and #3095): keeps #3048's pre-flight waiver note after its merged row, and drops the answered #2674 carry file. Title: "record: #3048 pre-flight waiver note; drop the answered #2674 carry file (R10-TRIAGE-S6)".

## Head

Merge commit 72c6eea33244b3fff2066758cd3989f567af6a1d (origin/main 407eb0cb38f3cd43e71f4ed7be1c23f80dc32cc1 merged into ba27089aebdebac42e72cd153363e08abecedde2; no rebase). Resolved dev/programme/delivery/3048.md: main contributed the merged row (first line, "merged 92588d5"), this branch the waiver sentence line verbatim. tests/closures.json auto-merged (carry-2674 entry pruned). dev/programme/delivery/3091.md retitled with the lane tag. Dropped as answered: nothing; both entries were checked and are still owed (see Figures).

## Mutation proof

n/a: record-only diff (delivery rows, a carry file deletion and its closures.json prune); no production line.

## Null control

n/a: no behaviour changes. Control for the drop checks: the same grep at origin/main for a recorded waiver returns nothing outside this branch's own line.

## Figures

- Waiver not recorded elsewhere: `git grep -n 5017455b origin/main -- dev/` prints no line; `git grep -n 5017455b origin/handoff/audit-r10-roster -- dev` prints no line.
- #2674 answered: issue #2674 state closed, completed (read via the GitHub issue API); `git grep -n carry-2674 origin/main -- tools tests dev/governance` names only tests/closures.json (pruned here); `git ls-tree origin/main --name-only dev/programme/carries/ | grep 2674` shows the file still on main; roster wave-r10-groups.json lists #2674 under a live group, so the carry file routes nothing.
- Pruning: `python3 tests/closure.py prune` reports 0 phantom entries at this head. `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh` at this head: rc=0, gate mode MODE: FULL (an unmeasured deleted file; CI re-records), CI PREDICT clean against 407eb0cb38f3, claim files byte-identical to origin/main. origin/main unmoved since that run.
- Delivery row dev/programme/delivery/3091.md stays in `git diff $(git merge-base origin/main HEAD)...HEAD`.

## Red checks

none: no check has run at the new head; the prepr.sh CI-predict step reports none predicted.

## Forward-carry

none

## Friction

none
