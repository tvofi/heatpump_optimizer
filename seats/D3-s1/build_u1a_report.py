"""Box D3-u1a: build seat D3-s1's REPORT.json for this box's slice.

Run from the seat worktree root:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/build_u1a_report.py

Reads the carried REPORT.json (boxes B1 and D3R), the results under
state/results/{pre,c2,c3c6,complete}/, this box's key file state/keys-D3-u1a.txt
and the step-4 answers in m4_answers.json (carried) and m4_u1a_part*.json (this
box). Writes REPORT-u1a.json and REPORT-u1a.md beside it; the caller copies them
over REPORT.json / REPORT.md. Prints RESULT lines with the slice tally.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prescreen as ps  # noqa: E402

STATE = HERE / "state"
RES = STATE / "results"
BOX = "D3-u1a"
OTHER = "D3-top6, D3-u1b, D3-u1c, D3-u1d and D3-m5"
REL = "dev/audit/rounds/round11/D3/s1"


def load(sub: str) -> dict[str, dict]:
    return {Path(p).stem: json.loads(Path(p).read_text())
            for p in sorted(glob.glob(str(RES / sub / "*.json")))}


def lines(p: Path) -> list[str]:
    return [ln.strip() for ln in p.read_text().splitlines() if ln.strip()]


def site(m: dict) -> str:
    return f"{m['file']}:{m['line']} {m.get('kind', '?')}"


def main() -> int:
    carried = json.loads((HERE / "REPORT.json").read_text())
    if carried.get("_box") == BOX:
        carried = json.loads((HERE / "REPORT-carried.json").read_text())
    inv = ps.unpinned()
    inv_keys = {ps.key(m): m for m in inv}
    pre, c2, c3c6, comp = load("pre"), load("c2"), load("c3c6"), load("complete")
    mine = lines(STATE / "keys-D3-u1a.txt")
    surv_file = lines(STATE / "keys-D3-u1a-surv.txt")

    # ---- K1 tally (this box's slice) ----
    k1 = collections.Counter(pre[k]["verdict"] for k in mine if k in pre)
    first = collections.Counter(pre[k]["killed_by"][0] for k in mine
                                if k in pre and pre[k]["killed_by"])
    skips = sum(len(pre[k]["skipped"]) for k in mine if k in pre)
    relaxed = sum(len(pre[k].get("relaxed_skipped", [])) for k in mine if k in pre)
    all_skipped = sum(1 for k in mine if k in pre and not pre[k]["runs"])
    unparse = sum(1 for k in mine if k in pre
                  and pre[k]["verdict"] not in ("KILLED", "SURVIVED", "TIMEOUT"))
    undriven = [k for k in mine if k not in pre]
    k1_surv = [k for k in mine if k in pre and pre[k]["verdict"] == "SURVIVED"]
    assert sorted(k1_surv) == sorted(surv_file), "survivor key file disagrees with results"

    # ---- K2 tally ----
    k2 = collections.Counter(comp[k]["verdict"] for k in k1_surv if k in comp)
    k2_by = collections.Counter(",".join(comp[k]["killed_by"]) for k in k1_surv
                                if k in comp and comp[k]["killed_by"])
    k2_undone = [k for k in k1_surv if k not in comp]
    k2_surv = [k for k in k1_surv if k in comp and comp[k]["verdict"] != "KILLED"]
    timeouts = {k: [s for s, r in comp[k]["runs"].items() if r.get("timed_out")]
                for k in k1_surv if k in comp and comp[k]["verdict"] == "TIMEOUT"}

    # ---- step-4 answers ----
    ans: dict[str, dict] = {}
    for p in sorted(HERE.glob("m4_u1a_part*.json"), key=lambda p: int(p.stem.split("part")[1])):
        ans.update(json.loads(p.read_text()))
    carried_ans = json.loads((HERE / "m4_answers.json").read_text())
    missing_ans = [k for k in k2_surv if k not in ans]
    kinds = collections.Counter(ans[k]["kind"] for k in k2_surv if k in ans)

    # ---- coverage ----
    def by_file(keys: list[str], what: str) -> list[str]:
        g: dict[str, list[int]] = collections.defaultdict(list)
        for k in keys:
            m = inv_keys[k]
            g[m["file"]].append(m["line"])
        return [f"{f}: {len(v)} unpinned sites {what} (lines {min(v)}-{max(v)})"
                for f, v in sorted(g.items())]

    driven_inv = {k for k in inv_keys if k in pre or k in c2 or k in c3c6}
    rest = sorted(k for k in inv_keys if k not in driven_inv)
    lo, hi = mine[0] if False else "000221f3921dd956", "3daa55123b452546"
    in_range_rest = [k for k in rest if lo <= k < hi]
    out_range_rest = [k for k in rest if not (lo <= k < hi)]
    cov_c = {c["step"]: c for c in carried["coverage"]}

    m2 = dict(cov_c["D3.M2"])
    m2["examined"] = len(driven_inv)
    m2["not_reached"] = (by_file(in_range_rest, f"in box {BOX}'s key range not driven")
                         + by_file(out_range_rest,
                                   f"not pre-screened: outside box {BOX}'s key range "
                                   f"[{lo}, {hi}), assigned to box D3-u1b/D3-u1c/D3-u1d"))
    m2["evidence"] = list(cov_c["D3.M2"]["evidence"]) + [{
        "command": f"PYTHONPATH=tests/hastub python3 {REL}/build_u1a_report.py",
        "value": (f"box {BOX} K1 (fast net = fast closure scripts + env_drift --all, "
                  f"traced baselines re-taken on this box): {sum(k1.values())} of {len(mine)} "
                  f"keys driven, {k1['KILLED']} killed, {k1['SURVIVED']} survived, "
                  f"{k1['TIMEOUT']} timeout, {unparse} unparseable; first kill by "
                  + ", ".join(f"{s} {n}" for s, n in first.most_common())
                  + f"; {skips} driver runs skipped by reach ({relaxed} by the relaxed git-only "
                  f"reach), {all_skipped} mutants with every driver reach-skipped. "
                  f"Inventory mutants driven by all runs, counted by mutant key (sha1 of anchor|new) "
                  f"over results/pre, c2 and c3c6: {len(driven_inv)} of {len(inv_keys)} (the carried "
                  f"rows' 34 also counted re-drawn R10 mutants that coincide with an inventory site by "
                  f"line but not by key).")}]

    m3_universe = sorted({k for d in (pre, c2, c3c6) for k, r in d.items()
                          if r["verdict"] in ("SURVIVED", "TIMEOUT")})
    m3_done = [k for k in m3_universe if k in comp]
    m3_rest = [k for k in m3_universe if k not in comp]
    src = {**c3c6, **c2, **pre}
    m3 = dict(cov_c["D3.M3"])
    m3["enumerator"] = (f"PYTHONPATH=tests/hastub python3 {REL}/build_u1a_report.py --m3-universe")
    m3["universe"] = len(m3_universe)
    m3["examined"] = len(m3_done)
    m3["not_reached"] = [f"{site(src[k]['mutant'])} {k} (full net not in box {BOX}'s slice; "
                         f"carried survivor, owed to the D3 boxes {OTHER})" for k in m3_rest][:200]
    m3["evidence"] = list(cov_c["D3.M3"]["evidence"]) + [{
        "command": f"PYTHONPATH=tests/hastub python3 {REL}/build_u1a_report.py",
        "value": (f"box {BOX} K2 full net (prescreen.py complete: every deferred slow script "
                  f"incl. features.py and entities.py, no relaxation, no early stop) on its "
                  f"{len(k1_surv)} K1 survivors: {sum(k2.values())} completed, {k2['KILLED']} killed ("
                  + ", ".join(f"{s} {n}" for s, n in k2_by.most_common())
                  + f"), {k2['SURVIVED']} survived, {k2['TIMEOUT']} timeout "
                  + "; ".join(f"{k} timed out in {','.join(v)}" for k, v in timeouts.items())
                  + f"; {len(k2_undone)} not completed.")}]

    m4_universe = sorted(set(carried_ans) | set(k2_surv))
    m4_done = [k for k in m4_universe if k in carried_ans or k in ans]
    m4 = dict(cov_c["D3.M4"])
    m4["enumerator"] = (f"PYTHONPATH=tests/hastub python3 {REL}/build_u1a_report.py --m4-universe")
    m4["universe"] = len(m4_universe)
    m4["examined"] = len(m4_done)
    m4["not_reached"] = [k for k in m4_universe if k not in m4_done]
    m4["evidence"] = list(cov_c["D3.M4"]["evidence"]) + [{
        "command": f"cat {REL}/m4_u1a_part*.json",
        "value": (f"box {BOX}: {len([k for k in k2_surv if k in ans])} of {len(k2_surv)} full-net "
                  f"survivors and timeouts answered (production line, file, the check that should "
                  f"have failed); read as " + ", ".join(f"{n} {s}" for s, n in kinds.most_common()))}]

    coverage = []
    for c in carried["coverage"]:
        coverage.append({"D3.M2": m2, "D3.M3": m3, "D3.M4": m4}.get(c["step"], c))

    # ---- prescreened survivors for the D3-top6 full gate ----
    pres = []
    for k in k2_surv:
        r = comp[k]; m = r["mutant"]
        pres.append({
            "key": k, "site": site(m), "anchor": m["anchor"],
            "patch": {"file": m["file"], "line": m["line"], "old": m["old"], "new": m["new"]},
            "closure_scripts": sorted(r["runs"]) + sorted(r["skipped"]),
            "ran": sorted(r["runs"]), "reach_skipped": sorted(r["skipped"]),
            "verdict_fast": pre[k]["verdict"], "verdict_full": r["verdict"],
            "timed_out": timeouts.get(k, []),
            "step4": ans.get(k, {}).get("answer", ""), "reading": ans.get(k, {}).get("kind", ""),
        })
    order = {"gap": 0, "boundary": 1, "equivalent": 2, "": 3}
    pres.sort(key=lambda p: (order.get(p["reading"], 3), p["site"]))
    (HERE / "prescreened-u1a.json").write_text(json.dumps(pres, indent=1))

    non_findings = list(carried["non_findings"]) + [
        {"claim": f"box {BOX} controls: the fast net LIVES on the unmutated tree and the harness can kill",
         "command": f"cat {REL}/state/u1a-null.out {REL}/state/u1a-posctl.out",
         "value": "null LIVES over 16 fast drivers; positive control 2/2 ledger-pinned sites KILLED by tests/manual_plan.py"},
        {"claim": f"box {BOX}: {k2['KILLED']} K1 survivors are pinned by the slow scripts only (fast net blind, full net kills)",
         "command": f"cat {REL}/state/results/complete/<key>.json for the K2 kills",
         "value": "; ".join(f"{site(comp[k]['mutant'])} by {','.join(comp[k]['killed_by'])}"
                            for k in k1_surv if k in comp and comp[k]["verdict"] == "KILLED")},
    ]
    harnesses = list(dict.fromkeys(list(carried["harnesses"]) + [
        f"{REL}/build_u1a_report.py", f"{REL}/m4_pending.py"]))

    unfinished = []
    if undriven:
        unfinished.append({"step": "D3.M2", "what": f"{len(undriven)} of box {BOX}'s {len(mine)} keys not driven"})
    if k2_undone:
        unfinished.append({"step": "D3.M3", "what": f"{len(k2_undone)} of box {BOX}'s K1 survivors without a full-net drive"})
    if missing_ans:
        unfinished.append({"step": "D3.M4", "what": f"{len(missing_ans)} full-net survivors without a step-4 answer: {missing_ans}"})

    exposure = (carried["exposure"] + f" Box {BOX} (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, alone; run inline "
                "in the box session per inbox command 1): read the carried REPORT.json and LOCAL-REPORT.json, "
                "D3.md, check_report.mjs, finding.schema.json, the seat's own harnesses and state, and the "
                f"{len(k2_surv)} survivor lines in the cell files with a few lines of context (m4_pending.py); "
                "no docs/, no GitHub beyond the box's own dispatch/inbox/wip refs.")

    rep = {"dimension": "D3", "baseline_sha": carried["baseline_sha"],
           "report_path": f"{REL}/REPORT.md", "exposure": exposure, "coverage": coverage,
           "unfinished": unfinished, "findings": [], "non_findings": non_findings,
           "harnesses": harnesses, "leads": [], "_box": BOX,
           "prescreened": f"{REL}/prescreened-u1a.json"}

    md = [f"# D3-s1 round 11, box {BOX} slice (baseline {carried['baseline_sha'][:8]})", "",
          f"Box {BOX}: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, alone (load1 ~4 under 4 workers). "
          "Evidence restored from the box's checkpoint; the seat's traced baselines re-taken here (21/21), "
          "null control LIVES (16 drivers), positive control 2/2 KILLED. Verdicts and counts are final; "
          "every wall/CPU number is provisional (the judge re-takes it).", "",
          "No findings from this slice: D3.md step 3 makes survivors candidates; the "
          "GATE_SCOPE=full GOLDEN_MODE=drift gate for the top survivors is box D3-top6's.", "",
          "## Slice tally", "",
          f"- K1 fast net: {len(mine)} keys (lo 000221f3921dd956 <= key < 3daa55123b452546), "
          f"{sum(k1.values())} driven, {k1['KILLED']} killed, {k1['SURVIVED']} survived, {k1['TIMEOUT']} timeout, "
          f"{unparse} unparseable, {all_skipped} with every driver reach-skipped ({skips} driver runs reach-skipped).",
          "- First kill by: " + ", ".join(f"{s} {n}" for s, n in first.most_common()),
          f"- K2 full net on the {len(k1_surv)} survivors: {k2['KILLED']} killed ("
          + ", ".join(f"{s} {n}" for s, n in k2_by.most_common()) + f"), {k2['SURVIVED']} survived, "
          f"{k2['TIMEOUT']} timeout" + "".join(f" ({k}: {','.join(v)})" for k, v in timeouts.items()) + ".",
          "- Step-4 readings of the full-net survivors: " + ", ".join(f"{n} {s}" for s, n in kinds.most_common()), "",
          "Incidents: three container restarts; the second killed K2 mid-drive and left four worker trees "
          "mutated, which were discarded and re-added before resuming (the in-flight mutants were re-driven); "
          "a comms lock left by the first restart silently failed checkpoints between 21:12Z and 00:27Z until cleared.", "",
          "## Coverage", ""]
    for c in coverage:
        md.append(f"- {c['step']}: universe {c['universe']}, examined {c['examined']}, "
                  f"not reached {len(c['not_reached'])} line(s). Enumerator: `{c['enumerator']}`")
    md += ["", "## Prescreened survivors (full net), for the D3-top6 full gate", "",
           "Ordered gap, boundary, equivalent. Each: site, key, the step-4 answer.", ""]
    for p in pres:
        md.append(f"- [{p['reading']}] `{p['site']}` {p['key']}: {p['step4']}")
    rep["report_md"] = "\n".join(md) + "\n"
    (HERE / "REPORT-u1a.json").write_text(json.dumps(rep, indent=1))
    (HERE / "REPORT-u1a.md").write_text(rep["report_md"])

    print(f"RESULT k1_driven={sum(k1.values())} k1_killed={k1['KILLED']} k1_survived={k1['SURVIVED']} "
          f"k1_timeout={k1['TIMEOUT']} undriven={len(undriven)}")
    print(f"RESULT k2_done={sum(k2.values())} k2_killed={k2['KILLED']} k2_survived={k2['SURVIVED']} "
          f"k2_timeout={k2['TIMEOUT']} k2_undone={len(k2_undone)} missing_answers={len(missing_ans)}")
    print(f"RESULT m2_examined={m2['examined']}/{m2['universe']} m3={m3['examined']}/{m3['universe']} "
          f"m4={m4['examined']}/{m4['universe']}")
    return 0


if __name__ == "__main__":
    if "--m3-universe" in sys.argv or "--m4-universe" in sys.argv:
        pre, c2, c3c6, comp = load("pre"), load("c2"), load("c3c6"), load("complete")
        src = {**c3c6, **c2, **pre}
        u = sorted({k for d in (pre, c2, c3c6) for k, r in d.items() if r["verdict"] in ("SURVIVED", "TIMEOUT")})
        if "--m4-universe" in sys.argv:
            carried_ans = json.loads((HERE / "m4_answers.json").read_text())
            u = sorted(set(carried_ans) | {k for k in u if k in comp and comp[k]["verdict"] != "KILLED"
                                           and k in set(lines(STATE / "keys-D3-u1a-surv.txt"))})
        for k in u:
            print(k, site(src[k]["mutant"]) if k in src else "")
        sys.exit(0)
    sys.exit(main())
