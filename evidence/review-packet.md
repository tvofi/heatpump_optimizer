# Review packet #3238
head: 3ccb4fd7698e9a2eaea83f0bcd8f69b9c67885ba
base: b88684a218923f85de66f1e8fb1833e31a76a154

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127840975186 success
arch-score / arch-score id=127840898321 success
arm id=127840744428 skipped
budget-raise-gate / budget-raise-gate id=127840898303 success
cancel-superseded id=127840673252 success
codeql id=127840888587 skipped
codeql / Analyze (actions) id=127840898075 success
codeql / Analyze (javascript-typescript) id=127840898254 success
codeql / Analyze (python) id=127840898120 success
gate id=127841334502 failure
governance id=127840888416 skipped
governance / delivery-status id=127840898374 success
governance / delivery-status-publish id=127840900589 skipped
governance / env-matrix id=127840898328 in_progress
governance / instrument-self-tests id=127840898320 in_progress
governance / policy-docs id=127840898183 success
governance / record id=127840900440 skipped
governance / wave-script id=127840898309 success
hassfest id=127840888142 skipped
hassfest / hassfest id=127840898099 success
kernel-points id=127840899798 skipped
pr-contract id=127841335792 skipped
prelude id=127840673179 success
refresh id=127840672809 success
tests id=127840887632 skipped
tests / arch-instrument id=127841096713 success
tests / briefs id=127840898121 success
tests / browser id=127841096724 in_progress
tests / closure-scope id=127840898224 success
tests / closures id=127841096814 in_progress
tests / coverage id=127841096899 in_progress
tests / fast (3.14) id=127841096917 in_progress
tests / mutation id=127840898091 success
tests / mutation-autofix id=127841265277 skipped
tests / mutation-pins id=127841264617 skipped
tests / nightly-ha id=127841099079 skipped
tests / nightly-status id=127840898029 success
tests / replay id=127841098665 skipped
tests / typing id=127841096839 success
validate id=127840887703 skipped
validate / validate-hacs id=127840898162 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks
required-red: required context `gate` concluded failure at 3ccb4fd7698e9a2eaea83f0bcd8f69b9c67885ba

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat b88684a218923f85de66f1e8fb1833e31a76a154...<head>
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         dev/audit/harnesses/record_burst_replay.py
             `dev/audit/harnesses/record_burst_replay.py` is in the tree at this head
  ok         tools/audit/seat/ref_privacy.py
             `tools/audit/seat/ref_privacy.py` is in the tree at this head

FIGURES: 2 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_triage_p391.py b/dev/audit/harnesses/r10_triage_p391.py
new file mode 100644
index 000000000..88abd736f
--- /dev/null
+++ b/dev/audit/harnesses/r10_triage_p391.py
@@ -0,0 +1,330 @@
+#!/usr/bin/env python3
+"""Triage batch 126 (P391, P392): the measurements behind the existing-set ruling.
+
+WHY IT EXISTS. The owner's bar (2026-11-05): non-production CI and the triage
+seat must show a measured improvement of 5 % (existing) or 10 % (new). Every
+figure in dev/programme/triage/s6-batch126.md is printed by one arm here, over a
+fixed window, so another seat re-derives it rather than trusting a carried number.
+
+    python3 -I dev/audit/harnesses/r10_triage_p391.py ci-cost  FROM TO OUT.json
+    python3 -I dev/audit/harnesses/r10_triage_p391.py ci-fails FROM TO OUT.json
+    python3 -I dev/audit/harnesses/r10_triage_p391.py nightly  FROM TO
+    python3 -I dev/audit/harnesses/r10_triage_p391.py report   COST.json FAILS.json
+    python3 -I dev/audit/harnesses/r10_triage_p391.py git      REF FROM TO
+    python3 -I dev/audit/harnesses/r10_triage_p391.py tokens   SINCE
+    python3 -I dev/audit/harnesses/r10_triage_p391.py roster   REF
+
+Every REST read is cached on disk by path (P391_CACHE), and an arm waits for
+the reset rather than take the shared core budget under FLOOR. FROM and TO are UTC ISO instants (2026-10-28T00:00:00Z). The API arms read
+`gh api` (the Actions runs and jobs, and the pull-request search); the git arm
+reads only the local clone at REF; `tokens` reads this host's session
+transcripts and so cannot be re-run by another seat. A share is runner seconds
+(job end less start, skipped jobs excluded) over the cost window's total.
+"PRs" counts pull requests whose branch had the lane red, then a later green
+CI run or a merge, with a red within 12 h of the same lane red on main left
+out: an UPPER bound on right-first-time, since no failure log is read.
+"""
+from __future__ import annotations
+
+import collections
+import datetime as D
+import glob
+import json
+import os
+import re
+import subprocess
+import sys
+import time
+
+# The first-parent merge-subject grammar is record_burst_replay's, read not restated.
+sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
+from record_burst_replay import MERGE_RE  # noqa: E402
+
+REPO = "tvofi/heatpump_optimizer"
+INHERIT_S = 12 * 3600
+# Lanes that report main's state rather than the pull request's code.
+REPORTERS = ("tests / nightly-status", "governance / delivery-status")
+# The REST core budget is the account's, shared by every seat: an arm stops
+# itself, never spending the last of it (2026-11-06: a re-take emptied it).
+FLOOR = 2500  # the merge train, the relay and the cloud seats share it (orchestrator, 2026-11-06)
+CHECK_EVERY = 25
+_calls = 0
+
+
+def headroom() -> None:
+    """Wait for the reset when the shared budget is under FLOOR; reading it is free."""
+    while True:
+        r = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.core | [.remaining, .reset] | @tsv"],
+                           capture_output=True, text=True)
+        if r.returncode != 0:
+            raise SystemExit("rate_limit unreadable: " + r.stderr[:160])
+        left, reset = (int(x) for x in r.stdout.split())
+        if left >= FLOOR:
+            return
+        wait = max(60, reset - int(time.time()) + 30)
+        print(f"WAIT {left} left under the floor {FLOOR}; sleeping {wait} s to the reset", file=sys.stderr, flush=True)
+        time.sleep(wait)
+
+
+def t(s: str) -> D.datetime:
+    return D.datetime.fromisoformat(s.replace("Z", "+00:00"))
+
+
+# Every read is cached on disk by its path, so a re-run never re-reads a page:
+# the windows are past, so a page does not change. P391_CACHE names the directory.
+CACHE = os.environ.get("P391_CACHE") or os.path.expanduser("~/.cache/hpo-p391")
+
+
+def api(path: str):
+    global _calls
+    safe = "".join(c if c.isascii() and (c.isalnum() or c in "._-") else "_" for c in path)
+    key = os.path.join(CACHE, safe + ".json")
+    if os.path.exists(key):
+        return json.load(open(key))
+    if _calls % CHECK_EVERY == 0:
+        headroom()
+    _calls += 1
+    for _ in range(4):
+        r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
+        if r.returncode == 0:
+            os.makedirs(CACHE, exist_ok=True)
+            with open(key + ".tmp", "w") as f:
+                f.write(r.stdout)
+            os.replace(key + ".tmp", key)
+            return json.loads(r.stdout)
+        print("ERR", path, r.stderr[:160], file=sys.stderr, flush=True)
+        time.sleep(30)
+    raise SystemExit("api failed: " + path)
+
+
+def ci_id() -> int:
+    return next(w["id"] for w in api(f"repos/{REPO}/actions/workflows?per_page=100")["workflows"]
+                if w["path"].endswith("/ci.yml"))
+
+
+def runs(wid, created: str, extra: str = "") -> list[dict]:
+    out, page = [], 1
+    while True:
+        d = api(f"repos/{REPO}/actions/workflows/{wid}/runs?per_page=100&page={page}&created={created}{extra}")
+        out += d["workflow_runs"]
+        if len(d["workflow_runs"]) < 100 or page >= 10:
+            if page >= 10 and len(d["workflow_runs"]) == 100:
+                raise SystemExit(f"over 1000 runs in {created}{extra}: narrow the window")
+            return out
+        page += 1
+
+
+def jobs(run_id) -> list[dict]:
+    out, page = [], 1
+    while True:
+        d = api(f"repos/{REPO}/actions/runs/{run_id}/jobs?per_page=100&page={page}")
+        out += d["jobs"]
+        if len(d["jobs"]) < 100:
+            return out
+        page += 1
+
+
+def secs(j: dict) -> float:
+    if j.get("conclusion") in (None, "skipped") or not j.get("started_at") or not j.get("completed_at"):
+        return 0.0
+    return max(0.0, (t(j["completed_at"]) - t(j["started_at"])).total_seconds())
+
+
+def windows(a: str, b: str, hours: int):
+    s, e = t(a), t(b)
+    while s < e:
+        n = min(e, s + D.timedelta(hours=hours))
+        yield s.strftime("%Y-%m-%dT%H:%M:%SZ"), n.strftime("%Y-%m-%dT%H:%M:%SZ")
+        s = n
+
+
+def arm_ci_cost(a, b, out):
+    wid, res = ci_id(), {"from": a, "to": b, "runs": {}}
+    for x, y in windows(a, b, 3):
+        for r in runs(wid, f"{x}..{y}", "&status=completed"):
+            res["runs"][str(r["id"])] = {"event": r["event"], "jobs": [
+                {"name": j["name"], "c": j["conclusion"], "s": secs(j)} for j in jobs(r["id"])]}
+    json.dump(res, open(out, "w"))
+    tot = sum(j["s"] for r in res["runs"].values() for j in r["jobs"])
+    print(f"RESULT ci-cost {a}..{b}: {len(res['runs'])} completed runs, {tot / 3600:.1f} runner h, "
+          f"{tot / 60 / max(len(res['runs']), 1):.1f} min a run")
+
+
+def arm_ci_fails(a, b, out):
+    wid, res = ci_id(), {"from": a, "to": b, "fail": {}, "green": {}}
+    for x, y in windows(a, b, 24):
+        for ev in ("pull_request", "push"):
+            for r in runs(wid, f"{x}..{y}", f"&event={ev}&status=failure"):
+                res["fail"][str(r["id"])] = {"event": ev, "sha": r["head_sha"], "branch": r["head_branch"],
+                                             "at": r["run_started_at"]}
+            for r in runs(wid, f"{x}..{y}", f"&event={ev}&status=success"):
+                res["green"].setdefault(r["head_branch"], []).append([r["head_sha"], r["run_started_at"]])
+    for r_id, r in res["fail"].items():
+        r["failed"] = [j["name"] for j in jobs(r_id) if j["conclusion"] in ("failure", "timed_out")]
+    # GraphQL, not one REST read per pull request: its budget is separate.
+    r = subprocess.run(["gh", "pr", "list", "--repo", REPO, "--state", "merged", "--limit", "1000",
+                        "--search", f"merged:{a}..{b}", "--json", "headRefName"],
+                       capture_output=True, text=True, check=True)
+    pulls = [x["headRefName"] for x in json.loads(r.stdout)]
+    res["merged"] = pulls
+    json.dump(res, open(out, "w"))
+    print(f"RESULT ci-fails {a}..{b}: {sum(r['event'] == 'pull_request' for r in res['fail'].values())} failed "
+          f"pull-request runs, {sum(r['event'] == 'push' for r in res['fail'].values())} failed push runs, "
+          f"{len(pulls)} pull requests merged")
+
+
+def arm_nightly(a, b):
+    wid = next(w["id"] for w in api(f"repos/{REPO}/actions/workflows?per_page=100")["workflows"]
+               if w["path"].endswith("/nightly.yml"))
+    tot = collections.Counter()
+    n = collections.Counter()
+    for r in runs(wid, f"{a}..{b}", "&status=completed"):
+        s = sum(secs(j) for j in jobs(r["id"]))
+        k = "push" if r["event"] == "push" else "schedule or dispatch"
+        tot[k] += s
+        n[k] += 1
+        if k != "push":
+            print(f"  {r['run_started_at']} {r['event']} {r['conclusion']} {s / 3600:.1f} h")
+    for k in tot:
+        print(f"RESULT nightly {a}..{b} {k}: {n[k]} runs, {tot[k] / 3600:.1f} runner h")
+
+
+def arm_report(cost, fails):
+    c, f = json.load(open(cost)), json.load(open(fails))
+    lane = collections.defaultdict(lambda: [0.0, 0])
+    for r in c["runs"].values():
+        for j in r["jobs"]:
+            if j["s"] > 0:
+                lane[j["name"]][0] += j["s"]
+                lane[j["name"]][1] += 1
+    tot = sum(v[0] for v in lane.values())
+    mainred = collections.defaultdict(list)
+    for r in f["fail"].values():
+        if r["event"] == "push" and r["branch"] == "main":
+            for n in r["failed"]:
+                mainred[n].append(t(r["at"]))
+    merged = set(f["merged"])
+    caught = collections.defaultdict(set)
+    sole = collections.defaultdict(set)
+    reds = collections.defaultdict(set)
+    inherited = collections.Counter()
+    for r in f["fail"].values():
+        if r["event"] != "pull_request":
+            continue
+        at = t(r["at"])
+        real = [n for n in r["failed"] if n != "gate" and not n.startswith("pr-contract") and n not in REPORTERS]
+        for n in r["failed"]:
+            reds[n].add(r["branch"])
+            if any(abs((at - x).total_seconds()) < INHERIT_S for x in mainred.get(n, [])):
+                inherited[n] += 1
+                continue
+            later = [g for g in f["green"].get(r["branch"], []) if g[0] != r["sha"] and t(g[1]) > at]
+            if later or r["branch"] in merged:
+                caught[n].add(r["branch"])
+            if real == [n]:
+                sole[n].add(r["branch"])
+    print(f"RESULT report: cost window {c['from']}..{c['to']}, {len(c['runs'])} runs, {tot / 3600:.1f} runner h; "
+          f"benefit window {f['from']}..{f['to']}, {len(merged)} merged, 5 % is {0.05 * len(merged):.1f}")
+    print("lane | share % | mean s | runs | PRs red | PRs caught (upper bound) | sole | inherited red runs | main red runs")
+    for n in sorted(set(lane) | set(reds), key=lambda k: -lane[k][0] if k in lane else 0):
+        s, k = lane.get(n, [0.0, 0])
+        print(f"{n} | {100 * s / tot:.1f} | {s / max(k, 1):.0f} | {k} | {len(reds[n])} | {len(caught[n])} | "
+              f"{len(sole[n])} | {inherited[n]} | {len(mainred.get(n, []))}")
+
+
+def arm_git(ref, a, b):
+    def log(*extra):
+        return subprocess.run(["git", "log", ref, f"--since={a}", f"--until={b}", "--format=%s", *extra],
+                              capture_output=True, text=True, check=True).stdout.splitlines()
+    subj = log()
+    for p in ("ci: pin killed", "ci: record delivery", "ci: record nightly", "ci: re-record closures",
+              "ci: drop inherited claims"):
+        print(f"RESULT git {ref} {a}..{b}: {sum(s.startswith(p) for s in subj)} commits '{p}'")
+    fp = log("--first-parent")
+    nums = {m.group(1) for s in fp if (m := MERGE_RE.match(s))}
+    print(f"RESULT git {ref} {a}..{b}: {len(nums)} 'Merge pull request #N' on the first parent")
+
+
+def arm_tokens(since):
+    root = os.path.expanduser("~/.claude/projects")
+    cut = t(since).timestamp()
+    seat = re.compile(r"(proposal-triage seat|standing triage|triage seat)", re.I)
+    rev = re.compile(r"fix reviewer|reviewer for pr|you are .{0,40}review", re.I)
+    keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
+    tot, mine, revs, n = collections.Counter(), collections.Counter(), collections.Counter(), 0
+    for d in glob.glob(root + "/*heatpump*"):
+        for dp, _, fs in os.walk(d):
+            for fn in fs:
+                p = os.path.join(dp, fn)
+                if not fn.endswith(".jsonl") or os.path.getmtime(p) < cut:
+                    continue
+                first, seen = None, {}
+                for line in open(p, errors="replace"):
+                    if first is None and '"type":"user"' in line.replace(" ", "")[:400000]:
+                        try:
+                            m = json.loads(line)["message"]["content"]
+                            first = m if isinstance(m, str) else json.dumps(m)
+                        except (ValueError, KeyError, TypeError):
+                            first = line
+                    if '"usage"' not in line:
+                        continue
+                    try:
+                        o = json.loads(line)
+                    except ValueError:
+                        continue
+                    m = o.get("message")
+                    if isinstance(m, dict) and m.get("usage"):
+                        seen[m.get("id") or o.get("uuid")] = m["usage"]
+                u = collections.Counter()
+                for us in seen.values():
+                    for k in keys:
+                        u[k] += us.get(k) or 0
+                tot.update(u)
+                head = (first or "")[:300]
+                if fn.startswith("agent-") and seat.search(head) and not rev.search(head[:200]):
+                    mine.update(u)
+                    n += 1
+                elif fn.startswith("agent-") and rev.search(head[:200]) and "triage" in (first or "")[:400].lower():
+                    revs.update(u)
+    print(f"RESULT tokens since {since}: {n} triage seat sessions")
+    for k in keys:
+        print(f"RESULT tokens {k}: seat {mine[k]}, triage reviews {revs[k]}, all {tot[k]}, "
+              f"seat share {100 * mine[k] / max(tot[k], 1):.1f} %")
+
+
+def arm_roster(ref):
+    """Verdicts in the triage batches and the roster's triage-cited carries, at REF."""
+    def show(path):
+        return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout
+    names = subprocess.run(["git", "ls-tree", "--name-only", ref, "dev/programme/triage/"],
+                           capture_output=True, text=True, check=True).stdout.split()
+    v = collections.Counter()
+    for n in names:
+        for m in re.finditer(r"^## P\d+.*?\n(?:.*\n){0,4}?\s*Verdict:\s*\**(\w+)", show(n), re.M):
+            v[m[1].upper()] += 1
+    print(f"RESULT roster {ref}: {len(names)} batch files, {sum(v.values())} entries: "
+          + ", ".join(f"{k} {n}" for k, n in v.most_common()))
+    r = json.loads(show("dev/programme/rosters/wave-r10-groups.json"))
+    rows = r["groups"] if isinstance(r["groups"], list) else list(r["groups"].values())
+    c = collections.Counter()
+    for g in rows:
+        closed = (g.get("resume") or {}).get("stage") in ("done", "absorbed", "superseded", "dropped", "rca-done")
+        for t_ in g.get("carry", []):
+            t_ = str(t_)
+            if re.search(r"triage: dev/programme/triage|From triage P\d+|triage P\d+", t_):
+                mk = re.search(r"\[(implemented|moved|dismissed):", t_)
+                c[mk[1] if mk else ("on a closed group" if closed else "on an open group")] += 1
+    print(f"RESULT roster {ref}: {sum(c.values())} carries cite triage: " + ", ".join(f"{k} {n}" for k, n in c.most_common()))
+    b = json.loads(show("dev/governance/config/machinery_budgets.json"))
+    print(f"RESULT roster {ref}: machinery_budgets.json exemptions {len(b.get('exemptions', []))}")
+
+
+def main(argv):
+    arm, rest = argv[0], argv[1:]
+    {"ci-cost": arm_ci_cost, "ci-fails": arm_ci_fails, "nightly": arm_nightly, "report": arm_report,
+     "git": arm_git, "tokens": arm_tokens, "roster": arm_roster}[arm](*rest)
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/3238.md b/dev/programme/delivery/3238.md
new file mode 100644
index 000000000..66fec7266
--- /dev/null
+++ b/dev/programme/delivery/3238.md
@@ -0,0 +1 @@
+- [#3238](https://github.com/tvofi/heatpump_optimizer/pull/3238) — **open**, triage: batch 126, P391 and P392 DEFER (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch126.md b/dev/programme/triage/s6-batch126.md
new file mode 100644
index 000000000..ff58e1205
--- /dev/null
+++ b/dev/programme/triage/s6-batch126.md
@@ -0,0 +1,103 @@
+# Proposal triage, session s12, batch 126 (P391, P392): the existing set under the 5 % and 10 % rules
+
+**The bar.** Owner, relayed by the orchestrator: "the non production CIs and the triage seat should fulfil the cost benefit analysis, the "5 percent rule" for existing ones and 10 percent rule for new ones". Working reading, the orchestrator's: a measured improvement in CI time, programme completion time, right-first-time or token usage, each figure with its command. New: over 10 %. Existing: at least 5 %, or a candidate for removal. Unmeasured does not pass. It applies to every ruling from P391. Removing anything is a proposal to the orchestrator; nothing here is an action.
+
+**Every figure is printed by one arm of `dev/audit/harnesses/r10_triage_p391.py` at `41c5e7bc82e2ce0ccf3baab58242c590c243fa95`, over a fixed window.** Run each from a checkout of that commit. Each REST read is cached on disk, and an arm waits rather than take the account's shared API budget under 2500.
+
+| arm | command | prints |
+|---|---|---|
+| cost | `python3 -I dev/audit/harnesses/r10_triage_p391.py ci-cost 2026-11-04T22:06:00Z 2026-11-05T07:05:00Z cost.json` | 221 completed CI runs, 309.7 runner h, 84.1 min a run |
+| benefit | `python3 -I dev/audit/harnesses/r10_triage_p391.py ci-fails 2026-10-28T00:00:00Z 2026-11-05T07:30:00Z fails.json` | 423 failed pull-request runs, 55 failed push runs, 262 pull requests merged over 232 branches |
+| lanes | `python3 -I dev/audit/harnesses/r10_triage_p391.py report cost.json fails.json` | the per-lane table below; 5 % of 232 branches is 11.6 |
+| nightly | `python3 -I dev/audit/harnesses/r10_triage_p391.py nightly 2026-10-29T00:00:00Z 2026-11-05T07:30:00Z` | 16 scheduled or dispatched runs, 176.2 runner h; 244 push runs, 3.8 h |
+| git | `python3 -I dev/audit/harnesses/r10_triage_p391.py git 9315526f8dca6dcd07f9cf3f2685bd1dd633b4f6 2026-10-29T00:00:00Z 2026-11-05T07:30:00Z` | commit counts by subject prefix; 229 merges on main's first parent |
+| roster | `python3 -I dev/audit/harnesses/r10_triage_p391.py roster f85b3b4d56eed0b57f5b3b1f46471f8ae323113a` | verdicts, triage-cited carries, `exemptions` |
+| tokens | `python3 -I dev/audit/harnesses/r10_triage_p391.py tokens 2026-10-01T00:00:00Z` | this host's transcripts only: **another seat cannot re-run it**, and a later run reads more sessions |
+
+The cost window is 9 hours of runs, not a week, and a share counts waiting inside a job. "Caught" counts branches whose lane went red, then a later green run or a merge. A red within 12 h of the same lane red on main is left out. **"Caught" is an upper bound on right-first-time:** later green proves no defect, a scope change also clears a red, and no failure log was read. Branches, not pull requests, are the unit, because a record branch is reused across pull requests.
+
+## P391: the non-production CI lanes
+
+Verdict: DEFER. Twelve lanes fail the bar even at the upper bound, together 24 % of the sampled runner hours. What would change it: the owner's decision on each proposal below, or a measured benefit the lane's owner brings.
+
+Source: the owner's ruling above, by the orchestrator's message after P390.
+
+Instances, from the lanes arm unless named:
+
+**Proposed for removal or narrowing: under 11.6 branches caught at the upper bound.** "Req" means `tools/ci/prelude.py` `UNITS` names it, so removing it changes the gate and its ruleset contract.
+
+| lane | share | mean s | caught | req | proposal |
+|---|---|---|---|---|---|
+| `governance / instrument-self-tests` | 10.7 % | 1328 | 9 | no | run only on a diff reaching the instruments; 19 of its red runs sat within 12 h of its own red on main |
+| `tests / arch-instrument` | 5.4 % | 779 | 0 | yes | run only on a diff reaching the score's own files |
+| `governance / env-matrix` | 2.8 % | 346 | 1 | yes | remove or narrow |
+| `governance / policy-docs` | 1.5 % | 192 | 2 | yes | narrow to policy paths |
+| `arch-score / arch-score` | 0.9 % | 82 | 2 | when production is reached | keep only if the owner wants the score enforced |
+| `governance / wave-script` | 0.8 % | 93 | 0 | yes | narrow |
+| `tests / briefs` | 0.7 % | 89 | 1 | yes | narrow to roster and brief paths |
+| `tests / graders-head-copy` | 0.3 % | 84 | 0 | no | remove or narrow |
+| `tests / lane-proofs` | under 0.1 % | 6 | 0 | no | negligible either way |
+
+**Proposed for removal because the red catches nothing.** These lanes report main's state, so their red does not depend on the pull request.
+
+| lane | share | red | evidence |
+|---|---|---|---|
+| `governance / delivery-status` | 0.6 % | 29 branches | reports the record's conclusion on main |
+| `tests / nightly-status` | 0.4 % | 81 branches | reports the last nightly; the nightly arm lists the last three scheduled runs as failures. A red must be answered in a body; the cost of that is not counted |
+| `tests / ci-ratchet` | 0.1 % | 52 red pushes to main | the owner ruled no pause on it (2026-11-04), so its red stops nothing |
+
+**Not refuted, kept.** `tests / mutation-pins (1-7)`, 9.0 %, with `tests / mutation-autofix`. The git arm counts 29 `ci: pin killed` commits, 12.5 % of 232 branches, though commits are not branches. Each spares a repair round but restarts CI, which is not netted out.
+
+**Withdrawn: not re-derivable within budget.** These figures came from an earlier ad-hoc sample, not from the harness: `merge-main.yml` (10.6 h), `gate-sweep.yml` (19.7 h) and `dependabot-automerge.yml` (1.9 h). They are no longer claimed, and no proposal rests on them.
+
+**Benefit not measurable here, so unmeasured and not passing:**
+- `merge-main.yml`, `gate-sweep.yml` and `dependabot-automerge.yml`, as above.
+- `record-autofix`: the nightly arm's push runs, 3.8 h. The git arm's 52 `ci: record delivery` and 13 `ci: record nightly` commits are its output, not a measure.
+- `governance / record` and `delivery-status-publish` (0.2 %).
+- `tests / closures-autofix` (7 `ci: re-record closures` commits) and `tests / claims-autofix` (0 `ci: drop inherited claims`).
+- `dependency-graph.yml`, `marketplace.yml` and `pages.yml`: no improvement figure exists for any of them.
+
+**Could not be measured:**
+- `kernel-points.yml`: no sampled run executed it.
+- `tests.yml`, `governance.yml`, `codeql.yml` and the other called files have no runs of their own; they are priced as jobs of `ci.yml`.
+- `probe.yml` and `probe-options-freeze.yml`: listed by the API, with no runs.
+
+**Separate, not ruled.**
+- **Required safety lanes:** `gate` (1.1 %), `prelude` (11.9 %), `pr-contract` (0.4 %, 64 caught), `budget-raise-gate` (0.6 %, 4), `codeql` (15.4 %, no red), `hassfest` (0.4 %), `validate-hacs` (0.4 %), `refresh` and `cancel-superseded` (2.7 %), `release.yml`. Also `closures` (9.7 %, 10 caught) and `closure-scope` (0.6 %, 0), which keep the scoped gate honest.
+- **Production tests:** `fast` (7.8 %, 22), `coverage` (9.0 %, 0), `coverage-ratchet`, `browser` (1.7 %, 0), `typing` (0.6 %, 2), `mutation` (3.0 %, 22), `replay` (1.2 %, 9), and `nightly.yml`'s `slow`, `nightly-ha`, `mutation-nightly` and `mutation-ledger`.
+- **For the orchestrator's eye:** the 16 nightlies cost 176.2 h in 7 days, and a run rose from about 7 h to about 17 h on 2026-11-01 (nightly arm). `closures` sits under 11.6 at its upper bound; read as non-production, it would join the first table.
+
+**Limits of this reading.** A check is insurance, so eight days without a red is weak evidence against it. A lane too cheap to measure cannot show 5 % either. The orchestrator's reading, not the owner's, puts both in the candidate column.
+
+Cost: the first two tables free up to 24 % of sampled runner hours. Removing gate-listed lanes changes `tools/ci/prelude.py`, the workflows and the ruleset contract, all code-owned. Narrowing needs a measured scope, as `replay` already has (R10-REPLAY-SCOPED). No capped file is touched.
+
+Binding: no action. Each proposal goes to the owner through the orchestrator. This is not a CI-capacity proposal, which the owner ruled out on 2026-11-01.
+
+## P392: the triage seat
+
+Verdict: DEFER. On the working reading the seat does not pass: its cost is measured and its benefit is not. This seat is ruling on itself, so the orchestrator should weigh the entry with that in mind.
+
+Source: the owner's ruling above.
+
+Instances:
+- **Cost, from the tokens arm.** 55 seat sessions against all local transcripts since 2026-10-01. Not reproducible by another seat; the share moves as sessions are added.
+
+  | | seat | share |
+  |---|---|---|
+  | output | 5.31 M | 8.5 % |
+  | cache creation | 72.7 M | 11.7 % |
+  | cache read | 1.93 G | 7.0 % |
+
+  Reviews of triage pull requests add 0.50 M output and 0.16 G cache read. Cloud seats are in neither the seat's figures nor the total.
+- **What it produced, from the roster arm.** 387 entries in 129 batch files: ACCEPT 235, DEFER 95, REJECT 56, OWNER 1. 247 roster carries cite triage: 60 implemented, 58 moved, 5 dismissed, 57 on a closed group, 67 on an open group.
+- **What is not measured.** No ruling has a before-and-after figure on any of the four measures. `exemptions` in `dev/governance/config/machinery_budgets.json` is empty (roster arm). The cost a REJECT or DEFER avoided is an estimate, and no week ran without the seat.
+- **This session's own record.** P389 was a proposal the instrument already answered, and the orchestrator withdrew it. P387's finding was real when filed, then answered by the fix. The seat made slips, all corrected: a wrong calibration re-check, a wrong note on a harness arm, body commits under the owner's name, a copy into another seat's temp directory, and figures carried out of the tree, which this repair cites.
+
+Cost: removing the seat frees at most 7 to 12 % of local tokens, less whatever moves to the orchestrator; that is not measured either.
+
+Binding: proposed, for the owner through the orchestrator, smallest first:
+1. **From P391, apply the bar at the door.** A queue line with no measured figure gets a one-line DEFER, with no investigation. This seat's own change; it needs no decision.
+2. **Measure before deciding:** one week of that form against the week before, on tokens per ruling and on blocked verdicts of the groups that received carries. Under 5 % on both, remove the seat.
+3. **Or remove it now:** the orchestrator applies the one-line cost test itself.
+
+An owner directive keeps its route: P386 needed no cost test on whether, only on form.
diff --git a/tests/closures.json b/tests/closures.json
index de003de01..79d3291ae 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4124,6 +4124,7 @@
    "dev/audit/harnesses/r10_train_raise_hold_replay.py",
    "dev/audit/harnesses/r10_train_upgrade_mutants.py",
    "dev/audit/harnesses/r10_triage_gate_replay.py",
+   "dev/audit/harnesses/r10_triage_p391.py",
    "dev/audit/harnesses/r10_trust_relative_bundle.py",
    "dev/audit/harnesses/r10_two_zone_hhl_inert.py",
    "dev/audit/harnesses/r10_u9a_ratchet_nulls.py",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
