#!/usr/bin/env python3
"""The tests/features.py freeze (R11-OWNER-FEATURES-SPLIT, design revision 5).

tests/features.py stays where it is, with every span and every mutation row
keyed to it; it may not grow. New tests go to a seam script,
`tests/features_<seam>.py`, whose seam this file's module table decides.
tests/entities.py runs `refusals` over the tree, so the freeze is a check
rather than a convention:

1. a span id in tests/features.py that the manifest does not list is refused
   (a section appended or inserted; a repeated title reads `#2`, `#3`, so a
   copy of an existing title is new too);
2. a line count above the manifest's `lines` is refused (no growth by edit,
   inside a span or outside one). A deleted span or line passes;
3. a span in a seam script whose home (`home`) is another seam is refused,
   naming its home. A span the manifest pins under `seam_pins` keeps the
   script it is pinned to, so a later edit of the module table moves no span
   already placed: the PR that edits the table pins the spans it would move.
   A seam script whose name is no seam, or whose text imports or names
   tests/features.py (the two would share a process and a kill path), is
   refused too.

The manifest is tests/features_frozen_budgets.json. Its `_budgets.json` name
puts it under budget-raise-gate: it has no SCHEMA entry, so every leaf is
FROZEN and any change to it, a raise of `lines`, a new span id or a new pin,
merges only on the owner's approving review or under a mandate's
`## Raise justification` (CLAUDE.md rule 2, decision 0013). A PR that appends
a span and re-records the manifest in the same diff is therefore refused by
the gate, not by this check. `--record` writes it; never edit it by hand.

The seam rule (design revision 1, step A): take the distinct production
modules a span names (imports and module aliases, `const`, `coordinator` and
the package `__init__` excluded); the seam holding the most wins, a tie going
to the first of ORDER; a module the table does not list counts as `surface`;
a span naming none goes to `cycle`.

A seam script is created by the first PR that needs it, never empty in
advance. That PR adds its `run` line to tests/run.sh's lane beside
features.py, its closure (tests/derive_closures.sh on Linux), its
`case_select.SCRIPTS` entry and its spans (`--cases`). Each seam script adds
2 to `script_runs_per_push` and 2 to `script_runs_full_case_pr` in
tests/ci_budgets.json, both MAX keys: that raise merges only on the owner's
approving review at its head or, under a mandate in force scoped
`budget-raise` or `all`, with a `## Raise justification` listing the payments
tried and an `Architecture score: dS` line. The freeze PR's own payment tried
does not carry over to those PRs.

What the freeze costs: a production change whose existing features.py test
needs one more line must net the line out elsewhere in the file, move the
test to a seam script, or raise `lines` through the gate. D5's s7 units
cannot grow by lines; they can still grow at a constant line count.

The split the owner asked for is not done. Its re-key was priced on the
spike (handoff-wip/r11-owner-features-split-spike ef2d5cd716) at an
expected 372156 CPU-s: a point estimate, biased low, from samples of n=6
(phase E: three finished, three stopped while in flight) and n=4 (MOD), with
no recorded seed, phase C's x2 assumed and the M and L strata counted at 0.
It is no bound on the population mean. The figure that alone exceeds the
150000 CPU-s cap is 166731 CPU-s, stratum E's find pass (phase F) over the
340 rows first reached in spans 0-2, on the same samples. Both print from the
spike's `stratlb.py` (the design note's `## Figures` names the command).
Freeze instead of split is decision: owner, taken by the orchestrator under
mandate 6893738184 and pending owner confirmation.

    python3 dev/audit/harnesses/features_freeze.py --check     # the refusals, exit 1 on any
    python3 dev/audit/harnesses/features_freeze.py --seam FILE # each span's home seam
    python3 dev/audit/harnesses/features_freeze.py --record    # re-write the manifest
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
import case_select as cs  # noqa: E402

FROZEN_SCRIPT = "tests/features.py"
MANIFEST = "tests/features_frozen_budgets.json"
PKG = "heatpump_optimizer"
SEAMS = {
    "inputs": "inputs pump_signals pump_mode running_signal flow_meter heat_energy open_meteo external_heat "
              "setpoint_check rooms room_history room_record",
    "model": "thermal_model sysid accuracy comfort_learning curve_learning dhw_learning defrost learner_progress "
             "learning_freeze slab_seed drift flow_lift heat_curve presets batchmath",
    "plan": "optimizer tariff price_model price_tiles pv battery grid_fee currency solve_gate plan_slots plan_step "
            "whatif early_cutoff comfort_band comfort_floor quiet_windows silent_mode freq_control duty_ledger "
            "duty_legs duty_switch wear runs driving_grade process_worker",
    "dhw": "dhw_planner dhw_schedule dhw_draws dhw_start disinfection legionella draw_range wood_fuel circulation",
    "actuation": "pump_arbiter mixing_valve supply_hold flow_limit power_guard boost away off_restore "
                 "number_restore slot_drivers pump_schedule manual_plan climate switch datetime",
}
ORDER = ("inputs", "model", "plan", "dhw", "actuation", "surface")
ALL_SEAMS = ORDER + ("cycle",)
MOD2SEAM = {m: s for s, ms in SEAMS.items() for m in ms.split()}
EXCLUDED = frozenset({"const", "coordinator", "__init__"})


def _prod_module(path: str) -> str | None:
    if path.startswith("custom_components."):
        path = path[len("custom_components."):]
    if not (path == PKG or path.startswith(PKG + ".")):
        return None
    rest = path[len(PKG):].lstrip(".").split(".")
    return rest[0] if rest and rest[0] else "__init__"


def home(span, aliases: dict[str, str]) -> str:
    """The seam a span belongs to, by the step-A rule in the docstring."""
    mods = set()
    for top in span.stmts:
        for n in ast.walk(top):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module:
                names = [f"{n.module}.{a.name}" for a in n.names]
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in aliases:
                names = [aliases[n.id]]
            mods.update(m for m in map(_prod_module, names) if m)
    count: dict[str, int] = {}
    for m in mods - EXCLUDED:
        seam = MOD2SEAM.get(m, "surface")
        count[seam] = count.get(seam, 0) + 1
    if not count:
        return "cycle"
    best = max(count.values())
    return next(p for p in ORDER if count.get(p) == best)


def homes(source: str) -> list[tuple[str, str]]:
    """(span id, home seam) for every span of one script's text."""
    tree = ast.parse(source)
    aliases = cs._aliases(tree)
    return [(s.id, home(s, aliases)) for s in cs.split(source, tree)[2]]


def measure(source: str) -> dict:
    """The manifest's measured fields for tests/features.py's text: its span
    ids in order, as case_select.split yields them, and its line count, as
    `wc -l` counts it."""
    return {"lines": source.count("\n"), "spans": [s.id for s in cs.split(source)[2]]}


def _names_frozen(source: str) -> bool:
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[-1] == "features" for a in n.names):
            return True
        if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[-1] == "features":
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and "features.py" in n.value:
            return True
    return False


def refusals(frozen_source: str, manifest: dict, seam_sources: dict[str, str]) -> list[str]:
    """Every refusal of the freeze, as text naming its condition: `span`
    (condition 1), `lines` (2), `seam` and `header` (3). Empty when the tree
    keeps the freeze. `seam_sources` maps each tests/features_*.py path to
    its text."""
    out = []
    got = measure(frozen_source)
    known = set(manifest["spans"])
    for sid in got["spans"]:
        if sid not in known:
            out.append(f"span: {FROZEN_SCRIPT} has span {sid!r}, which {MANIFEST} does not list; "
                       f"tests/features.py is frozen, so the section goes to a seam script "
                       f"(`--seam` names its home)")
    if got["lines"] > manifest["lines"]:
        out.append(f"lines: {FROZEN_SCRIPT} has {got['lines']} lines, above the {manifest['lines']} "
                   f"{MANIFEST} records; net the growth out, move the test to a seam script, or raise "
                   f"`lines` through budget-raise-gate")
    pins = manifest.get("seam_pins", {})
    for path in sorted(seam_sources):
        seam = Path(path).stem[len("features_"):]
        if seam not in ALL_SEAMS:
            out.append(f"seam: {path} is named for no seam; the seams are {', '.join(ALL_SEAMS)}")
            continue
        text = seam_sources[path]
        if _names_frozen(text):
            out.append(f"header: {path} imports or names tests/features.py; a seam script shares "
                       f"no process and no kill path with the frozen file")
        pinned = set(pins.get(path, []))
        for sid, h in homes(text):
            if h != seam and sid not in pinned:
                out.append(f"seam: {path} holds span {sid!r}, whose home is tests/features_{h}.py")
    return out


def tree_refusals(root: Path = ROOT) -> list[str]:
    """`refusals` over the files at `root`."""
    manifest = json.loads((root / MANIFEST).read_text())
    seams = {str(p.relative_to(root)): p.read_text()
             for p in sorted((root / "tests").glob("features_*.py"))}
    return refusals((root / FROZEN_SCRIPT).read_text(), manifest, seams)


def record(root: Path = ROOT) -> dict:
    """The manifest for the tree at `root`, keeping its existing pins."""
    path = root / MANIFEST
    old = json.loads(path.read_text()) if path.exists() else {}
    new = measure((root / FROZEN_SCRIPT).read_text())
    new["seam_pins"] = old.get("seam_pins", {})
    return {"lines": new["lines"], "seam_pins": new["seam_pins"], "spans": new["spans"]}


def main(argv: list[str]) -> int:
    if argv[:1] == ["--check"]:
        bad = tree_refusals()
        for line in bad:
            print(line)
        print(f"FEATURES FREEZE: {'REFUSED' if bad else 'HOLDS'} ({len(bad)} refusal(s))")
        return 1 if bad else 0
    if argv[:1] == ["--seam"] and len(argv) == 2:
        for sid, h in homes(Path(argv[1]).read_text()):
            print(f"{h}\t{sid}")
        return 0
    if argv[:1] == ["--record"]:
        (ROOT / MANIFEST).write_text(json.dumps(record(), indent=1) + "\n")
        return 0
    print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
