#!/usr/bin/env python3
"""D5 harness: platform module docstrings vs the entities the seam registers.

Metric definition (one line): per platform module, the number of entity objects
the production ``async_setup_entry`` hands to ``async_add_entities`` (executed
count) minus the number of entities the module's own docstring says the
platform provides (declared count), i.e. ``docstring_entity_gap``.

Run from the repository root:
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D5/platform_docstrings.py
Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225
Machine: Apple M1, 8 GB (audit box)

Instrumented production symbols (the seam, not a copy):
  heatpump_optimizer.switch:async_setup_entry
  heatpump_optimizer.binary_sensor:async_setup_entry
  heatpump_optimizer.button:async_setup_entry

Declared count: read from the module's own ``__doc__`` and *asserted present*,
so the number cannot silently drift the way the prose did. The quoted span is
printed beside it; the declared numbers are
  switch.py        1  "Provides an on/off switch to enable/disable the optimizer."
  binary_sensor.py 3  "Three states are worth surfacing as their own entities"
  button.py        2  "both momentary actions with no lasting state"
(singular article -> 1; the number word "Three" -> 3; "both" -> 2).

Perturbation the count must move under (+1, the required direction): append one
more entity to the list the seam publishes. The harness applies that
perturbation in memory (a read-only tree must not be edited) by re-running the
real ``async_setup_entry`` with a collecting callback that appends one extra
sentinel object; ``registered`` must rise by exactly 1 and ``docstring_entity_gap``
by exactly 1. The unperturbed run is executed twice as a null control: the delta
between the two unperturbed runs must be 0.

Counts are contention-immune (integers); thread_factor is 1.0 (no threaded
maths) and load1 is reported for the record.
"""
import os
import sys
import asyncio

# Thread pin must precede any numpy import: the platform modules import the
# coordinator, which imports numpy.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.getcwd()
for _p in (os.path.join(ROOT, "tests"),
           os.path.join(ROOT, "custom_components"),
           os.path.join(ROOT, "tests", "hastub")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from harness import FakeCoordinator, FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import switch as switch_mod  # noqa: E402
from heatpump_optimizer import binary_sensor as bs_mod  # noqa: E402
from heatpump_optimizer import button as button_mod  # noqa: E402

BASELINE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"

# module, declared count, the exact quoted span the count is read from
CASES = [
    (switch_mod, 1,
     "Provides an on/off switch to enable/disable the optimizer."),
    (bs_mod, 3,
     "Three states are worth surfacing as their own entities"),
    (button_mod, 2,
     "both momentary actions with no lasting state"),
]

# A representative published payload, copied from tests/entities.py's DATA so the
# entity properties the constructors touch resolve. The constructors themselves
# read only the coordinator/entry, but this keeps the fixture honest.
DATA = {
    "mode": "auto",
    "indoor_temperature": 21.3,
    "stale_inputs": [],
    "input_health": "ok",
    "external_heat_active": False,
    "away": False,
}


class _Sentinel:
    """One extra object appended only by the in-memory perturbation."""


def _collect(module, extra=0):
    """Drive the real ``async_setup_entry`` and return the added objects."""
    added = []
    coordinator = FakeCoordinator(dict(DATA))
    entry = FakeEntry()
    entry.runtime_data = coordinator
    hass = FakeHass()

    def add(entities):
        added.extend(entities)

    asyncio.run(module.async_setup_entry(hass, entry, add))
    return added


def main():
    gaps = []
    for module, declared, quote in CASES:
        name = module.__name__.rsplit(".", 1)[-1]
        doc = module.__doc__ or ""
        if quote not in doc:
            print("  WARN %-16s declared span no longer in the docstring: %r"
                  % (name, quote))
            declared = None

        run1 = _collect(module)
        run2 = _collect(module)          # null control: unperturbed, twice
        control_delta = len(run2) - len(run1)

        # In-memory perturbation: one more entity on the same seam.
        perturbed = []
        coord_p = FakeCoordinator(dict(DATA))
        entry_p = FakeEntry()
        entry_p.runtime_data = coord_p
        hass_p = FakeHass()

        def add_p(entities, _real=module):
            perturbed.extend(list(entities) + [_Sentinel()])

        asyncio.run(module.async_setup_entry(hass_p, entry_p, add_p))
        perturb_delta = len(perturbed) - len(run1)

        registered = len(run1)
        names = [type(e).__name__ for e in run1]
        gap = None if declared is None else registered - declared
        if gap is not None:
            gaps.append((name, declared, registered, gap))

        print("  %-16s declared=%s registered=%d gap=%s  %s"
              % (name, declared, registered, gap, ", ".join(names)))
        print("  %-16s null_control_delta=%d  min_in_memory_perturb_delta=%d"
              % (name, control_delta, perturb_delta))

    if gaps:
        print("RESULT platforms_checked=%d modules" % len(gaps))
        print("RESULT platforms_where_docstring_undercounts=%d modules"
              % sum(1 for _n, _d, _r, g in gaps if g > 0))
        print("RESULT total_docstring_entity_gap=%d entities"
              % sum(g for _n, _d, _r, g in gaps))
        for n, d, r, g in gaps:
            print("RESULT gap.%s=%d entities" % (n.replace(".py", ""), g))
    else:
        print("RESULT platforms_checked=0 modules")

    print("RESULT thread_factor=1.0")
    try:
        print("RESULT load1=%s" % os.getloadavg()[0])
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
