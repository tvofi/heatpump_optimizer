import sys
p="custom_components/heatpump_optimizer/coordinator.py"; s=open(p).read()
A_old="**rooms.floor_limits(rooms.hold(self, rooms.resolve(  # #3616: plus a short room's lift"
A_new="min_temp_margins=rooms.floor_limits(rooms.hold(self, rooms.resolve(  # #3616: plus a short room's lift"
A2_old="config, state.room_temperature, solve_now)), self._confidence_margins(n), config, solve_now, n),"
A2_new="config, state.room_temperature, solve_now)), self._confidence_margins(n), config, solve_now, n)[\"min_temp_margins\"],"
B_old="**rooms.floor_limits(rooms.lift_of(self), self._confidence_margins(len(horizon.prices)), scratch_config, solve_at, len(horizon.prices)),"
B_new="min_temp_margins=rooms.floor_limits(rooms.lift_of(self), self._confidence_margins(len(horizon.prices)), scratch_config, solve_at, len(horizon.prices))[\"min_temp_margins\"],"
w=sys.argv[1]
pairs=[]
if w=="whatif_cfg": pairs+=[("scratch_config, solve_at, len(horizon.prices)),  # the baseline","config, solve_at, len(horizon.prices)),  # the baseline")]
if w in("both","sched"): pairs+= [(A_old,A_new),(A2_old,A2_new)]
if w in("both","whatif"): pairs+= [(B_old,B_new)]
for o,n in pairs:
    assert s.count(o)==1,(o,s.count(o)); s=s.replace(o,n)
open(p,"w").write(s)
