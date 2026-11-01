import sys,re
sys.path.insert(0,'tools/audit/seat')
import roster_edit as r
src=open('dev/programme/triage/s6-batch99.md').read()
print('verdict',r.ruling_verdict(src,'P354'))
txt=src
for m in re.finditer(r'^> (.*(?:\n> .*)*)',src,re.M): pass
a=[l for l in src.split('Carry (a)')[1].split('Carry (b)')[0].split('\n') if l.startswith('>')]
b=[l for l in src.split('Carry (b)')[1].split('Roster ops')[0].split('\n') if l.startswith('>')]
ta='\n'.join(x[2:] for x in a); tb='\n'.join(x[2:] for x in b)
rd=lambda p: src
print(r.triage_refusal([ta,tb],rd))
bad=src.replace('Verdict: ACCEPT','Verdict: REJECT',1)
print(r.triage_refusal([ta],lambda p:bad)); print(r.triage_refusal([tb],lambda p:bad))
