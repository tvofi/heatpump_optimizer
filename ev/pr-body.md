Roster for round 10, eleventh landing (after #2601). It appends one carry to `R10-ARCH-DOCS-FIRST`, recording an owner request. Part of #201. It closes nothing by keyword and leaves #201 open.

The op's source is the owner's request (tvofi, 2026-10-22), verbatim: "For the docs PRs, I want a buymeacoffee button added to the top of the repo README and at the bottom of the web page, leading to buymeacoffee.com/rpgshcwb2tp".

## Head

`4649c7d531330970aa31b76afea523ae23d66b70` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2603.md`. The authored code head is `838178f8aa78b71b693e989799ea5e254f09a581`.

`b0006340a94a2096de6594586dd6a32d683002c4` merges origin/main `c409c9b18` into the authored code head `838178f8aa78b71b693e989799ea5e254f09a581` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

The authored code head is `838178f8aa78b71b693e989799ea5e254f09a581`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `c1e1967bcb75ebb59402696392c11c101358c5b5` (the #2601 merge) is `e511768ec75add5847883bebe6a1fb674f827247`, the roster as #2601 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 2 insertions and 1 deletion in one commit, pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code c1e1967bcb75ebb59402696392c11c101358c5b5 e511768ec75add5847883bebe6a1fb674f827247 -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote is overwritten. The `removed` list below is empty.

## Figures

The one op, `838178f8a` `append-carry` `R10-ARCH-DOCS-FIRST` with the text of the owner request above, extended with its delivery terms: a Buy Me a Coffee button linking `https://buymeacoffee.com/rpgshcwb2tp` at the top of `README.md` and in the footer of the docs site, rendered from in-tree assets in the tree's visual language with no hotlinked third-party image or script; any check reading the README head or the site footer is updated in the same PR; `R10-ARCH-DOCS` verifies both placements and the link target. The group goes from 3 to 4 carries. The stored text is the file's content (read back and compared byte for byte).

Measured with `B=origin/main`, `H=838178f8a`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 148 and 148 groups, none removed, none new, changed `R10-ARCH-DOCS-FIRST`. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/c1e1967bcb75ebb59402696392c11c101358c5b5/check-runs` (main's tip): no run is `failure`, `cancelled` or `timed_out`. Checks at this PR's own head are read by CI; this diff changes only the roster and one delivery row.

## Forward-carry

none

## Friction

none

