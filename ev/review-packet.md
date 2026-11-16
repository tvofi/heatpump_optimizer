# Review packet #3651
head: e5bf20c3b9b8af81663cd787de2460efb18656dc
base: 47f0f18a7ecebaa0f6ff0e4948b4f8d82e616e1a

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133032517920 success
arch-score / arch-score id=133032202091 success
arm id=133031774850 skipped
budget-raise-gate / budget-raise-gate id=133032202184 success
cancel-superseded id=133031961197 success
codeql id=133032203542 skipped
codeql / Analyze (actions) id=133032027426 success
codeql / Analyze (javascript-typescript) id=133032027386 success
codeql / Analyze (python) id=133032027474 success
gate id=133032768363 failure
governance id=133032203627 skipped
governance / env-matrix id=133032027282 success
governance / instrument-self-tests id=133032027299 in_progress
governance / policy-docs id=133032027313 success
governance / record id=133032029039 skipped
governance / wave-script id=133032027292 success
hassfest id=133032203327 skipped
hassfest / hassfest id=133032027295 success
kernel-points id=133032203591 skipped
pr-contract id=133032770092 skipped
prelude id=133031961906 success
refresh id=133031961018 success
sweep-self id=133033051879 skipped
tests id=133032203331 skipped
tests / arch-instrument id=133032445921 in_progress
tests / briefs id=133032027382 success
tests / browser id=133032445845 success
tests / closure-scope id=133032027315 success
tests / closures id=133032445853 in_progress
tests / coverage id=133032445913 in_progress
tests / fast (3.14) id=133032445871 in_progress
tests / mutation id=133032027329 success
tests / mutation-autofix id=133032442623 skipped
tests / mutation-pins id=133032442778 skipped
tests / nightly-ha id=133032447349 skipped
tests / nightly-status id=133032027375 success
tests / replay id=133032448331 skipped
tests / typing id=133032445843 success
validate id=133032203310 skipped
validate / validate-hacs id=133032027333 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 133032027299: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at e5bf20c3b9b8af81663cd787de2460efb18656dc in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item 4427fe25: R11-INTAKE-R10-RESIDUE
NOTE body item 00d4b808: R11-PRE-STANDING-SCRIPTS
NOTE body item 429c6e75: dismissed:an environment limit of the cloud seat, and the beat runs on the orchestrator's host, where gh is live
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         python3 -I tools/audit/seat/owed_watch.py --self-test
             `tools/audit/seat/owed_watch.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/beat_jobs.py --self-test
             `tools/audit/seat/beat_jobs.py` is in the tree at this head
  ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         gh pr list
             gh pr list: every long flag accepted
  unverified git ls-remote origin 'refs/heads/*R11-OUTSIDE-ROOMS-P2*'
             `git ls-remote` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "FIRE_GRACE_MIN\|SEAT_WINDOW_MIN\|FIRED_STAMP\|_seat_on\|_fired(\|fire_names\|def payloads\|\.payloads(" -- tools/audit/seat/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "STAMP.match" -- tools/audit/seat/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/archscore/score.py --diff 98847b99d7bb3238686efd6869f805c89c6d1ff1
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 -I tools/pr/ci_predict.py --base origin/main --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py record
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py static
             `tools/ci/selftest_scope.py` is in the tree at this head

FIGURES: 11 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 278971983f..d001fbf49d 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -1444,7 +1444,7 @@ jobs:
           python3 -I tools/audit/seat/sweep_driver.py --self-test | tee "$RUNNER_TEMP/sweep-driver-self-test.txt"
           grep -Eq '^sweep_driver self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/sweep-driver-self-test.txt"
 
-      - name: Show the beat's Gantt and verdict-audit instruments (sweep_gantt.py, verdict_audit.py) refusing their own fixtures
+      - name: Show the beat's Gantt, verdict-audit and owed-watch instruments (sweep_gantt.py, verdict_audit.py, owed_watch.py) refusing their own fixtures
         id: gantt-and-verdict-audit
         if: ${{ !cancelled() && steps.scope.outputs.gantt-and-verdict-audit == 'true' }}
         run: |
@@ -1453,6 +1453,8 @@ jobs:
           grep -Eq '^sweep_gantt self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/sweep-gantt-self-test.txt"
           python3 -I tools/audit/seat/verdict_audit.py --self-test | tee "$RUNNER_TEMP/verdict-audit-self-test.txt"
           grep -Eq '^verdict_audit self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/verdict-audit-self-test.txt"
+          python3 -I tools/audit/seat/owed_watch.py --self-test | tee "$RUNNER_TEMP/owed-watch-self-test.txt"
+          grep -Eq '^owed_watch self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/owed-watch-self-test.txt"
 
       - name: Show the survivor-list check (tools/audit/seat/survivor_list.py) refusing its own fixtures
         id: survivor-list
diff --git a/dev/programme/delivery/3651.md b/dev/programme/delivery/3651.md
new file mode 100644
index 0000000000..e0a9831556
--- /dev/null
+++ b/dev/programme/delivery/3651.md
@@ -0,0 +1 @@
+- [#3651](https://github.com/tvofi/heatpump_optimizer/pull/3651) — **open**, R11-PRE-STANDING-SCRIPTS: r11 pre standing scripts (R11-PRE-STANDING-SCRIPTS)
diff --git a/tests/closure.py b/tests/closure.py
index b7d319b2e7..d34d2b82b9 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -597,6 +597,10 @@ INERT_EXCEPT = (
     # their self-tests, so the tools/audit/seat/ INERT prefix must not hide them.
     "tools/audit/seat/ci_priority.py",
     "tools/audit/seat/ci_pause.py",
+    # R11-PRE-STANDING-SCRIPTS: the tick loads the owed watch (its fired-ledger,
+    # seat-on and FIRE-OWED reads moved there), so that self-test reads it. Same
+    # route as ci_priority.py: the prefix stays INERT, the file joins the closure.
+    "tools/audit/seat/owed_watch.py",
     # ... and that self-test reads these three (pr_cap.py, budget_raise_gate.py,
     # app_approve.sh), which ci_predict's self-test-reads arm names UNDER-SCOPED.
     "tools/audit/seat/pr_cap.py",
diff --git a/tests/closures.json b/tests/closures.json
index c8263ee70a..c27b4220f0 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1989,6 +1989,7 @@
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
    "tools/audit/seat/orchestrator_tick.py",
+   "tools/audit/seat/owed_watch.py",
    "tools/audit/seat/plan_page.py",
    "tools/audit/seat/plan_table.py",
    "tools/audit/seat/postmerge.py",
@@ -4145,6 +4146,7 @@
    "tools/audit/seat/outside_intake.py",
    "tools/audit/seat/outside_intake_selftest.py",
    "tools/audit/seat/owed_unactioned.py",
+   "tools/audit/seat/owed_watch.py",
    "tools/audit/seat/plan_audit.py",
    "tools/audit/seat/plan_page.py",
    "tools/audit/seat/plan_public.py",
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 62868e3c79..b6bcc5272e 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -128,6 +128,11 @@ ROWS (the job table's `interval_s` in brackets):
                      A failed slot-take or worktree add is `darwin-selftest: UNREADABLE
                      <step> rc=N: ...`, runs nothing and leaves the cycle where it was, so
                      the next pass retries it.
+  cp-owed [300]      owed_watch.py `cp-owed --repo R --fired <fire_ledger> --checkout <repo>`: one
+                     `CP-OWED <arm> <subject>` line per critical-path or outside step past its
+                     grace (owner directive tvofi 2026-11-09, "never let the critical path or
+                     outside PRs slip, ever"); `cp-owed: UNREADABLE` on a non-zero rc, never
+                     its partial lines.
   bottleneck [1800]  bottleneck_check.py `--checkout <repo> --train-log
                      <train_log> --wip-cap <plan_slots> --memory
                      state/bottleneck.json`: its `BOTTLENECK:` and
@@ -161,7 +166,7 @@ import time
 from pathlib import Path
 
 ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "gantt", "verdict-audit", "pulse",
-        "cancel-sweep", "disk", "opener", "loop-cwd", "head-watch", "audit-dispatch", "outside-intake", "bottleneck",
+        "cancel-sweep", "disk", "opener", "loop-cwd", "head-watch", "audit-dispatch", "outside-intake", "cp-owed", "bottleneck",
         "scorecard", "darwin-selftest")
 HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
 #: roster-drain starts no op past this many seconds into a pass; the rest wait for the next pass. At
@@ -677,6 +682,19 @@ def outside_intake(ctx: Ctx) -> None:
     write_job(ctx, "outside-intake", [why or f"outside-intake: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
 
 
+def cp_owed(ctx: Ctx) -> None:
+    """owed_watch.py cp-owed: one CP-OWED line per critical-path or outside step past its grace."""
+    got = ctx.need("cp-owed", "repo", "fire_ledger")
+    if got is None:
+        return
+    rc, out, err = ctx.py("tools/audit/seat/owed_watch.py", "cp-owed", "--repo", got[0], "--fired", got[1],
+                          "--checkout", str(ctx.repo))
+    if rc != 0:
+        why = next((ln for ln in out.splitlines() if ln.startswith("cp-owed: UNREADABLE")), None)
+        return write_job(ctx, "cp-owed", [why or f"cp-owed: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
+    write_job(ctx, "cp-owed", [ln for ln in out.splitlines() if ln.startswith("CP-OWED ")])
+
+
 def bottleneck(ctx: Ctx) -> None:
     """bottleneck_check.py: one line per flow metric past its threshold, held once per trip by its memory."""
     got = ctx.need("bottleneck", "train_log", "plan_slots")
@@ -783,7 +801,7 @@ def darwin_selftest(ctx: Ctx) -> None:
 RUN = {"tick-digest": tick_digest, "owed-check": owed_check, "roster-drain": roster_drain,
        "plan-beat": plan_beat, "gantt": gantt, "verdict-audit": verdict_audit, "pulse": pulse, "cancel-sweep": cancel_sweep, "disk": disk,
        "opener": opener, "loop-cwd": loop_cwd, "head-watch": head_watch, "audit-dispatch": audit_dispatch,
-       "outside-intake": outside_intake, "bottleneck": bottleneck, "scorecard": scorecard,
+       "outside-intake": outside_intake, "cp-owed": cp_owed, "bottleneck": bottleneck, "scorecard": scorecard,
        "darwin-selftest": darwin_selftest}
 
 
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index c18507df91..ddadc25090 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -736,6 +736,32 @@ def cases(bj) -> dict[str, bool]:
     bj.verdict_audit(c)
     res["verdict-audit null: nothing unheld writes no byte"] = not files(c)
 
+    # cp-owed
+    cpl = "CP-OWED DESIGN-REVIEW-OWED R11-X 64m past its 10m grace [OUTSIDE] -- design/R11-X at abc has no design review"
+    c, f = fresh(overlay={"repo": "o/r", "fire_ledger": "/fired"},
+                 answers={"owed_watch.py": (0, "note\n" + cpl + "\n", "")})
+    pre = "CP-OWED" not in digest(c)
+    bj.cp_owed(c)
+    v = (f.calls or [[]])[0]
+    res["cp-owed: a CP-OWED line reaches the digest, and the repo, ledger and checkout are handed on"] = (
+        pre and digest(c) == bj.norm(cpl) + "\n" and "cp-owed" in v and arg(v, "--repo") == "o/r"
+        and arg(v, "--fired") == "/fired" and arg(v, "--checkout") == str(root))
+    c, f = fresh(overlay={"repo": "o/r", "fire_ledger": "/fired"},
+                 answers={"owed_watch.py": (2, cpl + "\ncp-owed: UNREADABLE critical path: not JSON\n", "")})
+    bj.cp_owed(c)
+    res["cp-owed: rc 2 is its UNREADABLE line, never its partial lines"] = (
+        digest(c) == "cp-owed: UNREADABLE critical path: not JSON\n")
+    c, f = fresh(overlay={"repo": "o/r"})
+    bj.cp_owed(c)
+    res["cp-owed: an overlay with no fire_ledger is UNREADABLE and runs nothing"] = (
+        digest(c) == "cp-owed: UNREADABLE overlay lacks fire_ledger\n" and f.ran("owed_watch.py") == 0)
+    c, f = fresh(overlay={"repo": "o/r", "fire_ledger": "/fired"}, answers={"owed_watch.py": (0, "note\n", "")})
+    bj.cp_owed(c)
+    res["cp-owed null: nothing owed writes no byte"] = not files(c) and f.ran("owed_watch.py") == 1
+    row = [j for j in json.loads((HERE / "beatd.jobs.json").read_text())["jobs"] if j["name"] == "cp-owed"]
+    res["cp-owed: the table row runs every 300 s, under the shortest grace, and takes no class lock"] = (
+        len(row) == 1 and row[0]["interval_s"] <= 300 and row[0]["class"] is None)
+
     # pulse
     ok = "PULSE opener ok fine\npulse: 1 arms, 0 stopped, 0 unreadable at 2026-11-01T09:00:00Z\n"
     c, f = fresh(answers={"pulse.py": (0, ok, "")})
@@ -1314,6 +1340,14 @@ MUTANTS = {
                             "gantt: sweep_gantt is handed the plan, acks, roster, open PRs, live handoff rows and the fire ledger"),
     "verdict_filter_dropped": ('if ln.startswith("UNHELD ")])', "])",
                                "verdict-audit: an UNHELD line reaches the digest, and the repo, ledger and skip file are handed on"),
+    "cp_owed_filter_dropped": ('    write_job(ctx, "cp-owed", [ln for ln in out.splitlines() if ln.startswith("CP-OWED ")])',
+                               '    write_job(ctx, "cp-owed", out.splitlines())',
+                               "cp-owed: a CP-OWED line reaches the digest, and the repo, ledger and checkout are handed on"),
+    "cp_owed_rc_ignored": ('    if rc != 0:\n        why = next((ln for ln in out.splitlines() if ln.startswith("cp-owed: UNREADABLE"))',
+                           '    if False:\n        why = next((ln for ln in out.splitlines() if ln.startswith("cp-owed: UNREADABLE"))',
+                           "cp-owed: rc 2 is its UNREADABLE line, never its partial lines"),
+    "cp_owed_ledger_optional": ('got = ctx.need("cp-owed", "repo", "fire_ledger")', 'got = ctx.need("cp-owed", "repo", "repo")',
+                                "cp-owed: an overlay with no fire_ledger is UNREADABLE and runs nothing"),
     "verdict_rc_ignored": ('    if rc != 0:\n        return write_job(ctx, "verdict-audit",', '    if False:\n        return write_job(ctx, "verdict-audit",',
                            "verdict-audit: a failed run is UNREADABLE, never its partial lines"),
     "gantt_gh_rc_ignored": ('    if rc != 0:\n        return write_job(ctx, "gantt", [f"gantt: UNREADABLE gh pr list',
diff --git a/tools/audit/seat/beatd.jobs.json b/tools/audit/seat/beatd.jobs.json
index a428a776eb..82e82ba616 100644
--- a/tools/audit/seat/beatd.jobs.json
+++ b/tools/audit/seat/beatd.jobs.json
@@ -280,6 +280,26 @@
       "class": null,
       "kind": "periodic"
     },
+    {
+      "name": "cp-owed",
+      "argv": [
+        "python3",
+        "-I",
+        "tools/audit/seat/beat_jobs.py",
+        "cp-owed",
+        "--state",
+        "$S"
+      ],
+      "cwd": "orch",
+      "interval_s": 300,
+      "timeout_s": 180,
+      "heartbeat_s": null,
+      "env_pass": [
+        "GH_TOKEN"
+      ],
+      "class": null,
+      "kind": "periodic"
+    },
     {
       "name": "bottleneck",
       "argv": [
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index a7d15fee4a..3af801eaeb 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -125,9 +125,6 @@ ROOT = Path(__file__).resolve().parents[3]
 RULESET = "main-protect-checks"
 STUCK_FACTOR = 2  # a lane pending past this many critical-path medians is stuck (ETA and WAITING share it)
 RECUT_BLOCKED = 3          # the owner's three-round rule: the third blocked verdict owes a re-cut
-SEAT_WINDOW_MIN = 120      # "a seat is on it": a fire or a handoff ref move inside this window
-FIRE_GRACE_MIN = 15        # a rendered payload this old with no FIRED line is FIRE-OWED
-FIRED_STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z?)")
 GATE_CONTEXTS = {"gate", "pr-contract"}  # the contexts an early-gate race reddens
 STALL_MINUTES = 90  # P328: p95 dispatch-to-verdict is 70 min; 90 fires on ~2.6% of reviews
 #: Per merge_train.py (its self-test pins the two equal): under the umbrella
@@ -252,13 +249,16 @@ def _module(name: str, *candidates: str):
 mt = _module("merge_train_tick", "tools/audit/seat/merge_train.py")
 #: The CI-priority rule (owner, tvofi 2026-10-28): the one order owed PRs print in.
 cpri = _module("ci_priority_tick", "tools/audit/seat/ci_priority.py")
+#: The owed-event watch (R11-PRE-STANDING-SCRIPTS): the one owner of the fired-ledger read,
+#: "a seat is on it" and FIRE-OWED; the methods below delegate to it.
+owatch = _module("owed_watch_tick", "tools/audit/seat/owed_watch.py")
 #: A paused.json record older than this with no train running is owed (P267).
 PAUSED_OWED_MIN = 60
 
 
 def verdict_kind(line: str, head: str) -> "str | None":
     """'merge' or 'blocked' when the approver verdict line names exactly `head`."""
-    m = re.match(r"^Fix review: (merge|blocked) ([0-9a-f]{40})(?: |$)", line)
+    m = owatch.FIX_VERDICT.match(line)  # the one verdict-line grammar
     return m.group(1) if m and m.group(2) == head else None
 
 
@@ -815,27 +815,8 @@ class Tick:
             return None
 
     def _fired(self) -> "list[tuple]":
-        """[(utc or None, line)] for each FIRED line of the dispatch seat's ledger."""
-        try:
-            with open(self.fired_log, encoding="utf-8", errors="replace") as fh:
-                rows = [l.strip() for l in fh if "FIRED" in l]
-        except (OSError, TypeError):
-            return []
-        out = []
-        for l in rows:
-            m = FIRED_STAMP.match(l)
-            when = None
-            if m:
-                when = datetime.datetime.fromisoformat(m.group(1).rstrip("Z")).replace(
-                    tzinfo=datetime.timezone.utc)
-            out.append((when, l))
-        return out
-
-    def _fire_names(self, n: int, topics: list, line: str) -> bool:
-        """A FIRED line names a PR by number, topic or its payload file
-        (`payload-fix-<n>-r<k>.json`, `payload-<n>-r<k>.json`)."""
-        return bool(re.search(rf"#{n}(?!\d)|payload-(?:fix-)?{n}-r\d+\.json", line)) or any(
-            t and re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", line, re.I) for t in topics)
+        """[(utc or None, line)] for each FIRED line of the dispatch seat's ledger (owed_watch.fired)."""
+        return owatch.fired(self.fired_log)
 
     def _disposed(self, ref: str, sha: str) -> bool:
         """The obligations ledger holds a disposition for `ref` at exactly `sha` (an older sha
@@ -854,27 +835,8 @@ class Tick:
         return text if code == 0 else None
 
     def _seat_on(self, n: int, topics: list, heads: dict, kinds=("handoff-wip", "handoff", "handoff-body")) -> bool:
-        """A seat is on a PR when, inside SEAT_WINDOW_MIN, a FIRED line names it, or a
-        handoff-wip/, handoff/ or handoff-body/<topic> ref moved (`kinds` narrows the refs)."""
-        cutoff = self.now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
-        for when, l in self._fired():
-            if (when is None or when >= cutoff) and self._fire_names(n, topics, l):
-                return True
-        tg = _module("topic_grammar_tick", "tools/audit/seat/topic_grammar.py")
-        for t in topics:
-            for fam in kinds:
-                refs = [f"{fam}/{t}"]
-                if fam == "handoff-wip":  # a split seat step-pushes under the family's topic (topic-family.md)
-                    refs += sorted(k for k in heads if k.startswith("handoff-wip/")
-                                   and k != refs[0] and tg.family(t).fullmatch(k[len("handoff-wip/"):]))  # mut:wipfamily
-                for ref in refs:
-                    sha = heads.get(ref)
-                    if fam == "handoff-wip" and sha and self._blocked_md(sha) is not None:  # mut:blockedseat
-                        continue  # a stop on a question is owed by blocked_stops, not a seat on the PR
-                    age = self._age_min(ref, sha) if sha else None
-                    if age is not None and age <= SEAT_WINDOW_MIN:
-                        return True
-        return False
+        """owed_watch.seat_on over this tick's ledger, clock and git reads."""
+        return owatch.seat_on(n, topics, heads, self._fired(), self.now, self._age_min, self._blocked_md, kinds)
 
     @staticmethod
     def _topics(branch: str) -> list:
@@ -1084,15 +1046,11 @@ class Tick:
         return "review-owed", "", ""
 
     def payloads(self, S: str) -> None:
-        """FIRE-OWED: a rendered payload file older than FIRE_GRACE_MIN that no FIRED line names."""
+        """FIRE-OWED (owed_watch.fire_owed): a rendered payload past its grace that no FIRED line names."""
         if not self.payload_dir:
             return
-        fired = self._fired()
-        for f in sorted(Path(self.payload_dir).glob("payload-*.json")):
-            age = (self.now.timestamp() - f.stat().st_mtime) / 60
-            if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in fired):
-                self.line(S, f"OWED fire-owed {f.name} rendered {int(age)}m ago, no FIRED line "
-                             "(firing is a RemoteTrigger call: the orchestrator's turn)", flag=True)
+        for text in owatch.fire_owed(self.payload_dir, self._fired(), self.now):
+            self.line(S, text, flag=True)
 
     def _reviewer_ref_age(self, n: int) -> "int | None":
         """Minutes since the tip of `dispatch/reviewer-rev-<n>` (cloud_dispatch.py's
@@ -4394,13 +4352,13 @@ def self_test() -> int:
             fl.write_text(fired)
             tf = tick(prs=[], fired_log=str(fl), payload_dir=str(pd))
             tf.payloads("PRS")
-            return [x["text"] for x in tf.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed")]
+            return [x["text"] for x in tf.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed") and x["flag"]]
         fo, fo0 = fire_owed(""), fire_owed("FIRED payload-fix-86-r1.json\n")
         pd2 = tmp / "payloads-young"
         pd2.mkdir()
         pf2 = pd2 / "payload-fix-86-r2.json"
         pf2.write_text("{}")
-        os.utime(pf2, ((NOW - timedelta(minutes=FIRE_GRACE_MIN - 5)).timestamp(),) * 2)
+        os.utime(pf2, ((NOW - timedelta(minutes=owatch.FIRE_GRACE_MIN - 5)).timestamp(),) * 2)
         tfy = tick(prs=[], fired_log=os.devnull, payload_dir=str(pd2))
         tfy.payloads("PRS")
         fo_young = [x["text"] for x in tfy.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed")]
diff --git a/tools/audit/seat/owed_watch.py b/tools/audit/seat/owed_watch.py
new file mode 100644
index 0000000000..5d6cb62b74
--- /dev/null
+++ b/tools/audit/seat/owed_watch.py
@@ -0,0 +1,699 @@
+#!/usr/bin/env python3
+"""owed_watch.py -- the owed-event watch: who was fired, whether a seat is on it, what is owed past its grace.
+
+    python3 -I tools/audit/seat/owed_watch.py cp-owed --repo O/R --fired LEDGER [--checkout DIR] [--roster-ref REF]
+    python3 -I tools/audit/seat/owed_watch.py --self-test
+
+WHY THIS EXISTS (R11-PRE-STANDING-SCRIPTS part 1, design/R11-PRE-STANDING-SCRIPTS 375ce7ff3f,
+approved at design-verdict be6cc24cae). The owner's directive (tvofi 2026-11-09, triage
+s6-batch141.md P515): "never let the critical path or outside PRs slip, ever". The watch ran only
+as a session-local loop. This module owns the fired-ledger read, the "a seat is on it" predicate
+and every owed-by-grace arm; orchestrator_tick.py imports the first two and its FIRE-OWED level,
+and the beat's `cp-owed` row (beat_jobs.py) runs `cp-owed` here.
+
+THE WATCHED SET is computed, never hand-kept: every open roster group `roster_lib.is_outside` is
+true for, plus every group `roster_lib.critical_path_read` publishes at the roster ref, and the
+open pull requests mapped to them (`group_for_branch`, else `group_for_pr`). An unreadable
+critical-path file is UNREADABLE, never an empty set.
+
+THE ARMS, one `CP-OWED <arm> <subject> ...` line per step past its grace (GRACE_MIN):
+  merge-no-approval  a `Fix review: merge <head>` verdict at the PR head, no APPROVED review at it
+  approved-unmerged  an APPROVED review at the head of a still-open PR
+  blocked-no-fire    a `Fix review: blocked <head>` verdict at the head, no FIRED line naming the PR
+                     and no handoff ref moved since the verdict
+  head-no-dispatch   no verdict at the head and no reviewer dispatch whose prompt names the head
+  UNFIRED            a dispatch ref of the group (fixer, designer, design reviewer, reviewer) with
+                     no FIRED line naming the group and no return ref moved since it was published
+  DESIGN-REVIEW-OWED a design tip no design verdict names (P510's predicate); a `seat-refused`
+                     verdict is no review; a tip whose note opens `Design blocked:` is a designer
+                     stop, owed by the dispatch drain, never here
+  FIXER-OWED         an approve at the design tip, no fixer dispatch and no handoff ref since
+  SEAT-SILENT        the group's newest FIRED line with no return ref moved since it, keyed on
+                     refs and never on a cloud session's status (a dead session reads running)
+"After" compares a FIRED line's leading UTC stamp with the step's commit time; an unstamped line
+is never "after" anything. Lines are ranked by `roster_lib.dispatch_rank` (hotfix, then
+critical path or outside), the critical path ahead of outside inside a rank, oldest first.
+Exit 0 with the lines, 2 with `cp-owed: UNREADABLE <what>` lines when a read failed.
+"""
+from __future__ import annotations
+
+import argparse
+import datetime
+import json
+import os
+import re
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+SEAT = Path(__file__).resolve().parent
+sys.path.insert(0, str(SEAT))
+import roster_lib  # noqa: E402
+import topic_grammar  # noqa: E402
+
+SEAT_WINDOW_MIN = 120      # "a seat is on it": a fire or a handoff ref move inside this window
+FIRE_GRACE_MIN = 15        # a rendered payload this old with no FIRED line is FIRE-OWED
+SEAT_KINDS = ("handoff-wip", "handoff", "handoff-body")
+FIRED_STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z?)")
+#: carry 4's graces, minutes. UNFIRED takes FIRE_GRACE_MIN (the same step as FIRE-OWED: published,
+#: not fired) and FIXER-OWED the design-review step's 10 (verdict in, next seat not dispatched);
+#: the carry names no figure for either.
+GRACE_MIN = {"merge-no-approval": 10, "approved-unmerged": 45, "blocked-no-fire": 15,
+             "head-no-dispatch": 25, "UNFIRED": FIRE_GRACE_MIN, "DESIGN-REVIEW-OWED": 10,
+             "FIXER-OWED": 10, "SEAT-SILENT": 90}
+FIX_VERDICT = re.compile(r"^Fix review: (merge|blocked) ([0-9a-f]{40})(?: |$)")
+DESIGN_VERDICT = re.compile(r"^Design review: ([a-z-]+) ([0-9a-f]{40})(.*)$")
+DESIGN_BLOCKED = "Design blocked:"
+FAMILIES = ("verdict", "dispatch", "design", "design-verdict", "handoff", "handoff-wip", "handoff-body", "probe")
+RETURN_FAMILIES = ("handoff", "handoff-wip", "handoff-body", "design", "design-verdict")
+
+
+# ------------------------------------------------------------ the fired ledger (moved from the tick)
+
+def fired(path) -> "list[tuple]":
+    """[(utc datetime or None, line)] for each FIRED line of the dispatch seat's ledger."""
+    try:
+        with open(path, encoding="utf-8", errors="replace") as fh:
+            rows = [l.strip() for l in fh if "FIRED" in l]
+    except (OSError, TypeError):
+        return []
+    out = []
+    for l in rows:
+        m = FIRED_STAMP.match(l)
+        when = None
+        if m:
+            when = datetime.datetime.fromisoformat(m.group(1).rstrip("Z")).replace(
+                tzinfo=datetime.timezone.utc)
+        out.append((when, l))
+    return out
+
+
+def fire_names(n: int, topics: list, line: str) -> bool:
+    """A FIRED line names a PR by number, topic or its payload file
+    (`payload-fix-<n>-r<k>.json`, `payload-<n>-r<k>.json`)."""
+    return bool(re.search(rf"#{n}(?!\d)|payload-(?:fix-)?{n}-r\d+\.json", line)) or any(
+        t and re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", line, re.I) for t in topics)
+
+
+def seat_on(n: int, topics: list, heads: dict, rows: list, now, age_min, blocked_md,
+            kinds=SEAT_KINDS) -> bool:
+    """A seat is on a PR when, inside SEAT_WINDOW_MIN, a FIRED line names it, or a
+    handoff-wip/, handoff/ or handoff-body/<topic> ref moved (`kinds` narrows the refs).
+    `age_min(ref, sha)` and `blocked_md(sha)` are the caller's git reads."""
+    cutoff = now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
+    for when, l in rows:
+        if (when is None or when >= cutoff) and fire_names(n, topics, l):
+            return True
+    for t in topics:
+        for fam in kinds:
+            refs = [f"{fam}/{t}"]
+            if fam == "handoff-wip":  # a split seat step-pushes under the family's topic (topic-family.md)
+                refs += sorted(k for k in heads if k.startswith("handoff-wip/")
+                               and k != refs[0] and topic_grammar.family(t).fullmatch(k[len("handoff-wip/"):]))  # mut:wipfamily
+            for ref in refs:
+                sha = heads.get(ref)
+                if fam == "handoff-wip" and sha and blocked_md(sha) is not None:  # mut:blockedseat
+                    continue  # a stop on a question is owed by blocked_stops, not a seat on the PR
+                age = age_min(ref, sha) if sha else None
+                if age is not None and age <= SEAT_WINDOW_MIN:
+                    return True
+    return False
+
+
+def fire_owed(payload_dir, rows: list, now) -> "list[str]":
+    """FIRE-OWED: a rendered payload file older than FIRE_GRACE_MIN that no FIRED line names."""
+    out = []
+    for f in sorted(Path(payload_dir).glob("payload-*.json")):
+        age = (now.timestamp() - f.stat().st_mtime) / 60
+        if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in rows):
+            out.append(f"OWED fire-owed {f.name} rendered {int(age)}m ago, no FIRED line "
+                       "(firing is a RemoteTrigger call: the orchestrator's turn)")
+    return out
+
+
+# ------------------------------------------------------------------------------ cp-owed, pure
+
+def _names_group(g: dict, line: str) -> bool:
+    """A FIRED line names the group: its id, its topic, or one of its pull requests."""
+    return fire_names(-1, [g["gid"], g["topic"]], line) or any(fire_names(n, [], line) for n in g["prs"])
+
+
+def _fired_since(g: dict, rows: list, t: float) -> bool:
+    return any(when is not None and when >= t and _names_group(g, l) for when, l in rows)
+
+
+def _group_refs(g: dict, refs: dict, families) -> "list[str]":
+    """The group's refs in `families`: <family>/<topic> (any family member for handoff-wip and
+    dispatch/fixer-), <family>/<gid> (design refs carry the group's case), and per pull request
+    verdict/<n>, probe/rev-<n>-<nonce> and dispatch/reviewer-rev-<n>."""
+    fam_t, gid = topic_grammar.family(g["topic"]), g["gid"].lower()
+    out = []
+    for ref in refs:
+        family, _, rest = ref.partition("/")
+        if family not in families:
+            continue
+        low = rest.lower()
+        if family == "dispatch":
+            ok = (low.startswith("fixer-") and fam_t.fullmatch(low[6:])) or low in (
+                f"designer-{gid}", f"design-reviewer-{gid}") or any(low == f"reviewer-rev-{n}" for n in g["prs"])
+        elif family in ("design", "design-verdict"):
+            ok = low == gid
+        elif family == "verdict":
+            ok = any(low == str(n) for n in g["prs"])
+        elif family == "probe":
+            ok = any(low.startswith(f"rev-{n}-") for n in g["prs"])
+        else:
+            ok = bool(fam_t.fullmatch(low)) if family == "handoff-wip" else low == g["topic"]
+        if ok:
+            out.append(ref)
+    return out
+
+
+def _returned_since(g: dict, refs: dict, ctime: dict, t: float) -> bool:
+    return any(ctime[refs[r]] >= t for r in _group_refs(g, refs, RETURN_FAMILIES + ("verdict", "probe")))
+
+
+def cp_owed(groups: dict, prs: list, refs: dict, ctime: dict, first: dict, rows: list, now: float,
+            graces: dict = GRACE_MIN) -> "list[str]":
+    """The CP-OWED lines, ranked. groups: gid -> {gid, topic, tags, rank, prs}; prs: dicts
+    number/head/gid/head_t/approved_t; refs: `<family>/<name>` -> sha; ctime: sha -> epoch;
+    first: sha -> the first line of the tip's note (VERDICT.md, verdict.md, design.md, PROMPT.md);
+    rows: `fired()`'s output, stamps as epochs or None."""
+    owed = []
+
+    def owe(g, arm, subject, since, detail):
+        age = int((now - since) // 60)
+        if now - since > graces[arm] * 60:  # mut:grace
+            tags = " ".join(g["tags"])
+            owed.append(((g["rank"], "CP" not in g["tags"], -age),
+                         f"CP-OWED {arm} {subject} {age}m past its {graces[arm]}m grace [{tags}] -- {detail}"))
+
+    for p in prs:
+        g, n, head = groups[p["gid"]], p["number"], p["head"]
+        vsha = refs.get(f"verdict/{n}")
+        m = FIX_VERDICT.match(first.get(vsha, "")) if vsha else None
+        at_head = bool(m) and m[2] == head
+        if p.get("approved_t") is not None:
+            owe(g, "approved-unmerged", f"#{n}", p["approved_t"], f"approved at {head[:12]}, not merged")
+        elif at_head and m[1] == "merge":
+            owe(g, "merge-no-approval", f"#{n}", ctime[vsha], f"merge verdict at {head[:12]}, no approval")
+        if at_head and m[1] == "blocked":
+            t = ctime[vsha]
+            if not _fired_since(g, rows, t) and not any(  # mut:blockedfire
+                    ctime[refs[r]] >= t for r in _group_refs(g, refs, ("handoff", "handoff-wip", "handoff-body"))):
+                owe(g, "blocked-no-fire", f"#{n}", t, f"blocked at {head[:12]}, no fire and no repair since")
+        if not at_head:
+            dsha = refs.get(f"dispatch/reviewer-rev-{n}")
+            if not (dsha and f"at head {head}" in first.get(dsha, "")):  # mut:dispatchhead
+                owe(g, "head-no-dispatch", f"#{n}", p["head_t"], f"head {head[:12]} has no verdict and no reviewer dispatch")
+
+    for gid, g in groups.items():
+        for ref in _group_refs(g, refs, ("dispatch",)):
+            t = ctime[refs[ref]]
+            if not _fired_since(g, rows, t) and not _returned_since(g, refs, ctime, t):  # mut:unfired
+                owe(g, "UNFIRED", gid, t, f"{ref} published, no FIRED line and no return since")
+        dsha = refs.get(next((r for r in refs if r.lower() == f"design/{gid.lower()}"), ""))
+        if dsha and not first.get(dsha, "").startswith(DESIGN_BLOCKED):  # mut:designblocked
+            vsha = refs.get(next((r for r in refs if r.lower() == f"design-verdict/{gid.lower()}"), ""))
+            m = DESIGN_VERDICT.match(first.get(vsha, "")) if vsha else None
+            refused = bool(m) and m[3].split()[-1:] == ["seat-refused"]  # mut:seatrefused
+            kind = m[1] if m and m[2] == dsha and not refused else None  # the review at the tip, if any
+            if kind is None:
+                owe(g, "DESIGN-REVIEW-OWED", gid, ctime[dsha], f"design/{gid} at {dsha[:12]} has no design review")
+            elif kind == "approve":
+                t = ctime[vsha]
+                if not any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))
+                           if not r.startswith(("dispatch/design", "dispatch/reviewer-rev-"))):  # mut:fixerowed
+                    owe(g, "FIXER-OWED", gid, t, f"design approved at {dsha[:12]}, no fixer dispatched")
+        last = max((when for when, l in rows if when is not None and _names_group(g, l)), default=None)
+        if last is not None and not _returned_since(g, refs, ctime, last):  # mut:silent
+            owe(g, "SEAT-SILENT", gid, last, "fired, no return ref since")
+    return [line for _, line in sorted(owed)]
+
+
+# ------------------------------------------------------------------------------ cp-owed, live
+
+def sh(argv, cwd=None):
+    p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
+    return p.returncode, p.stdout + p.stderr
+
+
+class Unreadable(Exception):
+    pass
+
+
+def _epoch(iso: str) -> float:
+    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
+
+
+def read_world(repo: str, checkout: str, fired_path: str, roster_ref, run=sh):
+    """The pure core's inputs, read over gh and git; Unreadable names the first read that failed."""
+    git = lambda *a: run(["git", "-C", checkout, *a])
+    ref = roster_lib.reader_ref(checkout, roster_ref)
+    try:
+        roster = roster_lib.show_roster(checkout, ref)
+    except (roster_lib.RosterNotFound, ValueError) as e:
+        raise Unreadable(f"roster at {ref}: {e}")
+    cp, why = roster_lib.critical_path_read(checkout, ref)
+    if cp is None:
+        raise Unreadable(f"critical path: {why}")
+    groups = {}
+    for gid, g in roster_lib.open_groups(roster).items():
+        tags = [t for t, on in (("HOTFIX", roster_lib.is_hotfix(g)), ("CP", roster_lib.norm_group(gid) in cp),
+                                ("OUTSIDE", roster_lib.is_outside(g))) if on]
+        if "CP" in tags or "OUTSIDE" in tags:
+            groups[gid] = {"gid": gid, "topic": roster_lib.branch_of(g).split("/", 1)[-1].lower(), "tags": tags,
+                           "rank": roster_lib.dispatch_rank(roster, gid, cp), "prs": []}
+    code, o = run(["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "300",
+                   "--json", "number,headRefOid,headRefName,reviews"])
+    try:
+        listed = json.loads(o) if code == 0 else None
+        if not isinstance(listed, list):
+            raise ValueError(o.strip()[-120:])
+    except ValueError as e:
+        raise Unreadable(f"open pull requests: {e}")
+    prs = []
+    for p in listed:
+        gid = roster_lib.group_for_branch(roster, p.get("headRefName") or "") or roster_lib.group_for_pr(roster, p["number"])
+        if gid in groups:
+            groups[gid]["prs"].append(p["number"])
+            ok = [_epoch(r["submittedAt"]) for r in p.get("reviews") or ()
+                  if r.get("state") == "APPROVED" and (r.get("commit") or {}).get("oid") == p["headRefOid"]]
+            prs.append({"number": p["number"], "head": p["headRefOid"], "gid": gid,
+                        "approved_t": max(ok) if ok else None})
+    code, o = git("ls-remote", "origin", *(f"refs/heads/{f}/*" for f in FAMILIES))
+    if code:
+        raise Unreadable(f"ls-remote: {o.strip()[-120:]}")
+    every = {l.split()[1][len("refs/heads/"):]: l.split()[0] for l in o.splitlines()
+             if len(l.split()) == 2 and l.split()[1].startswith("refs/heads/")}
+    refs = {r: every[r] for g in groups.values() for r in _group_refs(g, every, FAMILIES)}
+    want = sorted(set(refs.values()) | {p["head"] for p in prs})
+    if want:
+        code, o = git("fetch", "-q", "origin", *(f"refs/heads/{r}" for r in sorted(refs)),
+                      *(f"refs/pull/{p['number']}/head" for p in prs))
+        if code:
+            raise Unreadable(f"fetch: {o.strip()[-120:]}")
+        code, o = git("log", "--no-walk", "--format=%H %ct", *want)
+        if code:
+            raise Unreadable(f"commit times: {o.strip()[-120:]}")
+    ctime = {l.split()[0]: float(l.split()[1]) for l in (o.splitlines() if want else []) if len(l.split()) == 2}
+    first = {}
+    for r, sha in refs.items():
+        note = {"verdict": "VERDICT.md", "design-verdict": "verdict.md", "design": "design.md",
+                "dispatch": "PROMPT.md"}.get(r.split("/", 1)[0])
+        if note:
+            code, o = git("show", f"{sha}:{note}")
+            first[sha] = (o.splitlines() or [""])[0] if code == 0 else ""
+    for p in prs:
+        p["head_t"] = ctime.get(p["head"])
+        if p["head_t"] is None:
+            raise Unreadable(f"#{p['number']}'s head {p['head'][:12]} commit time")
+    rows = [(w.timestamp() if w else None, l) for w, l in fired(fired_path)]
+    return groups, prs, refs, ctime, first, rows
+
+
+def main(argv=None) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    ap.add_argument("cmd", nargs="?", choices=("cp-owed",))
+    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
+    ap.add_argument("--fired", help="the dispatch seat's fire ledger")
+    ap.add_argument("--checkout", default=".")
+    ap.add_argument("--roster-ref")
+    ap.add_argument("--self-test", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    if a.cmd != "cp-owed" or not a.fired:
+        ap.error("cp-owed needs --fired")
+    try:
+        world = read_world(a.repo, a.checkout, a.fired, a.roster_ref)
+    except Unreadable as e:
+        print(f"cp-owed: UNREADABLE {e}")
+        return 2
+    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
+    for line in cp_owed(*world, now):
+        print(line)
+    return 0
+
+
+# ------------------------------------------------------------------------------ self-test
+SELF_TEST_MARK = "# " + "-" * 78 + " self-test"
+
+
+def _world(arm: str, grace0: bool):
+    """A planted world: one critical-path group CPG (PR #11) and one outside group OUT (PR #12),
+    every timestamp 60 min before now. `arm` plants exactly one owed step; "none" plants none."""
+    now, t = 1_800_000_000.0, 1_800_000_000.0 - 3600
+    h = {k: c * 40 for k, c in (("h11", "1"), ("h12", "2"), ("d", "d"), ("v", "e"), ("x", "f"))}
+    groups = {"CPG": {"gid": "CPG", "topic": "r11-cpg", "tags": ["CP"], "rank": 1, "prs": [11]},
+              "OUT": {"gid": "OUT", "topic": "r11-out", "tags": ["OUTSIDE"], "rank": 1, "prs": [12]}}
+    prs = [{"number": 11, "head": h["h11"], "gid": "CPG", "head_t": t, "approved_t": None},
+           {"number": 12, "head": h["h12"], "gid": "OUT", "head_t": t, "approved_t": None}]
+    refs = {"dispatch/reviewer-rev-11": "a1" * 20, "dispatch/reviewer-rev-12": "a2" * 20,
+            "verdict/12": "b2" * 20, "handoff/r11-cpg": "c1" * 20}
+    first = {"a1" * 20: f"CLOUD REVIEWER seat for PR #11, at head {h['h11']}. Bus nonce: x",
+             "a2" * 20: f"CLOUD REVIEWER seat for PR #12, at head {h['h12']}. Bus nonce: y",
+             "b2" * 20: f"Fix review: blocked {'0' * 40} code: old head"}
+    ctime = {h["h11"]: t, h["h12"]: t, "c1" * 20: t + 90, "b2" * 20: t + 90}  # each seat returned after its fire
+    rows = [(t + 60, "FIRED reviewer #11"), (t + 60, "FIRED reviewer #12")]
+    if arm == "merge-no-approval":
+        refs["verdict/11"], first["9" * 40] = "9" * 40, f"Fix review: merge {h['h11']}"
+    elif arm == "approved-unmerged":
+        refs["verdict/11"], first["9" * 40] = "9" * 40, f"Fix review: merge {h['h11']}"
+        prs[0]["approved_t"] = t
+    elif arm == "blocked-no-fire":
+        refs["verdict/12"], first["9" * 40] = "9" * 40, f"Fix review: blocked {h['h12']} code: x"
+        rows = [(t - 60, "FIRED reviewer #12"), (t + 60, "FIRED reviewer #11")]
+    elif arm == "head-no-dispatch":
+        first["a1" * 20] = f"CLOUD REVIEWER seat for PR #11, at head {'7' * 40}. Bus nonce: x"
+    elif arm == "UNFIRED":
+        refs["dispatch/designer-OUT"] = "8" * 40
+        ctime["8" * 40] = t + 120
+    elif arm in ("DESIGN-REVIEW-OWED", "seat-refused", "revise-at-tip", "design-blocked"):
+        refs["design/OUT"], first[h["d"]] = h["d"], ("Design blocked: ref_privacy refused" if arm == "design-blocked"
+                                                    else "# OUT: a design")
+        if arm in ("seat-refused", "revise-at-tip"):
+            refs["design-verdict/OUT"] = h["v"]
+            first[h["v"]] = f"Design review: revise {h['d']}" + (" seat-refused" if arm == "seat-refused" else "")
+    elif arm == "FIXER-OWED":
+        refs["design/OUT"], refs["design-verdict/OUT"] = h["d"], h["v"]
+        first[h["d"]], first[h["v"]] = "# OUT: a design", f"Design review: approve {h['d']}"
+        ctime[h["v"]] = t + 120
+    elif arm == "SEAT-SILENT":
+        rows.append((t + 300, "FIRED fixer for r11-out"))
+    for sha in refs.values():
+        ctime.setdefault(sha, t)
+    if grace0:
+        return groups, prs, refs, ctime, first, rows, now, dict.fromkeys(GRACE_MIN, 0)
+    return groups, prs, refs, ctime, first, rows, now, dict.fromkeys(GRACE_MIN, 24 * 60)
+
+
+ARMS = tuple(GRACE_MIN)
+
+
+def _aged(world):
+    """A planted world's refs and heads moved 1e8 s into the past, so a run at the real clock reads them old."""
+    groups, prs, refs, ctime, first, rows = world
+    return groups, prs, refs, {k: v - 1e8 for k, v in ctime.items()}, first, rows
+
+
+def cases(mod) -> "dict[str, bool]":
+    res = {}
+    run = lambda arm, g0=True: mod.cp_owed(*_world(arm, g0))
+    base = run("none")
+    res["null: every step answered, nothing is owed (grace 0)"] = base == []
+    for arm in ARMS:
+        got = run(arm)
+        res[f"planted {arm}: one line at grace 0"] = (
+            len(got) == 1 and got[0].startswith(f"CP-OWED {arm} ") and "past its 0m grace" in got[0])
+        res[f"null {arm}: inside its grace prints nothing"] = run(arm, False) == []
+    res["DESIGN-REVIEW-OWED: a seat-refused verdict at the tip is no review"] = (
+        [l.split()[1] for l in run("seat-refused")] == ["DESIGN-REVIEW-OWED"])
+    res["DESIGN-REVIEW-OWED null: a class-open revise at the tip is a review (the designer owes)"] = run("revise-at-tip") == []
+    res["DESIGN-REVIEW-OWED null: a `Design blocked:` tip is a designer stop, not a review owed"] = run("design-blocked") == []
+    w = list(_world("UNFIRED", True))
+    w[2]["handoff/r11-out"], w[3]["c9" * 20] = "c9" * 20, w[3]["8" * 40] + 60
+    res["UNFIRED null: a return ref newer than the dispatch is a fire"] = mod.cp_owed(*w) == []
+    def variant(arm, **extra):
+        """`arm`'s world with refs added: name -> (sha, seconds after the world's step time, first line)."""
+        w = list(_world(arm, True))
+        for ref, (sha, dt, line) in extra.items():
+            w[2][ref.replace("__", "/")], w[3][sha], w[4][sha] = sha, w[6] - 3600 + dt, line
+        return mod.cp_owed(*w)
+    got = variant("none", dispatch__fixer_x=("f1" * 20, 120, ""))
+    res["UNFIRED: only the group's own dispatch refs count (a stranger's fixer dispatch is not the group's)"] = got == []
+    got = variant("none", **{"dispatch__fixer-r11-out-p2": ("f1" * 20, 120, "")})
+    res["UNFIRED: a fixer dispatch of a family member (-p2) is the group's"] = (
+        [l.split()[1:3] for l in got] == [["UNFIRED", "OUT"]])
+    for name, ref, line in (("a design push", "design__OUT", "Design blocked: x"),
+                            ("a probe verdict", "probe__rev-12-abcd", ""),
+                            ("a family member's step push", "handoff-wip__r11-out-p1", "")):
+        res[f"SEAT-SILENT null: {name} after the fire is a return"] = variant("SEAT-SILENT", **{ref: ("f2" * 20, 400, line)}) == []
+    res["SEAT-SILENT: a design push of another group is no return"] = (
+        [l.split()[1] for l in variant("SEAT-SILENT", design__OUTX=("f2" * 20, 400, "Design blocked: x"))] == ["SEAT-SILENT"])
+    res["blocked-no-fire null: a handoff ref at the verdict's own second is a repair"] = (
+        variant("blocked-no-fire", **{"handoff__r11-out": ("f3" * 20, 0, "")}) == [])
+    w = list(_world("UNFIRED", True))
+    w[5] = w[5] + [(w[3]["8" * 40], "FIRED designer R11-out OUT")]
+    res["UNFIRED null: a FIRED line naming the group, stamped at the dispatch's own second, is a fire"] = not any(
+        l.split()[1] == "UNFIRED" for l in mod.cp_owed(*w))
+    w[5][-1] = (w[3]["8" * 40] - 1, "FIRED designer OUT")
+    res["UNFIRED: a FIRED line a second before the dispatch is no fire for it"] = (
+        [l.split()[1] for l in mod.cp_owed(*w) if l.split()[1] == "UNFIRED"] == ["UNFIRED"])
+    res["FIXER-OWED's age runs from the approve verdict, not from another ref"] = " 58m past " in (run("FIXER-OWED") or [""])[0]
+    res["the line names the step's age in whole minutes"] = " 60m past its 0m grace " in (run("merge-no-approval") or [""])[0]
+    w = list(_world("none", True))
+    w[0]["OUT"]["tags"], w[0]["OUT"]["rank"] = ["HOTFIX", "OUTSIDE"], 0
+    w[0]["CPG"]["tags"] = ["CP"]
+    w[2]["design/OUT"], w[2]["design/CPG"] = "d1" * 20, "d2" * 20
+    w[3]["d1" * 20] = w[3]["d2" * 20] = w[6] - 7200
+    ranked = mod.cp_owed(*w)
+    res["rank: a hotfix group ahead of a critical-path one (roster_lib.dispatch_rank)"] = (
+        [l.split()[2] for l in ranked] == ["OUT", "CPG"])
+    w[0]["OUT"]["tags"], w[0]["OUT"]["rank"] = ["OUTSIDE"], 1
+    res["rank: inside one rank the critical path is ahead of outside"] = (
+        [l.split()[2] for l in mod.cp_owed(*w)] == ["CPG", "OUT"])
+    return res
+
+
+#: one edit per arm, in a temp copy of this file; the named case must fail.
+MUTANTS = {
+    "grace_ignored": ("if now - since > graces[arm] * 60:  # mut:grace", "if True:  # mut:grace",
+                      "null merge-no-approval: inside its grace prints nothing"),
+    "approval_ignored": ('if p.get("approved_t") is not None:', "if False:", "planted approved-unmerged: one line at grace 0"),
+    "merge_arm": ('elif at_head and m[1] == "merge":', "elif False:", "planted merge-no-approval: one line at grace 0"),
+    "blocked_fire": ("if not _fired_since(g, rows, t) and not any(  # mut:blockedfire", "if any(  # mut:blockedfire",
+                     "planted blocked-no-fire: one line at grace 0"),
+    "dispatch_head": ('if not (dsha and f"at head {head}" in first.get(dsha, "")):  # mut:dispatchhead',
+                      "if not dsha:  # mut:dispatchhead", "planted head-no-dispatch: one line at grace 0"),
+    "unfired": ("if not _fired_since(g, rows, t) and not _returned_since(g, refs, ctime, t):  # mut:unfired",
+                "if not _fired_since(g, rows, t):  # mut:unfired",
+                "UNFIRED null: a return ref newer than the dispatch is a fire"),
+    "unfired_dropped": ('owe(g, "UNFIRED", gid, t,', 'None and owe(g, "UNFIRED", gid, t,', "planted UNFIRED: one line at grace 0"),
+    "design_blocked": ("if dsha and not first.get(dsha, \"\").startswith(DESIGN_BLOCKED):  # mut:designblocked",
+                       "if dsha:  # mut:designblocked",
+                       "DESIGN-REVIEW-OWED null: a `Design blocked:` tip is a designer stop, not a review owed"),
+    "seat_refused": ('refused = bool(m) and m[3].split()[-1:] == ["seat-refused"]  # mut:seatrefused',
+                     "refused = False  # mut:seatrefused",
+                     "DESIGN-REVIEW-OWED: a seat-refused verdict at the tip is no review"),
+    "design_review_dropped": ("            if kind is None:\n", "            if False:\n",
+                              "planted DESIGN-REVIEW-OWED: one line at grace 0"),
+    "fixer_owed": ('if not any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))',
+                   'if any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))',
+                   "planted FIXER-OWED: one line at grace 0"),
+    "silent": ("if last is not None and not _returned_since(g, refs, ctime, last):  # mut:silent",
+               "if False:  # mut:silent", "planted SEAT-SILENT: one line at grace 0"),
+    "rank_cp_first": ('owed.append(((g["rank"], "CP" not in g["tags"], -age),', 'owed.append(((g["rank"], "CP" in g["tags"], -age),',
+                      "rank: inside one rank the critical path is ahead of outside"),
+    "rank_dropped": ('owed.append(((g["rank"], "CP" not in g["tags"], -age),', 'owed.append((("CP" not in g["tags"], -age),',
+                     "rank: a hotfix group ahead of a critical-path one (roster_lib.dispatch_rank)"),
+}
+
+
+def read_world_checks() -> "dict[str, bool]":
+    """read_world over a throwaway origin: the roster and critical-path file on main, the watched
+    groups' refs and two pull-request heads; gh answered by a fake, every git read real."""
+    sys.path.insert(0, str(SEAT.parents[2] / "tests"))
+    from throwaway_git import throwaway_git_clone, throwaway_git_environ, throwaway_git_init
+    res = {}
+    with tempfile.TemporaryDirectory() as d, throwaway_git_environ():
+        o, c = Path(d) / "o", Path(d) / "c"
+        throwaway_git_init(o, "-q", "-b", "main")
+        g = lambda *a, cwd=o: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
+
+        def commit(branch, name, text, when):
+            g("checkout", "-q", "--orphan" if branch != "main" else "-B", branch)
+            g("rm", "-rqf", "--ignore-unmatch", ".")
+            (o / name).parent.mkdir(parents=True, exist_ok=True)
+            (o / name).write_text(text)
+            g("add", name)
+            env = {"GIT_COMMITTER_DATE": f"@{when} +0000", "GIT_AUTHOR_DATE": f"@{when} +0000"}
+            subprocess.run(["git", "commit", "-qm", branch], cwd=o, check=True, capture_output=True,
+                           env={**__import__("os").environ, **env})
+            return g("rev-parse", "HEAD")
+        roster = {"groups": [
+            {"group": "R11-CPG", "resume": {"stage": "not-started", "branch": "fix/r11-cpg"}},
+            {"group": "R11-OUT", "source": "outside", "resume": {"stage": "not-started", "pr": 12}},
+            {"group": "R11-OFF", "resume": {"stage": "not-started"}},
+            {"group": "R11-SHUT", "source": "outside", "resume": {"stage": "done"}}]}
+        commit("main", f"{roster_lib.ROSTERS_DIR}/wave-r11-groups.json", json.dumps(roster), 1_000)
+        (o / roster_lib.CRITICAL_PATH_NAME).write_text(json.dumps({"critical": ["R11-CPG"]}))
+        g("add", "-A")
+        g("commit", "-qm", "cp")
+        h11 = commit("work11", "x", "11", 2_000)
+        h12 = commit("work12", "x", "12", 3_000)
+        v12 = commit("verdict/12", "VERDICT.md", f"Fix review: merge {h12}\n", 4_000)
+        r11 = commit("dispatch/reviewer-rev-11", "PROMPT.md", f"CLOUD REVIEWER seat for PR #11, at head {h11}.\nRole\n", 5_000)
+        dz = commit("design/R11-OUT", "design.md", "# a design\n", 6_000)
+        commit("design/R11-OFF", "design.md", "# not watched\n", 6_000)
+        hf = commit("handoff/r11-cpg", "x", "h", 7_000)
+        g("update-ref", "refs/pull/11/head", h11)
+        g("update-ref", "refs/pull/12/head", h12)
+        g("checkout", "-q", "main")
+        throwaway_git_clone(o, c, "-q")
+        led = Path(d) / "fired.log"
+        led.write_text("2026-11-15T11:30:00Z FIRED reviewer #11\n")
+        prs = [{"number": 11, "headRefOid": h11, "headRefName": "fix/r11-cpg", "reviews": []},
+               {"number": 12, "headRefOid": h12, "headRefName": "patch-1", "reviews": [
+                   {"state": "APPROVED", "submittedAt": "2026-11-15T10:00:00Z", "commit": {"oid": h12}},
+                   {"state": "APPROVED", "submittedAt": "2026-11-15T11:00:00Z", "commit": {"oid": h11}},
+                   {"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-15T12:00:00Z", "commit": {"oid": h12}}]},
+               {"number": 13, "headRefOid": h11, "headRefName": "fix/r11-off", "reviews": []}]
+        calls = []
+
+        def fake(answer):
+            def run(argv, cwd=None):
+                calls.append(argv)
+                return answer if argv[0] == "gh" else sh(argv, cwd)
+            return run
+        groups, got_prs, refs, ctime, first, rows = read_world("o/r", str(c), str(led), None, fake((0, json.dumps(prs))))
+        res["read_world: the watched set is the open critical-path and outside groups, nothing else"] = (
+            sorted(groups) == ["R11-CPG", "R11-OUT"] and groups["R11-CPG"]["tags"] == ["CP"]
+            and groups["R11-OUT"]["tags"] == ["OUTSIDE"] and groups["R11-CPG"]["topic"] == "r11-cpg")
+        res["read_world: a pull request maps by branch, else by resume.pr; an unwatched group's is dropped"] = (
+            [(p["number"], p["gid"]) for p in got_prs] == [(11, "R11-CPG"), (12, "R11-OUT")]
+            and groups["R11-OUT"]["prs"] == [12])
+        res["read_world: approval is the newest APPROVED review at the head, never at another commit"] = (
+            got_prs[1]["approved_t"] == _epoch("2026-11-15T10:00:00Z") and got_prs[0]["approved_t"] is None)
+        res["read_world: the watched groups' refs, never an unwatched group's"] = (
+            sorted(refs) == ["design/R11-OUT", "dispatch/reviewer-rev-11", "handoff/r11-cpg", "verdict/12"])
+        res["read_world: commit times from git, for every ref tip and pull-request head"] = (
+            [ctime.get(x) for x in (h11, h12, v12, r11, dz, hf)] == [2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0]
+            and [p["head_t"] for p in got_prs] == [2000.0, 3000.0])
+        res["read_world: each tip's note is read to its first line"] = (
+            first.get(v12) == f"Fix review: merge {h12}" and first.get(r11) == f"CLOUD REVIEWER seat for PR #11, at head {h11}."
+            and first.get(dz) == "# a design" and hf not in first)
+        res["read_world: the fire ledger's stamps are epochs"] = rows == [(_epoch("2026-11-15T11:30:00Z"), "2026-11-15T11:30:00Z FIRED reviewer #11")]
+        res["read_world: gh is asked for the open pull requests of the repo given"] = any(
+            a[:3] == ["gh", "pr", "list"] and "o/r" in a and "open" in a for a in calls)
+        for name, answer in (("a gh refusal", (1, "HTTP 403")), ("a non-list answer", (0, "{}"))):
+            try:
+                read_world("o/r", str(c), str(led), None, fake(answer))
+                res[f"read_world: {name} is Unreadable, never an empty list"] = False
+            except Unreadable as e:
+                res[f"read_world: {name} is Unreadable, never an empty list"] = "open pull requests" in str(e)
+        def failing(word, out=None):
+            def run(argv, cwd=None):
+                if argv[0] == "gh":
+                    return 0, json.dumps(prs)
+                if word in argv:
+                    return (0, out) if out is not None else (1, f"{word} refused")
+                return sh(argv, cwd)
+            return run
+        for word, out, why in (("ls-remote", None, "ls-remote"), ("fetch", None, "fetch"), ("log", None, "commit times"),
+                               ("log", f"{h12} 3000\n", "#11's head")):
+            try:
+                read_world("o/r", str(c), str(led), None, failing(word, out))
+                ok = False
+            except Unreadable as e:
+                ok = str(e).startswith(why)
+            res[f"read_world: a failed {word}{' missing a head' if out else ''} is Unreadable ({why})"] = ok
+        try:
+            read_world("o/r", str(c), str(led), "refs/heads/nope", fake((0, "[]")))
+            res["read_world: an unreadable roster ref is Unreadable"] = False
+        except Unreadable as e:
+            res["read_world: an unreadable roster ref is Unreadable"] = str(e).startswith("roster at refs/heads/nope")
+        g("checkout", "-q", "main", cwd=c)
+        (c / roster_lib.CRITICAL_PATH_NAME).write_text("not json")
+        g("commit", "-qam", "bad", cwd=c)
+        try:
+            read_world("o/r", str(c), str(led), "HEAD", fake((0, "[]")))
+            res["read_world: an unreadable critical-path file is Unreadable, never an empty set"] = False
+        except Unreadable as e:
+            res["read_world: an unreadable critical-path file is Unreadable, never an empty set"] = "critical path" in str(e)
+    return res
+
+
+def self_test() -> int:
+    import importlib.util
+    res = cases(sys.modules[__name__])
+    res.update(read_world_checks())
+    # the moved FIRE-OWED level and fired-ledger read, against the tick's own fixture shape
+    with tempfile.TemporaryDirectory() as d:
+        now = datetime.datetime(2026, 11, 15, 12, 0, tzinfo=datetime.timezone.utc)
+        pf = Path(d) / "payload-fix-86-r1.json"
+        pf.write_text("{}")
+        old = (now - datetime.timedelta(minutes=60)).timestamp()
+        os.utime(pf, (old, old))
+        led = Path(d) / "fired.log"
+        led.write_text("2026-11-15T11:30:00Z FIRED payload-fix-86-r1.json\nno fire here\nFIRED #3 unstamped\n")
+        rows = fired(led)
+        res["fired: FIRED lines only, stamped as UTC, an unstamped one None"] = (
+            [w and w.isoformat() for w, _ in rows] == ["2026-11-15T11:30:00+00:00", None])
+        res["fire_owed: an unfired payload past its grace owes; one a FIRED line names does not"] = (
+            len(fire_owed(d, [], now)) == 1 and fire_owed(d, rows, now) == []
+            and " rendered 60m ago" in (fire_owed(d, [], now) or [""])[0])
+        edge = (now - datetime.timedelta(minutes=FIRE_GRACE_MIN)).timestamp()
+        os.utime(pf, (edge, edge))
+        res["fire_owed: a payload exactly FIRE_GRACE_MIN old is still inside its grace"] = fire_owed(d, [], now) == []
+        res["graces are carry 4's figures, UNFIRED at FIRE_GRACE_MIN; the tick's two windows unchanged (120, 15)"] = (
+            GRACE_MIN == {"merge-no-approval": 10, "approved-unmerged": 45, "blocked-no-fire": 15, "head-no-dispatch": 25,
+                          "UNFIRED": 15, "DESIGN-REVIEW-OWED": 10, "FIXER-OWED": 10, "SEAT-SILENT": 90}
+            and (SEAT_WINDOW_MIN, FIRE_GRACE_MIN) == (120, 15))
+        edge = now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
+        on = lambda rows, age: seat_on(7, ["r11-a"], {"handoff/r11-a": "a" * 40} if age is not None else {}, rows, now,
+                                       lambda ref, sha: age, lambda sha: None)
+        res["seat_on: a fire or a ref move exactly SEAT_WINDOW_MIN old is still a seat; one minute older is not"] = (
+            on([(edge, "FIRED #7")], None) and not on([(edge - datetime.timedelta(minutes=1), "FIRED #7")], None)
+            and on([], SEAT_WINDOW_MIN) and not on([], SEAT_WINDOW_MIN + 1))
+        res["fire_names: #3 names PR 3, never PR 30; a topic matches as a whole word"] = (
+            fire_names(3, [], "FIRED #3 x") and not fire_names(3, [], "FIRED #30")
+            and fire_names(9, ["r11-a"], "FIRED fixer R11-A") and not fire_names(9, ["r11-a"], "FIRED r11-ab"))
+    import contextlib
+    import io
+    real = globals()["read_world"]
+    try:
+        for answer, rc_want, out_want in ((Unreadable("open pull requests: x"), 2, "cp-owed: UNREADABLE open pull requests: x\n"),
+                                          (_aged(_world("merge-no-approval", True)[:6]), 0, "CP-OWED merge-no-approval #11 ")):
+            def stub(*a, answer=answer):
+                if isinstance(answer, Exception):
+                    raise answer
+                return answer
+            globals()["read_world"] = stub
+            buf = io.StringIO()
+            with contextlib.redirect_stdout(buf):
+                rc = main(["cp-owed", "--fired", "/dev/null"])
+            res[f"main: cp-owed exits {rc_want} printing {out_want.split(':')[0].split(' #')[0].strip()}"] = (
+                rc == rc_want and buf.getvalue().startswith(out_want))
+        with contextlib.redirect_stderr(io.StringIO()):
+            try:
+                main(["cp-owed"])
+                res["main: cp-owed without --fired is a usage error"] = False
+            except SystemExit as e:
+                res["main: cp-owed without --fired is a usage error"] = e.code == 2
+    finally:
+        globals()["read_world"] = real
+    failed = 0
+    for name, ok in res.items():
+        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
+        failed += not ok
+    total = len(res)
+    full = Path(__file__).read_text()
+    cut = full.index(SELF_TEST_MARK)  # a site is counted and edited above the self-test only
+    src, rest = full[:cut], full[cut:]
+    with tempfile.TemporaryDirectory() as d:
+        for i, (mname, (old, new, case)) in enumerate(MUTANTS.items()):
+            total += 1
+            if src.count(old) != 1:
+                print(f"  FAIL mutant {mname}: its site appears {src.count(old)} times")
+                failed += 1
+                continue
+            p = Path(d) / f"owed_watch_m{i}.py"
+            p.write_text(src.replace(old, new) + rest)
+            spec = importlib.util.spec_from_file_location(f"owed_watch_m{i}", p)
+            m = importlib.util.module_from_spec(spec)
+            try:
+                spec.loader.exec_module(m)
+                killed = cases(m).get(case) is False
+            except Exception as e:  # a crash is no kill
+                print(f"    mutant {mname} crashed: {e.__class__.__name__}: {e}")
+                killed = False
+            print(f"  {'ok  ' if killed else 'FAIL'} mutant {mname} killed by: {case}")
+            failed += not killed
+    print(f"owed_watch self-test: {total} checks, {failed} failed")
+    return 1 if failed else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 1a9f28dbae..01ad1ea8b9 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -51,7 +51,7 @@ rendered text that no overlay value supplied.
 | `train_state` | optional: the merge train's state dir; the `cancel-sweep` row passes it as `--train-state`, so a pull request in the train's queue or spool is never cancelled for a priority run; empty leaves the flag out |
 | `gantt_roster` | the roster the beat's `gantt` row reads, as `<branch>:<path>` (fetched to `refs/gantt/roster`, never a local branch) |
 | `gantt_acks` | the Gantt acks file `sweep_gantt.py --acks` reads, one `<ISO> <KEY> act\|defer\|accept [until=<ISO>] <reason>` line per answered slip |
-| `fire_ledger` | the session's fire ledger, one line per seat fired with its leading UTC stamp, which the `gantt` and `verdict-audit` rows hand on as `--fired` (a line within 12 h holds the pull request or topic it names) |
+| `fire_ledger` | the session's fire ledger, one line per seat fired with its leading UTC stamp, which the `gantt`, `verdict-audit` and `cp-owed` rows hand on as `--fired` (a line within 12 h holds the pull request or topic it names) |
 | `sweep_record` | optional: the day's sweep record file, rendered `scorecard.py --sweep-record FILE`; whose `recycle` lines of the standing dispatch and triage seats the `scorecard` row counts as K (absent: K prints unread) |
 | `train_glob` | the glob of live train logs `verdict_audit.py --train-glob` reads (a log modified within 3 h holds its queued pull requests) |
 | `train_log` | the live merge train's `train.log` (`$HOME/.local/state/hpo/merge_train/train.log`), which the beat's `bottleneck` and `plan-beat` rows hand on as `--train-log` (the skip-share alert and the plan page's train-skips table) |
@@ -74,7 +74,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.
 
-(4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.
+(4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `cp-owed` row (`tools/audit/seat/owed_watch.py`, reading {{fire_ledger}}) prints a `CP-OWED <arm> <subject>` line for each step of a critical-path or outside group, or of its pull request, past its grace: act on each this sweep, critical path and outside first (owner directive, tvofi 2026-11-09: never let the critical path or outside pull requests slip). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.
 
 (4d) Queue priority, for the train, review, fixer and CI queues alike: a push to main; then hotfix; then accepted outside issues and contributions (a roster group with `source: outside`, which `roster_edit.py set-source` writes) together with the critical path, one rank unordered between them (owner rulings tvofi 2026-11-07, triage P420, and 2026-11-08); then production pull requests with instrument pull requests saving 12 h or more; then other instruments by savings. A group's critical-path standing is the roster's `critical` list (`tools/audit/seat/roster_lib.py` `critical_path`); hotfix and top-rank standing are `roster_lib.dispatch_rank`'s, which `tools/pr/gate_priority.py` (hotfix the lease's top band, outside and critical path the next) and the tick's OWED order apply; `open_driver.py`, the train's drain and `tools/plan/replan.py`'s `dispatch_tier` (the plan page's tier) hold the same order from `roster_lib.is_outside`.
 
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 62f0c156b1..b0ff807e49 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -235,6 +235,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/fixtures/beat_jobs/**",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
@@ -259,10 +260,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -4181,6 +4184,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -4203,10 +4207,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -4513,15 +4519,23 @@
    "git": []
   },
   "gantt-and-verdict-audit": {
-   "run_sha": "d1f9161e487c99eb5be4378579e90ac6800a56240f6f3d5a8bd71abdc277e1ae",
+   "run_sha": "16bbc5a7a78f977e26aabe9f3756fcab21ffc79c4ad03ac92f57d5a1fbfdc634",
    "files": [
+    "tools/audit/seat/owed_watch.py",
+    "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/sweep_gantt.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/verdict_audit.py"
    ],
    "probes": [
-    "."
+    ".",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat"
+   ],
+   "dirs": [
+    "tools/audit/seat"
    ],
-   "dirs": [],
    "index": false,
    "objects": false,
    "git": []
@@ -4754,6 +4768,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -4778,10 +4793,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -5262,6 +5279,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -5285,10 +5303,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -5428,6 +5448,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/coverage/.gitattributes",
@@ -5464,6 +5485,7 @@
     "tools/audit/seat/ledger.py",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/orchestrator_tick.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/pr_cap.py",
     "tools/audit/seat/proof_watch.py",
     "tools/audit/seat/record_row.py",
@@ -5556,6 +5578,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/fixtures/**",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
@@ -5580,10 +5603,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -6663,6 +6688,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -6686,10 +6712,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -6829,6 +6857,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/audit/seat/.gitattributes",
     "tools/audit/seat/hooks/.gitattributes",
@@ -8650,6 +8679,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/fixtures/beat_jobs/**",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
@@ -8675,10 +8705,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -9396,6 +9428,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -9419,10 +9452,12 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -9562,6 +9597,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/coverage/.gitattributes",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
