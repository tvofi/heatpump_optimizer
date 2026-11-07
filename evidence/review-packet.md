# Review packet #3301
head: 926a01499de2a184481a42734fc91bfedc5bb4b1
base: dee8b413fd7da7b07f13e28a93d7d49b4a9e978a

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128538060823 success
arch-score / arch-score id=128545388364 success
arm id=128537930027 skipped
budget-raise-gate / budget-raise-gate id=128545388468 success
cancel-superseded id=128545404304 success
codeql id=128545388565 skipped
codeql / Analyze (actions) id=128538023016 success
codeql / Analyze (javascript-typescript) id=128538022989 success
codeql / Analyze (python) id=128538022986 success
gate id=128545388110 success
governance id=128545388311 skipped
governance / delivery-status id=128538023028 success
governance / delivery-status-publish id=128538024401 skipped
governance / env-matrix id=128538023047 success
governance / instrument-self-tests id=128538023017 success
governance / policy-docs id=128538023109 success
governance / record id=128538024431 skipped
governance / wave-script id=128538023121 success
hassfest id=128545409261 skipped
hassfest / hassfest id=128538022980 success
kernel-points id=128545388427 skipped
pr-contract id=128545389069 skipped
pr-contract / pr-contract id=128545051432 success
prelude id=128545425081 success
refresh id=128545418610 success
tests id=128545388283 skipped
tests / arch-instrument id=128538182601 success
tests / briefs id=128538023020 success
tests / browser id=128538182557 success
tests / ci-ratchet id=128543072076 skipped
tests / claims-autofix id=128540812593 skipped
tests / closure-scope id=128538023041 success
tests / closures id=128538182533 success
tests / closures-autofix id=128543072014 skipped
tests / coverage id=128538182513 success
tests / coverage-ratchet id=128541058813 success
tests / fast (3.14) id=128538182604 success
tests / graders-head-copy id=128541058890 success
tests / lane-proofs id=128541058817 success
tests / mutation id=128538022993 success
tests / mutation-autofix id=128538190934 skipped
tests / mutation-pins id=128538190227 skipped
tests / nightly-ha id=128538184095 skipped
tests / nightly-status id=128538023027 success
tests / replay id=128538183520 skipped
tests / typing id=128538182603 success
validate id=128545388450 skipped
validate / validate-hacs id=128538022951 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item cd3eb681: dismissed(R10-FLY-CIPREDICT-RESTORING):not dropped, still owed; already stated verbatim in this group's own roster carries, so no new landing.
NOTE body item 0c493515: dismissed(R10-FLY-CIPREDICT-RESTORING):not dropped, still owed; already stated verbatim in this group's own roster carries, so no new landing.
NOTE body item 10670659: dismissed(R10-FLY-CIPREDICT-RESTORING):not dropped, still owed; already stated verbatim in this group's own roster carries, so no new landing.
NOTE body item 4d51cee8: dismissed(R10-FLY-CIPREDICT-RESTORING):not dropped, still owed; already stated in this group's brief, so no new landing.
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git grep -n -- "- name: Restore the check source from the base commit" HEAD -- .github/workflows/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/tmp_paths.py --check
             `tools/audit/seat/tmp_paths.py` is in the tree at this head

FIGURES: 4 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/rca/prepr-head-graders/mutants.py b/dev/audit/rca/prepr-head-graders/mutants.py
index 5f9c69018..af2455f20 100644
--- a/dev/audit/rca/prepr-head-graders/mutants.py
+++ b/dev/audit/rca/prepr-head-graders/mutants.py
@@ -10,7 +10,9 @@ M = {
  "M1 restored_hit keys nothing": ("return sorted(p for p in names if p in at_tip and any(covers(s, p) for s in specs))", "return []"),
  "M2 restored_hit ignores the base tip": ("p in at_tip and any(covers(s, p)", "any(covers(s, p)"),
  "M3 grader_runs drops no exemption": ("not in GRADER_EXEMPT.keys() | AGREEMENT_RUNS]", "not in AGREEMENT_RUNS]"),
- "M4 predict's graders entry removed": ('        ("graders", lambda: grader_preds(root, base_ref)),\n', ""),
+ "M4 predict's graders entry removed": ('        ("graders", lambda: grader_preds(root, base_ref, body, notes)),\n', ""),
+ "M6 ci_tree_run reads governance.yml for every job": ("(r / (workflow or agreement_py.WORKFLOW))", "(r / agreement_py.WORKFLOW)"),
+ "M7 the enumeration reads governance.yml only": ('for wf in sorted((root / WORKFLOWS).glob("*.y*ml")):', 'for wf in [root / WORKFLOWS / "governance.yml"]:'),
  "M5 ci_tree_run restores nothing": ('        run("git", "checkout", tip, f"--pathspec-from-file={tmp / \'pinned.list\'}", "--pathspec-file-nul")\n', ""),
 }
 for name, (a, b) in M.items():
diff --git a/dev/audit/rca/prepr-head-graders/plant_jobs.sh b/dev/audit/rca/prepr-head-graders/plant_jobs.sh
new file mode 100755
index 000000000..3355b0d9b
--- /dev/null
+++ b/dev/audit/rca/prepr-head-graders/plant_jobs.sh
@@ -0,0 +1,24 @@
+#!/usr/bin/env bash
+# R10-FLY-CIPREDICT-RESTORING (#2952): one planted edit per restoring job, graded
+# by the working tree's ci_predict.py `graders` arm with --base <head>, so only
+# the plant is in the diff. The plant is a comment appended to the job's own
+# restored program (a head copy differing from the base copy), then committed.
+#
+#   plant_jobs.sh <head> <program> <out-file> [<body-file>]
+#
+# The job set the arm walks is the enumeration rule's (`restoring_jobs`), not a
+# list here. Writes the predictor's output, then `rc=<rc>`, to <out-file>.
+set -u
+head=$1 prog=$2 out=$3 body=${4:-}
+root=$(git rev-parse --show-toplevel)
+. "$root/tests/throwaway_git.sh"
+wt=$(mktemp -d); trap 'rm -rf "$wt"' EXIT
+throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" >/dev/null || exit 2
+cd "$wt/t" || exit 2
+throwaway_git_env
+git checkout -q --detach "$head" && git update-ref refs/remotes/origin/main "$head" || exit 2
+case $prog in *.mjs|*.js) printf '\n// plant\n' >> "$prog" ;; *) printf '\n# plant\n' >> "$prog" ;; esac
+git commit -qam "plant $prog" || exit 2
+cp "$root/tools/pr/ci_predict.py" tools/pr/ci_predict.py
+extra=(); [ -n "$body" ] && extra=(--body "$body")
+PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$head" --only graders "${extra[@]}" > "$out" 2>&1; echo "rc=$?" >> "$out"
diff --git a/dev/programme/delivery/3301.md b/dev/programme/delivery/3301.md
new file mode 100644
index 000000000..6d6c17d27
--- /dev/null
+++ b/dev/programme/delivery/3301.md
@@ -0,0 +1 @@
+- [#3301](https://github.com/tvofi/heatpump_optimizer/pull/3301) — **open**, R10-FLY-CIPREDICT-RESTORING: fly cipredict restoring (R10-FLY-CIPREDICT-RESTORING)
diff --git a/tools/audit/seat/tmp_paths.py b/tools/audit/seat/tmp_paths.py
index 4bbfc0e06..5294d5b13 100644
--- a/tools/audit/seat/tmp_paths.py
+++ b/tools/audit/seat/tmp_paths.py
@@ -99,6 +99,11 @@ TOKEN_END = re.compile(r"[\s\"'`;,()\[\]]")
 
 # (file, text the line must contain, reason). Exact and per file.
 ALLOW = (
+    ("tools/pr/ci_predict.py", 'PR_BODY = "/tmp/pr-body.md"', "the runner-side file CI's pr-contract job writes and the predictor stands in for (R10-FLY-CIPREDICT-RESTORING)"),
+    ("tools/pr/ci_predict.py", '"/tmp/pr-commits.tsv": "empty"', "the runner-side file CI's pr-contract job writes and the predictor stands in for (R10-FLY-CIPREDICT-RESTORING)"),
+    ("tools/pr/ci_predict.py", '/tmp/pr-author.txt', "the runner-side file CI's pr-contract job writes and the predictor stands in for (R10-FLY-CIPREDICT-RESTORING)"),
+    ("tools/pr/ci_predict.py", '"/tmp/pr-commits.tsv": ""', "the runner-side file CI's pr-contract job writes and the predictor stands in for (R10-FLY-CIPREDICT-RESTORING)"),
+    ("tools/pr/ci_predict.py", '"/tmp/pr-existing.txt": paths(', "the runner-side file CI's pr-contract job writes and the predictor stands in for (R10-FLY-CIPREDICT-RESTORING)"),
     ("tools/pr/gh_comment.py", "/private/tmp/claude-501/heatpump-optimizer-orchestrator/out/sync-201.md",
      "the literal body path of the #541 defect, kept as the fixture the poster must refuse"),
     ("tools/pr/gh_comment.py", '"/private/tmp/x/out/body.md"', "a fixture path the poster's self-test feeds it"),
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index 8ad7b7965..8a0ca5119 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -566,6 +566,7 @@ EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
 # The step a job restores its graders from the base commit in: the jobs that
 # hold it are the pull-request direction's whole population.
 RESTORE_STEP = "- name: Restore the check source from the base commit"
+WORKFLOWS = ".github/workflows"
 
 
 def job_text(text: str, job: str) -> str:
@@ -574,10 +575,24 @@ def job_text(text: str, job: str) -> str:
 
 
 def restore_jobs(text: str) -> list[str]:
-    """Each governance.yml job that restores its check source from the base."""
+    """Each job of one workflow's text that restores its check source from the base."""
     return [j for j in re.findall(r"^  ([a-z][\w-]*):\n", text, re.M) if RESTORE_STEP in job_text(text, j)]
 
 
+def restoring_jobs(root: Path) -> dict[str, tuple[str, str, str]]:
+    """Every job of every workflow under .github/workflows/ that restores its
+    check source from the base: key -> (the workflow's path, the job, the
+    workflow's text). The key is the job's name, `<workflow stem>/<job>` where
+    two workflows share one. The enumeration rule is `RESTORE_STEP`'s text over
+    the directory, not a list of names: a job added with the step is graded."""
+    found = []
+    for wf in sorted((root / WORKFLOWS).glob("*.y*ml")):
+        text = wf.read_text()
+        found += [(wf.relative_to(root).as_posix(), j, text) for j in restore_jobs(text)]
+    names = [j for _, j, _ in found]
+    return {j if names.count(j) == 1 else f"{Path(w).stem}/{j}": (w, j, t) for w, j, t in found}
+
+
 def restored_hit(names, specs, at_tip, covers) -> list[str]:
     """The diff's paths a job grades with the base's copy of: covered by its
     restore pathspecs and held by the base tip. Only there do the head's and
@@ -602,7 +617,9 @@ def pinned_runs(text: str, root: Path | None = None) -> list[tuple[str, str, tup
     out = []
     for job in restore_jobs(text):
         body = "\n".join(l for l in job_text(text, job).splitlines() if not l.lstrip().startswith("#"))
-        for prog, rest in re.findall(r"(?:node|python3(?: -I)?)\s+([\w./-]+\.(?:mjs|py))([^;&|\n]*)", body):
+        body = body.replace("\\\n", " ")  # a run line continued with a backslash is one line
+        for prog, rest in re.findall(r"(?:node|python3(?: -I)?|bash)\s+([\w./-]+\.(?:mjs|py|sh))([^;&|\n]*)", body):
+            rest = rest.split(">")[0]  # a stdout redirect is the run's own capture
             run = (job, prog, tuple(shlex.split(rest)))
             if (root is None or (root / prog).is_file()) and run not in out:
                 out.append(run)
@@ -617,11 +634,34 @@ GRADER_EXEMPT = {
 }
 
 
+# What a pull-request run reads off the event or the API, which the predictor
+# stands in for: tokens it can name, files it can write, and the inputs it
+# cannot (a run line naming one is PARTIAL, and its result is never a pass).
+PR_BODY = "/tmp/pr-body.md"
+PR_FILES = {"/tmp/pr-commits.tsv": "empty", "/tmp/pr-files.txt": "names", "/tmp/pr-existing.txt": "added"}
+PR_DROPPED = {"${RED_ARGS[@]}", "${CS_BASE_REPEATS:+--base-repeats}", "$INTENDED", "<"}
+PR_TOKENS = ("$PR_BASE", "$PR_HEAD", "$BASE_REF", "$HEAD_REF", "$PR_NUMBER", "$PR_TITLE", "$(cat /tmp/pr-author.txt)")
+GRADER_PARTIAL = {
+    ("budget-raise-gate", "budget_raise_gate.py", "--base", "--head", "--pr"):
+        "the live pull-request reviews, the mandate comments and the PR number",
+    ("pr-contract", "policy_lint.mjs", "--pr-body", "--head", "--base", "--title", "--author", "--commits-file",
+     "--paths-file", "--existing-file"): "the PR's live title, author, commits and red-check list",
+    ("pr-contract", "preflight.sh"): "the intended-file list",
+}
+GRADER_EXEMPT[("pr-contract", "codescan_wait.py", "--pr", "--base")] = "it queries the code-scanning API and grades no file"
+
+
+# The remedy a refusal carries when the refusing program is itself in the diff:
+# the pull request cannot reach the base's copy that grades it.
+BOOTSTRAP = ("BOOTSTRAP: no change in this pull request reaches the base's copy; move the registration to "
+             "unpinned data the grader reads, or split p1 grader / p2 artifact (fixer.md, decision 0013 Consequences)")
+
+
 def run_key(job: str, prog: str, argv) -> tuple[str, ...]:
     return (job, Path(prog).name, *(a for a in argv if a.startswith("--")))
 
 
-def ci_tree_run(root: Path, tip: str, job: str, steps) -> tuple[str, subprocess.CompletedProcess | None]:
+def ci_tree_run(root: Path, tip: str, job: str, steps, workflow: str | None = None) -> tuple[str, subprocess.CompletedProcess | None]:
     """Run `steps` (each a function of the tree, its runner and a scratch
     directory) where CI's pull-request run of `job` runs them: the merge of
     HEAD into the base tip (base first), the job's restore pathspecs checked
@@ -639,15 +679,15 @@ def ci_tree_run(root: Path, tip: str, job: str, steps) -> tuple[str, subprocess.
     try:
         env = throwaway_git_clone(root, r, "-q", "--shared", "--no-checkout")
 
-        def run(*a: str) -> subprocess.CompletedProcess:
-            return subprocess.run(a, cwd=r, env=env, capture_output=True, text=True)
+        def run(*a: str, input: str | None = None) -> subprocess.CompletedProcess:
+            return subprocess.run(a, cwd=r, env=env, input=input, capture_output=True, text=True)
 
         run("git", "update-ref", "refs/remotes/origin/main", tip)
         run("git", "checkout", "-q", "--detach", tip)
         if run("git", "merge", "-q", "--no-ff", "-m", f"Merge {head} into {tip}", head).returncode:
             return "unmerged", None
         shutil.rmtree(r / ".claude" / "workflows" / "vendor", ignore_errors=True)
-        specs = agreement_py.restore_specs((r / agreement_py.WORKFLOW).read_text(), job)
+        specs = agreement_py.restore_specs((r / (workflow or agreement_py.WORKFLOW)).read_text(), job)
         (tmp / "pinned.list").write_text(run("git", "diff", "--no-renames", "--name-only", "-z", EMPTY_TREE, tip, "--", *specs).stdout)
         run("git", "checkout", tip, f"--pathspec-from-file={tmp / 'pinned.list'}", "--pathspec-file-nul")
         out = None
@@ -672,14 +712,13 @@ def keyed_jobs(root: Path, base_ref: str) -> tuple[str, dict[str, list[str]], ob
     wf = root / agreement_py.WORKFLOW
     if not wf.is_file():
         return "", {}, agreement_py
-    text = wf.read_text()
     names = (git(root, "diff", "--name-only", "--no-renames", f"{tip}...HEAD") or "").split()
     at_tip = set((git(root, "ls-tree", "-r", "--name-only", tip) or "").splitlines())
     keyed = {}
-    for job in restore_jobs(text):
+    for key, (_, job, text) in restoring_jobs(root).items():
         hit = restored_hit(names, agreement_py.restore_specs(text, job), at_tip, agreement_py.covers)
         if hit:
-            keyed[job] = hit
+            keyed[key] = hit
     return tip, keyed, agreement_py
 
 
@@ -732,65 +771,111 @@ def grader_runs(text: str, root: Path, job: str) -> list[tuple[str, tuple[str, .
             if j == job and run_key(j, prog, argv) not in GRADER_EXEMPT.keys() | AGREEMENT_RUNS]
 
 
-def grader_gaps(text: str) -> list[str]:
+def grader_gaps(text) -> list[str]:
     """A run line the arm cannot run as CI does (a runner token `RUN_TOKENS`
     does not map), and an exemption no run line still holds. Empty is the
-    population closed over governance.yml."""
-    runs = pinned_runs(text)
+    population closed over the workflows (one text or several)."""
+    texts = [text] if isinstance(text, str) else list(text)
+    runs = [r for t in texts for r in pinned_runs(t)]
     gaps = [f"{job}: {prog} {' '.join(argv)} passes {a!r}, which RUN_TOKENS does not map"
             for job, prog, argv in runs for a in argv if "$" in a and a not in RUN_TOKENS
+            and a not in PR_TOKENS and a not in PR_DROPPED
             and not any(a.startswith(t) and a[len(t):].startswith("/") for t in RUN_TOKENS)]
     held = {run_key(job, prog, argv) for job, prog, argv in runs}
     gaps += [f"GRADER_EXEMPT: no run line still holds {' '.join(e)}" for e in GRADER_EXEMPT if e not in held]
     return gaps
 
 
-def grader_preds(root: Path, base_ref: str) -> list[tuple[str, str]]:
-    """Each run of each restoring job the diff keys (`restored_hit`), as CI
-    runs it on the pull request (`ci_tree_run`): every `grader_runs` program,
-    restored or the head's own, since a head copy that loads a restored file
-    grades with the base's copy of it too. The jobs run side by side, one CI
-    tree each; a refusal names the run and the restored paths that keyed it."""
+def grader_preds(root: Path, base_ref: str, body: str | None = None,
+                 notes: list | None = None) -> list[tuple[str, str]]:
+    """Each run of each restoring job the diff keys (`restored_hit`), in every
+    workflow `restoring_jobs` enumerates, as CI runs it on the pull request
+    (`ci_tree_run`): every `grader_runs` program, restored or the head's own,
+    since a head copy that loads a restored file grades with the base's copy of
+    it too. The jobs run side by side, one CI tree each; a refusal names the run
+    and the restored paths that keyed it. A run reading the event or the API
+    (`PR_TOKENS`, `PR_FILES`, the `body`) gets the predictor's stand-in; one in
+    `GRADER_PARTIAL` is noted as run without its inputs, whatever it returns, and
+    a run needing the body is skipped, noted, without one."""
     from concurrent.futures import ThreadPoolExecutor
     tip, keyed, agreement_py = keyed_jobs(root, base_ref)
     if not keyed:
         return []
-    text = (root / agreement_py.WORKFLOW).read_text()
+    homes = restoring_jobs(root)
+    body = Path(body).read_text() if body else None  # the argument is the body file's path
+    head = (git(root, "rev-parse", "HEAD") or "").strip()
+    branch = (git(root, "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
+    subject = (git(root, "log", "-1", "--format=%s") or "").strip()
+    paths = lambda *f: git(root, "diff", "--no-renames", "--name-only", *f, f"{tip}...HEAD") or ""
+    ctx = {"$PR_BASE": tip, "$PR_HEAD": head, "$BASE_REF": "main", "$HEAD_REF": branch, "$PR_NUMBER": "0",
+           "$PR_TITLE": subject, "$(cat /tmp/pr-author.txt)": "hpo-author[bot]"}  # the REST login policy_lint accepts
+    said: list[str] = []
 
-    def one(job: str) -> list[tuple[str, str]]:
-        hit, results = keyed[job], []
+    def one(key: str) -> list[tuple[str, str]]:
+        wf, job, text = homes[key]
+        hit, results = keyed[key], []
 
         def step(prog, argv):
             def grade(r, run, tmp):
-                args = [RUN_TOKENS[a](r, tmp) if a in RUN_TOKENS else
-                        next((RUN_TOKENS[t](r, tmp) + a[len(t):] for t in RUN_TOKENS if a.startswith(t + "/")), a)
-                        for a in argv]
-                cmd = (sys.executable, "-I", prog) if prog.endswith(".py") else ("node", prog)
-                out = run(*cmd, *args)
+                key_ = run_key(job, prog, argv)
+                part = next((why for k, why in GRADER_PARTIAL.items() if key_[:len(k)] == k), None)
+                files = {PR_BODY: body, "/tmp/pr-commits.tsv": "", "/tmp/pr-files.txt": paths(),
+                         "/tmp/pr-existing.txt": paths("--diff-filter=a")}
+                if PR_BODY in argv and body is None:
+                    said.append(f"GRADER SKIPPED {job}: {Path(prog).name} reads the pull-request body; "
+                                f"pass --body to grade it as CI does")
+                    return subprocess.CompletedProcess((), 0, "", "")
+                for f, text_ in files.items():
+                    (tmp / Path(f).name).write_text(text_ or "")
+                args, stdin = [], None
+                for i, a in enumerate(argv):
+                    if a == "$INTENDED":  # the roster-owned closes: stood in by every issue the body closes
+                        args += sorted(set(re.findall(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+#(\d+)", body or "", re.I)))
+                        continue
+                    if a in PR_DROPPED and a != "<" or (a == "<" or (i and argv[i - 1] == "<")):
+                        if i and argv[i - 1] == "<":
+                            stdin = (tmp / Path(a).name).read_text()
+                        continue
+                    a = ctx.get(a, a)
+                    a = str(tmp / Path(a).name) if a in files else a
+                    args.append(RUN_TOKENS[a](r, tmp) if a in RUN_TOKENS else
+                                next((RUN_TOKENS[t](r, tmp) + a[len(t):] for t in RUN_TOKENS if a.startswith(t + "/")), a))
+                cmd = (sys.executable, "-I", prog) if prog.endswith(".py") else ("bash" if prog.endswith(".sh") else "node", prog)
+                out = run(*cmd, *args, input=stdin)
+                if part:
+                    said.append(f"GRADER PARTIAL {job}: {Path(prog).name} ran without {part}; its result is "
+                                f"not a pass, a clean run grades only what it could read")
+                    if "reviews could not be read" in out.stdout:
+                        return subprocess.CompletedProcess(out.args, 0, out.stdout, out.stderr)  # the missing input, not a verdict
                 if out.returncode:
-                    results.append((prog, argv, out))
+                    results.append((prog, argv, out, part))
                 return subprocess.CompletedProcess(out.args, 0, out.stdout, out.stderr)  # run every step
             return grade
         runs = grader_runs(text, root, job)
         try:
-            state, _ = ci_tree_run(root, tip, job, tuple(step(p, a) for p, a in runs))
+            state, _ = ci_tree_run(root, tip, job, tuple(step(p, a) for p, a in runs), wf)
         except (OSError, StopIteration, ValueError) as e:
             return [(job, f"GRADER UNRUN {type(e).__name__}: {e}")]
         if state == "unmerged":
             return [(job, f"GRADER UNMERGED: HEAD does not merge into {tip[:12]}, and CI runs nothing "
                           f"on a conflict; merge the base first")]
         preds = []
-        for prog, argv, out in results:
+        for prog, argv, out, part in results:
             lines = [l.strip() for l in out.stdout.splitlines() if l.strip()] or \
                 [f"rc {out.returncode}: {out.stderr.strip()[-200:]}"]
             first = next((l for l in lines if l.startswith(("ERROR", "FAIL", "REFUSED", "BLIND", "DEAD", "MISSING",
                                                             "NOT WIRED", "STALE", "DRIFT", "SELF-TEST FAILED"))
                           and "probe, expected" not in l), lines[-1])
             label = " ".join((Path(prog).name, *argv))
-            preds.append((job, f"GRADER {label} REFUSED by the base's copy, over {over(hit)}: {first[:240]}"))
+            preds.append((job, f"GRADER {label} REFUSED by the base's copy, over {over(hit)}: {first[:240]}"
+                               + (f" (partial: ran without {part})" if part else "")
+                               + (f" -- {BOOTSTRAP}" if prog in hit else "")))
         return preds
     with ThreadPoolExecutor(max_workers=len(keyed)) as pool:
-        return [p for preds in pool.map(one, sorted(keyed)) for p in preds]
+        out = [p for preds in pool.map(one, sorted(keyed)) for p in preds]
+    if notes is not None:
+        notes += sorted(set(said))
+    return out
 
 
 def orphans(changed, closure):
@@ -896,7 +981,7 @@ def predict(root: Path, base_ref: str, pairs: set | None = None,
         ("wiring", lambda: wiring_preds(root, changed)),
         ("mutants", lambda: mutant_preds(root, changed)),
         ("agreement", lambda: agreement_preds(root, base_ref)),
-        ("graders", lambda: grader_preds(root, base_ref)),
+        ("graders", lambda: grader_preds(root, base_ref, body, notes)),
         ("no-recording", lambda: no_recording(root, base, changed, closure)),
         ("under-scoped", lambda: under_scoped(root, base, changed, tracked, closures,
                                               inert_reads, closure, pairs, scripts)),
@@ -1148,8 +1233,10 @@ def main(argv: list[str] | None = None) -> int:
                f"`--apply-inert` repairs the {inert} INERT READS, the lines "
                f"above the rest" if inert else
                "the lines above name each arm's repair")
+        boot = sum(1 for j, l in preds if is_red(j, l) and "BOOTSTRAP:" in l)
+        tail = ("repair before the handoff; " if boot < reds else "") + who
         print(f"CI PREDICT: {reds} predicted red(s) on {', '.join(jobs)} "
-              f"against {base[:12]} -- repair before the handoff; {who}")
+              f"against {base[:12]} -- {tail}" + (f" ({boot} BOOTSTRAP: split or move, not repair)" if boot else ""))
     else:
         ran = args.record_self_tests or args.only == "self-test-reads"
         seen = (" unless a changed file's own self-test makes it" if ran else "")
@@ -1359,14 +1446,20 @@ def graders_self_test(root: Path) -> int:
        keys("dev/governance/config/corpus_excluded.json") == [])
     ck("a restored path the base tip lacks keys no job (nothing to restore it from)",
        keys("tools/policy/vendor/markdown-it.min.js", tracked - {"tools/policy/vendor/markdown-it.min.js"}) == [])
-    runs = {run_key(*r) for r in pinned_runs(text, root)}
-    made = {run_key(j, p, a) for j in jobs for p, a in grader_runs(text, root, j)}
+    homes = restoring_jobs(root)
+    texts = sorted({t for _, _, t in homes.values()})
+    listed = (git(root, "grep", "-c", "--", RESTORE_STEP, "HEAD", "--", WORKFLOWS + "/") or "")
+    ck("the arm's job set is every restoring step the workflows hold (the enumeration rule's count)",
+       len(homes) == sum(int(l.rsplit(":", 1)[1]) for l in listed.splitlines()) and len(homes) > len(jobs),
+       f"{len(homes)} jobs, grep {listed!r}")
+    runs = {run_key(*r) for t in texts for r in pinned_runs(t, root)}
+    made = {run_key(j, p, a) for _, j, t in homes.values() for p, a in grader_runs(t, root, j)}
     want = {("policy-docs", "policy_lint.mjs"), ("policy-docs", "policy_lint.mjs", "--hooks"),
             ("wave-script", "check-wave-script.mjs"), ("env-matrix", "policy_lint_envmatrix.mjs")}
     ck("the arm makes every pinned run but the agreement arm's and the exempt", made == runs - AGREEMENT_RUNS -
        GRADER_EXEMPT.keys() and want <= made and not made & (AGREEMENT_RUNS | GRADER_EXEMPT.keys()), str(made))
-    ck("every pinned run line is runnable as CI runs it (null control: no gap)", grader_gaps(text) == [],
-       str(grader_gaps(text)))
+    ck("every pinned run line is runnable as CI runs it (null control: no gap)", grader_gaps(texts) == [],
+       str(grader_gaps(texts)))
     odd = text.replace("node tools/policy/check-wave-script.mjs;", "node tools/policy/check-wave-script.mjs $ODD;", 1)
     ck("a run line passing a token RUN_TOKENS does not map is a gap", odd != text and any("$ODD" in g for g in grader_gaps(odd)))
     unexempt = text.replace("--report", "--reprt")
@@ -1384,10 +1477,26 @@ def graders_self_test(root: Path) -> int:
              "for (const f of fs.readdirSync('corpus').sort()) {\n  if (EXCLUDED.has(f)) continue\n"
              "  const gate = execFileSync('python3', ['g/gate.py', f]).toString().trim()\n"
              "  if (!lib.ok(f) || gate !== 'ok') { console.log(`ERROR ${f}`); process.exit(1) }\n}\n")
+    # A second workflow's restoring job (not governance.yml's), and a third whose
+    # run line reads the pull request's live state (GRADER_PARTIAL).
+    other = workflow.replace("policy-docs", "other-job").replace("g/*.mjs", "h/*.mjs").replace("g/*.py", "h/*.py") \
+        .replace("'g/vendor'", "'h/vendor'").replace("g/grade.mjs", "h/check.mjs")
+    third = ("jobs:\n  gate:\n    steps:\n"
+             "      - name: Restore the check source from the base commit\n        run: |\n"
+             '          git diff --name-only -z "$(git hash-object -t tree /dev/null)" "$PINNED" -- \\\n'
+             "            'h/*.py' > \"$RUNNER_TEMP/pinned.list\"\n"
+             "      - name: Grade\n        run: |\n"
+             '          python3 -I h/gate2.py \\\n            --base "$PR_BASE" --head "$PR_HEAD" --pr "$PR_NUMBER"\n')
+    check = "import fs from 'fs'\nfor (const f of fs.readdirSync('corpus').sort()) {\n" \
+            "  if (f.startsWith('bad2')) { console.log(`ERROR ${f}`); process.exit(1) }\n}\n"
+    g = globals()
+    g["GRADER_PARTIAL"][("gate", "gate2.py", "--base", "--head", "--pr")] = "the live reviews (self-test stand-in)"
     base_files = {".github/workflows/governance.yml": workflow, "g/grade.mjs": grade,
                   "g/vendor/lib.js": "exports.ok = f => !f.startsWith('bad')\n",
                   "g/gate.py": "import sys\nprint('no' if 'worse' in sys.argv[1] else 'ok')\n",
                   "data/excluded.json": "[]\n", "corpus/good.md": "x\n",
+                  ".github/workflows/other.yml": other, "h/check.mjs": check,
+                  ".github/workflows/third.yml": third, "h/gate2.py": "import sys\nprint('ERROR ' + ' '.join(sys.argv[1:]))\nsys.exit(1)\n",
                   "tools/policy/agreement_py.py": (root / "tools" / "policy" / "agreement_py.py").read_text()}
 
     def app(t):
@@ -1395,7 +1504,16 @@ def graders_self_test(root: Path) -> int:
     inline = {"g/grade.mjs": lambda s: s.replace("...JSON", "'bad1.md', ...JSON"), "corpus/bad1.md": app("x\n")}
     vendored = {"g/vendor/lib.js": lambda s: s.replace("!f.startsWith('bad')", "true"), "corpus/bad1.md": app("x\n")}
     gated = {"g/gate.py": lambda s: s.replace("'worse' in", "'never' in"), "corpus/worse.md": app("x\n")}
-    cases = [("an exclusion written into the restored grader is predicted red (#2916's shape)", inline, True,
+    cases = [("a second workflow's restored grader edited so the head passes what the base refuses is predicted red, "
+              "job by job (the class, not governance.yml's three)",
+              {"h/check.mjs": lambda s: s.replace("'bad2'", "'never'"), "corpus/bad2.md": app("x\n")}, True,
+              "GRADER check.mjs REFUSED by the base's copy, over h/check.mjs: ERROR bad2.md"),
+             ("the same workflow with its program unedited and the corpus alone changed is not run "
+              "(null control)", {"corpus/bad2.md": app("x\n")}, True, None),
+             ("a run line reading the pull request's live state is run, predicted with what it ran without, and noted "
+              "partial", {"h/gate2.py": app("# a comment\n")}, True,
+              "GRADER gate2.py --base"),
+             ("an exclusion written into the restored grader is predicted red (#2916's shape)", inline, True,
               "GRADER grade.mjs REFUSED by the base's copy, over g/grade.mjs: ERROR bad1.md"),
              ("an edit to a vendored file the grader requires is predicted red (round 3's markdown-it.min.js)",
               vendored, True, "over g/vendor/lib.js: ERROR bad1.md"),
@@ -1426,14 +1544,24 @@ def graders_self_test(root: Path) -> int:
             run("git", "add", "-A")
             if commit:
                 run("git", "commit", "-qm", label)
-            got = grader_preds(r, tip)
-            ok = (any(j == "policy-docs" and want in l for j, l in got) if want else not got)
-            ck(label, ok, str(got))
+            nl: list[str] = []
+            got = grader_preds(r, tip, None, nl)
+            who = "gate" if "live state" in label else "other-job" if "second workflow" in label else "policy-docs"
+            ok = (any(j == who and want in l for j, l in got) if want else not got)
+            m = re.match(r"GRADER (\S+) REFUSED by the base's copy, over (\S+):", want or "")
+            if want and who != "gate":  # the remedy rides the line exactly when the refusing program is in the over-list
+                ok = ok and all(("BOOTSTRAP:" in l) == bool(m and m[2].endswith(m[1])) for _, l in got)
+            if who == "gate":
+                ok = ok and any(l.startswith("GRADER PARTIAL gate") and "not a pass" in l for l in nl) \
+                    and any("(partial: ran without" in l for _, l in got)
+            else:
+                ok = ok and not nl
+            ck(label, ok, str((got, nl)))
     finally:
         shutil.rmtree(tmp, ignore_errors=True)
-    g = globals()
+    GRADER_PARTIAL.pop(("gate", "gate2.py", "--base", "--head", "--pr"), None)
     real = g["grader_preds"]
-    g["grader_preds"] = lambda _root, _base: [("policy-docs", "GRADER sentinel")]
+    g["grader_preds"] = lambda _root, _base, *_a: [("policy-docs", "GRADER sentinel")]
     try:
         _, preds, _ = predict(root, "HEAD", only="graders")
     finally:
@@ -1469,7 +1597,7 @@ def self_test_reads_self_test(root: Path) -> int:
         (t / f).write_text("# throwaway_git.py --self-test\n")
         listed = {h: [f, h], n: [f, n], f: [f]}
 
-        def run(files, reads, inert_reads, changed=(f,), why=None):
+        def run(files, reads, inert_reads, changed=(f,), why=None, own=()):
             def record(_root, _f, out):
                 calls.append(_f)
                 out.write_text(json.dumps({"script": _f, "rc": 0, "files": [_f, *files],
@@ -1478,9 +1606,10 @@ def self_test_reads_self_test(root: Path) -> int:
             calls, notes = [], []
             closure.CLOSURES = t / "closures.json"
             ir = {i: [f], **inert_reads}
-            closure.write_closures(closure.CLOSURES, {"closures": listed, "inert_reads": ir})
+            tbl = {**listed, f: [f, *own]}  # `own`: reads the file's own key lists and its hosts' do not
+            closure.write_closures(closure.CLOSURES, {"closures": tbl, "inert_reads": ir})
             try:
-                preds = self_test_reads(t, set(changed), listed, ir, closure,
+                preds = self_test_reads(t, set(changed), tbl, ir, closure,
                                         record=record, notes=notes)
             finally:
                 closure.CLOSURES = saved
@@ -1497,6 +1626,10 @@ def self_test_reads_self_test(root: Path) -> int:
              + plain in p[0][1]),
             ("null control: a record inside the host's closure is not",
              run([], [], {}), lambda p, c, n: p == [] and c == [f]),
+            ("a read in the file's own closure but not the host's is graded under the host's key "
+             "(null control for the file-key mutant: grading under the file's own key passes it)",
+             run([plain], [], {}, own=(plain,)), lambda p, c, n: len(p) == 1 and f"UNDER-SCOPED {h}: "
+             + plain in p[0][1]),
             ("a self-test the recorder cannot finish is a note, never a red",
              run([inert], [inert], {}, why="not recorded in 180 s"), lambda p, c, n: p == [] and len(n) == 1),
             ("null control: a file the diff does not change is never recorded",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
