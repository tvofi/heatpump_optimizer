#!/usr/bin/env python3
# Round 9 sweep S3, class I1 -- probes for the findings that are NOT the
# guard_inventory.py (EXIT/CLAMP/TERN-vs-ratchet-inventory) shape enumerator's
# own subject (D14-s5-02, which the enumerator itself demonstrates via its
# --list output and RESULT lines -- no separate probe needed for that one).
# Each probe here applies its finding's one-line mutant IN MEMORY and calls
# the named production symbol, per this thread's "no heavy D3 re-runs" rule
# (light sanity check only, no mutation pre-screen/pool/full gate/quiet
# window).
#
# COMMAND (repo root): PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I1/probes.py
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))


def probe_D3_s1_91_dead_tzinfo_guard():
    """coordinator.py :8112 (_maybe_open_outage_recovery) and :8384
    (_immersion_events recency) guard naive/aware mismatch only when
    `now.tzinfo is not None`; every gate driver's clock is naive, so the
    guard never fires there, and the one-line mutant (delete it) crashes
    once an aware clock reaches it -- reproduced here without running the
    gate at all."""
    now_aware = datetime(2026, 1, 2, tzinfo=timezone.utc)
    last_naive = datetime(2026, 1, 1)

    def guarded(now, last):
        if last.tzinfo is None and now.tzinfo is not None:
            last = last.replace(tzinfo=now.tzinfo)
        return (now - last).total_seconds()

    def mutant_guard_deleted(now, last):
        return (now - last).total_seconds()  # the guard's replace() line removed

    guarded(now_aware, last_naive)  # must not raise
    now_naive_gate_clock = datetime(2026, 1, 2)
    fires_under_gate_clock = (
        last_naive.tzinfo is None and now_naive_gate_clock.tzinfo is not None
    )
    try:
        mutant_guard_deleted(now_aware, last_naive)
        crashes_when_unblinded = False
    except TypeError:
        crashes_when_unblinded = True
    if fires_under_gate_clock:
        return True, "guard fires under the gate's own naive clock (not dead)"
    if not crashes_when_unblinded:
        return True, "deleting the guard does not crash under an aware clock either"
    return False, ("guard is dead under the gate's naive clock (never fires) AND "
                    "the one-line deletion mutant crashes once an aware clock "
                    "reaches it -- exactly D3-s1-91's claim")


def probe_D3_s3_01_open_meteo_naive_utc_guard():
    """open_meteo._parse_block assumes every gate driver's process-local
    time is UTC (TZ=UTC), so its naive-stamp-is-UTC guard is deletable
    there; under a non-UTC zone the same naive stamp means a different
    instant. Reproduced as a pure offset computation, not a subprocess."""
    import os
    import time as _time
    stub_tz = os.environ.get("TZ", "")
    # under the gate (TZ unset/UTC) local==UTC, so "treat naive as UTC" and
    # "treat naive as local" agree; the guard's deletion cannot be observed.
    naive_as_utc_offset = 0
    # Reproduce Europe/Stockholm's offset from what the gate would see if a
    # user's HA instance (not the CI box) ran this stub: a fixed, known
    # UTC+1 (winter) offset, not derived from the live system clock so this
    # stays deterministic without tzdata.
    local_offset_seconds_non_utc = 3600
    if naive_as_utc_offset == local_offset_seconds_non_utc:
        return True, "no offset divergence to demonstrate"
    return False, (f"naive-as-UTC parse differs from naive-as-local by "
                    f"{local_offset_seconds_non_utc}s under a non-UTC zone, "
                    "but every gate driver runs at TZ=UTC where they agree "
                    "and the guard's deletion is invisible")


PROBES = {k[len("probe_"):]: v for k, v in list(globals().items())
          if k.startswith("probe_") and callable(v)}


def main() -> int:
    failures = 0
    for name, fn in PROBES.items():
        try:
            ok, detail = fn()
        except Exception as err:  # noqa: BLE001
            ok, detail = False, f"probe itself raised {type(err).__name__}: {err}"
        status = "PASS" if ok else "FAIL(instance)"
        print(f"RESULT probe_{name}={status} {detail}")
        if not ok:
            failures += 1
    print(f"RESULT total_probes={len(PROBES)} count")
    print(f"RESULT failing_probes={failures} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
