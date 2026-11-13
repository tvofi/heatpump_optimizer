#!/bin/bash
# alternate the synthetic fixture between the merge base and the head, sequentially
for i in 1 2 3 4 5; do for side in base head; do
  out=$(cd $HOME/wt/$side && PYTHONPATH=tests/hastub python3 tests/replay.py --fixture tests/replay/synthetic-dhw-only.json 2>&1)
  echo "run $i $side: $(echo "$out" | python3 -c "
import sys,re
t=sys.stdin.read()
m=re.search(r\"48 cycles over.*?cost \{'cpu_ratio': ([\d.]+).*?'loop_cpu_ratio': ([\d.]+).*?'ref_ms': ([\d.]+).*?'loop_ref_ms': ([\d.]+)\",t)
g=[l.strip() for l in t.splitlines() if 'synthetic-dhw-only.json: cycle_cost  ' in l or (l.strip().startswith(('ok','FAIL')) and l.strip().endswith('cycle_cost'))]
print('cpu_ratio',m.group(1),'loop_cpu_ratio',m.group(2),'ref_ms',m.group(3)[:6],'loop_ref_ms',m.group(4)[:6],'|',g[:1], '|', t.strip().splitlines()[-1])
")"
done; done
