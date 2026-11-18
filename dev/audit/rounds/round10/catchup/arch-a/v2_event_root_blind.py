#!/usr/bin/env python3
"""arch-a V2 (round 10 catch-up verify, ARCH2-s2 P4): the score's hub census does not root at the
coordinator's event callbacks, so an in-place hub write placed there is invisible to delta_S.

Metric: for a plant of one extra in-place write ``ctx._current_state.<field> = ...`` placed (a) in the
        scheduled cycle's _update_current_state (control) and (b) in two event callbacks
        (_on_defrost_event, _async_handle_ecl110_state_message), the change in
        hub_solve_writes (the score metric) and in shared_inplace_writes.
Count key: the metrics' own site keys.
Instrumented symbols: tools/audit/archscore/metrics/hub_solve_writes.py:measure,
        shared_inplace_writes.py:measure.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-a/v2_event_root_blind.py
          from the root of the tree under test (package copied to temp dirs per plant).
Null control: the cycle plant must move hub_solve_writes by +1.
Expected (d749c986d): cycle +1; both event plants +0 on both metrics (the blind spot P4's harness
        event_hub_writes.py exists for).
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tools" / "audit"))
from archscore.metrics import common as C  # noqa: E402
from archscore.metrics import hub_solve_writes as H  # noqa: E402
from archscore.metrics import shared_inplace_writes as S  # noqa: E402

PKG = Path("custom_components") / "heatpump_optimizer"
PLANTS = {
    "cycle_update_current_state": r"(    async def _update_current_state\(self[^\n]*\n(?:[^\n]*\n)*?        \"\"\"(?:.|\n)*?\"\"\"\n)",
    "event_on_defrost_event": r"(    def _on_defrost_event\(self[^\n]*\n(?:[^\n]*\n)*?        \"\"\"(?:.|\n)*?\"\"\"\n)",
    "event_ecl110_state": r"(    def _async_handle_ecl110_state_message\(self[^\n]*\n        \"\"\"[^\n]*\"\"\"\n)",
}
LINE = '        getattr(self, "_ctx", self)._current_state.ecl110_effective_displace = 0.0\n'


def measure(root: Path) -> tuple[int, int]:
    C.reset_caches()
    h = H.measure(root)["value"]
    C.reset_caches()
    return h, S.measure(root)["value"]


def main() -> int:
    t_cpu, th = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="archa-ev-") as tmp:
        base = Path(tmp) / "base"
        shutil.copytree(ROOT / PKG, base / PKG)
        bh, bs = measure(base)
        print(f"RESULT base hub_solve_writes={bh} shared_inplace_writes={bs} count")
        for name, pat in PLANTS.items():
            d = Path(tmp) / name
            shutil.copytree(ROOT / PKG, d / PKG)
            f = d / PKG / "coordinator.py"
            src = f.read_text()
            m = re.search(pat, src)
            if not m:
                print(f"RESULT {name} anchor=missing")
                continue
            f.write_text(src[: m.end()] + LINE + src[m.end():])
            h, s = measure(d)
            print(f"RESULT {name} hub_delta={h - bh:+d} shared_delta={s - bs:+d} count")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
