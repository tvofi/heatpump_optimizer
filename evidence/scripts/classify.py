import re, sys, subprocess
REQ = re.compile(r'^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)\s*\\?\s*$')
HASH = re.compile(r'--hash=sha256:[0-9a-f]{64}')
base, head, path = sys.argv[1], sys.argv[2], sys.argv[3]
d = subprocess.run(['git','diff','--unified=0',base,head,'--',path],capture_output=True,text=True,check=True).stdout
cur=None; counts={}
for line in d.splitlines():
    if line.startswith('@@'):
        m=re.search(r'\+(\d+)(?:,(\d+))?',line)
        cur=int(m.group(1)) if m else None
        continue
    if line.startswith(('+++','---','diff ','index ')): continue
    if line.startswith('+') or line.startswith('-'):
        body=line[1:]
        m=REQ.match(body)
        if m: kind=f'version:{m.group(1)}'
        elif HASH.search(body): kind='hash'
        elif body.strip().startswith('#'): kind='comment'
        elif body.strip()=='': kind='blank'
        else: kind='OTHER:'+body[:60]
        counts[kind]=counts.get(kind,0)+1
print(path)
for k,v in sorted(counts.items()): print(f'  {v:5d}  {k}')
print('  total:', sum(counts.values()))
