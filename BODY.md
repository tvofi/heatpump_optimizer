Root-cause record `dev/audit/rca/R11-RCA-ENOBUFS.md` for the hotfix #3840 (`fix/hotfix-brief-lint-maxbuffer`). It lands the record alone, no code and no policy file. The record's cause: each Node git reader carried its own `execFileSync` options and nothing tied them to the size of what they read, so the 1 MiB default overflowed when the tracked listing grew past it (1,033,586 bytes on main, 1,074,652 at the #3822 head). Process state (d): the process was sound and its precondition changed. Cost: 2 PRs reddened (#3822, #3824), 7 red CI runs, about 11 wall-hours. Decision: a recorded refusal of any countermeasure beyond #3840's shared `gitRead` (cost x recurrence is about zero per release cycle), with a revisit trigger at a 16 MiB listing or a second ENOBUFS reaching a PR it did not touch. Forward-carry to the planner: `tests/mutation_ledger/` (53%) and `dev/audit/` (34%) drive the listing size. No `bugclasses.json` entry: one instance, no class. Closes: none.

## Head

The code head is `1fd53e32cf283d87ef03db5c80640bffae61e73d`, one commit adding `dev/audit/rca/R11-RCA-ENOBUFS.md` on `origin/main` `4ebd430fbf`. The record was measured at that main on 2026-11-21.

## Mutation proof

n/a: a record adds no production or check code, so there is nothing to mutate. Its claims are read from #3840's mutation proof and finder harness.

## Null control

n/a: nothing is measured by this change. The record's own null control is that `buffer_scan.mjs` fires 13 times on the healthy head, which is why a syntactic gate was refused (section 5, rung 3).

## Figures

none

## Red checks

none

## Forward-carry

The listing's size drivers, `tests/mutation_ledger/` and `dev/audit/`, are a D9 or D13 question for the round's plan, lands in `dev/governance/dimensions/D9.md`. Carry: dev/governance/dimensions/D9.md

## Friction

none
