Carry 21: a hotfix group's branch runs a scoped prepr by default (owner instruction, tvofi 2026-11-09: "hotfixes should have aggressively scoped or no prepr"). The scope is decided once in `tools/pr/prepr.sh`, from the roster's class of the branch's group, and one line says so. A non-hotfix branch runs as before.

## Head

`2d030bdffb0634e826e9a0d9cd95f050bd127901`

## What changed, and which seam

- `tools/pr/gate_priority.py`: a new `is_hotfix` and a `--hotfix` flag. The roster lookup `derived_priority` already did is now one helper, `_rank`, that both read; `is_hotfix` is true only when `roster_lib.dispatch_rank` answers `RANK_HOTFIX`. `$HPO_GATE_PRIORITY` and `.gate-priority` are not consulted: they order the lease and say nothing about the group.
- `tools/pr/prepr.sh`: `hotfix_scope` runs before `REUSE` is read from `PREPR_SKIP_CODE`. On a hotfix branch it sets `PREPR_SKIP_CODE=hotfix` and `PREPR_SKIP_CLOSURES=1` for the variables that are unset, and prints one `hotfix scope` line. Everything a `PREPR_SKIP_CODE` run already kept still runs: merged-tree structure ratchet, ci predict on the merged tree, the transport, claims and body and contract checks, the carry check.

**Rule for an explicit caller value.** Each variable is judged alone. A value the caller set wins, set-empty included (empty means that part runs in full). When both are set the classifier is not asked at all.

**Why the roster key and not the `fix/r10-hotfix-*` topic pattern.** The carry named the pattern; the roster's class is the one the gate lease already trusts, so this extends that seam rather than adding a second string match. A roster read that fails answers "not a hotfix", so a failed read gives a full prepr, never a skipped one; a topic pattern would skip on a name alone. Alternative that lost: matching the topic in bash, which would disagree with `dispatch_rank` the first time a hotfix group used another branch name.

**Placement.** The brief put the step beside step 1b0. `REUSE` is read before step 1b0 and gates it, so the step sits just ahead of the `REUSE=` read; it still precedes step 1b, so a scoped run takes no heavy slot.

## Receipt, and the gate lease

- A scoped run writes no `hpo-prepr-receipt` (the existing `PREPR_SKIP_CODE` rule, unchanged here). On a hotfix branch `app_push.sh --reuse` therefore has no receipt of a full run to reuse; it takes the full path or a caller-set value. The receipt rule is not changed in this part.
- `tests/gate_lock.py`'s `_priority_cases` runs inside that file's own self-test, which prepr's `self-test` step runs; a scoped run skips that step (the verbose scoped run at the merge base printed no `self-test`, `heavy slot` or `gate priority` line), so the scoped run does not reach `_priority_cases`. That file is not edited here.

## Mutation proof

Each mutant re-created by hand in a checkout copy of the head, one at a time, and run against `bash tools/pr/prepr.sh --self-test` (the `gate_priority.py` one against `python3 tools/pr/gate_priority.py --self-test`):

    M1-class-pred: KILLED      (the roster predicate made always-true)
    M2-code-unset: KILLED      (the unset test on PREPR_SKIP_CODE dropped)
    M3-clos-unset: KILLED      (the unset test on PREPR_SKIP_CLOSURES dropped)
    M4-bothset: KILLED         (the both-set early return removed)
    M5-isHotfix: KILLED        (is_hotfix equality inverted)
    M6-scopeline: KILLED       (the scope line not printed)
    M7-order: KILLED           (the call before the REUSE read removed)
    NULL: SURVIVED             (a comment-only edit, the control)

## Null control

The null control for the carry is the non-hotfix branch: the arm `(hotfix) null control: a non-hotfix branch prints nothing and sets neither skip` passes at the merge base and at the head, and the full prepr is unchanged for it. An explicit caller value winning on a hotfix branch is its own arms (empty `PREPR_SKIP_CODE`, empty `PREPR_SKIP_CLOSURES`, both set). At the merge base the arms were red: 4 of the 6 new arms failed (`hotfix_scope: command not found`); the two null arms passed there because no step exists to misfire, which is the expected null-control answer.

## Figures

- `bash tools/pr/prepr.sh --self-test`: merge base before the step, 544 passed, 4 failed; head, 548 passed, 0 failed.
- `python3 tools/pr/gate_priority.py --self-test`: 17 checks, 0 failed at the head.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; budgets unchanged.
- A scoped run measured at the merge base, `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`, took 28 s of wall clock on this checkout and printed `merged structure` and `ci predict` as `ok`. The full-run cost named in the carry (about 40 minutes for the de.json hotfix) is the carry's figure, not re-measured here.

## Red checks

none

## Forward-carry

none

## Friction

none
