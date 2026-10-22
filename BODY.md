Roster for round 10, fourteenth landing (after #2613). It records three groups whose pull requests merged and marks one group in-progress while its fixer's second round is out. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `324b6d312fe337f9a3766d3d0adca6722e5b9bf3`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `4d407a35f5f5e7785d06bebf1e40f2ab9e02ff3b` is `d7e1f9fc06d02945c95ce6c14fcd17435ba45b24`, the roster as #2613 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 7 insertions and 7 deletions (`git diff --stat origin/main...324b6d312` prints them) over 4 commits (`git rev-list --count origin/main..324b6d312` prints 4), each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code 4d407a35f5f5e7785d06bebf1e40f2ab9e02ff3b d7e1f9fc06d02945c95ce6c14fcd17435ba45b24 -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote is overwritten. The `removed` list below is empty.

## Figures

The 4 ops, by commit:

- `2d755baab` `R10-FLOW-YIELD-PROBE` done at `a9db47846647a516fbdb544c55c59a416875309f` (#2579).
- `b767bae8a` `R10-FLOW-RELAY-HOLD` done at `50808a755ce300fac4b19b7cfe7f89c795b8387b` (#2580).
- `33f76c39d` `R10-PREPR-CAP` done at `f0724675ff079895f7af8756b342165137a344ed` (#2528).
- `324b6d312` `R10-CURRENCY` in-progress, not done: its fixer's round 2 is out.

Each merge commit is an ancestor of `origin/main` (`git merge-base --is-ancestor <sha> origin/main` prints rc 0 for all three). Before each group was set done, its brief and carries were read for an owed further pull request ("PR 2/2", "P2b", a follow-up): `R10-FLOW-YIELD-PROBE` (2 carries), `R10-FLOW-RELAY-HOLD` (3) and `R10-PREPR-CAP` (1) name none, and each has `after` empty. The done-before-reroute check read the bodies of the open pull requests #2612, #2524 and #2617 for the three group names: none carries to any of them (#2617's body is empty; the `Carry:` lines in #2612 and #2524 route to other groups).

Measured with `B=origin/main`, `H=324b6d312`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 151 and 151 groups, none removed, none new, and 4 changed (`R10-CURRENCY`, `R10-FLOW-RELAY-HOLD`, `R10-FLOW-YIELD-PROBE`, `R10-PREPR-CAP`). Groups by `resume.stage`, main then this head: done 73 then 76, in-progress 8 then 8 (`R10-CURRENCY` enters, `R10-PREPR-CAP` leaves), not-started 63 then 60, queued 7 then 7. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 47 file(s)`.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/4d407a35f5f5e7785d06bebf1e40f2ab9e02ff3b/check-runs` (main's tip, 55 runs), failures, cancellations and timeouts only: 6 runs of `rerun-stale-contract`, all `cancelled`. That workflow (`.github/workflows/pr-contract-rerun.yml`) shares one concurrency group per head with `cancel-in-progress: true`, so a superseded run at a head is cancelled by design (R10-FOLLOWER-DEBOUNCE, its header comment); none of the six is a failure of a required check. Checks at this PR's own head are read by CI; this diff changes only the roster and one delivery row.

## Forward-carry

none

## Friction

none
