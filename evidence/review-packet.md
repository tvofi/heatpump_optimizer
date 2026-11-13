# Review packet #3540
head: eeaa91d5bf60211f38d9a9d9d217a2e976ff8cc7
base: 5345766b417ce64e318c1f96092363922d83e740

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131754884425 success
arch-score / arch-score id=131766981473 success
arm id=131754564479 skipped
budget-raise-gate / budget-raise-gate id=131766982650 success
cancel-superseded id=131767018323 success
codeql id=131766982724 skipped
codeql / Analyze (actions) id=131754827732 success
codeql / Analyze (javascript-typescript) id=131754827819 success
codeql / Analyze (python) id=131754827797 success
gate id=131766981808 success
governance id=131766981724 skipped
governance / delivery-status id=131754827864 success
governance / delivery-status-publish id=131754829671 skipped
governance / env-matrix id=131754830224 success
governance / instrument-self-tests id=131754828053 success
governance / policy-docs id=131754827942 success
governance / record id=131754830197 skipped
governance / wave-script id=131754827980 success
hassfest id=131766982494 skipped
hassfest / hassfest id=131754827820 success
kernel-points id=131766981454 skipped
pr-contract id=131766982759 skipped
pr-contract / pr-contract id=131765528934 success
prelude id=131766981235 success
refresh id=131766980236 success
sweep-self id=131767287119 skipped
tests id=131767024031 skipped
tests / arch-instrument id=131755191735 success
tests / briefs id=131754828116 success
tests / browser id=131755191805 success
tests / ci-ratchet id=131765301341 skipped
tests / claims-autofix id=131759894377 skipped
tests / closure-scope id=131754828458 success
tests / closures id=131755191741 success
tests / closures-autofix id=131764095967 skipped
tests / coverage id=131755191841 success
tests / coverage-ratchet id=131765299794 success
tests / fast (3.14) id=131755191694 success
tests / graders-head-copy id=131765299796 success
tests / lane-proofs id=131765299832 success
tests / mutation id=131754827764 success
tests / mutation-autofix id=131755142282 skipped
tests / mutation-pins id=131755141586 skipped
tests / nightly-ha (2025.2.0) id=131755191621 success
tests / nightly-ha (stable) id=131755191793 success
tests / nightly-status id=131754827991 failure
tests / replay id=131755194425 skipped
tests / typing id=131755191627 success
validate id=131766981999 skipped
validate / validate-hacs id=131754827888 success

## Refusals
handoff-not-applied: handoff/r10-hotfix-nightly-ha 1dee0df2a4193d29fedd22e5d322717737a37c53 is not an ancestor of eeaa91d5bf60211f38d9a9d9d217a2e976ff8cc7

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tests/nightly_ha.py
             `tests/nightly_ha.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3540.md b/dev/programme/delivery/3540.md
new file mode 100644
index 0000000000..eaa45d31b4
--- /dev/null
+++ b/dev/programme/delivery/3540.md
@@ -0,0 +1 @@
+- [#3540](https://github.com/tvofi/heatpump_optimizer/pull/3540) — **open**, R10-HOTFIX-NIGHTLY-HA: r10 hotfix nightly ha (R10-HOTFIX-NIGHTLY-HA)
diff --git a/tests/entities.py b/tests/entities.py
index 9940663c19..cdee69a57c 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -17772,6 +17772,7 @@ R.check(
     set(_nightly.A4_INSIDE) <= set(_nightly.INSIDE_CHECKS)
     and set(_nightly.A4_INSIDE)
     == {
+        "a4:bridged",
         "a4:failed",
         "a4:unavailable",
         "a4:buttons",
@@ -17795,6 +17796,49 @@ R.check(
     and "send_response(401)" not in _a4_serve_src,
     "A4 must go through the Tibber counterparty (E57), not the FakeCoordinator poke",
 )
+# The price source is exhausted at the counterparty (a 200 with an ended curve,
+# which pull_prices accepts), never by writing the coordinator's prices.
+_a4_end_src = _inspect.getsource(_nightly.end_price_curve)
+R.check(
+    "A4 exhausts the published prices at the counterparty, not the coordinator",
+    "end_price_curve(True)" in _a4_walk_src
+    and "end_price_curve(False)" in _a4_walk_src
+    and "_prices" not in _a4_walk_src
+    and "_PRICE_CURVE_ENDED" in _a4_end_src
+    and "_PRICE_CURVE_ENDED" in _a4_serve_src
+    and "_ENDED_CURVE_AGE" in _a4_serve_src
+    and _nightly._ENDED_CURVE_AGE >= _nightly.timedelta(days=1),
+    "A4 phase 2 must reach UpdateFailed through the fake Tibber's ended curve",
+)
+_a4_bridge_before = [
+    {"entity_id": "sensor.a", "state": "1"},
+    {"entity_id": "button.b", "state": "unknown"},
+]
+_a4_bridge_up = [dict(r) for r in _a4_bridge_before]
+_a4_bridge_down = [
+    {"entity_id": "sensor.a", "state": "unavailable"},
+    {"entity_id": "button.b", "state": "unavailable"},
+]
+_a4_br_ok = _nightly.Checks()
+_nightly.check_a4_bridged(_a4_br_ok, True, True, _a4_bridge_before, _a4_bridge_up)
+_a4_br_failed = _nightly.Checks()
+_nightly.check_a4_bridged(_a4_br_failed, False, True, _a4_bridge_before, _a4_bridge_up)
+_a4_br_norepair = _nightly.Checks()
+_nightly.check_a4_bridged(_a4_br_norepair, True, False, _a4_bridge_before, _a4_bridge_up)
+_a4_br_down = _nightly.Checks()
+_nightly.check_a4_bridged(_a4_br_down, True, True, _a4_bridge_before, _a4_bridge_down)
+_a4_br_empty = _nightly.Checks()
+_nightly.check_a4_bridged(_a4_br_empty, True, True, (), _a4_bridge_up)
+R.check(
+    "a4:bridged fails a failed update, a missing repair, an unavailable entity and an empty before-set",
+    all(
+        "a4:bridged" in c.failures()
+        for c in (_a4_br_failed, _a4_br_norepair, _a4_br_down, _a4_br_empty)
+    )
+    and "a4:bridged" not in _a4_br_ok.failures(),
+    f"ok={_a4_br_ok.results.get('a4:bridged')} failed={_a4_br_failed.results.get('a4:bridged')} "
+    f"norepair={_a4_br_norepair.results.get('a4:bridged')} down={_a4_br_down.results.get('a4:bridged')}",
+)
 _a4_failed_ok = _nightly.Checks()
 _nightly.check_a4_failed(_a4_failed_ok, False)
 _a4_failed_bad = _nightly.Checks()
@@ -17885,7 +17929,7 @@ R.check(
     "and passing A4 checks still keep their detail",
     all(
         v[1]
-        for c in (_a4_failed_ok, _a4_un_ok, _a4_btn_ok, _a4_ns_ok, _a4_rc_ok)
+        for c in (_a4_failed_ok, _a4_un_ok, _a4_btn_ok, _a4_ns_ok, _a4_rc_ok, _a4_br_ok)
         for n, v in c.results.items()
         if n.startswith("a4:")
     ),
diff --git a/tests/nightly_ha.py b/tests/nightly_ha.py
index 87cc53eec6..0d860f9dfb 100644
--- a/tests/nightly_ha.py
+++ b/tests/nightly_ha.py
@@ -32,8 +32,9 @@ WHAT THIS LANE DOES NOT COVER, stated the way ``deployment_shape.py`` states
 its own limit:
 
 * **Tibber.** Prices are the one input whose absence stops a solve outright
-  (``_fetch_tibber_prices`` raises ``UpdateFailed``), and the real endpoint
-  needs a live account. ``api.tibber.com`` is redirected to a local TLS server
+  (``_fetch_tibber_prices`` raises ``UpdateFailed`` once the last published
+  prices no longer cover now; while they do, a failed fetch is bridged), and
+  the real endpoint needs a live account. ``api.tibber.com`` is redirected to a local TLS server
   in the container by ``--add-host``, whose certificate is added to the trust
   store the shared aiohttp session uses. Production code is not patched: the
   real URL, the real session and real TLS are exercised; only the counterparty
@@ -86,7 +87,10 @@ this merge base by listing those identifiers (not by carrying a filed total):
 E71, E33, E19, E45, E6, E74, E73, E77, E47, E113, E137, E138, E78, E7, E119.
 A4's named set is the §4 A4 row, listed (not a carried total): E57, E76, E30,
 E77, E75, E72. It breaks the Tibber counterparty (HTTP 500, not 401 -- 401
-starts reauth) and does not poke ``last_update_success``. The counts are
+starts reauth) in two phases and does not poke ``last_update_success`` or the
+coordinator's prices: with the last published prices still covering now the
+500 is bridged (``a4:bridged``, #3454); once the counterparty has answered 200
+with a curve that ended before now, the 500 fails the update. The counts are
 bullet-level, stable in ranking and about +/-15 in absolute terms; the two
 largest classes in the record -- solver numbers and card geometry, 68 escapes
 between them -- are out of this lane's reach by construction, so this is the
@@ -169,7 +173,14 @@ LOG_NAME = "home-assistant.log"
 
 TIBBER_HOST = "api.tibber.com"
 # HTTP 500, not 401: 401 starts reauth (D10-08) and is a different path from E57.
+# The 500 raises UpdateFailed only once the published prices no longer cover now;
+# before that it is bridged (see _PRICE_CURVE_ENDED).
 _PRICE_SOURCE_BROKEN = False
+# A 200 whose curve ended before now: the counterparty answers, but nothing it
+# published covers the present (the only way, short of poking the coordinator,
+# to exhaust the last published prices; pull_prices applies no expiry filter).
+_PRICE_CURVE_ENDED = False
+_ENDED_CURVE_AGE = timedelta(days=3)
 
 MARKER = "<<<nightly-ha-json>>>"
 
@@ -196,6 +207,7 @@ A4_NAMED_ESCAPES = (
     "E57", "E76", "E30", "E77", "E75", "E72",
 )
 A4_INSIDE = (
+    "a4:bridged",
     "a4:failed",
     "a4:unavailable",
     "a4:buttons",
@@ -1352,6 +1364,12 @@ def break_price_source(broken: bool) -> None:
     _PRICE_SOURCE_BROKEN = bool(broken)
 
 
+def end_price_curve(ended: bool) -> None:
+    """Make the Tibber counterparty answer 200 with a curve that ended before now."""
+    global _PRICE_CURVE_ENDED
+    _PRICE_CURVE_ENDED = bool(ended)
+
+
 def _a4_records(hass, entry) -> list[dict]:
     from homeassistant.helpers import entity_registry as er
 
@@ -1470,8 +1488,59 @@ def check_a4_recovered(
     )
 
 
+def _a4_issue_raised(hass, issue_id: str) -> bool:
+    from homeassistant.helpers import issue_registry as ir
+
+    return (PACKAGE_NAME, issue_id) in ir.async_get(hass).issues
+
+
+def check_a4_bridged(
+    checks: Checks,
+    last_update_success: object,
+    repair_raised: bool,
+    before: list[dict] | tuple[dict, ...],
+    after: list[dict] | tuple[dict, ...],
+) -> None:
+    """A failed fetch while published prices still cover now is bridged.
+
+    The update stays successful, the ``price_feed_stale`` repair is in the
+    registry and nothing that was published has gone unavailable. Encodes the
+    accepted contract of #3454; the fault below it is a4:failed's.
+    """
+    published = _a4_published(before)
+    after_by = {r["entity_id"]: r for r in after}
+    gone = [
+        r["entity_id"]
+        for r in published
+        if after_by.get(r["entity_id"], {}).get("state") in (None, "unavailable")
+    ]
+    ok = last_update_success is True and bool(repair_raised) and bool(published) and not gone
+    checks.check(
+        "a4:bridged",
+        ok,
+        (
+            f"bridged: last_update_success=True, price_feed_stale raised, "
+            f"{len(published)} entities available"
+            if ok
+            else (
+                f"last_update_success={last_update_success!r} "
+                f"price_feed_stale_raised={bool(repair_raised)} "
+                f"unavailable={sorted(gone)[:8] or ('none-published-before' if not published else 'none')}"
+            )
+        ),
+    )
+
+
 async def _async_check_a4(checks: Checks, hass, entry) -> None:
-    """Break the price source, assert unavailability, restore, assert recovery."""
+    """Two real-boundary phases against the Tibber counterparty, then recovery.
+
+    1. Break the source (HTTP 500) while the last published prices still cover
+       now: the failure is bridged (``a4:bridged``).
+    2. Exhaust the published prices at the counterparty -- it answers 200 with
+       a curve that ended before now, which the price pull accepts -- then
+       break the source: the update fails (``a4:failed`` and the rest).
+    Neither phase sets ``last_update_success`` or the coordinator's price cache.
+    """
     coordinator = getattr(entry, "runtime_data", None)
     if coordinator is None:
         for name in A4_INSIDE:
@@ -1481,13 +1550,33 @@ async def _async_check_a4(checks: Checks, hass, entry) -> None:
     break_price_source(True)
     try:
         try:
+            await coordinator.async_refresh()
+            await hass.async_block_till_done()
+            check_a4_bridged(
+                checks,
+                getattr(coordinator, "last_update_success", False),
+                _a4_issue_raised(hass, "price_feed_stale"),
+                before,
+                _a4_records(hass, entry),
+            )
+        except Exception as err:  # noqa: BLE001 - a raise is the A4 failure
+            checks.check("a4:bridged", False, f"{type(err).__name__}: {err}")
+        try:
+            # The ended curve is taken on a working source; its own refresh
+            # is not asserted, only what the 500 does once nothing covers now.
+            break_price_source(False)
+            end_price_curve(True)
+            await coordinator.async_refresh()
+            await hass.async_block_till_done()
+            before_failure = _a4_records(hass, entry)
+            break_price_source(True)
             await coordinator.async_refresh()
             await hass.async_block_till_done()
             broken = _a4_records(hass, entry)
             check_a4_failed(checks, getattr(coordinator, "last_update_success", True))
             check_a4_unavailable(checks, broken)
             check_a4_buttons(checks, broken)
-            check_a4_no_stale(checks, before, broken)
+            check_a4_no_stale(checks, before_failure, broken)
         except Exception as err:  # noqa: BLE001 - a raise is the A4 failure
             for name in A4_INSIDE:
                 if name == "a4:recovered" or name in checks.results:
@@ -1495,6 +1584,7 @@ async def _async_check_a4(checks: Checks, hass, entry) -> None:
                 checks.check(name, False, f"{type(err).__name__}: {err}")
     finally:
         break_price_source(False)
+        end_price_curve(False)
         # No return in here: it would discard whatever is still in flight
         # from the try, a cancellation included (PEP 765, D7-s3-51).
         try:
@@ -2515,7 +2605,8 @@ def _serve_prices(workdir: Path) -> None:
                 self.send_header("Content-Length", "0")
                 self.end_headers()
                 return
-            body = _tibber_body(datetime.now().astimezone())
+            now = datetime.now().astimezone()
+            body = _tibber_body(now - _ENDED_CURVE_AGE if _PRICE_CURVE_ENDED else now)
             self.send_response(200)
             self.send_header("Content-Type", "application/json")
             self.send_header("Content-Length", str(len(body)))
@@ -3394,7 +3485,8 @@ def check_blocking_positive_control(checks: Checks, probe_text: str) -> None:
 
 
 def _a4_update_failed_traceback(block: str) -> bool:
-    """A4 breaks Tibber with HTTP 500; UpdateFailed is the designed raise.
+    """A4's phase 2 breaks Tibber with HTTP 500 after an ended curve; UpdateFailed
+    is the designed raise.
 
     Newer Home Assistant logs that raise with a traceback naming this
     package. That is the coordinator doing its job, not an integration

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
