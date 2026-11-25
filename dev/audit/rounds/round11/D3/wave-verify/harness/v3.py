#!/usr/bin/env python3
"""V3 reach and class, per candidate, measured in the baseline tree:
- reach: d3wave/REACH.tsv (traced closures at the baseline): status and the scripts that execute the line;
- production callers: call/reference sites of the mutated symbol in custom_components/ outside its own def;
- stub divergence: whether the mutated function's body names a symbol tests/ha_contract.py marks DIVERGENT;
- seam_rule: present, and whether it enumerates beyond the demonstrated cluster (text test, then executed when it
  is a grep/awk/rg command over the tree);
- fields: claim, evidence, harness, metric and perturbation present on the record."""
import ast, csv, json, re, pathlib, subprocess
D = pathlib.Path("<seat-dir>")
BASE = D / "base"
S = D / "rec/dev/audit/rounds/round11/D3/s1"
REACH = {r["key"]: r for r in csv.DictReader(open("<d3wave-dir>/REACH.tsv"), delimiter="\t")}
DIVERGENT = ["FlowError", "HomeAssistantError", "cv.string", "cv.boolean", "cv.positive_int", "cv.positive_float", "as_local"]
PKG = BASE / "custom_components/heatpump_optimizer"
SRC = {p: p.read_text() for p in PKG.rglob("*.py")}


def func_node(path, line):
    tree = ast.parse(SRC[path])
    best = None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno <= line <= n.end_lineno:
            if best is None or n.lineno > best.lineno:
                best = n
    return best


def symbol(c, m, node):
    if node is not None:
        return node.name
    lhs = re.match(r"\s*([A-Za-z_]\w*)\s*(?::[^=]+)?=", m["old"])
    return lhs.group(1) if lhs else None


def callers(name, path, node):
    if not name:
        return 0, []
    pat = re.compile(r"(?<![\w])" + re.escape(name) + r"(?![\w])")
    hits = []
    for p, t in SRC.items():
        for i, l in enumerate(t.split("\n"), 1):
            if pat.search(l) and not re.match(r"\s*(async\s+)?def\s+" + re.escape(name) + r"\b", l):
                if p == path and node is not None and node.lineno <= i <= node.end_lineno:
                    continue
                if p == path and node is None and l.strip().startswith(name) and "=" in l and i == int(m_line[0]):
                    continue
                hits.append(f"{p.relative_to(BASE)}:{i}")
    return len(hits), hits[:3]


m_line = [0]
cands = json.load(open(D / "candidates.json"))
recs = {}
for f in sorted(S.glob("REPORT-D3-g*.json")):
    for c in json.load(open(f))["gate_survivors"]:
        recs[c["key"]] = c
out = []
for c in cands:
    rec = recs[c["key"]]
    fi = rec.get("finding") or rec
    src = re.search(r"--src (\S+)", c.get("gate_command") or "")
    src = src.group(1) if src else "complete"
    m = json.loads((BASE / "dev/audit/rounds/round11/D3/s1/state/results" / src / f"{c['key']}.json").read_text())["mutant"]
    m_line[0] = m["line"]
    path = BASE / m["file"]
    node = func_node(path, int(m["line"]))
    name = symbol(c, m, node)
    n_call, sample = callers(name, path, node)
    body = ast.get_source_segment(SRC[path], node) if node is not None else m["old"]
    div = [d for d in DIVERGENT if d in (body or "")]
    rr = REACH.get(c["key"], {})
    seam = fi.get("seam_rule")
    seam_kind = None
    if seam:
        s = str(seam)
        if re.search(r"SURVIVORS\.tsv|cluster|keys\.tsv|this (key|mutant)", s):
            seam_kind = "demonstrated cluster only (enumerates the wave's mutants of this function)"
        elif re.match(r"\s*`?(grep|rg|awk|git grep|python3)", s):
            cmd = s.strip("` ").split("`")[0]
            safe = re.compile(r"^\s*(grep|rg|awk|git grep|sort|uniq|wc|head|cut)\b")
            if re.search(r"[;&<>]|\$\(|`", cmd) or not all(safe.match(seg) for seg in cmd.split("|")):

                seam_kind = "not executed: not a plain read-only grep/awk pipeline"
                cmd = None
            try:
                if cmd is None:
                    raise StopIteration
                r = subprocess.run(cmd, shell=True, cwd=BASE, capture_output=True, text=True, timeout=60)
                n = len([l for l in r.stdout.splitlines() if l.strip()])
                seam_kind = f"executed: {n} seam(s) listed" + (" (beyond the demonstrated site)" if n > 1 else " (the demonstrated site only)")
            except StopIteration:
                pass
            except Exception as e:
                seam_kind = f"not executable as written ({type(e).__name__})"
        else:
            seam_kind = "prose rule, not executable"
    fields = {"claim": bool(fi.get("claim")), "evidence": bool(fi.get("evidence_command") or fi.get("evidence") or fi.get("evidence_value")),
              "harness": bool(fi.get("harness_paths")), "metric": bool(fi.get("metric_definition")),
              "perturbation": bool(fi.get("perturbation"))}
    out.append({"key": c["key"], "box": c["box"], "file": m["file"], "line": m["line"], "old": m["old"], "new": m["new"],
                "symbol": name, "function": node.name if node is not None else "<module>",
                "reach": rr.get("reach"), "hit_by": rr.get("hit_by", ""), "prod_refs": n_call, "prod_ref_sample": sample,
                "divergent_stub": div, "seam_rule": seam, "seam_kind": seam_kind, "class_guess": fi.get("class_guess"),
                "severity_claimed": fi.get("severity_claimed") or fi.get("severity"), "fields": fields,
                "missing_fields": [k for k, v in fields.items() if not v], "title": fi.get("title"), "claim": fi.get("claim")})
json.dump(out, open(D / "v3.json", "w"), indent=1)
from collections import Counter
print(len(out), Counter(o["reach"] for o in out), Counter(o["prod_refs"] > 0 for o in out),
      Counter(bool(o["divergent_stub"]) for o in out), Counter((o["seam_kind"] or "none")[:30] for o in out),
      Counter(tuple(o["missing_fields"]) for o in out))
