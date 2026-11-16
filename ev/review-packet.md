# Review packet #3645
head: a2e33e46c09fba23edaed5897351868525049da2
base: 921214bf4246338c1a83fbc5269eaa0bfe91b7d5

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133078874163 success
arch-score / arch-score id=133078860248 success
arm id=133078619866 skipped
budget-raise-gate / budget-raise-gate id=133078860090 success
cancel-superseded id=133078685654 success
codeql id=133078861590 skipped
codeql / Analyze (actions) id=133078820091 success
codeql / Analyze (javascript-typescript) id=133078820015 success
codeql / Analyze (python) id=133078820042 success
gate id=133079344854 failure
governance id=133078861739 skipped
governance / env-matrix id=133078819832 in_progress
governance / instrument-self-tests id=133078820014 in_progress
governance / policy-docs id=133078819735 success
governance / record id=133078820374 skipped
governance / wave-script id=133078819725 success
hassfest id=133078861853 skipped
hassfest / hassfest id=133078819082 success
kernel-points id=133078862231 skipped
pr-contract id=133079346322 skipped
prelude id=133078685351 success
refresh id=133078685695 success
sweep-self id=133079596988 skipped
tests id=133078862428 skipped
tests / arch-instrument id=133079127310 success
tests / briefs id=133078819461 success
tests / browser id=133079127576 in_progress
tests / closure-scope id=133078819509 success
tests / closures id=133079127320 in_progress
tests / coverage id=133079127424 in_progress
tests / fast (3.14) id=133079127321 in_progress
tests / mutation id=133078819651 success
tests / mutation-autofix id=133079105759 skipped
tests / mutation-pins id=133079105154 skipped
tests / nightly-ha id=133079128901 skipped
tests / nightly-status id=133078819667 success
tests / replay id=133079128501 skipped
tests / typing id=133079127296 success
validate id=133078861884 skipped
validate / validate-hacs id=133078819132 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 133078820014: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at a2e33e46c09fba23edaed5897351868525049da2 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item e5a63bf0: dismissed:the harness exits 0 with survived=0 at 31117b1029
NOTE body item 275f4d36: R11-PRE-TOOLCHAIN-PIN
NOTE body item cee9f2a4: R11-PRE-TOOLCHAIN-PIN
NOTE body item 635d2038: R11-PRE-TOOLCHAIN-PIN
NOTE body item 3420bc6d: dismissed:built at 31117b1029, measured in Figures
NOTE body item 577a3a38: dismissed:measured, no fixture handoff ref goes unlisted
NOTE body item 3a999745: R11-PRE-TOOLCHAIN-PIN
NOTE body item 690cba76: R11-PRE-TOOLCHAIN-PIN
NOTE body item 90b9a948: dismissed:the two bases agree again once main is merged into the head, which the train does
NOTE body item d29d6a0f: R11-PRE-TOKEN-LEDGER
CARRY-AUDIT: 10 finding item(s): 10 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/open_driver.py --self-test
             `tools/audit/seat/open_driver.py` is in the tree at this head
  ok         python3 tools/pr/cancel_superseded.py --self-test
             `tools/pr/cancel_superseded.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_open_driver_mutants.py
             `dev/audit/harnesses/r10_open_driver_mutants.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_main_cancel_mutants.py
             `dev/audit/harnesses/r11_main_cancel_mutants.py` is in the tree at this head
  ok         tests/ci_ratchet.py
             `tests/ci_ratchet.py` is in the tree at this head
  ok         python3 -I tests/ci_ratchet.py --self-test
             `tests/ci_ratchet.py` is in the tree at this head
  ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         tools/audit/seat/scorecard.py
             `tools/audit/seat/scorecard.py` is in the tree at this head
  unverified gh
             `gh` with no subcommand word to resolve
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 921214bf4246338c1a83fbc5269eaa0bfe91b7d5 --workdir <dir>
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head

FIGURES: 16 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_open_driver_mutants.py b/dev/audit/harnesses/r10_open_driver_mutants.py
index a1a18579ba..1b23a600e4 100644
--- a/dev/audit/harnesses/r10_open_driver_mutants.py
+++ b/dev/audit/harnesses/r10_open_driver_mutants.py
@@ -35,10 +35,21 @@ nothing mutated, must print failed=0. A pattern not found exactly once aborts.
                 (OPENER-LIVE-TIP, P603): the line at A no longer opens at B.
   M-moved-gone  drops the SKIP moved on an absent handoff ref: the null control
                 (a gone ref still prints SKIP moved) fails.
+  M-stale-env   every rc 1 is the environment's (P627 (iv)): a merge conflict
+                neither backs off nor counts.
+  M-stale-key   the HEAD key is dropped: a STALE CHECKOUT result is retried
+                every pass.
+  M-stale-count a STALE CHECKOUT result counts toward MAX_TRIES.
+  M-stale-unread an unreadable tools HEAD reads as a changed one.
+  M-stale-notice a NOTICE under HPO_ALLOW_STALE_TOOLS classifies as the refusal.
+  M-retry-nowrite the retry verb writes nothing (P678 (iii)).
+  M-retry-refuse  the retry verb does not refuse a topic with no entry.
+  M-retry-namesake the retry verb matches a topic by prefix: r10-cp drops r10-cp-2.
+  M-unlisted    a topic held by the cap draws no line: a board topic goes unlisted.
 
     python3 dev/audit/harnesses/r10_open_driver_mutants.py
 
-EXPECTED RESULT mutants=24
+EXPECTED RESULT mutants=33
 EXPECTED RESULT survived=0
 """
 from __future__ import annotations
@@ -98,6 +109,15 @@ PLANTS = {
     "M-reap-log": ('{reason(d / f"t-{stem(t)}.log")}', '{reason(d / f"t-{t}.log")}'),
     "M-escape": ('topic.replace("%", "%25").replace("/", "%2F")', 'topic.replace("/", "%2F")'),
     "M-maxtries": ('        elif fails.get(f"{topic} {sha}", {}).get("n", 0) >= MAX_TRIES:\n', "        elif False:\n"),
+    "M-stale-env": ("            head = stale_head(why)\n", '            head = stale_head(why) or "0" * 12\n'),
+    "M-stale-key": ('.get("stale") and (not tools or tools.startswith(fails[f"{topic} {sha}"]["stale"])):', '.get("stale") and False:'),
+    "M-stale-count": ('fails[key] = {"n": prev.get("n", 0), "next": prev.get("next", 0)', 'fails[key] = {"n": prev.get("n", 0) + 1, "next": prev.get("next", 0)'),
+    "M-stale-unread": ("and (not tools or tools.startswith(", "and (tools.startswith("),
+    "M-stale-notice": ('r"\\S+: REFUSE: STALE CHECKOUT', 'r"\\S+: (?:REFUSE|NOTICE): STALE CHECKOUT'),
+    "M-retry-nowrite": ("    p.write_text(json.dumps(fails))\n    if _load(p, None) != fails:\n", "    if False:\n"),
+    "M-retry-refuse": ("    if not keys:\n        out(f\"open_driver retry: REFUSE: {p} holds no entry", "    if False:\n        out(f\"open_driver retry: REFUSE: {p} holds no entry"),
+    "M-retry-namesake": ("if k.split()[0] == topic and k.split()[1].startswith", "if k.startswith(topic) and k.split()[1].startswith"),
+    "M-unlisted": ('            skipped[topic] = "cap"\n            log(f"SKIP {topic} {sha[:8]} cap")\n', '            skipped[topic] = "cap"\n'),
     "M-stuckowed": ('f"STUCK {t} {sha[:8]} rc=', 'f"OWED {stamp} open-refused {t} {sha[:8]} rc='),
 }
 
diff --git a/dev/audit/harnesses/r11_main_cancel_mutants.py b/dev/audit/harnesses/r11_main_cancel_mutants.py
new file mode 100644
index 0000000000..44dafcf046
--- /dev/null
+++ b/dev/audit/harnesses/r11_main_cancel_mutants.py
@@ -0,0 +1,97 @@
+#!/usr/bin/env python3
+"""R11-PRE-TOOLCHAIN-PIN carry 3 (MAIN-CANCEL-BOUNDED): each guard of the `main` arm dies alone.
+
+Each mutant is one exact one-occurrence replacement in a COPY of
+tools/pr/cancel_superseded.py (never the tree); the copy's own `--self-test`
+is then run and must FAIL. Null control: M0, nothing mutated, must print
+failed=0. A pattern not found exactly once aborts.
+
+  M-newest     the newest main run of a workflow may be cancelled.
+  M-row        the bound on a row of runs with no concluded one is dropped.
+  M-bound      the bound is four, not three.
+  M-older-side the row is not counted toward older runs.
+  M-newer-side the row is not counted toward newer runs.
+  M-planned    a cancel planned in this pass is not counted in later rows.
+  M-full       a row reaching the old end of a full listing is cancelled.
+  M-verdicts   a run that completed `skipped` counts as concluded.
+  M-event      a main run of any event is read, not only `push`.
+  M-branch     a push run on any branch is read, not only main.
+  M-dry        `--dry-run` posts the cancels.
+
+    python3 dev/audit/harnesses/r11_main_cancel_mutants.py
+
+EXPECTED RESULT mutants=11
+EXPECTED RESULT survived=0
+"""
+from __future__ import annotations
+
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = repo_root(__file__)
+TARGET = "tools/pr/cancel_superseded.py"
+PLANTS = {
+    "M-newest": ("        if i == len(rs) - 1:\n", "        if False:\n"),
+    "M-row": ("        elif hi - lo + 1 > MAIN_ROW_MAX:\n", "        elif False:\n"),
+    "M-bound": ("MAIN_ROW_MAX = 3 ", "MAIN_ROW_MAX = 4 "),
+    "M-older-side": ("        while lo > 0 and empty[lo - 1]:\n", "        while False:\n"),
+    "M-newer-side": ("        while hi < len(rs) - 1 and empty[hi + 1]:\n", "        while False:\n"),
+    "M-planned": ("            empty[i] = True\n", "            pass\n"),
+    "M-full": ("        elif lo == 0 and full:\n", "        elif False:\n"),
+    "M-verdicts": ('VERDICTS = ("success", "failure", "timed_out")', 'VERDICTS = ("success", "failure", "timed_out", "skipped")'),
+    "M-event": ('r.get("head_branch") == "main" and r.get("event") == "push"),', 'r.get("head_branch") == "main"),'),
+    "M-branch": ('r.get("head_branch") == "main" and r.get("event") == "push"),', 'r.get("event") == "push"),'),
+    "M-dry": ('            if a.dry_run:\n                print(f"cancel_superseded: would cancel {rid}")\n            else:\n'
+              "                post_cancel(api, a.repo, rid, {}, time.time())\n        print(f\"CANCEL-MAIN",
+              "            post_cancel(api, a.repo, rid, {}, time.time())\n        print(f\"CANCEL-MAIN"),
+}
+
+
+def main() -> int:
+    src = (ROOT / TARGET).read_text()
+    survived = 0
+    with tempfile.TemporaryDirectory() as tmp:
+        for name in ["M0", *PLANTS]:
+            text = src
+            if name != "M0":
+                old, new = PLANTS[name]
+                if src.count(old) != 1:
+                    print(f"ABORT {name}: pattern occurs {src.count(old)} times")
+                    return 2
+                text = src.replace(old, new)
+            copy = Path(tmp) / name / "tools" / "pr" / "cancel_superseded.py"
+            copy.parent.mkdir(parents=True)
+            copy.write_text(text)
+            r = subprocess.run([sys.executable, str(copy), "--self-test"], capture_output=True, text=True)
+            failed = sum(1 for l in r.stdout.splitlines() if l.strip().startswith("FAIL"))
+            if name == "M0":
+                print(f"RESULT mutant=M0 failed={failed} verdict={'null-ok' if r.returncode == 0 and not failed else 'NULL-RED'}")
+                if r.returncode:
+                    return 2
+                continue
+            dead = r.returncode != 0 and failed > 0
+            survived += not dead
+            print(f"RESULT mutant={name} failed={failed} verdict={'killed' if dead else 'SURVIVED'}")
+    print(f"RESULT mutants={len(PLANTS)}")
+    print(f"RESULT survived={survived}")
+    return 1 if survived else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3645.md b/dev/programme/delivery/3645.md
new file mode 100644
index 0000000000..07902e592c
--- /dev/null
+++ b/dev/programme/delivery/3645.md
@@ -0,0 +1 @@
+- [#3645](https://github.com/tvofi/heatpump_optimizer/pull/3645) — **open**, R11-PRE-TOOLCHAIN-PIN: r11 pre toolchain pin (R11-PRE-TOOLCHAIN-PIN)
diff --git a/tests/closures.json b/tests/closures.json
index 04c38a5ec2..0958b4e9d9 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4484,6 +4484,7 @@
    "dev/audit/harnesses/r10_verdict_item_barrier.py",
    "dev/audit/harnesses/r10_water_setpoint_feedback.py",
    "dev/audit/harnesses/r10_weekday_range_twins.py",
+   "dev/audit/harnesses/r11_main_cancel_mutants.py",
    "dev/audit/harnesses/r9_ci2b_closures_merge.py",
    "dev/audit/harnesses/r9_dbg2_selftest_price.py",
    "dev/audit/harnesses/r9_fr3_family_consumer.mjs",
diff --git a/tools/audit/seat/instruments/cancel_superseded.py.md b/tools/audit/seat/instruments/cancel_superseded.py.md
index 94e5711f1b..0dc3367a49 100644
--- a/tools/audit/seat/instruments/cancel_superseded.py.md
+++ b/tools/audit/seat/instruments/cancel_superseded.py.md
@@ -13,3 +13,13 @@
   `CANCEL-SWEEP: truncated`) + one commit read per open PR with something to cancel
   + one POST per cancel.
   Refusal: none; an unreadable answer cancels nothing and exits 0.
+- `cancel_superseded.py main` (`python3 -I tools/pr/cancel_superseded.py main --repo OWNER/REPO --workflow ci.yml [--dry-run]`) --
+  the one sanctioned path for cancelling superseded `push` runs on main, by hand
+  (P658); `sweep` and `run` never touch one. Per `--workflow`: cancels each active
+  main push run but the newest, oldest first, unless that would leave more than
+  three consecutive main runs of the workflow with no concluded one (completed
+  `success`, `failure` or `timed_out`). Leave a kept run to conclude.
+  Prints `CANCEL-MAIN: <workflow>: kept <id>: <why>` per refusal and one
+  `CANCEL-MAIN: <workflow>: cancelled n, kept m` line. API cost: one listing per
+  workflow + one POST per cancel. An unreadable answer cancels nothing. Exit
+  measure: `scorecard.py` line `C`. Mutants: `dev/audit/harnesses/r11_main_cancel_mutants.py`.
diff --git a/tools/audit/seat/instruments/open_driver.py.md b/tools/audit/seat/instruments/open_driver.py.md
index c87580eda6..1c616596e8 100644
--- a/tools/audit/seat/instruments/open_driver.py.md
+++ b/tools/audit/seat/instruments/open_driver.py.md
@@ -16,8 +16,14 @@
   tvofi 2026-11-07, triage P420, and 2026-11-08); an omitted topic slots by
   default class (hotfix `R10-HOTFIX-*`, outside or critical,
   `triage-*`/`roster-*`, the rest). State under `$HPO_STATE_DIR/open-driver/`: a (topic, sha) is seen only
-  on rc=0, a failed one retries after 5 min doubling to 2 h and prints `OWED
-  <utc> open-refused <topic> <sha8> rc=<n> <reason>` each pass. Prints `START`,
+  on rc=0, a failed one retries after 30 min doubling to 2 h, three runs in all,
+  and prints `OWED <utc> open-refused <topic> <sha8> rc=<n> <reason>` each pass.
+  A `REFUSE: STALE CHECKOUT <head>` result is the environment's: no backoff, no
+  count, `SKIP ... stale-checkout` until the tools checkout HEAD changes, then
+  retried on the next pass. After any other environment failure is fixed, run
+  `open_driver.py retry <topic> [<sha>]` (prints `RETRY <topic> <sha8> n= next=
+  why=`, refuses a topic with no entry); never edit `fails.json` by hand, every
+  pass loads and rewrites it. Prints `START`,
   `RESULT`, `SKIP`, `NEEDS-TITLE`, `STARVED <topic> <sha8> <h>h` (unstarted
   over 2 h). When: each tick, after the board is written. Not here yet (the
   next part of R10-OPENER-REUSE): the tick printing the OWED lines, and the
diff --git a/tools/audit/seat/open_driver.py b/tools/audit/seat/open_driver.py
index 52351648b3..eaa3e3bf92 100644
--- a/tools/audit/seat/open_driver.py
+++ b/tools/audit/seat/open_driver.py
@@ -2,6 +2,7 @@
 """The open driver: one pass opens the pull requests the tick board owes.
 
     python3 -I tools/audit/seat/open_driver.py [--board FILE] [--once]
+    python3 -I tools/audit/seat/open_driver.py retry <topic> [<sha>]
     python3 -I tools/audit/seat/open_driver.py --self-test
 
 A pass reads the board's `OWED <utc> handoff-no-pr refs/heads/handoff/<topic>
@@ -20,7 +21,7 @@ for the topic), `no-body` (no handoff-body/<topic>), `landed` (`ledger.py
 landed`, the classifier cloud_relay.sh and bus.sh orphans use), `fix-branch`
 (fix/<topic> or fix/<topic>-pr exists), `seen` (opened at this sha), `live`
 (its run is still going), `backoff` (a failed open waiting its turn), `stuck` (three
-runs failed), `cap`.
+runs failed), `stale-checkout` (refused STALE CHECKOUT at the tools HEAD still checked out), `cap`.
 
 TOPIC -> GROUP (P337 rule 3, P363), each candidate checked against the roster:
 the override in open-titles.json first; `triage-s<N>-batch<M>` -> R10-TRIAGE-S<N>
@@ -60,6 +61,20 @@ regex reads the `STUCK ` prefix). A new sha is a new key and starts fresh.
 Per-topic files are `t-<stem>.log`/`.rc`, so no topic name can equal
 `open-driver.log`; `stem` escapes `%` before `/` so two topics never share a stem.
 Log lines: START / RESULT rc=<n> / SKIP / RETIP / NEEDS-TITLE / STARVED.
+
+STALE CHECKOUT (P627) is the environment's refusal, not the branch's: `pr_args.sh`'s
+`pr_tools_fresh` line names the tools checkout HEAD it refused at. Such a result
+records that HEAD, sets no backoff and counts toward no stuck; the (topic, sha)
+is skipped `stale-checkout` while `World.tools_head` still starts with it (an
+unreadable HEAD is not a changed one) and retried on the first pass after, the
+rule merge_train.py applies to a [HOLDER] skip. Every other failure is counted.
+
+RETRY (P678): `retry <topic> [<sha>]` removes the topic's fails.json entries
+(only the (topic, sha) one when a sha or its prefix is given), prints each as
+`RETRY <topic> <sha8> n=<n> next=<utc> why=<reason>`, writes the file as a pass
+does and reads it back; a topic with no entry is refused (rc 1) and nothing is
+written. It is the cure once an environment failure is fixed, in place of a
+hand edit of fails.json, which every pass loads and rewrites.
 """
 from __future__ import annotations
 
@@ -82,6 +97,9 @@ BOARD_RE = re.compile(r"^(?:-> OWED: )?OWED \S+ handoff-no-pr refs/heads/handoff
 STARVE_S = 2 * 3600
 BACKOFF_S, BACKOFF_MAX_S, MAX_TRIES = 1800, 7200, 3
 DEFAULT_CAP = 2
+# pr_refuse's line for pr_tools_fresh (pr_args.sh), whole: `<name>: REFUSE: STALE CHECKOUT <head> behind ...`.
+# A NOTICE (HPO_ALLOW_STALE_TOOLS) or the phrase quoted inside another refusal is the branch's failure.
+STALE_RE = re.compile(r"\S+: REFUSE: STALE CHECKOUT ([0-9a-f]{12,40}) behind ")
 
 
 def state_dir() -> Path:
@@ -152,6 +170,16 @@ def backoff(n: int) -> int:
     return min(BACKOFF_S * 2 ** max(n - 1, 0), BACKOFF_MAX_S)
 
 
+def stale_head(why: str) -> str | None:
+    """The tools checkout HEAD a STALE CHECKOUT refusal names, None for any other result."""
+    m = STALE_RE.match(why)
+    return m.group(1) if m else None
+
+
+def utc(t: float) -> str:
+    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
+
+
 class World:
     """Everything a pass reads or starts outside its own state files."""
 
@@ -190,6 +218,11 @@ class World:
         return subprocess.Popen(argv, cwd=self.repo, start_new_session=True, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid
 
+    def tools_head(self) -> str:
+        """HEAD of the checkout holding open_pr.sh, the one pr_tools_fresh judges; "" when unreadable."""
+        r = subprocess.run(["git", "-C", str(self.opener.parent), "rev-parse", "HEAD"], capture_output=True, text=True)
+        return r.stdout.strip() if r.returncode == 0 else ""
+
     def alive(self, pid: int) -> bool:
         try:
             os.kill(pid, 0)
@@ -228,7 +261,7 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
     seen = set(_lines(d / "seen.txt"))
     runs = _load(d / "runs.json", {})
     fails = _load(d / "fails.json", {})
-    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
+    stamp = utc(now)
 
     def log(msg):
         out(msg)
@@ -248,8 +281,13 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
             with open(d / "seen.txt", "a") as fh:
                 fh.write(key + "\n")
         else:
-            n = fails.get(key, {}).get("n", 0) + 1
-            fails[key] = {"n": n, "next": now + backoff(n), "rc": rc, "why": reason(d / f"t-{stem(t)}.log")}
+            why, prev = reason(d / f"t-{stem(t)}.log"), fails.get(key, {})
+            head = stale_head(why)
+            if head:  # the environment's refusal: the count and any backoff stand as they were
+                fails[key] = {"n": prev.get("n", 0), "next": prev.get("next", 0), "rc": rc, "why": why, "stale": head}
+            else:
+                n = prev.get("n", 0) + 1
+                fails[key] = {"n": n, "next": now + backoff(n), "rc": rc, "why": why}
         del runs[t]
     (d / "fails.json").write_text(json.dumps(fails))
 
@@ -274,6 +312,7 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
     except ValueError:
         cap = DEFAULT_CAP
     skipped, cands, board_topics = {}, [], []
+    tools = world.tools_head() if any(f.get("stale") for f in fails.values()) else ""
     for topic, sha, ct in parse_board(board):
         def skip(why):
             skipped[topic] = why
@@ -300,6 +339,8 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
             skip("stuck")
         elif fails.get(f"{topic} {sha}", {}).get("next", 0) > now:
             skip("backoff")
+        elif fails.get(f"{topic} {sha}", {}).get("stale") and (not tools or tools.startswith(fails[f"{topic} {sha}"]["stale"])):
+            skip("stale-checkout")  # retried on the first pass after the tools HEAD changes, never before
         else:
             board_topics.append((topic, sha, ct))
             g, title = resolve(topic, groups, world.body_head(topic), titles)
@@ -328,10 +369,33 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
     return {"started": started, "skipped": skipped}
 
 
+def retry(sd: Path, topic: str, sha: str | None, out=print) -> int:
+    """Drop the topic's fails.json entries (one (topic, sha) when a sha is given). 0 removed, 1 refused."""
+    p = sd / "open-driver" / "fails.json"
+    fails = _load(p, {})
+    keys = [k for k in sorted(fails) if k.split()[0] == topic and k.split()[1].startswith(sha or "")]
+    if not keys:
+        out(f"open_driver retry: REFUSE: {p} holds no entry for {topic}{' at ' + sha if sha else ''}; nothing written")
+        return 1
+    for k in keys:
+        f = fails.pop(k)
+        out(f"RETRY {topic} {k.split()[1][:8]} n={f.get('n')} next={utc(f.get('next', 0))} why={f.get('why')}")
+    p.write_text(json.dumps(fails))
+    if _load(p, None) != fails:
+        out(f"open_driver retry: REFUSE: {p} read back differs from what was written")
+        return 1
+    return 0
+
+
 def main(argv) -> int:
     if argv[:1] == ["--self-test"]:
         import open_driver_selftest
         return open_driver_selftest.run()
+    if argv[:1] == ["retry"]:
+        if len(argv) not in (2, 3):
+            print("usage: open_driver.py retry <topic> [<sha>]", file=sys.stderr)
+            return 2
+        return retry(state_dir(), argv[1], argv[2] if len(argv) == 3 else None)
     board = None
     if "--board" in argv:
         board = argv[argv.index("--board") + 1]
diff --git a/tools/audit/seat/open_driver_selftest.py b/tools/audit/seat/open_driver_selftest.py
index 7e06d2e344..f3e0ba27ff 100644
--- a/tools/audit/seat/open_driver_selftest.py
+++ b/tools/audit/seat/open_driver_selftest.py
@@ -39,6 +39,7 @@ class Fake:
         for r in extra:
             self.t[r] = sha("c")
         self.dead, self.pid = set(), 100
+        self.head = sha("e")  # the tools checkout's HEAD (World.tools_head)
 
     def tips(self):
         return self.t
@@ -60,6 +61,9 @@ class Fake:
     def alive(self, pid):
         return pid not in self.dead
 
+    def tools_head(self):
+        return self.head
+
 
 def rd(p):
     try:
@@ -246,6 +250,21 @@ def run():
     go(sd, w, line("r10-zzz", sha("2")))
     check("NEEDS-TITLE opens nothing", w.launched == [] and any(o.startswith("NEEDS-TITLE r10-zzz") for o in out))
 
+    # every `handoff-no-pr` board topic is listed, once, each pass: SKIP, NEEDS-TITLE or START (the 2026-11-14
+    # aside: r10-arch-docs-delta drew no line). One topic per branch of the pass, the cap arm included.
+    lh = [("r10-cp", sha("1")), ("r10-inst", sha("2")), ("r10-onmain", sha("3")), ("r10-x", sha("4")), ("r10-zzz", sha("5")),
+          ("triage-s9-batch4", sha("6")), ("r10-old", sha("7")), ("r10-sav-comfort", sha("8"))]
+    lb = "\n".join(line(t, s_) for t, s_ in lh + [("r10-gone", sha("9"))])
+    sd, w = world("", heads=lh, landed={sha("3")}, extra=["refs/heads/fix/r10-x"])
+    w.t.pop("refs/heads/handoff-body/r10-old")
+    (sd / "open-cap.txt").write_text("1\n")
+    listed = lambda: sorted(o.split()[1] for o in out if o.split()[0] in ("SKIP", "NEEDS-TITLE", "START"))
+    go(sd, w, lb)
+    first = listed()
+    go(sd, w, lb, NOW + 10)
+    check("listing: each board topic draws exactly one SKIP, NEEDS-TITLE or START line, on the first pass and the next",
+          first == listed() == sorted(t for t, _ in lh + [("r10-gone", sha("9"))]) and len(w.launched) == 1)
+
     # seen only on rc=0; a failure retries with backoff and prints OWED
     d = lambda sd: sd / "open-driver"
     h1 = [("r10-cp", sha("2"))]
@@ -300,6 +319,147 @@ def run():
     go(sd, w, line("r10-cp", sha("7")), NOW + 100 * 3600 + 10)
     check("a new sha for a stuck topic launches again", len(w.launched) == 4)
 
+    # STALE CHECKOUT is the environment's refusal (P627): it records the tools checkout HEAD it was refused
+    # at, sets no backoff, counts toward no stuck, and is retried on the first pass after that HEAD changes.
+    def stale_line(w, name="open_pr"):
+        return (f"{name}: REFUSE: STALE CHECKOUT {w.head[:12]} behind origin/main {sha('9')[:12]} by 1 commit(s) "
+                "touching tools/audit/seat tools/pr: update the checkout holding /x, or set HPO_ALLOW_STALE_TOOLS=1\n")
+
+    def refuse(sd, text, topic="r10-cp"):
+        (d(sd) / f"t-{topic}.log").write_text(text)
+        (d(sd) / f"t-{topic}.rc").write_text("1\n")
+
+    key = f"r10-cp {sha('2')}"
+    sd, w = world("", heads=h1)
+    go(sd, w, b)
+    refuse(sd, stale_line(w))
+    go(sd, w, b, NOW + 10)
+    f = od._load(d(sd) / "fails.json", {}).get(key, {})
+    check("stale (i): a STALE CHECKOUT result is no failure counted and sets no backoff, and records the refused HEAD",
+          f.get("n") == 0 and f.get("next", 0) <= NOW + 10 and f.get("stale") == w.head[:12])
+    check("stale (i): with the HEAD unchanged it is not retried, in the pass that reaps it or after any wait",
+          len(w.launched) == 1 and f"SKIP r10-cp {sha('2')[:8]} stale-checkout" in out
+          and not go(sd, w, b, NOW + 100 * 3600)["started"] and len(w.launched) == 1)
+    check("stale (i): it prints OWED with the refusal, never STUCK",
+          [o.split(" ", 2)[2] for o in out if o.startswith(("OWED", "STUCK"))]
+          == [f"open-refused r10-cp {sha('2')[:8]} rc=1 {stale_line(w).strip()[:200]}"])
+    w.head = sha("f")
+    go(sd, w, b, NOW + 100 * 3600 + 1)
+    check("stale (ii): after the HEAD changes it is retried on the next pass", len(w.launched) == 2)
+    for i in range(od.MAX_TRIES + 2):  # refused again at each new HEAD: more environment refusals than MAX_TRIES
+        refuse(sd, stale_line(w))
+        go(sd, w, b, NOW + 101 * 3600 + 2 * i)
+        w.head = sha("abcdef"[i])
+        go(sd, w, b, NOW + 101 * 3600 + 2 * i + 1)
+    check("stale (i): any number of STALE CHECKOUT results never reaches stuck: each new HEAD relaunches",
+          len(w.launched) == 2 + od.MAX_TRIES + 2 and od._load(d(sd) / "fails.json", {})[key]["n"] == 0
+          and not any(o.startswith("STUCK") for o in out))
+    w.head = ""
+    refuse(sd, stale_line(type("H", (), {"head": sha("f")})))
+    go(sd, w, b, NOW + 102 * 3600)
+    k = len(w.launched)
+    go(sd, w, b, NOW + 102 * 3600 + 1)
+    check("stale: an unreadable tools HEAD is not a changed one, so nothing relaunches", len(w.launched) == k)
+    # (iii) null control: a merge conflict is the branch's rc 1 and keeps the backoff and the count
+    sd, w = world("", heads=h1)
+    go(sd, w, b)
+    refuse(sd, "open_pr: REFUSE: merging origin/main conflicts in tools/x.py\n")
+    go(sd, w, b, NOW + 10)
+    f = od._load(d(sd) / "fails.json", {}).get(key, {})
+    w.head = sha("f")
+    check("stale (iii) null: a merge-conflict rc 1 backs off 1800 s and counts toward MAX_TRIES, whatever the HEAD does",
+          f.get("n") == 1 and f.get("next") == NOW + 10 + 1800 and "stale" not in f
+          and not go(sd, w, b, NOW + 10 + 1799)["started"] and go(sd, w, b, NOW + 10 + 1801)["started"] == ["r10-cp"])
+    # a counted failure followed by the environment's refusal keeps its count and its backoff, extended by nothing
+    refuse(sd, stale_line(w))
+    go(sd, w, b, NOW + 4000)
+    f2 = od._load(d(sd) / "fails.json", {}).get(key, {})
+    check("stale: after a counted failure the count and its backoff stand unchanged",
+          f2.get("n") == 1 and f2.get("next") == f.get("next") and f2.get("stale") == w.head[:12])
+    # (v) the replay: three refusals at 13:34:54Z, the checkout rotated at 13:44:40Z, one pass a minute, cap 3
+    t0 = 1_794_404_094.0  # 2026-11-11T13:34:54Z
+    rot = t0 + 586  # 13:44:40Z
+    h3 = [("r10-hotfix-gate-redispatch-loop", sha("1")), ("r10-cp", sha("2")), ("r10-inst", sha("3"))]
+    b3 = "\n".join(line(t, s) for t, s in h3)
+    sd, w = world("", ros=roster("R10-HOTFIX-GATE-REDISPATCH-LOOP", "R10-CP", "R10-INST"), heads=h3)
+    (sd / "open-cap.txt").write_text("3\n")
+    go(sd, w, b3, t0 - 60)
+    for t, _ in h3:
+        refuse(sd, stale_line(w), t)
+    starts, now = [], t0
+    while not starts and now < t0 + 7200:
+        if now >= rot:
+            w.head = sha("f")
+        starts = go(sd, w, b3, now)["started"]
+        now += 60
+    check("stale (v) replay: the three 13:34:54Z refusals are all retried on the first pass after the 13:44:40Z HEAD change",
+          sorted(starts) == sorted(t for t, _ in h3) and rot <= now - 60 < rot + 60 and len(w.launched) == 6)
+    # the classifier over a generated spelling corpus: only pr_refuse's own line with a HEAD is the environment's
+    corpus = [(f"{nm}: {lv}: {ph} {hd}{tl}", lv == "REFUSE" and ph == "STALE CHECKOUT" and hd in (sha("a")[:12], sha("a")) and bool(tl))
+              for nm in ("open_pr", "update_pr", "pr") for lv in ("REFUSE", "NOTICE", "refuse", "Refuse")
+              for ph in ("STALE CHECKOUT", "stale checkout", "STALE-CHECKOUT", "STALE  CHECKOUT")
+              for hd in (sha("a")[:12], sha("a"), sha("a")[:7], "", "g" * 12) for tl in (" behind origin/main x by 1 commit(s)", "")]
+    wrong = [text for text, env in corpus if (od.stale_head(text) is not None) != env]
+    check(f"stale: the classifier agrees with pr_tools_fresh's line over {len(corpus)} generated spellings", len(corpus) == 480 and not wrong)
+    check("stale: a quoted refusal inside another line, and a NOTICE under HPO_ALLOW_STALE_TOOLS, are the branch's",
+          od.stale_head("open_pr: REFUSE: the body says `open_pr: REFUSE: STALE CHECKOUT " + sha("a")[:12] + " behind`") is None
+          and od.stale_head("open_pr: NOTICE: STALE CHECKOUT " + sha("a")[:12] + " behind origin/main") is None
+          and od.stale_head(stale_line(w).strip()) == w.head[:12])
+
+    # the retry verb (OPENER-RETRY-VERB, P678): the cure once an environment failure is fixed, never a hand edit
+    def backed_off():
+        sd, w = world("", heads=h1)
+        go(sd, w, b)
+        refuse(sd, "open_pr: REFUSE: prepr step 3 failed\n")
+        go(sd, w, b, NOW + 10)
+        return sd, w
+
+    sd, w = backed_off()
+    check("retry (ii) null: without the verb the pass inside the backoff window skips the topic as backoff",
+          go(sd, w, b, NOW + 600)["skipped"].get("r10-cp") == "backoff" and len(w.launched) == 1)
+    sd, w = backed_off()
+    said = []
+    rc = od.retry(sd, "r10-cp", None, said.append)
+    check("retry: prints the removed entry's n, next and why, and reads the file back without it",
+          rc == 0 and said == [f"RETRY r10-cp {sha('2')[:8]} n=1 next={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(NOW + 10 + 1800))} "
+                               "why=open_pr: REFUSE: prepr step 3 failed"]
+          and od._load(d(sd) / "fails.json", None) == {})
+    check("retry (i): the next pass starts the topic inside its backoff window",
+          go(sd, w, b, NOW + 600)["started"] == ["r10-cp"] and len(w.launched) == 2)
+    sd, w = backed_off()
+    before = (d(sd) / "fails.json").read_bytes()
+    said = []
+    check("retry (iv): a topic with no entry is refused and fails.json is byte-identical",
+          od.retry(sd, "r10-inst", None, said.append) == 1 and len(said) == 1 and said[0].startswith("open_driver retry: REFUSE: ")
+          and (d(sd) / "fails.json").read_bytes() == before
+          and od.retry(sd, "r10-cp", sha("7"), said.append) == 1 and (d(sd) / "fails.json").read_bytes() == before)
+    two = {f"r10-cp {sha('2')}": {"n": 3, "next": NOW, "rc": 1, "why": "a"}, f"r10-cp {sha('7')}": {"n": 1, "next": NOW, "rc": 1, "why": "b"},
+           f"r10-cp-2 {sha('2')}": {"n": 1, "next": NOW, "rc": 1, "why": "c"}}
+    (d(sd) / "fails.json").write_text(od.json.dumps(two))
+    check("retry: a sha names one (topic, sha) entry; no sha removes every entry of that topic and no namesake's",
+          od.retry(sd, "r10-cp", sha("7"), said.append) == 0 and sorted(od._load(d(sd) / "fails.json", {})) == [f"r10-cp {sha('2')}", f"r10-cp-2 {sha('2')}"]
+          and od.retry(sd, "r10-cp", None, said.append) == 0 and sorted(od._load(d(sd) / "fails.json", {})) == [f"r10-cp-2 {sha('2')}"])
+    (d(sd) / "fails.json").write_text(od.json.dumps(two))
+    said, real, reads = [], od._load, []
+    # a pass that loaded before the verb wrote and rewrote after it: the read-back holds the entry again
+    od._load = lambda path, default: (reads.append(path), real(path, default) if len(reads) == 1 else two)[1]
+    try:
+        rc = od.retry(sd, "r10-cp-2", None, said.append)
+    finally:
+        od._load = real
+    check("retry: a file that does not read back as what was written is refused (rc 1), naming the read-back",
+          rc == 1 and len(said) == 2 and said[0].startswith("RETRY r10-cp-2 ")
+          and said[1].startswith("open_driver retry: REFUSE: ") and "read back" in said[1])
+    with tempfile.TemporaryDirectory() as tmp:
+        env = {**os.environ, "HPO_STATE_DIR": tmp}
+        cli = lambda *a: subprocess.run([sys.executable, "-I", od.__file__, *a], capture_output=True, text=True, env=env)
+        (Path(tmp) / "open-driver").mkdir()
+        (Path(tmp) / "open-driver" / "fails.json").write_text(od.json.dumps(two))
+        r1, r2, r3 = cli("retry", "r10-cp-2"), cli("retry", "r10-cp-2"), cli("retry")
+        check("retry: the verb from the command line removes the entry (rc 0), refuses it gone (rc 1) and refuses no topic (rc 2)",
+              (r1.returncode, r2.returncode, r3.returncode) == (0, 1, 2) and r1.stdout.startswith(f"RETRY r10-cp-2 {sha('2')[:8]} n=1 ")
+              and "r10-cp-2" not in (Path(tmp) / "open-driver" / "fails.json").read_text())
+
     # a topic named like the driver's own log must not overwrite it; a plain one still works
     check("stem: a/b != a%2Fb", od.stem("a/b") != od.stem("a%2Fb"))
     with tempfile.TemporaryDirectory() as tmp:
@@ -353,6 +513,10 @@ def run():
         check("git layer: tips read handoff and main", t.get("refs/heads/handoff/side") == side and t.get("refs/heads/main") == on_main)
         check("git layer: ledger landed true for a main tip", wd.landed(on_main, on_main))
         check("git layer: ledger landed false for an unlanded tip", not wd.landed(on_main, side))
+        wd.opener = Path(tmp, "c", "open_pr.sh")
+        check("git layer: tools_head is the HEAD of the checkout holding the opener", wd.tools_head() == side)
+        wd.opener = Path(tmp, "open_pr.sh")
+        check("null: tools_head of a directory in no checkout is empty, never a guess", wd.tools_head() == "")
     # World.launch with hostile topics and a state directory holding a space
     with tempfile.TemporaryDirectory() as tmp:
         sd = Path(tmp) / "state dir"
diff --git a/tools/pr/cancel_superseded.py b/tools/pr/cancel_superseded.py
index ca3121c0f3..589f088cf3 100644
--- a/tools/pr/cancel_superseded.py
+++ b/tools/pr/cancel_superseded.py
@@ -4,6 +4,7 @@
     python3 -I tools/pr/cancel_superseded.py run --repo OWNER/REPO --workflow tests.yml \
         --pr N --head-sha SHA --branch BRANCH --run-id ID --sender LOGIN [--dry-run]
     python3 -I tools/pr/cancel_superseded.py sweep --repo OWNER/REPO [--dry-run]
+    python3 -I tools/pr/cancel_superseded.py main --repo OWNER/REPO --workflow ci.yml [--workflow ...] [--dry-run]
     python3 tools/pr/cancel_superseded.py --self-test
 
 R10-CI-CONCURRENCY. A workflow's `concurrency:` group cancels a pull request's
@@ -65,6 +66,17 @@ summary line). On, each cancel is recorded in `priority-held.json` and re-run (P
 .../rerun) once no priority run is queued; one line per cancel and per re-run naming the
 PR, the run and the priority PR that caused it.
 
+MAIN (`main --workflow W`, MAIN-CANCEL-BOUNDED, P658) is the one sanctioned path for cancelling
+superseded `push` runs on main, run by hand; `run` and `sweep` still never touch one. Per workflow
+it reads one listing of that workflow's main push runs (newest PAGE) and cancels each active run
+that is not the newest, oldest first, unless the cancel would leave more than MAIN_ROW_MAX
+consecutive main runs of that workflow with no concluded one. A run counts as concluded only when
+completed with a conclusion in VERDICTS; a run still active is not in a row, so a kept one must be
+left to conclude. A row that reaches the old end of a full listing cannot be counted and is
+refused. One `CANCEL-MAIN: <workflow>: kept <id>: <why>` line per refusal, then
+`CANCEL-MAIN: <workflow>: cancelled n, kept m`. API cost: one listing per workflow + one POST per
+cancel.
+
 `concurrency:` is unchanged and still models the bot rule (`tests/entities.py`).
 The workflow job runs the BASE's copy of this program with `actions: write`.
 """
@@ -84,6 +96,8 @@ BOT = "github-actions[bot]"
 ACTIVE = ("queued", "in_progress", "waiting", "pending", "requested")
 EVENTS = ("pull_request", "workflow_dispatch")
 PAGE, MAX_PAGES = 100, 10
+MAIN_ROW_MAX = 3  # the longest row of consecutive main runs of one workflow the `main` arm may leave with no verdict
+VERDICTS = ("success", "failure", "timed_out")  # the conclusions that say what main is
 
 
 def candidates(runs: list[dict], *, live_sha: str, branch: str, run_id: int) -> list[int]:
@@ -420,6 +434,60 @@ def sweep_plan(prs: list[dict], runs: list[dict], bot_heads: set[str], *, repo:
     return {"cancel": sorted(cancel), "kept": kept, "skipped": skipped, "ghosts": sorted(ghosts)}
 
 
+def main_plan(runs: list[dict], *, full: bool = False) -> dict:
+    """Pure part of `main`: {"cancel": ids, "refused": [(id, why)]} over ONE workflow's runs.
+
+    Only `push` runs on main are read. Every active one but the newest is superseded and is
+    cancelled, oldest first, unless it and the verdict-less completed runs around it (the cancels
+    planned here included) would make a row longer than MAIN_ROW_MAX. `full` says the listing may
+    go on past its oldest run: a row reaching that end is refused, not guessed."""
+    rs = sorted((r for r in runs if r.get("head_branch") == "main" and r.get("event") == "push"),
+                key=lambda r: int(r["id"]))
+    empty = [r.get("status") == "completed" and r.get("conclusion") not in VERDICTS for r in rs]
+    out: dict = {"cancel": [], "refused": []}
+    for i, r in enumerate(rs):
+        if r.get("status") not in ACTIVE:
+            continue
+        lo = hi = i
+        while lo > 0 and empty[lo - 1]:
+            lo -= 1
+        while hi < len(rs) - 1 and empty[hi + 1]:
+            hi += 1
+        if i == len(rs) - 1:
+            why = "it is the newest main run of its workflow"
+        elif hi - lo + 1 > MAIN_ROW_MAX:
+            why = (f"cancelling it would leave {hi - lo + 1} consecutive main runs with no concluded one "
+                   f"(the bound is {MAIN_ROW_MAX})")
+        elif lo == 0 and full:
+            why = "the listing ends inside its row of runs with no concluded one, so the row cannot be counted"
+        else:
+            empty[i] = True
+            out["cancel"].append(int(r["id"]))
+            continue
+        out["refused"].append((int(r["id"]), why))
+    return out
+
+
+def main_arm(a: argparse.Namespace, api=gh) -> int:
+    for wf in a.workflow:
+        got = api([f"repos/{a.repo}/actions/workflows/{wf}/runs", "-f", "branch=main", "-f", "event=push",
+                   "-f", f"per_page={PAGE}"])
+        runs = got.get("workflow_runs") if isinstance(got, dict) else None
+        if not isinstance(runs, list):
+            print(f"CANCEL-MAIN: {wf}: unreadable answer; cancelling nothing")
+            continue
+        p = main_plan(runs, full=len(runs) >= PAGE)
+        for rid, why in p["refused"]:
+            print(f"CANCEL-MAIN: {wf}: kept {rid}: {why}")
+        for rid in p["cancel"]:
+            if a.dry_run:
+                print(f"cancel_superseded: would cancel {rid}")
+            else:
+                post_cancel(api, a.repo, rid, {}, time.time())
+        print(f"CANCEL-MAIN: {wf}: {'would cancel' if a.dry_run else 'cancelled'} {len(p['cancel'])}, kept {len(p['refused'])}")
+    return 0
+
+
 def listing(api, path: str, query: dict, key: str | None = None) -> "tuple[list | None, bool]":
     """(items, truncated): every page up to MAX_PAGES; (None, False) when a page is unreadable."""
     out: list = []
@@ -823,6 +891,83 @@ def self_test() -> int:
         check("train pins: spool lines and queue entries are read, junk is skipped",
               train_pinned(td2), {21, 22, 23})
     check("train pins: no state dir pins nothing", train_pinned(None), set())
+
+    # --- the `main` arm (MAIN-CANCEL-BOUNDED, P658): superseded main push runs of ONE workflow, bounded.
+    def m(i, status="completed", conclusion="success", event="push", branch="main"):
+        return {"id": i, "head_branch": branch, "event": event, "status": status,
+                "conclusion": conclusion if status == "completed" else None}
+
+    def mp(runs, **kw):
+        got = main_plan(runs, **kw)
+        return got["cancel"], [i for i, _ in got["refused"]]
+
+    def row(runs, cancel):  # the longest row of consecutive runs with no verdict once `cancel` is applied
+        best = cur = 0
+        for r in sorted(runs, key=lambda r: r["id"]):
+            empty = r["id"] in cancel or (r["status"] == "completed" and r["conclusion"] not in VERDICTS)
+            cur = cur + 1 if empty else 0
+            best = max(best, cur)
+        return best
+
+    check("main: the newest main run, queued, is never cancelled", mp([m(1), m(2, "queued")]), ([], [2]))
+    check("main: the newest main run is kept though older runs are active (they are the superseded ones)",
+          mp([m(1, "in_progress"), m(2, "queued")]), ([1], [2]))
+    three = [m(1), m(2, conclusion="cancelled"), m(3, conclusion="cancelled"), m(4, conclusion="cancelled")]
+    check("main: with three cancelled in a row the fourth is refused",
+          mp(three + [m(5, "in_progress"), m(6, "queued")]), ([], [5, 6]))
+    check("main null: an older superseded run with a concluded run inside its last three is cancelled",
+          mp([m(1, conclusion="cancelled"), m(2, conclusion="failure"), m(3, conclusion="cancelled"),
+              m(4, conclusion="cancelled"), m(5, "in_progress"), m(6, "queued")]), ([5], [6]))
+    check("main: the row is counted on the newer side too",
+          mp([m(1), m(2, "in_progress")] + [m(i, conclusion="cancelled") for i in (3, 4, 5)] + [m(6, "queued")]), ([], [2, 6]))
+    seven = [m(1)] + [m(i, "in_progress") for i in range(2, 9)] + [m(9, "queued")]  # the shape after #3315: seven superseded
+    got7 = main_plan(seven)
+    check("main: of seven superseded runs every fourth is kept, so no row passes three",
+          (got7["cancel"], [i for i, _ in got7["refused"]], row(seven, set(got7["cancel"]))), ([2, 3, 4, 6, 7, 8], [5, 9], 3))
+    check("main: a second pass over the same listing, the cancels landed, cancels nothing more",
+          mp([m(1)] + [m(i, conclusion="cancelled") for i in (2, 3, 4)] + [m(5, "in_progress")]
+             + [m(i, conclusion="cancelled") for i in (6, 7, 8)] + [m(9, "queued")]), ([], [5, 9]))
+    check("main: each refusal says why",
+          [w for _, w in main_plan(three + [m(5, "in_progress"), m(6, "queued")])["refused"]],
+          ["cancelling it would leave 4 consecutive main runs with no concluded one (the bound is 3)",
+           "it is the newest main run of its workflow"])
+    check("main: a run that completed skipped, stale or with no conclusion is no verdict; success, failure and timed_out are",
+          [mp([m(1, conclusion=c), m(2, conclusion="cancelled"), m(3, conclusion="cancelled"), m(4, "in_progress"), m(5, "queued")])[0]
+           for c in ("skipped", "stale", None, "success", "failure", "timed_out")], [[], [], [], [4], [4], [4]])
+    check("main: a run of a pull request, on another branch or of a non-push event is neither cancelled nor counted",
+          mp([m(1), m(2, "in_progress", event="pull_request"), m(3, "in_progress", branch="fix/x"),
+              m(4, "in_progress", event="schedule"), m(5, "in_progress"), m(6, "queued")]), ([5], [6]))
+    check("main: a full listing that ends inside the row is refused, a short one is the whole history",
+          (mp([m(1, conclusion="cancelled"), m(2, "in_progress"), m(3, "queued")], full=True),
+           mp([m(1, conclusion="cancelled"), m(2, "in_progress"), m(3, "queued")])), (([], [2, 3]), ([2], [3])))
+    mposts, mseen = [], []
+
+    def mstub(args, method="GET", runs=seven):
+        if method == "POST":
+            mposts.append(int(args[0].split("/")[-2]))
+            return {}
+        mseen.append(args)
+        return {"workflow_runs": runs} if "/workflows/ci.yml/runs" in args[0] else None
+
+    ma = argparse.Namespace(repo=REPO, workflow=["ci.yml"], dry_run=False)
+    with contextlib.redirect_stdout(io.StringIO()) as mbuf:
+        mrc = main_arm(ma, mstub)
+    check("main end to end: one listing of the workflow's main push runs, POSTs exactly the planned cancels",
+          (mrc, mposts, mseen), (0, [2, 3, 4, 6, 7, 8],
+                                 [[f"repos/{REPO}/actions/workflows/ci.yml/runs", "-f", "branch=main", "-f", "event=push", "-f", f"per_page={PAGE}"]]))
+    check("main end to end: one kept line per refusal and one summary line",
+          [l for l in mbuf.getvalue().splitlines() if l.startswith("CANCEL-MAIN")],
+          ["CANCEL-MAIN: ci.yml: kept 5: cancelling it would leave 4 consecutive main runs with no concluded one (the bound is 3)",
+           "CANCEL-MAIN: ci.yml: kept 9: it is the newest main run of its workflow",
+           "CANCEL-MAIN: ci.yml: cancelled 6, kept 2"])
+    mposts.clear()
+    with contextlib.redirect_stdout(io.StringIO()) as mbuf:
+        main_arm(argparse.Namespace(repo=REPO, workflow=["ci.yml", "tests.yml"], dry_run=True), mstub)
+    check("main --dry-run posts nothing; an unreadable workflow listing cancels nothing and says so",
+          (mposts, "CANCEL-MAIN: tests.yml: unreadable answer; cancelling nothing" in mbuf.getvalue(),
+           mbuf.getvalue().count("cancel_superseded: would cancel ")), ([], True, 6))
+    check("null: `run` and `sweep` still never cancel a main run",
+          (plan(**{**base, "branch": "main", "runs": seven})[0], sweep_plan([], seven, set(), repo=REPO)["cancel"]), ([], []))
     print(f"cancel_superseded self-test: {n} checks, {fails} failed")
     return 1 if fails else 0
 
@@ -845,8 +990,12 @@ def main(argv: list[str]) -> int:
     w.add_argument("--priority", action="store_true",
                    help="apply the CI-priority rule (ci_priority.py): hold or cancel queued non-priority runs")
     w.add_argument("--train-state", help="the merge train's state dir: its queue and spool pin PRs")
+    mn = sub.add_parser("main")
+    mn.add_argument("--repo", required=True)
+    mn.add_argument("--workflow", action="append", required=True, help="a workflow file name, e.g. ci.yml; repeatable")
+    mn.add_argument("--dry-run", action="store_true")
     a = ap.parse_args(argv[1:])
-    return sweep(a) if a.cmd == "sweep" else run(a)
+    return {"sweep": sweep, "main": main_arm}.get(a.cmd, run)(a)
 
 
 if __name__ == "__main__":

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
