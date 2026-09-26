"""Picklable jobs for worker_protocol.py (imported by the child through PYTHONPATH)."""
import sys


def ok(x):
    return x * 2


def raises(x):
    raise ValueError(f"job error {x}")


class _NoPickle:
    def __reduce__(self):
        raise TypeError("refuses to pickle")


def unpicklable(_x):
    return _NoPickle()


def prints(x):
    print("progress", x)  # a library or job writing to stdout
    return x


def exits(_x):
    raise SystemExit(3)
