"""Is a stored defrost ``factors`` grid that is present but UNREADABLE as a
whole treated exactly like an absent grid?

Measures ``DefrostDerate.from_dict`` on a v2 document (STORE_VERSION 2; the
``factors``/``counts`` grids are read for both v1 and v2, so v2 is used)
built from a default instance with one cell set (factor 0.8, count 5) and
serialised with ``as_dict()``. Arms: ``valid`` (round trip), ``absent``
(``factors`` key removed) and unreadable ``factors``: wrong row count, wrong
row width, string, dict, scalar. Per arm: whether the loaded factors equal
the defaults, the WARNING+ records from heatpump_optimizer loggers, and any
loss record (``migrated``; DefrostDerate has no ``reset`` attribute, so a
loss is any instance state differing from a default instance's other than
factors/counts).

Run (repo root): PYTHONPATH=tests/hastub python3 \
    dev/audit/rounds/round11/D14/N-silent-zero/defrost_unreadable_grid.py [--perturb]

Expected baseline: valid_kept=1; every unreadable arm factors_equal_default=1,
warnings=0, no loss recorded, so unreadable_read_as_absent=5.
Perturbation (--perturb): wrap from_dict so a ``factors`` key that _grid_of
would reject as a whole (not an n_t x n_h list of lists) logs a WARNING on
the module _LOGGER first; expected unreadable_read_as_absent=0.
"""
from __future__ import annotations

import copy
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
for p in (ROOT / "tests", ROOT / "tests" / "hastub", ROOT / "custom_components"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import heatpump_optimizer.defrost as dm  # noqa: E402
from heatpump_optimizer.defrost import (  # noqa: E402
    HUMIDITY_EDGES,
    TEMP_EDGES,
    DefrostDerate,
)

PERTURB = "--perturb" in sys.argv
N_T, N_H = len(TEMP_EDGES) - 1, len(HUMIDITY_EDGES) - 1

if PERTURB:
    _orig = DefrostDerate.from_dict.__func__

    def _wrapped(cls, data):
        raw = data.get("factors") if isinstance(data, dict) else None
        if isinstance(data, dict) and "factors" in data and not (
            isinstance(raw, list)
            and len(raw) == N_T
            and all(isinstance(r, list) and len(r) == N_H for r in raw)
        ):
            dm._LOGGER.warning("Defrost derate: stored factors grid unreadable")
        return _orig(cls, data)

    DefrostDerate.from_dict = classmethod(_wrapped)


class Capture(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


cap = Capture()
logging.getLogger("heatpump_optimizer").addHandler(cap)
logging.getLogger("heatpump_optimizer").setLevel(logging.DEBUG)

DEFAULT = DefrostDerate()
base = DefrostDerate()
base.factors[1][1] = 0.8
base.counts[1][1] = 5
valid_doc = copy.deepcopy(base.as_dict())


def other_state(inst):
    return {k: v for k, v in vars(inst).items() if k not in ("factors", "counts")}


arms: dict[str, dict] = {"valid": valid_doc}
absent = copy.deepcopy(valid_doc)
del absent["factors"]
arms["absent"] = absent
unreadable = {
    "wrong_rows": valid_doc["factors"][:-1],
    "wrong_width": [r[:-1] for r in valid_doc["factors"]],
    "string": "nonsense",
    "dict": {"0": [1.0]},
    "scalar": 0.8,
}
for name, bad in unreadable.items():
    d = copy.deepcopy(valid_doc)
    d["factors"] = bad
    arms[name] = d

hits = 0
valid_kept = 0
for name, doc in arms.items():
    cap.n = 0
    inst = DefrostDerate.from_dict(doc)
    eq = int(inst.factors == DEFAULT.factors)
    warns = cap.n
    loss = other_state(inst) != other_state(DEFAULT)
    migrated = getattr(inst, "migrated", "n/a")
    print(
        f"ARM {name} factors_equal_default={eq} warnings={warns} "
        f"reset={migrated} loss_recorded={int(loss)}"
    )
    if name == "valid":
        valid_kept = int(inst.factors[1][1] == 0.8 and inst.counts[1][1] == 5)
    elif name in unreadable and eq and warns == 0 and not loss:
        hits += 1

print(f"RESULT unreadable_read_as_absent={hits} count")
print(f"RESULT valid_kept={valid_kept} count")
