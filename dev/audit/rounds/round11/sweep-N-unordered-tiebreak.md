# Class sweep: N-unordered-tiebreak (round 11, D14 steps 3-4)

Mechanism: a tie under `key=` is broken by set/hash iteration order, so output depends on PYTHONHASHSEED.

## Enumerator
`python3 dev/audit/rounds/round11/D14/unordered_tiebreak.py custom_components` (AST): `max`/`min` with `key=` over a set-typed
expression (set()/frozenset() call, set literal/comprehension, set operator, or a local bound to one), `next(iter(<set>))`, and `<set>.pop()`.

- Positive control: returns `plan_slots.py:87 close`, the site of D1-s1-51 (re-found).
- Null control: fixture `max(sorted(set(c)), key=c.count)` -> 0 seams.
- Perturbation: one-line `return min(s, key=len)` with `s = set(c)` -> 1 seam.

## Seams and disposition
| seam | disposition | evidence |
|---|---|---|
| `custom_components/heatpump_optimizer/plan_slots.py:87` `plan_slots.close` `max(set(codes), key=codes.count)` | instance (finding site D1-s1-51) | PYTHONHASHSEED 1..8 on a 1:1 cheap/preheat tie: cheap x5, preheat x3; lead probe `D1/leads/slot_reason_hashseed.py` |

Grep-adjacent sites `sorted(set(...))` (plan_slots.py:88, coordinator.py:4375, dhw_schedule.py:131,138) are not applicable: `sorted` imposes a total order.
Dict iteration is insertion-ordered and out of class.

Instances beyond the finding: 0. Proposed barrier: run the enumerator as a `tests/` lint class (sub-second, AST only) once the site is fixed
(e.g. `max(sorted(set(codes)), key=codes.count)` or `Counter.most_common` with an explicit tie rule). Class not barriered today.
