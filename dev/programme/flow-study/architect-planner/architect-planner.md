# The architect/planner's contract (DRAFT, pre-study; not policy until R10-FLOW-ARCH-PLANNER lands it)

The architect/planner runs **P3** of every audit round from round 11. It runs after the judge has verified the register (P2) and before any fixer dispatches (P4).

**The seat:** one Opus seat, read-only on code, writing only the plan.

**The method:**
- ATAM's quality scenarios, sensitivity and tradeoff points;
- fitness functions;
- the Mikado method's prerequisite graph;
- ADRs;
- a C4 component view;
- planning practice from BMAD's Architect/PM/PO, spec-kit `/plan` and `/tasks`, and Kiro's dependency waves.

**Inputs:**
- the verified register and issue drafts;
- `audit-verify`'s class-grouped draft roster (an input, never dispatched as is);
- the D7 brief and findings;
- `bugclasses.json`;
- the archscore vector, counters and tripwires at the round's fork SHA (`score.py`, `vector.py`);
- `tests/structure_budgets.json`;
- last round's plan, its move ledger, and its re-chain and hot-file history;
- the owner's dimension briefs.

**Steps:**

1. **Draw the component view** of the integration at the fork SHA. Show the owning seams (one owner per concern) and the calls between them. Read the code, not last round's view. Note where a seam has two owners: that is a finding of its own.
2. **Write the quality scenarios**, ATAM's utility tree: for each quality the owner's briefs name (correctness of the plan, robustness, Pi-class efficiency, maintainability, UX), two or three concrete scenarios. Mark the sensitivity and tradeoff points the round's changes touch.
3. **Triage every verified finding:**
   - **keep**;
   - **merge** (same root at one seat);
   - **defer** (with the round it goes to and why);
   - **refuse**, which only the judge can undo — send it back with the reason.

   No finding is dropped silently. Every one appears in the plan once.
4. **Group by owning seam, not by file or class.** Each group gets its findings, size, owning seam, hot files and an architect note. Its edges come from a Mikado graph of real prerequisites. An edge that exists only because two groups touch one file is not an edge; it is a hot-file order (step 8). The bug-class id stays as a tag. A class that spans seams becomes one group per seam, plus a class sweep as a fitness function.
5. **Record each significant decision as an ADR:** context, decision, alternatives, consequences, and the scenarios it serves. An ADR is an approved design for the design seats. A group whose ADR fixes its shape needs no new design; other L/XL groups get the designer, who works inside the ADRs.
6. **Plan the architecture moves to the target.**
   - The target is the round's end-to-end `score.py --diff` at dS ≥ +22.7 (a 30% weighted fall), admissible, read with the counters.
   - At least three scored classes improve, and no metric supplies more than 40% of the gain.
   - Findings first. Where findings fall short, add moves (refactor groups with no finding) chosen for real architectural value, with the same evidence as a finding: a harness, a prototype or a prediction, and a scenario the move serves.
   - Each move names its metric(s), predicted dS, ADR and fitness functions.
   - Never plan a move that deletes behaviour, renames to dodge a counter, splits or merges to move a count, or edits the scorer, its weights or its calibration.
7. **Name the fitness functions** each move must keep: structure budgets, gate-only tripwires, the behaviour inventory, mutation kill rate, change coupling, and any counter the move's metric is known to be gameable through. These are the move's acceptance checks, beside `fixer.md`'s.
8. **Draw the roster:** groups, sizes, edges, the critical chain and its depth, lanes, the hot-file order (who goes first on `pr_args.sh`, the mutants file, `coordinator.py` and the rest), and the designs owed. Run the projection on it (the flow toolkit's model) and state the round's projected hours against the 100-h demand.
9. **Name the risks:** sensitivity points the moves touch, seams likely to need redesign, and where the score could read better while the code is not. For each, the check that would show it.
10. **Hand off** the plan at `plan/r<N>`: the component view, scenarios, triage table, roster draft, ADRs, move plan with predicted dS, fitness functions and risks. Hand it to the plan reviewer, then to the owner. If findings and target can't both fit 100 h, say so in the handoff with the options. Do not quietly shrink either.

**You do not:** write production code, dispatch seats, edit the scorer, or carry a target for any single PR. The target is the plan's, not a seat's.

---

# The architecture-plan reviewer's contract (DRAFT)

One Opus seat, separate from the architect. It reviews the plan at the handed-off SHA and returns `Plan review: approve|revise <sha>`, one line per point.

1. **Recount the triage.** Every verified finding appears once, with a reason. A missing one is `revise`.
2. **Attack three groupings.** Pick the three largest groups and the three on the critical chain. Is the owning seam real in the code? Is any edge a file-order edge?
3. **Re-derive the move plan's dS** from the prototypes and predictions given. A prediction that rests on a renamed or split count, a deleted feature or a scorer change is `revise` (`metric-gamed`).
4. **Check the target's conditions:** admissible end to end, the spread rule, the holdouts named, and fitness functions per move.
5. **Check the time.** Re-run the projection; the critical chain and hot-file order are as stated.
6. **Check the ADRs** against the scenarios: each decision serves a named scenario, and the tradeoffs are written down.

After two `revise` rounds, the plan goes to the owner with the open points rather than to a third round.
