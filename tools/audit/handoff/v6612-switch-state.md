_Requested by **tvofi**_

Bug 5 of tvofi's v6.6.12 report, the switch half. Closes nothing: no issue
exists.

The report: "After reboot. Away, boost DHW, optimizer active and boost space
heating are all on and can not be switched back off, they flip back on in a
few seconds."

**Before.** The four switches (Optimizer active, Away, Boost hot water, Boost
space heating) showed the coordinator's published payload, which changes only
when the refresh a toggle asks for has run its solve: 33 to 73 s in tvofi's
log. Home Assistant's toggle falls back to the entity's last written state
after about two seconds without a change, so a switch turned off flipped back
on in front of the user, and turning it off again looked like it failed.

**After.** Optimizer active reads the coordinator's live mode, Away its live
override, and the two boosts the held boost state they already read; every
turn-on and turn-off writes the switch's state as soon as the action lands.
The toggle stays where it was put. Who switched the four on in the first place
is not in the log and has no Logbook entry; the pump-duty stand-down this
report also describes is fixed in the arbiter pull request.

The `Entity.async_write_ha_state` stub records what each call would publish
(`ha_state_writes`), and the harness `FakeCoordinator` carries `mode` and
`_away_state`, updated by its set calls.

## Head

ecb7af8edda8c6eee273682e197518faf7d3dbf3. Merge base 67a0cb9816565113447bb54415989090706435b4.

## Mutation proof

Each of the eight `self.async_write_ha_state()` lines removed in turn, and
each `is_on` put back to the payload, `python3 tests/entities.py` run, file
restored:

- turn-on and turn-off state writes, one at a time, for Optimizer active,
  Away, Boost hot water and Boost space heating (8 mutants) → each FAILs
  "every switch turned off shows off at once, while the published payload
  still says on" or "and every switch turned back on shows on at once",
  naming the switch whose write was removed.
- Optimizer active's `is_on` read from the payload → FAIL "every switch
  turned off shows off at once, while the published payload still says on".
- Away's `is_on` read from the payload → FAIL the same check.

## Null control

The merge base's `switch.py` under this branch's tests and stubs: the two new
checks fail ("every switch turned off shows off at once, while the published
payload still says on" and "and every switch turned back on shows on at
once") and every other entity check passes. At the head all pass. The first
check's own control: the published payload is asserted unchanged after the
toggles, so the pass cannot come from a refresh.

## Figures

- `python3 tests/entities.py` with `PYTHONPATH=tests/hastub`: `ALL 1926 ENTITY CHECKS PASSED` at the head; the two new checks fail at
  the merge base's `switch.py`.
- scoped gate: `python3 tests/closure.py select --diff
  67a0cb9816565113447bb54415989090706435b4` prints `MODE: SCOPED -- 22
  script(s) run, 4 scoped out.` Each selected script was run directly with
  `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`, `env_drift.py --all` and
  `card_drift.mjs` against the merge base: all rc 0 except optimality.py,
  which fails 1 of 84, "the production stop rule (ftol) buys a materially
  better plan", identically at the merge base (`python3 tests/optimality.py`
  at 67a0cb9: `1 of 84 OPTIMALITY CHECKS FAILED`). stress.py was left to CI
  at tvofi's call.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

none. The defect reached a released version (v6.6.12), so a root-cause seat
beside this fix is owed by `defect-root-cause.md`; it is not done here.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code) https://claude.ai/code/session_01GkTHXz5AEFdwvcCLvpJSrY
