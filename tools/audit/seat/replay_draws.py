#!/usr/bin/env python3
"""Harvest the replay lane's cost draws from CI job logs into a TSV.

One row per (job, fixture, arm) of every ``tests / replay`` job of ci.yml and
``slow`` job of nightly.yml that printed a ``cost`` line: the input
``tests/replay_draws.tsv`` holds and ``tests/replay.py``'s
``cycle_cost:draws`` controls read (R10-REPLAY-COST-BUDGET round 3). It is
the instrument the round-2 review found missing: a body figure over CI's
draws is re-derived by running it, not by reading a body.

    replay_draws.py fetch --cache DIR [--ci-runs N] [--nightly-runs N]
    replay_draws.py parse --cache DIR --out FILE.tsv
    replay_draws.py window --cache DIR --runs N --until 2026-11-05T23:59:59Z
    replay_draws.py grade --job ID [--ruler MS] [--clean-from ARM]
    replay_draws.py shift [--table FILE.tsv] [--no-cuts]
    replay_draws.py interleave --pre DIR --post DIR [--pairs N]

``fetch`` lists the runs (newest first), each run's jobs on every page and
every attempt, and downloads each concluded job's log once into ``DIR``,
retrying a page the API answers 5xx; a page that still fails is printed by
name, never skipped silently. ``window`` grades, at this tree, the synthetic
clean draw of every replay job of the ``N`` most recent ci.yml runs created
up to ``--until``, one per line, and exits 1 iff one offends or is missing
from the committed draw set. ``grade``
grades one job of ``tests/replay_cost_draws.tsv`` exactly as the lane does
(``replay.job_cost``) and exits 1 iff a clean run offends or a doubled arm is
not over budget: ``--ruler`` moves the job's ruler (a draw moved across a
border), ``--clean-from cpu`` grades the doubled arm as if it were clean.
``shift`` runs ``replay.level_shift_offenders`` over a draw table (default the
committed one; ``--table`` reads another, e.g. one ``git show <sha>:`` wrote),
prints the classes examined and every class resting wholly on draws before a
shift, and exits 1 iff it names one; ``--no-cuts`` drops ``COST_CUTS``.
``interleave`` measures a declared cut's factor on this box: the synthetic
fixture's clean replay (``replay.py --one``) in two checkouts, a commit's parent
(``--pre``) and the commit (``--post``), ``N`` pairs in alternating order,
printing each run's ``cpu_ratio`` and ruler and the ratio of the medians.
Needs an authenticated ``gh``.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
WORKFLOWS = {"ci": "ci.yml", "nightly": "nightly.yml"}
JOB_NAMES = re.compile(r"^(tests / replay|slow)$")
COST = re.compile(r"cycles over \d+ entities in [\d.]+ s; cost (\{.*\})")
ARM = re.compile(r"\s(cpu|memory|loop) doubled: cost (\{.*\})")
FIXTURE = re.compile(r"-- replay (\S+\.json)")
COLUMNS = ("job", "run", "event", "created", "jobname", "fixture", "arm",
           "ref_ms", "loop_ref_ms", "cpu_ratio", "peak_kib", "loop_cpu_ratio")


def gh(path: str, tries: int = 5) -> str | None:
    for t in range(tries):
        p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout
        time.sleep(2 * (t + 1))
    print(f"FAILED after {tries} tries: {path}: {p.stderr.strip()[:200]}", file=sys.stderr)
    return None


def fetch(cache: Path, counts: dict[str, int]) -> int:
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "logs").mkdir(exist_ok=True)
    failed = 0
    runs = []
    for key, n in counts.items():
        for page in range(1, (n + 99) // 100 + 1):
            body = gh(f"repos/{REPO}/actions/workflows/{WORKFLOWS[key]}/runs"
                      f"?per_page=100&page={page}")
            if body is None:
                failed += 1
                continue
            runs += [{"id": r["id"], "event": r["event"], "created": r["created_at"],
                      "workflow": key} for r in json.loads(body)["workflow_runs"]]
    (cache / "runs.json").write_text(json.dumps(runs))
    jobs_file = cache / "jobs.json"
    jobs = json.loads(jobs_file.read_text()) if jobs_file.exists() else {}
    for run in runs:
        rid = str(run["id"])
        if rid in jobs:
            continue
        found, page, ok = [], 1, True
        while True:
            body = gh(f"repos/{REPO}/actions/runs/{rid}/jobs?per_page=50&filter=all&page={page}")
            if body is None:
                ok = False
                break
            data = json.loads(body)
            found += [{"job": j["id"], "name": j["name"], "conclusion": j["conclusion"]}
                      for j in data["jobs"] if JOB_NAMES.match(j["name"])]
            if page * 50 >= data["total_count"]:
                break
            page += 1
        if not ok:
            failed += 1
            continue
        jobs[rid] = found
        jobs_file.write_text(json.dumps(jobs))
    for rid, found in jobs.items():
        for j in found:
            log = cache / "logs" / f"{j['job']}.log"
            if j["conclusion"] in ("success", "failure") and not log.exists():
                body = gh(f"repos/{REPO}/actions/jobs/{j['job']}/logs")
                if body is None:
                    failed += 1
                    continue
                log.write_text(body)
    print(f"runs {len(runs)}, runs with jobs listed {len(jobs)}, failed requests {failed}")
    return 1 if failed else 0


def parse_log(text: str) -> list[dict]:
    rows, fixture = [], None
    for line in text.splitlines():
        if m := FIXTURE.search(line):
            fixture = m.group(1)
            continue
        if m := COST.search(line):
            arm, blob = "clean", m.group(1)
        elif m := ARM.search(line):
            arm, blob = m.group(1), m.group(2)
        else:
            continue
        try:
            cost = ast.literal_eval(blob)
        except (ValueError, SyntaxError):
            continue
        rows.append({"fixture": fixture, "arm": arm,
                     **{k: cost.get(k) for k in COLUMNS[7:]}})
    return rows


def rows(cache: Path) -> list[dict]:
    runs = {str(r["id"]): r for r in json.loads((cache / "runs.json").read_text())}
    out = []
    for rid, found in json.loads((cache / "jobs.json").read_text()).items():
        for j in found:
            log = cache / "logs" / f"{j['job']}.log"
            if rid not in runs or not log.exists():
                continue
            for r in parse_log(log.read_text(errors="replace")):
                out.append({"job": j["job"], "run": rid, "event": runs[rid]["event"],
                            "created": runs[rid]["created"], "jobname": j["name"], **r})
    # A job's runs are one draw however often its log was fetched; order is
    # the ruler's, so the fixture diffs as a table, not as a fetch order.
    uniq = {(r["job"], r["fixture"], r["arm"]): r for r in out}
    return sorted(uniq.values(), key=lambda r: (r["created"], r["job"], r["fixture"] or "",
                                                r["arm"]))


def grade(job: str, ruler: float | None, clean_from: str | None) -> int:
    root = Path(__file__).resolve().parents[3]
    sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
    import replay
    draws = {k: v for k, v in replay.cost_draws().items() if k[0] == job}
    if not draws:
        print(f"job {job}: not in {replay.COST_DRAWS.name}")
        return 2
    rulers = replay.draw_rulers(draws)[job]
    rulers = (ruler, rulers[1]) if ruler is not None else rulers
    keys = {"cpu": "cpu_ratio", "memory": "peak_kib", "loop": "loop_cpu_ratio"}
    bad = 0
    for (_, fixture), runs in sorted(draws.items()):
        if clean_from and clean_from not in runs:
            continue
        clean = runs[clean_from] if clean_from else runs["clean"]
        arms = {k: v for k, v in runs.items() if k != "clean"}
        got = replay.job_cost(fixture, clean, arms, rulers)
        print(f"{fixture}: " + "; ".join(got["lines"]))
        print(f"  clean{' (the ' + clean_from + ' arm)' if clean_from else ''}: "
              f"{got['clean'] or 'passes'}")
        bad += bool(got["clean"])
        for k, offenders in got["arms"].items():
            seen = any(o.startswith(f"{keys[k]} ") and "over its budget" in o for o in offenders)
            print(f"  {k} doubled: {'refused' if seen else 'NOT REFUSED'}: {offenders[:1]}")
            bad += not seen
    return 1 if bad else 0


def shift(table: Path | None, cuts: bool) -> int:
    root = Path(__file__).resolve().parents[3]
    sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
    import replay
    path = table or replay.COST_DRAWS
    out = 0
    for name in replay.COST_CLASS_BUDGETS:
        examined, offenders = replay.level_shift_offenders(
            replay.cost_draws(path, cuts=()), replay.cost_draw_created(path), name,
            cuts=replay.COST_CUTS if cuts else ())
        print(f"{name}: classes examined {len(examined)} {examined}")
        for o in offenders:
            print(f"  {o}")
        out |= bool(offenders)
    return out


def interleave(pre: Path, post: Path, pairs: int) -> int:
    import os
    import statistics
    got: dict[str, list[float]] = {"pre": [], "post": []}
    for i in range(pairs):
        for arm in (("pre", "post") if i % 2 == 0 else ("post", "pre")):
            tree = pre if arm == "pre" else post
            run = subprocess.run(
                [sys.executable, "tests/replay.py", "--one", "tests/replay/synthetic-dhw-only.json"],
                cwd=tree, capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": "tests/hastub"})
            line = next((ln for ln in run.stdout.splitlines()
                         if ln.startswith("<<<replay-json>>>")), None)
            if line is None:
                print(f"pair {i + 1} {arm}: no replay-json line (exit {run.returncode})")
                return 2
            cost = json.loads(line[len("<<<replay-json>>>"):])["cost"]
            got[arm].append(cost["cpu_ratio"])
            print(f"pair {i + 1} {arm} cpu_ratio {cost['cpu_ratio']} ref_ms {cost['ref_ms']:.2f}",
                  flush=True)
    a, b = statistics.median(got["pre"]), statistics.median(got["post"])
    print(f"medians pre {a} post {b}; post/pre {b / a:.4f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--cache", type=Path, required=True)
    f.add_argument("--ci-runs", type=int, default=1200)
    f.add_argument("--nightly-runs", type=int, default=200)
    p = sub.add_parser("parse")
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    w = sub.add_parser("window")
    w.add_argument("--cache", type=Path, required=True)
    w.add_argument("--runs", type=int, required=True)
    w.add_argument("--until", required=True)
    g = sub.add_parser("grade")
    g.add_argument("--job", required=True)
    g.add_argument("--ruler", type=float)
    g.add_argument("--clean-from", choices=("cpu", "memory", "loop"))
    h = sub.add_parser("shift")
    h.add_argument("--table", type=Path)
    h.add_argument("--no-cuts", action="store_true")
    i = sub.add_parser("interleave")
    i.add_argument("--pre", type=Path, required=True)
    i.add_argument("--post", type=Path, required=True)
    i.add_argument("--pairs", type=int, default=12)
    args = ap.parse_args(argv)
    if args.cmd == "interleave":
        return interleave(args.pre, args.post, args.pairs)
    if args.cmd == "shift":
        return shift(args.table, not args.no_cuts)
    if args.cmd == "grade":
        return grade(args.job, args.ruler, args.clean_from)
    if args.cmd == "fetch":
        return fetch(args.cache, {"ci": args.ci_runs, "nightly": args.nightly_runs})
    if args.cmd == "parse":
        got = rows(args.cache)
        with args.out.open("w") as fh:
            fh.write("\t".join(COLUMNS) + "\n")
            for r in got:
                fh.write("\t".join(str(r[c]) for c in COLUMNS) + "\n")
        print(f"{len(got)} rows from {len({r['job'] for r in got})} jobs -> {args.out}")
        return 0
    runs = sorted((r for r in json.loads((args.cache / "runs.json").read_text())
                   if r["workflow"] == "ci" and r["created"] <= args.until),
                  key=lambda r: r["created"], reverse=True)[:args.runs]
    ids = {str(r["id"]) for r in runs}
    print(f"window: {len(runs)} ci.yml runs {runs[-1]['created']} .. {runs[0]['created']}")
    jobs = sorted({r["job"] for r in rows(args.cache) if r["run"] in ids
                   and r["arm"] == "clean" and r["fixture"] == "synthetic-dhw-only.json"})
    return window_grade(jobs)


def window_grade(jobs: list) -> int:
    """Grade each window job's ``tests / replay`` draw as the lane does at this
    tree, one line per job, then the per-class and offender counts."""
    root = Path(__file__).resolve().parents[3]
    sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
    import replay
    draws = replay.cost_draws()
    missing = [j for j in jobs if (str(j), "synthetic-dhw-only.json") not in draws]
    rulers = replay.draw_rulers(draws)
    classes: dict[str, int] = {}
    bad = 0
    for j in map(str, jobs):
        if j in missing:
            continue
        got = replay.job_cost("synthetic-dhw-only.json",
                              draws[(j, "synthetic-dhw-only.json")]["clean"], {}, rulers[j])
        classes[str(got["class"])] = classes.get(str(got["class"]), 0) + 1
        bad += bool(got["clean"])
        print(f"{j}\truler {got['ruler']:.4g}\tclass {got['class']}\t"
              f"{'; '.join(got['clean']) or 'passes'}")
    print(f"window jobs {len(jobs)}, not in {replay.COST_DRAWS.name}: {missing}; "
          f"by class {classes}; clean offending {bad}")
    return 1 if bad or missing else 0


if __name__ == "__main__":
    sys.exit(main())
