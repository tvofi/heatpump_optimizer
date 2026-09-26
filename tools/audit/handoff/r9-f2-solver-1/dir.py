import sys, json
sys.path[:0] = ['tests', 'custom_components', 'tests/hastub']
import golden
names = sys.argv[1].split(',')
out = {}
for n in names:
    cap = golden.capture(n, golden.SCENARIOS[n])
    built = golden.make(**golden.SCENARIOS[n])
    lo = built['optimizer'].config.min_temp
    br = 0.0
    for k in ('upper_temp_trajectory', 'lower_temp_trajectory'):
        br += sum(max(0.0, lo - t) for t in (cap.get(k) or [])[1:])
    out[n] = dict(breach=round(br, 4), cost=cap.get('predicted_cost'), minU=min((cap.get('upper_temp_trajectory') or [99])[1:]), minL=min((cap.get('lower_temp_trajectory') or [99])[1:]))
print(json.dumps(out))
