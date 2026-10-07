"""Provenance check for the DHW planner extraction (R9-EG-B5, #1743).

    python3 tools/audit/round9/EG-B5/provenance.py BASE HEAD

Reads both trees from git, so it runs from any checkout holding the two
commits. For every unit the move carries -- the nineteen planner-core methods,
the module-level names only they use, the section banner, and the three shared
helpers -- it cuts the unit's text out of BASE's optimizer.py (decorators and
the comment lines directly above included) and out of its HEAD destination,
and compares the two byte for byte. One unit may differ, and only by the
substitutions listed in SUBSTITUTIONS: the build's return shape. Each
substitution must apply exactly once.

It then prints the residual: BASE's optimizer.py with every moved unit cut
out, diffed against HEAD's optimizer.py. That residual is everything else the
move changed in the file -- the call sites, the imports, the planner's
construction -- and is what a reader reviews by eye.

Its own null control: every unit is compared again against a destination with
one character changed, and each must then differ. Exit 0 only when every unit
matches, nothing is left on the optimizer, the planner carries no method the
table does not name, and the control detects every perturbation.
"""
from __future__ import annotations

import ast
import difflib
import subprocess
import sys

PKG = "custom_components/heatpump_optimizer/"
CORE = (
    "_dhw_planning_prices", "_baseline_dhw_economics", "_effective_dhw_windows",
    "_dhw_legionella_due", "_dhw_legionella_ceilings", "_dhw_legionella_plan",
    "_dhw_coil_wood_forecast", "_dhw_planner_draws", "_dhw_window_floors",
    "_build_dhw_requirements", "_dhw_cop_profile", "_plan_dhw_min_cost",
    "_apply_dhw_pins", "_dhw_plan_temps", "_repair_dhw_floor",
    "_clamp_dhw_to_capacity", "_apply_dhw_min_run", "_dhw_raise_fits",
    "_plan_dhw_cheapest_first",
)
# (name, destination file); a module-level unit.
TOP = (
    ("_dhw_windows_at", "dhw_planner.py"),
    ("_DHW_REFILL_WINDOW_HOURS", "dhw_planner.py"),
    ("_DHW_MIN_RUN_CHUNK", "dhw_planner.py"),
    ("_DhwLegionellaPlan", "dhw_planner.py"),
    ("DhwPlan", "dhw_planner.py"),
    ("_step_humidity", "thermal_model.py"),
    ("_mean_humidity", "thermal_model.py"),
    ("_pin_is_free", "manual_plan.py"),
)
BANNER = (
    "    # ------------------------------------------------------------------\n"
    "    # DHW demand-window planning\n"
    "    # ------------------------------------------------------------------\n"
)
# The one allowed difference: the build returns (plan, requirement) instead of
# stashing the requirement and the legionella step on the optimizer.
SUBSTITUTIONS = {
    "_build_dhw_requirements": (
        ("    ) -> DhwPlan:\n",
         "    ) -> tuple[DhwPlan, np.ndarray]:\n"),
        ("        self._dhw_requirement = requirement\n"
         "        self._dhw_legionella_step = legionella_step\n"
         "\n"
         "        return DhwPlan(\n",
         "        return DhwPlan(\n"),
        ("            max_lead_hours=max_lead_hours,\n"
         "        )\n",
         "            max_lead_hours=max_lead_hours,\n"
         "        ), requirement\n"),
    ),
}
# Module-level names the destination adds that are not moved code: the
# planner's scaffolding, reviewed by eye.
NEW_TOP = {"_LOGGER", "_Horizon", "_PlannerConfig", "DhwPlanner"}


def show(ref: str, path: str) -> str:
    return subprocess.run(["git", "show", f"{ref}:{path}"], check=True,
                          capture_output=True, text=True).stdout


def segment(src: str, name: str, cls: str | None) -> tuple[int, int]:
    """1-based inclusive line span of ``name`` (in ``cls``), leading comments in."""
    tree = ast.parse(src)
    body = tree.body
    if cls is not None:
        body = next(n for n in tree.body
                    if isinstance(n, ast.ClassDef) and n.name == cls).body
    for n in body:
        names = [n.name] if hasattr(n, "name") else [
            t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
        if name in names:
            start = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])])
            lines = src.splitlines(keepends=True)
            while start > 1 and lines[start - 2].lstrip().startswith("#"):
                start -= 1
            return start, n.end_lineno
    raise KeyError(f"{name} not found in {cls or '<module>'}")


def cut(src: str, a: int, b: int) -> str:
    return "".join(src.splitlines(keepends=True)[a - 1:b])


def main(base: str, head: str) -> int:
    opt_base = show(base, PKG + "optimizer.py")
    opt_head = show(head, PKG + "optimizer.py")
    dst = {f: show(head, PKG + f) for f in ("dhw_planner.py", "thermal_model.py", "manual_plan.py")}
    units = [(m, "HeatPumpOptimizer", "dhw_planner.py", "DhwPlanner") for m in CORE]
    units += [(n, None, f, None) for n, f in TOP]
    bad = 0
    pairs = []
    spans = []
    for name, scls, dfile, dcls in units:
        sa, sb = segment(opt_base, name, scls)
        da, db = segment(dst[dfile], name, dcls)
        old, new = cut(opt_base, sa, sb), cut(dst[dfile], da, db)
        spans.append((sa, sb))
        subs = SUBSTITUTIONS.get(name, ())
        applied = old
        ok_subs = True
        for a, b in subs:
            if applied.count(a) != 1:
                ok_subs = False
            applied = applied.replace(a, b)
        where = f"optimizer.py:{sa}-{sb} -> {dfile}:{da}-{db}"
        if ok_subs and applied == new:
            tag = f"IDENTICAL after {len(subs)} listed substitution(s)" if subs else "IDENTICAL"
            print(f"  ok   {name:28s} {sb - sa + 1:4d} lines  {tag}  ({where})")
        else:
            bad += 1
            print(f"  FAIL {name:28s} DIFFERS ({where}; substitutions applied once each: {ok_subs})")
            sys.stdout.writelines(difflib.unified_diff(
                applied.splitlines(keepends=True), new.splitlines(keepends=True),
                "base (after substitutions)", "head", n=1))
        pairs.append((name, applied, new))
    # The banner travels with the block it heads.
    if opt_base.count(BANNER) == 1 and dst["dhw_planner.py"].count(BANNER) == 1 \
            and opt_head.count(BANNER) == 0:
        print(f"  ok   {'(section banner)':28s}    3 lines  IDENTICAL")
        b0 = opt_base[: opt_base.index(BANNER)].count("\n") + 1
        spans.append((b0, b0 + 2))
    else:
        bad += 1
        print("  FAIL (section banner) not moved exactly once")

    left = [m for m in CORE if f"    def {m}(" in opt_head]
    ptree = ast.parse(dst["dhw_planner.py"])
    planner = next(n for n in ptree.body if isinstance(n, ast.ClassDef) and n.name == "DhwPlanner")
    extra = [n.name for n in planner.body
             if isinstance(n, ast.FunctionDef) and n.name not in CORE and n.name != "__init__"]
    top_new = sorted(
        (n.name if hasattr(n, "name") else ast.unparse(n.targets[0]))
        for n in ptree.body
        if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign))
        and (n.name if hasattr(n, "name") else ast.unparse(n.targets[0])) not in {t for t, _ in TOP}
    )
    print(f"\n  still defined on HeatPumpOptimizer at HEAD: {left}")
    print(f"  DhwPlanner methods the table does not name (besides __init__): {extra}")
    print(f"  dhw_planner.py module-level names that are not moved code: {top_new}")
    if left or extra or set(top_new) != NEW_TOP:
        bad += 1

    # Residual: BASE's optimizer.py less every moved unit (and the blank lines
    # after it), against HEAD's.
    lines = opt_base.splitlines(keepends=True)
    drop = set()
    for a, b in spans:
        drop.update(range(a, b + 1))
        j = b + 1
        while j <= len(lines) and lines[j - 1].strip() == "":
            drop.add(j)
            j += 1
    rest = [l for i, l in enumerate(lines, 1) if i not in drop]
    diff = list(difflib.unified_diff(rest, opt_head.splitlines(keepends=True),
                                     "optimizer.py at BASE, moved units cut",
                                     "optimizer.py at HEAD", n=2))
    plus = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    minus = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    print(f"\n  residual diff in optimizer.py: +{plus} -{minus} lines")
    sys.stdout.writelines(diff)

    # Null control: one character changed in each destination unit is caught.
    caught = sum(1 for _, applied, new in pairs
                 if applied != new[:-2] + ("X" if new[-2] != "X" else "Y") + new[-1:])
    print(f"\n  control: {caught} of {len(pairs)} single-character perturbations detected")
    if caught != len(pairs):
        bad += 1
    print(f"\nPROVENANCE {'FAILED' if bad else 'PASSED'}: {len(pairs)} units, "
          f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
