#!/usr/bin/env python3
"""Fold an audit round into tools/audit/bugclasses.json, and check the register.

  fold_ledger.py fold  --round N [--root DIR] [--dry-run]
  fold_ledger.py check [--root DIR] [--ledger FILE] [--judge FILE ...]
  fold_ledger.py refresh [--root DIR]
  fold_ledger.py --self-test

`fold` is run by .claude/workflows/audit-verify.js after the class sweep. It
reads tools/audit/round<N>/JUDGE.json and every sweep-<class>.json beside it
and appends, to each survivor's class, `R<N> <finding id>`, and, for each sweep
seam marked `beyond_finding: true`, `R<N> sw:<file>::<symbol>`. A seam marked
false is the judged site itself and counts nowhere. It recomputes rounds,
per_round, total, max_per_round and trigger, prints both terms of every class's
N for the round (judged, beyond_finding), and refuses:
  - a survivor with no class, or a sweep seam with no boolean beyond_finding;
  - a survivor or a sweep whose class the ledger lacks and no `nearest` and
    `differs` (a class id in the ledger, and why it is not that class)
    accompany: a class is a mechanism, never a site, and is minted only after
    comparing it with the nearest existing one (judge.md step 6);
  - a survivor already placed in another class.
Two classes minted in one round with one `nearest` are counted as one class for
the trigger. A new id also lands in finding.schema.json's class_guess enum,
which check-wave-script.mjs holds equal to the ledger.

`check` runs in the wave-script lane of governance.yml (one pass, under a
second) and refuses, printing one line each:
  UNPLACED/DOUBLE     an in-tree judge survivor (tools/audit/round*/JUDGE.json,
                      verdict verified or weakened) in no class, or in two;
  UNPARSED            an instance that is not `R<n> <id>`;
  DRIFT               rounds, per_round, total, max_per_round or trigger that
                      is not what the instances and status derive (derived, never
                      carried); `refresh` rewrites them, after a barrier PR moves
                      a class's status, say;
  OWED                a class that met an adopted trigger (defect-root-cause.md:
                      >=3 in one round, >=3 over three consecutive rounds, >=5
                      while not barriered, or any instance of a barriered
                      class) and carries neither a barrier nor an rca whose
                      document is in tools/audit/rca;
  UNKNOWN-RCA/DANGLING  a cited rca not in `_rca`, or an `in_tree_home` that is
                      not an existing file under tools/audit/rca.
The default root is the repository this file lives in; the lane runs the base's
copy of this file against the pull request's tree (--root), so a branch cannot
edit the grader it is graded by.
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile

SURVIVES = ("verified", "weakened")
CLASS_ID = re.compile(r"^(?:[PI]\d+|N-[a-z0-9]+(?:-[a-z0-9]+)*)$")
INSTANCE = re.compile(r"^R(\d+) (\S+)$")
RCA_DIR = "tools/audit/rca"
LEDGER = "tools/audit/bugclasses.json"
SCHEMA = "tools/audit/finding.schema.json"


def classes(led):
    return {k: v for k, v in led.items() if not k.startswith("_")}


def parse(s):
    m = INSTANCE.match(s) if isinstance(s, str) else None
    return (int(m.group(1)), m.group(2)) if m else None


def derive(entry):
    per = {}
    for s in entry.get("instances", []):
        p = parse(s)
        if p:
            per[p[0]] = per.get(p[0], 0) + 1
    return {"rounds": sorted(per), "per_round": {f"R{r}": per[r] for r in sorted(per)},
            "total": sum(per.values()), "max_per_round": max(per.values(), default=0)}


def _group_counts(led, cid):
    """Per-round counts for the trigger: the class's own, plus those of classes
    minted in the same round with the same nearest class (counted as one)."""
    me = led[cid]
    ids = [cid]
    if me.get("minted") and me.get("nearest_existing"):
        ids = [k for k, v in classes(led).items()
               if v.get("minted") == me["minted"] and v.get("nearest_existing") == me["nearest_existing"]]
    per = {}
    for k in ids:
        for r, n in derive(led[k])["per_round"].items():
            per[int(r[1:])] = per.get(int(r[1:]), 0) + n
    return per


def trigger(led, cid, last):
    per = _group_counts(led, cid)
    cnt = [per.get(r, 0) for r in range(1, max(last, 3) + 1)]
    status = led[cid].get("status")
    total = sum(cnt)
    return {"per_round": max(cnt) >= 3,
            "cross_round": any(sum(cnt[i:i + 3]) >= 3 for i in range(len(cnt) - 2)) or (total >= 5 and status != "barriered"),
            "barriered_any": status == "barriered" and total >= 1,
            "class_rca_on_record": any(led.get("_rca", {}).get(r, {}).get("level") == "class" for r in led[cid].get("rca", []))}


def last_round(led):
    return max([r for e in classes(led).values() for r in derive(e)["rounds"]] or [0])


def _has(v):
    return v not in (None, "", "None")


def settle(led):
    """Write every derived field from the instances (and a status that moved)."""
    last = last_round(led)
    for e in classes(led).values():
        e.update(derive(e))
    for cid, e in classes(led).items():
        e["trigger"] = trigger(led, cid, last)


def refresh(root):
    lp = os.path.join(root, LEDGER)
    led = json.load(open(lp))
    settle(led)
    open(lp, "w").write(json.dumps(led, indent=2, ensure_ascii=False))
    return 0


def survivors(root, judge_files=None):
    """{(round, id): file} of every judge survivor in the tree."""
    out = {}
    files = judge_files if judge_files is not None else sorted(glob.glob(os.path.join(root, "tools/audit/round*/JUDGE.json")))
    for f in files:
        j = json.load(open(f))
        for v in j.get("verdicts", []):
            if v.get("verdict") in SURVIVES:
                out[(int(j["round"]), v["id"])] = f
    return out


def check(root, ledger_path=None, judge_files=None):
    led = json.load(open(ledger_path or os.path.join(root, LEDGER)))
    bad = []
    where = {}
    for cid, e in classes(led).items():
        for s in e.get("instances", []):
            p = parse(s)
            if p is None:
                bad.append(f"UNPARSED: {cid} instance {s!r} is not 'R<n> <id>'")
            else:
                where.setdefault(p, []).append(cid)
    for u in led.get("_unclassified", []):
        if _has(u.get("reason")):
            where.setdefault((int(u["round"][1:]), u["finding_id"]), []).append("_unclassified")
    surv = survivors(root, judge_files)
    for (r, i), f in sorted(surv.items()):
        w = where.get((r, i), [])
        if not w:
            bad.append(f"UNPLACED: R{r} {i} ({os.path.relpath(f, root)}) is in no class")
        elif len(w) > 1:
            bad.append(f"DOUBLE: R{r} {i} is in {', '.join(w)}")
    last = last_round(led)
    for cid, e in classes(led).items():
        want = derive(e)
        for k, v in want.items():
            if e.get(k) != v:
                bad.append(f"DRIFT: {cid}.{k} is {e.get(k)!r}, the instances derive {v!r}")
        t = trigger(led, cid, last)
        for k, v in t.items():
            if e.get("trigger", {}).get(k) != v:
                bad.append(f"DRIFT: {cid}.trigger.{k} is {e.get('trigger', {}).get(k)!r}, derived {v!r} (fold_ledger.py refresh)")
        rcas = e.get("rca", [])
        for r in rcas:
            if r not in led.get("_rca", {}):
                bad.append(f"UNKNOWN-RCA: {cid} cites {r}, which _rca does not index")
        met = t["per_round"] or t["cross_round"] or t["barriered_any"]
        home = [r for r in rcas if _intree(root, led.get("_rca", {}).get(r, {}).get("in_tree_home"))]
        if met and not _has(e.get("barrier")) and not home:
            bad.append(f"OWED: {cid} met a trigger ({_why(t)}) and has no barrier and no rca document in {RCA_DIR}")
    for r, e in led.get("_rca", {}).items():
        h = e.get("in_tree_home")
        if h is not None and not _intree(root, h):
            bad.append(f"DANGLING: _rca[{r}].in_tree_home {h!r} is not a file under {RCA_DIR}")
    n = sum(derive(e)["total"] for e in classes(led).values())
    print(f"fold_ledger: {len(classes(led))} classes, {n} instances, {len(surv)} in-tree judge survivors "
          f"(rounds {sorted({r for r, _ in surv})}), {len(led.get('_rca', {}))} rca entries")
    for b in bad:
        print(b)
    print(f"fold_ledger: {len(bad)} violation(s)")
    return 1 if bad else 0


def _intree(root, rel):
    return bool(rel) and rel.startswith(RCA_DIR + "/") and os.path.isfile(os.path.join(root, rel))


def _why(t):
    return ", ".join(k for k in ("per_round", "cross_round", "barriered_any") if t[k])


def fold(root, rnd, dry=False):
    d = os.path.join(root, f"tools/audit/round{rnd}")
    jp = os.path.join(d, "JUDGE.json")
    lp = os.path.join(root, LEDGER)
    raw = open(lp).read()
    led = json.loads(raw)
    j = json.load(open(jp))
    if int(j.get("round", -1)) != rnd:
        raise SystemExit(f"REFUSE: {jp} is round {j.get('round')}, not {rnd}")
    surv = [v for v in j.get("verdicts", []) if v.get("verdict") in SURVIVES]
    new = {}
    for v in surv:
        c = v.get("class")
        if not c:
            raise SystemExit(f"REFUSE: survivor {v['id']} has no class")
        if c in classes(led) or c in new:
            if c in new:
                new[c].append(v)
            continue
        new[c] = [v]
    for c, vs in new.items():
        got = {k: next((v[k] for v in vs if str(v.get(k, "")).strip()), "") for k in ("class_mechanism", "nearest", "differs")}
        if not CLASS_ID.match(c):
            raise SystemExit(f"REFUSE: class {c!r} is not in the ledger and is not a well-formed new id (P<n>, I<n> or N-<name>)")
        if not got["nearest"] or not got["differs"]:
            raise SystemExit(f"REFUSE: new class {c} (survivors {[v['id'] for v in vs]}) carries no nearest and differs: "
                             "name the closest existing class and the mechanism difference, or place the finding in it")
        if got["nearest"] not in classes(led):
            raise SystemExit(f"REFUSE: new class {c} names nearest {got['nearest']!r}, which the ledger does not have")
        if not got["class_mechanism"]:
            raise SystemExit(f"REFUSE: new class {c} carries no class_mechanism")
        led[c] = {"kind": vs[0].get("class_kind") or led[got["nearest"]].get("kind", "production"),
                  "mechanism": got["class_mechanism"], "rounds": [], "instances": [], "per_round": {}, "total": 0,
                  "max_per_round": 0, "detector": None, "barrier": None, "status": "open",
                  "nearest_existing": got["nearest"], "mechanism_difference": got["differs"], "minted": f"R{rnd}",
                  "aliases": [], "rca": [], "rca_planned": [], "trigger": {}}
    placed = {}
    for cid, e in classes(led).items():
        for s in e["instances"]:
            placed.setdefault(parse(s), cid)
    added = {}

    def put(cid, inst, kind):
        p = parse(inst)
        if p in placed:
            if placed[p] != cid:
                raise SystemExit(f"REFUSE: {inst} is already in {placed[p]}, and this round puts it in {cid}")
            return
        placed[p] = cid
        led[cid]["instances"].append(inst)
        added.setdefault(cid, {"judged": 0, "beyond_finding": 0})[kind] += 1

    for v in sorted(surv, key=lambda v: v["id"]):
        put(v["class"], f"R{rnd} {v['id']}", "judged")
    for sp in sorted(glob.glob(os.path.join(d, "sweep-*.json"))):
        s = json.load(open(sp))
        cid = s.get("class")
        if cid not in classes(led):
            raise SystemExit(f"REFUSE: {os.path.basename(sp)} sweeps class {cid!r}, which is in no class of the ledger")
        for it in s.get("instance_list", []):
            if not isinstance(it.get("beyond_finding"), bool):
                raise SystemExit(f"REFUSE: {os.path.basename(sp)} seam {it.get('file')}::{it.get('symbol')} has no boolean beyond_finding")
            if it["beyond_finding"]:
                put(cid, f"R{rnd} " + f"sw:{it['file']}::{it['symbol']}".replace(" ", "_"), "beyond_finding")
    settle(led)
    print(f"fold_ledger: round {rnd}: {sum(a['judged'] for a in added.values())} judged survivor(s) and "
          f"{sum(a['beyond_finding'] for a in added.values())} beyond_finding seam(s) folded into {len(added)} class(es)")
    for cid in sorted(added):
        a = added[cid]
        print(f"  {cid}: judged {a['judged']} + beyond_finding {a['beyond_finding']} = N {a['judged'] + a['beyond_finding']} "
              f"(round total {derive(led[cid])['per_round'].get(f'R{rnd}', 0)}){' NEW (nearest ' + led[cid]['nearest_existing'] + ')' if cid in new else ''}")
    if dry:
        return 0
    open(lp, "w").write(json.dumps(led, indent=2, ensure_ascii=False))
    if new:
        sp = os.path.join(root, SCHEMA)
        txt = open(sp).read()
        m = re.search(r'("class_guess": \{"enum": )(\[[^\]]*\])', txt)
        ids = json.loads(m.group(2))
        ids = [i for i in ids if i != "new"] + [c for c in new if c not in ids] + ["new"]
        open(sp, "w").write(txt[:m.start(2)] + json.dumps(ids) + txt[m.end(2):])
    return 0


def _plant(root, ledger, judge=None, sweep=None, docs=()):
    os.makedirs(os.path.join(root, RCA_DIR), exist_ok=True)
    os.makedirs(os.path.join(root, "tools/audit/round2"), exist_ok=True)
    json.dump(ledger, open(os.path.join(root, LEDGER), "w"), indent=2, ensure_ascii=False)
    open(os.path.join(root, SCHEMA), "w").write('{"class_guess": {"enum": ["P1", "P2", "new"], "description": "x"}}\n')
    if judge is not None:
        json.dump(judge, open(os.path.join(root, "tools/audit/round2/JUDGE.json"), "w"))
    if sweep is not None:
        json.dump(sweep, open(os.path.join(root, "tools/audit/round2/sweep-P1.json"), "w"))
    for dname in docs:
        open(os.path.join(root, RCA_DIR, dname), "w").write("# rca\n")


def _entry(insts, **kw):
    e = {"kind": "production", "mechanism": "m", "instances": list(insts), "status": "open", "barrier": None, "rca": [],
         "rounds": [], "per_round": {}, "total": 0, "max_per_round": 0, "trigger": {}}
    e.update(kw)
    return e


def _settle(led):
    settle(led)
    return led


def self_test():
    """Each refusal on a planted shape, and the null control that it stays quiet on a clean one."""
    fails = []

    def expect(name, ok):
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            fails.append(name)

    def run_check(led, judge=None, docs=()):
        with tempfile.TemporaryDirectory() as t:
            _plant(t, led, judge, docs=docs)
            import io
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = check(t)
            return rc, buf.getvalue()

    J = {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified", "class": "P1"}, {"id": "D1-02", "verdict": "refuted"}]}
    clean = _settle({"P1": _entry(["R2 D1-01"]), "P2": _entry(["R1 D2-01"]), "_rca": {}, "_unclassified": [], "_excluded": []})
    rc, out = run_check(clean, J)
    expect("null control: a ledger placing its survivor once, with nothing owed, passes", rc == 0 and "0 violation" in out)
    rc, out = run_check(_settle({"P1": _entry([]), "_rca": {}}), J)
    expect("a judge survivor in no class is UNPLACED (a refuted verdict is not one)", rc == 1 and "UNPLACED: R2 D1-01" in out and "D1-02" not in out)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01"]), "P2": _entry(["R2 D1-01"]), "_rca": {}}), J)
    expect("a survivor in two classes is DOUBLE", "DOUBLE: R2 D1-01" in out)
    rc, out = run_check({**clean, "P1": {**clean["P1"], "total": 9}}, J)
    expect("a carried total that the instances do not derive is DRIFT", "DRIFT: P1.total" in out)
    stale = _settle({"P1": _entry(["R2 D1-01"], rca=[]), "_rca": {}})
    stale["P1"]["status"] = "barriered"
    stale["P1"]["barrier"] = "a check"
    rc, out = run_check(stale, J)
    with tempfile.TemporaryDirectory() as t:
        _plant(t, stale, J)
        refresh(t)
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            rc2 = check(t)
    expect("a status moved by a barrier PR leaves the carried trigger stale (DRIFT), and refresh clears it", "DRIFT: P1.trigger.barriered_any" in out and rc2 == 0)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01", "R2 a", "R2 b"]), "_rca": {}}), J)
    expect("three instances in one round with no barrier and no rca is OWED", "OWED: P1" in out)
    owed = _settle({"P1": _entry(["R2 D1-01", "R2 a", "R2 b"], rca=["X"]), "_rca": {"X": {"level": "class", "in_tree_home": f"{RCA_DIR}/X.md"}}})
    rc, out = run_check(owed, J, docs=("X.md",))
    expect("an rca whose document is in tools/audit/rca answers it", rc == 0)
    rc, out = run_check(owed, J)
    expect("the same rca with its document missing is DANGLING and the class OWED", "DANGLING: _rca[X]" in out and "OWED: P1" in out)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01", "R2 a", "R2 b"], barrier="a check"), "_rca": {}}), J)
    expect("a barrier answers it", rc == 0)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01", "R1 a", "R3 b"]), "_rca": {}}), J)
    expect("three over three consecutive rounds (1,1,1) met the cross-round arm", "cross_round" in out and "OWED: P1" in out)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01", "R1 a", "R5 b"]), "_rca": {}}), J)
    expect("null control: three instances spread over rounds 1, 2 and 5 meet neither arm", rc == 0)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01", "R4 a", "R6 b", "R8 c", "R9 d"]), "_rca": {}}), J)
    expect("five instances in an open class meet the total arm", "OWED: P1" in out)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01", "R4 a", "R6 b", "R8 c", "R9 d"], status="barriered"), "_rca": {}}), J)
    expect("a barriered class is owed from its first instance (barrier_any)", "OWED: P1" in out)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01"], rca=["Y"]), "_rca": {}}), J)
    expect("a cited rca that _rca does not index is UNKNOWN-RCA", "UNKNOWN-RCA: P1 cites Y" in out)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01", "bad"]), "_rca": {}}), J)
    expect("an instance that is not R<n> <id> is UNPARSED", "UNPARSED: P1" in out)
    twin = _settle({"P1": _entry(["R2 D1-01"], nearest_existing="P2", minted="R2"), "P3": _entry(["R2 a", "R2 b"], nearest_existing="P2", minted="R2"),
                    "P2": _entry([]), "_rca": {}})
    rc, out = run_check(twin, J)
    expect("two ids minted in one round with one nearest are counted as one: 1 + 2 meets the trigger, in each", "OWED: P1" in out and "OWED: P3" in out)
    rc, out = run_check(_settle({"P1": _entry(["R2 D1-01"], nearest_existing="P2", minted="R2"), "P3": _entry(["R2 a", "R2 b"], nearest_existing="P1", minted="R2"),
                                 "P2": _entry([]), "_rca": {}}), J)
    expect("null control: different nearest classes are separate", rc == 0)

    def run_fold(led, judge, sweep=None, rnd=2):
        with tempfile.TemporaryDirectory() as t:
            _plant(t, led, judge, sweep)
            try:
                import io
                import contextlib
                with contextlib.redirect_stdout(io.StringIO()):
                    fold(t, rnd)
                return None, json.load(open(os.path.join(t, LEDGER))), open(os.path.join(t, SCHEMA)).read(), open(os.path.join(t, LEDGER)).read()
            except SystemExit as e:
                return str(e), None, None, None
            except Exception as e:  # a crash is not a refusal: the expectation below fails on it
                return f"CRASH {e!r}", None, None, None

    base = _settle({"P1": _entry([]), "P2": _entry(["R1 D2-01"]), "_rca": {}})
    jv = {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified", "class": "P1"}, {"id": "D1-02", "verdict": "weakened", "class": "P1"},
                                  {"id": "D1-03", "verdict": "refuted", "class": "P1"}]}
    sw = {"class": "P1", "instance_list": [{"file": "a.py", "symbol": "f", "beyond_finding": True}, {"file": "b.py", "symbol": "g", "beyond_finding": False}]}
    err, led, _, raw = run_fold(base, jv, sw)
    expect("fold appends each survivor and each beyond_finding seam, and not a refuted verdict or a judged-site seam",
           err is None and led["P1"]["instances"] == ["R2 D1-01", "R2 D1-02", "R2 sw:a.py::f"] and led["P1"]["total"] == 3 and led["P1"]["per_round"] == {"R2": 3})
    expect("and recomputes the trigger it feeds: P1 now has three in round 2", led and led["P1"]["trigger"]["per_round"] is True)
    with tempfile.TemporaryDirectory() as t:
        _plant(t, base, jv, sw)
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            fold(t, 2)
            a = open(os.path.join(t, LEDGER)).read()
            fold(t, 2)
            b = open(os.path.join(t, LEDGER)).read()
    expect("folding the same round twice changes nothing (idempotent, byte for byte)", a == b)
    err, *_ = run_fold(base, {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified", "class": "P7"}]})
    expect("a survivor whose class the ledger lacks, with no nearest and differs, is refused", err and "no nearest and differs" in err)
    err, *_ = run_fold(base, {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified", "class": "P7", "class_mechanism": "m", "nearest": "P2"}]})
    expect("nearest without differs is refused", err and "no nearest and differs" in err)
    err, *_ = run_fold(base, {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified", "class": "P7", "class_mechanism": "m", "nearest": "P99", "differs": "d"}]})
    expect("a nearest the ledger does not have is refused", err and "P99" in err)
    err, *_ = run_fold(base, {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified", "class": "site-7", "class_mechanism": "m", "nearest": "P2", "differs": "d"}]})
    expect("an id that is not P<n>, I<n> or N-<name> is refused", err and "well-formed" in err)
    err, led, schema, _ = run_fold(base, {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified", "class": "P7", "class_mechanism": "m7", "nearest": "P2", "differs": "d"}]})
    expect("a new class with nearest and differs is minted, marked, and lands in the schema enum before 'new'",
           err is None and led["P7"]["nearest_existing"] == "P2" and led["P7"]["minted"] == "R2" and '"P7", "new"' in schema)
    err, *_ = run_fold(base, {"round": 2, "verdicts": [{"id": "D1-01", "verdict": "verified"}]})
    expect("a survivor with no class is refused", err and "has no class" in err)
    err, *_ = run_fold(base, jv, {"class": "P1", "instance_list": [{"file": "a.py", "symbol": "f"}]})
    expect("a sweep seam with no boolean beyond_finding is refused (the unit of count is a field, not a phrase)", err and "beyond_finding" in err)
    err, *_ = run_fold(_settle({"P1": _entry([]), "P2": _entry(["R2 D1-01"]), "_rca": {}}), jv)
    expect("a survivor already in another class is refused", err and "already in P2" in err)
    return 1 if fails else 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", nargs="?", choices=("fold", "check", "refresh"))
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument("--round", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ledger")
    ap.add_argument("--judge", action="append")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.mode == "check":
        return check(a.root, a.ledger, a.judge)
    if a.mode == "refresh":
        return refresh(a.root)
    if a.mode == "fold" and a.round:
        return fold(a.root, a.round, a.dry_run)
    ap.error("a mode (fold --round N, check or refresh) or --self-test")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
