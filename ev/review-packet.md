# Review packet #3219
head: 140df0268a1065bf186d357ec75e8524a3c4b242
base: d91e464aafe8b9f3c763ecc495013e957a303d03

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=126950140665 skipped
cancel-superseded id=126953441073 queued
prelude id=126953440965 queued
refresh id=126953440853 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/replay.py
             `tests/replay.py` is in the tree at this head
  ok         python3 tests/replay.py
             `tests/replay.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
deleted file mode 100644
index c3450f3d2..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles GUARD_OFF 97aacf73",
-  "killed_by": "tests/entities.py",
-  "old": "            if isinstance(value, list):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/debugger.py b/custom_components/heatpump_optimizer/debugger.py
index 285b28d20..ce9ead047 100644
--- a/custom_components/heatpump_optimizer/debugger.py
+++ b/custom_components/heatpump_optimizer/debugger.py
@@ -451,6 +451,7 @@ def replay_document(
         recorder_schema=schema, entry=wants["entry"], inputs=inputs,
         published=wants["published"], price_series_entity=price,
         states={eid: states.get(eid, []) for eid in sorted(inputs | set(wants["published"]))},
+        conf=conf,
     )
     return replay_doc.seal(raw, conf)
 
diff --git a/custom_components/heatpump_optimizer/replay_doc.py b/custom_components/heatpump_optimizer/replay_doc.py
index d177af2c3..a7cbe681a 100644
--- a/custom_components/heatpump_optimizer/replay_doc.py
+++ b/custom_components/heatpump_optimizer/replay_doc.py
@@ -522,10 +522,31 @@ def state_rows(records: Iterable[tuple[Any, Any, Any, Any]]) -> list[list[Any]]:
 # --- masking every entity id ---------------------------------------------------
 
 
-def entity_roles(entry: Json, price_series_entity: str | None) -> dict[str, str]:
-    """``{id: <domain>.<role>}`` for every id the entry holds under a key, options
-    before data, keys in order, then the price series as ``price``. An id keeps
-    its first role; a role a second id would take leaves that id to the hash."""
+def _role_claims(entry: Json, conf: frozenset[str] | None) -> Iterable[tuple[object, str]]:
+    """``(value, role)`` for every entry value that may name an id, options before
+    data, keys in order: with ``conf`` only the keys ``sanitise`` keeps, and a
+    list counting only its ids, so the roles agree with those ``_unmasked``
+    re-derives from the sanitised entry, where a dropped key or item is gone."""
+    for section in ("options", "data"):
+        block = entry.get(section)
+        for key, value in sorted(block.items() if isinstance(block, dict) else ()):
+            if conf is not None and (key not in conf or SECRET_KEY.search(str(key))):
+                continue
+            role = re.sub(r"_entit(y|ies)$", "", str(key))
+            if not isinstance(value, list):
+                yield value, role
+                continue
+            if conf is not None:
+                value = [v for v in value if isinstance(v, str) and ENTITY_ID.match(v)]
+            for i, item in enumerate(value, start=1):
+                yield item, f"{role}_n{i}"
+
+
+def entity_roles(entry: Json, price_series_entity: str | None,
+                 conf: frozenset[str] | None = None) -> dict[str, str]:
+    """``{id: <domain>.<role>}`` for every id the entry holds under a key
+    (``_role_claims``), then the price series as ``price``. An id keeps its first
+    role; a role a second id would take leaves that id to the hash."""
     roles: dict[str, str] = {}
 
     def claim(eid: object, role: str) -> None:
@@ -534,15 +555,8 @@ def entity_roles(entry: Json, price_series_entity: str | None) -> dict[str, str]
             if rid not in roles.values():
                 roles[eid] = rid
 
-    for section in ("options", "data"):
-        block = entry.get(section)
-        for key, value in sorted(block.items() if isinstance(block, dict) else ()):
-            role = re.sub(r"_entit(y|ies)$", "", str(key))
-            if isinstance(value, list):
-                for i, item in enumerate(value, start=1):
-                    claim(item, f"{role}_n{i}")
-            else:
-                claim(value, role)
+    for value, role in _role_claims(entry, conf):
+        claim(value, role)
     for role in ("price", "price_series"):
         claim(price_series_entity, role)
     return roles
@@ -556,10 +570,10 @@ def hashed_id(entity_id: str, key: str) -> str:
     return f"{entity_id.split('.', 1)[0]}.e_{digest[:10]}"
 
 
-def mask_ids(doc: Json, key: str) -> Json:
+def mask_ids(doc: Json, key: str, conf: frozenset[str] | None = None) -> Json:
     """``doc`` with every entity id, at any depth and as any dict key,
     renamed through ``entity_roles`` else ``hashed_id``: one mapping."""
-    roles = entity_roles(doc.get("entry") or {}, doc.get("price_series_entity"))
+    roles = entity_roles(doc.get("entry") or {}, doc.get("price_series_entity"), conf)
 
     def rename(node: object) -> object:
         if isinstance(node, str) and ENTITY_ID.match(node):
@@ -626,6 +640,7 @@ def document(
     *, time_zone: str, window: tuple[str, str], recorder_schema: int | None,
     entry: Json, inputs: Iterable[str], published: Iterable[str],
     price_series_entity: str | None, states: dict[str, list[list[Any]]],
+    conf: frozenset[str] | None = None,
 ) -> Json:
     """The unsanitised ``hpo-replay/1`` document, every entity id masked
     (``mask_ids``, keyed by the entry's id); ``seal`` makes it writable."""
@@ -644,7 +659,7 @@ def document(
         "published": sorted(published),
         "price_series_entity": price_series_entity,
         "states": states,
-    }, str(entry.get("entry_id") or ""))
+    }, str(entry.get("entry_id") or ""), conf)
 
 
 def _copy(value: str) -> re.Pattern[str]:
diff --git a/dev/programme/delivery/3219.md b/dev/programme/delivery/3219.md
new file mode 100644
index 000000000..33ccc4fb1
--- /dev/null
+++ b/dev/programme/delivery/3219.md
@@ -0,0 +1 @@
+- [#3219](https://github.com/tvofi/heatpump_optimizer/pull/3219) — **open**, R10-FLY-REPLAY-MASK: fly replay mask (R10-FLY-REPLAY-MASK)
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json b/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
deleted file mode 100644
index c3450f3d2..000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles GUARD_OFF 97aacf73",
-  "killed_by": "tests/entities.py",
-  "old": "            if isinstance(value, list):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/replay.py b/tests/replay.py
index e675cdb77..e6ed289a3 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -1509,6 +1509,24 @@ def mask_checks() -> list[tuple[str, bool, str]]:
     return res + mask_seam_checks()
 
 
+def _sealed_options(states: dict, options: dict, plant: bool = False) -> tuple[dict | None, str]:
+    """``document`` then ``seal`` over ``options``; ``plant`` skips the mask."""
+    import export
+
+    conf = export.entry_keys(*export.default_const_paths())
+    raw = export._doc.document(
+        time_zone="UTC", window=("2026-01-15T00:00:00+00:00", "2026-01-16T00:00:00+00:00"),
+        recorder_schema=48, entry={"entry_id": "01JX", "data": {}, "options": options},
+        inputs=[k for k in states if k != "sensor.hpo_out"], published=["sensor.hpo_out"],
+        price_series_entity=None, states=states, conf=conf)
+    if plant:
+        raw["states"]["sensor.planted_unmasked"] = []
+    try:
+        return export._doc.seal(raw, conf), ""
+    except export._doc.Refused as err:
+        return None, str(err)
+
+
 def mask_seam_checks() -> list[tuple[str, bool, str]]:
     """Every place an id can sit, each alone: ``mask_ids`` renames it and
     ``mask_violations`` refuses it unrenamed -- a dict key anywhere (an
@@ -1545,6 +1563,24 @@ def mask_seam_checks() -> list[tuple[str, bool, str]]:
         stray = [f"raised {type(err).__name__}"]
     res.append(("mask:a_payload_that_is_no_document_has_no_violation", stray == [],
                 f"a list payload: {stray}"))
+    # R10-FLY-REPLAY-MASK: an id configured under an entry key ``sanitise`` drops
+    # (a key off the allowlist) or inside a list beside a non-id item took a role
+    # ``seal`` could not re-derive, and refused the whole replay.
+    ts = "2026-01-15T00:00:00+00:00"
+    rows = {"sensor.in": [[ts, "1", None, None]], "sensor.off_list": [[ts, "2", None, None]],
+            "sensor.late": [[ts, "3", None, None]], "sensor.hpo_out": [[ts, "4", None, None]]}
+    for name, opts in (("key_off_the_allowlist", {"legacy_probe_entity": "sensor.off_list"}),
+                       ("list_beside_a_non_id", {"room_sensor_entities": ["", "sensor.late"]})):
+        sealed, why = _sealed_options(rows, opts)
+        res.append((f"mask:id_under_{name}_seals_masked",
+                    sealed is not None and bool(sealed["states"])
+                    and not any(i in json.dumps(sealed) for i in ("off_list", "late")),
+                    why or f"{len(sealed['states'])} states"))
+    plain, why = _sealed_options(rows, {"outdoor_temp_entity": "sensor.in"})
+    res.append(("mask:clean_export_writes_a_non_empty_replay",
+                plain is not None and len(plain["states"]) == 4, why))
+    planted, _ = _sealed_options(rows, {}, plant=True)
+    res.append(("mask:planted_unmasked_id_still_refused", planted is None, "planted id"))
     # Carry 12 (D15-s1-04): a bool under a credential-named key carries no
     # credential -- ``_collect_strings`` already skips it, and ``_walk`` must
     # agree -- while a string under one still does (the null).
@@ -1576,7 +1612,8 @@ def _sealed(states: dict, entry_data: dict) -> tuple[dict | None, str]:
         time_zone="UTC", window=("2026-01-15T00:00:00+00:00", "2026-01-16T00:00:00+00:00"),
         recorder_schema=48, entry={"entry_id": "01JX", "data": entry_data, "options": {}},
         inputs=[k for k in states if k != "sensor.hpo_out"], published=["sensor.hpo_out"],
-        price_series_entity=None, states=states)
+        price_series_entity=None, states=states,
+        conf=export.entry_keys(*export.default_const_paths()))
     try:
         return export._doc.seal(raw, export.entry_keys(*export.default_const_paths())), ""
     except export._doc.Refused as err:
diff --git a/tools/replay/export.py b/tools/replay/export.py
index 657ae237d..1a7926522 100644
--- a/tools/replay/export.py
+++ b/tools/replay/export.py
@@ -492,7 +492,7 @@ def build_export(
     raw = _doc.document(
         time_zone=tz_name, window=(start.isoformat(), end.isoformat()),
         recorder_schema=version, entry=entry, inputs=inputs, published=published,
-        price_series_entity=price_entity, states=states,
+        price_series_entity=price_entity, states=states, conf=conf,
     )
     quiet = quiet_inputs(raw)
     if quiet:

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
