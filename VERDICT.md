Fix review: blocked 5dea8264f2c8712c15725884d00b99eea5b48d24 mutation-vacuous: 10 survivors of tests/features.py in full: supply_hold._passes mode, economy, space boost, dhw boost; _ends_soon both exemption and one-tick window; supply_tick released and stale-plan retry guards; _action_supply economy; supply_switch entity guard

bus-nonce: 992b692642b107569b827cf06f38045d

## Block

Round 1 of review, at handoff (no pull request yet). The body's mutation proof says it mutated "every predicate the fix adds or moves". It did not. I mutated the added predicates one at a time (`ev/mutants_head.txt`, driver `mut.py`). Ten mutants on added or moved production lines pass the group's mutation command, which is the two `features_block.py` blocks. They also pass the whole `tests/features.py`, which reported `ALL 5336 FEATURE CHECKS PASSED` under each mutant (`ev/full_mut_<i>.txt`). Here is every survivor:

```
SURVIVED supply_hold.py: _passes: 'inp.mode not in (MODE_AUTO, MODE_ECONOMY)' -> 'False'              (a fixed/non-plan mode is held like a plan)
SURVIVED supply_hold.py: _passes: 'inp.mode not in (MODE_AUTO, MODE_ECONOMY)' -> 'inp.mode != MODE_AUTO' (economy passes unheld)
SURVIVED supply_hold.py: _passes: 'boosts.active(CHANNEL_SPACE, now) or boosts.active(CHANNEL_DHW, now)' -> 'boosts.active(CHANNEL_DHW, now)'   (a live space boost is held up to MIN_PAUSE)
SURVIVED supply_hold.py: _passes: same -> 'boosts.active(CHANNEL_SPACE, now)'                          (a live DHW boost is held up to MIN_PAUSE)
SURVIVED supply_hold.py: _ends_soon: 'in ("dhw", "both") and tank_reason' -> '== "dhw" and tank_reason' (a "both" step with a cold tank loses rule three's exemption)
SURVIVED supply_hold.py: _ends_soon: 'nxt - now >= MIN_RUN' -> 'nxt - now >= MIN_RUN - timedelta(minutes=1)' (rule three's window one tick short: minute 6 is not pinned)
SURVIVED pump_arbiter.py: supply_tick: 'if on is None and held.supply_held and not inp.entry_released:' -> drop 'and not inp.entry_released' (a released entry retries the action's write)
SURVIVED pump_arbiter.py: _action_supply: drop 'or inp.plan_stale'                                     (a stale plan retries the action's write)
SURVIVED pump_arbiter.py: _action_supply: 'inp.mode not in (MODE_AUTO, MODE_ECONOMY)' -> 'inp.mode != MODE_AUTO' (economy drops a held write)
SURVIVED pump_arbiter.py: supply_switch: 'return inp.hass.states.get(entity) if entity else None' -> 'return inp.hass.states.get(entity)'
```

None of the first nine is equivalent. My probe block `probe_block.py` holds twenty checks, all `ok` at the head (`ALL 96 FEATURES BLOCK PASSED`, `ev/probe_head.txt`), and it kills each of the nine (`ev/mutants_probe.txt`). Each one changes control behaviour. Without the boost clauses, a boost the user asks for three minutes into a pause is held for up to MIN_PAUSE. Without the mode clause, a fixed mode is held like a plan. Without the released or stale guard, the step tick switches the pump after unload or on a stale plan.

The tenth is equivalent only under the stub: `FakeHass.states.get(None)` returns `None`. In real Home Assistant, `StateMachine.get(None)` raises, because it calls `.lower()` on the id. `hold_supply` now reaches `supply_switch` on every non-None write, including installs with no `heat_pump_switch_entity`, so this guard is load-bearing there. Pin it with a no-switch install through `_write_supply`, or say why it cannot be pinned.

Remedy: add killing checks for all ten, as `probe_block.py` does for nine. Then re-run the group's mutation command and `prepr.sh` step 6d'.

## Findings

## Evidence

- Head reviewed: 5dea8264f2c8712c15725884d00b99eea5b48d24 (`ev/HEAD.txt`). The body's `## Head` names the same SHA. Its merge base is 26072317b5, and `git merge-tree --write-tree origin/main <head>` against origin/main fc2a7edcf2 exits 0. The ledger driver resolved `tests/structure_budgets.json` and `tests/closures.json`, so there is no conflict (`ev/cheap_checks.txt`).
- Roles: `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- CI: there is no pull request, no review packet and no CI run, so no check was red or read. `merge_train.py owed-reds` prints coverage-ratchet, fast (3.14), mutation, typing and validate-hacs. Whether the body's `## Red checks` entry for `mutation` is owed is decided once a PR's checks exist.
- Mutation proof, re-run: 47 single mutants against the group's command (`mut_cmd.sh`: the supply-switch blocks through the ceiling-probe marker, plus the early cut-off block). 37 were killed and the 10 above survived (`ev/mutants_head.txt`). Every survivor was re-run against the whole `tests/features.py` (`ev/full_mut_*.txt`) and survived there too. The head's whole `tests/features.py` passes: `ALL 5336 FEATURE CHECKS PASSED` in 7m23s.
- Boundaries, one tick either side, from my probes at the head, all `ok`:
  - MIN_RUN: an OFF to a run 9 min old is held; at 10 and 11 min it passes.
  - MIN_PAUSE: an ON to a pause 9 min old is held; at 10 and 11 min it passes.
  - Rule three: an ON at minute 4 or 5 passes; at minute 6 or 14 it is skipped.
  - The early cut-off's MIN_ON `<` to `<=` mutant is killed, and MIN_OFF doubled is killed.
  - Changing MIN_RUN or MIN_PAUSE to 9 or 11 is killed.
- Closed loop: I re-ran `SUPPLY_HOLD=1 early_cutoff_closed_loop.py NULL HOT LIGHT`. At phase 7 (`ev/cl_phase7.txt`), at `CYCLE_PHASE_MIN=0` (`ev/cl_phase0.txt`), and with rule three forced off (`ev/cl_norule3.txt`, my own `no_rule3.py`, since the body's is out of tree), all 36 rows equal the body's tables after whitespace normalisation. The harness sha1 is 39a4867b2afda697d041add836d69a9fd3e37401, as quoted.
- Flat-price null control: every quantified figure has a flat twin in the tables, and at phase 0 gate on equals gate off on all six pairs. Under the flat profile at phase 7 the gate costs comfort:
  - HOT flat: pump 1.6 to 0.0 kWh/day, room minimum 20.18 to 19.68.
  - NULL flat: room minimum 19.69 to 19.68.
  - LIGHT flat: room minimum 18.97 to 18.90.
  
  On HOT flat, with rule three forced off, the pump runs 1.0 kWh and the room minimum is 19.99. The body states this and puts rule three to the owner, so it is not a review block. NULL and HOT winter rows are identical with and without rule three, as claimed.
- Harness extension: the merge-base harness and the head harness, both run on the head's code with NULL in default mode, give byte-identical output (`ev/harness_identity.txt`: IDENTICAL).
- Class: the body's rule, `git grep -n 'switch_supply(' -- custom_components`, returns the two call sites and the definition, matching the body's table. The other `turn_on`/`turn_off` writers (space pump `_async_set_pump`, the silent slot, disinfection) target other entities, so the class is closed.
- VERSION, manifest, release notes, golden fixtures and both claim files are untouched against the merge base. `structure.py`: STRUCTURE RATCHET PASSED.
- Not re-derived: `entities.py` 2709, the scoped-gate count and mode line, the closure set diff, and `ha_contract.py` under venv-ha. These are cheap checks a re-cut must re-take anyway, and none bears on the block.
- Instruments: `early_cutoff_closed_loop.py`'s `SUPPLY_HOLD` mode is the fixer's extension of the finder's harness and is committed in this diff. The reviewer's drivers are `mut.py`, `mut_cmd.sh`, `probe_block.py`, `probe_cmd.sh`, `full_mut.py` and `no_rule3.py`, copied into `ev/`.

## Friction

none
