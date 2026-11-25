#!/usr/bin/env python3
"""Render the one D3 wave verifier record from every votes-stage<N>.json: verify.json (all votes, each tagged with
its stage) and verify.md (per-stage coverage, counts, method, the non-verify votes, and the whole vote table)."""
import json, pathlib, shutil, collections, datetime
D = pathlib.Path("<seat-dir>")
OUT = D / "rec/dev/audit/rounds/round11/D3/wave-verify"
OUT.mkdir(parents=True, exist_ok=True)
stages = sorted((json.load(open(p)) for p in D.glob("votes-stage[1-9]*.json")), key=lambda s: s["stage"])
votes, cover = [], []
for s in stages:
    for v in s["votes"]:
        votes.append(dict(v, stage=s["stage"]))
    cover.append({"stage": s["stage"], "boxes": s["boxes"], "findings": len(s["votes"]),
                  "votes": dict(collections.Counter(v["vote"] for v in s["votes"]))})
json.dump({"dimension": "D3", "round": 11, "unit": "D3 u1 full-gate wave (d3wave PLAN), finder boxes D3-g01..g47",
           "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692", "stages": cover, "votes": votes},
          open(OUT / "verify.json", "w"), indent=1)
for sub in ("v1", "v1m", "v2"):
    shutil.copytree(D / sub, OUT / "out" / sub, dirs_exist_ok=True)
shutil.copy(D / "v3.json", OUT / "out" / "v3.json")
for h in ("candidates.py", "run_probes.py", "v1_analyse.py", "run_v2.py", "v3.py", "compose.py", "render.py"):
    shutil.copy(D / h, OUT / "harness" / h) if (OUT / "harness").exists() else ((OUT / "harness").mkdir(), shutil.copy(D / h, OUT / "harness" / h))
import re as _re
_HOME = str(pathlib.Path.home())
for f in list((OUT / "out").rglob("*")) + list((OUT / "harness").rglob("*")):
    if f.is_file():
        t = f.read_text()
        if _HOME in t:
            t = _re.sub(_re.escape(str(D)) + r"/v2tree\d", "<clone>", t)
            t = t.replace(str(D), "<seat-dir>").replace("<d3wave-dir>", "<d3wave-dir>")
            t = _re.sub(_re.escape(_HOME) + r"/[^ \"'\\]*", "<home>/...", t)
            f.write_text(t)
tot = collections.Counter(v["vote"] for v in votes)
L = ["# D3 wave verifier record, round 11 (one verifier, three lenses)", "",
     "Unit: the D3 u1 full-gate wave's gate survivors (`gate_survivors` of each `REPORT-D3-gNN.json`), one vote per mutant key. "
     "Ids are `D3-wave-<key>` until the consolidation step assigns D3-s1-72..99 by file and gap kind (d3wave PLAN, final ruling); "
     "a consolidated finding inherits the votes of the keys it lists. Equivalent candidates and KILLED keys are non-findings and get no vote.",
     "", "Baseline tree: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with the harvested D3 evidence copied over it. Host: 8-core Apple "
     "silicon macOS, CPython 3.14 from venv-ci, numpy 2.5.5, scipy 1.18.1; load1 30-70 from other seats, so every number used is a count or a "
     "solver value, never a timing.", "",
     "Not run here, by the brief: the judge, dedup and the class sweep (they wait for all 47 boxes).", "",
     "## Stages", "", "| stage | boxes | findings | votes |", "|---|---|---|---|"]
for s in cover:
    L.append(f"| {s['stage']} | {', '.join(b.replace('D3-', '') for b in s['boxes'])} | {s['findings']} | {s['votes']} |")
L += ["", f"Total: {len(votes)} findings; {dict(tot)}.", "",
      "## Method", "",
      "- **V1 reproduce.** Every probe re-run as its header says (`PYTHONPATH=tests/hastub python3 <probe>`, plus `--mutant` for the "
      "two-run probes of D3-g33) in the baseline tree; output in `out/v1/`, `out/v1m/`. Moved = baseline and mutant arm values the "
      "probe prints differ (`harness/v1_analyse.py`); else every value the finder stated is reproduced and the record's two values "
      "differ. Null control = the probe's null lines, which must not move. Leave-one-out does not apply: no aggregate claim.",
      "- **V2 independent.** `harness/run_v2.py` writes the one-line mutant (fullgate's own mutant record, refusing a moved line) into "
      "the production file of a private clone and re-runs the scenario. Metric: whether the finder's in-memory perturbation is the real "
      "source mutant. Most probes refuse the on-disk mutant because they rebuild the mutated body from the source text, so their "
      "mutant arm is the literal edit (faithful by construction); probes that patch a module global in both arms are inconclusive "
      "by construction; the rest are compared arm by arm.",
      "- **V3 reach and class.** `harness/v3.py`: traced reach from the wave's REACH.tsv; production references to the mutated symbol "
      "outside its definition; whether the function names a `tests/ha_contract.py` DIVERGENT stub symbol; the seam_rule's shape "
      "(executed only when it is a plain read-only grep/awk pipeline); the five record fields (claim, evidence, harness, metric, "
      "perturbation), all present on every record. Class: I1 for every test-gap key, as VD3L corrected `new` before.",
      "- **Gate.** The full gate was not re-taken (about 1 h per key on a quiet 4-core box; this host is shared at load 30-70). "
      "Every vote cites the box's gate record. Attack carried on every vote: the stripped finder tree's null is red on "
      "`closure.py selftest`, `entities.py` and `harness_headers.py`, so a kill by those three only shows as a rising fail count; "
      "the judge's runners should re-take the gate on an unstripped tree.",
      "- **Severity.** Highs whose consequence is a published attribute or report key, or a derate that re-learns, are graded medium "
      "(5); keys with no production reference would be cut to nit (none found by the scan; one cut by its own reach line).", "",
      "## Votes other than verify", "", "| stage | key | box | site | vote | severity | value | why |", "|---|---|---|---|---|---|---|---|"]
for v in votes:
    if v["vote"] != "verify":
        why = "; ".join(a for a in v["attacks"] if a.startswith(("read by hand", "severity: claimed", "reach:", "null control: MOVES")))
        L.append(f"| {v['stage']} | {v['key']} | {v['box']} | {v['site'].split('/')[-1]} | {v['vote']} | {v['severity']} | "
                 f"{(v['value'] or '').replace('|', '/')[:160]} | {why.replace('|', '/')[:300]} |")
L += ["", "## All votes", "", "| stage | key | box | site | vote | severity | V1 | V2 |", "|---|---|---|---|---|---|---|---|"]
for v in votes:
    L.append(f"| {v['stage']} | {v['key']} | {v['box']} | {v['site'].split('/')[-1]} | {v['vote']} | {v['severity']} | "
             f"{(v['value'] or '').replace('|', '/')[:110]} | {v['independent_value'].split(':')[0][:40]} |")
(OUT / "verify.md").write_text("\n".join(L) + "\n")
print(OUT, len(votes), dict(tot))
