"""One-shot interpreter for GIL-bound solves (#199 #290).

Started as ``python process_worker.py``, never as the parent's ``__main__``.
That is what lets test scripts (and Home Assistant) submit picklable jobs
without multiprocessing.spawn re-importing the calling script.
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path
from typing import IO, Any


def _bootstrap() -> None:
    # Running this file as a script puts its directory on sys.path[0]. That
    # directory is the integration package, so `import datetime` would bind
    # datetime.py (the HA platform) instead of the stdlib and the worker
    # cannot unpickle.
    here = Path(__file__).resolve().parent
    kept: list[str] = []
    for entry in sys.path:
        try:
            resolved = Path(entry).resolve() if entry else Path.cwd()
        except OSError:
            kept.append(entry)
            continue
        if resolved != here:
            kept.append(entry)
    sys.path[:] = kept
    parent = str(here.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)


def _describe(obj: object) -> str:
    """A description that cannot itself raise while reporting a failure."""
    try:
        return f"{type(obj).__name__}: {obj}"
    except Exception:  # noqa: BLE001 - a __str__ that raises must not kill us
        return type(obj).__name__


def _dump(stdout: IO[bytes], payload: tuple[str, Any]) -> None:
    """Write one reply, degrading an unpicklable error to its text (#511).

    Serialised before it is written: a ``dump`` that failed halfway would
    leave a partial frame in the pipe and the parent would unpickle garbage.
    """
    try:
        blob = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as err:  # noqa: BLE001 - the worker must still answer
        # A RESULT that will not pickle is a FAILED solve, not a solve whose
        # value happens to be an error object. Keeping "ok" here handed the
        # parent a RuntimeError to publish as the plan (#524) -- quieter than
        # the rc=1 this degradation replaced. "err" and "load-err" already
        # mean failure and keep their own status.
        status = "err" if payload[0] == "ok" else payload[0]
        blob = pickle.dumps(
            (status, RuntimeError(f"{_describe(payload[1])} ({_describe(err)})")),
            protocol=pickle.HIGHEST_PROTOCOL,
        )
    stdout.write(blob)
    stdout.flush()


def run_worker() -> None:
    _bootstrap()
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    while True:
        try:
            fn, args = pickle.load(stdin)
        except EOFError:
            return
        except Exception as err:  # noqa: BLE001 - #511: a job whose module the
            # child cannot resolve used to kill the worker, leaving the parent
            # a closed pipe and rc=1. Report the cause, then stop: a failed
            # load leaves the stream mid-frame, so resuming would unpickle
            # garbage. The parent respawns on its next call.
            _dump(stdout, ("load-err", err))
            return
        try:
            payload = ("ok", fn(*args))
        except Exception as err:  # noqa: BLE001 - rehydrate in the parent
            payload = ("err", err)
        _dump(stdout, payload)


if __name__ == "__main__":
    run_worker()
