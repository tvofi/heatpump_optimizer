#!/usr/bin/env python3
"""#1413: derive the claim set from the documents and the fact set from code.

The round-6 stale-prose class (CONDENSED.md section 6): a reader doc asserts a
fact about shipped code that the code no longer makes, and the only
doc-vs-code machinery is keyed to claims someone hand-enumerated -- so a newly
written sentence escapes until a later round names it. This check derives BOTH
sides for three claim shapes, and fails closed on a contradiction:

  * generated-figure freshness    -- D5-01 #1389 (marginal-cop.svg predates the
    #928 resistive clamp)
  * ECL110 topic shipped defaults -- D6-01 #1391 (README tells users to clear
    topics that ship empty)
  * entity object-id prefix       -- D6-03 #1393 (docs say the prefix follows
    the entry name; the code pins a hard-coded literal)

The fact set is derived by importing and executing production code; the claim
set is derived by scanning the reader documents and the shipped blueprints.
Neither side is a hand-maintained enumeration: a new sentence of the same shape
enters the check the moment it lands.

Every arm carries an anchor (null control): the absence of the claim's subject
is itself red, so the check cannot go green by skipping.

RUN (from the repository root, never elsewhere):
    PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py
"""
from __future__ import annotations

import importlib.util
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


def main() -> int:
    check_figures()
    check_ecl110_defaults()
    check_entity_prefix()
    check_requirements_claim()
    check_quickstart_numbering()
    return R.close("checks")


if __name__ == "__main__":
    raise SystemExit(main())
