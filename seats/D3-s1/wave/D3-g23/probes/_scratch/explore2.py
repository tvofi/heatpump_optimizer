import sys; sys.path.insert(0, "/root/probe-base/dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes")
import _g23_common as c, numpy as np
from profiles import house
print('house min/target', house()['min_temperature'], house()['target_temperature'])
nan=float('nan')
orig = c.OPT._safety_release_steps
log=[]
def spy(self, result, tmin, sp, dp):
    if sp is not None:
        room = result.sensor_trajectory(self.model.params.two_zone_enabled)
        n=len(result.power_schedule)
        gaps=[(i, round(room[i+1]-tmin[i],3)) for i in range(min(n,12))]
        log.append(gaps)
    return orig(self, result, tmin, sp, dp)
c.OPT._safety_release_steps = spy
for r0 in (17.5, 18.0, 18.5, 19.0):
    b=c.build('winter_extreme','winter_cold', room_temperature=r0, slab_temperature=r0)
    p=np.full(96,nan); p[0:8]=0.0
    log.clear(); res=c.solve(b, space_pins=p)
    print(r0, 'released', sorted(res.manual_released_space), 'first-call gaps', log[0] if log else None, 'calls', len(log))
