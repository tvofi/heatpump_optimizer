# Review packet #3705
head: 3099d416f40cf3e5468b6d93b6c410394cbbdfb2
base: 174e78cebf5ee60f8ee0428b86b5b06233060480

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133887557008 success
arch-score / arch-score id=133889256414 success
arm id=133887110835 skipped
budget-raise-gate / budget-raise-gate id=133889256473 success
cancel-superseded id=133888826163 success
codeql id=133889258715 skipped
codeql / Analyze (actions) id=133887473399 success
codeql / Analyze (javascript-typescript) id=133887473502 success
codeql / Analyze (python) id=133887473440 success
gate id=133899090888 in_progress
governance id=133889259233 skipped
governance / env-matrix id=133887473424 success
governance / instrument-self-tests id=133887473137 success
governance / policy-docs id=133887473260 success
governance / record id=133887475930 skipped
governance / wave-script id=133887473228 success
hassfest id=133889258727 skipped
hassfest / hassfest id=133887473484 success
kernel-points id=133889257980 skipped
pr-contract id=133889983627 skipped
pr-contract / pr-contract id=133898698804 success
prelude id=133888826273 success
refresh id=133888825798 success
sweep-self id=133890327162 skipped
tests id=133889257792 skipped
tests / arch-instrument id=133887860210 success
tests / briefs id=133887473438 success
tests / browser id=133887860179 success
tests / ci-ratchet id=133898699582 skipped
tests / claims-autofix id=133892077350 skipped
tests / closure-scope id=133887473524 success
tests / closures id=133887860027 success
tests / closures-autofix id=133898699477 skipped
tests / coverage id=133887860012 success
tests / coverage-ratchet id=133895866485 success
tests / fast (3.14) id=133887860153 success
tests / graders-head-copy id=133895866544 success
tests / lane-proofs id=133895866460 success
tests / mutation id=133887473564 success
tests / mutation-autofix id=133887952340 skipped
tests / mutation-pins id=133887950889 skipped
tests / nightly-ha id=133887862931 skipped
tests / nightly-status id=133887473489 failure
tests / replay id=133887862772 skipped
tests / typing id=133887860015 success
validate id=133889258525 skipped
validate / validate-hacs id=133887473289 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item cead2e27: dismissed:not a finding of this diff but that group's roster carry 12, which this part leaves open for the orchestrator's init and the owner's ruling
NOTE body item d6e53e43: dismissed:`KERNELS` is the union of the pin and the classes `.github/workflows/kernel-points.yml` measures; a class added there is added here by the diff that adds it
NOTE body item 755825b6: dismissed:the marks are the orchestrator's record step at each part's merge and change no stage's brief; the group is closed to carries on the round's roster
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 2 script(s) run, 31 scoped out.
             no segment of this names a program this check knows
  ok         python3 -I tools/audit/seat/cloud_dispatch.py --self-test
             `tools/audit/seat/cloud_dispatch.py` is in the tree at this head
  ok         bash tools/audit/seat/cloud-setup.sh --self-test
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_toolchain_mutants.py
             `dev/audit/harnesses/r11_toolchain_mutants.py` is in the tree at this head
  unverified bash <this head>/tools/audit/seat/cloud-setup.sh --kernels python3 tools/audit/seat/features_block.py <start marker> <end marker>
             the path `<this` is a template or an expansion, not a literal
  ok         dev/audit/harnesses/r11_honest_starts_runs.py
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  unverified bash tools/audit/seat/cloud-setup.sh --kernels sh -c 'OPENBLAS_VERBOSE=2 python3 -c "import numpy" 2>&1 | grep -qx "Core: $OPENBLAS_CORETYPE"'
             bash runs an inline script rather than a file
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py kernels
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  unverified git ls-remote origin 'refs/heads/toolchain/*'
             `git ls-remote` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 -I tools/audit/seat/toolchain.py behind . --fetch
             `tools/audit/seat/toolchain.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 38bf516bdd --workdir <dir>
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git grep -n 'parts +=\|pline\|dline' -- tools/audit/seat/cloud_dispatch.py
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/audit/seat/cloud-setup.sh --variables
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head

FIGURES: 17 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/r11_honest_starts_runs.py b/dev/audit/harnesses/r11_honest_starts_runs.py
index 56032ae21c..9f86df1410 100644
--- a/dev/audit/harnesses/r11_honest_starts_runs.py
+++ b/dev/audit/harnesses/r11_honest_starts_runs.py
@@ -610,8 +610,11 @@ def stage() -> int:
 
 KERNELS = ("SkylakeX", "Haswell", "Sandybridge", "Nehalem")
 _BLOCK = 'R.section("R11-OUTSIDE-HONEST-STARTS-RUNS: the start count and committed runs")'
-# The block that follows this group's in tests/features.py; the block runs up to it.
-_NEXT = "# --- R10-START-COUNTER-EDGES: the start counter fed from running-signal edges ---"
+# Stands for the header of whichever block follows this group's in tests/features.py on the tree
+# read (`_next_header`); the block runs up to it. A header named here went stale when #3616's
+# block landed between the two: the run then crossed into it and raised on a name it never built.
+_NEXT = "<the next block's header>"
+_HEADER = "\n# --- "
 _BLOCKS = (
     ("duty-switch block", ("from types import SimpleNamespace as _DspNS", _BLOCK)),
     ("starts-and-runs block", (_BLOCK, _NEXT)),
@@ -646,6 +649,12 @@ R.check = _kp_probe
 '''
 
 
+def _next_header(present: str) -> str:
+    """The first `# --- ` header line after `_BLOCK` in the features source, "" when none follows."""
+    start = present.find(_HEADER, present.find(_BLOCK)) if _BLOCK in present else -1
+    return "" if start < 0 else present[start + 1:].split("\n", 1)[0]
+
+
 def _kernel_blocks(kernel: str) -> list[tuple[str, int, list[str]]]:
     env = dict(os.environ, PYTHONPATH="tests/hastub", OPENBLAS_CORETYPE=kernel, R11_HSR_KERNEL_PROBE=_KERNEL_PROBE,
                OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
@@ -653,7 +662,8 @@ def _kernel_blocks(kernel: str) -> list[tuple[str, int, list[str]]]:
     with open("tests/features.py", encoding="utf-8") as fh:
         present = fh.read()
     for label, markers in _BLOCKS:
-        markers = tuple(m for m in markers if m in present)  # a tree before the next block holds no _NEXT
+        markers = tuple(_next_header(present) if m is _NEXT else m for m in markers)
+        markers = tuple(m for m in markers if m and m in present)  # no block after this group's: it runs to the end
         run = subprocess.run(
             [sys.executable, "tools/audit/seat/features_block.py",
              "--prelude", 'import os as _kp_os; exec(_kp_os.environ["R11_HSR_KERNEL_PROBE"])', *markers],
diff --git a/dev/audit/harnesses/r11_toolchain_mutants.py b/dev/audit/harnesses/r11_toolchain_mutants.py
index 25c453f86b..47757c5f09 100644
--- a/dev/audit/harnesses/r11_toolchain_mutants.py
+++ b/dev/audit/harnesses/r11_toolchain_mutants.py
@@ -35,10 +35,23 @@ tools/ci/gate.py:
   G-cancelled-red   a cancelled member is red, not unread.
   G-na              a skipped instrument-self-tests is read, not set aside.
   G-neither         one required name is in neither verdict.
+tools/audit/seat/cloud_dispatch.py (carry 10: the payload names the approved design):
+  D-design-line     a fixer's payload names no design.
+  D-part-clause     a part's design line says nothing of the two cuts.
+  D-part-always     an unsplit group's design line speaks of parts.
+  D-order           the design line follows the part line.
+  D-stale-approval  an approval of a design that has since moved is one.
+  D-no-verdict      a design with no verdict ref reads the verdict fetched last.
+tools/audit/seat/cloud-setup.sh (carry 11: a check read under each kernel class):
+  K-pin-kept        --kernels runs the command under the seat's pinned class every time.
+  K-probe           a class OpenBLAS does not load is run and counted.
+  K-red             a red class is not counted red.
+  K-none            no class run exits 0.
+  K-list            KERNELS is the pinned class alone.
 
     python3 dev/audit/harnesses/r11_toolchain_mutants.py
 
-EXPECTED RESULT mutants=26
+EXPECTED RESULT mutants=37
 EXPECTED RESULT survived=0
 """
 from __future__ import annotations
@@ -65,9 +78,11 @@ def repo_root(start):
 
 ROOT = repo_root(__file__)
 TOOLCHAIN, PRUNE, GATE = "tools/audit/seat/toolchain.py", "tools/audit/seat/prune_refs.py", "tools/ci/gate.py"
-#: What a copy holds: the three targets' own directories and what their self-tests read.
-COPIED = ("tools/audit/seat", "tools/ci", "tools/policy/fixtures", "tests/throwaway_git.py", "tests/closures.json",
-          ".github/workflows")
+DISPATCH, SETUP = "tools/audit/seat/cloud_dispatch.py", "tools/audit/seat/cloud-setup.sh"
+#: What a copy holds: the targets' own directories and what their self-tests read (`bus.sh`, which
+#: the dispatcher's reviewer path runs, refuses without `tools/pr`'s poster beside it).
+COPIED = ("tools/audit/seat", "tools/ci", "tools/policy", "tools/pr", "tests/throwaway_git.py", "tests/throwaway_git.sh",
+          "tests/closures.json", ".github/workflows")
 #: A plant is (file, old, new).
 PLANTS = {
     "M-absent-behind": (TOOLCHAIN, '    if git("rev-parse", "-q", "--verify", f"{TRACKING}^{{commit}}")[0]:\n', "    if False:\n"),
@@ -101,11 +116,24 @@ PLANTS = {
     "G-na": (GATE, '(jobs.get(n) or ("", ""))[1] != "skipped"]', "True]"),
     "G-neither": (GATE, "    return verdict([n for n in REQUIRED[cls] if n not in MACHINERY_JOBS]), verdict(MACHINERY_JOBS)\n",
                   "    return verdict([n for n in REQUIRED[cls] if n not in MACHINERY_JOBS][1:]), verdict(MACHINERY_JOBS)\n"),
+    "D-design-line": (DISPATCH, "        dline = design_line(group_id, approved, bool(pline))\n", '        dline = ""\n'),
+    "D-part-clause": (DISPATCH, '    if part:\n        line += (" Its parts', '    if False:\n        line += (" Its parts'),
+    "D-part-always": (DISPATCH, '    if part:\n        line += (" Its parts', '    if True:\n        line += (" Its parts'),
+    "D-order": (DISPATCH, "for ln in (dline, pline) if ln),", "for ln in (pline, dline) if ln),"),
+    "D-stale-approval": (DISPATCH, '    return tip if first == f"Design review: approve {tip}" else ""\n', "    return tip\n"),
+    "D-no-verdict": (DISPATCH, '    if not _git(repo_dir, "ls-remote", "origin", vref).split():\n        return ""\n',
+                     '    if not _git(repo_dir, "ls-remote", "origin", vref).split():\n        pass\n'),
+    "K-pin-kept": (SETUP, '    rc=0; OPENBLAS_CORETYPE=$k "$@" || rc=$?\n', '    rc=0; "$@" || rc=$?\n'),
+    "K-probe": (SETUP, '    if [ "$got" != "$k" ]; then\n', "    if false; then\n"),
+    "K-red": (SETUP, '    ran="$ran $k"; [ "$rc" = 0 ] || red="$red $k"\n', '    ran="$ran $k"\n'),
+    "K-none": (SETUP, '  [ -n "$ran" ] || return 2\n', ""),
+    "K-list": (SETUP, 'KERNELS="SkylakeX Haswell Sandybridge Nehalem"\n', 'KERNELS="Haswell"\n'),
 }
 
 
 def selftest(tree: Path, target: str) -> tuple:
-    r = subprocess.run([sys.executable, "-I", str(tree / target), "--self-test"], capture_output=True, text=True)
+    run = ["bash"] if target.endswith(".sh") else [sys.executable, "-I"]
+    r = subprocess.run([*run, str(tree / target), "--self-test"], capture_output=True, text=True)
     out = r.stdout + r.stderr
     return r.returncode, sum(1 for ln in out.splitlines() if ln.lstrip().startswith("FAIL"))
 
@@ -122,7 +150,7 @@ def copy(tmp: str, name: str) -> Path:
 def main() -> int:
     survived = 0
     with tempfile.TemporaryDirectory() as tmp:
-        for target in (TOOLCHAIN, PRUNE, GATE):
+        for target in (TOOLCHAIN, PRUNE, GATE, DISPATCH, SETUP):
             rc, failed = selftest(copy(tmp, "M0-" + Path(target).stem), target)
             print(f"RESULT mutant=M0 file={target} failed={failed} verdict={'null-ok' if rc == 0 and not failed else 'NULL-RED'}")
             if rc or failed:
diff --git a/dev/programme/delivery/3705.md b/dev/programme/delivery/3705.md
new file mode 100644
index 0000000000..21b3f2156a
--- /dev/null
+++ b/dev/programme/delivery/3705.md
@@ -0,0 +1 @@
+- [#3705](https://github.com/tvofi/heatpump_optimizer/pull/3705) — **open**, R11-PRE-TOOLCHAIN-PIN p3: design line in fixer payload, cloud-setup --kernels (R11-PRE-TOOLCHAIN-PIN)
diff --git a/tools/audit/seat/cloud-setup.sh b/tools/audit/seat/cloud-setup.sh
index 9e3a046744..a4e777fe4b 100644
--- a/tools/audit/seat/cloud-setup.sh
+++ b/tools/audit/seat/cloud-setup.sh
@@ -48,6 +48,16 @@
 #                                (the golden fixtures' BLAS floats depend on
 #                                it); else REFUSE naming the variables; exit 0
 #                                or 1
+#   cloud-setup.sh --kernels <command> [<argument>...]
+#                                the command once per kernel class of KERNELS,
+#                                the pin lifted for it: one pinned kernel
+#                                reproduces CI on one of the classes its
+#                                runners load, so a check that reads a solve
+#                                is read under each before it is trusted
+#                                (tests/README.md, the BLAS kernels section).
+#                                A class OpenBLAS does not load here is named
+#                                as not run, never as green. Exit 0 every
+#                                class run is green, 1 one is red, 2 none ran
 #   cloud-setup.sh --self-test   the profile, variables and check arms, in a temp dir
 set -euo pipefail
 
@@ -55,6 +65,10 @@ REPO=${HPO_REPO:-/home/user/heatpump_optimizer}
 PREFIX=${HPO_PREFIX:-/opt/hpo}
 PROFILE=${HPO_PROFILE:-/etc/profile.d/hpo-toolchain.sh}
 CORETYPE=Haswell
+# The kernel classes --kernels reads a command under: the pin's own, and the
+# others .github/workflows/kernel-points.yml measures or its `native` runner
+# loads (SkylakeX, the class `tests / fast` drew red on in #3602).
+KERNELS="SkylakeX Haswell Sandybridge Nehalem"
 # The seat identity (P320): an author in the environment overrides `git config`,
 # so the four variables git reads first are exported; a runner default
 # (Claude <noreply@anthropic.com>) then cannot author a seat's commit. The values
@@ -92,7 +106,9 @@ check() { # prefix
   local py; py=$(command -v python3 || true)
   if [ "$py" = "$1/venv-ci/bin/python3" ] && [ -x "${HPO_TYPING_PYTHON:-}" ] \
     && [ "${OPENBLAS_CORETYPE:-}" = "$CORETYPE" ]; then
-    echo "cloud-setup check: OK python3 is $py"; return 0
+    echo "cloud-setup check: OK python3 is $py; OPENBLAS_CORETYPE is pinned to $CORETYPE, one of the kernel" \
+      "classes CI's runners load: read a check of a solve under each with cloud-setup.sh --kernels <command>"
+    return 0
   fi
   echo "cloud-setup check: REFUSE python3 is ${py:-absent}," \
     "HPO_TYPING_PYTHON is ${HPO_TYPING_PYTHON:-unset}, OPENBLAS_CORETYPE is ${OPENBLAS_CORETYPE:-unset};" \
@@ -100,6 +116,29 @@ check() { # prefix
   return 1
 }
 
+loaded_kernel() { # the kernel class OpenBLAS reports loading under this environment; nothing when it reports none
+  local out; out=$(OPENBLAS_VERBOSE=2 python3 -c 'import numpy' 2>&1 >/dev/null || true)
+  sed -n '/^Core: */{s///p;q;}' <<<"$out"
+}
+
+kernels() { # command...
+  local k got rc ran="" red="" skipped=""
+  [ $# -gt 0 ] || { echo "usage: cloud-setup.sh --kernels <command> [<argument>...]" >&2; return 2; }
+  for k in $KERNELS; do
+    got=$(OPENBLAS_CORETYPE=$k loaded_kernel || true)
+    if [ "$got" != "$k" ]; then
+      echo "cloud-setup kernels: $k not run: asked for it, OpenBLAS loads ${got:-no kernel class} here"
+      skipped="$skipped $k"; continue
+    fi
+    rc=0; OPENBLAS_CORETYPE=$k "$@" || rc=$?
+    echo "cloud-setup kernels: $k exit $rc"
+    ran="$ran $k"; [ "$rc" = 0 ] || red="$red $k"
+  done
+  echo "cloud-setup kernels: ran${ran:- none}; red on${red:- none}; not run${skipped:- none}"
+  [ -n "$ran" ] || return 2
+  [ -z "$red" ]
+}
+
 # Every child runs with stdin from /dev/null: `env -i` drops SHLVL, and a
 # first-level bash on a socket stdin (the agent's) skips BASH_ENV.
 self_test() (
@@ -181,6 +220,48 @@ self_test() (
   [ "$out" = "$SEAT_NAME <$SEAT_EMAIL> $SEAT_NAME <$SEAT_EMAIL>" ]
   expect "a commit made under the exports is authored and committed as the seat even with a conflicting user.name in config" $?
 
+  # --kernels (R11-PRE-TOOLCHAIN-PIN carry 11). The fake python3 is numpy's load under
+  # OPENBLAS_VERBOSE=2: it reports the class asked for, another for a class in FAKE_FALLBACK
+  # (a processor that cannot run it), dies for one in FAKE_DIE, and reports none under FAKE_NOBLAS.
+  mkdir -p "$W/blas"; cat > "$W/blas/python3" <<'PY'
+#!/bin/sh
+case " ${FAKE_DIE:-} " in *" $OPENBLAS_CORETYPE "*) kill -ILL $$ ;; esac
+[ -z "${FAKE_NOBLAS:-}" ] || exit 0
+case " ${FAKE_FALLBACK:-} " in *" $OPENBLAS_CORETYPE "*) echo "Core not found: $OPENBLAS_CORETYPE" >&2; echo "Core: Nehalem" >&2; exit 0 ;; esac
+echo "Core: $OPENBLAS_CORETYPE" >&2
+PY
+  chmod +x "$W/blas/python3"
+  # The command under test: logs the kernel it was run under, red under $RED alone.
+  krun() { env -i HOME="$W" PATH="$W/blas:/usr/bin:/bin" LOG="$W/k.log" "$@" bash "$SELF" --kernels \
+    sh -c 'echo "$OPENBLAS_CORETYPE" >> "$LOG"; [ "$OPENBLAS_CORETYPE" != "${RED:-}" ]' </dev/null 2>&1; }
+  : > "$W/k.log"; out=$(krun "OPENBLAS_CORETYPE=$CORETYPE" RED=SkylakeX); rc=$?
+  [ "$rc" = 1 ] && [ "$(tr '\n' ' ' < "$W/k.log")" = "$KERNELS " ] \
+    && [ "$(grep -c '^cloud-setup kernels: SkylakeX exit 1$' <<< "$out")" = 1 ] \
+    && [ "$(grep -c ' exit 0$' <<< "$out")" = 3 ] && grep -q '; red on SkylakeX; not run none$' <<< "$out"
+  expect "a check red under one kernel class the pin is not is read red there: run under each class, exit 1 naming it" $?
+  env -i PATH="$W/blas:/usr/bin:/bin" "OPENBLAS_CORETYPE=$CORETYPE" RED=SkylakeX \
+    sh -c '[ "$OPENBLAS_CORETYPE" != "$RED" ]' </dev/null
+  expect "control: the same check under the seat's pinned class alone is green (the defect)" $?
+  out=$(krun "OPENBLAS_CORETYPE=$CORETYPE"); rc=$?
+  [ "$rc" = 0 ] && grep -q "^cloud-setup kernels: ran $KERNELS; red on none; not run none\$" <<< "$out"
+  expect "a check green under every class exits 0 naming each (null control)" $?
+  : > "$W/k.log"; out=$(krun FAKE_FALLBACK=SkylakeX RED=SkylakeX); rc=$?
+  [ "$rc" = 0 ] && ! grep -q SkylakeX "$W/k.log" && grep -q '; red on none; not run SkylakeX$' <<< "$out" \
+    && grep -q '^cloud-setup kernels: SkylakeX not run: asked for it, OpenBLAS loads Nehalem here$' <<< "$out"
+  expect "a class OpenBLAS falls back from is not run and is named so, neither green nor red" $?
+  : > "$W/k.log"; out=$(krun FAKE_DIE="Sandybridge Nehalem" RED=Nehalem); rc=$?
+  [ "$rc" = 0 ] && [ "$(tr '\n' ' ' < "$W/k.log")" = "SkylakeX Haswell " ] && grep -q '; not run Sandybridge Nehalem$' <<< "$out"
+  expect "a class whose load dies is not run" $?
+  : > "$W/k.log"; out=$(krun FAKE_NOBLAS=1); rc=$?
+  [ "$rc" = 2 ] && [ ! -s "$W/k.log" ] && grep -q '^cloud-setup kernels: ran none; red on none; not run '"$KERNELS"'$' <<< "$out"
+  expect "where no class loads (no OpenBLAS) nothing is measured: exit 2, not 0" $?
+  out=$(env -i PATH="$W/blas:/usr/bin:/bin" bash "$SELF" --kernels </dev/null 2>&1); rc=$?
+  [ "$rc" = 2 ] && case $out in usage:*) true ;; *) false ;; esac
+  expect "--kernels with no command is a usage error" $?
+  out=$(run "${vars[@]}" HPO_PREFIX="$P" bash "$SELF" --check)  # never-empty: vars is the seven-line output of variables, asserted above
+  case $out in *"pinned to $CORETYPE"*"cloud-setup.sh --kernels <command>"*) true ;; *) false ;; esac
+  expect "the check's OK line names the pinned class and the per-class run" $?
+
   printf 'cloud_setup self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
   [ "$fail" = 0 ]
 )
@@ -188,9 +269,10 @@ self_test() (
 case ${1:-} in
   --variables) variables "$PREFIX"; exit 0 ;;
   --check) check "$PREFIX"; exit $? ;;
+  --kernels) shift; kernels "$@"; exit $? ;;
   --self-test) [ -n "${PR_BOUND:-}" ] || { . "$(dirname -- "$0")/pr_args.sh"; pr_bounded cloud_setup bash "$0" --self-test; }; self_test; exit $? ;;
   "") ;;
-  *) echo "usage: cloud-setup.sh [--variables | --check | --self-test]" >&2; exit 2 ;;
+  *) echo "usage: cloud-setup.sh [--variables | --check | --kernels <command> | --self-test]" >&2; exit 2 ;;
 esac
 
 # The tree-rewriting hooks: the hiway-kit plugin's auto-format.py (PostToolUse)
diff --git a/tools/audit/seat/cloud_dispatch.py b/tools/audit/seat/cloud_dispatch.py
index e33ea0bf65..790c06afe8 100644
--- a/tools/audit/seat/cloud_dispatch.py
+++ b/tools/audit/seat/cloud_dispatch.py
@@ -596,18 +596,30 @@ def design_tip(repo_dir: str, group_id: str) -> str:
     return out[0] if out else ""
 
 
-def design_approved(repo_dir: str, group_id: str) -> bool:
-    """Whether `design-verdict/<group>` reads `Design review: approve <sha>` at the tip
-    `design/<group>` holds now: an approval of a design that has since moved is not one."""
+def design_approved(repo_dir: str, group_id: str) -> str:
+    """The tip `design/<group>` holds now, where `design-verdict/<group>` reads `Design review:
+    approve <sha>` at it, else "": an approval of a design that has since moved is not one."""
     tip = design_tip(repo_dir, group_id)
     if not tip:
-        return False
+        return ""
     vref = f"refs/heads/design-verdict/{group_id}"
     if not _git(repo_dir, "ls-remote", "origin", vref).split():
-        return False
+        return ""
     _git(repo_dir, "fetch", "-q", "origin", vref)
     first = _git(repo_dir, "show", "FETCH_HEAD:verdict.md").split("\n", 1)[0]
-    return first == f"Design review: approve {tip}"
+    return tip if first == f"Design review: approve {tip}" else ""
+
+
+def design_line(group_id: str, sha: str, part: bool) -> str:
+    """The generated brief line naming the approved design a fixer builds from. A fixer of a part
+    is also told how the two cuts relate: `part_line` cuts by carry index and a design by seam, and
+    with neither naming the other each seat of R11-PRE-TOOLCHAIN-PIN chose a cut for itself."""
+    line = (f"Approved design (decision 0014): design.md at {sha}, the design/{group_id} tip "
+            f"(`git fetch origin {sha} && git show {sha}:design.md`).")
+    if part:
+        line += (" Its parts are cut by seam and are not the part line's, which is cut by carry index: the part "
+                 "line is what you build, in the shape the design gives it.")
+    return line
 
 
 def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
@@ -659,9 +671,11 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
             for other in roster.get("groups", []):  # a part's topic is a roster group's own: one seat ref, one wrong credit
                 if other is not group and topic in (_topic_of(other), roster_lib.norm_group(str(other.get("group")))):
                     raise Refusal(f"--part {part}: {topic} is the topic of {other.get('group')}")
-    design = ""
+    design = dline = ""
     if role == "fixer" and roster_lib.needs_design(group) and not design_exempt.strip():
-        if not design_approved(repo_dir, group_id):
+        approved = design_approved(repo_dir, group_id)
+        dline = design_line(group_id, approved, bool(pline))
+        if not approved:
             raise Refusal(f"{group_id} is size {group.get('size')}: no approved `Design review: approve "
                           f"<sha>` at design-verdict/{group_id} names the current design/{group_id} tip "
                           "(decision 0014). Run the designer and design reviewer, or pass "
@@ -683,7 +697,8 @@ def dispatch_group(role: str, group_id: str, model: str, *, repo_dir: str = ".",
                        int(_git(repo_dir, "rev-list", "--count", vtip[0]).strip()))
     args = dict(design=design, verdict=verdict, env_id=known["env_id"], model=model, repo=roster.get("repo") or known["repo"],
                 pr=pr, topic=topic,
-                brief=group_brief(group, roster, fixer=role == "fixer") + (f"\n{pline}\n" if pline else ""),
+                brief=group_brief(group, roster, fixer=role == "fixer")
+                + "".join(f"\n{ln}\n" for ln in (dline, pline) if ln),
                 reviewed_head=reviewed_head)
     head = head or _git(repo_dir, "rev-parse", f"{HEAD_REF}^{{commit}}").strip()
     if role == "reviewer":
@@ -793,7 +808,9 @@ def _group_checks(check) -> None:
         alias = {"group": "R10-ALIAS", "brief": "Alias.\n", "resume": {"branch": "handoff/r10-clash-p3"}}
         selfp = {"group": "R10-SELF-P2", "brief": "Self.\n", "resume": {"branch": "handoff/r10-self"},
                  "carry": [f"Self {i}." for i in range(8)]}
-        land([grp, bad, big, two, cbad, ruled, legacy, prod, cons, share, donec, many, five, clash, clash2, alias, selfp])
+        # R11-PRE-TOOLCHAIN-PIN carry 10: an L group split into parts, its design approved below.
+        dsplit = {"group": "R10-DSPLIT", "size": "L", "brief": "Redesign in parts.\n", "carry": [f"Seam {i}." for i in range(8)]}
+        land([grp, bad, big, dsplit, two, cbad, ruled, legacy, prod, cons, share, donec, many, five, clash, clash2, alias, selfp])
         git(work, "remote", "add", "origin", str(origin))
         tip = git(work, "rev-parse", "origin/main").strip()
 
@@ -833,6 +850,7 @@ def _group_checks(check) -> None:
               refused("R10-BIG") and not git(work, "ls-remote", "origin", "refs/heads/dispatch/fixer-r10-big").strip())
         check("a fixer for an L group is dispatched with --design-exempt (the reason is the orchestrator's)",
               dispatch("R10-BIG", design_exempt="approved prototype on record") == "dispatch/fixer-r10-big")
+        exempt_text = fetched("dispatch/fixer-r10-big", "PROMPT.md")
         check("a designer for an S group is refused (only L and XL take a design)",
               refused("R10-X", "designer") and refused("R10-X", "design-reviewer"))
         check("a design reviewer with no design/<group> to review is refused, for that reason",
@@ -882,6 +900,16 @@ def _group_checks(check) -> None:
         _publish(str(work), "design-verdict/R10-BIG", {"verdict.md": f"Design review: approve {tip}\n"})
         check("a fixer is dispatched once the verdict approves the current design tip (null control)",
               dispatch("R10-BIG") == "dispatch/fixer-r10-big")
+        # R11-PRE-TOOLCHAIN-PIN carry 10: the payload names the design, and a part line's relation to it.
+        dnamed = (f"Approved design (decision 0014): design.md at {tip}, the design/R10-BIG tip "
+                  f"(`git fetch origin {tip} && git show {tip}:design.md`).")
+        btext = fetched("dispatch/fixer-r10-big", "PROMPT.md")
+        check("a fixer of a group with an approved design is given the design's ref and SHA in one generated line, its last",
+              sum(ln == dnamed for ln in btext.splitlines()) == 1 and btext.endswith("\n" + dnamed + "\n"))
+        check("a fixer dispatched design-exempt, and one of a group that takes no design, is given no such line (null control)",
+              "Approved design" not in exempt_text and "Redesign tools/y.py." in exempt_text
+              and "Approved design" not in fetched(line, "PROMPT.md") and "Fix the thing" in fetched(line, "PROMPT.md"))
+        check("an unsplit designed group's line carries no word of parts (null control)", "part line" not in btext)
         brief = work / "brief.txt"
         brief.write_text(group_brief(grp))  # what the group path briefs, so the two payloads can agree
         flags = ["--role", "fixer", "--head", tip, "--topic", "r10-x", "--brief", str(brief),
@@ -959,6 +987,18 @@ def _group_checks(check) -> None:
             p1text = fetched(dispatch("R10-SPLIT", part=1), "PROMPT.md")
             check("--part 1 keeps the group's own topic and names carries 0-4",
                   "topic r10-split, at head" in p1text and "\nPart 1 of 4: build carries 0-4; the others" in p1text)
+            # R11-PRE-TOOLCHAIN-PIN carry 10: a part of a designed group.
+            git(work, "push", "-q", "origin", f"{tip}:refs/heads/design/R10-DSPLIT")
+            check("a design with no verdict ref is not approved by another group's verdict of the same commit, fetched just before",
+                  design_approved(str(work), "R10-BIG") == tip and why_any("R10-DSPLIT", part=2).startswith("R10-DSPLIT is size L"))
+            _publish(str(work), "design-verdict/R10-DSPLIT", {"verdict.md": f"Design review: approve {tip}\n"})
+            stext = fetched(dispatch("R10-DSPLIT", part=2), "PROMPT.md").splitlines()
+            cuts = [ln for ln in stext if ln.startswith("Approved design (decision 0014): design.md at " + tip + ", the design/R10-DSPLIT tip")]
+            check("a part of a designed group names both cuts: the design line says its parts are not the part line's, "
+                  "and the part line follows it, the payload's last",
+                  len(cuts) == 1 and cuts[0].endswith(" Its parts are cut by seam and are not the part line's, which is cut by "
+                                                      "carry index: the part line is what you build, in the shape the design gives it.")
+                  and stext[-1].startswith("Part 2 of 2: build carries 5-7;") and stext[-3] == cuts[0])
             check("a part past the split, a part of a group of five or fewer, and a part for another role refuse",
                   "splits into 4 parts" in why_any("R10-SPLIT", part=5) and "five or fewer" in why_any("R10-FIVE", part=1)
                   and "fixer's" in why_any("R10-SPLIT", "probe", part=2))
diff --git a/tools/audit/seat/instruments/cloud-setup.sh.md b/tools/audit/seat/instruments/cloud-setup.sh.md
index 1d51bad02a..a004c8bbbc 100644
--- a/tools/audit/seat/instruments/cloud-setup.sh.md
+++ b/tools/audit/seat/instruments/cloud-setup.sh.md
@@ -8,7 +8,15 @@
   toolchain reaches it only through the environment's variables, which
   `--variables` prints and the setup run's last line names; `--check`, in a
   seat: `OK` (exit 0) only when all three hold, or `REFUSE` naming them (exit
-  1). The profile prepends `venv-ci/bin` only
+  1). `--kernels <command> [<argument>...]` runs the command once per OpenBLAS
+  kernel class of the script's `KERNELS` (SkylakeX, Haswell, Sandybridge,
+  Nehalem), the pin lifted for it. When: before trusting a check that reads a
+  solve, because the seat is pinned to one class and CI's runners load whichever
+  their processor selects (#3602: two clauses green under the pin, red on
+  `tests / fast (3.14)`). It prints `cloud-setup kernels: <class> exit <rc>` per
+  class and one closing line naming the classes run, red and not run; a class
+  OpenBLAS does not report loading here is not run, never green. Exit 0 every
+  class run is green, 1 one is red, 2 none ran. The profile prepends `venv-ci/bin` only
   when absent, so a PATH a caller narrowed is left alone, and sets every other
   variable only where it is unset, so a `BASH_ENV` naming it changes no value a
   caller handed its child; `--self-test`: the profile, variables and check
diff --git a/tools/audit/seat/instruments/cloud_dispatch.py.md b/tools/audit/seat/instruments/cloud_dispatch.py.md
index 5b10891152..939105084e 100644
--- a/tools/audit/seat/instruments/cloud_dispatch.py.md
+++ b/tools/audit/seat/instruments/cloud_dispatch.py.md
@@ -86,7 +86,9 @@ A `fixer` dispatch for an L or XL group is refused unless
 `design-verdict/<group>` reads `Design review: approve <sha>` at the current
 design tip, or `--design-exempt <reason>` names an approved design, pre-study
 or prototype already on record. The tick board's `DESIGN OWED:` line lists the
-groups whose designer is due.
+groups whose designer is due. A fixer dispatched on an approved design is given
+it in one generated line, `Approved design (decision 0014): design.md at <sha>,
+the design/<group> tip`, with the fetch command; a design-exempt dispatch gets none.
 `--role reviewer --topic <t> --head <handoff tip>` with no `--pr` renders a reviewer at the
 handoff: it reads `handoff-body/<t>`, renders no packet, waits on no CI and returns
 `probe/revt-<t>-<nonce8>` (subject `verdict <t> <head>`). With `--group`, an omitted `--model`
@@ -98,5 +100,8 @@ A `fixer` for a group holding more than five pending carries (`roster_lib.pendin
 is refused, and the refusal prints the split: index-ordered fives, a remainder of one or two
 folded into the last part. `--part <k>` dispatches part k under topic `<topic>-p<k>` (k over 1)
 with one generated line naming its carries; dispatch each part at the previous part's handoff.
+The split is by carry index and an approved design's parts are by seam, so a part's design
+line adds that the design's parts are not the part line's: the part line is what the seat
+builds, in the shape the design gives it.
 Every reviewer stop path, a setup refusal and a bounded CI wait included, pushes a verdict to
 its probe ref and reads it back.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
