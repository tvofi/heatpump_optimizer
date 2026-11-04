#!/usr/bin/env python3
"""R10-HOTFIX-CI-CRITPATH-4: why main went red at 8e90d8144, and the probed
grade replayed on the same real runs.

    python3 dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py

Reads only the tree and the files beside it. No network.
  runs.json          the 60 completed ci.yml push runs on main
                     41331759691..41818271680 (2026-11-01T17:29Z..
                     2026-11-04T11:03Z), each with its jobs, cut to the fields
                     tests/ci_ratchet.py reads (`--gather-runs --window 60`).
  fast_scripts.json  per run, the seconds of every script `tests / fast
                     (3.14)` ran: its job log's tests/run.sh `ok ... (Ns)`
                     lines, a 40-hex SHA in a command replaced by `SHA`.
  bridge.json        the probe and the same scripts timed on one machine:
                     what PROBE_REFERENCE_S is derived from (section 5).

  1. diagnose  the shipped grade (fastest draw) over the newest windows, and
               the run whose ageing out moved it.
  2. host      fast (3.14)'s host factor per run: the median over its scripts
               of >= 20 s of seconds / that script's median over the 60 runs.
               Its wall against its wall over that factor.
  3. probed    each run's fast (3.14) job given the probe step it did not yet
               carry -- PROBE_REFERENCE_S["3.14"] * factor / UNIT seconds,
               rounded to 1 s as the API's timestamps are -- and graded by
               tests/ci_ratchet.py's own window_work_minutes over every
               16-run window. The other lanes carry no history of their
               host's speed and stay priced on their fastest draw here.
  4. controls  over the newest window: every run's fast (3.14) host 1.9x
               slower (wall and probe) must not move the probed grade past
               the probe's 1 s rounding; one hung run at 3.2x wall must not;
               300 s more work in the newest k runs must move it by most of
               it at k = 9 and all of it from k = 12 (the null control of
               the first two), beside the grade at main.
  5. bridge    PROBE_REFERENCE_S from bridge.json, and its spread.

UNIT is the reference host's factor: the median factor of the fleet's fast
class (factors under FAST_CLASS_BELOW, a gap separating 0.61 from 0.74), the
host the shipped grade priced each heavy lane on, so the recorded budget
keeps its unit.

EXPECTED RESULT holds=1
"""
from __future__ import annotations

import copy
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "custom_components/heatpump_optimizer/manifest.json").is_file():
            return p
    raise RuntimeError("no repository root above " + str(start))


ROOT = repo_root(HERE)
sys.path.insert(0, str(ROOT))
from tests import ci_ratchet as cr  # noqa: E402

LANE = "tests / fast (3.14)"
MIN_SCRIPT_S = 20
FAST_CLASS_BELOW = 0.65
W = cr.PUSH_WINDOW


def load():
    runs = sorted(json.loads((HERE / "runs.json").read_text())["workflow_runs"],
                  key=lambda r: r["created_at"], reverse=True)
    scripts = json.loads((HERE / "fast_scripts.json").read_text())
    return runs, scripts


def lane_job(r):
    return next((j for j in r["jobs"] if j["name"] == LANE and j.get("conclusion") == "success"), None)


def wall_s(j):
    return (cr._at(j["completed_at"]) - cr._at(j["started_at"])).total_seconds()


def host_factors(runs, scripts):
    per = {str(r["id"]): scripts[str(r["id"])] for r in runs if str(r["id"]) in scripts}
    keys = {k for s in per.values() for k in s}
    ref = {k: statistics.median([s[k] for s in per.values() if k in s]) for k in keys}
    heavy = sorted(k for k in keys if ref[k] >= MIN_SCRIPT_S)
    return {rid: statistics.median([s[k] / ref[k] for k in heavy if s.get(k)])
            for rid, s in per.items()}, heavy, ref


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


STAMPS = ("created_at", "started_at", "completed_at")


def with_probe(r, probe_s, *, job=LANE):
    """r with `job` given the probe step it did not carry, of probe_s
    seconds (rounded to 1 s, as the API's timestamps are)."""
    r = copy.deepcopy(r)
    for j in r["jobs"]:
        if j["name"] == job and j.get("conclusion") == "success" and probe_s is not None:
            s = cr._at(j["started_at"]).timestamp()
            j["steps"] = [{"name": f"{cr.PROBE_STEP} (python 3.14)", "conclusion": "success",
                           "started_at": iso(s), "completed_at": iso(s + round(probe_s))}]
    return r


def scaled(r, k):
    """Every job of r on a host k times slower: each timestamp's distance
    from the run's creation times k, queues included, probe steps too."""
    r = copy.deepcopy(r)
    t0 = cr._at(r["created_at"]).timestamp()
    for j in r["jobs"] + [s for j in r["jobs"] for s in j.get("steps") or []]:
        for f in STAMPS:
            if j.get(f):
                j[f] = iso(t0 + k * (cr._at(j[f]).timestamp() - t0))
    return r


def grown(r, delta, *, job=LANE):
    """r with `job` doing delta more seconds of work: it ends delta later,
    and so does everything created once it had ended (what waited on it);
    a job already running keeps its times."""
    r = copy.deepcopy(r)
    lane = next((j for j in r["jobs"] if j["name"] == job and j.get("completed_at")), None)
    if lane is None:
        return r
    end = cr._at(lane["completed_at"]).timestamp()
    for j in r["jobs"]:
        if j is lane:
            j["completed_at"] = iso(end + delta)
        elif j.get("created_at") and cr._at(j["created_at"]).timestamp() >= end - cr.QUEUE_EPS:
            for f in STAMPS:
                if j.get(f):
                    j[f] = iso(cr._at(j[f]).timestamp() + delta)
    return r


def shipped_at_main(runs):
    """The statistic at main 8e90d8144, the comparison arm: every job at its
    fastest success run above a third of its median, summed along each
    run's own critical chain, the longest kept."""
    chains, work = [], {}
    for r in runs:
        w = cr._walk(r)
        if w is None:
            continue
        chains.append(cr.run_chain(r))
        for j in w:
            if j["priced"]:
                work.setdefault(j["name"], []).append(j["work"])
    price = {n: min(x for x in s if x >= statistics.median(s) / 3) for n, s in work.items()}
    return round(max(sum(price.get(n, 0.0) for n in ch) for ch in chains) / 60, 3)


def main() -> int:
    runs, scripts = load()
    holds = True
    new = cr.window_work_minutes
    print(f"1. diagnose: the grade at main (fastest draw) over the newest windows of {W}")
    for i in range(6):
        span = runs[i:i + W]
        print(f"   window from {runs[i]['id']} ({runs[i]['head_sha'][:9]}): {shipped_at_main(span)}"
              f"; {LANE} fastest draw {min(wall_s(j) for j in map(lane_job, span) if j):.0f} s")
    out = runs[W]
    print(f"   the run ageing out between the two newest windows: {out['id']} ({out['head_sha'][:9]}),"
          f" {LANE} {wall_s(lane_job(out)):.0f} s")

    factor, heavy, ref = host_factors(runs, scripts)
    unit = statistics.median([f for f in factor.values() if f < FAST_CLASS_BELOW])
    walls = [wall_s(lane_job(r)) for r in runs if lane_job(r) and str(r["id"]) in factor]
    norm = [wall_s(lane_job(r)) / factor[str(r["id"])] for r in runs
            if lane_job(r) and str(r["id"]) in factor]

    def spread(xs):
        m = statistics.median(xs)
        return f"median {m:.0f} s, {min(xs):.0f}..{max(xs):.0f}, sd {statistics.pstdev(xs) / m * 100:.1f} %"
    fast_class = sum(f < FAST_CLASS_BELOW for f in factor.values())
    newest = sum(factor[str(r["id"])] < FAST_CLASS_BELOW for r in runs[:26] if str(r["id"]) in factor)
    print(f"2. host: {len(factor)} runs, {len(heavy)} scripts of >= {MIN_SCRIPT_S} s; "
          f"fast class (factor < {FAST_CLASS_BELOW}) in {fast_class} runs, {newest} of the newest 26; UNIT {unit:.3f}")
    print(f"   wall          {spread(walls)}")
    print(f"   wall / factor {spread(norm)}")
    holds &= statistics.pstdev(norm) / statistics.median(norm) < 0.05

    pref = cr.PROBE_REFERENCE_S["3.14"]

    def probe_of(r):
        f = factor.get(str(r["id"]))
        return None if f is None else pref * f / unit
    allp = [with_probe(r, probe_of(r)) for r in runs]
    wins = [(runs[i]["id"], shipped_at_main(runs[i:i + W]), new(runs[i:i + W]), new(allp[i:i + W]))
            for i in range(len(runs) - W + 1)]
    budget = json.loads((ROOT / "tests/ci_budgets.json").read_text())
    print(f"3. probed: {len(wins)} windows; at main {min(w[1] for w in wins)}..{max(w[1] for w in wins)}, "
          f"this tree unprobed {min(w[2] for w in wins)}..{max(w[2] for w in wins)}, "
          f"fast (3.14) probed {min(w[3] for w in wins)}..{max(w[3] for w in wins)}; budget "
          f"{budget['critical_path_minutes']} + band {budget['critical_path_minutes_band']}")
    for rid, s, u, pr in wins[:4]:
        print(f"   window from {rid}: at main {s}, this tree unprobed {u}, probed {pr}")
    holds &= wins[0][3] <= budget["critical_path_minutes"] + budget["critical_path_minutes_band"]

    # The controls give EVERY job a probe -- fast (3.14) its own runner's;
    # each other job, which has no history of its host's speed, a stand-in
    # reading all of its spread in the window as host (its wall over its
    # fastest), so it prices at a constant and fast (3.14), the one lane
    # probed from real data, carries the critical path. The stand-ins come
    # from the unperturbed run, so a perturbation is never absorbed by them.
    span = runs[:W]
    fastest_of = {}
    for r in span:
        for j in r["jobs"]:
            if j.get("conclusion") == "success" and j.get("started_at") and j.get("completed_at"):
                fastest_of[j["name"]] = min(fastest_of.get(j["name"], 1e9), max(1.0, wall_s(j)))
    standin = {(r["id"], j["name"]): pref / unit * max(1.0, wall_s(j)) / fastest_of[j["name"]]
               for r in span for j in r["jobs"] if j["name"] in fastest_of and j["name"] != LANE
               and j.get("conclusion") == "success"}

    def probe_all(r, k=1.0):
        out = with_probe(r, None if probe_of(r) is None else probe_of(r) * k)
        for (rid, name), s in standin.items():
            if rid == r["id"]:
                out = with_probe(out, s * k, job=name)
        return out
    base = new([probe_all(r) for r in span])
    slow = new([scaled(probe_all(r, 1.9), 1.0) for r in [scaled(r, 1.9) for r in span]])
    fastest = min(wall_s(lane_job(r)) for r in span if lane_job(r))
    hung = new([probe_all(grown(span[0], 3.2 * fastest - wall_s(lane_job(span[0]))))]
               + [probe_all(r) for r in span[1:]])
    # A probe step's timestamps are whole seconds: the slow fleet's probes,
    # each rounded once, carry up to 1 s / the probe's seconds of error.
    tol = base / min(pref / unit, min(probe_of(r) for r in span if probe_of(r)))
    holds &= abs(slow - base) <= tol and abs(hung - base) < 0.02
    print(f"4. controls over the newest window, every job probed (grade {base}):")
    print(f"   slow fleet, every job 1.9x, probes too: {slow - base:+.3f} (1 s rounding bound {tol:.3f})")
    print(f"   one hung run, {LANE} at 3.2x the fastest: {hung - base:+.3f}")
    line = []
    want = 300 * unit / max(factor[str(r["id"])] for r in span) / 60
    for k in (1, 4, 8, 9, 12, 16):
        g = new([probe_all(grown(r, 300)) for r in span[:k]] + [probe_all(r) for r in span[k:]])
        o = shipped_at_main([grown(r, 300) for r in span[:k]] + span[k:])
        line.append(f"k={k} {g - base:+.2f}/{o - shipped_at_main(span):+.2f}")
        # The median's lag on real spread (sd ~3 %): most of it once growth
        # is in 9 of 16 runs, all of it by 12; at main nothing before 16.
        if k == 9:
            holds &= g - base > 0.5 * want
        if k >= 12:
            holds &= g - base > 0.8 * want
    print(f"   +300 s on {LANE} in the newest k runs (probed / at main; all of it "
          f"probed is >= {want:.2f}): " + "  ".join(line))

    b = json.loads((HERE / "bridge.json").read_text())
    rat = {k: b["scripts_s"][k] / ref[k] for k in heavy if k in b["scripts_s"]}
    f_local = statistics.median(rat.values())
    r14 = b["probe_s"]["3.14"] / f_local * unit
    r13 = r14 * b["probe_s"]["3.13"] / b["probe_s"]["3.14"]
    print(f"5. bridge: {len(rat)} scripts, local factor {f_local:.3f} "
          f"(per script {min(rat.values()):.2f}..{max(rat.values()):.2f}); probe "
          f"3.14 {b['probe_s']['3.14']:.2f} s, 3.13 {b['probe_s']['3.13']:.2f} s locally")
    print(f"   PROBE_REFERENCE_S derived 3.14 {r14:.1f}, 3.13 {r13:.1f}; in the tree {cr.PROBE_REFERENCE_S}")
    holds &= (abs(r14 - cr.PROBE_REFERENCE_S["3.14"]) < 0.05
              and abs(r13 - cr.PROBE_REFERENCE_S["3.13"]) < 0.05)
    print(f"RESULT holds={int(holds)}")
    return 0 if holds else 1


if __name__ == "__main__":
    sys.exit(main())
