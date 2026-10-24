_Requested by **tvofi**_

The root-cause seat `defect-root-cause.md` owes for the seven defects tvofi
reported against v6.6.12. It also carries the class barrier for bug 5, with the
two unfixed instances the class search found. No issue exists for these
defects, so the **Root cause** record is in this body (see Friction). The
paragraph under each defect is written to be pasted into that fix's own PR
body.

**Before.** The thermostat (HVAC mode, preset, on and off) and the away return
time read the published payload. The payload changes only when the refresh the
action asks for has run its solve (33 to 73 s in tvofi's log). So each showed
the old value after the user changed it, which is the switch defect of bug 5 in
two more entities. The switch fix pinned four named switches, so a fifth entity
action was free to repeat the defect.

**After.** The thermostat reads the coordinator's live mode, and the away
return time reads the live override. Each writes its state as the action lands.
`tests/entities.py` sweeps every entity every forwarded platform adds, through
the platform's real setup. An action with no row and no stated exemption fails.
Each row asserts three things: the payload is unchanged, a state write
happened, and the property shows the new value. `FakeCoordinator`'s live mode
now defaults to the real coordinator's own default (`auto`, `coordinator.py`
`self._mode: str = MODE_AUTO`) instead of `off`. One switch check depended on
the old default and is restated (see *A finding against the switch fix*).

**Stacking.** This branch is cut from `ecb7af8` (fix/v6612-switch-state's
fix commit), not from main. Recommended: merge it into the switch-state pull
request, so the class lands as one PR with its barrier and every instance. If it
lands as a separate PR, it waits until that one merges.

## Root cause, per defect

The class all seven share: **the only oracle for an external counterpart was a
double the implementer wrote from what the code needed.** `tests/ha_contract.py`
names this mechanism in its own docstring ("the stub was written from what the
code under test needed, which is exactly the shape that agrees with a wrong
implementation"). It exists only for the Python HA stub. v6.6.12 hit it at four
seams: HA core, HA's entity state machine, HA's recorder REST API, and the pump
behind the Tuya fork. No class in `audit-r8/bugclasses/classes.md` matches; P6
is its nearest neighbour (a fake coordinator supplying a key production never
writes).

### Bug 5: switches flip back on (fix: switch-state)

- **Cause, reproduced.** `switch.py` at 67a0cb9: `is_on` reads
  `coordinator.data`, and no action writes state. The switch branch's two
  checks fail with the released `switch.py`, and this branch's sweep fails on
  all eight switch actions there.
- **Process state: (a).** Nothing in the suite modelled "the payload lags an
  action". The `Entity` stub had no `async_write_ha_state`, so no test could
  observe a write. `ha_contract.py` states this limit itself: "a symbol upstream
  has that the stub does not model at all … nothing misses it".
- **Class search.** Every writable entity was checked. The thermostat has 9
  lagging actions (3 HVAC modes, 4 presets, on, off) and the away return has 1;
  the sweep printed all ten before this branch fixed them. `async_set_temperature`
  is exempt because persisting the option reloads the entry. `async_press` is
  exempt because a button has no state.
- **Countermeasure: built here** (the sweep). See the cost test below.

### Listener outside the event loop, found in bug 3's log (fix: arbiter)

- **Cause.** `pump_arbiter.py` `_listen._changed` at 67a0cb9 is a plain
  function. HA runs it in an executor, where `hass.async_create_task` is not
  thread-safe. Under the arbiter branch's stub, the released arbiter dies with
  `is neither @callback nor a coroutine function`. With `@callback` patched onto the
  released arbiter, the branch's `tests/features.py` still fails 24 of 3342
  checks (bugs 1 to 4 and 6); at the fix head it passes all 3342.
- **Process state: (c).** The contract process existed and was followed, and it
  produced a record instead of a barrier. `ha_contract.py` at 67a0cb9 files
  `homeassistant.core.callback` as DIVERGENT: "invisible to any lane here, none
  of which has an event loop" (#577). This is the class's second instance:
  `_on_power_event` lacked `@callback` in the v4.0.0 programme and was caught by
  review (`docs/plan-v4.0.0-program.md`).
- **Countermeasure: built by the fixer.** The stub `callback` now tags the
  function, and `async_track_state_change_event` refuses a sync function that is
  not tagged (`expect="both"`). Standing cost is one attribute check per
  registration. The remaining gap is a registration no test drives. All five
  current registrations are in setup paths.

### Bugs 3 and 4, and the 25 °C power-off reset (fix: arbiter)

- **Cause.** The released arbiter recorded a write as landed when the next
  reading matched. That reading is the fork's own 8 s sent-value cache
  (`tuya_heat_pump` `coordinator.py`: `_cache_timeout = 8.0` at :171,
  `_apply_sent_cache` at :677-690). So a set-point the pump refused read as
  landed and then as changed by hand. After a restart the prior readings were
  gone, and a pump switched off reports 25 °C of its own. Each of these stood
  the optimizer down.
- **Process state: (d).** Independent review exists, and it is built around the
  finder's harness (`fix-review.md`). A feature has no finder. The first review
  of #1588 says so: "No finder harness is committed for this feature"
  (`fix-helper/review-1588/VERDICT-r1.md`). So review ran the implementer's own
  fake pump, which applies each write only when the test sets it by hand
  (`_PaCoord.device`). The design had the missing requirements, but nothing
  carried them into acceptance:
  - P4 of `dhw-control/judge.md`: "a write counts as landed only when a device
    report taken more than 8 s after it, and after a real poll or push, agrees";
  - the Stage 0 on-device measurements (M1, M6 and M7);
  - M5, "Is DP 9 below 25 accepted?", left unverifiable.

  Neither the #1588 body nor its reviews carry P4 or an M-result. I found no
  waiver in the record I read (inferred, not proven absent).
- **Countermeasure.** tvofi's ruling (2026-09-25T19:09Z) removes the inference:
  while the optimizer is active it rewrites any difference, so an echo, a
  refusal or a reset can no longer stand it down. For the process, a policy
  change is proposed, not built (see the cost test).

### Bugs 1 and 6: the arbiter's own DHW-only read as a block (fix: arbiter)

- **Cause.** Ownership held only when the persisted record matched the last
  mode written. It did not match before the record loaded after a restart,
  while the pump lagged a write, or after a write first read as ignored.
- **Process state: (c).** P2 was implemented and tested, with its latch test,
  for the matching case only. The mismatch cases were not enumerated.
- **Countermeasure: none beyond the fix.** Under the ruling, any of the
  arbiter's three modes is its own while it controls, so ownership no longer
  depends on the record. The instance cannot recur in this module.

### Bug 2: the 90-minute DHW-only lease wrote Heating + DHW into a warm house (fix: arbiter)

- **Cause.** The lease counted idle steps and released regardless of room
  temperature.
- **Process state: (a).** The design's own rule is "a lease cap of at most
  90 min on `DHW`" (`judge.md` Stage 2). No rule said what a warm house does at
  the cap.
- **Countermeasure: none.** The cheapest detector was field use. The nightly
  replay runs the default config, where the arbiter is off, and it cannot model
  the pump's response to a write. Recorded, nothing built.

### Bug 7: card history (fix: card-history)

- **Cause, reproduced.** Nine card checks fail with the released card and pass
  at the fix. `tests/card_rig.mjs` `historyApi` at 67a0cb9 returns one list per
  requested id in request order, empty lists included, with no `entity_id`,
  and it ignores `significant_changes_only`. The card read the answer by
  position. HA drops empty lists and filters by default, so the real answer
  shifts every later series.
- **Process state: (a).** No contract covers the card's HA REST double.
  `ha_contract.py` covers only `tests/hastub`. This is the class's third
  history escape: #1286 shipped the view in v6.6.7, #1290 repaired it in
  v6.6.8, and tvofi reports it "has never worked as intended". Every release
  from v6.6.7 to v6.6.12 shipped it broken.
- **Countermeasure: built by the fixer** (the rig now serves HA's semantics).
  The remaining gap is that the rig is still a transcription. A captured real
  `history/period` answer would pin it; see the cost test.

## A finding against the switch fix

`ecb7af8` changed `OptimizerEnableSwitch.is_on` from the payload to the live
mode. It also set `FakeCoordinator.mode` to default to `"off"`, but the real
coordinator starts at `auto` (or the restored mode). Against that fake, the
existing check "with no coordinator data at all the switch reads off, not
crashes" stayed green while production behaviour changed: before the first
refresh, the real switch now reads on. That is the class again, inside its own
fix. This branch corrects the fake and restates the check to "…reads the live
mode, not crashes".

## Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock
per occurrence, over a release cycle.

- **cost(defect).** The v6.6.12 round used 89 min of fixer wall-clock (report
  at 18:35Z, handoffs at 20:04Z, in the thread "v6.6.12 card and mode bugs").
  On top of that: tvofi's own diagnosis in the thread, this seat, the review
  and merge seats, and field time with the optimizer switched off.
- **Entity-action sweep (built).** Its standing cost is 18 action runs inside
  `entities.py`, 0.007 s (see Figures). P(recurrence) is 1 escape
  plus 2 latent instances in one module family. The test is passed at any
  non-zero P.
- **Callback stub refusal (fixer's).** Standing cost is roughly zero, with 2
  instances in the record. Passed.
- **Real history answer for the rig (proposed, not built).** It needs tvofi to
  capture one `GET /api/history/period` answer from the install (browser
  devtools, about 5 min) as a fixture. After that the standing cost is one
  fixture comparison. P(recurrence): 2 detected escapes (#1290, bug 7) in the
  6 releases the view has shipped in. Passes if tvofi supplies the capture; otherwise record
  "no countermeasure: owner input unavailable".
- **Fix-review for feature PRs (proposed policy, needs tvofi's review).**
  Addresses state (d): when a PR implements a judge-ruled design and has no
  finder harness, the reviewer's harness is the design's P-items and on-device
  M-items, each traced to a test, a measured value or tvofi's explicit waiver.
  Otherwise the verdict is `blocked: design trace missing`. The standing cost is
  one table per design-implementing PR. dhw-control is the only such feature in
  the record I read, with 1 escape of at least 5 defects. Recommended, but
  marginal on frequency; tvofi decides.
- **Generic fake pump modelling the fork (not built).** After the ruling, no
  arbiter path infers intent from a reading. The remaining consumer, the
  ignored-write warning, retries and warns, so a misread costs one warning.
  Refused: P(recurrence) × cost is below the build and upkeep.

## Head

83c6dd67250b00d744f61993b30040666583ba5b, on `ecb7af8` (the switch-state fix). Merge base with main:
67a0cb9816565113447bb54415989090706435b4.

## Mutation proof

Each mutant is applied in a worktree at the head, `PYTHONPATH=tests/hastub
python3 tests/entities.py` is run, and the tree is restored:

- `switch.py` from 67a0cb9 → FAIL "every entity action publishes its own result
  at once, while the payload still holds the old one", naming all eight switch
  actions.
- datetime's `self.async_write_ha_state()` removed → FAIL, same check,
  `AwayReturnDateTime.async_set_value`.
- climate's `hvac_mode` read from the payload → FAIL, same check, the
  thermostat's mode actions.
- an unrowed `async_set_fan_mode` added to the thermostat → FAIL "every entity
  action has a row or a stated exemption".

## Null control

With this branch's tests and the switch fix's production code, the sweep printed
exactly ten thermostat and away-return actions, and nothing else failed that
does not also fail at `ecb7af8`. At the head, the sweep passes. It cannot pass by
skipping: it requires at least 12 action runs (it ran 18), and a platform
missing from `const.PLATFORMS` fails "the action sweep reaches every platform
the integration forwards". Each row asserts the payload is unchanged, so no pass
can come from a refresh.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py`: at `ecb7af8`, 3 of 1926
  checks fail; at the head, 3 of 1929 fail, the same three. They are the two
  HANDOVER `updated-for` ancestry checks, which a local clone off `main` cannot
  answer, and "the template arm turns the acceptance red…", an environment
  check. None of them touches this diff.
- The sweep's standing cost, 0.007 s, has no committed instrument. It was
  timed with `time.perf_counter()` around the sweep block, in a scratch copy of
  `tests/entities.py` that exits after the block.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff 67a0cb9816565113447bb54415989090706435b4`
  prints `MODE: SCOPED -- 22 script(s) run, 4 scoped out`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift
  GOLDEN_REF=67a0cb9816565113447bb54415989090706435b4 ./tests/run.sh`, under
  the `gate_lock.py` lease. Every script was ok, stress.py included, except
  two. optimality.py fails 1 of 84, "the production stop rule (ftol) buys a
  materially better plan", which fails the same way at 67a0cb9 (per both fix
  bodies). features.py raised `AttributeError: '_G8DtCoord' object has no
  attribute '_away_state'`. That fake of the away-return entity's coordinator
  carried no live state, and its check explained the payload's `or {}`. The
  fake now carries the live override and the explanation is restated. After
  that, `PYTHONPATH=tests/hastub python3 tests/features.py` prints
  `ALL 3331 FEATURE CHECKS PASSED`.
- `tests/typing_ruler.py --mypy`, on the pins in
  `tests/requirements-typing.txt`, prints `ALL 9 typing-ruler checks PASSED`.

## Red checks

none

## Forward-carry

The new class, "the only oracle for an external counterpart is a double the
implementer wrote", belongs in `tools/audit/briefs/D14.md` for round 9. That
file is policy, so the text goes to tvofi through the round-9 readiness pull
request (R2) instead of this branch. The proposed fix-review step belongs in
`tools/audit/briefs/fix-review.md` under the same approval.

## Friction

- `defect-root-cause: unclear: the Root cause section belongs on "the qualifying defect's issue", but these defects have none and CLAUDE.md's filing rule argues against opening one; recorded in this body.`
- `root-cause-brief: stale: root-cause.md says to read ".cursor/rules/defect-root-cause.mdc first"; that file is generated from .claude/rules/defect-root-cause.md, which is the source.`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01XQkb2K7Xcpm4KxSZRQ6EDx
