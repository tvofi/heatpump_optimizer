import sys, re
from html.parser import HTMLParser
VOID={'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr','line','path','circle','rect','stop'}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.st=[]; s.marked=[]; s.all=[]; s.alts=[]
    def handle_starttag(s,t,a):
        a=dict(a); m=('data-src' in a)
        if t=='img' and 'alt' in a and (m or any(x for x in s.st)): s.alts.append(a['alt'])
        if t in VOID: return
        s.st.append(m)
    def handle_startendtag(s,t,a):
        a=dict(a)
        if t=='img' and 'alt' in a and (('data-src' in a) or any(s.st)): s.alts.append(a['alt'])
    def handle_endtag(s,t):
        if t in VOID: return
        if s.st: s.st.pop()
    def handle_data(s,d):
        d=re.sub(r'\s+',' ',d).strip()
        if not d: return
        s.all.append(d)
        if any(s.st): s.marked.append(d)
def parse(p):
    x=P(); x.feed(open(p).read()); return x
b=parse(sys.argv[1]); h=parse(sys.argv[2])
hset=set(h.all); halts=set(h.alts)
miss=[t for t in dict.fromkeys(b.marked) if t not in hset]
missalt=[t for t in dict.fromkeys(b.alts) if t not in halts]
print(f"marked text nodes at base: {len(b.marked)} ({len(set(b.marked))} distinct)")
print("missing text nodes:", miss)
print("missing marked alt texts:", missalt)
