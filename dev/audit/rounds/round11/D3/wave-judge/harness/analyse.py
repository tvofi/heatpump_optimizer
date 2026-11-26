#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/analyse.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
"""Judge reading of the probe re-runs.
Per key: rc; my RESULT lines (volatile names dropped) against the verifier's recorded run (out/v1, out/v1m);
arm pairs (X_baseline / X_mutant, `X baseline=.. mutant=..`) that move, null pairs that move; the finder's stated
baseline/mutant values found in my output. Metric: moved non-null arm pairs in my re-run, with the null pairs held."""
import os, json, re, sys, pathlib, collections
WORK = pathlib.Path(os.environ.get("JUDGE_DIR", "dev/audit/rounds/round11/D3/wave-judge"))
WT = pathlib.Path.cwd()
VW = WT / "dev/audit/rounds/round11/D3/wave-verify"
sys.path.insert(0, str(VW / "harness"))
import v1_analyse as va  # the verifier's arm parser, reused as an instrument (overlay: read-only import)

VOL = re.compile(r"^(thread_factor|load1|swapins|wall|elapsed|rss|time\b|t_)|cpu", re.I)
master = json.load(open(WORK / "master.json"))


def res(stdout):
    return [l[7:].strip() for l in stdout.splitlines() if l.startswith("RESULT ") and not VOL.search(l[7:].strip().split("=")[0])]


def kv(lines):
    d = {}
    for l in lines:
        m = re.match(r"^(\S+?)\s*=\s*(.*)$", l)
        if m:
            d[m.group(1)] = m.group(2).strip()
    return d


rows = {}
for m in master:
    k = m["key"]; f = WORK / "rerun" / f"{k}.json"
    if not f.exists():
        continue
    r = json.load(open(f))
    row = {"key": k, "box": m["box"]}
    if "run" in r:
        row["rc"] = r["run"]["rc"]
        mine = res(r["run"]["stdout"])
        arms = va.arm_pairs(mine)
        row["stderr_tail"] = r["run"]["stderr"][-400:] if r["run"]["rc"] != 0 else ""
        vf = VW / "out/v1" / f"{k}.json"
        theirs = res(json.load(open(vf))["stdout"]) if vf.exists() else None
    else:
        row["rc"] = [r["base"]["rc"], r["mut"]["rc"]]
        b, mu = kv(res(r["base"]["stdout"])), kv(res(r["mut"]["stdout"]))
        arms = {n: [b.get(n), mu.get(n)] for n in sorted(set(b) | set(mu))}
        mine = res(r["base"]["stdout"]) + ["--mutant"] + res(r["mut"]["stdout"])
        row["stderr_tail"] = (r["base"]["stderr"] + r["mut"]["stderr"])[-400:]
        vf, vfm = VW / "out/v1" / f"{k}.json", VW / "out/v1m" / f"{k}.json"
        theirs = (res(json.load(open(vf))["stdout"]) + ["--mutant"] + res(json.load(open(vfm))["stdout"])) if vf.exists() and vfm.exists() else None
    moved = {n: v for n, v in arms.items() if "null" not in n.lower() and v[0] is not None and v[1] is not None and not va.same(v[0], v[1])}
    nulls = {n: v for n, v in arms.items() if "null" in n.lower() and v[0] is not None and v[1] is not None}
    null_moved = {n: v for n, v in nulls.items() if not va.same(v[0], v[1])}
    moved_lines = [l for l in mine if re.search(r"(^|_)(moved|differ\w*|changed|diff\w*)\w*=\s*[1-9]", l) and "null" not in l.lower()]
    null_lines = [l for l in mine if l.lower().startswith("null") or "_null" in l.lower().split("=")[0]]
    allout = json.dumps(r)
    tf = re.findall(r"thread_factor=([0-9.]+)", allout)
    row.update({
        "load1": round((r.get("run") or r.get("mut"))["load1"], 1), "thread_factor": max(map(float, tf)) if tf else None,
        "n_result": len(mine), "same_as_verifier": (theirs is not None and sorted(mine) == sorted(theirs)),
        "verifier_diff": None if theirs is None else [sorted(set(mine) - set(theirs))[:4], sorted(set(theirs) - set(mine))[:4]],
        "moved_pairs": len(moved), "moved_example": next(iter(moved.items()), None), "moved_lines": moved_lines[:3],
        "null_pairs": len(nulls), "null_moved": len(null_moved), "null_moved_example": next(iter(null_moved.items()), None),
        "null_lines": null_lines[:4], "head": mine[:10],
    })
    rows[k] = row
json.dump(rows, open(WORK / "analysis.json", "w"), indent=1)
c = collections.Counter()
for r in rows.values():
    c[(("rc0" if r["rc"] in (0, [0, 0]) else "rcX"), "same" if r["same_as_verifier"] else "diff",
       "moved" if (r["moved_pairs"] or r["moved_lines"]) else "NOMOVE", "nullmoved" if r["null_moved"] else "nullok")] += 1
print(len(rows))
for k, v in c.most_common():
    print(v, k)
