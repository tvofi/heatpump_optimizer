# Review packet #3905
head: 7f4028cb65588d1dde4213e27f4e402b0bcf66fd
base: 3ee06864daf26f75a1da135b437c4884a6aff341

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139661104051 success
arch-score / arch-score id=139660878701 success
arm id=139660037218 skipped
budget-raise-gate / budget-raise-gate id=139660878761 success
cancel-superseded id=139660079929 success
codeql id=139660880456 skipped
codeql / Analyze (actions) id=139660546534 success
codeql / Analyze (javascript-typescript) id=139660546619 success
codeql / Analyze (python) id=139660546657 success
gate id=139662243916 failure
governance id=139660880752 skipped
governance / env-matrix id=139660546600 success
governance / instrument-self-tests id=139660546604 success
governance / policy-docs id=139660546589 success
governance / record id=139660548553 skipped
governance / wave-script id=139660546627 success
hassfest id=139660880825 skipped
hassfest / hassfest id=139660546590 success
kernel-points id=139660880205 skipped
pr-contract id=139662245222 skipped
pr-contract / pr-contract id=139678834559 queued
prelude id=139660080329 success
refresh id=139660080465 success
sweep-self id=139663145219 skipped
tests id=139660880123 skipped
tests / arch-instrument id=139661070037 success
tests / briefs id=139660546499 success
tests / browser id=139661069956 success
tests / ci-ratchet id=139676622928 skipped
tests / claims-autofix id=139676621403 success
tests / closure-scope id=139660546483 success
tests / closures id=139661070014 success
tests / closures-autofix id=139673587270 skipped
tests / coverage id=139661070040 success
tests / coverage-ratchet id=139671723952 success
tests / fast (3.14) id=139661070068 failure
tests / graders-head-copy id=139671723951 success
tests / lane-proofs id=139676906759 success
tests / mutation id=139660546484 success
tests / mutation-autofix id=139661000431 skipped
tests / mutation-pins id=139660999298 skipped
tests / nightly-ha id=139661072153 skipped
tests / nightly-status id=139660546497 failure
tests / replay id=139661071364 skipped
tests / typing id=139661070020 success
validate id=139660880977 skipped
validate / validate-hacs id=139660546479 success

## Refusals
structure: tests/structure.py refuses the head merged with main: head does not merge cleanly with origin/main: ['100644 452c2f17c4dadfe1f6092fe3821df401e7331d94 1\t.github/workflows/ci.yml', '100644 0c108be76d0f0899b469ebe56575e6d46f99b1b0 2\t.github/workflows/ci.yml']
red-unanswered: concluded red check `tests / fast (3.14)` is not named in ## Red checks

## Advisories
required-wait: required context `gate` reads concluded failure at 7f4028cb65588d1dde4213e27f4e402b0bcf66fd in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/harnesses/ci3885_queue.py report 2026-11-25 --cache DIR
             `dev/audit/harnesses/ci3885_queue.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/ci3885_queue.py report 2026-11-24 --cache DIR
             `dev/audit/harnesses/ci3885_queue.py` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head 7f4028cb65588d1dde4213e27f4e402b0bcf66fd, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 452c2f17c4..e738de70a2 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -66,15 +66,21 @@ permissions: {}
 
 # A group per run (rev2, N1): `refresh` and gate-sweep.yml re-run `gate` jobs,
 # and a re-run re-enters its run's group, so a group shared between runs would
-# let a re-run cancel a pending run. Supersession is cancel-superseded's alone.
+# let a re-run cancel a pending run. Except a `synchronize` run's first attempt
+# sent by anyone but github-actions[bot] (#3885 L1): it joins its pull request's
+# `CI-pr-<number>` group and cancels the older such run at creation, pending or
+# in progress. A synchronize always heads a new SHA, so no same-head twin is
+# cancelled; a re-run keeps its run-id group; a bot-sent run (an autofix push)
+# never cancels the run doing the other autofix jobs. Every other superseded run
+# (opened, reopened, dispatched, bot-sent) is the `cancel-superseded` job's.
 # Except a push to main's first attempt (CI-5, owner 2026-11-21): one `CI-main`
 # group, cancelling nothing in progress, so one push run executes at a time and
 # GitHub replaces a pending one with the newest before it starts; a burst of
 # merges is graded once, at its last tip, and no started run is cancelled. A
 # re-run (attempt 2+) keeps its run-id group, so it never displaces that tip.
 concurrency:
-  group: ${{ github.event_name == 'push' && github.run_attempt == '1' && 'CI-main' || format('CI-{0}', github.run_id) }}
-  cancel-in-progress: false
+  group: ${{ github.event_name == 'push' && github.run_attempt == '1' && 'CI-main' || github.event_name == 'pull_request' && github.event.action == 'synchronize' && github.run_attempt == '1' && github.event.sender.login != 'github-actions[bot]' && format('CI-pr-{0}', github.event.pull_request.number) || format('CI-{0}', github.run_id) }}
+  cancel-in-progress: ${{ github.event_name == 'pull_request' && github.event.action == 'synchronize' && github.run_attempt == '1' && github.event.sender.login != 'github-actions[bot]' }}
 
 jobs:
   prelude:
diff --git a/dev/audit/harnesses/ci3885_queue.py b/dev/audit/harnesses/ci3885_queue.py
new file mode 100644
index 0000000000..b6d7dc825c
--- /dev/null
+++ b/dev/audit/harnesses/ci3885_queue.py
@@ -0,0 +1,344 @@
+#!/usr/bin/env python3
+"""#3885 queue group (R11-CI-3885-QUEUE): where the account's concurrent-job slots go.
+
+    python3 dev/audit/harnesses/ci3885_queue.py fetch DAY [--cache DIR]
+    python3 dev/audit/harnesses/ci3885_queue.py report DAY [--cache DIR] [--keep-copies]
+
+`fetch` lists every workflow run created on DAY (UTC) and every job of every
+attempt of each (`/actions/runs/{id}/jobs?filter=all`), and caches both as
+JSON under DIR (default $TMPDIR/ci3885_queue). `report` reads the cache only,
+so a re-read costs no API call, and prints one JSON object, a key per arm:
+
+  census      per workflow: runs, runs that held a runner (a job with a
+              started_at and conclusion other than skipped), runner-minutes
+              (started_at..completed_at over every non-skipped job, every
+              attempt), and the day's peak concurrent jobs (the cap as seen).
+  queue       per job: started_at - created_at, p50/p90/max, all jobs and
+              by hour; and for CI runs, run created -> first job started.
+  e2e         CI runs whose latest `gate` concluded: created -> gate completed.
+  sweep       Gate sweep runs: how many held a runner, their minutes and queue
+              wait; the triggering CI attempt is not on the run object, so a
+              sweep is attributed to the CI run that completed at its head
+              closest before it (same head_sha).
+  supersede   CI pull_request/dispatch runs on a branch: minutes their jobs ran
+              after a NEWER head's CI run on the same branch was created (waste
+              a cancel at creation saves), and minutes of jobs that never
+              started before that moment (queue slots a cancel frees).
+  rerun       jobs of attempt >= 2 whose same-named job concluded success in
+              the previous attempt (a whole-run re-run), minutes; excluding
+              `gate` and `sweep-self`, which sweep/refresh re-run on purpose.
+  record      CI runs on record/* (and other non-fix) branches, minutes.
+  prelude     prelude job minutes by run kind (title), the wait_sources share.
+
+NULL CONTROLS (each arm's predicate applied where it must read ~0):
+  supersede-null  the same arm with "newer head" replaced by "same head_sha"
+                  restricted to code runs: twins are never superseded, so the
+                  arm must not count a run against its own head.
+  rerun-null      attempt-1 jobs read as re-runs: must be 0 by construction of
+                  the previous-attempt lookup.
+  queue-null      the queue arm on a quiet day (pass that day): waits near 0.
+"""
+from __future__ import annotations
+
+import argparse
+import collections
+import datetime as dt
+import json
+import os
+import subprocess
+import sys
+import time
+from pathlib import Path
+
+REPO = "tvofi/heatpump_optimizer"
+
+
+def ts(s):
+    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
+
+
+def gh(path):
+    for attempt in range(4):                       # a 502 from the API is retried, never counted
+        out = subprocess.run(["gh", "api", "--paginate", path], capture_output=True, text=True)
+        if out.returncode == 0:
+            break
+        time.sleep(5 * (attempt + 1))
+    else:
+        raise SystemExit(f"gh api {path}: {out.stderr.strip()}")
+    # --paginate concatenates JSON objects; split them
+    dec, i, docs, s = json.JSONDecoder(), 0, [], out.stdout
+    while i < len(s):
+        while i < len(s) and s[i].isspace():
+            i += 1
+        if i >= len(s):
+            break
+        d, i = dec.raw_decode(s, i)
+        docs.append(d)
+    return docs
+
+
+def cache_dir(a):
+    d = Path(a.cache or os.path.join(os.environ.get("TMPDIR", "/tmp"), "ci3885_queue"))
+    d.mkdir(parents=True, exist_ok=True)
+    return d
+
+
+def fetch(a):
+    d = cache_dir(a)
+    runs = []
+    for doc in gh(f"repos/{REPO}/actions/runs?created={a.day}&per_page=100"):
+        runs += doc["workflow_runs"]
+    keep = [{k: r.get(k) for k in ("id", "name", "event", "head_branch", "head_sha", "status",
+                                   "conclusion", "created_at", "run_started_at", "updated_at",
+                                   "run_attempt", "display_title")} | {"actor": r["actor"]["login"]}
+            for r in runs]
+    jobs = {}
+    for r in keep:
+        js = []
+        for doc in gh(f"repos/{REPO}/actions/runs/{r['id']}/jobs?filter=all&per_page=100"):
+            js += [{k: j.get(k) for k in ("id", "name", "run_attempt", "status", "conclusion",
+                                          "created_at", "started_at", "completed_at")}
+                   for j in doc["jobs"]]
+        jobs[str(r["id"])] = js
+    (d / f"{a.day}.json").write_text(json.dumps({"runs": keep, "jobs": jobs}))
+    print(f"cached {len(keep)} runs, {sum(map(len, jobs.values()))} jobs -> {d / (a.day + '.json')}")
+
+
+def ran(j):
+    return j["conclusion"] not in (None, "skipped") and j["started_at"] and j["completed_at"] \
+        and ts(j["completed_at"]) > ts(j["started_at"])
+
+
+def mins(j):
+    return (ts(j["completed_at"]) - ts(j["started_at"])).total_seconds() / 60
+
+
+def pct(xs, p):
+    xs = sorted(xs)
+    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else 0
+
+
+def kind(r):
+    t = (r.get("display_title") or "").split()
+    return t[1] if r["name"] .startswith("CI") and len(t) > 1 else r["name"]
+
+
+def wf(r):
+    return "CI" if r["name"].startswith("CI ") else r["name"]
+
+
+def report(a):
+    data = json.loads((cache_dir(a) / f"{a.day}.json").read_text())
+    runs, jobs = data["runs"], {int(k): v for k, v in data["jobs"].items()}
+    # A re-run of one job lists EVERY job again under the new attempt, the untouched ones as
+    # copies carrying the earlier attempt's timestamps: counted, they read 1,303 copied jobs
+    # (2026-11-25) as executed re-runs. A job executed once is kept at its first attempt only.
+    out = {}
+    copies = 0
+    for rid, js in jobs.items():
+        seen, keep = set(), []
+        for j in sorted(js, key=lambda j: j["run_attempt"]):
+            key = (j["name"], j["started_at"], j["completed_at"])
+            if j["run_attempt"] > 1 and key in seen and not a.keep_copies:
+                copies += 1
+                continue
+            seen.add(key)
+            keep.append(j)
+        jobs[rid] = keep
+    out["copied_jobs_dropped"] = copies
+
+    # census
+    c = collections.defaultdict(lambda: [0, 0, 0.0, 0])
+    edges = []
+    for r in runs:
+        js = [j for j in jobs[r["id"]] if ran(j)]
+        e = c[wf(r)]
+        e[0] += 1
+        e[1] += bool(js)
+        e[2] += sum(map(mins, js))
+        e[3] += len(js)
+        for j in js:
+            edges += [(ts(j["started_at"]), 1), (ts(j["completed_at"]), -1)]
+    peak = cur = 0
+    for _, s in sorted(edges, key=lambda x: (x[0], x[1])):
+        cur += s
+        peak = max(peak, cur)
+    out["census"] = {k: {"runs": v[0], "held_runner": v[1], "runner_min": round(v[2]), "jobs": v[3]}
+                     for k, v in sorted(c.items(), key=lambda x: -x[1][2])}
+    out["peak_concurrent_jobs"] = peak
+
+    # queue
+    waits, byhour = [], collections.defaultdict(list)
+    for r in runs:
+        for j in jobs[r["id"]]:
+            if ran(j):
+                w = (ts(j["started_at"]) - ts(j["created_at"])).total_seconds() / 60
+                waits.append(w)
+                byhour[j["created_at"][11:13]].append(w)
+    out["queue"] = {"jobs": len(waits), "p50_min": round(pct(waits, .5), 1), "p90_min": round(pct(waits, .9), 1),
+                    "max_min": round(max(waits or [0]), 1),
+                    "by_hour_p90": {h: round(pct(v, .9)) for h, v in sorted(byhour.items())}}
+
+    # e2e
+    e2e, first = [], []
+    for r in runs:
+        if wf(r) != "CI":
+            continue
+        js = jobs[r["id"]]
+        st = [ts(j["started_at"]) for j in js if j["run_attempt"] == 1 and ran(j)]
+        if st:
+            first.append((min(st) - ts(r["created_at"])).total_seconds() / 60)
+        g = [j for j in js if j["name"] == "gate" and j["run_attempt"] == 1 and j["completed_at"]
+             and j["conclusion"] not in ("skipped", "cancelled")]
+        if g:
+            e2e.append(((ts(g[0]["completed_at"]) - ts(r["created_at"])).total_seconds() / 60, kind(r)))
+    # decompose: where a run's wall clock goes. pending = run created -> first job CREATED
+    # (a concurrency group holding the run; no runner involved); queue = the run's longest
+    # job created -> started (the account's runner cap); longest = its longest job's run time.
+    dec = collections.defaultdict(lambda: collections.defaultdict(list))
+    for r in runs:
+        if wf(r) != "CI":
+            continue
+        js = [j for j in jobs[r["id"]] if j["run_attempt"] == 1]
+        g = [j for j in js if j["name"] == "gate" and j["completed_at"] and j["conclusion"] not in ("skipped", "cancelled")]
+        if not js or not g:
+            continue
+        k = f"{r['event']}:{kind(r)}"
+        dec[k]["pending"].append((min(ts(j["created_at"]) for j in js) - ts(r["created_at"])).total_seconds() / 60)
+        q = [(ts(j["started_at"]) - ts(j["created_at"])).total_seconds() / 60 for j in js if ran(j)]
+        dec[k]["queue_max"].append(max(q or [0]))
+        dec[k]["longest_job"].append(max([mins(j) for j in js if ran(j) and j["name"] != "prelude"] or [0]))
+        dec[k]["prelude"].append(max([mins(j) for j in js if j["name"] == "prelude" and ran(j)] or [0]))
+        dec[k]["e2e"].append((ts(g[0]["completed_at"]) - ts(r["created_at"])).total_seconds() / 60)
+    out["decompose_p50_p90"] = {k: {m: [round(pct(v, .5)), round(pct(v, .9)), len(v)] for m, v in d.items()}
+                                for k, d in sorted(dec.items())}
+    for k in sorted({x[1] for x in e2e}):
+        v = [x[0] for x in e2e if x[1] == k]
+        out.setdefault("e2e_by_kind", {})[k] = {"n": len(v), "p50_min": round(pct(v, .5)), "p90_min": round(pct(v, .9))}
+    out["ci_first_job_wait"] = {"n": len(first), "p50_min": round(pct(first, .5)), "p90_min": round(pct(first, .9)),
+                                "max_min": round(max(first or [0]))}
+
+    # sweep
+    sw = [r for r in runs if r["name"] == "Gate sweep"]
+    held = [j for r in sw for j in jobs[r["id"]] if ran(j)]
+    ci_runs = [r for r in runs if wf(r) == "CI"]
+    attempt2 = 0
+    for r in sw:
+        cands = [x for x in ci_runs if x["head_sha"] == r["head_sha"] and ts(x["updated_at"]) <= ts(r["created_at"])]
+        if cands and max(cands, key=lambda x: x["updated_at"])["run_attempt"] > 1:
+            attempt2 += 1
+    out["sweep"] = {"runs": len(sw), "held_runner": len(held), "runner_min": round(sum(map(mins, held))),
+                    "p50_job_min": round(pct([mins(j) for j in held], .5), 1),
+                    "p90_job_min": round(pct([mins(j) for j in held], .9), 1),
+                    "after_ci_attempt_ge2": attempt2,
+                    "queue_p90_min": round(pct([(ts(j["started_at"]) - ts(j["created_at"])).total_seconds() / 60
+                                                for j in held], .9))}
+
+    # supersede (and its null)
+    def supersede(same):
+        waste = slot = 0.0
+        n = 0
+        pr = [r for r in ci_runs if r["event"] in ("pull_request", "workflow_dispatch") and r["head_branch"] != "main"]
+        for r in pr:
+            newer = [x for x in pr if x["head_branch"] == r["head_branch"] and x["id"] > r["id"]
+                     and ((x["head_sha"] == r["head_sha"] and kind(x) == "code" and kind(r) == "code") if same
+                          else x["head_sha"] != r["head_sha"])]
+            if not newer:
+                continue
+            t = min(ts(x["created_at"]) for x in newer)
+            hit = False
+            for j in jobs[r["id"]]:
+                if not ran(j):
+                    continue
+                s, e = ts(j["started_at"]), ts(j["completed_at"])
+                if e > t:
+                    waste += (e - max(s, t)).total_seconds() / 60
+                    hit = True
+                    if s > t:
+                        slot += 1
+            n += hit
+        return {"runs": n, "runner_min_after_newer_head": round(waste), "jobs_started_after_newer_head": int(slot)}
+    out["supersede"] = supersede(False)
+    out["supersede_null_same_head_code"] = supersede(True)
+
+    # rerun (and its null)
+    def rerun(null):
+        m, n, gate_m = 0.0, 0, 0.0
+        for r in runs:
+            js = jobs[r["id"]]
+            prev = {(j["name"], j["run_attempt"]): j for j in js}
+            for j in js:
+                if not ran(j) or (j["run_attempt"] != 1 if null else j["run_attempt"] < 2):
+                    continue
+                p = prev.get((j["name"], j["run_attempt"] - 1))
+                if p and p["conclusion"] == "success":
+                    if j["name"] in ("gate", "sweep-self"):
+                        gate_m += mins(j)
+                    else:
+                        m += mins(j)
+                        n += 1
+        return {"jobs": n, "runner_min": round(m), "gate_rejudge_min": round(gate_m)}
+    out["rerun_of_success"] = rerun(False)
+    out["rerun_null_attempt1"] = rerun(True)
+    att = collections.Counter(r["run_attempt"] for r in ci_runs)
+    out["ci_attempts"] = dict(sorted(att.items()))
+
+    # record
+    rec = collections.defaultdict(lambda: [0, 0.0])
+    for r in ci_runs:
+        b = (r["head_branch"] or "").split("/")[0]
+        rec[b][0] += 1
+        rec[b][1] += sum(mins(j) for j in jobs[r["id"]] if ran(j))
+    out["ci_by_branch_prefix"] = {k: {"runs": v[0], "runner_min": round(v[1])} for k, v in rec.items()}
+
+    # prelude
+    pre = collections.defaultdict(list)
+    for r in ci_runs:
+        for j in jobs[r["id"]]:
+            if j["name"] == "prelude" and ran(j):
+                pre[kind(r)].append(mins(j))
+    out["prelude"] = {k: {"n": len(v), "runner_min": round(sum(v)), "p50_min": round(pct(v, .5), 1),
+                          "p90_min": round(pct(v, .9), 1), "max_min": round(max(v), 1)} for k, v in pre.items()}
+    # job-name totals for CI
+    jn = collections.Counter()
+    for r in ci_runs:
+        for j in jobs[r["id"]]:
+            if ran(j):
+                jn[j["name"].split(" / ")[0]] += mins(j)
+    out["ci_minutes_by_unit"] = {k: round(v) for k, v in jn.most_common(15)}
+
+    # waits: runner-minutes a job held beyond its own no-wait floor (the day's p10 of that
+    # job's duration): the in-job polls and sleeps. The NULL rows are jobs with no wait in
+    # them (a compile/lint step): their excess is run-time spread, the arm's noise floor.
+    WAITERS = {"prelude": "prelude wait_sources (edit) / review", "gate": "gate judge lag wait",
+               "sweep": "Gate sweep poll/settle", "sweep-self": "sweep-self poll/settle",
+               "pr-contract / pr-contract": "pr-contract codescan_wait", "refresh": "refresh (no wait)",
+               "hassfest / hassfest": "NULL hassfest", "tests / typing": "NULL typing",
+               "validate / validate-hacs": "NULL validate"}
+    w = collections.defaultdict(list)
+    for r in runs:
+        for j in jobs[r["id"]]:
+            if ran(j) and j["name"] in WAITERS:
+                w[j["name"]].append((mins(j), kind(r)))
+    out["waits"] = {}
+    for name, v in w.items():
+        floor = pct([m for m, _ in v], .1)
+        excess = [max(0.0, m - floor) for m, _ in v]
+        out["waits"][WAITERS[name]] = {"n": len(v), "runner_min": round(sum(m for m, _ in v)), "floor_min": round(floor, 2),
+                                       "excess_min": round(sum(excess)), "jobs_over_5min_excess": sum(e > 5 for e in excess)}
+    print(json.dumps(out, indent=1))
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    ap.add_argument("cmd", choices=("fetch", "report"))
+    ap.add_argument("day")
+    ap.add_argument("--cache")
+    ap.add_argument("--keep-copies", action="store_true",
+                    help="the perturbation: count re-run listings' copied jobs as executed")
+    a = ap.parse_args()
+    (fetch if a.cmd == "fetch" else report)(a)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/programme/delivery/3905.md b/dev/programme/delivery/3905.md
new file mode 100644
index 0000000000..08891bf047
--- /dev/null
+++ b/dev/programme/delivery/3905.md
@@ -0,0 +1 @@
+- [#3905](https://github.com/tvofi/heatpump_optimizer/pull/3905) — **open**, ci: a PR synchronize run cancels the older one at creation (#3885 L1) (R11-CI-3885-QUEUE)
diff --git a/tests/closures.json b/tests/closures.json
index 7ac8283787..2fee9a7ceb 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4642,6 +4642,7 @@
    "dev/audit/harnesses/ci-version-edit/pr_contract_shapes.py",
    "dev/audit/harnesses/ci-version-edit/recheck_stamp_forgery.py",
    "dev/audit/harnesses/ci3885_light.py",
+   "dev/audit/harnesses/ci3885_queue.py",
    "dev/audit/harnesses/ci_script_seconds.py",
    "dev/audit/harnesses/claim_merge_census.py",
    "dev/audit/harnesses/claim_merge_mutants.py",
diff --git a/tests/entities.py b/tests/entities.py
index 50b1b588fd..41523b0949 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -21557,7 +21557,9 @@ R.check(
 #     for every modelled event (on `merge_group` with `pr=- base=-`, which no
 #     expression can cut from the queue ref), so a past run's kind, PR, base
 #     and `sha=` read back as the prelude derived them;
-#   - one run per concurrency group, cancelling nothing (rev2, N1);
+#   - one run per concurrency group (rev2, N1), but a push's first attempt
+#     (CI-main, CI-5, cancelling nothing) and a non-bot `synchronize`'s first
+#     attempt (CI-pr-<number>, #3885 L1, cancelling the PR's older one);
 #   - the callers are gate.py's UNITS plus kernel-points, each `uses:` its
 #     own stem (the naming rule), all inside the `# >>> units` block the
 #     coordinator cuts a probe from, each run exactly when the prelude's
@@ -21647,8 +21649,9 @@ _CI_EVENTS = {
 
 def _ci_ctx(ev: str, payload: dict, outputs=None, actor="hpo-author[bot]") -> "tuple[dict, dict]":
     """(the expression context, prelude.context's) for one modelled event;
-    `outputs` are the prelude's: a failed prelude's read as empty strings."""
-    flat = _ghx_flat("github.event", payload, {})
+    `outputs` are the prelude's: a failed prelude's read as empty strings.
+    The event's sender is `actor` unless the payload names one."""
+    flat = _ghx_flat("github.event", {"sender": {"login": actor}, **payload}, {})
     flat.update({"github.event_name": ev, "github.sha": _CI_SHA, "github.run_id": 99,
                  "github.repository": "o/r", "github.actor": actor})
     flat.update({f"inputs.{k}": v for k, v in (payload.get("inputs") or {}).items()})
@@ -21726,17 +21729,27 @@ def _ci_umbrella_defects(doc: dict, text: str) -> "list[str]":
     if doc.get("permissions") != {}:
         out.append(f"workflow permissions {doc.get('permissions')!r}")
     # CI-5 (owner 2026-11-21): a push's first attempt joins the one CI-main group, so a pending
-    # push run is replaced by the newest and none in progress is cancelled; every other run and
-    # every re-run keeps its run-id group (N1). Rendered per event and attempt, not matched as text.
+    # push run is replaced by the newest and none in progress is cancelled. #3885 L1: a
+    # `synchronize` run's first attempt, sent by anyone but github-actions[bot], joins its pull
+    # request's CI-pr-<number> group and cancels the older run there at creation. Every other
+    # run and every re-run keeps its run-id group (N1: a re-run never cancels a pending run), and
+    # a bot-sent run never cancels the run doing the other autofix jobs (cancel_superseded.BOT).
+    # Rendered per event, attempt and sender, not matched as text.
     cc = doc.get("concurrency") or {}
-    if cc.get("cancel-in-progress") is not False:
-        out.append(f"concurrency {cc} cancels in progress")
     for (ev, a), payload in _CI_EVENTS.items():
         for attempt in ("1", "2"):
-            want = "CI-main" if ev == "push" and attempt == "1" else "CI-99"
-            got = _ghx(cc.get("group", ""), {**_ci_ctx(ev, payload)[0], "github.run_attempt": attempt})
-            if got != want:
-                out.append(f"concurrency group under {ev}/{a} attempt {attempt} renders {got!r}, want {want!r}")
+            for sender in ("hpo-author[bot]", "tvofi", _SELF_ACTOR):
+                ctx = {**_ci_ctx(ev, payload, actor=sender)[0], "github.run_attempt": attempt}
+                pr_group = (ev, a, attempt) == ("pull_request", "synchronize", "1") and sender != _SELF_ACTOR
+                want = "CI-main" if ev == "push" and attempt == "1" else "CI-pr-7" if pr_group else "CI-99"
+                got = _ghx(cc.get("group", ""), ctx)
+                if got != want:
+                    out.append(f"concurrency group under {ev}/{a} attempt {attempt} sender {sender} "
+                               f"renders {got!r}, want {want!r}")
+                cancels = _ghx(cc.get("cancel-in-progress", False), ctx)
+                if cancels is not pr_group:
+                    out.append(f"concurrency under {ev}/{a} attempt {attempt} sender {sender} "
+                               f"cancel-in-progress reads {cancels!r}, want {pr_group}")
     jobs = doc.get("jobs") or {}
     callers = {j for j, b in jobs.items() if "uses" in (b or {})}
     if callers != set(_cig.UNITS) | {_cip.KP}:
@@ -21847,9 +21860,23 @@ _CI_PLANTS = {
                                        "format('CI-{0}', github.event.pull_request.number)", 1),
     "push re-runs in the main group": _CI_TEXT.replace(" && github.run_attempt == '1' && 'CI-main'", " && 'CI-main'", 1),
     "every push in its own group": _CI_TEXT.replace(" && 'CI-main' ||", " && format('CI-{0}', github.run_id) ||", 1),
-    "the main group cancelling in progress": _CI_TEXT.replace(
-        "'CI-main' || format('CI-{0}', github.run_id) }}\n  cancel-in-progress: false",
-        "'CI-main' || format('CI-{0}', github.run_id) }}\n  cancel-in-progress: true", 1),
+    "the main group cancelling in progress": re.sub(
+        r"(?m)^  cancel-in-progress: .*$", "  cancel-in-progress: true", _CI_TEXT, count=1),
+    # #3885 L1's own plants: each widens or narrows the CI-pr-<number> arm by one condition.
+    "the PR group on every pull_request action": _CI_TEXT.replace(
+        " && github.event.action == 'synchronize'", "", 2),
+    "the PR group's cancel on every pull_request action": _CI_TEXT.replace(
+        "cancel-in-progress: ${{ github.event_name == 'pull_request' && github.event.action == 'synchronize'",
+        "cancel-in-progress: ${{ github.event_name == 'pull_request'", 1),
+    "PR re-runs in the PR group": _CI_TEXT.replace(
+        " && github.event.action == 'synchronize' && github.run_attempt == '1'",
+        " && github.event.action == 'synchronize'", 2),
+    "bot-sent pushes in the PR group": _CI_TEXT.replace(
+        " && github.event.sender.login != 'github-actions[bot]' && format('CI-pr-{0}'", " && format('CI-pr-{0}'", 1),
+    "the PR group cancelling nothing": re.sub(
+        r"(?m)^  cancel-in-progress: .*$", "  cancel-in-progress: false", _CI_TEXT, count=1),
+    "no PR group": _CI_TEXT.replace(
+        "format('CI-pr-{0}', github.event.pull_request.number)", "format('CI-{0}', github.run_id)", 1),
     "gate skippable on merge_group": _CI_TEXT.replace(
         "    if: ${{ !cancelled() }}\n", "    if: ${{ !cancelled() && github.event_name != 'merge_group' }}\n", 1),
     "gate skipped when the prelude fails": _CI_TEXT.replace(
@@ -21895,7 +21922,8 @@ _CI_PLANT_MISSED = sorted(k for k, t in _CI_PLANTS.items()
                           if t == _CI_TEXT or not _ci_umbrella_defects(_yaml.safe_load(t) or {}, t))
 R.check(
     "the CI umbrella: DESIGN-P2's triggers with labeled and merge_group, a "
-    "run-name equal to prelude.title, one run per group but a push's first attempt (CI-main, CI-5), "
+    "run-name equal to prelude.title, one run per group but a push's first attempt (CI-main, CI-5) "
+    "and a non-bot synchronize's first attempt (CI-pr-<number>, cancelling in progress, #3885 L1), "
     "every unit called "
     "by its stem exactly when the prelude's workset names it, and a `gate` "
     "no event can skip, judging on the prelude's outputs (U0c)",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
