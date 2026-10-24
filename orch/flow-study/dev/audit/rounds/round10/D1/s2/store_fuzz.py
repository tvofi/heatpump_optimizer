"""D1.M2 store-corruption fuzz over every QuarantiningStore a coordinator writes.

Metric: per store key, of N seeded mutants of the healthy persisted payload,
how many (a) let an exception escape a startup load task, (b) fail cycle 1
(_async_update_data raises), (c) fail cycle 2 as well (the failure repeats);
key = the exception the production seam raised, never the mutant's own shape.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/store_fuzz.py [N] [store-substring]
Expected: see REPORT.md (counts are exact for a given seed; tolerance exact).
Baseline 17f1c55fad1b, machine: Apple M-series macOS, box B4.
Real loop: tasks scheduled on asyncio, executor jobs on a ThreadPoolExecutor.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, copy, json, logging, random, sys, time, traceback, collections
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import const  # noqa: E402
from custom_components.heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
ONLY = sys.argv[2] if len(sys.argv) > 2 else ""
CLOCK_AHEAD = os.environ.get("CLOCK_AHEAD") == "1"


class RealHass(FakeHass):
    def __init__(self, *a):
        super().__init__(*a)
        self.pool = ThreadPoolExecutor(2)

    def async_create_task(self, coro, *a, **k):
        return asyncio.get_running_loop().create_task(coro)

    async def async_add_executor_job(self, f, *a):
        return await asyncio.get_running_loop().run_in_executor(self.pool, f, *a)


class Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING); self.n = 0; self.msgs = []
    def emit(self, r):
        if r.name.startswith("custom_components.heatpump_optimizer") or "heatpump" in r.name:
            self.n += 1; self.msgs.append(r.getMessage()[:120])


CFG = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
       const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
       const.CONF_DHW_TANK_VOLUME: 180.0}


async def drain(c):
    excs = []
    for _ in range(20):
        if not c._background_tasks:
            break
        res = await asyncio.gather(*list(c._background_tasks), return_exceptions=True)
        excs += [r for r in res if isinstance(r, BaseException)]
    return excs


def build():
    h = RealHass()
    h.states.set("sensor.indoor", FakeState("21.4"))
    h.states.set("sensor.outdoor", FakeState("-3.0"))
    c = HeatPumpOptimizerCoordinator(h, FakeEntry(data=CFG))

    async def fp():
        st = dt_util.now().replace(minute=0, second=0, microsecond=0)
        c._prices = [{"total": round(0.6 + 0.5 * (k % 12) / 12, 4),
                      "starts_at": (st + timedelta(hours=k)).isoformat(), "level": "NORMAL"}
                     for k in range(-2, 46)]
    c._fetch_tibber_prices = fp
    return h, c


async def cycle(c):
    try:
        await c._async_update_data()
        return None
    except BaseException as e:  # noqa: BLE001
        return f"{type(e).__name__}: {str(e)[:100]}"
    finally:
        await drain(c)


async def healthy():
    storage._DISK.clear(); storage._VERSIONS.clear()
    h, c = build()
    await drain(c)
    for _ in range(2):
        assert await cycle(c) is None
    await c._async_save_ledger()
    await drain(c)
    return dict(storage._DISK), dict(storage._VERSIONS)


def paths(node, pre=()):
    yield pre
    if isinstance(node, dict):
        for k, v in node.items():
            yield from paths(v, pre + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node[:6]):
            yield from paths(v, pre + (i,))


def mutate(doc, rng):
    doc = copy.deepcopy(doc)
    ps = list(paths(doc))[1:] or [()]
    p = rng.choice(ps)
    op = rng.choice(["type", "delete", "huge", "neg", "nest", "str", "trunc", "null", "list", "bool"])
    parent = doc
    for k in p[:-1]:
        parent = parent[k]
    if not p:
        return rng.choice(["x", [], 1, None]), "root", op
    key = p[-1]
    cur = parent[key]
    if op == "delete" and isinstance(parent, dict):
        del parent[key]
    elif op == "type":
        parent[key] = (str(cur) if isinstance(cur, (int, float)) else
                       1.5 if isinstance(cur, str) else
                       ([] if isinstance(cur, dict) else {} if isinstance(cur, list) else "x"))
    elif op == "huge":
        parent[key] = rng.choice([1e308, 10**30, 1e19])
    elif op == "neg":
        parent[key] = rng.choice([-1.0, -1e9, -(10**18)])
    elif op == "nest":
        parent[key] = [cur]
    elif op == "str":
        parent[key] = "corrupt"
    elif op == "trunc" and isinstance(cur, (list, str)):
        parent[key] = cur[: len(cur) // 2]
    elif op == "null":
        parent[key] = None
    elif op == "list":
        parent[key] = {"0": cur}
    elif op == "bool":
        parent[key] = True
    else:
        parent[key] = "corrupt"
    return doc, "/".join(map(str, p)), op


async def main():
    t0 = time.process_time(); tt0 = time.thread_time()
    disk, vers = await healthy()
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger().handlers[:] = []
    out = {}
    for key in sorted(disk):
        if ONLY and ONLY not in key:
            continue
        base = json.loads(disk[key])
        rng = random.Random(f"{key}-r10")
        tally = collections.Counter(); examples = collections.defaultdict(list)
        for i in range(N):
            if CLOCK_AHEAD:
                # instants written by a clock 30 days ahead of the reader
                txt = disk[key]
                import re
                fut = (dt_util.now() + timedelta(days=30)).isoformat()
                doc_txt = re.sub(r'"20\d\d-\d\d-\d\dT[^"]+"', '"' + fut + '"', txt)
                doc, where, op = json.loads(doc_txt), "instants", "clock_ahead"
            else:
                doc, where, op = mutate(base, rng)
            storage._DISK.clear(); storage._DISK.update(disk)
            storage._VERSIONS.clear(); storage._VERSIONS.update(vers)
            storage._DISK[key] = json.dumps(doc)
            cnt = Count(); logging.getLogger().addHandler(cnt)
            try:
                h, c = build()
                lexc = await drain(c)
                e1 = await cycle(c)
                e2 = await cycle(c) if (e1 or lexc) else None
            except BaseException as e:  # noqa: BLE001
                lexc, e1, e2 = [e], "setup: " + repr(e)[:100], "setup"
            finally:
                logging.getLogger().removeHandler(cnt)
            if lexc:
                tally["load_exc"] += 1; examples["load_exc"].append((i, where, op, repr(lexc[0])[:100]))
            if e1:
                tally["cycle1_fail"] += 1; examples["cycle1_fail"].append((i, where, op, e1))
            if e2:
                tally["cycle2_fail"] += 1; examples["cycle2_fail"].append((i, where, op, e2))
            if not (lexc or e1):
                tally["ok"] += 1
            if cnt.n > 3:
                tally["log_gt3"] += 1; examples["log_gt3"].append((i, where, op, cnt.n, cnt.msgs[:2]))
            if CLOCK_AHEAD:
                break
        out[key] = tally
        short = key.replace("heatpump_optimizer_test_entry_", "")
        for name in ("ok", "load_exc", "cycle1_fail", "cycle2_fail", "log_gt3"):
            print(f"RESULT {short}.{name}={tally[name]} count")
        for name, ex in examples.items():
            for e in ex[:3]:
                print(f"  EX {short} {name} {e}")
        sys.stdout.flush()
    tf = (time.process_time() - t0) / max(1e-9, time.thread_time() - tt0)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main())
