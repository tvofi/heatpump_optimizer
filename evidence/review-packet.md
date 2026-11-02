# Review packet #3174
head: 6ba3033f34810c8a4e311cb2eba8cbb3b78ab627
base: a9c149289922e92bae57cad87afc4abd3ef6c235

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125316148062 neutral
arch-score / arch-score id=125315801741 success
arm id=125315524871 skipped
budget-raise-gate / budget-raise-gate id=125315802100 success
cancel-superseded id=125315548674 success
codeql / Analyze (actions) id=125315801793 success
codeql / Analyze (javascript-typescript) id=125315801965 success
codeql / Analyze (python) id=125315801848 in_progress
governance / delivery-status id=125315801969 success
governance / delivery-status-publish id=125315804226 skipped
governance / env-matrix id=125315801945 in_progress
governance / instrument-self-tests id=125315801725 in_progress
governance / policy-docs id=125315801745 success
governance / record id=125315804396 skipped
governance / wave-script id=125315801694 success
hassfest / hassfest id=125315801888 success
kernel-points id=125315804035 skipped
prelude id=125315548840 success
refresh id=125315549165 success
tests / arch-instrument id=125316010525 success
tests / briefs id=125315801937 success
tests / browser id=125316010639 success
tests / closure-scope id=125315801817 success
tests / closures id=125316010436 in_progress
tests / coverage id=125316010527 in_progress
tests / fast (3.14) id=125316010441 in_progress
tests / mutation id=125315801841 success
tests / mutation-autofix id=125316136454 skipped
tests / mutation-pins id=125316136888 skipped
tests / nightly-ha id=125316013016 skipped
tests / nightly-status id=125315802039 success
tests / replay id=125316010511 in_progress
tests / typing id=125316010447 success
validate / validate-hacs id=125315801806 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh api repos/tvofi/heatpump_optimizer/actions/jobs/<job id>/logs
             gh api: every long flag accepted
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
index e98f66930..d0336e29c 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -465,12 +465,29 @@ COST_DETECTION = 2.0
 #: 217.8-290.5, each edge 18-22 % inside; a loaded M1 (177-394, load average
 #: 30-200) spans more than a 2x band holds and is left out. ``peak_kib`` and
 #: ``loop_cpu_ratio`` over all four environments, the M1 included: 2514-2783
-#: and 0.137-0.227, the loop's edges 9-10 % inside. One CI class only: the
-#: R10-REPLAY-LANE carry asks for both, so re-centre when the other class reads.
+#: and 0.137-0.227, the loop's edges 9-10 % inside.
+#: Re-centred (R10-REPLAY-COST-BUDGET) on the readings the CI ``replay`` job
+#: itself takes, from its own ``cost`` lines, and on nothing a reviewer's or
+#: author's box read. Two runner classes, by the job's own rulers: ``ref_ms`` 30
+#: / ``loop_ref_ms`` 129-132 (job 125240101580 of run 41434115932, #3174; job
+#: 125160076828 of run 41405222589, #3167) and ``ref_ms`` 46 / ``loop_ref_ms``
+#: 156 (job 125097530406 of run 41389413359, #3078). Owner fixture
+#: ``cpu_ratio`` 235.8, 240.7, 241.9: sqrt(2) x the geometric midpoint is 337.8,
+#: the lowest reading 70 % of it. Synthetic ``cpu_ratio`` 2.754, 2.81, 2.325:
+#: 3.614, the lowest 64 % of it, and every ``cpu doubled`` arm of those jobs
+#: (5.53, 5.70, 4.65) is over it. Synthetic ``loop_cpu_ratio`` 0.0907, 0.0903,
+#: 0.0901, flat across both classes: 0.1278, and the ``loop doubled`` arms
+#: (0.183, 0.186, 0.179) are over it. A box outside both classes reads the
+#: loop figure higher at the same code (4 cores, ``loop_ref_ms`` 87: 0.175; the
+#: reviewer's, 85-99: 0.152-0.191), because the ruler does not track the
+#: loop's work there; the lane never runs on one, and widening to it would put
+#: the budget over the doubled arm. ``peak_kib`` and the owner fixture's
+#: ``loop_cpu_ratio`` stay: the same jobs read 2709 KiB and 0.128-0.142 inside
+#: both bands. Only what ran is recorded.
 COST_BUDGETS: dict[str, dict[str, float]] = {
-    "synthetic-dhw-only.json": {"cpu_ratio": 2.173, "peak_kib": 2686.0,
-                                "loop_cpu_ratio": 0.143},
-    "owner-2026-10-30-away.json": {"cpu_ratio": 355.7, "peak_kib": 3740.0,
+    "synthetic-dhw-only.json": {"cpu_ratio": 3.614, "peak_kib": 2686.0,
+                                "loop_cpu_ratio": 0.1278},
+    "owner-2026-10-30-away.json": {"cpu_ratio": 337.8, "peak_kib": 3740.0,
                                    "loop_cpu_ratio": 0.249},
 }
 #: Fixtures the lane replays once, clean, without the three doubled-cost
@@ -597,6 +614,15 @@ def arms_skip_offenders(skipped: set[str], committed: set[str]) -> list[str]:
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
@@ -738,6 +764,11 @@ def controls() -> list[tuple[str, bool, str]]:
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
@@ -1212,6 +1243,14 @@ def recorder_checks() -> list[tuple[str, bool, str]]:
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
@@ -2477,6 +2516,8 @@ def main(argv: list[str] | None = None) -> int:
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
