Design review: revise 65d571d655167a2df9c9ab54529f8d883ad2d23b class-open

Reviewed design/R11-OUTSIDE-START-APPROACH at 65d571d655 (ref unmoved at review start), against base d3d66c4040 and the heads the note reads (6f48176bb6, 6a4b37067e). Every `path:line` the note cites resolves at its named head. Both predecessors' pull requests have since moved (#3805 at a96d3f9ca1, #3835 at ee7df28bf3); the note's own revalidation section covers that.

## Revise points

1. class-open: axis "readers that compare the plan's shipped draw against the meter" is unenumerated (e.g. `coordinator.py:10062` at 6f48176bb6, where `_commanded_power()` becomes the accuracy sample's `predicted_power_kw`, which `delivered_ratio` (`accuracy.py:639`) turns into the defrost derate's inference at `coordinator.py:9939`). Over an entry, series D meters about 1.25 kW against a shipped 0.53 kW, a ratio of about 0.42; inside the frost band with no defrost sensor, that would read as a defrost loss. The note's sibling sweep (`delivered_space(`, `_shipped_and_received(`, `start_count(`, `edge_count(`) finds only the objective-side readers of the shipped draw. The shape keeps "shipped plan, asks, actuator writes: unchanged" and gives `accuracy.py` no line, although the hot list names it. Fix wanted: enumerate the axis by a rule: every `_commanded_power()` / `_commanded_split()` call site in `coordinator.py` (963, 5182, 5292, 8637, 9063, 9277, 10062, 10758, 10807, 10846 at 6f48176bb6) and `accuracy.plan_promise`'s cost (`accuracy.py:571`, shipped space x price). For each, say whether it reads the received draw, is gated off approach and ramp-down intervals by the new learner's age, or sits in a named residue category with its reason. One example: R11-SEAM-learners' `REASON_ASK_IGNORED` freeze on `Sample.DELIVERED_RATIO` (`learning_freeze.py:118` at 6a4b37067e) may already be that gate for delivered ratio, but only if `MeasuredCop.scale_response` reads ASK_IGNORED over an entry. Measure that; do not assume it. Add the matching failing case and null control under Evidence (series D's entry folded through `_settle_defrost` in the frost band, with no defrost sensor: no derate moves).

## Checked, no point

- Seam: one owner per concern. The new learner owns the evidence; `runs.py` owns the plan's received draw; `draw_range.fold`, `store.py`, `coordinator.py` and `optimizer.py` are callers only. No new write path into another module's state: the shipped level and the asks stay with their current writers.
- Shape against the finding: each of the brief's four questions is answered with a figure, and its null (series A 00:25 to 03:05, excess -0.009 kWh) is restated. Pricing the entry as received energy in the objective, not as a fee, prices it once: start and switch terms still read the shipped plan. No grader is changed inside the pull request.
- Evidence plan: failing case 1 fails today (the function and input do not exist). The mutation targets name the gates the shape adds. The harness named exists at base (`dev/audit/harnesses/r11_honest_starts_runs.py`) and is correctly disclosed as not the finder's: there is no finder harness for an outside report. "No golden moves, no claim line" is right for a learner with no evidence in any fixture.
- Sibling designs: design/R11-SEAM-learners (bee723ac4d) and design/R11-OUTSIDE-HONEST-DHW-RUNS (ce85b10049) are the overlapping ones, and both are ordered as predecessors. design/R11-OUTSIDE-HONEST-STARTS-RUNS (a63a2ca6cd) touches `runs.py` and `_shipped_and_received` as well; the note's harness arm sits in that group's harness, but it claims no seam that group owns.
- Cost: eight production files for an L. Routed as `decision: orchestrator` with a p1/p2 split proposed; no revise.

## Routed (no revise point)

- decision: owner, as the note states: `MIN_PAUSE` measured from the gate write; the grid report and power cap reading the shipped total.
- decision: orchestrator, as the note states: file count and split; the group's roster presence only on handoff/audit-r11-roster.

## Notes for the fixer

- The defrost-derate case under point 1 is the exposure; the accuracy panel's `power_ratio` and the plan-promise cost curve are the same axis. Carry: R11-OUTSIDE-START-APPROACH (item r1)

Seat tokens: the harness reports none for this seat.
