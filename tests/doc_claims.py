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
# Round 9 F8.1 (#1645, class I5) -- configuration.md "Initial setup" against
# the real ConfigFlow, and the simulate_plan field list against its schema.
# D5-s1-01 / D6-s2-01 / D6-s2-02: the section documented the pre-v6.6.5
# straight-line wizard -- no finish_setup menu, the Tibber token marked
# unconditionally required, and a stale entity count. D6-s2-05: the
# simulate_plan prose field list did not name the wood fields the schema
# grew.
# ---------------------------------------------------------------------------


def check_initial_setup_menu() -> None:
    R.section(
        "Initial setup: the finish_setup menu and the token requirement "
        "(#1645 D5-s1-01)"
    )
    import asyncio

    from harness import FakeHass
    from heatpump_optimizer import config_flow, const

    text = DOCS["configuration.md"]
    section = _section(text, "## Initial setup", "\n## ", "configuration.md")
    if section is None:
        return

    async def _first_two_screens():
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        first = await flow.async_step_user(
            {
                "name": "Heat Pump Optimizer",
                const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
                const.CONF_PRICE_ENTITY: "sensor.nordpool",
                const.CONF_WEATHER_ENTITY: "weather.home",
            }
        )
        second = await flow.async_step_user_sensors({})
        return first, second

    first, second = asyncio.run(_first_two_screens())
    R.check(
        "the first screen accepts a price entity with no Tibber token (anchor)",
        first.get("step_id") == "user_sensors" and not first.get("errors"),
        repr(first),
    )
    menu = dict(second.get("menu_options") or {})
    R.check(
        "async_step_finish_setup still shows a menu with these three options "
        "(anchor)",
        set(menu) == {"quick_setup", "temperature", "finish_now"},
        repr(menu),
    )
    unnamed = [
        label
        for label in menu.values()
        if re.sub(r"\s*\(.*?\)", "", label).lower() not in section.lower()
    ]
    R.check(
        "every finish_setup menu option is named in the 'Initial setup' "
        "section (D5-s1-01: the section drew the pre-v6.6.5 wizard, which "
        "had no such menu)",
        not unnamed,
        f"menu={menu}, unnamed in section: {unnamed}",
    )
    token_required_claim = bool(
        re.search(r"Tibber API token \| — \(\*\*required\*\*\)", section)
    ) or "genuinely required: a tibber api token" in text.lower()
    R.check(
        "the section does not claim the Tibber token is unconditionally "
        "required, now that a price-entity source clears the first screen "
        "without one (D5-s1-01)",
        not token_required_claim,
        "token-required claim still present" if token_required_claim else "ok",
    )
    # Null control: the pre-v6.6.5 shape (no menu, token always required) is
    # exactly what setup_section.py's --perturb arm re-creates, and it is
    # what this check is written to catch.
    _bad_section = (
        "**Settings → Devices & services → Add integration → Heat Pump "
        "Optimizer.**\n\n"
        "| Setting | Default | What it means |\n"
        "|---|---|---|\n"
        "| Tibber API token | — (**required**) | Reads your hourly "
        "electricity prices. |\n"
    )
    _bad_unnamed = [
        label
        for label in menu.values()
        if re.sub(r"\s*\(.*?\)", "", label).lower() not in _bad_section.lower()
    ]
    _bad_token_claim = bool(
        re.search(r"Tibber API token \| — \(\*\*required\*\*\)", _bad_section)
    )
    R.check(
        "the check fires on the pre-v6.6.5 shape it was written for (null "
        "control)",
        bool(_bad_unnamed) and _bad_token_claim,
        f"unnamed={_bad_unnamed} token_claim={_bad_token_claim}",
    )


def check_simulate_plan_fields() -> None:
    R.section(
        "simulate_plan's documented field list matches its schema "
        "(#1645 D6-s2-05)"
    )
    from heatpump_optimizer.services import SERVICE_SCHEMA_SIMULATE_PLAN

    schema_fields = {
        str(getattr(key, "schema", key)) for key in SERVICE_SCHEMA_SIMULATE_PLAN.schema
    }
    R.check(
        "the simulate_plan schema still has fields to document (anchor)",
        bool(schema_fields),
        repr(schema_fields),
    )
    text = DOCS["configuration.md"]
    m = re.search(
        r"\*\*`simulate_plan`\*\*.*?Fields,\s*\n?all optional:\s*(.*?)\.\s*An empty",
        text,
        re.S,
    )
    R.check(
        "configuration.md still documents simulate_plan's field list (anchor)",
        m is not None,
    )
    if m is None:
        return
    documented = set(re.findall(r"`([a-z0-9_]+)`", m.group(1)))
    missing = schema_fields - documented
    R.check(
        "configuration.md's simulate_plan field list names every schema "
        "field, including the wood fields the schema grew without the "
        "prose following (D6-s2-05)",
        not missing,
        f"schema={sorted(schema_fields)} documented={sorted(documented)} "
        f"missing={sorted(missing)}",
    )
    # Null control: re-run the SAME extraction regex on a mutated copy of the
    # actual doc text with one real, currently-documented field's backtick
    # literal deleted from the simulate_plan sentence, and confirm the
    # missing-field check fires on that mutation -- not on set algebra that
    # cannot fail regardless of whether the regex extraction works at all.
    if not schema_fields & documented:
        return
    _dropped = sorted(schema_fields & documented)[0]
    _mutated_text = text.replace(m.group(0), m.group(0).replace(f"`{_dropped}`", ""), 1)
    _mutated_span = re.search(
        r"\*\*`simulate_plan`\*\*.*?Fields,\s*\n?all optional:\s*(.*?)\.\s*An empty",
        _mutated_text,
        re.S,
    )
    _mutated_documented = (
        set(re.findall(r"`([a-z0-9_]+)`", _mutated_span.group(1))) if _mutated_span else set()
    )
    _synthetic_missing = schema_fields - _mutated_documented
    R.check(
        "the missing-field check fires when a field is undocumented (null "
        "control)",
        _dropped in _synthetic_missing,
        f"dropped={_dropped!r} synthetic missing={sorted(_synthetic_missing)}",
    )


def _section(text: str, start: str, end: str, where: str) -> str | None:
    """The text between ``start`` and the next ``end``, or None after a named FAIL.

    An anchor a doc rewrite moves must fail as a check, not abort the run with
    an IndexError that hides every other arm's result (carry-1645.json).
    """
    parts = text.split(start, 1)
    R.check(f"{where} still has {start.strip()!r} (anchor)", len(parts) == 2)
    return parts[1].split(end, 1)[0] if len(parts) == 2 else None


# ---------------------------------------------------------------------------
# Round 9 F8.2 (#1645, class I5) -- field labels the options forms do not
# show, the two-zone split's options-page placement, the Heat Pump Action
# state list, and the disabled-by-default census on a no-hot-water install.
# D5-s1-05 / D6-s1-02: configuration.md and README.md named fields by labels
# the options forms do not use, and put the two-zone split and the solar
# orientation factor on the wrong options page. D6-s1-01: the Heat Pump
# Action sensor also publishes idle and system_identification, which
# README's state list omitted. D6-s1-03: README's disabled-by-default census
# assumed hot water is configured, and omitted the six DHW entities a
# no-hot-water install also disables.
# ---------------------------------------------------------------------------

_EN_STRINGS = json.loads((PKG / "translations" / "en.json").read_text())


def check_two_zone_field_labels_and_placement() -> None:
    R.section(
        "Two-zone field labels and options-page placement "
        "(#1645 D5-s1-05, D6-s1-02)"
    )
    zones_sections = _EN_STRINGS["options"]["step"]["thermal_model_zones"]["sections"]
    inter_zone_label = zones_sections["zones"]["data"]["inter_zone_heat_transfer"]
    radiator_label = zones_sections["split"]["data"]["radiator_power_fraction"]
    floor_return_label = (
        _EN_STRINGS["options"]["step"]["entities"]["sections"]["plant"]["data"][
            "floor_return_temp_entity"
        ]
    )
    solar_source_label = (
        _EN_STRINGS["options"]["step"]["entities_metering"]["sections"]["solar"][
            "data"
        ]["solar_forecast_source"]
    )
    # Anchor: the labels this check pins still exist and are non-empty.
    R.check(
        "the four labels this check pins are still non-empty strings "
        "(anchor)",
        all(
            isinstance(s, str) and s
            for s in (inter_zone_label, radiator_label, floor_return_label, solar_source_label)
        ),
        repr((inter_zone_label, radiator_label, floor_return_label, solar_source_label)),
    )
    config_text = DOCS["configuration.md"]
    howitworks_text = DOCS["how-it-works.md"]
    zones_section = _section(config_text, "### Two-zone model", "\n### ", "configuration.md") or ""
    R.check(
        "configuration.md's Two-zone model table names the inter-zone "
        "transfer field by its actual options-form label, not a paraphrase "
        "(D5-s1-05)",
        f"| {inter_zone_label} |" in zones_section,
        zones_section[:400],
    )
    R.check(
        "...and the radiator-power-fraction field likewise (D5-s1-05)",
        f"| {radiator_label} |" in zones_section,
        zones_section[:400],
    )
    R.check(
        "configuration.md's mixing-valve note cites the floor-return probe "
        "by its actual options-form label (D5-s1-05)",
        f"*{floor_return_label}*" in config_text,
        "not found" if f"*{floor_return_label}*" not in config_text else "ok",
    )
    R.check(
        "how-it-works.md's weather section cites the solar-source field by "
        "its actual options-form label (D5-s1-05)",
        f"*{solar_source_label}*" in howitworks_text,
        "not found" if f"*{solar_source_label}*" not in howitworks_text else "ok",
    )

    # Page placement (D6-s1-02): derive each field's real options step from
    # config_flow._OPTION_FIELDS, the same artifact the finder's claims.py
    # reads, and check README's placement paragraph names that step for the
    # two-zone split and the orientation factor rather than Thermal model
    # (expert) or Building type and emitters.
    from heatpump_optimizer import config_flow, const

    step_title = {
        name: step.get("title")
        for name, step in _EN_STRINGS["options"]["step"].items()
    }
    fields_by_key = {row.key: row.step for row in config_flow._OPTION_FIELDS}
    two_zone_page = step_title[fields_by_key[const.CONF_INTER_ZONE_TRANSFER]]
    radiator_page = step_title[fields_by_key[const.CONF_RADIATOR_POWER_FRACTION]]
    orientation_page = step_title[fields_by_key[const.CONF_SOLAR_ORIENTATION_FACTOR]]
    thermal_expert_page = step_title["thermal_model"]
    R.check(
        "the two-zone split and the orientation factor are in fact one "
        "options page (anchor)",
        two_zone_page == radiator_page == orientation_page,
        repr((two_zone_page, radiator_page, orientation_page)),
    )
    readme_para = _section(README, "Both paths land on the same model", "\n\n", "README.md") or ""
    R.check(
        "README's page-placement paragraph names the two-zone split's real "
        "options page (D6-s1-02)",
        two_zone_page in readme_para,
        readme_para,
    )
    R.check(
        "...and does not claim the two-zone split lives on Thermal model "
        "(expert), which holds only the single-zone fields (D6-s1-02)",
        f"two-zone split\nand the power limits are on **Advanced settings → {thermal_expert_page}**" not in readme_para
        and not re.search(
            r"two-zone split[^.]*\*\*[^*]*" + re.escape(thermal_expert_page), readme_para
        ),
        readme_para,
    )
    # Null control: the historical (wrong) claim -- masses, losses, the
    # two-zone split and the power limits all on Thermal model (expert) --
    # is exactly what D6-s1-02 measured at baseline; confirm both checks
    # above fire against it.
    _bad_para = (
        " and every value either one sets can be edited afterwards. The "
        "masses, losses, the two-zone split and the power limits are on "
        f"**Advanced settings → {thermal_expert_page}**; buffer tank volume "
        "is on **Heating system and heat storage**."
    )
    R.check(
        "the placement checks fire on the baseline (wrong) claim (null "
        "control)",
        two_zone_page not in _bad_para
        and re.search(r"two-zone split[^.]*\*\*[^*]*" + re.escape(thermal_expert_page), _bad_para),
        _bad_para,
    )


def check_heat_pump_action_states() -> None:
    R.section("Heat Pump Action state list matches the sensor (#1645 D6-s1-01)")
    from heatpump_optimizer import const

    states = const.HEAT_PUMP_ACTION_STATES
    R.check(
        "HEAT_PUMP_ACTION_STATES still has 'unknown' as its no-data "
        "fallback and at least eight real states (anchor)",
        "unknown" in states and len(states) >= 9,
        repr(states),
    )
    row = next(
        line for line in README.splitlines() if line.startswith("| Heat Pump Action |")
    )
    named = {s for s in states if s != "unknown" and f"`{s}`" in row}
    missing = sorted(set(states) - {"unknown"} - named)
    R.check(
        "README's Heat Pump Action row names every state "
        "HEAT_PUMP_ACTION_STATES lists except the no-data fallback "
        "'unknown' (D6-s1-01: idle and system_identification were "
        "omitted)",
        not missing,
        f"row={row!r} missing={missing}",
    )
    # Null control: the pre-fix row (idle and system_identification absent)
    # is exactly the D6-s1-01 baseline shape.
    _bad_row = (
        "| Heat Pump Action | — | What the plan is doing now: `off` "
        "(neither circuit runs), `hot_water` (only the tank heats), "
        "`eco`, `normal`, `pre_heat` or `boost`, and `comfort` while "
        "comfort mode holds | |"
    )
    _bad_missing = sorted(
        s for s in states if s != "unknown" and f"`{s}`" not in _bad_row
    )
    R.check(
        "the row check fires on the pre-fix row (null control)",
        set(_bad_missing) == {"idle", "system_identification"},
        repr(_bad_missing),
    )


def check_disabled_by_default_without_hot_water() -> None:
    R.section(
        "Disabled-by-default census covers a no-hot-water install too "
        "(#1645 D6-s1-03)"
    )
    import asyncio

    from harness import FakeEntry, FakeHass
    from heatpump_optimizer import const
    import heatpump_optimizer as integ
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    def census(extra):
        hass, entry = FakeHass(), FakeEntry(
            data={const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home", **extra}
        )
        coord = HeatPumpOptimizerCoordinator(hass, entry)
        entry.runtime_data = coord
        out = []
        for platform in integ.PLATFORM_LIST:
            mod = importlib.import_module(f"heatpump_optimizer.{platform}")
            added: list = []
            asyncio.run(
                mod.async_setup_entry(hass, entry, lambda e, *a, **k: added.extend(e))
            )
            for e in added:
                key = getattr(e, "_attr_translation_key", None)
                default = getattr(
                    e,
                    "entity_registry_enabled_default",
                    getattr(e, "_attr_entity_registry_enabled_default", True),
                )
                out.append((str(platform), key, bool(default)))
        return out

    no_hot_water = census({})
    R.check(
        "a Finish-setup-now install (no hot water) still constructs "
        "entities to census (anchor)",
        bool(no_hot_water),
        f"{len(no_hot_water)} entities",
    )
    disabled_keys = {key for _plat, key, default in no_hot_water if not default and key}
    # The six DHW entities gated on has_hot_water() alone (no separate
    # probe), per entity.DHWEntityMixin and F8.2's carry note.
    dhw_only_keys = {
        "dhw_cost", "dhw_energy", "dhw_heating_cost",
        "dhw_heating_schedule", "dhw_setpoint_advisor", "plan_dhw_heating",
    }
    present = {k for k in dhw_only_keys if k in {key for _p, key, _d in no_hot_water}}
    R.check(
        "the six hot-water-gated translation keys this check names are "
        "still real entities (anchor)",
        present == dhw_only_keys,
        f"missing from the census entirely: {sorted(dhw_only_keys - present)}",
    )
    still_enabled = sorted(dhw_only_keys - disabled_keys)
    R.check(
        "every one of the six is disabled by default on a no-hot-water "
        "install (the property D6-s1-03 measured; a translation-key "
        "rename would fail the anchor above instead of silently passing "
        "here)",
        not still_enabled,
        f"unexpectedly enabled: {still_enabled}",
    )
    # README text: the paragraph documenting them must say so, by name.
    six_names = [
        "DHW Cost (lifetime)", "DHW Energy (lifetime)",
        "DHW Heating Cost (next 24 h)", "DHW Heating Schedule",
        "DHW Setpoint Advisor", "Plan DHW Heating (next 24 h)",
    ]
    prose = " ".join(ln for ln in README.splitlines() if not ln.startswith("|"))
    missing_in_prose = [
        name for name in six_names
        if not any(
            name in sent and "disabled by default" in sent
            for sent in re.split(r"(?<=\.)\s", prose)
        )
    ]
    R.check(
        "README documents all six as disabled by default, in one sentence "
        "naming each (D6-s1-03)",
        not missing_in_prose,
        f"undocumented: {missing_in_prose}",
    )
    # Null control: none of the six were named anywhere near "disabled by
    # default" before this PR (the paragraph did not exist).
    _bad_prose = (
        "Since #1335 that list is every entity the ordinary install cannot "
        "light. "
    )
    _bad_missing = [
        name for name in six_names
        if not any(
            name in sent and "disabled by default" in sent
            for sent in re.split(r"(?<=\.)\s", _bad_prose)
        )
    ]
    R.check(
        "the prose check fires when the six are undocumented (null "
        "control)",
        _bad_missing == six_names,
        repr(_bad_missing),
    )


def check_multistart_starting_points() -> None:
    R.section(
        "how-it-works.md's multi-start count matches the optimizer "
        "(#1645 D6-s2-04)"
    )
    from unittest import mock

    from heatpump_optimizer import optimizer as optmod
    import stress

    starts_seen: list[int] = []
    orig = optmod._multi_start_minimize

    def spy(objective, candidates, *a, **k):
        starts_seen.append(len(candidates))
        return orig(objective, candidates, *a, **k)

    with mock.patch.object(optmod, "_multi_start_minimize", spy):
        stress.build_case(season="winter", two_zone=False, dhw=False)
    R.check(
        "the space solve was exercised at least once (anchor)",
        bool(starts_seen),
        repr(starts_seen),
    )
    n = starts_seen[0] if starts_seen else -1
    text = DOCS["how-it-works.md"]
    R.check(
        "how-it-works.md no longer claims a fixed count of two starting "
        "points now that the optimizer scores more (D6-s2-04: measured "
        f"{n})",
        "two starting points" not in text.lower() and "two candidate" not in text.lower(),
        "still present" if "two starting points" in text.lower() else "ok",
    )
    m = re.search(r"scores (\w+) candidate", text)
    _NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    R.check(
        "...and the number it does state matches what the optimizer runs "
        "(anchor + D6-s2-04)",
        m is not None and _NUMBER_WORDS.get(m.group(1)) == n,
        f"doc states {m.group(1) if m else None!r}, measured {n}",
    )
    # Corpus-wide (I5): every count of starting points anywhere in the reader
    # docs is the count the optimizer runs, not only the sentence above.
    claims = multistart_count_claims(CORPUS)
    R.check(
        "every starting-point count the corpus states is the count the "
        f"optimizer runs (I5, measured {n})",
        all(v == n for _, v in claims),
        repr(claims),
    )
    R.check(
        "the corpus count fires on a stale count (null control)",
        multistart_count_claims({"probe.md": f"It runs from {n + 1} starting points."})
        == [("probe.md", n + 1)],
    )
    # Null control: the exact pre-fix sentence is what this check exists to
    # catch.
    _bad_text = (
        "**Two starting points, not one.** The space solve runs from two "
        "candidate initial guesses and keeps the better result."
    )
    R.check(
        "the claim check fires on the pre-fix sentence (null control)",
        "two starting points" in _bad_text.lower(),
        _bad_text,
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
# Round 9 F8.3: quick-setup storage promises vs the answers (D5-s1-02),
# the card-version banner vs the stamp (D5-s1-03), the curve-bias weekly
# bound (D6-s2-03), the currency fallback claim (D6-s1-81), and the Services
# paragraphs vs the registered schemas (the I5 barrier arm, landed early per
# F8.1's carry). Each arm derives both sides and carries an anchor.
# ---------------------------------------------------------------------------

_STORAGE_PROMISE = re.compile(r"stores cheap heat|two-tank physics")
_VALVE_GUARD = re.compile(r"mixing valve|valve mode", re.I)


def quick_setup_storage_facts() -> tuple[bool, bool, bool, bool]:
    """(buffer_is_store, two_tank_modelled) for the all-yes quick setup, then
    the same two with a throttling mixing-valve mode added.

    The five-question page never asks about the mixing valve, but
    ``thermal_model`` gates both properties on one: ``buffer_is_store``
    requires a throttling valve as well as a store-sized tank, and
    ``two_tank_modelled`` requires the four-way topology, which the same
    valve enables. The second pair is the control that the predicates
    distinguish a throttling install from the quick setup's default valve.
    """
    from heatpump_optimizer import const, mixing_valve, quick_setup
    from heatpump_optimizer.thermal_model import ThermalParameters

    answers = {
        quick_setup.FIELD_TWO_ZONE: True,
        quick_setup.FIELD_BUFFER_TANK: True,
        quick_setup.FIELD_DHW_TANK: True,
        quick_setup.FIELD_WOOD_FURNACE: True,
        quick_setup.FIELD_WOOD_BUFFER_TANK: True,
        const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
        const.CONF_WOOD_TANK_BOTTOM_ENTITY: "sensor.wood_bottom",
    }
    cfg = quick_setup.derive(dict(answers))
    p = ThermalParameters.from_config(cfg)
    throttle = sorted(mixing_valve.THROTTLING_MODES)[0]
    c = ThermalParameters.from_config({**cfg, const.CONF_MIXING_VALVE_MODE: throttle})
    return p.buffer_is_store, p.two_tank_modelled, c.buffer_is_store, c.two_tank_modelled


def _storage_unguarded(section: str) -> list[str]:
    """The promise lines in a five-questions section that name no precondition."""
    return [
        line
        for line in section.splitlines()
        if _STORAGE_PROMISE.search(line) and not _VALVE_GUARD.search(line)
    ]


def check_quick_setup_promises() -> None:
    R.section("quick-setup storage promises vs what the answers build (D5-s1-02)")
    bis, ttm, cbis, cttm = quick_setup_storage_facts()
    R.check(
        "the all-yes quick setup builds neither a store nor the two-tank model",
        not bis and not ttm,
        f"buffer_is_store={bis} two_tank_modelled={ttm}",
    )
    R.check(
        "with a throttling valve configured both properties turn on (control)",
        cbis and cttm,
        f"buffer_is_store={cbis} two_tank_modelled={cttm}",
    )
    section_m = re.search(r"### The five house questions\n(.*?)\n### ", DOCS["setup.md"], re.S)
    section = section_m.group(1) if section_m else ""
    R.check("the five-questions section is still there (anchor)", bool(section))
    R.check(
        "the section still says what the tank answers switch on (anchor)",
        bool(_STORAGE_PROMISE.search(section)),
    )
    unguarded = _storage_unguarded(section)
    R.check(
        "every storage promise names its mixing-valve precondition",
        not unguarded,
        repr(unguarded),
    )
    # Null control: the pre-fix rows promised the store and the two-tank
    # switch outright; the detector must fire on that shape, not merely pass
    # on the fixed one.
    pre_fix_section = (
        "| Buffer tank | off | A tank between the heat pump and the heating "
        "circuits. On stores cheap heat and releases it during expensive "
        "hours. |\n"
        "| Wood buffer tank | off | A second tank the wood furnace heats. "
        "The two probes below it are what actually switch the two-tank "
        "physics on. |\n"
    )
    fired = _storage_unguarded(pre_fix_section)
    R.check(
        "the pre-fix promise rows fire the precondition guard (null control)",
        len(fired) == 2,
        f"{len(fired)} of 2 rows fired",
    )


def stamp_tracks_card() -> tuple[str, float]:
    """(card version now, share of simulated stamps that rewrite the banner).

    Five successive patch releases of VERSION stamped over the real card
    bytes with ``tools/release/stamp.py:rewrite_card_version`` -- the call
    every stamp makes. The doc's old model (the banner "moves only when the
    card file changes") predicts a share of 0.0; the stamp makes it 1.0.
    """
    spec = importlib.util.spec_from_file_location(
        "f83-stamp", ROOT / "tools" / "release" / "stamp.py"
    )
    stamp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stamp)
    card = (PKG / "www" / "heatpump-optimizer-card.js").read_text()
    cur_m = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', card)
    version = (ROOT / "VERSION").read_text().strip()
    major, minor, patch = (int(x) for x in version.split("."))
    text, tracks = card, 0
    n = 5
    for k in range(1, n + 1):
        nxt = f"{major}.{minor}.{patch + k}"
        text, _old = stamp.rewrite_card_version(text, nxt)
        got = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', text)
        tracks += int(got is not None and got.group(1) == nxt)
    return cur_m.group(1) if cur_m else "", tracks / n


_CARD_LAGS = re.compile(
    r"often lower than the integration version|not against the integration version itself"
)


def check_card_version_tracks_stamp() -> None:
    R.section("the card-version banner vs what a stamp writes (D5-s1-03)")
    cur, share = stamp_tracks_card()
    R.check("the bundled card carries a version (anchor)", bool(cur), cur)
    R.check(
        "every simulated stamp rewrites the card version (share == 1.0)",
        share == 1.0,
        f"card now {cur}, share {share}",
    )
    doc = DOCS["dashboard-card.md"]
    m = re.search(r"heatpump-optimizer-card\s+v(\d+\.\d+\.\d+)", doc)
    R.check("the banner section still shows an example version (anchor)", m is not None)
    stale = _CARD_LAGS.findall(doc)
    R.check(
        "the doc no longer says the banner lags the integration version",
        not stale,
        repr(stale),
    )
    # Null control: re-inserting the pre-fix sentences must fire the claim scan.
    mutated = doc.replace(
        "That is the card's own version",
        "That is the card's own version. It moves only when the card file "
        "changes, so it is often lower than the integration version -- "
        "compare it against the card version named in the release notes, "
        "not against the integration version itself",
        1,
    )
    R.check(
        "re-inserting the pre-fix banner claim fires the scan (null control)",
        len(_CARD_LAGS.findall(mutated)) == len(_CARD_LAGS.findall(doc)) + 2,
        f"{len(_CARD_LAGS.findall(doc))} -> {len(_CARD_LAGS.findall(mutated))}",
    )


def curve_bias_facts() -> tuple[float, int, float]:
    """(bias after one cycle at a +2 K residual, its sample count, and the
    per-fold step a settled fold takes at a +10 K residual).

    The doc's old claim bounded the learner at "0.5 K per week". Both
    regimes the code actually runs exceed 0.5 K within a single cycle: the
    first residual is folded whole, and the settled EWMA takes
    ``FLOW_BIAS_ALPHA`` of each new residual per cycle.
    """
    from heatpump_optimizer.flow_lift import FLOW_BIAS_MIN_SAMPLES, FlowCurveBias

    one = FlowCurveBias()
    one.observe(42.0, 40.0)
    ewma = FlowCurveBias()
    for _ in range(FLOW_BIAS_MIN_SAMPLES):
        ewma.observe(50.0, 40.0)
    prev = ewma.bias_k
    ewma.observe(40.0, 40.0)
    step = abs(ewma.bias_k - prev)
    return one.bias_k, one.samples, step


def check_curve_bias_no_weekly_bound() -> None:
    R.section("the curve-bias learner against a weekly bound (D6-s2-03)")
    first_k, samples, ewma_step = curve_bias_facts()
    R.check(
        "one cycle folds a full residual into the bias",
        samples == 1 and first_k > 0.5,
        f"{samples} sample(s), bias {first_k} K",
    )
    R.check(
        "a settled fold tracks a changed residual by more than 0.5 K per cycle",
        ewma_step > 0.5,
        f"{ewma_step} K per fold",
    )
    hits = {
        name: found
        for name, text in CORPUS.items()
        if (found := re.findall(r"0\.5 K per week|half a degree per week", text))
    }
    R.check(
        "no reader doc bounds the curve-bias learner by a weekly amount",
        not hits,
        repr(hits),
    )
    R.check(
        "the corpus still documents the heat-curve correction (anchor)",
        any("heat-curve correction" in text for text in CORPUS.values()),
    )
    # Null control: re-adding the pre-fix bound to a README copy must fire.
    mutated = README.replace(
        "a cool-only heat-curve correction",
        "a cool-only heat-curve correction of at most 0.5 K per week",
    )
    R.check(
        "re-adding the weekly bound fires the scan (null control)",
        bool(re.search(r"0\.5 K per week", mutated)),
    )


def currency_facts() -> tuple[str, str]:
    """(resolve_currency under a real configured instance, under no config).

    A normal Home Assistant instance always has a currency (defaulting to
    EUR); the SEK fallback is what the code returns only when nothing is
    readable. README's old parenthetical claimed the fallback is what an
    unconfigured instance shows.
    """
    from heatpump_optimizer.currency import resolve_currency

    class _EurConfig:
        currency = "EUR"

    class _Hass:
        config = _EurConfig()

    return resolve_currency(_Hass()), resolve_currency(object())


# Whitespace-insensitive: the corpus wraps at ~90 columns, and the base's false
# claim reads "(SEK when the instance has none\nconfigured)" -- an inline-only
# pattern scans ok over the defect (the wrapped-fixture class; round-1 review).
_CURRENCY_FALSE_CLAIM = r"SEK\s+when\s+the\s+instance\s+has\s+none\s+configured"

# The merge base's exact wrapped sentence, restore-able for the null control.
_CURRENCY_BASE_SENTENCE = (
    "`CUR` is your Home Assistant instance currency "
    "(SEK when the instance has none\nconfigured)."
)


def check_readme_currency_claim() -> None:
    R.section("README's currency fallback claim vs resolve_currency (D6-s1-81)")
    real, fallback = currency_facts()
    R.check("a configured instance currency is returned as-is", real == "EUR", real)
    R.check("with nothing readable the code falls back to SEK", fallback == "SEK", fallback)
    hits = re.findall(_CURRENCY_FALSE_CLAIM, README)
    R.check(
        "README no longer claims SEK for an unconfigured instance",
        not hits,
        repr(hits),
    )
    R.check("README still documents the instance currency (anchor)", "instance currency" in README)
    # Null control over the corpus's real shape: restore the base's WRAPPED
    # sentence into the committed README text. At the merge base the committed
    # text already carries the wrapped claim, so the restore is a no-op there
    # and the scan check above is the red demonstration; at the head the
    # restore is real, and an inline-only scan would pass it -- so the control
    # pins the whitespace-insensitivity too.
    anchor = "`CUR` is your Home Assistant instance currency."
    mutated = README.replace(anchor, _CURRENCY_BASE_SENTENCE, 1)
    R.check(
        "restoring the base's wrapped claim fires the scan (null control)",
        bool(re.findall(_CURRENCY_FALSE_CLAIM, mutated)),
    )


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


def _service_paragraphs(doc: str) -> dict[str, str]:
    """Service name -> the text of its `**`name`**` paragraph."""
    return {
        m.group(1): m.group(2)
        for m in re.finditer(
            r"^\*\*`(\w+)`\*\*(.*?)(?=^\*\*`\w+`\*\*|^#|\Z)", doc, re.M | re.S
        )
    }


def _service_field_problems(
    fields: dict[str, set[str]], paras: dict[str, str]
) -> dict[str, str]:
    """Paragraphs whose field list or count disagrees with the schema."""
    wrong: dict[str, str] = {}
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
    return wrong


def check_service_fields() -> None:
    R.section("service paragraphs vs the registered schemas (I5)")
    doc = DOCS["configuration.md"]
    fields = registered_service_fields()
    paras = _service_paragraphs(doc)
    R.check(
        "the registry and the Services paragraphs are both there (anchor)",
        bool(fields) and bool(set(fields) & set(paras)),
        f"{sorted(fields)} / {sorted(paras)}",
    )
    wrong = _service_field_problems(fields, paras)
    R.check(
        "every service paragraph that lists or counts fields matches its schema",
        not wrong,
        repr(wrong),
    )
    # Null control: deleting a listed field name from the assign_entity
    # paragraph must make the comparison fire again (a no-op while the field
    # is missing, so the control is honest both before and after the fix).
    para = paras.get("assign_entity", "")
    mutated = {**paras, "assign_entity": para.replace("`manual_setpoint`", "", 1)}
    R.check(
        "removing a listed field from a paragraph fires the comparison "
        "(null control)",
        bool(_service_field_problems(fields, mutated)),
    )


# ---------------------------------------------------------------------------
# I5 class barrier (round 9, #1645): shape-agnostic arms. The services arm is
# F8.3's check_service_fields above, the leaf this barrier was written for. Each derives its claim
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


def _label(s: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", " ", s).strip().strip("*`").strip().lower()


_LABEL_END = r"(?:temperature|sensor|source|switch|entity|enabled|mode|control|feedback|experiment|cycle|limit)"


def check_option_labels() -> None:
    R.section("option fields the docs name are fields the forms show (I5)")
    en = json.loads((PKG / "translations" / "en.json").read_text())
    steps = en.get("options", {}).get("step", {})
    menu = {v: k for s in ("init", "advanced")
            for k, v in steps.get(s, {}).get("menu_options", {}).items()}
    R.check("the options flow keeps its init and advanced menus (anchor)", bool(menu))

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


def options_field_pages() -> tuple[dict[str, str], dict[str, set[str]]]:
    """(step -> page title, field label -> the steps whose form renders it)."""
    steps = _EN_STRINGS.get("options", {}).get("step", {})
    titles = {name: step["title"] for name, step in steps.items()
              if isinstance(step, dict) and isinstance(step.get("title"), str)}
    pages: dict[str, set[str]] = {}
    for name, step in steps.items():
        stack = [step]
        while stack:
            node = stack.pop()
            if not isinstance(node, dict):
                continue
            for key, value in node.items():
                if key == "data" and isinstance(value, dict):
                    for label in value.values():
                        if isinstance(label, str):
                            pages.setdefault(_label(label), set()).add(name)
                else:
                    stack.append(value)
    return titles, pages


def page_placement_problems(corpus: dict[str, str], titles: dict[str, str],
                            pages: dict[str, set[str]]) -> tuple[int, list[str]]:
    """(claims, wrong): italic field labels in a sentence naming a bold options page.

    A sentence that names one or more options pages in bold (``**Hot water**``,
    ``**Advanced settings → Thermal model (expert)**``) and the word "page"
    places every italic field label in it on one of those pages; the field's
    real page is the step whose form renders the label.
    """
    by_title = {_label(t): step for step, t in titles.items()}
    claims, wrong = 0, []
    for name, text in corpus.items():
        for sentence in re.split(r"(?<=[.;])\s", text.replace("\n", " ")):
            if "page" not in sentence:
                continue
            named = {by_title[_label(t.split("→")[-1])]
                     for t in re.findall(r"\*\*([^*]+?)\*\*", sentence)
                     if _label(t.split("→")[-1]) in by_title}
            if not named:
                continue
            for field in re.findall(r"(?<![*\w])\*([^*\n]{3,80}?)\*(?!\*)", sentence):
                homes = pages.get(_label(field))
                if homes is None:
                    continue
                claims += 1
                if not homes & named:
                    wrong.append(f"{name}: *{field}* on {sorted(titles[s] for s in named)},"
                                 f" rendered on {sorted(titles[s] for s in homes)}")
    return claims, wrong


def check_options_page_census() -> None:
    R.section("a field the docs place on an options page is on that page (I5, D6-s1-02)")
    titles, pages = options_field_pages()
    R.check("the options forms have titled pages and labelled fields (anchor)",
            bool(titles) and bool(pages), f"{len(titles)} pages, {len(pages)} labels")
    claims, wrong = page_placement_problems(CORPUS, titles, pages)
    R.check("the corpus places options fields on pages (anchor)", claims > 0, f"{claims} claims")
    R.check("every field the corpus places on an options page is rendered there",
            not wrong, repr(wrong))
    # Null control: one real label, placed on a real page that does not render it.
    field, homes = next((f, h) for f, h in sorted(pages.items()) if set(titles) - h)
    elsewhere = titles[sorted(set(titles) - homes)[0]]
    probe = {"probe.md": f"The *{field}* field is on the **{elsewhere}** page."}
    R.check("the census fires on a field placed on a page that does not render it (null control)",
            page_placement_problems(probe, titles, pages)[1] != [], probe["probe.md"])


_COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                "eight": 8, "nine": 9, "ten": 10}
_START_COUNT = re.compile(
    r"\b(\d+|" + "|".join(_COUNT_WORDS) + r")\s+(?:starting points|candidate"
    r"(?: initial guesses| starting points| starts)?s?|initial guesses)\b", re.I)


def multistart_count_claims(corpus: dict[str, str]) -> list[tuple[str, int]]:
    """Every '<n> starting points / candidates / initial guesses' the corpus states."""
    return [(name, int(m.group(1)) if m.group(1).isdigit() else _COUNT_WORDS[m.group(1).lower()])
            for name, text in corpus.items() for m in _START_COUNT.finditer(text.replace("\n", " "))]


def py_typed_files(root: pathlib.Path = PKG) -> int:
    """How many ``py.typed`` markers a package tree carries."""
    return sum(1 for _ in root.rglob("py.typed"))


def check_py_typed_claim() -> None:
    R.section("quality_scale.yaml's py.typed count vs the package (RCA-BULK-3, #1545)")
    claims = [int(n) for n in re.findall(r"\bqs_py_typed_files=(\d+)", QUALITY_SCALE)]
    R.check("strict-typing states qs_py_typed_files (anchor)", bool(claims), repr(claims))
    shipped = py_typed_files()
    R.check(
        "every qs_py_typed_files the checklist states is the number of py.typed "
        "files the package ships",
        bool(claims) and all(n == shipped for n in claims),
        f"stated {claims}, shipped {shipped}",
    )
    with tempfile.TemporaryDirectory() as _bare:
        _unmarked = py_typed_files(pathlib.Path(_bare))
    R.check(
        "the count fires on a package that ships no marker (null control)",
        bool(claims) and any(n != _unmarked for n in claims),
        f"stated {claims}, a bare tree counts {_unmarked}",
    )


def main() -> int:
    check_figures()
    check_ecl110_defaults()
    check_entity_prefix()
    check_requirements_claim()
    check_quickstart_numbering()
    check_initial_setup_menu()
    check_simulate_plan_fields()
    check_two_zone_field_labels_and_placement()
    check_heat_pump_action_states()
    check_disabled_by_default_without_hot_water()
    check_multistart_starting_points()
    check_census_self_test()
    check_quality_scale()
    check_py_typed_claim()
    check_quick_setup_promises()
    check_card_version_tracks_stamp()
    check_curve_bias_no_weekly_bound()
    check_readme_currency_claim()
    check_service_fields()
    check_entity_prose()
    check_private_mentions()
    check_unit_typography()
    check_option_labels()
    check_options_page_census()
    return R.close("checks")


if __name__ == "__main__":
    raise SystemExit(main())
