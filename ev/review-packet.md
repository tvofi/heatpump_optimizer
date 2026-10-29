# Review packet #2955
head: 9d97a52d52e05fd71abc98d47822c1b521447c91
base: 279578074a17cb2c7f527f5e28da0de4e2006db0

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123591717133 neutral
arch-score / arch-score id=123591391503 success
arm id=123591172713 skipped
budget-raise-gate / budget-raise-gate id=123591391562 success
cancel-superseded id=123597209863 success
codeql / Analyze (actions) id=123591391635 success
codeql / Analyze (javascript-typescript) id=123591391604 success
codeql / Analyze (python) id=123591391275 in_progress
governance / delivery-status id=123591391289 success
governance / delivery-status-publish id=123591393774 skipped
governance / env-matrix id=123591391291 success
governance / instrument-self-tests id=123591391402 in_progress
governance / policy-docs id=123591391300 success
governance / record id=123591394638 skipped
governance / wave-script id=123591391444 success
hassfest / hassfest id=123591391044 success
kernel-points id=123591392813 skipped
prelude id=123597210211 in_progress
refresh id=123597210206 success
tests / arch-instrument id=123591615932 in_progress
tests / briefs id=123591391486 success
tests / browser id=123591615657 success
tests / closure-scope id=123591391457 success
tests / closures id=123591615668 in_progress
tests / coverage id=123591616185 in_progress
tests / fast (3.14) id=123591615697 in_progress
tests / mutation id=123591391548 success
tests / mutation-autofix id=123591907322 skipped
tests / mutation-pins id=123591906493 skipped
tests / nightly-ha id=123591619458 skipped
tests / nightly-status id=123591391633 failure
tests / replay id=123591619902 skipped
tests / typing id=123591615929 success
validate / validate-hacs id=123591391031 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item c92faf56: R10-ERREXIT-COUNTERMEASURES
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git ls-files -- 'tests/*.py' 'tools/*.py'
             `git ls-files` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified bash
             bash with no script argument
  unverified sh
             sh with no script argument
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head
  unverified bash -e
             bash runs an inline script rather than a file
  ok         tools/coverage/coverage_tree.sh
             `tools/coverage/coverage_tree.sh` is in the tree at this head
  ok         tests/throwaway_git.py
             `tests/throwaway_git.py` is in the tree at this head
  ok         tests/throwaway_git.sh
             `tests/throwaway_git.sh` is in the tree at this head
  ok         tools/audit/judge_batch.py
             `tools/audit/judge_batch.py` is in the tree at this head
  ok         tools/audit/seat/train.sh
             `tools/audit/seat/train.sh` is in the tree at this head
  unverified bash -c
             bash runs an inline script rather than a file
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 14 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/gate-sweep.yml b/.github/workflows/gate-sweep.yml
index cb93a582f..eac1d5ebc 100644
--- a/.github/workflows/gate-sweep.yml
+++ b/.github/workflows/gate-sweep.yml
@@ -37,6 +37,8 @@ jobs:
       # is sweep.main's), so the outcome is the last output line's first word,
       # never the exit code: SWEEP-DONE, SKIP and SWEEP (a stop) are done;
       # RATE-LIMITED re-ran nothing further and says so; anything else failed.
+      # The `|| true` is load-bearing: the step runs under `bash -e`, and a bare
+      # capture of an exit 1 would end the step before `case` read the word.
       - name: Re-judge the older gates at this head
         env:
           GH_TOKEN: ${{ github.token }}
@@ -44,7 +46,7 @@ jobs:
         run: |
           set -uo pipefail
           [[ "$RUN_ID" =~ ^[0-9]+$ ]] || { echo "::error title=sweep refused::run id malformed"; exit 1; }
-          out=$(python3 -I tools/ci/gate.py --sweep --run "$RUN_ID" 2>&1)
+          out=$(python3 -I tools/ci/gate.py --sweep --run "$RUN_ID" 2>&1) || true
           printf '%s\n' "$out"
           last=$(printf '%s\n' "$out" | tail -n 1)
           case "${last%% *}" in
diff --git a/dev/programme/delivery/2955.md b/dev/programme/delivery/2955.md
new file mode 100644
index 000000000..54eb26234
--- /dev/null
+++ b/dev/programme/delivery/2955.md
@@ -0,0 +1 @@
+- [#2955](https://github.com/tvofi/heatpump_optimizer/pull/2955) — **open**, R10-ERREXIT-COUNTERMEASURES: errexit countermeasures from the record-autofix batch=$? RCA (R10-ERREXIT-COUNTERMEASURES)
diff --git a/tests/arch_score.py b/tests/arch_score.py
index ce28a5021..01d525c43 100644
--- a/tests/arch_score.py
+++ b/tests/arch_score.py
@@ -155,7 +155,8 @@ def base_runs_the_gate() -> None:
             subprocess.run([*g, "add", "-A"], check=True, env=env)
             subprocess.run([*g, "commit", "-qm", "head"], check=True, env=env)
             head = subprocess.run([*g, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
-            r = subprocess.run(["bash", "-c", script], cwd=repo, capture_output=True, text=True,
+            # The step under its own shell, GitHub's default `bash -e {0}`.
+            r = subprocess.run(["bash", "-e", "-c", script], cwd=repo, capture_output=True, text=True,
                                env={**env, "PR_BASE": base, "PR_HEAD": head})
             return r.stdout + r.stderr
 
diff --git a/tests/entities.py b/tests/entities.py
index 94258619f..266932ec6 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -19875,12 +19875,19 @@ R.check(
 # exits 1 on a rate limit and on a crash alike (P2a's forward-carry). The
 # step's own text is run under bash with a stand-in `python3` printing each
 # outcome, so the classification is measured, not read.
+# GitHub's shell for a `run:` block that names none: `bash -e {0}`. A harness
+# executing a step's own text runs it under this, never a bare `bash -c`, or a
+# bare call the step meant to classify ends the runner's step and passes the
+# harness's (gate-sweep's `out=$(...)`, R10-RCA-HOTFIX-BATCH-ERREXIT's I4).
+_GHA_RUN = ["bash", "-e", "-c"]
+
+
 def _gs_step_verdict(script: str, stdout: str, rc: int) -> "tuple[int, str]":
     with tempfile.TemporaryDirectory() as d:
         fake = Path(d) / "python3"
         fake.write_text("#!/bin/sh\nprintf '%s' \"$FAKE_OUT\"\nexit \"$FAKE_RC\"\n")
         fake.chmod(0o755)
-        p = _subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=30,
+        p = _subprocess.run([*_GHA_RUN, script], capture_output=True, text=True, timeout=30,
                             env={**os.environ, "PATH": f"{d}:{os.environ.get('PATH', '')}",
                                  "RUN_ID": "123", "FAKE_OUT": stdout, "FAKE_RC": str(rc)})
     return p.returncode, p.stdout
@@ -28123,28 +28130,223 @@ def _raf_review_gated(job: str) -> bool:
     return bool(hits) and g > 0 and all(h > g for h in hits) and bool(post)
 
 
+# The `--require-green` call must survive the step's shell, and so must every
+# exit a step means to read. GitHub runs a `run:` block under errexit -- the
+# default shell is `bash -e {0}`, `shell: bash` is `bash --noprofile --norc
+# -eo pipefail {0}`, `shell: sh` is `sh -e {0}`, and a `set -uo pipefail` line
+# does not clear `-e` -- so a `$?` read after a BARE simple command is dead
+# code for every nonzero exit: errexit ends the STEP with that exit first.
+# Twice this reached main (R10-RCA-HOTFIX-BATCH-ERREXIT): the guard's
+# `guard --require-green; rc=$?` (run 38553291314, exit 3, no
+# `AUTOMERGE:` line), and the batch gate's bare `--batch-due` then `batch=$?`
+# (job 121376503388, exit 4) after the barrier pinned only the first call.
+# The unit is every errexit block in the tree, not one call. A producer that
+# is a condition (`if cmd; then rc=0; else rc=$?; fi`, `cmd || rc=$?`) or a
+# read under `set +e` is exempt; a `$?` in an `if`/`while`/`until` TEST reads
+# the bare producer before it, an `elif` test the `if` condition's.
+# Reference logic and its finder: dev/audit/harnesses/r10_errexit_capture.py
+# at e1a684789. Gap, measured and left: a producer read through `out=$(...)`
+# and its output is not a `$?` read -- gate-sweep's I4 -- and is caught where
+# a harness runs the step under `_GHA_RUN` instead.
+_EX_SHELLS = {None, "bash", "sh"}
+_EX_SAFE = re.compile(
+    r"^(if|elif|while|until)\b|^!|\|\||&&|"
+    r"(^|\s)(then|do|else|\{|\()$|^(fi|done|esac|\}|\))\b|^(else|then|do)\b")
+_EX_TEST_HEAD = re.compile(r"^(if|while|until)\s+(!\s*)?(?=\[|test\b)")
+_EX_READER = re.compile(r"^(\w+=|case\b|\[|\[\[|test\b|echo\b|printf\b|exit\b|return\b|local\b)")
+
+
+def _ex_run_blocks(root: Path):
+    """(file, job, step, run text) for every errexit `run:` block under root."""
+    for f in sorted([*(root / ".github" / "workflows").glob("*.yml"),
+                     *(root / ".github" / "actions").glob("*/action.yml")]):
+        doc = _yaml.safe_load(f.read_text()) or {}
+        wdef = ((doc.get("defaults") or {}).get("run") or {}).get("shell")
+        jobs = doc.get("jobs") or {}
+        if "runs" in doc:  # a composite action
+            jobs = {"(composite)": {"steps": (doc["runs"] or {}).get("steps") or []}}
+        for jname, job in jobs.items():
+            jdef = (((job or {}).get("defaults") or {}).get("run") or {}).get("shell", wdef)
+            for i, step in enumerate((job or {}).get("steps") or []):
+                if "run" in step and step.get("shell", jdef) in _EX_SHELLS:
+                    yield (f.relative_to(root).as_posix(), jname,
+                           step.get("name") or f"step {i}", str(step["run"]))
+
+
+def _ex_hazards(text: str) -> "tuple[int, list[str]]":
+    """(`$?` reads examined, the reads errexit makes dead) in one errexit block:
+    comment lines dropped, continuations joined, the producer the statement
+    before the read on its line, else the line before."""
+    lines, cur = [], ""
+    for raw in text.split("\n"):
+        s = raw.strip()
+        if not cur and (not s or s.startswith("#")):
+            continue
+        if s.endswith("\\"):
+            cur += s[:-1] + " "
+            continue
+        lines.append((cur + s).strip())
+        cur = ""
+    if cur:
+        lines.append(cur.strip())
+    reads, hits, errexit, prev = 0, [], True, ""
+    for line in lines:
+        if re.match(r"^set\s+(\+e\b|\+o\s+errexit\b)", line):
+            errexit = False
+        elif re.match(r"^set\s+(-[a-z]*e|-o\s+errexit\b)", line):
+            errexit = True
+        for m in re.finditer(r"\$\?", line):
+            reads += 1
+            head = line[:m.start()]
+            cut = head.rfind(";")
+            whole = head[:cut].strip() if cut >= 0 else prev
+            producer = whole.split(";")[-1].strip()
+            stmt = _EX_TEST_HEAD.sub("", head[cut + 1:].strip())
+            if (errexit and whole and not _EX_SAFE.search(producer)
+                    and not _EX_SAFE.search(stmt) and (not stmt or _EX_READER.match(stmt))):
+                hits.append(f"`{producer[:90]}` then `{line[:60]}`")
+        prev = line
+    return reads, hits
+
+
+def _ex_scan(root: Path) -> "tuple[int, int, list[str]]":
+    blocks = reads = 0
+    out = []
+    for f, job, name, run in _ex_run_blocks(root):
+        blocks += 1
+        n, hs = _ex_hazards(run)
+        reads += n
+        out += [f"{f} job={job} step={name!r}: {h}" for h in hs]
+    return blocks, reads, out
+
+
+_EX_BLOCKS, _EX_READS, _EX_HITS = _ex_scan(Path("."))
+R.check(
+    "no errexit `run:` block reads `$?` after a bare producer (the unit is "
+    "every workflow and composite action, R10-RCA-HOTFIX-BATCH-ERREXIT A)",
+    _EX_BLOCKS > 0 and _EX_READS > 0 and not _EX_HITS,
+    f"blocks={_EX_BLOCKS} reads={_EX_READS} hits={_EX_HITS}; errexit ends the "
+    "step with the producer's exit before the read -- wrap the producer in a "
+    "condition (`if cmd; then rc=0; else rc=$?; fi`, or `rc=0; cmd || rc=$?`)",
+)
+_EX_CASES = {  # run text -> the hits it must yield
+    "bare then capture": ("set -uo pipefail\ncmd --batch-due\nbatch=$?\n", 1),
+    "same line": ("guard --require-green; rc=$?\ncase $rc in 0) ;; esac\n", 1),
+    "case on $?": ("cmd\ncase $? in 4) exit 0 ;; esac\n", 1),
+    "or-capture": ("batch=0\ncmd --batch-due || batch=$?\n", 0),
+    "if/else": ("if guard --require-green; then rc=0; else rc=$?; fi\n", 0),
+    "else line": ("if cmd; then\n  :\nelse\n  pitch=$?\nfi\n", 0),
+    "set +e": ("set +e\ncmd\nrc=$?\nset -e\n", 0),
+    "comment between": ("cmd \\\n  --flag\n# why\nrc=$?\n", 1),
+    "if test -ne": ("cmd --gate\nif [ $? -ne 0 ]; then exit 1; fi\n", 1),
+    "if test quoted": ("cmd --gate\nif [ \"$?\" = 4 ]; then :; fi\n", 1),
+    "if test builtin": ("cmd --gate\nif test $? -eq 4; then :; fi\n", 1),
+    "while test": ("cmd --gate\nwhile [ $? = 4 ]; do cmd; done\n", 1),
+    "same-line if": ("cmd --gate; if [[ $? -ne 0 ]]; then exit 1; fi\n", 1),
+    "elif test": ("if cmd; then :\nelif [ $? = 4 ]; then :\nfi\n", 0),
+    "if after or-capture": ("cmd || true\nif [ $? -ne 0 ]; then :; fi\n", 0),
+}
+_EX_CASES_BAD = sorted(k for k, (t, want) in _EX_CASES.items() if len(_ex_hazards(t)[1]) != want)
+with tempfile.TemporaryDirectory() as _ex_td:
+    _ex_wf = Path(_ex_td) / ".github" / "workflows"
+    _ex_wf.mkdir(parents=True)
+    _EX_EMPTY = _ex_scan(Path(_ex_td))
+    _ex_wf.joinpath("a.yml").write_text(_yaml.safe_dump({"jobs": {"j": {"steps": [
+        {"name": "py", "shell": "python", "run": "x\nrc=$?\n"},
+        {"name": "bash", "shell": "bash", "run": "x\nrc=$?\n"},
+        {"name": "default", "run": "x\nrc=$?\n"}]}}}))
+    _EX_SHELL_ARM = _ex_scan(Path(_ex_td))
+    # The live batch gate, its condition unwrapped back to the defect's form.
+    _ex_wf.joinpath("a.yml").write_text(_NIGHTLY_YML.replace(
+        "batch=0\n", "", 1).replace(" || batch=$?", "\n            batch=$?", 1))
+    _EX_PLANT = _ex_scan(Path(_ex_td))
+R.check(
+    "and the errexit check reads the shapes, not one call (null controls)",
+    not _EX_CASES_BAD and _EX_EMPTY == (0, 0, [])
+    and (_EX_SHELL_ARM[0], len(_EX_SHELL_ARM[2])) == (2, 2)
+    and len(_EX_PLANT[2]) == 1 and "record-autofix" in _EX_PLANT[2][0],
+    f"cases wrong={_EX_CASES_BAD} empty tree={_EX_EMPTY} (a green over no "
+    f"block is a skip) shell arm={_EX_SHELL_ARM[:2]}+{len(_EX_SHELL_ARM[2])} "
+    f"hits (`shell: python` is not errexit) live batch gate unwrapped="
+    f"{_EX_PLANT[2]}",
+)
+
+
+# Countermeasure B's pin (R10-RCA-HOTFIX-BATCH-ERREXIT): a check that runs a
+# step's text under a bare `bash -c` measures a shell GitHub never uses, so a
+# bare call the step means to classify passes the check and ends the runner's
+# step (gate-sweep's I4 stayed green that way). Every `["bash"|"sh", ..., "-c"]`
+# list literal in a tracked `.py` under tests/ and tools/ carries an errexit
+# flag, or runs text that is no `run:` block, keyed by (file, enclosing
+# function). The key does not see what a listed function runs, so a step
+# executed inside one is blinded: a listed function runs one named source, and
+# a new executor belongs in a function of its own. An argv built by anything
+# but a literal is outside the read.
+_SHELL_NOT_A_STEP = {
+    ("tests/throwaway_git.py", "self_test"): "sources tests/throwaway_git.sh",
+    ("tests/entities.py", "_cir_once_count"): "two lines of tools/coverage/coverage_tree.sh",
+    ("tools/audit/judge_batch.py", "run"): "a judge's own command line",
+}
+
+
+def _shell_c_sites(sources: "dict[str, str]") -> "list[tuple[str, str, bool]]":
+    """(file, enclosing function, errexit) for every `-c` shell list literal."""
+    out = []
+    for path, src in sorted(sources.items()):
+        def walk(node, fn):
+            for ch in ast.iter_child_nodes(node):
+                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                    walk(ch, ch.name)
+                    continue
+                if isinstance(ch, ast.List) and ch.elts:
+                    lits = [e.value for e in ch.elts
+                            if isinstance(e, ast.Constant) and isinstance(e.value, str)]
+                    if lits[:1] in (["bash"], ["sh"]) and "-c" in lits:
+                        out.append((path, fn, any(re.fullmatch(r"-[a-z]*e[a-z]*", t) for t in lits)))
+                walk(ch, fn)
+        walk(ast.parse(src), "<module>")
+    return out
+
+
+def _shell_c_defects(sources: "dict[str, str]") -> "list[str]":
+    return [f"{f}:{fn}" for f, fn, ee in _shell_c_sites(sources)
+            if not ee and (f, fn) not in _SHELL_NOT_A_STEP]
+
+
+_SHELL_SOURCES = {f: Path(f).read_text() for f in _subprocess.run(
+    ["git", "ls-files", "-z", "--", "tests/*.py", "tools/*.py"],
+    capture_output=True, text=True, check=True).stdout.split("\0") if f}
+_SHELL_SITES = _shell_c_sites(_SHELL_SOURCES)
+_SHELL_PLANTS = {
+    "a bare step runner": ("tests/x.py", 'def f(s):\n    run(["bash", "-c", s])\n'),
+    "sh, flags apart": ("tools/x.py", 'def g(s):\n    run(["sh", "-x", "-c", s])\n'),
+    "a listed name in another file": ("tests/x.py", 'def self_test(s):\n    run(["bash", "-c", s])\n'),
+}
+_SHELL_PLANT_MISSED = sorted(k for k, (f, src) in _SHELL_PLANTS.items()
+                             if _shell_c_defects({f: src}) != [f"{f}:{src[4:src.index('(')]}"])
+R.check(
+    "every `bash -c` / `sh -c` a check runs carries errexit, as GitHub's step "
+    "shell does, unless it runs no workflow step (countermeasure B)",
+    len(_SHELL_SITES) > len(_SHELL_NOT_A_STEP) and not _shell_c_defects(_SHELL_SOURCES)
+    and {(f, fn) for f, fn, ee in _SHELL_SITES if not ee} == set(_SHELL_NOT_A_STEP)
+    and not _SHELL_PLANT_MISSED
+    and not _shell_c_defects({"t.py": 'run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", s])'}),
+    f"sites={len(_SHELL_SITES)} without errexit={_shell_c_defects(_SHELL_SOURCES)} "
+    f"listed and unused={sorted(set(_SHELL_NOT_A_STEP) - {(f, fn) for f, fn, ee in _SHELL_SITES if not ee})} "
+    f"plants missed={_SHELL_PLANT_MISSED}; a step run under a bare `bash -c` passes a "
+    "bare call errexit ends on the runner -- use `_GHA_RUN`",
+)
+
+
 # The merge is the beat's own, pinned to the head the guard judged (#2029
 # review, round 1): a `PUT .../merge` whose payload carries that `sha`, after
 # the guard's `--require-green` call, and never GitHub's auto-merge, which
 # merges later on a head nobody judged.
-#
-# The `--require-green` call must survive the step's shell. GitHub runs a
-# `run:` block under `bash -e`, so a BARE `guard --require-green; rc=$?`
-# ends the STEP with the guard's own exit -- 3 while a required check still
-# runs, 1 on a refusal -- before the `case` after it can turn either into
-# `say ...; exit 0`. Every pending or refused beat then reddens the job the
-# report step is the one meant to decide (measured: run 38553291314, exit 3,
-# no `AUTOMERGE:` line). A condition is exempt from `-e`, so the exit reaches
-# the case; `if guard --require-green; then rc=0; else rc=$?; fi` captures it.
-_RAF_BARE_GREEN = re.compile(r"(?m)^\s*guard --require-green\b")
-
-
 def _raf_merge_pinned(job: str) -> bool:
     g = job.find("guard --require-green")
     put = job.find('"$API/repos/$REPO/pulls/$NUM/merge"')
     return (0 < g < put
             and "if guard --require-green" in job
-            and _RAF_BARE_GREEN.search(job) is None
             and '{"sha": sys.argv[1], "merge_method": "merge"}' in job
             and "AutoMerge" not in job)
 
@@ -28405,7 +28607,7 @@ def _train_hold_status(code: int, body: str, pitch_rc: int = 0, guard_rc: int =
         (bin_ / "curl").chmod(0o755)
         out = t / "out"
         out.write_text("")
-        p = subprocess.run(["bash", "-c", run or _HOLD_RUN], cwd=t, capture_output=True, text=True,
+        p = subprocess.run([*_GHA_RUN, run or _HOLD_RUN], cwd=t, capture_output=True, text=True,
                            env={**os.environ, "PATH": str(bin_) + os.pathsep + os.environ["PATH"],
                                 "RUNNER_TEMP": str(t), "GITHUB_OUTPUT": str(out),
                                 "REPO": "o/r", "TOKEN": "t0k", "APPROVER": approver, "NUM": "42",
@@ -28820,7 +29022,7 @@ def _pt_trigger(script: str, planted: str) -> str:
         subprocess.run(_g + ["commit", "-qm", "head"], check=True, env=_env)
         _head = subprocess.run(_g + ["rev-parse", "HEAD"], capture_output=True, text=True, env=_env).stdout.strip()
         _out = Path(_td, ".out")
-        subprocess.run(["bash", "-c", script], cwd=_td, capture_output=True, text=True,
+        subprocess.run([*_GHA_RUN, script], cwd=_td, capture_output=True, text=True,
                        env={**os.environ, "BASE": _base, "HEAD": _head,
                             "PATH": str(_bin) + os.pathsep + os.environ["PATH"],
                             "RUNNER_TEMP": _td, "GITHUB_OUTPUT": str(_out)})
@@ -30307,7 +30509,7 @@ def _cov_trust(check_run: str, marker: "str | None", base: str) -> "tuple[bool,
             (_tmp / "coverage-base" / ".measured-by").write_text(marker)
         _out = _tmp / "out"
         _out.write_text("")
-        subprocess.run(["bash", "-c", check_run], capture_output=True, text=True,
+        subprocess.run([*_GHA_RUN, check_run], capture_output=True, text=True,
                        env={**os.environ, "RUNNER_TEMP": str(_tmp), "BASE": base,
                             "GITHUB_OUTPUT": str(_out)})
         return ("trusted=true" in _out.read_text(), (_tmp / "coverage-base").exists())
@@ -30318,7 +30520,7 @@ def _cov_marker(stage_run: str, event: str, ref: str) -> str:
     with tempfile.TemporaryDirectory() as _t:
         _tmp = Path(_t)
         (_tmp / "w" / "out" / "per").mkdir(parents=True)
-        subprocess.run(["bash", "-c", stage_run], capture_output=True, text=True,
+        subprocess.run([*_GHA_RUN, stage_run], capture_output=True, text=True,
                        env={**os.environ, "RUNNER_TEMP": str(_tmp),
                             "W5P_WORK": str(_tmp / "w"), "GITHUB_EVENT_NAME": event,
                             "GITHUB_REF": ref})
diff --git a/tools/policy/agreement.mjs b/tools/policy/agreement.mjs
index 47710cfcd..386457aed 100644
--- a/tools/policy/agreement.mjs
+++ b/tools/policy/agreement.mjs
@@ -494,6 +494,9 @@ const PAIRS = [
 // instances only; the barrier pull request classifies every entry the
 // discovery arm prints.
 const SHARED_GRAMMARS = {
+  "(if|elif|while|until)\\b|^!|\\|\\||&&|": "identical:countermeasure A's errexit safe-producer grammar, in entities.py a disclosed port of the frozen finder harness r10_errexit_capture.py (e1a684789), equal to it on six trees in R10-ERREXIT-COUNTERMEASURES",
+  "(if|while|until)\\s+(!)?(?=\\[|test\\b)": "identical:countermeasure A's errexit test-head grammar, in entities.py a disclosed port of the frozen finder harness r10_errexit_capture.py (e1a684789), equal to it on six trees in R10-ERREXIT-COUNTERMEASURES",
+  "(\\w+=|case\\b|\\[|\\[\\[|test\\b|echo\\b|printf\\b|exit\\b|return\\b|local\\b)": "identical:countermeasure A's errexit reader-statement grammar, in entities.py a disclosed port of the frozen finder harness r10_errexit_capture.py (e1a684789), equal to it on six trees in R10-ERREXIT-COUNTERMEASURES",
   "  ([A-Za-z][\\w-]*):": "identical:the job-id scan of a workflow's jobs: block, a disclosed copy of entities.py _workflow_job_ids in the governance-workflow-jobs reader, null-controlled by the 'briefs' job",
   "wave-.*-groups\\.json": "identical:three directory filters over the wave rosters, one listing rule",
   "const VERDICT_CLASSES = \\[([^\\]]*)\\]": "identical:the wave script's verdict-class list extractor, read in three tools",

