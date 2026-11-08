# Review packet #3303
head: 265309b18236ed020da6dd25b5efaca1f880af40
base: 7c9c4c154cda514f938fd503cde2779716caf251

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=128563772679 success
arch-score / arch-score id=128570289471 success
arm id=128563430361 skipped
budget-raise-gate / budget-raise-gate id=128570284078 success
cancel-superseded id=128570281222 success
codeql id=128570297256 skipped
codeql / Analyze (actions) id=128563560589 success
codeql / Analyze (javascript-typescript) id=128563560677 success
codeql / Analyze (python) id=128563560597 success
gate id=128570257992 success
governance id=128570285771 skipped
governance / delivery-status id=128563560844 success
governance / delivery-status-publish id=128563562171 skipped
governance / env-matrix id=128563560855 success
governance / instrument-self-tests id=128563560944 success
governance / policy-docs id=128563560852 success
governance / record id=128563561795 skipped
governance / wave-script id=128563560798 success
hassfest id=128570258398 skipped
hassfest / hassfest id=128563560604 success
kernel-points id=128570299213 skipped
pr-contract id=128570297326 skipped
pr-contract / pr-contract id=128569891840 success
prelude id=128570294599 success
refresh id=128570291522 success
tests id=128570281433 skipped
tests / arch-instrument id=128563679189 success
tests / briefs id=128563560656 success
tests / browser id=128563679160 success
tests / ci-ratchet id=128569226802 skipped
tests / claims-autofix id=128567920588 skipped
tests / closure-scope id=128563560691 success
tests / closures id=128563679186 success
tests / closures-autofix id=128568586999 skipped
tests / coverage id=128563679190 success
tests / coverage-ratchet id=128569225911 success
tests / fast (3.14) id=128563679175 success
tests / graders-head-copy id=128569225909 success
tests / lane-proofs id=128569225941 success
tests / mutation id=128563560624 success
tests / mutation-autofix id=128563728694 skipped
tests / mutation-pins id=128563728725 skipped
tests / nightly-ha id=128563680601 skipped
tests / nightly-status id=128563560660 success
tests / replay id=128563680317 skipped
tests / typing id=128563679211 success
validate id=128570258741 skipped
validate / validate-hacs id=128563560664 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 27233708: R10-HOTFIX-GATE-BUSY-DEFER
NOTE body item b28a5e23: dismissed:zero label or kernel-points runs in the sample, so no cost was measured to act on
NOTE body item 9f799d14: dismissed:session tooling outside the repository
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         dev/audit/harnesses/r10_ci_slim/body_defer.py
             `dev/audit/harnesses/r10_ci_slim/body_defer.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py --fetch $SAMPLE --since 2026-11-05T13:26:00Z --until 2026-11-07T22:00:00Z
             `dev/audit/harnesses/r10_ci_slim/edit_runs.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_ci_slim/body_defer.py $SAMPLE --since 2026-11-07T05:00:00Z
             `dev/audit/harnesses/r10_ci_slim/body_defer.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_ci_slim/body_defer.py $SAMPLE --prelude $EXPORT/tools/ci/prelude.py
             `dev/audit/harnesses/r10_ci_slim/body_defer.py` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index e5aa45ed7..c682e25b7 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -309,6 +309,10 @@ jobs:
   # It needs every unit through `pr-contract`, which needs them all and whose
   # `!cancelled()` holds even its skip until they end (one edge into `gate`
   # in the run graph, not ten; dev/audit/harnesses/r10_ci_gate_ready.py).
+  # On a code run for a PR it re-runs the latest edit and review run at this
+  # head that deferred to it (ran no unit, prelude.defer_to) and waits for
+  # them before it judges (gate.redispatch, R10-CI-EDIT-RUNNER): hence
+  # `actions: write`, which only that re-run uses.
   gate:
     needs: [prelude, pr-contract]
     if: ${{ !cancelled() }}
@@ -316,7 +320,7 @@ jobs:
     timeout-minutes: 15
     permissions:
       contents: read
-      actions: read
+      actions: write
       pull-requests: read
     steps:
       # Full history: D-2's three-dot diff against origin/<base>.
@@ -345,7 +349,7 @@ jobs:
           PR: ${{ needs.prelude.outputs.pr }}
           BASE: ${{ needs.prelude.outputs.base }}
           KIND: ${{ needs.prelude.outputs.kind }}
-          # What the prelude ran here: an edit run beside an unfinished code run
-          # runs no pr-contract (prelude.defer_to, R10-CI-SLIM C3).
+          # What the prelude ran here: an edit or review run beside an
+          # unfinished code run runs no unit (prelude.defer_to).
           WORKSET: ${{ needs.prelude.outputs.workset }}
         run: python3 -I tools/ci/gate.py --pr "$PR" --base "$BASE" --kind "$KIND"
diff --git a/dev/audit/harnesses/r10_ci_slim/body_defer.py b/dev/audit/harnesses/r10_ci_slim/body_defer.py
new file mode 100644
index 000000000..55504b614
--- /dev/null
+++ b/dev/audit/harnesses/r10_ci_slim/body_defer.py
@@ -0,0 +1,164 @@
+#!/usr/bin/env python3
+"""R10-CI-EDIT-RUNNER: what CI 'edit' and 'review' runs cost, before and after a
+body run beside an unfinished code run stops holding a runner.
+
+    python3 dev/audit/harnesses/r10_ci_slim/body_defer.py SAMPLE.json [--prelude PATH]
+    python3 dev/audit/harnesses/r10_ci_slim/body_defer.py --self-test
+
+SAMPLE.json is edit_runs.py's recording (`edit_runs.py --fetch`): every ci.yml
+run created in a window, with its latest jobs.
+
+THE RULE. A job costs completed_at - started_at (job-minutes; queueing is not
+counted). A body run is a run whose title parses to kind `edit` or `review`
+(prelude.parse_title). The prelude WAIT of a body run is its prelude's minutes
+above the PRELUDE FLOOR, the median prelude of the sample's code runs (a
+prelude that never waits). For each body run the replay rebuilds the Actions
+state its prelude read at the prelude's started_at (edit_runs.state_at) and
+hands it to the PRODUCTION predicate prelude.defer_to of --prelude (default:
+this tree's copy). A run it does not defer costs what it cost. A run it defers
+costs, after, its deferring attempt: prelude and gate at the floor (it runs
+no unit and its gate publishes at once), every job other than prelude, gate
+and the body units at its recorded minutes. The latest deferred run of each
+kind at a head (gate.pending) also costs the re-run the code run's gate makes:
+prelude and gate at the floor, its body units at their recorded minutes, a
+unit the recording lacks (C3's skipped pr-contract) at the sample's median for
+that unit. The code run's gate waits on those re-runs: per head, the largest
+re-run's body-unit minutes, summed over its units (an estimate: arch-score and
+budget-raise-gate run side by side, which it over-counts, and the re-run's job
+pickups, which it does not count).
+Only the kinds the predicate module defers are replayed (its BODY_KINDS; a
+module without one, the merge base's, defers `edit` alone). --since keeps the
+runs created at or after an instant, the rest staying in the state replayed.
+NULL CONTROLS, printed beside the result: (1) code runs through the same
+predicate (a code run never defers: 0 expected); (2) a run defer_to does not
+defer costs the same before and after (by construction, its count printed).
+"""
+from __future__ import annotations
+
+import argparse
+import json
+import statistics
+import sys
+from pathlib import Path
+
+sys.path.insert(0, str(Path(__file__).resolve().parent))
+import edit_runs  # noqa: E402
+
+ROOT = edit_runs.ROOT
+BODY = ("arch-score / arch-score", "budget-raise-gate / budget-raise-gate", "pr-contract / pr-contract")
+OWES = {"edit": BODY, "review": ("budget-raise-gate / budget-raise-gate",)}
+m = edit_runs.minutes
+
+
+def replay(sample: dict, pre, kinds=("edit", "review"), since: float = 0.0) -> dict:
+    runs = sample["runs"]
+    defers = tuple(getattr(pre, "BODY_KINDS", ("edit",)))
+    kind_of = lambda r: (pre.parse_title(r["title"]) or ("",))[0]  # noqa: E731
+    floor = statistics.median([m(j) for r in runs if kind_of(r) == "code" for j in r["jobs"]
+                               if j["name"] == "prelude" and j.get("completed_at")] or [0.0])
+    unit_med = {n: statistics.median([m(j) for r in runs for j in r["jobs"] if j["name"] == n
+                                      and j.get("completed_at")] or [0.0]) for n in BODY}
+    res = {k: {"runs": 0, "deferred": 0, "before": 0.0, "after": 0.0, "wait_before": 0.0, "wait_after": 0.0,
+               "reruns": 0, "code_gate_wait_added": 0.0} for k in kinds}
+    res["prelude_floor"] = floor
+    latest: dict = {}
+    for r in runs:
+        t = pre.parse_title(r["title"])
+        if t is None or t[0] not in kinds or edit_runs.ts(r["created_at"]) < since:
+            continue
+        pj = next((j for j in r["jobs"] if j["name"] == "prelude" and j.get("started_at")), None)
+        if pj is None:
+            continue
+        x = res[t[0]]
+        x["runs"] += 1
+        before = sum(m(j) for j in r["jobs"])
+        x["before"] += before
+        x["wait_before"] += max(0.0, m(pj) - floor)
+        defer = getattr(pre, "defer_to", None)
+        ctx = {"repo": "o/r", "head": r["head_sha"], "run_id": r["id"]}
+        hit = (defer is not None and t[1] != "" and t[0] in defers
+               and defer(ctx, t[1], edit_runs.state_at(runs, r["head_sha"], edit_runs.ts(pj["started_at"]), r["id"]))
+               is not None)
+        if not hit:
+            x["after"] += before
+            x["wait_after"] += max(0.0, m(pj) - floor)
+            continue
+        x["deferred"] += 1
+        rec = {j["name"]: m(j) for j in r["jobs"]}
+        other = sum(v for n, v in rec.items() if n not in ("prelude", "gate") + BODY)
+        x["after"] += 2 * floor + other
+        units = sum(rec.get(n, unit_med[n]) for n in OWES.get(t[0], ()))
+        key = (r["head_sha"], t[1], t[0])
+        if key not in latest or latest[key][0] < r["id"]:
+            latest[key] = (r["id"], units)
+    gate_wait: dict = {}
+    for (head, pr, kind), (_, units) in latest.items():
+        res[kind]["reruns"] += 1
+        res[kind]["after"] += 2 * floor + units
+        if units > gate_wait.get(head, (0.0, kind))[0]:
+            gate_wait[head] = (units, kind)
+    for units, kind in gate_wait.values():
+        res[kind]["after"] += units
+        res[kind]["code_gate_wait_added"] += units
+    return res
+
+
+def show(label: str, res: dict) -> None:
+    for k, x in res.items():
+        if k == "prelude_floor":
+            continue
+        print(f"{label} {k}: {x['runs']} runs, {x['deferred']} deferred, {x['reruns']} re-run; "
+              f"job-minutes {x['before']:.0f} -> "
+              f"{x['after']:.0f}; prelude wait above the floor {x['wait_before']:.0f} -> {x['wait_after']:.0f}; "
+              f"code-gate wait added {x['code_gate_wait_added']:.0f}")
+    print(f"{label} prelude floor {res['prelude_floor']:.2f} min")
+
+
+def self_test() -> int:
+    pre = edit_runs.load_prelude(ROOT / "tools" / "ci" / "prelude.py")
+    T = lambda mm: f"2026-11-05T10:{mm:02d}:00Z"  # noqa: E731
+
+    def job(n, a, b, c="success"):
+        return {"name": n, "status": "completed", "conclusion": c, "started_at": T(a), "completed_at": T(b)}
+    code = {"id": 1, "title": pre.title("code", "7", "main", "H"), "head_sha": "H", "event": "pull_request",
+            "created_at": T(0), "status": "completed",
+            "jobs": [job("prelude", 0, 1), job("tests / fast (3.14)", 1, 40), job("pr-contract / pr-contract", 41, 42),
+                     job("gate", 42, 43)]}
+    early = {"id": 2, "title": pre.title("review", "7", "main", "H"), "head_sha": "H", "event": "pull_request_review",
+             "created_at": T(5), "status": "completed",
+             "jobs": [job("prelude", 5, 43), job("budget-raise-gate / budget-raise-gate", 43, 45), job("gate", 45, 46)]}
+    late = {**early, "id": 3, "created_at": T(50),
+            "jobs": [job("prelude", 50, 51), job("budget-raise-gate / budget-raise-gate", 51, 53), job("gate", 53, 54)]}
+    twin = {**early, "id": 4, "created_at": T(6)}
+    s = {"runs": [code, early, late]}
+    two = replay({"runs": [code, early, twin]}, pre)["review"]
+    r = replay(s, pre)["review"]
+    # early: before 38 + 2 + 1 = 41, wait 37; after (1+1+0) + (1+1+2) + 2 = 8. late: 4 both ends, wait 0.
+    ok = (r["deferred"], r["before"], r["after"], r["wait_before"], r["wait_after"]) == (1, 45.0, 12.0, 37.0, 0.0)
+    # two deferred at one head: the later is re-run once, the earlier costs its deferring attempt alone.
+    ok &= (two["deferred"], two["reruns"], two["after"]) == (2, 1, 2.0 + 6.0 + 2.0)
+    nul = replay(s, pre, kinds=("code",))["code"]
+    ok &= nul["deferred"] == 0 and nul["after"] == nul["before"]
+    print(f"body_defer self-test: {'ok' if ok else 'FAIL'} {r} / code control {nul['deferred']} deferred")
+    return 0 if ok else 1
+
+
+def main(argv) -> int:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("sample", nargs="?")
+    ap.add_argument("--prelude", default=str(ROOT / "tools" / "ci" / "prelude.py"))
+    ap.add_argument("--since", default="")
+    ap.add_argument("--self-test", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    sample = json.loads(Path(a.sample).read_text())
+    pre = edit_runs.load_prelude(Path(a.prelude))
+    since = edit_runs.ts(a.since) or 0.0
+    show(f"[{a.prelude} since {a.since or 'the start'}]", replay(sample, pre, since=since))
+    show("[null control: code runs, same predicate]", replay(sample, pre, kinds=("code",), since=since))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/harnesses/r10_ci_slim/edit_runs.py b/dev/audit/harnesses/r10_ci_slim/edit_runs.py
index ec8a0a2e2..8aa745daf 100644
--- a/dev/audit/harnesses/r10_ci_slim/edit_runs.py
+++ b/dev/audit/harnesses/r10_ci_slim/edit_runs.py
@@ -1,6 +1,10 @@
 #!/usr/bin/env python3
 """R10-CI-SLIM card C3: what CI 'edit' runs cost, before and after the deferral.
 
+Its cost model is C3's (a deferred run skips only `pr-contract`); for
+R10-CI-EDIT-RUNNER's predicate, where a deferred run runs no unit and is
+re-run, price with body_defer.py, which reads this file's recording.
+
     python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py --fetch SAMPLE.json --since T0 --until T1
     python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py SAMPLE.json [--prelude PATH]
     python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py --self-test
diff --git a/dev/programme/delivery/3303.md b/dev/programme/delivery/3303.md
new file mode 100644
index 000000000..898b7dd07
--- /dev/null
+++ b/dev/programme/delivery/3303.md
@@ -0,0 +1 @@
+- [#3303](https://github.com/tvofi/heatpump_optimizer/pull/3303) — **open**, R10-CI-EDIT-RUNNER: ci edit runner (R10-CI-EDIT-RUNNER)
diff --git a/tests/closures.json b/tests/closures.json
index a71088377..a930c56b1 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3993,6 +3993,7 @@
    "dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py",
    "dev/audit/harnesses/r10_ci_layout_u6/unitcheck.sh",
    "dev/audit/harnesses/r10_ci_layout_u8/unitcheck.sh",
+   "dev/audit/harnesses/r10_ci_slim/body_defer.py",
    "dev/audit/harnesses/r10_ci_slim/c2_replay.py",
    "dev/audit/harnesses/r10_ci_slim/c7_replay.py",
    "dev/audit/harnesses/r10_ci_slim/edit_runs.py",
diff --git a/tests/entities.py b/tests/entities.py
index 890a94459..5bb568eda 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -29842,7 +29842,7 @@ _PT_EXEMPT = {
         "(`pr-contract` needs `tests`, so it is PENDING), whatever the token can see",
     "tools/ci/prelude.py":
         "on a pull_request code run, the only run graders-head-copy executes in, it makes no "
-        "API read (its reads are a dispatch's PR check and a non-code kind's wait)",
+        "API read (its reads are a dispatch's PR check, a body kind's deferral and a non-code kind's wait)",
     # pr-contract's code-scanning wait (U6): it reads runs, jobs and code-scanning
     # analyses and alerts, none of which graders-head-copy's token holds.
     "tools/ci/codescan_wait.py":
@@ -31849,8 +31849,9 @@ _PRW_SUBJECTS = sorted({d.split(" ", 1)[0] for d in _prw_defects(_PRW_UNDONE)})
 R.check(
     "and the same ci.yml and tests.yml with their restores and token hygiene undone are "
     "refused on each of the three autofix jobs (a workflow_call callee of a pull_request "
-    "workflow) and on ci.yml's cancel-superseded and refresh jobs (null control)",
-    _PRW_SUBJECTS == ["ci.yml:cancel-superseded", "ci.yml:refresh", "tests.yml:claims-autofix",
+    "workflow) and on ci.yml's cancel-superseded, gate (its `actions: write` re-runs a deferred "
+    "body run, R10-CI-EDIT-RUNNER) and refresh jobs (null control)",
+    _PRW_SUBJECTS == ["ci.yml:cancel-superseded", "ci.yml:gate", "ci.yml:refresh", "tests.yml:claims-autofix",
                       "tests.yml:closures-autofix", "tests.yml:mutation-autofix"],
     f"refused jobs on the undone copy: {_PRW_SUBJECTS}",
 )
diff --git a/tools/ci/gate.py b/tools/ci/gate.py
index b12882c1f..3ced42136 100644
--- a/tools/ci/gate.py
+++ b/tools/ci/gate.py
@@ -45,6 +45,12 @@ runs whose gates have both started are broken by id (`busy`): the lower decides,
 the higher defers to it. Where a lagging listing still makes two gates defer
 to each other, both are red, and settle re-runs both once each has concluded:
 a gate re-run after every source finished is final, so settle cannot loop.
+A deferring body run (prelude.defer_to, R10-CI-EDIT-RUNNER) ran no unit, so it
+publishes SELF_DEFERRED at once like any deferral, and the code run's gate, once
+that run is judging, re-runs it (`redispatch`) before it judges; the re-run's own
+attempt then replaces that red with a verdict. Every gate at the head defers to
+the latest deferring run of each kind (`pending`) as to a busy one, so no gate
+passes the head before its latest body and review are judged.
 """
 from __future__ import annotations
 
@@ -60,8 +66,8 @@ from pathlib import Path
 HERE = Path(__file__).resolve().parent
 sys.path.insert(0, str(HERE))                      # -I drops the script's directory
 import ghapi  # noqa: E402
-from prelude import (BODY_UNITS, CODE_UNITS, POLL_S, STARTED, UNITS, context, derive, judging, parse_title,  # noqa: E402,F401
-                     run_jobs, title, workset)
+from prelude import (BODY_KINDS, BODY_UNITS, CODE_UNITS, POLL_S, STARTED, UNITS, context, deferring,  # noqa: E402,F401
+                     derive, judging, parse_title, run_jobs, title, workset)
 
 PUSH_ONLY = {"tests": ("coverage", "coverage-ratchet", "ci-ratchet")}      # B3
 CODE = {u: UNITS[u] for u in CODE_UNITS}
@@ -128,6 +134,56 @@ def deferral(ids: list) -> str:
     return f"run(s) {ids} at this head are still being judged; their gate decides"
 
 
+# R10-CI-EDIT-RUNNER. A body run (edit, review) beside an unfinished code run
+# that is not judging runs no unit (prelude.defer_to). Until it is re-run it is
+# the latest event's unjudged body or review, so every gate at the head waits
+# on the latest such run of each kind (`pending`) as on a busy one, and the
+# code run's gate, the one gate that run's deferral names, re-runs it
+# (`redispatch`), at most once per judge(). The re-run's prelude finds that
+# code run judging, so it runs its full workset and waits on nothing. An
+# earlier deferring run of a kind is superseded by the latest: its event's
+# body or review is read again by the later run.
+SELF_DEFERRED = "this run deferred to an unfinished code run at this head, whose gate re-runs it"
+
+
+def pending(ctx: dict, runs: list[dict]) -> list:
+    """The ids of the latest run of each body kind for this PR, when that run is
+    deferring (prelude.deferring): owed a re-run, then a judgement. `runs`
+    includes this run itself when the caller wants it considered."""
+    _, pr, _ = derive(ctx)
+    latest: dict[str, dict] = {}
+    for r in runs:
+        t = parse_title(r.get("title") or "")
+        if pr and t is not None and t[0] in BODY_KINDS and t[1] == pr and r["id"] > latest.get(t[0], {"id": -1})["id"]:
+            latest[t[0]] = r
+    return sorted(r["id"] for r in latest.values() if r.get("status") != "action_required" and deferring(r))
+
+
+def waiting_on(ctx: dict, others: list[dict]) -> list:
+    """What this gate waits on: the busy runs and the pending deferred ones."""
+    return sorted(set(busy(ctx, others)) | set(pending(ctx, others)))
+
+
+def redispatch(ctx: dict, runs: list[dict], post, done: set) -> list[str]:
+    """A code run's gate re-runs each pending deferred run that has completed and
+    that this judge() has not re-run yet; the reasons a re-run failed."""
+    kind, pr, _ = derive(ctx)
+    if kind != "code" or not pr or post is None:
+        return []
+    bad = []
+    for r in runs:
+        if r["id"] in done or r["id"] not in pending(ctx, runs) or r.get("status") != "completed":
+            continue
+        done.add(r["id"])
+        if int(r.get("attempt", 1)) >= ATTEMPT_CAP:
+            bad.append(f"deferred run {r['id']} is at attempt {r['attempt']}, the cap: push a new commit")
+            continue
+        st, _, _ = post(f"repos/{ctx['repo']}/actions/runs/{r['id']}/rerun")
+        if st not in (201, 204):
+            bad.append(f"re-run of deferred run {r['id']}: HTTP {st}")
+    return bad
+
+
 OWN_PENDING = ": PENDING (this run)"
 OWN_ABSENT = ": ABSENT (this run)"
 
@@ -179,16 +235,18 @@ def gate(ctx: dict, api: dict) -> tuple[bool, list[str]]:
         if lp.get("same_repo") is not True:  # R3-4: no supersession or refresh reaches a fork head
             return False, [f"PR {pr}: its head is not in this repository (a fork PR is not gated here)"]
     others = [r for r in api["runs_at_head"] if r["id"] != ctx["run_id"]]
-    own = pre.get("workset")                # the units the prelude ran here; a deferring edit run ran fewer (C3)
-    waiting = busy(ctx, others)
+    own = pre.get("workset")                # the units the prelude ran here; a deferring body run ran none
+    me = {"id": ctx["run_id"], "title": title(kind, pr, base, ctx.get("sha", "")), "status": "completed",
+          "jobs": api["jobs"]}
+    waiting = waiting_on(ctx, others)
+    if kind in BODY_KINDS and own == set() and deferring(me) and (waiting or ctx["run_id"] in pending(ctx, others + [me])):
+        return False, [SELF_DEFERRED]       # never waits: the code run's gate re-runs the latest deferring run
     if waiting:
         return False, [deferral(waiting)]
     required: dict[str, list[str]] = {}
     for name in REQUIRED[event_class(ev, pr, api.get("reaches_cc"))]:
         u, n = name.split(" / ", 1)
         required.setdefault(u, []).append(n)
-    me = {"id": ctx["run_id"], "title": title(kind, pr, base, ctx.get("sha", "")), "status": "completed",
-          "jobs": api["jobs"]}
     for unit, names in required.items():
         src = None
         for r in sorted(others + [me], key=lambda r: r["id"], reverse=True):
@@ -245,6 +303,7 @@ def read_api(ctx: dict, claim: dict, reaches_cc, get) -> dict:
         api["open_pr_heads"] = {p["head"]["sha"] for p in ghapi.paginate(f"repos/{repo}/pulls", {"state": "open"}, get=get)}
     runs = ghapi.paginate(f"repos/{repo}/actions/workflows/ci.yml/runs", {"head_sha": ctx["head"]}, get=get)
     api["runs_at_head"] = [{"id": r["id"], "title": r.get("display_title") or "", "status": r["status"],
+                            "attempt": int(r.get("run_attempt") or 1),
                             "jobs": {} if r["status"] == "action_required" else run_jobs(get, repo, r["id"])}
                            for r in runs if r["id"] != ctx["run_id"]]
     return api
@@ -258,17 +317,20 @@ def reaches_custom_components(base: str, head: str) -> bool:
 
 
 def judge(ctx: dict, claim: dict, get, reaches=reaches_custom_components, sleep=time.sleep,
-          now=time.monotonic) -> tuple[str, list[str], list[str]]:
+          now=time.monotonic, post=None) -> tuple[str, list[str], list[str]]:
     """(outcome, reasons, this run's other jobs: reported, never gating). A verdict
     that only waits on this run's own lagging jobs (lag_bound) is never published
-    while its bound allows a re-read; a deferral is published at once (DEFERRAL)."""
+    while its bound allows a re-read; a deferral is published at once (DEFERRAL). A
+    code run's gate re-runs the deferred body runs it finds (`redispatch`, with
+    `post`) before it judges."""
     kind, pr, base = derive(ctx)
     cc = reaches(base, ctx["head"]) if pr else None     # git first; the API reads are last (R3-1)
-    t0, lagged = now(), []
+    t0, lagged, rerun = now(), [], set()
     while True:
         api = read_api(ctx, claim, cc, get)
-        ok, why = gate(ctx, api)
-        if ok or now() - t0 + POLL_S > lag_bound(why):   # a deferral's bound is 0: published at once
+        failed = redispatch(ctx, api["runs_at_head"], post, rerun)
+        ok, why = (False, failed) if failed else gate(ctx, api)
+        if ok or now() - t0 + POLL_S > (0 if failed else lag_bound(why)):   # a deferral's bound is 0: published at once
             break
         lagged = lagged or why
         sleep(POLL_S)
@@ -341,7 +403,7 @@ def main(argv: list[str], get=ghapi.get, post=ghapi.post, env=os.environ) -> int
         claim = {"kind": a.kind, "pr": a.pr}
         if env.get("WORKSET") is not None:          # the prelude's workset output (ci.yml's gate step)
             claim["workset"] = set(env["WORKSET"].split())
-        outcome, why, notes = judge(ctx, claim, get)
+        outcome, why, notes = judge(ctx, claim, get, post=post)
     except ghapi.RateLimited as e:
         outcome, why = f"RATE-LIMITED reset_epoch={e.reset_epoch} {e.path}", [str(e)]
         # The annotation is how the sweep tells this red from any other (check-runs/<job>/annotations).
@@ -640,6 +702,65 @@ def self_test() -> int:
           busy({**ctx, "run_id": 99}, [{**r, "title": r["display_title"],
                                         "jobs": {j["name"]: (j["status"], j["conclusion"]) for j in r["jobs"]}}
                                        for r in reds + [rerun]]), [])
+    # R10-CI-EDIT-RUNNER: a deferring body run ran no unit (prelude.defer_to); its
+    # gate never waits, and the code run's gate re-runs the latest one of each kind.
+    skipped = lambda kind: ([{"name": "prelude", "status": "completed", "conclusion": "success", "id": 1}]  # noqa: E731
+                            + [{"name": u, "status": "completed", "conclusion": "skipped", "id": 1}
+                               for u in sorted(workset(kind, "7") & set(UNITS))])
+    g_in = [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}]
+    g_red = [{"name": "gate", "status": "completed", "conclusion": "failure", "id": 9}]
+    nothing = {"kind": "edit", "pr": "7", "workset": set()}
+    get, naps, nap, now = scene(busy_code, mine=skipped("edit") + g_in, me=101)
+    check("edit-runner: a deferring edit gate beside a busy code run publishes at once, holding no runner",
+          (verdict({**ectx, "run_id": 101}, get, nap, now, nothing), naps), ("FAIL " + SELF_DEFERRED, []))
+    rctx = context("pull_request_review", {**ev, "action": "submitted"}, env)
+    get, naps, nap, now = scene(busy_code, mine=skipped("review") + g_in, me=102)
+    check("edit-runner: a deferring review gate beside a busy code run publishes at once",
+          (verdict({**rctx, "run_id": 102}, get, nap, now, {"kind": "review", "pr": "7", "workset": set()}), naps),
+          ("FAIL " + SELF_DEFERRED, []))
+
+    def code_scene(*frames):
+        posts = []
+        get, naps, nap, now = scene(*frames)
+        return get, naps, nap, now, posts, lambda path, body=None: (posts.append(path), (201, {}, None))[1]
+    gone = run(95, "edit", "completed", skipped("edit") + g_red)
+    e_done = run(101, "edit", "completed", skipped("edit") + g_red)
+    r_done = run(102, "review", "completed", skipped("review") + g_red)
+    get, naps, nap, now, posts, post = code_scene(
+        [gone, e_done, r_done],
+        [gone, run(101, "edit", "in_progress", owed("edit", gate=False, state="in_progress")),
+         run(102, "review", "queued", [])],
+        [gone, run(101, "edit", "in_progress", owed("edit")), run(102, "review", "in_progress", owed("review"))])
+    check("edit-runner: the code run's gate re-runs the latest deferring edit and review run once each, "
+          "then defers to them at once (the sweep re-judges it)",
+          (judge(ctx, claim, get, cc, nap, now, post)[0], posts, naps),
+          ("FAIL " + deferral([101, 102]), ["repos/o/r/actions/runs/101/rerun", "repos/o/r/actions/runs/102/rerun"], []))
+    get, naps, nap, now, posts, post = code_scene(
+        [gone, run(101, "edit", "in_progress", skipped("edit") + g_in)], [gone, e_done],
+        [gone, run(101, "edit", "in_progress", owed("edit"))])
+    check("edit-runner: a deferring run still at its own gate is deferred to at once, not yet re-run",
+          (judge(ctx, claim, get, cc, nap, now, post)[0], posts, naps), ("FAIL " + deferral([101]), [], []))
+    get, naps, nap, now, posts, post = code_scene([run(101, "edit", "completed", owed("edit")), gone])
+    check("edit-runner null: beside a finished edit run that ran its units, the code gate re-runs nothing, "
+          "judges at once", (judge(ctx, claim, get, cc, nap, now, post)[0], posts, naps), ("PASS", [], []))
+    get, naps, nap, now, posts, _ = code_scene([e_done])
+    check("edit-runner: a refused re-run is published at once, never a PASS",
+          (judge(ctx, claim, get, cc, nap, now, lambda path, body=None: (403, {}, None))[0], naps),
+          ("FAIL re-run of deferred run 101: HTTP 403", []))
+    get, naps, nap, now, posts, post = code_scene([{**e_done, "run_attempt": ATTEMPT_CAP}])
+    check("edit-runner: a deferred run at the attempt cap is not re-run",
+          (judge(ctx, claim, get, cc, nap, now, post)[0].startswith("FAIL deferred run 101 is at attempt"), posts),
+          (True, []))
+    get, naps, nap, now, posts, post = code_scene([e_done])
+    lctx = context("pull_request", {**ev, "action": "labeled", "label": {"name": "x"}}, env)
+    judge(lctx, {"kind": "label", "pr": "7"}, get, cc, nap, now, post)
+    check("edit-runner: only a code run's gate re-runs; another gate defers to the pending run at once",
+          (posts, naps), ([], []))
+    get, naps, nap, now = scene([run(99, "code", "completed", owed("code")),
+                                 run(110, "edit", "completed", owed("edit"))], mine=skipped("edit") + g_in, me=101)
+    check("edit-runner null: a superseded deferring gate re-run once nothing is pending judges like every "
+          "other gate (the sweep's re-run converges)",
+          (verdict({**ectx, "run_id": 101}, get, nap, now, nothing), naps), ("PASS", []))
     # r10-gate-busy-defer-2: replay recorded runs (#3263, #3261) through judge() as the API read then.
     fx = json.loads((HERE / "fixtures" / "gate_busy_defer_runs.json").read_text())
     frepo = fx["repo"]
diff --git a/tools/ci/prelude.py b/tools/ci/prelude.py
index f3b2e74a5..8979c29e4 100644
--- a/tools/ci/prelude.py
+++ b/tools/ci/prelude.py
@@ -23,8 +23,10 @@ WORKSET is the units a kind's run owns; a code run on a PR carrying the
 
 A dispatch naming `pr` is VERIFIED against the live PR (open, from this
 repository, headed by this SHA, based on `base`) or the prelude fails, and the
-gate, which re-verifies, fails with it. A non-code run waits (`wait_sources`)
-until no run at its head that it orders after can still add a source: every
+gate, which re-verifies, fails with it. A body run beside an unfinished,
+not-judging code run for its PR runs no unit and exits (`defer_to`); the code
+run's gate re-runs it (gate.redispatch). Otherwise a non-code run waits
+(`wait_sources`) until no run at its head that it orders after can still add a source: every
 EARLIER run and every CODE run, whatever its id (a held run aside). GitHub
 does not number a same-second push and body edit in event order
 (R10-RCA-CODESCAN-WAIT: the edit run got the lower id in 27 of 94 pairs), so
@@ -52,12 +54,12 @@ CODE_UNITS = ("tests", "codeql", "governance", "hassfest", "validate")
 BODY_UNITS = ("arch-score", "budget-raise-gate", "pr-contract")
 BODY_ON_EDIT = frozenset(BODY_UNITS)
 BODY_ON_REVIEW = frozenset({"budget-raise-gate"})  # owner variant: a review re-runs only budget-raise-gate
-# An edit run beside an unfinished code run whose pr-contract has not started
-# (R10-CI-SLIM card C3, option A): it judges these two against the live body at
-# once and holds no runner waiting; `pr-contract`, which reads the body off the
-# API when it starts and needs every unit first, is the code run's, so the
-# code run's gate judges the LATEST body.
-EDIT_UNDER_CODE = BODY_ON_EDIT - {"pr-contract"}
+# A body run (edit or review) beside an unfinished code run for its PR that is
+# not yet judging (R10-CI-EDIT-RUNNER, superseding R10-CI-SLIM card C3) runs no
+# unit and holds no runner waiting: its workset is empty, and the code run's
+# gate re-runs it once the code run is judging (gate.redispatch), when it reads
+# the live body and finds nothing to wait for.
+BODY_KINDS = ("edit", "review")
 STARTED = ("in_progress", "completed")
 # R10-CI-SLIM card C7(a): the machinery lanes (tests / arch-instrument, tests /
 # closures' recording, governance / env-matrix, governance /
@@ -188,8 +190,8 @@ def judging(run: dict) -> bool:
     `gate` is listed, no listed prelude or unit job is unfinished, and every name
     its own title's workset owes is listed and completed (`tests /
     closure-scope` aside when it names no PR), or its caller job is listed completed
-    under the unit's bare name: a unit the run never expanded, as a deferring edit
-    run's skipped `pr-contract` (C3), adds no source. Read as owed, it made every
+    under the unit's bare name: a unit the run never expanded, as every unit of a
+    deferring body run (`deferring`) or C3's skipped `pr-contract`, adds no source. Read as owed, it made every
     such run busy to every other gate and prelude at its head (#3263, run
     42338396358 beside code run 42338396871)."""
     jobs = run.get("jobs") or {}
@@ -260,10 +262,23 @@ def machinery(changed: "list[str] | None", closures_json: Path = CLOSURES_JSON)
     return not files or is_product is None or not all(map(is_product, files))
 
 
+def deferring(run: dict) -> bool:
+    """A body run that ran none of its units after a green prelude (`defer_to`
+    emptied its workset): every unit its title owes is listed as its bare,
+    never-expanded caller, completed and skipped. The code run's gate re-runs
+    the latest one of each kind (gate.redispatch)."""
+    t = parse_title(run.get("title") or "")
+    jobs = run.get("jobs") or {}
+    if t is None or t[0] not in BODY_KINDS or jobs.get("prelude") != ("completed", "success"):
+        return False
+    return all(jobs.get(u) == ("completed", "skipped") for u in workset(t[0], t[1]) & set(UNITS))
+
+
 def defer_to(ctx: dict, pr: str, get) -> "int | None":
-    """The unfinished code run at this head for `pr` whose `pr-contract` has not
-    started, or None. Its pr-contract will read the body after this edit, and its
-    gate is listed only after that, so it is the later verdict at this head."""
+    """An unfinished code run at this head for `pr` that is not judging, or None.
+    Its gate starts only once it is judging and then re-runs this run
+    (gate.redispatch), which reads the live body and review then, so this run
+    holds no runner meanwhile, whatever stage that code run is at."""
     st, _, doc = get(f"repos/{ctx['repo']}/actions/workflows/ci.yml/runs",
                      {"head_sha": ctx["head"], "per_page": 100})
     if st != 200 or not isinstance(doc, dict):
@@ -272,8 +287,7 @@ def defer_to(ctx: dict, pr: str, get) -> "int | None":
         t = parse_title(r.get("display_title") or "")
         if r["id"] == ctx["run_id"] or r["status"] not in UNFINISHED or t is None or t[:2] != ("code", pr):
             continue
-        contract = run_jobs(get, ctx["repo"], r["id"]).get("pr-contract / pr-contract")
-        if contract is None or contract[0] not in STARTED:
+        if not judging({"title": r.get("display_title") or "", "jobs": run_jobs(get, ctx["repo"], r["id"])}):
             return r["id"]
     return None
 
@@ -324,10 +338,10 @@ def outputs(ctx: dict, changed: list[str] | None, get, sleep=time.sleep, proof=p
     out["legs"] = json.dumps({leg: codeql_scope.decide(leg, ev, changed or [], ref, proven)[0]
                               for leg in codeql_scope.LEGS}, separators=(",", ":"))
     why = verify_dispatch(ctx, get) if ev == "workflow_dispatch" else ""
-    if not why and kind == "edit":
+    if not why and kind in BODY_KINDS and pr:
         try:
             if defer_to(ctx, pr, get) is not None:
-                out["workset"] = " ".join(sorted(EDIT_UNDER_CODE))
+                out["workset"] = ""
                 return out, ""
         except ghapi.ApiError as e:
             return out, str(e)
@@ -441,15 +455,16 @@ def self_test() -> int:
     get, _ = timeline([run(1, "code", "queued")])
     w = wait_sources(rctx, get, lambda s: None, lambda: next(clock))
     check("the wait is bounded", w.startswith("run(s) [1] still adding sources"), True)
-    # C3 (option A): an edit run beside a code run that has not started its
-    # pr-contract exits at once with the body units less pr-contract; beside one
-    # whose pr-contract has started, or a finished one, it waits as before.
+    # R10-CI-EDIT-RUNNER: an edit or review run beside an unfinished code run for
+    # its PR that is not yet judging exits at once with no unit and no poll; the
+    # code run's gate re-runs it (gate.redispatch). Beside a code run that is
+    # judging, or finished, it runs its full workset as before (null control).
     ectx = ctx("pull_request", action="edited", pull_request=pr)       # run 50
     in_units = [{"name": "prelude", "status": "completed", "conclusion": "success"},
                 {"name": "tests / fast (3.14)", "status": "in_progress", "conclusion": None}]
     contract = lambda st: in_units + [{"name": "pr-contract / pr-contract", "status": st, "conclusion": None}]  # noqa: E731
 
-    def edit_out(*frames):
+    def body_out(c, *frames):
         get, naps = timeline(*frames)
 
         def nap(s):                         # bounded: a wait the frames never end is a failed check, not a hang
@@ -459,37 +474,54 @@ def self_test() -> int:
 
         def run_it():
             try:
-                return outputs(ectx, None, lambda path, params=None: (200, {}, live) if "/pulls/" in path
+                return outputs(c, None, lambda path, params=None: (200, {}, live) if "/pulls/" in path
                                else get(path, params), nap)
             except TimeoutError as e:
                 return {"workset": f"UNBOUNDED: {e}"}, ""
         return run_it, naps
+    edit_out = lambda *frames: body_out(ectx, *frames)  # noqa: E731
     f, naps = edit_out([run(40, "code", "in_progress", in_units)])
-    check("C3: beside a code run in its units, the edit run exits at once without pr-contract",
-          ((lambda o: (o[0]["workset"], o[1]))(f()), naps), (("arch-score budget-raise-gate", ""), []))
+    check("defer: beside a code run in its units, the edit run exits at once running no unit",
+          ((lambda o: (o[0]["workset"], o[1]))(f()), naps), (("", ""), []))
     f, naps = edit_out([run(40, "code", "queued", [])])
-    check("C3: beside a queued code run (nothing listed), it exits at once", (f()[0]["workset"], naps),
-          ("arch-score budget-raise-gate", []))
-    f, naps = edit_out([run(40, "code", "in_progress", contract("queued"))])
-    check("C3: a queued pr-contract has not read the body: exits at once", (f()[0]["workset"], naps),
-          ("arch-score budget-raise-gate", []))
+    check("defer: beside a queued code run (nothing listed), it exits at once", (f()[0]["workset"], naps), ("", []))
     f, naps = edit_out([run(40, "code", "in_progress", contract("in_progress"))],
                        [run(40, "code", "in_progress", done("code"))])
-    check("C3: beside a started pr-contract (it may have read the old body) the edit run waits and owns pr-contract",
-          ((lambda o: (o[0]["workset"], o[1]))(f()), naps), (("arch-score budget-raise-gate pr-contract", ""), [POLL_S]))
+    check("defer: beside a started pr-contract the edit run exits within one poll (no wait)",
+          ((lambda o: (o[0]["workset"], o[1]))(f()), naps), (("", ""), []))
+    f, naps = edit_out([run(60, "code", "in_progress", in_units)])
+    check("defer: a LATER-numbered code run defers it too (ids order nothing)", (f()[0]["workset"], naps), ("", []))
+    f, naps = edit_out([run(40, "code", "in_progress", done("code"))])
+    check("null: beside a JUDGING code run (its gate redispatches nothing more), the full edit workset, no wait",
+          ((lambda o: o[0]["workset"])(f()), naps), ("arch-score budget-raise-gate pr-contract", []))
     f, naps = edit_out([run(40, "code", "completed", done("code"))])
-    check("C3: beside a finished code run, the full edit workset and no wait", ((lambda o: o[0]["workset"])(f()), naps),
+    check("null: beside a finished code run, the full edit workset and no wait", ((lambda o: o[0]["workset"])(f()), naps),
           ("arch-score budget-raise-gate pr-contract", []))
     other = title("code", "8", "main", "M")
     f, naps = edit_out([{**run(40, "code", "in_progress", in_units), "display_title": other}],
                        [{**run(40, "code", "in_progress", done("code")), "display_title": other}])
-    check("C3: a code run for another PR at this head is no deferral; it is waited on (null control)",
+    check("null: a code run for another PR at this head is no deferral; it is waited on",
           (f()[0]["workset"], naps), ("arch-score budget-raise-gate pr-contract", [POLL_S]))
     f, naps = edit_out([run(40, "edit", "in_progress", in_units)], [run(40, "edit", "in_progress", done("edit"))])
-    check("C3: an unfinished EDIT run is no deferral; it is waited on as before", (f()[0]["workset"], naps),
+    check("null: an unfinished EDIT run is no deferral; it is waited on as before", (f()[0]["workset"], naps),
           ("arch-score budget-raise-gate pr-contract", [POLL_S]))
-    check("C3: a review run never defers (only an edit does)",
-          outputs(rctx, None, timeline([run(40, "code", "in_progress", done("code"))])[0])[0]["workset"], "budget-raise-gate")
+    f, naps = body_out(rctx, [run(40, "code", "in_progress", contract("in_progress"))],
+                       [run(40, "code", "in_progress", done("code"))])
+    check("defer: a review run beside an unfinished code run exits within one poll, running no unit",
+          ((lambda o: (o[0]["workset"], o[1]))(f()), naps), (("", ""), []))
+    f, naps = body_out(rctx, [run(40, "code", "completed", done("code"))])
+    check("null: a review run beside a finished code run grades as before",
+          ((lambda o: o[0]["workset"])(f()), naps), ("budget-raise-gate", []))
+    check("deferring: a run that ran none of its units after a green prelude",
+          [deferring({"title": title(k, "7", "main"), "jobs": j}) for k, j in (
+              ("edit", {"prelude": ("completed", "success"), **{u: ("completed", "skipped") for u in BODY_UNITS}}),
+              ("review", {"prelude": ("completed", "success"), "budget-raise-gate": ("completed", "skipped")}),
+              ("edit", {"prelude": ("completed", "failure"), **{u: ("completed", "skipped") for u in BODY_UNITS}}),
+              ("edit", {"prelude": ("completed", "success"), "arch-score / arch-score": ("completed", "success"),
+                        "budget-raise-gate": ("completed", "skipped"), "pr-contract": ("completed", "skipped")}),
+              ("code", {"prelude": ("completed", "success"), **{u: ("completed", "skipped") for u in CODE_UNITS}}),
+              ("edit", {"prelude": ("in_progress", None)}))],
+          [True, True, False, False, False, False])
     # C7(a): the machinery lanes stand down only on an all-product pull request.
     import tempfile
     with tempfile.TemporaryDirectory() as td:

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
