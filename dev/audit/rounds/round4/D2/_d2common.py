"""Shared RESULT/environment boilerplate for the D2 round-4 harnesses.

Not a harness. Each harness in this directory imports it after setting its
own thread pin, and each remains runnable by the single command in its own
header. Kept in one file so the three harnesses cannot drift about what a
RESULT line means.
"""
from __future__ import annotations

import os
import time


def result(name, value, unit=""):
    text = f"{value:.10g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}".rstrip(), flush=True)


class Cpu:
    """Process/thread CPU accumulator, for the thread_factor RESULT."""

    def __init__(self) -> None:
        self.process = 0.0
        self.thread = 0.0
        self._p = 0.0
        self._t = 0.0

    def __enter__(self):
        self._p, self._t = time.process_time(), time.thread_time()
        return self

    def __exit__(self, *exc):
        self.process += time.process_time() - self._p
        self.thread += time.thread_time() - self._t
        return False


def concurrent(pattern: str) -> int:
    out = os.popen(
        "ps ax -o args= | grep -E "
        f"'[s]tress\\.py|[t]ests/run\\.sh|{pattern}'"
    ).read().splitlines()
    return len(out)


def footer(cpu: Cpu, pattern: str) -> None:
    result("thread_factor", cpu.process / max(cpu.thread, 1e-9), "ratio")
    result("load1", float(os.getloadavg()[0]), "load")
    result("concurrent_processes", concurrent(pattern), "count")
    try:
        with open("/proc/vmstat") as fh:
            result(
                "swapins",
                next(int(l.split()[1]) for l in fh if l.startswith("pswpin")),
                "count",
            )
    except (OSError, StopIteration):
        # Darwin has no /proc/vmstat; vm_stat's pageins is the nearest
        # counter and is what the audit box can report.
        try:
            line = os.popen("vm_stat | grep -i 'Pageins'").read()
            result("swapins", int(line.split(":")[1].strip().rstrip(".")), "count")
        except (OSError, IndexError, ValueError):
            result("swapins", 0, "count")
