#!/usr/bin/env python3
"""D14 round-9 class sweep, class P6 (round9/sweep/S4):
"A consumer reads a key or field no producer writes, with a silent fallback."

Each of P6's five round-9 findings already names a whole-package (or
whole-entity, or whole-cell-grid) enumerator as its seam_rule. This driver
re-runs each verbatim; SWEEP.md carries the disposition of every seam it
prints.

COMMAND: PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P6/enumerate.py
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
"""
import subprocess

FINDINGS = [
    ("D2-s1-51", ["python3", "tools/audit/round9/D2/leads/dhw_sweep_outdoor.py"],
     "DHW advisor prices candidates at the 5.0 degC ThermalState default when no outdoor thermometer is mapped"),
    ("D4-s2-01", ["python3", "tools/audit/round9/D4/s2/prefill_config_strings.py"],
     "Setup wizard device pre-fill page: unlabelled fields, untranslated errors"),
    ("D4-s2-01b", ["python3", "tools/audit/round9/D4/s2/prefill_after_save.py"],
     "after_save destination fan-out (companion probe for the same finding)"),
    ("D10-s2-01", ["python3", "tools/audit/round9/D10/s2/climate_presets.py"],
     "Climate presets auto/economy have no translation or icon in any language"),
    ("D12-s1-01", ["python3", "tools/audit/round9/D12/s1/state_seed.py"],
     "Hot water without a tank probe: every solve starts from the 55C ThermalState default"),
    ("D14-s1-02", ["python3", "tools/audit/round9/D14/s1/p6_keys.py"],
     "horizon_hours read from coordinator.data but never written; boost probes a test-double-only field"),
]


def run(cmd, timeout=120):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return out.stdout + out.stderr
    except subprocess.TimeoutExpired as exc:
        return f"TIMEOUT: {exc}"


def main():
    for fid, cmd, claim in FINDINGS:
        print(f"== {fid}: {claim} ==")
        print(run(cmd)[-1200:])


if __name__ == "__main__":
    main()
