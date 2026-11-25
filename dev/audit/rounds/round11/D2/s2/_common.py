"""Shared boilerplate for the D2-s2 round-11 harnesses (not a harness itself).

Import this module FIRST: it pins the BLAS threads before numpy loads, puts the
production package on sys.path (or a private patched copy of it, under
``--perturb``), and prints the RESULT trailer (thread_factor, load1, swapins).
Writes only under a temp root derived from $TMPDIR.
"""
import os
import sys

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import shutil
import tempfile
import time

ROOT = os.getcwd()
PKG = os.path.join(ROOT, "custom_components", "heatpump_optimizer")
_T0 = (time.process_time(), time.thread_time())


def setup_paths(edits=None):
    """Put the package on sys.path; with ``edits`` [(file, old, new)], a patched
    private copy instead. Each ``old`` must occur exactly once (the one-line
    production edit the perturbation names)."""
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    if not edits:
        sys.path.insert(0, os.path.join(ROOT, "custom_components"))
        return None
    tmp = tempfile.mkdtemp(prefix="d2s2_perturb_")
    dst = os.path.join(tmp, "heatpump_optimizer")
    shutil.copytree(PKG, dst)
    for fname, old, new in edits:
        path = os.path.join(dst, fname)
        src = open(path, encoding="utf-8").read()
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"perturbation anchor found {n}x in {fname}: {old!r}")
        open(path, "w", encoding="utf-8").write(src.replace(old, new))
    sys.path.insert(0, tmp)
    print(f"# perturbed copy at {tmp}: {[(f, o, n) for f, o, n in edits]}")
    return tmp


def result(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def trailer():
    cpu = time.process_time() - _T0[0]
    thr = time.thread_time() - _T0[1]
    result("thread_factor", round(cpu / thr, 4) if thr > 1e-9 else 1.0)
    try:
        result("load1", os.getloadavg()[0])
    except OSError:
        result("load1", "nan")
    swapins = "nan"
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                swapins = int(line.split()[1])
    except OSError:
        pass
    result("swapins", swapins)
