#!/usr/bin/env python3
"""D6-s4 non-finding: per string leaf, the numbers and {placeholders} sv.json states against en.json.

Metric: count of sv.json leaves whose number multiset or placeholder set differs from en.json's.
Run: python3 dev/audit/rounds/round11/D6/s4/sv_en_numbers.py
Expected at baseline 92d38ecb: 3 number diffs, all formatting (two "1.0" in an sv label, "kl. 13"),
0 placeholder diffs. Not a truth check of either file against code (ledger.py does that).
Machine: B13 finder box; counts.
"""
import json,re
T='custom_components/heatpump_optimizer/translations/'
def walk(v,p=''):
    if isinstance(v,dict):
        for k,x in v.items(): yield from walk(x,p+'/'+k)
    else: yield p,v
sv=dict(walk(json.load(open(T+'sv.json')))); en=dict(walk(json.load(open(T+'en.json'))))
NUM=re.compile(r'(?<![\w.])[-−+±]?\d+(?:[.,]\d+)?')
def nums(s):
    s=re.sub(r'\{[^}]*\}','',s)
    return sorted(x.replace(',','.').replace('−','-').lstrip('+±') for x in NUM.findall(s))
print('sv only keys',len(set(sv)-set(en)),'en only',len(set(en)-set(sv)))
for k in sorted(set(sv)-set(en))[:20]: print(' SVONLY',k)
for k in sorted(set(en)-set(sv))[:20]: print(' ENONLY',k)
n=0
for k in sv:
    if k in en and isinstance(sv[k],str) and nums(sv[k])!=nums(en[k]):
        n+=1; print('DIFF',k,nums(sv[k]),nums(en[k]))
print('diffs',n)
p = 0
for k in sv:
    if isinstance(sv[k], str) and sorted(set(re.findall(r'\{(\w+)\}', sv[k]))) != sorted(set(re.findall(r'\{(\w+)\}', en[k]))):
        p += 1; print('PH', k)
print(f"RESULT number_diffs={n} count")
print(f"RESULT placeholder_diffs={p} count")
