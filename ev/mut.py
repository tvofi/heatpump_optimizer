import sys,subprocess,shutil,os
M={
"M4":("            self.record_drafts(queue)\n","            pass\n"),
"M7":("            pending.add(name)\n","            pass\n"),
"M8":('if x and not x.startswith("0001")]','if x]'),
"M9":('(c.get("completedAt"), c.get("startedAt"))','(c.get("completedAt"),)'),
"X10":("(stamp, i) >= best[name][0]","(stamp, i) > best[name][0]"),
"X11":('if "draft" not in item:\n                item["draft"]','if True:\n                item["draft"]'),
"X12":("if not item.get(\"draft\") or undrafted:","if not item.get(\"draft\"):"),
"X13":("                undrafted = True\n","                pass\n"),
"X14":("stamp = stamps[0] if stamps else \"\"","stamp = stamps[-1] if stamps else \"\""),
"X15":(' or state in ROLLUP_PENDING:',':'),
"X16":('name = c.get("name") or c.get("context") or "?"','name = c.get("name") or "?"'),
"X17":("if not self.real:\n            return\n        for item in queue:","for item in queue:"),
"X18":('(c.get("status") or state).upper() in ROLLUP_PENDING or','False or'),
"X19":('("PENDING" if n in pending else v[1])','v[1]'),
}
k=sys.argv[1]; wt=sys.argv[2]
p=wt+"/tools/audit/seat/merge_train.py"
s=open(p).read(); a,b=M[k]
assert s.count(a)==1,(k,s.count(a))
open(p,"w").write(s.replace(a,b))
r=subprocess.run(["python3",p,"--self-test"],capture_output=True,text=True,cwd=wt)
out=r.stdout+r.stderr
open(sys.argv[3],"w").write(out)
fails=[l for l in out.splitlines() if "FAIL" in l or "Traceback" in l or "Error" in l]
print(k,"rc",r.returncode,"KILLED" if r.returncode else "SURVIVED"); [print("  ",l[:170]) for l in fails[:4]]
