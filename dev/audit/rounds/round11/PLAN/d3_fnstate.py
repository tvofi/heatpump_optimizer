#!/usr/bin/env python3
"""Enumerator: for each judged D3 survivor, is its enclosing function byte-identical at REF to the wave baseline?
usage: fnstate.py <sites.json> <ref> [<ref>...]  -> prints per ref: same / changed / gone counts, and writes JSON to stdout with --json"""
import json,subprocess,ast,sys,collections
B="92d38ecb640bd462f2e19c0814d0f0b7df1ee692"; P="custom_components/heatpump_optimizer/"
cache={}
def fns(ref,f):
    k=(ref,f)
    if k in cache: return cache[k]
    r=subprocess.run(["git","show",f"{ref}:{P}{f}"],capture_output=True,text=True)
    out={}
    if r.returncode==0:
        t=r.stdout; tree=ast.parse(t); lines=t.splitlines()
        def walk(n,pre):
            for c in ast.iter_child_nodes(n):
                if isinstance(c,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    q=pre+c.name
                    if not isinstance(c,ast.ClassDef): out[q]="\n".join(lines[c.lineno-1:c.end_lineno])
                    walk(c,q+".")
                else: walk(c,pre)
        walk(tree,"")
        out["<module>"]=None
    cache[k]=out; return out
def state(ref,f,fn,patch_old=None):
    a=fns(B,f).get(fn); b=fns(ref,f)
    if fn=="<module>": return "module"
    if fn not in b: return "gone"
    return "same" if b[fn]==a else "changed"
if __name__=="__main__":
    sites=[s for s in json.load(open(sys.argv[1])) if s["verdict"] in("verified","weakened")]
    res={}
    for ref in sys.argv[2:]:
        c=collections.Counter(); 
        for s in sites:
            st=state(ref,s["file"],s["fn"]); c[st]+=1; res.setdefault(s["id"],{})[ref]=st
        print(ref,dict(c))
    json.dump(res,open(sys.argv[1].replace("sites","fnstate"),"w"))
