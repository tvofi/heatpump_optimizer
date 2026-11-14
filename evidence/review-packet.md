# Review packet #3584
head: b17c78773410c7e1d77dcbbe39e8c817edf87454
base: f7e7a0244a3d5f7763c4ec15d193d03ef4bb3274

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132394766721 success
arch-score / arch-score id=132394744384 success
arm id=132394588517 skipped
budget-raise-gate / budget-raise-gate id=132394744288 success
cancel-superseded id=132394554386 success
codeql id=132394745720 skipped
codeql / Analyze (actions) id=132394716872 success
codeql / Analyze (javascript-typescript) id=132394716855 success
codeql / Analyze (python) id=132394716901 success
gate id=132395182125 queued
governance id=132394745757 skipped
governance / delivery-status id=132394716950 success
governance / delivery-status-publish id=132394718288 skipped
governance / env-matrix id=132394717000 in_progress
governance / instrument-self-tests id=132394716953 in_progress
governance / policy-docs id=132394716877 success
governance / record id=132394717956 skipped
governance / wave-script id=132394716859 success
hassfest id=132394745551 skipped
hassfest / hassfest id=132394716886 success
kernel-points id=132394745130 skipped
pr-contract id=132395183312 skipped
prelude id=132394554364 success
refresh id=132394554095 success
tests id=132394745724 skipped
tests / arch-instrument id=132395150516 queued
tests / briefs id=132394716905 success
tests / browser id=132395150359 in_progress
tests / closure-scope id=132394716965 success
tests / closures id=132395150350 queued
tests / coverage id=132395150377 in_progress
tests / fast (3.14) id=132395150351 queued
tests / mutation id=132394716930 success
tests / mutation-autofix id=132394964422 skipped
tests / mutation-pins id=132394964413 skipped
tests / nightly-ha id=132395151569 skipped
tests / nightly-status id=132394716951 failure
tests / replay id=132395151504 skipped
tests / typing id=132395150380 queued
validate id=132394745748 skipped
validate / validate-hacs id=132394716945 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132394716953: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 2e903859: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/ci/sweep.py --self-test
             `tools/ci/sweep.py` is in the tree at this head
  ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_rca_sweep_settle_loop.py replay
             `dev/audit/harnesses/r10_rca_sweep_settle_loop.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay
             `dev/audit/harnesses/r10_gate_busy_defer_3.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_sweep_driver_arm.py
             `dev/audit/harnesses/r10_sweep_driver_arm.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3584.md b/dev/programme/delivery/3584.md
new file mode 100644
index 0000000000..93245fff6f
--- /dev/null
+++ b/dev/programme/delivery/3584.md
@@ -0,0 +1 @@
+- [#3584](https://github.com/tvofi/heatpump_optimizer/pull/3584) — **open**, Hotfix: sweep reads a deferral red as a verdict and dispatches a full CI run (R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH)
diff --git a/tools/ci/sweep.py b/tools/ci/sweep.py
index 7055a0af09..c75e5b58bd 100644
--- a/tools/ci/sweep.py
+++ b/tools/ci/sweep.py
@@ -53,7 +53,13 @@ dispatched twice for one red and the branch cannot loop. That run's green `gate`
 own suite and replaces no other run's red (#3400 at 7326025c: the edit run's stale red stood until
 re-run by hand), so the sweep of the fresh run itself -- ci.yml's sweep-self, its actor being the
 token's -- re-runs each stale red once (`fresh` returns False); the re-run's completion settles,
-where V is no green judge, and is left. This sweep runs main's copy
+where V is no green judge, and is left. A dispatch whose first gate attempt was green stays that judge
+after a refresh re-ran its gate red (R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH, #3544: a review event re-ran it,
+it deferred, and a second code run went out); its own red is re-run in place, never pinned. Nor does a
+DEFERRAL red dispatch where a green gate covers the newest event (`covered_deferral`): gate() reads busy()
+before any source, so a red judged while another run's source was unfinished is the deferral, no verdict,
+and is re-run in place, within ATTEMPT_CAP and `settled` like any red; with nothing green (#3261's pair)
+it still dispatches. This sweep runs main's copy
 (gate-sweep.yml), so the countermeasure reaches every PR at once; gate.py's `refresh` runs
 the pinned copy itself, which is why it lives here.
 
@@ -191,11 +197,11 @@ class Sweep:
     def fresh(self, run, gate, runs, pin):
         """Re-judge a stale-pinned red gate by one dispatched run at the head, unless one exists: True.
         False where V is that fresh judge and green: its check replaces no other run's red (#3400), so
-        the stale gate is re-run, once, the run judging after every run here concluded. A dispatch at
+        the stale gate is re-run, once, the run judging after every run here concluded; False too for a
+        covered deferral, no verdict (module doc). A dispatch at
         the head that is not completed, or concluded success, is that judge whenever it was created:
         a re-run stale gate completes after it, and keying on creation re-dispatched (#3446)."""
-        later = [r["id"] for r in runs if r.get("event") == "workflow_dispatch"
-                 and (r.get("status") in NOT_COMPLETED or r.get("conclusion") == "success")]
+        later = [r["id"] for r in runs if r.get("event") == "workflow_dispatch" and self.judged(r)]
         if self.green in later:
             self.out(f"STALE-PIN {pin}: run {self.green}, this head's fresh judge, is green and replaces no "
                      f"other run's red; run {run['id']}'s gate is re-run")
@@ -206,6 +212,10 @@ class Sweep:
         if self.dispatches:
             self.out(f"STALE-PIN {pin}: run {run['id']} left to this sweep's dispatched run")
             return True
+        if self.covered_deferral(run, gate, runs):
+            self.out(f"STALE-PIN {pin}: run {run['id']}'s red is a deferral and a green gate covers the newest "
+                     "event: no verdict to re-judge; re-run in place")
+            return False
         base, ref = self.pull["base"]["ref"], self.pull["head"]["ref"]
         st, _, _ = self.post(f"repos/{self.repo}/actions/workflows/ci.yml/dispatches",
                              {"ref": ref, "inputs": {"pr": str(self.pull_number), "base": base}})
@@ -214,6 +224,23 @@ class Sweep:
                  f"re-judged by a fresh run dispatched on {ref} (HTTP {st})")
         return True
 
+    def judged(self, r):
+        """A dispatch at the head is its fresh judge while not completed, green, or green at its first
+        attempt (a refresh re-run red judged nothing new); an unreadable first attempt is none: dispatch."""
+        if r.get("status") in NOT_COMPLETED or r.get("conclusion") == "success":
+            return True
+        if r["run_attempt"] < 2:
+            return False
+        st, _, body = self.get(f"repos/{self.repo}/actions/runs/{r['id']}/attempts/1/jobs", {"per_page": 100})
+        return st == 200 and (latest_gate((body or {}).get("jobs") or []) or {}).get("conclusion") == "success"
+
+    def covered_deferral(self, run, gate, runs):
+        """A source of another run finished after this red gate started, or has not (it deferred: gate()
+        reads busy() first), and a green gate at the head covers the newest event (module doc)."""
+        others = {r["id"]: self.jobs_of(r["id"]) for r in runs if r["id"] != run["id"]}
+        return (source_after(gate.get("started_at") or "", others)
+                and any(covers_newest(latest_gate(js), runs) for js in others.values()))
+
     def runs_at(self, head):
         runs = self.j("actions/runs", {"head_sha": head, "per_page": 100})["workflow_runs"]
         return [r for r in runs if r.get("path", "").split("@")[0] == CI_PATH]
diff --git a/tools/ci/sweep_selftest.py b/tools/ci/sweep_selftest.py
index 6d10353d6e..4f7f79a233 100644
--- a/tools/ci/sweep_selftest.py
+++ b/tools/ci/sweep_selftest.py
@@ -18,11 +18,17 @@ class World:
         self.limit, self.post_limit = limit, post_limit
         self.base_files, self.bodies, self.compares = [], [], 0     # the base's changes since the PR's pin
         self.head_repo = "o/r"
+        self.attempt_reads = 0
         self.caller = None      # GITHUB_RUN_ID of the job calling the sweep: V's own id is ci.yml's sweep-self
 
     def get(self, path, params=None):
         if self.limit:
             raise sweep.RateLimited(self.limit)
+        if m := re.search(r"/actions/runs/(\d+)/attempts/(\d+)/jobs", path):     # a past attempt's gate, or 404
+            self.attempt_reads += 1
+            g = self.runs[int(m[1])].get("attempts", {}).get(int(m[2]))
+            jobs = [{"name": f"u{k}"} for k in range(40)] + [g]       # #3544's 41 jobs, the gate past a default page
+            return (200, {}, {"jobs": jobs[:min((params or {}).get("per_page", 30), 100)]}) if g else (404, {}, {})
         if m := re.search(r"/actions/runs/(\d+)/jobs", path):
             r = self.runs[int(m[1])]
             return 200, {}, {"jobs": ([r["gate"]] if r.get("gate") else []) + r.get("units", [])}
@@ -153,6 +159,49 @@ def world3308(v_id=42471173865, edit=None):
     return World(runs, v_id)
 
 
+# #3544 at a60a65d8, recorded 2026-11-14 (`gh api .../actions/runs/<id>/attempts/<n>/jobs`): the dispatched run D's
+# first gate was green; review runs R1 and R2 came; R1's refresh re-ran D's green gate, which deferred to them (attempt 2);
+# R1's gate deferred to R2, whose gate went green. R2's sweep re-ran D in place and, R1 being stale-pinned and no green
+# dispatch listed, dispatched run 43574296856: a full code run whose gate held the PR BLOCKED. Trimmed to the gates and
+# the sources that bound them. Rows: (name, conclusion, started, completed), times on 2026-11-14 UTC.
+D3544, R1_3544, R2_3544 = 43531915583, 43572050013, 43572059623
+REC3544 = {     # the three bot-attempt pull_request runs: refresh re-ran their green gates, which deferred to R1 and R2
+    43512354900: ("pull_request", "2026-11-13T21:37:33", 5, BOT, [("gate", "failure", "07:50:57", "07:51:55")]),
+    43512355939: ("pull_request", "2026-11-13T21:37:34", 4, BOT, [("gate", "failure", "07:50:18", "07:51:01")]),
+    43531447639: ("pull_request", "00:02:37", 2, BOT, [("gate", "failure", "07:48:16", "07:48:59")]),
+    D3544: ("workflow_dispatch", "00:06:36", 2, BOT, [
+        ("gate", "failure", "07:41:32", "07:42:13"), ("tests / closures", "success", "00:08:46", "00:21:25"),
+        ("pr-contract / pr-contract", "success", "01:10:24", "01:11:34")]),
+    R1_3544: ("pull_request_review", "07:38:36", 1, "tvofi", [
+        ("gate", "failure", "07:54:14", "07:55:15"), ("refresh", "success", "07:40:21", "07:41:29"),
+        ("prelude", "success", "07:41:55", "07:42:56"), ("budget-raise-gate / budget-raise-gate", "success", "07:44:20", "07:45:06")]),
+    R2_3544: ("pull_request_review", "07:38:43", 1, "tvofi", [
+        ("gate", "success", "08:00:44", "08:01:40"), ("refresh", "success", "07:45:41", "07:46:32"),
+        ("prelude", "success", "07:46:48", "07:47:44"), ("budget-raise-gate / budget-raise-gate", "success", "07:57:19", "07:57:52")]),
+}
+D3544_FIRST_GATE = ("gate", "success", "01:12:52", "01:13:48")
+
+
+def world3544(v_id=R2_3544, edit=None, ids=tuple(REC3544)):
+    """The #3544 recording as a World at a stale pin (main changed tools/ci/gate.py after the PR's base sha)."""
+    stamp = lambda t: t + "Z" if "T" in t else f"2026-11-14T{t}Z"
+    job = lambda k, n, c, s, e: {"id": k, "name": n, "status": "completed", "conclusion": c,
+                                 "started_at": stamp(s), "completed_at": stamp(e)}
+    runs = []
+    for rid in ids:
+        ev, created, attempt, actor, rows = REC3544[rid]
+        js = [job(rid * 10 + k, *row) for k, row in enumerate(rows)]
+        runs.append({"id": rid, "event": ev, "created_at": stamp(created), "status": "completed", "run_attempt": attempt,
+                     "conclusion": js[0]["conclusion"], "triggering_actor": {"login": actor}, "gate": js[0], "units": js[1:]})
+    w = World(runs, v_id)
+    if D3544 in w.runs:
+        w.runs[D3544]["attempts"] = {1: job(D3544 * 10, *D3544_FIRST_GATE)}
+    w.base_files = ["tools/ci/gate.py"]
+    if edit:
+        edit(w.runs)
+    return w
+
+
 def run_checks():
     checks = []
 
@@ -497,6 +546,87 @@ def run_checks():
         w.sweep()
         ok(f"settle: an overlapping pair of re-run gates, re-run by {actor}, with no source after them, "
            f"{'is final' if not want else 'is re-judged (the lower id, null)'}", w.posts == want)
+    # R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH: a deferral red is no verdict where a green gate covers the newest event,
+    # and a dispatched run whose first gate was green stays the head's fresh judge after a refresh re-ran it red.
+    dispatch3544 = "repos/o/r/actions/workflows/ci.yml/dispatches"
+    rerun_of = lambda rid: f"repos/o/r/actions/jobs/{rid * 10}/rerun"
+    w = world3544()
+    rc, out = w.sweep()
+    ok("#3544: the recorded shape (green dispatch, review events, deferral reds, stale pin) dispatches nothing; "
+       "D is re-run in place and R1 left to it, D's first green attempt being the head's fresh judge",
+       rc == 0 and w.posts == [rerun_of(D3544)] and f"run {D3544} re-judges" in out and "dispatches=0" in out)
+    w = world3544(v_id=R1_3544)
+    rc, out = w.sweep()
+    ok("#3544: gate-sweep run 43573334631, R1's settle, the sweep that dispatched run 43574296856, dispatches nothing; "
+       "D is re-run in place, every stale-pinned deferral left to it", rc == 0 and w.posts == [rerun_of(D3544)]
+       and "dispatches=0" in out and out.count(f"run {D3544} re-judges") == 4)
+    w = world3544(ids=(R1_3544, R2_3544))
+    rc, out = w.sweep()
+    ok("#3544 without D: R1's deferral red under a stale pin, R2 green and newest-covering, is re-run in place, "
+       "never dispatched", w.posts == [rerun_of(R1_3544)] and "dispatches=0" in out and "deferral" in out)
+
+    def overlapped(runs):    # R2's last source finished while R1's gate ran: it may have read R2 busy, so a deferral
+        runs[R2_3544]["units"][-1]["completed_at"] = "2026-11-14T07:55:00Z"
+    w = world3544(ids=(R1_3544, R2_3544), edit=overlapped)
+    w.sweep()
+    ok("#3544: a source finishing while the red gate ran (after its start) makes it a deferral: re-run in place",
+       w.posts == [rerun_of(R1_3544)])
+
+    def old_red(runs):       # a third, older review run whose red gate is beside R2's green one, not covering
+        r0 = dict(runs[R1_3544], id=R1_3544 - 1, created_at="2026-11-14T07:30:00Z")
+        r0["gate"] = dict(r0["gate"], id=r0["id"] * 10, started_at="2026-11-14T07:35:00Z", completed_at="2026-11-14T07:36:00Z")
+        r0["units"] = []
+        runs[r0["id"]] = r0
+    w = world3544(ids=(R1_3544, R2_3544), edit=old_red)
+    w.sweep()
+    ok("#3544: one green newest-covering gate covers the head whatever other reds sit beside it: both deferrals "
+       "re-run in place, nothing dispatched", w.posts == [rerun_of(R1_3544 - 1), rerun_of(R1_3544)])
+
+    def real_red(runs):      # R1's gate judged after every OTHER run's source had finished: a verdict, no deferral
+        runs[R1_3544]["gate"].update(started_at="2026-11-14T08:02:00Z", completed_at="2026-11-14T08:02:30Z")
+        runs[R1_3544]["units"].append({"name": "late own job", "conclusion": "success",
+                                       "completed_at": "2026-11-14T08:02:10Z"})   # its own run's: busy() never reads it
+    w = world3544(ids=(R1_3544, R2_3544), edit=real_red)
+    rc, out = w.sweep()
+    ok("#3544 null: a real red on a stale pin, no dispatch at the head, still takes one dispatch",
+       w.posts == [dispatch3544] and "dispatches=1" in out)
+    w = world3544(edit=real_red)
+    rc, out = w.sweep()
+    ok("#3544: a real red on a stale pin beside a dispatch whose first gate was green dispatches nothing",
+       dispatch3544 not in w.posts and f"run {D3544} re-judges" in out)
+    for why, perturb in (("whose first gate was red", lambda w: w.runs[D3544]["attempts"][1].update(conclusion="failure")),
+                         ("whose first attempt cannot be read", lambda w: w.runs[D3544].pop("attempts"))):
+        w = world3544(edit=real_red)
+        perturb(w)
+        rc, out = w.sweep()
+        ok(f"#3544 null: a real red on a stale pin beside a red dispatch {why} dispatches, once",
+           w.posts.count(dispatch3544) == 1 and "dispatches=1" in out)
+    w = world3544(edit=real_red)
+    w.runs[D3544].update(run_attempt=1)
+    w.sweep()
+    ok("#3544 null: a red dispatch at its first attempt is read as is, never its attempts (one dispatch)",
+       w.posts.count(dispatch3544) == 1 and w.attempt_reads == 0)
+    w = world3544(ids=(R1_3544, R2_3544), edit=lambda runs: runs[R1_3544].update(run_attempt=sweep.ATTEMPT_CAP - 1))
+    rc, out = w.sweep()
+    ok("#3544 bound: a deferral red at attempt 44 is left at the cap, neither re-run nor dispatched",
+       w.posts == [] and "at the cap" in out)
+
+    def deferred_again(runs):    # the in-place re-runs overlapped: D's went green, R1's deferred to it again
+        runs[D3544].update(run_attempt=3, conclusion="success")
+        runs[D3544]["gate"].update(conclusion="success", started_at="2026-11-14T08:02:20Z", completed_at="2026-11-14T08:03:10Z")
+        runs[R1_3544].update(run_attempt=2, triggering_actor={"login": BOT})
+        runs[R1_3544]["gate"].update(started_at="2026-11-14T08:02:30Z", completed_at="2026-11-14T08:03:00Z")
+    w = world3544(v_id=R1_3544, edit=deferred_again)
+    rc, out = w.sweep()
+    ok("#3544 bound: R1's re-run that deferred again, swept from itself, is left by settle (the bot's attempt, "
+       "no source after it)", w.posts == [] and "dispatches=0" in out)
+    w = world3544(v_id=D3544, edit=deferred_again)
+    w.runs[D3544].update(status="in_progress")
+    w.runs[D3544]["units"].append({"name": sweep.SELF_JOB, "conclusion": None, "completed_at": None})
+    w.caller = D3544
+    rc, out = w.sweep()
+    ok("#3544 bound: D, green, sweeping itself, re-runs each deferral at the head once in place and dispatches nothing",
+       w.posts == [rerun_of(i) for i in sorted(REC3544) if i != D3544 and i != R2_3544] and "dispatches=0" in out)
     return checks
 
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
