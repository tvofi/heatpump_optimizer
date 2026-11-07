# Review packet #3275
head: d6482b704bb11831c12001ffc0b0210a47c35483
base: f2a015142714383722bf49d7ab20d8398ec9674c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128289990132 success
arch-score / arch-score id=128299179581 success
arm id=128288686318 skipped
budget-raise-gate / budget-raise-gate id=128299179682 success
cancel-superseded id=128299179368 success
codeql id=128299218677 skipped
codeql / Analyze (actions) id=128289649603 success
codeql / Analyze (javascript-typescript) id=128289649595 success
codeql / Analyze (python) id=128289649557 success
gate id=128299179386 success
governance id=128299179788 skipped
governance / delivery-status id=128289649720 success
governance / delivery-status-publish id=128289651319 skipped
governance / env-matrix id=128289649638 success
governance / instrument-self-tests id=128289649754 success
governance / policy-docs id=128289649747 success
governance / record id=128289650459 skipped
governance / wave-script id=128289649660 success
hassfest id=128299179618 skipped
hassfest / hassfest id=128289649518 success
kernel-points id=128299179448 skipped
pr-contract id=128299180452 skipped
pr-contract / pr-contract id=128298817138 success
prelude id=128299179436 success
refresh id=128299178827 success
tests id=128299179537 skipped
tests / arch-instrument id=128289937419 success
tests / briefs id=128289649591 success
tests / browser id=128289937477 success
tests / ci-ratchet id=128298817805 skipped
tests / claims-autofix id=128292136805 skipped
tests / closure-scope id=128289649479 success
tests / closures id=128289937464 success
tests / closures-autofix id=128298818012 skipped
tests / coverage id=128289937588 success
tests / coverage-ratchet id=128294783336 success
tests / fast (3.14) id=128289937436 success
tests / graders-head-copy id=128294783333 success
tests / lane-proofs id=128294783281 success
tests / mutation id=128289649492 success
tests / mutation-autofix id=128289882057 skipped
tests / mutation-pins id=128289881159 skipped
tests / nightly-ha id=128289939024 skipped
tests / nightly-status id=128289649439 success
tests / replay id=128289938278 skipped
tests / typing id=128289937397 success
validate id=128299180275 skipped
validate / validate-hacs id=128289649640 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: d6482b704bb11831c12001ffc0b0210a47c35483 lacks origin/main 630bf533d838110be56ede0366756da3de0d941e; roster read at origin/main
NOTE body item 720a1bef: dismissed:recorded at the launcher step's comment; a deterministic arm is pr_args.sh's
NOTE body item 91bb838f: dismissed:the pull request's own first run is the probe
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh run view 42297617709 --json jobs --jq '.jobs[]|select(.name=="governance / instrument-self-tests")|.steps[]|[.name,.startedAt,.completedAt]|@tsv'
             gh run view: every long flag accepted
  ok         time bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_selftest_timeout.py replay <(git show 41aa9050f:.github/workflows/governance.yml) all
             `dev/audit/harnesses/r10_selftest_timeout.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_selftest_timeout.py replay .github/workflows/governance.yml all
             `dev/audit/harnesses/r10_selftest_timeout.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 759ec575e..f36563a70 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -265,13 +265,15 @@ jobs:
     # request whose every changed file is product (prelude.machinery).
     if: inputs.machinery != 'false'
     runs-on: ubuntu-latest
-    # 20, not 10: the seat self-tests below add about four minutes run
-    # serially on a seat (pr_args.sh's runs three times, through open_pr.sh
-    # and update_pr.sh), beside the job's three. 30, not 20: beatd.py's
-    # self-test is sleep-bound; with its mutants run serially this job took
-    # 26 min at #2916's ad1ba9adb. They now run four at a time
-    # (MUTANT_WORKERS), the self-test about 4.5 min, so the job is about
-    # 21 min of 30 (#2873's, without it, ran 16.5).
+    # 30 minutes. Run in line, this job's steps reached it: two main runs
+    # were cancelled there and its last four successful ones finished inside
+    # its final 90 s, mostly in five self-tests (prepr.sh's, beatd.py's, and
+    # pr_args.sh's once alone and once each through open_pr.sh and
+    # update_pr.sh), four of which wait far more than they compute. They start
+    # detached in the first step and are read in the last five
+    # (R10-HOTFIX-SELFTEST-TIMEOUT), so the job lasts as long as the longer
+    # of its in-line steps and prepr.sh's self-test, not as long as all of
+    # them added together.
     timeout-minutes: 30
     env:
       HPO_JOB_GRADES: nothing
@@ -285,6 +287,57 @@ jobs:
         with:
           node-version: "22"
 
+      # THE FIVE SLOWEST SELF-TESTS START HERE AND ARE READ AT THE END
+      # (R10-HOTFIX-SELFTEST-TIMEOUT). Run in line they were most of this
+      # job's wall time and two main runs hit the timeout; four of them wait
+      # far more than they compute (prepr.sh's alone keeps a core busy), so
+      # they overlap the steps below, each with its own log and exit status.
+      # pr_args.sh's self-test, which the three PR-tool steps each run, runs
+      # them one after another, as before: its mut:unlock arm observes a lock
+      # holder inside the 0.2 s it takes to notice its parent has gone, and
+      # under the CPU of all five at once it missed that window.
+      # prepr.sh's, the one that computes, runs at nice 10 for the same reason.
+      # Each keeps its own step at the end, under its old name, which prints
+      # that log and fails on that status -- every step still runs and still
+      # greps its tally. bg_wait fails a test whose launcher vanished without
+      # a status rather than waiting for the job timeout.
+      - name: Start the five slowest self-tests beside the rest of the job
+        run: |
+          set -euo pipefail
+          mkdir -p "$RUNNER_TEMP/bg"
+          cat > "$RUNNER_TEMP/bg/lib.sh" <<'LIB'
+          bg_run() { # <name> <command...>: run it, to <name>.log, its status to <name>.rc
+            local d="$RUNNER_TEMP/bg" r
+            if "${@:2}" > "$d/$1.log" 2>&1; then r=0; else r=$?; fi
+            echo "$r" > "$d/$1.rc.tmp" && mv "$d/$1.rc.tmp" "$d/$1.rc"
+          }
+          bg_pid() { # <pid> <name...>: the detached process each name's bg_wait watches
+            local p=$1; shift
+            for n in "$@"; do echo "$p" > "$RUNNER_TEMP/bg/$n.pid"; done
+          }
+          bg_start() { # <name> <command...>: bg_run detached
+            ( bg_run "$@" ) < /dev/null > /dev/null 2>&1 &
+            bg_pid "$!" "$1"
+          }
+          bg_wait() { # <name>: wait for it, print its log, return its status
+            local d="$RUNNER_TEMP/bg"
+            while ! test -f "$d/$1.rc"; do
+              if ! kill -0 "$(cat "$d/$1.pid")" 2> /dev/null && ! test -f "$d/$1.rc"; then
+                cat "$d/$1.log"; echo "$1: its launcher exited with no status" >&2; return 1
+              fi
+              sleep 5
+            done
+            cat "$d/$1.log"; return "$(cat "$d/$1.rc")"
+          }
+          LIB
+          . "$RUNNER_TEMP/bg/lib.sh"
+          bg_start prepr nice -n 10 bash -c 'if test -f tools/audit/prepr.sh; then bash tools/audit/prepr.sh --self-test; else bash tools/pr/prepr.sh --self-test; fi'
+          bg_start beatd python3 -I tools/audit/seat/beatd.py --self-test
+          ( bg_run open-pr bash tools/audit/seat/open_pr.sh --self-test
+            bg_run pr-args bash tools/audit/seat/pr_args.sh --self-test
+            bg_run update-pr bash tools/audit/seat/update_pr.sh --self-test ) < /dev/null > /dev/null 2>&1 &
+          bg_pid "$!" open-pr pr-args update-pr
+
       # EVERY STEP HERE DRIVES A PROGRAM THE PULL REQUEST CARRIES. A
       # self-test's verdict is about a program's own refusals, and the copy
       # that must answer is the one the pull request carries -- a lane run from
@@ -355,9 +408,6 @@ jobs:
       - name: Show the record-predicate sweep refusing its own perturbations
         run: if test -f tools/audit/record-predicate/sweep.mjs; then node tools/audit/record-predicate/sweep.mjs --self-test; else node tools/policy/record-predicate/sweep.mjs --self-test; fi
 
-      - name: Show the pre-PR self-check refusing its own fixtures
-        run: if test -f tools/audit/prepr.sh; then bash tools/audit/prepr.sh --self-test; else bash tools/pr/prepr.sh --self-test; fi
-
       - name: Show the push script's decisions refusing their own fixtures
         run: if test -f tools/audit/push.sh; then bash tools/audit/push.sh --self-test; else bash tools/pr/push.sh --self-test; fi
 
@@ -741,14 +791,6 @@ jobs:
           python3 -I tools/audit/seat/moved_paths.py --self-test | tee "$RUNNER_TEMP/moved-paths-self-test.txt"
           grep -Eq '^moved_paths self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/moved-paths-self-test.txt"
 
-      - name: Show the PR opener (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures
-        if: ${{ !cancelled() }}
-        run: |
-          set -o pipefail
-          bash tools/audit/seat/open_pr.sh --self-test | tee "$RUNNER_TEMP/open-pr-self-test.txt"
-          grep -Eq '^delivery_row self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/open-pr-self-test.txt"
-          grep -Eq '^pr_args self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/open-pr-self-test.txt"
-
       - name: Show the plan table refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
@@ -763,13 +805,6 @@ jobs:
           python3 -I tools/audit/seat/plan_page.py --self-test | tee "$RUNNER_TEMP/plan-page-self-test.txt"
           grep -Eq '^plan_page self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/plan-page-self-test.txt"
 
-      - name: Show the PR argument builder refusing its own fixtures
-        if: ${{ !cancelled() }}
-        run: |
-          set -o pipefail
-          bash tools/audit/seat/pr_args.sh --self-test | tee "$RUNNER_TEMP/pr-args-self-test.txt"
-          grep -Eq '^pr_args self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/pr-args-self-test.txt"
-
       - name: Show the dispatch cap refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
@@ -948,13 +983,6 @@ jobs:
           set -o pipefail
           bash tools/audit/seat/heartbeat.sh --self-test | tee "$RUNNER_TEMP/heartbeat-self-test.txt"
           grep -Eq '^heartbeat self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/heartbeat-self-test.txt"
-
-      - name: Show the supervised beat refusing its own fixtures
-        if: ${{ !cancelled() }}
-        run: |
-          set -o pipefail
-          python3 -I tools/audit/seat/beatd.py --self-test | tee "$RUNNER_TEMP/beatd-self-test.txt"
-          grep -Eq '^beatd self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/beatd-self-test.txt"
       - name: Show the beat's job rows refusing their own fixtures
         if: ${{ !cancelled() }}
         run: |
@@ -962,14 +990,6 @@ jobs:
           python3 -I tools/audit/seat/beat_jobs.py --self-test | tee "$RUNNER_TEMP/beat-jobs-self-test.txt"
           grep -Eq '^beat_jobs self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/beat-jobs-self-test.txt"
 
-      - name: Show the PR updater (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures
-        if: ${{ !cancelled() }}
-        run: |
-          set -o pipefail
-          bash tools/audit/seat/update_pr.sh --self-test | tee "$RUNNER_TEMP/update-pr-self-test.txt"
-          grep -Eq '^delivery_row self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/update-pr-self-test.txt"
-          grep -Eq '^pr_args self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/update-pr-self-test.txt"
-
       - name: Show the offline spy refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
@@ -1124,6 +1144,47 @@ jobs:
           sh tools/ci/alert_list_mutants.sh --self-test | tee "$RUNNER_TEMP/alert-list-mutants.txt"
           grep -Eq '^ALERT-LIST MUTANTS: every mutant refused$' "$RUNNER_TEMP/alert-list-mutants.txt"
 
+      # The five started beside the job above, read in their old order.
+      - name: Show the pre-PR self-check refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          . "$RUNNER_TEMP/bg/lib.sh"
+          bg_wait prepr
+
+      - name: Show the PR opener (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          . "$RUNNER_TEMP/bg/lib.sh"
+          bg_wait open-pr | tee "$RUNNER_TEMP/open-pr-self-test.txt"
+          grep -Eq '^delivery_row self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/open-pr-self-test.txt"
+          grep -Eq '^pr_args self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/open-pr-self-test.txt"
+
+      - name: Show the PR argument builder refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          . "$RUNNER_TEMP/bg/lib.sh"
+          bg_wait pr-args | tee "$RUNNER_TEMP/pr-args-self-test.txt"
+          grep -Eq '^pr_args self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/pr-args-self-test.txt"
+
+      - name: Show the supervised beat refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          . "$RUNNER_TEMP/bg/lib.sh"
+          bg_wait beatd | tee "$RUNNER_TEMP/beatd-self-test.txt"
+          grep -Eq '^beatd self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/beatd-self-test.txt"
+
+      - name: Show the PR updater (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          . "$RUNNER_TEMP/bg/lib.sh"
+          bg_wait update-pr | tee "$RUNNER_TEMP/update-pr-self-test.txt"
+          grep -Eq '^delivery_row self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/update-pr-self-test.txt"
+          grep -Eq '^pr_args self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/update-pr-self-test.txt"
+
   # THE LANES ABOVE RUN IN ONE ENVIRONMENT. Five separate assertions in this
   # repository were CORRECT and never RAN, because whether they run is decided
   # by a fact about the clone -- shallow or not, origin/main present or not,
diff --git a/dev/audit/harnesses/r10_selftest_timeout.py b/dev/audit/harnesses/r10_selftest_timeout.py
new file mode 100644
index 000000000..f70ba3c35
--- /dev/null
+++ b/dev/audit/harnesses/r10_selftest_timeout.py
@@ -0,0 +1,138 @@
+#!/usr/bin/env python3
+"""R10-HOTFIX-SELFTEST-TIMEOUT: instrument-self-tests' detached self-tests, against their mutants and as a replay.
+
+    python3 dev/audit/harnesses/r10_selftest_timeout.py                  # arms and mutants
+    python3 dev/audit/harnesses/r10_selftest_timeout.py replay WF MODE   # MODE: bg | all
+
+Run from the repository root. The default mode reads the bg_start/bg_wait
+library out of the launcher step of `.github/workflows/governance.yml`,
+exactly as the step writes it, and drives it over four planted commands: a
+pass with a tally (the control), a non-zero exit, a launcher killed before it
+writes a status, and a pass printing no tally; and the same through a
+chain of bg_run under one bg_pid, the launcher's form for pr_args.sh's three
+callers: a failing first link, a passing second, a chain killed in its first
+link read from its second. Each refusal arm must refuse
+and each control must pass, first on the library as committed (M0) and then
+on two mutants of its predicates: M1 returns 0 in place of the recorded
+status, M2 returns 0 for a launcher gone with no status. Prints one line per
+arm and mutant, and `RESULT survivors=<n>`; exit 1 when a mutant survived or
+M0 failed.
+
+`replay` runs the job's steps from WF in order, each `run:` in its own
+`bash --noprofile --norc -eo pipefail` with one RUNNER_TEMP, the runner's
+skip rule for a step without `!cancelled()` after a failure, and prints each
+step's seconds and the total. `bg` runs only the launcher and the steps that
+call bg_wait; `all` runs every step. WF may be any copy of the workflow, e.g.
+the merge base's from `git show`.
+"""
+import os
+import re
+import subprocess
+import sys
+import tempfile
+import time
+
+import yaml
+
+JOB = "instrument-self-tests"
+LAUNCHER = "Start the five slowest self-tests beside the rest of the job"
+WORKFLOW = ".github/workflows/governance.yml"
+TALLY = r"^x self-test: [1-9][0-9]* checks, 0 failed$"
+
+ARMS = r'''
+set -eo pipefail
+mkdir -p "$RUNNER_TEMP/bg"; . "$1"
+bg_start ok bash -c 'echo "x self-test: 3 checks, 0 failed"'
+bg_start bad bash -c 'echo "x self-test: 3 checks, 1 failed"; exit 7'
+bg_start killed bash -c 'sleep 600'
+bg_start notally bash -c 'echo hi'
+( bg_run c1 bash -c 'exit 3'; bg_run c2 bash -c 'echo "x self-test: 1 checks, 0 failed"' ) < /dev/null > /dev/null 2>&1 &
+bg_pid "$!" c1 c2
+( bg_run d1 bash -c 'sleep 600'; bg_run d2 true ) < /dev/null > /dev/null 2>&1 &
+bg_pid "$!" d1 d2
+sleep 2; kill -9 "$(cat "$RUNNER_TEMP/bg/killed.pid")" "$(cat "$RUNNER_TEMP/bg/d1.pid")"; wait 2> /dev/null || true
+( bg_wait c1 > /dev/null ) && echo "FAIL refuse chained bad" || echo "PASS refuse chained bad"
+( bg_wait c2 | grep -Eq "$2" ) && echo "PASS control chained tally" || echo "FAIL control chained tally"
+( bg_wait d2 > /dev/null 2>&1 ) && echo "FAIL refuse chain killed" || echo "PASS refuse chain killed"
+( bg_wait ok > /dev/null ) && echo "PASS control ok" || echo "FAIL control ok"
+( bg_wait bad > /dev/null ) && echo "FAIL refuse bad" || echo "PASS refuse bad"
+( bg_wait killed > /dev/null 2>&1 ) && echo "FAIL refuse killed" || echo "PASS refuse killed"
+( bg_wait notally | grep -Eq "$2" ) && echo "FAIL refuse notally" || echo "PASS refuse notally"
+( bg_wait ok | grep -Eq "$2" ) && echo "PASS control tally" || echo "FAIL control tally"
+'''
+
+MUTANTS = {
+    "M1": ('return "$(cat "$d/$1.rc")"', "return 0"),
+    "M2": ('echo "$1: its launcher exited with no status" >&2; return 1', "return 0"),
+}
+
+
+def steps(wf):
+    with open(wf) as f:
+        return yaml.safe_load(f)["jobs"][JOB]["steps"]
+
+
+def library(wf):
+    run = next(s["run"] for s in steps(wf) if s.get("name") == LAUNCHER)
+    return re.search(r"<<'LIB'\n(.*?)\nLIB\n", run, re.S).group(1)
+
+
+def arms(lib):
+    with tempfile.TemporaryDirectory() as d:
+        p = os.path.join(d, "lib.sh")
+        with open(p, "w") as f:
+            f.write(lib)
+        env = dict(os.environ, RUNNER_TEMP=d)
+        r = subprocess.run(["bash", "-c", ARMS, "arms", p, TALLY], env=env,
+                           capture_output=True, text=True, timeout=120)
+        return [ln for ln in r.stdout.splitlines() if ln.startswith(("PASS", "FAIL"))]
+
+
+def mutants():
+    lib = library(WORKFLOW)
+    base = arms(lib)
+    for ln in base:
+        print(f"M0 {ln}")
+    ok0 = len(base) == 8 and all(ln.startswith("PASS") for ln in base)
+    survivors = 0
+    for name, (old, new) in MUTANTS.items():
+        if lib.count(old) != 1:
+            print(f"{name} NOT APPLIED: {old!r} occurs {lib.count(old)} times")
+            survivors += 1
+            continue
+        fails = [ln for ln in arms(lib.replace(old, new)) if ln.startswith("FAIL")]
+        print(f"{name} {'KILLED by ' + '; '.join(fails) if fails else 'SURVIVED'}")
+        survivors += not fails
+    print(f"RESULT survivors={survivors}")
+    return 0 if ok0 and survivors == 0 else 1
+
+
+def replay(wf, mode):
+    env = dict(os.environ, RUNNER_TEMP=tempfile.mkdtemp())
+    failed, t0 = False, time.time()
+    for s in steps(wf):
+        if "run" not in s:
+            continue
+        if mode == "bg" and s["name"] != LAUNCHER and "bg_wait" not in s["run"]:
+            continue
+        if failed and "!cancelled()" not in s.get("if", ""):
+            print(f"SKIP          {s['name']}")
+            continue
+        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
+            f.write(s["run"])
+        a = time.time()
+        r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", f.name],
+                           env=env, capture_output=True, text=True)
+        os.unlink(f.name)
+        failed |= r.returncode != 0
+        print(f"{'OK  ' if r.returncode == 0 else 'FAIL'} {time.time() - a:7.1f}s {s['name']}", flush=True)
+        if r.returncode:
+            print((r.stdout + r.stderr)[-1500:], flush=True)
+    print(f"RESULT replay_seconds={time.time() - t0:.0f} failed={int(failed)}")
+    return int(failed)
+
+
+if __name__ == "__main__":
+    if sys.argv[1:2] == ["replay"]:
+        sys.exit(replay(sys.argv[2], sys.argv[3]))
+    sys.exit(mutants())
diff --git a/dev/programme/delivery/3275.md b/dev/programme/delivery/3275.md
new file mode 100644
index 000000000..146ec7693
--- /dev/null
+++ b/dev/programme/delivery/3275.md
@@ -0,0 +1 @@
+- [#3275](https://github.com/tvofi/heatpump_optimizer/pull/3275) — **open**, R10-HOTFIX-SELFTEST-TIMEOUT: hotfix selftest timeout (R10-HOTFIX-SELFTEST-TIMEOUT)
diff --git a/tests/closures.json b/tests/closures.json
index c71959796..fefe6ccb9 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4101,6 +4101,7 @@
    "dev/audit/harnesses/r10_savings_upgrade_month.py",
    "dev/audit/harnesses/r10_scores_envelope.py",
    "dev/audit/harnesses/r10_seat_selftests_mutants.py",
+   "dev/audit/harnesses/r10_selftest_timeout.py",
    "dev/audit/harnesses/r10_setpoint_boost.py",
    "dev/audit/harnesses/r10_setpoint_power.py",
    "dev/audit/harnesses/r10_shape_claim_controls.sh",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
