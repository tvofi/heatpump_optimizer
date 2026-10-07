"""Reviewer's own probe (r9c-rev-1997): _arbitrate under a live block in
DUTY_CONTROL still writes the night schedule, and the command duty drops the
blocked channel. Run from a tree root: PYTHONPATH=tests/hastub python3 <this>."""
import asyncio, sys
from datetime import datetime, timezone
from types import SimpleNamespace
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from heatpump_optimizer import boost as boost_mod, pump_arbiter as arb

class _C:
    def __init__(self): self.entry = SimpleNamespace(entry_id="p")

now = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
log = []
async def _cmd(coord, inp, want, now): log.append(("command", want))
async def _night(coord, inp, now): log.append(("night",))
async def _persist(*a, **k): pass
arb._command = _cmd; arb._write_night_schedule = _night
arb._pump_off = lambda inp: False; arb.hold = lambda c, n: None
arb._observe = lambda *a: None; arb._leased = lambda inp, held, d, n: d
arb._planned_duty = lambda c, i, n: "both"; arb._share = lambda c, i, d, n: d
arb.desired = lambda c, i, d, n: d
boost_mod.release_blocked = lambda c, i, n: False; boost_mod.persist = _persist
for chans, want in (((), "both"), (("space",), "dhw"), (("dhw",), "space"), (("space", "dhw"), "idle")):
    log.clear()
    coord = _C()
    held = boost_mod.held_for(coord)
    for ch in chans:
        held.set(ch, True, now, block=True)
    inp = SimpleNamespace(mode="auto")
    asyncio.run(arb._arbitrate(coord, SimpleNamespace(written={}, retry=None), inp, arb.DUTY_CONTROL, now))
    ok = log == [("command", want), ("night",)]
    print(("OK  " if ok else "BAD ") + f"block={chans} log={log} want command={want} then night")
