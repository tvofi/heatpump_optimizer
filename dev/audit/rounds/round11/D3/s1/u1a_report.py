#!/usr/bin/env python3
"""D3-s1 box D3-u1a: assemble REPORT.json and REPORT.md for this box's slice.

Metric: none of its own; it copies the RESULT lines of u1a_tally.py and
m4_u1a.py and the tabulate.py --tsv rows into finding.schema.json's shape.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/u1a_report.py
Reads state/u1a-tally.out, state/u1a-m4.out, state/u1a-m4.json (JSON part),
state/u1a-tab.tsv, REPORT-D3R.json. Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = HERE / "state"
R = "dev/audit/rounds/round11/D3/s1/"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
MACHINE = "box D3-u1a, Linux x86_64, nproc 4, 16 GB, Intel Xeon @ 2.10GHz, alone on the box"


def results(name):
    return dict(l.split("RESULT ", 1)[1].split("=", 1) for l in (S / name).read_text().splitlines()
                if l.startswith("RESULT "))


def main() -> int:
    t = results("u1a-tally.out")
    m4r = results("u1a-m4.out")
    txt = (S / "u1a-m4.json").read_text()
    m4 = json.JSONDecoder().raw_decode(txt)[0]
    tab = [l.split("\t") for l in (S / "u1a-tab.tsv").read_text().splitlines() if l.count("\t") >= 7]
    mine = {k.strip() for k in (S / "keys-D3-u1a.txt").read_text().split()}
    surv = [r for r in tab if r[4] == "SURVIVED" and r[0] in ("pre", "c2", "c3c6")]
    m3_nr = [f"{r[2]} {r[3]} {r[1]} ({r[0]}, carried fast-net survivor outside this box's key slice; full net not driven by box D3-u1a)"
             for r in surv if r[6] == "-"]
    killed_full = [r for r in tab if r[0] == "pre" and r[1] in mine and r[6] == "KILLED"]
    d3r = json.loads((HERE / "REPORT-D3R.json").read_text())
    pre_res = {p.stem for p in (S / "results" / "pre").glob("*.json")}
    # M2 not_reached groups: unpinned keys of u1_keys.txt not yet driven, by file
    import sys
    sys.path.insert(0, str(HERE))
    import prescreen as ps
    km = {ps.key(m): m for m in ps.unpinned()}
    rest = sorted(set(km) - pre_res)
    byfile = Counter(km[k]["file"].rsplit("/", 1)[1] for k in rest)
    lo, hi = "000221f3921dd956", "3daa55123b452546"
    m2_nr = [f"custom_components/heatpump_optimizer/{f}: {n} unpinned sites not pre-screened here "
             f"(keys outside [{lo},{hi}), another box's slice of the RESUME split; not driven by box D3-u1a)" for f, n in sorted(byfile.items())]
    ex2 = len(pre_res & set(km))
    assert ex2 + len(rest) == len(km)
    note = f"provisional: true; {MACHINE}; load1 0.5-1.3 during K1/K2; thread_factor 1.00"
    prescreened = [{"key": x["key"], "patch": f"{x['file']}:{x['line']}: {x['old']} -> {x['new']}",
                    "kind": x["kind"], "symbol": x["symbol"], "closure_scripts_run": x["drivers_run"],
                    "killed_by": [], "scripts_executing_line_unmutated": x["executed_by"],
                    "m4_should_have_failed": x["should_fail"]} for x in m4]
    cov = [
        {"step": "D3.M2",
         "enumerator": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned",
         "universe": len(km), "examined": ex2, "not_reached": m2_nr,
         "redispatched": [{"item": "C2", "state": "examined"}, {"item": "C6", "state": "examined"}],
         "evidence": (f"PYTHONPATH=tests/hastub python3 {R}u1a_tally.py -> this box's slice "
                      f"(state/keys-D3-u1a.txt, 309 keys, sha256 8f30aae5ec9f17c0...): pre_driven={t['pre_driven']}, "
                      f"killed={t['pre_killed']}, survived={t['pre_survived']}, timeout={t['pre_timeout']}, "
                      f"skipped_by_reach={t['pre_skipped_by_reach']}, unparseable={t['pre_unparseable']}; "
                      f"examined {ex2} = 24 carried (boxes local/D3R) + 309 this box. C2/C6: carried runs (REPORT-D3R.json).")},
        {"step": "D3.M3",
         "enumerator": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\\tSURVIVED\\t' | grep -P '^(pre|c2|c3c6)\\t'",
         "universe": len(surv), "examined": len(surv) - len(m3_nr), "not_reached": m3_nr,
         "redispatched": [{"item": "C3", "state": "not_reached"}, {"item": "C5", "state": "examined"}],
         "evidence": (f"prescreen.py complete --src pre --keys state/keys-D3-u1a-surv.txt (no early stop over the full closure): "
                      f"complete_driven={t['complete_driven']}, killed={t['complete_killed']} "
                      f"(features.py {t.get('complete_every_kill[tests/features.py]')}, entities.py "
                      f"{t.get('complete_every_kill[tests/entities.py]')}, harness_headers.py "
                      f"{t.get('complete_every_kill[tests/harness_headers.py]')}, every-kill), survived={t['complete_survived']}; "
                      f"plus 2 carried completes (both KILLED). C3 (GATE_SCOPE=full GOLDEN_MODE=drift gate on the top six) is box D3-top6's. "
                      f"C5: REPORT.md written by this box.")},
    ]
    def carried(step):
        c = dict(next(x for x in d3r["coverage"] if x["step"] == step))
        if isinstance(c["evidence"], list):
            c["evidence"] = " | ".join(f"{e['command']} -> {e['value']}" for e in c["evidence"])
        c["evidence"] = "Carried unchanged from boxes local/D3R (REPORT-D3R.json); box D3-u1a measured nothing in this step. " + c["evidence"]
        return c
    nk = len(killed_full)
    cov = [carried("D3.M1")] + cov + [
        {"step": "D3.M4", "enumerator": cov[1]["enumerator"], "universe": len(surv), "examined": len(surv),
         "not_reached": [], "redispatched": [],
         "evidence": (f"PYTHONPATH=tests/hastub python3 {R}m4_u1a.py -> survivors={m4r['survivors']} answered (line, file, "
                      f"check that should have failed; executed_by_none={m4r['executed_by_none']}); {nk} slice survivors the full "
                      f"net killed are answered by their killing driver (REPORT.json full_net_killed); the {len(surv) - len(m4) - nk} "
                      f"carried survivors are answered in m4_answers.json (boxes local/D3R).")},
        carried("D3.M5")]
    assert len(m4) + nk + 35 == len(surv)
    nf = [
        {"claim": "Null control: the fast net LIVES on the unmutated tree on this box",
         "command": f"PYTHONPATH=tests/hastub python3 {R}prescreen.py null", "value": "null_verdict=LIVES over 16 drivers (state/u1a-r2-null.out)"},
        {"claim": "Positive control: both ledger-pinned sites are KILLED on this box",
         "command": f"PYTHONPATH=tests/hastub python3 {R}prescreen.py run --anchors {R}posctl_anchors.txt --sub posctl-D3-u1a-r2",
         "value": "2/2 KILLED by tests/manual_plan.py (state/u1a-r2-posctl.out)"},
        {"claim": f"{t['pre_killed']} of 309 slice mutants are pinned by the fast net (closure fast scripts + env_drift --all)",
         "command": f"PYTHONPATH=tests/hastub python3 {R}u1a_tally.py",
         "value": "first kill: " + ", ".join(f"{k[15:-1]} {v}" for k, v in t.items() if k.startswith("pre_first_kill"))},
        {"claim": f"{t['complete_killed']} of 236 fast-net survivors are pinned by the full closure (slow scripts)",
         "command": f"PYTHONPATH=tests/hastub python3 {R}u1a_tally.py --tsv | grep -P '^complete.*\\tKILLED\\t'",
         "value": f"features.py kills {t.get('complete_every_kill[tests/features.py]')}; --drop-driver tests/features.py moves complete_killed {t['complete_killed']} -> 6 (perturbation, down)"},
        {"claim": "M4: every full-net survivor's line has an answer; 177 of 178 lines are executed by at least one gate script unmutated (asserted on by none)",
         "command": f"PYTHONPATH=tests/hastub python3 {R}m4_u1a.py",
         "value": f"survivors={m4r['survivors']}, executed_by_none={m4r['executed_by_none']}; --drop-driver tests/features.py -> executed_by_none=39 (up)"},
    ]
    exposure = (d3r.get("exposure", "") + " Box D3-u1a: read COMMON.md, D3.md, finding.schema.json, the seat's own carried "
                "harnesses/state/REPORT.json; no docs/ or GitHub read.")
    harn = sorted(set(d3r["harnesses"]) | {R + "u1a_tally.py", R + "m4_u1a.py", R + "u1a_report.py"})
    rep = {"dimension": "D3", "baseline_sha": BASE, "report_path": R + "REPORT-D3-u1a.md", "exposure": exposure,
           "coverage": cov, "unfinished": [], "findings": [], "non_findings": nf, "harnesses": harn, "leads": [],
           "box": "D3-u1a",
           "slice_tally": {k: v for k, v in t.items() if not k.startswith(("load1", "thread"))},
           "prescreened_survivors_for_D3-top6_full_gate": prescreened,
           "full_net_killed": [{"key": r[1], "line": r[2], "kind": r[3], "killed_by": r[7]} for r in killed_full],
           "timing_note": note}
    (HERE / "REPORT-D3-u1a.json").write_text(json.dumps(rep, indent=1) + "\n")
    md = [f"# D3-s1 round 11, box D3-u1a slice (D3.M2 keys [{lo},{hi}), D3.M3 full net)", "",
          f"Baseline {BASE}. {MACHINE}. Timing {note}.", "",
          "## Method", "K0 key file state/keys-D3-u1a.txt (309 keys, sha256 8f30aae5ec9f17c0...). K1 prescreen.py run --sub pre "
          "(fast closure scripts + env_drift --all, first-kill stop), 4 workers, fresh tree per mutant. K2 prescreen.py complete "
          "(full closure, no early stop) on the 236 fast-net survivors. Controls on this box: null LIVES (16 drivers), positive 2/2 KILLED.", "",
          "## Tally", "| net | driven | killed | survived | timeout | skipped by reach | unparseable |", "|---|---|---|---|---|---|---|",
          f"| fast (pre) | {t['pre_driven']} | {t['pre_killed']} | {t['pre_survived']} | {t['pre_timeout']} | {t['pre_skipped_by_reach']} | {t['pre_unparseable']} |",
          f"| full (complete) | {t['complete_driven']} | {t['complete_killed']} | {t['complete_survived']} | {t['complete_timeout']} | {t['complete_skipped_by_reach']} | {t['complete_unparseable']} |", "",
          "Kills by driver: " + "; ".join(f"{k} {v}" for k, v in t.items() if "kill[" in k), "",
          "## Findings", "None from this box: D3.md step 3 makes the full-net survivors candidates; the GATE_SCOPE=full GOLDEN_MODE=drift gate is box D3-top6's (RESUME brief K2).", "",
          f"## Prescreened survivors (D3.M4 answers), {len(m4)}",
          "| key | line | kind | symbol | patch | scripts executing the line | check that should have failed |", "|---|---|---|---|---|---|---|"]
    for x in m4:
        md.append(f"| {x['key']} | {x['file'].rsplit('/', 1)[1]}:{x['line']} | {x['kind']} | {x['symbol']} | "
                  f"`{x['old'][:60]}` -> `{x['new'][:40]}` | {len(x['executed_by'])} | {x['should_fail']} |".replace("||", "| |"))
    md += ["", "## Non-findings"] + [f"- {n['claim']}: `{n['command']}` -> {n['value']}" for n in nf]
    md += ["", "## Coverage"] + [f"- {c['step']}: universe {c['universe']}, examined {c['examined']}, not_reached {len(c['not_reached'])} item(s)/group(s)" for c in cov]
    md += ["", "## Harnesses"] + [f"- {h}" for h in harn] + ["", "## Exposure", exposure, ""]
    (HERE / "REPORT-D3-u1a.md").write_text("\n".join(md))
    print(f"RESULT survivors={len(m4)} m2_examined={ex2} m3_universe={len(surv)} m3_not_reached={len(m3_nr)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
