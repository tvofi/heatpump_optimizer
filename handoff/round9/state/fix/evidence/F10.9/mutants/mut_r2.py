import sys
M={
"M0":("# The instrument is not a dependency of what it measures. Its table is:","# The instrument is not a dependency of what it measures (null). Its table is:"),
"M7":('f"{base.stdout.strip()}:{CLOSURES_REL}"','f"HEAD:{CLOSURES_REL}"'),
"M8":("select(sorted(set(files)), base_closures(a.diff) if a.diff else None)","select(sorted(set(files)), None)"),
}
k=sys.argv[1]; p=sys.argv[2]+'/tests/closure.py'; s=open(p).read(); a,b=M[k]
assert s.count(a)==1,(k,s.count(a)); open(p,'w').write(s.replace(a,b))
