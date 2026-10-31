import re,subprocess,sys
enum=set()
for l in open(sys.argv[1]):
    p=l.split(':')
    if len(p)>3 and p[1].isdigit(): enum.add(p[0]+':'+p[1])
pat=re.compile(r'([/*]\s*\(?\s*[\w.\[\]()]*cop(?!y)\w*)|(\b\w*cop(?!y)\w*[\w.\[\]()]*\s*[*/](?![*/]))',re.I)
out=subprocess.run(['git','grep','-n','-i','cop','--','custom_components/heatpump_optimizer/*.py'],capture_output=True,text=True).stdout
miss=[]
n=0
for line in out.splitlines():
    f,ln,src=line.split(':',2)
    s=src.split('#')[0]
    if not s.strip() or re.match(r'\s*("|\')',s): continue
    s2=re.sub(r'scope|copy|"[^"]*"|\'[^\']*\'','',s,flags=re.I)
    if pat.search(s2):
        n+=1
        k=f.split('/')[-1]+':'+ln
        if k not in enum: miss.append(line.strip()[:200])
print('MYGREP lines',n,'not-in-enum',len(miss))
print('\n'.join(miss))
