"""Verifier D1#2 V2 for D1-s3-05. Metric: of the 7 coordinator _async_save_* methods, called
unbound on a self whose store saves fine but whose payload attributes are missing (an
AttributeError while building the payload -- the programming-error route real HA leaves to the
integration), how many neither raise nor emit a WARNING+ record. Null: the same self with a
store whose async_save is never reached adds DEBUG only -> the count sees levels (a WARNING
handler would count)."""
import asyncio, logging
from heatpump_optimizer import coordinator as c
recs=[]
class H(logging.Handler):
    def emit(s,r): recs.append(r)
lg=logging.getLogger("custom_components.heatpump_optimizer"); lg.addHandler(H()); lg.setLevel(logging.DEBUG)
logging.getLogger(c.__name__).addHandler(H()); logging.getLogger(c.__name__).setLevel(logging.DEBUG)
class Store:
    saves=0
    async def async_save(self, d): Store.saves+=1
    def async_delay_save(self, f, delay=0): Store.saves+=1
class Self:
    def __getattr__(self, n):
        if n.endswith("_store"): return Store()
        raise AttributeError(n)
names=["_async_save_thermal_learning","_async_save_price_model","_async_save_ledger","_async_save_accuracy","_async_save_energy_totals","_async_save_manual_plan","_async_save_snapshots"]
silent=0; dbg=0
for n in names:
    recs.clear(); raised=None
    try:
        r=getattr(c.HeatPumpOptimizerCoordinator,n)(Self())
        if asyncio.iscoroutine(r): asyncio.run(r)
    except Exception as e: raised=type(e).__name__
    w=sum(1 for x in recs if x.levelno>=logging.WARNING); d=sum(1 for x in recs if x.levelno==logging.DEBUG)
    dbg+=d>0
    silent+= (raised is None and w==0)
    print(f"  {n}: raised={raised} warning+={w} debug={d} saves={Store.saves}")
print(f"V2 05 payload_build_fault_silent_above_debug={silent}/7 with_debug_record={dbg}/7")
