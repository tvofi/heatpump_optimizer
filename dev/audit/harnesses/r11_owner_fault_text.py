#!/usr/bin/env python3
"""Counts from the pump's fault record in a downloaded diagnostics bundle (R11-OWNER-FAULT-TEXT).

    python3 dev/audit/harnesses/r11_owner_fault_text.py BUNDLE.json

Reads the download's ``coordinator.fault_log`` section (``fault_log.diagnostics_view``)
and prints counts only, never a code or a time, so its output can be quoted from
a private bundle: ``source``, ``episodes`` (closed rows kept), ``dropped``,
``open`` (0 or 1), ``distinct_texts`` (tally keys, ``other`` included) and
``late`` (rows closed at a restart's first read). A bundle from a release
without the record, or an install with no fault source, prints
``fault_log absent`` and exits 1. Exit 0 otherwise.

The bundle is never committed; the owner runs this on one.

Perturbation: delete one entry of the section's ``episodes`` list and the
``episodes`` line prints one fewer.
"""
from __future__ import annotations

import json
import sys
from typing import Any


def section(bundle: Any) -> dict[str, Any] | None:
    """The fault record's section, whether the bundle is wrapped in ``data`` or not."""
    root = bundle.get("data", bundle) if isinstance(bundle, dict) else {}
    view = (root.get("coordinator") or {}).get("fault_log") if isinstance(root, dict) else None
    return view if isinstance(view, dict) else None


def counts(view: dict[str, Any]) -> dict[str, Any]:
    episodes = view.get("episodes") or []
    return {
        "source": view.get("source"),
        "episodes": len(episodes),
        "dropped": int(view.get("dropped") or 0),
        "open": int(view.get("open") is not None),
        "distinct_texts": len(view.get("codes") or {}),
        "late": sum(1 for row in episodes if row.get("late")),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2].strip())
        return 2
    with open(argv[0], encoding="utf-8") as handle:
        view = section(json.load(handle))
    if view is None:
        print("fault_log absent")
        return 1
    for key, value in counts(view).items():
        print(f"{key}\t{value}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
