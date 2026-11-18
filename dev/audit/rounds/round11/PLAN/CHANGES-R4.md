# Revision 4 against revision 3

Revision 3 is `fd5b78c0ff`; `REVIEW-R3.md` on `plan-verdict/r11` at `14f1e8a2b3`
returned `revise` (1 of 2). Each row answers a point of that review. Every hour
is `tools/plan/replan.py`'s at the pin in `PLAN.json` (start
2026-11-18T18:12Z), run on the draft, on revision 3's draft and on the roster
blob of `c7e683a6d4`; a positive hour is later. `CHANGES-R3.md` stands for
every row this file does not name.

| group, edge or move | before | after | objective term and rank reason | effect on in-flight work | hours |
|---|---|---|---|---|---|
| `R11-INTAKE-R10-RESIDUE` (review point 5) | rank 1 by card `E11-N-INTAKE-BUILDER`, first wave, "keep it running" | triaged (`INTAKE-TRIAGE.md`): 41 open carries, 6 kept and re-homed, 5 merged, 26 deferred, 2 refused, 2 dismissed. The group becomes `deferred`, unranked, holding 6 carries for round 12's architect | none: a holding group builds no read, so it keys no card | the fixer blocked at `handoff-wip/r11-intake-r10-residue` `a12c4c2ccc` is answered (a): its part 1/7 is not built; close the dispatch. Parts 2 to 7 are not fired. No design is owed | the L group's 46.17 h of seat work is not spent |
| `R11-READS-RESIDUE` (new, S, instrument) | carries 169 and 170 sat in the holding group | one group for the two open reads: the population levels of both axes, and the operation seed ledger its reader refuses | `coverage`, `unowned`, `operation`, `generality` and the other NO-READ terms the card names: rank 1 by card `E11-N-INTAKE-BUILDER`, keyed to the group that builds the reads | not on the roster: the orchestrator adds the row from the draft and dispatches a fixer. S, so no designer | finishes 20.87 h after the pin; the holding group finished at 46.17 h |
| edge `R11-PRODUCT-TEXT-PINS` after `R11-READS-RESIDUE` | no edge; the pins held a first-wave slot and the reads waited 23.77 h | the reads take the slot | rank 1 before rank 2 on a slot | neither is started, no ref for either | `R11-READS-RESIDUE` -23.77; `R11-PRODUCT-TEXT-PINS` +20.87; closure 0 |
| kept carries re-homed: 165 and 167 to `R11-SEAM-learners`, 118 to `R11-SEAM-tests`, 91 to `R11-SEAM-docs`, 171 to `R11-OUTSIDE-HONEST-DHW-RUNS` | in the holding group | each on the group owning its file | none keyed: a carry is not a register finding, so it moves no rank | `R11-SEAM-learners` and `R11-SEAM-docs` are not started. `R11-SEAM-tests`' design is approved (`7e60e1ba18`); carry 118 is pins with no shape and rides the fixer's brief. Carry 171 is a later part, never pull request 3709 | not priced: sizes unchanged, and `replan.py` prices by size |
| carry 157 (`mutant_run.py`) | in the holding group | deferred to `R11-CARRY-FIXER-CONTRACT` under P11, with an overlay now | none keyed; it protects every rank-1 fixer's mutation proof | the orchestrator adds one line to each fixer brief not yet handed off: a `--cmd` using `python3 -I` adds `-B` | 0 |
| finding `D5-s3-01` (review point 6) | triage `into` and `removes` of `R11-SEAM-money` | `R11-SEAM-kernel-layering`, in `PLAN.json` (triage, groups, `objective.groups`), `groups.json` and `COMPONENTS.md` | none: a hygiene finding. Money stays rank 1 on eight findings; kernel-layering stays rank 2 on two | none: pull request 3724 already claims it and 3726 does not | 0; dS 0 (below) |
| `R11-SEAM-cycle-solve` stage (review point 8) | `not-started` in the draft | `in-progress`, pull request 3738 (`fix/r11-seam-cycle-solve` at `1cf4d759c5`) | none: a re-sync, not a plan change | none | the projection prices it at its remaining part: it finishes at 24.57 h and not 59.87 h, and the coordinator chain behind it moves 11.48 to 35.1 h earlier; closure -11.48 |
| `R11-SEAM-tests`, `R11-SEAM-actuation-release`, `R11-SEAM-config` (review point 8) | "dispatch now; the design review is the first step" | each design is approved (`7e60e1ba18`, `4554fc2d66`, `45cf2dce82`, all 2026-11-18): dispatch the fixer | `escapes`: 1, 6 and 3 bug findings | the next step is the fixer, not a review | 0 |
| `R11-SEAM-card` (review point 8) | rank 1, first wave, unmentioned | rank 1, first wave, blocked since 12:32Z: `handoff-wip/r11-seam-card` `d9b28d8d57`, "fixer blocked before first edit", on a seat-environment hook; `inbox/r11-seam-card` holds a guard ruling | `escapes`: the group's bug findings wait on an environment, not on the plan | the orchestrator's to unblock, ahead of any rank-2 dispatch. The projection reads `in-progress` and prices it as running, so its 24.57 h finish is a lower bound | not priced |
| hot-file order, rank 1 before rank 2 (review point 9) | "delays none", true only inside `replan.py` | on a shared file the rank-1 pull request lands first and the rank-2 one rebases: 3726 (money) and 3728 (kernel-step) before 3724 (kernel-layering) on `currency.py`, `const.py` and `power_guard.py`; 3729 (ratchets) and 3736 (solver) before 3735 (ratchet-raise) on `tests/structure.py` and `tests/structure_budgets.json` | `escapes`, `lead_time`: a rebase is paid by the rank-2 group | 3724 and 3735 stay open and keep running; each re-runs `fixer.md` steps 2 to 8 after its rebase | one rebase each, not priced |
| outside-contributor groups (review point 10) | rank 2, undisclosed standing | rank 2 by the grammar only; their standing outside-contributor priority is unchanged, and no row of this plan orders one behind seam work | none | none: 3709, 3711, 3722 keep their turn | 0 |
| `R11-ARCH-fabric-learner`, `R11-ARCH-cycle-surface` (review point 11) | rank 2, last two coordinator turns | the same, and neither is cut at closure without an owner ruling: the floor rests on both with 0.28 of margin | the target is the floor; rank 2 orders them last, it does not make them optional | `R11-ARCH-fabric-learner`'s design is approved (`ebcc04b170`) | 0 |
| `D11-s1-06` overlay (review point 4) | "owes the in-round overlay", no seat | the orchestrator's: a caution line in the handover, never run `wt_sync.sh --self-test` outside a scratch clone until round 12 repairs it | none | none | 0 |
| the round's projection | wall 202.27 h, closure 2026-11-27T02:56Z at the 16:40Z pin | wall 190.78 h, critical path 139.68 h, closure 2026-11-26T16:59Z at the 18:12Z pin | `lead_time` p50/p90 35.1/162.87 h | none | closure -11.48 against either earlier roster at the same pin, all of it the cycle-solve re-sync |

## Rank-1 work, restated without the holding group

Over the 18 rank-1 groups common to the three rosters, at the 18:12Z pin:

| roster | last rank-1 finish | sum of rank-1 finishes |
|---|---|---|
| live, `c7e683a6d4` | 195.67 h | 1226.54 h |
| revision 3's draft | 161.72 h | 1192.59 h |
| revision 4's draft | 138.10 h | 1028.37 h |

Revision 3's gain was -33.95 h on the last finish and -33.95 h on the sum, all
of it `R11-SEAM-store`'s turn. Its stated -34.0 h and -48.2 h counted 14.22 h
on the holding group, which is withdrawn. Revision 4's further -23.62 h and
-164.22 h are the cycle-solve re-sync, a measurement and not a re-order. The
one re-order of revision 4 is the reads' slot: -23.77 h on
`R11-READS-RESIDUE`, the nineteenth rank-1 group.

## Started rank-2 groups, kept (unchanged from revision 3)

`R11-SEAM-kernel-layering` (18.15 h remain), `R11-SEAM-governance-text`
(21.53 h) and `R11-SEAM-ratchet-raise` (14.22 h) keep running. Stopping one
frees no rank-1 hour in the projection, and the hot-file row above is what they
owe rank-1 work.

## The dS target after the changes

The score target is the floor. No move, metric, ADR or prediction changed.
`D5-s3-01` is a docstring: the money move's `duplication_copies` +2.8741 and
the kernel-layering move's `layer_violations` +1.0 never counted it, so both
predictions stand, and the settlement now credits its removal to the group
that makes it. Planned +24.3811, floor +22.9801 against +22.7; without the
circ term +21.1938. The target is still not shown reachable by this plan
alone, and admissibility still rests on ADR-007's unmeasured `F`. Main is
`8751943e17`, as at revision 3: dS +0.0430 WORSENS.

The floor costs 35.53 h of critical path and 50.68 h of wall (projection A less
B). It delays no rank-1 group by more than 0.2 h.
