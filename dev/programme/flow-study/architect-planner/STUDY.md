# Pre-study: an architect/planner seat for the audit programme, from round 11 (2026-10-21)

The owner asked for a pre-study of an architect/planner seat. The seat triages, groups and plans every verified audit finding from an architectural perspective before the fix phase begins. Its architecture plan is the input for the designers and for the orchestrator.

**The target:** the plan improves the architecture score by at least 30% across the programme, whatever the number of findings, in a way that genuinely improves the architecture and does not game the metric.

The draft contract is `architect-planner.md` in this directory. Section 6 shows where the seat sits in the audit programme. Section 8 lists the round-10 groups that prepare it.

## 1. Answer

- **The seat is worth adding, as P3 of every round.** It replaces today's P3, where the orchestrator hand-edits a draft roster grouped by bug class.
  - **Round time:** in round 10, file-order edges (one change merely touching another's file) cost 12–13 h before a mid-round re-chain removed them: the model gives 98 h against 86 h, and 104 h against 91 h at today's slip. Critical depth was 11 against 8. A seam-first plan gets those edges right before dispatch.
  - **Hot files:** the plan sequences them, where today a content conflict costs a code round. Three such rounds were lost on 2026-10-21 alone.
  - **Designers:** they inherit seams and decisions instead of inventing them per group.
- **The 30% target is feasible, but not from findings alone.** The seat must plan architecture moves beyond the findings, and the plan adds L/XL work to P4 (estimate in section 5). Net round time is between −12 h and +8 h against a round without the seat. It depends on how much of the move work sits on the critical chain.
- **Gaming is the real risk, and the tree already has the evidence.**
  - `tools/audit/archscore/ABOUT.md`: "The red team raised the score with 13 of 16 moves that left the architecture no better." and "It is a review trigger, never a target a seat is rewarded for moving".
  - Since the score was introduced, the tree's own history improved it by dS +74.6, yet the scorer rates that range **inadmissible**, because four metrics regressed on the way (section 3).
  - So the target is defined at programme level, admissible only, attributed per move, and checked against holdout measures the score does not contain (section 4). No individual seat is rewarded for moving the score.

## 2. The architecture score, as it stands (origin/main, 2026-10-21)

**How it scores** (`tools/audit/archscore/score.py`):
- S = Σ w·log2((ref+1)/(cur+1)) over 17 scored counts, where a lower count is better.
- dS(base → head) = Σ w·log2((base+1)/(head+1)).
- A change is **admissible** only if no scored metric and no gate-only tripwire worsens.
- **Weights:** five class metrics at 5.4–8.9, and twelve at the floor weight 1. Σw = 44.18. The weights are frozen (`tests/arch_score.py` `FROZEN_WEIGHTS`), code-owned by @tvofi, and graded with the base's scorer in CI.

**The current vector.** "Movable" means the metric is above zero and can still fall.

| metric | count | weight | movable |
|---|---|---|---|
| duplication_copies | 41 | 8.93 | yes |
| hub_solve_writes | 41 | 5.44 | yes |
| shared_inplace_writes | 19 | 5.44 | yes |
| untyped_payload_keys | 0 | 6.90 | no (at 0) |
| family_splits | 0 | 5.47 | no |
| coord_footprint | 2494 | 1 | yes |
| coordinator_multiassigned_attrs | 115 | 1 | yes |
| literal_clone_copies | 186 | 1 | yes |
| card_clone_copies | 108 | 1 | yes |
| layer_violations | 19 | 1 | yes |
| private_cross_module | 12 | 1 | yes |
| params_over_10 | 8 | 1 | yes |
| coordinator_private_reach | 2 | 1 | yes |
| dead_members, public_unused | 1, 1 | 1 | yes |
| import_cycle_modules, card_dead_definitions | 0, 0 | 1 | no |

## 3. What the programme has moved so far

`score.py --diff 399098f63 origin/main` (the score's introduction, 2026-10-02, to today) gives **dS +74.6109, WORSENS (inadmissible)**.

**Gains:**
- `untyped_payload_keys` 166 → 0: +50.98
- `duplication_copies` 88 → 41: +9.67
- `coordinator_private_reach` 83 → 2: +4.81
- `hub_solve_writes` 74 → 41: +4.55
- `params_over_10` 28 → 8: +1.69
- `dead_members` 5 → 1: +1.59
- `card_dead_definitions` 1 → 0: +1.00

**Regressions:**
- `private_cross_module` 9 → 12
- `literal_clone_copies` 178 → 186
- `card_clone_copies` 99 → 108
- gate-only `computed_attr_access` 31 → 32

Between the two round-10 stamps (v7.0.1 → v7.0.2): dS +0.0000. Since v7.0.2: +0.0023.

**Reading.** The programme can move the score a long way: the history equals a 69% weighted fall. But the gains were unplanned by-products of fixes, and four metrics drifted the other way unseen. This is the case for a planned, admissible programme-level target. The largest single gain, typed payloads, is spent, so the next 30% has to come from the remaining heavy metrics.

Prototype evidence for what is left:
- `dev/audit/rounds/round10/D7/arch-s1/REPORT.md`: three prototypes together dS +11.00, with hub writes 38 → 16. P1 alone **worsens** (+6.52, footprint +3) and needs P2/P3 with it.
- `arch-s2`: combined +7.02 (duplication 68 → 39, mostly landed since).
- `arch-s3`: 0.0000, all cells at the floor.

## 4. The target, defined so it can't be gamed

**Definition.** A 30% improvement means the weighted geometric mean of (count + 1) over all 17 scored metrics falls by 30%:
- dS ≥ log2(1/0.7) × Σw = 0.5146 × 44.18 = **+22.7**;
- measured `score.py --diff <round fork SHA> <main after the round's last merge>`, with the frozen weights.

Metrics already at zero contribute nothing, so on the movable metrics this means about a 41% weighted fall. (A movable-only definition would give +15.3. The study uses the stricter one, because it is what the score itself reports.)

**Conditions.** All must hold, or the target is not met, whatever dS reads.
1. **Admissible:** the round's end-to-end diff reads `IMPROVES`. No scored metric and no gate-only tripwire worsens across the round, not just per PR. The four regressions in section 3 would have failed this.
2. **Counters on:** dS is read with the red-team counters C1–C23 enabled. "A gain that appears only without the counters did not happen" (ABOUT.md).
3. **Attributed:**
   - every move in the plan names its metric(s), its predicted dS and the architecture decision record (ADR) it implements;
   - each merged PR's `## Architecture score` lines are reconciled against the prediction in a ledger;
   - a dS no planned move explains is reviewed as possible gaming (`fix-review.md` step 14, `metric-gamed`), not banked.
4. **Spread:** no single metric supplies more than 40% of the round's dS, and at least three scored classes improve. A round that only deletes clones is not an architecture round.
5. **Holdouts the score does not contain**, all of which must not regress:
   - `tests/structure.py`'s budgets;
   - the gate-only tripwires;
   - a behaviour inventory (entities, services, options and card features unchanged unless a finding removes one: ABOUT.md's "Attempt 09 deletes a working feature" has no structural counter);
   - the test suite's mutation kill rate;
   - change coupling from git history (how often files change together), measured before and after.
6. **Judged:** at round end, an architecture review re-runs the plan's quality scenarios, ATAM-style, on the new tree. The next round's D7 findings on touched seams are the lagging check.
7. **Seats are not rewarded for moving the score.** The target binds the architect's plan, not a fixer or reviewer. Fix review still asks only "is the change sounder?" (`fixer.md` step 17) and "is every number earned?" (step 14).
   - This reconciles the target with ABOUT.md's rule. ABOUT.md needs one added sentence saying so; that is part of R10-FLOW-ARCH-PLANNER.

**Conflict rule.** If the findings and the target can't both fit the round, the architect does not trade quality for score. It reports the gap and the options (more moves and more time, or a smaller target) to the owner at plan approval.

## 5. Impact on a round

| effect | estimate | basis |
|---|---|---|
| Seam-first edges | **−12 h** (98 → 86 h; 104 → 91 h at 2× slip) | file-order edges restored on today's roster (`tools/simulate.py` with the HOT_ONLY pairs added back): depth 11 against 8 |
| Hot-file conflicts | fewer code rounds lost (3 on 2026-10-21 alone) | the plan serialises seams on hot files |
| P3 duration | +4 h (template P3 ≤4 h → ≤8 h, including plan review) | one Opus architect seat plus one plan-review seat |
| Moves to reach +22.7 | about 3 class-metric halvings, plus about 30% off the floor metrics | halving hub writes (≈ +5.4), shared writes (≈ +5.4) and duplication (≈ +8.9), plus the floor metrics (≈ +4.6) |
| P4 work added by moves | about 3 XL-equivalents (≈ 36 h of target lead, much of it parallel) | arch-s1's +11.0 is about two XL groups (LIVESTATE, PARAMS-OWNER) |
| Net round time | **−12 h to +8 h** | depends on how many moves share the coordinator seam and so serialise on the chain |
| Tokens | about +2% for the seats; +10–20% for the added move groups | seat-hours; groups scale with the move count |
| Bugs introduced | down, lagging | architectural debt studies: the top five architectural debts cover 20–61% of maintenance effort and 8–25% of error-prone files (Xiao et al., ICSE 2016, abstract); round 10's findings were 40% architecture-dimension |

Every move group is L/XL, so the design seats apply. The architect's plan is their input, and an ADR the plan already contains counts as an approved design (exempt from a new design).

## 6. Where it sits in the audit programme

| phase | today | from round 11 |
|---|---|---|
| P0 baseline | baseline pinned for finders | + archscore vector, counters and holdouts at the fork SHA (the plan's base) |
| P1 find | `audit-find` workflow | unchanged |
| P2 verify | `audit-verify`: verifiers, judge, class sweep, issue drafts, **draft roster grouped by bug class** (decision 0012 move 5) | unchanged, except that the class-grouped draft roster becomes the architect's **input** and is not dispatched |
| **P3 plan** | orchestrator edits the draft roster; architect notes by hand on about 30% of groups | **architect/planner seat → architecture-plan review → owner approval** (contract in section 7) |
| P4 fix | orchestrator dispatches; design seats on L/XL (revision 12) | orchestrator executes the approved plan; designers design inside the plan's seams and ADRs; a move ledger tracks predicted against actual dS per merge |
| P5 stamp | `web-stamp` | + the round's end-to-end archscore diff and holdouts, checked against section 4, in the stamp record |

**Round-11 template** (SHADOW-PLAN §6): P1 ≤10 h, P2 ≤10 h, **P3 ≤8 h** (was 4), **P4 ≤56 h** (was 60), P5 ≤6 h, buffer 10 h. P4 gets the 4 h back through the seam-first edges.

**Decision 0012 move 5** ("grouped and fixed by bugclasses class id, one PR per class") becomes: grouped **by owning seam**, with the class id kept as a tag. A class that spans seams is split per seam, and the class's sweep becomes one of the plan's fitness functions. That is a policy change; it lands with R10-FLOW-ARCH-PLANNER.

## 7. The role, grounded in published practice

The contract draws on these sources (as fetched 2026-10-21; most method texts were reachable only as summaries):
- **ATAM:** a utility tree of quality scenarios, sensitivity and tradeoff points, risks.
- **Fitness functions:** "an objective integrity assessment of some architectural characteristic(s)", atomic and holistic (Ford, Parsons, Kua).
- **The Mikado Method:** plan non-trivial improvements as a graph of prerequisites, done leaf first.
- **ADRs (Nygard 2011):** context, decision, status, consequences; superseded, never edited.
- **C4 and arc42:** for the component view.
- **BMAD-METHOD:** Architect plus PM/PO with story sharding (54.4k stars).
- **spec-kit `/plan` and `/tasks`** (142.3k stars).
- **Kiro `tasks.md`:** dependency waves.
- **Claude Code's Plan subagent:** read-only research for planning.
- **Design-structure-matrix metrics:** decoupling level and propagation cost (Mo et al. 2016; MacCormack et al. 2006), for seam boundaries.
- **Goodhart countermeasures:** several metrics, holdouts, qualitative review.

The seat owes, in order:
1. A component view of the integration and its owning seams.
2. A quality-scenario tree.
3. Triage of every verified finding: keep, merge, defer or refuse, with a reason.
4. Groups by seam, with sizes, edges from a Mikado prerequisite graph (never file order), and an architect note each.
5. One ADR per significant decision.
6. A move plan reaching the section-4 target, with predicted dS per move.
7. Fitness functions per move.
8. The critical chain and hot-file order.
9. The risks.

A separate plan reviewer attacks the plan before the owner approves it.

## 8. Preparing it in round 10

Two groups land the role before round 11's P3; neither is on round 10's critical path:
- **R10-FLOW-ARCH-PLANNER (policy, M):** the architect/planner and plan-review contracts in `dev/governance/roles/`; the `CLAUDE.md` role table; `orchestrator.md`'s P4 executes the approved plan; decision 0012 move 5 amended to seam grouping; ABOUT.md's sentence reconciling the programme-level target; the round-11 template. It merges after R10-FLOW-DESIGN-POLICY, which edits the same policy files.
- **R10-FLOW-AUDIT-PLAN (instrument, M):**
  - a workflow `audit-plan` that runs the architect seat and the plan reviewer between `audit-verify` and the fix wave;
  - a move ledger: per group, the predicted and merged dS per metric, and the round's end-to-end admissible diff;
  - the holdout check: structure budgets, tripwires, the behaviour inventory, mutation kill rate, and change coupling before and after.

  It reuses `score.py --diff` and R10-FLOW-TOOLKIT-MEASURE's flow metrics rather than re-implementing them.

## 9. Limits of this study

- The move-effort estimate rests on three prototype reports and on round 10's sizes, not on a costed plan. Round 11's findings are unknown.
- The −12 h comes from one roster.
- The literature figures are abstract-level.
- ABOUT.md records a calibration bar that "was not met and is not claimed". A 30% target leans on a score its authors call a review trigger, which is why section 4's conditions are not optional.
