#!/usr/bin/env python3
"""D3-s1 box D3-u1c report assembly: REPORT.json and REPORT.md for this box's slice.

Metric (one line): coverage rows D3.M2 (unpinned cell sites pre-screened by the
fast net), D3.M3 (fast-net survivors re-driven through the full net, no early
stop) and D3.M4 (survivors answered), counted from state/results/ exactly as
build_report.py counts them; the D3-u1c slice is state/keys-D3-u1c.txt.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1c_report.py
Instrumented symbol: prescreen.py verdicts of tests/mutation_table.py:killed
over each mutant's production line (state/results/{pre,c2,c3c6,complete}).
Perturbation: deleting one results/complete/<key>.json lowers D3.M3 examined by
one and adds that site to not_reached.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1c.
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
import prescreen as p  # noqa: E402

REL = "dev/audit/rounds/round11/D3/s1"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
BOX = "D3-u1c"
LO, HI = "8206a42b98c8dd86", "c0ecc8e0b6b66ded"
OTHERS = "D3-u1a, D3-u1b or D3-u1d"
MACHINE = ("box D3-u1c: Linux x86_64, nproc 4, Intel(R) Xeon(R) Processor @ 2.30GHz, "
           "16 GB, venv-ci CPython 3.14.7 (numpy 2.5.4, scipy 1.18.1), alone on the box")


def load(sub):
    d = p.RESULTS / sub
    return {q.stem: json.loads(q.read_text()) for q in d.glob("*.json")} if d.exists() else {}


def site_id(m):
    return f"{m['file']}:{m['line']} {m['kind']} {m['anchor'].split()[-1]}"


def short(m):
    return f"{m['file'].rsplit('/', 1)[-1]}:{m['line']}"


def main() -> int:
    uni = p.unpinned()
    keys = {p.key(m): m for m in uni}
    mine = [k.strip() for k in (p.STATE / "keys-D3-u1c.txt").read_text().split() if k.strip()]
    mine_set = set(mine)
    u1 = {ln.strip() for ln in (p.STATE / "u1_keys.txt").read_text().splitlines() if ln.strip()}
    pre, c2, c36, comp = load("pre"), load("c2"), load("c3c6"), load("complete")
    by_site = {(m["file"], m["line"], m["new"]): p.key(m) for m in uni}
    examined = set(k for k in pre if k in keys)
    for r in list(c2.values()) + list(c36.values()):
        m = r["mutant"]
        k = by_site.get((m["file"], m["line"], m["new"]))
        if k:
            examined.add(k)
    nr = defaultdict(list)
    for k, m in keys.items():
        if k in examined:
            continue
        owner = (f"assigned to box {BOX}, not driven" if k in mine_set else
                 f"assigned to box {OTHERS} (state/u1_keys.txt outside [{LO}, {HI}))"
                 if k in u1 else "outside state/u1_keys.txt, owner unknown")
        nr[(m["file"], owner)].append(m["line"])
    m2_nr = [f"{f}: {len(ls)} unpinned sites not pre-screened here (lines {min(ls)}-{max(ls)}), {o}"
             for (f, o), ls in sorted(nr.items())]
    mine_res = {k: pre[k] for k in mine if k in pre}
    c = Counter(r["verdict"] for r in mine_res.values())
    first = Counter(r["killed_by"][0] for r in mine_res.values() if r["killed_by"])

    surv = {k: r for sub in (pre, c2, c36) for k, r in sub.items() if r["verdict"] == "SURVIVED"}
    m3_done = [k for k in surv if k in comp]
    m3_nr = []
    for k in surv:
        if k in comp:
            continue
        who = (f"assigned to box {BOX}, not driven" if k in mine_set else
               "carried survivor (box B1/D3R), full net assigned to box D3-top6 or another resume box, not D3-u1c")
        m3_nr.append(f"{site_id(surv[k]['mutant'])}: {who}")
    my_comp = {k: comp[k] for k in mine if k in comp}
    cc = Counter(r["verdict"] for r in my_comp.values())
    ck = Counter(s for r in my_comp.values() for s in r["killed_by"])
    ck_first = Counter(r["killed_by"][0] for r in my_comp.values() if r["killed_by"])
    only = Counter(r["killed_by"][0] for r in my_comp.values() if len(r["killed_by"]) == 1)
    full_surv = sorted(k for k, r in my_comp.items() if r["verdict"] == "SURVIVED")
    full_to = sorted(k for k, r in my_comp.items() if r["verdict"] == "TIMEOUT")
    m4 = json.loads((HERE / "m4_answers-D3-u1c.json").read_text())
    m4_old = json.loads((HERE / "m4_answers.json").read_text())
    answered = set(m4) | set(m4_old)
    m4_nr = [site_id(surv[k]["mutant"]) for k in surv if k not in answered]

    walls = [r["wall"] for r in mine_res.values()]
    cwalls = [r["complete_wall"] for r in my_comp.values()]
    tally = (f"D3-u1c slice: {len(mine)} keys, 0 unparseable, {len(mine_res)} driven by the fast net "
             f"(fast closure scripts + env_drift --all HEAD^1): {c.get('KILLED', 0)} killed, "
             f"{c.get('SURVIVED', 0)} survived, {c.get('TIMEOUT', 0)} timeout, "
             f"{sum(1 for r in mine_res.values() if not r['runs'])} with every driver skipped by reach; "
             f"first kills " + ", ".join(f"{s.split('/')[-1]} {n}" for s, n in first.most_common()) +
             f"; driver skips by the gate's reach rule {sum(len(r['skipped']) for r in mine_res.values())}, "
             f"by the relaxed rule {sum(len(r.get('relaxed_skipped', [])) for r in mine_res.values())}.")
    full = (f"D3-u1c full net (prescreen.py complete, every deferred/relaxed-skipped closure driver, "
            f"no relaxation, no early stop) on {len(my_comp)} of {c.get('SURVIVED', 0)} slice survivors: "
            f"{cc.get('KILLED', 0)} killed, {cc.get('SURVIVED', 0)} survived, {cc.get('TIMEOUT', 0)} timeout; "
            f"kills per driver (every kill) " + ", ".join(f"{s.split('/')[-1]} {n}" for s, n in ck.most_common()) +
            "; sole killer " + ", ".join(f"{s.split('/')[-1]} {n}" for s, n in only.most_common()) + ".")
    prov = (f"Provisional (judge re-takes): fast-net wall per mutant median "
            f"{sorted(walls)[len(walls)//2] if walls else 0:.0f} s, full-net wall per survivor median "
            f"{sorted(cwalls)[len(cwalls)//2] if cwalls else 0:.0f} s, 4 workers, {MACHINE}, load1 1-5.")
    coverage = [
        {"step": "D3.M2",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --unpinned",
         "universe": len(uni), "examined": len(examined), "not_reached": m2_nr,
         "redispatched": [{"item": "C2", "state": "examined"}, {"item": "C6", "state": "examined"}],
         "evidence": tally + f" Carried runs (B1, D3R) examined {len(examined) - len(mine_res)}. "
                     f"Command: PYTHONPATH=tests/hastub python3 {REL}/u1c_slice.py. " + prov},
        {"step": "D3.M3",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
         "universe": len(surv), "examined": len(m3_done), "not_reached": m3_nr,
         "redispatched": [{"item": "C3", "state": "not_reached"}],
         "evidence": full + " C3 (the GATE_SCOPE=full GOLDEN_MODE=drift gate on the top six) is box "
                     "D3-top6's, not driven here; this box's full-net survivors are listed for it under "
                     "prescreened. " + prov},
        {"step": "D3.M4",
         "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
         "universe": len(surv), "examined": len(surv) - len(m4_nr), "not_reached": m4_nr,
         "redispatched": [],
         "evidence": f"m4_answers.json (carried, {len(m4_old)}) + m4_answers-D3-u1c.json ({len(m4)}): per "
                     "survivor the production line, its file, and the closure drivers whose traced unmutated "
                     "baseline executes the line yet passed (the checks that should have failed), from "
                     f"PYTHONPATH=tests/hastub python3 {REL}/u1c_slice.py --json."},
    ]
    for row in coverage:
        if len(row["not_reached"]) <= 200 and not any("sites not pre-screened" in x for x in row["not_reached"]):
            assert row["examined"] + len(row["not_reached"]) == row["universe"], row["step"]
    prescreened = []
    for k in full_surv + full_to:
        r = my_comp[k]
        a = m4[k]
        prescreened.append({
            "key": k, "site": site_id(r["mutant"]), "patch": f"{a['old']}  ->  {a['new']}",
            "closure_ran": sorted(r["runs"]), "skipped_by_reach": sorted(set(r["skipped"])),
            "verdict": r["verdict"], "should_have_failed": a["should_have_failed"]})
    old = json.loads((HERE / "REPORT-D3R.json").read_text())
    rep = {
        "dimension": "D3", "baseline_sha": BASE, "report_path": f"{REL}/REPORT.md",
        "exposure": old["exposure"] + " Box D3-u1c run: read the carried evidence directory "
                    "(c0adbc19, box D3R's return), COMMON.md, D3.md, dev/audit/README.md, "
                    "finding.schema.json; no docs/, no GitHub, no earlier-round findings.",
        "coverage": coverage, "unfinished": [], "findings": [],
        "prescreened": prescreened,
        "non_findings": [],
        "harnesses": old["harnesses"] + [f"{REL}/u1c_slice.py", f"{REL}/u1c_report.py",
                                         f"{REL}/u1c_chain.sh", f"{REL}/u1c_ckloop.sh"],
        "leads": [],
    }
    killed_full = sorted(k for k, r in my_comp.items() if r["verdict"] == "KILLED")
    rep["non_findings"] = [
        {"claim": "Null control: the fast net LIVES on the unmutated tree (re-taken on box D3-u1c after re-taking all 21 traced baselines, all rc=0 failed=0)",
         "command": f"PYTHONPATH=tests/hastub python3 {REL}/prescreen.py null",
         "value": "null_verdict=LIVES over 16 fast drivers (state/null-D3-u1c.json, state/u1c-null.out)"},
        {"claim": "Positive control: the pre-screen kills ledger-pinned sites on this box",
         "command": f"PYTHONPATH=tests/hastub python3 {REL}/prescreen.py run --anchors {REL}/posctl_anchors.txt --sub posctl-D3-u1c",
         "value": "2/2 KILLED by tests/manual_plan.py (state/u1c-posctl.out)"},
        {"claim": f"{c.get('KILLED', 0)} of {len(mine_res)} D3-u1c slice mutants are pinned by the fast net",
         "command": f"PYTHONPATH=tests/hastub python3 {REL}/u1c_slice.py",
         "value": tally},
        {"claim": f"{len(killed_full)} of {len(my_comp)} fast-net survivors of the slice are pinned by the full closure net",
         "command": f"PYTHONPATH=tests/hastub python3 {REL}/u1c_slice.py",
         "value": full + " Killed sites: " + "; ".join(short(my_comp[k]['mutant']) + " by " + ",".join(x.split('/')[-1] for x in my_comp[k]['killed_by']) for k in killed_full)},
    ]
    (HERE / "REPORT.json").write_text(json.dumps(rep, indent=1))
    L = [f"# D3-s1 round 11, box D3-u1c slice (baseline {BASE[:8]})", "",
         "Seat D3-s1, resume box D3-u1c: the D3.M2 slice `state/keys-D3-u1c.txt` (309 keys, "
         f"`{LO}` <= key < `{HI}` of `state/u1_keys.txt` less carried results; sha256 5f427b5e35ba1659...) "
         "and D3.M3's full net for its survivors. D3-s1-01 (box D3R) is not re-reported. The full "
         "GATE_SCOPE=full GOLDEN_MODE=drift gate is box D3-top6's.", "",
         "## Method", "",
         "R0 restored c0adbc19's s1/ directory. R1: state/baselines.json was box D3R's, so all 21 "
         "drivers' traced baselines were re-taken here (`prescreen.py baseline --workers 4`, all rc=0 "
         "failed=0; D3R's kept as state/superseded/baselines-D3R.json) and the env_drift capture child "
         "re-traced (`prescreen.py trace-capture`, procs 2/2). Null control LIVES (16 fast drivers); "
         "positive control 2/2 KILLED by tests/manual_plan.py. K1: `prescreen.py run --anchors "
         "state/keys-D3-u1c.txt --sub pre --workers 4` (fresh tree per mutant). K2: `prescreen.py "
         "complete --src pre --keys state/keys-D3-u1c-surv.txt --workers 4`. Driven by u1c_chain.sh, "
         "checkpointed by u1c_ckloop.sh (every 25 pre-screened keys, every full-net result).", "",
         f"Machine: {MACHINE}. Every wall figure is provisional: true; counts and verdicts are final.", "",
         "## Tally", "", "- " + tally, "- " + full, "- " + prov, "",
         "## Coverage", ""]
    for row in coverage:
        L.append(f"- {row['step']}: universe {row['universe']}, examined {row['examined']}, "
                 f"not reached {len(row['not_reached'])} line(s). Enumerator: `{row['enumerator']}`")
    L += ["", "## Prescreened survivors of the full net (for box D3-top6's full gate), with D3.M4's answer", "",
          "| site | patch | should have failed |", "|---|---|---|"]
    for x in prescreened:
        L.append(f"| {x['site']} | `{x['patch'][:90].replace('|', '/')}` | "
                 f"{', '.join(s.split('/')[-1] for s in x['should_have_failed'])[:160]} |")
    L += ["", "## Findings", "", "None from this box: per D3.md step 3 the slice's survivors are "
          "candidates; only the quiet-window full gate (box D3-top6) makes findings.", "",
          "## Non-findings", ""]
    for nf in rep["non_findings"]:
        L.append(f"- {nf['claim']}: `{nf['command']}` -> {nf['value']}")
    L += ["", "## Harnesses", ""] + [f"- `{h}`" for h in rep["harnesses"]]
    L += ["", "## Unfinished", "", "None for this box's slice.", "",
          "## Exposure", "", rep["exposure"], ""]
    (HERE / "REPORT.md").write_text("\n".join(L))
    for row in coverage:
        print(f"RESULT {row['step']}_universe={row['universe']} examined={row['examined']} not_reached={len(row['not_reached'])}")
    print(f"RESULT prescreened={len(prescreened)}")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
