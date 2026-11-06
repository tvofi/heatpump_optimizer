"""The solve worker's reply deadline, frame bound and stop-path lock bound.

    PYTHONPATH=tests/hastub python tests/worker_timeout.py

Its own script, not a section of ``features.py``: CodeQL's Python extractor
spends most of the analysis job's 45 minutes on that one 78k-line module, and
the 387 lines below took its extraction from 817-1389 s on main to over
2100 s, so ``codeql / Analyze (python)`` never finished (#3232). Here they
extract in seconds and run against the same production symbols.

``_run_in_process`` used to block in ``pickle.load`` with no deadline while it
held ``_PROCESS_LOCK``. A worker alive but silent raised nothing, so the #511
fallback never fired, every later solve and reload queued on the lock, and
Home Assistant's stop ran into the supervisor's timeout. Every check drives
the real worker process under Home Assistant's module naming.
"""
from __future__ import annotations

import asyncio as _asyncio
import logging as _logging
import os as _os
import sys
from pathlib import Path as _Path
from types import SimpleNamespace

from harness import FakeHass, Results
import harness as _harness

_root = str(_Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

# Home Assistant's spelling of the package: pickle ships a function by its
# qualified name, so the worker must be driven under the name a real install
# uses (#511).
import custom_components.heatpump_optimizer.coordinator as _coord  # noqa: E402

R = Results("Solve worker deadlines")


def _submit(run, fn, args):
    """Round-trip ``fn`` through the real worker. The error IS the measurement."""
    try:
        return None, run(fn, args)
    except Exception as err:  # noqa: BLE001
        return err, None


class _Hass(FakeHass):
    """Records what reached the executor, so a fallback cannot hide."""

    def __init__(self) -> None:
        super().__init__()
        self.jobs = []
        self.issues = []

    async def async_add_executor_job(self, func, *args):
        self.jobs.append(func)
        return func(*args)


class _LogSink(_logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=_logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(record)


def _solve(optimizer):
    """``_await_optimize``, keeping what it RAISED apart from what it RETURNED."""
    hass, sink = _Hass(), _LogSink()
    logger = _logging.getLogger(_coord.__name__)
    logger.addHandler(sink)
    try:
        try:
            out = _asyncio.run(_coord._await_optimize(hass, optimizer, "STATE"))
            raised, returned = None, out
        except Exception as err:  # noqa: BLE001
            raised, returned = err, None
    finally:
        logger.removeHandler(sink)
    return raised, returned, hass, [r for r in sink.records if r.levelno >= 30]


_parent = _os.getpid()

# ---------------------------------------------------------------------------
R.section("worker read timeout — a silent worker is reaped, not waited on")

# ``_run_in_process`` blocked in ``pickle.load`` with no deadline while it held
# ``_PROCESS_LOCK``. A worker that was alive but never answered (one install:
# no completed solve for ~55 minutes, one core busy) raised nothing, so the
# #511 fallback never fired, every later solve and reload queued on the lock,
# and Home Assistant's stop ran into the supervisor's timeout.
import threading as _wt_threading  # noqa: E402
import time as _wt_time  # noqa: E402

_wt_timeout_cls = getattr(_coord, "ProcessWorkerTimeout", None)
_wt_saved = (_coord.PROCESS_REPLY_TIMEOUT_S, _coord._SHUTDOWN_LOCK_TIMEOUT_S)
# Design-value pins: every timing check below shortens these, so none of
# them reads the shipped values. The reply deadline is the band its comment
# derives -- at least 4x the 426 s slowest solve measured, at most half an
# hour so a hung worker is reaped well inside the ~55-minute hang it bounds.
# The stop path's lock wait is the 5 s bookkeeping bound, far inside Home
# Assistant's 30 s close stage; a longer one buys the swap nothing.
R.check(
    "the reply deadline sits in its derived band: 4 x 426 s <= deadline <= 30 min",
    4 * 426 <= _wt_saved[0] <= 30 * 60,
    f"PROCESS_REPLY_TIMEOUT_S = {_wt_saved[0]!r}",
)
R.check(
    "the stop path's lock wait and the timed-out reap stay at the 5 s design bound",
    _wt_saved[1] == 5.0,
    f"_SHUTDOWN_LOCK_TIMEOUT_S = {_wt_saved[1]!r}",
)
try:
    # Spawns and first imports run under the real deadline: only the
    # measured call gets the short one, so a slow host cannot fail a check
    # by starting a worker.
    _wt_pid_before = _coord._run_in_process(_os.getpid, ())
    _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
    # Null control first, on the warm worker: a reply inside the deadline is
    # untouched by it.
    _wt_ok_err, _wt_ok_out = _submit(_coord._run_in_process, _wt_time.sleep, (0.05,))
    _wt_ok_pid = _coord._run_in_process(_os.getpid, ())
    R.check(
        "null control: a job that answers in time returns and keeps its worker",
        _wt_ok_err is None and _wt_ok_out is None and _wt_ok_pid == _wt_pid_before,
        f"raised {_wt_ok_err!r}; pid {_wt_pid_before} -> {_wt_ok_pid}",
    )
    _wt_t0 = _wt_time.monotonic()
    _wt_err, _wt_out = _submit(_coord._run_in_process, _wt_time.sleep, (30,))
    _wt_elapsed = _wt_time.monotonic() - _wt_t0
    _wt_lock_free = _coord._PROCESS_LOCK.acquire(blocking=False)
    if _wt_lock_free:
        _coord._PROCESS_LOCK.release()
    _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
    _wt_pid_after = _coord._run_in_process(_os.getpid, ())
    R.check(
        "a worker that gives no reply within the deadline raises ProcessWorkerTimeout",
        _wt_timeout_cls is not None and isinstance(_wt_err, _wt_timeout_cls)
        and _wt_out is None and _wt_elapsed < 10,
        f"raised {_wt_err!r} after {_wt_elapsed:.1f} s; returned {_wt_out!r}",
    )
    R.check(
        "and it frees the lock and the next job gets a fresh worker",
        _wt_lock_free and _wt_pid_after not in (_wt_pid_before, _parent),
        f"lock_free={_wt_lock_free} before={_wt_pid_before} after={_wt_pid_after}",
    )

    # ``_await_optimize`` must not rerun the timed-out job in process: the
    # same job would hold an executor thread just as long. Warm the child's
    # imports of the harness under the real deadline first.
    _solve(_harness.SleepyOptimizer(0))
    _coord.PROCESS_REPLY_TIMEOUT_S = 5.0
    _wt_fast_err, _wt_fast_plan, _wt_fast_hass, _ = _solve(_harness.SleepyOptimizer(0.05))
    R.check(
        "null control: a solve inside the deadline returns its plan through the worker",
        _wt_fast_err is None and isinstance(_wt_fast_plan, tuple)
        and _wt_fast_plan[0] == "slept" and _wt_fast_plan[1] != _parent
        and _wt_fast_hass.jobs == [_coord._run_in_process],
        f"raised {_wt_fast_err!r}; returned {_wt_fast_plan!r}",
    )
    _wt_raised, _wt_plan, _wt_hass, _wt_warned = _solve(_harness.SleepyOptimizer(30))
    R.check(
        "_await_optimize keeps the last plan on a timeout: translated UpdateFailed, no in-process solve",
        _wt_plan is None
        and type(_wt_raised).__name__ == "UpdateFailed"
        and getattr(_wt_raised, "translation_key", None) == "process_worker_timeout"
        and _wt_hass.jobs == [_coord._run_in_process]
        and [i for i in _wt_hass.issues if i[1] == "solve_worker_fallback"] == [],
        f"raised {_wt_raised!r}; returned {_wt_plan!r}; jobs={_wt_hass.jobs!r} "
        f"issues={_wt_hass.issues!r}",
    )

    # A timeout repeated every cycle warns ONCE, then says "Resolved" on the
    # first solve the worker carries again (R10 N-log-flood: log_held).
    _wt_latch_sink = _LogSink()
    _wt_latch_sink.setLevel(_logging.INFO)
    _wt_latch_log = _logging.getLogger(_coord.log_held.__module__)
    _wt_latch_log.addHandler(_wt_latch_sink)
    _wt_latch_level = _wt_latch_log.level
    _wt_latch_log.setLevel(_logging.INFO)
    _wt_one_hass = _Hass()
    try:
        for _wt_n in range(2):
            try:
                _asyncio.run(_coord._await_optimize(
                    _wt_one_hass, _harness.SleepyOptimizer(30), "STATE"))
            except Exception:  # noqa: BLE001 - the UpdateFailed is checked above
                pass
        _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
        _asyncio.run(_coord._await_optimize(
            _wt_one_hass, _harness.SleepyOptimizer(0), "STATE"))
    finally:
        _wt_latch_log.removeHandler(_wt_latch_sink)
        _wt_latch_log.setLevel(_wt_latch_level)
        _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
    _wt_latch_msgs = [(r.levelno, r.getMessage()) for r in _wt_latch_sink.records
                      if "process worker" in r.getMessage() or "process_worker" in r.getMessage()
                      or "Resolved" in r.getMessage()]
    R.check(
        "two timeouts in a row warn once, and the next solve logs the recovery",
        [lv for lv, _ in _wt_latch_msgs] == [_logging.WARNING, _logging.INFO],
        f"latch records={_wt_latch_msgs!r}",
    )

    # ``_await_off_loop`` (replay, recovery, sysid, advisor) must not rerun a
    # timed-out job on the executor, where it would run with no deadline.
    _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
    _coord._run_in_process(_os.getpid, ())  # warm the fresh worker
    _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
    _wt_ol_ok_hass = _Hass()
    _wt_ol_ok = _asyncio.run(_coord._await_off_loop(_wt_ol_ok_hass, _os.getpid))
    R.check(
        "null control: an off-loop job inside the deadline returns through the worker",
        _wt_ol_ok not in (None, _parent) and _wt_ol_ok_hass.jobs == [_coord._run_in_process],
        f"returned {_wt_ol_ok!r}; jobs={_wt_ol_ok_hass.jobs!r}",
    )
    _wt_ol_hass = _Hass()
    _wt_t2 = _wt_time.monotonic()
    try:
        _asyncio.run(_coord._await_off_loop(_wt_ol_hass, _wt_time.sleep, 30))
        _wt_ol_err = None
    except Exception as _wt_e:  # noqa: BLE001
        _wt_ol_err = _wt_e
    _wt_ol_s = _wt_time.monotonic() - _wt_t2
    R.check(
        "_await_off_loop raises a timeout to its caller instead of rerunning it on the executor",
        _wt_timeout_cls is not None and isinstance(_wt_ol_err, _wt_timeout_cls)
        and _wt_ol_hass.jobs == [_coord._run_in_process] and _wt_ol_s < 10,
        f"raised {_wt_ol_err!r} after {_wt_ol_s:.1f} s; jobs={_wt_ol_hass.jobs!r}",
    )

    # The off-loop route holds its timeout warning per job as well: without
    # it a timeout there is invisible at the default log level, because the
    # replay and the sensor advisor catch it and log at DEBUG. Two timeouts of
    # one job warn once, naming the job; its next completion logs "Resolved".
    _wt_olw_sink = _LogSink()
    _wt_olw_sink.setLevel(_logging.INFO)
    _wt_olw_log = _logging.getLogger(_coord.log_held.__module__)
    _wt_olw_log.addHandler(_wt_olw_sink)
    _wt_olw_level = _wt_olw_log.level
    _wt_olw_log.setLevel(_logging.INFO)
    _wt_olw_hass = _Hass()
    try:
        for _wt_n in range(2):
            try:
                _asyncio.run(_coord._await_off_loop(_wt_olw_hass, _wt_time.sleep, 30))
            except Exception:  # noqa: BLE001 - the raise is checked above
                pass
        _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
        _asyncio.run(_coord._await_off_loop(_wt_olw_hass, _wt_time.sleep, 0))
    finally:
        _wt_olw_log.removeHandler(_wt_olw_sink)
        _wt_olw_log.setLevel(_wt_olw_level)
        _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
    _wt_olw_msgs = [(r.levelno, r.getMessage()) for r in _wt_olw_sink.records
                    if "sleep" in r.getMessage()]
    R.check(
        "two off-loop timeouts of one job warn once, naming it, and its next completion logs the recovery",
        [lv for lv, _ in _wt_olw_msgs] == [_logging.WARNING, _logging.INFO]
        and "Resolved" in _wt_olw_msgs[1][1]
        and all("off loop timeout:sleep" in m or "sleep skipped" in m for _, m in _wt_olw_msgs),
        f"latch records={_wt_olw_msgs!r}",
    )

    # The reply frame is read under its own deadline: a worker stopped
    # mid-write after serialising its reply (SIGSTOP, a stalled host) must
    # not hold ``pickle.load`` and the lock (#3232 round 3).
    _wt_frame_saved = _coord._REPLY_FRAME_TIMEOUT_S
    R.check(
        "the reply frame deadline stays at its 60 s design value",
        _wt_frame_saved == 60.0,
        f"_REPLY_FRAME_TIMEOUT_S = {_wt_frame_saved!r}",
    )
    _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
    _coord._run_in_process(_os.getpid, ())  # warm a worker under the real deadline
    _wt_big_t0 = _wt_time.monotonic()
    _wt_big_err, _wt_big = _submit(_coord._run_in_process, bytes, (50_000_000,))
    _wt_big_s = _wt_time.monotonic() - _wt_big_t0
    R.check(
        "null control: a 50 MB reply arrives whole through the frame reader, inside its deadline",
        _wt_big_err is None and isinstance(_wt_big, bytes) and len(_wt_big) == 50_000_000
        and _wt_big_s < _wt_frame_saved,
        f"raised {_wt_big_err!r}; {len(_wt_big or b'')} bytes in {_wt_big_s:.2f} s",
    )
    _wt_big = None
    _coord._REPLY_FRAME_TIMEOUT_S = 0.5
    try:
        _wt_split_ok_err, _wt_split_ok = _submit(
            _coord._run_in_process, _harness.split_reply, (0.05,))
        R.check(
            "null control: a reply frame written in two halves inside the frame deadline returns",
            _wt_split_ok_err is None and _wt_split_ok == "split",
            f"raised {_wt_split_ok_err!r}; returned {_wt_split_ok!r}",
        )
        _coord._shutdown_process_pool()  # that child exited after its frame
        _coord._run_in_process(_os.getpid, ())  # warm a fresh one
        _wt_split_t0 = _wt_time.monotonic()
        _wt_split_err, _wt_split_out = _submit(
            _coord._run_in_process, _harness.split_reply, (30,))
        _wt_split_s = _wt_time.monotonic() - _wt_split_t0
        _wt_split_free = _coord._PROCESS_LOCK.acquire(blocking=False)
        if _wt_split_free:
            _coord._PROCESS_LOCK.release()
        R.check(
            "a worker stopped mid-reply raises ProcessWorkerTimeout, is reaped and frees the lock",
            _wt_timeout_cls is not None and isinstance(_wt_split_err, _wt_timeout_cls)
            and "mid-reply" in str(_wt_split_err) and _wt_split_out is None
            and _wt_split_s < 10 and _wt_split_free
            and _coord._PROCESS_WORKER is None,
            f"raised {_wt_split_err!r} after {_wt_split_s:.1f} s; returned {_wt_split_out!r}; "
            f"lock_free={_wt_split_free} worker={_coord._PROCESS_WORKER!r}",
        )
        # A child that dies mid-frame is an end of stream, a transport fault
        # the fallback routes around at once, never a wait out to the deadline.
        _coord._run_in_process(_os.getpid, ())  # warm a fresh one
        _wt_eof_t0 = _wt_time.monotonic()
        _wt_eof_err, _ = _submit(
            _coord._run_in_process, _harness.split_reply, (0.05, False))
        _wt_eof_s = _wt_time.monotonic() - _wt_eof_t0
        R.check(
            "a worker that dies mid-reply is a transport fault, not a timeout",
            isinstance(_wt_eof_err, _coord.ProcessWorkerUnavailable)
            and _wt_timeout_cls is not None and not isinstance(_wt_eof_err, _wt_timeout_cls)
            and _wt_eof_s < 0.5,
            f"raised {_wt_eof_err!r} after {_wt_eof_s:.2f} s",
        )
    finally:
        _coord._REPLY_FRAME_TIMEOUT_S = _wt_frame_saved
    _coord.PROCESS_REPLY_TIMEOUT_S = 0.5

    # The reader's ``readline`` (only text opcodes ask) returns one line and
    # leaves the rest of the frame unread, under the same deadline.
    _wt_rl_r, _wt_rl_w = _os.pipe()
    try:
        _os.write(_wt_rl_w, b"ab\ncd")
        _wt_rl = _coord._frame_reader(_wt_rl_r, 1.0)
        _wt_rl_line, _wt_rl_rest = _wt_rl.readline(), _wt_rl.read(2)
        _os.close(_wt_rl_w)
        _wt_rl_w = None
        _wt_rl_tail = _wt_rl.readline()
    finally:
        _os.close(_wt_rl_r)
        if _wt_rl_w is not None:
            _os.close(_wt_rl_w)
    R.check(
        "the frame reader's readline returns one line, the rest stays unread, and it stops at end of stream",
        (_wt_rl_line, _wt_rl_rest, _wt_rl_tail) == (b"ab\n", b"cd", b""),
        f"line={_wt_rl_line!r} rest={_wt_rl_rest!r} tail={_wt_rl_tail!r}",
    )

    # A worker whose pipe lands at a descriptor >= FD_SETSIZE (1024) -- Home
    # Assistant raises its soft fd limit past it -- must still be waited on
    # with the deadline, not read as a transport fault (select.select refuses
    # such a descriptor; the #3232 review's regression).
    import resource as _wt_resource  # noqa: E402
    import gc as _wt_gc  # noqa: E402

    _wt_soft, _wt_hard = _wt_resource.getrlimit(_wt_resource.RLIMIT_NOFILE)
    _wt_fds = []
    _wt_hi_fd = -1
    _wt_hi_ok = _wt_hi_err = _wt_hi_warm = None
    try:
        _wt_want = 1200
        if _wt_soft != _wt_resource.RLIM_INFINITY and _wt_soft < _wt_want:
            _wt_resource.setrlimit(_wt_resource.RLIMIT_NOFILE, (
                _wt_want if _wt_hard == _wt_resource.RLIM_INFINITY else min(_wt_want, _wt_hard),
                _wt_hard))
        # Reap first, then fill: the old worker's pipes freed after the fill
        # would hand the respawn low descriptors again.
        _coord._shutdown_process_pool()
        _wt_gc.collect()
        while len(_wt_fds) < 1100:
            _wt_fds.append(_os.open(_os.devnull, _os.O_RDONLY))
        _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]
        _wt_hi_warm, _ = _submit(_coord._run_in_process, _os.getpid, ())
        if _coord._PROCESS_WORKER is not None:
            _wt_hi_fd = _coord._PROCESS_WORKER.stdout.fileno()
        _coord.PROCESS_REPLY_TIMEOUT_S = 0.5
        _wt_hi_ok, _ = _submit(_coord._run_in_process, _wt_time.sleep, (0.05,))
        _wt_hi_err, _ = _submit(_coord._run_in_process, _wt_time.sleep, (30,))
    finally:
        for _wt_fd in _wt_fds:
            _os.close(_wt_fd)
        _coord._shutdown_process_pool()
        _wt_resource.setrlimit(_wt_resource.RLIMIT_NOFILE, (_wt_soft, _wt_hard))
    R.check(
        "a worker pipe at fd >= 1024 answers in time and still times out as a timeout",
        _wt_hi_warm is None and _wt_hi_fd >= 1024 and _wt_hi_ok is None
        and _wt_timeout_cls is not None and type(_wt_hi_err) is _wt_timeout_cls,
        f"warm raised {_wt_hi_warm!r}; stdout fd={_wt_hi_fd}; fast job raised {_wt_hi_ok!r}; slow job raised {_wt_hi_err!r}",
    )
    _coord.PROCESS_REPLY_TIMEOUT_S = _wt_saved[0]

    # The stop path: a lock held past the kill must not hold the stop.
    _coord._SHUTDOWN_LOCK_TIMEOUT_S = 0.2
    _coord._run_in_process(_os.getpid, ())
    _wt_release = _wt_threading.Event()

    def _wt_hold() -> None:
        with _coord._PROCESS_LOCK:
            _wt_release.wait(10)

    _wt_holder = _wt_threading.Thread(target=_wt_hold, daemon=True)
    _wt_holder.start()
    _wt_time.sleep(0.05)
    _wt_t1 = _wt_time.monotonic()
    _coord._shutdown_process_pool()
    _wt_stop_s = _wt_time.monotonic() - _wt_t1
    _wt_release.set()
    _wt_holder.join(5)
    R.check(
        "the stop path returns within its lock timeout while the lock is held",
        _wt_stop_s < 3,
        f"_shutdown_process_pool took {_wt_stop_s:.2f} s with the lock held",
    )
finally:
    _coord.PROCESS_REPLY_TIMEOUT_S, _coord._SHUTDOWN_LOCK_TIMEOUT_S = _wt_saved

# The diagnose service calls ``_await_process`` directly: a worker timeout or
# an unusable worker reaches its caller as the service-failed shape the other
# services raise, not as the worker's own RuntimeError (#3232 round 3).
from heatpump_optimizer import services as _wt_svc  # noqa: E402
from homeassistant.exceptions import HomeAssistantError as _wt_HAE  # noqa: E402

_wt_svc_coord_mod = sys.modules[_wt_svc.__name__.rsplit(".", 1)[0] + ".coordinator"]


class _WtDiagCoord:
    def __init__(self, outcome):
        self.outcome = outcome

    async def async_diagnose_interval(self):
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome


def _wt_diagnose(outcome):
    saved = _wt_svc._manual_targets
    _wt_svc._manual_targets = lambda hass, target: [("e1", _WtDiagCoord(outcome))]
    try:
        return None, _asyncio.run(_wt_svc.handle_diagnose_interval(
            None, SimpleNamespace(data={})))
    except Exception as err:  # noqa: BLE001 - the error IS the measurement
        return err, None
    finally:
        _wt_svc._manual_targets = saved


_wt_dg_ok_err, _wt_dg_ok = _wt_diagnose({"residual": 0.1})
R.check(
    "null control: a diagnosis that runs is returned by the service",
    _wt_dg_ok_err is None and _wt_dg_ok == {"diagnosis": {"e1": {"residual": 0.1}}},
    f"raised {_wt_dg_ok_err!r}; returned {_wt_dg_ok!r}",
)
for _wt_dg_exc in (
    _wt_svc_coord_mod.ProcessWorkerTimeout("process worker gave no reply within 1800 s"),
    _wt_svc_coord_mod.ProcessWorkerUnavailable("process worker cannot start: boom"),
):
    _wt_dg_err, _ = _wt_diagnose(_wt_dg_exc)
    R.check(
        f"a diagnosis failing with {type(_wt_dg_exc).__name__} reaches the service caller translated",
        isinstance(_wt_dg_err, _wt_HAE)
        and not isinstance(_wt_dg_err, _wt_svc_coord_mod.ProcessWorkerUnavailable)
        and getattr(_wt_dg_err, "translation_key", None) == "diagnose_interval_failed"
        and getattr(_wt_dg_err, "translation_placeholders", None)
        == {"entry_ids": "e1", "error": str(_wt_dg_exc)},
        f"raised {_wt_dg_err!r}",
    )

_coord._shutdown_process_pool()
sys.exit(R.close("worker deadline checks"))
