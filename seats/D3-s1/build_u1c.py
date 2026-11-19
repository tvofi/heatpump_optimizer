#!/usr/bin/env python3
"""D3-s1 box D3-u1c: assemble this box's REPORT.json and REPORT.md from state/.

Metric (one line): D3.M2 row = unpinned cell sites (enumerate.py --unpinned)
with a fast-net verdict in state/results/{pre,c2,c3c6}; D3.M3 row = fast-net
survivors with a full-net verdict in state/results/complete; the slice's
prescreened list = the full-net verdict of every survivor of
state/keys-D3-u1c.txt, with D3.md step 4's answer (production line, file, and
the closure drivers whose traced unmutated run executes it).
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/build_u1c.py
Expected: examined + not_reached closes on each row; counts exact.
Instrumented symbol: tests/mutation_table.py:inventory/unpinned_sites,
killed and reach_skip, via prescreen.py and slice_u1c.py.
Perturbation: deleting one results/complete/<key>.json lowers the D3.M3
row's examined by one and names that survivor under not_reached.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1c,
Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.argv = sys.argv[:1]
import prescreen as p  # noqa: E402

REL = "dev/audit/rounds/round11/D3/s1"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
LO, HI = "8206a42b98c8dd86", "c0ecc8e0b6b66ded"
ROOT = HERE.parents[5]


def load(sub):
    d = p.RESULTS / sub
    return {q.stem: json.loads(q.read_text()) for q in d.glob("*.json")} if d.exists() else {}


def site_id(m):
    return f"{m['file']}:{m['line']} {m['kind']} {m['anchor'].split()[-1]}"


def run(*a):
    env = {**os.environ, "PYTHONPATH": "tests/hastub"}
    return subprocess.run([sys.executable, *a], cwd=ROOT, env=env,
                          capture_output=True, text=True, check=True).stdout


def main() -> int:
    uni = p.unpinned()
    keys = {p.key(m): m for m in uni}
    pre, c2, c36, comp = load("pre"), load("c2"), load("c3c6"), load("complete")
    mine = [k.strip() for k in (p.STATE / "keys-D3-u1c.txt").read_text().split() if k.strip()]
    by_site = {(m["file"], m["line"], m["new"]): p.key(m) for m in uni}
    examined = {k for k in pre if k in keys}
    for r in list(c2.values()) + list(c36.values()):
        k = by_site.get((r["mutant"]["file"], r["mutant"]["line"], r["mutant"]["new"]))
        if k:
            examined.add(k)
    # D3.M2 not_reached: grouped by file and by owner (this box drove all of its range)
    grp = defaultdict(list)
    for k, m in keys.items():
        if k in examined:
            continue
        own = ("this box's range, NOT DRIVEN" if LO <= k < HI else
               f"assigned to box D3-u1a, D3-u1b or D3-u1d (key outside [{LO}, {HI}))")
        grp[(m["file"], own)].append(m["line"])
    m2_nr = [f"{f}: {len(ls)} unpinned sites not pre-screened here (lines {min(ls)}-{max(ls)}); {own}"
             for (f, own), ls in sorted(grp.items())]
    surv = {k: r for sub in (pre, c2, c36) for k, r in sub.items() if r["verdict"] == "SURVIVED"}
    m3_done = [k for k in surv if k in comp]
    m3_nr = [site_id(surv[k]["mutant"]) + (
        "; this box's slice, NOT DRIVEN" if k in mine else
        "; carried survivor outside D3-u1c's slice, assigned to another box of the split")
        for k in surv if k not in comp]
    slice_tab = run(f"{REL}/slice_u1c.py")
    tsv = run(f"{REL}/slice_u1c.py", "--tsv").splitlines()
    tsv = [ln for ln in tsv if not ln.startswith("RESULT")]
    base = p.load_base()
    prescreened = []
    for k in mine:
        if k not in pre or pre[k]["verdict"] != "SURVIVED":
            continue
        r = comp.get(k, pre[k])
        m = r["mutant"]
        ds = [s for s in base if m["file"] in p.mt.load_closures().get(s, ())]
        cls = {s: p.classify(base, s, m) for s in ds}
        prescreened.append({
            "key": k, "file": m["file"], "line": m["line"], "kind": m["kind"],
            "anchor": m["anchor"], "patch": {"old": m["old"], "new": m["new"]},
            "closure": sorted(ds),
            "fast_net_ran": sorted(pre[k]["runs"]),
            "full_net_ran": sorted(r["runs"]) if k in comp else None,
            "skipped_by_reach": sorted(set(r["skipped"])),
            "verdict": ("full:" + r["verdict"]) if k in comp else "fast:SURVIVED (full net not run)",
            "killed_by": r["killed_by"],
            "m4_production_line": f"{m['file']}:{m['line']}: {m['old'].strip()}",
            "m4_should_have_failed": sorted(s for s, v in cls.items() if v == "exec"),
        })
    full_surv = [x for x in prescreened if x["verdict"] == "full:SURVIVED"]
    extra = json.loads((HERE / "u1c_extra.json").read_text())
    cov = [
        {"step": "D3.M2",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --unpinned",
         "universe": len(uni), "examined": len(examined), "not_reached": m2_nr,
         "redispatched": [{"item": "C2", "state": "examined"}, {"item": "C6", "state": "examined"}],
         "evidence": extra["m2_evidence"] + " Slice tally: " + " ".join(
             ln.split(" ", 1)[1] for ln in slice_tab.splitlines() if ln.startswith("RESULT"))},
        {"step": "D3.M3",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
         "universe": len(surv), "examined": len(m3_done), "not_reached": m3_nr,
         "redispatched": [{"item": "C3", "state": "not_reached"}, {"item": "C5", "state": "examined"}],
         "evidence": extra["m3_evidence"]},
    ]
    d3r = {c["step"]: c for c in json.loads((HERE / "REPORT-D3R.json").read_text())["coverage"]}
    def ev(c):
        e = c["evidence"]
        return e if isinstance(e, str) else " | ".join(f"{x['command']} -> {x['value']}" for x in e)
    m1 = dict(d3r["D3.M1"], evidence="carried from box D3R (REPORT-D3R.json), not re-run here: " + ev(d3r["D3.M1"]))
    m4_done = set(extra["m4_answered_carried"]) | {x["key"] for x in prescreened}
    m4 = {"step": "D3.M4", "enumerator": cov[1]["enumerator"], "universe": len(surv),
          "examined": len([k for k in surv if k in m4_done]),
          "not_reached": [site_id(surv[k]["mutant"]) for k in surv if k not in m4_done],
          "redispatched": [], "evidence": extra["m4_evidence"]}
    m5c = d3r["D3.M5"]
    m5 = dict(m5c, not_reached=[f"{s} (assigned to box D3-m5)" for s in m5c["not_reached"]],
              evidence="carried from box D3R (REPORT-D3R.json); the M5 remainder (C4, C7, C9 and the four "
              "unmeasured scripts) is assigned to box D3-m5, not driven here: " + ev(m5c))
    cov = [m1, cov[0], cov[1], m4, m5]
    for row in cov:
        n = len(row["not_reached"])
        if row["step"] == "D3.M2":
            n = sum(len(v) for v in grp.values())
        assert row["examined"] + n == row["universe"], row["step"]
    rep = {
        "dimension": "D3", "baseline_sha": BASE, "report_path": f"{REL}/REPORT.md",
        "exposure": extra["exposure"], "coverage": cov,
        "unfinished": extra["unfinished"], "findings": [],
        "non_findings": extra["non_findings"],
        "harnesses": [f"{REL}/{n}" for n in ("enumerate.py", "prescreen.py", "tabulate.py",
                                               "slice_u1c.py", "build_u1c.py")],
        "leads": [],
        "prescreened": full_surv,
    }
    (HERE / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
    L = ["# D3-s1 round 11, box D3-u1c slice (baseline 92d38ecb)", "", extra["md_intro"], "",
         "## Coverage", ""]
    for c in cov:
        L.append(f"- {c['step']}: universe {c['universe']}, examined {c['examined']}; enumerator `{c['enumerator']}`")
        L += [f"  - not reached: {x}" for x in c["not_reached"]]
    L += ["", "## Slice tally (slice_u1c.py)", "", "```", slice_tab.strip(), "```", "",
          "## Full-net survivors (finding candidates for the D3-top6 full gate)", "",
          "key | file:line | symbol | kind | old -> new | verdict | drivers executing the line (should have failed)",
          "---|---|---|---|---|---|---"]
    L += [" | ".join(ln.split("\t")[:4] + [f"`{ln.split(chr(9))[4]}` -> `{ln.split(chr(9))[5]}`"]
                     + ln.split("\t")[6:]) for ln in tsv if "\tfull:SURVIVED\t" in ln]
    L += ["", "## Findings", "", "None from this slice: survivors are candidates (D3.md step 3); "
          "only the D3-top6 full gate turns them into findings.", "", "## Non-findings", ""]
    L += [f"- {n['claim']}: `{n['command']}` -> {n['value']}" for n in extra["non_findings"]]
    L += ["", "## Harnesses", ""] + [f"- {h}" for h in rep["harnesses"]]
    L += ["", "## Unfinished", ""] + ([f"- {u['step']}: {u['what']}" for u in extra["unfinished"]] or ["- none"])
    L += ["", "## Exposure", "", extra["exposure"], ""]
    (HERE / "REPORT.md").write_text("\n".join(L))
    for row in cov:
        print(f"RESULT {row['step']}_universe={row['universe']} examined={row['examined']} not_reached_lines={len(row['not_reached'])}")
    print(f"RESULT slice_prescreened={len(prescreened)} full_net_survivors={len(full_surv)}")
    print(f"RESULT kinds={dict(Counter(x['kind'] for x in full_surv))}")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
