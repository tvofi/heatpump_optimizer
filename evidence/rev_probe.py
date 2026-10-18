"""Reviewer's own probe (review-2375): drives QuarantiningStore.async_load on crafted
accuracy/snapshot documents. Usage: PYTHONPATH=<tree>/tests/hastub:<tree> python3 rev_probe.py"""
import asyncio, json, logging, sys
from datetime import timedelta
from homeassistant.helpers import storage
from homeassistant.util import dt as dt_util
from custom_components.heatpump_optimizer.store import QuarantiningStore, load_mapping
logging.disable(logging.CRITICAL)
now = dt_util.as_utc(dt_util.now())
iso = lambda h: (now + timedelta(hours=h)).isoformat()
KEY = "heatpump_optimizer_e_accuracy"
LEAD24 = timedelta(hours=24)

async def load(doc, lead):
    storage._DISK[KEY] = json.dumps(doc); storage._VERSIONS[KEY] = 1 if hasattr(storage, "_VERSIONS") else None
    s = QuarantiningStore(None, 1, KEY, lead=lead)
    try:
        return await s.async_load(), s.bounded, None
    except Exception as e:  # noqa: BLE001
        return None, None, f"{type(e).__name__}: {e}"

def hours(v):
    from datetime import datetime
    return round((datetime.fromisoformat(v) - now).total_seconds() / 3600, 2)

async def main():
    lead = None if "--base-lead" not in sys.argv else LEAD24
    # the coordinator's lead for the accuracy store at this tree: base passes 24h, head passes default 0
    lead = LEAD24 if "--base" in sys.argv else timedelta(0)
    doc = {"accuracy": {"lead_pending": [[iso(10), 12, 1.0], [iso(30), 24, 1.0]],
                        "samples": [{"t": iso(1)}], "evidence_since": iso(2)}}
    out, hits, err = await load(doc, lead)
    if err: print("RESULT probeA_error=1", err); 
    else:
        a = out["accuracy"]
        print(f"RESULT due_10h_kept_h={hours(a['lead_pending'][0][0])}")
        print(f"RESULT due_30h_bounded_to_h={hours(a['lead_pending'][1][0])}")
        print(f"RESULT sample_t_plus1h_loaded_as_h={hours(a['samples'][0]['t'])}")
        print(f"RESULT evidence_since_plus2h_loaded_as_h={hours(a['evidence_since'])}")
    # B: corrupt shapes -- a literal '~' / '' key where the trie holds a Domain
    for name, doc in [
        ("tilde_key_instant", {"accuracy": {"lead_sigma": {"~": iso(5)}}}),
        ("empty_key_under_leaf", {"accuracy": {"samples": [{"t": {"": iso(5)}}]}}),
        ("empty_key_list_under_leaf", {"accuracy": {"samples": [{"t": {"": [iso(5)]}}]}}),
    ]:
        out, hits, err = await load(doc, lead)
        print(f"RESULT corrupt_{name}_raises={int(err is not None)} {err or ''}")
        storage._DISK[KEY] = json.dumps(doc)
        s = QuarantiningStore(None, 1, KEY, lead=lead)
        m = await load_mapping(s, "probe")
        print(f"RESULT corrupt_{name}_load_mapping_none={int(m is None)}")
asyncio.run(main())
