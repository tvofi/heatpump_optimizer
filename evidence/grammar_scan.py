import json, re, os, sys
WT=os.path.expanduser("~/hpo-seats/r10s6/review-2889b/wt-head")
sys.path.insert(0,WT+"/tools/audit/seat"); sys.path.insert(0,WT+"/tools/audit")
import roster_sync as R
live=json.load(open("/tmp/r10roster.json"))
groups=[g for g in live["groups"] if isinstance(g,dict) and g.get("group")]
CITE=re.compile(r"\btriage:\s*(dev/programme/triage/[A-Za-z0-9_.-]+\.md)#(P\d+)\b")
PROSE=re.compile(r"\btriage\s+P(\d+)(?:/Q(\d+))?\s*\((s\d+)\)", re.I)
ANY=re.compile(r"\b(?:triage|proposal)\s+P\d+\b", re.I)
cats={"cite_only":0,"prose_only":0,"both":0,"other_grammar":0,"none":0}
others=[]
for g in groups:
    for c in (g.get("carry") or []):
        c=str(c)
        has_cite=bool(CITE.search(c)); has_prose=bool(PROSE.search(c)); has_any=bool(ANY.search(c))
        if has_cite and has_prose: cats["both"]+=1
        elif has_cite: cats["cite_only"]+=1
        elif has_prose: cats["prose_only"]+=1
        elif has_any:
            cats["other_grammar"]+=1; others.append((g["group"], c[:120]))
        else: cats["none"]+=1
print("RESULT carry_grammars:", cats)
for o in others[:15]: print("   OTHER:", o)
# how many distinct ruling keys, and how many destinations hold >1 carry under one key
from collections import defaultdict
per=defaultdict(set)
for g in groups:
    for c in (g.get("carry") or []):
        for k in R.rulings(c): per[(g["group"],k)].add(str(c))
print("RESULT destination_ruling_keys:", len(per))
print("RESULT keys_with_multiple_carries:", sum(1 for v in per.values() if len(v)>1))
