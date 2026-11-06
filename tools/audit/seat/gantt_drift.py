#!/usr/bin/env python3
"""Compare the plan's gantt against the real state; print one GANTT-SLIP line per slip.

    python3 -I tools/audit/seat/gantt_drift.py --plan plan.json --baseline base.json \
        --acks acks.json --roster roster.json --prs prs.json --refs refs.txt \
        --fired fired.txt --now 2026-11-01T18:00:00Z [--out new-baseline.json]
    python3 -I tools/audit/seat/gantt_drift.py --self-test

Every input is a command-line argument; no host path is read.

SLIPS (stdout, `GANTT-SLIP <KIND> <subject> ...`, critical-path IDLE first):
  IDLE     a not-done group the plan starts by now+grace that no open PR head,
           handoff ref or FIRED ledger line names (tagged CP on the critical path)
  LATE     a group whose planned finish moved past the baseline's by > --late-hours
  CLOSURE  the plan's closure moved past the baseline's by > --closure-hours

INPUTS. plan.json is replan.py's output (groups{g:{start,finish,done}},
summary.closure, critical_path). baseline.json is {"closure": iso, "finish":
{group: iso}}; absent LATE/CLOSURE entries are not graded. acks.json is a list
of {"key": "IDLE:<g>"|"LATE:<g>"|"CLOSURE", "kind": "act"|"defer"|"accept",
"until": iso}. act and defer silence the key while now < until (no until: for
good). accept silences the key and re-baselines it into --out (printed as
GANTT-BASELINE). roster.json supplies each group's resume.branch; prs.json is a
list with headRefName; refs.txt is a saved `git ls-remote` listing; fired.txt is
the dispatch ledger, of which only FIRED lines count.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import json
import re
import sys

FMT = "%Y-%m-%dT%H:%M:%SZ"


def ts(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, FMT)


def names_of(group: str, roster: dict) -> list:
    out = [group.lower()]
    for g in roster.get("groups", []):
        b = (g.get("resume") or {}).get("branch")
        if g.get("group") == group and b:
            out.append(b.lower())
    return out


def is_named(group: str, roster: dict, prs: list, refs: str, fired: str) -> bool:
    hay = "\n".join([p.get("headRefName", "") for p in prs] + [refs] +
                    [l for l in fired.splitlines() if "FIRED" in l]).lower()
    return any(re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", hay) for n in names_of(group, roster))


def detect(plan, base, roster, prs, refs, fired, now, grace_min, late_h, closure_h):
    """[(key, kind, line)], critical-path IDLE first."""
    now_t = ts(now)
    horizon = now_t + dt.timedelta(minutes=grace_min)
    cp = plan.get("critical_path") or []
    idle, rest = [], []
    for g, v in sorted(plan["groups"].items()):
        if v.get("done") or not v.get("start"):
            continue
        if ts(v["start"]) <= horizon and not is_named(g, roster, prs, refs, fired):
            tag = " CP" if g in cp else ""
            row = (f"IDLE:{g}", "IDLE", f"GANTT-SLIP IDLE{tag} {g} start={v['start']}")
            (idle if tag else rest).append(row)
        old = (base.get("finish") or {}).get(g)
        if old and v.get("finish"):
            d = (ts(v["finish"]) - ts(old)).total_seconds()
            if d > late_h * 3600:
                rest.append((f"LATE:{g}", "LATE", f"GANTT-SLIP LATE {g} finish={v['finish']} baseline={old} moved_h={d / 3600:.1f}"))
    c_old, c_new = base.get("closure"), plan["summary"].get("closure")
    if c_old and c_new:
        d = (ts(c_new) - ts(c_old)).total_seconds()
        if d > closure_h * 3600:
            rest.append(("CLOSURE", "CLOSURE", f"GANTT-SLIP CLOSURE closure={c_new} baseline={c_old} moved_h={d / 3600:.1f}"))
    return idle + rest


def apply_acks(slips, acks, base, plan, now):
    """(unsilenced lines, new baseline, GANTT-BASELINE lines)."""
    now_t = ts(now)
    new = json.loads(json.dumps(base))
    lines, notes = [], []
    for key, kind, line in slips:
        silenced = False
        for a in acks:
            if a.get("key") != key:
                continue
            if a.get("kind") == "accept":
                silenced = True
                if kind == "LATE":
                    g = key.split(":", 1)[1]
                    new.setdefault("finish", {})[g] = plan["groups"][g]["finish"]
                    notes.append(f"GANTT-BASELINE {key} finish={plan['groups'][g]['finish']}")
                elif kind == "CLOSURE":
                    new["closure"] = plan["summary"]["closure"]
                    notes.append(f"GANTT-BASELINE {key} closure={plan['summary']['closure']}")
            elif a.get("kind") in ("act", "defer"):
                if not a.get("until") or now_t < ts(a["until"]):
                    silenced = True
        if not silenced:
            lines.append(line)
    return lines, new, notes


def run(a) -> int:
    load = lambda p: json.load(open(p, encoding="utf-8"))
    text = lambda p: open(p, encoding="utf-8").read()
    plan, base, acks = load(a.plan), load(a.baseline), load(a.acks)
    slips = detect(plan, base, load(a.roster), load(a.prs), text(a.refs), text(a.fired),
                   a.now, a.grace_min, a.late_hours, a.closure_hours)
    lines, new, notes = apply_acks(slips, acks, base, plan, a.now)
    for l in lines + notes:
        print(l)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(new, fh, indent=1, sort_keys=True)
    return 0


# ------------------------------------------------------------------ self-test

NOW = "2026-11-01T18:00:00Z"


def fixture():
    g = lambda s, f, done=False: {"start": s, "finish": f, "done": done, "slot": 0}
    plan = {"groups": {
        "CPG": g("2026-11-01T17:00:00Z", "2026-11-02T00:00:00Z"),     # critical, unnamed
        "EDGE": g("2026-11-01T19:00:00Z", "2026-11-02T01:00:00Z"),    # starts exactly at now+grace
        "FARG": g("2026-11-01T19:00:01Z", "2026-11-02T01:00:00Z"),    # starts after the horizon
        "PRG": g("2026-11-01T17:00:00Z", "2026-11-02T01:00:00Z"),     # named by an open PR
        "REFG": g("2026-11-01T17:00:00Z", "2026-11-02T01:00:00Z"),    # named by a handoff ref
        "FIRG": g("2026-11-01T17:00:00Z", "2026-11-02T01:00:00Z"),    # named by a FIRED line
        "DONEG": g("2026-11-01T10:00:00Z", "2026-11-01T11:00:00Z", True),
        "LATEG": g("2026-11-01T20:00:00Z", "2026-11-02T10:00:01Z"),   # moved 6h + 1s
        "NEARG": g("2026-11-01T20:00:00Z", "2026-11-02T10:00:00Z"),   # moved exactly 6h: not late
        "EARLYG": g("2026-11-01T20:00:00Z", "2026-11-02T01:00:00Z"),  # moved 9h earlier: not late
    }, "critical_path": ["CPG"], "summary": {"closure": "2026-11-05T12:00:01Z"}}
    base = {"closure": "2026-11-05T10:00:00Z", "finish": {
        "LATEG": "2026-11-02T04:00:00Z", "NEARG": "2026-11-02T04:00:00Z",
        "EARLYG": "2026-11-02T10:00:00Z"}}
    roster = {"groups": [{"group": "REFG", "resume": {"branch": "handoff/refg-x"}}]}
    prs = [{"headRefName": "fix/prg"}]
    refs = "abc\trefs/heads/handoff/refg-x\n"
    fired = "2026-11-01T17:30Z FIRED fixer for firg\nnot a match: edge FIRE-OWED\n"
    return plan, base, roster, prs, refs, fired


def _conf(mod):
    """Run the checks against module namespace `mod`; return (checks, failed names)."""
    n, bad = [0], []

    def check(name, cond):
        n[0] += 1
        if not cond:
            bad.append(name)
            print(f"  FAIL {name}")

    plan, base, roster, prs, refs, fired = fixture()
    sl = mod["detect"](plan, base, roster, prs, refs, fired, NOW, 60, 6, 2)
    keys = [k for k, _, _ in sl]
    check("IDLE critical-path group is tagged CP", any(k == "IDLE:CPG" and "IDLE CP " in l for k, _, l in sl))
    check("critical-path IDLE is listed first", keys and keys[0] == "IDLE:CPG")
    check("IDLE at exactly now+grace is reported", "IDLE:EDGE" in keys)
    check("null: a start past now+grace is not IDLE", "IDLE:FARG" not in keys)
    check("null: an open PR head silences IDLE", "IDLE:PRG" not in keys)
    check("null: a handoff ref silences IDLE", "IDLE:REFG" not in keys)
    check("null: a FIRED line silences IDLE", "IDLE:FIRG" not in keys)
    check("null: a non-FIRED ledger line does not silence IDLE", "IDLE:EDGE" in keys)
    check("null: a done group is not IDLE", "IDLE:DONEG" not in keys)
    check("LATE past the threshold", "LATE:LATEG" in keys)
    check("null: a finish inside the threshold is not LATE", "LATE:NEARG" not in keys)
    check("null: a finish moved earlier is not LATE", "LATE:EARLYG" not in keys)
    check("CLOSURE past the threshold", "CLOSURE" in keys)
    plan["summary"]["closure"] = "2026-11-05T12:00:00Z"
    check("null: closure inside the threshold is not CLOSURE",
          "CLOSURE" not in [k for k, _, _ in mod["detect"](plan, base, roster, prs, refs, fired, NOW, 60, 6, 2)])
    plan["summary"]["closure"] = "2026-11-05T12:00:01Z"

    ap = mod["apply_acks"]
    out, nb, notes = ap(sl, [], base, plan, NOW)
    check("no acks: every slip is printed", len(out) == len(sl) and not notes and nb == base)
    for kind in ("act", "defer"):
        acks = [{"key": "IDLE:CPG", "kind": kind, "until": "2026-11-01T19:00:00Z"}]
        out, _, _ = ap(sl, acks, base, plan, NOW)
        check(f"{kind} silences its key before until", not any("IDLE CP CPG" in l for l in out) and len(out) == len(sl) - 1)
        out, _, _ = ap(sl, acks, base, plan, "2026-11-01T19:00:00Z")
        check(f"{kind} lapses at until", any("IDLE CP CPG" in l for l in out))
    out, _, _ = ap(sl, [{"key": "IDLE:CPG", "kind": "act"}], base, plan, NOW)
    check("act without until silences for good", len(out) == len(sl) - 1)
    out, _, _ = ap(sl, [{"key": "LATE:NOPE", "kind": "act"}], base, plan, NOW)
    check("null: an ack for another key silences nothing", len(out) == len(sl))
    acks = [{"key": "LATE:LATEG", "kind": "accept"}, {"key": "CLOSURE", "kind": "accept"},
            {"key": "IDLE:EDGE", "kind": "accept"}]
    out, nb, notes = ap(sl, acks, base, plan, NOW)
    check("accept silences its key", not any(" LATE LATEG" in l or "CLOSURE closure" in l or "IDLE EDGE" in l for l in out))
    check("accept re-baselines LATE", nb["finish"]["LATEG"] == "2026-11-02T10:00:01Z")
    check("accept re-baselines CLOSURE", nb["closure"] == "2026-11-05T12:00:01Z")
    check("accept leaves other baselines alone", nb["finish"]["NEARG"] == base["finish"]["NEARG"])
    check("accept prints GANTT-BASELINE lines", len(notes) == 2 and all(x.startswith("GANTT-BASELINE") for x in notes))
    check("accept does not mutate the input baseline", base["closure"] == "2026-11-05T10:00:00Z")
    return n[0], bad


# One textual edit per arm; each `old` occurs exactly once in this file.
MUTANTS = [
    ("idle-horizon", "if ts(v[\"start\"]) <= horizon and", "if ts(v[\"start\"]) < horizon and"),
    ("idle-prs", "[p.get(\"headRefName\", \"\") for p in prs]", "[]"),
    ("idle-refs", "+ [refs] +", "+ [] +"),
    ("idle-fired", "[l for l in fired.splitlines() if \"FIRED\" in l]", "[l for l in fired.splitlines()]"),
    ("idle-cp-first", "return idle + rest", "return rest + idle"),
    ("idle-cp-tag", "tag = \" CP\" if g in cp else \"\"", "tag = \"\""),
    ("late-threshold", "if d > late_h * 3600:", "if d >= late_h * 3600:"),
    ("late-direction", "if d > late_h * 3600:", "if abs(d) > late_h * 3600:"),
    ("closure-threshold", "if d > closure_h * 3600:", "if d >= closure_h * 3600:"),
    ("ack-until", "now_t < ts(a[\"until\"])", "now_t <= ts(a[\"until\"])"),
    ("ack-defer", "elif a.get(\"kind\") in (\"act\", \"defer\"):", "elif a.get(\"kind\") in (\"act\",):"),
    ("ack-key", "if a.get(\"key\") != key:", "if False:"),
    ("accept-late", "new.setdefault(\"finish\", {})[g] = plan[\"groups\"][g][\"finish\"]", "pass"),
    ("accept-closure", "new[\"closure\"] = plan[\"summary\"][\"closure\"]", "pass"),
    ("accept-silence", "silenced = True\n                if kind == \"LATE\":", "if kind == \"LATE\":"),
]


def self_test() -> int:
    # Mutate the text above MUTANTS only: the list itself quotes every `old`.
    src = open(__file__, encoding="utf-8").read().split("# One textual edit", 1)[0]
    total, failed = _conf(globals())
    print(f"  base: {total} checks")
    for name, old, new in MUTANTS:
        if src.count(old) != 1:
            total += 1
            failed.append(f"mutant {name}: old text occurs {src.count(old)} times")
            print(f"  FAIL mutant {name} is not applicable")
            continue
        ns = {"__name__": "gantt_mutant", "__file__": __file__}
        exec(compile(src.replace(old, new), f"<mutant {name}>", "exec"), ns)
        total += 1
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                _, bad = _conf(ns)
            except Exception:  # a crash kills the mutant too
                bad = ["crash"]
        if bad:
            print(f"  ok   mutant {name} killed")
        else:
            failed.append(f"mutant {name} survived")
            print(f"  FAIL mutant {name} survived")
    print(f"gantt_drift self-test: {total} checks, {len(failed)} failed")
    return 1 if failed else 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    for f in ("plan", "baseline", "acks", "roster", "prs", "refs", "fired", "now", "out"):
        ap.add_argument(f"--{f}")
    ap.add_argument("--grace-min", type=int, default=60)
    ap.add_argument("--late-hours", type=float, default=6)
    ap.add_argument("--closure-hours", type=float, default=2)
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    miss = [f for f in ("plan", "baseline", "acks", "roster", "prs", "refs", "fired", "now") if not getattr(a, f)]
    if miss:
        ap.error("required: " + ", ".join("--" + m for m in miss))
    return run(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
