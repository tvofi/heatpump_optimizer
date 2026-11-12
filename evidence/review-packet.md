# Review packet #3502
head: 2aa65fa6d39b06bd67201d6658019ae38f05b0bd
base: 2b4515dc52821ad721225090d329c224dbddafae

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131211360455 success
arch-score / arch-score id=131210959322 success
arm id=131210628741 skipped
budget-raise-gate / budget-raise-gate id=131210959450 success
cancel-superseded id=131210623548 success
codeql id=131210963421 skipped
codeql / Analyze (actions) id=131210913846 success
codeql / Analyze (javascript-typescript) id=131210914300 success
codeql / Analyze (python) id=131210913988 success
gate id=131211801687 failure
governance id=131210961465 skipped
governance / delivery-status id=131210914484 success
governance / delivery-status-publish id=131210916119 skipped
governance / env-matrix id=131210915902 success
governance / instrument-self-tests id=131210914672 success
governance / policy-docs id=131210914626 success
governance / record id=131210917049 skipped
governance / wave-script id=131210914655 success
hassfest id=131210963875 skipped
hassfest / hassfest id=131210914100 success
kernel-points id=131210961706 skipped
pr-contract id=131211803614 skipped
prelude id=131210623101 success
refresh id=131210624812 success
sweep-self id=131212210733 skipped
tests id=131210971424 skipped
tests / arch-instrument id=131211418347 in_progress
tests / briefs id=131210919962 success
tests / browser id=131211418451 success
tests / closure-scope id=131210915356 success
tests / closures id=131211418315 in_progress
tests / coverage id=131211418171 success
tests / coverage-ratchet id=131225213059 in_progress
tests / fast (3.14) id=131211418441 in_progress
tests / graders-head-copy id=131225212989 queued
tests / mutation id=131210914564 success
tests / mutation-autofix id=131211376261 skipped
tests / mutation-pins id=131211374821 skipped
tests / nightly-ha id=131211420813 skipped
tests / nightly-status id=131210914274 failure
tests / replay id=131211421558 skipped
tests / typing id=131211418255 success
validate id=131210961077 skipped
validate / validate-hacs id=131210914052 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 2aa65fa6d39b06bd67201d6658019ae38f05b0bd in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item c36778bf: dismissed:out-of-tree session inputs, named in instruments/scorecard.py.md
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

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
index 58a48dd9d8..c536e5b51c 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -484,6 +484,13 @@ jobs:
         if: steps.scope.outputs.bottleneck-alert == 'true'
         run: python3 -I tools/audit/seat/bottleneck_check.py --self-test
 
+      # The convergence scorecard's ten report-only lines: each rule held to its
+      # null control over planted inputs, offline, and one mutant per predicate.
+      - name: Show the scorecard holding each of its ten lines to its null control
+        id: scorecard
+        if: steps.scope.outputs.scorecard == 'true'
+        run: python3 -I tools/audit/seat/scorecard.py --self-test
+
       # The I3 barrier's own verdicts (BLIND, DEAD, REFUSED, unregistered) on a
       # synthetic registration, offline: `policy-docs` runs the base's copy,
       # which cannot answer for a change to this one.
diff --git a/dev/programme/delivery/3502.md b/dev/programme/delivery/3502.md
new file mode 100644
index 0000000000..cb700aefa5
--- /dev/null
+++ b/dev/programme/delivery/3502.md
@@ -0,0 +1 @@
+- [#3502](https://github.com/tvofi/heatpump_optimizer/pull/3502) — **open**, R10-MACH-SCORECARD: r10 mach scorecard (R10-MACH-SCORECARD)
diff --git a/tests/closures.json b/tests/closures.json
index 863633c4c5..36172cc22a 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4006,6 +4006,8 @@
    "tools/audit/seat/review_strength.py",
    "tools/audit/seat/roster_lib.py",
    "tools/audit/seat/roster_queue.py",
+   "tools/audit/seat/scorecard.py",
+   "tools/audit/seat/scorecard_selftest.py",
    "tools/audit/seat/selftest_wiring.py",
    "tools/audit/seat/survivor_list.py",
    "tools/audit/seat/sweep_driver.py",
@@ -5084,7 +5086,7 @@
    "seconds": 55.0
   },
   "tests/entities.py": {
-   "rc": 1,
+   "rc": 0,
    "seconds": 867.9
   },
   "tests/env_drift.py": {
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index b2c091fec2..72b0b6dca2 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -116,6 +116,7 @@ standing-seat liveness step keep the seats alive.
 - [`state_docs.py`](instruments/state_docs.py.md) — one call regenerates the four state docs (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`, `handover_prompt.py`), commits exactly their outputs to the orphan ref `handoff/audit-r<N>-plan` at `handoff/round<N>/state/`, N the roster's round
 - [`plan_public.py`](instruments/plan_public.py.md) — stages the ongoing round's plan page from the newest state ref for the public site, refusing a page that would publish a host path or a tool's attribution
 - [`bottleneck_check.py`](instruments/bottleneck_check.py.md) — prints one `BOTTLENECK:` line per flow metric past the owner's threshold, with a suggested action the orchestrator decides on, and nothing when none is
+- [`scorecard.py`](instruments/scorecard.py.md) — ten report-only convergence lines (gate and run health, first-verdict yield, machinery blocks, train skips, hotfix share, size, escapes, detection delay, seat cost), each but the hotfix naming measure held to a null control, written daily to `S/beatd/scorecard.txt`
 - [`outside_intake.py`](instruments/outside_intake.py.md) — lists submissions by outside users since a cursor with what each is owed (triage, answer, reply), and answers or refuses one, marked so none is answered twice
 - [`postmerge.py`](instruments/postmerge.py.md) — after a merge: the record-issue line, the roster stage, the state docs and main's suite state; a failed step is printed OWED and opens the ledger's `postmerge-owed`
 - [`record_beat.py`](instruments/record_beat.py.md) — one merged pull request's record-issue line from a fixed template, the full merge sha, read back byte-identical
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 4126564944..a07e17ac37 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -107,6 +107,10 @@ ROWS (the job table's `interval_s` in brackets):
                      owner's thresholds, 2026-11-07); a held breach re-prints its
                      first line, so it is new once per trip. A line suggests; the
                      orchestrator decides. `bottleneck: UNREADABLE` on a non-zero rc.
+  scorecard [86400]  scorecard.py `report --dir S/scorecard --train-log <train_log>
+                     [--sweep-record <sweep_record>]` into `S/beatd/scorecard.txt`
+                     (ten report-only lines, none a gate); the digest hears only
+                     `scorecard: UNREADABLE rc=<n>` when the instrument fails.
 No row runs `git checkout`, `reset`, `pull` or `merge`; main is read as
 `git -C <repo> cat-file -e origin/main:<path>`. No row touches a seat's alive
 file. Every row exits 0 once its lines are written: the digest is the signal,
@@ -129,7 +133,7 @@ import time
 from pathlib import Path
 
 ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "gantt", "verdict-audit", "pulse",
-        "cancel-sweep", "disk", "opener", "head-watch", "audit-dispatch", "outside-intake", "bottleneck")
+        "cancel-sweep", "disk", "opener", "head-watch", "audit-dispatch", "outside-intake", "bottleneck", "scorecard")
 HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
 #: roster-drain starts no op past this many seconds into a pass; the rest wait for the next pass. At
 #: most half the row's timeout_s in beatd.jobs.json (the self-test pins it), so an op started just
@@ -628,10 +632,25 @@ def bottleneck(ctx: Ctx) -> None:
     write_job(ctx, "bottleneck", [ln for ln in out.splitlines() if ln.startswith(("BOTTLENECK: ", "BOTTLENECK-UNREADABLE: "))])
 
 
+def scorecard(ctx: Ctx) -> None:
+    """scorecard.py report into S/beatd/scorecard.txt; report-only, so the digest hears only of a failed run."""
+    got = ctx.need("scorecard", "train_log")
+    if got is None:
+        return
+    args = ["report", "--dir", str(ctx.state / "scorecard"), "--train-log", got[0], "--repo", str(ctx.repo)]
+    if ctx.overlay.get("sweep_record"):
+        args += ["--sweep-record", str(ctx.overlay["sweep_record"])]
+    rc, out, err = ctx.py("tools/audit/seat/scorecard.py", *args)
+    if rc != 0 or not out.strip():
+        return write_job(ctx, "scorecard", [f"scorecard: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
+    atomic(ctx.state / "beatd" / "scorecard.txt", out)
+    write_job(ctx, "scorecard", [])
+
+
 RUN = {"tick-digest": tick_digest, "owed-check": owed_check, "roster-drain": roster_drain,
        "plan-beat": plan_beat, "gantt": gantt, "verdict-audit": verdict_audit, "pulse": pulse, "cancel-sweep": cancel_sweep, "disk": disk,
        "opener": opener, "head-watch": head_watch, "audit-dispatch": audit_dispatch,
-       "outside-intake": outside_intake, "bottleneck": bottleneck}
+       "outside-intake": outside_intake, "bottleneck": bottleneck, "scorecard": scorecard}
 
 
 def main(argv: list[str]) -> int:
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index 20ed9af3e4..bf0ca5ba98 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -507,6 +507,32 @@ def cases(bj) -> dict[str, bool]:
     res["bottleneck: an overlay without train_log is UNREADABLE and runs nothing"] = (
         digest(c) == "bottleneck: UNREADABLE overlay lacks train_log\n" and f.ran("bottleneck_check.py") == 0)
 
+    # scorecard
+    sc_out = "A_gate 1\nK 2\n"
+    c, f = fresh(answers={"scorecard.py": (0, sc_out, "")})
+    bj.scorecard(c)
+    sc = next((x for x in f.calls if any(a.endswith("scorecard.py") for a in x)), [])
+    res["scorecard null: a clean report leaves the digest empty and writes scorecard.txt"] = (
+        not digest(c) and f.ran("scorecard.py") == 1 and bj.read(c.state / "beatd" / "scorecard.txt") == sc_out)
+    res["scorecard: the instrument is handed report, its dir under state/, the train_log and the checkout"] = (
+        "report" in sc and arg(sc, "--dir") == str(c.state / "scorecard")
+        and arg(sc, "--train-log") == str(c.state / "train.log") and arg(sc, "--repo") == str(c.repo)
+        and "--sweep-record" not in sc)
+    ov = json.loads((c.state / "sweep-overlay.json").read_text())
+    c, f = fresh(overlay={**ov, "sweep_record": "/x/rec.json"}, answers={"scorecard.py": (0, sc_out, "")})
+    bj.scorecard(c)
+    sc = next((x for x in f.calls if any(a.endswith("scorecard.py") for a in x)), [])
+    res["scorecard: an overlay's sweep_record is handed on (null: none leaves the flag out)"] = (
+        arg(sc, "--sweep-record") == "/x/rec.json")
+    c, f = fresh(answers={"scorecard.py": (1, sc_out, "Traceback\nKeyError: 'x'\n")})
+    bj.scorecard(c)
+    res["scorecard: a failed instrument is UNREADABLE, never written"] = (
+        digest(c) == "scorecard: UNREADABLE rc=1: KeyError: 'x'\n" and not (c.state / "beatd" / "scorecard.txt").exists())
+    c, f = fresh(overlay={"repo": "o/r", "plan_slots": 10}, answers={"scorecard.py": (0, sc_out, "")})
+    bj.scorecard(c)
+    res["scorecard: an overlay without train_log is UNREADABLE and runs nothing"] = (
+        digest(c) == "scorecard: UNREADABLE overlay lacks train_log\n" and f.ran("scorecard.py") == 0)
+
     # roster-drain: the exact-line mark, UNRUN and CASCADE (folded from the retired roster_drain.py)
     c, f = fresh(answers={"roster_queue.py": (0, "", "")})
     (c.state / "roster-drain.queue").write_text("set-stage G1 done\n")
@@ -973,6 +999,13 @@ MUTANTS = {
     "bottleneck_unreadable_dropped": ('ln.startswith(("BOTTLENECK: ", "BOTTLENECK-UNREADABLE: "))',
                                       'ln.startswith(("BOTTLENECK: ",))',
                                       "bottleneck: each BOTTLENECK and BOTTLENECK-UNREADABLE line reaches the digest, nothing else"),
+    "scorecard_rc_clean": ('    if rc != 0 or not out.strip():\n        return write_job(ctx, "scorecard"',
+                           '    if not out.strip():\n        return write_job(ctx, "scorecard"',
+                           "scorecard: a failed instrument is UNREADABLE, never written"),
+    "scorecard_sweep_dropped": ('if ctx.overlay.get("sweep_record"):', "if False:",
+                                "scorecard: an overlay's sweep_record is handed on (null: none leaves the flag out)"),
+    "scorecard_write_dropped": ('    atomic(ctx.state / "beatd" / "scorecard.txt", out)\n', "    pass\n",
+                                "scorecard null: a clean report leaves the digest empty and writes scorecard.txt"),
     "plan_train_dropped": ('"--plan", plan, *train)', '"--plan", plan)',
                            "plan-beat: state_docs is handed the overlay's train_log (null: none leaves the flag out)"),
     "outside_lines_dropped": ('if ln.startswith("OUTSIDE ")]', 'if ln.startswith("OUTSIDEX ")]',
diff --git a/tools/audit/seat/beatd.jobs.json b/tools/audit/seat/beatd.jobs.json
index ac748746f5..780f713064 100644
--- a/tools/audit/seat/beatd.jobs.json
+++ b/tools/audit/seat/beatd.jobs.json
@@ -279,6 +279,24 @@
       "env_pass": [],
       "class": null,
       "kind": "periodic"
+    },
+    {
+      "name": "scorecard",
+      "argv": [
+        "python3",
+        "-I",
+        "tools/audit/seat/beat_jobs.py",
+        "scorecard",
+        "--state",
+        "$S"
+      ],
+      "cwd": "orch",
+      "interval_s": 86400,
+      "timeout_s": 600,
+      "heartbeat_s": null,
+      "env_pass": [],
+      "class": null,
+      "kind": "periodic"
     }
   ]
 }
diff --git a/tools/audit/seat/instruments/scorecard.py.md b/tools/audit/seat/instruments/scorecard.py.md
new file mode 100644
index 0000000000..ee69987209
--- /dev/null
+++ b/tools/audit/seat/instruments/scorecard.py.md
@@ -0,0 +1,38 @@
+# `scorecard.py`
+
+- `scorecard.py` — the convergence scorecard (R10-MACH-SCORECARD): ten
+  report-only lines, one per signal, the baseline from which thresholds can
+  later be set. No line sets an exit code or holds a merge. It is read-only on
+  every input and makes no GitHub call; an input it cannot read prints
+  `<line>  unread (<why>)`, never a guessed value. The lines:
+  - `A_gate` — the share of the last 20 concluded main `CI` runs whose job
+    `gate` succeeded (a run with no cached job listing is `unread`).
+  - `A_run` — the share of the same runs whose run conclusion is success.
+  - `Y_rev` — over the last 50 pull requests, the share whose first review
+    verdict (the earliest by `t`, whatever the order of `verdicts.json`) is `merge`.
+  - `M_first` — over the same 50, the share whose first verdict is `blocked`
+    in a machinery family (carry, body, CI state, merge state, root-cause
+    form, ruling or roster).
+  - `Y_train` — over the last 50 merges the merge train named, the share
+    never on a `SKIP #n` or `PARK` line.
+  - `H` — hotfix-token merges among the last 50 code merges (production or
+    instrument), with the production merges among them beside it. It has no
+    null control: it is a naming measure, a branch token, read with that caveat.
+  - `S` — size: `machinery_ratchet.py --measure` (non-production merges per
+    window, churn per 1 000 product lines) and machinery lines over product lines.
+  - `E` — roster groups whose source is `outside` and hotfix or bug groups
+    touching the product, and how many of both are still open.
+  - `C` — the longest run of consecutive cancelled main runs in the last 50.
+  - `K` — `recycle` lines of the standing dispatch and triage seats in the
+    day's sweep record.
+
+  Every line but `H` is held in `--self-test` to a null control (a case whose
+  right answer is the quiet one). Inputs sit under `<state>/scorecard/`
+  (`runs.json`, `jobs/jobs_<id>.json`, `verdicts.json`, `merges.tsv`,
+  `roster.json`) beside the overlay's `train_log` and the optional
+  `sweep_record`. When: the beat's `scorecard` row runs `report --dir
+  <state>/scorecard --train-log <train_log> --repo <checkout>` (plus
+  `--sweep-record` when the overlay names one) once a day and writes the
+  output to `S/beatd/scorecard.txt`; the digest hears only
+  `scorecard: UNREADABLE rc=<n>: <why>` when the run fails. `--self-test`:
+  planted and null cases per line, and one mutant per predicate.
diff --git a/tools/audit/seat/scorecard.py b/tools/audit/seat/scorecard.py
new file mode 100644
index 0000000000..97b4b64f48
--- /dev/null
+++ b/tools/audit/seat/scorecard.py
@@ -0,0 +1,276 @@
+#!/usr/bin/env python3
+"""Convergence scorecard: ten report-only lines, one per signal, each with its null control.
+
+    python3 -I scorecard.py report --dir D --train-log PATH [--repo DIR] [--sweep-record PATH]
+    python3 -I scorecard.py --self-test [--no-mutants]
+
+Report-only (R10-MACH-SCORECARD): no line sets an exit code or holds a merge. It
+is the baseline from which thresholds can later be set. Read-only on every
+input and no GitHub call; the inputs are refreshed elsewhere and an input it
+cannot read prints `<line>  unread (<why>)`, never a guessed value.
+
+INPUTS, all under D (the beat's `<state>/scorecard/`) except the train log:
+  runs.json      [{id, t, c}] main `CI` push runs: id, UTC stamp, run conclusion
+  jobs/jobs_<id>.json   the run's job listing (`{"jobs": [{name, conclusion}]}`)
+  verdicts.json  {"verdicts": [{pr, head, kind, cls, t}]} review verdicts
+  merges.tsv     TSV with columns pr, ct, class, tokens (merge order by ct)
+  roster.json    {"groups": [...]} the round's roster
+  ../study/work/yield.py  holds `FAMILY = [(name, regex), ...]`, read as a
+                 literal (never executed), the class-word to family map of M_first
+
+THE LINES (rule, then the null control the self-test holds it to):
+  A_gate   share of the last 20 concluded (success or failure) main runs whose
+           job named `gate` concluded success; a run with no cached job listing
+           is `unread`, reported and not guessed.
+           NULL: a run whose only failed job is `governance / instrument-self-tests`
+           counts green here and red in A_run.
+  A_run    share of the same runs whose run conclusion is success.
+           NULL: the same run counts red.
+  Y_rev    over the last 50 pull requests by first verdict (the earliest verdict by `t`,
+           whatever the order of verdicts.json): share whose first verdict is `merge`.
+           NULL: a bus of merge verdicts only prints 100%.
+  M_first  same 50: share whose first verdict is `blocked` in a machinery family
+           (MACH: carry, body, CI state, merge state, root-cause form, ruling or roster).
+           NULL: the same bus prints 0%.
+  Y_train  over the last 50 merged pull requests the merge train named: share
+           never on a `SKIP #n` or `PARK` line. A pull request the train never
+           named is not counted.
+           NULL: a log with no SKIP or PARK line prints 100%.
+  H        hotfix-token merges among the last 50 code merges (class production
+           or instrument), with the production merges among those 50 beside it.
+           NO NULL CONTROL: it is a naming measure (a branch token), read with
+           that caveat. The study's own text gives it none and none is invented.
+  S        size: `machinery_ratchet.py --measure --head origin/main` (its JSON's
+           non-production merges per window and churn per 1 000 product lines),
+           and machinery lines over product lines from `git grep -c ''` over
+           `tools .github .claude dev/governance` against `custom_components blueprints`.
+           NULL: a frozen machinery gives a flat or falling ratio (the ratio
+           of two unchanged counts is unchanged).
+  E        escapes: roster groups whose source is `outside`, and hotfix or bug
+           groups (group names HOTFIX, or kind bug|hotfix) whose files include
+           the product (`custom_components/`); and how many of both are still
+           open (resume.stage not `done`).
+           NULL: a round with no escape adds none.
+  C        detection delay: the longest run of consecutive cancelled main runs
+           in the last 50 runs (cancelled runs included, ordered by stamp).
+           NULL: C is 0 when no main run is cancelled.
+  K        seat cost: `recycle` lines of the standing dispatch and triage seats
+           in the day's sweep record.
+           NULL: K is 0 with no recycle line.
+C and K are one row of the study's table and print on one line.
+"""
+from __future__ import annotations
+
+import argparse
+import ast
+import collections
+import csv
+import io
+import json
+import re
+import subprocess
+import sys
+from pathlib import Path
+
+WINDOW_RUNS = 20
+WINDOW_PRS = 50
+WINDOW_MERGES = 50
+WINDOW_CANCEL = 50
+MACH = {"carry-bookkeeping", "body-bookkeeping", "ci-state", "merge-state", "root-cause-form", "ruling-or-roster"}
+RECYCLE = re.compile(r"\brecycle", re.I)
+SEATS = re.compile(r"standing[- ](?:dispatch|triage)|\b(?:dispatch|triage)\b", re.I)
+
+
+def pct(n: int, d: int) -> str:
+    return f"{100 * n / d:.0f}%" if d else "n/a"
+
+
+def family_of(cls: str, fam: list) -> str:
+    for name, rx in fam:
+        if re.match(rx, cls):
+            return name
+    return "unmapped"
+
+
+def load_family(text: str) -> list:
+    """FAMILY from yield.py's source, as a literal; nothing is executed."""
+    i = text.index("FAMILY = [")
+    j = text.index("def fam(", i)
+    return ast.literal_eval(text[i:j].split("=", 1)[1].strip())
+
+
+def line_a(runs: list, gate: dict) -> list[str]:
+    ok = [r for r in sorted(runs, key=lambda r: r["t"]) if r["c"] in ("success", "failure")][-WINDOW_RUNS:]
+    if not ok:
+        return ["A_gate  unread (no concluded main run)", "A_run   unread (no concluded main run)"]
+    g = collections.Counter("success" if r["c"] == "success" else gate.get(r["id"], "unread") for r in ok)
+    read = g["success"] + g["failure"]
+    run_ok = sum(r["c"] == "success" for r in ok)
+    gate_part = f"{g['success']}/{read} read = {pct(g['success'], read)}" if read else "0/0 read"
+    return [f"A_gate  {gate_part}  (unread {g['unread']} of {len(ok)}; window {ok[0]['t']} .. {ok[-1]['t']})",
+            f"A_run   {run_ok}/{len(ok)} = {pct(run_ok, len(ok))}"]
+
+
+def line_review(verdicts: list, fam: list | None) -> list[str]:
+    first: dict = {}
+    for v in sorted(verdicts, key=lambda v: v["t"]):  # the first verdict is the earliest by t, whatever the file order
+        first.setdefault(v["pr"], v)
+    last = list(first.values())[-WINDOW_PRS:]
+    if not last:
+        return ["Y_rev   unread (no verdict)", "M_first unread (no verdict)"]
+    n = len(last)
+    first_merge = sum(v["kind"] == "merge" for v in last)
+    span = f"first verdicts {last[0]['t'][:16]} .. {last[-1]['t'][:16]}"
+    y = f"Y_rev   first verdict merge {first_merge}/{n} = {pct(first_merge, n)}  ({span})"
+    if fam is None:
+        return [y, "M_first unread (no family map)"]
+    mf = sum(v["kind"] == "blocked" and family_of(v["cls"], fam) in MACH for v in last)
+    return [y, f"M_first {mf}/{n} = {pct(mf, n)}  ({span})"]
+
+
+def line_train(merged: list[str], train_text: str) -> str:
+    skipped, named = set(), set()
+    for ln in train_text.splitlines():
+        m = re.match(r"SKIP #(\d+)", ln)
+        if m:
+            skipped.add(m[1])
+        if ln.startswith("PARK"):
+            skipped |= set(re.findall(r"#(\d{4})", ln)[:1])
+        if re.match(r"(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)", ln):
+            named |= set(re.findall(r"#(\d{4})", ln))
+    tn = [p for p in merged if p in named][-WINDOW_MERGES:]
+    clean = sum(p not in skipped for p in tn)
+    return f"Y_train never skipped or parked {clean}/{len(tn)} = {pct(clean, len(tn))}  (last {WINDOW_MERGES} train-named merged PRs)"
+
+
+def line_hotfix(rows: list[dict]) -> str:
+    code = [r for r in rows if r["class"] in ("production", "instrument")][-WINDOW_MERGES:]
+    hot = sum("hotfix" in r["tokens"] for r in code)
+    prod = sum(r["class"] == "production" for r in code)
+    return (f"H       hotfix-token merges {hot}/{len(code)} of the last {WINDOW_MERGES} code merges; "
+            f"production merges among them {prod}  (naming measure, no null control)")
+
+
+def line_escapes(groups: list[dict]) -> str:
+    out = [x for x in groups if x.get("source") == "outside"]
+    ph = [x for x in groups if ("HOTFIX" in x["group"] or x.get("kind") in ("bug", "hotfix"))
+          and any(f.startswith("custom_components/") for f in (x.get("files") or []))]
+    openn = sum((x.get("resume") or {}).get("stage") != "done" for x in out + ph)
+    return (f"E       roster groups from outside reports {len(out)}; hotfix or bug groups touching the product "
+            f"{len(ph)}; open among both {openn}")
+
+
+def cancel_streak(runs: list) -> int:
+    best = cur = 0
+    for r in sorted(runs, key=lambda r: r["t"])[-WINDOW_CANCEL:]:
+        cur = cur + 1 if r["c"] == "cancelled" else 0
+        best = max(best, cur)
+    return best
+
+
+def recycle_count(record: str) -> int:
+    return sum(bool(RECYCLE.search(ln) and SEATS.search(ln)) for ln in record.splitlines())
+
+
+def line_ck(runs: list | None, record: str | None) -> str:
+    c = f"C {cancel_streak(runs)}" if runs is not None else "C unread"
+    k = f"K {recycle_count(record)}" if record is not None else "K unread"
+    return f"C, K    {c}; {k}  (longest cancelled main-run streak; recycle lines of the dispatch and triage seats)"
+
+
+def sh_out(argv: list[str], cwd: Path) -> tuple[int, str]:
+    try:
+        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=600)
+    except (OSError, subprocess.TimeoutExpired) as e:
+        return 127, str(e)
+    return p.returncode, p.stdout
+
+
+def count_lines(repo: Path, paths: list[str], run=sh_out) -> int | None:
+    rc, out = run(["git", "grep", "-c", "", "origin/main", "--", *paths], repo)
+    if rc not in (0, 1):
+        return None
+    return sum(int(ln.rsplit(":", 1)[1]) for ln in out.splitlines() if ":" in ln and ln.rsplit(":", 1)[1].isdigit())
+
+
+def line_size(repo: Path, run=sh_out) -> list[str]:
+    rc, out = run([sys.executable, "-I", "tools/audit/machinery_ratchet.py", "--measure", "--head", "origin/main"], repo)
+    mach = count_lines(repo, ["tools", ".github", ".claude", "dev/governance"], run)
+    prod = count_lines(repo, ["custom_components", "blueprints"], run)
+    try:
+        m = json.loads(out) if rc == 0 else None
+        lines = [f"S       non-production merges {m['nonproduction_merges']} per {m['window']}; "
+                 f"churn {m['churn_per_kilo_product_lines']} per 1 000 product lines"]
+    except (ValueError, KeyError, TypeError):
+        lines = ["S       ratchet unread"]
+    if mach is None or not prod:
+        lines.append("S       machinery/product unread")
+    else:
+        lines.append(f"S       machinery {mach} / product {prod} = {mach / prod:.2f}")
+    return lines
+
+
+def rd(path: Path):
+    try:
+        return path.read_text()
+    except OSError:
+        return None
+
+
+def report(d: Path, train_log: Path, repo: Path | None, record: Path | None, run=sh_out) -> list[str]:
+    out: list[str] = []
+
+    def load(name):
+        t = rd(d / name)
+        try:
+            return None if t is None else json.loads(t)
+        except ValueError:
+            return None
+
+    runs = load("runs.json")
+    gate: dict = {}
+    for f in sorted((d / "jobs").glob("jobs_*.json")) if (d / "jobs").is_dir() else []:
+        try:
+            for j in json.loads(f.read_text()).get("jobs", []):
+                if j["name"] == "gate":
+                    gate[int(f.stem.split("_")[1])] = j["conclusion"]
+        except (ValueError, KeyError, IndexError):
+            continue
+    out += line_a(runs, gate) if runs else ["A_gate  unread (runs.json)", "A_run   unread (runs.json)"]
+    v = load("verdicts.json")
+    ytxt = rd(d.parent / "study" / "work" / "yield.py")
+    try:
+        fam = load_family(ytxt) if ytxt else None
+    except (ValueError, SyntaxError):
+        fam = None
+    out += line_review(v["verdicts"], fam) if v else ["Y_rev   unread (verdicts.json)", "M_first unread (verdicts.json)"]
+    mt, tt = rd(d / "merges.tsv"), rd(train_log)
+    rows = sorted(csv.DictReader(io.StringIO(mt), delimiter="\t"), key=lambda r: int(r["ct"])) if mt else None
+    out.append(line_train([r["pr"] for r in rows if r["pr"]], tt) if rows is not None and tt is not None
+               else "Y_train unread (merges.tsv or train log)")
+    out.append(line_hotfix(rows) if rows is not None else "H       unread (merges.tsv)")
+    out += line_size(repo, run) if repo else ["S       unread (no checkout)"]
+    ro = load("roster.json")
+    out.append(line_escapes(ro["groups"]) if ro else "E       unread (roster.json)")
+    out.append(line_ck(runs, rd(record) if record else None))
+    return out
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--self-test"]:
+        import scorecard_selftest
+        return scorecard_selftest.run(Path(__file__), mutants="--no-mutants" not in argv)
+    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
+    ap.add_argument("cmd", choices=["report"])
+    ap.add_argument("--dir", required=True, type=Path)
+    ap.add_argument("--train-log", required=True, type=Path)
+    ap.add_argument("--repo", type=Path)
+    ap.add_argument("--sweep-record", type=Path)
+    a = ap.parse_args(argv)
+    print("\n".join(report(a.dir, a.train_log, a.repo, a.sweep_record)))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.path.insert(0, str(Path(__file__).resolve().parent))
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/scorecard_selftest.py b/tools/audit/seat/scorecard_selftest.py
new file mode 100644
index 0000000000..494fe70b3f
--- /dev/null
+++ b/tools/audit/seat/scorecard_selftest.py
@@ -0,0 +1,218 @@
+"""Self-test of scorecard.py: a null control and a planted case per line, and one mutant per predicate.
+
+Run through scorecard.py's own test mode, with or without the mutants. Offline, in-process over
+planted inputs; the mutants edit a temp copy of scorecard.py, and a mutant that survives, or whose
+copy does not run, fails the test.
+"""
+from __future__ import annotations
+
+import importlib.util
+import json
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+H = "a" * 40
+
+
+def load(path: Path):
+    spec = importlib.util.spec_from_file_location("scorecard_under_test", path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def runs(spec):
+    """[(conclusion, id)] -> run rows with ascending stamps."""
+    return [{"id": i, "t": f"2026-11-{1 + k // 24:02d}T{k % 24:02d}:00:00Z", "c": c} for k, (c, i) in enumerate(spec)]
+
+
+def verdicts(spec):
+    return [{"pr": p, "head": H, "kind": k, "cls": c, "t": f"2026-11-01T00:{n % 60:02d}:{n // 60:02d}Z"}
+            for n, (p, k, c) in enumerate(spec)]
+
+
+FAM = [("carry-bookkeeping", r"carry"), ("code", r"code")]
+TRAIN_CLEAN = "BATCH #1001 #1002\nMERGED #1001\nMERGED #1002\n"
+
+
+def cases(sc) -> dict[str, bool]:
+    r: dict[str, bool] = {}
+    # A_gate / A_run
+    rs = runs([("success", 1)] * 4 + [("failure", 5)])
+    ag, ar = sc.line_a(rs, {5: "success"})  # only a non-gate job failed
+    r["A_gate null: a run failing only outside the gate job counts green"] = "5/5 read = 100%" in ag
+    r["A_run null: the same run counts red"] = ar.startswith("A_run   4/5 = 80%")
+    ag, _ = sc.line_a(rs, {5: "failure"})
+    r["A_gate planted: a run whose gate job failed counts red"] = "4/5 read = 80%" in ag
+    ag, _ = sc.line_a(rs, {})
+    r["A_gate: a failed run with no job listing is unread, not guessed"] = "4/4 read = 100%" in ag and "unread 1 of 5" in ag
+    ag, ar = sc.line_a(runs([("cancelled", 9)] + [("success", 1)] * 2), {})
+    r["A_*: a cancelled run is not a concluded run"] = "2/2" in ag and "2/2" in ar
+    ag, ar = sc.line_a(runs([("failure", 100 + i) for i in range(5)] + [("success", i) for i in range(20)]), {})
+    r["A_*: only the last 20 concluded runs are read"] = "20/20 read = 100%" in ag and "20/20 = 100%" in ar
+    # Y_rev / M_first
+    bus = verdicts([(i, "merge", "none") for i in range(60)])
+    y, m = sc.line_review(bus, FAM)
+    r["Y_rev null: a bus of merge verdicts prints 100% over the last 50"] = "50/50 = 100%" in y
+    r["M_first null: the same bus prints 0%"] = m.startswith("M_first 0/50 = 0%")
+    mix = verdicts([(1, "blocked", "carry-x"), (2, "blocked", "code-x"), (3, "merge", "carry-x"), (4, "blocked", "zzz"),
+                    (1, "merge", "none"), (1, "blocked", "carry-x")])
+    y, m = sc.line_review(mix, FAM)
+    r["Y_rev planted: one merge first in four pull requests"] = "merge 1/4 = 25%" in y
+    r["M_first planted: only a blocked first verdict in a machinery family counts"] = m.startswith("M_first 1/4 = 25%")
+    # the first verdict is the earliest by t, in any file order; the window is the 50 latest first verdicts
+    shuf = [{"pr": 1, "head": H, "kind": "blocked", "cls": "carry-x", "t": "2026-11-03T00:00:00Z"},
+            {"pr": 1, "head": H, "kind": "merge", "cls": "none", "t": "2026-11-01T00:00:00Z"},
+            {"pr": 2, "head": H, "kind": "blocked", "cls": "zzz", "t": "2026-11-02T00:00:00Z"}]
+    y, m = sc.line_review(shuf, FAM)
+    r["Y_rev unordered: the earliest verdict by t is the first, not the first in the file"] = \
+        "merge 1/2 = 50%" in y and "first verdicts 2026-11-01T00:00 .. 2026-11-02T00:00" in y and m.startswith("M_first 0/2 = 0%")
+    rev = [{"pr": i, "head": H, "kind": "merge" if i < 50 else "blocked", "cls": "none",
+            "t": f"2026-11-{1 + (99 - i) // 24:02d}T{(99 - i) % 24:02d}:00:00Z"} for i in range(60)]
+    y, _ = sc.line_review(rev, FAM)
+    r["Y_rev unordered window: the 50 latest first verdicts, whatever the file order"] = "merge 50/50 = 100%" in y
+    y, _ = sc.line_review([{"pr": 1, "head": H, "kind": "blocked", "cls": "zzz", "t": "2026-11-01T00:00:00Z"},
+                           {"pr": 1, "head": H, "kind": "merge", "cls": "none", "t": "2026-11-02T00:00:00Z"}], FAM)
+    r["Y_rev first verdict: a later merge does not make a blocked first verdict a merge"] = "merge 0/1 = 0%" in y
+    y, m = sc.line_review(mix, None)
+    r["M_first without a family map is unread, Y_rev still prints"] = "unread" in m and "1/4" in y
+    # Y_train
+    mg = ["1001", "1002", "1003"]
+    t = sc.line_train(mg, TRAIN_CLEAN)
+    r["Y_train null: a log with no SKIP or PARK line prints 100%; an unnamed pull request is not counted"] = "2/2 = 100%" in t
+    t = sc.line_train(mg, TRAIN_CLEAN + "SKIP #1001 red\nPARK #1002 held\n")
+    r["Y_train planted: a SKIP line and a PARK line each cost the pull request"] = "0/2 = 0%" in t
+    t = sc.line_train(["1003"], "MERGED #1003\n")
+    r["Y_train named: a pull request named only on a MERGED line is counted"] = "1/1 = 100%" in t
+    # H
+    rows = [{"class": "production", "tokens": "hotfix-x"}, {"class": "instrument", "tokens": "hotfix"},
+            {"class": "docs", "tokens": "hotfix"}, {"class": "production", "tokens": "feat"}]
+    r["H: hotfix-token merges over code merges, docs not counted, production beside"] = \
+        "2/3 of the last 50 code merges; production merges among them 2" in sc.line_hotfix(rows)
+    r["H states it has no null control"] = "no null control" in sc.line_hotfix(rows)
+    # E
+    g = [{"group": "A", "source": "outside", "resume": {"stage": "done"}},
+         {"group": "R10-HOTFIX-X", "files": ["custom_components/a.py"], "resume": {"stage": "fix"}},
+         {"group": "B", "kind": "bug", "files": ["custom_components/b.py"]},
+         {"group": "C", "kind": "bug", "files": ["tools/x.py"]},
+         {"group": "D", "files": ["custom_components/d.py"]}]
+    e = sc.line_escapes(g)
+    r["E planted: one outside, two product hotfix or bug groups, two open"] = "outside reports 1;" in e and "product 2;" in e and "open among both 2" in e
+    r["E null: a round with no escape adds none"] = "reports 0; hotfix or bug groups touching the product 0; open among both 0" in sc.line_escapes([{"group": "D"}])
+    # C / K
+    cn = sc.line_ck(runs([("success", 1)] * 4), "all fine\n")
+    r["C, K null: no cancelled run and no recycle line are both 0"] = "C 0; K 0" in cn
+    cp = sc.line_ck(runs([("cancelled", 1), ("success", 2), ("cancelled", 3), ("cancelled", 4), ("cancelled", 5), ("success", 6)]),
+                    "standing-dispatch recycle at 10:00\nstanding triage RECYCLE\nroster recycle\nstanding-dispatch ok\n")
+    r["C planted: the longest consecutive cancelled streak"] = "C 3;" in cp
+    r["K planted: only recycle lines of the dispatch and triage seats"] = "K 2" in cp
+    r["C, K unread input is named, never 0"] = "C unread; K unread" in sc.line_ck(None, None)
+    # S
+    def fake(argv, cwd):
+        if "machinery_ratchet.py" in argv[2]:
+            return 0, '{"nonproduction_merges": 498, "window": 580, "churn_per_kilo_product_lines": 12299}\n'
+        paths = argv[-1:] if False else argv
+        n = "100" if "custom_components" in argv else "300"
+        return 0, f"origin/main:f:{n}\n"
+    s = sc.line_size(Path("."), fake)
+    r["S: the ratchet line verbatim and machinery over product"] = any("merges 498 per 580; churn 12299 per" in x for x in s) and any("300 / product 100 = 3.00" in x for x in s)
+    s2 = sc.line_size(Path("."), lambda argv, cwd: (0, "x:1\n") if "machinery_ratchet.py" not in argv[2] else (0, '{"nonproduction_merges": 1, "window": 2, "churn_per_kilo_product_lines": 3}'))
+    r["S null: frozen machinery and product give an unchanged ratio"] = s2[-1] == sc.line_size(Path("."), lambda argv, cwd: (0, "x:1\n") if "machinery_ratchet.py" not in argv[2] else (0, '{"nonproduction_merges": 1, "window": 2, "churn_per_kilo_product_lines": 3}'))[-1]
+    s3 = sc.line_size(Path("."), lambda argv, cwd: (2, ""))
+    s4 = sc.line_size(Path("."), lambda argv, cwd: fake(argv, cwd) if "machinery_ratchet.py" in argv[2] else (2, "origin/main:f:5\n"))
+    r["S: an unreadable ratchet is unread, never a number"] = "ratchet unread" in s3[0]
+    s5 = sc.line_size(Path("."), lambda argv, cwd: (3, '{"nonproduction_merges": 1, "window": 2, "churn_per_kilo_product_lines": 3}\n')
+                      if "machinery_ratchet.py" in argv[2] else fake(argv, cwd))
+    r["S: a ratchet that exits non-zero is unread even when it printed JSON"] = "ratchet unread" in s5[0]
+    r["S: an unreadable line count is unread, never a ratio"] = "498 per 580" in s4[0] and s4[-1].endswith("unread")
+    # the whole report over a planted state dir, and over an empty one
+    with tempfile.TemporaryDirectory() as td:
+        d = Path(td) / "scorecard"
+        (d / "jobs").mkdir(parents=True)
+        (d / "runs.json").write_text(json.dumps(rs))
+        (d / "jobs" / "jobs_5.json").write_text(json.dumps({"jobs": [{"name": "gate", "conclusion": "success"},
+                                                                    {"name": "governance / instrument-self-tests", "conclusion": "failure"}]}))
+        (d / "verdicts.json").write_text(json.dumps({"verdicts": mix}))
+        (d / "merges.tsv").write_text("pr\tct\tclass\ttokens\n1001\t1\tproduction\thotfix\n1002\t2\tproduction\tx\n")
+        (d / "roster.json").write_text(json.dumps({"groups": g}))
+        (Path(td) / "study" / "work").mkdir(parents=True)
+        (Path(td) / "study" / "work" / "yield.py").write_text(f"FAMILY = {FAM!r}\ndef fam(c):\n    pass\n")
+        (Path(td) / "train.log").write_text(TRAIN_CLEAN)
+        (Path(td) / "sweep.txt").write_text("dispatch recycle\n")
+        out = sc.report(d, Path(td) / "train.log", None, Path(td) / "sweep.txt")
+        r["report: ten lines' worth over a planted state dir (S unread without a checkout)"] = \
+            len(out) == 9 and not any("unread (" in x for x in out if x[:2] != "S ") and out[0].startswith("A_gate  5/5")
+        r["report: A_gate reads the job named gate, not the last job listed"] = out[0].startswith("A_gate  5/5 read = 100%") and out[1].startswith("A_run   4/5")
+        r["report: K reads the sweep record it is given"] = "K 1 " in out[-1] and "K unread" not in out[-1]
+        empty = sc.report(Path(td) / "none", Path(td) / "none.log", None, None)
+        r["report: an empty state dir prints unread on every line, none a number"] = \
+            all("unread" in x for x in empty if not x.startswith("C, K")) and "C unread; K unread" in empty[-1]
+    return r
+
+
+#: (needle, replacement, the case that must fail). One per predicate.
+MUTANTS = {
+    "A_gate reads the run conclusion": ('"success" if r["c"] == "success" else gate.get(r["id"], "unread")', 'r["c"]', "A_gate null"),
+    "A_gate window": ("WINDOW_RUNS = 20", "WINDOW_RUNS = 21", "only the last 20"),
+    "A_run counts cancelled green": ('sum(r["c"] == "success" for r in ok)', 'sum(r["c"] != "cancelled" for r in ok)', "A_run null"),
+    "Y_rev not merge": ('first_merge = sum(v["kind"] == "merge"', 'first_merge = sum(v["kind"] != "merge"', "Y_rev null"),
+    "Y_rev window": ("WINDOW_PRS = 50", "WINDOW_PRS = 51", "Y_rev null"),
+    "M_first ignores kind": ('v["kind"] == "blocked" and family_of', 'True and family_of', "M_first planted"),
+    "M_first family inverted": ("in MACH for v in last", "not in MACH for v in last", "M_first planted"),
+    "Y_rev first verdict kept": ("first.setdefault(v[\"pr\"], v)", "first[v[\"pr\"]] = v", "Y_rev first verdict"),
+    "Y_rev ordered by t": ('sorted(verdicts, key=lambda v: v["t"])', "list(verdicts)", "Y_rev unordered"),
+    "A_gate job named gate": ('if j["name"] == "gate":', "if True:", "report: A_gate reads the job named gate"),
+    "report passes the record": ("rd(record) if record else None", "None", "report: K reads"),
+    "Y_train MERGED names": ('(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)', '(BATCH|SKIP|PARK|ADMIT|ALREADY)', "Y_train named"),
+    "S ratchet exit": ("json.loads(out) if rc == 0 else None", "json.loads(out)", "S: a ratchet that exits non-zero"),
+    "Y_train SKIP": ('r"SKIP #(\\d+)"', 'r"SKIPX #(\\d+)"', "Y_train planted"),
+    "Y_train PARK": ('ln.startswith("PARK")', 'ln.startswith("PARKX")', "Y_train planted"),
+    "Y_train unnamed counted": ("tn = [p for p in merged if p in named]", "tn = [p for p in merged]", "Y_train null"),
+    "H token": ('"hotfix" in r["tokens"]', '"hotfixx" in r["tokens"]', "H: hotfix"),
+    "H class filter": ('("production", "instrument")', '("production",)', "H: hotfix"),
+    "H production beside": ('r["class"] == "production" for r in code', 'r["class"] != "x" for r in code', "H: hotfix"),
+    "E outside": ('x.get("source") == "outside"', 'x.get("source") != "outside"', "E planted"),
+    "E hotfix name": ('"HOTFIX" in x["group"]', '"HOTFIXX" in x["group"]', "E planted"),
+    "E product files": ('f.startswith("custom_components/")', 'f.startswith("custom_componentsX/")', "E planted"),
+    "E open": ('.get("stage") != "done"', '.get("stage") == "done"', "E planted"),
+    "C streak": ('cur = cur + 1 if r["c"] == "cancelled" else 0', 'cur = cur + 1 if r["c"] == "cancelled" else cur', "C planted"),
+    "K seats": ("RECYCLE.search(ln) and SEATS.search(ln)", "RECYCLE.search(ln) or SEATS.search(ln)", "K planted"),
+    "S ratio inverted": ("mach / prod:.2f", "prod / mach:.2f", "S: the ratchet"),
+    "S unreadable count": ("if rc not in (0, 1):\n        return None", "if False:\n        return None", "S: an unreadable line count"),
+}
+
+
+def run(path: Path, mutants: bool = True) -> int:
+    bad: list[str] = []
+
+    def show(res: dict[str, bool]) -> None:
+        for name, ok in res.items():
+            print(("ok   " if ok else "FAIL ") + name)
+            if not ok:
+                bad.append(name)
+
+    show(cases(load(path)))
+    if mutants:
+        src = path.read_text()
+        here = Path(__file__).resolve()
+        for name, (old, new, case) in MUTANTS.items():
+            if src.count(old) != 1:
+                print(f"FAIL mutant {name}: needle found {src.count(old)} times")
+                bad.append(name)
+                continue
+            with tempfile.TemporaryDirectory() as td:
+                (Path(td) / path.name).write_text(src.replace(old, new))
+                (Path(td) / here.name).write_text(here.read_text())
+                p = subprocess.run([sys.executable, "-I", str(Path(td) / here.name)], capture_output=True, text=True, timeout=120)
+            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
+            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
+            if not killed:
+                bad.append("mutant " + name)
+    print("scorecard self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":  # a mutant copy runs its cases only
+    sys.exit(run(Path(__file__).with_name("scorecard.py"), mutants=False))
diff --git a/tools/audit/seat/sweep_render.py b/tools/audit/seat/sweep_render.py
index 79ebcfdc99..461c49b6d6 100644
--- a/tools/audit/seat/sweep_render.py
+++ b/tools/audit/seat/sweep_render.py
@@ -91,7 +91,7 @@ DEFAULTS = {
 #: Placeholders the overlay may omit or leave empty; each renders as the pulse.py
 #: flag given, repeated once per entry, or as nothing when there is none.
 OPTIONAL_FLAGS = {"seat_alives": "--seat-alive", "launch_ledger": "--launch-ledger",
-                  "plan_coordinator_cap": "--coordinator-cap"}
+                  "plan_coordinator_cap": "--coordinator-cap", "sweep_record": "--sweep-record"}
 ENTRY = re.compile(r"^[a-z]+=\S+$")
 
 
@@ -249,10 +249,13 @@ def self_test() -> int:
           re.findall(r"--seat-alive (\S+)", render(tracked, dict(full, seat_alives=["tick=/a", "merge=/b"])))
           == ["tick=/a", "merge=/b"])
     none = {k: v for k, v in full.items() if k not in OPTIONAL_FLAGS}
-    bare, empty = render(tracked, none), render(tracked, dict(full, seat_alives="", launch_ledger="", plan_coordinator_cap=""))
+    bare, empty = render(tracked, none), render(tracked, dict(full, seat_alives="", launch_ledger="", plan_coordinator_cap="", sweep_record=""))
     check("null control: an overlay with no seat_alives renders step (1b) without the flag and does not fail",
           "--seat-alive" not in bare and "--launch-ledger" not in bare and bare == empty
           and "  " not in "".join(l for l in bare.splitlines() if "pulse.py --repo" in l))
+    check("sweep_record renders as one --sweep-record FILE, and none leaves the flag out (null control)",
+          re.findall(r"--sweep-record ([^\s`]+)", render(tracked, dict(full, sweep_record="/rec.json"))) == ["/rec.json"]
+          and "--sweep-record" not in bare)
     check("launch_ledger renders as one --launch-ledger FILE",
           re.findall(r"--launch-ledger ([^\s`]+)", render(tracked, dict(full, launch_ledger="/led"))) == ["/led"])
     check("a seat_alives entry that is not SEAT=FILE is refused",
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index bd38a67a0d..745520fa33 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -51,6 +51,7 @@ rendered text that no overlay value supplied.
 | `gantt_roster` | the roster the beat's `gantt` row reads, as `<branch>:<path>` (fetched to `refs/gantt/roster`, never a local branch) |
 | `gantt_acks` | the Gantt acks file `sweep_gantt.py --acks` reads, one `<ISO> <KEY> act\|defer\|accept [until=<ISO>] <reason>` line per answered slip |
 | `fire_ledger` | the session's fire ledger, one line per seat fired with its leading UTC stamp, which the `gantt` and `verdict-audit` rows hand on as `--fired` (a line within 12 h holds the pull request or topic it names) |
+| `sweep_record` | optional: the day's sweep record file, rendered `scorecard.py --sweep-record FILE`; whose `recycle` lines of the standing dispatch and triage seats the `scorecard` row counts as K (absent: K prints unread) |
 | `train_glob` | the glob of live train logs `verdict_audit.py --train-glob` reads (a log modified within 3 h holds its queued pull requests) |
 | `train_log` | the live merge train's `train.log` (`$HOME/.local/state/hpo/merge_train/train.log`), which the beat's `bottleneck` and `plan-beat` rows hand on as `--train-log` (the skip-share alert and the plan page's train-skips table) |
 | `unheld_skip` | the skip file `verdict_audit.py --skip` reads, one `#<N> <ruling>` line per pull request held by an owner ruling |
@@ -70,7 +71,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #3394 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), and the finished seat's worktrees under {{seat_root}} and its scratch removed.
 
-(4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01).
+(4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.
 
 (4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.
 
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 0887612435..b4cb9f9fa8 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -273,6 +273,25 @@
    "index": false,
    "objects": false
   },
+  "scorecard": {
+   "run_sha": "3215c0b1f85e68b18dde7d804fdeca68363603e0bf8bb708323038e2801941ac",
+   "files": [
+    "tools/audit/seat/scorecard.py",
+    "tools/audit/seat/scorecard_selftest.py"
+   ],
+   "probes": [
+    ".",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat"
+   ],
+   "dirs": [
+    "tools/audit/seat"
+   ],
+   "index": false,
+   "objects": false,
+   "git": []
+  },
   "budget-raise-gate": {
    "run_sha": "8e2afa7d1084b7223a39f0ef593e419b78e3a724781a06ccb99196801427962a",
    "files": [

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
