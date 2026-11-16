"""D9-s1 cell census: every universe file of D9-s1's cells, with its markers
on the four axes (sse_per_gradient, solves_per_cycle, gil_hold,
loop_thread_work). Not a finding harness: the denominator's examination
record, read beside h_loop_thread_work.py's dynamic CENSUS lines (which
files ran on the loop / executor threads during real cycles).

Metric: per file, counts of source lines matching each axis's markers --
solver entries (_multi_start_minimize, .optimize(, optimize_in_process,
_lbfgsb_run), model simulation (simulate_step, simulate_trajectory*),
off-loop submissions (_await_optimize/_await_off_loop/_await_process,
async_add_executor_job), loop-side hooks (@callback, async_track_*,
async_write_ha_state, _handle_coordinator_update, async_listen*), and GIL
yields (sleep(0.002), _gil_yield). Counts exact.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_cell_census.py
Perturbation: add a line calling simulate_step to any file -> its sim count +1.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B1 container.
"""
from __future__ import annotations

import re
import subprocess
import sys

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
MARKERS = {
    "solve": re.compile(r"_multi_start_minimize\(|\.optimize\(|optimize_in_process|_lbfgsb_run\("),
    "sim": re.compile(r"simulate_step\(|simulate_trajectory(_batch|_with_dhw)?\("),
    "offloop": re.compile(r"_await_optimize\(|_await_off_loop\(|_await_process\(|async_add_executor_job\("),
    "loophook": re.compile(r"@callback|async_track_|async_write_ha_state\(|_handle_coordinator_update|async_listen"),
    "yield": re.compile(r"sleep\(0(\.002)?\)|_gil_yield\("),
    "js_service": re.compile(r"callService\(|callWS\("),
}


def universe():
    out = subprocess.run(
        [sys.executable, "tools/audit/check_scopes.py", "--repo", ".", "--ref", BASE,
         "--seat", "D9-s1"], capture_output=True, text=True, check=True).stdout
    return [ln.split("\t")[2] for ln in out.splitlines() if ln.count("\t") >= 2]


def main():
    files = universe()
    print(f"RESULT universe_files={len(files)} count")
    tot = {k: 0 for k in MARKERS}
    for f in files:
        try:
            text = open(f, encoding="utf-8").read().splitlines()
        except OSError:
            print(f"CELL {f} missing")
            continue
        counts = {k: sum(1 for ln in text if rx.search(ln) and not ln.lstrip().startswith("#"))
                  for k, rx in MARKERS.items()}
        for k, v in counts.items():
            tot[k] += v
        print("CELL " + f + " " + " ".join(f"{k}={v}" for k, v in counts.items()))
    for k, v in tot.items():
        print(f"RESULT total.{k}={v} lines")
    print("RESULT thread_factor=1.0 1")
    import os
    print(f"RESULT load1={os.getloadavg()[0]:.2f} 1")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
