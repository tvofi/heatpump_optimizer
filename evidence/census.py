# REVIEWER'S OWN census: for every tracked .py, which repo-path literals are
# HELD but not read as opens by the arm's own _sp_literals, and does the line
# look like a real read site (.open( / read_text / read_bytes / open( )?
import subprocess, re, sys
files = subprocess.run(["git","ls-files","*.py"],capture_output=True,text=True).stdout.split()
hits=[]
for f in files:
    try: src=open(f, encoding="utf-8").read()
    except Exception: continue
    try:
        held={(l,v) for l,v,_ in _sp_literals(src, opened=False)}
        opn ={(l,v) for l,v,_ in _sp_literals(src, opened=True)}
    except Exception: continue
    drift=held-opn
    if not drift: continue
    lines=src.splitlines()
    for l,v in drift:
        txt=lines[l-1] if 0<l<=len(lines) else ""
        if re.search(r"\.\s*(open|read_text|read_bytes)\s*\(|=\s*open\(|\bopen\(", txt):
            hits.append((f,l,v,txt.strip()[:110]))
print("HELD_NOT_OPEN_AT_A_READ_SITE", len(hits))
for h in hits[:40]: print("  %s:%d %r :: %s" % h)
