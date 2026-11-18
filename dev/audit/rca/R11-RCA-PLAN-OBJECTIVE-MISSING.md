# R11-RCA-PLAN-OBJECTIVE-MISSING: P3 ran under a contract main had already replaced, and the fix wave dispatched on it

This was written by the root-cause seat (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`) on 2026-11-18. It ran apart from
any fix. The figures were taken at `plan/r11` =
`819aa2e354b4e5baaf824b8568fd72bea8168a75` and `origin/main` =
`8751943e17ef4d3ec699e7859ae829b4528d8ce7`. The prototype and its run
transcripts are out of tree, under
`$HPO_STATE_DIR/r11/proto/plan-objective-gate/`.

## 1. The defect, reproduced

Run from `origin/main`:

    python3 tools/audit/seat/plan_audit.py objective-check \
      --ref 819aa2e354b4e5baaf824b8568fd72bea8168a75 \
      --plan dev/audit/rounds/round11/PLAN/PLAN.json \
      --register dev/audit/rounds/round11/JUDGE.json
      FAIL NO objective block: PLAN.json commits to one (0018, architect-planner.md)
    OBJECTIVE FAIL                                                   (exit 1)

`PLAN.json`'s top-level keys at that SHA are `round fork target_dS draft
components scenarios triage groups moves projected_dS critical_chain depth
hours risks holdouts`. It has no `objective` key, and the plan directory has
no `PROJECTION.json`. Nothing on the branch shows that `objective-check` ran.
`REVIEW.md` does not contain "objective", and neither does `PLAN.md`.

## 2. The starting facts, checked

| stated | measured |
|---|---|
| the plan was cut at fork `92d38ecb64` (2026-11-16 19:05Z) | `92d38ecb64` is the round's measurement fork, and `PLAN.json` names it in `fork`. The branch's **tree** is a different commit: `plan/r11` continues `handoff/audit-r11-register`, which was cut from main at `33b1e089bc` (2026-11-17 13:19Z, #3704) by the intake commit `28b864af6d` and never merged main again. |
| the objective clause arrived in `6142e16f7a` (11-17) and `objective-check` in `f51c5bde89`, both after the fork | Both are commits on #3703's branch. They were authored at 04:33Z and 11:45Z on 11-17, and #3703 merged to main at **2026-11-17 20:33Z** (`e3c75934c2`). That is after both the fork and the branch's base. The same merge replaced `.claude/workflows/audit-plan.js`, `plan-review.md` step 5 and `plan_audit.py`'s guide. `tools/audit/seat/plan_audit.py` exists at the plan SHA, but it has no `objective-check` subcommand. |
| `plan-review.md` step 5 asks for objective-check, and the third review never mentions it | Confirmed. The `plan-review.md` at the plan SHA still reads "5. **Check the time**: re-run the projection". The third review's point 12 executes exactly that wording ("time, PASS: `projection.py --order --rev1` re-run"). |
| the fix wave dispatched on revision 2, under mandate decisions, without checking the plan against the contract | Confirmed. `819aa2e354` ("decided open points applied", 11:05Z) is a commit made by hand outside `audit-plan.js`, after a `revise` verdict. The first fix-wave fixers were dispatched at 12:16Z: kernel-step, solver, ratchets and ratchet-raise. Eleven of the 27 groups had started by 15:09Z. |

The timeline in UTC:

1. 11-17 13:19: the register branch's base. 13:56: intake.
2. 11-17 20:33: #3703 merges the objective contract, its check and the workflow gate.
3. 11-18 07:28: fold. 07:35: verify record.
4. 11-18 08:30: P3 plan. 09:01: revision 1. 09:38: revision 2. 09:50: third review, `revise`.
5. 11-18 11:05: points decided under mandate and applied.
6. 11-18 12:16: fix wave.

P3 began **eleven hours after** main's contract required the block.

## 3. The cause

**The P3 stage executes the contract, workflow and instrument copies on the
round's branch, not main's.** `audit-plan.js` at both versions says "work in a
fresh worktree off `${branch}` … Read `architect-planner.md`,
`plan-review.md` … there". The branch was frozen at main's 11-17 13:19Z tree.
#3703 replaced all five P3 contract files on main at 20:33Z. The planner and
the three reviews then executed the old copies faithfully. The workflow that
ran was also the old one: main's version requires `objective` in the
`plan/moves` schema and an `objective_rc` of 0 before publishing, so it could
not have produced this plan.

Two further facts let the plan reach dispatch:

- the step that applied the decided points was a hand commit, which no check
  re-reads;
- dispatch has no check of the plan head against main's contract.

It is not a symptom of a wider product defect. `objective-check` itself is
correct: it refuses the plan at once, and it passes a plan that carries the
block (section 7).

## 4. The process state: (d)

The process was sound and its precondition changed underneath it.

- **Sound.** On main since 20:33Z, P3 refuses itself without the block:
  - `architect-planner.md` says "`plan_audit.py objective-check` passes before the push";
  - `audit-plan.js` throws on a non-zero `objective_rc`;
  - `plan-review.md` step 5 re-runs the check.
- **The precondition.** These hold only if the stage runs main's current
  contract. The stage reads the round branch, and that branch carried a
  contract main had replaced eleven hours earlier.
- **Nothing noticed.** No step compares a round branch's contract files with
  main's: not at stage start, not at the reviewer's verdict, and not at
  dispatch.

It is not (b). Each seat obeyed the text it was given. The third review's
point 12 is a faithful execution of the old step 5. A firmer instruction would
have reached the same stale copy.

It is not (a) either: the check existed. Its unit (the workflow run off
`${branch}`) did not reach this instance.

The countermeasure therefore makes the process notice the change. It does not
add a rule.

## 5. How far the class reaches

The shape is that a stage reads policy from a long-lived round branch while
main changes that policy. The candidates are:

- **The stages run off `${branch}`**: `audit-plan.js` (planner),
  `audit-verify.js` (judge, re-run runner, class sweeps). The reviewer reads
  the plan ref, so it inherits the same copies.
- **Contract merges between the branch's base and the end of P3**: three.
  - #3703 (20:33Z) reached P3. This is the defect.
  - #3688 (11-18 06:47Z) changed `proposal-triage.md`, `root-cause.md` and
    `defect-root-cause.md`. None of them governs a stage run on the branch.
  - #3679 (11-18 01:45Z) changed `audit-find.js` and `audit-verify.js`, and
    the register's fold landed after it (07:28Z). Its reach on round 11 is
    reported to the owner directly, because of that change's subject.
- **Over the whole audit window**, from the fork to 11-18 11:05Z (40 h), eight
  merges touched `dev/governance/roles`, `rules`, `decisions` or
  `.claude/workflows/audit-*.js`. That is 0.2 per hour. Over the register
  branch's 21 h life before P3 ended, about four would be expected. Three
  landed.
- **The nearest prior record** is `r10-rca-restore-base-skew.md`, where one
  run read inputs from two mains. It sat in a different unit (CI restore),
  with the same mechanism.

## 6. The cost test, with numbers

All hours are `tools/plan/replan.py` group durations on the plan's own roster
(`.claude/workflows/wave-r11-groups.json` at `819aa2e3`, cap 3). Measuring it
reproduces `PLAN.json`'s `hours` value of 175.63 h wall.

**Ranks.** No objective block exists, so each group's rank is derived the way
`plan_audit.derived_rank` does from the one key the register supplies: a
verified or weakened `bug` finding. That rank is a **lower bound** on rank 1,
because an escape, card or class key can only promote a group.

**The roster.**
- 27 groups and 900.1 group-hours.
- 18 groups (621.5 h) carry at least one verified `bug` and are rank 1.
- 9 groups (278.6 h) carry none and are rank-2 candidates.

**Started at the census (15:09Z): 11 groups, 353.2 h.**
- 8 are rank 1 (276.2 h).
- 3 are rank-2 candidates, 77.0 h:
  - `R11-SEAM-kernel-layering` (25.9 h, #3724);
  - `R11-SEAM-governance-text` (30.8 h, #3727);
  - `R11-SEAM-ratchet-raise` (20.3 h, #3735).
- No rank-1 group waits on any of the three through `after`, so projection B
  (the floor) drops all three.

**Rank-1 groups on wave 1 not yet started**: 105.3 h.
- `R11-SEAM-actuation-release` (35.1 h, the head of the critical chain);
- `R11-SEAM-config` (35.1 h);
- `R11-SEAM-tests` (35.1 h).

**What the missing check hides.** Main's `objective-check` refuses 13 verified
`bug` findings deferred with no card (`D0-s3-01`, `D11-s1-01` to `-06`,
`D11-s2-01`, `D11-s3-02` to `-04`, `D17-s1-01`, `D5-s8-07`). The plan defers
them to round 12 under the instrument freeze.

**The floor the plan never priced.** The figures come from the synthetic
block of section 7, at the pinned cap of 2:

| | projection A | projection B (floor) | difference |
|---|---|---|---|
| critical path | 139.68 h | 104.15 h | 35.53 h |
| wall | 243.53 h | 208.0 h | 35.53 h |

B drops 9 groups. `R11-SEAM-store`, a rank-1 group, finishes 33.95 h later
than it would on the floor.

**cost(defect) per occurrence.**
- Fix-wave hours at risk of re-ordering or dropping: **77.0 h started**, out
  of 353.2 h started, plus 35.5 h of projected closure the floor would recover.
- Re-running P3: the first draft to the final commit took **2.6 h**
  (08:30Z to 11:05Z).
- 13 deferred bug findings that need a card or a group.

**cost(countermeasure, recurring).** Measured with the prototype on this
machine:
- 0.9 s on a refusal;
- 9.0 s on a pass, because objective-check runs two replan projections;
- about 45 s a round when run once per plan head (five heads this round);
- about 4 min a round when run on every one of 27 dispatches without a cache.

There is also induced work. A legitimate drift refusal costs one merge of main
into the plan branch, an objective-check re-run, and a delta re-review of the
plan. Pricing that at about 1 h for each contract change that lands under a
round, as this round's three did, gives about 3 h a round.

**P(recurrence).** It was measured at 1 occurrence in 1 round that ran P3.
Section 5's rate of 0.2 contract merges an hour during the audit window puts
the precondition change in nearly every round. On that basis P is estimated
at between 0.5 and 1 a round.

**Verdict.** About 3 h a round against (77 + 35.5 + 2.6) h × 0.5 to 1, which
is 58 h to 115 h a round. The countermeasure passes the test by more than an
order of magnitude.

## 7. The countermeasure

The rungs, in order:

1. **Delete the stale source.** P3 reads its contracts, workflow and
   instrument from `origin/main` and only the round's data from `${branch}`.
   This is a change to `audit-plan.js` and `audit-verify.js`, and it removes
   the precondition for every stage run inside the workflow. It does not
   reach a hand commit made after the workflow, like `819aa2e3`, or a dispatch
   on a `revise` verdict. So it is necessary but not enough.
2. **Self-repair.** Merge `origin/main` into the round branch at each stage's
   start. This covers a change that landed before the stage, but not one that
   lands mid-stage or after the verdict.
3. **Narrow, plus a refusal at the consumer.** The plan head is the one thing
   every path converges on. A gate runs there at the reviewer's `approve` and
   at each fix-wave dispatch for a round-N group, once per plan SHA. Rungs 1
   and 2 cannot cover a hand commit or a dispatch outside the workflow; that
   is why the gate is also needed.

**The prototype** is `plan_objective_gate.py --repo <main checkout> --ref
<plan head> --round N`. It runs two checks, each against main and never
against the branch's copies:

- **DRIFT**: each P3 contract file whose blob at the plan head differs from
  main's, where main is the side that moved since the merge base. A file the
  branch itself edited is also refused, because contracts change on main.
- **OBJECTIVE**: main's `objective-check` at the plan head. The check counts
  as green only on rc 0 and the literal `OBJECTIVE PASS` line.

Each refusal prints its repair command. Its runs:

| run | ref | result |
|---|---|---|
| the defect | `819aa2e3` | `PLAN-GATE FAIL (drift 5, objective 1)`, rc 1, 0.9 s. The drift lines name #3703 for all five files. |
| fixed | `33fdfbf7`: `819aa2e3` with main merged, a synthetic block from `make_fixture_block.py`, and `PROJECTION.json` committed | `PLAN-GATE PASS (drift 0, objective 0)`, rc 0, 9.0 s |
| control A: drift repaired, no block | `1bebb5fe` (`819aa2e3` with main merged) | `FAIL (drift 0, objective 1)` |
| control B: block present, contract stale | `49643dba` (`819aa2e3` and the block, main not merged; objective-check itself passes) | `FAIL (drift 5, objective 0)` |
| control C: a tool with no `objective-check` | the passing fixture, read by the `819aa2e3` tree's `plan_audit.py` | `FAIL`, rc 2 refused, not passed |
| shadow, every P3 head on `plan/r11` | `2f6cfeee`, `6a73d86e`, `446a5aa9`, `8d7cce80`, `819aa2e3` | 5 of 5 FAIL |

What the controls show:

- **The units are independent.** Control A refuses only on the objective and
  control B only on the drift, so each unit carries weight on its own.
- **A skipped check is a refusal.** Control C shows that a crashed or
  outdated tool is refused, never passed.
- **The shadow run is limited.** Every plan head that exists is a defective
  head, because round 11 is the first round whose P3 owes the block. The
  "20 healthy heads" shadow therefore cannot be run yet. The only healthy
  head is the fixture, and the gate passes it.
- **The fixture is synthetic.** Its ranks come from bug keys alone, and its
  13 deferred bugs carry a placeholder card. It demonstrates the passing side
  and is not a plan.

**What is proposed, and who decides.**
- Rung 1, and the gate at the reviewer's approve and at dispatch
  (`pr_cap.py dispatch-gate`, or the dispatch step's own check), change
  tracked tooling and the P3 and dispatch contracts. Policy changes only with
  the owner's approval, and the instrument freeze sends tooling to round-end
  triage. Until then the overlay is to run the prototype by hand before each
  further round-11 fix-wave dispatch and before any plan approve.
- It addresses state (d): the stage now notices that its precondition moved.

**Owed to round 11 itself (the fix, not this seat's).**
1. Merge main into `plan/r11`.
2. Write the objective block.
3. Run `objective-check --write`, then the reviewer's delta.
4. Rule on the three started rank-2 candidates and the 13 deferred bugs before
   the next dispatch.
