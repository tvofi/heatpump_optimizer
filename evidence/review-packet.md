# Review packet #3734
head: 98cb43e750457b41ae6feb9a0c56cf1d6728e201
base: ae0ed64af898d8923ac35afe6e9c031ac1e6b111

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=135183912919 success
arch-score / arch-score id=135183475253 success
arm id=135182971003 skipped
budget-raise-gate / budget-raise-gate id=135183475167 success
cancel-superseded id=135182982871 success
codeql id=135183343475 skipped
codeql / Analyze (actions) id=135183474824 success
codeql / Analyze (javascript-typescript) id=135183475095 success
codeql / Analyze (python) id=135183475000 success
gate id=135184236409 failure
governance id=135183342526 skipped
governance / env-matrix id=135183474661 success
governance / instrument-self-tests id=135183474915 in_progress
governance / policy-docs id=135183475137 success
governance / record id=135183476824 skipped
governance / wave-script id=135183475150 success
hassfest id=135183344832 skipped
hassfest / hassfest id=135183474884 success
kernel-points id=135183475801 skipped
pr-contract id=135184239133 skipped
prelude id=135182982780 success
refresh id=135182982048 success
sweep-self id=135184761382 skipped
tests id=135183344291 skipped
tests / arch-instrument id=135183866958 success
tests / briefs id=135183475871 success
tests / browser id=135183866884 success
tests / closure-scope id=135183475043 success
tests / closures id=135183867291 in_progress
tests / coverage id=135183866951 in_progress
tests / fast (3.14) id=135183867025 in_progress
tests / mutation id=135183475273 failure
tests / mutation-pins (1) id=135184231932 in_progress
tests / mutation-pins (2) id=135184232111 in_progress
tests / nightly-ha id=135183869494 skipped
tests / nightly-status id=135183475087 failure
tests / replay id=135183870030 skipped
tests / typing id=135183867026 success
validate id=135183343016 skipped
validate / validate-hacs id=135183474999 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 135183474915: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at 98cb43e750457b41ae6feb9a0c56cf1d6728e201 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item 2a2aee52: dismissed:the absence is recorded under Figures, and the round-end triage reads it there.
NOTE body item d3bb5061: dismissed:answered by the orchestrator's inbox ruling, line 1 of refs/heads/inbox/r11-seam-inputs-guards.
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 28 script(s) run, 5 scoped out.
             no segment of this names a program this check knows
  unverified EXPORT=$(mktemp -d); git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75 dev/audit/rounds/round11 | tar -x -C $EXPORT
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m4_tariff.py
             the path `$EXPORT/dev/audit/rounds/round11/D2/s3/m4_tariff.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py --only temperature_roundtrip
             the path `$EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D1/s3/parsers_fuzz.py --arm pump
             the path `$EXPORT/dev/audit/rounds/round11/D1/s3/parsers_fuzz.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D1/leads/plausible_upper.py
             the path `$EXPORT/dev/audit/rounds/round11/D1/leads/plausible_upper.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub:tests python3 $EXPORT/dev/audit/rounds/round11/D1/s2/config_fuzz.py --versions N
             the path `$EXPORT/dev/audit/rounds/round11/D1/s2/config_fuzz.py` is a template or an expansion, not a literal
  unverified git show 819aa2e354b4e5baaf824b8568fd72bea8168a75:dev/audit/rounds/round11/sweep-P1.md
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/wood_advisor.py
             `tests/wood_advisor.py` is in the tree at this head
  ok         tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/open_meteo.py
             `tests/open_meteo.py` is in the tree at this head
  ok         tests/finite_boundary.py
             `tests/finite_boundary.py` is in the tree at this head
  ok         tests/guard_pins.py
             `tests/guard_pins.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         tests/env_drift.py
             `tests/env_drift.py` is in the tree at this head
  ok         GOLDEN_MODE=drift tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/audit/seat/features_block.py
             `tools/audit/seat/features_block.py` is in the tree at this head

FIGURES: 13 resolved, 8 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json
new file mode 100644
index 0000000000..2161ad64c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/__init__.py:async_migrate_entry GUARD_OFF ab300483",
+  "killed_by": "tests/entities.py",
+  "old": "        if repairs:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json
new file mode 100644
index 0000000000..8ef22ec1ad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_interval_minutes RETURN_DEL 3410ce8b",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return minutes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json
new file mode 100644
index 0000000000..13f963296c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader._begin GUARD_OFF 6aa9ea3a",
+  "killed_by": "tests/features.py",
+  "old": "        if not isinstance(entity_id, str):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json b/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json
new file mode 100644
index 0000000000..c5754e5738
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:parse_bool RETURN_DEL 3434dfb6",
+  "killed_by": "tests/features.py",
+  "old": "    return None if number is None else number != 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json
new file mode 100644
index 0000000000..620f1267b2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block CMP_BOUND 30aea580",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    kept = [i for i, t in enumerate(times) if t >= floor]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`kept = [i for i, t in enumerate(times) if t > floor]`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json
new file mode 100644
index 0000000000..4a1284b11b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block CMP_BOUND 4d7eb319",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    if len(kept) < 2:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(kept) <= 2:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=3."
+}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/__init__.py b/custom_components/heatpump_optimizer/__init__.py
index 459287d196..24625319c8 100644
--- a/custom_components/heatpump_optimizer/__init__.py
+++ b/custom_components/heatpump_optimizer/__init__.py
@@ -32,7 +32,7 @@ from .const import (
     CONFIG_ENTRY_VERSION,
     DOMAIN,
 )
-from .entry_config import EntryConfig
+from .entry_config import EntryConfig, number_repairs, repaired_numbers
 
 # Bound here, not via ``_lazy``. Home Assistant 2026 evaluates
 # ``async_setup_entry``'s annotations with ``get_type_hints``, which looks
@@ -203,8 +203,10 @@ async def async_migrate_entry(hass: HomeAssistant, entry: HeatPumpOptimizerConfi
     """Migrate a config entry created by an older version of the integration.
 
     Every option the integration reads is looked up with a default, so older
-    entries only need their version stamped forward. Without this handler Home
-    Assistant refuses to load entries created before the current
+    entries need their version stamped forward and any numeric option stored
+    as a non-number repaired: numeric text stored as its number, anything else
+    dropped for its default (``entry_config.number_repairs``). Without this
+    handler Home Assistant refuses to load entries created before the current
     ``ConfigFlow.VERSION`` and the integration appears broken after an upgrade.
     """
     if entry.version > CONFIG_ENTRY_VERSION:
@@ -223,7 +225,19 @@ async def async_migrate_entry(hass: HomeAssistant, entry: HeatPumpOptimizerConfi
             entry.version,
             CONFIG_ENTRY_VERSION,
         )
-        hass.config_entries.async_update_entry(entry, version=CONFIG_ENTRY_VERSION)
+        repairs = number_repairs({**entry.data, **entry.options})
+        if repairs:
+            _LOGGER.warning(
+                "Stored options that are not numbers: %s; text is stored as its number, "
+                "anything else is dropped and its default applies",
+                ", ".join(sorted(repairs)),
+            )
+        hass.config_entries.async_update_entry(
+            entry,
+            data=repaired_numbers(entry.data, repairs),
+            options=repaired_numbers(entry.options, repairs),
+            version=CONFIG_ENTRY_VERSION,
+        )
 
     return True
 
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index 71f5d73017..c762cf8b3a 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -36,6 +36,37 @@ def _nonzero_number(value: Any, default: float) -> float:
     return finite_float(value, default) or default
 
 
+#: The longest span of minutes a plan option may name: past a day the plan
+#: outlives the day-ahead prices it was solved against.
+_MAX_PLAN_MINUTES = 24 * 60.0
+
+
+def _interval_minutes(value: Any, default: float) -> float:
+    """A re-solve interval in minutes inside ``(0, a day]``, else ``default``.
+
+    Zero or a negative interval stamps a cycle's end at or before its start,
+    and 1e12 minutes overflows the datetime it is added to (sweep-P1,
+    ``early_cutoff.arm``): neither is an interval.
+    """
+    minutes = finite_float(value)
+    if minutes is None or not 0.0 < minutes <= _MAX_PLAN_MINUTES:
+        return default
+    return minutes
+
+
+def _lead_minutes(value: Any, default: float) -> float:
+    """A lead in minutes inside ``[0, a day]``, else ``default``.
+
+    A zero lead is "at the window's start"; a negative one names no instant
+    before it, and 1e12 minutes overflows the datetime it is subtracted from (sweep-P1,
+    ``wood_fuel.lighting_window``).
+    """
+    minutes = finite_float(value)
+    if minutes is None or not 0.0 <= minutes <= _MAX_PLAN_MINUTES:
+        return default
+    return minutes
+
+
 def _whole(value: Any, default: int | None) -> int | None:
     try:
         return int(value)
@@ -186,8 +217,9 @@ class EntryConfig(Mapping[str, Any]):
     main_fuse_phases: float = _key(const.DEFAULT_MAIN_FUSE_PHASES, finite_float)
     max_temperature: float = _key(const.DEFAULT_MAX_TEMP, finite_float)
     min_temperature: float = _key(const.DEFAULT_MIN_TEMP, finite_float)
+    mixing_valve_target: float = _key(const.DEFAULT_MIXING_VALVE_TARGET, finite_float)
     mold_floor_breach_margin: float = _key(const.DEFAULT_MOLD_FLOOR_BREACH_MARGIN, finite_float)
-    optimization_interval: float = _key(const.DEFAULT_OPTIMIZATION_INTERVAL, finite_float)
+    optimization_interval: float = _key(const.DEFAULT_OPTIMIZATION_INTERVAL, _interval_minutes)
     peak_guard_margin_kw: float = _key(const.DEFAULT_PEAK_GUARD_MARGIN_KW, finite_float)
     peak_tariff_offpeak_factor: float = _key(const.DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR, finite_float)
     peak_tariff_peaks_averaged: float = _key(const.DEFAULT_PEAK_TARIFF_COUNT, finite_float)
@@ -203,7 +235,7 @@ class EntryConfig(Mapping[str, Any]):
     target_temperature: float = _key(const.DEFAULT_TARGET_TEMP, finite_float)
     thermal_bridge_frsi: float = _key(const.DEFAULT_THERMAL_BRIDGE_FRSI, finite_float)
     vvc_lead_minutes: float = _key(const.DEFAULT_VVC_LEAD_MINUTES, finite_float)
-    wood_lighting_lead_minutes: float = _key(const.DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, finite_float)
+    wood_lighting_lead_minutes: float = _key(const.DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, _lead_minutes)
     wood_tank_volume: float = _key(const.DEFAULT_WOOD_TANK_VOLUME, finite_float)
 
     # A fraction this version cannot read caps nothing: None, not the default.
@@ -293,6 +325,42 @@ class EntryConfig(Mapping[str, Any]):
         return len(self.raw)
 
 
+#: The parses that read a value they refuse as the key's default, so a refused
+#: stored value and an absent key parse alike.
+_DEFAULTED_NUMBERS: tuple[Parse, ...] = (
+    finite_float, _nonzero_number, _interval_minutes, _lead_minutes,
+)
+
+
+def number_repairs(stored: Mapping[str, Any]) -> dict[str, float | None]:
+    """Each defaulted numeric key ``stored`` holds a non-number for: its number, or None.
+
+    An earlier release could store text, a list, a dict or ``None`` under a
+    numeric option (D1-s2-05). The parse reads numeric text as its number and
+    anything else as the default, but the thermal table and the comfort band
+    read the stored value and raised on it at setup or on every cycle.
+    Storing the number, and dropping a key mapped to None, changes no parsed
+    field, and every raw reader then reads what the parse does.
+    """
+    return {
+        f.name: finite_float(value)
+        for f in fields(EntryConfig)
+        if f.metadata
+        and f.metadata["parse"] in _DEFAULTED_NUMBERS
+        and f.name in stored
+        and (isinstance(value := stored[f.name], bool) or not isinstance(value, (int, float)))
+    }
+
+
+def repaired_numbers(stored: Mapping[str, Any], repairs: Mapping[str, float | None]) -> dict[str, Any]:
+    """``stored`` with ``repairs`` applied: a number replaces its text, None drops the key."""
+    return {
+        key: repairs.get(key, value)
+        for key, value in stored.items()
+        if key not in repairs or repairs[key] is not None
+    }
+
+
 def _restore(raw: dict[str, Any], parsed: dict[str, Any]) -> EntryConfig:
     """``EntryConfig.__reduce__``'s constructor: the stored values and their parse."""
     return EntryConfig(raw=MappingProxyType(raw), **parsed)
diff --git a/custom_components/heatpump_optimizer/inputs.py b/custom_components/heatpump_optimizer/inputs.py
index 9d85331747..a8aea05a49 100644
--- a/custom_components/heatpump_optimizer/inputs.py
+++ b/custom_components/heatpump_optimizer/inputs.py
@@ -960,10 +960,10 @@ def parse_bool(raw: Any, *, strict: bool = False) -> bool | None:
         return True
     if token in BOOL_FALSE:
         return False
-    try:
-        return float(token) != 0.0
-    except (TypeError, ValueError):
-        return None
+    # Only a finite number is a code (D1-s3-01): "nan", "inf" and "1e309" are
+    # no reading, not a fault or a defrost.
+    number = finite_float(token)
+    return None if number is None else number != 0.0
 
 
 class InputReader:
@@ -1029,6 +1029,11 @@ class InputReader:
         and return it as-is.
         """
         entity_id = entity_id if entity_id is not None else self.config.get(key)
+        # A slot an earlier release stored as a list or a dict names no entity
+        # (D1-s2-05): read as unset, it no longer raises out of every cycle as a
+        # state-machine key.
+        if not isinstance(entity_id, str):
+            entity_id = None
         # `isinstance` rather than `is UNBOUNDED`: identical for a private
         # sentinel with one instance, and it is what narrows the union so
         # the `float()` below is checked rather than suppressed.
diff --git a/custom_components/heatpump_optimizer/open_meteo.py b/custom_components/heatpump_optimizer/open_meteo.py
index 5032c1bdca..bc85aafacc 100644
--- a/custom_components/heatpump_optimizer/open_meteo.py
+++ b/custom_components/heatpump_optimizer/open_meteo.py
@@ -248,8 +248,18 @@ def _parse_block(
         return _EMPTY
     resolution = timedelta(seconds=min(gaps, key=lambda gap: (-gaps[gap], gap)))
 
+    # A sample covers ``(t - resolution, t]``. A stamp within one resolution
+    # of year 1 has no representable span, and ``mean_over`` raised
+    # OverflowError on it for every plan step, failing every solve (D1-s3-03).
+    floor = datetime.min.replace(tzinfo=timezone.utc) + resolution
+    kept = [i for i, t in enumerate(times) if t >= floor]
+    if len(kept) < 2:
+        return _EMPTY
+
     return IrradianceSeries(
-        times=tuple(times), values=tuple(values), resolution=resolution
+        times=tuple(times[i] for i in kept),
+        values=tuple(values[i] for i in kept),
+        resolution=resolution,
     )
 
 
diff --git a/custom_components/heatpump_optimizer/wood_fuel.py b/custom_components/heatpump_optimizer/wood_fuel.py
index efa00e052e..d061ce27a5 100644
--- a/custom_components/heatpump_optimizer/wood_fuel.py
+++ b/custom_components/heatpump_optimizer/wood_fuel.py
@@ -7,20 +7,19 @@ from itertools import zip_longest
 from typing import Any
 
 from .drift import utc_elapsed_seconds
+from .entry_config import EntryConfig
 from .const import (
     CONF_DHW_WOOD_COIL_ENABLED,
     CONF_EXTERNAL_HEAT_ENABLED,
     CONF_EXTERNAL_HEAT_ENTITY,
     CONF_WOOD_FURNACE_EFFICIENCY,
     CONF_WOOD_FURNACE_ENABLED,
-    CONF_WOOD_LIGHTING_LEAD_MINUTES,
     CONF_WOOD_PACKING,
     CONF_WOOD_PRICE_SEK_M3,
     CONF_WOOD_TANK_BOTTOM_ENTITY,
     CONF_WOOD_TANK_TOP_ENTITY,
     CONF_WOOD_TYPE,
     DEFAULT_MIN_TEMP,
-    DEFAULT_WOOD_LIGHTING_LEAD_MINUTES,
     WOOD_TANK_MAX_TEMP,
 )
 from .const import finite_float
@@ -558,13 +557,7 @@ def _attach_windows(
     windows: list[WoodWindow] = [
         {"start": iso(start), "end": iso(end)} for start, end in runs
     ]
-    lead = max(
-        0.0,
-        finite_float(
-            config.get(CONF_WOOD_LIGHTING_LEAD_MINUTES),
-            DEFAULT_WOOD_LIGHTING_LEAD_MINUTES,
-        ),
-    )
+    lead = EntryConfig.from_mapping(config).wood_lighting_lead_minutes
     light_start, light_end = lighting_window(runs[0][0], timestamps[0], lead)
     view["cheaper_windows"] = windows
     view["lighting_start"] = iso(light_start)
diff --git a/dev/programme/delivery/3734.md b/dev/programme/delivery/3734.md
new file mode 100644
index 0000000000..9740c65f90
--- /dev/null
+++ b/dev/programme/delivery/3734.md
@@ -0,0 +1 @@
+- [#3734](https://github.com/tvofi/heatpump_optimizer/pull/3734) — **open**, R11-SEAM-inputs-guards: input guards (R11-SEAM-inputs-guards)
diff --git a/tests/entities.py b/tests/entities.py
index 7782c6a294..5aacc2fefd 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -15572,6 +15572,109 @@ R.check(
     and _old.data == _old_data,
     "every option is read with a default, so only the stamp moves",
 )
+# D1-s2-05: an earlier release's non-number under a numeric option raised in
+# the thermal table or the comfort band at setup or on every cycle.
+from heatpump_optimizer.entry_config import EntryConfig as _MigEC  # noqa: E402
+from dataclasses import fields as _mig_fields  # noqa: E402
+
+_mig_bad_data = {"min_temperature": [19.0], "max_temperature": "abc", "dhw_tank_volume": "200",
+                 "mixing_valve_target": "abc"}
+_mig_bad_options = {"target_temperature": None, "comfort_weight": {"v": 1.0}, "price_weight": "nan",
+                    "cop_scale": True, "silent_mode_power_fraction": "abc"}
+import logging as _mig_logging  # noqa: E402
+
+
+class _MigLog(_mig_logging.Handler):
+    def __init__(self):
+        super().__init__(_mig_logging.WARNING)
+        self.records = []
+
+    def emit(self, record):
+        self.records.append(record)
+
+
+def _mig_warnings(entry):
+    """Migrate ``entry``; return (result, the integration's WARNING records)."""
+    handler, logger = _MigLog(), _mig_logging.getLogger(integration.__name__)
+    logger.addHandler(handler)
+    try:
+        return asyncio.run(integration.async_migrate_entry(_mig_hass, entry)), handler.records
+    finally:
+        logger.removeHandler(handler)
+
+
+_mig_quiet = FakeEntry(data={"min_temperature": 19.0, "dhw_tank_volume": 200.0})
+_mig_quiet_ok, _mig_quiet_logs = _mig_warnings(_mig_quiet)
+R.check(
+    "a healthy old entry migrates with no repair warning (null control)",
+    _mig_quiet_ok is True and not _mig_quiet_logs
+    and _mig_quiet.data == {"min_temperature": 19.0, "dhw_tank_volume": 200.0},
+    f"{[r.getMessage() for r in _mig_quiet_logs]}",
+)
+_mig_bad = FakeEntry(data=dict(_mig_bad_data), options=dict(_mig_bad_options))
+_mig_before = _MigEC.from_mapping({**_mig_bad.data, **_mig_bad.options})
+_mig_bad_ok, _mig_bad_logs = _mig_warnings(_mig_bad)
+R.check(
+    "an old entry's non-numbers under numeric options are repaired, with one warning naming them",
+    _mig_bad_ok is True
+    and len(_mig_bad_logs) == 1 and "min_temperature" in _mig_bad_logs[0].getMessage()
+    and _mig_bad.version == const.CONFIG_ENTRY_VERSION
+    and _mig_bad.data == {"dhw_tank_volume": 200.0}
+    and _mig_bad.options == {"silent_mode_power_fraction": "abc"},
+    f"data={_mig_bad.data} options={_mig_bad.options}",
+)
+_mig_after = _MigEC.from_mapping({**_mig_bad.data, **_mig_bad.options})
+_mig_moved = [
+    f.name for f in _mig_fields(_MigEC)
+    if f.metadata and getattr(_mig_before, f.name) != getattr(_mig_after, f.name)
+]
+R.check(
+    "and the repair moves no parsed field (refused-number keys are left alone)",
+    not _mig_moved,
+    f"moved: {_mig_moved}",
+)
+
+# sweep-P1 (early_cutoff.arm): a re-solve interval outside (0, a day] is no
+# interval; the parse reads it as the default.
+_mig_iv = {v: _MigEC.from_mapping({"optimization_interval": v}).optimization_interval
+           for v in (0, -5, 0.0, 1e12, 1440.5, "nan", 10, 120, 1440)}
+R.check(
+    "an optimization interval outside (0, a day] parses as the default",
+    all(_mig_iv[v] == const.DEFAULT_OPTIMIZATION_INTERVAL for v in (0, -5, 0.0, 1e12, 1440.5, "nan")),
+    f"{_mig_iv}",
+)
+R.check(
+    "and one inside it, both ends' neighbours included, is read as stored (null control)",
+    _mig_iv[10] == 10.0 and _mig_iv[120] == 120.0 and _mig_iv[1440] == 1440.0,
+    f"{_mig_iv}",
+)
+
+# The keys the migration must repair, by the parse's own behaviour rather than
+# by entry_config._DEFAULTED_NUMBERS: a field whose parse reads numeric text as
+# its float and other text as the default. Text left under one such key is read
+# raw by no parse at all once a release reads it outside EntryConfig.
+from heatpump_optimizer.entry_config import number_repairs as _mig_repairs  # noqa: E402
+
+
+def _mig_defaulted(f):
+    _p = f.metadata["parse"]
+    _twelve = _p("12", f.default)
+    return _p("abc", f.default) == f.default and type(_twelve) is float and _twelve == 12.0
+
+
+_mig_numeric = [f.name for f in _mig_fields(_MigEC) if f.metadata and _mig_defaulted(f)]
+_mig_unrepaired = [k for k in _mig_numeric if _mig_repairs({k: "12"}) != {k: 12.0}]
+R.check(
+    "every option whose parse defaults text it cannot read is repaired by the migration",
+    "optimization_interval" in _mig_numeric and "wood_lighting_lead_minutes" in _mig_numeric
+    and not _mig_unrepaired,
+    f"unrepaired: {_mig_unrepaired}",
+)
+R.check(
+    "and a stored number under each is left alone (null control)",
+    not [k for k in _mig_numeric if _mig_repairs({k: 12.0})],
+)
+
 _new = FakeEntry()
 _new.version = const.CONFIG_ENTRY_VERSION + 1
 R.check(
@@ -42429,7 +42532,7 @@ _R10_LOG_ALLOWED_BY_REASON = {
     },
     "not reached per cycle: load, restore, migration, setup, frontend "
     "registration, a service call or shutdown": {
-        ("__init__.py", "async_migrate_entry"): 1, ("accuracy.py", "from_dict"): 1,
+        ("__init__.py", "async_migrate_entry"): 2, ("accuracy.py", "from_dict"): 1,
         ("defrost.py", "from_dict"): 1, ("ledger.py", "from_dict"): 1,
         ("price_model.py", "from_dict"): 1, ("price_model.py", "_stored_rows"): 1,
         ("price_model.py", "_in_domain"): 1, ("snapshots.py", "from_dict"): 1,
diff --git a/tests/features.py b/tests/features.py
index 51226adab5..4e89ca1fcb 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -3146,6 +3146,44 @@ R.check(
 R.check("parse_bool reads a real bool through", parse_bool(True) is True)
 R.check("parse_bool refuses a word it does not know", parse_bool("warm") is None)
 R.check("parse_bool reads any non-zero number as yes", parse_bool("-2") is True)
+_R11IG_NONFINITE = ("nan", "NaN", "inf", "-inf", "1e309", " Infinity ")
+R.check(
+    "parse_bool reads no non-finite number as a flag (D1-s3-01)",
+    all(parse_bool(_t) is None for _t in _R11IG_NONFINITE)
+    and all(parse_bool(_t, strict=True) is None for _t in _R11IG_NONFINITE),
+    f"{[(_t, parse_bool(_t)) for _t in _R11IG_NONFINITE]}",
+)
+R.check(
+    "and the codes either side of it still read (null control)",
+    parse_bool("0") is False and parse_bool("1") is True and parse_bool("0.0") is False,
+)
+_r11ig_slot = InputReader(
+    FakeHass({"sensor.indoor": FakeState("21.4", last_updated=minutes_ago(5, NOW))}),
+    {"indoor_temp_entity": {"v": "sensor.indoor"}, "outdoor_temp_entity": ["sensor.indoor"]},
+    now=lambda: NOW,
+)
+_r11ig_slot_reads = [_r11ig_slot.read(_k) for _k in ("indoor_temp_entity", "outdoor_temp_entity")]
+R.check(
+    "a slot holding a dict or a list reads as unset, not a raise (D1-s2-05)",
+    all(_r.problem == "not_configured" and _r.entity_id is None for _r in _r11ig_slot_reads),
+    f"{[(_r.problem, _r.entity_id) for _r in _r11ig_slot_reads]}",
+)
+_r11ig_window = _r9f41_const.INPUT_PLAUSIBLE_RANGE_C
+_r11ig_outside = [
+    (_k, _v)
+    for _k, (_lo, _hi) in _r11ig_window.items()
+    for _v in (_lo - 1.0, _hi + 1.0)
+    if inputs_mod.plausible_c(_k, _v)
+]
+R.check(
+    "every plausible window refuses a reading one degree past either end (D1-s2-51)",
+    len(_r11ig_window) > 0 and not _r11ig_outside,
+    f"accepted: {_r11ig_outside}",
+)
+R.check(
+    "and accepts its own midpoint (null control)",
+    all(inputs_mod.plausible_c(_k, (_lo + _hi) / 2.0) for _k, (_lo, _hi) in _r11ig_window.items()),
+)
 
 # -- health, and what must NOT freeze ---------------------------------------
 # Mode configured and healthy, online configured but unusable, defrost never
@@ -62817,6 +62855,19 @@ from heatpump_optimizer.const import (  # noqa: E402
     DEFAULT_PV_EXPORT_PRICE as _P8_EXPORT_DEFAULT,
 )
 
+_R11IG_TEMPS_C = (-20.0, 0.0, 21.5, 55.0, 100.0)
+_r11ig_units = _r9f41_const.TEMPERATURE_UNIT_TO_C
+_r11ig_trip = [
+    (_u, _c, inputs_mod.normalize_temperature_c(inputs_mod.temperature_from_c(_c, _u), _u))
+    for _u in _r11ig_units
+    for _c in _R11IG_TEMPS_C
+]
+R.check(
+    "temperature_from_c inverts every unit row the reader converts (D7-s3-01)",
+    any(_f != 1.0 for _o, _f in _r11ig_units.values())
+    and all(_back is not None and _p8_math.isclose(_back, _c, abs_tol=1e-9) for _u, _c, _back in _r11ig_trip),
+    f"{[t for t in _r11ig_trip if t[2] is None or not _p8_math.isclose(t[2], t[1], abs_tol=1e-9)]}",
+)
 _p8_norm = getattr(inputs_mod, "normalize_price_per_kwh", None)
 _P8_FACTORS = {
     "SEK/kWh": 1.0,
diff --git a/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json
new file mode 100644
index 0000000000..2161ad64c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/__init__.py:async_migrate_entry GUARD_OFF ab300483",
+  "killed_by": "tests/entities.py",
+  "old": "        if repairs:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json
new file mode 100644
index 0000000000..8ef22ec1ad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_interval_minutes RETURN_DEL 3410ce8b",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return minutes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json
new file mode 100644
index 0000000000..13f963296c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader._begin GUARD_OFF 6aa9ea3a",
+  "killed_by": "tests/features.py",
+  "old": "        if not isinstance(entity_id, str):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json b/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json
new file mode 100644
index 0000000000..c5754e5738
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:parse_bool RETURN_DEL 3434dfb6",
+  "killed_by": "tests/features.py",
+  "old": "    return None if number is None else number != 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json
new file mode 100644
index 0000000000..620f1267b2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block CMP_BOUND 30aea580",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    kept = [i for i, t in enumerate(times) if t >= floor]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`kept = [i for i, t in enumerate(times) if t > floor]`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json
new file mode 100644
index 0000000000..4a1284b11b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block CMP_BOUND 4d7eb319",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    if len(kept) < 2:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(kept) <= 2:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/open_meteo.py b/tests/open_meteo.py
index 5ab1127308..dc8679ba26 100644
--- a/tests/open_meteo.py
+++ b/tests/open_meteo.py
@@ -123,6 +123,40 @@ def block(start_hour: int, values, step_minutes: int = 60) -> dict:
 
 print("== parsing ==")
 
+# D1-s3-03: a year-1 stamp has no representable span, so mean_over raised
+# OverflowError for every plan step and every solve failed.
+_y1 = block(0, [100.0, 200.0, 300.0, 400.0])
+_y1 = {
+    "time": ["0001-01-01T00:00", "0001-01-01T01:00"] + _y1["time"],
+    "shortwave_radiation": [500.0, 500.0] + _y1["shortwave_radiation"],
+}
+_y1_series = om._parse_block(_y1, "shortwave_radiation")
+_y1_start = datetime(2026, 8, 21, 0, 0, tzinfo=UTC)
+try:
+    _y1_mean = _y1_series.mean_over(_y1_start, _y1_start + timedelta(hours=3))
+except OverflowError as exc:  # the defect
+    _y1_mean = exc
+_y1_clean = om._parse_block(block(0, [100.0, 200.0, 300.0, 400.0]), "shortwave_radiation")
+check(
+    "a stamp with no representable span is dropped, and the block still averages",
+    datetime(1, 1, 1, 0, 0, tzinfo=UTC) not in _y1_series.times
+    and datetime(1, 1, 1, 1, 0, tzinfo=UTC) in _y1_series.times
+    and all(t - _y1_series.resolution < t for t in _y1_series.times)
+    and _y1_series.resolution == timedelta(hours=1)
+    and approx(_y1_mean, _y1_clean.mean_over(_y1_start, _y1_start + timedelta(hours=3))),
+    f"times={_y1_series.times[:2]} mean={_y1_mean!r}",
+)
+_y1_two = om._parse_block(
+    {"time": ["0001-01-01T00:00", "2026-08-21T00:00", "2026-08-21T01:00"],
+     "shortwave_radiation": [1.0, 100.0, 200.0]},
+    "shortwave_radiation",
+)
+check(
+    "the floor keeps a stamp exactly one resolution past year 1, and two kept samples are a series",
+    len(_y1_two.times) == 2 and _y1_two.values == (100.0, 200.0),
+    f"times={_y1_two.times}",
+)
+
 hourly = om._parse_block(block(0, [0.0, 0.0, 100.0, 300.0, 500.0]), "shortwave_radiation")
 check("parses an hourly block", len(hourly.times) == 5)
 check("infers hourly resolution", hourly.resolution == timedelta(hours=1))
diff --git a/tests/wood_advisor.py b/tests/wood_advisor.py
index 0e90ed3666..85a8d84dd1 100644
--- a/tests/wood_advisor.py
+++ b/tests/wood_advisor.py
@@ -224,6 +224,27 @@ R.check(
     _lighting(_lead90) == (_at(4, 30), _at(6)),
     repr(_lighting(_lead90)),
 )
+_lead_views = {}
+for _lead in ("0", "240", "1440", "1440.5", "1e12", "-5", "nan"):
+    try:
+        _lead_views[_lead] = _lighting(
+            _wood_view({6, 7}, config={**_WOOD_READY, "wood_lighting_lead_minutes": float(_lead)})
+        )
+    except (OverflowError, ValueError) as _exc:
+        _lead_views[_lead] = repr(_exc)
+R.check(
+    "a lead inside [0, a day] is its own: 0 lights at the window's start, 240 four hours "
+    "before, and a day's lead lights now",
+    _lead_views["0"] == (_at(6), _at(6)) and _lead_views["240"] == (_at(2), _at(6))
+    and _lead_views["1440"] == (_at(0), _at(6)),
+    repr(_lead_views),
+)
+R.check(
+    "a stored lead outside [0, a day] is the default 60 min: 1e12 does not overflow "
+    "the window's datetime, and a negative or NaN lead is not one",
+    all(_lead_views[_bad] == (_at(5), _at(6)) for _bad in ("1440.5", "1e12", "-5", "nan")),
+    repr(_lead_views),
+)
 _now_open = _wood_view({0, 1})
 R.check(
     "a window open at the plan's first step lights now, never in the past",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
