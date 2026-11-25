# Round 11 class sweep: N-unbounded-retention (box SW4)

**Class mechanism (judge):** a buffer or cache that serves a fixed time window
never evicts rows older than the window, so retained memory grows linearly
with uptime. `N-unbounded-retention` has no entry in
`dev/audit/config/bugclasses.json` at the register tip: it is a new class this
round (nearest N-no-expiry), effectively `open`.

**Finding in the class:** D9-s2-01 (verified, low). The card's `HistorySource`
retains 1448 rows/day.

**Result:** 74 grown containers; **2 instances beyond the finding**, 4 judged
seams (the finding's own containers), 45 guarded by a named bound, 23 not
applicable. `instances` = 2.

## Detector (D14 step 3)

### Static enumerator

`dev/audit/rounds/round11/D14/retention/enumerate.py` covers Python and the
card JS. Its full output is in `D14/retention/seams.txt`.

- **Python** (AST, per class and module): a container on `self.X` or at module
  level is **grown** by `append`/`appendleft`/`extend`/`insert`/`add`/
  `update`/`setdefault`, by a subscript store, or by `+= [..]`. It is
  **bounded** by one of:
  - `deque(maxlen=…)`, including a dataclass `default_factory` lambda;
  - an eviction verb (`pop`/`popleft`/`popitem`/`remove`/`discard`/`clear`,
    `del X[...]`);
  - a self-reading reassignment (slice or filter, tuple targets included);
  - a reset to empty or None in a method other than `__init__`.
- **JS** (`www/*.js`, per `class`): the same, for `this.X.push`/`unshift`/
  `add`/`set`/`[k]=` against `splice`/`shift`/`pop`/`delete`/`clear`/
  `length=`/self-`filter`/`slice`, or a reset to empty outside the
  constructor.
- **Runtime decides:** a bound present is not proof that it bounds by the
  window, and an absent bound is not proof of growth when the key domain is
  fixed. The probes below settle each case.

### Controls and perturbation

- **Positive control:** the enumerator lists `HistorySource.log`,
  `HistorySource.actionLog`, `HistorySource.seen` and `HistorySource.covered`
  (`www/heatpump-optimizer-card.js:7366/7406/7372/7342`) as UNBOUNDED. These
  are every container the finding names; `memo` is re-materialised, not grown.
  The finding's harness reproduces **exactly** on this tree:
  `node --expose-gc dev/audit/rounds/round11/D9/s2/card_history_retained.mjs --days 30`
  prints `retained_rows_slope=1448.0` (log 476, action 152, seen 628, memo 192,
  covered 60 chunks), and its `--arm nopan` null prints 0.0.
- **Null control:** `enumerate.py --root dev/audit/rounds/round11/D14/retention/clean_fixture`
  finds 5 seams and **0 UNBOUNDED**. The fixture holds a maxlen deque, a
  `del [:-N]` list and a pruned dict, plus a JS class trimmed by `shift` and
  `delete`.
- **Perturbation:**
  - In the fixture, replacing `del self.log[:-48]` with `pass` gives
    UNBOUNDED 1 (`Ring.log`); restoring the line gives 0.
  - In a temporary copy of the package, removing `tariff.py:239`
    `del self.house_samples[:-HISTORY_LENGTH]` moves the production count from
    31 to 32, with `PeakTracker.house_samples` UNBOUNDED.
- **Cost:** the static scan takes under 1 s. The price-days probe takes about
  2 s; the card harness about 20 s.

## Disposition (D14 step 4)

### Instance, beyond the finding (2)

| seam | probe | value |
|---|---|---|
| `price_model.py` `PriceShapeLearner.days_seen` | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/retention/probe_price_days.py` | 800 keys at day 400 against the 180 its window holds; **slope 2.00 keys/day**, no plateau |
| `price_model.py` `PriceShapeLearner.quarter_days_seen` | same probe | 1 key/day each, counted together |

**Mechanism:**

- `fold()` adds every folded day to both sets
  (`price_model.py:448` and `:453`).
- `store_payload()` keeps only `sorted(...)[-90:]`, and its comment says why:
  *"an unbounded set would grow forever"*. The in-memory sets are never
  trimmed.
- The coordinator builds one learner per entry (`coordinator.py:3877`),
  restores it only at load (`:8289`) and folds each price refresh (`:8622`).
  A process that does not restart therefore holds one more key per day in
  each set, indefinitely.

**Arms:**

- `--perturb` applies the payload's own `[-90:]` to memory after each fold:
  slope 0.00, 180 keys.
- `--null` round-trips the learner through its own payload each day (a daily
  restart): slope 0.00, 180 keys. The growth is the long-lived in-memory path
  only.

**Severity:** the same shape as the finding but small, about 2 short strings
per day (about 70 kB per year). It is a class instance, not a resource
emergency.

### Judged site (4, `beyond_finding: false`)

`HistorySource.log`, `.actionLog`, `.seen` and `.covered`
(`www/heatpump-optimizer-card.js`), from D9-s2-01.

### Guarded by a named bound (45)

- 43 seams the enumerator marks with a bound (32 `evict:<verb>@line`,
  5 `maxlen`, 6 JS `reset`). Each line in `seams.txt` names its bound.
- 2 seams the enumerator cannot see the bound for:
  - `disinfection.py:193` `DisinfectionSwitch.lost` is drained by its reader,
    `legionella.py:509` `lost, switch.lost = switch.lost, []`.
  - `coordinator.py:10355` `_ledger.add(...)` is a method on `Ledger`, whose
    `months` are pruned to `KEEP_MONTHS` (`ledger.py:270-275`).

Caveats:

- `debugger.DebugCollector.rows` and `.snapshots` are bounded by
  `COLLECT_SPAN` lifecycle and `finalize` (`debugger.py:545-547`), not per
  row.
- `sysid.SystemIdentification.samples` is reset per run (`sysid.py:1507`).

### Not applicable (23)

**Not a container (6).** `.update(...)` is a method on a detector object:

- `_external_heat`, `_vent_cusum`, `_peak_guard` and `_cop_health_cusum` on
  the coordinator.
- `config_flow._data` is a config-flow-lifetime dict keyed by config keys.
- `coordinator.py:2819` `self.__dict__[n]` is an attribute proxy.

**Fixed or bounded key domain (17)**, where nothing grows with time:

- `AccuracyTracker.lead_sigma` and `.lead_counts` are keyed by
  `LEAD_BUCKETS`, 5 keys.
- `_pump_commanded` and `InputReturnWatch._reread_at` are keyed by
  configured entity ids.
- `_solar_aperture` and `_energy_totals` have fixed keys.
- `_cop_baseline` uses 3 K outdoor buckets inside the plausible outdoor
  range, times the curve id.
- `DhwProfileLearner.daytype_last_day` and `.daytype_samples` are
  fixed-length 2 lists.
- `FrequencyMap.buckets` is keyed by decile.
- `InputHealth.readings` is keyed by input key.
- `PriceShapeModel.residual_var`, `.shapes`, `.days`, `.quarter_factors` and
  `.quarter_days` are fixed-length index lists.
- Card `Legend.hidden` is keyed by series key.

## Proposed barrier (D14 step 5)

- **Runtime:** a soak test in `tests/` that drives one long-lived coordinator
  and one card `HistorySource` over 60 or more simulated days. It should
  assert that every container on the reachable object graph plateaus, with a
  slope of 0 after its declared window.
- **Static:** `enumerate.py` as a lint that refuses a new UNBOUNDED grown
  container unless it carries an allow-list entry naming its key domain.
- **Count:** 2 beyond-finding instances plus the judged site, in two
  languages, is a recurring class by `defect-root-cause.md`'s count. The
  barrier is worth landing beside the D9-s2-01 fix.
- **Fix shape for the instance:** apply the payload's `[-90:]` in `fold()`.
