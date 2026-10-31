"""R10-NIGHTLY-PYSPY-RETRY mutation proof: each mutant of tests/nightly_ha.py's
positive control against the A15 py-spy checks of tests/entities.py.

The checks run from ``_HB_BOTH = `` up to ``_hb_cmd = _nightly.docker_command``,
the block that drives ``_async_hb_control`` against stub samplers, on a copy of
nightly_ha.py with one substitution. M0 substitutes nothing: the null control.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py

Prints ``<id> KILLED by: <check>`` or ``<id> SURVIVED`` per mutant, then
``SUMMARY killed=<k> survived=<s> null=<ok|FAIL>``.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
MUTANTS = {
    "M0-null": ("", ""),
    "M1-one-try": ("for _ in range(tries):", "for _ in range(1):"),
    "M2-timeout-30": ("timeout=self.spy_timeout,", "timeout=30,"),
    "M3-any-output": ("        if all(hb_control_reading(summary)):\n            break",
                      '        if summary["dumps"]:\n            break'),
    "M4-no-hold": ("hold is not None and not hold.is_set() and now < bound", "False"),
    "M5-no-release": ("                    self.dumped.set()\n", ""),
    "M6-check-any-rc0": ('"_hb_spin" in d.split("py-spy rc=0:", 1)[1]', "True"),
    "M7-control-no-hold": ("call_soon(_hb_spin, HB_CONTROL_S, dumped)",
                           "call_soon(_hb_spin, HB_CONTROL_S)"),
    "M8-check-split-tries": ("        any(all(r) for r in readings),",
                             "        all(any(r[i] for r in readings) for i in range(3)),"),
    "M9-rc-ignored": ('d.split("py-spy rc=0:", 1)[1]\n        for d in summary["dumps"] if "py-spy rc=0:" in d',
                      'd.split("py-spy rc=", 1)[1]\n        for d in summary["dumps"] if "py-spy rc=" in d'),
    "M10-boot-skips-control": ("    await _async_hb_control(checks)\n", "    pass\n"),
    "X1-no-rest": ("            await asyncio.sleep(rest)\n", "            pass\n"),
    "X2-timeout-25": ("PY_SPY_TIMEOUT_S = 5.0", "PY_SPY_TIMEOUT_S = 25.0"),
    "X3-tries-2": ("HB_CONTROL_TRIES = 3", "HB_CONTROL_TRIES = 2"),
    "X5-default-30": ("spy_timeout=PY_SPY_TIMEOUT_S,", "spy_timeout=30.0,"),
}
HEADER = '''import asyncio, sys, tempfile, threading, inspect as _inspect, time as _time
from pathlib import Path
sys.path[:0] = [{mut!r}, {tests!r}, {stub!r}, {root!r}]
import nightly_ha as _nightly
assert _nightly.__file__.startswith({mut!r}), _nightly.__file__
class _R:
    def check(self, name, ok, detail=""):
        print(("ok   " if ok else "FAIL ") + name, flush=True)
R = _R()
'''


def block() -> str:
    lines = (ROOT / "tests" / "entities.py").read_text().splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines) if ln.startswith("_HB_BOTH = "))
    end = next(i for i, ln in enumerate(lines) if ln.startswith("_hb_cmd = _nightly.docker_command"))
    return "".join(lines[start:end])


def run(mid: str, old: str, new: str, checks: str) -> list[str]:
    source = (ROOT / "tests" / "nightly_ha.py").read_text()
    if old and source.count(old) != 1:
        raise SystemExit(f"{mid}: the mutated site occurs {source.count(old)} times, not once")
    with tempfile.TemporaryDirectory() as mut:
        Path(mut, "nightly_ha.py").write_text(source.replace(old, new) if old else source)
        Path(mut, "block.py").write_text(HEADER.format(
            mut=mut, tests=str(ROOT / "tests"), stub=str(ROOT / "tests" / "hastub"), root=str(ROOT),
        ) + checks)
        out = subprocess.run([sys.executable, "block.py"], cwd=mut, capture_output=True,
                             text=True, timeout=900)
    lines = [ln for ln in out.stdout.splitlines() if ln.startswith(("ok   ", "FAIL "))]
    if out.returncode or not lines:
        return [f"(block did not run: rc={out.returncode} {out.stderr[-200:]!r})"]
    return [ln[5:] for ln in lines if ln.startswith("FAIL ")]


def main() -> int:
    checks, killed, survived, null_ok = block(), 0, 0, False
    for mid, (old, new) in MUTANTS.items():
        failed = run(mid, old, new, checks)
        if mid == "M0-null":
            null_ok = not failed
            print(f"{mid} {'all checks pass' if null_ok else 'FAILS: ' + '; '.join(failed)}")
        elif failed:
            killed += 1
            print(f"{mid} KILLED by: " + " | ".join(failed))
        else:
            survived += 1
            print(f"{mid} SURVIVED")
    print(f"SUMMARY killed={killed} survived={survived} null={'ok' if null_ok else 'FAIL'}")
    return 0 if null_ok and not survived else 1


if __name__ == "__main__":
    raise SystemExit(main())
