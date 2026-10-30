Design review: approve ce5ca88b

Reviewed: round-3 design note, BODY.md at handoff-body/r10-cop-gate-vent-r3 d25be122, with its Appendix A harness. The note says it measured at origin/main e77418f9. Round 3 of 3. The verdict line names ce5ca88b because the brief fixes that string. The design under review is d25be122.

Tree: I ran in a detached worktree at e77418f9, which was clean before and after. `custom_components/` has no diff from 1afdef88 (round 2's SHA) to e77418f9, so every line number carries. From e77418f9 to the payload head cf4f6b7a, `custom_components/` changes only in `manifest.json` and the card's version string (the stamp). No cited line moves.

## Reproduction

I extracted Appendix A verbatim and ran it as `PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py` under venv-ci at e77418f9. It exited 0 in 43 s.

- **The `_fold_flow_lift under a window` block is byte-identical to the note's.** All 19 lines match under `diff`, including:
  - the null rows: law a, b and a2 at k=0.00, each +2.496 [+2.483..+2.511];
  - the law (b) rows, which equal the null at both k;
  - the room lines;
  - the latch-set row (folds=0);
  - the priced rows at 25/40/50 °C.
- **The arm does not fix flow temperature by construction.**
  - Under law (a), `run_flow` computes supply as room + Q/UA_em + spread/2. The room comes from `room_series`, a first-order room that the window cools, so supply follows room air through the emitter.
  - Only law (b), the declared null, holds the curve.
  - Law (a) at k=0 equals law (b) at k=0 exactly. This is the steady-state check: room + q0/UA_em equals the curve.
  - The driver is the production `coordinator._fold_flow_lift` with `FlowCurveBias.observe_temps`. Every cycle passes the real gates (1440/1440 folds).
  - With the latch set, the driver folds 0 times. That is the positive control on today's freeze.
- **Shifts against the null.** Law (a) moves the 30-day mean `bias_k` by −1.66 K and −3.15 K. Law (a2) moves it by −0.08 K and −0.15 K. Every seed range is disjoint from the null's. The seeds are shared across arms, so these shifts are paired differences, not noise.
- **Round-2 blocks also match round 2's figures.**
  - Cop under a window: inferred 0.500 against a null of 1.056 [0.989-1.120]; flow and span 1.000.
  - Draw range: slope 0.996/1.003/1.009.
  - Buffer: g=0 at 1.0000; g=0.0005 1.2946→1.3058; g=0.002 2.1781→2.2233.
  - The cusum, learners and latch arms are unchanged. The latch reads ventilation, ventilation, None, None across consecutive cycles.

## Round-2 revise point

1. `coordinator.py:878` (`_fold_flow_lift`): **answered.** The note runs the arm the review specified, and by its own rule it reverses the lift: `:878` keeps the default freeze. I read `:839-905` at e77418f9. The freeze gate is at `:878`, before `curve_supply_temp` and `observe`. Leaving it untouched is correct and costs nothing in code. New failing-test row 5 pins the reversal, and the mutant (`:878` set to `room_air=False`) kills that row.

## The other round-2 answers still hold at this note

- **Point 1, the COP split on heat evidence (`:5017`, `room_air=not measured_heat`).** Re-read at e77418f9:
  - the freeze is at `:5017`;
  - the counter exit is at `:5040`;
  - the hoisted `heat_kw` read is at `:5048`.
  The order is unchanged, and the arm is reproduced.
- **Point 2, draw-range `power_frozen` (`:9760`) stays frozen.** The arm is reproduced and the site is unchanged.
- **Buffer and sysid.** The buffer stays frozen, settled from the topology. sysid keeps its abort; R10-CEILING-PROBE's design owns the abort's held-arm change, and this note leaves it there.
- **DHW callable and probe (`:3405`, `:9926`).** Both lift. The `:3405` wiring still passes `frozen=self._learning_frozen`, so a partial is the right shape.
- **`:1152`.** The note now drops the edit and its equivalent mutant. `:1152-1153` still reads `":" in frozen`, and `:6641-6642` still returns `"ventilation"` with no colon.
- **Sibling sites.** A grep of `_learning_frozen` across `custom_components/` finds exactly the note's 13 call sites (`:878`, `:1152`, `:5017`, `:5311`, `:5437`, `:5601`, `:8971`, `:9388`, `:9760`, `:9780`, `:9926`, `:10773`, `:10858`) plus the `:3405` callable. Every other hit is a comment or docstring. No module outside the coordinator calls it.
- **Seam.** One keyword on `_learning_frozen` that defaults closed. There is no new write path, and `learner_freeze_reason` and the ranking are unchanged.
- **Siblings in flight.** I read every open `design/*` ref.
  - Only R10-HEAT-METER (`read_heat_output_kw` gains a counter source) and R10-CEILING-PROBE (the sysid hold) touch this group's inputs.
  - Neither claims `_learning_frozen` or the `:5017` gate. See the carry below.
- **Cost.** One file in production (`coordinator.py`), about four edited lines, plus tests and a harness. That fits the group.

## Notes for the fixer (carried, not revise points)

- **Mutant `room_air=not measured_heat` → `False`.** The note says this mutant fails tests 3 and 2b. Test 2b may survive it: a stale thermal-power reading is refused by the input-health branch (`problem:key`) ahead of the vent branch, whatever `room_air` is. Test 3 kills it on its own. Claim only the kills the mutation run shows. Carry: R10-COP-GATE (item E)
- **R10-HEAT-METER makes `read_heat_output_kw` answer from a counter.** If it lands first, `measured_heat` at `:5017` becomes true on counter installs too. That stays consistent, because the counter path is already the lifted one. Re-run tests 1–3 on the rebased head, and keep the gate keyed on a fresh heat reading. Carry: R10-HEAT-METER (item E)
- Carry: dismissed: freeze reason resets each cycle (item 9)

## Minimal fixer brief

Give the coordinator's learner-freeze query a keyword parameter that defaults to treating room air as relevant. When a caller passes false, the query skips only the open-window (ventilation) reason. Every other reason, including stale or unusable inputs, boost and the pump signals, is reported exactly as today.

Use it in three places:
- The hot-water probe read passes false.
- The hot-water learner is handed the query pre-bound with false.
- The measured-COP fold passes "room air relevant" only when this cycle has no measured heat output. The fold's own hoisted heat reading supplies that answer, and the heat must be read before the freeze check.

Make no edit at the flow-curve bias fold (line 878) or the frequency fold (line 1152), which already lifts through its own colon predicate. Leave the remaining call sites on the default: buffer, house, lower floor, comfort, input health, the draw-range and indoor accuracy freezes, quiet comfort and system identification.

Write the failing tests first, in `tests/features.py`, with the vent latch set:
1. A counter install gets the span-open refusal, not the frozen refusal.
2. A measured flow heat folds.
   2b. A stale thermal-power entity, read through the cycle's real observation, still gets the frozen refusal. If the reading is not None when stale, gate on freshness and say so in the PR body.
3. An inferred COP stays frozen.
4. The hot-water learner runs, and the probe returns its value.
5. The buffer, draw range, system identification, house and lower floor still freeze, and the flow-curve bias takes no sample.

Commit Appendix A as the finder's harness under `dev/audit/harnesses/`, classified in `tests/closure.py`. Run it at both ends. The flow-bias and cop-window arms must not change, and the learners arm gains counter and flow-heat rows. Show one mutant per gate. No goldens are expected to move. Serialize with #2262 on the COP fold.

Seat tokens: not reported by the harness.
