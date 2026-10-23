Roster for round 10, nineteenth landing (after #2637, batch 18). It records two pull-request numbers the roster sync read from open pull requests: #2638 under R10-CI-LAYOUT-P2 and #2639 under R10-FLY-GH-READ-RETRY. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `2a3d7afe8f2a0fad941ce6da7d2e4f93cc67115b`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `4e38e7d7b3138b24c97e7d0fbea74965c1d43d62` is `3e7aaed31a1dd5478d7a9acd83ed16de6d9f23eb`, the roster tip as #2637 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 4 insertions and 2 deletions (`git diff --stat origin/main...2a3d7afe8` prints them) over 1 commit (`git rev-list --count origin/main..2a3d7afe8` prints 1, not a merge), pushed by `roster_sync.py --apply` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code 4e38e7d7b3138b24c97e7d0fbea74965c1d43d62 3e7aaed31a1dd5478d7a9acd83ed16de6d9f23eb -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote since is overwritten. The `removed` list below is empty.

## Figures

The 1 op, by commit (`git log --format='%h %s' origin/main..2a3d7afe8` prints it):

- `2a3d7afe8` `roster_sync.py --apply`: `resume.pr` 2638 recorded on R10-CI-LAYOUT-P2 (the policy_lint pre-pull-request, `fix/r10-ci-layout-p2-policylint`) and 2639 on R10-FLY-GH-READ-RETRY (its PR 2, `fix/r10-fly-gh-read-retry-2`); both groups stay in-progress. The sync ran over a pull-request list that omits #2514 and #2589, whose groups have further pull requests owed and must not read as done.

Measured with `B=origin/main`, `H=2a3d7afe8`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 167 and 167 groups, none removed, none new and 2 changed (`R10-CI-LAYOUT-P2`, `R10-FLY-GH-READ-RETRY`). Groups by `resume.stage`, main then this head: done 88 then 88, in-progress 12 then 12, not-started 60 then 60, queued 6 then 6, absorbed 1 then 1. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`, and `python3 tools/audit/seat/ref_privacy.py --check` at `H` prints `3 line(s) added since 3e7aaed31a1d judged, 0 refused`.

## Red checks

Read 2026-10-23 from `repos/tvofi/heatpump_optimizer/commits/4e38e7d7b3138b24c97e7d0fbea74965c1d43d62/check-runs` (main's tip, 127 runs), failures, cancellations and timeouts only: none. The one commit of this branch carries no completed failure other than `pr-contract`, which the contract excludes. Checks at this pull request's own head are read by CI.

## Forward-carry

none

## Friction

none
