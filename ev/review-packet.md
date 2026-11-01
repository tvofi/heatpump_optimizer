# Review packet #3151
head: 1a6a7e6a8bf1cbe04f37989aaedbab66165df624
base: f04b25a005f51b9df48154a6544c03e6873ed9de

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124984851087 neutral
arch-score / arch-score id=124984685887 success
arm id=124984165568 skipped
budget-raise-gate / budget-raise-gate id=124984686080 success
cancel-superseded id=124984169131 success
codeql / Analyze (actions) id=124984685792 success
codeql / Analyze (javascript-typescript) id=124984685797 success
codeql / Analyze (python) id=124984685826 in_progress
governance / delivery-status id=124984685947 failure
governance / delivery-status-publish id=124984687578 skipped
governance / env-matrix id=124984685825 in_progress
governance / instrument-self-tests id=124984685996 in_progress
governance / policy-docs id=124984685927 in_progress
governance / record id=124984687226 skipped
governance / wave-script id=124984685955 success
hassfest / hassfest id=124984686116 success
kernel-points id=124984687618 skipped
prelude id=124984169030 in_progress
refresh id=124984169247 success
tests / arch-instrument id=124984937088 success
tests / briefs id=124984685791 success
tests / browser id=124984936969 in_progress
tests / closure-scope id=124984685898 success
tests / closures id=124984937056 in_progress
tests / coverage id=124984936994 in_progress
tests / fast (3.14) id=124984936997 in_progress
tests / mutation id=124984686043 success
tests / mutation-autofix id=124985199299 skipped
tests / mutation-pins id=124985198912 skipped
tests / nightly-ha id=124984938022 skipped
tests / nightly-status id=124984685916 success
tests / replay id=124984938770 skipped
tests / typing id=124984936998 success
validate / validate-hacs id=124984685900 success

## Refusals
red-unanswered: concluded red check `governance / delivery-status` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/mutant_run.py --self-test
             `tools/audit/seat/mutant_run.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/features_block.py --self-test
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/mutant_run.py --diff origin/main...HEAD --path tools/audit/seat/mutant_run.py --cmd 'python3 -I tools/audit/seat/mutant_run.py --self-test' --report-only
             `tools/audit/seat/mutant_run.py` is in the tree at this head

FIGURES: 5 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 12d078077..11d2ee0cc 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -636,6 +636,13 @@ jobs:
           python3 -I tools/audit/seat/features_block.py --self-test | tee "$RUNNER_TEMP/features-block-self-test.txt"
           grep -Eq '^features_block self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/features-block-self-test.txt"
 
+      - name: Show the mutant driver killing, sparing and restoring its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          python3 -I tools/audit/seat/mutant_run.py --self-test | tee "$RUNNER_TEMP/mutant-run-self-test.txt"
+          grep -Eq '^mutant_run self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/mutant-run-self-test.txt"
+
       - name: Show the handoff push and its row writer refusing their own fixtures
         if: ${{ !cancelled() }}
         run: |
diff --git a/dev/programme/delivery/3151.md b/dev/programme/delivery/3151.md
new file mode 100644
index 000000000..5a4470f8f
--- /dev/null
+++ b/dev/programme/delivery/3151.md
@@ -0,0 +1 @@
+- [#3151](https://github.com/tvofi/heatpump_optimizer/pull/3151) — **open**, R10-MUTANT-RUN-DRIVER: mutant run driver (R10-MUTANT-RUN-DRIVER)
diff --git a/tests/closures.json b/tests/closures.json
index 0875150fc..66c87c298 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3813,10 +3813,12 @@
    "tools/audit/seat/ci_probe.py",
    "tools/audit/seat/cloud_dispatch.py",
    "tools/audit/seat/daemonize.py",
+   "tools/audit/seat/features_block.py",
    "tools/audit/seat/flow_metrics.py",
    "tools/audit/seat/gh_calls.py",
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
+   "tools/audit/seat/mutant_run.py",
    "tools/audit/seat/orchestrator_tick.py",
    "tools/audit/seat/owed_unactioned.py",
    "tools/audit/seat/plan_audit.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 935f13a2a..0db6dd6d5 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -45,7 +45,8 @@ have a contract: `dev/governance/roles/standing-tick.md` (the tick board),
 `dev/governance/roles/standing-roster.md` (roster ops). `pulse.py` and the
 sweep's standing-seat liveness step keep them alive.
 
-- [`features_block.py`](instruments/features_block.py.md) — runs one block of `tests/features.py`
+- [`features_block.py`](instruments/features_block.py.md) — runs one block of `tests/features.py`, or the script through a marker
+- [`mutant_run.py`](instruments/mutant_run.py.md) — applies spec mutants or the diff's added lines one at a time to a git-archive copy and prints KILLED or SURVIVED
 - [`body_push.sh`](instruments/body_push.sh.md) — publishes a handoff's BODY.md on the orphan ref `handoff-body/<topic>` (plus RESUME.md), parentless first commit, fast-forwards after
 - [`body_patch.sh`](instruments/body_patch.sh.md) — repairs an open pull request's BODY, or any pull request's TITLE (`--title`), without moving its head
 - [`autofix_statuses.sh`](instruments/autofix_statuses.sh.md) — re-derives what `mutation-autofix` and `closures-autofix` answered on recent pull-request runs
diff --git a/tools/audit/seat/features_block.py b/tools/audit/seat/features_block.py
index f7d1a2d74..c81e9118c 100755
--- a/tools/audit/seat/features_block.py
+++ b/tools/audit/seat/features_block.py
@@ -1,7 +1,8 @@
 #!/usr/bin/env python3
 """Run one block of tests/features.py, from a marker line to the next block.
 
-    python3 tools/audit/seat/features_block.py "<first line of the block>" [END]
+    python3 tools/audit/seat/features_block.py [--prelude 'import line']... "<first line of the block>" [END]
+    python3 tools/audit/seat/features_block.py [--prelude 'import line']... --through "<marker line>"
 
 features.py runs every block in one process, which takes tens of minutes on a
 loaded seat; a mutation proof needs only the block that pins the mutated line.
@@ -12,6 +13,11 @@ pointing at features.py, so path arithmetic inside the block resolves as in
 the full run. Exit status is the block's ``R.close``: 0 when every check passed.
 Run from the repository root under the CI venv.
 
+``--prelude`` (repeatable) runs one line, typically an import an earlier block
+made, before the block. ``--through MARKER`` takes no block: it runs the whole
+script from the top up to the line holding MARKER, the state every earlier
+block builds, and exits with that prefix's ``R.close``.
+
 ``--self-test`` runs offline: it executes a two-check block it writes itself.
 """
 from __future__ import annotations
@@ -28,7 +34,13 @@ def block(source: str, start: str, end: str = CLOSE) -> str:
     return source[i:source.index(end, i)]
 
 
-def run(path: str, start: str, end: str = CLOSE) -> int:
+def through(source: str, marker: str) -> str:
+    """The script from the header's end up to the line holding ``marker``."""
+    i = source.rindex("\n", 0, source.index(marker)) + 1
+    return source[source.index('R = Results("Feature modules")'):i]
+
+
+def run(path: str, start: str | None, end: str = CLOSE, prelude: tuple = (), upto: str | None = None) -> int:
     root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
     sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
     source = open(path, encoding="utf-8").read()
@@ -36,20 +48,89 @@ def run(path: str, start: str, end: str = CLOSE) -> int:
     ns: dict = {"__file__": os.path.abspath(path), "__name__": "features_block"}
     exec(compile(header, path, "exec"), ns)
     exec(compile('R = Results("features block")', path, "exec"), ns)
+    for line in prelude:
+        exec(compile(line, f"{path}[prelude]", "exec"), ns)
+    if upto is not None:
+        exec(compile(through(source, upto), f"{path}[through]", "exec"), ns)
+        return ns["R"].close("FEATURES THROUGH")
     exec(compile(block(source, start, end), f"{path}[block]", "exec"), ns)
     return ns["R"].close("FEATURES BLOCK")
 
 
 def _self_test() -> int:
+    import shutil
+    import tempfile
+    results = []
+
+    def check(name: str, ok: bool) -> None:
+        results.append(ok)
+        print(("  ok  " if ok else "  FAIL") + " " + name)
+
     src = "a\n# start here\nx = 1\n# next\n" + CLOSE + "\n"
-    ok = block(src, "start here") == "# start here\nx = 1\n# next\n"
-    ok = ok and block(src, "start here", "# next") == "# start here\nx = 1\n"
-    print(("  ok  " if ok else "  FAIL") + " a block runs from its marker line to the close")
-    print(f"features_block self-test: 1 checks, {0 if ok else 1} failed")
-    return 0 if ok else 1
+    check("a block runs from its marker line to the close",
+          block(src, "start here") == "# start here\nx = 1\n# next\n"
+          and block(src, "start here", "# next") == "# start here\nx = 1\n")
+    fake = (
+        "class Results:\n"
+        "    def __init__(self, name): self.bad = 0\n"
+        "    def close(self, name): return self.bad\n"
+        'R = Results("Feature modules")\n'
+        "seed = 5\n"
+        "# first block\n"
+        "R.bad += seed != 5\n"
+        "# second block\n"
+        "R.bad += math.floor(2.5) != 2\n"
+        + CLOSE + "\n")
+    check("through stops before the marker line", through(fake, "second block").endswith("R.bad += seed != 5\n")
+          and "math" not in through(fake, "second block"))
+    tmp = tempfile.mkdtemp(prefix="fblock-")
+    try:
+        os.makedirs(os.path.join(tmp, "tests"))
+        path = os.path.join(tmp, "tests", "features.py")
+        open(path, "w").write(fake)
+        check("a block needing an import an earlier block made fails without --prelude",
+              _expect_error(lambda: run(path, "second block"), NameError))
+        check("--prelude supplies that import and the block passes", run(path, "second block", prelude=("import math",)) == 0)
+        check("--through runs the prefix and the state it builds, no block", run(path, None, upto="second block") == 0)
+        check("_main: a block with --prelude passes", _main(["--prelude", "import math", "second block"], path) == 0)
+        check("_main: --through takes the marker and no block", _main(["--through", "second block"], path) == 0)
+        check("_main: --through with a block, or no argument, is a usage error, rc 2",
+              _main(["--through", "second block", "first block"], path) == 2 and _main([], path) == 2)
+        bad = fake.replace("seed = 5", "seed = 6")
+        open(path, "w").write(bad)
+        check("--through reports the prefix's own failure (null control)", run(path, None, upto="second block") == 1)
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    failed = results.count(False)
+    print(f"features_block self-test: {len(results)} checks, {failed} failed")
+    return 1 if failed else 0
+
+
+def _expect_error(fn, exc) -> bool:
+    try:
+        fn()
+    except exc:
+        return True
+    return False
+
+
+def _main(argv: list[str], path: str = "tests/features.py") -> int:
+    prelude, upto, pos = [], None, []
+    it = iter(argv)
+    for a in it:
+        if a == "--prelude":
+            prelude.append(next(it, ""))
+        elif a == "--through":
+            upto = next(it, None)
+        else:
+            pos.append(a)
+    if upto is not None and pos or upto is None and not pos:
+        print(__doc__)
+        return 2
+    return run(path, pos[0] if pos else None, *pos[1:2], prelude=tuple(prelude), upto=upto)
 
 
 if __name__ == "__main__":
     if sys.argv[1:2] == ["--self-test"]:
         sys.exit(_self_test())
-    sys.exit(run("tests/features.py", *sys.argv[1:3]))
+    sys.exit(_main(sys.argv[1:]))
diff --git a/tools/audit/seat/instruments/features_block.py.md b/tools/audit/seat/instruments/features_block.py.md
index 9a65a2803..ee0b97a2f 100644
--- a/tools/audit/seat/instruments/features_block.py.md
+++ b/tools/audit/seat/instruments/features_block.py.md
@@ -6,3 +6,7 @@
   block pinning the mutated line, on a seat where the whole script takes tens
   of minutes. Refusal: a marker that is not in the script raises rather than
   running an empty block.
+  `--prelude 'import line'` (repeatable) runs one line before the block, the
+  import an earlier block made; `--through MARKER` runs the script from the top
+  up to the marker line instead of a block, the state every earlier block
+  builds. `--self-test` runs offline over a features file it writes itself.
diff --git a/tools/audit/seat/instruments/mutant_run.py.md b/tools/audit/seat/instruments/mutant_run.py.md
new file mode 100644
index 000000000..5fd4ea7a5
--- /dev/null
+++ b/tools/audit/seat/instruments/mutant_run.py.md
@@ -0,0 +1,21 @@
+# `mutant_run.py`
+
+- `mutant_run.py` — the tracked mutant driver. `--spec mutants.json --cmd
+  '<argv>'` takes a list of {name, file, old, new}, runs an automatic NULL
+  mutant first (it must print `SURVIVED NULL`; `KILLED NULL` is a broken
+  command, rc 3) and prints one `KILLED|SURVIVED name` line per mutant.
+  `--diff <base>...HEAD --cmd '<argv>'` mutates the ADDED Python lines with
+  GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL and CONST_SWAP, and prints one
+  `SURVIVED file:line OPERATOR` line per survivor (rc 1; `--report-only` rc 0;
+  `--max-mutants N` caps the pass; `--list` prints the mutants without running).
+  Mutants run in a `git archive` copy by default (`--copy-tree`), so a kill
+  cannot leave production mutated; `--in-place` writes into the working tree
+  under `dev/audit/harnesses/mutant_guard.py` for a command the #363
+  `recorded_at` check would fail in a copy. SIGTERM and SIGINT kill the
+  command's process group and restore. When: a mutation proof over several
+  mutants, or a fixer checking that the group's self-test pins the lines the
+  diff adds; `tools/pr/prepr.sh` runs the diff arm report-only when
+  `MUTANT_CMD` is set. Refusal, rc 2, before anything runs: a malformed spec, a
+  repeated name, an `old` not occurring exactly once, a target differing from
+  HEAD. A survivor is answered in the PR body; an equivalent one still owes a
+  `survivor_triage` record. `--self-test` builds throwaway repositories.
diff --git a/tools/audit/seat/mutant_run.py b/tools/audit/seat/mutant_run.py
new file mode 100644
index 000000000..6959b1265
--- /dev/null
+++ b/tools/audit/seat/mutant_run.py
@@ -0,0 +1,603 @@
+#!/usr/bin/env python3
+"""The tracked mutant driver: apply one textual edit, run a command, restore.
+
+    python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd '<argv>' [--copy-tree | --in-place]
+    python3 tools/audit/seat/mutant_run.py --diff <base>...HEAD --cmd '<argv>' [--max-mutants N] [--report-only] [--list]
+    python3 -I tools/audit/seat/mutant_run.py --self-test
+
+SPEC MODE. `mutants.json` is a list of {name, file, old, new}. An automatic
+NULL mutant with no edit runs first and must be reported SURVIVED: a command
+that fails on the unedited tree kills every mutant for the wrong reason, so
+`KILLED NULL` ends the run at rc 3 before any mutant is applied. One
+`KILLED name` or `SURVIVED name` line per mutant (a non-zero command exit
+kills). Refusals, rc 2, before anything runs: a spec entry that is malformed,
+a name used twice or named NULL, an `old` that does not occur exactly once in
+its file, and a target file that differs from HEAD.
+
+WHERE IT RUNS. By default in a `git archive` copy of the tree, so a kill cannot
+leave production mutated; `--copy-tree` names that default. The #363
+`recorded_at` check fails in a copy on every mutant, baseline included, so a
+command that reaches it needs `--in-place`: the mutant is written into the
+working tree under `dev/audit/harnesses/mutant_guard.py`, which refuses a
+target that differs from HEAD and restores it under SIGTERM, SIGINT and exit.
+Under either mode a signal kills the running command's process group first.
+
+DIFF MODE (R10-MUTANT-RUN-DRIVER, card 4). `--diff base...HEAD` reads the
+ADDED lines of the Python files the three-dot diff touches (not under tests/ or
+dev/, not inside a multi-line string) and mutates each with five operators:
+
+  GUARD_OFF   `if cond:` / `elif cond:` becomes `if False:`
+  RETURN_DEL  `return ...` becomes `pass`
+  CMP_BOUND   the first of < <= > >= moves one step (< to <=, >= to >)
+  CALL_DEL    a bare `f(...)` statement becomes `pass` (print and _LOGGER calls
+              are left alone: they pin no behaviour)
+  CONST_SWAP  the first number moves (n to n+1, 0.0 to 1.0) or, with none,
+              the first True/False flips
+
+A mutant that does not compile is skipped. The command runs once unedited (rc 3
+`BASELINE FAILS` if it fails: nothing is then readable) and once per mutant;
+one `SURVIVED file:line OPERATOR  <mutated line>` line is printed per survivor
+and nothing for a kill. rc 0 when nothing survived (an empty diff included),
+1 on survivors unless `--report-only`. A survivor is answered in the PR body;
+an equivalent one still needs a survivor_triage record. `--list` prints the
+mutants without running. The command is the group's named self-test or
+`python3 tools/audit/seat/features_block.py "<marker>"`.
+
+`--self-test` builds throwaway repositories and runs every arm above.
+"""
+from __future__ import annotations
+
+import argparse
+import ast
+import json
+import os
+import re
+import shlex
+import shutil
+import signal
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[3]
+REFUSE_RC, SURVIVE_RC, BROKEN_RC = 2, 1, 3
+OPERATORS = ("GUARD_OFF", "RETURN_DEL", "CMP_BOUND", "CALL_DEL", "CONST_SWAP")
+SKIP_PREFIXES = ("tests/", "dev/")
+_STR = re.compile(r"""("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')""")
+_CMP = re.compile(r"(?<![<>=!\-])(<=|>=|<|>)(?![<>=])")
+_NUM = re.compile(r"(?<![\w.])(\d+\.\d+|\d+)(?![\w.])")
+_BOOL = re.compile(r"\b(True|False)\b")
+_CALL = re.compile(r"^(?:await\s+)?[A-Za-z_][\w.]*\(.*\)$")
+_BOUND = {"<": "<=", "<=": "<", ">": ">=", ">=": ">"}
+
+_child: list = []  # the running command, for the signal handler
+
+
+class Refusal(Exception):
+    pass
+
+
+def git(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
+    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=text)
+
+
+# --- running one command ----------------------------------------------------
+def run_cmd(argv: list[str], cwd: Path, timeout: float) -> int:
+    """Exit status of the command; a timeout is -1 (a kill: the mutant hangs)."""
+    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
+    p = subprocess.Popen(argv, cwd=str(cwd), env=env, start_new_session=True,
+                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
+    _child.append(p)
+    try:
+        return p.wait(timeout=timeout)
+    except subprocess.TimeoutExpired:
+        _killpg(p)
+        p.wait()
+        return -1
+    finally:
+        _child.clear()
+
+
+def _killpg(p) -> None:
+    try:
+        os.killpg(p.pid, signal.SIGKILL)
+    except (ProcessLookupError, PermissionError):
+        pass
+
+
+class Workspace:
+    """Where mutants are written: an archive copy of a tree, or the working tree under the guard."""
+
+    def __init__(self, root: Path, files: list[str], in_place: bool, rev: str = "HEAD"):
+        self.root, self.in_place = root, in_place
+        self.copy: Path | None = None
+        self.rels = sorted(set(files))
+        if in_place:
+            sys.dont_write_bytecode = True  # no __pycache__ beside the tracked guard
+            sys.path.insert(0, str(root / "dev" / "audit" / "harnesses"))
+            import mutant_guard  # noqa: PLC0415 -- the shared restore-on-kill guard
+            self.finish = mutant_guard.arm(self.rels, root=root)
+            self.dir = root
+        else:
+            dirty = [r for r in self.rels if git(root, "diff", "--quiet", "HEAD", "--", r).returncode]
+            if dirty and rev == "HEAD":
+                raise Refusal("target differs from HEAD (a copy would test HEAD, not the edit): " + ", ".join(dirty))
+            self.copy = Path(tempfile.mkdtemp(prefix="mutant_run-"))
+            arc = subprocess.Popen(["git", "-C", str(root), "archive", rev], stdout=subprocess.PIPE)
+            tar = subprocess.run(["tar", "-x", "-C", str(self.copy)], stdin=arc.stdout, capture_output=True)
+            arc.stdout.close()
+            if arc.wait() or tar.returncode:
+                self.close()
+                raise Refusal("git archive of " + rev + " failed")
+            self.dir = self.copy
+        prev = {sg: signal.getsignal(sg) for sg in (signal.SIGTERM, signal.SIGINT)}
+
+        def on_signal(signum, frame):
+            for p in _child:
+                _killpg(p)
+            self.close()
+            h = prev[signum]
+            if callable(h):
+                h(signum, frame)  # the guard restores in place and exits 128+signal
+            os._exit(128 + signum)
+
+        for sg in prev:
+            signal.signal(sg, on_signal)
+
+    def path(self, rel: str) -> Path:
+        return self.dir / rel
+
+    def close(self) -> None:
+        if self.copy is not None:
+            shutil.rmtree(self.copy, ignore_errors=True)
+            self.copy = None
+
+    def apply(self, rel: str, text: str, run: list[str], timeout: float) -> int:
+        """Write `text` over `rel`, run, put the original bytes back."""
+        target = self.path(rel)
+        orig = target.read_bytes()
+        try:
+            target.write_text(text, encoding="utf-8")
+            return run_cmd(run, self.dir, timeout)
+        finally:
+            target.write_bytes(orig)
+
+
+# --- spec mode -------------------------------------------------------------
+def load_spec(path: str, root: Path) -> list[dict]:
+    try:
+        spec = json.loads(Path(path).read_text(encoding="utf-8"))
+    except (OSError, ValueError) as e:
+        raise Refusal(f"spec unreadable: {e}")
+    if not isinstance(spec, list):
+        raise Refusal("spec is not a list")
+    seen = {"NULL"}
+    for i, m in enumerate(spec):
+        if not isinstance(m, dict) or set(m) != {"name", "file", "old", "new"} \
+                or not all(isinstance(v, str) for v in m.values()):
+            raise Refusal(f"spec entry {i} is not {{name, file, old, new}} strings")
+        if m["name"] in seen:
+            raise Refusal(f"mutant name {m['name']!r} is used twice or is NULL")
+        seen.add(m["name"])
+        if not m["old"] or m["old"] == m["new"]:
+            raise Refusal(f"mutant {m['name']}: old is empty or equals new")
+        f = root / m["file"]
+        if not f.is_file():
+            raise Refusal(f"mutant {m['name']}: {m['file']} is not a file")
+        n = f.read_text(encoding="utf-8").count(m["old"])
+        if n != 1:
+            raise Refusal(f"mutant {m['name']}: old text occurs {n} times in {m['file']}, not exactly once")
+    return spec
+
+
+def run_spec(spec: list[dict], argv: list[str], ws: Workspace, timeout: float) -> int:
+    if run_cmd(argv, ws.dir, timeout) != 0:
+        print("KILLED NULL", flush=True)
+        print("mutant_run: the null mutant was killed, the command fails on the unedited tree", file=sys.stderr)
+        return BROKEN_RC
+    print("SURVIVED NULL", flush=True)
+    for m in spec:
+        text = ws.path(m["file"]).read_text(encoding="utf-8")
+        rc = ws.apply(m["file"], text.replace(m["old"], m["new"], 1), argv, timeout)
+        print(("SURVIVED " if rc == 0 else "KILLED ") + m["name"], flush=True)
+    return 0
+
+
+# --- diff mode -------------------------------------------------------------
+def added_lines(root: Path, rng: str, only: tuple = ()) -> dict[str, list[int]]:
+    r = git(root, "diff", "-U0", "--no-color", "--diff-filter=AM", rng, "--", "*.py")
+    if r.returncode:
+        raise Refusal("git diff " + rng + " failed: " + r.stderr.strip())
+    out: dict[str, list[int]] = {}
+    cur, ln = None, 0
+    for line in r.stdout.splitlines():
+        if line.startswith("+++ b/"):
+            cur = line[6:]
+            out.setdefault(cur, [])
+        elif line.startswith("@@"):
+            m = re.search(r"\+(\d+)", line)
+            ln = int(m.group(1))
+        elif cur and line.startswith("+") and not line.startswith("+++"):
+            out[cur].append(ln)
+            ln += 1
+    return {f: v for f, v in out.items() if v and not f.startswith(SKIP_PREFIXES) and (not only or f.startswith(only))}
+
+
+def string_lines(src: str) -> set[int]:
+    """Lines inside a multi-line string literal (docstrings, f-string bodies)."""
+    try:
+        tree = ast.parse(src)
+    except SyntaxError:
+        return set()
+    lines: set[int] = set()
+    for n in ast.walk(tree):
+        if isinstance(n, (ast.Constant, ast.JoinedStr)) and getattr(n, "end_lineno", None) \
+                and (isinstance(n, ast.JoinedStr) or isinstance(n.value, str)) and n.end_lineno > n.lineno:
+            lines.update(range(n.lineno, n.end_lineno + 1))
+    return lines
+
+
+def _mask(s: str) -> str:
+    return _STR.sub(lambda m: "x" * len(m.group(0)), s)
+
+
+def mutate_line(line: str):
+    """Yield (OPERATOR, mutated line) for one source line."""
+    body = line.lstrip()
+    if not body or body.startswith(("#", "import ", "from ", "def ", "class ", "@")):
+        return
+    ind = line[: len(line) - len(body)]
+    masked = _mask(line)
+    code = masked.split("#", 1)[0].rstrip()
+    mc = code.lstrip()
+    if re.match(r"(if|elif)\s", mc) and code.endswith(":"):
+        yield "GUARD_OFF", f"{ind}{mc.split(None, 1)[0]} False:"
+    if re.match(r"return\b", mc) and mc.count("(") == mc.count(")"):
+        yield "RETURN_DEL", f"{ind}pass"
+    m = _CMP.search(code)
+    if m:
+        yield "CMP_BOUND", line[: m.start()] + _BOUND[m.group(1)] + line[m.end():]
+    if _CALL.match(mc) and not mc.startswith(("print(", "_LOGGER.")) and mc.count("(") == mc.count(")"):
+        yield "CALL_DEL", f"{ind}pass"
+    m = _NUM.search(code)
+    if m:
+        tok = m.group(1)
+        new = (str(int(tok) + 1) if "." not in tok else ("1.0" if float(tok) == 0 else str(float(tok) * 2)))
+        yield "CONST_SWAP", line[: m.start()] + new + line[m.end():]
+    else:
+        m = _BOOL.search(code)
+        if m:
+            yield "CONST_SWAP", line[: m.start()] + ("False" if m.group(1) == "True" else "True") + line[m.end():]
+
+
+def diff_mutants(root: Path, rng: str, rev_root: Path, only: tuple = ()) -> list[tuple[str, int, str, str, str]]:
+    """(file, line, operator, mutated file text, mutated line) for every compiling mutant."""
+    found = []
+    for rel, nums in sorted(added_lines(root, rng, only).items()):
+        src = (rev_root / rel).read_text(encoding="utf-8")
+        lines = src.splitlines(keepends=True)
+        skip = string_lines(src)
+        for n in nums:
+            if n in skip or n > len(lines):
+                continue
+            raw = lines[n - 1]
+            eol = raw[len(raw.rstrip("\r\n")):]
+            for op, new in mutate_line(raw.rstrip("\r\n")):
+                text = "".join(lines[: n - 1]) + new + eol + "".join(lines[n:])
+                if text == src:
+                    continue
+                try:
+                    compile(text, rel, "exec")
+                except (SyntaxError, ValueError):
+                    continue
+                found.append((rel, n, op, text, new.strip()))
+    return found
+
+
+def run_diff(rng: str, argv: list[str], root: Path, in_place: bool, timeout: float,
+             limit: int, report_only: bool, list_only: bool, only: tuple = ()) -> int:
+    right = rng.split("...")[-1] if "..." in rng else "HEAD"
+    rev = right or "HEAD"
+    if "..." not in rng:
+        raise Refusal("--diff wants base...HEAD (three-dot), got " + rng)
+    if in_place and rev != "HEAD":
+        raise Refusal("--in-place mutates the working tree, whose diff end must be HEAD")
+    files = sorted(added_lines(root, rng, only))
+    if not files:
+        return 0
+    if in_place:
+        ws = Workspace(root, files, True)
+        rev_root = root
+    else:
+        ws = Workspace(root, files, False, rev=rev)
+        rev_root = ws.dir
+    try:
+        mutants = diff_mutants(root, rng, rev_root, only)
+        if limit:
+            mutants = mutants[:limit]
+        if list_only:
+            for rel, n, op, _t, new in mutants:
+                print(f"MUTANT {rel}:{n} {op}  {new}")
+            return 0
+        if not mutants:
+            return 0
+        if run_cmd(argv, ws.dir, timeout) != 0:
+            print("BASELINE FAILS: the command fails on the unedited tree; no mutant was run")
+            return BROKEN_RC
+        survivors = 0
+        for rel, n, op, text, new in mutants:
+            if ws.apply(rel, text, argv, timeout) == 0:
+                survivors += 1
+                print(f"SURVIVED {rel}:{n} {op}  {new}", flush=True)
+        return 0 if (report_only or not survivors) else SURVIVE_RC
+    finally:
+        ws.close() if not in_place else ws.finish()
+
+
+# --- entry point -----------------------------------------------------------
+def main(argv: list[str]) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
+    ap.add_argument("--spec")
+    ap.add_argument("--diff")
+    ap.add_argument("--cmd")
+    ap.add_argument("--copy-tree", action="store_true", help="the default: run in a git-archive copy")
+    ap.add_argument("--in-place", action="store_true", help="mutate the working tree under mutant_guard")
+    ap.add_argument("--root", default=str(ROOT))
+    ap.add_argument("--timeout", type=float, default=600.0)
+    ap.add_argument("--max-mutants", type=int, default=0)
+    ap.add_argument("--report-only", action="store_true")
+    ap.add_argument("--list", action="store_true")
+    ap.add_argument("--path", action="append", default=[], help="diff mode: only files under this prefix (repeatable)")
+    a = ap.parse_args(argv)
+    root = Path(a.root).resolve()
+    try:
+        if a.copy_tree and a.in_place:
+            raise Refusal("--copy-tree and --in-place exclude each other")
+        if bool(a.spec) == bool(a.diff):
+            raise Refusal("give exactly one of --spec and --diff")
+        if not a.cmd and not a.list:
+            raise Refusal("--cmd '<argv>' is required")
+        cmd = shlex.split(a.cmd or "true")
+        if a.spec:
+            spec = load_spec(a.spec, root)
+            ws = Workspace(root, [m["file"] for m in spec], a.in_place)
+            try:
+                return run_spec(spec, cmd, ws, a.timeout)
+            finally:
+                ws.close() if not a.in_place else ws.finish()
+        return run_diff(a.diff, cmd, root, a.in_place, a.timeout, a.max_mutants, a.report_only, a.list, tuple(a.path))
+    except Refusal as e:
+        print("mutant_run: refusing: " + str(e), file=sys.stderr)
+        return REFUSE_RC
+
+
+# --- self-test ---------------------------------------------------------------
+LIB = '''def clamp(x, lo, hi):
+    if x < lo:
+        return lo
+    if x > hi:
+        return hi
+    return x
+'''
+LIB2 = LIB + '''
+
+def norm(x):
+    if x < 0:
+        return 0
+    scale = 2
+    note(x)
+    return x * scale
+
+
+def note(x):
+    pass
+
+
+def label():
+    """Say it.
+
+    if x < 1:
+        return 7
+    """
+    msg = "a < b"  # c > d
+    on = True
+    return msg, on
+'''
+PINNED = ("from lib import clamp\n"
+          "assert clamp(-1, 0, 5) == 0 and clamp(9, 0, 5) == 5 and clamp(3, 0, 5) == 3\n"
+          "assert clamp(0, 0, 5) == 0 and clamp(5, 0, 5) == 5\n")
+NORM_PINNED = ("from lib import norm\nimport lib\nseen = []\nlib.note = seen.append\n"
+               "assert norm(-1) == 0 and norm(0) == 0 and norm(2) == 4 and seen == [0, 2]\n"
+               "assert lib.label() == ('a < b', True)\n")
+LOOSE = "from lib import clamp\nassert clamp(3, 0, 5) == 3\n"
+
+
+def _gone(pid: str) -> bool:
+    """True once the process `pid` no longer exists (polled for up to 5 s)."""
+    import time
+    for _ in range(50):
+        try:
+            os.kill(int(pid), 0)
+        except (ProcessLookupError, ValueError):
+            return True
+        time.sleep(0.1)
+    return False
+
+
+def _self_test() -> int:
+    import time
+    sys.path.insert(0, str(ROOT / "tests"))
+    from throwaway_git import throwaway_git_init
+    fails = checks = 0
+
+    def check(name: str, ok: bool) -> None:
+        nonlocal fails, checks
+        checks += 1
+        fails += not ok
+        print(("  ok   " if ok else "  FAIL ") + name)
+
+    tmp = Path(tempfile.mkdtemp(prefix="mutrun-st-"))
+    scratch = tmp / "tmpdir"
+    scratch.mkdir()
+    try:
+        repo = tmp / "repo"
+        repo.mkdir()
+        env = throwaway_git_init(repo, "-q", "-b", "main")
+        g = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, env=env)  # noqa: E731
+        for name, body in (("lib.py", LIB), ("check_pinned.py", PINNED), ("check_loose.py", LOOSE),
+                           ("check_norm.py", NORM_PINNED)):
+            (repo / name).write_text(body)
+        (repo / "dev" / "audit" / "harnesses").mkdir(parents=True)
+        shutil.copy(ROOT / "dev" / "audit" / "harnesses" / "mutant_guard.py", repo / "dev/audit/harnesses/mutant_guard.py")
+        (repo / "custom_components" / "heatpump_optimizer").mkdir(parents=True)
+        (repo / "custom_components/heatpump_optimizer/manifest.json").write_text("{}\n")
+        g("add", "-A")
+        g("commit", "-q", "-m", "base")
+        base = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, env=env).stdout.strip()
+        senv = dict(env, TMPDIR=str(scratch), PYTHONPATH="")
+
+        def drive(*args, sig=None, watch=None):
+            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--root", str(repo), *args],
+                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=senv, cwd=str(repo))
+            if sig:
+                for _ in range(150):
+                    if watch():
+                        break
+                    time.sleep(0.1)
+                p.send_signal(sig)
+            out, err = p.communicate(timeout=120)
+            return p.returncode, out, err
+
+        spec = tmp / "spec.json"
+
+        def write_spec(entries):
+            spec.write_text(json.dumps(entries))
+
+        bad = {"name": "ret_hi", "file": "lib.py", "old": "return lo", "new": "return hi"}
+        write_spec([bad])
+        pin = "python3 check_pinned.py"
+        rc, out, _ = drive("--spec", str(spec), "--cmd", pin)
+        check("spec: the NULL mutant reports SURVIVED and a pinned mutant KILLED",
+              rc == 0 and out.splitlines() == ["SURVIVED NULL", "KILLED ret_hi"])
+        rc, out, _ = drive("--spec", str(spec), "--cmd", "python3 check_loose.py", "--copy-tree")
+        check("spec: a command that does not pin the line reports the mutant SURVIVED",
+              rc == 0 and out.splitlines() == ["SURVIVED NULL", "SURVIVED ret_hi"])
+        rc, out, _ = drive("--spec", str(spec), "--cmd", 'python3 -c "raise SystemExit(1)"')
+        check("spec: a killed NULL is a broken harness, rc 3, and no mutant ran",
+              rc == 3 and out.splitlines() == ["KILLED NULL"])
+        write_spec([{**bad, "old": "return"}])
+        rc, out, err = drive("--spec", str(spec), "--cmd", pin)
+        check("spec: an old text occurring twice is refused, rc 2, nothing run", rc == 2 and out == "" and "3 times" in err)
+        write_spec([bad, {**bad, "file": "lib.py"}])
+        rc, out, err = drive("--spec", str(spec), "--cmd", pin)
+        check("spec: a name used twice is refused, rc 2", rc == 2 and out == "")
+        write_spec([bad])
+        (repo / "lib.py").write_text(LIB + "# dirty\n")
+        rc, out, err = drive("--spec", str(spec), "--cmd", pin)
+        check("spec: a target that differs from HEAD is refused, rc 2", rc == 2 and out == "" and "lib.py" in err)
+        rc, out, err = drive("--spec", str(spec), "--cmd", pin, "--in-place")
+        check("spec: --in-place refuses the same dirty target, rc 2", rc == 2 and out == "")
+        g("checkout", "--", "lib.py")
+
+        # two mutants: the second is only readable if the first was put back
+        write_spec([bad, {"name": "no_edit_equiv", "file": "lib.py", "old": "    return x\n", "new": "    return x  # same\n"}])
+        rc, out, _ = drive("--spec", str(spec), "--cmd", pin)
+        check("spec: the file is restored between mutants (the second, an equivalent edit, SURVIVES)",
+              out.splitlines() == ["SURVIVED NULL", "KILLED ret_hi", "SURVIVED no_edit_equiv"])
+
+        # a kill mid-run
+        write_spec([bad])
+        flag = tmp / "running.flag"
+        slow = f"python3 -c \"import pathlib, time; pathlib.Path('{flag}').write_text('x'); time.sleep(60)\""
+        listing = lambda: {p.name for p in scratch.iterdir()}  # noqa: E731
+        for mode in ("--copy-tree", "--in-place"):
+            flag.unlink(missing_ok=True)
+            # NULL runs first and would sleep: make the command fast on the unedited tree
+            cmd = ("python3 -c \"import pathlib, sys, time\n"
+                   "src = pathlib.Path('lib.py').read_text()\n"
+                   "if 'return hi\\n    if x > hi' in src:\n"
+                   f"    pathlib.Path('{flag}').write_text(str(__import__('os').getpid())); time.sleep(60)\"")
+            rc, out, err = drive("--spec", str(spec), "--cmd", cmd, mode, sig=signal.SIGTERM, watch=flag.exists)
+            clean = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", "lib.py"],
+                                   capture_output=True, text=True, env=env).stdout == ""
+            check(f"SIGTERM mid-mutant ({mode}): rc 143, tree byte-identical, no copy left behind",
+                  rc == 143 and clean and (repo / "lib.py").read_text() == LIB and not listing())
+            check(f"SIGTERM mid-mutant ({mode}): the running command was killed with the driver", _gone(flag.read_text()))
+            flag.unlink(missing_ok=True)
+
+        # a hung mutant is a kill, and its process group goes with it
+        pidf = tmp / "hung.pid"
+        hang = ("python3 -c \"import pathlib, time\n"
+                "if 'return hi\\n    if x > hi' in pathlib.Path('lib.py').read_text():\n"
+                f"    pathlib.Path('{pidf}').write_text(str(__import__('os').getpid())); time.sleep(60)\"")
+        t0 = time.monotonic()
+        rc, out, _ = drive("--spec", str(spec), "--cmd", hang, "--timeout", "2")
+        check("spec: a mutant that hangs past --timeout is KILLED, and its command is killed rather than waited out",
+              rc == 0 and out.splitlines() == ["SURVIVED NULL", "KILLED ret_hi"] and time.monotonic() - t0 < 30
+              and _gone(pidf.read_text()))
+        for label, body in (("not a list", "{}"), ("not JSON", "[oops"), ("missing keys", '[{"name": "a"}]'),
+                            ("empty old", json.dumps([{**bad, "old": ""}])), ("old equals new", json.dumps([{**bad, "new": "return lo"}])),
+                            ("absent file", json.dumps([{**bad, "file": "nope.py"}])),
+                            ("old absent", json.dumps([{**bad, "old": "zzz"}])), ("NULL name", json.dumps([{**bad, "name": "NULL"}]))):
+            spec.write_text(body)
+            rc, out, _ = drive("--spec", str(spec), "--cmd", pin)
+            check(f"spec: {label} is refused, rc 2, nothing run", rc == 2 and out == "")
+        write_spec([bad])
+        for label, args in (("both --spec and --diff", ["--spec", str(spec), "--diff", "a...b", "--cmd", pin]),
+                            ("neither", ["--cmd", pin]), ("no --cmd", ["--spec", str(spec)]),
+                            ("--copy-tree with --in-place", ["--spec", str(spec), "--cmd", pin, "--copy-tree", "--in-place"]),
+                            ("--in-place with a diff end that is not HEAD", ["--diff", f"{base}...{base}", "--cmd", pin, "--in-place"]),
+                            ("a two-dot --diff", ["--diff", "HEAD", "--cmd", pin]),
+                            ("an unresolvable --diff base", ["--diff", "nobase...HEAD", "--cmd", pin])):
+            rc, out, _ = drive(*args)
+            check(f"main: {label} is refused, rc 2", rc == 2 and out == "")
+
+        # diff mode
+        (repo / "lib.py").write_text(LIB2)
+        g("commit", "-q", "-am", "add norm")
+        rng = f"{base}...HEAD"
+        rc, out, _ = drive("--diff", rng, "--list")
+        ops = {l.split()[2] for l in out.splitlines() if l.startswith("MUTANT ")}
+        check("diff: the added lines yield all five operators", ops == set(OPERATORS))
+        rc, out, _ = drive("--diff", rng, "--list")
+        listed = [l for l in out.splitlines() if l.startswith("MUTANT ")]
+        src2 = LIB2.splitlines()
+        doc = {i + 1 for i, l in enumerate(src2) if l.strip() in ("if x < 1:", "return 7", "Say it.") or l.strip().startswith('"""')}
+        msg = next(i + 1 for i, l in enumerate(src2) if l.strip().startswith("msg ="))
+        check("diff: no mutant inside a multi-line string, and none from a < or # inside a string literal",
+              doc and not any(int(l.split()[1].split(":")[1]) in doc | {msg} for l in listed))
+        check("diff: a True constant is flipped", any(l.endswith("on = False") for l in listed))
+        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_norm.py")
+        check("diff: a self-test that pins the guard, return, bound, call and constant leaves no survivor, rc 0",
+              rc == 0 and "SURVIVED" not in out)
+        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py")
+        survivors = [l for l in out.splitlines() if l.startswith("SURVIVED ")]
+        check("diff: a self-test that does not pin them leaves survivors, rc 1, one line each",
+              rc == 1 and len(survivors) >= 5 and {l.split()[2] for l in survivors} == set(OPERATORS))
+        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_norm.py", "--in-place")
+        clean = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, env=env).stdout == ""
+        check("diff: --in-place over a pinning command leaves no survivor and the tree clean", rc == 0 and out == "" and clean)
+        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py", "--in-place", "--max-mutants", "4")
+        check("diff: --max-mutants caps the pass (4 mutants, at most 4 lines)", rc == 1 and 0 < len(out.splitlines()) <= 4)
+        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py", "--report-only")
+        check("diff: --report-only prints the survivors and exits 0", rc == 0 and "SURVIVED" in out)
+        rc, out, _ = drive("--diff", rng, "--cmd", 'python3 -c "raise SystemExit(1)"')
+        check("diff: a command failing on the unedited tree is BASELINE FAILS, rc 3", rc == 3 and "BASELINE FAILS" in out)
+        rc, out, _ = drive("--diff", f"HEAD...HEAD", "--cmd", "python3 check_loose.py")
+        check("diff: an empty diff prints no survivor and exits 0 (null control)", rc == 0 and out == "")
+        status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, env=env).stdout
+        check("diff: the working tree is clean after every run", status == "" and not listing())
+        check("operators: no mutant for a comment, an import or a def, and no CALL_DEL for a log call",
+              not any(list(mutate_line(s)) for s in ("# if x < 1:", "import a1", "def f(x=1):"))
+              and "CALL_DEL" not in {o for o, _ in mutate_line("    _LOGGER.info(x)")})
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    print(f"mutant_run self-test: {checks} checks, {fails} failed")
+    return 1 if fails else 0
+
+
+if __name__ == "__main__":
+    if sys.argv[1:] == ["--self-test"]:
+        sys.exit(_self_test())
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 3ff71ba5a..e4c10b70a 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -3880,6 +3880,30 @@ if [ -s "$UNPINNED_SITES" ]; then
   say WARN "unpinned sites" "$(grep -c . "$UNPINNED_SITES") site(s) the diff adds with no pin -- the body owes each a line under ## Unpinned sites (step 7d)"
 fi
 
+# --- 6d'. the diff's added lines mutated (R10-MUTANT-RUN-DRIVER, card 4), REPORT
+# ONLY: `mutant_run.py --diff` applies GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL
+# and CONST_SWAP to each added Python line and runs MUTANT_CMD, the group's named
+# self-test or `features_block.py` call, once per mutant. Each survivor is a WARN
+# line the body answers (an equivalent one still owes a survivor_triage record);
+# nothing here refuses, and with MUTANT_CMD unset the step skips. The cap keeps
+# the in-tree tier fast; the heavy pass (MUTANT_MAX=0, all mutants) is a cloud
+# seat's.
+if [ -z "${MUTANT_CMD:-}" ]; then
+  say skip "diff mutants" "MUTANT_CMD unset -- set it to the group's self-test or features_block.py call to mutate the diff's added lines (report only)"
+elif [ ! -f tools/audit/seat/mutant_run.py ]; then
+  say skip "diff mutants" "tools/audit/seat/mutant_run.py is not in this tree"
+else
+  MUT_OUT=$(python3 -I tools/audit/seat/mutant_run.py --diff "$BASE...HEAD" --cmd "$MUTANT_CMD" \
+    --max-mutants "${MUTANT_MAX:-40}" --report-only 2>&1)
+  MUT_N=$(printf '%s\n' "$MUT_OUT" | grep -c '^SURVIVED ')
+  if [ "$MUT_N" -gt 0 ]; then
+    printf '%s\n' "$MUT_OUT" | grep '^SURVIVED ' | sed 's/^/           /' >&2
+    say WARN "diff mutants" "$MUT_N survivor(s) on the diff's added lines -- the body answers each (report only)"
+  else
+    say ok "diff mutants" "no survivor: $(printf '%s\n' "$MUT_OUT" | tail -1 | cut -c1-120)"
+  fi
+fi
+
 # --- 6c. a test must import the production symbol: tests.yml's `no-copies`,
 # before the push. `copies_line` above. The scan reads the whole tree, so it
 # runs only when the diff can introduce a shared top-level name; any other

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
