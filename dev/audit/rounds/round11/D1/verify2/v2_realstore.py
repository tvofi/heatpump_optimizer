"""Verifier D1#2 V3 for D1-s3-05: what real Home Assistant's Store does with a save that fails.
Metric: per case (non-serialisable payload; unwritable storage file), whether async_save raised
to the caller, and ERROR records from homeassistant.helpers.storage. Real HA 2026.9.3 (venv-ha)."""
import asyncio, logging, os, sys
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
recs=[]
class H(logging.Handler):
    def emit(s,r): recs.append(r)
logging.getLogger("homeassistant").addHandler(H()); logging.getLogger("homeassistant").setLevel(logging.DEBUG)
async def main(cfg):
    hass=HomeAssistant(cfg)
    out=[]
    for name,data,prep in [("unserialisable",{"x":object()},None),("unwritable",{"x":1},"ro"),("healthy",{"x":1},None)]:
        st=Store(hass,1,f"hpo_v_{name}")
        if prep=="ro":
            os.makedirs(os.path.dirname(st.path),exist_ok=True)
            os.makedirs(st.path,exist_ok=True)  # path is a directory: the write must fail
        recs.clear(); raised=None
        try: await st.async_save(data)
        except Exception as e: raised=type(e).__name__
        errs=[r.getMessage()[:80] for r in recs if r.levelno>=logging.ERROR]
        print(f"  {name}: raised={raised} errors={len(errs)} {errs}")
        out.append((raised,len(errs)))
    await hass.async_stop(force=True)
    return out
o=asyncio.run(main(sys.argv[1]))
print("V3 05 real_store_raised=%d/2 failing_cases logged_ERROR=%d/2 healthy_errors=%d"%(sum(1 for r,_ in o[:2] if r),sum(1 for _,e in o[:2] if e),o[2][1]))
