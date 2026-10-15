# Sweep: N-registry-leak (round 10, D14 steps 3-4)

Class mechanism: a module-level registry keyed by a coordinator gains an entry at
setup that unload never removes (or whose value pins its own weak key), so every
torn-down coordinator stays reachable. Finding: D1-s1-01. Status in
`dev/audit/config/bugclasses.json`: no entry for this class (no detector, no barrier).

## Enumerator
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py [--rounds N] [--clean] [--plant]`

Static half: AST over every `custom_components/heatpump_optimizer/*.py`, every
module-level dict/set/list/WeakKeyDictionary/defaultdict/deque that some code in the
module mutates (subscript store, setdefault/add/append/update/extend/insert). This
widens the finding's seam rule (`grep WeakKeyDictionary[`) to strong containers too.
Dynamic half: 3 setup -> cycle -> unload rounds through `tests/harness.py` (rig from
`D1/s1`), touches `boost.held_for` and `pump_arbiter.state_for`, gc, then per
registry counts torn coordinators held, and whether the held value reaches its key
by gc referents (closures followed, module globals not).

| run | torn_alive | early_cutoff._STATES pins | boost._PLAN_BASES pins | all other pins |
|---|---|---|---|---|
| baseline (positive control) | 3 | 3 | 0 | 0 |
| `--clean` (null control: wiring dropped at shutdown) | 0 | 0 | 0 | 0 |
| `--plant` (one-line re-introduction in boost._PLAN_BASES) | 3 | 0 | 3 | 0 |

The positive control re-finds D1-s1-01; the null control is zero; the perturbation moves
the metric 0 -> 3 on a different registry, so the walk is not keyed on early_cutoff.

## Seams (9) and dispositions

| seam | disposition |
|---|---|
| early_cutoff.py:134 `_STATES` | **instance** (the judged site, D1-s1-01): pins_key=3 |
| boost.py:210 `_STATES` | guarded: WeakKeyDictionary, BoostState holds only datetimes (pins 0, freed in --clean) |
| boost.py:217 `_PLAN_BASES` | guarded: WeakKeyDictionary, CurrentAction is plain data (pins 0; --plant shows the walk would see it) |
| pump_arbiter.py:263 `_STATES` | guarded: WeakKeyDictionary, ArbiterState pins 0 in baseline, freed in --clean |
| debugger.py:77 `_COLLECTORS` | guarded: explicit `_COLLECTORS.pop` in `async_unload_debugger` (called from `__init__.py:423` at unload) plus weak keys; dynamic arm not populated by this rig (debug collection off in FakeEntry), so the guard is by reading |
| coordinator.py:538 `_FENCED_CAUSES` | not applicable: (message, cause) string tuples, no coordinator key or value |
| coordinator.py:1246 `_WORKER_FALLBACK_CAUSES` | not applicable: entry_id -> cause string, popped on clear; bounded by entry ids, holds no coordinator |
| store.py:76 `_NEWER_ON_DISK` | not applicable: store-key strings |
| const.py:281 `INPUT_MAX_AGE_MINUTES` | not applicable: import-time config table, mutated only at module load |

Instances beyond the finding: **0**. Proposed barrier: run the enumerator's dynamic
half (or its `reaches` walk over every module-level WeakKeyDictionary after a
reload) as a tests/ script; not built here. Barriered: no.
