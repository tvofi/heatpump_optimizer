#!/usr/bin/env python3
"""Per round and per dimension: found, fixed, injected, escaped, each with its denominator.

Usage (from the repo root):
  python3 -I tools/audit/convergence.py report --round N --roster FILE [--rotation FILE] [--out-json]
  python3 -I tools/audit/convergence.py check --roster FILE
  python3 -I tools/audit/convergence.py record --round N --roster FILE [--rotation FILE] [--replace]
  python3 -I tools/audit/convergence.py recurrence [--ledger dev/audit/config/bugclasses.json]
  python3 -I tools/audit/convergence.py --self-test
Sources: rotation.json (universe, examined, found = yield) and a roster {"groups": [...]}. A DEFECT group
has source "outside", kind hotfix|bug|defect, or HOTFIX in its name; its `cause` is {dimension: D<k>|none,
pr: int|null, round: int|null, by: fix|feature|preexisting|unknown}. Dimension of a finding id = text before
its first "-". injected = defect groups with by == "fix" and cause.round in (N, N-1), on cause.dimension's line.
Refusals: `check` (exit 1) names every DEFECT group at stage done with no well-formed cause; `record`
(exit 1) refuses what `check` refuses, and a differing rounds[N] already on file unless --replace.
A depth-word coverage (rounds <= 10) prints universe=? examined=?. `recurrence` is report-only.
Null control: --self-test plants each refusal with its passing twin, a round N-2 fix that must not count as
injected, and a date pair on either side of barriered_at.
"""
import argparse, contextlib, io, json, re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "dev/audit/config/convergence.json"
ROTATION = ROOT / "dev/audit/config/rotation.json"
LEDGER = ROOT / "dev/audit/config/bugclasses.json"
BYS = ("fix", "feature", "preexisting", "unknown")


def load(p):
    return json.loads(Path(p).read_text())


def is_defect(g):
    return g.get("source") == "outside" or g.get("kind") in ("hotfix", "bug", "defect") or "HOTFIX" in str(g.get("group", ""))


def done(g):
    return (g.get("resume") or {}).get("stage") == "done"


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cause_ok(c):
    if not isinstance(c, dict) or not isinstance(c.get("dimension"), str) or not re.fullmatch(r"D\d+|none", c["dimension"]):
        return False
    if c.get("by") not in BYS:
        return False
    return c["by"] != "fix" or (_int(c.get("pr")) and _int(c.get("round")))


def unattributed(roster):
    return [g.get("group", "?") for g in roster["groups"] if is_defect(g) and done(g) and not cause_ok(g.get("cause"))]


def dkey(d):
    return (1, 0) if d == "none" else (0, int(d[1:]))


def compute(n, roster, rotation):
    """{dimension: {universe, examined, found, fixed, fix_groups_done, injected, escaped}}; universe None when unrecorded."""
    groups = roster["groups"]
    fg = sum(1 for g in groups if done(g) and g.get("findings"))
    rows = {}

    def row(d):
        return rows.setdefault(d, dict(universe=None, examined=None, found=0, fixed=0, fix_groups_done=fg, injected=0, escaped=0))

    for d, e in rotation.items():
        r = (e.get("rounds") or {}).get(str(n)) if re.fullmatch(r"D\d+", d) and isinstance(e, dict) else None
        if r is None:
            continue
        x = row(d)
        cov = list((r.get("coverage") or {}).values())
        if cov and all(isinstance(c, dict) for c in cov):
            x["universe"] = sum(c["universe"] for c in cov)
            x["examined"] = sum(c["examined"] for c in cov)
        x["found"] = sum((r.get("yield") or {}).values())
    for g in groups:
        c = g.get("cause")
        if is_defect(g) and isinstance(c, dict) and isinstance(c.get("dimension"), str):
            x = row(c["dimension"])
            x["escaped"] += 1
            if c.get("by") == "fix" and c.get("round") in (n, n - 1):
                x["injected"] += 1
    for g in groups:
        for f in g.get("findings") or []:
            if f.split("-")[0] in rows and done(g):
                rows[f.split("-")[0]]["fixed"] += 1
    return dict(sorted(rows.items(), key=lambda kv: dkey(kv[0])))


def fmt(d, x):
    u = "?" if x["universe"] is None else x["universe"]
    e = "?" if x["examined"] is None else x["examined"]
    f, s = x["found"], x["escaped"]
    return (f"{d} universe={u} examined={e} found={f} fixed={x['fixed']}/{f} "
            f"injected={x['injected']}/{x['fix_groups_done']} escaped={s}/{f + s}")


def total(rows):
    t = {k: sum(x[k] for x in rows.values()) for k in ("found", "fixed", "injected", "escaped")}
    owned = [x for d, x in rows.items() if d != "none"]
    for k in ("universe", "examined"):
        t[k] = None if any(x[k] is None for x in owned) else sum(x[k] for x in owned)
    t["fix_groups_done"] = next((x["fix_groups_done"] for x in rows.values()), 0)
    return t


def report(n, roster, rotation, as_json=False):
    rows = compute(n, roster, rotation)
    if as_json:
        return json.dumps(rows, indent=2, sort_keys=True)
    return "\n".join([fmt(d, x) for d, x in rows.items()] + [fmt("TOTAL", total(rows))])


def check(roster):
    bad = unattributed(roster)
    n = sum(1 for g in roster["groups"] if is_defect(g))
    for g in bad:
        print(f"UNATTRIBUTED: defect group {g} is done and has no well-formed cause {{dimension, pr, round, by}}")
    if bad:
        return 1
    print(f"ok convergence: {n} defect group(s), all attributed")
    return 0


def record(n, roster, rotation, path, replace=False):
    if check(roster):
        return 1
    cfg = load(path)
    new = compute(n, roster, rotation)
    old = cfg["rounds"].get(str(n))
    if old is not None and old != json.loads(json.dumps(new)) and not replace:
        print(f"REFUSED: rounds[{n}] exists and differs; pass --replace to overwrite")
        return 1
    cfg["rounds"][str(n)] = new
    Path(path).write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    return 0


def recurrence(ledger, cfg):
    base = cfg.get("baselines", {})
    for cid, e in ledger.items():
        if cid.startswith("_") or not isinstance(e, dict) or e.get("status") != "barriered":
            continue
        at, after, before = e.get("barriered_at"), 0, 0
        for s in e.get("instances", []):
            m = re.match(r"R(\d+) ", s)
            d = (base.get(m.group(1)) or {}).get("date") if m else None
            if d and at and d > at:
                after += 1
            else:
                before += 1
        print(f"{cid} barriered_at={at or '?'} instances_after={after} instances_before_or_undated={before}")


def self_test():
    fails, arms = [], []

    def expect(name, ok):
        arms.append(name)
        if not ok:
            fails.append(name)

    def cap(fn, *a, **k):
        b = io.StringIO()
        with contextlib.redirect_stdout(b):
            rc = fn(*a, **k)
        return rc, b.getvalue()

    def grp(name, **kw):
        return {"group": name, "resume": {"stage": "done"}, **kw}

    cause = lambda dim, by, **kw: {"dimension": dim, "by": by, "pr": kw.get("pr"), "round": kw.get("round")}
    # arm 1-2: check refuses a done defect without cause; passes with one; refuses a malformed one
    bare = {"groups": [grp("X", kind="hotfix")]}
    expect("check: done defect without cause refused", cap(check, bare)[0] == 1 and "X" in cap(check, bare)[1])
    expect("check null control: with a cause it passes", cap(check, {"groups": [grp("X", kind="hotfix", cause=cause("D1", "feature"))]})[0] == 0)
    expect("check: by fix with no pr refused", cap(check, {"groups": [grp("X", source="outside", cause=cause("D1", "fix", round=10))]})[0] == 1)
    expect("check null control: by fix with pr and round passes", cap(check, {"groups": [grp("X", source="outside", cause=cause("D1", "fix", pr=5, round=10))]})[0] == 0)
    expect("check: not-done defect needs no cause", cap(check, {"groups": [{"group": "Y", "kind": "bug"}, grp("F", findings=["D1-s1-01"])]})[0] == 0)
    # arm 3: report on a planted rotation + roster
    rot = {"D1": {"rounds": {"11": {"coverage": {"M1": {"universe": 10, "examined": 8}, "M2": {"universe": 5, "examined": 5}}, "yield": {"M1": 2, "M2": 1}}}},
           "D2": {"rounds": {"11": {"coverage": {"M1": "deep"}, "yield": {"M1": 1}}}}}
    ros = {"groups": [
        grp("A", findings=["D1-s1-01", "D1-s1-02"]),
        {"group": "B", "findings": ["D1-s1-03", "D2-s1-01"], "resume": {"stage": "fixing"}},
        grp("H1", kind="hotfix", cause=cause("D1", "fix", pr=9, round=11)),
        grp("H2", source="outside", cause=cause("D1", "fix", pr=8, round=10)),
        grp("H3", kind="bug", cause=cause("D2", "fix", pr=7, round=9)),
        grp("H4 HOTFIX", cause=cause("none", "unknown")),
    ]}
    want = ["D1 universe=15 examined=13 found=3 fixed=2/3 injected=2/1 escaped=2/5",
            "D2 universe=? examined=? found=1 fixed=0/1 injected=0/1 escaped=1/2",
            "none universe=? examined=? found=0 fixed=0/0 injected=0/1 escaped=1/1",
            "TOTAL universe=? examined=? found=4 fixed=2/4 injected=2/1 escaped=4/8"]
    got = report(11, ros, rot).split("\n")
    expect("report: exact lines (? for a depth word, N-2 fix not injected, none line)", got == want)
    # the "none" line carries fix_groups_done too; spelled out above, so the want is the contract
    # arm 4: record writes the reported numbers; a differing overwrite is refused without --replace
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "c.json"
        p.write_text(json.dumps({"baselines": {}, "rounds": {}}))
        rc, _ = cap(record, 11, ros, rot, p)
        rows = load(p)["rounds"]["11"]
        expect("record: writes the reported numbers", rc == 0 and rows["D1"]["found"] == 3 and rows["D1"]["injected"] == 2
               and rows["D2"]["universe"] is None and rows["none"]["escaped"] == 1 and p.read_text().endswith("}\n"))
        expect("record null control: identical rewrite accepted", cap(record, 11, ros, rot, p)[0] == 0)
        rot2 = json.loads(json.dumps(rot))
        rot2["D1"]["rounds"]["11"]["yield"]["M1"] = 3
        rc, _ = cap(record, 11, ros, rot2, p)
        expect("record: differing overwrite refused", rc == 1 and load(p)["rounds"]["11"]["D1"]["found"] == 3)
        expect("record: --replace overwrites", cap(record, 11, ros, rot2, p, True)[0] == 0 and load(p)["rounds"]["11"]["D1"]["found"] == 4)
        expect("record: refuses an unattributed roster", cap(record, 12, bare, rot, p)[0] == 1 and "12" not in load(p)["rounds"])
    # arm 5: recurrence by date
    led = {"_x": {}, "C": {"status": "barriered", "barriered_at": "2026-10-01", "instances": ["R8 a", "R11 b", "R12 c"]},
           "U": {"status": "barriered", "barriered_at": None, "instances": ["R11 d"]}, "O": {"status": "open", "instances": ["R11 e"]}}
    cfg = {"baselines": {"8": {"date": "2026-09-23"}, "11": {"date": "2026-10-20"}}}
    out = cap(recurrence, led, cfg)[1].splitlines()
    expect("recurrence: after vs before by date, undated and missing baseline count as before",
           out == ["C barriered_at=2026-10-01 instances_after=1 instances_before_or_undated=2",
                   "U barriered_at=? instances_after=0 instances_before_or_undated=1"])
    if fails:
        print("SELF-TEST FAILED: " + "; ".join(fails))
        return 1
    print(f"SELF-TEST passed ({len(arms)} arms)")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["report", "check", "record", "recurrence"])
    ap.add_argument("--round", type=int)
    ap.add_argument("--roster")
    ap.add_argument("--rotation", default=str(ROTATION))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--out-json", action="store_true")
    ap.add_argument("--replace", action="store_true")
    a = ap.parse_args()
    if a.cmd == "recurrence":
        recurrence(load(a.ledger), load(CONFIG))
        return 0
    if not a.roster or (a.cmd != "check" and a.round is None):
        ap.error(f"{a.cmd} needs --roster" + ("" if a.cmd == "check" else " and --round"))
    roster = load(a.roster)
    if a.cmd == "check":
        return check(roster)
    rot = load(a.rotation)
    if a.cmd == "record":
        return record(a.round, roster, rot, CONFIG, a.replace)
    print(report(a.round, roster, rot, a.out_json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
