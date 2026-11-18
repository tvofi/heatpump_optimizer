# Class sweep: N-unordered-tiebreak (round 11, D14 steps 3-4)

Mechanism: a tie between equal candidates is broken by set or hash iteration order, so the published result depends on PYTHONHASHSEED.
Ledger status: not yet a key of `dev/audit/config/bugclasses.json` at the register head; `barriered: false`.
Finding: D1-s1-51 (verified, low) -- `plan_slots.py:87` `max(set(codes), key=codes.count)`.

## Enumerator

`dev/audit/rounds/round11/D14/sweep/enum_unordered_tiebreak.py` (AST, whole package), widened from the seam rule `grep -rn 'max(set('`: `max`/`min`/`sorted` with a `key=` over a set-like (set/frozenset call, literal, comprehension, set operation, a comprehension over one, a name or `self.` attribute assigned one, a parameter annotated as a set); `next(iter(set))`; `set.pop()`; `list(set)[i]`; a `for` over a set with a running best, `break` or `return`.

Result at the register head: seams=1 (plan_slots.py:87).

Controls (`bash dev/audit/rounds/round11/D14/sweep/controls_unordered_tiebreak.sh`): positive re-finds plan_slots.py:87; null fixture 0; perturbation: the one-line fix (dict.fromkeys) moves 1 -> 0, a one-line re-introduction at coordinator.py `sorted(set(day_types))` moves 1 -> 2.
Static limit: an iterable built from a set in a caller and passed as an `Iterable` parameter is invisible; every keyed `max`/`min`, `next(iter(..))` and no-argument `pop()` in the package (14 sites) and every set/frozenset site was reviewed by hand to cover it (table below).

## Dispositions

Instance (the judged site, `beyond_finding: false`):

| seam | probe |
|---|---|
| `plan_slots.py::plan_slots` (line 87) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py`: distinct_tie=2 (fails), null 1, `--perturb` 1 -- re-run in this box |

Guarded / not applicable:

| seam | disposition | reason |
|---|---|---|
| device_prefill.py:231 _matched_keys max(pairs, key=len(pair[1])) over a comprehension of the set `keys` | not applicable | pair order is hash order (keys is set(table) | {...} of (str,str)), but a tie needs two distinct candidate keys of equal length that are both suffixes of the same unique id -- the same string -- so no two candidates tie; found by review, not by the static enumerator (keys arrives as an Iterable parameter) |
| coordinator.py:8815 max(candidates, key=...) | not applicable | list built in fixed code order (tariff, then fuse); a tie resolves to the first |
| coordinator.py:10449 min(costs, key=...) | not applicable | dict, insertion-ordered by code (hourly_spot, monthly_avg_spot, fixed) |
| notifier.py:133, optimizer.py:637, optimizer.py:699 | not applicable | lists in schedule / stable-argsort / relaxed-plan order |
| open_meteo.py:249 min(gaps, key=(-count, gap)) | guarded | the key includes the gap itself, a total order: no tie |
| store.py:668 max(names, key=len) | not applicable | list from the DOMAINS dict literal; distinct equal-length names cannot both suffix one key |
| disinfection.py:265, optimizer.py:1767, pump_arbiter.py:2151, services.py:783/1280 | not applicable | list or insertion-ordered dict, not a set |
| coordinator.py:2399 peak_months frozenset[int] published unsorted | not applicable | int hashes are not randomised, so the order is stable across restarts; no tie-break involved |
| other set/frozenset sites (inputs.py:1356 _pending, optimizer.py excused/unheld, dhw_planner unreachable, price_model days_seen, away days, _background_tasks, ...) | not applicable | membership, add or bookkeeping iteration with no single-element pick and no ordered published output (inputs.py:1364 stamps every pending id with one time) |

`instances` = 0 beyond the finding.

## Barrier (proposed)

The enumerator as a `tests/` check (zero seams allowed; the fix is `max(dict.fromkeys(xs), key=...)` or a total-order key), under a second of gate time.
