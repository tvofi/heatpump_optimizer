# Review packet #3219
head: aca500910b8917fd41516f5f290c6a18f1727b8b
base: 662b29669ec5beb6773fa8b62ac98f2b020be90e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127046044460 neutral
arch-score id=127046940581 skipped
arch-score / arch-score id=127045678548 success
arm id=127043587299 skipped
budget-raise-gate id=127046941135 skipped
budget-raise-gate / budget-raise-gate id=127045678342 success
cancel-superseded id=127044448692 success
codeql id=127046941038 skipped
codeql / Analyze (actions) id=127045678382 success
codeql / Analyze (javascript-typescript) id=127045678263 success
codeql / Analyze (python) id=127045678326 in_progress
gate id=127046941758 cancelled
governance id=127046940546 skipped
governance / delivery-status id=127045678404 failure
governance / delivery-status-publish id=127045680822 skipped
governance / env-matrix id=127045678564 success
governance / instrument-self-tests id=127045678420 in_progress
governance / policy-docs id=127045678503 success
governance / record id=127045680530 skipped
governance / wave-script id=127045678521 success
hassfest id=127046941405 skipped
hassfest / hassfest id=127045678534 success
kernel-points id=127046941392 skipped
pr-contract id=127046942229 skipped
prelude id=127044449071 cancelled
refresh id=127044449161 success
tests id=127046941423 skipped
tests / arch-instrument id=127046649452 success
tests / briefs id=127045678411 success
tests / browser id=127046649313 success
tests / closure-scope id=127045678426 success
tests / closures id=127046649449 in_progress
tests / coverage id=127046649409 in_progress
tests / fast (3.14) id=127046649354 in_progress
tests / mutation id=127045678304 failure
tests / mutation-pins (1) id=127046066940 in_progress
tests / nightly-ha id=127046650778 skipped
tests / nightly-status id=127045678253 failure
tests / replay id=127046649273 in_progress
tests / typing id=127046649293 success
validate id=127046941241 skipped
validate / validate-hacs id=127045678237 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
red-unanswered: concluded red check `prelude` is not named in ## Red checks
required-red: required context `gate` concluded failure at aca500910b8917fd41516f5f290c6a18f1727b8b

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3 -c "import sys; sys.path[:0]=['tests','tests/hastub','tools/replay']; import replay; r=replay.mask_checks(); print(len(r), [n for n,ok,w in r if not ok])"
             python3 runs an inline script rather than a file
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/audit/seat/cloud-setup.sh
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head

FIGURES: 3 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.BOOLOP.3f780d78.json b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.BOOLOP.3f780d78.json
new file mode 100644
index 000000000..faad4d1f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.BOOLOP.3f780d78.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_role_claims BOOLOP 3f780d78",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if conf is not None and (key not in conf or SECRET_KEY.search(str(key))):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if conf is not None or (key not in conf or SECRET_KEY.search(str(key))):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.3f780d78.json
similarity index 61%
rename from tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
rename to tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.3f780d78.json
index c3450f3d2..667c37ecb 100644
--- a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.3f780d78.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles GUARD_OFF 97aacf73",
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_role_claims GUARD_OFF 3f780d78",
   "killed_by": "tests/entities.py",
-  "old": "            if isinstance(value, list):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+  "old": "            if conf is not None and (key not in conf or SECRET_KEY.search(str(key))):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.879cf566.json b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.879cf566.json
new file mode 100644
index 000000000..a3cf79904
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.879cf566.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_role_claims GUARD_OFF 879cf566",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if not isinstance(value, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}


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
index d177af2c3..e068b78ae 100644
--- a/custom_components/heatpump_optimizer/replay_doc.py
+++ b/custom_components/heatpump_optimizer/replay_doc.py
@@ -522,10 +522,33 @@ def state_rows(records: Iterable[tuple[Any, Any, Any, Any]]) -> list[list[Any]]:
 # --- masking every entity id ---------------------------------------------------
 
 
-def entity_roles(entry: Json, price_series_entity: str | None) -> dict[str, str]:
-    """``{id: <domain>.<role>}`` for every id the entry holds under a key, options
-    before data, keys in order, then the price series as ``price``. An id keeps
-    its first role; a role a second id would take leaves that id to the hash."""
+def _role_claims(entry: Json, conf: frozenset[str] | None) -> Iterable[tuple[object, str]]:
+    """``(value, role)`` for every entry value that may name an id, options before
+    data, keys in order: with ``conf`` only the keys ``sanitise`` keeps, each
+    through ``_entry_shape`` as ``sanitise`` shapes it, so the roles agree with those ``_unmasked``
+    re-derives from the sanitised entry, where a dropped key or item is gone."""
+    for section in ("options", "data"):
+        block = entry.get(section)
+        for key, value in sorted(block.items() if isinstance(block, dict) else ()):
+            if conf is not None and (key not in conf or SECRET_KEY.search(str(key))):
+                continue
+            if conf is not None:
+                # the one predicate ``sanitise`` applies; a _DROP it returns is no str,
+                # so the consumer's id test passes it over
+                value = _entry_shape(str(key), value)
+            role = re.sub(r"_entit(y|ies)$", "", str(key))
+            if not isinstance(value, list):
+                yield value, role
+                continue
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
@@ -534,15 +557,8 @@ def entity_roles(entry: Json, price_series_entity: str | None) -> dict[str, str]
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
@@ -556,10 +572,10 @@ def hashed_id(entity_id: str, key: str) -> str:
     return f"{entity_id.split('.', 1)[0]}.e_{digest[:10]}"
 
 
-def mask_ids(doc: Json, key: str) -> Json:
+def mask_ids(doc: Json, key: str, conf: frozenset[str] | None = None) -> Json:
     """``doc`` with every entity id, at any depth and as any dict key,
     renamed through ``entity_roles`` else ``hashed_id``: one mapping."""
-    roles = entity_roles(doc.get("entry") or {}, doc.get("price_series_entity"))
+    roles = entity_roles(doc.get("entry") or {}, doc.get("price_series_entity"), conf)
 
     def rename(node: object) -> object:
         if isinstance(node, str) and ENTITY_ID.match(node):
@@ -626,6 +642,7 @@ def document(
     *, time_zone: str, window: tuple[str, str], recorder_schema: int | None,
     entry: Json, inputs: Iterable[str], published: Iterable[str],
     price_series_entity: str | None, states: dict[str, list[list[Any]]],
+    conf: frozenset[str] | None = None,
 ) -> Json:
     """The unsanitised ``hpo-replay/1`` document, every entity id masked
     (``mask_ids``, keyed by the entry's id); ``seal`` makes it writable."""
@@ -644,7 +661,7 @@ def document(
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
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.BOOLOP.3f780d78.json b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.BOOLOP.3f780d78.json
new file mode 100644
index 000000000..faad4d1f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.BOOLOP.3f780d78.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_role_claims BOOLOP 3f780d78",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if conf is not None and (key not in conf or SECRET_KEY.search(str(key))):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if conf is not None or (key not in conf or SECRET_KEY.search(str(key))):`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.3f780d78.json
similarity index 61%
rename from tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
rename to tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.3f780d78.json
index c3450f3d2..667c37ecb 100644
--- a/tests/mutation_ledger/killed_by/replay_doc.py/entity_roles.GUARD_OFF.97aacf73.json
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.3f780d78.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:entity_roles GUARD_OFF 97aacf73",
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_role_claims GUARD_OFF 3f780d78",
   "killed_by": "tests/entities.py",
-  "old": "            if isinstance(value, list):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+  "old": "            if conf is not None and (key not in conf or SECRET_KEY.search(str(key))):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.879cf566.json b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.879cf566.json
new file mode 100644
index 000000000..a3cf79904
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/_role_claims.GUARD_OFF.879cf566.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:_role_claims GUARD_OFF 879cf566",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if not isinstance(value, list):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/replay.py b/tests/replay.py
index e675cdb77..7e7aa8a18 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -1509,6 +1509,66 @@ def mask_checks() -> list[tuple[str, bool, str]]:
     return res + mask_seam_checks()
 
 
+def _sealed_options(states: dict, options: dict, plant: bool = False,
+                    extra_conf: tuple[str, ...] = ()) -> tuple[dict | None, str]:
+    """``document`` then ``seal`` over ``options``; ``plant`` skips the mask."""
+    import export
+
+    conf = export.entry_keys(*export.default_const_paths()) | frozenset(extra_conf)
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
+def _conf_reaches_writers_checks() -> list[tuple[str, bool, str]]:
+    """``build_export`` (tools) and ``debugger.replay_document`` (the integration)
+    each seal an entry holding ``legacy_probe_entity``, a key off the allowlist,
+    beside the key that rightly names the same sensor; deleting ``conf=conf`` at
+    either ``document`` call refuses the replay."""
+    import export
+    import synthesize
+
+    sys.path.insert(0, str(ROOT / "custom_components"))
+    from heatpump_optimizer import debugger
+
+    outdoor = synthesize.ENTRY_DATA["outdoor_temp_entity"]
+    probed = {**synthesize.ENTRY_DATA, "legacy_probe_entity": outdoor}
+    saved = synthesize.ENTRY_DATA
+    synthesize.ENTRY_DATA = probed
+    try:
+        with tempfile.TemporaryDirectory() as tmp:
+            db = synthesize.write_install(Path(tmp))
+            payload = export.build_export(
+                Path(tmp), db, 1, (synthesize.DAY + timedelta(days=1)).date().isoformat(),
+                None, [], None)
+        tool, why_tool = payload is not None and outdoor not in json.dumps(payload), "written"
+    except SystemExit as err:
+        tool, why_tool = False, f"refused: {err}"
+    finally:
+        synthesize.ENTRY_DATA = saved
+    start = datetime(2026, 1, 15, tzinfo=timezone.utc)
+    wants = {"inputs": [outdoor], "candidates": None, "config": {}, "published": [],
+             "entry": {"entry_id": "01JX", "data": {}, "options": {
+                 "legacy_probe_entity": outdoor, "outdoor_temp_entity": outdoor}}}
+    try:
+        doc = debugger.replay_document(
+            wants, [], {outdoor: []}, (start, start + timedelta(days=1)), "UTC", 48,
+            export.entry_keys(*export.default_const_paths()))
+        integ, why_int = outdoor not in json.dumps(doc), "sealed"
+    except Exception as err:  # noqa: BLE001 -- the refusal is the finding
+        integ, why_int = False, f"{type(err).__name__}: {err}"
+    return [("mask:build_export_passes_conf_to_document", tool, why_tool),
+            ("mask:debugger_replay_document_passes_conf_to_document", integ, why_int)]
+
+
 def mask_seam_checks() -> list[tuple[str, bool, str]]:
     """Every place an id can sit, each alone: ``mask_ids`` renames it and
     ``mask_violations`` refuses it unrenamed -- a dict key anywhere (an
@@ -1545,6 +1605,40 @@ def mask_seam_checks() -> list[tuple[str, bool, str]]:
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
+    # A list under a key that does not end ``_entities`` is kept whole by
+    # ``sanitise`` (``_entry_shape``), so a non-id item beside an id must not
+    # refuse; under an ``_entities`` key (none is in the installed allowlist, so
+    # a synthetic one) the non-id item is dropped on both sides, never refused.
+    for name, key, extra in (("list_under_a_kept_key_beside_a_non_id", "after_save", ()),
+                             ("list_under_an_entities_key_beside_a_non_id", "zone_entities",
+                              ("zone_entities",))):
+        sealed, why = _sealed_options(rows, {key: ["abc", "sensor.late"]}, extra_conf=extra)
+        res.append((f"mask:id_in_{name}_seals_masked",
+                    sealed is not None and bool(sealed["states"])
+                    and "late" not in json.dumps(sealed),
+                    why or f"{len(sealed['states'])} states"))
+    # ``conf`` must reach ``document`` from both writers: an entry key off the
+    # allowlist holding an id another key also holds takes the earlier role, which
+    # ``seal`` cannot re-derive, unless ``document`` was given the allowlist.
+    res += _conf_reaches_writers_checks()
+    plain, why = _sealed_options(rows, {"outdoor_temp_entity": "sensor.in"})
+    res.append(("mask:clean_export_writes_a_non_empty_replay",
+                plain is not None and len(plain["states"]) == 4, why))
+    planted, _ = _sealed_options(rows, {}, plant=True)
+    res.append(("mask:planted_unmasked_id_still_refused", planted is None, "planted id"))
     # Carry 12 (D15-s1-04): a bool under a credential-named key carries no
     # credential -- ``_collect_strings`` already skips it, and ``_walk`` must
     # agree -- while a string under one still does (the null).
@@ -1576,7 +1670,8 @@ def _sealed(states: dict, entry_data: dict) -> tuple[dict | None, str]:
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
