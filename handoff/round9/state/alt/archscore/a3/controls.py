#!/usr/bin/env python3
"""Planted controls for the a3 metrics: for every metric, a scripted edit in
a throwaway detached worktree that ADDS one instance (control: the metric must
rise), one that REMOVES an instance (fix: it must fall), and a
behaviour-neutral rename / reformat (null: it must not move).

    python3 controls.py WORKTREE [--history PRE POST] > controls.out

WORKTREE must be a clean detached checkout of the baseline (7952d8f9); every
state is restored with ``git checkout -- . && git clean -fdq`` before the
next. Each measurement runs ``run_all.py`` in a fresh interpreter (the parse
cache is per process). A ``fix_on`` of "control" means the fix is applied on
top of the control edit (used where the baseline holds no instance to remove).
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = "custom_components/heatpump_optimizer"


# ---------------------------------------------------------------- edit helpers
def _p(wt: Path, rel: str) -> Path:
    return wt / PKG / rel


def sub(wt, rel, old, new):
    p = _p(wt, rel)
    s = p.read_text()
    n = s.count(old)
    assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
    p.write_text(s.replace(old, new))


def func_span(src: str, name: str, cls: str | None = None) -> tuple[int, int]:
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and cls and node.name == cls:
            for f in node.body:
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == name:
                    return f.lineno, f.end_lineno
        if cls is None and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node.lineno, node.end_lineno
    raise AssertionError(f"no function {cls}.{name}")


def rename_in_func(wt, rel, func, old, new, cls=None):
    p = _p(wt, rel)
    s = p.read_text()
    a, b = func_span(s, func, cls)
    lines = s.splitlines(keepends=True)
    body = "".join(lines[a - 1:b])
    body2, n = re.subn(rf"\b{re.escape(old)}\b", new, body)
    assert n > 0, f"{rel}:{func}: {old} not found"
    p.write_text("".join(lines[:a - 1]) + body2 + "".join(lines[b:]))


def rename_in_file(wt, rel, old, new):
    p = _p(wt, rel)
    s, n = re.subn(rf"\b{re.escape(old)}\b", new, p.read_text())
    assert n > 0, f"{rel}: {old} not found"
    p.write_text(s)


def rename_everywhere(wt, old, new):
    n = 0
    for p in sorted((wt / PKG).glob("*.py")):
        s, k = re.subn(rf"\b{re.escape(old)}\b", new, p.read_text())
        if k:
            p.write_text(s)
            n += k
    assert n > 0, f"{old} not found anywhere"


def append(wt, rel, text):
    p = _p(wt, rel)
    p.write_text(p.read_text() + text)


def json_name(wt, old, new, lang="en"):
    p = wt / PKG / "translations" / f"{lang}.json"
    s = p.read_text()
    anchor = f'"name": "{old}"'
    assert s.count(anchor) == 1, f"{lang}.json: {anchor} x{s.count(anchor)}"
    p.write_text(s.replace(anchor, f'"name": "{new}"'))


# ---------------------------------------------------------------- the plan
def plan():
    P = {}

    # 1 hub_solve_writes
    P["hub_solve_writes"] = dict(
        control=("away.lower_floor also writes max_temp through its parameter (m1 could not see away.py)",
                 lambda w: sub(w, "away.py",
                               "    opt_config.min_temp = max(ECONOMY_ABSOLUTE_FLOOR, opt_config.min_temp - by)\n",
                               "    opt_config.min_temp = max(ECONOMY_ABSOLUTE_FLOOR, opt_config.min_temp - by)\n"
                               "    opt_config.max_temp = opt_config.max_temp\n")),
        fix=("the solve stops writing peak_offpeak_factor into the live config",
             lambda w: sub(w, "coordinator.py",
                           "            ctx._opt_config.peak_offpeak_factor = tariff.offpeak_factor\n", "")),
        null=("rename the hub alias `params` -> `hub_params` in _prepare_dhw_inputs, and `ctx` -> `c2` in async_run_optimization",
              lambda w: (rename_in_func(w, "coordinator.py", "_prepare_dhw_inputs", "params", "hub_params",
                                        cls="HeatPumpOptimizerCoordinator"),
                         rename_in_func(w, "coordinator.py", "async_run_optimization", "ctx", "c2",
                                        cls="HeatPumpOptimizerCoordinator"))),
    )

    # 2 shared_inplace_writes
    P["shared_inplace_writes"] = dict(
        control=("re-plant #1752: boost.apply overlays the LIVE _current_action instead of a copy",
                 lambda w: sub(w, "boost.py", "    action = dict(_PLAN_BASES.get(coord) or {})\n",
                               "    action = coord._current_action\n")),
        fix=("the fixed-mode price stamp rebinds instead of mutating the published action",
             lambda w: sub(w, "coordinator.py",
                           '                self._current_action["price"] = self._get_current_price()\n',
                           '                self._current_action = {**self._current_action, "price": self._get_current_price()}\n')),
        null=("spell the price-tile write through a local alias (tiles = self._price_tiles; tiles[name] = ...)",
              lambda w: sub(w, "coordinator.py", "        self._price_tiles[name] = {\n",
                            "        tiles = self._price_tiles\n        tiles[name] = {\n")),
    )

    # 3 private_reach
    P["private_reach"] = dict(
        control=("m3 arm A: six private coordinator reads inside pump_arbiter.state_for",
                 lambda w: sub(w, "pump_arbiter.py", "def state_for(coord: Any) -> ArbiterState:\n",
                               "def state_for(coord: Any) -> ArbiterState:\n    if False:  # probe\n"
                               "        _ = (coord._away_state, coord._mode, coord._thermal_model,"
                               " coord._entity_state, coord._optimization_result, coord._current_action)\n")),
        control_write=("one foreign write: pump_arbiter.state_for sets coord._skip_solve_once",
                       lambda w: sub(w, "pump_arbiter.py", "def state_for(coord: Any) -> ArbiterState:\n",
                                     "def state_for(coord: Any) -> ArbiterState:\n    if False:  # probe\n"
                                     "        coord._skip_solve_once = False\n")),
        fix=("diagnostics reads the public mode, not getattr(coord, '_mode')",
             lambda w: sub(w, "diagnostics.py", '"mode": getattr(coord, "_mode", None),',
                           '"mode": getattr(coord, "mode", None),')),
        null=("rename every `coord` in pump_arbiter.py to `owner` (the roles must come from the call sites)",
              lambda w: rename_in_file(w, "pump_arbiter.py", "coord", "owner")),
    )

    # 4 untyped_payload_keys
    P["untyped_payload_keys"] = dict(
        control=("_build_data_dict publishes one more literal key",
                 lambda w: sub(w, "coordinator.py", '            "plan_stale": self._plan_is_stale(),\n',
                               '            "plan_stale": self._plan_is_stale(),\n            "probe_key": 1,\n')),
        fix=("a TypedDict contract on the producer's dict declares two keys (mode, plan_stale)",
             lambda w: (sub(w, "coordinator.py", "from typing import TYPE_CHECKING, Any, NamedTuple, NoReturn\n",
                            "from typing import TYPE_CHECKING, Any, NamedTuple, NoReturn, TypedDict\n"),
                        sub(w, "coordinator.py", "@dataclass(frozen=True)\nclass CoordinatorContext:\n",
                            "class CoordinatorData(TypedDict, total=False):\n    mode: str\n    plan_stale: bool\n\n\n"
                            "@dataclass(frozen=True)\nclass CoordinatorContext:\n"),
                        sub(w, "coordinator.py", "        data: dict[str, Any] = {\n            \"mode\": self._mode,\n",
                            "        data: CoordinatorData = {\n            \"mode\": self._mode,\n"))),
        null=("rename the producer's local `data` -> `payload` in _build_data_dict",
              lambda w: rename_in_func(w, "coordinator.py", "_build_data_dict", "data", "payload",
                                       cls="HeatPumpOptimizerCoordinator")),
    )

    # 5 xmodule_duplication
    def copy_window_slot(w):
        src = _p(w, "tariff.py").read_text()
        a, b = func_span(src, "_window_slot")
        body = "".join(src.splitlines(keepends=True)[a - 1:b]).replace("def _window_slot(", "def _window_slot_probe_copy(")
        append(w, "sysid.py", "\n\n" + body)

    def dedupe_entity_init(w):
        helper = ("\n\ndef pin_identity(entity: Any, entry: Any, key: str, translation_key: str, platform: str) -> None:\n"
                  "    \"\"\"The identity every platform entity pins at construction.\"\"\"\n"
                  "    entity._entry = entry\n    entity._key = key\n"
                  "    entity._attr_unique_id = f\"{entry.entry_id}_{key}\"\n"
                  "    entity._attr_translation_key = translation_key\n"
                  "    entity.entity_id = f\"{platform}.heat_pump_optimizer_{translation_key}\"\n")
        append(w, "entity.py", helper)
        for rel, plat in (("button.py", "button"), ("binary_sensor.py", "binary_sensor")):
            sub(w, rel,
                "        super().__init__(coordinator)\n        self._entry = entry\n        self._key = key\n"
                "        self._attr_unique_id = f\"{entry.entry_id}_{key}\"\n"
                "        self._attr_translation_key = translation_key\n"
                "        # Pin today's English object id for new installs (the integration\n"
                "        # suggested-object-id mechanism); see the sensor base class.\n"
                f"        self.entity_id = f\"{plat}.heat_pump_optimizer_{{translation_key}}\"\n",
                "        super().__init__(coordinator)\n"
                f"        pin_identity(self, entry, key, translation_key, \"{plat}\")\n")
            sub(w, rel, "from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator\n",
                "from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator\n"
                "from .entity import pin_identity\n")

    P["xmodule_duplication"] = dict(
        control=("m5 arm A: tariff._window_slot (32 lines) copied into sysid.py", copy_window_slot),
        fix=("button/binary_sensor base __init__ pin their identity through one entity.pin_identity helper",
             dedupe_entity_init),
        null=("comments and blank lines inserted inside both duplicated __init__ bodies; a local renamed in tariff._window_slot",
              lambda w: (sub(w, "button.py", "        self._key = key\n        self._attr_unique_id = f\"{entry.entry_id}_{key}\"\n",
                             "        self._key = key\n\n        # null: a comment\n        self._attr_unique_id = f\"{entry.entry_id}_{key}\"\n"),
                         append(w, "tariff.py", "\n# null: trailing comment\n"))),
    )

    # 6 import_cycles
    P["import_cycles"] = dict(
        control=("drift.py imports the coordinator module at module level (coordinator imports drift)",
                 lambda w: sub(w, "drift.py", "\n@dataclass\nclass Cusum:",
                               "\nfrom . import coordinator as _probe_cycle  # noqa: E402,F401\n\n\n@dataclass\nclass Cusum:")),
        fix=("[on top of control] the planted import moves under `if TYPE_CHECKING:`",
             lambda w: sub(w, "drift.py", "\nfrom . import coordinator as _probe_cycle  # noqa: E402,F401\n",
                           "\nfrom typing import TYPE_CHECKING  # noqa: E402\nif TYPE_CHECKING:\n"
                           "    from . import coordinator as _probe_cycle  # noqa: F401\n")),
        fix_on="control",
        null=("swap two intra-package import lines in coordinator.py",
              lambda w: sub(w, "coordinator.py", "from . import mixing_valve\nfrom . import topology\n",
                            "from . import topology\nfrom . import mixing_valve\n")),
    )

    # 7 public_surface
    P["public_surface"] = dict(
        control=("a new public helper in tariff.py nothing imports",
                 lambda w: append(w, "tariff.py", "\n\ndef probe_public_helper(x: float) -> float:\n    return x\n")),
        fix=("boost.overlay, used only inside boost.py, becomes _overlay",
             lambda w: rename_in_file(w, "boost.py", "overlay", "_overlay")),
        null=("boost.held_for renamed held_state_for in every package module (a consistent rename of a cross-module name)",
              lambda w: rename_everywhere(w, "held_for", "held_state_for")),
    )

    # 8 dead_by_reachability
    P["dead_by_reachability"] = dict(
        control=("two new Cusum methods, _probe_a calling _probe_b, nothing calling _probe_a",
                 lambda w: sub(w, "drift.py", "    def reset(self) -> None:\n",
                               "    def _probe_a(self) -> int:\n        return self._probe_b()\n\n"
                               "    def _probe_b(self) -> int:\n        return 1\n\n    def reset(self) -> None:\n")),
        fix=("delete Cusum.reset (reached by no production root)",
             lambda w: sub(w, "drift.py", "    def reset(self) -> None:\n        self.stat = 0.0\n        self.tripped = False\n\n", "")),
        null=("rename boost.held_for -> held_state_for everywhere; blank lines in drift.py",
              lambda w: (rename_everywhere(w, "held_for", "held_state_for"),
                         sub(w, "drift.py", "    def reset(self) -> None:\n", "\n\n    def reset(self) -> None:\n"))),
    )

    # 9 family_splits
    P["family_splits"] = dict(
        control=("en 'Cost Predicted' -> 'Predicted Cost' (splits the cost family in en)",
                 lambda w: json_name(w, "Cost Predicted", "Predicted Cost")),
        fix=("en 'Expected Return' -> 'Away Expected Return' (joins the away run in en)",
             lambda w: json_name(w, "Expected Return", "Away Expected Return")),
        null=("en 'Away Mode' -> 'Away mode' (case only; the sort casefolds)",
              lambda w: json_name(w, "Away Mode", "Away mode")),
    )
    return P


# ---------------------------------------------------------------- runner
def restore(wt: Path) -> None:
    subprocess.run(["git", "-C", str(wt), "checkout", "-q", "--", "."], check=True)
    subprocess.run(["git", "-C", str(wt), "clean", "-fdq"], check=True)


def run_all(wt: Path, details: bool = False) -> dict:
    cmd = [sys.executable, str(HERE / "run_all.py"), str(wt)] + (["--details"] if details else [])
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


def structure_dead(wt: Path) -> str:
    r = subprocess.run([sys.executable, "tests/structure.py"], cwd=wt, capture_output=True, text=True)
    return " ".join(l.split("RESULT ", 1)[1] for l in r.stdout.splitlines() if l.startswith("RESULT dead_"))


def main(argv):
    wt = Path(argv[1]).resolve()
    restore(wt)
    base = run_all(wt)
    results = {"baseline": base, "arms": {}}
    print(f"# baseline {subprocess.run(['git', '-C', str(wt), 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
    print(json.dumps(base))
    for metric, arms in plan().items():
        row = {}
        for arm in ("control", "control_write", "fix", "null"):
            if arm not in arms:
                continue
            desc, fn = arms[arm]
            restore(wt)
            if arm == "fix" and arms.get("fix_on") == "control":
                arms["control"][1](wt)
                ref = run_all(wt)[metric]
            else:
                ref = base[metric]
            fn(wt)
            vals = run_all(wt)
            v = vals[metric]
            others = {k: vals[k] - base[k] for k in vals if k != metric and vals[k] != base[k]}
            extra = ""
            if metric == "dead_by_reachability" and arm in ("control", "fix"):
                extra = f" | structure.py {structure_dead(wt)}"
            row[arm] = dict(desc=desc, ref=ref, value=v, delta=v - ref, other_metrics_moved=others)
            print(f"{metric:24} {arm:13} {ref:>4} -> {v:>4} ({v - ref:+d})  {desc}"
                  + (f"  [also moved: {others}]" if others else "") + extra)
        results["arms"][metric] = row
    restore(wt)
    print("# structure.py dead_* at baseline:", structure_dead(wt))
    if "--history" in argv:
        i = argv.index("--history")
        for tag, path in (("pre #1752/#1753 (47353326)", argv[i + 1]), ("post (ac65f2aa)", argv[i + 2])):
            v = run_all(Path(path))
            results[f"history {tag}"] = v
            print(f"# history {tag}: {json.dumps(v)}")
    (HERE / "controls.json").write_text(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
