#!/usr/bin/env python3
"""R10-HOTFIX-GATE-BUSY-DEFER (r10-gate-busy-defer-3): a deferring gate holds no runner; the sweep re-judges it.

    python3 dev/audit/harnesses/r10_gate_busy_defer_3.py record HEAD RUN:ATTEMPT [RUN:ATTEMPT ...]
    python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay [--ci DIR]
    python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census --since ISO --until ISO

record   reads each named run attempt at HEAD from the GitHub API (`gh api`) and prints it in
         tools/ci/fixtures/gate_busy_defer_runs.json's row shape (the `gate` job carries the
         start of its `Judge this head` step as `judge_started_at`), for a seat to merge in.
replay   the #3282 scene (head 024a0201, PR #3282, 2026-11-07) from that fixture, through DIR's
         `gate.judge` and `sweep.Sweep` (default: this tree's tools/ci; a baseline is
         `git archive <sha> tools/ci tools/pr | tar -x -C $D` and `--ci $D/tools/ci`). The edit
         run 42367457809's gate is judged from its recorded `Judge this head` start, re-reading
         the recorded listing one POLL_S per nap; then, at the code run 42367457479's recorded
         completion (11:48:41Z, gate-sweep.yml's trigger), DIR's sweep runs over the listing as
         recorded there, with the edit gate's attempt 1 completed red and NO human re-run
         (live, tvofi re-ran it at 11:48:45Z, before the sweep's 11:48:53Z read); each re-run
         the sweep posts is judged again at that time. Prints the wait, the first verdict, the
         sweep's re-runs and the re-judged verdict, then `RESULT replay wait_s=<n> first=<FAIL|PASS>
         swept=<yes|no> final=<verdict>`.
census   live: every `gate` job of a ci.yml run created in [since, until] whose log's verdict is
         the deferral ("... are still being judged"). Per such gate: the seconds it held its
         runner, the first green `gate` completion of each run it deferred to (the deciding
         gate), the deferring run's next gate attempt (start, conclusion, triggering actor).
         Prints one row per gate, then `RESULT census deferral_fails=<n> heads=<h> per_head_max=<m>
         held_runner_s=<s> held_ge_600=<k> resolved=<r> by_bot=<b> by_human=<u> median_min=<x>`,
         where median_min is minutes from the deciding gate's green to the deferring run's next
         green gate, over the deferrals a later green attempt resolved.
"""
from __future__ import annotations

import argparse
import importlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = "tvofi/heatpump_optimizer"
ROOT = repo_root(__file__)
FIXTURE = ROOT / "tools" / "ci" / "fixtures" / "gate_busy_defer_runs.json"
MODULES = ("prelude", "gate", "ghapi", "codeql_scope", "sweep", "sweep_selftest")
H3282, EDIT, CODE, REVIEW = "024a0201fbd531e21c0caef4f522a71711acea10", 42367457809, 42367457479, 42367461228
DEFERRAL = re.compile(r"FAIL run\(s\) \[([0-9, ]+)\] at this head are still being judged")


def epoch(s):
    return None if not s else datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def gh(path, raw=False):
    """`gh api` with three retries (the API drops a request now and then); a fourth failure exits."""
    for k in range(4):
        p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout if raw else json.loads(p.stdout)
        time.sleep(3 * (k + 1))
    raise SystemExit(f"gh api {path}: {p.stderr.strip()}")


def pages(path, key):
    out, n = [], 1
    while True:
        got = gh(f"{path}{'&' if '?' in path else '?'}per_page=100&page={n}")[key]
        out += got
        if len(got) < 100:
            return out
        n += 1


# ------------------------------------------------------------------ record
def record(head, specs):
    rows = []
    for spec in specs:
        rid, att = (int(x) for x in spec.split(":"))
        a = gh(f"repos/{REPO}/actions/runs/{rid}/attempts/{att}")
        jobs = []
        for j in pages(f"repos/{REPO}/actions/runs/{rid}/attempts/{att}/jobs", "jobs"):
            row = {k: j[k] for k in ("name", "status", "conclusion", "created_at", "started_at", "completed_at")}
            if j["name"] == "gate":
                row["judge_started_at"] = next((s["started_at"] for s in j.get("steps") or []
                                                if s["name"] == "Judge this head"), None)
            jobs.append(row)
        rows.append({"id": rid, "display_title": a["display_title"], "created_at": a["created_at"],
                     "updated_at": a["updated_at"], "status": a["status"], "conclusion": a["conclusion"],
                     "run_attempt": att, "jobs": sorted(jobs, key=lambda j: (j["created_at"], j["name"]))})
    print(json.dumps({"heads": {head: rows}}, indent=1, sort_keys=True))


# ------------------------------------------------------------------ replay
def at_time(rows, t, red=()):
    """The Actions API as it read at epoch t from recorded timestamps; `red` lists runs whose
    attempt-1 gate is read completed failure from its recorded completion on (gate-sweep.yml's view)."""
    out = []
    for r in rows:
        if epoch(r["created_at"]) > t:
            continue
        jobs = []
        for j in r["jobs"]:
            if epoch(j["created_at"]) > t:
                continue
            if j["status"] == "completed" and j["completed_at"] and epoch(j["completed_at"]) <= t:
                st, cc = "completed", j["conclusion"]
            elif j.get("started_at") and epoch(j["started_at"]) <= t:
                st, cc = "in_progress", None
            else:
                st, cc = "queued", None
            jobs.append({"name": j["name"], "status": st, "conclusion": cc, "id": r["id"] * 10 if j["name"] == "gate"
                         else 1, "started_at": j.get("started_at")})
        done = r["status"] == "completed" and epoch(r["updated_at"]) <= t
        out.append({"id": r["id"], "display_title": r["display_title"], "created_at": r["created_at"],
                    "status": "completed" if done else "in_progress", "run_attempt": r["run_attempt"],
                    "path": ".github/workflows/ci.yml", "head_sha": H3282,
                    "pull_requests": [{"number": 3282}], "jobs": jobs})
    return out


def load(ci):
    for m in MODULES:
        sys.modules.pop(m, None)
    sys.path[:0] = [str(ci)]
    return importlib.import_module("prelude"), importlib.import_module("gate"), importlib.import_module("sweep")


def replay(ci):
    prelude, gate, sweep = load(ci)
    fx = json.loads(FIXTURE.read_text())
    rows = fx["heads"][H3282]
    me = next(r for r in rows if r["id"] == EDIT)
    t0 = epoch(next(j for j in me["jobs"] if j["name"] == "gate")["judge_started_at"])
    pt = prelude.parse_title(me["display_title"])
    rec = fx["gates"][str(EDIT)]

    def judge_at(t_start, rid, attempt, views):
        naps = []

        def get(path, params=None):
            if sum(naps) > 2 * gate.GATE_WAIT_MAX_S:
                raise TimeoutError
            rs = views(t_start + sum(naps))
            if path.endswith("/pulls/3282"):
                return 200, {}, {"state": "open", "head": {"sha": H3282, "repo": {"full_name": REPO}},
                                 "base": {"ref": "main"}}
            if path.endswith("ci.yml/runs"):
                return 200, {}, {"workflow_runs": [{k: r[k] for k in ("id", "display_title", "status")} for r in rs]}
            i = int(path.split("/runs/")[1].split("/")[0])
            return 200, {}, {"jobs": next(r["jobs"] for r in rs if r["id"] == i)}
        ctx = prelude.context("pull_request", {"action": "edited", "pull_request": {
            "number": 3282, "base": {"ref": "main"}, "head": {"sha": H3282}}},
            {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": REPO, "GITHUB_RUN_ID": str(rid), "GITHUB_RUN_ATTEMPT": str(attempt)})
        claim = {"kind": pt[0], "pr": pt[1], "workset": set(rec["workset"].split())}
        try:
            return gate.judge(ctx, claim, get, lambda b, h: True, naps.append, lambda: sum(naps))[0], sum(naps)
        except TimeoutError:
            return "UNBOUNDED", sum(naps)

    first, wait = judge_at(t0, EDIT, 1, lambda t: at_time(rows, t))
    # gate-sweep.yml for the code run's completion; the edit gate's attempt 1 as the first verdict
    # left it (red unless it passed), the review run as recorded; no human re-run.
    t_sweep = epoch(next(r for r in rows if r["id"] == CODE)["updated_at"]) + 12
    posts = []

    def sview(t):
        rs = at_time(rows, t)
        for r in rs:
            if r["id"] == EDIT:
                g = next(j for j in r["jobs"] if j["name"] == "gate")
                g.update(status="completed", conclusion="success" if first == "PASS" else "failure")
                r["status"] = "completed"
        return rs
    clock = [t_sweep]

    def sget(path, params=None):
        rs = sview(clock[0])
        if path.endswith("/pulls/3282"):
            return 200, {}, {"head": {"sha": H3282}}
        if path.endswith("/actions/runs"):
            return 200, {}, {"workflow_runs": rs}
        r = next(r for r in rs if r["id"] == int(path.split("/runs/")[1].split("/")[0]))
        return 200, {}, ({"jobs": r["jobs"]} if path.endswith("/jobs") else r)

    def spost(path, body=None):
        posts.append(path)
        return 201, {}, {}

    def ssleep(s):
        clock[0] += s
    out = []
    sweep.main(["--run", str(CODE), "--repo", REPO], sget, spost, out.append, ssleep, lambda: clock[0])
    swept = f"actions/jobs/{EDIT * 10}/rerun" in " ".join(posts)
    final = first
    if swept:
        final, _ = judge_at(t_sweep + 20, EDIT, 2, lambda t: at_time(rows, t))
    print(f"replay: edit gate {EDIT} judged from {me['jobs'] and 'its recorded Judge this head start'}: "
          f"{first!r} after waiting {wait} s")
    for line in out:
        print(f"replay: sweep for code run {CODE}: {line}")
    print(f"replay: re-judged by the sweep's re-run: {final!r}" if swept else "replay: the sweep did not re-run it")
    print(f"RESULT replay wait_s={wait} first={first.split()[0]} swept={'yes' if swept else 'no'} final={final}")
    sys.path.remove(str(ci))
    return 0


# ------------------------------------------------------------------ census
def census(since, until):
    runs = pages(f"repos/{REPO}/actions/workflows/ci.yml/runs?created={since}..{until}", "workflow_runs")
    gates = []
    for r in runs:
        for j in pages(f"repos/{REPO}/actions/runs/{r['id']}/jobs?filter=all", "jobs"):
            if j["name"] == "gate":
                gates.append({"run": r["id"], "head": r["head_sha"], "attempt": j["run_attempt"], "job": j["id"],
                              "conclusion": j["conclusion"], "started": j["started_at"], "completed": j["completed_at"]})
    rows = []
    for g in gates:
        if g["conclusion"] != "failure":
            continue
        log = gh(f"repos/{REPO}/actions/jobs/{g['job']}/logs", raw=True)
        m = [DEFERRAL.search(line) for line in log.splitlines()]
        m = [x for x in m if x]
        if not m:
            continue
        ids = [int(i) for i in m[-1][1].split(",")]
        greens = [min((x["completed"] for x in gates if x["run"] == i and x["conclusion"] == "success"
                       and x["completed"] and x["completed"] >= g["completed"]), default=None) for i in ids]
        decided = None if None in greens else max(greens)
        later = sorted((x for x in gates if x["run"] == g["run"] and x["attempt"] > g["attempt"]),
                       key=lambda x: x["attempt"])
        nxt = later[0] if later else None
        green = next((x for x in later if x["conclusion"] == "success"), None)
        actor = (gh(f"repos/{REPO}/actions/runs/{g['run']}/attempts/{nxt['attempt']}").get("triggering_actor")
                 or {}).get("login") if nxt else None
        rows.append({**g, "deferred_to": ids, "held_s": int(epoch(g["completed"]) - epoch(g["started"])),
                     "decided": decided, "next_attempt": nxt and nxt["attempt"], "next_actor": actor,
                     "green": green and green["completed"]})
    for x in sorted(rows, key=lambda x: x["completed"]):
        print(f"census: {x['completed']} head {x['head'][:8]} run {x['run']} a{x['attempt']} held {x['held_s']} s "
              f"defer->{x['deferred_to']} decided {x['decided']} next a{x['next_attempt']} by {x['next_actor']} "
              f"green {x['green']}")
    heads = {}
    for x in rows:
        heads[x["head"]] = heads.get(x["head"], 0) + 1
    res = [x for x in rows if x["decided"] and x["green"] and x["green"] >= x["decided"]]
    mins = sorted((epoch(x["green"]) - epoch(x["decided"])) / 60 for x in res)
    print(f"RESULT census deferral_fails={len(rows)} heads={len(heads)} per_head_max={max(heads.values(), default=0)} "
          f"held_runner_s={sum(x['held_s'] for x in rows)} held_ge_600={sum(x['held_s'] >= 600 for x in rows)} "
          f"resolved={len(res)} by_bot={sum(x['next_actor'] == 'github-actions[bot]' for x in res)} "
          f"by_human={sum(x['next_actor'] not in (None, 'github-actions[bot]') for x in res)} "
          f"median_min={round(mins[len(mins) // 2], 1) if mins else None}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="arm", required=True)
    r = sub.add_parser("record")
    r.add_argument("head")
    r.add_argument("specs", nargs="+")
    p = sub.add_parser("replay")
    p.add_argument("--ci", default=str(ROOT / "tools" / "ci"))
    c = sub.add_parser("census")
    c.add_argument("--since", required=True)
    c.add_argument("--until", required=True)
    a = ap.parse_args(argv)
    if a.arm == "record":
        return record(a.head, a.specs) or 0
    if a.arm == "replay":
        return replay(Path(a.ci).resolve())
    return census(a.since, a.until)


if __name__ == "__main__":
    sys.exit(main())
