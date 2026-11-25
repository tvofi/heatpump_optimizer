import sys; sys.path.insert(0, "/root/probe-base/dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes")
import _g23_common as c, numpy as np
nan=float('nan')
MUT = {
 '856a': ('_safety_release_steps','while j >= 0:','while j > 0:'),
 '8fd1': ('_safety_release_steps','if pinned_off:','if False:'),
 'ce68': ('_safety_release_steps','pinned_off = not _pin_is_free(pin) and pin < 0.5','pinned_off = not _pin_is_free(pin) or pin < 0.5'),
 'fe3e': ('_safety_release_steps','if not _pin_is_free(pin) and pin < 0.5:','if not _pin_is_free(pin) or pin < 0.5:'),
 '8ef1': ('_safety_release_steps','pinned_off = not _pin_is_free(pin) and pin < 0.5','pinned_off = not _pin_is_free(pin) and pin <= 0.5'),
 '5ce8': ('_safety_release_steps','if not _pin_is_free(pin) and pin < 0.5:','if not _pin_is_free(pin) and pin <= 0.5:'),
}
def pins(spec):
    a=np.full(96,nan)
    for (s,e,v) in spec: a[s:e]=v
    return a
scen = {
 'winter_r19_off0': (('winter_typical','winter_cold',{'room_temperature':19.0}), [(0,1,0.0)]),
 'winter_r19.5_off0-4': (('winter_typical','winter_cold',{'room_temperature':19.5}), [(0,4,0.0)]),
 'winter_off0-16_on16-20': (('winter_typical','winter_cold',{}), [(0,16,0.0),(16,20,1.0)]),
 'winter_off0-32_on32-36': (('winter_typical','winter_cold',{}), [(0,32,0.0),(32,36,1.0)]),
 'winter_r19.2_off0-8_on8-12': (('winter_typical','winter_cold',{'room_temperature':19.2}), [(0,8,0.0),(8,12,1.0)]),
 'shoulder_off0-24': (('shoulder','shoulder',{}), [(0,24,0.0)]),
 'winter_off0-8_half8-12': (('winter_typical','winter_cold',{}), [(0,8,0.0),(8,12,0.5)]),
 'winter_r19.1_half0-8': (('winter_typical','winter_cold',{'room_temperature':19.1}), [(0,8,0.5)]),
 'winter_off_all': (('winter_typical','winter_cold',{}), [(0,96,0.0)]),
 'winter_off_20-40': (('winter_typical','winter_cold',{}), [(20,40,0.0)]),
}
for sn,(b,sp) in scen.items():
    bundle=c.build(b[0],b[1],**b[2])
    base=c.plan_signature(c.solve(bundle, space_pins=pins(sp)))
    row=[]
    for k,(n,o,nw) in MUT.items():
        try:
            with c.mutated(n,o,nw):
                m=c.plan_signature(c.solve(bundle, space_pins=pins(sp)))
            d = 'SAME' if m==base else f'DIFF rel {len(base[0])}->{len(m[0])} sumP {sum(base[2]):.2f}->{sum(m[2]):.2f}'
        except Exception as e: d='EXC '+type(e).__name__
        row.append(f'{k}:{d}')
    print(sn, 'rel', len(base[0]), '|', ' '.join(row), flush=True)
