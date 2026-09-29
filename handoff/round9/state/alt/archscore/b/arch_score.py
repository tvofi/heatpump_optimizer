#!/usr/bin/env python3
"""Prototype architecture score: a Pareto gate plus a weighted log-ratio score.

    python3 arch_score.py ROOT [--ref REF.json]      score one tree against the reference vector
    python3 arch_score.py --delta BASE.json CUR.json  gate + delta-S of one change
    python3 arch_score.py --calibrate                 every labelled case; exit 0 only if all classify right
    python3 arch_score.py --trajectory                S along the last 20 first-parent merges to the reference
    python3 arch_score.py --sensitivity               calibration with each weight at 0.5x and 2x

Definition (PRE-STUDY.md section 4):

* The vector is SCORE_METRICS below, measured by measure_vec.py (the pinned tests/structure.py
  at 7952d8f9, the a3 metric modules, the a1 probes). Retired and report-only rows are carried
  for the report and never enter the gate or the score.
* Gate: a change is admissible only if no SCORE_METRIC rises (tolerance 0; every metric is a
  deterministic static count, so there is no noise to allow for).
* Score: S = sum_i w_i * log2((ref_i + 1) / (cur_i + 1)). Halving a metric is worth w_i whatever
  its scale; +1 keeps a metric at its zero target finite. A change's delta-S is S(cur) - S(base).
* Weights: weights.json, frozen (sha256 in weights.sha256) before the first calibration run,
  w = log2(1 + defect cost in hours) of the register class the metric guards, floor 1.0.
  They are not fitted to the corpus.
* Verdict of a change: IMPROVES if admissible and delta-S > 0; NULL if admissible and delta-S == 0;
  otherwise WORSENS (a gate failure, or delta-S < 0).

Calibration acceptance: GOOD -> IMPROVES, BAD -> WORSENS, NULL -> NULL, NEUTRAL -> not IMPROVES
(a change the record says moved a defect without removing it must not be scored as a gain).
A metric missing (None) on either side of a historic case is dropped from that case and listed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEIGHTS = json.loads((HERE / "weights.json").read_text())
REF_VEC = HERE / "planted" / "_base.json"

# metric -> (guarded register class, the property it prices)
SCORE_METRICS = {
    "hub_solve_writes": ("N-shared-config", "writes into the live config hubs reachable from the solve"),
    "shared_inplace_writes": ("N-shared-config", "in-place writes of operation values into long-lived shared objects"),
    "a1_dup_pairs": ("P2+P3", "function pairs sharing an AST-identical statement window, package-wide"),
    "untyped_payload_keys": ("P6", "coordinator payload keys published with no declared type"),
    "dead_by_reachability": ("N-structure-blind", "members no production root reaches"),
    "family_splits": ("N-name-sort", "entity families the name sort splits"),
    "a1_coord_footprint": (None, "logical statements in the coordinator class plus every f(coord) free function"),
    "a1_coord_writers_multi": (None, "coordinator attributes written by more than one function, in or out of the class"),
    "private_reach": (None, "reads/writes of coordinator privates from outside it, writes x3"),
    "a1_import_cycle_modules": (None, "modules in an import cycle, function-scope imports included"),
    "public_unused": (None, "public names nothing uses"),
}
V1_SWAP = {"a1_coord_footprint": "coord_footprint_v1", "a1_dup_pairs": "dup_pairs_v1",
           "a1_import_cycle_modules": "import_cycle_modules_v1"}
VERSION = "v1" if "--v0" not in sys.argv else "v0"
if VERSION == "v1":
    SCORE_METRICS = {V1_SWAP.get(k, k): v for k, v in SCORE_METRICS.items()}
    SCORE_METRICS["a1_params_over_10"] = (None, "functions with more than 10 parameters (the fragment-chain guard)")
REPORT_ONLY = ("pkg_loc", "public_surface", "a1_params_over_10", "a1_logical_max_fn",
               "xmodule_duplication", "import_cycles")
RETIRED = ("attrbag_classes_over_30", "classes_over_300", "const_modules_over_50", "coordinator_loc",
           "coordinator_methods", "coordinator_attrs", "coordinator_multiassigned_attrs", "max_class_loc",
           "internal_call_edges", "cross_seam_edges", "cut_dhw", "cut_fetch", "cut_grid", "cut_learning",
           "cut_views", "duplication_blocks", "functions_cc_over_15", "functions_cc_over_25", "max_cc",
           "max_method_loc", "methods_over_150", "methods_over_200", "local_imports", "dead_methods",
           "dead_top_level_symbols", "a1_private_reach")


def weights(scale: dict | None = None) -> dict:
    w = {m: WEIGHTS["floor"] for m in SCORE_METRICS}
    for cls in WEIGHTS["classes"].values():
        share = cls["cost_h"] / len(cls["metrics"])
        for m in cls["metrics"]:
            key = m if m in SCORE_METRICS else f"a1_{m}"
            key = V1_SWAP.get(key, key) if VERSION == "v1" else key
            w[key] = math.log2(1 + share)
    for m, f in (scale or {}).items():
        w[m] *= f
    return w


def term(w: float, ref: float, cur: float) -> float:
    return w * math.log2((ref + 1) / (cur + 1))


def delta(base: dict, cur: dict, w: dict | None = None) -> dict:
    w = w or weights()
    rises, terms, missing = [], {}, []
    for m in SCORE_METRICS:
        b, c = base.get(m), cur.get(m)
        if b is None or c is None:
            missing.append(m)
            continue
        if c > b:
            rises.append(f"{m} {b}->{c}")
        t = term(w[m], b, c)
        if t:
            terms[m] = round(t, 4)
    ds = round(sum(terms.values()), 4)
    admissible = not rises
    verdict = "IMPROVES" if admissible and ds > 0 else "NULL" if admissible and ds == 0 else "WORSENS"
    return {"admissible": admissible, "rises": rises, "dS": ds, "terms": terms,
            "missing": missing, "verdict": verdict}


def expected_ok(label: str, verdict: str) -> bool:
    return {"GOOD": verdict == "IMPROVES", "BAD": verdict == "WORSENS", "NULL": verdict == "NULL",
            "NEUTRAL": verdict != "IMPROVES"}[label]


def score_tree(vec: dict, ref: dict, w: dict | None = None) -> float:
    w = w or weights()
    return round(sum(term(w[m], ref[m], vec[m]) for m in SCORE_METRICS
                     if vec.get(m) is not None and ref.get(m) is not None), 4)


# ------------------------------------------------------------------ cases
def load(p: Path) -> dict:
    d = json.loads(p.read_text())
    if VERSION == "v1":
        extra = {"vec": HERE / "vec1", "planted": HERE / "planted1"}.get(p.parent.name)
        if extra is not None and (extra / p.name).exists():
            v1 = json.loads((extra / p.name).read_text())
            if "vec" in d:
                d["vec"] = {**d["vec"], **v1}
            else:
                d = {**d, **v1}
    return d


def cases() -> list[dict]:
    out = []
    vec = HERE / "vec"
    with open(HERE.parent / "a2" / "corpus.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            b, a = _full(vec, r["parent"]), _full(vec, r["sha"])
            if not (b.exists() and a.exists()):
                print(f"corpus case {r['sha'][:8]}: vector missing", file=sys.stderr)
                continue
            out.append({"id": r["sha"][:8], "set": "corpus", "label": r["label"], "cls": r["class"],
                        "circ": r["circ"], "desc": r["description"][:90], "base": load(b), "cur": load(a),
                        "loc_changed": _loc(r)})
    pl = HERE / "planted"
    for p in sorted(pl.glob("a[13]_*.json")):
        d = load(p)
        base = load(pl / f"{d['base']}.json")
        base = base.get("vec", base)
        out.append({"id": p.stem, "set": "planted", "label": d["label"], "cls": "", "circ": "no",
                    "desc": d["src"][:90], "base": base, "cur": d["vec"], "loc_changed": None})
    return out


def _full(vec: Path, sha: str) -> Path:
    hits = sorted(vec.glob(f"{sha[:8]}*.json"))
    return hits[0] if len(hits) == 1 else vec / f"{sha[:12]}.json"


SIZES = {}
if (HERE / "corpus_size.tsv").exists():
    for _r in csv.DictReader(open(HERE / "corpus_size.tsv"), delimiter="\t"):
        SIZES[_r["sha"]] = int(_r["prod_lines_changed"])


def _loc(r: dict) -> int | None:
    return SIZES.get(r["sha"][:8])


def calibrate(w: dict | None = None, quiet: bool = False) -> tuple[int, int, list[dict]]:
    rows = []
    for c in cases():
        d = delta(c["base"], c["cur"], w)
        ok = expected_ok(c["label"], d["verdict"])
        rows.append({**{k: c[k] for k in ("id", "set", "label", "cls", "circ", "desc")}, **d, "ok": ok})
    bad = [r for r in rows if not r["ok"]]
    if not quiet:
        print(f"{'case':44} {'set':8} {'label':8} {'verdict':9} {'adm':4} {'dS':>9}  ok  rises / top terms")
        for r in rows:
            top = sorted(r["terms"].items(), key=lambda kv: -abs(kv[1]))[:3]
            info = "; ".join(r["rises"][:3]) if r["rises"] else ", ".join(f"{k}{v:+.3f}" for k, v in top)
            print(f"{r['id'][:44]:44} {r['set']:8} {r['label']:8} {r['verdict']:9} {'y' if r['admissible'] else 'n':4} "
                  f"{r['dS']:>9.4f}  {'ok' if r['ok'] else 'XX'}  {info[:150]}"
                  + (f"  [missing: {','.join(r['missing'])}]" if r["missing"] else ""))
        n = len(rows)
        print(f"\nCALIBRATION {n - len(bad)}/{n} correct; misclassified: {', '.join(r['id'] for r in bad) or 'none'}")
        for st in ("planted", "corpus"):
            for lab in ("GOOD", "BAD", "NULL", "NEUTRAL"):
                sub = [r for r in rows if r["label"] == lab and r["set"] == st]
                if not sub:
                    continue
                blind = sum(1 for r in sub if not r["ok"] and r["verdict"] == "NULL")
                wrong = sum(1 for r in sub if not r["ok"] and r["verdict"] != "NULL")
                print(f"  {st:8} {lab:8} {sum(r['ok'] for r in sub):>3}/{len(sub):<3} blind {blind:>2}  wrong-way {wrong:>2}")
        print(f"version {VERSION}; metrics: {', '.join(SCORE_METRICS)}")
        print(f"weights.json sha256 {hashlib.sha256((HERE / 'weights.json').read_bytes()).hexdigest()}")
    return len(rows) - len(bad), len(rows), rows


def trajectory() -> None:
    ref = load(REF_VEC)
    chain = (HERE / "trajectory_chain.txt").read_text().split()
    print(f"{'merge':10} {'S':>9} {'dS':>9} verdict   rises")
    prev = None
    for sha in reversed(chain):
        v = load(_full(HERE / "vec", sha))
        s = score_tree(v, ref)
        if prev is None:
            print(f"{sha[:10]} {s:>9.4f}")
        else:
            d = delta(prev, v)
            print(f"{sha[:10]} {s:>9.4f} {d['dS']:>+9.4f} {d['verdict']:9} {'; '.join(d['rises'])[:120]}")
        prev = v


def sensitivity() -> None:
    base_ok, n, _ = calibrate(quiet=True)
    print(f"frozen weights: {base_ok}/{n}")
    for m in SCORE_METRICS:
        for f in (0.5, 2.0):
            ok, n, rows = calibrate(weights({m: f}), quiet=True)
            flips = [r["id"] for r in rows if not r["ok"]]
            print(f"{m:26} x{f:<4} {ok}/{n}  misclassified: {', '.join(flips) or 'none'}")
    ok, n, _ = calibrate({m: 1.0 for m in SCORE_METRICS}, quiet=True)
    print(f"{'all weights equal (1.0)':26}       {ok}/{n}")


def main(argv: list[str]) -> int:
    if "--calibrate" in argv:
        ok, n, _ = calibrate()
        return 0 if ok == n else 1
    if "--trajectory" in argv:
        trajectory()
        return 0
    if "--sensitivity" in argv:
        sensitivity()
        return 0
    if "--delta" in argv:
        i = argv.index("--delta")
        print(json.dumps(delta(load(Path(argv[i + 1])), load(Path(argv[i + 2]))), indent=1, sort_keys=True))
        return 0
    sys.path.insert(0, str(HERE))
    from measure_vec import measure_vec
    ref = load(Path(argv[argv.index("--ref") + 1])) if "--ref" in argv else load(REF_VEC)
    v = measure_vec(Path(argv[1]).resolve())
    w = weights()
    print(json.dumps({"S": score_tree(v, ref), "vector": {m: v.get(m) for m in SCORE_METRICS},
                      "weights": {m: round(w[m], 3) for m in SCORE_METRICS}}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
