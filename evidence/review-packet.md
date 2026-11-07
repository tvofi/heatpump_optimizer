# Review packet #3269
head: 37d64edf2f82f78288999663cee629842aabef88
base: 80016a71f567d936450d8708abcbb79d9e8071d7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128242257030 success
arch-score / arch-score id=128255857915 success
arm id=128241776786 skipped
budget-raise-gate / budget-raise-gate id=128255857463 success
cancel-superseded id=128255898483 success
codeql id=128255892761 skipped
codeql / Analyze (actions) id=128241936506 success
codeql / Analyze (javascript-typescript) id=128241936413 success
codeql / Analyze (python) id=128241936512 success
gate id=128255856434 success
governance id=128255881317 skipped
governance / delivery-status id=128241936753 success
governance / delivery-status-publish id=128241937663 skipped
governance / env-matrix id=128241936503 success
governance / instrument-self-tests id=128241936416 success
governance / policy-docs id=128241937048 success
governance / record id=128241937750 skipped
governance / wave-script id=128241936498 success
hassfest id=128255896382 skipped
hassfest / hassfest id=128241936510 success
kernel-points id=128255890474 skipped
pr-contract id=128255894810 skipped
pr-contract / pr-contract id=128255052574 success
prelude id=128255857303 success
refresh id=128255887137 success
tests id=128255903394 skipped
tests / arch-instrument id=128242140219 success
tests / briefs id=128241936682 success
tests / browser id=128242140121 success
tests / ci-ratchet id=128252403340 skipped
tests / claims-autofix id=128249887209 skipped
tests / closure-scope id=128241936769 success
tests / closures id=128242140342 success
tests / closures-autofix id=128249091976 skipped
tests / coverage id=128242139952 success
tests / coverage-ratchet id=128252401308 success
tests / fast (3.14) id=128242140184 success
tests / graders-head-copy id=128252401202 success
tests / lane-proofs id=128252706512 success
tests / mutation id=128241936571 success
tests / mutation-autofix id=128242269103 skipped
tests / mutation-pins id=128242268981 skipped
tests / nightly-ha id=128242141986 skipped
tests / nightly-status id=128241936711 success
tests / replay id=128242141683 skipped
tests / typing id=128242139962 success
validate id=128255894651 skipped
validate / validate-hacs id=128241936442 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 88a5bb7b: dismissed:one-off for this group, whose after-run is named under Forward-carry for the seat that lands it; a fixer may not write the roster branch to land it there
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs
             gh api: every long flag accepted
  ok         python3 dev/audit/harnesses/nightly_drain_breakdown.py <4 scheduled shard logs> --prior <4 dispatch shard logs>
             `dev/audit/harnesses/nightly_drain_breakdown.py` is in the tree at this head
  ok         gh api repos/tvofi/heatpump_optimizer/actions/runs/42139479636/jobs
             gh api: every long flag accepted
  ok         python3 -I dev/audit/harnesses/drain_admission_probe.py <tree at 785c2b604> OUT.json -- --scope full --drain DIR --max 320 --jobs 4 --seed 20261106
             `dev/audit/harnesses/drain_admission_probe.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 80016a71f567
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 80016a71f567
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/nightly.yml b/.github/workflows/nightly.yml
index f54c83be8..0f8080926 100644
--- a/.github/workflows/nightly.yml
+++ b/.github/workflows/nightly.yml
@@ -142,7 +142,7 @@ jobs:
   # `mutation-nightly` samples the whole package and records nothing, and
   # `--pin-killed` reaches only the sites a diff adds, so the unpinned sites
   # that predate the ratchet had no way out. This job drives a slice of that
-  # stock -- whole anchors, walked by a date seed -- with the same kill rule,
+  # stock -- whole anchors, walked by the run's seed -- with the same kill rule,
   # baseline and null control, and hands what it killed to the next job. It
   # holds no write grant; the job that pushes runs no driver (D11-s1-03).
   # Main only (#1848): a dispatch on any other ref would drive that ref's
@@ -150,10 +150,27 @@ jobs:
   #
   # SHARDED four ways (triage s6-batch16 P85): one runner drove 40 sites a
   # night, about 24 kills, against ~3400 killable. `--shard K/4` deals the
-  # night's slice -- drawn at four times --max under the one date seed -- by
+  # night's slice -- drawn at four times --max under the one run seed -- by
   # whole anchor (`drain_pool`), so the shards are disjoint and together the
   # slice one runner would not have had the hours for. Each shard uploads its
   # own artifact; the one push merges them (`merge_pin_shards`).
+  #
+  # The seed is the RUN id, not the date (R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT):
+  # every run draws from the unpinned stock as it stood at its checkout, so
+  # two runs one UTC date apart by less than a drive -- a dispatch beside the
+  # schedule -- drew one slice twice. Run 42139479636 killed 90 sites and
+  # landed 20 pins, the other 70 pushed first by dispatch 42135552492 under
+  # the same date seed (dev/audit/harnesses/nightly_drain_breakdown.py
+  # --prior). The four shards of a run still share one seed, so they stay
+  # disjoint; the seed is printed in each DRAIN SHARD header, so a night's
+  # draw replays as before.
+  #
+  # --budget-minutes 270, mutation-nightly's sizing under the same 330-minute
+  # timeout (R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT): at 240, 185 of the 320 sites
+  # run 42139479636 drew were never started, while its longest shard ended
+  # 225 minutes into its 330 (nightly_drain_breakdown.py; the jobs API's
+  # started_at and completed_at). The 60 minutes left cover the runs in
+  # flight, each under its scaled timeout.
   mutation-ledger:
     if: github.ref == 'refs/heads/main' && github.event_name != 'push'
     runs-on: ubuntu-latest
@@ -202,7 +219,7 @@ jobs:
           python3 tests/mutation_table.py \
             --scope full --drain "$out" --shard ${{ matrix.shard }}/4 \
             --max 80 --jobs 4 \
-            --seed "$(date -u +%Y%m%d)" --budget-minutes 240 \
+            --seed "${{ github.run_id }}" --budget-minutes 270 \
             --pool-seconds "$RUNNER_TEMP/pool-seed/pool_seconds.json" \
             | tee "$RUNNER_TEMP/mutation-ledger.txt"
           test -s "$out/status"
diff --git a/dev/audit/harnesses/drain_admission_probe.py b/dev/audit/harnesses/drain_admission_probe.py
new file mode 100644
index 000000000..eb81e888a
--- /dev/null
+++ b/dev/audit/harnesses/drain_admission_probe.py
@@ -0,0 +1,91 @@
+#!/usr/bin/env python3
+"""How much of a drain's budget admission charge reach_skip frees.
+
+    python3 -I dev/audit/harnesses/drain_admission_probe.py TREE OUT.json \
+        -- --scope full --drain DIR --max 320 --jobs 4 --seed 20261106
+    python3 -I dev/audit/harnesses/drain_admission_probe.py --summary OUT.json
+
+TREE is a checkout whose `tests/mutation_table.py` runs unmodified: the probe
+replaces `drive_pool` in the imported module, never in the tree, because
+tests/entities.py reads that file's text and a probe written into it turns
+the entities baseline red. main() then draws, runs the traced baselines and
+the null control exactly as the nightly does, and hands the pool to the
+replacement, which writes one row per mutant and stops before any mutant
+runs:
+
+* need      -- what admission charges the mutant: its shared drivers at the
+  schedule's own `cost`;
+* need_free -- the share of it on pairs `reach_skip` frees, which no run ever
+  spends.
+
+`--summary` prints the totals. Without `--shard`, `--max N` draws the union
+of the N/4-per-shard slices one run's four shards would deal under that seed
+(`drain_pool` caps at max times the shard count and deals whole anchors).
+The cost seconds are this machine's baselines: the share is the figure, not
+the hours.
+"""
+from __future__ import annotations
+
+import json
+import statistics
+import sys
+
+
+def summary(path: str) -> int:
+    with open(path, encoding="utf-8") as fh:
+        rows = json.load(fh)["rows"]
+    if not rows:
+        print("no rows: the probe saw an empty pool")
+        return 1
+    pairs = sum(len(r["drivers"]) for r in rows)
+    free = sum(len(r["free"]) for r in rows)
+    need = sum(r["need"] for r in rows)
+    need_free = sum(r["need_free"] for r in rows)
+    print(f"mutants {len(rows)}; shared pairs {pairs}, reach-free {free} "
+          f"({100 * free / pairs:.0f}%)")
+    print(f"admission charge {need / 3600:.1f} h, reach-free "
+          f"{need_free / 3600:.1f} h ({100 * need_free / need:.0f}%)")
+    print("median charge per mutant: "
+          f"{statistics.median(r['need'] for r in rows) / 60:.1f} min charged, "
+          f"{statistics.median(r['need'] - r['need_free'] for r in rows) / 60:.1f}"
+          " min without the reach-free pairs")
+    return 0
+
+
+def probe(tree: str, out: str, argv: list[str]) -> int:
+    sys.path.insert(0, f"{tree}/tests")
+    import mutation_table as mt
+
+    def replacement(pool, workers, cost, drive, settle=None, deadline=None,
+                    **_):
+        cells = dict(zip(drive.__code__.co_freevars,
+                         (c.cell_contents for c in drive.__closure__)))
+        reaches = cells["reaches"]
+        rows = []
+        for m in pool:
+            shared = [s for s in m["drivers"] if s not in mt.EXCLUSIVE]
+            free = [s for s in shared if mt.reach_skip(reaches.get(s), m)]
+            rows.append({"key": mt.triage_key(m), "anchor": m.get("anchor"),
+                         "drivers": shared, "free": free,
+                         "need": sum(cost.get(s, 0.0) for s in shared),
+                         "need_free": sum(cost.get(s, 0.0) for s in free)})
+        with open(out, "w", encoding="utf-8") as fh:
+            json.dump({"cost": cost, "rows": rows}, fh, indent=1)
+        print(f"ADMISSION PROBE: {len(rows)} row(s) written", flush=True)
+        raise SystemExit(0)
+
+    mt.drive_pool = replacement
+    return mt.main(argv)
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--summary"] and len(argv) == 2:
+        return summary(argv[1])
+    if len(argv) < 3 or "--" not in argv or argv.index("--") != 2:
+        print(__doc__, file=sys.stderr)
+        return 2
+    return probe(argv[0], argv[1], argv[3:])
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/harnesses/nightly_drain_breakdown.py b/dev/audit/harnesses/nightly_drain_breakdown.py
new file mode 100644
index 000000000..2c648cef2
--- /dev/null
+++ b/dev/audit/harnesses/nightly_drain_breakdown.py
@@ -0,0 +1,133 @@
+#!/usr/bin/env python3
+"""Where a nightly's mutation-ledger draw went, per shard, from its job logs.
+
+    python3 dev/audit/harnesses/nightly_drain_breakdown.py SHARD.log... \
+        [--prior OTHER_RUN_SHARD.log...]
+
+Each SHARD.log is one `mutation-ledger (K)` job log, as
+`gh api repos/<owner>/<repo>/actions/jobs/<id>/logs` returns it. The rule,
+per shard, reads only the lines `tests/mutation_table.py --drain` prints
+between its `DRAIN SHARD` header and its `DRAIN:` summary:
+
+* drawn      -- the header's `N of M unpinned site(s)`;
+* killed     -- `pinned <site> -- killed by <script>` rows;
+* lives      -- `UNPINNED <site> -- lives` rows (owed a human verdict);
+* split      -- `UNPINNED <site> -- killed by ..., but its anchor also
+  covers a site no run killed` rows: killed, but unpinnable, since a
+  disposition covers the whole anchor;
+* timed out  -- `UNPINNED <site> -- skip-timed-out in ...` rows;
+* not run    -- `NOT RUN <site> -- not started: ... --budget-minutes` rows;
+* slack      -- minutes between the `DRAIN:` line and the --budget-minutes
+  deadline, the deadline taken as the header's timestamp plus the budget
+  read from the job's own echoed command (the drive's deadline is set a few
+  seconds before the header, so this overstates the slack by those seconds).
+
+Every drawn site lands in exactly one class or the shard reports `UNCLASSED`,
+the rule's own null control. `--prior` names the job logs of a run that
+pushed before this one: a kill it also recorded lands no new pin, so
+`killed new` is the count the push could record.
+"""
+from __future__ import annotations
+
+import argparse
+import re
+import sys
+from datetime import datetime, timedelta
+
+_HEAD = re.compile(r"DRAIN SHARD (\d+)/(\d+) -- (\d+) of (\d+) unpinned")
+_BUDGET = re.compile(r"--budget-minutes (\d+)")
+_ROW = re.compile(r"^  (pinned|UNPINNED|NOT RUN) +(\S+ [A-Z_]+) -- (.*)$")
+
+
+def _lines(path: str):
+    with open(path, encoding="utf-8", errors="replace") as fh:
+        for raw in fh:
+            stamp, _, text = raw.lstrip("\ufeff").rstrip("\n").partition(" ")
+            # The runner stamps each line `YYYY-MM-DDTHH:MM:SS.fffffffZ`; the
+            # seconds are the resolution this rule needs.
+            try:
+                when = datetime.fromisoformat(stamp[:19])
+            except ValueError:
+                continue
+            yield when, text
+
+
+def shard(path: str) -> dict:
+    """One shard's classes, read by the module docstring's rule."""
+    out = {"path": path, "killed": [], "lives": 0, "split": 0, "timed out": 0,
+           "not run": 0, "unclassed": []}
+    budget = start = end = None
+    inside = False
+    for when, text in _lines(path):
+        if budget is None and (b := _BUDGET.search(text)):
+            budget = int(b.group(1))
+        if (h := _HEAD.search(text)):
+            inside, start = True, when
+            out["shard"], out["drawn"] = f"{h.group(1)}/{h.group(2)}", int(h.group(3))
+            continue
+        if not inside:
+            continue
+        if text.startswith("DRAIN: "):
+            end = when
+            break
+        row = _ROW.match(text)
+        if not row:
+            continue
+        kind, site, why = row.groups()
+        if kind == "pinned" and why.startswith("killed by "):
+            out["killed"].append(site)
+        elif kind == "UNPINNED" and why == "lives":
+            out["lives"] += 1
+        elif kind == "UNPINNED" and "but its anchor also covers" in why:
+            out["split"] += 1
+        elif kind == "UNPINNED" and why.startswith("skip-timed-out"):
+            out["timed out"] += 1
+        elif kind == "NOT RUN" and "--budget-minutes" in why:
+            out["not run"] += 1
+        elif kind == "UNPINNED" and why == "skip-budget":
+            continue  # the NOT RUN row names the same mutant
+        else:
+            out["unclassed"].append(text.strip())
+    if start and end and budget:
+        out["slack_min"] = round(
+            (start + timedelta(minutes=budget) - end).total_seconds() / 60)
+    out["budget"] = budget
+    return out
+
+
+def main(argv: list[str] | None = None) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    ap.add_argument("logs", nargs="+")
+    ap.add_argument("--prior", nargs="*", default=[])
+    args = ap.parse_args(argv)
+    prior = {s for p in args.prior for s in shard(p)["killed"]}
+    totals: dict[str, int] = {}
+    bad = 0
+    for path in args.logs:
+        s = shard(path)
+        if "drawn" not in s:
+            print(f"{path}: no DRAIN SHARD header, not a shard log; skipped")
+            continue
+        new = [k for k in s["killed"] if k not in prior]
+        row = {"drawn": s.get("drawn", 0), "killed": len(s["killed"]),
+               "killed new": len(new), "lives": s["lives"], "split": s["split"],
+               "timed out": s["timed out"], "not run": s["not run"]}
+        summed = (row["killed"] + row["lives"] + row["split"]
+                  + row["timed out"] + row["not run"])
+        for k, v in row.items():
+            totals[k] = totals.get(k, 0) + v
+        print(f"shard {s.get('shard', '?')}: " + ", ".join(
+            f"{k} {v}" for k, v in row.items())
+            + f"; slack {s.get('slack_min', '?')} min of --budget-minutes "
+              f"{s['budget']}")
+        if summed != row["drawn"] or s["unclassed"]:
+            bad = 1
+            print(f"  UNCLASSED: classes sum to {summed} of {row['drawn']} "
+                  f"drawn; {len(s['unclassed'])} row(s) no rule reads: "
+                  + "; ".join(s["unclassed"][:3]))
+    print("total: " + ", ".join(f"{k} {v}" for k, v in totals.items()))
+    return bad
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3269.md b/dev/programme/delivery/3269.md
new file mode 100644
index 000000000..09fbeef93
--- /dev/null
+++ b/dev/programme/delivery/3269.md
@@ -0,0 +1 @@
+- [#3269](https://github.com/tvofi/heatpump_optimizer/pull/3269) — **open**, R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT: hotfix nightly pin throughput (R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT)
diff --git a/tests/closures.json b/tests/closures.json
index c71959796..b7082b69c 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3932,6 +3932,7 @@
    "dev/audit/harnesses/d1_s3_02_queued_apply.py",
    "dev/audit/harnesses/d6_page_anchors.py",
    "dev/audit/harnesses/d907_kernel_band.py",
+   "dev/audit/harnesses/drain_admission_probe.py",
    "dev/audit/harnesses/draw_range_evidence.py",
    "dev/audit/harnesses/dual_path.py",
    "dev/audit/harnesses/early_cutoff_closed_loop.py",
@@ -3950,6 +3951,7 @@
    "dev/audit/harnesses/learner_inputs_swap.py",
    "dev/audit/harnesses/merge_subject_guard_block.mjs",
    "dev/audit/harnesses/mutant_guard.py",
+   "dev/audit/harnesses/nightly_drain_breakdown.py",
    "dev/audit/harnesses/pulse_replay.py",
    "dev/audit/harnesses/r10_2205_replay_cost_arms.py",
    "dev/audit/harnesses/r10_advisor_degree.py",
diff --git a/tests/entities.py b/tests/entities.py
index 1a257bf95..3378376a8 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -35841,7 +35841,7 @@ R.check(
 # --drain (R9 F10.5): the pre-ratchet stock's path to a disposition. The slice
 # is whole anchors -- a split anchor spends runs on sites `pin_results` can
 # never pin -- reachable by a recorded closure, under the cap, fixed for one
-# seed and moved by another, so the nightly's date seed walks the stock rather
+# seed and moved by another, so the nightly's run seed walks the stock rather
 # than retrying the same survivors.
 _dp_site = lambda anchor, file, line: {  # noqa: E731
     "anchor": anchor, "file": file, "line": line, "kind": "CLAMP_DROP",
@@ -36107,7 +36107,7 @@ R.check(
 )
 
 # Wired, against the YAML: the measuring job holds no write grant and runs the
-# drain with a date seed; the pushing job runs no driver, applies through
+# drain with the run's seed; the pushing job runs no driver, applies through
 # `apply_drained` with the measured head's diff, checks the write set, pushes
 # only to main under the writer's subject, and is graded by `drain_report`.
 _ml_meas = _workflow_job(_NIGHTLY_YML, "mutation-ledger")
@@ -36115,12 +36115,12 @@ _ml_push = _workflow_job(_NIGHTLY_YML, "mutation-ledger-push")
 _ML_MISSING = [w for w, job in (
     ('--scope full --drain "$out" --shard ${{ matrix.shard }}/4', _ml_meas),
     ("--max 80 --jobs 4", _ml_meas),
-    ("--budget-minutes 240", _ml_meas),
+    ("--budget-minutes 270", _ml_meas),
     ("shard: [1, 2, 3, 4]", _ml_meas),
     ("pattern: mutation-ledger-*", _ml_push),
     ("m.merge_pin_shards(sys.argv[1], sys.argv[2])", _ml_push),
     ("if: always() && matrix.shard == 1", _ml_meas),
-    ('--seed "$(date -u +%Y%m%d)"', _ml_meas),
+    ('--seed "${{ github.run_id }}"', _ml_meas),
     ("github.event_name != 'push'", _ml_meas),
     ("needs.mutation-ledger.result == 'success'", _ml_push),
     ("m.apply_drained(pins, head, changed)", _ml_push),
@@ -38407,7 +38407,7 @@ R.check(
 # pull request's pin step only to a base program that has the flag.
 _MUT_BW_MISSING = [(j, w) for j, w in (
     ("mutation-nightly", "--budget-minutes 270"),
-    ("mutation-ledger", "--budget-minutes 240"),
+    ("mutation-ledger", "--budget-minutes 270"),
     ("mutation-pins", "&& budget=(--budget-minutes 260)"),
     ("mutation-pins", '"${budget[@]}" "${shard[@]}" 2>&1 | tee "$RUNNER_TEMP/pin-run.txt"'),
     # The budget's ceilings, derived 2026-10-09 from the draw_range-class
@@ -38736,6 +38736,56 @@ R.check(
     if _MUT_BG2_OUT else f"drive_pin_pool="
                          f"{'absent' if _mut_pin is None else 'present'}",
 )
+
+# A pair `reach_skip` frees costs no run, so admission must not charge it
+# (R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT): the drain's 06 Nov shards closed
+# their pools 16-80 minutes before --budget-minutes with 185 of 320 drawn
+# sites unstarted, charging each mutant the sweep of drivers its traced
+# baselines never ran. The fixture of the check above plus a 1000 s driver
+# every mutant's trace frees: charged, it closes the pool before the first
+# mutant; freed, the schedules measure what the 40 s driver alone allows,
+# and the freed driver never runs. A predicate freeing nothing is the null
+# control: both schedules close at once, as charging everything would.
+def _mut_rf_run(schedule, workers, free):
+    _MUT_BG2_T[0] = 0.0
+    ran: list = []
+    pool = [dict(m, drivers=["tests/a.py", "tests/big.py"])
+            for m in _MUT_BG2_POOL]
+
+    def drive(w, m, s):
+        ran.append((m["line"], s))
+        _MUT_BG2_T[0] += {"tests/a.py": 40, "tests/big.py": 1000}[s] / workers
+        return False
+
+    try:
+        out = schedule(pool, workers, {"tests/a.py": 40, "tests/big.py": 1000},
+                       drive, deadline=100, clock=lambda: _MUT_BG2_T[0],
+                       free=free)
+    except TypeError as exc:
+        return repr(exc)
+    return [v for _, v in out], sorted(ran)
+
+
+_mut_rf_big = lambda m, s: s == "tests/big.py"  # noqa: E731
+_MUT_RF_OUT = ((_mut_rf_run(_mut.drive_pool, 1, _mut_rf_big),
+                _mut_rf_run(_mut_pin, 4, _mut_rf_big),
+                _mut_rf_run(_mut.drive_pool, 1, lambda m, s: False),
+                _mut_rf_run(_mut_pin, 4, lambda m, s: False))
+               if _mut_pin is not None else None)
+R.check(
+    "budget admission charges no pair reach_skip frees, in both schedules, "
+    "and main() hands the schedule its reach predicate",
+    _MUT_RF_OUT is not None
+    and _MUT_RF_OUT[0] == (["LIVES", "LIVES", "SKIP-BUDGET", "SKIP-BUDGET"],
+                           [(0, "tests/a.py"), (1, "tests/a.py")])
+    and _MUT_RF_OUT[1] == (["LIVES"] * 4,
+                           [(i, "tests/a.py") for i in range(4)])
+    and _MUT_RF_OUT[2] == (["SKIP-BUDGET"] * 4, [])
+    and _MUT_RF_OUT[3] == (["SKIP-BUDGET"] * 4, [])
+    and "free=reach_free)" in _MUT_BODY,
+    f"{_MUT_RF_OUT!r}" if _MUT_RF_OUT else
+    f"drive_pin_pool={'absent' if _mut_pin is None else 'present'}",
+)
 # R9-CI-1: #2025's pin step started none of 56 sites (run 37663843895). The
 # split charged every admitted mutant its EXCLUSIVE tail up front -- stress.py
 # and harness_headers.py at three runs each, ~2535 s -- and every lazy driver
diff --git a/tests/mutation_table.py b/tests/mutation_table.py
index 5e235a33d..11b6e3cac 100644
--- a/tests/mutation_table.py
+++ b/tests/mutation_table.py
@@ -1460,7 +1460,7 @@ def drain_pool(unpinned: list[dict], closures: dict, allow: list[str],
     `pin_results` pins one only when all of them were driven and killed, and a
     slice that split an anchor would spend runs on sites it can never pin. The
     anchors are ordered by a hash of (seed, anchor), so the slice is fixed for
-    one seed and the nightly's date seed walks the stock rather than retrying
+    one seed and the nightly's run seed walks the stock rather than retrying
     the same survivors every night; an anchor no recorded closure reaches is
     left out, and anchors are taken while their sites fit under `cap`.
 
@@ -2792,7 +2792,7 @@ def drive_baselines(needed: list[str], workers: int, run, *, null_run=None,
 
 def drive_pool(pool: list[dict], workers: int, cost: dict[str, float],
                drive, settle=None, deadline: float | None = None,
-               clock=time.monotonic) -> list[tuple[dict, str]]:
+               clock=time.monotonic, free=None) -> list[tuple[dict, str]]:
     """Each mutant's verdict, its drivers shared over `workers` trees.
 
     `drive(worker, mut, script)` runs one driver on `mut` in that worker's tree
@@ -2815,7 +2815,10 @@ def drive_pool(pool: list[dict], workers: int, cost: dict[str, float],
     `deadline`, a `clock()` reading, is the budget (R9-F10.12). A mutant is
     started only if its every driver at `cost` -- the sweep it costs if it
     survives -- plus the EXCLUSIVE runs still owed by started mutants no driver
-    has killed, ends by then. The first that does not fit closes the pool:
+    has killed, ends by then. A pair `free(mut, script)` calls unkillable
+    (`reach_skip`: its traced baseline never ran the line) is neither queued
+    nor charged: it costs no run, so charging it closed the pool on a sweep
+    the night would never have spent. The first that does not fit closes the pool:
     it and every later one are SKIP-BUDGET, never started, so what ran is the
     shuffled pool's prefix and not a sample biased to cheap drivers. The cut
     falls on an anchor boundary: a mutant is admitted with every queued site
@@ -2826,7 +2829,8 @@ def drive_pool(pool: list[dict], workers: int, cost: dict[str, float],
     timeout over the estimate, not one per driver.
     """
     lock = threading.Lock()
-    todo = [[s for s in m["drivers"] if s not in EXCLUSIVE] for m in pool]
+    todo = [[s for s in m["drivers"] if s not in EXCLUSIVE
+             and not (free and free(m, s))] for m in pool]
     owes = [sum(cost.get(s, 0.0) for s in m["drivers"] if s in EXCLUSIVE)
             for m in pool]
     verdict: list[str | None] = [None] * len(pool)
@@ -2930,7 +2934,7 @@ MAX_PIN_JOBS = 8
 
 def drive_pin_pool(pool: list[dict], workers: int, cost: dict[str, float],
                    drive, settle=None, deadline: float | None = None,
-                   clock=time.monotonic) -> list[tuple[dict, str]]:
+                   clock=time.monotonic, free=None) -> list[tuple[dict, str]]:
     """Each pin-drive mutant's verdict, its shared drivers run N-way.
 
     The tasks are (mutant, driver) pairs, not whole mutants: a worker takes
@@ -2970,8 +2974,8 @@ def drive_pin_pool(pool: list[dict], workers: int, cost: dict[str, float],
     k = max(1, workers)
     lock = threading.Lock()
     order = [{s: i for i, s in enumerate(m["drivers"])} for m in pool]
-    shared0 = [[s for s in m["drivers"] if s not in EXCLUSIVE]
-               for m in pool]
+    shared0 = [[s for s in m["drivers"] if s not in EXCLUSIVE
+                and not (free and free(m, s))] for m in pool]
     todo = [list(s) for s in shared0]
     verdict: list[str | None] = [None] * len(pool)
     timed: list[list[str]] = [[] for _ in pool]
@@ -4131,6 +4135,17 @@ def main(argv: list[str] | None = None) -> int:
                   f"each row is hidden from that mutant's tree, so it cannot "
                   f"read killed for the row's sake (invalidated_rows)")
 
+        def reach_free(mut: dict, s: str) -> bool:
+            """A pair its traced baseline shows cannot kill, recorded as
+            reach-skipped before the schedule queues it, so the budget never
+            charges it (drive_pool's `free`). A lazy driver has no trace yet:
+            `drive` checks its pairs once its baseline has run."""
+            if not reach_skip(reaches.get(s), mut):
+                return False
+            reach_skipped.append((triage_key(mut), s))
+            outcomes[(id(mut), s)] = False
+            return True
+
         def drive(w: int, mut: dict, s: str) -> bool:
             # One task per worker at a time, so a tree carries one mutant.
             if verdicts.stop is not None:
@@ -4173,7 +4188,8 @@ def main(argv: list[str] | None = None) -> int:
             results += drive_phase(
                 [m for m in pool if id(m) in mutated], jobs, seconds, drive,
                 settle=lambda s: (s in deferred and verdicts.stop is None
-                                  and settle(s)), deadline=deadline)
+                                  and settle(s)), deadline=deadline,
+                free=reach_free)
         except Deferred as stop:
             return stop.rc
         if verdicts.stop is not None:

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
