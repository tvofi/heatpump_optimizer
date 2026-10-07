"""D1-s1-51 (instrument, P11): the hastub Store decodes with stdlib json, so a stored document
Home Assistant's orjson Store refuses whole (file moved aside, async_load returns None) loads
through the stub with its healthy siblings intact and only the bad leaf scrubbed.

Metric: of 6 stored documents, each one healthy leaf "a": 1.5 plus one hostile number token
(NaN, Infinity, -Infinity, 1e400, a 401-digit integer, 2**64), count those for which
QuarantiningStore.async_load over the stub returns a different payload than over Home Assistant's
codec (orjson.loads; a decode error returns None, as helpers/storage.Store._async_load_data does).
Count key: the payload the production QuarantiningStore.async_load hands its loader.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/stub_store_codec.py [--orjson]
Expected: divergent=6 of 6; healthy_sibling_lost stub=0 vs HA=5 (exact). A healthy control document
diverges 0. --orjson (perturbation: the stub's decode swapped for orjson with HA's corrupt-file
None) -> divergent=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container, orjson 3.11.9.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio, json
import orjson
from homeassistant.helpers import storage
from heatpump_optimizer.store import QuarantiningStore, _sanitize

ORJSON = "--orjson" in sys.argv
DOCS = {
    "nan": '{"a": 1.5, "b": NaN}', "inf": '{"a": 1.5, "b": Infinity}', "-inf": '{"a": 1.5, "b": -Infinity}',
    "1e400": '{"a": 1.5, "b": 1e400}', "10**400": '{"a": 1.5, "b": 1' + "0" * 400 + '}',
    "2**64": '{"a": 1.5, "b": 18446744073709551616}',
}
CONTROL = '{"a": 1.5, "b": 2.0}'


def ha_decode(text):
    try:
        return orjson.loads(text)
    except orjson.JSONDecodeError:
        return None  # HA: 'Unrecoverable error decoding storage', file renamed .corrupt, None


if ORJSON:
    storage.json = type("J", (), {"loads": staticmethod(ha_decode), "dumps": staticmethod(json.dumps)})


async def stub_load(text):
    storage._DISK["k"] = text
    return await QuarantiningStore(None, 1, "k").async_load()


def same(x, y):
    return json.dumps(x, sort_keys=True, default=repr) == json.dumps(y, sort_keys=True, default=repr)


def main():
    div = lost_stub = lost_ha = 0
    for name, text in DOCS.items():
        got = asyncio.run(stub_load(text))
        want = _sanitize(ha_decode(text))
        d = not same(got, want)
        div += d
        lost_stub += not (isinstance(got, dict) and got.get("a") == 1.5)
        lost_ha += not (isinstance(want, dict) and want.get("a") == 1.5)
        print(f"RESULT doc_{name}: stub={got!r:.60} ha={want!r:.60} divergent={int(d)}")
    ctl = int(not same(asyncio.run(stub_load(CONTROL)), _sanitize(ha_decode(CONTROL))))
    print(f"RESULT divergent={div} of_{len(DOCS)}")
    print(f"RESULT healthy_sibling_lost_stub={lost_stub} healthy_sibling_lost_ha={lost_ha}")
    print(f"RESULT control_divergent={ctl} of_1")


main()
_rig.tail()
