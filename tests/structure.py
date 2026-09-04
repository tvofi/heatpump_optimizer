#!/usr/bin/env python3
"""The structural ratchet of the decomposition program (#193), PR-0.

Measures the integration's STRUCTURE -- shapes an AST can see, never values
-- and ratchets it against the committed budget table in
``tests/structure_budgets.json`` (the ``tests/stress_budgets.json`` idea
applied to counts instead of timings). The program this pins is the
coordinator decomposition planned on #193: PRs that follow may only move
these numbers down. Anything that pushes one up fails here, with the delta.

Every metric is a COUNT (plus one fraction) computed with stdlib ``ast``
over ``custom_components/heatpump_optimizer/**/*.py``, and every one comes
with file:line evidence printed above its RESULT line. Counts do not care
about box load, so there is no timing guard here; the thread pin below is
the toolkit's habit, not a measurement.

Metrics (definitions, one line each; the code is the authority):

  classes_over_300            classes whose source span (ClassDef lineno to
                              end_lineno) is more than 300 lines
  attrbag_classes_over_30     classes assigning more than 30 distinct
                              ``self.*`` attributes anywhere in their methods
  methods_over_200 /          functions (methods included, nested included)
  methods_over_150            whose span is more than 200 / 150 lines
  max_class_loc               the largest class span in the integration
  coordinator_loc /           the same span, method count, distinct assigned
  coordinator_methods /       self-attrs and attrs assigned in more than one
  coordinator_attrs /         method, for the TOP attr-bag class -- which
  coordinator_multiassigned   this harness asserts is the coordinator; if
                              another class ever out-attrs it, this fails so
                              the budget is re-recorded deliberately
  duplication_blocks          maximal runs of >= DUP_BLOCK_LINES consecutive
                              normalized lines (whitespace/comments stripped)
                              that appear in more than one function of the
                              same module, nested defs excluded from their
                              parents so containment is not reported as
                              duplication
  functions_cc_over_25 /      cyclomatic complexity 1 + decision points
  functions_cc_over_15        (if/elif, for, while, ternary, except, assert,
                              boolean operator terms beyond the first, each
                              comprehension clause and its ifs, each match
                              case), counted over the whole function span
                              including nested defs
  const_modules_over_50       modules importing more than 50 names from
                              ``.const``
  local_imports               Import/ImportFrom statements inside a function
                              scope, anywhere in the integration
  dead_top_level_symbols      top-level defs/classes/assignments never
                              referenced by name anywhere else in the
                              integration (dunder, HA entry points, HA
                              convention constants and ConfigFlow/OptionsFlow
                              subclasses excluded -- Home Assistant finds
                              those by convention, not by import). A reference
                              is a name load, an attribute name, or BOTH halves
                              of an aliased import (``module_references``); the
                              four constants a runtime ``getattr`` assembles
                              are exempted by name, with their proof re-checked
                              on every run (``DYNAMIC_REFERENCES``)
  internal_call_edges         ``self.m(...)`` call occurrences inside the
                              coordinator where ``m`` is one of its own methods
  cross_seam_fraction         the fraction of those edges whose endpoints sit
                              in different name-regex seam buckets (dhw /
                              learning / fetch / grid / views, first regex
                              wins, everything else is core)
  cut_<seam>                  per-seam cut cost: cross attr refs + cross
                              method refs the extraction would have to make
                              explicit -- attribute references on self
                              crossing the ownership boundary (an attr is
                              owned by a seam when any of its methods assigns
                              it) in EITHER direction, plus self-method call
                              occurrences crossing in either direction

Run:

    python tests/structure.py             ratchet: metrics vs budgets, FAIL on
                                          any worsening (floats tolerate
                                          +-0.005), headroom printed for any
                                          improvement
    python tests/structure.py --record    recompute and WRITE the budget table
                                          (run this on a clean tree, at the
                                          SHA recorded in ``recorded_at``).
                                          REFUSES if any metric would move the
                                          wrong way; tolerance metrics are
                                          carried forward, never re-recorded

    python tests/structure.py --record --allow-regression="<reason>"
                                          record anyway, for a stated reason
                                          that belongs in the COMMIT message

Expected at the recorded baseline (tolerance 0 on every count): exactly the
numbers in ``tests/structure_budgets.json``. Baseline SHA: the commit in that
file's ``recorded_at``. Every number here is a count, immune to box load.

Wired into ``tests/run.sh`` (lane_units) and ``tests/derive_closures.sh``.
This script READS the whole integration, so its measured closure is large by
design: touching any integration file puts this lane in scope.
"""
from __future__ import annotations

import os

# The toolkit's thread pin (tools/audit/README.md): set before anything else
# is imported. Nothing here imports numpy and no RESULT below is a timing,
# but the habit is cheap and it keeps this script's environment identical to
# every other lane script on the box.
for _pin in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_pin, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = REPO_ROOT / "custom_components" / "heatpump_optimizer"
BUDGET_FILE = REPO_ROOT / "tests" / "structure_budgets.json"

# The class the whole program (#193) is about. The attr-bag metrics below are
# "for the top one (the coordinator)": if some other class ever becomes the
# biggest attr bag, the numbers change meaning, so the harness fails loudly
# instead of quietly ratcheting the wrong thing.
COORDINATOR_CLASS_NAME = "HeatPumpOptimizerCoordinator"

GOD_CLASS_LOC_LIMIT = 300
ATTR_BAG_LIMIT = 30
MONSTER_LIMITS = (200, 150)
# The duplication window (#369). It was 30, and the longest duplicated
# normalized run that exists anywhere in the integration is 19 -- so the
# metric could not fire, and its recorded 0 described the detector, not the
# tree. Measured over the whole package at a2c4982, changing only this
# constant and re-running measure():
#
#     window     30   25   20   15   12   10    8    6
#     blocks      0    0    0    4    6   13   32   76
#
# 10 is where the evidence stops: it is the largest window that sees the
# optimizer's objective / objective_batch closure pairs (11 and 10 normalized
# lines), which are the most-cited duplication in this codebase and the one
# 15 misses; 8 and below buy volume at a precision nobody has measured. No
# Home Assistant entity boilerplate is caught at any window down to 10 -- the
# 154 single-call __init__ bodies, the obvious false-positive class, appear
# in no row. Every one of the 13 rows sits inside an open decomposition issue
# (#193, #223, #224, #225), so the count ratchets down as that program lands.
DUP_BLOCK_LINES = 10
CC_LIMITS = (25, 15)
CONST_FANOUT_LIMIT = 50

# The seam partition of #193's plan of record: a method belongs to the FIRST
# seam whose regex matches its name; everything else is core. Order matters
# and is part of the metric definition -- a method named _fetch_dhw_prices is
# a dhw method, not a fetch method.
SEAM_REGEXES: list[tuple[str, re.Pattern[str]]] = [
    ("dhw", re.compile(r"dhw|hot_water|legionella|draw")),
    ("learning", re.compile(r"learn|reanchor|drift|curve|comfort|cop")),
    ("fetch", re.compile(r"fetch|tibber|weather|solar|price")),
    ("grid", re.compile(r"grid|peak|fuse|power|outage|tariff|ledger")),
    ("views", re.compile(r"view|build_data|publish|payload")),
]

# Names Home Assistant loads by convention (it imports the module and looks
# these up, or scans for subclasses), so "no integration module imports it"
# does not mean dead. Anything added here must say which convention it is.
HA_CONVENTION_NAMES = {
    "async_setup",
    "async_setup_entry",
    "async_unload_entry",
    "async_migrate_entry",
    "async_get_options_flow",
    "async_remove_entry",
    "async_remove_config_entry_device",
    "async_get_config_entry_diagnostics",
    "async_redact_data",
    "async_get_engine",
    "async_get_config_flow_dialect",
    # Module-level constants the HA framework reads off platform modules.
    "CONFIG_SCHEMA",
    "PARALLEL_UPDATES",
    "PLATFORMS",
}

# Symbols no static scan can see, because the name is assembled at runtime.
# An EXPLICIT, RE-CHECKED allowlist -- not a widening of what "referenced"
# means (``dynamic_reference_audit`` says why that trade is refused).
#
# ``thermal_model.py`` reads config keys off a table of bare suffix strings
# and resolves each with ``getattr(const, f"CONF_{conf}")``, so the ``CONF_``
# prefix never appears as a token and no census over names can find these
# four. #338 -- "Ten dead symbols go, four dynamic-lookup constants stay
# proven alive" -- proved them alive with a runtime sentinel and deliberately
# kept them, and the gate went on reporting them dead: a merged PR's evidence
# and the standing gate disagreeing, with nothing reconciling them (#364).
# This table is that reconciliation, and every run re-checks the proof.
#
#   (module, symbol) -> (proof module, the bare string, the getattr prefix, why)
DYNAMIC_REFERENCES: dict[tuple[str, str], tuple[str, str, str, str]] = {
    ("const.py", "CONF_BUFFER_TANK_LOSS"): (
        "thermal_model.py", "BUFFER_TANK_LOSS", "CONF_",
        "#338: _tabled_values row buffer_tank_heat_loss, sentinel-proven alive",
    ),
    ("const.py", "CONF_SOLAR_UPPER_FRACTION"): (
        "thermal_model.py", "SOLAR_UPPER_FRACTION", "CONF_",
        "#338: _tabled_values row solar_upper_fraction, sentinel-proven alive",
    ),
    ("const.py", "CONF_HOUSE_HEAT_LOSS_SCALE"): (
        "thermal_model.py", "HOUSE_HEAT_LOSS_SCALE", "CONF_",
        "#338: _tabled_values row house_heat_loss_scale, sentinel-proven alive",
    ),
    ("const.py", "CONF_LOWER_FLOOR_LOSS_RATIO"): (
        "thermal_model.py", "LOWER_FLOOR_LOSS_RATIO", "CONF_",
        "#338: _tabled_values row lower_floor_loss_ratio, sentinel-proven alive",
    ),
}

# Metrics that are fractions, not counts: they compare with a tolerance
# instead of "must not exceed", because a one-method change moves them by
# less than the noise of rounding. Everything else must be <= its budget.
FRACTION_METRICS = {"cross_seam_fraction"}
FRACTION_TOLERANCE = 0.005


# ---------------------------------------------------------------------------
# small AST helpers


def module_trees() -> list[tuple[Path, ast.Module]]:
    """Every integration module, parsed, in a stable order."""
    out = []
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        out.append((path, ast.parse(path.read_text(), filename=str(path))))
    return out


def span_loc(node: ast.AST) -> int:
    """Source span in lines (the def/class line through the last line)."""
    return node.end_lineno - node.lineno + 1  # type: ignore[attr-defined]


def all_functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def nested_spans(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[tuple[int, int]]:
    """(start, end) of every def/class nested directly or deeply in fn.

    Decorator lines belong to the nested definition, not the parent, so the
    span starts at the earliest decorator.
    """
    spans = []
    for child in ast.walk(fn):
        if child is fn:
            continue
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            starts = [d.lineno for d in getattr(child, "decorator_list", [])]
            spans.append((min(starts + [child.lineno]), child.end_lineno))
    return spans


def module_references(tree: ast.Module) -> set[str]:
    """Every name this module references, for the dead-symbol screen.

    Every name anyone reads, plus every name any import binds: an import is a
    reference even when the name is then used only as an attribute of the
    module. Attribute names count too -- coarse, but this is a screen for
    accidental deadness, not a linker. A load of name N from inside the body of
    a top-level function also called N is recursion, not a reference from
    elsewhere, so it does not count.

    **Both halves of an aliased import count** (#364). ``import x as y`` binds
    ``y``, but it also *names* ``x``, and ``x`` is the definition that would go
    if this screen were believed. Recording only ``asname`` made every aliased
    import in the tree invisible to the census -- the hole #281's panel had
    already corrected in the D7 audit harness, about this same symbol, without
    anyone checking the production gate for it. ``grid_fee.max_abs_component``
    is imported at ``coordinator.py:353`` as ``grid_fee_max_abs_component`` and
    called on every planning cycle of a grid-fee install; the gate called it
    dead.

    A symbol reached only through a runtime lookup is NOT handled here -- see
    ``DYNAMIC_REFERENCES``. Widening what "referenced" means for every symbol
    in the tree, so that four constants come out right, is the trade this
    function deliberately does not make.
    """
    own_fn_ranges: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            own_fn_ranges[node.name] = (node.lineno, node.end_lineno)

    referenced: set[str] = set()

    def note_reference(name: str, lineno: int) -> None:
        span = own_fn_ranges.get(name)
        if span and span[0] <= lineno <= span[1]:
            return  # the symbol's own body: recursion, not a reference
        referenced.add(name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            note_reference(node.id, node.lineno)
        elif isinstance(node, ast.Attribute):
            note_reference(node.attr, node.lineno)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                note_reference(alias.name.split(".")[-1], node.lineno)
                if alias.asname:
                    note_reference(alias.asname, node.lineno)

    return referenced


def dynamic_reference_audit(
    trees: list[tuple[Path, ast.Module]],
    top_level_defs: dict[tuple[str, str], int],
    referenced_names: set[str],
    entries: dict[tuple[str, str], tuple[str, str, str, str]] | None = None,
) -> tuple[set[tuple[str, str]], list[str]]:
    """Check every ``DYNAMIC_REFERENCES`` entry, and say which still hold.

    Returns ``(exempt, problems)``: the ``(rel, name)`` keys whose proof holds
    and which the dead-symbol screen should therefore skip, and one message per
    entry whose proof does not hold. A non-empty ``problems`` fails the run --
    an allowlist nobody re-checks is how a genuinely dead symbol gets kept
    alive in silence, which would be strictly worse than the false positives
    this list exists to remove.

    Four things are checked per entry, and each one is a way for the list to
    rot:

    1. the symbol still exists at top level in the module named;
    2. it is still statically unreferenced -- an entry that is no longer doing
       any work must go, so the list never grows a member it does not need;
    3. the bare string that names it is still a string literal in the module
       named as the proof site;
    4. that same module still assembles the name, ``getattr(x, f"PREFIX{..}")``
       with this entry's prefix.

    3 and 4 are the pair #338 proved with a runtime sentinel. They are checked
    at four hand-written ``(symbol, proof site, literal, prefix)`` addresses
    and nowhere else: this does not make a bare string count as a reference
    anywhere in the tree. That census is the tempting generalisation and it is
    the wrong one -- it would redefine "referenced" for every top-level symbol
    in the tree and buy its generality with false NEGATIVES: a genuinely dead
    symbol kept alive because its name turns up in some unrelated string. This
    metric exists to catch deadness; under-reporting is the failure it must
    not have, and over-reporting is only annoying. (``tvofi-claude-09``, #364.)

    A FIFTH dynamic constant needs no help from this function to be caught: it
    is not in the list, so it is reported dead and the ratchet fails at the
    count. The list can only ever absorb an entry a human writes down.
    """
    by_module = {p.relative_to(PACKAGE_DIR).as_posix(): t for p, t in trees}
    problems: list[str] = []
    exempt: set[tuple[str, str]] = set()

    for (module, name), (proof_module, literal, prefix, why) in sorted(
        (DYNAMIC_REFERENCES if entries is None else entries).items()
    ):
        rel = str((PACKAGE_DIR / module).relative_to(REPO_ROOT))
        where = f"DYNAMIC_REFERENCES[{module}:{name}]"
        if (rel, name) not in top_level_defs:
            problems.append(
                f"{where}: {name} is no longer a top-level symbol in {module};"
                " delete the entry")
            continue
        if name in referenced_names:
            problems.append(
                f"{where}: {name} is statically referenced now, so the entry"
                " does nothing; delete it")
            continue
        proof_tree = by_module.get(proof_module)
        if proof_tree is None:
            problems.append(
                f"{where}: the proof module {proof_module} is gone; re-prove"
                f" {name} or delete it ({why})")
            continue
        has_literal = any(
            isinstance(n, ast.Constant) and n.value == literal
            for n in ast.walk(proof_tree)
        )
        has_lookup = any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "getattr"
            and len(n.args) >= 2
            and isinstance(n.args[1], ast.JoinedStr)
            and n.args[1].values
            and isinstance(n.args[1].values[0], ast.Constant)
            and n.args[1].values[0].value == prefix
            for n in ast.walk(proof_tree)
        )
        if not has_literal:
            problems.append(
                f"{where}: {proof_module} no longer contains the literal"
                f" {literal!r}, so nothing reaches {name}; it is dead now"
                f" ({why})")
            continue
        if not has_lookup:
            problems.append(
                f"{where}: {proof_module} no longer assembles names with"
                f" getattr(x, f\"{prefix}{{..}}\"), so nothing reaches {name};"
                f" it is dead now ({why})")
            continue
        exempt.add((rel, name))

    return exempt, problems


def cyclomatic_complexity(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """1 + decision points, nested defs included (they are part of the span)."""
    cc = 1
    for node in ast.walk(fn):
        if isinstance(
            node,
            (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler, ast.Assert),
        ):
            cc += 1
        elif isinstance(node, ast.BoolOp):
            cc += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            cc += 1 + len(node.ifs)
        elif isinstance(node, ast.match_case):
            cc += 1
    return cc


# ---------------------------------------------------------------------------
# the metrics


def normalized_function_lines(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, src_lines: list[str]
) -> list[tuple[int, str]]:
    """``fn``'s body as (segment, stripped-source) pairs, nested defs removed.

    Blank and comment-only lines are dropped, so reformatting and commentary
    are not duplication. Each nested def/class span is cut out and bumps the
    segment counter, so a window is never allowed to span the hole a nested
    definition left behind -- containment is not a copy.
    """
    excluded = nested_spans(fn)
    normalized: list[tuple[int, str]] = []
    segment = 0
    for lineno in range(fn.lineno, fn.end_lineno + 1):  # type: ignore[arg-type]
        if any(a <= lineno <= b for a, b in excluded):
            segment += 1
            continue
        stripped = src_lines[lineno - 1].strip()
        if not stripped or stripped.startswith("#"):
            continue
        normalized.append((segment, stripped))
    return normalized


def duplicate_runs(
    normalized_functions: dict[tuple, list[tuple[int, str]]], window: int
) -> list[tuple[str, str, int, str, int]]:
    """Maximal runs of >= ``window`` normalized lines shared by two functions.

    ``window`` is a parameter and not a read of ``DUP_BLOCK_LINES`` for one
    reason: it is the only knob this metric has, and #369 was the case of a
    knob set past the point where the detector could see anything at all --
    30, against a longest real run of 19. A caller can therefore ask what the
    same tree looks like at another window, which is how that was established
    and how the tests pin both ends of it.

    Returns one row per (function, run): ``(file, func, func_line, "norm
    a-b", length)``, sorted, with overlapping windows merged into the longest
    run that covers them.
    """
    windows: dict[str, list[tuple[tuple, int]]] = defaultdict(list)
    for fid, normalized in normalized_functions.items():
        for i in range(len(normalized) - window + 1):
            if normalized[i][0] != normalized[i + window - 1][0]:
                continue  # the window spans an excluded (nested) gap
            digest = hashlib.sha1(
                "\n".join(line for _, line in normalized[i : i + window]).encode()
            ).hexdigest()
            windows[digest].append((fid, i))

    covered: dict[tuple, list[tuple[int, int]]] = defaultdict(list)
    for sites in windows.values():
        owners = {fid for fid, _ in sites}
        if len(owners) < 2:
            continue
        for fid, start in sites:
            covered[fid].append((start, start + window))

    rows: list[tuple[str, str, int, str, int]] = []
    for fid, spans in covered.items():
        spans.sort()
        runs = []
        run_start, run_end = spans[0]
        for a, b in spans[1:]:
            if a <= run_end:
                run_end = max(run_end, b)
            else:
                runs.append((run_start, run_end))
                run_start, run_end = a, b
        runs.append((run_start, run_end))
        for a, b in runs:
            rows.append((fid[0], fid[1], fid[2], f"norm {a}-{b - 1}", b - a))
    return sorted(rows)


def measure() -> dict:
    """Recompute every metric from the working tree. Returns a dict with the
    flat metric values (the budget keys) under ``metrics`` and everything the
    evidence tables print under ``tables``."""
    trees = module_trees()

    god_classes = []       # (loc, file, span, name, methods, attrs)
    attrbag_classes = []   # (attrs, file, line, name)
    per_class_attrs = {}   # (file, name) -> {attr: set(method names)}
    monsters = []          # (loc, file, span, name)
    cc_scores = []         # (cc, file, line, name)
    const_fanout = {}      # file -> imported names from .const
    local_imports = []     # (file, line, statement)
    dead_symbols = []      # (file, line, name)
    duplication = []       # (file, func_name, func_line, start-end, length)

    # -- classes, functions, imports, dead symbols -------------------------
    top_level_defs: dict[tuple[str, str], int] = {}
    referenced_names: set[str] = set()

    for path, tree in trees:
        rel = str(path.relative_to(REPO_ROOT))
        src_lines = path.read_text().splitlines()

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not (node.name.startswith("__") and node.name.endswith("__")):
                    top_level_defs[(rel, node.name)] = node.lineno
            elif isinstance(node, ast.ClassDef):
                is_flow = any(
                    (isinstance(b, ast.Name) and b.id.endswith(("ConfigFlow", "OptionsFlow")))
                    or (isinstance(b, ast.Attribute) and b.attr.endswith(("ConfigFlow", "OptionsFlow")))
                    for b in node.bases
                )
                if not (node.name.startswith("__") and node.name.endswith("__")) and not is_flow:
                    top_level_defs[(rel, node.name)] = node.lineno
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("__"):
                        top_level_defs[(rel, target.id)] = node.lineno
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if not node.target.id.startswith("__"):
                    top_level_defs[(rel, node.target.id)] = node.lineno

        referenced_names |= module_references(tree)

        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            methods = [
                m
                for m in cls.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            attr_writers: dict[str, set[str]] = defaultdict(set)
            for method in methods:
                for node in ast.walk(method):
                    if (
                        isinstance(node, ast.Attribute)
                        and isinstance(node.value, ast.Name)
                        and node.value.id == "self"
                        and isinstance(node.ctx, ast.Store)
                    ):
                        attr_writers[node.attr].add(method.name)
            loc = span_loc(cls)
            if loc > GOD_CLASS_LOC_LIMIT:
                god_classes.append(
                    (loc, rel, f"{cls.lineno}-{cls.end_lineno}", cls.name,
                     len(methods), len(attr_writers))
                )
            if len(attr_writers) > ATTR_BAG_LIMIT:
                attrbag_classes.append((len(attr_writers), rel, cls.lineno, cls.name))
            per_class_attrs[(rel, cls.name)] = attr_writers

        for fn in all_functions(tree):
            loc = span_loc(fn)
            if loc > MONSTER_LIMITS[1]:
                monsters.append((loc, rel, f"{fn.lineno}-{fn.end_lineno}", fn.name))
            cc = cyclomatic_complexity(fn)
            if cc > CC_LIMITS[1]:
                cc_scores.append((cc, rel, fn.lineno, fn.name))

        fanout = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (
                (node.level == 1 and node.module == "const")
                or node.module == "heatpump_optimizer.const"
            ):
                fanout += len(node.names)
        if fanout:
            const_fanout[rel] = fanout

        # Local (function-scope) imports: an Import/ImportFrom statement is
        # local when it sits inside any def. Walked from the module root so
        # each statement is seen exactly once; nesting depth only decides
        # the scope, and an import inside a nested def is still one local
        # import.
        def scan_scope(nodes, inside_function: bool) -> None:
            for node in nodes:
                if isinstance(node, (ast.Import, ast.ImportFrom)) and inside_function:
                    local_imports.append((rel, node.lineno, type(node).__name__))
                for field in ("body", "finalbody", "orelse"):
                    for child in getattr(node, field, []):
                        scan_scope(
                            [child],
                            inside_function
                            or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)),
                        )
        scan_scope(tree.body, False)

        # Duplication: normalized DUP_BLOCK_LINES-line windows shared by more
        # than one function of this module. Normalization strips whitespace
        # and comment-only lines; nested def/class spans are dropped from the
        # parent so a handler defined inside a registrar is not "a copy" of
        # its own container.
        normalized_functions: dict[tuple, list[tuple[int, str]]] = {}
        for fn in all_functions(tree):
            normalized_functions[(rel, fn.name, fn.lineno)] = normalized_function_lines(
                fn, src_lines
            )
        duplication.extend(duplicate_runs(normalized_functions, DUP_BLOCK_LINES))

    # -- dead top-level symbols --------------------------------------------
    dynamic_exempt, dynamic_problems = dynamic_reference_audit(
        trees, top_level_defs, referenced_names
    )
    for (rel, name), lineno in sorted(top_level_defs.items()):
        if name in HA_CONVENTION_NAMES:
            continue
        if name in referenced_names:
            continue
        if (rel, name) in dynamic_exempt:
            continue
        dead_symbols.append((rel, lineno, name))

    # -- the coordinator's seam metrics ------------------------------------
    coordinator = seam_table = None
    coord_file = PACKAGE_DIR / "coordinator.py"
    coord_tree = next(t for p, t in trees if p == coord_file)
    coord_class = next(
        n
        for n in ast.walk(coord_tree)
        if isinstance(n, ast.ClassDef) and n.name == COORDINATOR_CLASS_NAME
    )
    coord_methods = {
        m.name: m
        for m in coord_class.body
        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    def seam_bucket(method_name: str) -> str:
        for label, regex in SEAM_REGEXES:
            if regex.search(method_name):
                return label
        return "core"

    buckets = {name: seam_bucket(name) for name in coord_methods}
    attr_refs: dict[str, Counter] = defaultdict(Counter)  # attr -> bucket -> occurrences
    attr_owners: dict[str, set[str]] = defaultdict(set)   # attr -> buckets that store it
    call_edges = Counter()                                # (caller bucket, callee bucket) -> occurrences
    for name, fn in coord_methods.items():
        bucket = buckets[name]
        for node in ast.walk(fn):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "self"
                and node.attr not in coord_methods
            ):
                attr_refs[node.attr][bucket] += 1
                if isinstance(node.ctx, ast.Store):
                    attr_owners[node.attr].add(bucket)
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "self"
                and node.func.attr in coord_methods
            ):
                call_edges[(bucket, buckets[node.func.attr])] += 1

    total_edges = sum(call_edges.values())
    cross_edges = sum(c for (a, b), c in call_edges.items() if a != b)
    cross_seam_fraction = (cross_edges / total_edges) if total_edges else 0.0

    seam_rows = []
    cut_costs = {}
    for label, _ in SEAM_REGEXES:
        owned = {attr for attr, owners in attr_owners.items() if label in owners}
        cross_attr_refs = 0
        for attr, counter in attr_refs.items():
            inside = counter.get(label, 0)
            outside = sum(c for b, c in counter.items() if b != label)
            cross_attr_refs += outside if attr in owned else inside
        cross_method_refs = sum(
            c
            for (a, b), c in call_edges.items()
            if (a == label) != (b == label)
        )
        seam_rows.append(
            (label, sum(1 for b in buckets.values() if b == label), len(owned),
             cross_attr_refs, cross_method_refs, cross_attr_refs + cross_method_refs)
        )
        cut_costs[f"cut_{label}"] = cross_attr_refs + cross_method_refs

    coord_attr_writers = per_class_attrs[
        (str(coord_file.relative_to(REPO_ROOT)), COORDINATOR_CLASS_NAME)
    ]
    coordinator = {
        "coordinator_loc": span_loc(coord_class),
        "coordinator_methods": len(coord_methods),
        "coordinator_attrs": len(coord_attr_writers),
        "coordinator_multiassigned_attrs": sum(
            1 for writers in coord_attr_writers.values() if len(writers) > 1
        ),
    }

    # The attr-bag metrics are "for the top one (the coordinator)". If that
    # ever stops being true the budget changes meaning, so say it here
    # instead of ratcheting a different class's numbers by accident.
    attrbag_classes.sort(reverse=True)
    top_attrbag = attrbag_classes[0] if attrbag_classes else None
    top_is_coordinator = bool(
        top_attrbag and top_attrbag[3] == COORDINATOR_CLASS_NAME
    )

    metrics = {
        "classes_over_300": len(god_classes),
        "attrbag_classes_over_30": len(attrbag_classes),
        "methods_over_200": sum(1 for loc, *_ in monsters if loc > MONSTER_LIMITS[0]),
        "methods_over_150": len(monsters),
        "max_class_loc": max((g[0] for g in god_classes), default=0),
        "duplication_blocks": len(duplication),
        "functions_cc_over_25": sum(1 for cc, *_ in cc_scores if cc > CC_LIMITS[0]),
        "functions_cc_over_15": len(cc_scores),
        "const_modules_over_50": sum(1 for n in const_fanout.values() if n > CONST_FANOUT_LIMIT),
        "local_imports": len(local_imports),
        "dead_top_level_symbols": len(dead_symbols),
        "internal_call_edges": total_edges,
        "cross_seam_fraction": round(cross_seam_fraction, 4),
        **coordinator,
        **cut_costs,
    }
    tables = {
        "god_classes": sorted(god_classes, reverse=True),
        "attrbag_classes": attrbag_classes,
        "top_is_coordinator": top_is_coordinator,
        "monsters": sorted(monsters, reverse=True),
        "cc_scores": sorted(cc_scores, reverse=True),
        "const_fanout": dict(sorted(const_fanout.items(), key=lambda kv: -kv[1])),
        "local_imports": sorted(local_imports),
        "dead_symbols": dead_symbols,
        "dynamic_exempt": sorted(dynamic_exempt),
        "dynamic_problems": dynamic_problems,
        "duplication": sorted(duplication),
        "seam_rows": seam_rows,
        "cross_edges": cross_edges,
    }
    return {"metrics": metrics, "tables": tables}


# ---------------------------------------------------------------------------
# printing


def print_report(result: dict) -> None:
    tables = result["tables"]
    metrics = result["metrics"]

    print("########## god classes (> %d LOC) ##########" % GOD_CLASS_LOC_LIMIT)
    for loc, rel, span, name, methods, attrs in tables["god_classes"]:
        print(f"  {rel}:{span}  {loc} LOC  {methods} methods  {attrs} self-attrs  {name}")

    print()
    print("########## attr bags (> %d assigned self-attrs) ##########" % ATTR_BAG_LIMIT)
    for attrs, rel, line, name in tables["attrbag_classes"]:
        note = "  <- top attr bag" if (attrs, rel, line, name) == tables["attrbag_classes"][0] else ""
        print(f"  {rel}:{line}  {attrs} self-attrs  {name}{note}")
    if not tables["top_is_coordinator"]:
        print(
            f"  NOTE: the top attr bag is no longer {COORDINATOR_CLASS_NAME}; the"
        )
        print("  coordinator_* budgets describe a different class. Re-record on purpose.")

    print()
    print("########## monster methods: top 10 of %d over %d LOC ##########"
          % (metrics["methods_over_150"], MONSTER_LIMITS[1]))
    for loc, rel, span, name in tables["monsters"][:10]:
        print(f"  {rel}:{span}  {loc} LOC  {name}")

    print()
    print("########## worst 5 cyclomatic (of %d over %d) ##########"
          % (metrics["functions_cc_over_15"], CC_LIMITS[1]))
    for cc, rel, line, name in tables["cc_scores"][:5]:
        print(f"  {rel}:{line}  cc={cc}  {name}")

    print()
    print("########## .const import fan-out (names imported per module) ##########")
    for rel, n in tables["const_fanout"].items():
        flag = "  > %d" % CONST_FANOUT_LIMIT if n > CONST_FANOUT_LIMIT else ""
        print(f"  {rel}: {n}{flag}")

    print()
    print("########## function-scope imports ##########")
    for rel, line, kind in tables["local_imports"]:
        print(f"  {rel}:{line}  {kind}")

    print()
    print("########## dead top-level symbols ##########")
    for rel, line, name in tables["dead_symbols"]:
        print(f"  {rel}:{line}  {name}")

    print()
    print("########## dynamic-reference allowlist (not counted above) ##########")
    for rel, name in tables["dynamic_exempt"]:
        module = (REPO_ROOT / rel).relative_to(PACKAGE_DIR).as_posix()
        proof_module, literal, prefix, why = DYNAMIC_REFERENCES[(module, name)]
        print(f"  ok   {rel}  {name}")
        print(f"         reached by {proof_module}: getattr(x,"
              f" f\"{prefix}{{..}}\") off the literal {literal!r}")
        print(f"         {why}")
    for message in tables["dynamic_problems"]:
        print(f"  FAIL {message}")

    print()
    print("########## duplication (>= %d normalized lines, across functions) ##########"
          % DUP_BLOCK_LINES)
    for rel, name, line, span, length in tables["duplication"]:
        print(f"  {rel}:{line}  {name}  {span}  {length} lines")

    print()
    print("########## coordinator seam table ##########")
    print("  internal self-method call occurrences: %d, crossing a seam: %d"
          % (metrics["internal_call_edges"], tables["cross_edges"]))
    print("  %-8s %8s %6s %6s %6s %6s" % ("seam", "methods", "attrs", "xattr", "xmeth", "cut"))
    for label, methods, owned, xattr, xmeth, cut in tables["seam_rows"]:
        print("  %-8s %8d %6d %6d %6d %6d" % (label, methods, owned, xattr, xmeth, cut))

    print()
    print("########## RESULT lines ##########")
    for key in sorted(metrics):
        unit = "fraction" if key in FRACTION_METRICS else "count"
        print(f"RESULT {key}={metrics[key]} {unit}")
    thread_factor = 1.0
    if time.thread_time() > 0 and time.process_time() > 0:
        thread_factor = round(time.process_time() / max(time.thread_time(), 1e-9), 3)
    print(f"RESULT thread_factor={thread_factor} ratio")


# ---------------------------------------------------------------------------
# budget table: record and ratchet


def head_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def recorded_at_sha() -> str:
    """The commit whose tree these numbers describe, as a reader can check it.

    ``HEAD`` is the wrong answer and was the old one (#361). A re-record only
    ever happens on a branch, and a branch commit is rewritten by the next
    ``--amend`` and deleted by the squash-merge that lands it -- so the field
    named a SHA that resolves to nothing, and the value in the committed table
    was right only when somebody noticed and fixed it by hand.

    The merge base against the upstream default branch is the commit the
    measurement actually describes: it exists on ``main``, and it survives both
    the amend and the squash. ``HEAD`` remains the fallback for a run with no
    upstream configured, where it is the only thing there is.
    """
    for ref in ("origin/main", "main"):
        base = subprocess.run(
            ["git", "merge-base", "HEAD", ref], cwd=REPO_ROOT,
            capture_output=True, text=True,
        )
        if base.returncode == 0 and base.stdout.strip():
            return base.stdout.strip()
    return head_sha()


def recorded_at_unreachable(recorded: str) -> str | None:
    """Why ``recorded`` is not a commit a reader can resolve, or None if it is.

    Reported as a FAILURE, not a note, wherever the comparison can be made at
    all: ``recorded_at_sha`` returns ``git merge-base HEAD <upstream>``, which
    is an ancestor of that upstream by construction, so a value that is *not*
    an ancestor can only have come from the pre-#361 code (a branch SHA the
    squash deleted) or from a hand edit. There is no legitimate workflow that
    produces one, so refusing is safe.

    Returns None -- checks nothing -- when no upstream ref exists, which is the
    fresh-clone case ``recorded_at_sha``'s own HEAD fallback exists to serve.
    Failing there would break the case the fallback is for.
    """
    if not recorded or recorded == "unknown":
        return "recorded_at is missing"
    for ref in ("origin/main", "main"):
        if subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref], cwd=REPO_ROOT,
            capture_output=True, text=True,
        ).returncode != 0:
            continue
        ok = subprocess.run(
            ["git", "merge-base", "--is-ancestor", recorded, ref], cwd=REPO_ROOT,
            capture_output=True, text=True,
        ).returncode == 0
        if ok:
            return None
        return f"recorded_at {recorded[:12]} is not an ancestor of {ref}"
    return None  # no upstream to compare against; nothing to assert


def regression_rows(old: dict, new: dict) -> list[tuple[str, float, float]]:
    """Every metric a re-record would move in the WORSENING direction.

    The direction is uniformly ``new > old`` and needs no metric-specific
    knowledge: ``ratchet`` below compares all 22 counts the same way -- above
    the budget fails, below it is headroom -- so every one of them is
    lower-is-better. A per-metric direction table would be one more
    hand-maintained list to rot, which is the class of defect #364 and #304
    both turned out to be, so there deliberately is not one.

    ``FRACTION_METRICS`` are skipped, and that is not an oversight (it
    reverses #370's issue body). A tolerance metric passing inside its band
    has nothing to record, and failing outside it is a decision rather than
    bookkeeping; there is no third case. Re-recording one can therefore only
    ever loosen the band -- with ``cross_seam_fraction`` at budget 0.4289 and
    TOL 0.005 the ceiling is 0.4339, and recording the measured 0.4301 moves
    it to 0.4351 while buying nothing. So ``record_budgets`` does not rewrite
    them at all, which leaves this check nothing to check there.

    Keys absent from either side are not rows: a metric that appeared or
    disappeared is already a FAIL in ``ratchet`` ("measured but not in the
    budget table"), and it has no old and new to put side by side.
    """
    rows = []
    for key in sorted(set(old) & set(new)):
        if key == "recorded_at" or key in FRACTION_METRICS:
            continue
        if new[key] > old[key]:
            rows.append((key, old[key], new[key]))
    return rows


def record_budgets(result: dict, allow_regression: str | None = None) -> int:
    """Write the budget table, refusing a re-record that loosens any metric.

    ``--record`` used to rewrite every key from the working tree without ever
    reading the table it replaced, so it could not tell locking in a gain from
    laundering a regression, and the resulting diff could not tell the row you
    meant to change from the row that came along with it (#370: that happened
    twice on 2026-09-03, both caught by a human noticing).

    That is latent while ``--record`` is rare and standing the moment #350
    makes an improving PR re-record in the PR that earned it: the gate then
    prints the exact command, the author runs it, and a metric that worsened
    in the same diff is written silently with the gate's own authority behind
    it. So the refusal is the default and the reason goes in the COMMIT, where
    a squash-merge keeps it, rather than in a PR body that the history does
    not carry.
    """
    # Only the integration matters: a budget table describes its structure,
    # and this script itself being untracked is exactly the first-record
    # case, not a reason to warn.
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", "custom_components"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout.strip()
    if dirty:
        print("WARNING: the tree is dirty under custom_components/; the numbers")
        print("below describe the working tree, not commit %s." % head_sha()[:12])

    payload = dict(result["metrics"])
    previous: dict = {}
    if BUDGET_FILE.exists():
        previous = json.loads(BUDGET_FILE.read_text())

    # A tolerance metric is never re-recorded (see regression_rows): carry the
    # recorded value forward untouched. Correcting one is a deliberate edit of
    # its own, with its own reason, which is what makes it visible.
    carried = []
    for key in sorted(FRACTION_METRICS & set(previous) & set(payload)):
        if payload[key] != previous[key]:
            carried.append((key, previous[key], payload[key]))
        payload[key] = previous[key]

    rows = regression_rows(previous, payload)
    if rows:
        print()
        print("########## re-record would LOOSEN %d budget(s) ##########" % len(rows))
        print("  %-32s %12s %12s %10s" % ("metric", "recorded", "measured", "delta"))
        for key, was, now in rows:
            print("  %-32s %12s %12s %10s  WORSE (lower is better)"
                  % (key, was, now, f"{now - was:+}"))
        if allow_regression is None or not allow_regression.strip():
            print()
            print("REFUSING to record. A re-record that moves a metric the wrong way")
            print("is a concession, not housekeeping, and it must not ride along in")
            print("the same command that locks in an improvement (#370).")
            print("If the loosening is deliberate, say why:")
            print()
            print('  python tests/structure.py --record \\')
            print('      --allow-regression="<why this budget must grow>"')
            print()
            print("and put that same reason in the COMMIT message, not the PR body:")
            print("the squash-merge keeps the commit and discards the branch.")
            return 1
        print()
        print("ALLOWED: %s" % allow_regression.strip())
        print("Repeat this reason in the commit message -- the squash-merge keeps")
        print("the commit and discards the branch.")

    for key, kept, measured in carried:
        print()
        print("  keeping recorded %s = %s (tree measures %s): a tolerance metric"
              % (key, kept, measured))
        print("  is never re-recorded -- inside its band there is nothing to record,")
        print("  outside it a failure is a decision, and either way a re-record can")
        print("  only loosen the band. Correct it deliberately, on its own (#370).")

    payload["recorded_at"] = recorded_at_sha()
    BUDGET_FILE.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    print()
    print("########## budget table written to %s ##########" % BUDGET_FILE)
    for key in sorted(payload):
        was = previous.get(key)
        if was is not None and was != payload[key]:
            print(f"  {key} = {payload[key]}   (was {was})")
        else:
            print(f"  {key} = {payload[key]}")
    return 0


def ratchet(result: dict) -> int:
    metrics = result["metrics"]
    if not BUDGET_FILE.exists():
        print("no budget table at %s; run: python tests/structure.py --record"
              % BUDGET_FILE)
        return 1
    budgets = json.loads(BUDGET_FILE.read_text())
    if not result["tables"]["top_is_coordinator"]:
        print(f"FAIL {COORDINATOR_CLASS_NAME} is no longer the top attr-bag class;")
        print("  the coordinator_* budgets describe something else. Re-record deliberately.")
        return 1

    failures = 0
    print()
    print("########## ratchet vs %s (recorded_at %s) ##########"
          % (BUDGET_FILE.name, budgets.get("recorded_at", "?")[:12]))
    why = recorded_at_unreachable(budgets.get("recorded_at", ""))
    if why is not None:
        print(f"FAIL {why};")
        print("  the numbers cannot be traced to a tree anyone can check out.")
        print("  Re-record with tests/structure.py --record, which stamps the")
        print("  merge base -- a branch SHA does not survive the squash (#361).")
        failures += 1
    budget_keys = {k: v for k, v in budgets.items() if k != "recorded_at"}
    for key in sorted(set(budget_keys) | set(metrics)):
        if key not in budget_keys:
            print(f"FAIL {key}: measured but not in the budget table -- re-record")
            failures += 1
            continue
        if key not in metrics:
            print(f"FAIL {key}: in the budget table but never measured -- re-record")
            failures += 1
            continue
        budget, current = budget_keys[key], metrics[key]
        if key in FRACTION_METRICS:
            if current > budget + FRACTION_TOLERANCE:
                print(f"FAIL {key} {current:.4f} > {budget + FRACTION_TOLERANCE:.4f} "
                      f"(budget {budget}, +{current - budget:+.4f})")
                failures += 1
            elif current < budget - FRACTION_TOLERANCE:
                print(f"  headroom {key} {current:.4f} (budget {budget}, "
                      f"{current - budget:+.4f}; the next PR may re-record to lock it in)")
            else:
                print(f"  ok   {key} {current:.4f} <= {budget}")
        else:
            if current > budget:
                print(f"FAIL {key} {current} > {budget} (+{current - budget})")
                failures += 1
            elif current < budget:
                print(f"  headroom {key} {current} (budget {budget}, {current - budget:+d};"
                      " the next PR may re-record to lock it in)")
            else:
                print(f"  ok   {key} {current} <= {budget}")
    print()
    if failures:
        print(f"{failures} STRUCTURE BUDGET(S) BREACHED")
        print("A budget may only be re-recorded deliberately, on a clean tree,")
        print("with the reason in the PR body -- never to make a failure go away.")
        return 1
    print("STRUCTURE RATCHET PASSED")
    return 0


SELF_CHECK_SOURCE = '''
from .grid_fee import max_abs_component as gf_max, min_component
import package.submodule as sub

TABLE = {"row": "WANTED"}


def recurse(n):
    return recurse(n - 1)


def read(config, const):
    return config.get(getattr(const, f"CONF_{TABLE['row']}"))
'''


AUDIT_SELF_CHECK_CONST = 'CONF_PROVEN: Final = "proven"\n'
AUDIT_SELF_CHECK_PROOF = (
    'TABLE = {"row": "PROVEN"}\n'
    'def read(config, const):\n'
    '    return config.get(getattr(const, f"CONF_{TABLE[\'row\']}"))\n'
)
AUDIT_SELF_CHECK_ENTRY = {
    ("const.py", "CONF_PROVEN"): ("thermal_model.py", "PROVEN", "CONF_", "self-check"),
}


def audit_self_check() -> tuple[tuple[str, bool], ...]:
    """Pin every way a ``DYNAMIC_REFERENCES`` entry is allowed to rot (#364).

    An allowlist is only as honest as the re-check behind it, and a check has
    nothing else to catch it when it goes: drop the "is the bare string still
    there" clause and the four constants stay exempt for ever, silently, which
    is the failure mode the list must not have. So the audit is driven here
    against a two-module tree of our own, once per rot mode, and each
    assertion is one of the clauses.
    """
    const_rel = str((PACKAGE_DIR / "const.py").relative_to(REPO_ROOT))

    def audit(const_src: str | None, proof_src: str, referenced: set[str]):
        trees = [(PACKAGE_DIR / "thermal_model.py", ast.parse(proof_src))]
        defs: dict[tuple[str, str], int] = {}
        if const_src is not None:
            trees.insert(0, (PACKAGE_DIR / "const.py", ast.parse(const_src)))
            defs[(const_rel, "CONF_PROVEN")] = 1
        return dynamic_reference_audit(
            trees, defs, referenced, entries=AUDIT_SELF_CHECK_ENTRY
        )

    healthy = audit(AUDIT_SELF_CHECK_CONST, AUDIT_SELF_CHECK_PROOF, set())
    no_literal = audit(AUDIT_SELF_CHECK_CONST, AUDIT_SELF_CHECK_PROOF.replace(
        '"PROVEN"', '"SOMETHING_ELSE"'), set())
    no_lookup = audit(AUDIT_SELF_CHECK_CONST, AUDIT_SELF_CHECK_PROOF.replace(
        'getattr(const, f"CONF_{TABLE[\'row\']}")', "const.CONF_OTHER"), set())
    no_symbol = audit(None, AUDIT_SELF_CHECK_PROOF, set())
    now_static = audit(AUDIT_SELF_CHECK_CONST, AUDIT_SELF_CHECK_PROOF, {"CONF_PROVEN"})

    return (
        ("a proven dynamic reference exempts its symbol, with no complaint",
         healthy == ({(const_rel, "CONF_PROVEN")}, [])),
        ("the bare string going away is caught, and the symbol counts again",
         not no_literal[0] and len(no_literal[1]) == 1),
        ("the getattr lookup going away is caught",
         not no_lookup[0] and len(no_lookup[1]) == 1),
        ("an entry whose symbol no longer exists is caught",
         not no_symbol[0] and len(no_symbol[1]) == 1),
        ("an entry the tree no longer needs is caught",
         not now_static[0] and len(now_static[1]) == 1),
    )


def self_check() -> int:
    """Pin ``module_references``'s rules on a source of our own (#364).

    The tree's own aliased imports are what the alias rule was written for, but
    the tree moves: delete the last aliased import from the integration and
    that rule would be exercised by nothing, free to regress silently until the
    next symbol it hides. These assertions are the rules themselves,
    independent of what ``custom_components/`` happens to contain today.

    The last one is the boundary this fix is careful about: a name a
    ``getattr`` assembles at runtime is NOT a static reference and must not
    become one here. Reaching those four constants is
    ``DYNAMIC_REFERENCES``'s job, at four written-down addresses, so that no
    other symbol's liveness is redefined on their account.
    """
    refs = module_references(ast.parse(SELF_CHECK_SOURCE))
    failures = [
        message
        for message, ok in (
            ("an aliased import records the ORIGINAL name", "max_abs_component" in refs),
            ("an aliased import also records the alias", "gf_max" in refs),
            ("an unaliased import still records its name", "min_component" in refs),
            ("a dotted aliased import records both halves",
             "submodule" in refs and "sub" in refs),
            ("a function calling itself is recursion, not a reference",
             "recurse" not in refs),
            ('a getattr(x, f"CONF_{..}") name is NOT a static reference',
             "CONF_WANTED" not in refs),
            *audit_self_check(),
        )
        if not ok
    ]
    print("########## reference-rule self-check ##########")
    for message in failures:
        print(f"FAIL  {message}")
    if failures:
        print(f"{len(failures)} REFERENCE RULE(S) BROKEN -- "
              "dead_top_level_symbols cannot be trusted")
        return 1
    print("  ok   11 reference rules hold")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--record",
        action="store_true",
        help="write the measured table to tests/structure_budgets.json",
    )
    parser.add_argument(
        "--allow-regression",
        metavar="REASON",
        default=None,
        help="record even though a metric moves the wrong way, for this stated "
             "reason -- which belongs in the commit message too (#370)",
    )
    args = parser.parse_args()

    if self_check():
        return 1

    result = measure()
    print_report(result)
    problems = result["tables"]["dynamic_problems"]
    if problems:
        print()
        print(f"{len(problems)} DYNAMIC-REFERENCE ALLOWLIST ENTR(IES) NO LONGER HOLD")
        print("Each line above says what changed. An entry whose proof is gone")
        print("means the symbol is dead now -- delete the symbol and the entry,")
        print("never the check. (#364)")
        return 1
    if args.record:
        return record_budgets(result, allow_regression=args.allow_regression)
    if args.allow_regression is not None:
        print("--allow-regression only means anything with --record")
        return 1
    return ratchet(result)


if __name__ == "__main__":
    sys.exit(main())
