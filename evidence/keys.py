import re,sys,pathlib
r=pathlib.Path(sys.argv[1]); sys.path.insert(0,str(r/"tools/audit/seat"))
import sweep_render as s
names=set(s.declared((r/"tools/audit/seat/sweep_template.md").read_text()))
src=(r/"tools/audit/seat/beat_jobs.py").read_text()
keys=set()
for m in re.finditer(r'ctx\.need\(([^)]*)\)',src): keys|=set(re.findall(r'"([a-z_]+)"',m.group(1))[1:])
keys|=set(re.findall(r'overlay(?:\.get\(|\[)"([a-z_]+)"',src))
keys|=set(re.findall(r'\(\("([a-z_]+)", "--',src)); keys|=set(re.findall(r'\("([a-z_]+)", "--[a-z-]+"\)',src))
print(sys.argv[1],"beat_jobs overlay keys not in the template's placeholder table:",sorted(keys-names))
