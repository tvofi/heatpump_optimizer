"""R10-START-COUNTER-EDGES mutation proof: each production line the build adds or
moves, broken one at a time, against the two features.py blocks that pin it.

The blocks are the build's own ("R10-START-COUNTER-EDGES: the start counter
fed from running-signal edges") and part A's ("duty-switch restart learning,
part A"), each run alone by tools/audit/seat/features_block.py with the
prelude its --emit-prelude derives from the tree. A mutant is KILLED when a
check in either block fails or the block raises; the unmutated tree is run
first and must pass both blocks (the null control). Each file is restored in a
finally, so run it on a clean checkout and read git status after.

  PYTHONPATH=tests/hastub python3 dev/audit/harnesses/start_counter_edges_mutants.py

Prints one KILLED or SURVIVED line per mutant and RESULT survived=<n>.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile

P = "custom_components/heatpump_optimizer/"
SCE = "# --- R10-START-COUNTER-EDGES: the start counter fed from running-signal edges"
DS = "from heatpump_optimizer import duty_switch as _ds_mod"
DS_END = "# --- R10-CEILING-PROBE (#2498, #2808)"
M = [
 ("price-gate-ge", "coordinator.py", "            for at in starts if wear > 0 else ():", "            for at in starts if wear >= 0 else ():"),
 ("price-gate-true", "coordinator.py", "            for at in starts if wear > 0 else ():", "            for at in starts:"),
 ("zero-kwh", "coordinator.py", "                self._ledger.add(at, \"wear\", kwh=0.0, sek=wear)", "                self._ledger.add(at, \"wear\", kwh=1.0, sek=wear)"),
 ("wear-line-deleted", "coordinator.py", "                self._ledger.add(at, \"wear\", kwh=0.0, sek=wear)", "                pass"),
 ("wear-line-at-now", "coordinator.py", "                self._ledger.add(at, \"wear\", kwh=0.0, sek=wear)", "                self._ledger.add(dt_util.now(), \"wear\", kwh=0.0, sek=wear)"),
 ("restore-ignores-stored-running", "wear.py", "        self.running, self.lifetime, self.months = stored.running, stored.lifetime, stored.months", "        self.lifetime, self.months = stored.lifetime, stored.months"),
 ("none-overwrites-running", "wear.py", "        if running is None:\n            return []\n", "        if running is None:\n            self.running = False\n            return []\n"),
 ("month-key-now", "wear.py", "        key = since.strftime(\"%Y-%m\")", "        key = datetime.now().strftime(\"%Y-%m\")"),
 ("restore-order-before-ledger", "coordinator.py", "        stored = await load_mapping(self._ledger_store, \"ledger\")  # a failed read is None\n        try:", "        stored = await load_mapping(self._ledger_store, \"ledger\")  # a failed read is None\n        self._book_starts(self._start_counter.restore(stored.get(\"starts\") if stored else None))\n        try:"),
 ("attach-idempotence-off", "running_signal.py", "    if sig.unsub is not None or not entity:", "    if not entity:"),
 ("timer-delay-zero", "running_signal.py", "    delay = max(0.0, wear.EDGE_DEBOUNCE_S - utc_elapsed_seconds(dt_util.now(), pending[1]))", "    delay = 0.0"),
 ("immersion-commanded-term", "thermal_model.py", "        and commanded_kw > 0.1\n    )", "    )"),
 ("reader-freq-reads-meter", "running_signal.py", "    return sensor or meter, reader", "    return meter or sensor, reader"),
]


BLOCK = "tools/audit/seat/features_block.py"
ENV = {**os.environ, "PYTHONPATH": "tests/hastub"}


def prelude(tmp: str, marker: str, end: str | None) -> str:
    out = os.path.join(tmp, f"prelude{abs(hash(marker))}.py")
    subprocess.run([sys.executable, BLOCK, "--emit-prelude", out, marker] + ([end] if end else []),
                   env=ENV, check=True, capture_output=True)
    return out


def run(pre: str, marker: str, end: str | None = None) -> tuple[list[str], bool]:
    r = subprocess.run([sys.executable, BLOCK, "--prelude", f"exec(open({pre!r}).read())", marker]
                       + ([end] if end else []), capture_output=True, text=True, env=ENV, timeout=1800)
    fails = [ln.strip()[:110] for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
    return fails, ("Traceback" in r.stdout + r.stderr and not fails)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        blocks = [(prelude(tmp, SCE, None), SCE, None), (prelude(tmp, DS, DS_END), DS, DS_END)]
        base = [run(*b) for b in blocks]
        print("BASELINE", [(len(f), crash) for f, crash in base], flush=True)
        if any(f or crash for f, crash in base):
            print("RESULT survived=unmeasured (the unmutated tree fails a block)")
            return 1
        survived = 0
        for name, f, old, new in M:
            path = pathlib.Path(P + f)
            src = path.read_text()
            if src.count(old) != 1:
                print(f"STALE    {name}: its line is not in {f} exactly once")
                survived += 1
                continue
            path.write_text(src.replace(old, new))
            try:
                out = [run(*b) for b in blocks]
            finally:
                path.write_text(src)
            killed = any(fl or crash for fl, crash in out)
            survived += not killed
            print(f"{'KILLED  ' if killed else 'SURVIVED'} {name}: "
                  + ", ".join(f"{len(fl)} fail{' +raise' if crash else ''}" for fl, crash in out), flush=True)
            for ln in (out[0][0] + out[1][0])[:2]:
                print("        ", ln, flush=True)
        print(f"RESULT survived={survived}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
