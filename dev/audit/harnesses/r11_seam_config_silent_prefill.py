"""R11-SEAM-config companion to round 11's D17/s2/silent_prefill.py (D17-s2-04).

The finder's harness reads a created entry's ``data`` alone and posts a
schedule the setup page never showed; once settings are stored in options and
a kept schedule at fraction 1.0 is refused, its walk ends on the refusal and
its cap arms read flat. This applies the pre-fill pages' own rule to the same
inputs, at either end of the fix:

- ``fraction_shown_beside_windows``: a page showing the schedule field shows
  the power fraction beside it (1 fixed, 0 at the defect);
- ``uncapped_schedule_accepted``: a kept schedule whose fraction in force is
  the 1.0 default -- it caps nothing -- passes the page's refusals (0 fixed,
  1 at the defect);
- null controls, equal at both ends: ``capped_schedule_refused`` (schedule kept
  with fraction 0.6) and ``no_schedule_refused`` (fraction 1.0, no schedule).

Run from the tree root: ``PYTHONPATH=tests/hastub python3
dev/audit/harnesses/r11_seam_config_silent_prefill.py``.
"""
import sys

sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests")

from heatpump_optimizer import config_flow  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    CONF_SILENT_MODE_FRACTION,
    CONF_SILENT_MODE_WINDOWS,
)

SCHEDULE = {CONF_SILENT_MODE_WINDOWS: "06:00-10:00"}


def shown(keys, values):
    """The field names a pre-fill page renders for ``keys``."""
    if hasattr(config_flow, "_prefill_fields"):
        fields = config_flow._prefill_fields(keys, values, {})
    else:  # the defect's tree: the page builder took no in-force mapping
        fields = config_flow._prefill_schema(keys, values).schema
    return {str(getattr(marker, "schema", marker)) for marker in fields}


def refused(saved):
    return bool(config_flow._prefill_errors(dict(saved), {}))


def main():
    page = shown((CONF_SILENT_MODE_WINDOWS,), SCHEDULE)
    print(f"page fields for a suggested schedule: {sorted(page)}")
    print(f"RESULT fraction_shown_beside_windows={int(CONF_SILENT_MODE_FRACTION in page)} count")
    print(f"RESULT uncapped_schedule_accepted={int(not refused(SCHEDULE))} count")
    print(f"RESULT capped_schedule_refused="
          f"{int(refused({**SCHEDULE, CONF_SILENT_MODE_FRACTION: 0.6}))} count")
    print(f"RESULT no_schedule_refused={int(refused({CONF_SILENT_MODE_FRACTION: 1.0}))} count")


if __name__ == "__main__":
    main()
