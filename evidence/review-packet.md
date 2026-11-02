# Review packet #3174
head: a476a578ab2c3ee55d3dc3c22c7edb2a0bdaa737
base: 3905069f38a60559186fef916b0241e311cc81cd

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125240379610 neutral
arch-score / arch-score id=125239833863 success
arm id=125239617772 skipped
budget-raise-gate / budget-raise-gate id=125239833757 success
cancel-superseded id=125239621518 success
codeql / Analyze (actions) id=125239833867 success
codeql / Analyze (javascript-typescript) id=125239833758 success
codeql / Analyze (python) id=125239833748 in_progress
governance / delivery-status id=125239833525 success
governance / delivery-status-publish id=125239836407 skipped
governance / env-matrix id=125239833679 in_progress
governance / instrument-self-tests id=125239833699 in_progress
governance / policy-docs id=125239833660 success
governance / record id=125239835388 skipped
governance / wave-script id=125239833636 success
hassfest / hassfest id=125239833326 success
kernel-points id=125239835475 skipped
prelude id=125239621749 in_progress
refresh id=125239621296 success
tests / arch-instrument id=125240101784 success
tests / briefs id=125239833452 success
tests / browser id=125240102001 in_progress
tests / closure-scope id=125239833554 success
tests / closures id=125240101633 in_progress
tests / coverage id=125240101544 in_progress
tests / fast (3.14) id=125240101765 in_progress
tests / mutation id=125239833415 success
tests / mutation-autofix id=125240119877 skipped
tests / mutation-pins id=125240118706 skipped
tests / nightly-ha id=125240104325 skipped
tests / nightly-status id=125239833475 success
tests / replay id=125240101580 in_progress
tests / typing id=125240101684 success
validate / validate-hacs id=125239833593 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item eee8c76c: R10-REPLAY-COST-BUDGET
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/replay.py --one tests/replay/owner-2026-10-30-away.json
             `tests/replay.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3174.md b/dev/programme/delivery/3174.md
new file mode 100644
index 000000000..21fb30bbf
--- /dev/null
+++ b/dev/programme/delivery/3174.md
@@ -0,0 +1 @@
+- [#3174](https://github.com/tvofi/heatpump_optimizer/pull/3174) — **open**, R10-REPLAY-COST-BUDGET: replay cost budget (R10-REPLAY-COST-BUDGET)
diff --git a/tests/replay.py b/tests/replay.py
index e98f66930..231032c06 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -465,12 +465,20 @@ COST_DETECTION = 2.0
 #: 217.8-290.5, each edge 18-22 % inside; a loaded M1 (177-394, load average
 #: 30-200) spans more than a 2x band holds and is left out. ``peak_kib`` and
 #: ``loop_cpu_ratio`` over all four environments, the M1 included: 2514-2783
-#: and 0.137-0.227, the loop's edges 9-10 % inside. One CI class only: the
-#: R10-REPLAY-LANE carry asks for both, so re-centre when the other class reads.
+#: and 0.137-0.227, the loop's edges 9-10 % inside. Re-centred on the
+#: second CI class (R10-REPLAY-COST-BUDGET): a fresh container read ``cpu_ratio``
+#: 385.3 here, over 355.7, so the extremes are 217.8-385.3 (the M1 excluded as
+#: before); sqrt(2) x their geometric midpoint is 409.7, the lowest reading 53 %
+#: of it. The same rule for ``synthetic-dhw-only.json``'s ``cpu_ratio``: 2.0 and
+#: 2.14 (a 4-core box, ``ref_ms`` about 32) and 2.615 and 2.81 (the replay job of
+#: #3167, ``ref_ms`` 30, ``loop_ref_ms`` 132) give 3.353; the lowest reading
+#: doubled, 4.0, stays over it. ``peak_kib`` and the owner fixture's
+#: ``loop_cpu_ratio`` stay: its new readings (2687-2709 KiB; 0.134-0.196) sit
+#: inside both bands. Only what ran is recorded.
 COST_BUDGETS: dict[str, dict[str, float]] = {
-    "synthetic-dhw-only.json": {"cpu_ratio": 2.173, "peak_kib": 2686.0,
+    "synthetic-dhw-only.json": {"cpu_ratio": 3.353, "peak_kib": 2686.0,
                                 "loop_cpu_ratio": 0.143},
-    "owner-2026-10-30-away.json": {"cpu_ratio": 355.7, "peak_kib": 3740.0,
+    "owner-2026-10-30-away.json": {"cpu_ratio": 409.7, "peak_kib": 3740.0,
                                    "loop_cpu_ratio": 0.249},
 }
 #: Fixtures the lane replays once, clean, without the three doubled-cost
@@ -597,6 +605,15 @@ def arms_skip_offenders(skipped: set[str], committed: set[str]) -> list[str]:
     return out
 
 
+def away_covered_offenders(covered: frozenset[str] | set[str],
+                           committed: set[str]) -> list[str]:
+    """``AWAY_COVERED`` naming a fixture that is not committed: a misspelt
+    name declares coverage no fixture carries, and ``away_coverage_offenders``
+    would never see it."""
+    return [f"{name}: declares away coverage but is not a committed fixture"
+            for name in sorted(covered - committed)]
+
+
 def short_doubling(injected_ratio: float) -> list[str]:
     """A perturbation arm that burnt less than the clean span its metric
     times is no doubling (#2205: the cpu arm spun the update alone, ~0.93)."""
@@ -738,6 +755,11 @@ def controls() -> list[tuple[str, bool, str]]:
     pair("cycle_cost:arms_skipped_committed_only",
          arms_skip_offenders({"gone.json"}, {"a.json"}),
          arms_skip_offenders({"a.json"}, {"a.json", "b.json"}))
+    pair("away:covered_names_are_committed",
+         away_covered_offenders({"owner-2026-10-30-awya.json"},
+                                {"owner-2026-10-30-away.json"}),
+         away_covered_offenders({"owner-2026-10-30-away.json"},
+                                {"owner-2026-10-30-away.json"}))
     pair("cycle_cost:short_doubling", short_doubling(0.93), short_doubling(1.0001))
     pair("cycle_cost:unmetered_doubling", short_doubling(float("nan")), short_doubling(1.0))
     held = {"t": "t", "commanded_return": "r", "active": True, "override": True,
@@ -1212,6 +1234,14 @@ def recorder_checks() -> list[tuple[str, bool, str]]:
                     and "core-mariadb" not in said_url and marked.name not in said_url
                     and len(_CANARY_KEY) > 3 and len(_CANARY_USER) > 3,
                     "the URL branch's stderr searched for the user, password and host"))
+        # The unsupported-scheme refusal names neither the URL nor any part of
+        # it; a URL without credentials reads the same text (the null).
+        _, bad = _export_mariadb(None, tmp, db_url=f"ftp://{_CANARY_USER}:{_CANARY_KEY}@core-mariadb/x")
+        _, plain = _export_mariadb(None, tmp, db_url="ftp://core-mariadb/x")
+        res.append(("recorder:unsupported_scheme_refusal_prints_none_of_the_url",
+                    "neither SQLite nor" in bad
+                    and not any(c in bad for c in (_CANARY_KEY, _CANARY_USER, "core-mariadb", "ftp:"))
+                    and bad == plain, bad[-200:]))
         flag, _ = _export_mariadb(fake, tmp, db_url=_DB_URL.replace("homeassistant", "hadb"))
         res.append(("recorder:db_url_flag_read", flag is not None
                     and fake.kwargs.get("database") == "hadb", str(fake.kwargs.get("database"))))
@@ -2477,6 +2507,8 @@ def main(argv: list[str] | None = None) -> int:
     # committed fixtures and leaves at least one to them, so the full lane
     # (nightly, and every pull request that reaches it) always runs them.
     committed = {f.name for f in FIXTURES.glob("*.json")}
+    wrong = away_covered_offenders(AWAY_COVERED, committed)
+    R.check("AWAY_COVERED names committed fixtures", not wrong, " | ".join(wrong))
     wrong = arms_skip_offenders(set(COST_ARMS_SKIPPED), committed)
     R.check("the doubled-cost arms are skipped on committed fixtures only, never all",
             not wrong, " | ".join(wrong) + f"; this run perturbed {perturbed}")

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
