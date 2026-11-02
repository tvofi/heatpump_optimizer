# Review packet #3170
head: b307f3599921ff345f677f34583958fa930a935a
base: dfb4ce2b52fafb340e0320bc2efb870099a53884

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125168717876 neutral
arch-score / arch-score id=125168398485 success
arm id=125168297518 skipped
budget-raise-gate / budget-raise-gate id=125168398368 success
cancel-superseded id=125168239359 success
codeql / Analyze (actions) id=125168398419 success
codeql / Analyze (javascript-typescript) id=125168398399 success
codeql / Analyze (python) id=125168398439 in_progress
governance / delivery-status id=125168398661 success
governance / delivery-status-publish id=125168400169 skipped
governance / env-matrix id=125168398601 in_progress
governance / instrument-self-tests id=125168398560 in_progress
governance / policy-docs id=125168398641 success
governance / record id=125168400730 skipped
governance / wave-script id=125168398515 success
hassfest / hassfest id=125168398328 success
kernel-points id=125168400077 skipped
prelude id=125168239753 success
refresh id=125168239864 success
tests / arch-instrument id=125168587477 success
tests / briefs id=125168398345 success
tests / browser id=125168587656 in_progress
tests / closure-scope id=125168398364 success
tests / closures id=125168587556 in_progress
tests / coverage id=125168587596 in_progress
tests / fast (3.14) id=125168587614 in_progress
tests / mutation id=125168398455 success
tests / mutation-autofix id=125168713824 skipped
tests / mutation-pins id=125168713172 skipped
tests / nightly-ha id=125168590503 skipped
tests / nightly-status id=125168398380 success
tests / replay id=125168587530 in_progress
tests / typing id=125168587496 success
validate / validate-hacs id=125168398313 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 75ead625: R10-SUITE-HOST-DETERMINISM
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/golden.py
             `tests/golden.py` is in the tree at this head

FIGURES: 5 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 2e0a8bc85..f2994000f 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -542,8 +542,8 @@ def _comparable_ts(raw: Any, reference: datetime) -> datetime | None:
     """Parse an entry timestamp so it can be ordered against the step grid.
 
     A naive timestamp against an aware grid is taken as UTC, matching
-    ``_get_current_price``; an aware one against a naive grid keeps its own
-    wall clock.
+    ``_get_current_price``; an aware one against a naive grid is read as the
+    configured zone's wall clock (UTC unless the zone is set).
 
     Module level, not a coordinator method: it reads nothing off ``self``
     and never did, and the class it sat in is the one the decomposition
diff --git a/dev/programme/delivery/3170.md b/dev/programme/delivery/3170.md
new file mode 100644
index 000000000..216554c7f
--- /dev/null
+++ b/dev/programme/delivery/3170.md
@@ -0,0 +1 @@
+- [#3170](https://github.com/tvofi/heatpump_optimizer/pull/3170) — **open**, R10-SUITE-HOST-DETERMINISM: suite host determinism (R10-SUITE-HOST-DETERMINISM)
diff --git a/tests/entities.py b/tests/entities.py
index 1361f496e..ee9b18d1e 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -36815,13 +36815,17 @@ R.check(
 )
 
 
-def _coverage_revalidation(floor_fails: bool) -> tuple[dict, dict, str, dict]:
+def _coverage_revalidation(
+    floor_fails: bool, late: bool = False, wait_s: int = 300
+) -> tuple[dict, dict, str, dict, list, str]:
     """coverage_tree.sh's reuse plan and floor re-validation under a stub
     interpreter: the first script is reused, the rest measured, and the stub
     grader reports a floor FAIL when asked to. Returns (non-reused metric
     rows per script, executions per script, the stage's output, and per
     ledger -- out/scripts.tsv and out/per/provenance.tsv -- the rows each
-    script holds and how many of them say `reused`)."""
+    script holds and how many of them say `reused`), then the scripts the
+    stage recorded as `nodata` and the one script that, when ``late``, left a
+    descendant writing its coverage data two seconds after it returned."""
     with _tempfile.TemporaryDirectory() as td:
         d = Path(td)
         stub = d / "py"
@@ -36830,7 +36834,10 @@ def _coverage_revalidation(floor_fails: bool) -> tuple[dict, dict, str, dict]:
             'case "$1" in\n'
             "  -c) exit 0 ;;\n"
             "  -m) for a; do [ \"$prev\" = -o ] && echo '{}' > \"$a\"; "
-            'prev="$a"; done; exit 0 ;;\n'
+            'case "$a" in --rcfile=*) rcf="${a#--rcfile=}";; esac; '
+            'prev="$a"; done\n'
+            '    [ "$3" = combine ] && : > "$(sed -n \'s/^data_file = //p\' "$rcf")"\n'
+            "    exit 0 ;;\n"
             "  tests/closure.py)\n"
             '    [ "$2" = coverage-split ] || exit 0\n'
             "    n=0; while read -r s; do [ -n \"$s\" ] || continue\n"
@@ -36839,15 +36846,23 @@ def _coverage_revalidation(floor_fails: bool) -> tuple[dict, dict, str, dict]:
             "  tests/coverage_ratchet.py)\n"
             '    [ -n "$CTR_FLOOR_FAIL" ] && echo "  FAIL every module >= 95.0 %"'
             "\n    exit 0 ;;\n"
-            '  *) echo "$1" >> "$CTR_RAN"; exit 0 ;;\n'
+            '  *) echo "$1" >> "$CTR_RAN"\n'
+            '    if [ -n "$CTR_LATE" ] && mkdir "$CTR_LATE/once" 2> /dev/null; then\n'
+            '      echo "$1" > "$CTR_LATE/who"\n'
+            '      df=$(sed -n \'s/^data_file = //p\' "$COVERAGE_PROCESS_START")\n'
+            '      ( sleep 2; echo late > "$df.late" ) < /dev/null > /dev/null 2>&1 &\n'
+            '    fi\n'
+            '    exit 0 ;;\n'
             "esac\n")
         stub.chmod(0o755)
         (d / "reuse").mkdir()
         (d / "work").mkdir()
+        (d / "late").mkdir()
         env = {**_os.environ, "PYTHON": str(stub), "W5P_WORK": str(d / "work"),
                "W5P_SCOPE": str(d / "scope.json"), "W5P_REUSE": str(d / "reuse"),
                "W5P_LANES": "1", "HPO_CI_METRICS": str(d / "m.tsv"),
-               "CTR_RAN": str(d / "ran"),
+               "CTR_RAN": str(d / "ran"), "W5P_DESCENDANT_WAIT": str(wait_s),
+               "CTR_LATE": str(d / "late") if late else "",
                "CTR_FLOOR_FAIL": "1" if floor_fails else ""}
         res = _subprocess.run(["bash", "tools/coverage/coverage_tree.sh", "fast"],
                               env=env, capture_output=True, text=True,
@@ -36863,6 +36878,9 @@ def _coverage_revalidation(floor_fails: bool) -> tuple[dict, dict, str, dict]:
                      if (d / "ran").is_file() else []):
             name = Path(line).stem
             ran[name] = ran.get(name, 0) + 1
+        nodata = sorted(p.name for p in (d / "work/out/per").glob("*.nodata"))
+        who = (Path((d / "late/who").read_text().strip()).stem
+               if (d / "late/who").is_file() else "")
         ledgers: dict = {}
         for rel in ("out/scripts.tsv", "out/per/provenance.tsv"):
             f = d / "work" / rel
@@ -36874,11 +36892,12 @@ def _coverage_revalidation(floor_fails: bool) -> tuple[dict, dict, str, dict]:
                 per[r[0]] = per.get(r[0], 0) + 1
             ledgers[Path(rel).name] = {
                 "rows": per, "reused": sum(1 for r in rows if r[1:2] == ["reused"])}
-    return runs, ran, res.stdout[-400:] + res.stderr[-400:], ledgers
+    return (runs, ran, res.stdout[-400:] + res.stderr[-400:], ledgers, nodata,
+            who)
 
 
-_CRV_RUNS, _CRV_RAN, _CRV_OUT, _CRV_LEDGERS = _coverage_revalidation(floor_fails=True)
-_CRV_NULL_RUNS, _CRV_NULL_RAN, _, _CRV_NULL_LEDGERS = _coverage_revalidation(floor_fails=False)
+_CRV_RUNS, _CRV_RAN, _CRV_OUT, _CRV_LEDGERS, _, _ = _coverage_revalidation(floor_fails=True)
+_CRV_NULL_RUNS, _CRV_NULL_RAN, _, _CRV_NULL_LEDGERS, _, _ = _coverage_revalidation(floor_fails=False)
 R.check(
     "the coverage floor re-validation re-measures only the scripts it reused",
     len(_CRV_RUNS) >= 2 and set(_CRV_RUNS.values()) == {1}
@@ -36911,6 +36930,24 @@ R.check(
     "reused, the null control)",
 )
 
+# A measured script whose descendant writes its coverage data after the script
+# returned (#2632: features.py left 740 live workers). The stage waits for the
+# descendant, so the script is recorded as measured, not `nodata`. Null: with
+# no late writer no script reads `nodata` for that reason; planted defect: a
+# wait bound shorter than the late write must refuse, naming the script, never
+# record the missing data as `nodata` in silence.
+_CRV_LATE = _coverage_revalidation(floor_fails=False, late=True)
+_CRV_LATE_REFUSED = _coverage_revalidation(floor_fails=False, late=True, wait_s=0)
+R.check(
+    "a measured script's late-writing descendant is waited for, not recorded as nodata",
+    bool(_CRV_LATE[5]) and f"{_CRV_LATE[5]}.nodata" not in _CRV_LATE[4]
+    and "left descendants still running" not in _CRV_LATE[2]
+    and "left descendants still running" in _CRV_LATE_REFUSED[2]
+    and f"{_CRV_LATE_REFUSED[5]}.nodata" not in _CRV_LATE_REFUSED[4],
+    f"waiting: late script {_CRV_LATE[5]!r}, nodata {_CRV_LATE[4]}; bound 0: "
+    f"{_CRV_LATE_REFUSED[2]!r}",
+)
+
 # The recorded budget is the every-script-measured-once count: the closures
 # lane's full plan plus the coverage `fast` stage's scripts (since W1,
 # R10-CI-LAYOUT PR 1, the closures lane consumes no composed recording, so it
diff --git a/tests/features.py b/tests/features.py
index c9bf4d677..d997ced76 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -37022,7 +37022,11 @@ async def _pt_degree_at_seam(room):
 # stands, so the two starts part it. The clock is fixed at a night and an
 # afternoon instant: what the check reads is the same at every hour it runs.
 _pt_seams = {}
-for _pt_at in (datetime(2026, 1, 15, 3, 7, tzinfo=UTC), datetime(2026, 1, 15, 15, 7, tzinfo=UTC)):
+# The instants are 03:07 and 15:07 in the configured zone, so the hour the
+# keys name is the local hour the plan's price and comfort windows read, under
+# any ``HASTUB_TZ`` (UTC unless set).
+for _pt_at in (datetime(2026, 1, 15, 3, 7, tzinfo=_fi_dt.DEFAULT_TIME_ZONE),
+               datetime(2026, 1, 15, 15, 7, tzinfo=_fi_dt.DEFAULT_TIME_ZONE)):
     _fi_dt.freeze(_pt_at)
     try:
         for _pt_room in (19.0, 23.0):
@@ -47292,11 +47296,16 @@ def _t3_peak(house, measured, commanded, *, enabled=True):
     dt_util.freeze(_T3_PEAK_NOW)
     try:
         got = _t3_call(c._track_realised_peak)
+        # Read the window at the clock the production fold stamped it with
+        # (``dt_util.now()``: the same instant in the configured zone). The
+        # window key carries the slot's UTC offset, so the UTC literal reads a
+        # different key under a non-UTC ``HASTUB_TZ`` and finds no window.
+        read_at = dt_util.now()
     finally:
         dt_util.freeze(None)
     if isinstance(got, Exception):
         return got
-    return c._peak_tracker.window_snapshot(_T3_PEAK_NOW, c._capacity_tariff())[1]
+    return c._peak_tracker.window_snapshot(read_at, c._capacity_tariff())[1]
 
 
 R.check(
@@ -50961,11 +50970,12 @@ R.check(
 _T6_TS_AWARE = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
 _T6_TS_NAIVE = datetime(2026, 2, 1, 12, 0, 0)
 R.check(
-    "a naive timestamp against an aware grid is taken as UTC, and the reverse keeps its wall clock",
+    "a naive timestamp against an aware grid is taken as UTC, and the reverse reads the configured zone's wall clock",
     _t6_comparable_ts("2026-02-01T10:00:00", _T6_TS_AWARE)
     == datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc)
     and _t6_comparable_ts("2026-02-01T10:00:00+00:00", _T6_TS_NAIVE)
-    == datetime(2026, 2, 1, 10, 0, 0),
+    == datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc)
+    .astimezone(dt_util.DEFAULT_TIME_ZONE).replace(tzinfo=None),
     f"naive against aware -> "
     f"{_t6_comparable_ts('2026-02-01T10:00:00', _T6_TS_AWARE)!r}; aware "
     f"against naive -> "
@@ -61891,7 +61901,11 @@ from heatpump_optimizer import coordinator as _f11_cm  # noqa: E402
 
 
 async def _f11_midsolve(away: bool):
-    t0 = datetime(2026, 10, 2, 8, 0)
+    # Aware, so the price and forecast stamps and the frozen clock name one
+    # instant in any ``HASTUB_TZ``: a naive stamp is read as UTC against an
+    # aware clock, which under a non-UTC zone leaves no current price slot and
+    # the solve never reaches the write this check drives.
+    t0 = datetime(2026, 10, 2, 8, 0, tzinfo=timezone.utc)
     hass = FakeHass({"sensor.indoor": FakeState("21.4"),
                      "sensor.outdoor": FakeState("-3.0")})
     entry = _f11_Entry(data={"indoor_temp_entity": "sensor.indoor",
@@ -76455,7 +76469,9 @@ R.check(
     and _cp_qw.quiet_reason({"quiet_off_windows": "09:00-09:30"}, _CP_T0) is None
     and _cp_qw.quiet_reason({}, _CP_T0) is None,
 )
-_cp_dt.freeze(_CP_T0)
+# Quiet windows are wall-clock hours in the configured zone, so the instant is
+# the same 23:00 local under any ``HASTUB_TZ`` (``_CP_T0`` is 23:00 UTC).
+_cp_dt.freeze(_CP_T0.replace(tzinfo=_cp_dt.DEFAULT_TIME_ZONE))
 try:
     _CP_ROOM = {"indoor_temp_entity": "sensor.room", "outdoor_temp_entity": "sensor.out"}
     _cp_quiet = _cp_coord(**_CP_PROBE_CFG, **_CP_ROOM, quiet_off_windows="22:00-23:30")
diff --git a/tests/gate_lock.py b/tests/gate_lock.py
index d93b8ac0b..ce57de697 100644
--- a/tests/gate_lock.py
+++ b/tests/gate_lock.py
@@ -1739,7 +1739,7 @@ def _priority_cases(g) -> list[tuple[str, bool, str]]:
         g.WAIT_POLL_SECS = 0.05
         pool = g.pool_dir(d)
         g.take_slot("holder", lock_dir=d, slots=1, lease_seconds=60, wait=False)
-        inside, overlaps, guard = [0], [0], threading.Lock()
+        inside, overlaps, entered, guard = [0], [0], [0], threading.Lock()
 
         def one(who: str) -> None:
             g.take_slot(who, lock_dir=d, slots=1, lease_seconds=60)
@@ -1747,7 +1747,17 @@ def _priority_cases(g) -> list[tuple[str, bool, str]]:
                 if inside[0]:
                     overlaps[0] += 1
                 inside[0] += 1
-            time.sleep(0.15)
+                entered[0] += 1
+                first_in = entered[0] == 1
+            if first_in:
+                # Hold until the other waiter is provably polling the held slot:
+                # its ticket exists and a poll has rewritten it since. A fixed
+                # sleep is a window a loaded runner can outlast (the loser then
+                # enters after the winner left and the overlap goes unseen).
+                other = "b" if who == "a" else "a"
+                seen = ticket_text(pool, other)
+                if seen:
+                    rewritten(pool, other, seen)
             with guard:
                 inside[0] -= 1
             got.append(who)
diff --git a/tools/coverage/coverage_tree.sh b/tools/coverage/coverage_tree.sh
index b40e39466..f76928737 100755
--- a/tools/coverage/coverage_tree.sh
+++ b/tools/coverage/coverage_tree.sh
@@ -155,6 +155,31 @@ metric_line() {
   printf 'coverage\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" \
     "${GITHUB_EVENT_NAME:-local}" "${GITHUB_RUN_ID:-local}" >> "$_hpo_ci_metrics"
 }
+# A measured script's descendants (a multiprocessing pool, a daemonised worker)
+# write their .coverage.* files when THEY exit, which can be after the script
+# returns. Reading the data directory at the script's return then records a
+# script whose workers were still running as `nodata`, with no error, and the
+# ratchet reads a package-wide drop it cannot attribute (#2632's features.py:
+# 740 live workers at exit, 85.9 % against 98.7 %). Every descendant inherits
+# COVERAGE_PROCESS_START, so a process whose environment still carries this
+# script's own rcfile path is one the script left behind: wait for it, and name
+# the script when it does not exit. Linux only (/proc); elsewhere the wait is
+# skipped, as the closures recording is (gate-scoping.md).
+wait_descendants() {
+  local s="$1" rc="$WORK/coveragerc.$1" end
+  [ -d /proc/self ] || return 0
+  end=$((SECONDS + ${W5P_DESCENDANT_WAIT:-300}))
+  # Test the output, not the status: grep exits 2 on an unreadable /proc entry
+  # even when it matched.
+  while [ -n "$(grep -lsaxFz -- "COVERAGE_PROCESS_START=$rc" /proc/[0-9]*/environ 2> /dev/null)" ]; do
+    if [ "$SECONDS" -ge "$end" ]; then
+      echo "tests/$s.py left descendants still running ${W5P_DESCENDANT_WAIT:-300}s after it returned; their coverage data is not in yet" >&2
+      return 1
+    fi
+    sleep 1
+  done
+}
+
 measure() {
   while IFS=$'\t' read -r verb s; do
     [ -n "$s" ] || continue
@@ -183,6 +208,7 @@ measure() {
     printf '%s\tmeasured\n' "$s" >> "$OUT/per/provenance.tsv"
     echo "ran tests/$s.py exit=$rc wall=$((b-a))s"
     metric_line "$s" "$class" "$rc" "$((b-a))"
+    wait_descendants "$s" || return 1
     if ls "$WORK/data/$s"/.coverage.* > /dev/null 2>&1; then
       # env -u, never an empty COVERAGE_PROCESS_START= prefix: with
       # $WORK/site's sitecustomize on PYTHONPATH, coverage 7.13.1's

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
