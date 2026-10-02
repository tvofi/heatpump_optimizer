import sys
M={
"M0":("# The instrument is not a dependency of what it measures. Its table is:","# The instrument is not a dependency of what it measures (null). Its table is:"),
"M1":("if is_gate_file(f) and not (f == CLOSURES_REL and base is not None):","if is_gate_file(f):"),
"M2":("if hits or s in moved:","if hits:"),
"M3":("rederive = suite_order(why) + children","rederive = suite_order(why)"),
"M4":("            if c in fresh:\n                fresh[p]","            if False:\n                fresh[p]"),
"M5":("if script not in skipped and any(","if any("),
"M6":('    if s == "tests/closure.py":\n        return None','    if s in ("tests/closure.py", "tests/closures.json"):\n        return None'),
}
k=sys.argv[1]; p=sys.argv[2]+'/tests/closure.py'; s=open(p).read(); a,b=M[k]
assert s.count(a)==1,(k,s.count(a)); open(p,'w').write(s.replace(a,b))
