import types,sys
from heatpump_optimizer import away
from heatpump_optimizer.const import OPEN_WINDOW_RELAX_C
opt=types.SimpleNamespace(**{n:{"target_temp":21.0,"min_temp":19.0}.get(n,22.0) for n in away._OPT_FIELDS})
th=types.SimpleNamespace(**{n:45.0 for n in away._DHW_FIELDS})
st=away.AwayState() if hasattr(away,'AwayState') else None
st.active=True; st.recovery_active=False; st.target_temperature=10.0
for w in [(),(OPEN_WINDOW_RELAX_C,)]:
    c,_=away.solve_bands(opt,th,st,w); print("RESULT widen=",w,"min_temp=",c["min_temp"])
st.active=False
for w in [(),(OPEN_WINDOW_RELAX_C,)]:
    c,_=away.solve_bands(opt,th,st,w); print("RESULT home widen=",w,"min_temp=",c["min_temp"])
