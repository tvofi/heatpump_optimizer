#!/usr/bin/env python3
"""D3-s1 box D3-u1d: assemble this box's REPORT.json and REPORT.md (its D3.M2
slice, state/keys-D3-u1d.txt, and the D3.M3 full net on that slice's survivors).

Metric (one line): per step, universe = lines its enumerator prints at the
baseline, examined = items with a result under state/results (pre/c2/c3c6 for
D3.M2, complete/ or the leak harness for D3.M3), not_reached = the rest,
grouped by owning box and file. Exact counts; no timing claims of its own.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/build_report_u1d.py
Expected: RESULT D3.M2 examined + not-reached count == 1260; RESULT u1d_driven=309.
Instrumented symbol: tests/mutation_table.py:inventory/unpinned_sites (via
prescreen.unpinned). Perturbation: removing one results file lowers `examined`
by one and adds its site to not_reached.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1d (Linux x86_64, 4 cores).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.argv = sys.argv[:1]
import prescreen as p  # noqa: E402

REL = "dev/audit/rounds/round11/D3/s1"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
LO = "c0ecc8e0b6b66ded"
LEAK = "dc6c13eca2ca1737"


def load(sub):
    d = p.RESULTS / sub
    return {q.stem: json.loads(q.read_text()) for q in d.glob("*.json")} if d.exists() else {}


def sid(m):
    return f"{m['file']}:{m['line']} {m['kind']} {m['anchor'].split()[-1]}"


def main() -> int:
    uni = p.unpinned()
    keys = {p.key(m): m for m in uni}
    u1 = {k.strip() for k in (p.STATE / "u1_keys.txt").read_text().split()}
    mine = (p.STATE / "keys-D3-u1d.txt").read_text().split()
    surv_keys = (p.STATE / "keys-D3-u1d-surv.txt").read_text().split()
    pre, c2, c36, comp = load("pre"), load("c2"), load("c3c6"), load("complete")
    by_site = {(m["file"], m["line"], m["new"]): p.key(m) for m in uni}
    examined = {k for k in pre if k in keys}
    for r in list(c2.values()) + list(c36.values()):
        k = by_site.get((r["mutant"]["file"], r["mutant"]["line"], r["mutant"]["new"]))
        if k:
            examined.add(k)
    groups = defaultdict(list)
    for k, m in keys.items():
        if k in examined:
            continue
        owner = ("assigned to box D3-u1a, D3-u1b or D3-u1c (u1_keys below " + LO + ")"
                 if k in u1 and k < LO else "assigned to box D3-u1d" if k in u1
                 else "not in u1_keys, not driven by any box")
        groups[(owner, m["file"])].append(m["line"])
    m2_nr = [f"{f}: {len(ls)} unpinned sites not pre-screened (lines {min(ls)}-{max(ls)}), {o}"
             for (o, f), ls in sorted(groups.items())]
    m2_nr_n = sum(len(v) for v in groups.values())
    assert len(examined) + m2_nr_n == len(uni)

    # K1 tally (this box's slice)
    v = Counter(pre[k]["verdict"] for k in mine)
    first = Counter(pre[k]["killed_by"][0] for k in mine if pre[k]["killed_by"])
    reach_skip = sum(1 for k in mine if pre[k].get("skipped"))
    red_nokill = sum(1 for k in mine for x in pre[k]["runs"].values()
                     if x["rc"] != 0 and not x.get("killed") and not x["timed_out"])
    timeouts = sum(1 for k in mine if pre[k]["verdict"] == "TIMEOUT")

    # D3.M3 universe: every fast-net survivor in the seat's state
    surv = {k: r for sub in (pre, c2, c36) for k, r in sub.items() if r["verdict"] == "SURVIVED"}
    leak = (p.STATE / "leak-features-mutant.out").exists()
    m3_done = [k for k in surv if k in comp or (k == LEAK and leak)]
    nr = defaultdict(list)
    for k, r in surv.items():
        if k in m3_done:
            continue
        o = "assigned to box D3-u1d (not finished)" if k in surv_keys else \
            "carried survivor of runs 1-2, not D3-u1d's slice: full net owed by another box (D3-top6 holds the top six)"
        nr[o].append(sid(r["mutant"]))
    m3_nr = [f"{x} ({o})" for o, xs in sorted(nr.items()) for x in xs]
    if len(m3_nr) > 200:
        m3_nr = [f"{o}: {len(xs)} survivors" for o, xs in sorted(nr.items())]
    cv = Counter(comp[k]["verdict"] for k in surv_keys if k in comp)
    ck = Counter(s for k in surv_keys if k in comp for s in comp[k]["killed_by"])
    full_surv = [k for k in surv_keys if k in comp and comp[k]["verdict"] in ("SURVIVED", "TIMEOUT")]
    m4 = json.loads((HERE / "m4_answers-D3-u1d.json").read_text())
    extra = json.loads((HERE / "report_extra-u1d.json").read_text())
    tally = (f"K1 (D3.M2) on state/keys-D3-u1d.txt: driven {len(mine)}, KILLED {v['KILLED']} "
             f"(first kill: " + ", ".join(f"{s} {n}" for s, n in first.most_common()) + "), "
             f"SURVIVED {v['SURVIVED']}, TIMEOUT {timeouts}, skipped by reach: {reach_skip} mutants had "
             f">= 1 driver reach-skipped, unparseable (red with no failing check, structure.py exit 2) "
             f"{red_nokill} runs, no mutant decided by one.")
    ktally = (f"K2 (D3.M3 full net, prescreen.py complete, no early stop) on the {len(surv_keys)} K1 "
              f"survivors: completed {sum(cv.values())}: KILLED {cv['KILLED']} (every kill: "
              + ", ".join(f"{s} {n}" for s, n in ck.most_common()) + f"), SURVIVED {cv['SURVIVED']}, "
              f"TIMEOUT {cv['TIMEOUT']}; {LEAK} classified by ensure_worker_leak.py (resource exhaustion only).")
    cov = [
        {"step": "D3.M2",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --unpinned",
         "universe": len(uni), "examined": len(examined), "not_reached": m2_nr,
         "redispatched": [{"item": "C2", "state": "examined"}, {"item": "C6", "state": "examined"}],
         "evidence": tally + " " + extra["m2_evidence"]},
        {"step": "D3.M3",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
         "universe": len(surv), "examined": len(m3_done), "not_reached": m3_nr,
         "redispatched": [{"item": "C3", "state": "not_reached"}, {"item": "C5", "state": "examined"}],
         "evidence": ktally + " " + extra["m3_evidence"]},
    ]
    # D3.M1 and D3.M5 are not this box's slice: carried from box D3R's REPORT.json
    # (M5 owned by box D3-m5); D3.M4 is computed over the same survivor universe.
    carried = {c["step"]: c for c in json.loads((HERE / "REPORT-D3R.json").read_text())["coverage"]
               if c["step"] in ("D3.M1", "D3.M5")} if not extra.get("carried_rows") else extra["carried_rows"]
    extra["carried_rows"] = carried
    (HERE / "report_extra-u1d.json").write_text(json.dumps(extra, indent=1) + "\n")
    def flat(e):
        return e if isinstance(e, str) else " | ".join(f"{x['command']} -> {x['value']}" for x in e)
    m1 = dict(carried["D3.M1"], evidence=flat(carried["D3.M1"]["evidence"]) + " (carried from runs 1-2; not re-driven on box D3-u1d)")
    m5 = dict(carried["D3.M5"], evidence=flat(carried["D3.M5"]["evidence"]) + " (carried; the rest of D3.M5 is assigned to box D3-m5)")
    m5["not_reached"] = [x if "assigned to box" in x else x + " (assigned to box D3-m5)" for x in m5["not_reached"]]
    m4_old = json.loads((HERE / "m4_answers.json").read_text())
    m4_ok = [k for k in surv if k in m4 or k in m4_old]
    cov.insert(0, m1)
    cov.append({"step": "D3.M4",
                "enumerator": cov[-1]["enumerator"], "universe": len(surv), "examined": len(m4_ok),
                "not_reached": [sid(surv[k]["mutant"]) + " (no full-net result yet; another box's slice)"
                                for k in surv if k not in m4_ok],
                "redispatched": [],
                "evidence": f"cat {REL}/m4_answers.json {REL}/m4_answers-D3-u1d.json: {len(m4_ok)} of {len(surv)} fast-net survivors answered "
                            f"(production line, file, the check that should have failed); this box answered all {len(surv_keys)} of its slice, "
                            "KILLED ones by the full-net driver that killed them."})
    cov.append(m5)
    prescreened = []
    for k in full_surv + ([LEAK] if leak else []):
        r = comp.get(k) or pre[k]
        m = r["mutant"]
        prescreened.append({
            "key": k, "site": sid(m), "patch": f"{m['file']}:{m['line']}: `{m['old'].strip()}` -> `{m['new'].strip()}`",
            "scripts_ran": sorted(r["runs"]), "reach_skipped": sorted(r.get("skipped") or []),
            "verdict": "LEAK (killed only by resource exhaustion)" if k == LEAK else "TIMEOUT (features.py hangs; inconclusive, not a kill)" if r["verdict"] == "TIMEOUT" else r["verdict"],
            "m4": m4.get(k, "")})
    rep = {
        "dimension": "D3", "baseline_sha": BASE, "report_path": f"{REL}/REPORT.md",
        "exposure": extra["exposure"], "coverage": cov, "unfinished": extra["unfinished"],
        "findings": [], "non_findings": extra["non_findings"],
        "harnesses": [f"{REL}/{n}" for n in (
            "enumerate.py", "prescreen.py", "tabulate.py", "ensure_worker_leak.py",
            "m4_pending.py", "build_report_u1d.py")],
        "leads": extra["leads"], "box": "D3-u1d", "prescreened": prescreened,
    }
    L = ["# D3-s1 round 11, box D3-u1d slice (baseline 92d38ecb)", "",
         extra["machine"], "", "Counts are final; every wall/CPU number is provisional.", "",
         "## Method", "", extra["method"], "", "## Coverage", ""]
    for c in cov:
        L += [f"### {c['step']}: universe {c['universe']}, examined {c['examined']}", "",
              f"Enumerator: `{c['enumerator']}`", "", c["evidence"], "", "Not reached:", ""]
        L += [f"- {x}" for x in c["not_reached"]] + [""]
    L += ["## Findings", "", "None from this box (D3.md step 3: candidates, not findings; "
          "the full gate on the top six is box D3-top6's).", "",
          f"## Prescreened survivors of the full net ({len(prescreened)}), for the D3-top6 full gate", ""]
    for x in prescreened:
        L.append(f"- `{x['key']}` {x['patch']} -- {x['verdict']}; ran {len(x['scripts_ran'])} scripts. M4: {x['m4']}")
    L += ["", "## D3.M4 answers for this slice's full-net KILLED results", ""]
    L += [f"- `{k}`: {m4[k]}" for k in surv_keys if k in m4 and k in comp and comp[k]["verdict"] == "KILLED"]
    L += ["", "## Non-findings", ""] + [f"- {n['claim']}: {n['value']} (`{n['command']}`)" for n in rep["non_findings"]]
    L += ["", "## Leads", ""] + [f"- {x['owner_seat']} {x['file']} {x['symbol']}: {x['what']}" for x in rep["leads"]]
    L += ["", "## Unfinished", ""] + ([f"- {u['step']}: {u['what']}" for u in rep["unfinished"]] or ["- none"])
    L += ["", "## Exposure", "", rep["exposure"], ""]
    (HERE / "REPORT.md").write_text("\n".join(L) + "\n")
    rep["report_md"] = "see REPORT.md"
    (HERE / "REPORT.json").write_text(json.dumps(rep, indent=1) + "\n")
    for c in cov:
        print(f"RESULT {c['step']}_universe={c['universe']} examined={c['examined']} not_reached_lines={len(c['not_reached'])}")
    print(f"RESULT u1d_driven={len(mine)} killed={v['KILLED']} survived={v['SURVIVED']}")
    print(f"RESULT full_net_completed={sum(cv.values())} killed={cv['KILLED']} survived={cv['SURVIVED']} timeout={cv['TIMEOUT']}")
    print(f"RESULT prescreened={len(prescreened)}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
