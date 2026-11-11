#!/usr/bin/env python3
"""D7-02 harness: retained simulation state on ThermalModel, AST + runtime sentinel.

METRIC (one line): dead_instance_writes = the number of writes to a
ThermalModel INSTANCE attribute observed by a runtime sentinel during one real
HeatPumpOptimizer.optimize() call whose attribute name is read by no expression
anywhere in custom_components/ or tests/ (AST-confirmed, so a dynamic getattr
cannot hide a use, and the sentinel confirms the AST cannot hide a write).

RUN (from the repository root, nothing else):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/model_state_sentinel.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5 / numpy 2.4.6 / scipy 1.17.1). Counts only; contention cannot
move them:
    dead_instance_writes             = 1     exactly
    dead_instance_attrs              = 1     exactly   -- last_dhw_refused
    dead_attr_names                  = last_dhw_refused
    dead_attr_bytes_retained         = 880   +/- 16    bytes (one float64 array)
    dead_attr_present_after          = 1     exactly
    sentinel_total_writes            = 27062 +/- 4000  (solver-path dependent;
                                       any large number is the positive control)
    sentinel_distinct_attrs          = 6     exactly
    guard_subject_present_before     = 0     exactly
    guard_subject_present_after      = 0     exactly
    ast_readers_last_dhw_refused     = 0     exactly
    ast_writers_last_dhw_refused     = 1     exactly
    ast_writers_last_buffer_trajectory = 0   exactly
    ast_readers_last_buffer_trajectory_outside_guard = 0 exactly
    guard_asserts_over_empty_set     = 1     exactly
    prod_unread_instance_writes      = 10939 +/- 2000
    prod_unread_instance_write_fraction = 0.4042 +/- 0.05
    control__step_buffer_refused_writes = 12288 +/- 2000 (positive control)
    control__step_dhw_refused_ast_readers = 5 exactly    (positive control)
    perturb_deadwrite_removed_dead_instance_writes = 0 exactly (must fall from 1)

WHAT IT SHOWS
    tests/rolling.py:577 asserts "the thermal model retains no simulation
    side-channels" with the predicate
        not hasattr(_learner._thermal_model, "last_buffer_trajectory")
    and the detail "buffer trajectories travel in simulate_trajectory's return
    value". That name is written by nothing and read by nothing in the tree, so
    the assertion is over an EMPTY SET: it holds on any tree, including one in
    which the class it guards has grown a new side channel.

    It has. thermal_model.py:2938 ends simulate_trajectory_with_dhw with
        self.last_dhw_refused = dhw_refused
    -- an n_steps float64 array published on the long-lived model instance,
    read by no production code and by no test. The sentinel below counts the
    writes during one real solve and confirms zero reads; the AST pass confirms
    no reader anywhere, including the card and the test suite, so a dynamic
    lookup is not hiding one.

    The guard also runs only under SLOW=1 (tests/run.sh:402-404), so the
    default gate does not execute even the vacuous form.

CONTROLS
    positive control (the sentinel works): sentinel_total_writes is large and
        _step_buffer_refused / _step_dhw_refused show BOTH reads and writes, so
        a zero read count is a measurement and not a broken instrument.
    the guard's own subject: hasattr(model, "last_buffer_trajectory") is
        measured before AND after a full solve. Both are False -- which is what
        makes the committed assertion unfalsifiable rather than satisfied.

PERTURBATION (the judge's): comment out thermal_model.py's
    `self.last_dhw_refused = dhw_refused` (one line, restored immediately).
    DIRECTION: dead_instance_writes and dead_attr_present_after must fall to 0,
    and no gate check changes verdict -- which is the point.
    The harness performs this mutation itself, in a COPY of the tree under a
    private temp directory, and restores nothing in the tree under audit
    because it never edits it. Pass --no-mutate to skip that arm.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer,
    OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from profiles import DT, house, prices, weather  # noqa: E402

START = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
PKG = Path("custom_components/heatpump_optimizer")
TESTS = Path("tests")
#: The name tests/rolling.py:577's guard is written against.
GUARD_SUBJECT = "last_buffer_trajectory"


# ---------------------------------------------------------------- AST pass
def _py_files() -> list[Path]:
    return sorted(list(PKG.rglob("*.py")) + list(TESTS.rglob("*.py")))


def ast_attribute_census():
    """(writes, reads, prod_reads, guard_reads) per attribute name.

    Over every .py in custom_components/ and tests/. A write is
    `<anything>.<name> = ...`; a read is any other Attribute load of `<name>`,
    plus any string literal handed to getattr/hasattr/setattr, so a dynamic
    lookup counts as a read rather than hiding one. ``prod_reads`` counts only
    readers under custom_components/; ``guard_reads`` counts only readers
    inside tests/rolling.py, so a guard cannot be its own subject's reader.
    """
    writes: dict[str, int] = {}
    reads: dict[str, int] = {}
    prod_reads: dict[str, int] = {}
    guard_reads: dict[str, int] = {}
    for path in _py_files():
        in_prod = PKG in path.parents or path.parent == PKG
        is_guard = path.name == "rolling.py"
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        stored: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for t in targets:
                    if isinstance(t, ast.Attribute):
                        writes[t.attr] = writes.get(t.attr, 0) + 1
                        stored.add(id(t))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("getattr", "hasattr", "setattr"):
                    for a in node.args[1:2]:
                        if isinstance(a, ast.Constant) and isinstance(a.value, str):
                            reads[a.value] = reads.get(a.value, 0) + 1
                            if in_prod:
                                prod_reads[a.value] = prod_reads.get(a.value, 0) + 1
                            if is_guard:
                                guard_reads[a.value] = guard_reads.get(a.value, 0) + 1
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and id(node) not in stored:
                reads[node.attr] = reads.get(node.attr, 0) + 1
                if in_prod:
                    prod_reads[node.attr] = prod_reads.get(node.attr, 0) + 1
                if is_guard:
                    guard_reads[node.attr] = guard_reads.get(node.attr, 0) + 1
    return writes, reads, prod_reads, guard_reads


# ------------------------------------------------------------ the sentinel
class SentinelModel(ThermalModel):
    """ThermalModel that records every instance attribute write and read.

    Class-attribute swap on the module, restored in a finally -- the
    ``_fl_orig = _FlOpt`` idiom tests/features.py uses. Nothing in the tree is
    edited.
    """

    def __init__(self, params: ThermalParameters) -> None:
        object.__setattr__(self, "_sent_writes", {})
        object.__setattr__(self, "_sent_reads", {})
        super().__init__(params)

    def __setattr__(self, name, value):
        if not name.startswith("_sent_"):
            w = object.__getattribute__(self, "_sent_writes")
            w[name] = w.get(name, 0) + 1
        object.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if not name.startswith("_sent_") and not name.startswith("__"):
            try:
                r = object.__getattribute__(self, "_sent_reads")
                # Only count names that are (or could become) instance state:
                # bound methods are read on every call and say nothing here.
                if not callable(getattr(type(self), name, None)):
                    r[name] = r.get(name, 0) + 1
            except AttributeError:
                pass
        return object.__getattribute__(self, name)


def build_solve(dhw: bool = True, hours: int = 24):
    cfg = house(two_zone=False, dhw=dhw)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    opt_cfg = OptimizationConfig(
        horizon_hours=hours,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    n = int(hours / DT)

    def fit(arr):
        arr = np.asarray(arr, dtype=float)
        if len(arr) >= n:
            return arr[:n]
        return np.tile(arr, int(np.ceil(n / len(arr))))[:n]

    price_series = fit(prices("winter_typical", START))
    outdoor, wind, rain, solar = (fit(a) for a in weather("winter_cold", START))
    initial = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    return params, opt_cfg, initial, price_series, outdoor, wind, rain, solar


def run_sentinel(dhw: bool = True):
    params, opt_cfg, initial, ps, outdoor, wind, rain, solar = build_solve(dhw)
    model = SentinelModel(params)
    before = hasattr(model, GUARD_SUBJECT)
    opt = HeatPumpOptimizer(model, opt_cfg)
    opt.optimize(initial, ps, outdoor, wind, rain, solar, START, None, None)
    after = hasattr(model, GUARD_SUBJECT)
    writes = dict(object.__getattribute__(model, "_sent_writes"))
    reads = dict(object.__getattribute__(model, "_sent_reads"))
    return model, writes, reads, before, after


def mutated_arm(root: Path) -> int:
    """Copy the tree to a temp dir, delete the dead write, re-run the sentinel.

    Returns the mutated run's dead_instance_writes. The tree under audit is
    never edited.
    """
    with tempfile.TemporaryDirectory(prefix="d7-mutate-") as tmp:
        dst = Path(tmp) / "tree"
        subprocess.run(
            [
                "rsync",
                "-a",
                "--exclude",
                "__pycache__",
                "--exclude",
                ".abacus.donotdelete",
                f"{root}/",
                f"{dst}/",
            ],
            check=True,
        )
        target = dst / "custom_components/heatpump_optimizer/thermal_model.py"
        text = target.read_text(encoding="utf-8")
        needle = "        self.last_dhw_refused = dhw_refused\n"
        if needle not in text:
            return -1
        target.write_text(
            text.replace(
                needle, "        pass  # D7 spot mutation: dead write removed\n"
            ),
            encoding="utf-8",
        )
        here = Path(__file__).resolve()
        rel = here.relative_to(root.resolve())
        env = dict(os.environ, PYTHONPATH="tests/hastub", HPO_PLANDATA=tmp)
        out = subprocess.run(
            [sys.executable, str(rel), "--child"],
            cwd=dst,
            env=env,
            capture_output=True,
            text=True,
        )
        for line in out.stdout.splitlines():
            if line.startswith("RESULT dead_instance_writes="):
                return int(line.split("=")[1].split()[0])
        sys.stderr.write(out.stdout[-2000:] + out.stderr[-2000:])
        return -1


def thread_factor() -> float:
    m = np.random.default_rng(0).standard_normal((300, 300))
    t0, w0 = time.process_time(), time.thread_time()
    for _ in range(6):
        m @ m
    t1, w1 = time.process_time(), time.thread_time()
    dt, dw = t1 - t0, w1 - w0
    return float(dt / dw) if dw > 1e-9 else 1.0


def main() -> int:
    child = "--child" in sys.argv
    orig = tm_mod.ThermalModel
    try:
        model, writes, reads, before, after = run_sentinel(dhw=True)
    finally:
        tm_mod.ThermalModel = orig

    ast_w, ast_r, ast_pr, ast_gr = ast_attribute_census()
    # An attribute is dead when the sentinel saw it written on the instance and
    # nothing anywhere reads it -- neither the run nor any expression in the
    # package or the suite.
    dead = {
        name: n
        for name, n in writes.items()
        if reads.get(name, 0) == 0 and ast_r.get(name, 0) == 0
    }
    dead_writes = sum(dead.values())

    if not child:
        print("\nSENTINEL over one real HeatPumpOptimizer.optimize() (DHW on)")
        print(f"  distinct instance attributes written : {len(writes)}")
        print(f"  total instance writes                : {sum(writes.values())}")
        print(
            "  per attribute  (writes / sentinel reads / AST readers all / "
            "AST readers under custom_components)"
        )
        for name in sorted(writes, key=lambda k: -writes[k]):
            print(
                f"    {name:<28} {writes[name]:>7} / {reads.get(name, 0):>7} / "
                f"{ast_r.get(name, 0):>4} / {ast_pr.get(name, 0):>4}"
            )
        print(f"\n  DEAD (written, read by nobody): {sorted(dead)}")
        print(
            f"\n  guard subject {GUARD_SUBJECT!r}: "
            f"AST writers={ast_w.get(GUARD_SUBJECT, 0)} "
            f"AST readers={ast_r.get(GUARD_SUBJECT, 0)} "
            f"hasattr before={before} after={after}"
        )

    nbytes = 0
    if hasattr(model, "last_dhw_refused"):
        arr = object.__getattribute__(model, "last_dhw_refused")
        nbytes = int(getattr(arr, "nbytes", 0)) + sys.getsizeof(arr) - (
            int(getattr(arr, "nbytes", 0)) and 0
        )
        nbytes = sys.getsizeof(arr)

    print()
    print(f"RESULT dead_instance_writes={dead_writes} count")
    print(f"RESULT dead_instance_attrs={len(dead)} count")
    print(f"RESULT dead_attr_names={'|'.join(sorted(dead)) or 'none'} names")
    print(f"RESULT dead_attr_bytes_retained={nbytes} bytes")
    print(f"RESULT sentinel_total_writes={sum(writes.values())} count")
    print(f"RESULT sentinel_distinct_attrs={len(writes)} count")
    print(f"RESULT guard_subject_present_before={int(before)} count")
    print(f"RESULT guard_subject_present_after={int(after)} count")
    print(
        f"RESULT dead_attr_present_after="
        f"{int(hasattr(model, 'last_dhw_refused'))} count"
    )
    print(f"RESULT ast_readers_last_dhw_refused={ast_r.get('last_dhw_refused', 0)} count")
    print(f"RESULT ast_writers_last_dhw_refused={ast_w.get('last_dhw_refused', 0)} count")
    print(f"RESULT ast_readers_{GUARD_SUBJECT}={ast_r.get(GUARD_SUBJECT, 0)} count")
    print(f"RESULT ast_writers_{GUARD_SUBJECT}={ast_w.get(GUARD_SUBJECT, 0)} count")
    # The guard's own hasattr() string is itself an AST reader, so subtract it:
    # an assertion is over an empty set when nothing but the assertion mentions
    # the name.
    guard_outside = ast_r.get(GUARD_SUBJECT, 0) - ast_gr.get(GUARD_SUBJECT, 0)
    print(f"RESULT ast_readers_{GUARD_SUBJECT}_outside_guard={guard_outside} count")
    print(
        "RESULT guard_asserts_over_empty_set="
        f"{int(ast_w.get(GUARD_SUBJECT, 0) == 0 and guard_outside == 0)} count"
    )
    # A metric tests/structure_budgets.json does not carry: the share of one
    # solve's ThermalModel instance writes whose value NO production code reads.
    prod_unread = {
        n: c for n, c in writes.items() if ast_pr.get(n, 0) == 0
    }
    total_w = sum(writes.values()) or 1
    print(
        f"RESULT prod_unread_instance_writes={sum(prod_unread.values())} count"
    )
    print(
        f"RESULT prod_unread_instance_write_fraction="
        f"{sum(prod_unread.values()) / total_w:.4f} ratio"
    )
    print(
        f"RESULT prod_unread_attr_names={'|'.join(sorted(prod_unread)) or 'none'} names"
    )
    # Positive control: two scratch attributes of the same family that ARE read.
    for name in ("_step_buffer_refused", "_step_dhw_refused"):
        print(
            f"RESULT control_{name}_writes={writes.get(name, 0)} count"
        )
        print(
            f"RESULT control_{name}_ast_readers={ast_r.get(name, 0)} count"
        )

    if not child and "--no-mutate" not in sys.argv:
        mutated = mutated_arm(Path.cwd())
        print(f"RESULT perturb_deadwrite_removed_dead_instance_writes={mutated} count")

    print(f"RESULT thread_factor={thread_factor():.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT threads_alive={threading.active_count()} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
