# Reviewer's own implementation of RCA-2004 section 4's widened rule (not the fixer's).
import json,subprocess,re,os,sys
L=json.load(open('tests/layout.json'))
ret=[r for r in L.get('retired',[]) if isinstance(r,dict) and 'old' in r]
olds={r['old']:r.get('new') for r in ret if not os.path.exists(r['old'])}
print('retired.old absent at HEAD:',len(olds))
files=subprocess.run(['git','ls-files','*.mjs','*.js','*.py','*.sh','*.yml'],capture_output=True,text=True).stdout.split()
files=[f for f in files if not re.match(r"(tools/audit/round[^/]*/|dev/archive/|dev/audit/rounds/)",f)]
shape=re.compile(r"^\s*(export )?const [A-Z_]+ *= *'|spawn|exec|\bnode\b|python3|\bbash\b|readFileSync|readFile|open\(|read_text|import\(|require\(|git show|git cat-file")
hits=[];cleared=0
for f in files:
  try: lines=open(f,encoding='utf8',errors='replace').read().split('\n')
  except Exception: continue
  for i,l in enumerate(lines):
    for o,n in olds.items():
      if o in l:
        if not shape.search(l): continue
        ctx='\n'.join(lines[max(0,i-4):i+5])
        if (n and n in ctx) or re.search(r'locate\(|_layout_locate|layout\.',l):
          cleared+=1; continue
        hits.append(f"{f}:{i+1}: [{o}] {l.strip()[:170]}")
print('shape hits cleared by new-path/locate within +-4 lines:',cleared)
print('UNCLEARED:',len(hits))
for h in hits: print(h)
