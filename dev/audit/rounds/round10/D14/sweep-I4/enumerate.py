#!/usr/bin/env python3
"""Class I4 sweep enumerator (round 10): two readings of one key concept.

Seam family A ("hist"): every call of policy_lint.mjs's `bump(hist, key, pr)`.
  A histogram is an instance when one map receives keys from two populations:
  a key taken from parsed text AND a constant key that the parsed population
  can also produce (D13-s2-02's shape).
Seam family B ("canon"): every lookup (.has/.get/` in `) into a collection
  built from canonical paths (canon(), policyFiles(), trackedFiles(),
  policyKeyIndex()) in a module that imports canon. A lookup is guarded when
  its argument (or the line) passes through canon(); otherwise it is an
  instance candidate (D13-s2-51's shape).
Usage: enumerate.py [ROOT]   (ROOT defaults to cwd; prints TSV + counts)
"""
import re, sys, pathlib
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
FILES = ["tools/policy/policy_lint.mjs", "tools/policy/field_coverage.mjs",
         "tools/policy/budget_raise_gate.py", "tests/entities.py"]
BUILDERS = re.compile(r"canon\(|policyFiles\(|trackedFiles\(|policyKeyIndex\(|_layout_canon\(")
rows = []


def derived(lines, i, arg, depth=0):
    """True when `arg` was assigned, within the 12 lines above, from canon() or
    from a variable that was (one data-flow hop per level, 3 levels)."""
    if depth > 3 or not re.fullmatch(r"\w+", arg or ""):
        return False
    for l in reversed(lines[max(0, i - 13):i - 1]):
        m = re.match(r"\s*(?:const|let|var)?\s*%s\s*=\s*(.*)" % re.escape(arg), l)
        if m:
            if "canon(" in m.group(1):
                return True
            return any(derived(lines, i, v, depth + 1) for v in re.findall(r"\b([a-z]\w*)\.", m.group(1)))
    return False
for rel in FILES:
    p = ROOT / rel
    if not p.exists():
        continue
    lines = p.read_text().split("\n")
    # family A
    if rel.endswith("policy_lint.mjs"):
        per_map = {}
        for i, l in enumerate(lines, 1):
            for m in re.finditer(r"\bbump\((\w+),\s*([^,]+),", l):
                per_map.setdefault(m.group(1), []).append((i, m.group(2).strip()))
        for h, sites in per_map.items():
            consts = [k for _, k in sites if re.fullmatch(r"[A-Z_]+|'[^']*'", k)]
            parsed = [k for _, k in sites if k not in consts]
            mixed = bool(consts and parsed)
            for i, k in sites:
                rows.append(("hist", rel, i, h, k, "MIXED" if mixed else "single"))
    # family B
    colls = set()
    for l in lines:
        m = re.match(r"\s*(?:const|let|var)?\s*(\w+)\s*(?:\?\?)?=\s*(.*)", l)
        if m and BUILDERS.search(m.group(2)):
            colls.add(m.group(1))
    colls -= {"list", "rel", "f", "p", "q"}
    for i, l in enumerate(lines, 1):
        for c in colls:
            for m in re.finditer(r"\b%s\.(?:has|get)\(([^)]*)\)|([\w\.\[\]]+) (?:not )?in %s\b" % (c, c), l):
                arg = (m.group(1) or m.group(2) or "").strip()
                g = "guarded" if ("canon(" in arg or "canon(" in l or derived(lines, i, arg)) else "unguarded"
                rows.append(("canon", rel, i, c, arg, g))
for r in rows:
    print("\t".join(map(str, r)))
a = [r for r in rows if r[0] == "hist" and r[5] == "MIXED"]
b = [r for r in rows if r[0] == "canon" and r[5] == "unguarded"]
print(f"SEAMS {len(rows)} hist_mixed {len(a)} canon_unguarded {len(b)}")
