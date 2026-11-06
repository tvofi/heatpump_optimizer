# Review packet #3246
head: 2a0d228c8f6e3d5af516f48f786fe3cb3acea4e6
base: b36679ceaa65a08a67a84f0d934c93aa15f7c7f3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=127931430272 success
arch-score / arch-score id=127930797844 success
arm id=127929770808 skipped
budget-raise-gate / budget-raise-gate id=127930798081 success
cancel-superseded id=127929777876 success
codeql id=127930800007 skipped
codeql / Analyze (actions) id=127930702707 success
codeql / Analyze (javascript-typescript) id=127930702708 success
codeql / Analyze (python) id=127930702612 success
gate id=127931745088 queued
governance id=127930799984 skipped
governance / delivery-status id=127930702619 success
governance / delivery-status-publish id=127930705495 skipped
governance / env-matrix id=127930702726 in_progress
governance / instrument-self-tests id=127930702784 queued
governance / policy-docs id=127930702836 queued
governance / record id=127930705327 skipped
governance / wave-script id=127930702756 queued
hassfest id=127930800005 skipped
hassfest / hassfest id=127930702648 success
kernel-points id=127930800412 skipped
pr-contract id=127931746757 skipped
prelude id=127929777725 success
refresh id=127929777996 success
tests id=127930799694 skipped
tests / arch-instrument id=127931756284 queued
tests / briefs id=127930702654 success
tests / browser id=127931756300 queued
tests / closure-scope id=127930702588 success
tests / closures id=127931756729 queued
tests / coverage id=127931756458 queued
tests / fast (3.14) id=127931756435 queued
tests / mutation id=127930702576 success
tests / mutation-autofix id=127931545624 skipped
tests / mutation-pins id=127931544661 skipped
tests / nightly-ha id=127931759235 skipped
tests / nightly-status id=127930702471 success
tests / replay id=127931759287 skipped
tests / typing id=127931756261 queued
validate id=127930800431 skipped
validate / validate-hacs id=127930702575 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item ecbebc79: dismissed:one-shot payload text, the brief's later line is explicit
NOTE body item 1ecd5ae5: dismissed:identity of a seat commit, settled per brief; this round's commits were re-made as `hpo-fixer` with an identical tree
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show origin/probe/rev-3246-f805b9e8:ev/probe_mixed.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 -I tools/ci/prelude.py --self-test
             `tools/ci/prelude.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants
             `dev/audit/harnesses/r10_ci_gate_core.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_ci_gate_core.py replay
             `dev/audit/harnesses/r10_ci_gate_core.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/r10_gate_defer_race.py --ci <export>/tools/ci
             `dev/audit/harnesses/r10_gate_defer_race.py` is in the tree at this head
  unverified git archive HEAD tools/ci tools/pr
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         tools/ci/gate.py changes the gate itself
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git grep -n "sleep(" -- 'tools/ci/*.py'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 9 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_ci_gate_core.py b/dev/audit/harnesses/r10_ci_gate_core.py
index 72c90f7db..2d4950284 100644
--- a/dev/audit/harnesses/r10_ci_gate_core.py
+++ b/dev/audit/harnesses/r10_ci_gate_core.py
@@ -223,6 +223,19 @@ MUTANTS = [
      ''),
     ("M15 unreadable title", '                bad.append(f"run {r[\'id\']}: unreadable title {r[\'title\']!r}")\n', ''),
     ("M16 B3 on push", 'extra=PUSH_ONLY),', 'extra=None),'),
+    # r10-gate-busy-defer: the tie-break between two started gates at one head, and C3's at-once bound
+    # beside any run whose gate has not started (#3246 review).
+    ("M17 busy tie-break deleted", '\n                  and not (r["id"] > ctx["run_id"] and started(r)))', ')'),
+    ("M18 busy tie-break id inverted", 'r["id"] > ctx["run_id"] and started(r)', 'r["id"] < ctx["run_id"] and started(r)'),
+    ("M19 a listed gate read as started (R3-2 EARLY)", 'return (run.get("jobs") or {}).get("gate", ("",))[0] in STARTED',
+     'return "gate" in (run.get("jobs") or {})'),
+    ("M20 C3 at once beside any run", ' and not all(\n                started(r) for r in api["runs_at_head"] if r["id"] in waiting)', ''),
+    ("M21 C3 waits beside any run", 'deferring(kind, pr, claim) and not all(', 'deferring(kind, pr, claim) and not True and all('),
+    ("M22 C3 at once only beside a code run (c0c60886)", 'not all(\n                started(r) for r in api["runs_at_head"]',
+     'any(\n                (parse_title(r["title"]) or ("code",))[0] == "code" for r in api["runs_at_head"]'),
+    # #3246 round 2: C3 waits only when ALL waited runs have started their gate; ANY re-opens the cycle.
+    ("M24 C3 waits beside any started run (all to any)", 'deferring(kind, pr, claim) and not all(',
+     'deferring(kind, pr, claim) and not any('),
 ]
 
 
@@ -231,13 +244,14 @@ def mutants_arm() -> int:
         print("mutants: gate.py or prelude.py has uncommitted edits; the restore would erase them")
         return 2
 
-    def verdicts() -> tuple[int, int]:
-        st = subprocess.run([sys.executable, "-I", str(GATE), "--self-test"], capture_output=True).returncode
+    def verdicts() -> tuple[int, int, list[str]]:
+        p = subprocess.run([sys.executable, "-I", str(GATE), "--self-test"], capture_output=True, text=True)
         rp = subprocess.run([sys.executable, __file__, "replay"], capture_output=True).returncode
-        return st, rp
-    base = verdicts()
+        red = [ln[5:].split(": got ", 1)[0] for ln in p.stdout.splitlines() if ln.startswith("FAIL ")]
+        return p.returncode, rp, red
+    *base, _ = verdicts()
     print(f"mutants: unmutated self-test rc {base[0]}, replay rc {base[1]}")
-    if base != (0, 0):
+    if base != [0, 0]:
         return 1
     survived = 0
     for name, old, new, *where in MUTANTS:
@@ -250,12 +264,14 @@ def mutants_arm() -> int:
             continue
         target.write_text(text.replace(old, new))
         try:
-            st, rp = verdicts()
+            st, rp, red = verdicts()
         finally:
             target.write_bytes(orig)
         killed = st or rp
         survived += not killed
         print(f"  {name}: {'KILLED' if killed else 'SURVIVED'} (self-test rc {st}, replay rc {rp})")
+        for case in red:
+            print(f"    red: {case}")
     print(f"RESULT mutants={len(MUTANTS)} survivors={survived}")
     return 1 if survived else 0
 
diff --git a/dev/audit/harnesses/r10_gate_defer_race.py b/dev/audit/harnesses/r10_gate_defer_race.py
index 506b29d5a..4b42d85cd 100644
--- a/dev/audit/harnesses/r10_gate_defer_race.py
+++ b/dev/audit/harnesses/r10_gate_defer_race.py
@@ -34,6 +34,11 @@ Scenarios:
             decider, so a code gate expiring at the bound (--edit-s past 740)
             is red on the HIGHER id (#2770 round-1 review).
   single    one code run alone at the head: the null (no wait, no red).
+  prelude   a deferring edit run (C3: its prelude left `pr-contract` to the
+            unfinished code run) at its gate, the code run done, and a later
+            edit run whose prelude waits on it (#3246 review): the prelude/gate
+            seam. Only this scenario lets the runs take the workset their
+            prelude returns (`--defer`), so the others replay as recorded.
 
 Per scenario it prints every published `gate` verdict with its simulated time,
 then: UNDECIDED-RED (a FAIL whose reason is the deferral), MASKED (a PASS
@@ -41,7 +46,9 @@ published while a real red source exists), DEADLOCK (no gate PASS and no real
 red: nothing at the head ever decides green), and the gates' total wait, all
 over the gates the scenario runs; then RESIDUAL-RED, on a head with no real
 red, the runs whose latest gate, after every sweep has converged, is still the
-deferral's red.
+deferral's red. DEADLOCK also reads yes when a wait cycle formed: a gate slept
+on a run still in its prelude whose wait_sources waits on that gate's run (the
+CYCLE count beside it), however the bound later broke it.
 """
 from __future__ import annotations
 
@@ -131,6 +138,27 @@ class Head:
         self.sweep = importlib.import_module("sweep") if (ci / "sweep.py").exists() else None
         self.sim, self.runs, self.verdicts, self.waited = sim, {}, [], 0
         self.timed = "sleep" in inspect.signature(self.gate.judge).parameters
+        self.defer, self.cycles, self.last_busy = False, set(), {}
+        busy = self.gate.busy
+
+        def seen_busy(ctx, runs_at_head):          # judge() reads the module global at each call
+            out = busy(ctx, runs_at_head)
+            self.last_busy[int(ctx["run_id"])] = out
+            return out
+        self.gate.busy = seen_busy
+
+    def gate_nap(self, rid):
+        """The gate's sleep: first record each wait edge that closes a cycle through a prelude."""
+        def nap(s):
+            me = self.runs[rid]
+            mine = {"id": rid, "title": me["title"],
+                    "jobs": {k: (st, c) for k, (st, c, seen) in me["jobs"].items() if seen <= self.sim.t}}
+            for y in self.last_busy.get(rid, []):
+                if (self.runs[y].get("phase") == "prelude" and self.prelude.waits_on(y, mine)
+                        and not self.prelude.judging(mine)):
+                    self.cycles.add((rid, y))
+            self.sim.sleep(s)
+        return nap
 
     def get(self, path, params=None):
         if path.endswith(f"/pulls/{PR}"):
@@ -152,8 +180,8 @@ class Head:
         action = "edited" if kind == "edit" else "synchronize"
         return self.prelude.context("pull_request", {"action": action, "pull_request": pr}, env)
 
-    def names(self, kind):
-        ws = self.prelude.workset(kind, str(PR))
+    def names(self, kind, ws=None):
+        ws = self.prelude.workset(kind, str(PR)) if ws is None else ws
         return [f"{u} / {n}" for u in sorted(ws & set(self.gate.UNITS)) for n in self.gate.UNITS[u]]
 
     def add(self, rid, kind, created, prelude_at, units_s, red=(), lag=0, done=False):
@@ -173,12 +201,18 @@ class Head:
             r["status"] = "in_progress"
             r["jobs"]["prelude"] = ("in_progress", None, self.sim.t)
             c = self.ctx(rid, kind)
-            _, why = self.prelude.outputs(c, [], self.get, self.sim.sleep)
+            r["phase"] = "prelude"
+            out, why = self.prelude.outputs(c, [], self.get, self.sim.sleep)
+            r["phase"] = "units"
             r["jobs"]["prelude"] = ("completed", "failure" if why else "success", self.sim.t)
-            for n in self.names(kind):
+            ws = set(out["workset"].split()) if self.defer else None
+            if ws is not None and ws < self.prelude.workset(kind, str(PR)):
+                r["workset"] = ws                  # C3: the caller job is listed skipped, under its bare name
+                r["jobs"]["pr-contract"] = ("completed", "skipped", self.sim.t)
+            for n in self.names(kind, ws):
                 r["jobs"][n] = ("in_progress", None, self.sim.t)
             self.sim.sleep(units_s)
-            for n in self.names(kind):
+            for n in self.names(kind, ws):
                 r["jobs"][n] = ("completed", "failure" if n in red else "success", self.sim.t)
             self.judge(rid, kind, lag)
         self.sim.spawn(life)
@@ -197,8 +231,9 @@ class Head:
         r["jobs"]["gate"] = ("in_progress", None, self.sim.t + lag)
         c = self.ctx(rid, kind, attempt)
         t0 = self.sim.t
-        kw = {"sleep": self.sim.sleep, "now": self.sim.now} if self.timed else {}
-        out = self.gate.judge(c, {"kind": kind, "pr": str(PR)}, self.get, lambda b, h: True, **kw)[0]
+        kw = {"sleep": self.gate_nap(rid), "now": self.sim.now} if self.timed else {}
+        claim = {"kind": kind, "pr": str(PR), **({"workset": r["workset"]} if "workset" in r else {})}
+        out = self.gate.judge(c, claim, self.get, lambda b, h: True, **kw)[0]
         self.waited += self.sim.t - t0
         self.sim.sleep(JUDGE_S)                    # the job publishes its check-run after its last read
         self.verdicts.append((self.sim.t, rid, out, self.sim.t - JUDGE_S - t0, by_sweep))
@@ -259,19 +294,24 @@ def scenario(ci: Path, name: str, edit_s: int):
         h.rerun_gate(90, 30)
     elif name == "single":
         h.add(100, "code", 0, 30, 600)
+    elif name == "prelude":
+        h.defer = True
+        h.add(100, "code", 0, 60, 300)             # units 60-360 s: its pr-contract has not started at 30 s
+        h.add(101, "edit", 0, 30, 400)             # prelude at 30 s defers (C3); gate at 430 s
+        h.add(102, "edit", 420, 425, 120)          # prelude at 425 s, beside 101's gate (430 s)
     sim.run()
     defer = "still being judged"
     own = [v for v in h.verdicts if not v[4]]
     undecided = sum(1 for _, _, o, _, _ in own if o.startswith("FAIL") and defer in o)
     masked = sum(1 for _, _, o, _, _ in h.verdicts if o == "PASS") if real_red else 0
-    deadlock = not real_red and not any(o == "PASS" for _, _, o, _, _ in h.verdicts)
+    deadlock = bool(h.cycles) or not real_red and not any(o == "PASS" for _, _, o, _, _ in h.verdicts)
     latest = {rid: r["seeded"] for rid, r in h.runs.items() if "seeded" in r}
     latest.update((rid, o) for _, rid, o, _, _ in h.verdicts)
     residual = 0 if real_red else sum(1 for o in latest.values() if o.startswith("FAIL") and defer in o)
     for t, rid, o, w, by in h.verdicts:
         print(f"  t={t:>5}s run {rid}{' sweep' if by else ''} (waited {w} s): {o}")
     print(f"{name}: verdicts {len(own)} UNDECIDED-RED {undecided} MASKED {masked} "
-          f"DEADLOCK {'yes' if deadlock else 'no'} gate-wait {h.waited} s (judge takes a clock: {h.timed})")
+          f"DEADLOCK {'yes' if deadlock else 'no'} CYCLE {len(h.cycles)} gate-wait {h.waited} s (judge takes a clock: {h.timed})")
     print(f"{name}: sweep {'present' if h.sweep else 'absent'} re-runs {len(h.verdicts) - len(own)} "
           f"RESIDUAL-RED {residual}")
     for m in MODULES:
@@ -283,7 +323,7 @@ def main() -> int:
     ap = argparse.ArgumentParser()
     ap.add_argument("--ci", default=str(Path(__file__).resolve().parents[3] / "tools" / "ci"))
     ap.add_argument("--edit-s", type=int, default=518)
-    ap.add_argument("scenarios", nargs="*", default=["2754", "2754-red", "pair", "cascade", "editcode", "single"])
+    ap.add_argument("scenarios", nargs="*", default=["2754", "2754-red", "pair", "cascade", "editcode", "single", "prelude"])
     a = ap.parse_args()
     ci = Path(a.ci).resolve()
     for s in a.scenarios:
diff --git a/dev/programme/delivery/3246.md b/dev/programme/delivery/3246.md
new file mode 100644
index 000000000..f482ffa28
--- /dev/null
+++ b/dev/programme/delivery/3246.md
@@ -0,0 +1 @@
+- [#3246](https://github.com/tvofi/heatpump_optimizer/pull/3246) — **open**, R10-HOTFIX-GATE-BUSY-DEFER: one concurrent gate run decides at a head (R10-HOTFIX-GATE-BUSY-DEFER)
diff --git a/tools/ci/gate.py b/tools/ci/gate.py
index a3574b2e5..141ad2a31 100644
--- a/tools/ci/gate.py
+++ b/tools/ci/gate.py
@@ -35,13 +35,23 @@ verdict it then publishes is the one every gate at the head computes from the
 same finished sources, so a red source stays red and no wait masks it. The
 waits are acyclic: a gate waits only on runs that are not yet `judging`, and
 nothing waits on a judging run (prelude.wait_sources), so two gates that
-start together each find the other judging on a re-read. Only past the
+start together each find the other judging on a re-read. Two runs whose
+gates have both started are broken by id (`busy`): the lower decides, the higher
+waits on it, so a run that judging() misreads (a deferring edit run never lists
+its title's pr-contract) cannot make two gates defer to each other. Only past the
 bound, a run still busy after GATE_WAIT_MAX_S, does the gate FAIL deferring,
 for gate-sweep.yml to re-judge. One gate never waits (R10-CI-SLIM card C3): an
 edit run's whose prelude left `pr-contract` to an unfinished code run at this
 head (prelude.defer_to, `deferring` here). It publishes the deferral at once:
 that code run's gate is listed only after its pr-contract has read the latest
-body, so it is the later verdict here, and the sweep re-judges this one.
+body, so it is the later verdict here, and the sweep re-judges this one. The
+same holds beside any run whose gate has not started: judging() reads a
+deferring run busy, so such a run may sit in prelude.wait_sources waiting on
+this one, a cycle only GATE_WAIT_MAX_S would break (#3246 review). A deferring
+gate waits only when every run it waits on has started its gate: busy() leaves
+out a LATER started gate, so each is an earlier run, and one busy() still names
+is not judging, so a deferring run (it waits only so, down in id) or one whose
+listing lags its own owed jobs, which a re-read clears.
 """
 from __future__ import annotations
 
@@ -56,7 +66,7 @@ from pathlib import Path
 HERE = Path(__file__).resolve().parent
 sys.path.insert(0, str(HERE))                      # -I drops the script's directory
 import ghapi  # noqa: E402
-from prelude import (BODY_UNITS, CODE_UNITS, POLL_S, UNITS, context, derive, judging, parse_title,  # noqa: E402,F401
+from prelude import (BODY_UNITS, CODE_UNITS, POLL_S, STARTED, UNITS, context, derive, judging, parse_title,  # noqa: E402,F401
                      run_jobs, title, workset)
 
 PUSH_ONLY = {"tests": ("coverage", "coverage-ratchet", "ci-ratchet")}      # B3
@@ -98,10 +108,25 @@ def gate_required() -> list[str]:
     return sorted({n for names in REQUIRED.values() for n in names})
 
 
+def started(run: dict) -> bool:
+    """Whether the run's `gate` job has started: listed `in_progress` or `completed`,
+    never merely listed (GitHub lists it `waiting` from the run's start, R3-2)."""
+    return (run.get("jobs") or {}).get("gate", ("",))[0] in STARTED
+
+
 def busy(ctx: dict, runs_at_head: list[dict]) -> list:
-    """The OTHER runs at this head still adding a source: unfinished, not held, not judging."""
+    """The OTHER runs at this head still adding a source: unfinished, not held, not
+    judging, and not a LATER run whose `gate` has started. A started gate has run
+    every unit it needs (ci.yml's `needs`; a merely listed one has not: GitHub
+    lists it `waiting` from the run's start, R3-2), yet judging() can still read
+    it busy:
+    a deferring edit run never lists the `pr-contract / pr-contract` its title
+    owes (C3). Two such gates then each deferred to the other and none judged
+    (#3241 at 95c7e604, runs 42192623509 and 42193153511). The tie-break: the
+    lower id decides, the higher waits on it, so the waits stay acyclic."""
     return sorted(r["id"] for r in runs_at_head
-                  if r["id"] != ctx["run_id"] and r["status"] not in ("completed", "action_required") and not judging(r))
+                  if r["id"] != ctx["run_id"] and r["status"] not in ("completed", "action_required") and not judging(r)
+                  and not (r["id"] > ctx["run_id"] and started(r)))
 
 
 def deferral(ids: list) -> str:
@@ -260,8 +285,9 @@ def judge(ctx: dict, claim: dict, get, reaches=reaches_custom_components, sleep=
         ok, why = gate(ctx, api)
         waiting = busy(ctx, api["runs_at_head"])
         bound = GATE_WAIT_MAX_S if why == [deferral(waiting)] else lag_bound(why)
-        if why == [deferral(waiting)] and deferring(kind, pr, claim):
-            bound = 0                           # C3: that busy code run's gate is the later verdict; hold no runner
+        if why == [deferral(waiting)] and deferring(kind, pr, claim) and not all(
+                started(r) for r in api["runs_at_head"] if r["id"] in waiting):
+            bound = 0                           # C3: a waited run's gate is the later verdict; hold no runner
         if ok or now() - t0 + POLL_S > bound:
             break
         if why != [deferral(waiting)]:
@@ -505,6 +531,57 @@ def self_test() -> int:
     verdict(ectx, get, nap, now, {"kind": "edit", "pr": "7"})
     check("... null control: the same gate with the full edit workset waits on it, bounded, as before",
           (bool(naps), sum(naps) <= GATE_WAIT_MAX_S), (True, True))
+    # r10-gate-busy-defer: #3241 head 95c7e604, attempt 2 -- two deferring edit
+    # runs, each gate listed, each read the other as busy (its pr-contract never
+    # listed), so both published the deferral and no gate judged.
+    lo, hi = 42192623509, 42193153511
+    at_gate = deferred + [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}]
+    pair = [{"id": i, "title": title("edit", "7", "main", "M"), "status": "in_progress",
+             "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in at_gate}} for i in (lo, hi)]
+    check("busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower",
+          (busy({**ctx, "run_id": lo}, pair), busy({**ctx, "run_id": hi}, pair)), ([], [lo]))
+    coded = run(99, "code", "completed", owed("code")[:-1] + [{"name": "gate", "status": "completed",
+                                                                "conclusion": "success", "id": 9}])
+    get, naps, nap, now = scene([coded, run(hi, "edit", "in_progress", at_gate)], me=lo, mine=deferred)
+    check("busy-defer: the lower deferring edit gate judges at once beside the higher one",
+          (verdict({**ectx, "run_id": lo}, get, nap, now, eclaim3), naps), ("PASS", []))
+    get, naps, nap, now = scene([coded, run(lo, "edit", "in_progress", at_gate)],
+                                [coded, run(lo, "edit", "completed", deferred + [{"name": "gate", "status": "completed",
+                                                                          "conclusion": "success", "id": 9}])],
+                                me=hi, mine=deferred)
+    check("busy-defer: the higher deferring edit gate waits on the lower (an edit run, not C3's code run), "
+          "then judges, never a red deferral", (verdict({**ectx, "run_id": hi}, get, nap, now, eclaim3), naps),
+          ("PASS", [POLL_S]))
+    early = [{"id": lo, "title": title("code", "7", "main", "M"), "status": "in_progress",
+              "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in owed("code", gate=False, state="in_progress")}}]
+    check("busy-defer null: a genuinely earlier run still adding sources is still deferred to",
+          busy({**ctx, "run_id": hi}, early), [lo])
+    late_busy = [{**early[0], "id": hi}]
+    check("busy-defer null: a later run whose gate is not listed is still deferred to (no gate yet: it adds sources)",
+          busy({**ctx, "run_id": lo}, late_busy), [hi])
+    late_waiting = [{**early[0], "id": hi, "jobs": {**early[0]["jobs"], "gate": ("waiting", None)}}]
+    check("busy-defer null (R3-2 EARLY): a later run whose gate is listed `waiting` beside running units is "
+          "still deferred to", busy({**ctx, "run_id": lo}, late_waiting), [hi])
+    # #3246 review: the same deferring gate (lo) beside a LATER edit run (hi) still
+    # in its prelude, the code run done. hi's prelude waits on lo (judging() reads
+    # a deferring run busy), so lo's gate must not wait on hi: it publishes at once.
+    for label, hi_jobs in (("still in its prelude", in_prelude),
+                           ("in its prelude, gate listed `waiting` (R3-2)",
+                            in_prelude + [{"name": "gate", "status": "waiting", "conclusion": None, "id": 9}])):
+        get, naps, nap, now = scene([coded, run(hi, "edit", "in_progress", hi_jobs)], me=lo, mine=deferred)
+        check(f"prelude/gate cycle: a deferring gate beside a later edit run {label} publishes at once",
+              (verdict({**ectx, "run_id": lo}, get, nap, now, eclaim3), naps), ("FAIL " + deferral([hi]), []))
+    # #3246 round 2: the same scene with an EARLIER deferring edit run whose gate has
+    # started beside hi. C3 waits only when ALL waited runs have started their gate;
+    # read as ANY, lo waits on hi while hi's prelude waits on lo (the 720 s cycle).
+    early_gate = 42192000000
+    get, naps, nap, now = scene([coded, run(early_gate, "edit", "in_progress",
+                                            deferred + [{"name": "gate", "status": "in_progress",
+                                                         "conclusion": None, "id": 9}]),
+                                 run(hi, "edit", "in_progress", in_prelude)], me=lo, mine=deferred)
+    check("prelude/gate cycle: a deferring gate beside an earlier started gate and a later edit run in its "
+          "prelude publishes at once", (verdict({**ectx, "run_id": lo}, get, nap, now, eclaim3), naps),
+          ("FAIL " + deferral([early_gate, hi]), []))
     done_edit = run(101, "edit", "completed", deferred + [{"name": "gate", "status": "completed",
                                                            "conclusion": "failure", "id": 9}])
     get, naps, nap, now = scene([done_edit])

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
