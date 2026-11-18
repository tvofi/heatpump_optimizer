import sys, json, io, contextlib, collections
from pathlib import Path
R=Path.cwd()
for p in ("tests/hastub","tests","custom_components","tools/replay"): sys.path.insert(0,str(R/p))
import debug_ingest as di, importlib.util
from heatpump_optimizer import store as S
from heatpump_optimizer.accuracy import AccuracyTracker
ex=di.load_export()
raw=json.loads(Path(sys.argv[1]).read_text())
print("V03 top_keys_has_schema", "schema" in raw, "data.debug.schema", (raw.get("data") or {}).get("debug",{}).get("schema"))
def fails(b):
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf): r=di.ingest(b)
    return [l for l in buf.getvalue().splitlines() if "FAIL" in l]
f1=fails(raw); dbg=raw["data"]["debug"]; f2=fails(dbg)
print("V03 fails_raw",len(f1),"fails_dbg",len(f2)); print(f2)
print("V02 replay is None", dbg.get("replay") is None, "violations({})", ex.violations({}))
# V01: own metric: mean(actual-predicted) over store samples vs over rows deduped by full sample content, last N distinct
doc=[v for k,v in dbg["stores"].items() if k.endswith("_accuracy")][0]
tr=AccuracyTracker.from_dict(doc.get("accuracy",doc)); N=len(tr.samples)
rows=[r["accuracy_sample"] for r in dbg.get("cycle_rows",()) if r.get("accuracy_sample")]
def bias(ss):
    d=[s["actual_temp"]-s["predicted_temp"] for s in ss if s.get("actual_temp") is not None and s.get("predicted_temp") is not None]
    return sum(d)/len(d) if d else None
seen=[];keys=set()
for s in rows:
    k=json.dumps(s,sort_keys=True)
    if k not in keys: keys.add(k); seen.append(s)
st=[{"actual_temp":s.actual_temp,"predicted_temp":s.predicted_temp} for s in tr.samples]
print("V01 N",N,"rows",len(rows),"distinct",len(seen),"tail_distinct",len({json.dumps(s,sort_keys=True) for s in rows[-N:]}))
print("V01 tracker_bias",tr.temperature_bias(),"mybias_store",bias(st),"mybias_tail",bias(rows[-N:]),"mybias_dedup_lastN",bias(seen[-N:]))
# consecutive repeats
rep=sum(1 for a,b in zip(rows,rows[1:]) if a==b); print("V01 consecutive_repeat_rows",rep)
# V04: bool values under secret keys
cnt=[]
def w(n,p):
    if isinstance(n,dict):
        for k,v in n.items():
            if ex.SECRET_KEY.search(str(k)) and isinstance(v,bool): cnt.append(p+"."+k)
            w(v,p+"."+k)
    elif isinstance(n,list):
        for i,v in enumerate(n): w(v,p)
w(dbg,""); print("V04 bool_under_secret_key",len(cnt),sorted(set(cnt)))
print("V04 cred_viol", [v for v in ex.violations(dbg) if "credential" in v])
# V05: own walk via stored_fields, grouped
c=collections.Counter()
for k,doc in dbg["stores"].items():
    n=S._store_name(k)
    for p,_,d,v in S.stored_fields(n,doc):
        if d is None: c[(n,"/".join(str(x) if not isinstance(x,int) else "#" for x in p).split("/")[0:4].__str__())]+=1
        elif not S.in_domain(d,v): c[(n,"OUTDOMAIN")]+=1
print("V05 undeclared total",sum(c.values())); [print(" ",k,v) for k,v in c.items()]
