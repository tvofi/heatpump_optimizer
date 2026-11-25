# Class sweep: N-unbounded-retention (round 11, PLAN phase D)

Mechanism: a buffer or cache that serves a fixed time window never evicts rows
older than the window, so retained memory grows linearly with uptime. Nearest
class `N-no-expiry`; differs in that nothing stale is published.
`dev/audit/config/bugclasses.json` has no entry for this class yet (new in round 11).
Finding in class: D9-s2-01 (HistorySource in the card, 1448 rows/day).

## Enumerator (D14 method step 3)

`python3 dev/audit/rounds/round11/D14/unbounded_retention_seams.py [ROOT]`

It lists every `self.X` / `this.X` attribute that grows (append/push/add/extend/
setdefault/set/insert/update or a keyed store) and in its file is never shrunk
(pop/shift/splice/clear/remove/discard/delete/del), never re-assigned after its
initialiser, and never bounded (deque `maxlen`, slice/filter re-assignment).
The finding's `seam_rule` was a grep over one file. This enumerator covers the
whole package, both Python and JS.

- **Positive control:** it lists `HistorySource.log`, `.actionLog`, `.seen` and `.covered`
  in `www/heatpump-optimizer-card.js`, which are the D9-s2-01 collections. `chunks` is
  not listed because `ensure()` deletes the stale live-edge key. That is a known
  false negative: one delete of a single key does not bound a collection. `memo`
  is not listed because it is re-assigned to a single value, but that value grows
  with `covered`. Both are covered by the finding's own harness.
- **Null control:** `D14/unbounded_retention_fixture/clean.py` (a deque with maxlen
  and a set with discard) gives `SEAMS 0`.
- **Perturbation:** `perturbed.py.txt` is the clean fixture with the single
  `self.seen.discard(...)` line removed. Copied to a `.py` file, it gives `SEAMS 1` (`seen`).

On `custom_components/heatpump_optimizer` the enumerator returns 37 seams.

## Disposition (step 4)

### Instances

| seam | probe |
|---|---|
| card.js `HistorySource.log`, `.actionLog`, `.seen`, `.covered` (+ `chunks`, `memo`) | D9-s2-01 harness `node --expose-gc dev/audit/rounds/round11/D9/s2/card_history_retained.mjs --days 30 --arm baseline` (finding site) |
| price_model.py `PriceShapeLearner.days_seen`, `.quarter_days_seen` | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/probe_price_days_seen.py`. After 400 daily `fold()` calls, both sets hold 400 keys. `as_dict` persists only the last 90, and the feed never re-delivers a past day. Exit 1. **Beyond the finding.** Growth is one short string per day per set, so severity is low. |

### Guarded

| seam | guard |
|---|---|
| accuracy.py `samples` | `deque(maxlen=HISTORY_LENGTH)` (flagged only because the field is declared in a dataclass) |
| draw_range.py `idle` | `deque(maxlen=IDLE_WINDOW)` |
| debugger.py `rows` | `COLLECT_SPAN`: `record()` finalises once the span is reached; `reset` reassigns |
| sysid.py `samples` | reset to `[]` on every arm (sysid.py:1507); one run is bounded by its phases |
| dhw_learning.py `pending` | drained by `due, self.pending = self.pending, []` on every settle |
| disinfection.py `lost` | each entry is moved from `owned` (`owned.remove`), so the count is bounded by the configured switches |
| wear.py `queued` | queue exists only while a fold is deferred and is drained at its end |

### Not applicable (the key domain is fixed, so it is not time-indexed)

- accuracy.py `lead_sigma` and `lead_counts`: keyed by lead bucket.
- coordinator.py: `_capacity_envelope` (int bucket), `_cop_baseline` (outdoor/3 °C × curve, which is physically bounded), `_energy_totals` (fixed keys), `_solar_aperture` (fixed keys) and `_pump_commanded` (configured entities).
- coordinator.py `_cop_health_cusum`, `_vent_cusum`, `_external_heat` and `_peak_guard`: `.update()` is a state-machine call, not a container.
- dhw_learning.py `daytype_samples` and `daytype_last_day`: indexed by day type.
- freq_control.py `buckets`: deciles.
- price_model.py `days`, `shapes`, `residual_var`, `quarter_factors` and `quarter_days`: indexed by profile index.
- inputs.py `readings` (input keys) and `_reread_at` (configured entities).
- disinfection.py `_readings`: configured targets.
- config_flow.py `_data`: a dict that lives for one flow.
- card.js `hidden`: series keys.

## Barrier proposal

Two production sites (two symbols each) are not enough to justify a CI barrier
under `defect-root-cause.md`. The status stays `open`, and the enumerator is the
detector. A barrier would be a `tests/` script that runs the enumerator against
an allowlist of the guarded and not-applicable seams above, costing under 1 s of
gate time.
