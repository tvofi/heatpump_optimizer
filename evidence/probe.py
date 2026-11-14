import sys; sys.argv=['x']
sys.path.insert(0,'tests')
import guard_pins as g
for attrs,ev,leg in [({"min":30,"max":60,"step":1},55.0,65.0),({"min":30,"max":60,"step":5},55.0,65.0),({"min":30,"max":60,"step":0.5},50.0,65.0),({"min":30,"max":80,"step":1},55.0,65.0)]:
    for hold in (False,True):
        print(attrs, ev, leg, "hold" if hold else "instant", "->", g._step_notice(ev, leg, attrs["step"], hold=hold, attrs=attrs))
