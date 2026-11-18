"""Round-11 R11-SEAM-kernel-step: the finder's agreement harness, run at a tree past the fix.

Metric (one line): the `disagreements` m8_agree.py prints per family, with the
three private names this group's fix deleted bound to the owners that replaced
them, so the finder's harness reads the fixed tree unchanged.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_kernel_step_agree.py \
        $EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py --only step_covering_now
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_kernel_step_agree.py --seams

``$EXPORT`` is a ``git archive`` of plan/r11 (819aa2e354b4e5baaf824b8568fd72bea8168a75);
m8_agree.py is the D7-s3 finder's harness (sha1 aaef9a3b34b9c3d8a523eb24410ff97f7ce6b0d1),
which stays out of the tree. The bindings, each the owner the deleted copy became:

    coordinator._covering_index -> plan_step.covering_index
    pump_arbiter._step_index    -> plan_step.plan_step_index
    open_meteo._ensure_utc      -> drift.utc_instant
    drift._as_utc               -> drift.utc_instant  (read by --perturb only)

At the merge base every name exists and the adapter binds none; at the head
each is bound. Nothing else is touched, so every count is the finder's.
Null control: run at the merge base it binds none ("bound: none" prints) and
reads exactly what the harness alone reads.
"""
from __future__ import annotations

import os
import re
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path[:0] = [ROOT]

# The package as m8_agree.py imports it (``custom_components.heatpump_optimizer``),
# so a binding lands on the module object the harness reads.
from custom_components.heatpump_optimizer import (  # noqa: E402
    coordinator,
    drift,
    open_meteo,
    plan_step,
    pump_arbiter,
)

BINDINGS = (
    (coordinator, "_covering_index", lambda: plan_step.covering_index),
    (pump_arbiter, "_step_index", lambda: plan_step.plan_step_index),
    (open_meteo, "_ensure_utc", lambda: drift.utc_instant),
    (drift, "_as_utc", lambda: drift.utc_instant),
)


#: ``--seams``: the D7-s3-04 finder's D002 seam rule (m8_enum.py), every line of
#: the package matching it, each classed by the rule it applies. Only the
#: naive-to-UTC relabel is "the zone of a naive instant"; P2's
#: ``naive_instant_zone`` registry entry holds that class to drift.utc_instant.
D002 = re.compile(r"tzinfo is None|\.replace\(tzinfo=|\.astimezone\(|as_utc\(")
CLASSES = (
    ("text", lambda s: s.startswith(("#", '"')) or "``" in s),
    ("naive-to-UTC relabel: the naive-zone fact",
     lambda s: re.search(r"replace\(tzinfo=(timezone\.utc|UTC)\)", s)),
    ("Home Assistant's dt_util.as_utc", lambda s: "dt_util.as_utc(" in s),
    ("a naive stamp aligned to a reference's zone, for comparison",
     lambda s: re.search(r"replace\(tzinfo=(naive_zone|(\w+\.)?tzinfo|tz)\b", s)),
    ("a zone stripped after conversion, for a naive reference", lambda s: "replace(tzinfo=None)" in s),
    ("an aware conversion", lambda s: ".astimezone(" in s),
    ("a naive test guarding one of the above", lambda s: "tzinfo is None" in s),
)


def seams() -> None:
    """Print every D002 site with its class; a site in no class prints UNCLASSED."""
    pkg = os.path.join(ROOT, "custom_components", "heatpump_optimizer")
    counts: dict[str, int] = {}
    for name in sorted(os.listdir(pkg)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(pkg, name), encoding="utf-8") as fh:
            for no, line in enumerate(fh, 1):
                if not D002.search(line):
                    continue
                text = line.strip()
                cls = next((c for c, test in CLASSES if test(text)), "UNCLASSED")
                counts[cls] = counts.get(cls, 0) + 1
                print(f"SITE {name}:{no} [{cls}] {text[:100]}")
    for cls, n in counts.items():
        print(f"RESULT {cls}={n}")
    print(f"RESULT total={sum(counts.values())}")


def main() -> None:
    if sys.argv[1:2] == ["--seams"]:
        seams()
        return
    if len(sys.argv) < 2:
        raise SystemExit("usage: r11_kernel_step_agree.py <m8_agree.py> [m8_agree args]")
    bound = []
    for module, name, owner in BINDINGS:
        if not hasattr(module, name):
            setattr(module, name, owner())
            bound.append(f"{module.__name__.rsplit('.', 1)[-1]}.{name}")
    print("bound: " + (", ".join(bound) if bound else "none"))
    harness = sys.argv[1]
    sys.argv = [harness, *sys.argv[2:]]
    runpy.run_path(harness, run_name="__main__")


if __name__ == "__main__":
    main()
