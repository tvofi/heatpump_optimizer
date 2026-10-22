Roster for round 10, tenth landing (after #2600). It appends two carries to the roster: one from #2600's merge verdict and one recording orchestrator decision O-1. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `e511768ec75add5847883bebe6a1fb674f827247`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `0b162da1adb73367eddcae1623cf5688422ad9a7` (the #2600 merge) is `b93ece169acfa8c97b469bbb18df06267aa14f6f`, the roster as #2600 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 4 insertions and 2 deletions over two commits, each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code 0b162da1adb73367eddcae1623cf5688422ad9a7 b93ece169acfa8c97b469bbb18df06267aa14f6f -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote is overwritten. The `removed` list below is empty.

## Figures

The two ops, both `append-carry`:

- `ece26d837` `R10-ORCH-MACHINERY`: source review/2600 (#2600's merge verdict). Its finding is that the writer and verifier group names in the group's earlier carry go out of date after the replan: R10-ARCH-DOCS-FIRST now writes and draws the machinery, and R10-ARCH-DOCS verifies it. The group goes from 31 to 32 carries.
- `e511768ec` `R10-ARCH-DOCS-FIRST`: source orchestrator decision O-1 on the design note `design/r10-arch-docs-first` at `16954f0c`. `tools/site/build_docs.mjs` is in the group's scope for the one token-map read from `docs/site/docs.css` into the mermaid theme. `roster_edit` has no files op, so the decision is a carry; an overlap check reading only `files` must treat that file as touched by this group. The group goes from 2 to 3 carries.

Measured with `B=origin/main`, `H=e511768ec`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 148 and 148 groups, none removed, none new, changed `R10-ARCH-DOCS-FIRST` and `R10-ORCH-MACHINERY`. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/0b162da1adb73367eddcae1623cf5688422ad9a7/check-runs` (main's tip): no run is `failure`, `cancelled` or `timed_out`. Checks at this PR's own head are read by CI; this diff changes only the roster and one delivery row.

## Forward-carry

none

## Friction

none
