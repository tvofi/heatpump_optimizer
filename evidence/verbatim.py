"""Reviewer-built: stamp the head's claim file with rewrite_claims, then compare every may-drift
block (first line + following comment lines up to the next may-drift/non-comment/blank-#-line)
with v7.0.0's. Also checks each stale note's tail equals its live entry's first line."""
import sys, re, subprocess, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("s", "tools/release/stamp.py"); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
cur = Path("tests/golden/claimed_drift.txt").read_text()
v700 = subprocess.run(["git","show","v7.0.0:tests/golden/claimed_drift.txt"],capture_output=True,text=True,check=True).stdout
new, old, deleted = s.rewrite_claims(cur, "7.0.1", "t")
_, restored, stale = s.restore_suspended(cur)
print(f"RESULT deleted={deleted} old={old} restored={len(restored)} stale={len(stale)}")
def blocks(t):
    L = t.splitlines(); out = {}
    for i,l in enumerate(L):
        m = re.match(r"^# may-drift:\s*(\w+)", l)
        if m:
            b=[l]; j=i+1
            while j<len(L) and L[j].startswith("#") and not re.match(r"^# may-drift:",L[j]) and L[j].strip()!="#" and not L[j].startswith("# ("):
                b.append(L[j]); j+=1
            out.setdefault(m.group(1),[]).append(b)
    return out
bn, bo = blocks(new), blocks(v700)
print("names new", len(bn), "v7.0.0", len(bo), "dups new", [k for k,v in bn.items() if len(v)>1])
print("only new", sorted(set(bn)-set(bo)), "only v7.0.0", sorted(set(bo)-set(bn)))
bad = [k for k in bo if k in bn and bn[k][0]!=bo[k][0]]
for k in bad:
    print("DIFF", k, "\n  new:", bn[k][0], "\n  old:", bo[k][0])
print(f"RESULT verbatim_blocks={len([k for k in bo if k in bn])-len(bad)}/{len(bo)} differ={bad}")
# first lines only
fl = lambda t: sorted(l for l in t.splitlines() if l.startswith("# may-drift:"))
print("RESULT first_lines_equal=", fl(new)==fl(v700), len(fl(new)), len(fl(v700)))
# stale notes vs live entry
L = cur.splitlines()
for i,l in enumerate(L):
    h = s.SUSPEND_HEAD_RE.match(l)
    if h and h.group("name") in stale:
        tail = s.SUSPEND_TAIL_RE.match(L[i+1]).group("entry")
        live = [x for x in L if x.startswith(f"# may-drift: {h.group('name')} ")]
        print("stale", h.group("name"), "tail==live:", live==[f"# may-drift: {tail}"])
print("suspends left:", "suspends" in new)
Path("/tmp/seat/rev2456/ev/stamped_claimed_drift.txt").write_text(new)
