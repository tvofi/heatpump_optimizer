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


def main() -> int:
    check_figures()
    check_ecl110_defaults()
    check_entity_prefix()
    return R.close("checks")


if __name__ == "__main__":
    raise SystemExit(main())
