#!/usr/bin/env python3
"""D1-s3 M5: inject an exception into every except handler `enumerate.py d1-excepts` lists.

Metric (one line): per handler, with its guarded body forced to raise on every pass (a
persistent fault), what the integration's lifecycle does -- injections fired, handler entries,
phases that raised, last_update_success after each refresh, log records added over a fault-free
control run (by level, keyed on logger+template), and whether a fault-free refresh afterwards
recovers.
Count key: the injection is a raise compiled into the production try body itself (d1s3hook.py,
an import-time AST rewrite, same line numbers), so the counts are keyed on what production does
with it, never on an input attribute.

Command:
    PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/excepts_inject.py [--reach] [--only ID ...] \
        [--shard i/n] [--out PATH]
  --reach   two fault-free runs (process worker; in-process solve): which handlers' try bodies
            the workload passes, per phase -- the control arm
  default   one armed run per reached handler (JSONL to --out)
Workload (wl.py edges only, on a real asyncio loop with a ThreadPoolExecutor and scheduled tasks):
setup A (async_setup + async_setup_entry, the first refresh), refresh A1, refresh A2,
diagnostics A, unload A, restart: setup B on a fresh hass over the same persisted stores,
refresh B1, [disarm] refresh B2 (recovery), unload B.
Expected: deterministic counts (exact) on baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692;
machine: orchestrator Mac (darwin arm64), load1 ~190 (shared box) -- no RESULT is a timing.
Perturbation for a finding: named per finding in REPORT.md (a one-line handler edit, in memory).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import collections
import json
import sys
import time
import traceback
from datetime import timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d1s3hook as hook  # noqa: E402

ROWS = hook.handlers()
# --edit REL::OLD::NEW (repeatable): a finding's one-line production perturbation, applied in
# memory at import by the hook's loader; parsed here because the package imports below.
for _i, _a in enumerate(sys.argv):
    if _a == "--edit" and _i + 1 < len(sys.argv):
        hook.EDITS.append(tuple(sys.argv[_i + 1].split("::", 2)))
hook.install(ROWS)

import wl  # noqa: E402  (imports the package: after install)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as st  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer as integ  # noqa: E402
import heatpump_optimizer.coordinator as cmod  # noqa: E402
from heatpump_optimizer import diagnostics as diag  # noqa: E402

MARK, Injected = hook.MARK, hook.Injected


def _chain_has_mark(err):
    seen = set()
    while err is not None and id(err) not in seen:
        seen.add(id(err))
        if MARK in str(err) or isinstance(err, Injected):
            return True
        err = err.__cause__ or err.__context__
    return False


class RealHass(FakeHass):
    """FakeHass on a real loop: tasks are scheduled and drained, executor jobs run on a pool."""

    pool = None

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.live = []

    def async_create_task(self, coro, *a, **k):
        t = asyncio.get_running_loop().create_task(coro)
        self.live.append(t)
        return t

    def async_create_background_task(self, coro, *a, **k):
        return self.async_create_task(coro)

    async def async_add_executor_job(self, func, *args):
        return await asyncio.get_running_loop().run_in_executor(RealHass.pool, func, *args)

    async def drain(self):
        """Await every scheduled task (bounded); their exceptions are part of the phase."""
        errs = []
        for _ in range(5):
            pending = [t for t in self.live if not t.done()]
            if not pending:
                break
            await asyncio.wait(pending, timeout=60)
        for t in self.live:
            if t.done() and not t.cancelled() and t.exception() is not None:
                errs.append(t.exception())
        self.live = [t for t in self.live if not t.done()]
        return errs


def workload(tr, cap, inproc=False):
    """Run the phases on one loop; per phase: ok|raise, mark-in-chain, value, records."""
    import concurrent.futures as cf
    st._DISK.clear()
    st._VERSIONS.clear()
    RealHass.pool = cf.ThreadPoolExecutor(4)
    saved_proc = cmod._await_process
    if inproc:
        async def _inproc(hass, fn, *args):
            return await hass.async_add_executor_job(fn, *args)
        cmod._await_process = _inproc
    res = []
    state = {}

    def mkhass():
        hass = RealHass()
        hass.states.set("sensor.indoor", FakeState("21.4"))
        hass.states.set("sensor.outdoor", FakeState("-3.0"))
        hass.states.set("weather.home", FakeState("cloudy", attributes={"temperature": -3.0}))
        session = wl.FakeSession()

        async def get_forecasts(call):
            return {"weather.home": {"forecast": wl.forecast_rows()}}

        hass.services.async_register("weather", "get_forecasts", get_forecasts)
        cmod.async_get_clientsession = lambda h, *a, **k: session
        return hass

    async def setup():
        hass = mkhass()
        entry = FakeEntry(data=dict(wl.CONFIGS["all"]), entry_id="d1s3")
        hass.config_entries.entries.append(entry)
        state["hass"], state["entry"] = hass, entry
        await integ.async_setup(hass, {})
        return await integ.async_setup_entry(hass, entry)

    async def refresh():
        coord = getattr(state["entry"], "runtime_data", None)
        if coord is None or state.get("setup_failed"):
            # Home Assistant retries a failed setup (ConfigEntryNotReady): the recovery
            # refresh after a failed setup is that retry, disarmed.
            state["setup_failed"] = False
            ok = await setup()
            return bool(ok) and state["entry"].runtime_data.last_update_success
        await coord.async_refresh()
        return coord.last_update_success

    async def diagnostics():
        return bool(await diag.async_get_config_entry_diagnostics(state["hass"], state["entry"]))

    async def unload():
        return await integ.async_unload_entry(state["hass"], state["entry"])

    phases = [("setupA", setup), ("refreshA1", refresh), ("refreshA2", refresh),
              ("diagA", diagnostics), ("unloadA", unload), ("setupB", setup),
              ("refreshB1", refresh), ("refreshB2", refresh), ("unloadB", unload)]

    async def main():
        for k, (name, fn) in enumerate(phases):
            if name == "refreshB2":
                tr.armed = False
            tr.phase = name
            n0 = len(cap.records)
            dt_util.freeze((wl.START + timedelta(minutes=15 * k)).replace(tzinfo=None))
            out = {"phase": name}
            try:
                v = await fn()
                out["ok"] = True
                out["value"] = v if isinstance(v, bool) else None
            except BaseException as err:  # noqa: BLE001 - the outcome is the measurement
                out["ok"] = False
                out["err"] = f"{type(err).__name__}: {str(err)[:160]}"
                out["mark"] = _chain_has_mark(err)
                if name.startswith("setup"):
                    state["setup_failed"] = True
            hass = state.get("hass")
            if hass is not None:
                terrs = await hass.drain()
                out["task_errs"] = [f"{type(e).__name__}: {str(e)[:120]}" for e in terrs]
                out["task_mark"] = any(_chain_has_mark(e) for e in terrs)
            dt_util.freeze(None)
            tr.mark()
            out["fired"] = hook.FIRED[tr.inject["id"]] if tr.inject else 0
            out["entered"] = hook.ENTERED[tr.inject["id"]] if tr.inject else 0
            out["recs"] = [(r.levelno, r.name, str(r.msg)[:90], MARK in (r.getMessage() + (
                "".join(traceback.format_exception(*r.exc_info)) if r.exc_info else ""))) for r in cap.records[n0:]]
            res.append(out)

    try:
        asyncio.run(main())
    finally:
        cmod._await_process = saved_proc
        RealHass.pool.shutdown(wait=False, cancel_futures=True)
    return res


class PhaseTracker:
    """Which handlers' try bodies each phase passes (from the hook's PASSED counter)."""

    def __init__(self, inject=None):
        self.inject = inject
        self.phase = "?"
        self.reach = collections.defaultdict(set)
        self._snap = collections.Counter()

    @property
    def armed(self):
        return bool(hook.ARMED)

    @armed.setter
    def armed(self, value):
        hook.ARMED.clear()
        if value and self.inject is not None:
            hook.ARMED.add(self.inject["id"])

    def mark(self):
        for hid, n in hook.PASSED.items():
            if n > self._snap[hid]:
                self.reach[hid].add(self.phase)
        self._snap = collections.Counter(hook.PASSED)


def run(rows, inject=None, inproc=False):
    cap = wl.capture()
    cap.records.clear()
    hook.PASSED.clear()
    hook.FIRED.clear()
    hook.ENTERED.clear()
    hook.MODE = "persistent"
    tr = PhaseTracker(inject)
    tr.armed = True
    saved = dt_util.DEFAULT_TIME_ZONE
    dt_util.DEFAULT_TIME_ZONE = timezone.utc
    try:
        res = workload(tr, cap, inproc)
    finally:
        tr.armed = False
        dt_util.DEFAULT_TIME_ZONE = saved
    return tr, res


def summarize(ctrl, armed):
    """Per-phase record delta over the control (multiset of (level, logger, template))."""
    out = []
    for c, a in zip(ctrl, armed):
        cc = collections.Counter((l, n, m) for l, n, m, _ in c["recs"])
        ac = collections.Counter((l, n, m) for l, n, m, _ in a["recs"])
        delta = ac - cc
        out.append({
            "phase": a["phase"], "ok": a["ok"], "value": a.get("value"), "err": a.get("err"),
            "mark_escaped": a.get("mark", False), "task_errs": a.get("task_errs"),
            "task_mark": a.get("task_mark", False),
            "fired": a.get("fired", 0), "entered": a.get("entered", 0),
            "added": sum(delta.values()), "added_warn": sum(v for (l, _, _), v in delta.items() if l >= 30),
            "mark_logged": sum(1 for *_, m in a["recs"] if m),
            "added_tpl": sorted({f"{l}:{m}" for (l, _, m) in delta})[:4],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--edit", action="append", default=[], help="REL::OLD::NEW (applied at import)")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--out", default=None)
    ap.add_argument("--reached-file", default=os.path.join(HERE, "out", "reach.json"))
    a = ap.parse_args()
    rows = ROWS
    t0, th0 = time.process_time(), time.thread_time()
    if a.reach:
        rec = {"rows": rows, "reach": {}, "control": {}}
        for mode in ("proc", "inproc"):
            tr, res = run(rows, inproc=(mode == "inproc"))
            rec["reach"][mode] = {r["id"]: sorted(tr.reach.get(r["id"], ())) for r in rows}
            rec["control"][mode] = res
            print(f"RESULT reached_{mode}={sum(1 for v in rec['reach'][mode].values() if v)} handlers")
            print(f"RESULT control_{mode}_phases_ok={sum(1 for p in res if p['ok'])}/{len(res)} phases")
        os.makedirs(os.path.dirname(a.reached_file), exist_ok=True)
        json.dump(rec, open(a.reached_file, "w"), indent=1)
        both = {r["id"] for r in rows if rec["reach"]["proc"][r["id"]] or rec["reach"]["inproc"][r["id"]]}
        print(f"RESULT universe={len(rows)} handlers")
        print(f"RESULT reached={len(both)} handlers")
    else:
        rec = json.load(open(a.reached_file))
        todo = [r for r in rows if rec["reach"]["proc"].get(r["id"]) or rec["reach"]["inproc"].get(r["id"])]
        if a.only:
            todo = [r for r in rows if r["id"] in a.only]
        i, n = map(int, a.shard.split("/"))
        todo = todo[i::n]
        fh = open(a.out, "a") if a.out else sys.stdout
        for r in todo:
            mode = "proc" if rec["reach"]["proc"].get(r["id"]) else "inproc"
            tr, res = run(rows, inject=r, inproc=(mode == "inproc"))
            fh.write(json.dumps({"id": r["id"], "kind": r["kind"], "func": r["func"], "mode": mode,
                                 "fired": hook.FIRED[r["id"]], "entered": hook.ENTERED[r["id"]],
                                 "phases": summarize(rec["control"][mode], res)}) + "\n")
            fh.flush()
        print(f"RESULT injected={len(todo)} handlers")
    cpu, th = time.process_time() - t0, time.thread_time() - th0
    # deliberate work runs on the executor pool: the ratio is structural here, and no
    # RESULT of this harness is a timing (README, the FakeHass trap).
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
