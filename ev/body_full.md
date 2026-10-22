Roster for round 10, ninth landing (after #2598). It lands four carries appended after #2598's head was frozen: two from #2580's merge verdict (bus comment 6335670563) and two from #2598's merge verdict (bus 15d0bf56). Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

`c818b4677192d9476555d6001a1b5d5d8842ea35` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2600.md`. The authored code head is `8da941ac344ab0987f59484614ef97ef2e693060`.

`bfc6096642d26c137665423e89a435d6de7c6470` merges origin/main `01cf1398a` into the authored code head `8da941ac344ab0987f59484614ef97ef2e693060` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

The authored code head is `8da941ac344ab0987f59484614ef97ef2e693060`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `01cf1398a9cfa3dcae5945221afd0c1dae9cf682` (the #2598 merge) is `4da10dbae84c7915488ce9fcd29240fc14750eb0`, the roster as #2598 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 8 insertions and 3 deletions over four commits, each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code origin/main 4da10dbae84c7915488ce9fcd29240fc14750eb0 -- dev/programme/rosters/wave-r10-groups.json` is the control: the roster on main equals the merge base, so nothing main wrote is overwritten. The program below prints `removed` empty.

## Figures

The four ops, one `append-carry` each, with their roster commits:

- `3093279db` `R10-ORCH-MACHINERY`: the #2580 carry on the beat's handoff job reading the hold file only through `cloud_relay.sh held <pr>` (rc 0 skip, rc 1 proceed, rc 2 refuse the pass).
- `c4e214691` `R10-FLOW-ROSTER-FREEZE`: the #2580 carry setting the hold-file grammar precondition (plain PR-number lines only).
- `844c6c694` `R10-RCA-FRICTION-RESIDUE`: the first #2598 non-blocking carry (R10-RCA-FRICTION at stage done at 3976515a still holding its two carry entries).
- `8da941ac3` `R10-RCA-FRICTION-RESIDUE`: the second #2598 non-blocking carry (its `issues` hold seven numbers while the brief scopes five).

Measured with `B=origin/main`, `H=8da941ac3`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 147 and 147 groups, no group removed, none new, and changed `R10-FLOW-ROSTER-FREEZE`, `R10-ORCH-MACHINERY`, `R10-RCA-FRICTION-RESIDUE`. Carry counts after: 4, 31 and 2.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/01cf1398a9cfa3dcae5945221afd0c1dae9cf682/check-runs` (main's tip, just after the #2598 merge): no run is `failure`. Runs are `queued` or `in_progress` (a fresh push), and `rerun-stale-contract` shows 3 `cancelled`. `nightly-status` is not listed as red. Checks at this PR's own head are read by CI; this diff changes only the roster.

## Forward-carry

none

## Friction

none

