#!/usr/bin/env python3
"""D14 round-9 class sweep, class P11 (round9/sweep/S4):
"The only oracle for an external counterpart (HA core, its state machine, its
recorder REST API, a device behind an integration) is a test double the
implementer wrote from what the code needed, so the tests agree with a wrong
implementation."

Each of P11's six round-9 findings already names a whole-package enumerator
(its own seam_rule); this driver re-runs each verbatim and prints its result
lines, then disposition each finding's own seam as instance/guarded/n.a. --
see SWEEP.md for the widening argument (why each is a single seam, not a
family) and the two custom probes (currency fallback, Tibber reauth) that
have no existing harness of their own.

COMMAND: PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P11/enumerate.py
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
"""
import os
import subprocess
import sys

ROOT = os.getcwd()
FINDINGS = [
    ("D1-s1-51", ["python3", "tools/audit/round9/D1/leads/stub_store_codec.py"],
     "hastub Store decodes with stdlib json, not orjson: 6 of 6 hostile number tokens load where HA drops the file"),
    ("D1-s1-52", ["python3", "tools/audit/round9/D1/leads/stub_naive_clock.py"],
     "hastub dt_util.now() is naive by default: 6 of 6 aware/naive cells invert their verdict"),
    ("D1-s2-71", ["python3", "tools/audit/round9/D1/leads/l3_update_interval.py"],
     "hastub DataUpdateCoordinator drops update_interval: 4 of 4 cells unreadable"),
]


def run(cmd, timeout=90):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return out.stdout + out.stderr
    except subprocess.TimeoutExpired as exc:
        return f"TIMEOUT: {exc}"


def currency_probe():
    """D6-s1-81: README's SEK fallback is unreachable under real HA core."""
    sys.path.insert(0, ".")
    sys.path.insert(0, "tests/hastub")
    from custom_components.heatpump_optimizer.currency import resolve_currency

    class FakeConfig:
        currency = "EUR"  # HA core's own Config.currency default

    class FakeHass:
        config = FakeConfig()

    real_ha_result = resolve_currency(FakeHass())

    class FakeConfigNone:
        currency = None  # what the hastub double actually gives (unconfigured)

    class FakeHassNone:
        config = FakeConfigNone()

    hastub_result = resolve_currency(FakeHassNone())
    return {
        "under_real_ha_default_config_currency": real_ha_result,
        "under_hastub_double_currency_none": hastub_result,
        "readme_claims": "SEK when the instance has none configured",
        "instance": real_ha_result != "SEK",
    }


def tibber_reauth_probe():
    """D10-s1-03: verdict=='reauth' starts the Repairs flow but still raises
    UpdateFailed (never ConfigEntryAuthFailed), confirmed by reading the
    exact call sequence in coordinator.py:_fetch_tibber_prices (no live
    hass/coordinator instantiation needed -- the branch is unconditional)."""
    import re
    src = open("custom_components/heatpump_optimizer/coordinator.py", encoding="utf-8").read()
    m = re.search(
        r"if verdict == \"reauth\":\n\s+self\._tibber_start_reauth\(\)\n\s+if verdict != \"ok\":\n\s+self\._tibber_fetch_failed",
        src,
    )
    raises_auth_failed = "ConfigEntryAuthFailed" in src
    return {
        "reauth_falls_through_to_fetch_failed": bool(m),
        "ConfigEntryAuthFailed_referenced_anywhere": raises_auth_failed,
        "instance": bool(m) and not raises_auth_failed,
    }


def replay_clock_seams():
    """D14-s4-02: every dt_util.freeze( call site under tests/, dispositioned.
    tests/replay.py is the one nightly-replay loop; the rest are single-instant
    unit-test fixtures (dst_checks.py already exercises DST transitions with
    explicit fold/gap instants of its own, not a fixed-offset simulation
    clock) -- see SWEEP.md for the full per-file count."""
    import subprocess as sp
    out = sp.run(["grep", "-rn", "dt_util.freeze(", "tests/"], capture_output=True, text=True).stdout
    by_file = {}
    for line in out.splitlines():
        f = line.split(":", 1)[0]
        by_file[f] = by_file.get(f, 0) + 1
    return by_file


def main():
    for fid, cmd, claim in FINDINGS:
        print(f"== {fid}: {claim} ==")
        print(run(cmd)[-400:])

    print("== D6-s1-81 (currency fallback) ==")
    print(currency_probe())

    print("== D10-s1-03 (Tibber reauth) ==")
    print(tibber_reauth_probe())

    print("== D14-s4-02 (replay clock) call sites ==")
    for f, n in replay_clock_seams().items():
        print(f"{f}: {n} freeze() call(s)")


if __name__ == "__main__":
    main()
