#!/usr/bin/env python3
"""Compare the live state against the plan's Gantt and print each unacknowledged slip.

gantt_drift.py --plan PLAN.json --baseline BASE.json --acks ACKS.txt --roster ROSTER.json
               --open-prs PRS.json --handoffs REFS.txt --fired LEDGER.txt [--now ISO]
gantt_drift.py --self-test

Stand-in (orchestrator s10, 2026-11-01, tvofi: "each time the plan html is updated,
compare the real state against the gantt, mechanically if possible, and have slips
surfaced to you to act on, defer or accept") until a tracked instrument replaces it.

Slip kinds, one line each, `GANTT-SLIP <KEY> <detail>`:
  IDLE:<group>     the plan starts the group by now (+GRACE) and nothing is working on it:
                   no open PR, no handoff ref, no FIRED line naming its topic or group.
                   A critical-path group is tagged CP.
  LATE:<group>     its planned finish moved more than GROUP_H hours past the baseline's.
  CLOSURE          the plan's closure moved more than CLOSURE_H hours past the baseline's.
The baseline is the plan as last accepted; a missing baseline is seeded from --plan.

Acks file, one per line: `<ISO> <KEY> act|defer|accept [until=<ISO>] <reason>`.
  act / defer   silence KEY until `until` (default: 6 h after the ack's own time).
  accept        silence KEY for good AND re-baseline it (LATE: that group's finish;
                CLOSURE: the whole plan), so only a further slip reports again.
"""
import argparse, datetime as dt, json, re, sys

GRACE_MIN = 60
GROUP_H = 6.0
CLOSURE_H = 2.0
ACT_DEFAULT_H = 6.0
CLOSED_STAGES = {"done", "rca-done"}


def ts(s):
    return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def topic_of(name, group):
    br = ((group or {}).get("resume") or {}).get("branch") or ""
    t = br.split("/", 1)[1] if "/" in br else br
    if t:
        return t
    return "r10-" + name[len("R10-"):].lower() if name.startswith("R10-") else name.lower()


def read_acks(lines, now):
    live, accepted = {}, set()
    for ln in lines:
        p = ln.split()
        if len(p) < 3 or p[2] not in ("act", "defer", "accept"):
            continue
        at, key, verb = ts(p[0]), p[1], p[2]
        if verb == "accept":
            accepted.add(key)
            continue
        m = re.search(r"until=(\S+)", ln)
        until = ts(m.group(1)) if m else at + dt.timedelta(hours=ACT_DEFAULT_H)
        if until > now:
            live[key] = until
    return live, accepted


def rebaseline(base, plan, accepted):
    """Fold accepted keys into the baseline; return (baseline, changed)."""
    changed = False
    if "CLOSURE" in accepted and base.get("accepted_closure") != plan["summary"]["closure"]:
        base = {"summary": dict(plan["summary"]), "groups": {n: {"finish": g.get("finish")} for n, g in plan["groups"].items()},
                "accepted_closure": plan["summary"]["closure"], "accepted": sorted(accepted)}
        return base, True
    for key in accepted:
        if key.startswith("LATE:"):
            n = key[5:]
            f = plan["groups"].get(n, {}).get("finish")
            if f and base["groups"].get(n, {}).get("finish") != f and n not in base.get("accepted_groups", {}):
                base["groups"].setdefault(n, {})["finish"] = f
                base.setdefault("accepted_groups", {})[n] = f
                changed = True
    return base, changed


def slips(plan, base, roster, open_prs, handoffs, fired, now):
    groups = {g["group"]: g for g in roster}
    cp = set(plan.get("critical_path") or [])
    out = []
    pr_titles = [p.get("title", "") for p in open_prs]
    for n, g in sorted(plan["groups"].items()):
        if g.get("done"):
            continue
        stage = ((groups.get(n) or {}).get("resume") or {}).get("stage")
        if stage in CLOSED_STAGES:
            continue
        start = g.get("start")
        if start and ts(start) <= now + dt.timedelta(minutes=GRACE_MIN):
            topic = topic_of(n, groups.get(n))
            busy = (any(n in t for t in pr_titles)
                    or any(r.endswith("/" + topic) or r.endswith("/" + topic + "-p2") or ("/" + topic + "-") in r for r in handoffs)
                    or any(n in f or topic in f for f in fired))
            if not busy:
                out.append((0 if n in cp else 1, f"IDLE:{n}", f"{'CP ' if n in cp else ''}planned start {iso(ts(start))}, stage {stage}, no PR, handoff or fire"))
        bf = (base.get("groups", {}).get(n) or {}).get("finish")
        if bf and g.get("finish"):
            h = (ts(g["finish"]) - ts(bf)).total_seconds() / 3600
            if h > GROUP_H:
                out.append((0 if n in cp else 2, f"LATE:{n}", f"{'CP ' if n in cp else ''}finish {iso(ts(g['finish']))}, {h:+.1f} h vs baseline {iso(ts(bf))}"))
    c, bc = plan["summary"]["closure"], base["summary"]["closure"]
    h = (ts(c) - ts(bc)).total_seconds() / 3600
    if h > CLOSURE_H:
        out.append((0, "CLOSURE", f"closure {iso(ts(c))}, {h:+.1f} h vs baseline {iso(ts(bc))}"))
    return [(k, d) for _, k, d in sorted(out)]


def run(a):
    now = ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    plan = json.load(open(a.plan))
    try:
        base = json.load(open(a.baseline))
    except FileNotFoundError:
        base = {"summary": dict(plan["summary"]), "groups": {n: {"finish": g.get("finish")} for n, g in plan["groups"].items()},
                "seeded": iso(now)}
        json.dump(base, open(a.baseline, "w"), indent=1)
        print(f"GANTT-BASELINE seeded closure {base['summary']['closure']}")
    try:
        ack_lines = open(a.acks).read().splitlines()
    except FileNotFoundError:
        ack_lines = []
    live, accepted = read_acks(ack_lines, now)
    base, changed = rebaseline(base, plan, accepted)
    if changed:
        json.dump(base, open(a.baseline, "w"), indent=1)
        print(f"GANTT-BASELINE re-baselined (accepted: {', '.join(sorted(accepted))})")
    roster = json.load(open(a.roster))
    roster = roster["groups"] if isinstance(roster, dict) else roster
    prs = json.load(open(a.open_prs))
    handoffs = [l.split()[-1] for l in open(a.handoffs).read().splitlines() if l.strip()]
    fired = [l for l in open(a.fired).read().splitlines() if "FIRED" in l and l[:10] >= iso(now - dt.timedelta(days=2))[:10]]
    n = 0
    for key, detail in slips(plan, base, roster, prs, handoffs, fired, now):
        if key in live or key in accepted:
            continue
        print(f"GANTT-SLIP {key} {detail} -> ack: {iso(now)} {key} act|defer|accept [until=ISO] <reason> >> {a.acks}")
        n += 1
    return 0


def self_test():
    now = ts("2026-11-01T18:00:00Z")
    plan = {"critical_path": ["G-CP"], "summary": {"closure": "2026-11-05T04:00:00Z"},
            "groups": {"G-CP": {"start": "2026-11-01T17:00:00Z", "finish": "2026-11-02T04:00:00Z", "done": False},
                       "G-BUSY": {"start": "2026-11-01T17:00:00Z", "finish": "2026-11-02T04:00:00Z", "done": False},
                       "G-LATER": {"start": "2026-11-03T00:00:00Z", "finish": "2026-11-03T20:00:00Z", "done": False},
                       "G-DONE": {"start": None, "finish": None, "done": True}}}
    base = {"summary": {"closure": "2026-11-04T00:00:00Z"},
            "groups": {"G-CP": {"finish": "2026-11-02T04:00:00Z"}, "G-LATER": {"finish": "2026-11-03T08:00:00Z"}}}
    roster = [{"group": "G-CP", "resume": {"stage": "carries-open"}},
              {"group": "G-BUSY", "resume": {"stage": "in-progress", "branch": "handoff/r10-busy"}},
              {"group": "G-LATER", "resume": {"stage": "not-started"}}, {"group": "G-DONE", "resume": {"stage": "done"}}]
    got = dict(slips(plan, base, roster, [], ["x refs/heads/handoff/r10-busy"], [], now))
    want = {"IDLE:G-CP", "LATE:G-LATER", "CLOSURE"}
    assert set(got) == want, got
    assert got["IDLE:G-CP"].startswith("CP "), got
    # null control: the busy group is silent because of its handoff; remove it and it fires
    got2 = dict(slips(plan, base, roster, [], [], [], now))
    assert "IDLE:G-BUSY" in got2, got2
    # a FIRED line naming the group's topic also counts as busy
    got3 = dict(slips(plan, base, roster, [], [], ["2026-11-01T17:08:35Z FIRED G-CP p2"], now))
    assert "IDLE:G-CP" not in got3, got3
    # acks: act silences for 6 h by default, expired act does not, accept re-baselines
    live, acc = read_acks(["2026-11-01T17:30Z IDLE:G-CP act fixer firing",
                           "2026-11-01T08:00Z LATE:G-LATER defer waits on X",
                           "2026-11-01T17:40Z CLOSURE accept owner ruled"], now)
    assert "IDLE:G-CP" in live and "LATE:G-LATER" not in live and acc == {"CLOSURE"}, (live, acc)
    nb, ch = rebaseline(base, plan, acc)
    assert ch and nb["summary"]["closure"] == plan["summary"]["closure"]
    assert "CLOSURE" not in dict(slips(plan, nb, roster, [], [], [], now))
    nb2, ch2 = rebaseline(base, plan, {"LATE:G-LATER"})
    assert ch2 and "LATE:G-LATER" not in dict(slips(plan, nb2, roster, [], [], [], now))
    print("gantt_drift self-test: 9 checks passed")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for f in ("plan", "baseline", "acks", "roster", "open-prs", "handoffs", "fired", "now"):
        ap.add_argument("--" + f)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    sys.exit(self_test() if a.self_test else run(a))
