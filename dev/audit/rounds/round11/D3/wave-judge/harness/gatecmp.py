#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/gatecmp.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
"""Judge re-measure of each wave gate record against its box's null, from the committed gate logs:
failing-check lines (FAIL / FAILED / 'N of M ... FAILED' summaries) in the mutant gate minus the null gate's.
Metric: count of failing-check lines in the mutant log that the null log lacks (exact text; and digit-normalised)."""
import os, json, re, subprocess, pathlib, collections
REPO = "."
REF = "origin/handoff/audit-r11-verify-D3W"
WORK = pathlib.Path(os.environ.get("JUDGE_DIR", "dev/audit/rounds/round11/D3/wave-judge"))
master = json.load(open(WORK / "master.json"))
P = "dev/audit/rounds/round11/D3/s1/wave"


def show(path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{REF}:{path}"], capture_output=True, text=True, errors="replace")
    return r.stdout if r.returncode == 0 else None


FAILRE = re.compile(r"^\s*(FAIL\b.*|>>> FAILED.*|.*\b\d+ of \d+ .*FAILED.*|\d+ TEST SCRIPT\(S\) FAILED.*|Traceback.*|.*TIMEOUT.*)$")


def fails(text):
    return [l.rstrip() for l in text.splitlines() if FAILRE.match(l)]


def oks(text):
    return sum(1 for l in text.splitlines() if l.lstrip().startswith("ok "))


def norm(l):
    return re.sub(r"\d+(\.\d+)?", "#", l)


nulls = {}
out = {}
for m in master:
    box = m["box"]; k = m["key"]
    if box not in nulls:
        t = show(f"{P}/{box}/gates/null.log")
        nulls[box] = (collections.Counter(fails(t)), collections.Counter(norm(l) for l in fails(t)), oks(t)) if t else None
    t = show(f"{P}/{box}/gates/{k}.log")
    rec = json.loads(show(f"{P}/{box}/gates/{k}.json") or "{}")
    if t is None or nulls[box] is None:
        out[k] = {"box": box, "error": "log missing", "verdict": rec.get("verdict")}
        continue
    fm = collections.Counter(fails(t)); nm, nn, nok = nulls[box]
    new_exact = list((fm - nm).elements()); gone = list((nm - fm).elements())
    new_norm = list((collections.Counter(norm(l) for l in fails(t)) - nn).elements())
    summ = [l for l in fails(t) if " of " in l and "FAILED" in l]
    nsumm = [l for l in nm if " of " in l and "FAILED" in l]
    out[k] = {"box": box, "verdict": rec.get("verdict"), "fail_lines": rec.get("fail_lines"),
              "new_exact": new_exact, "new_norm": new_norm, "gone": gone, "summary": summ, "null_summary": nsumm,
              "ok_lines": oks(t), "null_ok_lines": nok, "bytes": len(t)}
json.dump(out, open(WORK / "gatecmp.json", "w"), indent=1)
c = collections.Counter()
for k, v in out.items():
    if "error" in v:
        c["error"] += 1
        continue
    c["new_norm>0" if v["new_norm"] else "no new (norm)"] += 1
    c["summary differs" if sorted(v["summary"]) != sorted(v["null_summary"]) else "summary same"] += 1
    c["ok fewer than null" if v["ok_lines"] < v["null_ok_lines"] else "ok >= null"] += 1
print(c)
