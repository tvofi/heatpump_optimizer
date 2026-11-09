#!/usr/bin/env python3
"""R10-RCA-GATE-BUSY-DEFER-2: replay recorded live run/job listings through a gate program.

Root-cause seat harness (dev/audit/rca/r10-gate-busy-defer-2.md). The two harnesses #3246
was proven with (r10_gate_defer_race.py, r10_ci_gate_core.py) build their run listings by
hand and import ONE copy of tools/ci per scene. This one feeds the gate the listings GitHub
actually served, reconstructed from recorded job timestamps, and names the program copy each
live gate ran (its `programs restored from <sha>` line), so it can answer the question those
harnesses could not ask: which program judged the red.

Arms:
  record OUT.json [--scene NAME]
                         read the scenes below from the GitHub API (gh api), write the fixture;
                         with --scene, re-read that one scene into the existing fixture only
  replay --ci DIR        judge every scene's gates with DIR's gate.py; print one line per scene
                         and exit 1 on a defect class: a pair scene's gate defers to its partner
                         (DEADLOCK: every one does; HALF-DEFERRED: some do; the live #3241/#3246/#3244
                         defect), or a scene in WANT reads another verdict (MISREAD: 3252-nosource's
                         gate took a stale red as its source). A single edit gate that publishes its deferral to a code run at once,
                         naps 0, is C3-AT-ONCE: #3263's defect under #3276, the design since #3287
                         (5c1fa41f: a deferral holds no runner, gate-sweep.yml re-judges it), so no
                         defect; nor is a gate that waited and then deferred (DEFERRED). The single-gate
                         scenes judge one gate beside a code run listed as recorded, so they see the
                         at-once bound and not the wait cycle judging() once made (#3276's fixture
                         self-test in gate.py pins that)
  census --since ISO [--until ISO]
                         live: every `gate` job started in the window on a ci.yml run, by
                         whether its pinned programs carry the fix (--fix SHA; no pin line:
                         unpinned), its verdict class, and whether it was a re-run attempt
  pins                   per scene: the pinned sha each live gate ran, and whether that sha
                         carries the #3246 fix (355d9965); needs the repository's history

The fixture is dev/audit/harnesses/r10_rca_gate_busy_defer_2.json (default --fixture).
A scene's snapshot at time T: a run is listed if created by T, under the attempt started
latest by T; a job is listed if created by T, `completed` if it completed by T, `in_progress`
if it started by T, else `queued`. The judging gates themselves are simulated, concurrently as
they ran live (the harness refuses a pair whose gates did not overlap): each first reads beside
its partner's gate `in_progress`; a gate that waited is re-judged with every partner that decided
at once `completed` from that verdict's time.
"""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
FIX = "355d9965a7a14ec45ef8cd25fb9c75c5ced044f1"        # #3246's merge
FIXTURE = Path(__file__).with_suffix(".json")
READ_AFTER_S = 20       # a gate's first read lands ~20 s after its job starts (#2754's edit gate: 21 s in all)
MODULES = ("prelude", "gate", "ghapi", "codeql_scope", "sweep")
# (scene, pr, head sha, [(run id, attempt) of each judging gate]); every gate here published red live.
SCENES = [
    ("3261-pair", "3261", "e17fadc1795ebbaaf0f01ed067fbb59aeba90dee", [(42307493684, 8), (42307798573, 8)]),
    ("3265-pair", "3265", "c7c5cef52a49bed59ee4c8a42e495ef2dae30db5", [(42332777827, 4), (42333388705, 4)]),
    ("3255-pair", "3255", "2ad28ecb50906877b34a378cacd8085e6afca029", [(42321825054, 5), (42322943199, 4)]),
    # three edit gates, attempt 2, started within 2 s after the code run's gate went green (r10-hotfix-gate-busy-defer-p5)
    # the code run's re-run gate (attempt 2, 17:14:38Z) beside two edit runs whose pr-contract failed
    # closed on codescan_wait's no-source refusal before its own pr-contract ran green (carry 10)
    ("3252-nosource", "3252", "3134798017b1d26994c410206349b06d187559a0", [(42385416529, 2)]),
    ("3244-triple", "3244", "a258212553e123d735c7eff139a8e347a1a52ea3", [(42286558101, 2), (42286624031, 2), (42293328283, 2)]),
    ("3263-c3", "3263", "02e92e7cbcb95c32fbb2ad3a7a46a8d465a436d8", [(42338396358, 1)]),
    ("3261-c3", "3261", "61187afe6cfdc4416f161e23111571bc50d25d9c", [(42338828285, 1)]),
    ("3241-c3", "3241", "3720667a319cca90628a6b4167e3774408cb60a3", [(42338898175, 1)]),
]


def ts(s):
    return None if not s else datetime.fromisoformat(s.replace("Z", "+00:00"))


def iso(t):
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- record (live, gh api)
def gh(path):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"gh api {path}: {p.stderr.strip()}")
    return json.loads(p.stdout) if p.stdout.strip().startswith(("{", "[")) else p.stdout


def gate_log(job_id):
    p = subprocess.run(["gh", "api", f"repos/{REPO}/actions/jobs/{job_id}/logs"], capture_output=True, text=True)
    pin = workset = verdict = None
    for line in p.stdout.splitlines():
        line = line.split(" ", 1)[1] if line[:4].isdigit() and " " in line else line
        if line.startswith("programs restored from "):
            pin = line.split()[3]
        elif line.strip().startswith("WORKSET:"):
            workset = line.split(":", 1)[1].strip()
        elif verdict is None and (line.startswith("FAIL") or line == "PASS"):
            verdict = line
    return {"pin": pin, "workset": workset, "verdict": verdict}


def record(out, only=None):
    doc = {"repo": REPO, "recorded_at": iso(datetime.now(timezone.utc)), "scenes": []}
    if only:
        doc = json.loads(Path(out).read_text())
        doc["scenes"] = [s for s in doc["scenes"] if s["name"] != only]
    for name, pr, head, gates in SCENES:
        if only and name != only:
            continue
        runs = gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?head_sha={head}&per_page=100")["workflow_runs"]
        rec = []
        for r in runs:
            atts = []
            for n in range(1, r["run_attempt"] + 1):
                a = gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/{n}")
                jobs = gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/{n}/jobs?per_page=100")["jobs"]
                atts.append({"n": n, "run_started_at": a["run_started_at"], "jobs": [
                    {k: j[k] for k in ("id", "name", "status", "conclusion", "created_at", "started_at",
                                       "completed_at")} for j in jobs]})
            rec.append({"id": r["id"], "title": r["display_title"], "created_at": r["created_at"],
                        "attempts": atts})
        live = []
        for rid, n in gates:
            run = next(x for x in rec if x["id"] == rid)
            g = next(j for j in run["attempts"][n - 1]["jobs"] if j["name"] == "gate")
            live.append({"run": rid, "attempt": n, "job": g["id"], "started_at": g["started_at"],
                         "completed_at": g["completed_at"], "conclusion": g["conclusion"], **gate_log(g["id"])})
        doc["scenes"].append({"name": name, "pr": pr, "head": head, "runs": rec, "gates": live})
    doc["scenes"].sort(key=lambda s: [x[0] for x in SCENES].index(s["name"]))
    Path(out).write_text(json.dumps(doc, indent=1) + "\n")
    print(f"recorded {len(doc['scenes'])} scenes to {out}")
    return 0


# ---------------------------------------------------------------- snapshot
def snapshot(scene, t, sim):
    """[{id, title, status, jobs: {name: (status, conclusion)}}] as listed at t. `sim` maps a
    judging gate's run id to (finished_at or None, conclusion): its gate is simulated."""
    out = []
    for r in scene["runs"]:
        if ts(r["created_at"]) > t:
            continue
        att = [a for a in r["attempts"] if ts(a["run_started_at"]) <= t]
        if not att:
            continue
        jobs, starts = {}, {}
        for j in att[-1]["jobs"]:
            if ts(j["started_at"]) and ts(j["started_at"]) <= t:
                starts[j["name"]] = j["started_at"]     # the gate's source order reads it (r10-hotfix-gate-busy-defer-p5)
            if ts(j["created_at"]) and ts(j["created_at"]) > t:
                continue
            if j["name"] == "gate" and r["id"] in sim:
                fin, concl = sim[r["id"]]
                jobs["gate"] = ("completed", concl) if fin is not None and fin <= t else ("in_progress", None)
            elif ts(j["completed_at"]) and ts(j["completed_at"]) <= t and j["status"] == "completed":
                jobs[j["name"]] = ("completed", j["conclusion"])
            elif ts(j["started_at"]) and ts(j["started_at"]) <= t:
                jobs[j["name"]] = ("in_progress", None)
            else:
                jobs[j["name"]] = ("queued", None)
        status = "completed" if jobs and all(s == "completed" for s, _ in jobs.values()) else "in_progress"
        out.append({"id": r["id"], "title": r["title"], "status": status, "jobs": jobs, "starts": starts})
    return out


# ---------------------------------------------------------------- replay
def load(ci):
    for m in MODULES:
        sys.modules.pop(m, None)
    sys.path[:0] = [str(ci)]
    try:
        return importlib.import_module("gate")
    finally:
        sys.path.remove(str(ci))


def judge_one(gate, scene, g, t0, sim):
    """Run gate.judge for live gate g, its first read at t0; (outcome, verdict time, naps)."""
    clock = {"t": t0, "naps": 0}
    run = next(r for r in scene["runs"] if r["id"] == g["run"])
    sha = run["title"].split("sha=")[1]

    def get(path, params=None):
        listing = snapshot(scene, clock["t"], sim)
        if path.endswith(f"/pulls/{scene['pr']}"):
            return 200, {}, {"head": {"sha": scene["head"], "repo": {"full_name": REPO}},
                             "base": {"ref": "main"}, "state": "open"}
        if path.endswith("/actions/workflows/ci.yml/runs"):
            return 200, {}, {"workflow_runs": [{"id": r["id"], "display_title": r["title"], "status": r["status"]}
                                               for r in listing]}
        if "/actions/runs/" in path and path.endswith("/jobs"):
            rid = int(path.split("/actions/runs/")[1].split("/")[0])
            r = next((x for x in listing if x["id"] == rid), None)
            jobs, starts = (dict(r["jobs"]), r["starts"]) if r else ({}, {})
            if rid == g["run"]:
                jobs["gate"] = ("in_progress", None)        # this gate is the one judging
            return 200, {}, {"jobs": [{"name": k, "status": s, "conclusion": c, "started_at": starts.get(k)}
                                      for k, (s, c) in jobs.items()]}
        return 404, {}, {"message": f"fixture serves no {path}"}

    def sleep(s):
        clock["t"] += timedelta(seconds=s)
        clock["naps"] += 1

    def now():
        return (clock["t"] - t0).total_seconds()

    ctx = gate.context("pull_request", {"action": "edited" if " edit " in run["title"] else "synchronize",
                                         "pull_request": {"number": int(scene["pr"]), "base": {"ref": "main"},
                                                          "head": {"sha": scene["head"]}}},
                       {"GITHUB_SHA": sha, "GITHUB_REPOSITORY": REPO, "GITHUB_RUN_ID": str(g["run"]),
                        "GITHUB_RUN_ATTEMPT": str(g["attempt"])})
    kind = gate.parse_title(run["title"])[0]
    claim = {"kind": kind, "pr": scene["pr"]}
    if g.get("workset") is not None:
        claim["workset"] = set(g["workset"].split())
    outcome, _, _ = gate.judge(ctx, claim, get, reaches=lambda b, h: False, sleep=sleep, now=now)
    return outcome, clock["t"], clock["naps"]


# Classes that make replay exit 1. C3-AT-ONCE was a defect from #3276 (812bb8747), which deleted gate.py's at-once
# bound for a deferring edit gate (the cause was prelude.judging() reading the deferring run's skipped
# `pr-contract` caller as owed); DEFERRED after naps is the bounded wait, a designed outcome.
# A scene whose every gate must read one verdict once its sources are judged by their freshest read:
# 3252-nosource's code run gate, its own pr-contract started after both edit runs' no-source reds.
WANT = {"3252-nosource": "PASS"}
DEFECTS = ("DEADLOCK", "HALF-DEFERRED", "MISREAD")    # C3-AT-ONCE left them at #3287 (5c1fa41f): the at-once deferral is its design


def classify(scene, verdicts):
    pair = {g["run"] for g in scene["gates"]}
    deferred_to = {}
    for rid, (out, _, _) in verdicts.items():
        if "are still being judged" in out:
            ids = {int(x) for x in out.split("[")[1].split("]")[0].split(",")}
            deferred_to[rid] = ids
    if len(pair) > 1:
        if all(rid in deferred_to and deferred_to[rid] & (pair - {rid}) for rid in pair):
            return "DEADLOCK"
        if any(deferred_to.get(rid, set()) & (pair - {rid}) for rid in pair):
            return "HALF-DEFERRED"
        return "DECIDED"
    (rid,) = pair
    if rid in deferred_to:
        others = deferred_to[rid]
        codes = [r for r in scene["runs"] if r["id"] in others and " code " in r["title"]]
        return "C3-AT-ONCE" if codes and verdicts[rid][2] == 0 else "DEFERRED"
    return "DECIDED"


def replay(fixture, ci):
    gate = load(Path(ci).resolve())
    doc = json.loads(Path(fixture).read_text())
    rc = 0
    for scene in doc["scenes"]:
        gates = sorted(scene["gates"], key=lambda g: g["run"])
        for g in gates:                                     # every judging gate's precondition: listed started
            if ts(g["started_at"]) is None:
                raise SystemExit(f"{scene['name']}: gate of run {g['run']} never started; fixture unusable")
        for g in gates:                                     # the pair's gates overlapped live: both started
            for o in gates:                                 # before the other's first read
                if o is not g and not ts(o["started_at"]) <= ts(g["started_at"]) + timedelta(seconds=READ_AFTER_S):
                    raise SystemExit(f"{scene['name']}: gate {o['run']} had not started by {g['run']}'s read")
        sim = {g["run"]: (None, None) for g in gates}       # pass 1: every partner's gate in_progress throughout
        verdicts = {g["run"]: judge_one(gate, scene, g, ts(g["started_at"]) + timedelta(seconds=READ_AFTER_S), sim)
                    for g in gates}
        if any(n for _, _, n in verdicts.values()):         # pass 2: a gate that waited sees each partner that
            sim = {rid: ((fin, "success" if out == "PASS" else "failure") if n == 0 else (None, None))
                   for rid, (out, fin, n) in verdicts.items()}   # decided at once finish when it did
            verdicts = {g["run"]: (verdicts[g["run"]] if verdicts[g["run"]][2] == 0 else judge_one(
                gate, scene, g, ts(g["started_at"]) + timedelta(seconds=READ_AFTER_S), sim)) for g in gates}
        cls = classify(scene, verdicts)
        if scene["name"] in WANT and any(out != WANT[scene["name"]] for out, _, _ in verdicts.values()):
            cls = "MISREAD"
        rc |= cls in DEFECTS
        detail = "; ".join(f"{rid}: {out[:60]} naps={n}" for rid, (out, _, n) in sorted(verdicts.items()))
        print(f"{scene['name']}: {cls} | {detail}")
    print(f"RESULT replay ci={ci} defects={'yes' if rc else 'no'}")
    return rc


def census(since, until, fix):
    """Every gate verdict since `since`: pinned sha, carries `fix`?, conclusion, class, seconds."""
    rows, page = [], 1
    while True:
        doc = gh(f"repos/{REPO}/actions/workflows/ci.yml/runs?per_page=100&page={page}")
        runs = [r for r in doc["workflow_runs"] if r["updated_at"] >= since]
        if not runs:
            break
        for r in runs:
            for n in range(1, r["run_attempt"] + 1):
                jobs = gh(f"repos/{REPO}/actions/runs/{r['id']}/attempts/{n}/jobs?per_page=100")["jobs"]
                for j in jobs:
                    if j["name"] != "gate" or j["status"] != "completed" or not j["started_at"] \
                            or not since <= j["started_at"] < until or j["run_attempt"] != n:
                        continue
                    lg = gate_log(j["id"])
                    ok = bool(lg["pin"]) and subprocess.run(
                        ["git", "merge-base", "--is-ancestor", fix, lg["pin"]]).returncode == 0
                    v = lg["verdict"] or ""
                    cls = "pass" if v == "PASS" else "defer" if "are still being judged" in v else \
                        "other-red" if j["conclusion"] == "failure" else j["conclusion"]
                    secs = (ts(j["completed_at"]) - ts(j["started_at"])).total_seconds()
                    rows.append((r["id"], n, r["display_title"].split()[2], "fixed" if ok else "stale" if lg["pin"] else "unpinned", cls, secs))
        page += 1
    for row in sorted(rows):
        print("\t".join(map(str, row)))
    for pin in ("stale", "fixed", "unpinned"):
        sub = [x for x in rows if x[3] == pin]
        by = {c: sum(1 for x in sub if x[4] == c) for c in sorted({x[4] for x in sub})}
        print(f"CENSUS {pin}: gates={len(sub)} {by} prs={sorted({x[2] for x in sub if x[4] == 'defer'})} "
              f"reruns={sum(1 for x in sub if x[1] > 1)} "
              f"defer_job_s={int(sum(x[5] for x in sub if x[4] == 'defer'))}")
    return 0


def pins(fixture):
    doc = json.loads(Path(fixture).read_text())
    stale = 0
    for scene in doc["scenes"]:
        for g in scene["gates"]:
            pin = g["pin"]
            ok = pin and subprocess.run(["git", "merge-base", "--is-ancestor", FIX, pin]).returncode == 0
            stale += not ok
            print(f"{scene['name']} run {g['run']} attempt {g['attempt']}: pinned {pin[:10] if pin else None} "
                  f"{'CARRIES' if ok else 'LACKS'} {FIX[:10]} | live: {g['verdict'][:70] if g['verdict'] else None}")
    print(f"RESULT pins gates={sum(len(s['gates']) for s in doc['scenes'])} stale={stale}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("arm", choices=("record", "replay", "pins", "census"))
    ap.add_argument("out", nargs="?")
    ap.add_argument("--ci", default=str(Path(__file__).resolve().parents[3] / "tools" / "ci"))
    ap.add_argument("--fixture", default=str(FIXTURE))
    ap.add_argument("--since", default="2026-11-07T03:45:14Z")    # 355d9965's merge
    ap.add_argument("--until", default="9999")
    ap.add_argument("--fix", default=FIX)
    ap.add_argument("--scene")
    a = ap.parse_args(argv)
    if a.arm == "record":
        return record(a.out or a.fixture, a.scene)
    if a.arm == "census":
        return census(a.since, a.until, a.fix)
    if a.arm == "pins":
        return pins(a.fixture)
    return replay(a.fixture, a.ci)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
