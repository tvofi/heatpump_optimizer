"""Verifier D1#2 own harness (V2) for D1-s3-01/02/03: function-level disagreement counts.
Run from the tree root: PYTHONPATH=tests/hastub:custom_components python3 v2_parsers.py"""
import json, math, sys
from datetime import datetime, timedelta, timezone
from heatpump_optimizer import inputs, open_meteo, const
from heatpump_optimizer import coordinator as c
# 01: tokens where parse_bool says a flag but finite_float refuses as a number non-finite
toks=["nan","NaN","NAN"," nan ","inf","-inf","+inf","Infinity","-Infinity","1e309","-1e309","1e999"]
fin_toks=["0","1","2","-1","0.0","1e308"]
n01=sum(1 for t in toks if inputs.parse_bool(t) is not None and const.finite_float(t) is None)
true01=sum(1 for t in toks if inputs.parse_bool(t) is True)
null01=sum(1 for t in fin_toks if (inputs.parse_bool(t) is None) != (const.finite_float(t) is None))
print(f"V2 01 nonfinite_tokens_read_as_flag={n01}/{len(toks)} true={true01} null_finite_disagree={null01}/{len(fin_toks)}")
# strict mode too
print("V2 01 strict", sum(1 for t in toks if inputs.parse_bool(t, strict=True) is not None))
# 02
pl=[True, False, "true","false",'{"displace": true}','{"displace": false}','{"command": {"displace": true}}','{"displace": 2, "effective_displace": true}', b"true"]
n02=0
for p in pl:
    try: d,e=c._parse_ecl110_state(p, (-10.0,10.0))
    except Exception as ex: print(" raise",p,type(ex).__name__); continue
    bad=(d is not None and isinstance(json.loads(p) if isinstance(p,(str,bytes)) else p,(bool,)) ) or (e is not None and isinstance(json.loads(p).get("effective_displace") if isinstance(p,str) and p.startswith("{") else None,bool)) or (isinstance(p,str) and 'true' in p and 'command' in p and d is not None) or (isinstance(p,str) and p.startswith('{"displace": t') and d is not None) or (isinstance(p,str) and p.startswith('{"displace": f') and d is not None)
    n02+=bool(bad); print(" ",repr(p),"->",d,e,"BOOL-ACCEPTED" if bad else "")
null02=[c._parse_ecl110_state(p,(-10.0,10.0)) for p in ["3",'{"displace": 3}']]
print(f"V2 02 bool_payloads_accepted={n02}/{len(pl)} null_numeric={null02}")
# 03
base=datetime(2026,11,17,tzinfo=timezone.utc)
stamps=["0001-01-01T00:00","0001-01-01T00:30","0001-01-01T01:00","0001-01-01T00:59","9999-12-31T23:00","9999-12-31T23:59"]
n03=0
for s in stamps:
    times=[s]+[(base+timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(72)]
    blk={"time":times,"shortwave_radiation":[100.0]*len(times)}
    ser=open_meteo._parse_block(blk,"shortwave_radiation")
    kept=len(ser.times)
    try: ser.mean_over(base+timedelta(hours=3), base+timedelta(hours=3,minutes=15)); r="ok"
    except Exception as ex: r=type(ex).__name__; n03+=1
    print(f"  stamp {s}: kept={kept} mean_over={r}")
ctrl=open_meteo._parse_block({"time":[(base+timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(72)],"shortwave_radiation":[100.0]*72},"shortwave_radiation")
print(f"V2 03 extreme_stamps_raising={n03}/{len(stamps)} null_control_mean={ctrl.mean_over(base+timedelta(hours=3), base+timedelta(hours=3,minutes=15))}")
