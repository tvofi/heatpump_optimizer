import sys
p=sys.argv[1]+"/custom_components/heatpump_optimizer/coordinator.py"; s=open(p).read()
old='            "measured_power": self._measured_power,\n'
assert s.count(old)==1
s=s.replace(old, '            "measured_power": "wrong type",\n            "zzz_undeclared": 1,\n',1)
open(p,"w").write(s)
