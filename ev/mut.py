import subprocess, sys, pathlib
W=sys.argv[1]; R=pathlib.Path(W)/'wt'/'custom_components/heatpump_optimizer'
M=[
 ("null", None, None, None),
 ("guard_off","entity.py","if params is not None and params.combi_tank_active:","if False:"),
 ("guard_on","entity.py","if params is not None and params.combi_tank_active:","if params is not None:"),
 ("guard_enabled_only","entity.py","params.combi_tank_active:","params.dhw_combi_tank_enabled:"),
 ("const_text","entity.py",'"includes space heat drawn from the store"','"includes heat"'),
 ("cost_attr_none","sensor.py",'return dhw_split_attributes(getattr(self.coordinator, "thermal_params", None)) or None','return None'),
 ("cost_attr_empty","sensor.py",'return dhw_split_attributes(getattr(self.coordinator, "thermal_params", None)) or None','return {}'),
 ("cost_unrec","sensor.py",'    # Static documentation, as ``split_method`` is on the accumulators.\n    _unrecorded_attributes = frozenset({"dhw_split"})','    _unrecorded_attributes = frozenset()'),
 ("acc_unrec","sensor.py",'frozenset({"period", "split_method", "dhw_split"})','frozenset({"period", "split_method"})'),
 ("acc_guard_space","sensor.py",'if self._ledger_line == "dhw":','if self._ledger_line == "space":'),
 ("acc_guard_true","sensor.py",'if self._ledger_line == "dhw":','if True:'),
 ("acc_call_del","sensor.py",'            attrs.update(dhw_split_attributes(getattr(self.coordinator, "thermal_params", None)))\n        if self._ledger_line:','            pass\n        if self._ledger_line:'),
 ("climate_call_del","climate.py",'            attrs.update(dhw_split_attributes(getattr(self.coordinator, "thermal_params", None)))\n','\n'),
 ("climate_unrec","climate.py",'_unrecorded_attributes = frozenset({"dhw_split"})','_unrecorded_attributes = frozenset()'),
]
for name,f,a,b in M:
    p=R/f if f else None; orig=p.read_text() if p else None
    try:
        if p:
            assert orig.count(a)==1,(name,orig.count(a)); p.write_text(orig.replace(a,b))
        out=subprocess.run(['bash',W+'/block.sh'],capture_output=True,text=True).stdout+''
        fails=[l.strip() for l in out.splitlines() if 'Carry 10' in l and 'FAIL' in l]
        if not any('Carry 10' in l for l in out.splitlines()): fails=['NO-CARRY10-OUTPUT (crash)']
        print(('SURVIVED' if not fails else 'KILLED'), name, '|', '; '.join(f[:70] for f in fails))
    finally:
        if p: p.write_text(orig)
