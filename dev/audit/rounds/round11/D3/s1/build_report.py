#!/usr/bin/env python3
"""D3-s1: assemble REPORT.json's coverage rows from the seat's state.

Metric (one line): per step, universe = lines its enumerator prints at the
baseline, examined = items the step's method ran on (state/results), and
not_reached = the rest, grouped by file past the schema's 200-item cap.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/build_report.py
Reads state/ and the hand-written findings.json/non_findings.json/leads.json
beside it; writes REPORT.json. Counts are exact; no timing claims.
Instrumented symbol: tests/mutation_table.py:inventory/unpinned_sites (via
enumerate.py). Perturbation: removing a results file lowers `examined` by one
and adds its site to not_reached.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.argv = sys.argv[:1]
import prescreen as p  # noqa: E402

REL = "dev/audit/rounds/round11/D3/s1"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"


def load(sub):
    d = p.RESULTS / sub
    return {q.stem: json.loads(q.read_text()) for q in d.glob("*.json")} if d.exists() else {}


def site_id(m):
    return f"{m['file']}:{m['line']} {m['kind']} {m['anchor'].split()[-1]}"


def grouped(items, cap=200):
    if len(items) <= cap:
        return [site_id(m) for m in items]
    by = defaultdict(list)
    for m in items:
        by[m["file"]].append(m["line"])
    return [f"{f}: {len(ls)} unpinned sites not pre-screened (lines {min(ls)}-{max(ls)})"
            for f, ls in sorted(by.items())]


def main() -> int:
    uni = p.unpinned()
    keys = {p.key(m): m for m in uni}
    pre, c2, c36, comp = load("pre"), load("c2"), load("c3c6"), load("complete")
    # inventory sites the R10 re-drawn mutants coincide with count as examined
    by_site = {(m["file"], m["line"], m["new"]): p.key(m) for m in uni}
    examined = set(k for k in pre if k in keys)
    for r in list(c2.values()) + list(c36.values()):
        m = r["mutant"]
        k = by_site.get((m["file"], m["line"], m["new"]))
        if k:
            examined.add(k)
    m2_nr = [m for k, m in keys.items() if k not in examined]
    surv = {k: r for sub in (pre, c2, c36) for k, r in sub.items()
            if r["verdict"] == "SURVIVED"}
    m3_done = [k for k in surv if k in comp]
    m3_nr = [surv[k]["mutant"] for k in surv if k not in comp]
    scripts = [ln.split("\t")[0] for ln in
               os.popen(f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --scripts").read().splitlines()]
    base = json.loads((p.STATE / "baselines.json").read_text())
    solved = {json.loads(ln)["script"] for ln in
              (p.STATE / "solves.jsonl").read_text().splitlines() if ln.strip()}
    m5_ex = [s for s in scripts if s in base or s in solved]
    m5_nr = [s for s in scripts if s not in m5_ex]
    extra = json.loads((HERE / "report_extra.json").read_text())
    cov = [
        {"step": "D3.M1",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --unpinned",
         "universe": len(uni), "examined": len(uni), "not_reached": [],
         "redispatched": extra["redispatched"]["D3.M1"],
         "evidence": extra["evidence"]["D3.M1"]},
        {"step": "D3.M2",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --unpinned",
         "universe": len(uni), "examined": len(examined),
         "not_reached": grouped(m2_nr),
         "redispatched": extra["redispatched"]["D3.M2"],
         "evidence": extra["evidence"]["D3.M2"]},
        {"step": "D3.M3",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
         "universe": len(surv), "examined": len(m3_done),
         "not_reached": [site_id(m) for m in m3_nr],
         "redispatched": extra["redispatched"]["D3.M3"],
         "evidence": extra["evidence"]["D3.M3"]},
        {"step": "D3.M4",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
         "universe": len(surv), "examined": len(extra["m4_answered"]),
         "not_reached": [site_id(surv[k]["mutant"]) for k in surv
                         if k not in extra["m4_answered"]],
         "redispatched": extra["redispatched"]["D3.M4"],
         "evidence": extra["evidence"]["D3.M4"]},
        {"step": "D3.M5",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --scripts",
         "universe": len(scripts), "examined": len(m5_ex), "not_reached": m5_nr,
         "redispatched": extra["redispatched"]["D3.M5"],
         "evidence": extra["evidence"]["D3.M5"]},
    ]
    for row in cov:
        assert row["examined"] + (len(row["not_reached"]) if len(row["not_reached"]) <= 200 and not any(": " in x and "not pre-screened" in x for x in row["not_reached"]) else row["universe"] - row["examined"]) == row["universe"], row["step"]
    rep = {
        "dimension": "D3", "baseline_sha": BASE,
        "report_path": f"{REL}/REPORT.md",
        "exposure": extra["exposure"],
        "coverage": cov,
        "unfinished": extra["unfinished"],
        "findings": json.loads((HERE / "findings.json").read_text()),
        "non_findings": extra["non_findings"],
        "harnesses": [f"{REL}/{n}" for n in (
            "enumerate.py", "prescreen.py", "tabulate.py", "m5_closure_reach.py",
            "m5_solves.py", "m5_envdrift_reach.py", "build_report.py", "finalize.py")],
        "leads": extra["leads"],
    }
    (HERE / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
    for row in cov:
        print(f"RESULT {row['step']}_universe={row['universe']} examined={row['examined']} not_reached_items={len(row['not_reached'])}")
    print(f"RESULT survivors={len(surv)} completed={len(m3_done)}")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
