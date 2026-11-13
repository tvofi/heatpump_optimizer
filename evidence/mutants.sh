#!/bin/bash
cd /tmp/claude-0/wt-head
S=custom_components/heatpump_optimizer/strings.json
PA=custom_components/heatpump_optimizer/pump_arbiter.py
C=custom_components/heatpump_optimizer/const.py
CL=custom_components/heatpump_optimizer/curve_learning.py
SV=custom_components/heatpump_optimizer/translations/sv.json
run(){ echo "=== $1"; PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py 2>&1 | grep -E "FAIL|checks (PASSED|FAILED)" | cut -c1-300; git checkout -q -- custom_components tests; }
time run baseline
python3 - <<'P'
import json,subprocess
S='custom_components/heatpump_optimizer/strings.json'
base=json.loads(subprocess.run(['git','show','154dbb4c:'+S],capture_output=True,text=True).stdout)
t=json.load(open(S))
k=t['options']['step']['entities']['sections']['indoor']['data_description']
k['space_setpoint_unit']=base['options']['step']['entities']['sections']['indoor']['data_description']['space_setpoint_unit']
json.dump(t,open(S,'w'),ensure_ascii=False,indent=2)
P
run M1-revert-space_setpoint_unit
sed -i 's/^LEASE_MINUTES = 90.0/LEASE_MINUTES = 60.0/' $PA; git diff --stat; run M2-LEASE_MINUTES-60
sed -i 's/^SPLIT_MIN_MINUTES = 5.0/SPLIT_MIN_MINUTES = 6.0/' $PA; git diff --stat; run M3-SPLIT_MIN-6
python3 - <<'P'
p='tests/doc_claims.py';s=open(p).read()
s=s.replace('''_OWNED_ELSEWHERE = {
    "options.step.entities.sections.indoor.data_description.space_setpoint_entity":
        "The optimizer never writes a recommended space set-point.",
}''','_OWNED_ELSEWHERE = {}');open(p,'w').write(s)
P
git diff --stat; run M4-exemption-removed
grep -n "^ECONOMY_MIN_TEMP_WIDENING\|^OPEN_WINDOW_RELAX_C\|^ECONOMY_ABSOLUTE_FLOOR\|^CONFIDENCE_MARGIN_CAP_C\|^DHW_LEGIONELLA_HOLD_MINUTES" $C
sed -i -E 's/^(ECONOMY_MIN_TEMP_WIDENING[^=]*= *)1\.5/\12.0/' $C; git diff --stat; run M5-ECONOMY_WIDENING-2
sed -i -E 's/^(STEP_K[^=]*= *)([0-9.]+)/\10.3/' $CL; git diff $CL | grep '^[-+]S'; run M6-STEP_K-0.3
python3 - <<'P'
import json
p='custom_components/heatpump_optimizer/translations/sv.json'
t=json.load(open(p));k=t['options']['step']['entities']['sections']['indoor']['data_description']
k['space_setpoint_unit']=k['space_setpoint_unit']+' Denna integration skriver aldrig ett rekommenderat börvärde (never writes).'
json.dump(t,open(p,'w'),ensure_ascii=False,indent=2)
P
git diff --stat; run M7-sv-never-writes-planted
python3 - <<'P'
import json
p='custom_components/heatpump_optimizer/strings.json'
t=json.load(open(p));k=t['options']['step']['entities_pump']['data_description']
k['heat_pump_capacity_limited_entity']+=' The optimizer never writes it.'
json.dump(t,open(p,'w'),ensure_ascii=False,indent=2)
P
run M8-never-writes-on-capacity_limited
python3 - <<'P'
import json
p='custom_components/heatpump_optimizer/strings.json'
t=json.load(open(p))
for path in (('config','step','user_sensors','data_description'),('options','step','entities','sections','plant','data_description')):
    n=t
    for x in path: n=n[x]
    n['heat_pump_switch_entity']+=' The optimizer never writes it.'
json.dump(t,open(p,'w'),ensure_ascii=False,indent=2)
P
run M9-never-writes-on-heat_pump_switch
