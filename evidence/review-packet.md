# Review packet #3484
head: 190ec599dac05e7a19e7639376c737d53ba40685
base: 6e100ef6980216a81eaa0438bdc215d62b19271f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131180931213 success
arch-score / arch-score id=131191981627 success
arm id=131180482462 skipped
budget-raise-gate / budget-raise-gate id=131191925733 success
cancel-superseded id=131191980566 success
codeql id=131191951357 skipped
codeql / Analyze (actions) id=131180812463 success
codeql / Analyze (javascript-typescript) id=131180812279 success
codeql / Analyze (python) id=131180812687 success
gate id=131191924099 success
governance id=131191948191 skipped
governance / delivery-status id=131180812622 success
governance / delivery-status-publish id=131180815209 skipped
governance / env-matrix id=131180812475 success
governance / instrument-self-tests id=131180812572 success
governance / policy-docs id=131180812419 success
governance / record id=131180815592 skipped
governance / wave-script id=131180812499 success
hassfest id=131191965939 skipped
hassfest / hassfest id=131180812218 success
kernel-points id=131191951608 skipped
pr-contract id=131191926889 skipped
pr-contract / pr-contract id=131189527139 success
prelude id=131191982982 success
refresh id=131191994833 success
sweep-self id=131192348646 skipped
tests id=131191924725 skipped
tests / arch-instrument id=131181254178 success
tests / briefs id=131180812470 success
tests / browser id=131181253384 success
tests / ci-ratchet id=131188975396 skipped
tests / claims-autofix id=131188974195 skipped
tests / closure-scope id=131180812806 success
tests / closures id=131181255359 success
tests / closures-autofix id=131188793399 skipped
tests / coverage id=131181253999 success
tests / coverage-ratchet id=131188660437 success
tests / fast (3.14) id=131181253415 success
tests / graders-head-copy id=131188660408 success
tests / lane-proofs id=131188971804 success
tests / mutation id=131180812408 success
tests / mutation-autofix id=131181220835 skipped
tests / mutation-pins id=131181219392 skipped
tests / nightly-ha id=131181257833 skipped
tests / nightly-status id=131180812348 failure
tests / replay id=131181255518 skipped
tests / typing id=131181253457 success
validate id=131191982221 skipped
validate / validate-hacs id=131180812556 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 6e100ef6980216a81eaa0438bdc215d62b19271f lacks origin/main 2b4515dc52821ad721225090d329c224dbddafae; roster read at origin/main
NOTE body item 209ce3ba: R10-SEAT-IDENTITY-P5: R10-SEAT-IDENTITY-P5 resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/beatd.py --self-test
             `tools/audit/seat/beatd.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/entities.py 677 files
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 -I tools/audit/seat/open_driver.py --self-test
             `tools/audit/seat/open_driver.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/beatd.py --self-test 9
             `tools/audit/seat/beatd.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_open_driver_mutants.py
             `dev/audit/harnesses/r10_open_driver_mutants.py` is in the tree at this head
  unverified git archive origin/main
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified HPO_GATE_PRIORITY=2 python3 -c '... gate_lock._priority_cases(gate_lock) ...'
             python3 runs an inline script rather than a file
  ok         HPO_GATE_PRIORITY=2 PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 13 resolved, 2 not verified, 0 refused

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
index 205ba633ed..44d3740eea 100644
--- a/dev/audit/harnesses/r10_open_driver_mutants.py
+++ b/dev/audit/harnesses/r10_open_driver_mutants.py
@@ -31,10 +31,14 @@ nothing mutated, must print failed=0. A pattern not found exactly once aborts.
   M-reap-stem   run_pass reads the raw topic's .rc: a slash topic's result is
                 never reaped (the reap side).
   M-reap-log    run_pass reads the raw topic's log: the RESULT reason is lost.
+  M-livetip     restores the SKIP moved on a board sha behind origin's live tip
+                (OPENER-LIVE-TIP, P603): the line at A no longer opens at B.
+  M-moved-gone  drops the SKIP moved on an absent handoff ref: the null control
+                (a gone ref still prints SKIP moved) fails.
 
     python3 dev/audit/harnesses/r10_open_driver_mutants.py
 
-EXPECTED RESULT mutants=22
+EXPECTED RESULT mutants=24
 EXPECTED RESULT survived=0
 """
 from __future__ import annotations
@@ -62,6 +66,9 @@ ROOT = repo_root(__file__)
 SEAT = "tools/audit/seat"
 TARGET = "open_driver.py"
 PLANTS = {
+    "M-livetip": ("            log(f\"RETIP {topic} {sha[:8]} -> {live_tip[:8]}\")\n            sha = live_tip\n",
+                  "            live_tip = None\n"),
+    "M-moved-gone": ("        elif live_tip is None:\n            skip(\"moved\")", "        elif False:\n            skip(\"moved\")"),
     "M-exact": ("    if up in groups:  # exact match always wins\n", "    if False:\n"),
     "M-body": (" and names_group(body_head, m.group(1).upper())", ""),
     "M-landed": ("        elif main and world.landed(main, sha):\n", "        elif False:\n"),
diff --git a/dev/programme/delivery/3484.md b/dev/programme/delivery/3484.md
new file mode 100644
index 0000000000..c1400eed99
--- /dev/null
+++ b/dev/programme/delivery/3484.md
@@ -0,0 +1 @@
+- [#3484](https://github.com/tvofi/heatpump_optimizer/pull/3484) — **open**, R10-HOTFIX-OPENER-UNBLOCK: r10 hotfix opener unblock (R10-HOTFIX-OPENER-UNBLOCK)
diff --git a/tests/gate_lock.py b/tests/gate_lock.py
index b496343862..8bfec99b5a 100644
--- a/tests/gate_lock.py
+++ b/tests/gate_lock.py
@@ -1625,9 +1625,12 @@ def _priority_cases(g) -> list[tuple[str, bool, str]]:
             time.sleep(0.15)
             g.release(who, lock_dir=d)
 
-        normal = threading.Thread(target=one, args=("normal",), daemon=True)
-        normal.start()
-        normal_queued = bool(ticket_text(d, "normal"))
+        # The normal waiter enters with no priority set, whatever the caller exports:
+        # prepr.sh exports HPO_GATE_PRIORITY=2 on a hotfix branch, which made both urgent.
+        with _Env(None):
+            normal = threading.Thread(target=one, args=("normal",), daemon=True)
+            normal.start()
+            normal_queued = bool(ticket_text(d, "normal"))
         with _Env("2"):
             urgent = threading.Thread(target=one, args=("urgent",), daemon=True)
             urgent.start()
@@ -1735,9 +1738,12 @@ def _priority_cases(g) -> list[tuple[str, bool, str]]:
             time.sleep(0.1)
             g.release_slot(who, lock_dir=d, slots=1)
 
-        normal = threading.Thread(target=one, args=("normal",), daemon=True)
-        normal.start()
-        normal_queued = bool(ticket_text(pool, "normal"))
+        # The normal waiter enters with no priority set, whatever the caller exports:
+        # prepr.sh exports HPO_GATE_PRIORITY=2 on a hotfix branch, which made both urgent.
+        with _Env(None):
+            normal = threading.Thread(target=one, args=("normal",), daemon=True)
+            normal.start()
+            normal_queued = bool(ticket_text(pool, "normal"))
         with _Env("2"):
             urgent = threading.Thread(target=one, args=("urgent",), daemon=True)
             urgent.start()
diff --git a/tools/audit/seat/beatd.py b/tools/audit/seat/beatd.py
index fbca6ebe1a..2d103b7cf4 100644
--- a/tools/audit/seat/beatd.py
+++ b/tools/audit/seat/beatd.py
@@ -61,6 +61,22 @@ when the START code is behind origin/main. rc 0 clean, 1 any alarm (late,
 DOWN, a non-ok last outcome, an ALERT, STALE-CODE), 2 unreadable (table,
 journal line, or the staleness read). An unreadable input is never clean.
 
+FRESH (BEAT-STALE-CHECKOUT, P581). The opener refuses STALE CHECKOUT when the
+beat's tools checkout is behind origin/main on tools/audit/seat or tools/pr
+(pr_args.sh pr_tools_fresh), so after every PASS (not under `--once`) the beat
+measures its own checkout, the one holding this file, with that path-filtered
+count; STATUS's STALE-CODE counts every commit and stays the alarm. Behind,
+it restarts when no job instance is running, the tree is clean (tracked files),
+no commit is outside origin/main, origin/main's beatd.py compiles, and it has
+not already restarted to this origin/main: `git checkout -q -B <branch>
+origin/main` (`--detach` on a detached head), STOP, `BEAT-RESTART <utc>
+code=<old> behind=<n> -> <new>` on stdout, then it re-execs itself in place
+with the same arguments and `HPO_BEATD_RESTARTED=<new>`, the guard. No job
+starts once the restart is taken. Otherwise it prints `beatd: NO-RESTART
+behind=<n> code=<sha12>: <why>`, and from the second consecutive refusal also
+`BEAT-STALE <utc> behind=<n> code=<sha12>: <why>`; a running instance only
+defers to the next PASS. The checkout path never changes.
+
 HELD. `held` is beatd.lock's one reader for other scripts: rc 0 and
 `held pid=<p>` while a beat holds it, rc 1 `free` otherwise. Its probe is a
 shared non-blocking flock released at once; `run` retries its own lock for
@@ -94,6 +110,8 @@ CLASSES = {None, "orch-checkout"}
 KINDS = {"periodic", "watch"}
 BASE_ENV = ("HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TMPDIR", "SHELL")
 KILL_GRACE_S = 10.0
+SEAT_PATHS = ("tools/audit/seat", "tools/pr")  # pr_args.sh PR_FRESH_PATHS: the opener's STALE CHECKOUT
+RESTARTED_ENV = "HPO_BEATD_RESTARTED"
 OUTCOMES = ("ok", "failed", "timeout", "locked", "busy", "unreadable")
 LINE_RE = re.compile(
     r"^(?:START \S+ beatd pid=\d+ code=\S+ supervisor=\S+"
@@ -298,6 +316,11 @@ class Beat:
         self.jlock = threading.Lock()
         self.stop = threading.Event()
         self.procs: dict[str, subprocess.Popen] = {}
+        self.alock = threading.Lock()  # guards active, the restart decision and stale_n
+        self.active: set[str] = set()
+        self.restart: str | None = None
+        self.stale_n = 0
+        self.once = False
 
     def journal(self, line: str) -> None:
         with self.jlock, open(self.dir / "journal.log", "a") as f:
@@ -320,6 +343,19 @@ class Beat:
 
     def run_one(self, job: dict) -> None:
         name, t0 = job["name"], time.time()
+        with self.alock:
+            if self.restart:
+                return  # a restart was taken: no new instance
+            self.active.add(name)
+        try:
+            self._run_one(job, name, t0)
+        finally:
+            with self.alock:
+                self.active.discard(name)
+        if not self.once:
+            self.fresh()
+
+    def _run_one(self, job: dict, name: str, t0: float) -> None:
         rc, outcome = -1, "ok"
         jl = Lock(self.dir / f"{name}.lock")
         cl = Lock(self.dir / f"{job['class']}.lock") if job["class"] else None
@@ -378,6 +414,57 @@ class Beat:
             nxt = next_start(job["kind"], nxt, start, time.time(), job["interval_s"])
             self.stop.wait(max(0.0, nxt - time.time()))
 
+    def g(self, top: Path, *a: str) -> subprocess.CompletedProcess:
+        return subprocess.run([self.git, "-C", str(top), *a], capture_output=True, text=True)
+
+    def fresh(self) -> None:
+        """Between passes: restart onto origin/main when the own checkout is behind on
+        SEAT_PATHS and every precondition holds, else print why (FRESH above)."""
+        top = Path(__file__).resolve().parents[3]
+        with self.alock:
+            if self.restart:
+                return
+            r = self.g(top, "rev-list", "--count", "HEAD..origin/main", "--", *SEAT_PATHS)
+            if r.returncode == 0 and r.stdout.strip() == "0":
+                self.stale_n = 0
+                return
+            behind = r.stdout.strip() if r.returncode == 0 else "unknown"
+            code = self.g(top, "rev-parse", "HEAD").stdout.strip()[:12] or "unknown"
+            new = self.g(top, "rev-parse", "origin/main").stdout.strip()
+            why = None
+            if r.returncode or not new:
+                why = "could not count origin/main over the checkout"
+            elif os.environ.get(RESTARTED_ENV) == new:
+                why = f"restarted once to {new[:12]} and still behind"
+            elif self.g(top, "status", "--porcelain", "--untracked-files=no").stdout.strip():
+                why = "the tree is dirty"
+            elif (n := self.g(top, "rev-list", "--count", "origin/main..HEAD").stdout.strip()) != "0":
+                why = f"{n or 'unknown'} commit(s) not on origin/main"
+            else:
+                src = self.g(top, "show", "origin/main:tools/audit/seat/beatd.py")
+                try:
+                    if src.returncode:
+                        raise SyntaxError(src.stderr.strip()[-80:])
+                    compile(src.stdout, "beatd.py", "exec")
+                except (SyntaxError, ValueError) as e:
+                    why = f"origin/main's tools/audit/seat/beatd.py does not compile: {str(e)[:80]}"
+            if why is None and self.active:
+                why = "a job instance is running: " + " ".join(sorted(self.active))
+            if why is None:
+                br = self.g(top, "symbolic-ref", "-q", "--short", "HEAD").stdout.strip()
+                co = self.g(top, "checkout", "-q", *(["-B", br] if br else ["--detach"]), "origin/main")
+                if co.returncode:
+                    why = f"the checkout failed: {co.stderr.strip()[-80:]}"
+                else:
+                    self.restart = new
+                    self.stop.set()
+                    print(f"BEAT-RESTART {utc()} code={code} behind={behind} -> {new[:12]}", flush=True)
+                    return
+            self.stale_n += 1
+            print(f"beatd: NO-RESTART behind={behind} code={code}: {why}", flush=True)
+            if self.stale_n >= 2:
+                print(f"BEAT-STALE {utc()} behind={behind} code={code}: {why}", flush=True)
+
     def code(self) -> str:
         r = subprocess.run([self.git, "-C", str(self.repo), "rev-parse", "HEAD"],
                            capture_output=True, text=True)
@@ -385,6 +472,7 @@ class Beat:
 
     def run(self, once: bool, for_s: float | None) -> int:
         sup = os.environ.get("HPO_BEATD_SUPERVISOR") or "none"
+        self.once = once
         self.journal(f"START {utc()} beatd pid={os.getpid()} code={self.code()} supervisor={sup}")
         threads = [threading.Thread(target=self.loop, args=(j, once), daemon=True)
                    for j in self.table["jobs"]]
@@ -431,10 +519,15 @@ def cmd_run(a) -> int:
                                                    "env": {k: v for k, v in os.environ.items() if k.startswith("HPO_")}}))
     except OSError:
         pass
+    beat = Beat(state, table, Path(a.repo).resolve(), real)
     try:
-        return Beat(state, table, Path(a.repo).resolve(), real).run(a.once, a.for_s)
+        rc = beat.run(a.once, a.for_s)
     finally:
         inst.drop()
+    if beat.restart:  # in place: same path, same arguments, the guard in the environment
+        os.execve(sys.executable, [sys.executable, "-I", str(Path(__file__).resolve()), *a.argv],
+                  {**os.environ, RESTARTED_ENV: beat.restart})
+    return rc
 
 
 # ---------------------------------------------------------------- status
@@ -551,6 +644,7 @@ def main(argv: list[str]) -> int:
     s.add_argument("--pulse")
     s.add_argument("--now", type=float)
     a = ap.parse_args(argv)
+    a.argv = argv
     try:
         return {"run": cmd_run, "status": cmd_status, "held": cmd_held}[a.cmd](a)
     except Refuse as e:
@@ -1119,8 +1213,112 @@ def case8(prog, w):
             "null: rc 1 after release": free1 == 1}
 
 
+def _fresh_repo(w: Path, label: str, prog: Path, main_adds: dict, local: bool = False,
+                dirty: bool = False):
+    """A checkout holding `prog` at tools/audit/seat/beatd.py on branch main at C1,
+    with origin/main at C2 = C1 + main_adds. Returns (repo, env, g, c1, c2)."""
+    real = resolve_git(os.environ.get("PATH", ""))
+    repo = w / f"repo9-{label}"
+    sys.path.insert(0, str(ROOT / "tests"))
+    from throwaway_git import throwaway_git_init
+    env = throwaway_git_init(repo, "-q", "-b", "main", git=(real,))
+    g = lambda *a: subprocess.run([real, "-C", str(repo), *a], check=True, env=env,
+                                  capture_output=True, text=True).stdout.strip()
+    seat = repo / "tools" / "audit" / "seat"
+    seat.mkdir(parents=True)
+    (seat / "beatd.py").write_text(prog.read_text())
+    (repo / "README").write_text("r\n")
+    g("add", "-A")
+    g("commit", "-q", "-m", "c1")
+    c1 = g("rev-parse", "HEAD")
+    for rel, text in main_adds.items():
+        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
+        (repo / rel).write_text(text)
+    g("add", "-A")
+    g("commit", "-q", "-m", "c2")
+    c2 = g("rev-parse", "HEAD")
+    g("update-ref", "refs/remotes/origin/main", c2)
+    g("reset", "-q", "--hard", c1)
+    if local:
+        g("commit", "-q", "--allow-empty", "-m", "local")
+    if dirty:
+        (repo / "README").write_text("dirty\n")
+    return repo, env, g, c1, c2
+
+
+def case9(prog, w):
+    """(a)9 BEAT-STALE-CHECKOUT (P581): between passes a beat whose own checkout is
+    behind origin/main on tools/audit/seat or tools/pr, idle, clean, with no local
+    commit and a compiling main beatd.py, checks out origin/main and re-execs
+    itself; each refusal prints its why, and a second one prints BEAT-STALE."""
+    res = {}
+
+    def beat(label, adds, jobs, for_s="3", guard=False, once=False, **kw):
+        repo, env, g, c1, c2 = _fresh_repo(w, label, prog, adds, **kw)
+        s = w / f"s9-{label}"
+        tbl = _table(w, jobs)
+        benv = {**os.environ, RESTARTED_ENV: c2} if guard else None
+        r = _beat(repo / "tools" / "audit" / "seat" / "beatd.py", "run", "--state", s,
+                  "--jobs", tbl, "--repo", repo, *(["--once"] if once else ["--for", for_s]),
+                  env=benv, timeout=60)
+        starts = [ln.split()[4].split("=", 1)[1] for ln in _jr(s) if ln.startswith("START ")]
+        return r, g, c1, c2, starts, _jr(s)
+
+    fast = [_job("a", ["/usr/bin/true"], interval_s=3600), _job("b", ["/usr/bin/true"], interval_s=3600)]
+    on_path = {"tools/audit/seat/zz.txt": "z\n"}
+    r, g, c1, c2, starts, _ = beat("behind", on_path, fast[:1])
+    res["behind on the seat paths and idle: checks out origin/main and re-execs"] = (
+        r.returncode == 0 and starts == [c1, c2] and g("rev-parse", "HEAD") == c2
+        and g("symbolic-ref", "--short", "HEAD") == "main" and "BEAT-RESTART" in r.stdout)
+    r, g, c1, c2, starts, _ = beat("guard", on_path, fast, guard=True)
+    res["the guard: already restarted to this origin/main refuses with its why"] = (
+        starts == [c1] and g("rev-parse", "HEAD") == c1
+        and f"restarted once to {c2[:12]} and still behind" in r.stdout)
+    r, g, c1, c2, starts, _ = beat("once", on_path, fast[:1], once=True)
+    res["--once never restarts"] = r.returncode == 0 and starts == [c1] and g("rev-parse", "HEAD") == c1
+    mod = _load(prog)
+    gate_s, mark = w / "s9-gate", w / "s9-gate-ran"
+    (gate_s / "beatd").mkdir(parents=True)
+    gb = mod.Beat(gate_s, {"class_wait_s": 60, "jobs": []}, w,
+                  resolve_git(os.environ.get("PATH", "")))
+    gb.once = True
+    gb.restart = "c" * 40
+    gb.run_one(_job("t", ["/usr/bin/touch", str(mark)]))
+    blocked = not mark.exists() and not _jr(gate_s)
+    gb.restart = None
+    gb.run_one(_job("t", ["/usr/bin/touch", str(mark)]))
+    res["once a restart is taken no job instance starts"] = blocked
+    res["null: with no restart taken the same job runs"] = mark.exists() and len(_passes(gate_s, "t")) == 1
+    r, g, c1, c2, starts, _ = beat("pr", {"tools/pr/zz.sh": "z\n"}, fast[:1])
+    res["behind on tools/pr alone restarts too"] = starts == [c1, c2]
+    r, g, c1, c2, starts, _ = beat("offpath", {"docs/zz.md": "z\n"}, fast[:1])
+    res["null: behind only off the seat paths does not restart"] = (
+        r.returncode == 0 and starts == [c1] and g("rev-parse", "HEAD") == c1
+        and "BEAT-RESTART" not in r.stdout and "NO-RESTART" not in r.stdout)
+    slow = [_job("fast", ["/usr/bin/true"], interval_s=3600),
+            _job("slow", ["/bin/sleep", "2"], interval_s=3600)]
+    r, g, c1, c2, starts, jr = beat("running", on_path, slow, for_s="5")
+    slow_pass = next((i for i, ln in enumerate(jr) if ln.startswith("PASS ") and " slow " in ln), -1)
+    second = [i for i, ln in enumerate(jr) if ln.startswith("START ")][1:2]
+    res["a running instance defers the restart to the next pass"] = (
+        "NO-RESTART" in r.stdout and "a job instance is running: slow" in r.stdout
+        and starts == [c1, c2] and slow_pass >= 0 and second and second[0] > slow_pass)
+    for label, kw, adds, why in (
+            ("dirty", {"dirty": True}, on_path, "the tree is dirty"),
+            ("local", {"local": True}, on_path, "1 commit(s) not on origin/main"),
+            ("broken", {}, {"tools/audit/seat/beatd.py": "def (\n"},
+             "origin/main's tools/audit/seat/beatd.py does not compile")):
+        r, g, c1, c2, starts, _ = beat(label, adds, fast, **kw)
+        res[f"{label}: refuses with its why"] = (
+            r.returncode == 0 and len(starts) == 1 and g("rev-parse", "HEAD") != c2
+            and f"NO-RESTART behind=1 " in r.stdout and why in r.stdout)
+        res[f"{label}: a refusal persisting into a second pass prints BEAT-STALE"] = (
+            sum(ln.startswith("BEAT-STALE ") and why in ln for ln in r.stdout.splitlines()) >= 1)
+    return res
+
+
 CASES = {"1": case1, "2": case2, "3": case3, "4": case4, "5": case5, "6": case6,
-         "6b": case6_beat, "7": case7, "7c": case7_cli, "8": case8}
+         "6b": case6_beat, "7": case7, "7c": case7_cli, "8": case8, "9": case9}
 
 # One predicate change per case: (file, anchor, replacement, case, the check it must break).
 MUTANTS = {
@@ -1210,6 +1408,37 @@ MUTANTS = {
     "m7_dead_running_kept": (
         "beatd", "        running.clear()  # no beat", "        pass  # no beat", "7",
         "a RUNNING line with no PASS under a free beatd.lock is a dead instance"),
+    "m9_paths_unfiltered": (
+        "beatd", '"HEAD..origin/main", "--", *SEAT_PATHS)', '"HEAD..origin/main")', "9",
+        "null: behind only off the seat paths does not restart"),
+    "m9_guard_off": (
+        "beatd", "elif os.environ.get(RESTARTED_ENV) == new:", "elif False:", "9",
+        "the guard: already restarted to this origin/main refuses with its why"),
+    "m9_dirty_ignored": (
+        "beatd", 'elif self.g(top, "status", "--porcelain", "--untracked-files=no").stdout.strip():',
+        "elif False:", "9", "dirty: refuses with its why"),
+    "m9_local_commit_ignored": (
+        "beatd", '.stdout.strip()) != "0":', '.stdout.strip()) == "never":', "9",
+        "local: refuses with its why"),
+    "m9_compile_unchecked": (
+        "beatd", '                    compile(src.stdout, "beatd.py", "exec")\n', "                    pass\n",
+        "9", "broken: refuses with its why"),
+    "m9_running_ignored": (
+        "beatd", "if why is None and self.active:", "if False:", "9",
+        "a running instance defers the restart to the next pass"),
+    "m9_stale_never": (
+        "beatd", "if self.stale_n >= 2:", "if self.stale_n >= 3:", "9",
+        "dirty: a refusal persisting into a second pass prints BEAT-STALE"),
+    "m9_no_exec": (
+        "beatd", "    if beat.restart:  # in place", "    if False:  # in place", "9",
+        "behind on the seat paths and idle: checks out origin/main and re-execs"),
+    "m9_once_restarts": (
+        "beatd", "        if not self.once:\n            self.fresh()", "        if True:\n            self.fresh()",
+        "9", "--once never restarts"),
+    "m9_no_start_gate": (
+        "beatd", "            if self.restart:\n                return  # a restart was taken",
+        "            if False:\n                return  # a restart was taken", "9",
+        "once a restart is taken no job instance starts"),
     "m8_held_always_free": (
         "beatd", "        return lock_pid(path) or 0\n", "        return None\n", "8",
         "held: rc 0 while held"),
diff --git a/tools/audit/seat/open_driver.py b/tools/audit/seat/open_driver.py
index 78fb52629b..52351648b3 100644
--- a/tools/audit/seat/open_driver.py
+++ b/tools/audit/seat/open_driver.py
@@ -10,8 +10,13 @@ A pass reads the board's `OWED <utc> handoff-no-pr refs/heads/handoff/<topic>
 orders the rest, and launches `open_pr.sh` detached for as many as the cap
 allows. The OPEN arm only: cloud_relay.sh's handoff arm owns update_pr.sh.
 
-SKIPPED (`SKIP <topic> <sha8> <reason>`): `moved` (origin's handoff tip is not
-the board's sha), `no-body` (no handoff-body/<topic>), `landed` (`ledger.py
+LIVE TIP (OPENER-LIVE-TIP, P603): the board is rewritten once per relay pass,
+so its sha can lag origin. When origin's handoff tip differs from the board's
+sha, the pass logs `RETIP <topic> <board sha8> -> <tip sha8>` and runs every
+check below, and the open, at the live tip; `ct` stays the board line's.
+
+SKIPPED (`SKIP <topic> <sha8> <reason>`): `moved` (origin has no handoff ref
+for the topic), `no-body` (no handoff-body/<topic>), `landed` (`ledger.py
 landed`, the classifier cloud_relay.sh and bus.sh orphans use), `fix-branch`
 (fix/<topic> or fix/<topic>-pr exists), `seen` (opened at this sha), `live`
 (its run is still going), `backoff` (a failed open waiting its turn), `stuck` (three
@@ -54,7 +59,7 @@ fewer than three runs have failed every pass prints
 regex reads the `STUCK ` prefix). A new sha is a new key and starts fresh.
 Per-topic files are `t-<stem>.log`/`.rc`, so no topic name can equal
 `open-driver.log`; `stem` escapes `%` before `/` so two topics never share a stem.
-Log lines: START / RESULT rc=<n> / SKIP / NEEDS-TITLE / STARVED.
+Log lines: START / RESULT rc=<n> / SKIP / RETIP / NEEDS-TITLE / STARVED.
 """
 from __future__ import annotations
 
@@ -273,9 +278,13 @@ def run_pass(board: str, world, sd: Path, now: float, out=print) -> dict:
         def skip(why):
             skipped[topic] = why
             log(f"SKIP {topic} {sha[:8]} {why}")
+        live_tip = tips.get(f"refs/heads/handoff/{topic}")
+        if live_tip and live_tip != sha:  # the board lags a relay pass: check and open origin's live tip (P603)
+            log(f"RETIP {topic} {sha[:8]} -> {live_tip[:8]}")
+            sha = live_tip
         if topic.startswith(SKIP_TOPIC_PREFIXES):  # mut:optopicskip
             skip("batched")  # triage and roster changes wait and merge together with stamps (tvofi 2026-11-04)
-        elif tips.get(f"refs/heads/handoff/{topic}") != sha:
+        elif live_tip is None:
             skip("moved")
         elif f"refs/heads/handoff-body/{topic}" not in tips:
             skip("no-body")
diff --git a/tools/audit/seat/open_driver_selftest.py b/tools/audit/seat/open_driver_selftest.py
index c3ba502157..7e06d2e344 100644
--- a/tools/audit/seat/open_driver_selftest.py
+++ b/tools/audit/seat/open_driver_selftest.py
@@ -212,9 +212,22 @@ def run():
     sd, w = world(upd, heads=heads)
     go(sd, w, upd)
     check("null: handoff-update / body line ignored", w.launched == [])
+    # OPENER-LIVE-TIP (P603): the board is rewritten once per relay pass, so a
+    # line can name a handoff sha origin has since moved past. The candidate
+    # checks re-run at origin's live tip; only an absent tip is `moved`.
     sd, w = world("", heads=[("r10-cp", sha("2"))])
     go(sd, w, line("r10-cp", sha("7")))
-    check("moved handoff skipped", w.launched == [])
+    check("live tip: a board line at A with origin's clean tip B opens at B",
+          len(w.launched) == 1 and od._load(sd / "open-driver" / "runs.json", {}).get("r10-cp", {}).get("sha") == sha("2")
+          and f"RETIP r10-cp {sha('7')[:8]} -> {sha('2')[:8]}" in out and not any(o.startswith("SKIP") for o in out))
+    sd, w = world("", heads=[("r10-cp", sha("2"))], landed={sha("2")})
+    go(sd, w, line("r10-cp", sha("7")))
+    check("live tip: the checks run at B, so a landed B is skipped landed, never opened",
+          w.launched == [] and out[-1] == f"SKIP r10-cp {sha('2')[:8]} landed")
+    sd, w = world("", heads=[])
+    go(sd, w, line("r10-cp", sha("7")))
+    check("null: a line whose handoff ref is gone still prints SKIP moved",
+          w.launched == [] and out == [f"SKIP r10-cp {sha('7')[:8]} moved"])
     for tp in ("triage-s9-batch4", "roster-carry-fold"):
         sd, w = world("", ros=roster("ROSTER-CARRY-FOLD", "R10-TRIAGE-S9"), heads=[(tp, sha("2"))])
         go(sd, w, line(tp, sha("2")))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
