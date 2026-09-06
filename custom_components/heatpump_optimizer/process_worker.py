"""One-shot interpreter for GIL-bound solves (#199 #290).

Started as ``python process_worker.py``, never as the parent's ``__main__``.
That is what lets test scripts (and Home Assistant) submit picklable jobs
without multiprocessing.spawn re-importing the calling script.
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path


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


def run_worker() -> None:
    _bootstrap()
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    while True:
        try:
            fn, args = pickle.load(stdin)
        except EOFError:
            return
        try:
            payload = ("ok", fn(*args))
        except Exception as err:  # noqa: BLE001 - rehydrate in the parent
            payload = ("err", err)
        pickle.dump(payload, stdout, protocol=pickle.HIGHEST_PROTOCOL)
        stdout.flush()


if __name__ == "__main__":
    run_worker()
