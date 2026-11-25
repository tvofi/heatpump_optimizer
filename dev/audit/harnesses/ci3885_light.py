#!/usr/bin/env python3
"""#3885: light grading's instruments -- the mutation proof, the range census, the run cost.

    python3 dev/audit/harnesses/ci3885_light.py mutants
    python3 dev/audit/harnesses/ci3885_light.py gaps [--since 2026-11-10] [--ref origin/main]
    python3 dev/audit/harnesses/ci3885_light.py cost RUN_ID [RUN_ID...]
    python3 dev/audit/harnesses/ci3885_light.py share DAY [--event workflow_dispatch]
    python3 dev/audit/harnesses/ci3885_light.py dup DAY

`mutants` reverts one production line of the fix at a time, in place, runs
`tools/ci/prelude.py --self-test` and prints the checks that fail; the file is
restored after each mutant. A site not found once is refused, never counted.
`gaps` classifies main's first-parent commits with prelude.light's own
predicate over each commit's first-parent diff and prints the longest run of
light commits and the longest time between two that are not: the delay a wrong
closure can now have before a full push reddens main. Its null control is the
predicate with PRODUCTION_FILES emptied (`--prefixes-only`).
`cost` sums runner minutes per job of a run, every attempt (`gh api`;
started_at to completed_at, skipped jobs excluded), the job table a light run's
cost is read from. `share` splits one day's runs of an event into light and full by
prelude.light over the named PR's final file list (a push: its first-parent diff), with
their runner minutes, and prices each light run's jobs against the lanes this tree's
prelude would stand down for that list. `dup` counts the day's PR-naming dispatches
that followed a pull_request run which had already graded the same head.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import subprocess
import time
import sys
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
sys.path.insert(0, str(ROOT / "tools" / "ci"))
import prelude  # noqa: E402

P = ROOT / "tools/ci/prelude.py"
WF = ROOT / ".github/workflows"
MUTANTS = [
    ("M0 fix A: a non-code run waits whatever its workset", P,
     'if not why and kind != "code" and set(out["workset"].split()) & SOURCE_READERS:',
     'if not why and kind != "code":'),
    ("M1 a cancelled (replaced) run counts as a base", P,
     ' or r.get("status") != "completed" or r.get("conclusion") == "cancelled"):',
     ' or r.get("status") != "completed"):'),
    ("M2 a run whose prelude failed counts as a base", P,
     '            if run_jobs(get, ctx["repo"], r["id"]).get("prelude") != ("completed", "success"):\n'
     '                continue\n',
     '            run_jobs(get, ctx["repo"], r["id"])\n'),
    ("M3 the root files HACS reads are not production", P,
     '\n                                   or f in PRODUCTION_FILES for f in files)',
     '\n                                   for f in files)'),
    ("M4 a .github/ change can be light", P,
     "f.startswith(PRODUCTION_PREFIXES + NEVER_LIGHT + ('\"',))", "f.startswith(PRODUCTION_PREFIXES + ('\"',))"),
    ("M5 a light push keeps the full scope", P,
     ', {**ctx, "base_sha": rng[0]}, "auto"', ', {**ctx, "base_sha": rng[0]}, out["scope"]'),
    ("M6 a light push stands down no push-only lane", P,
     '(list(LIGHT_PUSH_LANES) if push else [])', '[]'),
    ("M7 a lane stands down even when the change reaches what it reads", P,
     '        if not any(f in reads or f in node[0] or f.startswith(extra + node[1]) or Path(f).name in extra\n'
     '                   for f in changed):\n',
     '        if True:\n'),
    ("M8 a base that is no ancestor is accepted", P,
     'if not base or not (ancestor or _is_ancestor)(base, ctx["head"], cwd):', 'if not base:'),
    ("M9 a light pull request is never light", P,
     '    if scoped == "pull_request" and light(changed):\n', '    if ev == "push" and light(changed):\n'),
    ("M10 browser's job env stops reading the stand-down", WF / "tests.yml",
     " || contains(format(' {0} ', inputs.stand_down), ' browser ') }}", " }}"),
    ("M11 a typing step reads only the lane-skip", WF / "tests.yml",
     "      - name: Run the ruler and ratchet its three numbers\n        if: env.STAND_DOWN != 'true'\n",
     "      - name: Run the ruler and ratchet its three numbers\n"
     "        if: needs.closure-scope.outputs.typing_skip != 'skip'\n"),
    ("M12 env-matrix stops reading the stand-down", WF / "governance.yml",
     " || contains(format(' {0} ', inputs.stand_down), ' env-matrix ') }}", " }}"),
    ("M13 a light run analyzes the python leg", P,
     'LIGHT_SKIP_LEGS = ("python",)', 'LIGHT_SKIP_LEGS = ()'),
    ("M14 coverage stands down when the diff touches tests/", P,
     '"coverage": (None, ("tests/", ', '"coverage": (None, ('),
    ("M15 coverage-ratchet's job env stops reading the stand-down", WF / "tests.yml",
     "    # Nothing to grade when `coverage` stood down (#3885): it measured nothing.\n    env:\n"
     "      STAND_DOWN: ${{ contains(format(' {0} ', inputs.stand_down), ' coverage ') }}\n",
     "    # Nothing to grade when `coverage` stood down (#3885): it measured nothing.\n    env:\n"
     "      STAND_DOWN: false\n"),
    ("M16 (rev-3888) browser's node driver reads nothing beyond its closure", P,
     'NODE_DRIVERS = {"browser": "tests/card_browser.mjs"}', 'NODE_DRIVERS = {}'),
    ("M17 (rev-3888) node_reads follows no relative import", P,
     '            todo.append(os.path.normpath(os.path.join(os.path.dirname(rel), imp)))\n',
     '            pass\n'),
    ("M18 (rev-3888) a git-quoted path can be light", P,
     "f.startswith(PRODUCTION_PREFIXES + NEVER_LIGHT + ('\"',))", "f.startswith(PRODUCTION_PREFIXES + NEVER_LIGHT)"),
    ("M19 (rev-3888) the changed list is git's quoted default", ROOT / "tests/closure.py",
     '["git", "diff", "--no-renames", "--name-only", "-z",\n                          f"{base}{dots}{head}"]',
     '["git", "diff", "--no-renames", "--name-only",\n                          f"{base}{dots}{head}"]'),
]


def _selftest() -> tuple[int, list[str], str]:
    r = subprocess.run([sys.executable, "-I", str(P), "--self-test"], cwd=ROOT, capture_output=True, text=True)
    fails = [ln[5:].split(": got ")[0] for ln in r.stdout.splitlines() if ln.startswith("FAIL ")]
    return r.returncode, fails, (r.stdout.strip().splitlines() or [""])[-1]


def mutants() -> int:
    rc, fails, last = _selftest()
    print(f"baseline: rc={rc} {last}")
    if rc or fails:
        print("REFUSED: the baseline is not green")
        return 1
    survived = 0
    for name, path, old, new in MUTANTS:
        text = path.read_text()
        if text.count(old) != 1:
            print(f"{name}: SITE NOT FOUND ({text.count(old)} matches) -- refused, not counted")
            survived += 1
            continue
        try:
            path.write_text(text.replace(old, new))
            rc, fails, last = _selftest()
        finally:
            path.write_text(text)
        print(f"{name}: {'KILLED' if rc else 'SURVIVED'} -- {last}")
        survived += not rc
        for f in fails:
            print(f"    FAIL {f}")
    print(f"mutants: {len(MUTANTS)}, survived or refused: {survived}")
    return 1 if survived else 0


def gaps(since: str, ref: str, prefixes_only: bool) -> int:
    def git(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    if prefixes_only:
        prelude.PRODUCTION_FILES = frozenset()
    rows = [ln.split() for ln in git("log", "--first-parent", "--reverse", f"--since={since}",
                                       "--format=%H %ct", ref).splitlines()]
    light_run = longest = full = n_light = 0
    last_full = longest_gap = None
    for sha, ct in rows:
        files = git("diff", "--name-only", "--no-renames", f"{sha}^1", sha).split()
        if prelude.light(files):
            n_light += 1
            light_run += 1
            longest = max(longest, light_run)
        else:
            full += 1
            if last_full is not None:
                longest_gap = max(longest_gap or 0, int(ct) - last_full)
            last_full, light_run = int(ct), 0
    print(f"first-parent commits on {ref} since {since}: {len(rows)}; graded full: {full}; light: {n_light}")
    print(f"longest run of consecutive light commits: {longest}")
    print(f"longest time between two full-graded commits: {(longest_gap or 0) / 3600:.1f} h")
    return 0


def cost(run_ids: list[str]) -> int:
    def api(path):
        return json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)
    for rid in run_ids:
        run = api(f"repos/{{owner}}/{{repo}}/actions/runs/{rid}")
        per = collections.Counter()
        for attempt in range(1, int(run.get("run_attempt") or 1) + 1):
            page = 1
            while True:
                doc = api(f"repos/{{owner}}/{{repo}}/actions/runs/{rid}/attempts/{attempt}/jobs?per_page=100&page={page}")
                for j in doc["jobs"]:
                    if j.get("conclusion") == "skipped" or not j.get("started_at") or not j.get("completed_at"):
                        continue
                    s, e = (dt.datetime.fromisoformat(j[k].replace("Z", "+00:00")) for k in ("started_at", "completed_at"))
                    per[j["name"]] += max((e - s).total_seconds() / 60, 0)
                if len(doc["jobs"]) < 100:
                    break
                page += 1
        print(f"run {rid} ({run.get('event')}, {run.get('display_title')}): {sum(per.values()):.1f} runner-min")
        for name, m in per.most_common():
            print(f"    {m:7.2f}  {name}")
    return 0


def api(path: str) -> list:
    """Every page of one `gh api` listing; a transient refusal is retried, the eighth raised.
    A run's jobs listing of several hundred jobs answers HTTP 502 at 100 per page on some
    pages, so a retry asks for smaller pages."""
    for attempt in range(8):
        page = path if attempt < 2 else path.replace("per_page=100", "per_page=30")
        r = subprocess.run(["gh", "api", "--paginate", page], capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout.replace("}{", "},{").join(("[", "]")))
        time.sleep(5 * (attempt + 1))
    r.check_returncode()
    return []


def share(day: str, event: str) -> int:
    """Runs of ci.yml for `event` created on `day`, split by prelude.light over the file list of
    the PR the title names (its final list: a per-head list is not kept); a run naming no PR is
    full. Minutes as `cost` sums them (every attempt's latest jobs listing, filter=all). Each light
    run's jobs are then priced against what this tree's prelude would stand down for that list
    (`stand_down` over tests/closures.json, plus the python leg): the minutes a job of a lane in
    that set spent are the run's saving, per job name."""
    job_lane = {job: lane for (_wf, job), lane in prelude.LIGHT_GATE.items()}
    per, saved = collections.Counter(), collections.Counter()
    runs = [r for page in api(f"repos/{{owner}}/{{repo}}/actions/workflows/ci.yml/runs?event={event}"
                              f"&created={day}&per_page=100") for r in page["workflow_runs"]]
    cls, tot = {}, collections.Counter()
    for r in runs:
        t = prelude.parse_title(r.get("display_title") or "")
        pr = t[1] if t else ""
        if pr and pr not in cls:
            files = [f["filename"] for page in api(f"repos/{{owner}}/{{repo}}/pulls/{pr}/files?per_page=100")
                     for f in page]
            cls[pr] = files
        if r.get("event") == "push":  # a push names no PR: its own first-parent diff
            pr = r["id"]
            cls[pr] = subprocess.run(["git", "diff", "--name-only", f"{r['head_sha']}^1", r["head_sha"]],
                                     cwd=ROOT, capture_output=True, text=True).stdout.split()
        files = cls.get(pr) or []
        c = "light" if prelude.light(files) else "full"
        down = set(prelude.stand_down(files, r.get("event") == "push")) if c == "light" else set()
        down |= {"python"} & set(prelude.LIGHT_SKIP_LEGS) if c == "light" else set()
        m = 0.0
        for page in api(f"repos/{{owner}}/{{repo}}/actions/runs/{r['id']}/jobs?filter=all&per_page=100"):
            for j in page["jobs"]:
                if j.get("conclusion") != "skipped" and j.get("started_at") and j.get("completed_at"):
                    s, e = (dt.datetime.fromisoformat(j[k].replace("Z", "+00:00")) for k in ("started_at", "completed_at"))
                    m += max((e - s).total_seconds() / 60, 0)
                    jm = max((e - s).total_seconds() / 60, 0)
                    short = j["name"].split(" / ")[-1]
                    lane = "python" if short == "Analyze (python)" else job_lane.get(short)
                    if c == "light" and lane:
                        per[j["name"]] += jm
                        if lane in down:
                            saved[j["name"]] += jm
        tot[c, "runs"] += 1
        tot[c, "min"] += m
    for c in ("light", "full"):
        print(f"{event} {day} {c}: {tot[c, 'runs']} runs, {tot[c, 'min']:.0f} runner-min")
    for name, m in per.most_common():
        print(f"{event} {day} light job {name}: {m:.0f} runner-min, stood down {saved[name]:.0f}")
    print(f"{event} {day} stood down in all: {sum(saved.values()):.0f} runner-min")
    return 0


def dup(day: str) -> int:
    """ci.yml workflow_dispatch runs created on `day` that name a PR, split by whether a
    pull_request run at the same head had already COMPLETED with a conclusion other than
    cancelled, action_required or skipped (a run that graded the head) before the dispatch was
    created. Their unit sets are not compared: a duplicate here is an upper bound on what reusing
    the earlier run's verdict could save. Minutes as `cost` sums them."""
    base = "repos/{owner}/{repo}/actions"
    runs = [r for page in api(f"{base}/workflows/ci.yml/runs?event=workflow_dispatch&created={day}&per_page=100")
            for r in page["workflow_runs"] if prelude.parse_title(r.get("display_title") or "")]
    tot = collections.Counter()
    for r in runs:
        prior = [p for page in api(f"{base}/workflows/ci.yml/runs?head_sha={r['head_sha']}&event=pull_request"
                                   "&per_page=100") for p in page["workflow_runs"]
                 if p["status"] == "completed" and p["conclusion"] not in ("cancelled", "action_required", "skipped")
                 and p["created_at"] < r["created_at"]]
        m = 0.0
        for page in api(f"{base}/runs/{r['id']}/jobs?filter=all&per_page=100"):
            for j in page["jobs"]:
                if j.get("conclusion") != "skipped" and j.get("started_at") and j.get("completed_at"):
                    a, e = (dt.datetime.fromisoformat(j[k].replace("Z", "+00:00")) for k in ("started_at", "completed_at"))
                    m += max((e - a).total_seconds() / 60, 0)
        k = "duplicate" if prior else "sole"
        tot[k, "runs"] += 1
        tot[k, "min"] += m
        print(f"{r['id']} {r['head_sha'][:10]} prior_pr_runs={len(prior)} {m:.0f}min")
    print(f"dispatch {day}: duplicate (a graded pull_request run at the head first): {tot['duplicate', 'runs']} runs, "
          f"{tot['duplicate', 'min']:.0f} runner-min; sole grader: {tot['sole', 'runs']} runs, {tot['sole', 'min']:.0f}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("mutants")
    g = sub.add_parser("gaps")
    g.add_argument("--since", default="2026-11-10")
    g.add_argument("--ref", default="origin/main")
    g.add_argument("--prefixes-only", action="store_true")
    c = sub.add_parser("cost")
    c.add_argument("run_ids", nargs="+")
    sh = sub.add_parser("share")
    sh.add_argument("day")
    sh.add_argument("--event", default="workflow_dispatch")
    du = sub.add_parser("dup")
    du.add_argument("day")
    a = ap.parse_args(argv)
    if a.cmd == "dup":
        return dup(a.day)
    if a.cmd == "share":
        return share(a.day, a.event)
    if a.cmd == "mutants":
        return mutants()
    if a.cmd == "gaps":
        return gaps(a.since, a.ref, a.prefixes_only)
    return cost(a.run_ids)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
