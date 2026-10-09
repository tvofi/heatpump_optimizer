"""Three-stage per-key audit of tests/closures.json for the resolution merge.

stages: BASE = merge-base(d916687db, c518447eb); OURS = d916687db (the reviewed
head); THEIRS = c518447eb (main); MERGED = bab0aeb8d (the pushed head).
For every list-valued key, MERGED must contain OURS union THEIRS (nothing
dropped) and must not invent entries absent from both sides.
"""
import json
import subprocess
import sys

REPO = "/Users/timmalmstrom/hpo-seats/review-2024/wt3"
PATH = "tests/closures.json"


def blob(rev):
    out = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{PATH}"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


base = subprocess.run(["git", "-C", REPO, "merge-base", "d916687db", "c518447eb"],
                      capture_output=True, text=True, check=True).stdout.strip()
print(f"merge-base: {base}")
B, O, T, M = blob(base), blob("d916687db"), blob("c518447eb"), blob("bab0aeb8d")

keys = sorted(set(B) | set(O) | set(T) | set(M))
print(f"top-level keys: base={len(B)} ours={len(O)} theirs={len(T)} merged={len(M)}")

problems = []
listed_both = []
for k in keys:
    b, o, t, m = B.get(k), O.get(k), T.get(k), M.get(k)
    if isinstance(o, dict) and isinstance(t, dict) and isinstance(m, dict):
        # closures: {script: [files]}
        sub = sorted(set(b or {}) | set(o) | set(t) | set(m))
        for s in sub:
            bs, os_, ts, ms = (b or {}).get(s), o.get(s), t.get(s), m.get(s)
            if ms is None:
                problems.append(f"KEY {k}/{s}: merged has no entry (ours={os_ is not None}, theirs={ts is not None})")
                continue
            if isinstance(ms, list):
                want = set(os_ or []) | set(ts or [])
                got = set(ms)
                dropped = want - got
                invented = got - want - set(bs or [])
                if dropped:
                    problems.append(f"KEY {k}/{s}: DROPPED {sorted(dropped)}")
                if invented:
                    problems.append(f"KEY {k}/{s}: INVENTED {sorted(invented)}")
                if os_ is not None and ts is not None and os_ != ts and ms != sorted(want) and ms != want and list(ms) != sorted(want):
                    pass
    elif isinstance(o, list) or isinstance(t, list) or isinstance(m, list):
        want = set(o or []) | set(t or [])
        got = set(m or [])
        dropped = want - got
        if dropped:
            problems.append(f"KEY {k}: DROPPED {sorted(dropped)}")
        invented = got - want - set(B.get(k) or [])
        if invented:
            problems.append(f"KEY {k}: INVENTED {sorted(invented)}")
    else:
        # scalar / recorded timing etc: report changed values only
        if m != o and m != t and o != t:
            if isinstance(o, dict) or isinstance(t, dict) or isinstance(m, dict):
                problems.append(f"KEY {k}: dict-shaped, unhandled branch")
            else:
                print(f"scalar {k}: base={b} ours={o} theirs={t} merged={m}")

print("--- problems ---")
for p in problems:
    print(p)
print(f"PROBLEM_COUNT={len(problems)}")

# targeted presence checks
for script_key in ("closures", "inert_reads"):
    d = M.get(script_key, {})
    fm = [s for s, v in d.items() if isinstance(v, list) and any("flow_meter" in x for x in v)]
    ec = [s for s, v in d.items() if isinstance(v, list) and any("entry_config" in x for x in v)]
    ofm = [s for s, v in O.get(script_key, {}).items() if isinstance(v, list) and any("flow_meter" in x for x in v)]
    oec = [s for s, v in T.get(script_key, {}).items() if isinstance(v, list) and any("entry_config" in x for x in v)]
    print(f"{script_key}: merged flow_meter in {len(fm)} scripts, entry_config in {len(ec)}; "
          f"ours flow_meter in {len(ofm)}, theirs entry_config in {len(oec)}")
    print(f"   missing-from-merged: flow_meter {sorted(set(ofm) - set(fm))} entry_config {sorted(set(oec) - set(ec))}")
    print(f"   extra-in-merged: flow_meter {sorted(set(fm) - set(ofm) - set(s for s, v in B.get(script_key, {}).items() if isinstance(v, list) and any('flow_meter' in x for x in v)))} "
          f"entry_config {sorted(set(ec) - set(oec) - set(s for s, v in B.get(script_key, {}).items() if isinstance(v, list) and any('entry_config' in x for x in v)))}")

# entry counts per side for the two new modules anywhere
for mod in ("flow_meter.py", "entry_config.py"):
    for name, D in (("ours(d916687db)", O), ("theirs(main)", T), ("merged", M)):
        hits = []
        for k, v in D.items():
            if isinstance(v, dict):
                for s, lst in v.items():
                    if isinstance(lst, list) and any(mod in x for x in lst):
                        hits.append(f"{k}.{s}")
        print(f"{mod} in {name}: {len(hits)} lists")
