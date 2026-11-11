# Reviewer's own check 7: nearest-mark rule (a data-copy inside a data-src owns its text), containment in the head's whitespace-normalised page text; alt texts of marked images listed.
import sys, re
from html.parser import HTMLParser
VOID={'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr'}
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.st=[]; s.marked=[]; s.text=[]; s.alts=[]
    def cur(s):
        for m in reversed(s.st):
            if m: return m
    def handle_starttag(s,t,a):
        a=dict(a); m='src' if 'data-src' in a else 'copy' if 'data-copy' in a else None
        if t=='img' and 'alt' in a: s.alts.append((m or s.cur(), a['alt']))
        if t in VOID: return
        s.st.append(m)
    def handle_startendtag(s,t,a): s.handle_starttag(t,a); 
    def handle_endtag(s,t):
        if t not in VOID and s.st: s.st.pop()
    def handle_data(s,d):
        d=re.sub(r'\s+',' ',d).strip()
        if d: s.text.append(d); 
        if d and s.cur()=='src': s.marked.append(d)
def parse(p): x=P(); x.feed(open(p).read()); return x
b=parse(sys.argv[1]); h=parse(sys.argv[2]); ht=' '.join(h.text); halt=' '.join(a for _,a in h.alts)
miss=[t for t in dict.fromkeys(b.marked) if t not in ht]
print(f"base nodes whose nearest mark is a source mark: {len(b.marked)}")
print("missing from head page text:", miss)
for m,a in b.alts:
    if m=='src': print("base marked alt:", a[:70], "| on head (text or alt):", a in ht or a in halt)
