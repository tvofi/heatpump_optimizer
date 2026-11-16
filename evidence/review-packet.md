# Review packet #3654
head: 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e
base: 56ce2f695bcba5218444f52c04a5ed923a07d563

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=133098288061 queued
arm id=133094931790 skipped
budget-raise-gate / budget-raise-gate id=133098288023 success
cancel-superseded id=133096978369 queued
codeql id=133098289977 skipped
governance id=133098289521 skipped
hassfest id=133098289467 skipped
kernel-points id=133098289539 skipped
prelude id=133096978744 queued
refresh id=133096978730 queued
tests id=133098289384 skipped
validate id=133098289133 skipped

## Refusals
structure: tests/structure.py refuses the head merged with main: head does not merge cleanly with origin/main: ['100644 278971983f1373a9e81ff408205a0a1611dc7a0c 1\t.github/workflows/governance.yml', '100644 83ae8933aa3133c6dfb85f7ecff167c60ca6ea35 2\t.github/workflows/governance.yml']

## Advisories
none

## carry_audit at the head
NOTE body item 806e1101: R11-PRE-TOOLCHAIN-PIN
NOTE body item 9833c393: R11-PRE-TOOLCHAIN-PIN
NOTE body item a00789b0: R11-PRE-TOOLCHAIN-PIN
NOTE body item f7b54cbd: R11-PRE-TOOLCHAIN-PIN
NOTE body item 766671f4: R11-PRE-TOOLCHAIN-PIN
NOTE body item 1eaf8e55: R11-PRE-TOOLCHAIN-PIN
NOTE body item 6fd3d308: R11-PRE-TOOLCHAIN-PIN
NOTE body item 3e0749c4: R11-PRE-TOOLCHAIN-PIN
NOTE body item 0feb43b0: R11-PRE-PARALLEL-PIPELINE: R11-PRE-PARALLEL-PIPELINE resolved on origin/handoff/audit-r10-roster
NOTE body item a62b1fec: R11-PRE-TOOLCHAIN-PIN
NOTE body item 695d23a5: R11-PRE-TOOLCHAIN-PIN
CARRY-AUDIT: 11 finding item(s): 11 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         python3 -I tools/audit/seat/toolchain.py --self-test
             `tools/audit/seat/toolchain.py` is in the tree at this head
  ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 tools/audit/seat/prune_refs.py --self-test
             `tools/audit/seat/prune_refs.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/beat_jobs.py --self-test
             `tools/audit/seat/beat_jobs.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_toolchain_mutants.py
             `dev/audit/harnesses/r11_toolchain_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py record --step toolchain --step ref-pruner
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 921214bf42 --workdir <dir>
             `tests/closure.py` is in the tree at this head
  ok         tools/ci/gate.py changes the gate itself
             `tools/ci/gate.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  unverified git grep -n -E '\.\.origin/main|detach[^|]*origin/main|-B [^ ]+ origin/main|origin/main:\$?\{?(rel|tools)' -- tools/audit/seat tools/pr .claude/hooks ':!*selftest*' ':!*/instruments/*' ':!*/fixtures/*'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -ln "pr_args.sh" -- tools/audit/seat ':!*selftest*' ':!*.md'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -l "pr_tools_fresh" -- tools/audit/seat
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n -E 'fork_head\(|outside_is_mains' -- tools/audit/seat
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 16 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 278971983f..6c1012552b 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -504,6 +504,15 @@ jobs:
         if: steps.scope.outputs.scorecard == 'true'
         run: python3 -I tools/audit/seat/scorecard.py --self-test
 
+      # The stable tools ref (R11-PRE-TOOLCHAIN-PIN): behind's count over the
+      # seat paths and promote's refusals (absent, off main, not a fast-forward,
+      # machinery not green, a push that moved nothing), each beside the case
+      # that moves the ref, over a throwaway origin; GitHub is a fake.
+      - name: Show the stable tools ref promoting only a machinery-green commit of main, fast-forward
+        id: toolchain
+        if: steps.scope.outputs.toolchain == 'true'
+        run: python3 -I tools/audit/seat/toolchain.py --self-test
+
       # Decision 0018 section 5's two held-out checks (R11-PRE-ROUND-METRICS):
       # planted-defect recall's refusals and its count after the judge, and the
       # two-finder overlap estimate; each holds an empty input to unread, never
diff --git a/dev/audit/harnesses/r11_toolchain_mutants.py b/dev/audit/harnesses/r11_toolchain_mutants.py
new file mode 100644
index 0000000000..25c453f86b
--- /dev/null
+++ b/dev/audit/harnesses/r11_toolchain_mutants.py
@@ -0,0 +1,149 @@
+#!/usr/bin/env python3
+"""R11-PRE-TOOLCHAIN-PIN: each rule of the stable tools ref dies alone.
+
+Each mutant is one exact one-occurrence replacement in a COPY of tools/
+(never the tree); the mutated file's own `--self-test` is then run in the copy
+and must FAIL. Null control: M0 of each file, nothing mutated, must print
+failed=0. A pattern not found exactly once aborts.
+
+tools/audit/seat/toolchain.py:
+  M-absent-behind   behind no longer refuses an absent ref.
+  M-paths           behind counts every commit, not the seat paths.
+  M-from            behind ignores --from.
+  M-fetch           behind --fetch reads nothing from origin.
+  M-direction       behind counts what the checkout holds over the ref.
+  M-absent-promote  promote with no ref and no --init goes on.
+  M-init-present    --init is accepted while the ref exists.
+  M-offmain         a commit not on origin/main may be promoted.
+  M-ff              the fast-forward refusal is dropped (git's own push refusal then answers).
+  M-green-sha       promote <sha> no longer needs MACHINERY green.
+  M-green-walk      the walk takes its first concluded run, whatever it reads.
+  M-concluded       the walk reads a run that has not concluded.
+  M-stop-at-ref     the walk reads runs the ref already holds.
+  M-machinery       promotion reads PRODUCT, not MACHINERY.
+  M-held-count      one bad run is a hold.
+  M-held-any        a hold needs only one bad run among the newest three.
+  M-readback        a push that moved nothing is believed.
+  M-current-sha     promote <sha> at the ref's own commit is not CURRENT.
+  M-sha-filter      promote <sha> trusts the listing's head_sha filter.
+tools/audit/seat/prune_refs.py:
+  M-keep            the toolchain/* keep is dropped: the merged-ref rule deletes the tools ref.
+tools/ci/gate.py:
+  G-empty           the machinery tuple is empty.
+  G-unread-green    an unread verdict reads green.
+  G-skip-required   a skipped required member is not red.
+  G-cancelled-red   a cancelled member is red, not unread.
+  G-na              a skipped instrument-self-tests is read, not set aside.
+  G-neither         one required name is in neither verdict.
+
+    python3 dev/audit/harnesses/r11_toolchain_mutants.py
+
+EXPECTED RESULT mutants=26
+EXPECTED RESULT survived=0
+"""
+from __future__ import annotations
+
+import shutil
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = repo_root(__file__)
+TOOLCHAIN, PRUNE, GATE = "tools/audit/seat/toolchain.py", "tools/audit/seat/prune_refs.py", "tools/ci/gate.py"
+#: What a copy holds: the three targets' own directories and what their self-tests read.
+COPIED = ("tools/audit/seat", "tools/ci", "tools/policy/fixtures", "tests/throwaway_git.py", "tests/closures.json",
+          ".github/workflows")
+#: A plant is (file, old, new).
+PLANTS = {
+    "M-absent-behind": (TOOLCHAIN, '    if git("rev-parse", "-q", "--verify", f"{TRACKING}^{{commit}}")[0]:\n', "    if False:\n"),
+    "M-paths": (TOOLCHAIN, '*(() if every else ("--", *SEAT_PATHS)))', "*())"),
+    "M-from": (TOOLCHAIN, 'f"{frm}..{TRACKING}", *', 'f"HEAD..{TRACKING}", *'),
+    "M-fetch": (TOOLCHAIN, "    if fetch:\n", "    if False:\n"),
+    "M-direction": (TOOLCHAIN, 'f"{frm}..{TRACKING}", *', 'f"{TRACKING}..{frm}", *'),
+    "M-absent-promote": (TOOLCHAIN, "    if not old and not create:\n", "    if False:\n"),
+    "M-init-present": (TOOLCHAIN, "    if old and create:\n", "    if False:\n"),
+    "M-offmain": (TOOLCHAIN, '        if not SHA.fullmatch(new) or not ok("merge-base", "--is-ancestor", new, f"origin/{BASE}"):\n',
+                  "        if not SHA.fullmatch(new):\n"),
+    "M-ff": (TOOLCHAIN, '        if old and not ok("merge-base", "--is-ancestor", old, new):\n', "        if False:\n"),
+    "M-green-sha": (TOOLCHAIN, "        if v != gate_py().GREEN:\n", "        if False:\n"),
+    "M-green-walk": (TOOLCHAIN, "        if v == gate_py().GREEN:\n", "        if True:\n"),
+    "M-concluded": (TOOLCHAIN, '    for run in [r for r in runs if r.get("status") == "completed"][:SCAN_RUNS]:\n',
+                    "    for run in runs[:SCAN_RUNS]:\n"),
+    "M-stop-at-ref": (TOOLCHAIN, '        if at_or_behind(run.get("head_sha") or ""):\n', "        if False:\n"),
+    "M-machinery": (TOOLCHAIN, 'for j in jobs}, "push")[1]', 'for j in jobs}, "push")[0]'),
+    "M-held-count": (TOOLCHAIN, "    return len(read) >= HELD_RUNS and all(", "    return len(read) >= 1 and all("),
+    "M-held-any": (TOOLCHAIN, "HELD_RUNS and all(v != gate_py().GREEN", "HELD_RUNS and any(v != gate_py().GREEN"),
+    "M-readback": (TOOLCHAIN, "        if rc or listed.split()[:1] != [new]:\n", "        if rc:\n"),
+    "M-current-sha": (TOOLCHAIN, "    if sha == old and sha:\n", "    if False:\n"),
+    "M-sha-filter": (TOOLCHAIN, ' and r.get("head_sha") == sha]', "]"),
+    "M-keep": (PRUNE, "    if name == MAIN_REF or name.startswith(TOOLCHAIN_PREFIX):\n", "    if name == MAIN_REF:\n"),
+    "G-empty": (GATE, 'MACHINERY_JOBS = ("tests / arch-instrument", "tests / briefs", "tests / closures", "governance / policy-docs",\n'
+                      '                  "governance / wave-script", "governance / env-matrix", "governance / instrument-self-tests")\n',
+                "MACHINERY_JOBS = ()\n"),
+    "G-unread-green": (GATE, 'j[1] == "success" for j in ran) else UNREAD\n', 'j[1] == "success" for j in ran) else GREEN\n'),
+    "G-skip-required": (GATE, "               if n in REQUIRED[cls] or (jobs.get(n)", "               if (jobs.get(n)"),
+    "G-cancelled-red": (GATE, 'j[1] not in ("success", "cancelled") for j in ran)', 'j[1] not in ("success",) for j in ran)'),
+    "G-na": (GATE, '(jobs.get(n) or ("", ""))[1] != "skipped"]', "True]"),
+    "G-neither": (GATE, "    return verdict([n for n in REQUIRED[cls] if n not in MACHINERY_JOBS]), verdict(MACHINERY_JOBS)\n",
+                  "    return verdict([n for n in REQUIRED[cls] if n not in MACHINERY_JOBS][1:]), verdict(MACHINERY_JOBS)\n"),
+}
+
+
+def selftest(tree: Path, target: str) -> tuple:
+    r = subprocess.run([sys.executable, "-I", str(tree / target), "--self-test"], capture_output=True, text=True)
+    out = r.stdout + r.stderr
+    return r.returncode, sum(1 for ln in out.splitlines() if ln.lstrip().startswith("FAIL"))
+
+
+def copy(tmp: str, name: str) -> Path:
+    tree = Path(tmp) / name
+    for rel in COPIED:
+        src, dst = ROOT / rel, tree / rel
+        dst.parent.mkdir(parents=True, exist_ok=True)
+        (shutil.copytree if src.is_dir() else shutil.copy)(src, dst)
+    return tree
+
+
+def main() -> int:
+    survived = 0
+    with tempfile.TemporaryDirectory() as tmp:
+        for target in (TOOLCHAIN, PRUNE, GATE):
+            rc, failed = selftest(copy(tmp, "M0-" + Path(target).stem), target)
+            print(f"RESULT mutant=M0 file={target} failed={failed} verdict={'null-ok' if rc == 0 and not failed else 'NULL-RED'}")
+            if rc or failed:
+                return 2
+        for name, (target, old, new) in PLANTS.items():
+            tree = copy(tmp, name)
+            p = tree / target
+            s = p.read_text()
+            if s.count(old) != 1:
+                print(f"ABORT {name}: pattern occurs {s.count(old)} times")
+                return 2
+            p.write_text(s.replace(old, new))
+            rc, failed = selftest(tree, target)
+            dead = rc != 0 and failed > 0
+            survived += not dead
+            print(f"RESULT mutant={name} failed={failed} verdict={'killed' if dead else 'SURVIVED'}")
+            shutil.rmtree(tree)
+    print(f"RESULT mutants={len(PLANTS)}")
+    print(f"RESULT survived={survived}")
+    return 1 if survived else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3654.md b/dev/programme/delivery/3654.md
new file mode 100644
index 0000000000..48efef5142
--- /dev/null
+++ b/dev/programme/delivery/3654.md
@@ -0,0 +1 @@
+- [#3654](https://github.com/tvofi/heatpump_optimizer/pull/3654) — **open**, R11-PRE-TOOLCHAIN-PIN p2: r11 pre toolchain pin part 2
diff --git a/tests/closures.json b/tests/closures.json
index b8dbcd3555..35c3fc9420 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4186,6 +4186,8 @@
    "tools/audit/seat/sweep_gantt.py",
    "tools/audit/seat/sweep_render.py",
    "tools/audit/seat/tmp_paths.py",
+   "tools/audit/seat/toolchain.py",
+   "tools/audit/seat/toolchain_selftest.py",
    "tools/audit/seat/topic_grammar.py",
    "tools/audit/seat/verdict_audit.py",
    "tools/policy/budget_raise_gate.py",
@@ -4486,6 +4488,7 @@
    "dev/audit/harnesses/r10_water_setpoint_feedback.py",
    "dev/audit/harnesses/r10_weekday_range_twins.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
+   "dev/audit/harnesses/r11_toolchain_mutants.py",
    "dev/audit/harnesses/r9_ci2b_closures_merge.py",
    "dev/audit/harnesses/r9_dbg2_selftest_price.py",
    "dev/audit/harnesses/r9_fr3_family_consumer.mjs",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 4627ab4238..b331a364fe 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -122,6 +122,7 @@ standing-seat liveness step keep the seats alive.
 - [`plan_public.py`](instruments/plan_public.py.md) — stages the ongoing round's plan page from the newest state ref for the public site, refusing a page that would publish a host path or a tool's attribution
 - [`bottleneck_check.py`](instruments/bottleneck_check.py.md) — prints one `BOTTLENECK:` line per flow metric past the owner's threshold, with a suggested action the orchestrator decides on, and nothing when none is
 - [`scorecard.py`](instruments/scorecard.py.md) — ten report-only convergence lines (gate and run health, first-verdict yield, machinery blocks, train skips, hotfix share, size, escapes, detection delay, seat cost), each but the hotfix naming measure held to a null control, written daily to `S/beatd/scorecard.txt`
+- [`toolchain.py`](instruments/toolchain.py.md) — the stable tools ref `toolchain/stable`: `behind` counts what the ref holds over a checkout on the seat paths, `promote` moves it along main to the newest commit whose push run reads MACHINERY green, and prints `PROMOTE-HELD` when the newest three past it do not
 - [`plant_recall.py`](instruments/plant_recall.py.md) — plants a held-out seat's objective bugs into the baseline export before the finders, refusing an unsound plant list, and counts recall after the judge (found / planted, whole, per space and per kind), unread on no input
 - [`finder_overlap.py`](instruments/finder_overlap.py.md) — seats a twin finder on one scopes.json seat's universe and estimates the bugs there from the two seats' judged-real overlap, with both models, unread on no input
 - [`outside_intake.py`](instruments/outside_intake.py.md) — lists submissions by outside users since a cursor with what each is owed (triage, answer, reply), and answers or refuses one, marked so none is answered twice
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 62868e3c79..8c6c5374c4 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -139,6 +139,13 @@ ROWS (the job table's `interval_s` in brackets):
                      [--sweep-record <sweep_record>]` into `S/beatd/scorecard.txt`
                      (ten report-only lines, none a gate); the digest hears only
                      `scorecard: UNREADABLE rc=<n>` when the instrument fails.
+  toolchain-promote [600] toolchain.py `promote --repo <repo> --dir <checkout>`: moves the
+                     stable tools ref `toolchain/stable` along main to the newest commit
+                     whose push run reads MACHINERY green, and keeps the instrument's
+                     last answer in `S/beatd/toolchain.txt`. A promotion or nothing newer
+                     leaves the digest empty; `PROMOTE-HELD` (the newest three concluded
+                     main runs past the ref machinery red or unread) is the row's line, and
+                     a refusal or failed read is `toolchain-promote: rc=<n>: <why>`.
 No row runs `git checkout`, `reset`, `pull` or `merge`; main is read as
 `git -C <repo> cat-file -e origin/main:<path>`. No row touches a seat's alive
 file. Every row exits 0 once its lines are written: the digest is the signal,
@@ -162,7 +169,7 @@ from pathlib import Path
 
 ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "gantt", "verdict-audit", "pulse",
         "cancel-sweep", "disk", "opener", "loop-cwd", "head-watch", "audit-dispatch", "outside-intake", "bottleneck",
-        "scorecard", "darwin-selftest")
+        "scorecard", "toolchain-promote", "darwin-selftest")
 HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
 #: roster-drain starts no op past this many seconds into a pass; the rest wait for the next pass. At
 #: most half the row's timeout_s in beatd.jobs.json (the self-test pins it), so an op started just
@@ -705,6 +712,20 @@ def scorecard(ctx: Ctx) -> None:
     write_job(ctx, "scorecard", [])
 
 
+def toolchain_promote(ctx: Ctx) -> None:
+    """toolchain.py promote; the digest hears a hold, a refusal or a failed read, never a promotion."""
+    got = ctx.need("toolchain-promote", "repo")
+    if got is None:
+        return
+    rc, out, err = ctx.py("tools/audit/seat/toolchain.py", "promote", "--repo", got[0], "--dir", str(ctx.repo))
+    if out.strip():
+        atomic(ctx.state / "beatd" / "toolchain.txt", out)
+    held = [ln for ln in out.splitlines() if ln.startswith("PROMOTE-HELD ")]
+    if rc != 0 and not held:
+        held = [f"toolchain-promote: rc={rc}: {(err.strip().splitlines() or [''])[-1]}"]
+    write_job(ctx, "toolchain-promote", held)
+
+
 DARWIN_SEAT = "audit/seat/"
 DARWIN_LEASE_LABEL = "darwin-selftest"
 #: darwin-selftest starts no self-test past this many seconds into a pass and gives the heavy slot back;
@@ -784,7 +805,7 @@ RUN = {"tick-digest": tick_digest, "owed-check": owed_check, "roster-drain": ros
        "plan-beat": plan_beat, "gantt": gantt, "verdict-audit": verdict_audit, "pulse": pulse, "cancel-sweep": cancel_sweep, "disk": disk,
        "opener": opener, "loop-cwd": loop_cwd, "head-watch": head_watch, "audit-dispatch": audit_dispatch,
        "outside-intake": outside_intake, "bottleneck": bottleneck, "scorecard": scorecard,
-       "darwin-selftest": darwin_selftest}
+       "toolchain-promote": toolchain_promote, "darwin-selftest": darwin_selftest}
 
 
 def main(argv: list[str]) -> int:
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index c18507df91..1e36ec7d8a 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -539,6 +539,31 @@ def cases(bj) -> dict[str, bool]:
     res["scorecard: an overlay without train_log is UNREADABLE and runs nothing"] = (
         digest(c) == "scorecard: UNREADABLE overlay lacks train_log\n" and f.ran("scorecard.py") == 0)
 
+    # toolchain-promote
+    moved = "PROMOTE 2026-11-15T10:00:00Z aaaaaaaaaaaa -> bbbbbbbbbbbb run=7\n"
+    hold = ("PROMOTE-HELD 2026-11-15T10:00:00Z aaaaaaaaaaaa: the newest 3 concluded main runs past it read "
+            "MACHINERY 9=red, 8=unread, 7=red\n")
+    c, f = fresh(answers={"toolchain.py": (0, moved, "")})
+    bj.toolchain_promote(c)
+    tp = next((x for x in f.calls if any(a.endswith("toolchain.py") for a in x)), [])
+    res["toolchain-promote null: a promotion leaves the digest empty and keeps the instrument's answer"] = (
+        not digest(c) and f.ran("toolchain.py") == 1 and bj.read(c.state / "beatd" / "toolchain.txt") == moved)
+    res["toolchain-promote: the instrument is handed promote, the overlay's repo and the checkout, and no sha"] = (
+        tp[3:] == ["promote", "--repo", "o/r", "--dir", str(c.repo)])
+    c, f = fresh(answers={"toolchain.py": (3, moved + hold, "")})
+    bj.toolchain_promote(c)
+    res["toolchain-promote: PROMOTE-HELD is the row's one line, beside a promotion or alone"] = (
+        digest(c) == bj.norm(hold) + "\n")
+    c, f = fresh(answers={"toolchain.py": (1, "", "toolchain: REFUSED origin/toolchain/stable is absent\n")})
+    bj.toolchain_promote(c)
+    res["toolchain-promote: a refusal or a failed read reaches the digest with its reason, never clean"] = (
+        digest(c) == "toolchain-promote: rc=1: toolchain: REFUSED origin/toolchain/stable is absent\n"
+        and not (c.state / "beatd" / "toolchain.txt").exists())
+    c, f = fresh(overlay={"plan_slots": 10}, answers={"toolchain.py": (0, moved, "")})
+    bj.toolchain_promote(c)
+    res["toolchain-promote: an overlay without repo is UNREADABLE and runs nothing"] = (
+        digest(c) == "toolchain-promote: UNREADABLE overlay lacks repo\n" and f.ran("toolchain.py") == 0)
+
     # roster-drain: the exact-line mark, UNRUN and CASCADE (folded from the retired roster_drain.py)
     c, f = fresh(answers={"roster_queue.py": (0, "", "")})
     (c.state / "roster-drain.queue").write_text("set-stage G1 done\n")
@@ -1203,6 +1228,17 @@ MUTANTS = {
                                 "scorecard: an overlay's sweep_record is handed on (null: none leaves the flag out)"),
     "scorecard_write_dropped": ('    atomic(ctx.state / "beatd" / "scorecard.txt", out)\n', "    pass\n",
                                 "scorecard null: a clean report leaves the digest empty and writes scorecard.txt"),
+    "toolchain_overlay_unread": ('    if got is None:\n        return\n    rc, out, err = ctx.py("tools/audit/seat/toolchain.py"',
+                                 '    if got is None:\n        got = ["o/r"]\n    rc, out, err = ctx.py("tools/audit/seat/toolchain.py"',
+                                 "toolchain-promote: an overlay without repo is UNREADABLE and runs nothing"),
+    "toolchain_held_dropped": ('if ln.startswith("PROMOTE-HELD ")]', 'if ln.startswith("PROMOTE-HELDX ")]',
+                               "toolchain-promote: PROMOTE-HELD is the row's one line, beside a promotion or alone"),
+    "toolchain_rc_clean": ("    if rc != 0 and not held:\n", "    if False:\n",
+                           "toolchain-promote: a refusal or a failed read reaches the digest with its reason, never clean"),
+    "toolchain_answer_dropped": ('        atomic(ctx.state / "beatd" / "toolchain.txt", out)\n', "        pass\n",
+                                 "toolchain-promote null: a promotion leaves the digest empty and keeps the instrument's answer"),
+    "toolchain_sha_pinned": ('"promote", "--repo", got[0], "--dir", str(ctx.repo))', '"promote", "HEAD", "--repo", got[0], "--dir", str(ctx.repo))',
+                             "toolchain-promote: the instrument is handed promote, the overlay's repo and the checkout, and no sha"),
     "plan_train_dropped": ('"--plan", plan, *train)', '"--plan", plan)',
                            "plan-beat: state_docs is handed the overlay's train_log (null: none leaves the flag out)"),
     "outside_lines_dropped": ('if ln.startswith("OUTSIDE ")]', 'if ln.startswith("OUTSIDEX ")]',
diff --git a/tools/audit/seat/beatd.jobs.json b/tools/audit/seat/beatd.jobs.json
index a428a776eb..6c3a6237dc 100644
--- a/tools/audit/seat/beatd.jobs.json
+++ b/tools/audit/seat/beatd.jobs.json
@@ -316,6 +316,26 @@
       "class": null,
       "kind": "periodic"
     },
+    {
+      "name": "toolchain-promote",
+      "argv": [
+        "python3",
+        "-I",
+        "tools/audit/seat/beat_jobs.py",
+        "toolchain-promote",
+        "--state",
+        "$S"
+      ],
+      "cwd": "orch",
+      "interval_s": 600,
+      "timeout_s": 300,
+      "heartbeat_s": null,
+      "env_pass": [
+        "GH_TOKEN"
+      ],
+      "class": null,
+      "kind": "periodic"
+    },
     {
       "name": "darwin-selftest",
       "argv": [
diff --git a/tools/audit/seat/instruments/beat_jobs.py.md b/tools/audit/seat/instruments/beat_jobs.py.md
index 4f1ee4170a..afe9f0fe59 100644
--- a/tools/audit/seat/instruments/beat_jobs.py.md
+++ b/tools/audit/seat/instruments/beat_jobs.py.md
@@ -21,7 +21,7 @@
   `disk` (`worktree_gc.sh` under the floor), `opener` (one `open_driver.py
   --board` pass, its refusals and `STUCK` forwarded) `head-watch`
   (`HEAD-MOVED` events) and `audit-dispatch` (one `DISPATCH: planted-defect-audit
-  arm=<arm> cut=<span>` line per sustained `would-trip` of a guardrail arm, never twice while the arm stays tripped; a failed run's `UNREADABLE` clears on the next readable run) and `outside-intake` (`outside_intake.py list` from the overlay's `intake_since`, with a cursor under `state/`: its `OUTSIDE` lines) and `bottleneck` (`bottleneck_check.py` with the beat checkout, the overlay's `train_log`, the `plan_slots` cap and `--memory state/bottleneck.json`: its `BOTTLENECK:` and `BOTTLENECK-UNREADABLE:` lines, each new once per trip; a failed run is `bottleneck: UNREADABLE`). `darwin-selftest` (Darwin hosts only; one cycle per `origin/main` tip runs `prepr.sh --self-test` and the `--self-test` of every `tools/audit/seat` script `selftest_wiring.py` reports as self-testing and wired, with CI's plain `python3`; each pass holds a heavy slot of `tests/gate_lock.py` around a detached worktree it makes and removes, starts no self-test past `DARWIN_PASS_BUDGET_S` and resumes the same tip next pass, because one whole cycle outlasts the row's `timeout_s` on a Mac; a finished cycle writes one `darwin-selftest: RED <instrument> <first FAIL line>` per red, nothing when green; CI runs these on Linux only, so this finds a Darwin-only red after the merge and prevents none; the host's beat is the macOS leg, no paid runner). `plan-beat` hands the overlay's `train_log` to `state_docs.py --train-log`. Each writes only actionable lines to
+  arm=<arm> cut=<span>` line per sustained `would-trip` of a guardrail arm, never twice while the arm stays tripped; a failed run's `UNREADABLE` clears on the next readable run) and `outside-intake` (`outside_intake.py list` from the overlay's `intake_since`, with a cursor under `state/`: its `OUTSIDE` lines) and `bottleneck` (`bottleneck_check.py` with the beat checkout, the overlay's `train_log`, the `plan_slots` cap and `--memory state/bottleneck.json`: its `BOTTLENECK:` and `BOTTLENECK-UNREADABLE:` lines, each new once per trip; a failed run is `bottleneck: UNREADABLE`). `toolchain-promote` (`toolchain.py promote` with the overlay's `repo` and the beat checkout: a promotion of `toolchain/stable` or nothing newer writes nothing, `PROMOTE-HELD` is its line, a refusal or failed read is `toolchain-promote: rc=<n>`; the last answer is kept in `S/beatd/toolchain.txt`). `darwin-selftest` (Darwin hosts only; one cycle per `origin/main` tip runs `prepr.sh --self-test` and the `--self-test` of every `tools/audit/seat` script `selftest_wiring.py` reports as self-testing and wired, with CI's plain `python3`; each pass holds a heavy slot of `tests/gate_lock.py` around a detached worktree it makes and removes, starts no self-test past `DARWIN_PASS_BUDGET_S` and resumes the same tip next pass, because one whole cycle outlasts the row's `timeout_s` on a Mac; a finished cycle writes one `darwin-selftest: RED <instrument> <first FAIL line>` per red, nothing when green; CI runs these on Linux only, so this finds a Darwin-only red after the merge and prevents none; the host's beat is the macOS leg, no paid runner). `plan-beat` hands the overlay's `train_log` to `state_docs.py --train-log`. Each writes only actionable lines to
   `S/digest/jobs/<row>`; `fold` concatenates them into `S/digest/digest.txt`,
   diffs `new.txt` and `gone.txt`, and touches `new.stamp` only on a new line,
   so the orchestrator's one wake reads `new.stamp` and `events.txt`. A null
diff --git a/tools/audit/seat/instruments/toolchain.py.md b/tools/audit/seat/instruments/toolchain.py.md
new file mode 100644
index 0000000000..9ad204fe3a
--- /dev/null
+++ b/tools/audit/seat/instruments/toolchain.py.md
@@ -0,0 +1,34 @@
+# `toolchain.py`
+
+- `toolchain.py` — the stable tools ref (R11-PRE-TOOLCHAIN-PIN; owner ruling
+  2026-11-13, card P1): the branch `toolchain/stable`, always a commit of
+  main. This file is the one place the ref's name and the seat paths
+  (`tools/audit/seat`, `tools/pr`, `tools/audit/carry_audit.py`) exist.
+  - `behind [<dir>] [--from <sha>] [--all] [--fetch]` prints the count of
+    commits the ref holds that the checkout (or `<sha>`) lacks, over the seat
+    paths; `--all` counts every commit. A checkout level with or ahead of the
+    ref prints 0, so a caller that acts on the count never moves a checkout
+    backwards. `--fetch` reads the ref from origin first.
+  - `promote [<sha>] --repo <owner/name> [--dir <checkout>]` moves the ref to
+    the newest main commit whose `ci.yml` push run reads MACHINERY green
+    (`tools/ci/gate.py` `status`), or to `<sha>`. It refuses a commit not on
+    origin/main, a move that is not a fast-forward and a verdict that is not
+    green, pushes without force and reads the ref back. Its answers:
+    `PROMOTE <utc> <old> -> <new> run=<id>`; `PROMOTE-CURRENT` when nothing
+    newer is green; `PROMOTE-HELD`, exit 3, when the newest three concluded
+    main runs past the ref all read machinery red or unread. PRODUCT is not
+    read: a product-red, machinery-green commit promotes.
+  - `promote --init` creates the ref, and only while it is absent. Until it
+    exists every verb refuses naming this command; an absent ref is never
+    read as main.
+
+  Exit 0 a count, a promotion or nothing newer; 1 a refusal; 2 a failed read
+  (git or GitHub), which concludes nothing; 3 held. When: the beat's
+  `toolchain-promote` row runs `promote` every ten minutes and keeps the last
+  answer in `S/beatd/toolchain.txt`; a hold, a refusal or a failed read is the
+  row's digest line. By hand: `promote --init` once after the merge that adds
+  this file, and `promote <sha>` to move the ref to a named green commit.
+  `prune_refs.py` keeps `toolchain/*`. `--self-test`: real git over a
+  throwaway origin with GitHub faked, each refusal beside the case that moves
+  the ref; `dev/audit/harnesses/r11_toolchain_mutants.py` drops each rule in
+  turn.
diff --git a/tools/audit/seat/prune_refs.py b/tools/audit/seat/prune_refs.py
index a72d61158c..237e6cf4d9 100644
--- a/tools/audit/seat/prune_refs.py
+++ b/tools/audit/seat/prune_refs.py
@@ -116,6 +116,7 @@ from pathlib import Path
 
 sys.path.insert(0, str(Path(__file__).resolve().parent))
 import ref_privacy  # noqa: E402  an archive tag never names this host (#2310)
+from toolchain import REF_PREFIX as TOOLCHAIN_PREFIX  # noqa: E402  the stable tools ref's family
 
 SELF = "tools/audit/seat/prune_refs.py"
 ARCHIVE_PREFIX = "archive/"
@@ -277,7 +278,7 @@ def classify(name: str, sha: str, prs: dict, main_reachable: set,
              ages: "dict | None" = None) -> str:
     """The rule that settles one ref. Order is the precedence, not a detail.
 
-    `main` first, then an open pull request (the keep that dominates), then a
+    `main` and the `toolchain/*` tools ref first, then an open pull request (the keep that dominates), then a
     tip already merged into main, then a handoff ref whose pull request
     merged, then the residue.
 
@@ -296,8 +297,8 @@ def classify(name: str, sha: str, prs: dict, main_reachable: set,
     request has it as its head, whatever its tip: the open-PR keep above is the
     only thing that holds one.
     """
-    if name == MAIN_REF:
-        return KEEP
+    if name == MAIN_REF or name.startswith(TOOLCHAIN_PREFIX):
+        return KEEP                     # the tools ref is a commit of main by rule: merged, and never deletable
     slot = prs.get(name) or {}
     if slot.get("open"):
         return KEEP
@@ -591,6 +592,11 @@ def _self_test_keeps(results: list) -> None:
     _check("null: the same design/ ref of a done group is still deleted",
            classify("design/R10-DONE", orphan, {}, reachable, frozenset(), og)
            == RESIDUE_NONE, results)
+    _check("toolchain/stable, always a commit of main, is kept: the merged-ref rule would delete the tools ref",
+           classify("toolchain/stable", merged, {}, reachable, ages={merged: 7 * 3600.0}) == KEEP, results)
+    _check("null: a merged ref that only resembles the prefix is still deleted",
+           [classify(n, merged, {}, reachable) for n in ("toolchain", "toolchains/stable", "fix/toolchain/stable")]
+           == [DELETE_MERGED] * 3, results)
     ages = {orphan: 5 * 3600.0, merged: 7 * 3600.0}
     _check("a tip younger than 6 h is kept",
            classify("fix/y", orphan, {}, reachable, ages=ages) == KEEP_YOUNG, results)
diff --git a/tools/audit/seat/ref_privacy.py b/tools/audit/seat/ref_privacy.py
index 84298d9092..29a414c88c 100644
--- a/tools/audit/seat/ref_privacy.py
+++ b/tools/audit/seat/ref_privacy.py
@@ -461,6 +461,8 @@ PUSHERS = {
                                     "pull request's own branch"),
     ".github/workflows/nightly.yml": ("republishes", "on a runner, constant-message bot commits onto "
                                       "record/autofix or main (nightly kills), moved out of tests.yml"),
+    "tools/audit/seat/toolchain.py": ("republishes", "moves the constant ref toolchain/stable to a commit "
+                                      "origin/main already holds; it composes no name, message or commit"),
     "tools/audit/seat/closeout.py": ("fixture", "its pushes are the self-test's, into a temp bare repository; "
                                      "the live ref writes are prune_refs.py's, which is guarded"),
     "tools/pr/app_approve.sh": ("fixture", "its pushes are the self-test's, into a temp bare repository"),
diff --git a/tools/audit/seat/toolchain.py b/tools/audit/seat/toolchain.py
new file mode 100644
index 0000000000..7b1f6a24b6
--- /dev/null
+++ b/tools/audit/seat/toolchain.py
@@ -0,0 +1,243 @@
+#!/usr/bin/env python3
+"""The stable tools ref: the one place its name, its seat paths, `behind` and `promote` exist.
+
+    python3 -I tools/audit/seat/toolchain.py behind [<dir>] [--from <sha>] [--all] [--fetch]
+    python3 -I tools/audit/seat/toolchain.py promote [<sha>] [--init] --repo <owner/name> [--dir <checkout>]
+    python3 -I tools/audit/seat/toolchain.py --self-test
+
+Owner ruling 2026-11-13 (card P1): seats and the beat run their tools from a
+promoted stable ref, never the tip of main. The ref is the branch
+`toolchain/stable`, always a commit of main, moved only by `promote`.
+
+`behind` prints the count of commits in `<from or HEAD>..origin/toolchain/stable`
+touching SEAT_PATHS (`--all`: every commit). A checkout level with or ahead of
+the ref counts 0, so no caller is ever told to move backwards. `--fetch` reads
+the ref from origin first. An absent ref refuses with the init command and is
+never read as main.
+
+`promote` moves the ref to the newest main commit whose `ci.yml` push run reads
+MACHINERY green (`tools/ci/gate.py` `status`, the one owner of that verdict),
+or to <sha> when given. It refuses a commit not on origin/main, a move that is
+not a fast-forward, and a verdict that is not green; it pushes without force,
+reads the ref back and prints
+
+    PROMOTE <utc> <old> -> <new> run=<id>
+
+`PROMOTE-CURRENT` when nothing newer is green, and `PROMOTE-HELD` with exit 3
+when the newest HELD_RUNS concluded main runs past the ref are all machinery
+red or unread. `--init` creates the ref, and only while it is absent.
+
+Exit: 0 promoted, current or a count printed; 1 refused; 2 a read failed; 3 held.
+"""
+from __future__ import annotations
+
+import argparse
+import functools
+import io
+import json
+import re
+import subprocess
+import sys
+import time
+from pathlib import Path
+
+HERE = Path(__file__).resolve().parent
+sys.path.insert(0, str(HERE))                      # -I drops the script's directory
+import gh_read_run  # noqa: E402  the seat's one retried GitHub read
+
+REF_PREFIX = "toolchain/"                          # prune_refs.py keeps the family
+REF = REF_PREFIX + "stable"
+TRACKING = f"refs/remotes/origin/{REF}"
+BASE = "main"
+WORKFLOW = "ci.yml"
+#: What a seat runs from its tools checkout: the union of the lists the freshness sites held
+#: (beatd.py SEAT_PATHS, pr_args.sh PR_FRESH_PATHS, tick_loop.sh CODE_PATHS).
+SEAT_PATHS = ("tools/audit/seat", "tools/pr", "tools/audit/carry_audit.py")
+HELD_RUNS = 3      # this many newest concluded main runs past the ref, none machinery green: PROMOTE-HELD
+SCAN_RUNS = 10     # the walk's bound: concluded runs read for a green one before giving up
+LIST_RUNS = 30     # one listing page of main's push runs
+INIT = "python3 -I tools/audit/seat/toolchain.py promote --init --repo <owner/name>"
+SHA = re.compile(r"[0-9a-f]{40}")
+_GATE_PY = HERE.parents[1] / "ci" / "gate.py"
+
+
+class Refused(Exception):
+    """The rule says no (exit 1)."""
+
+
+class Unreadable(Exception):
+    """A read failed, so nothing is concluded (exit 2)."""
+
+
+@functools.lru_cache(maxsize=1)
+def gate_py():
+    """tools/ci/gate.py from its tree path: its `status` is THE verdict, never a copy."""
+    import importlib.util
+    spec = importlib.util.spec_from_file_location("hpo_ci_gate", str(_GATE_PY))
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def git_in(d: str):
+    def git(*args: str) -> tuple[int, str]:
+        p = subprocess.run(["git", "-C", d, *args], capture_output=True, text=True)
+        return p.returncode, (p.stdout if p.returncode == 0 else p.stderr).strip()
+    return git
+
+
+def gh(argv: list[str]) -> tuple[int, str]:
+    out, err = io.StringIO(), io.StringIO()
+    rc = gh_read_run.read(argv, out=out, err=err)
+    return rc, (out.getvalue() if rc == 0 else " ".join(err.getvalue().split()))
+
+
+def absent() -> Refused:
+    return Refused(f"origin/{REF} is absent: it is never read as {BASE}; create it once with `{INIT}`")
+
+
+def behind(git, frm: str = "HEAD", every: bool = False, fetch: bool = False) -> int:
+    """Commits the stable ref holds that <frm> lacks, over SEAT_PATHS unless `every`."""
+    if fetch:
+        rc, out = git("fetch", "-q", "origin", f"+refs/heads/{REF}:{TRACKING}")
+        if rc and "couldn't find remote ref" in out:
+            raise absent()
+        if rc:
+            raise Unreadable(f"could not fetch origin {REF}: {out[-200:]}")
+    if git("rev-parse", "-q", "--verify", f"{TRACKING}^{{commit}}")[0]:
+        raise absent()
+    rc, out = git("rev-list", "--count", f"{frm}..{TRACKING}", *(() if every else ("--", *SEAT_PATHS)))
+    if rc or not out.isdigit():
+        raise Unreadable(f"could not count {frm}..origin/{REF}: {out[-200:]}")
+    return int(out)
+
+
+def main_runs(api, repo: str, sha: str = "") -> list[dict]:
+    """Main's `ci.yml` push runs, newest first (those at <sha> when given)."""
+    rc, out = api(["gh", "api", f"repos/{repo}/actions/workflows/{WORKFLOW}/runs?branch={BASE}&event=push"
+                   f"&per_page={LIST_RUNS}" + (f"&head_sha={sha}" if sha else ""), "--jq", ".workflow_runs"])
+    try:
+        runs = None if rc else json.loads(out)
+    except ValueError:
+        runs = None
+    if not isinstance(runs, list):
+        raise Unreadable(f"could not list {BASE}'s {WORKFLOW} push runs: {out[-200:]}")
+    return sorted(runs, key=lambda r: r.get("id") or 0, reverse=True)
+
+
+def machinery(api, repo: str, run: dict) -> str:
+    """One concluded run's MACHINERY verdict, from its latest jobs."""
+    import gh_read
+    rc, jobs, why = gh_read.read_pages(api, f"repos/{repo}/actions/runs/{run.get('id')}/jobs?filter=latest", "jobs")
+    if rc or jobs is None:
+        raise Unreadable(f"could not list the jobs of run {run.get('id')}: {why[-200:]}")
+    return gate_py().status({j.get("name"): (j.get("status"), j.get("conclusion")) for j in jobs}, "push")[1]
+
+
+def choose(runs: list[dict], verdict, at_or_behind) -> tuple[dict | None, list[tuple]]:
+    """(the newest machinery-green concluded run past the ref or None, the (id, verdict) pairs read).
+    The walk stops at the first run the ref already holds: nothing older moves it."""
+    read: list[tuple] = []
+    for run in [r for r in runs if r.get("status") == "completed"][:SCAN_RUNS]:
+        if at_or_behind(run.get("head_sha") or ""):
+            break
+        v = verdict(run)
+        read.append((run.get("id"), v))
+        if v == gate_py().GREEN:
+            return run, read
+    return None, read
+
+
+def held(read: list[tuple]) -> bool:
+    return len(read) >= HELD_RUNS and all(v != gate_py().GREEN for _, v in read[:HELD_RUNS])
+
+
+def promote(git, api, repo: str, sha: str = "", create: bool = False, now=time.time, out=print) -> int:
+    def ok(*args: str) -> bool:
+        return git(*args)[0] == 0
+    rc, listed = git("ls-remote", "origin", f"refs/heads/{REF}")
+    if rc:
+        raise Unreadable(f"could not read origin's {REF}: {listed[-200:]}")
+    old = listed.split()[0] if listed else ""
+    if not old and not create:
+        raise absent()
+    if old and create:
+        raise Refused(f"--init only while {REF} is absent; it is at {old[:12]}")
+    rc, why = git("fetch", "-q", "origin", BASE, *((f"+refs/heads/{REF}:{TRACKING}",) if old else ()))
+    if rc:
+        raise Unreadable(f"could not fetch origin {BASE}: {why[-200:]}")
+    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now()))
+
+    def holds(commit: str) -> bool:                 # the ref is at or past <commit>
+        return bool(old) and ok("merge-base", "--is-ancestor", commit, old)
+
+    def movable(new: str, what: str) -> None:
+        if not SHA.fullmatch(new) or not ok("merge-base", "--is-ancestor", new, f"origin/{BASE}"):
+            raise Refused(f"{what} is not a commit of origin/{BASE}")
+        if old and not ok("merge-base", "--is-ancestor", old, new):
+            raise Refused(f"{old[:12]} -> {new[:12]} is not a fast-forward: the ref never moves backwards")
+    read: list[tuple] = []
+    if sha == old and sha:
+        run = None
+    elif sha:
+        movable(sha, sha[:12])
+        done = [r for r in main_runs(api, repo, sha) if r.get("status") == "completed" and r.get("head_sha") == sha]
+        v = machinery(api, repo, done[0]) if done else gate_py().UNREAD
+        if v != gate_py().GREEN:
+            raise Refused(f"{sha[:12]} reads MACHINERY {v}" + (f" (run {done[0].get('id')})" if done else
+                                                              f" (no concluded {WORKFLOW} push run)"))
+        run = done[0]
+    else:
+        run, read = choose(main_runs(api, repo), lambda r: machinery(api, repo, r), holds)
+        if run is not None:
+            movable(run.get("head_sha") or "", f"run {run.get('id')}'s head {(run.get('head_sha') or '')[:12]}")
+    if run is not None:
+        new = run["head_sha"]
+        rc, why = git("push", "-q", "origin", f"{new}:refs/heads/{REF}")
+        if rc:
+            raise Refused(f"origin refused the push of {new[:12]} to {REF}: {why[-200:]}")
+        rc, listed = git("ls-remote", "origin", f"refs/heads/{REF}")
+        if rc or listed.split()[:1] != [new]:
+            raise Refused(f"pushed {new[:12]} to {REF} and read back {(listed.split() or ['nothing'])[0][:12]}")
+        out(f"PROMOTE {stamp} {old[:12] or 'absent'} -> {new[:12]} run={run.get('id')}")
+    if held(read):
+        out(f"PROMOTE-HELD {stamp} {old[:12] or 'absent'}: the newest {HELD_RUNS} concluded {BASE} runs past it read "
+            "MACHINERY " + ", ".join(f"{i}={v}" for i, v in read[:HELD_RUNS]))
+        return 3
+    if run is None:
+        out(f"PROMOTE-CURRENT {stamp} {old[:12] or 'absent'}")
+    return 0
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--self-test"]:
+        import toolchain_selftest  # the cases live beside this file
+        return toolchain_selftest.run()
+    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
+    sub = ap.add_subparsers(dest="verb", required=True)
+    b = sub.add_parser("behind")
+    b.add_argument("dir", nargs="?", default=".")
+    b.add_argument("--from", dest="frm", default="HEAD")
+    b.add_argument("--all", dest="every", action="store_true")
+    b.add_argument("--fetch", action="store_true")
+    p = sub.add_parser("promote")
+    p.add_argument("sha", nargs="?", default="")
+    p.add_argument("--init", action="store_true")
+    p.add_argument("--repo", required=True)
+    p.add_argument("--dir", default=".")
+    a = ap.parse_args(argv)
+    try:
+        if a.verb == "behind":
+            print(behind(git_in(a.dir), a.frm, a.every, a.fetch))
+            return 0
+        return promote(git_in(a.dir), gh, a.repo, a.sha, create=a.init)
+    except Refused as e:
+        print(f"toolchain: REFUSED {e}", file=sys.stderr)
+        return 1
+    except Unreadable as e:
+        print(f"toolchain: UNREADABLE {e}", file=sys.stderr)
+        return 2
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/toolchain_selftest.py b/tools/audit/seat/toolchain_selftest.py
new file mode 100644
index 0000000000..340882db1c
--- /dev/null
+++ b/tools/audit/seat/toolchain_selftest.py
@@ -0,0 +1,275 @@
+#!/usr/bin/env python3
+"""toolchain.py's cases, run by that file's own self-test flag.
+
+Real git throughout: a bare origin whose main is six commits (c0..c5; c1, c3
+and c5 touch a seat path), a side commit off main, and one clone as the tools
+checkout. Only GitHub is a fake: a run listing and one job listing per run.
+Each refusal has its null control beside it, the case where the same call
+moves the ref. dev/audit/harnesses/r11_toolchain_mutants.py drops each rule
+in turn against this file.
+"""
+from __future__ import annotations
+
+import contextlib
+import io
+import json
+import re
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+HERE = Path(__file__).resolve().parent
+sys.path.insert(0, str(HERE.parents[2] / "tests"))
+from throwaway_git import throwaway_git_clone, throwaway_git_init  # noqa: E402
+import toolchain as tc  # noqa: E402
+
+REPO = "o/r"
+T0 = 1794700800.0  # 2026-11-15T00:00:00Z
+LINE = re.compile(r"PROMOTE 2026-11-15T00:00:00Z (absent|[0-9a-f]{12}) -> [0-9a-f]{12} run=\d+")
+
+
+class World:
+    """One origin, one checkout, and GitHub's answers about main's push runs."""
+
+    def __init__(self, tmp: str):
+        self.origin, self.work, src = f"{tmp}/origin.git", f"{tmp}/work", f"{tmp}/src"
+        self.env = throwaway_git_init(src, "-q", "-b", "main")
+        self.c = []
+        for i in range(6):
+            path = Path(src, "tools/audit/seat/x.sh" if i % 2 else "docs/x.md")
+            path.parent.mkdir(parents=True, exist_ok=True)
+            path.write_text(f"{i}\n")
+            self.sh(src, "add", "-A")
+            self.sh(src, "commit", "-q", "-m", f"c{i}")
+            self.c.append(self.sh(src, "rev-parse", "HEAD"))
+        self.sh(src, "checkout", "-q", "-b", "side", self.c[2])
+        Path(src, "side.txt").write_text("s\n")
+        self.sh(src, "add", "-A")
+        self.sh(src, "commit", "-q", "-m", "side")
+        self.side = self.sh(src, "rev-parse", "HEAD")
+        throwaway_git_clone(src, self.origin, "-q", "--bare")
+        throwaway_git_clone(self.origin, self.work, "-q")
+        self.sh(self.work, "checkout", "-q", "--detach", self.c[0])
+        self.runs: list[dict] = []
+        self.jobs: dict[int, list | None] = {}
+        self.calls: list[str] = []
+        self.lax = False  # a listing that ignores head_sha, so the caller's own filter is what holds
+        self.git = tc.git_in(self.work)
+
+    def sh(self, d: str, *args: str) -> str:
+        p = subprocess.run(["git", "-C", d, *args], capture_output=True, text=True, env=self.env)
+        assert p.returncode == 0, (args, p.stderr)
+        return p.stdout.strip()
+
+    def ref(self) -> str:
+        return self.sh(self.origin, "for-each-ref", "--format=%(objectname)", f"refs/heads/{tc.REF}")
+
+    def set_ref(self, sha: str) -> None:
+        if sha:
+            self.sh(self.origin, "update-ref", f"refs/heads/{tc.REF}", sha)
+            self.sh(self.work, "fetch", "-q", "origin", f"+refs/heads/{tc.REF}:{tc.TRACKING}")
+        elif self.ref():
+            self.sh(self.origin, "update-ref", "-d", f"refs/heads/{tc.REF}")
+            self.sh(self.work, "update-ref", "-d", tc.TRACKING)
+
+    def run(self, sha: str, machinery: str = "success", product: str = "success", status: str = "completed", **over):
+        """A main push run at <sha>; `machinery` and `product` conclude every job of that kind."""
+        rid = 100 + len(self.runs)
+        g = tc.gate_py()
+        jobs = [{"name": n, "status": "completed", "conclusion": machinery if n in g.MACHINERY_JOBS else product}
+                for n in (*g.REQUIRED["push"], "governance / instrument-self-tests")]
+        for j in jobs:
+            if j["name"] in over:
+                j["status"], j["conclusion"] = over[j["name"]]
+        self.runs.append({"id": rid, "head_sha": sha, "status": status})
+        self.jobs[rid] = jobs
+        return rid
+
+    def api(self, argv: list[str]) -> tuple[int, str]:
+        path = argv[2]
+        self.calls.append(path)
+        if "/jobs" in path:
+            jobs = self.jobs.get(int(path.split("/runs/")[1].split("/")[0]))
+            if jobs is None:
+                return 1, "gh: HTTP 502"
+            return 0, "".join(json.dumps(j) + "\n" for j in jobs) if "page=1" in path else ""
+        if self.runs is None:
+            return 1, "gh: HTTP 502"
+        sha = re.search(r"head_sha=([0-9a-f]+)", path)
+        return 0, json.dumps([r for r in self.runs if not sha or self.lax or r["head_sha"] == sha[1]])
+
+    def promote(self, sha: str = "", create: bool = False, git=None) -> tuple:
+        """(exit code or the exception class's name, what it printed, the ref afterwards)."""
+        lines: list[str] = []
+        self.calls.clear()
+        try:
+            rc = tc.promote(git or self.git, self.api, REPO, sha, create, now=lambda: T0, out=lines.append)
+        except (tc.Refused, tc.Unreadable) as e:
+            rc, lines = type(e).__name__, [str(e)]
+        return rc, lines, self.ref()
+
+    def jobs_read(self) -> int:
+        return sum("/jobs" in c for c in self.calls)
+
+
+def run() -> int:
+    n = fails = 0
+
+    def check(name: str, got, want=True) -> None:
+        nonlocal n, fails
+        n += 1
+        if got != want:
+            fails += 1
+            print(f"FAIL {name}: got {got!r}, want {want!r}")
+
+    def refused(fn, needle: str, exc=tc.Refused) -> bool:
+        try:
+            fn()
+        except (tc.Refused, tc.Unreadable) as e:
+            return type(e) is exc and needle in str(e)
+        return False
+
+    with tempfile.TemporaryDirectory() as tmp:
+        w = World(tmp)
+        c = w.c
+
+        # ---- behind
+        check("behind: an absent ref refuses with the init command, never a count against main",
+              refused(lambda: tc.behind(w.git), tc.INIT))
+        check("behind --fetch: a ref absent on origin refuses the same way",
+              refused(lambda: tc.behind(w.git, fetch=True), tc.INIT))
+        w.set_ref(c[4])
+        check("behind counts the ref's commits touching the seat paths (c1, c3 of c1..c4)", tc.behind(w.git), 2)
+        check("behind --all counts every commit of c1..c4", tc.behind(w.git, every=True), 4)
+        check("behind --from counts from that commit, not HEAD", tc.behind(w.git, frm=c[3]), 0)
+        check("null: --from a commit behind a seat-path change counts it", tc.behind(w.git, frm=c[2]), 1)
+        w.sh(w.work, "checkout", "-q", "--detach", c[5])
+        check("a checkout ahead of the ref is 0 behind: no caller is told to move backwards",
+              (tc.behind(w.git), tc.behind(w.git, every=True)), (0, 0))
+        w.sh(w.work, "checkout", "-q", "--detach", c[4])
+        check("a checkout level with the ref is 0 behind", tc.behind(w.git), 0)
+        w.sh(w.work, "checkout", "-q", "--detach", c[0])
+        w.sh(w.origin, "update-ref", f"refs/heads/{tc.REF}", c[5])
+        check("null: without --fetch a ref moved on origin is not seen", tc.behind(w.git), 2)
+        check("behind --fetch reads the ref from origin first", tc.behind(w.git, fetch=True), 3)
+        check("behind: a commit git cannot resolve is unreadable, never 0",
+              refused(lambda: tc.behind(w.git, frm="0" * 40), "could not count", tc.Unreadable))
+        out = io.StringIO()
+        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
+            rcs = (tc.main(["behind", w.work]), tc.main(["behind", w.work, "--all", "--from", c[4]]))
+            w.set_ref("")
+            rcs += (tc.main(["behind", w.work]),)
+        check("the verb prints the count and exits 0; an absent ref exits 1 and prints no count",
+              (rcs, out.getvalue().split()), ((0, 0, 1), ["3", "1"]))
+
+        # ---- promote: the absent ref and --init
+        w.run(c[1])
+        check("promote: an absent ref refuses with the init command and pushes nothing",
+              (lambda r: (r[0], tc.INIT in r[1][0], r[2]))(w.promote()), ("Refused", True, ""))
+        rc, lines, ref = w.promote(create=True)
+        check("promote --init creates the ref at the newest machinery-green main commit and reads it back",
+              (rc, ref, bool(LINE.fullmatch(lines[0])), lines[0].split()[2:]), (0, c[1], True, ["absent", "->", c[1][:12], "run=100"]))
+        check("promote --init while the ref exists refuses and leaves it",
+              (lambda r: (r[0], "only while" in r[1][0], r[2]))(w.promote(create=True)), ("Refused", True, c[1]))
+
+        # ---- promote: the default walk
+        rc, lines, ref = w.promote()
+        check("promote with nothing newer prints PROMOTE-CURRENT, exits 0 and reads no job listing",
+              (rc, lines, ref, w.jobs_read()), (0, [f"PROMOTE-CURRENT 2026-11-15T00:00:00Z {c[1][:12]}"], c[1], 0))
+        w.run(c[2])
+        rc, lines, ref = w.promote()
+        check("null: a machinery-green main commit past the ref is a fast-forward and promotes",
+              (rc, ref, lines[0].split()[2:]), (0, c[2], [c[1][:12], "->", c[2][:12], "run=101"]))
+        w.run(c[3], machinery="failure")
+        check("a main commit whose run reads MACHINERY red does not promote; one red is not held",
+              w.promote(), (0, [f"PROMOTE-CURRENT 2026-11-15T00:00:00Z {c[2][:12]}"], c[2]))
+        w.runs[-1]["head_sha"], red3 = c[2], w.runs[-1]
+        w.run(c[3], product="failure")
+        check("PRODUCT red with MACHINERY green promotes: the tools ref reads machinery alone",
+              w.promote()[::2], (0, c[3]))
+        red3["head_sha"] = c[3]
+        w.set_ref(c[2])
+        w.runs[-1]["status"] = "in_progress"
+        check("null: the same run still in progress is not concluded and promotes nothing",
+              w.promote()[::2], (0, c[2]))
+        w.runs.pop()
+        w.run(c[4], **{"tests / briefs": ("completed", "cancelled")})
+        w.run(c[5], **{"governance / env-matrix": ("in_progress", None)})
+        rc, lines, ref = w.promote()
+        check("the newest three concluded runs past the ref red or unread: PROMOTE-HELD, exit 3, the ref unmoved",
+              (rc, ref, lines), (3, c[2], [f"PROMOTE-HELD 2026-11-15T00:00:00Z {c[2][:12]}: the newest 3 concluded main runs "
+                                           "past it read MACHINERY 104=unread, 103=unread, 102=red"]))
+        w.jobs[104] = w.jobs[100]
+        check("null: the same three with the newest green promote it and are not held", w.promote()[::2], (0, c[5]))
+        w.set_ref(c[1])
+        w.jobs[104] = w.jobs[102]
+        w.runs.sort(key=lambda r: r["id"])
+        rc, lines, ref = w.promote()
+        check("a green run older than three bad ones still promotes, and the hold is still reported",
+              (rc, ref, [ln.split()[0] for ln in lines], w.jobs_read()), (3, c[2], ["PROMOTE", "PROMOTE-HELD"], 4))
+        rc, lines, ref = w.promote()
+        check("the walk stops at the ref: three bad runs past it are held, the run at it is never read",
+              (rc, ref, w.jobs_read()), (3, c[2], 3))
+        w.runs[2:] = w.runs[2:3]
+        check("null: one bad run past the ref is not three: PROMOTE-CURRENT, exit 0", w.promote()[0], 0)
+        w.runs[2]["head_sha"], w.jobs[102] = w.side, w.jobs[100]
+        check("a green run whose head descends from the ref and is not a commit of main refuses and leaves the ref",
+              (lambda r: (r[0], "not a commit of origin/main" in r[1][0], r[2]))(w.promote()), ("Refused", True, c[2]))
+        w.runs[2]["head_sha"] = c[3]
+        w.run(c[4], machinery="failure")
+        w.run(c[5], machinery="failure")
+        check("null: two bad runs above a green third are not a hold: it promotes, exit 0", w.promote()[::2], (0, c[3]))
+
+        # ---- promote <sha>
+        w.runs.clear()
+        w.set_ref(c[2])
+        for i in (1, 3, 4):
+            w.run(c[i], machinery="success" if i != 4 else "failure")
+        w.run(w.side)
+        for name, sha, needle in (("a commit not on main", w.side, "not a commit of origin/main"),
+                                  ("a commit behind the ref (not a fast-forward)", c[1], "not a fast-forward"),
+                                  ("a commit reading MACHINERY red", c[4], "MACHINERY red (run 102)"),
+                                  ("a commit with no concluded push run (unread)", c[5], "MACHINERY unread (no concluded"),
+                                  ("a word that is no sha", "main", "not a commit of origin/main")):
+            check(f"promote <sha> refuses {name} and leaves the ref",
+                  (lambda r: (r[0], needle in r[1][0], r[2]))(w.promote(sha)), ("Refused", True, c[2]))
+        w.lax = True
+        check("promote <sha> reads only a run at that commit, whatever the listing returns",
+              (lambda r: (r[0], "MACHINERY unread (no concluded" in r[1][0], r[2]))(w.promote(c[5])), ("Refused", True, c[2]))
+        w.lax = False
+        check("promote <sha> at the ref's own commit prints PROMOTE-CURRENT",
+              w.promote(c[2]), (0, [f"PROMOTE-CURRENT 2026-11-15T00:00:00Z {c[2][:12]}"], c[2]))
+        rc, lines, ref = w.promote(c[3])
+        check("null: promote <sha> of a green commit of main past the ref moves it",
+              (rc, ref, lines[0].split()[2:]), (0, c[3], [c[2][:12], "->", c[3][:12], "run=101"]))
+        w.sh(w.origin, "update-ref", f"refs/heads/{tc.REF}", w.side)
+        w.run(c[5])
+        check("a ref that left main is never moved: the walk's green commit is not a fast-forward of it",
+              (lambda r: (r[0], "not a fast-forward" in r[1][0], r[2]))(w.promote()), ("Refused", True, w.side))
+
+        # ---- the push's read-back, and the reads
+        w.set_ref(c[3])
+
+        def deaf(*args):                            # a push that reports success and moves nothing
+            return (0, "") if args[0] == "push" else w.git(*args)
+        check("a push that did not move the ref is refused by the read-back",
+              (lambda r: (r[0], f"read back {c[3][:12]}" in r[1][0], r[2]))(w.promote(git=deaf)), ("Refused", True, c[3]))
+        w.jobs[w.runs[-1]["id"]] = None
+        check("a job listing that cannot be read is unreadable, never a verdict", w.promote()[::2], ("Unreadable", c[3]))
+        w.runs = None
+        check("a run listing that cannot be read is unreadable", w.promote()[::2], ("Unreadable", c[3]))
+        w.runs = []
+        check("null: an empty listing reads, and promotes nothing", w.promote()[::2], (0, c[3]))
+        err = io.StringIO()
+        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
+            tc.gh, real = (lambda argv: (1, "gh: HTTP 502")), tc.gh
+            try:
+                rc = tc.main(["promote", "--repo", REPO, "--dir", w.work])
+            finally:
+                tc.gh = real
+        check("the verb exits 2 on a failed read and names it", (rc, err.getvalue().startswith("toolchain: UNREADABLE ")), (2, True))
+        check("the ref's name sits under the family prune_refs.py keeps", tc.REF.startswith(tc.REF_PREFIX) and tc.REF != tc.REF_PREFIX)
+
+    print(f"toolchain self-test: {n} checks, {fails} failed")
+    return 1 if fails else 0
diff --git a/tools/ci/gate.py b/tools/ci/gate.py
index 8ad794c5f4..b6613a8310 100644
--- a/tools/ci/gate.py
+++ b/tools/ci/gate.py
@@ -298,6 +298,29 @@ def machinery_line(jobs: dict, owed) -> str:
     return "machinery (report-only, never gating): " + (", ".join(rest) or "no other job listed")
 
 
+#: The jobs that grade the process and never the product (owner ruling 2026-11-13, card P1). `status` is
+#: their one reader: the product jobs of an event class are its REQUIRED less this tuple, computed, never listed.
+MACHINERY_JOBS = ("tests / arch-instrument", "tests / briefs", "tests / closures", "governance / policy-docs",
+                  "governance / wave-script", "governance / env-matrix", "governance / instrument-self-tests")
+GREEN, RED, UNREAD = "green", "red", "unread"
+
+
+def status(jobs: dict, cls: str) -> tuple[str, str]:
+    """(PRODUCT, MACHINERY) of one run's latest jobs (`run_jobs`' shape) under event class `cls`, each
+    green, red or unread. It reads nothing and moves no `gate` conclusion. Red: a member that concluded
+    anything but success or cancelled, a skipped required member included (`gate`'s own rule). Unread: no
+    red, and a member absent, unfinished or cancelled; it never reads green. A skipped member `cls` does
+    not require (instrument-self-tests, when its scope chose nothing) is not applicable: the verdict is
+    over the members that ran, and unread when none did."""
+    def verdict(names) -> str:
+        ran = [jobs.get(n) for n in names
+               if n in REQUIRED[cls] or (jobs.get(n) or ("", ""))[1] != "skipped"]
+        if any(j is not None and j[0] == "completed" and j[1] not in ("success", "cancelled") for j in ran):
+            return RED
+        return GREEN if ran and all(j is not None and j[1] == "success" for j in ran) else UNREAD
+    return verdict([n for n in REQUIRED[cls] if n not in MACHINERY_JOBS]), verdict(MACHINERY_JOBS)
+
+
 def judge(ctx: dict, claim: dict, get, reaches=reaches_custom_components, sleep=time.sleep,
           now=time.monotonic) -> tuple[str, list[str], list[str]]:
     """(outcome, reasons, this run's other jobs: reported, never gating). A verdict
@@ -459,6 +482,41 @@ def self_test() -> int:
     cov_red = [dict(j, conclusion="failure") if j["name"] == "tests / coverage-ratchet" else j for j in ratchet_red]
     check("a push with coverage-ratchet red still fails", judge(pctx, pclaim, fake(cov_red), cc)[0],
           "FAIL tests / coverage-ratchet: failure (this run)")
+    # R11-PRE-TOOLCHAIN-PIN: the pair of verdicts of one run. `gate`'s own conclusion is judged above and never moves.
+    pj = {x: ("completed", "success") for x in (*REQUIRED["push"], "governance / instrument-self-tests",
+                                                "tests / ci-ratchet")}
+
+    def st(cls="push", drop=(), **over):
+        named = {next(x for x in pj if x.split(" / ", 1)[1] == k.replace("_", "-") or x == k): v for k, v in over.items()}
+        return status({k: v for k, v in {**pj, **named}.items() if k not in drop}, cls)
+    red_job, running, cancelled, skipped = (("completed", "failure"), ("in_progress", None), ("completed", "cancelled"),
+                                            ("completed", "skipped"))
+    check("null: a push run with every job green reads PRODUCT green, MACHINERY green", st(), (GREEN, GREEN))
+    check("a push run red only in tests / closures reads PRODUCT green, MACHINERY red", st(closures=red_job), (GREEN, RED))
+    check("null: a push run red in tests / fast (3.14) reads PRODUCT red, MACHINERY green",
+          st(**{"tests / fast (3.14)": red_job}), (RED, GREEN))
+    check("a member absent, unfinished or cancelled is unread, never green, in either verdict",
+          [st(drop=("tests / typing",)), st(typing=running), st(typing=cancelled),
+           st(drop=("tests / briefs",)), st(briefs=running), st(briefs=cancelled)],
+          [(UNREAD, GREEN)] * 3 + [(GREEN, UNREAD)] * 3)
+    check("a red member beside an unread one is red: a concluded failure is known",
+          (st(typing=cancelled, browser=red_job), st(briefs=running, closures=red_job)), ((RED, GREEN), (GREEN, RED)))
+    check("a skipped required member is red, product or machinery (the gate's own 4.2 rule)",
+          (st(browser=skipped), st(briefs=skipped)), ((RED, GREEN), (GREEN, RED)))
+    check("a skipped instrument-self-tests (its scope chose nothing) is not applicable: MACHINERY over the rest",
+          (st(instrument_self_tests=skipped), st(instrument_self_tests=skipped, briefs=red_job)),
+          ((GREEN, GREEN), (GREEN, RED)))
+    check("null: an instrument-self-tests that ran red, absent or unfinished is read",
+          [st(instrument_self_tests=red_job)[1], st(drop=("governance / instrument-self-tests",))[1],
+           st(instrument_self_tests=running)[1]], [RED, UNREAD, UNREAD])
+    check("ci-ratchet is in neither verdict (advisory on push, owner 2026-11-11)", st(ci_ratchet=red_job), (GREEN, GREEN))
+    for cls, names in sorted(REQUIRED.items()):
+        allj = {x: ("completed", "success") for x in (*names, *MACHINERY_JOBS)}
+        moved = {x: [i for i, v in enumerate(status({**allj, x: red_job}, cls)) if v == RED] for x in allj}
+        check(f"{cls}: every required name reddens exactly one verdict, a machinery job MACHINERY and the rest PRODUCT",
+              {x: m for x, m in moved.items() if m != [1 if x in MACHINERY_JOBS else 0]}, {})
+    check("the machinery tuple names push-required jobs and the one self-tests lane prelude gates, nothing else",
+          [x for x in MACHINERY_JOBS if x not in REQUIRED["push"]], ["governance / instrument-self-tests"])
     check("on a pull request the notes stay one line per job, no machinery line",
           [x for x in judge(ctx, claim, fake(green + ratchet_red[-1:]), cc)[2] if x.startswith("machinery")], [])
     red = [dict(j, conclusion="failure") if j["name"] == "tests / closures" else j for j in green]
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 62f0c156b1..47ab440739 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -7976,8 +7976,11 @@
    "run_sha": "e9a4011f002b3591593de2307fd743aa0477052bc058be6cff2970467a11f0b9",
    "files": [
     "tests/throwaway_git.py",
+    "tools/audit/seat/gh_read.py",
+    "tools/audit/seat/gh_read_run.py",
     "tools/audit/seat/prune_refs.py",
-    "tools/audit/seat/ref_privacy.py"
+    "tools/audit/seat/ref_privacy.py",
+    "tools/audit/seat/toolchain.py"
    ],
    "probes": [
     ".",
@@ -9293,6 +9296,39 @@
     "rev-list"
    ]
   },
+  "toolchain": {
+   "run_sha": "58a9dcb43610f2fb8ff4466f1623dd23eff5bec9e8fdfd1cf4ca65cfa4bc6b54",
+   "files": [
+    "tests/throwaway_git.py",
+    "tools/audit/seat/gh_read.py",
+    "tools/audit/seat/gh_read_run.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
+    "tools/ci/gate.py",
+    "tools/ci/ghapi.py",
+    "tools/ci/prelude.py"
+   ],
+   "probes": [
+    ".",
+    "config",
+    "objects",
+    "packed-refs",
+    "refs",
+    "tests",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat",
+    "tools/ci"
+   ],
+   "dirs": [
+    "tests",
+    "tools/audit/seat",
+    "tools/ci"
+   ],
+   "index": false,
+   "objects": false,
+   "git": []
+  },
   "topic-grammar": {
    "run_sha": "40ac264ceeb40c59d850cd2d025f52a4c92776ec61b0806bd6c52bd159cec58d",
    "files": [

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
