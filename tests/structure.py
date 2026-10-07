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

  methods_over_200 /          functions (methods included, nested included)
  methods_over_150            whose span is more than 200 / 150 lines
  max_class_loc               the largest class span in the integration --
                              the coordinator's while it is the largest
                              class (coordinator_loc, equal to it at every
                              measured point, merged in by #1738)
  max_method_loc              the largest function span in the integration --
                              the WORST offender, not a count of offenders
                              (#374). Reads 0 when nothing exceeds
                              MONSTER_LIMITS[1], because the metric is the top
                              of the ``monsters`` table and that table starts
                              at 150; a re-record to 0 then makes the next
                              function over 150 fail at once, so the
                              truncation tightens the gate and cannot hide a
                              149-line method behind it
  max_cc                      the largest cyclomatic complexity in the
                              integration, same shape, off ``cc_scores``

  Why there is a max_* and deliberately NO sum_cc (#374). The four threshold
  counts above (methods_over_150/200, functions_cc_over_15/25) price a
  function CROSSING a line and nothing after it: once a function is counted
  it can grow without bound and no key in the budget table moves. That makes
  the worst function in the tree the cheapest place in the codebase to put new
  complexity, which is the agentic-complexity vector stated literally. The
  worked example below is AS OF #374 (841fe0f^) and every number in it is that
  snapshot's, not today's: with methods_over_200 at 14 and functions_cc_over_25
  at 11, ``optimize`` could go 540 -> 1,080 lines and CC 87 -> 174 with all 22
  budgets unmoved.
  ``max_class_loc`` already did exactly this job for the one shape family that
  had it.

  ``sum_cc`` is the obvious next proposal and it is REFUSED, for a reason that
  belongs here rather than only in #374. Cyclomatic complexity is 1 + decision
  points PER FUNCTION, so splitting a CC-87 function into a parent plus four
  CC-20 helpers yields about 100 where there was 87 -- five function bodies
  each paying their own +1, and the parent still branching to dispatch. A sum
  ratchet would therefore FAIL the exact refactor #224 exists to perform, and
  a metric that punishes the decomposition programme is worse than no metric.
  The maxima have the opposite sign and that is why they are worth having
  while #224 is in flight: splitting ``optimize`` drives max_cc 87 -> ~43 and
  max_method_loc 540 -> 483, so the ratchet rewards the programme and then
  asks for the gain to be recorded.

  Accepted and stated: a max metric bounds the worst offender, not the second.
  The RUNNER-UP can still grow to the leader's value invisibly
  (simulate_trajectory_batch CC 43 -> 86, _optimize_with_dhw 483 -> 539 LOC),
  gaps of 44 and 57 today and shrinking as #224 lands. Pretending otherwise
  would make this the same kind of half-blind gate it exists to fix.
  coordinator_attrs /         distinct attributes stored on the coordinator,
  coordinator_multiassigned   and those stored by more than one function --
                              wherever the store is: in its methods, in a
                              helper, or in another module holding it, which
                              the census used to drop (#1738). The
                              coordinator is found by role, not by name
                              (``CoordinatorRoles``)
  duplication_copies          clone classes of functions sharing a window of
                              DUP_WINDOW_STATEMENTS statements of one block,
                              at least DUP_MIN_NODES AST nodes, normalized
                              (a function's own names renamed in order of use,
                              ``mod.X`` read as ``X``, a string a placeholder)
                              and compared PACKAGE-wide; each class counts its
                              members past the first -- the copies that would
                              go if the logic were shared (#1738 arm a)
  functions_cc_over_25 /      cyclomatic complexity 1 + decision points
  functions_cc_over_15        (if/elif, for, while, ternary, except, assert,
                              boolean operator terms beyond the first, each
                              comprehension clause and its ifs, each match
                              case), counted over the whole function span
                              including nested defs
  const_modules_over_50       modules importing more than 50 names from
                              ``.const``
  import_cycle_modules        modules in a cycle of the package's import
                              graph, function-scope imports in and imports
                              under ``if TYPE_CHECKING:`` out (#1738)
  dead_top_level_symbols      top-level defs/classes/assignments no load in
                              the integration resolves to (dunder, HA entry
                              points, HA convention constants and
                              ConfigFlow/OptionsFlow subclasses excluded --
                              Home Assistant finds those by convention, not by
                              import). A load resolves through the module's
                              own bindings and its imports, not by bare name
                              (``bound_references``, #1538), and ``from .m
                              import *`` binds m's public names (#1738); the
                              four constants a runtime ``getattr`` assembles
                              are exempted by name, with their proof
                              re-checked on every run (``DYNAMIC_REFERENCES``)
  dead_methods                class members -- methods AND properties -- no
                              live attribute load reaches (#1395, #1686,
                              D7-s3-02). The receiver decides whose member a
                              load reaches: ``self.n`` in class C reaches C's
                              in-package family only, an untyped ``x.n`` every
                              class's ``n``, and a bare name ``n`` is a local
                              that reaches none. Live is REACHABILITY: a load
                              counts from module-level code, a module-level
                              function, a dunder, a Home Assistant convention
                              member (``HA_CONVENTION_METHODS``) or a live
                              member, so a member reached only from its own
                              body, or from dead members, is dead. The live
                              members an untyped load of a name two classes
                              define keeps alive are printed: the shape this
                              cannot measure, on the record
  coordinator_private_reach   ``<coordinator>._x`` reads, plus
                              PRIVATE_WRITE_WEIGHT x each write (a store, a
                              delete, an in-place mutation of what the slot
                              holds), anywhere outside the coordinator's
                              methods and helpers (#1738 arm b)
  seam_cut_total              the sum over the seams (dhw / learning / fetch /
                              grid / views; a unit's seam is its entry in
                              ``tests/seam_map.json``, #1539) of what an
                              extraction of the seam would have to make
                              explicit: attribute references crossing the
                              ownership boundary in either direction (an
                              attribute is owned by a seam when one of its
                              units stores it), plus calls between units
                              crossing it. The units are the coordinator's
                              methods and ``coordinator.py``'s module-level
                              helpers handed the coordinator, priced alike
                              (#1686): a body moved into ``_helper(self, ...)``
                              used to leave the cut. The per-seam rows print
                              as evidence

  Retired by #1738 (its pre-study's decision R3-2, where each one's
  perturbation evidence is recorded): classes_over_300,
  attrbag_classes_over_30, internal_call_edges and coordinator_methods;
  coordinator_loc, merged into max_class_loc; cross_seam_edges and the five
  cut_<seam> rows, into seam_cut_total; duplication_blocks, replaced by
  duplication_copies; and local_imports, replaced by import_cycle_modules.

Run:

    python tests/structure.py             ratchet: metrics vs budgets, exit 1
                                          on any worsening, exit 2 on any
                                          improvement that is not yet recorded
                                          (#350 / #808). Those are not the
                                          same report.
    python tests/structure.py --record    recompute and WRITE the budget table
                                          (run this on a clean tree, at the
                                          SHA recorded in ``recorded_at``).
                                          REFUSES if any metric would move the
                                          wrong way; every metric is

    python tests/structure.py --record --allow-regression="<reason>"
                                          record anyway, for a stated reason
                                          that belongs in the COMMIT message.
                                          Raising a budget to buy a genuine new
                                          production feature is legitimate, but
                                          needs the repository OWNER's explicit
                                          confirmation before the push

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
import math  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = REPO_ROOT / "custom_components" / "heatpump_optimizer"
BUDGET_FILE = REPO_ROOT / "tests" / "structure_budgets.json"

# The class the whole program (#193) is about. The coordinator_* rows and the
# seam cut price it wherever its role reaches (``CoordinatorRoles``).
COORDINATOR_CLASS_NAME = "HeatPumpOptimizerCoordinator"

GOD_CLASS_LOC_LIMIT = 300
MONSTER_LIMITS = (200, 150)
# The duplication window (#369, #1738): DUP_WINDOW_STATEMENTS statements of one
# block, carrying at least DUP_MIN_NODES AST nodes, compared after
# normalization across the whole package. It replaced DUP_BLOCK_LINES' text
# windows of 10 normalized lines, which a re-wrap moved (8 of their 14 rows
# were parameter lists) and which saw only copies inside one module, so a
# copy placed in another module cost nothing.
DUP_WINDOW_STATEMENTS = 2
DUP_MIN_NODES = 30
CC_LIMITS = (25, 15)
CONST_FANOUT_LIMIT = 50

# The seam partition of #193's plan of record. A coordinator method's seam is
# its entry in SEAM_MAP_FILE, never its name (#1539): bucketing by name let a
# pure rename move cross_seam_edges. A method the map does not name is refused,
# so a new or renamed method is assigned to a seam in a diff a reviewer sees.
SEAM_LABELS = ("dhw", "learning", "fetch", "grid", "views")
SEAM_MAP_FILE = REPO_ROOT / "tests" / "seam_map.json"

# The SEED rule only (``--seed-seam-map``), no longer the measurement: a method
# belongs to the FIRST seam whose regex matches its name, everything else is
# core -- a method named _fetch_dhw_prices is a dhw method, not a fetch one.
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
    # Home Assistant loads ``repairs.py`` by convention and looks this up
    # when the user clicks Fix on an issue (#408).
    "async_create_fix_flow",
    # Module-level constants the HA framework reads off platform modules.
    "CONFIG_SCHEMA",
    "PARALLEL_UPDATES",
    "PLATFORMS",
}

# The method-shaped twin of ``HA_CONVENTION_NAMES`` (#1395). Home Assistant
# imports the module, instantiates the class (an entity, the coordinator, a
# config-flow handler) and looks the name up on the INSTANCE, so no module in
# the package ever writes ``self.native_value()`` or ``x.is_on()`` and the
# method screen would call every one of them dead. Each entry says which
# convention it is; ``async_step_*`` is a family, matched by prefix below.
HA_CONVENTION_METHODS = {
    # DataUpdateCoordinator's own template method.
    "_async_update_data",
    # Store's migration hook: its _async_load_data calls it on a version
    # mismatch (QuarantiningStore's default, #1740).
    "_async_migrate_func",
    # Entity platform APIs, called by HA on the entity instance.
    "async_press",
    "async_set_hvac_mode",
    "async_set_preset_mode",
    "async_set_temperature",
    "async_set_value",
    "async_turn_on",
    "async_turn_off",
    "is_on",
    "current_temperature",
    "hvac_action",
    # ClimateEntity state HA reads off the instance (D7-s3-02: the member
    # census now counts properties, so these two must be named).
    "hvac_mode",
    "preset_mode",
    # Entity properties the platform reads as attributes.
    "native_value",
    "extra_state_attributes",
    "native_unit_of_measurement",
    "device_info",
    "entity_registry_enabled_default",
    # ConfigFlow / OptionsFlow: the flow engine dispatches on the step name.
    "async_get_options_flow",
}
HA_CONVENTION_METHOD_PREFIXES = ("async_step_",)


def is_ha_convention_method(name: str) -> bool:
    """Whether HA reaches ``name`` on an instance by convention, not import."""
    return (
        name in HA_CONVENTION_METHODS
        or name.startswith(HA_CONVENTION_METHOD_PREFIXES)
    )


def is_property_getter(node: ast.AST) -> bool:
    """Whether a class-body function is a ``@property`` (or a sibling accessor).

    No longer a boundary of the member census: a property is a member like any
    other (D7-s3-02). Kept as the predicate the round-9 D7 finder harnesses
    patch (``dev/audit/rounds/round9/D7/s3``), so they still run at both ends.
    """
    return any(
        (isinstance(d, ast.Name) and d.id == "property")
        or (isinstance(d, ast.Attribute) and d.attr in ("setter", "getter", "deleter"))
        for d in getattr(node, "decorator_list", [])
    )


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

# Every metric is a count that only moves down. There used to be two more
# categories here -- FRACTION_METRICS, compared inside a +-0.005 band, and
# NEVER_RERECORDED, carried forward untouched by --record -- with one member
# between them, cross_seam_fraction. Both retired on 2026-09-10 with that
# metric: a ratio of cross-seam call edges to all call edges falls when a
# class tangles and RISES when a cohesive part leaves it (the legionella guard
# removes 17 edges of which 6 cross a seam), so it refused the one move it was
# built to price. cross_seam_edges, the ratio's own numerator, ratchets like
# every other row and falls on that move. The seam table still prints the
# ratio as evidence; nothing budgets it.


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
    """Every name this module references, for the dead-METHOD screen.

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


def top_level_names(tree: ast.Module) -> set[str]:
    """The names a module's own top-level statements bind."""
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        for target in getattr(node, "targets", [getattr(node, "target", None)]):
            if isinstance(target, ast.Name):
                names.add(target.id)
    return names


def bound_references(trees: list[tuple[Path, ast.Module]]) -> set[tuple[str, str]]:
    """``(rel, name)`` of every top-level symbol a load resolves to (#1538).

    The dead-symbol screen used to ask whether a symbol's NAME was read
    anywhere (``module_references``), so ``grid_fee.is_valid_spec`` was live
    because config_flow reads ``dhw_schedule``'s function of that name, and ten
    module ``_LOGGER``s were live because other modules read theirs. A load now
    resolves the way Python resolves it:

    1. ``N`` in the defining module, outside ``N``'s own body (recursion);
    2. ``A`` wherever ``from .m import N as A`` bound it, through re-exports,
       and ``N`` wherever ``from .m import *`` did (#1738);
    3. ``m.N`` where ``m`` is bound to the defining module;
    4. ``x.N`` where ``x`` is neither a module binding nor ``self``/``cls``
       reaches every top-level ``N``: the AST cannot type it (the module
       ``_async_lazy`` returns, say), and a live symbol reported dead would be
       deleted. The one name-based arm left; a binding never takes it.
    """
    mods = {p.relative_to(PACKAGE_DIR).as_posix()[:-3].replace("/", "."): (p, t)
            for p, t in trees}
    tops = {(m, n) for m, (_p, t) in mods.items() for n in top_level_names(t)}
    sym_bind, mod_bind = import_bindings(
        {m: (str(p), t) for m, (p, t) in mods.items()})

    def resolve(mod: str, name: str) -> tuple[str, str]:
        seen = set()
        while (mod, name) not in tops and (mod, name) in sym_bind and (mod, name) not in seen:
            seen.add((mod, name))
            mod, name = sym_bind[(mod, name)]
        return mod, name

    found: set[tuple[str, str]] = set()
    untyped: set[str] = set()
    for mod, (_p, tree) in mods.items():
        own = {n.name: (n.lineno, n.end_lineno) for n in tree.body
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                span = own.get(node.id)
                if not (span and span[0] <= node.lineno <= span[1]):
                    found.add(resolve(mod, node.id))
            elif isinstance(node, ast.Attribute):
                base_name = node.value.id if isinstance(node.value, ast.Name) else None
                if (mod, base_name) in mod_bind:
                    found.add(resolve(mod_bind[(mod, base_name)], node.attr))
                elif base_name not in ("self", "cls"):
                    untyped.add(node.attr)
    found |= {key for key in tops if key[1] in untyped}
    return {(str(mods[m][0].relative_to(REPO_ROOT)), n) for m, n in found if m in mods}


def is_dead_symbol(key: tuple[str, str], bound: set[tuple[str, str]],
                   exempt: set[tuple[str, str]]) -> bool:
    """No load resolves to ``(rel, name)``, and no convention or proof exempts it."""
    return key[1] not in HA_CONVENTION_NAMES and key not in bound and key not in exempt


def dynamic_reference_audit(
    trees: list[tuple[Path, ast.Module]],
    top_level_defs: dict[tuple[str, str], int],
    referenced: set[tuple[str, str]],
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
        if (rel, name) in referenced:
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


def _is_docstring(stmt: ast.AST) -> bool:
    return isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) \
        and isinstance(stmt.value.value, str)


def _module_aliases(tree: ast.Module) -> set[str]:
    """Names a module binds to whole modules (``import x``, ``from . import m``)."""
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module is None:
            out |= {a.asname or a.name for a in n.names}
    return out


def _local_names(fn: ast.AST) -> set[str]:
    names = set(fn_params(fn))
    a = fn.args  # type: ignore[attr-defined]
    names |= {x.arg for x in (a.vararg, a.kwarg) if x}
    names |= {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    return names


def normalized_window(stmts: list[ast.stmt], local: set[str], modalias: set[str]) -> str:
    """A statement window as a string two copies of one logic share.

    The AST, not the text, so a re-wrap or a comment moves nothing (#1738's
    fourth defect: 8 of the 14 rows the line windows found were parameter
    lists, and an AST-identical re-wrap read -2). A function's own names are
    renamed in order of first use, ``mod.X`` for an imported module reads as
    ``X`` (a ``const.X`` spelling is the same logic as ``X``), and a string
    constant is a placeholder.
    """
    mapping: dict[str, str] = {}

    class Normalize(ast.NodeTransformer):
        def visit_Attribute(self, n):
            self.generic_visit(n)
            if isinstance(n.value, ast.Name) and n.value.id in modalias and n.value.id not in local:
                return ast.copy_location(ast.Name(id=n.attr, ctx=n.ctx), n)
            return n

        def visit_Name(self, n):
            if n.id in local:
                n.id = mapping.setdefault(n.id, f"v{len(mapping)}")
            return n

        def visit_Constant(self, n):
            if isinstance(n.value, str):
                n.value = "S"
            return n

    return "".join(
        ast.dump(Normalize().visit(ast.parse(ast.unparse(s)).body[0])) for s in stmts)


def duplicate_clones(trees: list[tuple[Path, ast.Module]],
                     window: int = DUP_WINDOW_STATEMENTS,
                     min_nodes: int = DUP_MIN_NODES) -> list[list[tuple[str, str, int]]]:
    """Clone classes: functions sharing a normalized statement window, package-wide.

    A window is ``window`` consecutive statements of one block (a body, an
    ``else``, a handler) carrying at least ``min_nodes`` AST nodes, nested
    defs excluded. Two functions sharing any window are joined, IN ANY MODULE
    (#1738 arm a: a copy placed in another module used to move nothing, the
    same copy in its own module moved it). Each connected group of functions
    is one clone class; ``duplication_copies`` counts every member past the
    first, the copies that would go if the logic were shared -- a count of
    copies, not of pairs, so a third copy costs one more, not two.
    """
    windows: dict[str, set[tuple[str, str, int]]] = defaultdict(set)
    for path, tree in trees:
        rel = str(path.relative_to(REPO_ROOT))
        modalias = _module_aliases(tree)
        for fn in all_functions(tree):
            local = _local_names(fn)
            owner = (rel, fn.name, fn.lineno)
            stack = [fn]
            while stack:
                node = stack.pop()
                for child in ast.iter_child_nodes(node):
                    if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                              ast.Lambda, ast.ClassDef)):
                        stack.append(child)
                blocks = [getattr(node, f) for f in ("body", "orelse", "finalbody")
                          if isinstance(getattr(node, f, None), list) and getattr(node, f)
                          and isinstance(getattr(node, f)[0], ast.stmt)]
                blocks += [h.body for h in getattr(node, "handlers", []) or []]
                for block in blocks:
                    block = [s for s in block if not _is_docstring(s)]
                    for i in range(len(block) - window + 1):
                        stmts = block[i:i + window]
                        if any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                               for s in stmts):
                            continue
                        if sum(1 for s in stmts for _ in ast.walk(s)) < min_nodes:
                            continue
                        digest = hashlib.sha1(
                            normalized_window(stmts, local, modalias).encode()).hexdigest()
                        windows[digest].add(owner)
    parent: dict[tuple[str, str, int], tuple[str, str, int]] = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for owners in windows.values():
        first, *rest = sorted(owners)
        for other in rest:
            parent[find(other)] = find(first)
    groups: dict[tuple[str, str, int], list[tuple[str, str, int]]] = defaultdict(list)
    for member in parent:
        groups[find(member)].append(member)
    return sorted(sorted(g) for g in groups.values() if len(g) > 1)


def import_cycle_modules(trees: list[tuple[Path, ast.Module]]) -> list[list[str]]:
    """Every non-trivial strongly connected group of the package's import graph.

    Function-scope imports are edges -- a deferred import is still a
    dependency, and a cycle made of one was the pre-study's missed case B6b
    -- and imports under ``if TYPE_CHECKING:`` are not, since they never
    run. It replaces ``local_imports``, which counted the deferral and could
    not see the cycle (#1738's eleventh defect: the package's first
    module-level cycle read 0 on every row).
    """
    mods = {p.relative_to(PACKAGE_DIR).as_posix()[:-3].replace("/", "."): t for p, t in trees}
    graph: dict[str, set[str]] = defaultdict(set)
    for mod, tree in mods.items():
        skip = type_checking_ids(tree)
        package = mod.split(".")[:-1]
        for n in ast.walk(tree):
            if id(n) in skip or not isinstance(n, ast.ImportFrom) or n.level == 0:
                continue
            base = package[:len(package) - n.level + 1]
            if n.module:
                src = ".".join(base + [n.module])
                graph[mod].add(src if src in mods else src.rsplit(".", 1)[0])
            else:
                graph[mod] |= {".".join(base + [a.name]) for a in n.names}
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    out: list[list[str]] = []

    def connect(v: str) -> None:
        index[v] = low[v] = len(index)
        stack.append(v)
        on_stack.add(v)
        for w in sorted(graph[v]):
            if w not in mods or w == v:
                continue
            if w not in index:
                connect(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            group = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                group.append(w)
                if w == v:
                    break
            if len(group) > 1:
                out.append(sorted(group))

    for v in sorted(mods):
        if v not in index:
            connect(v)
    return sorted(out)


def table_maxima(monsters: list, cc_scores: list) -> tuple[int, int]:
    """``(max_method_loc, max_cc)`` off the two tables ``measure`` already sorts.

    A function of its arguments rather than three characters inline in the
    metrics dict, so the rule can be driven from ``tests/features.py`` without
    calling ``measure()``, which reads every module under
    ``custom_components/`` and nothing outside it.

    That bought the smaller of two savings, and they are worth keeping apart.
    ``tests/features.py``'s measured closure already lists most of the
    integration, so recording ``measure()``'s reads would have added only the
    HA platform modules missing from it -- which that script does not test and
    would have opened purely because ``measure()`` walks the directory.
    Spurious, and cheap.

    The expensive dependency was never ``measure()``'s: it does not open the
    budget table at all, only ``record_budgets`` and ``ratchet`` do. It came
    from a separate check that read ``tests/structure_budgets.json`` directly
    to confirm both new keys had been recorded, and that check is gone,
    replaced by AST checks that read this module's source instead. That one
    mattered because a closure entry on the budget table would put the fast
    lane in scope for EVERY future re-record -- precisely the traffic #350
    above now makes mandatory -- so it would have taxed, for ever, the one
    operation this file just started demanding. Credit where it is due:
    ``table_maxima`` removes the directory walk, the AST checks remove the
    budget-table read.

    ``default=0`` is the empty-table case and it is safe in the direction that
    matters (#374). ``monsters`` starts at ``MONSTER_LIMITS[1]`` and
    ``cc_scores`` at ``CC_LIMITS[1]``, so a tree with nothing over those
    thresholds reports 0 rather than its real 149-line worst method. A budget
    re-recorded to 0 then fails the moment any function crosses 150 again, so
    the truncation TIGHTENS the gate; it cannot hide a 149-line method behind a
    budget of 540.
    """
    return (
        max((loc for loc, *_ in monsters), default=0),
        max((cc for cc, *_ in cc_scores), default=0),
    )


# The coordinator reaches its own state by three spellings that all resolve to
# the same object -- ``self.X``; ``getattr(self, "_ctx", self).X``, #500's
# migration idiom, whose fallback IS ``self``; and ``self._ctx.X`` -- and any
# of them may be bound to a local first. An extraction has to make every one
# of them explicit, so the cut has to price every one of them (#510). A helper
# handed the coordinator spells ``self`` as its parameter (#1686), so the root
# is a set of names, ``{"self"}`` for a method.
STATE_CONTEXT_ATTR = "_ctx"
SELF_ROOT = frozenset({"self"})


def _is_context_getattr(node: ast.AST, roots: frozenset[str] = SELF_ROOT) -> bool:
    """``getattr(self, "_ctx", self)`` -- self-rooted by its own default."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "getattr"
        and not node.keywords
        and len(node.args) == 3
        and all(
            isinstance(arg, ast.Name) and arg.id in roots
            for arg in (node.args[0], node.args[2])
        )
        and isinstance(node.args[1], ast.Constant)
        and node.args[1].value == STATE_CONTEXT_ATTR
    )


def _is_context_hop(node: ast.AST, roots: frozenset[str] = SELF_ROOT) -> bool:
    """A ``self._ctx`` read: the state ``self`` reaches, one hop out."""
    return (
        isinstance(node, ast.Attribute)
        and node.attr == STATE_CONTEXT_ATTR
        and isinstance(node.value, ast.Name)
        and node.value.id in roots
        and isinstance(node.ctx, ast.Load)
    )


def is_state_root(node: ast.AST, aliases: frozenset[str],
                  roots: frozenset[str] = SELF_ROOT) -> bool:
    """Does ``node`` evaluate to the coordinator's own state?"""
    if isinstance(node, ast.Name):
        return node.id in roots or node.id in aliases
    return _is_context_getattr(node, roots) or _is_context_hop(node, roots)


def state_root_bindings(fn: ast.AST, roots: frozenset[str] = SELF_ROOT,
                        ) -> tuple[frozenset[str], frozenset[int]]:
    """The locals this method binds to its own state, and the hops to discount.

    A ``self._ctx`` that something is read THROUGH is a hop, not a reference.
    Charging the hop rather than what lies beyond it costs the same in total
    but books every read against ``_ctx``, whose owner is core, so a seam pays
    for reaching state it owns itself. A ``self._ctx`` nothing is read through
    -- handed to a helper, returned -- stays a reference, or passing the
    context out would erase its reads for free: the ``_helper(self, ...)``
    move W4-G4 already refused, for the same reason.
    """
    aliases: set[str] = set()
    hops: set[int] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Attribute) and _is_context_hop(node.value, roots):
            hops.add(id(node.value))
        elif isinstance(node, ast.Assign) and is_state_root(node.value, frozenset(), roots):
            aliases.update(t.id for t in node.targets if isinstance(t, ast.Name))
            hops.add(id(node.value))
        elif isinstance(node, ast.NamedExpr) and is_state_root(node.value, frozenset(), roots):
            aliases.add(node.target.id)
            hops.add(id(node.value))
    return frozenset(aliases), frozenset(hops)


class SeamMapError(ValueError):
    """The seam map and the class it partitions disagree (#1539)."""


def regex_seam(method_name: str) -> str:
    """The seam ``SEAM_REGEXES`` gives a name: the seed rule, not the metric."""
    for label, regex in SEAM_REGEXES:
        if regex.search(method_name):
            return label
    return "core"


def load_seam_map() -> dict[str, str]:
    if not SEAM_MAP_FILE.exists():
        raise SeamMapError(f"no {SEAM_MAP_FILE.name}: seed it with --seed-seam-map")
    return json.loads(SEAM_MAP_FILE.read_text())["seams"]


def seed_seam_map() -> int:
    """Rewrite SEAM_MAP_FILE from ``regex_seam`` over every coordinator unit.

    The introduction's null control and the re-seed after a coordinator merge:
    each method and each ``coordinator.<helper>`` (#1686) gets the seam its
    name gives. Every later change to the map is a hand edit, a seam decision
    a reviewer reads.
    """
    pkg = Package(module_trees())
    cls = pkg.classes[(COORDINATOR_MODULE, COORDINATOR_CLASS_NAME)]
    seams = {m.name: regex_seam(m.name) for m in cls.body
             if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
    seams.update({key: regex_seam(key.split(".", 1)[1])
                  for key in CoordinatorRoles(pkg).coordinator_helpers()})
    SEAM_MAP_FILE.write_text(json.dumps(
        {"_comment": "Each coordinator method's seam for tests/structure.py (#1539),"
                     " and each coordinator.py helper handed the coordinator, as"
                     " coordinator.<name> (#1686). Seeded by `python3 tests/structure.py"
                     " --seed-seam-map`; a unit missing here fails the ratchet.",
         "seams": dict(sorted(seams.items()))}, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {len(seams)} units to {SEAM_MAP_FILE.relative_to(REPO_ROOT)}")
    return 0


def seam_metrics(coord_class: ast.ClassDef, seams: dict[str, str] | None = None,
                 helpers: dict[str, tuple[ast.AST, frozenset[str]]] | None = None) -> dict:
    """The coordinator's seam partition: cut costs, call edges, per-seam rows.

    Split out of ``measure`` so the counting rules can be pinned on sources of
    our own (``self_check``) rather than only on whatever ``coordinator.py``
    happens to hold. #510 was a counting rule that was wrong across four
    merges with nothing in the suite able to fail on it. ``seams`` defaults to
    SEAM_MAP_FILE, and must name exactly the class's methods and ``helpers``.

    ``helpers`` are ``coordinator.py``'s module-level functions handed the
    coordinator (``CoordinatorRoles.coordinator_helpers``), each with the
    parameters that hold it. A helper is priced as the method it is in all
    but its ``def`` line (#1686): before, moving a method's body into
    ``_helper(self, ...)`` took every reference in it out of the cut, and
    inlining one back ADDED to rows -- the ranking the D7 round-9 finder
    measured upside down.
    """
    methods = {
        m.name: m
        for m in coord_class.body
        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    helpers = helpers or {}
    units: dict[str, tuple[ast.AST, frozenset[str]]] = {
        name: (fn, SELF_ROOT) for name, fn in methods.items()}
    units.update(helpers)
    helper_names = {key.split(".", 1)[1]: key for key in helpers}
    seams = load_seam_map() if seams is None else seams
    unmapped = sorted(set(units) - set(seams))
    stale = sorted(set(seams) - set(units))
    unknown = sorted(n for n, label in seams.items() if label not in (*SEAM_LABELS, "core"))
    if unmapped or stale or unknown:
        raise SeamMapError(
            f"seam map disagrees with {coord_class.name}: unmapped {unmapped},"
            f" stale {stale}, unknown seam {unknown}. Give each new or renamed"
            f" method, and each coordinator.py helper handed the coordinator, its"
            f" seam in {SEAM_MAP_FILE.name} (#1539, #1686)")
    buckets = {name: seams[name] for name in units}
    attr_refs: dict[str, Counter] = defaultdict(Counter)  # attr -> bucket -> occurrences
    attr_owners: dict[str, set[str]] = defaultdict(set)   # attr -> buckets that store it
    call_edges = Counter()                                # (caller bucket, callee bucket) -> occurrences
    for name, (fn, roots) in units.items():
        bucket = buckets[name]
        aliases, hops = state_root_bindings(fn, roots)
        for node in ast.walk(fn):
            if (
                isinstance(node, ast.Attribute)
                and id(node) not in hops
                and is_state_root(node.value, aliases, roots)
                and node.attr not in methods
            ):
                attr_refs[node.attr][bucket] += 1
                if isinstance(node.ctx, ast.Store):
                    attr_owners[node.attr].add(bucket)
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in roots
                and node.func.attr in methods
            ):
                call_edges[(bucket, buckets[node.func.attr])] += 1
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in helper_names
                and any(is_state_root(a, aliases, roots)
                        for a in [*node.args, *(k.value for k in node.keywords)])
            ):
                call_edges[(bucket, buckets[helper_names[node.func.id]])] += 1

    total_edges = sum(call_edges.values())
    cross_edges = sum(c for (a, b), c in call_edges.items() if a != b)

    seam_rows = []
    cut_costs = {}
    for label in SEAM_LABELS:
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

    return {
        "method_count": len(methods),
        "helper_count": len(helpers),
        "cut_costs": cut_costs,
        "seam_cut_total": sum(cut_costs.values()),
        "seam_rows": seam_rows,
        "internal_call_edges": total_edges,
        "cross_edges": cross_edges,
        "cross_seam_fraction": (cross_edges / total_edges) if total_edges else 0.0,
    }




# ---------------------------------------------------------------------------
# the package index, the coordinator by role, and the member census
#
# Three rows below need to know which value IS the coordinator outside its own
# class: the seam cut (a module-level ``_helper(self, ...)`` carries methods'
# state out of the class, #1686), the private reach (pump_arbiter.py, boost.py
# and the surfaces read coordinator privates no row priced, #1738 arm b) and
# the attribute census (writes from outside the class vanished from it). They
# find it by ROLE -- a value the coordinator was passed into, stored into or
# constructed as -- never by a parameter's name: renaming ``coord`` to
# ``owner`` hid 232 statements from the pre-study's name-keyed prototype.

COORDINATOR_ENTITY_BASES = ("CoordinatorEntity",)
COORDINATOR_MODULE = "coordinator"
MUTATOR_METHODS = frozenset({
    "append", "extend", "insert", "pop", "remove", "clear", "update",
    "setdefault", "add", "discard", "popitem", "sort", "reverse",
})
PRIVATE_WRITE_WEIGHT = 3


def fn_params(fn: ast.AST) -> list[str]:
    a = fn.args  # type: ignore[attr-defined]
    return [p.arg for p in a.posonlyargs + a.args + a.kwonlyargs]


def names_coordinator(ann: ast.AST | None) -> bool:
    """An annotation naming the coordinator class: bare, dotted or a string."""
    if ann is None:
        return False
    if isinstance(ann, ast.Constant) and isinstance(ann.value, str):
        return re.search(rf"\b{COORDINATOR_CLASS_NAME}\b", ann.value) is not None
    return any(
        (isinstance(n, ast.Name) and n.id == COORDINATOR_CLASS_NAME)
        or (isinstance(n, ast.Attribute) and n.attr == COORDINATOR_CLASS_NAME)
        for n in ast.walk(ann)
    )


def type_checking_ids(tree: ast.Module) -> set[int]:
    """Every node under an ``if TYPE_CHECKING:`` block, which never runs."""
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and (
            (isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING")
            or (isinstance(node.test, ast.Attribute) and node.test.attr == "TYPE_CHECKING")
        ):
            for stmt in node.body:
                out.update(id(n) for n in ast.walk(stmt))
    return out


class Package:
    """The integration's modules, functions, classes and import bindings.

    ``units`` is every function the role engine and the member census look
    inside: each module-level function and each class-body function, keyed by
    ``id(node)`` with its module, class and node. A def nested in one is part
    of its unit, as its closure is.
    """

    def __init__(self, trees: list[tuple[Path, ast.Module]]):
        self.mods: dict[str, tuple[str, ast.Module]] = {}
        for path, tree in trees:
            mod = path.relative_to(PACKAGE_DIR).as_posix()[:-3].replace("/", ".")
            self.mods[mod] = (str(path.relative_to(REPO_ROOT)), tree)
        self.top: dict[tuple[str, str], ast.AST] = {}
        self.classes: dict[tuple[str, str], ast.ClassDef] = {}
        self.units: dict[int, tuple[str, str | None, ast.AST]] = {}
        for mod, (_rel, tree) in self.mods.items():
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.top[(mod, node.name)] = node
                    self.units[id(node)] = (mod, None, node)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.classes.setdefault((mod, node.name), node)
                    if node in tree.body:
                        self.top[(mod, node.name)] = node
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            self.units[id(item)] = (mod, node.name, item)
        self.sym_bind, self.mod_bind = import_bindings(self.mods, self.top)

    def resolve(self, mod: str, name: str) -> tuple[str, str]:
        """``(defining module, name)`` of what ``name`` is bound to in ``mod``."""
        seen = set()
        while (mod, name) not in self.top and (mod, name) in self.sym_bind \
                and (mod, name) not in seen:
            seen.add((mod, name))
            mod, name = self.sym_bind[(mod, name)]
        return mod, name

    def base_keys(self, key: tuple[str, str]) -> list[tuple[str, str]]:
        """The in-package classes ``key`` derives from, nearest first."""
        out, todo = [], [key]
        while todo:
            mod, name = todo.pop(0)
            cls = self.classes.get((mod, name))
            if cls is None:
                continue
            for base in cls.bases:
                if isinstance(base, ast.Name):
                    found = self.resolve(mod, base.id)
                elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name) \
                        and (mod, base.value.id) in self.mod_bind:
                    found = (self.mod_bind[(mod, base.value.id)], base.attr)
                else:
                    continue
                if found in self.classes and found not in out and found != key:
                    out.append(found)
                    todo.append(found)
        return out

    def family(self, key: tuple[str, str]) -> set[tuple[str, str]]:
        """``key``, its in-package bases and every in-package subclass."""
        out = {key, *self.base_keys(key)}
        out |= {k for k in self.classes if key in self.base_keys(k)}
        return out

    def external_bases(self, key: tuple[str, str]) -> set[str]:
        """Last names of the bases ``key`` or its in-package bases take from outside."""
        names = set()
        for mod, name in [key, *self.base_keys(key)]:
            for base in self.classes[(mod, name)].bases:
                last = base.id if isinstance(base, ast.Name) else \
                    base.attr if isinstance(base, ast.Attribute) else None
                if last and self.resolve(mod, last) not in self.classes:
                    names.add(last)
        return names

    def callee(self, mod: str, cls: str | None, self_name: str | None,
               call: ast.Call) -> tuple[ast.AST, int] | None:
        """The package function ``call`` runs and how many leading params it binds.

        A module-level function binds none; a class (its ``__init__``) and a
        ``self.m(...)`` method bind one. Anything the AST cannot place -- a
        call on an untyped value, ``super()`` -- is None.
        """
        f = call.func
        target = None
        if isinstance(f, ast.Name):
            target = self.resolve(mod, f.id)
        elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            if (mod, f.value.id) in self.mod_bind:
                target = self.resolve(self.mod_bind[(mod, f.value.id)], f.attr)
            elif cls is not None and f.value.id == self_name:
                for owner in [(mod, cls), *self.base_keys((mod, cls))]:
                    for item in self.classes[owner].body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                                and item.name == f.attr:
                            return item, 1
                return None
        node = self.top.get(target) if target else None
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node, 0
        if isinstance(node, ast.ClassDef):
            for owner in [target, *self.base_keys(target)]:
                for item in self.classes[owner].body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        return item, 1
        return None


def import_bindings(mods: dict[str, tuple[str, ast.Module]],
                    top: dict[tuple[str, str], ast.AST] | None = None,
                    ) -> tuple[dict[tuple[str, str], tuple[str, str]], dict[tuple[str, str], str]]:
    """``(symbol bindings, module bindings)`` every relative import makes.

    ``from .m import *`` binds each public top-level name of ``m`` (#1738's
    tenth defect: the screen called 42 live constants dead under a star
    import, because nothing bound them).
    """
    sym_bind: dict[tuple[str, str], tuple[str, str]] = {}
    mod_bind: dict[tuple[str, str], str] = {}
    for mod, (_rel, tree) in mods.items():
        package = mod.split(".")[:-1]
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or node.level == 0:
                continue
            base = package[:len(package) - node.level + 1]
            src = ".".join(base + [node.module] if node.module else base)
            for alias in node.names:
                if alias.name == "*":
                    if src in mods:
                        for name in top_level_names(mods[src][1]):
                            if not name.startswith("_"):
                                sym_bind[(mod, name)] = (src, name)
                    continue
                bound = alias.asname or alias.name
                target = f"{src}.{alias.name}" if src else alias.name
                if target in mods:
                    mod_bind[(mod, bound)] = target
                else:
                    sym_bind[(mod, bound)] = (src or "__init__", alias.name)
    return sym_bind, mod_bind


class CoordinatorRoles:
    """Which values in the package are the coordinator, found by role.

    Seeds: ``self`` in the coordinator's own methods; a parameter annotated
    with the coordinator's class; ``self.coordinator`` on a class deriving
    from Home Assistant's ``CoordinatorEntity``, which stores the coordinator
    it is constructed with there; ``entry.runtime_data``, where
    ``__init__.py`` stores it (HA's runtime-data convention); and a call of
    the class itself. Then to a fixpoint: a parameter of any package function
    a coordinator value is passed into, and any ``self.X`` a class stores one
    into. A local bound to a coordinator value, and the context hop
    (``x._ctx``, ``getattr(x, "_ctx", x)``), carry the role.
    """

    def __init__(self, pkg: Package):
        self.pkg = pkg
        self.params: dict[int, set[str]] = defaultdict(set)
        self.slots: set[tuple[str, str, str]] = set()
        for (mod, name), cls in pkg.classes.items():
            if name == COORDINATOR_CLASS_NAME:
                for item in cls.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                            and fn_params(item) and not _is_static(item):
                        self.params[id(item)].add(fn_params(item)[0])
            if set(COORDINATOR_ENTITY_BASES) & pkg.external_bases((mod, name)):
                self.slots.add((mod, name, "coordinator"))
        for fid, (_mod, _cls, fn) in pkg.units.items():
            a = fn.args  # type: ignore[attr-defined]
            for p in a.posonlyargs + a.args + a.kwonlyargs:
                if names_coordinator(p.annotation):
                    self.params[fid].add(p.arg)
        self._propagate()

    def self_name(self, fid: int) -> str | None:
        mod, cls, fn = self.pkg.units[fid]
        params = fn_params(fn)
        return params[0] if cls is not None and params and not _is_static(fn) else None

    def is_coord(self, e: ast.AST, roots: set[str], fid: int) -> bool:
        mod, cls, _fn = self.pkg.units[fid]
        if isinstance(e, ast.Name):
            return e.id in roots
        if isinstance(e, ast.Attribute) and isinstance(e.ctx, ast.Load):
            if e.attr == "runtime_data":
                return True
            if e.attr == STATE_CONTEXT_ATTR:
                return self.is_coord(e.value, roots, fid)
            sn = self.self_name(fid)
            if cls is not None and isinstance(e.value, ast.Name) and e.value.id == sn:
                return any((m, c, e.attr) in self.slots
                           for m, c in [(mod, cls), *self.pkg.base_keys((mod, cls))])
            return False
        if isinstance(e, ast.Call):
            if isinstance(e.func, ast.Name) and e.func.id == "getattr" and len(e.args) >= 2 \
                    and isinstance(e.args[1], ast.Constant):
                if e.args[1].value == "runtime_data":
                    return True
                if e.args[1].value == STATE_CONTEXT_ATTR:
                    return self.is_coord(e.args[0], roots, fid)
            name = e.func.id if isinstance(e.func, ast.Name) else \
                e.func.attr if isinstance(e.func, ast.Attribute) else None
            return name == COORDINATOR_CLASS_NAME
        if isinstance(e, ast.IfExp):
            return self.is_coord(e.body, roots, fid) or self.is_coord(e.orelse, roots, fid)
        if isinstance(e, ast.NamedExpr):
            return self.is_coord(e.value, roots, fid)
        return False

    def roots(self, fid: int) -> set[str]:
        """The names that hold the coordinator anywhere in unit ``fid``."""
        roots = set(self.params.get(fid, ()))
        fn = self.pkg.units[fid][2]
        while True:
            before = len(roots)
            for node in ast.walk(fn):
                if isinstance(node, ast.Assign) and self.is_coord(node.value, roots, fid):
                    roots.update(t.id for t in node.targets if isinstance(t, ast.Name))
                elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)) and node.value is not None \
                        and isinstance(node.target, ast.Name) \
                        and self.is_coord(node.value, roots, fid):
                    roots.add(node.target.id)
            if len(roots) == before:
                return roots

    def _propagate(self) -> None:
        pkg = self.pkg
        changed = True
        while changed:
            changed = False
            for fid, (mod, cls, fn) in pkg.units.items():
                roots = self.roots(fid)
                sn = self.self_name(fid)
                for node in ast.walk(fn):
                    if isinstance(node, ast.Call):
                        hit = pkg.callee(mod, cls, sn, node)
                        if hit is None:
                            continue
                        target, skip = hit
                        params = fn_params(target)[skip:]
                        tid = id(target)
                        for i, arg in enumerate(node.args):
                            if i < len(params) and self.is_coord(arg, roots, fid) \
                                    and params[i] not in self.params[tid]:
                                self.params[tid].add(params[i])
                                changed = True
                        for kw in node.keywords:
                            if kw.arg in params and self.is_coord(kw.value, roots, fid) \
                                    and kw.arg not in self.params[tid]:
                                self.params[tid].add(kw.arg)
                                changed = True
                    elif cls is not None and isinstance(node, ast.Assign) \
                            and self.is_coord(node.value, roots, fid):
                        for t in node.targets:
                            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                                    and t.value.id == sn and (mod, cls, t.attr) not in self.slots:
                                self.slots.add((mod, cls, t.attr))
                                changed = True

    def coordinator_helpers(self) -> dict[str, tuple[ast.AST, frozenset[str]]]:
        """``coordinator.py``'s module-level functions that are handed the coordinator.

        Each is a method in all but its ``def`` line (#1686): it reads and
        writes the coordinator's state through a parameter, so the seam cut
        charges it as one, under a ``coordinator.<name>`` entry in the seam map.
        """
        out = {}
        for fid, (mod, cls, fn) in sorted(self.pkg.units.items(), key=lambda kv: kv[1][2].lineno):
            if mod == COORDINATOR_MODULE and cls is None and self.params.get(fid):
                out[f"{COORDINATOR_MODULE}.{fn.name}"] = (fn, frozenset(self.params[fid]))
        return out

    def is_charged(self, fid: int) -> bool:
        """Inside the coordinator: one of its methods, or one of its helpers."""
        mod, cls, _fn = self.pkg.units[fid]
        return mod == COORDINATOR_MODULE and (cls == COORDINATOR_CLASS_NAME or (
            cls is None and bool(self.params.get(fid))))


def _is_static(fn: ast.AST) -> bool:
    return any(isinstance(d, ast.Name) and d.id == "staticmethod"
               for d in getattr(fn, "decorator_list", []))


def private_member(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__") and name != STATE_CONTEXT_ATTR


def private_reach_sites(roles: CoordinatorRoles) -> list[tuple[str, int, str, str, str]]:
    """``(file, line, member, read|write, function)`` of every private reach (#1738 b).

    A private reach is ``<coordinator>._x`` -- or ``getattr``/``hasattr``/
    ``setattr``/``delattr`` on it with a literal ``"_x"`` -- anywhere outside
    the coordinator's own methods and helpers. A write is a store or delete of
    the slot, or an in-place mutation of what it holds (``c._x[k] = v``,
    ``c._x.append(..)``): the shape behind the boost overlay's shared-state
    defect (#1752), where a foreign module wrote the coordinator's invariants.
    """
    pkg = roles.pkg
    sites = set()
    for fid, (mod, _cls, fn) in pkg.units.items():
        if roles.is_charged(fid):
            continue
        roots = roles.roots(fid)
        rel = pkg.mods[mod][0]
        mutated: set[int] = set()
        for n in ast.walk(fn):
            targets = n.targets if isinstance(n, (ast.Assign, ast.Delete)) else \
                [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else []
            for t in targets:
                for x in (t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]):
                    if isinstance(x, (ast.Attribute, ast.Subscript)):
                        mutated.add(id(x.value))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in MUTATOR_METHODS:
                mutated.add(id(n.func.value))
        for n in ast.walk(fn):
            if isinstance(n, ast.Attribute) and private_member(n.attr) \
                    and roles.is_coord(n.value, roots, fid):
                kind = "write" if isinstance(n.ctx, (ast.Store, ast.Del)) or id(n) in mutated \
                    else "read"
                sites.add((rel, n.lineno, n.col_offset, n.attr, kind, fn.name))
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr", "setattr", "delattr") \
                    and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) \
                    and isinstance(n.args[1].value, str) and private_member(n.args[1].value) \
                    and roles.is_coord(n.args[0], roots, fid):
                kind = "write" if n.func.id in ("setattr", "delattr") or id(n) in mutated \
                    else "read"
                sites.add((rel, n.lineno, n.col_offset, n.args[1].value, kind, fn.name))
    return sorted((rel, line, member, kind, fn) for rel, line, _c, member, kind, fn in sites)


def coordinator_writers(roles: CoordinatorRoles) -> dict[str, set[str]]:
    """attr -> every function, in or out of the class, that stores it on the coordinator."""
    pkg = roles.pkg
    writers: dict[str, set[str]] = defaultdict(set)
    for fid, (mod, cls, fn) in pkg.units.items():
        roots = roles.roots(fid)
        if not roots:
            continue
        where = f"{mod}:{cls + '.' if cls else ''}{fn.name}"
        for n in ast.walk(fn):
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store) \
                    and n.attr != STATE_CONTEXT_ATTR and roles.is_coord(n.value, roots, fid):
                writers[n.attr].add(where)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "setattr" and len(n.args) >= 2 \
                    and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str) \
                    and roles.is_coord(n.args[0], roots, fid):
                writers[n.args[1].value].add(where)
    return writers


def dead_members(pkg: Package) -> tuple[list[tuple[str, str, str, int]], list[tuple[str, str, str]]]:
    """``(dead, name-kept)``: class-body functions no live code reaches (#1395, D7-s3-02).

    A member is a method or a property -- a property is a member like any
    other, and skipping it hid eight of the nine dead members round 9 found.
    A load reaches it only as an ATTRIBUTE: a bare name ``healthy`` read
    somewhere is a local, not ``InputHealth.healthy``. The receiver decides
    which class's member it is: ``self.n`` (or ``cls.n``) inside class C
    reaches ``n`` in C's in-package family -- C, its bases, its subclasses --
    and nothing else; ``x.n`` on a value the AST cannot type reaches every
    class's ``n``, and ``getattr(x, "n")`` likewise. Liveness is then
    REACHABILITY: a load counts only from a live place -- module-level code,
    a module-level function, a dunder, a Home Assistant convention member, or
    a member already live -- so a member reached only from its own body, or
    from other dead members, stays dead.

    ``name-kept`` is the shape this cannot measure, printed so its size is on
    the record: live members whose only live loads are untyped ``x.n`` reads
    of a name another class also defines, as a member or as a field. One of them may be dead behind
    another's field (D7-s3-01's ``DefrostDerate.samples`` stood alive behind
    ``AccuracyTracker.samples`` in every name-based view).
    """
    members: dict[tuple[str, str, str], tuple[str, int]] = {}
    by_name: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    for (mod, cname), cls in pkg.classes.items():
        for item in cls.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                key = (mod, cname, item.name)
                members.setdefault(key, (pkg.mods[mod][0], item.lineno))
                by_name[item.name].add(key)
    # Fields: a class-body assignment or annotation, or a ``self.n`` store in
    # a method. An untyped ``x.n`` may be reading another class's field n, so
    # a member that shares its name with one is name-kept, not measured-live.
    fields: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for (mod, cname), cls in pkg.classes.items():
        for item in cls.body:
            targets = item.targets if isinstance(item, ast.Assign) else \
                [item.target] if isinstance(item, ast.AnnAssign) else []
            for t in targets:
                if isinstance(t, ast.Name):
                    fields[t.id].add((mod, cname))
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = fn_params(item)
                if params and not _is_static(item):
                    for n in ast.walk(item):
                        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store) \
                                and isinstance(n.value, ast.Name) and n.value.id == params[0]:
                            fields[n.attr].add((mod, cname))

    def unique(key: tuple[str, str, str]) -> bool:
        return len(by_name[key[2]]) == 1 and not fields[key[2]] - {(key[0], key[1])}

    def is_root_member(key: tuple[str, str, str]) -> bool:
        name = key[2]
        return (name.startswith("__") and name.endswith("__")) \
            or name in HA_CONVENTION_NAMES or is_ha_convention_method(name)

    # (from-member or None for a root place, reached members, typed?)
    edges: list[tuple[tuple[str, str, str] | None, set[tuple[str, str, str]], bool]] = []
    families: dict[tuple[str, str], set[tuple[str, str]]] = {}

    def visit(node: ast.AST, mod: str, cls: str | None,
              unit: tuple[str, str, str] | None, self_name: str | None) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                for item in child.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        params = fn_params(item)
                        sn = params[0] if params and not _is_static(item) else None
                        visit(item, mod, child.name, (mod, child.name, item.name), sn)
                    else:
                        visit(item, mod, child.name, unit, self_name)
                for deco in child.decorator_list + child.bases:
                    visit(deco, mod, cls, unit, self_name)
                continue
            name = None
            if isinstance(child, ast.Attribute) and isinstance(child.ctx, ast.Load):
                name = child.attr
            elif isinstance(child, ast.Call) and isinstance(child.func, ast.Name) \
                    and child.func.id in ("getattr", "hasattr") and len(child.args) >= 2 \
                    and isinstance(child.args[1], ast.Constant) and isinstance(child.args[1].value, str):
                name = child.args[1].value
            if name is not None and name in by_name:
                recv = child.value if isinstance(child, ast.Attribute) else None
                if cls is not None and isinstance(recv, ast.Name) and recv.id == self_name:
                    fam = families.setdefault((mod, cls), pkg.family((mod, cls)))
                    edges.append((unit, {k for k in by_name[name] if (k[0], k[1]) in fam}, True))
                else:
                    edges.append((unit, set(by_name[name]), False))
            visit(child, mod, cls, unit, self_name)

    for mod, (_rel, tree) in pkg.mods.items():
        visit(tree, mod, None, None, None)

    live = {k for k in members if is_root_member(k)}
    typed_live: set[tuple[str, str, str]] = set()
    changed = True
    while changed:
        changed = False
        for src, reached, typed in edges:
            if src is not None and src not in live:
                continue
            for key in reached:
                if key not in live:
                    live.add(key)
                    changed = True
                if typed or unique(key):
                    typed_live.add(key)
    dead = sorted((members[k][0], k[1], k[2], members[k][1]) for k in members if k not in live)
    name_kept = sorted((members[k][0], k[1], k[2]) for k in live
                       if k not in typed_live and not is_root_member(k))
    return dead, name_kept


# ---------------------------------------------------------------------------
# the metrics


def measure() -> dict:
    """Recompute every metric from the working tree. Returns a dict with the
    flat metric values (the budget keys) under ``metrics`` and everything the
    evidence tables print under ``tables``."""
    trees = module_trees()
    pkg = Package(trees)

    god_classes = []       # (loc, file, span, name, methods)
    monsters = []          # (loc, file, span, name)
    cc_scores = []         # (cc, file, line, name)
    const_fanout = {}      # file -> imported names from .const

    # -- classes, functions, imports, dead symbols -------------------------
    top_level_defs: dict[tuple[str, str], int] = {}

    for path, tree in trees:
        rel = str(path.relative_to(REPO_ROOT))

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

        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            loc = span_loc(cls)
            if loc > GOD_CLASS_LOC_LIMIT:
                methods = sum(1 for m in cls.body
                              if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)))
                god_classes.append((loc, rel, f"{cls.lineno}-{cls.end_lineno}", cls.name, methods))

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

    # -- dead top-level symbols --------------------------------------------
    bound = bound_references(trees)
    dynamic_exempt, dynamic_problems = dynamic_reference_audit(
        trees, top_level_defs, bound
    )
    dead_symbols = [(rel, lineno, name) for (rel, name), lineno in sorted(top_level_defs.items())
                    if is_dead_symbol((rel, name), bound, dynamic_exempt)]

    # -- dead members (#1395, D7-s3-02) ------------------------------------
    dead_methods, name_kept = dead_members(pkg)

    # -- the coordinator, by role (#1686, #1738) ---------------------------
    roles = CoordinatorRoles(pkg)
    helpers = roles.coordinator_helpers()
    coord_class = pkg.classes[(COORDINATOR_MODULE, COORDINATOR_CLASS_NAME)]
    seam = seam_metrics(coord_class, helpers=helpers)
    reach = private_reach_sites(roles)
    writers = coordinator_writers(roles)

    clones = duplicate_clones(trees)
    cycles = import_cycle_modules(trees)
    max_method_loc, max_cc = table_maxima(monsters, cc_scores)

    metrics = {
        "methods_over_200": sum(1 for loc, *_ in monsters if loc > MONSTER_LIMITS[0]),
        "methods_over_150": len(monsters),
        # The coordinator's span, while it is the largest class; any class's
        # when it is not, so an extraction that moves the bulk elsewhere is
        # still priced (coordinator_loc merged in, identical in 30 of 30 of the
        # pre-study's perturbations).
        "max_class_loc": max((g[0] for g in god_classes), default=0),
        # The worst offender, off tables that are already built and already
        # sorted (#374). The four threshold counts above stop pricing a
        # function once it has crossed the line, so without these two the
        # cheapest place in the tree to put new complexity is the function
        # that is already worst. sum_cc is refused, and the module docstring
        # says why: it would fail #224's own refactor.
        "max_method_loc": max_method_loc,
        "max_cc": max_cc,
        "duplication_copies": sum(len(g) - 1 for g in clones),
        "functions_cc_over_25": sum(1 for cc, *_ in cc_scores if cc > CC_LIMITS[0]),
        "functions_cc_over_15": len(cc_scores),
        "const_modules_over_50": sum(1 for n in const_fanout.values() if n > CONST_FANOUT_LIMIT),
        "import_cycle_modules": sum(len(c) for c in cycles),
        "dead_top_level_symbols": len(dead_symbols),
        "dead_methods": len(dead_methods),
        "coordinator_attrs": len(writers),
        "coordinator_multiassigned_attrs": sum(1 for w in writers.values() if len(w) > 1),
        "coordinator_private_reach": sum(
            PRIVATE_WRITE_WEIGHT if kind == "write" else 1 for *_x, kind, _f in reach),
        "seam_cut_total": seam["seam_cut_total"],
    }
    tables = {
        "god_classes": sorted(god_classes, reverse=True),
        "monsters": sorted(monsters, reverse=True),
        "cc_scores": sorted(cc_scores, reverse=True),
        "const_fanout": dict(sorted(const_fanout.items(), key=lambda kv: -kv[1])),
        "import_cycles": cycles,
        "dead_symbols": dead_symbols,
        "dead_methods": dead_methods,
        "name_kept": name_kept,
        "dynamic_exempt": sorted(dynamic_exempt),
        "dynamic_problems": dynamic_problems,
        "clones": clones,
        "seam_rows": seam["seam_rows"],
        "helpers": sorted(helpers),
        "private_reach": reach,
        "outside_writers": sorted(
            (attr, sorted(w for w in ws if not w.startswith(f"{COORDINATOR_MODULE}:{COORDINATOR_CLASS_NAME}.")))
            for attr, ws in writers.items()
            if any(not w.startswith(f"{COORDINATOR_MODULE}:{COORDINATOR_CLASS_NAME}.") for w in ws)),
        "internal_call_edges": seam["internal_call_edges"],
        "cross_edges": seam["cross_edges"],
        "cross_seam_fraction": round(seam["cross_seam_fraction"], 4),
    }
    return {"metrics": metrics, "tables": tables}


# ---------------------------------------------------------------------------
# printing


def print_report(result: dict) -> None:
    tables = result["tables"]
    metrics = result["metrics"]

    print("########## classes over %d LOC (evidence; max_class_loc is the row) ##########"
          % GOD_CLASS_LOC_LIMIT)
    for loc, rel, span, name, methods in tables["god_classes"]:
        print(f"  {rel}:{span}  {loc} LOC  {methods} methods  {name}")

    print()
    print("########## monster methods: top 10 of %d over %d LOC ##########"
          % (metrics["methods_over_150"], MONSTER_LIMITS[1]))
    for loc, rel, span, name in tables["monsters"][:10]:
        print(f"  {rel}:{span}  {loc} LOC  {name}")
    print("  max_method_loc = %d (the worst one, budgeted; a count over a"
          " threshold stops pricing growth)" % metrics["max_method_loc"])

    print()
    print("########## worst 5 cyclomatic (of %d over %d) ##########"
          % (metrics["functions_cc_over_15"], CC_LIMITS[1]))
    for cc, rel, line, name in tables["cc_scores"][:5]:
        print(f"  {rel}:{line}  cc={cc}  {name}")
    print("  max_cc = %d (the worst one, budgeted; sum_cc is refused -- see the"
          " module docstring)" % metrics["max_cc"])

    print()
    print("########## .const import fan-out (names imported per module) ##########")
    for rel, n in tables["const_fanout"].items():
        flag = "  > %d" % CONST_FANOUT_LIMIT if n > CONST_FANOUT_LIMIT else ""
        print(f"  {rel}: {n}{flag}")

    print()
    print("########## import cycles (function-scope imports in, TYPE_CHECKING out) ##########")
    for group in tables["import_cycles"]:
        print("  " + " <-> ".join(group))

    print()
    print("########## dead top-level symbols ##########")
    for rel, line, name in tables["dead_symbols"]:
        print(f"  {rel}:{line}  {name}")

    print()
    print("########## dead members (no live attribute load reaches them) ##########")
    for rel, cls, name, line in tables["dead_methods"]:
        print(f"  {rel}:{line}  {cls}.{name}")
    print("  dead_methods = %d (methods and properties; receiver-resolved,"
          " reachability from live code)" % metrics["dead_methods"])
    print("  unmeasured: %d live member(s) kept only by an untyped x.name load of a"
          " name another class also defines" % len(tables["name_kept"]))
    for rel, cls, name in tables["name_kept"]:
        print(f"    {rel}  {cls}.{name}")

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
    print("########## duplication: clone classes (%d-statement AST windows, package-wide) ##########"
          % DUP_WINDOW_STATEMENTS)
    for group in tables["clones"]:
        print("  " + "  ==  ".join(f"{rel}:{line} {name}" for rel, name, line in group))

    print()
    print("########## coordinator private reach (outside its methods and helpers) ##########")
    for rel, line, member, kind, fn in tables["private_reach"]:
        print(f"  {rel}:{line}  {member}  {kind}  in {fn}")
    print("  coordinator_private_reach = %d (reads + %d x writes)"
          % (metrics["coordinator_private_reach"], PRIVATE_WRITE_WEIGHT))

    print()
    print("########## coordinator attributes written outside its methods ##########")
    for attr, where in tables["outside_writers"]:
        print(f"  {attr}: {', '.join(where)}")

    print()
    print("########## coordinator seam table (helpers charged: %d) ##########"
          % len(tables["helpers"]))
    print("  internal call occurrences: %d, crossing a seam: %d (ratio %.4f, evidence only)"
          % (tables["internal_call_edges"], tables["cross_edges"], tables["cross_seam_fraction"]))
    print("  %-8s %8s %6s %6s %6s %6s" % ("seam", "units", "attrs", "xattr", "xmeth", "cut"))
    for label, units, owned, xattr, xmeth, cut in tables["seam_rows"]:
        print("  %-8s %8d %6d %6d %6d %6d" % (label, units, owned, xattr, xmeth, cut))
    print("  seam_cut_total = %d" % metrics["seam_cut_total"])

    print()
    print("########## RESULT lines ##########")
    for key in sorted(metrics):
        print(f"RESULT {key}={metrics[key]} count")
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
    ``--amend``; under the squash merges `main` took until 2026-09-14 it was
    deleted outright (decisions/0010) -- so the field named a SHA that resolves
    to nothing, and the value in the committed table was right only when
    somebody noticed and fixed it by hand.

    The merge base against the upstream default branch is the commit the
    measurement actually describes: it exists on ``main``, and it survives the
    amend and any merge method. ``HEAD`` remains the fallback for a run with no
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
    an ancestor can only have come from the pre-#361 code (a branch SHA, which
    is not on ``main`` when this check runs -- a squash deleted it outright,
    and a merge commit only puts it there afterwards; decisions/0010) or from
    a hand edit. There is no legitimate workflow that produces one, so
    refusing is safe.

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


# ---------------------------------------------------------------------------
# the recorded-number barrier, shared by every ratchet under tests/


def cap_problem(where: str, table: object, key: str, *, integer: bool = False,
                low: float = 0.0, low_open: bool = False,
                high: float | None = None) -> str | None:
    """Why ``table[key]`` cannot be a ratchet's recorded number, or None.

    The class this closes (#1583's review): Python's json reads ``NaN``,
    ``Infinity``, ``-Infinity`` and ``1e999`` as floats without complaint, and
    every comparison against NaN is False -- ``current > nan`` never fires and
    ``raw < nan`` never fires -- so a cap edited to NaN was an unlimited raise
    that this script printed as ``ok cut_views 110 <= nan``. Infinity passes
    by arithmetic. The other spellings fail differently per script and none of
    them says why: a string crashed one comparison and ``float()``-coerced in
    another (``"nan"`` into NaN), and a bool is 0 or 1 to Python.

    So every ratchet calls this on load and refuses before it compares. It
    refuses: an absent key, a bool, anything not an int or float, a
    non-finite number, a float where ``integer`` asks for a count, a value
    below ``low`` (or equal to it when ``low_open``), and one above ``high``.
    The message names the file, the key and the value, so the refusal is the
    fix's instructions.
    """
    if not isinstance(table, dict) or key not in table:
        return (f"{where}: {key} is absent -- a ratchet with no recorded "
                f"number compares against nothing")
    value = table[key]
    label = f"{where}: {key}={value!r:.40}"
    if isinstance(value, bool):
        return (f"{label} is a boolean, which Python compares as "
                f"{int(value)}; record the number")
    if not isinstance(value, (int, float)):
        return f"{label} is a {type(value).__name__}, not a number"
    # An int before isfinite: json reads a 400-digit integer as an exact int,
    # and math.isfinite (like every float() a ratchet then applies) raises
    # OverflowError on one no float can hold.
    if isinstance(value, int):
        if abs(value) > 2 ** 53:
            return (f"{label} is past the largest integer a float holds "
                    f"exactly, so no comparison with a measurement means "
                    f"anything")
    elif not math.isfinite(value):
        return (f"{label} is not finite: every comparison against NaN is "
                f"false and nothing exceeds Infinity, so this cap would be an "
                f"unlimited raise")
    if integer and not isinstance(value, int):
        return f"{label} is a float where a count is recorded"
    if value < low or (low_open and value == low):
        return f"{label} is {'at or ' if low_open else ''}below {low:g}"
    if high is not None and value > high:
        return f"{label} is above {high:g}"
    return None


def regression_rows(old: dict, new: dict) -> list[tuple[str, float, float]]:
    """Every metric a re-record would move in the WORSENING direction.

    The direction is uniformly ``new > old`` and needs no metric-specific
    knowledge: ``ratchet`` below compares every metric in the budgets table
    the same way -- above the budget fails, below it is headroom -- so every
    one of them is lower-is-better. A per-metric direction table would be one more
    hand-maintained list to rot, which is the class of defect #364 and #304
    both turned out to be, so there deliberately is not one.


    Keys absent from either side are not rows: a metric that appeared or
    disappeared is already a FAIL in ``ratchet`` ("measured but not in the
    budget table"), and it has no old and new to put side by side.
    """
    rows = []
    for key in sorted(set(old) & set(new)):
        if key == "recorded_at":
            continue
        if new[key] > old[key]:
            rows.append((key, old[key], new[key]))
    return rows


def improvement_rows(budgets: dict, metrics: dict) -> list[tuple[str, float, float]]:
    """Every metric the tree has moved BELOW its budget: the exact mirror of
    ``regression_rows``, ``new < old`` where that one is ``new > old``.

    These are the rows ``ratchet`` fails on (#350). It used to print
    ``the next PR may re-record to lock it in`` and pass, and that note has a
    measured 0-for-6 record: #338 opened five metrics of slack, the note
    printed on six consecutive commits including a full release stamp, and #340
    then added four more without clearing any. It is not a message people
    occasionally forget -- it is one nobody has ever acted on.

    What the unrecorded gap costs is the whole argument for failing. A budget
    sitting above the tree is not a loose gate, it is an ABSENT one: after #338
    removed ten dead symbols, five could have been reintroduced and #338's own
    gate -- the gate that PR added in order to remove them -- would have said
    nothing. Failing puts the re-record in the PR that EARNED it, which is the
    only PR that can say what moved and why.

    The tax is small and was measured before it was imposed: a failing gate
    would have fired on 2 of the last 18 commits on main, about 11%, and was
    silent across the first eleven. The tree improves rarely, which is exactly
    why the improvement is worth capturing when it happens.

    Same exclusion as ``regression_rows``, for the same reason:
    ``recorded_at`` is provenance rather than a metric. A key present on one
    side only is not a row either: it is already a FAIL in ``ratchet``
    ("measured but not in the budget table"), and it has no pair to compare.
    """
    rows = []
    for key in sorted(set(budgets) & set(metrics)):
        if key == "recorded_at":
            continue
        if metrics[key] < budgets[key]:
            rows.append((key, budgets[key], metrics[key]))
    return rows


def report_improvements(rows: list[tuple[str, float, float]], breached: bool) -> None:
    """Say what got better and how to write it down.

    The framing is a requirement of #350 and not decoration: *a gate that
    scolds a pull request for improving the tree will be worked around, and
    then it protects nothing*. So this block does not use the word breached, it
    names every metric that moved, and it prints the exact runnable command --
    a gate that demands a re-record without naming the command is
    unsatisfiable by anyone who has not read this file.

    ``breached`` suppresses the command, because ``--record`` REFUSES a table
    with a worsened row (#370). Offering it while a breach stands would send
    the author into a refusal, so the breach is named as the thing to settle
    first; the improvement is still listed, because it is still true.
    """
    print()
    print("########## %d metric(s) IMPROVED and not yet recorded ##########" % len(rows))
    print("  %-32s %12s %12s %10s" % ("metric", "budget", "measured", "delta"))
    for key, budget, current in rows:
        delta = current - budget
        shown = f"{delta:+.4f}" if isinstance(delta, float) else f"{delta:+}"
        print("  %-32s %12s %12s %10s  BETTER (lower is better)"
              % (key, budget, current, shown))
    print()
    print("  You made the tree better here, so write it down. The ratchet only")
    print("  guards numbers that are recorded: for everything in the gap between")
    print("  a budget and a better tree the gate is not loose, it is ABSENT, and")
    print("  the improvement can be given back without anything failing (#350).")
    print("  This belongs in the PR that earned it -- that is the only PR that can")
    print("  say what moved and why.")
    if breached:
        print()
        print("  A budget is also BREACHED above, so --record would refuse this table")
        print("  (#370). Settle the breach first: pay for the lines, or re-record the")
        print('  whole table with --allow-regression="<reason>" and put that reason in')
        print("  the commit message.")
        return
    print()
    print("  Run this, and commit the result with this change:")
    print()
    print("      python3 tests/structure.py --record")
    print()
    print("  Then say in the COMMIT message which rows moved and why -- the")
    print("  history of main keeps a commit message, never a PR body.")


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
    ``main``'s history keeps it, rather than in a PR body that history does
    not carry (decisions/0010).
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
            print("main's history keeps a commit message, never a PR body.")
            return 1
        print()
        print("ALLOWED: %s" % allow_regression.strip())
        print("Repeat this reason in the commit message -- main's history")
        print("keeps a commit message and never a pull-request body.")

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
    # Before any comparison: a cap that is not a finite count compares as
    # "ok" (NaN), crashes (a string), or means something nobody recorded.
    malformed = [p for p in (cap_problem(BUDGET_FILE.name, budgets, key, integer=True)
                             for key in sorted(budgets) if key != "recorded_at") if p]
    if malformed:
        for problem in malformed:
            print(f"FAIL {problem.split(': ', 1)[1]}")
        print(f"{len(malformed)} STRUCTURE BUDGET(S) MALFORMED -- every row is a")
        print("non-negative integer count; restore the recorded value, or re-record")
        print("with tests/structure.py --record.")
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
        print("  merge base -- a branch SHA is not on main yet (#361).")
        failures += 1
    budget_keys = {k: v for k, v in budgets.items() if k != "recorded_at"}
    improvements = improvement_rows(budget_keys, metrics)
    improved = {key for key, _, _ in improvements}
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
        if current > budget:
            print(f"FAIL {key} {current} > {budget} (+{current - budget})")
            failures += 1
        elif key in improved:
            print(f"  gain {key} {current} (budget {budget},"
                  f" {current - budget:+d}; not yet recorded -- see below)")
        else:
            print(f"  ok   {key} {current} <= {budget}")
    if improvements:
        # Not `bool(failures)`: what suppresses the command is precisely what
        # --record would refuse, which is a row over its budget. A key-set
        # mismatch also fails above and is also settled BY re-recording, so
        # offering the command there is right.
        report_improvements(
            improvements, breached=bool(regression_rows(budget_keys, metrics))
        )
    print()
    if failures:
        print(f"{failures} STRUCTURE BUDGET(S) BREACHED")
        print("Three responses, all of them deliberate: pay for the lines")
        print("elsewhere; re-record because the tree genuinely improved; or, for")
        print("a genuine new production FEATURE, RAISE the budget because the")
        print("capability is worth the structure it costs. Paying is the first")
        print("question; a raise is for when the honest answer is that you")
        print("cannot. A raise needs the repository OWNER'S EXPLICIT CONFIRMATION")
        print("before the branch is pushed -- stop and ask, do not push and")
        print("explain.")
        print("A budget may only be re-recorded deliberately, on a clean tree,")
        print("with the reason in the COMMIT -- never to make a failure go away.")
        print("--record refuses any row that moves the wrong way unless you pass")
        print('--allow-regression="<reason>", and that reason belongs in the commit')
        print("message: main's history keeps it and never a pull-request body.")
        return 1
    if improvements:
        # Deliberately not counted with the breaches above and deliberately not
        # worded like one. This run failed because the tree got BETTER, and the
        # only thing missing is the record of it (#350). Exit 2, not 1: a
        # violation and an unrecorded gain are not the same report (#808).
        print("%d STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED" % len(improvements))
        print("Nothing here is a violation. Run the command above, commit the")
        print("table with this change, and say in the commit which rows moved.")
        return 2
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


# ``_depth`` is stored by core and so crosses the fetch seam; ``_cache`` is
# stored by the fetch method and so is that seam's own. One read of one of
# them goes in the hole, written every way the coordinator spells a read of
# its own state -- the point being that the spelling must not set the price.
SEAM_SELF_CHECK_SOURCE = '''
class Coordinator:
    def __init__(self):
        self._ctx = None
        self._depth = 0

    def _fetch_prices(self):
        self._cache = 1
%s
'''
SEAM_SELF_CHECK_SPELLINGS = (
    "        return self.%(attr)s",
    '        return getattr(self, "_ctx", self).%(attr)s',
    "        return self._ctx.%(attr)s",
    '        ctx = getattr(self, "_ctx", self)\n        return ctx.%(attr)s',
    "        ctx = self._ctx\n        return ctx.%(attr)s",
)
SEAM_SELF_CHECK_FOREIGN = (
    "        ctx = elsewhere()\n        return ctx._depth",
    '        other = elsewhere()\n        return getattr(other, "_ctx", other)._depth',
)


def seam_self_check() -> tuple[tuple[str, bool], ...]:
    """Pin what ``cut_<seam>`` prices as a reference, spelling by spelling.

    ``getattr(self, "_ctx", self).X`` falls back to ``self``, so it reaches
    what ``self.X`` reaches and an extraction still has to make it explicit.
    Matching only ``ast.Attribute`` on ``ast.Name("self")`` scored it zero, so
    #500's 131 rewrites were recorded as a 138-point drop across five seams
    with no reference removed, and four merges of halt-or-extract decisions
    were taken against those denominators before anything noticed.

    The second assertion is the one the direct ``self._ctx.X`` spelling needs.
    Pricing the hop instead of what lies beyond it costs the same in total
    while attributing every read to ``_ctx``, which core owns -- so a seam is
    charged for reaching state it owns itself.
    """

    seams = {"__init__": "core", "_fetch_prices": "fetch"}

    def cut(body: str, rename: str = "_fetch_prices", seam_map=seams) -> int:
        tree = ast.parse((SEAM_SELF_CHECK_SOURCE % body).replace("_fetch_prices", rename))
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        return seam_metrics(cls, seam_map)["cut_costs"]["cut_fetch"]

    def refused(seam_map: dict[str, str]) -> bool:
        try:
            cut("        return 0", seam_map=seam_map)
        except SeamMapError:
            return True
        return False

    base = cut("        return 0")
    crossing = [cut(t % {"attr": "_depth"}) for t in SEAM_SELF_CHECK_SPELLINGS]
    owned = [cut(t % {"attr": "_cache"}) for t in SEAM_SELF_CHECK_SPELLINGS]
    foreign = [cut(b) for b in SEAM_SELF_CHECK_FOREIGN]
    return (
        ("a read that crosses the seam costs one, however it is spelt",
         all(c == base + 1 for c in crossing)),
        ("a read of what the seam owns costs nothing, however it is spelt",
         all(c == base for c in owned)),
        ("the state root is the binding, not the name it is bound to",
         all(c == base for c in foreign)),
        ("a method's seam is its map entry, not its name (#1539)",
         cut("        return self._depth", "_zz", {"__init__": "core", "_zz": "fetch"})
         == crossing[0]),
        ("a method the map does not name is refused",
         refused({"__init__": "core"})),
        ("a map entry naming no method, or no seam, is refused",
         refused({**seams, "_gone": "core"}) and refused({**seams, "__init__": "nowhere"})),
    )


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

    def audit(const_src: str | None, proof_src: str, referenced: set[tuple[str, str]]):
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
    now_static = audit(AUDIT_SELF_CHECK_CONST, AUDIT_SELF_CHECK_PROOF,
                       {(const_rel, "CONF_PROVEN")})

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


BOUND_SELF_CHECK_SOURCES = {
    "a.py": "from . import b\nfrom .c import shared as alias\n_LOGGER = 1\n"
            "def f(thing):\n    return alias() + b.g() + thing.untyped + self.own\n"
            "def recurse(n):\n    return recurse(n - 1)\n",
    "b.py": "_LOGGER = 2\ndef g():\n    return _LOGGER\ndef h(): pass\n"
            "def untyped(): pass\ndef own(): pass\n",
    "c.py": "def shared(): pass\n_LOGGER = 3\ndef g(): pass\n",
}


def bound_self_check() -> tuple[tuple[str, bool], ...]:
    """Pin ``bound_references``' four arms on a three-module tree (#1538)."""
    bound = bound_references(
        [(PACKAGE_DIR / m, ast.parse(src)) for m, src in BOUND_SELF_CHECK_SOURCES.items()])
    refs = {(Path(rel).name, name) for rel, name in bound}
    c_logger = (str((PACKAGE_DIR / "c.py").relative_to(REPO_ROOT)), "_LOGGER")
    return (
        ("an aliased import resolves to the symbol it binds", ("c.py", "shared") in refs),
        ("a same-named symbol read elsewhere is not a reference",
         ("b.py", "_LOGGER") in refs and not {("a.py", "_LOGGER"), ("c.py", "_LOGGER")} & refs),
        ("the screen reports a symbol whose name another module reads",
         is_dead_symbol(c_logger, bound, set())),
        ("m.N reaches N in m and nothing else",
         ("b.py", "g") in refs and not {("b.py", "h"), ("c.py", "g")} & refs),
        ("x.N on an untyped value reaches every top-level N", ("b.py", "untyped") in refs),
        ("self.N is not a module reference", ("b.py", "own") not in refs),
        ("a function calling itself is not bound-referenced", ("a.py", "recurse") not in refs),
    )


ROLE_SELF_CHECK_SOURCES = {
    "coordinator.py":
        "class HeatPumpOptimizerCoordinator:\n"
        "    def __init__(self):\n"
        "        self._depth = 0\n"
        "    def tick(self):\n"
        "        return _helper(self) + self.used\n"
        "    @property\n"
        "    def used(self):\n"
        "        return 1\n"
        "    @property\n"
        "    def unread(self):\n"
        "        return 2\n"
        "    def recur(self):\n"
        "        return self.recur()\n"
        "    def shared(self):\n"
        "        return 3\n"
        "def _helper(owner):\n"
        "    return owner._depth\n",
    "pump.py":
        "from .coordinator import HeatPumpOptimizerCoordinator\n"
        "from .other import *\n"
        "def poke(coord: HeatPumpOptimizerCoordinator, thing):\n"
        "    unread = coord.tick() + thing.shared() + STARRED\n"
        "    coord._depth += 1\n"
        "    return relay(coord) + unread\n"
        "def relay(c):\n"
        "    return inner(c)\n"
        "def inner(renamed):\n"
        "    renamed._log.append(1)\n"
        "    return renamed._depth\n",
    "other.py":
        "STARRED = 1\n"
        "class Other:\n"
        "    def shared(self):\n"
        "        return 4\n",
}

# One window, three spellings of it: a second copy in another module is a
# copy, and a third costs one more, not two more.
DUP_SELF_CHECK_BODY = (
    "def {name}({a}, {b}):\n"
    "    {t} = sum(v * {b} for v in {a} if v > 0)\n"
    "    return max({t}, len({a}) * {b} - 1)\n"
)

# A cycle through a function-scope import, and the same edge under
# TYPE_CHECKING, which never runs.
CYCLE_SELF_CHECK_SOURCES = {
    "a.py": "def f():\n    from . import b\n    return b\n",
    "b.py": "from . import a\n",
}
CYCLE_SELF_CHECK_GUARDED = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from . import a\n"

# A member whose only load is an untyped x.n, where another class holds a
# FIELD n (a self.n store, or a class-body annotation), not a method n: the
# shape D7-s3-01's DefrostDerate.samples hid behind AccuracyTracker.samples.
FIELD_SELF_CHECK_SOURCE = (
    "class Tracker:\n"
    "    def __init__(self):\n"
    "        self.samples = []\n"
    "class Record:\n"
    "    count: int = 0\n"
    "class Derate:\n"
    "    @property\n"
    "    def samples(self):\n"
    "        return 1\n"
    "    @property\n"
    "    def count(self):\n"
    "        return 2\n"
    "def read(thing):\n"
    "    return thing.samples + thing.count\n"
)


def role_self_check() -> tuple[tuple[str, bool], ...]:
    """Pin the member census, the role engine and the #1738 rows on our own trees."""
    trees = [(PACKAGE_DIR / m, ast.parse(src)) for m, src in ROLE_SELF_CHECK_SOURCES.items()]
    pkg = Package(trees)
    dead, name_kept = dead_members(pkg)
    dead_names = {(cls, name) for _rel, cls, name, _line in dead}
    coord = COORDINATOR_CLASS_NAME
    roles = CoordinatorRoles(pkg)
    helpers = roles.coordinator_helpers()
    reach = private_reach_sites(roles)
    sites = {(fn, member, kind) for _rel, _line, member, kind, fn in reach}
    writers = coordinator_writers(roles)
    bound = bound_references(trees)

    def seam_cut(source: str) -> int:
        local = Package([(PACKAGE_DIR / "coordinator.py", ast.parse(source))])
        local_helpers = CoordinatorRoles(local).coordinator_helpers()
        cls = local.classes[(COORDINATOR_MODULE, coord)]
        seams = {"__init__": "core", "tick": "fetch",
                 **{key: "fetch" for key in local_helpers}}
        return seam_metrics(cls, seams, local_helpers)["seam_cut_total"]

    inline = ("class HeatPumpOptimizerCoordinator:\n"
              "    def __init__(self):\n        self._depth = 0\n"
              "    def tick(self):\n        return self._depth\n")
    helped = ("class HeatPumpOptimizerCoordinator:\n"
              "    def __init__(self):\n        self._depth = 0\n"
              "    def tick(self):\n        return _helper(self)\n"
              "def _helper(owner):\n    return owner._depth\n")

    def copies(*names: str) -> int:
        srcs = [DUP_SELF_CHECK_BODY.format(name=f"f{i}", a=a, b=b, t=t)
                for i, (a, b, t) in enumerate(names)]
        return sum(len(g) - 1 for g in duplicate_clones(
            [(PACKAGE_DIR / f"m{i}.py", ast.parse(s)) for i, s in enumerate(srcs)]))

    field_dead, field_kept = dead_members(
        Package([(PACKAGE_DIR / "fields.py", ast.parse(FIELD_SELF_CHECK_SOURCE))]))

    def cycles(b_source: str) -> list[list[str]]:
        return import_cycle_modules([
            (PACKAGE_DIR / "a.py", ast.parse(CYCLE_SELF_CHECK_SOURCES["a.py"])),
            (PACKAGE_DIR / "b.py", ast.parse(b_source))])

    return (
        ("a property nothing reads is a dead member", (coord, "unread") in dead_names),
        ("a bare name is a local, and keeps no member alive", (coord, "unread") in dead_names),
        ("a member reached only from its own body is dead", (coord, "recur") in dead_names),
        ("a property read through self from a live member is live",
         (coord, "used") not in dead_names and (coord, "tick") not in dead_names),
        ("an untyped x.n keeps every class's n alive, and says so",
         not {(coord, "shared"), ("Other", "shared")} & dead_names
         and {name for _rel, _cls, name in name_kept} == {"shared"}),
        ("an untyped x.n of a name another class holds as a field is name-kept",
         not field_dead
         and {(cls, name) for _rel, cls, name in field_kept}
         == {("Derate", "samples"), ("Derate", "count")}),
        ("a coordinator.py function handed the coordinator is a helper",
         set(helpers) == {"coordinator._helper"}
         and helpers["coordinator._helper"][1] == {"owner"}),
        ("a helper is priced as the method it was cut from (#1686)",
         seam_cut(helped) == seam_cut(inline) > 0),
        ("a private read and write outside the class are reach, by role",
         {("poke", "_depth", "write"), ("inner", "_depth", "read")} <= sites),
        ("an in-place mutation is a write, through a renamed parameter",
         ("inner", "_log", "write") in sites),
        ("the helper's own reads are the coordinator's, not reach",
         not any(fn == "_helper" for fn, _m, _k in sites)),
        ("an attribute stored from another module is in the census",
         "pump:poke" in writers.get("_depth", set())
         and "coordinator:HeatPumpOptimizerCoordinator.__init__" in writers["_depth"]),
        ("a star import binds the public names it brings",
         (str((PACKAGE_DIR / "other.py").relative_to(REPO_ROOT)), "STARRED") in bound),
        ("a copy in another module is one copy, renamed or not",
         copies(("xs", "k", "t"), ("values", "scale", "total")) == 1),
        ("a third copy costs one more", copies(("a", "b", "c"), ("d", "e", "f"), ("g", "h", "i")) == 2),
        ("a function-scope import closes a cycle", cycles(CYCLE_SELF_CHECK_SOURCES["b.py"]) == [["a", "b"]]),
        ("a TYPE_CHECKING import is not an edge", cycles(CYCLE_SELF_CHECK_GUARDED) == []),
    )


def self_check() -> int:
    """Pin the counting rules on sources of our own (#364, #510).

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
    rules = (
        ("an aliased import records the ORIGINAL name", "max_abs_component" in refs),
        ("an aliased import also records the alias", "gf_max" in refs),
        ("an unaliased import still records its name", "min_component" in refs),
        ("a dotted aliased import records both halves",
         "submodule" in refs and "sub" in refs),
        ("a function calling itself is recursion, not a reference",
         "recurse" not in refs),
        ('a getattr(x, f"CONF_{..}") name is NOT a static reference',
         "CONF_WANTED" not in refs),
        *bound_self_check(),
        *audit_self_check(),
        *seam_self_check(),
        *role_self_check(),
    )
    failures = [message for message, ok in rules if not ok]
    print("########## counting-rule self-check ##########")
    for message in failures:
        print(f"FAIL  {message}")
    if failures:
        print(f"{len(failures)} COUNTING RULE(S) BROKEN -- "
              "the structure rows cannot be trusted")
        return 1
    print(f"  ok   {len(rules)} counting rules hold")
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
             "reason -- which belongs in the commit message too (#370). Raising "
             "a budget for a new production feature needs the repository "
             "owner's explicit confirmation before the branch is pushed",
    )
    parser.add_argument(
        "--seed-seam-map",
        action="store_true",
        help="rewrite tests/seam_map.json from SEAM_REGEXES over every "
             "coordinator method (#1539), then measure",
    )
    args = parser.parse_args()

    if args.seed_seam_map:
        seed_seam_map()
    if self_check():
        return 1

    try:
        result = measure()
    except SeamMapError as err:
        print(f"SEAM MAP REFUSED: {err}")
        return 1
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
