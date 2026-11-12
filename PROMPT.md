CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-mutant-run-darwin, at head 6e100ef6980216a81eaa0438bdc215d62b19271f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 6e100ef6980216a81eaa0438bdc215d62b19271f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-mutant-run-darwin before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-mutant-run-darwin, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-hotfix-mutant-run-darwin, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-mutant-run-darwin <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-mutant-run-darwin; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-mutant-run-darwin`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-mutant-run-darwin and refs/heads/handoff-wip/r10-hotfix-mutant-run-darwin-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
HOTFIX. Since #3475 (merge d655c4a8) tools/audit/seat/mutant_run.py reads /proc, which macOS lacks: os.listdir of /proc in family() (near line 134) and in _reap() (near line 158) raise FileNotFoundError, every run exits 1, and the prepr self-test fails five checks, which blocks every full-prepr open and update on the macOS host. Fix: failing test first, a self-test case that runs family() and _reap() with /proc absent (for example a patched listdir raising FileNotFoundError), red at main and green after. When /proc is absent build the process table from ps -axo pid=,ppid=,pgid=,stat= with the session from os.getsid, and _reap() skips. The four fork-cap self-test cases that need a subreaper or another process environment (chain leaves its session / cleans its env at every link) are skipped on a host without /proc WITH a printed line naming each skipped case and why, never silently. mutant_run.py --self-test and the three mutants_line fixtures in tools/pr/prepr.sh (around lines 2388-2412) must pass on Linux and with /proc absent. Update the instrument doc line in tools/audit/seat/instruments/mutant_run.py.md. Candidate patch, a starting point you must verify and not trust:
diff --git a/tools/audit/seat/mutant_run.py b/tools/audit/seat/mutant_run.py
index f47dac0b3d..b63be00d77 100644
--- a/tools/audit/seat/mutant_run.py
+++ b/tools/audit/seat/mutant_run.py
@@ -131,6 +131,25 @@ def family(sid: int, token: str, skip: frozenset = frozenset(), root: int = 0) -
     had before the command). The ppid leg is the one a descendant cannot leave: setsid, setpgid,
     a cleared environment and an exited parent all keep it under `root`. Zombies are not counted."""
     me, mark, kids, out = os.getpid(), ("MUTANT_RUN_TOKEN=" + token).encode(), {}, set()
+    if not os.path.isdir("/proc"):  # macOS/BSD: no procfs; the ps table carries ppid/pgid, os.getsid the session
+        rows = subprocess.run(["ps", "-axo", "pid=,ppid=,pgid=,stat="], capture_output=True, text=True).stdout
+        for line in rows.splitlines():
+            try:
+                pid, ppid, pgrp, state = line.split()[:4]
+                if int(pid) == me or state.startswith("Z"):
+                    continue
+                kids.setdefault(int(ppid), []).append(int(pid))
+                if sid and (sid == int(pgrp) or sid == os.getsid(int(pid))):
+                    out.add(int(pid))
+            except (OSError, ValueError):
+                continue
+        todo, seen = ([c for c in kids.get(root, []) if c not in skip] if root else []), set()
+        while todo:
+            pid = todo.pop()
+            if pid not in seen:
+                seen.add(pid)
+                todo.extend(kids.get(pid, []))
+        return sorted(out | seen)
     for d in os.listdir("/proc"):
         if not d.isdigit() or int(d) == me:
             continue
@@ -156,7 +175,7 @@ def family(sid: int, token: str, skip: frozenset = frozenset(), root: int = 0) -
 def _reap(skip: frozenset, keep: int) -> None:
     """Collect the exit status of every orphan reparented to this subreaper (children not in
     `skip` and not the command `keep`, which Popen waits for), so dead ones leave no zombie."""
-    for d in os.listdir("/proc"):
+    for d in (os.listdir("/proc") if os.path.isdir("/proc") else []):
         try:
             pid = int(d)
             stat = Path("/proc", d, "stat").read_text()

PR body answers the red-check trigger: the cheaper detector is a no-/proc self-test case in CI. Mutation proof and a null control (Linux path unchanged with /proc present) as the fixer contract requires.
Entities trap: a new tracked file must be classified in a closure or on the INERT list of tests/closure.py.
