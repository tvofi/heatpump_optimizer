#!/usr/bin/env python3
"""Prove the finder scopes are disjoint and complete within each dimension.

Usage: python3 tools/audit/check_scopes.py --repo <checkout> [--ref <baseline sha>] [--scopes scopes.json]
Exit 0 only if every dimension passes; each failure prints the cells owned twice or not at all.
Null control: --self-test duplicates one seat's block and empties another's; it exits 0 only
when the checker refuses that perturbed file.
--seat <D<k>-s<n>> prints the cells one seat owns instead, one line per (block, file):
steps, axis values, file. `rest` is resolved here, so a finder is handed files, not a rule.
.claude/workflows/audit-find.js runs the check in its Prepare step and refuses the round on rc != 0.
"""
import argparse, itertools, json, re, subprocess, sys, copy
from pathlib import Path

def expand_braces(p):
    m = re.search(r"\{([^{}]*)\}", p)
    if not m:
        return [p]
    return [q for alt in m.group(1).split(",") for q in expand_braces(p[:m.start()] + alt + p[m.end():])]

def glob_re(p):
    out, i = "", 0
    while i < len(p):
        if p.startswith("**", i):
            out += ".*"; i += 2
        elif p[i] == "*":
            out += "[^/]*"; i += 1
        else:
            out += re.escape(p[i]); i += 1
    return re.compile(out + r"\Z")

def match(files, globs):
    rx = [glob_re(q) for g in globs for q in expand_braces(g)]
    return {f for f in files if any(r.match(f) for r in rx)}

def resolver(d, tree):
    """The dimension's universe, and a block's files with `rest` resolved against it."""
    uni = match(tree, d["universe"]) if d["universe"] else {"<none>"}
    def rest_for(steps):
        # files no explicit block sharing one of these steps names
        named = set()
        for blocks in d["seats"].values():
            for b in blocks:
                if b["files"] != "rest" and (d["mode"] == "files" or set(b["steps"]) & set(steps)):
                    named |= match(uni, b["files"]) if d["universe"] else uni
        return uni - named
    def files_of(b):
        return rest_for(b["steps"]) if b["files"] == "rest" else (match(uni, b["files"]) if d["universe"] else uni)
    return uni, files_of

def check(scopes, tree, loc):
    ok = True
    for dim, d in scopes.items():
        if dim.startswith("_"):
            continue
        uni, files_of = resolver(d, tree)
        axis_vals = next(iter(d.get("axis", {}).values()), [None])
        owners, seat_files = {}, {}
        for seat, blocks in d["seats"].items():
            fs = set()
            for b in blocks:
                bf = files_of(b)
                fs |= bf
                ax = b.get("axis", axis_vals)
                for f in bf:
                    for s in b["steps"]:
                        for a in ax:
                            key = (f, s, a) if d["mode"] == "cells" else (f,)
                            owners.setdefault(key, set()).add(seat)
                if d["mode"] == "files":
                    for s in b["steps"]:
                        owners.setdefault(("step", s), set()).add(seat)
            seat_files[seat] = fs
        if d["mode"] == "cells":
            want = set(itertools.product(uni, d["steps"], axis_vals))
            dup = {k: v for k, v in owners.items() if len(v) > 1}
        else:
            want = {(f,) for f in uni} | {("step", s) for s in d["steps"]}
            dup = {k: v for k, v in owners.items() if len(v) > 1 and k[0] != "step"}
        missing = want - set(owners)
        extra = set(owners) - want
        status = "ok" if not (dup or missing or extra) else "FAIL"
        ok &= status == "ok"
        sizes = ", ".join(f"{s}:{len(fs)}f/{sum(loc.get(f,0) for f in fs)}loc" for s, fs in seat_files.items())
        print(f"{status} {dim} mode={d['mode']} seats={len(d['seats'])} universe={len(uni)} [{sizes}]")
        for k in sorted(missing, key=str)[:10]:
            print(f"   unowned {k}")
        for k, v in sorted(dup.items(), key=str)[:10]:
            print(f"   owned twice {k} by {sorted(v)}")
        for k in sorted(extra, key=str)[:10]:
            print(f"   outside universe/steps {k}")
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--scopes", default=str(Path(__file__).with_name("scopes.json")))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--seat", help="print the cells this seat (D<k>-s<n>) owns and exit")
    a = ap.parse_args()
    tree = set(subprocess.check_output(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", a.ref], text=True).split())
    loc = {}
    for f in tree:
        if f.startswith("custom_components/") and f.endswith((".py", ".js")):
            try:
                loc[f] = subprocess.check_output(["git", "-C", a.repo, "show", f"{a.ref}:{f}"], text=True).count("\n")
            except Exception:
                pass
    scopes = json.load(open(a.scopes))
    if a.seat:
        dim, _, seat = a.seat.partition("-")
        d = scopes.get(dim)
        if dim.startswith("_") or not d or seat not in d["seats"]:
            print(f"no seat {a.seat} in {a.scopes}", file=sys.stderr)
            sys.exit(2)
        _, files_of = resolver(d, tree)
        axis_vals = next(iter(d.get("axis", {}).values()), [None])
        for b in d["seats"][seat]:
            ax = ",".join(v for v in b.get("axis", axis_vals) if v) or "-"
            for f in sorted(files_of(b)):
                print(f"{'+'.join(b['steps'])}\t{ax}\t{'(any file: no file axis)' if f == '<none>' else f}")
        sys.exit(0)
    seats = sum(len(d["seats"]) for k, d in scopes.items() if not k.startswith("_"))
    print(f"ref={subprocess.check_output(['git','-C',a.repo,'rev-parse',a.ref],text=True).strip()} seats={seats}")
    if a.self_test:
        bad = copy.deepcopy(scopes)
        bad["D1"]["seats"]["s2"].append(copy.deepcopy(bad["D1"]["seats"]["s1"][0]))
        bad["D2"]["seats"]["s4"] = [{"files": ["**"], "steps": []}]
        res = check(bad, tree, loc)
        print("SELF-TEST", "passed (perturbed scopes refused)" if not res else "FAILED (perturbed scopes accepted)")
        sys.exit(0 if not res else 1)
    sys.exit(0 if check(scopes, tree, loc) else 1)

main()
