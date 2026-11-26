# Revision 5 against revision 4: the D3 wave fold

Revision 4 is `cf9f1ee2e6`, with `DEVIATIONS-20261125.md` on top. This
revision triages one input and nothing else: the D3 wave judge's record,
`handoff/audit-r11-judge-D3` at `a826f55f8c`
(`dev/audit/rounds/round11/D3/wave-judge/JUDGE.json`). Its roster base is the
live roster, `handoff/audit-r11-roster` at `694d2fad07`, not revision 4's
draft. `build_d3_fold.py` is the whole change: it reads those two files and
writes `D3-FOLD.json` (every finding, its enclosing function, seam and group)
and the amended roster `dev/programme/rosters/wave-r11-groups.json`, which this
branch carries for the orchestrator to land on the roster branch. Every number
below has its command in `## Figures`.

## Triage

Every judged finding appears once, in `D3-FOLD.json`:

| verdict | disposition |
|---|---|
| verified or weakened | keep, into the group of the seam that owns its enclosing function at the wave baseline (`groups`) |
| merged by the judge | merge, into the canonical key the judge names (`merged`) |
| unreproduced | refuse, back to the judge with the Linux x86 re-take the judge owes (`refused`); the re-take is a carry of `R11-SEAM-tests` |

The judge's ten issue drafts are not filed. They cut by production file;
`coordinator.py`'s survivors belong to five seams (actuation, learners, input
boundary, cycle, persisted store), so the cut here is by seam
(`architect-planner.md` step 4). Seam of a function: the module's row in
`COMPONENTS.md`; for `coordinator.py`, the table `COORDINATOR` in
`build_d3_fold.py`, one row per function, assigned from what the function
does. That table is the part of this revision a reviewer can dispute row by
row.

## Groups

All are tests-only, class I1, issue #3755, fixer and reviewer on opus (none is
an architectural change), shape fixed by `ADR-011-survivor-pins.md`, so no
design is owed. Size is one rule, pins per pull request (`size_for`).

| group | state | size | seam | reads | after (added) |
|---|---|---|---|---|---|
| `R11-D3-PINS-solver` | new | XL | solver | `optimizer.py`, `dhw_planner.py` | `R11-OUTSIDE-START-APPROACH`, `R11-SEAM-cycle-reporting` |
| `R11-D3-PINS-sysid` | new | L | learners | `sysid.py` | `R11-SEAM-learners` |
| `R11-D3-PINS-fabric` | new | L | learners | `coordinator.py`, the fabric learners | `R11-ARCH-fabric-learner`, `R11-SEAM-cycle-reporting`, `R11-OUTSIDE-START-APPROACH` |
| `R11-D3-PINS-plant` | new | L | plant model | `thermal_model.py`, `defrost.py`, `flow_lift.py` | none |
| `R11-D3-PINS-money` | new | L | money | `price_model.py`, `tariff.py`, `grid_fee.py` | none |
| `R11-D3-PINS-actuation` | new | M | actuation | `coordinator.py`, the pump writes | `R11-SEAM-actuation-writes`, `R11-OWNER-FAULT-HOLD` |
| `R11-D3-PINS-inputs` | new | M | input boundary | `coordinator.py`, the readers | none |
| `R11-SEAM-cycle-reporting-p2` | fold, not started | S to M | cycle | `coordinator.py`, solve and payload | `R11-SEAM-actuation-writes`, `R11-SEAM-learners` |
| `R11-SEAM-store-p2` | fold, not started | S | persisted store | `coordinator.py`, three loaders | none |
| `R11-SEAM-tests` | three carries | L | test suite | none | none |

Why each cut is what it is:

- **Two learner groups.** `sysid.py`'s pins wait only on
  `R11-SEAM-learners`. The coordinator's fabric-learner functions are the ones
  ADR-007 moves out of the cycle, so their pins wait on
  `R11-ARCH-fabric-learner`; one group would hold the `sysid.py` pins behind a
  move that does not touch them.
- **`R11-SEAM-cycle-reporting-p2`, not `R11-SEAM-cycle-solve`.** Both are the
  cycle seam. `R11-SEAM-cycle-solve` is first on the binding chain; the part-2
  group is not started, not on a coordinator slot and off the chain.
- **`R11-D3-PINS-inputs` is new although `R11-SEAM-inputs-freshness` owns the
  seam and is not started.** That fold was built and projected: it moves
  closure later (`## Figures`, row "inputs folded"), because
  `R11-SEAM-inputs-freshness` holds a coordinator slot ahead of
  `R11-SEAM-cycle-solve`. A tests-only group takes no coordinator slot. If the
  owner prefers one group fewer at that cost, the fold is one row of `PLAN` in
  `build_d3_fold.py`.
- **No fold into a group with an open pull request.** A handoff freezes the
  branch (`fixer.md`); the register groups of the solver, plant, money and
  actuation seams are merged or in review.

## Edges and the hot file

An after-edge is added only where an open pull request rewrites the enclosing
function of a survivor the group pins (`d3_fnstate.py --between`, per pull
request in `## Figures`): the pin would otherwise be derived against code about
to change. `R11-OUTSIDE-HONEST-DHW-RUNS` and `R11-SEAM-learners` reach
`R11-D3-PINS-solver` and `R11-D3-PINS-fabric` through edges already on the
roster.

Files against the open pull requests:

- under `custom_components/`: none, by ADR-011 part 1;
- `tests/mutation_ledger/`: one new file per key, no shared file;
- `tests/guard_pins.py`: shared with three open pull requests (`## Figures`).
  Hot-file order: those three land first and a D3 group rebases. The edges
  above already put `R11-D3-PINS-solver`, `-sysid`, `-fabric` and `-actuation`
  behind the groups of all three; `-plant`, `-money` and `-inputs` have no
  edge and rebase if they open first. Full disjointness from the open pull
  requests is not available to any group that adds a check: ADR-011 part 2
  states what a new script per group would cost instead.

## The judge's carries

| carry | destination | why there |
|---|---|---|
| class I1 (the wave's instances, and the root-cause analysis the class owes) | `R11-SEAM-tests`, carry | it holds #3755 on the roster and is carry-receivable (`carries-open`); the analysis is a root-cause seat's, beside the groups |
| R11-D3-JUDGE-GATE | `R11-SEAM-tests`, carry | a re-take of gates on a green-null Linux tree, one key per production file and gap kind; a cloud box. No D3 group waits on it: ADR-011 part 7 |
| R11-D3-JUDGE-LINUX (named in the record beside the three unreproduced findings) | `R11-SEAM-tests`, carry | same box as the re-take; a probe that moves on x86 becomes a carry of `R11-D3-PINS-sysid` |

## Objective (decision 0018)

By the grammar, a group that removes a verified `bug` finding is rank 1 on
`escapes`. Every receiving group but `R11-SEAM-store-p2` removes at least one
(the judge's `stop_rule_class`: high and medium are `bug`, low and nit are
`hygiene`); `R11-SEAM-store-p2` keeps its rank. Keys: `removes` is the group's
ids in `D3-FOLD.json`, `classes` is I1. Predicted dS is 0 for each (ADR-011);
the term they serve is `escapes`, and the holdout they move is the mutation
ledger's kill rate.

`plan_audit.py objective-check` was **not** re-run and `PLAN.json`,
`PROJECTION.json` and `OBJECTIVE-CHECK.txt` are unchanged, still revision 4's.
The check projects the roster the plan pins and refuses an open group with no
rank and a done group with one. Against the live roster the plan's block has
both (`## Figures`, "objective block against the live roster"), from the
deviations and merges since 2026-11-18, none of them this revision's. Adding
seven entries to a block that fails for other reasons would commit a record
that does not pass. Re-pinning the block to the live roster is a full
revision; this one supplies its D3 rows. The projection below is `replan.py`'s
directly, on both rosters at one start.

## Effect on the critical path and the fix-phase ETA

`replan.py` at the roster branch's tree, start 2026-11-26T09:00Z, on the live
roster and on three amended ones: **A** this revision; **A-count** the same
with one carry priced per pin (`--per-finding-carries`), because the size
model gives an XL of 131 pins the hours of any XL; **B** the option below.

| | closure | wall | binding chain | critical path |
|---|---|---|---|---|
| live | 2026-12-04T22:01Z | 205.02 h | `R11-SEAM-cycle-solve`, `R11-SEAM-product-text`, `R11-SEAM-docs` | 119.23 h |
| A | same | same | same | 119.23 h |
| A-count | same | same | same | 120.71 h |
| B | same | same | same | 119.23 h |

Closure and wall do not move in any of the three. The last D3 group
(`R11-D3-PINS-solver`) finishes 2026-11-30T00:15Z in A and
2026-12-01T09:42Z in A-count, against `R11-SEAM-docs` at 2026-12-04T20:01Z.
What does move, in A: CI minutes 4162.5 to 5287.5, batches 27 to 35, stamps 10
to 12, peak in flight 19 to 20 (the cap); seven new groups add 243.87 seat
hours by size and 340.30 by count. Four existing groups finish later, none on
the binding chain: `R11-SEAM-comments-tests` 24.75 h and
`R11-PRE-TOKEN-LEDGER` 14.62 h (slot contention: the three edge-free D3
groups take slots at the start), `R11-SEAM-cycle-reporting-p2` 14.60 h (its
fold) and `R11-SEAM-store-p2` 0.83 h (its fold).

`replan.py` does not model the standing dispatch rule (new groups only while
fewer than ten pull requests are open; deviation (c)). Fourteen are open, so
no D3 group dispatches yet, and the slot contention above is then the
orchestrator's order to set: the edge-free groups go behind the two it
delays. Seven new groups are seven more pull requests against that rule.

## Option B, for the owner: hygiene survivors to round 12

`--bug-only` keeps the high and medium survivors and defers the low and nit
ones to round 12 as hygiene. The grammar allows it (only a verified `bug`
deferred with no card is refused). Same closure; the D3 groups shrink
(`## Figures`), the last finishing 2026-11-29T22:38Z. It leaves the deferred
keys open under #3755 across the round's close. This revision plans A:
nothing is shrunk without the owner choosing it.

## Risks

- **A survivor already closed.** Functions holding some survivors differ on
  main from the baseline (`## Figures`); a merged group's new checks may kill
  them. ADR-011 part 4 returns those to the judge. The check that shows it:
  the fixer's probe run under the patch at its merge base.
- **The seam table is a judgement per function.** A wrong row puts a pin in
  the wrong group, not out of the plan; `D3-FOLD.json` is the list to check.
- **A pin that restates the formula.** Several hundred boundary pins invite
  it; the reviewer's check is ADR-011 part 5 with the patch applied.
- **Size by count hides hours.** A and A-count bracket it; neither moves
  closure.
- **Pin scripts' size.** If a structure budget bounds a test script at zero
  headroom, ADR-011's consequence applies; none was found by key name in
  `tests/structure_budgets.json`, which is not a measurement of every row.

## Figures

All at `handoff/audit-r11-judge-D3` `a826f55f8c`, `handoff/audit-r11-roster`
`694d2fad07`, `origin/main` `e91329c2c2`, wave baseline `92d38ecb64`.

Fold, `python3 -I dev/audit/rounds/round11/PLAN/build_d3_fold.py --judge <JUDGE.json> --roster <live roster> --out-roster R --out-fold F`:
judged 426, placed 401, merged 22, refused 3.

| group | survivors | high | medium | low | nit | carries added |
|---|---|---|---|---|---|---|
| `R11-D3-PINS-solver` | 131 | 0 | 23 | 107 | 1 | |
| `R11-D3-PINS-sysid` | 62 | 0 | 8 | 54 | 0 | |
| `R11-D3-PINS-fabric` | 47 | 0 | 10 | 37 | 0 | |
| `R11-D3-PINS-plant` | 46 | 0 | 16 | 30 | 0 | |
| `R11-D3-PINS-money` | 40 | 0 | 10 | 30 | 0 | |
| `R11-D3-PINS-actuation` | 23 | 3 | 6 | 14 | 0 | |
| `R11-D3-PINS-inputs` | 23 | 1 | 9 | 13 | 0 | |
| `R11-SEAM-cycle-reporting-p2` | 26 | 0 | 12 | 14 | 0 | 17, one per function |
| `R11-SEAM-store-p2` | 3 | 0 | 0 | 3 | 0 | 3 |
| `R11-SEAM-tests` | 0 | | | | | 3 |

Strata of the gate re-take (production file by gap kind, non-empty): 32, the
`strata` key of `D3-FOLD.json`.

Option B, the same command with `--bug-only`: placed 98, deferred 303; sizes
solver M, plant M, the other five new groups S.

Functions against the baseline, `python3 -I dev/audit/rounds/round11/PLAN/d3_fnstate.py dev/audit/rounds/round11/PLAN/D3-FOLD.json origin/main`:
same 328, changed 53, gone 0, at module level 20.

Open pull requests, `gh pr list --state open --json number --jq length`: 14.
Each one's rewrite of pinned functions,
`d3_fnstate.py D3-FOLD.json --between $(git merge-base origin/main pull/N/head) pull/N/head`:

| pull request | group | survivors in functions it rewrites |
|---|---|---|
| 3907 | `R11-OUTSIDE-START-APPROACH` | solver 28, fabric 17, sysid 33, cycle part 2 1; beyond 3835's head (`--between pull/3835/head pull/3907/head`): solver 28, fabric 2 |
| 3835 | `R11-SEAM-learners` | sysid 33, fabric 16, cycle part 2 1 |
| 3805 | `R11-OUTSIDE-HONEST-DHW-RUNS` | solver 18 |
| 3845 | `R11-SEAM-cycle-reporting` | solver 6, fabric 2 |
| 3897 | `R11-SEAM-actuation-writes` | actuation 2, cycle part 2 1 |
| 3872 | `R11-OWNER-FAULT-HOLD` | actuation 1 |
| 3869, 3870, 3874, 3882, 3883 | | 0 |

3902, 3903 and 3908 change no file under `custom_components/`. Open pull
requests touching `tests/guard_pins.py`
(`gh pr list --state open --json number,files`): 3835, 3897, 3907.

Projections, `python3 -I tools/plan/replan.py --roster-file <roster> --start 2026-11-26T09:00:00Z --out <plan>`,
reading `summary` and `binding`: the table above. Inputs folded (the `inputs`
row of `PLAN` pointed at `R11-SEAM-inputs-freshness`): closure
2026-12-05T01:56Z, wall 208.93 h, 3.92 h later than live.

Objective block against the live roster (open groups of `694d2fad07` absent
from `PLAN.json`'s `objective.groups`; groups it ranks whose stage is now
finished): 17 and 18.

`node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r11-groups.json`,
run in a checkout of `694d2fad07` with the amended roster in place: the live
roster reads 0 errors; the amended one is recorded in the commit message of
this revision.
