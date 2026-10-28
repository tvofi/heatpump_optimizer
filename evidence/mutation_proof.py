import sys,re
sys.path.insert(0,'tools/audit/seat')
import roster_edit as r
P='dev/programme/triage/s6-batch49.md'
src=open(P).read()
for n in range(237,248): print(n, r.ruling_verdict(src,f"P{n}"))
txts=[f"x triage: {P}#P{n}" for n in (239,241,242,247)]
print("all", r.triage_refusal(txts, lambda p: src))
m1=src.replace("Verdict: ACCEPT narrowed","Verdict: DEFER",1)  # first ACCEPT = P239
i=src.index("## P241:"); m1=src[:i]+src[i:].replace("Verdict: ACCEPT narrowed","Verdict: DEFER",1)
print("m1", r.triage_refusal([f"triage: {P}#P241"], lambda p:m1))
m2=src.replace("## P239:","## Q239:")
print("m2", r.triage_refusal([f"triage: {P}#P239"], lambda p:m2))
print("null", r.triage_refusal([f"triage: {P}#P239"], lambda p:None))
print("rej", r.triage_refusal([f"triage: {P}#P240"], lambda p:src))
