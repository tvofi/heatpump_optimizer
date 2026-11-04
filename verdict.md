Design review: revise 5ab827a8ed1fff0cea558199b71674708dfcc4c0 evidence-plan

Round 1. Base c3a279e3 = origin/main at review time, so the base and current main are the same tree. Design SHA unmoved.

## Revise points
1. design.md §6 "Goldens" (and §3 "Card"): the note names the solver claim file but not the card's. The card renders a "Why now" block from `why_now`, and the no-data text when the key is absent, so the block changes the rendered tree of the card states. tests/card_drift.mjs --list prints 44 states, all built from one plan payload (planStates, card_drift.mjs:82-121, payload from tests/plan_view.py), and card_drift requires byte-identical markup unless a state is named in tests/golden/card_claimed_drift.txt. The brief says every existing card golden claim stays unchanged unless it is named. Fix wanted: name the card footprint. Either list the states claimed in card_claimed_drift.txt with their direction (block added, or no-data line added), or state that the block mounts only where `why_now` is present and the no-data line sits in a place card_drift does not render, and say which. Also name docs/img/*.svg, which card_drift.mjs:23 says may then be stale.

## Checked and holding
- Seam (step 1): every tree claim in §1 holds at the base. classify_space_steps optimizer.py:1397; _build_result :2793 (space_reasons :2890); _Horizon :1965; SolveLimits.min_temp_floors :2098; _build_comfort_bounds :3746; _anticipatory_weights :2367; get_temp_bounds :1919; _fold_away coordinator.py:2234 (min(configured, target)); _mold_floor_series :8957; _build_plan_views :4558 ("views" in tests/seam_map.json:54); pump_arbiter._step_index :373; coordinator_private_reach budget 0.
- Dependency on R10-GRADE-DRIVERS: the note relies only on that seam. The coordinator publishes one payload key and the card renders from it alone. Computing the values on the solver path is what this group's brief requires ("the solver path publishes a per-slot reasons output ... the coordinator puts it in the payload under one key"). The note names no second owner of driver publication.
- Shape (step 2): five codes, direction and signed percent share, no-data on absent key, plan byte-identical. Each matches the brief.
- Sibling sites (step 3): both min_temp_floors= solve sites (coordinator.py:6074, :11133) are named. space_reasons consumers are unchanged.
- Evidence (step 4): the failing test can fail at the base (no space_drivers). The null control and both perturbations are the brief's. The coord_* goldens capture the whole data dict (tests/golden.py:1018), and frozen now is START, the first plan hour (golden.py:59, :943), so those goldens do gain why_now and claiming them is correct. There is no finder harness: this is an owner report, and the note says so.
- Consistency (step 5): no open design/* claims _Horizon, SolveLimits, _build_result or _build_plan_views.
- Cost (step 6): one new module plus the group's listed files fits L.

## Routed
- decision: orchestrator. R10-ADVISOR-WHATIF (design/R10-ADVISOR-WHATIF bf62c545, not started, after []) also lists www/heatpump-optimizer-card.js and coordinator.py as hot, including the what-if solve path this note touches at coordinator.py:11133. §7 orders this group only behind R10-GRADE-DRIVERS. The serial order of these two groups is the orchestrator's call.

## Notes for the fixer
Carry: R10-WHY-NOW-WIDGET (item r1-a). §3 calls the weights "the same 'shares of one push' contract as envelope_drivers". They are not the same: envelope_drivers is [{code, points}] with points summing to grade minus mid-scale (coordinator.py:3130), while why_now weights are signed percents with |w| summing to 100. Correct that sentence. Reuse GRADE-DRIVERS' row and hover helper with a field mapping in its call, not a second row renderer (duplication_copies is ratcheted).
Carry: R10-WHY-NOW-WIDGET (item r1-b). §4 rejects the coordinator-side alternative because coordinator.py sits at its max_class_loc and class_excess_loc ratchet, yet the shape still grows HeatPumpOptimizerCoordinator (the _build_plan_views addition and away_floor_drop_c at two solve sites). The coordinator is the largest class, so it sets max_class_loc. Keep step selection and the WhyNow dict build in slot_drivers.py as one module function, so the coordinator adds one call per site, and name the coordinator payment in the body before pushing.
Carry: R10-WHY-NOW-WIDGET (item r1-c). The null control's "flat weather" must also hold hlf and solar flat over the 8 h lookahead, or the forecast term is not zero.
