import sys,json
from pathlib import Path
sys.path.insert(0,"custom_components")
from heatpump_optimizer.accuracy import AccuracyTracker
d=json.loads(Path(sys.argv[1]).read_text())["data"]["debug"]
doc=[v for k,v in d["stores"].items() if k.endswith("_accuracy")][0]
tr=AccuracyTracker.from_dict(doc.get("accuracy",doc))
ts={s.get("t") or s.get("when") for r in d["cycle_rows"] for s in [r.get("accuracy_sample")] if s}
w=[s.when.isoformat() for s in tr.samples]
print("store",len(w),"row_ts",len(ts),"intersect",len(set(w)&ts))
# dedupe only (no store truncation): last N distinct-by-t rows vs full store
rows={}
for r in d["cycle_rows"]:
    s=r.get("accuracy_sample")
    if s: rows[s.get("t") or s.get("when")]=s
vals=[s["predicted_temp"]-s["actual_temp"] for s in list(rows.values())[-len(w):] if s.get("actual_temp") is not None and s.get("predicted_temp") is not None]
print("dedupe_only_bias",sum(vals)/len(vals),"store",tr.temperature_bias())
