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
  duplication_blocks          maximal runs of >= 30 consecutive normalized
                              lines (whitespace/comments stripped) that appear
                              in more than one function, nested defs excluded
                              from their parents so containment is not
                              reported as duplication
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
                              those by convention, not by import)
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
                                          SHA recorded in ``recorded_at``)

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
DUP_BLOCK_LINES = 30
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

        # Every name anyone reads, plus every name any import binds: an
        # import is a reference even when the name is then used only as an
        # attribute of the module. Attribute names count too -- coarse, but
        # this is a screen for accidental deadness, not a linker. A load of
        # name N from inside the body of a top-level function also called N
        # is recursion, not a reference from elsewhere, so it does not count.
        own_fn_ranges: dict[str, tuple[int, int]] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                own_fn_ranges[node.name] = (node.lineno, node.end_lineno)

        def note_reference(name: str, lineno: int) -> None:
            span = own_fn_ranges.get(name)
            if span and span[0] <= lineno <= span[1]:
                return  # the symbol's own body: recursion, not a reference
            referenced_names.add(name)

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                note_reference(node.id, node.lineno)
            elif isinstance(node, ast.Attribute):
                note_reference(node.attr, node.lineno)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    note_reference(alias.asname or alias.name.split(".")[-1], node.lineno)

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

        # Duplication: normalized 30-line windows shared by more than one
        # function. Normalization strips whitespace and comment-only lines;
        # nested def/class spans are dropped from the parent so a handler
        # defined inside a registrar is not "a copy" of its own container.
        windows: dict[str, list[tuple[tuple, int]]] = defaultdict(list)
        for fn in all_functions(tree):
            excluded = nested_spans(fn)
            normalized: list[tuple[int, str]] = []
            segment = 0
            for lineno in range(fn.lineno, fn.end_lineno + 1):
                if any(a <= lineno <= b for a, b in excluded):
                    segment += 1
                    continue
                stripped = src_lines[lineno - 1].strip()
                if not stripped or stripped.startswith("#"):
                    continue
                normalized.append((segment, stripped))
            fid = (rel, fn.name, fn.lineno)
            for i in range(len(normalized) - DUP_BLOCK_LINES + 1):
                if normalized[i][0] != normalized[i + DUP_BLOCK_LINES - 1][0]:
                    continue  # the window spans an excluded (nested) gap
                digest = hashlib.sha1(
                    "\n".join(line for _, line in normalized[i : i + DUP_BLOCK_LINES]).encode()
                ).hexdigest()
                windows[digest].append((fid, i))
        covered: dict[tuple, list[tuple[int, int]]] = defaultdict(list)
        for digest, sites in windows.items():
            owners = {fid for fid, _ in sites}
            if len(owners) < 2:
                continue
            for fid, start in sites:
                covered[fid].append((start, start + DUP_BLOCK_LINES))
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
                duplication.append((fid[0], fid[1], fid[2], f"norm {a}-{b - 1}", b - a))

    # -- dead top-level symbols --------------------------------------------
    for (rel, name), lineno in sorted(top_level_defs.items()):
        if name in HA_CONVENTION_NAMES:
            continue
        if name in referenced_names:
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


def record_budgets(result: dict) -> int:
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
    payload["recorded_at"] = recorded_at_sha()
    BUDGET_FILE.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    print()
    print("########## budget table written to %s ##########" % BUDGET_FILE)
    for key in sorted(payload):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--record",
        action="store_true",
        help="write the measured table to tests/structure_budgets.json",
    )
    args = parser.parse_args()

    result = measure()
    print_report(result)
    if args.record:
        return record_budgets(result)
    return ratchet(result)


if __name__ == "__main__":
    sys.exit(main())
