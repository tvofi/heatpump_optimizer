Roster for round 10, twentieth landing (after #2641, batch 19). It records what the roster seat was asked to write since batch 19: R10-FLOW-ARCH-PLANNER and R10-RECORD-API-BUDGET done, R10-LOOP-CPU's resume (PR 2632 at head 577ec62dbb35, in-progress), the re-homing of carries onto R10-FLY-YIELD-GUARD, R10-CI-LAYOUT-P2, R10-FLOW-JIDOKA and R10-FLOW-TOOLKIT-MODEL, and carries on R10-FLY-NO-FOOTERS, R10-FLY-OPENPR-ATOMIC, R10-FLY-RELAY-REVIEW-FF and R10-POLICY-LINT-FAMILY. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `8de7e22ac38cebf0badbaa204e392b306b368ccd`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `f38f91852ea0251a9043378f76f907794874b2be` is `2a3d7afe8f2a0fad941ce6da7d2e4f93cc67115b`, the roster tip as batch 19 landed it. The diff against `origin/main` is one file, `dev/programme/rosters/wave-r10-groups.json`, 23 insertions and 14 deletions (`git diff --stat origin/main...8de7e22ac` prints them) over 26 commits (`git rev-list --count origin/main..8de7e22ac` prints 26), each one `roster_edit.py` op pushed after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code 2a3d7afe8f2a0fad941ce6da7d2e4f93cc67115b f38f91852ea0251a9043378f76f907794874b2be -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote since is overwritten. The `removed` list below is empty.

## Figures

Measured with `B=origin/main`, `H=8de7e22ac`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 167 and 167 groups, none removed, none new and 11 changed (R10-CI-LAYOUT-P2, R10-FLOW-ARCH-PLANNER, R10-FLOW-JIDOKA, R10-FLOW-TOOLKIT-MODEL, R10-FLY-NO-FOOTERS, R10-FLY-OPENPR-ATOMIC, R10-FLY-RELAY-REVIEW-FF, R10-FLY-YIELD-GUARD, R10-LOOP-CPU, R10-POLICY-LINT-FAMILY, R10-RECORD-API-BUDGET). Groups by `resume.stage`, main then this head: done 88 then 90, in-progress 12 then 10, not-started 60 then 60, queued 6 then 6, absorbed 1 then 1. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s)`, and `python3 tools/audit/seat/ref_privacy.py --check` at `H` prints `0 refused`.

## Red checks

Read 2026-10-23 from `repos/tvofi/heatpump_optimizer/commits/f38f91852ea0251a9043378f76f907794874b2be/check-runs` (main's tip, 63 runs), failures, cancellations and timeouts only: five `rerun-stale-contract` runs, a check about re-run pull requests that this roster file does not touch. Checks at this pull request's own head are read by CI.

## Forward-carry

none

## Friction

none
