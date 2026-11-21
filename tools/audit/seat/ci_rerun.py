#!/usr/bin/env python3
"""Rerun only the failed REQUIRED jobs of a pull request's head runs (CI-6, P-R11-CI-SCOPED-RERUN).

    python3 -I tools/audit/seat/ci_rerun.py PR [--repo R] [--dry-run] [--dispatch]
    python3 -I tools/audit/seat/ci_rerun.py PR --record DIR
    python3 -I tools/audit/seat/ci_rerun.py --self-test

Per (workflow path, run name) the latest run at the PR's live head is judged:
  WAIT   still active, never rerun;
  OK     concluded success, skipped or neutral;
  CAP    at attempt MAX_ATTEMPT or past it, not rerun;
  SKIP   every failed job is outside the ruleset's required contexts: one
         `SKIP non-required <job>` line each, nothing rerun;
  RERUN  a failed, cancelled or timed-out job is required (or none is listed):
         POST rerun-failed-jobs, which re-executes the failed jobs alone;
  NORUN  no run at the head: `--dispatch` starts ci.yml naming the PR and its
         base (an undispatched PR head is gate.py's refusal), else it says so.
Only the head's runs are read, so a push run on main is never touched. The
required set is every active ruleset's `required_status_checks`, read live and
cached ten minutes in $HPO_STATE_DIR (unset: no cache). `--dry-run` (or DRY=1)
prints what it would POST. An unreadable pull request, ruleset or run listing
does nothing and says so. `--record` writes the PR's live reads as a fixture
directory for the self-test.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "ci_rerun" / "pr3836"
FAILED = ("failure", "cancelled", "timed_out", "startup_failure")
GREEN = ("success", "skipped", "neutral")
MAX_ATTEMPT = 6
CACHE_S = 600


def live_api(path: str, method: str = "GET"):
    p = subprocess.run(["gh", "api", "-X", method, path], capture_output=True, text=True)
    if p.returncode != 0:
        print(f"ci_rerun: gh api {path} rc={p.returncode}: {p.stderr.strip()[-160:]}", file=sys.stderr)
        return None
    try:
        return json.loads(p.stdout) if p.stdout.strip() else {}
    except ValueError:
        return None


def required_contexts(api, repo: str, cache: "Path | None") -> "set[str] | None":
    """The required status contexts of every active ruleset; None when unreadable."""
    if cache and cache.exists() and time.time() - cache.stat().st_mtime < CACHE_S:
        try:
            return set(json.loads(cache.read_text()))
        except ValueError:
            pass
    rs = api(f"repos/{repo}/rulesets")
    if not isinstance(rs, list):
        return None
    ctx = set()
    for r in rs:
        if r.get("enforcement") != "active":
            continue
        d = api(f"repos/{repo}/rulesets/{r['id']}")
        if not isinstance(d, dict):
            return None
        for rule in d.get("rules", []):
            if rule.get("type") == "required_status_checks":
                ctx |= {c["context"] for c in rule["parameters"]["required_status_checks"]}
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(sorted(ctx)))
    return ctx


def is_required(job: str, ctx) -> bool:
    """A job is required when its check name is a required context, or ends in ` / <context>`."""
    return any(job == c or job.endswith(" / " + c) for c in ctx)


def plan(sha: str, runs: list, jobs_of, ctx) -> "list[tuple[str, int, str]]":
    """Pure: [(action, run id, text)] over the runs at <sha>; jobs_of(run id) lists a run's jobs."""
    groups: dict = {}
    for r in runs:
        if r.get("head_sha") != sha:
            continue
        k = (r.get("path"), r.get("name"))
        if k not in groups or int(r["id"]) > int(groups[k]["id"]):
            groups[k] = r
    if not groups:
        return [("NORUN", 0, f"no run at {sha[:8]}")]
    out = []
    for (path, name), r in sorted(groups.items(), key=lambda kv: int(kv[1]["id"])):
        rid = int(r["id"])
        label = f"{(path or '').split('/')[-1]} '{name}' run {rid}"
        if r.get("status") != "completed":
            out.append(("WAIT", rid, f"{label} {r.get('status')}"))
        elif r.get("conclusion") in GREEN:
            out.append(("OK", rid, f"{label} {r.get('conclusion')}"))
        elif int(r.get("run_attempt") or 1) >= MAX_ATTEMPT:
            out.append(("CAP", rid, f"{label} at attempt {r.get('run_attempt')}: not rerun"))
        else:
            bad = [j["name"] for j in jobs_of(rid) if j.get("conclusion") in FAILED]
            req = [j for j in bad if is_required(j, ctx)]
            if bad and not req:
                out += [("SKIP", rid, f"non-required {j}") for j in bad]
            else:
                out.append(("RERUN", rid, f"{label} failed={','.join(req or ['(none listed)'])}"))
    return out


def run(pr: int, repo: str, api, dry: bool, dispatch: bool = False, start=subprocess.run,
        cache: "Path | None" = None) -> int:
    p = api(f"repos/{repo}/pulls/{pr}")
    if not isinstance(p, dict) or p.get("state") != "open":
        print(f"ci_rerun: #{pr} unreadable or not open; nothing done")
        return 0
    sha, branch, base = p["head"]["sha"], p["head"]["ref"], (p.get("base") or {}).get("ref", "")
    ctx = required_contexts(api, repo, cache)
    ls = api(f"repos/{repo}/actions/runs?head_sha={sha}&per_page=100")
    if ctx is None or not isinstance(ls, dict):
        print("ci_rerun: unreadable reads; nothing done")
        return 0

    def jobs_of(rid):
        return (api(f"repos/{repo}/actions/runs/{rid}/jobs?per_page=100") or {}).get("jobs", [])
    print(f"ci_rerun: #{pr} head {sha[:8]} required={sorted(ctx)}{' DRY' if dry else ''}")
    for act, rid, text in plan(sha, ls.get("workflow_runs", []), jobs_of, ctx):
        if act == "SKIP":
            print(f"SKIP {text} (run {rid})")
        elif act == "RERUN" and dry:
            print(f"RERUN would: POST runs/{rid}/rerun-failed-jobs :: {text}")
        elif act == "RERUN":
            got = api(f"repos/{repo}/actions/runs/{rid}/rerun-failed-jobs", "POST")
            print(f"RERUN {'done' if got is not None else 'FAILED'} {text}")
        elif act == "NORUN" and dispatch and not dry:
            argv = ["gh", "workflow", "run", "ci.yml", "-R", repo, "--ref", branch, "-f", f"pr={pr}", "-f", f"base={base}"]
            print(f"NORUN {text}: dispatched ci.yml on {branch} rc={start(argv).returncode}")
        elif act == "NORUN":
            print(f"NORUN {text}" + (" (DRY)" if dispatch else " (--dispatch would run ci.yml on the branch)"))
        else:
            print(f"{act} {text}")
    return 0


def record(pr: int, d: str, repo: str = REPO) -> None:
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    p = live_api(f"repos/{repo}/pulls/{pr}")
    sha = p["head"]["sha"]
    runs = live_api(f"repos/{repo}/actions/runs?head_sha={sha}&per_page=100")["workflow_runs"]
    keep = ["id", "name", "path", "head_sha", "status", "conclusion", "run_attempt", "event", "head_branch"]
    (d / "runs.json").write_text(json.dumps([{k: r.get(k) for k in keep} for r in runs], indent=1))
    (d / "pr.json").write_text(json.dumps({"number": pr, "state": p["state"], "head": {"sha": sha, "ref": p["head"]["ref"]}}))
    for r in runs:
        j = live_api(f"repos/{repo}/actions/runs/{r['id']}/jobs?per_page=100")
        (d / f"jobs-{r['id']}.json").write_text(json.dumps(
            [{"name": x["name"], "status": x["status"], "conclusion": x["conclusion"]} for x in j["jobs"]], indent=1))
    (d / "required.json").write_text(json.dumps(sorted(required_contexts(live_api, repo, None))))
    print(f"recorded {len(runs)} runs of #{pr} at {sha[:8]} into {d}")


def self_test() -> int:
    runs = json.loads((FIXTURE / "runs.json").read_text())
    ctx = set(json.loads((FIXTURE / "required.json").read_text()))
    pr = json.loads((FIXTURE / "pr.json").read_text())
    sha = pr["head"]["sha"]
    jobs = {r["id"]: json.loads((FIXTURE / f"jobs-{r['id']}.json").read_text()) for r in runs}
    fails = n = 0

    def chk(label, got, want):
        nonlocal fails, n
        n += 1
        fails += got != want
        print(f"  {'ok  ' if got == want else 'FAIL'} {label}" + ("" if got == want else f": got {got!r}, want {want!r}"))

    def acts(rs, jb, c=ctx, s=sha):
        return [(a, i) for a, i, _ in plan(s, rs, lambda i: jb.get(i, []), c)]
    base = acts(runs, jobs)
    latest_failed = max(r["id"] for r in runs if r["conclusion"] == "failure")
    older_failed = min(r["id"] for r in runs if r["conclusion"] == "failure")
    queued = [r["id"] for r in runs if r["status"] != "completed"]
    chk("recorded: a failed required gate reruns the latest failed run", ("RERUN", latest_failed) in base, True)
    chk("recorded: a queued run waits, is never rerun", all(("WAIT", q) in base for q in queued) and bool(queued), True)
    chk("recorded: a skipped run is OK", any(a == "OK" for a, _ in base), True)
    chk("recorded: only the LATEST run of a (workflow, name) is judged", sum(1 for _, i in base if i == older_failed),
        0 if older_failed != latest_failed else 1)
    m = acts(runs, jobs, c={"never-a-real-check"})
    chk("mutation: failed jobs all non-required -> no RERUN", any(a == "RERUN" for a, _ in m), False)
    chk("mutation: failed jobs all non-required -> SKIP", any(a == "SKIP" for a, _ in m), True)
    chk("no run at head -> NORUN", acts(runs, jobs, s="0" * 40), [("NORUN", 0)])
    capped = [dict(r, run_attempt=MAX_ATTEMPT) if r["id"] == latest_failed else r for r in runs]
    chk("attempt cap -> CAP, not RERUN", ("CAP", latest_failed) in acts(capped, jobs), True)
    chk("null: one attempt below the cap still reruns",
        ("RERUN", latest_failed) in acts([dict(r, run_attempt=MAX_ATTEMPT - 1) if r["id"] == latest_failed else r
                                          for r in runs], jobs), True)
    chk("failed run with no job listed -> RERUN", ("RERUN", latest_failed) in acts(runs, {**jobs, latest_failed: []}), True)
    chk("'x / gate' counts as the required gate", is_required("ci / gate", {"gate"}), True)
    chk("'gate2' is not the gate", is_required("gate2", {"gate"}), False)

    # End to end over a stub API: the live head's PR, the rulesets, the listing, one POST.
    def stub(runs_at, rulesets=True):
        posts, started = [], []

        def api(path, method="GET"):
            if method == "POST":
                posts.append(path)
                return {}
            if path.endswith(f"/pulls/{pr['number']}"):
                return {**pr, "base": {"ref": "main"}}
            if path.endswith("/rulesets"):
                return [{"id": 1, "enforcement": "active"}] if rulesets else None
            if path.endswith("/rulesets/1"):
                return {"rules": [{"type": "required_status_checks",
                                   "parameters": {"required_status_checks": [{"context": c} for c in ctx]}}]}
            if "/actions/runs?head_sha=" in path:
                return {"workflow_runs": runs_at}
            return {"jobs": jobs.get(int(path.split("/runs/")[1].split("/")[0]), [])}

        def start(argv):
            started.append(argv)
            return subprocess.CompletedProcess(argv, 0)
        return api, start, posts, started

    import contextlib
    import io
    for label, dry, want in (("live: POSTs rerun-failed-jobs for the latest failed run alone", False,
                              [f"repos/{REPO}/actions/runs/{latest_failed}/rerun-failed-jobs"]),
                             ("null: --dry-run POSTs nothing", True, [])):
        api, start, posts, _ = stub(runs)
        with contextlib.redirect_stdout(io.StringIO()):
            run(pr["number"], REPO, api, dry, start=start)
        chk(label, posts, want)
    api, start, posts, started = stub([])
    with contextlib.redirect_stdout(io.StringIO()):
        run(pr["number"], REPO, api, False, dispatch=True, start=start)
    chk("--dispatch with no run at the head starts ci.yml naming the PR and its base",
        started, [["gh", "workflow", "run", "ci.yml", "-R", REPO, "--ref", pr["head"]["ref"],
                   "-f", f"pr={pr['number']}", "-f", "base=main"]])
    api, start, posts, started = stub(runs, rulesets=False)
    with contextlib.redirect_stdout(io.StringIO()):
        run(pr["number"], REPO, api, False, dispatch=True, start=start)
    chk("an unreadable ruleset reruns and dispatches nothing", (posts, started), ([], []))
    print(f"ci_rerun self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(a: "list[str]") -> int:
    if a[:1] == ["--self-test"]:
        return self_test()
    if not a or not a[0].isdigit():
        print(__doc__)
        return 2
    pr = int(a[0])
    repo = a[a.index("--repo") + 1] if "--repo" in a else REPO
    if "--record" in a:
        record(pr, a[a.index("--record") + 1], repo)
        return 0
    state = os.environ.get("HPO_STATE_DIR")
    return run(pr, repo, live_api, "--dry-run" in a or os.environ.get("DRY") == "1", "--dispatch" in a,
               cache=Path(state) / "ci-rerun-required.json" if state else None)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
