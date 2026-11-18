#!/usr/bin/env python3
"""Triage batch 126 (P391, P392): the measurements behind the existing-set ruling.

WHY IT EXISTS. The owner's bar (2026-11-05): non-production CI and the triage
seat must show a measured improvement of 5 % (existing) or 10 % (new). Every
figure in dev/programme/triage/s6-batch126.md is printed by one arm here, over a
fixed window, so another seat re-derives it rather than trusting a carried number.

    python3 -I dev/audit/harnesses/r10_triage_p391.py ci-cost  FROM TO OUT.json
    python3 -I dev/audit/harnesses/r10_triage_p391.py ci-fails FROM TO OUT.json
    python3 -I dev/audit/harnesses/r10_triage_p391.py nightly  FROM TO
    python3 -I dev/audit/harnesses/r10_triage_p391.py report   COST.json FAILS.json
    python3 -I dev/audit/harnesses/r10_triage_p391.py git      REF FROM TO
    python3 -I dev/audit/harnesses/r10_triage_p391.py tokens   SINCE
    python3 -I dev/audit/harnesses/r10_triage_p391.py roster   REF

Every REST read is cached on disk by path (P391_CACHE), and an arm waits for
the reset rather than take the shared core budget under FLOOR. FROM and TO are UTC ISO instants (2026-10-28T00:00:00Z). The API arms read
`gh api` (the Actions runs and jobs, and the pull-request search); the git arm
reads only the local clone at REF; `tokens` reads this host's session
transcripts and so cannot be re-run by another seat. `ci-fails` is REST-only (search/issues for the merged
pull requests by merged_at, then pulls/<n> for each head ref), so a cloud seat
re-derives it; "merged" there is merged_at inside the window, not a first-parent
merge by commit date, and it counts head refs, so a branch merged twice counts twice.
A share is runner seconds
(job end less start, skipped jobs excluded) over the cost window's total.
"PRs" counts pull requests whose branch had the lane red, then a later green
CI run or a merge, with a red within 12 h of the same lane red on main left
out: an UPPER bound on right-first-time, since no failure log is read.
"""
from __future__ import annotations

import collections
import datetime as D
import glob
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

# The first-parent merge-subject grammar is record_burst_replay's, read not restated.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from record_burst_replay import MERGE_RE  # noqa: E402

REPO = "tvofi/heatpump_optimizer"
INHERIT_S = 12 * 3600
# Lanes that report main's state rather than the pull request's code.
REPORTERS = ("tests / nightly-status", "governance / delivery-status")
# The REST core budget is the account's, shared by every seat: an arm stops
# itself, never spending the last of it (2026-11-06: a re-take emptied it).
FLOOR = 2500  # the merge train, the relay and the cloud seats share it (orchestrator, 2026-11-06)
CHECK_EVERY = 25
_calls = 0


def headroom() -> None:
    """Wait for the reset when the shared budget is under FLOOR; reading it is free."""
    while True:
        r = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.core | [.remaining, .reset] | @tsv"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("rate_limit unreadable: " + r.stderr[:160])
        left, reset = (int(x) for x in r.stdout.split())
        if left >= FLOOR:
            return
        wait = max(60, reset - int(time.time()) + 30)
        print(f"WAIT {left} left under the floor {FLOOR}; sleeping {wait} s to the reset", file=sys.stderr, flush=True)
        time.sleep(wait)


def t(s: str) -> D.datetime:
    return D.datetime.fromisoformat(s.replace("Z", "+00:00"))


# Every read is cached on disk by its path, so a re-run never re-reads a page:
# the windows are past, so a page does not change. P391_CACHE names the directory.
CACHE = os.environ.get("P391_CACHE") or os.path.expanduser("~/.cache/hpo-p391")


def api(path: str):
    global _calls
    safe = "".join(c if c.isascii() and (c.isalnum() or c in "._-") else "_" for c in path)
    key = os.path.join(CACHE, safe + ".json")
    if os.path.exists(key):
        return json.load(open(key))
    if _calls % CHECK_EVERY == 0:
        headroom()
    _calls += 1
    for _ in range(4):
        r = subprocess.run(["gh", "api", "-X", "GET", path], capture_output=True, text=True)
        if r.returncode == 0:
            os.makedirs(CACHE, exist_ok=True)
            with open(key + ".tmp", "w") as f:
                f.write(r.stdout)
            os.replace(key + ".tmp", key)
            return json.loads(r.stdout)
        print("ERR", path, r.stderr[:160], file=sys.stderr, flush=True)
        time.sleep(30)
    raise SystemExit("api failed: " + path)


def ci_id() -> int:
    return next(w["id"] for w in api(f"repos/{REPO}/actions/workflows?per_page=100")["workflows"]
                if w["path"].endswith("/ci.yml"))


def runs(wid, created: str, extra: str = "") -> list[dict]:
    out, page = [], 1
    while True:
        d = api(f"repos/{REPO}/actions/workflows/{wid}/runs?per_page=100&page={page}&created={created}{extra}")
        out += d["workflow_runs"]
        if len(d["workflow_runs"]) < 100 or page >= 10:
            if page >= 10 and len(d["workflow_runs"]) == 100:
                raise SystemExit(f"over 1000 runs in {created}{extra}: narrow the window")
            return out
        page += 1


def jobs(run_id) -> list[dict]:
    out, page = [], 1
    while True:
        d = api(f"repos/{REPO}/actions/runs/{run_id}/jobs?per_page=100&page={page}")
        out += d["jobs"]
        if len(d["jobs"]) < 100:
            return out
        page += 1


def secs(j: dict) -> float:
    if j.get("conclusion") in (None, "skipped") or not j.get("started_at") or not j.get("completed_at"):
        return 0.0
    return max(0.0, (t(j["completed_at"]) - t(j["started_at"])).total_seconds())


def windows(a: str, b: str, hours: int):
    s, e = t(a), t(b)
    while s < e:
        n = min(e, s + D.timedelta(hours=hours))
        yield s.strftime("%Y-%m-%dT%H:%M:%SZ"), n.strftime("%Y-%m-%dT%H:%M:%SZ")
        s = n


def arm_ci_cost(a, b, out):
    wid, res = ci_id(), {"from": a, "to": b, "runs": {}}
    for x, y in windows(a, b, 3):
        for r in runs(wid, f"{x}..{y}", "&status=completed"):
            res["runs"][str(r["id"])] = {"event": r["event"], "jobs": [
                {"name": j["name"], "c": j["conclusion"], "s": secs(j)} for j in jobs(r["id"])]}
    json.dump(res, open(out, "w"))
    tot = sum(j["s"] for r in res["runs"].values() for j in r["jobs"])
    print(f"RESULT ci-cost {a}..{b}: {len(res['runs'])} completed runs, {tot / 3600:.1f} runner h, "
          f"{tot / 60 / max(len(res['runs']), 1):.1f} min a run")


def arm_ci_fails(a, b, out):
    wid, res = ci_id(), {"from": a, "to": b, "fail": {}, "green": {}}
    for x, y in windows(a, b, 24):
        for ev in ("pull_request", "push"):
            for r in runs(wid, f"{x}..{y}", f"&event={ev}&status=failure"):
                res["fail"][str(r["id"])] = {"event": ev, "sha": r["head_sha"], "branch": r["head_branch"],
                                             "at": r["run_started_at"]}
            for r in runs(wid, f"{x}..{y}", f"&event={ev}&status=success"):
                res["green"].setdefault(r["head_branch"], []).append([r["head_sha"], r["run_started_at"]])
    for r_id, r in res["fail"].items():
        r["failed"] = [j["name"] for j in jobs(r_id) if j["conclusion"] in ("failure", "timed_out")]
    # REST only: GraphQL (`gh pr list --search`) is refused (403) from cloud seats, so a
    # cloud reviewer could not re-derive this arm. search/issues pages give the merged
    # pull requests (merged_at inside FROM..TO, 100 a page), pulls/<n> gives each head ref.
    pulls, page = [], 1
    while True:
        q = urllib.parse.quote(f"repo:{REPO} is:pr is:merged merged:{a}..{b}")
        got = api(f"search/issues?q={q}&per_page=100&page={page}")["items"]
        for it in got:
            pulls.append(api(f"repos/{REPO}/pulls/{it['number']}")["head"]["ref"])
        if len(got) < 100:
            break
        page += 1
    res["merged"] = pulls
    json.dump(res, open(out, "w"))
    print(f"RESULT ci-fails {a}..{b}: {sum(r['event'] == 'pull_request' for r in res['fail'].values())} failed "
          f"pull-request runs, {sum(r['event'] == 'push' for r in res['fail'].values())} failed push runs, "
          f"{len(pulls)} pull requests merged")


def arm_nightly(a, b):
    wid = next(w["id"] for w in api(f"repos/{REPO}/actions/workflows?per_page=100")["workflows"]
               if w["path"].endswith("/nightly.yml"))
    tot = collections.Counter()
    n = collections.Counter()
    for r in runs(wid, f"{a}..{b}", "&status=completed"):
        s = sum(secs(j) for j in jobs(r["id"]))
        k = "push" if r["event"] == "push" else "schedule or dispatch"
        tot[k] += s
        n[k] += 1
        if k != "push":
            print(f"  {r['run_started_at']} {r['event']} {r['conclusion']} {s / 3600:.1f} h")
    for k in tot:
        print(f"RESULT nightly {a}..{b} {k}: {n[k]} runs, {tot[k] / 3600:.1f} runner h")


def arm_report(cost, fails):
    c, f = json.load(open(cost)), json.load(open(fails))
    lane = collections.defaultdict(lambda: [0.0, 0])
    for r in c["runs"].values():
        for j in r["jobs"]:
            if j["s"] > 0:
                lane[j["name"]][0] += j["s"]
                lane[j["name"]][1] += 1
    tot = sum(v[0] for v in lane.values())
    mainred = collections.defaultdict(list)
    for r in f["fail"].values():
        if r["event"] == "push" and r["branch"] == "main":
            for n in r["failed"]:
                mainred[n].append(t(r["at"]))
    merged = set(f["merged"])
    caught = collections.defaultdict(set)
    sole = collections.defaultdict(set)
    reds = collections.defaultdict(set)
    inherited = collections.Counter()
    for r in f["fail"].values():
        if r["event"] != "pull_request":
            continue
        at = t(r["at"])
        real = [n for n in r["failed"] if n != "gate" and not n.startswith("pr-contract") and n not in REPORTERS]
        for n in r["failed"]:
            reds[n].add(r["branch"])
            if any(abs((at - x).total_seconds()) < INHERIT_S for x in mainred.get(n, [])):
                inherited[n] += 1
                continue
            later = [g for g in f["green"].get(r["branch"], []) if g[0] != r["sha"] and t(g[1]) > at]
            if later or r["branch"] in merged:
                caught[n].add(r["branch"])
            if real == [n]:
                sole[n].add(r["branch"])
    print(f"RESULT report: cost window {c['from']}..{c['to']}, {len(c['runs'])} runs, {tot / 3600:.1f} runner h; "
          f"benefit window {f['from']}..{f['to']}, {len(merged)} merged, 5 % is {0.05 * len(merged):.1f}")
    print("lane | share % | mean s | runs | PRs red | PRs caught (upper bound) | sole | inherited red runs | main red runs")
    for n in sorted(set(lane) | set(reds), key=lambda k: -lane[k][0] if k in lane else 0):
        s, k = lane.get(n, [0.0, 0])
        print(f"{n} | {100 * s / tot:.1f} | {s / max(k, 1):.0f} | {k} | {len(reds[n])} | {len(caught[n])} | "
              f"{len(sole[n])} | {inherited[n]} | {len(mainred.get(n, []))}")


def arm_git(ref, a, b):
    def log(*extra):
        return subprocess.run(["git", "log", ref, f"--since={a}", f"--until={b}", "--format=%s", *extra],
                              capture_output=True, text=True, check=True).stdout.splitlines()
    subj = log()
    for p in ("ci: pin killed", "ci: record delivery", "ci: record nightly", "ci: re-record closures",
              "ci: drop inherited claims"):
        print(f"RESULT git {ref} {a}..{b}: {sum(s.startswith(p) for s in subj)} commits '{p}'")
    fp = log("--first-parent")
    nums = {m.group(1) for s in fp if (m := MERGE_RE.match(s))}
    print(f"RESULT git {ref} {a}..{b}: {len(nums)} 'Merge pull request #N' on the first parent")


def arm_tokens(since):
    root = os.path.expanduser("~/.claude/projects")
    cut = t(since).timestamp()
    seat = re.compile(r"(proposal-triage seat|standing triage|triage seat)", re.I)
    rev = re.compile(r"fix reviewer|reviewer for pr|you are .{0,40}review", re.I)
    keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    tot, mine, revs, n = collections.Counter(), collections.Counter(), collections.Counter(), 0
    for d in glob.glob(root + "/*heatpump*"):
        for dp, _, fs in os.walk(d):
            for fn in fs:
                p = os.path.join(dp, fn)
                if not fn.endswith(".jsonl") or os.path.getmtime(p) < cut:
                    continue
                first, seen = None, {}
                for line in open(p, errors="replace"):
                    if first is None and '"type":"user"' in line.replace(" ", "")[:400000]:
                        try:
                            m = json.loads(line)["message"]["content"]
                            first = m if isinstance(m, str) else json.dumps(m)
                        except (ValueError, KeyError, TypeError):
                            first = line
                    if '"usage"' not in line:
                        continue
                    try:
                        o = json.loads(line)
                    except ValueError:
                        continue
                    m = o.get("message")
                    if isinstance(m, dict) and m.get("usage"):
                        seen[m.get("id") or o.get("uuid")] = m["usage"]
                u = collections.Counter()
                for us in seen.values():
                    for k in keys:
                        u[k] += us.get(k) or 0
                tot.update(u)
                head = (first or "")[:300]
                if fn.startswith("agent-") and seat.search(head) and not rev.search(head[:200]):
                    mine.update(u)
                    n += 1
                elif fn.startswith("agent-") and rev.search(head[:200]) and "triage" in (first or "")[:400].lower():
                    revs.update(u)
    print(f"RESULT tokens since {since}: {n} triage seat sessions")
    for k in keys:
        print(f"RESULT tokens {k}: seat {mine[k]}, triage reviews {revs[k]}, all {tot[k]}, "
              f"seat share {100 * mine[k] / max(tot[k], 1):.1f} %")


def arm_roster(ref):
    """Verdicts in the triage batches and the roster's triage-cited carries, at REF."""
    def show(path):
        return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout
    names = subprocess.run(["git", "ls-tree", "--name-only", ref, "dev/programme/triage/"],
                           capture_output=True, text=True, check=True).stdout.split()
    v = collections.Counter()
    for n in names:
        for m in re.finditer(r"^## P\d+.*?\n(?:.*\n){0,4}?\s*Verdict:\s*\**(\w+)", show(n), re.M):
            v[m[1].upper()] += 1
    print(f"RESULT roster {ref}: {len(names)} batch files, {sum(v.values())} entries: "
          + ", ".join(f"{k} {n}" for k, n in v.most_common()))
    r = json.loads(show("dev/programme/rosters/wave-r10-groups.json"))
    rows = r["groups"] if isinstance(r["groups"], list) else list(r["groups"].values())
    c = collections.Counter()
    for g in rows:
        closed = (g.get("resume") or {}).get("stage") in ("done", "absorbed", "superseded", "dropped", "rca-done")
        for t_ in g.get("carry", []):
            t_ = str(t_)
            if re.search(r"triage: dev/programme/triage|From triage P\d+|triage P\d+", t_):
                mk = re.search(r"\[(implemented|moved|dismissed):", t_)
                c[mk[1] if mk else ("on a closed group" if closed else "on an open group")] += 1
    print(f"RESULT roster {ref}: {sum(c.values())} carries cite triage: " + ", ".join(f"{k} {n}" for k, n in c.most_common()))
    b = json.loads(show("dev/governance/config/machinery_budgets.json"))
    print(f"RESULT roster {ref}: machinery_budgets.json exemptions {len(b.get('exemptions', []))}")


def main(argv):
    arm, rest = argv[0], argv[1:]
    {"ci-cost": arm_ci_cost, "ci-fails": arm_ci_fails, "nightly": arm_nightly, "report": arm_report,
     "git": arm_git, "tokens": arm_tokens, "roster": arm_roster}[arm](*rest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
