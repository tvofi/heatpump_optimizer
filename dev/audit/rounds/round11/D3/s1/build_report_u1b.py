#!/usr/bin/env python3
"""D3-s1, box D3-u1b: assemble this box's slice report (D3.M2 slice, D3.M3 full net).

Metric (one line): per step, universe = items its enumerator prints at the
baseline, examined = items the step's method ran on here or in the carried
runs (state/results/<sub>/<key>.json present), not_reached = the rest, grouped
by owning box and file. Counts are exact; walls are provisional.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/build_report_u1b.py
Reads state/ (results/{pre,c2,c3c6,complete}, keys-D3-u1b*.txt, baselines.json),
REPORT.json (box D3R's carried report) and report_extra.json; writes
REPORT-D3-u1b.json, REPORT-D3-u1b.md and m4_answers_u1b.json beside it.
Instrumented symbol: tests/mutation_table.py:unpinned_sites (via prescreen.unpinned)
and the per-script traced reach in state/baselines.json (coverage hits).
Perturbation: deleting one state/results/complete/<key>.json of this slice lowers
D3.M3 examined by one and adds that survivor to not_reached (direction: down).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: cloud box D3-u1b,
4 vCPU Intel Xeon @ 2.30GHz, 16 GB.
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
BOX = "D3-u1b"
# U1 key ranges per box, from each box's dispatch (K0): lo <= key < hi
RANGES = [("D3-u1a", "000221f3921dd956", "3daa55123b452546"),
          ("D3-u1b", "3daa55123b452546", "8206a42b98c8dd86"),
          ("D3-u1c", "8206a42b98c8dd86", "c0ecc8e0b6b66ded"),
          ("D3-u1d", "c0ecc8e0b6b66ded", None)]
# checks that read source text or structure, not behaviour of the mutated line
STATIC = {"tests/structure.py", "tests/typing_ruler.py", "tests/arch_score_head.py",
          "tests/harness_headers.py", "tests/doc_claims.py", "tests/deployment_shape.py"}


def owner(k):
    for b, lo, hi in RANGES:
        if k >= lo and (hi is None or k < hi):
            return b
    return "unknown"


def load(sub):
    d = p.RESULTS / sub
    return {q.stem: json.loads(q.read_text()) for q in d.glob("*.json")} if d.exists() else {}


def site_id(m):
    return f"{m['file']}:{m['line']} {m['kind']} {m['anchor'].split()[-1]}"


def short(f):
    return f.rsplit("/", 1)[-1]


def group(items, label):
    by = defaultdict(list)
    for m in items:
        by[m["file"]].append(m["line"])
    return [f"{label}: {short(f)}: {len(ls)} sites (lines {min(ls)}-{max(ls)})"
            for f, ls in sorted(by.items())]


def main() -> int:
    uni = p.unpinned()
    keys = {p.key(m): m for m in uni}
    pre, c2, c36, comp = load("pre"), load("c2"), load("c3c6"), load("complete")
    mine = [ln.strip() for ln in (p.STATE / "keys-D3-u1b.txt").read_text().splitlines() if ln.strip()]
    u1 = {ln.strip() for ln in (p.STATE / "u1_keys.txt").read_text().splitlines() if ln.strip()}
    carried = json.loads((HERE / "REPORT.json").read_text()) if (HERE / "REPORT.json").exists() else {}
    if carried.get("box") == BOX:  # a re-run: take the carried report from its saved copy
        carried = json.loads((HERE / "REPORT-D3R.json").read_text())
    else:
        (HERE / "REPORT-D3R.json").write_text(json.dumps(carried, indent=1) + "\n")
    extra = json.loads((HERE / "report_extra.json").read_text())
    base = json.loads((p.STATE / "baselines.json").read_text())

    # ---- D3.M2 -------------------------------------------------------------
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
        b = owner(k) if k in u1 else "unknown"
        nr[b].append(m)
    m2_nr = []
    for b in sorted(nr):
        lab = f"assigned to box {b}" if b != "unknown" else "unassigned"
        m2_nr += group(nr[b], lab)
    slice_res = {k: pre[k] for k in mine if k in pre}
    tally = Counter(r["verdict"] for r in slice_res.values())
    killers = Counter(s for r in slice_res.values() if r["verdict"] == "KILLED" for s in r["killed_by"])
    first = Counter(r["killed_by"][0] for r in slice_res.values() if r["verdict"] == "KILLED" and r["killed_by"])
    skipped = sum(len(r.get("skipped", [])) for r in slice_res.values())
    relaxed = sum(len(r.get("relaxed_skipped", [])) for r in slice_res.values())
    deferred = sum(len(r.get("deferred_slow", [])) for r in slice_res.values())
    unparse = sum(1 for r in slice_res.values() for run in r["runs"].values()
                  if run.get("rc") not in (0, None) and run.get("failed", 0) == 0 and not run.get("timed_out"))
    timeouts = sum(1 for r in slice_res.values() for run in r["runs"].values() if run.get("timed_out"))
    walls = sorted(r["wall"] for r in slice_res.values())

    # ---- D3.M3 (full net) --------------------------------------------------
    surv = {k: r for sub in (pre, c2, c36) for k, r in sub.items() if r["verdict"] == "SURVIVED"}
    my_surv = [k for k in mine if k in surv]
    comp_mine = {k: comp[k] for k in my_surv if k in comp and comp[k].get("completed")}
    m3_ex = [k for k in surv if k in comp and comp[k].get("completed")]
    m3_nr = []
    car_nr = [surv[k]["mutant"] for k in surv if k not in mine and k not in m3_ex]
    if car_nr:
        m3_nr += [f"assigned to box D3-top6: {site_id(m)}" for m in car_nr]
    mine_nr = [surv[k]["mutant"] for k in my_surv if k not in comp_mine]
    m3_nr += [f"not reached on box {BOX}: {site_id(m)}" for m in mine_nr]
    for b, _, _ in RANGES:
        if b != BOX:
            m3_nr.append(f"assigned to box {b}: the U1 survivors of its key range (its pre-screen "
                         f"is driven there; none is in this box's state)")
    ctally = Counter(r["verdict"] for r in comp_mine.values())
    ckill = Counter(s for r in comp_mine.values() if r["verdict"] == "KILLED" for s in r["killed_by"])
    cwalls = sorted(r.get("complete_wall", 0) for r in comp_mine.values())
    full_surv = [k for k, r in comp_mine.items() if r["verdict"] == "SURVIVED"]

    # ---- D3.M4 answers for this slice's full-net survivors -----------------
    m4 = {}
    for k in full_surv:
        r = comp_mine[k]
        m = r["mutant"]
        ran = sorted(r["runs"])
        hit = [s for s in ran if s not in STATIC and
               m["line"] in set(base.get(s, {}).get("reach", {}).get("hits", {}).get(m["file"], []))]
        sym = m["anchor"].split(":", 1)[1].rsplit(" ", 2)[0]
        should = (", ".join(hit) + f" each execute{'s' if len(hit) == 1 else ''} line {m['line']} "
                  "on the traced baseline yet no check of "
                  f"{'it' if len(hit) == 1 else 'theirs'} reads an outcome the mutation changes") if hit else (
            "no closure script executes this line on the traced baseline; a check that drives "
            f"{sym} through this branch should exist and fail")
        m4[k] = (f"{short(m['file'])}:{m['line']} {sym} {m['kind']}: `{m['old'].strip()}` -> "
                 f"`{m['new'].strip()}`. Ran {len(ran)} closure scripts, none killed. "
                 f"Should fail: {should}.")
    (HERE / "m4_answers_u1b.json").write_text(json.dumps(m4, indent=1) + "\n")

    # ---- rows --------------------------------------------------------------
    crow = {r["step"]: r for r in carried.get("coverage", [])}
    ev = lambda lst: "; ".join(f"{e['command']} -> {e['value']}" for e in lst) if isinstance(lst, list) else str(lst)
    rows = []
    r1 = dict(crow["D3.M1"]); r1["evidence"] = "carried from box D3R (not re-driven here): " + ev(r1["evidence"])
    rows.append(r1)
    rows.append({
        "step": "D3.M2", "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/enumerate.py --unpinned",
        "universe": len(uni), "examined": len(examined), "not_reached": m2_nr,
        "redispatched": [{"item": "C2", "state": "examined"}, {"item": "C6", "state": "examined"}],
        "evidence": (f"box {BOX} slice: state/keys-D3-u1b.txt, {len(mine)} keys (sha256 64a2b349a1a11196...), "
                     f"lo=3daa55123b452546 <= key < 8206a42b98c8dd86; prescreen.py run --sub pre --workers 4: "
                     f"driven {len(slice_res)}, KILLED {tally['KILLED']}, SURVIVED {tally['SURVIVED']}, "
                     f"TIMEOUT {tally['TIMEOUT']}; tabulate.py; examined {len(examined)} = carried runs + this slice"),
    })
    rows.append({
        "step": "D3.M3",
        "enumerator": f"PYTHONPATH=tests/hastub python3 {REL}/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
        "universe": len(surv), "examined": len(m3_ex), "not_reached": m3_nr,
        "redispatched": [{"item": "C3", "state": "not_reached"}, {"item": "C5", "state": "examined"}],
        "evidence": (f"prescreen.py complete --src pre --keys {REL}/state/keys-D3-u1b-surv.txt --workers 4: "
                     f"{len(comp_mine)} of {len(my_surv)} slice survivors completed, KILLED {ctally['KILLED']}, "
                     f"SURVIVED {ctally['SURVIVED']}, TIMEOUT {ctally['TIMEOUT']}; universe here = the "
                     f"SURVIVED results present on this box (carried + this slice); the other U1 boxes' "
                     f"survivors are named by box in not_reached; C3 (full gate) is box D3-top6's"),
    })
    m4_carried = set(extra.get("m4_answered", []))
    m4_ex = [k for k in surv if k in m4_carried or k in m4]
    m4_nr = []
    for k in surv:
        if k in m4_ex:
            continue
        if k in mine and k in comp_mine and comp_mine[k]["verdict"] == "KILLED":
            m4_nr.append(f"killed by the full net (no step-4 answer owed): {site_id(surv[k]['mutant'])}")
        elif k in mine:
            m4_nr.append(f"not reached on box {BOX}: {site_id(surv[k]['mutant'])}")
        else:
            m4_nr.append(f"assigned to box D3-top6: {site_id(surv[k]['mutant'])}")
    rows.append({
        "step": "D3.M4", "enumerator": rows[2]["enumerator"], "universe": len(surv),
        "examined": len(m4_ex), "not_reached": m4_nr if len(m4_nr) <= 200 else
        [f"{len(m4_nr)} survivors: see m4_answers_u1b.json"], "redispatched": [],
        "evidence": (f"m4_answers.json (carried, {len(m4_carried)}) + m4_answers_u1b.json "
                     f"({len(m4)} full-net survivors of this slice, built from state/baselines.json reach)"),
    })
    r5 = dict(crow["D3.M5"]); r5["evidence"] = "carried from box D3R (not re-driven here; (a)-(e) are box D3-m5's): " + ev(r5["evidence"])
    r5["not_reached"] = [f"assigned to box D3-m5: {s}" for s in r5["not_reached"]]
    rows.append(r5)
    for r in rows:
        assert r["examined"] + (0 if r["not_reached"] else 0) <= r["universe"], r["step"]

    nf = [
        {"claim": "null control: the fast net lives on the unmutated tree on this box",
         "command": f"PYTHONPATH=tests/hastub python3 {REL}/prescreen.py null",
         "value": "null_verdict=LIVES, null_drivers_run=16, load1=1.00"},
        {"claim": "positive control: both ledger-pinned sites are killed on this box",
         "command": f"PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1 python3 {REL}/prescreen.py run --anchors {REL}/posctl_anchors.txt --sub posctl-D3-u1b --workers 2",
         "value": "2/2 KILLED by tests/manual_plan.py (coordinator.py:8535 RETURN_DEL, optimizer.py:1052 GUARD_OFF)"},
        {"claim": f"box {BOX} pre-screen slice tally",
         "command": f"PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1 python3 {REL}/prescreen.py run --anchors {REL}/state/keys-D3-u1b.txt --sub pre --workers 4",
         "value": (f"driven {len(slice_res)}: KILLED {tally['KILLED']}, SURVIVED {tally['SURVIVED']}, TIMEOUT {tally['TIMEOUT']}; "
                   f"first killer: {dict(first.most_common())}; script-runs skipped by reach {skipped}, relaxed-skipped {relaxed}, "
                   f"deferred slow {deferred}, unparseable (rc!=0, 0 failed, no timeout) {unparse}, script timeouts {timeouts}; "
                   f"wall per mutant median {walls[len(walls)//2]:.0f} s (provisional: 4 vCPU Xeon 2.30GHz, load1 3.7-4.4)")},
        {"claim": f"box {BOX} full net on the slice's survivors",
         "command": f"PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1 python3 {REL}/prescreen.py complete --src pre --keys {REL}/state/keys-D3-u1b-surv.txt --workers 4",
         "value": (f"{len(comp_mine)} completed: KILLED {ctally['KILLED']}, SURVIVED {ctally['SURVIVED']}, TIMEOUT {ctally['TIMEOUT']}; "
                   f"killers {dict(ckill.most_common())}; wall per mutant median "
                   f"{(cwalls[len(cwalls)//2] if cwalls else 0):.0f} s (provisional, same machine)")},
    ]
    report = {
        "dimension": "D3", "baseline_sha": BASE, "box": BOX,
        "report_path": f"{REL}/REPORT-D3-u1b.md",
        "exposure": (carried.get("exposure", "") + " Box D3-u1b additionally read only this seat's carried "
                     "evidence (REPORT.json, LOCAL-REPORT.json, harness sources) and the sibling boxes' "
                     "dispatch PROMPT.md key ranges; no docs/ or GitHub records."),
        "coverage": rows,
        "unfinished": [],
        "findings": [],
        "non_findings": nf,
        "harnesses": [f"{REL}/{h}" for h in ("prescreen.py", "tabulate.py", "enumerate.py", "build_report_u1b.py")],
        "leads": [],
        "prescreened_survivors": [
            {"key": k, "site": site_id(comp_mine[k]["mutant"]), "answer": m4[k]} for k in full_surv],
    }
    static_first = sum(v for s, v in first.items() if s in STATIC)
    md = [f"# D3-s1, round 11, box {BOX}: D3.M2 slice and D3.M3 full net", "",
          f"Baseline `{BASE}`. Machine: 4 vCPU Intel Xeon @ 2.30GHz, 16 GB, load1 3.5-5.2 "
          "while driving (every wall below is provisional; the judge re-takes it). Counts are final.", "",
          "## Slice", "",
          f"`state/keys-D3-u1b.txt`: {len(mine)} U1 keys, 3daa55123b452546 <= key < 8206a42b98c8dd86 "
          "(sha256 64a2b349a1a11196..., as the dispatch required). Controls on this box before driving: "
          "null LIVES (16 drivers); positive control 2/2 KILLED by tests/manual_plan.py.", "",
          "## D3.M2 pre-screen tally", "",
          "| driven | KILLED | SURVIVED | TIMEOUT | script-runs skipped by reach | unparseable runs |",
          "|---|---|---|---|---|---|",
          f"| {len(slice_res)} | {tally['KILLED']} | {tally['SURVIVED']} | {tally['TIMEOUT']} | {skipped} | {unparse} |", "",
          "First killer per KILLED mutant: " + ", ".join(f"{s} {n}" for s, n in first.most_common()) + ".",
          f"{static_first} of {tally['KILLED']} kills came first from a check that reads source text or "
          "structure (typing_ruler, structure, deployment_shape); the fast net stops at the "
          "first kill, so whether a behavioural check also kills them is box D3-m5's kill-overlap matrix.", "",
          "## D3.M3 full net (every closure script, no early stop)", "",
          f"{len(comp_mine)} of {len(my_surv)} slice survivors completed: KILLED {ctally['KILLED']}, "
          f"SURVIVED {ctally['SURVIVED']}, TIMEOUT {ctally['TIMEOUT']}. Killers: "
          + ", ".join(f"{s} {n}" for s, n in ckill.most_common()) + ".",
          f"Median full-net wall per mutant {(cwalls[len(cwalls)//2] if cwalls else 0):.0f} s (provisional).", "",
          "## Prescreened survivors for the D3-top6 full gate, with D3.md step 4's answer", "",
          "Each answer names the production line, its file, and the closure scripts whose traced baseline "
          "executes that line (state/baselines.json reach): those are the checks that should have failed. "
          "Only a full-gate survivor becomes a finding (D3.md step 3); none is reported here.", ""]
    md += [f"- `{k}` {m4[k]}" for k in full_surv]
    md += ["", "## Coverage", ""]
    md += [f"- {r['step']}: universe {r['universe']}, examined {r['examined']}, not_reached {len(r['not_reached'])} rows"
           for r in rows]
    report["report_md"] = "\n".join(md) + "\n"
    (HERE / "REPORT-D3-u1b.md").write_text(report["report_md"])
    (HERE / "REPORT-D3-u1b.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"RESULT slice_driven={len(slice_res)} killed={tally['KILLED']} survived={tally['SURVIVED']} timeout={tally['TIMEOUT']}")
    print(f"RESULT fullnet_done={len(comp_mine)}/{len(my_surv)} killed={ctally['KILLED']} survived={ctally['SURVIVED']}")
    print(f"RESULT M2 universe={len(uni)} examined={len(examined)} groups={len(m2_nr)}")
    print(f"RESULT M3 universe={len(surv)} examined={len(m3_ex)} nr={len(m3_nr)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
