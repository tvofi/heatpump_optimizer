Roster for round 10, eighth landing (after #2588). It applies the roster operations queued while the roster branch was frozen: three new groups, one brief citation repair, issue wiring, two stage changes and three carries. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

`0c563c12e1ace15d5e2c73dc0a19f9fca1953f2b` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2598.md`. The authored code head is `5620151813e03a5916c375554dd57c977f6d8097`.

`1730aa8e8e1946648c08ef66870e24d3571be207` merges origin/main `16a8240f1` into the authored code head `5620151813e03a5916c375554dd57c977f6d8097` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`5620151813e03a5916c375554dd57c977f6d8097` is the authored code head, the tip of `handoff/audit-r10-roster`; its merge base with `origin/main` `16a8240f179d8a6a1ecaae2b284f6ec5a0f04eab` is `306a96d5f21f7876070d48c194fd4be99b64022c`, the roster as #2588 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 146 insertions and 13 deletions over 15 commits, each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code origin/main 306a96d5f21f7876070d48c194fd4be99b64022c -- dev/programme/rosters/wave-r10-groups.json` has rc 0, so main wrote nothing to the roster since the merge base and nothing is overwritten. The removed count in the program below prints 0.

## Figures

`B=306a96d5f`, `H=562015181`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{new:[$H|keys[]|select($B[.]==null)],removed:[$B|keys[]|select($H[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'`.

- Groups: 144 at base, 147 at head.
- New (3): `R10-RCA-FRICTION-RESIDUE`, `R10-TRAIN-OVERLAP-GRADE`, `R10-NIGHTLY-PYSPY-RETRY`, each stage `queued`.
- Removed: none.
- Changed (5): `R10-SCORES` (the brief's citation `coordinator.py:10293` becomes `coordinator.py:10309`, the envelope score's loss term in `_scores_view`; line 1083 is a different function, so the repair names 10309; this one error was the whole reason every push was refused), `R10-RCA-FRICTION` (done at 3976515a, five issues unwired), `R10-FLOW-DESIGN-POLICY` (done at 6077bf70e), `R10-FLOW-BOARD`, `R10-FLY-GH-READ-RETRY` (one carry each).
- `R10-FLOW-DESIGN-POLICY` done check, against 6077bf70e (#2586): `designer.md` and `design-review.md` exist; `orchestrator.md` dispatches the designer, the design reviewer and the fixer after `Design review: approve`; `fixer.md` step 17 says a departure is raised, not made; `fix-review.md` step 15 judges departures from the approved design note; `CLAUDE.md` rows 118 and 119 name both contracts; decision 0014 exists and 0012 is marked revoked by it; `policy_budgets.json` rose by the new files. All six checklist items met.
- `R10-RCA-FRICTION-RESIDUE` gains #2593. `R10-TRAIN-OVERLAP-GRADE` holds #2595's root-cause item as its one carry; no carry naming #2595 existed on `R10-POLICY-LINT-FAMILY`, so there was none to move.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/16a8240f179d8a6a1ecaae2b284f6ec5a0f04eab/check-runs` (main's tip, not this head): no run is `failure`; `Analyze (python)`, `coverage` and `fast (3.14)` are `in_progress`, and 14 `rerun-stale-contract` runs are `cancelled`. `nightly-status` is not red at that read. Checks at this PR's own head are read by CI; this diff changes only the roster.

## Forward-carry

none

## Friction

none

