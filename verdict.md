Design review: approve 1442f9067ab3592ef5ed7c3389809539324c4ad1

Reviewed design.md at 1442f9067ab3592ef5ed7c3389809539324c4ad1 (note 2 of at most 3; parent 1a4d3c239d, the revised note), against b8f67a775137a8032d5c71b34ea64165c1d4613a. Commit 1, the contributor's text, is unchanged; the round adds §"Round 2: answers to revise points R1-R5", the answered owner decision (Carry 3) and the stated orchestrator assumption.

- Seam (step 1): holds as in round 1. `hold` (`pump_arbiter.py:1051-1072`) is the one place a readback drops a record. `_persist` (`pump_arbiter.py:1475-1483`) stores only `written`. The loop's cut bound, stop bound and record live on `ArbiterState`, with no new read path. Defrost comes only through one `ArbiterInputs` field, and the InputReader fallback is withdrawn (§2, fixer item 3).
- R1 (anti-windup): answered. The bracket rule in `hold` uses only the existing readback (`_observed`, `_differs`, `ECHO_GRACE_S`). A loop-caused cut adopts the reading, sets a one-sided bound and is exempt from `ISSUE_IGNORED`. A base-write cut keeps today's issue. Parameter 979 above the inlet is a recorded limitation with a docs line. The mutants named in R4 pin it.
- R2 (start versus hysteresis): option (a), a recorded limitation with a docs line. Option (b) is correctly not taken, because it needs a new read path. The self-caused stop is answered: lo = inlet - 0.3 K, plus a learned stop bound as a fallback, and the extra start is bounded and disclosed.
- R3 (600 s volatility): (i) the integration's polling is a precondition with a docs line. No HPO re-write, so fixer item 5 (`_write`'s equal-value skip) stays untouched. (ii) A 35.0 °C revert goes through `hold`'s path and resets the loop record. A mode revert is a recorded limitation, bounded by I2.
- R4 (fixture): it models start threshold at 0.5 K and at 2 K, the stop condition, the [979, return limit] clamp with readback, and the 600 s revert. k is cited to F6 as an install measurement. Mutants are added for the bracket, cut bound, stop bound, self-caused test and revert reset, and each must fail a repeat.
- R5: one line each for F3, F5 and F6 is present. The docs file is a hot file whatever the option.
- Evidence plan (step 4): the failing test fails at the base (open-loop re-anchor, `pump_arbiter.py:756`). The owner-reported route is used, and the synthetic fixture is named. The I1 null control must move for `return` with a power entity.
- Sibling designs (step 5): the open `design/*` refs whose notes name `pump_arbiter` are `r10-ceiling-probe`, `R10-COP-GATE` and `r10-livestate`. This note switches the loop off under `_experiment_kw` and at full level, and leaves `_full_draw_c` alone, so it claims no seam of the ceiling probe. COP-GATE is a learner consumer, and it is covered by §"Learners that read measured power". The GENERIC-HEAT-CURVE mode conflict is routed to the orchestrator, with the config_flow refusal stated as an assumption.
- Cost (step 6): the file list grew by the owner-mandated option (`const.py`, `config_flow.py`, `strings.json`, translations, `docs/configuration.md`, the config_flow golden, `tests/config_flow_steps.py`) and by `coordinator.py`. That still fits L. No split is needed.

## Notes for the fixer

- `_write` (`pump_arbiter.py:1113-1115`) skips any value within `SETPOINT_TOLERANCE` (0.3 K, `pump_arbiter.py:219`, via `_differs` at `pump_arbiter.py:1024`) of the record. So the loop's effective write quantum is above 0.3 K, not the entity's 0.1 K.
  - R2's lo margin (inlet - 0.3 K: one 0.1 K step plus a 0.1 K inlet rise) does not count this lag. While W is pinned at lo and the inlet rises, the written value can trail the inlet by more than the 0.5 K minimum hysteresis.
  - Item 1's fixture must drive the real `_write`. At 0.5 K hysteresis, if the fixture shows a self-caused stop, widen lo's margin by the tolerance, or force a write when lo binds. The stop-bound fallback alone does not meet "one start".
  - Carry: R10-WATER-SETPOINT-FEEDBACK (item 7)
- R4's stop-bound mutant relies on a fixture stop model at W + 0.1 K. Make that model an explicit repeat in item 1, beside the W + hysteresis model, so the mutant has a repeat to fail. Carry: R10-WATER-SETPOINT-FEEDBACK (item 8)
- §6 item 6 and §"Decision: owner" pair the `tests/golden/config_flow.json` move with a `tests/golden/claimed_drift.txt` row. Read `claim-files.md` first. Claim only a value-bearing fixture. If config_flow.json is re-recordable, both claim files stay byte-identical. Carry: R10-WATER-SETPOINT-FEEDBACK (item 9)
- R1's bracket is `[previous held value, new write] ± SETPOINT_TOLERANCE`. A cut within 0.3 K of the write is already "held" by `_differs`, so it never reaches the bracket. Pin both sides in one test:
  - a cut within the tolerance, where W keeps integrating and the next write is detected;
  - a cut beyond it, where the cut bound is set.
  Carry: R10-WATER-SETPOINT-FEEDBACK (item 10)

Seat token count: not reported by the harness.
