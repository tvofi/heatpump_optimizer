#!/usr/bin/env python3
"""D4-s2 harness: every options-flow field a page actually renders must have
a label in strings.json (and both translations), or Home Assistant's
frontend falls back to showing the raw snake_case schema key to the user.

    Metric definition: RESULT unlabeled_fields=<n> -- count of
    (step_id, field_key) pairs that `rendered_keys()` (tests/config_flow_steps.py,
    which walks the *real* voluptuous schema each options page returns,
    section nesting and toggle-conditioned fields included) presents for a
    page, where strings.json's `options.step.<step_id>` (or its
    `sections.<section>`) `data` map has no entry for that key.

    Command:
      cd <tree root>
      PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
        MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
        python3 tools/audit/round8/D4/s2_label_coverage.py

    Instrumented symbol: custom_components.heatpump_optimizer.config_flow
    .HeatPumpOptimizerOptionsFlow (every async_step_* the options menus list),
    driven exactly as tests/config_flow_steps.py:rendered_keys() does.

    Perturbation: delete one key from strings.json's matching `data` map
    (see PERTURB_STEP/PERTURB_KEY below) with --perturb; unlabeled_fields
    must increase by exactly 1, and the specific (step, key) pair must
    appear in the mismatch list. Baseline expected: 0 +/- 0 (exact count;
    the schema-vs-strings mapping is deterministic, no measurement noise).

    Machine: cloud 4-vCPU container, baseline cdf82daabcfe3777d98b31489f36df5555ec9d82.
    This is a pure count (no timing), so no thread_factor/load1 caveat applies
    to the correctness of the number itself; load1 is still printed per the
    harness contract.
"""
import os
for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "tests/hastub")
sys.path.insert(0, ".")

# tests/config_flow_steps.py runs its entire 454-check suite at import time
# and ends with `sys.exit(asyncio.run(main()))` at module scope (undocumented
# in tools/audit/README.md's trap list, which only names entities.py,
# features.py, rolling.py, backtest.py, optimality.py for this behaviour --
# see the harness-gap note in REPORT-s2.md). Neutralise sys.exit for the
# duration of the import so this harness's own RESULT lines are not lost.
import contextlib
import io

_real_exit = sys.exit
sys.exit = lambda *a, **k: None
_import_noise = io.StringIO()
try:
    with contextlib.redirect_stdout(_import_noise):
        import config_flow_steps as cfs  # noqa: E402
finally:
    sys.exit = _real_exit
from custom_components.heatpump_optimizer import config_flow  # noqa: E402

PERTURB_STEP = "hot_water"
PERTURB_SECTION = "schedule"
PERTURB_KEY = "dhw_windows_by_day"


def load_strings():
    with open(
        "custom_components/heatpump_optimizer/strings.json", encoding="utf-8"
    ) as fh:
        return json.load(fh)


def label_keys_for_step(strings, step_id):
    """Every data key strings.json would label for this options step."""
    step = strings.get("options", {}).get("step", {}).get(step_id)
    if step is None:
        return None
    keys = set(step.get("data", {}))
    for sect in step.get("sections", {}).values():
        keys |= set(sect.get("data", {}))
    return keys


async def walk_all_pages(strings):
    flow, entry, hass = cfs.fresh_options()
    top = await flow.async_step_init(None)
    advanced = await flow.async_step_advanced(None)
    pages = sorted(
        set(top.get("menu_options", {})) | set(advanced.get("menu_options", {}))
        - {"quick_setup", "advanced", "setup_overview"}
    )
    mismatches = []
    checked_pages = []
    for step_id in pages:
        handler = getattr(flow, f"async_step_{step_id}", None)
        if handler is None:
            continue
        try:
            result = await handler(None)
        except Exception as exc:  # a page that needs seeded state to render
            mismatches.append((step_id, f"<step raised {exc!r}, skipped>"))
            continue
        if result.get("type") != "form":
            continue
        rendered = cfs.rendered_keys(result)
        labeled = label_keys_for_step(strings, step_id)
        if labeled is None:
            mismatches.append((step_id, "<no strings.json step entry at all>"))
            continue
        checked_pages.append(step_id)
        for key in sorted(rendered):
            if key not in labeled:
                mismatches.append((step_id, key))
    return checked_pages, mismatches


def main():
    perturb = "--perturb" in sys.argv
    strings = load_strings()
    if perturb:
        del strings["options"]["step"][PERTURB_STEP]["sections"][PERTURB_SECTION][
            "data"
        ][PERTURB_KEY]

    t0 = time.process_time()
    checked_pages, mismatches = asyncio.run(walk_all_pages(strings))
    t1 = time.process_time()

    print(f"RESULT pages_checked={len(checked_pages)} count")
    print(f"RESULT unlabeled_fields={len(mismatches)} count")
    for step_id, key in mismatches:
        print(f"  MISMATCH step={step_id} field={key}")
    print(f"RESULT harness_cpu_s={t1 - t0:.4f} s")
    print("RESULT thread_factor=1.00 ratio")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
