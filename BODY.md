Why this change, and what it measures.

The R10-N-log-flood barrier (`tests/entities.py` `_R10_LOG_ALLOWED_BY_REASON`) carried eight unlatched WARNING/ERROR sites under "OWED", each reached every cycle or solve and triggered by a persisting condition. This PR latches each through the existing transition latch, moved from `coordinator.py` to a new leaf module `log_latch.py` so the pump arbiter and the input reader can import it without closing an import cycle, demotes the optimizer's three redundant per-solve reports to DEBUG, deletes each OWED entry, and adds the owed runtime probe arms.

- `coordinator._apply_action` (stale-plan hold), `_command_valve_target` (three sites), `_note_solve_failure`, `pump_arbiter._space_target` and `inputs._age_gate` route through `log_latch._log_held` keyed on the coordinator (the arbiter and reader receive it, since the reader is rebuilt on every read and keying on `self` would log once per read).
- `optimizer.optimize` / `_solve_space` / `_optimize_space_only` are demoted to DEBUG: a failed solve already surfaces once through the coordinator's latched `_note_solve_failure` (the `failed (...)` status), and a released manual plan through its `manual_plan_released` notification. The optimizer cannot latch on the coordinator -- it runs in a worker process with a fresh optimizer per solve -- and importing `coordinator` would add HA glue to the pure solver (fixer.md step 17), so the duplicate is dropped to DEBUG rather than latched in place.

## Head

83bf0770c6aceb32161d68523f525e8488d5bfa4

## Mutation proof

Revert the latch in `_note_solve_failure` (coordinator.py:632) to a bare `_LOGGER.error`, and the barrier's enumerator reopens the seam (the OWED entry is gone, so the site would be refused):

```
PYTHONPATH=tests/hastub python3 - <<'PY'
import ast, re
from collections import Counter
from pathlib import Path
def unlatched(sources):
    found = Counter()
    for name, source in sources.items():
        tree = ast.parse(source)
        def walk(node, chain, fn):
            for child in ast.iter_child_nodes(node):
                inner = child if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
                if (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
                        and child.func.attr in ('warning','error')
                        and ast.unparse(child.func.value) == '_LOGGER'):
                    latched = False
                    for test in chain:
                        text = ast.unparse(test.test)
                        if re.compile(r'(warn|logged|report|latch|announc|_failed|notified|seen)', re.I).search(text) or (
                                isinstance(test.test, ast.Compare) and any(isinstance(o, ast.NotIn) for o in test.test.ops)
                                and f'{ast.unparse(test.test.comparators[0])}.add(' in ast.unparse(fn)):
                            latched = True
                    if not latched:
                        found[(name, fn.name if fn else '<module>')] += 1
                walk(child, chain + [child] if isinstance(child, ast.If) else chain, inner)
        walk(tree, [], None)
    return found
pkg = Path('custom_components/heatpump_optimizer')
src = {p.name: p.read_text() for p in sorted(pkg.glob('*.py'))}
mut = dict(src)
mut['coordinator.py'] = mut['coordinator.py'].replace(
    '_log_held(coord, "solve_failure", True, "Optimization failed: %s", err)',
    '_LOGGER.error("Optimization failed: %s", err, exc_info=True)')
print('FIXED  _note_solve_failure unlatched:', unlatched(src).get(('coordinator.py','_note_solve_failure'), 0))
print('MUTANT _note_solve_failure unlatched:', unlatched(mut).get(('coordinator.py','_note_solve_failure'), 0))
PY
```
FIXED  _note_solve_failure unlatched: 0
MUTANT _note_solve_failure unlatched: 1

## Null control

The unmodified tree at `origin/main` (`10d00fe0f46cab2dbe5246094fddf7c18a34625d`) reads the eight OWED sites as seams; the barrier's own planted latched fixture is not a site, and the runtime probe's `control` arm reads `floods=0`.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/structure.py` — all rows ok, including `max_class_loc 8635 <= 8635`, `import_cycle_modules 0 <= 0`, `seam_cut_total 752 <= 752`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` — `ok R10 N-log-flood barrier: every unlatched WARNING/ERROR is on the reasoned list with its exact count`.
- `python3 dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer` — `sites=70 latched=6 seams=64` at the head; the same command over `git archive origin/main` prints `sites=80 latched=6 seams=74` and lists `_apply_action`, `_command_valve_target` (3), `_note_solve_failure`, `_space_target`, `_age_gate`, `optimize`, `_solve_space`, `_optimize_space_only` as SEAM.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py` — every arm reads `floods=0`: `control`, `no_weather_entity`, `weather_fetch_fails`, `open_meteo_no_coord`, `open_meteo_bad_coord`, `no_prices`, `bad_peak_months`, `bad_peak_hours`, and the five new arms `solve_failure`, `stale_plan`, `valve_mistyped`, `space_target_misdeclared`, `future_stamp`.

## Red checks

`the lease has one winner, a dead gate is stolen, a live one is not, and run.sh runs unleased` — `tests/gate_lock.py`'s self-check, red only while sibling seats hold `/tmp/hpo-gate.lock` (its subprocesses then all "win" the contended lease). The branch does not touch `gate_lock.py`; the failure is the shared machine's, not this diff's. No cheaper detector is owed: the check is its own detector, and it passes on a quiet machine.

## Forward-carry

none

## Friction

none
