Design review: approve a1688d8d6a552a76b6b72ec6e56644d47d2b8134

Judged at f567988b519a8cb28d6f6ebdf2328fd120d028bd. The note's base 7c2f4c30ca is an ancestor of it; `git diff --stat 7c2f4c30ca f567988b51 -- custom_components` changes only manifest.json and the card's version line, so every line the note cites resolves at the judged base (coordinator.py:5315, :5343, :5345, :1193; accuracy.py:1221, :1310; draw_range.py:243, :326, :611, :701-704, :760, :819; sysid.py:1321, :1332; pump_arbiter.py:497).

1. Seam: the owners are the approved note's (archive/design/R10-DRAW-MAP-EVIDENCE 9aa450f55e). The routing stays in `draw_range.fold`, the efficiency refusal in `MeasuredCop.judge_floor`, and kind selection in `sysid.armable`. No new write path into another module's state.
2. Shape: every behaviour traces to a carry. C13 widens the hold re-derivation from the sweep to fit and probe; finding 108e8b09 names those two kinds as stale, so the widening is named.
3. Sibling sites: I reran the note's grep at f567988b51 and it matches the note's list: window readers draw_range.py:528/:577/:605 sit behind `observe`; ceiling readers :172/:186/:819 and sysid.py:1332 fall under r14; `judge_floor` has two callers (coordinator.py:5345, :1193); the remaining `.observe` hits belong to other learners. R11-OUTSIDE-SELF-SETTING-PUMP (#3662) and R11-OUTSIDE-HONEST-METERED-FLOOR (#3670) have both merged into this base, and the note re-cuts against both.
4. Evidence: the conflict sets match at f567988b51 under `git merge-tree --write-tree`: A conflicts in accuracy/coordinator/draw_range/store/features, B adds round4/D6 claims, F conflicts only in policy_budgets.json. B's own diff is separable: its tip 8c1508d9c1 is a merge of main 6abf88e617, with no tools/audit/seat file on its side. The harnesses are present: r10_cop_gate_band.py and draw_map_linearity.py on main, draw_map_rows.py at the A tag, d15_trace_budget.py at the F tag.
5. Overlap: both sibling designs that share the hot files have approve verdicts and are merged. No other open design/* note claims `fold` or `MeasuredCop`.
6. Cost: three parts in sequence (A, then B and F), each one porting an archived tag. This fits an XL group, and the note's alternatives show why no further split is needed.

Notes for the fixer:
- Point the null control's mutant at the sweep exclusion that the port adds to `draw_range.fold`, so that a sweep interval reaches `DrawRange.observe`. The guard at draw_range.py:701 in the base is the ceiling route (`experiment_s`), and flipping it does not perform the brief's perturbation. Show r10_cop_gate_band.py and the routing checks failing under that mutant and passing without it. Carry: R11-CARRY-DRAWMAP (item null-mutant-site)
- Item 1's dither null must include the sweep's first cycle. `ScaleProbe.owed_scale` (accuracy.py:1088) reads `dither.admitted` from the cycle before, so a row admitted just before the sweep can step the scale once inside it. Either show it byte-identical there or hold the step for an experiment cycle. Carry: R11-CARRY-DRAWMAP (item dither-first-cycle)

Decisions routed:
- decision: orchestrator. The brief says the S1-S4 confirmation comes before the first part is built ("ask before the first part"), but the note puts it before part A pushes. One of the two texts needs to change.
- decision: orchestrator. The note swaps the A/B part labels against the roster brief's parenthetical to match the approved note and the carries. The roster text is the orchestrator's to correct.
