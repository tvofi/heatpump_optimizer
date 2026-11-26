# Review packet #3908
head: 60bc4b3b3db63a345b8adc5f18c5e03aae48723b
base: dbdc71faea358a95a7b33840ed252b0d8a646a31

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139952944334 success
arch-score / arch-score id=139953556172 success
arm id=139945614182 skipped
budget-raise-gate / budget-raise-gate id=139953556157 success
cancel-superseded id=139949937062 success
codeql id=139953558807 skipped
codeql / Analyze (actions) id=139948877058 success
codeql / Analyze (javascript-typescript) id=139948876871 success
codeql / Analyze (python) id=139948876794 success
gate id=139957989183 failure
governance id=139953557763 skipped
governance / env-matrix id=139948876785 success
governance / instrument-self-tests id=139948876740 success
governance / policy-docs id=139948877249 success
governance / record id=139948880232 skipped
governance / wave-script id=139948876856 success
hassfest id=139953557606 skipped
hassfest / hassfest id=139948876991 success
kernel-points id=139953559618 skipped
pr-contract id=139957992232 skipped
prelude id=139949937832 success
refresh id=139949937510 success
sweep-self id=139959431325 skipped
tests id=139953558760 skipped
tests / arch-instrument id=139951486423 success
tests / briefs id=139948877272 success
tests / browser id=139951486254 success
tests / claims-autofix id=139964938141 skipped
tests / closure-scope id=139948876898 success
tests / closures id=139951486563 in_progress
tests / coverage id=139951486465 in_progress
tests / fast (3.14) id=139951486297 success
tests / mutation id=139948877167 success
tests / mutation-autofix id=139953618595 skipped
tests / mutation-pins id=139953616790 skipped
tests / nightly-ha id=139951489190 skipped
tests / nightly-status id=139948877011 failure
tests / replay id=139951488483 skipped
tests / typing id=139951486499 success
validate id=139953559031 skipped
validate / validate-hacs id=139948877042 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at 60bc4b3b3db63a345b8adc5f18c5e03aae48723b in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/harnesses/prepr_6d_arms.py <commit> [<file> ...]
             `dev/audit/harnesses/prepr_6d_arms.py` is in the tree at this head
  ok         dev/audit/rca/open_prepr_6d.sh 6671786843
             `dev/audit/rca/open_prepr_6d.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/prepr_6d_arms.py e3cb5c019b464a770cc7c6fe2fbc858ed29debf7
             `dev/audit/harnesses/prepr_6d_arms.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/prepr_6d_arms.py 026ea0ea9b3dc32ee9f672e7bc78f4b6aeaffd96
             `dev/audit/harnesses/prepr_6d_arms.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/prepr_6d_arms.py <commit> custom_components/heatpump_optimizer/currency.py
             `dev/audit/harnesses/prepr_6d_arms.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff e3cb5c019b464a770cc7c6fe2fbc858ed29debf7
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head 60bc4b3b3db63a345b8adc5f18c5e03aae48723b, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/dev/audit/harnesses/prepr_6d_arms.py b/dev/audit/harnesses/prepr_6d_arms.py
new file mode 100644
index 0000000000..27563ff39a
--- /dev/null
+++ b/dev/audit/harnesses/prepr_6d_arms.py
@@ -0,0 +1,105 @@
+#!/usr/bin/env python3
+"""Step 6d's predictor timed per arm over one fixed diff, at one tree (R10-RCA-OPEN-PREPR-SLOW, C4).
+
+    python3 dev/audit/harnesses/prepr_6d_arms.py <commit> [<file> ...]
+
+In a throwaway worktree of <commit>, commits one comment line appended to each
+<file> (default `TOUCH`, the paths of slim-p2's diff at 6671786843 that a gate
+cannot scope, code and prose, that still exist), then runs that tree's own
+`tools/pr/ci_predict.py --base <commit> --record-self-tests`, prepr's 6d call,
+with each arm, each restoring job of GRADER and each STEP REPLAY replay timed.
+The diff is the same bytes at any <commit> where the files exist, so two
+commits run on one host, seconds apart, compare the predictor and nothing else:
+`<merge base>` is the before, `<fixed head>` the after. Prints one
+`ARM <name> <s>` line per arm, `JOB` per restoring job, `REPLAY` per replay,
+then `wall_s`, `predict_sha1` (a sha1 of the sorted PREDICT lines: the
+before/after identity check `open_prepr_6d.sh` prints) and `predict_lines`,
+`left_to_ci` (the steps the replay budget left to CI) and the predictor's
+last line. Hours at a full diff on a 4-CPU container; run it in the background.
+"""
+from __future__ import annotations
+
+import hashlib
+import os
+import subprocess
+import sys
+import tempfile
+import time
+from pathlib import Path
+
+TOUCH = (".github/workflows/governance.yml", ".github/workflows/tests.yml", "tests/entities.py",
+         "tools/pr/ci_predict.py", "tools/audit/seat/merge_train.py", "tools/audit/seat/body_push.sh",
+         "tools/audit/seat/bus.sh", "tools/audit/seat/postmerge.py", "tools/pr/app_approve.sh",
+         "dev/governance/roles/fixer.md", "CLAUDE.md")
+
+# Runs inside the throwaway tree: wraps the module's own functions, changes none.
+TIMER = r'''
+import sys, time
+sys.path.insert(0, "tools/pr")
+import ci_predict as cp
+def say(*a):
+    print(*a, file=sys.stderr, flush=True)
+def wrap(name, label):
+    f = getattr(cp, name, None)
+    if f is None:
+        return
+    def timed(*a, **k):
+        t = time.monotonic(); r = f(*a, **k)
+        say(label(a, r), f"{time.monotonic() - t:.1f}")
+        return r
+    setattr(cp, name, timed)
+wrap("ci_tree_run", lambda a, r: f"JOB {a[2]}")
+wrap("replay_step", lambda a, r: f"REPLAY rc={r}")
+arms = cp.run_arms
+def run_arms(arms_, only, record):
+    out = []
+    for name, arm in arms_:
+        if cp.arm_runs(name, only, record):
+            t = time.monotonic(); p = arm(); out += p
+            say(f"ARM {name}", f"{time.monotonic() - t:.1f}")
+    return out
+cp.run_arms = run_arms
+sys.exit(cp.main(sys.argv[1:]))
+'''
+
+
+def main(argv: list[str]) -> int:
+    if not argv:
+        print(__doc__)
+        return 2
+    commit, files = argv[0], tuple(argv[1:]) or TOUCH
+    repo = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
+    with tempfile.TemporaryDirectory() as d:
+        wt = Path(d) / "t"
+        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "--detach", str(wt), commit], check=True)
+        try:
+            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=wt, text=True).strip()
+            held = [f for f in files if (wt / f).is_file()]
+            for f in held:
+                with open(wt / f, "a") as fh:
+                    fh.write("\n<!-- prepr_6d_arms touch -->\n" if f.endswith(".md") else "\n# prepr_6d_arms touch\n")
+            subprocess.run(["git", "-c", "user.name=h", "-c", "user.email=h@h", "commit", "-qam",
+                            "prepr_6d_arms touch"], cwd=wt, check=True)
+            (Path(d) / "timer.py").write_text(TIMER)
+            env = dict(os.environ, PYTHONPATH="tests/hastub")
+            t = time.monotonic()
+            r = subprocess.run([sys.executable, str(Path(d) / "timer.py"), "--base", sha, "--record-self-tests"],
+                               cwd=wt, env=env, capture_output=True, text=True)
+            wall = time.monotonic() - t
+        finally:
+            subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)])
+    timed = [l for l in r.stderr.splitlines() if l.startswith(("ARM ", "JOB ", "REPLAY "))]
+    pred = sorted(l for l in r.stdout.splitlines() if l.startswith("PREDICT"))
+    left = [l for l in r.stdout.splitlines() if l.startswith("NOTE    LEFT TO CI")]
+    print(f"at={sha} touched={len(held)} rc={r.returncode}")
+    print("\n".join(timed))
+    print(f"wall_s={wall:.0f}")
+    print(f"predict_sha1={hashlib.sha1(''.join(l + chr(10) for l in pred).encode()).hexdigest()} "
+          f"predict_lines={len(pred)}")
+    print(f"left_to_ci={left[0].split()[4] if left else 0}")
+    print((r.stdout.strip().splitlines() or ["(no output)"])[-1])
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/harnesses/r10_seat_selftests_mutants.py b/dev/audit/harnesses/r10_seat_selftests_mutants.py
index 610a80d401..f31ef6473e 100644
--- a/dev/audit/harnesses/r10_seat_selftests_mutants.py
+++ b/dev/audit/harnesses/r10_seat_selftests_mutants.py
@@ -685,6 +685,8 @@ MUTANTS = [
      'hit = {n: r for n, r in head.items() if names_changed(root, r, changed)}', 'hit = {}'),
     ("ci_predict-4", "tools/pr/ci_predict.py", '                if b:\n', '                if True:\n'),
     ("ci_predict-5", "tools/pr/ci_predict.py", '        if any(n in text for n in names):\n', '        if False:\n'),
+    # R10-RCA-OPEN-PREPR-SLOW C4: the STEP REPLAY budget leaves the steps past it to CI.
+    ("ci_predict-6", "tools/pr/ci_predict.py", '        if spent >= budget:\n', '        if False:\n'),
     ("local_alerts-1", "tools/pr/local_alerts.py", "        if not prs:\n            return 3,",
      "        if False:\n            return 3,"),
     ("local_alerts-2", "tools/pr/local_alerts.py", 'and j.get("conclusion") == "success")', ")"),
diff --git a/dev/programme/delivery/3908.md b/dev/programme/delivery/3908.md
new file mode 100644
index 0000000000..4a29b9bdb9
--- /dev/null
+++ b/dev/programme/delivery/3908.md
@@ -0,0 +1 @@
+- [#3908](https://github.com/tvofi/heatpump_optimizer/pull/3908) — **open**, prepr.sh: per-step elapsed seconds and a STEP REPLAY budget (R11-PREPR-STEP-TIMING)
diff --git a/tests/closures.json b/tests/closures.json
index 3d381134e0..c3b3b8f90d 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4715,6 +4715,7 @@
    "dev/audit/harnesses/nightly_drain_breakdown.py",
    "dev/audit/harnesses/owner_only_channel.py",
    "dev/audit/harnesses/owner_only_mutants.py",
+   "dev/audit/harnesses/prepr_6d_arms.py",
    "dev/audit/harnesses/prepr_slot_nested.py",
    "dev/audit/harnesses/pulse_replay.py",
    "dev/audit/harnesses/r10_2205_replay_cost_arms.py",
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index 08cf2fad59..34c1722934 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -41,8 +41,10 @@ scoped to what the three-dot diff adds or changes, so a red main already
 carries is never charged to a branch. Nothing here runs a test, a recording
 or a mutant: seconds, never a heavy script, but for AGREEMENT, which runs the
 lane in a throwaway clone (about 10 s) and only on a diff to a path its job
-restores, and three opt-in by `--record-self-tests` (prepr's 6d passes it):
-GRADER, minutes where keyed (measured in its record), SELFTEST SCOPE (main's
+restores, and four opt-in by `--record-self-tests` (prepr's 6d passes it):
+GRADER, minutes where keyed (its slowest restoring job bounds it, the jobs
+running side by side; `dev/audit/rca/open_prepr_6d.sh` times a head), STEP
+REPLAY (below, held to `STEP_REPLAY_BUDGET`), SELFTEST SCOPE (main's
 drift step over the gated self-tests whose own script the diff changes,
 traced in a scratch clone: `selftest_scope_preds`), and SELF-TEST READS,
 a changed file's own `--self-test`, recorded by `closure._exec_record` and
@@ -65,7 +67,10 @@ an over-approximation at worst, the direction `_fold_inert_reads` keeps.
 STEP REPLAY, opt-in with SELF-TEST READS, runs each `instrument-self-tests`
 step whose run text names a changed file as the runner does, and predicts a
 red the base's step of that name does not share (#3245: a self-test summary
-line removed while governance.yml still grepped it).
+line removed while governance.yml still grepped it). Those steps are ones CI
+runs on the pull request anyway, one after another: past `STEP_REPLAY_BUDGET`
+seconds (`HPO_STEP_REPLAY_BUDGET_S`) the rest are left to CI in one `LEFT TO
+CI` note naming them, the steps naming a changed file replayed first.
 
 `--body FILE` adds a fifth arm, the carry check `pr-contract` runs on the body
 (R10-CI-LAYOUT-P2 carry 6): `tools/audit/carry_audit.py`'s own `audit`, imported
@@ -582,14 +587,28 @@ STEP_REPLAY_TIMEOUT_ENV = "HPO_STEP_REPLAY_TIMEOUT_S"
 TIMED_OUT = -124  # never a bash rc: bash exits 0..255
 
 
-def step_replay_timeout() -> float:
-    """The replay bound in seconds: the environment's, else SELF_TEST_TIMEOUT."""
+# The arm's whole budget (R10-RCA-OPEN-PREPR-SLOW, C4). Every step it replays
+# is one `instrument-self-tests` runs on the pull request anyway, a context no
+# merge requires, so past the budget the rest is left to CI, noted by name,
+# never predicted: a diff keying most of the job's steps replayed them one by
+# one for longer than the rest of prepr together.
+STEP_REPLAY_BUDGET_ENV = "HPO_STEP_REPLAY_BUDGET_S"
+STEP_REPLAY_BUDGET = 600
+
+
+def env_seconds(name: str, default: float) -> float:
+    """A positive number of seconds from the environment's ``name``, else ``default``."""
     import os
     try:
-        v = float(os.environ.get(STEP_REPLAY_TIMEOUT_ENV, ""))
+        v = float(os.environ.get(name, ""))
     except ValueError:
-        return SELF_TEST_TIMEOUT
-    return v if v > 0 else SELF_TEST_TIMEOUT
+        return default
+    return v if v > 0 else default
+
+
+def step_replay_timeout() -> float:
+    """The replay bound in seconds: the environment's, else SELF_TEST_TIMEOUT."""
+    return env_seconds(STEP_REPLAY_TIMEOUT_ENV, SELF_TEST_TIMEOUT)
 
 
 def replay_step(tree: Path, run: str) -> int:
@@ -616,10 +635,25 @@ def step_replay_preds(root: Path, base: str, changed: set[str],
     base's is green -- so a step this container cannot run (a missing binary,
     an unset variable: red at both ends) is a note left to CI, never the branch's."""
     import tempfile
+    import time
     head = instrument_steps(root)
     readers = recorded_readers(root, changed)  # mut:readers
     hit = {n: r for n, r in head.items() if n in readers or names_changed(root, r, changed)}
-    ran = {n: replay_step(root, r) for n, r in hit.items()}
+    # Within the budget, a step whose run text names a changed file first
+    # (#3245's shape), then a recorded reader, then one keyed through a tool's text.
+    order = sorted(hit, key=lambda n: (not any(c in hit[n] for c in changed), n not in readers))
+    budget, spent, ran, left = env_seconds(STEP_REPLAY_BUDGET_ENV, STEP_REPLAY_BUDGET), 0.0, {}, []
+    for n in order:
+        if spent >= budget:
+            left.append(n)
+            continue
+        t0 = time.monotonic()
+        ran[n] = replay_step(root, hit[n])
+        spent += time.monotonic() - t0
+    if left:
+        (notes if notes is not None else []).append(
+            f"LEFT TO CI {len(left)} of {len(hit)} instrument-self-tests step(s) the diff keys, past the "
+            f"{budget:g} s replay budget ({STEP_REPLAY_BUDGET_ENV}): {', '.join(left)}")
     for n, rc in ran.items():
         if rc == TIMED_OUT:
             (notes if notes is not None else []).append(
@@ -788,6 +822,32 @@ def step_replay_self_test(root: Path) -> int:
             got = len(step_replay_preds(t, base, changed))
             print(f"  {'ok  ' if got == want else 'FAIL'} {label}")
             bad += got != want
+        # env_seconds: only a positive number overrides; empty, junk, 0 and negative keep the default.
+        import os
+        from unittest import mock
+        got = []
+        for raw in ("", "x", "0", "-1", "2.5"):
+            with mock.patch.dict(os.environ, {"HPO_ENV_SECONDS_PROBE": raw}):
+                got.append(env_seconds("HPO_ENV_SECONDS_PROBE", 7))
+        good = got == [7, 7, 7, 7, 2.5]
+        print(f"  {'ok  ' if good else 'FAIL'} env_seconds keeps the default for empty, junk, 0 and a negative; "
+              f"null control: 2.5 overrides it")
+        bad += not good
+        # C4's bound (R10-RCA-OPEN-PREPR-SLOW): a's step names a.sh, c's reaches it through
+        # c.sh's text; under a spent budget a is replayed first and c is left to CI, by name.
+        # An empty budget is env_seconds' default, so the null-control arm needs no unset.
+        for budget, want, left in (("0.001", ["a"], True), ("", ["a", "c"], False)):
+            notes = []
+            with mock.patch.dict(os.environ, {STEP_REPLAY_BUDGET_ENV: budget}):
+                got = sorted(l.split(":")[0].removeprefix("STEP REPLAY ")
+                             for _, l in step_replay_preds(t, base, {"tools/a.sh"}, notes))
+            said = any(x.startswith("LEFT TO CI 1 of 2 ") and x.endswith(": c") for x in notes)
+            held = got == want and said == left  # its own name: a deleted line cannot inherit `good`
+            print(f"  {'ok  ' if held else 'FAIL'} " + (
+                "a spent replay budget replays the step naming the changed file first and leaves "
+                "the rest to CI, named" if budget else
+                "null control: under the default budget both steps are replayed and none is left"))
+            bad += not held
         wf = (t / INSTRUMENT_WF).read_text()
         (t / INSTRUMENT_WF).write_text(wf + "      - name: e\n        id: e\n        if: ${{ !cancelled() && steps.d.outcome == 'failure' }}\n"
                                        "        run: bash tools/e.sh\n      - name: f\n        id: f\n"
@@ -1585,7 +1645,8 @@ def main(argv: list[str] | None = None) -> int:
     ap.add_argument("--record-self-tests", action="store_true",
                     help="also record each changed file's own self-test a gate script runs "
                          "(SELF-TEST READS: seconds per file) and run each restoring job's programs "
-                         "the diff keys (GRADER: minutes where keyed), so prepr's 6d passes it")
+                         "the diff keys (GRADER: minutes where keyed) and the instrument-self-tests steps it keys "
+                         "(STEP REPLAY, within STEP_REPLAY_BUDGET), so prepr's 6d passes it")
     ap.add_argument("--self-test", action="store_true")
     ap.add_argument("--rekey-body", metavar="BODY", help="re-key BODY's moved `## Unpinned sites` lines in place")
     ap.add_argument("--from", dest="frm", metavar="SHA", help="with --rekey-body: the code sha the keys were taken at")
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 3ab1dcbc33..594c8301d0 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -624,12 +624,17 @@ PY
   return 1
 }
 
-# Step 6d's whole body: tools/pr/ci_predict.py over the three-dot diff, read
-# statically -- no test or mutant runs, and the one recording is a changed
-# file's own self-test a gate script runs (SELF-TEST READS, the fifth
-# argument), so it costs seconds where
-# step 6b's recordings cost the scoped scripts' run time and are left to CI
-# under the owner's heavy-scripts rule (2026-10-07). It predicts `closures`'s
+# Step 6d's whole body: tools/pr/ci_predict.py over the three-dot diff. Its
+# default arms read the diff statically; the fifth argument adds the gated
+# arms (`GATED_ARMS`), which run code: a changed file's own self-test a gate
+# script runs (SELF-TEST READS), every program of each restoring job the diff
+# keys (GRADER, its jobs side by side), each instrument-self-tests step the
+# diff keys (STEP REPLAY, bounded by HPO_STEP_REPLAY_BUDGET_S, the rest left
+# to CI) and SELFTEST SCOPE. It costs seconds only on a diff keying none of
+# them: one the gate cannot scope runs GRADER's slowest job for minutes, which
+# dev/audit/rca/open_prepr_6d.sh times at one head (R10-RCA-OPEN-PREPR-SLOW,
+# C4). Step 6b's recordings are left to CI under the owner's heavy-scripts
+# rule (2026-10-07). It predicts `closures`'s
 # UNDER-SCOPED and INERT READS, entities' unclassified file and
 # a STALE PIN the diff itself stales (a stale pin main carries only warns),
 # which R9-RO-11's pre-study measured reddening this round's fix heads after
@@ -648,7 +653,7 @@ predict_line() { # base ref, [file the unpinned site keys are written to], [body
   fi
   local bf=""; [ -n "${3:-}" ] && [ -f "$3" ] && bf=$3   # pr-contract's carry check, when a body exists
   [ -n "${4:-}" ] && only="--only $4"   # a caller that needs one arm's answer, not every arm's
-  [ -n "${5:-}" ] && rec="--record-self-tests"   # 6d itself: the one arm that runs code (SELF-TEST READS)
+  [ -n "${5:-}" ] && rec="--record-self-tests"   # 6d itself: the gated arms, which run code (`GATED_ARMS`, above)
   # shellcheck disable=SC2086 # $only is empty or exactly "--only <arm>"; $rec is empty or one flag
   out=$(PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$1" ${bf:+--body "$bf"} $only $rec 2>&1); r=$?
   [ -n "${2:-}" ] && printf '%s\n' "$out" \
@@ -4216,11 +4221,34 @@ step "ref privacy" $? "$PRIVACY_LINE"'*) r=0 ;; *) r=1 ;; esac
   case "$out" in *'| AssertionError: the failing line'*) r=0 ;; *) r=1 ;; esac
   st "$r" 0 "and the refusal's failing lines"
   lg=$(sed -n '$s/.*full log: \([^ ]*\) .*/\1/p' <<<"$out")
-  case "$(tail -1 <<<"$out")" in 'PRE-PR: deadbeef 01 rc=1; full log: '"$SM"/prepr-log.*) r=0 ;; *) r=1 ;; esac
+  case "$(tail -1 <<<"$out")" in 'PRE-PR: deadbeef 01 rc=1 elapsed='[0-9]*'s; full log: '"$SM"/prepr-log.*) r=0 ;; *) r=1 ;; esac
   st "$r" 0 "the last line is the result with rc, naming a unique log under TMPDIR"
   [ -f "$lg" ] && [ -n "$(sed -n '/test_one PASSED/p' "$lg")" ]; st $? 0 "and that log holds the full output"
   out=$(sdrv 1); case "$out" in *'test_one PASSED'*'REFUSE   loud'*) r=0 ;; *) r=1 ;; esac
   st "$r" 0 "PREPR_VERBOSE=1 prints the full output on stdout"
+  # C3 (dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md): each step line leads its
+  # detail with the step's elapsed seconds, measured from the verdict line
+  # before it, and the result line carries the run's.
+  out=$(TMPDIR="$SM" bash -c "$sfn"'
+    rc=0 digest="" ORDER="" PREPR_LOG="" LOG_MARK=0 STEP_MARK=$SECONDS; summary_start
+    sleep 2; step "slow" 0 "slept"; step "noop" 0 "did nothing"; SECONDS=1000; summary_end deadbeef')
+  t=$(sed -nE 's/^  ok +slow +\[([0-9]+)s\] slept$/\1/p' <<<"$out")
+  [ "${t:-0}" -ge 2 ]; st $? 0 "a step stubbed to sleep 2 s prints an elapsed of at least 2 (C3)"
+  t=$(sed -nE 's/^  ok +noop +\[([0-9]+)s\] did nothing$/\1/p' <<<"$out")
+  case "$t" in 0|1) r=0 ;; *) r=1 ;; esac
+  st "$r" 0 "and a no-op step after it prints 0 or 1, so the field times the step, not the run (C3's null control)"
+  t=$(sed -nE 's/^PRE-PR: deadbeef 00 rc=0 elapsed=([0-9]+)s; .*/\1/p' <<<"$out")
+  case "$t" in 1000|1001) r=0 ;; *) r=1 ;; esac
+  st "$r" 0 "and the result line carries the run's elapsed read from the clock: SECONDS set to 1000 before summary_end prints 1000 or 1001, so a constant fails"
+  # The main flow's own stdout result line, run with the clock driven and git
+  # stubbed: its elapsed is the clock read, neither a constant nor absent.
+  pl=$(sed -n '/^echo "PRE-PR: /p' <<<"$flow")
+  out=$(bash -c 'git() { echo cafe; }; digest=07; SECONDS=730; '"$pl")
+  case "$out" in 'PRE-PR: cafe 07 elapsed='73[01]s) r=0 ;; *) r=1 ;; esac
+  st "$r" 0 "the main flow's stdout PRE-PR line carries the run's elapsed from the clock (SECONDS=730 prints 730 or 731)"
+  out=$(bash -c 'git() { echo cafe; }; digest=07; SECONDS=40; '"$pl")
+  case "$out" in 'PRE-PR: cafe 07 elapsed='4[01]s) r=0 ;; *) r=1 ;; esac
+  st "$r" 0 "and a different clock (SECONDS=40) prints 40 or 41, so the field tracks the clock"
   case "$flow" in *'step "merge-base" 0 "$BASE"
 summary_start'*'summary_end "$(git rev-parse HEAD)"
 exit $rc'*) r=0 ;; *) r=1 ;; esac
@@ -4372,19 +4400,24 @@ ORDER=""
 # verdict line, each refusal's own log lines (`refusal_lines`), and the result
 # line naming the log. `PREPR_VERBOSE=1` or `--verbose` keeps today's stdout.
 # Both pushers that run this mode read its rc alone, never its stdout.
-PREPR_LOG="" LOG_MARK=0
+# STEP_MARK is bash's $SECONDS at the last verdict line, so a step line's
+# elapsed field (`step`) is the time since the line before it, read with no
+# spawn: the step's own cost, not the run's (R10-RCA-OPEN-PREPR-SLOW, C3).
+PREPR_LOG="" LOG_MARK=0 STEP_MARK=$SECONDS
 say() {
   local l; l=$(printf '  %-8s %-22s %s' "$1" "$2" "${3:-}")
   printf '%s\n' "$l"; [ -z "$PREPR_LOG" ] || printf '%s\n' "$l" >&3
   [ -z "$PREPR_LOG" ] || LOG_MARK=$(wc -l <"$PREPR_LOG")
+  STEP_MARK=$SECONDS
 }
 refusal_lines() { # -> fd 3: the last 40 log lines since the previous verdict
   [ -n "$PREPR_LOG" ] || return 0
   tail -n +"$((LOG_MARK + 1))" "$PREPR_LOG" | tail -40 | sed 's/^/    | /' >&3
 }
-step() { # name, rc, detail
+step() { # name, rc, detail; the detail is led by the step's elapsed seconds
+  local t="[$((SECONDS - ${STEP_MARK:-0}))s]"
   digest="${digest}$2"
-  if [ "$2" -eq 0 ]; then say ok "$1" "${3:-}"; else refusal_lines; say REFUSE "$1" "${3:-}"; rc=1; fi
+  if [ "$2" -eq 0 ]; then say ok "$1" "$t ${3:-}"; else refusal_lines; say REFUSE "$1" "$t ${3:-}"; rc=1; fi
 }
 summary_start() { # -> stdout and stderr to $PREPR_LOG, fd 3 the real stdout; none under PREPR_VERBOSE=1
   [ "${PREPR_VERBOSE:-}" != 1 ] || return 0
@@ -4394,7 +4427,7 @@ summary_start() { # -> stdout and stderr to $PREPR_LOG, fd 3 the real stdout; no
 summary_end() { # head sha -> the result line on fd 3, naming the log
   [ -n "$PREPR_LOG" ] || return 0
   [ -z "$ORDER" ] || printf '  !!! %s: the push must follow at once (the full warning is in the log)\n' "$ORDER" >&3
-  echo "PRE-PR: $1 $digest rc=$rc; full log: $PREPR_LOG (PREPR_VERBOSE=1 prints it on stdout)" >&3
+  echo "PRE-PR: $1 $digest rc=$rc elapsed=${SECONDS}s; full log: $PREPR_LOG (PREPR_VERBOSE=1 prints it on stdout)" >&3
 }
 
 # --- 0. the body is not in a root other seats write to (`shared_root` above).
@@ -4804,7 +4837,8 @@ fi
 # --- 6d. the CI reds a static read of the diff predicts (`predict_line`), and
 # the reads each changed file's own self-test makes in a gate script that runs
 # it, recorded by CI's recorder (SELF-TEST READS, dev/audit/rca/R10-RCA-CLOSURE-ARGV.md):
-# seconds per such file, none on a diff that changes none.
+# seconds per such file, none on a diff that changes none; the other gated
+# arms' cost is `predict_line`'s comment's.
 UNPINNED_SITES=/tmp/prepr-unpinned.$$
 if [ -z "$REUSE" ]; then  # under PREPR_SKIP_CODE, `merged_steps` runs it on the merged tree
 PREDICT_LINE=$(predict_line origin/main "$UNPINNED_SITES" "${1:-}" "" record)
@@ -5024,6 +5058,6 @@ fi
 rm -f "${UNPINNED_SITES:-}"
 receipt_write "$rc" "${BODY:-}" "$RUN_START"
 echo
-echo "PRE-PR: $(git rev-parse HEAD) $digest"
+echo "PRE-PR: $(git rev-parse HEAD) $digest elapsed=${SECONDS}s"
 summary_end "$(git rev-parse HEAD)"
 exit $rc

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
