#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/compose.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
"""Compose the D3 wave judge record from the judge's own measurements:
analysis.json (probe re-runs), gatecmp.json (gate logs vs box null), dedup.json (cross runs), the verifier's votes,
and hand rulings (hand.json). Writes JUDGE.json and the verdict table rows."""
import os, json, re, sys, pathlib, collections
WORK = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
master = json.load(open(WORK / "master.json"))
ana = json.load(open(WORK / "analysis.json"))
gate = json.load(open(WORK / "gatecmp.json"))
dd = json.load(open(WORK / "dedup.json"))
hand = json.load(open(WORK / "hand.json")) if (WORK / "hand.json").exists() else {}
merged = {m["id"].replace("D3-wave-", ""): m for m in dd["merged"]}
SEVR = ["nit", "low", "medium", "high", "critical"]
G = {"CMP_BOUND": "boundary", "GUARD_OFF": "guard", "BOOLOP": "guard", "RETURN_DEL": "guard", "CLAMP_DROP": "clamp", "CONST": "constant"}
I1 = "A mutation kill miscounted, or a guard whose deletion leaves the gate green"
verdicts = []
for m in master:
    k = m["key"]; a = ana.get(k, {}); g = gate.get(k, {}); h = hand.get(k, {})
    f = m["rec"].get("finding", m["rec"])
    kind = m["rec"]["site"].split()[-1]
    row = {"id": f"D3-wave-{k}", "key": k, "box": m["box"], "site": m["site"].replace("custom_components/heatpump_optimizer/", ""),
           "patch": m["patch"], "gap_kind": G.get(kind, kind), "mutant_kind": kind,
           "title": f.get("title"), "votes": [f"{m['vote']} ({m['vsev']})"], "severity_claimed": m["csev"]}
    if k in merged:
        row.update({"verdict": "merged", "into": merged[k]["into"], "note": f"merged into {merged[k]['into']}: {merged[k]['number']}"})
        verdicts.append(row); continue
    moved = bool(a.get("moved_pairs") or a.get("moved_lines"))
    rc_ok = a.get("rc") in (0, [0, 0])
    def counts(lines):
        return {re.sub(r"^\d+ of \d+ ", "", l): int(l.split()[0]) for l in lines}
    mc, nc = counts(g.get("summary", [])), counts(g.get("null_summary", []))
    new_gate = [f"{s}: {n} > null {nc.get(s, 0)}" for s, n in mc.items() if n > nc.get(s, 0)]
    new_gate += [l for l in g.get("new_exact", []) if l.startswith(">>> FAILED") or "Traceback" in l or "TIMEOUT" in l]
    summ_same = True
    gate_txt = ("gate log vs box null: no failed script beyond the null's, no script's failing-check count above the null's ("
                + "; ".join(g.get("summary", [])) + ")" if not new_gate else f"gate log vs box null: {new_gate[:3]}")
    ex = a.get("moved_example") or (a.get("moved_lines") or [None])[0]
    num = f"re-run rc {a.get('rc')}; {a.get('moved_pairs', 0)} arm pair(s) moved (e.g. {ex}); null pairs moved {a.get('null_moved', 0)} of {a.get('null_pairs', 0)}; RESULT lines {'identical to' if a.get('same_as_verifier') else 'differ from'} the verifier's run"
    sev = h.get("severity", m["vsev"])
    if h.get("verdict"):
        verdict = h["verdict"]
    elif not a:
        verdict = "unreproduced"
    elif new_gate or not summ_same:
        verdict = "refuted"
    elif not (rc_ok and moved):
        verdict = "unreproduced"
    elif SEVR.index(sev) < SEVR.index(m["csev"]):
        verdict = "weakened"
    else:
        verdict = "verified"
    stop = h.get("stop_rule_class") or ("bug" if sev in ("medium", "high", "critical") else "hygiene")
    row.update({"verdict": verdict, "severity": sev, "value": h.get("value", num), "gate": gate_txt,
                "stop_rule_class": stop, "class": "I1", "class_mechanism": I1,
                "note": h.get("note", f"load1 {a.get('load1')}, thread_factor {a.get('thread_factor')}; counts only, no timing relied on")})
    verdicts.append(row)
json.dump({"round": 11, "dimension": "D3", "unit": "D3 u1 full-gate wave (47 boxes)", "verdicts": verdicts}, open(WORK / "JUDGE.json", "w"), indent=1)
c = collections.Counter(v["verdict"] for v in verdicts)
print(dict(c))
print(collections.Counter(v.get("severity") for v in verdicts if v["verdict"] in ("verified", "weakened")))
