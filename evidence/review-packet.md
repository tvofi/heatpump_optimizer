# Review packet #3431
head: 3861ae76214c26900658bfa52c91d880fe8865a1
base: a7628041dc02e298c5399003d4c0576391dd5c4e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
arch-score / arch-score id=130539043890 success
budget-raise-gate / budget-raise-gate id=130538990299 success
cancel-superseded id=130539060601 success
codeql id=130538990712 skipped
codeql / Analyze (actions) id=130538972859 success
codeql / Analyze (javascript-typescript) id=130539051548 success
codeql / Analyze (python) id=130539043272 success
gate id=130538989786 queued
governance id=130538989956 skipped
governance / delivery-status id=130539041178 success
governance / delivery-status-publish id=130539020421 skipped
governance / env-matrix id=130538972971 success
governance / instrument-self-tests id=130539032481 success
governance / policy-docs id=130539040517 success
governance / record id=130538973695 skipped
governance / wave-script id=130539039513 success
hassfest id=130539059740 skipped
hassfest / hassfest id=130539015127 success
kernel-points id=130539013634 skipped
pr-contract id=130538990888 skipped
pr-contract / pr-contract id=130538975942 failure
prelude id=130539049504 success
refresh id=130539028867 success
sweep-self id=130538453310 success
tests id=130538990140 skipped
tests / arch-instrument id=130538974289 success
tests / briefs id=130538973348 success
tests / browser id=130538974451 success
tests / ci-ratchet id=130538976111 skipped
tests / claims-autofix id=130538974915 success
tests / closure-scope id=130539038316 success
tests / closures id=130538974925 success
tests / closures-autofix id=130538976750 skipped
tests / coverage id=130538975388 success
tests / coverage-ratchet id=130538976287 success
tests / fast (3.14) id=130538974513 failure
tests / graders-head-copy id=130538975328 success
tests / lane-proofs id=130538975629 success
tests / mutation id=130538973512 success
tests / mutation-autofix id=130538974946 skipped
tests / mutation-pins id=130538973491 skipped
tests / nightly-ha id=130537865496 skipped
tests / nightly-ha (2025.2.0) id=130538974645 success
tests / nightly-ha (stable) id=130538975475 success
tests / nightly-status id=130538973252 failure
tests / replay id=130538974649 skipped
tests / typing id=130538975076 success
validate id=130538989999 skipped
validate / validate-hacs id=130539049365 success

## Refusals
red-unanswered: concluded red check `pr-contract / pr-contract` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
NOTE body item 7f49a086: dismissed:premise stale, venv-ha is not a suite interpreter.
NOTE body item 6d8732be: dismissed:needs an owner ruling on a cap raise; the fact is `ci.yml` `workflow_dispatch` with `-f base=<ref>` and no `pr` input.
NOTE body item cd736041: dismissed:no red measured; `tests/nightly_ha.py` already samples with `_remote_debugging` where it exists.
NOTE body item 65af5ac0: dismissed:no destination is live. The precondition stays in the carry text of the brief: re-measure base beside head on one box before reading a 3.14 stress memory red.
NOTE body item bb36f50a: dismissed:the reproduced fault is fixed in this PR, and the other does not reproduce.
NOTE body item b46fffe8: dismissed:duplicate of Carry 6, not reproduced.
CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff a7628041dc
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head
  ok         tests/arch_score_head.py
             `tests/arch_score_head.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git grep -l 'from harness import\|import harness' -- dev/audit/harnesses/ | xargs grep -l sys.path
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -l os.chdir -- dev/audit/harnesses/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/harness.py
             `tests/harness.py` is in the tree at this head

FIGURES: 8 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3431.md b/dev/programme/delivery/3431.md
new file mode 100644
index 000000000..38715847a
--- /dev/null
+++ b/dev/programme/delivery/3431.md
@@ -0,0 +1 @@
+- [#3431](https://github.com/tvofi/heatpump_optimizer/pull/3431) — **open**, R10-SUITE-ENV-RESIDUE: r10 suite env residue (R10-SUITE-ENV-RESIDUE)
diff --git a/tests/arch_score.py b/tests/arch_score.py
index 07095a7b0..1a3ce1506 100644
--- a/tests/arch_score.py
+++ b/tests/arch_score.py
@@ -135,13 +135,16 @@ def base_runs_the_gate() -> None:
     stub = ('import sys\nfrom pathlib import Path\n'
             'if "--self-test" not in sys.argv:\n    print("SAW " + Path("tests/structure.py").read_text().strip())\n')
 
-    def run(base_has_gate: bool) -> str:
+    def run(base_has_gate: bool) -> tuple[str, bool]:
         with tempfile.TemporaryDirectory(prefix="archscore-plant-") as tmp:
-            repo, env = Path(tmp) / "r", {**os.environ, "RUNNER_TEMP": str(Path(tmp) / "t")}
-            (Path(tmp) / "t").mkdir()
+            repo, runner_temp = Path(tmp) / "r", Path(tmp) / "t"
+            runner_temp.mkdir()
             (repo / "tests").mkdir(parents=True)
             g = ["git", "-C", str(repo)]
-            env = {**env, **throwaway_git_init(repo, "-q")}
+            # RUNNER_TEMP last: throwaway_git_init's env copies os.environ, whose
+            # RUNNER_TEMP (a seat's, or a runner's) would take the step's worktree
+            # out of this temp dir, and a second run then finds it already there.
+            env = {**throwaway_git_init(repo, "-q"), "RUNNER_TEMP": str(runner_temp)}
             (repo / "tests" / "structure.py").write_text("BASE\n")
             if base_has_gate:
                 (repo / "tools" / "audit" / "archscore").mkdir(parents=True)
@@ -159,13 +162,15 @@ def base_runs_the_gate() -> None:
             # The step under its own shell, GitHub's default `bash -e {0}`.
             r = subprocess.run(["bash", "-e", "-c", script], cwd=repo, capture_output=True, text=True,
                                env={**env, "PR_BASE": base, "PR_HEAD": head})
-            return r.stdout + r.stderr
+            return r.stdout + r.stderr, (runner_temp / "base").is_dir()
 
     attributes_do_not_hide_code()
-    out = run(True)
+    out, own_temp = run(True)
     R.check("arch-score.yml: a head edit to tests/structure.py is not what the gate loads (the #2068 plant)",
             re.search(r"^SAW BASE$", out, re.M) is not None and "PLANT" not in out, out[-300:])
-    out = run(False)
+    R.check("the #2068 plant's base worktree lands in its own RUNNER_TEMP, not the caller's",
+            own_temp, out[-300:])
+    out, _ = run(False)
     R.check("and a base with no gate.py is the adoption: the head's copy runs once (null control)",
             re.search(r"^SAW PLANT$", out, re.M) is not None, out[-300:])
 
diff --git a/tests/harness.py b/tests/harness.py
index 9497279e3..6ca70cb5b 100644
--- a/tests/harness.py
+++ b/tests/harness.py
@@ -19,8 +19,12 @@ from operator import attrgetter
 from types import SimpleNamespace
 from typing import Any
 
-sys.path.insert(0, "tests")
-sys.path.insert(0, "custom_components")
+# Anchored to this file's own tree, not the cwd: a harness that imports this
+# module from a root other than the cwd (an export, a worktree) measures that
+# root's package, not whichever tree the shell stands in.
+_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
+sys.path.insert(0, os.path.join(_ROOT, "tests"))
+sys.path.insert(0, os.path.join(_ROOT, "custom_components"))
 
 from homeassistant.config_entries import ConfigEntryState
 from homeassistant.helpers.typing import UNDEFINED
@@ -34,7 +38,7 @@ UTC = timezone.utc
 # to the working directory, as every suite path is (tests/run.sh runs from
 # the repository root).
 SHIPPED_LANGS: tuple[str, ...] = tuple(
-    sorted(p[:-5] for p in os.listdir("custom_components/heatpump_optimizer/translations")
+    sorted(p[:-5] for p in os.listdir(os.path.join(_ROOT, "custom_components/heatpump_optimizer/translations"))
            if p.endswith(".json"))
 )
 TRANSLATED_LANGS: tuple[str, ...] = tuple(lang for lang in SHIPPED_LANGS if lang != "en")
diff --git a/tests/harness_headers.py b/tests/harness_headers.py
index 7c72025c0..b36292610 100644
--- a/tests/harness_headers.py
+++ b/tests/harness_headers.py
@@ -10,11 +10,13 @@ RESULT. Playwright and stress harnesses are not run here.
 """
 from __future__ import annotations
 
+import json
 import os
 import re
 import resource
 import subprocess
 import sys
+import tempfile
 from pathlib import Path
 
 sys.path.insert(0, "tests")
@@ -592,6 +594,55 @@ def main() -> int:
         clean,
         detail,
     )
+    # tests/harness.py anchors its sys.path and its translations read to its
+    # own tree: imported from a foreign cwd it must still import and name the
+    # catalogues (before the anchor it raised FileNotFoundError there).
+    with tempfile.TemporaryDirectory() as decoy:
+        # A decoy tree at the cwd holding a module of each name the harness's
+        # importers take from either insert: a cwd-relative insert of either
+        # half resolves the decoy's module instead of this tree's
+        # (dev/audit/harnesses/learner_inputs_swap.py imports `profiles`
+        # straight after `harness`).
+        os.makedirs(os.path.join(decoy, "custom_components", "heatpump_optimizer"))
+        os.makedirs(os.path.join(decoy, "tests"))
+        for stub in (("custom_components", "heatpump_optimizer", "__init__.py"),
+                     ("tests", "profiles.py")):
+            with open(os.path.join(decoy, *stub), "w"):
+                pass
+        foreign = subprocess.run(
+            [sys.executable, "-c",
+             "import json, sys; sys.path.insert(0, sys.argv[1]); before = list(sys.path); "
+             "import harness, heatpump_optimizer, profiles; "
+             "added = sys.path[:len(sys.path) - len(before)]; "
+             "print(json.dumps({'langs': len(harness.SHIPPED_LANGS), "
+             "'package': heatpump_optimizer.__file__, 'profiles': profiles.__file__, "
+             "'added': added, 'kept': sys.path[len(added):] == before}))",
+             str(ROOT / "tests")],
+            cwd=decoy, capture_output=True, text=True,
+            env={**os.environ, "PYTHONPATH": str(ROOT / "tests" / "hastub")},
+        )
+    try:
+        got = json.loads(foreign.stdout.strip().splitlines()[-1])
+    except (IndexError, ValueError):
+        got = {}
+    detail = (foreign.stderr or foreign.stdout)[-200:]
+
+    def own(path: object, sub: str) -> bool:
+        return isinstance(path, str) and os.path.isabs(path) and \
+            Path(path).resolve().is_relative_to(ROOT / sub)
+
+    R.check("tests/harness.py from a foreign cwd finds its catalogues and its own tree's package",
+            foreign.returncode == 0 and isinstance(got.get("langs"), int) and got["langs"] > 0
+            and own(got.get("package"), "custom_components"), detail)
+    R.check("tests/harness.py from a foreign cwd resolves a module the cwd's tests/ also holds "
+            "to its own tests/", own(got.get("profiles"), "tests"), detail)
+    # Each insert pinned alone: exactly the two anchored paths, absolute, in
+    # this tree, so neither half can go back to cwd-relative unnoticed.
+    R.check("tests/harness.py's sys.path inserts are exactly its own tests/ and custom_components/, absolute",
+            got.get("kept") is True
+            and sorted(got.get("added") or []) == sorted([str(ROOT / "custom_components"), str(ROOT / "tests")])
+            and all(os.path.isabs(a) for a in got.get("added") or []),
+            f"added={got.get('added')!r} {detail}")
     return R.close("HARNESS HEADER CHECKS")
 
 
diff --git a/tools/audit/seat/cloud-setup.sh b/tools/audit/seat/cloud-setup.sh
index 917249de1..e4b7c39e7 100644
--- a/tools/audit/seat/cloud-setup.sh
+++ b/tools/audit/seat/cloud-setup.sh
@@ -15,6 +15,9 @@
 #            the `typing` job installs it: mypy, homeassistant and
 #            homeassistant-stubs; exported as HPO_TYPING_PYTHON, and asserted
 #            to import the lock's homeassistant pin, read from the lock
+#            (typing only: it has no scipy and no paho by design. The suites
+#            run under venv-ci with PYTHONPATH=tests/hastub, the stub standing
+#            in for Home Assistant; never put venv-ha first on PATH for them)
 #
 # The pins are read from the checkout, never restated here, so this script
 # cannot drift from the lock files; a lock edit reaches the next session.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
