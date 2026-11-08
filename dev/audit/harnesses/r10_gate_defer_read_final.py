#!/usr/bin/env python3
"""R10-RCA-GATE-BUSY-DEFER-2, carries part: how long a deferral red stands before a gate at its head goes green.

Root-cause seat harness (dev/audit/rca/r10-gate-defer-read-final.md). #3287 (5c1fa41fb) made a
deferring gate publish its red at once ("run(s) [...] at this head are still being judged; their
gate decides") and left the re-judging to gate-sweep.yml's settle. This census scores the recorded
gate jobs of the named pull requests: one row per deferral red, the gate program that published it
(the `programs restored from <sha>` line), when its deciding run concluded, and when a gate at the
same head next concluded success.

Arms:
  census [--fixture F]   one line per deferral red, then RESULT lines. Rules:
                         - a deferral red: a `gate` job attempt that concluded failure with
                           gate.py's deferral() line; any other gate failure is counted apart
                           (non_deferral_reds) and never scored;
                         - program: `at-once` when the pinned sha carries 5c1fa41fb (#3287),
                           `waiting` when it does not, `unpinned` with no pin line;
                         - decider_done: for each run the red names, the end of its first
                           attempt ending at or after the red's gate started (an attempt ends at
                           the later of its last non-gate job and its gate job), the latest of
                           those, with that attempt's gate conclusion (cancelled: the decider
                           never decided); unknown when a named run is not recorded;
                         - green_at: the earliest `gate` attempt at the same head sha, in any run,
                           that concluded success after the red completed;
                         - red_min: green_at minus the red's completed_at, the minutes the
                           deferral red stood as a reader saw it; lag_min: green_at minus
                           decider_done (negative: a gate went green before the decider's run
                           ended, e.g. its gate job was the last job);
                         - stale_pin_*: `waiting` reds published after #3287 merged, and how
                           many were re-run attempts (a re-run replays the run's pinned base);
                         - by: who started the green attempt, known only when it is its run's
                           latest attempt (the listing carries one triggering_actor per run).
                         Exit 1 when the fixture is malformed; the census itself has no verdict.
  heads [--fixture F]    per pull request: heads recorded, heads with a deferral red, and the
                         gate failures that were not deferrals (the null control: such a red is
                         not counted as a deferral)

The fixture (default: this file's .json) was recorded through the GitHub REST API's
actions/workflows/ci.yml/runs?branch=, actions/runs/<id>/jobs?filter=all and
actions/jobs/<id>/logs (via the GitHub MCP tools, which this seat had in place of gh), for runs
created 2026-11-07T00:00Z to 2026-11-08T07:00Z; only runs with a re-run attempt or a non-success
conclusion had their jobs read (an attempt-1 success has no deferral red to score).
Needs the repository's history for the program split (git merge-base --is-ancestor).

EXPECTED RESULT (fixture as committed):
  RESULT deferral_reds=see the RCA document's Figures; this header carries the rule, not the count
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

FIXTURE = Path(__file__).with_suffix(".json")
AT_ONCE_FIX = "5c1fa41fb9773048a79d86f741e30dec60fa5253"    # #3287's merge: the deferral publishes at once
AT_ONCE_MERGED = "2026-11-07T19:14:31Z"                       # its committer stamp, 20:14:31 +0100
_ANCESTRY: dict = {}


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def program(pin):
    if not pin:
        return "unpinned"
    if pin not in _ANCESTRY:
        r = subprocess.run(["git", "merge-base", "--is-ancestor", AT_ONCE_FIX, pin], capture_output=True)
        if r.returncode not in (0, 1):
            raise SystemExit(f"program split: git cannot place {pin} (fetch the history)")
        _ANCESTRY[pin] = "at-once" if r.returncode == 0 else "waiting"
    return _ANCESTRY[pin]


def load(path):
    doc = json.loads(Path(path).read_text())
    prs = doc["prs"] if isinstance(doc, dict) and "prs" in doc else doc
    for p in prs:
        for r in p["runs"]:
            for k in ("id", "head_sha", "updated_at", "run_attempt", "gate"):
                if k not in r:
                    raise SystemExit(f"fixture: pr {p.get('pr')} run {r.get('id')} lacks {k}")
    return prs


def attempt_end(run, after):
    """(end, gate conclusion) of the first attempt of <run> that ended at or after <after>: an
    attempt ends at the later of its last non-gate job and its gate job; an attempt-1 success whose
    jobs were not read ends at the run's updated_at."""
    ends = []
    for a, t in (run.get("work_done_at") or {}).items():
        gs = [g for g in run["gate"] if str(g["run_attempt"]) == str(a)]
        stamps = [ts(t)] + [ts(g["completed_at"]) for g in gs if g.get("completed_at")]
        stamps = [s for s in stamps if s]
        if stamps:
            ends.append((max(stamps), gs[-1]["conclusion"] if gs else None))
    if not ends:
        ends = [(ts(run["updated_at"]), run.get("conclusion"))]
    later = sorted(e for e in ends if e[0] >= after)
    return later[0] if later else max(ends)


def rows(prs):
    out, nondefer = [], 0
    for p in prs:
        runs = {r["id"]: r for r in p["runs"]}
        greens = [(ts(g["completed_at"]), r, g) for r in p["runs"] for g in r["gate"]
                  if g["conclusion"] == "success" and g.get("completed_at")]
        for r in p["runs"]:
            for g in r["gate"]:
                if g["conclusion"] != "failure":
                    continue
                if not g.get("defer_to"):
                    nondefer += 1
                    continue
                done = ts(g["completed_at"])
                named = [runs.get(i) for i in g["defer_to"]]
                ends = [attempt_end(n, ts(g["started_at"])) for n in named if n]
                decider = max(e for e, _ in ends) if len(ends) == len(named) else None
                verdict = ",".join(c or "?" for _, c in ends) if decider else None
                if done is None:
                    continue    # recorded in progress: no red yet
                later = sorted(((t, rr, gg) for t, rr, gg in greens
                                if rr["head_sha"] == r["head_sha"] and t > done), key=lambda e: e[0])
                green = later[0] if later else None
                by = None
                if green and green[2]["run_attempt"] == green[1]["run_attempt"]:
                    by = green[1].get("triggering_actor")
                out.append({
                    "pr": p["pr"], "run": r["id"], "attempt": g["run_attempt"], "head": r["head_sha"][:8],
                    "program": program(g.get("pinned")), "red_at": g["completed_at"],
                    "decider_done": decider, "decider_verdict": verdict, "green": green,
                    "red_min": (green[0] - done).total_seconds() / 60 if green else None,
                    "lag_min": (green[0] - decider).total_seconds() / 60 if green and decider else None,
                    "by": by or ("?" if green else None),
                    "same_run": bool(green and green[1]["id"] == r["id"]),
                })
    return out, nondefer


def fmt(x):
    return "-" if x is None else f"{x:.1f}"


def census(prs):
    rs, nondefer = rows(prs)
    for x in sorted(rs, key=lambda x: x["red_at"]):
        g = x["green"]
        print(f"#{x['pr']} {x['head']} run {x['run']}#{x['attempt']} {x['program']:8} red {x['red_at']} "
              f"decider {x['decider_done'].isoformat()[:19] + ' ' + x['decider_verdict'] if x['decider_done'] else 'unknown'} "
              f"green {g[0].isoformat()[:19] + ' run ' + str(g[1]['id']) + '#' + str(g[2]['run_attempt']) if g else 'NONE'} "
              f"red_min {fmt(x['red_min'])} lag_min {fmt(x['lag_min'])} by {x['by']}")
    heads = {(x["pr"], x["head"]) for x in rs}
    print(f"RESULT deferral_reds={len(rs)}")
    print(f"RESULT heads_with_deferral={len(heads)}")
    print(f"RESULT prs_with_deferral={len({x['pr'] for x in rs})}")
    print(f"RESULT non_deferral_reds={nondefer}")
    resid = [x for x in rs if x["green"] is None]
    print(f"RESULT residual_red={len(resid)}")
    # a residual red is honest when its decider did not succeed (the head is red or superseded
    # anyway); one whose every named run's attempt succeeded is a red nothing re-judged
    print(f"RESULT residual_red_decider_success="
          f"{sum(1 for x in resid if x['decider_verdict'] and set(x['decider_verdict'].split(',')) == {'success'})}")
    print(f"RESULT residual_red_decider_unknown={sum(1 for x in resid if not x['decider_verdict'])}")
    stale = [x for x in rs if x["program"] == "waiting" and ts(x["red_at"]) > ts(AT_ONCE_MERGED)]
    # a red published after #3287 merged by a program without it: a re-run of a run pinned before
    # the merge (r10-gate-busy-defer-2.md section 5.2), or a pull request whose base predates it
    print(f"RESULT stale_pin_reds_after_fix={len(stale)}")
    print(f"RESULT stale_pin_reruns_after_fix={sum(1 for x in stale if x['attempt'] > 1)}")
    for prog in ("waiting", "at-once", "unpinned"):
        sub = [x for x in rs if x["program"] == prog]
        reds = [x["red_min"] for x in sub if x["red_min"] is not None]
        lags = [x["lag_min"] for x in sub if x["lag_min"] is not None]
        print(f"RESULT {prog.replace('-', '_')}_reds={len(sub)}")
        if reds:
            print(f"RESULT {prog.replace('-', '_')}_red_min_median={statistics.median(reds):.1f}")
            print(f"RESULT {prog.replace('-', '_')}_red_min_max={max(reds):.1f}")
        if lags:
            print(f"RESULT {prog.replace('-', '_')}_lag_min_median={statistics.median(lags):.1f}")
            print(f"RESULT {prog.replace('-', '_')}_lag_min_max={max(lags):.1f}")
        humans = sum(1 for x in sub if x["by"] not in (None, "?", "github-actions[bot]"))
        print(f"RESULT {prog.replace('-', '_')}_green_by_human={humans}")
    return 0


def heads(prs):
    for p in prs:
        hs = {r["head_sha"] for r in p["runs"]}
        dh = {r["head_sha"] for r in p["runs"] for g in r["gate"] if g["conclusion"] == "failure" and g.get("defer_to")}
        nd = sum(1 for r in p["runs"] for g in r["gate"] if g["conclusion"] == "failure" and not g.get("defer_to"))
        print(f"#{p['pr']} heads={len(hs)} heads_with_deferral={len(dh)} non_deferral_reds={nd}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arm", choices=("census", "heads"))
    ap.add_argument("--fixture", default=str(FIXTURE))
    a = ap.parse_args(argv)
    prs = load(a.fixture)
    return census(prs) if a.arm == "census" else heads(prs)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
