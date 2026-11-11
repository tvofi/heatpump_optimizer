#!/usr/bin/env python3
"""R10-CI-SLIM card C3: what CI 'edit' runs cost, before and after the deferral.

    python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py --fetch SAMPLE.json --since T0 --until T1
    python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py SAMPLE.json [--prelude PATH]
    python3 dev/audit/harnesses/r10_ci_slim/edit_runs.py --self-test

--fetch records every ci.yml run created in [T0, T1) with its latest jobs
(name, started_at, completed_at, conclusion), its title and head SHA: the
recorded sample. The replay reads it offline.

THE RULE. A job costs completed_at - started_at (job-minutes; queueing is not
counted, as the card counted). An edit run is a run whose title parses to kind
`edit` (prelude.parse_title). For each, the replay rebuilds the Actions state
its prelude read, at the prelude job's started_at: every run at the same head
created by then, `completed` if its last job had ended, its jobs listed when
they had started, `completed` when they had ended. It hands that state to the
PRODUCTION predicate, prelude.defer_to, imported from --prelude (default: this
tree's tools/ci/prelude.py; give the merge base's copy for the control, which
has no defer_to and so defers nothing). A run it defers costs, after: its
jobs less `pr-contract` (skipped), with its prelude priced at the median
prelude of the sample's CODE runs (a prelude that never waits); every other
job, the gate included, at its recorded duration (conservative: the
deferring gate publishes at once). A run it does not defer costs what it cost.

NULL CONTROLS, printed beside the result: (1) the same predicate over the
sample's code runs, as if each were an edit run: a code run is never deferred
by another (0 expected only where no two code runs share a head; the count is
printed, not asserted); (2) the merge base's prelude defers nothing, so its
after equals its before.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
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


ROOT = repo_root(__file__)


def load_prelude(path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"prelude_{abs(hash(str(path)))}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None


def minutes(job) -> float:
    a, b = ts(job.get("started_at")), ts(job.get("completed_at"))
    return (b - a) / 60 if a is not None and b is not None and b >= a else 0.0


def fetch(out: Path, since: str, until: str) -> int:
    sys.path.insert(0, str(ROOT / "tools" / "ci"))
    import ghapi
    repo = "tvofi/heatpump_optimizer"
    def pages(path, params, key):
        # Paged by `page=` on the repos/ path: the API's own next links name
        # repositories/{id}, which the session proxy refuses.
        out, page = [], 1
        while True:
            st, _, doc = ghapi.get(path, {**params, "per_page": 100, "page": page})
            if st != 200 or not isinstance(doc, dict):
                raise SystemExit(f"{path} page {page}: HTTP {st}")
            got = doc.get(key) or []
            out += got
            if len(got) < 100:
                return out
            page += 1
    runs = pages(f"repos/{repo}/actions/workflows/ci.yml/runs",
                 {"created": f"{since}..{until}", "exclude_pull_requests": "true"}, "workflow_runs")
    rows = []
    for r in runs:
        jobs = pages(f"repos/{repo}/actions/runs/{r['id']}/jobs", {"filter": "latest"}, "jobs")
        rows.append({"id": r["id"], "title": r.get("display_title") or "", "head_sha": r["head_sha"],
                     "event": r["event"], "created_at": r["created_at"], "status": r["status"],
                     "jobs": [{k: j.get(k) for k in ("name", "status", "conclusion", "started_at", "completed_at")}
                              for j in jobs]})
    out.write_text(json.dumps({"since": since, "until": until, "runs": rows}, indent=0, sort_keys=True) + "\n")
    print(f"recorded {len(rows)} ci.yml runs created {since}..{until} -> {out}")
    return 0


def state_at(sample_runs, head: str, t: float, me: int):
    """The runs-at-head listing and each run's jobs, as the API read them at t."""
    listing, jobs = [], {}
    for r in sample_runs:
        if r["head_sha"] != head or ts(r["created_at"]) > t:
            continue
        ends = [ts(j["completed_at"]) for j in r["jobs"] if j.get("completed_at")]
        done = r["id"] != me and bool(ends) and all(j.get("completed_at") for j in r["jobs"]) and max(ends) <= t
        listing.append({"id": r["id"], "display_title": r["title"], "status": "completed" if done else "in_progress"})
        jobs[r["id"]] = [{"name": j["name"], "status": "completed" if ts(j.get("completed_at")) and ts(j["completed_at"]) <= t
                          else "in_progress", "conclusion": j.get("conclusion")}
                         for j in r["jobs"] if ts(j.get("started_at")) is not None and ts(j["started_at"]) <= t]

    def get(path, params=None):
        if path.endswith("ci.yml/runs"):
            return 200, {}, {"workflow_runs": listing}
        rid = int(path.split("/runs/")[1].split("/")[0])
        return 200, {}, {"jobs": jobs.get(rid, [])}
    return get


def replay(sample: dict, pre, as_kind: str = "edit") -> dict:
    runs = sample["runs"]
    code_preludes = [minutes(j) for r in runs if (pre.parse_title(r["title"]) or ("",))[0] == "code"
                     for j in r["jobs"] if j["name"] == "prelude" and j.get("completed_at")]
    prelude_floor = statistics.median(code_preludes) if code_preludes else 0.0
    total = sum(minutes(j) for r in runs for j in r["jobs"])
    res = {"runs": 0, "deferred": 0, "before": 0.0, "after": 0.0, "prelude_before": 0.0, "prelude_after": 0.0,
           "pr_contract_before": 0.0, "all_ci_minutes": total, "prelude_floor": prelude_floor}
    for r in runs:
        t = pre.parse_title(r["title"])
        if t is None or t[0] != as_kind:
            continue
        pj = next((j for j in r["jobs"] if j["name"] == "prelude" and j.get("started_at")), None)
        if pj is None:
            continue
        res["runs"] += 1
        before = sum(minutes(j) for j in r["jobs"])
        res["before"] += before
        res["prelude_before"] += minutes(pj)
        res["pr_contract_before"] += sum(minutes(j) for j in r["jobs"] if j["name"].startswith("pr-contract"))
        defer = getattr(pre, "defer_to", None)
        ctx = {"repo": "o/r", "head": r["head_sha"], "run_id": r["id"]}
        hit = defer is not None and defer(ctx, t[1], state_at(runs, r["head_sha"], ts(pj["started_at"]), r["id"])) is not None
        if hit:
            res["deferred"] += 1
            after = sum(minutes(j) for j in r["jobs"] if j["name"] != "prelude" and not j["name"].startswith("pr-contract"))
            after += min(prelude_floor, minutes(pj))
            res["prelude_after"] += min(prelude_floor, minutes(pj))
        else:
            after = before
            res["prelude_after"] += minutes(pj)
        res["after"] += after
    return res


def show(label, r):
    share = 100 * (r["before"] - r["after"]) / r["all_ci_minutes"] if r["all_ci_minutes"] else 0.0
    print(f"{label}: {r['runs']} runs, {r['deferred']} deferred; job-minutes {r['before']:.0f} -> {r['after']:.0f} "
          f"(prelude {r['prelude_before']:.0f} -> {r['prelude_after']:.0f}, pr-contract before "
          f"{r['pr_contract_before']:.0f}); saving {r['before'] - r['after']:.0f} of {r['all_ci_minutes']:.0f} "
          f"ci.yml job-minutes ({share:.1f}%); prelude floor {r['prelude_floor']:.2f} min")


def self_test() -> int:
    pre = load_prelude(ROOT / "tools" / "ci" / "prelude.py")
    T = lambda m: f"2026-11-05T10:{m:02d}:00Z"  # noqa: E731
    title = pre.title

    def job(n, a, b, c="success"):
        return {"name": n, "status": "completed", "conclusion": c, "started_at": T(a), "completed_at": T(b)}
    code = {"id": 1, "title": title("code", "7", "main", "H"), "head_sha": "H", "event": "pull_request",
            "created_at": T(0), "status": "completed",
            "jobs": [job("prelude", 0, 1), job("tests / fast (3.14)", 1, 40), job("pr-contract / pr-contract", 41, 42),
                     job("gate", 42, 43)]}
    early = {"id": 2, "title": title("edit", "7", "main", "H"), "head_sha": "H", "event": "pull_request",
             "created_at": T(5), "status": "completed",
             "jobs": [job("prelude", 5, 43), job("arch-score / arch-score", 43, 45), job("pr-contract / pr-contract", 45, 46),
                      job("gate", 46, 47)]}
    late = {**early, "id": 3, "created_at": T(50),
            "jobs": [job("prelude", 50, 51), job("pr-contract / pr-contract", 51, 52), job("gate", 52, 53)]}
    s = {"runs": [code, early, late]}
    r = replay(s, pre)
    ok = r["deferred"] == 1 and abs(r["before"] - (38 + 2 + 1 + 1 + 1 + 1 + 1)) < 1e-9 \
        and abs(r["after"] - (1 + 2 + 1 + 3)) < 1e-9
    base = replay(s, type("NoDefer", (), {"parse_title": staticmethod(pre.parse_title)}))
    ok &= base["deferred"] == 0 and base["after"] == base["before"]
    print(f"edit_runs self-test: {'ok' if ok else 'FAIL'} {r} / control {base['deferred']} deferred")
    return 0 if ok else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sample", nargs="?")
    ap.add_argument("--fetch")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--prelude", default=str(ROOT / "tools" / "ci" / "prelude.py"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.fetch:
        return fetch(Path(a.fetch), a.since, a.until)
    sample = json.loads(Path(a.sample).read_text())
    pre = load_prelude(Path(a.prelude))
    show(f"edit runs ({a.prelude})", replay(sample, pre))
    show("null control (code runs through the same predicate)", replay(sample, pre, as_kind="code"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
