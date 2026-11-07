# Review packet #3264
head: 0542969c33313f54db611ca0609fade7c1b14989
base: a37c58e5f32123b4028e90983799dc2aa81816f8

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128434587326 success
arch-score / arch-score id=128470407015 success
arm id=128434178160 skipped
budget-raise-gate / budget-raise-gate id=128470419377 success
cancel-superseded id=128470409993 success
codeql id=128470379451 skipped
codeql / Analyze (actions) id=128470413104 success
codeql / Analyze (javascript-typescript) id=128470408297 success
codeql / Analyze (python) id=128470399376 success
gate id=128470378677 success
governance id=128470379177 skipped
governance / delivery-status id=128470375164 success
governance / delivery-status-publish id=128470405015 skipped
governance / env-matrix id=128470399878 success
governance / instrument-self-tests id=128470375026 success
governance / policy-docs id=128470399403 success
governance / record id=128470375204 skipped
governance / wave-script id=128470406722 success
hassfest id=128470401902 skipped
hassfest / hassfest id=128470404076 success
kernel-points id=128470415813 skipped
pr-contract id=128470379686 skipped
pr-contract / pr-contract id=128470376626 failure
prelude id=128470411168 success
refresh id=128470378878 success
tests id=128470379468 skipped
tests / arch-instrument id=128470375769 success
tests / briefs id=128470375181 success
tests / browser id=128470375757 success
tests / ci-ratchet id=128470375966 skipped
tests / claims-autofix id=128470375876 skipped
tests / closure-scope id=128470407367 success
tests / closures id=128470375711 success
tests / closures-autofix id=128470375887 skipped
tests / coverage id=128470375638 success
tests / coverage-ratchet id=128470375753 success
tests / fast (3.14) id=128470375734 success
tests / graders-head-copy id=128470376105 success
tests / lane-proofs id=128470375832 success
tests / mutation id=128470403146 success
tests / mutation-autofix id=128470375288 skipped
tests / mutation-pins id=128470375154 skipped
tests / nightly-ha id=128470375998 skipped
tests / nightly-status id=128470374844 failure
tests / replay id=128470375874 skipped
tests / typing id=128470375474 success
validate id=128470403163 skipped
validate / validate-hacs id=128470375285 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 759ec575e..39dc1d6d5 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -756,6 +756,13 @@ jobs:
           python3 -I tools/audit/seat/plan_table.py --self-test | tee "$RUNNER_TEMP/plan-table-self-test.txt"
           grep -Eq '^plan_table self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/plan-table-self-test.txt"
 
+      - name: Show the gantt drift reader refusing its own fixtures
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          python3 -I tools/audit/seat/gantt_drift.py --self-test | tee "$RUNNER_TEMP/gantt-drift-self-test.txt"
+          grep -Eq '^gantt_drift self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/gantt-drift-self-test.txt"
+
       - name: Show the plan page refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
diff --git a/dev/programme/delivery/3264.md b/dev/programme/delivery/3264.md
new file mode 100644
index 000000000..64acb7f99
--- /dev/null
+++ b/dev/programme/delivery/3264.md
@@ -0,0 +1 @@
+- [#3264](https://github.com/tvofi/heatpump_optimizer/pull/3264) — **open**, R10-FLOW-TOOLKIT-MODEL: plan-model correctness in tools/plan/replan.py and the Gantt-drift instrument (R10-FLOW-TOOLKIT-MODEL)
diff --git a/tests/closures.json b/tests/closures.json
index 828aa5824..24ed802bf 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3869,6 +3869,7 @@
    "tools/audit/seat/daemonize.py",
    "tools/audit/seat/features_block.py",
    "tools/audit/seat/flow_metrics.py",
+   "tools/audit/seat/gantt_drift.py",
    "tools/audit/seat/gh_calls.py",
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 57fcb0697..6bee73a3a 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -65,6 +65,7 @@ sweep's standing-seat liveness step keep them alive.
 - [`delivery_row.sh`](instruments/delivery_row.sh.md) — the one seat-script writer of a PR's own `**open**` row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
 - [`failure_logs.sh`](instruments/failure_logs.sh.md) — answers why a PR's newest red at its live head is red
 - [`flow_metrics.py`](instruments/flow_metrics.py.md) — a round's flow over one window
+- [`gantt_drift.py`](instruments/gantt_drift.py.md) — compares the replanned gantt with the real state and prints one `GANTT-SLIP` line per unacknowledged IDLE, LATE or CLOSURE slip
 - [`gh_read.py`](instruments/gh_read.py.md) — the read rule every seat instrument's GitHub READS are under
 - [`handoff_push.sh`](instruments/handoff_push.sh.md) — the legacy one-shot
 - [`handover_prompt.py`](instruments/handover_prompt.py.md) — generates the next-session prompt from the roster (and optionally a resume doc)
diff --git a/tools/audit/seat/gantt_drift.py b/tools/audit/seat/gantt_drift.py
new file mode 100644
index 000000000..dcfe9e9e3
--- /dev/null
+++ b/tools/audit/seat/gantt_drift.py
@@ -0,0 +1,284 @@
+#!/usr/bin/env python3
+"""Compare the plan's gantt against the real state; print one GANTT-SLIP line per slip.
+
+    python3 -I tools/audit/seat/gantt_drift.py --plan plan.json --baseline base.json \
+        --acks acks.json --roster roster.json --prs prs.json --refs refs.txt \
+        --fired fired.txt --now 2026-11-01T18:00:00Z [--out new-baseline.json]
+    python3 -I tools/audit/seat/gantt_drift.py --self-test
+
+Every input is a command-line argument; no host path is read.
+
+SLIPS (stdout, `GANTT-SLIP <KIND> <subject> ...`, critical-path IDLE first):
+  IDLE     a not-done group the plan starts by now+grace that no open PR head,
+           handoff ref or FIRED ledger line names (tagged CP on the critical path)
+  LATE     a group whose planned finish moved past the baseline's by > --late-hours
+  CLOSURE  the plan's closure moved past the baseline's by > --closure-hours
+
+INPUTS. plan.json is replan.py's output (groups{g:{start,finish,done}},
+summary.closure, critical_path). baseline.json is {"closure": iso, "finish":
+{group: iso}}; absent LATE/CLOSURE entries are not graded. acks.json is a list
+of {"key": "IDLE:<g>"|"LATE:<g>"|"CLOSURE", "kind": "act"|"defer"|"accept",
+"until": iso}. act and defer silence the key while now < until (no until: for
+good). accept silences the key and re-baselines it into --out (printed as
+GANTT-BASELINE). roster.json supplies each group's resume.branch; prs.json is a
+list with headRefName; refs.txt is a saved `git ls-remote` listing; fired.txt is
+the dispatch ledger, of which only FIRED lines count.
+"""
+from __future__ import annotations
+
+import argparse
+import contextlib
+import datetime as dt
+import io
+import json
+import re
+import sys
+
+FMT = "%Y-%m-%dT%H:%M:%SZ"
+
+
+def ts(s: str) -> dt.datetime:
+    return dt.datetime.strptime(s, FMT)
+
+
+def names_of(group: str, roster: dict) -> list:
+    out = [group.lower()]
+    for g in roster.get("groups", []):
+        b = (g.get("resume") or {}).get("branch")
+        if g.get("group") == group and b:
+            out.append(b.lower())
+    return out
+
+
+def is_named(group: str, roster: dict, prs: list, refs: str, fired: str) -> bool:
+    hay = "\n".join([p.get("headRefName", "") for p in prs] + [refs] +
+                    [l for l in fired.splitlines() if "FIRED" in l]).lower()
+    return any(re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", hay) for n in names_of(group, roster))
+
+
+def detect(plan, base, roster, prs, refs, fired, now, grace_min, late_h, closure_h):
+    """[(key, kind, line)], critical-path IDLE first."""
+    now_t = ts(now)
+    horizon = now_t + dt.timedelta(minutes=grace_min)
+    cp = plan.get("critical_path") or []
+    idle, rest = [], []
+    for g, v in sorted(plan["groups"].items()):
+        if v.get("done") or not v.get("start"):
+            continue
+        if ts(v["start"]) <= horizon and not is_named(g, roster, prs, refs, fired):
+            tag = " CP" if g in cp else ""
+            row = (f"IDLE:{g}", "IDLE", f"GANTT-SLIP IDLE{tag} {g} start={v['start']}")
+            (idle if tag else rest).append(row)
+        old = (base.get("finish") or {}).get(g)
+        if old and v.get("finish"):
+            d = (ts(v["finish"]) - ts(old)).total_seconds()
+            if d > late_h * 3600:
+                rest.append((f"LATE:{g}", "LATE", f"GANTT-SLIP LATE {g} finish={v['finish']} baseline={old} moved_h={d / 3600:.1f}"))
+    c_old, c_new = base.get("closure"), plan["summary"].get("closure")
+    if c_old and c_new:
+        d = (ts(c_new) - ts(c_old)).total_seconds()
+        if d > closure_h * 3600:
+            rest.append(("CLOSURE", "CLOSURE", f"GANTT-SLIP CLOSURE closure={c_new} baseline={c_old} moved_h={d / 3600:.1f}"))
+    return idle + rest
+
+
+def apply_acks(slips, acks, base, plan, now):
+    """(unsilenced lines, new baseline, GANTT-BASELINE lines)."""
+    now_t = ts(now)
+    new = json.loads(json.dumps(base))
+    lines, notes = [], []
+    for key, kind, line in slips:
+        silenced = False
+        for a in acks:
+            if a.get("key") != key:
+                continue
+            if a.get("kind") == "accept":
+                silenced = True
+                if kind == "LATE":
+                    g = key.split(":", 1)[1]
+                    new.setdefault("finish", {})[g] = plan["groups"][g]["finish"]
+                    notes.append(f"GANTT-BASELINE {key} finish={plan['groups'][g]['finish']}")
+                elif kind == "CLOSURE":
+                    new["closure"] = plan["summary"]["closure"]
+                    notes.append(f"GANTT-BASELINE {key} closure={plan['summary']['closure']}")
+            elif a.get("kind") in ("act", "defer"):
+                if not a.get("until") or now_t < ts(a["until"]):
+                    silenced = True
+        if not silenced:
+            lines.append(line)
+    return lines, new, notes
+
+
+def run(a) -> int:
+    load = lambda p: json.load(open(p, encoding="utf-8"))
+    text = lambda p: open(p, encoding="utf-8").read()
+    plan, base, acks = load(a.plan), load(a.baseline), load(a.acks)
+    slips = detect(plan, base, load(a.roster), load(a.prs), text(a.refs), text(a.fired),
+                   a.now, a.grace_min, a.late_hours, a.closure_hours)
+    lines, new, notes = apply_acks(slips, acks, base, plan, a.now)
+    for l in lines + notes:
+        print(l)
+    if a.out:
+        with open(a.out, "w", encoding="utf-8") as fh:
+            json.dump(new, fh, indent=1, sort_keys=True)
+    return 0
+
+
+# ------------------------------------------------------------------ self-test
+
+NOW = "2026-11-01T18:00:00Z"
+
+
+def fixture():
+    g = lambda s, f, done=False: {"start": s, "finish": f, "done": done, "slot": 0}
+    plan = {"groups": {
+        "CPG": g("2026-11-01T17:00:00Z", "2026-11-02T00:00:00Z"),     # critical, unnamed
+        "EDGE": g("2026-11-01T19:00:00Z", "2026-11-02T01:00:00Z"),    # starts exactly at now+grace
+        "FARG": g("2026-11-01T19:00:01Z", "2026-11-02T01:00:00Z"),    # starts after the horizon
+        "PRG": g("2026-11-01T17:00:00Z", "2026-11-02T01:00:00Z"),     # named by an open PR
+        "REFG": g("2026-11-01T17:00:00Z", "2026-11-02T01:00:00Z"),    # named by a handoff ref
+        "FIRG": g("2026-11-01T17:00:00Z", "2026-11-02T01:00:00Z"),    # named by a FIRED line
+        "DONEG": g("2026-11-01T10:00:00Z", "2026-11-01T11:00:00Z", True),
+        "LATEG": g("2026-11-01T20:00:00Z", "2026-11-02T10:00:01Z"),   # moved 6h + 1s
+        "NEARG": g("2026-11-01T20:00:00Z", "2026-11-02T10:00:00Z"),   # moved exactly 6h: not late
+        "EARLYG": g("2026-11-01T20:00:00Z", "2026-11-02T01:00:00Z"),  # moved 9h earlier: not late
+    }, "critical_path": ["CPG"], "summary": {"closure": "2026-11-05T12:00:01Z"}}
+    base = {"closure": "2026-11-05T10:00:00Z", "finish": {
+        "LATEG": "2026-11-02T04:00:00Z", "NEARG": "2026-11-02T04:00:00Z",
+        "EARLYG": "2026-11-02T10:00:00Z"}}
+    roster = {"groups": [{"group": "REFG", "resume": {"branch": "handoff/refg-x"}}]}
+    prs = [{"headRefName": "fix/prg"}]
+    refs = "abc\trefs/heads/handoff/refg-x\n"
+    fired = "2026-11-01T17:30Z FIRED fixer for firg\nnot a match: edge FIRE-OWED\n"
+    return plan, base, roster, prs, refs, fired
+
+
+def _conf(mod):
+    """Run the checks against module namespace `mod`; return (checks, failed names)."""
+    n, bad = [0], []
+
+    def check(name, cond):
+        n[0] += 1
+        if not cond:
+            bad.append(name)
+            print(f"  FAIL {name}")
+
+    plan, base, roster, prs, refs, fired = fixture()
+    sl = mod["detect"](plan, base, roster, prs, refs, fired, NOW, 60, 6, 2)
+    keys = [k for k, _, _ in sl]
+    check("IDLE critical-path group is tagged CP", any(k == "IDLE:CPG" and "IDLE CP " in l for k, _, l in sl))
+    check("critical-path IDLE is listed first", keys and keys[0] == "IDLE:CPG")
+    check("IDLE at exactly now+grace is reported", "IDLE:EDGE" in keys)
+    check("null: a start past now+grace is not IDLE", "IDLE:FARG" not in keys)
+    check("null: an open PR head silences IDLE", "IDLE:PRG" not in keys)
+    check("null: a handoff ref silences IDLE", "IDLE:REFG" not in keys)
+    check("null: a FIRED line silences IDLE", "IDLE:FIRG" not in keys)
+    check("null: a non-FIRED ledger line does not silence IDLE", "IDLE:EDGE" in keys)
+    check("null: a done group is not IDLE", "IDLE:DONEG" not in keys)
+    check("LATE past the threshold", "LATE:LATEG" in keys)
+    check("null: a finish inside the threshold is not LATE", "LATE:NEARG" not in keys)
+    check("null: a finish moved earlier is not LATE", "LATE:EARLYG" not in keys)
+    check("CLOSURE past the threshold", "CLOSURE" in keys)
+    plan["summary"]["closure"] = "2026-11-05T12:00:00Z"
+    check("null: closure inside the threshold is not CLOSURE",
+          "CLOSURE" not in [k for k, _, _ in mod["detect"](plan, base, roster, prs, refs, fired, NOW, 60, 6, 2)])
+    plan["summary"]["closure"] = "2026-11-05T12:00:01Z"
+
+    ap = mod["apply_acks"]
+    out, nb, notes = ap(sl, [], base, plan, NOW)
+    check("no acks: every slip is printed", len(out) == len(sl) and not notes and nb == base)
+    for kind in ("act", "defer"):
+        acks = [{"key": "IDLE:CPG", "kind": kind, "until": "2026-11-01T19:00:00Z"}]
+        out, _, _ = ap(sl, acks, base, plan, NOW)
+        check(f"{kind} silences its key before until", not any("IDLE CP CPG" in l for l in out) and len(out) == len(sl) - 1)
+        out, _, _ = ap(sl, acks, base, plan, "2026-11-01T19:00:00Z")
+        check(f"{kind} lapses at until", any("IDLE CP CPG" in l for l in out))
+    out, _, _ = ap(sl, [{"key": "IDLE:CPG", "kind": "act"}], base, plan, NOW)
+    check("act without until silences for good", len(out) == len(sl) - 1)
+    out, _, _ = ap(sl, [{"key": "LATE:NOPE", "kind": "act"}], base, plan, NOW)
+    check("null: an ack for another key silences nothing", len(out) == len(sl))
+    acks = [{"key": "LATE:LATEG", "kind": "accept"}, {"key": "CLOSURE", "kind": "accept"},
+            {"key": "IDLE:EDGE", "kind": "accept"}]
+    out, nb, notes = ap(sl, acks, base, plan, NOW)
+    check("accept silences its key", not any(" LATE LATEG" in l or "CLOSURE closure" in l or "IDLE EDGE" in l for l in out))
+    check("accept re-baselines LATE", nb["finish"]["LATEG"] == "2026-11-02T10:00:01Z")
+    check("accept re-baselines CLOSURE", nb["closure"] == "2026-11-05T12:00:01Z")
+    check("accept leaves other baselines alone", nb["finish"]["NEARG"] == base["finish"]["NEARG"])
+    check("accept prints GANTT-BASELINE lines", len(notes) == 2 and all(x.startswith("GANTT-BASELINE") for x in notes))
+    check("accept does not mutate the input baseline", base["closure"] == "2026-11-05T10:00:00Z")
+    isn = mod["is_named"]
+    check("a longer group's branch does not silence the shorter name (word boundary)",
+          not isn("PRG", roster, [{"headRefName": "fix/prg-extra"}], "", ""))
+    check("null: the exact topic branch names the group",
+          isn("PRG", roster, [{"headRefName": "fix/prg"}], "", ""))
+    return n[0], bad
+
+
+# One textual edit per arm; each `old` occurs exactly once in this file.
+MUTANTS = [
+    ("idle-horizon", "if ts(v[\"start\"]) <= horizon and", "if ts(v[\"start\"]) < horizon and"),
+    ("idle-prs", "[p.get(\"headRefName\", \"\") for p in prs]", "[]"),
+    ("idle-refs", "+ [refs] +", "+ [] +"),
+    ("idle-fired", "[l for l in fired.splitlines() if \"FIRED\" in l]", "[l for l in fired.splitlines()]"),
+    ("word-boundary", 'rf"(?<![\\w-]){re.escape(n)}(?![\\w-])"', "re.escape(n)"),
+    ("idle-cp-first", "return idle + rest", "return rest + idle"),
+    ("idle-cp-tag", "tag = \" CP\" if g in cp else \"\"", "tag = \"\""),
+    ("late-threshold", "if d > late_h * 3600:", "if d >= late_h * 3600:"),
+    ("late-direction", "if d > late_h * 3600:", "if abs(d) > late_h * 3600:"),
+    ("closure-threshold", "if d > closure_h * 3600:", "if d >= closure_h * 3600:"),
+    ("ack-until", "now_t < ts(a[\"until\"])", "now_t <= ts(a[\"until\"])"),
+    ("ack-defer", "elif a.get(\"kind\") in (\"act\", \"defer\"):", "elif a.get(\"kind\") in (\"act\",):"),
+    ("ack-key", "if a.get(\"key\") != key:", "if False:"),
+    ("accept-late", "new.setdefault(\"finish\", {})[g] = plan[\"groups\"][g][\"finish\"]", "pass"),
+    ("accept-closure", "new[\"closure\"] = plan[\"summary\"][\"closure\"]", "pass"),
+    ("accept-silence", "silenced = True\n                if kind == \"LATE\":", "if kind == \"LATE\":"),
+]
+
+
+def self_test() -> int:
+    # Mutate the text above MUTANTS only: the list itself quotes every `old`.
+    src = open(__file__, encoding="utf-8").read().split("# One textual edit", 1)[0]
+    total, failed = _conf(globals())
+    print(f"  base: {total} checks")
+    for name, old, new in MUTANTS:
+        if src.count(old) != 1:
+            total += 1
+            failed.append(f"mutant {name}: old text occurs {src.count(old)} times")
+            print(f"  FAIL mutant {name} is not applicable")
+            continue
+        ns = {"__name__": "gantt_mutant", "__file__": __file__}
+        exec(compile(src.replace(old, new), f"<mutant {name}>", "exec"), ns)
+        total += 1
+        with contextlib.redirect_stdout(io.StringIO()):
+            try:
+                _, bad = _conf(ns)
+            except Exception:  # a crash kills the mutant too
+                bad = ["crash"]
+        if bad:
+            print(f"  ok   mutant {name} killed")
+        else:
+            failed.append(f"mutant {name} survived")
+            print(f"  FAIL mutant {name} survived")
+    print(f"gantt_drift self-test: {total} checks, {len(failed)} failed")
+    return 1 if failed else 0
+
+
+def main(argv) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    ap.add_argument("--self-test", action="store_true")
+    for f in ("plan", "baseline", "acks", "roster", "prs", "refs", "fired", "now", "out"):
+        ap.add_argument(f"--{f}")
+    ap.add_argument("--grace-min", type=int, default=60)
+    ap.add_argument("--late-hours", type=float, default=6)
+    ap.add_argument("--closure-hours", type=float, default=2)
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    miss = [f for f in ("plan", "baseline", "acks", "roster", "prs", "refs", "fired", "now") if not getattr(a, f)]
+    if miss:
+        ap.error("required: " + ", ".join("--" + m for m in miss))
+    return run(a)
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/instruments/gantt_drift.py.md b/tools/audit/seat/instruments/gantt_drift.py.md
new file mode 100644
index 000000000..e77d56808
--- /dev/null
+++ b/tools/audit/seat/instruments/gantt_drift.py.md
@@ -0,0 +1,13 @@
+# `gantt_drift.py`
+
+- `gantt_drift.py` — compares the plan JSON `tools/plan/replan.py` writes with
+  the real state (open PR heads, handoff refs, the dispatch ledger's FIRED
+  lines) and a baseline, and prints one `GANTT-SLIP` line per unacknowledged
+  slip: IDLE (a group the plan has started that nothing names; `CP` on the
+  critical path, listed first), LATE (a planned finish moved past the
+  baseline's by more than `--late-hours`), CLOSURE (the plan closure moved by
+  more than `--closure-hours`). Acks are act, defer (silence a key until a
+  time) or accept (silence it and re-baseline it into `--out`). When: after
+  each replan and plan page render. Refusal: none; a slip is surfaced for the
+  owner to act on, defer or accept. `--self-test` runs each slip kind and ack
+  kind with its null, and a mutant per arm.
diff --git a/tools/audit/seat/plan_page.py b/tools/audit/seat/plan_page.py
index a40231521..50b3ebeb4 100644
--- a/tools/audit/seat/plan_page.py
+++ b/tools/audit/seat/plan_page.py
@@ -260,6 +260,8 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
             "crit": g in crit, "wave": None if g in done else pg["wave"],
             "start": None if g in done else pg["start"],
             "finish": None if g in done else pg["finish"]})
+        if pg.get("done"):  # the plan counts it done (absorbed): nothing to draw
+            rows[-1].update(wave=None, start=None, finish=None)
     rows.sort(key=lambda r: (r["st"] != "done", r["finish"] or "", r["g"]))
     return rows
 
@@ -273,7 +275,9 @@ def swimlanes(plan: dict, rows: list) -> tuple[str, int]:
     now = _t(plan["generated"]["start"])
     # The axis runs to the last planned stamp: the round-close stamp lands
     # after closure, and an axis ending at closure would not draw it.
-    end = max([_t(plan["summary"]["closure"])] + [_t(s["at"]) for s in plan["stamps"]])
+    end = max([_t(plan["summary"]["closure"])] + [_t(s["at"]) for s in plan["stamps"]]
+              + [_t(plan["summary"]["post_closure_finish"])
+                 for _ in [0] if plan["summary"].get("post_closure_finish")])
     slots = plan["generated"]["caps"]["slots"]
     span_h = max(1.0, (end - now).total_seconds() / 3600)
     W, LW, RH = 1180, 120, 24
@@ -551,7 +555,12 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict) -> str:
             f"{inherited} inherited in-progress coordinator groups are recorded in "
             f"plan.json. The line above the lanes is how many groups are in flight at "
             f"each hour, riding the cap. Stamps: one patch per {every} production groups, "
-            f"the round's major at closure. Hover any bar, however narrow, for its name, state, "
+            f"the round's major at closure. {summ.get('production_since_tag', 0)} production "
+            f"groups already merged since the last tag count toward the next patch stamp"
+            + (f"; {len(summ['post_closure'])} post-closure group(s) run after the "
+               f"round-close stamp, in no stamp: {', '.join(map(short, summ['post_closure']))}"
+               if summ.get("post_closure") else "")
+            + f". Hover any bar, however narrow, for its name, state, "
             f"start, ETA and wave. {drawn} of {max(0, len(chain) - 1)} critical-path links "
             f"are drawn; the ◆ and the caption carry the rest."),
         "sizes": e(sizes),
@@ -853,7 +862,8 @@ def _self_test() -> int:
                   and rows["R9-HELD"]["tier"] is None
                   and 'data-name="HELD"' not in page)
             check("every open group has a bar; no done group does",
-                  all(f'data-name="{short(g)}"' in page for g in rows if scheduled(g))
+                  all(f'data-name="{short(g)}"' in page for g in rows
+                      if rows[g]["st"] != "done" and scheduled(g))
                   and 'data-name="DONE-SHA"' not in page)
             check("critical-path groups carry the mark",
                   all(rows[g]["crit"] for g in plan["critical_path"])
@@ -872,7 +882,8 @@ def _self_test() -> int:
                   {g: rows[g]["tier"] for g in rows})
             check("each open group's ETA cell names why it starts when it does",
                   all(f'title="{html.escape(rows[g]["why"])}"' in page and plan["groups"][g]["start_reason"]
-                      in rows[g]["why"] for g in rows if scheduled(g)),
+                      in rows[g]["why"] for g in rows
+                      if rows[g]["st"] != "done" and scheduled(g)),
                   {g: rows[g]["why"] for g in rows})
             check("a planned stamp is drawn", 'class="stampline"' in page)
             check("the closure stamp renders as the round's major, kind round-close",
diff --git a/tools/plan/durations.json b/tools/plan/durations.json
index ebbe423e1..2ce69631e 100644
--- a/tools/plan/durations.json
+++ b/tools/plan/durations.json
@@ -178,6 +178,7 @@
    "open": 4
   }
  },
+ "inflow_groups_per_hour": 0.4,
  "live_remaining_fraction": 0.7,
  "live_remaining_fraction_note": "0.7: the share of a size duration still ahead for a group whose fixer is already working. A working estimate carried from the out-of-tree renderer; no measurement supports a different fraction.",
  "provenance": {
diff --git a/tools/plan/replan.py b/tools/plan/replan.py
index 0b9698882..b2da9a9d0 100644
--- a/tools/plan/replan.py
+++ b/tools/plan/replan.py
@@ -89,6 +89,7 @@ import datetime as dt
 import json
 import math
 import os
+import re
 import subprocess
 import sys
 from pathlib import Path
@@ -122,7 +123,7 @@ DEFAULT_CAPS = {
     "slots": 16,             # open pull requests: the owner's cap since 2026-10-31
     "seats": 16,             # fixers working: one per open pull request
     "coordinator_cap": 2,    # open pull requests touching coordinator.py
-    "stamp_every": 5,        # production groups per patch stamp
+    "stamp_every": 3,        # production groups per patch stamp (tvofi 2026-10-26)
 }
 #: Where DEFAULT_CAPS' slots and seats come from, recorded in every plan that
 #: uses them: a plan drawn at a cap nobody chose must say whose cap it is.
@@ -200,10 +201,54 @@ def groups_of(roster: dict) -> dict:
     return {g["group"]: g for g in roster.get("groups", [])}
 
 
+#: A group in a closed stage (`roster_lib.CLOSED_STAGES`, `absorbed` included:
+#: R10-FLOW-TOOLKIT-MODEL carry 2) is not scheduled as open work; its remaining
+#: work lives in the group its resume note names.
+ABSORBED_RE = re.compile(r"absorbed into ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)")
+
+#: The group that cuts the round's closing stamp; a group after it is post-closure.
+CLOSE_STAMP_MARK = "STAMP-ROUND-MAJOR"
+POST_CLOSE_STEP_RE = re.compile(r"after the .*\b(stamp|closeout)\b", re.I)
+
+
 def is_done(group: dict) -> bool:
     return not roster_lib.is_open(group)
 
 
+def absorbers(G: dict) -> dict:
+    """{absorbed group: (absorber or None, advisory or None)}: the group the
+    resume note names ("absorbed into <G>"), and an advisory -- never a
+    refusal -- for a note that names no group in the roster."""
+    out = {}
+    for n in sorted(G):
+        res = G[n].get("resume") or {}
+        if res.get("stage") != "absorbed":
+            continue
+        m = ABSORBED_RE.search(" ".join(str(res.get(k) or "") for k in ("note", "next_step")))
+        into = m.group(1) if m and m.group(1) in G else None
+        out[n] = (into, None if into else
+                  f"ADVISORY: {n} is absorbed but its resume note names no existing group")
+    return out
+
+
+def post_closure_groups(G: dict, open_: set) -> set:
+    """Open groups that run after the round's closing stamp: an owner-step
+    whose next step is "after the ... stamp", a group whose `after` names the
+    closing-stamp group, and every group after one of those."""
+    post = {n for n in open_
+            if (G[n].get("kind") == "owner-step"
+                and POST_CLOSE_STEP_RE.search(str((G[n].get("resume") or {}).get("next_step") or "")))
+            or any(CLOSE_STAMP_MARK in a for a in G[n].get("after") or [])}
+    grew = True
+    while grew:
+        grew = False
+        for n in open_ - post:
+            if any(a in post for a in G[n].get("after") or []):
+                post.add(n)
+                grew = True
+    return post
+
+
 def roster_lane(group: dict) -> str:
     """The lane a group is drawn in and counted under for the stamp cadence.
 
@@ -571,9 +616,18 @@ def selftest_model() -> int:
            {n: G[n]["start"] for n in G})
     expect("a started group says why it starts: its fixer is working",
            G["L0"]["start_reason"] == "started: its fixer is working", G["L0"]["start_reason"])
-    expect("a planned group waits while started groups fill the cap, and names it",
-           G["NEW"]["start"] > iso(start, 0) and G["NEW"]["start_reason"].startswith("slot cap 2"),
+    # NEW heads DEP's chain, so it is on the critical path: it starts at once
+    # on an overflow slot, exempt from the cap (carry 8). A group off the path
+    # still waits (the null control below).
+    expect("a critical-path group starts past a full cap, flagged exempt",
+           G["NEW"]["start"] == iso(start, 0) and G["NEW"].get("exempt") is True,
            G["NEW"])
+    off = {"groups": many["groups"] + [grp("OFF")]}
+    poff = build_plan(off, M, caps1, start, "v1.0.0", round_n=2)
+    expect("null: a non-critical group in the same position still waits, and names it",
+           poff["groups"]["OFF"]["start"] > iso(start, 0)
+           and poff["groups"]["OFF"]["start_reason"].startswith("slot cap 2"),
+           poff["groups"]["OFF"])
     expect("a started group waits only for its unmerged after-group, and names it",
            G["DEP"]["start"] == G["NEW"]["finish"]
            and G["DEP"]["start_reason"].startswith("started: its fixer is working; after NEW"),
@@ -582,6 +636,7 @@ def selftest_model() -> int:
            check_plan(pm))
     bad = json.loads(json.dumps(pm))
     bad["groups"]["NEW"]["start"] = iso(start, 0)
+    bad["groups"]["NEW"].pop("exempt", None)
     expect("a PLANNED dispatch into a full cap is still refused",
            any(b.startswith("in flight: NEW dispatched") for b in check_plan(bad)),
            check_plan(bad))
@@ -652,14 +707,126 @@ def selftest_model() -> int:
 
 # ------------------------------------------------------------------- schedule
 
+WORK_REF_PREFIXES = ("fixer/", "handoff/", "handoff-wip/", "dispatch/")
+DESIGN_REF_PREFIX = "design/"
+
+
+def parse_live_refs(text: str) -> set:
+    """Branch names from a saved `git ls-remote` listing (sha, tab, ref)."""
+    out = set()
+    for line in text.splitlines():
+        ref = line.split()[-1] if line.split() else ""
+        if ref.startswith("refs/heads/"):
+            out.add(ref[len("refs/heads/"):])
+    return out
+
+
+def topics_of(group: dict) -> set:
+    t = {group["group"].lower()}
+    branch = (group.get("resume") or {}).get("branch") or ""
+    if branch:
+        t.add(branch.rsplit("/", 1)[-1])
+    return t
+
+
+def topic_evidence(group: dict, evidence: dict) -> str | None:
+    """'pr' (an open pull request), 'work' (a fixer, handoff or dispatch ref),
+    'design' (a design ref and nothing built), or None, from the offline
+    listing and the in-flight file."""
+    topics = topics_of(group)
+    for pr in evidence.get("prs") or []:
+        head = str(pr.get("headRefName") or "")
+        if head.rsplit("/", 1)[-1] in topics:
+            return "pr"
+    refs = evidence.get("refs") or set()
+    if any(p + t in refs for p in WORK_REF_PREFIXES for t in topics):
+        return "work"
+    if any(DESIGN_REF_PREFIX + t in refs for t in topics):
+        return "design"
+    return None
+
+
+def substantive(diff: str) -> bool:
+    """True when a unified diff changes a line that is neither blank nor a
+    `#` comment: a comment-only or whitespace-only change ships no behaviour."""
+    for line in diff.splitlines():
+        if line[:1] in "+-" and not line.startswith(("+++", "---")):
+            body = line[1:].strip()
+            if body and not body.startswith("#"):
+                return True
+    return False
+
+
+MERGE_BRANCH_RE = re.compile(r"^Merge pull request #\d+ from \S+/(\S+)\s*$")
+
+
+def merge_topic(subject: str) -> str | None:
+    """The topic of a "Merge pull request #N from <owner>/<type>/<topic>"
+    subject: the last path segment of the merged branch, lower-cased."""
+    m = MERGE_BRANCH_RE.match(subject)
+    return m.group(1).rsplit("/", 1)[-1].lower() if m else None
+
+
+def production_groups_since(commits: list, G: dict) -> list:
+    """Production groups with a substantive `custom_components` change since
+    the last tag, once each however many pull requests they took.
+    `commits`: [{"subject": str, "diff": the change against the first parent
+    of custom_components}]. A group is named by a merge's topic branch, as
+    `topic_evidence` matches one (main's merges read "Merge pull request #N
+    from tvofi/fix/<topic>"; a part branch `<topic>-p2` extends its group's
+    topic at a `-` boundary), else by the longest roster group name in the
+    subject (a squash)."""
+    by_topic = {t: n for n in G for t in topics_of(G[n])}
+    out: dict = {}
+    for c in commits:
+        topic = merge_topic(c["subject"])
+        n = None
+        if topic:
+            # a part branch (`<topic>-p2`) belongs to the longest roster topic it
+            # equals or extends at a `-` boundary
+            hit = [t for t in by_topic if topic == t or topic.startswith(t + "-")]
+            n = by_topic[max(hit, key=len)] if hit else None
+        if n is None:
+            named = [g for g in G if g in c["subject"]]
+            n = max(named, key=len) if named else None
+        if n and roster_lane(G[n]) in PRODUCTION and substantive(c.get("diff") or ""):
+            out[n] = True
+    return list(out)
+
+
+def git_commits_since_tag(repo: str) -> list:
+    """The `production_groups_since` input from git: first-parent commits
+    since the last tag, each with its custom_components diff against its
+    FIRST PARENT (`git show` prints a merge's combined diff, empty for a
+    clean merge)."""
+    tag = _git(repo, "describe", "--tags", "--abbrev=0")
+    if tag.returncode != 0:
+        raise PlanError("--since-tag: the repository has no tag")
+    log = _git(repo, "log", "--first-parent", "--format=%H%x1f%s", f"{tag.stdout.strip()}..HEAD")
+    out = []
+    for line in log.stdout.splitlines():
+        sha, _, subject = line.partition("\x1f")
+        diff = _git(repo, "diff", "-U0", f"{sha}^1", sha, "--", "custom_components").stdout
+        out.append({"subject": subject, "diff": diff})
+    return out
+
+
 def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
                version: str, roster_ref: str = "", roster_blob: str = "",
-               roster_path: str = "", *, round_n: int) -> dict:
+               roster_path: str = "", *, round_n: int, since_tag: list | None = None,
+               evidence: dict | None = None) -> dict:
     closing, why = closure_version(version, round_n)
     if why:
         raise PlanError(f"the round-close stamp: {why}")
     G = groups_of(roster)
     deps, open_, done = dependency_graph(G)
+    # Groups after the round's closing stamp are scheduled after it and are
+    # neither inside closure nor in any stamp's carries (carries 10, 11).
+    post = post_closure_groups(G, open_)
+    open_all = open_
+    open_ = open_all - post
+    deps_post = {n: deps[n] for n in post}
+    deps = {n: deps[n] for n in open_}
     order = topo_order(deps)
     children = children_of(deps)
     size_hours = durations["sizes_hours"]
@@ -671,6 +838,24 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
     lane = {n: roster_lane(G[n]) for n in G}
     coord = {n: touches_coordinator(G[n]) for n in open_}
     live = {n for n in open_ if (G[n].get("resume") or {}).get("stage") in LIVE_STAGES}
+    design_only: set = set()
+    demoted: set = set()
+    if evidence is not None:
+        # Liveness by evidence, not by the stage word (carries 0, 3): an open
+        # pull request is live (credit); a design ref with no build starts at
+        # t=0 without credit; a stage-word live group with neither a work ref
+        # nor a pull request is pending. Offline: the listing is a saved file.
+        ev_live, ev_design = set(), set()
+        for n in open_:
+            if topic_evidence(G[n], evidence) == "pr":
+                ev_live.add(n)
+            elif topic_evidence(G[n], evidence) == "design":
+                ev_design.add(n)
+        demoted = {n for n in live if topic_evidence(G[n], evidence) is None}
+        # A stage-word live group whose only evidence is a design ref has
+        # built nothing: it is design-only, uncredited (carry 3).
+        live = (live - demoted - ev_design) | ev_live
+        design_only = ev_design - live
     dur_h, basis = {}, {}
     for n in open_:
         dur_h[n], basis[n] = group_hours(G[n], durations, n in live,
@@ -719,21 +904,30 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
     # but its record step -- already holds its pull request: it starts the
     # moment its `after` groups have merged, past the slot and coordinator
     # caps (which bind new dispatches), and is never queued behind them.
-    started = live | settled
+    started = live | settled | design_only
     released = {n: 0 for n in open_ if not deps[n]}   # n -> when it became ready
     coord_held: set = set()     # ready groups the coordinator cap passed over
     ready = {n for n in open_ if not deps[n]}
     pending = set(open_)
     batch_rows: list = []
     stamps: list = []
-    carry: list = []
+    # Production groups already merged since the last tag count toward the
+    # next patch stamp, once each however many pull requests they took.
+    # Only a DONE group is credit: one still open merges inside this plan and
+    # is counted there, so crediting it too would count it twice (carry 9).
+    credit = [n for n in dict.fromkeys(since_tag or [])
+              if n in G and lane[n] in PRODUCTION and n in done]
+    carry: list = list(credit)
     stamp_by_group: dict = {}
     patch = 0
+    overflow_base = slots + 100
+    exempt: set = set()         # critical-path groups started past the slots cap
 
     def free_slot() -> int | None:
         # A slot is held from the start to the merge, not to the end of the
         # work: a finished group waiting for its batch still has its PR open.
-        used = {s for s, _ in running.values()} | {slot_of[n] for n in finished}
+        used = ({s for s, _ in running.values()} | {slot_of[n] for n in finished})
+        used = {s for s in used if s < overflow_base}
         if len(used) >= slots:
             return None
         return next((s for s in range(slots) if s not in used), None)
@@ -741,7 +935,8 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
     def held_slot() -> int:
         # A started group's slot: the lowest free index, past the cap if the
         # started set alone exceeds it.
-        used = {s for s, _ in running.values()} | {slot_of[n] for n in finished}
+        used = ({s for s, _ in running.values()} | {slot_of[n] for n in finished})
+        used = {s for s in used if s < overflow_base}
         return next(s for s in range(len(used) + 1) if s not in used)
 
     def in_flight_coord() -> int:
@@ -782,6 +977,23 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
                 inherited.add(n)
             ready.discard(n)
             pending.discard(n)
+        # A ready critical-path group starts now whatever the slots cap, as
+        # dispatch does (orchestrator.md section 5); it takes a free slot when
+        # one exists and an overflow slot otherwise, and is exempt from the cap.
+        while True:
+            n = pick(sorted(x for x in ready if x in crit), t)
+            if n is None:
+                break
+            s = free_slot()
+            if s is None:
+                s = overflow_base + len(start_t)
+                exempt.add(n)
+            start_t[n] = t
+            slot_of[n] = s
+            work_end[n] = t + dur_min[n]
+            running[n] = (s, work_end[n])
+            ready.discard(n)
+            pending.discard(n)
         while ready and free_slot() is not None:
             n = pick(sorted(ready), t)
             if n is None:
@@ -829,15 +1041,15 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
             for n in sorted(batch):
                 if lane[n] in PRODUCTION:
                     carry.append(n)
-                    if len(carry) >= every:
+                    while len(carry) >= every:
                         patch += 1
                         v = bump(version, patch)
+                        cut, carry = carry[:every], carry[every:]
                         stamps.append({"version": v, "at": t + stamp_lead,
-                                       "carries": list(carry), "kind": "patch",
+                                       "carries": cut, "kind": "patch",
                                        "batch": bid})
-                        for c in carry:
+                        for c in cut:
                             stamp_by_group[c] = v
-                        carry = []
             for n in batch:
                 for c in children[n]:
                     # THE invariant that keeps a started group out of `ready`:
@@ -861,6 +1073,21 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
     stamps.append({"version": closing, "at": closure + closure_lead,
                    "carries": list(carry), "kind": ROUND_CLOSE, "batch": None})
 
+    # Post-closure groups (owner steps after the closing stamp, and what
+    # follows them) start once the stamp is cut and every dependency has
+    # finished; they hold no slot, join no batch and are in no stamp.
+    post_dur = {}
+    for n in post:
+        h, _ = group_hours(G[n], durations, False, roster_path or roster_ref or "<fixture>")
+        post_dur[n] = max(1, int(round(h * 60)))
+    post_start: dict = {}
+    post_end: dict = {}
+    for n in topo_order({n: [a for a in deps_post[n] if a in post] for n in post}):
+        ready_at = max([stamps[-1]["at"]] + [post_end[a] for a in deps_post[n] if a in post_end]
+                       + [merged_t[a] for a in deps_post[n] if a in merged_t])
+        post_start[n] = ready_at
+        post_end[n] = ready_at + post_dur[n]
+
     # a wave is the set of groups the replan dispatches at one instant
     by_open: dict = {}
     for n in open_:
@@ -880,6 +1107,7 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
             "groups": gs,
         })
 
+    inflow = float(durations.get("inflow_groups_per_hour") or 0)
     gate = gate_minutes(durations)
     # The published gate is rounded; the CI minutes are the product of the
     # published pair, so a reader who multiplies the summary's own numbers
@@ -908,7 +1136,21 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
         return [None if isinstance(k, float) and math.isinf(k) else k for k in key]
 
     groups_out = {}
+    absorbed_by = absorbers(G)
     for n in sorted(G):
+        if n in post:
+            groups_out[n] = {
+                "wave": None, "start": iso(start, post_start[n]),
+                "finish": iso(start, post_end[n]), "slot": None,
+                "duration_minutes": post_dur[n], "size": G[n].get("size"),
+                "lane": lane[n], "tier": None, "level": None, "live": False,
+                "inherited": False, "started": False,
+                "start_reason": "post-closure: after the round-close stamp",
+                "coordinator": touches_coordinator(G[n]), "batch": None,
+                "stamp": None, "after": sorted(deps_post[n]), "done": False,
+                "post_closure": True,
+            }
+            continue
         if n in done:
             groups_out[n] = {
                 "wave": None, "start": None, "finish": None, "slot": None,
@@ -919,6 +1161,8 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
                 "coordinator": touches_coordinator(G[n]), "batch": None,
                 "stamp": None, "after": [], "done": True,
             }
+            if n in absorbed_by:
+                groups_out[n]["absorbed_into"] = absorbed_by[n][0]
             continue
         groups_out[n] = {
             "wave": next(w["wave"] for w in waves if n in w["groups"]),
@@ -943,7 +1187,19 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
             "after": sorted(deps[n]),
             "done": False,
         }
-
+        if n in exempt:
+            groups_out[n]["exempt"] = True
+        if n in design_only:
+            groups_out[n]["design_only"] = True
+
+    arrivals = None
+    if inflow > 0:
+        # Expected arrivals over the plan's wall time, priced at the median
+        # size: reported, not scheduled -- they are not groups yet.
+        sz = sorted(float(v) for v in size_hours.values())
+        n_exp = inflow * closure / 60.0
+        arrivals = {"groups": round(n_exp, 2),
+                    "work_hours": round(n_exp * sz[len(sz) // 2], 2)}
     peak_flight, peak_coord = peak_concurrency(groups_out, start)
     peak_working = peak_seats(groups_out, start)
     inherited_deps = [
@@ -953,9 +1209,32 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
         if merged_t[g] > start_t[n]
     ]
     inherited_coord = sorted(n for n in inherited if coord[n])
+    # The binding chain: from the closing group, back through each group's
+    # last-finishing predecessor in the SCHEDULE. It differs from the
+    # unconstrained critical path whenever slots bind; the gap is its slack.
+    chain = []
+    if merged_t:
+        node = max(merged_t, key=lambda n: (merged_t[n], n))
+        while node is not None:
+            chain.append(node)
+            node = (max(deps[node], key=lambda a: (merged_t[a], a)) if deps[node] else None)
+        chain.reverse()
+    cp_hours = height[cp[0]] if cp else 0.0
+    binding = {
+        "chain": chain,
+        "links": [{"group": n, "start": iso(start, start_t[n]),
+                   "finish": iso(start, merged_t[n])} for n in chain],
+        "critical_path_hours": round(cp_hours, 2),
+        "critical_path_slack_hours": round(closure / 60.0 - cp_hours, 2),
+        "slot_sensitivity": "uncalibrated: 7-day roster history (27 snapshots 6 h "
+                            "apart) gave r=0.045 between live groups and completions 12 h later",
+    }
     plan = {
         "schema": 1,
         "generated": {
+            "stamp_credit": credit,
+            "liveness": ("evidence" if evidence is not None else "stage word"),
+            "demoted_live": sorted(demoted),
             "roster_ref": roster_ref,
             "roster_blob": roster_blob,
             "start": iso(start, 0),
@@ -995,7 +1274,12 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
             "stamps": len(stamps),
             "groups_total": len(G),
             "groups_done": len(done),
-            "groups_open": len(open_),
+            "groups_open": len(open_all),
+            "post_closure": sorted(post),
+            "post_closure_finish": (iso(start, max(post_end.values())) if post_end else None),
+            "production_since_tag": len(credit),
+            "exempt_started": len(exempt),
+            **({"expected_arrivals": arrivals} if arrivals else {}),
             "inherited_in_progress": len(inherited),
             "inherited_coordinator": sum(1 for n in inherited if coord[n]),
             "peak_in_flight": peak_flight,
@@ -1003,6 +1287,8 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
             "peak_coordinator_in_flight": peak_coord,
         },
         "critical_path": cp,
+        "binding": binding,
+        "absorbed": {n: {"into": a, "advisory": adv} for n, (a, adv) in absorbed_by.items()},
         "groups": groups_out,
         "waves": waves,
         "batches": [{"id": b["id"], "at": iso(start, b["at"]), "groups": b["groups"]}
@@ -1063,7 +1349,7 @@ def _sweep(groups_out: dict, start: dt.datetime, coord_only: bool = False,
 
     events = []
     for g in groups_out.values():
-        if g.get("done"):
+        if g.get("done") or g.get("post_closure"):
             continue
         if coord_only and not g.get("coordinator"):
             continue
@@ -1110,6 +1396,12 @@ def check_plan(plan: dict) -> list:
     coord_cap = caps["coordinator_cap"]
     every = caps["stamp_every"]
     groups = {n: g for n, g in plan["groups"].items() if not g.get("done")}
+    # What the caps count: not the critical-path groups started past the
+    # slots cap (exempt by rule, never filtered out of the report), and not
+    # post-closure owner steps, which hold no slot.
+    counted = {n: g for n, g in groups.items()
+               if not g.get("exempt") and not g.get("post_closure")}
+    in_round = {n: g for n, g in groups.items() if not g.get("post_closure")}
     start = dt.datetime.strptime(plan["generated"]["start"], "%Y-%m-%dT%H:%M:%SZ")
 
     def mins(s: str) -> int:
@@ -1144,16 +1436,16 @@ def check_plan(plan: dict) -> list:
     # The caps bind what the plan DISPATCHES: a started group (a working
     # fixer, its PR already open) is never refused for the state it inherited,
     # but no planned group may start while the cap is already full.
-    for n, g in groups.items():
+    for n, g in counted.items():
         if g.get("started"):
             continue
         t0 = mins(g["start"])
-        cur = sum(1 for m, h in groups.items() if m != n
+        cur = sum(1 for m, h in counted.items() if m != n
                   and mins(h["start"]) <= t0 < mins(h["finish"]))
         if cur >= slots:
             bad.append(f"in flight: {n} dispatched at {g['start']} with {cur} "
                        f"groups in flight (cap {slots})")
-        curw = sum(1 for m, h in groups.items() if m != n
+        curw = sum(1 for m, h in counted.items() if m != n
                    and mins(h["start"]) <= t0 < mins(h["start"]) + h["duration_minutes"])
         if curw >= seats:
             bad.append(f"seats: {n} dispatched at {g['start']} with {curw} "
@@ -1161,7 +1453,7 @@ def check_plan(plan: dict) -> list:
 
     # 3. coordinator cap: at most `coord_cap` PLANNED groups in flight; the
     #    inherited in-progress set is recorded and must match the groups.
-    coord = [(n, g) for n, g in groups.items() if g.get("coordinator")]
+    coord = [(n, g) for n, g in in_round.items() if g.get("coordinator")]
     for t, _, _ in events:
         curc = sum(1 for n, g in coord
                    if not g.get("started")
@@ -1190,7 +1482,7 @@ def check_plan(plan: dict) -> list:
     # 4. a wave opens only while the open-PR cap has room
     for w in plan.get("waves", []):
         t = mins(w["opens"])
-        cur = sum(1 for g in groups.values() if not g.get("started")
+        cur = sum(1 for g in counted.values() if not g.get("started")
                   and mins(g["start"]) <= t < mins(g["finish"]))
         if cur > slots:
             bad.append(f"wave {w['wave']} opens at {w['opens']} with {cur} in "
@@ -1200,8 +1492,10 @@ def check_plan(plan: dict) -> list:
     #    the last fewer-than-`every` ride the one round-close stamp that closes
     #    the programme, last, at the version `closure_version` assigns
     produced = [n for n, g in sorted(
-        ((n, g) for n, g in groups.items() if g.get("lane") in PRODUCTION),
+        ((n, g) for n, g in in_round.items() if g.get("lane") in PRODUCTION),
         key=lambda x: (mins(x[1]["finish"]), x[0]))]
+    credit = list((plan.get("generated") or {}).get("stamp_credit") or [])
+    produced = credit + produced
     patch_stamps = [s for s in plan.get("stamps", []) if s["kind"] == "patch"]
     closes = [s for s in plan.get("stamps", []) if s["kind"] == ROUND_CLOSE]
     gen = plan.get("generated") or {}
@@ -1218,6 +1512,11 @@ def check_plan(plan: dict) -> list:
              if s["kind"] not in ("patch", ROUND_CLOSE)]
     if stray:
         bad.append(f"stamp cadence: unknown stamp kind(s) {stray}")
+    for n in plan.get("summary", {}).get("post_closure") or []:
+        if any(n in s["carries"] for s in plan.get("stamps", [])):
+            bad.append(f"post-closure: {n} is in a stamp's carries")
+        if closes and mins(groups[n]["start"]) < mins(closes[0]["at"]):
+            bad.append(f"post-closure: {n} starts before the round-close stamp")
     if len(patch_stamps) != len(produced) // every:
         bad.append(f"stamp cadence: {len(patch_stamps)} patch stamps for "
                    f"{len(produced)} production merges at a cadence of {every}")
@@ -1244,7 +1543,7 @@ def check_plan(plan: dict) -> list:
         bad.append("summary: stamp count disagrees with the stamps list")
     if s["groups_open"] != len(groups):
         bad.append("summary: open-group count disagrees with the groups list")
-    closure = max((mins(g["finish"]) for g in groups.values()), default=0)
+    closure = max((mins(g["finish"]) for g in in_round.values()), default=0)
     if mins(s["closure"]) != closure:
         bad.append("summary: closure is not the last group finish")
     if "model" in plan["generated"]:
@@ -1659,6 +1958,7 @@ def selftest() -> int:
     prod = {"groups": [
         {"group": f"P{i}", "size": "S", "lane": "Core model", "kind": "defect",
          "after": [], "resume": {"stage": "not-started"}} for i in range(6)]}
+    caps = dict(caps, stamp_every=5)
     p6 = build_plan(prod, durations, caps, start, "v1.0.0", round_n=FIXTURE_ROUND)
     pat = [s for s in p6["stamps"] if s["kind"] == "patch"]
     expect("five production merges cut one patch stamp",
@@ -1725,6 +2025,258 @@ def selftest() -> int:
     expect("--check refuses a plan recording no round",
            any("round close" in b for b in bad), str(bad))
 
+    # ---- the round-10 flow-toolkit carries: one arm each, with a null control
+    def fx(n, size="S", kind="defect", lane="Core model", stage="not-started",
+           after=(), **kw):
+        return {"group": n, "size": size, "lane": lane, "kind": kind,
+                "after": list(after), "resume": {"stage": stage, **kw.pop("res", {})}, **kw}
+
+    def sched(p, drop=()):
+        return json.dumps({"g": {n: v for n, v in p["groups"].items() if n not in drop},
+                           "w": p["waves"], "s": p["stamps"], "b": p["batches"]},
+                          sort_keys=True)
+
+    def mk(groups, **kw):
+        c = kw.pop("caps_", dict(caps, stamp_every=DEFAULT_CAPS["stamp_every"]))
+        return build_plan({"groups": groups}, kw.pop("dur", durations), c, start,
+                          "v1.0.0", round_n=FIXTURE_ROUND, **kw)
+
+    # 1. absorbed counts as done (carry 2)
+    base_g = [fx("R10-A"), fx("R10-B", after=["R10-A"])]
+    ab = mk(base_g + [fx("R10-AB", stage="absorbed", res={"note": "absorbed into R10-A"})])
+    expect("absorbed: the group is done, names its absorber, is not scheduled",
+           ab["groups"]["R10-AB"]["done"] and ab["groups"]["R10-AB"]["start"] is None
+           and ab["groups"]["R10-AB"]["absorbed_into"] == "R10-A"
+           and ab["absorbed"]["R10-AB"] == {"into": "R10-A", "advisory": None}, str(ab["absorbed"]))
+    nb = mk(base_g + [fx("R10-AB", stage="absorbed", res={"note": "folded away"})])
+    expect("absorbed: a note naming no group records the ADVISORY, never a refusal",
+           nb["absorbed"]["R10-AB"]["into"] is None
+           and nb["absorbed"]["R10-AB"]["advisory"].startswith("ADVISORY: R10-AB"), str(nb["absorbed"]))
+    expect("absorbed (null): the roster minus the absorbed group reproduces the schedule",
+           sched(ab, drop=("R10-AB",)) == sched(mk(base_g)), "schedules differ")
+
+    # 2. post-closure groups (carries 10, 11)
+    cat = fx("R10-CATALOG-PR", kind="owner-step", lane="Docs", after=["R10-B"],
+             res={"next_step": "after the round-close stamp"})
+    pc = mk(base_g + [cat])
+    p0 = mk(base_g)
+    close_at = pc["stamps"][-1]["at"]
+    expect("post-closure: the owner step starts at or after the closing stamp, flagged",
+           pc["groups"]["R10-CATALOG-PR"].get("post_closure") is True
+           and pc["groups"]["R10-CATALOG-PR"]["start"] >= close_at
+           and pc["summary"]["post_closure"] == ["R10-CATALOG-PR"], str(pc["groups"]["R10-CATALOG-PR"]))
+    expect("post-closure: in no stamp's carries and outside summary.closure",
+           all("R10-CATALOG-PR" not in s["carries"] for s in pc["stamps"])
+           and pc["summary"]["closure"] == p0["summary"]["closure"]
+           and pc["stamps"] == p0["stamps"], str(pc["stamps"]))
+    expect("post-closure (null): a production group with no stamp dependency is in the "
+           "closing stamp's carries",
+           pc["stamps"][-1]["carries"] == ["R10-A", "R10-B"], str(pc["stamps"][-1]))
+    expect("post-closure: the plan passes --check", check_plan(pc) == [], str(check_plan(pc)))
+
+    # 3. overflow start (carry 8): a critical-path group starts past a full cap
+    ov = mk([fx("L1", stage="in-progress"), fx("L2", stage="in-progress"), fx("X3", "L"),
+             fx("CP1", "XL"), fx("CP2", after=["CP1"])], caps_=dict(caps, slots=2))
+    expect("overflow: a ready critical-path group starts at t=0, flagged exempt",
+           ov["groups"]["CP1"]["start"] == iso(start, 0) and ov["groups"]["CP1"].get("exempt") is True
+           and check_plan(ov) == [], str({n: g["start"] for n, g in ov["groups"].items()}))
+    expect("overflow (null): the non-critical group past the cap waits and is not exempt",
+           any(g["start"] > iso(start, 0) and not g.get("exempt")
+               for n, g in ov["groups"].items() if n == "X3"), "none waited")
+
+    # 4. stamp cadence counts groups, not pull requests (carry 9)
+    cad = [fx("P1", stage="done"), fx("P2", stage="done"), fx("Q1"), fx("Q2")]
+    ck = mk(cad, since_tag=["P1", "P1", "P2"])    # P1 took two pull requests
+    expect("cadence: the patch stamp lands at the 3rd GROUP, carrying it, not the 3rd PR",
+           [s["carries"] for s in ck["stamps"]] == [["P1", "P2", "Q1"], ["Q2"]]
+           and ck["summary"]["production_since_tag"] == 2, str(ck["stamps"]))
+    expect("cadence (null): no credit leaves two groups and no patch stamp",
+           [s["carries"] for s in mk(cad)["stamps"]] == [["Q1", "Q2"]], "")
+    G4 = groups_of({"groups": [fx("R10-X"), fx("R10-Y"), fx("R10-Z"), fx("R10-W", kind="instrument")]})
+    code, note = "+x = 1\n-x = 0\n", "+# a new note\n-\n+   \n"
+    got = production_groups_since([
+        {"subject": "R10-X (#1)", "diff": code}, {"subject": "R10-X part 2 (#2)", "diff": code},
+        {"subject": "R10-Y (#3)", "diff": note}, {"subject": "R10-Z (#4)", "diff": code},
+        {"subject": "R10-W (#5)", "diff": code}], G4)
+    expect("cadence: production groups since the tag, once each; comment-only and "
+           "instrument groups do not count", got == ["R10-X", "R10-Z"], str(got))
+
+    # 5. evidence liveness (carries 0, 3)
+    wip = [fx("W", stage="in-progress"), fx("O")]
+    nev = mk(wip, evidence={"refs": set(), "prs": []})
+    lev = mk(wip, evidence={"refs": {"handoff/w"}, "prs": []})
+    expect("evidence: an in-progress group with no ref is pending",
+           nev["groups"]["W"]["live"] is False and nev["generated"]["demoted_live"] == ["W"],
+           str(nev["groups"]["W"]))
+    expect("evidence (null): with a handoff ref it is live",
+           lev["groups"]["W"]["live"] is True and lev["generated"]["demoted_live"] == [],
+           str(lev["groups"]["W"]))
+    def strip_g(p):
+        q = json.loads(json.dumps(p))
+        q["generated"].pop("liveness"), q["generated"].pop("demoted_live")
+        return json.dumps(q, sort_keys=True)
+    expect("evidence (null): no-evidence reproduces the stage-word plan byte-for-byte",
+           strip_g(mk(wip)) == strip_g(lev) and mk(wip) == mk(wip, evidence=None), "plans differ")
+    one = dict(caps, slots=1)
+    held = [fx("H", "L", stage="carries-open", carry=["c"] * 3), fx("F", "XL")]
+    hp = mk(held, caps_=one, evidence={"refs": set(), "prs": [{"headRefName": "fixer/h"}]})
+    hn = mk(held, caps_=one, evidence={"refs": set(), "prs": []})
+    expect("evidence: a carries-open group with an open PR starts at t=0 as live",
+           hp["groups"]["H"]["start"] == iso(start, 0) and hp["groups"]["H"]["live"] is True,
+           str(hp["groups"]["H"]))
+    expect("evidence (null): the same group with no PR waits behind the full slot",
+           hn["groups"]["H"]["live"] is False, str(hn["groups"]["H"]))
+    pr_ = mk([fx("N", "M")], evidence={"refs": set(), "prs": [{"headRefName": "fixer/n"}]})
+    expect("evidence: an open PR credits the live fraction (0.7 x 4 h)",
+           pr_["groups"]["N"]["duration_minutes"] == 168, str(pr_["groups"]["N"]))
+    ds = mk([fx("F", "XL"), fx("D", "M")], caps_=one,
+            evidence={"refs": {"design/d"}, "prs": []})
+    expect("evidence: a design-only group starts at t=0 at its full duration, no credit",
+           ds["groups"]["D"]["start"] == iso(start, 0) and ds["groups"]["D"]["live"] is False
+           and ds["groups"]["D"]["duration_minutes"] == 240
+           and ds["groups"]["D"].get("design_only") is True, str(ds["groups"]["D"]))
+
+    # 6. the binding chain beside the critical path
+    bind = mk([fx("C", "L"), fx("BA"), fx("BB", after=["BA"])], caps_=one)
+    bw = mk([fx("C", "L"), fx("BA"), fx("BB", after=["BA"])])
+    expect("binding: the slot-delayed predecessor is a link, with the critical-path slack",
+           bind["critical_path"] == ["C"] and bind["binding"]["chain"] == ["BA", "BB"]
+           and bind["groups"]["BA"]["start"] > iso(start, 0)
+           and bind["binding"]["critical_path_slack_hours"] > 0
+           and "uncalibrated" in bind["binding"]["slot_sensitivity"], str(bind["binding"]))
+    expect("binding (null): with a slot for each the chain is the critical path",
+           bw["binding"]["chain"] == bw["critical_path"], str(bw["binding"]))
+
+    # 7. inflow
+    infl = [fx("A"), fx("B", after=["A"])]
+    i0 = mk(infl, dur=dict(durations, inflow_groups_per_hour=0))
+    expect("inflow: 0 reproduces the plan byte-for-byte, no arrivals",
+           i0 == mk(infl) and "expected_arrivals" not in i0["summary"], "")
+    i4 = mk(infl, dur=dict(durations, inflow_groups_per_hour=0.4))
+    want = round(0.4 * i4["summary"]["wall_hours"], 2)
+    expect("inflow: above 0 adds expected_arrivals and changes nothing scheduled",
+           abs(i4["summary"]["expected_arrivals"]["groups"] - want) <= 0.01
+           and sched(i4) == sched(mk(infl)), str(i4["summary"].get("expected_arrivals")))
+
+    # 8. repair round 4: one pin per reviewer mutant, each with its null control
+    ovs = mk([fx("L1", stage="in-progress"), fx("L2", "XL", stage="in-progress"), fx("X3"),
+              fx("CP1", "XL"), fx("CP2", after=["CP1"])], caps_=dict(caps, slots=2))
+    expect("overflow slots do not hold a real slot: the waiting group takes the slot a "
+           "finished group frees while the exempt one still runs",
+           ovs["groups"]["CP1"].get("exempt") is True
+           and ovs["groups"]["X3"]["start"] == ovs["groups"]["L1"]["finish"]
+           and ovs["groups"]["X3"]["start"] < ovs["groups"]["CP1"]["finish"],
+           str({n: (g["start"], g["finish"]) for n, g in ovs["groups"].items()}))
+    expect("overflow (null): no exempt group, the waiter also starts at the freed slot",
+           mk([fx("L1", stage="in-progress"), fx("L2", "XL", stage="in-progress"), fx("X3")],
+              caps_=dict(caps, slots=2))["groups"]["X3"]["start"]
+           == ovs["groups"]["L1"]["finish"], "")
+    pcs = mk(base_g + [cat, fx("R10-AFTER", after=["R10-CATALOG-PR"]),
+                       fx("STAMP-ROUND-MAJOR"), fx("R10-ZED", after=["STAMP-ROUND-MAJOR"])])
+    expect("post-closure: what follows an owner step, and what follows the closing-stamp "
+           "group, is post-closure too",
+           pcs["summary"]["post_closure"] == ["R10-AFTER", "R10-CATALOG-PR", "R10-ZED"]
+           and check_plan(pcs) == [], str(pcs["summary"]["post_closure"]) + str(check_plan(pcs)))
+    expect("post-closure (null): a group after nothing post-closure is in the round",
+           "R10-B" not in pcs["summary"]["post_closure"]
+           and "STAMP-ROUND-MAJOR" not in pcs["summary"]["post_closure"], "")
+    early = json.loads(json.dumps(pc))
+    early["groups"]["R10-CATALOG-PR"]["start"] = iso(start, 0)
+    expect("--check refuses a post-closure group starting before the round-close stamp",
+           any("starts before the round-close stamp" in b for b in check_plan(early)),
+           str(check_plan(early)))
+    carried = json.loads(json.dumps(pc))
+    carried["stamps"][0]["carries"] = carried["stamps"][0]["carries"] + ["R10-CATALOG-PR"]
+    expect("--check refuses a post-closure group named in a stamp's carries",
+           any("is in a stamp's carries" in b for b in check_plan(carried)),
+           str(check_plan(carried)))
+    expect("--check counts the credited groups among the merges (null: plan holds)",
+           check_plan(ck) == [], str(check_plan(ck)))
+    nonprod = mk(cad + [fx("R10-W", kind="instrument", stage="done")],
+                 since_tag=["R10-W", "P1", "P1", "P2"])
+    expect("cadence: a non-production done group in the tag range earns no credit",
+           nonprod["summary"]["production_since_tag"] == 2
+           and [s["carries"] for s in nonprod["stamps"]] == [["P1", "P2", "Q1"], ["Q2"]],
+           str(nonprod["stamps"]))
+    open_c = mk(cad, since_tag=["Q1"])
+    expect("cadence: a credited group still open is counted once, in the plan",
+           open_c["summary"]["production_since_tag"] == 0
+           and [s["carries"] for s in open_c["stamps"]] == [["Q1", "Q2"]], str(open_c["stamps"]))
+    pd = [fx("P%d" % i, stage="done") for i in range(1, 5)] + [fx("Q1"), fx("Q2")]
+    cutd = mk(pd, since_tag=["P1", "P2", "P3", "P4"])
+    expect("cadence: a patch stamp cuts `every` groups and keeps the rest for the next",
+           [s["carries"] for s in cutd["stamps"]] == [["P1", "P2", "P3"], ["P4", "Q1", "Q2"], []],
+           str([s["carries"] for s in cutd["stamps"]]))
+    bj = mk([fx("A"), fx("B", "XL"), fx("C", after=["A", "B"])])
+    expect("binding: the chain walks back through the LAST-finishing predecessor",
+           bj["binding"]["chain"] == ["B", "C"], str(bj["binding"]["chain"]))
+    expect("binding (null): the early predecessor is not the link",
+           "A" not in bj["binding"]["chain"], "")
+    szs = sorted(float(v) for v in durations["sizes_hours"].values())
+    ea = i4["summary"]["expected_arrivals"]
+    expect("inflow: arrivals are priced at the median size",
+           abs(ea["work_hours"] - ea["groups"] * szs[len(szs) // 2]) <= 0.05
+           and szs[0] != szs[len(szs) // 2], str(ea))
+    expect("live refs: a ls-remote listing yields branch names without refs/heads/, tags dropped",
+           parse_live_refs("abc\trefs/heads/fixer/w\nabc\trefs/tags/v1\n\n") == {"fixer/w"},
+           str(parse_live_refs("abc\trefs/heads/fixer/w\nabc\trefs/tags/v1\n")))
+    pp = mk(base_g + [cat, fx("R10-CAT2", kind="owner-step", lane="Docs", after=["R10-B"],
+                              res={"next_step": "after the round-close stamp"})])
+    expect("post-closure groups are outside the in-flight peak (null: none, same peak)",
+           pp["summary"]["peak_in_flight"] == p0["summary"]["peak_in_flight"]
+           and pp["summary"]["peak_working"] == p0["summary"]["peak_working"],
+           str((pp["summary"]["peak_in_flight"], p0["summary"]["peak_in_flight"])))
+    # liveness: a stage-word live group with a design ref only is design-only, uncredited
+    wd = mk([fx("W", "M", stage="in-progress"), fx("O")],
+            evidence={"refs": {"design/w"}, "prs": []})
+    wn = mk([fx("W", "M"), fx("O")], evidence={"refs": {"design/w"}, "prs": []})
+    expect("evidence: a stage-live group with only a design ref gets no live credit",
+           wd["groups"]["W"]["live"] is False and wd["groups"]["W"].get("design_only") is True
+           and wd["groups"]["W"]["duration_minutes"] == wn["groups"]["W"]["duration_minutes"],
+           str(wd["groups"]["W"]))
+    # --since-tag on main's real merge subjects and merge diffs (carry 9)
+    G9 = groups_of({"groups": [fx("R10-STORE"), fx("R10-STORE-RACES", res={}, branch="fix/r10-store-races"),
+                               fx("R10-W", kind="instrument")]})
+    real = [{"subject": "Merge pull request #12 from tvofi/fix/r10-store-races", "diff": code},
+            {"subject": "Merge pull request #13 from tvofi/fix/r10-w", "diff": code},
+            {"subject": "Merge pull request #14 from tvofi/fix/unrelated", "diff": code}]
+    expect("since-tag: a real-shaped merge subject names its group by the topic branch",
+           production_groups_since(real, G9) == ["R10-STORE-RACES"],
+           str(production_groups_since(real, G9)))
+    expect("since-tag (null): the same merges with no code change credit nothing",
+           production_groups_since([dict(c, diff=note) for c in real], G9) == [], "")
+    parts = [{"subject": "Merge pull request #15 from tvofi/fix/r10-store-p2", "diff": code},
+             {"subject": "Merge pull request #16 from tvofi/fix/r10-store-p3", "diff": code},
+             {"subject": "Merge pull request #17 from tvofi/fix/r10-store-races-p2", "diff": code},
+             {"subject": "Merge pull request #18 from tvofi/fix/r10-storey", "diff": code},
+             {"subject": "Merge pull request #19 from tvofi/fix/unrelated-p2", "diff": code}]
+    expect("since-tag: part branches credit their group by the longest roster topic they extend, once each",
+           production_groups_since(parts, G9) == ["R10-STORE", "R10-STORE-RACES"],
+           str(production_groups_since(parts, G9)))
+    expect("since-tag (null): an unrelated topic and a non-boundary prefix (r10-storey) credit nothing",
+           production_groups_since(parts[3:], G9) == [], str(production_groups_since(parts[3:], G9)))
+    sq = production_groups_since([{"subject": "R10-STORE-RACES (#20)", "diff": code}], G9)
+    expect("since-tag: a squash subject naming R10-STORE-RACES credits it, not the shorter R10-STORE",
+           sq == ["R10-STORE-RACES"], str(sq))
+    with throwaway_git_environ(), tempfile.TemporaryDirectory() as gd:
+        def g(*a):
+            return subprocess.run(["git", "-C", gd, *a], capture_output=True, text=True)
+        throwaway_git_init(gd, "-q", "-b", "main")
+        (Path(gd) / "custom_components").mkdir()
+        (Path(gd) / "custom_components" / "a.py").write_text("x = 0\n")
+        g("add", "-A"), g("commit", "-q", "-m", "base"), g("tag", "v0")
+        g("checkout", "-q", "-b", "fix/r10-store-races")
+        (Path(gd) / "custom_components" / "a.py").write_text("x = 1\n")
+        g("commit", "-q", "-am", "work")
+        g("checkout", "-q", "main")
+        (Path(gd) / "other.txt").write_text("m\n")
+        g("add", "-A"), g("commit", "-q", "-m", "mainline")
+        g("merge", "-q", "--no-ff", "-m", "Merge pull request #12 from tvofi/fix/r10-store-races",
+          "fix/r10-store-races")
+        got = production_groups_since(git_commits_since_tag(gd), G9)
+        expect("since-tag: a clean merge's change is read against its first parent",
+               got == ["R10-STORE-RACES"], str(got))
+
     gate = gate_minutes(durations)
     want_gate = 50.0 + 22.0 + 27.0 * (1.0 + 0.04)
     expect("the gate price includes the cancelled-leg rerun",
@@ -1794,8 +2346,80 @@ def selftest() -> int:
              _m("def dispatch_key(n: str, ", "tier: dict, crit: set,"),
              _m('sav = (-savings[n] if n in savings ', 'else float("inf"))'), "sav = (0.0)"),
             ("cp-first-in-tier",
-             _m("def dispatch_key(n: str, ", "tier: dict, crit: set,"),
-             _m("(t, 0 if n in crit ", "else 1, sav,"), "(t, 0, sav,"),
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             _m("n = pick(sorted(x for x in ready ", "if x in crit), t)"),
+             "n = pick(sorted(x for x in ready if False), t)"),
+            ("overflow-exempt",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "exempt.add(n)", "pass"),
+            ("absorbed-done",
+             _m("def is_done(group: ", "dict) -> bool:"),
+             "return not roster_lib.is_open(group)",
+             'return (group.get("resume") or {}).get("stage") in ("done", "rca-done")'),
+            ("absorbed-advisory",
+             _m("def absorbers(G: ", "dict) -> dict:"),
+             _m('out[n] = (into, None if into else', ''), 'out[n] = (into, None if True else'),
+            ("post-closure-excluded",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "open_ = open_all - post", "open_ = open_all"),
+            ("post-closure-after-stamp",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             'max([stamps[-1]["at"]] + [', "max([0] + ["),
+            ("stamp-credit-groups",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "dict.fromkeys(since_tag or [])", "(since_tag or [])"),
+            ("comment-only-diff",
+             _m("def substantive(diff: ", "str) -> bool:"),
+             'not body.startswith("#")', "True"),
+            ("stamp-credit-lane",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "lane[n] in PRODUCTION and n in done]", "n in done]"),
+            ("stamp-credit-done",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "lane[n] in PRODUCTION and n in done]", "lane[n] in PRODUCTION]"),
+            ("since-tag-merge-topic",
+             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
+             "n = by_topic[max(hit, key=len)] if hit else None", "n = None"),
+            ("since-tag-first-parent",
+             _m("def git_commits_since_tag(", "repo: str) -> list:"),
+             '"diff", "-U0", f"{sha}^1", sha,', '"show", "-U0", sha, "--format=",'),
+            ("since-tag-part-branch",
+             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
+             'topic == t or topic.startswith(t + "-")]', 'topic == t]'),
+            ("since-tag-part-boundary",
+             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
+             'topic.startswith(t + "-")]', 'topic.startswith(t)]'),
+            ("since-tag-part-longest",
+             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
+             "n = by_topic[max(hit, key=len)] if hit else None", "n = by_topic[min(hit, key=len)] if hit else None"),
+            ("since-tag-squash-longest",
+             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
+             "n = max(named, key=len) if named else None", "n = min(named, key=len) if named else None"),
+            ("since-tag-once",
+             _m("def production_groups_since(commits: ", "list, G: dict) -> list:"),
+             "return list(out)", "return [n for n in out] + list(out)"),
+            ("evidence-design-uncredited",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "live = (live - demoted - ev_design) | ev_live\n",
+             "live = (live - demoted) | ev_live | ev_design\n"),
+            ("evidence-demotes",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "demoted = {n for n in live if topic_evidence", "demoted = {n for n in set() if topic_evidence"),
+            ("evidence-pr-live",
+             _m("def topic_evidence(group: ", "dict, evidence: dict) -> str | None:"),
+             'return "pr"', 'return "work"'),
+            ("binding-start",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "node = max(merged_t, key=", "node = min(merged_t, key="),
+            ("binding-slack",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "closure / 60.0 - cp_hours", "0.0"),
+            ("inflow-zero",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "if inflow > 0:", "if inflow >= 0:"),
+            ("inflow-rate",
+             _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
+             "n_exp = inflow * closure / 60.0", "n_exp = 1.0"),
             ("height-tiebreak",
              _m("def dispatch_key(n: str, ", "tier: dict, crit: set,"),
              _m("sav, -height[n], ", "-dur_min[n], n)"), "sav, n)"),
@@ -1848,7 +2472,7 @@ def selftest() -> int:
              "if size not in sizes:", "if False:"),
             ("stamp-cadence",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
-             _m("if len(carry) >= ", "every:"), "if False:"),
+             _m("while len(carry) >= ", "every:"), "while False:"),
             ("round-close-version",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
              _m("stamps.append({\"version\": closing, ", "\"at\": closure + closure_lead,"),
@@ -1865,8 +2489,8 @@ def selftest() -> int:
              _m("if s[\"kind\"] not in (\"patch\", ", "\"minor\", ROUND_CLOSE)]")),
             ("round-n-required",
              _m("def build_plan(roster: dict, ", "durations: dict, caps: dict, start: dt.datetime,"),
-             _m("roster_path: str = \"\", *, ", "round_n: int) -> dict:"),
-             _m("roster_path: str = \"\", *, ", "round_n: int = 10) -> dict:")),
+             _m("roster_path: str = \"\", *, ", "round_n: int, since_tag"),
+             _m("roster_path: str = \"\", *, ", "round_n: int = 10, since_tag")),
             ("round-from-roster",
              _m("def main(argv=", "None) -> int:"),
              _m("round_n = roster_lib.roster_round(", "src)"), "round_n = 99"),
@@ -2050,6 +2674,13 @@ def parse_args(argv=None):
     p.add_argument("--sizes-csv", default=None, help="--measure-sizes: write the raw rows here")
     p.add_argument("--prs-cache", default=None, help="--measure-sizes: read or write the fetch")
     p.add_argument("--out-durations", default=None)
+    p.add_argument("--live-refs", default=None,
+                   help="a saved `git ls-remote --heads` listing: liveness by evidence")
+    p.add_argument("--in-flight", default=None,
+                   help="JSON list of open pull requests (number, headRefOid, headRefName, isDraft)")
+    p.add_argument("--since-tag", action="store_true",
+                   help="credit the stamp cadence with production groups merged since the last tag "
+                        "(comment-only diffs ignored)")
     p.add_argument("--repo-owner", default="tvofi/heatpump_optimizer")
     p.add_argument("--merges", type=int, default=30)
     p.add_argument("--slots", type=int, default=None,
@@ -2140,8 +2771,18 @@ def main(argv=None) -> int:
         round_n = roster_lib.roster_round(src)
     except roster_lib.RosterNotFound as exc:
         raise PlanError(f"no round for the round-close stamp: {exc}") from exc
+    evidence = None
+    if args.live_refs or args.in_flight:
+        evidence = {
+            "refs": (parse_live_refs(Path(args.live_refs).read_text(encoding="utf-8"))
+                     if args.live_refs else set()),
+            "prs": (json.loads(Path(args.in_flight).read_text(encoding="utf-8"))
+                    if args.in_flight else []),
+        }
+    since_tag = (production_groups_since(git_commits_since_tag(args.repo), groups_of(roster))
+                 if args.since_tag else None)
     plan = build_plan(roster, durations, caps, start, version, ref, blob,
-                      roster_path=src, round_n=round_n)
+                      roster_path=src, round_n=round_n, since_tag=since_tag, evidence=evidence)
     bad = check_plan(plan)
     if bad:
         print("the model produced a violating plan; refusing to write it", file=sys.stderr)
@@ -2168,6 +2809,19 @@ def print_waves(plan: dict) -> None:
           f"| inherited coordinator {len(ic.get('groups') or [])}/{ic.get('cap')} "
           f"({len(g.get('inherited_dependency_violations') or [])} inherited "
           f"dependency inversion(s))")
+    for n, a in (plan.get("absorbed") or {}).items():
+        print(f"absorbed: {n} -> {a['into'] or '?'}" + (f"  {a['advisory']}" if a["advisory"] else ""))
+    if s.get("post_closure"):
+        print(f"post-closure (after the round-close stamp, in no stamp): "
+              f"{', '.join(s['post_closure'])} until {s['post_closure_finish']}")
+    b = plan.get("binding") or {}
+    print(f"binding chain: {' -> '.join(b.get('chain') or [])} | critical path "
+          f"{b.get('critical_path_hours')} h, slack {b.get('critical_path_slack_hours')} h | "
+          f"slot sensitivity {b.get('slot_sensitivity')}")
+    print(f"production groups since the last tag: {s.get('production_since_tag', 0)}")
+    if s.get("expected_arrivals"):
+        print(f"expected arrivals: {s['expected_arrivals']['groups']} groups, "
+              f"{s['expected_arrivals']['work_hours']} work-hours")
 
 
 if __name__ == "__main__":

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
