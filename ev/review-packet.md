# Review packet #3943
head: 70965f42a8cef9c1233940f5375f22599a80594a
base: ac9045c223721608e684c8a2213831aa34c1fa4f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=141037355192 success
arch-score / arch-score id=141037291714 success
arm id=141036988563 skipped
budget-raise-gate / budget-raise-gate id=141037291807 success
cancel-superseded id=141036994449 success
codeql id=141037257081 skipped
codeql / Analyze (actions) id=141037291707 success
codeql / Analyze (javascript-typescript) id=141037291702 success
codeql / Analyze (python) id=141037291664 success
gate id=141037647023 failure
governance id=141037257136 skipped
governance / env-matrix id=141037291768 success
governance / instrument-self-tests id=141037291862 in_progress
governance / policy-docs id=141037291764 success
governance / record id=141037293456 skipped
governance / wave-script id=141037291799 success
hassfest id=141037257288 skipped
hassfest / hassfest id=141037291683 success
kernel-points id=141037293120 skipped
pr-contract id=141037647879 skipped
prelude id=141036994739 success
sweep-self id=141037938800 skipped
tests id=141037256759 skipped
tests / arch-instrument id=141037627590 success
tests / briefs id=141037291767 success
tests / browser id=141037627594 success
tests / closure-scope id=141037291857 success
tests / closures id=141037627591 in_progress
tests / coverage id=141037627547 in_progress
tests / fast (3.14, 1/4) id=141037627639 in_progress
tests / fast (3.14, 2/4) id=141037627674 success
tests / fast (3.14, 3/4) id=141037627630 success
tests / fast (3.14, 4/4) id=141037627653 success
tests / mutation id=141037291720 success
tests / mutation-autofix id=141037703574 skipped
tests / mutation-pins id=141037703169 skipped
tests / nightly-ha id=141037629179 skipped
tests / nightly-status id=141037291736 failure
tests / replay id=141037628694 skipped
tests / typing id=141037627517 success
validate id=141037256859 skipped
validate / validate-hacs id=141037291699 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 141037291862: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at 70965f42a8cef9c1233940f5375f22599a80594a in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item cf28f50a: dismissed:an unpinned site's killer is unmeasured, so capping it would drop the sites the sample exists to check.
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         dev/audit/harnesses/mutation_draw_cost.py
             `dev/audit/harnesses/mutation_draw_cost.py` is in the tree at this head
  ok         cd <ebd70acc checkout> && python3 dev/audit/harnesses/mutation_draw_cost.py --cost tests/env_drift.py=397
             `dev/audit/harnesses/mutation_draw_cost.py` is in the tree at this head
  ok         tests/mutation_table.py
             `tests/mutation_table.py` is in the tree at this head
  unverified git diff 4c16879e8d HEAD -- tests/mutation_table.py
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/archscore/score.py --diff ac9045c223721608e684c8a2213831aa34c1fa4f HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         tests/closure.py select --diff <merge-base>
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/pr/ci_predict.py --apply-inert
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/mutation_draw_cost.py b/dev/audit/harnesses/mutation_draw_cost.py
new file mode 100644
index 0000000000..a59ee3a26f
--- /dev/null
+++ b/dev/audit/harnesses/mutation_draw_cost.py
@@ -0,0 +1,111 @@
+#!/usr/bin/env python3
+"""R11-HOTFIX-MUTATION-DRIVER-CAP harness: the `tests / mutation` job's wall clock.
+
+    cd <checkout> && python3 <this> [--base REF] [--scale N] [--cost S=SECS]...
+
+Runs the checkout's own `tests/mutation_table.py` main() exactly as tests.yml's
+drive step calls it (`--scope changed --base REF --max 10 --jobs 3`), with the
+real draw, driver order, worker trees, lazy settles, null control and
+`drive_pool` schedule. Only `run_script` is stubbed: each driver run sleeps
+its cost divided by `--scale` and is red iff the tree carries a drawn mutant
+(an AST change, so the comment-only null control stays green) and the driver
+is that site's `killed_by` pin. An unpinned site is killed by nothing, its
+whole sweep paid -- an upper bound. A driver's cost is its `recorded_seconds`
+(tests/closures.json), overridden by `--cost` (the CI log's measured baseline
+of a ref-driven driver, whose recording times a stub).
+
+Prints one line per drawn site (its pin, or `unpinned`), one per site the
+draw passed over, one per driver (runs, recorded seconds summed) and
+`ESTIMATE <s> s` = the span from the first stubbed driver run's start to the
+last one's end, times `--scale`: the drive's schedule at the recorded seconds,
+not a CI measurement, and without the job's setup and inventory minutes. Run it in a checkout with the program under test; the before/after
+pair is two checkouts of one head, one carrying the patched program.
+"""
+from __future__ import annotations
+
+import argparse
+import ast
+import contextlib
+import tempfile
+import sys
+import threading
+import time
+from pathlib import Path
+
+
+def main(argv: list[str] | None = None) -> int:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--base", default="origin/main")
+    ap.add_argument("--scale", type=float, default=100.0)
+    ap.add_argument("--cost", action="append", default=[], metavar="S=SECS")
+    args = ap.parse_args(argv)
+
+    root = Path.cwd()
+    sys.path.insert(0, str(root / "tests"))
+    import mutation_table as mt  # noqa: E402  (the checkout's own program)
+
+    cost = mt.recorded_seconds()
+    for spec in args.cost:
+        name, _, secs = spec.partition("=")
+        cost[name] = float(secs)
+    killed_by = mt.load_budgets().get("killed_by", {})
+    drawn: list[dict] = []
+    real_sampled = mt.sampled_pool
+
+    def sampled(*a, **k):
+        pool, held = real_sampled(*a, **k)
+        drawn[:] = pool
+        return pool, held
+
+    runs: dict[str, list[float]] = {}
+    span: list[float] = []
+    lock = threading.Lock()
+
+    def stub(script, cwd, timeout, extra_args=None, extra_env=None):
+        red = False
+        for mut in drawn:
+            text = (Path(cwd) / mut["file"]).read_text()
+            lines = text.splitlines()
+            if (len(lines) >= mut["line"]
+                    and lines[mut["line"] - 1] == mut["new"]
+                    and ast.dump(ast.parse(text)) != ast.dump(ast.parse(
+                        (root / mut["file"]).read_text()))):
+                red = mt.pinned_script(killed_by, mut) == script
+                break
+        secs = cost.get(script, 0.0)
+        start = time.monotonic()
+        time.sleep(secs / args.scale)
+        with lock:
+            runs.setdefault(script, []).append(secs)
+            span.extend((start, time.monotonic()))
+        return mt.ScriptRun(1 if red else 0, 1 if red else 0, secs,
+                            "  FAIL stub\n1 of 1 STUB CHECKS FAILED\n" if red
+                            else "ok\n")
+
+    mt.sampled_pool = sampled
+    mt.run_script = stub
+    log = tempfile.TemporaryFile("w+")  # main() line-buffers its stdout
+    with contextlib.redirect_stdout(log):
+        rc = mt.main(["--scope", "changed", "--base", args.base, "--max", "10",
+                      "--jobs", "3"])
+    # The first driver run's start to the last's end: the inventory, draw and
+    # worktree setup before it are this machine's real seconds, not a scaled
+    # driver's, so scaling them would charge them 100 times over.
+    wall = (max(span) - min(span)) if span else 0.0
+    for mut in drawn:
+        print(f"SITE {mt.triage_key(mut)} "
+              f"{mt.pinned_script(killed_by, mut) or 'unpinned'}")
+    log.seek(0)
+    for line in log.read().splitlines():
+        if "passed over" in line:
+            print(f"PASSED {line.strip()}")
+    for s, secs in sorted(runs.items()):
+        print(f"DRIVER {s} runs={len(secs)} seconds={sum(secs):.0f}")
+    print(f"MAIN rc={rc}")
+    print(f"ESTIMATE {wall * args.scale:.0f} s at --scale {args.scale:.0f} "
+          f"({wall * args.scale / 60:.0f} min against the job's 160)")
+    return rc
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3943.md b/dev/programme/delivery/3943.md
new file mode 100644
index 0000000000..b12b8619bf
--- /dev/null
+++ b/dev/programme/delivery/3943.md
@@ -0,0 +1 @@
+- [#3943](https://github.com/tvofi/heatpump_optimizer/pull/3943) — **open**, Cap the mutation driver so mutation runs stop timing out (R11-HOTFIX-MUTATION-DRIVER-CAP)
diff --git a/tests/closures.json b/tests/closures.json
index d0376f630d..6d95bfaaa4 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4766,6 +4766,7 @@
    "dev/audit/harnesses/merge_subject_guard_block.mjs",
    "dev/audit/harnesses/mutant_guard.py",
    "dev/audit/harnesses/mutant_run_diff_shards.py",
+   "dev/audit/harnesses/mutation_draw_cost.py",
    "dev/audit/harnesses/nightly_drain_breakdown.py",
    "dev/audit/harnesses/owner_only_channel.py",
    "dev/audit/harnesses/owner_only_mutants.py",
diff --git a/tests/entities.py b/tests/entities.py
index c2a1957d0c..02ce67f05c 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -41691,6 +41691,70 @@ R.check(
     f"marked, two drivers -> {_MUT_SP and _MUT_SP[0][:2]}; marked, only the "
     f"judge -> {_MUT_SP and _MUT_SP[1][:2]}; no mark -> {_MUT_SP and _MUT_SP[2][:2]}",
 )
+# The PR lane's costly-pin cap (R11-HOTFIX-MUTATION-DRIVER-CAP, #3897): the
+# first K+1 pump_arbiter.py sites of the draw and every other one after, pinned to
+# one driver, drawn by the real sampled_pool at a cap of K+3. Dear, the draw
+# holds exactly COSTLY_PIN_DRAWS pinned sites, keeps the uncapped draw's order,
+# and passes over only pinned sites. Cheap (at the threshold, not over it),
+# with no pins, or pinned to a script none of the site's drivers is, it is the
+# uncapped draw site for site: the null control.
+_MUT_CP_D = "tests/features.py"
+_MUT_CP_F = [_mut.PRODUCTION / "pump_arbiter.py"]
+_MUT_CP_REL = str(_MUT_CP_F[0].relative_to(_mut.ROOT))
+_MUT_CP_K = getattr(_mut, "COSTLY_PIN_DRAWS", None)
+
+
+def _mut_cp(cap, pins=None, secs=None):
+    with _pv_ctx.redirect_stdout(_mut_io.StringIO()):
+        pool, _ = _mut_spool(_MUT_CP_F, {_MUT_CP_D: [_MUT_CP_REL]},
+                             [_MUT_CP_D], None, {}, _pv_random.Random(7),
+                             10_000, cap,
+                             **({} if pins is None else
+                                {"killed_by": pins, "seconds": secs}))
+    return pool
+
+
+_MUT_CP = None
+if _mut_spool is not None and _MUT_CP_K is not None:
+    # A site is (line, kind, new): twins share an anchor, so one pin covers
+    # every twin and the pinned set is read through ledger_key.
+    _mut_cp_id = lambda m: (m["line"], m["kind"], m["new"])  # noqa: E731
+    _MUT_CP_SITES = _mut_cp(10_000)
+    _MUT_CP_ALL = [_mut_cp_id(m) for m in _MUT_CP_SITES]
+    _MUT_CP_KB = {_mut.ledger_key(m): {"killed_by": _MUT_CP_D, "old": m["old"]}
+                  for m in (_MUT_CP_SITES[:_MUT_CP_K + 1]
+                            + _MUT_CP_SITES[_MUT_CP_K + 1::2])}
+    _MUT_CP_PIN = {_mut_cp_id(m) for m in _MUT_CP_SITES
+                   if _mut.ledger_key(m) in _MUT_CP_KB}
+    _MUT_CP_T = _mut.COSTLY_PIN_SECONDS
+    _MUT_CP_N = _MUT_CP_K + 3
+    _MUT_CP = tuple([_mut_cp_id(m) for m in _mut_cp(_MUT_CP_N, *a)] for a in (
+        (_MUT_CP_KB, {_MUT_CP_D: _MUT_CP_T + 1.0}),
+        (_MUT_CP_KB, {_MUT_CP_D: _MUT_CP_T}),
+        ({}, {_MUT_CP_D: _MUT_CP_T + 1.0}), (),
+        ({k: dict(v, killed_by="tests/gone.py") for k, v in _MUT_CP_KB.items()},
+         {"tests/gone.py": _MUT_CP_T + 1.0})))
+    _MUT_CP_DEAR = _MUT_CP[0]
+    _MUT_CP_SKIPPED = ([] if not _MUT_CP_DEAR else
+                       [k for k in _MUT_CP_ALL[:_MUT_CP_ALL.index(_MUT_CP_DEAR[-1])]
+                        if k not in _MUT_CP_DEAR])
+R.check(
+    "the PR lane's draw holds at most COSTLY_PIN_DRAWS sites pinned to a "
+    "driver over COSTLY_PIN_SECONDS, fills its cap in draw order with the "
+    "rest, and passes over only those pinned sites; a pin at the threshold, "
+    "or no pin, draws exactly the uncapped pool (R11-HOTFIX-MUTATION-DRIVER-CAP)",
+    _MUT_CP is not None and len(_MUT_CP_ALL) >= 2 * _MUT_CP_N
+    and len(set(_MUT_CP_ALL)) == len(_MUT_CP_ALL)
+    and len(_MUT_CP[0]) == _MUT_CP_N
+    and sum(k in _MUT_CP_PIN for k in _MUT_CP[0]) == _MUT_CP_K
+    and [k for k in _MUT_CP_ALL if k in _MUT_CP[0]] == _MUT_CP[0]
+    and bool(_MUT_CP_SKIPPED) and all(k in _MUT_CP_PIN for k in _MUT_CP_SKIPPED)
+    and (_MUT_CP[1] == _MUT_CP[2] == _MUT_CP[3] == _MUT_CP[4]
+         == _MUT_CP_ALL[:_MUT_CP_N]),
+    f"K={_MUT_CP_K}; uncapped={_MUT_CP and _MUT_CP[3]}; dear={_MUT_CP and _MUT_CP[0]}; "
+    f"at threshold={_MUT_CP and _MUT_CP[1]}; no pins={_MUT_CP and _MUT_CP[2]}; "
+    f"pinned to a non-driver={_MUT_CP and _MUT_CP[4]}",
+)
 _mut_ordpool = getattr(_mut, "order_pool_drivers", None)
 _MUT_OP_SITE = _mut_pv_site("x.py:ord K 0")
 
diff --git a/tests/mutation_table.py b/tests/mutation_table.py
index 11b6e3cac6..b6d561b43d 100644
--- a/tests/mutation_table.py
+++ b/tests/mutation_table.py
@@ -3089,15 +3089,50 @@ def drive_pin_pool(pool: list[dict], workers: int, cost: dict[str, float],
             for m, v, t in zip(pool, verdict, timed)]
 
 
+# The PR lane's costly-pin cap (R11-HOTFIX-MUTATION-DRIVER-CAP, #3897). A
+# pinned site's own killer runs first (`order_pool_drivers`), so drawing it
+# costs that driver's run. Under --scope changed the first red run of a driver
+# also pays its lazy baseline and null control. On #3897 the draw held 9
+# features.py pins of 10 sites: 11 runs of 1617 s recorded on 3 workers. The
+# `tests / mutation` job overran its 160 minutes on five pull requests that
+# day. So the PR lane draws at most COSTLY_PIN_DRAWS sites whose pinned killer
+# records over COSTLY_PIN_SECONDS. It fills its --max with the next sites of
+# the same shuffled draw. Only a PINNED site is passed over: its kill is a
+# measured ledger row, which the nightly's --scope full draw re-drives
+# (`pin_reverification`). An unpinned site's killer is what the lane exists
+# to find, so it is never passed over. 900 s sits between the two drivers
+# over it (features.py, entities.py) and the next shared one by
+# `recorded_seconds` (boost_drift_replay.py). 2 keeps one dear lazy settle as
+# the drive's critical path: its first red run, baseline and null control,
+# back to back on one worker. `mutation_draw_cost.py` simulates it.
+COSTLY_PIN_SECONDS = 900.0
+COSTLY_PIN_DRAWS = 2
+
+
+def costly_pin(mut: dict, killed_by: dict,
+               seconds: dict[str, float]) -> str | None:
+    """The driver `mut` is pinned to, when it is one of its drivers and
+    records over COSTLY_PIN_SECONDS; else None."""
+    pin = pinned_script(killed_by, mut)
+    if pin in mut["drivers"] and seconds.get(pin, 0.0) > COSTLY_PIN_SECONDS:
+        return pin
+    return None
+
+
 def sampled_pool(files: list[Path], closures: dict, allow: list[str],
                  touched: dict[str, set[int]] | None, triage: dict,
-                 rng: random.Random, per_file: int,
-                 cap: int) -> tuple[list[dict], int]:
+                 rng: random.Random, per_file: int, cap: int,
+                 killed_by: dict | None = None,
+                 seconds: dict[str, float] | None = None,
+                 ) -> tuple[list[dict], int]:
     """The sampled pool, and how many drawn sites a triage mark constrains.
 
     A triaged site is still driven -- by every driver but `TRIAGE_JUDGE` -- so
     a driver that kills an "equivalent" mutant refutes its mark. A site whose
-    only driver is that one is left out (R9-F10.13).
+    only driver is that one is left out (R9-F10.13). Given `killed_by` and the
+    drivers' `seconds`, the draw's first `cap` sites are taken, but a site
+    `costly_pin` names past the COSTLY_PIN_DRAWS-th is replaced by the next
+    one. With no such pin it is the draw's first `cap`, as before.
     """
     pool: list[dict] = []
     held = 0
@@ -3117,7 +3152,22 @@ def sampled_pool(files: list[Path], closures: dict, allow: list[str],
             if mut["drivers"]:
                 pool.append(mut)
     rng.shuffle(pool)
-    return pool[:cap], held
+    if killed_by is None:
+        return pool[:cap], held
+    drawn: list[dict] = []
+    dear = 0
+    for mut in pool:
+        if len(drawn) == cap:
+            break
+        pin = costly_pin(mut, killed_by, seconds or {})
+        if pin is not None and dear == COSTLY_PIN_DRAWS:
+            print(f"  {triage_key(mut)}: passed over, pinned to {pin} "
+                  f"(over {COSTLY_PIN_SECONDS:.0f} s) and {dear} such "
+                  f"site(s) drawn")
+            continue
+        dear += pin is not None
+        drawn.append(mut)
+    return drawn, held
 
 
 def order_pool_drivers(pool: list[dict], seconds: dict[str, float],
@@ -3961,8 +4011,13 @@ def main(argv: list[str] | None = None) -> int:
     if not (args.pin_killed or args.drain or args.anchor):
         # A pull request draws only from the lines it wrote (`changed_lines`).
         touched = changed_lines(args.base) if args.scope == "changed" else None
-        pool, held_n = sampled_pool(files, closures, allow, touched, triage,
-                                    rng, args.per_file, args.max)
+        # The costly-pin cap binds the PR lane, whose lazy settles it bounds;
+        # --scope full is the nightly's re-drive of those pins.
+        pool, held_n = sampled_pool(
+            files, closures, allow, touched, triage, rng, args.per_file,
+            args.max, **({"killed_by": budgets.get("killed_by", {}),
+                          "seconds": recorded_seconds()}
+                         if args.scope == "changed" else {}))
         whole = pool
         if held_n:
             print(f"  {held_n} drawn site(s) hold a survivor_triage mark: "

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
