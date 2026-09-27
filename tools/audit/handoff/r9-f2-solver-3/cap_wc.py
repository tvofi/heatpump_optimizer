import sys, json
import sys
sys.argv=[sys.argv[0]]
import golden
d = golden.capture('wood_coil', golden.SCENARIOS['wood_coil'])
for k in ('baseline_cost','predicted_cost','deferred_energy_cost','dhw_heating_cost','predicted_savings','savings_percentage'):
    print(k, d.get(k))
print([m.__file__ for n,m in sys.modules.items() if n.endswith('.optimizer') or n=='optimizer'])
