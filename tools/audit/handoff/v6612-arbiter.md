_Requested by **tvofi**_

Bugs 1, 2, 3, 4 and 6 of tvofi's v6.6.12 report, and the pump-duty half of
bug 5. Closes nothing: no issue exists.

The report, in part: "The card warns that DHW only is on even though the mode
is DHW+Heating", "The mode is sometimes set by the integration to DHW+heating
even though DHW is needed and the house is too warm", "A warning is shown that
the temperature setpoint for space heating has been manually set to 25 degrees
instead of the intended 15 even though I have not touched it", "The warning
says optimizer is no longer active even though that switch is still on", and
"When the heat pump is turned off by the integration, the heat pump flips its
target temp to 25 degrees, which the optimizer incorrectly interprets as a
manual change, which turns the optimizer off".

**Before.** With Pump duty control at *Control*, any reading the arbiter could
not explain as its own write or as an ignored write counted as a person:
it switched Optimizer active off and raised a "changed by hand" repair. On
tvofi's install that fired with nobody touching the pump. The Tuya fork shows
a sent value for about 8 s whatever the device does, so a refused set-point
read as landed and then as changed. A restart lost the readings from before
each write, so any difference afterwards read as a person. A pump switched
off reports a set-point of 25 °C of its own. Separately, the next solve read
the arbiter's own DHW-only as "the pump cannot heat" whenever the record did
not match the last mode written (after a restart before the record loaded,
while the pump lagged a new write, after a write first read as ignored), so
the card warned "DHW only" and dropped every space slot (bugs 1 and 6). The
90-minute DHW-only lease counted idle steps in a house already above its
planned temperature and wrote Heating + DHW into it (bug 2). The state
listener was a plain function, which Home Assistant runs in an executor
thread, where `hass.async_create_task` is not safe (tvofi's log shows the
warning).

**After.** tvofi's ruling (2026-09-25): while Optimizer active is on, the
optimizer is the pump's one writer. A reading that differs from what it wrote,
past a 20 s echo window, is written back at once; one that still differs after
that rewrite raises the existing "does not hold a setting" warning and is sent
again every five minutes, and the first reading that holds clears it. Turning
Optimizer active off writes the baseline once and nothing after, which is how a
person takes the pump back. While the configured power switch reads off,
nothing is compared or written. Any of the arbiter's three modes (heating,
DHW-only, heating + DHW) is its own under control, so the solve never reads it
as a block. The DHW-only lease releases to Heating + DHW only when the room is
below the step's planned temperature. The listener is `@callback`. The
manual-change repair and its state are gone; a stored v6.6.12 stand-down clears
its old repair on load. The option description and docs/configuration.md say
the new rule.

The test stubs now refuse what Home Assistant refuses: `callback` tags the
function as HA does, and `async_track_state_change_event` raises unless the
action is `@callback` or a coroutine function (`tests/ha_contract.py` pins
both, `expect="both"` for `callback`).

## Head

a6b398d32e3208d6f1f27555077e30e360697f34. Merge base 67a0cb9816565113447bb54415989090706435b4. Four commits:
d9a46139 (own-writes and listener), dc26410e (power switch off), 13852148
(hold what it wrote, the ruling above) and a6b398d3 (the mutation ledger's
mark for the removed `foreign_change`).

## Mutation proof

Each production line replaced in `pump_arbiter.py`, the arbiter section of
`tests/features.py` run, file restored:

- echo window removed → FAIL "a differing reading inside the fork's echo
  window is not rewritten yet" (5 fails).
- warn on the first difference (`> 1` → `> 0`) → FAIL "a change the arbiter
  did not make is written back at once, and the optimizer stays on" (18).
- record kept on a difference (no rewrite) → FAIL the same check (13).
- miss count not reset when a value holds → FAIL "a later change over a
  rewrite that held is written back again, still with no warning" (2).
- retry not cleared when a value holds → FAIL "a write the pump does not hold
  is sent again after five minutes, and the first one that holds clears the
  warning" (1).
- power switch ignored → FAIL "a set-point the pump resets while switched off
  is not a manual change, and is written again once it is on" (1).
- stored v6.6.12 stand-down not cleared → FAIL "a v6.6.12 stand-down on
  record clears its repair on load, and unloading writes nothing" (1).
- `@callback` removed → the section dies with the stub's TypeError "is neither
  @callback nor a coroutine function".
- warm-house guard removed → FAIL "in a house above the plan's room
  temperature the DHW-only lease does not write Heating + DHW" (1).
- retry wait removed → FAIL "a write the pump never took is sent again at
  once, and warned about when that does not hold either" (2).
- baseline on switch-off removed → FAIL "switching the optimizer off writes
  the baseline once, then nothing over a person's setting" (2).

The earlier commits' own mutants (own-last-only, echo counted as landing,
lost prior after restart, pump-off) were killed at their commits; the rewrite
removed the code two of them mutated.

## Null control

The merge base's `pump_arbiter.py` and stubs under this branch's tests:
25 of 83 arbiter checks fail, and each names one of the reported
symptoms (the optimizer switched off, the arbiter's own DHW-only read as a
block, the lease writing Heating + DHW into a warm house, the listener not
`@callback`). At the head all pass. Null controls that pass at both ends: a
DHW-only mode blocks space heat in observe and with the optimizer off; a
cooling mode is never the arbiter's; a DHW-only lease below the planned room
temperature still releases at 90 minutes; with the pump on throughout, a 25
°C reading is written back at once.

## Figures

- 83 arbiter checks pass at the head, 25 fail at the base: the
  section of `tests/features.py` from `R.section("pump-duty arbiter` to
  `R.section("P5 — sysid`, run with `PYTHONPATH=tests/hastub`.
- scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift
  GOLDEN_REF=67a0cb9816565113447bb54415989090706435b4 ./tests/run.sh` at 13852148
  printed `MODE: SCOPED -- 24 script(s) run, 2 scoped out.` All ok but three.
  entities.py failed one check, "every mark still names a mutant this tree
  generates", on the equivalent mark for the removed `foreign_change`;
  a6b398d3 drops it, and `python3 tests/entities.py` then prints `ALL 1924
  ENTITY CHECKS PASSED`. optimality.py fails 1 of 84, "the production stop
  rule (ftol) buys a materially better plan", and fails the same way at the
  merge base (`python3 tests/optimality.py` at 67a0cb9: `1 of 84 OPTIMALITY
  CHECKS FAILED`), so it is not this diff's. stress.py was stopped and left
  to CI at tvofi's call.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

none. The defect reached a released version (v6.6.12), so a root-cause seat
beside this fix is owed by `defect-root-cause.md`; it is not done here.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code) https://claude.ai/code/session_01GkTHXz5AEFdwvcCLvpJSrY
