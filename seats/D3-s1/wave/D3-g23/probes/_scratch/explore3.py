import sys; sys.path.insert(0, "/root/probe-base/dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes")
import _g23_common as c, numpy as np
nan=float('nan')
MUT = {
 '856a': ('_safety_release_steps','while j >= 0:','while j > 0:'),
 '8fd1': ('_safety_release_steps','if pinned_off:','if False:'),
 'ce68': ('_safety_release_steps','pinned_off = not _pin_is_free(pin) and pin < 0.5','pinned_off = not _pin_is_free(pin) or pin < 0.5'),
 'fe3e': ('_safety_release_steps','if not _pin_is_free(pin) and pin < 0.5:','if not _pin_is_free(pin) or pin < 0.5:'),
}
hits={k:[] for k in MUT}
for r0 in np.arange(16.8, 17.61, 0.1):
  for spec in ([(0,1,0.0)], [(0,4,0.0)], [(0,8,0.0)], [(0,4,0.0),(4,6,1.0)], [(0,8,0.0),(8,10,1.0)], [(0,2,0.0),(2,3,1.0)]):
    p=np.full(96,nan)
    for s,e,v in spec: p[s:e]=v
    b=c.build('winter_extreme','winter_cold', room_temperature=float(r0), slab_temperature=float(r0))
    base=c.plan_signature(c.solve(b, space_pins=p.copy()))
    for k,(n,o,nw) in MUT.items():
        with c.mutated(n,o,nw):
            m=c.plan_signature(c.solve(b, space_pins=p.copy()))
        if m!=base:
            hits[k].append((round(float(r0),2),spec,base[0],m[0]))
            print('HIT',k,round(float(r0),2),spec,'released',base[0],'->',m[0],flush=True)
print({k:len(v) for k,v in hits.items()})
