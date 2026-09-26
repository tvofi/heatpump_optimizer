#!/usr/bin/env python3
"""#1413: derive the claim set from the documents and the fact set from code.

The round-6 stale-prose class (CONDENSED.md section 6): a reader doc asserts a
fact about shipped code that the code no longer makes, and the only
doc-vs-code machinery is keyed to claims someone hand-enumerated -- so a newly
written sentence escapes until a later round names it. This check derives BOTH
sides for seven claim shapes, and fails closed on a contradiction:

  * generated-figure freshness    -- D5-01 #1389 (marginal-cop.svg predates the
    #928 resistive clamp)
  * ECL110 topic shipped defaults -- D6-01 #1391 (README tells users to clear
    topics that ship empty)
  * entity object-id prefix       -- D6-03 #1393 (docs say the prefix follows
    the entry name; the code pins a hard-coded literal)
  * README requirements vs manifest.json -- D6-s1 #1537
  * Quick start step numbering    -- D5-s1 #1535
  * quality_scale strict-typing census -- R8-D10-s1-01 #1545 (the yaml states
    qs_entry_param_bare=0 while annotations still name the bare ConfigEntry)
  * quality_scale exception-translation census -- R8-D10-s1-02 #1546 (the
    yaml marks every raise site translated while four UpdateFailed raises
    carried no translation_domain / translation_key)

The fact set is derived by importing and executing production code; the claim
set is derived by scanning the reader documents and the shipped blueprints.
For the two quality_scale arms the "document" is quality_scale.yaml, which
hassfest never reads for a custom integration, so nothing else checks it.
Neither side is a hand-maintained enumeration: a new sentence of the same shape
enters the check the moment it lands.

Every arm carries an anchor (null control): the absence of the claim's subject
is itself red, so the check cannot go green by skipping.

RUN (from the repository root, never elsewhere):
    PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
for _extra in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(ROOT / _extra))

from harness import Results  # noqa: E402

R = Results("doc claims vs code facts (#1413)")

PKG = ROOT / "custom_components" / "heatpump_optimizer"
BLUEPRINTS_DIR = ROOT / "blueprints" / "automation"

README = (ROOT / "README.md").read_text()
# Reader-facing prose only: the audit-* pages and backlog.md are measurement
# RECORDS that may legitimately quote a stale claim, and plan-* / HANDOVER.md
# are internal programme state -- a record stays as written (fixer.md step 10),
# so they are not scanned.
DOCS = {
    p.name: p.read_text()
    for p in sorted((ROOT / "docs").glob("*.md"))
    if (
        not p.name.startswith("plan-")
        and not p.name.startswith("audit-")
        and p.name not in ("HANDOVER.md", "backlog.md")
    )
}
BLUEPRINTS = {
    p.name: p.read_text() for p in sorted(BLUEPRINTS_DIR.glob("*.yaml"))
}
# The reader corpus this check scans: README, the top-level user docs, and the
# shipped blueprints (docs/automations.md links them, and a blueprint input
# description is reader-facing prose).
CORPUS = {"README.md": README, **DOCS, **{"blueprints/automation/" + k: v for k, v in BLUEPRINTS.items()}}


# ---------------------------------------------------------------------------
# Fact set, derived from code
# ---------------------------------------------------------------------------

def ecl110_topic_defaults() -> dict[str, str]:
    """Shipped defaults of the three ECL110 topic options, by execution.

    The empty-string default is the fact #1391's README prose contradicts:
    ``_F("heat_curve", CONF_ECL110_*_TOPIC, "", str)``.
    """
    from heatpump_optimizer import const
    from heatpump_optimizer import config_flow

    keys = (
        const.CONF_ECL110_DISPLACE_SET_TOPIC,
        const.CONF_ECL110_COMMAND_TOPIC,
        const.CONF_ECL110_STATE_TOPIC,
    )
    return {row.key: row.default for row in config_flow._OPTION_FIELDS if row.key in keys}


def manifest_requirement_names() -> list[str]:
    """Package names (PEP 508, stripped of version specifiers) that
    ``manifest.json`` pins, in the order the manifest lists them.

    #1537's fact: the manifest's own ``requirements`` list, which Home
    Assistant installs automatically -- the set the README's Requirements
    section claims to enumerate.
    """
    import json

    manifest = json.loads((PKG / "manifest.json").read_text())
    return [re.split(r"[<>=!~\[]", r, 1)[0].strip() for r in manifest["requirements"]]


def entity_id_prefix_literals() -> dict[str, str]:
    """The object-id prefix token each platform pins in its ``entity_id`` f-string.

    Returns ``{module_name: prefix_token}`` for every platform that assigns
    ``entity_id = f"<domain>.<prefix>_{translation_key}"``. A prefix that
    followed the entry name would be written as an expression (``{slug(entry
    title)}``) or omit the assignment; the shipped form is a hard-coded
    literal, which is the fact #1393's prose contradicts.
    """
    pattern = re.compile(r'entity_id\s*=\s*f"[a-z_]+\.([a-z0-9_]+)_\{translation_key\}"')
    found: dict[str, str] = {}
    for path in sorted(PKG.glob("*.py")):
        text = path.read_text()
        for m in pattern.finditer(text):
            found[path.name] = m.group(1)
    return found


def regenerated_model_figures() -> dict[str, bytes]:
    """Every docs/img model SVG re-derived from the shipped model, as bytes.

    Imports ``docs/img/make_model_figures.py`` (which calls production
    ``ThermalModel`` methods) and collects what ``__main__`` would write, so a
    committed figure that stopped agreeing with the model is a byte difference
    here rather than a stale picture. ``demand_windows`` reads the plan payload
    ``tests/plan_view.py`` writes; both honour ``HPO_PLANDATA`` and agree on its
    default, so the payload is written to a scratch path first. ``plan_view``
    ends with a module-level ``sys.exit`` (it is written to be run, not
    imported), so it is driven as a subprocess rather than imported.
    """
    import subprocess

    _plan_dir = tempfile.mkdtemp(prefix="doc-claims-plan-")
    plan_path = str(pathlib.Path(_plan_dir) / "plan.json")

    env = dict(os.environ)
    env["HPO_PLANDATA"] = plan_path
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ROOT / "tests" / "hastub"), str(ROOT / "tests"), str(ROOT / "custom_components")]
        + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
    )
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "plan_view.py")],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"plan_view.py failed to write the plan payload (rc {proc.returncode}):\n{proc.stdout}"
        )

    # make_model_figures reads HPO_PLANDATA at import time, so it must be set
    # to the same path before the module is executed.
    os.environ["HPO_PLANDATA"] = plan_path
    spec = importlib.util.spec_from_file_location(
        "make_model_figures", ROOT / "docs" / "img" / "make_model_figures.py"
    )
    mmf = importlib.util.module_from_spec(spec)
    sys.modules["make_model_figures"] = mmf
    spec.loader.exec_module(mmf)

    out: dict[str, bytes] = {}
    svg = mmf.demand_windows()
    out["dhw-demand-windows.svg"] = svg.encode()
    svg, _identical = mmf.marginal_cop()
    out["marginal-cop.svg"] = svg.encode()
    svg, _ceiling, _retained = mmf.store_decay()
    out["dhw-store-decay.svg"] = svg.encode()
    return out


# ---------------------------------------------------------------------------
# Arm 1 -- generated-figure freshness (D5-01 / #1389)
# ---------------------------------------------------------------------------

def check_figures() -> None:
    R.section("generated-figure freshness (#1389)")
    fresh = regenerated_model_figures()
    names = sorted(fresh)
    # Null control: the generator must produce exactly the committed set.
    R.check("make_model_figures produces 3 model SVGs", names == sorted(
        ["dhw-demand-windows.svg", "dhw-store-decay.svg", "marginal-cop.svg"]
    ), repr(names))
    for name in names:
        committed_path = ROOT / "docs" / "img" / name
        committed = committed_path.read_bytes()
        R.check(
            f"{name} matches the regenerated bytes",
            committed == fresh[name],
            f"committed {len(committed)} B vs regenerated {len(fresh[name])} B",
        )


# ---------------------------------------------------------------------------
# Arm 2 -- ECL110 topic shipped defaults (D6-01 / #1391)
# ---------------------------------------------------------------------------

# The false-claim shapes #1391 found in README.md. Scanned, not enumerated per
# claim: any sentence of this shape is red while the defaults are empty.
_SHIP_NONEMPTY = re.compile(r"ship non-empty")
_CLEAR_TOPICS = re.compile(r"clear the (two )?command topics?")


def check_ecl110_defaults() -> None:
    R.section("ECL110 topic shipped defaults (#1391)")
    defaults = ecl110_topic_defaults()
    empty = {k: v for k, v in defaults.items() if v == ""}
    # Fact: every topic option ships an empty-string default.
    R.check(
        "all three ECL110 topic options ship an empty-string default",
        len(empty) == 3 and set(empty) == set(defaults),
        repr(defaults),
    )
    # Anchor: README still documents the ECL110 path at all.
    R.check(
        "README still documents the ECL110 path (anchor)", "ECL110" in CORPUS["README.md"]
    )
    offenders: dict[str, list[str]] = {}
    for name, text in CORPUS.items():
        hits = _SHIP_NONEMPTY.findall(text) + _CLEAR_TOPICS.findall(text)
        if hits:
            offenders[name] = hits
    R.check(
        "no reader doc claims the ECL110 topics ship non-empty",
        not offenders,
        repr(offenders),
    )


# ---------------------------------------------------------------------------
# Arm 3 -- entity object-id prefix (D6-03 / #1393)
# ---------------------------------------------------------------------------

# The whitespace between words is ``\s+``: YAML folded scalars wrap a long
# sentence across lines, and the same claim wrapped differently must still be
# caught (#1393's own round named two blueprints and missed the third, whose
# "prefix\n        follows" split the two words across a fold).
_PREFIX_FOLLOWS_NAME = re.compile(
    r"(?:entity\s+)?prefix\s+follows\s+the\s+name", re.IGNORECASE
)
_CHANGE_PREFIX = re.compile(r"change\s+the\s+prefix\s+if\s+you\s+named", re.IGNORECASE)
_HAS_ENTITY_NAME_PREFIX = re.compile(
    r"has_entity_name.{0,120}?prefix", re.IGNORECASE | re.DOTALL
)


def check_entity_prefix() -> None:
    R.section("entity object-id prefix (#1393)")
    literals = entity_id_prefix_literals()
    # Fact: every platform that pins an object id uses the same hard-coded
    # token, ``heat_pump_optimizer`` -- never a function of the entry title.
    R.check(
        "the object-id prefix is the hard-coded literal, not entry.title",
        bool(literals) and set(literals.values()) == {"heat_pump_optimizer"},
        repr(literals),
    )
    # Anchor: the reader corpus still documents entity ids at all.
    ids_present = sum(
        len(re.findall(r"heat_pump_optimizer_[a-z0-9_]+", text))
        for text in CORPUS.values()
    )
    R.check(
        "the reader corpus still documents entity ids (anchor)",
        ids_present > 0,
        f"{ids_present} id token(s) found",
    )
    offenders: dict[str, list[str]] = {}
    for name, text in CORPUS.items():
        hits = (
            _PREFIX_FOLLOWS_NAME.findall(text)
            + _CHANGE_PREFIX.findall(text)
            + _HAS_ENTITY_NAME_PREFIX.findall(text)
        )
        if hits:
            offenders[name] = hits
    R.check(
        "no reader doc claims the entity prefix follows the entry name",
        not offenders,
        repr(offenders),
    )


# ---------------------------------------------------------------------------
# Arm 4 -- README requirements claim vs manifest.json (D6-s1 / #1537)
# ---------------------------------------------------------------------------

def check_requirements_claim() -> None:
    R.section("README requirements vs manifest.json (#1537)")
    names = manifest_requirement_names()
    # Anchor: the manifest still pins requirements at all, and README still
    # has a Requirements section -- the absence of either side is itself red.
    R.check("manifest.json still pins requirements (anchor)", bool(names), repr(names))
    m = re.search(r"## Requirements\n(.*?)\n## ", README, re.S)
    section = m.group(1) if m else ""
    R.check("README still has a Requirements section (anchor)", bool(section))
    undocumented = [n for n in names if n.lower() not in section.lower()]
    R.check(
        "every manifest requirement is named in README's Requirements section",
        not undocumented,
        repr(undocumented),
    )


# ---------------------------------------------------------------------------
# Arm 5 -- Quick start step numbering: distinct, and diagram agrees with
# prose (D5-s1 / #1535, round 2)
# ---------------------------------------------------------------------------

# #1535 round 1 shifted four prose headings down by one to agree with the
# diagram's own numbered nodes, without noticing that the diagram's *menu*
# node (unnumbered by construction, since it has no matching prose-side
# label the finder's harness compares against) collided with the shifted
# "Temperatures" heading -- both read "3 ·" at that PR's head. The finder's
# own harness (s1_stepnum.py) cannot see this: it only compares a label that
# is numbered on BOTH sides, and "the finish menu" has no diagram-side
# numbered counterpart to compare against by construction. This arm adds the
# property that harness never checked: every prose heading number in the
# Quick start section is used exactly once.
_QS_DIAGRAM_NODE_RE = re.compile(r'[\[{]"(\d+)\s*\xb7\s*([^"<]+?)(?:<br/>|")')
_QS_PROSE_HEADING_RE = re.compile(r'^\*\*(\d+)\s*\xb7\s*([^*]+?)\.?\*\*', re.M)


def _qs_normalize(label: str) -> str:
    label = label.strip().rstrip(".?").lower()
    label = re.sub(r"[^a-z0-9 ]", "", label)
    return " ".join(label.split()[:3])


def _qs_extract(text: str) -> tuple[dict[str, int], dict[str, int], list[int]]:
    """(diagram label->number, prose label->number, prose numbers in order).

    The third element carries every prose heading's number, duplicates and
    all -- the first two dicts collapse repeats under `setdefault`, which is
    exactly the shape that hid #1535 round 1's duplicate "3 ·": two distinct
    labels sharing a number look like one entry per dict, so uniqueness has
    to be checked over the list, not the dicts.
    """
    section = text.split("## Quick start", 1)[1]
    section = section.split("\n## ", 1)[0]
    diagram: dict[str, int] = {}
    for m in _QS_DIAGRAM_NODE_RE.finditer(section):
        diagram.setdefault(_qs_normalize(m.group(2)), int(m.group(1)))
    prose: dict[str, int] = {}
    prose_numbers: list[int] = []
    for m in _QS_PROSE_HEADING_RE.finditer(section):
        num = int(m.group(1))
        prose.setdefault(_qs_normalize(m.group(2)), num)
        prose_numbers.append(num)
    return diagram, prose, prose_numbers


def _qs_duplicates(numbers: list[int]) -> list[int]:
    seen: set[int] = set()
    dupes: list[int] = []
    for n in numbers:
        if n in seen and n not in dupes:
            dupes.append(n)
        seen.add(n)
    return dupes


def check_quickstart_numbering() -> None:
    R.section("Quick start step numbering is distinct and diagram-agreed (#1535)")
    diagram, prose, prose_numbers = _qs_extract(README)
    # Anchor: the section still exists and still has several numbered
    # headings on both sides -- the absence of the claim's subject (an empty
    # section, or a Quick start rewritten with no numbered steps at all)
    # would otherwise read as a vacuous pass.
    R.check(
        "the Quick start section still has 5+ numbered prose headings and "
        "5+ numbered diagram nodes (anchor)",
        len(prose_numbers) >= 5 and len(diagram) >= 5,
        f"prose={prose_numbers!r} diagram={diagram!r}",
    )
    mismatches = [
        (label, dnum, prose[label])
        for label, dnum in diagram.items()
        if label in prose and prose[label] != dnum
    ]
    R.check(
        "every label numbered in both the diagram and the prose agrees on "
        "its number",
        not mismatches,
        repr(mismatches),
    )
    dupes = _qs_duplicates(prose_numbers)
    R.check(
        "every Quick start prose heading number is used exactly once (the "
        "property #1535 round 1's own fix broke: two headings both read "
        "'3 \xb7' at that PR's head)",
        not dupes,
        f"duplicated number(s) {dupes!r} in {prose_numbers!r}",
    )
    # Null control: the duplicate-check must actually fire on the shape it
    # exists to catch, not just on the (already-fixed) real README. Rebuild
    # round 1's own regression -- the untouched "finish menu" heading at 3,
    # colliding with a "Temperatures" heading shifted down to 3 as well --
    # as a synthetic section, and confirm the duplicate is detected there.
    _bad_section = (
        "## Quick start\n\n"
        "**1 \xb7 Basics.** x\n\n"
        "**2 \xb7 Optional sensors.** x\n\n"
        "**3 \xb7 The finish menu: Quick setup, Continue setup or Finish "
        "setup now.** x\n\n"
        "**3 \xb7 Temperatures.** x\n\n"
        "## Entities\n"
    )
    _bad_diagram, _bad_prose, _bad_numbers = _qs_extract(_bad_section)
    R.check(
        "the duplicate-number check fires on round 1's own regression "
        "(null control)",
        _qs_duplicates(_bad_numbers) == [3],
        f"got {_qs_duplicates(_bad_numbers)!r} from {_bad_numbers!r}",
    )
    # And the same synthetic section is clean once renumbered the way this
    # PR's round 2 fix renumbers the real README (menu keeps 3, the shifted
    # heading moves to 4 instead of colliding) -- the check must not flag a
    # section that is actually fine.
    _good_section = _bad_section.replace("**3 \xb7 Temperatures.**", "**4 \xb7 Temperatures.**")
    _, _, _good_numbers = _qs_extract(_good_section)
    R.check(
        "and does not fire on the corrected shape (null control, other arm)",
        _qs_duplicates(_good_numbers) == [],
        f"got {_qs_duplicates(_good_numbers)!r} from {_good_numbers!r}",
    )


# ---------------------------------------------------------------------------
# Arms 6 and 7 -- quality_scale.yaml censuses (#1545, #1546)
# ---------------------------------------------------------------------------

QUALITY_SCALE = (PKG / "quality_scale.yaml").read_text()
_PKG_TREES = {p.name: ast.parse(p.read_text(), str(p)) for p in sorted(PKG.glob("*.py"))}


def _rule_block(rule: str) -> str:
    """The yaml text of one quality-scale rule, through the next rule's key."""
    m = re.search(rf"^  {re.escape(rule)}:(.*?)(?=^  [a-z-]+:|\Z)", QUALITY_SCALE, re.M | re.S)
    return m.group(0) if m else ""


def _names_bare_entry(node: ast.AST | None) -> bool:
    """Whether an annotation mentions ``ConfigEntry`` rather than the typed alias.

    Walks the whole expression, so a union, an Optional and a subscript are
    seen as well as the bare name; a string annotation is parsed first.
    """
    if node is None:
        return False
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            node = ast.parse(node.value, mode="eval")
        except SyntaxError:
            return False
    return any(
        (isinstance(n, ast.Name) and n.id == "ConfigEntry")
        or (isinstance(n, ast.Attribute) and n.attr == "ConfigEntry")
        for n in ast.walk(node)
    )


def bare_entry_annotations(trees: dict[str, ast.Module] | None = None) -> list[str]:
    """Every parameter, return and variable annotation naming the bare ConfigEntry."""
    hits: list[str] = []
    for name, tree in (_PKG_TREES if trees is None else trees).items():
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                a = node.args
                for arg in a.posonlyargs + a.args + a.kwonlyargs + [a.vararg, a.kwarg]:
                    if arg is not None and _names_bare_entry(arg.annotation):
                        hits.append(f"{name}:{node.lineno} {node.name}({arg.arg})")
                if _names_bare_entry(node.returns):
                    hits.append(f"{name}:{node.lineno} {node.name} -> return")
            elif isinstance(node, ast.AnnAssign) and _names_bare_entry(node.annotation):
                hits.append(f"{name}:{node.lineno} {ast.unparse(node.target)}")
    return hits


_EXC_FAMILY = {
    "HomeAssistantError", "ServiceValidationError", "IntegrationError",
    "ConfigEntryError", "ConfigEntryNotReady", "ConfigEntryAuthFailed",
    "UpdateFailed",
}


def _callee(call: ast.AST) -> str | None:
    if not isinstance(call, ast.Call):
        return None
    f = call.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None


def _translated(call: ast.Call) -> bool:
    return {"translation_domain", "translation_key"} <= {kw.arg for kw in call.keywords}


def exception_helpers(trees: dict[str, ast.Module] | None = None) -> dict[str, int]:
    """Key-forwarding raise helpers: name -> the position of their key parameter.

    #1546 routed the coordinator's UpdateFailed raises through one helper, so
    the census counts each CALL of a helper as a site rather than losing it.
    A helper is a module-level function in which every family exception it
    builds is translated and takes ``translation_key`` from one of its own
    parameters; any other function's family calls are counted where they are.
    """
    out: dict[str, int] = {}
    for tree in (_PKG_TREES if trees is None else trees).values():
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            params = [a.arg for a in node.args.posonlyargs + node.args.args]
            built = [c for c in ast.walk(node) if _callee(c) in _EXC_FAMILY]
            fwd = {
                kw.value.id
                for c in built
                for kw in c.keywords
                if kw.arg == "translation_key" and isinstance(kw.value, ast.Name)
            }
            if built and all(_translated(c) for c in built) and len(fwd) == 1 and fwd <= set(params):
                out[node.name] = params.index(fwd.pop())
    return out


def exception_raise_census(
    trees: dict[str, ast.Module] | None = None,
) -> tuple[int, list[str], set[str]]:
    """(exception sites, the untranslated ones, the translation keys they name).

    A site is every construction of a family exception outside a helper,
    every call of a helper, and every ``raise`` of a bare family class --
    construction rather than ``raise``, so an error built into a variable
    first, or returned by a factory, is still counted.
    """
    trees = _PKG_TREES if trees is None else trees
    helpers = exception_helpers(trees)
    total, missing, keys = 0, [], set()
    for name, tree in trees.items():
        inside = {
            id(n)
            for f in tree.body
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name in helpers
            for n in ast.walk(f)
        }
        for node in ast.walk(tree):
            where = f"{name}:{getattr(node, 'lineno', 0)}"
            callee = _callee(node)
            key: ast.AST | None = None
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Name) and node.exc.id in _EXC_FAMILY:
                total += 1
                missing.append(f"{where} {node.exc.id} (no call)")
            elif callee in _EXC_FAMILY and id(node) not in inside:
                total += 1
                if not _translated(node):
                    missing.append(f"{where} {callee}")
                key = next((kw.value for kw in node.keywords if kw.arg == "translation_key"), None)
            elif callee in helpers:
                total += 1
                pos = helpers[callee]
                key = node.args[pos] if len(node.args) > pos else None
                if key is None:
                    missing.append(f"{where} {callee}() names no key")
            if key is not None:
                keys.add(key.value if isinstance(key, ast.Constant) else f"<{where}>")
    return total, missing, keys


# Self-test fixtures: synthetic modules with every defect shape the censuses
# must see, and a clean module they must pass. A census that matched nothing,
# or read every raise as translated, would leave the real tree's arms green
# (the #1590 review measured both), so each census is held to exact results
# on these every run. _RAISE_BAD's two extra helpers pin the helper rule: a
# key-forwarding helper that omits the domain is not a helper (its own raise
# is refused), and a helper's key may be any positional parameter.
_TYPING_BAD = """
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
def name_param(entry: ConfigEntry) -> None: ...
def attr_param(entry: config_entries.ConfigEntry) -> None: ...
def posonly(entry: ConfigEntry, /) -> None: ...
def kwonly(*, entry: ConfigEntry[X]) -> None: ...
def star(*entries: ConfigEntry, **named: ConfigEntry) -> None: ...
def union_return(n: int) -> config_entries.ConfigEntry | None: ...
def stringly(entry: "ConfigEntry") -> None: ...
async def coroutine(entry: ConfigEntry) -> None: ...
class Flow:
    def __init__(self) -> None:
        self.entry: config_entries.ConfigEntry | None = None
"""
_TYPING_BAD_HITS = [
    "m.py:4 name_param(entry)",
    "m.py:5 attr_param(entry)",
    "m.py:6 posonly(entry)",
    "m.py:7 kwonly(entry)",
    "m.py:8 star(entries)",
    "m.py:8 star(named)",
    "m.py:9 union_return -> return",
    "m.py:10 stringly(entry)",
    "m.py:11 coroutine(entry)",
    "m.py:14 self.entry",
]
_TYPING_CLEAN = """
def ok(entry: HeatPumpOptimizerConfigEntry, n: int, /, *a: str, k: ConfigEntryX = None) -> HeatPumpOptimizerConfigEntry: ...
x: "HeatPumpOptimizerConfigEntry | None" = None
"""
_RAISE_BAD = """
def _raise_helper(key, message, cause=None, **ph):
    raise UpdateFailed(message, translation_domain=DOMAIN, translation_key=key) from cause
def _literal_key(message):
    return HomeAssistantError(message, translation_domain=DOMAIN, translation_key="lit")
def _untranslated_factory(message):
    return UpdateFailed(message)
def _half_helper(key, message):
    raise UpdateFailed(message, translation_key=key)
def _second_key(message, key):
    raise HomeAssistantError(message, translation_domain=DOMAIN, translation_key=key)
def sites():
    raise UpdateFailed("x")
    raise ServiceValidationError(translation_domain=DOMAIN)
    raise ServiceValidationError(translation_key="k1")
    raise exceptions.HomeAssistantError("y", translation_domain=DOMAIN, translation_key="k2")
    raise ConfigEntryNotReady
    _raise_helper("k3", "m")
    _raise_helper(key="k4", message="m")
    _half_helper("k5", "m")
    _second_key("m", "k6")
    raise ValueError("not in the family")
"""
_RAISE_BAD_RESULT = (
    11,
    [
        "m.py:7 UpdateFailed",
        "m.py:9 UpdateFailed",
        "m.py:13 UpdateFailed",
        "m.py:14 ServiceValidationError",
        "m.py:15 ServiceValidationError",
        "m.py:17 ConfigEntryNotReady (no call)",
        "m.py:19 _raise_helper() names no key",
    ],
    {"lit", "<m.py:9>", "k1", "k2", "k3", "k6"},
)
_RAISE_CLEAN = """
def _raise_helper(key, message):
    raise UpdateFailed(message, translation_domain=DOMAIN, translation_key=key)
def sites():
    raise ServiceValidationError(translation_domain=DOMAIN, translation_key="a")
    raise exceptions.UpdateFailed(translation_domain=DOMAIN, translation_key="b")
    _raise_helper("c", "m")
    raise ValueError("not in the family")
"""


def _fixture(src: str) -> dict[str, ast.Module]:
    return {"m.py": ast.parse(src)}


def check_census_self_test() -> None:
    """Hold both censuses to exact results on the synthetic fixtures above."""
    R.section("quality_scale census self-test (#1545, #1546)")
    hits = bare_entry_annotations(_fixture(_TYPING_BAD))
    R.check(
        "the typing census finds every bare ConfigEntry shape, and only those",
        hits == _TYPING_BAD_HITS,
        f"got {hits}",
    )
    clean = bare_entry_annotations(_fixture(_TYPING_CLEAN))
    R.check("the typing census passes the alias and look-alike names (null control)", clean == [], repr(clean))
    total, missing, keys = exception_raise_census(_fixture(_RAISE_BAD))
    R.check(
        "the exception census counts every site, refuses each untranslated one, and reads each key",
        (total, sorted(missing), keys) == (_RAISE_BAD_RESULT[0], sorted(_RAISE_BAD_RESULT[1]), _RAISE_BAD_RESULT[2]),
        f"got {(total, sorted(missing), sorted(keys))}",
    )
    R.check(
        "the exception census passes a translated module (null control)",
        exception_raise_census(_fixture(_RAISE_CLEAN)) == (3, [], {"a", "b", "c"}),
        repr(exception_raise_census(_fixture(_RAISE_CLEAN))),
    )


def _exception_keys(path: pathlib.Path) -> set[str]:
    return set(json.loads(path.read_text()).get("exceptions", {}))


def check_quality_scale() -> None:
    R.section("quality_scale.yaml censuses (#1545, #1546)")
    typing_rule = _rule_block("strict-typing")
    claimed = re.search(r"qs_entry_param_bare=(\d+)", typing_rule)
    # Anchor: the claim is where the check reads it; a reworded comment is red.
    R.check("strict-typing states qs_entry_param_bare (anchor)", claimed is not None, typing_rule[:200])
    bare = bare_entry_annotations()
    R.check(
        "qs_entry_param_bare in quality_scale.yaml equals the annotation census",
        claimed is not None and int(claimed.group(1)) == len(bare),
        f"claimed {claimed.group(1) if claimed else None}, census {len(bare)}: {bare}",
    )
    # The census itself is held to exact results by check_census_self_test.

    status = _rule_block("exception-translations").split(":", 1)[1]
    done = re.match(r"\s*(?:status:\s*)?done\b", status) is not None
    R.check("quality_scale.yaml marks exception-translations done (anchor)", done, status[:80])
    total, missing, keys = exception_raise_census()
    R.check("the census finds exception sites (anchor)", total > 0, f"{total} site(s)")
    R.check(
        "every exception site carries translation_domain and translation_key",
        not missing,
        f"{len(missing)} of {total}: {missing}",
    )
    for label, path in (
        ("strings.json", PKG / "strings.json"),
        ("translations/en.json", PKG / "translations" / "en.json"),
        ("translations/sv.json", PKG / "translations" / "sv.json"),
    ):
        absent = sorted(keys - _exception_keys(path))
        R.check(f"{label} has an exceptions entry for every raised key", not absent, repr(absent))


# ---------------------------------------------------------------------------
# I5 class barrier (round 9): five shape-agnostic arms. Each derives its claim
# set from a whole corpus and its fact set from code, so a new sentence,
# table row or comment of the shape joins the check the moment it lands; none
# is keyed to a round-9 sentence. Every arm carries an anchor.
# ---------------------------------------------------------------------------

def entity_census(extra: dict) -> list[dict]:
    """Every entity the platforms' real ``async_setup_entry`` add for an entry."""
    import asyncio
    import importlib

    import heatpump_optimizer as integ
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer import const
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    names = json.loads((PKG / "strings.json").read_text())["entity"]
    cfg = {const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home", **extra}
    hass, entry = FakeHass(), FakeEntry(data=cfg)
    entry.runtime_data = HeatPumpOptimizerCoordinator(hass, entry)
    out: list[dict] = []
    for plat in integ.PLATFORM_LIST:
        added: list = []
        mod = importlib.import_module(f"heatpump_optimizer.{plat}")
        asyncio.run(mod.async_setup_entry(hass, entry, lambda e, *a, **k: added.extend(e)))
        for e in added:
            key = getattr(e, "_attr_translation_key", None)
            out.append({
                "platform": str(plat),
                "name": names.get(str(plat), {}).get(key, {}).get("name", f"<{plat}:{key}>"),
                "enabled": getattr(e, "entity_registry_enabled_default", True),
                "options": set(getattr(e, "_attr_options", None) or ()) - {"unknown"},
            })
    return out


_HEADS = {"Sensors": "sensor", "Binary Sensors": "binary_sensor", "Buttons": "button",
          "Switches": "switch"}


def check_entity_prose() -> None:
    R.section("entity prose vs the constructed entity set (I5)")
    from heatpump_optimizer import const

    with_dhw = entity_census({const.CONF_DHW_TANK_VOLUME: 200.0})
    bare = entity_census({})
    R.check("the census constructs entities (anchor)", len(with_dhw) > 0 and len(bare) > 0)
    total = len(with_dhw)
    counts = [(n, int(m.group(1))) for n, text in CORPUS.items()
              for m in re.finditer(r"\b(\d{2,3}) entities\b", text)]
    R.check("the corpus states an entity count (anchor)", bool(counts))
    R.check("every '<N> entities' in the corpus equals the constructed total",
            all(v == total for _, v in counts), f"total {total}: {counts}")
    heads = [(h, int(n)) for h, n in re.findall(r"^### (.+?) \((\d+) total\)", README, re.M)
             if h in _HEADS]
    per = {p: sum(1 for e in with_dhw if e["platform"] == p) for p in _HEADS.values()}
    R.check("README states per-platform totals (anchor)", bool(heads))
    R.check("every README '### <platform> (N total)' equals that platform's count",
            all(per[_HEADS[h]] == n for h, n in heads), f"{heads} vs {per}")
    rows = {}
    for line in README.splitlines():
        if line.startswith("| ") and line.count("|") >= 4:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.setdefault(cells[0], " ".join(cells[1:]))
    listed = []
    omitted = {}
    for e in with_dhw:
        named = set(re.findall(r"`(\w+)`", rows.get(e["name"], "")))
        if e["options"] and named & e["options"]:
            listed.append(e["name"])
            if e["options"] - named:
                omitted[e["name"]] = sorted(e["options"] - named)
    R.check("README lists an enum entity's states (anchor)", bool(listed))
    R.check("every README row that lists an enum entity's states lists all of them",
            not omitted, repr(omitted))
    m = re.search(r"Disabled by default: (.*?)\.\n", README, re.S)
    R.check("README keeps its 'Disabled by default:' list (anchor)", m is not None)
    census_list = {x.strip() for x in re.split(r",| and ", m.group(1).replace("\n", " "))} if m else set()
    prose = " ".join(l for l in README.splitlines() if not l.startswith("|"))
    sentences = [s for s in re.split(r"(?<=\.)\s", prose) if "disabled by default" in s.lower()]

    def documented(name: str) -> bool:
        return (name in census_list or "disabled by default" in rows.get(name, "").lower()
                or any(name in s for s in sentences))

    undoc = sorted(e["name"] for e in bare if not e["enabled"] and not documented(e["name"]))
    R.check("every entity a no-hot-water install disables is documented as disabled",
            not undoc, repr(undoc))


CARD = PKG / "www" / "heatpump-optimizer-card.js"
_TICKED_PRIVATE = re.compile(r"`(?:this\.)?(_[A-Za-z][\w$]*)(?:\(\))?`")


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z_$][\w$]*", text))


def check_private_mentions() -> None:
    R.section("backticked private names in the card resolve (I5)")
    src = CARD.read_text()
    cited = set(_TICKED_PRIVATE.findall(src))
    R.check("the card's comments cite private names (anchor)", bool(cited), f"{len(cited)}")
    known = _tokens(_TICKED_PRIVATE.sub(" ", src))
    for path in sorted(PKG.rglob("*")):
        if path.suffix in (".py", ".json", ".yaml") and "__pycache__" not in path.parts:
            known |= _tokens(path.read_text())
    stale = sorted(n for n in cited if n not in known)
    R.check("every backticked private name in the card names something that exists",
            not stale, repr(stale))


_BARE_UNIT = re.compile(r"(\d) C\b|\bm2\b")


def check_unit_typography() -> None:
    R.section("translated text writes units as the selectors do (I5)")
    hits: list[str] = []
    leaves = 0
    for rel in ("strings.json", "translations/en.json", "translations/sv.json"):
        stack = [((rel,), json.loads((PKG / rel).read_text()))]
        while stack:
            path, node = stack.pop()
            if isinstance(node, dict):
                stack.extend((path + (k,), v) for k, v in node.items())
            elif isinstance(node, str):
                leaves += 1
                if _BARE_UNIT.search(node):
                    hits.append(".".join(path))
    R.check("the catalogs carry text (anchor)", leaves > 0, f"{leaves} leaves")
    R.check("no translated string writes '<n> C' or 'm2' for °C / m²", not hits, repr(sorted(hits)))


def registered_service_fields() -> dict[str, set[str]]:
    """Service name -> the keys its registered voluptuous schema accepts."""
    from harness import FakeHass
    from heatpump_optimizer import services

    hass = FakeHass()
    services.async_register_services(hass)
    out: dict[str, set[str]] = {}
    for (_, name), schema in hass.services._schemas.items():
        while schema is not None and not hasattr(schema, "schema"):
            schema = next((v for v in getattr(schema, "validators", ()) if hasattr(v, "schema")), None)
        out[name] = {str(getattr(k, "schema", k)) for k in (schema.schema if schema else {})}
    return out


def check_service_fields() -> None:
    R.section("service paragraphs vs the registered schemas (I5)")
    doc = DOCS["configuration.md"]
    fields = registered_service_fields()
    paras = {m.group(1): m.group(2) for m in
             re.finditer(r"^\*\*`(\w+)`\*\*(.*?)(?=^\*\*`\w+`\*\*|^#|\Z)", doc, re.M | re.S)}
    R.check("the registry and the Services paragraphs are both there (anchor)",
            bool(fields) and bool(set(fields) & set(paras)), f"{sorted(fields)} / {sorted(paras)}")
    wrong = {}
    for name, keys in fields.items():
        text = paras.get(name)
        if text is None:
            continue
        stated = re.search(r"\b(?:All )?(\d+) fields\b", text)
        named = set(re.findall(r"`(\w+)`", text)) & keys
        if stated and int(stated.group(1)) != len(keys - {"entry_id"}):
            wrong[name] = f"says {stated.group(1)} fields, schema has {len(keys - {'entry_id'})}"
        elif not stated and len(named) > 1 and keys - named - {"entry_id"}:
            wrong[name] = f"lists {len(named)}, omits {sorted(keys - named - {'entry_id'})}"
    R.check("every service paragraph that lists or counts fields matches its schema",
            not wrong, repr(wrong))


def _label(s: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", " ", s).strip().strip("*`").strip().lower()


_LABEL_END = r"(?:temperature|sensor|source|switch|entity|enabled|mode|control|feedback|experiment|cycle|limit)"


def check_option_labels() -> None:
    R.section("option fields the docs name are fields the forms show (I5)")
    en = json.loads((PKG / "translations" / "en.json").read_text())
    steps = en["options"]["step"]
    menu = {v: k for s in ("init", "advanced") for k, v in steps[s]["menu_options"].items()}

    def labels(node, out):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "data" and isinstance(v, dict):
                    out |= {_label(x) for x in v.values() if isinstance(x, str)}
                labels(v, out)
        return out

    every: set[str] = set()
    stack = [en]
    while stack:
        n = stack.pop()
        if isinstance(n, dict):
            stack.extend(n.values())
        elif isinstance(n, str):
            every.add(_label(n))
    rows, bad = 0, []
    for name, text in CORPUS.items():
        page = hdr = None
        for line in text.splitlines():
            if (m := re.match(r"^###\s+(.*)", line)):
                page, hdr = m.group(1).strip(), None
            elif line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if hdr is None:
                    hdr = cells
                elif (hdr[0] == "Setting" and page in menu and not set(line) <= set("|-: ")
                      and not re.search(r" / |, |^The |Monday", cells[0])):
                    rows += 1
                    if _label(cells[0]) not in labels(steps.get(menu[page], {}), set()):
                        bad.append(f"{name} '{page}': {cells[0]}")
            else:
                hdr = None
            for m in re.finditer(r"(?<![*\w])\*([A-Z][^*\n]{3,70}?" + _LABEL_END + r")\*(?!\*)", line):
                if not m.group(1).startswith("HP ") and _label(m.group(1)) not in every:
                    bad.append(f"{name}: *{m.group(1)}*")
    R.check("the docs tabulate options-page fields (anchor)", rows > 0, f"{rows} rows")
    R.check("every options field the docs name is a label the forms render", not bad, repr(bad))


def main() -> int:
    check_figures()
    check_ecl110_defaults()
    check_entity_prefix()
    check_requirements_claim()
    check_quickstart_numbering()
    check_census_self_test()
    check_quality_scale()
    check_entity_prose()
    check_private_mentions()
    check_unit_typography()
    check_service_fields()
    check_option_labels()
    return R.close("checks")


if __name__ == "__main__":
    raise SystemExit(main())
