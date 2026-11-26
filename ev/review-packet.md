# Review packet #3912
head: 8e0391b08fa316937564766964e3e13c3a1fb97d
base: 1d3077736d4a7ced6ec15d9aec29f6bcf40fbae8

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139916584185 success
arch-score / arch-score id=139928148691 success
arm id=139913140192 skipped
budget-raise-gate / budget-raise-gate id=139928148522 success
cancel-superseded id=139927520829 success
codeql id=139928151048 skipped
codeql / Analyze (actions) id=139915638440 success
codeql / Analyze (javascript-typescript) id=139915638465 success
codeql / Analyze (python) id=139915638485 success
gate id=139929309774 failure
governance id=139928151863 skipped
governance / env-matrix id=139915638656 success
governance / instrument-self-tests id=139915638688 success
governance / policy-docs id=139915638564 success
governance / record id=139915641465 skipped
governance / wave-script id=139915638693 success
hassfest id=139928152019 skipped
hassfest / hassfest id=139915638313 success
kernel-points id=139928151307 skipped
pr-contract id=139929313482 skipped
prelude id=139927521132 success
refresh id=139927520639 success
sweep-self id=139930047615 skipped
tests id=139928150826 skipped
tests / arch-instrument id=139918878501 in_progress
tests / briefs id=139915638516 success
tests / browser id=139918878459 success
tests / claims-autofix id=139937483666 skipped
tests / closure-scope id=139915638694 success
tests / closures id=139918878553 in_progress
tests / coverage id=139918878558 success
tests / coverage-ratchet id=139935804123 success
tests / fast (3.14) id=139918878533 success
tests / graders-head-copy id=139935804197 success
tests / mutation id=139915638563 success
tests / mutation-autofix id=139919480269 skipped
tests / mutation-pins id=139919479834 skipped
tests / nightly-ha id=139918881367 skipped
tests / nightly-status id=139915638727 failure
tests / replay id=139918878679 in_progress
tests / typing id=139918878398 success
validate id=139928151182 skipped
validate / validate-hacs id=139915638562 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 8e0391b08fa316937564766964e3e13c3a1fb97d in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified PYTHONPATH=tests/hastub python3 -c "import sys; sys.path[:0]=['tests']; import replay as r; c=r.controls(); print(len(c), sum(not x[1] for x in c))"
             python3 runs an inline script rather than a file
  unverified python3 -c "import sys,yaml; sys.path[:0]=['tests']; import replay as r; t=open('.github/workflows/tests.yml').read(); print(r.replay_timeout_minutes(t), yaml.safe_load(t)['jobs']['replay']['timeout-minutes'])"
             python3 runs an inline script rather than a file
  unverified python3 -c "import sys,subprocess; sys.path[:0]=['tests']; import replay as r; b=r.replay_timeout_minutes(subprocess.run(['git','show','origin/main:.github/workflows/tests.yml'],capture_output=True,text=True).stdout); h=r.replay_timeout_minutes(open('.github/workflows/tests.yml').read()); [print(w, b, r.headroom_offenders(w,b) or 'ok', h, r.headroom_offenders(w,h) or 'ok') for w in (772.0,836.1,1518.1,1476.4,1798.0,1751.8)]"
             python3 runs an inline script rather than a file
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py select --base $(git merge-base origin/main HEAD)
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         bash tools/pr/app_push.sh --self-test
             `tools/pr/app_push.sh` is in the tree at this head
  ok         python3 -I tools/pr/ci_predict.py --self-test
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 -I dev/audit/harnesses/owner_only_channel.py
             `dev/audit/harnesses/owner_only_channel.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 9 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head 8e0391b08fa316937564766964e3e13c3a1fb97d, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/.github/workflows/tests.yml b/.github/workflows/tests.yml
index ae96fc9e2f..af4c2dd8f4 100644
--- a/.github/workflows/tests.yml
+++ b/.github/workflows/tests.yml
@@ -1444,7 +1444,12 @@ jobs:
   # `replay_reach`. Never on every pull request: a blanket per-PR lane is
   # refused for good. Unrequired, and its verdict is about the pull request's
   # own code: it grades nothing (codeowners_gap.py's rule). tests/entities.py
-  # pins the reach and the wiring.
+  # pins the reach and the wiring. The cap is sized from the lane's own cost
+  # budget: the owner fixture's `cpu_ratio` budget (tests/replay.py
+  # COST_BUDGETS) at the worst seconds per unit measured is about 38.6 min of
+  # lane, and 45 leaves headroom over it. tests/replay.py reads this value and
+  # goes red each night when the lane's wall time leaves too little of it
+  # (`headroom_offenders`).
   replay:
     needs: [closure-scope]
     if: >-
@@ -1452,7 +1457,7 @@ jobs:
       && github.event_name == 'pull_request'
       && needs.closure-scope.outputs.replay == 'true'
     runs-on: ubuntu-latest
-    timeout-minutes: 30
+    timeout-minutes: 45
     env:
       HPO_JOB_GRADES: nothing
     steps:
diff --git a/dev/programme/delivery/3912.md b/dev/programme/delivery/3912.md
new file mode 100644
index 0000000000..63f907a119
--- /dev/null
+++ b/dev/programme/delivery/3912.md
@@ -0,0 +1 @@
+- [#3912](https://github.com/tvofi/heatpump_optimizer/pull/3912) — **open**, ci(replay): raise the replay job timeout to 45 min and check its headroom (FG-4)
diff --git a/tests/replay.py b/tests/replay.py
index 9c954c1912..616e567189 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -602,10 +602,21 @@ COST_CLASS_GAP_MS = 2.0
 #: is fixture-independent and stays on the fixtures not named here, which the
 #: driver requires to exist.
 COST_ARMS_SKIPPED: dict[str, str] = {
-    "owner-2026-10-30-away.json": "a real install's solve: 16 cycles, about 12 "
-    "CPU-minutes a replay, so four would overrun the replay job; the arms run on "
-    "the synthetic fixture",
+    "owner-2026-10-30-away.json": "a real install's solve: 16 cycles, most of the "
+    "lane's wall time (its own 'cycles over' line), so four would overrun the "
+    "replay job; the arms run on the synthetic fixture",
 }
+#: The pull-request ``replay`` job in this file, whose ``timeout-minutes`` the
+#: lane checks its own wall time against (``headroom_offenders``).
+REPLAY_WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
+#: The job's seconds before ``tests/replay.py`` starts: checkout, Python and
+#: the pinned install (about 20 s on the runs P-R11-REPLAY-TIMEOUT measured).
+REPLAY_JOB_SETUP_S = 20.0
+#: The share of the job's remaining time the lane may use. The nightly
+#: ``slow`` job runs the same lane under a much larger cap, so the check goes
+#: red there while the pull-request arm still finishes, and names the cap to
+#: raise before that arm starts timing out.
+REPLAY_HEADROOM_SHARE = 0.8
 #: Fixtures that declare away coverage: their ``controls.away`` must hold an
 #: active command and their replay must carry it for at least one cycle
 #: (``away_offenders``'s ``expect_commanded``). A design choice: coverage is
@@ -965,6 +976,28 @@ def arms_skip_offenders(skipped: set[str], committed: set[str]) -> list[str]:
     return out
 
 
+def replay_timeout_minutes(workflow: str) -> int | None:
+    """The ``replay`` job's ``timeout-minutes`` in tests.yml's text, or None
+    when the job or its cap is not there (the caller reads None as red)."""
+    m = re.search(r"\n  replay:\n(?:    .*\n|[ \t]*\n)*?    timeout-minutes: (\d+)\n", workflow)
+    return int(m.group(1)) if m else None
+
+
+def headroom_offenders(wall_s: float, cap_minutes: int | None) -> list[str]:
+    """The lane's wall time over ``REPLAY_HEADROOM_SHARE`` of what the
+    pull-request job leaves it under ``cap_minutes``: the lane is growing
+    toward the cap, and the job will soon be cancelled with no verdict."""
+    if cap_minutes is None:
+        return [f"no replay timeout-minutes in {REPLAY_WORKFLOW.name}"]
+    limit = REPLAY_HEADROOM_SHARE * (cap_minutes * 60 - REPLAY_JOB_SETUP_S)
+    if wall_s <= limit:
+        return []
+    return [f"lane wall time {wall_s:.1f} s > {REPLAY_HEADROOM_SHARE} x "
+            f"({cap_minutes} min - {REPLAY_JOB_SETUP_S:.0f} s) = {limit:.1f} s; raise the "
+            f"replay job's timeout-minutes to at least "
+            f"{math.ceil((wall_s / REPLAY_HEADROOM_SHARE + REPLAY_JOB_SETUP_S) / 60)}"]
+
+
 def away_covered_offenders(covered: frozenset[str] | set[str],
                            committed: set[str]) -> list[str]:
     """``AWAY_COVERED`` naming a fixture that is not committed: a misspelt
@@ -1246,6 +1279,20 @@ def controls() -> list[tuple[str, bool, str]]:
     pair("cycle_cost:arms_skipped_committed_only",
          arms_skip_offenders({"gone.json"}, {"a.json"}),
          arms_skip_offenders({"a.json"}, {"a.json", "b.json"}))
+    # Nightly lane wall times (P-R11-REPLAY-TIMEOUT): 1798.0 s on 2026-11-25
+    # is over the 30-minute job's headroom and inside 45's; 836.1 s on
+    # 2026-11-16 is inside both. A cap the workflow does not carry is red.
+    pair("headroom:over_the_cap", headroom_offenders(1798.0, 30),
+         headroom_offenders(1798.0, 45) + headroom_offenders(836.1, 30))
+    pair("headroom:cap_unread", headroom_offenders(1.0, None), headroom_offenders(1.0, 30))
+    job = "\n  replay:\n    needs: [x]\n\n    timeout-minutes: 45\n  next:\n"
+    res.append(("control:headroom:reads_the_replay_job",
+                replay_timeout_minutes(job) == 45
+                and replay_timeout_minutes(job.replace("  replay:", "  other:")) is None
+                and replay_timeout_minutes(job.replace("    timeout", "      timeout")) is None
+                and replay_timeout_minutes(job.replace("    timeout-minutes: 45\n  next:\n",
+                                                       "  next:\n    timeout-minutes: 45\n")) is None,
+                f"read {replay_timeout_minutes(job)}"))
     pair("away:covered_names_are_committed",
          away_covered_offenders({"owner-2026-10-30-awya.json"},
                                 {"owner-2026-10-30-away.json"}),
@@ -3169,7 +3216,12 @@ def main(argv: list[str] | None = None) -> int:
     wrong = arms_skip_offenders(set(COST_ARMS_SKIPPED), committed)
     R.check("the doubled-cost arms are skipped on committed fixtures only, never all",
             not wrong, " | ".join(wrong) + f"; this run perturbed {perturbed}")
-    print(f"\nreplay lane wall time {time.monotonic() - began:.1f} s")
+    wall_s = time.monotonic() - began
+    print(f"\nreplay lane wall time {wall_s:.1f} s")
+    cap = replay_timeout_minutes(REPLAY_WORKFLOW.read_text())
+    wrong = headroom_offenders(wall_s, cap)
+    R.check("lane wall time within the pull-request replay job's headroom", not wrong,
+            " | ".join(wrong) or f"{wall_s:.1f} s under timeout-minutes {cap}")
     return R.close("replay checks")
 
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
