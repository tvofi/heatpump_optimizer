# Review packet #3293
head: 4b663581a88e96ce6b90223ae4b1a563de1e250f
base: 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128460956608 success
arch-score / arch-score id=128512727603 success
arm id=128454243171 skipped
budget-raise-gate / budget-raise-gate id=128512770787 success
cancel-superseded id=128512727017 success
codeql id=128470205286 skipped
codeql / Analyze (actions) id=128512754954 success
codeql / Analyze (javascript-typescript) id=128512757934 success
codeql / Analyze (python) id=128512763982 success
gate id=128520496977 success
governance id=128470165599 skipped
governance / delivery-status id=128512727344 success
governance / delivery-status-publish id=128512727313 skipped
governance / env-matrix id=128512760187 success
governance / instrument-self-tests id=128512725910 success
governance / policy-docs id=128512763151 success
governance / record id=128512727113 skipped
governance / wave-script id=128512760164 success
hassfest id=128470165785 skipped
hassfest / hassfest id=128512756631 success
kernel-points id=128512726693 skipped
pr-contract id=128470165895 skipped
pr-contract / pr-contract id=128520300802 success
prelude id=128512766665 success
refresh id=128512759135 success
tests id=128470165835 skipped
tests / arch-instrument id=128512760167 success
tests / briefs id=128512767860 success
tests / browser id=128512728091 success
tests / ci-ratchet id=128512728753 skipped
tests / claims-autofix id=128512728267 skipped
tests / closure-scope id=128512761834 success
tests / closures id=128512753269 success
tests / closures-autofix id=128512728508 skipped
tests / coverage id=128512728055 success
tests / coverage-ratchet id=128512728641 success
tests / fast (3.14) id=128512727396 success
tests / graders-head-copy id=128512728506 success
tests / lane-proofs id=128512728232 success
tests / mutation id=128512727489 success
tests / mutation-autofix id=128512728022 skipped
tests / mutation-pins id=128512727811 skipped
tests / nightly-ha id=128512727702 skipped
tests / nightly-status id=128512726111 success
tests / replay id=128512728035 skipped
tests / typing id=128512754224 success
validate id=128470206113 skipped
validate / validate-hacs id=128512752005 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item 195beea5: R10-HANDOFF-PATH
NOTE body item c9f45e05: R10-HANDOFF-PATH
NOTE body item 86ddb31f: R10-HANDOFF-PATH
NOTE body item da830f63: R10-HANDOFF-PATH
NOTE body item a7a31149: R10-HANDOFF-PATH
NOTE body item 7656755f: R10-HANDOFF-PATH
NOTE body item b85a01f9: R10-HANDOFF-PATH
NOTE body item a09788c8: R10-HANDOFF-PATH
NOTE body item e0404ef9: R10-HANDOFF-PATH
NOTE body item b1532434: R10-HANDOFF-PATH
NOTE body item 568f99c3: R10-HANDOFF-PATH
NOTE body item c406c470: R10-HANDOFF-PATH
NOTE body item 9f797c16: R10-HANDOFF-PATH
NOTE body item cf1fc31d: R10-HANDOFF-PATH
NOTE body item 370104d0: R10-HANDOFF-PATH
NOTE body item e0e2b6f9: R10-HANDOFF-PATH
NOTE body item 5e91c904: R10-HANDOFF-PATH
NOTE body item 768d41f1: R10-HANDOFF-PATH
NOTE body item 03290508: R10-HANDOFF-PATH
NOTE body item 8f2763d6: R10-HANDOFF-PATH
CARRY-AUDIT: 20 finding item(s): 20 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/pr_args.sh --self-test
             `tools/audit/seat/pr_args.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/open_driver.py --self-test
             `tools/audit/seat/open_driver.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_open_driver_mutants.py b/dev/audit/harnesses/r10_open_driver_mutants.py
index 08e314daa..205ba633e 100644
--- a/dev/audit/harnesses/r10_open_driver_mutants.py
+++ b/dev/audit/harnesses/r10_open_driver_mutants.py
@@ -17,12 +17,15 @@ nothing mutated, must print failed=0. A pattern not found exactly once aborts.
   M-backoff  a failed open is retried every pass.
   M-live     a topic whose run is still alive launches again.
   M-launch   World.launch pastes the topic and state directory into bash -c text.
-  M-bo-base  the backoff base 300 s -> 600 s.
+  M-bo-base  the backoff base 1800 s -> 600 s.
   M-bo-max   the backoff cap 7200 s -> 14400 s.
   M-head4    body_head reads four lines, not three.
   M-headall  body_head reads the whole body.
   M-first    parse_board lets a later line for a topic win.
   M-triageB  the R10-TRIAGE-B<M> fallback is dropped.
+  M-escape   stem() no longer escapes % before /: `a%2Fb` and `a/b` share a file.
+  M-maxtries the MAX_TRIES stop is dropped: a failing open is retried forever.
+  M-stuckowed a stuck (topic, sha) prints OWED, not STUCK.
   M-open-stem   World.launch names the .rc by the raw topic: a slash topic's
                 result file is never written (the open side).
   M-reap-stem   run_pass reads the raw topic's .rc: a slash topic's result is
@@ -31,7 +34,7 @@ nothing mutated, must print failed=0. A pattern not found exactly once aborts.
 
     python3 dev/audit/harnesses/r10_open_driver_mutants.py
 
-EXPECTED RESULT mutants=19
+EXPECTED RESULT mutants=22
 EXPECTED RESULT survived=0
 """
 from __future__ import annotations
@@ -70,20 +73,23 @@ PLANTS = {
     "M-live": ("        elif topic in runs:\n", "        elif False:\n"),
     "M-launch": (
         """        cmd = 'o=$0; l=$1; r=$2; shift 2; bash "$o" "$@" > "$l" 2>&1; echo $? > "$r"'
-        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"{stem(topic)}.log"), str(rc), topic, sha, title, group]
+        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"t-{stem(topic)}.log"), str(rc), topic, sha, title, group]
 """,
-        """        cmd = f'bash {self.opener} "$@" > {d}/{topic}.log 2>&1; echo $? > {d}/{topic}.rc'
+        """        cmd = f'bash {self.opener} "$@" > {d}/t-{topic}.log 2>&1; echo $? > {d}/t-{topic}.rc'
         argv = ["bash", "-c", cmd, "_", topic, sha, title, group]
 """),
-    "M-bo-base": ("BACKOFF_S, BACKOFF_MAX_S = 300, 7200", "BACKOFF_S, BACKOFF_MAX_S = 600, 7200"),
-    "M-bo-max": ("BACKOFF_S, BACKOFF_MAX_S = 300, 7200", "BACKOFF_S, BACKOFF_MAX_S = 300, 14400"),
+    "M-bo-base": ("BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 7200, 3", "BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 600, 7200, 3"),
+    "M-bo-max": ("BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 7200, 3", "BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 14400, 3"),
     "M-head4": ("splitlines()[:3]", "splitlines()[:4]"),
     "M-headall": ('"\\n".join(r.stdout.splitlines()[:3])', "r.stdout"),
     "M-first": ("        if m and m.group(1) not in seen:\n", "        if m:\n"),
     "M-triageB": ('for g in (f"R10-TRIAGE-S{m.group(1)}", f"R10-TRIAGE-B{m.group(2)}"):', 'for g in (f"R10-TRIAGE-S{m.group(1)}",):'),
-    "M-open-stem": ('        rc = d / f"{stem(topic)}.rc"\n', '        rc = d / f"{topic}.rc"\n'),
-    "M-reap-stem": ('        rcf = d / f"{stem(t)}.rc"\n', '        rcf = d / f"{t}.rc"\n'),
-    "M-reap-log": ("reason(d / (stem(t) + '.log'))", "reason(d / (t + '.log'))"),
+    "M-open-stem": ('        rc = d / f"t-{stem(topic)}.rc"\n', '        rc = d / f"t-{topic}.rc"\n'),
+    "M-reap-stem": ('        rcf = d / f"t-{stem(t)}.rc"\n', '        rcf = d / f"t-{t}.rc"\n'),
+    "M-reap-log": ('{reason(d / f"t-{stem(t)}.log")}', '{reason(d / f"t-{t}.log")}'),
+    "M-escape": ('topic.replace("%", "%25").replace("/", "%2F")', 'topic.replace("/", "%2F")'),
+    "M-maxtries": ('        elif fails.get(f"{topic} {sha}", {}).get("n", 0) >= MAX_TRIES:\n', "        elif False:\n"),
+    "M-stuckowed": ('f"STUCK {t} {sha[:8]} rc=', 'f"OWED {stamp} open-refused {t} {sha[:8]} rc='),
 }
 
 
diff --git a/dev/programme/delivery/3293.md b/dev/programme/delivery/3293.md
new file mode 100644
index 000000000..445706c1d
--- /dev/null
+++ b/dev/programme/delivery/3293.md
@@ -0,0 +1 @@
+- [#3293](https://github.com/tvofi/heatpump_optimizer/pull/3293) — **open**, R10-HANDOFF-PATH: handoff path, part 2 (R10-HANDOFF-PATH)
diff --git a/tools/audit/seat/open_driver.py b/tools/audit/seat/open_driver.py
index 1e8e4508f..597b74b05 100644
--- a/tools/audit/seat/open_driver.py
+++ b/tools/audit/seat/open_driver.py
@@ -14,7 +14,8 @@ SKIPPED (`SKIP <topic> <sha8> <reason>`): `moved` (origin's handoff tip is not
 the board's sha), `no-body` (no handoff-body/<topic>), `landed` (`ledger.py
 landed`, the classifier cloud_relay.sh and bus.sh orphans use), `fix-branch`
 (fix/<topic> or fix/<topic>-pr exists), `seen` (opened at this sha), `live`
-(its run is still going), `backoff` (a failed open waiting its turn), `cap`.
+(its run is still going), `backoff` (a failed open waiting its turn), `stuck` (three
+runs failed), `cap`.
 
 TOPIC -> GROUP (P337 rule 3, P363), each candidate checked against the roster:
 the override in open-titles.json first; `triage-s<N>-batch<M>` -> R10-TRIAGE-S<N>
@@ -39,9 +40,17 @@ A board topic unstarted for more than 2 h prints `STARVED <topic> <sha8> <h>h`
 RUNS (P337 rule 4, carry 4): a run is `bash open_pr.sh` in its own session; its
 PID and result file live in `$HPO_STATE_DIR/open-driver/`, and live runs are
 counted from those PIDs alone. A (topic, sha) is marked seen ONLY on rc=0; a
-failed one is retried with backoff (5 min doubling to 2 h) and prints
-`OWED <utc> open-refused <topic> <sha8> rc=<n> <reason>` every pass until it
-opens. Log lines: START / RESULT rc=<n> / SKIP / NEEDS-TITLE / STARVED.
+failed one is retried with backoff 30 min, then 60 min (doubling, capped at 2 h),
+for THREE runs in all. The standing-contracts design's 30 min replaced the old
+5-minute start: three fast retries of a content refusal only repeat it. While
+fewer than three runs have failed every pass prints
+`OWED <utc> open-refused <topic> <sha8> rc=<n> <reason>`; after the third the
+(topic, sha) is `stuck`, never relaunched, and every pass prints exactly one
+`STUCK <topic> <sha8> rc=<n> <reason>` line instead (beat_jobs.py's OPENER
+regex reads the `STUCK ` prefix). A new sha is a new key and starts fresh.
+Per-topic files are `t-<stem>.log`/`.rc`, so no topic name can equal
+`open-driver.log`; `stem` escapes `%` before `/` so two topics never share a stem.
+Log lines: START / RESULT rc=<n> / SKIP / NEEDS-TITLE / STARVED.
 """
 from __future__ import annotations
 
@@ -60,7 +69,7 @@ import roster_lib  # noqa: E402
 REPO = "tvofi/heatpump_optimizer"
 BOARD_RE = re.compile(r"^OWED \S+ handoff-no-pr refs/heads/handoff/(\S+) ([0-9a-f]{40})(?: ct=(\d+|\?))?")
 STARVE_S = 2 * 3600
-BACKOFF_S, BACKOFF_MAX_S = 300, 7200
+BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 7200, 3
 DEFAULT_CAP = 2
 
 
@@ -133,7 +142,7 @@ def order(items, priority: list, critical) -> list:
 
 def stem(topic: str) -> str:
     """The topic as one file name: a ref may hold a slash, a file name may not."""
-    return topic.replace("/", "%2F")
+    return topic.replace("%", "%25").replace("/", "%2F")
 
 
 def backoff(n: int) -> int:
@@ -170,11 +179,11 @@ class World:
 
     def launch(self, topic, sha, title, group) -> int:
         d = self.sd / "open-driver"
-        rc = d / f"{stem(topic)}.rc"
+        rc = d / f"t-{stem(topic)}.rc"
         rc.unlink(missing_ok=True)
         # Paths and the topic travel as arguments, never as shell text: a ref name may hold `$(...)`.
         cmd = 'o=$0; l=$1; r=$2; shift 2; bash "$o" "$@" > "$l" 2>&1; echo $? > "$r"'
-        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"{stem(topic)}.log"), str(rc), topic, sha, title, group]
+        argv = ["bash", "-c", cmd, str(self.opener), str(d / f"t-{stem(topic)}.log"), str(rc), topic, sha, title, group]
         return subprocess.Popen(argv, cwd=self.repo, start_new_session=True, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid
 
@@ -224,12 +233,12 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
             fh.write(f"{stamp} {msg}\n")
 
     for t, r in list(runs.items()):  # reap: a result file settles a run; a vanished PID without one is a kill
-        rcf = d / f"{stem(t)}.rc"
+        rcf = d / f"t-{stem(t)}.rc"
         rc = int(rcf.read_text().strip() or -1) if rcf.exists() else (None if world.alive(r["pid"]) else -1)
         if rc is None:
             continue
         key = f"{t} {r['sha']}"
-        log(f"RESULT {t} {r['sha'][:8]} rc={rc} {reason(d / (stem(t) + '.log'))}")
+        log(f"RESULT {t} {r['sha'][:8]} rc={rc} {reason(d / f"t-{stem(t)}.log")}")
         if rc == 0:
             seen.add(key)
             fails.pop(key, None)
@@ -237,13 +246,16 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
                 fh.write(key + "\n")
         else:
             n = fails.get(key, {}).get("n", 0) + 1
-            fails[key] = {"n": n, "next": now + backoff(n), "rc": rc, "why": reason(d / (stem(t) + ".log"))}
+            fails[key] = {"n": n, "next": now + backoff(n), "rc": rc, "why": reason(d / f"t-{stem(t)}.log")}
         del runs[t]
     (d / "fails.json").write_text(json.dumps(fails))
 
     for key, f in sorted(fails.items()):
         t, sha = key.split()
-        out(f"OWED {stamp} open-refused {t} {sha[:8]} rc={f['rc']} {f['why']}")
+        if f["n"] >= MAX_TRIES:
+            out(f"STUCK {t} {sha[:8]} rc={f['rc']} {f['why']}")
+        else:
+            out(f"OWED {stamp} open-refused {t} {sha[:8]} rc={f['rc']} {f['why']}")
 
     tips = world.tips()
     main = tips.get("refs/heads/main", "")
@@ -273,6 +285,8 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
             skip("fix-branch")
         elif topic in runs:
             skip("live")
+        elif fails.get(f"{topic} {sha}", {}).get("n", 0) >= MAX_TRIES:
+            skip("stuck")
         elif fails.get(f"{topic} {sha}", {}).get("next", 0) > now:
             skip("backoff")
         else:
diff --git a/tools/audit/seat/open_driver_selftest.py b/tools/audit/seat/open_driver_selftest.py
index 5314f777f..f921577e9 100644
--- a/tools/audit/seat/open_driver_selftest.py
+++ b/tools/audit/seat/open_driver_selftest.py
@@ -61,6 +61,13 @@ class Fake:
         return pid not in self.dead
 
 
+def rd(p):
+    try:
+        return p.read_text()
+    except OSError:
+        return None
+
+
 def line(topic, s, ct=None):
     return f"OWED 2026-11-02T00:00:00Z handoff-no-pr refs/heads/handoff/{topic} {s}" + (f" ct={int(ct)}" if ct else "")
 
@@ -159,20 +166,20 @@ def run():
     sd, w = world("", heads=h1)
     b = line("r10-cp", sha("2"))
     go(sd, w, b)
-    (d(sd) / "r10-cp.rc").write_text("1\n")
-    (d(sd) / "r10-cp.log").write_text("open_pr: REFUSE: the body lints red\n")
+    (d(sd) / "t-r10-cp.rc").write_text("1\n")
+    (d(sd) / "t-r10-cp.log").write_text("open_pr: REFUSE: the body lints red\n")
     go(sd, w, b, NOW + 10)
     check("failed open not marked seen", not (d(sd) / "seen.txt").exists() and len(w.launched) == 1)
     check("failed open prints OWED with reason", any(o.startswith("OWED") and "open-refused r10-cp" in o and "REFUSE" in o for o in out))
     check("backoff holds the retry", len(w.launched) == 1)
     go(sd, w, b, NOW + 10 + od.BACKOFF_S + 1)
     check("retry after backoff", len(w.launched) == 2)
-    (d(sd) / "r10-cp.rc").write_text("1\n")
+    (d(sd) / "t-r10-cp.rc").write_text("1\n")
     go(sd, w, b, NOW + 5000)
-    check("backoff schedule: 5 min, doubling, 2 h cap", [od.backoff(1), od.backoff(2), od.backoff(6), od.backoff(7)] == [300, 600, 7200, 7200])
+    check("backoff schedule: 30 min, 60 min, 2 h cap", [od.backoff(1), od.backoff(2), od.backoff(3), od.backoff(7)] == [1800, 3600, 7200, 7200])
     check("backoff doubles", od.backoff(2) == 2 * od.backoff(1) and od.backoff(99) == od.BACKOFF_MAX_S)
     go(sd, w, b, NOW + 5000 + 3 * 3600)
-    (d(sd) / "r10-cp.rc").write_text("0\n")
+    (d(sd) / "t-r10-cp.rc").write_text("0\n")
     go(sd, w, b, NOW + 5000 + 4 * 3600)
     check("rc=0 marks seen", f"r10-cp {sha('2')}" in (d(sd) / "seen.txt").read_text())
     k = len(w.launched)
@@ -181,10 +188,51 @@ def run():
     sd, w = world("", heads=h1)
     go(sd, w, b)
     w.dead.add(w.pid)
-    (d(sd) / "r10-cp.rc").unlink(missing_ok=True)
+    (d(sd) / "t-r10-cp.rc").unlink(missing_ok=True)
     go(sd, w, b, NOW + 1)
     check("a killed run (no result, no PID) is a failure", any("open-refused r10-cp" in o and "rc=-1" in o for o in out))
 
+    # three failed runs end the retries: STUCK once per pass, nothing relaunches; a new sha starts fresh
+    sd, w = world("", heads=h1)
+    go(sd, w, b)
+    (d(sd) / "t-r10-cp.log").write_text("open_pr: REFUSE: the body lints red\n")
+    (d(sd) / "t-r10-cp.rc").write_text("1\n")
+    go(sd, w, b, NOW + 10)
+    go(sd, w, b, NOW + 2000)
+    (d(sd) / "t-r10-cp.rc").write_text("1\n")
+    go(sd, w, b, NOW + 2100)
+    check("two failures print OWED, not STUCK", any(o.startswith("OWED") for o in out) and not any(o.startswith("STUCK") for o in out))
+    go(sd, w, b, NOW + 6000)
+    (d(sd) / "t-r10-cp.rc").write_text("1\n")
+    go(sd, w, b, NOW + 6100)
+    check("third failure prints exactly one STUCK line, no OWED",
+          [o for o in out if o.startswith(("STUCK", "OWED"))] == [f"STUCK r10-cp {sha('2')[:8]} rc=1 open_pr: REFUSE: the body lints red"])
+    go(sd, w, b, NOW + 100 * 3600)
+    check("stuck: no relaunch after a long time, STUCK again",
+          len(w.launched) == 3 and sum(o.startswith("STUCK r10-cp ") for o in out) == 1 and not any(o.startswith("OWED") for o in out))
+    w.t["refs/heads/handoff/r10-cp"] = sha("7")
+    go(sd, w, line("r10-cp", sha("7")), NOW + 100 * 3600 + 10)
+    check("a new sha for a stuck topic launches again", len(w.launched) == 4)
+
+    # a topic named like the driver's own log must not overwrite it; a plain one still works
+    check("stem: a/b != a%2Fb", od.stem("a/b") != od.stem("a%2Fb"))
+    with tempfile.TemporaryDirectory() as tmp:
+        sd = Path(tmp) / "sd"
+        (sd / "open-driver").mkdir(parents=True)
+        (sd / "open-driver" / "open-driver.log").write_text("driver\n")
+        wl = od.World(tmp, sd)
+        wl.opener = Path(tmp) / "o.sh"
+        wl.opener.write_text("echo topic-ran\n")
+        for topic in ("open-driver", "r10-plain"):
+            rcf = sd / "open-driver" / f"t-{od.stem(topic)}.rc"
+            wl.launch(topic, sha("1"), "T", "G")
+            for _ in range(100):
+                if rcf.exists() and rcf.read_text().strip():
+                    break
+                time.sleep(0.1)
+            check(f"topic {topic!r} launches into its own t- files", rd(sd / "open-driver" / f"t-{od.stem(topic)}.log") == "topic-ran\n")
+        check("open-driver.log not overwritten by topic 'open-driver'", rd(sd / "open-driver" / "open-driver.log") == "driver\n")
+
     # a second pass with the first run still alive must not launch again
     sd, w = world("", heads=h1)
     go(sd, w, b)
@@ -235,14 +283,14 @@ def run():
             argsf.unlink(missing_ok=True)
             os.environ["HPO_ARGS_OUT"] = str(argsf)
             wl.launch(topic, sha("1"), "T x", "G")
-            rcf = sd / "open-driver" / f"{od.stem(topic)}.rc"
+            rcf = sd / "open-driver" / f"t-{od.stem(topic)}.rc"
             for _ in range(100):
                 if rcf.exists() and rcf.read_text().strip():
                     break
                 time.sleep(0.1)
             check(f"launch {topic!r}: rc file written with 0", rcf.exists() and rcf.read_text().strip() == "0")
             check(f"launch {topic!r}: topic arrives as one argument", argsf.exists() and argsf.read_text() == f"{topic}|{sha('1')}|T x|G|")
-            check(f"launch {topic!r}: log written", (sd / "open-driver" / f"{od.stem(topic)}.log").read_text() == "ran\n")
+            check(f"launch {topic!r}: log written", rd(sd / "open-driver" / f"t-{od.stem(topic)}.log") == "ran\n")
         check("launch: no topic executed as shell code", not marker.exists() and not list(Path(tmp).rglob("INJECTED")))
 
     # a slash topic end to end: run_pass launches it through the real World.launch, a later pass reaps its result
@@ -266,7 +314,7 @@ def run():
         ws = Slash(wr, roster("A/B"), heads=[("a/b", sha("4"))])
         b = line("a/b", sha("4"))
         go(sd, ws, b)
-        rcf = sd / "open-driver" / f"{od.stem('a/b')}.rc"
+        rcf = sd / "open-driver" / f"t-{od.stem('a/b')}.rc"
         for _ in range(100):
             if rcf.exists() and rcf.read_text().strip():
                 break
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 164eea228..bb6e4b756 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -166,9 +166,10 @@ pr_kept() { printf '%s: KEPT %s on %s: %s\n' "${PR_NAME:-pr}" "$1" "$2" "$3" >&2
 # HPO_ALLOW_STALE_TOOLS=1 names the staleness and goes on.
 # Top-relative (`:/`): git runs in the tools' own directory, where a bare path would be read below it.
 PR_FRESH_PATHS=(:/tools/audit/seat :/tools/pr)  # mut:freshpaths
+# This file's own directory, absolute, fixed once at source time. A caller that sourced it by a relative path and then changed directory (update_pr.sh and open_pr.sh `cd "$M"`) would otherwise resolve the relative BASH_SOURCE against the new directory and measure the main checkout, not the one holding these tools: a false STALE CHECKOUT (P362, P401). Every reader uses this, never BASH_SOURCE at call time.
+PR_ARGS_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)  # mut:argsdir
 pr_tools_fresh() { # after `git fetch origin main`: refuse when this file's checkout is behind it in PR_FRESH_PATHS
-  local d n h o why
-  d=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
+  local d=${PR_ARGS_DIR:-} n h o why
   h=$(git -C "$d" rev-parse --short=12 HEAD 2>/dev/null) && o=$(git -C "$d" rev-parse --short=12 origin/main 2>/dev/null) \
     && n=$(git -C "$d" rev-list --count HEAD..origin/main -- ${PR_FRESH_PATHS[@]+"${PR_FRESH_PATHS[@]}"} 2>/dev/null) \
     || pr_refuse "could not count what origin/main adds over the checkout holding $d"
@@ -372,7 +373,7 @@ tools/pr/prepr.sh mention: comments; it honours the receipt app_push.sh --reuse
 tools/pr/app_mint.sh mention: comments; sourced by app_push.sh, it launches nothing
 tools/policy/policy_lint.mjs mention: a refusal message'
 pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any OPEN
-  local root=${1:-$(cd "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)} rev=${2:-} f kind txt bad=0
+  local root=${1:-$(cd "$PR_ARGS_DIR/../../.." && pwd)} rev=${2:-} f kind txt bad=0
   local found
   if [ -n "$rev" ]; then
     found=$(git -C "$root" grep -lE "$PR_PUSHER_RULE" "$rev" -- 'tools/*.sh' 'tools/*.py' 'tools/*.mjs' 'tools/*.js' | sed "s|^$rev:||")
@@ -421,7 +422,7 @@ pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any
 # fails closed without it, so its reap arms never reached a push (#2668's CI).
 pr_args_self_test() (
   local src t f=0 n=0 o m base code side body i reapsha UNREL
-  src=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
+  src=$PR_ARGS_DIR
   t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
   # The pusher stubs the reap arms drive read this directory ($T is open_pr's topic).
   REAP_DIR=$t; export REAP_DIR
@@ -621,6 +622,36 @@ STUB
   cp "$t/body.md" "$t/b.md"; fresh - tools/pr/zz update_pr.sh fix/x - "$t/b.md"
   [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: STALE CHECKOUT" "$t/out" && ! grep -qF "the push failed" "$t/out"
   ck "update_pr: tools behind origin/main under tools/pr refuse too" $?
+  # P362/P401: the directory is fixed at source time. (A) a fresh clone sourced by a relative path, then a cd into a stale sibling checkout, passes; (B, null control) the same clone made stale still refuses; (C) update_pr.sh run by a relative path from a fresh worktree whose common checkout is behind origin/main passes the check, where call-time resolution measured that common checkout.
+  mkdir -p "$o/tools/audit/seat" && printf 's\n' > "$o/tools/audit/seat/zzr" && git -C "$o" add tools/audit/seat/zzr && git -C "$o" commit -q -m "main: zzr"
+  throwaway_git_clone -q "$o" "$t/fr" && throwaway_git_clone -q "$o" "$t/st" && git -C "$t/st" reset -q --hard "$base"
+  git -C "$o" reset -q --hard "$base"
+  relsrc() { # <mutant|-> <fresh clone> <sibling>: source by a relative path, cd to the sibling, ask
+    mkdir -p "$2/tools/audit/seat"
+    if [ "$1" = - ]; then cp "$src/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
+    else grep -v "# mut:$1\$" "$src/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
+    ( unset PR_ARGS_DIR; cd "$2" && . ./tools/audit/seat/pr_args.sh && cd "$3" && PR_NAME=fresh pr_tools_fresh ) > "$t/out" 2>&1
+  }
+  relsrc - "$t/fr" "$t/st"; ck "pr_args: sourced by a relative path from a fresh clone, then cd'd into a stale sibling, passes" $?
+  ! relsrc argsdir "$t/fr" "$t/st"
+  ck "  mutant mut:argsdir (its line deleted): call-time resolution reads the sibling and refuses" $?
+  git -C "$t/fr" reset -q --hard "$base"
+  ! relsrc - "$t/fr" "$t/st" && grep -qF "STALE CHECKOUT" "$t/out"
+  ck "null control: the same clone made stale refuses STALE CHECKOUT" $?
+  mkdir -p "$o/tools/audit/seat" && printf 's\n' > "$o/tools/audit/seat/zzw" && git -C "$o" add tools/audit/seat/zzw && git -C "$o" commit -q -m "main: zzw"
+  git -C "$m" fetch -q origin main; rm -rf "$t/wtf"; git -C "$m" worktree prune
+  git -C "$m" worktree add -q --detach "$t/wtf" origin/main
+  relupd() { # <mutant|->: update_pr.sh by a relative path from the fresh worktree; the common checkout $m is behind
+    copyin "$1"; mkdir -p "$t/wtf/tools/audit/seat" "$t/wtf/tools/pr"
+    cp "$m"/tools/audit/seat/*.sh "$m"/tools/audit/seat/*.py "$t/wtf/tools/audit/seat/"; cp "$m/tools/pr/head_note.py" "$t/wtf/tools/pr/"
+    i=$((i + 1)); ( cd "$t/wtf" && HPO_STATE_DIR=$t/s$i BR=fix/x-$i BR_FIXED=1 bash tools/audit/seat/update_pr.sh fix/x - "$t/b.md" ) > "$t/out" 2>&1
+  }
+  cp "$t/body.md" "$t/b.md"
+  relupd -; ! grep -qF "STALE CHECKOUT" "$t/out"
+  ck "update_pr: run by a relative path from a fresh worktree, the common checkout behind origin/main, passes the freshness check" $?
+  relupd argsdir; grep -qF "STALE CHECKOUT" "$t/out"
+  ck "  mutant mut:argsdir (its line deleted): the common checkout is measured and refuses" $?
+  git -C "$m" worktree remove --force "$t/wtf"; git -C "$o" reset -q --hard "$base"; git -C "$m" fetch -q origin main
   # ---- a stopped pusher reaps its whole descendant tree (R10-PUSHER-REAP) ----
   # The stub app_push above leaves a two-level sleep tree recorded by pid, so
   # each arm counts what is still alive after the signal. The bystander sleeper

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
