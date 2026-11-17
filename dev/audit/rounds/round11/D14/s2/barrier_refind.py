"""D14.M3 re-find (D14-s2, round 11): do the AST barriers of N-log-flood and N-no-expiry re-find their own instances at the pre-fix tree?

Metric, per class: the number of the ledger's listed instance functions
(bugclasses.json `instances`, the `sw:` rows naming a package function) that
the class's barrier verdict flags when its baseline function and reasoned list
(tests/entities.py ``_r10_unlatched_logs`` + ``_R10_LOG_ALLOWED_BY_REASON`` and
``_r10_covering_lookups`` + ``_R10_COVERING_ALLOWED``, extracted by AST and
exec'd, never copied) are run over the package sources of a given tree.
Key: the barrier's own verdict dict, keyed (module, function).

Arms:
  pre-fix   the package at d7b1712297^1 (main before #2336, the PR that fixed
            the instances and landed both barriers), read with `git show`
  baseline  the package at the export root: must flag 0 (null control)
Perturbation (``--plant``): the baseline package with one listed instance
re-introduced in memory (an unlatched ``_LOGGER.warning`` appended to
coordinator ``_tariff_hours``'s module as a top-level function of that name,
and one ``bisect_right(s, now) - 1`` in a ``forecast_outdoor_now``) -> each
baseline count rises 0 -> 1.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/barrier_refind.py [--plant]
  (needs this checkout's git for the pre-fix arm; prints SKIP otherwise)
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: printed per class, exact (counts, no timing).
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import ast
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

PREFIX = "d7b1712297^1"
PKG = "custom_components/heatpump_optimizer"
WANT = {
    "N-log-flood": ("_r10_unlatched_logs", ("_R10_LATCH_WORD", "_R10_LOG_ALLOWED_BY_REASON", "_R10_LOG_ALLOWED")),
    "N-no-expiry": ("_r10_covering_lookups", ("_R10_COVERING_ALLOWED",)),
}


def _barriers():
    tree = ast.parse(Path("tests/entities.py").read_text())
    names = {"_r10_functions"} | {f for f, _ in WANT.values()} | {a for _, al in WANT.values() for a in al}
    keep = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in names:
            keep.append(n)
        elif isinstance(n, ast.Assign) and any(getattr(t, "id", "") in names for t in n.targets):
            keep.append(n)
    ns = {"ast": ast, "Counter": Counter, "re": re}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "tests/entities.py", "exec"), ns)
    allowed = {
        "N-log-flood": dict(ns["_R10_LOG_ALLOWED"]),
        "N-no-expiry": {k: v[0] for k, v in ns["_R10_COVERING_ALLOWED"].items()},
    }
    return {k: (ns[f], allowed[k]) for k, (f, _) in WANT.items()}


def _verdict(fn, allowed, sources):
    found = fn(sources)
    return {k: (found.get(k, 0), allowed.get(k, 0)) for k in set(found) | set(allowed)
            if found.get(k, 0) != allowed.get(k, 0)}


def _instances(ledger, cls):
    out = []
    for row in ledger[cls]["instances"]:
        m = re.search(r"sw:custom_components/heatpump_optimizer/(\w+\.py)::(?:\w+\.)?(\w+)$", str(row))
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def _tree_sources(ref):
    try:
        names = subprocess.run(["git", "ls-tree", "--name-only", f"{ref}:{PKG}"], capture_output=True,
                               text=True, check=True).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return {n: subprocess.run(["git", "show", f"{ref}:{PKG}/{n}"], capture_output=True, text=True,
                              check=True).stdout for n in names if n.endswith(".py")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    t0, c0 = time.thread_time(), time.process_time()
    ledger = json.loads(Path("dev/audit/config/bugclasses.json").read_text())
    bars = _barriers()
    base = {p.name: p.read_text() for p in sorted(Path(PKG).glob("*.py"))}
    if a.plant:
        base = dict(base)
        base["coordinator.py"] += ("\n\ndef _tariff_hours(self):\n    _LOGGER.warning('x')\n"
                                   "\n\ndef forecast_outdoor_now(s, now):\n    return s[bisect_right(s, now) - 1]\n")
    pre = _tree_sources(PREFIX)
    for cls, (fn, allowed) in bars.items():
        inst = _instances(ledger, cls)
        print(f"# {cls}: {len(inst)} listed package-function instances: {inst}")
        for arm, src in (("prefix", pre), ("baseline", base)):
            if src is None:
                print(f"SKIP {cls} {arm}: no git")
                continue
            v = _verdict(fn, allowed, src)
            hit = [i for i in inst if i in v]
            for i in inst:
                print(f"SEAM {cls} arm={arm} {i[0]}::{i[1]} flagged={'yes' if i in v else 'no'} "
                      f"found/allowed={v.get(i, 'match')}")
            print(f"RESULT {cls.replace('-', '_')}_{arm}_refound={len(hit)} of {len(inst)}")
            print(f"RESULT {cls.replace('-', '_')}_{arm}_mismatches={len(v)}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
