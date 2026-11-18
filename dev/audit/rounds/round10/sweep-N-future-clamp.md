# Class sweep: N-future-clamp (round 10, D14 steps 3-4)

Base `handoff/audit-r10-register` at 9355f107d. Class mechanism: a legitimately
future instant in a persisted store is treated as a clock-ahead stamp and
rewritten to now on load. Judged finding: D1-s2-01. The class has no entry in
`dev/audit/config/bugclasses.json` (0 matches); its nearest, `N-future-instant`,
is `barriered` by `QuarantiningStore(lead=...)` -- this class is that barrier's
over-reach, so nothing bars it.

## Enumerator

`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep/future_clamp_seams.py`
(output: `D14/sweep/future_clamp_seams.out`). It reads every
`QuarantiningStore(...)` construction's `lead` by AST (15 stores), expands
`store.DOMAINS` with aliases resolved, and lists every stored instant leaf (55)
with its host store's lead and its writing (origin) store's lead; it flags a
leaf whose origin lead exceeds the host's (a host embedding a forward-leaning
store's payload). Generalises the finding's seam rule.

| control | command | result |
|---|---|---|
| positive | live tree | 7 leaves / 2 host-origin pairs flagged, incl. `snapshots/#/learners/accuracy/lead_pending/#/0` (D1-s2-01) |
| null | `--null` (clean fixture) | 0 |
| perturbation | `--reintro` (one alias line) | 0 -> 1 |
| finding's perturbation | `--perturb` (snapshots lead 24 h) | snapshots pair 1 -> 0 |

Finding probe retaken: `snapshot_bound.py` 5 rewritten / 5 WARNINGs; `--perturb` 0 / 0.

## Disposition of every seam

Flagged leaves (origin lead 24 h, host lead 0):

| seam | disposition |
|---|---|
| snapshots `learners/accuracy/lead_pending/#/0` | **instance** -- D1-s2-01 itself; probe `snapshot_bound.py` |
| snapshots `learners/accuracy/promises/*/start` | not applicable: `plan_promise` stamps `start` = solve_time (accuracy.py:566), never future |
| snapshots `learners/accuracy/samples/#/t`, `evidence_since` | not applicable: stamped with now (accuracy.py:81, :197) |
| snapshots `learners/comfort/last_update`, `comfort/history/#/t` | not applicable: event times (comfort_learning.py:120) |
| debug `rows/#/accuracy_sample/t` | not applicable: a sample's own past stamp |

Unflagged leaves:

- Stores with a forward lead -- boost (2 h, `_MAX_LEAD`), manual_plan (20 h,
  `build_override` clamps to the window), accuracy (24 h), away and notifier
  (`lead=None`): **guarded** by their own lead.
- debug `snapshots/#/data`: **guarded** -- JSON text, which `_bound_instants`
  does not descend (store.py comment: its plan instants lie ahead by design).
- Every other leaf in a lead-0 store (thermal_learning, price_model, energy,
  ledger, pump_duty, dhw_profile, dhw_draws, dhw_legionella, snapshots
  `taken_at`, debug `started_at`/`rows/#/t`): **not applicable** -- write-time
  stamps of past events, which a lead of 0 correctly bounds.

## Result

Instances beyond the finding: **0**. One judged site. Proposed barrier: the
enumerator's flag as a `tests/` check restricted to leaves carrying a
"forward" mark in `DOMAINS` (store-level origin lead over-flags 6 past-stamp
leaves), or simply give the snapshots store `lead=max(LEAD_BUCKETS)` -- the
fix the finding's perturbation already demonstrates.
