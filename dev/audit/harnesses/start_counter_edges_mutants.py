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
 ("count-condition", "wear.py", "started, self.running = running and not self.running, running", "started, self.running = running, running"),
 ("none-guard", "wear.py", "        if running is None:\n            return []\n", "        if False:\n            return []\n"),
 ("queue-replay", "wear.py", "        return [at for edge in queued for at in self.fold(*edge)]", "        return []"),
 ("queue-on-unrestored", "wear.py", "        if self.queued is not None:\n            self.queued.append((since, running))\n            return []\n", "        if False:\n            self.queued.append((since, running))\n            return []\n"),
 ("finally-restore", "coordinator.py", "        finally:\n            self._book_starts(self._start_counter.restore(stored.get(\"starts\") if stored else None))\n", "        finally:\n            pass\n        self._book_starts(self._start_counter.restore(stored.get(\"starts\") if stored else None))\n"),
 ("released-guard", "coordinator.py", "        if starts and not self._entry_released:\n", "        if starts:\n"),
 ("stop-edge-save", "coordinator.py", "            self._schedule_ledger_save()\n\n    def _roll_month", "            pass\n\n    def _roll_month"),
 ("element-instant-term", "coordinator.py", "self._immersion_active or immersion_over(kw, self._ctx._thermal_params, self._commanded_power()))))", "self._immersion_active)))"),
 ("element-latch-term", "coordinator.py", "self._immersion_active or immersion_over(kw, self._ctx._thermal_params, self._commanded_power()))))", "immersion_over(kw, self._ctx._thermal_params, self._commanded_power()))))"),
 ("element-both-sources", "running_signal.py", "        if sensor:\n            return resolve_reading", "        if sensor and not element(0.0 if True else 0):\n            return resolve_reading"),
 ("element-reader-guard", "running_signal.py", "        if kw is not None and element(kw):\n", "        if False:\n"),
 ("timer-arm", "running_signal.py", "    sig.timer = (pending, async_call_later(sig.hass, delay, _due))", "    sig.timer = None"),
 ("timer-delay-zero", "running_signal.py", "    delay = max(0.0, wear.EDGE_DEBOUNCE_S - utc_elapsed_seconds(dt_util.now(), pending[1]))", "    delay = 0.0"),
 ("timer-cancel-on-detach", "running_signal.py", "    if timer is not None:\n        timer[1]()\n", "    if False:\n        timer[1]()\n"),
 ("per-refresh-reread", "running_signal.py", "    note(sig, when)\n    read = running_now(sig) is True\n", "    read = running_now(sig) is True\n"),
 ("attach-in-init", "coordinator.py", "        running_signal.attach(running_signal.signal_for(self), *running_signal.source(", "        (lambda *a: None)(running_signal.signal_for(self), *running_signal.source("),
 ("detach-on-release", "coordinator.py", "        running_signal.detach(running_signal.signal_for(self))\n        # #1755 r1", "        # #1755 r1"),
 ("detach-clears-subscribers", "running_signal.py", "    sig.subscribers.clear()\n", ""),
 ("running-now-pending", "running_signal.py", "    return sig.tracker.settled if sig.tracker.pending is None else None", "    return sig.tracker.settled"),
 ("ds-subscribe", "duty_switch.py", "    running_signal.subscribe(rec.signal, rec.feed)", "    pass"),
 ("ds-unsubscribe", "duty_switch.py", "    running_signal.unsubscribe(rec.signal, rec.feed)\n", ""),
 ("ds-pass-confirm", "duty_switch.py", "    running_signal.confirm(rec.signal, when)\n", ""),
 # S7, the refresh-held start (owner ruling D1).
 ("hold-off", "coordinator.py", "StartCounter(hold=None if self._ctx._config.compressor_freq_sensor else RiseHold())", "StartCounter(hold=None)"),
 ("hold-on-frequency", "coordinator.py", "StartCounter(hold=None if self._ctx._config.compressor_freq_sensor else RiseHold())", "StartCounter(hold=RiseHold())"),
 ("hear-bypasses-hold", "coordinator.py", "            self._start_counter.hear(*edge)), lambda read:", "            self._start_counter.fold(*edge)), lambda read:"),
 ("refresh-tick-not-subscribed", "coordinator.py", "            self._start_counter.hear(*edge)), lambda read: self._book_starts(self._start_counter.refresh(read)))", "            self._start_counter.hear(*edge)))"),
 ("refresh-ticks-not-called", "running_signal.py", "    for tick in list(sig.ticks):\n        tick(read)\n", ""),
 ("tick-before-note", "running_signal.py", "    note(sig, when)\n    read = running_now(sig) is True\n", "    read = running_now(sig) is True\n    note(sig, when)\n"),
 ("refresh-reads-unsettled", "running_signal.py", "    read = running_now(sig) is True\n", "    read = True\n"),
 ("refresh-only-note", "coordinator.py", "        running_signal.refresh(running_signal.signal_for(self), dt_util.now())\n", "        running_signal.note(running_signal.signal_for(self), dt_util.now())\n"),
 ("detach-clears-ticks", "running_signal.py", "    sig.ticks.clear()\n", ""),
 ("tick-subscribe-dropped", "running_signal.py", "    if tick is not None and tick not in sig.ticks:\n        sig.ticks.append(tick)\n", ""),
 ("hold-refreshes-one", "wear.py", "HOLD_REFRESHES = 2\n", "HOLD_REFRESHES = 1\n"),
 ("hold-refreshes-three", "wear.py", "HOLD_REFRESHES = 2\n", "HOLD_REFRESHES = 3\n"),
 ("hold-seen-not-counted", "wear.py", "        seen += 1\n        if seen < HOLD_REFRESHES:\n", "        if seen < HOLD_REFRESHES:\n"),
 ("hold-rose-from-any", "wear.py", "            self.held = (since, rose_from is False, 0)\n", "            self.held = (since, True, 0)\n"),
 ("hold-rose-from-none", "wear.py", "            self.held = (since, rose_from is False, 0)\n", "            self.held = (since, False, 0)\n"),
 ("hold-short-run-any-edge", "wear.py", "        if held is not None and held[1] and running is False:  # a short run\n", "        if held is not None and held[1]:  # a short run\n"),
 ("hold-short-run-at-stop", "wear.py", "            return [(held[0], True), (since, running)]\n", "            return [(since, True), (since, running)]\n"),
 ("hold-refresh-unsettled", "wear.py", "        if self.held is None or not running:\n", "        if self.held is None:\n"),
 ("hold-release-at-refresh-time", "wear.py", "        self.held = None\n        return [(since, True)]", "        self.held = None\n        return [(since.replace(second=59), True)]"),
 ("hold-last-not-kept", "wear.py", "        held, rose_from, self.held, self.last = self.held, self.last, None, running\n", "        held, rose_from, self.held = self.held, self.last, None\n"),
 ("counter-refresh-off", "wear.py", "        edges = [] if self.hold is None else self.hold.refresh(running)\n", "        edges = []\n"),
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
