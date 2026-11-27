"""Spike: per-span difference set of two swap_run logs (the gate: empty passes).

    python3 diff.py A.log B.log
"""
import re
import sys
from collections import defaultdict

LINE = re.compile(r"^  (ok  |FAIL) ")


def spans(path):
    out, cur, part = defaultdict(list), "pre", {}
    for ln in open(path, encoding="utf-8", errors="replace"):
        if ln.startswith("@@SPAN "):
            _, sid_part = ln.split(" ", 1)
            sid, _, p = sid_part.rstrip("\n").rpartition(" ")
            cur, part[sid] = sid, p
        elif LINE.match(ln):
            out[cur].append(ln.rstrip("\n"))
    return out, part


def main(a, b):
    sa, pa = spans(a)
    sb, pb = spans(b)
    diff = [s for s in sorted(set(sa) | set(sb)) if sorted(sa.get(s, [])) != sorted(sb.get(s, []))]
    na = sum(len(v) for v in sa.values())
    nb = sum(len(v) for v in sb.values())
    fa = sum(1 for v in sa.values() for x in v if x.startswith("  FAIL"))
    fb = sum(1 for v in sb.values() for x in v if x.startswith("  FAIL"))
    print(f"lines {na} vs {nb}; FAIL {fa} vs {fb}; spans {len(sa)} vs {len(sb)}; differing spans {len(diff)}")
    for s in diff:
        A, B = set(sa.get(s, [])), set(sb.get(s, []))
        print(f"DIFF {pb.get(s, pa.get(s, '?'))}\t{s}\t-{len(A - B)} +{len(B - A)}")
        for x in sorted(A - B)[:3]:
            print("   -", x[:160])
        for x in sorted(B - A)[:3]:
            print("   +", x[:160])
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
