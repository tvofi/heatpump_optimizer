#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/cross.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
"""Judge dedup measurement (judge.md: merge only where the canonical's perturbation moves the other's harness).
For every ordered pair (A, B) of wave keys on the same production line, B's probe is copied with B's one-line
mutant text replaced by A's (code lines only, never the header comments) and run; its RESULT lines are kept for
comparison with B's own run. A pair whose mutant text does not appear in B's probe is 'not expressible'."""
import json, os, re, subprocess, sys, tempfile, time, pathlib, itertools, collections, concurrent.futures as cf
REPO = "."
REF = "origin/handoff/audit-r11-verify-D3W"
WORK = pathlib.Path(os.environ.get("JUDGE_DIR", "dev/audit/rounds/round11/D3/wave-judge"))
WT = pathlib.Path.cwd()
OUT = WORK / "cross"; OUT.mkdir(exist_ok=True)
P = "dev/audit/rounds/round11/D3/s1/wave"
master = json.load(open(WORK / "master.json"))
by_site = collections.defaultdict(list)
for m in master:
    by_site[m["site"]].append(m)


def mutant(m):
    r = subprocess.run(["git", "-C", REPO, "show", f"{REF}:{P}/{m['box']}/gates/{m['key']}.json"], capture_output=True, text=True)
    return json.loads(r.stdout)["mutant"]


def strip(line):
    return line.strip()


def pair(a, b, ma, mb):
    f = OUT / f"{b['key']}__x_{a['key']}.json"
    if f.exists():
        return f.name, "cached"
    src_p = WT / b["rec"]["probe"]["path"]
    src = src_p.read_text().splitlines(keepends=True)
    nb, na = strip(mb["new"]), strip(ma["new"])
    n = 0
    out = []
    for line in src:
        if not line.lstrip().startswith("#") and nb in line:
            n += line.count(nb)
            line = line.replace(nb, na)
        out.append(line)
    rec = {"a": a["key"], "b": b["key"], "site": a["site"], "a_new": na, "b_new": nb, "replacements": n}
    if n == 0:
        rec["status"] = "not expressible"
        json.dump(rec, open(f, "w"), indent=1)
        return f.name, "nx"
    tmpf = src_p.parent / f"_judge_cross_{b['key']}__{a['key']}.py"
    tmpf.write_text("".join(out))
    tmp = tempfile.mkdtemp(prefix="d3jx-")
    env = dict(os.environ, PYTHONPATH="tests/hastub", TMPDIR=tmp + "/", HPO_PROBE_ROOT=str(WT), PROBE_ROOT=str(WT), HPO_PLANDATA=tmp + "/pd")
    rel = str(tmpf.relative_to(WT))
    runs = {}
    try:
        argsets = {"base": [rel], "mut": [rel, "--mutant"]} if "[--mutant]" in b["rec"]["probe"]["command"] else {"run": [rel]}
        for name, args in argsets.items():
            try:
                p = subprocess.run(["python3", *args], cwd=WT, env=env, capture_output=True, text=True, timeout=2400)
                runs[name] = {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr[-3000:]}
            except subprocess.TimeoutExpired:
                runs[name] = {"rc": "timeout", "stdout": "", "stderr": "TIMEOUT"}
    finally:
        tmpf.unlink(missing_ok=True)
        subprocess.run(["rm", "-rf", tmp])
    rec["runs"] = runs
    rec["status"] = "ran"
    json.dump(rec, open(f, "w"), indent=1)
    return f.name, "ran"


tasks = []
muts = {}
for site, ms in by_site.items():
    if len(ms) < 2:
        continue
    for m in ms:
        muts[m["key"]] = mutant(m)
    for a, b in itertools.permutations(ms, 2):
        tasks.append((a, b))
if os.environ.get("REVERSE"): tasks = tasks[::-1]
print("pairs", len(tasks), flush=True)
jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
with cf.ThreadPoolExecutor(jobs) as ex:
    futs = [ex.submit(pair, a, b, muts[a["key"]], muts[b["key"]]) for a, b in tasks]
    for i, fu in enumerate(cf.as_completed(futs)):
        print(i + 1, *fu.result(), flush=True)
print("DONE", flush=True)
