#!/usr/bin/env python3
"""Compose the D3 wave verifier record (votes per candidate) from V1, V2 and V3 outputs, for the boxes named.
Usage: compose.py <stage-number> <boxes comma list> -> writes votes-stage<N>.json beside this script."""
import json, pathlib, sys, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import v1_analyse as A
D = pathlib.Path("<seat-dir>")
stage, boxes = int(sys.argv[1]), sys.argv[2].split(",")
cands = [c for c in json.load(open(D / "candidates.json")) if c["box"] in boxes]
v3 = {o["key"]: o for o in json.load(open(D / "v3.json"))}
gate, RECS = {}, {}
for f in (D / "rec/dev/audit/rounds/round11/D3/s1").glob("REPORT-D3-g*.json"):
    for c in json.load(open(f))["gate_survivors"]:
        gate[c["key"]] = c.get("gate") or {}
        RECS[c["key"]] = c


def v2_reading(c, a1):
    p = D / "v2" / f"{c['key']}.json"
    if not p.exists():
        return None, "not taken"
    r = json.load(open(p))
    if not r.get("applied"):
        return None, f"mutant not applied: {r.get('note')}"
    clean = A.arm_pairs([l[7:] for l in json.load(open(D / 'v1' / f"{c['key']}.json"))["stdout"].splitlines() if l.startswith("RESULT ")])
    disk = A.arm_pairs([l[7:] for l in r["stdout"].splitlines() if l.startswith("RESULT ")])
    moving = {k: v for k, v in clean.items() if "null" not in k.lower() and None not in v and not A.same(*v)}
    tail = (r.get("stderr") or "").strip().splitlines()[-1:] or [""]
    if r["rc"] != 0 and ("anchor" in tail[0] or "not '" in tail[0] or "AssertionError" in tail[0]):
        return None, (f"faithful by construction: with the mutant on disk the probe refuses ({tail[0][:120]}), "
                      "so its mutant arm is the literal source edit of that line")
    if r["rc"] != 0:
        return None, f"probe rc {r['rc']} with the mutant on disk ({tail[0][:140]}): inconclusive"
    faithful = [k for k, v in moving.items() if k in disk and disk[k][0] is not None and A.same(disk[k][0], v[1])]
    if moving and not faithful:
        return None, (f"inconclusive by construction: 0 of {len(moving)} moving arms change with the mutant on disk, "
                      "because the probe sets the perturbed value explicitly in both arms (patched global or recompiled body)")
    if not moving:
        return None, "no parsed moving arm to compare"
    return (len(faithful), len(moving)), f"{len(faithful)} of {len(moving)} moving arms read the mutant value in the baseline arm with the mutant on disk (rc 0)"


SEV_OVERRIDE = {
    "ac6bedc70bb82ff7": ("medium", "the consequence is a published attribute (manual_override reads None); no actuator or plan moves"),
    "6aeb83e5435c9cac": ("medium", "the consequence is a missing report key (grid_fee_sek) in the contract comparison; no control path reads it"),
    "d06a2d8e53342785": ("medium", "the consequence is the contract comparison's monthly-average entry vanishing from a report; no control path reads it"),
    "a66e107749d0ae11": ("medium", "the consequence is the published dhw_required_temperature_now value; the plan itself is unchanged"),
    "4aac8e694ddc5dfe": ("medium", "zero-duty buckets re-learn after a restart: a transient derate (1.0 -> 0.8571) until re-measured, not a lasting fault"),
}

_FLOAT = ("the finder's boundary input does not land on the boundary on this host (macOS arm64 CPython/numpy): "
          "the probe's hunt found no hitting input, so neither arm moves here; solver floats do not reproduce across "
          "BLAS builds, so this is a non-reproduction to re-take on a Linux x86 box, not a refute")
MANUAL = {
    "b1a8d3056bf42597": ("weaken", "differing_pmax_nonpos=120/120 (max_delta 3 kW) but differing_pmax_pos=0/120; null 0/60", "nit",
                         "the mutant moves the plan only at p_total_max <= 0, which the probe's own reach line says is not established as reachable"),
    "62abf71b9686f2b8": ("verify", "guess_max_abs_diff=0.2358 at a price mean exactly PRICE_MEAN_GUESS_EPS; null_ordinary_prices_diff=0", None,
                         "single-run probe: the moved metric is guess_max_abs_diff, the null is ordinary prices"),
    "64f3ef1feaaf7bc9": ("unresolved", "hunt_hit=0 of 14087 evaluations; key case not reached", None, _FLOAT),
    "d661d68f54982097": ("unresolved", "key_tapped_tau=200.00000000000887 (not 200); key_completed baseline False = mutant False", None, _FLOAT),
    "4da9d281d4714565": ("unresolved", "hunt_hit=0 of 28215 evaluations; key case not reached", None, _FLOAT),
}

votes = []
for c in cands:
    k = c["key"]
    a1 = A.analyse(c) if (D / "v1" / f"{k}.json").exists() else None
    o = v3[k]
    g = gate.get(k, {})
    attacks = []
    if a1 is None or a1["rc"] != 0:
        vote, value = "unresolved", None
        rep = "probe not re-run" if a1 is None else f"probe rc {a1['rc']}: {a1['stderr_tail'][-160:]}"
    else:
        moved = a1["moved_pairs"] + a1["moved_lines"]
        rep = (f"rc 0; {a1['moved_pairs']} of {a1['arm_pairs']} arm pairs moved (+{a1['moved_lines']} moved= lines); "
               f"null pairs moved {a1['null_moved']} of {a1['null_pairs']}; finder's stated values matched {a1['matched']} of {a1['pairs']} ({a1['basis']})")
        by_values = (not moved and a1["pairs"] and a1["matched"] == a1["pairs"]
                     and str(c.get("baseline_value")) != str(c.get("mutant_value")))
        if moved:
            value = f"V1 {a1['moved_pairs']} arm pair(s) moved, null moved {a1['null_moved']}; e.g. {a1['moved_example']}"
            vote = "verify"
        elif (D / "v1m" / f"{k}.json").exists():
            pr = (RECS[k].get("probe") or {})
            def kv(s):
                return dict(l[7:].split("=", 1) for l in s.splitlines() if l.startswith("RESULT ") and "=" in l)
            b0 = kv(json.load(open(D / "v1" / f"{k}.json"))["stdout"])
            m0 = kv(json.load(open(D / "v1m" / f"{k}.json"))["stdout"])
            mk, nk = pr.get("metric"), pr.get("null_metric")
            mb, mm = b0.get(mk), m0.get(mk)
            nb, nm = b0.get(nk), m0.get(nk)
            moved = int(mb is not None and mm is not None and mb != mm)
            null_ok2 = nb is not None and nb == nm
            value = f"V1 {mk}: baseline run {mb} vs --mutant run {mm} (finder {pr.get('baseline_value')} -> {pr.get('mutant_value')}); null {nk}: {nb} vs {nm}"
            rep += f"; two-run probe: {value}"
            vote = ("verify" if null_ok2 else "weaken") if moved else "unresolved"
            attacks.append(f"perturbation (--mutant run): {'moves' if moved else 'does NOT move'} {mk}; null {'holds' if null_ok2 else 'MOVES'}")
        elif by_values:
            value = f"V1 every finder-stated value reproduced ({a1['matched']} of {a1['pairs']}); baseline {str(c.get('baseline_value'))[:120]} vs mutant {str(c.get('mutant_value'))[:120]}"
            vote = "verify"
            moved = 1
        else:
            value = None
            vote = "unresolved"
            rep += f"; output lines {a1['result_head'][:4]}; unmatched {a1['unmatched'][:3]}"
        attacks.append(f"perturbation: {'moves' if moved else 'does NOT move'} the probe's metric")
        null_holds = a1["null_moved"] == 0 and a1["null_ok"] is not False
        attacks.append(f"null control: {'holds' if null_holds else 'MOVES or unparsed'} ({a1['null_pairs']} null pair(s) moved {a1['null_moved']}; null lines {a1['null_lines'][:2]})")
        if a1["null_moved"] and vote == "verify":
            vote = "weaken"
        attacks.append(f"contention: load1 {a1['load1']} on an 8-core macOS host; counts only, no timing claim relied on")
    if k in MANUAL:
        vote, value, sev_m, note = MANUAL[k]
        attacks.append(f"read by hand: {note}")
        if sev_m:
            o = dict(o, severity_claimed=sev_m)
    v2n, v2s = v2_reading(c, a1)
    if v2n is not None and vote in ("verify", "weaken"):
        f_, m_ = v2n
        if m_ and f_ == 0:
            vote = "refute"
            value = (value or "") + f"; V2 on-disk mutant moves 0 of {m_} arms"
        elif m_ and f_ < m_ and vote == "verify":
            vote = "weaken"
    attacks.append(f"perturbation fidelity (V2): {v2s}")
    gm = g.get("more_fails_than_null")
    attacks.append(f"gate mode: box gate {g.get('verdict')} with failed {len(g.get('failed_scripts') or [])} script(s), new vs null {g.get('killed_by')}, "
                   f"more fail lines than null {gm}; the stripped tree's null is red on closure.py selftest, entities.py and harness_headers.py, "
                   "so a kill by those three shows only as a rising fail count -- not re-taken here (full gate owed to the judge's runners)")
    reach_ok = o["prod_refs"] > 0 or o["function"] not in ("<module>",) and o["prod_refs"] > 0
    reach = (f"traced reach {o['reach']} by {len([x for x in o['hit_by'].split(',') if x])} script(s); "
             f"{o['prod_refs']} production reference(s) to {o['symbol']} outside its definition (e.g. {o['prod_ref_sample'][:2]}); "
             f"divergent stub symbols in the function: {o['divergent_stub'] or 'none'}")
    sev = o["severity_claimed"] or "low"
    if k in SEV_OVERRIDE and vote in ("verify", "weaken"):
        sev, why = SEV_OVERRIDE[k]
        vote = "weaken"
        attacks.append(f"severity: claimed {o['severity_claimed']}, graded {sev} by consequence: {why}")
    elif sev in ("high", "medium"):
        attacks.append(f"severity: claimed {sev}, kept: {'actuator or real-HA failure path' if sev == 'high' else 'not re-graded beyond reach in this stage'}")
    if o["prod_refs"] == 0 and vote in ("verify", "weaken"):
        vote, sev = "weaken", "nit"
        attacks.append("reach: no production reference to the mutated symbol; severity cut to nit")
    elif o["divergent_stub"] and vote == "verify":
        vote = "weaken"
        attacks.append(f"reach: the function names DIVERGENT stub symbols {o['divergent_stub']}: real-HA reach unproven")
    votes.append({"id": f"D3-wave-{k}", "key": k, "box": c["box"], "site": f"{o['file']}:{o['line']}", "patch": f"{o['old'].strip()} -> {o['new'].strip()}",
                  "title": o["title"], "vote": vote, "severity": sev, "severity_claimed": o["severity_claimed"], "value": value,
                  "metric_definition": "V1: baseline vs mutant arm values the probe prints (RESULT lines), counted as moved pairs; "
                                       "V2: of those moving arms, how many read the mutant value in the baseline arm with the one-line mutant written to the source file",
                  "method": f"V1 finder probe re-run as its header says in baseline tree 92d38ecb64 (+ D3 evidence from the harvest); V2 own on-disk patcher; V3 REACH.tsv, reference scan, ha_contract DIVERGENT scan; gate record {g.get('verdict')} from the box (not re-taken)",
                  "attacks": attacks, "reproduced": rep, "independent_value": v2s, "reachable": reach,
                  "class": "I1 (a guard or behaviour whose mutation leaves the gate green)" + ("; class_guess 'new' corrected" if o["class_guess"] == "new" else
                                (f"; class_guess {o['class_guess']!r} names the product mechanism, the suite gap itself is I1" if o["class_guess"] not in (None, "I1") else "")),
                  "seam_rule_enumerates": o["seam_kind"] or "no seam_rule on the record",
                  "test_gap_mutation": f"{o['file']}:{o['line']} `{o['old'].strip()}` -> `{o['new'].strip()}` (production file)",
                  "missing_fields": o["missing_fields"]})
json.dump({"stage": stage, "boxes": boxes, "votes": votes}, open(D / f"votes-stage{stage}.json", "w"), indent=1)
from collections import Counter
print(len(votes), Counter(v["vote"] for v in votes), Counter(v["severity"] for v in votes))
