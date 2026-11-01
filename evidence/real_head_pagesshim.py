#!/usr/bin/env python3
"""Reviewer-built transport shim (round 2), extending the body's r10_fly_raise_reviewable.py:
this seat's proxy refuses `gh api --paginate` follow-up links, and #3045 now carries 120 check runs,
so `--paginate --jq J P` is answered by reading P&page=1..N with `gh api --jq J` until a page is empty,
and `--paginate --slurp P` likewise as a list of pages. Nothing else in merge_train is changed.
    python3 real_head_pagesshim.py <checkout> classify <sha> --repo R [--pr N]"""
import importlib.util, json, sys
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("mt", f"{root}/tools/audit/seat/merge_train.py")
mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt)
orig = mt.Train._run
def pages(path):
    sep = "&" if "?" in path else "?"
    for n in range(1, 30):
        yield f"{path}{sep}page={n}"
def run(argv, cwd=mt.ROOT, stdin=None):
    if argv[:3] == ["gh", "api", "--paginate"]:
        rest = argv[3:]
        if rest[:1] == ["--slurp"]:
            out = []
            for p in pages(rest[1]):
                c, o = orig(["gh", "api", p], cwd=cwd, stdin=stdin)
                if c: return c, o
                v = json.loads(o)
                if not v or (isinstance(v, dict) and not any(isinstance(x, list) and x for x in v.values())): break
                out.append(v)
                if isinstance(v, list) and len(v) < 30: break
            return 0, json.dumps(out or [[]])
        if rest[:1] == ["--jq"]:
            jq, path = rest[1], rest[2]
            acc = ""
            for p in pages(path):
                c, o = orig(["gh", "api", "--jq", jq, p], cwd=cwd, stdin=stdin)
                if c: return c, o
                if not o.strip(): break
                acc += o if o.endswith("\n") else o + "\n"
            return 0, acc
    return orig(argv, cwd=cwd, stdin=stdin)
mt.Train._run = staticmethod(run)
rc = mt.main(sys.argv[2:]); print(f"rc={rc}"); sys.exit(0)
