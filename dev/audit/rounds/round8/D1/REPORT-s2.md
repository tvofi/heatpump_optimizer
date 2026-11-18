# D1 seat s2 — store corruption fuzzing (method step 2)

Baseline SHA `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree:
`/home/claude/audit-r8/seats/D1-s2` (a copy export, no `.git`).

## Method

Enumerated every `QuarantiningStore(...)` construction (12 constructions, 11
distinct persisted payloads: `boost`, `away`, DHW `profile`/`draws`,
`snapshots`, `thermal_learning`, `price_model`, `ledger`, `accuracy`,
`energy`, `manual_plan`, `legionella`). For each loader, read the
`from_dict`/loader body and located every seam where a leaf value is
trusted without a `try/except (TypeError, ValueError, OverflowError)`
around its numeric coercion, or without an `isinstance` check on a nested
container. Where a gap looked real, built a seeded-mutant fuzz harness
(`tests/hastub`'s honest in-memory `Store`, keyed the same way the real
`homeassistant.helpers.storage.Store` is, round-tripped through `json` like
the real one) that seeds >= 200 mutants of a healthy payload directly into
the simulated "disk", runs the *real* production loader
(`HeatPumpOptimizerCoordinator._async_load_ledger`, etc.), and then runs one
real cycle's read of that data (`_build_data_dict()`, which every
`_async_update_data()` call makes) -- the same "load through the real
loader, run one cycle" the brief asks for.

## Findings

### D1-s2-01 -- `MonthlyLedger.from_dict` validates dict shape but not the
numeric leaves inside `lines[*]`, so a type-confused `kwh`/`sek` value
crashes every cycle forever

See `tools/audit/round8/D1/s2_ledger_fuzz.py` (committed, single-command
header). 250 seeded mutants of a healthy ledger payload (type swaps,
NaN/inf spellings, huge/negative numbers, wrong nesting, missing keys,
bogus extra months), applied at the JSON-storage boundary the same way disk
corruption or a hand-edited `.storage` file would appear, then loaded
through the real `_async_load_ledger()` and read through the real
`_build_data_dict()` (the dict every coordinator refresh assembles for
`self.data`).

- `RESULT ledger_mutants_n=250`
- `RESULT ledger_loader_raised=0` -- the *loader itself* never raises; it
  believes every mutant is clean.
- `RESULT ledger_escape_rate=0.3240` -- 81/250 mutants cause an **uncaught**
  `TypeError`/`ValueError` the first time `_build_data_dict()` reads the
  loaded ledger (`MonthlyLedger.savings_months` -> `.line()` ->
  `float(entry.get("kwh"/"sek", 0.0))`).
- `RESULT ledger_repeat_rate=1.0000` -- every one of those 81 repeats
  verbatim on a second call with no state change: nothing quarantines the
  bad month, so the failure is **permanent** for the life of the loaded
  instance, not a one-cycle blip. There is no "one log line" either -- the
  exception is not logged by production code at all at this seam; it
  simply escapes.
- Null control, same 250 mutants at the same JSON paths, run against two
  sibling loaders that *do* leaf-validate
  (`AccuracyTracker.from_dict`/`PriceShapeModel.from_dict`, both reachable
  the same way): `RESULT accuracy_escape_rate=0.0000`,
  `RESULT price_model_escape_rate=0.0000`. This rules out the harness
  itself as the source of the escapes -- the same corruption pool and the
  same "seed disk, load, read" procedure finds nothing wrong in the two
  control stores.
- Perturbation (applied to the tree only to record the RESULT lines below,
  then reverted -- see "Restored"): adding the same
  `try: float(...) except (TypeError, ValueError, OverflowError)` leaf
  guard that every sibling loader already has, inside
  `MonthlyLedger.from_dict`'s `months.items()` loop, drops
  `ledger_escape_rate` to `0.0000` (`ledger_quarantined_clean=250`) while
  leaving the two control stores' already-zero rate unchanged -- the number
  moves in the stated direction under the named one-line production edit.

**Claim**: a single type-confused numeric leaf in the persisted ledger
store (e.g. a `.storage` file hand-edited, corrupted by a partial write, or
written by a future/rolled-back version with a different `lines` schema)
makes `HeatPumpOptimizerCoordinator._build_data_dict()` raise an uncaught
exception on every subsequent refresh, for the life of the coordinator
instance, with no log line naming the cause and no self-repair -- this is
the "turns a corrupt input into a permanent failure" case the brief names,
and it reaches every entity's `coordinator.data`, not only the ledger
sensors, because `_build_data_dict()` is the single dict every entity
reads.

**Severity**: `critical`. On a real install this converts a few bytes of
disk corruption (or a manual `.storage` edit, or a partially-written save
interrupted by e.g. #237's reload-mid-cycle race, which this seat's sibling
method step 1 exercises) into every entity going unavailable/stale forever,
with the log giving no clue why, until the user finds and hand-edits the
`.storage` file themselves. This is squarely the finiteness-boundary class
the module's own docstring (`store.py`) warns about -- "a guard sat on the
seam a harness happened to show, while its sibling in the same store dict
stayed open" -- except here the *entire* leaf-validation pass was skipped
for one store, not just one field of it.

**Instrumented symbol**:
`heatpump_optimizer.ledger:MonthlyLedger.from_dict` /
`.savings_months` / `.line`;
`heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_load_ledger`
/ `._build_data_dict`.

**Phenomenon / seam rule**: every `QuarantiningStore` loader whose
`from_dict` recurses into a nested container without wrapping each numeric
leaf's `float()`/`int()` coercion in `try/except (TypeError, ValueError,
OverflowError)`. Enumerated by:
`grep -n "def from_dict" custom_components/heatpump_optimizer/*.py`
followed by, per hit, checking whether every leaf under a validated
container is itself coerced inside a narrow `except`. Of the 11 loaders
checked this round, only `ledger.py`'s has the gap; the other 10
(`accuracy.py`, `wear.py`, `price_model.py`, `dhw_draws.py`, `defrost.py`,
`flow_lift.py`, `freq_control.py`, `snapshots.py`, `tariff.py`,
`comfort_learning.py`, `curve_learning.py`, `manual_plan.py`/`legionella.py`)
leaf-guard every numeric field they parse (see non-findings).

**Proposed fix scope**: one method, `MonthlyLedger.from_dict` in
`custom_components/heatpump_optimizer/ledger.py` -- wrap each `lines[*]`
entry's `kwh`/`sek` (and, for symmetry, `meta[*]`'s `sum`/`count`) in the
same `try/except (TypeError, ValueError, OverflowError)` its sibling
loaders already use, dropping (and counting, with the existing one-line
`_LOGGER.warning`) the enclosing month on failure rather than keeping a
month whose leaves cannot be read back.

**Restored**: the perturbation patch was applied to
`custom_components/heatpump_optimizer/ledger.py` only to record the
`RESULT` lines above, then reverted (`cp` from a pre-patch backup) before
this report was written; `diff -r` against `/home/claude/audit-r8/export`
shows no tracked-source difference (only a `__pycache__/*.pyc` artefact,
which is not a tracked file).

## Non-findings

- The other 10 `QuarantiningStore` loaders leaf-guard every numeric
  coercion they perform (read by hand, see method section above); the two
  used as the fuzz harness's null control (`accuracy`, `price_model`) show
  `escape_rate=0.0000` over the same 250 mutants that expose the ledger gap
  -- `tools/audit/round8/D1/s2_ledger_fuzz.py`.
- `ManualOverride.from_dict` deliberately *raises* `ManualPlanError` on any
  malformed slot/expiry (by design, not a bug); its caller
  (`_async_load_manual_plan`) catches `(ManualPlanError, AttributeError,
  TypeError)` and every raise inside `parse_channel`/`_parse_dt` is
  re-wrapped as `ManualPlanError` before it can escape that tuple, so no
  exception type there is missed. Checked by reading, not separately
  fuzzed given the time budget.
- `legionella.py`'s `async_load` wraps the whole load-and-parse
  (`_load_switch_record` included) in one outer `try/except Exception`, so
  a parse error there is caught at the same seam that catches a store
  read failure, unlike ledger's loader which only wraps the `async_load()`
  call itself.
- `QuarantiningStore.async_load` (`store.py`) does scrub non-finite float
  leaves and non-finite-parseable strings (`"NaN"`, `"Infinity"`, ...)
  before any loader sees them -- confirmed those particular mutants in the
  pool never contribute to `ledger_loader_raised`; the escapes are all leaf
  **type** confusion (list/dict/bare string in a numeric slot), which
  `_sanitize` explicitly does not touch (its own docstring says so) and
  which is a different gap from the one `store.py` closes.

## What I could not finish

Time budget did not allow building the same >=200-mutant harness for the
remaining 9 stores (only read + spot-checked their `from_dict`s by hand);
the ledger finding was strong enough on its own that COMMON.md's "three
findings the judge will reproduce over ten it will void" argued for depth
over breadth here. No other candidate finding in this seat's scope (store
corruption fuzzing) cleared the executed-number bar.

## Exposure

None -- no `docs/` or GitHub reading was needed for this seat's method.

## Harnesses

- `tools/audit/round8/D1/s2_ledger_fuzz.py`
