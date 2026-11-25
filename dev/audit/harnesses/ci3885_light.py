#!/usr/bin/env python3
"""#3885: light grading's instruments -- the mutation proof, the range census, the run cost.

    python3 dev/audit/harnesses/ci3885_light.py mutants
    python3 dev/audit/harnesses/ci3885_light.py gaps [--since 2026-11-10] [--ref origin/main]
    python3 dev/audit/harnesses/ci3885_light.py cost RUN_ID [RUN_ID...]
    python3 dev/audit/harnesses/ci3885_light.py share DAY [--event workflow_dispatch]

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
prelude.light over the named PR's final file list, with their runner minutes.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
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
     ' or f in PRODUCTION_FILES\n                                   for f in files)',
     '\n                                   for f in files)'),
    ("M4 a .github/ change can be light", P,
     'f.startswith(PRODUCTION_PREFIXES + NEVER_LIGHT)', 'f.startswith(PRODUCTION_PREFIXES)'),
    ("M5 a light push keeps the full scope", P,
     ', {**ctx, "base_sha": rng[0]}, "auto"', ', {**ctx, "base_sha": rng[0]}, out["scope"]'),
    ("M6 a light push stands down no push-only lane", P,
     '(list(LIGHT_PUSH_LANES) if push else [])', '[]'),
    ("M7 a lane stands down even when the change reaches what it reads", P,
     '        if not any(f in reads or f.startswith(extra) or Path(f).name in extra for f in changed):\n',
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


def share(day: str, event: str) -> int:
    """Runs of ci.yml for `event` created on `day`, split by prelude.light over the file list of
    the PR the title names (its final list: a per-head list is not kept); a run naming no PR is
    full. Minutes as `cost` sums them (every attempt's latest jobs listing, filter=all). The light
    runs' minutes are then split per job whose name carries a lane the fix stands down."""
    lanes = ("python", "coverage", "browser", "typing", "hassfest", "validate", "closures", "env-matrix")
    per = collections.Counter()
    def api(path):
        return json.loads(subprocess.run(["gh", "api", "--paginate", path], capture_output=True, text=True,
                                         check=True).stdout.replace("}{", "},{").join(("[", "]")))
    runs = [r for page in api(f"repos/{{owner}}/{{repo}}/actions/workflows/ci.yml/runs?event={event}"
                              f"&created={day}&per_page=100") for r in page["workflow_runs"]]
    cls, tot = {}, collections.Counter()
    for r in runs:
        t = prelude.parse_title(r.get("display_title") or "")
        pr = t[1] if t else ""
        if pr and pr not in cls:
            files = [f["filename"] for page in api(f"repos/{{owner}}/{{repo}}/pulls/{pr}/files?per_page=100")
                     for f in page]
            cls[pr] = "light" if prelude.light(files) else "full"
        c = cls.get(pr, "full")
        m = 0.0
        for page in api(f"repos/{{owner}}/{{repo}}/actions/runs/{r['id']}/jobs?filter=all&per_page=100"):
            for j in page["jobs"]:
                if j.get("conclusion") != "skipped" and j.get("started_at") and j.get("completed_at"):
                    s, e = (dt.datetime.fromisoformat(j[k].replace("Z", "+00:00")) for k in ("started_at", "completed_at"))
                    m += max((e - s).total_seconds() / 60, 0)
                    hit = [x for x in lanes if x in j["name"]]
                    if c == "light" and hit:
                        per[j["name"]] += max((e - s).total_seconds() / 60, 0)
        tot[c, "runs"] += 1
        tot[c, "min"] += m
    for c in ("light", "full"):
        print(f"{event} {day} {c}: {tot[c, 'runs']} runs, {tot[c, 'min']:.0f} runner-min")
    for name, m in per.most_common():
        print(f"{event} {day} light job {name}: {m:.0f} runner-min")
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
    a = ap.parse_args(argv)
    if a.cmd == "share":
        return share(a.day, a.event)
    if a.cmd == "mutants":
        return mutants()
    if a.cmd == "gaps":
        return gaps(a.since, a.ref, a.prefixes_only)
    return cost(a.run_ids)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
